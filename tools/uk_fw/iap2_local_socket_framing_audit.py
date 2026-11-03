#!/usr/bin/env python3
"""Verify recovered iAP2 local-socket framing, producer, and SMACK boundaries offline."""

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

SCHEMA = "ioniq-iap2-local-socket-framing-audit/v1"
TOOL_VERSION = "1.1.0"
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

CONFIG_SUBJECTS = {
    "unit": {
        "basename": "carplay_iAP2.service",
        "size": 397,
        "sha256": "f7cf915509005a4aaa18d09e3a6ccd0abdd72ef2b2816641ea9a592a1e3f4495",
    },
    "relabel": {
        "basename": "smack-relabel-ro.sh",
        "size": 6_206,
        "sha256": "8275625764c30b6e82d99e5fdf887038261f97e9f0ef5a36da8faa743a35a15f",
    },
    "projection_policy": {
        "basename": "projection",
        "size": 831,
        "sha256": "978ccab43e6724df0bb74c4f84e3319ab3f0022dec442f4389fba140f6b3c1c9",
    },
}

SERVICE_RANGES = {
    "SendEventToApp": (0x2BE82, 0x2CA54, "dba272cd56cc9f69af071534cf39080cee0375d6960e6917e628b74eb22df5b1"),
    "sendData": (0x2CA54, 0x2CBF6, "6fa21a30d759689415b8737a1168915f0360ba0c5fbd8b0c0c1f5a901fcc486e"),
    "serverThread": (0x2D64A, 0x2E542, "ac7a8fb5b186f87cc168c494cf37a823b55c76c0b82dce87863fdc1fc360b9c2"),
    "listenClient": (0x2E542, 0x2E89D, "dc480c7bf3a9851a020d13787dd43878dd6d598bdba58b92ca4587e64f837427"),
    "handleClientCmd": (0x2EA28, 0x2F1AD, "b49918f988a4060fbd76847f0e1f6000999a7ae676267ff99d7e37709d18c9e3"),
}

FRAMEWORK_RANGES = {
    "iAp2ConnectionConnectToService": (0x1EE57, 0x1F15D, "df52f3ef3ed8e5ddc5e8a9a462e50d09b94bf639706033276fe50fcc0444f216"),
    "iAp2EventHandleThread": (0x1FCF4, 0x2052F, "be80016f73eebb826c0239d2ff6e2750ab3e33424c2d264e8ddae9c18936d998"),
    "iAp2MarshalInit": (0x2100D, 0x210FF, "6ee6b7cf272006bb7987d92bb0bdb56e157cadb031512f0dc4527b528cf96e77"),
    "iAp2MarshalInitFromTxn": (0x210FF, 0x21175, "4e7fbd707234bf553adf0c59de1501865d873ebeae4ee058f59139124dbf5729"),
    "iAp2MarshalAlloc": (0x21175, 0x2129D, "ed1c5e939eee08fccb99eb673f74747c6201c390ae878651ff18b72cb94bc2e7"),
    "iAp2MarshalPutUint32": (0x21359, 0x213B3, "459ed98a9a68a8aa8dde1abfa84222e0baa8a8b312c92559a043858d0b21904f"),
    "iAp2MarshalPutBytes": (0x21583, 0x21645, "1e002cee0cb9c0e073017c7ccdc2a8dfe4da61e413181227ec92fedeac2fa2ff"),
    "iAp2MarshalGetUsedSize": (0x21B21, 0x21CA0, "aa7ecb6f0be22bd24ec8d32b90a9a7e22b34475a0d42c587507563c3efa82b4f"),
}

