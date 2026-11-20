"""Startup-aware facade for the local Gen5W browser service.

The HTTP server is intentionally started before VM preparation.  This facade
implements the existing :class:`WorkbenchBackend` contract while preparation is
in progress, then delegates to the admitted runtime backend without exposing a
second control API.
"""

from __future__ import annotations

from collections import deque
import threading
import time
from typing import Any, Callable, List, Mapping, Optional

from .contracts import CommandReceipt, EventRecord, FrameSnapshot, ModuleSnapshot


_TERMINAL_STATES = frozenset(("failed", "stopped"))


class WorkbenchServiceBackend:
    """Expose bounded startup progress and attach one runtime backend once."""

    def __init__(self, *, simulation_mode: bool = False, event_limit: int = 256):
        if type(simulation_mode) is not bool:
            raise TypeError("simulation_mode must be a boolean")
        if type(event_limit) is not int or not 16 <= event_limit <= 4096:
            raise ValueError("event_limit must be between 16 and 4096")
        self.simulation_mode = simulation_mode
        self.cancelled = threading.Event()
        self._lock = threading.RLock()
        self._backend = None
        self._state = "starting"
        self._stage = "service"
        self._message = "Browser service is starting"
        self._error_code = None
        self._progress = 0
        self._started_ns = time.time_ns()
        self._events = deque(maxlen=event_limit)
        self._event_sequence = 0
        self._record("service", "starting", {"stage": self._stage, "progress": 0})

    @staticmethod
    def _clean_text(value: Any, field: str, limit: int = 240) -> str:
        if not isinstance(value, str) or not value or len(value) > limit or any(c in value for c in "\r\n\0"):
            raise ValueError(field + " is invalid")
        return value

    def _record(self, component: str, event: str, detail: Mapping[str, Any]) -> None:
        self._event_sequence += 1
        self._events.append(EventRecord(self._event_sequence, time.time_ns(), "service",
                                        component, event, dict(detail)))

    def service_mark_progress(self, stage: str, progress: int, message: str) -> None:
        """Publish one monotonic, sanitized startup progress transition."""

        stage = self._clean_text(stage, "stage", 48)
        message = self._clean_text(message, "message")
        if type(progress) is not int or not 0 <= progress <= 99:
            raise ValueError("progress must be an integer from 0 to 99")
        with self._lock:
            if self._state != "starting":
                raise RuntimeError("startup progress is already terminal")
            if progress < self._progress:
                raise ValueError("startup progress cannot move backwards")
            self._stage, self._progress, self._message = stage, progress, message
            self._record("service", "progress", {"stage": stage, "progress": progress,
                                                   "message": message})

    def service_attach_backend(self, backend: Any) -> None:
        """Atomically attach the single admitted backend and publish readiness."""

        required = ("get_status", "get_frame", "send_pointer", "send_key", "get_modules",
                    "set_module_field", "observe_module", "diagnose_module", "get_events",
                    "observe_and_confirm_once", "shutdown")
        if backend is None or any(not callable(getattr(backend, name, None)) for name in required):
            raise TypeError("backend does not implement the workbench contract")
        with self._lock:
            if self._state != "starting" or self._backend is not None or self.cancelled.is_set():
                raise RuntimeError("service backend cannot be attached now")
            self._backend = backend
            self._state, self._stage, self._progress = "ready", "ready", 100
            self._message, self._error_code = "VM browser is ready", None
            self.simulation_mode = bool(getattr(backend, "simulation_mode", self.simulation_mode))
            self._record("service", "ready", {"stage": "ready", "progress": 100})

    def service_fail(self, code: str, message: str) -> None:
        """Publish one stable startup or admitted-runtime failure."""

        code = self._clean_text(code, "failure code", 48)
        message = self._clean_text(message, "failure message")
        with self._lock:
            if self._state not in ("starting", "ready"):
                raise RuntimeError("service failure is already terminal")
            self._state, self._stage = "failed", "failed"
            self._error_code, self._message = code, message
            self._record("service", "failed", {"code": code, "message": message})

    def service_stop(self, message: str = "Service stopped") -> None:
        """Mark startup as stopped and request bounded owner cleanup."""

        message = self._clean_text(message, "stop message")
        with self._lock:
            self.cancelled.set()
            if self._state not in _TERMINAL_STATES:
                self._state, self._stage, self._message = "stopped", "stopped", message
                self._record("service", "stopped", {"message": message})

    def get_status(self) -> Mapping[str, Any]:
        """Return the service lifecycle plus the attached runtime status."""

        with self._lock:
            backend = self._backend
            service_state = self._state
            result = {"state": self._state, "service_state": self._state,
                      "stage": self._stage, "progress": self._progress,
                      "message": self._message, "error_code": self._error_code,
                      "elapsed_ms": max(0, (time.time_ns() - self._started_ns) // 1_000_000),
                      "snapshot": True, "guest_network": False, "scope": "local-vm"}
            service_snapshot = dict(result)
        if backend is not None:
            runtime = dict(backend.get_status())
            result.update(runtime)
            if service_state == "ready":
                result.update({"service_state": "ready", "stage": "ready", "progress": 100,
                               "message": "VM browser is ready", "error_code": None})
            else:
                result.update(service_snapshot)
        return result

    def get_frame(self) -> FrameSnapshot:
        """Return the admitted backend frame or report that startup is incomplete."""

        with self._lock:
            backend = self._backend
        if backend is None:
            raise LookupError("VM frame is not ready")
        return backend.get_frame()

    def _refusal(self, correlation_id: Optional[str] = None) -> CommandReceipt:
        created = time.time_ns()
        with self._lock:
            state = self._state
        identifier = correlation_id if isinstance(correlation_id, str) and correlation_id else "service"
        return CommandReceipt(identifier, False, state, "VM controls are not ready", created, created)

    def _call(self, name: str, *, correlation_id: Optional[str] = None, **kwargs):
        with self._lock:
            backend = self._backend
        if backend is None:
            return self._refusal(correlation_id)
        return getattr(backend, name)(correlation_id=correlation_id, **kwargs)

    def send_pointer(self, *, action: str, x1: int, y1: int, x2: Optional[int] = None,
                     y2: Optional[int] = None, frame_sequence: Optional[int] = None,
                     correlation_id: Optional[str] = None) -> CommandReceipt:
        values = {"action": action, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
        if frame_sequence is not None:
            values["frame_sequence"] = frame_sequence
        return self._call("send_pointer", correlation_id=correlation_id, **values)

    def observe_and_confirm_once(self, *, frame_sequence: int,
                                 correlation_id: Optional[str] = None) -> CommandReceipt:
        return self._call("observe_and_confirm_once", frame_sequence=frame_sequence,
                          correlation_id=correlation_id)

    def send_key(self, *, action: str, key: str,
                 correlation_id: Optional[str] = None) -> CommandReceipt:
        return self._call("send_key", action=action, key=key, correlation_id=correlation_id)

    def get_modules(self) -> List[ModuleSnapshot]:
        with self._lock:
            backend = self._backend
        return [] if backend is None else backend.get_modules()

    def set_module_field(self, *, module_id: str, field: str, value: Any,
                         correlation_id: Optional[str] = None) -> CommandReceipt:
        return self._call("set_module_field", module_id=module_id, field=field, value=value,
                          correlation_id=correlation_id)

    def observe_module(self, *, module_id: str,
                       correlation_id: Optional[str] = None) -> CommandReceipt:
        return self._call("observe_module", module_id=module_id, correlation_id=correlation_id)

    def diagnose_module(self, *, module_id: str,
                        correlation_id: Optional[str] = None) -> CommandReceipt:
        return self._call("diagnose_module", module_id=module_id, correlation_id=correlation_id)

    def get_events(self, *, after_id: int, limit: int) -> List[EventRecord]:
        """Return stable startup events followed by offset runtime events."""

        if type(after_id) is not int or after_id < 0 or type(limit) is not int or limit < 1:
            raise ValueError("invalid event query")
        with self._lock:
            startup = list(self._events)
            offset = self._event_sequence
            backend = self._backend
        result = [event for event in startup if event.event_id > after_id][:limit]
        if backend is None or len(result) >= limit:
            return result
        runtime_after = max(0, after_id - offset)
        for event in backend.get_events(after_id=runtime_after, limit=limit - len(result)):
            result.append(EventRecord(offset + event.event_id, event.timestamp_ns, event.correlation_id,
                                      event.component, event.event, event.detail))
        return result

    def shutdown(self) -> CommandReceipt:
        """Cancel startup or delegate bounded shutdown to the attached backend."""

        with self._lock:
            backend = self._backend
        self.cancelled.set()
        if backend is None:
            self.service_stop("Stop requested before VM readiness")
            return self._refusal("shutdown")
        receipt = backend.shutdown()
        with self._lock:
            self._state, self._stage, self._message = "stopped", "stopped", "VM stopped"
            self._record("service", "stopped", {"message": "VM stopped"})
        return receipt


def service_run_worker(service: WorkbenchServiceBackend, operation: Callable[[], Any],
                       on_ready: Callable[[Any], Any]) -> threading.Thread:
    """Run one startup operation and publish its bounded terminal outcome."""

    if not isinstance(service, WorkbenchServiceBackend) or not callable(operation) or not callable(on_ready):
        raise TypeError("invalid service worker arguments")

    def run() -> None:
        try:
            backend = operation()
            if service.cancelled.is_set():
                shutdown = getattr(backend, "shutdown", None)
                if callable(shutdown):
                    shutdown()
                return
            on_ready(backend)
            service.service_attach_backend(backend)
        except Exception as exc:
            if not service.cancelled.is_set():
                code = type(exc).__name__.lower()
                lines = str(exc).splitlines()
                message = lines[0][:240] if lines and lines[0] else "VM startup failed"
                service.service_fail(code, message)

    thread = threading.Thread(target=run, name="gen5w-startup", daemon=True)
    thread.start()
    return thread
