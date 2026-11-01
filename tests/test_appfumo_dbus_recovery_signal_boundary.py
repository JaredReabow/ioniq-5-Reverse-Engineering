"""Focused tests for the AppFUMO wildcard recovery-signal boundary."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_DIR = ROOT / "tools/uk_fw"
sys.path.insert(0, str(TOOL_DIR))
TOOL = TOOL_DIR / "appfumo_dbus_recovery_signal_boundary.py"
ELF = ROOT / "work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf"
ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
KERNEL = ROOT / "work/eu-260128/kernel.config"
MANIFEST = ROOT / "evidence/artifacts/update-candidates/appfumo-dbus-recovery-signal-boundary-manifest.json"
REPORT = ROOT / "evidence/artifacts/update-candidates/appfumo-dbus-recovery-signal-boundary.json"
SELECTED_EVIDENCE = ROOT / "evidence/artifacts/update-candidates/appfumo-dbus-recovery-signal-boundary-exact-static.txt"
ASSESSMENT = ROOT / "evidence/appfumo-dbus-recovery-signal-boundary.md"
PLAN = ROOT / "docs/agent-work/appfumo-dbus-recovery-signal-boundary/PLAN.md"
CHECKPOINT = ROOT / "docs/agent-work/appfumo-dbus-recovery-signal-boundary/CHECKPOINT.md"
BREW = shutil.which("brew")
LLVM_BIN = Path(subprocess.check_output([BREW, "--prefix", "llvm"], text=True).strip()) / "bin" if BREW else Path("/nonexistent")
OBJDUMP = LLVM_BIN / "llvm-objdump"
READELF = LLVM_BIN / "llvm-readelf"
EXACT_AVAILABLE = all(path.is_file() for path in (
    ELF, ROOTFS, KERNEL, MANIFEST, REPORT, SELECTED_EVIDENCE,
    ASSESSMENT, PLAN, CHECKPOINT, OBJDUMP, READELF,
))

SPEC = importlib.util.spec_from_file_location("appfumo_dbus_recovery_signal_boundary", TOOL)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)

DOCTYPE = ('<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN"\n'
           ' "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">\n')


def exact_command() -> list[str]:
    return [
        sys.executable, str(TOOL), "--elf", str(ELF), "--rootfs", str(ROOTFS),
        "--kernel-config", str(KERNEL), "--llvm-objdump", str(OBJDUMP),
        "--llvm-readelf", str(READELF), "--manifest", str(MANIFEST),
    ]


@lru_cache(maxsize=1)
def run_exact() -> bytes:
    env = dict(os.environ, PYTHONIOENCODING="utf-16:strict")
    completed = subprocess.run(exact_command(), check=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    if completed.stderr:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return completed.stdout


def policy_xml(body: str) -> bytes:
    return (DOCTYPE + "<busconfig>" + body + "</busconfig>\n").encode("utf-8")


def tar_expectation(path: Path, policy_name: str, policy_raw: bytes) -> tuple[dict, dict]:
    raw = path.read_bytes()
    inventory = hashlib.sha256()
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        for index, member in enumerate(members):
            inventory.update(M._inventory_line(index, member))
    canonical = M._canonical_member_name(policy_name)
    row = {
        "name_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "mode": 0o644,
        "size": len(policy_raw),
        "sha256": hashlib.sha256(policy_raw).hexdigest(),
    }
    expected = {
        "member_count": len(members),
        "inventory_sha256": inventory.hexdigest(),
        "selected_members": [],
        "policy_members": [row],
        "policy_inventory_sha256": M._policy_inventory_hash([row]),
        "selected_policy_sha256": row["sha256"],
    }
    return {"size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}, expected


def write_policy_tar(path: Path, *, policy_kind: str = "regular", system_local: bool = False) -> tuple[str, bytes]:
    name = "./etc/dbus-1/system.d/fixture.conf"
    raw = policy_xml('<policy context="default"><allow send_type="signal"/></policy>')
    with tarfile.open(path, "w:gz") as archive:
        directory = tarfile.TarInfo("./etc/dbus-1/system.d")
        directory.type = tarfile.DIRTYPE
        directory.mode = 0o755
        archive.addfile(directory)
        item = tarfile.TarInfo(name)
        item.mode = 0o644
        if policy_kind == "regular":
            item.size = len(raw)
            archive.addfile(item, io.BytesIO(raw))
        elif policy_kind == "symlink":
            item.type = tarfile.SYMTYPE
            item.linkname = "target"
            archive.addfile(item)
        else:
            raise AssertionError(policy_kind)
        if system_local:
            local = tarfile.TarInfo("./etc/dbus-1/system-local.conf")
            local.mode = 0o644
            local.size = len(raw)
            archive.addfile(local, io.BytesIO(raw))
    return name, raw


class ParserAndFailClosedTests(unittest.TestCase):
    def test_policy_parser_accepts_supported_general_and_exact_rules(self) -> None:
        raw = policy_xml(
            '<policy context="default">'
            '<allow send_type="signal"/>'
            '<allow receive_interface="normalized.interface" receive_member="NormalizedMember"/>'
            '</policy>'
        )
        result = M.audit_policy_xml(raw, "normalized.interface", "NormalizedMember", system_config=False)
        self.assertEqual(result["rule_count"], 2)
        self.assertEqual(result["general_signal_allow"], 1)
        self.assertEqual(result["exact_filter_allow"], 1)

    def test_policy_parser_rejects_malformed_doctype_entity_include_and_rule_forms(self) -> None:
        cases = (
            b"<busconfig>",
            policy_xml('<!ENTITY x "y"><policy context="default"><allow send_type="signal"/></policy>'),
            policy_xml("<include>other.conf</include>"),
            policy_xml('<policy context="default"><allow eavesdrop="true"/></policy>'),
            policy_xml('<policy context="default"><allow send_type="unknown"/></policy>'),
            policy_xml('<policy context="default"><allow own="x" send_type="signal"/></policy>'),
            policy_xml('<policy context="default"><allow send_type="signal"><child/></allow></policy>'),
        )
        for index, raw in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(M.BoundaryError):
                M.audit_policy_xml(raw, "normalized.interface", "NormalizedMember", system_config=False)

    def test_wildcard_peer_constraints_and_conjunctive_matching(self) -> None:
        interface, member = "normalized.interface", "NormalizedMember"
        self.assertTrue(M._signal_rule_matches(
            {"send_destination": "*"}, interface, member,
            direction="send", destination=None,
        ))
        self.assertFalse(M._signal_rule_matches(
            {"send_destination": "named.destination"}, interface, member,
            direction="send", destination=None,
        ))
        self.assertTrue(M._signal_rule_matches(
            {"receive_sender": "*"}, interface, member,
            direction="receive", sender="named.sender",
        ))
        self.assertTrue(M._signal_rule_matches(
            {"receive_sender": "named.sender"}, interface, member,
            direction="receive", sender="named.sender",
        ))
        self.assertFalse(M._signal_rule_matches(
            {"receive_sender": "named.sender"}, interface, member,
            direction="receive", sender="other.sender",
        ))
        self.assertFalse(M._signal_rule_matches(
            {"receive_sender": "named.sender", "receive_interface": "other.interface"},
            interface, member, direction="receive", sender="named.sender",
        ))
        self.assertEqual(
            M._rule_signal_class({"send_destination": "*"}, interface, member),
            ("send", "general"),
        )
        self.assertEqual(
            M._rule_signal_class({"receive_sender": "*"}, interface, member),
            ("receive", "general"),
        )
        self.assertEqual(
            M._rule_signal_class({"receive_sender": "named.sender"}, interface, member),
            ("receive", "sender-constrained"),
        )

    def test_ordered_overrides_scope_precedence_and_cross_file_unknown(self) -> None:
        interface, member = "normalized.interface", "NormalizedMember"
        allow = {"effect": "allow", "attrs": {"receive_sender": "*"}}
        deny = {"effect": "deny", "attrs": {"receive_sender": "*"}}
        self.assertEqual(M._ordered_signal_effect(
            [allow, deny], interface, member, direction="receive", sender="named.sender"
        ), "deny")
        self.assertEqual(M._ordered_signal_effect(
            [deny, allow], interface, member, direction="receive", sender="named.sender"
        ), "allow")
        self.assertEqual(
            M._apply_scope_precedence("allow", (), "deny", "no-match", "no-match", "no-match"),
            "deny",
        )
        self.assertEqual(
            M._apply_scope_precedence("deny", (), "allow", "no-match", "no-match", "no-match"),
            "allow",
        )
        self.assertEqual(M._undefined_order_effect(("allow", "deny")), "unknown")
        self.assertEqual(M._undefined_order_effect(("allow", "allow")), "allow")

    def test_policy_scope_and_ownership_forms_fail_closed(self) -> None:
        interface, member = "normalized.interface", "NormalizedMember"
        valid = (
            policy_xml('<policy group="valid-group"><allow send_type="signal"/></policy>'),
            policy_xml('<policy context="mandatory"><allow group="valid-group"/></policy>'),
            policy_xml('<policy at_console="false"><allow send_type="signal"/></policy>'),
        )
        for raw in valid:
            M.audit_policy_xml(raw, interface, member, system_config=False)
        invalid = (
            policy_xml('<policy context="unexpected"><allow send_type="signal"/></policy>'),
            policy_xml('<policy at_console="maybe"><allow send_type="signal"/></policy>'),
            policy_xml('<policy user=" "><allow send_type="signal"/></policy>'),
            policy_xml('<policy group=" "><allow send_type="signal"/></policy>'),
            policy_xml('<policy context="default"><allow own="name" user="user"/></policy>'),
            policy_xml('<policy context="default"><allow user="user" group="group"/></policy>'),
            policy_xml('<policy user="user"><allow group="group"/></policy>'),
        )
        for index, raw in enumerate(invalid):
            with self.subTest(index=index), self.assertRaises(M.BoundaryError):
                M.audit_policy_xml(raw, interface, member, system_config=False)

    def test_system_config_rejects_unexpected_include(self) -> None:
        singletons = (
            "<type>system</type><user>messagebus</user><fork/><standard_system_servicedirs/>"
            "<servicehelper>x</servicehelper><pidfile>x</pidfile><syslog/><auth>EXTERNAL</auth><listen>x</listen>"
        )
        policies = (
            '<policy context="default"><allow user="*"/><deny send_type="method_call"/>'
            '<allow send_type="signal"/><allow receive_type="signal"/></policy>'
        )
        raw = policy_xml(singletons + policies + "<includedir>unexpected</includedir>")
        with self.assertRaises(M.BoundaryError):
            M.audit_policy_xml(raw, "normalized.interface", "NormalizedMember", system_config=True)

    def test_manifest_rejects_unknown_missing_boolean_and_evidence_drift(self) -> None:
        source = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mutations = []
        value = json.loads(json.dumps(source)); value["extra"] = 1; mutations.append(value)
        value = json.loads(json.dumps(source)); del value["artifacts"]["elf"]["build_id"]; mutations.append(value)
        value = json.loads(json.dumps(source)); value["artifacts"]["rootfs"]["size"] = True; mutations.append(value)
        value = json.loads(json.dumps(source)); value["expected"]["fdes"][0]["start"] += 1; mutations.append(value)
        value = json.loads(json.dumps(source)); value["expected"]["rootfs"]["policy_members"] = []; mutations.append(value)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            for index, mutation in enumerate(mutations):
                with self.subTest(index=index):
                    path.write_text(json.dumps(mutation), encoding="utf-8")
                    with self.assertRaises(M.BoundaryError):
                        M._load_manifest(path)
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(M.BoundaryError, "duplicate JSON key"):
                M._load_manifest(path)

    def test_kernel_config_rejects_duplicate_and_malformed_lines(self) -> None:
        values, digest = M._parse_kernel_config(b"CONFIG_SECURITY_SMACK=y\n# CONFIG_SECURITY_SELINUX is not set\n")
        self.assertEqual(values["CONFIG_SECURITY_SELINUX"], "n")
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        with self.assertRaisesRegex(M.BoundaryError, "duplicate"):
            M._parse_kernel_config(b"CONFIG_A=y\nCONFIG_A=n\n")
        with self.assertRaisesRegex(M.BoundaryError, "unsupported"):
            M._parse_kernel_config(b"CONFIG A=y\n")

    def test_rootfs_stream_rejects_policy_link_and_system_local_member(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.tar.gz"
            name, raw = write_policy_tar(good)
            artifact, expected = tar_expectation(good, name, raw)
            result = M._audit_rootfs(good, artifact, expected)
            self.assertEqual(len(result["policy_rows"]), 1)

            link = Path(tmp) / "link.tar.gz"
            name, raw = write_policy_tar(link, policy_kind="symlink")
            artifact, expected = tar_expectation(link, name, b"")
            with self.assertRaisesRegex(M.BoundaryError, "alias, link, or special"):
                M._audit_rootfs(link, artifact, expected)

            local = Path(tmp) / "local.tar.gz"
            name, raw = write_policy_tar(local, system_local=True)
            artifact, expected = tar_expectation(local, name, raw)
            with self.assertRaisesRegex(M.BoundaryError, "system-local"):
                M._audit_rootfs(local, artifact, expected)

    def test_unit_parser_rejects_explicit_user(self) -> None:
        expected = {"unit_execstart_sha256": hashlib.sha256(b"normalized-start").hexdigest()}
        valid = b"[Service]\nExecStart=normalized-start\n"
        self.assertFalse(M._parse_unit(valid, expected)["user_directive_present"])
        with self.assertRaisesRegex(M.BoundaryError, "identity drift"):
            M._parse_unit(valid + b"User=root\n", expected)


@unittest.skipUnless(EXACT_AVAILABLE, "exact inputs or Homebrew LLVM are unavailable")
class ExactArtifactTests(unittest.TestCase):
    def test_cli_is_deterministic_utf8_lf_and_matches_report(self) -> None:
        output = run_exact()
        self.assertNotIn(b"\r", output)
        self.assertEqual(output, REPORT.read_bytes())
        self.assertEqual(json.loads(output), json.loads(REPORT.read_text(encoding="utf-8")))

    def test_exact_connect_dispatch_guards_and_request_boundary(self) -> None:
        report = json.loads(run_exact())
        exact = report["exact_static"]
        for key in (
            "connect_service_filter_empty", "connect_path_filter_empty",
            "connect_interface_filter_fixed", "connect_member_filter_fixed",
            "connect_receiver_bound", "connect_slot_bound",
            "generated_dispatch_reaches_local_consumer",
            "input_nonempty_and_normalized_value_guarded",
            "local_state_guards_precede_request", "consumer_tail_reaches_separate_request",
            "separate_request_is_asynchronous",
        ):
            self.assertTrue(exact[key])
        self.assertFalse(exact["remote_action_confirmed"])
        self.assertEqual(set(exact["literal_bindings"]), set(M.REQUIRED_LITERALS))

    def test_complete_policy_audit_and_include_boundary(self) -> None:
        policy = json.loads(run_exact())["canonical_policy"]
        # Main system.conf policy counts are deliberately separate from the
        # 18-member system.d audit; do not fold the default signal allows into
        # the system.d allow total.
        self.assertEqual(policy["system_conf_policy_rule_count"], 14)
        self.assertEqual(policy["system_conf_policy_allow_count"], 10)
        self.assertEqual(policy["system_conf_policy_deny_count"], 4)
        self.assertEqual(policy["system_conf_default_policy_rule_count"], 13)
        self.assertEqual(policy["system_conf_default_policy_allow_count"], 9)
        self.assertEqual(policy["system_conf_default_policy_deny_count"], 4)
        for key in (
            "system_conf_default_all_users_connect_allow_rule_count",
            "system_conf_default_method_call_send_deny_rule_count",
            "system_conf_default_signal_send_allow_rule_count",
            "system_conf_default_signal_receive_allow_rule_count",
        ):
            self.assertEqual(policy[key], 1)
        self.assertTrue(policy["system_conf_default_all_users_may_connect"])
        self.assertTrue(policy["system_conf_default_send_signal_allowed"])
        self.assertTrue(policy["system_conf_default_receive_signal_allowed"])
        self.assertTrue(policy["system_conf_default_method_call_send_denied"])

        self.assertEqual(policy["system_d_policy_member_count"], 18)
        self.assertEqual(policy["system_d_policy_rule_count"], 221)
        self.assertEqual(policy["system_d_policy_allow_count"], 208)
        self.assertEqual(policy["system_d_policy_deny_count"], 13)
        for key in (
            "system_d_policy_exact_filter_allow_count", "system_d_policy_exact_filter_deny_count",
            "system_d_policy_general_signal_allow_count", "system_d_policy_general_signal_deny_count",
        ):
            self.assertEqual(policy[key], 0)
        self.assertEqual(policy["system_d_named_receive_sender_allow_rule_count"], 15)
        self.assertEqual(policy["system_d_named_receive_sender_deny_rule_count"], 1)
        pair = policy["system_d_paired_receive_sender_group"]
        self.assertEqual(pair["length"], 21)
        self.assertEqual(
            pair["sha256"],
            "508d97e50a6fa1dd3369295f5e1d748cd188a9ab297d3cec406c6eff9fc3b5a5",
        )
        self.assertEqual(pair["main_default_receive_effect"], "allow")
        self.assertEqual(pair["non_root_recipient_effect"], "deny")
        self.assertEqual(pair["root_recipient_effect"], "allow")
        self.assertIsNone(pair["installed_consumer_effect"])
        self.assertTrue(pair["rules_share_one_policy_member"])
        self.assertEqual(policy["system_d_send_destination_value_count"], 137)
        self.assertEqual(policy["system_d_send_destination_named_non_wildcard_count"], 137)
        self.assertEqual(policy["system_d_send_destination_wildcard_count"], 0)
        self.assertEqual(policy["system_d_send_destinationless_broadcast_match_count"], 0)
        self.assertTrue(policy["policy_rules_are_conjunctive"])
        self.assertEqual(policy["policy_rule_order_semantics"], "last-matching-rule-wins")
        self.assertFalse(policy["includedir_cross_file_order_defined"])
        self.assertFalse(policy["includedir_cross_file_order_material_for_exact_signal"])
        self.assertEqual(policy["includedir_same_scope_conflict_resolution"], "unknown")
        self.assertFalse(policy["archive_system_local_member_present"])
        self.assertIsNone(policy["runtime_system_local_or_include_replacement"])
        self.assertIsNone(policy["dynamic_include_effect"])

    def test_launcher_kernel_and_named_integration_boundaries(self) -> None:
        report = json.loads(run_exact())
        launcher = report["launcher_and_identity"]
        self.assertFalse(launcher["launcher_unit_user_directive_present"])
        self.assertEqual(launcher["systemd_configured_default_uid_role"], "root")
        self.assertTrue(launcher["launcher_script_starts_launcher"])
        self.assertTrue(launcher["launcher_contains_dynamic_app_process_construction_for_updater_role"])
        self.assertTrue(launcher["updater_exec_label_assignment_named_in_both_canonical_scripts"])
        self.assertIsNone(launcher["complete_installed_runtime_uid"])
        self.assertIsNone(launcher["complete_installed_runtime_label"])
        mac = report["mandatory_access_control"]
        self.assertTrue(mac["kernel_smack_enabled"])
        self.assertFalse(mac["kernel_selinux_enabled"])
        self.assertFalse(mac["kernel_apparmor_enabled"])
        self.assertTrue(mac["bus_daemon_selinux_named_strings_present"])
        self.assertFalse(mac["bus_daemon_smack_named_strings_present"])
        self.assertIsNone(mac["kernel_socket_mediation"])
        self.assertIsNone(mac["arbitrary_label_same_bus_admission"])

    def test_model_distinctions_unknowns_and_privacy(self) -> None:
        output = run_exact()
        report = json.loads(output)
        combined = b"\n".join((
            output, MANIFEST.read_bytes(), REPORT.read_bytes(),
            SELECTED_EVIDENCE.read_bytes(), ASSESSMENT.read_bytes(),
            PLAN.read_bytes(), CHECKPOINT.read_bytes(),
        ))
        elf = M.ElfView(ELF.read_bytes())
        private_literals = [
            elf.bytes_at(va, length, "private literal")
            for va, length in ((0x215273, 21), (0x21E610, 23), (0x227358, 29),
                               (0x215289, 4), (0x21528E, 17), (0x21EC50, 15))
        ]
        selected_policy_sha = json.loads(MANIFEST.read_text(encoding="utf-8"))["expected"]["rootfs"]["selected_policy_sha256"]
        selected_policy_values: list[bytes] = []
        with tarfile.open(ROOTFS, "r|gz") as archive:
            for item in archive:
                if not item.isreg() or not item.name.startswith("./etc/dbus-1/system.d/"):
                    continue
                extracted = archive.extractfile(item)
                assert extracted is not None
                raw = extracted.read()
                if hashlib.sha256(raw).hexdigest() != selected_policy_sha:
                    continue
                root = ET.fromstring(raw)
                selected_policy_values.extend(
                    value.encode("utf-8") for element in root.iter()
                    for value in element.attrib.values() if "." in value
                )
                break
        self.assertTrue(selected_policy_values)
        for value in private_literals + selected_policy_values:
            self.assertNotIn(value, combined)
        self.assertNotIn(b"/Users/", combined)
        self.assertNotIn(str(ELF).encode(), output)
        finding = report["finding"]
        for key in (
            "bus_policy_permission_equals_same_bus_socket_reachability",
            "interface_member_match_authenticates_sender",
            "local_slot_invocation_confirms_external_action",
            "recovery_control_implies_code_execution_or_root",
            "code_execution_established", "root_transition_established", "persistence_established",
        ):
            self.assertFalse(finding[key])
        self.assertTrue(report["qt5_semantics"]["wildcard_filter_means_message_acceptance_not_message_forgery"])
        self.assertTrue(all(value is None for value in report["unknowns"].values()))
        scope = report["scope"]
        for key in (
            "target_code_executed", "bus_connected", "signal_or_method_sent",
            "operational_request_created", "payload_or_packet_created",
            "flash_update_or_persistence_action", "supplied_paths_emitted",
            "target_instructions_or_bytes_emitted", "callable_dbus_coordinates_emitted",
            "signal_or_argument_values_emitted", "commands_or_exploit_steps_emitted",
        ):
            self.assertFalse(scope[key])


if __name__ == "__main__":
    unittest.main()
