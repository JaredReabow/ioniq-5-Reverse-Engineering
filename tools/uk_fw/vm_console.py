#!/usr/bin/env python3.13
"""Boot the projection and hand its serial console to this terminal.

The vendor kernel has neither virtio nor 9p (no `virtio*` or `9p*` entries in
`modules.builtin`, no modules on disk), so there is no host<->guest filesystem
channel. The serial line is the only bidirectional path, which is why this is a
console rather than a file share: you type into the guest shell.

This wraps `vm_boot.run(..., interactive=True)`, which is the mode that performs
the SDHCI compatibility patch over the QEMU debug socket. That patch is required:
without it the guest stops at `Waiting for root device /dev/mmcblk0...` and never
reaches userspace, so a hand-rolled QEMU command line will not boot.

Usage:
    python3.13 tools/uk_fw/vm_console.py [--workspace work/vm/softbackend]
                                        [--memory 2048] [--display none|cocoa]

At the guest prompt, the short version of what to type:

    sh /run-chain23.sh >/tmp/chain.log 2>&1 &     # vendor compositor + apps
    sh /run-live.sh                               # report what came up
    /usr/bin/ivi-wm 2080                          # place a surface so it is drawn
    cd /tmp && timeout 25 /usr/libexec/weston-screenshooter
    echo 'click 960 400' > /tmp/weston-vm-input    # touch input

Quit with Ctrl-C, or Ctrl-A X (QEMU's own escape).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vm_boot as vb  # noqa: E402


BANNER = """
==================================================================
 projection console
==================================================================
  sh /run-chain23.sh >/tmp/chain.log 2>&1 &   start the vendor stack
  sh /run-live.sh                             what came up, and what to do
  pidof weston-headless                       the compositor (NOT `pidof weston`)
  /usr/bin/ivi-wm <id>                        place a surface so it is drawn
  echo 'click 960 400' > /tmp/weston-vm-input  touch input
  logs: /tmp/launcher-chain/{launcher,weston,dlt}.log
  quit: Ctrl-C
==================================================================
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Boot the projection with a live guest console.")
    ap.add_argument("--workspace", default="work/vm/softbackend")
    ap.add_argument("--memory", type=int, default=2048)
    ap.add_argument("--display", default="none", choices=("none", "cocoa"))
    ap.add_argument("--micom-serial", action="store_true",
                    help="also provide /dev/ttyS1 for the micom manager")
    args = ap.parse_args()

    print(BANNER, flush=True)
    rc = vb.run(Path(args.workspace), True, "", 0.0,
                interactive=True, display=args.display,
                memory_mib=args.memory, micom_serial=args.micom_serial)
    print("\nconsole closed (vc run status %s)" % rc, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
