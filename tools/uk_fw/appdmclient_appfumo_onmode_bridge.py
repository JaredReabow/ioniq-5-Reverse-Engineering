#!/usr/bin/env python3
"""Audit the exact-static AppDMClient -> AppFUMO priority-mode bridge.

The analyzer is execution-free with respect to recovered targets.  It streams the
canonical rootfs, structurally selects the embedded updater ELF, invokes only
identity-bound host LLVM readers, and emits normalized roles/hashes rather than
D-Bus values, target bytes, supplied paths, commands, or actuation material.
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
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable

from appfumo_boot_activation_boundary import (  # type: ignore
    BoundaryError,
    ElfView,
    _HashingReader,
    _branch_target,
    _canonical_hash,
    _canonical_member_name,
    _inventory_line,
    _read_regular,
    _run_tool,
    _same_stat,
    _stat_regular,
    _validate_tool,
    parse_build_id,
    parse_disassembly,
    parse_fdes,
)
from embedded_elf import EmbeddedElfError, parse_elf_at  # type: ignore

SCHEMA_VERSION = 1
TOOL_NAME = "appdmclient-appfumo-priority-mode-bridge"
TOOL_VERSION = "1.0.0"
MAX_MANIFEST_SIZE = 2 << 20
MAX_ELF_SIZE = 64 << 20
MAX_ROOTFS_SIZE = 1 << 30
MAX_TOOL_SIZE = 16 << 20
MAX_SELECTED_MEMBER = 64 << 20

ARTIFACTS = {
    "rootfs": {
        "size": 879109759,
        "sha256": "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84",
    },
    "appdmclient": {
        "size": 2226072,
        "sha256": "9a1fb796d7ac24fcce71c16e3dbee9306c888f43e705ee081f41b7d473978bd0",
        "build_id": "b2dbcc5231f444d8f1dd68eb7a2376323ce805df",
    },
    "outer_appupgrade": {
        "size": 10787256,
        "sha256": "5295c6e4c41fb9c03760cf006c58b66fcd11aeb4e6e889af6e31b062549b6df0",
    },
    "appfumo": {
        "size": 5066264,
        "sha256": "464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7",
        "build_id": "863a8730e66a1c5245a1bf458fe2554adee0351a",
    },
    "session_config": {
        "size": 3382,
        "sha256": "c5999ae1f226935ce2b10b19d060874194b7cc87cdc318dd63ce265acbba0119",
        "mode": 0o644,
    },
}
MEMBERS = {
    "appdmclient": "./app/bin/AppDMClient",
    "outer_appupgrade": "./app/bin/AppUpgrade",
    "session_config": "./etc/dbus-1/session.conf",
}
SESSION_D = "etc/dbus-1/session.d"
SESSION_LOCAL = "etc/dbus-1/session-local.conf"
ROOTFS_MEMBER_COUNT = 66836
ROOTFS_INVENTORY_SHA256 = "c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c"
EMBEDDED_OFFSET = 0x5721C8

FDE_ROLES = {
    ("appdmclient", "signal-sender"): (0x4F1C0, 0x4F58A),
    ("appdmclient", "source-checker"): (0x67E30, 0x69144),
    ("appdmclient", "source-staging"): (0x7FF60, 0x830E4),
    ("appdmclient", "mounted-source-callback"): (0x84700, 0x84E2D),
    ("appdmclient", "state-notification-sender"): (0x85340, 0x85A90),
    ("appdmclient", "generated-row-dispatch"): (0x108BD0, 0x10A075),
    ("appfumo", "session-subscription-setup"): (0xE2C30, 0xE3296),
    ("appfumo", "generated-row-dispatch"): (0x16DF80, 0x16EFE4),
    ("appfumo", "priority-mode-consumer"): (0x10F4A0, 0x10FA30),
    ("appfumo", "readiness-predicate"): (0xFED10, 0xFF280),
    ("appfumo", "news-copy"): (0x101110, 0x104C1B),
}
DIRECT_TRANSFERS = {
    ("appdmclient", 0x4F1C0): ((0x685E7, 0x8573F, 0x8595F, 0x109766), ()),
    ("appdmclient", 0x67E30): ((0x8079D,), ()),
    ("appdmclient", 0x7FF60): (
        (0x8323B, 0x8400F, 0x849A7, 0x84C9C, 0x84D8E, 0x850DE,
         0x8680C, 0x868C3, 0x86F8C, 0x87395, 0x87858, 0x882F3),
        (),
    ),
    ("appfumo", 0x10F4A0): ((0x16E6DA,), ()),
    ("appfumo", 0xFED10): ((0x10F8A2, 0x114A5E, 0x1244CF, 0x16E587), ()),
    ("appfumo", 0x101110): ((0x10F995, 0x1244FD, 0x16E59F), (0x104C4C,)),
}
LITERAL_ROLES = {
    ("appdmclient", "emitter-path"): (0x176060, 44),
    ("appdmclient", "emitter-interface"): (0x172A70, 43),
    ("appdmclient", "emitter-member"): (0x173BFE, 14),
    ("appfumo", "receiver-interface"): (0x214950, 43),
    ("appfumo", "receiver-member"): (0x21E6E3, 14),
    ("appfumo", "receiver-slot"): (0x227570, 42),
    ("appfumo", "unrelated-member"): (0x21EDE8, 12),
    ("appfumo", "unrelated-interface"): (0x21E6A4, 27),
    ("appfumo", "unrelated-path"): (0x21E6C0, 12),
    ("appfumo", "unrelated-service"): (0x2189D8, 30),
    ("appfumo", "news-archive-basename"): (0x20BB63, 16),
    ("appfumo", "two-part-path-template"): (0x209CD4, 5),
}

APPDM_ANCHORS = {
    0x4F2F0, 0x4F2F5, 0x4F301, 0x4F306, 0x4F317, 0x4F321, 0x4F348,
    0x4F3BD, 0x4F3CF, 0x4F3DA, 0x4F3E5, 0x4F40A, 0x4F415,
    0x685D9, 0x685DC, 0x685DF, 0x685E7,
    0x80797, 0x8079A, 0x8079D,
    0x84874, 0x848D8, 0x848DD, 0x848E0, 0x848EE,
    0x84983, 0x84988, 0x8499F, 0x849A4, 0x849A7,
    0x85712, 0x85717, 0x8571E, 0x85723, 0x8572F, 0x85732, 0x85735, 0x8573F,
    0x85932, 0x85937, 0x8593E, 0x85943, 0x8594F, 0x85952, 0x85955, 0x8595F,
    0x109717, 0x109733, 0x10974F, 0x10975E, 0x109761, 0x109764, 0x109766,
}
APPFUMO_ANCHORS = {
    0xE2C5A,
    0xE2F4A, 0xE2F56, 0xE2F62, 0xE2F67, 0xE2F77, 0xE2F80, 0xE2F8C,
    0xE2F95, 0xE2FB5, 0xE2FB8, 0xE2FC5,
    0xE3030, 0xE3037, 0xE3048, 0xE304C, 0xE305F, 0xE3062, 0xE3065,
    0xE3068, 0xE3070, 0xE3073, 0xE307C, 0xE3083, 0xE308B,
    0x16E66C, 0x16E69D, 0x16E6CE, 0x16E6D2, 0x16E6D5, 0x16E6D8, 0x16E6DA,
    0x10F4A6, 0x10F4AB, 0x10F4B0, 0x10F4B6,
    0x10F61B, 0x10F621, 0x10F628, 0x10F62D, 0x10F634, 0x10F637,
    0x10F678, 0x10F67F, 0x10F8A2, 0x10F8A7, 0x10F8A9, 0x10F970, 0x10F992, 0x10F995,
    0xFED39, 0xFED3D, 0xFEE04, 0xFEE23, 0xFF0D8, 0xFF0DD, 0xFF0E4, 0xFF0EB,
    0x101134, 0x10114F, 0x10155B, 0x101563, 0x10157A, 0x101589,
    0x1015A4, 0x1015CD, 0x102C90, 0x102C98, 0x102CA4,
}
ANCHOR_ADDRESSES = {"appdmclient": APPDM_ANCHORS, "appfumo": APPFUMO_ANCHORS}

EXPECTED_LLVM = {
    "version": "Homebrew LLVM version 23.1.3",
    "objdump_size": 813808,
    "objdump_sha256": "7b04d723638c0793efbd31b99b2389f36ceb8c803bdc1008e43ea7525958376f",
    "readelf_size": 1805104,
    "readelf_sha256": "80a1f8ffc44c5a1e4dbeaa5c409cd98a01cb2fa73e1ccc2eeb22a3b7ee2e1cb0",
    "binaries": {
        "appdmclient": {
            "instruction_count": 321113,
            "instruction_sha256": "77c0187fc865feaf9ce6bac45ef22d6e3eef29981637190fdf1d225c6928a39d",
            "fde_count": 2418,
            "fde_sha256": "48598865977ec790c555d4441e15c0ec7501d4999d5f66070d70b686f94c4301",
        },
        "appfumo": {
            "instruction_count": 470739,
            "instruction_sha256": "693dce0d89faabeea30512fe0a696a733e9bdd64fd7be7379dba98a44d2dc0c8",
            "fde_count": 3789,
            "fde_sha256": "2c71813a3f098f8f949c6acee1080c0147df182e589f8b8b576798ce4807eb07",
        },
    },
}

DOCTYPE_RE = re.compile(
    rb'<!DOCTYPE\s+busconfig\s+PUBLIC\s+"-//freedesktop//DTD D-Bus Bus Configuration 1\.0//EN"\s+'
    rb'"http://www\.freedesktop\.org/standards/dbus/1\.0/busconfig\.dtd"\s*>',
    re.DOTALL,
)


def _reject_artifact_alias(path: Path, what: str) -> None:
    try:
        row = path.lstat()
    except OSError as exc:
        raise BoundaryError(f"cannot lstat {what}: {exc.strerror}") from exc
    if not stat.S_ISREG(row.st_mode) or row.st_nlink != 1:
        raise BoundaryError(f"{what} is linked, aliased, or non-regular")


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BoundaryError(f"manifest contains duplicate JSON key: {key}")
        result[key] = value
    return result


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


def _boolean(value: Any, what: str) -> bool:
    if type(value) is not bool:
        raise BoundaryError(f"{what} must be Boolean")
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


def _load_artifact(value: Any, role: str) -> dict[str, Any]:
    keys = {"size", "sha256"}
    if role in ("appdmclient", "appfumo"):
        keys.add("build_id")
    if role == "session_config":
        keys.add("mode")
    row = _object(value, keys, f"artifact {role}")
    out = {
        "size": _integer(row["size"], f"{role}.size", MAX_ROOTFS_SIZE),
        "sha256": _digest(row["sha256"], f"{role}.sha256"),
    }
    if "build_id" in row:
        out["build_id"] = _hex_id(row["build_id"], f"{role}.build_id")
    if "mode" in row:
        out["mode"] = _integer(row["mode"], f"{role}.mode", 0o7777)
    if out != ARTIFACTS[role]:
        raise BoundaryError(f"artifact {role} does not match the supported audit")
    return out


def load_manifest(path: Path) -> dict[str, Any]:
    _reject_artifact_alias(path, "manifest")
    raw = _read_regular(path, MAX_MANIFEST_SIZE, "manifest")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BoundaryError("manifest is not valid strict UTF-8 JSON") from exc
    top = _object(value, {"schema_version", "artifacts", "llvm", "expected"}, "manifest")
    if _integer(top["schema_version"], "schema_version") != SCHEMA_VERSION:
        raise BoundaryError("unsupported manifest schema version")

    artifacts_value = _object(top["artifacts"], ARTIFACTS.keys(), "artifacts")
    artifacts = {role: _load_artifact(artifacts_value[role], role) for role in ARTIFACTS}

    llvm_value = _object(top["llvm"], {
        "version", "objdump_size", "objdump_sha256", "readelf_size", "readelf_sha256", "binaries"
    }, "llvm")
    binaries_value = _object(llvm_value["binaries"], {"appdmclient", "appfumo"}, "llvm.binaries")
    binaries: dict[str, Any] = {}
    for role in ("appdmclient", "appfumo"):
        row = _object(binaries_value[role], {
            "instruction_count", "instruction_sha256", "fde_count", "fde_sha256"
        }, f"llvm binary {role}")
        binaries[role] = {
            "instruction_count": _integer(row["instruction_count"], "instruction_count", 2_000_000),
            "instruction_sha256": _digest(row["instruction_sha256"], "instruction_sha256"),
            "fde_count": _integer(row["fde_count"], "fde_count", 100_000),
            "fde_sha256": _digest(row["fde_sha256"], "fde_sha256"),
        }
    llvm = {
        "version": _string(llvm_value["version"], "llvm.version", 128),
        "objdump_size": _integer(llvm_value["objdump_size"], "objdump_size", MAX_TOOL_SIZE),
        "objdump_sha256": _digest(llvm_value["objdump_sha256"], "objdump_sha256"),
        "readelf_size": _integer(llvm_value["readelf_size"], "readelf_size", MAX_TOOL_SIZE),
        "readelf_sha256": _digest(llvm_value["readelf_sha256"], "readelf_sha256"),
        "binaries": binaries,
    }
    if llvm != EXPECTED_LLVM:
        raise BoundaryError("LLVM identity or complete inventory expectation drift")

    expected_value = _object(top["expected"], {
        "rootfs", "embedded", "fdes", "direct_transfers", "anchors", "literals"
    }, "expected")
    rootfs_value = _object(expected_value["rootfs"], {
        "member_count", "inventory_sha256", "session_d_child_count", "session_local_present"
    }, "expected.rootfs")
    rootfs = {
        "member_count": _integer(rootfs_value["member_count"], "member_count", 1_000_000),
        "inventory_sha256": _digest(rootfs_value["inventory_sha256"], "inventory_sha256"),
        "session_d_child_count": _integer(rootfs_value["session_d_child_count"], "session_d_child_count", 1000),
        "session_local_present": _boolean(rootfs_value["session_local_present"], "session_local_present"),
    }
    if rootfs != {
        "member_count": ROOTFS_MEMBER_COUNT,
        "inventory_sha256": ROOTFS_INVENTORY_SHA256,
        "session_d_child_count": 0,
        "session_local_present": False,
    }:
        raise BoundaryError("canonical rootfs expectation drift")

    embedded_value = _object(expected_value["embedded"], {
        "outer_offset", "structural_extent", "build_id"
    }, "expected.embedded")
    embedded = {
        "outer_offset": _integer(embedded_value["outer_offset"], "outer_offset"),
        "structural_extent": _integer(embedded_value["structural_extent"], "structural_extent", MAX_ELF_SIZE),
        "build_id": _hex_id(embedded_value["build_id"], "embedded.build_id"),
    }
    if embedded != {
        "outer_offset": EMBEDDED_OFFSET,
        "structural_extent": ARTIFACTS["appfumo"]["size"],
        "build_id": ARTIFACTS["appfumo"]["build_id"],
    }:
        raise BoundaryError("embedded structural expectation drift")

    fdes = []
    for index, item in enumerate(_array(expected_value["fdes"], "fdes", 64)):
        row = _object(item, {"binary", "role", "start", "end_exclusive"}, f"fde {index}")
        fdes.append({
            "binary": _string(row["binary"], "fde.binary", 32),
            "role": _string(row["role"], "fde.role", 64),
            "start": _integer(row["start"], "fde.start"),
            "end_exclusive": _integer(row["end_exclusive"], "fde.end"),
        })
    actual_fdes = {
        (row["binary"], row["role"]): (row["start"], row["end_exclusive"]) for row in fdes
    }
    if len(actual_fdes) != len(fdes) or actual_fdes != FDE_ROLES:
        raise BoundaryError("selected FDE expectation drift")

    transfers = []
    for index, item in enumerate(_array(expected_value["direct_transfers"], "direct_transfers", 64)):
        row = _object(item, {"binary", "target", "call_vas", "jump_vas"}, f"transfer {index}")
        transfers.append({
            "binary": _string(row["binary"], "transfer.binary", 32),
            "target": _integer(row["target"], "transfer.target"),
            "call_vas": tuple(_integer(v, "call va") for v in _array(row["call_vas"], "call_vas", 64)),
            "jump_vas": tuple(_integer(v, "jump va") for v in _array(row["jump_vas"], "jump_vas", 64)),
        })
    actual_transfers = {
        (row["binary"], row["target"]): (row["call_vas"], row["jump_vas"]) for row in transfers
    }
    if len(actual_transfers) != len(transfers) or actual_transfers != DIRECT_TRANSFERS:
        raise BoundaryError("direct-transfer expectation drift")

    anchors = []
    for index, item in enumerate(_array(expected_value["anchors"], "anchors", 512)):
        row = _object(item, {"binary", "va", "mnemonic", "operands"}, f"anchor {index}")
        anchors.append({
            "binary": _string(row["binary"], "anchor.binary", 32),
            "va": _integer(row["va"], "anchor.va"),
            "mnemonic": _string(row["mnemonic"], "anchor.mnemonic", 32),
            "operands": _string(row["operands"], "anchor.operands", 512),
        })
    actual_anchor_keys = [(row["binary"], row["va"]) for row in anchors]
    expected_anchor_keys = {(binary, va) for binary, values in ANCHOR_ADDRESSES.items() for va in values}
    if len(set(actual_anchor_keys)) != len(anchors) or set(actual_anchor_keys) != expected_anchor_keys:
        raise BoundaryError("machine-anchor expectation drift")

    literals = []
    for index, item in enumerate(_array(expected_value["literals"], "literals", 64)):
        row = _object(item, {"binary", "role", "va", "length", "sha256"}, f"literal {index}")
        literals.append({
            "binary": _string(row["binary"], "literal.binary", 32),
            "role": _string(row["role"], "literal.role", 64),
            "va": _integer(row["va"], "literal.va"),
            "length": _integer(row["length"], "literal.length", 4096),
            "sha256": _digest(row["sha256"], "literal.sha256"),
        })
    actual_literal_roles = {
        (row["binary"], row["role"]): (row["va"], row["length"]) for row in literals
    }
    if len(actual_literal_roles) != len(literals) or actual_literal_roles != LITERAL_ROLES:
        raise BoundaryError("literal role/address expectation drift")

    return {
        "artifacts": artifacts,
        "llvm": llvm,
        "expected": {
            "rootfs": rootfs, "embedded": embedded, "fdes": fdes,
            "direct_transfers": transfers, "anchors": anchors, "literals": literals,
        },
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
    }


def classify_receiver_filters(*, service_empty: bool, path_empty: bool,
                              interface_fixed: bool, member_fixed: bool) -> str:
    values = (service_empty, path_empty, interface_fixed, member_fixed)
    if any(type(value) is not bool for value in values):
        raise BoundaryError("receiver filter facts must be Boolean")
    if values == (True, True, True, True):
        return "wildcard-service-and-path-fixed-interface-and-member"
    if not service_empty and not path_empty and interface_fixed and member_fixed:
        return "fixed-service-path-interface-and-member"
    raise BoundaryError("unsupported or contradictory receiver filter class")


def validate_runtime_facts(value: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "same_bus_participation", "socket_reachability", "sender_identity",
        "signal_delivery", "slot_execution", "readiness_success", "copy_success",
    }
    row = _object(value, expected, "runtime facts")
    if any(item is not None for item in row.values()):
        raise BoundaryError("runtime facts cannot be promoted by this static analyzer")
    return row


def _parse_session_xml(raw: bytes) -> ET.Element:
    matches = list(DOCTYPE_RE.finditer(raw))
    if len(matches) != 1:
        raise BoundaryError("session config DOCTYPE is absent or ambiguous")
    cleaned = raw[:matches[0].start()] + raw[matches[0].end():]
    if b"<!DOCTYPE" in cleaned or b"<!ENTITY" in cleaned:
        raise BoundaryError("session config contains an unsupported declaration")
    try:
        root = ET.fromstring(cleaned)
    except ET.ParseError as exc:
        raise BoundaryError("session config XML is malformed") from exc
    if root.tag != "busconfig" or root.attrib or (root.text or "").strip():
        raise BoundaryError("session config root is unsupported")
    return root


def parse_session_config(raw: bytes) -> dict[str, Any]:
    """Strictly summarize the selected canonical per-session bus configuration."""
    root = _parse_session_xml(raw)
    type_values: list[str] = []
    listen_values: list[str] = []
    auth_values: list[str] = []
    includes: list[tuple[str, str, tuple[tuple[str, str], ...]]] = []
    default_policies: list[list[tuple[str, tuple[tuple[str, str], ...]]]] = []
    singleton_empty = {"keep_umask", "standard_session_servicedirs"}
    limits: set[str] = set()
    for child in root:
        if (child.tail or "").strip():
            raise BoundaryError("session config contains unexpected tail text")
        if child.tag in ("type", "listen", "auth"):
            if child.attrib or list(child):
                raise BoundaryError("session config singleton is malformed")
            text = (child.text or "").strip()
            if not text:
                raise BoundaryError("session config singleton is empty")
            {"type": type_values, "listen": listen_values, "auth": auth_values}[child.tag].append(text)
        elif child.tag in singleton_empty:
            if child.attrib or list(child) or (child.text or "").strip():
                raise BoundaryError("session config empty singleton is malformed")
        elif child.tag in ("include", "includedir"):
            if list(child):
                raise BoundaryError("session config include has children")
            text = (child.text or "").strip()
            if not text:
                raise BoundaryError("session config include is empty")
            includes.append((child.tag, text, tuple(sorted(child.attrib.items()))))
        elif child.tag == "policy":
            if child.attrib != {"context": "default"} or (child.text or "").strip():
                raise BoundaryError("session config policy scope drift")
            rules: list[tuple[str, tuple[tuple[str, str], ...]]] = []
            for rule in child:
                if rule.tag not in ("allow", "deny") or list(rule) or (rule.text or "").strip() or (rule.tail or "").strip():
                    raise BoundaryError("session config policy rule is malformed")
                rules.append((rule.tag, tuple(sorted(rule.attrib.items()))))
            default_policies.append(rules)
        elif child.tag == "limit":
            if set(child.attrib) != {"name"} or list(child) or not (child.text or "").strip().isdigit():
                raise BoundaryError("session config limit is malformed")
            name = child.attrib["name"]
            if not name or name in limits:
                raise BoundaryError("session config limit name is empty or duplicate")
            limits.add(name)
        else:
            raise BoundaryError("session config contains an unsupported element")
    if type_values != ["session"] or listen_values != ["unix:tmpdir=/tmp"] or auth_values != ["EXTERNAL"]:
        raise BoundaryError("session bus type, listener, or authentication drift")
    expected_rules = [[
        ("allow", (("eavesdrop", "true"), ("send_destination", "*"))),
        ("allow", (("eavesdrop", "true"),)),
        ("allow", (("own", "*"),)),
    ]]
    if default_policies != expected_rules:
        raise BoundaryError("session default policy shape drift")
    expected_includes = {
        ("includedir", "session.d", ()),
        ("include", "session-local.conf", (("ignore_missing", "yes"),)),
        ("include", "contexts/dbus_contexts", (("if_selinux_enabled", "yes"), ("selinux_root_relative", "yes"))),
    }
    if set(includes) != expected_includes or len(includes) != len(expected_includes):
        raise BoundaryError("session include set drift")
    if len(limits) != 15:
        raise BoundaryError("session limit inventory drift")
    return {
        "bus_type": "session",
        "listener_class": "unix-temporary-directory",
        "authentication": "EXTERNAL",
        "default_send_permission": "allow",
        "default_receive_permission": "allow",
        "default_own_permission": "allow",
        "included_policy_directory": True,
        "optional_local_include": True,
        "policy_permission_is_socket_reachability": False,
    }


def _stream_member(archive: tarfile.TarFile, member: tarfile.TarInfo,
                   maximum: int, what: str) -> tuple[str, bytes]:
    if member.size > maximum:
        raise BoundaryError(f"{what} exceeds the size bound")
    stream = archive.extractfile(member)
    if stream is None:
        raise BoundaryError(f"{what} cannot be streamed")
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = stream.read(1 << 16)
        if not chunk:
            break
        total += len(chunk)
        if total > member.size:
            raise BoundaryError(f"{what} exceeds its declared size")
        digest.update(chunk)
        chunks.append(chunk)
    if total != member.size:
        raise BoundaryError(f"{what} is truncated")
    return digest.hexdigest(), b"".join(chunks)


def audit_rootfs(path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    expected = manifest["expected"]["rootfs"]
    _reject_artifact_alias(path, "rootfs archive")
    before = _stat_regular(path, MAX_ROOTFS_SIZE, "rootfs archive")
    selected_by_canonical = {_canonical_member_name(name): role for role, name in MEMBERS.items()}
    selected: dict[str, bytes] = {}
    seen: set[str] = set()
    inventory = hashlib.sha256()
    count = 0
    session_d_seen = False
    session_d_children = 0
    session_local_present = False
    try:
        with path.open("rb") as raw_handle:
            reader = _HashingReader(raw_handle)
            with tarfile.open(fileobj=reader, mode="r|gz") as archive:
                for index, member in enumerate(archive):
                    count += 1
                    inventory.update(_inventory_line(index, member))
                    canonical = _canonical_member_name(member.name)
                    if canonical in seen:
                        raise BoundaryError("rootfs contains a duplicate or aliased member")
                    seen.add(canonical)
                    if canonical == SESSION_LOCAL:
                        session_local_present = True
                    if canonical == SESSION_D:
                        if member.name != "./" + SESSION_D or not member.isdir() or member.linkname:
                            raise BoundaryError("session policy directory metadata drift")
                        session_d_seen = True
                    elif canonical.startswith(SESSION_D + "/"):
                        session_d_children += 1
                        if member.islnk() or member.issym() or not member.isreg():
                            raise BoundaryError("session policy directory contains an alias or special node")
                    role = selected_by_canonical.get(canonical)
                    if role is None:
                        continue
                    expected_name = MEMBERS[role]
                    artifact = ARTIFACTS[role]
                    expected_mode = artifact.get("mode", 0o755)
                    if role in selected or member.name != expected_name:
                        raise BoundaryError("selected rootfs member is duplicated or aliased")
                    if (not member.isreg() or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                            or member.linkname or member.mode != expected_mode or member.size != artifact["size"]):
                        raise BoundaryError("selected rootfs member metadata drift")
                    digest, content = _stream_member(archive, member, MAX_SELECTED_MEMBER, role)
                    if digest != artifact["sha256"]:
                        raise BoundaryError("selected rootfs member identity drift")
                    selected[role] = content
            while reader.read(1 << 20):
                pass
            archive_sha = reader.digest.hexdigest()
            descriptor_after = os.fstat(raw_handle.fileno())
    except (tarfile.TarError, OSError, UnicodeEncodeError) as exc:
        raise BoundaryError(f"cannot stream canonical rootfs: {type(exc).__name__}") from exc
    after = _stat_regular(path, MAX_ROOTFS_SIZE, "rootfs archive")
    if not _same_stat(before, after) or not _same_stat(before, descriptor_after):
        raise BoundaryError("rootfs archive changed during analysis")
    if before.st_size != ARTIFACTS["rootfs"]["size"] or archive_sha != ARTIFACTS["rootfs"]["sha256"]:
        raise BoundaryError("rootfs archive identity drift")
    if count != expected["member_count"] or inventory.hexdigest() != expected["inventory_sha256"]:
        raise BoundaryError("complete rootfs inventory drift")
    if set(selected) != set(MEMBERS) or not session_d_seen:
        raise BoundaryError("canonical selected rootfs members are incomplete")
    if session_d_children != expected["session_d_child_count"]:
        raise BoundaryError("session policy directory state drift")
    if session_local_present != expected["session_local_present"]:
        raise BoundaryError("session local-include state drift")
    return {
        "sha256": archive_sha,
        "size": before.st_size,
        "member_count": count,
        "inventory_sha256": inventory.hexdigest(),
        "session_d_child_count": session_d_children,
        "session_local_present": session_local_present,
        "selected": selected,
    }


def _transfers(instructions: list[Any], target: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    calls = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("call") and _branch_target(item) == target)
    jumps = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("j") and _branch_target(item) == target)
    return calls, jumps


def _require_anchor(by_va: dict[int, Any], va: int, mnemonic: str, operands: str) -> None:
    item = by_va.get(va)
    if item is None or item.mnemonic != mnemonic or item.operands != operands:
        raise BoundaryError(f"semantic machine anchor drift at 0x{va:x}")


def _validate_anchor_rows(binary: str, instructions: list[Any], anchors: list[dict[str, Any]]) -> None:
    by_va = {item.address: item for item in instructions}
    for row in anchors:
        if row["binary"] != binary:
            continue
        item = by_va.get(row["va"])
        if item is None or item.mnemonic != row["mnemonic"] or item.operands != row["operands"]:
            raise BoundaryError(f"machine anchor drift at 0x{row['va']:x}")


def _validate_semantics(binary: str, instructions: list[Any], anchors: list[dict[str, Any]]) -> None:
    by_va = {item.address: item for item in instructions}
    _validate_anchor_rows(binary, instructions, anchors)
    for (role, target), expected in DIRECT_TRANSFERS.items():
        if role == binary and _transfers(instructions, target) != expected:
            raise BoundaryError(f"direct-transfer inventory drift at 0x{target:x}")

    if binary == "appdmclient":
        required = {
            0x4F348: ("callq", "0x1c710 <_ZN12QDBusMessage12createSignalERK7QStringS2_S2_@plt>"),
            0x4F3CF: ("callq", "0x1b650 <_ZN12QDBusMessagelsERK8QVariant@plt>"),
            0x4F3DA: ("callq", "0x1b650 <_ZN12QDBusMessagelsERK8QVariant@plt>"),
            0x4F3E5: ("callq", "0x1b650 <_ZN12QDBusMessagelsERK8QVariant@plt>"),
            0x4F40A: ("callq", "0x1afb0 <_ZN15QDBusConnection10sessionBusEv@plt>"),
            0x4F415: ("callq", "0x1bf70 <_ZNK15QDBusConnection4sendERK12QDBusMessage@plt>"),
            0x685D9: ("movq", "%rbx, %rcx"),
            0x685DC: ("movq", "%rbp, %rdx"),
            0x685DF: ("movl", "$0x1, %esi"),
            0x685E7: ("callq", "0x4f1c0 <.text+0x32010>"),
            0x80797: ("movq", "%rbx, %rsi"),
            0x8079D: ("callq", "0x67e30 <.text+0x4ac80>"),
            0x84874: ("cmpl", "$0x1, %r12d"),
            0x848DD: ("movq", "%r14, %rsi"),
            0x848E0: ("leaq", "0x128(%rax), %rdi"),
            0x848EE: ("callq", "0x1ca30 <_ZN7QStringaSERKS_@plt>"),
            0x849A7: ("callq", "0x7ff60 <.text+0x62db0>"),
            0x85717: ("xorl", "%edi, %edi"),
            0x85723: ("xorl", "%edi, %edi"),
            0x8573F: ("callq", "0x4f1c0 <.text+0x32010>"),
            0x85937: ("xorl", "%edi, %edi"),
            0x85943: ("xorl", "%edi, %edi"),
            0x8595F: ("callq", "0x4f1c0 <.text+0x32010>"),
            0x10975E: ("movq", "%r12, %rcx"),
            0x109761: ("movq", "%r13, %rdx"),
            0x109764: ("movl", "(%rax), %esi"),
            0x109766: ("callq", "0x4f1c0 <.text+0x32010>"),
        }
    else:
        required = {
            0xE2C5A: ("callq", "0x22060 <_ZN15QDBusConnection10sessionBusEv@plt>"),
            0xE2FB5: ("movq", "%r13, %rsi"),
            0xE2FB8: ("movq", "%r14, %rdi"),
            0xE2FC5: ("callq", "0x23240 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>"),
            0xE305F: ("movq", "%r15, %r9"),
            0xE3062: ("movq", "%rbx, %r8"),
            0xE3065: ("movq", "%r12, %rdx"),
            0xE3070: ("movq", "%r13, %rsi"),
            0xE307C: ("leaq", "0x5f161d(%rip), %rax    # 0x6d46a0 <_ZN10QArrayData11shared_nullE>"),
            0xE3083: ("movq", "%rax, -0x60(%rbp)"),
            0xE308B: ("callq", "0x23240 <_ZN15QDBusConnection7connectERK7QStringS2_S2_S2_P7QObjectPKc@plt>"),
            0x16E6D2: ("movq", "%rbp, %rcx"),
            0x16E6D5: ("movq", "%r12, %rdx"),
            0x16E6D8: ("movl", "(%rax), %esi"),
            0x16E6DA: ("callq", "0x10f4a0 <.text+0xeac70>"),
            0x10F4AB: ("movq", "%rdx, %r14"),
            0x10F4B0: ("movq", "%rcx, %r13"),
            0x10F4B6: ("movl", "%esi, %ebx"),
            0x10F61B: ("movl", "%ebx, 0x5c5997(%rip)    # 0x6d4fb8 <_ZN9QListData11shared_nullE+0x758>"),
            0x10F621: ("leaq", "0x5c5988(%rip), %rdi    # 0x6d4fb0 <_ZN9QListData11shared_nullE+0x750>"),
            0x10F62D: ("leaq", "0x5c5974(%rip), %rdi    # 0x6d4fa8 <_ZN9QListData11shared_nullE+0x748>"),
            0x10F8A2: ("callq", "0xfed10 <.text+0xda4e0>"),
            0x10F8A7: ("testb", "%al, %al"),
            0x10F8A9: ("jne", "0x10f970 <.text+0xeb140>"),
            0x10F995: ("callq", "0x101110 <.text+0xdc8e0>"),
            0xFEE23: ("cmpl", "$0x1, %eax"),
            0xFF0DD: ("leaq", "0x5d5ec4(%rip), %rsi    # 0x6d4fa8 <_ZN9QListData11shared_nullE+0x748>"),
            0x101134: ("cmpl", "$0x1, 0x5d3e7d(%rip)    # 0x6d4fb8 <_ZN9QListData11shared_nullE+0x758>"),
            0x10114F: ("je", "0x102c90 <.text+0xde460>"),
            0x101589: ("movq", "0x60(%rsp), %rdx"),
            0x102C98: ("leaq", "0x5d2309(%rip), %rsi    # 0x6d4fa8 <_ZN9QListData11shared_nullE+0x748>"),
        }
    for va, (mnemonic, operands) in required.items():
        _require_anchor(by_va, va, mnemonic, operands)


def _analyze_elf(role: str, path: Path, data: bytes, objdump: Path, readelf: Path,
                 manifest: dict[str, Any]) -> dict[str, Any]:
    artifact = manifest["artifacts"][role]
    if len(data) != artifact["size"] or hashlib.sha256(data).hexdigest() != artifact["sha256"]:
        raise BoundaryError(f"{role} identity drift")
    ElfView(data)
    instructions = parse_disassembly(_run_tool(
        [str(objdump), "-d", "--no-show-raw-insn", str(path)], f"{role} disassembly"
    ))
    expected_inventory = manifest["llvm"]["binaries"][role]
    instruction_sha = _canonical_hash(item.canonical for item in instructions)
    if (len(instructions) != expected_inventory["instruction_count"]
            or instruction_sha != expected_inventory["instruction_sha256"]):
        raise BoundaryError(f"{role} complete instruction inventory drift")
    fdes = parse_fdes(_run_tool([str(readelf), "--unwind", str(path)], f"{role} unwind"))
    fde_sha = _canonical_hash(f"{start:x}-{end:x}" for start, end in fdes)
    if len(fdes) != expected_inventory["fde_count"] or fde_sha != expected_inventory["fde_sha256"]:
        raise BoundaryError(f"{role} complete FDE inventory drift")
    fde_map = dict(fdes)
    for (binary, _fde_role), (start, end) in FDE_ROLES.items():
        if binary == role and fde_map.get(start) != end:
            raise BoundaryError(f"{role} selected FDE drift")
    notes = _run_tool([str(readelf), "--notes", str(path)], f"{role} notes", 8 << 20)
    if parse_build_id(notes) != artifact["build_id"]:
        raise BoundaryError(f"{role} Build ID drift")
    _validate_semantics(role, instructions, manifest["expected"]["anchors"])
    return {
        "instruction_count": len(instructions),
        "instruction_sha256": instruction_sha,
        "fde_count": len(fdes),
        "fde_sha256": fde_sha,
    }


def _literal_bindings(data_by_role: dict[str, bytes], manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    views = {role: ElfView(data) for role, data in data_by_role.items()}
    values: dict[tuple[str, str], bytes] = {}
    public: dict[str, dict[str, Any]] = {}
    for row in manifest["expected"]["literals"]:
        raw = views[row["binary"]].bytes_at(row["va"], row["length"] + 1, row["role"])
        if raw[-1:] != b"\0" or b"\0" in raw[:-1] or hashlib.sha256(raw[:-1]).hexdigest() != row["sha256"]:
            raise BoundaryError(f"literal identity drift for {row['role']}")
        values[(row["binary"], row["role"])] = raw[:-1]
        public[row["role"]] = {"length": row["length"], "sha256": row["sha256"]}
    if values[("appdmclient", "emitter-interface")] != values[("appfumo", "receiver-interface")]:
        raise BoundaryError("cross-binary interface identity mismatch")
    if values[("appdmclient", "emitter-member")] != values[("appfumo", "receiver-member")]:
        raise BoundaryError("cross-binary member identity mismatch")
    if values[("appfumo", "receiver-member")] == values[("appfumo", "unrelated-member")]:
        raise BoundaryError("corrected and unrelated subscriptions are conflated")
    return public


def _privacy_scan(report: dict[str, Any], supplied_paths: Iterable[Path]) -> None:
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    forbidden_text = [
        "/com/lge/hkmc/avn/upgrade/fota/fotaInterface",
        "com.lge.hkmc.avn.upgrade.fota.fotaInterface",
        "onModePriority",
        "sleep_status",
        "1slotonModePriority(int, QString, QString)",
    ]
    for path in supplied_paths:
        forbidden_text.extend((str(path), str(path.resolve())))
    if any(value and value.encode("utf-8") in encoded for value in forbidden_text):
        raise BoundaryError("public report contains privacy-sensitive material")
    if b"\\x" in encoded:
        raise BoundaryError("public report contains a byte-escape sequence")


def analyze(appdmclient_path: Path, appfumo_path: Path, rootfs_path: Path,
            objdump_path: Path, readelf_path: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    llvm = manifest["llvm"]
    _validate_tool(objdump_path, llvm["version"], llvm["objdump_size"], llvm["objdump_sha256"], "llvm-objdump")
    _validate_tool(readelf_path, llvm["version"], llvm["readelf_size"], llvm["readelf_sha256"], "llvm-readelf")

    _reject_artifact_alias(appdmclient_path, "AppDMClient ELF")
    _reject_artifact_alias(appfumo_path, "AppFUMO ELF")
    appdm_data = _read_regular(appdmclient_path, MAX_ELF_SIZE, "AppDMClient ELF")
    appfumo_data = _read_regular(appfumo_path, MAX_ELF_SIZE, "AppFUMO ELF")
    rootfs = audit_rootfs(rootfs_path, manifest)
    if rootfs["selected"]["appdmclient"] != appdm_data:
        raise BoundaryError("supplied AppDMClient is not the canonical rootfs member")
    outer = rootfs["selected"]["outer_appupgrade"]
    try:
        selected = parse_elf_at(outer, EMBEDDED_OFFSET)
    except EmbeddedElfError as exc:
        raise BoundaryError("embedded ELF structure is invalid") from exc
    if (selected.structural_extent != ARTIFACTS["appfumo"]["size"]
            or selected.build_id != ARTIFACTS["appfumo"]["build_id"]):
        raise BoundaryError("embedded ELF structural extent or Build ID drift")
    embedded_bytes = outer[EMBEDDED_OFFSET:selected.structural_end]
    if embedded_bytes != appfumo_data:
        raise BoundaryError("supplied AppFUMO does not equal the selected structural extent")

    session = parse_session_config(rootfs["selected"]["session_config"])
    inventories = {
        "appdmclient": _analyze_elf("appdmclient", appdmclient_path, appdm_data, objdump_path, readelf_path, manifest),
        "appfumo": _analyze_elf("appfumo", appfumo_path, appfumo_data, objdump_path, readelf_path, manifest),
    }
    literals = _literal_bindings({"appdmclient": appdm_data, "appfumo": appfumo_data}, manifest)
    receiver_class = classify_receiver_filters(
        service_empty=True, path_empty=True, interface_fixed=True, member_fixed=True
    )
    unrelated_class = classify_receiver_filters(
        service_empty=False, path_empty=False, interface_fixed=True, member_fixed=True
    )
    runtime = validate_runtime_facts({
        "same_bus_participation": None,
        "socket_reachability": None,
        "sender_identity": None,
        "signal_delivery": None,
        "slot_execution": None,
        "readiness_success": None,
        "copy_success": None,
    })

    selected_fdes: dict[str, Any] = {}
    for (binary, role), (start, end) in FDE_ROLES.items():
        selected_fdes[f"{binary}:{role}"] = {"start": f"0x{start:x}", "end_exclusive": f"0x{end:x}"}
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "artifacts": {
            "rootfs": {"size": rootfs["size"], "sha256": rootfs["sha256"]},
            "appdmclient": ARTIFACTS["appdmclient"],
            "outer_appupgrade": ARTIFACTS["outer_appupgrade"],
            "appfumo": ARTIFACTS["appfumo"],
            "embedded_selection": {
                "outer_offset": f"0x{EMBEDDED_OFFSET:x}",
                "structural_extent": selected.structural_extent,
                "trailing_container_bytes_included": False,
            },
        },
        "exact_static": {
            "llvm_version": llvm["version"],
            "manifest_sha256": manifest["manifest_sha256"],
            "complete_inventories": inventories,
            "selected_fdes": selected_fdes,
            "sender_direct_call_vas": [f"0x{value:x}" for value in DIRECT_TRANSFERS[("appdmclient", 0x4F1C0)][0]],
            "corrected_subscription_call": "0xe308b",
            "superseded_subscription_call": "0xe2fc5",
            "corrected_receiver_filter_class": receiver_class,
            "superseded_receiver_filter_class": unrelated_class,
            "superseded_member_distinct": True,
            "literal_bindings": literals,
            "interface_bytes_equal_cross_binary": True,
            "member_bytes_equal_cross_binary": True,
        },
        "bridge": {
            "mounted_callback_copies_first_string_to_object_field": True,
            "mounted_callback_object_field_offset": "0x128",
            "mounted_callback_passes_source_to_staging": True,
            "staging_passes_copied_source_to_checker": True,
            "checker_selected_call_uses_fixed_accepted_state": True,
            "checker_source_is_sender_second_string": True,
            "checker_version_is_sender_first_string": True,
            "state_notification_calls_use_empty_strings": True,
            "sender_argument_order": ["status", "version", "source-path"],
            "sender_uses_session_bus": True,
            "sender_calls_signal_send": True,
            "receiver_service_filter_empty": True,
            "receiver_path_filter_empty": True,
            "receiver_interface_filter_fixed": True,
            "receiver_member_filter_fixed": True,
            "generated_receiver_row": 69,
            "consumer_argument_order": ["status", "version", "source-path"],
            "status_global": "0x6d4fb8",
            "version_global": "0x6d4fb0",
            "source_path_global": "0x6d4fa8",
            "accepted_mode_readiness_is_checked": True,
            "copy_call_is_conditional_on_readiness": True,
            "alternate_local_request_is_copy_call": False,
            "accepted_copy_package_base_is_source_path_global": True,
            "archive_class": "package-base-plus-fixed-hidden-news-archive-basename",
        },
        "session_bus_boundary": {
            **session,
            "session_policy_directory_present": True,
            "session_policy_regular_member_count": rootfs["session_d_child_count"],
            "local_override_present": rootfs["session_local_present"],
            "empty_service_and_path_authenticate_sender": False,
            "interface_and_member_authenticate_sender": False,
        },
        "runtime": runtime,
        "scope": {
            "static_pathname_value_continuity_established": True,
            "runtime_delivery_established": False,
            "sender_control_established": False,
            "authentication_success_established": False,
            "copy_success_established": False,
            "code_execution_established": False,
            "root_established": False,
            "partition_write_established": False,
            "boot_acceptance_established": False,
            "persistence_established": False,
            "recovered_target_executed": False,
            "bus_contacted": False,
            "signal_or_method_created_or_sent": False,
        },
    }
    _privacy_scan(report, (appdmclient_path, appfumo_path, rootfs_path, objdump_path, readelf_path, manifest_path))

    if _read_regular(appdmclient_path, MAX_ELF_SIZE, "AppDMClient ELF") != appdm_data:
        raise BoundaryError("AppDMClient changed during analysis")
    if _read_regular(appfumo_path, MAX_ELF_SIZE, "AppFUMO ELF") != appfumo_data:
        raise BoundaryError("AppFUMO changed during analysis")
    if hashlib.sha256(_read_regular(manifest_path, MAX_MANIFEST_SIZE, "manifest")).hexdigest() != manifest["manifest_sha256"]:
        raise BoundaryError("manifest changed during analysis")
    return report


def _write_json(value: Any) -> None:
    raw = (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    sys.stdout.buffer.write(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--appdmclient", type=Path, required=True)
    parser.add_argument("--appfumo", type=Path, required=True)
    parser.add_argument("--rootfs", type=Path, required=True)
    parser.add_argument("--objdump", type=Path, required=True)
    parser.add_argument("--readelf", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = analyze(args.appdmclient, args.appfumo, args.rootfs,
                         args.objdump, args.readelf, args.manifest)
    except (BoundaryError, OSError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    _write_json(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
