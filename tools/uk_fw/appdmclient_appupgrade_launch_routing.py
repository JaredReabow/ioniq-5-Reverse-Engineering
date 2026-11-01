#!/usr/bin/env python3
"""Audit the exact-static AppDMClient AppUpgrade launch-routing contract.

Recovered targets are never executed. The tool identity-binds one supported
AppDMClient ELF, invokes only identity-bound host LLVM readers, validates a
strict manifest, and emits a deterministic static report with runtime facts
left unknown.
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
    _branch_target,
    _canonical_hash,
    _read_regular,
    _run_tool,
    _same_stat,
    _stat_regular,
    _validate_tool,
    parse_build_id,
    parse_disassembly,
    parse_fdes,
)

SCHEMA_VERSION = 1
TOOL_NAME = "appdmclient-appupgrade-launch-routing"
TOOL_VERSION = "1.0.1"
MAX_ELF_SIZE = 64 << 20
MAX_MANIFEST_SIZE = 2 << 20
MAX_TOOL_SIZE = 16 << 20
MAX_ROOTFS_SIZE = 1 << 30

ROOTFS = {
    "size": 879109759,
    "sha256": "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84",
    "member": "./app/bin/AppDMClient",
}
ARTIFACT = {
    "size": 2226072,
    "sha256": "9a1fb796d7ac24fcce71c16e3dbee9306c888f43e705ee081f41b7d473978bd0",
    "build_id": "b2dbcc5231f444d8f1dd68eb7a2376323ce805df",
}
LLVM = {
    "version": "Homebrew LLVM version 23.1.3",
    "objdump_size": 813808,
    "objdump_sha256": "7b04d723638c0793efbd31b99b2389f36ceb8c803bdc1008e43ea7525958376f",
    "readelf_size": 1805104,
    "readelf_sha256": "80a1f8ffc44c5a1e4dbeaa5c409cd98a01cb2fa73e1ccc2eeb22a3b7ee2e1cb0",
    "instruction_count": 321113,
    "instruction_sha256": "77c0187fc865feaf9ce6bac45ef22d6e3eef29981637190fdf1d225c6928a39d",
    "fde_count": 2418,
    "fde_sha256": "48598865977ec790c555d4441e15c0ec7501d4999d5f66070d70b686f94c4301",
}
FDE_ROLES = {
    "executable-validator": (0x70B50, 0x712B9),
    "timer-relaunch-caller": (0x712C0, 0x71C53),
    "staging-and-routing": (0x7FF60, 0x830E4),
    "standby-relaunch-caller": (0x87400, 0x886E7),
    "launch-proxy": (0x8C0C0, 0x8C2AB),
}
DIRECT_TRANSFERS = {
    0x8C0C0: ((0x71A0A, 0x818F6, 0x8201D, 0x8817E), ()),
}
LITERAL_ROLES = {
    "staged-base": (0x17397F, "utf-8", 15),
    "source-executable-template": (0x17FFFF, "utf-8", 13),
    "route-marker-template": (0x175445, "utf-8", 25),
    "launch-name": (0x187644, "utf-8", 10),
    "launch-method": (0x17C678, "utf-16-le", 6),
}
ANCHOR_ADDRESSES = {
    0x70B50, 0x70B82, 0x70B8A, 0x70B91, 0x70B9F, 0x70BA4,
    0x70E13, 0x70E20, 0x70F5C, 0x70F6C,
    0x71090, 0x7109E, 0x710A9, 0x710B4, 0x711B8, 0x711CD,
    0x71654, 0x7165B, 0x71661, 0x7167F, 0x716A9,
    0x716E2, 0x716F8, 0x716FA,
    0x719D5, 0x719E9, 0x719ED, 0x719F2, 0x719F5, 0x71A07, 0x71A0A,
    0x7FF69,
    0x80165, 0x80189, 0x80192, 0x80196, 0x801AB, 0x801E1, 0x801EA, 0x801EF,
    0x80895, 0x80899, 0x8089C, 0x808A1, 0x808A3,
    0x80A24, 0x80A2E,
    0x80F20, 0x80F2A, 0x80F3F, 0x80F42, 0x80F48, 0x80F50,
    0x80F58, 0x80F68, 0x80F6B, 0x80F92, 0x80F95, 0x80F98,
    0x80F9D, 0x80FA7, 0x80FAA, 0x80FB0,
    0x818D7, 0x818E4, 0x818E7, 0x818EC, 0x818F0, 0x818F3, 0x818F6,
    0x81FF0, 0x81FFF, 0x82003, 0x8200B, 0x8200E, 0x82013,
    0x82017, 0x8201A, 0x8201D,
    0x877F0, 0x87815, 0x8781A, 0x8781C,
    0x87D13, 0x87D18, 0x87D1A, 0x87E00, 0x87EF8, 0x87F2E, 0x87F31,
    0x88002, 0x8800B, 0x88011, 0x8801A, 0x88047, 0x88057, 0x8805A,
    0x88154, 0x88163, 0x88168, 0x8816B,
    0x8816E, 0x8817E,
    0x8C0C0, 0x8C0C4, 0x8C0D1, 0x8C0D5, 0x8C0F3, 0x8C0F7,
    0x8C109, 0x8C115, 0x8C120, 0x8C12C, 0x8C131, 0x8C139,
    0x8C149, 0x8C154, 0x8C15F, 0x8C181, 0x8C184, 0x8C187,
    0x82A9C, 0x82AA6,
    0x8C18A, 0x8C194, 0x8C199, 0x8C19E, 0x8C1A1, 0x8C1AC, 0x8C1F1,
}


def _reject_alias(path: Path, what: str) -> os.stat_result:
    try:
        row = path.lstat()
    except OSError as exc:
        raise BoundaryError(f"cannot lstat {what}: {exc.strerror}") from exc
    if not stat.S_ISREG(row.st_mode) or row.st_nlink != 1:
        raise BoundaryError(f"{what} is linked, aliased, or non-regular")
    return row


def _pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in rows:
        if key in out:
            raise BoundaryError(f"manifest contains duplicate JSON key: {key}")
        out[key] = value
    return out


def _object(value: Any, keys: Iterable[str], what: str) -> dict[str, Any]:
    required = set(keys)
    if type(value) is not dict:
        raise BoundaryError(f"{what} must be an object")
    actual = set(value)
    if actual != required:
        raise BoundaryError(
            f"{what} keys mismatch: missing={sorted(required-actual)}, extra={sorted(actual-required)}"
        )
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


def _hex_id(value: Any, what: str) -> str:
    text = _string(value, what, 128)
    if not re.fullmatch(r"[0-9a-f]+", text):
        raise BoundaryError(f"{what} must be lowercase hexadecimal")
    return text


def load_manifest(path: Path) -> dict[str, Any]:
    _reject_alias(path, "manifest")
    raw = _read_regular(path, MAX_MANIFEST_SIZE, "manifest")
    try:
        top = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BoundaryError("manifest is not valid strict UTF-8 JSON") from exc
    top = _object(top, {"schema_version", "rootfs", "artifact", "llvm", "expected"}, "manifest")
    if _integer(top["schema_version"], "schema_version") != SCHEMA_VERSION:
        raise BoundaryError("unsupported manifest schema version")

    rootfs = _object(top["rootfs"], ROOTFS.keys(), "rootfs")
    parsed_rootfs = {
        "size": _integer(rootfs["size"], "rootfs.size", MAX_ROOTFS_SIZE),
        "sha256": _digest(rootfs["sha256"], "rootfs.sha256"),
        "member": _string(rootfs["member"], "rootfs.member", 256),
    }
    if parsed_rootfs != ROOTFS:
        raise BoundaryError("rootfs expectation drift")

    artifact = _object(top["artifact"], ARTIFACT.keys(), "artifact")
    parsed_artifact = {
        "size": _integer(artifact["size"], "artifact.size", MAX_ELF_SIZE),
        "sha256": _digest(artifact["sha256"], "artifact.sha256"),
        "build_id": _hex_id(artifact["build_id"], "artifact.build_id"),
    }
    if parsed_artifact != ARTIFACT:
        raise BoundaryError("artifact expectation drift")

    llvm = _object(top["llvm"], LLVM.keys(), "llvm")
    parsed_llvm = {
        "version": _string(llvm["version"], "llvm.version", 128),
        "objdump_size": _integer(llvm["objdump_size"], "llvm.objdump_size", MAX_TOOL_SIZE),
        "objdump_sha256": _digest(llvm["objdump_sha256"], "llvm.objdump_sha256"),
        "readelf_size": _integer(llvm["readelf_size"], "llvm.readelf_size", MAX_TOOL_SIZE),
        "readelf_sha256": _digest(llvm["readelf_sha256"], "llvm.readelf_sha256"),
        "instruction_count": _integer(llvm["instruction_count"], "llvm.instruction_count", 2_000_000),
        "instruction_sha256": _digest(llvm["instruction_sha256"], "llvm.instruction_sha256"),
        "fde_count": _integer(llvm["fde_count"], "llvm.fde_count", 100_000),
        "fde_sha256": _digest(llvm["fde_sha256"], "llvm.fde_sha256"),
    }
    if parsed_llvm != LLVM:
        raise BoundaryError("LLVM expectation drift")

    expected = _object(top["expected"], {"fdes", "direct_transfers", "anchors", "literals"}, "expected")

    fdes: dict[str, tuple[int, int]] = {}
    for index, item in enumerate(_array(expected["fdes"], "fdes", 64)):
        row = _object(item, {"role", "start", "end"}, f"fde {index}")
        role = _string(row["role"], "fde.role", 96)
        if role in fdes:
            raise BoundaryError("duplicate FDE role")
        fdes[role] = (
            _integer(row["start"], "fde.start", MAX_ELF_SIZE),
            _integer(row["end"], "fde.end", MAX_ELF_SIZE),
        )
    if fdes != FDE_ROLES:
        raise BoundaryError("FDE role/range drift")

    transfers: dict[int, tuple[tuple[int, ...], tuple[int, ...]]] = {}
    for index, item in enumerate(_array(expected["direct_transfers"], "direct_transfers", 64)):
        row = _object(item, {"target", "calls", "jumps"}, f"transfer {index}")
        target = _integer(row["target"], "transfer.target", MAX_ELF_SIZE)
        if target in transfers:
            raise BoundaryError("duplicate direct-transfer target")
        calls = tuple(_integer(value, "transfer.call", MAX_ELF_SIZE)
                      for value in _array(row["calls"], "transfer.calls", 128))
        jumps = tuple(_integer(value, "transfer.jump", MAX_ELF_SIZE)
                      for value in _array(row["jumps"], "transfer.jumps", 128))
        if calls != tuple(sorted(set(calls))) or jumps != tuple(sorted(set(jumps))):
            raise BoundaryError("direct-transfer rows must be unique and sorted")
        transfers[target] = (calls, jumps)
    if transfers != DIRECT_TRANSFERS:
        raise BoundaryError("direct-transfer expectation drift")

    anchors: dict[int, str] = {}
    for index, item in enumerate(_array(expected["anchors"], "anchors", 1024)):
        row = _object(item, {"va", "sha256"}, f"anchor {index}")
        va = _integer(row["va"], "anchor.va", MAX_ELF_SIZE)
        if va in anchors:
            raise BoundaryError("duplicate machine anchor")
        anchors[va] = _digest(row["sha256"], "anchor.sha256")
    if set(anchors) != ANCHOR_ADDRESSES:
        raise BoundaryError("machine-anchor address set drift")

    literals: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(_array(expected["literals"], "literals", 64)):
        row = _object(item, {"role", "va", "encoding", "length", "sha256"}, f"literal {index}")
        role = _string(row["role"], "literal.role", 96)
        if role in literals:
            raise BoundaryError("duplicate literal role")
        parsed = {
            "va": _integer(row["va"], "literal.va", MAX_ELF_SIZE),
            "encoding": _string(row["encoding"], "literal.encoding", 32),
            "length": _integer(row["length"], "literal.length", 1024),
            "sha256": _digest(row["sha256"], "literal.sha256"),
        }
        literals[role] = parsed
    expected_literal_shape = {
        role: {"va": va, "encoding": encoding, "length": length}
        for role, (va, encoding, length) in LITERAL_ROLES.items()
    }
    if {role: {key: row[key] for key in ("va", "encoding", "length")}
        for role, row in literals.items()} != expected_literal_shape:
        raise BoundaryError("literal role/range drift")

    return {"rootfs": parsed_rootfs, "artifact": parsed_artifact, "llvm": parsed_llvm, "expected": {
        "fdes": fdes, "direct_transfers": transfers, "anchors": anchors, "literals": literals,
    }}


def _transfers(instructions: list[Any], target: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    calls = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("call") and _branch_target(item) == target)
    jumps = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("j") and _branch_target(item) == target)
    return calls, jumps


def _literal_bytes(raw: bytes, row: dict[str, Any]) -> bytes:
    unit = 2 if row["encoding"] == "utf-16-le" else 1
    start = row["va"]
    end = start + row["length"] * unit
    if row["encoding"] not in {"utf-8", "utf-16-le"} or end > len(raw):
        raise BoundaryError("literal range or encoding is invalid")
    value = raw[start:end]
    try:
        decoded = value.decode(row["encoding"])
    except UnicodeDecodeError as exc:
        raise BoundaryError("literal is not valid in its declared encoding") from exc
    if len(decoded) != row["length"] or "\x00" in decoded:
        raise BoundaryError("literal length or content drift")
    return value


def _hash_open_file(handle: Any) -> str:
    digest = hashlib.sha256()
    while True:
        block = handle.read(1 << 20)
        if not block:
            break
        digest.update(block)
    return digest.hexdigest()


def _canonical_member(handle: Any) -> bytes:
    try:
        with tarfile.open(fileobj=handle, mode="r:gz") as archive:
            matches = [member for member in archive.getmembers() if member.name == ROOTFS["member"]]
            if len(matches) != 1:
                raise BoundaryError("canonical AppDMClient member is absent or duplicated")
            member = matches[0]
            if not member.isfile() or member.issym() or member.islnk() or member.size != ARTIFACT["size"]:
                raise BoundaryError("canonical AppDMClient member type or size drift")
            stream = archive.extractfile(member)
            if stream is None:
                raise BoundaryError("cannot stream canonical AppDMClient member")
            value = stream.read(ARTIFACT["size"] + 1)
    except (OSError, tarfile.TarError) as exc:
        raise BoundaryError("cannot parse canonical rootfs archive") from exc
    if len(value) != ARTIFACT["size"] or hashlib.sha256(value).hexdigest() != ARTIFACT["sha256"]:
        raise BoundaryError("canonical AppDMClient member identity drift")
    return value


def _canonical_rootfs_snapshot(rootfs: Path) -> tuple[os.stat_result, str, bytes]:
    path_before = _reject_alias(rootfs, "canonical rootfs")
    if path_before.st_size > MAX_ROOTFS_SIZE:
        raise BoundaryError("canonical rootfs exceeds size bound")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(rootfs, flags)
    except OSError as exc:
        raise BoundaryError(f"cannot open canonical rootfs: {exc.strerror}") from exc
    try:
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                    or not _same_stat(path_before, opened)):
                raise BoundaryError("canonical rootfs changed before stable open")
            rootfs_hash = _hash_open_file(handle)
            handle.seek(0)
            canonical_raw = _canonical_member(handle)
            descriptor_after = os.fstat(handle.fileno())
    except OSError as exc:
        raise BoundaryError(f"cannot read canonical rootfs: {exc.strerror}") from exc
    try:
        path_after = rootfs.lstat()
    except OSError as exc:
        raise BoundaryError(f"cannot revalidate canonical rootfs: {exc.strerror}") from exc
    if (not _same_stat(opened, descriptor_after)
            or not _same_stat(path_before, path_after)
            or not stat.S_ISREG(path_after.st_mode)
            or path_after.st_nlink != 1):
        raise BoundaryError("canonical rootfs changed during hash/member streaming")
    return opened, rootfs_hash, canonical_raw


def analyze(rootfs: Path, appdmclient: Path, manifest_path: Path, objdump: Path, readelf: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    rootfs_stat, rootfs_hash, canonical_raw = _canonical_rootfs_snapshot(rootfs)
    if rootfs_stat.st_size != ROOTFS["size"] or rootfs_hash != ROOTFS["sha256"]:
        raise BoundaryError("canonical rootfs identity does not match the supported audit")
    before = _reject_alias(appdmclient, "AppDMClient")
    raw = _read_regular(appdmclient, MAX_ELF_SIZE, "AppDMClient")
    if len(raw) != ARTIFACT["size"] or hashlib.sha256(raw).hexdigest() != ARTIFACT["sha256"]:
        raise BoundaryError("AppDMClient identity does not match the supported audit")
    if raw != canonical_raw:
        raise BoundaryError("supplied AppDMClient does not equal the canonical rootfs member")

    _validate_tool(objdump, LLVM["version"], LLVM["objdump_size"], LLVM["objdump_sha256"], "llvm-objdump")
    _validate_tool(readelf, LLVM["version"], LLVM["readelf_size"], LLVM["readelf_sha256"], "llvm-readelf")

    notes = _run_tool([str(readelf), "--notes", str(appdmclient)], "readelf notes")
    if parse_build_id(notes) != ARTIFACT["build_id"]:
        raise BoundaryError("AppDMClient Build ID drift")
    disassembly = _run_tool(
        [str(objdump), "--disassemble", "--no-show-raw-insn", str(appdmclient)],
        "objdump disassembly", 128 << 20,
    )
    instructions = parse_disassembly(disassembly)
    instruction_hash = _canonical_hash(item.canonical for item in instructions)
    if len(instructions) != LLVM["instruction_count"] or instruction_hash != LLVM["instruction_sha256"]:
        raise BoundaryError("complete instruction inventory drift")
    unwind = _run_tool([str(readelf), "--unwind", str(appdmclient)], "readelf unwind", 64 << 20)
    fdes = parse_fdes(unwind)
    fde_hash = _canonical_hash(f"{start:x}-{end:x}" for start, end in fdes)
    if len(fdes) != LLVM["fde_count"] or fde_hash != LLVM["fde_sha256"]:
        raise BoundaryError("complete FDE inventory drift")
    fde_set = set(fdes)
    if any(bounds not in fde_set for bounds in FDE_ROLES.values()):
        raise BoundaryError("required FDE range is absent")

    by_va = {item.address: item for item in instructions}
    for va, digest in manifest["expected"]["anchors"].items():
        item = by_va.get(va)
        if item is None or hashlib.sha256(item.canonical.encode("utf-8")).hexdigest() != digest:
            raise BoundaryError(f"machine-anchor identity drift at 0x{va:x}")
    for target, expected in DIRECT_TRANSFERS.items():
        if _transfers(instructions, target) != expected:
            raise BoundaryError(f"direct-transfer inventory drift for target 0x{target:x}")

    literal_hashes: dict[str, str] = {}
    for role, row in manifest["expected"]["literals"].items():
        value = _literal_bytes(raw, row)
        digest = hashlib.sha256(value).hexdigest()
        if digest != row["sha256"]:
            raise BoundaryError(f"literal identity drift for {role}")
        literal_hashes[role] = digest

    after = os.stat(appdmclient, follow_symlinks=False)
    if not _same_stat(before, after):
        raise BoundaryError("AppDMClient changed during analysis")

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "rootfs": {
            "role": "canonical-EU-260128-rootfs",
            "size": ROOTFS["size"],
            "sha256": ROOTFS["sha256"],
            "selected_member": "app/bin/AppDMClient",
        },
        "artifact": {
            "role": "canonical-rootfs-AppDMClient",
            "size": ARTIFACT["size"],
            "sha256": ARTIFACT["sha256"],
            "build_id": ARTIFACT["build_id"],
        },
        "static_contract": {
            "launch_proxy": {
                "fde": ["0x8c0c0", "0x8c2ab"],
                "abi": "x86-64-sysv-hidden-return-plus-interface-plus-logical-arguments",
                "logical_argument_types": ["int", "QString", "QString"],
                "variant_type_tags": [2, 10, 10],
                "variant_order_matches_logical_order": True,
                "method_role": "launcher-request-method",
                "method_literal_sha256": literal_hashes["launch-method"],
                "async_call_site": "0x8c199",
                "return_handling": "construct-hidden-pending-reply-result-assign-pending-call-return-result-address",
            },
            "direct_callers": [
                {"call_site": "0x71a0a", "owner_fde": ["0x712c0", "0x71c53"],
                 "app_id": 300, "first_qstring_role": "fixed-AppUpgrade-name",
                 "second_qstring_role": "staged-AppUpgrade-path",
                 "static_predicates": ["object-byte-0xe2-nonzero", "staged-path-validator-true"]},
                {"call_site": "0x818f6", "owner_fde": ["0x7ff60", "0x830e4"],
                 "app_id": 300, "first_qstring_role": "fixed-AppUpgrade-name",
                 "second_qstring_role": "staged-AppUpgrade-path",
                 "static_predicates": ["common-staging-gates", "source-root-marker-absent", "staged-path-validator-true"]},
                {"call_site": "0x8201d", "owner_fde": ["0x7ff60", "0x830e4"],
                 "app_id": 300, "first_qstring_role": "fixed-AppUpgrade-name",
                 "second_qstring_role": "source-root-derived-AppUpgrade-path",
                 "static_predicates": ["common-staging-gates", "source-root-marker-present"]},
                {"call_site": "0x8817e", "owner_fde": ["0x87400", "0x886e7"],
                 "app_id": 300, "first_qstring_role": "fixed-AppUpgrade-name",
                 "second_qstring_role": "staged-AppUpgrade-path",
                 "static_predicates": ["ext-units-path-present", "route-helper-false", "object-bytes-0x161-and-0x160-zero", "staged-path-validator-true"]},
            ],
            "staging_path_bindings": {
                "source_root_argument": "logical-first-QString-in-rsi-copied-to-r13",
                "source_executable_local": "stack-slot-0x0-built-as-source-root-plus-AppUpgrade",
                "staged_executable_local": "stack-slot-0x8-built-as-fixed-staged-base-plus-AppUpgrade",
                "stack_slot_0x8_is_source_root": False,
                "normal_and_exception_cleanup_cover_both_locals": True,
            },
            "staging_terminal_selection": {
                "common_source_executable_existence_gate": True,
                "staged_executable_existence_is_common_gate": False,
                "staged_existence_true_adds_permission_handling": True,
                "route_marker_role": "source-root-HU-images-start-marker",
                "marker_present": {
                    "request_call_site": "0x8201d",
                    "executable_role": "source-root-derived-AppUpgrade-path",
                    "final_local_elf_and_executable_helper_gate": False,
                },
                "marker_absent": {
                    "validator_fde": ["0x70b50", "0x712b9"],
                    "validator_requires": ["path-exists", "read-open", "four-byte-ELF-magic", "executable-bit-test"],
                    "validator_true_request_call_site": "0x818f6",
                    "validator_true_executable_role": "staged-AppUpgrade-path",
                    "validator_false_request": None,
                },
            },
            "literal_bindings": [
                {"role": role, "sha256": literal_hashes[role]}
                for role in sorted(literal_hashes)
            ],
        },
        "runtime_observations": {
            "session_bus_reachable": None,
            "launcher_service_owned": None,
            "request_object_registered": None,
            "message_accepted_or_delivered": None,
            "app_process_created_or_reused": None,
            "app_launcher_argv_selected": None,
            "qprocess_start_accepted": None,
            "child_exec_succeeded": None,
            "effective_child_credentials_or_label": None,
            "update_accepted": None,
            "partition_written": None,
            "boot_accepted": None,
            "persistence": None,
        },
        "classification": {
            "static_launch_message_construction": True,
            "static_terminal_path_selection": True,
            "runtime_delivery_or_execution_established": False,
            "root_or_persistence_established": False,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rootfs", required=True, type=Path)
    parser.add_argument("--appdmclient", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--llvm-objdump", required=True, type=Path)
    parser.add_argument("--llvm-readelf", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = analyze(args.rootfs, args.appdmclient, args.manifest, args.llvm_objdump, args.llvm_readelf)
        encoded = (json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        if args.output is None:
            sys.stdout.buffer.write(encoded)
        else:
            if args.output.exists() or args.output.is_symlink():
                raise BoundaryError("output already exists")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("xb") as handle:
                handle.write(encoded)
    except BoundaryError as exc:
        sys.stderr.buffer.write((f"error: {exc}\n").encode("utf-8"))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
