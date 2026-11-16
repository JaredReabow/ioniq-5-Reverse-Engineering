#!/usr/bin/env python3
"""Verify recovered AirPlay screen-parser output-bound arithmetic offline."""

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

SCHEMA = "ioniq-airplay-screen-parser-bounds-audit/v1"
TOOL_VERSION = "1.1.0"
MAX_FILE_BYTES = 64 * 1024 * 1024
ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PROGRAM_HEADER = struct.Struct("<IIQQQQQQ")
PT_LOAD = 1

SUBJECTS = {
    "airplay": {
        "basename": "libAirPlay.so",
        "size": 215_896,
        "sha256": "ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0",
    },
    "media": {
        "basename": "libCarPlayMediaFramework.so",
        "size": 162_392,
        "sha256": "69690210d1aa4dec33c77b0e80f1d3368f8a70bcb507c1b158b6245dc29eb2f3",
    },
    "coreutils": {
        "basename": "libCoreUtils.so",
        "size": 1_200_368,
        "sha256": "9104e2c16ee27e647fac090ee7f3aa4cc686b8caaea1dc24763af2950c0ebfae",
    },
}

RANGES = {
    "screen_socket_process_frames": (
        "airplay", 0x1F250, 0x1FA93,
        "51016b6ba869ea0cda6a2940196ced53b1b9957735f3a114935d06d976d1c0b1",
    ),
    "screen_header_and_body_read": (
        "airplay", 0x1F4B9, 0x1F54A,
        "5182656ae5329d23d9be03d818905479b578966e9d858efa34e6a973a195e1ef",
    ),
    "screen_frame_and_config_dispatch": (
        "airplay", 0x1F54A, 0x1F7D5,
        "fe0f41bc965071aac29d648e87b9862f9c17f859628803769204865aebca4b98",
    ),
    "screen_stream_initialize": (
        "media", 0x11D34, 0x11FDD,
        "f922e85799a0795d2fd9df80a595d98fe79923023f798853b2ae08bd4e257a3b",
    ),
    "zeroed_context_allocation": (
        "media", 0x11DC2, 0x11EE5,
        "b766b2197791ab3b2b710e3ac01b9f23cac0a7a16f9bf71e4f06bc3c539682ca",
    ),
    "screen_stream_set_avcc": (
        "media", 0x1227B, 0x124C1,
        "60c4af44c4c3634702ba8b20ad1297e2e50d26302ccb4a352149adece798d439",
    ),
    "screen_stream_start": (
        "media", 0x124C1, 0x126FC,
        "a05f3a63efd7c708ed916d871d098acf69a42bc916b5ce95bc5b729bf2902516",
    ),
    "screen_stream_process_data": (
        "media", 0x133F2, 0x13F06,
        "f80e0c035321845e4c5e8e0c7d50e8d973e1059725887e509429262cec63af47",
    ),
    "double_size_capacity_allocation": (
        "media", 0x13618, 0x13732,
        "390a45d45346addd1cdf013f6c59ac958e66660537ba5bc3aeb6aeaa85c8d2c6",
    ),
    "first_frame_config_prepend": (
        "media", 0x13760, 0x137DC,
        "f439933453da8206f9c0f6d40d89cb1a239f03e42d425037dcb15c18258a1aad",
    ),
    "nal_conversion_loop": (
        "media", 0x13825, 0x13ACC,
        "5b983dc3aa1572d143e811607e23d1c8f100e9214240bed3a66bc56e66428ace",
    ),
    "declared_nal_length_to_synthetic_end": (
        "media", 0x139AD, 0x13A31,
        "bdf5cafe0174be2190b610f472ed7db04435ba2eb7a17026c03abb48eef0815b",
    ),
    "h264_avcc_to_annex_b_header": (
        "coreutils", 0x81F2E, 0x821F4,
        "6ff7467bc1689bb04859aedc693b75f96e96627cb25d497d606c1c2134d53885",
    ),
    "h264_get_next_nal_unit": (
        "coreutils", 0x821F4, 0x82295,
        "4f93ad628a9cfbaf35c18a3e6cc5eca8c3ac67d82c93e56a1bf85607bac93c82",
    ),
}

