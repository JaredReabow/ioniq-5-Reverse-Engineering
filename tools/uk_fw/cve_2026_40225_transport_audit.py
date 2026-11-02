#!/usr/bin/env python3
"""Build a deterministic transport matrix for recovered CVE-2026-40225 paths.

This host-only audit reads and hashes files. It does not execute recovered code,
boot a VM, access hardware, generate descriptors, or construct injected udev
properties.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

SCHEMA = "ioniq-cve-2026-40225-transport-audit/v1"
CONTROL_SCHEMA = "ioniq-usb-scsi-rule-precedence/v1"
MAX_FILE_BYTES = 64 * 1024 * 1024
EXPECTED_CONFIG_SHA256 = "987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56"
EXPECTED_FILES = {
    "bin/udevadm": "b3d0274757f9ded9260f22a629da22e1e06ef0f6c750293b317e09810c93692b",
    "lib/udev/scsi_id": "85aa83a73d44f19f6b60162a53ee896854b71e7882848819aad20c1ccf079b32",
    "lib/udev/v4l_id": "afb756b457284578c29960d4abd57f9612020fb45a14fbc285f5061da90a7125",
    "lib/udev/rules.d/50-udev-default.rules": "c90d7b298f009b82995fdcb288cd717e6d196640b0c8d3d1505b9cb402de7039",
    "lib/udev/rules.d/60-persistent-storage.rules": "5757bc1da0b3e07ee1769faa266af7720b8eef21006212051a8720c02eab5a8e",
    "lib/udev/rules.d/60-persistent-v4l.rules": "219eb6b4c0df4d8701cc5a316b2ddf63797d4c1b689bc0b289d5cb8063a7034e",
    "lib/udev/rules.d/99-systemd.rules": "87799b92929bed3766a2c6f7a186035886043e62f93fa3bf9995cc8ca66fdd5c",
    "lib/systemd/system/debug-shell.service": "b277d7ffcfdbc9198af6935b64c167c8f7d50ec9ec9acb93b5f7b5d815cfe518",
}
EXPECTED_CONTROL_MARKERS = (
    "USB_SCSI_RULE_PROBE_BEGIN",
    "USB_SCSI_RULE_ARTIFACTS=verified",
    "USB_SCSI_RULE_MODULES=loaded",
    "USB_SCSI_RULE_TARGET=sda",
    "USB_SCSI_RULE_USB_SERIAL_ATTR=absent",
    "USB_SCSI_RULE_BLOCK_READONLY=1",
    "USB_SCSI_RULE_ROOT_READONLY=1",
    "USB_SCSI_RULE_UDEVADM_RC=0",
    "USB_SCSI_RULE_USB_ID_IMPORT=present",
    "USB_SCSI_RULE_ID_BUS=usb",
    "USB_SCSI_RULE_ID_SERIAL=QEMU_QEMU_HARDDISK-0:0",
    "USB_SCSI_RULE_ID_SERIAL_SHORT=absent",
    "USB_SCSI_RULE_ID_SCSI_SERIAL=absent",
    "USB_SCSI_RULE_SCSI_ID_EXECUTION=absent",
    "USB_SCSI_RULE_PROBE_COMPLETE",
)
CONFIG_RE = re.compile(r"^CONFIG_([A-Z0-9_]+)=(.*)$")
NOT_SET_RE = re.compile(r"^# CONFIG_([A-Z0-9_]+) is not set$")


class AuditError(ValueError):
    """Fail-closed audit input error."""


def stable_read(path: Path, limit: int = MAX_FILE_BYTES) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise AuditError(f"cannot open regular no-follow input {path}: {exc}") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise AuditError(f"input is not a regular file: {path}")
        if before.st_size > limit:
            raise AuditError(f"input exceeds {limit} byte limit: {path}")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, limit + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                raise AuditError(f"input exceeds {limit} byte limit: {path}")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    current = os.stat(path, follow_symlinks=False)
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    identity_current = (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns)
    if identity_before != identity_after or identity_after != identity_current:
        raise AuditError(f"input identity changed while reading: {path}")
    return b"".join(chunks)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_json(data: bytes, path: Path) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise AuditError(f"non-finite JSON constant in {path}: {value}")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise AuditError(f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result

    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise AuditError(f"input is not strict UTF-8: {path}: {exc}") from exc
    try:
        value = json.loads(
            text, object_pairs_hook=unique_object, parse_constant=reject_constant
        )
    except json.JSONDecodeError as exc:
        raise AuditError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"top-level JSON must be an object: {path}")
    return value


def parse_config(data: bytes) -> dict[str, str]:
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise AuditError(f"kernel config is not strict UTF-8: {exc}") from exc
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = CONFIG_RE.fullmatch(line)
        if match:
            values[match.group(1)] = match.group(2)
            continue
        match = NOT_SET_RE.fullmatch(line)
        if match:
            values[match.group(1)] = "n"
    return values


def require_config(config: dict[str, str], name: str, expected: str) -> None:
    observed = config.get(name)
    if observed != expected:
        raise AuditError(f"CONFIG_{name}: expected {expected!r}, observed {observed!r}")


def read_expected(rootfs: Path, relative: str, expected: str) -> bytes:
    data = stable_read(rootfs / relative)
    observed = sha256(data)
    if observed != expected:
        raise AuditError(
            f"hash mismatch for {relative}: expected {expected}, observed {observed}"
        )
    return data


def exact_line_number(data: bytes, expected_line: str, label: str) -> int:
    try:
        lines = data.decode("utf-8", "strict").splitlines()
    except UnicodeDecodeError as exc:
        raise AuditError(f"{label} is not strict UTF-8: {exc}") from exc
    matches = [index for index, line in enumerate(lines, 1) if line == expected_line]
    if len(matches) != 1:
        raise AuditError(f"{label}: expected one exact line, found {len(matches)}")
    return matches[0]


def module_inventory(rootfs: Path) -> tuple[list[dict[str, str]], str]:
    base = rootfs / "lib/modules/4.1.27-abl/kernel"
    if not base.is_dir() or base.is_symlink():
        raise AuditError("kernel module directory is missing or is a symlink")
    paths: list[Path] = []
    for current, directories, files in os.walk(base, followlinks=False):
        current_path = Path(current)
        for name in list(directories):
            candidate = current_path / name
            if candidate.is_symlink():
                raise AuditError(f"symlink in bounded module tree: {candidate}")
        for name in files:
            candidate = current_path / name
            if candidate.is_symlink():
                raise AuditError(f"symlink in bounded module tree: {candidate}")
            if name.endswith(".ko"):
                paths.append(candidate)
    records: list[dict[str, str]] = []
    for path in sorted(paths, key=lambda value: value.as_posix()):
        data = stable_read(path)
        records.append(
            {
                "path": path.relative_to(rootfs).as_posix(),
                "sha256": sha256(data),
            }
        )
    canonical = json.dumps(records, separators=(",", ":"), sort_keys=True).encode()
    return records, sha256(canonical)


def validate_control(report: dict[str, Any]) -> None:
    if report.get("schema") != CONTROL_SCHEMA:
        raise AuditError(f"USB control schema must be {CONTROL_SCHEMA}")
    if report.get("classification") != "usb-id-suppresses-scsi-id":
        raise AuditError("USB control does not have the accepted classification")
    if report.get("network") != "disabled by vm_boot (-nic none)":
        raise AuditError("USB control network boundary differs")
    if report.get("salient_lines") != list(EXPECTED_CONTROL_MARKERS):
        raise AuditError("USB control marker sequence differs")
    guest = report.get("guest_artifacts")
    if not isinstance(guest, dict):
        raise AuditError("USB control guest_artifacts must be an object")
    required_control_files = (
        "bin/udevadm",
        "lib/udev/scsi_id",
        "lib/udev/rules.d/60-persistent-storage.rules",
    )
    for relative in required_control_files:
        absolute = "/" + relative
        expected = EXPECTED_FILES[relative]
        if guest.get(absolute) != expected:
            raise AuditError(f"USB control identity mismatch for {absolute}")
    attached = report.get("attached_disk")
    if not isinstance(attached, dict):
        raise AuditError("USB control attached_disk must be an object")
    if attached.get("sha256") != "bb9f8df61474d25e71fa00722318cd387396ca1736605e1248821cc0de3d3af8":
        raise AuditError("USB control zero-disk identity differs")
    if attached.get("qemu_access") != "snapshot=on,readonly=on":
        raise AuditError("USB control disk was not read-only and snapshot-backed")
    if attached.get("usb_serial") != "explicitly empty":
        raise AuditError("USB control serial was not explicitly empty")


def build_report(config_path: Path, rootfs: Path, control_path: Path) -> dict[str, Any]:
    config_data = stable_read(config_path)
    config_hash = sha256(config_data)
    if config_hash != EXPECTED_CONFIG_SHA256:
        raise AuditError(
            f"kernel config hash mismatch: expected {EXPECTED_CONFIG_SHA256}, observed {config_hash}"
        )
    config = parse_config(config_data)
    requirements = {
        "SCSI": "m",
        "BLK_DEV_SD": "m",
        "USB_STORAGE": "m",
        "SCSI_ISCSI_ATTRS": "n",
        "SCSI_LOWLEVEL": "n",
        "MEDIA_USB_SUPPORT": "n",
        "VIDEO_DEV": "y",
        "VIDEO_V4L2": "y",
        "VIDEO_INTEL_IPU4": "y",
        "VIDEO_INTEL_IPU4_SOC": "y",
        "INTEL_IPU4_ADV7282": "y",
        "INTEL_IPU4_MAX9288": "y",
        "INTEL_IPU4_MAX9288_INCAM": "y",
    }
    for name, expected in requirements.items():
        require_config(config, name, expected)

    file_data = {
        relative: read_expected(rootfs, relative, digest)
        for relative, digest in EXPECTED_FILES.items()
    }
    storage = file_data["lib/udev/rules.d/60-persistent-storage.rules"]
    usb_line = exact_line_number(
        storage,
        'KERNEL=="sd*[!0-9]|sr*", ENV{ID_SERIAL}!="?*", SUBSYSTEMS=="usb", IMPORT{builtin}="usb_id"',
        "USB storage identity rule",
    )
    scsi_line = exact_line_number(
        storage,
        'KERNEL=="sd*[!0-9]|sr*", ENV{ID_SERIAL}!="?*", IMPORT{program}="scsi_id --export --whitelisted -d $devnode", ENV{ID_BUS}="scsi"',
        "SCSI identity rule",
    )
    if usb_line >= scsi_line:
        raise AuditError("usb_id rule does not precede scsi_id rule")
    v4l_line = exact_line_number(
        file_data["lib/udev/rules.d/60-persistent-v4l.rules"],
        'IMPORT{program}="v4l_id $devnode"',
        "V4L import rule",
    )
    remove_line = exact_line_number(
        file_data["lib/udev/rules.d/50-udev-default.rules"],
        'ACTION=="remove", ENV{REMOVE_CMD}!="", RUN+="$env{REMOVE_CMD}"',
        "REMOVE_CMD rule",
    )

    control_data = stable_read(control_path)
    control = strict_json(control_data, control_path)
    validate_control(control)
    modules, module_digest = module_inventory(rootfs)
    module_paths = [record["path"].lower() for record in modules]
    iscsi_modules = [path for path in module_paths if "iscsi" in path]
    usb_video_modules = [path for path in module_paths if "uvc" in path or "usbvideo" in path]
    if iscsi_modules or usb_video_modules:
        raise AuditError("module inventory contradicts disabled transport configuration")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": {
            "kernel_config": {
                "sha256": config_hash,
                "bytes": len(config_data),
            },
            "rootfs_files": EXPECTED_FILES,
            "usb_scsi_control": {
                "sha256": sha256(control_data),
                "schema": control["schema"],
                "classification": control["classification"],
            },
            "module_inventory": {
                "count": len(modules),
                "canonical_sha256": module_digest,
                "iscsi_matches": iscsi_modules,
                "usb_video_matches": usb_video_modules,
            },
        },
        "config": {name: config[name] for name in sorted(requirements)},
        "rule_order": {
            "usb_id_line": usb_line,
            "scsi_id_line": scsi_line,
            "usb_id_precedes_scsi_id": True,
            "v4l_id_line": v4l_line,
            "remove_cmd_line": remove_line,
        },
        "transports": {
            "ordinary_usb_mass_storage_to_scsi_id": {
                "state": "suppressed-by-prior-usb-id",
                "basis": "exact empty-iSerial VM control plus exact rule order",
            },
            "iscsi_to_scsi_id": {
                "state": "not-built",
                "basis": "CONFIG_SCSI_ISCSI_ATTRS=n and no installed iSCSI module",
            },
            "generic_usb_v4l_to_v4l_id": {
                "state": "not-built",
                "basis": "CONFIG_MEDIA_USB_SUPPORT=n and no installed UVC/usbvideo module",
            },
            "platform_ipu4_camera_to_v4l_id": {
                "state": "built-in-external-control-unproved",
                "basis": "Intel IPU4 SOC with ADV7282/MAX9288 inputs is enabled",
            },
            "other_scsi_to_scsi_id": {
                "state": "unproved",
                "basis": "CONFIG_SCSI_LOWLEVEL=n; USB storage exists but is suppressed in the accepted ordinary geometry",
            },
        },
        "verdict": {
            "vulnerable_helper_mechanisms_present": True,
            "downstream_privileged_effect_mechanisms_present": True,
            "ordinary_public_usb_scsi_transport_demonstrated": False,
            "public_iscsi_transport_present": False,
            "public_usb_v4l_transport_present": False,
            "stock_external_entry_vector_demonstrated": False,
            "root_access_demonstrated": False,
            "persistence_demonstrated": False,
        },
        "boundaries": [
            "The vulnerable scsi_id and v4l_id output mechanisms remain exact binary findings.",
            "Disabled public transports and one suppressed USB geometry do not exclude every vendor/internal producer or malformed-enumeration failure.",
            "Platform IPU4 camera inputs are enabled, but attacker control and helper invocation from an external port are not established.",
            "No physical device, injected property, unit activation, root command, target write, or persistence is demonstrated.",
        ],
    }
    canonical = json.dumps(report, separators=(",", ":"), sort_keys=True).encode()
    report["canonical_sha256"] = sha256(canonical)
    return report


def write_exclusive(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel-config", type=Path, required=True)
    parser.add_argument("--rootfs", type=Path, required=True)
    parser.add_argument("--usb-control", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(args.kernel_config, args.rootfs, args.usb_control)
        rendered = json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        if args.output:
            write_exclusive(args.output, rendered)
        else:
            sys.stdout.buffer.write(rendered)
    except (AuditError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
