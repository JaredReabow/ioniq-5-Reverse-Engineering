"""Offline tests for the vendor-userspace workspace builder."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

TOOL = Path(__file__).parents[1] / "tools/uk_fw/vendor_rootfs.py"
SPEC = importlib.util.spec_from_file_location("vendor_rootfs", TOOL)
VENDOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VENDOR)


def vendor_root(base: Path) -> Path:
    """Minimal stand-in for the recovered root: the files the builder checks for."""
    root = base / "mango-rootfs"
    (root / "app/bin").mkdir(parents=True)
    (root / "app/bin/AppLauncher").write_text("#!/bin/sh\n")
    (root / "usr/lib").mkdir(parents=True)
    (root / "usr/lib/libwayland-client.so.0").write_text("stub\n")
    (root / "etc").mkdir()
    (root / "etc/version").write_text("NE_E.EUR.S5W_L.001.001.260128\n")
    return root


class AssembleTests(unittest.TestCase):
    def test_requires_every_local_input(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = vendor_root(base)
            with self.assertRaises(VENDOR.VendorError):
                VENDOR.assemble(root, base / "absent", base / "navi", base, base / "tree")

    def test_assembles_app_trees_init_and_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = vendor_root(base)
            new_gui = base / "new_gui"
            (new_gui / "night").mkdir(parents=True)
            (new_gui / "night/theme.png").write_text("pixels\n")
            navi = base / "appnavi"
            (navi / "Bin").mkdir(parents=True)
            (navi / "Bin/AppNavi").write_text("#!/bin/sh\n")
            helpers = base / "helpers"
            helpers.mkdir()
            for name in VENDOR.HELPER_BINARIES:
                (helpers / name).write_bytes(b"\0")
            tree = base / "tree"

            layout = VENDOR.assemble(root, new_gui, navi, helpers, tree)

            self.assertEqual(layout["chain"], str(tree / "opt/vm/vendor-chain.sh"))
            self.assertTrue((tree / "init").is_file())
            self.assertTrue((tree / "app/bin/AppLauncher").is_file())
            self.assertTrue((tree / "system/new_gui/night/theme.png").is_file())
            self.assertTrue((tree / "navi/Bin/AppNavi").is_file())
            self.assertTrue((tree / "etc/version").is_file())
            self.assertEqual((tree / "tmp").stat().st_mode & 0o7777, 0o1777)
            for name in VENDOR.HELPER_BINARIES:
                self.assertTrue((tree / "opt/vm" / name).is_file(), name)
            init = (tree / "init").read_text()
            self.assertIn("IONIQ_VM_VENDOR_READY", init)
            chain = (tree / "opt/vm/vendor-chain.sh").read_text()
            self.assertIn("interpose-probe", chain)
            self.assertIn("VENDOR_CHAIN_END", chain)

    def test_refuses_a_root_without_the_launcher(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = vendor_root(base)
            (root / "app/bin/AppLauncher").unlink()
            with self.assertRaises(VENDOR.VendorError):
                VENDOR.assemble(root, base / "n", base / "a", base, base / "tree")

    def test_refuses_a_root_without_the_vendor_wayland_client(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = vendor_root(base)
            (root / "usr/lib/libwayland-client.so.0").unlink()
            with self.assertRaises(VENDOR.VendorError):
                VENDOR.assemble(root, base / "n", base / "a", base, base / "tree")


class RunForwardingTests(unittest.TestCase):
    """vendor_rootfs run must forward the inspection flags to the boot harness."""

    def test_display_and_interactive_are_forwarded(self):
        calls = {}

        def fake_run(*args, **kwargs):
            calls["args"] = args
            return 0

        with mock.patch.object(VENDOR.vm_boot, "run", side_effect=fake_run), \
                mock.patch.object(VENDOR, "set_software_gl", return_value={}):
            code = VENDOR.main(["run", "--display", "vnc", "--interactive",
                                "--workspace", str(VENDOR.PROJECT / "work/vm/example")])
        self.assertEqual(code, 0)
        args = calls["args"]
        self.assertIn("vnc", args)
        self.assertIn(True, args)


class HelperListTests(unittest.TestCase):
    def test_every_declared_helper_is_built_by_name(self):
        self.assertEqual(VENDOR.HELPER_BINARIES,
                         ("navi-bg-0x0.so", "launcher-appnavi-navibg.so",
                          "interpose-probe", "guest-client-probe"))

    def test_refreshed_files_cover_every_helper(self):
        for name in VENDOR.HELPER_BINARIES:
            self.assertIn(f"opt/vm/{name}", VENDOR.REFRESHED, name)

    def test_every_declared_source_exists(self):
        for name, source_name in VENDOR.HELPER_BUILDS + VENDOR.HELPER_PROGRAMS:
            self.assertTrue((VENDOR.HELPERS / source_name).is_file(), source_name)
            self.assertTrue(name)


class HelperBuildTests(unittest.TestCase):
    def test_missing_toolchain_is_reported_with_the_remedy(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(VENDOR.shutil, "which", return_value=None), \
                    mock.patch.dict(sys.modules, {"ziglang": None}):
                with self.assertRaisesRegex(VENDOR.VendorError, "zig"):
                    VENDOR.build_helpers(Path(directory), Path(directory))


if __name__ == "__main__":
    unittest.main()