ANCHORS = {
    "socket_header_read_128_bytes": (
        "airplay", 0x1F4B9,
        "518b442418be800000004c89e74c8d7b484531c94531c04c89f9ba800000005041ff542418",
    ),
    "uint32_body_size_and_malloc": (
        "airplay", 0x1F4F6,
        "448b73484d85f674494c89f7e8f993feff4989c2",
    ),
    "video_frame_process_data_call": (
        "airplay", 0x1F72D,
        "41568b53484531c94531c0488bbb280300004c89e96a004889eee8549bfeff89",
    ),
    "video_config_set_avcc_call": (
        "airplay", 0x1F792,
        "3c0175548a434ef3480f2c535cf3480f2c7358488bbb28030000d0e883e001884328e8378dfeff8b534885d27470488bbb280300004889eee80192feff89",
    ),
    "calloc_zeroed_context": (
        "media", 0x11DC2,
        "bec8000000bf01000000e8bf4fffff488945f048",
    ),
    "start_sets_first_frame_flag": (
        "media", 0x12598, "c6809800000001",
    ),
    "set_avcc_retains_header_length_and_prefix_width": (
        "media", 0x1247B,
        "488b45e8488b55f048899080000000488b55d8488b45e848899088000000488b55e0488b45e848899090000000",
    ),
    "double_body_size_capacity": (
        "media", 0x13618,
        "488b8598feffff488d1400488b85f8feffff488b80a80000004839c20f86f8000000488b8598feffff4801c0",
    ),
    "store_exact_double_capacity": (
        "media", 0x1371D,
        "488b85f8feffff488b9510ffffff488990a8000000",
    ),
    "unchecked_first_frame_config_copy": (
        "media", 0x13760,
        "488b85f8feffff0fb680980000003c010f85af000000488b85f8feffff488b9088000000488b85f8feffff488b8880000000488b85e0feffff4889ce4889c7e8dc36ffff",
    ),
    "prefix_width_1_2_4_selection": (
        "media", 0x13835,
        "488b85f8feffff488b80900000004883f8017519488b85e8feffff0fb6000fb6c0488985d8feffffe94b010000488b85f8feffff488b80900000004883f8027534488b85e8feffff0fb6000fb6c0c1e00889c2488b85e8feffff4883c0010fb6000fb6c009d00fb7c0488985d8feffffe903010000488b85f8feffff488b80900000004883f804755f",
    ),
    "declared_length_forms_helper_end": (
        "media", 0x139AD,
        "488b85f8feffff488b9090000000488b85d8feffff4801d048898508ffffff488b85e8feffff488985c0feffff488b95c0feffff488b8508ffffff4801d048898518ffffff488b85f8feffff488b9090000000488b85c0feffff4c8d85c0feffff488dbdd0feffff488d8dc8feffff488bb518ffffff4d89c14989f84889c7",
    ),
    "helper_receives_synthetic_end": (
        "media", 0x139F2,
        "488b85f8feffff488b9090000000488b85c0feffff4c8d85c0feffff488dbdd0feffff488d8dc8feffff488bb518ffffff4d89c14989f84889c7e86f36ffff",
    ),
    "four_byte_start_code_and_nal_copy": (
        "media", 0x13A3A,
        "8b5590488b85e0feffff8910488b95d0feffff488b85c8feffff488b8de0feffff4883c1044889c64889cfe81634ffff488b85d0feffff4883c004480185e0feffff488b95d0feffff488b85f0feffff4801d04883c004488985f0feffffe955",
    ),
    "loop_uses_input_consumption_bound": (
        "media", 0x13A9D,
        "488b8508ffffff480185e8feffff488b95e8feffff488b85a0feffff4829c24889d0483b8598feffff0f8259fdffff",
    ),
    "one_byte_prefix_zero_length_decode": (
        "coreutils", 0x8222E,
        "48ffcab8cfe5ffff75434c8d57010fb617eb1f0fb6",
    ),
    "zero_length_accepted_and_input_advanced": (
        "coreutils", 0x82260,
        "4c29d6b8a2e5ffff4839f2770e4c891131c04989104c01d2498911",
    ),
}

PUBLIC_COMPARATOR = {
    "repository": "45clouds/WirelessCarPlay",
    "commit": "51145ef55f8dd9f1cbadd58353cacb5e0ca215e9",
    "screen_source": "source/Sources/AirPlayReceiverSessionScreen.c",
    "screen_source_sha256": "c5fc6bca8a6758caaea59394859d5d857e6f9683d079ae3741a35da6f8999bc7",
    "common_header": "source/Sources/AirPlayCommon.h",
    "common_header_sha256": "6774bd04f8889d991caacea613b1873d1ac08e0014f371d8b1c1a42ba86df17d",
    "role": "comparative protocol and semantic names only; recovered bytes and addresses are authoritative",
}


