#!/usr/bin/env python3
"""Verify AppFUMO boot-image pairing, staging, and stock repair boundaries.

The analyzer is execution-free.  It reads one exact embedded AppFUMO ELF and
one exact canonical rootfs archive, then emits deterministic bounded evidence.
It never executes recovered code, mounts media, writes a target partition, or
constructs a boot image.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import posixpath
import stat
import struct
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

TOOL = "appfumo-boot-image-pairing"
VERSION = "1.0.0"
SCHEMA = "appfumo-boot-image-pairing/v1"
MAX_ELF_SIZE = 16 * 1024 * 1024
MAX_ROOTFS_SIZE = 1024 * 1024 * 1024
MAX_MEMBER_SIZE = 1024 * 1024

ELF_SIZE = 5_066_264
ELF_SHA256 = "464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7"
ELF_BUILD_ID = "863a8730e66a1c5245a1bf458fe2554adee0351a"
ROOTFS_SIZE = 879_109_759
ROOTFS_SHA256 = "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84"
ROOTFS_MEMBER_COUNT = 66_836
ROOTFS_INVENTORY_SHA256 = "c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c"
ESINIT_NAME = "./lib/systemd/esinit"
ESINIT_MODE = 0o755
ESINIT_SIZE = 17_894
ESINIT_SHA256 = "9f39947ec144322b29c0366bb681f0452ae3696139589bc2f4a2f05bf44afa52"

RANGES = {
    "boot_filename_selector": (0xA2480, 0xA2C17, "b0c155bb9f8b81ca5bba4035166690ea44d959277d75bbaf66e3633126905b57"),
    "boot_image_staging": (0xA2EF0, 0xA3E83, "40971ac6025a7c7e8fbfbeacb6143809789dcfb408b517c55f278d9e7e1bf42b"),
    "staging_caller_context": (0xAAA80, 0xAAB20, "c790649c7d91ad51a243705e3a3d73337c0eac6179eac8e8c75c495666846618"),
    "copy_helper": (0x1413F0, 0x141B28, "88d727d519722aeb8f621abcf4db6ba5eb730203fdeb9fe44d813cd84b018a85"),
}

LITERALS = {
    "root_p3": (0x2110FC, "/dev/mmcblk0p3"),
    "root_p5": (0x211128, "/dev/mmcblk0p5"),
    "root_p7": (0x211137, "/dev/mmcblk0p7"),
    "p3_default": (0x22DB33, "iasImage"),
    "p3_1280": (0x2163A9, "iasImage_1280"),
    "p3_1920_12": (0x2163B7, "iasImage_1920_12"),
    "p5_default": (0x2163C8, "iasImage_p5"),
    "p5_1280": (0x2163D4, "iasImage_p5_1280"),
    "p5_1920_12": (0x2163E5, "iasImage_p5_1920_12"),
    "p7_default": (0x2163F9, "iasImage_p7"),
    "p7_1280": (0x216405, "iasImage_p7_1280"),
    "p7_1920_12": (0x216416, "iasImage_p7_1920_12"),
    "source_suffix": (0x20BBC6, "/HU/images"),
    "staging_root": (0x2130F6, "/tmp/update/usb"),
    "staging_suffix": (0x216E92, "/bootImage"),
    "sub_suffix": (0x22DB45, "_sub"),
}

DIRECT_CALLS = {
    "selector_record_copy_index_1": (0xA24E0, 0xA0D50),
    "staging_select_filename": (0xA30B5, 0xA2480),
    "staging_copy_normal": (0xA3370, 0x1413F0),
    "staging_copy_sub": (0xA396E, 0x1413F0),
    "preparation_stage_boot_images": (0xAAAC1, 0xA2EF0),
    "copy_read_all": (0x1416A3, 0x24100),
    "copy_write_buffer": (0x1416C2, 0x231C0),
    "copy_flush": (0x1416DE, 0x246D0),
    "copy_handle": (0x1416E6, 0x24750),
    "copy_fsync": (0x1416ED, 0x23840),
    "copy_close_source": (0x1417B8, 0x22020),
    "copy_close_destination": (0x1417C0, 0x22020),
    "copy_source_size": (0x1417DB, 0x21F40),
    "copy_destination_size": (0x1417F1, 0x21F40),
    "copy_set_permissions": (0x141905, 0x231F0),
}

# These exact instruction fragments close the material branch semantics without
# requiring a host disassembler at report time.
INSTRUCTION_ANCHORS = {
    "selector_p3_display_mode_dispatch": (0xA2593, bytes.fromhex(
        "8b0517fb620083f8030f848e02000083f8010f842504000083e80283e0fd7475"
    )),
    "selector_p5_display_mode_dispatch": (0xA275E, bytes.fromhex(
        "8b054cf9620083f8030f840b03000083f8010f845a03000083e80283"
    )),
    "selector_p7_display_mode_dispatch": (0xA294C, bytes.fromhex(
        "8b055ef7620083f8030f84cd01000083f8010f841c02000083e80283"
    )),
    "staging_normal_sub_existence_gates": (0xA3149, bytes.fromhex(
        "488b3424488b7c2420e82914f8ff84c07412488b7c2430e83b09f8ff84c00f842e090000"
        "488b742418488b7c2420e80414f8ff84c00f847405"
    )),
    "staging_normal_then_sub_gate": (0xA33F2, bytes.fromhex(
        "84db0f84760100004584f60f859d0400"
    )),
    "preparation_staging_result_capture": (0xAAAC1, bytes.fromhex(
        "e82a84ffff4189c6488d85f0eaffff"
    )),
    "copy_read_buffer_to_write": (0x141695, bytes.fromhex(
        "488d9c24b00000004c89e64889dfe8582aeeff4c8bbc24b00000004c89ffe80844f1ff"
        "496357044889ef4889c6e8f91aeeff"
    )),
    "copy_requested_length_from_buffer": (0x1416B8, bytes.fromhex("496357044889ef4889c6")),
    "copy_negative_write_failure_test": (0x1416D2, bytes.fromhex("4d85ff0f88a5020000")),
    "copy_ignored_flush_fsync_results": (0x1416DB, bytes.fromhex(
        "4889efe8ed2feeff4889efe86530eeff89c7e84e21eeff"
    )),
    "copy_close_reopen_size_compare": (0x1417B5, bytes.fromhex(
        "4c89e7e86308eeff4889efe85b08eeff4c8dbc24200100004c89f64c89ffe82815eeff"
        "4c89ffe86007eeff4c89ee4889df4989c6e81215eeff4889dfe84a07eeff4889df48890424"
        "e86e14eeff4c89ffe86614eeff488b04244939c60f84e1000000"
    )),
    "copy_post_close_size_compare": (0x14180A, bytes.fromhex("488b04244939c60f84e1000000")),
    "copy_permissions_success_gate": (0x1418F8, bytes.fromhex(
        "4c89e7e8301ceeff89c64889efe8e618eeff41be0100000084c00f85c6fcffff"
    )),
}

FILENAME_MATRIX = (
    ("/dev/mmcblk0p3", 3, "iasImage"),
    ("/dev/mmcblk0p3", 1, "iasImage_1280"),
    ("/dev/mmcblk0p3", 2, "iasImage_1920_12"),
    ("/dev/mmcblk0p3", 4, "iasImage_1920_12"),
    ("/dev/mmcblk0p5", 3, "iasImage_p5"),
    ("/dev/mmcblk0p5", 1, "iasImage_p5_1280"),
    ("/dev/mmcblk0p5", 2, "iasImage_p5_1920_12"),
    ("/dev/mmcblk0p5", 4, "iasImage_p5_1920_12"),
    ("/dev/mmcblk0p7", 3, "iasImage_p7"),
    ("/dev/mmcblk0p7", 1, "iasImage_p7_1280"),
    ("/dev/mmcblk0p7", 2, "iasImage_p7_1920_12"),
    ("/dev/mmcblk0p7", 4, "iasImage_p7_1920_12"),
)

ESINIT_SNIPPETS = (
    '#PLK1: ABL.boot=2\n#PLK2: ABL.boot=3\n',
    '#grep "ABL.boot=2" /proc/cmdline >/dev/null\n'
    'grep "ABL.bdev=mmc2:/iasImage" /proc/cmdline >/dev/null\n',
    '/sbin/fsck.ext2  -fy /dev/mmcblk0p1  >/dev/null 2>&1\n',
    'mount /dev/mmcblk0p2 /tmp/plk2\n'
    '    mount /dev/mmcblk0p1 /tmp/plk1\n'
    '    cp /tmp/plk2/iasImage /tmp/plk1/iasImage\n',
    'if [ -f /sys/module/i915/parameters/splash_error ]; then\n'
    '\tsplash_error="$(cat /sys/module/i915/parameters/splash_error)"\n'
    '\tif [ "$splash_error" = "1" ]; then\n',
    '/sbin/fsck.ext2  -fy /dev/mmcblk0p2  >/dev/null 2>&1\n',
    'mount  /dev/mmcblk0p1 /tmp/plk1\n',
    'mount  /dev/mmcblk0p2 /tmp/plk2\n',
    'cp /tmp/plk1/iasImage /tmp/plk2/iasImage\n',
)


class Failure(Exception):
    """An input or evidence item falls outside the frozen contract."""


@dataclass(frozen=True)
class MemberExpectation:
    name: str
    mode: int
    uid: int
    gid: int
    size: int
    sha256: str


@dataclass(frozen=True)
class ArchiveResult:
    sha256: str
    size: int
    member_count: int
    inventory_sha256: str
    member_bytes: bytes


def _identity(value: os.stat_result) -> tuple[int, int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _open_regular_nofollow(path: Path, maximum: int, what: str) -> tuple[int, os.stat_result]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise Failure(f"cannot open {what} safely: {exc}") from exc
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise Failure(f"{what} is not a regular file")
        if st.st_size < 0 or st.st_size > maximum:
            raise Failure(f"{what} exceeds the size limit")
        return fd, st
    except Exception:
        os.close(fd)
        raise


def stable_read(path: Path, maximum: int, what: str) -> bytes:
    fd, before = _open_regular_nofollow(path, maximum, what)
    try:
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(fd, min(remaining, 1024 * 1024))
            if not chunk:
                raise Failure(f"short read from {what}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(fd, 1):
            raise Failure(f"{what} grew while being read")
        after = os.fstat(fd)
        if _identity(before) != _identity(after):
            raise Failure(f"{what} changed while being read")
        return b"".join(chunks)
    finally:
        os.close(fd)


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def u64(data: bytes, offset: int) -> int:
    return struct.unpack_from("<Q", data, offset)[0]


def parse_elf(data: bytes) -> tuple[str, list[tuple[int, int, int]]]:
    if data[:16] != b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8:
        raise Failure("unsupported ELF identity")
    if len(data) < 64 or u16(data, 0x12) != 62 or u32(data, 0x14) != 1:
        raise Failure("unsupported ELF ABI")
    phoff, phents, phnum = u64(data, 0x20), u16(data, 0x36), u16(data, 0x38)
    if phents != 56 or not 0 < phnum <= 256 or phoff + phents * phnum > len(data):
        raise Failure("malformed ELF program-header table")
    loads: list[tuple[int, int, int]] = []
    build_id: str | None = None
    for index in range(phnum):
        offset = phoff + index * phents
        p_type = u32(data, offset)
        p_offset, p_vaddr = u64(data, offset + 8), u64(data, offset + 16)
        p_filesz, p_memsz = u64(data, offset + 32), u64(data, offset + 40)
        if p_filesz > p_memsz or p_offset + p_filesz > len(data):
            raise Failure("ELF program segment exceeds file")
        if p_type == 1:
            loads.append((p_vaddr, p_vaddr + p_filesz, p_offset))
        elif p_type == 4:
            cursor, end = p_offset, p_offset + p_filesz
            while cursor < end:
                if cursor + 12 > end:
                    raise Failure("truncated PT_NOTE header")
                namesz, descsz, note_type = struct.unpack_from("<III", data, cursor)
                cursor += 12
                padded_name = (namesz + 3) & ~3
                padded_desc = (descsz + 3) & ~3
                if cursor + padded_name + padded_desc > end:
                    raise Failure("truncated PT_NOTE record")
                name = data[cursor:cursor + namesz]
                cursor += padded_name
                desc = data[cursor:cursor + descsz]
                cursor += padded_desc
                if name.rstrip(b"\0") == b"GNU" and note_type == 3:
                    if build_id is not None:
                        raise Failure("duplicate GNU Build ID")
                    build_id = desc.hex()
    if build_id is None or not loads:
        raise Failure("required ELF identity records are absent")
    loads.sort()
    for left, right in zip(loads, loads[1:]):
        if left[1] > right[0]:
            raise Failure("overlapping file-backed PT_LOAD ranges")
    return build_id, loads


def va_to_offset(va: int, size: int, loads: list[tuple[int, int, int]]) -> int:
    if type(va) is not int or type(size) is not int or va < 0 or size < 0:
        raise Failure("invalid virtual range")
    end = va + size
    hits = [(va - start) + offset for start, stop, offset in loads if start <= va and end <= stop]
    if len(hits) != 1:
        raise Failure(f"virtual range does not map uniquely: 0x{va:x}+0x{size:x}")
    return hits[0]


def bytes_at(data: bytes, va: int, size: int, loads: list[tuple[int, int, int]]) -> bytes:
    offset = va_to_offset(va, size, loads)
    return data[offset:offset + size]


def c_string(data: bytes, va: int, loads: list[tuple[int, int, int]]) -> str:
    offset = va_to_offset(va, 1, loads)
    limit = min(len(data), offset + 4096)
    end = data.find(b"\0", offset, limit)
    if end < 0:
        raise Failure(f"unterminated string at 0x{va:x}")
    try:
        return data[offset:end].decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise Failure(f"non-UTF-8 string at 0x{va:x}") from exc


def direct_call_target(data: bytes, va: int, loads: list[tuple[int, int, int]]) -> int:
    raw = bytes_at(data, va, 5, loads)
    if raw[0] != 0xE8:
        raise Failure(f"expected direct call at 0x{va:x}")
    return va + 5 + struct.unpack_from("<i", raw, 1)[0]


def audit_elf(path: Path) -> dict[str, object]:
    data = stable_read(path, MAX_ELF_SIZE, "AppFUMO ELF")
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != ELF_SIZE or digest != ELF_SHA256:
        raise Failure("AppFUMO ELF identity mismatch")
    build_id, loads = parse_elf(data)
    if build_id != ELF_BUILD_ID:
        raise Failure("AppFUMO Build ID mismatch")

    ranges: dict[str, dict[str, object]] = {}
    for role, (start, end, expected) in RANGES.items():
        raw = bytes_at(data, start, end - start, loads)
        actual = hashlib.sha256(raw).hexdigest()
        if actual != expected:
            raise Failure(f"machine-code range drift: {role}")
        ranges[role] = {"start": start, "end_exclusive": end, "sha256": actual}

    literals: dict[str, dict[str, object]] = {}
    for role, (va, expected) in LITERALS.items():
        actual = c_string(data, va, loads)
        if actual != expected:
            raise Failure(f"literal drift: {role}")
        literals[role] = {"va": va, "value": actual}

    calls: dict[str, dict[str, int]] = {}
    for role, (site, target) in DIRECT_CALLS.items():
        actual = direct_call_target(data, site, loads)
        if actual != target:
            raise Failure(f"direct-call drift: {role}")
        calls[role] = {"site": site, "target": actual}

    anchors: dict[str, dict[str, object]] = {}
    for role, (va, expected) in INSTRUCTION_ANCHORS.items():
        actual = bytes_at(data, va, len(expected), loads)
        if actual != expected:
            raise Failure(f"instruction-anchor drift: {role}")
        anchors[role] = {"va": va, "size": len(expected), "sha256": hashlib.sha256(actual).hexdigest()}

    return {
        "size": len(data),
        "sha256": digest,
        "build_id": build_id,
        "ranges": ranges,
        "literals": literals,
        "direct_calls": calls,
        "instruction_anchors": anchors,
    }


class _HashingReader:
    def __init__(self, handle: BinaryIO):
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


def canonical_member_name(name: str) -> str:
    if not name or "\0" in name or name.startswith("/"):
        raise Failure("unsafe archive member name")
    if name == ".":
        return "."
    parts = name.split("/")
    if parts and parts[0] == ".":
        parts = parts[1:]
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise Failure("unsafe archive member spelling")
    canonical = posixpath.normpath("/".join(parts))
    if canonical in ("", ".", "..") or canonical.startswith("../"):
        raise Failure("archive member escapes root")
    return canonical


def inventory_line(index: int, member: tarfile.TarInfo) -> bytes:
    try:
        return (f"{index}\t{member.name}\t{member.type.hex()}\t{member.mode:o}\t"
                f"{member.size}\t{member.linkname}\n").encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise Failure("archive inventory is not UTF-8") from exc


def scan_archive_handle(handle: BinaryIO, declared_size: int, expectation: MemberExpectation) -> ArchiveResult:
    reader = _HashingReader(handle)
    inventory = hashlib.sha256()
    count = 0
    selected: bytes | None = None
    selected_canonical = canonical_member_name(expectation.name)
    try:
        with tarfile.open(fileobj=reader, mode="r|gz") as archive:
            for index, member in enumerate(archive):
                count += 1
                inventory.update(inventory_line(index, member))
                canonical = canonical_member_name(member.name)
                if canonical != selected_canonical:
                    continue
                if member.name != expectation.name:
                    raise Failure("selected rootfs member is present through an alias")
                if selected is not None:
                    raise Failure("selected rootfs member is duplicated")
                if (not member.isreg() or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                        or member.linkname or member.mode != expectation.mode
                        or member.uid != expectation.uid or member.gid != expectation.gid
                        or member.size != expectation.size or member.size > MAX_MEMBER_SIZE):
                    raise Failure("selected rootfs member metadata drift")
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise Failure("selected rootfs member cannot be streamed")
                value = extracted.read(member.size + 1)
                if len(value) != member.size:
                    raise Failure("selected rootfs member length drift")
                if hashlib.sha256(value).hexdigest() != expectation.sha256:
                    raise Failure("selected rootfs member content drift")
                selected = value
        while reader.read(1024 * 1024):
            pass
    except (tarfile.TarError, OSError) as exc:
        raise Failure(f"cannot stream rootfs archive: {type(exc).__name__}") from exc
    if handle.tell() != declared_size:
        raise Failure("rootfs archive was not consumed to its declared size")
    if selected is None:
        raise Failure("selected rootfs member is missing")
    return ArchiveResult(reader.digest.hexdigest(), declared_size, count, inventory.hexdigest(), selected)


def audit_rootfs(path: Path) -> tuple[dict[str, object], bytes]:
    fd, before = _open_regular_nofollow(path, MAX_ROOTFS_SIZE, "rootfs archive")
    try:
        if before.st_size != ROOTFS_SIZE:
            raise Failure("rootfs archive size mismatch")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            result = scan_archive_handle(handle, before.st_size, MemberExpectation(
                ESINIT_NAME, ESINIT_MODE, 0, 0, ESINIT_SIZE, ESINIT_SHA256
            ))
        after = os.fstat(fd)
        if _identity(before) != _identity(after):
            raise Failure("rootfs archive changed during analysis")
    finally:
        os.close(fd)
    if result.sha256 != ROOTFS_SHA256:
        raise Failure("rootfs archive SHA-256 mismatch")
    if result.member_count != ROOTFS_MEMBER_COUNT or result.inventory_sha256 != ROOTFS_INVENTORY_SHA256:
        raise Failure("rootfs complete inventory identity mismatch")
    return ({
        "size": result.size,
        "sha256": result.sha256,
        "member_count": result.member_count,
        "inventory_sha256": result.inventory_sha256,
        "selected_member": {
            "role": "early_userspace_initialization",
            "type": "regular",
            "mode": "0755",
            "uid": 0,
            "gid": 0,
            "size": ESINIT_SIZE,
            "sha256": ESINIT_SHA256,
        },
    }, result.member_bytes)


def audit_esinit(data: bytes) -> dict[str, object]:
    if len(data) != ESINIT_SIZE or hashlib.sha256(data).hexdigest() != ESINIT_SHA256:
        raise Failure("esinit identity mismatch")
    if b"\0" in data or b"\r" in data or not data.endswith(b"\n"):
        raise Failure("esinit is not strict LF text")
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise Failure("esinit is not UTF-8") from exc
    cursor = 0
    anchors: list[dict[str, object]] = []
    for snippet in ESINIT_SNIPPETS:
        offset = text.find(snippet, cursor)
        if offset < 0:
            raise Failure("esinit semantic snippet drift")
        anchors.append({
            "offset": len(text[:offset].encode("utf-8")),
            "size": len(snippet.encode("utf-8")),
            "sha256": hashlib.sha256(snippet.encode("utf-8")).hexdigest(),
        })
        cursor = offset + len(snippet)
    active_boot_selector_names = tuple(name for name in (
        "fw_setenv", "abctl", "systemd-bless-boot", "mark-good", "bootcount"
    ) if name in text)
    if active_boot_selector_names:
        raise Failure("unexpected boot selector/mark-good token appeared in esinit")
    if 'grep "ABL.boot=2" /proc/cmdline' not in text or '#grep "ABL.boot=2" /proc/cmdline' not in text:
        raise Failure("expected commented ABL.boot probe drift")
    return {
        "semantic_anchor_count": len(anchors),
        "semantic_anchors": anchors,
        "commented_boot_mode_mapping": {
            "ELK": 0,
            "CLI": 1,
            "PLK1": 2,
            "PLK2": 3,
            "runtime_effect": False,
        },
        "active_cmdline_probe": "ABL.bdev pairing marker",
        "probe_is_post_boot_observation": True,
        "probe_is_persistent_selector": False,
        "probe_true_repair_direction": "boot partition 2 image to boot partition 1 image",
        "splash_error_repair_direction": "boot partition 1 image to boot partition 2 image",
        "exact_selector_or_mark_good_token_absence": list((
            "fw_setenv", "abctl", "systemd-bless-boot", "mark-good", "bootcount"
        )),
    }


def build_report(elf_path: Path, rootfs_path: Path) -> dict[str, object]:
    elf = audit_elf(elf_path)
    rootfs, esinit_bytes = audit_rootfs(rootfs_path)
    esinit = audit_esinit(esinit_bytes)
    matrix = [
        {"selected_root_target": root, "display_mode": mode, "staged_basename": name}
        for root, mode, name in FILENAME_MATRIX
    ]
    return {
        "schema": SCHEMA,
        "tool": {"name": TOOL, "version": VERSION},
        "artifacts": {
            "appfumo": {key: elf[key] for key in ("size", "sha256", "build_id")},
            "canonical_rootfs": {key: rootfs[key] for key in (
                "size", "sha256", "member_count", "inventory_sha256", "selected_member"
            )},
        },
        "exact_static": {
            "root_target_display_filename_matrix": matrix,
            "selector": {
                "copied_partition_record_index": 1,
                "target_field_offset": 0x28,
                "supported_display_modes": [1, 2, 3, 4],
                "unsupported_display_mode_result": "empty string",
                "range": elf["ranges"]["boot_filename_selector"],
            },
            "staging": {
                "source_role": "package-base plus HU image directory",
                "destination_role": "temporary update boot-image directory",
                "requires_selected_normal_source_name": True,
                "requires_selected_sub_companion_source_name": True,
                "normal_and_sub_use_same_copy_helper": True,
                "preparation_call_site_bound": True,
                "range": elf["ranges"]["boot_image_staging"],
            },
            "copy_helper": {
                "range": elf["ranges"]["copy_helper"],
                "source_read_all_buffer_passed_to_destination_write": True,
                "requested_write_length_loaded_from_buffer_length": True,
                "immediate_write_result_check": "negative-only",
                "post_close_source_destination_size_equality_required": True,
                "source_permissions_applied_to_destination_and_success_required": True,
                "flush_return_checked": False,
                "fsync_return_checked": False,
                "destination_content_readback": False,
                "destination_content_digest_or_signature": False,
                "stable_source_destination_inode_identity": False,
            },
            "early_userspace_repair": esinit,
            "machine_evidence": {
                "ranges": elf["ranges"],
                "direct_calls": elf["direct_calls"],
                "instruction_anchors": elf["instruction_anchors"],
                "literals": elf["literals"],
            },
        },
        "conclusions": {
            "inactive_root_record_to_boot_filename_pairing": True,
            "normal_and_sub_companion_staging_paths_present": True,
            "copy_helper_success_requires_equal_final_sizes": True,
            "copy_helper_proves_destination_byte_identity": False,
            "staged_boot_image_payload_present_in_recovered_package": None,
            "staging_copy_succeeded": None,
            "boot_image_authenticated_after_staging": None,
            "boot_partition_write_succeeded": None,
            "persistent_boot_target_selected": None,
            "abl_or_micom_accepted_image": None,
            "boot_health_or_mark_good_completed": None,
            "rollback_behavior_established": False,
            "root_or_persistence_established": False,
        },
        "limitations": [
            "The filename matrix binds selected inactive-root targets to candidate boot-image names; it does not inspect the named image contents.",
            "The copy helper passes one in-memory source buffer to a destination write and later compares sizes, but performs no destination-byte readback, digest, or signature verification.",
            "Static call sites do not establish successful source existence checks, copy, flush, fsync, permission change, or durable storage effects.",
            "The active early-userspace command-line probe observes the boot already in progress and drives repair copying; it is not a demonstrated persistent selector.",
            "The PLK/ABL.boot mapping is present only in comments and is not executable evidence.",
            "No boot-image payload presence, boot-partition activation, reset, ABL/MICOM acceptance, health decision, mark-good action, rollback, root, or persistence is established.",
        ],
    }


def encode_report(report: dict[str, object]) -> bytes:
    return (json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False, separators=(",", ": ")) + "\n").encode("utf-8")


def write_exclusive(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise Failure(f"cannot create output exclusively: {exc}") from exc
    try:
        total = 0
        while total < len(payload):
            written = os.write(fd, payload[total:])
            if written <= 0:
                raise Failure("short output write")
            total += written
    except Exception:
        try:
            os.unlink(path)
        except OSError:
            pass
        raise
    finally:
        os.close(fd)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("elf", type=Path, help="exact embedded AppFUMO ELF")
    value.add_argument("rootfs", type=Path, help="canonical mango-rootfs.tar.gz")
    value.add_argument("-o", "--output", type=Path, help="exclusive JSON output path")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        payload = encode_report(build_report(args.elf, args.rootfs))
        if args.output is None:
            sys.stdout.buffer.write(payload)
        else:
            write_exclusive(args.output, payload)
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
