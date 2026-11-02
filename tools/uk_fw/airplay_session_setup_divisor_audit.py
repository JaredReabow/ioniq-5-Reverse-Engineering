#!/usr/bin/env python3
"""Verify the recovered AirPlay session-setup zero-divisor candidate offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import sys
from pathlib import Path
from typing import Any

SCHEMA = "ioniq-airplay-session-setup-divisor-audit/v1"
TOOL_VERSION = "1.0.0"
MAX_FILE_BYTES = 64 * 1024 * 1024
EXPECTED_SIZE = 215_896
EXPECTED_SHA256 = "ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0"
ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PROGRAM_HEADER = struct.Struct("<IIQQQQQQ")
PT_LOAD = 1

RANGES = {
    "AirPlayReceiverSessionSetup": (
        0x1998A,
        0x1C24A,
        "31f794fd8074bde88c42fea984664430b3c1a38b2ae43835936e2f25c6a56f41",
    ),
    "setup_encryption_to_session_setup": (
        0x103C3,
        0x10637,
        "5cde34310a8cdf36004c110ed3f9656dbdadaacf2b808fb12dc057e1fce57a81",
    ),
    "main_high_audio_to_divisor_exit": (
        0x19F3F,
        0x1A6D5,
        "22eb130b2e003a5815c9dd7f7d2df880a042b8a8b36bdcff33e2f8f1a54fcf50",
    ),
    "spf_load_and_geometry": (
        0x1A35A,
        0x1A39B,
        "53725b779b9ee88d61bedbfce06dfb9d1039070ef2338eeb1e621c07aa595324",
    ),
    "redundant_audio_branch_to_divisor_exit": (
        0x1A5E1,
        0x1A6D5,
        "617d62b9cd30e77f9f29e7406f36631d451a6d1e5e06e28d9bb460f42214245d",
    ),
    "divisor_load_to_div": (
        0x1A647,
        0x1A6C2,
        "4ca9172f3de6ce259425fe3cb7611aa53f92d561730f5cf6fb21c55688899b84",
    ),
}

ANCHORS = {
    "encryption_error_to_setup": (0x103D7, "837c2450004989c50f8541020000"),
    "encryption_none_to_setup": (0x103E5, "83f8010f8438020000"),
    "session_setup_call": (0x10626, "488b7b10488d5424704c89e6e8a97fffff"),
    "stream_type_main_high": (0x19F4B, "e840eafeff4989c683f866741e"),
    "redundant_audio_lookup_and_store": (0x1A29E, "31d24c89efc683c014000000488d350f000100e8dae6feff31d24c89ef488d35150001008983bc140000"),
    "redundant_audio_cfstring_object": (0x2A2C0, "56070100ffffff7f726564756e64616e74417564696f00"),
    "spf_dictionary_lookup": (0x1A35A, "4c89ef488d35d8ff00004c8dab3009000019c031d283c00b898338040000e813e6feff"),
    "spf_store": (0x1A38C, "898334040000"),
    "redundant_audio_zero_branch": (0x1A5E1, "83bbbc14000000740c"),
    "redundant_audio_nonzero_bypass": (0x1A5EA, "c683b803000001e9df000000"),
    "divisor_load": (0x1A647, "8b8b34040000"),
    "unsigned_divide": (0x1A6C0, "f7f1"),
    "spf_cfstring_object": (0x2A33C, "56070100ffffff7f73706600"),
}

PUBLIC_COMPARATOR = {
    "repository": "45clouds/WirelessCarPlay",
    "commit": "51145ef55f8dd9f1cbadd58353cacb5e0ca215e9",
    "session_source": "source/Sources/AirPlayReceiverSession.c",
    "session_source_sha256": "5ed352778a8e786707245ef993994e6e172efd6b89f5fb71893e71e1c8ca3b61",
    "server_source": "source/Sources/AirPlayReceiverServer.c",
    "server_source_sha256": "c517c24c4ae07510b7d00c5b31656e9397076c2de9058ef5ad3d41383d47a571",
    "role": "comparative semantic names only; recovered bytes and addresses are authoritative",
}


class AuditError(ValueError):
    """An input or deterministic-output invariant failed."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_read(path: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise AuditError(f"not a regular file: {path}")
        if before.st_size < 0 or before.st_size > MAX_FILE_BYTES:
            raise AuditError(f"file exceeds {MAX_FILE_BYTES} byte limit: {path}")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                raise AuditError(f"short read: {path}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise AuditError(f"file grew during read: {path}")
        after = os.fstat(descriptor)
        identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if identity_before != identity_after:
            raise AuditError(f"file identity changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def parse_load_segments(data: bytes) -> list[dict[str, int]]:
    if len(data) < ELF_HEADER.size:
        raise AuditError("truncated ELF header")
    values = ELF_HEADER.unpack_from(data)
    ident = values[0]
    if ident[:4] != b"\x7fELF" or ident[4:7] != b"\x02\x01\x01":
        raise AuditError("expected ELF64 little-endian version 1")
    if values[1] != 3 or values[2] != 62 or values[3] != 1:
        raise AuditError("expected x86-64 ET_DYN ELF version 1")
    phoff, phentsize, phnum = values[5], values[9], values[10]
    if phentsize != PROGRAM_HEADER.size or phnum > 1024:
        raise AuditError("invalid program-header geometry")
    end = phoff + phentsize * phnum
    if phoff > len(data) or end > len(data):
        raise AuditError("program-header table is out of bounds")
    segments: list[dict[str, int]] = []
    for index in range(phnum):
        fields = PROGRAM_HEADER.unpack_from(data, phoff + index * phentsize)
        p_type, p_flags, p_offset, p_vaddr, _p_paddr, p_filesz, p_memsz, p_align = fields
        if p_type != PT_LOAD:
            continue
        if p_filesz > p_memsz or p_offset + p_filesz > len(data):
            raise AuditError("invalid PT_LOAD bounds")
        segments.append(
            {
                "flags": p_flags,
                "offset": p_offset,
                "vaddr": p_vaddr,
                "filesz": p_filesz,
                "memsz": p_memsz,
                "align": p_align,
            }
        )
    if not segments:
        raise AuditError("ELF has no PT_LOAD segment")
    return segments


def va_to_offset(segments: list[dict[str, int]], va: int, size: int) -> int:
    if va < 0 or size < 0 or va + size < va:
        raise AuditError("invalid virtual-address range")
    for segment in segments:
        start = segment["vaddr"]
        end = start + segment["filesz"]
        if start <= va and va + size <= end:
            return segment["offset"] + (va - start)
    raise AuditError(f"virtual-address range is not file-backed: {va:#x}+{size:#x}")


def verify_slice(data: bytes, segments: list[dict[str, int]], va: int, expected: bytes) -> dict[str, Any]:
    offset = va_to_offset(segments, va, len(expected))
    actual = data[offset : offset + len(expected)]
    if actual != expected:
        raise AuditError(f"anchor mismatch at ELF VA {va:#x}")
    return {
        "elf_va": f"0x{va:x}",
        "file_offset": f"0x{offset:x}",
        "size": len(expected),
        "bytes_hex": expected.hex(),
        "sha256": sha256(expected),
        "matched": True,
    }


def build_report(data: bytes) -> dict[str, Any]:
    if len(data) != EXPECTED_SIZE:
        raise AuditError(f"unexpected input size: {len(data)}")
    digest = sha256(data)
    if digest != EXPECTED_SHA256:
        raise AuditError(f"unexpected input SHA-256: {digest}")
    segments = parse_load_segments(data)

    ranges: dict[str, Any] = {}
    for name, (start, end, expected_digest) in RANGES.items():
        offset = va_to_offset(segments, start, end - start)
        actual_digest = sha256(data[offset : offset + end - start])
        if actual_digest != expected_digest:
            raise AuditError(f"range hash mismatch: {name}")
        ranges[name] = {
            "elf_va_start": f"0x{start:x}",
            "elf_va_end_exclusive": f"0x{end:x}",
            "file_offset_start": f"0x{offset:x}",
            "size": end - start,
            "sha256": actual_digest,
            "matched": True,
        }

    anchors = {
        name: verify_slice(data, segments, va, bytes.fromhex(expected_hex))
        for name, (va, expected_hex) in ANCHORS.items()
    }

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "tool": {
            "name": "airplay_session_setup_divisor_audit.py",
            "version": TOOL_VERSION,
        },
        "subject": {
            "basename": "libAirPlay.so",
            "size": len(data),
            "sha256": digest,
            "format": "ELF64 little-endian ET_DYN x86-64",
        },
        "address_model": {
            "artifact_addresses": "ELF virtual addresses",
            "file_mapping": "resolved through file-backed PT_LOAD segments",
            "ghidra_image_base": "0x100000",
            "ghidra_normalization": "subtract 0x100000 from the Ghidra address to obtain the ELF virtual address for this analysis",
            "example": {"ghidra": "0x11998a", "elf_va": "0x1998a"},
        },
        "ranges": ranges,
        "anchors": anchors,
        "decoded_flow": {
            "callback_to_setup": {
                "call_site": "0x10632",
                "callee_plt": "0x85e0 (AirPlayReceiverSessionSetup@plt)",
                "encryption_error_branch": "0x103d7 tests the CFDictionaryGetInt64 error slot and 0x103df branches to 0x10626 when nonzero",
                "encryption_none_branch": "0x103e5 compares encryption type with 1 and 0x103e8 branches to 0x10626 when equal",
                "boundary": "this shows a local route that does not require the MFi-SAP decrypt branch when the getter reports an error or encryption type is None; it does not establish upstream request authorization or live delivery",
            },
            "main_high_audio_selection": {
                "type_key": "type",
                "type_value": "0x66",
                "comparison": "0x19f53 cmp eax,0x66; 0x19f56 je 0x19f76",
                "frames_per_packet_key_exact": "spf",
                "semantic_name_from_public_comparator": "framesPerPacket",
                "lookup_and_store": "0x1a35d loads the CFString object at 0x2a33c; the getter returns at 0x1a37d; 0x1a38c stores EAX at session+0x434",
            },
            "zero_divisor_path": {
                "redundant_audio_state": "session+0x14bc",
                "branch": "0x1a5e1 compares the state with zero; zero falls through the retransmit initialization, while nonzero reaches 0x1a5ea and jumps to 0x1a6d5",
                "divisor": "0x1a647 loads ECX from session+0x434 (the spf value)",
                "operation": "0x1a6c0 executes unsigned div ecx",
                "guard": "the exact 0x1a647..0x1a6c2 byte range contains no divisor-zero rejection between the load and divide",
                "architectural_result_if_zero": "x86 DIV with a zero divisor raises #DE before producing a quotient",
            },
        },
        "assessment": {
            "classification": "exact-static denial-of-service candidate",
            "demonstrated": [
                "exact recovered bytes bind the SETUP callback call to AirPlayReceiverSessionSetup",
                "exact recovered bytes bind MainHighAudio type 0x66 and the spf getter/store",
                "exact recovered bytes bind the redundant-audio branch, divisor load, and unguarded unsigned divide",
                "a zero spf value on that path is an architectural divide exception",
            ],
            "not_demonstrated": [
                "that a physical phone, USB/NCM peer, or network peer can deliver the required dictionary to the exact installed unit",
                "listener/interface exposure, upstream generic HTTP authorization state, or route eligibility at runtime",
                "that session creation, control setup, socket setup, and earlier format checks all succeed on a live unit",
                "process termination, service restart behavior, or user-visible denial of service",
                "memory corruption, code execution, authentication bypass, root access, SMACK escape, persistence, or firmware modification",
                "CVE identity, affected-versus-fixed lineage, or impact on the owner's installed firmware",
            ],
            "prerequisites": [
                "the exact recovered libAirPlay.so identity",
                "a locally accepted SETUP request with a parsed dictionary",
                "successful session/control setup up to the reviewed stream branch",
                "a streams array containing a MainHighAudio descriptor (type 0x66)",
                "audio compression/format values accepted by earlier checks",
                "redundantAudio resolving to zero",
                "spf resolving to zero",
            ],
            "mfi_sap_required_for_this_candidate": False,
            "mfi_sap_note": "the exact encryption-error and encryption-None branches reach AirPlayReceiverSessionSetup without entering the reviewed MFi-SAP decrypt path; other runtime gates remain unexcluded",
            "cve_attribution": None,
        },
        "public_comparator": PUBLIC_COMPARATOR,
    }
    report["canonical_sha256"] = sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    )
    return report


def encode_report(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def exclusive_write(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o644)
    try:
        total = 0
        while total < len(payload):
            written = os.write(descriptor, payload[total:])
            if written <= 0:
                raise AuditError(f"short write: {path}")
            total += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="recovered libAirPlay.so")
    parser.add_argument("--output", type=Path, help="create report without overwriting an existing path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = build_report(stable_read(args.input))
        payload = encode_report(report)
        if args.output is None:
            sys.stdout.buffer.write(payload)
        else:
            exclusive_write(args.output, payload)
    except (AuditError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
