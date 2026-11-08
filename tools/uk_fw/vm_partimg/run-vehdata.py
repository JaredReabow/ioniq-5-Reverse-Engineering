#!/usr/bin/env python3.13
"""Boot the gesture projection (work/vm/vehdata) on the authentic esinit path.

A CoW clone of work/vm/stockui for the stock engineering-mode tap-gesture
experiment (docs/vm/stock-gesture-in-vm.md).  Same harness overrides as
run-stockui.py, plus a lossless PNG channel: a second serial port (ttyS2)
whose output lands in a host file out.b64 in the run directory, because many
small writes to the console get dropped while systemd spins.

Usage:
    python3.13 tools/uk_fw/vm_partimg/run-gesture.py --init /init-authentic-hmi.sh --smp 4 --timeout 900
"""
from __future__ import annotations
import argparse
import hashlib
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT / "tools/uk_fw"))
import vm_boot as vb  # noqa: E402

WS = (PROJECT / "work/vm/vehdata").resolve()
ACTIVE_ROOT = "/dev/mmcblk0p5"

vb.KERNEL_SHA256 = hashlib.file_digest((WS / "bzImage").open("rb"), "sha256").hexdigest()
vb.INIT_CHOICES = ("/init", "/lib/systemd/esinit", "/lib/systemd/systemd",
                    "/init-esinit-spi.sh", "/init-authentic-hmi.sh")

_orig_qemu_command = vb.qemu_command

SMP = "4"
AUDIT_OFF = False


def qemu_command(*args, **kwargs):
    argv = _orig_qemu_command(*args, **kwargs)
    i = argv.index("-append")
    # GPT image: root must be the active-root partition, not the whole device.
    argv[i + 1] = argv[i + 1].replace(
        "root=/dev/mmcblk0 ", f"root={ACTIVE_ROOT} ", 1)
    if AUDIT_OFF:
        argv[i + 1] += " audit=0"
    j = argv.index("-smp")
    argv[j + 1] = SMP
    # lossless PNG channel: a third serial port (ttyS2) whose output lands in a
    # host file out.b64 in the run directory (the chardev path is relative to
    # the run cwd).  The console (ttyS0) drops small writes while systemd spins.
    if "-serial" in argv:      # note: vm_boot emits "-serial", one dash
        argv += ["-chardev", "file,id=dbg,path=out.b64",
                 "-device", "isa-serial,chardev=dbg,index=2"]
    return argv


vb.qemu_command = qemu_command

DIAG_CMD = (
    "echo ===spi===; cat /sys/module/micom/parameters/spi_validation 2>/dev/null; "
    "ls -l /tmp/spi_validation_* 2>/dev/null; "
    "echo ===weston===; ps | grep -i weston | grep -v grep; "
    "ls -l /run/user/root/wayland-* 2>/dev/null; "
    "echo ===partitions===; cat /proc/partitions"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", default="/init-authentic-hmi.sh",
                    choices=vb.INIT_CHOICES)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--memory-mib", type=int, default=2048)
    ap.add_argument("--cmd", default=DIAG_CMD)
    ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--smp", default="4", help="vCPU count passed to qemu -smp")
    ap.add_argument("--audit-off", action="store_true",
                    help="append audit=0 to the kernel command line")
    args = ap.parse_args()
    global SMP, AUDIT_OFF
    SMP = str(args.smp)
    AUDIT_OFF = bool(args.audit_off)
    return vb.run(WS, True, args.cmd, timeout=args.timeout,
                  interactive=args.interactive, memory_mib=args.memory_mib,
                  init=args.init)


if __name__ == "__main__":
    sys.exit(main())
