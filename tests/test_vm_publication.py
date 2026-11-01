"""Verify that the public VM evidence manifests match the published files."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VmPublicationTests(unittest.TestCase):
    def test_published_vm_manifests(self) -> None:
        """Reject missing, changed, linked or out-of-tree evidence files."""
        for manifest_name, prefix, hash_key, size_key in (
            ("source-manifest.json", "vm/repro/", "published_sha256", "published_size"),
            ("evidence-manifest.json", "vm/evidence/", "sha256", "size"),
        ):
            with self.subTest(manifest=manifest_name):
                manifest = json.loads((ROOT / "vm" / manifest_name).read_text())
                self.assertEqual(manifest["schema_version"], 1)
                self.assertTrue(manifest["files"])
                paths: set[str] = set()
                for record in manifest["files"]:
                    relative = record["published"]
                    self.assertTrue(relative.startswith(prefix), relative)
                    self.assertNotIn("..", Path(relative).parts, relative)
                    self.assertNotIn(relative, paths)
                    paths.add(relative)
                    path = ROOT / relative
                    self.assertFalse(path.is_symlink(), relative)
                    self.assertTrue(path.is_file(), relative)
                    self.assertEqual(path.stat().st_size, record[size_key], relative)
                    self.assertEqual(
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                        record[hash_key],
                        relative,
                    )
