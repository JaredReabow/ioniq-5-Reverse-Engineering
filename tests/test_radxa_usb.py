"""Fixture-only tests for the Radxa USB gadget adapter."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

PROJECT = Path(__file__).parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools.uk_fw import radxa_usb


class FakeProcess:
    """Record process lifecycle calls without starting anything."""

    def __init__(self, argv, **_kwargs) -> None:
        self.argv = list(argv)
        self.pid = 4242
        self.terminated = False
        self.waited = False
        self.returncode = None

    def terminate(self) -> None:
        """Record that the owned process was terminated."""
        self.terminated = True
        self.returncode = 0

    def wait(self, timeout=None) -> int:
        """Record that the owned process was reaped."""
        self.waited = timeout is not None
        return 0

    def poll(self):
        """Report whether the fake process has exited."""
        return self.returncode


class RadxaUSBFixture(unittest.TestCase):
    """Build only temporary sysfs, configfs, proc, dev, and input trees."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name).resolve()
        self.sysfs = self.root / "sys"
        self.dev = self.root / "dev"
        self.configfs = self.root / "sys" / "kernel" / "config" / "usb_gadget"
        self.proc = self.root / "proc"
        self.state = self.root / "run" / "ioniq-toctou"
        self.state.parent.mkdir(parents=True)
        self.udc_root = self.sysfs / "class" / "udc"
        self.block_root = self.sysfs / "block"
        self.configfs.mkdir(parents=True)
        self.dev.mkdir()
        (self.proc / "device-tree").mkdir(parents=True)
        (self.proc / "device-tree" / "model").write_text(
            "Radxa Zero 3W\n", encoding="utf-8"
        )
        self.baseline = self.root / "usb.img"
        self.baseline.write_bytes(b"BASELINE")
        self.evil = self.root / "rootfs.te2"
        self.evil.write_bytes(b"REPLACED")
        self.regions = self.root / "regions.json"
        self.regions.write_text(
            json.dumps(
                [
                    {
                        "off": 0,
                        "len": 8,
                        "evil": str(self.evil),
                        "switch_after_pass": 2,
                        "mode": "benign_then_evil",
                    }
                ]
            ),
            encoding="utf-8",
        )
        self.plugin = self.root / "nbdkit_toctou.py"
        self.plugin.write_text("# fixture plugin\n", encoding="utf-8")
        self.builder_manifest = self.root / "custom.manifest.json"
        self.serve_plan = self.root / "serve-plan.json"
        self.write_serve_plan()
        self.commands: list[list[str]] = []
        self.processes: list[FakeProcess] = []

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _check_cache_survives_new_session_without_reading_large_inputs(self) -> None:
        """A power-cycle equivalent reuses exact identities without image reads."""
        cache = self.root / "private-cache/validated.json"
        with radxa_usb.radxa_usb_validation_session(cache, prepare=True):
            prepared = radxa_usb._radxa_usb_load_bound_content(self.serve_plan)
        self.assertEqual(cache.stat().st_mode & 0o777, 0o600)
        original_open = Path.open

        class NoImageRead:
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.handle.close()

            def fileno(self):
                return self.handle.fileno()

            def read(self, *_args):
                raise AssertionError("prepared image was reread on startup")

        def guarded_open(path, *args, **kwargs):
            handle = original_open(path, *args, **kwargs)
            return NoImageRead(handle) if path in (self.baseline, self.evil) else handle

        with mock.patch.object(Path, "open", guarded_open):
            with radxa_usb.radxa_usb_validation_session(cache):
                current = radxa_usb._radxa_usb_load_bound_content(self.serve_plan)
                radxa_usb._radxa_usb_verify_bound_content(current)
        self.assertEqual(prepared.to_dict(), current.to_dict())

    def _check_cache_rejects_mutation_even_with_restored_mtime(self) -> None:
        cache = self.root / "private-cache/validated.json"
        with radxa_usb.radxa_usb_validation_session(cache, prepare=True):
            radxa_usb._radxa_usb_load_bound_content(self.serve_plan)
        old = self.baseline.stat()
        self.baseline.write_bytes(b"MUTATION")
        os.utime(self.baseline, ns=(old.st_atime_ns, old.st_mtime_ns))
        with radxa_usb.radxa_usb_validation_session(cache):
            with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "prepared input changed"):
                radxa_usb._radxa_usb_load_bound_content(self.serve_plan)

    def _check_cache_rejects_replacement_inode(self) -> None:
        cache = self.root / "private-cache/validated.json"
        with radxa_usb.radxa_usb_validation_session(cache, prepare=True):
            radxa_usb._radxa_usb_load_bound_content(self.serve_plan)
        replacement = self.root / "identical.img"
        replacement.write_bytes(self.baseline.read_bytes())
        replacement.replace(self.baseline)
        with radxa_usb.radxa_usb_validation_session(cache):
            with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "prepared input changed"):
                radxa_usb._radxa_usb_load_bound_content(self.serve_plan)

    def _check_cache_private_modes_and_failed_prepare(self) -> None:
        cache = self.root / "private-cache/validated.json"
        with self.assertRaisesRegex(RuntimeError, "injected"):
            with radxa_usb.radxa_usb_validation_session(cache, prepare=True):
                radxa_usb._radxa_usb_load_bound_content(self.serve_plan)
                raise RuntimeError("injected")
        self.assertFalse(cache.exists())
        with radxa_usb.radxa_usb_validation_session(cache, prepare=True):
            radxa_usb._radxa_usb_load_bound_content(self.serve_plan)
        cache.chmod(0o644)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "private regular"):
            with radxa_usb.radxa_usb_validation_session(cache):
                pass

    def _check_prepare_cli_builds_cache_without_hardware_inspection(self) -> None:
        cache = self.root / "private-cache/validated.json"
        result = radxa_usb.radxa_usb_main([
            "prepare", "--serve-plan", str(self.serve_plan),
            "--validation-cache", str(cache)])
        self.assertEqual(result, 0)
        self.assertTrue(cache.is_file())

    def add_udc(self, name: str, driver: str = "dwc3") -> None:
        """Add a fixture UDC and driver link."""
        udc = self.udc_root / name
        driver_link = udc / "device" / "driver"
        driver_link.mkdir(parents=True)
        target = self.root / "drivers" / driver
        target.mkdir(parents=True, exist_ok=True)
        driver_link.rmdir()
        driver_link.symlink_to(target, target_is_directory=True)

    def add_nbd(
        self,
        number: int,
        *,
        pid: str | None = None,
        holder: str | None = None,
        linux_layout: bool = False,
    ) -> None:
        """Add a fixture NBD sysfs entry and device path."""
        if linux_layout:
            entry = self.sysfs / "devices" / "virtual" / "block" / f"nbd{number}"
        else:
            entry = self.block_root / f"nbd{number}"
        (entry / "holders").mkdir(parents=True)
        if pid is not None:
            (entry / "pid").write_text(pid + "\n", encoding="utf-8")
        if holder is not None:
            (entry / "holders" / holder).mkdir()
        if linux_layout:
            self.block_root.mkdir(parents=True, exist_ok=True)
            (self.block_root / f"nbd{number}").symlink_to(
                Path("..") / "devices" / "virtual" / "block" / f"nbd{number}"
            )
        (self.dev / f"nbd{number}").write_bytes(b"")

    def inspection(self):
        """Inspect the fixture roots without touching real hardware."""
        return radxa_usb.radxa_usb_inspect(
            sysfs_root=self.sysfs,
            dev_root=self.dev,
            configfs_root=self.configfs,
            proc_root=self.proc,
            state_root=self.state,
            which=lambda name: f"/fixture/bin/{name}",
            effective_uid=0,
            uname=lambda: mock.Mock(release="6.1-radxa-fixture"),
            is_block_device=lambda path: path.exists(),
        )

    @staticmethod
    def sha256(path: Path) -> str:
        """Return the fixture's declared file digest."""
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def file_record(self, path: Path) -> dict[str, object]:
        """Return one normalized file identity accepted by the serve plan."""
        return {
            "path": str(path.resolve()),
            "size": path.stat().st_size,
            "sha256": self.sha256(path),
        }

    def write_builder_manifest(self) -> None:
        """Write the existing builder report used as the trust anchor."""
        baseline = self.baseline.read_bytes()
        value = {
            "schema": radxa_usb.BUILDER_MANIFEST_SCHEMA,
            "tool": {
                "name": radxa_usb.BUILDER_TOOL_NAME,
                "version": radxa_usb.BUILDER_TOOL_VERSION,
            },
            "payload_version": "fixture",
            "device_basename": "mango-rootfs.tar.gz",
            "genuine": {
                "path": str(self.baseline.resolve()),
                "size": len(baseline),
                "sha256": self.sha256(self.baseline),
                "body_size": len(baseline),
            },
            "custom": {
                "path": str(self.evil.resolve()),
                "size": self.evil.stat().st_size,
                "sha256": self.sha256(self.evil),
                "compressed_size": self.evil.stat().st_size,
                "zero_padding": 0,
                "te2_integrity_valid": True,
            },
            "overlay": {},
            "limitations": [],
        }
        self.builder_manifest.write_text(
            json.dumps(value), encoding="utf-8"
        )

    def write_serve_plan(self) -> None:
        """Write a serve plan that references the builder manifest."""
        self.write_builder_manifest()
        regions_value = json.loads(
            self.regions.read_text(encoding="utf-8")
        )
        first_region = (
            regions_value[0]
            if isinstance(regions_value, list) and regions_value
            else {
                "off": 0,
                "len": self.baseline.stat().st_size,
                "mode": "benign_then_evil",
                "switch_after_pass": 2,
            }
        )
        value = {
            "schema": radxa_usb.SERVE_PLAN_SCHEMA,
            "baseline": self.file_record(self.baseline),
            "regions": self.file_record(self.regions),
            "plugin": self.file_record(self.plugin),
            "replacements": [
                {
                    **self.file_record(self.evil),
                    "offset": first_region["off"],
                    "length": first_region["len"],
                    "mode": first_region["mode"],
                    "switch_after_pass": first_region["switch_after_pass"],
                    "builder_manifest": self.file_record(
                        self.builder_manifest
                    ),
                }
            ],
        }
        self.serve_plan.write_text(json.dumps(value), encoding="utf-8")

    def build_plan(self, **overrides):
        """Build a validated fixture plan."""
        if "serve_plan" not in overrides:
            self.write_serve_plan()
        values = {
            "serve_plan": self.serve_plan,
            "nbd_port": 19009,
            "port_scan_count": 1,
            "inspection": self.inspection(),
            "port_available": lambda _host, _port: True,
        }
        values.update(overrides)
        return radxa_usb.radxa_usb_build_plan(**values)

    def runner(self, command):
        """Record an NBD command and emulate the sysfs connection transition."""
        self.commands.append(list(command))
        if "-N" in command:
            (self.block_root / "nbd2" / "pid").write_text("777\n", encoding="utf-8")
        elif "-d" in command:
            try:
                (self.block_root / "nbd2" / "pid").unlink()
            except FileNotFoundError:
                pass
        return subprocess.CompletedProcess(command, 0, "", "")

    def starter(self, command, **kwargs):
        """Record a foreground nbdkit start without spawning a process."""
        process = FakeProcess(command, **kwargs)
        self.processes.append(process)
        self.write_process_identity(command)
        return process

    def write_process_identity(self, command, *, start_ticks=1234, boot_id="fixture-boot"):
        """Write a Linux proc fixture including start time and executable identity."""
        proc_dir = self.proc / "4242"
        proc_dir.mkdir(exist_ok=True)
        boot_path = self.proc / "sys/kernel/random/boot_id"
        boot_path.parent.mkdir(parents=True, exist_ok=True)
        boot_path.write_text(boot_id)
        fields = ["S"] + ["0"] * 18 + [str(start_ticks)] + ["0"] * 8
        (proc_dir / "stat").write_text("4242 (nbdkit (fixture)) " + " ".join(fields))
        (proc_dir / "cmdline").write_bytes(b"\x00".join(os.fsencode(arg) for arg in command) + b"\x00")
        executable = self.root / "fixture-nbdkit"
        if not executable.exists():
            executable.write_bytes(b"fixture executable")
        if not (proc_dir / "exe").is_symlink():
            (proc_dir / "exe").symlink_to(executable)

    def process_probe(self, pid, identity):
        """Run production identity matching on fixture proc data."""
        return radxa_usb._radxa_usb_default_process_probe(pid, identity, proc_root=self.proc)

    def arm(self, plan, **overrides):
        """Execute the fixture arm with hardware predicates injected."""
        values = {
            "execute": True,
            "runner": self.runner,
            "process_starter": self.starter,
            "process_identity_capture": lambda pid: radxa_usb._radxa_usb_capture_process_identity(
                pid, proc_root=self.proc
            ),
            "process_probe": self.process_probe,
            "port_probe": lambda _host, _port: None,
            "is_block_device": lambda path: path.exists(),
        }
        values.update(overrides)
        return radxa_usb.radxa_usb_arm(plan, **values)

    def teardown(self, **overrides):
        """Execute fixture teardown with a known-absent fake nbdkit PID."""
        values = {
            "state_root": self.state,
            "execute": True,
            "runner": self.runner,
            "is_block_device": lambda path: path.exists(),
            "process_probe": lambda _pid, _identity: "absent",
        }
        values.update(overrides)
        return radxa_usb.radxa_usb_teardown(**values)


