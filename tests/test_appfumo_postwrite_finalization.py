from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/uk_fw/appfumo_postwrite_finalization.py"
ELF = ROOT / "work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf"

spec = importlib.util.spec_from_file_location("appfumo_postwrite_finalization", TOOL_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


@unittest.skipUnless(ELF.is_file(), "exact recovered AppFUMO ELF is unavailable")
class AppFumoPostwriteFinalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = ELF.read_bytes()

    def test_exact_analysis(self) -> None:
        report = mod.analyze(self.data)
        self.assertEqual(report["schema"], mod.SCHEMA)
        self.assertEqual(report["input"]["sha256"], mod.EXPECTED_SHA256)
        self.assertEqual(report["input"]["build_id"], mod.EXPECTED_BUILD_ID)
        self.assertEqual(len(report["instruction_ranges"]), 6)
        self.assertEqual(len(report["direct_calls"]), len(mod.DIRECT_CALLS))
        self.assertEqual(report["finish_dispatch"]["finish_raw_va"], "0xd1e70")
        self.assertEqual(report["fstab_rewrite"]["selected_vr_variant"], "foldervr when present, otherwise vr")
        self.assertIn("progress 100 can be reported", report["finish_flow"]["failure_boundary"])
        self.assertEqual(report["bounded_conclusion"]["status"], "exact_static_postwrite_finalization_boundary")

    def test_identity_mismatch_fails_closed(self) -> None:
        changed = bytearray(self.data)
        changed[-1] ^= 1
        with self.assertRaisesRegex(mod.Failure, "SHA-256 mismatch"):
            mod.analyze(bytes(changed))

    def test_malformed_elf_is_rejected_after_identity_boundary(self) -> None:
        original = mod.EXPECTED_SHA256
        changed = bytearray(self.data)
        changed[0] = 0
        mod.EXPECTED_SHA256 = hashlib.sha256(changed).hexdigest()
        try:
            with self.assertRaisesRegex(mod.Failure, "ELF64"):
                mod.analyze(bytes(changed))
        finally:
            mod.EXPECTED_SHA256 = original

    def test_instruction_drift_is_rejected_after_identity_boundary(self) -> None:
        original_sha = mod.EXPECTED_SHA256
        changed = bytearray(self.data)
        changed[0xD0C80] ^= 1
        mod.EXPECTED_SHA256 = hashlib.sha256(changed).hexdigest()
        try:
            with self.assertRaisesRegex(mod.Failure, "instruction-range mismatch"):
                mod.analyze(bytes(changed))
        finally:
            mod.EXPECTED_SHA256 = original_sha

    def test_direct_call_contract_fails_closed(self) -> None:
        original = mod.DIRECT_CALLS
        changed = dict(original)
        site, target = changed["modify_fstab"]
        changed["modify_fstab"] = (site, target + 1)
        mod.DIRECT_CALLS = changed
        try:
            with self.assertRaisesRegex(mod.Failure, "direct-call target mismatch"):
                mod.analyze(self.data)
        finally:
            mod.DIRECT_CALLS = original

    def test_literal_contract_fails_closed(self) -> None:
        original = mod.LITERALS
        changed = dict(original)
        va, value = changed["complete_message"]
        changed["complete_message"] = (va, value + " changed")
        mod.LITERALS = changed
        try:
            with self.assertRaisesRegex(mod.Failure, "literal mismatch"):
                mod.analyze(self.data)
        finally:
            mod.LITERALS = original

    def test_vtable_relocation_contract_fails_closed(self) -> None:
        original = mod.VTABLE_TARGET_VA
        mod.VTABLE_TARGET_VA = original + 1
        try:
            with self.assertRaisesRegex(mod.Failure, "vtable relocation mismatch"):
                mod.analyze(self.data)
        finally:
            mod.VTABLE_TARGET_VA = original

    def test_stable_read_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            link = Path(td) / "elf"
            link.symlink_to(ELF)
            with self.assertRaises(mod.Failure):
                mod.stable_read(link)

    def test_cli_is_deterministic_under_host_encoding(self) -> None:
        base = subprocess.run([sys.executable, str(TOOL_PATH), str(ELF)], cwd=ROOT, check=True, capture_output=True)
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-16"
        altered = subprocess.run([sys.executable, str(TOOL_PATH), str(ELF)], cwd=ROOT, env=env, check=True, capture_output=True)
        self.assertEqual(base.stdout, altered.stdout)
        self.assertTrue(base.stdout.endswith(b"\n"))
        self.assertNotIn(b"\r", base.stdout)
        parsed = json.loads(base.stdout.decode("utf-8"))
        self.assertEqual(parsed["schema"], mod.SCHEMA)

    def test_cli_output_is_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "report.json"
            first = subprocess.run([sys.executable, str(TOOL_PATH), str(ELF), "-o", str(output)], cwd=ROOT, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr.decode())
            second = subprocess.run([sys.executable, str(TOOL_PATH), str(ELF), "-o", str(output)], cwd=ROOT, capture_output=True)
            self.assertEqual(second.returncode, 2)
            self.assertIn(b"File exists", second.stderr)


if __name__ == "__main__":
    unittest.main()
