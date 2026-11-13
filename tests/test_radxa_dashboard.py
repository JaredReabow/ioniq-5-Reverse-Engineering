"""Fixture-only tests for the read-only Radxa dashboard."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock
from urllib.request import Request, urlopen

PROJECT = Path(__file__).parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools.uk_fw import radxa_dashboard


class DashboardFixture(unittest.TestCase):
    """Create a temporary controller boundary with no hardware access."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.state_root = self.root / "run" / "ioniq-toctou"
        self.state_root.mkdir(parents=True)
        self.persistent_root = self.root / "var" / "lib" / "ioniq5-update"
        self.persistent_root.mkdir(mode=0o700, parents=True)
        self.sysfs = self.root / "sys"
        self.proc = self.root / "proc"
        self.gadget = self.sysfs / "kernel" / "config" / "usb_gadget" / "ioniq_toctou"
        self.gadget.mkdir(parents=True)
        (self.sysfs / "class" / "udc" / "fixture-udc").mkdir(parents=True)
        (self.sysfs / "class" / "udc" / "fixture-udc" / "state").write_text(
            "configured\n", encoding="utf-8"
        )
        (self.gadget / "UDC").write_text("fixture-udc\n", encoding="utf-8")
        (self.sysfs / "block" / "nbd2").mkdir(parents=True)
        (self.sysfs / "block" / "nbd2" / "pid").write_text("4242\n", encoding="utf-8")
        self.ui = self.root / "WEB_UI_radxa_dashboard.html"
        self.ui.write_text(
            "<!doctype html><title>fixture dashboard</title>", encoding="utf-8"
        )
        self.state_path = self.state_root / "state.json"
        self.log_path = self.state_root / "nbdkit.log"
        self.reads_path = self.state_root / "reads.log"
        self.boot_id_path = self.proc / "sys" / "kernel" / "random" / "boot_id"
        self.boot_id_path.parent.mkdir(parents=True)
        self.boot_id_path.write_text("11111111-1111-4111-8111-111111111111\n")
        self.write_active_fixture()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_active_fixture(self) -> None:
        """Publish a complete active controller snapshot and measured logs."""

        plugin = self.root / "nbdkit_dynamic_media.py"
        plugin.write_text("# fixture\n", encoding="utf-8")
        (self.proc / "4242").mkdir(parents=True)
        (self.proc / "4242" / "cmdline").write_bytes(
            b"python3\0" + str(plugin).encode() + b"\0"
        )
        baseline = {
            "path": "/opt/ioniq5-update/media/baseline.img",
            "size": 30064771072,
            "sha256": "a" * 64,
        }
        replacement = {
            "path": "/opt/ioniq5-update/media/custom.te2",
            "size": 20,
            "sha256": "b" * 64,
        }
        state = {
            "schema": "ioniq-radxa-usb-state/v4",
            "tool_version": "1.2.0",
            "udc": "fixture-udc",
            "gadget_name": "ioniq_toctou",
            "nbd_name": "nbd2",
            "nbd_attached": True,
            "nbdkit_pid": 4242,
            "nbdkit_plugin": str(plugin),
            "nbdkit_command": [
                "nbdkit",
                "-f",
                str(plugin),
                f"log={self.log_path}",
                f"reads={self.reads_path}",
                "password=must-not-appear",
            ],
            "bound_content": {
                "baseline": baseline,
                "manifest": {
                    "path": "/opt/ioniq5-update/config/serve-plan.json",
                    "size": 500,
                    "sha256": "c" * 64,
                },
                "plugin": {
                    "path": str(plugin),
                    "size": plugin.stat().st_size,
                    "sha256": "d" * 64,
                },
                "regions": {
                    "path": "/opt/ioniq5-update/config/regions.json",
                    "size": 200,
                    "sha256": "e" * 64,
                },
                "replacements": [
                    {
                        "replacement": replacement,
                        "offset": 100,
                        "length": 20,
                        "switch_after_pass": 2,
                        "mode": "benign_then_evil",
                    }
                ],
            },
            "cleanup": {
                "udc_unbound": False,
                "nbd_detached": False,
                "gadget_removed": False,
                "nbdkit_stopped": False,
            },
            "reconciliation_required": None,
        }
        self.state_path.write_text(json.dumps(state), encoding="utf-8")
        self.log_path.write_text(
            "[dynamic-media] 2026-11-12T00:00:00 mono=90.000 "
            "region@100 pass=2 start off=100 len=16\n"
            "[dynamic-media] 2026-11-12T00:00:01 mono=90.100 "
            "region@100 switch pass=2 mode=benign_then_evil password=secret-value\n",
            encoding="utf-8",
        )
        self.reads_path.write_text(
            "95.000 B off=100 len=10 pass=2 region=100\n"
            "95.500 R off=105 len=10 pass=2 region=100\n"
            "96.000 R off=110 len=5 pass=2 region=100\n",
            encoding="utf-8",
        )

    @staticmethod
    def systemctl_result() -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            ["systemctl"],
            0,
            stdout=(
                "LoadState=loaded\n"
                "ActiveState=active\n"
                "SubState=running\n"
                "UnitFileState=enabled\n"
                "ExecMainPID=1001\n"
                "StatusText=IONIQ update media active\n"
            ),
            stderr="",
        )

    def config(self) -> radxa_dashboard.DashboardConfig:
        return radxa_dashboard.DashboardConfig(
            state_root=self.state_root,
            persistent_root=self.persistent_root,
            sysfs_root=self.sysfs,
            proc_root=self.proc,
            web_ui_path=self.ui,
        )

    def write_prepared_cache(self) -> list[Path]:
        """Write the controller's private metadata-only prepared-content shape."""

        private_dir = self.root / "private-do-not-expose"
        private_dir.mkdir(mode=0o700)
        baseline = private_dir / "baseline.img"
        replacement = private_dir / "custom-firmware.te2"
        baseline.write_bytes(b"B" * 80)
        replacement.write_bytes(b"R" * 20)
        baseline.chmod(0o600)
        replacement.chmod(0o600)
        entries: dict[str, object] = {}
        for path, offset, length in (
            (baseline, 0, baseline.stat().st_size),
            (replacement, 0, replacement.stat().st_size),
        ):
            info = path.lstat()
            entries[
                json.dumps(
                    [str(path), offset, length],
                    separators=(",", ":"),
                )
            ] = {
                "identity": [
                    info.st_dev,
                    info.st_ino,
                    info.st_size,
                    info.st_mtime_ns,
                    info.st_ctime_ns,
                    info.st_mode,
                    info.st_uid,
                ],
                "sha256": ("a" if path == baseline else "b") * 64,
            }
        cache = self.persistent_root / "validation-cache.json"
        cache.write_text(
            json.dumps(
                {
                    "schema": radxa_dashboard.PREPARED_CACHE_SCHEMA,
                    "tool_version": radxa_dashboard.PREPARED_CACHE_TOOL_VERSION,
                    "entries": entries,
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        cache.chmod(0o600)
        return [baseline, replacement]

    def collect(self) -> tuple[dict[str, object], list[list[str]]]:
        commands: list[list[str]] = []

        def runner(command, _timeout):
            commands.append(list(command))
            return self.systemctl_result()

        status = radxa_dashboard.radxa_dashboard_collect_status(
            self.config(),
            command_runner=runner,
            now_monotonic=lambda: 97.0,
            now_wall=lambda: datetime(2026, 11, 12, tzinfo=timezone.utc),
        )
        return status, commands


class RadxaDashboardTests(DashboardFixture):
    """Verify honest progress, bounded observation and HTTP safety."""

    def test_readable_zero_size_proc_cmdline_reports_the_running_backend(self) -> None:
        """Kernel procfs size zero does not mean its command line is empty."""
        from types import SimpleNamespace
        cmdline = (self.proc / '4242/cmdline').stat()
        real_fstat = os.fstat

        def proc_stat(descriptor):
            info = real_fstat(descriptor)
            if (info.st_dev, info.st_ino) == (cmdline.st_dev, cmdline.st_ino):
                return SimpleNamespace(st_mode=info.st_mode, st_size=0, st_mtime=info.st_mtime)
            return info

        with mock.patch.object(os, 'fstat', side_effect=proc_stat):
            state = json.loads(self.state_path.read_text())
            health, detail = radxa_dashboard._process_status(state, self.proc)
        self.assertEqual(health, 'healthy', detail)

    def test_head_reads_are_bounded_even_for_large_files(self) -> None:
        """Both head and tail observation respect their byte budget."""
        source = self.root / 'large-observation'
        source.write_text('a' * 512)
        snapshot = radxa_dashboard._bounded_file(source, limit=32, tail=False)
        self.assertEqual(len(snapshot.text), 32)
        self.assertTrue(snapshot.truncated)

    def test_fuse_transport_uses_live_controller_verdict_without_nbd(self) -> None:
        """A FUSE-backed session never depends on a stale NBD attachment."""
        state = json.loads(self.state_path.read_text())
        state['backing_kind'] = 'fuse-direct'
        self.state_path.write_text(json.dumps(state))
        (self.sysfs / 'block/nbd2/pid').unlink()
        with mock.patch.object(radxa_dashboard._radxa_controller, 'radxa_usb_status',
                               return_value={'healthy': True, 'backing_kind': 'fuse-direct'}) as probe:
            status, _ = self.collect()
        probe.assert_called_once_with(state_root=self.state_root)
        row = next(item for item in status['connections'] if item['name'] == 'USB backing')
        self.assertEqual(row['status'], 'healthy')
        self.assertIn('read-only', row['value'])

    def test_fuse_helper_failure_is_visible_in_dashboard(self) -> None:
        """A recorded mount alone must not be displayed as a working transport."""
        state = json.loads(self.state_path.read_text())
        state['backing_kind'] = 'fuse-direct'
        self.state_path.write_text(json.dumps(state))
        with mock.patch.object(radxa_dashboard._radxa_controller, 'radxa_usb_status',
                               side_effect=radxa_dashboard._radxa_controller.RadxaUSBError('helper exited')):
            status, _ = self.collect()
        row = next(item for item in status['connections'] if item['name'] == 'USB backing')
        self.assertEqual(row['status'], 'error')
        self.assertIn('helper exited', row['value'])

    def test_active_snapshot_reports_measured_coverage_without_flash_claim(self) -> None:
        status, commands = self.collect()

        self.assertEqual(status["runtime"]["status"], "prepared")
        self.assertEqual(status["level"], "active")
        self.assertEqual(status["progress"]["percent"], 75.0)
        self.assertEqual(status["progress"]["measured_bytes"], 15)
        self.assertEqual(status["progress"]["pass"], 2)
        self.assertEqual(status["progress"]["latest_source"], "R")
        self.assertEqual(status["progress"]["car_write_status"], "unknown")
        self.assertNotIn("flash complete", json.dumps(status).lower())
        self.assertEqual(len(commands), 1)
        self.assertIn("ioniq-update-media.service", commands[0])
        self.assertFalse(any("radxa_usb.py" in arg for arg in commands[0]))
        self.assertNotIn("must-not-appear", json.dumps(status))
        self.assertNotIn("secret-value", json.dumps(status))
        self.assertTrue(any("[REDACTED]" in line for line in status["logs"]["event"]))
        labels = {item["label"] for item in status["artifacts"]}
        self.assertIn("Baseline image", labels)
        self.assertIn("Replacement 1", labels)

    def test_incomplete_coverage_is_not_rounded_to_a_finished_car_write(self) -> None:
        self.reads_path.write_text(
            "95.000 B off=100 len=5 pass=2 region=100\n",
            encoding="utf-8",
        )
        status, _commands = self.collect()

        self.assertEqual(status["progress"]["percent"], 25.0)
        self.assertFalse(status["progress"]["pass_finished"])
        self.assertEqual(status["timeline"][-1]["status"], "unknown")

    def test_current_prepared_cache_without_runtime_is_not_armed(self) -> None:
        payloads = self.write_prepared_cache()
        self.state_path.unlink()

        def runner(_command, _timeout):
            return subprocess.CompletedProcess(
                ["systemctl"],
                0,
                stdout="LoadState=loaded\nActiveState=inactive\n",
                stderr="",
            )

        bounded_paths: list[Path] = []
        original_bounded_file = radxa_dashboard._bounded_file

        def tracked_bounded_file(path, **kwargs):
            bounded_paths.append(Path(path))
            return original_bounded_file(path, **kwargs)

        with (
            mock.patch.object(
                radxa_dashboard,
                "_bounded_file",
                side_effect=tracked_bounded_file,
            ),
            mock.patch.object(
                Path,
                "open",
                side_effect=AssertionError("prepared payload must not be opened"),
            ),
        ):
            status = radxa_dashboard.radxa_dashboard_collect_status(
                self.config(),
                command_runner=runner,
                now_monotonic=lambda: 97.0,
            )

        self.assertEqual(status["runtime"]["status"], "not_armed")
        self.assertEqual(status["headline"], "Prepared media ready; not armed")
        self.assertEqual(status["preparation"]["status"], "current")
        self.assertEqual(status["preparation"]["progress"]["percent"], 100.0)
        self.assertEqual(status["timeline"][1]["status"], "done")
        self.assertEqual(status["timeline"][-1]["status"], "unknown")
        rendered = json.dumps(status)
        self.assertNotIn("private-do-not-expose", rendered)
        self.assertNotIn(str(self.persistent_root), rendered)
        self.assertTrue(all(item["name"] in rendered for item in status["preparation"]["artifacts"]))
        self.assertFalse(set(path.resolve() for path in bounded_paths) & set(payloads))
        self.assertEqual(len(payloads), 2)

    def test_changed_prepared_identity_is_reported_without_rehashing(self) -> None:
        baseline, _replacement = self.write_prepared_cache()
        self.state_path.unlink()
        baseline.write_bytes(b"C" * baseline.stat().st_size)

        def runner(_command, _timeout):
            return subprocess.CompletedProcess(
                ["systemctl"], 0, stdout="LoadState=loaded\nActiveState=inactive\n", stderr=""
            )

        status = radxa_dashboard.radxa_dashboard_collect_status(
            self.config(),
            command_runner=runner,
            now_monotonic=lambda: 97.0,
        )

        self.assertEqual(status["runtime"]["status"], "not_armed")
        self.assertEqual(status["preparation"]["status"], "changed")
        self.assertEqual(status["preparation"]["cache"]["changed_entries"], 1)
        self.assertIn("baseline.img", status["preparation"]["cache"]["changed_names"])
        self.assertIn("identities changed", status["headline"].lower())
        self.assertNotIn(str(self.root), json.dumps(status))
        artifact = next(item for item in status["preparation"]["artifacts"] if item["name"] == "baseline.img")
        self.assertFalse(artifact["current"])

    def test_current_whole_file_supersedes_old_size_without_hiding_mutation(self) -> None:
        """Retained old-size keys do not mark a freshly prepared file stale."""
        baseline, _ = self.write_prepared_cache()
        cache = self.persistent_root / "validation-cache.json"
        value = json.loads(cache.read_text())
        current_key = json.dumps([str(baseline), 0, baseline.stat().st_size], separators=(",", ":"))
        old = json.loads(json.dumps(value["entries"][current_key]))
        old["identity"][2] = 30
        old["sha256"] = "c" * 64
        value["entries"][json.dumps([str(baseline), 0, 30], separators=(",", ":"))] = old
        cache.write_text(json.dumps(value, sort_keys=True))

        status = radxa_dashboard.radxa_dashboard_preparation_status(self.config())
        self.assertEqual(status["status"], "current")
        self.assertEqual(status["cache"]["changed_entries"], 0)
        self.assertEqual(status["cache"]["superseded_entries"], 1)
        artifact = next(item for item in status["artifacts"] if item["name"] == "baseline.img")
        self.assertEqual((artifact["size"], artifact["extents"], artifact["sha256"]), (80, 1, "a" * 64))

        # A matching partial extent cannot vouch for the whole file.
        current = value["entries"].pop(current_key)
        value["entries"][json.dumps([str(baseline), 0, 20], separators=(",", ":"))] = current
        cache.write_text(json.dumps(value, sort_keys=True))
        partial = radxa_dashboard.radxa_dashboard_preparation_status(self.config())
        self.assertEqual(partial["status"], "changed")
        self.assertEqual(partial["cache"]["superseded_entries"], 0)

        baseline.write_bytes(b"C" * baseline.stat().st_size)
        changed = radxa_dashboard.radxa_dashboard_preparation_status(self.config())
        self.assertEqual(changed["status"], "changed")
        self.assertEqual(changed["cache"]["changed_entries"], 2)

    def test_invalid_prepared_cache_is_distinct_from_missing_cache(self) -> None:
        self.state_path.unlink()
        missing = radxa_dashboard.radxa_dashboard_preparation_status(self.config())
        self.assertEqual(missing["status"], "missing")

        self.write_prepared_cache()
        cache = self.persistent_root / "validation-cache.json"
        cache.chmod(0o644)
        invalid = radxa_dashboard.radxa_dashboard_preparation_status(self.config())
        self.assertEqual(invalid["status"], "invalid")
        self.assertFalse(invalid["cache"]["valid"])
        self.assertNotIn(str(self.root), json.dumps(invalid))

    def test_inactive_preserved_state_is_explicitly_interrupted(self) -> None:
        def runner(_command, _timeout):
            return subprocess.CompletedProcess(
                ["systemctl"], 0, stdout="LoadState=loaded\nActiveState=inactive\n", stderr=""
            )

        status = radxa_dashboard.radxa_dashboard_collect_status(
            self.config(),
            command_runner=runner,
            now_monotonic=lambda: 97.0,
        )

        self.assertTrue(status["runtime"]["interrupted"])
        self.assertEqual(status["level"], "warning")
        self.assertIn("preserved", status["headline"].lower())
        self.assertEqual(status["preparation"]["status"], "missing")

    def test_activating_service_is_not_misreported_as_interrupted(self) -> None:
        def runner(_command, _timeout):
            return subprocess.CompletedProcess(
                ["systemctl"],
                0,
                stdout="LoadState=loaded\nActiveState=activating\n",
                stderr="",
            )

        status = radxa_dashboard.radxa_dashboard_collect_status(
            self.config(),
            command_runner=runner,
            now_monotonic=lambda: 97.0,
        )

        self.assertFalse(status["runtime"]["interrupted"])
        self.assertEqual(status["level"], "waiting")
        self.assertIn("preparing", status["headline"].lower())
        self.assertEqual(status["timeline"][0]["status"], "waiting")

    def test_previous_boot_armed_journal_warns_without_claiming_a_flash(self) -> None:
        self.write_prepared_cache()
        self.state_path.unlink()
        session = self.persistent_root / "session.json"
        session.write_text(
            json.dumps(
                {
                    "schema": radxa_dashboard.SESSION_SCHEMA,
                    "boot_id": "22222222-2222-4222-8222-222222222222",
                    "state": "armed",
                    "updated_at": "2026-11-12T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        session.chmod(0o600)

        def runner(_command, _timeout):
            return subprocess.CompletedProcess(
                ["systemctl"], 0, stdout="LoadState=loaded\nActiveState=inactive\n", stderr=""
            )

        status = radxa_dashboard.radxa_dashboard_collect_status(
            self.config(),
            command_runner=runner,
            now_monotonic=lambda: 97.0,
        )

        self.assertTrue(status["runtime"]["interrupted"])
        self.assertTrue(status["runtime"]["interrupted_previous_session"])
        self.assertEqual(status["runtime"]["journal_relation"], "previous")
        self.assertEqual(status["level"], "warning")
        self.assertIn("previous boot", status["headline"].lower())
        self.assertIn("will not auto-arm", status["phase"])
        self.assertNotIn("car update complete", json.dumps(status).lower())
        self.assertEqual(status["progress"]["car_write_status"], "unknown")

    def test_prepare_log_reports_measured_progress_without_private_path(self) -> None:
        self.state_path.unlink()
        log = self.persistent_root / "prepare.log"
        log.write_text(
            "prepare start total=100\n"
            "prepare bytes=25 total=100 file=/home/private/baseline.img\n",
            encoding="utf-8",
        )
        preparation = radxa_dashboard.radxa_dashboard_preparation_status(self.config())

        self.assertEqual(preparation["status"], "missing")
        self.assertEqual(preparation["progress"]["percent"], 25.0)
        self.assertEqual(preparation["progress"]["file"], "baseline.img")
        rendered = json.dumps(preparation)
        self.assertIn("baseline.img", rendered)
        self.assertNotIn("/home/private", rendered)

        def runner(_command, _timeout):
            return subprocess.CompletedProcess(
                ["systemctl"], 0, stdout="LoadState=loaded\nActiveState=inactive\n", stderr=""
            )

        status = radxa_dashboard.radxa_dashboard_collect_status(
            self.config(),
            command_runner=runner,
            now_monotonic=lambda: 97.0,
        )
        self.assertEqual(status["headline"], "Preparation progress observed")
        self.assertEqual(status["preparation"]["progress"]["percent"], 25.0)
        self.assertEqual(status["timeline"][-1]["status"], "unknown")

    def test_symlink_state_is_not_followed(self) -> None:
        secret = self.root / "secret.json"
        secret.write_text('{"secret": "do-not-read"}', encoding="utf-8")
        self.state_path.unlink()
        self.state_path.symlink_to(secret)
        status, _commands = self.collect()

        self.assertIn("runtime state unavailable", " ".join(status["errors"]))
        self.assertNotIn("do-not-read", json.dumps(status))

    def test_http_api_is_read_only_and_server_refuses_non_loopback(self) -> None:
        server = radxa_dashboard.radxa_dashboard_create_server(self.config(), port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_address[1]
        try:
            with urlopen(f"http://127.0.0.1:{port}/api/status", timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
                self.assertEqual(payload["api_version"], "1.0.0")
                self.assertEqual(response.headers["Cache-Control"], "no-store")
            request = Request(
                f"http://127.0.0.1:{port}/api/arm",
                data=b"{}",
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with self.assertRaises(Exception) as raised:
                urlopen(request, timeout=3)
            self.assertEqual(getattr(raised.exception, "code", None), 405)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

        with self.assertRaisesRegex(ValueError, "exclusively"):
            radxa_dashboard.radxa_dashboard_create_server(
                self.config(), host="0.0.0.0", port=0
            )

    def test_version_and_ui_have_recovery_and_reduced_motion(self) -> None:
        self.assertEqual(radxa_dashboard.radxa_dashboard_version(), "1.0.10")
        self.assertEqual(radxa_dashboard.radxa_dashboard_api_version(), "1.0.0")
        self.assertEqual(
            radxa_dashboard.DEFAULT_STATE_ROOT,
            Path("/run/ioniq-toctou"),
        )
        self.assertEqual(
            radxa_dashboard.DEFAULT_SERVICE_NAME,
            "ioniq-update-media.service",
        )
        self.assertEqual(
            radxa_dashboard.DEFAULT_PERSISTENT_ROOT,
            Path("/var/lib/ioniq5-update"),
        )
        self.assertEqual(
            radxa_dashboard.PREPARED_CACHE_SCHEMA,
            "ioniq-radxa-prepared-content/v1",
        )
        self.assertEqual(radxa_dashboard.PREPARED_CACHE_TOOL_VERSION, "1.2.1")
        self.assertEqual(radxa_dashboard.SESSION_SCHEMA, "ioniq-radxa-session/v1")
        source = (PROJECT / "tools/uk_fw/WEB_UI_radxa_dashboard.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("fetch(\"/api/status\"", source)
        self.assertIn("prefers-reduced-motion", source)
        self.assertIn("Automatic reconnect", source)
        self.assertIn("No synthetic percentage", source)
        self.assertIn("Preparation progress", source)
        self.assertIn("prepare-log", source)
        self.assertIn('"version">1.0.10', source)
        self.assertIn("textContent", source)
        self.assertNotIn("--no-sandbox", source)
        self.assertNotIn("innerHTML", source)

    def test_installed_script_resolves_canonical_controller_dependency(self) -> None:
        """Exercise script-mode import from the separate installed dashboard directory."""
        import shutil
        installed = self.root / 'installed'
        dashboard = installed / 'dashboard'
        controller = installed / 'tools/uk_fw'
        dashboard.mkdir(parents=True)
        controller.mkdir(parents=True)
        for name, dest in [('radxa_dashboard.py', dashboard), ('radxa_usb.py', controller)]:
            shutil.copy2(PROJECT / 'tools/uk_fw' / name, dest / name)
        installer = (PROJECT / 'tools/uk_fw/install-radxa-dashboard.sh').read_text()
        self.assertIn('Environment=PYTHONPATH=/opt/ioniq5-update/tools/uk_fw', installer)
        result = subprocess.run([sys.executable, str(dashboard / 'radxa_dashboard.py'), '--help'],
                                cwd=self.root, env=os.environ | {'PYTHONPATH': str(controller)},
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('usage:', result.stdout)
        self.assertIn('runuser -u "$desktop_user" -- "$configuration_helper"', installer)
        dashboard_source = (
            PROJECT / "tools/uk_fw/radxa_dashboard.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("hashlib", dashboard_source)

    def test_dashboard_inline_javascript_parses(self) -> None:
        source = (PROJECT / "tools/uk_fw/WEB_UI_radxa_dashboard.html").read_text(
            encoding="utf-8"
        )
        parts = source.split("<script>", 1)
        self.assertEqual(len(parts), 2)
        script = parts[1].split("</script>", 1)[0]
        self.assertIsNone(
            re.search(r"\bels\.[A-Za-z_$][A-Za-z0-9_$]*-", script),
            "hyphenated element ids must use bracket notation",
        )
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node.js is required for the JavaScript syntax gate")
        with tempfile.TemporaryDirectory() as temporary:
            script_path = Path(temporary) / "dashboard.js"
            script_path.write_text(script, encoding="utf-8")
            result = subprocess.run(
                [node, "--check", str(script_path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)


class DashboardInstallerTests(unittest.TestCase):
    """Check installer syntax and browser launch boundaries."""

    def test_power_profile_removes_idle_actions_and_keeps_manual_buttons(self) -> None:
        """The dedicated updater cannot inherit KDE's 15-minute auto-suspend."""
        installer = PROJECT / "tools/uk_fw/install-radxa-dashboard.sh"
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "power.ini"
            config.write_text("[AC]\nicon=battery-charging\n\n[AC][SuspendSession]\nidleTime=900000\nsuspendType=1\n\n[AC][DPMSControl]\nidleTime=600\n\n[AC][HandleButtonEvents]\npowerButtonAction=16\n")
            result = subprocess.run(["bash", str(installer), "--render-power-config", str(config)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = config.read_text()
            self.assertNotIn("SuspendSession", rendered)
            self.assertNotIn("DPMSControl", rendered)
            self.assertIn("[AC][HandleButtonEvents]", rendered)
            self.assertIn("powerButtonAction = 16", rendered)
        self.assertIn("--what=sleep:idle --mode=block", installer.read_text())

    def test_installer_is_valid_and_does_not_use_insecure_chromium_flags(self) -> None:
        installer = PROJECT / "tools/uk_fw/install-radxa-dashboard.sh"
        result = subprocess.run(
            ["bash", "-n", str(installer)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        source = installer.read_text(encoding="utf-8")
        self.assertIn("desktop_user=$1", source)
        self.assertIn(
            'exec /usr/bin/chromium --user-data-dir="$chromium_profile_dir" --kiosk',
            source,
        )
        self.assertIn(".local/share/ioniq5-dashboard-browser", source)
        self.assertIn("no browser was force-launched", source)
        self.assertNotIn("rm -rf", source)
        self.assertNotIn("--no-sandbox", source)
        self.assertIn("backup_existing", source)
        self.assertIn("ioniq5-radxa-dashboard.service", source)
        self.assertNotIn("ioniq5-update-media.service", source)
        self.assertIn("/etc/gdm3/daemon.conf", source)
        self.assertIn("AutomaticLoginEnable=true", source)
        self.assertIn('f"AutomaticLogin={user}"', source)
        self.assertIn("Session=plasma", source)
        self.assertIn("no display manager restart", source)
        self.assertNotIn("apt-get", source)
        self.assertNotIn("radxa_usb.py", source)

    def test_gdm_renderer_preserves_sections_and_sets_explicit_autologin(self) -> None:
        installer = PROJECT / "tools/uk_fw/install-radxa-dashboard.sh"
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary) / "daemon.conf"
            config.write_text(
                "# managed fixture\n"
                "[security]\n"
                "DisallowTCP=false\n"
                "\n"
                "[daemon]\n"
                "# existing owner setting\n"
                "WaylandEnable=false\n"
                "\n"
                "[chooser]\n"
                "IncludeAll=true\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    "bash",
                    str(installer),
                    "--render-gdm-config",
                    str(config),
                    "radxa",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = config.read_text(encoding="utf-8")
            self.assertIn("# managed fixture", rendered)
            self.assertIn("# existing owner setting", rendered)
            self.assertIn("AutomaticLoginEnable=true", rendered)
            self.assertIn("AutomaticLogin=radxa", rendered)
            self.assertEqual(rendered.count("[daemon]"), 1)
            self.assertLess(
                rendered.index("AutomaticLogin=radxa"),
                rendered.index("[chooser]"),
            )


if __name__ == "__main__":
    unittest.main()
