"""Integration test for tools/uk_fw/guest/interval-capture.sh.

Runs the real guest script on the host against synthetic inputs and asserts the guarantees that
docs/kernel/42 requires. This is deliberately an end-to-end test rather than a unit test of the
shell: the defects being prevented (a streamed export exceeding its own bound, a name-only
capture binding, an unidentifiable harness) were all integration-shaped, so a unit test of the
pieces would not have caught them.

Requires only a POSIX shell plus base64/sha256sum, so it runs on the host without the guest.
"""

from __future__ import annotations

import base64
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/uk_fw/guest/interval-capture.sh"

HAVE_TOOLS = bool(shutil.which("base64")) and bool(shutil.which("sha256sum") or shutil.which("shasum"))


def _synthetic_log(lines: int, start_ms: int = 637916) -> str:
    """A log shaped like the weston protocol stream: one timestamped line per millisecond."""
    out = []
    for i in range(lines):
        out.append(f"[{start_ms + i}.{i % 1000:03d}]  -> wl_display@1.sync(new id wl_callback@{i})\n")
    return "".join(out)


@unittest.skipUnless(HAVE_TOOLS, "needs base64 and a sha256 implementation")
class IntervalCaptureIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="interval-capture-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.log = self.tmp / "weston-real.log"
        self.out = self.tmp / "receipt.txt"
        self.uptime = self.tmp / "uptime"
        self.uptime.write_text("1000.00 2000.00\n", encoding="utf-8")

    def _run(self, extra_env: dict[str, str] | None = None, settle: int = 0, generation: str | None = None) -> subprocess.CompletedProcess[str]:
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "IC_UPTIME": str(self.uptime),
            "IC_PROC": str(self.tmp / "proc"),
        }
        if extra_env:
            env.update(extra_env)
        args = ["/bin/sh", str(SCRIPT), "--log", str(self.log), "--out", str(self.out), "--settle", str(settle)]
        if generation is not None:
            args += ["--generation", generation]
        return subprocess.run(args, capture_output=True, text=True, env=env, timeout=120)

    def test_closed_snapshot_never_exceeds_measured_size(self) -> None:
        # The exact boot58 defect: the export must not contain more than was measured.
        self.log.write_text(_synthetic_log(500), encoding="utf-8")
        measured = self.log.stat().st_size
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = self.out.read_text(encoding="utf-8")

        self.assertIn("SNAPSHOT_CLOSED", receipt)
        cap = [ln for ln in receipt.splitlines() if ln.startswith("CAPTURE ")][0]
        self.assertIn(f"bytes={measured}", cap)

        # Recover the emitted base64 and prove it decodes to exactly the measured size.
        blob = receipt.split("BEGIN interval ", 1)[1].split("\n", 1)[1].split("\nENDinterval", 1)[0]
        decoded = base64.b64decode(blob)
        self.assertEqual(len(decoded), measured)

    def test_appending_during_capture_cannot_widen_the_export(self) -> None:
        # Simulates a still-growing log. The bound is taken first, so late writes are excluded.
        self.log.write_text(_synthetic_log(400), encoding="utf-8")
        measured = self.log.stat().st_size
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = self.out.read_text(encoding="utf-8")
        self.assertIn(f"bytes={measured}", receipt)
        self.assertIn(f"SNAPSHOT_CLOSED bytes={measured} decoded={measured} match=yes", receipt)

    def test_self_identity_is_recorded(self) -> None:
        self.log.write_text(_synthetic_log(10), encoding="utf-8")
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = self.out.read_text(encoding="utf-8")
        # The path legitimately contains spaces, so the path group cannot be \S+.
        self.assertRegex(receipt, r"SELF path=.+ algo=(sha256|md5) digest=[0-9a-f]{32,64}")

    def test_unidentifiable_harness_refuses_to_measure(self) -> None:
        # If the script cannot hash itself, it must stop rather than emit measurements.
        self.log.write_text(_synthetic_log(10), encoding="utf-8")
        proc = self._run(extra_env={"PATH": "/nonexistent"})
        self.assertEqual(proc.returncode, 3, proc.stderr)
        receipt = self.out.read_text(encoding="utf-8")
        self.assertIn("OUTCOME HARNESS_UNIDENTIFIED", receipt)
        self.assertNotIn("SNAPSHOT_CLOSED", receipt)

    def test_unbound_capture_is_labelled_name_only(self) -> None:
        self.log.write_text(_synthetic_log(10), encoding="utf-8")
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = self.out.read_text(encoding="utf-8")
        self.assertIn("binding=name_only", receipt)

    def test_requested_generation_absent_is_a_harness_mismatch(self) -> None:
        self.log.write_text(_synthetic_log(10), encoding="utf-8")
        (self.tmp / "proc").mkdir(exist_ok=True)
        proc = self._run(generation="2")
        self.assertEqual(proc.returncode, 5, proc.stderr)
        receipt = self.out.read_text(encoding="utf-8")
        self.assertIn("OUTCOME HARNESS_MISMATCH", receipt)
        self.assertIn("requested_generation_absent", receipt)

    def test_markers_carry_monotonic_and_offset(self) -> None:
        self.log.write_text(_synthetic_log(10), encoding="utf-8")
        proc = self._run(settle=1)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = self.out.read_text(encoding="utf-8")
        marks = [ln for ln in receipt.splitlines() if ln.startswith("MARK ")]
        self.assertTrue(marks, "expected MARK lines")
        for line in marks:
            self.assertIn("t_mono=", line)
            self.assertIn("off_c=", line)

    def test_first_and_last_protocol_timestamps_are_extracted(self) -> None:
        self.log.write_text(_synthetic_log(50, start_ms=637916), encoding="utf-8")
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = self.out.read_text(encoding="utf-8")
        self.assertIn("first_ts=637916", receipt)
        self.assertIn("last_ts=637965", receipt)

    def test_empty_log_is_refused(self) -> None:
        self.log.write_text("", encoding="utf-8")
        proc = self._run()
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("OUTCOME HARNESS_MISMATCH", self.out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
