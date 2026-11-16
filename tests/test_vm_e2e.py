"""End-to-end test: boot the prepared EU 260128 guest in QEMU and inspect it.

The prepared workspace holds the vendor kernel and a BusyBox serial shell, so
the end-to-end contract available today is exactly that: the measured kernel
image boots, the ext4 root is mounted through the patched SD controller, the
guest runs as root, the ABL loader arguments are readable from sysfs, and the
exit status of a guest command is relayed back over the serial console.

The test is skipped, never failed, when QEMU or the workspace is missing: both
are local artifacts outside version control.
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
TOOL = PROJECT / "tools/uk_fw/vm_boot.py"
SPEC = importlib.util.spec_from_file_location("vm_boot_e2e", TOOL)
VM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VM)

WORKSPACE = Path(os.environ.get("IONIQ_VM_WORKSPACE", "")
                 or PROJECT / "work/vm/bootable-eu260128")
BOOT_TIMEOUT = 120


def resolved_qemu() -> str | None:
    try:
        return VM.find_qemu()
    except ValueError:
        return None


def workspace_ready() -> bool:
    if not (WORKSPACE / "prepare.json").is_file():
        return False
    return all((WORKSPACE / name).is_file() for name in VM.ARTIFACTS)


def boot(command: str, timeout: float = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), "run", "--workspace", str(WORKSPACE),
         "--sdhci-compat", "--cmd", command, "--timeout", str(timeout)],
        cwd=PROJECT, capture_output=True, text=True, timeout=BOOT_TIMEOUT + timeout,
    )


def run_directory(result: subprocess.CompletedProcess) -> Path | None:
    matched = re.search(r"^Run artifacts: (.+)$", result.stdout, re.M)
    return Path(matched[1].strip()) if matched else None


@unittest.skipUnless(
    resolved_qemu() and workspace_ready(),
    "QEMU and a prepared EU 260128 workspace are required for the VM end-to-end test",
)
class VmEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = boot(VM.DEFAULT_COMMAND)
        cls.runs = run_directory(cls.result)

    def serial(self) -> str:
        self.assertIsNotNone(self.runs, self.result.stdout[-2000:] + self.result.stderr[-2000:])
        return (self.runs / "serial.log").read_text(encoding="utf-8", errors="replace")

    def result_record(self) -> dict:
        self.assertIsNotNone(self.runs, self.result.stderr[-2000:])
        return json.loads((self.runs / "result.json").read_text(encoding="utf-8"))

    def test_guest_boots_to_a_root_shell_end_to_end(self):
        self.assertEqual(self.result.returncode, 0,
                         self.result.stdout[-2000:] + self.result.stderr[-2000:])
        serial = self.serial()
        self.assertIn("IONIQ_VM_USERSPACE_READY", serial)
        self.assertIn("uid=0 gid=0", serial)
        self.assertRegex(serial, r"VM_COMMAND_END_[0-9a-f]{32}:0")

    def test_kernel_and_ext4_root_are_the_measured_ones(self):
        serial = self.serial()
        self.assertIn("Linux (none) 4.1.27-abl", serial)
        self.assertIn("VFS: Mounted root (ext4 filesystem)", serial)
        self.assertRegex(serial, r"/dev/root / ext4 rw")

    def test_sd_root_is_reached_through_the_compatibility_patch(self):
        serial = self.serial()
        self.assertIn("mmcblk0", serial)
        patch = json.loads((self.runs / "patch.json").read_text(encoding="utf-8"))
        self.assertEqual(patch["address"], hex(VM.TABLE_ENTRY))
        record = self.result_record()
        self.assertTrue(record["root_mounted"])
        self.assertTrue(record["compatibility_patch"])

    def test_abl_loader_arguments_reach_the_guest(self):
        serial = self.serial()
        self.assertIn("oemkm", serial)
        self.assertIn("seed", serial)

    def test_run_artifacts_and_result_are_consistent(self):
        record = self.result_record()
        self.assertTrue(record["userspace"])
        self.assertTrue(record["root_mounted"])
        self.assertEqual(record["command_exit_code"], 0)
        self.assertIsNone(record["error"])
        self.assertFalse(record["timeout"])
        self.assertTrue((self.runs / "command.json").is_file())

    def test_guest_exit_status_is_relayed_to_the_host(self):
        failure = boot("/bin/busybox false")
        self.assertEqual(failure.returncode, 1, failure.stdout[-1500:])
        self.assertRegex(failure.stdout, r"VM_COMMAND_END_[0-9a-f]{32}:1")
        runs = run_directory(failure)
        self.assertIsNotNone(runs)
        self.assertEqual(json.loads((runs / "result.json").read_text())["command_exit_code"], 1)


if __name__ == "__main__":
    unittest.main()
