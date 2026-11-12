#!/usr/bin/env python3
"""Generate independent USB serial and local-terminal owner access channels.

The CDC-ACM channel is restricted to one caller-supplied USB VID:PID and
revalidates that identity from sysfs before starting a root getty. The local
terminal channel starts the stock Weston terminal after a USB-backed keyboard
input event. Neither service depends on Ethernet, Wi-Fi, SSH, or the other
service. The generator stages files and never writes to hardware.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

_BASE = "opt/ioniq-owner"
_VERSION = "1.1.0"
_CDC_ID_RE = re.compile(r"[0-9A-Fa-f]{4}:[0-9A-Fa-f]{4}")
_SERIAL_RULE = "etc/udev/rules.d/71-ioniq-owner-cdc-acm.rules"
_KEYBOARD_RULE = "etc/udev/rules.d/72-ioniq-owner-keyboard-terminal.rules"
_SERIAL_UNIT = "etc/systemd/system/ioniq-owner-serial-getty@.service"
_KEYBOARD_UNIT = "etc/systemd/system/ioniq-owner-keyboard-terminal.service"

_SERIAL_RULE_TEMPLATE = '''# Exact CDC-ACM identity; never admit an unrelated ttyACM device.
ACTION=="add", SUBSYSTEM=="tty", KERNEL=="ttyACM[0-9]*", SUBSYSTEMS=="usb", ATTRS{{idVendor}}=="{vendor}", ATTRS{{idProduct}}=="{product}", SYMLINK+="ioniq-owner-serial", TAG+="systemd", ENV{{SYSTEMD_WANTS}}+="ioniq-owner-serial-getty@%k.service"
'''

_KEYBOARD_RULE_CONTENT = '''# Exact input class: a USB-backed keyboard, not a touchscreen or generic event node.
ACTION=="add", SUBSYSTEM=="input", KERNEL=="event[0-9]*", SUBSYSTEMS=="usb", ENV{ID_INPUT_KEYBOARD}=="1", TAG+="systemd", ENV{SYSTEMD_WANTS}+="ioniq-owner-keyboard-terminal.service"
'''

_SERIAL_START = r'''#!/bin/sh
# Revalidate the udev-admitted CDC-ACM identity before granting root access.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077
sysroot=/sys

if [ "$#" -ne 1 ]; then
    echo 'Owner serial rejected: expected exactly one tty name'
    exit 2
fi

tty=$1
case "$tty" in
    ttyACM[0-9]*) ;;
    *)
        echo "Owner serial ignored: $tty is not a CDC-ACM tty"
        exit 0
        ;;
esac
case "${tty#ttyACM}" in
    ''|*[!0-9]*)
        echo "Owner serial ignored: malformed tty name $tty"
        exit 0
        ;;
esac

for command in readlink cat; do
    command -v "$command" >/dev/null 2>&1 || exit 1
done

device_link="$sysroot/class/tty/$tty/device"
if [ ! -e "$device_link" ]; then
    echo "Owner serial ignored: $tty has no sysfs device"
    exit 0
fi
device=$(readlink -f "$device_link" 2>/dev/null) || {
    echo "Owner serial ignored: cannot resolve $tty"
    exit 0
}
case "$device" in
    "$sysroot"/devices/*) ;;
    *)
        echo "Owner serial ignored: $tty resolves outside the device tree"
        exit 0
        ;;
esac

parent=$device
identity=
while [ "$parent" != "$sysroot/devices" ] && [ "$parent" != / ]; do
    case "$parent" in
        "$sysroot"/devices/*) ;;
        *) break ;;
    esac
    if [ -r "$parent/idVendor" ] && [ -r "$parent/idProduct" ]; then
        vendor=$(cat "$parent/idVendor")
        product=$(cat "$parent/idProduct")
        identity="$vendor:$product"
        break
    fi
    parent=${parent%/*}
done

case "$identity" in
    @CDC_ACM_ID@) ;;
    *)
        echo "Owner serial ignored: $tty identity is '$identity', not the configured CDC-ACM device"
        exit 0
        ;;
esac

if [ ! -c "/dev/$tty" ]; then
    echo "Owner serial ignored: /dev/$tty is not a character device"
    exit 0
fi

printf 'IONIQ5_OWNER_CONSOLE_VERSION=@VERSION@ serial tty=%s id=%s\n' "$tty" "$identity"
exec /sbin/agetty --autologin root --noclear --keep-baud \
    115200,38400,9600 "$tty" vt100
'''

_KEYBOARD_START = r'''#!/bin/sh
# This path deliberately has no dependency on SSH, Ethernet, or Wi-Fi.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077
runtime_dir=/var/run/user/root
terminal=/usr/bin/weston-terminal

if [ -L "$runtime_dir" ]; then
    echo "Owner terminal rejected: runtime path is a symlink: $runtime_dir"
    exit 1
fi
if [ -e "$runtime_dir" ] && [ ! -d "$runtime_dir" ]; then
    echo "Owner terminal rejected: runtime path is not a directory: $runtime_dir"
    exit 1
fi
if [ ! -d "$runtime_dir" ]; then
    mkdir -p "$runtime_dir"
    chmod 700 "$runtime_dir"
fi
metadata=$(stat -c '%u:%g:%a' "$runtime_dir") || exit 1
if [ "$metadata" != '0:0:700' ]; then
    echo "Owner terminal rejected: unsafe runtime metadata $metadata at $runtime_dir"
    exit 1
fi

if [ -L "$terminal" ] || [ ! -f "$terminal" ] || [ ! -x "$terminal" ]; then
    echo "Owner terminal rejected: stock Weston terminal is unavailable"
    exit 1
fi

export XDG_RUNTIME_DIR="$runtime_dir"
printf 'IONIQ5_OWNER_CONSOLE_VERSION=@VERSION@ local-terminal keyboard-usb\n'
exec "$terminal" --shell=/bin/sh
'''

_SERIAL_UNIT_CONTENT = '''[Unit]
Description=IONIQ5 exact CDC-ACM root recovery getty @VERSION@
BindsTo=dev-%i.device
After=dev-%i.device local-fs.target
ConditionPathExists=/dev/%I
StartLimitIntervalSec=30
StartLimitBurst=3

[Service]
Type=simple
User=root
UMask=0077
ExecStart=/opt/ioniq-owner/bin/start-owner-serial %I
Restart=on-failure
RestartSec=2s
TimeoutStopSec=10s
KillMode=control-group
TTYPath=/dev/%I
TTYReset=yes
TTYVHangup=yes
TTYVTDisallocate=no
'''

_KEYBOARD_UNIT_CONTENT = '''[Unit]
Description=IONIQ5 USB-keyboard Weston terminal @VERSION@
ConditionPathExists=/usr/bin/weston-terminal
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=simple
User=root
UMask=0077
Environment=XDG_RUNTIME_DIR=/var/run/user/root
ExecStart=/opt/ioniq-owner/bin/start-owner-keyboard-terminal
Restart=on-failure
RestartSec=2s
TimeoutStopSec=5s
KillMode=control-group
'''


def _cdc_acm_id(value: object) -> str:
    """Validate and normalize one explicit `VID:PID`; there is no default."""
    if not isinstance(value, str) or _CDC_ID_RE.fullmatch(value) is None:
        raise ValueError("cdc_acm_id must be exactly four hex digits, a colon, and four hex digits")
    return value.lower()


def _manifest(cdc_acm_id: str | None, files: dict[str, tuple[bytes, int]]) -> dict:
    """Build the deterministic manifest fragment for an owner-console overlay."""
    return {
        "format": 1,
        "fragment": True,
        "module": "owner-console",
        "version": _VERSION,
        "archive_ownership": {"uid": 0, "gid": 0},
        "cdc_acm_id": cdc_acm_id,
        "channels": {
            "serial": {
                "enabled": cdc_acm_id is not None,
                "trigger": "udev exact ttyACM USB VID:PID",
                "service": "ioniq-owner-serial-getty@.service",
                "autologin_user": "root",
                "network_dependency": False,
            },
            "local_terminal": {
                "trigger": "udev USB-backed ID_INPUT_KEYBOARD event",
                "service": "ioniq-owner-keyboard-terminal.service",
                "program": "/usr/bin/weston-terminal --shell=/bin/sh",
                "xdg_runtime_dir": "/var/run/user/root",
                "network_dependency": False,
            },
        },
        "files": {
            name: {
                "sha256": hashlib.sha256(data).hexdigest(),
                "mode": oct(mode),
                "uid": 0,
                "gid": 0,
            }
            for name, (data, mode) in sorted(files.items())
        },
        "symlinks": {},
        "limitations": [
            "CDC-ACM serial hardware and the configured VID:PID require head-unit enumeration and login verification.",
            "The serial getty relies on the recovered CONFIG_USB_ACM=m, cdc-acm.ko, and /sbin/agetty; FTDI, CH341, CP210X, and PL2303 are not provided.",
            "Weston IVI surface visibility, keyboard focus and input, and clean return to the OEM UI require target/product verification.",
            "Touch-only local-terminal entry is not provided; the local trigger requires a USB-backed keyboard input device.",
            "Archive every overlay member as root:root; host staging ownership is not target ownership.",
        ],
        "excluded": [
            "Radxa CDC-ECM transport",
            "target-side USB gadget/UCD role",
            "SSH, Ethernet, Wi-Fi, routing, and bridging",
            "OEM compositor edits and boot-image changes",
            "vehicle-control code and hardware action",
        ],
    }


def ioniq5_owner_console_generate(*, cdc_acm_id: str | None = None, output: Path) -> dict:
    """Stage the exact-ID serial and local-terminal overlay plus manifest.

    `cdc_acm_id`, when supplied, must be the owner device's explicit USB
    VID:PID. If absent, only the keyboard terminal is activated. The dormant
    serial launcher can never admit a device until a matching rule is installed.
    The output parent must exist. Existing output and manifest paths,
    including dangling symlinks, are rejected. This function never executes the
    generated scripts and never writes to the target or attached hardware.
    """
    selected_id = _cdc_acm_id(cdc_acm_id) if cdc_acm_id is not None else None
    output = Path(output)
    if ".." in output.parts or output.name in ("", ".", ".."):
        raise ValueError("unsafe output path")
    output = output.parent.resolve(strict=True) / output.name
    manifest_path = output.with_name(output.name + ".manifest.json")
    if os.path.lexists(output) or os.path.lexists(manifest_path):
        raise ValueError("output or sibling manifest already exists")

    if selected_id:
        vendor, product = selected_id.split(":", 1)
        serial_rule = _SERIAL_RULE_TEMPLATE.format(vendor=vendor, product=product)
    else:
        serial_rule = "# Serial recovery inactive: no owner CDC-ACM bridge configured.\n"
    serial_start = (
        _SERIAL_START
        .replace("@CDC_ACM_ID@", selected_id or "UNCONFIGURED")
        .replace("@VERSION@", _VERSION)
    )
    keyboard_start = _KEYBOARD_START.replace("@VERSION@", _VERSION)
    serial_unit = _SERIAL_UNIT_CONTENT.replace("@VERSION@", _VERSION)
    keyboard_unit = _KEYBOARD_UNIT_CONTENT.replace("@VERSION@", _VERSION)
    files = {
        f"{_BASE}/bin/start-owner-serial": (serial_start.encode("ascii"), 0o755),
        f"{_BASE}/bin/start-owner-keyboard-terminal": (
            keyboard_start.encode("ascii"), 0o755),
        _SERIAL_RULE: (serial_rule.encode("ascii"), 0o644),
        _KEYBOARD_RULE: (_KEYBOARD_RULE_CONTENT.encode("ascii"), 0o644),
        _SERIAL_UNIT: (serial_unit.encode("ascii"), 0o644),
        _KEYBOARD_UNIT: (keyboard_unit.encode("ascii"), 0o644),
    }
    if selected_id is None:
        # The selected authentication-recovery build has no TTL/serial path.
        # Preserve its generator source for prior research, but ship none of it.
        for name in (f"{_BASE}/bin/start-owner-serial", _SERIAL_RULE, _SERIAL_UNIT):
            files.pop(name)
    manifest = _manifest(selected_id, files)

    staging = Path(tempfile.mkdtemp(prefix=".ioniq-owner-console-", dir=output.parent))
    manifest_created = False
    output_created = False
    try:
        for name, (data, mode) in sorted(files.items()):
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(mode)
        for directory in sorted(
            (path for path in staging.rglob("*") if path.is_dir()),
            reverse=True,
        ):
            directory.chmod(0o755)
        staging.chmod(0o700)

        fd = os.open(manifest_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        manifest_created = True
        with os.fdopen(fd, "w") as stream:
            stream.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        output.mkdir(mode=0o700)
        output_created = True
        staging.rename(output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        if output_created:
            try:
                output.rmdir()
            except OSError:
                pass
        if manifest_created:
            try:
                manifest_path.unlink()
            except OSError:
                pass
        raise
    return manifest


def ioniq5_owner_console_main(argv: list[str] | None = None) -> int:
    """Generate the independent console overlay from an explicit CDC-ACM ID."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cdc-acm-id", help="exact USB VID:PID; omit to leave serial inactive")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        ioniq5_owner_console_generate(
            cdc_acm_id=args.cdc_acm_id,
            output=args.output,
        )
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(2, f"overlay rejected: {exc}\n")
    print(f"Created overlay: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(ioniq5_owner_console_main())
