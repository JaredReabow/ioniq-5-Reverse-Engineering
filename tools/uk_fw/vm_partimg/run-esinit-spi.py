#!/usr/bin/env python3.13
"""Boot the partitioned projection with the MICOM SPI gate reported as OK.

esinit refuses to launch the vendor display server while `/tmp/spi_validation_NOK` exists:

    spi_validation="$(cat /sys/module/micom/parameters/spi_validation)"
    if [ "$spi_validation" = "1" ]; then touch /tmp/spi_validation_OK; rm /tmp/spi_validation_NOK ...
    ...
    if [ -e /tmp/spi_validation_NOK ]; then echo "SPI NOK"; else (/usr/bin/weston --tty=1 ...) & fi

`spi_validation` is a micom module parameter, so it can be supplied on the kernel command line before
esinit runs.  This runner adds `micom.spi_validation=1` to the append line so the authentic OK branch
is taken and the real display server is started, on top of the two documented changes in
run-esinit.py (vendor kernel hash, `root=` token to the active-root partition p5).

Original docstring follows.

Boot the GPT-partitioned eMMC projection (work/vm/partimg) with the vendor
kernel, the SDHCI compatibility patch, and the active-root partition p5.

The harness hard-codes `root=/dev/mmcblk0` (whole device).  This image is a
real GPT disk, so the root must be the active-root partition.  Rather than edit
vm_boot.py, we override the module's `qemu_command` to rewrite that one append
token to `root=/dev/mmcblk0p5`; the change is recorded in prepare.json and
docs/vm/partitioned-image.md.

Usage:
    python3.13 tools/uk_fw/vm_partimg/run-esinit-spi.py --init /lib/systemd/esinit --timeout 300
    python3.13 tools/uk_fw/vm_partimg/run-esinit-spi.py --init /init --timeout 120 \
        --cmd 'cat /proc/partitions; mount -t ext4 /dev/mmcblk0p11 /mnt && echo P11_OK'
"""
from __future__ import annotations
import argparse
import hashlib
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT / "tools/uk_fw"))
import vm_boot as vb  # noqa: E402

WS = (PROJECT / "work/vm/partimg").resolve()
ACTIVE_ROOT = "/dev/mmcblk0p5"

vb.KERNEL_SHA256 = hashlib.file_digest((WS / "bzImage").open("rb"), "sha256").hexdigest()
vb.INIT_CHOICES = ("/init", "/lib/systemd/esinit", "/lib/systemd/systemd")

_orig_qemu_command = vb.qemu_command


def qemu_command(*args, **kwargs):
    argv = _orig_qemu_command(*args, **kwargs)
    i = argv.index("-append")
    # Root is the whole device in the stock harness; this image is GPT so the
    # root must be the active-root partition.  One documented, token-scoped edit.
    argv[i + 1] = argv[i + 1].replace(
        "root=/dev/mmcblk0 ", f"root={ACTIVE_ROOT} ", 1)
    # Report the MICOM SPI handshake as complete so esinit takes its OK branch and
    # starts /usr/bin/weston.  Second documented append change.
    argv[i + 1] += " micom.spi_validation=1"
    return argv


vb.qemu_command = qemu_command

DIAG_CMD = (
    "echo ===spi===; cat /sys/module/micom/parameters/spi_validation; "
    "ls -l /tmp/spi_validation_* 2>/dev/null; "
    "echo ===weston===; pidof weston; ls -l /tmp/weston.crash 2>/dev/null; "
    "echo ===hmi===; pidof AppLauncher AppHomeScreen keeper; "
    "echo ===log===; dmesg | grep -iE 'weston|SPI|ias' | tail -12; "
    "echo ===tail===; tail -12 /log_data/kernel/*.dlt 2>/dev/null | cut -c1-140; "
    "echo ===partitions===; cat /proc/partitions; "
    "echo ===mounts===; cat /proc/mounts; "
    "mkdir -p /tmp/mnt; "
    "for p in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17; do "
    "mount -t ext4 /dev/mmcblk0p$p /tmp/mnt 2>/dev/null && echo P${p}_OK; umount /tmp/mnt 2>/dev/null; "
    "done"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", default="/lib/systemd/esinit",
                    choices=vb.INIT_CHOICES)
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--memory-mib", type=int, default=2048)
    ap.add_argument("--cmd", default=DIAG_CMD)
    ap.add_argument("--interactive", action="store_true")
    args = ap.parse_args()
    return vb.run(WS, True, args.cmd, timeout=args.timeout,
                  interactive=args.interactive, memory_mib=args.memory_mib,
                  init=args.init)


if __name__ == "__main__":
    sys.exit(main())