SERVICE_ANCHORS = {
    "server_umask_zero": (0x2E5A2, "bf00000000e8a46cfdff"),
    "server_af_unix_stream_socket": (0x2E5E7, "ba00000000be01000000bf01000000e88561fdff89c2488b8558ffffff"),
    "server_path_bind_and_umask_restore": (0x2E6DA, "66c78570ffffff0100488d8570ffffff4883c002ba6c000000488d35f3dc04004889c7e8ce62fdffc78564ffffff6e0000008b9564ffffff488b8558ffffff8b4008488d8d70ffffff4889ce89c7e80360fdff89856cffffff8b8568ffffff89c7e8106bfdff"),
    "server_accept_without_preceding_peer_credential_gate": (0x2E290, "b86e0000008985c8fdffff488b85b8fdffff8b4008488d95c8fdffff488d8d70feffff4889ce89c7e83365fdff8985ccfdffff"),
    "server_header_recv_msg_waitall": (0x2DADD, "488db530feffff8b85d0fdffffb900010000ba4000000089c7e8056dfdff8985e4fdffff"),
    "server_malloc_declared_total": (0x2DCD8, "8b8568feffff89c04889c7e82872fdff48898508feffff"),
    "server_fixed_64_byte_header_copy": (0x2DD2C, "488b8508feffff488b9530feffff488910488b9538feffff48895008488b9540feffff48895010488b9548feffff48895018488b9550feffff48895020488b9558feffff48895028488b9560feffff48895030488b9568feffff48895038"),
    "server_post_copy_lower_bound_check": (0x2DD8A, "8b8568feffff89c04883f8400f86df010000"),
    "server_body_recv_positive_only_check": (0x2DD9C, "8b8568feffff89c0488d50c0488b8508feffff488d70408b85d0fdffffb90001000089c7e83b6afdff8985e4fdffff83bde4fdffff000f8f0f010000"),
    "server_dispatch_after_positive_body": (0x2DEE7, "8b9530feffff488b8d08feffff8bb5d0fdffff488b85b8fdffffffb560feffffffb558feffffffb550feffffffb548feffffffb540feffffffb538feffff4889c7e8fb0a00004883c4308985e0fdffff"),
    "server_dispatch_for_declared_total_at_most_64": (0x2DF7B, "8b9530feffff488b8d08feffff8bb5d0fdffff488b85b8fdffffffb560feffffffb558feffffffb550feffffffb548feffffffb540feffffffb538feffff4889c7e8670a00004883c430"),
    "server_socket_path": (0x7C3ED, "2f746d702f69417032536f636b657400"),
}

FRAMEWORK_ANCHORS = {
    "client_af_unix_stream_socket": (0x1EEE1, "ba00000000be01000000bf01000000e88b61feff89c2488b8558feffff895020"),
    "client_path_and_connect": (0x1EFC8, "66c78570feffff0100488d8570feffff4883c002ba6c000000488d35d8b300004889c7e8f061feffc78568feffff6e000000c78564feffffc80000008b9568feffff488d8570feffff4889c1488b8558feffff8b40204889ce89c7e84863feff89856cfeffff"),
    "client_header_recv_msg_waitall": (0x1FFDA, "488b8580feffff8b4020488db5a0feffffb900010000ba4000000089c7e8d450feff89856cfeffff"),
    "client_malloc_declared_total": (0x2017A, "8b85d8feffff89c04889c7e8d654feff48898588feffff"),
    "client_fixed_64_byte_header_copy": (0x201CE, "488b8588feffff488b95a0feffff488910488b95a8feffff48895008488b95b0feffff48895010488b95b8feffff48895018488b95c0feffff48895020488b95c8feffff48895028488b95d0feffff48895030488b95d8feffff48895038"),
    "client_post_copy_lower_bound_check": (0x2022C, "8b85d8feffff83f8400f86fb010000"),
    "client_body_recv": (0x2023B, "8b85d8feffff89c0488d50c0488b8588feffff488d7040488b8580feffff8b4020b90001000089c7e8684efeff89856cfeffff"),
    "client_dispatch_after_positive_body": (0x203B9, "8b95dcfeffff8b8da0feffff488bb588feffff488b8580feffffff7028ff7020ff7018ff7010ff7008ff3089cfe8440100004883c430"),
    "client_socket_path": (0x2A3C0, "2f746d702f69417032536f636b657400"),
    "marshal_init_from_txn_overstates_remaining": (0x21126, "488b45f0488d5040488b45e848895010488b45e8488b5010488b45e8488910488b45f08b5038488b45e889500c488b45e8c7401801000000"),
    "marshal_init_rejects_offset_gt_capacity": (0x21038, "483b45d8765e"),
    "marshal_alloc_loads_remaining": (0x211E5, "8b400c89c0"),
    "marshal_alloc_compares_remaining_vs_aligned": (0x211EA, "483b45d07355"),
    "marshal_alloc_failure_sets_flag_bit2": (0x211F7, "83c802"),
    "marshal_putbytes_calls_putuint32_then_alloc": (0x215E3, "e8c83afeff"),
    "marshal_putbytes_alloc_failure_skips_memcpy": (0x215FE, "48837df000742a"),
    "marshal_getusedsize_validates_bounds": (0x21B87, "4839c2732e"),
}

