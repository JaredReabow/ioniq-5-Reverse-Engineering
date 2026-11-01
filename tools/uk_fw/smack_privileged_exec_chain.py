#!/usr/bin/env python3
"""Audit the configured SMACK execute-label transition chain.

This host-side analyzer never executes a recovered target.  It streams the
canonical rootfs through one stable no-follow descriptor, parses only policy and
relabel text, compares a supplied bash binary with its canonical archive member,
and validates hash-bound public Linux/Bash source.  Output describes configured
semantics and unresolved runtime gates; it does not emit a payload or perform an
exec, label change, update, flash, or target write.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import posixpath
import re
import stat
import struct
import sys
import tarfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
TOOL_NAME = "smack-privileged-exec-chain"
TOOL_VERSION = "1.3.0"
MAX_ROOTFS_SIZE = 1 << 30
MAX_MEMBER_SIZE = 16 << 20
MAX_SOURCE_SIZE = 4 << 20

ROOTFS = {
    "size": 879109759,
    "sha256": "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84",
    "member_count": 66836,
    "inventory_sha256": "c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c",
}
POLICY_PREFIX = "etc/smack/accesses.d/"
POLICY_COUNT = 27
POLICY_RULE_COUNT = 636
POLICY_NORMALIZED_SHA256 = "4aa679165cca01d53993082df802bbaec29ee1fcaf42eda9f014951653a08f1a"
SELECTED = {
    "bin/sh": {"kind": "symlink", "mode": 0o777, "uid": 0, "gid": 0, "link": "/bin/bash"},
    "bin/bash": {
        "kind": "regular", "mode": 0o755, "uid": 0, "gid": 0, "size": 946216,
        "sha256": "783a69b9b27fae5da3fa93e441467160d6e760f3a79048a4dd02d98b571ad0aa",
    },
    "lib/ld-linux-x86-64.so.2": {
        "kind": "symlink", "mode": 0o777, "uid": 0, "gid": 0, "link": "ld-2.25.so",
    },
    "lib/ld-2.25.so": {
        "kind": "regular", "mode": 0o755, "uid": 0, "gid": 0, "size": 149184,
        "sha256": "0dfa16d8b5c9b35fb161a6f5dab48e7b267531ecf8ec3bf3ac74de61ce2ad99e",
    },
    "app/bin/AppUpgrade": {
        "kind": "regular", "mode": 0o755, "uid": 0, "gid": 0, "size": 10787256,
        "sha256": "5295c6e4c41fb9c03760cf006c58b66fcd11aeb4e6e889af6e31b062549b6df0",
    },
    "etc/smack_setup.sh": {
        "kind": "regular", "mode": 0o700, "uid": 0, "gid": 0, "size": 7603,
        "sha256": "847af53be34d0e325c738a4ae26d11f7ed69b940cf2aa53d27e3b422e8a8ebb6",
    },
    "etc/smack-relabel-ro.sh": {
        "kind": "regular", "mode": 0o700, "uid": 0, "gid": 0, "size": 6206,
        "sha256": "8275625764c30b6e82d99e5fdf887038261f97e9f0ef5a36da8faa743a35a15f",
    },
    "etc/update_start_5w.sh.ori": {
        "kind": "regular", "mode": 0o700, "uid": 0, "gid": 0, "size": 3933,
        "sha256": "06c3ab7e24b082c24a81299f0627245c0281bc5d519005cd921c13707eb5e838",
    },
}
BASH_BUILD_ID = "bbe47288a3fee7f0979fed1eb2794e5596f33113"
SOURCE_IDENTITIES = {
    "smack_lsm": "78d4ce7d6f9849aefa6c2882edcff2d72cf8e1372c97c55fb678b66494101a3e",
    "smack_header": "1877a14e27c28440195e702e0ff69cbe367bff01ee8ba5e037666b0974d45e53",
    "exec": "f60f64215f6081b09c81a22a6f1f6dd93503d0bb7f17da3609e0bcb6d9e2e5cb",
    "binfmt_script": "07942e13ede294115fb307cb2817d35f00fb813dca23030c97ba59dd98313030",
    "binfmt_elf": "7c0d0c032a53f725f127d2d6977eb484be7e6e24f64858b639dc5db75725bf43",
    "commoncap": "bf00df2e6cdeaf72e033dfaeaf60425a165c1c7bfa32627139930aedd9097255",
    "bash_shell": "e2a1b14881a0803aab6ee3bdce4ede3bff6c115dd220ad1ab335ca04303123d0",
    "bash_variables": "9b82ffc4313cdb63d626179f27d8ab94c4794d653f987930c1823ee77e7d8360",
    "bash_findcmd": "8fa6dc160579ac75027d0b67b7e6c625619a7a2016fced68a729a50973316dad",
    "glibc_rtld": "909759872684237c9d8c93bfa71acd1bfd50f44aa68175c71e59692d3cda3aa3",
    "glibc_unsecvars": "8c9d4b40d34e1fc443900fdc0eb499ff0b0632ed8d39a0f9f2a7a79c37a09451",
    "glibc_extra_unsecvars": "cadb9cfad08f1372f87a8f3fccd8e8f49382fc0fd8b5043f48b30a3adf7f226a",
}
class BoundaryError(ValueError):
    """Input or evidence falls outside the exact bounded contract."""


class _HashingReader:
    """Hash every compressed archive byte consumed through one descriptor."""

    def __init__(self, handle: io.BufferedReader):
        self.handle = handle
        self.digest = hashlib.sha256()

    def read(self, size: int = -1) -> bytes:
        raw = self.handle.read(size)
        self.digest.update(raw)
        return raw

    def tell(self) -> int:
        return self.handle.tell()

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        return self.handle.seek(offset, whence)

    def readable(self) -> bool:
        return True


def _same_stat(before: os.stat_result, after: os.stat_result) -> bool:
    return all(
        getattr(before, key) == getattr(after, key)
        for key in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_nlink")
    )


def _canonical_member_name(name: str) -> str:
    if (
        type(name) is not str
        or not name
        or name.startswith("/")
        or any(ord(char) < 0x20 or ord(char) == 0x7f for char in name)
    ):
        raise BoundaryError("archive member name is invalid")
    if name in (".", "./"):
        return "."
    parts = name.split("/")
    while parts and parts[0] == ".":
        parts.pop(0)
    if parts and parts[-1] == "":
        parts.pop()
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise BoundaryError("archive member name is non-canonical or unsafe")
    canonical = posixpath.normpath("/".join(parts))
    if canonical.startswith("../") or canonical == "..":
        raise BoundaryError("archive member escapes the archive root")
    return canonical


def _inventory_line(index: int, member: tarfile.TarInfo) -> bytes:
    try:
        line = (
            f"{index}\t{member.name}\t{member.type.hex()}\t{member.mode:o}\t"
            f"{member.size}\t{member.linkname}\n"
        )
        return line.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise BoundaryError("archive inventory is not UTF-8") from exc


SOURCE_ANCHORS = {
    "smack_lsm": (
        b"rc = cap_bprm_set_creds(bprm);",
        b"if (bprm->cred_prepared)",
        b"if (isp->smk_task == NULL || isp->smk_task == bsp->smk_task)",
        b"bsp->smk_task = isp->smk_task;",
        b"if (!ret && (tsp->smk_task != tsp->smk_forked))",
        b"mask &= (MAY_READ|MAY_WRITE|MAY_EXEC|MAY_APPEND);",
        b"rc = smk_curacc(smk_of_inode(inode), mask, &ad);",
        b"if (smack_privileged(CAP_MAC_OVERRIDE))",
        b"rc = smk_access(tsp->smk_task, smk_of_inode(inode), MAY_READ, &ad);",
    ),
    "smack_header": (
        b"if (!capable(cap))",
        b"if (smack_onlycap == NULL || smack_onlycap == skp)",
    ),
    "exec": (
        b"if (task_no_new_privs(current))",
        b"bprm->unsafe |= LSM_UNSAFE_NO_NEW_PRIVS;",
        b"retval = security_bprm_set_creds(bprm);",
        b"bprm->cred_prepared = 1;",
    ),
    "binfmt_script": (
        b"retval = bprm_change_interp(interp, bprm);",
        b"file = open_exec(interp);",
        b"retval = prepare_binprm(bprm);",
        b"return search_binary_handler(bprm);",
    ),
    "binfmt_elf": (
        b"retval = flush_old_exec(bprm);",
        b"install_exec_creds(bprm);",
    ),
    "commoncap": (
        b"new->cap_permitted = cap_combine(old->cap_bset,",
        b"if (uid_eq(new->euid, root_uid))",
        b"new->cap_effective = new->cap_permitted;",
    ),
    "bash_shell": (
        b"running_setuid = uidget ();",
        b"return (current_user.uid != current_user.euid) ||",
        b"initialize_shell_variables (shell_environment, privileged_mode||running_setuid);",
    ),
    "bash_variables": (
        b"If PRIVMODE is nonzero, don't import functions from ENV",
        b"if (privmode == 0 && read_but_dont_execute == 0 &&",
        b"STREQN (BASHFUNC_PREFIX, name, BASHFUNC_PREFLEN)",
        b"temp_var = bind_variable (name, string, 0);",
        b"temp_var = set_if_not (\"PATH\", DEFAULT_PATH_VALUE);",
    ),
    "bash_findcmd": (
        b"path_list = value_cell (var);",
        b"cmd = find_user_command_in_path (name, path_list, flags);",
    ),
    "glibc_rtld": (
        b"if (__builtin_expect (__libc_enable_secure, 0))",
        b"static const char unsecure_envvars[] =",
        b"#ifdef EXTRA_UNSECURE_ENVVARS",
        b"EXTRA_UNSECURE_ENVVARS",
        b"UNSECURE_ENVVARS;",
        b"unsetenv (nextp);",
    ),
    "glibc_unsecvars": (
        b"#define UNSECURE_ENVVARS",
        b'"LD_LIBRARY_PATH\\0"',
        b'"LD_PRELOAD\\0"',
    ),
    "glibc_extra_unsecvars": (
        b"#define EXTRA_UNSECURE_ENVVARS",
        b'"LD_PREFER_MAP_32BIT_EXEC\\0"',
    ),
}


def _regular(path: Path, maximum: int, what: str) -> os.stat_result:
    try:
        row = path.lstat()
    except OSError as exc:
        raise BoundaryError(f"cannot lstat {what}: {exc.strerror}") from exc
    if not stat.S_ISREG(row.st_mode) or row.st_nlink != 1 or row.st_size > maximum:
        raise BoundaryError(f"{what} is linked, non-regular, or oversized")
    return row


def _read_stable(path: Path, maximum: int, what: str) -> bytes:
    before = _regular(path, maximum, what)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise BoundaryError(f"cannot open {what}: {exc.strerror}") from exc
    try:
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not _same_stat(before, opened):
                raise BoundaryError(f"{what} changed before stable open")
            raw = handle.read(maximum + 1)
            after_fd = os.fstat(handle.fileno())
    except OSError as exc:
        raise BoundaryError(f"cannot read {what}: {exc.strerror}") from exc
    try:
        after = path.lstat()
    except OSError as exc:
        raise BoundaryError(f"cannot revalidate {what}: {exc.strerror}") from exc
    if len(raw) != before.st_size or len(raw) > maximum:
        raise BoundaryError(f"{what} is truncated or oversized")
    if not _same_stat(opened, after_fd) or not _same_stat(before, after):
        raise BoundaryError(f"{what} changed while reading")
    return raw


def _member_bytes(archive: tarfile.TarFile, member: tarfile.TarInfo) -> bytes:
    if not member.isreg() or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE):
        raise BoundaryError("selected archive member is not a regular file")
    if member.linkname or member.size > MAX_MEMBER_SIZE:
        raise BoundaryError("selected archive member is linked or oversized")
    stream = archive.extractfile(member)
    if stream is None:
        raise BoundaryError("selected archive member cannot be streamed")
    raw = stream.read(member.size + 1)
    if len(raw) != member.size:
        raise BoundaryError("selected archive member is truncated or oversized")
    return raw


def _check_selected_metadata(name: str, member: tarfile.TarInfo, raw: bytes | None) -> None:
    expected = SELECTED[name]
    if member.mode != expected["mode"] or member.uid != expected["uid"] or member.gid != expected["gid"]:
        raise BoundaryError(f"selected member metadata drift: {name}")
    if expected["kind"] == "symlink":
        if not member.issym() or member.type != tarfile.SYMTYPE or member.size != 0:
            raise BoundaryError(f"selected symlink type drift: {name}")
        if member.linkname != expected["link"] or raw is not None:
            raise BoundaryError(f"selected symlink target drift: {name}")
        return
    if raw is None or not member.isreg() or member.linkname:
        raise BoundaryError(f"selected regular member type drift: {name}")
    if member.size != expected["size"] or hashlib.sha256(raw).hexdigest() != expected["sha256"]:
        raise BoundaryError(f"selected member identity drift: {name}")


def rootfs_snapshot(path: Path) -> tuple[dict[str, bytes], list[dict[str, Any]], dict[str, Any]]:
    before = _regular(path, MAX_ROOTFS_SIZE, "canonical rootfs")
    if before.st_size != ROOTFS["size"]:
        raise BoundaryError("canonical rootfs size drift")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise BoundaryError(f"cannot open canonical rootfs: {exc.strerror}") from exc
    selected: dict[str, bytes] = {}
    selected_seen: set[str] = set()
    policies: list[dict[str, Any]] = []
    seen: set[str] = set()
    count = 0
    inventory = hashlib.sha256()
    try:
        with os.fdopen(descriptor, "rb") as raw_handle:
            opened = os.fstat(raw_handle.fileno())
            if not _same_stat(before, opened):
                raise BoundaryError("canonical rootfs changed before stable open")
            reader = _HashingReader(raw_handle)
            with tarfile.open(fileobj=reader, mode="r|gz") as archive:
                for index, member in enumerate(archive):
                    count += 1
                    inventory.update(_inventory_line(index, member))
                    canonical = _canonical_member_name(member.name)
                    if canonical in seen:
                        raise BoundaryError("rootfs contains duplicate or aliased member names")
                    seen.add(canonical)
                    if canonical in SELECTED:
                        if canonical in selected_seen or member.name != "./" + canonical:
                            raise BoundaryError("selected rootfs member is duplicated or aliased")
                        selected_seen.add(canonical)
                        value = None if SELECTED[canonical]["kind"] == "symlink" else _member_bytes(archive, member)
                        _check_selected_metadata(canonical, member, value)
                        if value is not None:
                            selected[canonical] = value
                    elif canonical.startswith(POLICY_PREFIX):
                        if member.name != "./" + canonical or "/" in canonical[len(POLICY_PREFIX):]:
                            raise BoundaryError("policy member is nested or aliased")
                        value = _member_bytes(archive, member)
                        policies.append({
                            "name": canonical,
                            "size": member.size,
                            "sha256": hashlib.sha256(value).hexdigest(),
                            "bytes": value,
                        })
            while reader.read(1 << 20):
                pass
            archive_digest = reader.digest.hexdigest()
            descriptor_after = os.fstat(raw_handle.fileno())
    except (OSError, tarfile.TarError, UnicodeEncodeError) as exc:
        if isinstance(exc, BoundaryError):
            raise
        raise BoundaryError(f"cannot stream canonical rootfs: {type(exc).__name__}") from exc
    try:
        after = path.lstat()
    except OSError as exc:
        raise BoundaryError(f"cannot revalidate canonical rootfs: {exc.strerror}") from exc
    if not _same_stat(opened, descriptor_after) or not _same_stat(before, after):
        raise BoundaryError("canonical rootfs changed during streaming")
    if archive_digest != ROOTFS["sha256"] or count != ROOTFS["member_count"]:
        raise BoundaryError("canonical rootfs identity or member-count drift")
    if inventory.hexdigest() != ROOTFS["inventory_sha256"]:
        raise BoundaryError("canonical rootfs inventory drift")
    if selected_seen != set(SELECTED) or set(selected) != {n for n, v in SELECTED.items() if v["kind"] == "regular"}:
        raise BoundaryError("required selected rootfs member set drift")
    policies.sort(key=lambda row: row["name"])
    normalized = hashlib.sha256()
    for row in policies:
        normalized.update(f"./{row['name']}\0{row['size']}\0{row['sha256']}\n".encode("utf-8"))
    if len(policies) != POLICY_COUNT or normalized.hexdigest() != POLICY_NORMALIZED_SHA256:
        raise BoundaryError("SMACK policy member identity drift")
    return selected, policies, {
        "size": before.st_size,
        "sha256": archive_digest,
        "member_count": count,
        "inventory_sha256": inventory.hexdigest(),
        "policy_member_count": len(policies),
        "policy_normalized_sha256": normalized.hexdigest(),
    }


def parse_policy(policies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    pairs: set[tuple[str, str]] = set()
    for policy in policies:
        try:
            text = policy["bytes"].decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise BoundaryError(f"policy is not UTF-8: {policy['name']}") from exc
        if "\r" in text or not text.endswith("\n"):
            raise BoundaryError(f"policy has unsupported line endings: {policy['name']}")
        for line_number, raw in enumerate(text.splitlines(), 1):
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            fields = raw.split()
            if len(fields) != 3:
                raise BoundaryError(f"policy rule field-count drift: {policy['name']}:{line_number}")
            subject, obj, access = fields
            if not re.fullmatch(r"[A-Za-z0-9_:*.-]{1,255}", subject):
                raise BoundaryError("unsupported policy subject")
            if not re.fullmatch(r"[A-Za-z0-9_:*.-]{1,255}", obj):
                raise BoundaryError("unsupported policy object")
            if not re.fullmatch(r"[rwxatl-]{1,16}", access):
                raise BoundaryError("unsupported policy access string")
            pair = (subject, obj)
            if pair in pairs:
                raise BoundaryError("duplicate SMACK subject/object rule")
            pairs.add(pair)
            rules.append({
                "subject": subject,
                "object": obj,
                "access": access,
                "source_role": Path(policy["name"]).name,
                "line": line_number,
            })
    if len(rules) != POLICY_RULE_COUNT:
        raise BoundaryError("SMACK policy rule-count drift")
    return rules


def validate_contract_text(selected: dict[str, bytes]) -> dict[str, Any]:
    try:
        setup = selected["etc/smack_setup.sh"].decode("utf-8", "strict")
        relabel = selected["etc/smack-relabel-ro.sh"].decode("utf-8", "strict")
        anchor = selected["etc/update_start_5w.sh.ori"].decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise BoundaryError("selected contract text is not UTF-8") from exc
    required_setup = (
        'echo "Privileged" > /sys/fs/smackfs/onlycap',
        'echo "Privileged" >> $ONLYCAP_FILE',
        'chsmack -e "App::upgrade" /update/usb/bin/AppUpgrade',
    )
    required_relabel = (
        'APP_10=("AppUpgrade" "App::upgrade")',
        '${SMACK_LABEL_EXEC} ${APP_LABEL} ${PDK_app_Path}/app/bin/${APP_NAME}',
        'chsmack -a "_" "${1}"',
        'chsmack -r -A -E "${1}"',
    )
    required_anchor = (
        '#!/bin/sh',
        '${SMACK_LABEL_EXEC} "Privileged" ${TARGET_DIR}${ANCHOR_FILE}',
        '${SMACK_LABEL_ACCESS} "_" ${TARGET_DIR}${ANCHOR_FILE}',
        'echo `date +%Y%m%d-%H%M%S` "[SMACK]" $IN >> $LOGFILE 2>/dev/null',
    )
    for text, anchors, role in (
        (setup, required_setup, "smack setup"),
        (relabel, required_relabel, "relabel script"),
        (anchor, required_anchor, "update anchor"),
    ):
        if any(item not in text for item in anchors):
            raise BoundaryError(f"{role} contract anchor drift")
    path_assignments = [line for line in anchor.splitlines() if re.match(r"^\s*(?:export\s+)?PATH=", line)]
    if path_assignments:
        raise BoundaryError("update anchor unexpectedly resets PATH")
    return {
        "onlycap_label": "Privileged",
        "appupgrade_exec_label": "App::upgrade",
        "anchor_access_label": "_",
        "anchor_exec_label": "Privileged",
        "anchor_interpreter": "/bin/sh",
        "anchor_resets_path": False,
        "unqualified_lookup_before_argument_exit": "date",
    }


def validate_sources(paths: dict[str, Path]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for role in SOURCE_IDENTITIES:
        raw = _read_stable(paths[role], MAX_SOURCE_SIZE, f"{role} source")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != SOURCE_IDENTITIES[role]:
            raise BoundaryError(f"{role} source identity drift")
        if any(anchor not in raw for anchor in SOURCE_ANCHORS[role]):
            raise BoundaryError(f"{role} source semantic anchor drift")
        if role in ("glibc_unsecvars", "glibc_extra_unsecvars") and b'"PATH\\0"' in raw:
            raise BoundaryError("glibc secure-environment list unexpectedly includes PATH")
        result[role] = {"sha256": digest, "anchor_count": len(SOURCE_ANCHORS[role])}
    return result


def _gnu_build_id(raw: bytes) -> str:
    if raw[:6] != b"\x7fELF\x02\x01" or len(raw) < 0x40:
        raise BoundaryError("bash is not a supported ELF64 little-endian artifact")
    phoff = struct.unpack_from("<Q", raw, 0x20)[0]
    phentsize = struct.unpack_from("<H", raw, 0x36)[0]
    phnum = struct.unpack_from("<H", raw, 0x38)[0]
    values: list[str] = []
    for index in range(phnum):
        base = phoff + index * phentsize
        if phentsize < 56 or base + 56 > len(raw):
            raise BoundaryError("bash program-header table is malformed")
        p_type, _flags, offset, _vaddr, _paddr, filesz, _memsz, _align = struct.unpack_from(
            "<IIQQQQQQ", raw, base
        )
        if p_type != 4:
            continue
        if filesz > 1 << 20 or offset > len(raw) or filesz > len(raw) - offset:
            raise BoundaryError("bash PT_NOTE range is malformed")
        cursor = offset
        end = offset + filesz
        while cursor < end:
            if end - cursor < 12:
                raise BoundaryError("bash PT_NOTE header is truncated")
            namesz, descsz, note_type = struct.unpack_from("<III", raw, cursor)
            name_offset = cursor + 12
            desc_offset = (name_offset + namesz + 3) & ~3
            next_note = (desc_offset + descsz + 3) & ~3
            if desc_offset > end or next_note > end:
                raise BoundaryError("bash PT_NOTE record is malformed")
            name = raw[name_offset:name_offset + namesz]
            if note_type == 3 and name.rstrip(b"\0") == b"GNU":
                values.append(raw[desc_offset:desc_offset + descsz].hex())
            cursor = next_note
    if values != [BASH_BUILD_ID]:
        raise BoundaryError("bash GNU build-id is absent, ambiguous, or changed")
    return values[0]


def _elf_interpreter(raw: bytes) -> str:
    if raw[:6] != b"\x7fELF\x02\x01" or len(raw) < 0x40:
        raise BoundaryError("bash is not a supported ELF64 little-endian artifact")
    phoff = struct.unpack_from("<Q", raw, 0x20)[0]
    phentsize = struct.unpack_from("<H", raw, 0x36)[0]
    phnum = struct.unpack_from("<H", raw, 0x38)[0]
    interpreters: list[str] = []
    for index in range(phnum):
        base = phoff + index * phentsize
        if phentsize < 56 or base + 56 > len(raw):
            raise BoundaryError("bash program-header table is malformed")
        p_type, _flags, offset, _vaddr, _paddr, filesz, _memsz, _align = struct.unpack_from(
            "<IIQQQQQQ", raw, base
        )
        if p_type != 3:
            continue
        if filesz < 2 or filesz > 4096 or offset + filesz > len(raw):
            raise BoundaryError("bash PT_INTERP is malformed")
        value = raw[offset:offset + filesz]
        if not value.endswith(b"\0") or b"\0" in value[:-1]:
            raise BoundaryError("bash PT_INTERP is not one NUL-terminated string")
        try:
            interpreters.append(value[:-1].decode("ascii"))
        except UnicodeDecodeError as exc:
            raise BoundaryError("bash PT_INTERP is not ASCII") from exc
    if interpreters != ["/lib/ld-linux-x86-64.so.2"]:
        raise BoundaryError("bash PT_INTERP identity drift")
    return interpreters[0]


def validate_bash(path: Path, canonical: bytes, loader: bytes) -> dict[str, Any]:
    raw = _read_stable(path, MAX_MEMBER_SIZE, "supplied bash")
    if raw != canonical:
        raise BoundaryError("supplied bash does not match canonical rootfs member")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SELECTED["bin/bash"]["sha256"] or len(raw) != SELECTED["bin/bash"]["size"]:
        raise BoundaryError("supplied bash identity drift")
    build_id = _gnu_build_id(raw)
    required = (
        b"Bash version 3.2.57(1) release GNU", b"privileged_mode", b"PATH",
        b"getuid", b"geteuid", b"BASH_FUNC_", b"() {",
    )
    if any(value not in raw for value in required):
        raise BoundaryError("supplied bash semantic string anchor drift")
    forbidden = (b"secure_getenv", b"getauxval", b"AT_SECURE", b"__libc_enable_secure")
    loader_digest = hashlib.sha256(loader).hexdigest()
    if (len(loader) != SELECTED["lib/ld-2.25.so"]["size"]
            or loader_digest != SELECTED["lib/ld-2.25.so"]["sha256"]):
        raise BoundaryError("canonical dynamic-loader identity drift")
    return {
        "size": len(raw),
        "sha256": digest,
        "build_id": build_id,
        "embedded_version_role": "GNU-bash-3.2.57-release",
        "elf_interpreter": _elf_interpreter(raw),
        "dynamic_loader": {
            "role": "canonical-glibc-2.25-loader",
            "size": len(loader),
            "sha256": loader_digest,
        },
        "named_secure_environment_interfaces_present": [
            value.decode("ascii") for value in forbidden if value in raw
        ],
    }


def build_report(rootfs: Path, bash: Path, sources: dict[str, Path]) -> dict[str, Any]:
    selected, policies, rootfs_info = rootfs_snapshot(rootfs)
    rules = parse_policy(policies)
    contract = validate_contract_text(selected)
    source_info = validate_sources(sources)
    bash_info = validate_bash(bash, selected["bin/bash"], selected["lib/ld-2.25.so"])

    app_floor = sorted(
        (row for row in rules if row["subject"].startswith("App::") and row["object"] == "_"),
        key=lambda row: row["subject"],
    )
    if len(app_floor) != 27 or len({row["subject"] for row in app_floor}) != 27:
        raise BoundaryError("App-domain to floor rule-set drift")
    if any(not {"r", "x"}.issubset(set(row["access"])) for row in app_floor):
        raise BoundaryError("an App-domain to floor rule lacks read or execute permission")

    selected_report = []
    for name in sorted(SELECTED):
        expected = SELECTED[name]
        row: dict[str, Any] = {
            "role": name.replace("/", "-"),
            "kind": expected["kind"],
            "mode": f"{expected['mode']:04o}",
            "uid": expected["uid"],
            "gid": expected["gid"],
        }
        if expected["kind"] == "symlink":
            row["target"] = expected["link"]
        else:
            row["size"] = expected["size"]
            row["sha256"] = expected["sha256"]
        selected_report.append(row)

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "rootfs": rootfs_info,
        "selected_members": selected_report,
        "public_sources": source_info,
        "policy": {
            "rule_count": len(rules),
            "app_domain_floor_execute_rule_count": len(app_floor),
            "app_domain_floor_execute_subjects": [row["subject"] for row in app_floor],
            "all_enumerated_app_floor_rules_allow_read_and_execute": True,
        },
        "configured_labels": contract,
        "bash": bash_info,
        "static_chain": {
            "initial_subject_role": "enumerated-App-domain-task",
            "target_inode_access_label": "_",
            "target_inode_exec_label": "Privileged",
            "pretransition_subject_and_inode_access_label_control_open_admission": True,
            "exec_transition_label_does_not_authorize_open": True,
            "ordinary_read_and_execute_permission_from_every_enumerated_app_domain": True,
            "dac_requires_uid_zero_or_equivalent_access": True,
            "anchor_mode": "0700",
            "script_first_prepare_selects_exec_label_in_proposed_credentials": True,
            "interpreter_second_prepare_preserves_prepared_smack_label": True,
            "elf_credential_commit_applies_selected_task_label": True,
            "credential_commit_can_precede_late_elf_loader_failure": True,
            "committed_anchor_task_label": "Privileged",
            "smack_secureexec_predicted": True,
            "glibc_secure_mode_removes_named_unsecure_variables_but_not_path": True,
            "bash_privileged_mode_predicate_uses_uid_gid_mismatch": True,
            "same_uid_label_transition_triggers_bash_uid_gid_privileged_mode": False,
            "bash_imports_ordinary_environment_variables_when_uid_gid_match": True,
            "bash_source_allows_environment_function_import_when_uid_gid_match": True,
            "bash_command_lookup_uses_path_variable": True,
            "anchor_performs_unqualified_lookup_without_resetting_path": True,
            "onlycap_label_matches_after_transition": True,
            "smack_override_still_requires_effective_capability": True,
            "onlycap_is_a_smack_call_site_gate_not_a_capability_mask": True,
            "v028_or_session_bus_required_for_this_transition": False,
        },
        "assessment": {
            "configured_direct_app_to_onlycap_label_transition_candidate": True,
            "configured_uid_escalation": False,
            "configured_smack_override_eligibility_after_transition": True,
            "effective_smack_override_established": False,
            "runtime_root_or_persistence_demonstrated": False,
            "operational_payload_emitted": False,
        },
        "runtime_unknowns": {
            "installed_artifact_identity_matches": None,
            "policy_loaded": None,
            "anchor_access_label_is_floor": None,
            "anchor_exec_label_is_privileged": None,
            "source_task_label_is_enumerated_app_domain": None,
            "source_uid_is_zero": None,
            "source_capability_sets_include_mac_override_and_admin": None,
            "source_securebits_preserve_root_capability_semantics": None,
            "source_no_new_privs_is_clear": None,
            "source_is_not_unsafely_ptraced_or_fs_shared": None,
            "pathname_traversal_and_mount_exec_checks_allow_anchor": None,
            "pretransition_read_and_execute_admission_succeeds": None,
            "anchor_exec_reaches_credential_commit": None,
            "anchor_interpreter_completes_loading": None,
            "caller_controls_or_influences_environment": None,
            "caller_controls_or_influences_path": None,
            "environment_function_import_is_runtime_relevant": None,
            "path_resolves_an_executable_object_before_stock_utility": None,
            "resolved_object_access_and_exec_labels": None,
            "posttransition_smack_privileged_mac_override_succeeds": None,
            "unqualified_command_exec_succeeds": None,
            "resulting_task_uid_capabilities_and_label": None,
            "useful_writable_persistence_anchor_exists": None,
            "update_or_boot_acceptance": None,
        },
        "limits": [
            "Canonical archive configuration is not owner-unit runtime state.",
            "The ordinary inode access label and pre-transition subject control read/execute admission; SMACK64EXEC does not authorize opening the file.",
            "Execute-label transition changes the SMACK task label, not UID, capabilities, mount flags, or bytes.",
            "Credential commitment is not synonymous with complete successful ELF loading; later loader work can still fail.",
            "Named interface/string evidence in the exact bash binary is bounded corroboration; hash-bound public source supplies the semantic model.",
            "Environment influence, function-import relevance, PATH influence, and a suitable executable object are runtime preconditions, not static facts.",
            "onlycap does not change Linux capability masks; it gates smack_privileged() call sites by current SMACK label.",
            "No update authentication, partition write, slot activation, boot acceptance, mark-good, rollback, or recovery result is established.",
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rootfs", required=True, type=Path)
    parser.add_argument("--bash", required=True, type=Path)
    parser.add_argument("--smack-lsm", required=True, type=Path)
    parser.add_argument("--smack-header", required=True, type=Path)
    parser.add_argument("--exec-source", required=True, type=Path)
    parser.add_argument("--binfmt-script", required=True, type=Path)
    parser.add_argument("--binfmt-elf", required=True, type=Path)
    parser.add_argument("--commoncap", required=True, type=Path)
    parser.add_argument("--bash-shell", required=True, type=Path)
    parser.add_argument("--bash-variables", required=True, type=Path)
    parser.add_argument("--bash-findcmd", required=True, type=Path)
    parser.add_argument("--glibc-rtld", required=True, type=Path)
    parser.add_argument("--glibc-unsecvars", required=True, type=Path)
    parser.add_argument("--glibc-extra-unsecvars", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    sources = {
        "smack_lsm": args.smack_lsm,
        "smack_header": args.smack_header,
        "exec": args.exec_source,
        "binfmt_script": args.binfmt_script,
        "binfmt_elf": args.binfmt_elf,
        "commoncap": args.commoncap,
        "bash_shell": args.bash_shell,
        "bash_variables": args.bash_variables,
        "bash_findcmd": args.bash_findcmd,
        "glibc_rtld": args.glibc_rtld,
        "glibc_unsecvars": args.glibc_unsecvars,
        "glibc_extra_unsecvars": args.glibc_extra_unsecvars,
    }
    try:
        report = build_report(args.rootfs, args.bash, sources)
    except BoundaryError as exc:
        sys.stderr.buffer.write((f"error: {exc}\n").encode("utf-8"))
        return 2
    raw = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True).encode("utf-8") + b"\n"
    sys.stdout.buffer.write(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
