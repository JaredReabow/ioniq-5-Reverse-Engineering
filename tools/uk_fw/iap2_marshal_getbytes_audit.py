#!/usr/bin/env python3
"""Verify the recovered iAP2 marshaled-byte helper and every direct static caller offline."""

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

SCHEMA = "ioniq-iap2-marshal-getbytes-audit/v1"
TOOL_VERSION = "1.0.0"
MAX_FILE_BYTES = 64 * 1024 * 1024
ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PROGRAM_HEADER = struct.Struct("<IIQQQQQQ")
PT_LOAD = 1

SUBJECTS = {
    "framework": {
        "basename": "libiAP2AppFramework-2.0.so",
        "size": 190_272,
        "sha256": "d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120",
    },
    "service": {
        "basename": "iAP2Service-2.0",
        "size": 633_216,
        "sha256": "38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e",
    },
}

FRAMEWORK_RANGES = {
    "iAp2MarshalInitFromTxn": (0x210FF, 0x21175, "4e7fbd707234bf553adf0c59de1501865d873ebeae4ee058f59139124dbf5729"),
    "bounded_aligned_byte_accessor": (0x21645, 0x2176A, "98cbc5af41238b006a7497dfce512b59c21b448f616a55ff641597a058303fcf"),
    "iAp2MarshalGetBytes": (0x21A56, 0x21B21, "601fc208cd6c41eb6926c782dcafcedd47c88785516c98c1290ebcdd2e08ac31"),
}

FRAMEWORK_ANCHORS = {
    "get_length_store_and_bounded_accessor_call": (
        0x21AE3,
        "488b45e84889c7e82136feff89c2488b45e08910488b45e08b10488b45e889d64889c7e83afbffff",
    ),
    "length_overflow_guard_and_four_byte_rounding": (
        0x2166B,
        "837dd4fc762e4c8d057f940000b9ea000000488d1555940000488d3567940000bf5a000000b800000000e8c63bfeffe9b10000008b45d483c00383e0fc8945d4",
    ),
    "remaining_length_check_and_failure_state": (
        0x216AB,
        "488b45d88b400c3b45d4735f488b45d8c7400c00000000488b45d88b401883c80289c2488b45d8895018488b45d88b500c4883ec088b45d4504189d14c8d0582940000b9f4",
    ),
    "success_pointer_and_remaining_advance": (
        0x21716,
        "488b45d8488b00488945f0488b45d8488b108b45d44801c2488b45d8488910488b45d88b400c2b45d489c2488b45d889500c488b",
    ),
}

CALLER_RANGES = {
    "heap_string_materializer": (0x2957C, 0x296A7, "f21e5820d74dfce847a6d0817ec9ce5e466a8c18eb1a4648820387f5891dd1bb"),
    "SessionBTConnection": (0x3C368, 0x3C77B, "2e6f8131494a2f555ec211b903c2b91368062e1649e78f72f59fa1a917b1d187"),
    "SessionLocation": (0x3E0DE, 0x3E48A, "fb309c942bd31f30925e3c8e1f22ec0bd9a630c1e0fde79d69c62dd5da6b9779"),
    "SessionAppLaunch": (0x3F544, 0x3F7AD, "9629dd8242b4d514d7778ac57525828d7fd9c185540cb272e08ce0bbc93d907a"),
    "SessionExternalAccessoryProtocol": (0x41BE2, 0x41F2B, "d984621d5bf56706e588c0563a2105b430ec0dda914a1879ceafebb56cc8ddf1"),
    "SessionHID": (0x42CFC, 0x430CF, "4cc3645bfbf52be8ebfa05d9c8e3fb39052c7a226f06b881515575badcf550e8"),
    "SessionMediaLibraryUpdates": (0x47428, 0x47806, "bebd730b3facc4f1238e133862007b1e46d99552e5cc63a3e9b5cef92e64ef02"),
    "SessionVoiceOver": (0x4B0D8, 0x4BB86, "e7ea5ffe2e26d5946674090580ca497c436095b39f9c106544948e8d54697ebc"),
    "SessionWiFiInformation": (0x4E47E, 0x4E7EF, "feba28457c2892542a83c923403215ced41b529e10f5ce79c6a6e6d032eba05d"),
    "SessionPlayMediaLibrary": (0x4EDE6, 0x4F2B0, "ebe016041ba39ff12c9e73172b0d9a092d72eb330d48b0211a3b4031d0cbae6c"),
    "SessionCommunications": (0x59F24, 0x5B01C, "0bd790bebd7a3abd85570cad0bd216e1a6a05f7788fa4aeab72dc372cac6a2ef"),
}

