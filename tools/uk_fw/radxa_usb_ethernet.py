#!/usr/bin/env python3
"""Arm a Radxa Zero 3W CDC-ECM USB Ethernet gadget.

The controller owns one named configfs gadget and one static IPv4 address.
It does not provide DHCP, forwarding, NAT, or a Wi-Fi bridge. Mutating
operations verify the UDC, gadget identity, recorded state, and network
address ownership before changing or deleting anything.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from typing import Callable, Sequence


DEFAULT_SYSFS_ROOT = Path("/sys")
DEFAULT_CONFIGFS_ROOT = Path("/sys/kernel/config/usb_gadget")
DEFAULT_STATE_ROOT = Path("/run/ioniq5-owner-ecm")
GADGET_NAME = "ioniq_owner_ecm"
UDC_NAME = "fcc00000.usb"
USB_VENDOR_ID = "0x1d6b"
USB_PRODUCT_ID = "0x0104"
USB_IDENTITY = "1d6b:0104"
INTERFACE_NAME = "usb0"
LOCAL_ADDRESS = "10.42.0.2/24"
HOST_MAC = "02:49:54:35:00:01"
DEVICE_MAC = "02:49:54:35:00:02"
STATE_SCHEMA = "ioniq-radxa-owner-ecm/v1"
TOOL_VERSION = "1.0.0"
STATUS_SCHEMA = "ioniq-radxa-owner-ecm-status/v1"
STATE_LIMIT = 16 * 1024
COMMAND_TIMEOUT_SECONDS = 30
INTERFACE_WAIT_ATTEMPTS = 50
INTERFACE_WAIT_SECONDS = 0.1


class RadxaUSBEthernetError(RuntimeError):
    """Base error for a refused or failed USB Ethernet operation."""


class RadxaUSBEthernetReconciliationRequired(RadxaUSBEthernetError):
    """Raised when live resources cannot be attributed safely."""


@dataclass(frozen=True)
class RadxaUSBEthernetConfig:
    """Injected filesystem roots and command boundary for one controller."""

    sysfs_root: Path = DEFAULT_SYSFS_ROOT
    configfs_root: Path = DEFAULT_CONFIGFS_ROOT
    state_root: Path = DEFAULT_STATE_ROOT


Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def radxa_usb_ethernet_config() -> dict[str, str | int]:
    """Return the fixed, reviewable gadget and network policy."""
    return {
        "tool_version": TOOL_VERSION,
        "gadget_name": GADGET_NAME,
        "udc": UDC_NAME,
        "usb_identity": USB_IDENTITY,
        "interface": INTERFACE_NAME,
        "address": LOCAL_ADDRESS,
        "host_mac": HOST_MAC,
        "device_mac": DEVICE_MAC,
    }


def _default_runner(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Execute one bounded networking command without a shell."""
    return subprocess.run(
        list(command),
        capture_output=True,
        check=False,
        text=True,
        timeout=COMMAND_TIMEOUT_SECONDS,
    )


def _read_bounded(path: Path, limit: int = STATE_LIMIT) -> bytes:
    """Read one bounded nonempty regular file without following its final link."""
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or not 0 < metadata.st_size <= limit:
            raise RadxaUSBEthernetError(f"unsafe or oversized file: {path}")
        value = stream.read(limit + 1)
    if len(value) > limit:
        raise RadxaUSBEthernetError(f"oversized file: {path}")
    return value


def _write_attribute(path: Path, value: str) -> None:
    """Write one exact configfs attribute without following a final symlink."""
    # Configfs uses line-oriented stores. The newline is required to invoke
    # the unbind handler when UDC is cleared to an empty value.
    encoded = (value + "\n").encode("ascii")
    descriptor = os.open(path, os.O_WRONLY | os.O_NOFOLLOW)
    try:
        position = 0
        while position < len(encoded):
            position += os.write(descriptor, encoded[position:])
    finally:
        os.close(descriptor)


