#!/usr/bin/env python3
"""Deterministic signed NFTP module inventory across affected and first-fixed TXE.

The tool performs passive host-side parsing only. It never executes a firmware
module or opens a HECI/MEI endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

try:
    from tools.uk_fw import txe_fixed_module_diff as fixed
except ModuleNotFoundError:  # Direct script execution from the repository root.
    import txe_fixed_module_diff as fixed


SCHEMA = "ioniq-txe-first-fixed-module-inventory/v1"
MODULE_BASE = 0x26000
SYSLIB_BASE = 0x6000
KERNEL_BASE = 0x80000
AFFECTED_KERNEL_SHA256 = "cf7dd5fc9918f96ffd2352d09a3e303471a768b3a6ee056089dd7a3d5c00bfdf"
FIRST_FIXED_KERNEL_SHA256 = "5de5db65abe4602d9c5bf12cdbc5cf5402974025901924307cf6f38f302bacfb"
EXPECTED_MODULES = (
    "adspa",
    "busdrv",
    "cls",
    "crypto",
    "dal_ivm",
    "dal_lnch",
    "dal_sdm",
    "evtdisp",
    "fpf",
    "gpio",
    "hci",
    "heci",
    "hotham",
    "ipc_drv",
    "ish_bup",
    "ish_srv",
    "iunitcse",
    "loadmgr",
    "maestro",
    "mca_boot",
    "mca_srv",
    "mctp",
    "pavp",
    "pm",
    "pmdrv",
    "policy",
    "prtc",
    "ptt",
    "sigma",
    "storage",
    "tcb",
    "tls_iso",
    "vdm",
    "vfs",
)
EXPECTED_IDENTICAL = {"ish_bup"}
EXPECTED_RELOCATION_ONLY = {
    "adspa",
    "busdrv",
    "evtdisp",
    "hci",
    "heci",
    "pmdrv",
    "tcb",
    "tls_iso",
    "vdm",
}
EXPECTED_OPAQUE = {"pavp"}
MINIMAL_LENGTH_DELTA_SITES = {
    "ish_srv": ((0x420C, 0x13, 0x14, "push_imm8", 0x421A, 0x60B4, 0x60B4),),
    "loadmgr": ((0x2600, 0x15, 0x16, "push_imm8", 0x260E, 0x60B4, 0x60B4),),
    "gpio": (
        (0x28E6, 0x16, 0x17, "push_imm8", 0x28EC, 0x60B4, 0x60B4),
        (0x29C2, 0x0E, 0x0F, "push_imm8", 0x29CB, 0x60B4, 0x60B4),
    ),
    "pm": (
        (0x0832, 0x0B, 0x0C, "push_imm8", 0x0844, 0x60B4, 0x60B4),
        (0x1823, 0x0D, 0x0E, "push_imm8", 0x1835, 0x60B4, 0x60B4),
        (0x18C6, 0x10, 0x11, "mov_byte_imm8", 0x18DF, 0x6609, 0x660E),
        (0x195C, 0x18, 0x19, "mov_byte_imm8", 0x1961, 0x6609, 0x660E),
        (0x24E2, 0x0E, 0x0F, "push_imm8", 0x24EB, 0x60B4, 0x60B4),
        (0x263E, 0x13, 0x14, "push_imm8", 0x264C, 0x60B4, 0x60B4),
        (0x2AD5, 0x15, 0x16, "push_imm8", 0x2AE3, 0x60B4, 0x60B4),
    ),
}


class Failure(ValueError):
    pass


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def differing_byte_count(left: bytes, right: bytes) -> int:
    return sum(a != b for a, b in zip(left, right)) + abs(len(left) - len(right))


def _module_extension(metadata: bytes, label: str) -> bytes:
    values = [value for tag, value in fixed.metadata_extensions(metadata, label) if tag == 10]
    if len(values) != 1 or len(values[0]) != 0x38:
        raise Failure(f"{label} module extension drift")
    return values[0]


def _partition_context(image: bytes, offset: int, label: str) -> dict:
    entries = fixed.parse_cpd(image, offset, b"NFTP")
    manifest = fixed.member(image, offset, entries, "NFTP.man")
    manifest_report = fixed.verify_mn2(manifest, f"{label} NFTP.man")
    module_names = tuple(sorted(name[:-4] for name in entries if name.endswith(".met") and name[:-4] in entries))
    if module_names != EXPECTED_MODULES:
        raise Failure(f"{label} NFTP module set drift")
    return {
        "entries": entries,
        "manifest": manifest,
        "manifest_report": manifest_report,
    }


def _extract_inventory_module(
    image: bytes,
    offset: int,
    context: dict,
    name: str,
) -> tuple[bytes | None, dict]:
    entries = context["entries"]
    manifest = context["manifest"]
    compressed = fixed.member(image, offset, entries, name)
    metadata_name = f"{name}.met"
    metadata = fixed.member(image, offset, entries, metadata_name)
    metadata_digest = hashlib.sha256(metadata).digest()[::-1]
    if manifest.count(metadata_digest) != 1:
        raise Failure(f"manifest-to-{metadata_name} binding drift")
    extension = _module_extension(metadata, metadata_name)
    compression = extension[8]
    extension_flag_byte_9 = extension[9]
    uncompressed_size, compressed_size = struct.unpack_from("<II", extension, 0x0C)
    if compressed_size != len(compressed):
        raise Failure(f"{metadata_name} compressed-size drift")

    common = {
        "cpd_relative_offset": entries[name][0],
        "compressed_size": len(compressed),
        "compressed_sha256": sha256(compressed),
        "metadata_cpd_relative_offset": entries[metadata_name][0],
        "metadata_size": len(metadata),
        "metadata_sha256": sha256(metadata),
        "manifest_binds_metadata_reverse_sha256": True,
        "module_extension_compression_byte": compression,
        "module_extension_flag_byte_9": extension_flag_byte_9,
        "declared_uncompressed_size": uncompressed_size,
        "declared_compressed_size": compressed_size,
    }
    if extension_flag_byte_9:
        common.update({
            "status": "opaque",
            "opaque_reason": "module extension byte +9 is nonzero; the strict reviewed extractor does not transform this member",
            "metadata_module_digest_matches_stored_member": extension[0x18:0x38] == hashlib.sha256(compressed).digest()[::-1],
        })
        return None, common

    try:
        value, extracted = fixed.extract_module(
            image, offset, entries, manifest, name
        )
    except fixed.Failure as exc:
        raise Failure(str(exc)) from exc
    common.update(extracted)
    common["status"] = "decoded"
    return value, common


def _syslib_stub_destination(syslib: bytes, stub: int) -> int:
    offset = stub - SYSLIB_BASE
    if offset < 0 or offset + 5 > len(syslib) or syslib[offset] != 0xE9:
        raise Failure("external target is not a bounded syslib rel32 export stub")
    displacement = struct.unpack_from("<i", syslib, offset + 1)[0]
    return stub + 5 + displacement


def relocation_review(
    affected: bytes,
    first_fixed: bytes,
    affected_syslib: bytes,
    first_fixed_syslib: bytes,
) -> dict:
    raw_difference_count = differing_byte_count(affected, first_fixed)
    if len(affected) != len(first_fixed):
        return {
            "eligible_equal_size": False,
            "raw_differing_byte_count": raw_difference_count,
            "reviewed_external_rel32_site_count": 0,
            "reviewed_external_rel32_differing_byte_count": 0,
            "unexplained_differing_byte_count": raw_difference_count,
            "equal_after_reviewed_external_rel32_normalization": False,
        }

    actual_differences = {
        index for index, (left, right) in enumerate(zip(affected, first_fixed))
        if left != right
    }
    normalized_affected = bytearray(affected)
    normalized_first_fixed = bytearray(first_fixed)
    allowed_differences: set[int] = set()
    sites = []
    target_counts: dict[int, int] = {}
    opcode_counts = {0xE8: 0, 0xE9: 0}

    for offset in range(len(affected) - 4):
        opcode = affected[offset]
        if opcode not in opcode_counts or first_fixed[offset] != opcode:
            continue
        old_displacement = struct.unpack_from("<i", affected, offset + 1)[0]
        new_displacement = struct.unpack_from("<i", first_fixed, offset + 1)[0]
        old_target = MODULE_BASE + offset + 5 + old_displacement
        new_target = MODULE_BASE + offset + 5 + new_displacement
        changed = any(
            affected[index] != first_fixed[index]
            for index in range(offset + 1, offset + 5)
        )
        if (
            not changed
            or new_displacement - old_displacement != 5
            or new_target != old_target + 5
        ):
            continue
        try:
            _syslib_stub_destination(affected_syslib, old_target)
            _syslib_stub_destination(first_fixed_syslib, new_target)
        except Failure:
            continue
        opcode_counts[opcode] += 1
        target_counts[old_target] = target_counts.get(old_target, 0) + 1
        allowed_differences.update(range(offset + 1, offset + 5))
        normalized_affected[offset + 1 : offset + 5] = b"\0" * 4
        normalized_first_fixed[offset + 1 : offset + 5] = b"\0" * 4
        sites.append({
            "module_relative_offset": offset,
            "runtime_address": MODULE_BASE + offset,
            "opcode": opcode,
            "affected_syslib_stub": old_target,
            "first_fixed_syslib_stub": new_target,
        })

    reviewed_differences = actual_differences & allowed_differences
    unexplained_differences = actual_differences - allowed_differences
    equal_after_normalization = (
        actual_differences <= allowed_differences
        and normalized_affected == normalized_first_fixed
    )
    result = {
        "eligible_equal_size": True,
        "raw_differing_byte_count": len(actual_differences),
        "reviewed_external_rel32_site_count": len(sites),
        "reviewed_external_call_site_count": opcode_counts[0xE8],
        "reviewed_external_tail_jump_site_count": opcode_counts[0xE9],
        "reviewed_external_rel32_differing_byte_count": len(reviewed_differences),
        "unexplained_differing_byte_count": len(unexplained_differences),
        "distinct_affected_syslib_stub_count": len(target_counts),
        "affected_syslib_stub_reference_counts": {
            f"0x{target:x}": target_counts[target] for target in sorted(target_counts)
        },
        "all_reviewed_first_fixed_syslib_stubs_equal_affected_plus_five": True,
        "all_reviewed_targets_decode_as_bounded_syslib_rel32_export_stubs": True,
        "equal_after_reviewed_external_rel32_normalization": equal_after_normalization,
    }
    if len(unexplained_differences) <= 32:
        result["unexplained_module_relative_offsets"] = sorted(unexplained_differences)
    return result


def _rel32_call_target(module: bytes, call_offset: int) -> int:
    if call_offset < 0 or call_offset + 5 > len(module) or module[call_offset] != 0xE8:
        raise Failure("reviewed module call opcode drift")
    return MODULE_BASE + call_offset + 5 + struct.unpack_from("<i", module, call_offset + 1)[0]


def minimal_length_delta_review(
    decoded_modules: dict[str, tuple[bytes, bytes]],
    module_reports: dict,
    affected_syslib: bytes,
    first_fixed_syslib: bytes,
) -> dict:
    sites = []
    for name, expected_sites in MINIMAL_LENGTH_DELTA_SITES.items():
        affected, first_fixed = decoded_modules[name]
        review = module_reports[name]["relocation_review"]
        expected_offsets = {site[0] for site in expected_sites}
        if set(review.get("unexplained_module_relative_offsets", ())) != expected_offsets:
            raise Failure(f"{name} minimal length-delta offset drift")
        for (
            immediate_offset,
            old_value,
            new_value,
            encoding,
            call_offset,
            affected_stub,
            first_fixed_stub,
        ) in expected_sites:
            if affected[immediate_offset] != old_value or first_fixed[immediate_offset] != new_value:
                raise Failure(f"{name} reviewed length immediate drift")
            if new_value != old_value + 1:
                raise Failure(f"{name} reviewed length translation drift")
            if encoding == "push_imm8":
                if affected[immediate_offset - 1] != 0x6A or first_fixed[immediate_offset - 1] != 0x6A:
                    raise Failure(f"{name} push-imm8 encoding drift")
            elif encoding == "mov_byte_imm8":
                if affected[immediate_offset - 3 : immediate_offset] != first_fixed[immediate_offset - 3 : immediate_offset] or affected[immediate_offset - 3] != 0xC6:
                    raise Failure(f"{name} mov-byte-imm8 encoding drift")
            else:
                raise Failure(f"{name} unknown reviewed immediate encoding")
            message_word_push = b"\x68\x00\x02\x00\x02"
            if affected[max(0, call_offset - 32) : call_offset].count(message_word_push) != 1:
                raise Failure(f"{name} affected message dword-zero drift")
            if first_fixed[max(0, call_offset - 32) : call_offset].count(message_word_push) != 1:
                raise Failure(f"{name} first-fixed message dword-zero drift")
            if _rel32_call_target(affected, call_offset) != affected_stub:
                raise Failure(f"{name} affected reviewed call target drift")
            if _rel32_call_target(first_fixed, call_offset) != first_fixed_stub:
                raise Failure(f"{name} first-fixed reviewed call target drift")
            _syslib_stub_destination(affected_syslib, affected_stub)
            _syslib_stub_destination(first_fixed_syslib, first_fixed_stub)
            sites.append({
                "module": name,
                "module_relative_immediate_offset": immediate_offset,
                "runtime_immediate_address": MODULE_BASE + immediate_offset,
                "encoding": encoding,
                "affected_length": old_value,
                "first_fixed_length": new_value,
                "module_relative_call_offset": call_offset,
                "affected_syslib_stub": affected_stub,
                "first_fixed_syslib_stub": first_fixed_stub,
            })

    affected_constructor = affected_syslib[0x8E8A - SYSLIB_BASE : 0x8ED3 - SYSLIB_BASE]
    first_constructor = first_fixed_syslib[0x8E8F - SYSLIB_BASE : 0x8ED8 - SYSLIB_BASE]
    affected_submit = affected_syslib[0x7F38 - SYSLIB_BASE : 0x7F65 - SYSLIB_BASE]
    first_submit = first_fixed_syslib[0x7F3D - SYSLIB_BASE : 0x7F6A - SYSLIB_BASE]
    if (
        sha256(affected_constructor) != "1a9f71789daff697fe6ac80b110101ecc63d84bbc3759c6a869bfc648a6d8c28"
        or sha256(first_constructor) != "1a9f71789daff697fe6ac80b110101ecc63d84bbc3759c6a869bfc648a6d8c28"
        or affected_constructor[7:13] != b"\x8b\x45\x0c\x88\x43\x04"
        or first_constructor[7:13] != b"\x8b\x45\x0c\x88\x43\x04"
        or affected_submit[:12] != b"\x55\x89\xe5\x8b\x45\x0c\x8b\x55\x08\x89\x10\x50"
        or first_submit[:12] != affected_submit[:12]
        or _syslib_stub_destination(affected_syslib, 0x60B4) != 0x8E8A
        or _syslib_stub_destination(first_fixed_syslib, 0x60B4) != 0x8E8F
        or _syslib_stub_destination(affected_syslib, 0x6609) != 0x7F38
        or _syslib_stub_destination(first_fixed_syslib, 0x660E) != 0x7F3D
    ):
        raise Failure("reviewed serialized-length constructor drift")

    return {
        "module_count": len(MINIMAL_LENGTH_DELTA_SITES),
        "site_count": len(sites),
        "message_dword_zero": 0x02000200,
        "affected_constructor_runtime_range": [0x8E8A, 0x8ED3],
        "first_fixed_constructor_runtime_range": [0x8E8F, 0x8ED8],
        "constructor_sha256": sha256(affected_constructor),
        "submit_wrapper_stores_first_argument_dword_at_message_offset_zero": True,
        "constructor_stores_second_argument_low_byte_at_message_offset_four": True,
        "all_reviewed_lengths_increment_by_one": True,
        "sites": sites,
        "attribution_boundary": "The eleven residual bytes in ish_srv, loadmgr, gpio, and pm are exact one-byte increases in serialized message-length fields whose message dword zero is 0x02000200. This is a coordinated interface delta, but the dword's semantics, recipient, added byte meaning, attacker control, HECI reachability, and CVE attribution remain unproved.",
    }


def kernel_message_submit_selector_review(
    affected_kernel: bytes,
    first_fixed_kernel: bytes,
    affected_syslib: bytes,
    first_fixed_syslib: bytes,
) -> dict:
    """Bind the exact syscall path used by the reviewed message submit wrapper."""
    if len(affected_kernel) != 0x12000 or len(first_fixed_kernel) != 0x12000:
        raise Failure("FTPR kernel size drift")
    if sha256(affected_kernel) != AFFECTED_KERNEL_SHA256:
        raise Failure("affected FTPR kernel identity mismatch")
    if sha256(first_fixed_kernel) != FIRST_FIXED_KERNEL_SHA256:
        raise Failure("first-fixed FTPR kernel identity mismatch")

    affected_table = 0x10D24
    first_table = 0x10CE0
    selector = 0x10
    affected_entry = struct.unpack_from("<III", affected_kernel, affected_table + selector * 12)
    first_entry = struct.unpack_from("<III", first_fixed_kernel, first_table + selector * 12)
    if affected_entry != (1, 0x40, 0x8C6B8) or first_entry != (1, 0x40, 0x8C65A):
        raise Failure("kernel selector 0x10 table entry drift")

    affected_range = (0x8C6B8, 0x8C946)
    first_range = (0x8C65A, 0x8C8E8)
    affected_body = affected_kernel[affected_range[0] - KERNEL_BASE : affected_range[1] - KERNEL_BASE]
    first_body = first_fixed_kernel[first_range[0] - KERNEL_BASE : first_range[1] - KERNEL_BASE]
    if len(affected_body) != len(first_body) or len(affected_body) != 0x28E:
        raise Failure("kernel selector 0x10 handler geometry drift")
    if sha256(affected_body) != "8335a78c6ea2ca8f1c7a255a1cc5e82855bdba76dc4bdb134106d2092ce89792":
        raise Failure("affected kernel selector 0x10 handler hash drift")
    if sha256(first_body) != "fece441f780c7171087f410322244c1ffbb9afcb2a55879d5c103dcb48147e0f":
        raise Failure("first-fixed kernel selector 0x10 handler hash drift")

    normalized_affected = bytearray(affected_body)
    normalized_first = bytearray(first_body)
    rel32_sites = []
    allowed: set[int] = set()
    for relative_offset in (0x52, 0xF3):
        if affected_body[relative_offset] != 0xE8 or first_body[relative_offset] != 0xE8:
            raise Failure("kernel selector 0x10 reviewed call opcode drift")
        old_displacement = struct.unpack_from("<i", affected_body, relative_offset + 1)[0]
        new_displacement = struct.unpack_from("<i", first_body, relative_offset + 1)[0]
        old_target = affected_range[0] + relative_offset + 5 + old_displacement
        new_target = first_range[0] + relative_offset + 5 + new_displacement
        rel32_sites.append({
            "handler_relative_offset": relative_offset,
            "affected_runtime_address": affected_range[0] + relative_offset,
            "first_fixed_runtime_address": first_range[0] + relative_offset,
            "affected_target": old_target,
            "first_fixed_target": new_target,
        })
        allowed.update(range(relative_offset + 1, relative_offset + 5))
        normalized_affected[relative_offset + 1 : relative_offset + 5] = b"\0" * 4
        normalized_first[relative_offset + 1 : relative_offset + 5] = b"\0" * 4

    semantic_sites = []
    for relative_offset, opcode in ((0x1C6, 0xB8), (0x263, 0x3D)):
        if affected_body[relative_offset] != opcode or first_body[relative_offset] != opcode:
            raise Failure("kernel selector 0x10 sentinel opcode drift")
        old_value = struct.unpack_from("<I", affected_body, relative_offset + 1)[0]
        new_value = struct.unpack_from("<I", first_body, relative_offset + 1)[0]
        if (old_value, new_value) != (0xFF, 0x102):
            raise Failure("kernel selector 0x10 sentinel value drift")
        semantic_sites.append({
            "handler_relative_immediate_offset": relative_offset + 1,
            "affected_runtime_immediate_address": affected_range[0] + relative_offset + 1,
            "first_fixed_runtime_immediate_address": first_range[0] + relative_offset + 1,
            "instruction": "mov_eax_imm32" if opcode == 0xB8 else "cmp_eax_imm32",
            "affected_value": old_value,
            "first_fixed_value": new_value,
        })
        allowed.update(range(relative_offset + 1, relative_offset + 5))
        normalized_affected[relative_offset + 1 : relative_offset + 5] = b"\0" * 4
        normalized_first[relative_offset + 1 : relative_offset + 5] = b"\0" * 4

    actual = {index for index, pair in enumerate(zip(affected_body, first_body)) if pair[0] != pair[1]}
    if actual - allowed or normalized_affected != normalized_first:
        raise Failure("kernel selector 0x10 unexplained body delta")

    global_immediates = {
        "affected_mov_eax_0xff": [0x860F2, 0x8C87E],
        "first_fixed_mov_eax_0x102": [0x86347, 0x8C820],
        "affected_mov_edx_0xff": [0x8C08A],
        "first_fixed_mov_edx_0x102": [0x8C02C],
        "affected_cmp_eax_0xff": [
            0x88096, 0x88A02, 0x88C9C, 0x89A23, 0x89C9A, 0x8B6CD,
            0x8BDB9, 0x8C91B, 0x8CB6D, 0x8EC67, 0x8EFDF, 0x901F9,
        ],
        "first_fixed_cmp_eax_0x102": [
            0x88038, 0x889A4, 0x88C3E, 0x899C5, 0x89C3C, 0x8B66F,
            0x8BD5B, 0x8C8BD, 0x8CB0F, 0x8EC09, 0x8EF81, 0x9019B,
        ],
    }
    census_specs = (
        (affected_kernel, b"\xb8\xff\x00\x00\x00", "affected_mov_eax_0xff"),
        (first_fixed_kernel, b"\xb8\x02\x01\x00\x00", "first_fixed_mov_eax_0x102"),
        (affected_kernel, b"\xba\xff\x00\x00\x00", "affected_mov_edx_0xff"),
        (first_fixed_kernel, b"\xba\x02\x01\x00\x00", "first_fixed_mov_edx_0x102"),
        (affected_kernel, b"\x3d\xff\x00\x00\x00", "affected_cmp_eax_0xff"),
        (first_fixed_kernel, b"\x3d\x02\x01\x00\x00", "first_fixed_cmp_eax_0x102"),
    )
    for kernel, pattern, key in census_specs:
        found = []
        cursor = 0
        while True:
            cursor = kernel.find(pattern, cursor)
            if cursor < 0:
                break
            found.append(KERNEL_BASE + cursor)
            cursor += 1
        if found != global_immediates[key]:
            raise Failure(f"kernel global immediate census drift: {key}")

    affected_helper = affected_kernel[0x8BFE7 - KERNEL_BASE : 0x8C099 - KERNEL_BASE]
    first_helper = first_fixed_kernel[0x8BF89 - KERNEL_BASE : 0x8C03B - KERNEL_BASE]
    helper_prefix = bytes.fromhex("8d57508b475085c074088d50288b4028ebf48932ba")
    if (
        len(affected_helper) != 0xB2
        or len(first_helper) != 0xB2
        or sha256(affected_helper) != "140dff321f92ee9e8fc551ff9e28e7501a97ab81b4b4e5c0f73ed52648cd3cea"
        or sha256(first_helper) != "0a10e5956f69381c8c455af7c14b72320d844709a9304af0ff439d38dfa7c196"
        or affected_helper[0x8F : 0x8F + len(helper_prefix)] != helper_prefix
        or first_helper[0x8F : 0x8F + len(helper_prefix)] != helper_prefix
        or struct.unpack_from("<I", affected_helper, 0xA4)[0] != 0xFF
        or struct.unpack_from("<I", first_helper, 0xA4)[0] != 0x102
        or affected_helper[:0xA4] != first_helper[:0xA4]
        or affected_helper[0xA8:] != first_helper[0xA8:]
    ):
        raise Failure("selector 0x10 directly called helper drift")

    ordinal_pairs = (
        (0x87587, 0x876BF, 0x0C4, 0x0C6, {9}),
        (0x87609, 0x87741, 0x0C4, 0x0C6, {9}),
        (0x87642, 0x8777A, 0x0C5, 0x0C7, {0, 1, 9, 18, 19}),
        (0x87650, 0x87788, 0x0C5, 0x0C7, {4, 5, 9}),
        (0x87695, 0x877CD, 0x0C6, 0x0C8, {1, 9}),
        (0x876A6, 0x877DE, 0x0C6, 0x0C8, {4, 5, 9}),
        (0x880F6, 0x88098, 0x0C7, 0x0CA, {9, 16, 17}),
        (0x88122, 0x880C4, 0x0C8, 0x0CB, {0, 9}),
        (0x85A1D, 0x824E4, 0x0C8, 0x0CB, {9}),
        (0x8A3F4, 0x8A396, 0x100, 0x103, {9, 19, 20}),
        (0x873D4, 0x874B7, 0x100, 0x103, {9}),
        (0x8A872, 0x8A814, 0x101, 0x104, {9, 16, 17}),
        (0x8A47D, 0x8A41F, 0x102, 0x105, {9}),
        (0x8A4A5, 0x8A447, 0x102, 0x105, {9}),
        (0x8A835, 0x8A7D7, 0x102, 0x105, {9}),
        (0x8A8BC, 0x8A85E, 0x102, 0x105, {9}),
    )
    ordinal_shift_sites = []
    for old_address, new_address, old_value, new_value, expected_window_differences in ordinal_pairs:
        old_offset = old_address - KERNEL_BASE
        new_offset = new_address - KERNEL_BASE
        old_opcode = affected_kernel[old_offset]
        new_opcode = first_fixed_kernel[new_offset]
        if old_opcode != new_opcode or old_opcode not in (0xB8, 0xBA):
            raise Failure("kernel post-sentinel ordinal opcode drift")
        if struct.unpack_from("<I", affected_kernel, old_offset + 1)[0] != old_value:
            raise Failure("affected kernel post-sentinel ordinal drift")
        if struct.unpack_from("<I", first_fixed_kernel, new_offset + 1)[0] != new_value:
            raise Failure("first-fixed kernel post-sentinel ordinal drift")
        old_window = affected_kernel[old_offset - 8 : old_offset + 13]
        new_window = first_fixed_kernel[new_offset - 8 : new_offset + 13]
        window_differences = {
            index for index, pair in enumerate(zip(old_window, new_window))
            if pair[0] != pair[1]
        }
        if window_differences != expected_window_differences:
            raise Failure("kernel post-sentinel instruction-context drift")
        ordinal_shift_sites.append({
            "instruction": "mov_eax_imm32" if old_opcode == 0xB8 else "mov_edx_imm32",
            "affected_runtime_address": old_address,
            "first_fixed_runtime_address": new_address,
            "affected_value": old_value,
            "first_fixed_value": new_value,
        })

    status_0xfd_body = affected_kernel[0x85A04 - KERNEL_BASE : 0x85A90 - KERNEL_BASE]
    status_0x100_body = first_fixed_kernel[0x824CB - KERNEL_BASE : 0x82557 - KERNEL_BASE]
    status_0xfe_body = affected_kernel[0x8539F - KERNEL_BASE : 0x853FD - KERNEL_BASE]
    status_0x101_body = first_fixed_kernel[0x8580B - KERNEL_BASE : 0x85869 - KERNEL_BASE]
    if (
        len(status_0xfd_body) != 0x8C
        or sha256(status_0xfd_body) != "6a5da5501dac433546a2c08220ddff17b80ef4160549b9c6cde38da2a9f8df19"
        or status_0xfd_body[0x44] != 0xB8
        or struct.unpack_from("<I", status_0xfd_body, 0x45)[0] != 0xFD
        or len(status_0x100_body) != 0x8C
        or sha256(status_0x100_body) != "b12ad8b0c4e784655e76de10ba1977c906bb55c14d0b7eccfd2c62479b96d930"
        or status_0x100_body[0x44] != 0xB8
        or struct.unpack_from("<I", status_0x100_body, 0x45)[0] != 0x100
        or len(status_0xfe_body) != 0x5E
        or sha256(status_0xfe_body) != "1e17058b43cdf950a3abdcb1c729565d66171a19d319c431fc8843c7903a2063"
        or status_0xfe_body[0x52] != 0xB8
        or struct.unpack_from("<I", status_0xfe_body, 0x53)[0] != 0xFE
        or len(status_0x101_body) != 0x5E
        or sha256(status_0x101_body) != "004b911c32d58e78d2ffb3aab766308fb6b9168b35781208021eeabeb2f0f10e"
        or status_0x101_body[0x52] != 0xB8
        or struct.unpack_from("<I", status_0x101_body, 0x53)[0] != 0x101
    ):
        raise Failure("shifted status producer drift")

    producer_callers: dict[str, list[int]] = {
        "affected_0xfd": [],
        "first_fixed_0x100": [],
        "affected_0xfe": [],
        "first_fixed_0x101": [],
    }
    for kernel, targets in (
        (affected_kernel, {0x85A04: "affected_0xfd", 0x8539F: "affected_0xfe"}),
        (first_fixed_kernel, {0x824CB: "first_fixed_0x100", 0x8580B: "first_fixed_0x101"}),
    ):
        for offset in range(len(kernel) - 4):
            if kernel[offset] != 0xE8:
                continue
            target = KERNEL_BASE + offset + 5 + struct.unpack_from("<i", kernel, offset + 1)[0]
            if target in targets:
                producer_callers[targets[target]].append(KERNEL_BASE + offset)
    if producer_callers != {
        "affected_0xfd": [0x85AA6, 0x85AE9, 0x88118],
        "first_fixed_0x100": [0x85E86, 0x85EC9, 0x880BA],
        "affected_0xfe": [0x854CA],
        "first_fixed_0x101": [0x85936],
    }:
        raise Failure("shifted status producer caller drift")

    inserted_status_sites = [
        {"value": 0xC4, "runtime_address": 0x876A6, "instruction": "mov_eax_imm32"},
        {"value": 0xC5, "runtime_address": 0x87687, "instruction": "mov_eax_imm32"},
        {"value": 0xC9, "runtime_address": 0x8765C, "instruction": "mov_eax_imm32"},
    ]
    for site in inserted_status_sites:
        offset = site["runtime_address"] - KERNEL_BASE
        if first_fixed_kernel[offset] != 0xB8 or struct.unpack_from("<I", first_fixed_kernel, offset + 1)[0] != site["value"]:
            raise Failure("first-fixed inserted ordinal status site drift")

    generic_completion_pairs = (
        (0x88096, 0x88038),
        (0x88A02, 0x889A4),
        (0x88C9C, 0x88C3E),
        (0x89A23, 0x899C5),
        (0x89C9A, 0x89C3C),
        (0x8B6CD, 0x8B66F),
        (0x8BDB9, 0x8BD5B),
        (0x8CB6D, 0x8CB0F),
        (0x8EFDF, 0x8EF81),
        (0x901F9, 0x9019B),
    )
    generic_completion_sites = []
    for affected_address, first_address in generic_completion_pairs:
        branch_targets = []
        error_targets = []
        for kernel, address, value, error_target in (
            (affected_kernel, affected_address, 0xFF, 0x89889),
            (first_fixed_kernel, first_address, 0x102, 0x8982B),
        ):
            offset = address - KERNEL_BASE
            if (
                kernel[offset - 9 : offset - 1] != bytes.fromhex("a38483090085c074")
                or kernel[offset] != 0x3D
                or struct.unpack_from("<I", kernel, offset + 1)[0] != value
                or kernel[offset + 5] != 0x74
            ):
                raise Failure("kernel generic completion filter drift")
            zero_target = address + struct.unpack_from("<b", kernel, offset - 1)[0]
            sentinel_target = address + 7 + struct.unpack_from("<b", kernel, offset + 6)[0]
            if zero_target != sentinel_target:
                raise Failure("kernel generic completion filter branch-target drift")
            branch_targets.append(zero_target)
            found_error_targets = []
            for cursor in range(offset + 7, min(offset + 32, len(kernel) - 4)):
                if kernel[cursor] not in (0xE8, 0xE9):
                    continue
                target = KERNEL_BASE + cursor + 5 + struct.unpack_from("<i", kernel, cursor + 1)[0]
                if target == error_target:
                    found_error_targets.append(target)
            if found_error_targets != [error_target]:
                raise Failure("kernel generic completion error-target drift")
            error_targets.append(error_target)
        generic_completion_sites.append({
            "affected_runtime_address": affected_address,
            "first_fixed_runtime_address": first_address,
            "zero_and_sentinel_branch_targets": branch_targets,
            "other_nonzero_error_targets": error_targets,
        })

    producer_role_sites = [
        {
            "role": "list_registration_return",
            "affected_runtime_address": 0x860F2,
            "first_fixed_runtime_address": 0x86347,
            "affected_direct_call_sites": [0x88268, 0x8840A],
            "first_fixed_direct_call_sites": [0x8820A, 0x883AC],
        },
        {
            "role": "selector_0x10_handler_immediate_return",
            "affected_runtime_address": 0x8C87E,
            "first_fixed_runtime_address": 0x8C820,
        },
        {
            "role": "linked_tail_helper_return",
            "affected_runtime_address": 0x8C08A,
            "first_fixed_runtime_address": 0x8C02C,
            "affected_direct_call_sites": [0x8C916, 0x8C93C],
            "first_fixed_direct_call_sites": [0x8C8B8, 0x8C8DE],
        },
    ]
    for site in producer_role_sites:
        for kernel, address, value, call_key in (
            (affected_kernel, site["affected_runtime_address"], 0xFF, "affected_direct_call_sites"),
            (first_fixed_kernel, site["first_fixed_runtime_address"], 0x102, "first_fixed_direct_call_sites"),
        ):
            offset = address - KERNEL_BASE
            expected_opcode = 0xBA if site["role"] == "linked_tail_helper_return" else 0xB8
            if kernel[offset] != expected_opcode or struct.unpack_from("<I", kernel, offset + 1)[0] != value:
                raise Failure("kernel status producer role drift")
            if call_key in site:
                found_callers = []
                target = address - (0xA3 if site["role"] == "linked_tail_helper_return" else 0x1B)
                for cursor in range(len(kernel) - 4):
                    if kernel[cursor] != 0xE8:
                        continue
                    called = KERNEL_BASE + cursor + 5 + struct.unpack_from("<i", kernel, cursor + 1)[0]
                    if called == target:
                        found_callers.append(KERNEL_BASE + cursor)
                if found_callers != site[call_key]:
                    raise Failure("kernel status producer direct-caller drift")

    for kernel, address, value in (
        (affected_kernel, 0x8EC67, 0xFF),
        (first_fixed_kernel, 0x8EC09, 0x102),
    ):
        offset = address - KERNEL_BASE
        if (
            kernel[offset - 5 : offset] != bytes.fromhex("a184830900")
            or kernel[offset] != 0x3D
            or struct.unpack_from("<I", kernel, offset + 1)[0] != value
            or kernel[offset + 5 : offset + 8] != bytes.fromhex("750ae9")
        ):
            raise Failure("kernel dispatch-continue status consumer drift")

    role_affected_sites = {
        site["affected_runtime_address"] for site in producer_role_sites
    } | {
        site["affected_runtime_address"] for site in generic_completion_sites
    } | {0x8C91B, 0x8EC67}
    role_first_sites = {
        site["first_fixed_runtime_address"] for site in producer_role_sites
    } | {
        site["first_fixed_runtime_address"] for site in generic_completion_sites
    } | {0x8C8BD, 0x8EC09}
    census_affected_sites = set(
        global_immediates["affected_mov_eax_0xff"]
        + global_immediates["affected_mov_edx_0xff"]
        + global_immediates["affected_cmp_eax_0xff"]
    )
    census_first_sites = set(
        global_immediates["first_fixed_mov_eax_0x102"]
        + global_immediates["first_fixed_mov_edx_0x102"]
        + global_immediates["first_fixed_cmp_eax_0x102"]
    )
    if role_affected_sites != census_affected_sites or role_first_sites != census_first_sites:
        raise Failure("kernel status site role coverage drift")

    affected_epilogue = affected_kernel[0x8BDB0 - KERNEL_BASE : 0x8BDCF - KERNEL_BASE]
    first_epilogue = first_fixed_kernel[0x8BD52 - KERNEL_BASE : 0x8BD71 - KERNEL_BASE]
    if (
        sha256(affected_epilogue) != "09ea11155b3e87de23f62f18420589a74c6fefd14c5f0dda24bf956a7264bdb4"
        or sha256(first_epilogue) != "34967dbd0be79aae7c2c0319e1e237210740e207895932e2269b42cef1bd978d"
        or affected_epilogue[:9] != first_epilogue[:9]
        or struct.unpack_from("<I", affected_epilogue, 10)[0] != 0xFF
        or struct.unpack_from("<I", first_epilogue, 10)[0] != 0x102
        or affected_epilogue[14:] != first_epilogue[14:]
    ):
        raise Failure("selector 0x10 shared return epilogue drift")

    affected_wrapper = affected_syslib[0x16F8F - SYSLIB_BASE : 0x16FB3 - SYSLIB_BASE]
    first_wrapper = first_fixed_syslib[0x16FB1 - SYSLIB_BASE : 0x16FD5 - SYSLIB_BASE]
    expected_prefix = bytes.fromhex("5589e50fb7450c0fb65508c1e2180d0000010009d08b551089550c8945085d")
    if affected_wrapper[:31] != expected_prefix or first_wrapper[:31] != expected_prefix:
        raise Failure("syslib selector wrapper instruction drift")
    if affected_wrapper[31] != 0xE9 or first_wrapper[31] != 0xE9:
        raise Failure("syslib selector wrapper tail gate drift")
    affected_gate = 0x16F8F + 36 + struct.unpack_from("<i", affected_wrapper, 32)[0]
    first_gate = 0x16FB1 + 36 + struct.unpack_from("<i", first_wrapper, 32)[0]
    if (affected_gate, first_gate) != (0x118B2, 0x118BA):
        raise Failure("syslib selector wrapper gate target drift")

    affected_submit = affected_syslib[0x7F38 - SYSLIB_BASE : 0x7F65 - SYSLIB_BASE]
    first_submit = first_fixed_syslib[0x7F3D - SYSLIB_BASE : 0x7F6A - SYSLIB_BASE]
    if affected_submit[9:16] != b"\x89\x10\x50\x6a\x40\x6a\x10" or first_submit[9:16] != affected_submit[9:16]:
        raise Failure("reviewed message submit selector arguments drift")
    for value, runtime, expected_target in (
        (affected_submit, 0x7F38, 0x16F8F),
        (first_submit, 0x7F3D, 0x16FB1),
    ):
        if value[16] != 0xE8:
            raise Failure("reviewed message submit wrapper call drift")
        target = runtime + 21 + struct.unpack_from("<i", value, 17)[0]
        if target != expected_target:
            raise Failure("reviewed message submit selector wrapper target drift")

    return {
        "selector": selector,
        "syscall_argument_size": 0x40,
        "affected_table_runtime_address": KERNEL_BASE + affected_table,
        "first_fixed_table_runtime_address": KERNEL_BASE + first_table,
        "affected_handler_runtime_range": list(affected_range),
        "first_fixed_handler_runtime_range": list(first_range),
        "handler_size": len(affected_body),
        "affected_handler_sha256": sha256(affected_body),
        "first_fixed_handler_sha256": sha256(first_body),
        "raw_differing_byte_count": len(actual),
        "reviewed_rel32_sites": rel32_sites,
        "semantic_immediate_sites": semantic_sites,
        "only_handler_semantic_change_after_rel32_normalization": "two uses of the same immediate change from 0x000000ff to 0x00000102",
        "directly_called_helper": {
            "affected_runtime_range": [0x8BFE7, 0x8C099],
            "first_fixed_runtime_range": [0x8BF89, 0x8C03B],
            "size": len(affected_helper),
            "affected_sha256": sha256(affected_helper),
            "first_fixed_sha256": sha256(first_helper),
            "only_raw_differences": "two bytes inside MOV EDX immediate 0x000000ff to 0x00000102",
            "bounded_behavior": "after walking +0x50/+0x28 links to a null tail, the helper stores the source pointer at the tail, loads the reviewed immediate into EDX, then returns it through EAX",
        },
        "shared_return_epilogue": {
            "affected_runtime_range": [0x8BDB0, 0x8BDCF],
            "first_fixed_runtime_range": [0x8BD52, 0x8BD71],
            "affected_sha256": sha256(affected_epilogue),
            "first_fixed_sha256": sha256(first_epilogue),
            "only_change": "cmp eax immediate 0x000000ff to 0x00000102",
            "bounded_behavior": "stores EAX at 0x98384; zero and the reviewed immediate both take the path that clears EAX and returns, while other nonzero values call a separate handler",
        },
        "adjacent_ordinal_shift_review": {
            "site_count": len(ordinal_shift_sites),
            "sites": ordinal_shift_sites,
            "all_reviewed_values_follow_expected_translation": all(
                site["first_fixed_value"]
                == site["affected_value"] + (2 if site["affected_value"] <= 0xC6 else 3)
                for site in ordinal_shift_sites
            ),
            "affected_to_first_fixed_value_counts": {
                "0xc4_to_0xc6": 2,
                "0xc5_to_0xc7": 2,
                "0xc6_to_0xc8": 2,
                "0xc7_to_0xca": 1,
                "0xc8_to_0xcb": 2,
                "0x100_to_0x103": 2,
                "0x101_to_0x104": 1,
                "0x102_to_0x105": 4,
            },
            "first_fixed_inserted_numeric_ordinals": inserted_status_sites,
            "interpretation_boundary": "Matching instruction contexts show a plus-two shift for affected 0xc4..0xc6, a plus-three shift from affected 0xc7 onward, and exact first-fixed status-return sites at new ordinals 0xc4, 0xc5, and 0xc9. This identifies the numeric insertion points but not the vendor status names.",
        },
        "shifted_memory_status_producers": {
            "status_0xfd_to_0x100": {
                "affected_runtime_range": [0x85A04, 0x85A90],
                "first_fixed_runtime_range": [0x824CB, 0x82557],
                "size": len(status_0x100_body),
                "affected_sha256": sha256(status_0xfd_body),
                "first_fixed_sha256": sha256(status_0x100_body),
                "affected_direct_call_sites": producer_callers["affected_0xfd"],
                "first_fixed_direct_call_sites": producer_callers["first_fixed_0x100"],
                "bounded_behavior": "both counterparts examine a page-table entry at 0x08002000, validate state and index bounds, return the translated status when a secondary table byte has bits 0..5 set, and otherwise can clear the entry and invalidate its page",
            },
            "status_0xfe_to_0x101": {
                "affected_runtime_range": [0x8539F, 0x853FD],
                "first_fixed_runtime_range": [0x8580B, 0x85869],
                "size": len(status_0x101_body),
                "affected_sha256": sha256(status_0xfe_body),
                "first_fixed_sha256": sha256(status_0x101_body),
                "affected_direct_call_sites": producer_callers["affected_0xfe"],
                "first_fixed_direct_call_sites": producer_callers["first_fixed_0x101"],
                "bounded_behavior": "both counterparts scan 128 table entries, append selected indexes to an output array, and return the translated status when the output count exceeds 62",
            },
            "interpretation_boundary": "The first-fixed 0x100 and 0x101 producers are exact semantic counterparts of affected 0xfd and 0xfe producers, not newly inserted statuses. Their translation corroborates the ordinal shift and does not attribute either SA-00125 CVE.",
        },
        "kernel_status_site_role_map": {
            "producer_site_count": len(producer_role_sites),
            "producer_sites": producer_role_sites,
            "consumer_site_count": len(generic_completion_sites) + 2,
            "generic_completion_filter_sites": generic_completion_sites,
            "selector_helper_acceptance": {
                "affected_runtime_address": 0x8C91B,
                "first_fixed_runtime_address": 0x8C8BD,
                "bounded_behavior": "compares the linked-tail helper return and continues selector-0x10 state updates only when it equals the reviewed sentinel",
            },
            "dispatch_queue_continue": {
                "affected_runtime_address": 0x8EC67,
                "first_fixed_runtime_address": 0x8EC09,
                "bounded_behavior": "loads the global status at 0x98384 and returns to the pending-work dequeue path when it equals the reviewed sentinel",
            },
            "covers_complete_fifteen_site_census": True,
            "interpretation_boundary": "Three sites produce the value. Ten generic completion filters treat zero and the sentinel alike while forwarding other nonzero values to a common error handler; selector 0x10 accepts the linked-tail helper's sentinel result; and the central dispatcher continues dequeuing pending work when the global status equals it. This supports a queued/deferred or nonordinary-completion role, not a recovered vendor name or CVE attribution.",
        },
        "kernel_global_immediate_census": {
            **global_immediates,
            "affected_total_site_count": 15,
            "first_fixed_total_site_count": 15,
            "interpretation_boundary": "The same numeric change occurs in fifteen MOV/CMP sites across each complete kernel. The exact selector-0x10 helper returns it after linking an object into a queue-like structure, and the shared epilogue handles it like zero rather than other nonzero values. This supports a deferred/nonordinary-completion sentinel interpretation, but does not establish the vendor name or CVE attribution.",
        },
        "affected_syslib_selector_wrapper_runtime_range": [0x16F8F, 0x16FB3],
        "first_fixed_syslib_selector_wrapper_runtime_range": [0x16FB1, 0x16FD5],
        "affected_syslib_selector_wrapper_sha256": sha256(affected_wrapper),
        "first_fixed_syslib_selector_wrapper_sha256": sha256(first_wrapper),
        "syslib_wrapper_builds_syscall_value": "(selector_byte << 24) | 0x00010000 | argument_size_word",
        "reviewed_submit_syscall_value": 0x10010040,
        "attribution_boundary": "The changed 0x10 kernel handler is on the exact path used by the eleven reviewed message-length sites, but the same 0xff-to-0x102 change appears at fifteen MOV/CMP sites kernel-wide, including the directly called helper's MOV EDX return path. Three numeric ordinal insertions are now bound to first-fixed status-return sites at 0xc4, 0xc5, and 0xc9, but their vendor names and semantics, message dword-zero meaning, HECI reachability, attacker control, and CVE-2018-12147 attribution remain unproved.",
    }


def build_report(affected_image: bytes, first_fixed_image: bytes) -> dict:
    if fixed.sha256(affected_image) != fixed.OLD_SHA256:
        raise Failure("affected ABL identity mismatch")
    if fixed.sha256(first_fixed_image) != fixed.FIRST_FIXED_SHA256:
        raise Failure("first-fixed IFWI identity mismatch")

    affected_context = _partition_context(affected_image, fixed.OLD_NFTP, "affected")
    first_context = _partition_context(first_fixed_image, fixed.FIRST_FIXED_NFTP, "first-fixed")

    affected_ftpr = fixed.parse_cpd(affected_image, fixed.OLD_FTPR, b"FTPR")
    first_ftpr = fixed.parse_cpd(first_fixed_image, fixed.FIRST_FIXED_FTPR, b"FTPR")
    affected_ftpr_manifest = fixed.member(affected_image, fixed.OLD_FTPR, affected_ftpr, "FTPR.man")
    first_ftpr_manifest = fixed.member(first_fixed_image, fixed.FIRST_FIXED_FTPR, first_ftpr, "FTPR.man")
    fixed.verify_mn2(affected_ftpr_manifest, "affected FTPR.man")
    fixed.verify_mn2(first_ftpr_manifest, "first-fixed FTPR.man")
    affected_syslib, _ = fixed.extract_module(
        affected_image, fixed.OLD_FTPR, affected_ftpr, affected_ftpr_manifest, "syslib"
    )
    first_syslib, _ = fixed.extract_module(
        first_fixed_image, fixed.FIRST_FIXED_FTPR, first_ftpr, first_ftpr_manifest, "syslib"
    )
    affected_kernel, _ = fixed.extract_module(
        affected_image, fixed.OLD_FTPR, affected_ftpr, affected_ftpr_manifest, "kernel"
    )
    first_kernel, _ = fixed.extract_module(
        first_fixed_image, fixed.FIRST_FIXED_FTPR, first_ftpr, first_ftpr_manifest, "kernel"
    )
    if fixed.sha256(affected_syslib) != fixed.OLD_SYSLIB_SHA256:
        raise Failure("affected syslib identity mismatch")
    if fixed.sha256(first_syslib) != fixed.FIRST_FIXED_SYSLIB_SHA256:
        raise Failure("first-fixed syslib identity mismatch")

    modules = {}
    decoded_modules: dict[str, tuple[bytes, bytes]] = {}
    class_names: dict[str, list[str]] = {
        "byte_identical": [],
        "syslib_relocation_only": [],
        "changed_with_unexplained_bytes": [],
        "opaque_changed": [],
    }
    for name in EXPECTED_MODULES:
        affected_value, affected_info = _extract_inventory_module(
            affected_image, fixed.OLD_NFTP, affected_context, name
        )
        first_value, first_info = _extract_inventory_module(
            first_fixed_image, fixed.FIRST_FIXED_NFTP, first_context, name
        )
        item = {
            "affected": affected_info,
            "first_fixed": first_info,
        }
        if affected_value is None or first_value is None:
            if affected_value is not None or first_value is not None:
                raise Failure(f"{name} opaque-status asymmetry")
            raw_differences = differing_byte_count(
                fixed.member(affected_image, fixed.OLD_NFTP, affected_context["entries"], name),
                fixed.member(first_fixed_image, fixed.FIRST_FIXED_NFTP, first_context["entries"], name),
            )
            item["classification"] = "opaque_changed"
            item["opaque_stored_member_differing_byte_count"] = raw_differences
        else:
            decoded_modules[name] = (affected_value, first_value)
            review = relocation_review(
                affected_value,
                first_value,
                affected_syslib,
                first_syslib,
            )
            item["relocation_review"] = review
            if affected_value == first_value:
                item["classification"] = "byte_identical"
            elif review["equal_after_reviewed_external_rel32_normalization"]:
                item["classification"] = "syslib_relocation_only"
            else:
                item["classification"] = "changed_with_unexplained_bytes"
        class_names[item["classification"]].append(name)
        modules[name] = item

    for values in class_names.values():
        values.sort()
    if set(class_names["byte_identical"]) != EXPECTED_IDENTICAL:
        raise Failure("byte-identical module classification drift")
    if set(class_names["syslib_relocation_only"]) != EXPECTED_RELOCATION_ONLY:
        raise Failure("relocation-only module classification drift")
    if set(class_names["opaque_changed"]) != EXPECTED_OPAQUE:
        raise Failure("opaque module classification drift")

    return {
        "schema": SCHEMA,
        "inputs": {
            "affected": {
                "sha256": fixed.OLD_SHA256,
                "nftp_cpd_offset": fixed.OLD_NFTP,
                "nftp_manifest": affected_context["manifest_report"],
                "syslib_sha256": fixed.OLD_SYSLIB_SHA256,
            },
            "first_fixed": {
                "sha256": fixed.FIRST_FIXED_SHA256,
                "nftp_cpd_offset": fixed.FIRST_FIXED_NFTP,
                "nftp_manifest": first_context["manifest_report"],
                "syslib_sha256": fixed.FIRST_FIXED_SYSLIB_SHA256,
            },
        },
        "summary": {
            "module_count": len(modules),
            "decoded_module_count": len(modules) - len(class_names["opaque_changed"]),
            "opaque_module_count": len(class_names["opaque_changed"]),
            "classification_counts": {
                key: len(value) for key, value in class_names.items()
            },
            "classification_modules": class_names,
            "smallest_unexplained_equal_size_modules": sorted(
                (
                    {
                        "name": name,
                        "unexplained_differing_byte_count": item["relocation_review"]["unexplained_differing_byte_count"],
                    }
                    for name, item in modules.items()
                    if item["classification"] == "changed_with_unexplained_bytes"
                    and item["relocation_review"]["eligible_equal_size"]
                ),
                key=lambda entry: (entry["unexplained_differing_byte_count"], entry["name"]),
            )[:10],
        },
        "minimal_length_delta_review": minimal_length_delta_review(
            decoded_modules,
            modules,
            affected_syslib,
            first_syslib,
        ),
        "kernel_message_submit_selector_0x10_review": kernel_message_submit_selector_review(
            affected_kernel,
            first_kernel,
            affected_syslib,
            first_syslib,
        ),
        "modules": modules,
        "boundaries": [
            "Relocation-only means local module bytes normalize to identity after only same-offset E8/E9 rel32 operands targeting hash-bound syslib export stubs are zeroed; it does not prove transitive behavioral identity.",
            "Changed-with-unexplained-bytes identifies a static review priority, not a vulnerability or advisory attribution.",
            "The opaque pavp member is retained with exact stored-member and metadata identities; this tool does not guess the transform represented by nonzero module-extension byte +9.",
            "Embedded signatures prove self-consistency and byte binding only, not external ROM, fuse, Boot Guard, OEM, or installed-unit acceptance.",
            "No firmware module or HECI/MEI endpoint was executed or opened.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--affected-abl", type=Path, required=True)
    parser.add_argument("--first-fixed-ifwi", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(
            fixed.stable_read(args.affected_abl),
            fixed.stable_read(args.first_fixed_ifwi),
        )
    except (Failure, fixed.Failure, OSError, struct.error) as exc:
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
