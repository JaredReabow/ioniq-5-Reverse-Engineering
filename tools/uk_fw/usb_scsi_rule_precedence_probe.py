#!/usr/bin/env python3
"""Run a benign USB mass-storage udev rule-precedence control.

The offline probe attaches a fixed zero-filled read-only QEMU USB disk with an
empty USB serial. Exact recovered ``udevadm test`` evaluates one synthetic add
action for the already-enumerated block device. The probe contains no control
characters, second property, unit name, service request, daemon, kernel uevent,
shell payload, filesystem, or target write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

import vm_boot

SCHEMA = "ioniq-usb-scsi-rule-precedence/v1"
DISK_SIZE = 4 * 1024 * 1024
DISK_SHA256 = "bb9f8df61474d25e71fa00722318cd387396ca1736605e1248821cc0de3d3af8"
EXPECTED_WORKSPACE_SHA256 = {
    "bzImage": "85e0086202758117015437a5ce7b580d7d32484807d1953c3a16e571f65f3f59",
    "rootfs.img": "4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f",
    "manifest.bin": "d282155bfed37b20a7222bb3e9d21a7c8618eaab88f7644f5770f35bdd90ef2d",
    "seed_dev.bin": "a5112d84e63962066e1d2ad290e0a9f1f2e806c56df15b6a10681aa532ecd7ca",
    "seed_user.bin": "9706e118d96d4ac08ee34ff276330d01db646aeb5356cd88ea8ef05099f9c50c",
}
EXPECTED_GUEST_HASHES = {
    "/bin/udevadm": "b3d0274757f9ded9260f22a629da22e1e06ef0f6c750293b317e09810c93692b",
    "/lib/udev/scsi_id": "85aa83a73d44f19f6b60162a53ee896854b71e7882848819aad20c1ccf079b32",
    "/lib/udev/rules.d/60-persistent-storage.rules": "5757bc1da0b3e07ee1769faa266af7720b8eef21006212051a8720c02eab5a8e",
    "/lib/modules/4.1.27-abl/kernel/drivers/scsi/scsi_mod.ko": "c58b7b49ab2ab2abdf385396354d8bbb8d8500b87dc82fcd69d8e4aced01f977",
    "/lib/modules/4.1.27-abl/kernel/drivers/scsi/sd_mod.ko": "fd59150d72a3ccb560ad100c86248c9fe786c362e6343b7b69c4b67ff94c7b8c",
    "/lib/modules/4.1.27-abl/kernel/drivers/usb/host/ehci-hcd.ko": "68de820c111cb89cafeba41c36ce8a0ae4a636ba38d0e0f30ecc60d99ad6b181",
    "/lib/modules/4.1.27-abl/kernel/drivers/usb/host/ehci-pci.ko": "a4be9e3497eb097e8aca52c653c590a5369eb7e76e007c828b544d25fa492556",
    "/lib/modules/4.1.27-abl/kernel/drivers/usb/storage/usb-storage.ko": "1850dc68fd5ab3ae2289951099b8394a46c6fa0a83b12430c52e1faa619e8008",
}
BEGIN_MARKER = "USB_SCSI_RULE_PROBE_BEGIN"
COMPLETE_MARKER = "USB_SCSI_RULE_PROBE_COMPLETE"
MARKER_RE = re.compile(r"^USB_SCSI_RULE_[A-Z0-9_]+(?:=[A-Za-z0-9_.:-]+)?$")
EXPECTED_SEQUENCE = (
    BEGIN_MARKER,
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
    COMPLETE_MARKER,
)


def validate_output(output: Path, workspace: Path) -> Path:
    resolved = vm_boot.project_output(output)
    workspace = vm_boot.project_output(workspace)
    if resolved.is_relative_to(workspace) or workspace.is_relative_to(resolved):
        raise ValueError("output directory must not alias or contain the VM workspace")
    if resolved.exists():
        raise ValueError("output directory already exists")
    return resolved


def verify_exact_workspace(workspace: Path) -> dict[str, str]:
    vm_boot.verify_workspace(workspace)
    metadata = json.loads((workspace / "prepare.json").read_text())
    actual = metadata.get("sha256")
    if actual != EXPECTED_WORKSPACE_SHA256:
        raise ValueError("workspace artifacts do not match the approved recovered VM")
    return dict(actual)


def write_zero_disk(path: Path) -> str:
    digest = hashlib.sha256()
    block = bytes(64 * 1024)
    remaining = DISK_SIZE
    with path.open("xb") as output:
        while remaining:
            chunk = block[: min(len(block), remaining)]
            output.write(chunk)
            digest.update(chunk)
            remaining -= len(chunk)
    actual = digest.hexdigest()
    if actual != DISK_SHA256:
        raise RuntimeError("fixed zero-disk digest mismatch")
    return actual


def guest_script() -> str:
    hash_checks = "\n".join(
        f'''ACTUAL=$($BB sha256sum {path} | $BB cut -d' ' -f1)
[ "$ACTUAL" = "{digest}" ] || {{ probe_fail artifact_hash; return 1; }}'''
        for path, digest in EXPECTED_GUEST_HASHES.items()
    )
    return f'''export PATH=/bin:/sbin:/usr/bin:/usr/sbin
BB=/bin/busybox
probe_fail() {{
    echo "USB_SCSI_RULE_FAIL=$1"
    echo {COMPLETE_MARKER}
    return 1
}}
probe_main() {{
    echo {BEGIN_MARKER}
{hash_checks}
    echo USB_SCSI_RULE_ARTIFACTS=verified
    for module in scsi_mod sd_mod ehci-hcd ehci-pci usb-storage; do
        $BB modprobe "$module" >/dev/null 2>&1 || {{ probe_fail module_load; return 1; }}
    done
    echo USB_SCSI_RULE_MODULES=loaded
    $BB sleep 5
    TARGET=
    TARGET_COUNT=0
    for candidate in /sys/class/block/sd*; do
        [ -e "$candidate" ] || continue
        TARGET=$candidate
        TARGET_COUNT=$((TARGET_COUNT + 1))
    done
    [ "$TARGET_COUNT" -eq 1 ] || {{ probe_fail target_count; return 1; }}
    [ "$TARGET" = /sys/class/block/sda ] || {{ probe_fail target_name; return 1; }}
    echo USB_SCSI_RULE_TARGET=sda
    USB_DEVICE=
    USB_DEVICE_COUNT=0
    for candidate in /sys/bus/usb/devices/*; do
        [ -f "$candidate/idVendor" ] || continue
        [ -f "$candidate/idProduct" ] || continue
        [ "$($BB cat "$candidate/idVendor")" = 46f4 ] || continue
        [ "$($BB cat "$candidate/idProduct")" = 0001 ] || continue
        USB_DEVICE=$candidate
        USB_DEVICE_COUNT=$((USB_DEVICE_COUNT + 1))
    done
    [ "$USB_DEVICE_COUNT" -eq 1 ] || {{ probe_fail usb_device_count; return 1; }}
    if [ -e "$USB_DEVICE/serial" ] || [ -L "$USB_DEVICE/serial" ]; then
        probe_fail usb_serial_present
        return 1
    fi
    echo USB_SCSI_RULE_USB_SERIAL_ATTR=absent
    [ "$($BB cat /sys/class/block/sda/ro)" = 1 ] || {{ probe_fail block_writable; return 1; }}
    echo USB_SCSI_RULE_BLOCK_READONLY=1
    $BB mount -t tmpfs -o mode=0700,nosuid,nodev,noexec tmpfs /tmp || {{ probe_fail tmp_mount; return 1; }}
    $BB mount -o remount,ro / || {{ probe_fail root_remount; return 1; }}
    ROOT_FLAGS=$($BB awk '$2 == "/" {{ print $4; exit }}' /proc/mounts)
    echo "$ROOT_FLAGS" | $BB tr ',' '\n' | $BB grep -Fx ro >/dev/null || {{ probe_fail root_not_readonly; return 1; }}
    echo USB_SCSI_RULE_ROOT_READONLY=1
    LOG=/tmp/usb-scsi-rule.log
    /bin/udevadm test --action=add /sys/class/block/sda > "$LOG" 2>&1
    RC=$?
    echo USB_SCSI_RULE_UDEVADM_RC=$RC
    [ "$RC" -eq 0 ] || {{ probe_fail udevadm; return 1; }}
    if $BB grep -F "IMPORT builtin 'usb_id' /lib/udev/rules.d/60-persistent-storage.rules:31" "$LOG" >/dev/null; then
        echo USB_SCSI_RULE_USB_ID_IMPORT=present
    else
        echo USB_SCSI_RULE_USB_ID_IMPORT=absent
    fi
    ID_BUS=$($BB grep '^ID_BUS=' "$LOG" | $BB tail -n 1 | $BB cut -d= -f2-)
    ID_SERIAL=$($BB grep '^ID_SERIAL=' "$LOG" | $BB tail -n 1 | $BB cut -d= -f2-)
    echo USB_SCSI_RULE_ID_BUS=$ID_BUS
    echo USB_SCSI_RULE_ID_SERIAL=$ID_SERIAL
    if $BB grep '^ID_SERIAL_SHORT=' "$LOG" >/dev/null; then
        echo USB_SCSI_RULE_ID_SERIAL_SHORT=present
    else
        echo USB_SCSI_RULE_ID_SERIAL_SHORT=absent
    fi
    if $BB grep '^ID_SCSI_SERIAL=' "$LOG" >/dev/null; then
        echo USB_SCSI_RULE_ID_SCSI_SERIAL=present
    else
        echo USB_SCSI_RULE_ID_SCSI_SERIAL=absent
    fi
    if $BB grep -E "(^|[ /'])scsi_id([[:space:]']|$)" "$LOG" >/dev/null; then
        echo USB_SCSI_RULE_SCSI_ID_EXECUTION=present
    else
        echo USB_SCSI_RULE_SCSI_ID_EXECUTION=absent
    fi
    $BB rm -f "$LOG"
    echo {COMPLETE_MARKER}
}}
probe_main
'''


def probe_frame(serial: str) -> tuple[list[str], bool]:
    lines = serial.splitlines()
    starts = [index for index, line in enumerate(lines) if line == BEGIN_MARKER]
    ends = [index for index, line in enumerate(lines) if line == COMPLETE_MARKER]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        return [], False
    return lines[starts[0] : ends[0] + 1], True


def salient_lines(serial: str, limit: int = 80) -> list[str]:
    frame, _ = probe_frame(serial)
    return [line for line in frame if MARKER_RE.fullmatch(line)][:limit]


def classify(serial: str, result: dict[str, Any]) -> str:
    if result.get("timeout"):
        return "timeout"
    if result.get("error") or not result.get("userspace") or not result.get("root_mounted"):
        return "harness-error"
    frame, complete = probe_frame(serial)
    if not complete:
        return "harness-error"
    raw_markers = [line for line in serial.splitlines() if MARKER_RE.fullmatch(line)]
    markers = [line for line in frame if MARKER_RE.fullmatch(line)]
    if raw_markers != markers or any(line.startswith("USB_SCSI_RULE_FAIL=") for line in markers):
        return "harness-error"
    positions: list[int] = []
    for expected in EXPECTED_SEQUENCE:
        if markers.count(expected) != 1:
            return "unexpected-rule-result"
        positions.append(markers.index(expected))
    if positions != sorted(positions) or result.get("command_exit_code") != 0:
        return "harness-error"
    return "usb-id-suppresses-scsi-id"


def newest_run(workspace: Path, before: set[Path]) -> Path:
    runs = workspace / "runs"
    candidates = [path for path in runs.iterdir() if path.is_dir() and path not in before]
    if len(candidates) != 1:
        raise RuntimeError(f"expected one new VM run directory, got {len(candidates)}")
    return candidates[0]


def run_probe(
    workspace: Path, output: Path, timeout: float, memory_mib: int
) -> tuple[dict[str, Any], int]:
    workspace = vm_boot.project_output(workspace)
    workspace_hashes = verify_exact_workspace(workspace)
    output = validate_output(output, workspace)
    output.mkdir(parents=True)
    disk = output / "benign-zero-usb-disk.img"
    disk_hash = write_zero_disk(disk)
    runs = workspace / "runs"
    before = set(runs.iterdir()) if runs.exists() else set()
    extra_devices = [
        "ich9-usb-ehci1,id=ehci",
        "-drive",
        f"if=none,id=usbtest,format=raw,file={disk},snapshot=on,readonly=on",
        "usb-storage,bus=ehci.0,drive=usbtest,serial=",
    ]
    rc = vm_boot.run(
        workspace,
        True,
        guest_script(),
        timeout=timeout,
        memory_mib=memory_mib,
        extra_devices=extra_devices,
        serial_completion_marker=COMPLETE_MARKER,
    )
    run_dir = newest_run(workspace, before)
    result_path = run_dir / "result.json"
    result = json.loads(result_path.read_text()) if result_path.exists() else {}
    serial_path = run_dir / "serial.log"
    serial = serial_path.read_text(errors="replace") if serial_path.exists() else ""
    report = {
        "schema": SCHEMA,
        "scope": "benign USB mass-storage rule-precedence control",
        "network": "disabled by vm_boot (-nic none)",
        "workspace": str(workspace.relative_to(vm_boot.PROJECT)),
        "run_directory": str(run_dir.relative_to(vm_boot.PROJECT)),
        "workspace_artifacts": workspace_hashes,
        "guest_artifacts": EXPECTED_GUEST_HASHES,
        "attached_disk": {
            "path": str(disk.relative_to(vm_boot.PROJECT)),
            "bytes": DISK_SIZE,
            "sha256": disk_hash,
            "content": "all zero bytes; no partition table or filesystem",
            "qemu_access": "snapshot=on,readonly=on",
            "usb_serial": "explicitly empty",
        },
        "classification": classify(serial, result),
        "vm_return_code": rc,
        "vm_result": result,
        "salient_lines": salient_lines(serial),
        "conclusion": (
            "For this ordinary empty-serial USB mass-storage geometry, exact recovered "
            "usb_id sets ID_SERIAL before the conditional scsi_id rule, so scsi_id is skipped."
        ),
        "limitations": [
            "The control does not prove behavior for malformed USB enumeration, non-USB SCSI, SCSI tape, or CCISS transports.",
            "The QEMU EHCI topology does not prove which owner-unit physical ports expose USB host mode.",
            "No control characters, injected property, service request, root transition, or persistence were attempted.",
            "The exact vulnerable scsi_id output path remains present; this result narrows only ordinary USB mass-storage reachability.",
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    (output / "usb-scsi-rule-precedence.json").write_text(rendered)
    return report, rc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--memory-mib", type=int, default=1024)
    args = parser.parse_args(argv)
    if not 30 <= args.timeout <= 300:
        parser.error("--timeout must be between 30 and 300 seconds")
    if not 256 <= args.memory_mib <= 8192:
        parser.error("--memory-mib must be between 256 and 8192")
    try:
        report, _ = run_probe(args.workspace, args.output, args.timeout, args.memory_mib)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["classification"] == "usb-id-suppresses-scsi-id" else 1


if __name__ == "__main__":
    raise SystemExit(main())
