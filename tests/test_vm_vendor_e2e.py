"""End-to-end test: boot the recovered vendor userspace and drive its HMI chain.

`tools/uk_fw/vendor_rootfs.py prepare` assembles the vendor root with our research
init; this test boots that workspace in QEMU and asserts the chain from the host:
the vendor dynamic loader resolves against the recovered libraries, D-Bus comes
up, weston creates the Wayland socket, the observer's commit wrapper is the
definition the guest's linker actually resolves, and AppLauncher starts.

Skipped, never failed, when the workspace or QEMU is absent: the vendor trees are
local, ignored artifacts.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

PROJECT = Path(__file__).parents[1]
TOOL = PROJECT / "tools/uk_fw/vendor_rootfs.py"
BOOT_TOOL = PROJECT / "tools/uk_fw/vm_boot.py"
SPEC = importlib.util.spec_from_file_location("vm_boot_vendor_e2e", BOOT_TOOL)
VM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VM)

WORKSPACE = Path(os.environ.get("IONIQ_VM_VENDOR_WORKSPACE", "")
                 or PROJECT / "work/vm/vendor-userspace-260128")
COMMAND = "/opt/vm/vendor-chain.sh"
BOOT_TIMEOUT = 600
RUN_TIMEOUT = BOOT_TIMEOUT + 300


def resolved_qemu() -> str | None:
    try:
        return VM.find_qemu()
    except ValueError:
        return None


def workspace_ready() -> bool:
    if not (WORKSPACE / "prepare.json").is_file():
        return False
    return all((WORKSPACE / name).is_file() for name in VM.ARTIFACTS)


REASON = ("the vendor userspace workspace and QEMU are required for the vendor "
          "end-to-end test; run tools/uk_fw/vendor_rootfs.py prepare first")


@unittest.skipUnless(resolved_qemu() and workspace_ready(), REASON)
class VendorEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = subprocess.run(
            [sys.executable, str(TOOL), "run", "--workspace", str(WORKSPACE),
             "--cmd", COMMAND, "--timeout", str(BOOT_TIMEOUT)],
            cwd=PROJECT, capture_output=True, text=True, timeout=RUN_TIMEOUT,
        )
        matched = re.search(r"^Run artifacts: (.+)$", cls.result.stdout, re.M)
        cls.runs = Path(matched[1].strip()) if matched else None
        cls.serial = ""
        if cls.runs and (cls.runs / "serial.log").is_file():
            cls.serial = (cls.runs / "serial.log").read_text(
                encoding="utf-8", errors="replace").replace("\r", "")

    def test_vendor_init_reaches_a_root_shell(self):
        self.assertIsNotNone(self.runs, self.result.stdout[-2000:] + self.result.stderr[-2000:])
        self.assertIn("IONIQ_VM_USERSPACE_READY", self.serial)
        self.assertIn("IONIQ_VM_VENDOR_READY", self.serial)
        self.assertIn("VFS: Mounted root (ext4 filesystem)", self.serial)

    def test_vendor_dynamic_loader_runs_recovered_binaries(self):
        self.assertIn("VENDOR_CHAIN_BEGIN", self.serial)
        self.assertIn("LOADER_OK", self.serial)

    def test_guest_buses_come_up(self):
        self.assertIn("DBUS_SYSTEM_OK", self.serial)
        self.assertIn("DBUS_SESSION_OK", self.serial)

    def test_weston_creates_the_wayland_socket(self):
        self.assertIn("WESTON_SOCKET_OK", self.serial)

    def test_guest_linker_resolves_the_observer_wrapper(self):
        """The interposition proof: the guest's own linker must pick our symbol."""
        matched = re.search(r"^PROBE resolved=(.+)$", self.serial, re.M)
        self.assertIsNotNone(matched, self.serial[-3000:])
        self.assertIn("navi-bg-0x0.so", matched[1])
        # The vendor library exports no wl_surface_commit at all, so the shared
        # definition has to be ours and not the library's.
        self.assertIn("PROBE shared=0", self.serial)
        self.assertIn("PROBE surface_symbol=0", self.serial)

    def test_observer_observes_a_real_client_through_the_vendor_abi(self):
        """A real client's null attach and its commits reach the observer."""
        self.assertIn("CLIENT_RC=0", self.serial)
        self.assertIn("CLIENT attach-commit-sent", self.serial)
        self.assertIn("interposed=1", self.serial)
        self.assertIn("surface#0 first observed", self.serial)
        self.assertRegex(self.serial, r"null-attach surface#0 target=1 .*attach=1")
        self.assertRegex(self.serial, r"commit-after-null-attach surface#0 forced=0 commit=1")
        self.assertIn("observation verdict=observed", self.serial)
        self.assertIn("complete=1", self.serial)
        self.assertRegex(self.serial, r"attaches=2 commits=2 null_attaches=2 commits_after_null=2")

    def test_launcher_starts_appnavi_with_the_observer_inside_it(self):
        self.assertIn("NAVI_REQUEST_OK", self.serial)
        self.assertRegex(self.serial, r"APPNAVI_PIDS=\s*\d+")
        self.assertIn("LD_PRELOAD=/opt/vm/navi-bg-0x0.so", self.serial)
        self.assertRegex(self.serial, r"APPNAVI_MAPS=[1-9]")
        self.assertRegex(self.serial, r"navi-bg: loaded pid=\d+")

    def test_appnavi_renderer_state_is_measured_not_assumed(self):
        """The handover quotes these; they have to come from a run."""
        self.assertRegex(self.serial, r"APPNAVI_RENDER_MAPS=[1-9]")
        self.assertIn("libEGL", self.serial)
        self.assertIn("libwayland-egl", self.serial)
        self.assertIn("APPNAVI_STDOUT=/dev/null", self.serial)
        self.assertRegex(self.serial, r"APPNAVI_SOCKET_FDS=\d+")
        self.assertRegex(self.serial, r"OPT_DIR=.*\bias\b")
        self.assertNotIn("software-egl", self.serial.split("OPT_DIR=")[1].split("\n")[0])

    def test_software_gl_stays_off_unless_the_workspace_opts_in(self):
        """The EGL substitution is experimental; the default run must not use it."""
        self.assertIn("SOFTWARE_GL=disabled", self.serial)

    def test_other_vendor_clients_reach_the_compositor(self):
        """The compositor works; AppNavi simply contributes no attach of its own.

        `OBSERVER_NAVI_LINES=0` is the canary: the observer's own surface lines are
        exactly the fact the status text calls unobserved, so a run that produces
        one fails here and forces the text to be updated.
        """
        self.assertRegex(self.serial, r"WESTON_CREATE_SURFACE=[1-9]")
        self.assertRegex(self.serial, r"WESTON_REGISTRIES=[1-9]")
        self.assertIn("OBSERVER_NAVI_LINES=0", self.serial)
        self.assertIn("APPNAVI_ALIVE=", self.serial)

    def test_chain_completes_and_reports_applauncher(self):
        self.assertIn("VENDOR_CHAIN_END", self.serial)
        self.assertRegex(self.serial, r"APPLAUNCHER_PIDS=\s*\d+")
        # Sampled while it is alive: the manager is gone from a late snapshot.
        self.assertRegex(self.serial, r"LAUNCHER_MANAGER=[1-9]")
        record = json.loads((self.runs / "result.json").read_text(encoding="utf-8"))
        self.assertTrue(record["userspace"])
        self.assertTrue(record["root_mounted"])
        self.assertEqual(record["command_exit_code"], 0)
        self.assertFalse(record["timeout"])
        self.assertIsNone(record["error"])


if __name__ == "__main__":
    unittest.main()
