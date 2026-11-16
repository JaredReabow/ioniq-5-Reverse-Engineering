"""Safety tests for the offline EU 260128 setup helper."""

from __future__ import annotations

import io
import importlib.util
from pathlib import Path
import tarfile
import tempfile
import unittest

PROJECT = Path(__file__).parents[1]
TOOL = PROJECT / "tools/uk_fw/setup_eu260128.py"
SPEC = importlib.util.spec_from_file_location("setup_eu260128", TOOL)
SETUP = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SETUP)


def add_file(archive, name: str, payload: bytes) -> None:
    member = tarfile.TarInfo(name)
    member.size = len(payload)
    member.mode = 0o644
    archive.addfile(member, io.BytesIO(payload))


class SafeExtractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_regular_files_and_guest_root_symlinks_extract_safely(self):
        archive_path = self.root / "valid.tar"
        with tarfile.open(archive_path, "w") as archive:
            add_file(archive, "root/lib/file.so", b"library")
            link = tarfile.TarInfo("root/lib64")
            link.type = tarfile.SYMTYPE
            link.linkname = "/root/lib"
            archive.addfile(link)
        output = self.root / "out"

        summary = SETUP.safe_extract_tar(archive_path, output)

        self.assertEqual((output / "root/lib/file.so").read_bytes(), b"library")
        self.assertTrue((output / "root/lib64").is_symlink())
        self.assertEqual((output / "root/lib64").resolve(), (output / "root/lib").resolve())
        self.assertEqual(summary["files"], 1)
        self.assertEqual(summary["symlinks"], 1)
        self.assertFalse(summary["ownership_preserved"])

    def test_parent_traversal_is_rejected(self):
        archive_path = self.root / "traversal.tar"
        with tarfile.open(archive_path, "w") as archive:
            add_file(archive, "../../outside.txt", b"no")
        output = self.root / "out"

        with self.assertRaisesRegex(SETUP.SetupError, "escapes"):
            SETUP.safe_extract_tar(archive_path, output)
        self.assertFalse((self.root.parent / "outside.txt").exists())

    def test_link_target_outside_root_is_rejected(self):
        archive_path = self.root / "link.tar"
        with tarfile.open(archive_path, "w") as archive:
            link = tarfile.TarInfo("root/escape")
            link.type = tarfile.SYMTYPE
            link.linkname = "../../outside"
            archive.addfile(link)
        output = self.root / "out"

        with self.assertRaisesRegex(SETUP.SetupError, "link escapes"):
            SETUP.safe_extract_tar(archive_path, output)
        self.assertFalse((self.root.parent / "outside").exists())
