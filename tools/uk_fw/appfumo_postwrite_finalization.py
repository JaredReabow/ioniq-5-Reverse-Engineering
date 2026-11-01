#!/usr/bin/env python3
"""Verify the exact AppFUMO post-write finalization and completion boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import sys
from pathlib import Path

TOOL = "appfumo-postwrite-finalization"
VERSION = "1.0.0"
SCHEMA = "appfumo-postwrite-finalization/v1"
MAX_SIZE = 16 * 1024 * 1024
EXPECTED_SIZE = 5_066_264
EXPECTED_SHA256 = "464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7"
EXPECTED_BUILD_ID = "863a8730e66a1c5245a1bf458fe2554adee0351a"

# Raw VAs equal file offsets for these executable ranges in the exact ELF.
RANGES = {
    "modify_fstab_full": (0xD0C80, 0xD1E6C, "5ce33f0f105ae05a4fb5233057de700e363c370c703a53d0e6d6f2e6e54117f3"),
    "finish_full": (0xD1E70, 0xD327F, "2150baafb8f774f82688f367176a9ee66519a0b0a8e34d53829b639dc22c5254"),
    "finish_mount_and_finalizer": (0xD1EB0, 0xD240D, "b1ad6dc19da279bfb680977f027d9212066440af06d8d1c225de83722cec083b"),
    "finish_progress_and_maintenance": (0xD240D, 0xD2C32, "f417ac7155200fff5d4b9a25724e57e8c9c42d4328ea58593c8f9f6cc0c4630b"),
    "finish_finalizer_failure_branch": (0xD2C08, 0xD2C32, "d1192dcd7d4d63e3a965c677167f9166268cb3bb403ebdbc8f53d750187e3acc"),
    "finish_progress_100": (0xD2A49, 0xD2B0A, "59a0821919eb2db05656120fe37ca7391354a6f58c1af9a3a7ea06e71c95678b"),
}

LITERALS = {
    "root_selector": (0x21FFA7, "root"),
    "vr_selector": (0x21648E, "vr"),
    "foldervr_selector": (0x2163A0, "foldervr"),
    "fstab": (0x21A92C, "/mnt/root/etc/fstab"),
    "fstab_emmc": (0x21A8F6, "/mnt/root/etc/fstab_emmc"),
    "fstab_emmc_fde": (0x21A90F, "/mnt/root/etc/fstab_emmc_fde"),
    "mount_probe": (0x21A140, "mount | grep /mnt/root | awk '{print $1}'"),
    "mount_program": (0x21E79E, "mount"),
    "mount_type": (0x211123, "ext4"),
    "mount_type_option": (0x21A96F, "-t"),
    "root_mountpoint": (0x216476, "/rw_data/mnt/root"),
    "app_mountpoint": (0x21A8B0, "/rw_data/mnt/app"),
    "vr_mountpoint": (0x21649E, "/rw_data/mnt/vr"),
    "fstrim_program": (0x210E66, "/sbin/fstrim"),
    "resume_marker": (0x21A361, "/update/resumeBlockNumber"),
    "temporary_resume_marker": (0x21A3AB, "/tmp/resume_mode_block_number"),
    "complete_message": (0x21A988, "System Update Complete!!"),
    "complete_domain": (0x21A9A1, "System"),
}

DIRECT_CALLS = {
    # modifyEtcFstabFile selector admission and active/inactive path derivation.
    "contains_root": (0xD0CC4, 0xBE1A0),
    "contains_vr": (0xD0CE8, 0xBE1A0),
    "contains_foldervr": (0xD0D0D, 0xBE1A0),
    "active_vr_path_foldervr_branch": (0xD0DBF, 0xA0E10),
    "inactive_vr_path_foldervr_branch": (0xD0DFB, 0xA14C0),
    "active_vr_path_vr_branch": (0xD0F0C, 0xA0E10),
    "inactive_vr_path_vr_branch": (0xD0F48, 0xA14C0),
    # One replace/write/flush/fsync/close sequence for each supported fstab path.
    "fstab_replace": (0xD1286, 0x231E0),
    "fstab_write": (0xD12FF, 0x231C0),
    "fstab_flush": (0xD1365, 0x246D0),
    "fstab_fsync": (0xD1374, 0x23840),
    "fstab_close": (0xD137C, 0x22020),
    "fstab_emmc_replace": (0xD15D9, 0x231E0),
    "fstab_emmc_write": (0xD165A, 0x231C0),
    "fstab_emmc_flush": (0xD16C8, 0x246D0),
    "fstab_emmc_fsync": (0xD16D7, 0x23840),
    "fstab_emmc_close": (0xD16DF, 0x22020),
    "fstab_emmc_fde_replace": (0xD19B4, 0x231E0),
    "fstab_emmc_fde_write": (0xD1A37, 0x231C0),
    "fstab_emmc_fde_flush": (0xD1A9D, 0x246D0),
    "fstab_emmc_fde_fsync": (0xD1AAC, 0x23840),
    "fstab_emmc_fde_close": (0xD1AB4, 0x22020),
    # finish(): mount-state handling, finalizer, progress, maintenance and cleanup.
    "sync": (0xD1EB0, 0x23420),
    "inactive_root_path": (0xD1F47, 0xA14C0),
    "compare_mounted_device": (0xD1FD0, 0x22090),
    "mount_process": (0xD22E4, 0x13BBA0),
    "modify_fstab": (0xD2400, 0xD0C80),
    "progress_99": (0xD246A, 0x168570),
    "fdisk_start": (0xD2514, 0x23670),
    "fdisk_wait": (0xD2541, 0x22E90),
    "root_fstrim_process": (0xD28EA, 0x13BFD0),
    "root_unmount": (0xD2920, 0x245E0),
    "app_fstrim_process": (0xD29CE, 0x13BFD0),
    "app_unmount": (0xD2A04, 0x245E0),
    "remove_resume_marker": (0xD2A6B, 0x13FEB0),
    "remove_temporary_resume_marker": (0xD2A9A, 0x13FEB0),
    "progress_100": (0xD2AEB, 0x168570),
    "vr_fstrim_process": (0xD2BB9, 0x13BFD0),
    "vr_unmount": (0xD2BEF, 0x245E0),
}

VTABLE_SLOT_VA = 0x6CE350
VTABLE_TARGET_VA = 0xD1E70


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


def parse_elf(data: bytes) -> tuple[str, list[tuple[int, int, int]], dict[str, tuple[int, int, int]]]:
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
    sections_raw = [struct.unpack_from("<IIQQQQIIQQ", data, shoff + i * shents) for i in range(shnum)]
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


def direct_call_target(data: bytes, va: int, loads: list[tuple[int, int, int]]) -> int:
    off = va_to_offset(va, loads)
    if off + 5 > len(data) or data[off] != 0xE8:
        raise Failure(f"expected direct call at 0x{va:x}")
    displacement = struct.unpack_from("<i", data, off + 1)[0]
    return va + 5 + displacement


def direct_jump_target(data: bytes, va: int, loads: list[tuple[int, int, int]]) -> int:
    off = va_to_offset(va, loads)
    if off + 5 > len(data) or data[off] != 0xE9:
        raise Failure(f"expected direct jump at 0x{va:x}")
    displacement = struct.unpack_from("<i", data, off + 1)[0]
    return va + 5 + displacement


def conditional_jump_target(data: bytes, va: int, loads: list[tuple[int, int, int]]) -> int:
    off = va_to_offset(va, loads)
    if off + 6 > len(data) or data[off] != 0x0F or not 0x80 <= data[off + 1] <= 0x8F:
        raise Failure(f"expected near conditional jump at 0x{va:x}")
    displacement = struct.unpack_from("<i", data, off + 2)[0]
    return va + 6 + displacement


def expect_bytes(data: bytes, va: int, expected: bytes, loads: list[tuple[int, int, int]]) -> None:
    off = va_to_offset(va, loads)
    if data[off:off + len(expected)] != expected:
        raise Failure(f"instruction anchor mismatch at 0x{va:x}")


def analyze(data: bytes) -> dict[str, object]:
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise Failure(f"ELF SHA-256 mismatch: {digest}")
    build_id, loads, sections = parse_elf(data)
    if build_id != EXPECTED_BUILD_ID:
        raise Failure(f"Build ID mismatch: {build_id}")

    range_report = []
    for name, (start, end, expected) in RANGES.items():
        start_off, end_off = va_to_offset(start, loads), va_to_offset(end - 1, loads) + 1
        actual = hashlib.sha256(data[start_off:end_off]).hexdigest()
        if actual != expected:
            raise Failure(f"instruction-range mismatch for {name}: {actual}")
        range_report.append({"name": name, "raw_va_start": f"0x{start:x}", "raw_va_end": f"0x{end:x}", "sha256": actual})

    literal_report: dict[str, dict[str, str]] = {}
    for name, (va, expected) in LITERALS.items():
        actual = c_string(data, va, loads)
        if actual != expected:
            raise Failure(f"literal mismatch for {name}")
        literal_report[name] = {"raw_va": f"0x{va:x}", "value": actual}

    call_report = []
    for name, (site, expected_target) in DIRECT_CALLS.items():
        target = direct_call_target(data, site, loads)
        if target != expected_target:
            raise Failure(f"direct-call target mismatch for {name}: 0x{target:x}")
        call_report.append({"name": name, "raw_va": f"0x{site:x}", "target_raw_va": f"0x{target:x}"})

    try:
        _, rela_off, rela_size = sections[".rela.dyn"]
    except KeyError as exc:
        raise Failure(".rela.dyn absent") from exc
    if rela_size % 24:
        raise Failure("malformed .rela.dyn size")
    slot_targets = []
    for off in range(rela_off, rela_off + rela_size, 24):
        r_offset, r_info, addend = struct.unpack_from("<QQq", data, off)
        if r_offset == VTABLE_SLOT_VA:
            slot_targets.append((r_info & 0xFFFFFFFF, addend))
    if slot_targets != [(8, VTABLE_TARGET_VA)]:
        raise Failure(f"finish vtable relocation mismatch: {slot_targets!r}")

    if conditional_jump_target(data, 0xD2407, loads) != 0xD2C08:
        raise Failure("finalizer-failure branch target mismatch")
    if direct_jump_target(data, 0xD2C2D, loads) != 0xD242E:
        raise Failure("finalizer-failure rejoin target mismatch")
    expect_bytes(data, 0xD2429, b"\xc6\x44\x24\x10\x01", loads)
    expect_bytes(data, 0xD245C, b"\xb9\x63\x00\x00\x00", loads)
    expect_bytes(data, 0xD2C28, b"\xc6\x44\x24\x10\x00", loads)
    expect_bytes(data, 0xD2ADD, b"\xb9\x64\x00\x00\x00", loads)
    expect_bytes(data, 0xD2B0A, b"\x0f\xb6\x6c\x24\x10", loads)

    return {
        "schema": SCHEMA,
        "tool": TOOL,
        "tool_version": VERSION,
        "input": {"size": len(data), "sha256": digest, "build_id": build_id},
        "instruction_ranges": range_report,
        "literal_anchors": literal_report,
        "direct_calls": call_report,
        "finish_dispatch": {
            "vtable_slot_raw_va": f"0x{VTABLE_SLOT_VA:x}",
            "relocation_type": "R_X86_64_RELATIVE",
            "finish_raw_va": f"0x{VTABLE_TARGET_VA:x}",
        },
        "fstab_rewrite": {
            "admission": "root is selected and either foldervr or vr is selected",
            "selected_vr_variant": "foldervr when present, otherwise vr",
            "direction": "replace the selected VR variant's active partition pathname with its inactive partition pathname",
            "candidate_files": [
                "/mnt/root/etc/fstab_emmc",
                "/mnt/root/etc/fstab_emmc_fde",
                "/mnt/root/etc/fstab",
            ],
            "durability_sequence": "QString replace, QIODevice write, QFileDevice flush, fsync(handle), close",
            "scope": "VR pathname maintenance inside the mounted inactive root; not a root-slot selector update",
        },
        "finish_flow": {
            "ordered_observations": [
                "a mode-byte/object-state guard can return before the main maintenance path",
                "after that guard, sync and a one-second sleep precede post-write finalization",
                "the inactive root pathname is derived and compared with the device mounted at /mnt/root",
                "the inactive root is mounted for maintenance when that comparison does not match",
                "the fstab rewrite helper is called before progress value 99",
                "a false fstab-helper result stores the eventual false return value and rejoins immediately before progress value 99",
                "root, app and selected VR mountpoints have bounded fstrim and unmount maintenance paths",
                "resumeBlockNumber marker paths are removed on the shared normal tail after optional selected-VR maintenance",
                "the normal tail reports progress value 100 and then returns the stored result byte",
            ],
            "failure_boundary": "A fstab-helper failure does not itself prevent the progress-99 path. If later processing reaches the normal tail, progress 100 can be reported while finish still returns false.",
        },
        "bounded_conclusion": {
            "status": "exact_static_postwrite_finalization_boundary",
            "established": [
                "The virtual finish implementation resolves and maintains the inactive root after partition writing.",
                "Its fstab helper rewrites active-to-inactive VR pathname references in the inactive root and flushes/fsyncs each opened configuration file.",
                "Completion progress is not equivalent to a true finish return: the finalizer-failure path preserves false while rejoining completion processing.",
                "The reviewed finalizer performs mount, fstab, trim, unmount and resume-marker maintenance; these are not a demonstrated persistent root-slot activation primitive.",
            ],
            "not_established": [
                "runtime invocation or successful mounting, replacement, flushing, trimming, unmounting, or marker removal",
                "same-object or same-byte continuity from authentication through final partition bytes",
                "final partition integrity or successful partition-write confirmation",
                "persistent boot-slot selection, MICOM or ABL acceptance, health, mark-good, rollback, root, or persistence",
            ],
        },
    }


def emit(obj: object, output: Path | None) -> None:
    payload = (json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=False) + "\n").encode("utf-8")
    if output is None:
        sys.stdout.buffer.write(payload)
        return
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    fd = os.open(output, flags, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError("short output write")
            view = view[written:]
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
