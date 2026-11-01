#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools" / "uk_fw"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import appdmclient_appupgrade_launch_routing as model  # noqa: E402

ROOTFS = ROOT / "work" / "decrypted-eu-260128" / "HU" / "images" / "mango-rootfs.tar.gz"
APPDM = ROOT / "work" / "decrypted-eu-260128" / "extracted-partial-bsdtar" / "mango-rootfs" / "app" / "bin" / "AppDMClient"
MANIFEST = ROOT / "evidence" / "artifacts" / "update-candidates" / "appdmclient-appupgrade-launch-routing-manifest.json"
REPORT = ROOT / "evidence" / "artifacts" / "update-candidates" / "appdmclient-appupgrade-launch-routing-report.json"
SCRIPT = TOOLS / "appdmclient_appupgrade_launch_routing.py"
OBJDUMP = Path("/opt/homebrew/opt/llvm/bin/llvm-objdump")
READELF = Path("/opt/homebrew/opt/llvm/bin/llvm-readelf")


class AppDMClientAppUpgradeLaunchRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        required = (ROOTFS, APPDM, MANIFEST, REPORT, OBJDUMP, READELF)
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise unittest.SkipTest("exact audit inputs unavailable: " + ", ".join(missing))
        cls.expected = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.actual = model.analyze(ROOTFS, APPDM, MANIFEST, OBJDUMP, READELF)
        cls.manifest_raw = MANIFEST.read_bytes()
        cls.manifest_obj = json.loads(cls.manifest_raw)

    def _write_manifest(self, directory: Path, value: object) -> Path:
        path = directory / "manifest.json"
        path.write_bytes((json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8"))
        return path

    def test_exact_report_matches_retained_evidence(self) -> None:
        self.assertEqual(self.actual, self.expected)
        raw = REPORT.read_bytes()
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"\r", raw)
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "7584e9a7f4107f451bd690e05babefb60f6d20928ab27c5eb3efe4eb310b2449",
        )

    def test_helper_abi_and_four_callers_are_exact(self) -> None:
        contract = self.actual["static_contract"]
        helper = contract["launch_proxy"]
        self.assertEqual(helper["fde"], ["0x8c0c0", "0x8c2ab"])
        self.assertEqual(helper["logical_argument_types"], ["int", "QString", "QString"])
        self.assertEqual(helper["variant_type_tags"], [2, 10, 10])
        self.assertTrue(helper["variant_order_matches_logical_order"])
        callers = contract["direct_callers"]
        self.assertEqual([row["call_site"] for row in callers], [
            "0x71a0a", "0x818f6", "0x8201d", "0x8817e"
        ])
        self.assertEqual({row["app_id"] for row in callers}, {300})
        self.assertEqual({row["first_qstring_role"] for row in callers}, {"fixed-AppUpgrade-name"})

    def test_stack_slot_correction_and_terminal_selection_are_preserved(self) -> None:
        contract = self.actual["static_contract"]
        bindings = contract["staging_path_bindings"]
        self.assertFalse(bindings["stack_slot_0x8_is_source_root"])
        self.assertIn("source-root", bindings["source_executable_local"])
        self.assertIn("fixed-staged-base", bindings["staged_executable_local"])
        selection = contract["staging_terminal_selection"]
        self.assertFalse(selection["staged_executable_existence_is_common_gate"])
        self.assertTrue(selection["staged_existence_true_adds_permission_handling"])
        self.assertEqual(selection["marker_present"]["request_call_site"], "0x8201d")
        self.assertEqual(selection["marker_present"]["executable_role"], "source-root-derived-AppUpgrade-path")
        self.assertEqual(selection["marker_absent"]["validator_true_request_call_site"], "0x818f6")
        self.assertEqual(selection["marker_absent"]["validator_true_executable_role"], "staged-AppUpgrade-path")
        self.assertIsNone(selection["marker_absent"]["validator_false_request"])

    def test_runtime_claims_remain_unknown_and_unpromoted(self) -> None:
        self.assertTrue(all(value is None for value in self.actual["runtime_observations"].values()))
        classification = self.actual["classification"]
        self.assertFalse(classification["runtime_delivery_or_execution_established"])
        self.assertFalse(classification["root_or_persistence_established"])

    def test_report_is_privacy_safe(self) -> None:
        raw = REPORT.read_bytes()
        for forbidden in (
            str(ROOT).encode(), str(ROOTFS).encode(), str(APPDM).encode(),
            b"work/decrypted", b"/Users/", b"pgrep -x", b"asyncCallWithArgumentList",
        ):
            self.assertNotIn(forbidden, raw)

    def test_manifest_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_bytes(b'{"schema_version":1,"schema_version":1}')
            with self.assertRaisesRegex(model.BoundaryError, "duplicate JSON key"):
                model.load_manifest(path)

    def test_manifest_rejects_boolean_as_integer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            value = json.loads(self.manifest_raw)
            value["artifact"]["size"] = True
            path = self._write_manifest(Path(tmp), value)
            with self.assertRaisesRegex(model.BoundaryError, "non-Boolean integer"):
                model.load_manifest(path)

    def test_manifest_rejects_schema_and_anchor_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            value = json.loads(self.manifest_raw)
            value["unexpected"] = 1
            with self.assertRaisesRegex(model.BoundaryError, "keys mismatch"):
                model.load_manifest(self._write_manifest(directory, value))
            value = json.loads(self.manifest_raw)
            value["expected"]["anchors"][0]["sha256"] = "0" * 64
            path = self._write_manifest(directory, value)
            with self.assertRaisesRegex(model.BoundaryError, "machine-anchor identity drift"):
                model.analyze(ROOTFS, APPDM, path, OBJDUMP, READELF)

    def test_manifest_rejects_direct_transfer_and_literal_shape_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            value = json.loads(self.manifest_raw)
            value["expected"]["direct_transfers"][0]["calls"].pop()
            with self.assertRaisesRegex(model.BoundaryError, "direct-transfer expectation drift"):
                model.load_manifest(self._write_manifest(directory, value))
            value = json.loads(self.manifest_raw)
            value["expected"]["literals"][0]["length"] += 1
            with self.assertRaisesRegex(model.BoundaryError, "literal role/range drift"):
                model.load_manifest(self._write_manifest(directory, value))

    def test_manifest_rejects_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            alias = Path(tmp) / "manifest-link.json"
            alias.symlink_to(MANIFEST)
            with self.assertRaisesRegex(model.BoundaryError, "linked, aliased, or non-regular"):
                model.load_manifest(alias)

    def test_rootfs_replacement_between_hash_and_member_stream_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            rootfs = directory / "rootfs.tar.gz"
            original = directory / "original.tar.gz"
            rootfs.write_bytes(b"stable descriptor test")

            def replace_path(_handle: object) -> bytes:
                rootfs.replace(original)
                rootfs.write_bytes(b"replacement pathname")
                return b""

            with mock.patch.object(model, "_canonical_member", side_effect=replace_path):
                with self.assertRaisesRegex(
                    model.BoundaryError, "changed during hash/member streaming"
                ):
                    model._canonical_rootfs_snapshot(rootfs)

    def test_cli_is_fixed_lf_under_hostile_encoding(self) -> None:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-16"
        completed = subprocess.run([
            sys.executable, str(SCRIPT),
            "--rootfs", str(ROOTFS),
            "--appdmclient", str(APPDM),
            "--manifest", str(MANIFEST),
            "--llvm-objdump", str(OBJDUMP),
            "--llvm-readelf", str(READELF),
        ], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8", "replace"))
        self.assertEqual(completed.stderr, b"")
        self.assertEqual(completed.stdout, REPORT.read_bytes())
        self.assertNotIn(b"\r", completed.stdout)


if __name__ == "__main__":
    unittest.main()
