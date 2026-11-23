"""Prepare and operate one private, snapshot-backed Gen5W workbench VM."""

from __future__ import annotations

import argparse
from contextlib import suppress
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Optional, Tuple
import webbrowser

from . import vm_workbench_version
from .guest_shell import GuestShell
from .runtime import WorkbenchRuntime
from .server import WorkbenchHTTPServer
from .service import WorkbenchServiceBackend
from .transport import GuestMailbox, SimulatorMailbox

PROJECT = Path(__file__).resolve().parents[3]
# The portable server never uses the legacy preparation path. Keep that path
# explicitly configurable instead of embedding a developer-only sibling name in
# the public source package.
RESEARCH = Path(os.environ.get("GEN5W_LEGACY_RESEARCH", PROJECT / ".gen5w/legacy-research"))
BASE = RESEARCH / "work/vm/vendor-userspace-260128"
RECIPE = RESEARCH / "vm/repro/vendor-userspace-260128/micom-contract/full-chain-timeout120-legal-reason11-llvmpipe-home-settle.sh"
ZIG = RESEARCH / "work/toolchains/zig-macos-aarch64-0.13.0/zig"
GUEST_DBUS = RESEARCH / "work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/libdbus-1.so.3"
DBUS_INC = Path("/opt/homebrew/include/dbus-1.0")
DBUS_ARCH_INC = Path("/opt/homebrew/lib/dbus-1.0/include")
DEBUGFS = Path("/opt/homebrew/opt/e2fsprogs/sbin/debugfs")
QEMU = Path("/opt/homebrew/bin/qemu-system-x86_64")
OUTPUT = PROJECT / "work/vm/interactive-hardware-simulation-20261116/runtime"
FAILURE_VISIBILITY_SECONDS = 30.0
BASE_HASH = "4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f"
PROBE_SOURCE_HASH = "e8328c25e9c1acb35f7ec0461b5f987461488c411ed86ed6b2d538a3c51d1f14"
PROBE_SCRIPT_HASH = "d76bceca7b3306cae364fe67a826d15ba4de8305555fd893d65ca17e22ef3678"
RECIPE_HASH = "25a2ee9726d160c03b52c8dc3c5a76aaba33dd57d7d4be7ecba6f9b2f34485ae"
VM_INIT = """#!/bin/busybox sh
# VM-only supervisor: a console EOF must not terminate guest PID 1.
BB=/bin/busybox
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/app/bin
$BB mkdir -p /rw_data/var/run/user/root /rw_data/var/log /rw_data/var/tmp
$BB mount -t proc proc /proc
$BB mount -t sysfs sysfs /sys
$BB mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
$BB mount -t tmpfs tmpfs /run
$BB mount -t tmpfs tmpfs /tmp
$BB mkdir -p /sys/fs/smackfs /run/user/root /var/run/user/root
$BB mount -t smackfs smackfs /sys/fs/smackfs 2>/dev/null || true
echo IONIQ_VM_USERSPACE_READY
echo IONIQ_VENDOR_USERSPACE_READY
export PS1='ioniq-vendor# '
while true; do
  $BB sh
  echo WORKBENCH_CONSOLE_RESTARTED
  $BB sleep 1
done
"""


