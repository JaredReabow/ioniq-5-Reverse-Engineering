"""Tests for the bounded exact-static GStreamer backport analyzer."""
from __future__ import annotations

import copy
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
from functools import lru_cache
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/uk_fw/gstreamer_parser_backport_audit.py"
MANIFEST = ROOT / "evidence/artifacts/media-candidates/gstreamer-parser-backport-audit-manifest.json"
REPORT = ROOT / "evidence/artifacts/media-candidates/gstreamer-parser-backport-audit-report.json"
EXCERPT = ROOT / "evidence/artifacts/media-candidates/gstreamer-parser-backport-exact-static.txt"
ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
BREW = shutil.which("brew")
LLVM_BIN = Path(subprocess.check_output([BREW, "--prefix", "llvm"], text=True).strip()) / "bin" if BREW else Path("/nonexistent")
OBJDUMP = LLVM_BIN / "llvm-objdump"
READELF = LLVM_BIN / "llvm-readelf"

SPEC = importlib.util.spec_from_file_location("gstreamer_parser_backport_audit", TOOL)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def _tool_matches(path: Path, row: dict[str, object]) -> bool:
    if not path.is_file():
        return False
    raw = path.read_bytes()
    return len(raw) == row["size"] and hashlib.sha256(raw).hexdigest() == row["sha256"]


_MANIFEST_JSON = json.loads(MANIFEST.read_text(encoding="utf-8"))
EXACT_AVAILABLE = (
    ROOTFS.is_file() and ROOTFS.stat().st_size == _MANIFEST_JSON["artifacts"]["rootfs"]["size"]
    and REPORT.is_file() and OBJDUMP.is_file() and READELF.is_file()
    and _tool_matches(OBJDUMP, _MANIFEST_JSON["llvm"]["objdump"])
    and _tool_matches(READELF, _MANIFEST_JSON["llvm"]["readelf"])
)


def exact_command() -> list[str]:
    return [
        sys.executable, str(TOOL),
        "--rootfs", str(ROOTFS),
        "--llvm-objdump", str(OBJDUMP),
        "--llvm-readelf", str(READELF),
        "--manifest", str(MANIFEST),
    ]


