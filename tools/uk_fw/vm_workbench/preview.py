"""Asset-free synthetic workbench backend for preview-service qualification."""

from __future__ import annotations

from collections import deque
import struct
import threading
import time
from typing import Any, Mapping, Optional
import zlib

from .contracts import (
    CommandReceipt,
    EventRecord,
    FrameSnapshot,
    GUEST_HEIGHT,
    GUEST_WIDTH,
    ModuleField,
    ModuleSnapshot,
)
from .transport import vm_transport_identifier, vm_transport_key, vm_transport_pointer


PREVIEW_SOURCE = "fixture"
PREVIEW_MODULE_ID = "fixture"
PREVIEW_FIELD_NAME = "fixture_level"
PREVIEW_DETAILS_POINT = (1410, 380)
PREVIEW_SLIDER_START = (850, 545)
PREVIEW_SLIDER_END = (1180, 545)

_WIDTH, _HEIGHT = GUEST_WIDTH, GUEST_HEIGHT
_DETAILS_BUTTON = (1240, 330, 1580, 430)
_SLIDER_DRAG_AREA = (700, 500, 1350, 590)
_SLIDER_TRACK = (730, 568, 620, 18)

_BACKGROUND = (9, 14, 20)
_PANEL = (20, 31, 42)
_PANEL_ALT = (25, 39, 52)
_INK = (235, 241, 244)
_MUTED = (142, 158, 169)
_GOLD = (222, 173, 74)
_BLUE = (55, 135, 190)
_GREEN = (73, 182, 139)
_WARNING = (214, 111, 64)

_FONT = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    "/": ("00001", "00010", "00100", "01000", "10000", "00000", "00000"),
    ":": ("00000", "00110", "00110", "00000", "00110", "00110", "00000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
}


def _chunk(kind: bytes, payload: bytes) -> bytes:
    """Encode one checksummed PNG chunk."""

    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def _png(pixels: bytearray) -> bytes:
    """Encode a filter-zero RGB canvas with explicit synthetic provenance."""

    stride = _WIDTH * 3
    rows = b"".join(b"\x00" + bytes(pixels[offset:offset + stride])
                    for offset in range(0, len(pixels), stride))
    header = struct.pack(">IIBBBBB", _WIDTH, _HEIGHT, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header)
            + _chunk(b"tEXt", b"Software\x00Gen5W synthetic host fixture")
            + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b""))


def _rectangle(pixels: bytearray, bounds, color) -> None:
    """Fill an axis-aligned rectangle clipped to the canvas."""

    x, y, width, height = bounds
    left, top = max(0, x), max(0, y)
    right, bottom = min(_WIDTH, x + width), min(_HEIGHT, y + height)
    if right <= left or bottom <= top:
        return
    color_bytes = bytes(color)
    for row in range(top, bottom):
        offset = (row * _WIDTH + left) * 3
        pixels[offset:offset + (right - left) * 3] = color_bytes * (right - left)


def _text(pixels: bytearray, x: int, y: int, value: str, color, scale: int = 3) -> None:
    """Draw bounded uppercase fixture text using an original 5x7 glyph set."""

    cursor = x
    for character in value.upper():
        glyph = _FONT.get(character, _FONT[" "])
        for row, bits in enumerate(glyph):
            for column, bit in enumerate(bits):
                if bit == "1":
                    _rectangle(pixels, (cursor + column * scale, y + row * scale,
                                        scale, scale), color)
        cursor += 6 * scale


def _panel(pixels: bytearray, x: int, y: int, width: int, height: int, accent=_BLUE) -> None:
    """Draw one unframed fixture panel with a narrow accent rule."""

    _rectangle(pixels, (x, y, width, height), _PANEL)
    _rectangle(pixels, (x, y, 5, height), accent)