def vm_workbench_hash(path: Path) -> str:
    """Hash an existing local artifact without loading it into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def vm_workbench_prerequisites() -> None:
    """Validate exact retained artifacts and show missing paths before writing."""
    required = [QEMU, DEBUGFS, ZIG, GUEST_DBUS, DBUS_INC / "dbus/dbus.h",
                DBUS_ARCH_INC / "dbus/dbus-arch-deps.h", RECIPE,
                *(BASE / name for name in ("prepare.json", "bzImage", "rootfs.img", "manifest.bin", "seed_dev.bin", "seed_user.bin"))]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing workbench prerequisites: " + ", ".join(missing))
    if vm_workbench_hash(RECIPE) != RECIPE_HASH:
        raise ValueError("retained startup recipe hash mismatch: " + str(RECIPE))
    if vm_workbench_hash(BASE / "rootfs.img") != BASE_HASH:
        raise ValueError("retained base rootfs hash mismatch: " + str(BASE / "rootfs.img"))


def vm_workbench_prepare(destination: Path, frame_probe: bool = False) -> Path:
    """Build guest helpers and inject them into a new APFS clone only."""
    destination = Path(destination).resolve()
    if destination.parent != OUTPUT.resolve() or destination.exists():
        raise ValueError("workspace must be a new direct child of " + str(OUTPUT))
    vm_workbench_prerequisites()
    destination.mkdir(parents=True)
    build = destination / "build"
    build.mkdir()
    for name in ("bzImage", "manifest.bin", "seed_dev.bin", "seed_user.bin", "prepare.json"):
        shutil.copy2(BASE / name, destination / name)
    subprocess.run(["/bin/cp", "-c", str(BASE / "rootfs.img"), str(destination / "rootfs.img")], check=True)
    environment = {**os.environ, "ZIG": str(ZIG), "DBUS_INC": str(DBUS_INC),
                   "DBUS_ARCH_INC": str(DBUS_ARCH_INC), "GUEST_LIBDBUS": str(GUEST_DBUS),
                   "PYTHON": "/usr/bin/python3", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"}
    helpers = [("build-weston-vm-input.sh", "weston-vm-input.so"),
               ("build-eng-data-sim.sh", "eng-data-sim")]
    if frame_probe:
        if (vm_workbench_hash(PROJECT / "tools/uk_fw/guest/weston_ivi_frame_probe.c") != PROBE_SOURCE_HASH or
                vm_workbench_hash(PROJECT / "tools/uk_fw/guest/build-weston-ivi-frame-probe.sh") != PROBE_SCRIPT_HASH):
            raise ValueError("pinned frame-probe source or build script mismatch")
        helpers.append(("build-weston-ivi-frame-probe.sh", "weston-ivi-frame-probe.so"))
    for script, name in helpers:
        subprocess.run(["/bin/sh", str(PROJECT / "tools/uk_fw/guest" / script)], cwd=PROJECT,
                       env={**environment, "OUT": str(build / name)}, check=True)
    shutil.copy2(PROJECT / "tools/uk_fw/guest/launch-vm-workbench.sh", build / "launch-vm-workbench.sh")
    (build / "init-workbench").write_text(VM_INIT, encoding="ascii")
    commands = []
    injected = [name for _, name in helpers] + ["launch-vm-workbench.sh"]
    for name in injected:
        commands += ["rm /" + name, "write " + name + " /" + name,
                     "set_inode_field /" + name + " mode 0100755"]
    commands += ["rm /init", "write init-workbench /init", "set_inode_field /init mode 0100755"]
    # debugfs treats the cwd-relative source names as single tokens even when
    # the enclosing project path contains spaces.
    command_file = build / "inject.cmds"
    command_file.write_text("\n".join(commands) + "\n", encoding="ascii")
    result = subprocess.run([str(DEBUGFS), "-w", "-f", str(command_file), str(destination / "rootfs.img")],
                            cwd=build, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    (build / "debugfs.log").write_text(result.stdout, encoding="utf-8")
    for name in injected + ["init"]:
        check = subprocess.run([str(DEBUGFS), "-R", "stat /" + name, str(destination / "rootfs.img")],
                               text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        if "Type: regular" not in check.stdout or "0755" not in check.stdout:
            raise RuntimeError("debugfs injection verification failed for " + name)
    metadata = json.loads((destination / "prepare.json").read_text())
    metadata["sha256"]["rootfs.img"] = vm_workbench_hash(destination / "rootfs.img")
    if frame_probe:
        metadata["workbench_frame_probe"] = {"source_sha256": PROBE_SOURCE_HASH,
                                             "script_sha256": PROBE_SCRIPT_HASH,
                                             "helper_sha256": vm_workbench_hash(build / "weston-ivi-frame-probe.so"),
                                             "rootfs_sha256": metadata["sha256"]["rootfs.img"]}
    (destination / "prepare.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return destination


def vm_workbench_prepare_portable(workspace: Path, config, *,
                                  progress: Optional[Callable[[str, int, str], None]] = None) -> Path:
    """Build and inject the public workbench helpers into one admitted workspace.

    The caller has already copied and hash-verified the user-supplied inputs. This
    stage uses only discovered host tools and paths inside that private workspace.
    """

    from .platform_config import platform_config_require

    platform_config_require(config)
    workspace = Path(workspace).resolve()
    runtime_root = Path(config.runtime_dir).resolve()
    if (workspace.parent != runtime_root or not workspace.is_dir() or workspace.is_symlink()
            or stat.S_IMODE(workspace.stat().st_mode) != 0o700
            or workspace.stat().st_uid != os.geteuid()):
        raise ValueError("portable workspace must be a private direct runtime child")
    build = workspace / "build"
    build.mkdir(mode=0o700)
    if progress:
        progress("helpers", 46, "Building pinned guest helpers")
    tools = (config.python, config.zig, config.debugfs, config.shell, config.file_tool)
    tool_dirs = tuple(dict.fromkeys(str(Path(tool).parent) for tool in tools if tool is not None))
    system_path = tuple(path for path in ("/usr/bin", "/bin", "/usr/sbin", "/sbin")
                        if Path(path).is_dir())
    environment = {**os.environ, "ZIG": str(config.zig),
                   "DBUS_INC": str(config.dbus_inc),
                   "DBUS_ARCH_INC": str(config.dbus_arch_inc),
                   "GUEST_LIBDBUS": str(workspace / "libdbus-1.so.3"),
                   "PYTHON": str(config.python),
                   "PATH": os.pathsep.join(dict.fromkeys(tool_dirs + system_path))}
    helpers = (("build-weston-vm-input.sh", "weston-vm-input.so"),
               ("build-eng-data-sim.sh", "eng-data-sim"),
               ("build-weston-ivi-frame-probe.sh", "weston-ivi-frame-probe.so"))
    if (vm_workbench_hash(PROJECT / "tools/uk_fw/guest/weston_ivi_frame_probe.c") != PROBE_SOURCE_HASH or
            vm_workbench_hash(PROJECT / "tools/uk_fw/guest/build-weston-ivi-frame-probe.sh") != PROBE_SCRIPT_HASH):
        raise ValueError("pinned frame-probe source or build script mismatch")
    for script, name in helpers:
        subprocess.run([str(config.shell), str(PROJECT / "tools/uk_fw/guest" / script)],
                       cwd=PROJECT, env={**environment, "OUT": str(build / name)}, check=True)
    shutil.copy2(PROJECT / "tools/uk_fw/guest/launch-vm-workbench.sh",
                 build / "launch-vm-workbench.sh")
    (build / "init-workbench").write_text(VM_INIT, encoding="ascii")
    injected = [name for _, name in helpers] + ["launch-vm-workbench.sh"]
    commands = []
    for name in injected:
        commands += ["rm /" + name, "write " + name + " /" + name,
                     "set_inode_field /" + name + " mode 0100755"]
    commands += ["rm /init", "write init-workbench /init", "set_inode_field /init mode 0100755"]
    command_file = build / "inject.cmds"
    command_file.write_text("\n".join(commands) + "\n", encoding="ascii")
    if progress:
        progress("helpers", 48, "Injecting helpers into the private snapshot source")
    result = subprocess.run([str(config.debugfs), "-w", "-f", str(command_file),
                             str(workspace / "rootfs.img")], cwd=build, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    (build / "debugfs.log").write_text(result.stdout, encoding="utf-8")
    for name in injected + ["init"]:
        check = subprocess.run([str(config.debugfs), "-R", "stat /" + name,
                                str(workspace / "rootfs.img")], text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        if "Type: regular" not in check.stdout or "0755" not in check.stdout:
            raise RuntimeError("debugfs injection verification failed for " + name)
    metadata = json.loads((workspace / "prepare.json").read_text(encoding="utf-8"))
    metadata["sha256"]["rootfs.img"] = vm_workbench_hash(workspace / "rootfs.img")
    metadata["workbench_frame_probe"] = {
        "source_sha256": PROBE_SOURCE_HASH,
        "script_sha256": PROBE_SCRIPT_HASH,
        "helper_sha256": vm_workbench_hash(build / "weston-ivi-frame-probe.so"),
        "rootfs_sha256": metadata["sha256"]["rootfs.img"],
    }
    temporary = workspace / "prepare.json.next"
    temporary.write_text(json.dumps(metadata, indent=2) + "\n", encoding="ascii")
    os.chmod(temporary, 0o600)
    os.replace(temporary, workspace / "prepare.json")
    if progress:
        progress("helpers", 50, "Portable workspace preparation passed")
    return workspace


def vm_workbench_prepare_public(asset_directory: Path, *, wifi_sim: bool,
                                progress: Callable[[str, int, str], None]):
    """Admit local assets and return one portable backend preparation tuple."""

    from .assets import assets_admit, assets_copy_workspace, assets_manifest
    from .platform_config import platform_config_discover, platform_config_require

    config = platform_config_discover(PROJECT)
    platform_config_require(config, wifi_sim=wifi_sim)
    for directory in (config.state_dir, config.runtime_dir):
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = directory.lstat()
        if (not stat.S_ISDIR(info.st_mode) or directory.is_symlink()
                or info.st_uid != os.geteuid()):
            raise PermissionError("Gen5W state directories must be locally owned directories")
        os.chmod(directory, 0o700)

    def scaled_progress(stage: str, start: int, finish: int):
        names = tuple(assets_manifest(wifi_sim=wifi_sim)["files"])
        indexes = {name: index for index, name in enumerate(names)}
        last = [start]

        def update(name: str, done: int, total: int) -> None:
            index = indexes.get(name, 0)
            ratio = (index + (done / total if total else 0)) / max(1, len(names))
            value = max(last[0], min(finish, start + int((finish - start) * ratio)))
            if value > last[0] or done == 0:
                last[0] = value
                progress(stage, value, f"{stage.title()}: {name} ({done:,}/{total:,} bytes)")
        return update

    def workspace_progress():
        """Map physical copy and digest verification into one monotonic stage."""
        names = tuple(assets_manifest(wifi_sim=wifi_sim)["files"])
        indexes = {name: index for index, name in enumerate(names)}
        count = max(1, len(names))
        last_percent = [25]
        last_bytes: dict[tuple[str, str], int] = {}

        def update(phase: str, name: str, done: int, total: int) -> None:
            index = indexes.get(name, 0)
            member_ratio = done / total if total else 0
            half = 0 if phase == "Copying" else .5
            ratio = (index + half + .5 * member_ratio) / count
            value = max(last_percent[0], min(44, 25 + int(19 * ratio)))
            key = (phase, name)
            previous = last_bytes.get(key, -1)
            # Keep long 32 GiB copies visibly alive without flooding the event log.
            byte_step = 256 * 1024 * 1024
            visible = (value > last_percent[0] or done == 0 or done == total
                       or previous < 0 or done - previous >= byte_step)
            if visible:
                last_percent[0] = value
                last_bytes[key] = done
                progress("workspace", value,
                         f"{phase}: {name} ({done:,}/{total:,} bytes)")

        return (lambda name, done, total: update("Copying", name, done, total),
                lambda name, done, total: update("Verifying", name, done, total))

    progress("assets", 5, "Verifying the compatible local asset manifest")
    admitted = assets_admit(asset_directory, wifi_sim=wifi_sim,
                            progress=scaled_progress("assets", 5, 24))
    session = config.runtime_dir / ("session-" + str(time.time_ns()))
    workspace = None
    try:
        progress("workspace", 25, "Copying admitted assets into private state")
        copy_progress, verify_progress = workspace_progress()
        workspace = assets_copy_workspace(admitted, config.runtime_dir, session,
                                          progress=verify_progress,
                                          copy_progress=copy_progress)
        vm_workbench_prepare_portable(workspace, config, progress=progress)
        wifi_simulation = None
        if wifi_sim:
            from .wifi_sim.integration import (SIM_TARGET_SHA256, wifi_sim_build_target,
                                               wifi_sim_checked_bytes)
            from .wifi_sim.session import wifi_sim_load_assets
            assets = wifi_sim_load_assets(workspace / "wifi-sim",
                                          Path(__file__).with_name("wifi_sim") /
                                          "0001-vm-only-wifi-simulated-banner.patch")
            target = workspace / "build" / "wifi-sim"
            wifi_sim_build_target(Path(__file__).with_name("wifi_sim") / "wifi_sim.c",
                                  target, config.musl_cc)
            wifi_simulation = (assets, wifi_sim_checked_bytes(target, SIM_TARGET_SHA256),
                               config.magick)
        return workspace, wifi_simulation, config.qemu
    except BaseException:
        if workspace is not None and workspace.parent == config.runtime_dir and workspace.exists():
            shutil.rmtree(workspace)
        raise


class KeyboardTapBackend:
    """Adapt browser keydown/up to one bounded guest key tap per release."""

    def __init__(self, runtime: WorkbenchRuntime):
        self._runtime, self._pressed, self._lock = runtime, set(), threading.Lock()

    def __getattr__(self, name):
        return getattr(self._runtime, name)

    def send_key(self, *, action, key, correlation_id=None):
        from .contracts import CommandReceipt
        from .transport import vm_transport_identifier, vm_transport_key
        vm_transport_key(action, key)
        with self._lock:
            if action == "press":
                command_id = vm_transport_identifier(correlation_id)
                if key in self._pressed:
                    return CommandReceipt(command_id, False, "duplicate", "key already held", time.time_ns())
                self._pressed.add(key)
                return CommandReceipt(command_id, True, "pending", "tap occurs on release", time.time_ns())
            if action == "release":
                if key not in self._pressed:
                    return CommandReceipt(vm_transport_identifier(correlation_id), False, "error", "key was not pressed", time.time_ns())
                self._pressed.remove(key)
                action = "tap"
            return self._runtime.send_key(action=action, key=key, correlation_id=correlation_id)


class _ManagedWorkbenchBackend:
    """Transfer runtime, bridge and capture cleanup as one backend owner."""

    def __init__(self, backend, runtime: WorkbenchRuntime, shell: GuestShell):
        self._backend, self._runtime, self._shell = backend, runtime, shell
        self._stop = threading.Event()
        self._capture_thread = None
        self._server = None
        self._unexpected_exit = threading.Event()
        self._close_lock = threading.Lock()
        self._closed = False
        self.simulation_mode = bool(getattr(backend, "simulation_mode", False))

    def __getattr__(self, name):
        return getattr(self._backend, name)

    def start_capture(self, server=None, *, defer_unexpected_shutdown: bool = False) -> None:
        """Start the sole compositor capture loop after backend admission."""

        if type(defer_unexpected_shutdown) is not bool:
            raise TypeError("defer_unexpected_shutdown must be a boolean")
        with self._close_lock:
            if self._closed or self._capture_thread is not None:
                raise RuntimeError("capture lifecycle cannot be started")
            self._server = server
            unexpected_exit = self._unexpected_exit if defer_unexpected_shutdown else None
            thread = threading.Thread(target=vm_workbench_capture_loop,
                                      args=(self._stop, self._runtime, lambda: self._shell, server,
                                            unexpected_exit),
                                      name="workbench-capture", daemon=True)
            self._capture_thread = thread
            thread.start()

    def vm_workbench_wait_runtime_stop(self, timeout: float) -> bool:
        """Wait for an admitted runtime to stop without an operator request."""

        return self._unexpected_exit.wait(timeout)

    def vm_workbench_runtime_stopped_unexpectedly(self) -> bool:
        """Report a post-admission runtime loss separately from normal Stop."""

        return self._unexpected_exit.is_set()

    def close(self) -> None:
        """Stop and reap only this session's capture, QEMU and bridge."""

        with self._close_lock:
            if self._closed:
                return
            self._closed = True
            self._stop.set()
            thread = self._capture_thread
        self._runtime.shutdown()
        if thread is not None:
            thread.join(timeout=5)
        self._shell.close()

    def shutdown(self):
        """Preserve the existing receipt and complete owned cleanup."""

        receipt = self._backend.shutdown()
        self.close()
        shutdown = getattr(self._server, "shutdown", None)
        if callable(shutdown):
            shutdown()
        return receipt