# (iAp2MarshalInit call, iAp2MarshalGetUsedSize call, total-length store, SendEventToApp call)
PRODUCER_ANCHORS = [
    (0x17A20, 0x17A2C, 0x17A45, 0x17A82), (0x29032, 0x2903E, 0x29057, 0x29094),
    (0x2B221, 0x2B397, 0x2B3B0, 0x2B3ED), (0x346BD, 0x3475F, 0x34778, 0x347B5),
    (0x36298, 0x36392, 0x363AB, 0x363E8), (0x36563, 0x36580, 0x36599, 0x365D6),
    (0x37645, 0x376D6, 0x376EF, 0x3772C), (0x378FD, 0x3794A, 0x37963, 0x379E5),
    (0x37BAC, 0x37C00, 0x37C19, 0x37C56), (0x37E27, 0x37E74, 0x37E8D, 0x37ECA),
    (0x3B527, 0x3B547, 0x3B560, 0x3B5CF), (0x3B75F, 0x3B794, 0x3B7AD, 0x3B82E),
    (0x3B9E0, 0x3BA00, 0x3BA19, 0x3BA88), (0x3BC3A, 0x3BC5A, 0x3BC73, 0x3BCE2),
    (0x3BE94, 0x3BEB4, 0x3BECD, 0x3BF3C), (0x3C0FB, 0x3C188, 0x3C1A1, 0x3C223),
    (0x3D883, 0x3DAFE, 0x3DB17, 0x3DB54), (0x3F078, 0x3F132, 0x3F14B, 0x3F1CD),
    (0x3F347, 0x3F364, 0x3F37D, 0x3F3FF), (0x40068, 0x4008C, 0x400A5, 0x400E2),
    (0x41529, 0x41566, 0x4157F, 0x415BC), (0x4178F, 0x417B3, 0x417CC, 0x41809),
    (0x41A25, 0x41A47, 0x41A60, 0x41A9D), (0x42956, 0x42993, 0x429AC, 0x429E9),
    (0x4419D, 0x44241, 0x4425A, 0x44297), (0x44D92, 0x45166, 0x4517F, 0x45204),
    (0x49876, 0x4989A, 0x498B3, 0x498F0), (0x4A9B4, 0x4AA78, 0x4AA91, 0x4AACE),
    (0x4AC7D, 0x4AF3D, 0x4AF56, 0x4AF93), (0x4E05C, 0x4E102, 0x4E11B, 0x4E158),
    (0x4E2D6, 0x4E2E2, 0x4E2FB, 0x4E338), (0x53663, 0x53849, 0x53862, 0x5389F),
    (0x547EE, 0x5486A, 0x54883, 0x548C0), (0x54BDE, 0x54C96, 0x54CAF, 0x54CEC),
    (0x58CE5, 0x58F3D, 0x58F56, 0x58F93), (0x5916D, 0x59592, 0x595AB, 0x595E8),
    (0x597A4, 0x59992, 0x599AB, 0x599E8),
]

COMMAND_DISPATCH_CALLS = {
    "SessionConnection": [(0x2ED07, 0x38010), (0x2ED40, 0x38010)],
    "SessionLocation": [(0x2EDD9, 0x3E0DE)],
    "SessionMediaLibraryUpdates": [(0x2EE3F, 0x47428)],
    "SessionPlayMediaLibrary": [(0x2EE72, 0x4EDE6)],
    "SessionHID": [(0x2EEA5, 0x42CFC)],
    "SessionBTConnection": [(0x2EF0B, 0x3C368)],
    "SessionAppLaunch": [(0x2EF3E, 0x3F544)],
    "SessionVoiceOver": [(0x2EFD7, 0x4B0D8)],
    "SessionWiFiInformation": [(0x2F00A, 0x4E47E)],
    "SessionExternalAccessoryProtocol": [(0x2F03D, 0x41BE2)],
    "SessionIdentification": [(0x2F070, 0x556E2)],
    "SessionCommunications": [(0x2F0A3, 0x59F24)],
}