class InspectionTests(RadxaUSBFixture):
    def test_fuse_inspection_uses_the_recorded_backend_mount_namespace(self):
        """A sandboxed dashboard must compare mount IDs in the owner's namespace."""
        (self.proc / 'self').mkdir(exist_ok=True)
        (self.proc / '4242').mkdir(exist_ok=True)
        target = self.root / 'lun'
        state = {'proc_root': str(self.proc), 'nbdkit_pid': 4242,
                 'fuse_mountpoint': str(target), 'fuse_fsname': 'ioniq-test'}
        line = ' 1 0:50 / ' + str(target) + ' rw - fuse ioniq-test rw,user_id=0\n'
        (self.proc / 'self/mountinfo').write_text('100' + line)
        owner = self.proc / '4242/mountinfo'
        owner.write_text('200' + line)
        self.assertEqual(radxa_usb._radxa_usb_fuse_mount(state)['mount_id'], 200)
        owner.unlink()
        self.assertEqual(radxa_usb._radxa_usb_fuse_mount(state)['mount_id'], 100)

    """Exercise read-only platform discovery."""

    def test_inspect_discovers_radxa_udc_nbd_devices_and_dependencies(self) -> None:
        """Observed resources are reported without Pi-specific controller names."""
        self.add_udc("rk3x0-udc", driver="controller-driver")
        self.add_nbd(3)
        inspection = self.inspection()
        self.assertEqual(inspection.udcs, ("rk3x0-udc",))
        self.assertEqual(inspection.udc_drivers["rk3x0-udc"], "controller-driver")
        self.assertEqual([item.name for item in inspection.nbd_devices], ["nbd3"])
        self.assertTrue(inspection.nbd_devices[0].free)
        self.assertEqual(inspection.dependencies["nbdkit"], "/fixture/bin/nbdkit")
        self.assertEqual(inspection.board_model, "Radxa Zero 3W")
        self.assertEqual(inspection.issues, ())

    def test_occupied_nbd_is_not_selected(self) -> None:
        """A pid or holder marks an NBD device unavailable."""
        self.add_udc("rk-udc")
        self.add_nbd(0, pid="123")
        self.add_nbd(1, holder="100:0")
        self.add_nbd(2)
        plan = self.build_plan()
        self.assertTrue(plan.ready, plan.issues)
        self.assertEqual(plan.nbd_device.name, "nbd2")
        self.assertEqual(plan.nbd_device.device_path, (self.dev / "nbd2").resolve())

    def test_missing_dependencies_and_resources_are_explicit(self) -> None:
        """Missing executable and gadget resources produce actionable issues."""
        inspection = radxa_usb.radxa_usb_inspect(
            sysfs_root=self.sysfs,
            dev_root=self.dev,
            configfs_root=self.configfs,
            proc_root=self.proc,
            state_root=self.state,
            which=lambda _name: None,
            effective_uid=0,
            uname=lambda: mock.Mock(release="fixture"),
            is_block_device=lambda _path: False,
        )
        joined = "\n".join(inspection.issues)
        self.assertIn("no UDC", joined)
        self.assertIn("no NBD", joined)
        self.assertIn("missing dependency: nbdkit", joined)
        self.assertIn("missing dependency: nbd-client", joined)


class PlanningTests(RadxaUSBFixture):
    """Exercise ambiguity, occupied-resource, and input validation failures."""

    def test_multiple_udcs_require_explicit_selection(self) -> None:
        """The adapter never guesses which USB controller should be bound."""
        self.add_udc("udc-a")
        self.add_udc("udc-b")
        self.add_nbd(0)
        plan = self.build_plan()
        self.assertFalse(plan.ready)
        self.assertIn("multiple UDCs found", "; ".join(plan.issues))
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "multiple UDCs"):
            radxa_usb.radxa_usb_arm(plan)

    def test_explicit_udc_and_free_nbd_are_used(self) -> None:
        """Explicit selections work when the selected resources are free."""
        self.add_udc("udc-a")
        self.add_udc("udc-b")
        self.add_nbd(0, pid="77")
        self.add_nbd(1)
        plan = self.build_plan(udc="udc-b", nbd_device="nbd1")
        self.assertTrue(plan.ready, plan.issues)
        self.assertEqual(plan.udc, "udc-b")
        self.assertEqual(plan.nbd_device.name, "nbd1")
        self.assertNotIn("/dev/nbd0", plan.nbd_client_attach_command)

    def test_explicit_occupied_nbd_fails(self) -> None:
        """Explicit selection cannot bypass NBD ownership checks."""
        self.add_udc("udc-a")
        self.add_nbd(0, pid="77")
        plan = self.build_plan(nbd_device="nbd0")
        self.assertFalse(plan.ready)
        self.assertIn("selected NBD device is unavailable", "; ".join(plan.issues))

    def test_multiple_free_nbds_select_lowest_numeric_device(self) -> None:
        """Free NBD ambiguity is resolved by explicit numeric ordering."""
        self.add_udc("udc-a")
        self.add_nbd(10)
        self.add_nbd(2)
        plan = self.build_plan()
        self.assertTrue(plan.ready, plan.issues)
        self.assertEqual(plan.nbd_device.name, "nbd2")

    def test_already_bound_udc_is_rejected(self) -> None:
        """A controller bound by another gadget is never adopted."""
        self.add_udc("udc-a")
        self.add_nbd(0)
        other = self.configfs / "other-gadget"
        other.mkdir()
        (other / "UDC").write_text("udc-a\n", encoding="utf-8")
        plan = self.build_plan()
        self.assertFalse(plan.ready)
        self.assertIn("already bound to other-gadget", "; ".join(plan.issues))

    def test_invalid_regions_are_rejected(self) -> None:
        """Serve-plan region files must match the bound JSON list."""
        self.add_udc("udc-a")
        self.add_nbd(0)
        self.regions.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBError, "regions JSON must be a non-empty list"
        ):
            self.build_plan()

    def test_occupied_configfs_is_rejected(self) -> None:
        """A pre-existing gadget path is never adopted."""
        self.add_udc("udc-a")
        self.add_nbd(0)
        (self.configfs / radxa_usb.DEFAULT_GADGET_NAME).mkdir()
        plan = self.build_plan()
        joined = "; ".join(plan.issues)
        self.assertIn("configfs gadget already exists", joined)

    def test_no_raspberry_pi_deployment_assumptions(self) -> None:
        """The module does not copy Pi controller, boot, user, or NBD paths."""
        source = Path(radxa_usb.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "dwc2",
            "/boot/firmware/config.txt",
            "dtoverlay",
            "pi@",
            "/dev/nbd0",
        ):
            self.assertNotIn(forbidden, source)


