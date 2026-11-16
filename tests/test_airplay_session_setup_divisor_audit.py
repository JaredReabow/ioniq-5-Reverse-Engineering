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
TOOL_PATH = ROOT / "tools/uk_fw/airplay_session_setup_divisor_audit.py"
RECOVERED = (
    ROOT
    / "work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libAirPlay.so"
)

spec = importlib.util.spec_from_file_location("airplay_divisor_audit", TOOL_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AirPlaySessionSetupDivisorAuditTests(unittest.TestCase):
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

    def test_program_header_mapping_uses_file_backed_load_segment(self) -> None:
        segments = module.parse_load_segments(self._synthetic_elf())
        self.assertEqual(module.va_to_offset(segments, 0x1020, 4), 0x120)
        with self.assertRaises(module.AuditError):
            module.va_to_offset(segments, 0x10FF, 2)

    def test_rejects_non_elf_and_bad_bounds(self) -> None:
        with self.assertRaises(module.AuditError):
            module.parse_load_segments(b"not an ELF")
        malformed = bytearray(self._synthetic_elf())
        struct.pack_into("<Q", malformed, 32, 0x1000)
        with self.assertRaises(module.AuditError):
            module.parse_load_segments(bytes(malformed))

    @unittest.skipUnless(RECOVERED.is_file(), "recovered firmware is not present")
    def test_exact_recovered_report(self) -> None:
        report = module.build_report(module.stable_read(RECOVERED))
        self.assertEqual(report["schema"], module.SCHEMA)
        self.assertEqual(report["subject"]["sha256"], module.EXPECTED_SHA256)
        self.assertEqual(
            report["ranges"]["AirPlayReceiverSessionSetup"]["size"], 0x28C0
        )
        self.assertEqual(
            report["anchors"]["unsigned_divide"]["bytes_hex"], "f7f1"
        )
        self.assertEqual(
            report["decoded_flow"]["main_high_audio_selection"]["frames_per_packet_key_exact"],
            "spf",
        )
        self.assertEqual(
            report["assessment"]["classification"],
            "exact-static denial-of-service candidate",
        )
        self.assertFalse(report["assessment"]["mfi_sap_required_for_this_candidate"])
        self.assertIsNone(report["assessment"]["cve_attribution"])

    @unittest.skipUnless(RECOVERED.is_file(), "recovered firmware is not present")
    def test_cli_is_deterministic_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            command = [sys.executable, str(TOOL_PATH), str(RECOVERED)]
            subprocess.run(command + ["--output", str(first)], check=True)
            subprocess.run(command + ["--output", str(second)], check=True)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            parsed = json.loads(first.read_text(encoding="ascii"))
            self.assertEqual(parsed["canonical_sha256"], "e4eb3df14e54bd65c9fe3b52ea839d579eccae6989a495afab0fb2b8bbc7d527")
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