DIRECT_CALLS = {
    "heap_string_materializer": [0x295D5],
    "SessionBTConnection": [0x3C517, 0x3C620],
    "SessionLocation": [0x3E2B4, 0x3E2EC, 0x3E324, 0x3E35C, 0x3E394, 0x3E3CC, 0x3E404],
    "SessionAppLaunch": [0x3F6CA],
    "SessionExternalAccessoryProtocol": [0x41EA1],
    "SessionHID": [0x42EF2, 0x42FBA],
    "SessionMediaLibraryUpdates": [0x475D9, 0x4760B, 0x47780],
    "SessionVoiceOver": [0x4B603],
    "SessionWiFiInformation": [0x4E6E1, 0x4E713],
    "SessionPlayMediaLibrary": [0x4EF6F, 0x4EFF8, 0x4F039, 0x4F10B, 0x4F1C4],
    "SessionCommunications": [0x5A4F1, 0x5A5C1, 0x5A71A, 0x5A873, 0x5AB0B, 0x5AD05],
}

CALL_BYTES = {
    0x295D5: "e8c6b9fdff", 0x3C517: "e8848afcff", 0x3C620: "e87b89fcff",
    0x3E2B4: "e8e76cfcff", 0x3E2EC: "e8af6cfcff", 0x3E324: "e8776cfcff",
    0x3E35C: "e83f6cfcff", 0x3E394: "e8076cfcff", 0x3E3CC: "e8cf6bfcff",
    0x3E404: "e8976bfcff", 0x3F6CA: "e8d158fcff", 0x41EA1: "e8fa30fcff",
    0x42EF2: "e8a920fcff", 0x42FBA: "e8e11ffcff", 0x475D9: "e8c2d9fbff",
    0x4760B: "e890d9fbff", 0x47780: "e81bd8fbff", 0x4B603: "e89899fbff",
    0x4E6E1: "e8ba68fbff", 0x4E713: "e88868fbff", 0x4EF6F: "e82c60fbff",
    0x4EFF8: "e8a35ffbff", 0x4F039: "e8625ffbff", 0x4F10B: "e8905efbff",
    0x4F1C4: "e8d75dfbff", 0x5A4F1: "e8aaaafaff", 0x5A5C1: "e8daa9faff",
    0x5A71A: "e881a8faff", 0x5A873: "e828a7faff", 0x5AB0B: "e890a4faff",
    0x5AD05: "e896a2faff",
}

WRAPPER_CALLER_RANGES = {
    "SessionConnection": (0x38010, 0x3AB40, "9a5af95a4f5f427a3cd0cbbcd60791f594cc25275381d768855f354dc84f5a3d"),
    "SessionIdentification": (0x556E2, 0x55E2C, "b63fd6951214ff2c6f1a39caaaaf186cfc405868b828c29ec7e50a6ee155320a"),
}

WRAPPER_CALLS = {
    "SessionConnection": [
        (0x38525, "e85210ffff"), (0x385EA, "e88d0fffff"),
        (0x38998, "e8df0bffff"), (0x389FC, "e87b0bffff"),
        (0x38B31, "e8460affff"), (0x38BD6, "e8a109ffff"),
        (0x38C6B, "e80c09ffff"), (0x38D40, "e83708ffff"),
        (0x38E5D, "e81a07ffff"), (0x38EA2, "e8d506ffff"),
        (0x38EE7, "e89006ffff"), (0x38F2C, "e84b06ffff"),
        (0x38F93, "e8e405ffff"), (0x38FD8, "e89f05ffff"),
        (0x39065, "e81205ffff"),
    ],
    "SessionIdentification": [
        (0x55873, "e8043dfdff"), (0x55914, "e8633cfdff"),
        (0x559B5, "e8c23bfdff"), (0x55A56, "e8213bfdff"),
        (0x55AF7, "e8803afdff"), (0x55B98, "e8df39fdff"),
        (0x55C39, "e83e39fdff"),
    ],
}

