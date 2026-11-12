"""Exercise installed-media commands without hardware or large image reads."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "tools/uk_fw/radxa_update_media.sh"


class RadxaUpdateMediaTests(unittest.TestCase):
    """The wrapper performs explicit preparation and fast, manually armed starts."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "commands.log"
        for name in ("modprobe", "mountpoint", "mount", "systemctl", "python3"):
            source = ('#!/bin/sh\nprintf "%s %s\\n" "${0##*/}" "$*" >>"$WRAPPER_LOG"\n'
                      + ('[ "$1" != is-active ]\n' if name == "systemctl" else 'exit 0\n'))
            executable = self.bin / name
            executable.write_text(source)
            executable.chmod(0o755)
        self.script = self.root / "wrapper.sh"
        source = SCRIPT.read_text().replace("base=/opt/ioniq5-update", f"base={self.root}/app")
        source = source.replace("runtime=/run/ioniq5-update", f"runtime={self.root}/run")
        source = source.replace("private=/var/lib/ioniq5-update", f"private={self.root}/private")
        self.script.write_text(source)

    def run_wrapper(self, command):
        result = subprocess.run(["/bin/bash", str(self.script), command],
            env=os.environ | {"PATH": str(self.bin) + ":" + os.environ["PATH"],
                              "WRAPPER_LOG": str(self.log)},
            capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.log.read_text()

    def test_arm_has_no_build_or_hash_and_records_a_session(self):
        log = self.run_wrapper("arm")
        self.assertIn("systemctl start ioniq-update-media.service", log)
        self.assertNotIn(" prepare ", log)
        self.assertIn("arm_requested", log)
        self.assertIn("armed", log)
        self.assertFalse((self.root / "run/manual-arm").exists())

    def test_internal_arm_requires_prepared_cache(self):
        log = self.run_wrapper("internal-arm")
        self.assertIn("--execute --hold --validation-cache", log)
        self.assertNotIn(" prepare ", log)

    def test_preparation_is_explicit_and_full_verify_can_be_requested(self):
        prepared = self.run_wrapper("prepare")
        self.assertIn(" prepare --serve-plan ", prepared)
        self.assertNotIn("--force", prepared)
        self.log.unlink()
        verified = self.run_wrapper("verify")
        self.assertIn("--force", verified)

    def test_teardown_stops_the_service_before_controller_cleanup(self):
        log = self.run_wrapper("teardown")
        self.assertLess(log.index("systemctl stop "), log.index(" teardown --execute"))
        self.assertIn("stopped", log)


if __name__ == "__main__":
    unittest.main()
