"""Bounded, serialized workbench channels and compositor-frame validation.

The JSON-line transport is an adapter boundary, not a claim that an existing
guest speaks this protocol. A guest bridge must explicitly implement it. All
operations are typed and no shell command is accepted by this module.
"""

from __future__ import annotations

import json
import re
import socket
import struct
import threading
import time
import uuid
import zlib
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

from .contracts import CommandReceipt, FrameSnapshot, GUEST_HEIGHT, GUEST_WIDTH

MAX_MESSAGE = 8192
MAX_FRAME = 16 * 1024 * 1024
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_KEY = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
_EVDEV_KEYS = dict(zip(
    ("KeyQ", "KeyW", "KeyE", "KeyR", "KeyT", "KeyY", "KeyU", "KeyI", "KeyO", "KeyP",
     "KeyA", "KeyS", "KeyD", "KeyF", "KeyG", "KeyH", "KeyJ", "KeyK", "KeyL",
     "KeyZ", "KeyX", "KeyC", "KeyV", "KeyB", "KeyN", "KeyM",
     "Digit1", "Digit2", "Digit3", "Digit4", "Digit5", "Digit6", "Digit7", "Digit8", "Digit9", "Digit0",
     "Escape", "Backspace", "Tab", "Enter", "Space", "ArrowUp", "ArrowLeft", "ArrowRight", "ArrowDown"),
    (16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 30, 31, 32, 33, 34, 35, 36, 37, 38,
     44, 45, 46, 47, 48, 49, 50, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 14, 15, 28, 57, 103, 105, 106, 108)))


def vm_transport_identifier(value: Optional[str]) -> str:
    """Validate an operator correlation identifier or allocate one."""

    if value is None:
        return uuid.uuid4().hex
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError("correlation_id must be 1-64 ASCII letters, digits, _ or -")
    return value


def vm_transport_pointer(action: str, x1: int, y1: int,
                         x2: Optional[int] = None,
                         y2: Optional[int] = None) -> Dict[str, Any]:
    """Validate a click or drag in fixed guest coordinates."""

    if action not in ("click", "drag", "pdrag"):
        raise ValueError("unsupported pointer action")
    points = [(x1, y1)]
    if action == "click":
        if x2 is not None or y2 is not None:
            raise ValueError("click accepts exactly one point")
    else:
        points.append((x2, y2))
    for x, y in points:
        if type(x) is not int or type(y) is not int or not (0 <= x < GUEST_WIDTH and 0 <= y < GUEST_HEIGHT):
            raise ValueError("pointer coordinates outside guest frame")
    result = {"type": "pointer", "action": action, "x1": x1, "y1": y1}
    if action != "click":
        result.update(x2=x2, y2=y2)
    return result


def vm_transport_key(action: str, key: str) -> Dict[str, Any]:
    """Validate a key operation; guest support is separately acknowledged."""

    if action not in ("press", "release", "tap"):
        raise ValueError("unsupported key action")
    if not isinstance(key, str) or not _KEY.fullmatch(key):
        raise ValueError("invalid key name")
    return {"type": "key", "action": action, "key": key}


class JsonLineSocket:
    """Exchange one bounded JSON request and response on an owned local socket.

    The caller supplies an already-connected socket, allowing Unix socket and
    socketpair fixtures without this adapter discovering or connecting devices.
    """

    def __init__(self, sock: socket.socket):
        self._socket = sock
        self._buffer = bytearray()

    def exchange(self, request: Mapping[str, Any], timeout: float) -> Mapping[str, Any]:
        """Send one message and receive exactly one complete bounded reply."""

        if not 0 < timeout <= 60:
            raise ValueError("timeout must be between 0 and 60 seconds")
        encoded = json.dumps(dict(request), separators=(",", ":"), allow_nan=False).encode("utf-8") + b"\n"
        if len(encoded) > MAX_MESSAGE:
            raise ValueError("request exceeds transport limit")
        deadline = time.monotonic() + timeout
        self._socket.settimeout(timeout)
        self._socket.sendall(encoded)
        while b"\n" not in self._buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("guest acknowledgement timed out")
            self._socket.settimeout(remaining)
            try:
                chunk = self._socket.recv(min(4096, MAX_MESSAGE + 1 - len(self._buffer)))
            except socket.timeout as exc:
                raise TimeoutError("guest acknowledgement timed out") from exc
            if not chunk:
                raise EOFError("guest channel closed before acknowledgement")
            self._buffer.extend(chunk)
            if len(self._buffer) > MAX_MESSAGE:
                raise ValueError("guest response exceeds transport limit")
        line, _, rest = self._buffer.partition(b"\n")
        self._buffer = bytearray(rest)
        try:
            reply = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("malformed guest response") from exc
        if not isinstance(reply, dict):
            raise ValueError("guest response must be an object")
        return reply


