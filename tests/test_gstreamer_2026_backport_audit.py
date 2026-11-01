"""Tests for the exact-static GStreamer CVE-2026-2921/2922 audit."""
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
TOOL = ROOT / "tools/uk_fw/gstreamer_2026_backport_audit.py"
MANIFEST = ROOT / "evidence/artifacts/media-candidates/gstreamer-2026-backport-audit-manifest.json"
REPORT = ROOT / "evidence/artifacts/media-candidates/gstreamer-2026-backport-audit-report.json"
EXCERPT = ROOT / "evidence/artifacts/media-candidates/gstreamer-2026-backport-exact-static.txt"
EVIDENCE = ROOT / "evidence/gstreamer-cve-2026-2921-2922.md"
ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
BREW = shutil.which("brew")
LLVM_BIN = (
    Path(subprocess.check_output([BREW, "--prefix", "llvm"], text=True).strip()) / "bin"
    if BREW
    else Path("/nonexistent")
)
OBJDUMP = LLVM_BIN / "llvm-objdump"
READELF = LLVM_BIN / "llvm-readelf"

SPEC = importlib.util.spec_from_file_location("gstreamer_2026_backport_audit", TOOL)
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
    ROOTFS.is_file()
    and ROOTFS.stat().st_size == _MANIFEST_JSON["artifacts"]["rootfs"]["size"]
    and REPORT.is_file()
    and _tool_matches(OBJDUMP, _MANIFEST_JSON["llvm"]["objdump"])
    and _tool_matches(READELF, _MANIFEST_JSON["llvm"]["readelf"])
)


def exact_command() -> list[str]:
    return [
        sys.executable,
        str(TOOL),
        "--rootfs",
        str(ROOTFS),
        "--llvm-objdump",
        str(OBJDUMP),
        "--llvm-readelf",
        str(READELF),
        "--manifest",
        str(MANIFEST),
    ]


