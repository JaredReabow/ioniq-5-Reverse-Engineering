"""Focused ownership and transport tests for the FUSE-backed USB path."""

from __future__ import annotations

from dataclasses import replace
import json
import os
from pathlib import Path
import stat
import subprocess
import unittest
from unittest import mock

from test_radxa_usb import RadxaUSBFixture

from tools.uk_fw import radxa_usb


class FuseTransportTests(RadxaUSBFixture):
    """Exercise the FUSE branch without importing hardware into the fixture."""

    def fuse_inspection(self):
        """Remove the raw-NBD-only inspection issue for a FUSE plan."""
        inspection = self.inspection()
        issues = tuple(
            item for item in inspection.issues if "no NBD block devices" not in item
        )
        return replace(inspection, issues=issues)

    @staticmethod
    def mountinfo_record(
        mountpoint: Path,
        fsname: str,
        *,
        mount_id: int = 41,
        fstype: str = "fuse",
    ) -> str:
        """Return one valid Linux mountinfo record."""
        return (
            f"{mount_id} 1 0:52 / {mountpoint} rw,nosuid,nodev - "
            f"{fstype} {fsname} rw,user_id=0,group_id=0\n"
        )

    def make_fuse_state(self, mountpoint: Path, fsname: str) -> dict[str, object]:
        """Return the minimum live ownership record used by health."""
        return {
            "schema": radxa_usb.STATE_SCHEMA,
            "backing_kind": "fuse-direct",
            "backing_path": str(mountpoint),
            "state_root": str(self.state),
            "configfs_root": str(self.configfs),
            "gadget_name": radxa_usb.DEFAULT_GADGET_NAME,
            "fuse_mountpoint": str(mountpoint),
            "fuse_fsname": fsname,
            "fuse_helper_pid": 5353,
            "fuse_helper_command": [
                str(radxa_usb.DEFAULT_FUSE_HELPER),
                "-r",
                "-s",
                "-C",
                "1",
            ],
            "fuse_helper_identity": {
                "pid": 5353,
                "boot_id": "fixture-boot",
                "start_ticks": 17,
                "argv": [
                    str(radxa_usb.DEFAULT_FUSE_HELPER),
                    "-r",
                    "-s",
                    "-C",
                    "1",
                ],
                "executable": {"path": "/helper", "dev": 1, "ino": 2},
            },
            "gadget_phase": "attached",
            "udc_attached": True,
            "udc": "radxa-udc",
            "nbdkit_pid": 4242,
            "fuse_lun_ro": "1",
            "fuse_backing_size": 4096,
            "cleanup": {
                "udc_unbound": False,
                "nbd_detached": True,
                "gadget_removed": False,
                "fuse_unmounted": False,
                "fuse_helper_stopped": False,
                "nbdkit_stopped": False,
            },
        }

    def test_fuse_plan_has_no_nbd_requirement_and_exact_helper_argv(self) -> None:
        """FUSE plans require no NBD device and never enable helper debug mode."""
        self.add_udc("radxa-udc")
        helper = self.root / "ioniq-nbdfuse-direct"
        fusermount = self.root / "fusermount3"
        helper.write_bytes(b"fixture helper")
        fusermount.write_bytes(b"fixture fusermount")
        helper.chmod(0o755)
        fusermount.chmod(0o755)
        fake_stat = os.stat_result(
            (stat.S_IFREG | 0o755, 1, 1, 1, 0, 0, 16, 0, 0, 0)
        )

        def version_runner(command):
            self.assertEqual(list(command), [str(helper), "--version"])
            return subprocess.CompletedProcess(
                command,
                0,
                radxa_usb.FUSE_HELPER_VERSION + "\nlibnbd 1.14.2\n",
                "",
            )

        plan = radxa_usb.radxa_usb_build_plan(
            serve_plan=self.serve_plan,
            backing_kind="fuse-direct",
            inspection=self.fuse_inspection(),
            helper_path=helper,
            fusermount3_path=fusermount,
            helper_preflight=lambda _path: None,
            nbd_port=19009,
            port_scan_count=1,
            port_available=lambda _host, _port: True,
        )
        with mock.patch.object(Path, "lstat", return_value=fake_stat):
            radxa_usb._radxa_usb_preflight_fuse_helper(
                helper, runner=version_runner
            )

        self.assertTrue(plan.ready, plan.issues)
        self.assertEqual(plan.backing_kind, "fuse-direct")
        self.assertEqual(plan.backing_path, plan.fuse_mount_directory / "lun")
        self.assertEqual(plan.fuse_mount_directory, self.state / "fuse-mount")
        self.assertFalse(plan.nbd_client_attach_command)
        self.assertFalse(plan.nbd_client_detach_command)
        self.assertNotIn("-d", plan.fuse_helper_command)
        self.assertEqual(
            plan.fuse_helper_command[1:5], ("-r", "-s", "-C", "1")
        )
        self.assertIn(f"fsname={plan.fuse_fsname}", plan.fuse_helper_command)
        self.assertEqual(plan.fuse_unmount_command[1], "-u")
        self.assertNotIn("-z", plan.fuse_unmount_command)

    def test_exact_mount_provenance_rejects_foreign_source(self) -> None:
        """Only the planned mountpoint, source, and FUSE filesystem are owned."""
        mountpoint = self.state / "fuse-mount" / "lun"
        state = self.make_fuse_state(mountpoint, "ioniq-fuse-owned")
        state["proc_root"] = str(self.proc)
        mountinfo = self.proc / "self" / "mountinfo"
        mountinfo.parent.mkdir(parents=True)
        mountinfo.write_text(
            self.mountinfo_record(mountpoint, "ioniq-fuse-owned"),
            encoding="utf-8",
        )
        self.assertEqual(
            radxa_usb._radxa_usb_fuse_mount(state)["mount_id"], 41
        )

        mountinfo.write_text(
            self.mountinfo_record(mountpoint, "ioniq-fuse-foreign"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "source.*changed"):
            radxa_usb._radxa_usb_validate_fuse_mount(state, required=False)

    def test_helper_death_fails_health_before_any_file_io(self) -> None:
        """A missing helper PID fails closed without inspecting the FUSE file."""
        mountpoint = self.state / "fuse-mount" / "lun"
        state = self.make_fuse_state(mountpoint, "ioniq-fuse-owned")
        with mock.patch.object(
            radxa_usb, "_radxa_usb_process_status", return_value="owned"
        ), mock.patch.object(
            radxa_usb, "_radxa_usb_fuse_helper_status", return_value="absent"
        ), mock.patch.object(
            Path, "stat", side_effect=AssertionError("FUSE file stat is forbidden")
        ):
            with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "FUSE helper is absent"):
                radxa_usb._radxa_usb_health(
                    state,
                    owned_process=object(),
                    process_probe=lambda _pid, _identity: "absent",
                    is_block_device=lambda _path: False,
                )

    def test_cleanup_unmount_failure_checkpoints_and_stops_backends(self) -> None:
        """UDC and gadget removal precede unmount; failures stop later steps."""
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        gadget.mkdir()
        (gadget / "UDC").write_text("radxa-udc\n", encoding="ascii")
        mountpoint = self.state / "fuse-mount" / "lun"
        state = self.make_fuse_state(mountpoint, "ioniq-fuse-owned")
        self.state.mkdir(mode=0o700)
        state_path = self.state / "state.json"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        live_mount = {
            "mount_id": 41,
            "parent_id": 1,
            "device": "0:52",
            "mountpoint": str(mountpoint),
            "mount_options": "rw",
            "fstype": "fuse",
            "fsname": "ioniq-fuse-owned",
        }
        events: list[str] = []

        def remove_gadget(_root, _name, errors):
            events.append(
                "gadget-remove:" + (gadget / "UDC").read_text(encoding="ascii")
            )
            if errors:
                return
            (gadget / "UDC").unlink()
            gadget.rmdir()

        with mock.patch.object(
            radxa_usb,
            "_radxa_usb_validate_gadget_identity",
            return_value=gadget,
        ), mock.patch.object(
            radxa_usb, "_radxa_usb_fuse_helper_status", return_value="owned"
        ), mock.patch.object(
            radxa_usb, "_radxa_usb_process_status", return_value="owned"
        ), mock.patch.object(
            radxa_usb,
            "_radxa_usb_validate_fuse_mount",
            return_value=live_mount,
        ), mock.patch.object(
            radxa_usb, "_radxa_usb_remove_gadget", side_effect=remove_gadget
        ), mock.patch.object(
            radxa_usb,
            "_radxa_usb_unmount_fuse",
            side_effect=OSError("fixture unmount failed"),
        ), mock.patch.object(
            radxa_usb, "_radxa_usb_stop_fuse_helper"
        ) as stop_helper, mock.patch.object(
            radxa_usb, "_radxa_usb_stop_owned_nbdkit"
        ) as stop_nbdkit:
            errors = radxa_usb._radxa_usb_cleanup(
                state,
                state_path=state_path,
                runner=lambda command: subprocess.CompletedProcess(command, 0, "", ""),
                process_probe=lambda _pid, _identity: "owned",
            )

        self.assertTrue(
            any("FUSE unmount failed" in item for item in errors), errors
        )
        self.assertEqual(events, ["gadget-remove:\n"])
        self.assertFalse(gadget.exists())
        persisted = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertTrue(persisted["cleanup"]["udc_unbound"])
        self.assertTrue(persisted["cleanup"]["gadget_removed"])
        self.assertFalse(persisted["cleanup"]["fuse_unmounted"])
        stop_helper.assert_not_called()
        stop_nbdkit.assert_not_called()

    def test_cache_policy_is_stable_across_transport_version_and_rejects_change(self) -> None:
        """Transport 1.3 reuses policy 1.2.1 cache but changed inputs fail."""
        self.assertEqual(radxa_usb.TOOL_VERSION, "1.3.1")
        self.assertEqual(radxa_usb.radxa_usb_validation_cache_version(), "1.2.1")
        cache_path = self.root / "private-cache/validated.json"
        with radxa_usb.radxa_usb_validation_session(cache_path, prepare=True):
            radxa_usb._radxa_usb_load_bound_content(self.serve_plan)
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        self.assertEqual(cache["tool_version"], "1.2.1")

        with radxa_usb.radxa_usb_validation_session(cache_path):
            radxa_usb._radxa_usb_load_bound_content(self.serve_plan)
        self.baseline.write_bytes(b"CHANGED")
        with radxa_usb.radxa_usb_validation_session(cache_path):
            with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "prepared input changed"):
                radxa_usb._radxa_usb_load_bound_content(self.serve_plan)


if __name__ == "__main__":
    unittest.main()
