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
TOOL_PATH = ROOT / "tools/uk_fw/airplay_screen_parser_bounds_audit.py"
LIB_DIR = ROOT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib"
AIRPLAY = LIB_DIR / "libAirPlay.so"
MEDIA = LIB_DIR / "libCarPlayMediaFramework.so"
COREUTILS = LIB_DIR / "libCoreUtils.so"
RECOVERED_PRESENT = all(path.is_file() for path in (AIRPLAY, MEDIA, COREUTILS))

spec = importlib.util.spec_from_file_location("airplay_screen_bounds_audit", TOOL_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AirPlayScreenParserBoundsAuditTests(unittest.TestCase):
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

    def test_abstract_length_geometry_detects_expansion(self) -> None:
        result = module.conversion_geometry(4, 1, [0, 0, 0, 0])
        self.assertEqual(result["input_consumed"], 4)
        self.assertEqual(result["output_produced"], 16)
        self.assertEqual(result["capacity"], 8)
        self.assertTrue(result["out_of_bounds"])
        self.assertEqual(result["excess_bytes"], 8)

        bounded = module.conversion_geometry(8, 4, [0, 0])
        self.assertFalse(bounded["out_of_bounds"])
        with_header = module.conversion_geometry(8, 4, [0, 0], config_size=9)
        self.assertTrue(with_header["out_of_bounds"])

    def test_geometry_rejects_inconsistent_or_invalid_values(self) -> None:
        with self.assertRaises(module.AuditError):
            module.conversion_geometry(4, 3, [1])
        with self.assertRaises(module.AuditError):
            module.conversion_geometry(4, 1, [1])
        with self.assertRaises(module.AuditError):
            module.conversion_geometry(4, 1, [])
        with self.assertRaises(module.AuditError):
            module.conversion_geometry(True, 1, [0])

    @unittest.skipUnless(RECOVERED_PRESENT, "recovered firmware is not present")
    def test_exact_recovered_report(self) -> None:
        report = module.build_report(
            module.stable_read(AIRPLAY),
            module.stable_read(MEDIA),
            module.stable_read(COREUTILS),
        )
        self.assertEqual(report["schema"], module.SCHEMA)
        self.assertEqual(
            report["subjects"]["media"]["sha256"],
            module.SUBJECTS["media"]["sha256"],
        )
        self.assertEqual(
            report["ranges"]["screen_stream_process_data"]["size"], 0xB14
        )
        self.assertEqual(
            report["anchors"]["start_sets_first_frame_flag"]["bytes_hex"],
            "c6809800000001",
        )
        self.assertEqual(
            report["assessment"]["classification"],
            "exact-static heap out-of-bounds write candidate",
        )
        self.assertIn("CWE-787", report["assessment"]["cwe"])
        self.assertIsNone(report["assessment"]["cve_attribution"])
        self.assertIn(
            "does not establish a size-doubling integer wrap",
            report["arithmetic_proof"]["important_correction"],
        )

    @unittest.skipUnless(RECOVERED_PRESENT, "recovered firmware is not present")
    def test_cli_is_deterministic_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            command = [
                sys.executable,
                str(TOOL_PATH),
                str(AIRPLAY),
                str(MEDIA),
                str(COREUTILS),
            ]
            subprocess.run(command + ["--output", str(first)], check=True)
            subprocess.run(command + ["--output", str(second)], check=True)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            parsed = json.loads(first.read_text(encoding="ascii"))
            self.assertEqual(
                parsed["canonical_sha256"],
                "a01793627cae6f52c6befaf58c4e6c01cabfffd8e5a7494f3801fc00e5dcea54",
            )
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