DYNAMIC_PRODUCER_RANGES = {
    "DeviceInformation": (0x37502, 0x377B9, "93a82004543b9adcabfab2c788e415a303f6f6e04f17964058fbae56fc1a3563", "(length + 0x50) * 4"),
    "DeviceLanguage": (0x377BA, 0x37A72, "adb2996111c97be167afbe3077b15f84797ecbddf169bde357bca56083ed82dc", "(length + 0x50) * 4"),
    "DeviceUUID": (0x37CE4, 0x37F57, "95cc3933d3cb70cd09147f29bedb03e068311690d64249c25990b48d1e5e585d", "(length + 0x50) * 4"),
    "ExternalAccessoryProtocolRecvData": (0x41896, 0x41B2A, "7050e8d8477e06e184742d46ed970c0ce680e7fae9ec2ca2314176395d58d890", "length + 0x58"),
    "WiFiInformation": (0x4DF10, 0x4E1E5, "04c674297ecd67c594ac0e98bbdce3d4287c1fd29b8faec12ed2aec09834c652", "(length_a + length_b + 0x68) * 4"),
    "FileTransferCallUUID": (0x546BC, 0x5494B, "94698ef418f21cc67dfcdc045f6727205aaa690399e5b37a3c3537597d1291e1", "(length + 0x58) * 4"),
    "FileTransferPlaylist": (0x54AAC, 0x54D42, "15945e042194db70c4435f67853885c56397f26d636269964504686e9e7a19ef", "(length + 0x68) * 4"),
    "CallStateUpdateStrings": (0x58B7E, 0x59020, "a5263a731ee7bea52645ff2c83647552b0c8d750804df9be271f133c9aebb1af", "(five lengths + 0xc0) * 4"),
    "CallStateUpdateAddress": (0x59020, 0x59675, "62954b46436402e11b938967b8de5187cfcad49c8a8c67ab4b518d093035eaaf", "(length + 0x6230) * 4"),
}

EXPECTED_BILATERAL_LABELS = [
    "App::bluetooth", "App::camera", "App::dlt", "App::engineermode", "App::euradio",
    "App::home", "App::locationmanager", "App::manager", "App::mediaplayer",
    "App::micommanager", "App::mpautotest", "App::navi", "App::setup",
    "App::standbyclock", "App::tms", "App::upgrade", "App::userprofilemanager",
    "App::vh", "_",
]


