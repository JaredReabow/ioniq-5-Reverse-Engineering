import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/uk_fw/abl_ias_key_provenance.py"
REPORT = ROOT / "evidence/artifacts/update-candidates/abl-ias-key-provenance.json"
EXCERPT = ROOT / "evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm"
UPDATE = ROOT / "work/decrypted-eu-260128/HU/firmware/update.tar.gz"
SBL = ROOT / "work/online-slimbootloader-20261110"
MEA = ROOT / "work/online-meanalyzer-20261111"
SPEC = importlib.util.spec_from_file_location("abl_key_provenance", TOOL)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class AblIasKeyProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        missing = [str(path) for path in (UPDATE, SBL, MEA) if not path.exists()]
        if missing:
            raise unittest.SkipTest("analysis inputs absent: " + ", ".join(missing))
        process = subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--update-archive",
                str(UPDATE),
                "--sbl-repo",
                str(SBL),
                "--mea-repo",
                str(MEA),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=300,
        )
        if process.returncode:
            raise AssertionError(process.stderr.decode("utf-8", "replace"))
        cls.raw = process.stdout
        cls.report = json.loads(process.stdout)

    def test_report_is_frozen_and_deterministic(self):
        self.assertEqual(self.raw, REPORT.read_bytes())
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), "73459a4376b9ae12f0fcf3d4828960859eefe4e1683c2cc3033988e14addb984")
        self.assertEqual(self.raw, M.encode(self.report))

    def test_exact_static_excerpt_is_frozen(self):
        data = EXCERPT.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), "56ea91be8c7b7f03a71e042a3129ed0df096e4331b02af2ef62a26444386c666")
        self.assertNotIn(b"work/", data)
        self.assertNotIn(b"Contents of section", data)

    def test_exact_fit_and_manifest_chain(self):
        exact = self.report["exact_update"]
        loader = exact["ibb_loader"]
        stage = exact["decompressed_stage1"]
        self.assertEqual(loader["source_fit_address"], 0xFEF80000)
        self.assertEqual(loader["relocated_fit_address"], 0xC10C0)
        self.assertEqual(loader["fit_signature"], "_FIT_   ")
        self.assertTrue(loader["type_0b_payload_relocated_if_present"])
        self.assertEqual(stage["fit_table"]["selected_type"], 0x0B)
        self.assertEqual(stage["key_manifest"]["extension_offset"], 0x284)
        self.assertEqual(stage["key_manifest"]["entry_size"], 0x44)
        self.assertEqual(stage["key_manifest"]["digest_offset"], 0x24)
        self.assertEqual(stage["key_manifest"]["kernel_command_line_name"], "ABL.oemkm")
        producer = exact["cse_bup_fit_producer"]
        self.assertEqual(producer["sha256"], M.CSE_BUP_SHA256)
        self.assertEqual(producer["source_object_name"], "oem_key_man")
        self.assertEqual(producer["published_fit_address"], 0xFFFE1000)
        self.assertEqual(producer["published_fit_type"], 0x0B)
        self.assertFalse(producer["final_handoff_address_0xfef80000_mapping_proved"])
        self.assertFalse(producer["oem_key_man_byte_identity_with_ftpr_oem_key_proved"])

    def test_selector_0x27_is_usage_bit_39(self):
        selector = self.report["exact_update"]["decompressed_stage1"]["type3_os_selector"]
        self.assertEqual(selector["value"], 0x27)
        self.assertEqual(selector["usage_bit_index"], 39)
        self.assertEqual(selector["usage_byte_index"], 4)
        self.assertEqual(selector["usage_byte_mask"], 0x80)
        self.assertEqual(selector["public_me_analyzer_name"], "OS Kernel")

    def test_conclusions_remain_bounded(self):
        conclusions = self.report["conclusions"]
        self.assertTrue(conclusions["runtime_descriptor_is_fit_entry_type_0b_proved"])
        self.assertTrue(conclusions["ibbl_copies_fit_and_relocates_type_0b_payload_proved"])
        self.assertTrue(conclusions["cse_bup_constructs_fit_type0b_from_oem_key_man_proved"])
        self.assertTrue(conclusions["cse_bup_resolver_couples_oem_key_and_oem_key_man_names_proved"])
        self.assertTrue(conclusions["source_fit_content_producer_cse_bup_proved"])
        self.assertTrue(conclusions["runtime_fit_type0b_object_name_oem_key_man_proved"])
        self.assertTrue(conclusions["stored_oem_key_manifest_bytes_recovered"])
        self.assertTrue(conclusions["stored_usage39_digest_recovered"])
        self.assertTrue(conclusions["stored_oem_key_manifest_embedded_signature_valid"])
        self.assertFalse(conclusions["package_candidate_matches_stored_usage39_digest"])
        self.assertFalse(conclusions["runtime_fit_type0b_bound_to_stored_oem_key_manifest"])
        self.assertFalse(conclusions["runtime_expected_digest_bytes_recovered"])
        self.assertFalse(conclusions["final_handoff_address_0xfef80000_mapping_proved"])
        self.assertFalse(conclusions["pre_ibbl_key_manifest_authentication_proved"])
        self.assertFalse(conclusions["custom_signed_image_acceptance_proved"])
        self.assertFalse(conclusions["boot_root_or_persistence_proved"])

    def test_stored_oem_key_and_candidate_mismatch_are_bounded(self):
        exact = self.report["exact_update"]
        stored = exact["stored_oem_key_manifest"]
        self.assertEqual(stored["flash_offset"], M.OEM_KEY_OFFSET)
        self.assertEqual(stored["sha256"], M.OEM_KEY_SHA256)
        self.assertTrue(stored["manifest"]["embedded_signature_valid"])
        self.assertEqual(stored["extension"]["usage39_record"]["digest"], M.STORED_USAGE39_DIGEST)
        self.assertTrue(stored["extension"]["usage39_digest_equals_manifest_public_key_digest"])
        candidate = exact["package_carried_os_key_candidate_digest"]
        self.assertEqual(candidate["sha256"], M.CANDIDATE_OS_KEY_DIGEST)
        self.assertFalse(candidate["present_verbatim_in_update_abl"])
        self.assertFalse(candidate["present_verbatim_in_ibbl"])
        self.assertFalse(candidate["present_verbatim_in_stage1"])
        self.assertFalse(candidate["matches_stored_oem_key_usage39_digest"])

    def test_public_sources_are_separate_and_hash_bound(self):
        public = self.report["public_structure_corroboration"]
        self.assertEqual(public["slim_bootloader"]["commit"], M.SBL_COMMIT)
        self.assertEqual(public["slim_bootloader"]["type_0b_name"], "FIT_TYPE_0B_KEY_MANIFEST")
        self.assertEqual(public["me_analyzer"]["commit"], M.MEA_COMMIT)
        self.assertEqual(public["me_analyzer"]["usage_39_name"], "OS Kernel")
        self.assertIn("public-source corroboration", public["boundary"])

    def test_unsafe_archive_spellings_fail_closed(self):
        for name in ("", "/x", "././x", "a/./b", "a/../b", "a//b", "a\\b"):
            with self.subTest(name=name), self.assertRaises(M.Failure):
                M.canonical(name)
        self.assertIsNone(M.canonical("."))
        self.assertEqual(M.canonical("./a/b"), "a/b")

    def test_archive_alias_and_link_fail_closed_before_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "alias.tar.gz"
            with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as archive:
                for name in (M.ABL_MEMBER, "./" + M.ABL_MEMBER):
                    member = tarfile.TarInfo(name)
                    member.uid = 8100
                    member.gid = 8100
                    member.mode = 0o755
                    member.size = 1
                    archive.addfile(member, io.BytesIO(b"x"))
            old_size, old_digest = M.UPDATE_SIZE, M.UPDATE_SHA256
            try:
                data = path.read_bytes()
                M.UPDATE_SIZE = len(data)
                M.UPDATE_SHA256 = hashlib.sha256(data).hexdigest()
                with self.assertRaises(M.Failure):
                    M.archive_one(path)
            finally:
                M.UPDATE_SIZE, M.UPDATE_SHA256 = old_size, old_digest

    def test_lz4_decoder_fails_closed(self):
        with self.assertRaises(M.Failure):
            M.lz4_block(b"", 1)
        with self.assertRaises(M.Failure):
            M.lz4_block(b"\x00\x00\x00", 4)
        self.assertEqual(M.lz4_block(b"\x30abc", 3), b"abc")

    def test_public_source_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repo"
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            with self.assertRaises(M.Failure):
                M.git_blob(repository, M.SBL_COMMIT, M.SBL_FILE, M.SBL_FILE_SHA256)

    def test_serialization_ignores_pythonioencoding(self):
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-16"
        script = (
            "import importlib.util,sys;"
            f"s=importlib.util.spec_from_file_location('m',r'{TOOL}');"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            f"sys.stdout.buffer.write(m.encode({self.report!r}))"
        )
        process = subprocess.run(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            check=False,
            timeout=30,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, self.raw)


if __name__ == "__main__":
    unittest.main()
