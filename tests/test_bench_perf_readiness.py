from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
PRODUCER_PATH = ROOT / "tools" / "uk_fw" / "bench_state_bundle.py"
TOOL_PATH = ROOT / "tools" / "uk_fw" / "bench_perf_readiness.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRODUCER = load_module("bench_state_bundle_for_perf", PRODUCER_PATH)
TOOL = load_module("bench_perf_readiness", TOOL_PATH)


def framed_record(key: str, value: str) -> str:
    return f"@@R|{key}|{value.encode('utf-8').hex()}"


def parsed_capture(identity: list[tuple[str, str]]) -> dict:
    records = {name: [] for name in PRODUCER.EXPECTED_SECTIONS}
    records["meta"] = [("schema", PRODUCER.SCHEMA)]
    records["identity"] = identity
    records["complete"] = [("result", "complete")]
    lines: list[str] = []
    for section in PRODUCER.EXPECTED_SECTIONS:
        lines.append(f"@@IONIQ_BENCH_STATE_V1|BEGIN|{section}@@")
        lines.extend(framed_record(key, value) for key, value in records[section])
        lines.append(f"@@IONIQ_BENCH_STATE_V1|END|{section}|0@@")
    return PRODUCER.parse_capture(("\n".join(lines) + "\n").encode())


def positive_identity() -> list[tuple[str, str]]:
    return [
        ("uname", "Linux bench 4.1.27-abl #1 SMP x86_64 GNU/Linux"),
        ("perf-event-paranoid", "1"),
        ("perf-event-source", "software|present|1|absent||absent|"),
        (
            "perf-event-source",
            "cpu|present|4|absent||present|../../../devices/cpu",
        ),
        ("perf-event-source-count", "2"),
    ]


