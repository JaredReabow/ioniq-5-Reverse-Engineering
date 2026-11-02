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

TOOL = Path(__file__).parents[1] / "tools/uk_fw/cve_2026_40225_transport_audit.py"
SPEC = importlib.util.spec_from_file_location("cve_2026_40225_transport_audit", TOOL)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUDIT)
PROJECT = Path(__file__).parents[1]
CONFIG = PROJECT / "work/eu-260128/kernel.config"
ROOTFS = PROJECT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"
CONTROL = PROJECT / "work/usb-scsi-rule-precedence-20260325/usb-scsi-rule-precedence.json"
HAVE_EXACT_INPUTS = CONFIG.is_file() and ROOTFS.is_dir() and CONTROL.is_file()


def control_fixture() -> dict[str, object]:
    return {
        "schema": AUDIT.CONTROL_SCHEMA,
        "classification": "usb-id-suppresses-scsi-id",
        "network": "disabled by vm_boot (-nic none)",
        "salient_lines": list(AUDIT.EXPECTED_CONTROL_MARKERS),
        "guest_artifacts": {
            "/bin/udevadm": AUDIT.EXPECTED_FILES["bin/udevadm"],
            "/lib/udev/scsi_id": AUDIT.EXPECTED_FILES["lib/udev/scsi_id"],
            "/lib/udev/rules.d/60-persistent-storage.rules": AUDIT.EXPECTED_FILES[
                "lib/udev/rules.d/60-persistent-storage.rules"
            ],
        },
        "attached_disk": {
            "sha256": "bb9f8df61474d25e71fa00722318cd387396ca1736605e1248821cc0de3d3af8",
            "qemu_access": "snapshot=on,readonly=on",
            "usb_serial": "explicitly empty",
        },
    }


class ParserTests(unittest.TestCase):
    def test_parse_config_handles_values_and_not_set(self) -> None:
        config = AUDIT.parse_config(
            b"CONFIG_SCSI=m\n# CONFIG_MEDIA_USB_SUPPORT is not set\nCONFIG_VIDEO_DEV=y\n"
        )
        self.assertEqual(
            config,
            {"SCSI": "m", "MEDIA_USB_SUPPORT": "n", "VIDEO_DEV": "y"},
        )

    def test_require_config_and_exact_line_fail_closed(self) -> None:
        with self.assertRaisesRegex(AUDIT.AuditError, "expected"):
            AUDIT.require_config({"SCSI": "y"}, "SCSI", "m")
        self.assertEqual(AUDIT.exact_line_number(b"a\nb\n", "b", "fixture"), 2)
        with self.assertRaisesRegex(AUDIT.AuditError, "found 2"):
            AUDIT.exact_line_number(b"a\na\n", "a", "fixture")

    def test_control_validation_rejects_every_material_change(self) -> None:
        AUDIT.validate_control(control_fixture())
        mutations = []
        for key, value in (
            ("schema", "wrong"),
            ("classification", "unexpected-rule-result"),
            ("network", "enabled"),
        ):
            item = control_fixture()
            item[key] = value
            mutations.append(item)
        item = control_fixture()
        item["salient_lines"] = item["salient_lines"][:-1]
        mutations.append(item)
        item = control_fixture()
        item["guest_artifacts"]["/lib/udev/scsi_id"] = "0" * 64
        mutations.append(item)
        item = control_fixture()
        item["attached_disk"]["usb_serial"] = "present"
        mutations.append(item)
        for item in mutations:
            with self.subTest(item=item):
                with self.assertRaises(AUDIT.AuditError):
                    AUDIT.validate_control(item)

    def test_strict_json_rejects_duplicate_nonfinite_and_nonobject(self) -> None:
        with self.assertRaisesRegex(AUDIT.AuditError, "duplicate"):
            AUDIT.strict_json(b'{"x":1,"x":2}', Path("fixture"))
        with self.assertRaisesRegex(AUDIT.AuditError, "non-finite"):
            AUDIT.strict_json(b'{"x":NaN}', Path("fixture"))
        with self.assertRaisesRegex(AUDIT.AuditError, "top-level"):
            AUDIT.strict_json(b"[]", Path("fixture"))


class StableInputTests(unittest.TestCase):
    def test_stable_read_accepts_regular_and_rejects_symlink_directory_oversize(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            regular = root / "regular"
            regular.write_bytes(b"abc")
            self.assertEqual(AUDIT.stable_read(regular), b"abc")
            link = root / "link"
            link.symlink_to(regular)
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.stable_read(link)
            with self.assertRaisesRegex(AUDIT.AuditError, "not a regular"):
                AUDIT.stable_read(root)
            with self.assertRaisesRegex(AUDIT.AuditError, "exceeds"):
                AUDIT.stable_read(regular, limit=2)

    def test_exclusive_output_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            AUDIT.write_exclusive(path, b"first")
            with self.assertRaises(FileExistsError):
                AUDIT.write_exclusive(path, b"second")
            self.assertEqual(path.read_bytes(), b"first")


@unittest.skipUnless(HAVE_EXACT_INPUTS, "exact ignored recovered inputs unavailable")
class ExactIntegrationTests(unittest.TestCase):
    def test_exact_inputs_produce_bounded_transport_matrix(self) -> None:
        report = AUDIT.build_report(CONFIG, ROOTFS, CONTROL)
        self.assertEqual(report["schema"], AUDIT.SCHEMA)
        self.assertEqual(
            report["transports"]["ordinary_usb_mass_storage_to_scsi_id"]["state"],
            "suppressed-by-prior-usb-id",
        )
        self.assertEqual(report["transports"]["iscsi_to_scsi_id"]["state"], "not-built")
        self.assertEqual(
            report["transports"]["generic_usb_v4l_to_v4l_id"]["state"],
            "not-built",
        )
        self.assertEqual(
            report["transports"]["platform_ipu4_camera_to_v4l_id"]["state"],
            "built-in-external-control-unproved",
        )
        self.assertEqual(report["inputs"]["module_inventory"]["count"], 160)
        self.assertFalse(report["verdict"]["stock_external_entry_vector_demonstrated"])
        self.assertFalse(report["verdict"]["root_access_demonstrated"])
        subject = copy.deepcopy(report)
        digest = subject.pop("canonical_sha256")
        canonical = json.dumps(subject, separators=(",", ":"), sort_keys=True).encode()
        self.assertEqual(AUDIT.sha256(canonical), digest)

    def test_cli_stdout_is_encoding_independent(self) -> None:
        command = [
            sys.executable,
            str(TOOL),
            "--kernel-config",
            str(CONFIG),
            "--rootfs",
            str(ROOTFS),
            "--usb-control",
            str(CONTROL),
        ]
        normal = subprocess.run(command, check=False, capture_output=True)
        environment = dict(os.environ)
        environment["PYTHONIOENCODING"] = "utf-16"
        utf16 = subprocess.run(
            command, check=False, capture_output=True, env=environment
        )
        self.assertEqual(normal.returncode, 0, normal.stderr)
        self.assertEqual(utf16.returncode, 0, utf16.stderr)
        self.assertEqual(normal.stdout, utf16.stdout)
        self.assertEqual(json.loads(normal.stdout)["schema"], AUDIT.SCHEMA)


if __name__ == "__main__":
    unittest.main()
