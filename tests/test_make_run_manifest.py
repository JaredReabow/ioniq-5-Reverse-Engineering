"""Tests for tools/uk_fw/make_run_manifest.py and its integration with the capture helper.

Astra C10 rejected a hand-written manifest: the check must describe the files that actually exist,
computed from those files. Astra C11 then established the manifest's limit — it proves the named
driver file *matched*, never that the driver *ran* — so these tests assert only the property the
manifest can carry.
"""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/uk_fw/make_run_manifest.py"
DRIVER = ROOT / "tools/uk_fw/guest/interval-run.sh"
HELPER = ROOT / "tools/uk_fw/guest/interval-capture.sh"

spec = importlib.util.spec_from_file_location("make_run_manifest", TOOL_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestManifestContents(unittest.TestCase):
    def test_digest_is_computed_from_the_real_bytes(self) -> None:
        text = mod.build_manifest("r1", DRIVER, HELPER)
        self.assertIn(f"sha256={_sha(DRIVER)}", text)
        self.assertIn(f"sha256={_sha(HELPER)}", text)

    def test_matches_independent_sha256(self) -> None:
        # Cross-check against the platform tool, so a bug in sha256_of cannot hide.
        tool = shutil.which("shasum") or shutil.which("sha256sum")
        if not tool:
            self.skipTest("no independent sha256 tool")
        cmd = [tool, "-a", "256", str(DRIVER)] if tool.endswith("shasum") else [tool, str(DRIVER)]
        expected = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.split()[0]
        self.assertIn(f"sha256={expected}", mod.build_manifest("r1", DRIVER, HELPER))

    def test_run_id_and_record_shape(self) -> None:
        lines = mod.build_manifest("my-run", DRIVER, HELPER).splitlines()
        self.assertEqual(lines[0], "RUN id=my-run")
        self.assertTrue(lines[1].startswith("DRIVER path="))
        self.assertTrue(lines[2].startswith("HELPER path="))

    def test_spaced_path_is_preserved_whole(self) -> None:
        # The project's own repository path contains spaces, and a truncated extraction once
        # resolved to a directory that hashed to nothing.
        tmp = Path(tempfile.mkdtemp(prefix="manifest space "))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        spaced = tmp / "with space.sh"
        spaced.write_text("#!/bin/sh\ntrue\n", encoding="utf-8")
        text = mod.build_manifest("r1", spaced, HELPER)
        self.assertIn(f"DRIVER path={spaced} sha256=", text)

    def test_missing_driver_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            mod.build_manifest("r1", ROOT / "nope-does-not-exist.sh", HELPER)

    def test_directory_driver_raises(self) -> None:
        # A directory is not a driver; the helper once accepted one because it only tested -r.
        with self.assertRaises(FileNotFoundError):
            mod.build_manifest("r1", ROOT / "tools", HELPER)


class TestGuestPaths(unittest.TestCase):
    """The guest sees staged paths, not host paths, so the manifest must be able to name them.

    The digest is still computed from the host file - only the recorded path differs. Recording the
    host path would make the helper's in-guest readability check fail for the wrong reason.
    """

    def test_guest_paths_are_recorded_while_digests_come_from_host_files(self) -> None:
        text = mod.build_manifest(
            "r1", DRIVER, HELPER,
            driver_guest_path="/interval-run.sh",
            helper_guest_path="/interval-capture.sh",
        )
        self.assertIn("DRIVER path=/interval-run.sh", text)
        self.assertIn("HELPER path=/interval-capture.sh", text)
        self.assertIn(f"sha256={_sha(DRIVER)}", text)
        self.assertIn(f"sha256={_sha(HELPER)}", text)
        self.assertNotIn(str(DRIVER), text)

    def test_absent_guest_path_falls_back_to_host_path(self) -> None:
        text = mod.build_manifest("r1", DRIVER, HELPER)
        self.assertIn(f"DRIVER path={DRIVER}", text)


class TestManifestCli(unittest.TestCase):
    def test_writes_file(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="manifest-cli-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        out = tmp / "manifest.txt"
        rc = mod.main(["--run-id", "cli-run", "--driver", str(DRIVER), "--helper", str(HELPER), "--output", str(out)])
        self.assertEqual(rc, 0)
        self.assertIn("RUN id=cli-run", out.read_text(encoding="utf-8"))

    def test_missing_file_returns_3(self) -> None:
        rc = mod.main(["--run-id", "x", "--driver", str(ROOT / "nope.sh"), "--helper", str(HELPER)])
        self.assertEqual(rc, 3)


@unittest.skipUnless(
    shutil.which("base64") and (shutil.which("sha256sum") or shutil.which("shasum")),
    "needs base64 and sha256",
)
class TestGeneratorFeedsTheHelper(unittest.TestCase):
    """The generated manifest must be accepted by the frozen helper. This is the integration seam."""

    def test_helper_accepts_generated_manifest(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="manifest-int-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "up").write_text("1000.00 2000.00\n", encoding="utf-8")
        (tmp / "proc" / "2667").mkdir(parents=True)
        (tmp / "proc" / "2667" / "stat").write_text(
            "2667 (AppHomeScreen) S 1 2667 2667 0 -1 4194560 100 0 0 0 5 3 0 0 20 0 1 0 123456 12345 100\n",
            encoding="utf-8",
        )
        manifest = tmp / "manifest.txt"
        self.assertEqual(
            mod.main(["--run-id", "int", "--driver", str(DRIVER), "--helper", str(HELPER), "--output", str(manifest)]),
            0,
        )
        log = tmp / "weston.log"
        log.write_bytes(b"[1000.000] a\n[2000.000] b\n")
        out = tmp / "receipt.txt"
        env = {
            "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
            "IC_UPTIME": str(tmp / "up"),
            "IC_PROC": str(tmp / "proc"),
            "IC_SNAP": str(tmp / "s.bin"),
            "IC_B64": str(tmp / "p.b64"),
            "IC_RAW": str(tmp / "raw"),
            "IC_DEC": str(tmp / "dec"),
        }
        proc = subprocess.run(
            ["/bin/sh", str(HELPER), "--manifest", str(manifest), "--log", str(log),
             "--out", str(out), "--settle", "0", "--expect-pid", "2667",
             "--expect-starttime", "123456"],
            capture_output=True, text=True, env=env, timeout=300, cwd=str(ROOT),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = out.read_text(encoding="utf-8")
        self.assertIn("HARNESS run=int", receipt)
        self.assertIn("helper_sha256=", receipt)
        self.assertIn("driver_sha256=", receipt)


if __name__ == "__main__":
    unittest.main()
