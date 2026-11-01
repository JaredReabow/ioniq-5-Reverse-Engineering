#!/usr/bin/env python3
"""Audit the exact-static AppFUMO boot-activation boundary.

This execution-free analyzer binds one exact ELF, one canonical rootfs archive,
and explicit LLVM tools to a strict manifest.  It emits normalized role labels,
hashes, ranges, and Boolean/null findings only: never target instructions,
callable D-Bus coordinates, serial bytes, fallback command text, or supplied
operator paths.
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
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
TOOL_NAME = "appfumo-boot-activation-boundary"
TOOL_VERSION = "1.0.0"
MAX_ELF_SIZE = 64 << 20
MAX_ROOTFS_SIZE = 1 << 30
MAX_MANIFEST_SIZE = 1 << 20
MAX_TOOL_SIZE = 16 << 20
MAX_TOOL_OUTPUT = 192 << 20
MAX_SELECTED_MEMBER = 2 << 20
ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PROGRAM_HEADER = struct.Struct("<IIQQQQQQ")
PT_LOAD = 1

REQUIRED_FDE_ROLES = {
    "update-view-constructor": (0xDEA90, 0xDF6AC),
    "update-view-meta-dispatch": (0x16D430, 0x16DAAD),
    "controller-constructor": (0x135A80, 0x135FA6),
    "controller-meta-dispatch": (0x16F520, 0x16FAB3),
    "controller-reboot": (0x134CE0, 0x134D79),
    "reset-wrapper": (0x146680, 0x146711),
    "reset-core": (0x145CA0, 0x14667E),
    "engine-dbus-subscriptions": (0xE2790, 0xE2C2B),
    "reboot-system": (0xE8C20, 0xE8D06),
    "reboot-system-core": (0xE7810, 0xE7FE1),
    "recovery-mode-slot": (0x11F060, 0x11F1A9),
    "set-recovery-mode": (0xE8D10, 0xE907C),
    "ask-system-boot-info": (0xEEB00, 0xEEF10),
    "get-booting-type": (0x1122D0, 0x112A58),
}
REQUIRED_DIRECT_TRANSFERS = {
    0x134CE0: ((0x16F930,), ()),
    0x146680: ((0x134D18,), ()),
    0x145CA0: ((), (0x1466CC,)),
    0xE2790: ((0x126830,), ()),
    0xE7810: ((0x121066,), (0xE8C92,)),
    0xE8C20: ((0x16E801,), ()),
    0xE8D10: ((), (0x11F11C,)),
    0xEEB00: ((), ()),
    0x1122D0: ((0x12598A,), ()),
    0x11F060: ((0x16E8F6,), ()),
}
REQUIRED_ANCHOR_VAS = {
    0xDF157, 0xDF163, 0xDF185,
    0x16D45E, 0x16D618, 0x16D623,
    0x135DF3, 0x135DFF, 0x135E2D, 0x16F930,
    0x134D18, 0x134D20, 0x1466CC,
    0x145D9D, 0x145E31, 0x145EEF, 0x145F18, 0x145F1D,
    0x14603C, 0x146369,
    0xE8C92, 0xE78CB, 0xE795F, 0xE7A11, 0xE7A3A, 0xE7A3F,
    0xE7B42, 0xE7DCA,
    0xE2973, 0xE298B, 0xE29DF,
    0x11F092, 0x11F11C,
    0xE8D57, 0xE8DD7, 0xE8E68, 0xE8E99,
    0xEEB29, 0xEEBA9, 0xEEC3A, 0xEEC62, 0xEEC91, 0xEECA3, 0xEEDC3,
    0x112326, 0x112357, 0x11247D, 0x11248D, 0x1125F3, 0x112601,
    0x11262D, 0x112644, 0x112649, 0x112651, 0x112656, 0x11283E,
}
REQUIRED_LITERAL_VAS = {
    "update-view-start-signal-primary": 0x21E160,
    "qml-reboot-signal": 0x21E190,
    "controller-reboot-slot": 0x22B620,
    "update-view-start-signal-secondary": 0x22B650,
    "recovery-notification": 0x21E610,
    "recovery-slot": 0x227358,
    "reset-request-method": 0x21EB3B,
    "recovery-request-method": 0x21EC50,
    "boot-info-request-method": 0x21EE7C,
    "micom-status-shared-memory-key": 0x21FE22,
    "reset-operational-fallback-redacted": 0x2214C8,
    "normalized-endpoint-service": 0x215273,
    "normalized-endpoint-path": 0x215289,
    "normalized-endpoint-interface": 0x21528E,
}
REQUIRED_BLOB_RANGES = {
    "completion-qml-resource": (0x3FC386, 1788),
    "completion-qml-active-timer": (0x3FC811, 13),
    "completion-qml-zero-count-gate": (0x3FC8B6, 21),
    "completion-qml-active-reboot-expression": (0x3FC8FE, 24),
}
REQUIRED_ROOTFS_ROLES = {
    "update-start-dispatch": "./etc/update_start_5w.sh",
    "update-start-labeler": "./etc/update_start_5w.sh.ori",
    "root-fsck-service": "./lib/systemd/system/systemd-fsck-root.service",
    "root-fsck-helper": "./lib/systemd/systemd-fsck",
    "generic-system-update-generator": "./lib/systemd/system-generators/systemd-system-update-generator",
    "generic-system-update-done": "./lib/systemd/systemd-update-done",
    "generic-system-update-target": "./lib/systemd/system/system-update.target",
    "generic-system-update-done-service": "./lib/systemd/system/systemd-update-done.service",
    "generic-boot-control-tool": "./usr/bin/bootctl",
    "generic-flashing-tool": "./usr/bin/fastboot",
}
REQUIRED_ABSENT_BASENAMES = (
    "fw_setenv", "abctl", "grub", "systemd-bless-boot", "mark-good", "bootcount",
)


class BoundaryError(ValueError):
    """Input or evidence falls outside the exact bounded contract."""


@dataclass(frozen=True)
class Segment:
    offset: int
    vaddr: int
    filesz: int


@dataclass(frozen=True)
class Instruction:
    address: int
    mnemonic: str
    operands: str

    @property
    def canonical(self) -> str:
        return f"{self.address:x}\t{self.mnemonic}\t{self.operands}"


class ElfView:
    def __init__(self, data: bytes):
        self.data = data
        if len(data) < ELF_HEADER.size:
            raise BoundaryError("ELF header is truncated")
        fields = ELF_HEADER.unpack_from(data)
        ident = fields[0]
        if ident[:4] != b"\x7fELF" or ident[4:7] != bytes((2, 1, 1)):
            raise BoundaryError("unsupported ELF identity")
        if fields[1] not in (2, 3) or fields[2] != 62 or fields[3] != 1:
            raise BoundaryError("unsupported ELF ABI")
        phoff, ehsize, phentsize, phnum = fields[5], fields[8], fields[9], fields[10]
        if ehsize != ELF_HEADER.size or phentsize != PROGRAM_HEADER.size:
            raise BoundaryError("unsupported ELF header layout")
        if not 0 < phnum <= 256 or phoff + phnum * phentsize > len(data):
            raise BoundaryError("ELF program-header table is malformed or truncated")
        segments: list[Segment] = []
        for index in range(phnum):
            row = PROGRAM_HEADER.unpack_from(data, phoff + index * phentsize)
            if row[0] != PT_LOAD:
                continue
            offset, vaddr, filesz, memsz = row[2], row[3], row[5], row[6]
            if filesz > memsz or offset + filesz > len(data):
                raise BoundaryError("ELF PT_LOAD range is malformed")
            segments.append(Segment(offset, vaddr, filesz))
        if not segments:
            raise BoundaryError("ELF has no file-backed PT_LOAD segment")
        self.segments = segments

    def map(self, va: int, size: int, what: str) -> int:
        if type(va) is not int or type(size) is not int or va < 0 or size < 0:
            raise BoundaryError(f"{what} range is invalid")
        end = va + size
        if end > 1 << 64:
            raise BoundaryError(f"{what} range overflows")
        candidates = [
            item.offset + va - item.vaddr
            for item in self.segments
            if item.vaddr <= va and end <= item.vaddr + item.filesz
        ]
        if len(candidates) != 1:
            raise BoundaryError(f"{what} range is {'ambiguous' if candidates else 'unmapped'}")
        return candidates[0]

    def bytes_at(self, va: int, size: int, what: str) -> bytes:
        offset = self.map(va, size, what)
        return self.data[offset:offset + size]


def _stat_regular(path: Path, maximum: int, what: str) -> os.stat_result:
    try:
        result = path.stat()
    except OSError as exc:
        raise BoundaryError(f"cannot stat {what}: {exc.strerror}") from exc
    if not stat.S_ISREG(result.st_mode):
        raise BoundaryError(f"{what} is not a regular file")
    if result.st_size > maximum:
        raise BoundaryError(f"{what} exceeds the size limit")
    return result


def _same_stat(before: os.stat_result, after: os.stat_result) -> bool:
    return all(getattr(before, key) == getattr(after, key)
               for key in ("st_dev", "st_ino", "st_size", "st_mtime_ns"))


def _read_regular(path: Path, maximum: int, what: str) -> bytes:
    before = _stat_regular(path, maximum, what)
    try:
        with path.open("rb") as handle:
            raw = handle.read(before.st_size + 1)
    except OSError as exc:
        raise BoundaryError(f"cannot read {what}: {exc.strerror}") from exc
    after = _stat_regular(path, maximum, what)
    if len(raw) != before.st_size or not _same_stat(before, after):
        raise BoundaryError(f"{what} changed while being read")
    return raw


def _object(value: Any, keys: Iterable[str], what: str) -> dict[str, Any]:
    expected = set(keys)
    if type(value) is not dict:
        raise BoundaryError(f"{what} must be an object")
    actual = set(value)
    if actual != expected:
        raise BoundaryError(
            f"{what} keys mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
        )
    return value


def _array(value: Any, what: str, maximum: int = 4096) -> list[Any]:
    if type(value) is not list or len(value) > maximum:
        raise BoundaryError(f"{what} must be a bounded array")
    return value


def _integer(value: Any, what: str, maximum: int = (1 << 64) - 1) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise BoundaryError(f"{what} must be a bounded non-Boolean integer")
    return value


def _string(value: Any, what: str, maximum: int = 4096) -> str:
    if type(value) is not str or not value or len(value) > maximum:
        raise BoundaryError(f"{what} must be a bounded non-empty string")
    return value


def _digest(value: Any, what: str) -> str:
    text = _string(value, what, 64)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise BoundaryError(f"{what} must be lowercase SHA-256")
    return text


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BoundaryError(f"manifest contains duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_manifest(path: Path) -> dict[str, Any]:
    raw = _read_regular(path, MAX_MANIFEST_SIZE, "manifest")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BoundaryError("manifest is not valid UTF-8 JSON") from exc
    top = _object(value, {"schema_version", "artifacts", "llvm", "expected"}, "manifest")
    if _integer(top["schema_version"], "schema_version") != SCHEMA_VERSION:
        raise BoundaryError("unsupported manifest schema version")
    artifacts = _object(top["artifacts"], {"elf", "rootfs"}, "artifacts")
    elf = _object(artifacts["elf"], {"sha256", "size", "build_id"}, "artifacts.elf")
    elf_out = {
        "sha256": _digest(elf["sha256"], "elf.sha256"),
        "size": _integer(elf["size"], "elf.size", MAX_ELF_SIZE),
        "build_id": _string(elf["build_id"], "elf.build_id", 128),
    }
    if not re.fullmatch(r"[0-9a-f]+", elf_out["build_id"]):
        raise BoundaryError("elf.build_id must be lowercase hexadecimal")
    rootfs = _object(artifacts["rootfs"], {"sha256", "size"}, "artifacts.rootfs")
    rootfs_out = {
        "sha256": _digest(rootfs["sha256"], "rootfs.sha256"),
        "size": _integer(rootfs["size"], "rootfs.size", MAX_ROOTFS_SIZE),
    }
    llvm_obj = _object(top["llvm"], {
        "version", "objdump_size", "objdump_sha256", "readelf_size", "readelf_sha256",
        "instruction_count", "instruction_sha256", "fde_count", "fde_sha256",
    }, "llvm")
    llvm = {
        "version": _string(llvm_obj["version"], "llvm.version", 128),
        "objdump_size": _integer(llvm_obj["objdump_size"], "llvm.objdump_size", MAX_TOOL_SIZE),
        "objdump_sha256": _digest(llvm_obj["objdump_sha256"], "llvm.objdump_sha256"),
        "readelf_size": _integer(llvm_obj["readelf_size"], "llvm.readelf_size", MAX_TOOL_SIZE),
        "readelf_sha256": _digest(llvm_obj["readelf_sha256"], "llvm.readelf_sha256"),
        "instruction_count": _integer(llvm_obj["instruction_count"], "llvm.instruction_count", 2_000_000),
        "instruction_sha256": _digest(llvm_obj["instruction_sha256"], "llvm.instruction_sha256"),
        "fde_count": _integer(llvm_obj["fde_count"], "llvm.fde_count", 100_000),
        "fde_sha256": _digest(llvm_obj["fde_sha256"], "llvm.fde_sha256"),
    }
    expected = _load_expected(top["expected"])
    return {"elf": elf_out, "rootfs": rootfs_out, "llvm": llvm, "expected": expected,
            "manifest_sha256": hashlib.sha256(raw).hexdigest()}


def _load_expected(value: Any) -> dict[str, Any]:
    obj = _object(value, {"fdes", "direct_transfers", "anchors", "literals", "blobs", "rootfs"}, "expected")
    fdes = []
    for index, item in enumerate(_array(obj["fdes"], "fdes", 64)):
        row = _object(item, {"role", "start", "end_exclusive"}, f"fde {index}")
        fdes.append({"role": _string(row["role"], "fde.role", 80),
                     "start": _integer(row["start"], "fde.start"),
                     "end_exclusive": _integer(row["end_exclusive"], "fde.end_exclusive")})
    if len(fdes) != len(REQUIRED_FDE_ROLES) or {
        row["role"]: (row["start"], row["end_exclusive"]) for row in fdes
    } != REQUIRED_FDE_ROLES:
        raise BoundaryError("selected FDE role/range set does not match the supported audit")
    transfers = []
    for index, item in enumerate(_array(obj["direct_transfers"], "direct_transfers", 64)):
        row = _object(item, {"target", "call_vas", "jump_vas"}, f"direct transfer {index}")
        transfers.append({
            "target": _integer(row["target"], "direct target"),
            "call_vas": tuple(_integer(v, "call VA") for v in _array(row["call_vas"], "call_vas", 128)),
            "jump_vas": tuple(_integer(v, "jump VA") for v in _array(row["jump_vas"], "jump_vas", 128)),
        })
    if len(transfers) != len(REQUIRED_DIRECT_TRANSFERS) or {
        row["target"]: (row["call_vas"], row["jump_vas"]) for row in transfers
    } != REQUIRED_DIRECT_TRANSFERS:
        raise BoundaryError("direct-transfer expectation set does not match the supported audit")
    anchors = []
    for index, item in enumerate(_array(obj["anchors"], "anchors", 256)):
        row = _object(item, {"va", "sha256"}, f"anchor {index}")
        anchors.append({"va": _integer(row["va"], "anchor.va"),
                        "sha256": _digest(row["sha256"], "anchor.sha256")})
    if len(anchors) != len(REQUIRED_ANCHOR_VAS) or {row["va"] for row in anchors} != REQUIRED_ANCHOR_VAS:
        raise BoundaryError("machine-anchor address set does not match the supported audit")
    literals = _load_ranges(obj["literals"], "literal", REQUIRED_LITERAL_VAS, cstrings=True)
    blobs = _load_ranges(obj["blobs"], "blob", REQUIRED_BLOB_RANGES, cstrings=False)
    rootfs = _load_rootfs_expected(obj["rootfs"])
    return {"fdes": fdes, "direct_transfers": transfers, "anchors": anchors,
            "literals": literals, "blobs": blobs, "rootfs": rootfs}


def _load_ranges(value: Any, label: str, required: dict[str, Any], *, cstrings: bool) -> list[dict[str, Any]]:
    rows = []
    for index, item in enumerate(_array(value, label + "s", 64)):
        row = _object(item, {"role", "va", "length", "sha256"}, f"{label} {index}")
        rows.append({"role": _string(row["role"], f"{label}.role", 96),
                     "va": _integer(row["va"], f"{label}.va"),
                     "length": _integer(row["length"], f"{label}.length", 4096),
                     "sha256": _digest(row["sha256"], f"{label}.sha256")})
    actual = ({row["role"]: row["va"] for row in rows} if cstrings else
              {row["role"]: (row["va"], row["length"]) for row in rows})
    if len(rows) != len(required) or actual != required:
        raise BoundaryError(f"{label} role/range set does not match the supported audit")
    return rows


def _load_rootfs_expected(value: Any) -> dict[str, Any]:
    obj = _object(value, {"member_count", "inventory_sha256", "selected_members", "absent_basenames"}, "expected.rootfs")
    selected = []
    for index, item in enumerate(_array(obj["selected_members"], "selected_members", 32)):
        row = _object(item, {"role", "name", "type", "mode", "size", "sha256"}, f"selected member {index}")
        selected.append({
            "role": _string(row["role"], "member.role", 96),
            "name": _string(row["name"], "member.name", 512),
            "type": _string(row["type"], "member.type", 32),
            "mode": _integer(row["mode"], "member.mode", 0o7777),
            "size": _integer(row["size"], "member.size", MAX_SELECTED_MEMBER),
            "sha256": _digest(row["sha256"], "member.sha256"),
        })
    if len(selected) != len(REQUIRED_ROOTFS_ROLES) or {
        row["role"]: row["name"] for row in selected
    } != REQUIRED_ROOTFS_ROLES:
        raise BoundaryError("selected rootfs role/name set does not match the supported audit")
    if any(row["type"] != "regular" for row in selected):
        raise BoundaryError("selected rootfs members must require regular files")
    absent = tuple(_string(item, "absent basename", 128)
                   for item in _array(obj["absent_basenames"], "absent_basenames", 32))
    if absent != REQUIRED_ABSENT_BASENAMES:
        raise BoundaryError("rootfs exact-name absence set does not match the supported audit")
    return {
        "member_count": _integer(obj["member_count"], "rootfs.member_count", 1_000_000),
        "inventory_sha256": _digest(obj["inventory_sha256"], "rootfs.inventory_sha256"),
        "selected_members": selected,
        "absent_basenames": absent,
    }


def _run_tool(command: list[str], what: str, maximum: int = MAX_TOOL_OUTPUT) -> bytes:
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except OSError as exc:
        raise BoundaryError(f"cannot run {what}: {exc.strerror}") from exc
    if completed.returncode != 0:
        raise BoundaryError(f"{what} failed with status {completed.returncode}")
    if len(completed.stdout) > maximum or len(completed.stderr) > 1 << 20:
        raise BoundaryError(f"{what} output exceeds bound")
    if completed.stderr:
        raise BoundaryError(f"{what} produced unexpected stderr")
    return completed.stdout


def _validate_tool(path: Path, version: str, size: int, digest: str, what: str) -> None:
    st = _stat_regular(path, MAX_TOOL_SIZE, what)
    if not os.access(path, os.X_OK):
        raise BoundaryError(f"{what} is not executable")
    raw = _read_regular(path, MAX_TOOL_SIZE, what)
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
        raise BoundaryError(f"{what} file identity does not match manifest")
    lines = _run_tool([str(path), "--version"], f"{what} version", 1 << 20).decode("utf-8", "strict").splitlines()
    if not lines or lines[0] != version or st.st_size != size:
        raise BoundaryError(f"{what} version identity does not match manifest")


def parse_disassembly(raw: bytes) -> list[Instruction]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BoundaryError("objdump output is not UTF-8") from exc
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
                raise BoundaryError("objdump instruction mnemonic is malformed")
            if address in seen:
                raise BoundaryError("objdump contains a duplicate instruction address")
            seen.add(address)
            result.append(Instruction(address, mnemonic, operands))
        elif active and malformed_re.match(line):
            raise BoundaryError("objdump contains a malformed or truncated instruction line")
    if not result:
        raise BoundaryError("objdump contains no decoded instructions")
    if any(left.address >= right.address for left, right in zip(result, result[1:])):
        raise BoundaryError("objdump instruction addresses are not strictly increasing")
    return result


def parse_fdes(raw: bytes) -> list[tuple[int, int]]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BoundaryError("readelf unwind output is not UTF-8") from exc
    pattern = re.compile(
        r"^\s*\[0x[0-9a-f]+\] FDE length=[0-9]+ cie=\[0x[0-9a-f]+\]\n"
        r"\s+initial_location: 0x([0-9a-f]+)\n"
        r"\s+address_range: 0x([0-9a-f]+) \(end : 0x([0-9a-f]+)\)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    headers = re.findall(r"^\s*\[0x[0-9a-f]+\] FDE length=", text, re.MULTILINE)
    if len(matches) != len(headers):
        raise BoundaryError("readelf contains a malformed or truncated FDE record")
    rows = []
    for match in matches:
        start, size, end = (int(match.group(i), 16) for i in (1, 2, 3))
        if size == 0 or start + size != end:
            raise BoundaryError("readelf contains a malformed FDE range")
        rows.append((start, end))
    if not rows:
        raise BoundaryError("readelf contains no FDE ranges")
    if len({start for start, _ in rows}) != len(rows):
        raise BoundaryError("readelf contains duplicate FDE starts")
    rows.sort()
    return rows


def parse_build_id(raw: bytes) -> str:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BoundaryError("readelf note output is not UTF-8") from exc
    values = re.findall(r"Build ID: ([0-9a-f]+)", text)
    if len(values) != 1:
        raise BoundaryError("readelf Build ID is absent or ambiguous")
    return values[0]


def _canonical_hash(lines: Iterable[str]) -> str:
    return hashlib.sha256("".join(line + "\n" for line in lines).encode("utf-8")).hexdigest()


def _branch_target(item: Instruction) -> int | None:
    if not item.mnemonic.startswith(("call", "j")):
        return None
    match = re.match(r"0x([0-9a-f]+)(?:\s|$)", item.operands)
    return int(match.group(1), 16) if match else None


def _transfers(instructions: list[Instruction], target: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    calls = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("call") and _branch_target(item) == target)
    jumps = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("j") and _branch_target(item) == target)
    return calls, jumps


def _validate_machine(instructions: list[Instruction], expected: dict[str, Any]) -> None:
    by_va = {item.address: item for item in instructions}
    for row in expected["anchors"]:
        item = by_va.get(row["va"])
        if item is None or hashlib.sha256(item.canonical.encode("utf-8")).hexdigest() != row["sha256"]:
            raise BoundaryError(f"machine-anchor identity drift at 0x{row['va']:x}")
    for target, transfers in REQUIRED_DIRECT_TRANSFERS.items():
        if _transfers(instructions, target) != transfers:
            raise BoundaryError(f"direct-transfer inventory drift for target 0x{target:x}")


def _canonical_member_name(name: str) -> str:
    if (type(name) is not str or not name or name.startswith("/")
            or any(ord(char) < 0x20 or ord(char) == 0x7f for char in name)):
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
        line = (f"{index}\t{member.name}\t{member.type.hex()}\t{member.mode:o}\t"
                f"{member.size}\t{member.linkname}\n")
        return line.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise BoundaryError("archive inventory is not UTF-8") from exc


def _audit_rootfs(path: Path, artifact: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    before = _stat_regular(path, MAX_ROOTFS_SIZE, "rootfs archive")
    selected_by_name = {row["name"]: row for row in expected["selected_members"]}
    selected_by_canonical = {_canonical_member_name(name): name for name in selected_by_name}
    found: dict[str, dict[str, Any]] = {}
    basenames: set[str] = set()
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
                    basenames.add(canonical.rsplit("/", 1)[-1])
                    expected_name = selected_by_canonical.get(canonical)
                    if expected_name is None:
                        continue
                    if member.name != expected_name:
                        raise BoundaryError("selected rootfs member is present through an archive alias")
                    if expected_name in found:
                        raise BoundaryError("selected rootfs member is duplicated")
                    row = selected_by_name[expected_name]
                    if (not member.isreg() or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                            or member.linkname or member.mode != row["mode"] or member.size != row["size"]
                            or member.size > MAX_SELECTED_MEMBER):
                        raise BoundaryError(f"selected rootfs member type/mode/size drift: {row['role']}")
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        raise BoundaryError(f"selected rootfs member cannot be streamed: {row['role']}")
                    digest = hashlib.sha256()
                    total = 0
                    while True:
                        chunk = extracted.read(1 << 16)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > member.size:
                            raise BoundaryError("selected rootfs member exceeds declared size")
                        digest.update(chunk)
                    if total != member.size or digest.hexdigest() != row["sha256"]:
                        raise BoundaryError(f"selected rootfs member content drift: {row['role']}")
                    found[expected_name] = row
            while True:
                chunk = reader.read(1 << 20)
                if not chunk:
                    break
            archive_digest = reader.digest.hexdigest()
            descriptor_after = os.fstat(raw_handle.fileno())
    except (tarfile.TarError, OSError) as exc:
        raise BoundaryError(f"cannot stream rootfs archive: {type(exc).__name__}") from exc
    after = _stat_regular(path, MAX_ROOTFS_SIZE, "rootfs archive")
    if not _same_stat(before, after) or not _same_stat(before, descriptor_after):
        raise BoundaryError("rootfs archive changed during analysis")
    if before.st_size != artifact["size"] or archive_digest != artifact["sha256"]:
        raise BoundaryError("rootfs archive identity does not match manifest")
    if count != expected["member_count"] or inventory.hexdigest() != expected["inventory_sha256"]:
        raise BoundaryError("complete rootfs inventory identity/count does not match manifest")
    missing = set(selected_by_name) - set(found)
    if missing:
        raise BoundaryError("selected rootfs members are missing")
    present_absent = set(expected["absent_basenames"]) & basenames
    if present_absent:
        raise BoundaryError("an exact-name negative is no longer absent")
    return {
        "sha256": archive_digest,
        "size": before.st_size,
        "member_count": count,
        "inventory_sha256": inventory.hexdigest(),
        "selected_members": {
            row["role"]: {"type": row["type"], "mode": f"0{row['mode']:o}",
                          "size": row["size"], "sha256": row["sha256"]}
            for row in expected["selected_members"]
        },
        "exact_name_absence": list(expected["absent_basenames"]),
    }


def analyze(elf_path: Path, rootfs_path: Path, objdump_path: Path,
            readelf_path: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    artifact, root_artifact = manifest["elf"], manifest["rootfs"]
    llvm, expected = manifest["llvm"], manifest["expected"]
    _validate_tool(objdump_path, llvm["version"], llvm["objdump_size"], llvm["objdump_sha256"], "llvm-objdump")
    _validate_tool(readelf_path, llvm["version"], llvm["readelf_size"], llvm["readelf_sha256"], "llvm-readelf")
    elf_data = _read_regular(elf_path, MAX_ELF_SIZE, "ELF")
    elf_sha = hashlib.sha256(elf_data).hexdigest()
    if len(elf_data) != artifact["size"] or elf_sha != artifact["sha256"]:
        raise BoundaryError("ELF identity does not match manifest")
    elf = ElfView(elf_data)
    dis_raw = _run_tool([str(objdump_path), "-d", "--no-show-raw-insn", str(elf_path)], "llvm-objdump disassembly")
    instructions = parse_disassembly(dis_raw)
    if (len(instructions) != llvm["instruction_count"]
            or _canonical_hash(item.canonical for item in instructions) != llvm["instruction_sha256"]):
        raise BoundaryError("complete instruction identity/count does not match manifest")
    unwind_raw = _run_tool([str(readelf_path), "--unwind", str(elf_path)], "llvm-readelf unwind")
    fdes = parse_fdes(unwind_raw)
    if (len(fdes) != llvm["fde_count"]
            or _canonical_hash(f"{start:x}-{end:x}" for start, end in fdes) != llvm["fde_sha256"]):
        raise BoundaryError("complete FDE identity/count does not match manifest")
    fde_map = dict(fdes)
    for role, (start, end) in REQUIRED_FDE_ROLES.items():
        if fde_map.get(start) != end:
            raise BoundaryError(f"selected {role} FDE range drift")
    notes = _run_tool([str(readelf_path), "--notes", str(elf_path)], "llvm-readelf notes", 8 << 20)
    if parse_build_id(notes) != artifact["build_id"]:
        raise BoundaryError("ELF Build ID does not match manifest")
    for row in expected["literals"]:
        raw = elf.bytes_at(row["va"], row["length"] + 1, f"{row['role']} literal")
        if raw[-1:] != b"\0" or b"\0" in raw[:-1] or hashlib.sha256(raw[:-1]).hexdigest() != row["sha256"]:
            raise BoundaryError(f"{row['role']} literal identity does not match")
    for row in expected["blobs"]:
        raw = elf.bytes_at(row["va"], row["length"], f"{row['role']} blob")
        if hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise BoundaryError(f"{row['role']} blob identity does not match")
    _validate_machine(instructions, expected)
    rootfs = _audit_rootfs(rootfs_path, root_artifact, expected["rootfs"])
    if _read_regular(elf_path, MAX_ELF_SIZE, "ELF") != elf_data:
        raise BoundaryError("ELF changed during analysis")
    if hashlib.sha256(_read_regular(manifest_path, MAX_MANIFEST_SIZE, "manifest")).hexdigest() != manifest["manifest_sha256"]:
        raise BoundaryError("manifest changed during analysis")
    for path, size, digest, what in (
        (objdump_path, llvm["objdump_size"], llvm["objdump_sha256"], "llvm-objdump"),
        (readelf_path, llvm["readelf_size"], llvm["readelf_sha256"], "llvm-readelf"),
    ):
        raw = _read_regular(path, MAX_TOOL_SIZE, what)
        if len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
            raise BoundaryError(f"{what} changed during analysis")
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "artifacts": {
            "elf": {"sha256": elf_sha, "size": len(elf_data), "build_id": artifact["build_id"]},
            "rootfs": {"sha256": rootfs["sha256"], "size": rootfs["size"]},
        },
        "evidence": {
            "llvm_version": llvm["version"],
            "instruction_count": len(instructions),
            "instruction_sha256": llvm["instruction_sha256"],
            "fde_count": len(fdes),
            "fde_sha256": llvm["fde_sha256"],
            "manifest_sha256": manifest["manifest_sha256"],
            "selected_fdes": {role: {"start": f"0x{start:x}", "end_exclusive": f"0x{end:x}"}
                               for role, (start, end) in REQUIRED_FDE_ROLES.items()},
            "direct_transfers": {f"0x{target:x}": {
                "calls": [f"0x{va:x}" for va in calls],
                "jumps": [f"0x{va:x}" for va in jumps],
            } for target, (calls, jumps) in REQUIRED_DIRECT_TRANSFERS.items()},
            "literal_roles": [row["role"] for row in expected["literals"]],
        },
        "completion_to_reset": {
            "completion_qml_active_timer_emits_reboot_clicked": True,
            "qml_signal_to_update_view_signal_connected": True,
            "qml_to_update_view_connection_type": "auto",
            "update_view_start_signal_local_index": 0,
            "update_view_dispatch_action": "activate-signal",
            "update_view_start_signal_to_controller_reboot_slot_connected": True,
            "update_view_to_controller_connection_type": "auto",
            "controller_reboot_local_method_index": 12,
            "controller_meta_dispatch_reaches_reboot": True,
            "controller_reboot_reaches_reset_wrapper": True,
            "reset_wrapper_tail_reaches_reset_core": True,
            "reset_argument_type": "byte-array",
            "reset_argument_byte_count": 1,
            "reset_argument_normalized_role": "reset-request",
            "reset_send_is_asynchronous": True,
            "send_status_observed": True,
            "send_false_enters_bounded_retry_flow": True,
            "terminal_send_false_reaches_redacted_fallback": True,
            "send_acceptance_proves_remote_action": False,
            "slot_identifier_present": False,
            "operational_fallback_present_but_redacted": True,
        },
        "separate_reboot_system": {
            "meta_dispatch_reaches_reboot_system": True,
            "wrapper_tail_reaches_separate_reset_core": True,
            "argument_type": "byte-array",
            "argument_byte_count": 1,
            "argument_normalized_role": "reset-request",
            "send_is_asynchronous": True,
            "send_status_observed": True,
            "send_false_enters_bounded_retry_flow": True,
            "terminal_send_false_reaches_redacted_fallback": True,
            "slot_identifier_present": False,
            "remote_action_proved": False,
        },
        "recovery_mode": {
            "system_bus_notification_connection_bound": True,
            "sender_service_and_path_are_wildcards": True,
            "fixed_interface_and_member_values_redacted": True,
            "slot_signature": "normalized-byte-array-slot",
            "nonempty_payload_last_byte_gate": "normalized-recovery-request",
            "state_gates_precede_request": True,
            "slot_tail_reaches_set_recovery_mode": True,
            "request_argument_type": "byte-array",
            "request_argument_byte_count": 1,
            "request_argument_normalized_role": "recovery-request",
            "request_send_is_asynchronous": True,
            "send_status_controls_flow": False,
            "slot_identifier_present": False,
            "remote_action_proved": False,
        },
        "boot_information": {
            "ask_request_argument_count": 0,
            "ask_call_mode": "block-with-gui",
            "ask_timeout_milliseconds": 1000,
            "reply_first_argument_converted_to_byte_array": True,
            "reply_minimum_length_for_status": 27,
            "returned_status_offset": 26,
            "short_or_missing_reply_status": 0,
            "status_enum_meaning": None,
            "shared_memory_key_role": "micom-status-message",
            "shared_memory_requested_size": 35,
            "shared_memory_copy_size": 35,
            "shared_memory_lock_copy_unlock_detach_bound": True,
            "booting_type_direct_selector_offsets": [0, 2],
            "additional_shared_status_fields_parsed": True,
            "shared_memory_producer": None,
            "booting_type_enum_meaning": None,
            "shared_memory_freshness_or_atomicity": None,
        },
        "rootfs_audit": {
            "member_count": rootfs["member_count"],
            "inventory_sha256": rootfs["inventory_sha256"],
            "selected_members": rootfs["selected_members"],
            "update_start_scripts_classification": "label-management-only",
            "root_fsck_observation_scope": "current-root-device",
            "generic_system_update_components_installed": True,
            "generic_boot_control_tool_installed": True,
            "generic_flashing_tool_installed": True,
            "generic_components_bound_to_appfumo_flow": False,
            "exact_name_absence": rootfs["exact_name_absence"],
            "absence_scope": "exact-basename-only",
        },
        "boundary": {
            "inactive_slot_activation_visible": False,
            "mark_good_visible": False,
            "boot_counter_update_visible": False,
            "rollback_programming_visible": False,
            "persistent_slot_choice_visible": False,
            "external_micom_boundary_remains": True,
            "external_abl_or_bootloader_boundary_remains": True,
            "reset_or_recovery_request_proves_action": False,
            "installed_runtime_identity_or_reachability": None,
            "boot_slot_change": None,
            "boot_acceptance": None,
            "rollback_behavior": None,
        },
        "scope": {
            "exact_static_direct_coverage": True,
            "canonical_rootfs_streamed": True,
            "target_code_executed": False,
            "operator_paths_emitted": False,
            "callable_dbus_coordinates_emitted": False,
            "serial_bytes_emitted": False,
            "target_instructions_emitted": False,
            "operational_fallback_command_emitted": False,
            "proprietary_binary_bytes_emitted": False,
        },
    }


def _write_json(value: Any) -> None:
    sys.stdout.buffer.write((json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", required=True, type=Path)
    parser.add_argument("--rootfs", required=True, type=Path)
    parser.add_argument("--llvm-objdump", required=True, type=Path)
    parser.add_argument("--llvm-readelf", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = analyze(args.elf, args.rootfs, args.llvm_objdump, args.llvm_readelf, args.manifest)
    except BoundaryError as exc:
        sys.stderr.buffer.write((f"error: {exc}\n").encode("utf-8"))
        return 2
    _write_json(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