class SequencedTransport:
    """Serialize typed requests and distinguish delivery from guest response."""

    def __init__(self, exchange: Callable[[Mapping[str, Any], float], Mapping[str, Any]],
                 event: Callable[[str, str, Mapping[str, Any]], None], timeout: float = 3.0):
        if not 0 < timeout <= 60:
            raise ValueError("timeout must be between 0 and 60 seconds")
        self._exchange, self._event, self._timeout = exchange, event, timeout
        self._lock = threading.Lock()
        self._sequence = 0

    def send(self, operation: Mapping[str, Any], correlation_id: Optional[str] = None) -> CommandReceipt:
        """Send one request, waiting for its exact matching acknowledgement.

        Failure is returned as a receipt. A timeout never causes an automatic
        retry because the guest may have executed the original request.
        """

        command_id = vm_transport_identifier(correlation_id)
        created = time.time_ns()
        with self._lock:
            self._sequence += 1
            sequence = self._sequence
            request = {"sequence": sequence, "command_id": command_id, "operation": dict(operation)}
            self._event(command_id, "sent", {"sequence": sequence, "operation": dict(operation)})
            try:
                reply = self._exchange(request, self._timeout)
                if (not isinstance(reply, Mapping) or set(reply) != {"sequence", "command_id", "state", "message"}
                        or type(reply["sequence"]) is not int or reply["sequence"] != sequence
                        or reply["command_id"] != command_id
                        or reply["state"] not in ("accepted", "completed", "unsupported", "error")
                        or not isinstance(reply["message"], str) or len(reply["message"]) > 512):
                    raise ValueError("invalid or mismatched guest acknowledgement")
                acknowledged = time.time_ns()
                state = reply["state"]
                self._event(command_id, "acknowledged", {"sequence": sequence, "state": state})
                return CommandReceipt(command_id, state in ("accepted", "completed"), state,
                                      reply["message"], created, acknowledged)
            except (OSError, ValueError, EOFError, TimeoutError) as exc:
                state = "timeout" if isinstance(exc, TimeoutError) else "error"
                self._event(command_id, state, {"sequence": sequence, "message": str(exc)})
                return CommandReceipt(command_id, False, state, str(exc), created)


def vm_transport_png_dimensions(raw: bytes) -> Tuple[int, int]:
    """Validate a complete bounded PNG and return its dimensions.

    Chunk CRCs and ordering are checked to reject partial serial captures. The
    compositor is the authority for the pixel contents, not this parser.
    """

    if not isinstance(raw, bytes) or len(raw) > MAX_FRAME or not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("invalid or oversized PNG frame")
    offset, width, height, seen_idat, finished = 8, 0, 0, False, False
    while offset + 12 <= len(raw):
        size = struct.unpack_from(">I", raw, offset)[0]
        if size > MAX_FRAME or offset + size + 12 > len(raw):
            raise ValueError("truncated PNG chunk")
        kind = raw[offset + 4:offset + 8]
        data = raw[offset + 8:offset + 8 + size]
        expected = struct.unpack_from(">I", raw, offset + 8 + size)[0]
        if zlib.crc32(kind + data) & 0xffffffff != expected:
            raise ValueError("PNG chunk checksum mismatch")
        if offset == 8:
            if kind != b"IHDR" or size != 13:
                raise ValueError("PNG must begin with IHDR")
            width, height = struct.unpack_from(">II", data)
            if not 0 < width <= 4096 or not 0 < height <= 4096:
                raise ValueError("PNG dimensions out of bounds")
        elif kind == b"IHDR":
            raise ValueError("duplicate PNG IHDR")
        if kind == b"IDAT":
            seen_idat = True
        offset += size + 12
        if kind == b"IEND":
            if size or not seen_idat or offset != len(raw):
                raise ValueError("invalid PNG ending")
            finished = True
            break
    if not finished:
        raise ValueError("incomplete PNG frame")
    return width, height


