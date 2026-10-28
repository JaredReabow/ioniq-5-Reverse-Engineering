"""Tests for the CRC-32 forge utility.

The point of these tests is the security property, not the arithmetic: arbitrary
content changes can be hidden by a 4-byte correction while the CRC-32 stays
identical. That is why a CRC-32 manifest value cannot be an integrity control.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zlib
from pathlib import Path

TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "crc32_forge.py"
SPEC = importlib.util.spec_from_file_location("crc32_forge", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Crc32ForgeTests(unittest.TestCase):
    def test_preserves_crc_after_content_change(self) -> None:
        original = bytes(range(256)) * 4
        target = zlib.crc32(original) & 0xFFFFFFFF
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "src.bin"
            src.write_bytes(original)
            # change real content, then hide it in the correction window
            modified = bytearray(original)
            modified[300] ^= 0xFF
            src.write_bytes(bytes(modified))
            out = Path(temp) / "out.bin"
            result, correction = MODULE.forge(src, out, target, 8)
            forged = out.read_bytes()
        self.assertEqual(result, target)
        self.assertEqual(zlib.crc32(forged) & 0xFFFFFFFF, target)
        self.assertEqual(forged[300], original[300] ^ 0xFF)  # change preserved
        self.assertNotEqual(forged[8:12], original[8:12])    # correction applied
        self.assertEqual(correction, forged[8:12])

    def test_no_change_when_already_matching(self) -> None:
        data = b"already matching payload" * 3
        target = zlib.crc32(data) & 0xFFFFFFFF
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "src.bin"
            src.write_bytes(data)
            out = Path(temp) / "out.bin"
            result, _ = MODULE.forge(src, out, target, 0)
        self.assertEqual(result, target)

    def test_rejects_offset_outside_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "src.bin"
            src.write_bytes(b"short")
            with self.assertRaises(SystemExit):
                MODULE.forge(src, Path(temp) / "out.bin", 0, 10)

    def test_arbitrary_target_is_reachable(self) -> None:
        data = b"x" * 512
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "src.bin"
            src.write_bytes(data)
            out = Path(temp) / "out.bin"
            for target in (0x00000000, 0xFFFFFFFF, 0xDEADBEEF):
                result, _ = MODULE.forge(src, out, target, 100)
                self.assertEqual(result, target)


if __name__ == "__main__":
    unittest.main()
