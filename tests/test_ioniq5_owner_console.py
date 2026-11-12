"""Fixture-only tests for IONIQ5 serial and local-terminal recovery channels."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import textwrap
import unittest
from unittest import mock


REPOSITORY = Path(__file__).parents[1]
TOOL = REPOSITORY / "tools/uk_fw/ioniq5_owner_console.py"
SPEC = importlib.util.spec_from_file_location("ioniq5_owner_console", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load owner console tool")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OwnerConsoleFixtureTests(unittest.TestCase):
    """Exercise generated admission and launch policy without target access."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="owner-console-test-")
        self.root = Path(self.temporary.name).resolve()
        self.output = self.root / "overlay"
        self.manifest = MODULE.ioniq5_owner_console_generate(
            cdc_acm_id="234A:004B",
            output=self.output,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def source(self, relative: str) -> str:
        """Read one generated file as text."""
        return (self.output / relative).read_text()

    def test_exact_serial_and_keyboard_admission(self) -> None:
        """Rules select one CDC identity and USB keyboards without broad tty access."""
        serial_rule = self.source(MODULE._SERIAL_RULE)
        self.assertIn('KERNEL=="ttyACM[0-9]*"', serial_rule)
        self.assertIn('ATTRS{idVendor}=="234a"', serial_rule)
        self.assertIn('ATTRS{idProduct}=="004b"', serial_rule)
        self.assertIn('SYMLINK+="ioniq-owner-serial"', serial_rule)
        self.assertIn(
            'ENV{SYSTEMD_WANTS}+="ioniq-owner-serial-getty@%k.service"',
            serial_rule,
        )
        self.assertNotIn('KERNEL=="ttyACM*"', serial_rule)
        self.assertNotIn('ATTRS{idVendor}=="*"', serial_rule)

        keyboard_rule = self.source(MODULE._KEYBOARD_RULE)
        self.assertIn('SUBSYSTEM=="input"', keyboard_rule)
        self.assertIn('KERNEL=="event[0-9]*"', keyboard_rule)
        self.assertIn('SUBSYSTEMS=="usb"', keyboard_rule)
        self.assertIn('ENV{ID_INPUT_KEYBOARD}=="1"', keyboard_rule)
        self.assertIn(
            'ENV{SYSTEMD_WANTS}+="ioniq-owner-keyboard-terminal.service"',
            keyboard_rule,
        )

        serial_start = self.source(f"{MODULE._BASE}/bin/start-owner-serial")
        self.assertIn("    234a:004b) ;;", serial_start)
        self.assertIn('case "$identity" in', serial_start)
        self.assertIn("Owner serial ignored", serial_start)
        self.assertIn("--autologin root", serial_start)

    def test_services_are_independent_and_bounded(self) -> None:
        """Neither recovery service depends on networking or the other channel."""
        serial_unit = self.source(MODULE._SERIAL_UNIT)
        keyboard_unit = self.source(MODULE._KEYBOARD_UNIT)
        for unit in (serial_unit, keyboard_unit):
            self.assertIn("Restart=on-failure", unit)
            self.assertIn("StartLimitBurst=3", unit)
            self.assertNotIn("Requires=", unit)
            self.assertNotIn("network", unit.lower())
            self.assertNotIn("dropbear", unit.lower())
            self.assertNotIn("connman", unit.lower())
            self.assertNotIn("wpa_supplicant", unit.lower())
        self.assertIn("BindsTo=dev-%i.device", serial_unit)
        self.assertNotIn("BindsTo=", keyboard_unit)
        self.assertEqual(self.manifest["channels"]["serial"]["network_dependency"], False)
        self.assertEqual(
            self.manifest["channels"]["local_terminal"]["network_dependency"],
            False,
        )

    def test_absent_serial_hardware_keeps_local_terminal_and_no_serial_admission(self) -> None:
        """No guessed device identity is installed when the owner has no bridge."""
        output = self.root / "no-serial"
        manifest = MODULE.ioniq5_owner_console_generate(output=output)
        self.assertFalse(manifest["channels"]["serial"]["enabled"])
        self.assertIsNone(manifest["cdc_acm_id"])
        self.assertFalse((output / MODULE._SERIAL_RULE).exists())
        self.assertFalse((output / MODULE._SERIAL_UNIT).exists())
        self.assertIn("ID_INPUT_KEYBOARD", (output / MODULE._KEYBOARD_RULE).read_text())

    def test_keyboard_terminal_contract_and_exclusions(self) -> None:
        """The local channel launches the stock terminal without Radxa or gadget work."""
        script = self.source(f"{MODULE._BASE}/bin/start-owner-keyboard-terminal")
        self.assertIn("runtime_dir=/var/run/user/root", script)
        self.assertIn('export XDG_RUNTIME_DIR="$runtime_dir"', script)
        self.assertIn('terminal=/usr/bin/weston-terminal', script)
        self.assertIn('exec "$terminal" --shell=/bin/sh', script)
        self.assertIn("runtime path is a symlink", script)
        self.assertIn("unsafe runtime metadata", script)
        self.assertIn(f"IONIQ5_OWNER_CONSOLE_VERSION={MODULE._VERSION}", script)
        self.assertEqual(
            self.manifest["channels"]["local_terminal"]["program"],
            "/usr/bin/weston-terminal --shell=/bin/sh",
        )

        names = "\n".join(
            str(path.relative_to(self.output)).lower()
            for path in self.output.rglob("*")
        )
        for forbidden in (
            "cdc-ecm",
            "cdc_ecm",
            "usb-gadget",
            "usb_gadget",
            "ioniq-owner-ecm",
            "wpa_supplicant",
            "dropbear",
        ):
            self.assertNotIn(forbidden, names)
        self.assertIn("Radxa CDC-ECM transport", self.manifest["excluded"])

    def test_manifest_modes_ownership_and_determinism(self) -> None:
        """All files carry reproducible target metadata and stable bytes."""
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        for name, entry in self.manifest["files"].items():
            path = self.output / name
            self.assertTrue(path.is_file())
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                entry["sha256"],
            )
            self.assertEqual(path.stat().st_mode & 0o777, int(entry["mode"], 8))
            self.assertEqual((entry["uid"], entry["gid"]), (0, 0))
        self.assertEqual(self.manifest["symlinks"], {})

        second = self.root / "second"
        second_manifest = MODULE.ioniq5_owner_console_generate(
            cdc_acm_id="234A:004B",
            output=second,
        )
        self.assertEqual(second_manifest, self.manifest)
        self.assertEqual(
            (self.output.with_name(self.output.name + ".manifest.json")).read_bytes(),
            (second.with_name(second.name + ".manifest.json")).read_bytes(),
        )

    def test_cdc_id_is_explicit_and_exact(self) -> None:
        """Malformed, empty, partial, and surrounded IDs fail closed."""
        for value in (
            "",
            "234a",
            "234a:004",
            "234a:004bz",
            " 234a:004b",
            "234a:004b ",
            "0x234a:0x004b",
            b"234a:004b",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "cdc_acm_id"):
                    MODULE.ioniq5_owner_console_generate(
                        cdc_acm_id=value,
                        output=self.root / f"bad-{len(str(value))}",
                    )

    def test_output_paths_and_failures_are_fail_closed(self) -> None:
        """Existing files, symlinks, traversal, and partial publication are rejected."""
        foreign = self.output / "sentinel"
        foreign.write_text("keep")
        with self.assertRaisesRegex(ValueError, "already exists"):
            MODULE.ioniq5_owner_console_generate(
                cdc_acm_id="234a:004b",
                output=self.output,
            )
        self.assertEqual(foreign.read_text(), "keep")

        manifest_only = self.root / "manifest-only"
        manifest_path = manifest_only.with_name(manifest_only.name + ".manifest.json")
        manifest_path.write_text("keep")
        with self.assertRaisesRegex(ValueError, "already exists"):
            MODULE.ioniq5_owner_console_generate(
                cdc_acm_id="234a:004b",
                output=manifest_only,
            )
        self.assertEqual(manifest_path.read_text(), "keep")

        symlink_output = self.root / "symlink-output"
        symlink_output.symlink_to(self.root / "missing-target")
        with self.assertRaisesRegex(ValueError, "already exists"):
            MODULE.ioniq5_owner_console_generate(
                cdc_acm_id="234a:004b",
                output=symlink_output,
            )

        with self.assertRaisesRegex(ValueError, "unsafe output path"):
            MODULE.ioniq5_owner_console_generate(
                cdc_acm_id="234a:004b",
                output=self.root / "nested/../traversal",
            )

        failed = self.root / "failed"
        real_write = Path.write_bytes

        def fail_write(path: Path, value: bytes) -> int:
            if path.name == "start-owner-serial":
                raise OSError("simulated write failure")
            return real_write(path, value)

        with mock.patch.object(Path, "write_bytes", fail_write):
            with self.assertRaisesRegex(OSError, "simulated"):
                MODULE.ioniq5_owner_console_generate(
                    cdc_acm_id="234a:004b",
                    output=failed,
                )
        self.assertFalse(failed.exists())
        self.assertFalse(
            failed.with_name(failed.name + ".manifest.json").exists(),
        )
        self.assertEqual(list(self.root.glob(".ioniq-owner-console-*")), [])

        with mock.patch.object(Path, "rename", side_effect=OSError("rename failure")):
            with self.assertRaisesRegex(OSError, "rename"):
                MODULE.ioniq5_owner_console_generate(
                    cdc_acm_id="234a:004b",
                    output=failed,
                )
        self.assertFalse(failed.exists())
        self.assertFalse(
            failed.with_name(failed.name + ".manifest.json").exists(),
        )
        self.assertEqual(list(self.root.glob(".ioniq-owner-console-*")), [])

    def test_generated_shell_syntax(self) -> None:
        """Both generated launchers parse with the target-compatible shell."""
        for relative in (
            f"{MODULE._BASE}/bin/start-owner-serial",
            f"{MODULE._BASE}/bin/start-owner-keyboard-terminal",
        ):
            with self.subTest(relative=relative):
                if shutil.which("sh") is None:
                    self.skipTest("sh unavailable")
                result = subprocess.run(
                    ["sh", "-n", str(self.output / relative)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_serial_runtime_revalidates_exact_identity(self) -> None:
        """Matching ttyACM starts getty; a different product does nothing."""
        bindir = self.root / "stubbin"
        bindir.mkdir()
        agetty_log = self.root / "agetty.log"
        agetty = bindir / "agetty"
        agetty.write_text(
            "#!/bin/sh\nprintf '%s\\n' \"$*\" >\"$OWNER_AGETTY_LOG\"\n"
        )
        agetty.chmod(0o755)

        source = self.source(f"{MODULE._BASE}/bin/start-owner-serial")
        source = source.replace("sysroot=/sys", f"sysroot={self.root / 'sys'}")
        source = source.replace("/dev/$tty", str(self.root / "dev/$tty"))
        source = source.replace('[ ! -c "', '[ ! -f "')
        source = source.replace(
            "exec /sbin/agetty",
            f"exec {agetty}",
        )
        source = source.replace(
            "PATH=/usr/sbin:/usr/bin:/sbin:/bin",
            f"PATH={bindir}:/usr/sbin:/usr/bin:/sbin:/bin",
        )
        # The fixture is a regular placeholder rather than a host character device.
        script = self.root / "start-owner-serial"
        script.write_text(source)
        script.chmod(0o755)
        (self.root / "dev").mkdir()
        (self.root / "dev/ttyACM0").write_text("")

        usb = self.root / "sys/devices/pci0000:00/usb1/1-1"
        interface = usb / "1-1:1.0"
        class_tty = self.root / "sys/class/tty"
        interface.mkdir(parents=True)
        class_tty.mkdir(parents=True)
        device_link = class_tty / "ttyACM0"
        device_link.mkdir()
        (usb / "idVendor").write_text("234a\n")
        (usb / "idProduct").write_text("004b\n")
        os.symlink(interface, device_link / "device")

        environment = {"OWNER_AGETTY_LOG": str(agetty_log)}
        matched = subprocess.run(
            [str(script), "ttyACM0"],
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(matched.returncode, 0, matched.stderr)
        self.assertIn("serial tty=ttyACM0 id=234a:004b", matched.stdout)
        self.assertIn("--autologin root", agetty_log.read_text())
        self.assertIn("ttyACM0 vt100", agetty_log.read_text())

        agetty_log.unlink()
        unrelated_usb = self.root / "sys/devices/pci0000:00/usb1/1-2"
        unrelated_interface = unrelated_usb / "1-2:1.0"
        unrelated_interface.mkdir(parents=True)
        unrelated_device = class_tty / "ttyACM1"
        unrelated_device.mkdir()
        (unrelated_usb / "idVendor").write_text("234a\n")
        (unrelated_usb / "idProduct").write_text("ffff\n")
        os.symlink(unrelated_interface, unrelated_device / "device")
        (self.root / "dev/ttyACM1").write_text("")
        unrelated = subprocess.run(
            [str(script), "ttyACM1"],
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(unrelated.returncode, 0, unrelated.stderr)
        self.assertIn("identity is '234a:ffff'", unrelated.stdout)
        self.assertFalse(agetty_log.exists())

    def test_keyboard_runtime_sets_weston_environment(self) -> None:
        """The keyboard launcher owns only its runtime directory and shell entry."""
        terminal = self.root / "weston-terminal"
        terminal_log = self.root / "terminal.log"
        terminal.write_text(
            textwrap.dedent(
                """\
                #!/bin/sh
                {
                    printf 'XDG_RUNTIME_DIR=%s\\n' "$XDG_RUNTIME_DIR"
                    printf 'ARGS=%s\\n' "$*"
                } >"$OWNER_TERMINAL_LOG"
                """
            )
        )
        terminal.chmod(0o755)

        source = self.source(f"{MODULE._BASE}/bin/start-owner-keyboard-terminal")
        runtime = self.root / "runtime"
        runtime.mkdir(mode=0o700)
        source = source.replace(
            "runtime_dir=/var/run/user/root",
            f"runtime_dir={runtime}",
        )
        source = source.replace(
            "terminal=/usr/bin/weston-terminal",
            f"terminal={terminal}",
        )
        # The host stat differs from the target's coreutils call.
        source = source.replace(
            "stat -c '%u:%g:%a' \"$runtime_dir\"",
            "printf '0:0:700\\n'",
        )
        script = self.root / "start-owner-keyboard-terminal"
        script.write_text(source)
        script.chmod(0o755)

        result = subprocess.run(
            [str(script)],
            text=True,
            capture_output=True,
            env={"OWNER_TERMINAL_LOG": str(terminal_log)},
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("IONIQ5_OWNER_CONSOLE_VERSION=1.1.0", result.stdout)
        terminal_output = terminal_log.read_text()
        self.assertIn(f"XDG_RUNTIME_DIR={runtime}", terminal_output)
        self.assertIn("ARGS=--shell=/bin/sh", terminal_output)

    def test_cli_requires_explicit_device_id(self) -> None:
        """The command line has no guessed VID:PID default."""
        output = self.root / "cli"
        with mock.patch("builtins.print"):
            self.assertEqual(
                MODULE.ioniq5_owner_console_main(
                    [
                        "--cdc-acm-id",
                        "234A:004B",
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
        manifest = json.loads(
            output.with_name(output.name + ".manifest.json").read_text()
        )
        self.assertEqual(manifest["cdc_acm_id"], "234a:004b")
        self.assertEqual(MODULE.ioniq5_owner_console_main(
            ["--output", str(self.root / "missing-id")]), 0)
        self.assertFalse((self.root / "missing-id" / MODULE._SERIAL_RULE).exists())


class RetainedTargetEvidenceTests(unittest.TestCase):
    """Check the recovered target's console prerequisites without executing them."""

    def test_stock_console_and_serial_prerequisites_exist(self) -> None:
        """Weston terminal supports shell selection and CDC-ACM/getty are retained."""
        rootfs = REPOSITORY / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"
        terminal = rootfs / "usr/bin/weston-terminal"
        agetty = rootfs / "sbin/agetty"
        module = rootfs / "lib/modules/4.1.27-abl/kernel/drivers/usb/class/cdc-acm.ko"
        config = REPOSITORY / "work/eu-260128/kernel.config"
        if not terminal.is_file() or not agetty.is_file() or not module.is_file():
            self.skipTest("retained private target rootfs unavailable")
        terminal_bytes = terminal.read_bytes()
        self.assertIn(b"--shell=NAME", terminal_bytes)
        self.assertIn(b"ivi_application", terminal_bytes)
        self.assertTrue(agetty.is_file())
        self.assertTrue(module.is_file())
        if config.is_file():
            self.assertIn("CONFIG_USB_ACM=m", config.read_text())

    def test_generated_tree_contains_only_assigned_channels(self) -> None:
        """No shared aggregate target or unexpected unit is generated."""
        with tempfile.TemporaryDirectory(prefix="owner-console-tree-") as temporary:
            output = Path(temporary) / "overlay"
            MODULE.ioniq5_owner_console_generate(
                cdc_acm_id="234a:004b",
                output=output,
            )
            units = sorted(
                path.name
                for path in (output / "etc/systemd/system").iterdir()
                if path.is_file()
            )
            self.assertEqual(
                units,
                [
                    "ioniq-owner-keyboard-terminal.service",
                    "ioniq-owner-serial-getty@.service",
                ],
            )
            for path in output.rglob("*"):
                if path.is_file():
                    self.assertFalse(stat.S_ISLNK(path.lstat().st_mode))


if __name__ == "__main__":
    unittest.main()