CALLER_SEMANTICS = {
    "heap_string_materializer": {
        "commands": [], "byte_fields": 1,
        "handling": "frees the previous pointer, obtains pointer+uint32 length, allocates length+1, zeroes the allocation, then strncpy-copies exactly length bytes",
        "finding": "does not reject a null byte pointer returned for a declared length that exceeds the remaining transaction before passing it to strncpy",
    },
    "SessionBTConnection": {"commands": ["0x2f1d", "0x2f1e"], "byte_fields": 2, "handling": "retains pointer+length pairs; transforms two lengths with right shifts before downstream dispatch"},
    "SessionLocation": {"commands": ["0x2eff"], "byte_fields": 7, "handling": "retains seven optional pointer+length pairs in a stack aggregate and dispatches it downstream"},
    "SessionAppLaunch": {"commands": ["0x2f45"], "byte_fields": 1, "handling": "retains AppBundleID pointer+length, logs the pointer with %s, and dispatches the aggregate downstream"},
    "SessionExternalAccessoryProtocol": {"commands": ["0x2f8c"], "byte_fields": 1, "handling": "retains one pointer+length pair followed by a uint16 and dispatches the aggregate downstream"},
    "SessionHID": {"commands": ["0x2f27", "0x2f28"], "byte_fields": 2, "handling": "retains HID-report pointer+length pairs and dispatches stack aggregates downstream"},
    "SessionMediaLibraryUpdates": {"commands": ["0x2f3b", "0x2f3c"], "byte_fields": 3, "handling": "retains library identifiers as pointer+length pairs and dispatches stack aggregates downstream"},
    "SessionVoiceOver": {"commands": ["0x2f68"], "byte_fields": 1, "handling": "retains optional speak-text pointer+length and dispatches the stack aggregate downstream"},
    "SessionWiFiInformation": {"commands": ["0x2f78"], "byte_fields": 2, "handling": "retains two optional Wi-Fi pointer+length pairs and dispatches the stack aggregate downstream"},
    "SessionPlayMediaLibrary": {"commands": ["0x2f81", "0x2f82", "0x2f83", "0x2f84"], "byte_fields": 5, "handling": "retains pointer+length pairs; command 0x2f84 logs its recovered byte pointer with %s before downstream dispatch"},
    "SessionCommunications": {"commands": ["0x2fa3", "0x2fa4", "0x2fa5", "0x2fa8", "0x2faa"], "byte_fields": 6, "handling": "retains destination/address-book/call UUID pointer+length pairs; six recovered fields are logged with %s before downstream dispatch"},
}