class AuditError(ValueError):
    """An input, arithmetic, or deterministic-output invariant failed."""


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
        segments.append({
            "flags": p_flags,
            "offset": p_offset,
            "vaddr": p_vaddr,
            "filesz": p_filesz,
            "memsz": p_memsz,
            "align": p_align,
        })
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


def conversion_geometry(
    body_size: int,
    prefix_size: int,
    nal_lengths: list[int] | tuple[int, ...],
    *,
    config_size: int = 0,
    capacity: int | None = None,
) -> dict[str, int | bool]:
    """Model lengths only; this does not construct or parse protocol input."""
    values = (body_size, prefix_size, config_size)
    if any(not isinstance(value, int) or isinstance(value, bool) for value in values):
        raise AuditError("geometry values must be integers")
    if body_size <= 0 or prefix_size not in (1, 2, 4) or config_size < 0:
        raise AuditError("invalid screen conversion geometry")
    lengths = list(nal_lengths)
    if not lengths or any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in lengths):
        raise AuditError("NAL lengths must be a non-empty sequence of non-negative integers")
    consumed = prefix_size * len(lengths) + sum(lengths)
    if consumed != body_size:
        raise AuditError("NAL geometry does not consume the complete body")
    if capacity is None:
        capacity = 2 * body_size
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0:
        raise AuditError("capacity must be a non-negative integer")
    produced = config_size + 4 * len(lengths) + sum(lengths)
    return {
        "body_size": body_size,
        "prefix_size": prefix_size,
        "nal_count": len(lengths),
        "nal_payload_bytes": sum(lengths),
        "config_size": config_size,
        "input_consumed": consumed,
        "output_produced": produced,
        "capacity": capacity,
        "out_of_bounds": produced > capacity,
        "excess_bytes": max(0, produced - capacity),
    }


def declared_extent_geometry(
    body_size: int,
    consumed_before: int,
    prefix_size: int,
    declared_length: int,
) -> dict[str, int | bool]:
    """Model the caller's declared extent versus the true body; no bytes are made."""
    values = (body_size, consumed_before, prefix_size, declared_length)
    if any(not isinstance(value, int) or isinstance(value, bool) for value in values):
        raise AuditError("declared-extent geometry values must be integers")
    if (
        body_size <= 0
        or consumed_before < 0
        or consumed_before >= body_size
        or prefix_size not in (1, 2, 4)
        or declared_length < 0
    ):
        raise AuditError("invalid declared-extent geometry")
    remaining = body_size - consumed_before
    prefix_out_of_bounds = prefix_size > remaining
    declared_extent = prefix_size + declared_length
    body_out_of_bounds = declared_extent > remaining
    return {
        "body_size": body_size,
        "consumed_before": consumed_before,
        "true_remaining": remaining,
        "prefix_size": prefix_size,
        "declared_length": declared_length,
        "synthetic_extent": declared_extent,
        "prefix_out_of_bounds": prefix_out_of_bounds,
        "body_out_of_bounds": body_out_of_bounds,
        "excess_input_bytes": max(0, declared_extent - remaining),
    }


def _verify_subject(name: str, data: bytes) -> tuple[dict[str, Any], list[dict[str, int]]]:
    expected = SUBJECTS[name]
    if len(data) != expected["size"]:
        raise AuditError(f"unexpected {name} input size: {len(data)}")
    digest = sha256(data)
    if digest != expected["sha256"]:
        raise AuditError(f"unexpected {name} input SHA-256: {digest}")
    segments = parse_load_segments(data)
    return ({
        "basename": expected["basename"],
        "size": len(data),
        "sha256": digest,
        "format": "ELF64 little-endian ET_DYN x86-64",
    }, segments)


def _verify_slice(
    data: bytes,
    segments: list[dict[str, int]],
    subject: str,
    va: int,
    expected: bytes,
) -> dict[str, Any]:
    offset = va_to_offset(segments, va, len(expected))
    actual = data[offset : offset + len(expected)]
    if actual != expected:
        raise AuditError(f"anchor mismatch in {subject} at ELF VA {va:#x}")
    return {
        "subject": SUBJECTS[subject]["basename"],
        "elf_va": f"0x{va:x}",
        "file_offset": f"0x{offset:x}",
        "size": len(expected),
        "bytes_hex": expected.hex(),
        "sha256": sha256(expected),
        "matched": True,
    }


