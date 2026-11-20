"""Host discovery and package planning fixtures for macOS, Linux and WSL2."""

from dataclasses import replace
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/uk_fw"))
from vm_workbench import platform_config as host


class PortableHostTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name).resolve()
        self.tools = self.project / "tools with spaces"
        self.tools.mkdir()
        self.environment = {"PATH": str(self.tools)}

    def fake_tool(self, name, executable=True):
        tool = self.tools / name
        tool.write_text("#!/bin/sh\nexit 99\n")
        if executable:
            tool.chmod(0o700)
        return tool

    def discover(self, *, system="Linux", machine="x86_64", release="generic", extra=None):
        return host.platform_config_discover(
            self.project, system=system, machine=machine, release=release,
            environment={**self.environment, **(extra or {})},
        )

    def test_tools_and_headers_are_discovered_without_executing_them(self):
        names = ("qemu-system-x86_64", "qemu-img", "debugfs", "zig", "x86_64-linux-musl-gcc", "magick")
        tools = [self.fake_tool(name) for name in names]
        includes = self.project / "include"
        architecture = self.project / "arch include"
        for path, name in ((includes, "dbus.h"), (architecture, "dbus-arch-deps.h")):
            (path / "dbus").mkdir(parents=True)
            (path / "dbus" / name).touch()
        config = self.discover(extra={"GEN5W_DBUS_INC": str(includes),
                                      "GEN5W_DBUS_ARCH_INC": str(architecture)})
        self.assertEqual(
            (config.qemu, config.qemu_img, config.debugfs, config.zig, config.musl_cc, config.magick),
            tuple(tools),
        )
        self.assertEqual((config.dbus_inc, config.dbus_arch_inc), (includes, architecture))
        self.assertEqual(host.platform_config_missing(config, wifi_sim=True), ())
        self.assertEqual(config.state_dir, self.project / ".gen5w")
        self.assertEqual(config.cache_dir, config.state_dir / "cache")
        self.assertEqual(config.runtime_dir, config.state_dir / "runtime")
        self.assertFalse(config.state_dir.exists())

    def test_mac_homebrew_prefix_keg_and_arm64_alias(self):
        prefix = self.project / "brew"
        debugfs = prefix / "opt/e2fsprogs/sbin/debugfs"
        debugfs.parent.mkdir(parents=True)
        debugfs.touch(mode=0o700)
        # A PATH entry should have priority. First verify the keg-only fallback
        # in an isolated fixture that does not depend on this host's packages.
        with mock.patch.object(host.shutil, "which", return_value=None):
            config = self.discover(system="Darwin", machine="arm64",
                                   extra={"HOMEBREW_PREFIX": str(prefix)})
        self.assertEqual((config.family, config.architecture), ("macos", "aarch64"))
        self.assertEqual(config.debugfs, debugfs)

    def test_linux_wsl2_and_unsupported_hosts(self):
        self.assertEqual(self.discover().family, "linux")
        self.assertEqual(self.discover(release="6.6.87.2-microsoft-standard-WSL2",
                                       extra={"WSL_INTEROP": "/run/WSL/123_interop"}).family, "wsl2")
        self.assertEqual(self.discover(release="4.19.128-microsoft-standard").family, "wsl2")
        for params, message in (
            ({"system": "Windows"}, "Windows needs"),
            ({"system": "FreeBSD"}, "requires macOS"),
            ({"release": "4.4.0-19041-Microsoft"}, "requires a WSL2"),
            ({"machine": "riscv64"}, "x86-64 or ARM64"),
        ):
            with self.subTest(params=params), self.assertRaisesRegex(host.PlatformConfigError, message):
                self.discover(**params)

    def test_sanitizes_path_and_honors_explicit_tools(self):
        override = self.fake_tool("pinned-zig")
        unrelated = self.fake_tool("zig", executable=False)
        with mock.patch.object(host.shutil, "which", return_value=None) as which:
            found = self.discover(extra={"PATH": "relative:" + str(self.tools) + ":",
                                         "GEN5W_ZIG": str(override)})
        self.assertEqual(found.zig, override)
        self.assertTrue(all(call.kwargs["path"] == str(self.tools) for call in which.call_args_list))
        self.assertIsNone(self.discover(extra={"GEN5W_ZIG": str(unrelated)}).zig)
        with self.assertRaisesRegex(host.PlatformConfigError, "GEN5W_ZIG"):
            self.discover(extra={"GEN5W_ZIG": "relative/zig"})

    def test_keeps_venv_invocation_path(self):
        python = self.tools / "venv-python"
        python.symlink_to(sys.executable)
        with mock.patch.object(host.sys, "executable", str(python)):
            self.assertEqual(self.discover().python, python)

    def test_discovers_image_magick_six_and_prefers_seven(self):
        six = self.fake_tool("convert-im6.q16")
        self.assertEqual(self.discover().magick, six)
        seven = self.fake_tool("magick")
        self.assertEqual(self.discover().magick, seven)

    def test_state_override_requires_canonical_qemu_safe_path(self):
        valid = self.project / "state with spaces"
        link = self.project / "state link"
        link.symlink_to(valid)
        self.assertEqual(self.discover(extra={"GEN5W_STATE_DIR": str(valid)}).state_dir, valid)
        for value in (".", str(link), str(self.project / "state,bad"), str(self.project / "two\nlines")):
            with self.subTest(value=value), self.assertRaises(host.PlatformConfigError):
                self.discover(extra={"GEN5W_STATE_DIR": value})

    def test_packages_are_missing_only_deduplicated_and_platform_specific(self):
        need = replace(self.discover(), qemu=None, qemu_img=None, zig=None, debugfs=None,
                       dbus_inc=None, dbus_arch_inc=None, musl_cc=None, magick=None)
        self.assertEqual(host.platform_config_dependency_packages(need, "apt")[-4:],
                         ("qemu-system-x86", "qemu-utils", "e2fsprogs", "libdbus-1-dev"))
        self.assertEqual(host.platform_config_dependency_packages(need, "apt", wifi_sim=True)[-2:],
                         ("musl-tools", "imagemagick"))
        arm = replace(need, architecture="aarch64")
        self.assertNotIn("musl-tools", host.platform_config_dependency_packages(arm, "apt", wifi_sim=True))
        self.assertEqual(host.platform_config_dependency_packages(replace(need, family="macos"), "brew")[-3:],
                         ("qemu", "e2fsprogs", "dbus"))
        for invalid in ("brew", "unknown"):
            with self.assertRaisesRegex(host.PlatformConfigError, "Unsupported package manager"):
                host.platform_config_dependency_packages(need, invalid)
        self.assertIn("zig", host.platform_config_missing(need))
        with self.assertRaisesRegex(host.PlatformConfigError, "Missing Gen5W dependencies"):
            host.platform_config_require(need)


if __name__ == "__main__":
    unittest.main()
