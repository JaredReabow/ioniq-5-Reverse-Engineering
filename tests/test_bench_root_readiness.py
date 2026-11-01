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


TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "bench_root_readiness.py"
SPEC = importlib.util.spec_from_file_location("bench_root_readiness", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def seal(report: dict[str, object]) -> dict[str, object]:
    result = copy.deepcopy(report)
    result.pop("canonical_sha256", None)
    result["canonical_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    return result


def cap(names: list[str], value: int = 0) -> dict[str, object]:
    return {"hex": f"{value:016x}", "value": value, "names": names}


def positive_report() -> dict[str, object]:
    files = {
        MODULE.ANCHOR: "present|700|0|0|3933|regular file|0|0|",
        "/bin/sh": "present|777|0|0|9|symbolic link|0|0|/bin/bash",
        "/bin/bash": "present|755|0|0|946216|regular file|0|0|",
        "/lib/ld-linux-x86-64.so.2": "present|777|0|0|10|symbolic link|0|0|ld-2.25.so",
        "/lib/ld-2.25.so": "present|755|0|0|149184|regular file|0|0|",
        "/bin/date": "present|777|0|0|7|symbolic link|0|0|busybox",
    }
    xattrs = {
        MODULE.ANCHOR: {
            "SMACK64": {"state": "present", "provider": "getfattr", "value": "_"},
            "SMACK64EXEC": {
                "state": "present",
                "provider": "getfattr",
                "value": "Privileged",
            },
        },
        "/bin/date": {
            "SMACK64": {"state": "present", "provider": "getfattr", "value": "_"},
            "SMACK64EXEC": {
                "state": "attribute-absent",
                "provider": "getfattr",
                "value": "",
            },
        },
    }
    hashes = {
        MODULE.ANCHOR: MODULE.ANCHOR_SHA256,
        "/bin/sh": MODULE.BASH_SHA256,
        "/bin/bash": MODULE.BASH_SHA256,
        "/lib/ld-linux-x86-64.so.2": MODULE.LOADER_SHA256,
        "/lib/ld-2.25.so": MODULE.LOADER_SHA256,
        "/bin/date": "1" * 64,
        "/usr/bin/date": "absent",
    }
    credentials = {
        "42": {
            "ruid": 0,
            "euid": 0,
            "suid": 0,
            "fsuid": 0,
            "rgid": 0,
            "egid": 0,
            "sgid": 0,
            "fsgid": 0,
            "supplementary_groups": [],
        }
    }
    security = {
        "42": {
            "ppid": 1,
            "cap_inheritable": cap([], 0),
            "cap_permitted": cap(
                ["CAP_MAC_OVERRIDE", "CAP_MAC_ADMIN"], (1 << 32) | (1 << 33)
            ),
            "cap_effective": cap(
                ["CAP_MAC_OVERRIDE", "CAP_MAC_ADMIN"], (1 << 32) | (1 << 33)
            ),
            "cap_bounding": cap(
                ["CAP_MAC_OVERRIDE", "CAP_MAC_ADMIN"], (1 << 32) | (1 << 33)
            ),
            "cap_ambient": None,
            "no_new_privs": None,
            "seccomp": 0,
        }
    }
    report: dict[str, object] = {
        "schema": MODULE.INPUT_SCHEMA,
        "capture_sha256": "a" * 64,
        "capture_bytes": 1234,
        "complete": True,
        "section_order": list(MODULE.EXPECTED_SECTION_ORDER),
        "sections": [
            {
                "name": "smack",
                "complete": True,
                "end_status": 0,
                "records": [
                    {"key": "smack-onlycap", "value": "Privileged"},
                    {"key": "smack-rule", "value": "App::home _ rwx---"},
                    {
                        "key": "smack-mounts",
                        "value": "/dev/mmcblk0p3 / ext4 ro,relatime 0 0",
                    },
                ],
            }
        ],
        "facts": {
            "hashes": hashes,
            "files": files,
            "smack_xattrs": xattrs,
            "processes": [
                {
                    "pid": 42,
                    "uid": 0,
                    "gid": 0,
                    "smack_label": "App::home",
                    "exe": "/app/bin/AppHomeScreen",
                    "comm": "AppHomeScreen",
                    "cmdline": "/app/bin/AppHomeScreen",
                }
            ],
            "process_credentials": credentials,
            "process_security": security,
            "process_paths": {"42": "/usr/bin:/bin"},
        },
        "warnings": [],
    }
    return seal(report)


class BenchRootReadinessTests(unittest.TestCase):
    def test_positive_report_keeps_transition_and_override_separate(self) -> None:
        report = positive_report()
        result = MODULE.assess(report)
        self.assertEqual(result["schema"], MODULE.OUTPUT_SCHEMA)
        self.assertTrue(result["verdict"]["runtime_chain_prerequisites_observed"])
        self.assertTrue(
            result["verdict"]["effective_mac_override_prerequisites_observed"]
        )
        self.assertFalse(result["verdict"]["credential_commit_observed"])
        self.assertFalse(result["verdict"]["complete_interpreter_loading_observed"])
        self.assertFalse(result["verdict"]["root_access_demonstrated"])
        self.assertFalse(result["verdict"]["persistence_demonstrated"])
        gates = {item["id"]: item for item in result["gates"]}
        self.assertTrue(all(item["status"] == "pass" for item in gates.values()))
        self.assertEqual(result["gate_counts"], {"fail": 0, "pass": 10, "unknown": 0})
        self.assertEqual(
            result["callers"][0]["mac_capability_prerequisite"]["matching"],
            ["CAP_MAC_ADMIN", "CAP_MAC_OVERRIDE"],
        )
        subject = dict(result)
        digest = subject.pop("canonical_sha256")
        self.assertEqual(hashlib.sha256(canonical_bytes(subject)).hexdigest(), digest)

    def test_missing_runtime_observations_remain_unknown(self) -> None:
        report = positive_report()
        report["complete"] = False
        report["warnings"] = ["capture truncated"]
        report["facts"] = {}
        report["sections"] = []
        report = seal(report)
        result = MODULE.assess(report)
        gates = {item["id"]: item["status"] for item in result["gates"]}
        self.assertEqual(gates["capture.complete"], "fail")
        for gate_id in (
            "anchor.identity",
            "anchor.metadata",
            "anchor.smack64",
            "anchor.smack64exec",
            "interpreter.bash_identity",
            "interpreter.loader_identity",
            "smack.onlycap",
            "mount.anchor_exec",
            "source.app_domain_task",
        ):
            self.assertEqual(gates[gate_id], "unknown")
        self.assertFalse(result["verdict"]["runtime_chain_prerequisites_observed"])

    def test_noncanonical_section_order_fails_capture_gate(self) -> None:
        report = positive_report()
        report["section_order"] = ["meta", "smack", "complete"]
        report = seal(report)
        result = MODULE.assess(report)
        gate = next(item for item in result["gates"] if item["id"] == "capture.complete")
        self.assertEqual(gate["status"], "fail")

    def test_identity_mismatch_fails_without_becoming_root_claim(self) -> None:
        report = positive_report()
        report["facts"]["hashes"][MODULE.ANCHOR] = "b" * 64
        report = seal(report)
        result = MODULE.assess(report)
        gate = next(item for item in result["gates"] if item["id"] == "anchor.identity")
        self.assertEqual(gate["status"], "fail")
        self.assertFalse(result["verdict"]["runtime_chain_prerequisites_observed"])
        self.assertFalse(result["verdict"]["root_access_demonstrated"])

    def test_anchor_label_mismatch_and_query_error_are_distinct(self) -> None:
        report = positive_report()
        report["facts"]["smack_xattrs"][MODULE.ANCHOR]["SMACK64"]["value"] = "App::upgrade"
        report["facts"]["smack_xattrs"][MODULE.ANCHOR]["SMACK64EXEC"] = {
            "state": "query-error",
            "provider": "getfattr",
            "value": "status=13",
        }
        report = seal(report)
        result = MODULE.assess(report)
        gates = {item["id"]: item["status"] for item in result["gates"]}
        self.assertEqual(gates["anchor.smack64"], "fail")
        self.assertEqual(gates["anchor.smack64exec"], "unknown")

    def test_onlycap_mismatch_fails(self) -> None:
        report = positive_report()
        report["sections"][0]["records"][0]["value"] = "OtherLabel"
        report = seal(report)
        result = MODULE.assess(report)
        gate = next(item for item in result["gates"] if item["id"] == "smack.onlycap")
        self.assertEqual(gate["status"], "fail")

    def test_policy_requires_read_and_execute(self) -> None:
        report = positive_report()
        report["sections"][0]["records"][1]["value"] = "App::home _ r-----"
        report = seal(report)
        result = MODULE.assess(report)
        caller = result["callers"][0]
        self.assertEqual(caller["policy_to_floor"]["status"], "fail")
        source = next(
            item for item in result["gates"] if item["id"] == "source.app_domain_task"
        )
        self.assertEqual(source["status"], "fail")

    def test_capability_absence_does_not_reject_label_transition(self) -> None:
        report = positive_report()
        report["facts"]["process_security"]["42"]["cap_effective"] = cap(
            ["CAP_SYS_ADMIN"], 1 << 21
        )
        report = seal(report)
        result = MODULE.assess(report)
        self.assertTrue(result["verdict"]["runtime_chain_prerequisites_observed"])
        self.assertFalse(
            result["verdict"]["effective_mac_override_prerequisites_observed"]
        )
        self.assertEqual(
            result["callers"][0]["mac_capability_prerequisite"]["status"], "fail"
        )

    def test_incomplete_security_record_is_unknown_not_zero(self) -> None:
        for mutation in ("missing", "inconsistent"):
            with self.subTest(mutation=mutation):
                report = positive_report()
                security = report["facts"]["process_security"]["42"]
                if mutation == "missing":
                    del security["cap_bounding"]
                else:
                    security["cap_effective"]["value"] = 0
                report = seal(report)
                result = MODULE.assess(report)
                caller = result["callers"][0]
                self.assertEqual(caller["security_status"], "unknown")
                self.assertFalse(caller["runtime_source_prerequisites_observed"])
                self.assertFalse(result["verdict"]["runtime_chain_prerequisites_observed"])

    def test_covering_mount_noexec_fails(self) -> None:
        report = positive_report()
        report["sections"][0]["records"].append(
            {
                "key": "smack-mounts",
                "value": "/dev/mmcblk0p9 /etc ext4 ro,noexec 0 0",
            }
        )
        report = seal(report)
        result = MODULE.assess(report)
        gate = next(item for item in result["gates"] if item["id"] == "mount.anchor_exec")
        self.assertEqual(gate["status"], "fail")
        self.assertEqual(gate["observed"]["mountpoint"], "/etc")

    def test_fixed_date_observation_does_not_claim_path_resolution(self) -> None:
        result = MODULE.assess(positive_report())
        date = result["fixed_date_observations"][0]
        self.assertEqual(date["path"], "/bin/date")
        self.assertEqual(date["hash"], "1" * 64)
        self.assertNotIn("resolved", date)
        self.assertTrue(
            any("do not prove runtime PATH resolution" in line for line in result["limits"])
        )

    def test_load_rejects_duplicate_keys_wrong_hash_and_bad_digest(self) -> None:
        with self.assertRaisesRegex(MODULE.AssessmentError, "duplicate JSON object key"):
            MODULE.load_report_bytes(
                b'{"schema":"ioniq-bench-state/v1","schema":"ioniq-bench-state/v1"}'
            )
        report = positive_report()
        report["canonical_sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.AssessmentError, "canonical_sha256 mismatch"):
            MODULE.load_report_bytes(json.dumps(report).encode())
        report = positive_report()
        report["capture_sha256"] = "NOT-A-DIGEST"
        report = seal(report)
        with self.assertRaisesRegex(MODULE.AssessmentError, "capture_sha256"):
            MODULE.load_report_bytes(json.dumps(report).encode())

    def test_load_rejects_non_finite_and_oversized_input(self) -> None:
        with self.assertRaisesRegex(MODULE.AssessmentError, "non-finite"):
            MODULE.load_report_bytes(b'{"schema":NaN}')
        with self.assertRaisesRegex(MODULE.AssessmentError, "byte limit"):
            MODULE.load_report_bytes(b" " * (MODULE.MAX_INPUT_BYTES + 1))

    def test_cli_is_deterministic_under_hostile_pythonioencoding(self) -> None:
        report = positive_report()
        payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "state.json"
            source.write_bytes(payload)
            command = [sys.executable, "-B", str(TOOL), str(source)]
            normal = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            hostile = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONIOENCODING": "utf-16"},
                check=False,
            )
        self.assertEqual(normal.returncode, 0, normal.stderr)
        self.assertEqual(hostile.returncode, 0, hostile.stderr)
        self.assertEqual(normal.stderr, b"")
        self.assertEqual(hostile.stderr, b"")
        self.assertEqual(normal.stdout, hostile.stdout)
        self.assertTrue(normal.stdout.endswith(b"\n"))
        self.assertNotIn(b"\r", normal.stdout)
        decoded = json.loads(normal.stdout)
        self.assertEqual(decoded["schema"], MODULE.OUTPUT_SCHEMA)

    def test_cli_output_is_exclusive(self) -> None:
        report = positive_report()
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "state.json"
            target = Path(tmp) / "result.json"
            source.write_text(json.dumps(report), encoding="utf-8")
            first = subprocess.run(
                [sys.executable, "-B", str(TOOL), str(source), "-o", str(target)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            original = target.read_bytes()
            second = subprocess.run(
                [sys.executable, "-B", str(TOOL), str(source), "-o", str(target)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            after_second = target.read_bytes()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 2)
        self.assertIn(b"File exists", second.stderr)
        self.assertEqual(after_second, original)


if __name__ == "__main__":
    unittest.main()