def vm_workbench_spawn(argv, *, run_dir, event, process_factory=None, bridge_type=None, **kwargs):
    """Create a child and bridge, retaining cleanup ownership until adoption.

    A partially initialized bridge is kept reachable so its reader/log can be
    closed if construction fails after opening the log or starting its thread.
    """
    factory = process_factory or subprocess.Popen
    bridge_class = bridge_type or GuestShell
    kwargs["stdout"] = subprocess.PIPE
    kwargs["stderr"] = subprocess.STDOUT
    process = factory(argv, **kwargs)
    bridge = None
    try:
        bridge = bridge_class.__new__(bridge_class)
        bridge_class.__init__(bridge, process, Path(run_dir) / "serial.log", event)
        return process, bridge
    except BaseException:
        # The runtime has not adopted this child yet; only this scope can reap it.
        if process.poll() is None:
            with suppress(OSError):
                process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            with suppress(OSError):
                process.kill()
            with suppress(subprocess.TimeoutExpired, OSError):
                process.wait(timeout=5)
        except OSError:
            pass
        finally:
            reader = getattr(bridge, "_reader", None)
            if reader is not None:
                with suppress(RuntimeError):
                    reader.join(timeout=5)
            for name in ("stdin", "stdout", "stderr"):
                stream = getattr(process, name, None)
                if stream is not None:
                    with suppress(OSError, ValueError):
                        stream.close()
            log = getattr(bridge, "_log", None)
            if log is not None:
                with suppress(OSError, ValueError):
                    log.close()
        raise


