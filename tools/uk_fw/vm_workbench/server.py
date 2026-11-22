"""Loopback-only HTTP adapter for the Gen5W VM workbench backend.

The HTTP surface never executes shell commands or controls a device itself.
Its only operations are calls to the public ``WorkbenchBackend`` interface.
"""

from __future__ import annotations

import json
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Mapping
from urllib.parse import parse_qs, urlsplit

from .contracts import API_PREFIX, GUEST_HEIGHT, GUEST_WIDTH, WorkbenchBackend
from . import vm_workbench_version

MAX_BODY = 4096
MAX_FRAME = 16 * 1024 * 1024
MAX_EVENTS = 200
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
_KEY = re.compile(r"^(?:Key[A-Z]|Digit[0-9]|Arrow(?:Left|Right|Up|Down)|Enter|Escape|Space|Backspace|Tab)$")
_CORRELATION = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
_MIME = {"image/png", "image/jpeg", "image/webp"}
_LOCAL_HOSTS = frozenset(("127.0.0.1", "gen5w.local"))


class WorkbenchRequestError(Exception):
    """A client request cannot be accepted as a typed workbench operation."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def _object_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _exact_keys(data: Mapping[str, Any], required, optional=()):
    if not set(required).issubset(data) or set(data) - set(required) - set(optional):
        raise WorkbenchRequestError(400, "invalid_fields", "Missing or unknown fields")


def _correlation_id(data: Mapping[str, Any]):
    value = data.get("correlation_id")
    if value is not None and (not isinstance(value, str) or not _CORRELATION.fullmatch(value)):
        raise WorkbenchRequestError(400, "invalid_correlation_id", "Invalid correlation ID")
    return value


def _coordinate(value: Any, bound: int) -> int:
    if type(value) is not int or not 0 <= value < bound:
        raise WorkbenchRequestError(400, "invalid_coordinate", "Coordinate is outside the guest display")
    return value


def _check_module_value(field, value: Any) -> None:
    """Check the module's public metadata; final validation belongs to the module."""
    if not field.writable:
        raise WorkbenchRequestError(403, "read_only", "Simulator field is read-only")
    predicates = {
        "boolean": lambda v: type(v) is bool,
        "bool": lambda v: type(v) is bool,
        "integer": lambda v: type(v) is int,
        "int": lambda v: type(v) is int,
        "number": lambda v: type(v) in (int, float),
        "string": lambda v: isinstance(v, str) and len(v) <= 256,
    }
    check = predicates.get(field.value_type)
    if check is None or not check(value) or (field.choices is not None and value not in field.choices):
        raise WorkbenchRequestError(400, "invalid_value", "Value does not match the module field")


class WorkbenchHTTPServer(ThreadingHTTPServer):
    """Serve one backend on an exclusively loopback address and ephemeral token."""

    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, backend: WorkbenchBackend, port: int = 0,
                 host_name: str = "127.0.0.1"):
        if type(port) is not int or not 0 <= port <= 65535:
            raise ValueError("port must be an integer from 0 to 65535")
        if host_name not in _LOCAL_HOSTS:
            raise ValueError("host_name must be 127.0.0.1 or gen5w.local")
        self.backend = backend
        self.token = secrets.token_urlsafe(32)
        self._shutdown_reply = threading.Lock()
        super().__init__(("127.0.0.1", port), WorkbenchRequestHandler)
        self.authority = host_name if self.server_port == 80 else "%s:%d" % (host_name, self.server_port)
        self.origin = "http://" + self.authority

    def server_close(self):
        """Keep the foreground process alive until its shutdown receipt flushes.

        HTTP handlers are daemon threads. Cancellation can wake the CLI before
        the handler writes its body, so closing the listener alone is not an
        acknowledgement boundary. Only shutdown replies need this bounded wait.
        """
        acquired = self._shutdown_reply.acquire(timeout=30)
        try:
            super().server_close()
            if not acquired:
                raise TimeoutError("Shutdown response did not finish within 30 seconds")
        finally:
            if acquired:
                self._shutdown_reply.release()

    def server_shutdown_reply(self):
        """Return the lock owning shutdown operation and response publication."""
        return self._shutdown_reply


