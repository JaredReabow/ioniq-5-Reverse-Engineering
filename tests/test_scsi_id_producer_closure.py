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

TOOL = Path(__file__).parents[1] / "tools/uk_fw/scsi_id_producer_closure.py"
SPEC = importlib.util.spec_from_file_location("scsi_id_producer_closure", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(TOOL.parent))
try:
    assert SPEC.loader is not None
    SPEC.loader.exec_module(MODULE)
finally:
    sys.path.pop(0)
PROJECT = Path(__file__).parents[1]
ROOTFS = PROJECT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"
CONFIG = PROJECT / "work/eu-260128/kernel.config"
TRANSPORT = PROJECT / "evidence/artifacts/udev-candidates/cve-2026-40225-transport-audit.json"
HAVE_INPUTS = ROOTFS.is_dir() and CONFIG.is_file() and TRANSPORT.is_file()


class UnitTests(unittest.TestCase):
    def test_canonical_validator_rejects_change(self) -> None:
        report = {
            "schema": MODULE.TRANSPORT_SCHEMA,
            "transports": {},
        }
        canonical = json.dumps(report, separators=(",", ":"), sort_keys=True).encode()
        report["canonical_sha256"] = MODULE.digest(canonical)
        MODULE.validate_canonical(report, MODULE.TRANSPORT_SCHEMA, "x")
        report["transports"]["changed"] = True
        with self.assertRaisesRegex(MODULE.AuditError, "mismatch"):
            MODULE.validate_canonical(report, MODULE.TRANSPORT_SCHEMA, "x")

    def test_exclusive_output_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            MODULE.write_exclusive(path, b"one")
            with self.assertRaises(FileExistsError):
                MODULE.write_exclusive(path, b"two")
            self.assertEqual(path.read_bytes(), b"one")


@unittest.skipUnless(HAVE_INPUTS, "exact ignored firmware inputs unavailable")
class ExactIntegrationTests(unittest.TestCase):
    def test_exact_producer_closure(self) -> None:
        report = MODULE.build_report(ROOTFS, CONFIG, TRANSPORT)
        self.assertEqual(report["schema"], MODULE.SCHEMA)
        self.assertEqual(report["inputs"]["module_inventory"]["count"], 160)
        self.assertEqual(
            report["producer_matrix"]["ordinary_usb_mass_storage"]["state"],
            "suppressed-by-prior-usb-id",
        )
        self.assertEqual(
            report["producer_matrix"]["ordinary_ata_disk"]["state"],
            "suppressed-by-prior-sanitizing-ata-id",
        )
        self.assertFalse(report["ata_id_review"]["control_characters_preserved_in_id_serial"])
        self.assertFalse(report["verdict"]["ordinary_usb_reaches_scsi_id"])
        self.assertFalse(report["verdict"]["ordinary_ata_reaches_scsi_id"])
        self.assertFalse(report["verdict"]["stock_external_scsi_id_property_injection_demonstrated"])
        self.assertEqual(
            report["producer_matrix"]["malformed_identity_or_prior_import_failure"]["state"],
            "unproved",
        )
        subject = copy.deepcopy(report)
        supplied = subject.pop("canonical_sha256")
        canonical = json.dumps(subject, separators=(",", ":"), sort_keys=True).encode()
        self.assertEqual(MODULE.digest(canonical), supplied)

    def test_cli_stdout_is_encoding_independent(self) -> None:
        command = [
            sys.executable,
            str(TOOL),
            "--rootfs",
            str(ROOTFS),
            "--kernel-config",
            str(CONFIG),
            "--transport-report",
            str(TRANSPORT),
        ]
        normal = subprocess.run(command, check=False, capture_output=True)
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-16"
        utf16 = subprocess.run(command, check=False, capture_output=True, env=env)
        self.assertEqual(normal.returncode, 0, normal.stderr)
        self.assertEqual(utf16.returncode, 0, utf16.stderr)
        self.assertEqual(normal.stdout, utf16.stdout)


if __name__ == "__main__":
    unittest.main()