class FrameStore:
    """Store one validated frame and mark it stale based on its age."""

    def __init__(self, stale_seconds: float = 5.0):
        if not 0 < stale_seconds <= 3600:
            raise ValueError("invalid stale frame interval")
        self._stale_ns = int(stale_seconds * 1_000_000_000)
        self._lock = threading.Lock()
        self._frame: Optional[FrameSnapshot] = None
        self._sequence = 0

    def publish(self, payload: bytes, source: str, *, historical: bool = False) -> FrameSnapshot:
        """Publish a complete PNG, keeping fixture source explicit."""

        if source not in ("guest-compositor", "fixture", "replay"):
            raise ValueError("invalid frame source")
        width, height = vm_transport_png_dimensions(payload)
        with self._lock:
            self._sequence += 1
            self._frame = FrameSnapshot(self._sequence, time.time_ns(), width, height,
                                        "image/png", payload, source, historical)
            return self._frame

    def get(self, disconnected: bool = False) -> FrameSnapshot:
        """Return the latest frame, or a clear error until one arrives."""

        with self._lock:
            frame = self._frame
        if frame is None:
            raise LookupError("no compositor frame available")
        stale = frame.stale or disconnected or time.time_ns() - frame.captured_ns > self._stale_ns
        return FrameSnapshot(frame.sequence, frame.captured_ns, frame.width, frame.height,
                             frame.mime_type, frame.payload, frame.source, stale)


