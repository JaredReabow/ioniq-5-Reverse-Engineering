"""Tests for the .ver manifest parser and verifier."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zlib
from pathlib import Path

TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "ver_manifest.py"
SPEC = importlib.util.spec_from_file_location("ver_manifest", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

PACKAGE = "IONIQ5_EU"


def signed(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - (1 << 32) if value & 0x80000000 else value


class VerManifestTests(unittest.TestCase):
    def _build(self, root: Path) -> Path:
        files = {
            "AppUpgrade": b"top-level payload",
            "HU/images/iasImage_1280_sub": b"nested payload",
        }
        lines = [f"+|21393|NE_E.EUR.S5W_L.001.001.260128|HM|{PACKAGE}|101489|1"]
        for index, (rel, data) in enumerate(files.items(), start=341142):
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            parent = str(Path(rel).parent)
            win = PACKAGE + ("\\" + parent.replace("/", "\\") if parent != "." else "")
            lines.append(f"{win}|{Path(rel).name}|{index}|{signed(zlib.crc32(data))}|{len(data)}|1")
        manifest = root / f"{PACKAGE}.ver"
        manifest.write_text("\n".join(lines) + "\n")
        return manifest

    def test_parse_strips_package_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            parsed = MODULE.parse(self._build(root))
        self.assertEqual(parsed["package"]["version"], "NE_E.EUR.S5W_L.001.001.260128")
        self.assertEqual([r["path"] for r in parsed["records"]],
                         ["AppUpgrade", "HU/images/iasImage_1280_sub"])

    def test_verify_all_ok(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = MODULE.verify(MODULE.parse(self._build(root)), root, 2048, False)
        self.assertEqual(result["summary"], {"ok": 2, "mismatch": 0, "missing": 0,
                                             "skipped_large": 0, "total": 2})

    def test_verify_detects_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self._build(root)
            (root / "AppUpgrade").write_bytes(b"tampered!!")
            result = MODULE.verify(MODULE.parse(manifest), root, 2048, False)
        self.assertEqual(result["summary"]["mismatch"], 1)
        self.assertEqual(result["records"][0]["status"], "mismatch")

    def test_verify_detects_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self._build(root)
            (root / "AppUpgrade").unlink()
            result = MODULE.verify(MODULE.parse(manifest), root, 2048, False)
        self.assertEqual(result["summary"]["missing"], 1)

    def test_skip_large(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self._build(root)
            result = MODULE.verify(MODULE.parse(manifest), root, 0, False)
        self.assertEqual(result["summary"]["skipped_large"], 2)


if __name__ == "__main__":
    unittest.main()
