"""Exercise launcher plans and setup against local fixtures and fake commands."""

from contextlib import redirect_stdout
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/uk_fw"))
from vm_workbench import bootstrap as setup


class BootstrapTests(unittest.TestCase):
    def make_plan(self, root, family="macos", manager=None, packages=(), **options):
        root = Path(root)
        return setup.bootstrap_plan(
            family=family, state_dir=root / "local state", assets=root / "imported firmware",
            manager=manager, packages=packages, sudo="/usr/bin/sudo", python="/opt/python3", **options,
        )

    def test_manager_detection_and_ordered_install_plan(self):
        for family, command, name in (("macos", "brew", "brew"), ("linux", "apt-get", "apt"),
                                      ("linux", "dnf", "dnf"), ("linux", "pacman", "pacman"),
                                      ("wsl2", "apt-get", "apt")):
            with self.subTest(family=family, manager=name):
                manager = setup.bootstrap_package_manager(
                    family, which=lambda candidate: f"/path/{command}" if candidate == command else None,
                )
                with tempfile.TemporaryDirectory() as directory:
                    plan = self.make_plan(directory, family, manager, ("qemu-x86",))
                    package_step = next(step for step in plan.steps if step.key == "packages")
                    self.assertEqual(manager, (name, f"/path/{command}"))
                    self.assertEqual(package_step.argv[-1], "qemu-x86")
                    self.assertTrue(package_step.confirm)
                    self.assertEqual(package_step.elevated, name != "brew")
                    self.assertEqual(plan.steps[0].key, "update" if name == "apt" else "packages")
                    self.assertFalse(plan.state_dir.exists())

    def test_unsupported_host_and_missing_package_manager(self):
        with self.assertRaisesRegex(setup.BootstrapError, "WSL2"):
            setup.bootstrap_package_manager("windows", which=lambda name: "/path/" + name)
        self.assertIsNone(setup.bootstrap_package_manager("linux", which=lambda name: None))
        with self.assertRaisesRegex(setup.BootstrapError, "No supported package manager"):
            self.make_plan("/unused", "linux", packages=("qemu",))
        with self.assertRaisesRegex(setup.BootstrapError, "Windows hosts file"):
            self.make_plan("/unused", "wsl2", configure_hostname=True)

    def test_alias_admission_and_port_fallback(self):
        for body, expected in (
            (b"127.0.0.1 localhost # gen5w.local\n", "missing"),
            (b"127.0.0.1 localhost Gen5W.LOCAL.\n", "loopback"),
            (b"127.0.0.1 gen5w.local\n::1 gen5w.local\n", "loopback"),
            (b"::1 gen5w.local\n", "loopback"),
            (b"192.0.2.5 gen5w.local\n", "conflict"),
            (b"127.0.0.1 othergen5w.local\n", "missing"),
        ):
            self.assertEqual(setup.bootstrap_hosts_mapping(body), expected)
        self.assertEqual(setup.bootstrap_address(80, True, available=lambda _: True), (80, "gen5w.local", None))
        port, host, note = setup.bootstrap_address(80, False, available=lambda _: True)
        self.assertEqual((port, host), (8765, None))
        self.assertIn("numeric", note)
        port, host, note = setup.bootstrap_address(80, True, available=lambda candidate: candidate == 8765)
        self.assertEqual((port, host), (8765, "gen5w.local"))
        self.assertIn("Port 80", note)
        self.assertEqual(setup.bootstrap_address(8765, False, available=lambda _: False)[:2], (0, None))
        self.assertEqual(setup.bootstrap_address(80, True, fallback_port=8767,
                                                 available=lambda candidate: candidate == 8767)[:2],
                         (8767, "gen5w.local"))
        for forbidden in (True, 0, -1, 65536):
            with self.assertRaises(setup.BootstrapError):
                setup.bootstrap_address(forbidden, True)

    def test_alias_requires_ipv4_but_allows_additional_ipv6_loopback(self):
        for addresses, expected in ((["127.0.0.1", "::1"], True), (["::1"], False),
                                    (["127.0.0.1", "192.0.2.5"], False), ([], False)):
            resolve = lambda *args, **kwargs: [(None, None, None, None, (ip, 0)) for ip in addresses]
            self.assertEqual(setup._verify_alias(resolve), expected)

    def test_explicit_yes_builds_noninteractive_packages_without_reading_stdin(self):
        for name, tool, flag in (("apt", "apt-get", "-y"), ("dnf", "dnf", "-y"),
                                 ("pacman", "pacman", "--noconfirm")):
            with self.subTest(manager=name), tempfile.TemporaryDirectory() as directory:
                plan = self.make_plan(directory, "wsl2", (name, f"/usr/bin/{tool}"),
                                      ("qemu",), assume_yes=True)
                packages = next(step for step in plan.steps if step.key == "packages")
                self.assertEqual(packages.argv[:2], ("/usr/bin/sudo", "-n"))
                self.assertIn(flag, packages.argv)
                ask = mock.Mock(side_effect=AssertionError("stdin must not be read"))
                runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0))
                with redirect_stdout(io.StringIO()):
                    setup.bootstrap_apply(plan, config=SimpleNamespace(family="wsl2"),
                                          runner=runner, assume_yes=True, ask=ask, open_browser=False)
                ask.assert_not_called()
                self.assertTrue(runner.called)

    def test_decline_install_prints_plan_without_mutation(self):
        with tempfile.TemporaryDirectory() as folder, redirect_stdout(io.StringIO()) as terminal:
            plan = self.make_plan(folder, "linux", ("apt", "/usr/bin/apt-get"), ("qemu-system-x86",))
            runner = mock.Mock()
            with self.assertRaisesRegex(setup.BootstrapError, "declined"):
                setup.bootstrap_apply(plan, config=SimpleNamespace(family="linux"), ask=lambda _: False,
                                      runner=runner)
            runner.assert_not_called()
            self.assertFalse(plan.state_dir.exists())
        self.assertIn("sudo /usr/bin/apt-get update", terminal.getvalue())

    def test_first_package_failure_stops_and_logs_elapsed_and_exit(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()) as terminal:
            plan = self.make_plan(directory, "linux", ("apt", "/usr/bin/apt-get"), ("qemu-system-x86",))
            runner = mock.Mock(return_value=subprocess.CompletedProcess([], 7))
            with self.assertRaisesRegex(setup.BootstrapError, "exit 7"):
                setup.bootstrap_apply(plan, config=SimpleNamespace(family="linux"), ask=lambda _: True,
                                      runner=runner)
            runner.assert_called_once()
            self.assertEqual(runner.call_args.args[0], ("/usr/bin/sudo", "/usr/bin/apt-get", "update"))
            self.assertEqual((plan.state_dir / "logs").stat().st_mode & 0o777, 0o700)
            log, = (plan.state_dir / "logs").glob("bootstrap-*.log")
            self.assertIn("Exit 7 in ", log.read_text())
            self.assertEqual(log.stat().st_mode & 0o777, 0o600)
        self.assertIn("[--------------------]", terminal.getvalue())

    def test_launch_uses_separate_arguments_and_foreground_command(self):
        with tempfile.TemporaryDirectory(prefix="repo spaces ") as directory, redirect_stdout(io.StringIO()) as terminal:
            plan = self.make_plan(directory)
            runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0))
            with (mock.patch.object(setup, "_configured_alias", return_value=True),
                  mock.patch.object(setup, "bootstrap_address", return_value=(8765, "gen5w.local", None))):
                setup.bootstrap_apply(plan, config=SimpleNamespace(family="macos"), runner=runner)
            create, serve = runner.call_args_list
            self.assertEqual(create.args[0][-1], str(plan.state_dir / ".venv"))
            self.assertIn("--without-pip", create.args[0])
            self.assertIn(str(plan.assets), serve.args[0])
            self.assertEqual(serve.args[0][-5:], ("--port", "8765", "--host-name", "gen5w.local", "--open-browser"))
            self.assertEqual(serve.kwargs["env"]["GEN5W_STATE_DIR"], str(plan.state_dir))
            self.assertFalse(serve.kwargs["check"])
        self.assertIn("100% ", terminal.getvalue())
        self.assertIn("Ctrl+C stops", terminal.getvalue())

    def test_opt_in_hostname_checks_conflict_and_confirmation(self):
        for mapping, consent, append_expected in (
            ("conflict", True, False), ("loopback", True, False),
            ("missing", False, False), ("missing", True, True),
        ):
            with self.subTest(mapping=mapping, consent=consent), tempfile.TemporaryDirectory() as directory:
                plan = self.make_plan(directory, configure_hostname=True)
                runner = mock.Mock(return_value=subprocess.CompletedProcess([], 0))
                with (redirect_stdout(io.StringIO()),
                      mock.patch.object(setup, "_hosts_mapping", return_value=mapping),
                      mock.patch.object(setup, "_verify_alias", return_value=False),
                      mock.patch.object(setup, "bootstrap_address", return_value=(8765, None, None))):
                    setup.bootstrap_apply(plan, config=SimpleNamespace(family="macos"), runner=runner,
                                          ask=lambda _: consent, open_browser=False)
                host_calls = [call for call in runner.call_args_list if "/usr/bin/tee" in call.args[0]]
                self.assertEqual(len(host_calls), int(append_expected))
                if append_expected:
                    self.assertEqual(host_calls[0].args[0], ("/usr/bin/sudo", "/usr/bin/tee", "-a", "/etc/hosts"))
                    self.assertEqual(host_calls[0].kwargs["input"], b"\n" + setup._HOSTS_LINE)
                self.assertNotIn("--open-browser", runner.call_args.args[0])

    def test_pinned_archive_validation_and_staging_cleanup(self):
        class Download(io.BytesIO):
            def geturl(self):
                return "https://example.invalid/zig.tar.xz"

        def archive(items):
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode="w:xz") as tar:
                for name, data, mode in items:
                    info = tarfile.TarInfo(name)
                    info.size, info.mode = len(data), mode
                    tar.addfile(info, io.BytesIO(data))
            return stream.getvalue()

        files = (("zig-test/zig", b"executable fixture", 0o755), ("zig-test/lib/header", b"stdlib", 0o644))
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            root = Path(directory)
            target = root / "zig-test"
            for records, digest_match, pattern in (
                (files, False, "SHA-256"),
                (files + (("zig-test/../escape", b"reject", 0o644),), True, "Unexpected path"),
                (files, True, None),
            ):
                payload = archive(records)
                digest = hashlib.sha256(payload).hexdigest() if digest_match else "0" * 64
                args = ("https://example.invalid/zig.tar.xz", target, len(payload), digest)
                if pattern:
                    with self.assertRaisesRegex(setup.BootstrapError, pattern):
                        setup._download_zig(args, download=lambda *_, **__: Download(payload))
                    self.assertFalse(list(root.iterdir()))
                else:
                    tool = setup._download_zig(args, download=lambda *_, **__: Download(payload))
                    self.assertEqual(tool.read_bytes(), b"executable fixture")
                    self.assertEqual(tool.stat().st_mode & 0o111, 0o111)
                    self.assertEqual(list(root.iterdir()), [target])
                    self.assertEqual(setup._cached_zig(args), tool)
                    self.assertIsNone(setup._cached_zig((*args[:3], "0" * 64)))

    def test_visible_launcher_contracts_and_wsl_reboot_instructions(self):
        launchers = ROOT / "launchers"
        sh = (launchers / "start.sh").read_text()
        mac = (launchers / "Gen5W.command").read_text()
        desktop = (launchers / "Gen5W.desktop").read_text()
        cmd = (launchers / "Gen5W.cmd").read_text()
        windows = (launchers / "Gen5W.ps1").read_text()
        self.assertIn('exec /bin/sh "$launcher_dir/start.sh" --terminal "$@"', mac)
        self.assertIn("Terminal=true", desktop)
        self.assertIn("x-terminal-emulator -e", sh)
        self.assertIn('-m vm_workbench.bootstrap "$@"', sh)
        self.assertIn('"%~dp0Gen5W.ps1"', cmd)
        self.assertIn("RemoteSigned", cmd)
        self.assertIn("--no-launch", windows)
        self.assertIn("Restart Windows if requested", windows)
        self.assertIn("reopen Gen5W.cmd", windows)
        self.assertIn("'--cd', $root, '--exec'", windows)
        self.assertIn("GEN5W_WINDOWS_BROWSER=$linuxBrowser", windows)
        self.assertIn("/usr/bin/wslpath", windows)
        self.assertIn("& $wsl @Arguments", windows)
        self.assertIn("[Net.IPAddress]::Loopback", windows)
        self.assertIn("'--windows-fallback-port', [string]$fallback", windows)
        self.assertNotIn("Invoke-Expression", windows)
        self.assertNotIn("ExecutionPolicy Bypass", cmd)
        self.assertNotIn("0.0.0.0", windows + sh)
        self.assertNotIn("wsl.exe --shutdown", windows)

    @unittest.skipUnless(shutil.which("powershell.exe") or shutil.which("pwsh"),
                         "Native PowerShell runtime is required for executable Windows launcher checks")
    def test_native_powershell_launcher_decisions(self):
        powershell = shutil.which("powershell.exe") or shutil.which("pwsh")
        script = str(ROOT / "tests/test_gen5w_windows_launcher.ps1")
        if os.name != "nt" and Path(powershell).name.lower() == "powershell.exe":
            converter = shutil.which("wslpath")
            if converter is None:
                self.skipTest("Windows PowerShell interop needs wslpath for the fixture script")
            script = subprocess.check_output((converter, "-w", script), text=True, timeout=10).strip()
            self.assertTrue(script, "wslpath returned an empty Windows fixture path")
        result = subprocess.run(
            (powershell, "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
             script),
            cwd=ROOT, text=True, capture_output=True, timeout=45, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("GEN5W_WINDOWS_LAUNCHER_TESTS_PASS", result.stdout)

    @unittest.skipIf(os.name == "nt", "The Windows launcher runs the shell bootstrap inside WSL2")
    def test_shell_handoff_preserves_checkout_and_asset_paths(self):
        with tempfile.TemporaryDirectory(prefix="checkout with spaces ") as directory:
            root = Path(directory)
            scripts, binaries = root / "launchers", root / "fixture bin"
            scripts.mkdir()
            binaries.mkdir()
            shutil.copyfile(ROOT / "launchers/start.sh", scripts / "start.sh")
            for name, body in (
                ("uname", "printf '%s\\n' Linux"),
                ("python3", "test \"$1\" != -I || exit 1\nexit 97"),
                ("python3.13", "test \"$1\" != -I || exit 0\n"
                               "printf '%s\\n' \"$PWD\" \"$PYTHONPATH\" \"$@\""),
            ):
                executable = binaries / name
                executable.write_text("#!/bin/sh\n" + body + "\n")
                executable.chmod(0o755)
            assets = root / "asset path & spaces"
            result = subprocess.run(
                ("/bin/sh", str(scripts / "start.sh"), "--terminal", "--assets", str(assets), "--plan"),
                cwd=ROOT, env={**os.environ, "PATH": f"{binaries}:/usr/bin:/bin"},
                text=True, capture_output=True, check=True,
            )
            root = root.resolve()
            self.assertEqual(result.stdout.splitlines(), [
                str(root), str(root / "tools/uk_fw"),
                "-s", "-B", "-m", "vm_workbench.bootstrap", "--assets", str(assets), "--plan",
            ])


if __name__ == "__main__":
    unittest.main()
