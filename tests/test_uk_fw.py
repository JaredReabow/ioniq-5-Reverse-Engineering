"""Tests for the Gen5W_L IPK inspection helper."""

from __future__ import annotations

import importlib.util
import gzip
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "inspect_ipk_kernel.py"
SPEC = importlib.util.spec_from_file_location("inspect_ipk_kernel", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class IpkInspectorTests(unittest.TestCase):
    """Validate safe rejection and deterministic hashing."""

    def test_sha256(self) -> None:
        self.assertEqual(
            MODULE.sha256(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_rejects_non_ipk_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "not-ipk.bin"
            path.write_bytes(b"not firmware")
            with self.assertRaisesRegex(ValueError, "ipk. magic"):
                MODULE.inspect_ipk(path)

    def test_decompresses_one_gzip_member_with_trailing_kernel_bytes(self) -> None:
        payload = b"CONFIG_IKCONFIG=y\n"
        carrier = gzip.compress(payload, mtime=0) + b"IKCFG_ED\x00kernel-data"
        self.assertEqual(MODULE.decompress_gzip_member(carrier), payload)

    def test_rejects_truncated_gzip_member(self) -> None:
        with self.assertRaisesRegex(ValueError, "truncated gzip stream"):
            MODULE.decompress_gzip_member(gzip.compress(b"config")[:8])


if __name__ == "__main__":
    unittest.main()
