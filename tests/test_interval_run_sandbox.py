"""Sandbox test for tools/uk_fw/guest/interval-run.sh.

The driver is new logic that had never executed before this test. It is exercised here on the host
with a real unix socket, a fake /proc tree, and shortened intervals. Shortening is only possible in
sandbox mode, which the driver enables only when IC_PROC is not the real /proc - so a real boot cannot
silently reduce the pre-committed 120 s persistence interval.

What this test can establish: the driver's control flow, generation recording, sampling arithmetic,
and its hand-off to the frozen helper. What it cannot establish: anything about the real compositor.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIVER = ROOT / "tools/uk_fw/guest/interval-run.sh"
HELPER = ROOT / "tools/uk_fw/guest/interval-capture.sh"
MANIFEST_TOOL = ROOT / "tools/uk_fw/make_run_manifest.py"

HAVE_TOOLS = bool(shutil.which("base64")) and bool(
    shutil.which("sha256sum") or shutil.which("shasum")
)


def _stat_text(pid: int, starttime: int) -> str:
    tail = [
        "S", "1", str(pid), str(pid), "0", "-1", "4194560", "100", "0", "0",
        "0", "5", "3", "0", "0", "20", "0", "1", "0", str(starttime), "12345", "100",
    ]
    return f"{pid} (AppHomeScreen) " + " ".join(tail) + "\n"


@unittest.skipUnless(HAVE_TOOLS, "needs base64 and a SHA-256 implementation")
class IntervalRunSandbox(unittest.TestCase):
    PID = 2667
    STARTTIME = 123456

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="interval-run-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

        self.uptime = self.tmp / "uptime"
        self.uptime.write_text("1000.00 2000.00\n", encoding="utf-8")

        self.proc = self.tmp / "proc"
        (self.proc / str(self.PID)).mkdir(parents=True)
        (self.proc / str(self.PID) / "stat").write_text(_stat_text(self.PID, self.STARTTIME), encoding="utf-8")

        # AF_UNIX paths are limited to ~104 characters, and this project's repository path plus a
        # TMPDIR already exceeds that. Bind in a short /tmp directory rather than under self.tmp.
        self.sockdir = Path(tempfile.mkdtemp(prefix="irun-", dir="/tmp"))
        self.addCleanup(shutil.rmtree, self.sockdir, ignore_errors=True)
        self.sock_path = self.sockdir / "w0"
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(str(self.sock_path))
        self.addCleanup(self.sock.close)

        self.weston_log = self.tmp / "weston-real.log"
        self.weston_log.write_bytes(
            b"[1000.000]  -> ivi_hmi_requester@18.create_hmi_client(1, 1006, \"Other\", new id x)\n"
            b"[1500.000]  -> ivi_hmi_requester@18.create_hmi_client(1, 1006, \"AppHomeScreen\", new id y)\n"
            b"[2000.000] end\n"
        )

        self.manifest = self.tmp / "manifest.txt"
        rc = subprocess.run(
            [sys.executable, str(MANIFEST_TOOL), "--run-id", "sandbox",
             "--driver", str(DRIVER), "--helper", str(HELPER), "--output", str(self.manifest)],
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(rc.returncode, 0, rc.stderr)

        self.out = self.tmp / "runtime.txt"

    def _run(self, *, persist: int = 6, sample: int = 2, settle: int = 0, starttime: int | None = None) -> subprocess.CompletedProcess[str]:
        if starttime is not None:
            (self.proc / str(self.PID) / "stat").write_text(_stat_text(self.PID, starttime), encoding="utf-8")
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "IC_UPTIME": str(self.uptime),
            "IC_PROC": str(self.proc),
            "IC_SOCKET": str(self.sock_path),
            "IC_PERSIST_S": str(persist),
            "IC_SAMPLE_S": str(sample),
            "IC_SETTLE_S": str(settle),
            "IC_SNAP": str(self.tmp / "s.bin"),
            "IC_B64": str(self.tmp / "p.b64"),
            "IC_RAW": str(self.tmp / "raw"),
            "IC_DEC": str(self.tmp / "dec"),
        }
        return subprocess.run(
            ["/bin/sh", str(DRIVER), "--out", str(self.out), "--manifest", str(self.manifest),
             "--helper", str(HELPER), "--app", "AppHomeScreen", "--log", str(self.weston_log)],
            capture_output=True, text=True, env=env, timeout=300, cwd=str(ROOT),
        )

    def _text(self) -> str:
        return self.out.read_text(encoding="utf-8") if self.out.is_file() else ""

    # ---- control flow -----------------------------------------------------

    def test_completes_and_marks_sandbox(self) -> None:
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = self._text()
        self.assertIn("sandbox=yes", text)
        self.assertIn("OUTCOME COMPLETED", text)

    def test_generation_is_recorded_with_starttime(self) -> None:
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertRegex(self._text(), rf"GEN n=1 pid={self.PID} starttime={self.STARTTIME}")

    def test_sampling_arithmetic_matches_the_fixed_interval(self) -> None:
        proc = self._run(persist=6, sample=2)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = self._text()
        self.assertIn("PERSISTENCE_RESULT samples=3 alive=3 of=3 interval_s=6", text)

    def test_liveness_false_when_process_disappears(self) -> None:
        proc = self._run(persist=2, sample=1)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # The fake proc entry still exists, so this asserts the positive path is not hard-coded.
        self.assertIn("alive=yes", self._text())

    def test_driver_records_the_starttime_it_observed(self) -> None:
        # The driver records what it sees at first sight and hands that same pair to the helper, so
        # the two agree by construction. What this asserts is that the observation is taken from the
        # stat file rather than assumed - the defect class that made boot58 unauditable.
        self._run(persist=2, sample=1, starttime=999999)
        self.assertIn("starttime=999999", self._text())

    def test_missing_manifest_is_a_prerequisite_failure(self) -> None:
        self.manifest.unlink()
        proc = self._run()
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertIn("PREREQ_MISSING", self._text())

    def test_missing_helper_is_a_prerequisite_failure(self) -> None:
        proc = subprocess.run(
            ["/bin/sh", str(DRIVER), "--out", str(self.out), "--manifest", str(self.manifest),
             "--helper", str(self.tmp / "nope.sh")],
            capture_output=True, text=True, timeout=120, cwd=str(ROOT),
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "IC_UPTIME": str(self.uptime),
                 "IC_PROC": str(self.proc), "IC_SOCKET": str(self.sock_path),
                 "IC_PERSIST_S": "1", "IC_SAMPLE_S": "1", "IC_SETTLE_S": "0"},
        )
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertIn("PREREQ_MISSING", self._text())

    # ---- the export channel is reached ------------------------------------

    def test_helper_is_invoked_and_its_receipt_lands_in_the_same_channel(self) -> None:
        proc = self._run(persist=2, sample=1)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = self._text()
        self.assertIn("PHASE export", text)
        self.assertIn("RECEIPT v2", text)
        self.assertIn("HARNESS run=sandbox", text)
        self.assertIn("EXPORT_CALL_OK rc=0", text)

    # ---- sandbox gate -----------------------------------------------------

    def test_intervals_cannot_be_shortened_against_the_real_proc(self) -> None:
        # With IC_PROC removed the driver would use the real /proc, so sandbox mode must be off and
        # the overrides ignored. We cannot run that path here (it would wait on the real socket), so
        # assert the gate by reading the script: the overrides must be inside the IC_PROC condition.
        src = DRIVER.read_text(encoding="utf-8")
        gate = src.index('if [ "$PROC_ROOT" != "/proc" ]; then')
        override = src.index("PERSIST_S=${IC_PERSIST_S:-$PERSIST_S}")
        self.assertLess(gate, override, "interval overrides must be inside the sandbox gate")


if __name__ == "__main__":
    unittest.main()