class GuestMailbox:
    """Serialize exact Weston input mailbox operations over an injected bridge.

    ``publish`` must atomically create the guest command only if absent;
    ``read_result`` reads a complete result or returns None. They are callbacks
    because guest paths are not host files and require an explicit VM bridge.
    A timed-out command poisons the channel until its result is reconciled by
    the caller, preventing a later command from overwriting an uncertain action.
    """

    def __init__(self, publish: Callable[[str], None], read_result: Callable[[], Optional[str]],
                 event: Callable[[str, str, Mapping[str, Any]], None],
                 timeout: float = 3.0, poll_interval: float = 0.05,
                 bounded_publish: Optional[Callable[[str, float, int], bool]] = None):
        if not 0 < timeout <= 60 or not 0 < poll_interval <= timeout:
            raise ValueError("invalid mailbox timeout or polling interval")
        self._publish, self._read_result, self._event = publish, read_result, event
        self._timeout, self._poll = timeout, poll_interval
        self._lock = threading.RLock()
        self._bounded_publish = bounded_publish
        self._sequence = 0
        self._uncertain = False

    def send(self, operation: Mapping[str, Any], correlation_id: Optional[str] = None, *, _deadline=None, _guest_expiry=None) -> CommandReceipt:
        """Publish one typed input and await its matching terminal result."""

        command_id = vm_transport_identifier(correlation_id)
        created = time.time_ns()
        if operation.get("type") == "pointer":
            checked = vm_transport_pointer(operation.get("action"), operation.get("x1"),
                                           operation.get("y1"), operation.get("x2"), operation.get("y2"))
            fields = [checked["action"], str(checked["x1"]), str(checked["y1"])]
            if checked["action"] != "click":
                fields.extend((str(checked["x2"]), str(checked["y2"])))
        elif operation.get("type") == "key":
            checked = vm_transport_key(operation.get("action"), operation.get("key"))
            if checked["action"] != "tap":
                return CommandReceipt(command_id, False, "unsupported",
                                      "guest mailbox supports key tap only", created)
            code = _EVDEV_KEYS.get(checked["key"])
            if code is None:
                return CommandReceipt(command_id, False, "unsupported",
                                      "key has no validated evdev mapping", created)
            fields = ["key", str(code)]
        else:
            raise ValueError("unsupported mailbox operation")
        with self._lock:
            if self._uncertain:
                return CommandReceipt(command_id, False, "uncertain", "previous command needs reconciliation", created)
            self._sequence += 1
            sequence = self._sequence
            if _deadline is not None:
                if checked.get("type") != "pointer" or checked.get("action") != "click" or type(_guest_expiry) is not int or _guest_expiry <= 0:
                    raise ValueError("invalid bounded click")
                fields = ["cclick", str(checked["x1"]), str(checked["y1"]), str(_guest_expiry)]
            line = "seq {} {}\n".format(sequence, " ".join(fields))
            try:
                if _deadline is None:
                    self._publish(line)
                else:
                    if self._bounded_publish is None or time.monotonic() >= _deadline:
                        self._event(command_id, "expired", {"sequence": sequence, "published": False})
                        return CommandReceipt(command_id, False, "expired", "bounded publication unavailable or expired", created)
                    if not self._bounded_publish(line, _deadline, _guest_expiry):
                        self._event(command_id, "expired", {"sequence": sequence, "published": False})
                        return CommandReceipt(command_id, False, "expired", "guest publication window expired", created)
                self._event(command_id, "sent", {"sequence": sequence, "operation": checked})
                deadline = time.monotonic() + self._timeout
                accepted_at = None
                while time.monotonic() < deadline:
                    result = self._read_result()
                    if result is None:
                        time.sleep(min(self._poll, max(0, deadline - time.monotonic())))
                        continue
                    if not isinstance(result, str) or len(result) > 1024:
                        raise ValueError("malformed mailbox result")
                    match = re.fullmatch(r"seq ([1-9][0-9]*) (accepted|completed|error) ([^\r\n]{1,512})\n", result)
                    if not match:
                        raise ValueError("malformed mailbox result")
                    received_sequence, state, message = match.groups()
                    if int(received_sequence) < sequence:
                        # The result file may still contain the preceding command.
                        time.sleep(min(self._poll, max(0, deadline - time.monotonic())))
                        continue
                    if int(received_sequence) != sequence:
                        raise ValueError("unexpected future mailbox sequence")
                    if state == "accepted":
                        if accepted_at is None:
                            accepted_at = time.time_ns()
                            self._event(command_id, "accepted", {"sequence": sequence})
                        time.sleep(min(self._poll, max(0, deadline - time.monotonic())))
                        continue
                    acknowledged = time.time_ns()
                    self._event(command_id, state, {"sequence": sequence, "message": message})
                    return CommandReceipt(command_id, state == "completed", state, message, created, acknowledged)
                raise TimeoutError("guest mailbox terminal acknowledgement timed out")
            except (OSError, ValueError, RuntimeError, EOFError, TimeoutError) as exc:
                if _deadline is None and isinstance(exc, RuntimeError):
                    raise
                self._uncertain = True
                state = "timeout" if isinstance(exc, TimeoutError) else "error"
                self._event(command_id, state, {"sequence": sequence, "message": str(exc), "uncertain": True})
                return CommandReceipt(command_id, False, state, str(exc), created)

    def send_once(self, operation: Mapping[str, Any], correlation_id: str, deadline: float, guest_expiry_ms: int) -> CommandReceipt:
        """Publish at most once without waiting for an occupied mailbox."""
        command_id = vm_transport_identifier(correlation_id)
        created = time.time_ns()
        if not self._lock.acquire(blocking=False):
            return CommandReceipt(command_id, False, "busy", "input mailbox busy", created)
        try:
            return self.send(operation, command_id, _deadline=deadline, _guest_expiry=guest_expiry_ms)
        finally:
            self._lock.release()


