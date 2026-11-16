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


TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "bench_carplay_readiness.py"
SPEC = importlib.util.spec_from_file_location("bench_carplay_readiness", TOOL)
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


def label(value: str) -> dict[str, object]:
    return {"state": "present", "provider": "getfattr", "value": value}


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
            "units": {
                "carplay_iAP2.service": (
                    "LoadState=loaded;ActiveState=active;SubState=running;"
                    "UnitFileState=enabled;"
                ),
                "carplay_mdnsd.service": (
                    "LoadState=loaded;ActiveState=active;SubState=running;"
                    "UnitFileState=enabled;"
                ),
            },
            "processes": [
                {
                    "pid": 42,
                    "uid": 0,
                    "gid": 0,
                    "smack_label": "App::projection",
                    "exe": "/app/bin/iAP2Service-2.0",
                    "comm": "iAP2Service-2.",
                    "cmdline": "/app/bin/iAP2Service-2.0 ",
                }
            ],
            "process_credentials": {
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
            },
            "process_security": {
                "42": {
                    "ppid": 1,
                    "cap_inheritable": {"hex": "0", "value": 0, "names": []},
                    "cap_permitted": {"hex": "0", "value": 0, "names": []},
                    "cap_effective": {"hex": "0", "value": 0, "names": []},
                    "cap_bounding": {"hex": "0", "value": 0, "names": []},
                    "cap_ambient": None,
                    "no_new_privs": None,
                    "seccomp": 0,
                }
            },
            "files": {
                "/dev/mfd-iap2": "present|660|0|0|0|character special file|f4|0|",
                "/dev/ttyIAP20": "present|660|0|0|0|character special file|f5|0|",
                "/dev/i2c-1": "present|660|0|0|0|character special file|59|1|",
            },
            "smack_xattrs": {
                "/app/bin/iAP2Service-2.0": {"SMACK64": label("App::projection")},
                "/dev/mfd-iap2": {"SMACK64": label("System::iap20")},
                "/dev/ttyIAP20": {"SMACK64": label("System::iap20")},
            },
            "modules": [
                "usb_f_ncm 16384 0 - Live 0xffffffffa0000000",
                "usb_f_iap2 16384 0 - Live 0xffffffffa0010000",
                "mfd_iap2 16384 0 - Live 0xffffffffa0020000",
            ],
            "listeners": [
                "udp UNCONN 0 0 0.0.0.0:5353 0.0.0.0:* users:((\"mdnsd\",pid=43,fd=4))",
                "tcp LISTEN 0 10 0.0.0.0:7000 0.0.0.0:* users:((\"AppProjection\",pid=44,fd=7))",
            ],
        },
        "warnings": [],
    }
    return seal(report)


