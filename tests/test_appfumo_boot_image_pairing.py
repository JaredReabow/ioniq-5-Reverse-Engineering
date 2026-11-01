from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import stat
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/uk_fw/appfumo_boot_image_pairing.py"
ELF = ROOT / "work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf"
ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
REPORT = ROOT / "evidence/artifacts/update-candidates/appfumo-boot-image-pairing.json"

_spec = importlib.util.spec_from_file_location("appfumo_boot_image_pairing", TOOL_PATH)
assert _spec and _spec.loader
mod = importlib.util.module_from_spec(_spec)
import sys
sys.modules[_spec.name] = mod
_spec.loader.exec_module(mod)


class BootImagePairingTests(unittest.TestCase):
    def archive(self, rows: list[tuple[str, bytes, bytes, str]]) -> tuple[bytes, mod.MemberExpectation]:
        selected = b"#!/bin/sh\necho bounded\n"
        expectation = mod.MemberExpectation(
            "./lib/systemd/esinit", 0o755, 0, 0, len(selected),
            hashlib.sha256(selected).hexdigest()
        )
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode="w:gz") as archive:
            for name, member_type, content, linkname in rows:
                info = tarfile.TarInfo(name)
                info.type = member_type
                info.mode = 0o755
                info.linkname = linkname
                info.size = len(content) if member_type in (tarfile.REGTYPE, tarfile.AREGTYPE) else 0
                archive.addfile(info, io.BytesIO(content) if info.size else None)
        return out.getvalue(), expectation

    def scan(self, raw: bytes, expectation: mod.MemberExpectation):
        return mod.scan_archive_handle(io.BytesIO(raw), len(raw), expectation)

    def test_canonical_selected_regular_member(self):
        selected = b"#!/bin/sh\necho bounded\n"
        raw, expectation = self.archive([
            (".", tarfile.DIRTYPE, b"", ""),
            ("./lib/systemd/esinit", tarfile.REGTYPE, selected, ""),
        ])
        result = self.scan(raw, expectation)
        self.assertEqual(result.member_bytes, selected)
        self.assertEqual(result.member_count, 2)
        self.assertEqual(result.sha256, hashlib.sha256(raw).hexdigest())

    def test_selected_alias_is_rejected(self):
        selected = b"#!/bin/sh\necho bounded\n"
        raw, expectation = self.archive([
            ("lib/systemd/esinit", tarfile.REGTYPE, selected, ""),
        ])
        with self.assertRaisesRegex(mod.Failure, "through an alias"):
            self.scan(raw, expectation)

    def test_internal_single_dot_spelling_is_rejected(self):
        selected = b"#!/bin/sh\necho bounded\n"
        raw, expectation = self.archive([
            ("./lib/./systemd/esinit", tarfile.REGTYPE, selected, ""),
        ])
        with self.assertRaisesRegex(mod.Failure, "unsafe archive member spelling"):
            self.scan(raw, expectation)

    def test_dotdot_spelling_is_rejected(self):
        selected = b"#!/bin/sh\necho bounded\n"
        raw, expectation = self.archive([
            ("./lib/../lib/systemd/esinit", tarfile.REGTYPE, selected, ""),
        ])
        with self.assertRaisesRegex(mod.Failure, "unsafe archive member spelling"):
            self.scan(raw, expectation)

    def test_duplicate_selected_member_is_rejected(self):
        selected = b"#!/bin/sh\necho bounded\n"
        raw, expectation = self.archive([
            ("./lib/systemd/esinit", tarfile.REGTYPE, selected, ""),
            ("./lib/systemd/esinit", tarfile.REGTYPE, selected, ""),
        ])
        with self.assertRaisesRegex(mod.Failure, "duplicated"):
            self.scan(raw, expectation)

    def test_selected_links_are_rejected(self):
        for link_type in (tarfile.SYMTYPE, tarfile.LNKTYPE):
            with self.subTest(link_type=link_type):
                raw, expectation = self.archive([
                    ("./lib/systemd/esinit", link_type, b"", "elsewhere"),
                ])
                with self.assertRaisesRegex(mod.Failure, "metadata drift"):
                    self.scan(raw, expectation)

    def test_selected_wrong_owner_is_rejected(self):
        selected = b"#!/bin/sh\necho bounded\n"
        _, expectation = self.archive([
            ("./lib/systemd/esinit", tarfile.REGTYPE, selected, ""),
        ])
        # Rebuild rather than mutate gzip bytes: the helper fixture defaults to uid 0.
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode="w:gz") as archive:
            info = tarfile.TarInfo("./lib/systemd/esinit")
            info.type = tarfile.REGTYPE
            info.mode = 0o755
            info.uid = 1000
            info.gid = 0
            info.size = len(selected)
            archive.addfile(info, io.BytesIO(selected))
        with self.assertRaisesRegex(mod.Failure, "metadata drift"):
            self.scan(out.getvalue(), expectation)

    def test_selected_special_node_is_rejected(self):
        raw, expectation = self.archive([
            ("./lib/systemd/esinit", tarfile.FIFOTYPE, b"", ""),
        ])
        with self.assertRaisesRegex(mod.Failure, "metadata drift"):
            self.scan(raw, expectation)

    def test_symlink_input_is_rejected_without_following(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.write_bytes(b"safe")
            link = root / "link"
            link.symlink_to(target)
            with self.assertRaises(mod.Failure):
                mod.stable_read(link, 1024, "fixture")

    def test_malformed_elf_is_rejected(self):
        with self.assertRaises(mod.Failure):
            mod.parse_elf(b"\x7fELF" + b"\0" * 100)

    def test_exclusive_output_and_fixed_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            payload = b"{}\n"
            mod.write_exclusive(path, payload)
            self.assertEqual(path.read_bytes(), payload)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            with self.assertRaises(mod.Failure):
                mod.write_exclusive(path, payload)

    def test_deterministic_utf8_lf_encoding(self):
        value = {"z": "PLK", "a": [1, None, False]}
        first = mod.encode_report(value)
        second = mod.encode_report(value)
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertNotIn(b"\r", first)
        self.assertEqual(json.loads(first.decode("utf-8")), value)

    @unittest.skipUnless(ELF.is_file(), "exact ignored AppFUMO ELF is unavailable")
    def test_exact_elf_contract(self):
        result = mod.audit_elf(ELF)
        self.assertEqual(result["sha256"], mod.ELF_SHA256)
        self.assertEqual(result["build_id"], mod.ELF_BUILD_ID)
        self.assertEqual(
            result["direct_calls"]["staging_copy_normal"]["target"],
            result["direct_calls"]["staging_copy_sub"]["target"],
        )

    @unittest.skipUnless(ELF.is_file() and ROOTFS.is_file() and REPORT.is_file(),
                         "exact ignored artifacts or tracked report are unavailable")
    def test_exact_report_reproduces_and_preserves_boundaries(self):
        report = mod.build_report(ELF, ROOTFS)
        payload = mod.encode_report(report)
        self.assertEqual(payload, REPORT.read_bytes())
        decoded = json.loads(payload.decode("utf-8"))
        conclusions = decoded["conclusions"]
        self.assertTrue(conclusions["inactive_root_record_to_boot_filename_pairing"])
        self.assertTrue(conclusions["normal_and_sub_companion_staging_paths_present"])
        self.assertTrue(conclusions["copy_helper_success_requires_equal_final_sizes"])
        self.assertFalse(conclusions["copy_helper_proves_destination_byte_identity"])
        self.assertIsNone(conclusions["persistent_boot_target_selected"])
        self.assertFalse(conclusions["root_or_persistence_established"])
        self.assertNotIn(str(ELF), payload.decode("utf-8"))
        self.assertNotIn(str(ROOTFS), payload.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