def _render_home(level: int, control: float) -> bytes:
    pixels = bytearray(bytes(_BACKGROUND) * (_WIDTH * _HEIGHT))
    _rectangle(pixels, (0, 0, _WIDTH, 96), _PANEL_ALT)
    _rectangle(pixels, (0, 92, _WIDTH, 4), _GOLD)
    _rectangle(pixels, (0, 96, 292, _HEIGHT - 96), (15, 23, 31))
    _text(pixels, 38, 28, "WORKBENCH", _GOLD, 3)
    _text(pixels, 38, 57, "SYNTHETIC FIXTURE", _MUTED, 2)
    _rectangle(pixels, (24, 154, 244, 64), _PANEL)
    _text(pixels, 44, 174, "HOME", _INK, 3)
    _text(pixels, 44, 254, "DETAILS", _MUTED, 3)
    _text(pixels, 344, 135, "FIXTURE HOME", _INK, 5)
    _text(pixels, 348, 183, "HOST-ONLY UI - NO OEM ASSETS", _MUTED, 2)
    _panel(pixels, 344, 238, 710, 210, _GOLD)
    _text(pixels, 382, 274, "FIXTURE LEVEL", _MUTED, 2)
    _text(pixels, 382, 316, f"{level:02d}", _GOLD, 8)
    _text(pixels, 382, 396, "TYPED MODULE VALUE", _MUTED, 2)
    _panel(pixels, 1240, 238, 560, 210, _BLUE)
    _text(pixels, 1280, 277, "DETAILS PAGE", _INK, 3)
    button_left, button_top, button_right, button_bottom = _DETAILS_BUTTON
    _rectangle(pixels, (button_left, button_top, button_right - button_left,
                        button_bottom - button_top), _BLUE)
    _text(pixels, 1312, 362, "OPEN DETAILS", _INK, 3)
    _panel(pixels, 344, 500, 1456, 165, _GREEN)
    _text(pixels, 382, 525, "DRAG THE FIXTURE CONTROL", _INK, 3)
    track_x, track_y, track_width, _ = _SLIDER_TRACK
    _rectangle(pixels, _SLIDER_TRACK, (44, 58, 67))
    knob_x = track_x + int((track_width - 24) * control)
    _rectangle(pixels, (knob_x, track_y - 17, 24, 52), _GOLD)
    _text(pixels, 382, 607, "FRAME-BOUND INPUT - ESCAPE RETURNS HOME", _MUTED, 2)
    return _png(pixels)


def _render_details(level: int, control: float) -> bytes:
    pixels = bytearray(bytes(_BACKGROUND) * (_WIDTH * _HEIGHT))
    _rectangle(pixels, (0, 0, _WIDTH, 96), _PANEL_ALT)
    _rectangle(pixels, (0, 92, _WIDTH, 4), _GOLD)
    _rectangle(pixels, (0, 96, 292, _HEIGHT - 96), (15, 23, 31))
    _text(pixels, 38, 28, "WORKBENCH", _GOLD, 3)
    _text(pixels, 38, 57, "SYNTHETIC FIXTURE", _MUTED, 2)
    _text(pixels, 44, 174, "HOME", _MUTED, 3)
    _rectangle(pixels, (24, 234, 244, 64), _PANEL)
    _text(pixels, 44, 254, "DETAILS", _INK, 3)
    _text(pixels, 344, 135, "FIXTURE DETAILS", _INK, 5)
    _text(pixels, 348, 183, "SOURCE FIXTURE - SYNTHETIC HOST PIXELS", _MUTED, 2)
    cards = (
        (344, "SNAPSHOT", "OFF", _WARNING),
        (720, "GUEST NETWORK", "OFF", _WARNING),
        (1096, "FRAME SOURCE", "FIXTURE", _BLUE),
        (1472, "FIXTURE LEVEL", f"{level:02d}", _GOLD),
    )
    for x, label, value, accent in cards:
        _panel(pixels, x, 256, 328, 168, accent)
        _text(pixels, x + 28, 292, label, _MUTED, 2)
        _text(pixels, x + 28, 342, value, accent, 4)
    _panel(pixels, 344, 476, 1456, 166, _GREEN)
    _text(pixels, 382, 514, "CONTROL POSITION", _MUTED, 2)
    _text(pixels, 382, 558, f"{int(control * 100):03d} PERCENT", _GREEN, 4)
    _text(pixels, 1050, 563, "PRESS ESCAPE TO RETURN HOME", _INK, 2)
    track_x, track_y, track_width, _ = _SLIDER_TRACK
    _rectangle(pixels, (1050, track_y - 90, track_width - 50, 18), (44, 58, 67))
    _rectangle(pixels, (1050 + int((track_width - 74) * control), track_y - 108, 24, 52), _GOLD)
    return _png(pixels)


