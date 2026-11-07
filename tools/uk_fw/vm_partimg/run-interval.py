#!/usr/bin/env python3.13
"""run-interval.py - boot the interval run on a CoW clone with two evidence channels.

This is the wrapper for the controlled run specified in docs/vm/59-controlled-run-spec.md. It is
TRACKED, and so are the driver and helper it launches, because boot58's fatal flaw was an unretained
driver (docs/kernel/42).

Two channels, physically separate:

    /dev/ttyS2  -> interval-export.txt   the frozen helper's receipt and payload (narrow claim only)
    /dev/ttyS3  -> interval-runtime.txt  the driver's generation, sampling and persistence record

They are separate on purpose. A shared channel would place the driver's own terminal OUTCOME line
inside the helper's receipt transaction, and the verifier requires exactly one terminal outcome - so
sharing would make every run read as RECEIPT_INCOMPLETE.

The init script must already be staged into the workspace image as /init-interval-run.sh, together with
/interval-run.sh, /interval-capture.sh and /interval-manifest.txt. Stage them with
tools/uk_fw/vm_partimg/stage-interval.py.

Usage:
    python3.13 tools/uk_fw/vm_partimg/run-interval.py --timeout 900
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT / "tools/uk_fw"))
import vm_boot as vb  # noqa: E402

# A CoW clone, never the base workspace. Created with `cp -c` (APFS clonefile).
WS = (PROJECT / "work/vm/kbuild/ws-run61").resolve()
ACTIVE_ROOT = "/dev/mmcblk0p5"
INIT = "/init-interval-run.sh"

vb.KERNEL_SHA256 = hashlib.file_digest((WS / "bzImage").open("rb"), "sha256").hexdigest()
vb.INIT_CHOICES = ("/init", "/lib/systemd/esinit", "/lib/systemd/systemd", INIT)

_orig_qemu_command = vb.qemu_command

SMP = "4"
EXPORT_CHANNEL = "interval-export.txt"
RUNTIME_CHANNEL = "interval-runtime.txt"


def qemu_command(*args, **kwargs):  # type: ignore[no-untyped-def]
    argv = _orig_qemu_command(*args, **kwargs)

    i = argv.index("-append")
    # GPT image: the root must be the active-root partition, not the whole device.
    argv[i + 1] = argv[i + 1].replace("root=/dev/mmcblk0 ", f"root={ACTIVE_ROOT} ", 1)

    j = argv.index("-smp")
    argv[j + 1] = SMP

    # The compositor needs the 1920x720 mode the vendor launcher expects. The stock harness emits a
    # plain VGA device, so add the EDID hint that produced the correct mode in earlier runs.
    for k, token in enumerate(argv):
        if token.startswith("VGA,id=display0"):
            argv[k] = "VGA,id=display0,addr=01.0,edid=on,xres=1920,yres=720"
            break

    # Two file-backed serial channels. ttyS0 stays on stdio (serial.log); ttyS1 is left unused
    # because the micom boundary may claim it; the evidence channels are ttyS2 and ttyS3.
    argv += [
        # index=2 is ttyS2, which the vendor image gives a getty; index=3 is ttyS3, which showed no
        # getty in run 1794055821491663000. The pristine channel carries the export transaction.
        "-chardev", f"file,id=run,path={RUNTIME_CHANNEL}",
        "-device", "isa-serial,chardev=run,index=2",
        "-chardev", f"file,id=exp,path={EXPORT_CHANNEL}",
        "-device", "isa-serial,chardev=exp,index=3",
    ]
    return argv


vb.qemu_command = qemu_command

# The driver reports to ttyS3 and hands the helper ttyS2. Nothing in the guest writes serial output
# directly, so the diagnostic command string is only a liveness marker.
# vm_boot only sends the command once it sees this exact line, and only then sets userspace=True.
# Omitting it made the first attempt stall and report userspace=false (run 1794055821491663000).
DIAG_CMD = (
    "echo IONIQ_VM_USERSPACE_READY; "
    "cat /proc/uptime; "
    "ls -l /interval-run.sh /interval-capture.sh /interval-manifest.txt 2>/dev/null"
)


def main() -> int:
    # `global` must precede the first read of SMP, which happens in the --smp default below.
    global SMP
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--memory-mib", type=int, default=2048)
    ap.add_argument("--cmd", default=DIAG_CMD)
    ap.add_argument("--interactive", action="store_true")
    ap.add_argument("--smp", default=SMP)
    # The SDHCI compat patch is applied over a gdb RSP connection BEFORE the guest runs, and vm_boot
    # caps that connection at 30 s. In run 1794056122069443000 the patch never completed (no
    # patch.json) and qemu was killed at 30.28 s, yet the guest had already mounted mmcblk0p16 and
    # reached systemd - which is evidence the patch may no longer be required for this image. Left
    # selectable so the choice is explicit and recorded rather than silently assumed.
    ap.add_argument("--compat", dest="compat", action="store_true", default=True)
    ap.add_argument("--no-compat", dest="compat", action="store_false")
    args = ap.parse_args()

    SMP = str(args.smp)

    if not (WS / "rootfs.img").is_file():
        print(f"error: cloned workspace missing rootfs.img: {WS}", file=sys.stderr)
        return 2
    if not (WS / "partimg-build" / "p5.img").is_file():
        print(f"error: cloned workspace missing partimg-build/p5.img: {WS}", file=sys.stderr)
        return 2

    return vb.run(
        WS,
        args.compat,
        args.cmd,
        timeout=args.timeout,
        interactive=args.interactive,
        memory_mib=args.memory_mib,
        init=INIT,
    )


if __name__ == "__main__":
    sys.exit(main())