def vm_workbench_foreground_prerequisites(shell: GuestShell, runtime: WorkbenchRuntime) -> None:
    """Require the same native and simulator prerequisites for both paths."""
    shell.wait_standby_prerequisites()
    shell.capture()
    receipt = shell.read_startup_receipt()
    if receipt["byte0"] != 8:
        raise RuntimeError("startup IHU parking-status receipt is not the selected scenario")
    runtime.record_event("startup", "ihu_receipt", receipt, "simulator")


def vm_workbench_require_probe_workspace(workspace: Path) -> None:
    """Reject old or changed clones before starting the normal acquisition."""
    try:
        metadata = json.loads((workspace / "prepare.json").read_text())
        probe = metadata["workbench_frame_probe"]
        valid = (probe["source_sha256"] == PROBE_SOURCE_HASH and
                 probe["script_sha256"] == PROBE_SCRIPT_HASH and
                 probe["helper_sha256"] == vm_workbench_hash(workspace / "build/weston-ivi-frame-probe.so") and
                 probe["rootfs_sha256"] == metadata["sha256"]["rootfs.img"] and
                 probe["rootfs_sha256"] == vm_workbench_hash(workspace / "rootfs.img"))
    except (OSError, ValueError, KeyError, TypeError):
        valid = False
    if not valid:
        raise ValueError("workspace is incompatible: pinned frame-probe helper or prepared metadata missing or changed; prepare a new workspace")


