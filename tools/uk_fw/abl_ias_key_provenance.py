#!/usr/bin/env python3
"""Freeze the exact FIT/OEM-key-manifest handoff used by ABL IAS verification."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import subprocess
import sys
import tarfile
from pathlib import Path

SCHEMA = "abl-ias-key-provenance/v1"
VERSION = "1.0.0"
UPDATE_SIZE = 42_101_042
UPDATE_SHA256 = "1e67344a714708733a9158a52ef5d4def95b126e5725d070669ea64e0644c4c8"
ABL_MEMBER = "abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin"
ABL_SIZE = 8_388_608
ABL_SHA256 = "f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac"
IBBL_SHA256 = "394c442368c67f82f17e84854575bf07abafac2b8fbf2fda7dca68b182f91b93"
STAGE1_SHA256 = "3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2"
CANDIDATE_OS_KEY_DIGEST = "437008c1b26fd821a7c7c0ec855aaba5587f62deaaa98d9b2fcbf6ad4179aa06"
OEM_KEY_OFFSET = 0x17C000
OEM_KEY_SIZE = 0x61C
OEM_KEY_SHA256 = "a72a5d867185852be1466a9d3d2e97bb11bd6b0a89b48f5454220def946814bd"
STORED_USAGE39_DIGEST = "9b0a59c842ba70857b595ed8115630d3a342a10c9d4437f9ff4807517693e0af"
SBL_COMMIT = "5f5c14b10ae6bd3cd0cf7e274142767dc2635a06"
SBL_FILE = "BootloaderCorePkg/Include/FirmwareInterfaceTable.h"
SBL_FILE_SHA256 = "0e0f1fff576e4edc48d2918d14bb1292526d3c01d3547d38305ea435543722ef"
MEA_COMMIT = "d27ccdba0aadbad490f47b5b631c369b682a7ef5"
MEA_FILE = "MEA.py"
MEA_FILE_SHA256 = "ed2dfb3b9efe58431609b4d3eefe6908b3124228288163dd4fd667dd17d5f4ef"
IBBL_RANGES = {
    "fit_payload_relocator": (0x40, 0xF3, "688cec0863886aa5a7ca6ed5cb1b9333c8112cd1babb4af2c79a07ebb80cb35a"),
    "fit_table_validator_and_copy": (0xF3, 0x171, "a83c5a32fb4e8b8157769332a6f27ba7484b1e55948228b1ce9cd45e0fb41ea8"),
    "source_fit_handoff_copy": (0x4EF, 0x54C, "c3bd36e3b536f906633be18e362f7744bd845bb505cf11eff8b4af0e46ee4b19"),
}
STAGE1_RANGES = {
    "ias_key_and_payload_auth": (0x157A3, 0x159FE, "4b71d5c95ff2bcf4210ba23a96883f3ce3524fb31b40f037a00991a6c14a7f30"),
    "oemkm_command_line_export": (0xBEA5, 0xBF10, "f37111948019b765312545efc1c3472d488b4fef7a3a322f86e5df92a722e40b"),
}


class Failure(Exception):
    pass


def canonical(name: str) -> str | None:
    if name == ".":
        return None
    if not isinstance(name, str) or not name or name.startswith("/") or "\\" in name or "\0" in name:
        raise Failure("unsafe archive member spelling")
    parts = name.split("/")
    if parts and parts[0] == ".":
        parts = parts[1:]
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise Failure("unsafe archive member component")
    return "/".join(parts)


def _identity(st: os.stat_result) -> tuple[int, int, int, int, int]:
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


def archive_one(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise Failure(f"cannot safely open archive: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size != UPDATE_SIZE:
            raise Failure("archive size/type mismatch")
        digest = hashlib.sha256()
        left = UPDATE_SIZE
        while left:
            chunk = os.read(fd, min(left, 1 << 20))
            if not chunk:
                raise Failure("short archive read")
            digest.update(chunk)
            left -= len(chunk)
        if digest.hexdigest() != UPDATE_SHA256 or _identity(before) != _identity(os.fstat(fd)):
            raise Failure("archive identity mismatch")
        os.lseek(fd, 0, os.SEEK_SET)
        found: list[bytes] = []
        with os.fdopen(os.dup(fd), "rb") as stream:
            try:
                with tarfile.open(fileobj=stream, mode="r:gz") as archive:
                    seen: set[str] = set()
                    for member in archive:
                        name = canonical(member.name)
                        if name is None:
                            continue
                        if name in seen:
                            raise Failure("duplicate canonical archive identity")
                        seen.add(name)
                        if name != ABL_MEMBER:
                            continue
                        if (
                            not member.isreg()
                            or member.size != ABL_SIZE
                            or member.mode & 0o7777 != 0o755
                            or member.uid != 8100
                            or member.gid != 8100
                        ):
                            raise Failure("selected ABL member metadata drift")
                        source = archive.extractfile(member)
                        if source is None:
                            raise Failure("selected ABL member unreadable")
                        data = source.read(ABL_SIZE + 1)
                        if len(data) != ABL_SIZE or hashlib.sha256(data).hexdigest() != ABL_SHA256:
                            raise Failure("selected ABL member content drift")
                        found.append(data)
            except (tarfile.TarError, OSError, EOFError) as exc:
                raise Failure(f"archive parse failure: {exc}") from exc
        if len(found) != 1 or _identity(before) != _identity(os.fstat(fd)):
            raise Failure("selected ABL multiplicity/change")
        return found[0]
    finally:
        os.close(fd)


def lz4_block(raw: bytes, expected: int) -> bytes:
    pos = 0
    out = bytearray()
    while len(out) < expected:
        if pos >= len(raw):
            raise Failure("truncated ABL LZ4 token")
        token = raw[pos]
        pos += 1
        literal = token >> 4
        if literal == 15:
            while True:
                if pos >= len(raw):
                    raise Failure("truncated ABL LZ4 literal length")
                value = raw[pos]
                pos += 1
                literal += value
                if value != 255:
                    break
        if pos + literal > len(raw) or len(out) + literal > expected:
            raise Failure("ABL LZ4 literal bounds drift")
        out += raw[pos : pos + literal]
        pos += literal
        if len(out) == expected:
            break
        if pos + 2 > len(raw):
            raise Failure("truncated ABL LZ4 offset")
        offset = raw[pos] | raw[pos + 1] << 8
        pos += 2
        if offset == 0 or offset > len(out):
            raise Failure("invalid ABL LZ4 offset")
        match = (token & 15) + 4
        if (token & 15) == 15:
            while True:
                if pos >= len(raw):
                    raise Failure("truncated ABL LZ4 match length")
                value = raw[pos]
                pos += 1
                match += value
                if value != 255:
                    break
        if len(out) + match > expected:
            raise Failure("ABL LZ4 match bounds drift")
        for _ in range(match):
            out.append(out[-offset])
    if pos != len(raw):
        raise Failure("ABL LZ4 trailing compressed bytes")
    return bytes(out)


def git_blob(repo: Path, commit: str, name: str, wanted: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show", f"{commit}:{name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Failure(f"git source read failed: {exc}") from exc
    if result.returncode or hashlib.sha256(result.stdout).hexdigest() != wanted:
        raise Failure(f"public source identity mismatch: {name}")
    return result.stdout


def require_once(source: bytes, needle: bytes, label: str) -> None:
    if source.count(needle) != 1:
        raise Failure(f"public source semantic anchor multiplicity: {label}")


def extract_ibb(abl: bytes) -> tuple[bytes, bytes]:
    if struct.unpack_from("<IIBBBBI", abl, 0x187000)[:6] != (0x44504324, 4, 1, 1, 16, 50):
        raise Failure("IBB CPD drift")
    entries = []
    for index in range(4):
        name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, 0x187010 + index * 24)
        entries.append((name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    expected = [
        ("IBBP.man", 0x70, 0x2EC),
        ("BPM.met", 0x380, 0xB4),
        ("IBBL", 0x440, 0x4000),
        ("IBB", 0x4440, 0x34000),
    ]
    if entries != expected:
        raise Failure("IBB CPD entries drift")
    ibbl = abl[0x187000 + 0x440 : 0x187000 + 0x440 + 0x4000]
    if hashlib.sha256(ibbl).hexdigest() != IBBL_SHA256:
        raise Failure("IBBL identity drift")
    ias = 0x187000 + 0x4440
    header = struct.unpack_from("<7I", abl, ias)
    if header != (0x2E6B7069, 0, 0, 0x33CD4, 0x2C, 0x33CD4, 0xF753ACFA):
        raise Failure("IBB IAS header drift")
    sizes = struct.unpack_from("<4I", abl, ias + 0x1C)
    if sizes != (0xC0, 0x172D2, 0x44A9, 0x18493):
        raise Failure("IBB subimage table drift")
    pos = ias + 0x2C
    subimages = []
    for index, size in enumerate(sizes):
        subimages.append(abl[pos : pos + size])
        pos += size
        if index + 1 < len(sizes):
            pos = (pos + 3) & ~3
    packed = subimages[1]
    output_size = struct.unpack_from("<I", packed)[0]
    if output_size != 0x1FE00:
        raise Failure("stage-1 output size drift")
    stage1 = lz4_block(packed[4:-4], output_size)
    if hashlib.sha256(stage1).hexdigest() != STAGE1_SHA256:
        raise Failure("stage-1 identity drift")
    return ibbl, stage1


def check_ranges(data: bytes, ranges: dict[str, tuple[int, int, str]], label: str) -> dict[str, dict]:
    result = {}
    for name, (start, end, digest) in ranges.items():
        if end > len(data) or hashlib.sha256(data[start:end]).hexdigest() != digest:
            raise Failure(f"{label} instruction range drift: {name}")
        result[name] = {"file_start": start, "file_end": end, "sha256": digest}
    return result


def parse_stored_oem_key(abl: bytes) -> dict:
    cpd = 0x11E000
    if struct.unpack_from("<IIBBBBI", abl, cpd)[:6] != (0x44504324, 12, 1, 1, 16, 150):
        raise Failure("FTPR CPD drift")
    entries = []
    for index in range(12):
        raw_name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, cpd + 0x10 + index * 24)
        entries.append((raw_name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    matches = [entry for entry in entries if entry[0] == "oem.key"]
    if matches != [("oem.key", 0x5E000, OEM_KEY_SIZE)]:
        raise Failure("FTPR oem.key entry drift")
    absolute = cpd + matches[0][1]
    if absolute != OEM_KEY_OFFSET:
        raise Failure("FTPR oem.key absolute offset drift")
    manifest = abl[absolute : absolute + OEM_KEY_SIZE]
    if len(manifest) != OEM_KEY_SIZE or hashlib.sha256(manifest).hexdigest() != OEM_KEY_SHA256:
        raise Failure("stored oem.key identity drift")
    header_type, header_subtype = struct.unpack_from("<HH", manifest, 0)
    header_size = struct.unpack_from("<I", manifest, 4)[0] * 4
    header_version = struct.unpack_from("<I", manifest, 8)[0]
    vendor_id = struct.unpack_from("<I", manifest, 0x10)[0]
    manifest_size = struct.unpack_from("<I", manifest, 0x18)[0] * 4
    tag = manifest[0x1C:0x20]
    public_key_size = struct.unpack_from("<I", manifest, 0x78)[0] * 4
    exponent_size = struct.unpack_from("<I", manifest, 0x7C)[0] * 4
    if (
        (header_type, header_subtype, header_size, header_version, vendor_id, manifest_size, tag)
        != (4, 0, 0x284, 0x10000, 0x8086, OEM_KEY_SIZE, b"$MN2")
        or public_key_size != 0x100
        or exponent_size != 4
    ):
        raise Failure("stored oem.key manifest header drift")
    modulus = manifest[0x80:0x180]
    exponent_bytes = manifest[0x180:0x184]
    signature = manifest[0x184:0x284]
    exponent = int.from_bytes(exponent_bytes, "little")
    signed_data = manifest[:0x80] + manifest[header_size:manifest_size]
    signed_digest = hashlib.sha256(signed_data).digest()
    encoded = pow(int.from_bytes(signature, "little"), exponent, int.from_bytes(modulus, "little")).to_bytes(
        public_key_size, "big"
    )
    separator = encoded.find(b"\0", 2)
    signature_valid = (
        encoded.startswith(b"\0\1")
        and separator >= 10
        and encoded[2:separator] == b"\xff" * (separator - 2)
        and encoded[separator + 1 :] == bytes.fromhex("3031300d060960864801650304020105000420") + signed_digest
    )
    if not signature_valid:
        raise Failure("stored oem.key embedded RSA signature failure")
    extension_tag, extension_size = struct.unpack_from("<II", manifest, 0x284)
    key_type = struct.unpack_from("<I", manifest, 0x28C)[0]
    if (extension_tag, extension_size, key_type) != (0x0E, 0x398, 2):
        raise Failure("stored oem.key extension-14 drift")
    if (extension_size - 0x24) % 0x44:
        raise Failure("stored oem.key entry geometry drift")
    records = []
    for index in range((extension_size - 0x24) // 0x44):
        offset = 0x2A8 + index * 0x44
        usage = [bit for bit in range(128) if manifest[offset + bit // 8] & (1 << (bit & 7))]
        flags = manifest[offset + 0x20]
        algorithm = manifest[offset + 0x21]
        digest_size = struct.unpack_from("<H", manifest, offset + 0x22)[0]
        digest = manifest[offset + 0x24 : offset + 0x44].hex()
        if len(usage) != 1 or flags != 0 or algorithm != 2 or digest_size != 0x20:
            raise Failure("stored oem.key record drift")
        records.append({"index": index, "usage_bits": usage, "digest": digest})
    selected = [record for record in records if record["usage_bits"] == [39]]
    if len(selected) != 1 or selected[0]["digest"] != STORED_USAGE39_DIGEST:
        raise Failure("stored oem.key usage-39 record drift")
    manifest_key_digest = hashlib.sha256(modulus + exponent_bytes).hexdigest()
    if manifest_key_digest != STORED_USAGE39_DIGEST:
        raise Failure("stored oem.key self-key digest drift")
    return {
        "cpd": "FTPR",
        "cpd_offset": cpd,
        "member": "oem.key",
        "member_cpd_offset": matches[0][1],
        "flash_offset": absolute,
        "size": len(manifest),
        "sha256": OEM_KEY_SHA256,
        "manifest": {
            "tag": "$MN2",
            "header_size": header_size,
            "total_size": manifest_size,
            "vendor_id": vendor_id,
            "public_key_size": public_key_size,
            "exponent": exponent,
            "embedded_signature": "RSA-2048 PKCS#1 v1.5 SHA-256",
            "embedded_signature_valid": signature_valid,
            "embedded_signature_boundary": "self-consistency only; no external root established",
        },
        "extension": {
            "tag": extension_tag,
            "size": extension_size,
            "key_type": key_type,
            "record_count": len(records),
            "usage39_record": selected[0],
            "manifest_public_key_digest": manifest_key_digest,
            "usage39_digest_equals_manifest_public_key_digest": selected[0]["digest"] == manifest_key_digest,
        },
    }


def analyze(update: Path, sbl_repo: Path, mea_repo: Path) -> dict:
    abl = archive_one(update)
    ibbl, stage1 = extract_ibb(abl)
    stored_oem_key = parse_stored_oem_key(abl)
    ibbl_ranges = check_ranges(ibbl, IBBL_RANGES, "IBBL")
    stage_ranges = check_ranges(stage1, STAGE1_RANGES, "stage-1")

    # Fixed exact instruction and string anchors within the hash-bound ranges.
    exact_sequences = (
        (
            ibbl,
            0x4F0,
            "ba0000f8fe89e5b8c0100c0057e8f1fbffffba02000000b8c0100c00",
            "IBBL FIT source/destination/copy sequence",
        ),
        (ibbl, 0xFE, "817a045f2020207519813a5f4649547511", "IBBL _FIT_ signature check"),
        (ibbl, 0x118, "8d42ff83f814760d", "IBBL FIT count bound"),
        (
            ibbl,
            0x149,
            "c6460e7f8d44031089068d42018b530825ffffff0081e2000000ff09d089430889d8",
            "IBBL appended FIT entry/count sequence",
        ),
        (
            stage1,
            0x157DD,
            "a1c8100c008b1d60100c0025ffffff00c685a6fdffff0089858cfdffffa164100c008985a8fdffff89c8c1e80383e107898590fdffffb801000000d3e0898588fdffffb9c0100c00c685a7fdffff00c78598fdffff000000008bbd8cfdffff39bd98fdffff0f8dd90000008a410e83e07f3c0b740bff8598fdffff83c110ebd9",
            "stage-1 FIT type-0x0b traversal",
        ),
    )
    for source, offset, encoded, label in exact_sequences:
        sequence = bytes.fromhex(encoded)
        if source[offset : offset + len(sequence)] != sequence:
            raise Failure(f"{label} drift")
    if stage1.find(b"%x@%x\0") != 0x1C85B or stage1.find(b"ABL.oemkm\0") != 0x1C861:
        raise Failure("ABL.oemkm command-line strings drift")
    if stage1[0xC1E4:0xC1E6] != b"\x6a\x27":
        raise Failure("type-3 OS selector drift")

    fit_source = git_blob(sbl_repo, SBL_COMMIT, SBL_FILE, SBL_FILE_SHA256)
    require_once(fit_source, b"#define FIT_TYPE_0B_KEY_MANIFEST            0x0B", "FIT type 0x0b")
    require_once(fit_source, b"#define FIT_TYPE_10_CSE_SECURE_BOOT         0x10", "FIT type 0x10")
    require_once(fit_source, b"#define FIT_TYPE_00_SIGNATURE  SIGNATURE_64 ('_', 'F', 'I', 'T', '_', ' ', ' ', ' ')", "FIT signature")
    require_once(fit_source, b"UINT8  Size[3];", "FIT 24-bit size")
    require_once(fit_source, b"UINT8  Type : 7;", "FIT 7-bit type")

    mea_source = git_blob(mea_repo, MEA_COMMIT, MEA_FILE, MEA_FILE_SHA256)
    start = mea_source.find(b"class CSE_Ext_0E_Mod(ctypes.LittleEndianStructure)")
    end = mea_source.find(b"class CSE_Ext_0E_Mod_R2", start)
    if start < 0 or end < 0:
        raise Failure("ME Analyzer extension-14 structure bounds drift")
    ext14 = mea_source[start:end]
    for needle, label in (
        (b'("UsageBitmap",        uint8_t*16)', "extension-14 usage bitmap"),
        (b'("Flags",            uint8_t)', "extension-14 flags"),
        (b'("HashAlgorithm",    uint8_t)', "extension-14 hash algorithm"),
        (b'("HashSize",        uint16_t)', "extension-14 hash size"),
        (b'("Hash",            uint32_t*8)', "extension-14 SHA-256 hash"),
        (b"# 0x44", "extension-14 entry size"),
    ):
        require_once(ext14, needle, label)
    require_once(mea_source, b"39 : 'OS Kernel'", "usage 39 name")

    candidate = bytes.fromhex(CANDIDATE_OS_KEY_DIGEST)
    selector = 0x27
    return {
        "schema": SCHEMA,
        "tool": {"name": "abl-ias-key-provenance", "version": VERSION},
        "exact_update": {
            "archive": {"size": UPDATE_SIZE, "sha256": UPDATE_SHA256},
            "abl": {"member": ABL_MEMBER, "size": ABL_SIZE, "sha256": ABL_SHA256},
            "ibb_loader": {
                "size": len(ibbl),
                "sha256": IBBL_SHA256,
                "instruction_ranges": ibbl_ranges,
                "source_fit_address": 0xFEF80000,
                "relocated_fit_address": 0x000C10C0,
                "fit_signature": "_FIT_   ",
                "maximum_accepted_source_entries": 21,
                "appended_entry_type": 0x7F,
                "relocation_mode": 2,
                "relocation_skips_type": 1,
                "type_0b_payload_relocated_if_present": True,
            },
            "decompressed_stage1": {
                "size": len(stage1),
                "sha256": STAGE1_SHA256,
                "load_base": 0x000E0000,
                "instruction_ranges": stage_ranges,
                "fit_table": {
                    "base": 0x000C10C0,
                    "header_size_count_address": 0x000C10C8,
                    "entry_size": 0x10,
                    "type_offset": 0x0E,
                    "type_mask": 0x7F,
                    "selected_type": 0x0B,
                },
                "key_manifest": {
                    "pointer_from_fit_entry_offset": 0,
                    "extension_offset": 0x284,
                    "extension_size_offset": 0x288,
                    "entry_array_offset": 0x2A8,
                    "entry_size": 0x44,
                    "digest_offset": 0x24,
                    "digest_size": 0x20,
                    "cached_extension_pointer_address": 0x000C1060,
                    "cached_extension_size_address": 0x000C1064,
                    "kernel_command_line_name": "ABL.oemkm",
                    "kernel_command_line_format": "%x@%x",
                },
                "type3_os_selector": {
                    "value": selector,
                    "usage_bit_index": selector,
                    "usage_byte_index": selector >> 3,
                    "usage_byte_mask": 1 << (selector & 7),
                    "public_me_analyzer_name": "OS Kernel",
                },
            },
            "stored_oem_key_manifest": stored_oem_key,
            "package_carried_os_key_candidate_digest": {
                "sha256": CANDIDATE_OS_KEY_DIGEST,
                "present_verbatim_in_update_abl": candidate in abl,
                "present_verbatim_in_ibbl": candidate in ibbl,
                "present_verbatim_in_stage1": candidate in stage1,
                "matches_stored_oem_key_usage39_digest": CANDIDATE_OS_KEY_DIGEST == STORED_USAGE39_DIGEST,
            },
        },
        "public_structure_corroboration": {
            "slim_bootloader": {
                "commit": SBL_COMMIT,
                "file": SBL_FILE,
                "file_sha256": SBL_FILE_SHA256,
                "type_0b_name": "FIT_TYPE_0B_KEY_MANIFEST",
                "type_10_name": "FIT_TYPE_10_CSE_SECURE_BOOT",
            },
            "me_analyzer": {
                "commit": MEA_COMMIT,
                "file": MEA_FILE,
                "file_sha256": MEA_FILE_SHA256,
                "structure": "CSE Extension 14 R1 key-manifest entry",
                "entry_size": 0x44,
                "usage_bitmap_size": 0x10,
                "digest_offset": 0x24,
                "digest_size": 0x20,
                "usage_39_name": "OS Kernel",
            },
            "boundary": "Names and pre-IBBL authentication semantics are public-source corroboration; exact target instructions independently prove the layout, selector, copy, and compare path.",
        },
        "conclusions": {
            "runtime_descriptor_is_fit_entry_type_0b_proved": True,
            "type_0b_symbolic_name_key_manifest_publicly_corroborated": True,
            "pre_ibbl_fit_handoff_address_proved": True,
            "ibbl_copies_fit_and_relocates_type_0b_payload_proved": True,
            "runtime_key_manifest_layout_proved": True,
            "selector_0x27_is_usage_bit_39_proved": True,
            "usage_bit_39_os_kernel_name_publicly_corroborated": True,
            "oem_key_manifest_kernel_command_line_export_proved": True,
            "stored_oem_key_manifest_bytes_recovered": True,
            "stored_usage39_digest_recovered": True,
            "stored_oem_key_manifest_embedded_signature_valid": True,
            "package_candidate_matches_stored_usage39_digest": False,
            "runtime_fit_type0b_bound_to_stored_oem_key_manifest": False,
            "runtime_expected_digest_bytes_recovered": False,
            "producer_of_source_fit_at_0xfef80000_proved": False,
            "pre_ibbl_key_manifest_authentication_proved": False,
            "custom_signed_image_acceptance_proved": False,
            "boot_root_or_persistence_proved": False,
        },
        "limitations": [
            "Exact IBBL code proves that a pre-existing FIT-format table at 0xfef80000 is validated structurally, copied to 0xc10c0, and has non-type-1 payloads relocated; it does not identify the code or hardware that produced the source table.",
            "Exact stage-1 code consumes FIT type 0x0b as the key-manifest source. Public Intel structure names and ME Analyzer's usage-39 label corroborate the nomenclature but do not independently prove target provisioning policy.",
            "The exact flash contains an FTPR oem.key $MN2/Extension-14 manifest with a valid embedded self-signature and usage-39 digest 9b0a59...; exact recovered code does not prove that the runtime FIT type-0x0b entry points to this stored object.",
            "The stored usage-39 digest does not equal the package carried-key candidate 437008... . Without the missing runtime FIT binding, this mismatch does not prove that the package boots or fails to boot under an installed ABL.",
            "The recovered IBB stages do not locally authenticate the key manifest before use. Any CSE, Boot Guard, fuse, ACM, or earlier-ROM authentication remains outside the recovered instruction boundary; the embedded manifest signature proves self-consistency only.",
            "The exact package carried-key candidate digest remains absent verbatim from the update ABL, IBBL, and decompressed stage 1; the installed platform's volatile handoff was not captured.",
            "No updater, bootloader, target helper, firmware image, flash operation, partition write, selector change, or boot attempt was executed or generated.",
        ],
    }


def encode(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def exclusive(path: Path, data: bytes) -> None:
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0), 0o600)
    except OSError as exc:
        raise Failure(f"cannot create output exclusively: {exc}") from exc
    try:
        written = 0
        while written < len(data):
            count = os.write(fd, data[written:])
            if count <= 0:
                raise Failure("short output write")
            written += count
    finally:
        os.close(fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update-archive", type=Path, required=True)
    parser.add_argument("--sbl-repo", type=Path, required=True)
    parser.add_argument("--mea-repo", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = encode(analyze(args.update_archive, args.sbl_repo, args.mea_repo))
        if args.output:
            exclusive(args.output, data)
        else:
            sys.stdout.buffer.write(data)
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
