#!/usr/bin/env python3
"""Audit the exact-static AppLauncher app-ID-300 program/argv path.

Recovered targets are never executed. The analyzer streams the canonical rootfs
through one stable no-follow descriptor, compares the supplied AppLauncher to
that member, invokes identity-bound host LLVM readers, and emits normalized
roles and hashes rather than target bytes, complete option rows, supplied host
paths, requests, commands, or actuation material.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tarfile
from pathlib import Path
from typing import Any, Iterable

from appfumo_boot_activation_boundary import (  # type: ignore
    BoundaryError,
    _HashingReader,
    _branch_target,
    _canonical_hash,
    _canonical_member_name,
    _inventory_line,
    _read_regular,
    _run_tool,
    _same_stat,
    _validate_tool,
    parse_build_id,
    parse_disassembly,
    parse_fdes,
)

SCHEMA_VERSION = 1
TOOL_NAME = "applauncher-app300-argv"
TOOL_VERSION = "1.0.0"
MAX_MANIFEST_SIZE = 2 << 20
MAX_ELF_SIZE = 8 << 20
MAX_ROOTFS_SIZE = 1 << 30
MAX_SELECTED_MEMBER = 8 << 20
MAX_TOOL_SIZE = 16 << 20

ROOTFS = {
    "size": 879109759,
    "sha256": "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84",
    "member_count": 66836,
    "inventory_sha256": "c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c",
    "selected_member": "./app/bin/AppLauncher",
    "external_option_member": "app/bin/CarOption.csv",
    "external_option_present": False,
}
ARTIFACT = {
    "size": 407720,
    "sha256": "c8d6d56bc254ad0731e81f40bd83aa9b3be6b49bcbd8efb291157a06c4a84268",
    "build_id": "0452df1033bd1bbae15727a83d4d56576d8b9444",
}
LLVM = {
    "version": "Homebrew LLVM version 23.1.3",
    "objdump_size": 813808,
    "objdump_sha256": "7b04d723638c0793efbd31b99b2389f36ceb8c803bdc1008e43ea7525958376f",
    "readelf_size": 1805104,
    "readelf_sha256": "80a1f8ffc44c5a1e4dbeaa5c409cd98a01cb2fa73e1ccc2eeb22a3b7ee2e1cb0",
    "instruction_count": 59259,
    "instruction_sha256": "a83cf95ee11850142b5c6b37d7a2d861f48452521aa1d8b4f57fd74c08faa168",
    "fde_count": 436,
    "fde_sha256": "b7d430bbf6dedd5285ffdabe84188d7eb404909550ffc3aaf1f7380a30a664c5",
}
FDE_ROLES = {
    "process-start": (0x163F0, 0x1854D),
    "option-loader-caller": (0x19860, 0x19A3E),
    "dynamic-process-construction": (0x1FD30, 0x1FFCF),
    "option-builder": (0x34510, 0x36A74),
    "table-map-builder": (0x37530, 0x378C9),
    "external-option-loader": (0x378D0, 0x37D54),
    "embedded-table-constructor": (0x37D60, 0x3809E),
    "vehicle-option-selector": (0x380A0, 0x3987A),
}
DIRECT_TRANSFERS = {
    0xA740: ((0x1745D, 0x17EB2, 0x17EE9, 0x18169), ()),
    0x163F0: ((0x1899A, 0x18C35, 0x18FA2, 0x1D875, 0x20207), ()),
    0x1FD30: ((0x204B5,), ()),
    0x34510: ((0x1F9E9, 0x1FEC8, 0x23B6F, 0x23FB2, 0x24ABD, 0x36AC3), ()),
    0x37530: ((0x37F59,), ()),
    0x378D0: ((0x37F19,), ()),
    0x380A0: ((0x19925, 0x38DF0), ()),
}
LITERAL_ROLES = {
    "embedded-table": (0x4BA10, "utf-8", 0x69B5),
    "external-option-path": (0x526F8, "ascii", 22),
    "row-delimiter": (0x5270F, "ascii", 3),
    "field-delimiter": (0x52720, "ascii", 1),
    "vehicle-code-heading": (0x52722, "ascii", 12),
    "update-mode-zero-token": (0x5273B, "ascii", 5),
    "energy-template": (0x52599, "ascii", 6),
    "performance-template": (0x525B5, "ascii", 6),
    "hex-prefix": (0x52713, "ascii", 2),
    "short-hex-prefix": (0x52716, "ascii", 3),
    "performance-one-token": (0x5271A, "ascii", 5),
    "energy-key-prefix": (0x5272F, "ascii", 4),
}
ANCHOR_ADDRESSES = {
    0x16679, 0x1668D,
    0x17430, 0x1744D, 0x17452, 0x17457, 0x1745A, 0x1745D,
    0x1991B, 0x19920, 0x19925,
    0x1FD51, 0x1FD5D, 0x1FD62, 0x1FE28, 0x1FE43, 0x1FE61,
    0x1FEA6, 0x1FEB3, 0x1FEC3, 0x1FEC5, 0x1FEC8, 0x1FECD,
    0x1FED2, 0x1FED8, 0x1FEEB, 0x1FEEF,
    0x35467, 0x3547A, 0x354B0, 0x354C1, 0x354E9,
    0x35C8E, 0x35C9D, 0x35CA8, 0x35CB5, 0x35CD0,
    0x378DE, 0x3790B, 0x37931, 0x37934, 0x3793A, 0x37986,
    0x3798B, 0x3798D, 0x379F0, 0x379F6, 0x37A42, 0x37A47, 0x37A55,
    0x37EC0, 0x37EC7, 0x37ED7, 0x37EEA, 0x37F11, 0x37F19, 0x37F59,
    0x38164, 0x38167, 0x3816F, 0x38173, 0x38177, 0x3817E,
    0x38185, 0x38188, 0x3818B, 0x3818F, 0x38193, 0x38197,
    0x3819B, 0x3819F, 0x381A3, 0x381BF, 0x381E4,
    0x38206, 0x38217, 0x3826A, 0x3827B, 0x382CE, 0x382E3,
    0x38303, 0x38336, 0x3833A, 0x38347, 0x38353, 0x383BE,
    0x383C7, 0x383D4, 0x38463, 0x38498, 0x3851E, 0x38531,
    0x38537, 0x38543, 0x38545, 0x3857F, 0x385AF, 0x385BE,
    0x385C3, 0x385C8, 0x3862C, 0x38700, 0x3870D, 0x3874A,
    0x38758, 0x3878B, 0x389C0, 0x389F3, 0x38A14, 0x38A1E,
    0x38A38, 0x38EB0,
    0x38D05, 0x38D0C, 0x38D13, 0x38D16, 0x38D1C, 0x38D23,
    0x38D29, 0x38D30, 0x38D37, 0x38D3B, 0x38D8B, 0x38D92,
    0x38DC0, 0x38DF0, 0x38DF5,
}


def _pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in rows:
        if key in out:
            raise BoundaryError(f"manifest contains duplicate JSON key: {key}")
        out[key] = value
    return out


def _object(value: Any, keys: Iterable[str], what: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != set(keys):
        raise BoundaryError(f"{what} object keys mismatch")
    return value


def _array(value: Any, what: str, maximum: int = 4096) -> list[Any]:
    if type(value) is not list or len(value) > maximum:
        raise BoundaryError(f"{what} must be a bounded array")
    return value


def _integer(value: Any, what: str, maximum: int = (1 << 64) - 1) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise BoundaryError(f"{what} must be a bounded non-Boolean integer")
    return value


def _string(value: Any, what: str, maximum: int = 4096) -> str:
    if type(value) is not str or not value or len(value) > maximum:
        raise BoundaryError(f"{what} must be a bounded non-empty string")
    return value


def _digest(value: Any, what: str) -> str:
    text = _string(value, what, 64)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise BoundaryError(f"{what} must be lowercase SHA-256")
    return text


def _reject_alias(path: Path, what: str) -> os.stat_result:
    try:
        row = path.lstat()
    except OSError as exc:
        raise BoundaryError(f"cannot lstat {what}: {exc.strerror}") from exc
    if not stat.S_ISREG(row.st_mode) or row.st_nlink != 1:
        raise BoundaryError(f"{what} is linked, aliased, or non-regular")
    return row


def load_manifest(path: Path) -> dict[str, Any]:
    _reject_alias(path, "manifest")
    raw = _read_regular(path, MAX_MANIFEST_SIZE, "manifest")
    try:
        top = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BoundaryError("manifest is not strict UTF-8 JSON") from exc
    top = _object(top, {"schema_version", "rootfs", "artifact", "llvm", "expected"}, "manifest")
    if _integer(top["schema_version"], "schema_version") != SCHEMA_VERSION:
        raise BoundaryError("unsupported manifest schema")
    if _object(top["rootfs"], ROOTFS.keys(), "rootfs") != ROOTFS:
        raise BoundaryError("rootfs expectation drift")
    if _object(top["artifact"], ARTIFACT.keys(), "artifact") != ARTIFACT:
        raise BoundaryError("artifact expectation drift")
    if _object(top["llvm"], LLVM.keys(), "llvm") != LLVM:
        raise BoundaryError("LLVM expectation drift")
    expected = _object(top["expected"], {"fdes", "direct_transfers", "anchors", "literals"}, "expected")
    fdes: dict[str, tuple[int, int]] = {}
    for index, item in enumerate(_array(expected["fdes"], "fdes", 64)):
        row = _object(item, {"role", "start", "end"}, f"fde {index}")
        role = _string(row["role"], "fde.role", 96)
        if role in fdes:
            raise BoundaryError("duplicate FDE role")
        fdes[role] = (_integer(row["start"], "fde.start", MAX_ELF_SIZE),
                      _integer(row["end"], "fde.end", MAX_ELF_SIZE))
    if fdes != FDE_ROLES:
        raise BoundaryError("FDE expectation drift")
    transfers: dict[int, tuple[tuple[int, ...], tuple[int, ...]]] = {}
    for index, item in enumerate(_array(expected["direct_transfers"], "transfers", 64)):
        row = _object(item, {"target", "calls", "jumps"}, f"transfer {index}")
        target = _integer(row["target"], "target", MAX_ELF_SIZE)
        if target in transfers:
            raise BoundaryError("duplicate transfer target")
        calls = tuple(_integer(x, "call", MAX_ELF_SIZE) for x in _array(row["calls"], "calls", 128))
        jumps = tuple(_integer(x, "jump", MAX_ELF_SIZE) for x in _array(row["jumps"], "jumps", 128))
        if calls != tuple(sorted(set(calls))) or jumps != tuple(sorted(set(jumps))):
            raise BoundaryError("transfer rows are not unique and sorted")
        transfers[target] = (calls, jumps)
    if transfers != DIRECT_TRANSFERS:
        raise BoundaryError("direct-transfer expectation drift")
    anchors: dict[int, str] = {}
    for index, item in enumerate(_array(expected["anchors"], "anchors", 1024)):
        row = _object(item, {"va", "sha256"}, f"anchor {index}")
        va = _integer(row["va"], "anchor.va", MAX_ELF_SIZE)
        if va in anchors:
            raise BoundaryError("duplicate anchor")
        anchors[va] = _digest(row["sha256"], "anchor.sha256")
    if set(anchors) != ANCHOR_ADDRESSES:
        raise BoundaryError("anchor address-set drift")
    literals: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(_array(expected["literals"], "literals", 64)):
        row = _object(item, {"role", "va", "encoding", "length", "sha256"}, f"literal {index}")
        role = _string(row["role"], "literal.role", 96)
        if role in literals:
            raise BoundaryError("duplicate literal role")
        literals[role] = {
            "va": _integer(row["va"], "literal.va", MAX_ELF_SIZE),
            "encoding": _string(row["encoding"], "literal.encoding", 32),
            "length": _integer(row["length"], "literal.length", 1 << 20),
            "sha256": _digest(row["sha256"], "literal.sha256"),
        }
    shape = {role: {"va": va, "encoding": enc, "length": length}
             for role, (va, enc, length) in LITERAL_ROLES.items()}
    if {role: {k: row[k] for k in ("va", "encoding", "length")}
        for role, row in literals.items()} != shape:
        raise BoundaryError("literal role/range drift")
    return {"anchors": anchors, "literals": literals}


def _stream_member(archive: tarfile.TarFile, member: tarfile.TarInfo) -> bytes:
    if member.size > MAX_SELECTED_MEMBER:
        raise BoundaryError("selected member exceeds size bound")
    stream = archive.extractfile(member)
    if stream is None:
        raise BoundaryError("selected member cannot be streamed")
    value = stream.read(member.size + 1)
    if len(value) != member.size:
        raise BoundaryError("selected member is truncated or oversized")
    return value


def _rootfs_snapshot(path: Path) -> tuple[bytes, dict[str, Any]]:
    before = _reject_alias(path, "canonical rootfs")
    if before.st_size > MAX_ROOTFS_SIZE:
        raise BoundaryError("canonical rootfs exceeds size bound")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise BoundaryError(f"cannot open canonical rootfs: {exc.strerror}") from exc
    selected: bytes | None = None
    count = 0
    inventory = hashlib.sha256()
    seen: set[str] = set()
    external_present = False
    try:
        with os.fdopen(descriptor, "rb") as raw_handle:
            opened = os.fstat(raw_handle.fileno())
            if not _same_stat(before, opened) or not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                raise BoundaryError("canonical rootfs changed before stable open")
            reader = _HashingReader(raw_handle)
            with tarfile.open(fileobj=reader, mode="r|gz") as archive:
                for index, member in enumerate(archive):
                    count += 1
                    inventory.update(_inventory_line(index, member))
                    canonical = _canonical_member_name(member.name)
                    if canonical in seen:
                        raise BoundaryError("rootfs contains duplicate or aliased member names")
                    seen.add(canonical)
                    if canonical == ROOTFS["external_option_member"]:
                        external_present = True
                    if canonical != _canonical_member_name(ROOTFS["selected_member"]):
                        continue
                    if selected is not None or member.name != ROOTFS["selected_member"]:
                        raise BoundaryError("selected AppLauncher member is duplicated or aliased")
                    if (not member.isreg() or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                            or member.linkname or member.mode != 0o755 or member.size != ARTIFACT["size"]):
                        raise BoundaryError("selected AppLauncher member metadata drift")
                    selected = _stream_member(archive, member)
            while reader.read(1 << 20):
                pass
            archive_hash = reader.digest.hexdigest()
            descriptor_after = os.fstat(raw_handle.fileno())
    except (OSError, tarfile.TarError, UnicodeEncodeError) as exc:
        if isinstance(exc, BoundaryError):
            raise
        raise BoundaryError(f"cannot stream canonical rootfs: {type(exc).__name__}") from exc
    try:
        after = path.lstat()
    except OSError as exc:
        raise BoundaryError(f"cannot revalidate canonical rootfs: {exc.strerror}") from exc
    if not _same_stat(opened, descriptor_after) or not _same_stat(before, after):
        raise BoundaryError("canonical rootfs changed during streaming")
    if (opened.st_size != ROOTFS["size"] or archive_hash != ROOTFS["sha256"]
            or count != ROOTFS["member_count"] or inventory.hexdigest() != ROOTFS["inventory_sha256"]):
        raise BoundaryError("canonical rootfs identity or inventory drift")
    if external_present != ROOTFS["external_option_present"]:
        raise BoundaryError("canonical external-option member state drift")
    if selected is None or len(selected) != ARTIFACT["size"] or hashlib.sha256(selected).hexdigest() != ARTIFACT["sha256"]:
        raise BoundaryError("canonical AppLauncher member identity drift")
    return selected, {
        "size": opened.st_size,
        "sha256": archive_hash,
        "member_count": count,
        "inventory_sha256": inventory.hexdigest(),
        "external_option_member_present": external_present,
    }


def _literal(raw: bytes, row: dict[str, Any]) -> bytes:
    start, length = row["va"], row["length"]
    end = start + length
    if end > len(raw):
        raise BoundaryError("literal exceeds artifact")
    value = raw[start:end]
    try:
        decoded = value.decode(row["encoding"])
    except UnicodeDecodeError as exc:
        raise BoundaryError("literal encoding drift") from exc
    if len(decoded) == 0 or "\x00" in decoded:
        raise BoundaryError("literal content drift")
    return value


def _transfers(instructions: list[Any], target: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    calls = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("call") and _branch_target(item) == target)
    jumps = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("j") and _branch_target(item) == target)
    return calls, jumps


def _table_contract(value: bytes) -> dict[str, Any]:
    text = value.decode("utf-8", "strict")
    delimiter = "END            "
    if text.count(delimiter) != 128:
        raise BoundaryError("embedded table delimiter inventory drift")
    rows = text.split(delimiter)
    if len(rows) != 129:
        raise BoundaryError("embedded table row inventory drift")
    matches = [(index, row) for index, row in enumerate(rows) if row.startswith("NE,")]
    if len(matches) != 1:
        raise BoundaryError("recovered NE row is absent or ambiguous")
    index, row = matches[0]
    fields = row.split(",")
    if len(fields) != 38 or fields[-1] != "":
        raise BoundaryError("recovered NE row field shape drift")
    normal_matches = []
    for candidate_index, candidate in enumerate(rows):
        candidate_fields = candidate.split(",")
        if (len(candidate_fields) == 38 and candidate_fields[2].lower() == "0x26"
                and "-et:8" in candidate_fields):
            normal_matches.append(candidate_index)
    if normal_matches != [50]:
        raise BoundaryError("recovered normal-branch selection is not unique")
    options = fields[20:-1]
    expected = [
        "-et:8", "-by:0", "-gui:3", "-sc:1", "-vc:65", "-kt:0", "-dn:0",
        "-nm:0", "-p2s2:1", "-ke:na", "-pf:0", "-pvv:0x26", "-os:1",
        "-osr:1", "-un:0", "-er:0", "-is:0",
    ]
    if options != expected:
        raise BoundaryError("recovered NE option sequence drift")
    option_hash = hashlib.sha256(("\n".join(options) + "\n").encode("utf-8")).hexdigest()
    row_hash = hashlib.sha256(row.encode("utf-8")).hexdigest()
    return {
        "delimiter_occurrences": 128,
        "split_component_count": 129,
        "selected_row_role": "recovered-NE-EUR-fallback-row",
        "selected_row_split_index": index,
        "selected_row_field_count_including_terminal_empty": len(fields),
        "selected_row_sha256": row_hash,
        "normal_branch_matching_row_count": len(normal_matches),
        "selected_option_count": len(options),
        "selected_option_sequence_sha256": option_hash,
        "selected_option_roles": [
            "energy-type", "brand-type", "gui-generation", "screen-control", "vehicle-class",
            "korean-type", "day-night", "n-mode", "phone-projection-split-screen", "emblem",
            "performance-feature", "parent-vehicle-value", "ota-support", "ota-region",
            "update-mode", "engineering-region", "isr-support",
        ],
        "update_mode_option_ordinal_zero_based": 14,
        "update_mode_value_role": "zero",
        "owner_unit_selected_this_row": None,
    }


def analyze(rootfs: Path, app: Path, manifest_path: Path, objdump: Path, readelf: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    canonical, rootfs_report = _rootfs_snapshot(rootfs)
    app_before = _reject_alias(app, "AppLauncher")
    raw = _read_regular(app, MAX_ELF_SIZE, "AppLauncher")
    if len(raw) != ARTIFACT["size"] or hashlib.sha256(raw).hexdigest() != ARTIFACT["sha256"] or raw != canonical:
        raise BoundaryError("supplied AppLauncher does not equal the canonical member")
    _validate_tool(objdump, LLVM["version"], LLVM["objdump_size"], LLVM["objdump_sha256"], "llvm-objdump")
    _validate_tool(readelf, LLVM["version"], LLVM["readelf_size"], LLVM["readelf_sha256"], "llvm-readelf")
    notes = _run_tool([str(readelf), "--notes", str(app)], "readelf notes")
    if parse_build_id(notes) != ARTIFACT["build_id"]:
        raise BoundaryError("AppLauncher Build ID drift")
    disassembly = _run_tool([str(objdump), "--disassemble", "--no-show-raw-insn", str(app)],
                            "objdump disassembly", 64 << 20)
    instructions = parse_disassembly(disassembly)
    instruction_hash = _canonical_hash(item.canonical for item in instructions)
    if len(instructions) != LLVM["instruction_count"] or instruction_hash != LLVM["instruction_sha256"]:
        raise BoundaryError("complete AppLauncher instruction inventory drift")
    unwind = _run_tool([str(readelf), "--unwind", str(app)], "readelf unwind", 16 << 20)
    fdes = parse_fdes(unwind)
    fde_hash = _canonical_hash(f"{start:x}\t{end:x}" for start, end in fdes)
    if len(fdes) != LLVM["fde_count"] or fde_hash != LLVM["fde_sha256"]:
        raise BoundaryError("complete AppLauncher FDE inventory drift")
    if any(bounds not in set(fdes) for bounds in FDE_ROLES.values()):
        raise BoundaryError("required FDE range is absent")
    by_va = {item.address: item for item in instructions}
    for va, digest in manifest["anchors"].items():
        item = by_va.get(va)
        if item is None or hashlib.sha256(item.canonical.encode("utf-8")).hexdigest() != digest:
            raise BoundaryError(f"machine-anchor drift at 0x{va:x}")
    for target, expected in DIRECT_TRANSFERS.items():
        if _transfers(instructions, target) != expected:
            raise BoundaryError(f"direct-transfer drift for 0x{target:x}")
    literal_hashes: dict[str, str] = {}
    literal_values: dict[str, bytes] = {}
    for role, row in manifest["literals"].items():
        value = _literal(raw, row)
        digest = hashlib.sha256(value).hexdigest()
        if digest != row["sha256"]:
            raise BoundaryError(f"literal identity drift for {role}")
        literal_hashes[role] = digest
        literal_values[role] = value
    table = _table_contract(literal_values["embedded-table"])
    app_after = app.lstat()
    if not _same_stat(app_before, app_after):
        raise BoundaryError("AppLauncher changed during analysis")
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "rootfs": rootfs_report,
        "artifact": {"role": "canonical-rootfs-AppLauncher", **ARTIFACT},
        "static_contract": {
            "table_source": {
                "embedded_source_range": ["0x4ba10", "0x523c5"],
                "embedded_source_size": 0x69B5,
                "embedded_source_sha256": literal_hashes["embedded-table"],
                "active_source_field": "option-loader-object-plus-0x18",
                "embedded_fallback_copy_field": "option-loader-object-plus-0x20",
                "external_path_literal_sha256": literal_hashes["external-option-path"],
                "external_loader_behavior": "if-file-exists-and-read-open-succeeds-then-read-all-decode-utf8-and-replace-plus-0x18; absent-or-open-failed-retains-embedded-source",
                "invalid_or_nonmatching_external_behavior": "if-selected-option-list-remains-empty-and-fallback-mode-flag-is-zero-copy-plus-0x20-to-plus-0x18-and-reinvoke-selector-with-fallback-mode-one",
                "recursive_fallback_call_site": "0x38df0",
                "fallback_is_bounded_to_one_transition": True,
                "canonical_external_member_present": rootfs_report["external_option_member_present"],
                "canonical_absence_is_owner_unit_runtime_absence": False,
            },
            "table": table,
            "selector_input_provenance": {
                "caller_fde": ["0x19860", "0x19a3e"],
                "call_site": "0x19925",
                "source_object": "caller-field-plus-0x18",
                "source_offsets_in_logical_argument_order": [
                    "0x60", "0x3f", "0x1d-four-bytes", "0x3e", "0x32", "0xad",
                    "0xc0", "0xc1", "boolean-from-0x84", "0x3d", "0x3a", "0x83",
                ],
                "initial_fallback_mode": 0,
                "selector_destination_fields": {
                    "argument-1": "loader-plus-0x41", "argument-2": "loader-plus-0x42",
                    "argument-3": "loader-plus-0x44", "argument-4": "loader-plus-0x48",
                    "argument-5": "loader-plus-0x49", "argument-6": "loader-plus-0x51",
                    "argument-7": "loader-plus-0x53", "argument-8": "loader-plus-0x54",
                    "argument-9": "loader-plus-0x55", "argument-10": "loader-plus-0x56",
                    "argument-11": "loader-plus-0x57", "argument-12": "loader-plus-0x58"
                },
            },
            "recovered_row_selection_predicate": {
                "normal_branch_condition": "formatted-performance-argument-is-not-the-performance-one-token",
                "vehicle_key": "argument-4-formatted-as-lowercase-0x-prefixed-two-digit-hex",
                "vehicle_key_required_value_role": "0x26",
                "energy_key": "argument-7-formatted-with-energy-template",
                "energy_key_required_value_role": "8",
                "comparison": "case-folded-vehicle-equality-and-exact-energy-token-equality",
                "matching_embedded_data_rows": 1,
                "matching_embedded_split_index": 50,
                "region_column_participates_in_predicate": False,
                "EUR_is_selected_row_data_not_runtime_region_proof": True,
                "owner_unit_runtime_predicate_satisfied": None,
            },
            "process_construction": {
                "owner_fde": ["0x1fd30", "0x1ffcf"],
                "accepted_app_id_range": [1, 1024],
                "allocation_site": "0x1fe28",
                "app_id_store": {"site": "0x1fe43", "field": "AppProcess+0x20"},
                "program_store": {"site": "0x1fe61", "field": "AppProcess+0x58"},
                "option_builder_call": {"site": "0x1fec8", "target": "0x34510", "mode": 0},
                "generated_arguments_store": {"sites": ["0x1fed2", "0x1feef"], "field": "AppProcess+0x60"},
                "app_id_300_uses_this_ordinary_path": True,
            },
            "option_builder": {
                "owner_fde": ["0x34510", "0x36a74"],
                "selected_option_source": "option-loader-object-plus-0x28",
                "selected_option_append_loop": ["0x35c8e", "0x35cd2"],
                "selected_options_preserve_list_order": True,
                "recovered_row_selected_options_would_be_appended": 17,
                "whole_generated_argv_fixed_by_static_row_alone": False,
                "reason": "builder-also-uses-runtime-fields-runtime-files-and-conditional-options",
            },
            "process_start": {
                "owner_fde": ["0x163f0", "0x1854d"],
                "argument_list_address_binding": {"site": "0x16679", "source": "AppProcess+0x60", "call_register": "rdx"},
                "program_binding": {"site": "0x17430", "source": "AppProcess+0x58", "call_register": "rsi"},
                "qprocess_start_site": "0x1745d",
                "qprocess_open_mode_immediate": 3,
                "call_receiver": "AppProcess-as-QProcess",
            },
            "causal_chain": [
                "dynamic-helper-stores-requested-app-id-and-program",
                "dynamic-helper-calls-option-builder-mode-zero",
                "dynamic-helper-stores-generated-QStringList-at-AppProcess-plus-0x60",
                "process-start-binds-AppProcess-plus-0x58-as-program",
                "process-start-binds-AppProcess-plus-0x60-as-argument-list",
                "process-start-calls-QProcess-start",
            ],
        },
        "whole_inventory": {
            "instruction_count": len(instructions),
            "instruction_sha256": instruction_hash,
            "fde_count": len(fdes),
            "fde_sha256": fde_hash,
            "machine_anchor_count": len(ANCHOR_ADDRESSES),
            "direct_transfer_target_count": len(DIRECT_TRANSFERS),
        },
        "runtime_unknowns": {
            "installed_binary_and_data_equal_recovered_image": None,
            "owner_unit_external_option_file_state": None,
            "owner_unit_vehicle_model_region_fields": None,
            "owner_unit_selects_recovered_NE_row": None,
            "whole_runtime_argument_list": None,
            "dbus_delivery": None,
            "qprocess_acceptance": None,
            "child_creation_and_exec_success": None,
            "child_credentials_and_smack_label": None,
            "update_acceptance_or_partition_write": None,
            "boot_acceptance_or_persistence": None,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rootfs", type=Path, required=True)
    parser.add_argument("--applauncher", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--objdump", type=Path, required=True)
    parser.add_argument("--readelf", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        result = analyze(args.rootfs, args.applauncher, args.manifest, args.objdump, args.readelf)
        payload = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True).encode("utf-8") + b"\n"
        sys.stdout.buffer.write(payload)
        return 0
    except BoundaryError as exc:
        sys.stderr.buffer.write((f"error: {exc}\n").encode("utf-8"))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
