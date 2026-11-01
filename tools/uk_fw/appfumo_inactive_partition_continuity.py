#!/usr/bin/env python3
"""Verify the exact AppFUMO inactive-partition selector continuity package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import sys
from pathlib import Path

TOOL = "appfumo-inactive-partition-continuity"
VERSION = "1.0.0"
SCHEMA = "appfumo-inactive-partition-continuity/v1"
MAX_SIZE = 16 * 1024 * 1024
EXPECTED_SIZE = 5_066_264
EXPECTED_SHA256 = "464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7"
EXPECTED_BUILD_ID = "863a8730e66a1c5245a1bf458fe2554adee0351a"
TABLE_VA = 0x6C51A0
EXPECTED_TABLE = [
    "/dev/mmcblk0p3", "/dev/mmcblk0p5", "/dev/mmcblk0p6", "/dev/mmcblk0p7", None,
    None, "/dev/mmcblk0p1", "/dev/mmcblk0p2", "/dev/mmcblk0p17", "/dev/mmcblk0p17",
    "/dev/mmcblk0p5", "/dev/mmcblk0p3", "/dev/mmcblk0p7", "/dev/mmcblk0p6", None,
    None, "/dev/mmcblk0p2", "/dev/mmcblk0p1", "/dev/mmcblk0p17", "/dev/mmcblk0p17",
]
# Raw VAs equal file offsets for these executable ranges in the exact ELF.
RANGES = {
    "inactive_name_lookup": (0xA14C0, 0xA1B70, "ad0654c7471238d57b3fc2dc6156b24bdc4680f219f7b133f009971c35ecbf77"),
    "selected_table_population": (0xA1B70, 0xA2480, "8624adf53ae9e2c22f300d35f9294ca70bbaba9d9149098f9bd0a6a2047cd08f"),
    "selected_record_copy": (0xA0D50, 0xA0DC3, "2d0d8c8e1c6e36890ada9d34ba5d759526b8520a271d898465b24f94faf6f6fe"),
    "selector_to_index": (0xBFB20, 0xC0130, "2e49a19b7df4868438cf722178bc8ce994db3c80c4edac66363d944a3239ea69"),
    "writer_selection_head": (0xC541A, 0xC556F, "fbb72522bdca54beec75b0f0a94eafe24b62fd2b9c51169a36c9d513f319c43f"),
    "writer_jump_dispatch": (0xC608D, 0xC60C4, "74dbec9794d4197ecdd6666adf7225b03faeaa38b1c8b49e9670bfabb7377256"),
    "root_target_construction": (0xC765B, 0xC792C, "5a3bb6ba1dd0c8e357d00d96f0649f4ea2c8d5b04531c4cea668c7f790b787b4"),
}

class Failure(Exception):
    pass

def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]

def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]

def u64(data: bytes, off: int) -> int:
    return struct.unpack_from("<Q", data, off)[0]

def stable_read(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise Failure(f"cannot open input safely: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise Failure("input is not a regular file")
        if before.st_size != EXPECTED_SIZE or before.st_size > MAX_SIZE:
            raise Failure(f"unexpected input size: {before.st_size}")
        chunks: list[bytes] = []
        left = before.st_size
        while left:
            chunk = os.read(fd, min(left, 1024 * 1024))
            if not chunk:
                raise Failure("short read")
            chunks.append(chunk)
            left -= len(chunk)
        after = os.fstat(fd)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after):
            raise Failure("input changed during read")
        return b"".join(chunks)
    finally:
        os.close(fd)

def parse(data: bytes) -> tuple[str, list[tuple[int, int, int]], dict[str, tuple[int, int, int]]]:
    if data[:16] != b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8:
        raise Failure("not the expected ELF64 little-endian identity")
    phoff, shoff = u64(data, 0x20), u64(data, 0x28)
    phents, phnum = u16(data, 0x36), u16(data, 0x38)
    shents, shnum, shstrndx = u16(data, 0x3A), u16(data, 0x3C), u16(data, 0x3E)
    if phents != 56 or shents != 64 or not phnum or not shnum or shstrndx >= shnum:
        raise Failure("unsupported ELF table geometry")
    if phoff + phents * phnum > len(data) or shoff + shents * shnum > len(data):
        raise Failure("ELF table exceeds file")
    loads: list[tuple[int, int, int]] = []
    build_id: str | None = None
    for i in range(phnum):
        off = phoff + i * phents
        p_type = u32(data, off)
        p_offset, p_vaddr, p_filesz = u64(data, off + 8), u64(data, off + 16), u64(data, off + 32)
        if p_offset + p_filesz > len(data):
            raise Failure("program segment exceeds file")
        if p_type == 1:
            loads.append((p_vaddr, p_vaddr + p_filesz, p_offset))
        elif p_type == 4:
            cur, end = p_offset, p_offset + p_filesz
            while cur + 12 <= end:
                namesz, descsz, ntype = struct.unpack_from("<III", data, cur)
                cur += 12
                name = data[cur:cur + namesz]
                cur += (namesz + 3) & ~3
                desc = data[cur:cur + descsz]
                cur += (descsz + 3) & ~3
                if cur > end:
                    raise Failure("malformed PT_NOTE")
                if name.rstrip(b"\0") == b"GNU" and ntype == 3:
                    if build_id is not None:
                        raise Failure("duplicate GNU Build ID")
                    build_id = desc.hex()
    loads.sort()
    for left, right in zip(loads, loads[1:]):
        if left[1] > right[0]:
            raise Failure("overlapping file-backed PT_LOAD ranges")
    sections_raw = []
    for i in range(shnum):
        sections_raw.append(struct.unpack_from("<IIQQQQIIQQ", data, shoff + i * shents))
    shstr = sections_raw[shstrndx]
    if shstr[4] + shstr[5] > len(data):
        raise Failure("section-name table exceeds file")
    names = data[shstr[4]:shstr[4] + shstr[5]]
    sections: dict[str, tuple[int, int, int]] = {}
    for item in sections_raw:
        noff = item[0]
        if noff >= len(names) or b"\0" not in names[noff:]:
            raise Failure("invalid section name")
        name = names[noff:names.index(b"\0", noff)].decode("ascii", "strict")
        if name in sections:
            raise Failure(f"duplicate section name: {name}")
        if item[4] + item[5] > len(data) and item[1] != 8:
            raise Failure(f"section exceeds file: {name}")
        sections[name] = (item[3], item[4], item[5])
    if build_id is None:
        raise Failure("GNU Build ID absent")
    return build_id, loads, sections

def va_to_offset(va: int, loads: list[tuple[int, int, int]]) -> int:
    hits = [(va - start) + off for start, end, off in loads if start <= va < end]
    if len(hits) != 1:
        raise Failure(f"VA does not map uniquely: 0x{va:x}")
    return hits[0]

def c_string(data: bytes, va: int, loads: list[tuple[int, int, int]]) -> str:
    off = va_to_offset(va, loads)
    end = data.find(b"\0", off, min(len(data), off + 4096))
    if end < 0:
        raise Failure(f"unterminated string at VA 0x{va:x}")
    return data[off:end].decode("utf-8", "strict")

def analyze(data: bytes) -> dict[str, object]:
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise Failure(f"ELF SHA-256 mismatch: {digest}")
    build_id, loads, sections = parse(data)
    if build_id != EXPECTED_BUILD_ID:
        raise Failure(f"Build ID mismatch: {build_id}")
    try:
        _, rela_off, rela_size = sections[".rela.dyn"]
    except KeyError as exc:
        raise Failure(".rela.dyn absent") from exc
    if rela_size % 24:
        raise Failure("malformed .rela.dyn size")
    relatives: dict[int, int] = {}
    for off in range(rela_off, rela_off + rela_size, 24):
        r_offset, r_info, addend = struct.unpack_from("<QQq", data, off)
        if (r_info & 0xFFFFFFFF) == 8:
            if r_offset in relatives:
                raise Failure(f"duplicate relative relocation: 0x{r_offset:x}")
            relatives[r_offset] = addend
    table: list[str | None] = []
    table_off = va_to_offset(TABLE_VA, loads)
    for i in range(20):
        slot_va = TABLE_VA + i * 8
        raw = u64(data, table_off + i * 8)
        value = relatives.get(slot_va, raw)
        table.append(None if value == 0 else c_string(data, value, loads))
    if table != EXPECTED_TABLE:
        raise Failure("inactive-partition table mismatch")
    range_report = []
    for name, (start, end, expected) in RANGES.items():
        if end > len(data) or start >= end:
            raise Failure(f"invalid frozen range: {name}")
        actual = hashlib.sha256(data[start:end]).hexdigest()
        if actual != expected:
            raise Failure(f"instruction-range mismatch for {name}: {actual}")
        range_report.append({"name": name, "raw_va_start": f"0x{start:x}", "raw_va_end": f"0x{end:x}", "sha256": actual})
    rows = []
    for i in range(2):
        row = table[i * 10:(i + 1) * 10]
        rows.append({
            "active_root": row[0], "inactive_root": row[1], "app": row[5],
            "inactive_vr": row[3], "inactive_boot": row[7], "vrfix": row[9],
            "uninterpreted_companion_fields": [row[2], row[4], row[6], row[8]],
        })
    return {
        "schema": SCHEMA,
        "tool": TOOL,
        "tool_version": VERSION,
        "input": {"size": len(data), "sha256": digest, "build_id": build_id},
        "instruction_ranges": range_report,
        "inactive_partition_rows": rows,
        "bounded_conclusion": {
            "status": "exact_static_selector_to_inactive_target_continuity",
            "established": [
                "The selected update record's +0x20 selector is mapped to an index before writer dispatch.",
                "The root writer branch reuses index 1 when copying the selected inactive-partition record.",
                "The same slot predicate selects the record table that population previously updated.",
                "Active root /dev/mmcblk0p3 maps to inactive root /dev/mmcblk0p5 and vice versa.",
            ],
            "not_established": [
                "same-object or same-byte continuity between authentication and writer pathname reopen",
                "successful partition write or final inactive-partition integrity",
                "persistent slot activation, boot acceptance, mark-good, rollback, root, or persistence",
            ],
        },
    }

def emit(obj: object, output: Path | None) -> None:
    text = json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=False) + "\n"
    payload = text.encode("utf-8")
    if output is None:
        sys.stdout.buffer.write(payload)
        return
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    fd = os.open(output, flags, 0o600)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("elf", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        emit(analyze(stable_read(args.elf)), args.output)
    except (Failure, OSError, UnicodeError, struct.error, ValueError) as exc:
        sys.stderr.write(f"{TOOL}: error: {exc}\n")
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
