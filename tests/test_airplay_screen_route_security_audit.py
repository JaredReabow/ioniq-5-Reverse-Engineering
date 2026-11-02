from __future__ import annotations

import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/uk_fw/airplay_screen_route_security_audit.py"
LIB_DIR = ROOT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib"
AIRPLAY = LIB_DIR / "libAirPlay.so"
COREUTILS = LIB_DIR / "libCoreUtils.so"
RECOVERED_PRESENT = AIRPLAY.is_file() and COREUTILS.is_file()

spec = importlib.util.spec_from_file_location("airplay_screen_route_security_audit", TOOL_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AirPlayScreenRouteSecurityAuditTests(unittest.TestCase):
    def _synthetic_elf(self) -> bytes:
        payload = bytearray(0x300)
        ident = b"\x7fELF\x02\x01\x01" + b"\x00" * 9
        header = module.ELF_HEADER.pack(
            ident,
            3,
            62,
            1,
            0,
            module.ELF_HEADER.size,
            0,
            0,
            module.ELF_HEADER.size,
            module.PROGRAM_HEADER.size,
            1,
            0,
            0,
            0,
        )
        payload[: len(header)] = header
        program = module.PROGRAM_HEADER.pack(
            module.PT_LOAD,
            5,
            0x100,
            0x1000,
            0,
            0x100,
            0x180,
            0x1000,
        )
        start = module.ELF_HEADER.size
        payload[start : start + len(program)] = program
        return bytes(payload)

    def test_program_header_mapping_is_file_backed(self) -> None:
        segments = module.parse_load_segments(self._synthetic_elf())
        self.assertEqual(module.va_to_offset(segments, 0x1020, 4), 0x120)
        with self.assertRaises(module.AuditError):
            module.va_to_offset(segments, 0x10FF, 2)

    def test_rejects_non_elf_and_bad_geometry(self) -> None:
        with self.assertRaises(module.AuditError):
            module.parse_load_segments(b"not an ELF")
        malformed = bytearray(self._synthetic_elf())
        struct.pack_into("<Q", malformed, 32, 0x1000)
        with self.assertRaises(module.AuditError):
            module.parse_load_segments(bytes(malformed))

    def test_crypto_route_classification(self) -> None:
        self.assertIn("ChaCha20-Poly1305", module.classify_crypto_route(True, False))
        self.assertIn("session-base-key-derived AES-CTR", module.classify_crypto_route(False, True))
        self.assertIn("zero-session-base-key", module.classify_crypto_route(False, False))
        with self.assertRaises(module.AuditError):
            module.classify_crypto_route(1, False)

    @unittest.skipUnless(RECOVERED_PRESENT, "recovered firmware is not present")
    def test_exact_recovered_report(self) -> None:
        report = module.build_report(
            module.stable_read(AIRPLAY),
            module.stable_read(COREUTILS),
        )
        self.assertEqual(report["schema"], module.SCHEMA)
        self.assertEqual(report["route"]["setup_stream"]["type"], "0x6e")
        self.assertEqual(report["route"]["listener"]["ipv4_bind_address"], "INADDR_ANY (zero address)")
        self.assertFalse(report["route"]["listener"]["accepted_peer_address_requested_by_caller"])
        self.assertTrue(report["assessment"]["no_mfi_fallback_candidate"])
        self.assertIsNone(report["assessment"]["cve_attribution"])
        self.assertEqual(
            report["direct_offset_inventory"]["direct_explicit_store_pattern_count"],
            1,
        )
        self.assertIn(
            "AES-CTR",
            report["route"]["security"]["pair_verify_absent_without_installed_base_key"],
        )

    @unittest.skipUnless(RECOVERED_PRESENT, "recovered firmware is not present")
    def test_cli_is_deterministic_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            command = [sys.executable, str(TOOL_PATH), str(AIRPLAY), str(COREUTILS)]
            subprocess.run(command + ["--output", str(first)], check=True)
            subprocess.run(command + ["--output", str(second)], check=True)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            parsed = json.loads(first.read_text(encoding="ascii"))
            self.assertEqual(parsed["schema"], module.SCHEMA)
            duplicate = subprocess.run(
                command + ["--output", str(first)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn(b"File exists", duplicate.stderr)


if __name__ == "__main__":
    unittest.main()
