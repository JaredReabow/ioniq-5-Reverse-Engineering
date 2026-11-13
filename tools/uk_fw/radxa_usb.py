#!/usr/bin/env python3
"""Inspect, arm, and tear down a Radxa USB mass-storage gadget.

The module owns the Linux side of the IONIQ USB serving chain:

    nbdkit -> nbd-client -> NBD block device -> configfs mass-storage -> UDC

It deliberately discovers the board's UDC and an unused NBD device. Raspberry
Pi-specific overlays, controller names, usernames, and fixed NBD paths are not
part of this adapter.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, dataclass, field
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import socket
import stat
import subprocess
import sys
import time
from typing import Callable, Mapping, Sequence


DEFAULT_SYSFS_ROOT = Path("/sys")
DEFAULT_DEV_ROOT = Path("/dev")
DEFAULT_CONFIGFS_ROOT = Path("/sys/kernel/config/usb_gadget")
DEFAULT_PROC_ROOT = Path("/proc")
DEFAULT_STATE_ROOT = Path("/run/ioniq-toctou")
DEFAULT_GADGET_NAME = "ioniq_toctou"
DEFAULT_NBD_HOST = "127.0.0.1"
DEFAULT_NBD_PORT = 10809
DEFAULT_PORT_SCAN_COUNT = 64
DEFAULT_FUSE_HELPER = Path("/usr/local/libexec/ioniq-nbdfuse-direct")
FUSE_HELPER_VERSION = "ioniq-nbdfuse-direct 1.14.2-ioniq-direct.1"
TOOL_VERSION = "1.3.2"
VALIDATION_CACHE_POLICY_VERSION = "1.2.1"
SERVE_PLAN_SCHEMA = "ioniq-radxa-usb-serve-plan/v1"
BUILDER_MANIFEST_SCHEMA = "ioniq5-custom-firmware/v1"
BUILDER_TOOL_NAME = "ioniq5_custom_firmware"
BUILDER_TOOL_VERSION = "1.0.2"
STATE_SCHEMA = "ioniq-radxa-usb-state/v5"
LEGACY_STATE_SCHEMA_V4 = "ioniq-radxa-usb-state/v4"
USB_VENDOR_ID = "0x0781"
USB_PRODUCT_ID = "0x5591"
USB_RELEASE = "0x0100"
USB_CONFIGURATION = "cfg1"
USB_MANUFACTURER = "Generic"
USB_PRODUCT = "USB DISK"
USB_SERIAL_PREFIX = "IT5"
USB_MAX_POWER_MA = "250"
COMMAND_TIMEOUT_SECONDS = 30
SERVER_START_TIMEOUT_SECONDS = 8.0
SERVER_POLL_SECONDS = 0.1
NBD_DETACH_TIMEOUT_SECONDS = 5.0
SUPERVISOR_POLL_SECONDS = 0.25
FUSE_READY_TIMEOUT_SECONDS = 8.0
FUSE_UNMOUNT_TIMEOUT_SECONDS = 5.0
PROCESS_IDENTITY_RETRY_SECONDS = 2.0
NBD_NAME_RE = re.compile(r"nbd([0-9]+)")
SAFE_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
BACKING_KINDS = frozenset(("nbd", "fuse-direct"))
_VALIDATION_CACHE = ContextVar("radxa_usb_validation_cache", default=None)
_CACHE_SCHEMA = "ioniq-radxa-prepared-content/v1"


class RadxaUSBError(RuntimeError):
    """Raised when the USB serving chain cannot be prepared safely."""


class RadxaUSBReconciliationRequired(RadxaUSBError):
    """Raised when live resources cannot be attributed safely."""


class RadxaUSBCancelled(RadxaUSBError):
    """Raised when a cooperative stop is requested before arming completes."""


class _RadxaUSBValidationCache:
    """Reuse hashes only while exact local file identities remain unchanged.

    This trusts the local owner and filesystem metadata. It does not detect
    silent media corruption; force preparation after a storage error. Startup
    refuses changed files instead of unexpectedly rehashing the entire image.
    """

    def __init__(self, path: Path, *, prepare: bool, force: bool = False) -> None:
        self.path, self.prepare, self.entries = path, prepare, {}
        if not path.is_absolute() or ".." in path.parts:
            raise RadxaUSBError("validation cache requires an absolute normalized path")
        if _radxa_usb_symlink_reason(path.parent):
            raise RadxaUSBError("validation cache directory contains a symlink")
        if prepare:
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            parent = path.parent.stat()
        except OSError as exc:
            raise RadxaUSBError("validation cache absent; run prepare once") from exc
        if parent.st_uid != os.geteuid() or stat.S_IMODE(parent.st_mode) != 0o700:
            raise RadxaUSBError("validation cache directory must have owner-only mode 0700")
        if os.path.lexists(path):
            info = path.lstat()
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                    or stat.S_IMODE(info.st_mode) != 0o600 or info.st_size > 1024 * 1024):
                raise RadxaUSBError("validation cache must be a private regular file")
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd, "r") as stream:
                if _radxa_usb_stat_identity(os.fstat(stream.fileno())) != _radxa_usb_stat_identity(info):
                    raise RadxaUSBError("validation cache changed while opening")
                try:
                    value = json.load(stream)
                except (ValueError, UnicodeError) as exc:
                    raise RadxaUSBError("invalid validation cache") from exc
            if (not isinstance(value, dict) or value.get("schema") != _CACHE_SCHEMA
                    or value.get("tool_version") != VALIDATION_CACHE_POLICY_VERSION
                    or not isinstance(value.get("entries"), dict)):
                if not prepare:
                    raise RadxaUSBError("validation cache policy changed; prepare again")
            elif not force:
                self.entries = value["entries"]
        elif not prepare:
            raise RadxaUSBError("prepared-content cache absent; run prepare once")

    @staticmethod
    def key(path: Path, offset: int, length: int) -> str:
        """Include the exact path and extent boundaries in the cache key."""
        return json.dumps([str(path), offset, length], separators=(",", ":"))

    def lookup(self, path: Path, info: os.stat_result, offset: int, length: int) -> str | None:
        """Accept hashes for owner-controlled inputs with identical metadata."""
        if info.st_uid != os.geteuid() or info.st_mode & 0o022:
            raise RadxaUSBError(f"prepared input must be owner-controlled: {path}")
        item = self.entries.get(self.key(path, offset, length))
        metadata = list(_radxa_usb_stat_identity(info)) + [info.st_mode, info.st_uid]
        if (isinstance(item, dict) and item.get("identity") == metadata
                and isinstance(item.get("sha256"), str)
                and re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
            return item["sha256"]
        if not self.prepare:
            raise RadxaUSBError(f"prepared input changed; run prepare: {path}")
        return None

    def remember(self, path: Path, info: os.stat_result, offset: int, length: int, digest: str) -> None:
        """Retain only a completed check; partial checks never reach disk."""
        if self.prepare:
            self.entries[self.key(path, offset, length)] = {
                "identity": list(_radxa_usb_stat_identity(info)) + [info.st_mode, info.st_uid],
                "sha256": digest,
            }

    def save(self) -> None:
        """Publish once the complete preparation operation has succeeded."""
        import tempfile
        fd, name = tempfile.mkstemp(prefix=".validation-", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump({"schema": _CACHE_SCHEMA,
                           "tool_version": VALIDATION_CACHE_POLICY_VERSION,
                           "entries": self.entries}, stream, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.path)
            directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(name):
                os.unlink(name)


@contextmanager
def radxa_usb_validation_session(cache_path: str | Path | None, *, prepare: bool = False,
                                 force: bool = False):
    """Scope the optional cache to one operation; default behavior hashes fully."""
    cache = _RadxaUSBValidationCache(Path(cache_path), prepare=prepare, force=force) if cache_path else None
    token = _VALIDATION_CACHE.set(cache)
    try:
        yield
        if cache is not None and prepare:
            cache.save()
    finally:
        _VALIDATION_CACHE.reset(token)


def radxa_usb_validation_cache_version() -> str:
    """Return the stable prepared-content policy identity, independent of transport."""
    return VALIDATION_CACHE_POLICY_VERSION


@dataclass(frozen=True)
class RadxaUSBServedFile:
    """One manifest-bound regular file and the inode observed at validation."""

    path: Path
    size: int
    sha256: str
    st_dev: int
    st_ino: int
    st_mode: int
    st_mtime_ns: int
    st_ctime_ns: int

    def to_dict(self) -> dict[str, object]:
        """Return the state representation used for later revalidation."""
        return {
            "path": str(self.path),
            "size": self.size,
            "sha256": self.sha256,
            "st_dev": self.st_dev,
            "st_ino": self.st_ino,
            "st_mode": self.st_mode,
            "st_mtime_ns": self.st_mtime_ns,
            "st_ctime_ns": self.st_ctime_ns,
        }


@dataclass(frozen=True)
class RadxaUSBBuilderBinding:
    """One builder manifest and the genuine/custom bytes it authorizes."""

    manifest: RadxaUSBServedFile
    genuine_path: Path
    genuine_size: int
    genuine_sha256: str
    custom_path: Path
    custom_size: int
    custom_sha256: str

    def to_dict(self) -> dict[str, object]:
        """Return the trust-anchor identity retained for teardown."""
        return {
            "manifest": self.manifest.to_dict(),
            "genuine_path": str(self.genuine_path),
            "genuine_size": self.genuine_size,
            "genuine_sha256": self.genuine_sha256,
            "custom_path": str(self.custom_path),
            "custom_size": self.custom_size,
            "custom_sha256": self.custom_sha256,
        }


@dataclass(frozen=True)
class RadxaUSBManifestRegion:
    """One replacement record, including its nbdkit switching policy."""

    replacement: RadxaUSBServedFile
    builder: RadxaUSBBuilderBinding
    offset: int
    length: int
    mode: str
    switch_after_pass: int

    def to_dict(self) -> dict[str, object]:
        """Return the state representation for one replacement region."""
        return {
            "replacement": self.replacement.to_dict(),
            "builder": self.builder.to_dict(),
            "offset": self.offset,
            "length": self.length,
            "mode": self.mode,
            "switch_after_pass": self.switch_after_pass,
        }


@dataclass(frozen=True)
class RadxaUSBBoundContent:
    """Exact manifest and served inputs retained by one arm plan."""

    manifest: RadxaUSBServedFile
    baseline: RadxaUSBServedFile
    regions: RadxaUSBServedFile
    plugin: RadxaUSBServedFile
    replacements: tuple[RadxaUSBManifestRegion, ...]

    def to_dict(self) -> dict[str, object]:
        """Return all verified identities for state and CLI output."""
        return {
            "manifest": self.manifest.to_dict(),
            "baseline": self.baseline.to_dict(),
            "regions": self.regions.to_dict(),
            "plugin": self.plugin.to_dict(),
            "replacements": [item.to_dict() for item in self.replacements],
        }


@dataclass(frozen=True)
class RadxaUSBNbdDevice:
    """One NBD device observed under the injected sysfs and dev roots."""

    name: str
    device_path: Path
    sysfs_path: Path
    pid: str | None
    holders: tuple[str, ...]
    block_device: bool

    @property
    def free(self) -> bool:
        """Return true only when no pid or holder owns the NBD device."""
        return not self.pid and not self.holders and self.block_device

    def occupancy_reason(self) -> str | None:
        """Describe why this NBD device is not free."""
        reasons: list[str] = []
        if self.pid:
            reasons.append(f"pid={self.pid}")
        if self.holders:
            reasons.append("holders=" + ",".join(self.holders))
        if not self.block_device:
            reasons.append("device path is not a block device")
        return "; ".join(reasons) or None


@dataclass(frozen=True)
class RadxaUSBInspection:
    """Read-only platform facts used to build an arm plan."""

    platform: str
    kernel_release: str
    effective_uid: int
    sysfs_root: Path
    dev_root: Path
    proc_root: Path
    dependencies: Mapping[str, str | None]
    udcs: tuple[str, ...]
    udc_drivers: Mapping[str, str | None]
    nbd_devices: tuple[RadxaUSBNbdDevice, ...]
    configfs_root: Path
    gadget_path: Path
    configfs_present: bool
    gadget_occupied: bool
    bound_udcs: Mapping[str, str]
    state_root: Path
    state_occupied: bool
    board_model: str | None
    issues: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation for CLI output."""
        value = asdict(self)
        for key in (
            "sysfs_root",
            "dev_root",
            "proc_root",
            "configfs_root",
            "gadget_path",
            "state_root",
        ):
            value[key] = str(value[key])
        for device in value["nbd_devices"]:
            device["device_path"] = str(device["device_path"])
            device["sysfs_path"] = str(device["sysfs_path"])
        return value


