"""Tests for the ipk. boot-container tool.

Builds synthetic containers in memory so the parser, the signature verifier and
the re-signing path can be exercised without any firmware artifact on disk.
"""

from __future__ import annotations

import hashlib
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "ipk_tool.py"
SPEC = importlib.util.spec_from_file_location("ipk_tool", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

HEADER_SIZE = 0x34
CMDLINE_SIZE = 0x80


def _sign(container: bytearray, private_key, trailer_off: int) -> None:
    digest = hashlib.sha256(bytes(container[: trailer_off + 4])).digest()
    em = MODULE.encode_pkcs1_v15_sha256(digest, 256)
    numbers = private_key.private_numbers()
    signature = pow(int.from_bytes(em, "big"), numbers.d, numbers.public_numbers.n)
    container[trailer_off + 0x100 : trailer_off + 0x200] = signature.to_bytes(256, "big")
    container[trailer_off + 0x200 : trailer_off + 0x300] = numbers.public_numbers.n.to_bytes(256, "big")
    struct.pack_into("<I", container, trailer_off + 0x300, 65537)


def make_container(cmdline: bytes, payload: bytes, private_key) -> bytes:
    total = CMDLINE_SIZE + len(payload)  # total runs from header end to trailer
    header = bytearray(HEADER_SIZE)
    header[0:4] = MODULE.MAGIC
    struct.pack_into("<i", header, 4, 0x00030300)
    struct.pack_into("<I", header, 0x0C, total)
    struct.pack_into("<I", header, 0x10, HEADER_SIZE)
    struct.pack_into("<I", header, 0x14, total)
    struct.pack_into("<I", header, 0x18, 0x42F08D94)
    struct.pack_into("<I", header, 0x1C, CMDLINE_SIZE)
    body = bytes(header) + cmdline.ljust(CMDLINE_SIZE, b"\x00") + payload
    trailer_off = len(body)
    trailer = bytearray(0x304)
    trailer[0:4] = b"\xfd\x45\x78\xf5"
    for i in range(4, 0x100):
        trailer[i] = 0xFF
    container = bytearray(body + bytes(trailer))
    _sign(container, private_key, trailer_off)
    return bytes(container)


class IpkToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.container = make_container(b"console=ttyS2,115200n8 root=/dev/mmcblk0p3", b"payload-bytes", cls.key)

    def _write(self, directory: str, name: str = "image_sub") -> Path:
        path = Path(directory) / name
        path.write_bytes(self.container)
        return path

    def test_parse_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            info = MODULE.parse(self._write(temp))
        self.assertEqual(info["header"]["header_size"], HEADER_SIZE)
        self.assertEqual(info["header"]["build_id"], "0x42f08d94")
        self.assertEqual(info["exponent"], 65537)
        self.assertTrue(info["cmdline"].startswith("console=ttyS2"))
        self.assertEqual(info["modulus_bits"], 2048)

    def test_signature_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = MODULE.verify(MODULE.parse(self._write(temp)))
        self.assertTrue(result["ok"])
        self.assertTrue(result["digest_matches"])

    def test_detects_payload_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self._write(temp)
            raw = bytearray(path.read_bytes())
            raw[HEADER_SIZE + CMDLINE_SIZE + 2] ^= 0xFF  # flip one payload byte
            path.write_bytes(bytes(raw))
            result = MODULE.verify(MODULE.parse(path))
        self.assertFalse(result["ok"])
        self.assertFalse(result["digest_matches"])

    def test_detects_tag_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self._write(temp)
            raw = bytearray(path.read_bytes())
            trailer = HEADER_SIZE + struct.unpack_from("<I", raw, 0x0C)[0]
            raw[trailer] ^= 0xFF  # tag is inside the signed range
            path.write_bytes(bytes(raw))
            result = MODULE.verify(MODULE.parse(path))
        self.assertFalse(result["ok"])

    def test_rejects_non_ipk(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "junk"
            path.write_bytes(b"not a container")
            with self.assertRaisesRegex(MODULE.ContainerError, "ipk."):
                MODULE.parse(path)

    def test_resign_replaces_key_and_cmdline(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            src = self._write(temp)
            key_path = Path(temp) / "test.pem"
            key_path.write_bytes(
                self.key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            )
            out = Path(temp) / "re-signed"
            result = MODULE.resign(MODULE.parse(src), out, key_path,
                                   "init=/bin/sh", "aabbccdd")
            reparsed = MODULE.parse(out)
            verified = MODULE.verify(reparsed)
        self.assertTrue(result["self_signed"])
        self.assertTrue(verified["ok"])
        self.assertEqual(reparsed["cmdline"], "init=/bin/sh")
        self.assertEqual(reparsed["tag"], "aabbccdd")

    def test_resign_rejects_oversized_cmdline(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            src = self._write(temp)
            key_path = Path(temp) / "test.pem"
            key_path.write_bytes(
                self.key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            )
            with self.assertRaisesRegex(MODULE.ContainerError, "field is"):
                MODULE.resign(MODULE.parse(src), Path(temp) / "out", key_path, "x" * 999, None)

    def test_encoded_digestinfo_is_pkcs1_v15(self) -> None:
        em = MODULE.encode_pkcs1_v15_sha256(b"\x00" * 32, 256)
        self.assertTrue(em.startswith(b"\x00\x01\xff"))
        self.assertIn(MODULE.DIGESTINFO_SHA256, em)
        self.assertEqual(len(em), 256)


if __name__ == "__main__":
    unittest.main()