def _safe_mac(value: str) -> bool:
    """Accept one fixed unicast, locally administered Ethernet address."""
    if re.fullmatch(r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", value) is None:
        return False
    first = int(value.split(":", 1)[0], 16)
    return not first & 1 and bool(first & 2)


class _Controller:
    """Internal owner of the configfs, state, and network transitions."""

    def __init__(self, config: RadxaUSBEthernetConfig, runner: Runner | None) -> None:
        self.config = config
        self.runner = runner or _default_runner
        self.gadget_path = config.configfs_root / GADGET_NAME
        self.state_path = config.state_root / "state.json"
        self.udc_sysfs_path = config.sysfs_root / "class/udc" / UDC_NAME
        self.current_state_digest: str | None = None
        self.address_added = False

    def _invoke(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        """Invoke the injected runner and normalize process failures."""
        try:
            return self.runner(tuple(command))
        except (OSError, subprocess.SubprocessError) as exc:
            raise RadxaUSBEthernetError(
                f"command could not run ({' '.join(command)})"
            ) from exc

    def _run(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        """Run and validate one exact command."""
        result = self._invoke(command)
        if result.returncode:
            detail = (result.stderr or result.stdout or "").strip()
            suffix = f": {detail}" if detail else ""
            raise RadxaUSBEthernetError(
                f"command failed ({' '.join(command)}){suffix}"
            )
        return result

    def _expected_state(self, phase: str) -> dict[str, object]:
        """Build the one state record accepted for the configured roots."""
        return {
            "schema": STATE_SCHEMA,
            "tool_version": TOOL_VERSION,
            "phase": phase,
            "gadget_name": GADGET_NAME,
            "gadget_path": str(self.gadget_path.resolve(strict=False)),
            "state_path": str(self.state_path.resolve(strict=False)),
            "udc": UDC_NAME,
            "usb_identity": USB_IDENTITY,
            "interface": INTERFACE_NAME,
            "address": LOCAL_ADDRESS,
            "host_mac": HOST_MAC,
            "device_mac": DEVICE_MAC,
        }

    def _read_state(self) -> tuple[dict[str, object], bytes] | None:
        """Read one regular state file, rejecting links and malformed JSON."""
        if not os.path.lexists(self.state_path):
            return None
        raw = _read_bounded(self.state_path)
        try:
            value = json.loads(raw)
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise RadxaUSBEthernetReconciliationRequired(
                "owner state is not valid JSON"
            ) from exc
        if not isinstance(value, dict):
            raise RadxaUSBEthernetReconciliationRequired(
                "owner state must be one JSON object"
            )
        return value, raw

    def _validate_state(
        self,
        value: dict[str, object],
    ) -> tuple[dict[str, object], bytes]:
        """Require exact state identity and reject any phase mutation."""
        phase = value.get("phase")
        if phase not in ("preparing", "armed") or value != self._expected_state(phase):
            raise RadxaUSBEthernetReconciliationRequired(
                "owner state identity or schema changed"
            )
        record = self._read_state()
        if record is None:
            raise RadxaUSBEthernetError("owner state disappeared")
        return record

    def _ensure_state_root(self) -> None:
        """Create only the private runtime state directory."""
        root = self.config.state_root
        if os.path.lexists(root):
            metadata = os.lstat(root)
            if not stat.S_ISDIR(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) & 0o077:
                raise RadxaUSBEthernetReconciliationRequired(
                    "owner state root is foreign or not private"
                )
            return
        root.parent.mkdir(parents=True, exist_ok=True)
        root.mkdir(mode=0o700)

    def _write_state(self, phase: str) -> None:
        """Atomically publish one bounded state record under the runtime root."""
        self._ensure_state_root()
        payload = (
            json.dumps(self._expected_state(phase), indent=2, sort_keys=True)
            + "\n"
        ).encode("ascii")
        temporary = self.config.state_root / ".state.json.new"
        if os.path.lexists(temporary):
            raise RadxaUSBEthernetReconciliationRequired(
                "temporary owner state already exists"
            )
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
        )
        try:
            os.write(descriptor, payload)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        try:
            os.replace(temporary, self.state_path)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
        self.current_state_digest = hashlib.sha256(payload).hexdigest()

    def _delete_owned_state(self) -> None:
        """Delete state only when its bytes are still the exact owned bytes."""
        if not os.path.lexists(self.state_path):
            return
        raw = _read_bounded(self.state_path)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != self.current_state_digest:
            raise RadxaUSBEthernetReconciliationRequired(
                "owner state changed before cleanup"
            )
        self.state_path.unlink()

    def _validate_roots(self) -> None:
        """Require real directories and the selected physical UDC."""
        configfs = self.config.configfs_root
        if not configfs.is_dir() or configfs.is_symlink():
            raise RadxaUSBEthernetError(
                f"configfs gadget root is unavailable: {configfs}"
            )
        if not self.udc_sysfs_path.exists():
            raise RadxaUSBEthernetError(f"selected UDC is unavailable: {UDC_NAME}")

    def _udc_collision(self) -> str | None:
        """Return the gadget currently bound to the selected UDC, if any."""
        for entry in sorted(self.config.configfs_root.iterdir(), key=lambda item: item.name):
            if entry.name == GADGET_NAME:
                continue
            attribute = entry / "UDC"
            if not os.path.lexists(attribute):
                continue
            try:
                value = _read_bounded(attribute, 4096).decode("ascii").strip()
            except (OSError, UnicodeError, RadxaUSBEthernetError) as exc:
                raise RadxaUSBEthernetReconciliationRequired(
                    f"cannot determine UDC ownership for {entry.name}"
                ) from exc
            if value == UDC_NAME:
                return entry.name
        return None

    def _address_collision(self) -> None:
        """Refuse a pre-existing usb0, address, or route before mutation."""
        addresses = self._run(("ip", "-4", "-o", "addr", "show"))
        for line in addresses.stdout.splitlines():
            fields = line.split()
            if len(fields) >= 2 and fields[1].rstrip(":") == INTERFACE_NAME:
                raise RadxaUSBEthernetReconciliationRequired(
                    "usb0 already has a non-owned IPv4 identity"
                )
            if LOCAL_ADDRESS in fields:
                raise RadxaUSBEthernetReconciliationRequired(
                    "the owner IPv4 address is already in use"
                )
        routes = self._run(
            ("ip", "-4", "route", "show", "10.42.0.0/24")
        )
        if routes.stdout.strip():
            raise RadxaUSBEthernetReconciliationRequired(
                "the owner IPv4 subnet already has a route"
            )
        interface = self._invoke(
            ("ip", "-o", "link", "show", "dev", INTERFACE_NAME)
        )
        if interface.returncode == 0:
            raise RadxaUSBEthernetReconciliationRequired(
                "usb0 already exists and is not owned by this controller"
            )
        if not _is_missing_interface(interface):
            detail = (interface.stderr or interface.stdout or "").strip()
            raise RadxaUSBEthernetError(
                f"cannot establish usb0 ownership: {detail}"
            )

    def _gadget_identity(self) -> dict[str, str]:
        """Read the exact private gadget identity used for persistence."""
        paths = {
            "idVendor": self.gadget_path / "idVendor",
            "idProduct": self.gadget_path / "idProduct",
            "bcdUSB": self.gadget_path / "bcdUSB",
            "bcdDevice": self.gadget_path / "bcdDevice",
            "manufacturer": self.gadget_path / "strings/0x409/manufacturer",
            "product": self.gadget_path / "strings/0x409/product",
            "serialnumber": self.gadget_path / "strings/0x409/serialnumber",
            "configuration": self.gadget_path
            / "configs/c.1/strings/0x409/configuration",
            "MaxPower": self.gadget_path / "configs/c.1/MaxPower",
            "host_addr": self.gadget_path / "functions/ecm.usb0/host_addr",
            "dev_addr": self.gadget_path / "functions/ecm.usb0/dev_addr",
        }
        if not self.gadget_path.is_dir() or self.gadget_path.is_symlink():
            raise RadxaUSBEthernetReconciliationRequired(
                "owned gadget path is absent or not a directory"
            )
        values = {}
        for name, path in paths.items():
            try:
                values[name] = _read_bounded(path, 4096).decode("ascii").strip()
            except (OSError, UnicodeError, RadxaUSBEthernetError) as exc:
                raise RadxaUSBEthernetReconciliationRequired(
                    f"gadget identity field is unavailable: {name}"
                ) from exc
        expected = {
            "idVendor": USB_VENDOR_ID,
            "idProduct": USB_PRODUCT_ID,
            "bcdUSB": "0x0200",
            "bcdDevice": "0x0100",
            "manufacturer": "Radxa",
            "product": "IONIQ5 Owner USB Ethernet",
            "serialnumber": "IONIQ5-OWNER-ECM",
            "configuration": "owner-ssh",
            "MaxPower": "250",
            "host_addr": HOST_MAC,
            "dev_addr": DEVICE_MAC,
        }
        if values != expected:
            raise RadxaUSBEthernetReconciliationRequired(
                "gadget identity changed from the owned state"
            )
        link = self.gadget_path / "configs/c.1/ecm.usb0"
        if not link.is_symlink() or os.readlink(link) != "../../functions/ecm.usb0":
            raise RadxaUSBEthernetReconciliationRequired(
                "gadget function link changed from the owned state"
            )
        values["UDC"] = _read_bounded(
            self.gadget_path / "UDC", 4096
        ).decode("ascii").strip()
        return values

    def _create_gadget(self) -> None:
        """Create the exact CDC-ECM configfs tree and bind the selected UDC."""
        self.gadget_path.mkdir(mode=0o755)
        attributes = {
            "idVendor": USB_VENDOR_ID,
            "idProduct": USB_PRODUCT_ID,
            "bcdUSB": "0x0200",
            "bcdDevice": "0x0100",
        }
        for name, value in attributes.items():
            _write_attribute(self.gadget_path / name, value)
        for directory in (
            self.gadget_path / "strings/0x409",
            self.gadget_path / "configs/c.1/strings/0x409",
            self.gadget_path / "functions/ecm.usb0",
        ):
            directory.mkdir(parents=True, exist_ok=False)
        string_values = {
            "strings/0x409/serialnumber": "IONIQ5-OWNER-ECM",
            "strings/0x409/manufacturer": "Radxa",
            "strings/0x409/product": "IONIQ5 Owner USB Ethernet",
            "configs/c.1/strings/0x409/configuration": "owner-ssh",
            "configs/c.1/MaxPower": "250",
            "functions/ecm.usb0/dev_addr": DEVICE_MAC,
            "functions/ecm.usb0/host_addr": HOST_MAC,
        }
        for name, value in string_values.items():
            _write_attribute(self.gadget_path / name, value)
        os.symlink(
            "../../functions/ecm.usb0",
            self.gadget_path / "configs/c.1/ecm.usb0",
        )
        _write_attribute(self.gadget_path / "UDC", UDC_NAME)

    def _wait_for_interface(self) -> None:
        """Wait briefly for the gadget's network interface to enumerate."""
        for _ in range(INTERFACE_WAIT_ATTEMPTS):
            result = self._invoke(("ip", "link", "show", "dev", INTERFACE_NAME))
            if result.returncode == 0:
                return
            if not _is_missing_interface(result):
                detail = (result.stderr or result.stdout or "").strip()
                raise RadxaUSBEthernetError(
                    f"cannot inspect {INTERFACE_NAME}: {detail}"
                )
            import time

            time.sleep(INTERFACE_WAIT_SECONDS)
        raise RadxaUSBEthernetError(f"USB interface did not appear: {INTERFACE_NAME}")

    def _configure_interface(self) -> None:
        """Apply only the fixed local MAC and static owner address."""
        self._wait_for_interface()
        self._run(
            ("ip", "link", "set", "dev", INTERFACE_NAME, "address", DEVICE_MAC)
        )
        self._run(("ip", "link", "set", "dev", INTERFACE_NAME, "up"))
        self._run(
            ("ip", "addr", "add", LOCAL_ADDRESS, "dev", INTERFACE_NAME)
        )
        self.address_added = True

    def _unbind(self) -> None:
        """Unbind only when the live gadget UDC is empty or still ours."""
        path = self.gadget_path / "UDC"
        if not os.path.lexists(path):
            return
        value = _read_bounded(path, 4096).decode("ascii").strip()
        if value not in ("", UDC_NAME):
            raise RadxaUSBEthernetReconciliationRequired(
                "owned gadget is bound to a different UDC"
            )
        if value:
            _write_attribute(path, "")

    def _remove_gadget_tree(self) -> None:
        """Remove only the exact configfs tree created by this controller."""
        link = self.gadget_path / "configs/c.1/ecm.usb0"
        if os.path.lexists(link):
            if not link.is_symlink() or os.readlink(link) != "../../functions/ecm.usb0":
                raise RadxaUSBEthernetReconciliationRequired(
                    "refusing to remove a changed gadget function link"
                )
            link.unlink()
        attribute_files = (
            "idVendor",
            "idProduct",
            "bcdUSB",
            "bcdDevice",
            "UDC",
            "strings/0x409/serialnumber",
            "strings/0x409/manufacturer",
            "strings/0x409/product",
            "configs/c.1/MaxPower",
            "configs/c.1/strings/0x409/configuration",
            "functions/ecm.usb0/dev_addr",
            "functions/ecm.usb0/host_addr",
        )
        for name in attribute_files:
            path = self.gadget_path / name
            if path.is_file() and not path.is_symlink():
                # Configfs removes these files with their parent directory.
                # Normal fixture filesystems require explicit removal.
                try:
                    path.unlink()
                except OSError:
                    pass
        for directory in (
            self.gadget_path / "configs/c.1/strings/0x409",
            self.gadget_path / "configs/c.1/strings",
            self.gadget_path / "configs/c.1",
            self.gadget_path / "configs",
            self.gadget_path / "functions/ecm.usb0",
            self.gadget_path / "functions",
            self.gadget_path / "strings/0x409",
            self.gadget_path / "strings",
            self.gadget_path,
        ):
            try:
                directory.rmdir()
            except FileNotFoundError:
                pass

    def _rollback(self) -> None:
        """Remove only state created by this arm attempt."""
        if self.address_added:
            try:
                self._run((
                    "ip", "addr", "del", LOCAL_ADDRESS, "dev", INTERFACE_NAME,
                ))
            except (OSError, subprocess.SubprocessError, RadxaUSBEthernetError):
                pass
        try:
            self._unbind()
        except (OSError, ValueError, RadxaUSBEthernetError):
            pass
        tree_removed = not os.path.lexists(self.gadget_path)
        if not tree_removed:
            try:
                self._remove_gadget_tree()
            except (OSError, ValueError, RadxaUSBEthernetError):
                pass
            tree_removed = not os.path.lexists(self.gadget_path)
        if tree_removed:
            try:
                self._delete_owned_state()
            except (OSError, ValueError, RadxaUSBEthernetError):
                pass

    def _validate_recorded_gadget(self) -> None:
        """Require the recorded state and live gadget to agree exactly."""
        record = self._read_state()
        if record is None:
            raise RadxaUSBEthernetReconciliationRequired("owner state is absent")
        value, _ = self._validate_state(record[0])
        if value["phase"] != "armed":
            raise RadxaUSBEthernetReconciliationRequired(
                "a previous arm is incomplete; teardown is required"
            )
        identity = self._gadget_identity()
        if identity["UDC"] != UDC_NAME:
            raise RadxaUSBEthernetReconciliationRequired(
                "owned gadget is not bound to the selected UDC"
            )
        if not self._network_address():
            raise RadxaUSBEthernetReconciliationRequired(
                "owned usb0 address is absent"
            )
        if self._interface_mac() != DEVICE_MAC:
            raise RadxaUSBEthernetReconciliationRequired(
                "owned usb0 hardware address changed"
            )

    def arm(self) -> dict[str, object]:
        """Create the ECM gadget or return the exact existing armed state."""
        if not _safe_mac(HOST_MAC) or not _safe_mac(DEVICE_MAC):
            raise RadxaUSBEthernetError("fixed MAC policy is invalid")
        self._validate_roots()
        record = self._read_state()
        if record is not None:
            value, raw = self._validate_state(record[0])
            self.current_state_digest = hashlib.sha256(raw).hexdigest()
            if value["phase"] == "armed":
                self._validate_recorded_gadget()
                return self._result("unchanged", value=False)
            raise RadxaUSBEthernetReconciliationRequired(
                "a previous arm is incomplete; teardown is required"
            )
        if os.path.lexists(self.gadget_path):
            raise RadxaUSBEthernetReconciliationRequired(
                "the selected gadget path is owned by another process"
            )
        occupied = self._udc_collision()
        if occupied:
            raise RadxaUSBEthernetReconciliationRequired(
                f"selected UDC is already bound by {occupied}"
            )
        self._address_collision()
        self._ensure_state_root()
        try:
            self._write_state("preparing")
            self._create_gadget()
            self._configure_interface()
            self._write_state("armed")
        except BaseException:
            self._rollback()
            raise
        return self._result("armed", value=True)

    def _network_address(self) -> bool:
        """Return whether usb0 still has the exact owned address."""
        result = self._invoke(tuple(("ip", "-4", "-o", "addr", "show")))
        if result.returncode:
            detail = (result.stderr or result.stdout or "").strip()
            raise RadxaUSBEthernetError(f"cannot inspect IPv4 addresses: {detail}")
        for line in result.stdout.splitlines():
            fields = line.split()
            if (len(fields) >= 2 and fields[1].rstrip(":") == INTERFACE_NAME
                    and LOCAL_ADDRESS in fields):
                return True
        return False

    def _interface_mac(self) -> str | None:
        """Return the observed usb0 MAC or None when the interface is absent."""
        result = self._invoke(
            ("ip", "-o", "link", "show", "dev", INTERFACE_NAME)
        )
        if result.returncode:
            if _is_missing_interface(result):
                return None
            detail = (result.stderr or result.stdout or "").strip()
            raise RadxaUSBEthernetError(f"cannot inspect {INTERFACE_NAME}: {detail}")
        fields = result.stdout.split()
        try:
            return fields[fields.index("link/ether") + 1].lower()
        except (ValueError, IndexError) as exc:
            raise RadxaUSBEthernetReconciliationRequired(
                "cannot verify the usb0 hardware address"
            ) from exc

    def _remove_owned_address(self) -> None:
        """Delete the fixed address only from the MAC-bound owned interface."""
        if not self._network_address():
            return
        observed_mac = self._interface_mac()
        if observed_mac != DEVICE_MAC:
            raise RadxaUSBEthernetReconciliationRequired(
                "usb0 identity changed before address cleanup"
            )
        self._run(("ip", "addr", "del", LOCAL_ADDRESS, "dev", INTERFACE_NAME))

    def teardown(self) -> dict[str, object]:
        """Unbind and remove only the exact recorded owned gadget identity."""
        record = self._read_state()
        if record is None:
            if os.path.lexists(self.gadget_path):
                raise RadxaUSBEthernetReconciliationRequired(
                    "refusing to remove a gadget without owner state"
                )
            occupied = self._udc_collision()
            if occupied:
                raise RadxaUSBEthernetReconciliationRequired(
                    f"refusing to remove foreign UDC owner {occupied}"
                )
            return self._result("not_armed", value=False)
        _, raw = self._validate_state(record[0])
        self.current_state_digest = hashlib.sha256(raw).hexdigest()
        if not os.path.lexists(self.gadget_path):
            occupied = self._udc_collision()
            if occupied:
                raise RadxaUSBEthernetReconciliationRequired(
                    f"refusing to remove foreign UDC owner {occupied}"
                )
            self._delete_owned_state()
            return self._result("cleaned_stale_state", value=True)
        identity = self._gadget_identity()
        if identity["UDC"] not in ("", UDC_NAME):
            raise RadxaUSBEthernetReconciliationRequired(
                "owned gadget is bound to a different UDC"
            )
        self._remove_owned_address()
        self._unbind()
        self._remove_gadget_tree()
        self._delete_owned_state()
        return self._result("torn_down", value=True)

    def status(self) -> dict[str, object]:
        """Report state and live configfs ownership without changing anything."""
        issues: list[str] = []
        try:
            record = self._read_state()
        except (OSError, RadxaUSBEthernetError) as exc:
            record = None
            issues.append(str(exc))
        state = "not_armed"
        recorded_phase = None
        if record is not None:
            try:
                value, _ = self._validate_state(record[0])
                recorded_phase = value["phase"]
                state = str(recorded_phase)
                if recorded_phase == "armed":
                    self._validate_recorded_gadget()
            except (OSError, ValueError, RadxaUSBEthernetError) as exc:
                state = "inconsistent"
                issues.append(str(exc))
        elif os.path.lexists(self.gadget_path):
            state = "foreign"
            issues.append("gadget exists without owner state")
        return {
            "schema": STATUS_SCHEMA,
            "tool_version": TOOL_VERSION,
            **radxa_usb_ethernet_config(),
            "state": state,
            "recorded_phase": recorded_phase,
            "gadget_present": os.path.lexists(self.gadget_path),
            "issues": issues,
        }

    def _result(self, action: str, *, value: bool) -> dict[str, object]:
        """Return a stable command result."""
        return {
            "schema": STATUS_SCHEMA,
            "tool_version": TOOL_VERSION,
            "action": action,
            "changed": value,
            **radxa_usb_ethernet_config(),
        }


def _is_missing_interface(result: subprocess.CompletedProcess[str]) -> bool:
    """Recognize the normal iproute2 response for an absent interface."""
    text = (result.stderr or result.stdout or "").lower()
    return "does not exist" in text or "cannot find device" in text


def radxa_usb_ethernet_arm(
    *,
    config: RadxaUSBEthernetConfig | None = None,
    runner: Runner | None = None,
) -> dict[str, object]:
    """Arm the fixed CDC-ECM gadget and static usb0 address."""
    return _Controller(config or RadxaUSBEthernetConfig(), runner).arm()


def radxa_usb_ethernet_status(
    *,
    config: RadxaUSBEthernetConfig | None = None,
    runner: Runner | None = None,
) -> dict[str, object]:
    """Return read-only live ownership and configfs status."""
    return _Controller(config or RadxaUSBEthernetConfig(), runner).status()


def radxa_usb_ethernet_teardown(
    *,
    config: RadxaUSBEthernetConfig | None = None,
    runner: Runner | None = None,
) -> dict[str, object]:
    """Remove only the exact recorded owner gadget and static address."""
    return _Controller(config or RadxaUSBEthernetConfig(), runner).teardown()


def _config_from_args(args: argparse.Namespace) -> RadxaUSBEthernetConfig:
    """Build the injected controller configuration from CLI arguments."""
    return RadxaUSBEthernetConfig(
        sysfs_root=args.sysfs_root,
        configfs_root=args.configfs_root,
        state_root=args.state_root,
    )


def radxa_usb_ethernet_main(argv: list[str] | None = None) -> int:
    """Run one arm, status, or teardown command and print JSON."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("arm", "status", "teardown"))
    parser.add_argument("--sysfs-root", type=Path, default=DEFAULT_SYSFS_ROOT)
    parser.add_argument("--configfs-root", type=Path, default=DEFAULT_CONFIGFS_ROOT)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    args = parser.parse_args(argv)
    config = _config_from_args(args)
    operation = {
        "arm": radxa_usb_ethernet_arm,
        "status": radxa_usb_ethernet_status,
        "teardown": radxa_usb_ethernet_teardown,
    }[args.command]
    try:
        result = operation(config=config)
    except (OSError, ValueError, RadxaUSBEthernetError) as exc:
        parser.exit(2, f"USB Ethernet operation rejected: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(radxa_usb_ethernet_main())
