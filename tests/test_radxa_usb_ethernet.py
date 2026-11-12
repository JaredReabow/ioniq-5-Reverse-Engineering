"""Fixture-only tests for the Radxa CDC-ECM USB Ethernet controller."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PROJECT = Path(__file__).parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools.uk_fw import radxa_usb_ethernet as module


class RadxaUSBEthernetFixture(unittest.TestCase):
    """Exercise ownership and rollback against temporary fake filesystems."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="owner-ecm-test-")
        self.root = Path(self.temporary.name).resolve()
        self.sysfs = self.root / "sys"
        self.configfs = self.sysfs / "kernel/config/usb_gadget"
        self.state_root = self.root / "run/ioniq5-owner-ecm"
        self.configfs.mkdir(parents=True)
        (self.sysfs / "class/udc" / module.UDC_NAME).mkdir(parents=True)
        self.config = module.RadxaUSBEthernetConfig(
            sysfs_root=self.sysfs,
            configfs_root=self.configfs,
            state_root=self.state_root,
        )
        self.commands: list[tuple[str, ...]] = []
        self.network_address = False
        self.interface_present = False
        self.address_collision = False
        self.route_collision = False
        self.fail_command: tuple[str, ...] | None = None
        self.attribute_patch = mock.patch.object(
            module,
            "_write_attribute",
            side_effect=self.write_attribute,
        )
        self.attribute_patch.start()

    def tearDown(self) -> None:
        self.attribute_patch.stop()
        self.temporary.cleanup()

    def write_attribute(self, path: Path, value: str) -> None:
        """Emulate configfs auto-created attributes in a normal temp file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value + "\n", encoding="ascii")
        if path.name == "UDC":
            self.interface_present = bool(value)

    def add_gadget(self, name: str, udc: str = "") -> Path:
        """Create one minimal foreign gadget that the owner must not claim."""
        path = self.configfs / name
        path.mkdir()
        (path / "UDC").write_text(udc, encoding="ascii")
        return path

    def runner(self, command: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        """Emulate bounded iproute2 calls without changing the host network."""
        self.commands.append(tuple(command))
        if self.fail_command and command[:len(self.fail_command)] == self.fail_command:
            return subprocess.CompletedProcess(command, 1, "", "injected failure")
        if command == ("ip", "-4", "-o", "addr", "show"):
            lines = []
            if self.address_collision:
                lines.append(
                    f"2: {module.INTERFACE_NAME} inet {module.LOCAL_ADDRESS} "
                    "scope global usb0"
                )
            elif self.network_address:
                lines.append(
                    f"5: {module.INTERFACE_NAME} inet {module.LOCAL_ADDRESS} "
                    "scope global usb0"
                )
            return subprocess.CompletedProcess(command, 0, "\n".join(lines), "")
        if command == ("ip", "-4", "route", "show", "10.42.0.0/24"):
            stdout = "10.42.0.0/24 dev foreign\n" if self.route_collision else ""
            return subprocess.CompletedProcess(command, 0, stdout, "")
        if command == ("ip", "link", "show", "dev", module.INTERFACE_NAME):
            if not self.interface_present:
                return subprocess.CompletedProcess(
                    command, 1, "", "Device does not exist."
                )
            return subprocess.CompletedProcess(
                command,
                0,
                f"5: {module.INTERFACE_NAME}: <BROADCAST> mtu 1500 "
                f"link/ether {module.DEVICE_MAC} brd ff:ff:ff:ff:ff:ff\n",
                "",
            )
        if command == ("ip", "-o", "link", "show", "dev", module.INTERFACE_NAME):
            if not self.interface_present:
                return subprocess.CompletedProcess(
                    command, 1, "", "Device does not exist."
                )
            return subprocess.CompletedProcess(
                command,
                0,
                f"5: {module.INTERFACE_NAME}: <BROADCAST> mtu 1500 "
                f"link/ether {module.DEVICE_MAC} brd ff:ff:ff:ff:ff:ff\n",
                "",
            )
        if command[:5] == (
            "ip", "addr", "add", module.LOCAL_ADDRESS, "dev",
        ):
            self.network_address = True
        elif command[:5] == (
            "ip", "addr", "del", module.LOCAL_ADDRESS, "dev",
        ):
            self.network_address = False
        return subprocess.CompletedProcess(command, 0, "", "")

    def arm(self) -> dict[str, object]:
        """Call the public arm API with the fixture boundary."""
        return module.radxa_usb_ethernet_arm(
            config=self.config,
            runner=self.runner,
        )

    def status(self) -> dict[str, object]:
        """Call the public status API with the fixture boundary."""
        return module.radxa_usb_ethernet_status(
            config=self.config,
            runner=self.runner,
        )

    def teardown(self) -> dict[str, object]:
        """Call the public teardown API with the fixture boundary."""
        return module.radxa_usb_ethernet_teardown(
            config=self.config,
            runner=self.runner,
        )

    def gadget_path(self) -> Path:
        """Return the fixed fixture gadget path."""
        return self.configfs / module.GADGET_NAME

    def state_path(self) -> Path:
        """Return the fixed fixture state path."""
        return self.state_root / "state.json"

    def test_arm_status_and_teardown_are_owner_scoped(self) -> None:
        arm = self.arm()
        self.assertEqual(arm["action"], "armed")
        self.assertTrue(self.gadget_path().is_dir())
        state = json.loads(self.state_path().read_text(encoding="ascii"))
        self.assertEqual(state["phase"], "armed")
        self.assertEqual(
            (self.gadget_path() / "idVendor").read_text(encoding="ascii").strip(),
            module.USB_VENDOR_ID,
        )
        self.assertEqual(
            (self.gadget_path() / "functions/ecm.usb0/dev_addr").read_text(
                encoding="ascii"
            ).strip(),
            module.DEVICE_MAC,
        )
        self.assertEqual(
            (self.gadget_path() / "UDC").read_text(encoding="ascii").strip(),
            module.UDC_NAME,
        )
        self.assertIn(
            ("ip", "addr", "add", module.LOCAL_ADDRESS, "dev", module.INTERFACE_NAME),
            self.commands,
        )

        status = self.status()
        self.assertEqual(status["state"], "armed")
        self.assertEqual(status["issues"], [])

        teardown = self.teardown()
        self.assertEqual(teardown["action"], "torn_down")
        self.assertFalse(self.gadget_path().exists())
        self.assertFalse(self.state_path().exists())
        self.assertFalse(self.network_address)
        self.assertIn(
            ("ip", "addr", "del", module.LOCAL_ADDRESS, "dev", module.INTERFACE_NAME),
            self.commands,
        )
        joined = "\n".join(" ".join(command) for command in self.commands)
        for forbidden in ("iptables", "nft", "dnsmasq", "hostapd", "wpa_supplicant"):
            self.assertNotIn(forbidden, joined)

    def test_arm_is_idempotent_only_for_exact_owned_state(self) -> None:
        first = self.arm()
        before = len(self.commands)
        second = self.arm()
        self.assertEqual(first["action"], "armed")
        self.assertEqual(second["action"], "unchanged")
        self.assertFalse(second["changed"])
        repeated = self.commands[before:]
        self.assertTrue(repeated)
        for command in repeated:
            self.assertNotIn("link set", " ".join(command))
            self.assertNotIn("addr add", " ".join(command))

    def test_occupied_udc_is_rejected_before_owner_mutation(self) -> None:
        self.add_gadget("foreign", module.UDC_NAME)
        with self.assertRaises(module.RadxaUSBEthernetReconciliationRequired):
            self.arm()
        self.assertFalse(self.gadget_path().exists())
        self.assertFalse(self.state_path().exists())
        self.assertEqual(self.commands, [])

    def test_foreign_owner_path_is_never_reused(self) -> None:
        foreign = self.gadget_path()
        foreign.mkdir()
        sentinel = foreign / "sentinel"
        sentinel.write_text("keep", encoding="ascii")
        with self.assertRaises(module.RadxaUSBEthernetReconciliationRequired):
            self.arm()
        self.assertEqual(sentinel.read_text(encoding="ascii"), "keep")
        self.assertFalse(self.state_path().exists())

    def test_address_and_route_collisions_are_rejected(self) -> None:
        for name in ("address_collision", "route_collision"):
            with self.subTest(name=name):
                if self.gadget_path().exists():
                    self.teardown()
                self.address_collision = name == "address_collision"
                self.route_collision = name == "route_collision"
                with self.assertRaises(module.RadxaUSBEthernetReconciliationRequired):
                    self.arm()
                self.assertFalse(self.gadget_path().exists())
                self.assertFalse(self.state_path().exists())

    def test_teardown_refuses_changed_gadget_identity(self) -> None:
        self.arm()
        product = self.gadget_path() / "idProduct"
        product.write_text("ffff", encoding="ascii")
        with self.assertRaises(module.RadxaUSBEthernetReconciliationRequired):
            self.teardown()
        self.assertTrue(self.gadget_path().exists())
        self.assertTrue(self.state_path().exists())
        self.assertTrue(self.network_address)
        self.assertNotIn(
            ("ip", "addr", "del", module.LOCAL_ADDRESS, "dev", module.INTERFACE_NAME),
            self.commands,
        )

    def test_partial_arm_failure_rolls_back_only_owned_state(self) -> None:
        self.fail_command = (
            "ip", "addr", "add", module.LOCAL_ADDRESS, "dev", module.INTERFACE_NAME,
        )
        with self.assertRaises(module.RadxaUSBEthernetError):
            self.arm()
        self.assertFalse(self.gadget_path().exists())
        self.assertFalse(self.state_path().exists())
        self.assertFalse(self.network_address)

    def test_teardown_refuses_foreign_state_and_leaves_gadget(self) -> None:
        foreign = self.add_gadget(module.GADGET_NAME, module.UDC_NAME)
        sentinel = foreign / "sentinel"
        sentinel.write_text("keep", encoding="ascii")
        self.state_root.mkdir(parents=True)
        self.state_root.chmod(0o700)
        self.state_path().write_text(
            json.dumps({"schema": "foreign", "phase": "armed"}),
            encoding="ascii",
        )
        original = self.state_path().read_bytes()
        with self.assertRaises(module.RadxaUSBEthernetReconciliationRequired):
            self.teardown()
        self.assertEqual(sentinel.read_text(encoding="ascii"), "keep")
        self.assertEqual(self.state_path().read_bytes(), original)
        self.assertEqual(self.commands, [])


class RadxaUSBEthernetStaticPolicyTests(unittest.TestCase):
    """Check public constants without touching a live device."""

    def test_fixed_policy_is_ecm_only_and_locally_administered(self) -> None:
        policy = module.radxa_usb_ethernet_config()
        self.assertEqual(policy["gadget_name"], "ioniq_owner_ecm")
        self.assertEqual(policy["udc"], "fcc00000.usb")
        self.assertEqual(policy["usb_identity"], "1d6b:0104")
        self.assertEqual(policy["interface"], "usb0")
        self.assertEqual(policy["address"], "10.42.0.2/24")
        self.assertTrue(module._safe_mac(module.HOST_MAC))
        self.assertTrue(module._safe_mac(module.DEVICE_MAC))


if __name__ == "__main__":
    unittest.main()
