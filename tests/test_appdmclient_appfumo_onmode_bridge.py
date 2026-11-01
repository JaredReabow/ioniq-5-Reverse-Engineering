"""Tests for the exact-static AppDMClient -> AppFUMO priority-mode bridge."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/uk_fw/appdmclient_appfumo_onmode_bridge.py"
TOOLS_DIR = TOOL.parent
APPDM = ROOT / "work/decrypted-eu-260128/extracted-partial-bsdtar/mango-rootfs/app/bin/AppDMClient"
APPFUMO = ROOT / "work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf"
ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
SESSION_CONF = ROOT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs/etc/dbus-1/session.conf"
MANIFEST = ROOT / "evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-manifest.json"
REPORT = ROOT / "evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge.json"
EXACT_STATIC = ROOT / "evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-exact-static.txt"
ASSESSMENT = ROOT / "evidence/appdmclient-appfumo-onmode-bridge.md"
BREW = shutil.which("brew")
LLVM_BIN = Path(subprocess.check_output([BREW, "--prefix", "llvm"], text=True).strip()) / "bin" if BREW else Path("/nonexistent")
OBJDUMP = LLVM_BIN / "llvm-objdump"
READELF = LLVM_BIN / "llvm-readelf"
EXACT_AVAILABLE = all(path.is_file() for path in (
    APPDM, APPFUMO, ROOTFS, MANIFEST, REPORT, EXACT_STATIC, ASSESSMENT, OBJDUMP, READELF
))

sys.path.insert(0, str(TOOLS_DIR))
SPEC = importlib.util.spec_from_file_location("appdmclient_appfumo_onmode_bridge", TOOL)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def exact_command() -> list[str]:
    return [
        sys.executable, str(TOOL),
        "--appdmclient", str(APPDM),
        "--appfumo", str(APPFUMO),
        "--rootfs", str(ROOTFS),
        "--objdump", str(OBJDUMP),
        "--readelf", str(READELF),
        "--manifest", str(MANIFEST),
    ]


@lru_cache(maxsize=1)
def run_exact_hostile() -> bytes:
    env = dict(os.environ, PYTHONIOENCODING="utf-16:strict")
    completed = subprocess.run(
        exact_command(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    if completed.stderr:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return completed.stdout


class StrictParserAndSafetyTests(unittest.TestCase):
    def test_manifest_accepts_exact_and_rejects_duplicate_keys(self) -> None:
        exact = M.load_manifest(MANIFEST)
        self.assertEqual(exact["manifest_sha256"], "9a3b105a9e5e7bacb3f179f5162b1dfb860caf1cebce2a45c1709e5266f9bc24")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(M.BoundaryError, "duplicate JSON key"):
                M.load_manifest(path)

    def test_manifest_rejects_schema_type_boolean_and_evidence_drift(self) -> None:
        source = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mutations = []
        extra = json.loads(json.dumps(source)); extra["extra"] = 1; mutations.append(extra)
        missing = json.loads(json.dumps(source)); del missing["artifacts"]["appfumo"]["build_id"]; mutations.append(missing)
        boolean = json.loads(json.dumps(source)); boolean["artifacts"]["appdmclient"]["size"] = True; mutations.append(boolean)
        bool_root = json.loads(json.dumps(source)); bool_root["expected"]["rootfs"]["member_count"] = False; mutations.append(bool_root)
        instruction = json.loads(json.dumps(source)); instruction["llvm"]["binaries"]["appfumo"]["instruction_count"] += 1; mutations.append(instruction)
        fde_inventory = json.loads(json.dumps(source)); fde_inventory["llvm"]["binaries"]["appdmclient"]["fde_count"] += 1; mutations.append(fde_inventory)
        fde = json.loads(json.dumps(source)); fde["expected"]["fdes"][0]["end_exclusive"] += 1; mutations.append(fde)
        direct = json.loads(json.dumps(source)); direct["expected"]["direct_transfers"][0]["call_vas"] = []; mutations.append(direct)
        extent = json.loads(json.dumps(source)); extent["expected"]["embedded"]["structural_extent"] += 1; mutations.append(extent)
        offset = json.loads(json.dumps(source)); offset["expected"]["embedded"]["outer_offset"] += 1; mutations.append(offset)
        rootfs = json.loads(json.dumps(source)); rootfs["expected"]["rootfs"]["inventory_sha256"] = "00" * 32; mutations.append(rootfs)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            for index, value in enumerate(mutations):
                with self.subTest(index=index):
                    path.write_text(json.dumps(value), encoding="utf-8")
                    with self.assertRaises(M.BoundaryError):
                        M.load_manifest(path)

    def test_anchor_and_literal_manifest_mutations_fail_against_exact_bytes(self) -> None:
        source = json.loads(MANIFEST.read_text(encoding="utf-8"))
        original = source["expected"]["anchors"][0]
        changed_anchor = dict(original)
        changed_anchor["operands"] += " drift"
        actual = SimpleNamespace(
            address=original["va"], mnemonic=original["mnemonic"], operands=original["operands"]
        )
        with self.assertRaisesRegex(M.BoundaryError, "machine anchor drift"):
            M._validate_anchor_rows(original["binary"], [actual], [changed_anchor])

        changed = json.loads(json.dumps(source))
        changed["expected"]["literals"][0]["sha256"] = "00" * 32
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            manifest = M.load_manifest(path)
            with self.assertRaisesRegex(M.BoundaryError, "literal identity drift"):
                M._literal_bindings(
                    {"appdmclient": APPDM.read_bytes(), "appfumo": APPFUMO.read_bytes()}, manifest
                )

    def test_manifest_and_artifact_aliases_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            target = directory / "target.json"
            target.write_bytes(MANIFEST.read_bytes())
            alias = directory / "alias.json"
            alias.symlink_to(target.name)
            with self.assertRaisesRegex(M.BoundaryError, "linked, aliased, or non-regular"):
                M.load_manifest(alias)
            hard = directory / "hard.json"
            os.link(target, hard)
            with self.assertRaisesRegex(M.BoundaryError, "linked, aliased, or non-regular"):
                M.load_manifest(target)

    def test_session_config_parser_is_strict_and_separates_permission(self) -> None:
        raw = SESSION_CONF.read_bytes()
        report = M.parse_session_config(raw)
        self.assertEqual(report["bus_type"], "session")
        self.assertEqual(report["authentication"], "EXTERNAL")
        self.assertEqual(report["listener_class"], "unix-temporary-directory")
        self.assertEqual(report["default_send_permission"], "allow")
        self.assertFalse(report["policy_permission_is_socket_reachability"])
        for changed in (
            raw.replace(b"<auth>EXTERNAL</auth>", b"<auth>ANONYMOUS</auth>"),
            raw.replace(b"<type>session</type>", b"<type>system</type>"),
            raw.replace(b"<includedir>session.d</includedir>", b"<includedir>other.d</includedir>"),
            raw.replace(b"<allow own=\"*\"/>", b"<deny own=\"*\"/>"),
            raw + b"<!ENTITY bad 'x'>\n",
        ):
            with self.subTest(change=changed[-40:]):
                with self.assertRaises(M.BoundaryError):
                    M.parse_session_config(changed)

    def test_filter_classification_and_runtime_contradictions_fail_closed(self) -> None:
        self.assertEqual(
            M.classify_receiver_filters(service_empty=True, path_empty=True,
                                        interface_fixed=True, member_fixed=True),
            "wildcard-service-and-path-fixed-interface-and-member",
        )
        self.assertEqual(
            M.classify_receiver_filters(service_empty=False, path_empty=False,
                                        interface_fixed=True, member_fixed=True),
            "fixed-service-path-interface-and-member",
        )
        with self.assertRaises(M.BoundaryError):
            M.classify_receiver_filters(service_empty=1, path_empty=True,
                                        interface_fixed=True, member_fixed=True)
        facts = {
            "same_bus_participation": None, "socket_reachability": None,
            "sender_identity": None, "signal_delivery": None, "slot_execution": None,
            "readiness_success": None, "copy_success": None,
        }
        self.assertEqual(M.validate_runtime_facts(facts), facts)
        facts["signal_delivery"] = True
        with self.assertRaisesRegex(M.BoundaryError, "cannot be promoted"):
            M.validate_runtime_facts(facts)

    def test_tar_name_and_type_primitives_reject_unsafe_aliases(self) -> None:
        self.assertEqual(M._canonical_member_name("./etc/dbus-1/session.conf"), "etc/dbus-1/session.conf")
        for name in ("/absolute", "../escape", "a/../b", "a//b", "a/./b"):
            with self.subTest(name=name):
                with self.assertRaises(M.BoundaryError):
                    M._canonical_member_name(name)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "not-a-rootfs"
            path.write_bytes(b"not a canonical archive")
            manifest = M.load_manifest(MANIFEST)
            with self.assertRaises(M.BoundaryError):
                M.audit_rootfs(path, manifest)

    def test_disassembly_and_fde_parsers_reject_malformed_duplicate_and_truncated_rows(self) -> None:
        with self.assertRaisesRegex(M.BoundaryError, "no decoded instructions"):
            M.parse_disassembly(b"Disassembly of section .text:\n")
        with self.assertRaisesRegex(M.BoundaryError, "duplicate"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10: nop\n  10: retq\n")
        with self.assertRaisesRegex(M.BoundaryError, "malformed or truncated"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10:\n")
        valid = (
            b"  [0x20] FDE length=10 cie=[0x10]\n"
            b"    initial_location: 0x100\n"
            b"    address_range: 0x20 (end : 0x120)\n"
        )
        self.assertEqual(M.parse_fdes(valid), [(0x100, 0x120)])
        with self.assertRaisesRegex(M.BoundaryError, "malformed FDE"):
            M.parse_fdes(valid.replace(b"0x120", b"0x121"))
        with self.assertRaisesRegex(M.BoundaryError, "duplicate"):
            M.parse_fdes(valid + valid)
        with self.assertRaisesRegex(M.BoundaryError, "no FDE"):
            M.parse_fdes(b"truncated\n")

    @unittest.skipUnless(APPFUMO.is_file(), "ignored exact embedded ELF is unavailable")
    def test_structural_extent_is_exact_and_excludes_trailing_data(self) -> None:
        raw = APPFUMO.read_bytes()
        selected = M.parse_elf_at(raw + b"trailing-resource-metadata", 0)
        self.assertEqual(selected.structural_extent, len(raw))
        self.assertEqual(selected.build_id, M.ARTIFACTS["appfumo"]["build_id"])
        self.assertEqual((raw + b"trailing-resource-metadata")[:selected.structural_extent], raw)

    @unittest.skipUnless(all(path.is_file() for path in (APPDM, OBJDUMP, READELF)), "exact ELF or LLVM unavailable")
    def test_binary_and_tool_identity_mutations_fail_before_acceptance(self) -> None:
        manifest = M.load_manifest(MANIFEST)
        raw = bytearray(APPDM.read_bytes())
        raw[-1] ^= 1
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "changed.elf"
            changed.write_bytes(raw)
            with self.assertRaisesRegex(M.BoundaryError, "identity drift"):
                M._analyze_elf("appdmclient", changed, bytes(raw), OBJDUMP, READELF, manifest)
        objdump_raw = OBJDUMP.read_bytes()
        with self.assertRaisesRegex(M.BoundaryError, "file identity"):
            M._validate_tool(OBJDUMP, M.EXPECTED_LLVM["version"], len(objdump_raw), "00" * 32, "llvm-objdump")

    def test_privacy_scanner_rejects_values_paths_and_byte_escapes(self) -> None:
        M._privacy_scan({"normalized": True}, [])
        for report in (
            {"value": "onModePriority"},
            {"value": "/tmp/supplied"},
            {"value": "\\x7fELF"},
        ):
            paths = [Path("/tmp/supplied")] if "supplied" in str(report) else []
            with self.subTest(report=report):
                with self.assertRaisesRegex(M.BoundaryError, "privacy-sensitive|byte-escape"):
                    M._privacy_scan(report, paths)


@unittest.skipUnless(EXACT_AVAILABLE, "authorized ignored exact inputs or Homebrew LLVM are unavailable")
class ExactBridgeTests(unittest.TestCase):
    def test_hostile_encoding_regeneration_is_utf8_lf_and_matches_retained_report(self) -> None:
        output = run_exact_hostile()
        self.assertEqual(output, REPORT.read_bytes())
        self.assertNotIn(b"\r", output)
        self.assertTrue(output.endswith(b"\n"))
        output.decode("utf-8", "strict")

    def test_exact_report_binds_corrected_subscription_and_rejects_old_attribution(self) -> None:
        report = json.loads(run_exact_hostile())
        exact = report["exact_static"]
        self.assertEqual(exact["corrected_subscription_call"], "0xe308b")
        self.assertEqual(exact["superseded_subscription_call"], "0xe2fc5")
        self.assertEqual(
            exact["corrected_receiver_filter_class"],
            "wildcard-service-and-path-fixed-interface-and-member",
        )
        self.assertEqual(
            exact["superseded_receiver_filter_class"],
            "fixed-service-path-interface-and-member",
        )
        self.assertTrue(exact["superseded_member_distinct"])
        self.assertNotEqual(
            exact["literal_bindings"]["receiver-member"]["sha256"],
            exact["literal_bindings"]["unrelated-member"]["sha256"],
        )

    def test_cross_binary_identity_fdes_calls_and_structural_binding_are_exact(self) -> None:
        report = json.loads(run_exact_hostile())
        exact = report["exact_static"]
        self.assertTrue(exact["interface_bytes_equal_cross_binary"])
        self.assertTrue(exact["member_bytes_equal_cross_binary"])
        self.assertEqual(
            exact["literal_bindings"]["emitter-interface"],
            exact["literal_bindings"]["receiver-interface"],
        )
        self.assertEqual(
            exact["literal_bindings"]["emitter-member"],
            exact["literal_bindings"]["receiver-member"],
        )
        self.assertEqual(exact["sender_direct_call_vas"], ["0x685e7", "0x8573f", "0x8595f", "0x109766"])
        self.assertEqual(
            exact["selected_fdes"]["appfumo:session-subscription-setup"],
            {"start": "0xe2c30", "end_exclusive": "0xe3296"},
        )
        self.assertEqual(
            exact["selected_fdes"]["appdmclient:signal-sender"],
            {"start": "0x4f1c0", "end_exclusive": "0x4f58a"},
        )
        self.assertFalse(report["artifacts"]["embedded_selection"]["trailing_container_bytes_included"])
        self.assertEqual(report["artifacts"]["embedded_selection"]["structural_extent"], 5066264)

    def test_bridge_data_flow_and_conditional_copy_are_bounded(self) -> None:
        report = json.loads(run_exact_hostile())
        bridge = report["bridge"]
        for key in (
            "mounted_callback_copies_first_string_to_object_field",
            "mounted_callback_passes_source_to_staging",
            "staging_passes_copied_source_to_checker",
            "checker_source_is_sender_second_string",
            "state_notification_calls_use_empty_strings",
            "sender_uses_session_bus",
            "sender_calls_signal_send",
            "receiver_service_filter_empty",
            "receiver_path_filter_empty",
            "accepted_mode_readiness_is_checked",
            "copy_call_is_conditional_on_readiness",
            "accepted_copy_package_base_is_source_path_global",
        ):
            self.assertTrue(bridge[key], key)
        self.assertFalse(bridge["alternate_local_request_is_copy_call"])
        self.assertEqual(bridge["source_path_global"], "0x6d4fa8")
        self.assertEqual(bridge["version_global"], "0x6d4fb0")
        self.assertEqual(bridge["status_global"], "0x6d4fb8")
        self.assertEqual(bridge["sender_argument_order"], ["status", "version", "source-path"])
        self.assertEqual(bridge["consumer_argument_order"], ["status", "version", "source-path"])

    def test_session_policy_permission_and_runtime_unknowns_remain_separate(self) -> None:
        report = json.loads(run_exact_hostile())
        boundary = report["session_bus_boundary"]
        self.assertEqual(boundary["authentication"], "EXTERNAL")
        self.assertEqual(boundary["default_send_permission"], "allow")
        self.assertEqual(boundary["session_policy_regular_member_count"], 0)
        self.assertFalse(boundary["local_override_present"])
        self.assertFalse(boundary["policy_permission_is_socket_reachability"])
        self.assertFalse(boundary["empty_service_and_path_authenticate_sender"])
        self.assertFalse(boundary["interface_and_member_authenticate_sender"])
        self.assertTrue(all(value is None for value in report["runtime"].values()))
        for key in (
            "runtime_delivery_established", "sender_control_established",
            "authentication_success_established", "copy_success_established",
            "code_execution_established", "root_established",
            "partition_write_established", "boot_acceptance_established", "persistence_established",
        ):
            self.assertFalse(report["scope"][key], key)

    def test_tracked_outputs_obey_privacy_contract(self) -> None:
        outputs = b"\n".join(path.read_bytes() for path in (REPORT, MANIFEST, EXACT_STATIC, ASSESSMENT))
        for forbidden in (
            b"/Users/",
            str(APPDM).encode("utf-8"),
            str(APPFUMO).encode("utf-8"),
            b"/com/lge/hkmc/avn/upgrade/fota/fotaInterface",
            b"com.lge.hkmc.avn.upgrade.fota.fotaInterface",
            b"onModePriority",
            b"sleep_status",
            b"1slotonModePriority(int, QString, QString)",
            b"\\x7fELF",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, outputs)


if __name__ == "__main__":
    unittest.main()