def vm_workbench_prepare_foreground(shell: GuestShell, runtime: WorkbenchRuntime) -> None:
    """Acquire one verified probe image; its transferred pixels are historical."""
    vm_workbench_foreground_prerequisites(shell, runtime)
    model, frame, receipt, _source, _output, records = shell.foreground_and_probe()
    runtime.record_event("foreground", "model_acquired", model, "hmi")
    runtime.record_event("foreground", "probe_acquired", {"acquisition": receipt["acquisition"],
                         "records": records}, "display")
    runtime.publish_frame(frame, "guest-compositor", historical=True)


def vm_workbench_capture_loop(stop, runtime, shell, server, unexpected_exit=None) -> None:
    """Capture immediately, then poll at the normal three-second cadence."""
    while not stop.is_set() and runtime.get_status()["state"] == "running":
        try:
            runtime.publish_frame(shell().capture(), "guest-compositor")
        except (OSError, ValueError, RuntimeError, EOFError, TimeoutError) as exc:
            runtime.record_event("capture", "error", {"message": str(exc)}, "display")
        stop.wait(3)
    if server is not None and not stop.is_set():
        if unexpected_exit is None:
            server.shutdown()
        else:
            unexpected_exit.set()


def vm_workbench_write_acquisition_failure(run_dir: Path, exc: BaseException,
                                           filename: str = "acquisition-failure.json") -> Path | None:
    """Persist one validated failure diagnostic without masking the acquisition error."""
    diagnostic = getattr(exc, "diagnostic", None)
    if not isinstance(diagnostic, dict) or Path(filename).name != filename:
        return None
    try:
        payload = (json.dumps(diagnostic, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        return None
    destination = Path(run_dir) / filename
    fd = None
    created = False
    try:
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        created = True
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            fd = None
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except (OSError, TypeError, ValueError):
        if fd is not None:
            with suppress(OSError):
                os.close(fd)
        if created:
            with suppress(OSError):
                destination.unlink()
        return None
    try:
        print("Private acquisition failure diagnostic saved in " + str(destination), flush=True)
    except (OSError, ValueError):
        pass
    return destination


def vm_workbench_create_backend(workspace: Path, *, qemu: Path = QEMU,
                                wifi_simulation=None,
                                progress: Optional[Callable[[str, int, str], None]] = None):
    """Start and admit one normal VM session without creating another HTTP API."""

    workspace, qemu = Path(workspace).resolve(), Path(qemu).resolve()
    vm_workbench_require_probe_workspace(workspace)
    spec = importlib.util.spec_from_file_location("workbench_boot", PROJECT / "tools/uk_fw/vm_boot.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load VM boot implementation")
    boot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(boot)
    run_dir = workspace / "runs" / str(time.time_ns())
    bridge = {}
    runtime = None

    def report(stage: str, percent: int, message: str) -> None:
        if progress is not None:
            progress(stage, percent, message)

    def factory(argv, **kwargs):
        process, shell = vm_workbench_spawn(argv, run_dir=run_dir, event=runtime.record_event, **kwargs)
        bridge["shell"] = shell
        return process

    def compatibility(process, directory):
        deadline = time.monotonic() + 30
        while not (directory / "gdb.sock").exists():
            if process.poll() is not None:
                raise RuntimeError("QEMU exited before SDHCI debug socket was ready")
            if time.monotonic() >= deadline:
                raise TimeoutError("SDHCI debug socket did not appear")
            time.sleep(.05)
        with boot.connect_unix(directory, "gdb.sock") as sock:
            boot.adapt_sdhci(boot.RSP(sock))

    runtime = WorkbenchRuntime(workspace, run_dir, qemu, process_factory=factory,
                               compatibility_setup=compatibility)
    shell = lambda: bridge["shell"]
    input_adapter = GuestMailbox(lambda line: shell().publish_input(line), lambda: shell().read_input(),
                                 runtime.record_event, timeout=20, poll_interval=.2,
                                 bounded_publish=lambda line, deadline, guest_expiry:
                                 shell().publish_input_bounded(line, deadline, guest_expiry))
    sim_adapter = SimulatorMailbox(lambda line: shell().publish_simulator(line), lambda: shell().read_simulator(),
                                   runtime.record_event, timeout=20, poll_interval=.2)
    runtime.attach_channels(input_channel=input_adapter, simulator=sim_adapter,
                            observer=lambda: shell().observe_debugging_mode(),
                            hmi_observer=lambda: shell().observe_confirm_geometry(),
                            hmi_diagnoser=lambda: shell().diagnose_confirm_observation(), confirm_bridge=shell)
    try:
        report("vm", 55, "Starting snapshot/no-network VM")
        runtime.start()
        shell().wait_ready()
        report("guest", 65, "Guest userspace is ready")
        if wifi_simulation is not None:
            from .wifi_sim.session import wifi_sim_prepare_overlay
            assets, target = wifi_simulation[:2]
            wifi_sim_prepare_overlay(shell(), assets)
            report("simulation", 72, "Synthetic Wi-Fi overlay is staged")
        shell().launch(frame_probe=True)
        report("hmi", 78, "Gen5W HMI is launching")
        try:
            vm_workbench_prepare_foreground(shell(), runtime)
        except (OSError, RuntimeError, EOFError, TimeoutError, ValueError) as exc:
            vm_workbench_write_acquisition_failure(run_dir, exc)
            raise
        report("admission", 92, "Display and input admission passed")
        if wifi_simulation is not None:
            from .wifi_sim.session import wifi_sim_start_backend
            wifi_sim_start_backend(shell(), target)
        backend = KeyboardTapBackend(runtime)
        if wifi_simulation is not None:
            from .wifi_sim.guard import WifiSimInputGuard
            if len(wifi_simulation) == 3:
                backend = WifiSimInputGuard(backend, shell(), runtime,
                                            image_tool=str(wifi_simulation[2]))
            elif len(wifi_simulation) == 2:
                backend = WifiSimInputGuard(backend, shell(), runtime)
            else:
                raise ValueError("invalid Wi-Fi simulation preparation tuple")
        return _ManagedWorkbenchBackend(backend, runtime, shell())
    except BaseException:
        runtime.shutdown()
        if "shell" in bridge:
            shell().close()
        raise


def vm_workbench_open_browser(url: str) -> bool:
    """Open only an already validated loopback workbench URL."""

    if not isinstance(url, str) or not (url.startswith("http://127.0.0.1:")
                                       or url == "http://gen5w.local"
                                       or url.startswith("http://gen5w.local:")):
        raise ValueError("refusing to open an untrusted workbench URL")
    windows_browser = os.environ.get("GEN5W_WINDOWS_BROWSER")
    if windows_browser is not None:
        executable = Path(windows_browser)
        normalized = executable.as_posix().casefold()
        if (not executable.is_absolute() or not normalized.endswith("/windows/explorer.exe")
                or not executable.is_file() or not os.access(executable, os.X_OK)):
            raise ValueError("GEN5W_WINDOWS_BROWSER is not a verified Windows explorer.exe path")
        subprocess.Popen([str(executable), url], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         close_fds=True)
        return True
    return bool(webbrowser.open(url, new=1, autoraise=True))


def vm_workbench_failure_summary(exc: BaseException) -> str:
    """Return one bounded browser-safe first line, including empty exceptions."""

    lines = str(exc).splitlines()
    return (lines[0][:240] if lines and lines[0] else "VM startup failed")


def vm_workbench_run_server(prepare: Callable[[Callable[[str, int, str], None]],
                                              Tuple[Path, Any, Path]], *,
                            port: int = 8765, host_name: str = "127.0.0.1",
                            open_browser: bool = False,
                            simulation_mode: bool = False) -> bool:
    """Serve progress first, then attach one admitted normal VM backend."""

    if not callable(prepare):
        raise TypeError("prepare must be callable")
    service = WorkbenchServiceBackend(simulation_mode=simulation_mode)
    server = WorkbenchHTTPServer(service, port, host_name)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .2},
                              name="gen5w-http", daemon=True)
    managed = None
    failed = False
    thread.start()
    print("Gen5W browser service listening at " + server.origin, flush=True)

    def report(stage: str, percent: int, message: str) -> None:
        if service.cancelled.is_set():
            raise InterruptedError("startup cancelled by operator")
        service.service_mark_progress(stage, percent, message)

    try:
        if open_browser:
            try:
                opened = vm_workbench_open_browser(server.origin)
            except (OSError, ValueError, webbrowser.Error) as exc:
                opened = False
                print("Browser handoff failed: " + vm_workbench_failure_summary(exc),
                      file=sys.stderr, flush=True)
            if not opened:
                print("Browser did not open automatically. Open " + server.origin,
                      file=sys.stderr, flush=True)
        report("assets", 5, "Checking compatible local assets")
        workspace, wifi_simulation, qemu = prepare(report)
        if service.cancelled.is_set():
            raise InterruptedError("startup cancelled by operator")
        report("workspace", 50, "Workspace is prepared and hash-bound")
        managed = vm_workbench_create_backend(workspace, qemu=qemu,
                                              wifi_simulation=wifi_simulation,
                                              progress=report)
        if service.cancelled.is_set():
            managed.close(); managed = None
            raise InterruptedError("startup cancelled by operator")
        managed.start_capture(server, defer_unexpected_shutdown=True)
        service.service_attach_backend(managed)
        print("Workbench " + vm_workbench_version() + " ready at " + server.origin, flush=True)
        while (thread.is_alive() and service.get_status()["service_state"] == "ready"
               and not managed.vm_workbench_wait_runtime_stop(.2)):
            pass
        if (managed.vm_workbench_runtime_stopped_unexpectedly()
                and not service.cancelled.is_set()):
            failed = True
            message = "VM stopped unexpectedly; review the terminal and run log"
            service.service_fail("runtime_stopped", message)
            print("workbench error: " + message, file=sys.stderr, flush=True)
            if not service.cancelled.wait(FAILURE_VISIBILITY_SECONDS):
                service.service_stop("Failure visibility period expired")
    except KeyboardInterrupt:
        service.service_stop("Interrupted by operator")
    except InterruptedError:
        if not service.cancelled.is_set():
            service.service_stop("Startup cancelled")
    except (OSError, ValueError, RuntimeError, EOFError, subprocess.SubprocessError) as exc:
        failed = True
        if service.get_status()["service_state"] == "starting":
            service.service_fail(type(exc).__name__.lower(), vm_workbench_failure_summary(exc))
        print("workbench error: " + vm_workbench_failure_summary(exc), file=sys.stderr, flush=True)
        if not service.cancelled.wait(FAILURE_VISIBILITY_SECONDS):
            service.service_stop("Failure visibility period expired")
    finally:
        service.cancelled.set()
        if managed is not None:
            managed.close()
        server.shutdown(); server.server_close(); thread.join(5)
    return not failed and service.get_status()["error_code"] != "shutdown_failed"


