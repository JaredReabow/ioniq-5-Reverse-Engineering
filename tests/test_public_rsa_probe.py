"""Synthetic controls for the bounded public-RSA probe; no firmware required."""
import hashlib
import struct
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from tools.uk_fw import public_rsa_probe as probe


class PublicRSAProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.public = cls.private.public_key()
        cls.message = b"offline public RSA positive control"
        cls.signature = cls.private.sign(cls.message, padding.PKCS1v15(), hashes.SHA256())
        cls.digestinfo = probe.ipk_tool.DIGESTINFO_SHA256 + hashlib.sha256(cls.message).digest()

    def test_signature_control(self):
        self.assertEqual(probe.recover(self.public, self.signature), self.digestinfo)

    def test_non_digest_type_one_wrapped_data(self):
        data = b"synthetic-key-16"
        self.assertEqual(len(data), 16)
        em = b"\x00\x01" + b"\xff" * 237 + b"\x00" + data
        n = self.private.private_numbers()
        block = pow(int.from_bytes(em, "big"), n.d, n.public_numbers.n).to_bytes(256, "big")
        self.assertEqual(probe.recover(self.public, block), data)
        hit = probe.scan_bytes(block, self.public)["hits"][0]
        self.assertEqual(hit["recovered_length"], 16)
        self.assertEqual(hit["classification"], "unclassified-type1-data")

    def test_load_boot_key_checks_the_signed_bytes(self):
        raw = bytearray(b"ipk." + struct.pack("<12I", 0x30300, 0, 1024, 52, 1024,
                                             0, 0, 0, 0, 0, 0, 0))
        trailer = 52 + 1024
        raw.extend(b"\x00" * (trailer + 4 - len(raw)))
        signature = self.private.sign(bytes(raw), padding.PKCS1v15(), hashes.SHA256())
        raw.extend(b"\xff" * 252 + signature)
        raw.extend(self.public.public_numbers().n.to_bytes(256, "big"))
        raw.extend(struct.pack("<I", 65537))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.ipk"
            path.write_bytes(raw)
            key, source = probe.load_boot_key(path)
            self.assertEqual(key.public_numbers(), self.public.public_numbers())
            self.assertEqual(source["sha256"], probe.sha256(raw))
            raw[100] ^= 1
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "positive control"):
                probe.load_boot_key(path)

    def test_strict_padding_rejects_type_two(self):
        # Construct a type-2 encoded block with the synthetic private key.
        em = b"\x00\x02" + b"\x11" * 237 + b"\x00" + b"example-aes-key!"
        self.assertEqual(len(em), 256)
        n = self.private.private_numbers()
        block = pow(int.from_bytes(em, "big"), n.d, n.public_numbers.n).to_bytes(256, "big")
        self.assertIsNone(probe.recover(self.public, block))

    def test_strict_padding_rejects_short_type_one_padding(self):
        em = b"\x00\x01" + b"\xff" * 7 + b"\x00" + b"x" * 246
        n = self.private.private_numbers()
        block = pow(int.from_bytes(em, "big"), n.d, n.public_numbers.n).to_bytes(256, "big")
        self.assertIsNone(probe.recover(self.public, block))

    def test_bad_width_and_zero(self):
        for block in (b"", b"x" * 255, b"x" * 257, b"\x00" * 256, b"\xff" * 256):
            self.assertIsNone(probe.recover(self.public, block))

    def test_big_endian_unaligned_at_last_possible_start(self):
        result = probe.scan_bytes(b"prefix!" + self.signature, self.public)
        self.assertEqual(result["positions"], 8)
        self.assertEqual(result["rsa_attempts"], 16)
        self.assertEqual(len(result["hits"]), 1)
        hit = result["hits"][0]
        self.assertEqual((hit["offset"], hit["byte_order"]), (7, "big"))
        self.assertEqual(hit["classification"], "sha256-DigestInfo-shaped")
        self.assertNotIn(self.digestinfo.hex(), str(result))

    def test_little_endian(self):
        hits = probe.scan_bytes(self.signature[::-1], self.public)["hits"]
        self.assertEqual([(h["offset"], h["byte_order"]) for h in hits], [(0, "little")])

    def test_short_data(self):
        self.assertEqual(probe.scan_bytes(b"x" * 255, self.public),
                         {"positions": 0, "rsa_attempts": 0, "hits": []})

    def test_edge_ranges_merge(self):
        self.assertEqual(probe.edge_ranges(0, 256), [])
        self.assertEqual(probe.edge_ranges(511, 256), [(0, 511)])
        self.assertEqual(probe.edge_ranges(512, 256), [(0, 512)])
        self.assertEqual(probe.edge_ranges(513, 256), [(0, 256), (257, 513)])

    def test_invalid_ranges_and_orders(self):
        for size, window in ((-1, 256), (1, 255), (1, 1048577)):
            with self.assertRaises(ValueError):
                probe.edge_ranges(size, window)
        for orders in ((), ("big", "big"), ("unknown",)):
            with self.assertRaises(ValueError):
                probe.scan_bytes(b"", self.public, orders)

    def test_file_offset_and_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample"
            raw = b"z" * 1000 + self.signature
            path.write_bytes(raw)
            result = probe.scan_file(path, self.public, 256)
            self.assertEqual(result["hits"][0]["offset"], 1000)
            self.assertEqual(result["regions"][-1]["sha256"], probe.sha256(self.signature))
            self.assertEqual(path.read_bytes(), raw)

    def test_existing_output_refused_before_reading_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "existing.json"
            out.write_text("keep")
            with self.assertRaises(SystemExit):
                probe.main(["--container", "absent", "--input", "absent", "--output", str(out)])
            self.assertEqual(out.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
