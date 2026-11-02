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
TOOL_PATH = ROOT / "tools/uk_fw/iap2_marshal_getbytes_audit.py"
FRAMEWORK = ROOT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libiAP2AppFramework-2.0.so"
SERVICE = ROOT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/iAP2Service-2.0"
RECOVERED_PRESENT = FRAMEWORK.is_file() and SERVICE.is_file()

spec = importlib.util.spec_from_file_location("iap2_marshal_getbytes_audit", TOOL_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Iap2MarshalGetBytesAuditTests(unittest.TestCase):
    def _synthetic_elf(self) -> bytes:
        payload = bytearray(0x300)
        ident = b"\x7fELF\x02\x01\x01" + b"\x00" * 9
        header = module.ELF_HEADER.pack(
            ident, 3, 62, 1, 0, module.ELF_HEADER.size, 0, 0,
            module.ELF_HEADER.size, module.PROGRAM_HEADER.size, 1, 0, 0, 0,
        )
        payload[: len(header)] = header
        program = module.PROGRAM_HEADER.pack(
            module.PT_LOAD, 5, 0x100, 0x1000, 0, 0x100, 0x180, 0x1000,
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

    @unittest.skipUnless(RECOVERED_PRESENT, "recovered firmware is not present")
    def test_exact_recovered_report(self) -> None:
        report = module.build_report(module.stable_read(FRAMEWORK), module.stable_read(SERVICE))
        self.assertEqual(report["schema"], module.SCHEMA)
        self.assertEqual(report["subjects"]["framework"]["sha256"], module.SUBJECTS["framework"]["sha256"])
        self.assertEqual(report["subjects"]["service"]["sha256"], module.SUBJECTS["service"]["sha256"])
        self.assertEqual(report["coverage"]["direct_static_call_count"], 31)
        self.assertEqual(report["coverage"]["direct_static_caller_count"], 11)
        self.assertEqual(report["coverage"]["heap_string_wrapper_call_count"], 22)
        self.assertEqual(report["coverage"]["heap_string_wrapper_caller_count"], 2)
        self.assertEqual(report["caller_semantics"]["SessionLocation"]["byte_fields"], 7)
        self.assertEqual(report["framework_anchors"]["get_length_store_and_bounded_accessor_call"]["elf_va"], "0x21ae3")
        self.assertEqual(report["findings"]["generic_helper"]["classification"], "bounded direct byte accessor")
        self.assertEqual(report["findings"]["null_return_consumer"]["classification"], "exact-static null-source denial-of-service candidate")
        self.assertEqual(report["service_support_ranges"]["variadic_logger"]["size"], 0x2D1)
        self.assertEqual(report["findings"]["percent_s_consumers"]["classification"], "exact-static unbounded-source-read candidates with bounded formatted output")

    @unittest.skipUnless(RECOVERED_PRESENT, "recovered firmware is not present")
    def test_cli_is_deterministic_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            command = [sys.executable, str(TOOL_PATH), str(FRAMEWORK), str(SERVICE)]
            subprocess.run(command + ["--output", str(first)], check=True)
            subprocess.run(command + ["--output", str(second)], check=True)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            parsed = json.loads(first.read_text(encoding="ascii"))
            self.assertEqual(parsed["schema"], module.SCHEMA)
            self.assertEqual(parsed["canonical_sha256"], "d5dc0a104ee3b9de9c148e9bfdbc578b75f54ed66eeb4ddfd3f76de58afceeb6")
            duplicate = subprocess.run(
                command + ["--output", str(first)], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=False,
            )
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn(b"File exists", duplicate.stderr)


if __name__ == "__main__":
    unittest.main()
