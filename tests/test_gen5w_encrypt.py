"""Round-trip tests for the TE2 envelope writer."""

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from tools.uk_fw import gen5w_decrypt as gd
from tools.uk_fw import gen5w_encrypt as ge

PROJECT = Path(__file__).resolve().parents[1]
VENDOR_ENVELOPE = PROJECT / "work/firmware/IONIQ5_EU/HU/firmware/update.tar.gz"
HAVE_CRYPTO = True
try:
    gd._crypto()
except gd.DecryptError:
    HAVE_CRYPTO = False


@unittest.skipUnless(HAVE_CRYPTO, "the 'cryptography' package is required")
class EnvelopeRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def build(self, payload: bytes, name: str = "payload.bin") -> Path:
        plain = self.root / name
        plain.write_bytes(payload)
        return plain

    def test_round_trip_restores_the_payload_exactly(self):
        payload = bytes(range(256)) * 19 + b"tail"
        plain = self.build(payload)
        envelope = self.root / "payload.te2"
        report = ge.encrypt_native(plain, envelope)
        self.assertEqual(report["body_size"], len(payload))
        self.assertEqual(envelope.stat().st_size, len(payload) + gd.META_SIZE)
        self.assertTrue(ge.verify_round_trip(envelope, plain))

    def test_envelope_passes_the_vendor_integrity_check(self):
        plain = self.build(b"x" * 4096)
        envelope = self.root / "aligned.te2"
        ge.encrypt_native(plain, envelope)
        report, meta = gd._analyze(envelope)
        self.assertTrue(report["magic_valid"])
        self.assertTrue(report["integrity_valid"])
        # A block-aligned payload leaves no ciphertext tail to store.
        self.assertEqual(report["padding_hex"][:2], "00")
        self.assertEqual(meta[3], 0)

    def test_reference_to_missing_template_is_refused(self):
        plain = self.build(b"y" * 100)
        with self.assertRaises(ge.EncryptError):
            ge.encrypt_native(plain, self.root / "out.te2",
                              template_path=self.root / "absent.te2")

    def test_same_input_and_output_is_refused(self):
        plain = self.build(b"z" * 100)
        with self.assertRaises(ge.EncryptError):
            ge.encrypt_native(plain, plain)

    def test_existing_output_is_not_overwritten_silently(self):
        plain = self.build(b"w" * 100)
        envelope = self.root / "existing.te2"
        envelope.write_bytes(b"keep me")
        with self.assertRaises(ge.EncryptError):
            ge.encrypt_native(plain, envelope)
        self.assertEqual(envelope.read_bytes(), b"keep me")


@unittest.skipUnless(HAVE_CRYPTO and VENDOR_ENVELOPE.is_file(),
                     "the vendor envelope and 'cryptography' are required")
class VendorEnvelopeReproductionTests(unittest.TestCase):
    """Re-encrypting a decrypted vendor payload must reproduce its exact bytes."""

    def test_reencrypting_a_vendor_payload_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            # The IV depends on the basename, so the payload keeps its own name.
            plaintext = work / VENDOR_ENVELOPE.name
            gd.decrypt_native(VENDOR_ENVELOPE, plaintext)
            rebuilt = work / "rebuilt" / VENDOR_ENVELOPE.name
            rebuilt.parent.mkdir()
            report = ge.encrypt_native(plaintext, rebuilt, template_path=VENDOR_ENVELOPE)
            digest = hashlib.sha256(rebuilt.read_bytes()).hexdigest()
            self.assertEqual(digest, hashlib.sha256(VENDOR_ENVELOPE.read_bytes()).hexdigest())
            self.assertEqual(report["plaintext_size"], VENDOR_ENVELOPE.stat().st_size - gd.META_SIZE)
            self.assertEqual(report["total_size"], VENDOR_ENVELOPE.stat().st_size)


if __name__ == "__main__":
    unittest.main()