@dataclass(frozen=True)
class RadxaUSBPlan:
    """Validated resources and commands for one explicit arm operation."""

    baseline_image: Path
    backing_kind: str
    backing_path: Path
    regions_json: Path
    plugin: Path
    serve_plan: Path
    bound_content: RadxaUSBBoundContent
    udc: str
    nbd_device: RadxaUSBNbdDevice
    sysfs_root: Path
    dev_root: Path
    configfs_root: Path
    gadget_name: str
    gadget_path: Path
    state_root: Path
    nbd_host: str
    nbd_port: int
    nbdkit_command: tuple[str, ...]
    nbd_client_attach_command: tuple[str, ...]
    nbd_client_detach_command: tuple[str, ...]
    fuse_helper: Path | None = None
    fuse_fusermount: Path | None = None
    fuse_mount_directory: Path | None = None
    fuse_fsname: str | None = None
    fuse_helper_command: tuple[str, ...] = ()
    fuse_unmount_command: tuple[str, ...] = ()
    proc_root: Path = DEFAULT_PROC_ROOT
    issues: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ready(self) -> bool:
        """Return true when every arm precondition passed."""
        return not self.issues

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation for CLI output."""
        value = asdict(self)
        for key in (
            "baseline_image",
            "backing_path",
            "regions_json",
            "plugin",
            "serve_plan",
            "sysfs_root",
            "dev_root",
            "configfs_root",
            "gadget_path",
            "state_root",
            "proc_root",
            "fuse_helper",
            "fuse_fusermount",
            "fuse_mount_directory",
        ):
            if value[key] is not None:
                value[key] = str(value[key])
        value["nbd_device"] = asdict(self.nbd_device)
        value["nbd_device"]["device_path"] = str(self.nbd_device.device_path)
        value["nbd_device"]["sysfs_path"] = str(self.nbd_device.sysfs_path)
        value["bound_content"] = self.bound_content.to_dict()
        return value


@dataclass(frozen=True)
class RadxaUSBArmed:
    """Confirmation returned after the complete USB serving chain is armed."""

    plan: RadxaUSBPlan
    state_path: Path
    nbdkit_pid: int
    nbdkit_process: object = field(repr=False, compare=False)
    state: dict[str, object] = field(repr=False, compare=False)
    fuse_helper_pid: int | None = None
    fuse_helper_process: object | None = field(
        default=None, repr=False, compare=False
    )


CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]
ProcessStarter = Callable[..., object]
ProcessIdentityCapture = Callable[[int], dict[str, object]]
ProcessProbe = Callable[[int, Mapping[str, object]], str]
ProcessTerminator = Callable[[int], None]
PortChecker = Callable[[str, int], bool]
PathChecker = Callable[[Path], bool]
CancelChecker = Callable[[], bool]
NotifySender = Callable[[str], bool]


def radxa_usb_run_command(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Run a bounded external command without a shell."""
    try:
        return subprocess.run(
            list(argv),
            check=False,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RadxaUSBError(f"could not run {argv[0]}: {exc}") from exc


def _radxa_usb_require_success(
    command: Sequence[str], result: subprocess.CompletedProcess[str]
) -> None:
    """Raise a useful error for a failed external command."""
    if result.returncode == 0:
        return
    detail = (result.stderr or result.stdout or "").strip()
    suffix = f": {detail}" if detail else ""
    raise RadxaUSBError(
        f"{command[0]} failed with status {result.returncode}{suffix}"
    )


def _radxa_usb_read_text(path: Path) -> str | None:
    """Read a small sysfs value when it exists."""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _radxa_usb_symlink_reason(path: Path) -> str | None:
    """Return the first symlinked component in an existing path prefix."""
    parts = path.expanduser().absolute().parts
    current = Path(parts[0])
    for part in parts[1:]:
        current /= part
        try:
            if stat.S_ISLNK(current.lstat().st_mode):
                return f"symlinked path component: {current}"
        except FileNotFoundError:
            continue
        except OSError as exc:
            return f"cannot inspect path component {current}: {exc}"
    return None


def _radxa_usb_assert_safe_path(path: Path) -> None:
    """Reject symlinked or unreadable components before traversal or mutation."""
    reason = _radxa_usb_symlink_reason(path)
    if reason:
        raise RadxaUSBError(reason)


def _radxa_usb_nbd_value(path: Path) -> str | None:
    """Read an NBD pid value, treating zero as disconnected."""
    raw = _radxa_usb_read_text(path)
    return raw if raw and raw != "0" else None


def _radxa_usb_snapshot_nbd(
    *,
    sysfs_root: Path,
    nbd_name: str,
    device_path: Path,
    is_block_device: PathChecker,
) -> RadxaUSBNbdDevice | None:
    """Read current NBD occupancy; None means the sysfs device disappeared."""
    sysfs_resolved = sysfs_root.resolve()
    entry = sysfs_root / "block" / nbd_name
    try:
        resolved = entry.resolve(strict=True)
    except FileNotFoundError:
        if entry.is_symlink():
            raise RadxaUSBError(f"sysfs NBD symlink is broken: {entry}")
        return None
    except OSError as exc:
        raise RadxaUSBError(f"cannot resolve sysfs NBD entry {entry}: {exc}") from exc
    try:
        resolved.relative_to(sysfs_resolved)
    except ValueError as exc:
        raise RadxaUSBError(f"sysfs NBD entry escapes injected root: {entry}") from exc
    if resolved.name != nbd_name or not resolved.is_dir():
        raise RadxaUSBError(f"sysfs NBD entry identity changed: {entry}")
    holders_root = resolved / "holders"
    try:
        holders = tuple(sorted(path.name for path in holders_root.iterdir()))
    except OSError:
        holders = ()
    return RadxaUSBNbdDevice(
        name=nbd_name,
        device_path=device_path,
        sysfs_path=resolved,
        pid=_radxa_usb_nbd_value(resolved / "pid"),
        holders=holders,
        block_device=is_block_device(device_path),
    )


def _radxa_usb_sysfs_numbers(root: Path, prefix: str) -> list[Path]:
    """Return numbered sysfs block entries with numeric ordering."""
    block = root / "block"
    if not block.is_dir():
        return []
    entries = [
        path
        for path in block.iterdir()
        if path.name.startswith(prefix) and (path.is_dir() or path.is_symlink())
    ]

    def sort_key(path: Path) -> tuple[int, str]:
        match = NBD_NAME_RE.fullmatch(path.name)
        return (int(match.group(1)), path.name) if match else (sys.maxsize, path.name)

    return sorted(entries, key=sort_key)


def _radxa_usb_default_is_block(path: Path) -> bool:
    """Return true for an existing Linux block device."""
    try:
        return stat.S_ISBLK(path.stat().st_mode)
    except OSError:
        return False


def _radxa_usb_udc_driver(sysfs_root: Path, udc: str) -> str | None:
    """Resolve the UDC's driver link basename without assuming a controller."""
    link = sysfs_root / "class" / "udc" / udc / "device" / "driver"
    try:
        return link.resolve(strict=False).name or None
    except OSError:
        return None


def _radxa_usb_bound_udcs(configfs_root: Path) -> dict[str, str]:
    """Map currently bound UDC names to existing configfs gadgets."""
    bound: dict[str, str] = {}
    if not configfs_root.is_dir():
        return bound
    for gadget in configfs_root.iterdir():
        if not gadget.is_dir():
            continue
        udc = _radxa_usb_read_text(gadget / "UDC")
        if udc:
            bound[udc] = gadget.name
    return bound


def radxa_usb_inspect(
    *,
    backing_kind: str = "nbd",
    sysfs_root: str | Path = DEFAULT_SYSFS_ROOT,
    dev_root: str | Path = DEFAULT_DEV_ROOT,
    configfs_root: str | Path = DEFAULT_CONFIGFS_ROOT,
    proc_root: str | Path = DEFAULT_PROC_ROOT,
    state_root: str | Path = DEFAULT_STATE_ROOT,
    gadget_name: str = DEFAULT_GADGET_NAME,
    which: Callable[[str], str | None] = shutil.which,
    effective_uid: int | None = None,
    uname: Callable[[], object] = os.uname,
    is_block_device: PathChecker = _radxa_usb_default_is_block,
) -> RadxaUSBInspection:
    """Return platform, dependency, UDC, backing, and configfs state.

    The injected roots make every observation fixture-testable. This function
    performs no write and starts no process.
    """
    if backing_kind not in BACKING_KINDS:
        raise RadxaUSBError(f"unsupported backing kind: {backing_kind}")
    sysfs = Path(sysfs_root).expanduser().resolve()
    dev = Path(dev_root).expanduser().resolve()
    requested_configfs = Path(configfs_root).expanduser().absolute()
    configfs = requested_configfs.resolve()
    proc = Path(proc_root).expanduser().resolve()
    runtime_state = Path(state_root).expanduser().resolve()
    udc_root = sysfs / "class" / "udc"
    try:
        udcs = tuple(sorted(path.name for path in udc_root.iterdir()))
    except OSError:
        udcs = ()

    issues: list[str] = []
    devices: list[RadxaUSBNbdDevice] = []
    for entry in _radxa_usb_sysfs_numbers(sysfs, "nbd"):
        try:
            device = _radxa_usb_snapshot_nbd(
                sysfs_root=sysfs,
                nbd_name=entry.name,
                device_path=dev / entry.name,
                is_block_device=is_block_device,
            )
        except RadxaUSBError as exc:
            issues.append(str(exc))
            continue
        if device is not None:
            devices.append(device)

    try:
        kernel_release = str(uname().release)
    except (AttributeError, OSError):
        kernel_release = "unknown"
    board_model = _radxa_usb_read_text(proc / "device-tree" / "model")
    gadget_path = configfs / gadget_name
    bound = _radxa_usb_bound_udcs(configfs)
    dependencies = {"nbdkit": which("nbdkit")}
    if backing_kind == "nbd":
        dependencies["nbd-client"] = which("nbd-client")
    else:
        dependencies["fusermount3"] = which("fusermount3")
        helper = DEFAULT_FUSE_HELPER
        dependencies["ioniq-nbdfuse-direct"] = str(helper) if os.access(helper, os.X_OK) else None
    if not udcs:
        issues.append(f"no UDC found under {udc_root}")
    if backing_kind == "nbd" and not devices:
        issues.append(f"no NBD block devices found under {sysfs / 'block'}")
    for name, executable in dependencies.items():
        if not executable:
            issues.append(f"missing dependency: {name}")
    if not configfs.is_dir():
        issues.append(f"configfs gadget root is unavailable: {configfs}")
    configfs_symlink = _radxa_usb_symlink_reason(requested_configfs)
    if configfs_symlink:
        issues.append(configfs_symlink)
    if gadget_path.exists() or gadget_path.is_symlink():
        issues.append(f"configfs gadget already exists: {gadget_path}")
    if runtime_state.exists():
        issues.append(f"arm state already exists: {runtime_state}")
    elif not runtime_state.parent.is_dir():
        issues.append(f"arm state parent is unavailable: {runtime_state.parent}")

    return RadxaUSBInspection(
        platform=sys.platform,
        kernel_release=kernel_release,
        effective_uid=os.geteuid() if effective_uid is None else effective_uid,
        sysfs_root=sysfs,
        dev_root=dev,
        proc_root=proc,
        dependencies=dependencies,
        udcs=udcs,
        udc_drivers={
            udc: _radxa_usb_udc_driver(sysfs, udc) for udc in udcs
        },
        nbd_devices=tuple(devices),
        configfs_root=configfs,
        gadget_path=gadget_path,
        configfs_present=configfs.is_dir(),
        gadget_occupied=gadget_path.exists(),
        bound_udcs=bound,
        state_root=runtime_state,
        state_occupied=runtime_state.exists(),
        board_model=board_model,
        issues=tuple(issues),
    )


def _radxa_usb_pairs_without_duplicates(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    """Build one JSON object while rejecting repeated field names."""
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise RadxaUSBError(f"duplicate JSON field: {key}")
        value[key] = item
    return value


def _radxa_usb_parse_json(data: bytes, label: str) -> object:
    """Decode strict JSON and convert parser failures to module errors."""
    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_radxa_usb_pairs_without_duplicates,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise RadxaUSBError(f"{label} is invalid JSON: {exc}") from exc


def _radxa_usb_normalized_path(value: object, label: str) -> Path:
    """Return one absolute lexical path without resolving symlink targets."""
    if not isinstance(value, str) or not value:
        raise RadxaUSBError(f"{label} path must be a non-empty string")
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        raise RadxaUSBError(f"{label} path must be absolute: {value}")
    normalized = Path(os.path.normpath(os.fspath(candidate)))
    if str(normalized) != value:
        raise RadxaUSBError(f"{label} path is not normalized: {value}")
    reason = _radxa_usb_symlink_reason(normalized)
    if reason:
        raise RadxaUSBError(f"{label} {reason}")
    return normalized


def _radxa_usb_stat_identity(info: os.stat_result) -> tuple[int, ...]:
    """Return stable file identity fields without read-induced atime."""
    return (
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _radxa_usb_check_cancelled(cancel_requested: CancelChecker | None) -> None:
    """Raise at safe checkpoints when the service has been asked to stop."""
    if cancel_requested is not None and cancel_requested():
        raise RadxaUSBCancelled("arming cancelled before USB exposure")


def _radxa_usb_bound_file(
    path: Path,
    label: str,
    *,
    retain_bytes: bool = False,
    cancel_requested: CancelChecker | None = None,
) -> tuple[RadxaUSBServedFile, bytes | None]:
    """Read and hash one regular file while binding its path and inode."""
    _radxa_usb_check_cancelled(cancel_requested)
    try:
        before = path.lstat()
    except OSError as exc:
        raise RadxaUSBError(f"{label} is unavailable: {path}: {exc}") from exc
    if not stat.S_ISREG(before.st_mode):
        raise RadxaUSBError(f"{label} is not a regular file: {path}")
    try:
        with path.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            if _radxa_usb_stat_identity(opened) != _radxa_usb_stat_identity(before):
                raise RadxaUSBError(f"{label} changed while opening: {path}")
            digest = hashlib.sha256()
            chunks: list[bytes] = []
            cache = _VALIDATION_CACHE.get()
            cached_value = cache.lookup(path, opened, 0, opened.st_size) if cache else None
            cached = cached_value if not retain_bytes else None
            last_report = 0
            while cached is None:
                _radxa_usb_check_cancelled(cancel_requested)
                block = handle.read(1024 * 1024)
                if not block:
                    break
                digest.update(block)
                if cache and handle.tell() - last_report >= 256 * 1024 * 1024:
                    last_report = handle.tell()
                    print(f"prepare bytes={last_report} total={opened.st_size} file={path.name}", file=sys.stderr, flush=True)
                if retain_bytes:
                    chunks.append(block)
            _radxa_usb_check_cancelled(cancel_requested)
            after_open = os.fstat(handle.fileno())
    except OSError as exc:
        raise RadxaUSBError(f"cannot read {label}: {path}: {exc}") from exc
    try:
        after_path = path.lstat()
    except OSError as exc:
        raise RadxaUSBError(f"{label} disappeared while reading: {path}") from exc
    identity = _radxa_usb_stat_identity(before)
    if (
        _radxa_usb_stat_identity(after_open) != identity
        or _radxa_usb_stat_identity(after_path) != identity
    ):
        raise RadxaUSBError(f"{label} changed while reading: {path}")
    record = RadxaUSBServedFile(
        path=path,
        size=before.st_size,
        sha256=cached if cached is not None else digest.hexdigest(),
        st_dev=before.st_dev,
        st_ino=before.st_ino,
        st_mode=before.st_mode,
        st_mtime_ns=before.st_mtime_ns,
        st_ctime_ns=before.st_ctime_ns,
    )
    if cache is not None:
        cache.remember(path, after_path, 0, after_path.st_size, record.sha256)
    return record, b"".join(chunks) if retain_bytes else None


def _radxa_usb_manifest_file_field(
    value: object, label: str, *, retain_bytes: bool = False
) -> tuple[RadxaUSBServedFile, bytes | None]:
    """Validate one manifest file record and bind it to live file content."""
    if not isinstance(value, dict):
        raise RadxaUSBError(f"manifest {label} must be an object")
    expected_keys = {"path", "size", "sha256"}
    if set(value) != expected_keys:
        missing = sorted(expected_keys - set(value))
        unknown = sorted(set(value) - expected_keys)
        detail = f"manifest {label} fields"
        if missing:
            detail += f" missing={missing}"
        if unknown:
            detail += f" unknown={unknown}"
        raise RadxaUSBError(detail)
    path = _radxa_usb_normalized_path(value["path"], f"manifest {label}")
    size = value["size"]
    digest = value["sha256"]
    if type(size) is not int or size < 0:
        raise RadxaUSBError(f"manifest {label} size is invalid")
    if (
        not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise RadxaUSBError(f"manifest {label} sha256 is invalid")
    record, data = _radxa_usb_bound_file(
        path,
        label,
        retain_bytes=retain_bytes,
    )
    if record.size != size:
        raise RadxaUSBError(
            f"{label} size mismatch: manifest={size} live={record.size}"
        )
    if record.sha256 != digest:
        raise RadxaUSBError(f"{label} sha256 mismatch: {path}")
    return record, data


def _radxa_usb_sha256_extent(path: Path, offset: int, length: int) -> str:
    """Hash one exact baseline extent without trusting its filename."""
    before = path.lstat()
    cache = _VALIDATION_CACHE.get()
    cached = cache.lookup(path, before, offset, length) if cache else None
    if cached is not None:
        return cached
    digest = hashlib.sha256()
    remaining = length
    try:
        with path.open("rb") as handle:
            handle.seek(offset)
            while remaining:
                block = handle.read(min(1024 * 1024, remaining))
                if not block:
                    raise RadxaUSBError(
                        f"baseline extent is short at {path}:{offset}+{length}"
                    )
                digest.update(block)
                remaining -= len(block)
    except OSError as exc:
        raise RadxaUSBError(
            f"cannot read baseline extent {path}:{offset}+{length}: {exc}"
        ) from exc
    after = path.lstat()
    if _radxa_usb_stat_identity(before) != _radxa_usb_stat_identity(after):
        raise RadxaUSBError("baseline changed during extent validation")
    result = digest.hexdigest()
    if cache is not None:
        cache.remember(path, after, offset, length, result)
    return result


def _radxa_usb_validate_builder_manifest(
    value: object,
    record: RadxaUSBServedFile,
    *,
    baseline: RadxaUSBServedFile,
    replacement: RadxaUSBServedFile,
    offset: int,
    length: int,
) -> RadxaUSBBuilderBinding:
    """Validate the existing builder manifest as the replacement trust anchor."""
    if not isinstance(value, dict):
        raise RadxaUSBError("builder manifest must be an object")
    expected_keys = {
        "schema",
        "tool",
        "payload_version",
        "device_basename",
        "genuine",
        "custom",
        "overlay",
        "limitations",
    }
    if set(value) != expected_keys:
        missing = sorted(expected_keys - set(value))
        unknown = sorted(set(value) - expected_keys)
        detail = "builder manifest fields"
        if missing:
            detail += f" missing={missing}"
        if unknown:
            detail += f" unknown={unknown}"
        raise RadxaUSBError(detail)
    if value["schema"] != BUILDER_MANIFEST_SCHEMA:
        raise RadxaUSBError("builder manifest schema is unsupported")
    tool = value["tool"]
    if (
        not isinstance(tool, dict)
        or set(tool) != {"name", "version"}
        or tool["name"] != BUILDER_TOOL_NAME
        or tool["version"] != BUILDER_TOOL_VERSION
    ):
        raise RadxaUSBError(
            "builder manifest tool identity is not "
            f"{BUILDER_TOOL_NAME} {BUILDER_TOOL_VERSION}"
        )
    genuine = value["genuine"]
    custom = value["custom"]
    genuine_keys = {"path", "size", "sha256", "body_size"}
    custom_keys = {
        "path",
        "size",
        "sha256",
        "compressed_size",
        "zero_padding",
        "te2_integrity_valid",
    }
    if not isinstance(genuine, dict) or set(genuine) != genuine_keys:
        raise RadxaUSBError("builder manifest genuine record is invalid")
    if not isinstance(custom, dict) or set(custom) != custom_keys:
        raise RadxaUSBError("builder manifest custom record is invalid")
    genuine_path = _radxa_usb_normalized_path(
        genuine["path"], "builder genuine"
    )
    custom_path = _radxa_usb_normalized_path(
        custom["path"], "builder custom"
    )
    genuine_size = genuine["size"]
    custom_size = custom["size"]
    genuine_sha256 = genuine["sha256"]
    custom_sha256 = custom["sha256"]
    for label, size in (
        ("genuine", genuine_size),
        ("custom", custom_size),
    ):
        if type(size) is not int or size < 1:
            raise RadxaUSBError(f"builder manifest {label} size is invalid")
    for label, digest in (
        ("genuine", genuine_sha256),
        ("custom", custom_sha256),
    ):
        if (
            not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
        ):
            raise RadxaUSBError(
                f"builder manifest {label} sha256 is invalid"
            )
    if custom.get("te2_integrity_valid") is not True:
        raise RadxaUSBError("builder manifest custom TE2 integrity is not true")
    # Builder paths are provenance from the machine that produced the custom
    # envelope.  They are intentionally not local identity claims: the Radxa
    # normally receives copied artifacts, and its baseline is the complete USB
    # image rather than the standalone genuine envelope.  The portable trust
    # binding is the manifest size/hash below, while the serve plan separately
    # binds every Radxa-local path and inode.
    if genuine_size != length:
        raise RadxaUSBError(
            "builder genuine size does not match replacement region length"
        )
    if custom_size != replacement.size or custom_sha256 != replacement.sha256:
        raise RadxaUSBError(
            "replacement does not match builder manifest custom size/hash"
        )
    extent_sha256 = _radxa_usb_sha256_extent(
        baseline.path, offset, length
    )
    if extent_sha256 != genuine_sha256:
        raise RadxaUSBError(
            "baseline region does not match builder manifest genuine sha256"
        )
    return RadxaUSBBuilderBinding(
        manifest=record,
        genuine_path=genuine_path,
        genuine_size=genuine_size,
        genuine_sha256=genuine_sha256,
        custom_path=custom_path,
        custom_size=custom_size,
        custom_sha256=custom_sha256,
    )


def _radxa_usb_manifest_region_field(
    value: object,
    index: int,
    *,
    baseline: RadxaUSBServedFile,
) -> tuple[RadxaUSBManifestRegion, bytes | None]:
    """Validate one replacement record from the serve manifest."""
    if not isinstance(value, dict):
        raise RadxaUSBError(
            f"manifest replacement item {index} must be an object"
        )
    expected_keys = {
        "path",
        "size",
        "sha256",
        "offset",
        "length",
        "mode",
        "switch_after_pass",
        "builder_manifest",
    }
    if set(value) != expected_keys:
        missing = sorted(expected_keys - set(value))
        unknown = sorted(set(value) - expected_keys)
        detail = f"manifest replacement item {index} fields"
        if missing:
            detail += f" missing={missing}"
        if unknown:
            detail += f" unknown={unknown}"
        raise RadxaUSBError(detail)
    path = _radxa_usb_normalized_path(
        value["path"], f"manifest replacement item {index}"
    )
    size = value["size"]
    digest = value["sha256"]
    offset = value["offset"]
    length = value["length"]
    mode = value["mode"]
    switch_after_pass = value["switch_after_pass"]
    if type(size) is not int or size < 1:
        raise RadxaUSBError(
            f"manifest replacement item {index} size is invalid"
        )
    if (
        not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise RadxaUSBError(
            f"manifest replacement item {index} sha256 is invalid"
        )
    if type(offset) is not int or offset < 0:
        raise RadxaUSBError(
            f"manifest replacement item {index} offset is invalid"
        )
    if type(length) is not int or length < 1:
        raise RadxaUSBError(
            f"manifest replacement item {index} length is invalid"
        )
    if mode not in {"benign_then_evil", "evil_then_benign"}:
        raise RadxaUSBError(
            f"manifest replacement item {index} mode is invalid"
        )
    if type(switch_after_pass) is not int or switch_after_pass < 1:
        raise RadxaUSBError(
            f"manifest replacement item {index} switch_after_pass is invalid"
        )
    record, _ = _radxa_usb_bound_file(
        path, f"replacement item {index}"
    )
    if record.size != size:
        raise RadxaUSBError(
            f"replacement item {index} size mismatch: "
            f"manifest={size} live={record.size}"
        )
    if record.sha256 != digest:
        raise RadxaUSBError(
            f"replacement item {index} sha256 mismatch: {path}"
        )
    builder_record, builder_bytes = _radxa_usb_manifest_file_field(
        value["builder_manifest"],
        f"builder manifest for replacement item {index}",
        retain_bytes=True,
    )
    assert builder_bytes is not None
    builder_value = _radxa_usb_parse_json(
        builder_bytes, f"builder manifest for replacement item {index}"
    )
    builder = _radxa_usb_validate_builder_manifest(
        builder_value,
        builder_record,
        baseline=baseline,
        replacement=record,
        offset=offset,
        length=length,
    )
    return (
        RadxaUSBManifestRegion(
            replacement=record,
            builder=builder,
            offset=offset,
            length=length,
            mode=mode,
            switch_after_pass=switch_after_pass,
        ),
        None,
    )


def _radxa_usb_parse_regions(
    data: bytes,
    replacements: Sequence[RadxaUSBManifestRegion],
) -> None:
    """Require the regions file to reproduce every bound replacement record."""
    value = _radxa_usb_parse_json(data, "regions JSON")
    if not isinstance(value, list) or not value:
        raise RadxaUSBError("regions JSON must be a non-empty list")
    if len(value) != len(replacements):
        raise RadxaUSBError("regions JSON and manifest replacement counts differ")
    expected_keys = {
        "off",
        "len",
        "evil",
        "switch_after_pass",
        "mode",
    }
    for index, (item, manifest_region) in enumerate(zip(value, replacements)):
        if not isinstance(item, dict):
            raise RadxaUSBError(f"regions JSON item {index} must be an object")
        if set(item) != expected_keys:
            missing = sorted(expected_keys - set(item))
            unknown = sorted(set(item) - expected_keys)
            detail = f"regions JSON item {index} fields"
            if missing:
                detail += f" missing={missing}"
            if unknown:
                detail += f" unknown={unknown}"
            raise RadxaUSBError(detail)
        evil = _radxa_usb_normalized_path(
            item["evil"], f"regions JSON item {index}"
        )
        if evil != manifest_region.replacement.path:
            raise RadxaUSBError(
                f"regions JSON item {index} replacement path mismatch"
            )
        if item["off"] != manifest_region.offset:
            raise RadxaUSBError(f"regions JSON item {index} offset mismatch")
        if item["len"] != manifest_region.length:
            raise RadxaUSBError(f"regions JSON item {index} length mismatch")
        if item["mode"] != manifest_region.mode:
            raise RadxaUSBError(f"regions JSON item {index} mode mismatch")
        if item["switch_after_pass"] != manifest_region.switch_after_pass:
            raise RadxaUSBError(
                f"regions JSON item {index} switch count mismatch"
            )


def _radxa_usb_load_bound_content(path: str | Path) -> RadxaUSBBoundContent:
    """Load one serve plan and verify its existing builder trust anchors."""
    manifest_path = Path(path).expanduser()
    if not manifest_path.is_absolute():
        manifest_path = Path.cwd() / manifest_path
    manifest_path = Path(os.path.normpath(os.fspath(manifest_path)))
    reason = _radxa_usb_symlink_reason(manifest_path)
    if reason:
        raise RadxaUSBError(f"serve plan {reason}")
    manifest_record, manifest_bytes = _radxa_usb_bound_file(
        manifest_path, "serve plan", retain_bytes=True
    )
    assert manifest_bytes is not None
    value = _radxa_usb_parse_json(manifest_bytes, "serve plan")
    if not isinstance(value, dict):
        raise RadxaUSBError("serve plan must be a JSON object")
    expected_keys = {
        "schema",
        "baseline",
        "regions",
        "plugin",
        "replacements",
    }
    if set(value) != expected_keys:
        missing = sorted(expected_keys - set(value))
        unknown = sorted(set(value) - expected_keys)
        detail = "serve plan fields"
        if missing:
            detail += f" missing={missing}"
        if unknown:
            detail += f" unknown={unknown}"
        raise RadxaUSBError(detail)
    if value["schema"] != SERVE_PLAN_SCHEMA:
        raise RadxaUSBError(
            f"unsupported serve plan schema: {value['schema']!r}"
        )
    baseline, _ = _radxa_usb_manifest_file_field(
        value["baseline"], "baseline image"
    )
    regions, regions_bytes = _radxa_usb_manifest_file_field(
        value["regions"], "regions JSON", retain_bytes=True
    )
    plugin, _ = _radxa_usb_manifest_file_field(value["plugin"], "nbdkit plugin")
    raw_replacements = value["replacements"]
    if not isinstance(raw_replacements, list) or not raw_replacements:
        raise RadxaUSBError(
            "manifest replacements must be a non-empty list"
        )
    replacements = tuple(
        _radxa_usb_manifest_region_field(
            item, index, baseline=baseline
        )[0]
        for index, item in enumerate(raw_replacements)
    )
    assert regions_bytes is not None
    _radxa_usb_parse_regions(regions_bytes, replacements)
    if baseline.size < 1:
        raise RadxaUSBError("baseline image must not be empty")
    for index, region in enumerate(replacements):
        if region.replacement.size != region.length:
            raise RadxaUSBError(
                f"replacement item {index} size does not equal region length"
            )
        if region.offset + region.length > baseline.size:
            raise RadxaUSBError(
                f"replacement item {index} exceeds baseline image"
            )
        if index and region.offset < (
            replacements[index - 1].offset
            + replacements[index - 1].length
        ):
            raise RadxaUSBError("manifest replacement regions overlap")
    return RadxaUSBBoundContent(
        manifest=manifest_record,
        baseline=baseline,
        regions=regions,
        plugin=plugin,
        replacements=replacements,
    )


def _radxa_usb_verify_served_file(
    record: RadxaUSBServedFile,
    label: str,
    *,
    cancel_requested: CancelChecker | None = None,
) -> None:
    """Reject any content or inode change after manifest validation."""
    current, _ = _radxa_usb_bound_file(
        record.path,
        label,
        cancel_requested=cancel_requested,
    )
    if current.to_dict() != record.to_dict():
        raise RadxaUSBError(f"{label} identity or content changed: {record.path}")


def _radxa_usb_verify_bound_content(
    content: RadxaUSBBoundContent,
    *,
    cancel_requested: CancelChecker | None = None,
) -> None:
    """Revalidate the serve plan, builder manifests, and every bound file."""
    _radxa_usb_verify_served_file(
        content.manifest, "serve plan", cancel_requested=cancel_requested
    )
    _radxa_usb_verify_served_file(
        content.baseline, "baseline image", cancel_requested=cancel_requested
    )
    _radxa_usb_verify_served_file(
        content.regions, "regions JSON", cancel_requested=cancel_requested
    )
    _radxa_usb_verify_served_file(
        content.plugin, "nbdkit plugin", cancel_requested=cancel_requested
    )
    for index, region in enumerate(content.replacements):
        _radxa_usb_verify_served_file(
            region.builder.manifest,
            f"builder manifest for replacement item {index}",
            cancel_requested=cancel_requested,
        )
        _radxa_usb_verify_served_file(
            region.replacement,
            f"replacement item {index}",
            cancel_requested=cancel_requested,
        )


def _radxa_usb_default_port_available(host: str, port: int) -> bool:
    """Check whether a local TCP port can be bound."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _radxa_usb_make_command(
    inspection: RadxaUSBInspection,
    baseline: Path,
    regions: Path,
    plugin: Path,
    host: str,
    port: int,
) -> tuple[str, ...]:
    """Build the foreground nbdkit command with module-owned logging paths."""
    nbdkit = inspection.dependencies["nbdkit"]
    assert nbdkit is not None
    return (
        nbdkit,
        "--foreground",
        "--ip-addr",
        host,
        "--port",
        str(port),
        "python",
        str(plugin),
        f"baseline={baseline}",
        f"regions={regions}",
        f"log={inspection.state_root / 'nbdkit.log'}",
        f"reads={inspection.state_root / 'reads.log'}",
    )


def _radxa_usb_preflight_fuse_helper(
    helper: Path, *, runner: CommandRunner = radxa_usb_run_command
) -> None:
    """Require the exact installed helper identity before any arm mutation."""
    reason = _radxa_usb_symlink_reason(helper)
    if reason:
        raise RadxaUSBError(f"FUSE helper {reason}")
    try:
        metadata = helper.lstat()
    except OSError as exc:
        raise RadxaUSBError(f"FUSE helper is unavailable: {helper}: {exc}") from exc
    if not stat.S_ISREG(metadata.st_mode):
        raise RadxaUSBError(f"FUSE helper is not a regular file: {helper}")
    if metadata.st_uid != 0 or metadata.st_mode & 0o022:
        raise RadxaUSBError("FUSE helper must be root-owned and not group/world writable")
    result = runner((str(helper), "--version"))
    _radxa_usb_require_success((str(helper), "--version"), result)
    first_line = (result.stdout or "").splitlines()[0] if result.stdout else ""
    if first_line != FUSE_HELPER_VERSION:
        raise RadxaUSBError(
            f"unexpected FUSE helper version: {first_line!r}; "
            f"expected {FUSE_HELPER_VERSION!r}"
        )


def radxa_usb_build_plan(
    *,
    serve_plan: str | Path,
    backing_kind: str = "nbd",
    udc: str | None = None,
    nbd_device: str | None = None,
    nbd_host: str = DEFAULT_NBD_HOST,
    nbd_port: int = DEFAULT_NBD_PORT,
    port_scan_count: int = DEFAULT_PORT_SCAN_COUNT,
    inspection: RadxaUSBInspection | None = None,
    sysfs_root: str | Path = DEFAULT_SYSFS_ROOT,
    dev_root: str | Path = DEFAULT_DEV_ROOT,
    configfs_root: str | Path = DEFAULT_CONFIGFS_ROOT,
    proc_root: str | Path = DEFAULT_PROC_ROOT,
    state_root: str | Path = DEFAULT_STATE_ROOT,
    gadget_name: str = DEFAULT_GADGET_NAME,
    helper_path: str | Path = DEFAULT_FUSE_HELPER,
    fusermount3_path: str | Path | None = None,
    helper_version_runner: CommandRunner = radxa_usb_run_command,
    helper_preflight: Callable[[Path], None] | None = None,
    which: Callable[[str], str | None] = shutil.which,
    effective_uid: int | None = None,
    uname: Callable[[], object] = os.uname,
    is_block_device: PathChecker = _radxa_usb_default_is_block,
    port_available: PortChecker = _radxa_usb_default_port_available,
) -> RadxaUSBPlan:
    """Validate all resources and return a concrete arm plan.

    Ambiguous UDCs require an explicit ``udc``. Raw NBD mode selects the
    lowest-numbered free device; FUSE mode has no NBD device dependency.
    """
    if backing_kind not in BACKING_KINDS:
        raise RadxaUSBError(f"unsupported backing kind: {backing_kind}")
    bound_content = _radxa_usb_load_bound_content(serve_plan)
    manifest_path = bound_content.manifest.path
    baseline = bound_content.baseline.path
    regions = bound_content.regions.path
    plugin_path = bound_content.plugin.path
    if inspection is None:
        inspection = radxa_usb_inspect(
            backing_kind=backing_kind,
            sysfs_root=sysfs_root,
            dev_root=dev_root,
            configfs_root=configfs_root,
            proc_root=proc_root,
            state_root=state_root,
            gadget_name=gadget_name,
            which=which,
            effective_uid=effective_uid,
            uname=uname,
            is_block_device=is_block_device,
        )
    issues = list(inspection.issues)
    if inspection.effective_uid != 0:
        issues.append("root privileges are required to arm the USB gadget")
    if not SAFE_NAME_RE.fullmatch(gadget_name):
        issues.append(f"unsafe gadget name: {gadget_name}")

    if udc is None:
        if len(inspection.udcs) == 1:
            selected_udc = inspection.udcs[0]
        else:
            selected_udc = ""
            if len(inspection.udcs) > 1:
                issues.append(
                    "multiple UDCs found; select one with --udc: "
                    + ", ".join(inspection.udcs)
                )
    elif udc in inspection.udcs:
        selected_udc = udc
    else:
        selected_udc = udc
        issues.append(f"selected UDC does not exist: {udc}")
    if selected_udc in inspection.bound_udcs:
        issues.append(
            f"selected UDC {selected_udc} is already bound to "
            f"{inspection.bound_udcs[selected_udc]}"
        )

    selected_nbd = RadxaUSBNbdDevice(
        name="",
        device_path=Path(),
        sysfs_path=Path(),
        pid=None,
        holders=(),
        block_device=False,
    )
    if backing_kind == "nbd" and nbd_device is None:
        available = [item for item in inspection.nbd_devices if item.free]
        if available:
            selected_nbd = available[0]
        else:
            issues.append("no free NBD block device is available")
    elif backing_kind == "nbd":
        matches = [item for item in inspection.nbd_devices if item.name == nbd_device]
        if not matches:
            selected_nbd = RadxaUSBNbdDevice(
                name=nbd_device,
                device_path=Path(),
                sysfs_path=Path(),
                pid=None,
                holders=(),
                block_device=False,
            )
            issues.append(f"selected NBD device does not exist: {nbd_device}")
        else:
            selected_nbd = matches[0]
            if not selected_nbd.free:
                issues.append(
                    "selected NBD device is unavailable: "
                    + str(selected_nbd.occupancy_reason())
                )

    selected_port = nbd_port
    ports = range(nbd_port, nbd_port + max(port_scan_count, 1))
    free_ports = [port for port in ports if port_available(nbd_host, port)]
    if free_ports:
        selected_port = free_ports[0]
    else:
        issues.append(
            f"no free local TCP port for nbdkit in range "
            f"{nbd_port}..{nbd_port + max(port_scan_count, 1) - 1}"
        )
    if inspection.state_root.exists():
        pass  # The inspection issue already explains the occupied runtime state.
    gadget_path = inspection.configfs_root / gadget_name
    command = _radxa_usb_make_command(
        inspection,
        baseline,
        regions,
        plugin_path,
        nbd_host,
        selected_port,
    ) if inspection.dependencies.get("nbdkit") else ()
    nbd_client = inspection.dependencies.get("nbd-client")
    attach = (
        (
            nbd_client,
            "-N",
            "default",
            nbd_host,
            str(selected_port),
            str(selected_nbd.device_path),
            "-persist",
        )
        if backing_kind == "nbd" and nbd_client and selected_nbd.device_path
        else ()
    )
    detach = (
        (nbd_client, "-d", str(selected_nbd.device_path))
        if backing_kind == "nbd" and nbd_client and selected_nbd.device_path
        else ()
    )
    helper: Path | None = None
    fusermount: Path | None = None
    mount_directory: Path | None = None
    fsname: str | None = None
    fuse_command: tuple[str, ...] = ()
    fuse_unmount: tuple[str, ...] = ()
    backing_path = selected_nbd.device_path
    if backing_kind == "fuse-direct":
        helper = Path(helper_path).expanduser().absolute()
        try:
            if helper_preflight is None:
                _radxa_usb_preflight_fuse_helper(
                    helper, runner=helper_version_runner
                )
            else:
                helper_preflight(helper)
        except (OSError, RadxaUSBError) as exc:
            issues.append(str(exc))
        selected_fusermount = fusermount3_path or inspection.dependencies.get(
            "fusermount3"
        )
        if selected_fusermount is None:
            issues.append("missing dependency: fusermount3")
        else:
            fusermount = Path(selected_fusermount).expanduser().absolute()
        mount_directory = inspection.state_root / "fuse-mount"
        backing_path = mount_directory / "lun"
        fsname = "ioniq-fuse-" + secrets.token_hex(8)
        if fusermount is not None:
            fuse_command = (
                str(helper),
                "-r",
                "-s",
                "-C",
                "1",
                "-P",
                str(inspection.state_root / "fuse-helper.pid"),
                "-o",
                f"fsname={fsname}",
                str(backing_path),
                "--tcp",
                nbd_host,
                str(selected_port),
            )
            fuse_unmount = (str(fusermount), "-u", str(backing_path))
    return RadxaUSBPlan(
        baseline_image=baseline,
        backing_kind=backing_kind,
        backing_path=backing_path,
        regions_json=regions,
        plugin=plugin_path,
        serve_plan=manifest_path,
        bound_content=bound_content,
        udc=selected_udc,
        nbd_device=selected_nbd,
        sysfs_root=inspection.sysfs_root,
        dev_root=inspection.dev_root,
        configfs_root=inspection.configfs_root,
        gadget_name=gadget_name,
        gadget_path=gadget_path,
        state_root=inspection.state_root,
        nbd_host=nbd_host,
        nbd_port=selected_port,
        nbdkit_command=command,
        nbd_client_attach_command=attach,
        nbd_client_detach_command=detach,
        fuse_helper=helper,
        fuse_fusermount=fusermount,
        fuse_mount_directory=mount_directory,
        fuse_fsname=fsname,
        fuse_helper_command=fuse_command,
        fuse_unmount_command=fuse_unmount,
        proc_root=inspection.proc_root,
        issues=tuple(dict.fromkeys(issues)),
    )


def _radxa_usb_write_text(path: Path, value: str) -> None:
    """Write one bounded configfs control value."""
    path.write_text(value + "\n", encoding="ascii")


def _radxa_usb_mkdir_owned(path: Path) -> None:
    """Create a directory that must not already exist."""
    if path.exists():
        raise RadxaUSBError(f"refusing to adopt existing directory: {path}")
    path.mkdir()


def _radxa_usb_ensure_owned_directory(path: Path) -> None:
    """Accept a directory auto-created inside an owned gadget, or create it."""
    if path.is_dir() and not path.is_symlink():
        return
    if path.exists() or path.is_symlink():
        raise RadxaUSBError(f"unexpected gadget child is not a directory: {path}")
    path.mkdir()


def _radxa_usb_atomic_json(path: Path, value: Mapping[str, object]) -> None:
    """Atomically replace the ownership state file."""
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temp, path)


def _radxa_usb_state_document(
    plan: RadxaUSBPlan,
    *,
    gadget_identity: str,
    gadget_created: bool,
    nbd_attached: bool,
    udc_attached: bool,
    nbdkit_pid: int | None,
    state_dir_created: bool,
) -> dict[str, object]:
    """Return the complete state required for ownership-safe teardown."""
    return {
        "schema": STATE_SCHEMA,
        "tool_version": TOOL_VERSION,
        "backing_kind": plan.backing_kind,
        "backing_path": str(plan.backing_path),
        "validation_cache_policy_version": radxa_usb_validation_cache_version(),
        "configfs_root": str(plan.configfs_root),
        "gadget_name": plan.gadget_name,
        "gadget_identity": gadget_identity,
        "gadget_phase": "pending",
        "gadget_dev": None,
        "gadget_ino": None,
        "gadget_created": gadget_created,
        "udc": plan.udc,
        "udc_attached": udc_attached,
        "nbd_name": plan.nbd_device.name,
        "nbd_device": str(plan.nbd_device.device_path),
        "nbd_phase": "prepared",
        "nbd_attempt": None,
        "nbd_attached": nbd_attached,
        "nbd_live_identity": None,
        "nbd_client_detach_command": list(plan.nbd_client_detach_command),
        "nbdkit_pid": nbdkit_pid,
        "nbdkit_plugin": str(plan.plugin),
        "nbdkit_command": list(plan.nbdkit_command),
        "nbdkit_identity": None,
        "fuse_helper": str(plan.fuse_helper) if plan.fuse_helper else None,
        "fuse_helper_pid": None,
        "fuse_helper_command": list(plan.fuse_helper_command),
        "fuse_helper_identity": None,
        "fuse_fusermount": str(plan.fuse_fusermount) if plan.fuse_fusermount else None,
        "fuse_mount_directory": (
            str(plan.fuse_mount_directory) if plan.fuse_mount_directory else None
        ),
        "fuse_mount_dir_dev": None,
        "fuse_mount_dir_ino": None,
        "fuse_mountpoint": str(plan.backing_path) if plan.fuse_helper else None,
        "fuse_fsname": plan.fuse_fsname,
        "fuse_mount_identity": None,
        "fuse_backing_size": None,
        "fuse_lun_ro": None,
        "bound_content": plan.bound_content.to_dict(),
        "reconciliation_required": None,
        "sysfs_root": str(plan.sysfs_root),
        "proc_root": str(plan.proc_root),
        "fuse_unmount_command": list(plan.fuse_unmount_command),
        "fuse_backing_dev": None,
        "fuse_backing_ino": None,
        "state_root": str(plan.state_root),
        "state_dir_created": state_dir_created,
        "cleanup": {
            "udc_unbound": False,
            "nbd_detached": plan.backing_kind != "nbd",
            "gadget_removed": False,
            "fuse_unmounted": plan.backing_kind != "fuse-direct",
            "fuse_helper_stopped": plan.backing_kind != "fuse-direct",
            "nbdkit_stopped": False,
        },
    }


def _radxa_usb_capture_process_identity(
    pid: int, *, proc_root: Path = DEFAULT_PROC_ROOT, label: str = "nbdkit"
) -> dict[str, object]:
    """Read one Linux process instance, rejecting exit/reuse during capture."""
    proc_dir = proc_root / str(pid)

    def start_ticks() -> int:
        """Parse stat field 22 after the possibly space-containing comm field."""
        value = (proc_dir / "stat").read_text(encoding="utf-8")
        fields = value[value.rindex(")") + 2:].split()
        return int(fields[19])

    try:
        boot_id = (proc_root / "sys/kernel/random/boot_id").read_text().strip()
        first_start = start_ticks()
        raw_argv = (proc_dir / "cmdline").read_bytes()
        executable = proc_dir / "exe"
        exe_stat = executable.stat()
        identity = {
            "pid": pid,
            "boot_id": boot_id,
            "start_ticks": first_start,
            "argv": [os.fsdecode(arg) for arg in raw_argv[:-1].split(b"\x00")],
            "executable": {
                "path": os.readlink(executable),
                "dev": int(exe_stat.st_dev),
                "ino": int(exe_stat.st_ino),
            },
        }
        if (
            not boot_id or not raw_argv.endswith(b"\x00")
            or first_start <= 0 or start_ticks() != first_start
            or (proc_dir / "cmdline").read_bytes() != raw_argv
            or executable.stat() != exe_stat
        ):
            raise ValueError("process changed or has incomplete identity")
        return identity
    except (OSError, ValueError, IndexError) as exc:
        raise RadxaUSBError(f"cannot establish {label} process identity: {exc}") from exc


def _radxa_usb_default_process_probe(
    pid: int, expected: Mapping[str, object], *, proc_root: Path = DEFAULT_PROC_ROOT
) -> str:
    """Require the same boot, start ticks, exact argv, and executable instance."""
    try:
        (proc_root / str(pid)).stat()
    except FileNotFoundError:
        return "absent"
    except OSError:
        return "mismatch"
    try:
        live = _radxa_usb_capture_process_identity(pid, proc_root=proc_root)
    except RadxaUSBError:
        # Unreadable, exiting, or unstable processes are never permission to kill.
        return "mismatch"
    return "owned" if live == expected else "mismatch"


def _radxa_usb_signal_process_instance(
    pid: int,
    expected: Mapping[str, object],
    process_probe: ProcessProbe,
    *,
    label: str = "nbdkit",
) -> None:
    """Pin the PID before rechecking identity so reuse cannot redirect SIGTERM."""
    if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
        raise RadxaUSBError("pidfd signalling unavailable; reconciliation required")
    try:
        pidfd = os.pidfd_open(pid)
    except ProcessLookupError:
        return
    try:
        status = process_probe(pid, expected)
        if status == "absent":
            return
        if status != "owned":
            raise RadxaUSBError(f"{label} PID changed before signalling")
        try:
            signal.pidfd_send_signal(pidfd, signal.SIGTERM)
        except ProcessLookupError:
            pass
    finally:
        os.close(pidfd)


def _radxa_usb_wait_for_port(
    host: str, port: int, *, sleep: Callable[[float], None] = time.sleep
) -> None:
    """Wait until the owned nbdkit listener accepts local connections."""
    deadline = time.monotonic() + SERVER_START_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) == 0:
                return
        except OSError:
            pass
        finally:
            sock.close()
        sleep(SERVER_POLL_SECONDS)
    raise RadxaUSBError(f"nbdkit did not listen on {host}:{port} before timeout")


def _radxa_usb_decode_mountinfo(value: str) -> str:
    """Decode the octal escapes used by Linux mountinfo."""
    return re.sub(
        r"\\([0-7]{3})", lambda match: chr(int(match.group(1), 8)), value
    )


def _radxa_usb_fuse_mount(
    state: Mapping[str, object],
) -> dict[str, object] | None:
    """Find the exact FUSE target in proc mountinfo without touching its files."""
    proc_root = Path(str(state.get("proc_root", DEFAULT_PROC_ROOT)))
    mountpoint = str(_radxa_usb_state_value(state, "fuse_mountpoint", str))
    fsname = str(_radxa_usb_state_value(state, "fuse_fsname", str))
    # A hardened dashboard runs in another mount namespace. The backend
    # inherits the controller's namespace, whose mount IDs were checkpointed.
    # After backend exit, cleanup runs in the original controller namespace.
    owner = state.get("nbdkit_pid")
    owner_mountinfo = proc_root / str(owner) / "mountinfo"
    mountinfo = owner_mountinfo if type(owner) is int and owner_mountinfo.exists() else proc_root / "self/mountinfo"
    try:
        lines = mountinfo.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RadxaUSBError(f"cannot inspect FUSE mount provenance: {exc}") from exc
    matches: list[dict[str, object]] = []
    for line in lines:
        fields = line.split()
        try:
            separator = fields.index("-")
            live_mountpoint = _radxa_usb_decode_mountinfo(fields[4])
            if live_mountpoint != mountpoint:
                continue
            matches.append(
                {
                    "mount_id": int(fields[0]),
                    "parent_id": int(fields[1]),
                    "device": fields[2],
                    "mountpoint": live_mountpoint,
                    "mount_options": fields[5],
                    "fstype": fields[separator + 1],
                    "fsname": _radxa_usb_decode_mountinfo(fields[separator + 2]),
                }
            )
        except (IndexError, ValueError) as exc:
            raise RadxaUSBError("invalid Linux mountinfo record") from exc
    if len(matches) > 1:
        raise RadxaUSBError("multiple mounts claim the owned FUSE target")
    if not matches:
        return None
    live = matches[0]
    if live["fstype"] != "fuse" or live["fsname"] != fsname:
        raise RadxaUSBError("FUSE mount source or filesystem type changed")
    return live


def _radxa_usb_validate_fuse_mount(
    state: Mapping[str, object], *, required: bool = True
) -> dict[str, object] | None:
    """Validate the exact recorded FUSE mount or report its absence."""
    live = _radxa_usb_fuse_mount(state)
    if live is None:
        if required:
            raise RadxaUSBError("owned FUSE mount disappeared")
        return None
    _radxa_usb_validate_fuse_directory(state)
    expected = state.get("fuse_mount_identity")
    if expected is not None and live != expected:
        raise RadxaUSBError("FUSE mount identity changed")
    return live


def _radxa_usb_validate_fuse_directory(state: Mapping[str, object]) -> Path:
    """Validate the private parent, which is outside the file-mode FUSE mount."""
    directory = Path(str(_radxa_usb_state_value(state, "fuse_mount_directory", str)))
    target = Path(str(_radxa_usb_state_value(state, "fuse_mountpoint", str)))
    _radxa_usb_assert_safe_path(directory)
    info = directory.lstat()
    if (target.parent != directory or not stat.S_ISDIR(info.st_mode)
            or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700
            or info.st_dev != state.get("fuse_mount_dir_dev")
            or info.st_ino != state.get("fuse_mount_dir_ino")):
        raise RadxaUSBError("FUSE private directory identity changed")
    return directory


def _radxa_usb_fuse_helper_status(
    state: Mapping[str, object],
    *,
    owned_process: object | None,
    process_probe: ProcessProbe,
) -> str:
    """Return absent, owned, or mismatch for the exact FUSE helper instance."""
    pid_value = state.get("fuse_helper_pid")
    if pid_value is None:
        return "absent"
    if not isinstance(pid_value, int) or pid_value <= 0:
        raise RadxaUSBError("state has invalid FUSE helper PID")
    command = state.get("fuse_helper_command")
    if (
        not isinstance(command, list)
        or len(command) < 2
        or any(not isinstance(arg, str) for arg in command)
        or "-d" in command
    ):
        raise RadxaUSBError("state has invalid FUSE helper command")
    identity = state.get("fuse_helper_identity")
    if owned_process is not None:
        if getattr(owned_process, "pid", None) != pid_value:
            return "mismatch"
        poll = getattr(owned_process, "poll", None)
        if not callable(poll) or poll() is not None:
            return "absent"
        if identity is None:
            return "owned"
    if (
        not isinstance(identity, dict)
        or identity.get("pid") != pid_value
        or identity.get("argv") != command
        or not isinstance(identity.get("boot_id"), str)
        or type(identity.get("start_ticks")) is not int
        or identity["start_ticks"] <= 0
        or not isinstance(identity.get("executable"), dict)
    ):
        raise RadxaUSBError("state has invalid FUSE helper identity")
    return process_probe(pid_value, identity)


def _radxa_usb_capture_started_process(
    process: object,
    *,
    command: Sequence[str],
    capture: ProcessIdentityCapture,
    process_probe: ProcessProbe,
    cancel_requested: CancelChecker | None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    """Capture a stable just-exec identity while the exact Popen stays owned."""
    pid = int(getattr(process, "pid"))
    deadline = time.monotonic() + PROCESS_IDENTITY_RETRY_SECONDS
    last_error = "process identity unavailable"
    while True:
        _radxa_usb_check_cancelled(cancel_requested)
        poll = getattr(process, "poll", None)
        if not callable(poll):
            raise RadxaUSBError("started process has no ownership probe")
        if poll() is not None:
            raise RadxaUSBError("started process exited before identity capture")
        try:
            identity = capture(pid)
            if identity.get("pid") != pid or identity.get("argv") != list(command):
                raise RadxaUSBError("started process command does not match its plan")
            if process_probe(pid, identity) == "owned" and poll() is None:
                return identity
            last_error = "process changed during identity capture"
        except RadxaUSBError as exc:
            last_error = str(exc)
        if time.monotonic() >= deadline:
            raise RadxaUSBError(f"cannot establish process identity: {last_error}")
        sleep(SERVER_POLL_SECONDS)


def _radxa_usb_wait_for_fuse_ready(
    plan: RadxaUSBPlan,
    state: dict[str, object],
    state_path: Path,
    *,
    helper_process: object,
    process_probe: ProcessProbe,
    cancel_requested: CancelChecker | None,
    stat_once: Callable[[Path], os.stat_result] = Path.stat,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    """Wait for exact mount provenance, then inspect the backing size once."""
    pid = int(_radxa_usb_state_value(state, "fuse_helper_pid", int))
    identity = _radxa_usb_state_value(state, "fuse_helper_identity", dict)
    deadline = time.monotonic() + FUSE_READY_TIMEOUT_SECONDS
    while True:
        _radxa_usb_check_cancelled(cancel_requested)
        status = _radxa_usb_fuse_helper_status(
            state,
            owned_process=helper_process,
            process_probe=process_probe,
        )
        if status != "owned":
            raise RadxaUSBError(f"FUSE helper is {status} before mount readiness")
        mount = _radxa_usb_fuse_mount(state)
        if mount is not None:
            state["fuse_mount_identity"] = mount
            _radxa_usb_atomic_json(state_path, state)
            metadata = stat_once(plan.backing_path)
            if (not stat.S_ISREG(metadata.st_mode)
                    or metadata.st_size != plan.bound_content.baseline.size):
                raise RadxaUSBError("FUSE backing size/type does not match the verified baseline")
            state["fuse_backing_size"] = int(metadata.st_size)
            _radxa_usb_atomic_json(state_path, state)
            if (
                _radxa_usb_fuse_helper_status(
                    state,
                    owned_process=helper_process,
                    process_probe=process_probe,
                )
                != "owned"
            ):
                raise RadxaUSBError("FUSE helper exited after mount readiness")
            return mount
        if time.monotonic() >= deadline:
            raise RadxaUSBError(f"FUSE helper PID {pid} did not mount before timeout")
        sleep(SERVER_POLL_SECONDS)


def _radxa_usb_create_gadget(
    plan: RadxaUSBPlan,
    state: dict[str, object],
    state_path: Path,
) -> None:
    """Create and configure the unique configfs gadget tree."""
    gadget = plan.gadget_path
    _radxa_usb_assert_safe_path(plan.configfs_root)
    if gadget.exists() or gadget.is_symlink():
        raise RadxaUSBError(f"refusing to adopt existing gadget path: {gadget}")
    _radxa_usb_mkdir_owned(gadget)
    metadata = gadget.lstat()
    state["gadget_created"] = True
    state["gadget_phase"] = "directory_created"
    state["gadget_dev"] = int(metadata.st_dev)
    state["gadget_ino"] = int(metadata.st_ino)
    _radxa_usb_atomic_json(state_path, state)
    for default_directory in (
        gadget / "strings",
        gadget / "configs",
        gadget / "functions",
    ):
        _radxa_usb_ensure_owned_directory(default_directory)
    _radxa_usb_mkdir_owned(gadget / "strings" / "0x409")
    _radxa_usb_write_text(
        gadget / "strings" / "0x409" / "serialnumber",
        str(state["gadget_identity"]),
    )
    state["gadget_phase"] = "identity_written"
    _radxa_usb_atomic_json(state_path, state)
    _radxa_usb_mkdir_owned(gadget / "configs" / "c.1")
    _radxa_usb_ensure_owned_directory(gadget / "configs" / "c.1" / "strings")
    _radxa_usb_mkdir_owned(gadget / "configs" / "c.1" / "strings" / "0x409")
    _radxa_usb_mkdir_owned(gadget / "functions" / "mass_storage.0")
    function = gadget / "functions" / "mass_storage.0"
    _radxa_usb_ensure_owned_directory(function / "lun.0")
    _radxa_usb_write_text(gadget / "idVendor", USB_VENDOR_ID)
    _radxa_usb_write_text(gadget / "idProduct", USB_PRODUCT_ID)
    _radxa_usb_write_text(gadget / "bcdUSB", "0x0200")
    _radxa_usb_write_text(gadget / "bcdDevice", USB_RELEASE)
    _radxa_usb_write_text(
        gadget / "strings" / "0x409" / "manufacturer", USB_MANUFACTURER
    )
    _radxa_usb_write_text(gadget / "strings" / "0x409" / "product", USB_PRODUCT)
    _radxa_usb_write_text(
        gadget / "configs" / "c.1" / "strings" / "0x409" / "configuration",
        USB_CONFIGURATION,
    )
    _radxa_usb_write_text(
        gadget / "configs" / "c.1" / "MaxPower", USB_MAX_POWER_MA
    )
    _radxa_usb_write_text(function / "stall", "1")
    _radxa_usb_write_text(function / "lun.0" / "removable", "1")
    requested_ro = "1" if plan.backing_kind == "fuse-direct" else "0"
    _radxa_usb_write_text(function / "lun.0" / "ro", requested_ro)
    _radxa_usb_write_text(function / "lun.0" / "cdrom", "0")
    _radxa_usb_write_text(
        function / "lun.0" / "file", str(plan.backing_path)
    )
    effective_ro = _radxa_usb_read_text(function / "lun.0" / "ro")
    if plan.backing_kind == "fuse-direct" and effective_ro != "1":
        raise RadxaUSBError(
            f"FUSE-backed mass storage did not remain read-only: lun.ro={effective_ro!r}"
        )
    state["fuse_lun_ro"] = effective_ro if plan.backing_kind == "fuse-direct" else None
    link = gadget / "configs" / "c.1" / "mass_storage.0"
    # Linux configfs resolves a function link through its configfs item, not as
    # an ordinary filesystem-relative symlink.  The Radxa kernel rejected the
    # relative target with ENOENT; the canonical absolute configfs item works.
    link.symlink_to(function)
    state["gadget_phase"] = "configured"
    _radxa_usb_atomic_json(state_path, state)


def _radxa_usb_rmdir_if_exact(path: Path, errors: list[str]) -> None:
    """Remove one expected directory while refusing symlinks."""
    try:
        if path.is_symlink():
            errors.append(f"refusing to remove unexpected symlink: {path}")
        elif path.is_dir():
            path.rmdir()
        elif path.exists():
            errors.append(f"refusing to remove unexpected non-directory: {path}")
    except OSError as exc:
        errors.append(f"could not remove directory {path}: {exc}")


def _radxa_usb_try_rmdir(path: Path) -> OSError | None:
    """Try one exact directory removal and return its error without recording it."""
    try:
        if path.is_symlink():
            return OSError(errno.ELOOP, "refusing to remove unexpected symlink", path)
        if path.is_dir():
            path.rmdir()
        elif path.exists():
            return OSError(errno.ENOTDIR, "unexpected non-directory", path)
        return None
    except OSError as exc:
        return exc


def _radxa_usb_remove_composite_dir(
    path: Path,
    fallback_children: Sequence[Path],
    errors: list[str],
) -> None:
    """Remove a configfs item, then empty fixture-only default groups as fallback."""
    first_error = _radxa_usb_try_rmdir(path)
    if first_error is None:
        return
    for child in fallback_children:
        _radxa_usb_try_rmdir(child)
    retry_error = _radxa_usb_try_rmdir(path)
    if retry_error is not None:
        errors.append(f"could not remove directory {path}: {retry_error}")


def _radxa_usb_unlink_owned_file(path: Path, errors: list[str]) -> None:
    """Remove a fixture file, ignoring configfs' non-unlinkable attributes."""
    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.exists():
            errors.append(f"refusing to remove unexpected non-file: {path}")
    except OSError as exc:
        if exc.errno not in {
            errno.EACCES,
            errno.EINVAL,
            errno.ENOTSUP,
            errno.EPERM,
        }:
            errors.append(f"could not remove file {path}: {exc}")


def _radxa_usb_remove_gadget(
    configfs_root: Path, gadget_name: str, errors: list[str]
) -> None:
    """Remove only the known gadget tree created by this tool."""
    gadget = configfs_root / gadget_name
    if not gadget.exists() and not gadget.is_symlink():
        return
    udc_file = gadget / "UDC"
    try:
        if udc_file.is_file() and _radxa_usb_read_text(udc_file):
            _radxa_usb_write_text(udc_file, "")
    except OSError as exc:
        errors.append(f"could not unbind UDC: {exc}")
    link = gadget / "configs" / "c.1" / "mass_storage.0"
    try:
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            errors.append(f"refusing to remove unexpected link target: {link}")
    except OSError as exc:
        errors.append(f"could not remove function link {link}: {exc}")
    for owned_file in (
        gadget / "configs" / "c.1" / "strings" / "0x409" / "configuration",
        gadget / "configs" / "c.1" / "MaxPower",
        gadget / "functions" / "mass_storage.0" / "stall",
        gadget / "functions" / "mass_storage.0" / "lun.0" / "removable",
        gadget / "functions" / "mass_storage.0" / "lun.0" / "ro",
        gadget / "functions" / "mass_storage.0" / "lun.0" / "cdrom",
        gadget / "functions" / "mass_storage.0" / "lun.0" / "file",
        gadget / "strings" / "0x409" / "serialnumber",
        gadget / "strings" / "0x409" / "manufacturer",
        gadget / "strings" / "0x409" / "product",
        gadget / "idVendor",
        gadget / "idProduct",
        gadget / "bcdUSB",
        gadget / "bcdDevice",
        gadget / "UDC",
    ):
        _radxa_usb_unlink_owned_file(owned_file, errors)
    for directory in (
        gadget / "configs" / "c.1" / "strings" / "0x409",
        gadget / "strings" / "0x409",
    ):
        _radxa_usb_rmdir_if_exact(directory, errors)
    config = gadget / "configs" / "c.1"
    _radxa_usb_remove_composite_dir(
        config, (config / "strings",), errors
    )
    function = gadget / "functions" / "mass_storage.0"
    _radxa_usb_remove_composite_dir(
        function, (function / "lun.0",), errors
    )
    _radxa_usb_remove_composite_dir(
        gadget,
        (
            gadget / "strings",
            gadget / "configs",
            gadget / "functions",
        ),
        errors,
    )


def _radxa_usb_state_value(state: Mapping[str, object], key: str, kind: type):
    """Return one required typed state value."""
    value = state.get(key)
    if not isinstance(value, kind):
        raise RadxaUSBError(f"state has invalid {key}")
    return value


def _radxa_usb_state_backing_kind(state: Mapping[str, object]) -> str:
    """Resolve v5 transport while treating only v4 as legacy raw NBD."""
    schema = state.get("schema")
    if schema == LEGACY_STATE_SCHEMA_V4:
        return "nbd"
    if schema != STATE_SCHEMA:
        raise RadxaUSBError("unsupported arm-state schema")
    backing_kind = state.get("backing_kind")
    if backing_kind not in BACKING_KINDS:
        raise RadxaUSBError(f"state has invalid backing kind: {backing_kind!r}")
    return str(backing_kind)


def _radxa_usb_live_identity(device: RadxaUSBNbdDevice) -> dict[str, object]:
    """Return the live evidence that distinguishes one NBD connection."""
    metadata = device.sysfs_path.lstat()
    return {
        "device_path": str(device.device_path),
        "sysfs_path": str(device.sysfs_path),
        "sysfs_dev": int(metadata.st_dev),
        "sysfs_ino": int(metadata.st_ino),
        "pid": device.pid,
        "holders": list(device.holders),
    }


def _radxa_usb_checkpoint(
    state: dict[str, object], state_path: Path, step: str
) -> None:
    """Persist one completed teardown transition before continuing."""
    cleanup = state.setdefault("cleanup", {})
    if not isinstance(cleanup, dict):
        raise RadxaUSBError("state cleanup record is not an object")
    cleanup[step] = True
    _radxa_usb_atomic_json(state_path, state)


def _radxa_usb_cleanup_flags(state: Mapping[str, object]) -> dict[str, bool]:
    """Validate cleanup flags, adding FUSE-only checkpoints to legacy v4."""
    value = state.get("cleanup")
    if not isinstance(value, dict):
        raise RadxaUSBError("state has no cleanup progress record")
    flags: dict[str, bool] = {}
    schema = state.get("schema")
    legacy = schema == LEGACY_STATE_SCHEMA_V4
    backing_kind = "nbd" if legacy else state.get("backing_kind")
    names = ["udc_unbound", "nbd_detached", "gadget_removed"]
    if not legacy:
        names.extend(("fuse_unmounted", "fuse_helper_stopped"))
    names.append("nbdkit_stopped")
    for name in names:
        if not isinstance(value.get(name), bool):
            raise RadxaUSBError(f"state cleanup flag is invalid: {name}")
        flags[name] = bool(value[name])
    if legacy or backing_kind == "nbd":
        flags["fuse_unmounted"] = True
        flags["fuse_helper_stopped"] = True
    elif backing_kind == "fuse-direct":
        flags["nbd_detached"] = True
    else:
        raise RadxaUSBError(f"state has invalid backing kind: {backing_kind!r}")
    return flags


def radxa_usb_cleanup_started(state: Mapping[str, object]) -> bool:
    """Return whether relevant cleanup checkpoints have begun for this transport."""
    kind = _radxa_usb_state_backing_kind(state)
    flags = _radxa_usb_cleanup_flags(state)
    names = ["udc_unbound", "gadget_removed", "nbdkit_stopped"]
    names += ["nbd_detached"] if kind == "nbd" else ["fuse_unmounted", "fuse_helper_stopped"]
    return any(flags[name] for name in names)


def _radxa_usb_validate_gadget_identity(
    state: Mapping[str, object],
    *,
    require_udc_unbound: bool = False,
) -> Path | None:
    """Validate the owned gadget identity and backing device without mutation."""
    configfs = Path(str(_radxa_usb_state_value(state, "configfs_root", str)))
    gadget_name = str(_radxa_usb_state_value(state, "gadget_name", str))
    identity = str(_radxa_usb_state_value(state, "gadget_identity", str))
    if not SAFE_NAME_RE.fullmatch(gadget_name) or len(identity) < 8:
        raise RadxaUSBError("state contains unsafe gadget identity")
    _radxa_usb_assert_safe_path(configfs)
    gadget = configfs / gadget_name
    _radxa_usb_assert_safe_path(gadget)
    if not gadget.exists() and not gadget.is_symlink():
        return None
    if gadget.is_symlink() or not gadget.is_dir():
        raise RadxaUSBError(f"gadget path is not a real directory: {gadget}")
    phase = str(_radxa_usb_state_value(state, "gadget_phase", str))
    if phase not in {
        "directory_created",
        "identity_written",
        "configured",
        "attached",
        "removing",
    }:
        raise RadxaUSBError(f"state has invalid gadget phase: {phase}")
    expected_dev = state.get("gadget_dev")
    expected_ino = state.get("gadget_ino")
    metadata = gadget.lstat()
    if (
        not isinstance(expected_dev, int)
        or not isinstance(expected_ino, int)
        or metadata.st_dev != expected_dev
        or metadata.st_ino != expected_ino
    ):
        raise RadxaUSBError("gadget directory inode no longer matches owned state")
    identity_path = gadget / "strings" / "0x409" / "serialnumber"
    if identity_path.is_symlink():
        raise RadxaUSBError("gadget identity file became a symlink")
    live_identity = _radxa_usb_read_text(identity_path)
    if live_identity == "" and phase in ("directory_created", "removing"):
        live_identity = None
    if live_identity is not None and live_identity != identity:
        raise RadxaUSBError("gadget identity no longer matches owned state")
    if live_identity is None and phase not in ("directory_created", "removing"):
        raise RadxaUSBError("gadget identity file is missing")
    config_directory = gadget / "configs" / "c.1"
    function = gadget / "functions" / "mass_storage.0"
    if state.get("schema") == LEGACY_STATE_SCHEMA_V4:
        expected_backing = str(_radxa_usb_state_value(state, "nbd_device", str))
    else:
        expected_backing = str(_radxa_usb_state_value(state, "backing_path", str))
    if phase in ("configured", "attached"):
        _radxa_usb_assert_safe_path(config_directory)
        _radxa_usb_assert_safe_path(function)
        if function.is_symlink() or not function.is_dir():
            raise RadxaUSBError("gadget mass-storage function is not a real directory")
        backing_path = function / "lun.0" / "file"
        if backing_path.is_symlink():
            raise RadxaUSBError("gadget backing file became a symlink")
        backing = _radxa_usb_read_text(backing_path)
        if backing != expected_backing:
            raise RadxaUSBError("gadget backing device no longer matches owned state")
        if state.get("backing_kind") == "fuse-direct" and _radxa_usb_read_text(function / "lun.0" / "ro") != "1":
            raise RadxaUSBError("FUSE gadget is no longer read-only")
        config_link = config_directory / "mass_storage.0"
        if not config_link.is_symlink():
            raise RadxaUSBError("gadget function link is missing")
        if config_link.resolve() != function.resolve():
            raise RadxaUSBError("gadget function link no longer matches owned state")
    else:
        if function.exists() or function.is_symlink():
            _radxa_usb_assert_safe_path(function)
            if function.is_symlink() or not function.is_dir():
                raise RadxaUSBError("partial gadget function has an unsafe type")
            backing_path = function / "lun.0" / "file"
            if backing_path.is_symlink():
                raise RadxaUSBError("partial gadget backing file became a symlink")
            backing = _radxa_usb_read_text(backing_path)
            if backing is not None and backing != expected_backing:
                raise RadxaUSBError("partial gadget backing identity changed")
        config_link = config_directory / "mass_storage.0"
        if config_link.is_symlink():
            if not function.exists() or config_link.resolve() != function.resolve():
                raise RadxaUSBError("partial gadget function link changed")
        elif config_link.exists():
            raise RadxaUSBError("partial gadget function link has an unsafe type")
    udc_path = gadget / "UDC"
    if udc_path.is_symlink():
        raise RadxaUSBError("gadget UDC file became a symlink")
    udc = _radxa_usb_read_text(udc_path) or ""
    expected_udc = str(_radxa_usb_state_value(state, "udc", str))
    if state.get("udc_attached"):
        if udc not in ("", expected_udc):
            raise RadxaUSBError("gadget UDC binding no longer matches owned state")
    elif udc:
        raise RadxaUSBError("gadget unexpectedly acquired a UDC binding")
    if require_udc_unbound and udc:
        raise RadxaUSBError("gadget is still bound after UDC-unbound checkpoint")
    return gadget


def _radxa_usb_unbind_owned_gadget(
    state: dict[str, object],
    *,
    state_path: Path,
) -> None:
    """Fail closed by unbinding only the exact gadget recorded in state.

    This step intentionally does not inspect NBD or nbdkit ownership.  If a
    backend identity changes, the car-facing USB endpoint must still be removed
    immediately while foreign backend resources remain untouched.
    """
    _radxa_usb_state_backing_kind(state)
    if str(_radxa_usb_state_value(state, "state_root", str)) != str(
        state_path.parent
    ):
        raise RadxaUSBError(f"state contains unsafe resource identity: {state_path}")
    flags = _radxa_usb_cleanup_flags(state)
    if flags["udc_unbound"]:
        return
    gadget = _radxa_usb_validate_gadget_identity(
        state,
        require_udc_unbound=False,
    )
    if gadget is not None:
        live_udc = _radxa_usb_read_text(gadget / "UDC") or ""
        expected_udc = str(_radxa_usb_state_value(state, "udc", str))
        if live_udc:
            if not state.get("udc_attached") or live_udc != expected_udc:
                raise RadxaUSBError("refusing to unbind an unknown UDC")
            _radxa_usb_write_text(gadget / "UDC", "")
            if _radxa_usb_read_text(gadget / "UDC"):
                raise RadxaUSBError("UDC did not become unbound")
    _radxa_usb_checkpoint(state, state_path, "udc_unbound")


def _radxa_usb_validate_nbd_identity(
    state: Mapping[str, object],
    *,
    is_block_device: PathChecker,
) -> RadxaUSBNbdDevice | None:
    """Validate the live NBD connection against the post-attach ownership record."""
    if not state.get("nbd_attached"):
        return None
    sysfs_root = Path(str(_radxa_usb_state_value(state, "sysfs_root", str)))
    nbd_name = str(_radxa_usb_state_value(state, "nbd_name", str))
    device_path = Path(str(_radxa_usb_state_value(state, "nbd_device", str)))
    expected = state.get("nbd_live_identity")
    if not isinstance(expected, dict):
        raise RadxaUSBError("state has no post-attach NBD ownership identity")
    live = _radxa_usb_snapshot_nbd(
        sysfs_root=sysfs_root,
        nbd_name=nbd_name,
        device_path=device_path,
        is_block_device=is_block_device,
    )
    if live is None or (not live.pid and not live.holders):
        return None
    if _radxa_usb_live_identity(live) != expected:
        raise RadxaUSBError("NBD connection no longer matches owned state")
    return live


def _radxa_usb_detach_command(state: Mapping[str, object]) -> list[str] | None:
    """Return the exact recorded nbd-client detach command for this device."""
    if not state.get("nbd_attached"):
        return None
    detach = state.get("nbd_client_detach_command")
    expected_device = str(_radxa_usb_state_value(state, "nbd_device", str))
    if (
        not isinstance(detach, list)
        or len(detach) != 3
        or not all(isinstance(item, str) for item in detach)
        or Path(detach[0]).name != "nbd-client"
        or detach[1] != "-d"
        or detach[2] != expected_device
    ):
        raise RadxaUSBError("state has no valid NBD detach command")
    return detach


def _radxa_usb_wait_nbd_detach(
    state: Mapping[str, object],
    *,
    is_block_device: PathChecker,
) -> None:
    """Wait for the owned NBD identity to disappear after command completion."""
    deadline = time.monotonic() + NBD_DETACH_TIMEOUT_SECONDS
    while True:
        if (
            _radxa_usb_validate_nbd_identity(
                state, is_block_device=is_block_device
            )
            is None
        ):
            return
        if time.monotonic() >= deadline:
            raise RadxaUSBError("NBD remained connected after detach")
        time.sleep(SERVER_POLL_SECONDS)


def _radxa_usb_process_status(
    state: Mapping[str, object],
    *,
    owned_process: object | None,
    process_probe: ProcessProbe,
) -> str:
    """Return absent, owned, or mismatch for the recorded nbdkit process."""
    pid_value = state.get("nbdkit_pid")
    plugin_value = state.get("nbdkit_plugin")
    if pid_value is None:
        return "absent"
    if not isinstance(pid_value, int) or pid_value <= 0:
        raise RadxaUSBError("state has invalid nbdkit PID")
    if not isinstance(plugin_value, str):
        raise RadxaUSBError("state has no owned nbdkit plugin path")
    identity = state.get("nbdkit_identity")
    command = state.get("nbdkit_command")
    if owned_process is not None:
        if getattr(owned_process, "pid", None) != pid_value:
            return "mismatch"
        poll = getattr(owned_process, "poll", None)
        if not callable(poll) or poll() is not None:
            return "absent"
        # Before capture completes, retaining the exact Popen object is the
        # strongest available ownership proof and allows safe startup unwind.
        if identity is None:
            return "owned"
    if (
        not isinstance(identity, dict)
        or identity.get("pid") != pid_value
        or not isinstance(identity.get("boot_id"), str)
        or not identity.get("boot_id")
        or type(identity.get("start_ticks")) is not int
        or identity["start_ticks"] <= 0
        or not isinstance(command, list)
        or not command
        or any(not isinstance(arg, str) for arg in command)
        or identity.get("argv") != command
        or plugin_value not in command
        or not isinstance(identity.get("executable"), dict)
    ):
        raise RadxaUSBError("state has invalid nbdkit process-instance identity")
    return process_probe(pid_value, identity)


def _radxa_usb_stop_owned_nbdkit(
    state: dict[str, object],
    *,
    state_path: Path,
    owned_process: object | None,
    process_probe: ProcessProbe,
    process_terminator: ProcessTerminator | None = None,
) -> None:
    """Terminate and verify only the nbdkit process recorded by this attempt."""
    status = _radxa_usb_process_status(
        state,
        owned_process=owned_process,
        process_probe=process_probe,
    )
    if status == "mismatch":
        raise RadxaUSBError("nbdkit PID belongs to a different process")
    if status == "absent":
        _radxa_usb_checkpoint(state, state_path, "nbdkit_stopped")
        return
    if status != "owned":
        raise RadxaUSBError("nbdkit process status is unknown")
    if owned_process is not None:
        owned_process.terminate()
        owned_process.wait(timeout=5)
        status = _radxa_usb_process_status(
            state,
            owned_process=owned_process,
            process_probe=process_probe,
        )
    else:
        pid_value = int(_radxa_usb_state_value(state, "nbdkit_pid", int))
        identity = _radxa_usb_state_value(state, "nbdkit_identity", dict)
        if process_terminator is None:
            _radxa_usb_signal_process_instance(pid_value, identity, process_probe)
        else:
            process_terminator(pid_value)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            status = process_probe(pid_value, identity)
            if status != "owned":
                break
            time.sleep(SERVER_POLL_SECONDS)
    if status == "mismatch":
        raise RadxaUSBError("nbdkit PID changed during cleanup")
    if status != "absent":
        raise RadxaUSBError("nbdkit process did not stop")
    _radxa_usb_checkpoint(state, state_path, "nbdkit_stopped")


def _radxa_usb_unmount_fuse(
    state: dict[str, object],
    *,
    state_path: Path,
    runner: CommandRunner,
) -> None:
    """Unmount only the exact recorded FUSE target; lazy success is forbidden."""
    live = _radxa_usb_validate_fuse_mount(state, required=False)
    if live is None:
        _radxa_usb_checkpoint(state, state_path, "fuse_unmounted")
        return
    if state.get("fuse_mount_identity") is None:
        # A helper can mount just before startup fails. Its unique source and
        # recorded private parent prove ownership before we checkpoint it.
        state["fuse_mount_identity"] = live
        _radxa_usb_atomic_json(state_path, state)
    command = state.get("fuse_unmount_command")
    if (
        not isinstance(command, list)
        or len(command) != 3
        or any(not isinstance(argument, str) for argument in command)
        or Path(command[0]).name != "fusermount3"
        or command[1] != "-u"
        or command[2] != state.get("fuse_mountpoint")
        or command[0] != state.get("fuse_fusermount")
        or "-z" in command
    ):
        raise RadxaUSBError("state has no valid non-lazy FUSE unmount command")
    result = runner(command)
    if result.returncode != 0 and _radxa_usb_validate_fuse_mount(
        state, required=False
    ) is not None:
        _radxa_usb_require_success(command, result)
    deadline = time.monotonic() + FUSE_UNMOUNT_TIMEOUT_SECONDS
    while _radxa_usb_validate_fuse_mount(state, required=False) is not None:
        if time.monotonic() >= deadline:
            raise RadxaUSBError("FUSE mount remained live after unmount")
        time.sleep(SERVER_POLL_SECONDS)
    _radxa_usb_checkpoint(state, state_path, "fuse_unmounted")


def _radxa_usb_stop_fuse_helper(
    state: dict[str, object],
    *,
    state_path: Path,
    owned_process: object | None,
    process_probe: ProcessProbe,
    process_terminator: ProcessTerminator | None = None,
) -> None:
    """Stop only the exact helper instance after its mount has been removed."""
    status = _radxa_usb_fuse_helper_status(
        state,
        owned_process=owned_process,
        process_probe=process_probe,
    )
    if status == "mismatch":
        raise RadxaUSBError("FUSE helper PID belongs to a different process")
    if status == "absent":
        _radxa_usb_checkpoint(state, state_path, "fuse_helper_stopped")
        return
    pid = int(_radxa_usb_state_value(state, "fuse_helper_pid", int))
    if owned_process is not None:
        if state.get("fuse_mount_identity") is None:
            owned_process.terminate()
        owned_process.wait(timeout=5)
        status = _radxa_usb_fuse_helper_status(
            state,
            owned_process=owned_process,
            process_probe=process_probe,
        )
    else:
        identity = _radxa_usb_state_value(state, "fuse_helper_identity", dict)
        if state.get("fuse_mount_identity") is None:
            if process_terminator is None:
                _radxa_usb_signal_process_instance(
                    pid, identity, process_probe, label="FUSE helper"
                )
            else:
                process_terminator(pid)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            status = process_probe(pid, identity)
            if status != "owned":
                break
            time.sleep(SERVER_POLL_SECONDS)
    if status == "mismatch":
        raise RadxaUSBError("FUSE helper PID changed during cleanup")
    if status != "absent":
        raise RadxaUSBError("FUSE helper did not stop")
    _radxa_usb_checkpoint(state, state_path, "fuse_helper_stopped")


def _radxa_usb_remove_fuse_files(state: Mapping[str, object], state_path: Path) -> None:
    """Remove only the unmounted regular stub and this helper's pidfile."""
    directory = Path(str(_radxa_usb_state_value(state, "fuse_mount_directory", str)))
    if directory.exists() or directory.is_symlink():
        _radxa_usb_validate_fuse_directory(state)
        backing = Path(str(_radxa_usb_state_value(state, "backing_path", str)))
        if backing.exists() or backing.is_symlink():
            _radxa_usb_assert_safe_path(backing)
            info = backing.lstat()
            if (not stat.S_ISREG(info.st_mode)
                    or info.st_dev != state.get("fuse_backing_dev")
                    or info.st_ino != state.get("fuse_backing_ino")):
                raise RadxaUSBError("unmounted FUSE stub identity changed")
            backing.unlink()
        directory.rmdir()
    pidfile = state_path.parent / "fuse-helper.pid"
    if pidfile.exists() or pidfile.is_symlink():
        _radxa_usb_assert_safe_path(pidfile)
        info = pidfile.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_size > 128
                or info.st_uid != os.geteuid()
                or pidfile.read_text().strip() != str(state.get("fuse_helper_pid"))):
            raise RadxaUSBError("FUSE pidfile identity changed")
        pidfile.unlink()


def _radxa_usb_attach_attempt(
    plan: RadxaUSBPlan, current_nbd: RadxaUSBNbdDevice
) -> dict[str, object]:
    """Record the exact free device and command immediately before attach."""
    metadata = current_nbd.sysfs_path.lstat()
    return {
        "device_path": str(current_nbd.device_path),
        "sysfs_path": str(current_nbd.sysfs_path.resolve(strict=True)),
        "sysfs_dev": int(metadata.st_dev),
        "sysfs_ino": int(metadata.st_ino),
        "pre_pid": current_nbd.pid,
        "pre_holders": list(current_nbd.holders),
        "command": list(plan.nbd_client_attach_command),
    }


def _radxa_usb_classify_attach_result(
    plan: RadxaUSBPlan,
    state: Mapping[str, object],
    *,
    is_block_device: PathChecker,
    succeeded: bool = False,
) -> RadxaUSBNbdDevice | None:
    """Only a successful command and matching post-state can claim an NBD."""
    attempt = state.get("nbd_attempt")
    if not isinstance(attempt, dict):
        raise RadxaUSBError(
            "reconciliation required: pre-attach identity checkpoint is missing"
        )
    if (
        attempt.get("device_path") != str(plan.nbd_device.device_path)
        or attempt.get("pre_pid") is not None
        or attempt.get("pre_holders") != []
    ):
        raise RadxaUSBError(
            "reconciliation required: pre-attach identity checkpoint is invalid"
        )
    live = _radxa_usb_snapshot_nbd(
        sysfs_root=plan.sysfs_root,
        nbd_name=plan.nbd_device.name,
        device_path=plan.nbd_device.device_path,
        is_block_device=is_block_device,
    )
    if live is None or live.free:
        return None
    if not succeeded:
        # NBD/sysfs inodes persist across clients; a new PID can be a foreign
        # claimant racing after our free checkpoint, including on interruption.
        raise RadxaUSBError(
            "reconciliation required: failed attach has ambiguous NBD identity"
        )
    metadata = live.sysfs_path.lstat()
    if (
        str(live.device_path) != attempt.get("device_path")
        or str(live.sysfs_path) != attempt.get("sysfs_path")
        or int(metadata.st_dev) != attempt.get("sysfs_dev")
        or int(metadata.st_ino) != attempt.get("sysfs_ino")
        or not live.pid
        or live.holders
        or not live.block_device
    ):
        raise RadxaUSBError(
            "reconciliation required: failed attach has ambiguous NBD identity"
        )
    return live


def _radxa_usb_preserve_reconciliation(
    state: dict[str, object],
    *,
    state_path: Path,
    reason: str,
    owned_process: object | None,
    process_probe: ProcessProbe,
) -> RadxaUSBReconciliationRequired:
    """Persist ambiguity and stop only the owned server without touching NBD."""
    state["nbd_phase"] = "reconciliation_required"
    state["reconciliation_required"] = {
        "phase": "nbd_attach",
        "reason": reason,
    }
    _radxa_usb_atomic_json(state_path, state)
    cleanup_error: str | None = None
    try:
        _radxa_usb_stop_owned_nbdkit(
            state,
            state_path=state_path,
            owned_process=owned_process,
            process_probe=process_probe,
        )
    except (OSError, RadxaUSBError, subprocess.SubprocessError) as exc:
        cleanup_error = str(exc)
    suffix = f"; nbdkit cleanup failed: {cleanup_error}" if cleanup_error else ""
    return RadxaUSBReconciliationRequired(
        f"{reason}; state preserved at {state_path}{suffix}"
    )


def _radxa_usb_cleanup(
    state: dict[str, object],
    *,
    state_path: Path,
    runner: CommandRunner,
    is_block_device: PathChecker = _radxa_usb_default_is_block,
    owned_process: object | None = None,
    owned_fuse_process: object | None = None,
    process_probe: ProcessProbe = _radxa_usb_default_process_probe,
    process_terminator: ProcessTerminator | None = None,
) -> list[str]:
    """Preflight and checkpoint an ownership-safe teardown."""
    try:
        backing_kind = _radxa_usb_state_backing_kind(state)
    except RadxaUSBError as exc:
        return [f"refusing to use unknown state schema in {state_path}: {exc}"]
    if state.get("reconciliation_required"):
        return [
            f"reconciliation required before teardown: {state_path}; "
            f"{state.get('reconciliation_required')}"
        ]
    if str(_radxa_usb_state_value(state, "state_root", str)) != str(
        state_path.parent
    ):
        return [f"state contains unsafe resource identity: {state_path}"]
    try:
        flags = _radxa_usb_cleanup_flags(state)
        configfs_path = Path(
            str(_radxa_usb_state_value(state, "configfs_root", str))
        )
        recorded_gadget = configfs_path / str(
            _radxa_usb_state_value(state, "gadget_name", str)
        )
        _radxa_usb_assert_safe_path(configfs_path)
        _radxa_usb_assert_safe_path(recorded_gadget)
        if not flags["gadget_removed"]:
            gadget = _radxa_usb_validate_gadget_identity(
                state, require_udc_unbound=flags["udc_unbound"]
            )
        else:
            gadget = None
            if recorded_gadget.exists() or recorded_gadget.is_symlink():
                raise RadxaUSBError("gadget exists after gadget-removed checkpoint")
        if backing_kind == "nbd":
            nbd_live = _radxa_usb_validate_nbd_identity(
                state, is_block_device=is_block_device
            )
            _radxa_usb_detach_command(state)
            if flags["nbd_detached"] and nbd_live is not None:
                raise RadxaUSBError("NBD is connected after detached checkpoint")
        else:
            fuse_status = _radxa_usb_fuse_helper_status(
                state,
                owned_process=owned_fuse_process,
                process_probe=process_probe,
            )
            if fuse_status == "mismatch":
                raise RadxaUSBError("FUSE helper PID belongs to a different process")
            if flags["fuse_helper_stopped"] and fuse_status == "owned":
                raise RadxaUSBError("FUSE helper is live after stopped checkpoint")
            fuse_mount = _radxa_usb_validate_fuse_mount(state, required=False)
            if flags["fuse_unmounted"] and fuse_mount is not None:
                raise RadxaUSBError("FUSE mount is live after unmounted checkpoint")
        process_status = _radxa_usb_process_status(
            state,
            owned_process=owned_process,
            process_probe=process_probe,
        )
        if process_status == "mismatch":
            raise RadxaUSBError("nbdkit PID belongs to a different process")
        if process_status not in ("absent", "owned"):
            raise RadxaUSBError("nbdkit process status is unknown")
        if flags["nbdkit_stopped"]:
            if process_status == "owned":
                raise RadxaUSBError("nbdkit is live after stopped checkpoint")
    except (OSError, RadxaUSBError) as exc:
        return [str(exc)]

    errors: list[str] = []
    if not flags["udc_unbound"]:
        try:
            _radxa_usb_unbind_owned_gadget(state, state_path=state_path)
            flags["udc_unbound"] = True
        except (OSError, RadxaUSBError) as exc:
            errors.append(f"UDC teardown failed: {exc}")

    if not flags["gadget_removed"] and errors == []:
        try:
            gadget = _radxa_usb_validate_gadget_identity(
                state, require_udc_unbound=True
            )
            if gadget is not None:
                state["gadget_phase"] = "removing"
                _radxa_usb_atomic_json(state_path, state)
                _radxa_usb_remove_gadget(
                    Path(str(_radxa_usb_state_value(state, "configfs_root", str))),
                    str(_radxa_usb_state_value(state, "gadget_name", str)),
                    errors,
                )
                if gadget.exists() or gadget.is_symlink():
                    raise RadxaUSBError("gadget still exists after removal")
            _radxa_usb_checkpoint(state, state_path, "gadget_removed")
            flags["gadget_removed"] = True
        except (OSError, RadxaUSBError) as exc:
            errors.append(f"gadget teardown failed: {exc}")

    # Closing the configfs backing handle must precede NBD detach. Linux
    # rejects the NBD capacity reset while configfs still has the device open.
    if (
        backing_kind == "nbd"
        and not flags["nbd_detached"]
        and errors == []
    ):
        if state.get("nbd_attached"):
            try:
                detach = _radxa_usb_detach_command(state)
                current = _radxa_usb_validate_nbd_identity(
                    state, is_block_device=is_block_device
                )
                if current is None:
                    _radxa_usb_checkpoint(state, state_path, "nbd_detached")
                    flags["nbd_detached"] = True
                else:
                    assert detach is not None
                    result = runner(detach)
                    if result.returncode != 0:
                        retry = _radxa_usb_validate_nbd_identity(
                            state, is_block_device=is_block_device
                        )
                        if retry is not None:
                            _radxa_usb_require_success(detach, result)
                    _radxa_usb_wait_nbd_detach(
                        state, is_block_device=is_block_device
                    )
                    _radxa_usb_checkpoint(state, state_path, "nbd_detached")
                    flags["nbd_detached"] = True
            except (OSError, RadxaUSBError) as exc:
                errors.append(f"NBD teardown failed: {exc}")
        else:
            try:
                _radxa_usb_checkpoint(state, state_path, "nbd_detached")
                flags["nbd_detached"] = True
            except OSError as exc:
                errors.append(f"NBD checkpoint failed: {exc}")

    if backing_kind == "fuse-direct" and errors == []:
        if not flags["fuse_unmounted"]:
            try:
                _radxa_usb_unmount_fuse(
                    state, state_path=state_path, runner=runner
                )
                flags["fuse_unmounted"] = True
            except (OSError, RadxaUSBError) as exc:
                errors.append(f"FUSE unmount failed: {exc}")
        if not flags["fuse_helper_stopped"] and errors == []:
            try:
                _radxa_usb_stop_fuse_helper(
                    state,
                    state_path=state_path,
                    owned_process=owned_fuse_process,
                    process_probe=process_probe,
                    process_terminator=process_terminator,
                )
                flags["fuse_helper_stopped"] = True
            except (OSError, RadxaUSBError, subprocess.SubprocessError) as exc:
                errors.append(f"FUSE helper teardown failed: {exc}")

    if not flags["nbdkit_stopped"] and errors == []:
        try:
            _radxa_usb_stop_owned_nbdkit(
                state,
                state_path=state_path,
                owned_process=owned_process,
                process_probe=process_probe,
                process_terminator=process_terminator,
            )
            flags["nbdkit_stopped"] = True
        except (OSError, RadxaUSBError, subprocess.SubprocessError) as exc:
            errors.append(f"nbdkit teardown failed: {exc}")

    if errors:
        return errors
    if backing_kind == "fuse-direct":
        try:
            _radxa_usb_remove_fuse_files(state, state_path)
        except (OSError, RadxaUSBError) as exc:
            return [f"FUSE files could not be released: {exc}"]
    if state.get("state_dir_created"):
        for owned_log in ("nbdkit.log", "reads.log"):
            try:
                (state_path.parent / owned_log).unlink()
            except FileNotFoundError:
                pass
            except OSError as exc:
                errors.append(f"could not remove owned log {owned_log}: {exc}")
    if errors:
        return errors
    try:
        state_path.unlink()
    except FileNotFoundError:
        pass
    except OSError as exc:
        errors.append(f"could not remove state file {state_path}: {exc}")
    if state.get("state_dir_created") and not errors:
        try:
            state_path.parent.rmdir()
        except FileNotFoundError:
            pass
        except OSError as exc:
            errors.append(
                f"could not remove state directory {state_path.parent}: {exc}"
            )
    return errors


def _radxa_usb_health(
    state: Mapping[str, object],
    *,
    owned_process: object | None,
    owned_fuse_process: object | None = None,
    process_probe: ProcessProbe,
    is_block_device: PathChecker,
) -> dict[str, object]:
    """Validate every live component required to keep USB safely exposed."""
    backing_kind = _radxa_usb_state_backing_kind(state)
    if radxa_usb_cleanup_started(state):
        raise RadxaUSBError("armed state has already entered teardown")
    if state.get("gadget_phase") != "attached" or not state.get("udc_attached"):
        raise RadxaUSBError("USB gadget is not recorded as attached")
    if backing_kind == "nbd" and (
        state.get("nbd_phase") != "attached" or not state.get("nbd_attached")
    ):
        raise RadxaUSBError("NBD backend is not recorded as attached")
    process_status = _radxa_usb_process_status(
        state,
        owned_process=owned_process,
        process_probe=process_probe,
    )
    if process_status != "owned":
        raise RadxaUSBError(f"nbdkit backend is {process_status}")
    if backing_kind == "nbd":
        nbd = _radxa_usb_validate_nbd_identity(
            state,
            is_block_device=is_block_device,
        )
        if nbd is None:
            raise RadxaUSBError("owned NBD connection disappeared")
        backing_detail: dict[str, object] = {
            "nbd_name": str(_radxa_usb_state_value(state, "nbd_name", str)),
            "nbd_device": str(_radxa_usb_state_value(state, "nbd_device", str)),
            "nbd_live_identity": _radxa_usb_state_value(
                state, "nbd_live_identity", dict
            ),
        }
        backing_path = str(_radxa_usb_state_value(state, "nbd_device", str))
    else:
        helper_status = _radxa_usb_fuse_helper_status(
            state,
            owned_process=owned_fuse_process,
            process_probe=process_probe,
        )
        if helper_status != "owned":
            raise RadxaUSBError(f"FUSE helper is {helper_status}")
        mount = _radxa_usb_validate_fuse_mount(state)
        assert mount is not None
        backing_path = str(_radxa_usb_state_value(state, "backing_path", str))
        backing_detail = {
            "helper_pid": int(_radxa_usb_state_value(state, "fuse_helper_pid", int)),
            "helper_identity": _radxa_usb_state_value(
                state, "fuse_helper_identity", dict
            ),
            "mountpoint": str(_radxa_usb_state_value(state, "fuse_mountpoint", str)),
            "fsname": str(_radxa_usb_state_value(state, "fuse_fsname", str)),
            "mount_id": int(mount["mount_id"]),
            "fstype": str(mount["fstype"]),
            "readonly": True,
            "lun_ro": str(_radxa_usb_state_value(state, "fuse_lun_ro", str)),
            "backing_size": int(_radxa_usb_state_value(state, "fuse_backing_size", int)),
        }
    gadget = _radxa_usb_validate_gadget_identity(state)
    if gadget is None:
        raise RadxaUSBError("owned USB gadget disappeared")
    live_udc = _radxa_usb_read_text(gadget / "UDC") or ""
    expected_udc = str(_radxa_usb_state_value(state, "udc", str))
    if live_udc != expected_udc:
        raise RadxaUSBError("owned USB gadget is no longer bound to its UDC")
    result: dict[str, object] = {
        "armed": True,
        "ready": True,
        "healthy": True,
        "backing_kind": backing_kind,
        "backing_path": backing_path,
        "backing_detail": backing_detail,
        "nbdkit_pid": int(_radxa_usb_state_value(state, "nbdkit_pid", int)),
        "udc": expected_udc,
        "gadget": str(gadget),
    }
    if backing_kind == "nbd":
        result["nbd_device"] = backing_path
    return result


def radxa_usb_status(
    *,
    state_root: str | Path = DEFAULT_STATE_ROOT,
    process_probe: ProcessProbe = _radxa_usb_default_process_probe,
    is_block_device: PathChecker = _radxa_usb_default_is_block,
) -> dict[str, object]:
    """Return live health, rejecting stale JSON as an armed state."""
    root = Path(state_root).expanduser().resolve()
    state_path = root / "state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RadxaUSBError("update media is not armed") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RadxaUSBError(f"could not read arm state: {exc}") from exc
    if not isinstance(state, dict):
        raise RadxaUSBError("arm state must be a JSON object")
    if str(_radxa_usb_state_value(state, "state_root", str)) != str(root):
        raise RadxaUSBError("arm state root does not match the requested state")
    health = _radxa_usb_health(
        state,
        owned_process=None,
        process_probe=process_probe,
        is_block_device=is_block_device,
    )
    health["state_path"] = str(state_path)
    return health


def radxa_usb_sd_notify(message: str) -> bool:
    """Send one native systemd notification without a helper-process race."""
    target = os.environ.get("NOTIFY_SOCKET")
    if not target:
        return False
    if target.startswith("@"):
        address = "\0" + target[1:]
    elif target.startswith("/"):
        address = target
    else:
        raise RadxaUSBError("NOTIFY_SOCKET is neither absolute nor abstract")
    payload = message.encode("utf-8")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        sock.connect(address)
        written = sock.send(payload)
    except OSError as exc:
        raise RadxaUSBError(f"could not notify systemd: {exc}") from exc
    finally:
        sock.close()
    if written != len(payload):
        raise RadxaUSBError("systemd notification was truncated")
    return True


def _radxa_usb_preserve_supervisor_failure(
    armed: RadxaUSBArmed,
    *,
    reason: str,
    errors: Sequence[str],
) -> None:
    """Persist a health failure when complete ownership-safe cleanup cannot finish."""
    if not armed.state_path.exists():
        return
    armed.state["reconciliation_required"] = {
        "phase": "supervisor_health",
        "reason": reason,
        "cleanup_errors": list(errors),
    }
    _radxa_usb_atomic_json(armed.state_path, armed.state)


def radxa_usb_supervise(
    armed: RadxaUSBArmed,
    *,
    stop_requested: CancelChecker,
    runner: CommandRunner = radxa_usb_run_command,
    process_probe: ProcessProbe = _radxa_usb_default_process_probe,
    is_block_device: PathChecker = _radxa_usb_default_is_block,
    notify: NotifySender = radxa_usb_sd_notify,
    sleep: Callable[[float], None] = time.sleep,
    poll_seconds: float = SUPERVISOR_POLL_SECONDS,
) -> dict[str, object]:
    """Keep the Python parent alive and fail closed if any backend dies."""
    if poll_seconds <= 0:
        raise RadxaUSBError("supervisor poll interval must be positive")
    try:
        health = _radxa_usb_health(
            armed.state,
            owned_process=armed.nbdkit_process,
            owned_fuse_process=armed.fuse_helper_process,
            process_probe=process_probe,
            is_block_device=is_block_device,
        )
        # A stop can arrive after the final arming checkpoint but before this
        # function starts. Never advertise readiness for an already-stopping run.
        if not stop_requested():
            notify("READY=1\nSTATUS=IONIQ update media ready")
        while not stop_requested():
            sleep(poll_seconds)
            if stop_requested():
                break
            health = _radxa_usb_health(
                armed.state,
                owned_process=armed.nbdkit_process,
                owned_fuse_process=armed.fuse_helper_process,
                process_probe=process_probe,
                is_block_device=is_block_device,
            )
    except (OSError, RadxaUSBError, subprocess.SubprocessError) as exc:
        reason = str(exc)
        fail_closed_errors: list[str] = []
        try:
            _radxa_usb_unbind_owned_gadget(
                armed.state,
                state_path=armed.state_path,
            )
        except (OSError, RadxaUSBError) as unbind_exc:
            fail_closed_errors.append(f"emergency UDC unbind failed: {unbind_exc}")
        fail_closed_errors.extend(
            _radxa_usb_cleanup(
                armed.state,
                state_path=armed.state_path,
                runner=runner,
                is_block_device=is_block_device,
                owned_process=armed.nbdkit_process,
                owned_fuse_process=armed.fuse_helper_process,
                process_probe=process_probe,
            )
        )
        if fail_closed_errors:
            _radxa_usb_preserve_supervisor_failure(
                armed,
                reason=reason,
                errors=fail_closed_errors,
            )
        detail = "; ".join(fail_closed_errors)
        suffix = f"; cleanup incomplete: {detail}" if detail else ""
        raise RadxaUSBError(f"supervisor health failure: {reason}{suffix}") from exc

    try:
        notify("STOPPING=1\nSTATUS=Stopping IONIQ update media")
    except RadxaUSBError:
        # Notification is best-effort once teardown has been requested.
        pass
    cleanup_errors = _radxa_usb_cleanup(
        armed.state,
        state_path=armed.state_path,
        runner=runner,
        is_block_device=is_block_device,
        owned_process=armed.nbdkit_process,
        owned_fuse_process=armed.fuse_helper_process,
        process_probe=process_probe,
    )
    if cleanup_errors:
        try:
            _radxa_usb_unbind_owned_gadget(
                armed.state,
                state_path=armed.state_path,
            )
        except (OSError, RadxaUSBError) as unbind_exc:
            cleanup_errors.append(f"emergency UDC unbind failed: {unbind_exc}")
        _radxa_usb_preserve_supervisor_failure(
            armed,
            reason="cooperative stop cleanup failed",
            errors=cleanup_errors,
        )
        raise RadxaUSBError(
            "supervisor teardown incomplete: " + "; ".join(cleanup_errors)
        )
    return {"stopped": True, "last_health": health}


def radxa_usb_arm(
    plan: RadxaUSBPlan,
    *,
    execute: bool = False,
    runner: CommandRunner = radxa_usb_run_command,
    process_starter: ProcessStarter = subprocess.Popen,
    process_identity_capture: ProcessIdentityCapture = _radxa_usb_capture_process_identity,
    process_probe: ProcessProbe = _radxa_usb_default_process_probe,
    port_probe: Callable[[str, int], None] = _radxa_usb_wait_for_port,
    is_block_device: PathChecker = _radxa_usb_default_is_block,
    cancel_requested: CancelChecker | None = None,
) -> RadxaUSBArmed | RadxaUSBPlan:
    """Arm the complete chain, or return the plan when ``execute`` is false."""
    _radxa_usb_check_cancelled(cancel_requested)
    if not plan.ready:
        raise RadxaUSBError("arm plan is not ready: " + "; ".join(plan.issues))
    if not execute:
        return plan
    state_root = plan.state_root
    state_path = state_root / "state.json"
    state_dir_created = False
    if state_root.exists():
        raise RadxaUSBError(f"refusing to adopt existing state root: {state_root}")
    if not state_root.parent.is_dir():
        raise RadxaUSBError(f"state parent is unavailable: {state_root.parent}")
    state_root.mkdir(mode=0o700)
    state_dir_created = True
    process = None
    fuse_process = None
    gadget_identity = f"{USB_SERIAL_PREFIX}-{secrets.token_hex(8)}"
    state = _radxa_usb_state_document(
        plan,
        gadget_identity=gadget_identity,
        gadget_created=False,
        nbd_attached=False,
        udc_attached=False,
        nbdkit_pid=None,
        state_dir_created=state_dir_created,
    )
    try:
        _radxa_usb_verify_bound_content(
            plan.bound_content,
            cancel_requested=cancel_requested,
        )
        _radxa_usb_check_cancelled(cancel_requested)
        _radxa_usb_atomic_json(state_path, state)
        try:
            process = process_starter(
                list(plan.nbdkit_command),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                close_fds=True,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise RadxaUSBError(f"could not start nbdkit: {exc}") from exc
        pid = int(process.pid)
        state["nbdkit_pid"] = pid
        _radxa_usb_atomic_json(state_path, state)
        port_probe(plan.nbd_host, plan.nbd_port)
        _radxa_usb_check_cancelled(cancel_requested)
        identity = process_identity_capture(pid)
        if identity.get("pid") != pid or identity.get("argv") != list(plan.nbdkit_command):
            raise RadxaUSBError("started nbdkit does not match its expected command")
        state["nbdkit_identity"] = identity
        _radxa_usb_atomic_json(state_path, state)
        _radxa_usb_check_cancelled(cancel_requested)

        if plan.backing_kind == "fuse-direct":
            _radxa_usb_preflight_fuse_helper(plan.fuse_helper)
            assert plan.fuse_mount_directory is not None
            plan.fuse_mount_directory.mkdir(mode=0o700)
            parent_info = plan.fuse_mount_directory.lstat()
            state["fuse_mount_dir_dev"] = parent_info.st_dev
            state["fuse_mount_dir_ino"] = parent_info.st_ino
            # A regular stub selects nbdfuse file-mount mode; its private
            # parent stays outside FUSE for nonblocking ownership checks.
            fd = os.open(plan.backing_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                stub = os.fstat(fd)
                state["fuse_backing_dev"] = stub.st_dev
                state["fuse_backing_ino"] = stub.st_ino
            finally:
                os.close(fd)
            _radxa_usb_atomic_json(state_path, state)
            _radxa_usb_check_cancelled(cancel_requested)
            fuse_process = process_starter(
                list(plan.fuse_helper_command), stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                start_new_session=True, close_fds=True,
            )
            state["fuse_helper_pid"] = int(fuse_process.pid)
            _radxa_usb_atomic_json(state_path, state)
            state["fuse_helper_identity"] = _radxa_usb_capture_started_process(
                fuse_process, command=plan.fuse_helper_command,
                capture=process_identity_capture, process_probe=process_probe,
                cancel_requested=cancel_requested,
            )
            _radxa_usb_atomic_json(state_path, state)
            _radxa_usb_wait_for_fuse_ready(
                plan, state, state_path, helper_process=fuse_process,
                process_probe=process_probe, cancel_requested=cancel_requested,
            )
        else:
            current_nbd = _radxa_usb_snapshot_nbd(
                sysfs_root=plan.sysfs_root,
                nbd_name=plan.nbd_device.name,
                device_path=plan.nbd_device.device_path,
                is_block_device=is_block_device,
            )
            if current_nbd is None:
                raise RadxaUSBError(
                    f"selected NBD device disappeared: {plan.nbd_device.name}"
                )
            if not current_nbd.free:
                raise RadxaUSBError(
                    "selected NBD device was claimed after planning: "
                    + str(current_nbd.occupancy_reason())
                )
            state["nbd_phase"] = "attach_pending"
            state["nbd_attempt"] = _radxa_usb_attach_attempt(plan, current_nbd)
            _radxa_usb_atomic_json(state_path, state)
            try:
                result = runner(plan.nbd_client_attach_command)
            except BaseException as exc:
                classification_error: str | None = None
                try:
                    _radxa_usb_classify_attach_result(
                        plan, state, is_block_device=is_block_device
                    )
                except (OSError, RadxaUSBError) as identity_exc:
                    classification_error = str(identity_exc)
                if classification_error:
                    reconciliation = _radxa_usb_preserve_reconciliation(
                        state,
                        state_path=state_path,
                        reason=classification_error,
                        owned_process=process,
                        process_probe=process_probe,
                    )
                    if not isinstance(exc, Exception):
                        exc.add_note(str(reconciliation))
                        raise
                    raise reconciliation from exc
                raise
            if result.returncode != 0:
                try:
                    _radxa_usb_classify_attach_result(
                        plan, state, is_block_device=is_block_device
                    )
                except (OSError, RadxaUSBError) as identity_exc:
                    raise _radxa_usb_preserve_reconciliation(
                        state,
                        state_path=state_path,
                        reason=str(identity_exc),
                        owned_process=process,
                        process_probe=process_probe,
                    ) from identity_exc
                state["nbd_phase"] = "attach_failed"
                _radxa_usb_atomic_json(state_path, state)
                _radxa_usb_require_success(
                    plan.nbd_client_attach_command, result
                )
            try:
                attached_nbd = _radxa_usb_classify_attach_result(
                    plan, state, is_block_device=is_block_device, succeeded=True
                )
            except (OSError, RadxaUSBError) as identity_exc:
                raise _radxa_usb_preserve_reconciliation(
                    state,
                    state_path=state_path,
                    reason=str(identity_exc),
                    owned_process=process,
                    process_probe=process_probe,
                ) from identity_exc
            if attached_nbd is None:
                raise RadxaUSBError(
                    "nbd-client succeeded without observable NBD ownership"
                )
            state["nbd_live_identity"] = _radxa_usb_live_identity(attached_nbd)
            state["nbd_attached"] = True
            state["nbd_phase"] = "attached"
            _radxa_usb_atomic_json(state_path, state)

        _radxa_usb_check_cancelled(cancel_requested)
        _radxa_usb_create_gadget(plan, state, state_path)
        _radxa_usb_verify_bound_content(
            plan.bound_content,
            cancel_requested=cancel_requested,
        )
        _radxa_usb_check_cancelled(cancel_requested)
        try:
            _radxa_usb_write_text(plan.gadget_path / "UDC", plan.udc)
        except OSError:
            if _radxa_usb_read_text(plan.gadget_path / "UDC") == plan.udc:
                state["udc_attached"] = True
                _radxa_usb_atomic_json(state_path, state)
            raise
        state["udc_attached"] = True
        state["gadget_phase"] = "attached"
        _radxa_usb_atomic_json(state_path, state)
        _radxa_usb_check_cancelled(cancel_requested)
        return RadxaUSBArmed(
            plan=plan,
            state_path=state_path,
            nbdkit_pid=pid,
            nbdkit_process=process,
            state=state,
            fuse_helper_pid=state["fuse_helper_pid"],
            fuse_helper_process=fuse_process,
        )
    except RadxaUSBReconciliationRequired:
        raise
    except BaseException as exc:
        try:
            cleanup_errors = _radxa_usb_cleanup(
                state,
                state_path=state_path,
                runner=runner,
                is_block_device=is_block_device,
                owned_process=process,
                owned_fuse_process=fuse_process,
                process_probe=process_probe,
            )
        except BaseException as cleanup_exc:
            cleanup_errors = [f"cleanup raised {type(cleanup_exc).__name__}: {cleanup_exc}"]
        detail = "; ".join(cleanup_errors)
        if not isinstance(exc, Exception):
            if detail and hasattr(exc, "add_note"):
                exc.add_note(f"USB cleanup also failed: {detail}")
            raise
        if detail:
            raise RadxaUSBError(f"{exc}; cleanup also failed: {detail}") from exc
        if isinstance(exc, RadxaUSBError):
            raise
        raise RadxaUSBError(str(exc)) from exc


def radxa_usb_teardown(
    *,
    state_root: str | Path = DEFAULT_STATE_ROOT,
    execute: bool = False,
    runner: CommandRunner = radxa_usb_run_command,
    is_block_device: PathChecker = _radxa_usb_default_is_block,
    process_probe: ProcessProbe = _radxa_usb_default_process_probe,
    process_terminator: ProcessTerminator | None = None,
) -> dict[str, object]:
    """Inspect or execute ownership-safe teardown from the state file."""
    root = Path(state_root).expanduser().resolve()
    state_path = root / "state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {
            "execute": execute,
            "state_path": str(state_path),
            "removed": False,
            "already_absent": True,
        }
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RadxaUSBError(f"could not read arm state: {exc}") from exc
    if not isinstance(state, dict):
        raise RadxaUSBError("arm state must be a JSON object")
    if not execute:
        return {"execute": False, "state_path": str(state_path), "state": state}
    errors = _radxa_usb_cleanup(
        state,
        state_path=state_path,
        runner=runner,
        is_block_device=is_block_device,
        process_probe=process_probe,
        process_terminator=process_terminator,
    )
    if errors:
        raise RadxaUSBError("teardown incomplete: " + "; ".join(errors))
    return {"execute": True, "state_path": str(state_path), "removed": True}


def _radxa_usb_add_common_paths(parser: argparse.ArgumentParser) -> None:
    """Add injected/system root options shared by CLI commands."""
    parser.add_argument("--sysfs-root", default=str(DEFAULT_SYSFS_ROOT))
    parser.add_argument("--dev-root", default=str(DEFAULT_DEV_ROOT))
    parser.add_argument("--configfs-root", default=str(DEFAULT_CONFIGFS_ROOT))
    parser.add_argument("--proc-root", default=str(DEFAULT_PROC_ROOT))
    parser.add_argument("--state-root", default=str(DEFAULT_STATE_ROOT))
    parser.add_argument("--gadget-name", default=DEFAULT_GADGET_NAME)


def _radxa_usb_json(value: object) -> None:
    """Print deterministic JSON suitable for review or recording."""
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def radxa_usb_main(argv: Sequence[str] | None = None) -> int:
    """Run the Radxa adapter command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_parser = sub.add_parser("inspect", help="report board and resource state")
    _radxa_usb_add_common_paths(inspect_parser)
    inspect_parser.add_argument("--json", action="store_true")
    inspect_parser.add_argument("--backing-kind", choices=sorted(BACKING_KINDS), default="nbd")

    plan_parser = sub.add_parser("plan", help="validate inputs and print an arm plan")
    _radxa_usb_add_common_paths(plan_parser)
    plan_parser.add_argument("--serve-plan", required=True)
    plan_parser.add_argument("--backing-kind", choices=sorted(BACKING_KINDS), default="nbd")
    plan_parser.add_argument("--udc")
    plan_parser.add_argument("--nbd")
    plan_parser.add_argument("--nbd-host", default=DEFAULT_NBD_HOST)
    plan_parser.add_argument("--nbd-port", type=int, default=DEFAULT_NBD_PORT)
    plan_parser.add_argument("--json", action="store_true")
    plan_parser.add_argument("--validation-cache", help="reuse prepared local content")

    arm_parser = sub.add_parser(
        "arm", help="arm the gadget (dry-run unless --execute is supplied)"
    )
    _radxa_usb_add_common_paths(arm_parser)
    arm_parser.add_argument("--serve-plan", required=True)
    arm_parser.add_argument("--backing-kind", choices=sorted(BACKING_KINDS), default="nbd")
    arm_parser.add_argument("--udc")
    arm_parser.add_argument("--nbd")
    arm_parser.add_argument("--nbd-host", default=DEFAULT_NBD_HOST)
    arm_parser.add_argument("--nbd-port", type=int, default=DEFAULT_NBD_PORT)
    arm_parser.add_argument("--execute", action="store_true")
    arm_parser.add_argument(
        "--hold",
        action="store_true",
        help="remain as the supervising parent until stopped",
    )
    arm_parser.add_argument("--json", action="store_true")
    arm_parser.add_argument("--validation-cache", help="require unchanged prepared local content")

    prepare_parser = sub.add_parser("prepare", help="verify content once for fast future starts")
    prepare_parser.add_argument("--serve-plan", required=True)
    prepare_parser.add_argument("--validation-cache", required=True)
    prepare_parser.add_argument("--force", action="store_true", help="rehash even unchanged files")

    teardown_parser = sub.add_parser(
        "teardown", help="tear down only resources recorded as owned"
    )
    teardown_parser.add_argument("--state-root", default=str(DEFAULT_STATE_ROOT))
    teardown_parser.add_argument("--execute", action="store_true")
    teardown_parser.add_argument("--json", action="store_true")

    status_parser = sub.add_parser(
        "status", help="validate live backend, NBD, gadget, and UDC health"
    )
    status_parser.add_argument("--state-root", default=str(DEFAULT_STATE_ROOT))
    status_parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    stop_state = {"requested": False, "phase": "planning"}
    previous_handlers: dict[int, object] = {}
    cache_token = None

    def request_stop(signum: int, _frame: object) -> None:
        """Cancel planning immediately, then cooperate once resources exist."""
        stop_state["requested"] = True
        if stop_state["phase"] == "planning":
            raise RadxaUSBCancelled(f"received signal {signum} before arming")

    if args.command == "arm" and args.hold:
        if not args.execute:
            parser.error("--hold requires --execute")
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, request_stop)

    try:
        if getattr(args, "validation_cache", None):
            cache = _RadxaUSBValidationCache(Path(args.validation_cache),
                                            prepare=args.command == "prepare",
                                            force=getattr(args, "force", False))
            cache_token = _VALIDATION_CACHE.set(cache)
        if args.command == "prepare":
            content = _radxa_usb_load_bound_content(args.serve_plan)
            cache.save()
            print(f"prepared: {content.baseline.path.name}; unchanged content is ready for fast starts")
            return 0
        if args.command == "inspect":
            inspection = radxa_usb_inspect(
                backing_kind=args.backing_kind,
                sysfs_root=args.sysfs_root,
                dev_root=args.dev_root,
                configfs_root=args.configfs_root,
                proc_root=args.proc_root,
                state_root=args.state_root,
                gadget_name=args.gadget_name,
            )
            if args.json:
                _radxa_usb_json(inspection.to_dict())
            else:
                print(f"board: {inspection.board_model or 'unknown'}")
                print(f"platform: {inspection.platform} {inspection.kernel_release}")
                print(f"root: {'yes' if inspection.effective_uid == 0 else 'no'}")
                print(f"UDCs: {', '.join(inspection.udcs) or 'none'}")
                for device in inspection.nbd_devices:
                    print(
                        f"NBD {device.name}: {device.device_path} "
                        f"({'free' if device.free else device.occupancy_reason()})"
                    )
                for issue in inspection.issues:
                    print(f"issue: {issue}")
            return 0 if not inspection.issues else 1

        if args.command in ("plan", "arm"):
            plan = radxa_usb_build_plan(
                serve_plan=args.serve_plan,
                backing_kind=args.backing_kind,
                udc=args.udc,
                nbd_device=args.nbd,
                nbd_host=args.nbd_host,
                nbd_port=args.nbd_port,
                sysfs_root=args.sysfs_root,
                dev_root=args.dev_root,
                configfs_root=args.configfs_root,
                proc_root=args.proc_root,
                state_root=args.state_root,
                gadget_name=args.gadget_name,
            )
            if not plan.ready:
                raise RadxaUSBError("plan is not ready: " + "; ".join(plan.issues))
            if args.command == "plan":
                result: object = plan
            else:
                if args.hold:
                    stop_state["phase"] = "arming"
                result = radxa_usb_arm(
                    plan,
                    execute=args.execute,
                    cancel_requested=(
                        (lambda: bool(stop_state["requested"]))
                        if args.hold
                        else None
                    ),
                )
                if args.hold:
                    if not isinstance(result, RadxaUSBArmed):
                        raise AssertionError("hold mode did not execute arming")
                    stop_state["phase"] = "supervising"
                    supervised = radxa_usb_supervise(
                        result,
                        stop_requested=lambda: bool(stop_state["requested"]),
                    )
                else:
                    supervised = None
            if isinstance(result, RadxaUSBArmed):
                payload = {
                    "state_path": str(result.state_path),
                    "nbdkit_pid": result.nbdkit_pid,
                    "plan": result.plan.to_dict(),
                }
                if supervised is not None:
                    payload["supervisor"] = supervised
            elif isinstance(result, RadxaUSBPlan):
                payload = {
                    "execute": False,
                    "plan": result.to_dict(),
                }
            else:
                raise AssertionError("unexpected arm result")
            if args.json:
                _radxa_usb_json(payload)
            else:
                print(
                    f"{'armed' if isinstance(result, RadxaUSBArmed) else 'dry-run'}: "
                    f"UDC={plan.udc} backing={plan.backing_kind}:{plan.backing_path} "
                    f"port={plan.nbd_port}"
                )
                if isinstance(result, RadxaUSBArmed):
                    print(f"state: {result.state_path}")
            return 0

        if args.command == "status":
            result = radxa_usb_status(state_root=args.state_root)
            if args.json:
                _radxa_usb_json(result)
            else:
                print(
                    "update media healthy: "
                    f"runtime={TOOL_VERSION} PID={result['nbdkit_pid']} "
                    f"backing={result['backing_kind']}:{result['backing_path']} "
                    f"UDC={result['udc']}"
                )
            return 0

        if args.command == "teardown":
            result = radxa_usb_teardown(
                state_root=args.state_root,
                execute=args.execute,
            )
            if args.json:
                _radxa_usb_json(result)
            else:
                print(
                    "removed owned resources"
                    if result.get("removed")
                    else "already absent"
                    if result.get("already_absent")
                    else (
                        "dry-run: state loaded; pass --execute to remove "
                        "owned resources"
                    )
                )
            return 0
        raise AssertionError(f"unhandled command: {args.command}")
    except RadxaUSBCancelled as exc:
        if stop_state["requested"]:
            print(f"radxa_usb: {exc}", file=sys.stderr)
            return 0
        print(f"radxa_usb: {exc}", file=sys.stderr)
        return 2
    except RadxaUSBError as exc:
        print(f"radxa_usb: {exc}", file=sys.stderr)
        return 2
    finally:
        if cache_token is not None:
            _VALIDATION_CACHE.reset(cache_token)
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)


if __name__ == "__main__":
    raise SystemExit(radxa_usb_main())
