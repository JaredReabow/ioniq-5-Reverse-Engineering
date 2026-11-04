#!/usr/bin/env python3.13
"""Boot the stockhmi projection (work/vm/byhand) on the authentic esinit path.

Same harness overrides as run-esinit-spi.py (vendor kernel hash, `root=` token
moved to the active-root partition p5), plus the authentic-HMI init wrapper
`/init-authentic-hmi.sh` which forces the MICOM SPI gate and then execs
/lib/systemd/esinit.  See docs/vm/authentic-hmi.md.

Usage:
    python3.13 tools/uk_fw/vm_partimg/run-stockhmi.py --init /init-authentic-hmi.sh --timeout 240
    python3.13 tools/uk_fw/vm_partimg/run-stockhmi.py --init /init --timeout 120 --cmd '...'
"""
from __future__ import annotations
import argparse
import hashlib
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT / "tools/uk_fw"))
import vm_boot as vb  # noqa: E402

WS = (PROJECT / "work/vm/byhand").resolve()
ACTIVE_ROOT = "/dev/mmcblk0p5"

vb.KERNEL_SHA256 = hashlib.file_digest((WS / "bzImage").open("rb"), "sha256").hexdigest()
vb.INIT_CHOICES = ("/init", "/lib/systemd/esinit", "/lib/systemd/systemd",
                    "/init-esinit-spi.sh", "/init-authentic-hmi.sh")

_orig_qemu_command = vb.qemu_command

SMP = "2"


def qemu_command(*args, **kwargs):
    argv = _orig_qemu_command(*args, **kwargs)
    i = argv.index("-append")
    # GPT image: root must be the active-root partition, not the whole device.
    argv[i + 1] = argv[i + 1].replace(
        "root=/dev/mmcblk0 ", f"root={ACTIVE_ROOT} ", 1)
    # Research-only CPU headroom: the vendor kernel + TCG run the HMI app stack
    # under software GL; more vCPUs let AppHomeScreen's main thread reach its
    # event loop. Overridden here (not in vm_boot) so the shared harness keeps
    # its -smp 2 default.
    j = argv.index("-smp")
    argv[j + 1] = SMP
    # lossless probe channel: a second serial port whose output lands in a host file,
    # because many small writes to the console get dropped while systemd spins.
    if "-serial" in argv:      # note: the flag is "-serial", not "--serial"
        argv += ["-chardev", "file,id=dbg,path=dbg-out.txt",
                 "-device", "isa-serial,chardev=dbg,index=2"]
    return argv


vb.qemu_command = qemu_command

DIAG_CMD = (
    "echo ===spi===; cat /sys/module/micom/parameters/spi_validation 2>/dev/null; "
    "ls -l /tmp/spi_validation_* 2>/dev/null; "
    "echo ===weston===; ps | grep -i weston | grep -v grep; "
    "ls -l /run/user/root/wayland-* 2>/dev/null; "
    "echo ===ini===; readlink -f /tmp/weston.ini 2>/dev/null; "
    "cat /etc/xdg/weston/weston_1920.ini 2>/dev/null | head -5; "
    "echo ===wrap===; cat /tmp/weston-wrap.log 2>/dev/null; "
    "echo ===auth===; cat /tmp/auth-hmi/shot.log 2>/dev/null; "
    "echo ===partitions===; cat /proc/partitions"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", default="/init-authentic-hmi.sh",
                    choices=vb.INIT_CHOICES)
    ap.add_argument("--timeout", type=float, default=240.0)
    ap.add_argument("--memory-mib", type=int, default=2048)
    ap.add_argument("--cmd", default=DIAG_CMD)
    ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--smp", default="2", help="vCPU count passed to qemu -smp")
    args = ap.parse_args()
    global SMP
    SMP = str(args.smp)
    return vb.run(WS, True, args.cmd, timeout=args.timeout,
                  interactive=args.interactive, memory_mib=args.memory_mib,
                  init=args.init)


if __name__ == "__main__":
    sys.exit(main())
