#!/usr/bin/env python3
"""Audit the bounded AppFUMO wildcard recovery-signal trust boundary.

The analyzer is static and fail closed.  It hashes and parses one exact embedded
ELF, one canonical rootfs tar stream, one exact kernel configuration, and exact
LLVM tools.  Its JSON contains normalized roles and hashes only: no supplied
paths, target instructions or bytes, callable D-Bus coordinates, signal values,
commands, requests, payloads, packets, or actuation steps.
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

# Reuse the repository's already-tested execution-free ELF, LLVM, and tar
# primitives. Importing this module does not analyze or execute a target.
from appfumo_boot_activation_boundary import (  # type: ignore
    BoundaryError,
    ElfView,
    _HashingReader,
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

SCHEMA_VERSION = 1
TOOL_NAME = "appfumo-dbus-recovery-signal-boundary"
TOOL_VERSION = "1.0.0"
MAX_ELF_SIZE = 64 << 20
MAX_ROOTFS_SIZE = 1 << 30
MAX_KERNEL_CONFIG_SIZE = 1 << 20
MAX_MANIFEST_SIZE = 2 << 20
MAX_SELECTED_MEMBER = 16 << 20
MAX_POLICY_MEMBER = 1 << 20

REQUIRED_ARTIFACTS = {
    "elf": {
        "sha256": "464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7",
        "size": 5066264,
        "build_id": "863a8730e66a1c5245a1bf458fe2554adee0351a",
    },
    "rootfs": {
        "sha256": "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84",
        "size": 879109759,
    },
    "kernel_config": {
        "sha256": "987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56",
        "size": 113598,
    },
}
REQUIRED_FDES = {
    "recovery-subscription-setup": (0xE2790, 0xE2C2B),
    "generated-recovery-dispatch": (0x16DF80, 0x16EFE4),
    "recovery-local-consumer": (0x11F060, 0x11F1A9),
    "separate-recovery-request": (0xE8D10, 0xE907C),
}
REQUIRED_DIRECT_TRANSFERS = {
    0x11F060: ((0x16E8F6,), ()),
    0xE8D10: ((), (0x11F11C,)),
}
REQUIRED_ANCHOR_VAS = {
    0xE27BA, 0xE281E, 0xE282F, 0xE2847,
    0xE2973, 0xE297F, 0xE2984, 0xE298B, 0xE2997, 0xE29A0,
    0xE29AC, 0xE29B3, 0xE29B6, 0xE29B9, 0xE29C4, 0xE29C7,
    0xE29CA, 0xE29D0, 0xE29D7, 0xE29DB, 0xE29DF,
    0x16E8F6,
    0x11F07C, 0x11F088, 0x11F092, 0x11F0D5, 0x11F0DE, 0x11F0E7,
    0x11F0F0, 0x11F0FA, 0x11F0FF, 0x11F11C,
    0xE8D52, 0xE8D57, 0xE8D68, 0xE8D7E, 0xE8D94, 0xE8DD7,
    0xE8E63, 0xE8E68, 0xE8E70, 0xE8E7B, 0xE8E86, 0xE8E99,
}
REQUIRED_LITERALS = {
    "recovery-filter-interface": (0x215273, 21),
    "recovery-filter-member": (0x21E610, 23),
    "bound-receiver-slot": (0x227358, 29),
}
REQUIRED_ROOTFS_ROLES = {
    "system-bus-config": "./etc/dbus-1/system.conf",
    "launcher-unit": "./lib/systemd/system/ApplicationLauncher.service",
    "launcher-script": "./app/bin/AppLauncher.sh",
    "launcher-binary": "./app/bin/AppLauncher",
    "outer-updater": "./app/bin/AppUpgrade",
    "read-only-label-script": "./etc/smack-relabel-ro.sh",
    "runtime-label-script": "./etc/smack_setup.sh",
    "bus-daemon": "./usr/bin/dbus-daemon",
    "qt-dbus-library": "./usr/lib/libQt5DBus.so.5.4.1",
    "qt-dbus-version-config": "./usr/lib/cmake/Qt5DBus/Qt5DBusConfigVersion.cmake",
}
REQUIRED_LAUNCHER_RANGES = {
    "dynamic-process-helper": (0x1FD30, 0x1FFCF),
    "dynamic-process-construction": (0x1FE28, 0x1FEC8),
    "process-start-binding": (0x17426, 0x17462),
    "app-upgrade-role-literal": (0x52D9E, 0x52DA8),
}
SYSTEM_D_DIR = "etc/dbus-1/system.d"
SYSTEM_LOCAL = "etc/dbus-1/system-local.conf"
REQUIRED_POLICY_MEMBER_COUNT = 18
REQUIRED_SELECTED_POLICY_SHA256 = "c7e7354134e32048904297b9f9de8bec2a8bf0d0000bdf4cb6ab79feb56ed5a0"
REQUIRED_NAMED_RECEIVE_ALLOW_COUNT = 15
REQUIRED_NAMED_RECEIVE_DENY_COUNT = 1
REQUIRED_SEND_DESTINATION_VALUE_COUNT = 137
ALLOWED_RULE_ATTRIBUTES = {
    "own", "user", "group",
    "send_type", "send_destination", "send_interface", "send_member",
    "send_requested_reply",
    "receive_type", "receive_sender", "receive_interface", "receive_member",
}
MESSAGE_TYPES = {"method_call", "method_return", "error", "signal"}
DOCTYPE_RE = re.compile(
    rb'<!DOCTYPE\s+busconfig\s+PUBLIC\s+"-//freedesktop//DTD D-B(?:US|us) Bus Configuration 1\.0//EN"\s+'
    rb'"http://www\.freedesktop\.org/standards/dbus/1\.0/busconfig\.dtd"\s*>',
    re.DOTALL,
)


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BoundaryError(f"manifest contains duplicate JSON key: {key}")
        result[key] = value
    return result


def _object(value: Any, keys: Iterable[str], what: str) -> dict[str, Any]:
    expected = set(keys)
    if type(value) is not dict:
        raise BoundaryError(f"{what} must be an object")
    actual = set(value)
    if actual != expected:
        raise BoundaryError(
            f"{what} keys mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
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


def _load_manifest(path: Path) -> dict[str, Any]:
    raw = _read_regular(path, MAX_MANIFEST_SIZE, "manifest")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BoundaryError("manifest is not valid UTF-8 JSON") from exc
    top = _object(value, {"schema_version", "artifacts", "llvm", "expected"}, "manifest")
    if _integer(top["schema_version"], "schema_version") != SCHEMA_VERSION:
        raise BoundaryError("unsupported manifest schema version")

    artifacts_obj = _object(top["artifacts"], {"elf", "rootfs", "kernel_config"}, "artifacts")
    artifacts: dict[str, dict[str, Any]] = {}
    for role in ("elf", "rootfs", "kernel_config"):
        keys = {"sha256", "size", "build_id"} if role == "elf" else {"sha256", "size"}
        row = _object(artifacts_obj[role], keys, f"artifacts.{role}")
        parsed = {
            "sha256": _digest(row["sha256"], f"{role}.sha256"),
            "size": _integer(row["size"], f"{role}.size", MAX_ROOTFS_SIZE),
        }
        if role == "elf":
            parsed["build_id"] = _string(row["build_id"], "elf.build_id", 64)
        if parsed != REQUIRED_ARTIFACTS[role]:
            raise BoundaryError(f"{role} identity does not match the supported audit")
        artifacts[role] = parsed

    llvm_obj = _object(top["llvm"], {
        "version", "objdump_size", "objdump_sha256", "readelf_size", "readelf_sha256",
        "instruction_count", "instruction_sha256", "fde_count", "fde_sha256",
    }, "llvm")
    llvm = {
        "version": _string(llvm_obj["version"], "llvm.version", 128),
        "objdump_size": _integer(llvm_obj["objdump_size"], "llvm.objdump_size", 16 << 20),
        "objdump_sha256": _digest(llvm_obj["objdump_sha256"], "llvm.objdump_sha256"),
        "readelf_size": _integer(llvm_obj["readelf_size"], "llvm.readelf_size", 16 << 20),
        "readelf_sha256": _digest(llvm_obj["readelf_sha256"], "llvm.readelf_sha256"),
        "instruction_count": _integer(llvm_obj["instruction_count"], "llvm.instruction_count", 2_000_000),
        "instruction_sha256": _digest(llvm_obj["instruction_sha256"], "llvm.instruction_sha256"),
        "fde_count": _integer(llvm_obj["fde_count"], "llvm.fde_count", 100_000),
        "fde_sha256": _digest(llvm_obj["fde_sha256"], "llvm.fde_sha256"),
    }
    expected = _load_expected(top["expected"])
    return {
        "artifacts": artifacts,
        "llvm": llvm,
        "expected": expected,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _load_expected(value: Any) -> dict[str, Any]:
    obj = _object(value, {
        "fdes", "direct_transfers", "anchors", "literals", "rootfs",
        "launcher_ranges", "kernel", "daemon_strings", "semantic_assertions",
    }, "expected")

    fdes = []
    for index, item in enumerate(_array(obj["fdes"], "fdes", 16)):
        row = _object(item, {"role", "start", "end_exclusive"}, f"fde {index}")
        fdes.append({
            "role": _string(row["role"], "fde.role", 96),
            "start": _integer(row["start"], "fde.start"),
            "end_exclusive": _integer(row["end_exclusive"], "fde.end_exclusive"),
        })
    if len(fdes) != len(REQUIRED_FDES) or {
        row["role"]: (row["start"], row["end_exclusive"]) for row in fdes
    } != REQUIRED_FDES:
        raise BoundaryError("selected FDE set does not match the supported audit")

    transfers = []
    for index, item in enumerate(_array(obj["direct_transfers"], "direct_transfers", 8)):
        row = _object(item, {"target", "call_vas", "jump_vas"}, f"transfer {index}")
        transfers.append({
            "target": _integer(row["target"], "transfer.target"),
            "call_vas": tuple(_integer(v, "call VA") for v in _array(row["call_vas"], "call_vas", 16)),
            "jump_vas": tuple(_integer(v, "jump VA") for v in _array(row["jump_vas"], "jump_vas", 16)),
        })
    if len(transfers) != len(REQUIRED_DIRECT_TRANSFERS) or {
        row["target"]: (row["call_vas"], row["jump_vas"]) for row in transfers
    } != REQUIRED_DIRECT_TRANSFERS:
        raise BoundaryError("direct-transfer set does not match the supported audit")

    anchors = []
    for index, item in enumerate(_array(obj["anchors"], "anchors", 128)):
        row = _object(item, {"va", "sha256"}, f"anchor {index}")
        anchors.append({"va": _integer(row["va"], "anchor.va"),
                        "sha256": _digest(row["sha256"], "anchor.sha256")})
    if len(anchors) != len(REQUIRED_ANCHOR_VAS) or {row["va"] for row in anchors} != REQUIRED_ANCHOR_VAS:
        raise BoundaryError("machine-anchor set does not match the supported audit")

    literals = []
    for index, item in enumerate(_array(obj["literals"], "literals", 16)):
        row = _object(item, {"role", "va", "length", "sha256"}, f"literal {index}")
        literals.append({
            "role": _string(row["role"], "literal.role", 96),
            "va": _integer(row["va"], "literal.va"),
            "length": _integer(row["length"], "literal.length", 4096),
            "sha256": _digest(row["sha256"], "literal.sha256"),
        })
    if len(literals) != len(REQUIRED_LITERALS) or {
        row["role"]: (row["va"], row["length"]) for row in literals
    } != REQUIRED_LITERALS:
        raise BoundaryError("literal role/range set does not match the supported audit")

    launcher_ranges = []
    for index, item in enumerate(_array(obj["launcher_ranges"], "launcher_ranges", 16)):
        row = _object(item, {"role", "start", "end_exclusive", "sha256"}, f"launcher range {index}")
        launcher_ranges.append({
            "role": _string(row["role"], "launcher_range.role", 96),
            "start": _integer(row["start"], "launcher_range.start"),
            "end_exclusive": _integer(row["end_exclusive"], "launcher_range.end_exclusive"),
            "sha256": _digest(row["sha256"], "launcher_range.sha256"),
        })
    if len(launcher_ranges) != len(REQUIRED_LAUNCHER_RANGES) or {
        row["role"]: (row["start"], row["end_exclusive"]) for row in launcher_ranges
    } != REQUIRED_LAUNCHER_RANGES:
        raise BoundaryError("launcher range set does not match the supported audit")

    rootfs = _load_rootfs_expected(obj["rootfs"])
    kernel_obj = _object(obj["kernel"], {"config_count", "canonical_sha256"}, "kernel")
    kernel = {
        "config_count": _integer(kernel_obj["config_count"], "kernel.config_count", 100_000),
        "canonical_sha256": _digest(kernel_obj["canonical_sha256"], "kernel.canonical_sha256"),
    }
    daemon_obj = _object(obj["daemon_strings"], {
        "ascii_string_count", "ascii_string_sha256", "selinux_named_string_count", "smack_named_string_count",
    }, "daemon_strings")
    daemon = {
        "ascii_string_count": _integer(daemon_obj["ascii_string_count"], "daemon string count", 1_000_000),
        "ascii_string_sha256": _digest(daemon_obj["ascii_string_sha256"], "daemon string hash"),
        "selinux_named_string_count": _integer(daemon_obj["selinux_named_string_count"], "SELinux string count", 1000),
        "smack_named_string_count": _integer(daemon_obj["smack_named_string_count"], "Smack string count", 1000),
    }
    semantic_obj = _object(obj["semantic_assertions"], {
        "unit_execstart_sha256", "launcher_script_dispatch_sha256",
        "read_only_label_assignment_sha256", "runtime_label_assignment_sha256",
        "normalized_exec_label_sha256", "normalized_exec_label_length",
    }, "semantic_assertions")
    semantic = {
        "unit_execstart_sha256": _digest(semantic_obj["unit_execstart_sha256"], "unit ExecStart hash"),
        "launcher_script_dispatch_sha256": _digest(semantic_obj["launcher_script_dispatch_sha256"], "launcher dispatch hash"),
        "read_only_label_assignment_sha256": _digest(semantic_obj["read_only_label_assignment_sha256"], "read-only label hash"),
        "runtime_label_assignment_sha256": _digest(semantic_obj["runtime_label_assignment_sha256"], "runtime label hash"),
        "normalized_exec_label_sha256": _digest(semantic_obj["normalized_exec_label_sha256"], "exec label hash"),
        "normalized_exec_label_length": _integer(semantic_obj["normalized_exec_label_length"], "exec label length", 128),
    }
    return {
        "fdes": fdes, "direct_transfers": transfers, "anchors": anchors,
        "literals": literals, "rootfs": rootfs, "launcher_ranges": launcher_ranges,
        "kernel": kernel, "daemon_strings": daemon, "semantic_assertions": semantic,
    }


def _load_rootfs_expected(value: Any) -> dict[str, Any]:
    obj = _object(value, {
        "member_count", "inventory_sha256", "selected_members", "policy_members",
        "policy_inventory_sha256", "selected_policy_sha256",
    }, "expected.rootfs")
    selected = []
    for index, item in enumerate(_array(obj["selected_members"], "selected_members", 32)):
        row = _object(item, {"role", "name", "type", "mode", "size", "sha256"}, f"selected member {index}")
        selected.append({
            "role": _string(row["role"], "member.role", 96),
            "name": _string(row["name"], "member.name", 512),
            "type": _string(row["type"], "member.type", 16),
            "mode": _integer(row["mode"], "member.mode", 0o7777),
            "size": _integer(row["size"], "member.size", MAX_SELECTED_MEMBER),
            "sha256": _digest(row["sha256"], "member.sha256"),
        })
    if len(selected) != len(REQUIRED_ROOTFS_ROLES) or {
        row["role"]: row["name"] for row in selected
    } != REQUIRED_ROOTFS_ROLES or any(row["type"] != "regular" for row in selected):
        raise BoundaryError("selected rootfs members do not match the supported audit")

    policies = []
    for index, item in enumerate(_array(obj["policy_members"], "policy_members", 64)):
        row = _object(item, {"name_sha256", "mode", "size", "sha256"}, f"policy member {index}")
        policies.append({
            "name_sha256": _digest(row["name_sha256"], "policy name hash"),
            "mode": _integer(row["mode"], "policy mode", 0o7777),
            "size": _integer(row["size"], "policy size", MAX_POLICY_MEMBER),
            "sha256": _digest(row["sha256"], "policy content hash"),
        })
    if len(policies) != REQUIRED_POLICY_MEMBER_COUNT:
        raise BoundaryError("policy member count does not match the supported audit")
    if len({row["name_sha256"] for row in policies}) != len(policies):
        raise BoundaryError("policy member name hashes are duplicated")
    selected_policy_sha256 = _digest(obj["selected_policy_sha256"], "selected policy hash")
    if selected_policy_sha256 != REQUIRED_SELECTED_POLICY_SHA256:
        raise BoundaryError("selected policy identity does not match the supported audit")
    return {
        "member_count": _integer(obj["member_count"], "rootfs.member_count", 1_000_000),
        "inventory_sha256": _digest(obj["inventory_sha256"], "rootfs.inventory_sha256"),
        "selected_members": selected,
        "policy_members": policies,
        "policy_inventory_sha256": _digest(obj["policy_inventory_sha256"], "policy inventory hash"),
        "selected_policy_sha256": selected_policy_sha256,
    }


def _branch_target(item: Any) -> int | None:
    if not item.mnemonic.startswith(("call", "j")):
        return None
    match = re.match(r"0x([0-9a-f]+)(?:\s|$)", item.operands)
    return int(match.group(1), 16) if match else None


def _transfers(instructions: list[Any], target: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    calls = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("call") and _branch_target(item) == target)
    jumps = tuple(item.address for item in instructions
                  if item.mnemonic.startswith("j") and _branch_target(item) == target)
    return calls, jumps


def _validate_machine(instructions: list[Any], expected: dict[str, Any]) -> None:
    by_va = {item.address: item for item in instructions}
    for row in expected["anchors"]:
        item = by_va.get(row["va"])
        if item is None or hashlib.sha256(item.canonical.encode("utf-8")).hexdigest() != row["sha256"]:
            raise BoundaryError("selected machine-anchor identity drift")
    for target, wanted in REQUIRED_DIRECT_TRANSFERS.items():
        if _transfers(instructions, target) != wanted:
            raise BoundaryError("selected direct-transfer inventory drift")


def _parse_doctype_xml(raw: bytes, what: str) -> ET.Element:
    if len(raw) > MAX_POLICY_MEMBER or b"\0" in raw:
        raise BoundaryError(f"{what} is oversized or contains NUL")
    if raw.count(b"<!DOCTYPE") != 1 or raw.count(b"<!ENTITY") or raw.count(b"<![CDATA["):
        raise BoundaryError(f"{what} has unsupported XML declarations")
    match = DOCTYPE_RE.search(raw)
    if match is None:
        raise BoundaryError(f"{what} has an unsupported DOCTYPE")
    without = raw[:match.start()] + raw[match.end():]
    if b"<!DOCTYPE" in without or b"<!ENTITY" in without:
        raise BoundaryError(f"{what} has ambiguous XML declarations")
    try:
        root = ET.fromstring(without)
    except ET.ParseError as exc:
        raise BoundaryError(f"{what} is malformed XML") from exc
    if root.tag != "busconfig" or root.attrib:
        raise BoundaryError(f"{what} has an unsupported root element")
    return root


def _nonspace_text(element: ET.Element) -> bool:
    return bool((element.text or "").strip() or (element.tail or "").strip())


def _validate_rule(element: ET.Element, what: str) -> dict[str, str]:
    if element.tag not in ("allow", "deny") or list(element) or _nonspace_text(element):
        raise BoundaryError(f"{what} has an unsupported policy rule form")
    attrs = dict(element.attrib)
    if not attrs or not set(attrs) <= ALLOWED_RULE_ATTRIBUTES or any(not value for value in attrs.values()):
        raise BoundaryError(f"{what} has unsupported policy rule attributes")
    send = {key for key in attrs if key.startswith("send_")}
    receive = {key for key in attrs if key.startswith("receive_")}
    own = {key for key in attrs if key == "own"}
    connection = {key for key in attrs if key in {"user", "group"}}
    domains = (send, receive, own, connection)
    if sum(bool(domain) for domain in domains) != 1:
        raise BoundaryError(f"{what} mixes unsupported policy rule domains")
    if own and set(attrs) != {"own"}:
        raise BoundaryError(f"{what} mixes ownership rule attributes")
    if connection and (len(connection) != 1 or set(attrs) != connection):
        raise BoundaryError(f"{what} mixes connection rule attributes")
    if connection:
        identity = attrs[next(iter(connection))]
        if not identity.strip() or any(ord(char) < 0x20 for char in identity):
            raise BoundaryError(f"{what} has an invalid connection identity")
    if "send_type" in attrs and attrs["send_type"] not in MESSAGE_TYPES:
        raise BoundaryError(f"{what} has an unknown send type")
    if "receive_type" in attrs and attrs["receive_type"] not in MESSAGE_TYPES:
        raise BoundaryError(f"{what} has an unknown receive type")
    if "send_requested_reply" in attrs and attrs["send_requested_reply"] not in ("true", "false"):
        raise BoundaryError(f"{what} has an unknown requested-reply value")
    return attrs


def _signal_field_matches(expected: str | None, actual: str | None) -> bool:
    return expected is None or expected == "*" or expected == actual


def _signal_rule_matches(attrs: dict[str, str], interface: str, member: str, *,
                         direction: str, sender: str | None = None,
                         destination: str | None = None) -> bool:
    """Apply supported D-Bus rule attributes conjunctively to one signal."""
    if direction not in ("send", "receive"):
        raise BoundaryError("policy signal direction is unsupported")
    if not any(key.startswith(direction + "_") for key in attrs):
        return False
    if attrs.get(direction + "_type", "signal") != "signal":
        return False
    if not _signal_field_matches(attrs.get(direction + "_interface"), interface):
        return False
    if not _signal_field_matches(attrs.get(direction + "_member"), member):
        return False
    if direction == "send":
        if not _signal_field_matches(attrs.get("send_destination"), destination):
            return False
        # A signal is not a requested reply.
        if attrs.get("send_requested_reply") == "true":
            return False
    elif not _signal_field_matches(attrs.get("receive_sender"), sender):
        return False
    return True


def _rule_signal_class(attrs: dict[str, str], interface: str, member: str) -> tuple[str, str] | None:
    """Classify supported rules against the normalized destination-less signal."""
    send = any(key.startswith("send_") for key in attrs)
    receive = any(key.startswith("receive_") for key in attrs)
    if not send and not receive:
        return None
    direction = "send" if send else "receive"
    if attrs.get(direction + "_type", "signal") != "signal":
        return None
    iface = attrs.get(direction + "_interface")
    mem = attrs.get(direction + "_member")
    if not _signal_field_matches(iface, interface) or not _signal_field_matches(mem, member):
        return None
    if direction == "send":
        destination = attrs.get("send_destination")
        if destination not in (None, "*"):
            return None
        if attrs.get("send_requested_reply") == "true":
            return None
    else:
        sender = attrs.get("receive_sender")
        if sender not in (None, "*"):
            return direction, "sender-constrained"
    if ((iface not in (None, "*") and iface == interface)
            or (mem not in (None, "*") and mem == member)):
        return direction, "exact-filter"
    return direction, "general"


def _ordered_signal_effect(rules: list[dict[str, Any]], interface: str, member: str, *,
                           direction: str, sender: str | None = None,
                           destination: str | None = None) -> str:
    """Return the last matching effect within one defined rule order."""
    effect = "no-match"
    for row in rules:
        if _signal_rule_matches(row["attrs"], interface, member, direction=direction,
                                sender=sender, destination=destination):
            effect = row["effect"]
    return effect


def _undefined_order_effect(effects: Iterable[str]) -> str:
    """Resolve effects from sources whose relative order is undefined."""
    material = {effect for effect in effects if effect != "no-match"}
    if not material:
        return "no-match"
    if "unknown" in material or len(material) > 1:
        return "unknown"
    return next(iter(material))


def _apply_scope_precedence(default_effect: str, group_effects: Iterable[str],
                            user_effect: str, at_console_true_effect: str,
                            at_console_false_effect: str,
                            mandatory_effect: str) -> str:
    """Apply documented default, groups, user, console, mandatory precedence."""
    result = default_effect
    for effect in (_undefined_order_effect(group_effects), user_effect,
                   at_console_true_effect, at_console_false_effect,
                   mandatory_effect):
        if effect != "no-match":
            result = effect
    return result


def _validate_policy_scope(attrs: dict[str, str], what: str) -> tuple[tuple[str, str], ...]:
    if len(attrs) != 1:
        raise BoundaryError(f"{what} has unsupported policy scope")
    key, value = next(iter(attrs.items()))
    if key == "context":
        if value not in ("default", "mandatory"):
            raise BoundaryError(f"{what} has unsupported policy context")
    elif key == "at_console":
        if value not in ("true", "false"):
            raise BoundaryError(f"{what} has unsupported console scope")
    elif key in ("user", "group"):
        if not value.strip() or any(ord(char) < 0x20 for char in value):
            raise BoundaryError(f"{what} has invalid identity scope")
    else:
        raise BoundaryError(f"{what} has unsupported policy scope")
    return ((key, value),)


def _parse_policy_container(root: ET.Element, interface: str, member: str,
                            what: str, *, allow_includes: bool) -> dict[str, Any]:
    rules: list[dict[str, Any]] = []
    includes: list[tuple[str, dict[str, str]]] = []
    for child in root:
        if child.tag in ("include", "includedir"):
            if not allow_includes or list(child):
                raise BoundaryError(f"{what} has an unexpected include")
            text = (child.text or "").strip()
            if not text or (child.tail or "").strip():
                raise BoundaryError(f"{what} has a malformed include")
            includes.append((child.tag + ":" + text, dict(child.attrib)))
            continue
        if child.tag != "policy" or list(child) == [] or (child.text or "").strip() or (child.tail or "").strip():
            raise BoundaryError(f"{what} has an unsupported top-level policy form")
        scope = _validate_policy_scope(dict(child.attrib), what)
        for rule_index, rule_element in enumerate(child):
            attrs = _validate_rule(rule_element, what)
            if ({"user", "group"} & set(attrs)) and scope[0][0] not in ("context",):
                raise BoundaryError(f"{what} places a connection rule in an unsupported scope")
            classification = _rule_signal_class(attrs, interface, member)
            rules.append({"effect": rule_element.tag, "scope": scope,
                          "attrs": attrs, "classification": classification,
                          "rule_index": rule_index})
    return {"rules": rules, "includes": includes}


def audit_policy_xml(raw: bytes, interface: str, member: str, *, system_config: bool) -> dict[str, Any]:
    """Strict parser exposed for focused malformed/unsupported-policy tests."""
    root = _parse_doctype_xml(raw, "policy XML")
    if not system_config:
        parsed = _parse_policy_container(root, interface, member, "system policy", allow_includes=False)
        return _summarize_rules(parsed["rules"])

    policy_root = ET.Element("busconfig")
    includes: list[ET.Element] = []
    singleton_tags = {
        "type", "user", "fork", "standard_system_servicedirs", "servicehelper",
        "pidfile", "syslog", "auth", "listen",
    }
    seen: dict[str, int] = {}
    for child in root:
        if child.tag == "policy":
            policy_root.append(child)
        elif child.tag in ("include", "includedir"):
            includes.append(child)
        elif child.tag in singleton_tags:
            seen[child.tag] = seen.get(child.tag, 0) + 1
            if seen[child.tag] != 1 or list(child) or (child.tail or "").strip():
                raise BoundaryError("system config has malformed singleton elements")
        else:
            raise BoundaryError("system config has unsupported elements")
    if set(seen) != singleton_tags:
        raise BoundaryError("system config singleton set is incomplete")
    for element in includes:
        policy_root.append(element)
    parsed = _parse_policy_container(policy_root, interface, member, "system config", allow_includes=True)
    expected_includes = {
        ("includedir:system.d", ()),
        ("include:system-local.conf", (("ignore_missing", "yes"),)),
        ("include:contexts/dbus_contexts", (("if_selinux_enabled", "yes"), ("selinux_root_relative", "yes"))),
    }
    actual_includes = {(name, tuple(sorted(attrs.items()))) for name, attrs in parsed["includes"]}
    if actual_includes != expected_includes:
        raise BoundaryError("system config include set is unexpected")
    summary = _summarize_rules(parsed["rules"])
    default_rules = [row for row in parsed["rules"] if row["scope"] == (("context", "default"),)]
    required = {
        "all_users_connect_allow_rule_count": ("allow", {"user": "*"}),
        "method_call_send_deny_rule_count": ("deny", {"send_type": "method_call"}),
        "signal_send_allow_rule_count": ("allow", {"send_type": "signal"}),
        "signal_receive_allow_rule_count": ("allow", {"receive_type": "signal"}),
    }
    for count_name, (effect, attrs) in required.items():
        count = sum(row["effect"] == effect and row["attrs"] == attrs for row in default_rules)
        if count != 1:
            raise BoundaryError("system config default policy baseline drift")
        summary[count_name] = count
    summary.update({
        "default_policy_rule_count": len(default_rules),
        "default_policy_allow_count": sum(row["effect"] == "allow" for row in default_rules),
        "default_policy_deny_count": sum(row["effect"] == "deny" for row in default_rules),
        "include_count": len(parsed["includes"]),
    })
    return summary


def _summarize_rules(rules: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {
        "rule_count": len(rules),
        "allow_count": sum(row["effect"] == "allow" for row in rules),
        "deny_count": sum(row["effect"] == "deny" for row in rules),
        "exact_filter_allow": 0,
        "exact_filter_deny": 0,
        "general_signal_allow": 0,
        "general_signal_deny": 0,
        "sender_constrained_signal_allow": 0,
        "sender_constrained_signal_deny": 0,
    }
    for row in rules:
        classification = row["classification"]
        if classification is None:
            continue
        _, kind = classification
        count_prefix = {
            "exact-filter": "exact_filter",
            "general": "general_signal",
            "sender-constrained": "sender_constrained_signal",
        }[kind]
        counts[f"{count_prefix}_{row['effect']}"] += 1
    return counts


def _scope_rules(rules: list[dict[str, Any]], scope: tuple[tuple[str, str], ...]) -> list[dict[str, Any]]:
    return [row for row in rules if row["scope"] == scope]


def _later_includedir_effect(main_effect: str, included_effects: Iterable[str]) -> str:
    included = _undefined_order_effect(included_effects)
    return main_effect if included == "no-match" else included


def _analyze_exact_policy_semantics(system_rules: list[dict[str, Any]],
                                    documents: list[dict[str, Any]],
                                    interface: str, member: str) -> dict[str, Any]:
    named_receive: list[dict[str, Any]] = []
    send_destinations: list[tuple[str, int, str]] = []
    for document in documents:
        for index, row in enumerate(document["rules"]):
            attrs = row["attrs"]
            sender = attrs.get("receive_sender")
            if sender is not None and sender != "*" and _rule_signal_class(attrs, interface, member) is not None:
                named_receive.append({"sender": sender, "effect": row["effect"],
                                      "scope": row["scope"], "attrs": attrs,
                                      "source": document["source"]})
            destination = attrs.get("send_destination")
            if destination is not None:
                send_destinations.append((document["source"], index, destination))

    named_allow = sum(row["effect"] == "allow" for row in named_receive)
    named_deny = sum(row["effect"] == "deny" for row in named_receive)
    if (named_allow != REQUIRED_NAMED_RECEIVE_ALLOW_COUNT
            or named_deny != REQUIRED_NAMED_RECEIVE_DENY_COUNT):
        raise BoundaryError("named receive-sender signal rule inventory drift")

    if len(send_destinations) != REQUIRED_SEND_DESTINATION_VALUE_COUNT:
        raise BoundaryError("send-destination rule inventory drift")
    wildcard_destinations = sum(value == "*" for _, _, value in send_destinations)
    named_destinations = sum(value != "*" for _, _, value in send_destinations)
    if wildcard_destinations or named_destinations != REQUIRED_SEND_DESTINATION_VALUE_COUNT:
        raise BoundaryError("send-destination wildcard expectation drift")
    destination_lines = [
        f"{source}\t{index}\t{len(value)}\t{hashlib.sha256(value.encode('utf-8')).hexdigest()}"
        for source, index, value in sorted(send_destinations)
    ]
    destination_inventory_hash = hashlib.sha256(
        "".join(line + "\n" for line in destination_lines).encode("ascii")
    ).hexdigest()

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in named_receive:
        grouped.setdefault(row["sender"], []).append(row)
    paired: list[tuple[str, list[dict[str, Any]]]] = []
    for sender, rows in grouped.items():
        default_denies = [row for row in rows
                          if row["effect"] == "deny"
                          and row["scope"] == (("context", "default"),)
                          and row["attrs"].get("receive_type") == "signal"]
        root_allows = [row for row in rows
                       if row["effect"] == "allow"
                       and row["scope"] == (("user", "root"),)
                       and row["attrs"].get("receive_type") == "signal"]
        if len(default_denies) == 1 and len(root_allows) == 1:
            if default_denies[0]["source"] != root_allows[0]["source"]:
                raise BoundaryError("paired receive-sender policy crosses undefined file order")
            paired.append((sender, rows))
    if len(paired) != 1:
        raise BoundaryError("paired root/default receive-sender group drift")
    paired_sender, _ = paired[0]

    def document_effects(scope: tuple[tuple[str, str], ...], sender: str) -> list[str]:
        return [
            _ordered_signal_effect(_scope_rules(document["rules"], scope), interface, member,
                                   direction="receive", sender=sender)
            for document in documents
        ]

    main_default = _ordered_signal_effect(
        _scope_rules(system_rules, (("context", "default"),)), interface, member,
        direction="receive", sender=paired_sender)
    included_default_effects = document_effects((("context", "default"),), paired_sender)
    default_effect = _later_includedir_effect(main_default, included_default_effects)

    main_root = _ordered_signal_effect(
        _scope_rules(system_rules, (("user", "root"),)), interface, member,
        direction="receive", sender=paired_sender)
    root_included = _undefined_order_effect(document_effects((("user", "root"),), paired_sender))
    root_user_effect = main_root if root_included == "no-match" else root_included

    matching_group_effects = []
    matching_console_effects = []
    matching_mandatory_effects = []
    matching_other_user_effects = []
    all_rule_sets = [system_rules] + [document["rules"] for document in documents]
    for rules in all_rule_sets:
        scopes = {row["scope"] for row in rules}
        for scope in scopes:
            effect = _ordered_signal_effect(_scope_rules(rules, scope), interface, member,
                                            direction="receive", sender=paired_sender)
            key, value = scope[0]
            if key == "group" and effect != "no-match":
                matching_group_effects.append(effect)
            elif key == "at_console" and effect != "no-match":
                matching_console_effects.append(effect)
            elif key == "context" and value == "mandatory" and effect != "no-match":
                matching_mandatory_effects.append(effect)
            elif key == "user" and value != "root" and effect != "no-match":
                matching_other_user_effects.append(effect)
    if matching_group_effects or matching_console_effects or matching_mandatory_effects or matching_other_user_effects:
        raise BoundaryError("paired receive-sender group has an unsupported additional scope override")

    non_root_effect = _apply_scope_precedence(
        default_effect, (), "no-match", "no-match", "no-match", "no-match"
    )
    root_effect = _apply_scope_precedence(
        default_effect, (), root_user_effect, "no-match", "no-match", "no-match"
    )
    if main_default != "allow" or default_effect != "deny" or non_root_effect != "deny" or root_effect != "allow":
        raise BoundaryError("paired receive-sender policy outcome drift")

    cross_file_material = False
    for sender in grouped:
        scopes = {row["scope"] for document in documents for row in document["rules"]}
        for scope in scopes:
            effects = document_effects(scope, sender)
            if _undefined_order_effect(effects) == "unknown":
                cross_file_material = True
    # Destination-less send rules are also part of the normalized signal audit.
    scopes = {row["scope"] for document in documents for row in document["rules"]}
    for scope in scopes:
        effects = [
            _ordered_signal_effect(_scope_rules(document["rules"], scope), interface, member,
                                   direction="send", destination=None)
            for document in documents
        ]
        if _undefined_order_effect(effects) == "unknown":
            cross_file_material = True
    if cross_file_material:
        raise BoundaryError("includedir cross-file order is material for the exact normalized signal")

    return {
        "named_receive_sender_allow_rule_count": named_allow,
        "named_receive_sender_deny_rule_count": named_deny,
        "paired_sender_group": {
            "role": "root-allow-default-deny-signal-sender",
            "length": len(paired_sender),
            "sha256": hashlib.sha256(paired_sender.encode("utf-8")).hexdigest(),
            "root_signal_allow_rule_count": 1,
            "default_signal_deny_rule_count": 1,
            "rules_share_one_policy_member": True,
            "main_default_receive_effect": main_default,
            "non_root_recipient_effect": non_root_effect,
            "root_recipient_effect": root_effect,
            "installed_consumer_effect": None,
        },
        "send_destination_value_count": len(send_destinations),
        "send_destination_named_non_wildcard_count": named_destinations,
        "send_destination_wildcard_count": wildcard_destinations,
        "send_destinationless_broadcast_match_count": 0,
        "send_destination_inventory_sha256": destination_inventory_hash,
        "includedir_cross_file_order_defined": False,
        "includedir_cross_file_order_material_for_exact_signal": False,
    }


def _stream_member(archive: tarfile.TarFile, member: tarfile.TarInfo,
                   maximum: int, what: str, *, retain: bool) -> tuple[str, bytes | None]:
    if member.size > maximum:
        raise BoundaryError(f"{what} exceeds the size bound")
    extracted = archive.extractfile(member)
    if extracted is None:
        raise BoundaryError(f"{what} cannot be streamed")
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = extracted.read(1 << 16)
        if not chunk:
            break
        total += len(chunk)
        if total > member.size:
            raise BoundaryError(f"{what} exceeds its declared size")
        digest.update(chunk)
        if retain:
            chunks.append(chunk)
    if total != member.size:
        raise BoundaryError(f"{what} is truncated")
    return digest.hexdigest(), b"".join(chunks) if retain else None


def _policy_inventory_hash(rows: list[dict[str, Any]]) -> str:
    lines = [
        f"{row['name_sha256']}\t{row['mode']:o}\t{row['size']}\t{row['sha256']}"
        for row in sorted(rows, key=lambda item: item["name_sha256"])
    ]
    return hashlib.sha256("".join(line + "\n" for line in lines).encode("ascii")).hexdigest()


def _audit_rootfs(path: Path, artifact: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    before = _stat_regular(path, MAX_ROOTFS_SIZE, "rootfs archive")
    selected_by_name = {row["name"]: row for row in expected["selected_members"]}
    selected_by_canonical = {_canonical_member_name(name): name for name in selected_by_name}
    retain_roles = {
        "system-bus-config", "launcher-unit", "launcher-script", "launcher-binary",
        "read-only-label-script", "runtime-label-script", "bus-daemon", "qt-dbus-version-config",
    }
    found: dict[str, dict[str, Any]] = {}
    retained: dict[str, bytes] = {}
    policies: list[dict[str, Any]] = []
    policy_raw: dict[str, bytes] = {}
    seen: set[str] = set()
    inventory = hashlib.sha256()
    count = 0
    system_d_dir_seen = False
    system_local_present = False
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
                    if canonical == SYSTEM_LOCAL:
                        system_local_present = True
                    if canonical == SYSTEM_D_DIR:
                        if not member.isdir() or member.linkname or member.name != "./" + SYSTEM_D_DIR:
                            raise BoundaryError("system policy directory type or name drift")
                        system_d_dir_seen = True
                        continue
                    if canonical.startswith(SYSTEM_D_DIR + "/"):
                        relative = canonical[len(SYSTEM_D_DIR) + 1:]
                        if "/" in relative or not relative.endswith(".conf"):
                            raise BoundaryError("system policy directory has an unexpected member")
                        if (member.name != "./" + canonical or not member.isreg()
                                or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                                or member.linkname):
                            raise BoundaryError("system policy member is an alias, link, or special member")
                        digest, content = _stream_member(archive, member, MAX_POLICY_MEMBER,
                                                         "system policy member", retain=True)
                        assert content is not None
                        name_hash = hashlib.sha256(canonical.encode("utf-8", "strict")).hexdigest()
                        row = {"name_sha256": name_hash, "mode": member.mode,
                               "size": member.size, "sha256": digest}
                        policies.append(row)
                        policy_raw[digest] = content
                        continue
                    expected_name = selected_by_canonical.get(canonical)
                    if expected_name is None:
                        continue
                    if member.name != expected_name or expected_name in found:
                        raise BoundaryError("selected rootfs member is duplicated or aliased")
                    row = selected_by_name[expected_name]
                    if (not member.isreg() or member.type not in (tarfile.REGTYPE, tarfile.AREGTYPE)
                            or member.linkname or member.mode != row["mode"] or member.size != row["size"]):
                        raise BoundaryError("selected rootfs member metadata drift")
                    digest, content = _stream_member(
                        archive, member, MAX_SELECTED_MEMBER, "selected rootfs member",
                        retain=row["role"] in retain_roles,
                    )
                    if digest != row["sha256"]:
                        raise BoundaryError("selected rootfs member content drift")
                    found[expected_name] = row
                    if content is not None:
                        retained[row["role"]] = content
            while reader.read(1 << 20):
                pass
            archive_digest = reader.digest.hexdigest()
            descriptor_after = os.fstat(raw_handle.fileno())
    except (tarfile.TarError, OSError, UnicodeEncodeError) as exc:
        raise BoundaryError(f"cannot stream canonical rootfs: {type(exc).__name__}") from exc
    after = _stat_regular(path, MAX_ROOTFS_SIZE, "rootfs archive")
    if not _same_stat(before, after) or not _same_stat(before, descriptor_after):
        raise BoundaryError("rootfs archive changed during analysis")
    if before.st_size != artifact["size"] or archive_digest != artifact["sha256"]:
        raise BoundaryError("rootfs archive identity drift")
    if count != expected["member_count"] or inventory.hexdigest() != expected["inventory_sha256"]:
        raise BoundaryError("complete rootfs inventory drift")
    if set(found) != set(selected_by_name) or not system_d_dir_seen:
        raise BoundaryError("required rootfs members are incomplete")
    if system_local_present:
        raise BoundaryError("canonical rootfs contains a system-local member")
    expected_policies = {row["name_sha256"]: row for row in expected["policy_members"]}
    actual_policies = {row["name_sha256"]: row for row in policies}
    if actual_policies != expected_policies:
        raise BoundaryError("system policy member inventory drift")
    policy_hash = _policy_inventory_hash(policies)
    if policy_hash != expected["policy_inventory_sha256"]:
        raise BoundaryError("system policy inventory hash drift")
    if expected["selected_policy_sha256"] not in policy_raw:
        raise BoundaryError("selected policy member is absent")
    return {
        "sha256": archive_digest,
        "size": before.st_size,
        "member_count": count,
        "inventory_sha256": inventory.hexdigest(),
        "retained": retained,
        "policy_rows": policies,
        "policy_raw": policy_raw,
        "policy_inventory_sha256": policy_hash,
        "selected_policy_sha256": expected["selected_policy_sha256"],
    }


def _parse_kernel_config(raw: bytes) -> tuple[dict[str, str], str]:
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise BoundaryError("kernel config is not ASCII") from exc
    values: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith("#") and not line.startswith("# CONFIG_"):
            continue
        enabled = re.fullmatch(r"(CONFIG_[A-Za-z0-9_]+)=(.+)", line)
        disabled = re.fullmatch(r"# (CONFIG_[A-Za-z0-9_]+) is not set", line)
        if enabled:
            key, value = enabled.groups()
        elif disabled:
            key, value = disabled.group(1), "n"
        else:
            raise BoundaryError("kernel config contains an unsupported line")
        if key in values:
            raise BoundaryError("kernel config contains a duplicate key")
        values[key] = value
    canonical = "".join(f"{key}={values[key]}\n" for key in sorted(values)).encode("ascii")
    return values, hashlib.sha256(canonical).hexdigest()


def _ascii_strings(raw: bytes) -> list[str]:
    return [match.group(0).decode("ascii") for match in re.finditer(rb"[\x20-\x7e]{4,}", raw)]


def _parse_unit(raw: bytes, expected: dict[str, Any]) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BoundaryError("launcher unit is not UTF-8") from exc
    section = ""
    service: dict[str, list[str]] = {}
    for original in text.splitlines():
        line = original.strip()
        if not line or line.startswith(("#", ";")):
            continue
        match = re.fullmatch(r"\[([^\]]+)\]", line)
        if match:
            section = match.group(1)
            continue
        if "=" not in line or not section or line.endswith("\\"):
            raise BoundaryError("launcher unit has unsupported syntax")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key:
            raise BoundaryError("launcher unit has an empty directive")
        if section == "Service":
            service.setdefault(key, []).append(value)
    if "User" in service or "Group" in service:
        raise BoundaryError("launcher unit configured identity drift")
    starts = service.get("ExecStart", [])
    if len(starts) != 1 or hashlib.sha256(starts[0].encode("utf-8")).hexdigest() != expected["unit_execstart_sha256"]:
        raise BoundaryError("launcher unit start directive drift")
    return {"user_directive_present": False, "group_directive_present": False,
            "execstart_hash": expected["unit_execstart_sha256"]}


def _line_hash_match(raw: bytes, digest: str, what: str) -> str:
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise BoundaryError(f"{what} is not UTF-8") from exc
    matches = [line.strip() for line in lines
               if hashlib.sha256(line.strip().encode("utf-8")).hexdigest() == digest]
    if len(matches) != 1:
        raise BoundaryError(f"{what} normalized assertion line drift")
    return matches[0]


def _validate_launcher_and_labels(retained: dict[str, bytes], expected: dict[str, Any],
                                  ranges: list[dict[str, Any]]) -> dict[str, Any]:
    unit = _parse_unit(retained["launcher-unit"], expected)
    _line_hash_match(retained["launcher-script"], expected["launcher_script_dispatch_sha256"], "launcher script")
    ro_line = _line_hash_match(retained["read-only-label-script"], expected["read_only_label_assignment_sha256"], "read-only label script")
    runtime_line = _line_hash_match(retained["runtime-label-script"], expected["runtime_label_assignment_sha256"], "runtime label script")
    label_matches = re.findall(r'"(App::[A-Za-z0-9_:.-]+)"', ro_line + "\n" + runtime_line)
    expected_label_hash = expected["normalized_exec_label_sha256"]
    expected_length = expected["normalized_exec_label_length"]
    if not any(len(value) == expected_length and hashlib.sha256(value.encode("utf-8")).hexdigest() == expected_label_hash
               for value in label_matches):
        raise BoundaryError("normalized updater exec-label identity drift")

    launcher = ElfView(retained["launcher-binary"])
    for row in ranges:
        size = row["end_exclusive"] - row["start"]
        if size <= 0:
            raise BoundaryError("launcher range is empty")
        raw = launcher.bytes_at(row["start"], size, row["role"])
        if hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise BoundaryError("launcher exact-static range drift")
    role = next(row for row in ranges if row["role"] == "app-upgrade-role-literal")
    literal = launcher.bytes_at(role["start"], role["end_exclusive"] - role["start"], role["role"])
    if b"\0" in literal or not re.fullmatch(rb"[A-Za-z][A-Za-z0-9]+", literal):
        raise BoundaryError("launcher role literal is malformed")
    return unit


def _validate_daemon_strings(raw: bytes, expected: dict[str, Any]) -> dict[str, Any]:
    strings = _ascii_strings(raw)
    canonical_hash = hashlib.sha256("".join(value + "\n" for value in strings).encode("ascii")).hexdigest()
    selinux = sum("selinux" in value.lower() for value in strings)
    smack = sum("smack" in value.lower() for value in strings)
    actual = {
        "ascii_string_count": len(strings),
        "ascii_string_sha256": canonical_hash,
        "selinux_named_string_count": selinux,
        "smack_named_string_count": smack,
    }
    if actual != expected:
        raise BoundaryError("canonical bus-daemon string inventory drift")
    if selinux == 0 or smack != 0:
        raise BoundaryError("named bus-daemon integration expectation drift")
    return actual


def _selected_policy_shape(raw: bytes, interface: str, member: str) -> None:
    root = _parse_doctype_xml(raw, "selected policy")
    parsed = _parse_policy_container(root, interface, member, "selected policy", allow_includes=False)
    rules = parsed["rules"]
    if len(rules) != 2 or any(row["effect"] != "allow" or row["scope"] != (("user", "root"),) for row in rules):
        raise BoundaryError("selected policy shape drift")
    attrs = [row["attrs"] for row in rules]
    if {next(iter(row)) for row in attrs if len(row) == 1} != {"own", "send_destination"}:
        raise BoundaryError("selected policy grants drift")
    values = [next(iter(row.values())) for row in attrs]
    if len(set(values)) != 1:
        raise BoundaryError("selected policy role identity drift")
    if any(row["classification"] is not None for row in rules):
        raise BoundaryError("selected policy unexpectedly matches recovery signals")


def analyze(elf_path: Path, rootfs_path: Path, kernel_config_path: Path,
            objdump_path: Path, readelf_path: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    artifacts = manifest["artifacts"]
    llvm = manifest["llvm"]
    expected = manifest["expected"]
    _validate_tool(objdump_path, llvm["version"], llvm["objdump_size"], llvm["objdump_sha256"], "llvm-objdump")
    _validate_tool(readelf_path, llvm["version"], llvm["readelf_size"], llvm["readelf_sha256"], "llvm-readelf")

    elf_data = _read_regular(elf_path, MAX_ELF_SIZE, "ELF")
    elf_sha = hashlib.sha256(elf_data).hexdigest()
    if len(elf_data) != artifacts["elf"]["size"] or elf_sha != artifacts["elf"]["sha256"]:
        raise BoundaryError("ELF identity drift")
    elf = ElfView(elf_data)
    instructions = parse_disassembly(_run_tool(
        [str(objdump_path), "-d", "--no-show-raw-insn", str(elf_path)], "llvm-objdump disassembly"))
    if len(instructions) != llvm["instruction_count"] or _canonical_hash(
            item.canonical for item in instructions) != llvm["instruction_sha256"]:
        raise BoundaryError("complete instruction identity drift")
    fdes = parse_fdes(_run_tool([str(readelf_path), "--unwind", str(elf_path)], "llvm-readelf unwind"))
    if len(fdes) != llvm["fde_count"] or _canonical_hash(
            f"{start:x}-{end:x}" for start, end in fdes) != llvm["fde_sha256"]:
        raise BoundaryError("complete FDE identity drift")
    fde_map = dict(fdes)
    if any(fde_map.get(start) != end for start, end in REQUIRED_FDES.values()):
        raise BoundaryError("selected FDE identity drift")
    notes = _run_tool([str(readelf_path), "--notes", str(elf_path)], "llvm-readelf notes", 8 << 20)
    if parse_build_id(notes) != artifacts["elf"]["build_id"]:
        raise BoundaryError("ELF Build ID drift")
    _validate_machine(instructions, expected)

    literal_values: dict[str, str] = {}
    literal_public: dict[str, dict[str, Any]] = {}
    for row in expected["literals"]:
        raw = elf.bytes_at(row["va"], row["length"] + 1, row["role"])
        if raw[-1:] != b"\0" or b"\0" in raw[:-1] or hashlib.sha256(raw[:-1]).hexdigest() != row["sha256"]:
            raise BoundaryError("selected literal identity drift")
        try:
            value = raw[:-1].decode("ascii")
        except UnicodeDecodeError as exc:
            raise BoundaryError("selected literal is not ASCII") from exc
        literal_values[row["role"]] = value
        literal_public[row["role"]] = {"length": row["length"], "sha256": row["sha256"]}
    interface = literal_values["recovery-filter-interface"]
    member = literal_values["recovery-filter-member"]
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", interface) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", member):
        raise BoundaryError("recovery filter literals are not valid normalized identifiers")

    rootfs = _audit_rootfs(rootfs_path, artifacts["rootfs"], expected["rootfs"])
    system_config_raw = rootfs["retained"]["system-bus-config"]
    system_summary = audit_policy_xml(system_config_raw, interface, member, system_config=True)
    system_root = _parse_doctype_xml(system_config_raw, "system config")
    system_policy_root = ET.Element("busconfig")
    for child in system_root:
        if child.tag == "policy":
            system_policy_root.append(child)
    system_rules = _parse_policy_container(
        system_policy_root, interface, member, "system config policies", allow_includes=False
    )["rules"]

    system_d_summaries = []
    policy_documents = []
    for row in rootfs["policy_rows"]:
        content = rootfs["policy_raw"].get(row["sha256"])
        if content is None:
            raise BoundaryError("policy content identity is ambiguous")
        policy_root = _parse_doctype_xml(content, "system policy")
        parsed_policy = _parse_policy_container(
            policy_root, interface, member, "system policy", allow_includes=False
        )
        system_d_summaries.append(_summarize_rules(parsed_policy["rules"]))
        policy_documents.append({"source": row["name_sha256"], "rules": parsed_policy["rules"]})
    combined = {key: sum(item[key] for item in system_d_summaries)
                for key in system_d_summaries[0] if key != "include_count"}
    policy_semantics = _analyze_exact_policy_semantics(
        system_rules, policy_documents, interface, member
    )
    _selected_policy_shape(rootfs["policy_raw"][rootfs["selected_policy_sha256"]], interface, member)
    if combined["exact_filter_allow"] or combined["exact_filter_deny"] or combined["general_signal_allow"] or combined["general_signal_deny"]:
        raise BoundaryError("canonical system policy directory contains an unexpected matching signal rule")

    kernel_raw = _read_regular(kernel_config_path, MAX_KERNEL_CONFIG_SIZE, "kernel config")
    if len(kernel_raw) != artifacts["kernel_config"]["size"] or hashlib.sha256(kernel_raw).hexdigest() != artifacts["kernel_config"]["sha256"]:
        raise BoundaryError("kernel config identity drift")
    kernel_values, kernel_canonical_hash = _parse_kernel_config(kernel_raw)
    if len(kernel_values) != expected["kernel"]["config_count"] or kernel_canonical_hash != expected["kernel"]["canonical_sha256"]:
        raise BoundaryError("kernel config canonical inventory drift")
    if kernel_values.get("CONFIG_SECURITY_SMACK") != "y" or kernel_values.get("CONFIG_SECURITY_SELINUX") != "n" or kernel_values.get("CONFIG_SECURITY_APPARMOR") != "n":
        raise BoundaryError("kernel mandatory-access-control selection drift")

    unit = _validate_launcher_and_labels(rootfs["retained"], expected["semantic_assertions"], expected["launcher_ranges"])
    daemon_strings = _validate_daemon_strings(rootfs["retained"]["bus-daemon"], expected["daemon_strings"])
    qt_version_raw = rootfs["retained"]["qt-dbus-version-config"]
    if not re.search(rb'PACKAGE_VERSION\s+"?5\.[0-9.]+"?', qt_version_raw):
        raise BoundaryError("canonical Qt D-Bus major version drift")

    if _read_regular(elf_path, MAX_ELF_SIZE, "ELF") != elf_data:
        raise BoundaryError("ELF changed during analysis")
    if _read_regular(kernel_config_path, MAX_KERNEL_CONFIG_SIZE, "kernel config") != kernel_raw:
        raise BoundaryError("kernel config changed during analysis")
    if hashlib.sha256(_read_regular(manifest_path, MAX_MANIFEST_SIZE, "manifest")).hexdigest() != manifest["manifest_sha256"]:
        raise BoundaryError("manifest changed during analysis")
    for tool_path, size_key, digest_key, what in (
        (objdump_path, "objdump_size", "objdump_sha256", "llvm-objdump"),
        (readelf_path, "readelf_size", "readelf_sha256", "llvm-readelf"),
    ):
        tool_raw = _read_regular(tool_path, 16 << 20, what)
        if len(tool_raw) != llvm[size_key] or hashlib.sha256(tool_raw).hexdigest() != llvm[digest_key]:
            raise BoundaryError(f"{what} changed during analysis")

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": TOOL_NAME, "version": TOOL_VERSION},
        "artifacts": {
            "elf": {"sha256": elf_sha, "size": len(elf_data), "build_id": artifacts["elf"]["build_id"]},
            "rootfs": {"sha256": rootfs["sha256"], "size": rootfs["size"]},
            "kernel_config": {"sha256": artifacts["kernel_config"]["sha256"], "size": len(kernel_raw)},
        },
        "exact_static": {
            "selected_fdes": {role: {"start": f"0x{start:x}", "end_exclusive": f"0x{end:x}"}
                               for role, (start, end) in REQUIRED_FDES.items()},
            "complete_instruction_count": len(instructions),
            "complete_instruction_sha256": llvm["instruction_sha256"],
            "complete_fde_count": len(fdes),
            "complete_fde_sha256": llvm["fde_sha256"],
            "recovery_connect_call": "0xe29df",
            "connect_service_filter_empty": True,
            "connect_path_filter_empty": True,
            "connect_interface_filter_fixed": True,
            "connect_member_filter_fixed": True,
            "connect_receiver_bound": True,
            "connect_slot_bound": True,
            "literal_bindings": literal_public,
            "generated_dispatch_reaches_local_consumer": True,
            "input_nonempty_and_normalized_value_guarded": True,
            "local_state_guards_precede_request": True,
            "consumer_tail_reaches_separate_request": True,
            "separate_request_argument_shape": "single-byte-array-argument-value-redacted",
            "separate_request_is_asynchronous": True,
            "separate_request_coordinates_redacted": True,
            "remote_action_confirmed": False,
        },
        "qt5_semantics": {
            "canonical_qt_major": 5,
            "empty_service_filter_matches_any_remote_bus_application": True,
            "empty_path_filter_matches_any_path": True,
            "fixed_interface_and_member_are_message_filters_not_sender_authentication": True,
            "wildcard_filter_means_message_acceptance_not_message_forgery": True,
        },
        "canonical_policy": {
            "rootfs_member_count": rootfs["member_count"],
            "rootfs_inventory_sha256": rootfs["inventory_sha256"],
            "system_conf_policy_rule_count": system_summary["rule_count"],
            "system_conf_policy_allow_count": system_summary["allow_count"],
            "system_conf_policy_deny_count": system_summary["deny_count"],
            "system_conf_default_policy_rule_count": system_summary["default_policy_rule_count"],
            "system_conf_default_policy_allow_count": system_summary["default_policy_allow_count"],
            "system_conf_default_policy_deny_count": system_summary["default_policy_deny_count"],
            "system_conf_default_all_users_connect_allow_rule_count": system_summary["all_users_connect_allow_rule_count"],
            "system_conf_default_method_call_send_deny_rule_count": system_summary["method_call_send_deny_rule_count"],
            "system_conf_default_signal_send_allow_rule_count": system_summary["signal_send_allow_rule_count"],
            "system_conf_default_signal_receive_allow_rule_count": system_summary["signal_receive_allow_rule_count"],
            "system_conf_default_all_users_may_connect": True,
            "system_conf_default_send_signal_allowed": True,
            "system_conf_default_receive_signal_allowed": True,
            "system_conf_default_method_call_send_denied": True,
            "system_d_policy_member_count": len(rootfs["policy_rows"]),
            "system_d_policy_inventory_sha256": rootfs["policy_inventory_sha256"],
            "system_d_policy_rule_count": combined["rule_count"],
            "system_d_policy_allow_count": combined["allow_count"],
            "system_d_policy_deny_count": combined["deny_count"],
            "system_d_policy_exact_filter_allow_count": combined["exact_filter_allow"],
            "system_d_policy_exact_filter_deny_count": combined["exact_filter_deny"],
            "system_d_policy_general_signal_allow_count": combined["general_signal_allow"],
            "system_d_policy_general_signal_deny_count": combined["general_signal_deny"],
            "system_d_named_receive_sender_allow_rule_count": policy_semantics["named_receive_sender_allow_rule_count"],
            "system_d_named_receive_sender_deny_rule_count": policy_semantics["named_receive_sender_deny_rule_count"],
            "system_d_paired_receive_sender_group": policy_semantics["paired_sender_group"],
            "system_d_send_destination_value_count": policy_semantics["send_destination_value_count"],
            "system_d_send_destination_named_non_wildcard_count": policy_semantics["send_destination_named_non_wildcard_count"],
            "system_d_send_destination_wildcard_count": policy_semantics["send_destination_wildcard_count"],
            "system_d_send_destinationless_broadcast_match_count": policy_semantics["send_destinationless_broadcast_match_count"],
            "system_d_send_destination_inventory_sha256": policy_semantics["send_destination_inventory_sha256"],
            "policy_rules_are_conjunctive": True,
            "policy_rule_order_semantics": "last-matching-rule-wins",
            "policy_scope_precedence": [
                "default", "groups", "user", "at-console-true",
                "at-console-false", "mandatory"
            ],
            "group_scope_relative_order_defined": False,
            "includedir_cross_file_order_defined": policy_semantics["includedir_cross_file_order_defined"],
            "includedir_cross_file_order_material_for_exact_signal": policy_semantics["includedir_cross_file_order_material_for_exact_signal"],
            "includedir_same_scope_conflict_resolution": "unknown",
            "selected_policy_root_own_and_destination_grants": True,
            "selected_policy_authenticates_broadcast_signal_origin": False,
            "archive_system_local_member_present": False,
            "runtime_system_local_or_include_replacement": None,
            "dynamic_include_effect": None,
        },
        "launcher_and_identity": {
            "launcher_unit_user_directive_present": unit["user_directive_present"],
            "systemd_configured_default_uid_role": "root",
            "launcher_script_starts_launcher": True,
            "launcher_contains_dynamic_app_process_construction_for_updater_role": True,
            "launcher_runtime_dynamic_path": None,
            "outer_updater_canonical_member_bound": True,
            "updater_exec_label_assignment_named_in_both_canonical_scripts": True,
            "complete_installed_runtime_uid": None,
            "complete_installed_runtime_label": None,
        },
        "mandatory_access_control": {
            "kernel_smack_enabled": True,
            "kernel_selinux_enabled": False,
            "kernel_apparmor_enabled": False,
            "bus_daemon_selinux_named_strings_present": daemon_strings["selinux_named_string_count"] > 0,
            "bus_daemon_smack_named_strings_present": daemon_strings["smack_named_string_count"] > 0,
            "named_bus_daemon_smack_integration_established": False,
            "kernel_socket_mediation": None,
            "arbitrary_label_same_bus_admission": None,
            "uid_root_implies_smack_escape": False,
        },
        "finding": {
            "classification": "conditional-wildcard-signal-trust-boundary",
            "normalized_shape": "matching-signal-to-privileged-local-consumer-to-separate-asynchronous-recovery-request",
            "bus_policy_permission_equals_same_bus_socket_reachability": False,
            "interface_member_match_authenticates_sender": False,
            "local_slot_invocation_confirms_external_action": False,
            "recovery_control_implies_code_execution_or_root": False,
            "code_execution_established": False,
            "root_transition_established": False,
            "persistence_established": False,
        },
        "unknowns": {
            "runtime_consumer_uid_and_label": None,
            "runtime_sender_uid_and_label": None,
            "same_bus_socket_reachability_for_arbitrary_label": None,
            "kernel_socket_mediation_effect": None,
            "dynamic_policy_replacement_or_generated_include": None,
            "signal_observed": None,
            "local_slot_observed": None,
            "external_recovery_action": None,
        },
        "scope": {
            "exact_static_analysis": True,
            "canonical_rootfs_streamed": True,
            "target_code_executed": False,
            "bus_connected": False,
            "signal_or_method_sent": False,
            "operational_request_created": False,
            "payload_or_packet_created": False,
            "flash_update_or_persistence_action": False,
            "supplied_paths_emitted": False,
            "target_instructions_or_bytes_emitted": False,
            "callable_dbus_coordinates_emitted": False,
            "signal_or_argument_values_emitted": False,
            "commands_or_exploit_steps_emitted": False,
        },
        "evidence": {
            "llvm_version": llvm["version"],
            "manifest_sha256": manifest["manifest_sha256"],
            "kernel_config_count": len(kernel_values),
            "kernel_config_canonical_sha256": kernel_canonical_hash,
            "bus_daemon_ascii_string_count": daemon_strings["ascii_string_count"],
            "bus_daemon_ascii_string_sha256": daemon_strings["ascii_string_sha256"],
        },
    }


def _write_json(value: Any) -> None:
    sys.stdout.buffer.write((json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--elf", required=True, type=Path)
    parser.add_argument("--rootfs", required=True, type=Path)
    parser.add_argument("--kernel-config", required=True, type=Path)
    parser.add_argument("--llvm-objdump", required=True, type=Path)
    parser.add_argument("--llvm-readelf", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = analyze(args.elf, args.rootfs, args.kernel_config,
                         args.llvm_objdump, args.llvm_readelf, args.manifest)
    except BoundaryError as exc:
        sys.stderr.buffer.write((f"error: {exc}\n").encode("utf-8"))
        return 2
    _write_json(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