class PreviewBackend:
    """Provide one deterministic, synthetic UI through the frozen backend API."""

    simulation_mode = False
    requires_frame_sequence = True

    def __init__(self, event_limit: int = 256):
        if type(event_limit) is not int or not 64 <= event_limit <= 4096:
            raise ValueError("event_limit must be between 64 and 4096")
        self._lock = threading.RLock()
        self._events = deque(maxlen=event_limit)
        self._event_sequence = 0
        self._command_sequence = 0
        self._frame_sequence = 1
        self._page = "home"
        self._fixture_level = 42
        self._control = 0.42
        self._closed = threading.Event()
        self._payload = self._render()
        self._record("startup", "ready", {"scope": "host-fixture", "source": PREVIEW_SOURCE})
        self._record("display", "frame", {"sequence": 1, "source": PREVIEW_SOURCE,
                                          "width": _WIDTH, "height": _HEIGHT, "page": "home"})

    def _record(self, component: str, event: str,
                detail: Mapping[str, Any], correlation_id: str = "preview") -> None:
        self._event_sequence += 1
        self._events.append(EventRecord(self._event_sequence, time.time_ns(), correlation_id,
                                        component, event, dict(detail)))

    def _render(self) -> bytes:
        renderer = _render_home if self._page == "home" else _render_details
        payload = renderer(self._fixture_level, self._control)
        self._payload = payload
        return payload

    def _publish_frame(self, correlation_id: str, event: str) -> None:
        self._frame_sequence += 1
        self._render()
        self._record("display", "frame", {
            "sequence": self._frame_sequence,
            "source": PREVIEW_SOURCE,
            "width": _WIDTH,
            "height": _HEIGHT,
            "page": self._page,
            "event": event,
        }, correlation_id)

    def _command_start(self, correlation_id: Optional[str]) -> tuple[str, int, int]:
        command_id = vm_transport_identifier(correlation_id)
        with self._lock:
            self._command_sequence += 1
            return command_id, self._command_sequence, time.time_ns()

    def _finish(self, command_id: str, command_sequence: int, created: int, accepted: bool,
                state: str, message: str, detail: Mapping[str, Any]) -> CommandReceipt:
        acknowledged = time.time_ns()
        self._record("input", "completed" if accepted else "refused", {
            "command_sequence": command_sequence,
            "state": state,
            "frame_sequence": self._frame_sequence,
            **dict(detail),
        }, command_id)
        return CommandReceipt(command_id, accepted, state, message, created, acknowledged)

    def get_status(self) -> Mapping[str, Any]:
        with self._lock:
            stopped = self._closed.is_set()
            return {
                "state": "stopped" if stopped else "running",
                "service_state": "stopped" if stopped else "ready",
                "stage": "stopped" if stopped else "ready",
                "progress": 100,
                "message": "Synthetic fixture preview is ready",
                "scope": "host-fixture",
                "snapshot": False,
                "guest_network": False,
                "frame_source": PREVIEW_SOURCE,
                "frame_sequence": self._frame_sequence,
                "fixture_page": self._page,
                "fixture_level": self._fixture_level,
                "control_percent": int(self._control * 100),
                "input_connected": not stopped,
            }

    def get_frame(self) -> FrameSnapshot:
        with self._lock:
            if self._closed.is_set():
                raise LookupError("fixture preview is stopped")
            return FrameSnapshot(self._frame_sequence, time.time_ns(), _WIDTH, _HEIGHT,
                                 "image/png", self._payload, PREVIEW_SOURCE, False)

    def send_pointer(self, *, action: str, x1: int, y1: int, x2: Optional[int] = None,
                     y2: Optional[int] = None, frame_sequence: Optional[int] = None,
                     correlation_id: Optional[str] = None) -> CommandReceipt:
        vm_transport_pointer(action, x1, y1, x2, y2)
        command_id, command_sequence, created = self._command_start(correlation_id)
        with self._lock:
            detail = {"action": action, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
            if self._closed.is_set():
                return self._finish(command_id, command_sequence, created, False,
                                    "stopped", "Fixture preview has stopped", detail)
            if frame_sequence is not None and (type(frame_sequence) is not int
                                               or not 1 <= frame_sequence <= 2**53 - 1):
                return self._finish(command_id, command_sequence, created, False,
                                    "refused", "Invalid fixture frame sequence", detail)
            if frame_sequence is not None and frame_sequence != self._frame_sequence:
                return self._finish(command_id, command_sequence, created, False,
                                    "stale", "Displayed fixture frame is stale or changed", detail)
            if action == "click":
                if self._page != "home":
                    return self._finish(command_id, command_sequence, created, False,
                                        "refused", "Escape to Home before opening Details", detail)
                left, top, right, bottom = _DETAILS_BUTTON
                if not left <= x1 <= right or not top <= y1 <= bottom:
                    return self._finish(command_id, command_sequence, created, False,
                                        "refused", "Click the visible Open Details control", detail)
                self._page = "details"
                self._publish_frame(command_id, "details_opened")
                return self._finish(command_id, command_sequence, created, True,
                                    "completed", "Synthetic Details page opened", detail)
            if action in ("drag", "pdrag"):
                left, top, right, bottom = _SLIDER_DRAG_AREA
                if not left <= x1 <= right or not top <= y1 <= bottom:
                    return self._finish(command_id, command_sequence, created, False,
                                        "refused", "Start the drag on the visible fixture slider", detail)
                if self._page != "home":
                    return self._finish(command_id, command_sequence, created, False,
                                        "refused", "The fixture slider is available on Home", detail)
                track_left, _, track_width, _ = _SLIDER_TRACK
                self._control = max(0.0, min(1.0, (x2 - track_left) / (track_width - 24)))
                self._publish_frame(command_id, "control_moved")
                detail = {**detail, "control_percent": int(self._control * 100)}
                return self._finish(command_id, command_sequence, created, True,
                                    "completed", "Fixture control moved", detail)
            return self._finish(command_id, command_sequence, created, False,
                                "refused", "Unsupported fixture pointer action", detail)

    def observe_and_confirm_once(self, *, frame_sequence: int,
                                 correlation_id: Optional[str] = None) -> CommandReceipt:
        command_id, command_sequence, created = self._command_start(correlation_id)
        with self._lock:
            return self._finish(command_id, command_sequence, created, False, "unsupported",
                                "Live compositor confirmation is unavailable in fixture preview",
                                {"frame_sequence": frame_sequence})

    def send_key(self, *, action: str, key: str,
                 correlation_id: Optional[str] = None) -> CommandReceipt:
        vm_transport_key(action, key)
        command_id, command_sequence, created = self._command_start(correlation_id)
        with self._lock:
            detail = {"action": action, "key": key}
            if self._closed.is_set():
                return self._finish(command_id, command_sequence, created, False,
                                    "stopped", "Fixture preview has stopped", detail)
            if action != "tap" or key != "Escape":
                return self._finish(command_id, command_sequence, created, False,
                                    "refused", "Only Escape tap is supported by the fixture preview", detail)
            if self._page == "home":
                return self._finish(command_id, command_sequence, created, True,
                                    "completed", "Fixture is already on Home", detail)
            self._page = "home"
            self._publish_frame(command_id, "home_restored")
            return self._finish(command_id, command_sequence, created, True,
                                "completed", "Escape returned the fixture to Home", detail)

    def get_modules(self) -> list[ModuleSnapshot]:
        with self._lock:
            fields = [
                ModuleField(PREVIEW_FIELD_NAME, self._fixture_level, "integer", True,
                            "host-fixture rendering input; no guest acknowledgement",
                            list(range(100))),
                ModuleField("fixture_page", self._page, "string", False,
                            "host-fixture frame state"),
                ModuleField("control_percent", int(self._control * 100), "integer", False,
                            "host-fixture rendering input; no guest acknowledgement"),
            ]
        return [ModuleSnapshot(PREVIEW_MODULE_ID, "Synthetic fixture display", "in-process",
                               "host fixture only", fields, "Refresh fixture frame")]

    def set_module_field(self, *, module_id: str, field: str, value: Any,
                         correlation_id: Optional[str] = None) -> CommandReceipt:
        command_id, command_sequence, created = self._command_start(correlation_id)
        with self._lock:
            detail = {"module": module_id, "field": field, "value": value}
            if self._closed.is_set():
                return self._finish(command_id, command_sequence, created, False,
                                    "stopped", "Fixture preview has stopped", detail)
            if module_id != PREVIEW_MODULE_ID or field != PREVIEW_FIELD_NAME:
                return self._finish(command_id, command_sequence, created, False,
                                    "refused", "Unknown fixture module field", detail)
            if type(value) is not int or not 0 <= value <= 99:
                return self._finish(command_id, command_sequence, created, False,
                                    "refused", "fixture_level must be an integer from 0 through 99", detail)
            previous = self._fixture_level
            self._fixture_level = value
            self._publish_frame(command_id, "fixture_level_set")
            return self._finish(command_id, command_sequence, created, True, "completed",
                                "Synthetic fixture value changed",
                                {**detail, "previous": previous, "frame_sequence": self._frame_sequence})

    def observe_module(self, *, module_id: str,
                       correlation_id: Optional[str] = None) -> CommandReceipt:
        command_id, command_sequence, created = self._command_start(correlation_id)
        with self._lock:
            if module_id != PREVIEW_MODULE_ID:
                return self._finish(command_id, command_sequence, created, False,
                                    "refused", "Unknown fixture module", {"module": module_id})
            self._publish_frame(command_id, "fixture_refreshed")
            return self._finish(command_id, command_sequence, created, True, "completed",
                                "Fixture frame refreshed", {"module": module_id})

    def diagnose_module(self, *, module_id: str,
                        correlation_id: Optional[str] = None) -> CommandReceipt:
        command_id, command_sequence, created = self._command_start(correlation_id)
        with self._lock:
            return self._finish(command_id, command_sequence, created, False, "unsupported",
                                "Fixture preview does not expose a diagnostic",
                                {"module": module_id})

    def get_events(self, *, after_id: int, limit: int) -> list[EventRecord]:
        if type(after_id) is not int or after_id < 0 or type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("invalid event cursor or limit")
        with self._lock:
            return [event for event in self._events if event.event_id > after_id][:limit]

    def shutdown(self) -> CommandReceipt:
        command_id, command_sequence, created = self._command_start(None)
        with self._lock:
            if not self._closed.is_set():
                self._closed.set()
                self._record("lifecycle", "shutdown", {
                    "command_sequence": command_sequence,
                    "state": "stopped",
                }, command_id)
            return CommandReceipt(command_id, True, "completed", "Synthetic fixture preview stopped",
                                  created, time.time_ns())

    def vm_workbench_wait_runtime_stop(self, timeout: float) -> bool:
        """Wait for an authenticated shutdown before the listener is closed."""

        return self._closed.wait(timeout)

    def close(self) -> None:
        """Release this host-only backend without an owned child process."""

        with self._lock:
            self._closed.set()
