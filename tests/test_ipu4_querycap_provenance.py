from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).parents[1] / "tools/uk_fw/ipu4_querycap_provenance.py"
SPEC = importlib.util.spec_from_file_location("ipu4_querycap_provenance", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(TOOL.parent))
try:
    assert SPEC.loader is not None
    SPEC.loader.exec_module(MODULE)
finally:
    sys.path.pop(0)
PROJECT = Path(__file__).parents[1]
VMLINUX = PROJECT / "work/eu-260128/vmlinux"
KALLSYMS = PROJECT / "work/eu-260128/kallsyms.tsv"
TRANSPORT = PROJECT / "evidence/artifacts/udev-candidates/cve-2026-40225-transport-audit.json"
HAVE_INPUTS = VMLINUX.is_file() and KALLSYMS.is_file() and TRANSPORT.is_file()


class ParserTests(unittest.TestCase):
    def test_kallsyms_parser_selects_only_reviewed_symbols(self) -> None:
        lines = [
            f"{address:016x}\tT\t{name}"
            for name, address in MODULE.SYMBOLS.items()
        ]
        lines.append("ffffffff81000000\tt\tunrelated")
        parsed = MODULE.parse_kallsyms(("\n".join(lines) + "\n").encode())
        self.assertEqual(parsed, MODULE.SYMBOLS)

    def test_kallsyms_duplicate_reviewed_symbol_and_bad_line_fail(self) -> None:
        name, address = next(iter(MODULE.SYMBOLS.items()))
        line = f"{address:016x}\tT\t{name}\n"
        with self.assertRaisesRegex(MODULE.AuditError, "duplicate reviewed"):
            MODULE.parse_kallsyms((line + line).encode())
        with self.assertRaisesRegex(MODULE.AuditError, "malformed"):
            MODULE.parse_kallsyms(b"bad\n")

    def test_pattern_review_requires_every_pattern_exactly_once(self) -> None:
        data = b"abc123def456"
        self.assertEqual(
            MODULE.require_unique_patterns(data, {"one": b"123", "two": b"456"}, "x"),
            {"one": 3, "two": 9},
        )
        with self.assertRaisesRegex(MODULE.AuditError, "absent or non-unique"):
            MODULE.require_unique_patterns(b"abcabc", {"duplicate": b"abc"}, "x")
        with self.assertRaisesRegex(MODULE.AuditError, "absent or non-unique"):
            MODULE.require_unique_patterns(b"abc", {"missing": b"xyz"}, "x")

    def test_transport_report_digest_and_state_are_required(self) -> None:
        report = json.loads(TRANSPORT.read_text()) if TRANSPORT.is_file() else {
            "schema": MODULE.TRANSPORT_SCHEMA,
            "transports": {"generic_usb_v4l_to_v4l_id": {"state": "not-built"}},
        }
        if "canonical_sha256" not in report:
            canonical = json.dumps(report, separators=(",", ":"), sort_keys=True).encode()
            report["canonical_sha256"] = MODULE.digest(canonical)
        MODULE.validate_transport(report)
        changed = copy.deepcopy(report)
        changed["transports"]["generic_usb_v4l_to_v4l_id"]["state"] = "present"
        with self.assertRaisesRegex(MODULE.AuditError, "canonical_sha256 mismatch"):
            MODULE.validate_transport(changed)
        changed = copy.deepcopy(report)
        changed["transports"]["generic_usb_v4l_to_v4l_id"]["state"] = "present"
        supplied = changed.pop("canonical_sha256")
        self.assertIsInstance(supplied, str)
        canonical = json.dumps(changed, separators=(",", ":"), sort_keys=True).encode()
        changed["canonical_sha256"] = MODULE.digest(canonical)
        with self.assertRaisesRegex(MODULE.AuditError, "not accepted"):
            MODULE.validate_transport(changed)

    def test_exclusive_output_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            MODULE.write_exclusive(path, b"first")
            with self.assertRaises(FileExistsError):
                MODULE.write_exclusive(path, b"second")
            self.assertEqual(path.read_bytes(), b"first")


@unittest.skipUnless(HAVE_INPUTS, "exact ignored kernel inputs unavailable")
class ExactIntegrationTests(unittest.TestCase):
    def test_exact_bytes_bind_card_to_fixed_pci_identity_strings(self) -> None:
        report = MODULE.build_report(VMLINUX, KALLSYMS, TRANSPORT)
        self.assertEqual(report["schema"], MODULE.SCHEMA)
        self.assertEqual(report["ranges"]["querycap"]["size"], 0xA8)
        self.assertEqual(report["ranges"]["card_bus_producer_prefix"]["size"], 0xC9)
        self.assertEqual(
            report["dataflow"]["card"]["producer_sources"],
            ["ipu4/Broxton B", "ipu5/A"],
        )
        self.assertEqual(
            report["dataflow"]["card"]["producer_destination"], "isys +0x320"
        )
        self.assertTrue(report["verdict"]["ipu4_card_selected_from_fixed_driver_strings"])
        self.assertTrue(report["verdict"]["ipu4_card_selected_by_pci_identity"])
        self.assertFalse(report["verdict"]["camera_pixels_control_querycap_card"])
        self.assertFalse(report["verdict"]["usb_descriptor_controls_ipu4_querycap_card"])
        self.assertFalse(report["verdict"]["stock_external_v4l_product_injection_demonstrated"])
        subject = copy.deepcopy(report)
        supplied = subject.pop("canonical_sha256")
        canonical = json.dumps(subject, separators=(",", ":"), sort_keys=True).encode()
        self.assertEqual(MODULE.digest(canonical), supplied)

    def test_cli_stdout_is_encoding_independent(self) -> None:
        command = [
            sys.executable,
            str(TOOL),
            "--vmlinux",
            str(VMLINUX),
            "--kallsyms",
            str(KALLSYMS),
            "--transport-report",
            str(TRANSPORT),
        ]
        normal = subprocess.run(command, check=False, capture_output=True)
        environment = dict(os.environ)
        environment["PYTHONIOENCODING"] = "utf-16"
        utf16 = subprocess.run(command, check=False, capture_output=True, env=environment)
        self.assertEqual(normal.returncode, 0, normal.stderr)
        self.assertEqual(utf16.returncode, 0, utf16.stderr)
        self.assertEqual(normal.stdout, utf16.stdout)


if __name__ == "__main__":
    unittest.main()
