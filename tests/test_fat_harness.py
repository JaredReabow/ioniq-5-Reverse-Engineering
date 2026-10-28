"""Tests for the FAT image harness."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "fat_harness.py"
SPEC = importlib.util.spec_from_file_location("fat_harness", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FatHarnessTests(unittest.TestCase):
    def _seed(self, temp: str, fat_bits: int = 32) -> Path:
        path = Path(temp) / f"seed{fat_bits}.img"
        MODULE.build_image(path, [("MAIN_LOOP.SH", b"#!/bin/bash\necho hi\n")], fat_bits)
        return path

    def test_built_images_are_structurally_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            for bits in (16, 32):
                result = MODULE.inspect_image(self._seed(temp, bits))
                self.assertEqual(result["anomalies"], [], f"FAT{bits}")
                self.assertEqual(result["fat_bits"], bits)
                self.assertEqual(result["boot_signature"], "0xaa55")

    def test_fat32_puts_root_in_cluster_two_and_data_at_three(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "s.img"
            info = MODULE.build_image(path, [("A.TXT", b"x")], 32)
            self.assertEqual(info["files"][0]["first_cluster"], 3)
            self.assertEqual(MODULE.inspect_image(path)["root_cluster"], 2)

    def test_file_size_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            info = MODULE.build_image(Path(temp) / "s.img", [("A.TXT", b"12345")], 16)
            self.assertEqual(info["files"][0]["size"], 5)

    def test_each_case_changes_the_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            seed = self._seed(temp).read_bytes()
            for case in MODULE.CASES:
                mutated = MODULE.apply_case(seed, case)
                self.assertNotEqual(mutated, seed, case)

    def test_specific_cases_hit_their_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            seed = self._seed(temp).read_bytes()
            self.assertEqual(MODULE.apply_case(seed, "bps_zero")[11:13], b"\x00\x00")
            self.assertEqual(MODULE.apply_case(seed, "spc_zero")[13], 0)
            self.assertEqual(MODULE.apply_case(seed, "boot_sig_bad")[510:512], b"\x00\x00")

    def test_inspect_flags_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            seed = self._seed(temp)
            cut = Path(temp) / "cut.img"
            cut.write_bytes(MODULE.apply_case(seed.read_bytes(), "truncated"))
            result = MODULE.inspect_image(cut)
            self.assertTrue(any("exceeds file size" in a for a in result["anomalies"]))

    def test_corpus_writes_every_case_plus_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            seed = self._seed(temp)
            out = Path(temp) / "corpus"
            rc = MODULE.main(["corpus", "--seed", str(seed), "--out", str(out)])
            self.assertEqual(rc, 0)
            index = json.loads((out / "corpus.json").read_text())
            self.assertEqual(len(index), len(MODULE.CASES))
            for name in MODULE.CASES:
                self.assertTrue((out / f"{name}.img").is_file(), name)


if __name__ == "__main__":
    unittest.main()
