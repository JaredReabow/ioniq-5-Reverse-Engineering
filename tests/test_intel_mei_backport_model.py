from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/uk_fw/intel_mei_backport_model.py"
EVIDENCE = ROOT / "evidence/artifacts/kernel-candidates/intel-mei-backport-exact-static.asm"
SPEC = importlib.util.spec_from_file_location("intel_mei_backport_model", TOOL)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class IntelMeiBackportModelTests(unittest.TestCase):
    def test_pre_recorded_state_rejects_four_historical_premises(self) -> None:
        result = M.classify(**M.PRE_RECORDED_TARGET_STATE)
        self.assertTrue(result["all_four_historical_premises_rejected"])
        self.assertTrue(all(result["complete_fix_effects"].values()))
        self.assertTrue(
            all(result["historical_premises_rejected_by_supplied_fix_effects"].values())
        )
        for name in M.OBSERVED_FIELDS:
            self.assertIsNone(result[name])

    def test_exhaustive_fix_effect_domain(self) -> None:
        for bits in itertools.product((False, True), repeat=len(M.FACT_NAMES)):
            state = dict(zip(M.FACT_NAMES, bits))
            with self.subTest(bits=bits):
                result = M.classify(**state)
                rejected = result[
                    "historical_premises_rejected_by_supplied_fix_effects"
                ]
                self.assertEqual(
                    result["all_four_historical_premises_rejected"],
                    all(rejected.values()),
                )

    def test_each_fact_is_required_by_at_least_one_fix(self) -> None:
        baseline = M.classify(**M.PRE_RECORDED_TARGET_STATE)
        for name in M.FACT_NAMES:
            state = dict(M.PRE_RECORDED_TARGET_STATE)
            state[name] = False
            with self.subTest(name=name):
                result = M.classify(**state)
                self.assertNotEqual(
                    result["complete_fix_effects"], baseline["complete_fix_effects"]
                )
                self.assertFalse(result["all_four_historical_premises_rejected"])

    def test_rejects_wrong_keys_and_non_booleans(self) -> None:
        state = dict(M.PRE_RECORDED_TARGET_STATE)
        state.pop(M.FACT_NAMES[0])
        with self.assertRaisesRegex(M.ModelError, "state keys mismatch"):
            M.classify(**state)
        state = dict(M.PRE_RECORDED_TARGET_STATE)
        state[M.FACT_NAMES[0]] = 1
        with self.assertRaisesRegex(M.ModelError, "must be a boolean"):
            M.classify(**state)

    def test_exact_static_artifact_identity_and_regions(self) -> None:
        data = EVIDENCE.read_bytes()
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            M.build_report()["artifact"]["exact_static_excerpt_sha256"],
        )
        text = data.decode("utf-8")
        for token in (
            "000000000000228c <mei_cl_irq_read_msg>",
            "0000000000004c4c <mei_cl_write>",
            "00000000000050d8 <mei_cl_complete>",
            "000000000000566f <mei_write>",
            "R_X86_64_PC32\tmei_io_cb_free-0x4",
            "R_X86_64_PC32\tmei_cl_set_disconnected-0x4",
        ):
            self.assertIn(token, text)

    def test_cli_deterministic_across_output_encodings(self) -> None:
        expected = json.dumps(M.build_report(), indent=2, sort_keys=True).encode("ascii") + b"\n"
        outputs = []
        for encoding in ("ascii:strict", "latin-1:strict", "utf-16:strict"):
            run = subprocess.run(
                [sys.executable, str(TOOL)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONIOENCODING": encoding},
            )
            self.assertEqual(run.stdout, expected)
            self.assertNotIn(b"\r", run.stdout)
            outputs.append(run.stdout)
        self.assertEqual(len(set(outputs)), 1)
        self.assertEqual(
            hashlib.sha256(outputs[0]).hexdigest(),
            "ad7fe8d29735da6e8a800c1ee3d037a33b3f992b45ccb2434fdd04a3f4d295f8",
        )

    def test_cli_requires_complete_explicit_state(self) -> None:
        option = "--" + M.FACT_NAMES[0].replace("_", "-")
        run = subprocess.run(
            [sys.executable, str(TOOL), option, "true"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("supply all Intel MEI fix-effect arguments or none", run.stderr)

    def test_report_contains_no_operational_mei_material(self) -> None:
        encoded = json.dumps(M.build_report(), sort_keys=True).lower()
        for forbidden in (
            "ioctl(",
            "open(/dev/mei",
            "write(/dev/mei",
            "heci_connect",
            "client_uuid",
            "0xffffffff",
        ):
            self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
