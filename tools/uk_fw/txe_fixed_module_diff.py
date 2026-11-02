#!/usr/bin/env python3
"""Hash-bound passive comparison of affected, first-fixed, and later TXE modules.

This tool does not execute firmware.  It parses three already-extracted flash images,
validates the signed CPD/metadata/module chains used for the comparison, strictly
decompresses selected CSE modules, and emits deterministic JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import os
import stat
import struct
import sys
from pathlib import Path

SCHEMA = "ioniq-txe-fixed-module-diff/v5"
OLD_SHA256 = "f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac"
FIRST_FIXED_SHA256 = "db9325168976e1e68cba25924e82c2aeb2db85fb7a678de5fd66e200ab7643b9"
LATER_SHA256 = "75a866331d8f23d023bbdcf9efdfee7b57bf4727eb50f6162940a2a51cb57b4a"
OLD_NFTP = 0x203000
OLD_FTPR = 0x11E000
FIRST_FIXED_NFTP = 0x254000
FIRST_FIXED_FTPR = 0x21000
LATER_NFTP = 0x147000
LATER_FTPR = 0x20000
OLD_HECI_SHA256 = "82b7be7bb8069aebfb2c9f7a0e994500fe10d631e67a16f5a5fec71d29679125"
FIRST_FIXED_HECI_SHA256 = "16afeb7e9a9328bd22b5c8b383b5e003bcce2e4d46db18ea1737606bffa3ed31"
LATER_HECI_SHA256 = "04dceeb0b42db7910d913545b9b2342e9a26349c8e9d2e2bede201af62bf3b8f"
OLD_BUSDRV_SHA256 = "f226a92dd219a020bca96aeca3b54d8b0870f230128b7cb206c3389d5096ad21"
FIRST_FIXED_BUSDRV_SHA256 = "0e995c76f16f1f86240f85416059ca32e5c6fd0155eb1d3132b90505e8646fc0"
OLD_SYSLIB_SHA256 = "dba068b882c11783af4e2c0b7911b3a0db90f9b22808f42ac3e8768e2dda961c"
FIRST_FIXED_SYSLIB_SHA256 = "1f4722eeaab64eee5b6febe1b7e6d21565794c929173a56ff4bb9a01f96b00c8"
OLD_FPF_SHA256 = "9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9"
FIRST_FIXED_FPF_SHA256 = "e8f635d1ae1db00fb686fcacece4f2684109b9b8a32f852bc00f383218f784b8"
LATER_FPF_SHA256 = "2c188d8f1c0ee1a0eab08e716599149b370305033d2435c3745c7f399909713d"
OLD_VFS_SHA256 = "59b0ee9381860d1700f6c4638b0e165e3dba27d97d5017b8118b82a18f77f91b"
FIRST_FIXED_VFS_SHA256 = "52e0773d3115581d16b039e7c7e65c5dcbddf9d332cd98bdc9bb1ab6f6ff9e68"
LATER_VFS_SHA256 = "c5775a79d72c6f6d35656d6cd56a2648a17093f8436809b309d44229f107bc3b"
MODULES = ("heci", "busdrv", "storage", "policy", "fpf", "dal_sdm", "vfs")

LATER_HECI_RANGES = {
    "receive_dispatch": (0x189A, 0x1EF8, "4aea1addeb7e4e4fef929be25f3eb879a0114673e7572ec8c4b1d9dcff03fe64"),
    "fifo_bounded_copy": (0x27DA, 0x28D5, "5b8eafc086806a31c4d8adff2fd079d65b6ab205bd09a730cb7e252df7efa764"),
    "payload_consumer": (0x2B46, 0x3052, "6ef9be6f6d5d37d30dfab717dd8651118a7e8510ccce8455c72d83c473019d9e"),
    "client_lookup": (0x3052, 0x3094, "0b7634ab4b6af9e543ea8afbdd3feedb68c5aada26400b0db8b2ff5af9fa5266"),
    "connection_lookup": (0x3094, 0x3109, "86f2ac3493e735de1788d98144a0e2480b0801591522ee0a80c04c6056f3ef16"),
    "extended_header_parser": (0x3AD2, 0x3C0A, "f3ed29ecdcd43505ac0824e7b4762bde7bc29c477747a891f5646cb5a3e49e42"),
}

FIRST_FIXED_HECI_RANGES = {
    "receive_dispatch": (
        0x17C8,
        0x1DC9,
        "89d34094c7c72571ae5a5790b95c1570a81acc31a48105aa0092fb3017f05dc7",
        "203b2c1b83c63e939cd73d451a9656ae21544c2ce875842506c928e99bfa128b",
        (0x17F7, 0x1852, 0x1888, 0x1900, 0x1920, 0x195B, 0x19B4, 0x1A0C, 0x1AD9,
         0x1AF7, 0x1B49, 0x1B6C, 0x1C08, 0x1C43, 0x1C82, 0x1D26, 0x1D76, 0x1DBC),
    ),
    "fifo_bounded_copy": (
        0x268D,
        0x27B7,
        "d8df2a82e6f71db82616c63898b8e3a3cb46cf4bb524ae5bd93d573ad889e362",
        "99811a48487433d89db5ce8eaa90fd74c7be94f1a45577e73adcea88003159d8",
        (0x270F, 0x2785),
    ),
    "payload_consumer": (
        0x2A2D,
        0x2E78,
        "5c77d1e0db46ff8847d0a232ef6efa074767d5fe24aaa41727f595997831c419",
        "b5079daa3220f61e3eea68fefc12fdc3cdd7477cd6ac67a1fd236c5fbbf7f7fc",
        (0x2A8A, 0x2B1F, 0x2B42, 0x2B83, 0x2BAF, 0x2C46, 0x2C9E, 0x2CD4,
         0x2D0C, 0x2D96, 0x2DF9),
    ),
}

# Runtime ranges for all 42 syslib destinations imported by affected HECI.
# Each end is the next reviewed function entry (or the end of the two-byte
# interrupt stub at 0x118b0). The first-fixed start is recovered independently
# from the corresponding HECI import stub at affected address +5.
SYSLIB_HECI_DESTINATION_RANGES = {
    0x06ABC: (0x06FBF, 0x06AC1, 0x06FC4),
    0x07972: (0x07989, 0x07977, 0x0798E),
    0x07F65: (0x07F80, 0x07F6A, 0x07F85),
    0x08489: (0x084C6, 0x0848E, 0x084CB),
    0x084E8: (0x085E0, 0x084ED, 0x085E5),
    0x08F00: (0x08F0C, 0x08F05, 0x08F11),
    0x09088: (0x0909D, 0x0908D, 0x090A2),
    0x090B3: (0x090CB, 0x090B8, 0x090D0),
    0x09783: (0x097A1, 0x09788, 0x097A6),
    0x09874: (0x09983, 0x09879, 0x09988),
    0x09983: (0x099CA, 0x09988, 0x099CF),
    0x09B51: (0x09B72, 0x09B56, 0x09B77),
    0x0A274: (0x0A298, 0x0A279, 0x0A29D),
    0x0A298: (0x0A2A3, 0x0A29D, 0x0A2A8),
    0x0A2A3: (0x0A2AD, 0x0A2A8, 0x0A2B2),
    0x0AF34: (0x0AFB4, 0x0AF39, 0x0AFB9),
    0x0B393: (0x0B43B, 0x0B398, 0x0B440),
    0x0BD56: (0x0BD98, 0x0BD5B, 0x0BD9D),
    0x0BDE8: (0x0BDFA, 0x0BDED, 0x0BDFF),
    0x0BEA2: (0x0BEBC, 0x0BEA7, 0x0BEC1),
    0x0C7E7: (0x0C7F9, 0x0C7EC, 0x0C7FE),
    0x0CFB5: (0x0CFC9, 0x0CFBA, 0x0CFCE),
    0x0D660: (0x0D671, 0x0D665, 0x0D676),
    0x0D6C2: (0x0D750, 0x0D6C7, 0x0D755),
    0x0DA93: (0x0DAAA, 0x0DA98, 0x0DAAF),
    0x0DAAA: (0x0DB68, 0x0DAAF, 0x0DB6D),
    0x0DE35: (0x0DE5C, 0x0DE3A, 0x0DE61),
    0x0E0BD: (0x0E105, 0x0E0C2, 0x0E10A),
    0x0E46D: (0x0E60E, 0x0E472, 0x0E613),
    0x0EC24: (0x0EC38, 0x0EC29, 0x0EC3D),
    0x0F8F8: (0x0F9D1, 0x0F8FD, 0x0F9D6),
    0x103D6: (0x10593, 0x103DB, 0x10598),
    0x1140A: (0x11427, 0x1140F, 0x1142C),
    0x118B0: (0x118B2, 0x118B8, 0x118BA),
    0x164F3: (0x16516, 0x164FB, 0x1651E),
    0x17D3B: (0x17D46, 0x17D5D, 0x17D68),
    0x17D46: (0x17D73, 0x17D68, 0x17D95),
    0x17E3D: (0x17E48, 0x17E5F, 0x17E6A),
    0x17E48: (0x17E5C, 0x17E6A, 0x17E7E),
    0x17E5C: (0x17E6D, 0x17E7E, 0x17E8F),
    0x17F1A: (0x17F2E, 0x17F3C, 0x17F50),
    0x17FC1: (0x17FE2, 0x17FE3, 0x18004),
}

SYSLIB_HECI_ALLOWED_REL32_TARGET_PAIRS = {
    (0x0102E, 0x0102E),
    (0x0103D, 0x0103D),
    (0x079E9, 0x079EE),
    (0x118B0, 0x118B8),
    (0x120D3, 0x120DB),
    (0x12C02, 0x12C0A),
    (0x1693C, 0x1695E),
    (0x17F2E, 0x17F50),
}

# Reviewed direct-call instruction offsets within the 42 bodies above. These
# 96 instruction boundaries exclude nine incidental 0xe8 data/immediate bytes.
SYSLIB_HECI_DIRECT_CALL_OFFSETS = {
    0x06ABC: (0x2B, 0x109, 0x114, 0x130, 0x142, 0x154, 0x1A1, 0x1AC, 0x1B3, 0x208, 0x217, 0x296, 0x310, 0x373, 0x435, 0x43F, 0x490, 0x4AF, 0x4C5, 0x4D0, 0x4E4),
    0x07F65: (0x14,),
    0x08489: (0xD,),
    0x084E8: (0xE, 0x32, 0x3D, 0xAD, 0xD4, 0xDF),
    0x08F00: (0x5,),
    0x09088: (0xE,),
    0x090B3: (0x11,),
    0x09783: (0x17,),
    0x09874: (0x2C, 0x37, 0x83, 0xC4, 0xE4, 0xEF, 0x102),
    0x09983: (0xD,),
    0x09B51: (0x1A,),
    0x0A274: (0x1D,),
    0x0AF34: (0x1B, 0x26, 0x2E, 0x5A),
    0x0B393: (0x29, 0x65, 0x6D, 0x79, 0x82, 0x8F, 0x98),
    0x0BEA2: (0x13,),
    0x0C7E7: (0xB,),
    0x0CFB5: (0xD,),
    0x0D660: (0x8,),
    0x0D6C2: (0x18, 0x23, 0x74, 0x7F),
    0x0DA93: (0x10,),
    0x0DAAA: (0x21, 0x62, 0xB1),
    0x0DE35: (0x5,),
    0x0E0BD: (0xE,),
    0x0E46D: (0xF, 0x1A, 0x37, 0x73, 0x8C, 0x97, 0xCA, 0xD5, 0xFB, 0x10F, 0x170, 0x186, 0x191),
    0x0EC24: (0xA,),
    0x0F8F8: (0x2E, 0x3C, 0xB8),
    0x103D6: (0x1B, 0x5F, 0xD5, 0x112, 0x184, 0x192, 0x1B0),
    0x1140A: (0x16,),
    0x164F3: (0x1C,),
    0x17E48: (0xA,),
    0x17FC1: (0x15,),
}

# New internal first-level callees after excluding the two unchanged external
# gates (0x102e/0x103d) and the already reviewed 0x7972/0x118b0 bodies.
SYSLIB_HECI_INCIDENTAL_E8_OFFSETS = {
    0x06ABC: (0x27F, 0x2A9, 0x369, 0x399, 0x4B0),
    0x0DAAA: (0x2B,),
    0x0E46D: (0x107,),
    0x103D6: (0x8B, 0xE6),
}

SYSLIB_HECI_FIRST_LEVEL_CALLEE_RANGES = {
    0x06A95: (0x06ABC, 0x06A9A, 0x06AC1),
    0x0790B: (0x07914, 0x07910, 0x07919),
    0x07963: (0x07972, 0x07968, 0x07977),
    0x07989: (0x079E9, 0x0798E, 0x079EE),
    0x079E9: (0x07A83, 0x079EE, 0x07A88),
    0x07C5E: (0x07C6A, 0x07C63, 0x07C6F),
    0x07E31: (0x07EA2, 0x07E36, 0x07EA7),
    0x081D1: (0x0847D, 0x081D6, 0x08482),
    0x084C6: (0x084E8, 0x084CB, 0x084ED),
    0x085E0: (0x08994, 0x085E5, 0x08999),
    0x08A77: (0x08AE6, 0x08A7C, 0x08AEB),
    0x08B27: (0x08B36, 0x08B2C, 0x08B3B),
    0x08ED3: (0x08F00, 0x08ED8, 0x08F05),
    0x09411: (0x09421, 0x09416, 0x09426),
    0x09458: (0x09461, 0x0945D, 0x09466),
    0x097A1: (0x09874, 0x097A6, 0x09879),
    0x0B4B1: (0x0B4DF, 0x0B4B6, 0x0B4E4),
    0x0BE51: (0x0BEA2, 0x0BE56, 0x0BEA7),
    0x0D0D7: (0x0D0EA, 0x0D0DC, 0x0D0EF),
    0x0D29B: (0x0D2EE, 0x0D2A0, 0x0D2F3),
    0x0E1A8: (0x0E358, 0x0E1AD, 0x0E35D),
    0x0E358: (0x0E3A2, 0x0E35D, 0x0E3A7),
    0x0E66B: (0x0E67A, 0x0E670, 0x0E67F),
    0x0E6D7: (0x0E7D7, 0x0E6DC, 0x0E7DC),
    0x101C4: (0x10226, 0x101C9, 0x1022B),
    0x120D3: (0x12170, 0x120DB, 0x12178),
    0x12C02: (0x12C3C, 0x12C0A, 0x12C44),
    0x1693C: (0x1694F, 0x1695E, 0x16971),
    0x17F2E: (0x17F6C, 0x17F50, 0x17F8E),
}

SYSLIB_HECI_FIRST_LEVEL_ALLOWED_REL32_TARGET_PAIRS = {
    (0x0102E, 0x0102E),
    (0x0103D, 0x0103D),
    (0x07972, 0x07977),
    (0x08F00, 0x08F05),
    (0x0A274, 0x0A279),
    (0x118B0, 0x118B8),
    (0x11AB8, 0x11AC0),
    (0x11ADA, 0x11AE2),
    (0x120D3, 0x120DB),
    (0x16F8F, 0x16FB1),
}

LATER_FPF_ARB_FIELDS = {
    "RbeArbEn": (0x51C4, 2, 0x0A0, 0x0A1, "ec9b3df2ad66201dff320e17ccdbfdc9e916225c15e8e9f40785d8e7724257ba"),
    "OemKmArbEn": (0x51F0, 2, 0x0A4, 0x0A5, "d2f7aac91c2edbbfd31380f44aa3999df75c13cf48ec724dfdb084ea331f3cf7"),
    "UcodeArbEn": (0x537C, 2, 0x0C8, 0x0C9, "b52d64f84ba8c5e9ce884e66531a6c031a500c1831b2421887bee9d7a14ff671"),
    "RbeArbSvn": (0x5694, 12, 0x280, 0x28B, "2fe296dae7117a2d68249d70a75bd5d8cb8bde2e0d1016c63ef60ce331efe380"),
    "OemKmArbSvn": (0x56C0, 20, 0x28C, 0x29F, "b404993bc5636c51555449c91ca892a003a572a8a7a57a69b070af393273d185"),
    "UcodeArbSvn": (0x56EC, 14, 0x2A0, 0x2AD, "d636f759f668656b927bda76d35b02f3a78ee50107edc97066b1cc0e95e6fcc9"),
}


class Failure(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_read(path: Path, maximum: int = 32 * 1024 * 1024) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise Failure(f"unsafe or oversized input: {path}")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(fd, min(1024 * 1024, remaining))
            if not chunk:
                raise Failure(f"short read: {path}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(fd, 1):
            raise Failure(f"input grew while reading: {path}")
        after = os.fstat(fd)
        identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
        if identity(before) != identity(after):
            raise Failure(f"input changed while reading: {path}")
        return b"".join(chunks)
    finally:
        os.close(fd)


def parse_cpd(image: bytes, offset: int, expected_partition: bytes) -> dict[str, tuple[int, int]]:
    if offset + 0x10 > len(image):
        raise Failure("truncated CPD header")
    tag, count, header_version, entry_version, header_size, _, partition = struct.unpack_from(
        "<IIBBBBI", image, offset
    )
    if (
        tag != 0x44504324
        or not 1 <= count <= 256
        or header_version != 1
        or entry_version != 1
        or header_size != 0x10
        or partition.to_bytes(4, "little") != expected_partition
        or offset + 0x10 + count * 24 > len(image)
    ):
        raise Failure(f"{expected_partition.decode()} CPD header drift")
    entries: dict[str, tuple[int, int]] = {}
    for index in range(count):
        raw_name, raw_offset, size, _ = struct.unpack_from("<12sIII", image, offset + 0x10 + index * 24)
        try:
            name = raw_name.rstrip(b"\0").decode("ascii")
        except UnicodeDecodeError as exc:
            raise Failure("non-ASCII CPD member") from exc
        relative = raw_offset & 0x1FFFFFF
        if not name or name in entries or relative + size > len(image) - offset:
            raise Failure(f"invalid CPD member geometry: {name!r}")
        entries[name] = (relative, size)
    return entries


def member(image: bytes, cpd: int, entries: dict[str, tuple[int, int]], name: str) -> bytes:
    if name not in entries:
        raise Failure(f"missing CPD member: {name}")
    relative, size = entries[name]
    value = image[cpd + relative : cpd + relative + size]
    if len(value) != size:
        raise Failure(f"truncated CPD member: {name}")
    return value


def verify_mn2(manifest: bytes, label: str) -> dict:
    if len(manifest) < 0x284 or manifest[0x1C:0x20] != b"$MN2":
        raise Failure(f"{label} manifest header drift")
    header_size = struct.unpack_from("<I", manifest, 4)[0] * 4
    total_size = struct.unpack_from("<I", manifest, 0x18)[0] * 4
    key_size = struct.unpack_from("<I", manifest, 0x78)[0] * 4
    exponent_size = struct.unpack_from("<I", manifest, 0x7C)[0] * 4
    if (header_size, total_size, key_size, exponent_size) != (0x284, len(manifest), 0x100, 4):
        raise Failure(f"{label} manifest geometry drift")
    modulus = int.from_bytes(manifest[0x80:0x180], "little")
    exponent = int.from_bytes(manifest[0x180:0x184], "little")
    signature = int.from_bytes(manifest[0x184:0x284], "little")
    digest = hashlib.sha256(manifest[:0x80] + manifest[header_size:total_size]).digest()
    encoded = pow(signature, exponent, modulus).to_bytes(key_size, "big")
    separator = encoded.find(b"\0", 2)
    prefix = bytes.fromhex("3031300d060960864801650304020105000420")
    if not (
        encoded.startswith(b"\0\1")
        and separator >= 10
        and encoded[2:separator] == b"\xff" * (separator - 2)
        and encoded[separator + 1 :] == prefix + digest
    ):
        raise Failure(f"{label} embedded signature invalid")
    major, minor, hotfix, build = struct.unpack_from("<HHHH", manifest, 0x24)
    date = manifest[0x14:0x18]
    date_text = f"{date[3]:02x}{date[2]:02x}-{date[1]:02x}-{date[0]:02x}"
    return {
        "sha256": sha256(manifest),
        "size": len(manifest),
        "version": f"{major}.{minor}.{hotfix}.{build}",
        "date_bcd": date_text,
        "embedded_signature_valid": True,
        "signature_boundary": "self-consistency and byte binding only; no external ROM/fuse acceptance is established",
    }


def metadata_extensions(metadata: bytes, label: str) -> list[tuple[int, bytes]]:
    result: list[tuple[int, bytes]] = []
    position = 0
    while position < len(metadata):
        if position + 8 > len(metadata):
            raise Failure(f"{label} truncated extension")
        tag, size = struct.unpack_from("<II", metadata, position)
        if size < 8 or position + size > len(metadata):
            raise Failure(f"{label} extension geometry drift")
        result.append((tag, metadata[position : position + size]))
        position += size
    return result


def strict_cse_lzma(compressed: bytes, expected_size: int, label: str) -> bytes:
    if len(compressed) < 0x11 or compressed[0x0E:0x11] != b"\0\0\0":
        raise Failure(f"{label} Intel CSE LZMA header drift")
    decoder = lzma.LZMADecompressor()
    try:
        value = decoder.decompress(compressed[:0x0E] + compressed[0x11:])
    except lzma.LZMAError as exc:
        raise Failure(f"{label} LZMA failure") from exc
    if not decoder.eof or decoder.unused_data or len(value) != expected_size:
        raise Failure(f"{label} strict decompression drift")
    return value


def extract_module(
    image: bytes,
    cpd: int,
    entries: dict[str, tuple[int, int]],
    manifest: bytes,
    name: str,
) -> tuple[bytes, dict]:
    metadata_name = f"{name}.met"
    compressed = member(image, cpd, entries, name)
    metadata = member(image, cpd, entries, metadata_name)
    metadata_digest = hashlib.sha256(metadata).digest()[::-1]
    if manifest.count(metadata_digest) != 1:
        raise Failure(f"manifest-to-{metadata_name} binding drift")
    extensions = metadata_extensions(metadata, metadata_name)
    module_extensions = [value for tag, value in extensions if tag == 10]
    if len(module_extensions) != 1 or len(module_extensions[0]) != 0x38:
        raise Failure(f"{metadata_name} module extension drift")
    extension = module_extensions[0]
    compression = extension[8]
    uncompressed_size, compressed_size = struct.unpack_from("<II", extension, 0x0C)
    if compressed_size != len(compressed) or extension[0x18:0x38] != hashlib.sha256(compressed).digest()[::-1]:
        raise Failure(f"{metadata_name}-to-module binding drift")
    if compression == 2:
        decompressed = strict_cse_lzma(compressed, uncompressed_size, name)
    elif compression == 0 and uncompressed_size == compressed_size:
        decompressed = compressed
    else:
        raise Failure(f"unsupported {name} compression: {compression}")
    report = {
        "cpd_relative_offset": entries[name][0],
        "compressed_size": len(compressed),
        "compressed_sha256": sha256(compressed),
        "metadata_cpd_relative_offset": entries[metadata_name][0],
        "metadata_size": len(metadata),
        "metadata_sha256": sha256(metadata),
        "compression": "lzma" if compression == 2 else "none",
        "decompressed_size": len(decompressed),
        "decompressed_sha256": sha256(decompressed),
        "manifest_binds_metadata_reverse_sha256": True,
        "metadata_binds_module_reverse_sha256": True,
        "strict_decompression": compression == 2,
    }
    if name == "storage":
        report["reviewed_special_file_occurrences"] = {
            value.decode("ascii"): metadata.count(value)
            for value in (b"ndl_critical", b"ndl_counting")
        }
    return decompressed, report


def extract_syslib(image: bytes, cpd: int, entries: dict[str, tuple[int, int]], manifest: bytes) -> tuple[bytes, dict]:
    value = member(image, cpd, entries, "syslib")
    metadata = member(image, cpd, entries, "syslib.met")
    if manifest.count(hashlib.sha256(metadata).digest()[::-1]) != 1:
        raise Failure("FTPR manifest-to-syslib.met binding drift")
    if metadata.count(hashlib.sha256(value).digest()[::-1]) != 1:
        raise Failure("syslib.met-to-syslib binding drift")
    return value, {
        "cpd_relative_offset": entries["syslib"][0],
        "size": len(value),
        "sha256": sha256(value),
        "metadata_cpd_relative_offset": entries["syslib.met"][0],
        "metadata_size": len(metadata),
        "metadata_sha256": sha256(metadata),
        "manifest_binds_metadata_reverse_sha256": True,
        "metadata_binds_module_reverse_sha256": True,
    }


def byte_comparison(old: bytes, fixed: bytes) -> dict:
    common_prefix = 0
    for left, right in zip(old, fixed):
        if left != right:
            break
        common_prefix += 1
    common_suffix = 0
    limit = min(len(old), len(fixed)) - common_prefix
    while common_suffix < limit and old[-1 - common_suffix] == fixed[-1 - common_suffix]:
        common_suffix += 1
    overlap = min(len(old), len(fixed))
    differing = sum(old[index] != fixed[index] for index in range(overlap))
    return {
        "byte_identical": old == fixed,
        "same_size": len(old) == len(fixed),
        "overlap_size": overlap,
        "differing_bytes_at_same_offsets": differing,
        "common_prefix_size": common_prefix,
        "common_suffix_size": common_suffix,
    }


def checked_range(module: bytes, start: int, end: int, digest: str, label: str) -> dict:
    value = module[start:end]
    if len(value) != end - start or sha256(value) != digest:
        raise Failure(f"fixed HECI {label} range drift")
    return {
        "file_range": [start, end],
        "runtime_range": [0x26000 + start, 0x26000 + end],
        "size": end - start,
        "sha256": digest,
    }


def call_relocation_only_range(
    affected: bytes,
    first_fixed: bytes,
    start: int,
    end: int,
    affected_digest: str,
    first_fixed_digest: str,
    call_sites: tuple[int, ...],
    label: str,
) -> dict:
    affected_range = affected[start:end]
    first_fixed_range = first_fixed[start:end]
    if sha256(affected_range) != affected_digest or sha256(first_fixed_range) != first_fixed_digest:
        raise Failure(f"first-fixed HECI {label} range drift")
    allowed_differences = {offset for call in call_sites for offset in range(call + 1, call + 5)}
    actual_differences = {
        start + index
        for index, (left, right) in enumerate(zip(affected_range, first_fixed_range))
        if left != right
    }
    if not actual_differences or not actual_differences <= allowed_differences:
        raise Failure(f"first-fixed HECI {label} non-call-byte drift")
    normalized_affected = bytearray(affected_range)
    normalized_first_fixed = bytearray(first_fixed_range)
    calls = []
    for call in call_sites:
        if affected[call] != 0xE8 or first_fixed[call] != 0xE8:
            raise Failure(f"first-fixed HECI {label} call opcode drift")
        old_displacement = struct.unpack_from("<i", affected, call + 1)[0]
        new_displacement = struct.unpack_from("<i", first_fixed, call + 1)[0]
        if new_displacement - old_displacement != 5:
            raise Failure(f"first-fixed HECI {label} call relocation delta drift")
        normalized_affected[call + 1 - start : call + 5 - start] = b"\0" * 4
        normalized_first_fixed[call + 1 - start : call + 5 - start] = b"\0" * 4
        calls.append({
            "runtime_call_address": 0x26000 + call,
            "affected_relative_displacement": old_displacement,
            "first_fixed_relative_displacement": new_displacement,
            "displacement_delta": 5,
        })
    if normalized_affected != normalized_first_fixed:
        raise Failure(f"first-fixed HECI {label} normalized byte drift")
    return {
        "file_range": [start, end],
        "runtime_range": [0x26000 + start, 0x26000 + end],
        "affected_sha256": affected_digest,
        "first_fixed_sha256": first_fixed_digest,
        "raw_differing_byte_count": len(actual_differences),
        "non_call_immediate_differing_byte_count": 0,
        "call_relocations": calls,
        "equal_after_zeroing_only_enumerated_rel32_call_immediates": True,
    }


def module_wide_external_relocation_review(affected: bytes, first_fixed: bytes) -> dict:
    actual_differences = {
        index for index, (left, right) in enumerate(zip(affected, first_fixed)) if left != right
    }
    sites = []
    allowed_differences = set()
    normalized_affected = bytearray(affected)
    normalized_first_fixed = bytearray(first_fixed)
    target_counts: dict[int, int] = {}
    opcode_counts = {0xE8: 0, 0xE9: 0}
    for offset in range(len(affected) - 4):
        opcode = affected[offset]
        if opcode != first_fixed[offset] or opcode not in opcode_counts:
            continue
        old_displacement = struct.unpack_from("<i", affected, offset + 1)[0]
        new_displacement = struct.unpack_from("<i", first_fixed, offset + 1)[0]
        old_target = 0x26000 + offset + 5 + old_displacement
        new_target = 0x26000 + offset + 5 + new_displacement
        changed = any(
            affected[index] != first_fixed[index] for index in range(offset + 1, offset + 5)
        )
        if not changed or new_displacement - old_displacement != 5 or old_target >= 0x26000:
            continue
        if new_target != old_target + 5 or new_target >= 0x26000:
            raise Failure("first-fixed HECI external branch target drift")
        opcode_counts[opcode] += 1
        target_counts[old_target] = target_counts.get(old_target, 0) + 1
        allowed_differences.update(range(offset + 1, offset + 5))
        normalized_affected[offset + 1 : offset + 5] = b"\0" * 4
        normalized_first_fixed[offset + 1 : offset + 5] = b"\0" * 4
        sites.append(offset)
    if (
        len(actual_differences) != 377
        or opcode_counts != {0xE8: 366, 0xE9: 3}
        or len(target_counts) != 42
        or not actual_differences <= allowed_differences
        or normalized_affected != normalized_first_fixed
    ):
        raise Failure("first-fixed HECI module-wide relocation-only comparison drift")
    return {
        "affected_sha256": OLD_HECI_SHA256,
        "first_fixed_sha256": FIRST_FIXED_HECI_SHA256,
        "module_size": len(affected),
        "raw_differing_byte_count": len(actual_differences),
        "non_external_rel32_immediate_differing_byte_count": 0,
        "external_rel32_site_count": len(sites),
        "external_call_site_count": opcode_counts[0xE8],
        "external_tail_jump_site_count": opcode_counts[0xE9],
        "distinct_affected_external_target_count": len(target_counts),
        "affected_external_target_range": [min(target_counts), max(target_counts)],
        "all_first_fixed_external_targets_equal_affected_plus_five": True,
        "equal_after_zeroing_only_selected_external_rel32_immediates": True,
        "affected_external_target_reference_counts": {
            f"0x{target:x}": target_counts[target] for target in sorted(target_counts)
        },
    }


def first_fixed_busdrv_review(affected: bytes, first_fixed: bytes) -> dict:
    if (
        sha256(affected) != OLD_BUSDRV_SHA256
        or sha256(first_fixed) != FIRST_FIXED_BUSDRV_SHA256
        or len(affected) != 0x6000
        or len(first_fixed) != 0x6000
    ):
        raise Failure("first-fixed busdrv identity drift")

    actual_differences = {
        index for index, (left, right) in enumerate(zip(affected, first_fixed))
        if left != right
    }
    sites = []
    allowed_differences: set[int] = set()
    normalized_affected = bytearray(affected)
    normalized_first_fixed = bytearray(first_fixed)
    target_counts: dict[int, int] = {}
    for offset in range(len(affected) - 4):
        if affected[offset] != 0xE8 or first_fixed[offset] != 0xE8:
            continue
        old_displacement = struct.unpack_from("<i", affected, offset + 1)[0]
        new_displacement = struct.unpack_from("<i", first_fixed, offset + 1)[0]
        old_target = 0x26000 + offset + 5 + old_displacement
        new_target = 0x26000 + offset + 5 + new_displacement
        changed = any(
            affected[index] != first_fixed[index]
            for index in range(offset + 1, offset + 5)
        )
        if not changed or new_displacement - old_displacement != 5 or old_target >= 0x26000:
            continue
        if new_target != old_target + 5 or new_target >= 0x26000:
            raise Failure("first-fixed busdrv external call target drift")
        target_counts[old_target] = target_counts.get(old_target, 0) + 1
        allowed_differences.update(range(offset + 1, offset + 5))
        normalized_affected[offset + 1 : offset + 5] = b"\0" * 4
        normalized_first_fixed[offset + 1 : offset + 5] = b"\0" * 4
        sites.append(offset)

    if (
        len(actual_differences) != 97
        or len(sites) != 96
        or len(target_counts) != 26
        or min(target_counts, default=-1) != 0x6465
        or max(target_counts, default=-1) != 0x67AD
        or not actual_differences <= allowed_differences
        or normalized_affected != normalized_first_fixed
    ):
        raise Failure("first-fixed busdrv relocation-only comparison drift")

    return {
        "affected_sha256": OLD_BUSDRV_SHA256,
        "first_fixed_sha256": FIRST_FIXED_BUSDRV_SHA256,
        "module_size": len(affected),
        "raw_differing_byte_count": len(actual_differences),
        "non_external_rel32_immediate_differing_byte_count": 0,
        "external_rel32_call_site_count": len(sites),
        "distinct_affected_external_target_count": len(target_counts),
        "affected_external_target_range": [min(target_counts), max(target_counts)],
        "all_first_fixed_external_targets_equal_affected_plus_five": True,
        "equal_after_zeroing_only_selected_external_rel32_call_immediates": True,
        "affected_external_target_reference_counts": {
            f"0x{target:x}": target_counts[target] for target in sorted(target_counts)
        },
        "exact_static_observations": {
            "entire_busdrv_module_equal_after_only_external_rel32_call_normalization": True,
            "busdrv_local_opcode_or_non_address_data_change_at_first_fixed_boundary": False,
        },
        "attribution_boundary": "The complete affected and first-fixed busdrv modules are byte-identical after normalizing only 96 external call displacements to 26 syslib import stubs, each shifted by the inserted syslib export. This excludes busdrv-local opcode and non-address-data changes as the first-fixed CVE-2018-12147 fix, but does not exclude changed transitive callees, kernel/service handlers, another module, or downstream clients.",
    }


def first_fixed_heci_syslib_import_review(
    affected_heci: bytes,
    first_fixed_heci: bytes,
    affected_syslib: bytes,
    first_fixed_syslib: bytes,
) -> dict:
    if (
        sha256(affected_heci) != OLD_HECI_SHA256
        or sha256(first_fixed_heci) != FIRST_FIXED_HECI_SHA256
        or sha256(affected_syslib) != OLD_SYSLIB_SHA256
        or sha256(first_fixed_syslib) != FIRST_FIXED_SYSLIB_SHA256
        or len(affected_syslib) != 0x13000
        or len(first_fixed_syslib) != 0x13000
    ):
        raise Failure("HECI/syslib import-review identity drift")

    relocation_review = module_wide_external_relocation_review(
        affected_heci, first_fixed_heci
    )
    stub_references = {
        int(address, 16): count
        for address, count in relocation_review[
            "affected_external_target_reference_counts"
        ].items()
    }
    destinations: dict[int, tuple[int, int, int]] = {}
    for affected_stub, reference_count in sorted(stub_references.items()):
        affected_offset = affected_stub - 0x6000
        first_fixed_stub = affected_stub + 5
        first_fixed_offset = first_fixed_stub - 0x6000
        affected_destination = rel32_target(
            0x6000, affected_syslib, affected_offset, 0xE9
        )
        first_fixed_destination = rel32_target(
            0x6000, first_fixed_syslib, first_fixed_offset, 0xE9
        )
        if affected_destination in destinations:
            raise Failure("duplicate HECI-imported syslib destination")
        destinations[affected_destination] = (
            affected_stub,
            first_fixed_destination,
            reference_count,
        )
    if set(destinations) != set(SYSLIB_HECI_DESTINATION_RANGES):
        raise Failure("HECI-imported syslib destination set drift")

    bodies = {}
    total_bytes = 0
    total_raw_differences = 0
    total_rel32_relocations = 0
    total_absolute_relocations = 0
    for affected_start in sorted(destinations):
        affected_end, expected_first_start, first_end = (
            SYSLIB_HECI_DESTINATION_RANGES[affected_start]
        )
        affected_stub, first_start, reference_count = destinations[affected_start]
        if first_start != expected_first_start:
            raise Failure("HECI-imported syslib destination mapping drift")
        affected_body = affected_syslib[
            affected_start - 0x6000 : affected_end - 0x6000
        ]
        first_body = first_fixed_syslib[
            first_start - 0x6000 : first_end - 0x6000
        ]
        if not affected_body or len(affected_body) != len(first_body):
            raise Failure("HECI-imported syslib body geometry drift")

        actual_differences = {
            index
            for index, (left, right) in enumerate(zip(affected_body, first_body))
            if left != right
        }
        allowed_differences: set[int] = set()
        normalized_affected = bytearray(affected_body)
        normalized_first = bytearray(first_body)
        rel32_relocations = []
        for offset in range(len(affected_body) - 4):
            opcode = affected_body[offset]
            if opcode not in (0xE8, 0xE9) or first_body[offset] != opcode:
                continue
            if affected_body[offset + 1 : offset + 5] == first_body[offset + 1 : offset + 5]:
                continue
            affected_target = (
                affected_start
                + offset
                + 5
                + struct.unpack_from("<i", affected_body, offset + 1)[0]
            )
            first_target = (
                first_start
                + offset
                + 5
                + struct.unpack_from("<i", first_body, offset + 1)[0]
            )
            if (affected_target, first_target) not in SYSLIB_HECI_ALLOWED_REL32_TARGET_PAIRS:
                raise Failure("HECI-imported syslib rel32 target drift")
            allowed_differences.update(range(offset + 1, offset + 5))
            normalized_affected[offset + 1 : offset + 5] = b"\0" * 4
            normalized_first[offset + 1 : offset + 5] = b"\0" * 4
            rel32_relocations.append({
                "affected_runtime_address": affected_start + offset,
                "first_fixed_runtime_address": first_start + offset,
                "opcode": opcode,
                "affected_target": affected_target,
                "first_fixed_target": first_target,
            })

        absolute_relocations = []
        if affected_start == 0x6ABC:
            operand_offset = 0x1D5
            affected_value = struct.unpack_from("<I", affected_body, operand_offset)[0]
            first_value = struct.unpack_from("<I", first_body, operand_offset)[0]
            if (affected_value, first_value) != (0x18994, 0x189B8):
                raise Failure("HECI-imported syslib jump-table address drift")
            allowed_differences.update(range(operand_offset, operand_offset + 4))
            normalized_affected[operand_offset : operand_offset + 4] = b"\0" * 4
            normalized_first[operand_offset : operand_offset + 4] = b"\0" * 4
            absolute_relocations.append({
                "affected_operand_runtime_range": [0x6C91, 0x6C95],
                "first_fixed_operand_runtime_range": [0x6C96, 0x6C9A],
                "affected_value": affected_value,
                "first_fixed_value": first_value,
                "instruction": "indexed indirect jump table base",
            })

        if (
            not actual_differences <= allowed_differences
            or normalized_affected != normalized_first
        ):
            raise Failure("HECI-imported syslib normalized body drift")
        normalized_digest = sha256(bytes(normalized_affected))
        bodies[f"0x{affected_start:x}"] = {
            "affected_import_stub": affected_stub,
            "first_fixed_import_stub": affected_stub + 5,
            "heci_reference_count": reference_count,
            "affected_runtime_range": [affected_start, affected_end],
            "first_fixed_runtime_range": [first_start, first_end],
            "size": len(affected_body),
            "affected_sha256": sha256(affected_body),
            "first_fixed_sha256": sha256(first_body),
            "raw_differing_byte_count": len(actual_differences),
            "rel32_relocations": rel32_relocations,
            "absolute_address_relocations": absolute_relocations,
            "normalized_sha256": normalized_digest,
            "equal_after_reviewed_address_normalization": True,
        }
        total_bytes += len(affected_body)
        total_raw_differences += len(actual_differences)
        total_rel32_relocations += len(rel32_relocations)
        total_absolute_relocations += len(absolute_relocations)

    entry_shift_counts: dict[int, int] = {}
    for affected_start, (_, first_start, _) in SYSLIB_HECI_DESTINATION_RANGES.items():
        shift = first_start - affected_start
        entry_shift_counts[shift] = entry_shift_counts.get(shift, 0) + 1
    if (
        len(bodies) != 42
        or total_bytes != 4410
        or total_raw_differences != 39
        or total_rel32_relocations != 37
        or total_absolute_relocations != 1
        or entry_shift_counts != {5: 33, 8: 2, 34: 7}
    ):
        raise Failure("HECI-imported syslib aggregate drift")
    return {
        "syslib_code_base": 0x6000,
        "affected_syslib_sha256": OLD_SYSLIB_SHA256,
        "first_fixed_syslib_sha256": FIRST_FIXED_SYSLIB_SHA256,
        "imported_destination_count": len(bodies),
        "heci_external_reference_count": sum(stub_references.values()),
        "reviewed_body_byte_count": total_bytes,
        "raw_differing_byte_count": total_raw_differences,
        "rel32_relocation_site_count": total_rel32_relocations,
        "absolute_address_relocation_site_count": total_absolute_relocations,
        "destination_entry_shift_counts": {
            str(shift): entry_shift_counts[shift] for shift in sorted(entry_shift_counts)
        },
        "destination_bodies": bodies,
        "exact_static_observations": {
            "all_42_heci_import_stubs_resolved_to_syslib_destinations": True,
            "all_42_destination_bodies_have_equal_reviewed_geometry": True,
            "all_42_destination_bodies_equal_after_only_reviewed_address_normalization": True,
            "no_directly_imported_syslib_body_has_an_opcode_or_non_address_data_change": True,
        },
        "attribution_boundary": "All 42 syslib bodies directly imported by HECI are unchanged after normalizing 37 reviewed rel32 address operands and one indexed-jump-table base operand. This excludes a direct opcode or non-address data change in those entry bodies; it does not exclude changed transitive callees, syscall/service implementations, indirect dispatch targets, another signed module, or a downstream HECI client.",
    }


def first_fixed_heci_syslib_first_level_callee_review(
    affected_syslib: bytes,
    first_fixed_syslib: bytes,
) -> dict:
    if (
        sha256(affected_syslib) != OLD_SYSLIB_SHA256
        or sha256(first_fixed_syslib) != FIRST_FIXED_SYSLIB_SHA256
    ):
        raise Failure("HECI/syslib first-level review identity drift")

    call_target_counts: dict[tuple[int, int], int] = {}
    reviewed_call_addresses: set[int] = set()
    for affected_body_start, call_offsets in sorted(
        SYSLIB_HECI_DIRECT_CALL_OFFSETS.items()
    ):
        _, first_body_start, _ = SYSLIB_HECI_DESTINATION_RANGES[
            affected_body_start
        ]
        for relative_offset in call_offsets:
            affected_call = affected_body_start + relative_offset
            first_call = first_body_start + relative_offset
            affected_target = rel32_target(
                0x6000, affected_syslib, affected_call - 0x6000, 0xE8
            )
            first_target = rel32_target(
                0x6000, first_fixed_syslib, first_call - 0x6000, 0xE8
            )
            pair = (affected_target, first_target)
            call_target_counts[pair] = call_target_counts.get(pair, 0) + 1
            reviewed_call_addresses.add(affected_call)

    raw_e8_addresses: set[int] = set()
    for affected_start, (affected_end, _, _) in SYSLIB_HECI_DESTINATION_RANGES.items():
        raw_e8_addresses.update(
            address
            for address in range(affected_start, affected_end)
            if affected_syslib[address - 0x6000] == 0xE8
        )
    reviewed_incidental_e8_addresses = {
        affected_start + relative_offset
        for affected_start, offsets in SYSLIB_HECI_INCIDENTAL_E8_OFFSETS.items()
        for relative_offset in offsets
    }
    if (
        len(raw_e8_addresses) != 105
        or len(reviewed_call_addresses) != 96
        or len(reviewed_incidental_e8_addresses) != 9
        or raw_e8_addresses
        != reviewed_call_addresses | reviewed_incidental_e8_addresses
        or reviewed_call_addresses & reviewed_incidental_e8_addresses
    ):
        raise Failure("HECI/syslib direct-call instruction boundary drift")

    new_internal_targets: dict[int, tuple[int, int]] = {}
    external_gate_references = 0
    already_reviewed_references = 0
    for (affected_target, first_target), count in call_target_counts.items():
        if affected_target < 0x6000:
            if (affected_target, first_target) not in {
                (0x102E, 0x102E),
                (0x103D, 0x103D),
            }:
                raise Failure("HECI/syslib external direct-call target drift")
            external_gate_references += count
        elif affected_target in SYSLIB_HECI_DESTINATION_RANGES:
            expected_first = SYSLIB_HECI_DESTINATION_RANGES[affected_target][1]
            if first_target != expected_first:
                raise Failure("HECI/syslib already-reviewed direct-call target drift")
            already_reviewed_references += count
        else:
            previous = new_internal_targets.get(affected_target)
            if previous is not None and previous[0] != first_target:
                raise Failure("HECI/syslib inconsistent first-level target mapping")
            new_internal_targets[affected_target] = (
                first_target,
                (previous[1] if previous else 0) + count,
            )
    if (
        sum(call_target_counts.values()) != 96
        or len(call_target_counts) != 33
        or external_gate_references != 12
        or already_reviewed_references != 6
        or set(new_internal_targets) != set(SYSLIB_HECI_FIRST_LEVEL_CALLEE_RANGES)
        or sum(value[1] for value in new_internal_targets.values()) != 78
    ):
        raise Failure("HECI/syslib first-level call inventory drift")

    absolute_operand_specs = {
        0x06A95: (0x1F, 0x188B0, 0x188D4),
        0x081D1: (0x20E, 0x182BC, 0x182E0),
        0x08ED3: (0x25, 0x188B0, 0x188D4),
        0x0BE51: (0x39, 0x188B0, 0x188D4),
    }
    bodies = {}
    total_bytes = 0
    total_raw_differences = 0
    total_rel32_relocations = 0
    total_absolute_relocations = 0
    for affected_start in sorted(new_internal_targets):
        affected_end, expected_first_start, first_end = (
            SYSLIB_HECI_FIRST_LEVEL_CALLEE_RANGES[affected_start]
        )
        first_start, reference_count = new_internal_targets[affected_start]
        if first_start != expected_first_start:
            raise Failure("HECI/syslib first-level destination mapping drift")
        affected_body = affected_syslib[
            affected_start - 0x6000 : affected_end - 0x6000
        ]
        first_body = first_fixed_syslib[
            first_start - 0x6000 : first_end - 0x6000
        ]
        if not affected_body or len(affected_body) != len(first_body):
            raise Failure("HECI/syslib first-level body geometry drift")

        actual_differences = {
            index
            for index, (left, right) in enumerate(zip(affected_body, first_body))
            if left != right
        }
        allowed_differences: set[int] = set()
        normalized_affected = bytearray(affected_body)
        normalized_first = bytearray(first_body)
        rel32_relocations = []
        for offset in range(len(affected_body) - 4):
            opcode = affected_body[offset]
            if opcode not in (0xE8, 0xE9) or first_body[offset] != opcode:
                continue
            if affected_body[offset + 1 : offset + 5] == first_body[offset + 1 : offset + 5]:
                continue
            affected_target = (
                affected_start
                + offset
                + 5
                + struct.unpack_from("<i", affected_body, offset + 1)[0]
            )
            first_target = (
                first_start
                + offset
                + 5
                + struct.unpack_from("<i", first_body, offset + 1)[0]
            )
            if (
                affected_target,
                first_target,
            ) not in SYSLIB_HECI_FIRST_LEVEL_ALLOWED_REL32_TARGET_PAIRS:
                continue
            allowed_differences.update(range(offset + 1, offset + 5))
            normalized_affected[offset + 1 : offset + 5] = b"\0" * 4
            normalized_first[offset + 1 : offset + 5] = b"\0" * 4
            rel32_relocations.append({
                "affected_runtime_address": affected_start + offset,
                "first_fixed_runtime_address": first_start + offset,
                "opcode": opcode,
                "affected_target": affected_target,
                "first_fixed_target": first_target,
            })

        absolute_relocations = []
        if affected_start in absolute_operand_specs:
            operand_offset, affected_value_expected, first_value_expected = (
                absolute_operand_specs[affected_start]
            )
            affected_value = struct.unpack_from(
                "<I", affected_body, operand_offset
            )[0]
            first_value = struct.unpack_from("<I", first_body, operand_offset)[0]
            if (affected_value, first_value) != (
                affected_value_expected,
                first_value_expected,
            ):
                raise Failure("HECI/syslib first-level table-base drift")
            allowed_differences.update(range(operand_offset, operand_offset + 4))
            normalized_affected[operand_offset : operand_offset + 4] = b"\0" * 4
            normalized_first[operand_offset : operand_offset + 4] = b"\0" * 4
            absolute_relocations.append({
                "affected_operand_runtime_range": [
                    affected_start + operand_offset,
                    affected_start + operand_offset + 4,
                ],
                "first_fixed_operand_runtime_range": [
                    first_start + operand_offset,
                    first_start + operand_offset + 4,
                ],
                "affected_value": affected_value,
                "first_fixed_value": first_value,
                "instruction": "indexed table base",
            })

        if (
            not actual_differences <= allowed_differences
            or normalized_affected != normalized_first
        ):
            raise Failure("HECI/syslib first-level normalized body drift")
        bodies[f"0x{affected_start:x}"] = {
            "direct_reference_count": reference_count,
            "affected_runtime_range": [affected_start, affected_end],
            "first_fixed_runtime_range": [first_start, first_end],
            "size": len(affected_body),
            "affected_sha256": sha256(affected_body),
            "first_fixed_sha256": sha256(first_body),
            "raw_differing_byte_count": len(actual_differences),
            "rel32_relocations": rel32_relocations,
            "absolute_address_relocations": absolute_relocations,
            "normalized_sha256": sha256(bytes(normalized_affected)),
            "equal_after_reviewed_address_normalization": True,
        }
        total_bytes += len(affected_body)
        total_raw_differences += len(actual_differences)
        total_rel32_relocations += len(rel32_relocations)
        total_absolute_relocations += len(absolute_relocations)

    if (
        len(bodies) != 29
        or total_bytes != 3911
        or total_raw_differences != 34
        or total_rel32_relocations != 29
        or total_absolute_relocations != 4
    ):
        raise Failure("HECI/syslib first-level aggregate drift")
    return {
        "raw_0xe8_byte_count_in_42_bodies": len(raw_e8_addresses),
        "reviewed_direct_call_site_count": sum(call_target_counts.values()),
        "reviewed_incidental_0xe8_byte_count": len(reviewed_incidental_e8_addresses),
        "distinct_direct_call_target_pair_count": len(call_target_counts),
        "unchanged_external_gate_reference_count": external_gate_references,
        "already_reviewed_body_reference_count": already_reviewed_references,
        "new_internal_first_level_callee_reference_count": sum(
            value[1] for value in new_internal_targets.values()
        ),
        "new_internal_first_level_callee_count": len(bodies),
        "reviewed_callee_body_byte_count": total_bytes,
        "raw_differing_byte_count": total_raw_differences,
        "rel32_relocation_site_count": total_rel32_relocations,
        "absolute_address_relocation_site_count": total_absolute_relocations,
        "callee_bodies": bodies,
        "exact_static_observations": {
            "all_96_reviewed_direct_call_sites_resolved": True,
            "all_29_new_internal_first_level_callees_have_equal_reviewed_geometry": True,
            "all_29_new_internal_first_level_callees_equal_after_only_reviewed_address_normalization": True,
            "no_first_level_callee_body_has_an_opcode_or_non_address_data_change": True,
        },
        "attribution_boundary": "The 96 reviewed direct calls from HECI-imported syslib bodies resolve to two unchanged external gates, two already reviewed bodies, and 29 new internal first-level callee bodies. The 29 new bodies are unchanged after reviewed address normalization. This does not cover indirect calls/jumps, indexed dispatch targets, deeper callees not present in these next-entry-bounded bodies, kernel/service handlers behind the external gates, another signed module, or downstream HECI clients.",
    }


def first_fixed_heci_review(affected: bytes, first_fixed: bytes) -> dict:
    if sha256(affected) != OLD_HECI_SHA256 or sha256(first_fixed) != FIRST_FIXED_HECI_SHA256:
        raise Failure("first-fixed HECI identity drift")
    ranges = {
        name: call_relocation_only_range(
            affected,
            first_fixed,
            start,
            end,
            affected_digest,
            first_fixed_digest,
            call_sites,
            name,
        )
        for name, (
            start,
            end,
            affected_digest,
            first_fixed_digest,
            call_sites,
        ) in FIRST_FIXED_HECI_RANGES.items()
    }
    dispatcher = first_fixed[0x17C8:0x1DC9]
    signatures = {
        "nine_bit_length_mask": bytes.fromhex("66 25 ff 01"),
        "fragment_maximum_0x1fc": bytes.fromhex("81 fe fc 01 00 00"),
        "complete_bit_only_mask": bytes.fromhex("24 80"),
        "control_length_4_to_8": bytes.fromhex("8d 46 fc 83 f8 04"),
    }
    counts = {name: dispatcher.count(value) for name, value in signatures.items()}
    if any(count != 1 for count in counts.values()):
        raise Failure("first-fixed HECI validation signature drift")
    later_only = {
        "reject_header_bit_29": bytes.fromhex("f6 c2 20 75 ef"),
        "control_requires_bit31_and_rejects_bit28": bytes.fromhex("83 e2 90 80 fa 80"),
        "control_maximum_0x28": bytes.fromhex("8d 46 fc 83 f8 24"),
    }
    if any(dispatcher.count(value) for value in later_only.values()):
        raise Failure("later-only HECI signature unexpectedly present in first-fixed dispatcher")
    return {
        "code_base": 0x26000,
        "module_wide_relocation_review": module_wide_external_relocation_review(
            affected, first_fixed
        ),
        "instruction_ranges": ranges,
        "reviewed_signature_occurrences": counts,
        "later_only_signature_occurrences": {
            name: dispatcher.count(value) for name, value in later_only.items()
        },
        "exact_static_observations": {
            "entire_heci_module_equal_after_only_external_rel32_relocation_normalization": True,
            "three_primary_receive_ranges_equal_after_only_rel32_call_relocation_normalization": True,
            "first_fixed_retains_nine_bit_fragment_length_and_0x1fc_maximum": True,
            "first_fixed_retains_complete_bit_only_header_test": True,
            "first_fixed_retains_control_payload_bound_of_4_to_8_bytes": True,
            "later_bit_29_rejection_absent": True,
            "later_bit_28_control_rejection_absent": True,
            "later_40_byte_control_bound_absent": True,
        },
        "advisory_attribution": "The entire affected and first-fixed HECI modules become byte-identical after normalizing only 369 external rel32 call/jump immediates; all 377 raw differing bytes lie inside those immediates, and every target moves by exactly five bytes within the external 0x6460..0x67b2 stub range. No HECI-local opcode or data change implements the 3.1.55 fix. The exact defect may instead involve changed external syslib behavior or another signed module/client.",
    }


def later_heci_review(heci: bytes) -> dict:
    if sha256(heci) != LATER_HECI_SHA256:
        raise Failure("later HECI identity drift")
    signatures = {
        "nine_bit_length_mask": bytes.fromhex("66 25 ff 01"),
        "fragment_maximum_0x1fc": bytes.fromhex("81 fe fc 01 00 00"),
        "reject_header_bit_29": bytes.fromhex("f6 c2 20 75 ef"),
        "control_requires_bit31_and_rejects_bit28": bytes.fromhex("83 e2 90 80 fa 80"),
        "control_maximum_0x28": bytes.fromhex("8d 46 fc 83 f8 24"),
    }
    receive_dispatch = heci[0x189A:0x1EF8]
    counts = {name: receive_dispatch.count(value) for name, value in signatures.items()}
    if any(count != 1 for count in counts.values()):
        raise Failure("fixed HECI reviewed validation signature drift")
    ranges = {
        name: checked_range(heci, start, end, digest, name)
        for name, (start, end, digest) in LATER_HECI_RANGES.items()
    }
    return {
        "code_base": 0x26000,
        "instruction_ranges": ranges,
        "reviewed_signature_occurrences": counts,
        "exact_static_observations": {
            "nine_bit_fragment_length_retained": True,
            "fragment_length_above_0x1fc_rejected": True,
            "dma_ring_bit_29_now_rejected_before_payload_dispatch": True,
            "control_header_now_requires_bit_31_and_rejects_extended_bit_28": True,
            "control_payload_bound_changed_from_4_to_8_bytes_to_4_to_40_bytes": True,
            "bit_28_extended_header_parser_added": True,
            "extended_header_parser_checks_encoded_size_against_payload_and_0x1fc_destination": True,
            "extended_header_parser_requires_exact_single_entry_geometry": True,
            "primary_payload_copy_still_uses_0x1fc_destination_bound": True,
        },
        "advisory_attribution": "The later image adds stricter reserved/header-bit validation and a bounded extended-header parser. Exact first-fixed comparison shows the primary 3.1.55 path retains the affected behavior, so these 3.1.94 changes postdate and are not the first-fixed primary-path repair.",
    }


def later_fpf_review(affected: bytes, first_fixed: bytes, later: bytes) -> dict:
    if (
        sha256(affected) != OLD_FPF_SHA256
        or sha256(first_fixed) != FIRST_FIXED_FPF_SHA256
        or sha256(later) != LATER_FPF_SHA256
    ):
        raise Failure("FPF identity drift")
    fields = {}
    for name, (offset, width, bit_start, bit_end, digest) in LATER_FPF_ARB_FIELDS.items():
        record = later[offset : offset + 0x2C]
        record_name = record[:12].split(b"\0", 1)[0]
        parsed_width = struct.unpack_from("<I", record, 0x14)[0] if len(record) == 0x2C else -1
        parsed_start, parsed_end = struct.unpack_from("<HH", record, 0x1C) if len(record) == 0x2C else (-1, -1)
        if (
            record_name != name.encode("ascii")
            or parsed_width != width
            or (parsed_start, parsed_end) != (bit_start, bit_end)
            or parsed_end - parsed_start + 1 != parsed_width
            or sha256(record) != digest
            or affected.count(name.encode("ascii")) != 0
            or first_fixed.count(name.encode("ascii")) != 0
        ):
            raise Failure(f"fixed FPF anti-rollback field drift: {name}")
        fields[name] = {
            "record_file_range": [offset, offset + 0x2C],
            "record_sha256": digest,
            "width_bits": width,
            "field_bit_range_inclusive": [bit_start, bit_end],
            "affected_literal_occurrences": 0,
            "first_fixed_literal_occurrences": 0,
            "later_literal_occurrences": later.count(name.encode("ascii")),
        }
    if any(value["later_literal_occurrences"] != 1 for value in fields.values()):
        raise Failure("fixed FPF anti-rollback field multiplicity drift")
    return {
        "fields": fields,
        "exact_static_observations": {
            "affected_fpf_lacks_all_six_field_names": True,
            "first_fixed_fpf_lacks_all_six_field_names": True,
            "later_fpf_contains_all_six_structured_field_records": True,
            "later_enable_fields_are_two_bits_each": True,
            "later_svn_fields_are_contiguous_12_20_and_14_bit_ranges": True,
        },
        "advisory_attribution": "The later signed FPF contains explicit RBE, OEM key-manifest, and microcode anti-rollback enable/SVN field records absent by name from both affected and first-fixed signed FPF. These fields were not the 3.1.55 fix. This does not establish when they appeared, whether they were provisioned, or what exact storage/anti-replay defect CVE-2018-3655 repaired.",
    }


def rel32_target(module_base: int, module: bytes, offset: int, opcode: int) -> int:
    if module[offset] != opcode:
        raise Failure(f"rel32 opcode drift at 0x{module_base + offset:x}")
    return module_base + offset + 5 + struct.unpack_from("<i", module, offset + 1)[0]


def first_fixed_vfs_review(
    affected_vfs: bytes,
    first_fixed_vfs: bytes,
    affected_syslib: bytes,
    first_fixed_syslib: bytes,
    affected_storage_report: dict,
    first_fixed_storage_report: dict,
) -> dict:
    if (
        sha256(affected_vfs) != OLD_VFS_SHA256
        or sha256(first_fixed_vfs) != FIRST_FIXED_VFS_SHA256
        or len(affected_vfs) != 0x1D000
        or len(first_fixed_vfs) != 0x1F000
    ):
        raise Failure("first-fixed VFS identity drift")
    paths = (b"/dev/ndl_critical", b"/dev/ndl_counting")
    if any(affected_vfs.count(path) != 0 or first_fixed_vfs.count(path) != 1 for path in paths):
        raise Failure("first-fixed VFS NDL path drift")
    init_range = first_fixed_vfs[0x1055F:0x105AA]
    if sha256(init_range) != "fe4f7355232906a4402174f535a32b292b0c263c8c1552f00e42cb6bc319c675":
        raise Failure("first-fixed VFS NDL initializer drift")
    storage_names = ("ndl_critical", "ndl_counting")
    for report in (affected_storage_report, first_fixed_storage_report):
        occurrences = report.get("reviewed_special_file_occurrences", {})
        if any(occurrences.get(name) != 1 for name in storage_names):
            raise Failure("storage NDL special-file metadata drift")
    if (
        rel32_target(0x26000, first_fixed_vfs, 0x1059C, 0xE8) != 0x6451
        or rel32_target(0x6000, affected_syslib, 0x451, 0xE9) != 0x16689
        or rel32_target(0x6000, first_fixed_syslib, 0x451, 0xE9) != 0x16691
        or rel32_target(0x6000, first_fixed_syslib, 0x456, 0xE9) != 0x166AB
    ):
        raise Failure("first-fixed VFS/syslib NDL binding drift")
    setter = first_fixed_syslib[0x10691:0x106AB]
    if sha256(setter) != "31433029861d3307d6f82d871b5356220452e18f390306d408ea1abb0256920c":
        raise Failure("first-fixed syslib NDL setter drift")
    critical_names = (
        "fTDisClear", "fTReadOnly", "fTEnrsHier", "RsaKeyCache1", "RsaKeyCache2",
        "RsaKeyCache3", "RsaKeyCache4", "RsaKeyCache5", "pr_tee_clock",
        "lspcon_cert", "hdcp_srm_ver", "widi_srm_ver", "wv_gen_num", "widi_km0",
        "widi_km1", "widi_km2", "widi_km3", "widi_km4", "widi_km5", "widi_km6",
        "widi_km7", "widi_km8", "widi_km9", "wv_gen_num", "pnd_m4_msg",
    )
    if any(affected_vfs.count(b"\0" + name.encode("ascii") + b"\0") != 0 for name in set(critical_names)):
        raise Failure("affected VFS unexpectedly contains first-fixed bare critical-name table")
    pointer_array = first_fixed_vfs[0x11154:0x111B8]
    recovered_names = []
    for index in range(25):
        address = struct.unpack_from("<I", pointer_array, index * 4)[0]
        offset = address - 0x26000
        if offset < 0 or offset >= len(first_fixed_vfs):
            raise Failure("first-fixed VFS critical-name pointer out of range")
        end = first_fixed_vfs.find(b"\0", offset, min(offset + 32, len(first_fixed_vfs)))
        if end < 0:
            raise Failure("first-fixed VFS critical-name terminator missing")
        recovered_names.append(first_fixed_vfs[offset:end].decode("ascii"))
    if tuple(recovered_names) != critical_names:
        raise Failure("first-fixed VFS critical-name table drift")
    classifier = first_fixed_vfs[0xDB0A:0xDB6B]
    if (
        sha256(pointer_array) != "dd0ed2254567b2c42599b10f00890e8b387b936905cc02bfbecb8421c5dde693"
        or sha256(classifier) != "cf68f0c685de3283670936fe1c3cfbe8e2e19c525b61663891b08a807fb4a42d"
    ):
        raise Failure("first-fixed VFS critical-name classifier drift")
    return {
        "affected_vfs": {
            "size": len(affected_vfs),
            "sha256": OLD_VFS_SHA256,
            "ndl_path_occurrences": {path.decode("ascii"): 0 for path in paths},
        },
        "first_fixed_vfs": {
            "size": len(first_fixed_vfs),
            "sha256": FIRST_FIXED_VFS_SHA256,
            "ndl_path_occurrences": {path.decode("ascii"): 1 for path in paths},
            "initializer_runtime_range": [0x3655F, 0x365AA],
            "initializer_sha256": sha256(init_range),
            "syslib_setter_call_runtime_address": 0x3659C,
            "syslib_setter_stub_target": 0x6451,
            "critical_name_pointer_array_runtime_range": [0x37154, 0x371B8],
            "critical_name_pointer_array_sha256": sha256(pointer_array),
            "critical_name_classifier_runtime_range": [0x33B0A, 0x33B6B],
            "critical_name_classifier_sha256": sha256(classifier),
            "critical_name_table": recovered_names,
        },
        "storage_metadata": {
            "affected_defines_both_ndl_special_files": True,
            "first_fixed_defines_both_ndl_special_files": True,
        },
        "first_fixed_syslib": {
            "new_or_reassigned_stub_address": 0x6451,
            "new_setter_runtime_range": [0x16691, 0x166AB],
            "new_setter_sha256": sha256(setter),
            "next_shifted_legacy_stub_address": 0x6456,
            "next_shifted_legacy_target": 0x166AB,
        },
        "exact_static_observations": {
            "storage_special_files_predate_first_fixed": True,
            "first_fixed_vfs_adds_both_ndl_path_consumers": True,
            "first_fixed_vfs_opens_both_ndl_paths_and_passes_results_to_new_syslib_setter": True,
            "first_fixed_syslib_setter_updates_thread_context_flag_and_two_descriptor_fields": True,
            "first_fixed_vfs_adds_25_entry_critical_name_table_absent_from_affected_vfs": True,
            "critical_name_classifier_performs_bounded_12_byte_comparisons": True,
        },
        "advisory_attribution": "This is an exact first-fixed VFS/syslib integration delta for pre-existing ndl_critical and ndl_counting storage channels, accompanied by a new 25-entry critical-name table. Its names and timing make it a high-priority CVE-2018-3655 anti-replay/data-file-integrity candidate, but exact transaction semantics, physical reachability, and advisory attribution are not yet proved.",
    }


def image_report(image: bytes, nftp_offset: int, ftpr_offset: int, label: str) -> tuple[dict, dict[str, bytes]]:
    nftp_entries = parse_cpd(image, nftp_offset, b"NFTP")
    ftpr_entries = parse_cpd(image, ftpr_offset, b"FTPR")
    nftp_manifest = member(image, nftp_offset, nftp_entries, "NFTP.man")
    ftpr_manifest = member(image, ftpr_offset, ftpr_entries, "FTPR.man")
    report = {
        "label": label,
        "size": len(image),
        "sha256": sha256(image),
        "nftp_cpd_offset": nftp_offset,
        "ftpr_cpd_offset": ftpr_offset,
        "nftp_manifest": verify_mn2(nftp_manifest, f"{label} NFTP.man"),
        "ftpr_manifest": verify_mn2(ftpr_manifest, f"{label} FTPR.man"),
        "modules": {},
    }
    values: dict[str, bytes] = {}
    for name in MODULES:
        values[name], report["modules"][name] = extract_module(
            image, nftp_offset, nftp_entries, nftp_manifest, name
        )
    values["syslib"], report["modules"]["syslib"] = extract_syslib(
        image, ftpr_offset, ftpr_entries, ftpr_manifest
    )
    return report, values


def build_report(old: bytes, first_fixed: bytes, later: bytes) -> dict:
    if sha256(old) != OLD_SHA256:
        raise Failure("affected ABL identity mismatch")
    if sha256(first_fixed) != FIRST_FIXED_SHA256:
        raise Failure("first-fixed IFWI identity mismatch")
    if sha256(later) != LATER_SHA256:
        raise Failure("later IFWI identity mismatch")
    old_report, old_modules = image_report(old, OLD_NFTP, OLD_FTPR, "affected-eu-abl")
    first_report, first_modules = image_report(
        first_fixed,
        FIRST_FIXED_NFTP,
        FIRST_FIXED_FTPR,
        "first-fixed-asus-x541na-ifwi",
    )
    later_report, later_modules = image_report(
        later,
        LATER_NFTP,
        LATER_FTPR,
        "later-public-apl-ifwi",
    )
    if sha256(old_modules["heci"]) != OLD_HECI_SHA256:
        raise Failure("affected HECI identity drift")
    comparisons = {
        "affected_to_first_fixed": {
            name: byte_comparison(old_modules[name], first_modules[name])
            for name in sorted(old_modules)
        },
        "first_fixed_to_later": {
            name: byte_comparison(first_modules[name], later_modules[name])
            for name in sorted(old_modules)
        },
        "affected_to_later": {
            name: byte_comparison(old_modules[name], later_modules[name])
            for name in sorted(old_modules)
        },
    }
    return {
        "schema": SCHEMA,
        "inputs": {
            "affected": old_report,
            "first_fixed": first_report,
            "later": later_report,
        },
        "comparisons": comparisons,
        "first_fixed_heci_exact_static_review": first_fixed_heci_review(
            old_modules["heci"], first_modules["heci"]
        ),
        "first_fixed_busdrv_exact_static_review": first_fixed_busdrv_review(
            old_modules["busdrv"], first_modules["busdrv"]
        ),
        "first_fixed_heci_syslib_import_review": first_fixed_heci_syslib_import_review(
            old_modules["heci"],
            first_modules["heci"],
            old_modules["syslib"],
            first_modules["syslib"],
        ),
        "first_fixed_heci_syslib_first_level_callee_review": first_fixed_heci_syslib_first_level_callee_review(
            old_modules["syslib"],
            first_modules["syslib"],
        ),
        "first_fixed_vfs_exact_static_review": first_fixed_vfs_review(
            old_modules["vfs"],
            first_modules["vfs"],
            old_modules["syslib"],
            first_modules["syslib"],
            old_report["modules"]["storage"],
            first_report["modules"]["storage"],
        ),
        "later_heci_exact_static_review": later_heci_review(later_modules["heci"]),
        "later_fpf_exact_static_review": later_fpf_review(
            old_modules["fpf"], first_modules["fpf"], later_modules["fpf"]
        ),
        "classification": {
            "exact_signed_first_fixed_3_1_55_build_obtained": True,
            "exact_signed_later_modules_obtained": True,
            "first_fixed_entire_heci_module_changes_only_external_rel32_immediates": True,
            "first_fixed_entire_busdrv_module_changes_only_external_rel32_call_immediates": True,
            "first_fixed_primary_heci_ranges_change_only_rel32_call_immediates": True,
            "first_fixed_all_42_heci_imported_syslib_bodies_change_only_address_operands": True,
            "first_fixed_all_29_new_first_level_syslib_callees_change_only_address_operands": True,
            "later_heci_header_and_extended_parser_changes_are_the_3_1_55_fix": False,
            "later_fpf_named_anti_rollback_fields_are_the_3_1_55_fix": False,
            "first_fixed_vfs_ndl_integration_candidate_identified": True,
            "cve_2018_12147_exact_bug_identified": False,
            "cve_2018_3655_exact_storage_bug_identified": False,
            "simple_oversized_nine_bit_fragment_overflow_observed": False,
        },
        "boundaries": [
            "The official ASUS first-fixed image closes the version-bisect gap for 3.1.55, but attribution still requires exact changed-function and reachability analysis.",
            "The reviewed primary HECI ranges exclude later header/extension changes as the first-fixed primary-path delta; they do not exclude another HECI function or downstream client parser.",
            "The complete busdrv module also normalizes to byte identity after only 96 external rel32 call displacements are zeroed. All 26 affected targets are syslib import stubs and their first-fixed targets are affected plus five, excluding a busdrv-local opcode or non-address-data fix while leaving its transitive services open.",
            "All 42 syslib bodies directly imported by HECI normalize to byte identity after only reviewed address operands are zeroed. Their 96 reviewed direct calls resolve to two unchanged external gates, two already reviewed bodies, and 29 new internal first-level callee bodies; all 29 new bodies also normalize to identity. This excludes opcode/non-address-data changes in those bounded bodies, but not indirect dispatch, deeper callees, kernel/service handlers, another signed module, or a downstream client.",
            "The named later FPF anti-rollback fields are absent from both affected and first-fixed FPF; this excludes those records as the 3.1.55 fix.",
            "First-fixed VFS newly opens pre-existing ndl_critical and ndl_counting storage channels and passes their descriptors to a new syslib setter. This is an exact anti-replay/data-integrity candidate, not yet proof of CVE-2018-3655 attribution or physical reachability.",
            "Embedded $MN2 verification proves self-consistency and byte binding only, not platform ROM, fuse, Boot Guard, or OEM acceptance.",
            "This is passive host-side parsing and exact-static comparison; no CSE module or host HECI endpoint was executed or opened.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--affected-abl", type=Path, required=True)
    parser.add_argument("--first-fixed-ifwi", type=Path, required=True)
    parser.add_argument("--later-ifwi", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(
            stable_read(args.affected_abl),
            stable_read(args.first_fixed_ifwi),
            stable_read(args.later_ifwi),
        )
    except (Failure, OSError, struct.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    encoded = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