class AuditError(ValueError):
    """An input or deterministic-output invariant failed."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_read(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
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
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
        if identity(before) != identity(after):
            raise AuditError(f"file identity changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def stable_read_directory(path: Path) -> dict[str, bytes]:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISDIR(before.st_mode):
            raise AuditError(f"not a directory: {path}")
        names = sorted(os.listdir(descriptor))
        if len(names) > 1024:
            raise AuditError("policy directory contains too many entries")
        result: dict[str, bytes] = {}
        for name in names:
            if not name or name in {".", ".."} or "/" in name or "\x00" in name:
                raise AuditError("invalid policy filename")
            child_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            child = os.open(name, child_flags, dir_fd=descriptor)
            try:
                child_before = os.fstat(child)
                if not stat.S_ISREG(child_before.st_mode):
                    raise AuditError(f"non-regular policy entry: {name}")
                if child_before.st_size > 1024 * 1024:
                    raise AuditError(f"policy file too large: {name}")
                data = bytearray()
                while len(data) < child_before.st_size:
                    chunk = os.read(child, child_before.st_size - len(data))
                    if not chunk:
                        raise AuditError(f"short policy read: {name}")
                    data.extend(chunk)
                if os.read(child, 1):
                    raise AuditError(f"policy file grew during read: {name}")
                child_after = os.fstat(child)
                if (child_before.st_dev, child_before.st_ino, child_before.st_size, child_before.st_mtime_ns) != (child_after.st_dev, child_after.st_ino, child_after.st_size, child_after.st_mtime_ns):
                    raise AuditError(f"policy file changed during read: {name}")
                result[name] = bytes(data)
            finally:
                os.close(child)
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_mtime_ns):
            raise AuditError("policy directory changed during read")
        if names != sorted(os.listdir(descriptor)):
            raise AuditError("policy directory membership changed during read")
        return result
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
        fields = PROGRAM_HEADER.unpack_from(data, phoff + index * phentsize)
        p_type, p_flags, p_offset, p_vaddr, _p_paddr, p_filesz, p_memsz, p_align = fields
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
    if len(data) != expected["size"] or sha256(data) != expected["sha256"]:
        raise AuditError(f"unexpected {key} identity")
    return parse_load_segments(data)


def verify_config(data: bytes, key: str) -> dict[str, Any]:
    expected = CONFIG_SUBJECTS[key]
    digest = sha256(data)
    if len(data) != expected["size"] or digest != expected["sha256"]:
        raise AuditError(f"unexpected {key} identity")
    return {**expected, "sha256": digest, "matched": True}


def verify_ranges(data: bytes, segments: list[dict[str, int]], ranges: dict[str, tuple[int, int, str]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, (start, end, digest) in ranges.items():
        offset = va_to_offset(segments, start, end - start)
        actual = sha256(data[offset:offset + end - start])
        if actual != digest:
            raise AuditError(f"range hash mismatch: {name}")
        result[name] = {"elf_va_start": f"0x{start:x}", "elf_va_end_exclusive": f"0x{end:x}", "size": end - start, "sha256": actual, "matched": True}
    return result


def verify_anchor(data: bytes, segments: list[dict[str, int]], va: int, expected_hex: str) -> dict[str, Any]:
    expected = bytes.fromhex(expected_hex)
    offset = va_to_offset(segments, va, len(expected))
    if data[offset:offset + len(expected)] != expected:
        raise AuditError(f"anchor mismatch at ELF VA {va:#x}")
    return {"elf_va": f"0x{va:x}", "size": len(expected), "sha256": sha256(expected), "bytes_hex": expected_hex, "matched": True}


def verify_rel_call(data: bytes, segments: list[dict[str, int]], va: int, target: int) -> dict[str, Any]:
    offset = va_to_offset(segments, va, 5)
    raw = data[offset:offset + 5]
    if raw[0] != 0xE8 or va + 5 + struct.unpack_from("<i", raw, 1)[0] != target:
        raise AuditError(f"call target mismatch at ELF VA {va:#x}")
    return {"elf_va": f"0x{va:x}", "target_elf_va": f"0x{target:x}", "bytes_hex": raw.hex(), "matched": True}


def direct_call_xrefs(data: bytes, segments: list[dict[str, int]], target: int) -> list[int]:
    hits: list[int] = []
    for segment in segments:
        if not (segment["flags"] & 1):
            continue
        start = segment["offset"]
        blob = data[start:start + segment["filesz"]]
        for index in range(max(0, len(blob) - 4)):
            if blob[index] != 0xE8:
                continue
            va = segment["vaddr"] + index
            if va + 5 + struct.unpack_from("<i", blob, index + 1)[0] == target:
                hits.append(va)
    return sorted(hits)


def parse_smack_rules(policies: dict[str, bytes]) -> tuple[list[dict[str, Any]], list[str]]:
    rules: list[dict[str, Any]] = []
    for name, data in sorted(policies.items()):
        try:
            text = data.decode("ascii")
        except UnicodeDecodeError as exc:
            raise AuditError(f"non-ASCII SMACK policy: {name}") from exc
        for line_number, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            fields = stripped.split()
            if len(fields) != 3 or not (1 <= len(fields[2]) <= 7) or any(character not in "rwxatl-" for character in fields[2]):
                raise AuditError(f"unexpected SMACK rule at {name}:{line_number}")
            rules.append({"subject": fields[0], "object": fields[1], "access": fields[2], "file": name, "line": line_number})
    incoming = {rule["subject"] for rule in rules if rule["object"] == "App::projection" and "w" in rule["access"]}
    outgoing = {rule["object"] for rule in rules if rule["subject"] == "App::projection" and "w" in rule["access"]}
    bilateral = sorted(incoming & outgoing)
    if bilateral != sorted(EXPECTED_BILATERAL_LABELS):
        raise AuditError("unexpected bilateral App::projection SMACK label set")
    relevant = [rule for rule in rules if "App::projection" in (rule["subject"], rule["object"])]
    return relevant, bilateral


def build_report(framework: bytes, service: bytes, unit: bytes, relabel: bytes, policies: dict[str, bytes]) -> dict[str, Any]:
    framework_segments = verify_subject(framework, "framework")
    service_segments = verify_subject(service, "service")
    unit_identity = verify_config(unit, "unit")
    relabel_identity = verify_config(relabel, "relabel")
    if "projection" not in policies:
        raise AuditError("projection SMACK policy is missing")
    projection_identity = verify_config(policies["projection"], "projection_policy")

    unit_text = unit.decode("ascii")
    relabel_text = relabel.decode("ascii")
    if "ExecStart=/app/bin/iAP2Service-2.0" not in unit_text or "Restart=always" not in unit_text:
        raise AuditError("unexpected iAP2 service unit semantics")
    active_unit_lines = [line.strip() for line in unit_text.splitlines() if line.strip() and not line.lstrip().startswith(("#", ";"))]
    if any(line.startswith("User=") for line in active_unit_lines):
        raise AuditError("iAP2 service unexpectedly has a User= restriction")
    if 'APP_25=("iAP2Service-2.0" "App::projection")' not in relabel_text:
        raise AuditError("iAP2 service SMACK execute label assignment is missing")

    relevant_rules, bilateral = parse_smack_rules(policies)

    producer_entries: list[dict[str, Any]] = []
    expected_event_calls = []
    for init_call, used_call, length_store, event_call in PRODUCER_ANCHORS:
        init = verify_rel_call(service, service_segments, init_call, 0x4720)
        used = verify_rel_call(service, service_segments, used_call, 0x4F00)
        store = verify_anchor(service, service_segments, length_store, "895038")
        event = verify_rel_call(service, service_segments, event_call, 0x2BE82)
        window_offset = va_to_offset(service_segments, init_call - 24, 24)
        window = service[window_offset:window_offset + 24]
        marker = b"\xb9\x40\x00\x00\x00"
        positions = [index for index in range(len(window) - len(marker) + 1) if window[index:index + len(marker)] == marker]
        if len(positions) != 1:
            raise AuditError(f"missing unique offset-0x40 initializer at {init_call:#x}")
        producer_entries.append({
            "marshal_init_call": init,
            "marshal_initial_offset": {"elf_va": f"0x{init_call - 24 + positions[0]:x}", "value": 64, "matched": True},
            "get_used_size_call": used,
            "total_length_store": store,
            "send_event_call": event,
        })
        expected_event_calls.append(event_call)
    found_event_calls = direct_call_xrefs(service, service_segments, 0x2BE82)
    if found_event_calls != sorted(expected_event_calls):
        raise AuditError("SendEventToApp direct-call inventory mismatch")

    command_dispatch = {
        name: [verify_rel_call(service, service_segments, call, target) for call, target in calls]
        for name, calls in COMMAND_DISPATCH_CALLS.items()
    }

    dynamic_ranges = {
        name: {
            **verify_ranges(service, service_segments, {name: (start, end, digest)})[name],
            "unchecked_uint32_capacity_formula": formula,
        }
        for name, (start, end, digest, formula) in DYNAMIC_PRODUCER_RANGES.items()
    }

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "tool": {"name": "iap2_local_socket_framing_audit.py", "version": TOOL_VERSION},
        "subjects": {key: {**value, "format": "ELF64 little-endian ET_DYN x86-64"} for key, value in SUBJECTS.items()},
        "configuration_subjects": {"unit": unit_identity, "relabel": relabel_identity, "projection_policy": projection_identity},
        "address_model": {
            "artifact_addresses": "ELF virtual addresses",
            "file_mapping": "resolved through file-backed PT_LOAD segments",
            "ghidra_image_base": "0x100000",
            "ghidra_normalization": "subtract 0x100000 from recovered Ghidra addresses",
        },
        "service_ranges": verify_ranges(service, service_segments, SERVICE_RANGES),
        "framework_ranges": verify_ranges(framework, framework_segments, FRAMEWORK_RANGES),
        "service_anchors": {name: verify_anchor(service, service_segments, va, expected) for name, (va, expected) in SERVICE_ANCHORS.items()},
        "framework_anchors": {name: verify_anchor(framework, framework_segments, va, expected) for name, (va, expected) in FRAMEWORK_ANCHORS.items()},
        "local_endpoint": {
            "path": "/tmp/iAp2Socket",
            "family": "AF_UNIX (1)",
            "type": "SOCK_STREAM (1)",
            "server_creation": "iAP2Service-2.0 calls umask(0), unlinks the path, creates and binds the pathname socket, restores the prior umask, and listens with backlog 5",
            "dac_creation_mode": "0777 before parent-directory, mount, and LSM checks",
            "accept_boundary": "the exact accept-to-header-recv path performs no peer-credential check; no live pathname metadata or accepted peer was observed",
            "service_unit": {"configured_uid": 0, "basis": "no User= restriction", "restart": "always"},
            "smack": {
                "configured_service_exec_label": "App::projection",
                "new_inode_label_semantics": "Linux 4.1 Smack initializes a new inode from the creating task label unless transmutation applies",
                "bilateral_write_labels_for_uds_stream_connect": bilateral,
                "bilateral_label_count": len(bilateral),
                "relevant_rules": relevant_rules,
                "runtime_boundary": "actual task/socket/inode labels, /tmp mount label/transmutation state, live policy load, pathname ownership, and connect success remain unobserved",
            },
        },
        "framing": {
            "header_size": 64,
            "declared_total_size_offset": "0x38",
            "declared_total_size_type": "uint32_t (loaded with 32-bit zero extension)",
            "recv_flags": "MSG_WAITALL (0x100)",
            "service_server_receiver": [
                "receives a nominal 64-byte header into an uncleared stack object but accepts any positive return rather than requiring 64",
                "uses the potentially unreceived declared-total field at header offset 0x38 and allocates exactly that value",
                "copies all 64 header bytes into that allocation before testing whether declared total size is at most 64",
                "for declared totals above 64, receives declared_total-64 body bytes but accepts any positive short body before dispatch",
                "dispatches the allocation to handleClientCmd for both the at-most-64 branch and the positive-body branch",
            ],
            "framework_client_receiver": [
                "uses the same uncleared-stack 64-byte MSG_WAITALL header read and positive-only return check",
                "may consume an unreceived declared-total field, then allocates exactly that value, copies 64 bytes before the lower-bound branch, and dispatches server events",
            ],
            "marshal_length_semantics": {
                "producer": "all 37 recovered direct SendEventToApp producers initialize marshaling at offset 0x40 and store iAp2MarshalGetUsedSize at header offset 0x38; successful ordinary marshals therefore encode total transaction size including the 64-byte header",
                "consumer": "iAp2MarshalInitFromTxn starts parsing at transaction+0x40 but copies the total-size field directly into remaining without subtracting 0x40",
                "overstatement": 64,
            },
        },
        "local_command_dispatch": {
            "range": "handleClientCmd 0x2ea28..0x2f1ad",
            "command_handler_count": len(COMMAND_DISPATCH_CALLS),
            "calls": command_dispatch,
            "conclusion": "the accepted local-client transaction dispatcher directly reaches all 11 iAp2MarshalGetBytes caller functions and both identification handlers that supply the heap-string wrapper; command and session-state predicates still apply",
        },
        "marshal_writer_family": {
            "iAp2MarshalInit": {
                "range": "0x2100d..0x210ff",
                "rejects_offset_gt_capacity": {
                    "elf_va": "0x21038",
                    "mechanism": "cmp rdx, rax; jbe success; else sets flag bit 1, remaining=0, ptr=0",
                    "matched": True
                }
            },
            "iAp2MarshalInitFromTxn": {
                "range": "0x210ff..0x21175",
                "overstates_remaining_by": 64,
                "anchor": "0x21126..0x2115e copies txn+0x38 (total size) into remaining without subtracting 0x40",
                "matched": True
            },
            "iAp2MarshalAlloc": {
                "range": "0x21175..0x2129d",
                "loads_remaining": {"elf_va": "0x211e5", "matched": True},
                "compares_remaining_vs_aligned_request": {"elf_va": "0x211ea", "matched": True},
                "failure_sets_flag_bit2_returns_null": {"elf_va": "0x211f7", "matched": True},
                "success_requires_remaining_ge_aligned": True
            },
            "iAp2MarshalPutBytes": {
                "range": "0x21583..0x21645",
                "calls_putuint32_then_alloc": {"elf_va": "0x215e3", "matched": True},
                "alloc_failure_skips_memcpy": {"elf_va": "0x215fe", "matched": True}
            },
            "iAp2MarshalGetUsedSize": {
                "range": "0x21b21..0x21ca0",
                "validates_current_ptr_le_end_ptr": {"elf_va": "0x21b87", "matched": True},
                "returns_zero_on_error_state": True
            },
            "conclusion": "writer family fails closed: wrapped or undersized capacity causes iAp2MarshalAlloc to fail, iAp2MarshalPutBytes skips memcpy; no phone-controlled heap overflow via dynamic producer arithmetic"
        },
        "producer_inventory": {
            "direct_send_event_call_count": len(PRODUCER_ANCHORS),
            "successful_marshal_minimum_total": 64,
            "anchors": producer_entries,
            "dynamic_capacity_producer_count": len(DYNAMIC_PRODUCER_RANGES),
            "dynamic_capacity_producers": dynamic_ranges,
            "capacity_bounds": {
                "wrap_threshold": "uint32 multiplication wraps at 2^32; requires length ~1 GiB",
                "upstream_parser_bounds": "all reviewed callers supply 16-bit TLV lengths (max 65535)",
                "max_observed_capacity": "~524 KiB (WiFiInformation with two max lengths)",
                "wrap_reachable": False
            },
            "producer_residue": {
                "location": "handleExternalAccessoryProtocolRecvData at 0x141896",
                "issue": "unconditional header stores at +0x00, +0x38, +0x3c after possibly-failed marshal",
                "reachability": "requires param_5 <= -0x19 (negative length); reviewed receive paths produce positive bounded lengths only",
                "classification": "code smell / defect residue, not a demonstrated primitive"
            },
            "boundary": "wrapped-capacity heap-overflow hypothesis retired by writer capacity enforcement and upstream bounds; only unreachable negative-length header-store residue remains",
        },
        "findings": {
            "undersized_total": {
                "classification": "exact-static local AF_UNIX heap out-of-bounds write candidate (CWE-787)",
                "mechanism": "a connected client can supply a declared total below 64; the UID-zero App::projection server allocates that smaller size and performs eight fixed qword header stores before its lower-bound branch",
                "impact_boundary": "allocation behavior, allocator corruption, process crash, code execution, SMACK-domain transition, root, persistence, and installed-unit applicability are not demonstrated",
            },
            "transaction_remaining": {
                "classification": "exact-static transaction-tail out-of-bounds read candidate (CWE-125)",
                "mechanism": "the field proven by producers and receivers to be total size is reused as payload remaining after the parse pointer advances by 64, allowing marshal accessors to accept reads extending by as much as 64 bytes past the transaction allocation",
                "impact_boundary": "a specific downstream disclosure, crash, code execution, physical phone route, or CVE identity is not demonstrated",
            },
            "partial_reads": {
                "classification": "exact-static uninitialized header/body consumption candidate (CWE-457)",
                "mechanism": "both receivers treat positive short MSG_WAITALL reads as success; a short header leaves unread stack fields, potentially including declared total, in use, while a short body leaves an uninitialized malloc tail inside the declared allocation before dispatch",
                "impact_boundary": "short-read realization, allocator effects, and any attacker-visible use of uninitialized bytes are not demonstrated",
            },
            "resource_use": {
                "classification": "exact-static local resource-exhaustion candidate (CWE-400)",
                "mechanism": "the uint32 declared total has no reviewed maximum before malloc and a blocking MSG_WAITALL body receive",
                "impact_boundary": "memory availability, process/supervisor behavior, and user-visible denial of service are unknown",
            },
        },
        "assessment": {
            "demonstrated": [
                "exact recovered local AF_UNIX pathname, server/client socket construction, framing receivers, command dispatcher, and marshal initializer semantics",
                "direct dispatcher calls to all 11 recovered byte-accessor caller functions and both identification handlers",
                "configured UID-zero service and App::projection execute label",
                "19 recovered labels with bilateral write rules required by Linux 4.1 Smack UDS stream-connect checks",
                "37 exact direct first-party event producers using offset-64 marshaling and total used-size framing",
                "fixed 64-byte copies before the declared-total lower-bound checks in both local receiver directions",
            ],
            "not_demonstrated": [
                "a live /tmp/iAp2Socket, actual pathname mode/label, connect success, accepted untrusted peer, or installed-unit byte match",
                "physical phone delivery to this local framing defect or bypass of iAP2/CarPlay admission",
                "allocator corruption, process crash/restart, information disclosure, reliable control-flow influence, code execution, unrestricted root, SMACK escape, persistence, or firmware modification",
                "CVE identity, public exploit identity, or affected-versus-fixed SDK lineage",
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
    parser.add_argument("framework", type=Path)
    parser.add_argument("service", type=Path)
    parser.add_argument("unit", type=Path)
    parser.add_argument("relabel", type=Path)
    parser.add_argument("smack_dir", type=Path)
    parser.add_argument("--output", type=Path, help="create report without overwriting an existing path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = build_report(
            stable_read(args.framework), stable_read(args.service), stable_read(args.unit),
            stable_read(args.relabel), stable_read_directory(args.smack_dir),
        )
        payload = encode_report(report)
        if args.output is None:
            sys.stdout.buffer.write(payload)
        else:
            exclusive_write(args.output, payload)
    except (AuditError, OSError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
