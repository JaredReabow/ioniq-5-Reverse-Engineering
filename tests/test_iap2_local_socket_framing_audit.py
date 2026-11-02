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
TOOL_PATH = ROOT / "tools/uk_fw/iap2_local_socket_framing_audit.py"
ROOTFS = ROOT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"
FRAMEWORK = ROOTFS / "app/lib/libiAP2AppFramework-2.0.so"
SERVICE = ROOTFS / "app/bin/iAP2Service-2.0"
UNIT = ROOTFS / "lib/systemd/system/carplay_iAP2.service"
RELABEL = ROOTFS / "etc/smack-relabel-ro.sh"
SMACK_DIR = ROOTFS / "etc/smack/accesses.d"
RECOVERED_PRESENT = all(path.exists() for path in (FRAMEWORK, SERVICE, UNIT, RELABEL, SMACK_DIR))

spec = importlib.util.spec_from_file_location("iap2_local_socket_framing_audit", TOOL_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Iap2LocalSocketFramingAuditTests(unittest.TestCase):
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

    def test_file_backed_mapping_and_relative_call_decoder(self) -> None:
        payload = bytearray(self._synthetic_elf())
        call_va = 0x1020
        target = 0x1080
        payload[0x120:0x125] = b"\xe8" + struct.pack("<i", target - (call_va + 5))
        segments = module.parse_load_segments(bytes(payload))
        self.assertEqual(module.va_to_offset(segments, call_va, 5), 0x120)
        decoded = module.verify_rel_call(bytes(payload), segments, call_va, target)
        self.assertEqual(decoded["target_elf_va"], "0x1080")

    def test_rejects_non_elf_and_bad_smack_syntax(self) -> None:
        with self.assertRaises(module.AuditError):
            module.parse_load_segments(b"not an ELF")
        with self.assertRaises(module.AuditError):
            module.parse_smack_rules({"bad": b"subject object invalid!\n"})

    @unittest.skipUnless(RECOVERED_PRESENT, "recovered firmware is not present")
    def test_exact_recovered_report(self) -> None:
        report = module.build_report(
            module.stable_read(FRAMEWORK), module.stable_read(SERVICE),
            module.stable_read(UNIT), module.stable_read(RELABEL),
            module.stable_read_directory(SMACK_DIR),
        )
        self.assertEqual(report["schema"], module.SCHEMA)
        self.assertEqual(report["producer_inventory"]["direct_send_event_call_count"], 37)
        self.assertEqual(report["producer_inventory"]["dynamic_capacity_producer_count"], 9)
        self.assertEqual(report["local_command_dispatch"]["command_handler_count"], 12)
        self.assertEqual(report["local_endpoint"]["smack"]["bilateral_label_count"], 19)
        self.assertEqual(report["framing"]["marshal_length_semantics"]["overstatement"], 64)
        self.assertIn("CWE-787", report["findings"]["undersized_total"]["classification"])
        self.assertIn("CWE-125", report["findings"]["transaction_remaining"]["classification"])
        self.assertEqual(report["canonical_sha256"], "2246011e805b39b9f38d1a3af674d299fd0fe782dc8a67c8c5bee7d1f0826336")

    @unittest.skipUnless(RECOVERED_PRESENT, "recovered firmware is not present")
    def test_cli_is_deterministic_and_refuses_overwrite(self) -> None:
        command = [
            sys.executable, str(TOOL_PATH), str(FRAMEWORK), str(SERVICE),
            str(UNIT), str(RELABEL), str(SMACK_DIR),
        ]
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            subprocess.run(command + ["--output", str(first)], check=True)
            subprocess.run(command + ["--output", str(second)], check=True)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            parsed = json.loads(first.read_text(encoding="ascii"))
            self.assertEqual(parsed["canonical_sha256"], "2246011e805b39b9f38d1a3af674d299fd0fe782dc8a67c8c5bee7d1f0826336")
            duplicate = subprocess.run(
                command + ["--output", str(first)], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, check=False,
            )
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn(b"File exists", duplicate.stderr)


if __name__ == "__main__":
    unittest.main()