class SimulatorMailbox:
    """Serialize the simulator's typed debug-byte and IHU parking APIs."""

    def __init__(self, publish: Callable[[str], None], read_result: Callable[[], Optional[str]],
                 event: Callable[[str, str, Mapping[str, Any]], None],
                 timeout: float = 3.0, poll_interval: float = 0.05):
        if not 0 < timeout <= 60 or not 0 < poll_interval <= timeout:
            raise ValueError("invalid simulator timeout or polling interval")
        self._publish, self._read_result, self._event = publish, read_result, event
        self._timeout, self._poll = timeout, poll_interval
        self._lock = threading.Lock()
        self._uncertain = False
        self._used_ids = set()

    def request(self, value: Optional[int] = None, correlation_id: Optional[str] = None,
                *, field: str = "debug_count") -> Tuple[CommandReceipt, Optional[int]]:
        """Get or set one supported simulator field and return its receipt."""

        command_id = vm_transport_identifier(correlation_id)
        if len(command_id) > 32:
            raise ValueError("simulator command ID exceeds 32 characters")
        if field not in ("debug_count", "parking_status"):
            raise ValueError("unknown simulator field")
        if value is not None and (type(value) is not int or not 0 <= value <= (1 if field == "parking_status" else 255)):
            raise ValueError("invalid simulator value")
        evidence = "recovered-ihu-parking-status" if field == "parking_status" else "recovered-consumer-byte0"
        created = time.time_ns()
        with self._lock:
            if self._uncertain:
                return CommandReceipt(command_id, False, "uncertain", "previous request needs reconciliation", created), None
            if command_id in self._used_ids:
                raise ValueError("simulator command ID has already been used")
            if len(self._used_ids) >= 10000:
                raise ValueError("simulator session command limit reached")
            self._used_ids.add(command_id)
            line = f"{command_id} GET {field}\n" if value is None else f"{command_id} SET {field} {value}\n"
            try:
                self._publish(line)
                self._event(command_id, "sent", {"field": field, "configured": value})
                deadline = time.monotonic() + self._timeout
                while time.monotonic() < deadline:
                    result = self._read_result()
                    if result is None:
                        time.sleep(min(self._poll, max(0, deadline - time.monotonic())))
                        continue
                    if not isinstance(result, str) or len(result) > 1024:
                        raise ValueError("malformed simulator reply")
                    match = re.fullmatch(r"([A-Za-z0-9_-]{1,32}) OK " + field + r" ([0-9]{1,3}) evidence=" + evidence + r"\n", result)
                    error = re.fullmatch(r"([A-Za-z0-9_-]{1,32}) ERR ([^\r\n]{1,512})\n", result)
                    if error and error.group(1) == command_id:
                        self._event(command_id, "error", {"message": error.group(2)})
                        return CommandReceipt(command_id, False, "error", error.group(2), created, time.time_ns()), None
                    if (match and match.group(1) != command_id) or (error and error.group(1) != command_id):
                        # The atomic reply file may still hold a previous request.
                        time.sleep(min(self._poll, max(0, deadline - time.monotonic())))
                        continue
                    if not match or int(match.group(2)) > (1 if field == "parking_status" else 255):
                        raise ValueError("malformed or mismatched simulator reply")
                    observed = int(match.group(2))
                    if value is not None and observed != value:
                        raise ValueError("simulator acknowledged a different value")
                    self._event(command_id, "acknowledged", {"field": field, "value": observed,
                                                             "evidence": evidence})
                    return CommandReceipt(command_id, True, "completed", "simulator acknowledged", created, time.time_ns()), observed
                raise TimeoutError("simulator acknowledgement timed out")
            except (OSError, ValueError, EOFError, TimeoutError) as exc:
                self._uncertain = True
                state = "timeout" if isinstance(exc, TimeoutError) else "error"
                self._event(command_id, state, {"message": str(exc), "uncertain": True})
                return CommandReceipt(command_id, False, state, str(exc), created), None
