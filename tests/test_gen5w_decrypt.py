"""Tests for the native LG Gen5W TE2 envelope parser/decryptor.

All fixtures are synthetic and generated under ``tempfile`` directories; nothing
here depends on ``Downloads`` or ``work/``. The trailing-metadata layout, IV
derivation and AES-128-CBC streaming path are exercised against the module under
test, and the historical ``build_plan`` external-mode helper is smoke-tested so
it cannot silently regress.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "gen5w_decrypt.py"
SPEC = importlib.util.spec_from_file_location("gen5w_decrypt", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def make_envelope(path: Path, body: bytes, discriminator: int = 0) -> Path:
    """Write a valid synthetic TE2 envelope whose plaintext is ``body``."""
    pad_len = (16 - len(body) % 16) % 16
    iv = MODULE.derive_iv(path, len(body))
    cipher = Cipher(algorithms.AES(MODULE.parse_key(MODULE.DEFAULT_KEY_HEX)),
                    modes.CBC(iv))
    enc = cipher.encryptor()
    full = enc.update(body + b"\x00" * pad_len) + enc.finalize()
    body_ct = full[:len(body)]
    pad_ct = full[len(body):]

    metadata = bytearray(MODULE.META_SIZE)
    metadata[0:3] = b"TE2"
    metadata[3] = discriminator
    metadata[36:36 + pad_len] = pad_ct
    metadata[4:36] = hashlib.sha256(iv + bytes(metadata[36:])).digest()

    path.write_bytes(body_ct + bytes(metadata))
    return path


class SignedInt32Tests(unittest.TestCase):
    def test_boundary_wrap_matches_xcrypt(self) -> None:
        self.assertEqual(MODULE.signed_int32(0), 0)
        self.assertEqual(MODULE.signed_int32(0x7FFFFFFF), 0x7FFFFFFF)
        self.assertEqual(MODULE.signed_int32(0x80000000), -0x80000000)
        self.assertEqual(MODULE.signed_int32(0xFFFFFFFF), -1)
        self.assertEqual(MODULE.signed_int32(0x100000000), 0)
        self.assertEqual(MODULE.signed_int32(0x100000001), 1)

    def test_iv_signed_wrap_uses_decimal_string_without_huge_files(self) -> None:
        # body_size 2**32 wraps to 0, 2**32-1 wraps to -1 in the IV material.
        self.assertEqual(
            MODULE.derive_iv("/tmp/foo.bin", 0x100000000),
            hashlib.sha256(b"foo.bin0").digest()[:16],
        )
        self.assertEqual(
            MODULE.derive_iv("/tmp/foo.bin", 0xFFFFFFFF),
            hashlib.sha256(b"foo.bin-1").digest()[:16],
        )

    def test_iv_uses_basename_not_full_path(self) -> None:
        self.assertEqual(
            MODULE.derive_iv("/a/foo.bin", 100),
            MODULE.derive_iv("/b/foo.bin", 100),
        )
        self.assertNotEqual(
            MODULE.derive_iv("/a/foo.bin", 100),
            MODULE.derive_iv("/a/bar.bin", 100),
        )


class ParseKeyTests(unittest.TestCase):
    def test_default_key_is_16_bytes(self) -> None:
        key = MODULE.parse_key(MODULE.DEFAULT_KEY_HEX)
        self.assertEqual(key, bytes.fromhex(MODULE.DEFAULT_KEY_HEX))
        self.assertEqual(len(key), 16)

    def test_invalid_hex_rejected(self) -> None:
        for bad in ("zz", "0x" + MODULE.DEFAULT_KEY_HEX, MODULE.DEFAULT_KEY_HEX[:-1], ""):
            with self.assertRaises(MODULE.DecryptError):
                MODULE.parse_key(bad)

    def test_wrong_length_rejected(self) -> None:
        for bad in ("00", MODULE.DEFAULT_KEY_HEX + "00"):
            with self.assertRaises(MODULE.DecryptError):
                MODULE.parse_key(bad)


class NativeRoundTripTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _roundtrip(self, body: bytes, chunk_size: int = 16) -> Path:
        src = self.root / "envelope.bin"
        make_envelope(src, body)
        out = self.root / "envelope.out"
        result = MODULE.decrypt_native(src, out, chunk_size=chunk_size)
        self.assertEqual(result["bytes_written"], len(body))
        self.assertEqual(result["body_size"], len(body))
        self.assertEqual(out.read_bytes(), body)
        return out

    def test_aligned_body_roundtrip(self) -> None:
        self._roundtrip(bytes(range(48)), chunk_size=16)

    def test_unaligned_body_roundtrip_exact_recovery(self) -> None:
        body = bytes(range(100))
        out = self._roundtrip(body, chunk_size=16)
        self.assertEqual(out.read_bytes(), body)

    def test_large_streaming_roundtrip(self) -> None:
        body = (b"TE2-payload-" * 20000)[:200_000]
        self._roundtrip(body, chunk_size=4096)

    def test_iv_basename_dependence_two_files_decrypt(self) -> None:
        body = bytes(range(100))
        a = self.root / "alpha.bin"
        b = self.root / "beta.bin"
        make_envelope(a, body)
        make_envelope(b, body)
        report_a = MODULE.analyze_envelope(a)
        report_b = MODULE.analyze_envelope(b)
        self.assertNotEqual(report_a["iv"], report_b["iv"])

        out_a = self.root / "alpha.out"
        out_b = self.root / "beta.out"
        MODULE.decrypt_native(a, out_a, chunk_size=16)
        MODULE.decrypt_native(b, out_b, chunk_size=16)
        self.assertEqual(out_a.read_bytes(), body)
        self.assertEqual(out_b.read_bytes(), body)

    def test_discriminator_byte3_is_opaque_and_not_validated(self) -> None:
        body = bytes(range(64))
        for disc in (0x00, 0x7F, 0xAB):
            src = self.root / f"disc{disc:02x}.bin"
            make_envelope(src, body, discriminator=disc)
            report = MODULE.analyze_envelope(src)
            self.assertEqual(report["byte3"], disc)
            out = self.root / f"disc{disc:02x}.out"
            MODULE.decrypt_native(src, out, chunk_size=16)
            self.assertEqual(out.read_bytes(), body)


class InspectReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_report_fields(self) -> None:
        body = bytes(range(100))
        src = make_envelope(self.root / "inspect.bin", body, discriminator=0xAB)
        raw = src.read_bytes()
        trailer = raw[-MODULE.META_SIZE:]

        report = MODULE.analyze_envelope(src)
        self.assertNotIn("error", report)
        self.assertEqual(report["total_size"], len(raw))
        self.assertEqual(report["body_size"], len(body))
        self.assertEqual(report["metadata_size"], MODULE.META_SIZE)
        self.assertEqual(report["magic_hex"], b"TE2\xab".hex())
        self.assertEqual(report["magic_ascii"], "TE2.")
        self.assertEqual(report["byte3"], 0xAB)
        self.assertEqual(report["byte3_hex"], "0xab")
        self.assertTrue(report["magic_valid"])
        self.assertEqual(report["iv"], MODULE.derive_iv(src, len(body)).hex())
        self.assertEqual(report["stored_metadata_sha256"],
                         report["calculated_metadata_sha256"])
        self.assertTrue(report["integrity_valid"])
        self.assertEqual(len(report["padding_hex"]), 32)
        self.assertEqual(report["signature_store_size"], 8176)
        self.assertEqual(report["key_store_size"], 8192)
        self.assertEqual(report["signature_store_sha256"],
                         hashlib.sha256(trailer[52:8228]).hexdigest())
        self.assertEqual(report["key_store_sha256"],
                         hashlib.sha256(trailer[8228:16420]).hexdigest())


class NegativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _envelope(self, name: str = "neg.bin", body: bytes = bytes(range(64))) -> Path:
        return make_envelope(self.root / name, body)

    def test_too_small_file_fails_closed(self) -> None:
        src = self.root / "small.bin"
        src.write_bytes(b"short")
        with self.assertRaisesRegex(MODULE.DecryptError, "too small"):
            MODULE.decrypt_native(src, self.root / "out.bin")
        report = MODULE.analyze_envelope(src)
        self.assertIn("error", report)
        self.assertFalse(report["integrity_valid"])

    def test_wrong_magic_fails_closed(self) -> None:
        src = self.root / "badmagic.bin"
        metadata = bytearray(MODULE.META_SIZE)
        metadata[0:4] = b"BAD!"
        src.write_bytes(bytes(16) + bytes(metadata))
        with self.assertRaisesRegex(MODULE.DecryptError, "magic"):
            MODULE.decrypt_native(src, self.root / "out.bin")
        self.assertFalse(MODULE.analyze_envelope(src)["magic_valid"])

    def test_integrity_mismatch_fails_closed(self) -> None:
        src = self._envelope()
        raw = bytearray(src.read_bytes())
        raw[-MODULE.META_SIZE + 100] ^= 0xFF  # flip a byte inside metadata[36:]
        src.write_bytes(bytes(raw))
        with self.assertRaisesRegex(MODULE.DecryptError, "integrity"):
            MODULE.decrypt_native(src, self.root / "out.bin")
        self.assertFalse(MODULE.analyze_envelope(src)["integrity_valid"])

    def test_bad_key_rejected_before_decrypt(self) -> None:
        src = self._envelope()
        for bad in ("zz", "00", MODULE.DEFAULT_KEY_HEX[:-1]):
            with self.assertRaises(MODULE.DecryptError):
                MODULE.decrypt_native(src, self.root / "out.bin", key_hex=bad)

    def test_invalid_chunk_size_rejected(self) -> None:
        src = self._envelope()
        for bad in (0, -16, 10, 15):
            with self.assertRaises(MODULE.DecryptError):
                MODULE.decrypt_native(src, self.root / "out.bin", chunk_size=bad)

    def test_same_path_refused_and_input_untouched(self) -> None:
        src = self._envelope()
        before = src.read_bytes()
        with self.assertRaises(MODULE.DecryptError):
            MODULE.decrypt_native(src, src)
        self.assertEqual(src.read_bytes(), before)

    def test_existing_output_refused_without_force(self) -> None:
        src = self._envelope()
        out = self.root / "existing.out"
        out.write_bytes(b"keep me")
        with self.assertRaises(MODULE.DecryptError):
            MODULE.decrypt_native(src, out)
        self.assertEqual(out.read_bytes(), b"keep me")

    def test_force_overwrites_existing_output(self) -> None:
        src = self._envelope()
        out = self.root / "existing.out"
        out.write_bytes(b"old")
        MODULE.decrypt_native(src, out, force=True, chunk_size=16)
        self.assertEqual(out.read_bytes(), bytes(range(64)))

    def test_cleanup_partial_output_after_midstream_failure(self) -> None:
        body = bytes(range(100))
        src = make_envelope(self.root / "partial.bin", body)
        out = self.root / "partial.out"

        real_read_exact = MODULE._read_exact
        calls = {"n": 0}

        def flaky(fh, n):
            calls["n"] += 1
            # Call 1 is the metadata read inside _analyze; fail on a later body read.
            if calls["n"] == 3:
                raise MODULE.DecryptError("forced mid-stream failure")
            return real_read_exact(fh, n)

        with mock.patch.object(MODULE, "_read_exact", side_effect=flaky):
            with self.assertRaises(MODULE.DecryptError):
                MODULE.decrypt_native(src, out, chunk_size=16)
        self.assertFalse(out.exists())

    def test_read_exact_short_read_raises(self) -> None:
        with self.assertRaises(MODULE.DecryptError):
            MODULE._read_exact(io.BytesIO(b"abc"), 10)


class BuildPlanCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_build_plan_still_produces_steps(self) -> None:
        pkg = self.root / "pkg"
        pkg.mkdir()
        common = b"\x00" * 128
        (pkg / "AppUpgrade").write_bytes(b"AAA" + common)
        (pkg / ".lge.upgrade.xml").write_bytes(b"BBBB" + common)

        plan = MODULE.build_plan(
            pkg, self.root / "out",
            ["AppUpgrade", ".lge.upgrade.xml", "missing.bin"],
            "cmd {input} {output} {key} {footer}", None,
        )
        self.assertEqual(plan["root"], str(pkg))
        self.assertEqual(plan["out"], str(self.root / "out"))
        self.assertEqual(plan["footer"], 128)
        self.assertIsInstance(plan["footer_note"], str)
        self.assertEqual(len(plan["steps"]), 2)
        for step in plan["steps"]:
            self.assertIn("input", step)
            self.assertIn("output", step)
            self.assertIn("size", step)
            self.assertIn("command", step)
            self.assertIn("128", step["command"])

    def test_build_plan_no_payloads_raises(self) -> None:
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaises(SystemExit):
            MODULE.build_plan(empty, self.root / "out", ["AppUpgrade"], "cmd {input}", None)


class CliCompatTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_cli_decrypt_end_to_end(self) -> None:
        body = bytes(range(64))
        src = make_envelope(self.root / "cli.bin", body)
        out = self.root / "cli.out"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = MODULE.main(["decrypt", str(src), str(out), "--chunk-size", "16"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.read_bytes(), body)

    def test_cli_inspect_invalid_returns_nonzero(self) -> None:
        bad = self.root / "bad.bin"
        bad.write_bytes(b"nope")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = MODULE.main(["inspect", str(bad)])
        self.assertEqual(rc, 1)
        self.assertIn("error", buf.getvalue())

    def test_cli_plan_subcommand_preserved(self) -> None:
        pkg = self.root / "pkg"
        pkg.mkdir()
        (pkg / "AppUpgrade").write_bytes(b"x" * 32)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = MODULE.main(["plan", "--root", str(pkg),
                              "--out", str(self.root / "out")])
        self.assertEqual(rc, 0)
        self.assertIn('"steps"', buf.getvalue())

    def test_cli_verify_subcommand_preserved(self) -> None:
        d = self.root / "plain"
        d.mkdir()
        (d / "a.txt").write_text("hello world, this is plaintext")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = MODULE.main(["verify", str(d)])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
