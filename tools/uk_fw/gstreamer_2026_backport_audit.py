#!/usr/bin/env python3
"""Audit exact GStreamer CVE-2026-2921/2922 backport state offline.

The analyzer streams two selected regular members from one pinned rootfs tar,
validates exact LLVM identities, and checks bounded instruction/FDE evidence.
It never executes a recovered target and never creates or parses media input.
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
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
TOOL_NAME = "gstreamer-2026-backport-audit"
TOOL_VERSION = "1.0.0"
MAX_ROOTFS_SIZE = 1 << 30
MAX_MANIFEST_SIZE = 1 << 20
MAX_MEMBER_SIZE = 2 << 20
MAX_TOOL_SIZE = 16 << 20
MAX_TOOL_OUTPUT = 128 << 20
MAX_STDERR = 1 << 20

ROOTFS_SHA256 = "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84"
MEMBER_NAMES = {
    "riff": "./usr/lib/libgstriff-1.0.so.0.803.0",
    "realmedia": "./usr/lib/gstreamer-1.0/libgstrmdemux.so",
}
MEMBER_IDENTITIES = {
    "riff": {
        "size": 59256,
        "sha256": "7ba228a5fed61f45b4f5b547e22e37ce18f23246dbe88d5231736006cc473396",
        "build_id": "44aa3041663b7bec8f33c4d730704867af39b56b",
        "fde": (0x1D50, 0x51D0),
    },
    "realmedia": {
        "size": 142128,
        "sha256": "8bcb86554f54f38b6c78cd0b9754a7ba9d546399128353ab658f1424b8ccb5f0",
        "build_id": "ee26bea186ce1052d6b38285dfb55131899fd16c",
        "fde": (0xB780, 0xE649),
    },
}
RIFF_EXPORT = ("gst_riff_create_video_caps", 0x1D50)
COMMITS = {
    "riff_checked_multiplication_fix": "66d1f79c78b573db714434cf08e7531bed4f4473",
    "rm_primary_pre_store_fix": "8a17c9d183ca3cfb5e97ae3b3f344ba79f8859df",
    "rm_companion_extent_fix": "cfc74588fca99328419eb16921fa559739a7b503",
}

# Exact Homebrew LLVM-rendered rows. Full instruction and FDE identities are
# separately pinned in the manifest; these rows support bounded semantics.
REQUIRED_ANCHORS: dict[str, dict[str, tuple[int, str, str]]] = {
    "riff": {
        "strf-pointer-test": (0x24C6, "testq", "%rbp, %rbp"),
        "strf-null-default-branch": (
            0x24C9, "je", "0x2d50 <gst_riff_create_video_caps+0x1000>"
        ),
        "num-colors-32-bit-load": (0x24CF, "movl", "0x20(%rbp), %ebp"),
        "num-colors-32-bit-shift": (0x24D2, "shll", "$0x2, %ebp"),
        "palette-buffer-argument": (0x24D5, "movq", "%r14, %rdi"),
        "palette-size-call": (0x24D8, "callq", "0x1870 <gst_buffer_get_size@plt>"),
        "available-size-save": (0x24DD, "movq", "%rax, %r12"),
        "wrapped-product-size-compare": (0x24E0, "cmpq", "%rbp, %rax"),
        "unsigned-accept-branch": (
            0x24E3, "jae", "0x2ca0 <gst_riff_create_video_caps+0xf50>"
        ),
        "accepted-allocation": (0x2CAF, "callq", "0x19c0 <g_malloc0@plt>"),
        "accepted-extraction": (0x2CC2, "callq", "0x1a00 <gst_buffer_extract@plt>"),
        "default-palette-size": (
            0x2D50, "movl", "$0x400, %ebp            # imm = 0x400"
        ),
        "default-rejoin": (
            0x2D55, "jmp", "0x24d5 <gst_riff_create_video_caps+0x785>"
        ),
    },
    "realmedia": {
        "fragment-data-pointer": (0xD566, "movq", "0x40(%rsp), %rdx"),
        "fragment-length-zero-extend": (0xD56B, "movl", "%ebp, %r12d"),
        "copy-region-flags": (0xD56E, "movl", "$0xf, %esi"),
        "fragment-offset": (0xD578, "subq", "0x110(%rsp), %rdx"),
        "copy-region-length": (0xD580, "movq", "%r12, %rcx"),
        "copy-region-input-buffer": (0xD583, "movq", "0x20(%rsp), %rdi"),
        "fragment-copy-call": (0xD588, "callq", "0x5910 <gst_buffer_copy_region@plt>"),
        "adapter-insertion-start": (0xD603, "movq", "0x58(%rsp), %rsi"),
        "adapter-pointer-load": (0xD608, "movq", "0x4b0(%r13), %rdi"),
        "adapter-push-call": (0xD60F, "callq", "0x5520 <gst_adapter_push@plt>"),
        "fragment-count-load": (0xD614, "movl", "0xac(%r13), %edx"),
        "fragment-current-load": (0xD61B, "movl", "0xa8(%r13), %eax"),
        "count-to-index": (0xD622, "movq", "%rdx, %rsi"),
        "fragment-size-add": (0xD625, "addl", "%eax, %ebp"),
        "count-increment": (0xD627, "addl", "$0x1, %esi"),
        "indexed-offset-store": (0xD62A, "movl", "%eax, 0xb0(%r13,%rdx,4)"),
        "new-current-store": (0xD632, "movl", "%ebp, 0xa8(%r13)"),
        "incremented-count-store": (0xD639, "movl", "%esi, 0xac(%r13)"),
        "post-store-max-compare": (
            0xD640, "cmpl", "$0x100, %esi            # imm = 0x100"
        ),
        "post-store-error-branch": (0xD646, "ja", "0xdcf5 <.text+0x7fb5>"),
        "later-remaining-size-subtract": (0xD99C, "subq", "%r12, %rbx"),
        "max-frags-error-value": (
            0xDCF5, "movl", "$0x100, %edx            # imm = 0x100"
        ),
        "max-frags-error-call": (
            0xDD0C, "callq", "0x5960 <_gst_element_error_printf@plt>"
        ),
    },
}


class AuditError(ValueError):
    """Evidence or input is malformed or outside the supported exact state."""


@dataclass(frozen=True)
class Instruction:
    address: int
    mnemonic: str
    operands: str

    @property
    def canonical(self) -> str:
        return f"{self.address:x}\t{self.mnemonic}\t{self.operands}"


def _stat_regular(path: Path, maximum: int, what: str) -> os.stat_result:
    try:
        result = path.stat()
    except OSError as exc:
        raise AuditError(f"cannot stat {what}: {exc.strerror}") from exc
    if not stat.S_ISREG(result.st_mode):
        raise AuditError(f"{what} is not a regular file")
    if result.st_size > maximum:
        raise AuditError(f"{what} exceeds the size limit")
    return result


def _same_stat(before: os.stat_result, after: os.stat_result) -> bool:
    return all(
        getattr(before, key) == getattr(after, key)
        for key in ("st_dev", "st_ino", "st_size", "st_mtime_ns")
    )


def _read_regular(path: Path, maximum: int, what: str) -> bytes:
    before = _stat_regular(path, maximum, what)
    try:
        with path.open("rb") as handle:
            raw = handle.read(before.st_size + 1)
            descriptor_after = os.fstat(handle.fileno())
    except OSError as exc:
        raise AuditError(f"cannot read {what}: {exc.strerror}") from exc
    after = _stat_regular(path, maximum, what)
    if (
        len(raw) != before.st_size
        or not _same_stat(before, after)
        or not _same_stat(before, descriptor_after)
    ):
        raise AuditError(f"{what} changed while being read")
    return raw


def _object(value: Any, keys: Iterable[str], what: str) -> dict[str, Any]:
    expected = set(keys)
    if type(value) is not dict:
        raise AuditError(f"{what} must be an object")
    actual = set(value)
    if actual != expected:
        raise AuditError(
            f"{what} keys mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )
    return value


def _array(value: Any, what: str, maximum: int = 4096) -> list[Any]:
    if type(value) is not list or len(value) > maximum:
        raise AuditError(f"{what} must be a bounded array")
    return value


def _integer(value: Any, what: str, maximum: int = (1 << 63) - 1) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise AuditError(f"{what} must be a bounded non-Boolean integer")
    return value


def _boolean(value: Any, what: str) -> bool:
    if type(value) is not bool:
        raise AuditError(f"{what} must be a Boolean")
    return value


def _string(value: Any, what: str, maximum: int = 4096, *, empty: bool = False) -> str:
    if type(value) is not str or (not empty and not value) or len(value) > maximum:
        qualifier = "string" if empty else "non-empty string"
        raise AuditError(f"{what} must be a bounded {qualifier}")
    return value


def _digest(value: Any, what: str) -> str:
    text = _string(value, what, 64)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise AuditError(f"{what} must be lowercase SHA-256")
    return text


def _hex_identity(value: Any, what: str, maximum: int = 128) -> str:
    text = _string(value, what, maximum)
    if not re.fullmatch(r"[0-9a-f]+", text):
        raise AuditError(f"{what} must be lowercase hexadecimal")
    return text


def _commit(value: Any, what: str) -> str:
    text = _hex_identity(value, what, 40)
    if len(text) != 40:
        raise AuditError(f"{what} must be a full 40-character commit identity")
    return text


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuditError(f"manifest contains duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_manifest(path: Path) -> dict[str, Any]:
    raw = _read_regular(path, MAX_MANIFEST_SIZE, "manifest")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError("manifest is not valid UTF-8 JSON") from exc
    top = _object(value, {"schema_version", "artifacts", "llvm", "expected"}, "manifest")
    if _integer(top["schema_version"], "schema_version") != SCHEMA_VERSION:
        raise AuditError("unsupported manifest schema version")

    artifacts = _object(top["artifacts"], {"rootfs", "members"}, "artifacts")
    root = _object(
        artifacts["rootfs"],
        {"sha256", "size", "member_count", "inventory_sha256"},
        "artifacts.rootfs",
    )
    root_out = {
        "sha256": _digest(root["sha256"], "rootfs.sha256"),
        "size": _integer(root["size"], "rootfs.size", MAX_ROOTFS_SIZE),
        "member_count": _integer(root["member_count"], "rootfs.member_count", 1_000_000),
        "inventory_sha256": _digest(root["inventory_sha256"], "rootfs.inventory_sha256"),
    }
    if root_out != {
        "sha256": ROOTFS_SHA256,
        "size": 879109759,
        "member_count": 66836,
        "inventory_sha256": "c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c",
    }:
        raise AuditError("unsupported canonical rootfs identity/inventory")

    members: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(_array(artifacts["members"], "artifacts.members", 8)):
        row = _object(
            item,
            {
                "role", "name", "type", "mode", "size", "sha256", "build_id",
                "instruction_count", "instruction_sha256", "fde_count", "fde_sha256",
                "selected_fde", "anchors",
            },
            f"member {index}",
        )
        role = _string(row["role"], "member.role", 32)
        if role in members:
            raise AuditError("manifest contains a duplicate member role")
        selected = _object(row["selected_fde"], {"start", "end_exclusive"}, "selected_fde")
        fde = (
            _integer(selected["start"], "selected_fde.start"),
            _integer(selected["end_exclusive"], "selected_fde.end_exclusive"),
        )
        if fde[0] >= fde[1]:
            raise AuditError("selected FDE range is malformed")
        anchors: dict[str, dict[str, Any]] = {}
        addresses: set[int] = set()
        for anchor_index, anchor_value in enumerate(_array(row["anchors"], "anchors", 64)):
            anchor = _object(
                anchor_value,
                {"role", "address", "mnemonic", "operands", "sha256"},
                f"anchor {anchor_index}",
            )
            anchor_role = _string(anchor["role"], "anchor.role", 96)
            address = _integer(anchor["address"], "anchor.address")
            mnemonic = _string(anchor["mnemonic"], "anchor.mnemonic", 32)
            operands = _string(anchor["operands"], "anchor.operands", 256, empty=True)
            if not re.fullmatch(r"[a-z][a-z0-9.]*", mnemonic):
                raise AuditError("anchor instruction mnemonic is malformed")
            if anchor_role in anchors or address in addresses:
                raise AuditError("manifest contains duplicate anchor role/address")
            addresses.add(address)
            canonical = f"{address:x}\t{mnemonic}\t{operands}"
            anchor_hash = _digest(anchor["sha256"], "anchor.sha256")
            if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != anchor_hash:
                raise AuditError("anchor canonical hash does not match its instruction")
            anchors[anchor_role] = {
                "address": address,
                "mnemonic": mnemonic,
                "operands": operands,
                "sha256": anchor_hash,
            }
        members[role] = {
            "role": role,
            "name": _string(row["name"], "member.name", 512),
            "type": _string(row["type"], "member.type", 32),
            "mode": _integer(row["mode"], "member.mode", 0o7777),
            "size": _integer(row["size"], "member.size", MAX_MEMBER_SIZE),
            "sha256": _digest(row["sha256"], "member.sha256"),
            "build_id": _hex_identity(row["build_id"], "member.build_id"),
            "instruction_count": _integer(
                row["instruction_count"], "member.instruction_count", 1_000_000
            ),
            "instruction_sha256": _digest(
                row["instruction_sha256"], "member.instruction_sha256"
            ),
            "fde_count": _integer(row["fde_count"], "member.fde_count", 100_000),
            "fde_sha256": _digest(row["fde_sha256"], "member.fde_sha256"),
            "selected_fde": fde,
            "anchors": anchors,
        }
    if set(members) != set(MEMBER_NAMES):
        raise AuditError("member role set does not match the supported audit")
    for role, row in members.items():
        identity = MEMBER_IDENTITIES[role]
        if (
            row["name"] != MEMBER_NAMES[role]
            or row["type"] != "regular"
            or row["mode"] != 0o755
            or row["size"] != identity["size"]
            or row["sha256"] != identity["sha256"]
            or row["build_id"] != identity["build_id"]
            or row["selected_fde"] != identity["fde"]
        ):
            raise AuditError(f"{role} exact identity/range state is unsupported")
        actual = {
            name: (anchor["address"], anchor["mnemonic"], anchor["operands"])
            for name, anchor in row["anchors"].items()
        }
        if actual != REQUIRED_ANCHORS[role]:
            raise AuditError(f"{role} anchor set does not match the supported audit")

    llvm_obj = _object(top["llvm"], {"version", "objdump", "readelf"}, "llvm")
    llvm: dict[str, Any] = {"version": _string(llvm_obj["version"], "llvm.version", 128)}
    for name in ("objdump", "readelf"):
        tool = _object(llvm_obj[name], {"size", "sha256"}, f"llvm.{name}")
        llvm[name] = {
            "size": _integer(tool["size"], f"llvm.{name}.size", MAX_TOOL_SIZE),
            "sha256": _digest(tool["sha256"], f"llvm.{name}.sha256"),
        }

    expected_obj = _object(top["expected"], set(COMMITS), "expected")
    expected = {name: _commit(expected_obj[name], f"expected.{name}") for name in COMMITS}
    if expected != COMMITS:
        raise AuditError("upstream implementation-fix lineage does not match the supported audit")
    return {
        "rootfs": root_out,
        "members": members,
        "llvm": llvm,
        "expected": expected,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _canonical_member_name(name: str) -> str:
    if (
        type(name) is not str
        or not name
        or name.startswith("/")
        or any(ord(char) < 0x20 or ord(char) == 0x7F for char in name)
    ):
        raise AuditError("archive member name is invalid")
    if name in (".", "./"):
        return "."
    parts = name.split("/")
    while parts and parts[0] == ".":
        parts.pop(0)
    if parts and parts[-1] == "":
        parts.pop()
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise AuditError("archive member name is non-canonical or unsafe")
    canonical = posixpath.normpath("/".join(parts))
    if canonical == ".." or canonical.startswith("../"):
        raise AuditError("archive member escapes the archive root")
    return canonical


class _HashingReader:
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


def _inventory_line(index: int, member: tarfile.TarInfo) -> bytes:
    try:
        return (
            f"{index}\t{member.name}\t{member.type.hex()}\t{member.mode:o}\t"
            f"{member.size}\t{member.linkname}\n"
        ).encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise AuditError("archive inventory is not UTF-8") from exc


def _audit_archive(
    path: Path,
    artifact: dict[str, Any],
    selected_rows: dict[str, dict[str, Any]],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    before = _stat_regular(path, MAX_ROOTFS_SIZE, "rootfs archive")
    selected_by_name = {row["name"]: row for row in selected_rows.values()}
    selected_by_canonical: dict[str, str] = {}
    for name in selected_by_name:
        canonical = _canonical_member_name(name)
        if canonical in selected_by_canonical:
            raise AuditError("selected member expectation has a canonical alias")
        selected_by_canonical[canonical] = name
    found: dict[str, bytes] = {}
    inventory = hashlib.sha256()
    count = 0
    total_selected = 0
    try:
        with path.open("rb") as raw_handle:
            reader = _HashingReader(raw_handle)
            with tarfile.open(fileobj=reader, mode="r|gz") as archive:
                for index, member in enumerate(archive):
                    count += 1
                    inventory.update(_inventory_line(index, member))
                    canonical = _canonical_member_name(member.name)
                    expected_name = selected_by_canonical.get(canonical)
                    if expected_name is None:
                        continue
                    if member.name != expected_name:
                        raise AuditError("selected rootfs member is present through an archive alias")
                    if expected_name in found:
                        raise AuditError("selected rootfs member is duplicated")
                    row = selected_by_name[expected_name]
                    if (
                        not member.isreg()
                        or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                        or member.linkname
                        or member.mode != row["mode"]
                        or member.size != row["size"]
                        or member.size > MAX_MEMBER_SIZE
                    ):
                        raise AuditError(
                            f"selected rootfs member type/mode/size drift: {row['role']}"
                        )
                    total_selected += member.size
                    if total_selected > len(selected_rows) * MAX_MEMBER_SIZE:
                        raise AuditError("selected rootfs work exceeds bound")
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        raise AuditError(
                            f"selected rootfs member cannot be streamed: {row['role']}"
                        )
                    data = extracted.read(member.size + 1)
                    if len(data) != member.size:
                        raise AuditError(
                            f"selected rootfs member length drift: {row['role']}"
                        )
                    if hashlib.sha256(data).hexdigest() != row["sha256"]:
                        raise AuditError(
                            f"selected rootfs member content drift: {row['role']}"
                        )
                    found[expected_name] = data
            while reader.read(1 << 20):
                pass
            archive_digest = reader.digest.hexdigest()
            descriptor_after = os.fstat(raw_handle.fileno())
    except AuditError:
        raise
    except (tarfile.TarError, OSError) as exc:
        raise AuditError(f"cannot stream rootfs archive: {type(exc).__name__}") from exc
    after = _stat_regular(path, MAX_ROOTFS_SIZE, "rootfs archive")
    if not _same_stat(before, after) or not _same_stat(before, descriptor_after):
        raise AuditError("rootfs archive changed during analysis")
    if before.st_size != artifact["size"] or archive_digest != artifact["sha256"]:
        raise AuditError("rootfs archive identity does not match manifest")
    if count != artifact["member_count"] or inventory.hexdigest() != artifact["inventory_sha256"]:
        raise AuditError("rootfs inventory identity/count does not match manifest")
    if set(selected_by_name) - set(found):
        raise AuditError("selected rootfs members are missing")
    return (
        {row["role"]: found[row["name"]] for row in selected_rows.values()},
        {
            "sha256": archive_digest,
            "size": before.st_size,
            "member_count": count,
            "inventory_sha256": inventory.hexdigest(),
        },
    )


def _run_tool(command: list[str], what: str, maximum: int = MAX_TOOL_OUTPUT) -> bytes:
    environment = dict(os.environ)
    environment.update({"LC_ALL": "C", "LANG": "C"})
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=environment,
        )
    except OSError as exc:
        raise AuditError(f"cannot run {what}: {exc.strerror}") from exc
    if completed.returncode != 0:
        raise AuditError(f"{what} failed with status {completed.returncode}")
    if len(completed.stdout) > maximum or len(completed.stderr) > MAX_STDERR:
        raise AuditError(f"{what} output exceeds bound")
    if completed.stderr:
        raise AuditError(f"{what} produced unexpected stderr")
    return completed.stdout


def _validate_tool(path: Path, version: str, expected: dict[str, Any], what: str) -> None:
    result = _stat_regular(path, MAX_TOOL_SIZE, what)
    if not os.access(path, os.X_OK):
        raise AuditError(f"{what} is not executable")
    raw = _read_regular(path, MAX_TOOL_SIZE, what)
    if len(raw) != expected["size"] or hashlib.sha256(raw).hexdigest() != expected["sha256"]:
        raise AuditError(f"{what} file identity does not match manifest")
    try:
        lines = _run_tool([str(path), "--version"], f"{what} version", MAX_STDERR).decode(
            "utf-8", "strict"
        ).splitlines()
    except UnicodeDecodeError as exc:
        raise AuditError(f"{what} version is not UTF-8") from exc
    if not lines or lines[0] != version or result.st_size != expected["size"]:
        raise AuditError(f"{what} version identity does not match manifest")


def parse_disassembly(raw: bytes) -> list[Instruction]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError("objdump output is not UTF-8") from exc
    result: list[Instruction] = []
    seen: set[int] = set()
    active = False
    line_re = re.compile(r"^\s*([0-9a-f]+):\s+([^\s]+)(?:\s+(.*?))?\s*$")
    malformed_re = re.compile(r"^\s*[0-9a-f]+:")
    for line in text.splitlines():
        if line.startswith("Disassembly of section "):
            active = True
            continue
        match = line_re.match(line)
        if match:
            if not active:
                raise AuditError("objdump instruction appears outside a disassembly section")
            address = int(match.group(1), 16)
            mnemonic = match.group(2)
            operands = (match.group(3) or "").strip()
            if not re.fullmatch(r"[a-z][a-z0-9.]*", mnemonic):
                raise AuditError("objdump instruction mnemonic is malformed")
            if address in seen:
                raise AuditError("objdump contains a duplicate instruction address")
            seen.add(address)
            result.append(Instruction(address, mnemonic, operands))
        elif active and malformed_re.match(line):
            raise AuditError("objdump contains a malformed or truncated instruction line")
    if not result:
        raise AuditError("objdump contains no decoded instructions")
    if any(left.address >= right.address for left, right in zip(result, result[1:])):
        raise AuditError("objdump instruction addresses are not strictly increasing")
    return result


def parse_fdes(raw: bytes) -> list[tuple[int, int]]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError("readelf unwind output is not UTF-8") from exc
    pattern = re.compile(
        r"^\s*\[0x[0-9a-f]+\] FDE length=[0-9]+ cie=\[0x[0-9a-f]+\]\n"
        r"\s+initial_location: 0x([0-9a-f]+)\n"
        r"\s+address_range: 0x([0-9a-f]+) \(end : 0x([0-9a-f]+)\)$",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    headers = re.findall(r"^\s*\[0x[0-9a-f]+\] FDE length=", text, re.MULTILINE)
    if len(matches) != len(headers):
        raise AuditError("readelf contains a malformed or truncated FDE record")
    rows: list[tuple[int, int]] = []
    for match in matches:
        start, size, end = (int(match.group(index), 16) for index in (1, 2, 3))
        if size == 0 or start + size != end:
            raise AuditError("readelf contains a malformed FDE range")
        rows.append((start, end))
    if not rows:
        raise AuditError("readelf contains no FDE ranges")
    if len(set(rows)) != len(rows) or len({start for start, _ in rows}) != len(rows):
        raise AuditError("readelf contains duplicate FDE ranges")
    rows.sort()
    return rows


def parse_build_id(raw: bytes) -> str:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError("readelf note output is not UTF-8") from exc
    values = re.findall(r"Build ID: ([0-9a-f]+)", text)
    if len(values) != 1:
        raise AuditError("readelf Build ID is absent or ambiguous")
    return values[0]


def parse_exported_symbol(raw: bytes, name: str) -> int:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError("readelf dynamic-symbol output is not UTF-8") from exc
    pattern = re.compile(
        rf"^\s*\d+:\s+([0-9a-f]+)\s+[0-9]+\s+FUNC\s+GLOBAL\s+DEFAULT\s+"
        rf"[0-9]+\s+{re.escape(name)}\s*$",
        re.MULTILINE,
    )
    values = [int(match.group(1), 16) for match in pattern.finditer(text)]
    if len(values) != 1:
        raise AuditError("readelf exported symbol is absent, malformed, or ambiguous")
    return values[0]


def _canonical_hash(lines: Iterable[str]) -> str:
    return hashlib.sha256("".join(line + "\n" for line in lines).encode("utf-8")).hexdigest()


def _validate_anchors(
    role: str, instructions: list[Instruction], expected: dict[str, Any]
) -> dict[int, Instruction]:
    by_address = {item.address: item for item in instructions}
    for anchor_role, row in expected["anchors"].items():
        item = by_address.get(row["address"])
        if item is None or item.mnemonic != row["mnemonic"] or item.operands != row["operands"]:
            raise AuditError(f"{role} machine anchor drift: {anchor_role}")
        if hashlib.sha256(item.canonical.encode("utf-8")).hexdigest() != row["sha256"]:
            raise AuditError(f"{role} machine anchor hash drift: {anchor_role}")
    return by_address


def _validate_machine(
    role: str,
    instructions: list[Instruction],
    fdes: list[tuple[int, int]],
    expected: dict[str, Any],
) -> dict[str, bool]:
    by_address = _validate_anchors(role, instructions, expected)
    if expected["selected_fde"] not in fdes:
        raise AuditError(f"{role} selected FDE range drift")
    start, end = expected["selected_fde"]
    anchor_addresses = [row[0] for row in REQUIRED_ANCHORS[role].values()]
    if any(not (start <= address < end) for address in anchor_addresses):
        raise AuditError(f"{role} anchor falls outside selected FDE")

    if role == "riff":
        ordered = (
            0x24C6, 0x24C9, 0x24CF, 0x24D2, 0x24D5, 0x24D8, 0x24DD,
            0x24E0, 0x24E3, 0x2CAF, 0x2CC2,
        )
        if tuple(sorted(ordered)) != ordered:
            raise AuditError("internal RIFF ordering assertion is malformed")
        if not (
            by_address[0x24C9].operands.startswith("0x2d50 ")
            and by_address[0x24E3].operands.startswith("0x2ca0 ")
            and by_address[0x2D55].operands.startswith("0x24d5 ")
            and 0x24E3 < 0x2CAF < 0x2CC2 < 0x2D50
        ):
            raise AuditError("RIFF branch/default/accepted-path ordering drift")
        unsupported = [
            item
            for item in instructions
            if 0x24CF < item.address < 0x24E0
            and (
                item.mnemonic in {"imulq", "mulq", "jo", "jc"}
                or (item.mnemonic.startswith("mov") and "%ebp" in item.operands and "%rbp" in item.operands)
            )
        ]
        if unsupported:
            raise AuditError("RIFF contradictory checked/widened multiplication state")
        return {
            "riff_checked_multiply": False,
            "riff_wrap32": True,
            "rm_pre_store_check": False,
            "rm_store_before_check": False,
            "rm_extent_gate": False,
            "rm_copy_before_later_subtract": False,
        }

    if role == "realmedia":
        if not (
            0xD566 < 0xD56B < 0xD578 < 0xD580 < 0xD583 < 0xD588
            < 0xD603 < 0xD608 < 0xD60F < 0xD614 < 0xD61B < 0xD622
            < 0xD625 < 0xD627 < 0xD62A < 0xD632 < 0xD639 < 0xD640
            < 0xD646 < 0xD99C < 0xDCF5 < 0xDD0C
        ):
            raise AuditError("RealMedia copy/store/check ordering drift")
        if not by_address[0xD646].operands.startswith("0xdcf5 "):
            raise AuditError("RealMedia MAX_FRAGS branch target drift")
        pre_store_max_checks = [
            item
            for item in instructions
            if 0xD603 <= item.address < 0xD62A
            and item.mnemonic.startswith("cmp")
            and "$0x100" in item.operands
        ]
        if pre_store_max_checks:
            raise AuditError("RealMedia contradictory pre-store and post-store check state")
        local_extent_checks = [
            item
            for item in instructions
            if 0xD566 <= item.address < 0xD588
            and item.mnemonic.startswith(("cmp", "test"))
        ]
        if local_extent_checks:
            raise AuditError("RealMedia contradictory pre-copy extent-gate state")
        if 0xB0 + 4 * 256 != 0x4B0:
            raise AuditError("internal RealMedia field-overlap arithmetic is malformed")
        return {
            "riff_checked_multiply": False,
            "riff_wrap32": False,
            "rm_pre_store_check": False,
            "rm_store_before_check": True,
            "rm_extent_gate": False,
            "rm_copy_before_later_subtract": True,
        }
    raise AuditError("unsupported machine role")


def _validate_complete_identity(
    role: str,
    instructions: list[Instruction],
    fdes: list[tuple[int, int]],
    expected: dict[str, Any],
) -> tuple[str, str]:
    instruction_hash = _canonical_hash(item.canonical for item in instructions)
    if (
        len(instructions) != expected["instruction_count"]
        or instruction_hash != expected["instruction_sha256"]
    ):
        raise AuditError(f"{role} complete instruction identity/count drift")
    fde_hash = _canonical_hash(f"{start:x}-{end:x}" for start, end in fdes)
    if len(fdes) != expected["fde_count"] or fde_hash != expected["fde_sha256"]:
        raise AuditError(f"{role} complete FDE identity/count drift")
    return instruction_hash, fde_hash


def _derive_assessments(facts: dict[str, Any]) -> dict[str, Any]:
    expected_keys = {
        "riff_checked_multiply", "riff_wrap32", "rm_pre_store_check",
        "rm_store_before_check", "rm_extent_gate", "rm_copy_before_later_subtract",
    }
    row = _object(facts, expected_keys, "semantic facts")
    checked = {key: _boolean(row[key], f"semantic facts.{key}") for key in expected_keys}
    if checked != {
        "riff_checked_multiply": False,
        "riff_wrap32": True,
        "rm_pre_store_check": False,
        "rm_store_before_check": True,
        "rm_extent_gate": False,
        "rm_copy_before_later_subtract": True,
    }:
        raise AuditError("contradictory or unsupported semantic state")
    return {
        "riff_palette": {
            "associated_issue": "CVE-2026-2921",
            "advisory": "GST-SA-2026-0004",
            "implementation_fix_commit": COMMITS["riff_checked_multiplication_fix"],
            "upstream_patch_state": "absent",
            "checked_multiplication_invariant": "violated",
            "multiplication_width_bits": 32,
            "guard_arithmetic_wraps_for_num_colors_gte": 1 << 30,
            "safe_widening_equivalent_on_exact_architecture": True,
            "upstream_big_endian_conversion_loop_present": False,
            "exact_downstream_memory_effect": None,
            "exploitability": None,
        },
        "rm_fragment_index": {
            "associated_issue": "CVE-2026-2922",
            "advisory": "GST-SA-2026-0005",
            "primary_implementation_fix_commit": COMMITS["rm_primary_pre_store_fix"],
            "upstream_patch_state": "absent",
            "pre_store_rejection_invariant": "violated",
            "max_fragments": 256,
            "old_count_reaching_store": 256,
            "indexed_store_displacement": "0x4b0",
            "following_adapter_pointer_displacement": "0x4b0",
            "bounded_object_field_effect": "low 4 bytes of following adapter-pointer field overwritten before error",
            "exploitability": None,
        },
        "rm_fragment_extent": {
            "associated_issue": "CVE-2026-2922",
            "companion_implementation_fix_commit": COMMITS["rm_companion_extent_fix"],
            "upstream_patch_state": "absent",
            "local_pre_copy_invariant": "unsatisfied",
            "overflow_safe_fragment_le_map_and_offset_le_map_minus_fragment_gate": False,
            "later_remaining_size_subtraction_after_processing": True,
            "downstream_library_behavior": None,
            "runtime_impact": None,
        },
    }


def _analyze_member(
    role: str,
    data: bytes,
    expected: dict[str, Any],
    objdump: Path,
    readelf: Path,
    directory: Path,
) -> tuple[dict[str, Any], dict[str, bool]]:
    path = directory / f"{role}.elf"
    try:
        with path.open("xb") as handle:
            os.chmod(path, 0o600)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise AuditError(f"cannot create bounded temporary {role} copy: {exc.strerror}") from exc
    if path.stat().st_size != len(data) or path.stat().st_mode & 0o111:
        raise AuditError(f"temporary {role} copy identity/mode drift")
    disassembly = parse_disassembly(
        _run_tool(
            [str(objdump), "-d", "--no-show-raw-insn", str(path)],
            f"{role} disassembly",
        )
    )
    fdes = parse_fdes(_run_tool([str(readelf), "--unwind", str(path)], f"{role} unwind"))
    instruction_hash, fde_hash = _validate_complete_identity(
        role, disassembly, fdes, expected
    )
    build_id = parse_build_id(
        _run_tool([str(readelf), "--notes", str(path)], f"{role} notes", 8 << 20)
    )
    if build_id != expected["build_id"]:
        raise AuditError(f"{role} Build ID drift")
    facts = _validate_machine(role, disassembly, fdes, expected)
    result = {
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "build_id": build_id,
        "instruction_count": len(disassembly),
        "instruction_sha256": instruction_hash,
        "fde_count": len(fdes),
        "fde_sha256": fde_hash,
        "selected_fde": {
            "start": f"0x{expected['selected_fde'][0]:x}",
            "end_exclusive": f"0x{expected['selected_fde'][1]:x}",
        },
        "verified_anchor_roles": list(expected["anchors"]),
    }
    if role == "riff":
        name, address = RIFF_EXPORT
        actual = parse_exported_symbol(
            _run_tool(
                [str(readelf), "--dyn-symbols", str(path)],
                "riff dynamic symbols",
                8 << 20,
            ),
            name,
        )
        if actual != address:
            raise AuditError("RIFF exported symbol address drift")
        result["exported_symbol"] = {"name": name, "address": f"0x{actual:x}"}
    return result, facts


def analyze(
    rootfs_path: Path,
    objdump_path: Path,
    readelf_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    _validate_tool(
        objdump_path, manifest["llvm"]["version"], manifest["llvm"]["objdump"], "llvm-objdump"
    )
    _validate_tool(
        readelf_path, manifest["llvm"]["version"], manifest["llvm"]["readelf"], "llvm-readelf"
    )
    member_bytes, root = _audit_archive(rootfs_path, manifest["rootfs"], manifest["members"])
    with tempfile.TemporaryDirectory(prefix="gst-2026-static-audit-") as temporary:
        directory = Path(temporary)
        analyzed: dict[str, Any] = {}
        machine_facts: dict[str, dict[str, bool]] = {}
        for role in ("riff", "realmedia"):
            analyzed[role], machine_facts[role] = _analyze_member(
                role,
                member_bytes[role],
                manifest["members"][role],
                objdump_path,
                readelf_path,
                directory,
            )

    facts = {
        "riff_checked_multiply": machine_facts["riff"]["riff_checked_multiply"],
        "riff_wrap32": machine_facts["riff"]["riff_wrap32"],
        "rm_pre_store_check": machine_facts["realmedia"]["rm_pre_store_check"],
        "rm_store_before_check": machine_facts["realmedia"]["rm_store_before_check"],
        "rm_extent_gate": machine_facts["realmedia"]["rm_extent_gate"],
        "rm_copy_before_later_subtract": machine_facts["realmedia"][
            "rm_copy_before_later_subtract"
        ],
    }
    assessments = _derive_assessments(facts)

    manifest_raw = _read_regular(manifest_path, MAX_MANIFEST_SIZE, "manifest")
    if hashlib.sha256(manifest_raw).hexdigest() != manifest["manifest_sha256"]:
        raise AuditError("manifest changed during analysis")
    for path, name in ((objdump_path, "objdump"), (readelf_path, "readelf")):
        raw = _read_regular(path, MAX_TOOL_SIZE, f"llvm-{name}")
        expected = manifest["llvm"][name]
        if len(raw) != expected["size"] or hashlib.sha256(raw).hexdigest() != expected["sha256"]:
            raise AuditError(f"llvm-{name} changed during analysis")

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "canonical_rootfs": root,
        "members": analyzed,
        "assessments": assessments,
        "outcomes": {
            "delivery": None,
            "parser_execution": None,
            "crash": None,
            "information_disclosure": None,
            "code_execution": None,
            "privilege_gain": None,
            "root": None,
            "persistence": None,
            "exact_installed_runtime_reachability": None,
        },
        "scope": {
            "offline_exact_static_analysis": True,
            "canonical_tar_members_streamed_directly": True,
            "recovered_targets_executed": False,
            "plugins_loaded": False,
            "media_inputs_created_loaded_or_parsed": False,
            "malformed_media_emitted": False,
            "trigger_recipe_emitted": False,
            "callable_target_coordinates_emitted": False,
            "proprietary_binary_retained": False,
            "full_disassembly_retained": False,
            "operational_device_procedure_emitted": False,
            "manifest_sha256": manifest["manifest_sha256"],
            "llvm_version": manifest["llvm"]["version"],
        },
    }


def _write_json(value: Any) -> None:
    raw = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    sys.stdout.buffer.write(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--rootfs", required=True, type=Path)
    parser.add_argument("--llvm-objdump", required=True, type=Path)
    parser.add_argument("--llvm-readelf", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = analyze(args.rootfs, args.llvm_objdump, args.llvm_readelf, args.manifest)
    except AuditError as exc:
        sys.stderr.buffer.write((f"error: {exc}\n").encode("utf-8"))
        return 2
    _write_json(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