@lru_cache(maxsize=1)
def run_exact() -> bytes:
    environment = dict(os.environ, PYTHONIOENCODING="utf-16:strict")
    completed = subprocess.run(
        exact_command(),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    if completed.stderr:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return completed.stdout


def _tar_member(
    name: str,
    data: bytes = b"bound",
    *,
    mode: int = 0o644,
    kind: bytes = tarfile.REGTYPE,
    linkname: str = "",
) -> tuple[tarfile.TarInfo, bytes]:
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


def selected_row(
    name: str = "./selected", data: bytes = b"bound", *, mode: int = 0o644
) -> dict[str, object]:
    return {
        "role": "fixture",
        "name": name,
        "type": "regular",
        "mode": mode,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def machine_fixture(
    role: str,
) -> tuple[list[object], list[tuple[int, int]], dict[str, object]]:
    manifest = M._load_manifest(MANIFEST)
    expected = copy.deepcopy(manifest["members"][role])
    instructions = [
        M.Instruction(address, mnemonic, operands)
        for address, mnemonic, operands in M.REQUIRED_ANCHORS[role].values()
    ]
    instructions.sort(key=lambda item: item.address)
    return instructions, [expected["selected_fde"]], expected


def mutate_instruction(
    instructions: list[object], address: int, *, mnemonic: str | None = None,
    operands: str | None = None
) -> list[object]:
    changed = []
    for item in instructions:
        if item.address == address:
            item = M.Instruction(
                item.address,
                item.mnemonic if mnemonic is None else mnemonic,
                item.operands if operands is None else operands,
            )
        changed.append(item)
    return changed


class StrictSchemaAndParserTests(unittest.TestCase):
    def test_manifest_loads_and_binds_only_supported_exact_state(self) -> None:
        manifest = M._load_manifest(MANIFEST)
        self.assertEqual(manifest["rootfs"]["sha256"], M.ROOTFS_SHA256)
        self.assertEqual(set(manifest["members"]), {"riff", "realmedia"})
        self.assertEqual(manifest["expected"], M.COMMITS)
        for role, identity in M.MEMBER_IDENTITIES.items():
            row = manifest["members"][role]
            self.assertEqual(row["size"], identity["size"])
            self.assertEqual(row["sha256"], identity["sha256"])
            self.assertEqual(row["build_id"], identity["build_id"])
            self.assertEqual(row["selected_fde"], identity["fde"])

    def test_manifest_rejects_unknown_missing_boolean_and_unsupported_values(self) -> None:
        source = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mutations = []
        value = copy.deepcopy(source); value["unknown"] = 1; mutations.append(value)
        value = copy.deepcopy(source); del value["llvm"]["version"]; mutations.append(value)
        value = copy.deepcopy(source); value["schema_version"] = True; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["rootfs"]["size"] = True; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["instruction_count"] = False; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["mode"] = True; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["size"] += 1; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["sha256"] = "00" * 32; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][1]["build_id"] = "00"; mutations.append(value)
        value = copy.deepcopy(source); value["expected"]["rm_primary_pre_store_fix"] = "00" * 20; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["rootfs"]["member_count"] += 1; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"].append(copy.deepcopy(value["artifacts"]["members"][0])); mutations.append(value)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            for index, value in enumerate(mutations):
                with self.subTest(index=index):
                    path.write_text(json.dumps(value), encoding="utf-8")
                    with self.assertRaises(M.AuditError):
                        M._load_manifest(path)

    def test_manifest_rejects_duplicate_json_keys_and_invalid_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(M.AuditError, "duplicate JSON key"):
                M._load_manifest(path)
            path.write_bytes(b"\xff")
            with self.assertRaisesRegex(M.AuditError, "valid UTF-8 JSON"):
                M._load_manifest(path)

    def test_manifest_rejects_malformed_duplicate_and_drifted_anchors_and_fdes(self) -> None:
        source = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mutations = []
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["selected_fde"]["end_exclusive"] = value["artifacts"]["members"][0]["selected_fde"]["start"]; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["anchors"][0]["mnemonic"] = "???"; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["anchors"][0]["address"] = True; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["anchors"][0]["sha256"] = "00" * 32; mutations.append(value)
        value = copy.deepcopy(source); value["artifacts"]["members"][0]["anchors"].append(copy.deepcopy(value["artifacts"]["members"][0]["anchors"][0])); mutations.append(value)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            for index, value in enumerate(mutations):
                with self.subTest(index=index):
                    path.write_text(json.dumps(value), encoding="utf-8")
                    with self.assertRaises(M.AuditError):
                        M._load_manifest(path)

    def test_disassembly_rejects_empty_malformed_duplicate_truncated_and_ordering(self) -> None:
        with self.assertRaisesRegex(M.AuditError, "no decoded instructions"):
            M.parse_disassembly(b"Disassembly of section .text:\n")
        with self.assertRaisesRegex(M.AuditError, "outside"):
            M.parse_disassembly(b"  10: nop\n")
        with self.assertRaisesRegex(M.AuditError, "mnemonic"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10: ??? operand\n")
        with self.assertRaisesRegex(M.AuditError, "duplicate"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10: nop\n  10: retq\n")
        with self.assertRaisesRegex(M.AuditError, "strictly increasing"):
            M.parse_disassembly(b"Disassembly of section .text:\n  11: nop\n  10: retq\n")
        with self.assertRaisesRegex(M.AuditError, "malformed or truncated"):
            M.parse_disassembly(b"Disassembly of section .text:\n  10:\n")
        with self.assertRaisesRegex(M.AuditError, "UTF-8"):
            M.parse_disassembly(b"\xff")

    def test_fde_build_id_and_export_parsers_fail_closed(self) -> None:
        valid = (
            b"  [0x20] FDE length=10 cie=[0x10]\n"
            b"    initial_location: 0x100\n"
            b"    address_range: 0x20 (end : 0x120)\n"
        )
        self.assertEqual(M.parse_fdes(valid), [(0x100, 0x120)])
        with self.assertRaisesRegex(M.AuditError, "malformed FDE"):
            M.parse_fdes(valid.replace(b"0x120", b"0x121"))
        with self.assertRaisesRegex(M.AuditError, "duplicate FDE"):
            M.parse_fdes(valid + valid)
        with self.assertRaisesRegex(M.AuditError, "malformed or truncated"):
            M.parse_fdes(b"[0x20] FDE length=10 cie=[0x10]\n")
        with self.assertRaisesRegex(M.AuditError, "no FDE"):
            M.parse_fdes(b"no records\n")
        self.assertEqual(M.parse_build_id(b"Build ID: aabb\n"), "aabb")
        for raw in (b"Build ID: aa\nBuild ID: bb\n", b"Build ID: AABB\n", b"truncated"):
            with self.subTest(raw=raw), self.assertRaisesRegex(M.AuditError, "absent or ambiguous"):
                M.parse_build_id(raw)
        symbols = b"  65: 0000000000001d50 13440 FUNC GLOBAL DEFAULT 11 gst_riff_create_video_caps\n"
        self.assertEqual(M.parse_exported_symbol(symbols, "gst_riff_create_video_caps"), 0x1D50)
        with self.assertRaisesRegex(M.AuditError, "absent, malformed, or ambiguous"):
            M.parse_exported_symbol(symbols + symbols, "gst_riff_create_video_caps")
        with self.assertRaisesRegex(M.AuditError, "absent, malformed, or ambiguous"):
            M.parse_exported_symbol(symbols.replace(b"GLOBAL", b"LOCAL "), "gst_riff_create_video_caps")


class FileAndArchiveSafetyTests(unittest.TestCase):
    def test_regular_reader_rejects_nonregular_oversized_and_changing_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path = directory / "bounded"
            path.write_bytes(b"abc")
            self.assertEqual(M._read_regular(path, 3, "fixture"), b"abc")
            with self.assertRaisesRegex(M.AuditError, "not a regular file"):
                M._read_regular(directory, 10, "fixture")
            with self.assertRaisesRegex(M.AuditError, "size limit"):
                M._read_regular(path, 2, "fixture")
            with mock.patch.object(M, "_same_stat", return_value=False):
                with self.assertRaisesRegex(M.AuditError, "changed while being read"):
                    M._read_regular(path, 3, "fixture")

    def test_canonicalization_rejects_unsafe_names(self) -> None:
        self.assertEqual(M._canonical_member_name("./usr/lib/item"), "usr/lib/item")
        for name in ("/usr/lib/item", "../item", "usr//item", "usr/./item", "", "usr/../item", "usr\x00/item"):
            with self.subTest(name=name), self.assertRaises(M.AuditError):
                M._canonical_member_name(name)

    def test_regular_selected_member_is_streamed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "good.tar.gz"
            write_tar(path, [_tar_member("./selected")])
            data, result = M._audit_archive(path, archive_artifact(path), {"fixture": selected_row()})
            self.assertEqual(data, {"fixture": b"bound"})
            self.assertEqual(result["member_count"], 1)

    def test_selected_alias_duplicate_missing_content_mode_size_and_inventory_drift_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            cases = [
                ("alias", [_tar_member("selected")], selected_row("./selected"), "alias"),
                ("duplicate", [_tar_member("./selected"), _tar_member("./selected")], selected_row(), "duplicated"),
                ("missing", [_tar_member("./other")], selected_row(), "missing"),
                ("content", [_tar_member("./selected", b"drift")], selected_row(), "content drift"),
                ("size", [_tar_member("./selected", b"longer")], selected_row(), "mode/size drift"),
                ("mode", [_tar_member("./selected", mode=0o600)], selected_row(), "mode/size drift"),
            ]
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
            ("block", tarfile.BLKTYPE, ""),
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


class ToolAndMachineBindingTests(unittest.TestCase):
    def test_tool_runner_rejects_failure_stderr_and_oversized_output(self) -> None:
        cases = (
            (subprocess.CompletedProcess([], 1, b"", b""), "failed"),
            (subprocess.CompletedProcess([], 0, b"", b"warning"), "stderr"),
            (subprocess.CompletedProcess([], 0, b"1234", b""), "exceeds"),
        )
        for completed, message in cases:
            with self.subTest(message=message), mock.patch.object(M.subprocess, "run", return_value=completed):
                with self.assertRaisesRegex(M.AuditError, message):
                    M._run_tool(["fixture"], "fixture", 3)

    @unittest.skipUnless(OBJDUMP.is_file(), "Homebrew llvm-objdump is unavailable")
    def test_exact_llvm_tool_identity_and_version_are_enforced(self) -> None:
        manifest = M._load_manifest(MANIFEST)
        expected = manifest["llvm"]["objdump"]
        M._validate_tool(OBJDUMP, manifest["llvm"]["version"], expected, "llvm-objdump")
        with self.assertRaisesRegex(M.AuditError, "file identity"):
            M._validate_tool(
                OBJDUMP,
                manifest["llvm"]["version"],
                {"size": expected["size"], "sha256": "00" * 32},
                "llvm-objdump",
            )
        with self.assertRaisesRegex(M.AuditError, "version identity"):
            M._validate_tool(OBJDUMP, "Homebrew LLVM version 0", expected, "llvm-objdump")
        with mock.patch.object(M, "_same_stat", return_value=False):
            with self.assertRaisesRegex(M.AuditError, "changed while being read"):
                M._validate_tool(OBJDUMP, manifest["llvm"]["version"], expected, "llvm-objdump")

    def test_supported_machine_semantics_pass_and_return_positive_facts(self) -> None:
        riff_instructions, riff_fdes, riff_expected = machine_fixture("riff")
        rm_instructions, rm_fdes, rm_expected = machine_fixture("realmedia")
        riff = M._validate_machine("riff", riff_instructions, riff_fdes, riff_expected)
        rm = M._validate_machine("realmedia", rm_instructions, rm_fdes, rm_expected)
        self.assertTrue(riff["riff_wrap32"])
        self.assertFalse(riff["riff_checked_multiply"])
        self.assertTrue(rm["rm_store_before_check"])
        self.assertFalse(rm["rm_pre_store_check"])
        self.assertFalse(rm["rm_extent_gate"])
        self.assertTrue(rm["rm_copy_before_later_subtract"])

    def test_riff_width_order_default_and_accept_path_mutations_fail(self) -> None:
        instructions, fdes, expected = machine_fixture("riff")
        mutations = [
            mutate_instruction(instructions, 0x24CF, mnemonic="movq", operands="0x20(%rbp), %rbp"),
            mutate_instruction(instructions, 0x24D2, mnemonic="shlq", operands="$0x2, %rbp"),
            mutate_instruction(instructions, 0x24C9, operands="0x24d5 <gst_riff_create_video_caps+0x785>"),
            mutate_instruction(instructions, 0x24E3, mnemonic="jb"),
            mutate_instruction(instructions, 0x2D50, operands="$0x200, %ebp"),
            mutate_instruction(instructions, 0x2D55, operands="0x24d8 <gst_riff_create_video_caps+0x788>"),
            mutate_instruction(instructions, 0x2CC2, operands="0x1a70 <gst_buffer_new_wrapped@plt>"),
        ]
        widened = list(instructions) + [M.Instruction(0x24D0, "movq", "%ebp, %rbp")]
        widened.sort(key=lambda item: item.address)
        mutations.append(widened)
        for index, changed in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(M.AuditError):
                M._validate_machine("riff", changed, fdes, expected)

    def test_realmedia_primary_store_overlap_and_branch_mutations_fail(self) -> None:
        instructions, fdes, expected = machine_fixture("realmedia")
        mutations = [
            mutate_instruction(instructions, 0xD608, operands="0x4b8(%r13), %rdi"),
            mutate_instruction(instructions, 0xD614, operands="0xa8(%r13), %edx"),
            mutate_instruction(instructions, 0xD622, operands="%rsi, %rdx"),
            mutate_instruction(instructions, 0xD62A, operands="%eax, 0xb4(%r13,%rdx,4)"),
            mutate_instruction(instructions, 0xD639, operands="%esi, 0xa8(%r13)"),
            mutate_instruction(instructions, 0xD640, operands="$0xff, %esi"),
            mutate_instruction(instructions, 0xD646, mnemonic="jbe"),
            mutate_instruction(instructions, 0xD646, operands="0xdd11 <.text+0x7fd1>"),
        ]
        contradictory = list(instructions) + [M.Instruction(0xD623, "cmpl", "$0x100, %edx")]
        contradictory.sort(key=lambda item: item.address)
        mutations.append(contradictory)
        for index, changed in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(M.AuditError):
                M._validate_machine("realmedia", changed, fdes, expected)

    def test_realmedia_companion_argument_and_check_order_mutations_fail(self) -> None:
        instructions, fdes, expected = machine_fixture("realmedia")
        mutations = [
            mutate_instruction(instructions, 0xD566, operands="0x20(%rsp), %rdx"),
            mutate_instruction(instructions, 0xD56B, mnemonic="movq", operands="%rbp, %r12"),
            mutate_instruction(instructions, 0xD578, operands="0x108(%rsp), %rdx"),
            mutate_instruction(instructions, 0xD580, operands="%rbx, %rcx"),
            mutate_instruction(instructions, 0xD583, operands="0x40(%rsp), %rdi"),
            mutate_instruction(instructions, 0xD588, operands="0x5520 <gst_adapter_push@plt>"),
            mutate_instruction(instructions, 0xD99C, mnemonic="addq"),
        ]
        guarded = list(instructions) + [M.Instruction(0xD57A, "cmpq", "%r12, %rbx")]
        guarded.sort(key=lambda item: item.address)
        mutations.append(guarded)
        for index, changed in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(M.AuditError):
                M._validate_machine("realmedia", changed, fdes, expected)

    def test_missing_anchor_fde_and_complete_count_hash_drift_fail(self) -> None:
        for role in ("riff", "realmedia"):
            instructions, fdes, expected = machine_fixture(role)
            with self.subTest(role=role, kind="anchor"), self.assertRaisesRegex(M.AuditError, "anchor drift"):
                M._validate_machine(role, instructions[1:], fdes, expected)
            with self.subTest(role=role, kind="fde"), self.assertRaisesRegex(M.AuditError, "FDE range drift"):
                M._validate_machine(role, instructions, [(fdes[0][0], fdes[0][1] + 1)], expected)

        instructions = [M.Instruction(0x10, "nop", ""), M.Instruction(0x11, "retq", "")]
        fdes = [(0x10, 0x12)]
        expected = {
            "instruction_count": 2,
            "instruction_sha256": M._canonical_hash(item.canonical for item in instructions),
            "fde_count": 1,
            "fde_sha256": M._canonical_hash(["10-12"]),
        }
        M._validate_complete_identity("fixture", instructions, fdes, expected)
        mutations = []
        value = dict(expected); value["instruction_count"] = 1; mutations.append(value)
        value = dict(expected); value["instruction_sha256"] = "00" * 32; mutations.append(value)
        value = dict(expected); value["fde_count"] = 2; mutations.append(value)
        value = dict(expected); value["fde_sha256"] = "00" * 32; mutations.append(value)
        for index, value in enumerate(mutations):
            with self.subTest(index=index), self.assertRaises(M.AuditError):
                M._validate_complete_identity("fixture", instructions, fdes, value)

    def test_contradictory_unsupported_and_non_boolean_semantic_states_fail(self) -> None:
        facts = {
            "riff_checked_multiply": False,
            "riff_wrap32": True,
            "rm_pre_store_check": False,
            "rm_store_before_check": True,
            "rm_extent_gate": False,
            "rm_copy_before_later_subtract": True,
        }
        assessments = M._derive_assessments(facts)
        self.assertEqual(set(assessments), {"riff_palette", "rm_fragment_index", "rm_fragment_extent"})
        for key in facts:
            value = dict(facts); value[key] = not value[key]
            with self.subTest(key=key), self.assertRaisesRegex(M.AuditError, "contradictory or unsupported"):
                M._derive_assessments(value)
        value = dict(facts); value["riff_wrap32"] = 1
        with self.assertRaisesRegex(M.AuditError, "must be a Boolean"):
            M._derive_assessments(value)
        value = dict(facts); value["unknown"] = False
        with self.assertRaisesRegex(M.AuditError, "keys mismatch"):
            M._derive_assessments(value)


@unittest.skipUnless(EXACT_AVAILABLE, "canonical rootfs or exact Homebrew LLVM tools are unavailable")
class ExactArtifactTests(unittest.TestCase):
    def test_cli_is_deterministic_explicit_utf8_lf_and_matches_report_bytes(self) -> None:
        output = run_exact()
        self.assertEqual(output, REPORT.read_bytes())
        self.assertNotIn(b"\r", output)
        self.assertTrue(output.endswith(b"\n"))
        report = json.loads(output.decode("utf-8"))
        self.assertEqual(report["schema_version"], M.SCHEMA_VERSION)
        self.assertEqual(report["canonical_rootfs"]["sha256"], M.ROOTFS_SHA256)

    def test_exact_three_verdicts_and_unknown_outcomes(self) -> None:
        report = json.loads(run_exact())
        assessments = report["assessments"]
        self.assertEqual(set(assessments), {"riff_palette", "rm_fragment_index", "rm_fragment_extent"})
        riff = assessments["riff_palette"]
        self.assertEqual(riff["upstream_patch_state"], "absent")
        self.assertEqual(riff["checked_multiplication_invariant"], "violated")
        self.assertEqual(riff["guard_arithmetic_wraps_for_num_colors_gte"], 1 << 30)
        self.assertIsNone(riff["exact_downstream_memory_effect"])
        primary = assessments["rm_fragment_index"]
        self.assertEqual(primary["upstream_patch_state"], "absent")
        self.assertEqual(primary["pre_store_rejection_invariant"], "violated")
        self.assertEqual(primary["indexed_store_displacement"], "0x4b0")
        companion = assessments["rm_fragment_extent"]
        self.assertEqual(companion["upstream_patch_state"], "absent")
        self.assertEqual(companion["local_pre_copy_invariant"], "unsatisfied")
        self.assertTrue(all(value is None for value in report["outcomes"].values()))

    def test_exact_member_export_fde_count_and_hash_bindings(self) -> None:
        report = json.loads(run_exact())
        riff = report["members"]["riff"]
        self.assertEqual(riff["exported_symbol"], {"name": "gst_riff_create_video_caps", "address": "0x1d50"})
        self.assertEqual(riff["selected_fde"], {"start": "0x1d50", "end_exclusive": "0x51d0"})
        self.assertEqual(riff["instruction_count"], 8084)
        rm = report["members"]["realmedia"]
        self.assertEqual(rm["selected_fde"], {"start": "0xb780", "end_exclusive": "0xe649"})
        self.assertEqual(rm["instruction_count"], 19045)

    def test_privacy_and_non_operational_artifacts(self) -> None:
        combined = REPORT.read_bytes() + MANIFEST.read_bytes() + EXCERPT.read_bytes() + EVIDENCE.read_bytes()
        for forbidden in (
            b"/Users/",
            b"gst-launch",
            b"filesrc",
            b"shellcode",
            b"payload",
            b"BEGIN ELF",
            b"physical device procedure",
        ):
            self.assertNotIn(forbidden, combined)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        scope = report["scope"]
        for key in (
            "recovered_targets_executed",
            "plugins_loaded",
            "media_inputs_created_loaded_or_parsed",
            "malformed_media_emitted",
            "trigger_recipe_emitted",
            "callable_target_coordinates_emitted",
            "proprietary_binary_retained",
            "full_disassembly_retained",
            "operational_device_procedure_emitted",
        ):
            self.assertFalse(scope[key])


if __name__ == "__main__":
    unittest.main()
