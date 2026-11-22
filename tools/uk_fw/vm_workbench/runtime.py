"""Owned QEMU lifecycle and backend facade for the local VM workbench.

No physical-device discovery or arbitrary command endpoint exists here. The
caller wires an explicit guest bridge and invokes start once per session.
"""

from __future__ import annotations

from collections import deque
from contextlib import contextmanager
from copy import deepcopy
import importlib.util
import os
import stat
from pathlib import Path
import subprocess
import threading
import time
from typing import Any, Callable, Dict, List, Mapping, Optional

from .contracts import CommandReceipt, EventRecord, FrameSnapshot, ModuleField, ModuleSnapshot
from .confirm_action import ConfirmAction
from .platform_config import platform_config_qemu_cpu_profile
from .transport import FrameStore, GuestMailbox, SimulatorMailbox, vm_transport_key, vm_transport_pointer


class WorkbenchRuntime:
    """Own exactly one QEMU child and provide the frozen backend API."""

    def __init__(self, workspace: Path, run_dir: Path, qemu: Path, *,
                 input_channel: Optional[GuestMailbox] = None,
                 simulator: Optional[SimulatorMailbox] = None,
                 observer: Optional[Callable[[], int]] = None,
                 hmi_observer: Optional[Callable[[], dict]] = None,
                 hmi_diagnoser: Optional[Callable[[], dict]] = None,
                 frame_store: Optional[FrameStore] = None,
                 process_factory: Callable[..., Any] = subprocess.Popen,
                 compatibility_setup: Optional[Callable[[Any, Path], None]] = None,
                 event_limit: int = 1024):
        if not 1 <= event_limit <= 10000:
            raise ValueError("event limit must be between 1 and 10000")
        self._workspace = Path(workspace).resolve()
        self._run_dir = Path(run_dir).resolve()
        self._qemu = Path(qemu).resolve()
        self._input = input_channel
        self._simulator = simulator
        self._observer = observer
        self._hmi_observer = hmi_observer
        self._hmi_diagnoser = hmi_diagnoser
        self._hmi_diagnostic = None
        self._diagnostic_lock = threading.Lock()
        self._hmi_observed = None
        self._hmi_observed_ns = None
        self._frames = frame_store or FrameStore()
        self._factory = process_factory
        self._compatibility_setup = compatibility_setup
        self._process = None
        self._cpu_profile: Optional[str] = None
        self._events: deque = deque(maxlen=event_limit)
        self._event_sequence = 0
        self._event_lock = threading.Lock()
        self._lifecycle_lock = threading.Lock()
        self._sim_value: Optional[int] = None
        self._sim_configured: Optional[int] = None
        self._sim_observed: Optional[int] = None
        self._parking_value: Optional[bool] = None
        self._parking_configured: Optional[bool] = None
        self._sim_lock = threading.Lock()
        self._sim_turns = deque()
        self._sim_ready = threading.Condition(self._sim_lock)
        self._sim_shutdown = False
        self._closing = threading.Event()
        self._confirm_bridge = None
        self._confirm = ConfirmAction(self.get_frame, self._confirm_session, self.record_event)

    @contextmanager
    def _sim_turn(self, ticket: object):
        """Run an admitted guest effect in FIFO order without holding state lock.

        The ticket was queued under ``_sim_lock`` with the state snapshot. Remove
        it even if waiting or I/O raises, so later admitted calls can advance.
        """
        try:
            with self._sim_ready:
                while self._sim_turns[0] is not ticket:
                    self._sim_ready.wait()
            yield
        finally:
            with self._sim_ready:
                self._sim_turns.remove(ticket)
                self._sim_ready.notify_all()

    def attach_channels(self, *, input_channel: Optional[GuestMailbox],
                        simulator: Optional[SimulatorMailbox],
                        observer: Optional[Callable[[], int]] = None,
                        hmi_observer: Optional[Callable[[], dict]] = None,
                        hmi_diagnoser: Optional[Callable[[], dict]] = None,
                        confirm_bridge: Optional[Callable[[], Any]] = None) -> None:
        """Attach explicitly constructed guest bridges before the VM is started."""

        with self._lifecycle_lock:
            if self._process is not None:
                raise RuntimeError("channels cannot change after process start")
            with self._sim_lock:
                self._input, self._simulator = input_channel, simulator
                self._observer = observer
                self._hmi_observer = hmi_observer
                self._hmi_diagnoser = hmi_diagnoser
                self._confirm_bridge = confirm_bridge

    def _confirm_session(self):
        """Return the exact live process, bridge and input channel identities."""
        if self._closing.is_set(): return None
        process, mailbox, provider = self._process, self._input, self._confirm_bridge
        if process is None or process.poll() is not None or mailbox is None or provider is None:
            return None
        try:
            bridge = provider()
        except (KeyError, RuntimeError):
            return None
        if bridge is None: return None
        return process, bridge, mailbox

    def observe_and_confirm_once(self, *, frame_sequence: int, correlation_id: Optional[str] = None) -> CommandReceipt:
        """Observe one approved live frame and publish at most one Confirm click."""
        return self._confirm.run(frame_sequence, correlation_id)

    def record_event(self, correlation_id: str, event: str, detail: Mapping[str, Any],
                     component: str = "guest") -> None:
        """Record one bounded, correlated diagnostic event."""

        with self._event_lock:
            self._event_sequence += 1
            self._events.append(EventRecord(self._event_sequence, time.time_ns(), correlation_id,
                                            component, event, dict(detail)))

    def start(self, *, memory_mib: int = 1536, compatibility: bool = True) -> None:
        """Validate the existing workspace and start the owned QEMU process.

        The exact-build SDHCI adaptation is delegated to a supplied callback;
        a paused compatibility guest is never silently left running without it.
        """

        with self._lifecycle_lock:
            if self._process is not None:
                raise RuntimeError("this workbench already owns a process")
            missing = [str(path) for path in (self._qemu, self._workspace / "prepare.json",
                       *(self._workspace / name for name in ("bzImage", "rootfs.img", "manifest.bin", "seed_dev.bin", "seed_user.bin")))
                       if not path.is_file()]
            if missing:
                raise FileNotFoundError("missing VM prerequisites: " + ", ".join(missing))
            if not os.access(self._qemu, os.X_OK):
                raise PermissionError("QEMU is not executable: " + str(self._qemu))
            if compatibility and self._compatibility_setup is None:
                raise ValueError("SDHCI compatibility setup callback is required")
            if not 256 <= memory_mib <= 8192:
                raise ValueError("VM memory must be between 256 and 8192 MiB")
            source = Path(__file__).resolve().parents[1] / "vm_boot.py"
            spec = importlib.util.spec_from_file_location("vm_workbench_existing_boot", source)
            if spec is None or spec.loader is None:
                raise RuntimeError("cannot load existing VM boot implementation")
            boot = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(boot)
            boot.verify_workspace(self._workspace)
            self._cpu_profile = platform_config_qemu_cpu_profile()
            argv = boot.qemu_command(self._workspace, str(self._qemu), compatibility,
                                     display="none", qmp=True, memory_mib=memory_mib,
                                     cpu=self._cpu_profile)
            if argv[argv.index("-nic") + 1] != "none" or "snapshot=on" not in argv[argv.index("-drive") + 1]:
                raise RuntimeError("QEMU command lacks required snapshot/no-network isolation")
            # Serial output can include private frame pixels. Establish the
            # directory boundary before spawning a process that can emit them.
            self._run_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
            run_fd = os.open(self._run_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fchmod(run_fd, 0o700)
                run_stat = os.fstat(run_fd)
                path_stat = os.lstat(self._run_dir)
                if (not stat.S_ISDIR(run_stat.st_mode) or run_stat.st_uid != os.geteuid() or
                    stat.S_IMODE(run_stat.st_mode) != 0o700 or
                    (run_stat.st_dev, run_stat.st_ino) != (path_stat.st_dev, path_stat.st_ino)):
                    raise PermissionError("workbench run directory is not private")
            finally:
                os.close(run_fd)
            process = self._factory(argv, cwd=str(self._run_dir), stdin=subprocess.PIPE,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    env={**os.environ, "TMPDIR": str(self._run_dir)})
            with self._sim_lock:
                self._process = process
                self._sim_shutdown = False
            self.record_event("session", "started", {"pid": process.pid, "snapshot": True,
                                                      "guest_network": False,
                                                      "cpu_profile": self._cpu_profile}, "runtime")
            if compatibility:
                try:
                    self._compatibility_setup(process, self._run_dir)
                except Exception:
                    self._stop_owned(process)
                    self.record_event("session", "compatibility_failed", {}, "runtime")
                    raise

    @staticmethod
    def _stop_owned(process: Any) -> bool:
        """Attempt bounded termination and report whether this child was reaped."""

        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Retain the owned process reference so a caller can
                        # retry cleanup; a kill request is not proof of exit.
                        return False
            return process.poll() is not None
        finally:
            if process.stdin is not None:
                process.stdin.close()

    def get_status(self) -> Mapping[str, Any]:
        """Report owned process state and explicit isolated scope."""

        process = self._process
        running = process is not None and process.poll() is None
        return {"state": "running" if running else ("stopped" if process is not None else "not_started"),
                "pid": process.pid if running else None, "snapshot": True, "guest_network": False,
                "cpu_profile": self._cpu_profile,
                "scope": "local-vm", "input_connected": self._input is not None,
                "simulator_connected": self._simulator is not None}

    def get_frame(self) -> FrameSnapshot:
        """Return the last compositor frame with disconnect and stale status."""

        return self._frames.get(disconnected=self.get_status()["state"] != "running")

    def publish_frame(self, payload: bytes, source: str, correlation_id: str = "capture", *, historical: bool = False) -> FrameSnapshot:
        """Publish a validated compositor frame from the explicit capture bridge."""

        if not self._confirm.acquire_manual():
            raise BlockingIOError("Confirm action is active")
        try:
            frame = self._frames.publish(payload, source, historical=historical)
            self.record_event(correlation_id, "frame", {"sequence": frame.sequence, "source": source,
                              "width": frame.width, "height": frame.height, "historical": historical}, "display")
            return frame
        finally:
            self._confirm.release_manual()

    def send_pointer(self, *, action: str, x1: int, y1: int, x2: Optional[int] = None,
                     y2: Optional[int] = None, correlation_id: Optional[str] = None) -> CommandReceipt:
        """Validate and send one pointer operation through the guest bridge."""

        operation = vm_transport_pointer(action, x1, y1, x2, y2)
        return self._send_input(operation, correlation_id)

    def wifi_sim_guarded_click(self, *, frame_sequence: int, x: int, y: int,
                               verifier, correlation_id: Optional[str] = None) -> CommandReceipt:
        """Bind one simulated click to an unchanged displayed compositor frame."""
        from .transport import vm_transport_identifier
        command_id, created = vm_transport_identifier(correlation_id), time.time_ns()
        def refusal(state, message):
            return CommandReceipt(command_id, False, state, message, created, time.time_ns())
        if type(frame_sequence) is not int or not 1 <= frame_sequence <= 2**53 - 1:
            raise ValueError('invalid simulated frame sequence')
        if not self._confirm.acquire():
            return refusal('busy', 'another input or capture is active')
        try:
            session = self._confirm_session()
            if session is None:
                return refusal('disconnected', 'guest bridge unavailable')
            try:
                reference = self.get_frame()
            except LookupError:
                return refusal('stale', 'displayed frame unavailable')
            if (reference.sequence != frame_sequence or reference.stale or reference.source != 'guest-compositor'
                    or reference.mime_type != 'image/png' or (reference.width, reference.height) != (1920, 720)):
                return refusal('stale', 'displayed frame is stale or changed')
            process, bridge, mailbox = session
            deadline = time.monotonic() + 10.0
            def current():
                now = self._confirm_session()
                return (now is not None and all(a is b for a,b in zip(now,session))
                        and len(now) == len(session) and bridge.is_available()
                        and time.monotonic() < deadline)
            try:
                with bridge.compound_lease():
                    if not current(): return refusal('disconnected', 'guest session changed')
                    identity = verifier.prepare(reference.payload)
                    if not current(): return refusal('expired', 'guest session changed')
                    frame, guest_ms = bridge.capture_timed(deadline)
                    if frame != reference.payload or self.get_frame() != reference:
                        return refusal('changed', 'fresh frame differs from displayed frame')
                    captured = time.monotonic()
                    verifier.finish(identity, frame)
                    if (not current() or self.get_frame() != reference or
                            time.monotonic() - captured > 0.8):
                        return refusal('expired', 'frame or guest state changed before input')
                    operation = vm_transport_pointer('click', x, y)
                    return mailbox.send_once(operation, command_id,
                                             min(deadline, time.monotonic()+0.8), guest_ms+990)
            except (OSError, EOFError, RuntimeError, ValueError, TimeoutError) as exc:
                return refusal('error', str(exc))
        finally:
            self._confirm.release()

    def send_key(self, *, action: str, key: str, correlation_id: Optional[str] = None) -> CommandReceipt:
        """Validate and send one key operation through the guest bridge."""

        return self._send_input(vm_transport_key(action, key), correlation_id)

    def _send_input(self, operation: Mapping[str, Any], correlation_id: Optional[str]) -> CommandReceipt:
        from .transport import vm_transport_identifier
        if not self._confirm.acquire_manual():
            return CommandReceipt(vm_transport_identifier(correlation_id), False, "busy", "Confirm action is active", time.time_ns())
        try:
            return self._send_input_unlocked(operation, correlation_id)
        finally:
            self._confirm.release_manual()

    def _send_input_unlocked(self, operation: Mapping[str, Any], correlation_id: Optional[str]) -> CommandReceipt:
        from .transport import vm_transport_identifier
        if self.get_status()["state"] != "running" or self._input is None:
            return CommandReceipt(vm_transport_identifier(correlation_id), False, "disconnected",
                                  "guest input bridge unavailable", time.time_ns())
        return self._input.send(operation, correlation_id)

    def get_modules(self) -> List[ModuleSnapshot]:
        """Describe simulator fields and distinguish receipts from observations."""

        with self._sim_lock:
            connected = (not self._sim_shutdown and self._simulator is not None
                         and self._process is not None and self._process.poll() is None)
            fields = [ModuleField("debug_count", self._sim_value, "integer", connected,
                                  "guest-mailbox-acknowledged; recovered-consumer-byte0"),
                      ModuleField("debug_count_configured", self._sim_configured, "integer", False,
                                  "operator-requested; not guest acknowledgement"),
                      ModuleField("debug_count_dbus_observed", self._sim_observed, "integer", False,
                                  "guest-system-bus AskDebuggingMode reply byte0; VM-only observation"),
                      ModuleField("parking_status", self._parking_value, "boolean", connected,
                                  "IHU parking-status simulator receipt; not physical gear or speed"),
                      ModuleField("parking_status_configured", self._parking_configured, "boolean", False,
                                  "operator-requested; initial VM scenario sets true before launcher")]
            hmi_connected = (not self._sim_shutdown and self._hmi_observer is not None
                             and self._process is not None and self._process.poll() is None)
            state = deepcopy(self._hmi_observed or {})
            hmi_fields = [ModuleField(name, state.get(name), kind, False,
                                      "new QML timer record during last probe; verify foreground with a fresh frame")
                          for name, kind in (("buttonRoot", "geometry"), ("enabled", "boolean"),
                                             ("modelEnableBtn", "integer"), ("visible", "boolean"),
                                             ("wide", "boolean"), ("dimmed", "boolean"),
                                             ("driving", "boolean"), ("calling", "boolean"))]
            hmi_fields.append(ModuleField("observed_ns", self._hmi_observed_ns, "integer", False,
                                          "host probe completion time; correlate with a fresh frame"))
            hmi_fields.append(ModuleField("last_diagnostic", deepcopy(self._hmi_diagnostic), "diagnostic", False,
                                          "last successful fixed diagnostic; VM only"))
        return [ModuleSnapshot("micom", "MICOM engineering-data simulator", "guest-mailbox",
                               "guest-integrated simulator" if connected else "disconnected", fields,
                               "Observe guest D-Bus"),
                ModuleSnapshot("hmi", "HMI Confirm observation", "guest-log",
                               "guest QML observation" if hmi_connected else "disconnected", hmi_fields,
                               "Observe Confirm state", "Diagnose Confirm observation")]

    def set_module_field(self, *, module_id: str, field: str, value: Any,
                         correlation_id: Optional[str] = None) -> CommandReceipt:
        """Set a supported simulator value via its owning adapter."""

        if module_id != "micom" or field not in ("debug_count", "parking_status"):
            raise ValueError("unknown simulator field")
        if field == "parking_status" and type(value) is not bool:
            raise ValueError("parking_status must be boolean")
        if field == "debug_count" and (type(value) is not int or not 0 <= value <= 255):
            raise ValueError("debug_count must be an integer from 0 through 255")
        from .transport import vm_transport_identifier
        command_id = vm_transport_identifier(correlation_id)
        created = time.time_ns()
        with self._sim_lock:
            if field == "parking_status":
                self._parking_configured = value
            else:
                self._sim_configured = value
            adapter, process = self._simulator, self._process
            if self._sim_shutdown or process is None or process.poll() is not None or adapter is None:
                return CommandReceipt(command_id, False, "disconnected", "guest simulator bridge unavailable", created)
            ticket = object()
            self._sim_turns.append(ticket)
        # Admission is ordered by the same lock that records the configured value.
        with self._sim_turn(ticket):
            with self._sim_lock:
                current = (not self._sim_shutdown and self._process is process and process.poll() is None
                           and self._simulator is adapter)
            if not current:
                self.record_event(command_id, "stale_result", {"module": module_id}, "simulator")
                return CommandReceipt(command_id, False, "disconnected", "guest simulator bridge changed", created)
            try:
                receipt, acknowledged = (adapter.request(int(value), command_id, field=field)
                                         if field == "parking_status" else adapter.request(value, command_id))
            except Exception:
                with self._sim_lock:
                    current = (not self._sim_shutdown and self._process is process and process.poll() is None
                               and self._simulator is adapter)
                if not current:
                    self.record_event(command_id, "stale_result", {"module": module_id}, "simulator")
                    return CommandReceipt(command_id, False, "disconnected", "guest simulator bridge changed", created)
                raise
            with self._sim_lock:
                current = (not self._sim_shutdown and self._process is process and process.poll() is None
                           and self._simulator is adapter)
                if current and receipt.accepted:
                    if field == "parking_status":
                        self._parking_value = bool(acknowledged)
                    else:
                        self._sim_value = acknowledged
            if not current:
                self.record_event(command_id, "stale_result", {"module": module_id}, "simulator")
                return CommandReceipt(command_id, False, "disconnected", "guest simulator bridge changed", created)
            return receipt

    def observe_module(self, *, module_id: str,
                       correlation_id: Optional[str] = None) -> CommandReceipt:
        """Query the fixed simulated guest system-bus debugging-mode reply."""
        if module_id == "hmi":
            return self._observe_hmi(correlation_id)
        from .transport import vm_transport_identifier
        if module_id != "micom":
            raise ValueError("unknown simulator module")
        command_id = vm_transport_identifier(correlation_id)
        created = time.time_ns()
        with self._sim_lock:
            adapter, observer, process = self._simulator, self._observer, self._process
            if (self._sim_shutdown or process is None or process.poll() is not None
                    or adapter is None or observer is None):
                return CommandReceipt(command_id, False, "disconnected", "guest observation bridge unavailable", created)
            ticket = object()
            self._sim_turns.append(ticket)
        with self._sim_turn(ticket):
            with self._sim_lock:
                current = (not self._sim_shutdown and self._process is process and process.poll() is None
                           and self._simulator is adapter and self._observer is observer)
            if not current:
                self.record_event(command_id, "observation_error", {"module": module_id, "message": "guest observation bridge changed"}, "simulator")
                return CommandReceipt(command_id, False, "disconnected", "guest observation bridge changed", created)
            self.record_event(command_id, "observation_requested", {"module": module_id}, "simulator")
            try:
                value = observer()
                if type(value) is not int or not 0 <= value <= 255:
                    raise ValueError("guest observation is not one byte")
                with self._sim_lock:
                    current = (not self._sim_shutdown and self._process is process and process.poll() is None
                               and self._simulator is adapter and self._observer is observer)
                    if current:
                        self._sim_observed = value
                        acknowledged = self._sim_value
                if not current:
                    self.record_event(command_id, "observation_error", {"module": module_id, "message": "guest observation bridge changed"}, "simulator")
                    return CommandReceipt(command_id, False, "disconnected", "guest observation bridge changed", created)
                mismatch = acknowledged is not None and value != acknowledged
                state = "mismatch" if mismatch else "completed"
                self.record_event(command_id, state, {"module": module_id, "observed": value,
                                  "acknowledged": acknowledged, "mismatch": mismatch}, "simulator")
                return CommandReceipt(command_id, not mismatch, state,
                                      "guest reply differs from mailbox acknowledgement" if mismatch else "guest D-Bus byte observed",
                                      created, time.time_ns())
            except (OSError, ValueError, RuntimeError, EOFError, TimeoutError) as exc:
                with self._sim_lock:
                    current = (not self._sim_shutdown and self._process is process and process.poll() is None
                               and self._simulator is adapter and self._observer is observer)
                self.record_event(command_id, "observation_error", {"module": module_id, "message": str(exc)}, "simulator")
                return CommandReceipt(command_id, False, "error" if current else "disconnected", str(exc), created)

    def _observe_hmi(self, correlation_id: Optional[str]) -> CommandReceipt:
        """Read one fixed QML observation without holding the shared state lock."""
        from .transport import vm_transport_identifier
        command_id, created = vm_transport_identifier(correlation_id), time.time_ns()
        with self._sim_lock:
            observer, process = self._hmi_observer, self._process
            if self._sim_shutdown or process is None or process.poll() is not None or observer is None:
                return CommandReceipt(command_id, False, "disconnected", "guest HMI observation unavailable", created)
            ticket = object()
            self._sim_turns.append(ticket)
        with self._sim_turn(ticket):
            def current():
                return (not self._sim_shutdown and self._process is process and process.poll() is None
                        and self._hmi_observer is observer)
            with self._sim_lock:
                if not current():
                    return CommandReceipt(command_id, False, "disconnected", "guest HMI observation bridge changed", created)
            self.record_event(command_id, "observation_requested", {"module": "hmi"}, "hmi")
            try:
                value = observer()
                if not isinstance(value, dict):
                    raise ValueError("invalid HMI observation")
                with self._sim_lock:
                    if not current():
                        return CommandReceipt(command_id, False, "disconnected", "guest HMI observation bridge changed", created)
                    self._hmi_observed, self._hmi_observed_ns = deepcopy(value), time.time_ns()
                    observed_ns = self._hmi_observed_ns
                self.record_event(command_id, "completed", {"module": "hmi", "state": value,
                                  "observed_ns": observed_ns}, "hmi")
                return CommandReceipt(command_id, True, "completed", "new QML timer record observed; verify foreground with a fresh frame", created, observed_ns)
            except (OSError, ValueError, RuntimeError, EOFError, TimeoutError):
                with self._sim_lock:
                    valid = current()
                self.record_event(command_id, "observation_error", {"module": "hmi"}, "hmi")
                return CommandReceipt(command_id, False, "error" if valid else "disconnected", "guest HMI observation unavailable", created)

    def diagnose_module(self, *, module_id: str, correlation_id: Optional[str] = None) -> CommandReceipt:
        """Run only the fixed HMI diagnostic, preserving the last success."""
        from .transport import vm_transport_identifier
        if module_id != "hmi":
            raise ValueError("unknown diagnostic module")
        command_id, created = vm_transport_identifier(correlation_id), time.time_ns()
        with self._sim_lock:
            process, simulator, observer, diagnoser = self._process, self._simulator, self._hmi_observer, self._hmi_diagnoser
            if self._sim_shutdown or process is None or process.poll() is not None or diagnoser is None:
                return CommandReceipt(command_id, False, "disconnected", "guest diagnostic unavailable", created)
        self.record_event(command_id, "diagnostic_requested", {"module": "hmi"}, "hmi")
        if not self._diagnostic_lock.acquire(blocking=False):
            self.record_event(command_id, "diagnostic_error", {"module": "hmi", "reason": "busy"}, "hmi")
            return CommandReceipt(command_id, False, "busy", "guest diagnostic already running", created)
        try:
            try:
                value = diagnoser()
                if not isinstance(value, dict) or value.get("status") not in ("completed", "error"):
                    raise ValueError("invalid diagnostic result")
            except (OSError, ValueError, RuntimeError, EOFError, TimeoutError):
                value = {"status": "error", "failed_stage": "bridge", "reason": "stage_failed"}
            # Keep admission exclusive through validation, state and event
            # publication: a newer result must not be overwritten by this one.
            with self._sim_lock:
                current = (not self._sim_shutdown and self._process is process and process.poll() is None
                           and self._simulator is simulator and self._hmi_observer is observer and self._hmi_diagnoser is diagnoser)
                if not current:
                    self.record_event(command_id, "diagnostic_error", {"module": "hmi", "reason": "bridge_changed"}, "hmi")
                    return CommandReceipt(command_id, False, "disconnected", "guest diagnostic bridge changed", created)
                success = value["status"] == "completed"
                if success:
                    self._hmi_diagnostic = deepcopy(value)
                self.record_event(command_id, "diagnostic_completed" if success else "diagnostic_error",
                                  {"module": "hmi", "diagnostic": deepcopy(value)}, "hmi")
                return CommandReceipt(command_id, success, "completed" if success else "error",
                                      "diagnostic completed" if success else "diagnostic failed; see event log", created, time.time_ns())
        finally:
            self._diagnostic_lock.release()

    def get_events(self, *, after_id: int, limit: int) -> List[EventRecord]:
        """Return bounded ordered events after a caller's cursor."""

        if type(after_id) is not int or after_id < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("invalid event cursor or limit")
        with self._event_lock:
            return [item for item in self._events if item.event_id > after_id][:limit]

    def shutdown(self) -> CommandReceipt:
        """Stop only the process started by this runtime and reap it."""

        created = time.time_ns()
        self._closing.set()
        with self._lifecycle_lock:
            if self._process is None:
                return CommandReceipt("shutdown", False, "not_started", "no owned process", created)
            with self._sim_lock:
                self._sim_shutdown = True
            if not self._stop_owned(self._process):
                self.record_event("shutdown", "stop_failed", {"reason": "process_exit_timeout"}, "runtime")
                return CommandReceipt("shutdown", False, "error", "owned process did not exit before the shutdown deadline",
                                      created, time.time_ns())
            self.record_event("shutdown", "stopped", {"returncode": self._process.returncode}, "runtime")
        return CommandReceipt("shutdown", True, "completed", "owned process stopped", created, time.time_ns())