def vm_workbench_run(workspace: Path, port: int = 0, diagnostic_console: bool = False,
                     diagnostic_launch: bool = False, diagnostic_ivi_frame: bool = False,
                     diagnostic_ivi_confirm: bool = False, wifi_simulation=None) -> None:
    """Run the owned guest and local operator server until interrupted."""
    if not any((diagnostic_console, diagnostic_launch, diagnostic_ivi_frame, diagnostic_ivi_confirm)):
        managed = vm_workbench_create_backend(workspace, wifi_simulation=wifi_simulation)
        server = WorkbenchHTTPServer(managed, port)
        try:
            managed.start_capture(server)
            print("Workbench " + vm_workbench_version() + " listening at " + server.origin, flush=True)
            server.serve_forever(poll_interval=.2)
        finally:
            server.server_close()
            managed.close()
        return
    spec = importlib.util.spec_from_file_location("workbench_boot", PROJECT / "tools/uk_fw/vm_boot.py")
    boot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(boot)
    run_dir = workspace / "runs" / str(time.time_ns())
    bridge = {}

    def factory(argv, **kwargs):
        process, shell = vm_workbench_spawn(argv, run_dir=run_dir, event=runtime.record_event, **kwargs)
        bridge["shell"] = shell
        return process

    def compatibility(process, directory):
        deadline = time.monotonic() + 30
        while not (directory / "gdb.sock").exists():
            if process.poll() is not None:
                raise RuntimeError("QEMU exited before SDHCI debug socket was ready")
            if time.monotonic() >= deadline:
                raise TimeoutError("SDHCI debug socket did not appear")
            time.sleep(.05)
        with boot.connect_unix(directory, "gdb.sock") as sock:
            boot.adapt_sdhci(boot.RSP(sock))

    runtime = WorkbenchRuntime(workspace, run_dir, QEMU, process_factory=factory,
                               compatibility_setup=compatibility)
    shell = lambda: bridge["shell"]
    input_adapter = GuestMailbox(lambda line: shell().publish_input(line), lambda: shell().read_input(),
                                 runtime.record_event, timeout=20, poll_interval=.2,
                                 bounded_publish=lambda line, deadline, guest_expiry: shell().publish_input_bounded(line, deadline, guest_expiry))
    sim_adapter = SimulatorMailbox(lambda line: shell().publish_simulator(line), lambda: shell().read_simulator(),
                                   runtime.record_event, timeout=20, poll_interval=.2)
    runtime.attach_channels(input_channel=input_adapter, simulator=sim_adapter,
                            observer=lambda: shell().observe_debugging_mode(),
                            hmi_observer=lambda: shell().observe_confirm_geometry(),
                            hmi_diagnoser=lambda: shell().diagnose_confirm_observation(), confirm_bridge=shell)
    server = None
    stop = threading.Event()
    capture_thread = None
    try:
        runtime.start()
        shell().wait_ready()
        if wifi_simulation is not None:
            from .wifi_sim.session import wifi_sim_prepare_overlay
            assets, target = wifi_simulation
            wifi_sim_prepare_overlay(shell(), assets)
        if diagnostic_console:
            shell()._run("printf console-ready", timeout=10)
            time.sleep(15)
            reply = shell()._run("printf console-still-ready", timeout=10)
            if reply != b"console-still-ready":
                raise RuntimeError("unexpected console diagnostic reply")
            print("Console diagnostic passed after 15 seconds", flush=True)
            return
        if diagnostic_console or diagnostic_launch:
            shell().launch()
        else:
            shell().launch(frame_probe=True)
        if diagnostic_launch:
            time.sleep(3)
            (run_dir / "launch-diagnostic.log").write_bytes(shell().diagnostics())
            print("Early startup diagnostics captured in " + str(run_dir / "launch-diagnostic.log"), flush=True)
            return
        if diagnostic_ivi_frame:
            shell().wait_standby_prerequisites()
            receipt, source, output = shell().observe_ivi_frame()
            # Artifacts stay in the private run directory and are created only once.
            for name, content in (("ivi-frame-source.raw", source), ("ivi-frame-output.raw", output),
                                  ("ivi-frame-receipt.json", (json.dumps(receipt, sort_keys=True) + "\n").encode())):
                fd = os.open(run_dir / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(content)
            print("Private IVI frame diagnostic saved in " + str(run_dir), flush=True)
            return
        if diagnostic_ivi_confirm:
            vm_workbench_foreground_prerequisites(shell(), runtime)
            try:
                model, frame, receipt, source, output, records = shell().foreground_and_probe()
            except (OSError, RuntimeError, EOFError, TimeoutError, ValueError) as exc:
                vm_workbench_write_acquisition_failure(run_dir, exc, "ivi-confirm-failure.json")
                raise
            receipt["native_model"] = model
            receipt["acquisition_records"] = records
            for name, content in (("ivi-confirm-source.raw", source), ("ivi-confirm-output.raw", output),
                                  ("ivi-confirm-frame.png", frame),
                                  ("ivi-confirm-receipt.json", (json.dumps(receipt, sort_keys=True) + "\n").encode())):
                fd = os.open(run_dir / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(content)
            print("Private IVI Confirm-window diagnostic saved in " + str(run_dir) + "; pixels require inspection", flush=True)
            return
        try:
            vm_workbench_prepare_foreground(shell(), runtime)
        except (OSError, RuntimeError, EOFError, TimeoutError, ValueError) as exc:
            vm_workbench_write_acquisition_failure(run_dir, exc)
            raise
        if wifi_simulation is not None:
            from .wifi_sim.session import wifi_sim_start_backend
            wifi_sim_start_backend(shell(), target)
        backend = KeyboardTapBackend(runtime)
        if wifi_simulation is not None:
            from .wifi_sim.guard import WifiSimInputGuard
            backend = WifiSimInputGuard(backend, shell(), runtime)
        server = WorkbenchHTTPServer(backend, port)
        print("Workbench " + vm_workbench_version() + " listening at " + server.origin, flush=True)

        capture_thread = threading.Thread(target=vm_workbench_capture_loop,
                                          args=(stop, runtime, shell, server),
                                          name="workbench-capture", daemon=True)
        capture_thread.start()

        server.serve_forever(poll_interval=.2)
    finally:
        stop.set()
        if server is not None:
            server.server_close()
        runtime.shutdown()
        if capture_thread is not None:
            capture_thread.join(timeout=5)
        if "shell" in bridge:
            shell().close()


def main(argv=None) -> int:
    """Parse CLI arguments and report precise local prerequisite failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version="%(prog)s " + vm_workbench_version())
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--server", action="store_true",
                        help="serve startup progress and the admitted VM in a browser")
    parser.add_argument("--assets", type=Path,
                        help="directory containing a compatible gen5w-assets.json bundle")
    parser.add_argument("--host-name", choices=("127.0.0.1", "gen5w.local"),
                        default="127.0.0.1", help="exact loopback authority shown to the browser")
    parser.add_argument("--open-browser", action="store_true",
                        help="open the validated local URL after the listener starts")
    parser.add_argument("--workspace", type=Path, help="existing prepared workbench clone")
    parser.add_argument("--diagnostic-console", action="store_true", help="check guest serial console without starting the HMI")
    parser.add_argument("--diagnostic-launch", action="store_true", help="capture the first HMI startup diagnostics")
    parser.add_argument("--diagnostic-ivi-frame", action="store_true", help="capture one private owner-bound IVI and output frame diagnostic")
    parser.add_argument("--diagnostic-ivi-confirm", action="store_true", help="capture private IVI pixels within the bounded native Confirm acquisition")
    parser.add_argument("--wifi-sim", action="store_true", help="start isolated synthetic Wi-Fi controls (new VM only)")
    parser.add_argument("--wifi-sim-assets", type=Path, help="directory containing pinned private simulation UI inputs")
    args = parser.parse_args(argv)
    print("GEN5W_VM_WORKBENCH_VERSION=" + vm_workbench_version(), flush=True)
    try:
        diagnostics = (args.diagnostic_console, args.diagnostic_launch,
                       args.diagnostic_ivi_frame, args.diagnostic_ivi_confirm)
        if args.server:
            if args.assets is None:
                raise ValueError("--server requires --assets")
            if args.workspace is not None or any(diagnostics) or args.wifi_sim_assets is not None:
                raise ValueError("--server uses a fresh asset workspace and no diagnostic mode")
            if not 0 <= args.port <= 65535:
                raise ValueError("--port must be between 0 and 65535")
            completed = vm_workbench_run_server(
                lambda progress: vm_workbench_prepare_public(
                    args.assets, wifi_sim=args.wifi_sim, progress=progress),
                port=args.port, host_name=args.host_name,
                open_browser=args.open_browser, simulation_mode=args.wifi_sim,
            )
            return 0 if completed else 1
        if args.assets is not None or args.open_browser or args.host_name != "127.0.0.1":
            raise ValueError("--assets, --host-name and --open-browser require --server")
        wifi_simulation = None
        assets = None
        if args.wifi_sim:
            from .wifi_sim.integration import wifi_sim_require_fresh_opt_in
            from .wifi_sim.session import wifi_sim_load_assets
            wifi_sim_require_fresh_opt_in(True, args.workspace, any(diagnostics))
            if args.wifi_sim_assets is None:
                raise ValueError("--wifi-sim requires --wifi-sim-assets")
            assets = wifi_sim_load_assets(args.wifi_sim_assets, Path(__file__).with_name('wifi_sim') / '0001-vm-only-wifi-simulated-banner.patch')
            print("SIMULATED - NO RADIO", flush=True)
        elif args.wifi_sim_assets is not None:
            raise ValueError("--wifi-sim-assets requires --wifi-sim")
        OUTPUT.mkdir(parents=True, exist_ok=True)
        workspace = args.workspace.resolve() if args.workspace else vm_workbench_prepare(OUTPUT / ("session-" + str(time.time_ns())), frame_probe=not (args.diagnostic_console or args.diagnostic_launch))
        if workspace.parent != OUTPUT.resolve() or not workspace.is_dir():
            raise ValueError("workspace must be an existing direct child of " + str(OUTPUT))
        if sum(diagnostics) > 1:
            raise ValueError("select only one diagnostic mode")
        if assets is not None:
            from .wifi_sim.integration import wifi_sim_build_target, SIM_TARGET_SHA256, wifi_sim_checked_bytes
            target = workspace / 'build' / 'wifi-sim'
            wifi_sim_build_target(Path(__file__).with_name('wifi_sim') / 'wifi_sim.c', target, Path('/opt/homebrew/bin/x86_64-linux-musl-gcc'))
            wifi_simulation = (assets, wifi_sim_checked_bytes(target, SIM_TARGET_SHA256))
        vm_workbench_run(workspace, args.port, args.diagnostic_console, args.diagnostic_launch, args.diagnostic_ivi_frame, args.diagnostic_ivi_confirm, wifi_simulation)
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, RuntimeError, EOFError, subprocess.SubprocessError) as exc:
        print("workbench error: " + vm_workbench_failure_summary(exc), file=sys.stderr)
        return 1
    return 0