class WorkbenchRequestHandler(BaseHTTPRequestHandler):
    """Strict typed request routing with a same-origin mutation boundary."""

    server_version = "Gen5WWorkbench/0.1"
    sys_version = ""

    def setup(self):
        """Bound idle local clients so a partial request cannot hold a thread forever."""
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, format, *args):
        """Avoid leaking the local session token into server logs."""

    def _headers(self, status: int, content_type: str, length: int):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src blob:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")

    def _send_json(self, status: int, value: Any):
        payload = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode("utf-8")
        self._headers(status, "application/json; charset=utf-8", len(payload))
        self.end_headers()
        self.wfile.write(payload)

    def _assert_local(self):
        if self.client_address[0] != "127.0.0.1":
            raise WorkbenchRequestError(403, "forbidden", "Loopback clients only")
        if self.headers.get_all("Host") != [self.server.authority]:
            raise WorkbenchRequestError(403, "invalid_host", "Invalid workbench host")

    def _assert_token(self):
        values = self.headers.get_all("X-Workbench-Token") or []
        if len(values) != 1 or not secrets.compare_digest(values[0], self.server.token):
            raise WorkbenchRequestError(403, "invalid_session", "Invalid workbench session")

    def _assert_mutation(self):
        self._assert_token()
        if self.headers.get_all("Origin") != [self.server.origin]:
            raise WorkbenchRequestError(403, "invalid_origin", "A same-origin request is required")
        if self.headers.get_all("Content-Type") != ["application/json"]:
            raise WorkbenchRequestError(415, "invalid_content_type", "Expected application/json")

    def _body(self) -> Dict[str, Any]:
        if self.headers.get_all("Transfer-Encoding"):
            raise WorkbenchRequestError(400, "invalid_body", "Transfer encoding is unsupported")
        sizes = self.headers.get_all("Content-Length") or []
        if len(sizes) != 1 or not sizes[0].isascii() or not sizes[0].isdigit():
            raise WorkbenchRequestError(411, "invalid_length", "A single Content-Length is required")
        length = int(sizes[0])
        if length > MAX_BODY:
            self.close_connection = True
            raise WorkbenchRequestError(413, "body_too_large", "Request body is too large")
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise WorkbenchRequestError(400, "invalid_body", "Incomplete request body")
        try:
            body = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_without_duplicates,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid number")))
        except (ValueError, UnicodeError):
            raise WorkbenchRequestError(400, "invalid_json", "Expected a JSON object")
        if not isinstance(body, dict):
            raise WorkbenchRequestError(400, "invalid_json", "Expected a JSON object")
        return body

    def _dispatch(self):
        self._assert_local()
        parsed = urlsplit(self.path)
        if parsed.fragment or parsed.scheme or parsed.netloc:
            raise WorkbenchRequestError(400, "invalid_path", "Invalid path")
        path = parsed.path
        if self.command == "GET" and path == "/" and not parsed.query:
            source = Path(__file__).with_name("WEB_UI.html").read_text(encoding="utf-8")
            if getattr(self.server.backend, "simulation_mode", False):
                source = source.replace('<header><h1>', '<header><strong class="badge warning">SIMULATED - NO RADIO</strong><h1>', 1)
            payload = source.replace("__WORKBENCH_SESSION_TOKEN__", self.server.token).replace(
                "__WORKBENCH_VERSION__", vm_workbench_version()).replace(
                "__WORKBENCH_WIFI_SIM__", "true" if getattr(self.server.backend, "simulation_mode", False) else "false").encode("utf-8")
            self._headers(200, "text/html; charset=utf-8", len(payload))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.command == "GET":
            self._assert_token()
            if path == API_PREFIX + "/events":
                query = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
                if set(query) - {"after", "limit"} or any(len(v) != 1 for v in query.values()):
                    raise WorkbenchRequestError(400, "invalid_query", "Invalid event query")
                after, limit = query.get("after", ["0"])[0], query.get("limit", ["100"])[0]
                if not after.isascii() or not after.isdigit() or not limit.isascii() or not limit.isdigit():
                    raise WorkbenchRequestError(400, "invalid_query", "Invalid event query")
                if len(after) > 18 or len(limit) > 3 or not 1 <= int(limit) <= MAX_EVENTS:
                    raise WorkbenchRequestError(400, "invalid_query", "Event query is out of bounds")
                self._send_json(200, {"events": [e.to_dict() for e in self.server.backend.get_events(after_id=int(after), limit=int(limit))]})
                return
            if parsed.query:
                raise WorkbenchRequestError(400, "invalid_query", "Unexpected query")
            if path == API_PREFIX + "/status":
                self._send_json(200, dict(self.server.backend.get_status()))
                return
            if path == API_PREFIX + "/modules":
                self._send_json(200, {"modules": [m.to_dict() for m in self.server.backend.get_modules()]})
                return
            if path == API_PREFIX + "/frame":
                frame = self.server.backend.get_frame()
                if (frame.mime_type not in _MIME or not isinstance(frame.payload, bytes)
                        or not 0 < len(frame.payload) <= MAX_FRAME
                        or type(frame.width) is not int or not 1 <= frame.width <= 8192
                        or type(frame.height) is not int or not 1 <= frame.height <= 8192
                        or type(frame.sequence) is not int or frame.sequence < 0
                        or type(frame.captured_ns) is not int or frame.captured_ns < 0
                        or type(frame.stale) is not bool or not isinstance(frame.source, str)
                        or not _IDENTIFIER.fullmatch(frame.source)):
                    raise WorkbenchRequestError(503, "invalid_frame", "Frame is unavailable or malformed")
                self._headers(200, frame.mime_type, len(frame.payload))
                for key, value in (("Sequence", frame.sequence), ("Captured-Ns", frame.captured_ns),
                                   ("Width", frame.width), ("Height", frame.height),
                                   ("Source", frame.source), ("Stale", str(frame.stale).lower())):
                    self.send_header("X-Frame-" + key, str(value))
                self.end_headers()
                self.wfile.write(frame.payload)
                return
        elif self.command == "POST":
            self._assert_mutation()
            if parsed.query:
                raise WorkbenchRequestError(400, "invalid_query", "Unexpected query")
            data = self._body()
            if path == API_PREFIX + "/input/confirm-once":
                _exact_keys(data, ("frame_sequence",), ("correlation_id",))
                if type(data["frame_sequence"]) is not int or not 1 <= data["frame_sequence"] <= 2**53 - 1:
                    raise WorkbenchRequestError(400, "invalid_frame", "Invalid approved frame sequence")
                receipt = self.server.backend.observe_and_confirm_once(frame_sequence=data["frame_sequence"],
                                                                          correlation_id=_correlation_id(data))
            elif path == API_PREFIX + "/input/pointer":
                sim = getattr(self.server.backend, "simulation_mode", False)
                _exact_keys(data, ("action", "x1", "y1", "frame_sequence") if sim else ("action", "x1", "y1"),
                            ("x2", "y2", "correlation_id"))
                if sim and (type(data["frame_sequence"]) is not int or not 1 <= data["frame_sequence"] <= 2**53-1):
                    raise WorkbenchRequestError(400, "invalid_frame", "Simulation input requires a displayed frame")
                action = data["action"]
                if action not in ("click", "drag", "pdrag"):
                    raise WorkbenchRequestError(400, "invalid_action", "Unsupported pointer action")
                if action == "click" and ("x2" in data or "y2" in data):
                    raise WorkbenchRequestError(400, "invalid_fields", "Click takes one position")
                if action != "click" and not {"x2", "y2"}.issubset(data):
                    raise WorkbenchRequestError(400, "invalid_fields", "Drag needs two positions")
                receipt = self.server.backend.send_pointer(action=action, x1=_coordinate(data["x1"], GUEST_WIDTH),
                    y1=_coordinate(data["y1"], GUEST_HEIGHT),
                    x2=_coordinate(data["x2"], GUEST_WIDTH) if "x2" in data else None,
                    y2=_coordinate(data["y2"], GUEST_HEIGHT) if "y2" in data else None,
                    correlation_id=_correlation_id(data), **({"frame_sequence": data["frame_sequence"]} if sim else {}))
            elif path == API_PREFIX + "/input/key":
                _exact_keys(data, ("action", "key"), ("correlation_id",))
                if data["action"] not in ("press", "release", "tap") or not isinstance(data["key"], str) or not _KEY.fullmatch(data["key"]):
                    raise WorkbenchRequestError(400, "invalid_key", "Unsupported key or action")
                receipt = self.server.backend.send_key(action=data["action"], key=data["key"], correlation_id=_correlation_id(data))
            elif path == API_PREFIX + "/shutdown":
                _exact_keys(data, ())
                with self.server.server_shutdown_reply():
                    receipt = self.server.backend.shutdown()
                    self._send_json(200, receipt.to_dict())
                    self.wfile.flush()
                return
            else:
                parts = path.split("/")
                if len(parts) != 6 or parts[:4] != ["", "api", "v1", "modules"]:
                    raise WorkbenchRequestError(404, "not_found", "Unknown endpoint")
                module_id, field_name = parts[4:]
                if not _IDENTIFIER.fullmatch(module_id) or not _IDENTIFIER.fullmatch(field_name):
                    raise WorkbenchRequestError(400, "invalid_field", "Invalid module or field name")
                if field_name in ("observe", "diagnose"):
                    _exact_keys(data, (), ("correlation_id",))
                    modules = [m for m in self.server.backend.get_modules() if m.module_id == module_id]
                    if len(modules) != 1:
                        raise WorkbenchRequestError(404, "not_found", "Unknown simulator module")
                    if not (modules[0].observe_label if field_name == "observe" else modules[0].diagnose_label):
                        raise WorkbenchRequestError(403, "unsupported", "Module does not support observation")
                    method = (self.server.backend.observe_module if field_name == "observe"
                              else self.server.backend.diagnose_module)
                    receipt = method(module_id=module_id, correlation_id=_correlation_id(data))
                else:
                    _exact_keys(data, ("value",), ("correlation_id",))
                    matches = [f for m in self.server.backend.get_modules() if m.module_id == module_id
                               for f in m.fields if f.name == field_name]
                    if len(matches) != 1:
                        raise WorkbenchRequestError(404, "not_found", "Unknown simulator field")
                    _check_module_value(matches[0], data["value"])
                    receipt = self.server.backend.set_module_field(module_id=module_id, field=field_name,
                        value=data["value"], correlation_id=_correlation_id(data))
            self._send_json(200, receipt.to_dict())
            return
        raise WorkbenchRequestError(404, "not_found", "Unknown endpoint")

    def _handle(self):
        try:
            self._dispatch()
        except WorkbenchRequestError as exc:
            self._send_json(exc.status, {"error": {"code": exc.code, "message": exc.message}})
        except (ValueError, TypeError):
            self._send_json(400, {"error": {"code": "invalid_request", "message": "Request rejected"}})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            self._send_json(503, {"error": {"code": "backend_unavailable", "message": "Workbench backend unavailable"}})

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle
    do_PATCH = _handle
    do_DELETE = _handle
    do_OPTIONS = _handle
