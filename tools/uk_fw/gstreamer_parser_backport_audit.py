#!/usr/bin/env python3
"""Audit two exact GStreamer parser backport states without target execution.

The analyzer streams selected regular members directly from the canonical
rootfs tar archive, validates exact LLVM tool identities, and performs bounded
instruction/FDE assertions.  It never executes a recovered target and never
creates parser input.
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
TOOL_NAME = "gstreamer-parser-backport-audit"
TOOL_VERSION = "1.0.0"
MAX_ROOTFS_SIZE = 1 << 30
MAX_MANIFEST_SIZE = 1 << 20
MAX_MEMBER_SIZE = 2 << 20
MAX_TOOL_SIZE = 16 << 20
MAX_TOOL_OUTPUT = 128 << 20

ROOTFS_SHA256 = "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84"
MEMBER_NAMES = {
    "subparse": "./usr/lib/gstreamer-1.0/libgstsubparse.so",
    "typefind": "./usr/lib/gstreamer-1.0/libgsttypefindfunctions.so",
}
MEMBER_IDENTITIES = {
    "subparse": {
        "sha256": "8814f320ebb3ec9558e9455baaecf25ff51f527c49bd8ee716eae288fc564c1e",
        "build_id": "0f86f3c35000b43071f28990a5d9e9b34140ed52",
        "fde": (0xB7B0, 0xB9BF),
    },
    "typefind": {
        "sha256": "d772d31a2b64d393a72844bbfeba2f0efa12b93d6bf87f37818823958668df30",
        "build_id": "224dc195678a0319cf6319c5db46551bc1d46740",
        "fde": (0x2CA0, 0x2D8B),
    },
}
COMMITS = {
    "subparse_nonzero_length_fix": "d894c19db62ce87115317616f0a5d4482d6332c4",
    "typefind_initial_length_fix": "2fdccfd64fc609e44e9c4b8eed5bfdc0ab9c9095",
    "typefind_complete_length_correction": "a3bf3094d17dded324c713d5d55968caa779a895",
}

# Exact LLVM-rendered instructions.  The strict manifest repeats these rows and
# hashes each canonical row; this mapping also supplies semantic assertions that
# are independent of the manifest's claimed conclusion.
REQUIRED_ANCHORS: dict[str, dict[str, tuple[int, str, str]]] = {
    "subparse": {
        "strlen-call": (0xB86B, "callq", "0x4d00 <strlen@plt>"),
        "length-zero-test": (0xB870, "testq", "%rax, %rax"),
        "zero-length-skip": (0xB873, "je", "0xb88d <.text+0x659d>"),
        "last-byte-address": (0xB875, "leaq", "-0x1(%rbx,%rax), %rcx"),
        "last-byte-read": (0xB87A, "movzbl", "(%rcx), %eax"),
        "double-quote-check": (0xB87D, "cmpb", "$0x22, %al"),
        "double-quote-write-branch": (0xB87F, "je", "0xb928 <.text+0x6638>"),
        "single-quote-check": (0xB885, "cmpb", "$0x27, %al"),
        "single-quote-write-branch": (0xB887, "je", "0xb928 <.text+0x6638>"),
        "zero-length-continuation": (0xB88D, "movq", "0x28(%rsp), %rax"),
        "terminal-byte-write": (0xB928, "movb", "$0x0, (%rcx)"),
    },
    "typefind": {
        "get-length-call": (0x2CB9, "callq", "0x1c90 <gst_type_find_get_length@plt>"),
        "initial-17-compare": (0x2CBE, "cmpq", "$0x11, %rax"),
        "greater-than-17-branch": (0x2CC2, "jg", "0x2ce0 <.text+0x1030>"),
        "short-return-start": (0x2CC4, "movq", "0x8(%rsp), %rax"),
        "short-return-stack": (0x2CD8, "addq", "$0x18, %rsp"),
        "short-return": (0x2CDE, "retq", ""),
        "peek-offset-zero": (0x2CE0, "xorl", "%esi, %esi"),
        "peek-six-byte-length": (0x2CE2, "movl", "$0x6, %edx"),
        "save-total-length": (0x2CEA, "movq", "%rax, %rbp"),
        "peek-call": (0x2CED, "callq", "0x1b20 <gst_type_find_peek@plt>"),
        "peek-null-test": (0x2CF2, "testq", "%rax, %rax"),
        "peek-null-return": (0x2CF5, "je", "0x2cc4 <.text+0x1014>"),
        "type-one-branch": (0x2D1B, "je", "0x2d79 <.text+0x10c9>"),
        "size-field-read": (0x2D1D, "movl", "0xe(%rax), %edx"),
        "offset-field-read": (0x2D20, "movl", "0x12(%rax), %eax"),
    },
}


class AuditError(ValueError):
    """Evidence or input falls outside the supported exact audit."""


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
    return all(getattr(before, key) == getattr(after, key)
               for key in ("st_dev", "st_ino", "st_size", "st_mtime_ns"))


def _read_regular(path: Path, maximum: int, what: str) -> bytes:
    before = _stat_regular(path, maximum, what)
    try:
        with path.open("rb") as handle:
            raw = handle.read(before.st_size + 1)
            descriptor_after = os.fstat(handle.fileno())
    except OSError as exc:
        raise AuditError(f"cannot read {what}: {exc.strerror}") from exc
    after = _stat_regular(path, maximum, what)
    if (len(raw) != before.st_size or not _same_stat(before, after)
            or not _same_stat(before, descriptor_after)):
        raise AuditError(f"{what} changed while being read")
    return raw


def _object(value: Any, keys: Iterable[str], what: str) -> dict[str, Any]:
    expected = set(keys)
    if type(value) is not dict:
        raise AuditError(f"{what} must be an object")
    actual = set(value)
    if actual != expected:
        raise AuditError(
            f"{what} keys mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
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


def _string(value: Any, what: str, maximum: int = 4096, *, empty: bool = False) -> str:
    if type(value) is not str or (not empty and not value) or len(value) > maximum:
        raise AuditError(f"{what} must be a bounded {'string' if empty else 'non-empty string'}")
    return value


def _digest(value: Any, what: str) -> str:
    text = _string(value, what, 64)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise AuditError(f"{what} must be lowercase SHA-256")
    return text


def _build_id(value: Any, what: str) -> str:
    text = _string(value, what, 128)
    if not re.fullmatch(r"[0-9a-f]+", text):
        raise AuditError(f"{what} must be lowercase hexadecimal")
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
    root = _object(artifacts["rootfs"],
                   {"sha256", "size", "member_count", "inventory_sha256"}, "artifacts.rootfs")
    root_out = {
        "sha256": _digest(root["sha256"], "rootfs.sha256"),
        "size": _integer(root["size"], "rootfs.size", MAX_ROOTFS_SIZE),
        "member_count": _integer(root["member_count"], "rootfs.member_count", 1_000_000),
        "inventory_sha256": _digest(root["inventory_sha256"], "rootfs.inventory_sha256"),
    }
    if root_out["sha256"] != ROOTFS_SHA256:
        raise AuditError("unsupported canonical rootfs identity")

    members: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(_array(artifacts["members"], "artifacts.members", 8)):
        row = _object(item, {
            "role", "name", "type", "mode", "size", "sha256", "build_id",
            "instruction_count", "instruction_sha256", "fde_count", "fde_sha256",
            "selected_fde", "anchors",
        }, f"member {index}")
        role = _string(row["role"], "member.role", 32)
        if role in members:
            raise AuditError("manifest contains a duplicate member role")
        selected_fde = _object(row["selected_fde"], {"start", "end_exclusive"}, "selected_fde")
        fde = (
            _integer(selected_fde["start"], "selected_fde.start"),
            _integer(selected_fde["end_exclusive"], "selected_fde.end_exclusive"),
        )
        if fde[0] >= fde[1]:
            raise AuditError("selected FDE range is malformed")
        anchors: dict[str, dict[str, Any]] = {}
        addresses: set[int] = set()
        for anchor_index, anchor_value in enumerate(_array(row["anchors"], "anchors", 64)):
            anchor = _object(anchor_value,
                             {"role", "address", "mnemonic", "operands", "sha256"},
                             f"anchor {anchor_index}")
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
                "address": address, "mnemonic": mnemonic,
                "operands": operands, "sha256": anchor_hash,
            }
        members[role] = {
            "role": role,
            "name": _string(row["name"], "member.name", 512),
            "type": _string(row["type"], "member.type", 32),
            "mode": _integer(row["mode"], "member.mode", 0o7777),
            "size": _integer(row["size"], "member.size", MAX_MEMBER_SIZE),
            "sha256": _digest(row["sha256"], "member.sha256"),
            "build_id": _build_id(row["build_id"], "member.build_id"),
            "instruction_count": _integer(row["instruction_count"], "member.instruction_count", 1_000_000),
            "instruction_sha256": _digest(row["instruction_sha256"], "member.instruction_sha256"),
            "fde_count": _integer(row["fde_count"], "member.fde_count", 100_000),
            "fde_sha256": _digest(row["fde_sha256"], "member.fde_sha256"),
            "selected_fde": fde,
            "anchors": anchors,
        }
    if set(members) != set(MEMBER_NAMES):
        raise AuditError("member role set does not match the supported audit")
    for role, row in members.items():
        identity = MEMBER_IDENTITIES[role]
        if (row["name"] != MEMBER_NAMES[role] or row["type"] != "regular"
                or row["sha256"] != identity["sha256"]
                or row["build_id"] != identity["build_id"]
                or row["selected_fde"] != identity["fde"]):
            raise AuditError(f"{role} exact identity/range state is unsupported")
        required = REQUIRED_ANCHORS[role]
        actual = {name: (item["address"], item["mnemonic"], item["operands"])
                  for name, item in row["anchors"].items()}
        if actual != required:
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
    expected = {name: _build_id(expected_obj[name], f"expected.{name}") for name in COMMITS}
    if expected != COMMITS:
        raise AuditError("upstream commit semantics do not match the supported audit")
    return {
        "rootfs": root_out,
        "members": members,
        "llvm": llvm,
        "expected": expected,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _canonical_member_name(name: str) -> str:
    if (type(name) is not str or not name or name.startswith("/")
            or any(ord(char) < 0x20 or ord(char) == 0x7F for char in name)):
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
        return (f"{index}\t{member.name}\t{member.type.hex()}\t{member.mode:o}\t"
                f"{member.size}\t{member.linkname}\n").encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise AuditError("archive inventory is not UTF-8") from exc


def _audit_archive(path: Path, artifact: dict[str, Any],
                   selected_rows: dict[str, dict[str, Any]]) -> tuple[dict[str, bytes], dict[str, Any]]:
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
                    if (not member.isreg()
                            or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                            or member.linkname or member.mode != row["mode"]
                            or member.size != row["size"] or member.size > MAX_MEMBER_SIZE):
                        raise AuditError(f"selected rootfs member type/mode/size drift: {row['role']}")
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        raise AuditError(f"selected rootfs member cannot be streamed: {row['role']}")
                    data = extracted.read(member.size + 1)
                    if len(data) != member.size:
                        raise AuditError(f"selected rootfs member length drift: {row['role']}")
                    if hashlib.sha256(data).hexdigest() != row["sha256"]:
                        raise AuditError(f"selected rootfs member content drift: {row['role']}")
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
    missing = set(selected_by_name) - set(found)
    if missing:
        raise AuditError("selected rootfs members are missing")
    role_bytes = {row["role"]: found[row["name"]] for row in selected_rows.values()}
    return role_bytes, {
        "sha256": archive_digest,
        "size": before.st_size,
        "member_count": count,
        "inventory_sha256": inventory.hexdigest(),
    }


def _run_tool(command: list[str], what: str, maximum: int = MAX_TOOL_OUTPUT) -> bytes:
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except OSError as exc:
        raise AuditError(f"cannot run {what}: {exc.strerror}") from exc
    if completed.returncode != 0:
        raise AuditError(f"{what} failed with status {completed.returncode}")
    if len(completed.stdout) > maximum or len(completed.stderr) > 1 << 20:
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
        lines = _run_tool([str(path), "--version"], f"{what} version", 1 << 20).decode("utf-8", "strict").splitlines()
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
        r"\s+address_range: 0x([0-9a-f]+) \(end : 0x([0-9a-f]+)\)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    headers = re.findall(r"^\s*\[0x[0-9a-f]+\] FDE length=", text, re.MULTILINE)
    if len(matches) != len(headers):
        raise AuditError("readelf contains a malformed or truncated FDE record")
    rows: list[tuple[int, int]] = []
    for match in matches:
        start, size, end = (int(match.group(i), 16) for i in (1, 2, 3))
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


def _canonical_hash(lines: Iterable[str]) -> str:
    return hashlib.sha256("".join(line + "\n" for line in lines).encode("utf-8")).hexdigest()


def _validate_machine(role: str, instructions: list[Instruction], fdes: list[tuple[int, int]],
                      expected: dict[str, Any]) -> None:
    by_address = {item.address: item for item in instructions}
    for anchor_role, row in expected["anchors"].items():
        item = by_address.get(row["address"])
        if item is None or item.mnemonic != row["mnemonic"] or item.operands != row["operands"]:
            raise AuditError(f"{role} machine anchor drift: {anchor_role}")
        if hashlib.sha256(item.canonical.encode("utf-8")).hexdigest() != row["sha256"]:
            raise AuditError(f"{role} machine anchor hash drift: {anchor_role}")
    if expected["selected_fde"] not in fdes:
        raise AuditError(f"{role} selected FDE range drift")

    if role == "subparse":
        ordered = (0xB86B, 0xB870, 0xB873, 0xB875, 0xB87A, 0xB87D, 0xB87F,
                   0xB885, 0xB887, 0xB88D, 0xB928)
        if tuple(sorted(ordered)) != ordered:
            raise AuditError("internal subparse ordering assertion is malformed")
        if not (by_address[0xB873].operands.startswith("0xb88d ")
                and by_address[0xB87F].operands.startswith("0xb928 ")
                and by_address[0xB887].operands.startswith("0xb928 ")):
            raise AuditError("subparse branch target drift")
        if not (0xB873 < 0xB875 < 0xB88D < 0xB928):
            raise AuditError("subparse guard/read/write ordering drift")
    elif role == "typefind":
        if not (by_address[0x2CC2].operands.startswith("0x2ce0 ")
                and by_address[0x2CF5].operands.startswith("0x2cc4 ")):
            raise AuditError("typefind branch target drift")
        if not (0x2CB9 < 0x2CBE < 0x2CC2 < 0x2CC4 < 0x2CDE < 0x2CE0
                < 0x2CE2 < 0x2CEA < 0x2CED < 0x2CF2 < 0x2CF5 < 0x2D1D < 0x2D20):
            raise AuditError("typefind guard/peek/read ordering drift")
        start, end = expected["selected_fde"]
        length_compares = [item for item in instructions
                           if start <= item.address < 0x2D20
                           and item.mnemonic.startswith("cmp")
                           and "%rbp" in item.operands]
        if length_compares:
            raise AuditError("typefind gained an unsupported pre-read total-length comparison")
    else:
        raise AuditError("unsupported machine role")


def _validate_complete_identity(role: str, instructions: list[Instruction],
                                fdes: list[tuple[int, int]], expected: dict[str, Any]) -> tuple[str, str]:
    instruction_hash = _canonical_hash(item.canonical for item in instructions)
    if (len(instructions) != expected["instruction_count"]
            or instruction_hash != expected["instruction_sha256"]):
        raise AuditError(f"{role} complete instruction identity/count drift")
    fde_hash = _canonical_hash(f"{start:x}-{end:x}" for start, end in fdes)
    if len(fdes) != expected["fde_count"] or fde_hash != expected["fde_sha256"]:
        raise AuditError(f"{role} complete FDE identity/count drift")
    return instruction_hash, fde_hash


def _analyze_member(role: str, data: bytes, expected: dict[str, Any],
                    objdump: Path, readelf: Path, directory: Path) -> dict[str, Any]:
    path = directory / f"{role}.elf"
    try:
        with path.open("xb") as handle:
            os.chmod(path, 0o600)
            handle.write(data)
    except OSError as exc:
        raise AuditError(f"cannot create bounded temporary {role} copy: {exc.strerror}") from exc
    disassembly = parse_disassembly(_run_tool(
        [str(objdump), "-d", "--no-show-raw-insn", str(path)], f"{role} disassembly"))
    fdes = parse_fdes(_run_tool([str(readelf), "--unwind", str(path)], f"{role} unwind"))
    instruction_hash, fde_hash = _validate_complete_identity(
        role, disassembly, fdes, expected
    )
    build_id = parse_build_id(_run_tool([str(readelf), "--notes", str(path)], f"{role} notes", 8 << 20))
    if build_id != expected["build_id"]:
        raise AuditError(f"{role} Build ID drift")
    _validate_machine(role, disassembly, fdes, expected)
    return {
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


def analyze(rootfs_path: Path, objdump_path: Path, readelf_path: Path,
            manifest_path: Path) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    _validate_tool(objdump_path, manifest["llvm"]["version"], manifest["llvm"]["objdump"], "llvm-objdump")
    _validate_tool(readelf_path, manifest["llvm"]["version"], manifest["llvm"]["readelf"], "llvm-readelf")
    member_bytes, root = _audit_archive(rootfs_path, manifest["rootfs"], manifest["members"])
    with tempfile.TemporaryDirectory(prefix="gst-static-audit-") as temporary:
        directory = Path(temporary)
        analyzed = {
            role: _analyze_member(role, member_bytes[role], manifest["members"][role],
                                  objdump_path, readelf_path, directory)
            for role in ("subparse", "typefind")
        }

    if hashlib.sha256(_read_regular(manifest_path, MAX_MANIFEST_SIZE, "manifest")).hexdigest() != manifest["manifest_sha256"]:
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
        "subparse_assessment": {
            "associated_issue": "CVE-2017-5842",
            "upstream_fix_commit": COMMITS["subparse_nonzero_length_fix"],
            "nonzero_length_test_precedes_last_byte_address": True,
            "zero_length_branch_skips_last_byte_address_and_write": True,
            "terminal_quote_checks_precede_write": True,
            "named_zero_length_underwrite_mechanism": "rejected-for-exact-binary",
            "unrelated_subtitle_defects_rejected": False,
        },
        "typefind_assessment": {
            "associated_issue": "CVE-2016-9811",
            "initial_fix_commit": COMMITS["typefind_initial_length_fix"],
            "later_correction_commit": COMMITS["typefind_complete_length_correction"],
            "initial_less_than_18_guard_present": True,
            "complete_less_than_22_guard_present": False,
            "six_byte_peek_precedes_offset_field_read": True,
            "offset_field_source_offset": 18,
            "offset_field_read_width_bytes": 4,
            "residual_total_lengths": [18, 19, 20, 21],
            "residual_out_of_range_bytes_by_total_length": {
                "18": 4, "19": 3, "20": 2, "21": 1,
            },
            "bounded_residual_out_of_range_read_possible": True,
        },
        "outcomes": {
            "parser_execution": None,
            "production_delivery": None,
            "information_disclosure": None,
            "code_execution": None,
            "privilege_gain_or_root": None,
            "persistence": None,
        },
        "scope": {
            "offline_exact_static_analysis": True,
            "canonical_tar_members_streamed_directly": True,
            "recovered_targets_executed": False,
            "parser_inputs_created": False,
            "malformed_media_bytes_emitted": False,
            "trigger_recipe_emitted": False,
            "full_binary_retained": False,
            "full_disassembly_retained": False,
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