@lru_cache(maxsize=1)
def run_exact() -> bytes:
    env = dict(os.environ, PYTHONIOENCODING="utf-16:strict")
    completed = subprocess.run(
        exact_command(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=env,
    )
    if completed.stderr:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return completed.stdout


def _tar_member(name: str, data: bytes = b"bound", *, mode: int = 0o644,
                kind: bytes = tarfile.REGTYPE, linkname: str = "") -> tuple[tarfile.TarInfo, bytes]:
    item = tarfile.TarInfo(name)
    item.mode = mode
    item.type = kind
    item.linkname = linkname
    if kind in (tarfile.REGTYPE, tarfile.AREGTYPE):
        item.size = len(data)
    return item, data


def write_tar(path: Path, rows: list[tuple[tarfile.TarInfo, bytes]]) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for item, data in rows:
            source = io.BytesIO(data) if item.type in (tarfile.REGTYPE, tarfile.AREGTYPE) else None
            archive.addfile(item, source)


def archive_artifact(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    inventory = hashlib.sha256()
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        for index, member in enumerate(members):
            inventory.update(M._inventory_line(index, member))
    return {
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "member_count": len(members),
        "inventory_sha256": inventory.hexdigest(),
    }


def selected_row(name: str = "./selected", data: bytes = b"bound", *, mode: int = 0o644) -> dict[str, object]:
    return {
        "role": "fixture", "name": name, "type": "regular", "mode": mode,
        "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
    }


def machine_fixture(role: str) -> tuple[list[object], list[tuple[int, int]], dict[str, object]]:
    manifest = M._load_manifest(MANIFEST)
    expected = copy.deepcopy(manifest["members"][role])
    instructions = [M.Instruction(address, mnemonic, operands)
                    for address, mnemonic, operands in M.REQUIRED_ANCHORS[role].values()]
    instructions.sort(key=lambda item: item.address)
    return instructions, [expected["selected_fde"]], expected


class StrictSchemaAndParserTests(unittest.TestCase):
    def test_manifest_loads_and_binds_supported_exact_state(self) -> None:
        manifest = M._load_manifest(MANIFEST)
        self.assertEqual(manifest["rootfs"]["sha256"], M.ROOTFS_SHA256)
        self.assertEqual(set(manifest["members"]), {"subparse", "typefind"})
        for role, identity in M.MEMBER_IDENTITIES.items():
            self.assertEqual(manifest["members"][role]["sha256"], identity["sha256"])
            self.assertEqual(manifest["members"][role]["build_id"], identity["build_id"])
            self.assertEqual(manifest["members"][role]["selected_fde"], identity["fde"])

    def test_manifest_rejects_unknown_missing_boolean_duplicate_and_unsupported_state(self) -> None:
        source = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mutations: list[dict[str, object]] = []
        value = copy.deepcopy(source); value["unknown"] = 1; mutations.append(value)
        value = copy.deepcopy(source); del value["llvm"]["version"]; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["rootfs"]["size"] = True; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["instruction_count"] = False; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["sha256"] = "00" * 32; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][1]["build_id"] = "00"; mutations.append(value)
        value = copy.deepcopy(source); value["expected"]["typefind_complete_length_correction"] = "00"; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"].append(copy.deepcopy(value["artifacts"]["members"][0])); mutations.append(value)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            for index, value in enumerate(mutations):
                with self.subTest(index=index):
                    path.write_text(json.dumps(value), encoding="utf-8")
                    with self.assertRaises(M.AuditError):
                        M._load_manifest(path)
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(M.AuditError, "duplicate JSON key"):
                M._load_manifest(path)

    def test_manifest_rejects_malformed_ranges_instructions_and_anchor_hashes(self) -> None:
        source = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mutations = []
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["selected_fde"]["end_exclusive"] = value["artifacts"]["members"][0]["selected_fde"]["start"]; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["anchors"][0]["mnemonic"] = "???"; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["anchors"][0]["address"] = -1; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["anchors"][0]["sha256"] = "00" * 32; mutations.append(value)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            for index, value in enumerate(mutations):
                with self.subTest(index=index):
                    path.write_text(json.dumps(value), encoding="utf-8")
                    with self.assertRaises(M.AuditError):
                        M._load_manifest(path)

    def test_disassembly_rejects_empty_malformed_duplicate_and_ordering(self) -> None:
        with self.assertRaisesRegex(M.AuditError, "no decoded instructions"):
            M.parse_disassembly(b"Disassembly of section .text:\n")
        with self.assertRaisesRegex(M.AuditError, "mnemonic"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10: ??? operand\n")
        with self.assertRaisesRegex(M.AuditError, "duplicate"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10: nop\n  10: retq\n")
        with self.assertRaisesRegex(M.AuditError, "strictly increasing"):
            M.parse_disassembly(b"Disassembly of section .text:\n  11: nop\n  10: retq\n")
        with self.assertRaisesRegex(M.AuditError, "malformed or truncated"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10:\n")

    def test_fde_and_build_id_parsers_fail_closed(self) -> None:
        valid = (b"  [0x20] FDE length=10 cie=[0x10]\n"
                 b"    initial_location: 0x100\n"
                 b"    address_range: 0x20 (end : 0x120)\n")
        self.assertEqual(M.parse_fdes(valid), [(0x100, 0x120)])
        with self.assertRaisesRegex(M.AuditError, "malformed FDE"):
            M.parse_fdes(valid.replace(b"0x120", b"0x121"))
        with self.assertRaisesRegex(M.AuditError, "duplicate FDE"):
            M.parse_fdes(valid + valid)
        with self.assertRaisesRegex(M.AuditError, "no FDE"):
            M.parse_fdes(b"truncated\n")
        with self.assertRaisesRegex(M.AuditError, "absent or ambiguous"):
            M.parse_build_id(b"Build ID: aa\nBuild ID: bb\n")


class ArchiveSafetyTests(unittest.TestCase):
    def test_canonicalization_rejects_unsafe_names(self) -> None:
        self.assertEqual(M._canonical_member_name("./usr/lib/item"), "usr/lib/item")
        for name in ("/usr/lib/item", "../item", "usr//item", "usr/./item", "", "usr/../item"):
            with self.subTest(name=name), self.assertRaises(M.AuditError):
                M._canonical_member_name(name)

    def test_regular_selected_member_is_streamed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "good.tar.gz"
            write_tar(path, [_tar_member("./selected")])
            data, result = M._audit_archive(path, archive_artifact(path), {"fixture": selected_row()})
            self.assertEqual(data, {"fixture": b"bound"})
            self.assertEqual(result["member_count"], 1)

    def test_selected_alias_duplicate_missing_content_mode_and_inventory_drift_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            cases: list[tuple[str, list[tuple[tarfile.TarInfo, bytes]], dict[str, object], str]] = []
            cases.append(("alias", [_tar_member("selected")], selected_row("./selected"), "alias"))
            cases.append(("duplicate", [_tar_member("./selected"), _tar_member("./selected")], selected_row(), "duplicated"))
            cases.append(("missing", [_tar_member("./other")], selected_row(), "missing"))
            cases.append(("content", [_tar_member("./selected", b"drift")], selected_row(), "content drift"))
            cases.append(("size", [_tar_member("./selected", b"longer")], selected_row(), "mode/size drift"))
            cases.append(("mode", [_tar_member("./selected", mode=0o600)], selected_row(), "mode/size drift"))
            for label, rows, expected, message in cases:
                with self.subTest(label=label):
                    path = directory / f"{label}.tar.gz"
                    write_tar(path, rows)
                    with self.assertRaisesRegex(M.AuditError, message):
                        M._audit_archive(path, archive_artifact(path), {"fixture": expected})
            good = directory / "inventory.tar.gz"
            write_tar(good, [_tar_member("./selected")])
            artifact = archive_artifact(good); artifact["member_count"] = 2
            with self.assertRaisesRegex(M.AuditError, "inventory identity/count"):
                M._audit_archive(good, artifact, {"fixture": selected_row()})

    def test_selected_links_and_special_nodes_fail_closed(self) -> None:
        kinds = (
            ("symlink", tarfile.SYMTYPE, "target"),
            ("hardlink", tarfile.LNKTYPE, "target"),
            ("fifo", tarfile.FIFOTYPE, ""),
            ("character", tarfile.CHRTYPE, ""),
        )
        with tempfile.TemporaryDirectory() as temporary:
            for label, kind, linkname in kinds:
                with self.subTest(kind=label):
                    path = Path(temporary) / f"{label}.tar.gz"
                    write_tar(path, [_tar_member("./selected", kind=kind, linkname=linkname)])
                    with self.assertRaisesRegex(M.AuditError, "type/mode/size drift"):
                        M._audit_archive(path, archive_artifact(path), {"fixture": selected_row()})

    def test_archive_identity_nonregular_oversized_and_changing_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path = directory / "good.tar.gz"
            write_tar(path, [_tar_member("./selected")])
            artifact = archive_artifact(path)
            bad = dict(artifact); bad["sha256"] = "00" * 32
            with self.assertRaisesRegex(M.AuditError, "identity"):
                M._audit_archive(path, bad, {"fixture": selected_row()})
            with self.assertRaisesRegex(M.AuditError, "not a regular file"):
                M._stat_regular(directory, M.MAX_ROOTFS_SIZE, "fixture")
            with self.assertRaisesRegex(M.AuditError, "size limit"):
                M._stat_regular(path, path.stat().st_size - 1, "fixture")
            with mock.patch.object(M, "_same_stat", return_value=False):
                with self.assertRaisesRegex(M.AuditError, "changed during analysis"):
                    M._audit_archive(path, artifact, {"fixture": selected_row()})


class MachineBindingTests(unittest.TestCase):
    def test_supported_machine_anchor_sets_and_ordering_pass(self) -> None:
        for role in ("subparse", "typefind"):
            instructions, fdes, expected = machine_fixture(role)
            with self.subTest(role=role):
                M._validate_machine(role, instructions, fdes, expected)

    def test_instruction_branch_immediate_and_register_drift_fail(self) -> None:
        cases = (
            ("typefind", 0x2CC2, "operands", "0x2cc4 <.text+0x1014>"),
            ("typefind", 0x2CBE, "operands", "$0x15, %rax"),
            ("typefind", 0x2D20, "operands", "0x12(%rbx), %eax"),
            ("subparse", 0xB873, "operands", "0xb875 <.text+0x6585>"),
            ("subparse", 0xB870, "operands", "%rbx, %rbx"),
        )
        for role, address, field, replacement in cases:
            instructions, fdes, expected = machine_fixture(role)
            changed = []
            for item in instructions:
                if item.address == address:
                    values = {"address": item.address, "mnemonic": item.mnemonic, "operands": item.operands}
                    values[field] = replacement
                    item = M.Instruction(**values)
                changed.append(item)
            with self.subTest(role=role, address=hex(address)), self.assertRaises(M.AuditError):
                M._validate_machine(role, changed, fdes, expected)

    def test_missing_anchor_and_fde_drift_fail(self) -> None:
        for role in ("subparse", "typefind"):
            instructions, fdes, expected = machine_fixture(role)
            with self.subTest(role=role, kind="anchor"), self.assertRaisesRegex(M.AuditError, "anchor drift"):
                M._validate_machine(role, instructions[1:], fdes, expected)
            with self.subTest(role=role, kind="fde"), self.assertRaisesRegex(M.AuditError, "FDE range drift"):
                M._validate_machine(role, instructions, [(fdes[0][0], fdes[0][1] + 1)], expected)

    def test_instruction_and_fde_count_hash_drift_fail(self) -> None:
        instructions = [M.Instruction(0x10, "nop", ""), M.Instruction(0x11, "retq", "")]
        fdes = [(0x10, 0x12)]
        expected = {
            "instruction_count": 2,
            "instruction_sha256": M._canonical_hash(item.canonical for item in instructions),
            "fde_count": 1,
            "fde_sha256": M._canonical_hash("10-12" for _ in (0,)),
        }
        self.assertEqual(len(M._validate_complete_identity("fixture", instructions, fdes, expected)), 2)
        mutations = []
        value = dict(expected); value["instruction_count"] = 1; mutations.append(value)
        value = dict(expected); value["instruction_sha256"] = "00" * 32; mutations.append(value)
        value = dict(expected); value["fde_count"] = 2; mutations.append(value)
        value = dict(expected); value["fde_sha256"] = "00" * 32; mutations.append(value)
        for index, value in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(M.AuditError):
                M._validate_complete_identity("fixture", instructions, fdes, value)

    @unittest.skipUnless(OBJDUMP.is_file(), "Homebrew llvm-objdump is unavailable")
    def test_tool_identity_is_enforced(self) -> None:
        raw = OBJDUMP.read_bytes()
        version = subprocess.check_output([str(OBJDUMP), "--version"], text=True).splitlines()[0]
        with self.assertRaisesRegex(M.AuditError, "file identity"):
            M._validate_tool(OBJDUMP, version, {"size": len(raw), "sha256": "00" * 32}, "llvm-objdump")


@unittest.skipUnless(EXACT_AVAILABLE, "canonical rootfs or exact Homebrew LLVM tools are unavailable")
class ExactArtifactTests(unittest.TestCase):
    def test_cli_is_deterministic_utf8_lf_and_matches_report(self) -> None:
        output = run_exact()
        self.assertEqual(output, REPORT.read_bytes())
        self.assertNotIn(b"\r", output)
        report = json.loads(output.decode("utf-8"))
        self.assertEqual(report["schema_version"], M.SCHEMA_VERSION)
        self.assertEqual(report["canonical_rootfs"]["sha256"], M.ROOTFS_SHA256)

    def test_exact_conclusions_are_bounded(self) -> None:
        report = json.loads(run_exact())
        subparse = report["subparse_assessment"]
        self.assertTrue(subparse["nonzero_length_test_precedes_last_byte_address"])
        self.assertEqual(subparse["named_zero_length_underwrite_mechanism"], "rejected-for-exact-binary")
        self.assertFalse(subparse["unrelated_subtitle_defects_rejected"])
        typefind = report["typefind_assessment"]
        self.assertTrue(typefind["initial_less_than_18_guard_present"])
        self.assertFalse(typefind["complete_less_than_22_guard_present"])
        self.assertTrue(typefind["bounded_residual_out_of_range_read_possible"])
        self.assertEqual(typefind["residual_total_lengths"], [18, 19, 20, 21])
        self.assertEqual(typefind["residual_out_of_range_bytes_by_total_length"], {"18": 4, "19": 3, "20": 2, "21": 1})
        self.assertTrue(all(value is None for value in report["outcomes"].values()))

    def test_privacy_and_non_operational_outputs(self) -> None:
        combined = REPORT.read_bytes() + MANIFEST.read_bytes() + EXCERPT.read_bytes()
        for forbidden in (
            b"/Users/", b"gst-launch", b"filesrc", b"shellcode", b"payload recipe",
            b"malformed media bytes", b"BEGIN ELF", b"root persistence",
        ):
            self.assertNotIn(forbidden, combined)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        scope = report["scope"]
        self.assertFalse(scope["recovered_targets_executed"])
        self.assertFalse(scope["parser_inputs_created"])
        self.assertFalse(scope["trigger_recipe_emitted"])
        self.assertFalse(scope["full_binary_retained"])
        self.assertFalse(scope["full_disassembly_retained"])


if __name__ == "__main__":
    unittest.main()