class BenchPerfReadinessTests(unittest.TestCase):
    def test_emitted_probe_inventory_is_passive_and_audited(self) -> None:
        script = PRODUCER.PROBE_SCRIPT
        self.assertIn("for I_PERF_DIR in /sys/bus/event_source/devices/*", script)
        self.assertIn('record perf-event-source "$I_PERF_NAME|$I_PERF_TYPE_STATE|$I_PERF_TYPE|$I_PERF_CPUMASK_STATE|$I_PERF_CPUMASK|$I_PERF_DEVICE_STATE|$I_PERF_DEVICE"', script)
        self.assertIn('record perf-event-source-count "$I_PERF_SOURCE_COUNT"', script)
        self.assertNotIn("perf stat", script)
        self.assertEqual(
            [line for line in script.splitlines() if "perf_event_open" in line],
            ["# perf_event_open, create an event, enable a PMU, or write sysfs."],
        )
        self.assertEqual(PRODUCER.audit_script(script), [])
        ok, error = PRODUCER.shell_syntax_check(script)
        self.assertTrue(ok, error)

    def test_positive_capture_binds_only_passive_prerequisites(self) -> None:
        report = TOOL.build_report(parsed_capture(positive_identity()))
        self.assertEqual(report["schema"], TOOL.OUTPUT_SCHEMA)
        self.assertTrue(report["observations"]["kernel_banner_match"])
        self.assertEqual(report["observations"]["perf_event_paranoid"], 1)
        self.assertFalse(report["observations"]["cpu_wide_without_capability_allowed_by_v4_1_paranoid_check"])
        self.assertTrue(report["observations"]["kernel_sampling_without_capability_allowed_by_v4_1_paranoid_check"])
        self.assertTrue(report["observations"]["per_task_user_space_not_blanket_denied_by_v4_1_paranoid_checks"])
        self.assertEqual(report["observations"]["event_sources"]["software"]["type"], 1)
        self.assertEqual(report["observations"]["event_sources"]["cpu"]["type"], 4)
        gates = {item["id"]: item["status"] for item in report["gates"]}
        self.assertEqual(gates, {
            "kernel-banner": "pass",
            "per-task-policy": "pass",
            "software-event-source": "pass",
            "cpu-event-source": "pass",
        })
        candidate = report["candidate_runtime_gates"]
        self.assertTrue(candidate["passive_policy_and_event_sources_observed"])
        for name in (
            "installed_kernel_exact_identity",
            "perf_event_open_syscall_acceptance",
            "compatible_software_group_and_hardware_event_acceptance",
            "concurrent_move_group_race",
            "stale_or_dead_context_use",
            "controlled_kernel_memory_corruption",
            "privilege_escalation",
            "unrestricted_root",
            "persistence",
        ):
            self.assertIsNone(candidate[name])

    def test_negative_and_missing_capture_states_remain_separate(self) -> None:
        negative = parsed_capture([
            ("uname", "Linux bench 5.10.0 #1 SMP x86_64 GNU/Linux"),
            ("perf-event-paranoid", "3"),
            ("perf-event-source", "software|present|1|absent||absent|"),
            ("perf-event-source-count", "1"),
        ])
        report = TOOL.build_report(negative)
        gates = {item["id"]: item["status"] for item in report["gates"]}
        self.assertEqual(gates["kernel-banner"], "fail")
        self.assertEqual(gates["per-task-policy"], "pass")
        self.assertFalse(report["observations"]["cpu_wide_without_capability_allowed_by_v4_1_paranoid_check"])
        self.assertFalse(report["observations"]["kernel_sampling_without_capability_allowed_by_v4_1_paranoid_check"])
        self.assertEqual(gates["software-event-source"], "pass")
        self.assertEqual(gates["cpu-event-source"], "fail")
        self.assertFalse(report["candidate_runtime_gates"]["passive_policy_and_event_sources_observed"])

        missing = TOOL.build_report(parsed_capture([]))
        self.assertIsNone(missing["observations"]["kernel_banner_match"])
        self.assertIsNone(missing["observations"]["perf_event_paranoid"])
        self.assertFalse(missing["observations"]["event_source_inventory_observed"])
        self.assertIsNone(missing["candidate_runtime_gates"]["passive_policy_and_event_sources_observed"])

    def test_malformed_duplicate_and_nonfinite_inputs_fail_closed(self) -> None:
        mismatch = parsed_capture([
            ("perf-event-source", "software|present|1|absent||absent|"),
            ("perf-event-source-count", "2"),
        ])
        with self.assertRaisesRegex(TOOL.AssessmentError, "count mismatch"):
            TOOL.build_report(mismatch)

        duplicate_source = parsed_capture([
            ("perf-event-source", "cpu|present|4|absent||absent|"),
            ("perf-event-source", "cpu|present|4|absent||absent|"),
            ("perf-event-source-count", "2"),
        ])
        with self.assertRaisesRegex(TOOL.AssessmentError, "duplicate perf event source"):
            TOOL.build_report(duplicate_source)

        with self.assertRaisesRegex(TOOL.AssessmentError, "duplicate JSON object key"):
            TOOL.load_report_bytes(b'{"a":1,"a":2}')
        with self.assertRaisesRegex(TOOL.AssessmentError, "non-finite JSON constant"):
            TOOL.load_report_bytes(b'{"x":NaN}')

    def test_deterministic_output_and_exclusive_creation(self) -> None:
        source = parsed_capture(positive_identity())
        report_a = TOOL.build_report(source)
        report_b = TOOL.build_report(source)
        self.assertEqual(report_a, report_b)
        subject = dict(report_a)
        supplied = subject.pop("canonical_sha256")
        self.assertEqual(supplied, __import__("hashlib").sha256(TOOL._canonical_bytes(subject)).hexdigest())

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "input.json"
            output_path = root / "output.json"
            input_path.write_text(json.dumps(source, sort_keys=True), encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(TOOL_PATH), str(input_path), "-o", str(output_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            first = output_path.read_bytes()
            json.loads(first.decode("ascii"))
            second = subprocess.run(
                [sys.executable, str(TOOL_PATH), str(input_path), "-o", str(output_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("cannot create output exclusively", second.stderr)
            self.assertEqual(output_path.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
