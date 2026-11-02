"""Safety and classification tests for the USB/SCSI rule-precedence control."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

TOOL = Path(__file__).parents[1] / "tools/uk_fw/usb_scsi_rule_precedence_probe.py"
SPEC = importlib.util.spec_from_file_location("usb_scsi_rule_precedence_probe", TOOL)
PROBE = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(TOOL.parent))
try:
    assert SPEC.loader is not None
    SPEC.loader.exec_module(PROBE)
finally:
    sys.path.pop(0)


class ProjectFixture(unittest.TestCase):
    def setUp(self):
        work = PROBE.vm_boot.PROJECT / "work"
        work.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=work)
        self.base = Path(self.temp.name)
        self.workspace = self.base / "vm"
        self.workspace.mkdir()

    def tearDown(self):
        self.temp.cleanup()


class OutputAndDiskTests(ProjectFixture):
    def test_accepts_new_project_local_output(self):
        output = self.base / "result"
        self.assertEqual(PROBE.validate_output(output, self.workspace), output.resolve())

    def test_rejects_existing_aliasing_and_external_output(self):
        existing = self.base / "existing"
        existing.mkdir()
        with self.assertRaisesRegex(ValueError, "already exists"):
            PROBE.validate_output(existing, self.workspace)
        with self.assertRaisesRegex(ValueError, "workspace"):
            PROBE.validate_output(self.workspace / "result", self.workspace)
        with tempfile.TemporaryDirectory() as outside:
            with self.assertRaisesRegex(ValueError, "subdirectory of the project"):
                PROBE.validate_output(Path(outside) / "result", self.workspace)

    def test_zero_disk_has_fixed_size_and_digest_and_refuses_overwrite(self):
        path = self.base / "disk.img"
        self.assertEqual(PROBE.write_zero_disk(path), PROBE.DISK_SHA256)
        self.assertEqual(path.stat().st_size, PROBE.DISK_SIZE)
        self.assertEqual(path.read_bytes(), bytes(PROBE.DISK_SIZE))
        with self.assertRaises(FileExistsError):
            PROBE.write_zero_disk(path)


class GuestContractTests(unittest.TestCase):
    def test_script_binds_exact_artifacts_and_read_only_geometry(self):
        script = PROBE.guest_script()
        for path, digest in PROBE.EXPECTED_GUEST_HASHES.items():
            self.assertIn(path, script)
            self.assertIn(digest, script)
        self.assertIn("udevadm test --action=add /sys/class/block/sda", script)
        self.assertIn("USB_SCSI_RULE_USB_SERIAL_ATTR=absent", script)
        self.assertIn("USB_SCSI_RULE_BLOCK_READONLY=1", script)
        self.assertIn("mount -o remount,ro /", script)
        self.assertIn("IMPORT builtin 'usb_id'", script)
        self.assertIn("ID_SCSI_SERIAL", script)
        self.assertIn("SCSI_ID_EXECUTION", script)

    def test_script_has_no_property_injection_activation_or_write(self):
        script = PROBE.guest_script()
        for forbidden in (
            "SYSTEMD_WANTS",
            "REMOVE_CMD",
            "debug-shell",
            "systemctl",
            "udevadm trigger",
            "/uevent",
            "mkfs",
            "mount /dev/sda",
            "dd if=",
            "RUN+=",
        ):
            self.assertNotIn(forbidden, script)
        self.assertNotIn("scsi_id --export", script)
        self.assertNotIn("/lib/udev/scsi_id -", script)


class ClassificationTests(unittest.TestCase):
    def result(self):
        return {
            "userspace": True,
            "root_mounted": True,
            "timeout": False,
            "error": None,
            "command_exit_code": 0,
        }

    def serial(self, markers=None):
        values = list(PROBE.EXPECTED_SEQUENCE if markers is None else markers)
        return "boot\n" + "\n".join(values) + "\nshutdown\n"

    def test_accepts_one_exact_ordered_frame(self):
        serial = self.serial()
        self.assertEqual(PROBE.classify(serial, self.result()), "usb-id-suppresses-scsi-id")
        self.assertEqual(PROBE.salient_lines(serial), list(PROBE.EXPECTED_SEQUENCE))

    def test_missing_or_changed_negative_observation_fails(self):
        markers = list(PROBE.EXPECTED_SEQUENCE)
        index = markers.index("USB_SCSI_RULE_SCSI_ID_EXECUTION=absent")
        markers[index] = "USB_SCSI_RULE_SCSI_ID_EXECUTION=present"
        self.assertEqual(PROBE.classify(self.serial(markers), self.result()), "unexpected-rule-result")
        markers = list(PROBE.EXPECTED_SEQUENCE)
        markers.remove("USB_SCSI_RULE_ID_SCSI_SERIAL=absent")
        self.assertEqual(PROBE.classify(self.serial(markers), self.result()), "unexpected-rule-result")

    def test_duplicate_frame_failure_marker_timeout_and_harness_error_fail(self):
        duplicated = self.serial() + self.serial()
        self.assertEqual(PROBE.classify(duplicated, self.result()), "harness-error")
        failed = [PROBE.BEGIN_MARKER, "USB_SCSI_RULE_FAIL=artifact_hash", PROBE.COMPLETE_MARKER]
        self.assertEqual(PROBE.classify(self.serial(failed), self.result()), "harness-error")
        result = self.result()
        result["timeout"] = True
        self.assertEqual(PROBE.classify(self.serial(), result), "timeout")
        result = self.result()
        result["userspace"] = False
        self.assertEqual(PROBE.classify(self.serial(), result), "harness-error")


class RunProbeTests(ProjectFixture):
    def test_run_uses_empty_serial_read_only_disk_and_emits_bounded_report(self):
        output = self.base / "output"
        captured: dict[str, object] = {}

        def fake_run(workspace, compat, command, **kwargs):
            captured.update(
                workspace=workspace,
                compat=compat,
                command=command,
                kwargs=kwargs,
            )
            run = workspace / "runs" / "1"
            run.mkdir(parents=True)
            (run / "result.json").write_text(json.dumps({
                "userspace": True,
                "root_mounted": True,
                "timeout": False,
                "error": None,
                "command_exit_code": 0,
            }))
            (run / "serial.log").write_text(
                "\n".join(PROBE.EXPECTED_SEQUENCE) + "\n"
            )
            return 0

        with mock.patch.object(
            PROBE, "verify_exact_workspace", return_value=dict(PROBE.EXPECTED_WORKSPACE_SHA256)
        ), mock.patch.object(PROBE.vm_boot, "run", side_effect=fake_run):
            report, rc = PROBE.run_probe(self.workspace, output, 120, 1024)

        self.assertEqual(rc, 0)
        self.assertEqual(report["classification"], "usb-id-suppresses-scsi-id")
        self.assertEqual(report["attached_disk"]["sha256"], PROBE.DISK_SHA256)
        self.assertEqual(report["attached_disk"]["usb_serial"], "explicitly empty")
        devices = captured["kwargs"]["extra_devices"]
        self.assertIn("usb-storage,bus=ehci.0,drive=usbtest,serial=", devices)
        drive = next(item for item in devices if item.startswith("if=none"))
        self.assertIn("snapshot=on", drive)
        self.assertIn("readonly=on", drive)
        self.assertEqual(captured["kwargs"]["serial_completion_marker"], PROBE.COMPLETE_MARKER)
        self.assertTrue((output / "usb-scsi-rule-precedence.json").is_file())
        self.assertTrue((output / "benign-zero-usb-disk.img").is_file())
        self.assertIn("No control characters", report["limitations"][2])


if __name__ == "__main__":
    unittest.main()
