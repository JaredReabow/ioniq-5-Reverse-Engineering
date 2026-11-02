#!/usr/bin/env python3
"""Hash-bound passive comparison of affected and later Apollo Lake TXE modules.

This tool does not execute firmware.  It parses two already-extracted flash images,
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

SCHEMA = "ioniq-txe-fixed-module-diff/v1"
OLD_SHA256 = "f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac"
FIXED_SHA256 = "75a866331d8f23d023bbdcf9efdfee7b57bf4727eb50f6162940a2a51cb57b4a"
OLD_NFTP = 0x203000
OLD_FTPR = 0x11E000
FIXED_NFTP = 0x147000
FIXED_FTPR = 0x20000
OLD_HECI_SHA256 = "82b7be7bb8069aebfb2c9f7a0e994500fe10d631e67a16f5a5fec71d29679125"
FIXED_HECI_SHA256 = "04dceeb0b42db7910d913545b9b2342e9a26349c8e9d2e2bede201af62bf3b8f"
OLD_FPF_SHA256 = "9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9"
FIXED_FPF_SHA256 = "2c188d8f1c0ee1a0eab08e716599149b370305033d2435c3745c7f399909713d"
MODULES = ("heci", "busdrv", "storage", "policy", "fpf", "dal_sdm")

FIXED_HECI_RANGES = {
    "receive_dispatch": (0x189A, 0x1EF8, "4aea1addeb7e4e4fef929be25f3eb879a0114673e7572ec8c4b1d9dcff03fe64"),
    "fifo_bounded_copy": (0x27DA, 0x28D5, "5b8eafc086806a31c4d8adff2fd079d65b6ab205bd09a730cb7e252df7efa764"),
    "payload_consumer": (0x2B46, 0x3052, "6ef9be6f6d5d37d30dfab717dd8651118a7e8510ccce8455c72d83c473019d9e"),
    "client_lookup": (0x3052, 0x3094, "0b7634ab4b6af9e543ea8afbdd3feedb68c5aada26400b0db8b2ff5af9fa5266"),
    "connection_lookup": (0x3094, 0x3109, "86f2ac3493e735de1788d98144a0e2480b0801591522ee0a80c04c6056f3ef16"),
    "extended_header_parser": (0x3AD2, 0x3C0A, "f3ed29ecdcd43505ac0824e7b4762bde7bc29c477747a891f5646cb5a3e49e42"),
}

FIXED_FPF_ARB_FIELDS = {
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
    return decompressed, {
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


def fixed_heci_review(heci: bytes) -> dict:
    if sha256(heci) != FIXED_HECI_SHA256:
        raise Failure("fixed HECI identity drift")
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
        for name, (start, end, digest) in FIXED_HECI_RANGES.items()
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
        "advisory_attribution": "The later image adds stricter reserved/header-bit validation and a bounded extended-header parser. Because 3.1.94 is not the first fixed 3.1.55 build and spans years of intervening changes, this comparison does not identify any delta as CVE-2018-12147 or CVE-2018-3655's exact fix.",
    }


def fixed_fpf_review(affected: bytes, fixed: bytes) -> dict:
    if sha256(affected) != OLD_FPF_SHA256 or sha256(fixed) != FIXED_FPF_SHA256:
        raise Failure("FPF identity drift")
    fields = {}
    for name, (offset, width, bit_start, bit_end, digest) in FIXED_FPF_ARB_FIELDS.items():
        record = fixed[offset : offset + 0x2C]
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
        ):
            raise Failure(f"fixed FPF anti-rollback field drift: {name}")
        fields[name] = {
            "record_file_range": [offset, offset + 0x2C],
            "record_sha256": digest,
            "width_bits": width,
            "field_bit_range_inclusive": [bit_start, bit_end],
            "affected_literal_occurrences": 0,
            "later_literal_occurrences": fixed.count(name.encode("ascii")),
        }
    if any(value["later_literal_occurrences"] != 1 for value in fields.values()):
        raise Failure("fixed FPF anti-rollback field multiplicity drift")
    return {
        "fields": fields,
        "exact_static_observations": {
            "affected_fpf_lacks_all_six_field_names": True,
            "later_fpf_contains_all_six_structured_field_records": True,
            "later_enable_fields_are_two_bits_each": True,
            "later_svn_fields_are_contiguous_12_20_and_14_bit_ranges": True,
        },
        "advisory_attribution": "The later signed FPF contains explicit RBE, OEM key-manifest, and microcode anti-rollback enable/SVN field records absent by name from the affected signed FPF. The non-minimal 3.1.94 comparison does not establish when these fields appeared, whether they were provisioned on either platform, or whether they implement CVE-2018-3655's fix.",
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


def build_report(old: bytes, fixed: bytes) -> dict:
    if sha256(old) != OLD_SHA256:
        raise Failure("affected ABL identity mismatch")
    if sha256(fixed) != FIXED_SHA256:
        raise Failure("later fixed IFWI identity mismatch")
    old_report, old_modules = image_report(old, OLD_NFTP, OLD_FTPR, "affected-eu-abl")
    fixed_report, fixed_modules = image_report(fixed, FIXED_NFTP, FIXED_FTPR, "later-public-apl-ifwi")
    if sha256(old_modules["heci"]) != OLD_HECI_SHA256:
        raise Failure("affected HECI identity drift")
    comparisons = {
        name: byte_comparison(old_modules[name], fixed_modules[name])
        for name in sorted(old_modules)
    }
    return {
        "schema": SCHEMA,
        "inputs": {"affected": old_report, "later": fixed_report},
        "comparisons": comparisons,
        "later_heci_exact_static_review": fixed_heci_review(fixed_modules["heci"]),
        "later_fpf_exact_static_review": fixed_fpf_review(old_modules["fpf"], fixed_modules["fpf"]),
        "classification": {
            "later_version_is_at_or_after_intel_sa_00125_first_fixed_3_1_55": True,
            "exact_signed_later_modules_obtained": True,
            "exact_first_fixed_3_1_55_build_obtained": False,
            "cve_2018_12147_exact_bug_identified": False,
            "cve_2018_3655_exact_storage_bug_identified": False,
            "simple_oversized_nine_bit_fragment_overflow_observed": False,
        },
        "boundaries": [
            "The public later image is Intel TXE 3.1.94.3086, not the first fixed 3.1.55 release; changed bytes cannot be attributed to a specific advisory without an intermediate or first-fixed image.",
            "Embedded $MN2 verification proves self-consistency and byte binding only, not platform ROM, fuse, Boot Guard, or OEM acceptance.",
            "This is passive host-side parsing and exact-static comparison; no CSE module or host HECI endpoint was executed or opened.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--affected-abl", type=Path, required=True)
    parser.add_argument("--later-ifwi", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(stable_read(args.affected_abl), stable_read(args.later_ifwi))
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