class ManifestBindingTests(RadxaUSBFixture):
    """Exercise the serve plan and builder-manifest trust chain."""

    def write_json(self, path: Path, value: object) -> None:
        """Replace one fixture JSON document."""
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_valid_plan_binds_builder_manifest_and_baseline_extent(self) -> None:
        """A valid plan retains both trust-anchor and served-file identities."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        plan = self.build_plan()
        self.assertTrue(plan.ready, plan.issues)
        self.assertEqual(plan.serve_plan, self.serve_plan.resolve())
        binding = plan.bound_content.replacements[0].builder
        self.assertEqual(binding.genuine_sha256, self.sha256(self.baseline))
        self.assertEqual(binding.custom_sha256, self.sha256(self.evil))
        self.assertEqual(binding.genuine_size, self.baseline.stat().st_size)
        self.assertEqual(
            plan.bound_content.to_dict()["manifest"]["sha256"],
            self.sha256(self.serve_plan),
        )

    def test_relocated_builder_paths_bind_nonzero_baseline_extent(self) -> None:
        """Copied artifacts bind by hashes, not producer-local path strings."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        prefix = b"USB-HEADER:"
        genuine = b"BASELINE"
        suffix = b":USB-TRAILER"
        self.baseline.write_bytes(prefix + genuine + suffix)
        self.regions.write_text(
            json.dumps(
                [
                    {
                        "off": len(prefix),
                        "len": len(genuine),
                        "evil": str(self.evil),
                        "switch_after_pass": 2,
                        "mode": "benign_then_evil",
                    }
                ]
            ),
            encoding="utf-8",
        )
        self.write_serve_plan()

        builder = json.loads(
            self.builder_manifest.read_text(encoding="utf-8")
        )
        builder["genuine"].update(
            {
                "path": "/builder-host/input/mango-rootfs.tar.gz",
                "size": len(genuine),
                "sha256": hashlib.sha256(genuine).hexdigest(),
                "body_size": len(genuine),
            }
        )
        builder["custom"]["path"] = (
            "/builder-host/output/mango-rootfs.tar.gz"
        )
        self.write_json(self.builder_manifest, builder)
        serve_plan = json.loads(
            self.serve_plan.read_text(encoding="utf-8")
        )
        serve_plan["replacements"][0]["builder_manifest"] = self.file_record(
            self.builder_manifest
        )
        self.write_json(self.serve_plan, serve_plan)

        plan = self.build_plan(serve_plan=self.serve_plan)
        self.assertTrue(plan.ready, plan.issues)
        binding = plan.bound_content.replacements[0].builder
        self.assertEqual(
            binding.genuine_path,
            Path("/builder-host/input/mango-rootfs.tar.gz"),
        )
        self.assertEqual(
            binding.custom_path,
            Path("/builder-host/output/mango-rootfs.tar.gz"),
        )
        self.assertNotEqual(binding.genuine_path, self.baseline)
        self.assertNotEqual(binding.custom_path, self.evil)

        # The serve plan owns the whole-image identity, including bytes outside
        # the replacement region.
        outside_changed = bytearray(self.baseline.read_bytes())
        outside_changed[0] ^= 1
        self.baseline.write_bytes(outside_changed)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "sha256 mismatch"):
            self.build_plan(serve_plan=self.serve_plan)

        # Once the serve plan explicitly authorizes that outer-image change,
        # the builder binding remains valid because the genuine extent did not.
        serve_plan["baseline"] = self.file_record(self.baseline)
        self.write_json(self.serve_plan, serve_plan)
        plan = self.build_plan(serve_plan=self.serve_plan)
        self.assertTrue(plan.ready, plan.issues)

        # Changing a byte inside the genuine envelope still violates the
        # builder manifest even when the whole-image serve plan is refreshed.
        inside_changed = bytearray(self.baseline.read_bytes())
        inside_changed[len(prefix)] ^= 1
        self.baseline.write_bytes(inside_changed)
        serve_plan["baseline"] = self.file_record(self.baseline)
        self.write_json(self.serve_plan, serve_plan)
        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBError,
            "baseline region does not match builder manifest genuine sha256",
        ):
            self.build_plan(serve_plan=self.serve_plan)

    def test_manifest_missing_unknown_and_duplicate_fields_are_rejected(
        self,
    ) -> None:
        """The strict schema never guesses through malformed objects."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        original = json.loads(self.serve_plan.read_text(encoding="utf-8"))

        missing = dict(original)
        missing.pop("plugin")
        self.write_json(self.serve_plan, missing)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "missing"):
            self.build_plan(serve_plan=self.serve_plan)

        unknown = dict(original)
        unknown["unexpected"] = True
        self.write_json(self.serve_plan, unknown)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "unknown"):
            self.build_plan(serve_plan=self.serve_plan)

        duplicate = self.serve_plan.read_text(encoding="utf-8")
        duplicate = duplicate.replace(
            "{", '{"schema": "duplicate",', 1
        )
        self.serve_plan.write_text(duplicate, encoding="utf-8")
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "duplicate JSON"):
            self.build_plan(serve_plan=self.serve_plan)

    def test_manifest_size_and_hash_mismatches_are_rejected(self) -> None:
        """Declared sizes and hashes must match the actual bound files."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        original = json.loads(self.serve_plan.read_text(encoding="utf-8"))

        wrong_size = json.loads(json.dumps(original))
        wrong_size["baseline"]["size"] += 1
        self.write_json(self.serve_plan, wrong_size)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "size mismatch"):
            self.build_plan(serve_plan=self.serve_plan)

        wrong_hash = json.loads(json.dumps(original))
        wrong_hash["plugin"]["sha256"] = "0" * 64
        self.write_json(self.serve_plan, wrong_hash)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "sha256 mismatch"):
            self.build_plan(serve_plan=self.serve_plan)

    def test_builder_custom_and_genuine_mismatches_are_rejected(self) -> None:
        """The builder manifest remains the trust anchor for every region."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        builder = json.loads(
            self.builder_manifest.read_text(encoding="utf-8")
        )
        plan = json.loads(self.serve_plan.read_text(encoding="utf-8"))

        builder["custom"]["sha256"] = "0" * 64
        self.write_json(self.builder_manifest, builder)
        plan["replacements"][0]["builder_manifest"] = self.file_record(
            self.builder_manifest
        )
        self.write_json(self.serve_plan, plan)
        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBError, "builder manifest custom"
        ):
            self.build_plan(serve_plan=self.serve_plan)

        self.write_serve_plan()
        plan = json.loads(self.serve_plan.read_text(encoding="utf-8"))
        self.baseline.write_bytes(b"CHANGED!")
        plan["baseline"] = self.file_record(self.baseline)
        self.write_json(self.serve_plan, plan)
        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBError, "builder manifest genuine sha256"
        ):
            self.build_plan(serve_plan=self.serve_plan)

    def test_baseline_swap_after_planning_stops_before_nbdkit(self) -> None:
        """A same-path baseline replacement is caught before process start."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        plan = self.build_plan()
        replacement = self.root / "baseline replacement"
        replacement.write_bytes(self.baseline.read_bytes())
        os.replace(replacement, self.baseline)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "changed"):
            self.arm(plan)
        self.assertFalse(self.processes)
        self.assertFalse(self.state.exists())

    def test_replacement_swap_after_planning_stops_before_nbdkit(self) -> None:
        """A same-path replacement payload change is caught before start."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        plan = self.build_plan()
        replacement = self.root / "replacement swap"
        replacement.write_bytes(b"DIFFERNT")
        os.replace(replacement, self.evil)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "changed"):
            self.arm(plan)
        self.assertFalse(self.processes)
        self.assertFalse(self.state.exists())

    def test_builder_manifest_swap_after_planning_is_rejected(self) -> None:
        """The trust-anchor file identity is bound before arming."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        plan = self.build_plan()
        replacement = self.root / "builder manifest swap"
        replacement.write_bytes(self.builder_manifest.read_bytes())
        os.replace(replacement, self.builder_manifest)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "changed"):
            self.arm(plan)
        self.assertFalse(self.processes)
        self.assertFalse(self.state.exists())


