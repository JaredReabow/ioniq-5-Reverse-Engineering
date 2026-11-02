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
        "shared_return_epilogue": {
            "affected_runtime_range": [0x8BDB0, 0x8BDCF],
            "first_fixed_runtime_range": [0x8BD52, 0x8BD71],
            "affected_sha256": sha256(affected_epilogue),
            "first_fixed_sha256": sha256(first_epilogue),
            "only_change": "cmp eax immediate 0x000000ff to 0x00000102",
        },
        "kernel_global_immediate_census": {
            **global_immediates,
            "affected_total_site_count": 15,
            "first_fixed_total_site_count": 15,
            "interpretation_boundary": "The same numeric change occurs in fifteen MOV/CMP sites across each complete kernel, so the selector-0x10 uses are part of a kernel-wide status/sentinel renumbering candidate rather than isolated proof of message-validation logic.",
        },
        "affected_syslib_selector_wrapper_runtime_range": [0x16F8F, 0x16FB3],
        "first_fixed_syslib_selector_wrapper_runtime_range": [0x16FB1, 0x16FD5],
        "affected_syslib_selector_wrapper_sha256": sha256(affected_wrapper),
        "first_fixed_syslib_selector_wrapper_sha256": sha256(first_wrapper),
        "syslib_wrapper_builds_syscall_value": "(selector_byte << 24) | 0x00010000 | argument_size_word",
        "reviewed_submit_syscall_value": 0x10010040,
        "attribution_boundary": "The changed 0x10 kernel handler is on the exact path used by the eleven reviewed message-length sites, but the same 0xff-to-0x102 change appears at fifteen MOV/CMP sites kernel-wide, including the directly called helper's MOV EDX return path. Its semantic name, reason for the plus-three renumbering, message dword-zero meaning, HECI reachability, attacker control, and CVE-2018-12147 attribution remain unproved.",
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