class AuditError(ValueError):
    """An input or deterministic-output invariant failed."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_read(path: Path) -> bytes:
    flags = os.O_RDONLY | (getattr(os, "O_NOFOLLOW", 0))
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
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
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
    if phentsize != PROGRAM_HEADER.size or phnum > 1024 or phoff + phentsize * phnum > len(data):
        raise AuditError("invalid program-header geometry")
    segments: list[dict[str, int]] = []
    for index in range(phnum):
        p_type, p_flags, p_offset, p_vaddr, _p_paddr, p_filesz, p_memsz, p_align = PROGRAM_HEADER.unpack_from(data, phoff + index * phentsize)
        if p_type != PT_LOAD:
            continue
        if p_filesz > p_memsz or p_offset + p_filesz > len(data):
            raise AuditError("invalid PT_LOAD bounds")
        segments.append({"flags": p_flags, "offset": p_offset, "vaddr": p_vaddr, "filesz": p_filesz, "memsz": p_memsz, "align": p_align})
    if not segments:
        raise AuditError("ELF has no PT_LOAD segment")
    return segments


def va_to_offset(segments: list[dict[str, int]], va: int, size: int) -> int:
    if va < 0 or size < 0 or va + size < va:
        raise AuditError("invalid virtual-address range")
    for segment in segments:
        if segment["vaddr"] <= va and va + size <= segment["vaddr"] + segment["filesz"]:
            return segment["offset"] + va - segment["vaddr"]
    raise AuditError(f"virtual-address range is not file-backed: {va:#x}+{size:#x}")


def verify_subject(data: bytes, key: str) -> list[dict[str, int]]:
    expected = SUBJECTS[key]
    if len(data) != expected["size"]:
        raise AuditError(f"unexpected {key} size: {len(data)}")
    digest = sha256(data)
    if digest != expected["sha256"]:
        raise AuditError(f"unexpected {key} SHA-256: {digest}")
    return parse_load_segments(data)


def verify_ranges(data: bytes, segments: list[dict[str, int]], ranges: dict[str, tuple[int, int, str]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, (start, end, digest) in ranges.items():
        offset = va_to_offset(segments, start, end - start)
        actual = sha256(data[offset:offset + end - start])
        if actual != digest:
            raise AuditError(f"range hash mismatch: {name}")
        result[name] = {"elf_va_start": f"0x{start:x}", "elf_va_end_exclusive": f"0x{end:x}", "file_offset_start": f"0x{offset:x}", "size": end - start, "sha256": actual, "matched": True}
    return result


def verify_anchor(data: bytes, segments: list[dict[str, int]], va: int, expected_hex: str) -> dict[str, Any]:
    expected = bytes.fromhex(expected_hex)
    offset = va_to_offset(segments, va, len(expected))
    if data[offset:offset + len(expected)] != expected:
        raise AuditError(f"anchor mismatch at ELF VA {va:#x}")
    return {"elf_va": f"0x{va:x}", "file_offset": f"0x{offset:x}", "size": len(expected), "bytes_hex": expected_hex, "sha256": sha256(expected), "matched": True}


def build_report(framework: bytes, service: bytes) -> dict[str, Any]:
    framework_segments = verify_subject(framework, "framework")
    service_segments = verify_subject(service, "service")
    direct_calls: dict[str, Any] = {}
    total = 0
    for caller, addresses in DIRECT_CALLS.items():
        entries = []
        for va in addresses:
            entries.append(verify_anchor(service, service_segments, va, CALL_BYTES[va]))
        direct_calls[caller] = entries
        total += len(entries)
    if total != 31:
        raise AuditError("internal direct-call inventory must contain 31 entries")
    wrapper_calls: dict[str, Any] = {}
    wrapper_total = 0
    for caller, entries in WRAPPER_CALLS.items():
        wrapper_calls[caller] = [
            verify_anchor(service, service_segments, va, expected)
            for va, expected in entries
        ]
        wrapper_total += len(entries)
    if wrapper_total != 22:
        raise AuditError("internal wrapper-call inventory must contain 22 entries")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "tool": {"name": "iap2_marshal_getbytes_audit.py", "version": TOOL_VERSION},
        "subjects": {
            key: {**value, "format": "ELF64 little-endian ET_DYN x86-64"}
            for key, value in SUBJECTS.items()
        },
        "address_model": {
            "artifact_addresses": "ELF virtual addresses",
            "file_mapping": "resolved through file-backed PT_LOAD segments",
            "ghidra_image_base": "0x100000",
            "ghidra_normalization": "subtract 0x100000 from Ghidra addresses for these two artifacts",
        },
        "framework_ranges": verify_ranges(framework, framework_segments, FRAMEWORK_RANGES),
        "framework_anchors": {name: verify_anchor(framework, framework_segments, va, expected) for name, (va, expected) in FRAMEWORK_ANCHORS.items()},
        "service_caller_ranges": verify_ranges(service, service_segments, CALLER_RANGES),
        "direct_calls": direct_calls,
        "heap_string_wrapper_caller_ranges": verify_ranges(service, service_segments, WRAPPER_CALLER_RANGES),
        "heap_string_wrapper_calls": wrapper_calls,
        "coverage": {
            "direct_static_call_count": total,
            "direct_static_caller_count": len(DIRECT_CALLS),
            "heap_string_wrapper_call_count": wrapper_total,
            "heap_string_wrapper_caller_count": len(WRAPPER_CALLS),
            "recovered_symbol_string_carriers": ["libiAP2AppFramework-2.0.so", "iAP2Service-2.0"],
            "method": "exact imported-symbol and PLT-call inventory within the recovered extracted-safe corpus, followed by FDE-bounded caller review",
            "boundary": "does not exclude calls through previously captured function pointers, symbol-name-free wrappers, runtime-generated code, files outside extracted-safe, or alternate builds",
        },
        "decoded_helper": {
            "prototype": "void *iAp2MarshalGetBytes(Marshal *state, uint32_t *declared_length_out)",
            "flow": [
                "rejects null state or null length-output pointer by logging and returning null",
                "reads a uint32 declared length and stores it through the caller-provided output pointer",
                "rejects declared lengths above UINT32_MAX-3 before four-byte alignment",
                "rounds the declared length up to a four-byte-aligned consumption length",
                "compares aligned consumption length against the marshal state's remaining byte count",
                "on insufficiency sets remaining to zero, sets state flag bit 1, logs, and returns null",
                "on success returns the current transaction pointer, advances it by aligned consumption length, and subtracts that length from remaining",
            ],
            "copy_behavior": "the helper returns an interior transaction pointer; it performs no destination allocation and no fixed-size copy",
            "failure_detail": "the already stored declared length is not cleared when the bounded accessor later fails",
        },
        "caller_semantics": CALLER_SEMANTICS,
        "findings": {
            "generic_helper": {
                "classification": "bounded direct byte accessor",
                "conclusion": "the exact generic iAp2MarshalGetBytes body is not a fixed-stack-copy primitive and rejects aligned lengths larger than the remaining transaction",
            },
            "null_return_consumer": {
                "classification": "exact-static null-source denial-of-service candidate",
                "location": "heap_string_materializer 0x2957c..0x296a7; direct helper call at 0x295d5; 22 exact wrapper calls from SessionConnection and SessionIdentification",
                "commands": ["SessionConnection kCmdIdentificationSelect 0x2afb", "SessionIdentification kCmdIdentificationUpdate 0x2f95"],
                "mechanism": "a malformed declared byte length can be stored before the helper returns null; the consumer allocates declared_length+1 and, if allocation succeeds, calls strncpy with the null source and declared length without rejecting the null return",
                "impact_boundary": "a faulting libc read is a static candidate; live delivery, process termination, supervisor behavior, and user-visible impact are not demonstrated",
            },
            "percent_s_consumers": {
                "classification": "exact-static unbounded-string-read candidates",
                "locations": ["SessionAppLaunch command 0x2f45", "SessionPlayMediaLibrary command 0x2f84", "SessionCommunications commands 0x2fa3/0x2fa4/0x2fa5/0x2fa8/0x2faa"],
                "mechanism": "recovered length-delimited byte pointers are passed to %s logging without a local terminator check or precision bound in the reviewed caller ranges",
                "impact_boundary": "the exact extent depends on transaction allocation, padding, protocol conformance, and logger implementation; no live disclosure, crash, or cross-boundary log exposure is demonstrated",
            },
        },
        "assessment": {
            "demonstrated": [
                "exact recovered identities for the helper library and sole imported-symbol service carrier",
                "31 exact direct PLT calls across 11 reviewed service functions",
                "22 exact calls to the null-return-consuming heap-string wrapper from two identification-related command handlers",
                "bounded aligned remaining-length enforcement and absence of a copy in the generic helper",
                "one exact null-return consumer and multiple exact unbounded %s consumers",
            ],
            "not_demonstrated": [
                "physical phone-to-handler delivery, successful iAP2 admission/authentication, or session eligibility",
                "that the owner unit runs either exact recovered binary",
                "process crash, service restart behavior, information disclosure to an attacker, code execution, root access, SMACK escape, persistence, or firmware modification",
                "CVE identity or affected-versus-fixed SDK lineage",
                "complete indirect-call or alternate-build coverage",
            ],
        },
    }
    report["canonical_sha256"] = sha256(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii"))
    return report


def encode_report(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def exclusive_write(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
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
    parser.add_argument("framework", type=Path, help="recovered libiAP2AppFramework-2.0.so")
    parser.add_argument("service", type=Path, help="recovered iAP2Service-2.0")
    parser.add_argument("--output", type=Path, help="create report without overwriting an existing path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = build_report(stable_read(args.framework), stable_read(args.service))
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