class ArmAndTeardownTests(RadxaUSBFixture):
    """Exercise ownership-safe execution against temporary configfs fixtures."""

    def ready_plan(self):
        """Return a plan selecting one known fixture UDC and NBD."""
        self.add_udc("radxa-udc")
        self.add_nbd(2)
        return self.build_plan()

    def assert_supervisor_component_failure(
        self,
        mutate: object,
        expected_error: str,
    ) -> None:
        """Fail closed after one live component disappears during supervision."""
        armed = self.arm(self.ready_plan())
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, expected_error):
            radxa_usb.radxa_usb_supervise(
                armed,
                stop_requested=lambda: False,
                runner=self.runner,
                process_probe=self.process_probe,
                is_block_device=lambda path: path.exists(),
                notify=lambda _message: True,
                sleep=lambda _seconds: mutate(),
            )
        self.assertFalse(self.state.exists())

    def test_arm_execute_records_owned_resources_and_teardown_removes_them(
        self,
    ) -> None:
        """A successful arm can be fully unwound from its recorded state."""
        plan = self.ready_plan()
        armed = self.arm(plan)
        self.assertIsInstance(armed, radxa_usb.RadxaUSBArmed)
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        self.assertEqual((gadget / "UDC").read_text().strip(), "radxa-udc")
        self.assertEqual(
            (gadget / "functions" / "mass_storage.0" / "lun.0" / "file")
            .read_text()
            .strip(),
            str((self.dev / "nbd2").resolve()),
        )
        self.assertEqual(
            os.readlink(gadget / "configs" / "c.1" / "mass_storage.0"),
            str(gadget / "functions" / "mass_storage.0"),
        )
        self.assertEqual(
            self.commands[0],
            [
                "/fixture/bin/nbd-client",
                "-N",
                "default",
                "127.0.0.1",
                "19009",
                str((self.dev / "nbd2").resolve()),
                "-persist",
            ],
        )
        state = json.loads((self.state / "state.json").read_text(encoding="utf-8"))
        self.assertTrue(state["gadget_created"])
        self.assertTrue(state["nbd_attached"])
        self.assertTrue(state["udc_attached"])
        (self.state / "nbdkit.log").write_text("fixture log\n", encoding="utf-8")
        (self.state / "reads.log").write_text("fixture reads\n", encoding="utf-8")

        self.assertEqual(state["nbd_live_identity"]["pid"], "777")
        result = self.teardown()
        self.assertTrue(result["removed"])
        self.assertFalse(gadget.exists())
        self.assertFalse(self.state.exists())
        self.assertEqual(
            self.commands[-1],
            ["/fixture/bin/nbd-client", "-d", str((self.dev / "nbd2").resolve())],
        )

    def test_partial_failure_cleans_created_resources(self) -> None:
        """A UDC bind failure unwinds nbdkit, NBD, and the owned gadget."""
        plan = self.ready_plan()
        original_write = radxa_usb._radxa_usb_write_text

        def fail_udc(path: Path, value: str) -> None:
            if path.name == "UDC" and value:
                raise OSError("fixture UDC bind failure")
            original_write(path, value)

        with mock.patch.object(
            radxa_usb, "_radxa_usb_write_text", side_effect=fail_udc
        ):
            with self.assertRaisesRegex(
                radxa_usb.RadxaUSBError, "fixture UDC bind failure"
            ):
                self.arm(plan)
        self.assertTrue(self.processes[0].terminated)
        self.assertTrue(self.processes[0].waited)
        self.assertFalse((self.configfs / radxa_usb.DEFAULT_GADGET_NAME).exists())
        self.assertFalse(self.state.exists())
        self.assertEqual(
            self.commands[-1],
            ["/fixture/bin/nbd-client", "-d", str((self.dev / "nbd2").resolve())],
        )

    def test_failure_before_gadget_serial_cleans_staged_resources(self) -> None:
        """A directory-only stage is inode-bound strongly enough to clean."""
        plan = self.ready_plan()
        original_write = radxa_usb._radxa_usb_write_text

        def fail_serial(path: Path, value: str) -> None:
            if path.name == "serialnumber":
                path.write_text("", encoding="ascii")
                raise OSError("fixture serial failure")
            original_write(path, value)

        with mock.patch.object(
            radxa_usb, "_radxa_usb_write_text", side_effect=fail_serial
        ):
            with self.assertRaisesRegex(
                radxa_usb.RadxaUSBError, "fixture serial failure"
            ):
                self.arm(plan)
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())
        self.assertFalse((self.configfs / radxa_usb.DEFAULT_GADGET_NAME).exists())
        self.assertTrue(self.processes[0].terminated)
        self.assertFalse(self.state.exists())

    def test_first_idvendor_failure_cleans_partial_gadget(self) -> None:
        """The staged serial identity permits cleanup before configuration."""
        plan = self.ready_plan()
        original_write = radxa_usb._radxa_usb_write_text

        def fail_vendor(path: Path, value: str) -> None:
            if path.name == "idVendor":
                raise OSError("fixture idVendor failure")
            original_write(path, value)

        with mock.patch.object(
            radxa_usb, "_radxa_usb_write_text", side_effect=fail_vendor
        ):
            with self.assertRaisesRegex(
                radxa_usb.RadxaUSBError, "fixture idVendor failure"
            ):
                self.arm(plan)
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())
        self.assertFalse((self.configfs / radxa_usb.DEFAULT_GADGET_NAME).exists())
        self.assertTrue(self.processes[0].terminated)
        self.assertFalse(self.state.exists())

    def test_replaced_partial_gadget_is_refused(self) -> None:
        """A staged directory replaced before serial write is not deleted."""
        plan = self.ready_plan()
        original_write = radxa_usb._radxa_usb_write_text
        decoy = self.root / "ambiguous-partial-gadget"

        def replace_then_fail(path: Path, value: str) -> None:
            if path.name == "serialnumber":
                gadget = path.parents[2]
                gadget.rename(decoy)
                gadget.mkdir()
                raise OSError("fixture replaced partial gadget")
            original_write(path, value)

        with mock.patch.object(
            radxa_usb, "_radxa_usb_write_text", side_effect=replace_then_fail
        ):
            with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "inode"):
                self.arm(plan)
        self.assertTrue((self.block_root / "nbd2" / "pid").exists())
        self.assertFalse(self.processes[0].terminated)
        self.assertTrue((self.state / "state.json").exists())

    def test_partial_gadget_removal_can_resume(self) -> None:
        """A half-removed owned gadget remains recoverable from state."""
        plan = self.ready_plan()
        self.arm(plan)
        real_remove = radxa_usb._radxa_usb_remove_gadget

        def fail_after_partial(
            configfs_root: Path, gadget_name: str, errors: list[str]
        ) -> None:
            gadget = configfs_root / gadget_name
            (gadget / "configs" / "c.1" / "mass_storage.0").unlink()
            (gadget / "configs" / "c.1" / "MaxPower").unlink()
            errors.append("fixture partial gadget removal")

        with mock.patch.object(
            radxa_usb,
            "_radxa_usb_remove_gadget",
            side_effect=fail_after_partial,
        ):
            with self.assertRaisesRegex(
                radxa_usb.RadxaUSBError, "fixture partial gadget removal"
            ):
                self.teardown()
        state = json.loads((self.state / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["gadget_phase"], "removing")
        self.assertTrue(state["cleanup"]["udc_unbound"])
        self.assertFalse(state["cleanup"]["nbd_detached"])
        self.assertFalse(state["cleanup"]["gadget_removed"])
        self.assertFalse(any("-d" in command for command in self.commands))
        self.assertTrue((self.configfs / radxa_usb.DEFAULT_GADGET_NAME).exists())

        with mock.patch.object(radxa_usb, "_radxa_usb_remove_gadget", real_remove):
            self.assertTrue(self.teardown()["removed"])
        self.assertFalse(self.state.exists())

    def test_gadget_removal_skips_write_when_udc_is_already_unbound(self) -> None:
        """An empty configfs UDC is not written again during gadget removal."""
        plan = self.ready_plan()
        self.arm(plan)
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        (gadget / "UDC").write_text("\n", encoding="ascii")

        with mock.patch.object(radxa_usb, "_radxa_usb_write_text") as write_text:
            self.assertTrue(self.teardown()["removed"])

        write_text.assert_not_called()
        self.assertFalse(gadget.exists())
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())

    def test_nbd_detach_waits_until_gadget_releases_backing_device(self) -> None:
        """A live configfs backing handle keeps NBD connected until removal."""
        plan = self.ready_plan()
        self.arm(plan)
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        backing = gadget / "functions" / "mass_storage.0" / "lun.0" / "file"

        def detach_after_backing_release(command):
            self.commands.append(list(command))
            if "-d" in command and backing.exists():
                return subprocess.CompletedProcess(
                    command, 1, "", "fixture NBD remained open by configfs"
                )
            if "-d" in command:
                state = json.loads(
                    (self.state / "state.json").read_text(encoding="utf-8")
                )
                self.assertTrue(state["cleanup"]["gadget_removed"])
                (self.block_root / "nbd2" / "pid").unlink()
            return subprocess.CompletedProcess(command, 0, "", "")

        self.assertTrue(self.teardown(runner=detach_after_backing_release)["removed"])
        self.assertFalse(gadget.exists())
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())
        self.assertEqual(
            self.commands[-1],
            ["/fixture/bin/nbd-client", "-d", str((self.dev / "nbd2").resolve())],
        )

    def test_nbd_detach_polls_until_delayed_kernel_completion(self) -> None:
        """A successful detach command may report before sysfs clears."""
        plan = self.ready_plan()
        self.arm(plan)
        real_validate = radxa_usb._radxa_usb_validate_nbd_identity
        detaching = False
        post_detach_checks = 0

        def delayed_detach(command):
            nonlocal detaching
            self.commands.append(list(command))
            if "-d" in command:
                detaching = True
            return subprocess.CompletedProcess(command, 0, "", "")

        def delayed_validation(state, *, is_block_device):
            nonlocal post_detach_checks
            if detaching:
                post_detach_checks += 1
                if post_detach_checks == 3:
                    (self.block_root / "nbd2" / "pid").unlink()
            return real_validate(state, is_block_device=is_block_device)

        with mock.patch.object(
            radxa_usb,
            "_radxa_usb_validate_nbd_identity",
            side_effect=delayed_validation,
        ), mock.patch.object(
            radxa_usb.time, "monotonic", return_value=0.0
        ), mock.patch.object(radxa_usb.time, "sleep") as sleep:
            self.assertTrue(self.teardown(runner=delayed_detach)["removed"])

        self.assertEqual(post_detach_checks, 3)
        self.assertEqual(sleep.call_count, 2)
        self.assertFalse(self.state.exists())
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())

    def test_nbd_detach_timeout_preserves_resumable_state(self) -> None:
        """A detach that never appears in sysfs leaves a resumable checkpoint."""
        plan = self.ready_plan()
        self.arm(plan)

        def accepted_detach(command):
            self.commands.append(list(command))
            return subprocess.CompletedProcess(command, 0, "", "")

        with mock.patch.object(
            radxa_usb.time, "monotonic", side_effect=[0.0, 5.1]
        ), mock.patch.object(radxa_usb.time, "sleep") as sleep:
            with self.assertRaisesRegex(
                radxa_usb.RadxaUSBError, "NBD remained connected after detach"
            ):
                self.teardown(runner=accepted_detach)

        sleep.assert_not_called()
        state = json.loads((self.state / "state.json").read_text(encoding="utf-8"))
        self.assertTrue(state["cleanup"]["gadget_removed"])
        self.assertFalse(state["cleanup"]["nbd_detached"])
        self.assertFalse(state["cleanup"]["nbdkit_stopped"])
        self.assertTrue((self.block_root / "nbd2" / "pid").exists())

    def test_nbd_detach_polling_rejects_changed_identity(self) -> None:
        """A detach command cannot turn a foreign NBD claimant into success."""
        plan = self.ready_plan()
        self.arm(plan)

        def replace_nbd_claimant(command):
            self.commands.append(list(command))
            (self.block_root / "nbd2" / "pid").write_text("999\n", encoding="ascii")
            return subprocess.CompletedProcess(command, 0, "", "")

        with mock.patch.object(radxa_usb.time, "sleep") as sleep:
            with self.assertRaisesRegex(
                radxa_usb.RadxaUSBError, "no longer matches owned state"
            ):
                self.teardown(runner=replace_nbd_claimant)

        sleep.assert_not_called()
        state = json.loads((self.state / "state.json").read_text(encoding="utf-8"))
        self.assertTrue(state["cleanup"]["gadget_removed"])
        self.assertFalse(state["cleanup"]["nbd_detached"])
        self.assertEqual(
            (self.block_root / "nbd2" / "pid").read_text(encoding="ascii"),
            "999\n",
        )

    def test_failed_attach_does_not_claim_or_disconnect_nbd(self) -> None:
        """A failed nbd-client command leaves an unowned connection alone."""
        plan = self.ready_plan()

        def fail_attach(command):
            self.commands.append(list(command))
            return subprocess.CompletedProcess(command, 1, "", "fixture attach failure")

        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "attach failure"):
            self.arm(plan, runner=fail_attach)
        self.assertFalse(any("-d" in command for command in self.commands))
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())
        self.assertTrue(self.processes[0].terminated)
        self.assertFalse(self.state.exists())

    def test_failed_attach_with_partial_connection_requires_reconciliation(self) -> None:
        """An occupied device after failure cannot be attributed to this attempt."""
        plan = self.ready_plan()

        def fail_with_live_device(command):
            if "-d" in command:
                return self.runner(command)
            self.commands.append(list(command))
            checkpoint = json.loads(
                (self.state / "state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(checkpoint["nbd_phase"], "attach_pending")
            self.assertEqual(
                checkpoint["nbd_attempt"]["device_path"],
                str((self.dev / "nbd2").resolve()),
            )
            (self.block_root / "nbd2" / "pid").write_text(
                "777\n", encoding="utf-8"
            )
            return subprocess.CompletedProcess(
                command, 1, "", "fixture partial attach failure"
            )

        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBReconciliationRequired, "ambiguous NBD identity"
        ):
            self.arm(plan, runner=fail_with_live_device)
        self.assertEqual((self.block_root / "nbd2" / "pid").read_text().strip(), "777")
        self.assertFalse(any("-d" in command for command in self.commands))
        self.assertTrue(self.processes[0].terminated)
        self.assertTrue(self.processes[0].waited)
        state = json.loads((self.state / "state.json").read_text())
        self.assertEqual(state["nbd_phase"], "reconciliation_required")
        self.assertFalse(state["nbd_attached"])
        self.assertIsNone(state["nbd_live_identity"])

    def test_foreign_claim_after_free_checkpoint_on_attach_failure_is_preserved(self):
        """A foreign PID on the permanent sysfs inode never becomes our NBD."""
        plan = self.ready_plan()
        inode = (self.block_root / "nbd2").stat().st_ino

        def foreign_race(command):
            self.commands.append(list(command))
            checkpoint = json.loads((self.state / "state.json").read_text())
            self.assertIsNone(checkpoint["nbd_attempt"]["pre_pid"])
            self.assertEqual(checkpoint["nbd_attempt"]["sysfs_ino"], inode)
            (self.block_root / "nbd2" / "pid").write_text("999\n")
            raise OSError("foreign claimant won the free-device race")

        with self.assertRaises(radxa_usb.RadxaUSBReconciliationRequired):
            self.arm(plan, runner=foreign_race)
        self.assertEqual((self.block_root / "nbd2").stat().st_ino, inode)
        self.assertEqual((self.block_root / "nbd2" / "pid").read_text().strip(), "999")
        self.assertFalse(any("-d" in command for command in self.commands))
        self.assertTrue(self.processes[0].terminated)
        self.assertTrue(self.processes[0].waited)
        before = (self.state / "state.json").read_bytes()
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "reconciliation required"):
            self.teardown()
        self.assertEqual((self.state / "state.json").read_bytes(), before)

    def test_failed_attach_with_ambiguous_identity_is_preserved(self) -> None:
        """Extra live ownership prevents cleanup and requires reconciliation."""
        plan = self.ready_plan()

        def fail_with_unknown_holder(command):
            self.commands.append(list(command))
            (self.block_root / "nbd2" / "pid").write_text(
                "998\n", encoding="utf-8"
            )
            (self.block_root / "nbd2" / "holders" / "foreign").mkdir()
            return subprocess.CompletedProcess(
                command, 1, "", "fixture ambiguous attach"
            )

        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBReconciliationRequired,
            "ambiguous NBD identity",
        ):
            self.arm(plan, runner=fail_with_unknown_holder)
        self.assertFalse(any("-d" in command for command in self.commands))
        self.assertTrue((self.block_root / "nbd2" / "pid").exists())
        state = json.loads((self.state / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["nbd_phase"], "reconciliation_required")
        self.assertTrue(state["cleanup"]["nbdkit_stopped"])
        self.assertTrue(self.processes[0].terminated)

    def test_ambiguous_attach_preserves_every_foreign_nbd(self) -> None:
        """Reconciliation never detaches an unrelated pre-existing session."""
        self.add_udc("radxa-udc")
        self.add_nbd(1, pid="111", holder="foreign")
        self.add_nbd(2)
        plan = self.build_plan()

        def ambiguous(command):
            self.commands.append(list(command))
            (self.block_root / "nbd2" / "pid").write_text(
                "222\n", encoding="utf-8"
            )
            (self.block_root / "nbd2" / "holders" / "unexpected").mkdir()
            return subprocess.CompletedProcess(
                command, 1, "", "fixture ambiguous attach"
            )

        with self.assertRaises(radxa_usb.RadxaUSBReconciliationRequired):
            self.arm(plan, runner=ambiguous)
        self.assertEqual(
            (self.block_root / "nbd1" / "pid").read_text().strip(), "111"
        )
        self.assertTrue((self.block_root / "nbd1" / "holders" / "foreign").exists())
        self.assertFalse(any("-d" in command for command in self.commands))

    def test_keyboard_interrupt_during_attach_preserves_occupied_nbd(
        self,
    ) -> None:
        """KeyboardInterrupt preserves reconciliation and only stops our Popen."""
        plan = self.ready_plan()

        def interrupted(command):
            if "-d" in command:
                return self.runner(command)
            self.commands.append(list(command))
            (self.block_root / "nbd2" / "pid").write_text(
                "777\n", encoding="utf-8"
            )
            raise KeyboardInterrupt("fixture attach interrupt")

        with self.assertRaisesRegex(KeyboardInterrupt, "fixture attach interrupt"):
            self.arm(plan, runner=interrupted)
        self.assertEqual((self.block_root / "nbd2" / "pid").read_text().strip(), "777")
        self.assertFalse(any("-d" in command for command in self.commands))
        self.assertTrue(self.processes[0].terminated)
        self.assertTrue(self.processes[0].waited)
        state = json.loads((self.state / "state.json").read_text())
        self.assertEqual(state["nbd_phase"], "reconciliation_required")
        self.assertTrue(state["cleanup"]["nbdkit_stopped"])
        self.assertFalse(state["nbd_attached"])

    def test_keyboard_interrupt_during_udc_bind_cleans_all_owned_resources(
        self,
    ) -> None:
        """A later interruption unwinds NBD, gadget, and nbdkit."""
        plan = self.ready_plan()
        original_write = radxa_usb._radxa_usb_write_text

        def interrupt_udc(path: Path, value: str) -> None:
            if path.name == "UDC" and value:
                raise KeyboardInterrupt("fixture UDC interrupt")
            original_write(path, value)

        with mock.patch.object(
            radxa_usb, "_radxa_usb_write_text", side_effect=interrupt_udc
        ):
            with self.assertRaisesRegex(KeyboardInterrupt, "UDC interrupt"):
                self.arm(plan)
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())
        self.assertFalse((self.configfs / radxa_usb.DEFAULT_GADGET_NAME).exists())
        self.assertTrue(self.processes[0].terminated)
        self.assertTrue(self.processes[0].waited)
        self.assertFalse(self.state.exists())

    def test_system_exit_after_attach_is_cleaned_and_preserved(self) -> None:
        """SystemExit follows the same BaseException cleanup path."""
        plan = self.ready_plan()

        with mock.patch.object(
            radxa_usb,
            "_radxa_usb_create_gadget",
            side_effect=SystemExit("fixture system exit"),
        ):
            with self.assertRaisesRegex(SystemExit, "fixture system exit"):
                self.arm(plan)
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())
        self.assertTrue(self.processes[0].terminated)
        self.assertFalse(self.state.exists())

    def test_nbd_claimed_after_plan_is_rejected_before_attach(self) -> None:
        """Execution rechecks NBD ownership immediately before nbd-client."""
        plan = self.ready_plan()
        (self.block_root / "nbd2" / "pid").write_text("999\n", encoding="utf-8")
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "claimed after planning"):
            self.arm(plan)
        self.assertFalse(self.commands)
        self.assertTrue(self.processes[0].terminated)
        self.assertFalse(self.state.exists())

    def test_linux_sysfs_nbd_symlink_arms_and_tears_down(self) -> None:
        """The normal /sys/block/nbdN symlink layout is accepted in-root."""
        self.add_udc("radxa-udc")
        self.add_nbd(2, linux_layout=True)
        plan = self.build_plan()
        self.assertTrue(plan.ready, plan.issues)
        self.arm(plan)
        self.assertTrue(self.teardown()["removed"])

    def test_escaping_sysfs_nbd_symlink_is_rejected(self) -> None:
        """A replaced /sys/block/nbdN link cannot escape the sysfs root."""
        self.add_udc("radxa-udc")
        external = self.root / "outside" / "nbd2"
        (external / "holders").mkdir(parents=True)
        self.block_root.mkdir(parents=True, exist_ok=True)
        (self.block_root / "nbd2").symlink_to(external, target_is_directory=True)
        (self.dev / "nbd2").write_bytes(b"")
        plan = self.build_plan()
        self.assertFalse(plan.ready)
        self.assertIn("escapes injected root", "; ".join(plan.issues))

    def test_retargeted_sysfs_nbd_symlink_is_rejected(self) -> None:
        """An in-root symlink cannot rename the selected NBD identity."""
        self.add_udc("radxa-udc")
        target = self.sysfs / "devices" / "virtual" / "block" / "nbd1"
        (target / "holders").mkdir(parents=True)
        self.block_root.mkdir(parents=True, exist_ok=True)
        (self.block_root / "nbd2").symlink_to(target, target_is_directory=True)
        (self.dev / "nbd2").write_bytes(b"")
        plan = self.build_plan()
        self.assertFalse(plan.ready)
        self.assertIn("identity changed", "; ".join(plan.issues))

    def test_replaced_gadget_with_symlink_is_refused_without_mutation(self) -> None:
        """Teardown never follows a gadget path replaced by a symlink."""
        plan = self.ready_plan()
        self.arm(plan)
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        shutil.rmtree(gadget)
        decoy = self.root / "decoy-gadget"
        decoy.mkdir()
        gadget.symlink_to(decoy, target_is_directory=True)
        command_count = len(self.commands)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "symlinked path"):
            self.teardown()
        self.assertTrue(gadget.is_symlink())
        self.assertTrue((self.block_root / "nbd2" / "pid").exists())
        self.assertTrue((self.state / "state.json").exists())
        self.assertEqual(len(self.commands), command_count)

    def test_symlinked_configfs_ancestor_is_refused(self) -> None:
        """Teardown rejects a symlinked ancestor of the recorded gadget."""
        plan = self.ready_plan()
        self.arm(plan)
        real_configfs = self.configfs.with_name("real-usb-gadget")
        self.configfs.rename(real_configfs)
        self.configfs.symlink_to(real_configfs, target_is_directory=True)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "symlinked path"):
            self.teardown()
        self.assertTrue((self.state / "state.json").exists())

    def test_replaced_gadget_backing_device_is_refused(self) -> None:
        """A live gadget with a different backing device is not trusted."""
        plan = self.ready_plan()
        self.arm(plan)
        backing = (
            self.configfs
            / radxa_usb.DEFAULT_GADGET_NAME
            / "functions"
            / "mass_storage.0"
            / "lun.0"
            / "file"
        )
        backing.write_text("/dev/nbd99\n", encoding="utf-8")
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "backing device"):
            self.teardown()
        self.assertTrue((self.state / "state.json").exists())

    def test_changed_udc_binding_is_refused(self) -> None:
        """A gadget rebound to another UDC is not torn down as owned state."""
        plan = self.ready_plan()
        self.arm(plan)
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        (gadget / "UDC").write_text("different-udc\n", encoding="utf-8")
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "UDC binding"):
            self.teardown()
        self.assertTrue((self.state / "state.json").exists())

    def test_changed_nbd_connection_identity_is_refused(self) -> None:
        """A connection replaced after attach is not disconnected by this run."""
        plan = self.ready_plan()
        self.arm(plan)
        (self.block_root / "nbd2" / "pid").write_text("999\n", encoding="utf-8")
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "NBD connection"):
            self.teardown()
        self.assertTrue((self.block_root / "nbd2" / "pid").exists())
        self.assertTrue((self.state / "state.json").exists())

    def test_tampered_detach_target_is_refused(self) -> None:
        """Persisted commands cannot redirect cleanup to another NBD device."""
        plan = self.ready_plan()
        self.arm(plan)
        state_path = self.state / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["nbd_client_detach_command"] = [
            "/fixture/bin/nbd-client",
            "-d",
            "/dev/nbd99",
        ]
        state_path.write_text(json.dumps(state), encoding="utf-8")
        command_count = len(self.commands)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "valid NBD detach"):
            self.teardown()
        self.assertEqual(len(self.commands), command_count)
        self.assertTrue((self.block_root / "nbd2" / "pid").exists())
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        self.assertEqual((gadget / "UDC").read_text().strip(), "radxa-udc")

    def test_exited_nbdkit_is_treated_as_already_stopped(self) -> None:
        """An absent recorded nbdkit PID does not block teardown."""
        plan = self.ready_plan()
        self.arm(plan)
        self.processes[0].returncode = 0
        result = self.teardown(process_probe=lambda _pid, _identity: "absent")
        self.assertTrue(result["removed"])
        self.assertFalse(self.state.exists())

    def test_live_mismatched_nbdkit_pid_is_refused_before_mutation(self) -> None:
        """A reused PID is never signalled or partially cleaned as ours."""
        plan = self.ready_plan()
        self.arm(plan)
        command_count = len(self.commands)
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "different process"):
            self.teardown(process_probe=lambda _pid, _identity: "mismatch")
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        self.assertEqual((gadget / "UDC").read_text().strip(), "radxa-udc")
        self.assertTrue((self.block_root / "nbd2" / "pid").exists())
        self.assertEqual(len(self.commands), command_count)
        self.assertTrue((self.state / "state.json").exists())

    def test_persisted_process_identity_refuses_reuse_or_changed_media(self):
        """Same-plugin PID reuse or command changes are rejected before mutation."""
        plan = self.ready_plan()
        self.arm(plan)
        before = (self.state / "state.json").read_bytes()
        state = json.loads(before)
        self.assertEqual(state["schema"], "ioniq-radxa-usb-state/v5")
        self.assertEqual(state["nbdkit_identity"]["argv"], list(plan.nbdkit_command))
        command_count = len(self.commands)
        changed_media = [
            "baseline=/foreign/usb.img" if arg.startswith("baseline=") else
            "regions=/foreign/regions.json" if arg.startswith("regions=") else arg
            for arg in plan.nbdkit_command
        ]
        self.assertNotEqual(changed_media, list(plan.nbdkit_command))
        for ticks, boot, command in (
            (9999, "fixture-boot", changed_media),
            (9999, "fixture-boot", plan.nbdkit_command),
            (1234, "other-boot", plan.nbdkit_command),
            (1234, "fixture-boot", changed_media),
        ):
            with self.subTest(ticks=ticks, boot=boot, command=command):
                self.write_process_identity(command, start_ticks=ticks, boot_id=boot)
                terminate = mock.Mock()
                with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "different process"):
                    self.teardown(process_probe=self.process_probe, process_terminator=terminate)
                terminate.assert_not_called()
                self.assertEqual((self.state / "state.json").read_bytes(), before)
                self.assertEqual(len(self.commands), command_count)
                gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
                self.assertEqual((gadget / "UDC").read_text().strip(), "radxa-udc")
                self.assertTrue((self.block_root / "nbd2" / "pid").exists())

    def test_unreadable_process_identity_is_refused_before_mutation(self):
        """Missing proc identity is uncertainty, not an absent owned process."""
        plan = self.ready_plan()
        self.arm(plan)
        before = (self.state / "state.json").read_bytes()
        command_count = len(self.commands)
        (self.proc / "4242" / "stat").unlink()
        terminate = mock.Mock()
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "different process"):
            self.teardown(process_probe=self.process_probe, process_terminator=terminate)
        terminate.assert_not_called()
        self.assertEqual((self.state / "state.json").read_bytes(), before)
        self.assertEqual(len(self.commands), command_count)
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        self.assertEqual((gadget / "UDC").read_text().strip(), "radxa-udc")

    def test_changed_executable_identity_is_refused_before_mutation(self):
        """Matching argv cannot authorize a different executable inode."""
        plan = self.ready_plan()
        self.arm(plan)
        before = (self.state / "state.json").read_bytes()
        executable = self.root / "fixture-nbdkit"
        executable.rename(self.root / "old-nbdkit")
        executable.write_bytes(b"foreign executable")
        command_count = len(self.commands)
        terminate = mock.Mock()
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "different process"):
            self.teardown(process_probe=self.process_probe, process_terminator=terminate)
        terminate.assert_not_called()
        self.assertEqual((self.state / "state.json").read_bytes(), before)
        self.assertEqual(len(self.commands), command_count)

    def test_matching_persisted_process_identity_can_be_stopped(self):
        """Exact process-instance state permits bounded normal teardown."""
        plan = self.ready_plan()
        self.arm(plan)
        signalled = []

        def terminate(pid):
            signalled.append(pid)
            shutil.rmtree(self.proc / str(pid))

        result = self.teardown(process_probe=self.process_probe, process_terminator=terminate)
        self.assertTrue(result["removed"])
        self.assertEqual(signalled, [4242])
        self.assertFalse(self.state.exists())

    def test_pidfd_signal_rechecks_identity_and_closes_handle(self):
        """A reused PID after pidfd acquisition is not signalled."""
        with mock.patch.object(radxa_usb.os, "pidfd_open", return_value=55, create=True), mock.patch.object(
            radxa_usb.signal, "pidfd_send_signal", create=True
        ) as send, mock.patch.object(radxa_usb.os, "close") as close:
            with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "changed before signalling"):
                radxa_usb._radxa_usb_signal_process_instance(4242, {}, lambda *_: "mismatch")
            send.assert_not_called()
            close.assert_called_once_with(55)

    def test_pidfd_signal_targets_pinned_instance(self):
        """The production signal uses the pinned descriptor, never kill(pid)."""
        with mock.patch.object(radxa_usb.os, "pidfd_open", return_value=55, create=True), mock.patch.object(
            radxa_usb.signal, "pidfd_send_signal", create=True
        ) as send, mock.patch.object(radxa_usb.os, "close") as close, mock.patch.object(radxa_usb.os, "kill") as kill:
            radxa_usb._radxa_usb_signal_process_instance(4242, {}, lambda *_: "owned")
            send.assert_called_once_with(55, radxa_usb.signal.SIGTERM)
            kill.assert_not_called()
            close.assert_called_once_with(55)

    def test_pidfd_unavailable_never_falls_back_to_pid_signal(self):
        """Hosts without pidfds must reconcile instead of using unsafe kill."""
        real_hasattr = hasattr

        def supported(obj, name):
            return False if name == "pidfd_open" else real_hasattr(obj, name)

        with mock.patch("builtins.hasattr", side_effect=supported), mock.patch.object(radxa_usb.os, "kill") as kill:
            with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "pidfd signalling unavailable"):
                radxa_usb._radxa_usb_signal_process_instance(4242, {}, lambda *_: "owned")
            kill.assert_not_called()

    def test_repeated_teardown_is_safe_after_success(self) -> None:
        """Repeating teardown after the state root is gone is a success no-op."""
        plan = self.ready_plan()
        self.arm(plan)
        self.assertTrue(self.teardown()["removed"])
        second = self.teardown()
        self.assertFalse(second["removed"])
        self.assertTrue(second["already_absent"])

    def test_cleanup_command_failure_is_checkpointed_and_recoverable(self) -> None:
        """A failed detach persists progress and a later teardown resumes."""
        plan = self.ready_plan()
        self.arm(plan)

        def fail_detach(command):
            self.commands.append(list(command))
            return subprocess.CompletedProcess(command, 1, "", "fixture detach failure")

        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "detach failure"):
            self.teardown(runner=fail_detach)
        state = json.loads((self.state / "state.json").read_text(encoding="utf-8"))
        self.assertTrue(state["cleanup"]["udc_unbound"])
        self.assertFalse(state["cleanup"]["nbd_detached"])
        self.assertTrue(state["cleanup"]["gadget_removed"])
        self.assertFalse(state["cleanup"]["nbdkit_stopped"])
        self.assertTrue((self.block_root / "nbd2" / "pid").exists())

        recovered = self.teardown()
        self.assertTrue(recovered["removed"])
        self.assertFalse(self.state.exists())

    def test_teardown_without_state_never_removes_unknown_resource(self) -> None:
        """An already absent state root makes repeated teardown a no-op."""
        unknown = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        unknown.mkdir()
        result = self.teardown()
        self.assertTrue(result["already_absent"])
        self.assertTrue(unknown.exists())

    def test_supervisor_holds_parent_until_requested_stop(self) -> None:
        """Readiness keeps the exact Popen alive until cooperative teardown."""
        armed = self.arm(self.ready_plan())
        notifications: list[str] = []
        calls = 0

        def stop_requested() -> bool:
            nonlocal calls
            calls += 1
            return calls >= 3

        def observe_sleep(_seconds: float) -> None:
            self.assertIsNone(self.processes[0].poll())
            self.assertTrue((self.state / "state.json").exists())

        result = radxa_usb.radxa_usb_supervise(
            armed,
            stop_requested=stop_requested,
            runner=self.runner,
            process_probe=self.process_probe,
            is_block_device=lambda path: path.exists(),
            notify=lambda message: notifications.append(message) is None or True,
            sleep=observe_sleep,
        )
        self.assertTrue(result["stopped"])
        self.assertTrue(self.processes[0].terminated)
        self.assertFalse(self.state.exists())
        self.assertTrue(notifications[0].startswith("READY=1"))
        self.assertTrue(notifications[-1].startswith("STOPPING=1"))

    def test_stop_during_arm_to_supervisor_handoff_skips_readiness(self) -> None:
        """A signal in the handoff window cannot advertise a stopping run ready."""
        armed = self.arm(self.ready_plan())
        notifications: list[str] = []

        result = radxa_usb.radxa_usb_supervise(
            armed,
            stop_requested=lambda: True,
            runner=self.runner,
            process_probe=self.process_probe,
            is_block_device=lambda path: path.exists(),
            notify=lambda message: notifications.append(message) is None or True,
            sleep=lambda _seconds: None,
        )
        self.assertTrue(result["stopped"])
        self.assertTrue(self.processes[0].terminated)
        self.assertFalse(self.state.exists())
        self.assertTrue(notifications[0].startswith("STOPPING=1"))
        self.assertFalse(any(message.startswith("READY=1") for message in notifications))

    def test_stopping_notification_failure_cannot_block_safe_teardown(self) -> None:
        """Systemd notification loss is best-effort after a clean stop request."""
        armed = self.arm(self.ready_plan())

        def notify(message: str) -> bool:
            if message.startswith("STOPPING=1"):
                raise radxa_usb.RadxaUSBError("fixture notify failure")
            return True

        result = radxa_usb.radxa_usb_supervise(
            armed,
            stop_requested=lambda: True,
            runner=self.runner,
            process_probe=self.process_probe,
            is_block_device=lambda path: path.exists(),
            notify=notify,
            sleep=lambda _seconds: None,
        )
        self.assertTrue(result["stopped"])
        self.assertFalse(self.state.exists())

    def test_backend_death_unbinds_and_exits_nonzero(self) -> None:
        """A dead nbdkit removes USB exposure and reports service failure."""
        armed = self.arm(self.ready_plan())

        def kill_backend(_seconds: float) -> None:
            self.processes[0].returncode = 1

        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBError,
            "supervisor health failure: nbdkit backend is absent",
        ):
            radxa_usb.radxa_usb_supervise(
                armed,
                stop_requested=lambda: False,
                runner=self.runner,
                process_probe=self.process_probe,
                is_block_device=lambda path: path.exists(),
                notify=lambda _message: True,
                sleep=kill_backend,
            )
        self.assertFalse((self.configfs / radxa_usb.DEFAULT_GADGET_NAME).exists())
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())
        self.assertFalse(self.state.exists())

    def test_owned_nbd_disappearance_fails_closed(self) -> None:
        """A vanished NBD connection immediately removes USB exposure."""
        self.assert_supervisor_component_failure(
            lambda: (self.block_root / "nbd2" / "pid").unlink(),
            "owned NBD connection disappeared",
        )

    def test_udc_binding_disappearance_fails_closed(self) -> None:
        """A vanished UDC binding immediately tears down the owned chain."""
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME

        def unbind_udc() -> None:
            (gadget / "UDC").write_text("", encoding="utf-8")

        self.assert_supervisor_component_failure(
            unbind_udc,
            "no longer bound to its UDC",
        )

    def test_gadget_disappearance_fails_closed(self) -> None:
        """A vanished gadget immediately tears down the remaining owned chain."""
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        self.assert_supervisor_component_failure(
            lambda: shutil.rmtree(gadget),
            "owned USB gadget disappeared",
        )

    def test_foreign_nbd_is_unbound_but_never_detached(self) -> None:
        """A replaced NBD claimant cannot leave USB exposed or be detached."""
        armed = self.arm(self.ready_plan())
        command_count = len(self.commands)

        def replace_nbd(_seconds: float) -> None:
            (self.block_root / "nbd2" / "pid").write_text(
                "999\n", encoding="utf-8"
            )

        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBError,
            "NBD connection no longer matches owned state",
        ):
            radxa_usb.radxa_usb_supervise(
                armed,
                stop_requested=lambda: False,
                runner=self.runner,
                process_probe=self.process_probe,
                is_block_device=lambda path: path.exists(),
                notify=lambda _message: True,
                sleep=replace_nbd,
            )
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        self.assertEqual((gadget / "UDC").read_text().strip(), "")
        self.assertEqual(len(self.commands), command_count)
        self.assertFalse(self.processes[0].terminated)
        state = json.loads((self.state / "state.json").read_text())
        self.assertTrue(state["cleanup"]["udc_unbound"])
        self.assertEqual(state["reconciliation_required"]["phase"], "supervisor_health")

    def test_stop_race_with_foreign_nbd_still_unbinds_usb(self) -> None:
        """A backend change concurrent with SIGTERM cannot leave USB exposed."""
        armed = self.arm(self.ready_plan())
        command_count = len(self.commands)

        def replace_then_stop() -> bool:
            (self.block_root / "nbd2" / "pid").write_text(
                "999\n", encoding="utf-8"
            )
            return True

        with self.assertRaisesRegex(
            radxa_usb.RadxaUSBError,
            "supervisor teardown incomplete",
        ):
            radxa_usb.radxa_usb_supervise(
                armed,
                stop_requested=replace_then_stop,
                runner=self.runner,
                process_probe=self.process_probe,
                is_block_device=lambda path: path.exists(),
                notify=lambda _message: True,
                sleep=lambda _seconds: None,
            )
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        self.assertEqual((gadget / "UDC").read_text().strip(), "")
        self.assertEqual(len(self.commands), command_count)
        self.assertFalse(self.processes[0].terminated)

    def test_foreign_process_identity_is_unbound_but_not_signalled(self) -> None:
        """Retaining Popen does not bypass exact process-instance validation."""
        armed = self.arm(self.ready_plan())

        def replace_identity(_seconds: float) -> None:
            self.write_process_identity(
                armed.plan.nbdkit_command,
                start_ticks=9999,
            )

        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "backend is mismatch"):
            radxa_usb.radxa_usb_supervise(
                armed,
                stop_requested=lambda: False,
                runner=self.runner,
                process_probe=self.process_probe,
                is_block_device=lambda path: path.exists(),
                notify=lambda _message: True,
                sleep=replace_identity,
            )
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        self.assertEqual((gadget / "UDC").read_text().strip(), "")
        self.assertFalse(self.processes[0].terminated)

    def test_foreign_gadget_identity_is_left_untouched(self) -> None:
        """Fail-closed cleanup never mutates a gadget whose identity changed."""
        armed = self.arm(self.ready_plan())
        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME

        def replace_gadget(_seconds: float) -> None:
            (gadget / "strings" / "0x409" / "serialnumber").write_text(
                "FOREIGN-GADGET\n", encoding="utf-8"
            )

        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "identity no longer"):
            radxa_usb.radxa_usb_supervise(
                armed,
                stop_requested=lambda: False,
                runner=self.runner,
                process_probe=self.process_probe,
                is_block_device=lambda path: path.exists(),
                notify=lambda _message: True,
                sleep=replace_gadget,
            )
        self.assertEqual((gadget / "UDC").read_text().strip(), "radxa-udc")
        self.assertFalse(self.processes[0].terminated)

    def test_cancellation_before_udc_bind_cleans_without_exposure(self) -> None:
        """A stop during final validation removes staged resources before bind."""
        plan = self.ready_plan()
        original_create = radxa_usb._radxa_usb_create_gadget
        created = False

        def create_then_cancel(*args, **kwargs) -> None:
            nonlocal created
            original_create(*args, **kwargs)
            created = True

        with mock.patch.object(
            radxa_usb,
            "_radxa_usb_create_gadget",
            side_effect=create_then_cancel,
        ):
            with self.assertRaisesRegex(radxa_usb.RadxaUSBCancelled, "cancelled"):
                self.arm(plan, cancel_requested=lambda: created)
        self.assertFalse((self.configfs / radxa_usb.DEFAULT_GADGET_NAME).exists())
        self.assertFalse((self.block_root / "nbd2" / "pid").exists())
        self.assertFalse(self.state.exists())

    def test_live_status_rejects_stale_process_nbd_and_udc_state(self) -> None:
        """Stored attached flags are never accepted without live components."""
        self.arm(self.ready_plan())
        kwargs = {
            "state_root": self.state,
            "process_probe": self.process_probe,
            "is_block_device": lambda path: path.exists(),
        }
        self.assertTrue(radxa_usb.radxa_usb_status(**kwargs)["armed"])

        shutil.rmtree(self.proc / "4242")
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "backend is absent"):
            radxa_usb.radxa_usb_status(**kwargs)
        self.write_process_identity(
            json.loads((self.state / "state.json").read_text())["nbdkit_command"]
        )

        (self.block_root / "nbd2" / "pid").unlink()
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "NBD connection"):
            radxa_usb.radxa_usb_status(**kwargs)
        (self.block_root / "nbd2" / "pid").write_text("777\n", encoding="utf-8")

        gadget = self.configfs / radxa_usb.DEFAULT_GADGET_NAME
        (gadget / "UDC").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(radxa_usb.RadxaUSBError, "no longer bound"):
            radxa_usb.radxa_usb_status(**kwargs)

    def test_sd_notify_sends_ready_from_the_main_process(self) -> None:
        """Native notification avoids a helper PID attribution race."""
        notify_path = self.root / "notify.sock"
        receiver = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        receiver.bind(str(notify_path))
        receiver.settimeout(1)
        try:
            with mock.patch.dict(os.environ, {"NOTIFY_SOCKET": str(notify_path)}):
                self.assertTrue(radxa_usb.radxa_usb_sd_notify("READY=1\nSTATUS=ready"))
            self.assertEqual(receiver.recv(128), b"READY=1\nSTATUS=ready")
        finally:
            receiver.close()


class PreparedContentTests(RadxaUSBFixture):
    """Exercise cached startup once, independently of other fixture subclasses."""

    test_reuses_prepared_images = RadxaUSBFixture._check_cache_survives_new_session_without_reading_large_inputs
    test_rejects_restored_mtime = RadxaUSBFixture._check_cache_rejects_mutation_even_with_restored_mtime
    test_rejects_new_inode = RadxaUSBFixture._check_cache_rejects_replacement_inode
    test_private_cache_and_partial_prepare = RadxaUSBFixture._check_cache_private_modes_and_failed_prepare
    test_prepare_cli = RadxaUSBFixture._check_prepare_cli_builds_cache_without_hardware_inspection


if __name__ == "__main__":
    unittest.main()