class BenchCarplayReadinessTests(unittest.TestCase):
    def test_positive_report_observes_prerequisites_not_cve_or_root(self) -> None:
        result = MODULE.assess(positive_report())
        self.assertEqual(result["schema"], MODULE.OUTPUT_SCHEMA)
        verdict = result["verdict"]
        self.assertTrue(verdict["installed_reference_stack_matches"])
        self.assertTrue(verdict["active_wired_carplay_prerequisites_observed"])
        self.assertTrue(verdict["configured_uid_zero_and_projection_process_observed"])
        self.assertTrue(verdict["iap2_device_boundary_observed"])
        self.assertTrue(verdict["alternate_tty_iap2_endpoint_observed"])
        self.assertTrue(verdict["mfi_auth_i2c_transport_observed"])
        self.assertTrue(verdict["transport_modules_observed"])
        self.assertTrue(verdict["airplay_port_7000_observed"])
        for key in (
            "exact_public_cve_code_match_established",
            "phone_to_parser_delivery_observed",
            "malformed_protocol_input_sent",
            "crash_observed",
            "code_execution_observed",
            "unrestricted_root_access_demonstrated",
            "persistence_demonstrated",
        ):
            self.assertFalse(verdict[key])
        subject = dict(result)
        digest = subject.pop("canonical_sha256")
        self.assertEqual(hashlib.sha256(canonical_bytes(subject)).hexdigest(), digest)

    def test_inactive_service_preserves_identity_but_blocks_active_prerequisites(self) -> None:
        report = positive_report()
        report["facts"]["units"]["carplay_iAP2.service"] = (
            "LoadState=loaded;ActiveState=inactive;SubState=dead;UnitFileState=enabled;"
        )
        result = MODULE.assess(seal(report))
        self.assertTrue(result["verdict"]["installed_reference_stack_matches"])
        self.assertFalse(result["verdict"]["active_wired_carplay_prerequisites_observed"])
        statuses = {gate["id"]: gate["status"] for gate in result["gates"]}
        self.assertEqual(statuses["unit.carplay_iAP2.service.loaded"], "pass")
        self.assertEqual(statuses["unit.carplay_iAP2.service.active"], "fail")

    def test_identity_mismatch_fails_installed_and_active_verdicts(self) -> None:
        report = positive_report()
        report["facts"]["hashes"]["/app/lib/libAirPlay.so"] = "b" * 64
        result = MODULE.assess(seal(report))
        self.assertFalse(result["verdict"]["installed_reference_stack_matches"])
        self.assertFalse(result["verdict"]["active_wired_carplay_prerequisites_observed"])
        mismatches = [
            gate for gate in result["gates"]
            if gate["status"] == "fail" and gate["observed"] == {
                "path": "/app/lib/libAirPlay.so", "sha256": "b" * 64
            }
        ]
        self.assertEqual(len(mismatches), 1)

    def test_process_label_and_device_label_mismatch_fail_closed(self) -> None:
        report = positive_report()
        report["facts"]["processes"][0]["smack_label"] = "App::other"
        report["facts"]["smack_xattrs"]["/dev/mfd-iap2"]["SMACK64"] = label(
            "System::other"
        )
        result = MODULE.assess(seal(report))
        statuses = {gate["id"]: gate["status"] for gate in result["gates"]}
        self.assertEqual(statuses["process.iap2_service"], "fail")
        self.assertEqual(statuses["smack.mfd-iap2"], "fail")
        self.assertFalse(result["verdict"]["active_wired_carplay_prerequisites_observed"])
        self.assertFalse(result["verdict"]["unrestricted_root_access_demonstrated"])

    def test_missing_new_capture_fields_remain_unknown_or_inactive(self) -> None:
        report = positive_report()
        report["facts"] = {
            "hashes": {},
            "units": {},
            "files": {},
            "smack_xattrs": {},
            "process_credentials": {},
            "process_security": {},
            "processes": [],
            "modules": [],
            "listeners": [],
        }
        result = MODULE.assess(seal(report))
        statuses = {gate["id"]: gate["status"] for gate in result["gates"]}
        self.assertEqual(statuses["capture.complete"], "pass")
        self.assertEqual(statuses["transport.modules"], "unknown")
        self.assertEqual(statuses["listener.airplay_7000"], "unknown")
        self.assertEqual(statuses["device.i2c-1"], "unknown")
        self.assertEqual(statuses["process.iap2_service"], "fail")
        self.assertFalse(result["verdict"]["installed_reference_stack_matches"])
        self.assertFalse(result["verdict"]["active_wired_carplay_prerequisites_observed"])

    def test_wrong_device_kind_and_missing_modules_block_active_gate(self) -> None:
        report = positive_report()
        report["facts"]["files"]["/dev/mfd-iap2"] = (
            "present|600|0|0|10|regular file|0|0|"
        )
        report["facts"]["modules"] = [
            "usb_f_ncm 16384 0 - Live 0xffffffffa0000000"
        ]
        result = MODULE.assess(seal(report))
        statuses = {gate["id"]: gate["status"] for gate in result["gates"]}
        self.assertEqual(statuses["device.mfd-iap2"], "fail")
        self.assertEqual(statuses["transport.modules"], "fail")
        self.assertFalse(result["verdict"]["active_wired_carplay_prerequisites_observed"])

    def test_duplicate_nonfinite_bad_digest_symlink_and_oversize_are_rejected(self) -> None:
        with self.assertRaisesRegex(MODULE.AssessmentError, "duplicate"):
            MODULE.load_report_bytes(b'{"schema":"ioniq-bench-state/v1","schema":"x"}')
        with self.assertRaisesRegex(MODULE.AssessmentError, "non-finite"):
            MODULE.load_report_bytes(b'{"schema":"ioniq-bench-state/v1","x":NaN}')
        report = positive_report()
        report["canonical_sha256"] = "0" * 64
        with self.assertRaisesRegex(MODULE.AssessmentError, "canonical_sha256 mismatch"):
            MODULE.load_report_bytes(json.dumps(report).encode())
        with self.assertRaisesRegex(MODULE.AssessmentError, "strict UTF-8"):
            MODULE.load_report_bytes(b"\xff")
        with self.assertRaisesRegex(MODULE.AssessmentError, "exceeds"):
            MODULE.load_report_bytes(b" " * (MODULE.MAX_INPUT_BYTES + 1))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.json"
            target.write_text(json.dumps(positive_report()), encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(OSError):
                MODULE.load_report(link)

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
