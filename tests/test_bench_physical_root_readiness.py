from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "bench_physical_root_readiness.py"
SPEC = importlib.util.spec_from_file_location("bench_physical_root_readiness", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def seal(report: dict[str, object]) -> dict[str, object]:
    value = copy.deepcopy(report)
    value.pop("canonical_sha256", None)
    value["canonical_sha256"] = hashlib.sha256(canonical_bytes(value)).hexdigest()
    return value


def positive_report() -> dict[str, object]:
    report: dict[str, object] = {
        "schema": MODULE.INPUT_SCHEMA,
        "capture_sha256": "a" * 64,
        "capture_bytes": 1234,
        "complete": True,
        "section_order": list(MODULE.EXPECTED_SECTION_ORDER),
        "sections": [],
        "facts": {
            "hashes": dict(MODULE.REFERENCE_HASHES),
            "files": {
                "/dev/tty9": "present|600|0|0|0|character special file|4|9|",
            },
            "units": {
                "debug-shell.service": (
                    "LoadState=loaded;ActiveState=inactive;SubState=dead;"
                    "UnitFileState=disabled;"
                ),
            },
        },
        "warnings": [],
    }
    return seal(report)


class BenchPhysicalRootReadinessTests(unittest.TestCase):
    def test_positive_report_observes_prerequisites_not_root(self) -> None:
        result = MODULE.assess(positive_report())
        self.assertEqual(result["schema"], MODULE.OUTPUT_SCHEMA)
        self.assertTrue(result["verdict"]["scsi_root_console_prerequisites_observed"])
        self.assertTrue(result["verdict"]["v4l_property_injection_prerequisites_observed"])
        for key in (
            "hardware_control_bytes_observed",
            "property_injection_observed",
            "debug_shell_activation_observed",
            "interactive_console_observed",
            "root_access_demonstrated",
            "persistence_demonstrated",
        ):
            self.assertFalse(result["verdict"][key])
        self.assertEqual(result["gate_counts"], {"fail": 0, "pass": 12, "unknown": 0})
        subject = dict(result)
        digest = subject.pop("canonical_sha256")
        self.assertEqual(hashlib.sha256(canonical_bytes(subject)).hexdigest(), digest)

    def test_inactive_disabled_loaded_unit_still_passes_load_gate(self) -> None:
        result = MODULE.assess(positive_report())
        gate = next(gate for gate in result["gates"] if gate["id"] == "debug_shell.loaded")
        self.assertEqual(gate["status"], "pass")
        self.assertEqual(gate["observed"]["ActiveState"], "inactive")
        self.assertEqual(gate["observed"]["UnitFileState"], "disabled")
        self.assertFalse(result["verdict"]["debug_shell_activation_observed"])

    def test_missing_runtime_values_remain_unknown(self) -> None:
        report = positive_report()
        report["facts"] = {"hashes": {}, "files": {}, "units": {}}
        report = seal(report)
        result = MODULE.assess(report)
        statuses = {gate["id"]: gate["status"] for gate in result["gates"]}
        self.assertEqual(statuses["capture.complete"], "pass")
        self.assertTrue(all(status == "unknown" for key, status in statuses.items() if key != "capture.complete"))
        self.assertFalse(result["verdict"]["scsi_root_console_prerequisites_observed"])

    def test_identity_mismatch_fails_only_affected_chain(self) -> None:
        report = positive_report()
        report["facts"]["hashes"]["/lib/udev/scsi_id"] = "b" * 64
        report = seal(report)
        result = MODULE.assess(report)
        statuses = {gate["id"]: gate["status"] for gate in result["gates"]}
        self.assertEqual(statuses["scsi.helper_identity"], "fail")
        self.assertFalse(result["verdict"]["scsi_root_console_prerequisites_observed"])
        self.assertTrue(result["verdict"]["v4l_property_injection_prerequisites_observed"])
        self.assertFalse(result["verdict"]["root_access_demonstrated"])

    def test_tty9_wrong_device_fails(self) -> None:
        report = positive_report()
        report["facts"]["files"]["/dev/tty9"] = (
            "present|600|0|0|0|character special file|4|8|"
        )
        report = seal(report)
        result = MODULE.assess(report)
        gate = next(gate for gate in result["gates"] if gate["id"] == "console.tty9")
        self.assertEqual(gate["status"], "fail")
        self.assertFalse(result["verdict"]["scsi_root_console_prerequisites_observed"])

    def test_incomplete_capture_blocks_both_prerequisite_verdicts(self) -> None:
        report = positive_report()
        report["complete"] = False
        report["warnings"] = ["capture truncated"]
        report = seal(report)
        result = MODULE.assess(report)
        self.assertEqual(result["gates"][0]["status"], "fail")
        self.assertFalse(result["verdict"]["scsi_root_console_prerequisites_observed"])
        self.assertFalse(result["verdict"]["v4l_property_injection_prerequisites_observed"])

    def test_duplicate_key_nonfinite_and_bad_digest_are_rejected(self) -> None:
        duplicate = b'{"schema":"ioniq-bench-state/v1","schema":"x"}'
        with self.assertRaisesRegex(MODULE.AssessmentError, "duplicate"):
            MODULE.load_report_bytes(duplicate)
        with self.assertRaisesRegex(MODULE.AssessmentError, "non-finite"):
            MODULE.load_report_bytes(b'{"schema":"ioniq-bench-state/v1","x":NaN}')
        report = positive_report()
        report["canonical_sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.AssessmentError, "canonical_sha256 mismatch"):
            MODULE.load_report_bytes(json.dumps(report).encode())

    def test_invalid_utf8_and_oversized_input_are_rejected(self) -> None:
        with self.assertRaisesRegex(MODULE.AssessmentError, "strict UTF-8"):
            MODULE.load_report_bytes(b"\xff")
        with self.assertRaisesRegex(MODULE.AssessmentError, "exceeds"):
            MODULE.load_report_bytes(b" " * (MODULE.MAX_INPUT_BYTES + 1))

    def test_cli_is_encoding_independent_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "state.json"
            source.write_text(json.dumps(positive_report()), encoding="utf-8")
            normal = subprocess.run(
                [sys.executable, str(TOOL), str(source)],
                check=False,
                capture_output=True,
            )
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-16"
            utf16 = subprocess.run(
                [sys.executable, str(TOOL), str(source)],
                check=False,
                capture_output=True,
                env=env,
            )
            self.assertEqual(normal.returncode, 0, normal.stderr)
            self.assertEqual(utf16.returncode, 0, utf16.stderr)
            self.assertEqual(normal.stdout, utf16.stdout)
            output = root / "report.json"
            first = subprocess.run(
                [sys.executable, str(TOOL), str(source), "-o", str(output)],
                check=False,
                capture_output=True,
            )
            second = subprocess.run(
                [sys.executable, str(TOOL), str(source), "-o", str(output)],
                check=False,
                capture_output=True,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 2)
            self.assertIn(b"File exists", second.stderr)


if __name__ == "__main__":
    unittest.main()
