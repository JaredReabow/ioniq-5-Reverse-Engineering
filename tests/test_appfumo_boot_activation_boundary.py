"""Tests for the exact-static AppFUMO boot-activation boundary analyzer."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile
import unittest
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/uk_fw/appfumo_boot_activation_boundary.py"
ELF = ROOT / "work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf"
ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
MANIFEST = ROOT / "evidence/artifacts/update-candidates/appfumo-boot-activation-boundary-manifest.json"
REPORT = ROOT / "evidence/artifacts/update-candidates/appfumo-boot-activation-boundary.json"
BREW = shutil.which("brew")
LLVM_BIN = Path(subprocess.check_output([BREW, "--prefix", "llvm"], text=True).strip()) / "bin" if BREW else Path("/nonexistent")
OBJDUMP = LLVM_BIN / "llvm-objdump"
READELF = LLVM_BIN / "llvm-readelf"
EXACT_AVAILABLE = all(path.is_file() for path in (ELF, ROOTFS, MANIFEST, REPORT, OBJDUMP, READELF))

SPEC = importlib.util.spec_from_file_location("appfumo_boot_activation_boundary", TOOL)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)

ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PROGRAM_HEADER = struct.Struct("<IIQQQQQQ")


def minimal_elf(*, duplicate_load: bool = False) -> bytes:
    size = 0x3000
    raw = bytearray(size)
    ident = b"\x7fELF" + bytes((2, 1, 1, 0)) + b"\0" * 8
    phnum = 2 if duplicate_load else 1
    raw[:ELF_HEADER.size] = ELF_HEADER.pack(
        ident, 3, 62, 1, 0, ELF_HEADER.size, 0, 0,
        ELF_HEADER.size, PROGRAM_HEADER.size, phnum, 0, 0, 0,
    )
    row = PROGRAM_HEADER.pack(1, 5, 0, 0, 0, size, size, 0x1000)
    raw[ELF_HEADER.size:ELF_HEADER.size + PROGRAM_HEADER.size] = row
    if duplicate_load:
        offset = ELF_HEADER.size + PROGRAM_HEADER.size
        raw[offset:offset + PROGRAM_HEADER.size] = row
    return bytes(raw)


def exact_command() -> list[str]:
    return [
        sys.executable, str(TOOL), "--elf", str(ELF), "--rootfs", str(ROOTFS),
        "--llvm-objdump", str(OBJDUMP), "--llvm-readelf", str(READELF),
        "--manifest", str(MANIFEST),
    ]


@lru_cache(maxsize=1)
def run_exact() -> bytes:
    env = dict(os.environ, PYTHONIOENCODING="utf-16:strict")
    completed = subprocess.run(exact_command(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if completed.stderr:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return completed.stdout


def write_tar(path: Path, *, name: str, kind: str = "regular", data: bytes = b"bound") -> None:
    with tarfile.open(path, "w:gz") as archive:
        item = tarfile.TarInfo(name)
        item.mode = 0o644
        if kind == "regular":
            item.size = len(data)
            archive.addfile(item, io.BytesIO(data))
        elif kind == "symlink":
            item.type = tarfile.SYMTYPE
            item.linkname = "target"
            archive.addfile(item)
        else:
            raise AssertionError(kind)


def fixture_expectation(path: Path, expected_name: str, *, absent: tuple[str, ...] = ()) -> tuple[dict, dict]:
    raw = path.read_bytes()
    inventory = hashlib.sha256()
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        for index, member in enumerate(members):
            inventory.update(M._inventory_line(index, member))
    artifact = {"size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    expected = {
        "member_count": len(members),
        "inventory_sha256": inventory.hexdigest(),
        "selected_members": [{
            "role": "fixture", "name": expected_name, "type": "regular", "mode": 0o644,
            "size": 5, "sha256": hashlib.sha256(b"bound").hexdigest(),
        }],
        "absent_basenames": absent,
    }
    return artifact, expected


class ParserAndSafetyTests(unittest.TestCase):
    def test_disassembly_rejects_empty_malformed_duplicate_and_ordering(self) -> None:
        with self.assertRaisesRegex(M.BoundaryError, "no decoded instructions"):
            M.parse_disassembly(b"Disassembly of section .text:\n")
        with self.assertRaisesRegex(M.BoundaryError, "mnemonic"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10: ??? operand\n")
        with self.assertRaisesRegex(M.BoundaryError, "duplicate"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10: nop\n  10: retq\n")
        with self.assertRaisesRegex(M.BoundaryError, "strictly increasing"):
            M.parse_disassembly(b"Disassembly of section .text:\n  11: nop\n  10: retq\n")
        with self.assertRaisesRegex(M.BoundaryError, "malformed or truncated"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10:\n")

    def test_fde_and_build_id_parsers_fail_closed(self) -> None:
        valid = (b"  [0x20] FDE length=10 cie=[0x10]\n"
                 b"    initial_location: 0x100\n"
                 b"    address_range: 0x20 (end : 0x120)\n")
        self.assertEqual(M.parse_fdes(valid), [(0x100, 0x120)])
        with self.assertRaisesRegex(M.BoundaryError, "malformed FDE"):
            M.parse_fdes(valid.replace(b"0x120", b"0x121"))
        with self.assertRaisesRegex(M.BoundaryError, "duplicate"):
            M.parse_fdes(valid + valid)
        with self.assertRaisesRegex(M.BoundaryError, "no FDE"):
            M.parse_fdes(b"truncated\n")
        with self.assertRaisesRegex(M.BoundaryError, "absent or ambiguous"):
            M.parse_build_id(b"Build ID: aa\nBuild ID: bb\n")

    def test_elf_mapping_rejects_truncated_ambiguous_and_unmapped(self) -> None:
        with self.assertRaisesRegex(M.BoundaryError, "truncated"):
            M.ElfView(b"\x7fELF")
        with self.assertRaisesRegex(M.BoundaryError, "ambiguous"):
            M.ElfView(minimal_elf(duplicate_load=True)).map(0x100, 1, "fixture")
        with self.assertRaisesRegex(M.BoundaryError, "unmapped"):
            M.ElfView(minimal_elf()).map(0x4000, 1, "fixture")

    def test_manifest_rejects_unknown_missing_bool_and_evidence_drift(self) -> None:
        source = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mutations = []
        value = json.loads(json.dumps(source)); value["extra"] = 1; mutations.append(value)
        value = json.loads(json.dumps(source)); del value["artifacts"]["elf"]["build_id"]; mutations.append(value)
        value = json.loads(json.dumps(source)); value["artifacts"]["rootfs"]["size"] = True; mutations.append(value)
        value = json.loads(json.dumps(source)); value["expected"]["anchors"] = {}; mutations.append(value)
        value = json.loads(json.dumps(source)); value["expected"]["direct_transfers"][0]["call_vas"] = []; mutations.append(value)
        value = json.loads(json.dumps(source)); value["expected"]["fdes"][0]["end_exclusive"] += 1; mutations.append(value)
        value = json.loads(json.dumps(source)); value["expected"]["rootfs"]["selected_members"][0]["mode"] = True; mutations.append(value)
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

    def test_archive_canonicalization_rejects_unsafe_names(self) -> None:
        self.assertEqual(M._canonical_member_name("./etc/item"), "etc/item")
        self.assertEqual(M._canonical_member_name("."), ".")
        for name in ("/etc/item", "../item", "etc//item", "etc/./item", ""):
            with self.subTest(name=name), self.assertRaises(M.BoundaryError):
                M._canonical_member_name(name)

    def test_stream_audit_accepts_regular_member_and_rejects_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.tar.gz"
            write_tar(good, name="./file")
            artifact, expected = fixture_expectation(good, "./file")
            result = M._audit_rootfs(good, artifact, expected)
            self.assertEqual(result["selected_members"]["fixture"]["mode"], "0644")
            alias = Path(tmp) / "alias.tar.gz"
            write_tar(alias, name="file")
            artifact, expected = fixture_expectation(alias, "./file")
            with self.assertRaisesRegex(M.BoundaryError, "archive alias"):
                M._audit_rootfs(alias, artifact, expected)

    def test_stream_audit_rejects_link_and_exact_negative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "link.tar.gz"
            write_tar(link, name="./file", kind="symlink")
            artifact, expected = fixture_expectation(link, "./file")
            with self.assertRaisesRegex(M.BoundaryError, "type/mode/size drift"):
                M._audit_rootfs(link, artifact, expected)
            negative = Path(tmp) / "negative.tar.gz"
            write_tar(negative, name="./fw_setenv")
            artifact, expected = fixture_expectation(negative, "./fw_setenv", absent=("fw_setenv",))
            with self.assertRaisesRegex(M.BoundaryError, "no longer absent"):
                M._audit_rootfs(negative, artifact, expected)

    @unittest.skipUnless(OBJDUMP.is_file(), "Homebrew llvm-objdump is unavailable")
    def test_tool_file_identity_is_enforced(self) -> None:
        raw = OBJDUMP.read_bytes()
        version = subprocess.check_output([str(OBJDUMP), "--version"], text=True).splitlines()[0]
        with self.assertRaisesRegex(M.BoundaryError, "file identity"):
            M._validate_tool(OBJDUMP, version, len(raw), "00" * 32, "llvm-objdump")


@unittest.skipUnless(EXACT_AVAILABLE, "exact ELF/rootfs or Homebrew LLVM is unavailable")
class ExactArtifactTests(unittest.TestCase):
    def test_cli_is_utf8_lf_deterministic_and_matches_report(self) -> None:
        output = run_exact()
        self.assertNotIn(b"\r", output)
        self.assertEqual(output, REPORT.read_bytes())
        self.assertEqual(json.loads(output), json.loads(REPORT.read_text(encoding="utf-8")))

    def test_completion_qml_qt_dispatch_and_reset_chain(self) -> None:
        report = json.loads(run_exact())
        chain = report["completion_to_reset"]
        for key in (
            "completion_qml_active_timer_emits_reboot_clicked",
            "qml_signal_to_update_view_signal_connected",
            "update_view_start_signal_to_controller_reboot_slot_connected",
            "controller_meta_dispatch_reaches_reboot",
            "controller_reboot_reaches_reset_wrapper",
            "reset_wrapper_tail_reaches_reset_core",
        ):
            self.assertTrue(chain[key])
        self.assertEqual(report["evidence"]["direct_transfers"]["0x134ce0"]["calls"], ["0x16f930"])
        self.assertEqual(report["evidence"]["direct_transfers"]["0x146680"]["calls"], ["0x134d18"])
        self.assertEqual(report["evidence"]["direct_transfers"]["0x145ca0"]["jumps"], ["0x1466cc"])

    def test_reboot_recovery_and_boot_information_are_bounded(self) -> None:
        report = json.loads(run_exact())
        for section in ("completion_to_reset", "separate_reboot_system", "recovery_mode"):
            self.assertFalse(report[section]["slot_identifier_present"])
            self.assertFalse(report[section].get("remote_action_proved", report[section].get("send_acceptance_proves_remote_action")))
        for section in ("completion_to_reset", "separate_reboot_system"):
            self.assertTrue(report[section]["send_status_observed"])
            self.assertTrue(report[section]["send_false_enters_bounded_retry_flow"])
            self.assertTrue(report[section]["terminal_send_false_reaches_redacted_fallback"])
        self.assertFalse(report["recovery_mode"]["send_status_controls_flow"])
        boot = report["boot_information"]
        self.assertEqual(boot["shared_memory_key_role"], "micom-status-message")
        self.assertIsNone(boot["shared_memory_producer"])
        self.assertIsNone(boot["booting_type_enum_meaning"])
        self.assertIsNone(boot["status_enum_meaning"])

    def test_rootfs_inventory_and_negative_scope(self) -> None:
        report = json.loads(run_exact())
        rootfs = report["rootfs_audit"]
        self.assertEqual(rootfs["member_count"], 66836)
        self.assertEqual(rootfs["update_start_scripts_classification"], "label-management-only")
        self.assertEqual(rootfs["root_fsck_observation_scope"], "current-root-device")
        self.assertFalse(rootfs["generic_components_bound_to_appfumo_flow"])
        self.assertEqual(rootfs["absence_scope"], "exact-basename-only")
        self.assertEqual(set(rootfs["exact_name_absence"]), set(M.REQUIRED_ABSENT_BASENAMES))
        self.assertTrue(all(row["type"] == "regular" for row in rootfs["selected_members"].values()))

    def test_unknown_boundary_and_privacy(self) -> None:
        output = run_exact()
        report = json.loads(output)
        combined = output + MANIFEST.read_bytes() + REPORT.read_bytes()
        self.assertNotIn(b"/" + b"Users/", combined)
        self.assertNotIn(str(ELF).encode(), output)
        self.assertNotIn(b"CVE-", combined)
        boundary = report["boundary"]
        for key in ("inactive_slot_activation_visible", "mark_good_visible", "boot_counter_update_visible",
                    "rollback_programming_visible", "persistent_slot_choice_visible"):
            self.assertFalse(boundary[key])
        self.assertIsNone(boundary["boot_slot_change"])
        self.assertIsNone(boundary["boot_acceptance"])
        scope = report["scope"]
        for key in ("operator_paths_emitted", "callable_dbus_coordinates_emitted", "serial_bytes_emitted",
                    "target_instructions_emitted", "operational_fallback_command_emitted",
                    "proprietary_binary_bytes_emitted"):
            self.assertFalse(scope[key])


if __name__ == "__main__":
    unittest.main()