def build_report(airplay: bytes, media: bytes, coreutils: bytes) -> dict[str, Any]:
    blobs = {"airplay": airplay, "media": media, "coreutils": coreutils}
    subjects: dict[str, Any] = {}
    mappings: dict[str, list[dict[str, int]]] = {}
    for name in ("airplay", "media", "coreutils"):
        subjects[name], mappings[name] = _verify_subject(name, blobs[name])

    ranges: dict[str, Any] = {}
    for name, (subject, start, end, expected_digest) in RANGES.items():
        offset = va_to_offset(mappings[subject], start, end - start)
        actual_digest = sha256(blobs[subject][offset : offset + end - start])
        if actual_digest != expected_digest:
            raise AuditError(f"range hash mismatch: {name}")
        ranges[name] = {
            "subject": SUBJECTS[subject]["basename"],
            "elf_va_start": f"0x{start:x}",
            "elf_va_end_exclusive": f"0x{end:x}",
            "file_offset_start": f"0x{offset:x}",
            "size": end - start,
            "sha256": actual_digest,
            "matched": True,
        }

    anchors = {
        name: _verify_slice(blobs[subject], mappings[subject], subject, va, bytes.fromhex(expected_hex))
        for name, (subject, va, expected_hex) in ANCHORS.items()
    }

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "tool": {"name": "airplay_screen_parser_bounds_audit.py", "version": TOOL_VERSION},
        "subjects": subjects,
        "address_model": {
            "artifact_addresses": "ELF virtual addresses",
            "file_mapping": "resolved independently through each file-backed PT_LOAD segment",
            "ghidra_image_base": "0x100000",
            "ghidra_normalization": "subtract 0x100000 from Ghidra addresses used by the reviewed REA dossiers",
        },
        "ranges": ranges,
        "anchors": anchors,
        "decoded_flow": {
            "socket_to_parser": {
                "header": "0x1f4b9 requests exactly 0x80 bytes into the retained AirPlayScreenHeader at session+0x48",
                "body_size": "0x1f4f6 loads the uint32 field at session+0x48 and 0x1f502 allocates that many body bytes",
                "video_frame": "opcode 0 reaches ScreenStreamProcessData@plt at 0x1f747 with the body pointer and uint32 body size",
                "video_config": "opcode 1 reaches ScreenStreamSetAVCC@plt at 0x1f7ca when body size is nonzero",
                "boundary": "the read is from the already-established screen NetSocket; listener creation, pairing, authentication, encryption state, and live peer control are not established here",
            },
            "retained_state": {
                "initialization": "ScreenStreamInitialize calls calloc(1,0xc8), so output pointer, capacity, retained AVCC state, and first-frame state begin zeroed",
                "configuration": "ScreenStreamSetAVCC converts bounded AVCC configuration and stores the Annex-B header pointer at context+0x80, header length H at +0x88, and length-prefix width p at +0x90",
                "start": "ScreenStreamStart stores 1 at context+0x98, selecting the one-time retained-header prepend on the next processed frame",
            },
            "output_capacity": {
                "body_symbol": "S",
                "growth_test": "0x1361f computes 2*S and compares it with retained capacity at context+0xa8",
                "growth_allocation": "when growth is required, 0x13641 computes 2*S, operator new[] receives that value at 0x136a3, and 0x1372b stores the same value as capacity",
                "upstream_width": "the exact socket route supplies a uint32 body size zero-extended into the x86-64 size_t argument",
                "no_route_local_doubling_wrap": "for S <= 0xffffffff, 2*S <= 0x1fffffffe, so the 64-bit doubling does not wrap on this route",
            },
            "writes_without_output_bound": {
                "config_prepend": "when context+0x98 is 1, 0x13776..0x1379f copies H retained bytes to the output and advances output-used by H without comparing H with capacity",
                "declared_extent": "0x13849..0x13911 reads the next p-byte declared NAL length before checking true remaining bytes; 0x139c2 computes p+length and 0x139eb forms a synthetic end pointer from that declared extent",
                "helper_boundary_mismatch": "0x13a2c passes the synthetic end to H264GetNextNALUnit rather than the true body end; the helper can therefore validate a declared body against caller-invented bounds that extend past the socket allocation",
                "nal_conversion": "for each helper-accepted NAL, 0x13a3a stores a 4-byte Annex-B start code and 0x13a65 copies the declared NAL body, then advances output-used by 4+length",
                "late_loop_bound": "only after the copy, 0x13a9d..0x13ac6 compares cumulative declared input consumption with S; it neither prevents an out-of-input read/copy nor compares output-used with context+0xa8",
                "bounded_helper_scope": "H264GetNextNALUnit restricts p to 1, 2, or 4 and bounds each NAL against the end pointer it is given, but that end is synthetic here; it also accepts length zero and returns an input pointer advanced by p",
            },
        },
        "arithmetic_proof": {
            "symbols": {
                "S": "input body bytes",
                "p": "AVCC length-prefix width in {1,2,4}",
                "N": "number of accepted NAL units",
                "L": "sum of NAL payload lengths",
                "H": "retained Annex-B configuration-header bytes prepended on the first-frame branch",
                "C": "output capacity after the exact growth branch",
            },
            "input_identity": "S = p*N + L",
            "output_identity": "O = H + 4*N + L = H + S + (4-p)*N",
            "growth_capacity": "C = 2*S",
            "out_of_bounds_condition": "O > C, equivalently H + (4-p)*N > S",
            "accepted_zero_length_case": "H264GetNextNALUnit accepts zero-length units; with p=1 and N=S, O=H+4*S while C=2*S, so O>C for every S>0",
            "first_frame_header_case": "independently, the unchecked initial memcpy crosses C whenever H>C before NAL conversion begins",
            "declared_extent_failure": "before calling the helper, the caller does not require p+declared_length <= true_remaining; it uses p+declared_length to invent the helper end, so a declared extent past the socket body can be accepted and copied before the late cumulative-consumption comparison",
            "partial_prefix_failure": "because the outer loop continues while at least one byte remains, p=2 or p=4 can read a truncated final prefix beyond the true body before any helper check",
            "important_correction": "this exact socket path does not establish a size-doubling integer wrap on x86-64; the demonstrated defects are true-input-bound and output-capacity accounting failures",
        },
        "assessment": {
            "classification": "exact-static heap out-of-bounds read/write candidate",
            "cwe": ["CWE-125", "CWE-787"],
            "demonstrated": [
                "exact recovered bytes bind socket body reads and opcode dispatch to the media callbacks",
                "exact recovered bytes bind zeroed initial context, retained AVCC state, and the first-frame flag",
                "exact recovered bytes bind output allocation to 2*S on the growth path",
                "exact recovered bytes bind declared-length and prefix reads that are not checked against true remaining body bytes",
                "the caller gives the bounded helper a synthetic end derived from the unchecked declared length, then copies the accepted declared body",
                "exact recovered bytes bind an unchecked retained-header memcpy and unchecked per-NAL output writes",
                "the exact NAL helper accepts zero length and advances by the configured prefix width",
                "the length identities admit accepted parser geometry whose output exceeds the recorded capacity",
            ],
            "prerequisites": [
                "the three exact recovered library identities",
                "an established screen-stream NetSocket and successful ScreenStream initialization/start",
                "accepted video configuration retaining a supported prefix width",
                "a subsequent video-frame body with a declared NAL extent beyond true remaining input, accepted NAL geometry making H+(4-p)*N exceed S, or first-frame retained H exceeding capacity",
                "the growth/reuse state must leave actual output allocation smaller than produced output; the fresh calloc-zeroed context reaches the exact 2*S growth case",
            ],
            "not_demonstrated": [
                "a physical phone, USB/NCM peer, or network peer can deliver the required sequence to the exact installed unit",
                "listener/interface exposure, session establishment, pairing, authentication, authorization, or encryption prerequisites",
                "an observed allocator overwrite, crash, process termination, supervisor behavior, or user-visible denial of service",
                "reliable control-flow influence, code execution, authentication bypass, root access, SMACK escape, persistence, or firmware modification",
                "CVE-2025-30422 identity, any other CVE identity, affected-versus-fixed lineage, or impact on the owner's installed firmware",
            ],
            "cve_attribution": None,
            "cve_2025_30422_boundary": "Apple describes a fixed AirPlay SDK buffer overflow and Oligo classifies that CVE as potential integer-overflow RCE, but neither reviewed source names this function or supplies fixed bytes. This exact socket path has no 64-bit 2*S wrap, so broad class overlap is not attribution.",
        },
        "public_comparator": PUBLIC_COMPARATOR,
        "safety": {
            "execution": "no recovered executable, service, parser, or shared-library entry point was executed",
            "protocol_input": "no screen header, AVCC configuration, frame body, packet, or malformed media input was created or transmitted",
            "scope": "host-side byte hashing, ELF mapping, disassembly review, and abstract length arithmetic only",
        },
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
    parser.add_argument("airplay", type=Path, help="recovered libAirPlay.so")
    parser.add_argument("media", type=Path, help="recovered libCarPlayMediaFramework.so")
    parser.add_argument("coreutils", type=Path, help="recovered libCoreUtils.so")
    parser.add_argument("--output", type=Path, help="create report without overwriting an existing path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = build_report(
            stable_read(args.airplay),
            stable_read(args.media),
            stable_read(args.coreutils),
        )
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
