"""One-shot, reference-bound Confirm action for the isolated VM workbench."""

import hashlib
import math
import threading
import time

from .contracts import CommandReceipt
from .transport import vm_transport_identifier, vm_transport_pointer


class ConfirmAction:
    """Own admission, consumed references and uncertainty for one VM runtime."""

    def __init__(self, frame, session, event):
        self._frame, self._session, self._event = frame, session, event
        self._lock = threading.Lock()
        self._active = False
        self._manual = 0
        self._used = set()
        self._ids = set()
        self._uncertain = False

    def acquire(self):
        """Acquire the action lease without queuing."""
        with self._lock:
            if self._active or self._manual:
                return False
            self._active = True
            return True

    def release(self):
        """Release a lease acquired by this thread."""
        with self._lock:
            self._active = False

    def acquire_manual(self):
        """Admit normal work concurrently unless a compound action owns the lease."""
        with self._lock:
            if self._active:
                return False
            self._manual += 1
            return True

    def release_manual(self):
        """Release a normal-work admission."""
        with self._lock:
            self._manual -= 1

    @staticmethod
    def _center(model):
        if not isinstance(model, dict) or any(model.get(k) is not v for k, v in
                (("enabled", True), ("visible", True), ("dimmed", False), ("driving", False), ("calling", False))):
            raise ValueError("unsafe or invalid Confirm state")
        if type(model.get("modelEnableBtn")) is not int or model["modelEnableBtn"] != 1:
            raise ValueError("Confirm model is disabled")
        rect = model.get("buttonRoot")
        if not isinstance(rect, (list, tuple)) or len(rect) != 4 or any(type(v) not in (int, float) or not math.isfinite(v) for v in rect):
            raise ValueError("invalid Confirm geometry")
        x, y, width, height = rect
        if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 1920 or y + height > 720:
            raise ValueError("Confirm geometry outside display")
        cx, cy = math.floor(x + width / 2), math.floor(y + height / 2)
        if not (x < cx < x + width and y < cy < y + height):
            raise ValueError("Confirm has no interior pixel")
        return cx, cy

    def run(self, sequence, correlation_id=None):
        """Pin a live reference, verify state and frame, and publish at most once."""
        command_id, created = vm_transport_identifier(correlation_id), time.time_ns()
        if type(sequence) is not int or not 1 <= sequence <= 2**53 - 1:
            raise ValueError("invalid frame sequence")
        def result(state, message, accepted=False):
            self._event(command_id, "confirm_result", {"state": state, "message": message}, "hmi")
            return CommandReceipt(command_id, accepted, state, message, created, time.time_ns())
        if not self.acquire():
            return result("busy", "Confirm action or input is busy")
        try:
            if self._uncertain:
                return result("uncertain", "previous publication requires reconciliation")
            session = self._session()
            if session is None:
                return result("disconnected", "guest bridge unavailable")
            try:
                reference = self._frame()
            except LookupError:
                return result("stale", "approved frame is unavailable")
            if (reference.sequence != sequence or reference.stale or reference.source != "guest-compositor" or
                    reference.mime_type != "image/png" or (reference.width, reference.height) != (1920, 720) or
                    not isinstance(reference.payload, bytes) or not reference.payload):
                return result("stale", "approved frame is stale or not a live compositor frame")
            if sequence in self._used or command_id in self._ids:
                return result("duplicate", "approved frame was already used")
            if len(self._used) >= 10000:
                return result("limit", "Confirm action session limit reached")
            self._used.add(sequence)
            self._ids.add(command_id)
            digest = hashlib.sha256(reference.payload).hexdigest()
            self._event(command_id, "confirm_preparation", {"reference_sequence": sequence, "reference_sha256": digest,
                        "width": reference.width, "height": reference.height, "source": reference.source}, "hmi")
            started = time.monotonic()
            deadline = started + 6.0
            bridge, mailbox = session[1], session[2]
            def current():
                current_session = self._session()
                return (current_session is not None and all(a is b for a, b in zip(current_session, session)) and
                        len(current_session) == len(session) and bridge.is_available() and time.monotonic() < deadline)
            try:
                with bridge.compound_lease():
                    if not current(): return result("disconnected", "guest session changed")
                    model = bridge.observe_confirm_geometry(deadline=deadline)
                    if not current(): return result("expired", "observation deadline or session changed")
                    x, y = self._center(model)
                    self._event(command_id, "confirm_observation", {"state": model, "x": x, "y": y}, "hmi")
                    raw, guest_ms = bridge.capture_timed(deadline)
                    if not current(): return result("expired", "capture deadline or session changed")
                    if type(guest_ms) is not int or guest_ms <= 0 or not isinstance(raw, bytes):
                        return result("error", "invalid fresh capture")
                    fresh_hash = hashlib.sha256(raw).hexdigest()
                    self._event(command_id, "confirm_reference", {"reference_sequence": sequence, "reference_sha256": digest,
                                "fresh_sha256": fresh_hash, "equal": raw == reference.payload}, "display")
                    if raw != reference.payload:
                        return result("changed", "fresh frame differs from approved frame")
                    if self._frame() != reference or not current():
                        return result("stale", "approved frame or session changed")
                    publication_deadline = min(deadline, time.monotonic() + 1.0)
                    # Linux /proc/uptime and the input consumer both use
                    # suspend-inclusive boottime. Reserve its centisecond tick.
                    receipt = mailbox.send_once(vm_transport_pointer("click", x, y), command_id,
                                                publication_deadline, guest_ms + 990)
                    self._event(command_id, "confirm_click_receipt", receipt.to_dict(), "input")
                    self._event(command_id, "confirm_visible_result", {"state": "not_observed", "causality": "not_established"}, "display")
                    if receipt.state == "error" and receipt.message == "expired":
                        return result("expired", "guest rejected the expired pointer click")
                    if receipt.state in ("timeout", "error", "uncertain"):
                        self._uncertain = True
                        return result("uncertain", "publication or acknowledgement is uncertain; retry disabled")
                    return receipt
            except BlockingIOError:
                return result("busy", "guest serial bridge busy")
            except (OSError, EOFError, RuntimeError, ValueError, TimeoutError) as exc:
                return result("error", str(exc))
        finally:
            self.release()
