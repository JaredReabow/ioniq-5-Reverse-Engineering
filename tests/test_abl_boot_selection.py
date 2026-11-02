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
TOOL = ROOT / "tools/uk_fw/abl_boot_selection.py"
REPORT = ROOT / "evidence/artifacts/update-candidates/abl-boot-selection.json"
EXCERPT = ROOT / "evidence/artifacts/update-candidates/abl-boot-selection-exact-static.asm"
UPDATE = ROOT / "work/decrypted-eu-260128/HU/firmware/update.tar.gz"
ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
SBL = ROOT / "work/online-slimbootloader-20261110"
SPEC = importlib.util.spec_from_file_location("ablboot", TOOL)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class AblBootSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        missing = [str(path) for path in (UPDATE, ROOTFS, SBL) if not path.exists()]
        if missing:
            raise unittest.SkipTest("private analysis inputs absent: " + ", ".join(missing))
        process = subprocess.run(
            [sys.executable, str(TOOL), "--update-archive", str(UPDATE), "--rootfs", str(ROOTFS), "--sbl-repo", str(SBL)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=300,
        )
        if process.returncode:
            raise AssertionError(process.stderr.decode())
        cls.raw = process.stdout
        cls.report = json.loads(process.stdout)

    def test_report_is_frozen_and_deterministic(self):
        self.assertEqual(self.raw, REPORT.read_bytes())
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), "204adff4a69478db3ca113985585ceff30f7e31b8101068b223b9630c497136e")
        self.assertEqual(self.raw, M.encode(self.report))

    def test_exact_static_excerpt_is_frozen_and_byte_free(self):
        data = EXCERPT.read_bytes()
        self.assertEqual(len(data), 12607)
        self.assertEqual(hashlib.sha256(data).hexdigest(), "efd46f8f7604daa73a9e51707efa7a1c44fb19aa6868208b2221720dd661899e")
        self.assertNotIn(b"work/", data)
        self.assertNotIn(b"Contents of section", data)
        self.assertIn(b"byte ptr [0xc0214]", data)

    def test_exact_boot_records_and_crc_are_bound(self):
        container = self.report["exact_update"]["config_container"]
        self.assertEqual(container["flash_offset"], 0x102E6A)
        self.assertEqual(container["sha256"], M.CONFIG_SHA256)
        self.assertEqual(container["header_crc32c"], "a242938d")
        self.assertEqual(container["payload_crc32c"], "dd7740d8")
        self.assertEqual(
            [(record["boot_index"], record["device_instance"], record["basename"]) for record in container["boot_records"]],
            [(2, 1, "iasImage"), (3, 2, "iasImage")],
        )
        self.assertFalse(container["direct_sub_literal_present"])
        gpio = container["boot_mode_gpio_record"]
        self.assertEqual((gpio["tag"], gpio["mask"], gpio["invert"]), ("0x04e", 3, 0))
        self.assertEqual(gpio["input_pins"], ["0xc184", "0xc103"])

    def test_public_gpio_semantics_remain_comparative(self):
        public = self.report["comparative_public_slim_bootloader"]
        self.assertEqual(public["commit"], M.SBL_COMMIT)
        self.assertEqual(public["tag_0x04e_name"], "ABL_CDATA_BOOT_MODE_GPIO_TAG")
        self.assertFalse(public["exact_runtime_equivalence_proved"])
        self.assertFalse(self.report["conclusions"]["exact_runtime_boot_state_populated_from_gpio_proved"])

    def test_fallback_and_sub_conclusions_remain_bounded(self):
        conclusions = self.report["conclusions"]
        self.assertTrue(conclusions["selected_primary_failure_can_fall_forward_to_secondary_record"])
        self.assertTrue(conclusions["userspace_repairs_primary_from_successful_secondary_fallback"])
        self.assertFalse(conclusions["abl_configuration_directly_selects_iasimage_sub"])
        self.assertTrue(conclusions["engineering_script_promotes_sub_by_overwriting_primary_basename"])
        self.assertTrue(conclusions["exact_config_contains_boot_mode_gpio_record"])
        self.assertTrue(conclusions["exact_stage_maps_tag_0x04e_to_boot_mode_gpio"])
        self.assertFalse(conclusions["persistent_boot_index_source_proved"])
        self.assertFalse(conclusions["attempt_counter_proved"])
        self.assertFalse(conclusions["health_or_mark_good_proved"])
        self.assertFalse(conclusions["rollback_policy_proved"])
        self.assertFalse(conclusions["custom_image_acceptance_root_or_persistence_proved"])

    def test_selected_and_actual_boot_fields_are_separate(self):
        stage = self.report["exact_update"]["decompressed_stage"]
        self.assertEqual(stage["selected_index_expression"], "byte[0x000c0214] & 0x1f")
        self.assertTrue(stage["selected_index_skips_earlier_records"])
        self.assertTrue(stage["boot_record_callback_returns_zero_after_returned_load_failure"])
        self.assertTrue(stage["config_iterator_callback_zero_continues_to_next_record"])
        self.assertTrue(stage["later_records_remain_eligible_after_a_returned_failure"])
        self.assertIn("ABL.boot", stage["kernel_cmdline_selected_field"])
        self.assertIn("ABL.bdev", stage["kernel_cmdline_actual_device_field"])

    def test_unsafe_archive_spellings_fail_closed(self):
        for spelling in ("", "/x", "././x", "a/./b", "a/../b", "a//b", "a\\b"):
            with self.subTest(spelling=spelling), self.assertRaises(M.Failure):
                M.canonical(spelling)
        self.assertIsNone(M.canonical("."))
        self.assertEqual(M.canonical("./a/b"), "a/b")

    def test_archive_alias_link_and_ownership_drift_fail_closed(self):
        def check(entries):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "a.tar.gz"
                with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as archive:
                    for name, kind, uid in entries:
                        member = tarfile.TarInfo(name)
                        member.uid = uid
                        member.gid = 0
                        member.mode = 0o644
                        member.size = 1 if kind == "file" else 0
                        if kind == "symlink":
                            member.type = tarfile.SYMTYPE
                            member.linkname = "target"
                            archive.addfile(member)
                        else:
                            archive.addfile(member, io.BytesIO(b"x"))
                raw = path.read_bytes()
                wanted = {"x": {"size": 1, "mode": 0o644, "uid": 0, "gid": 0, "sha256": hashlib.sha256(b"x").hexdigest()}}
                with self.assertRaises(M.Failure):
                    M.archive_members(path, len(raw), hashlib.sha256(raw).hexdigest(), wanted)

        check([("x", "file", 0), ("./x", "file", 0)])
        check([("./x", "symlink", 0)])
        check([("./x", "file", 1)])

    def test_decoders_fail_closed(self):
        with self.assertRaises(M.Failure):
            M.lz4_block(b"", 1)
        with self.assertRaises(M.Failure):
            M.lz4_block(b"\x00\x00\x00", 4)
        self.assertEqual(M.lz4_block(b"\x30abc", 3), b"abc")
        with self.assertRaises(M.Failure):
            M.config_records(b"\x08\x00\x00\x00")

    def test_public_source_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            name, digest = next(iter(M.SBL_FILES.items()))
            with self.assertRaises(M.Failure):
                M.git_blob(repo, name, digest)

    def test_serialization_ignores_pythonioencoding(self):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-16"
        code = (
            'import importlib.util,sys;'
            f's=importlib.util.spec_from_file_location("m",r"{TOOL}");'
            'm=importlib.util.module_from_spec(s);s.loader.exec_module(m);'
            f'sys.stdout.buffer.write(m.encode({self.report!r}))'
        )
        process = subprocess.run(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
            timeout=30,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout, self.raw)


if __name__ == "__main__":
    unittest.main()
