"""Exercise the workbench HTTP boundary using only a deterministic fake backend."""

import http.client
import json
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "uk_fw"))
from vm_workbench.contracts import CommandReceipt, EventRecord, FrameSnapshot, ModuleField, ModuleSnapshot
from vm_workbench.server import MAX_BODY, WorkbenchHTTPServer


class FakeBackend:
    """A host-only fixture; no methods talk to QEMU or a physical device."""

    def __init__(self):
        self.calls = []
        self.frame = FrameSnapshot(3, 1_700_000_000_000_000_000, 1920, 720, "image/png", b"fixture-png", "host-fixture", False)

    def get_status(self):
        return {"state": "fixture"}

    def get_frame(self):
        return self.frame

    def get_modules(self):
        return [ModuleSnapshot("micom", "MICOM", "fixture", "host-fixture", [
            ModuleField("acc", False, "boolean", True, "inferred"),
            ModuleField("parking_status", None, "boolean", True, "simulator receipt"),
            ModuleField("firmware", "fixture", "string", False, "fixture"),
            ModuleField("mode", "park", "string", True, "recovered", ["park", "drive"]),
        ], "Observe guest D-Bus"), ModuleSnapshot("hmi", "HMI", "fixture", "host-fixture", [], "Observe Confirm state", "Diagnose Confirm observation"),
                ModuleSnapshot("plain", "Plain", "fixture", "host-fixture", [])]

    def get_events(self, *, after_id, limit):
        self.calls.append(("events", after_id, limit))
        return [EventRecord(2, 123, "op-1", "fixture", "ack", {"ok": True})]

    def _receipt(self, name, values):
        self.calls.append((name, values))
        return CommandReceipt("op-1", True, "queued", "Fixture accepted", 123)

    def send_pointer(self, **kwargs):
        return self._receipt("pointer", kwargs)

    def observe_and_confirm_once(self, **kwargs):
        return self._receipt("confirm", kwargs)

    def send_key(self, **kwargs):
        return self._receipt("key", kwargs)

    def set_module_field(self, **kwargs):
        return self._receipt("module", kwargs)

    def observe_module(self, *, module_id, correlation_id=None):
        return self._receipt("observe", {"module_id": module_id, "correlation_id": correlation_id})

    def diagnose_module(self, *, module_id, correlation_id=None):
        return self._receipt("diagnose", {"module_id": module_id, "correlation_id": correlation_id})

    def shutdown(self):
        return self._receipt("shutdown", {})


class WorkbenchHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = FakeBackend()
        cls.server = WorkbenchHTTPServer(cls.backend)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(3)

    def setUp(self):
        self.backend.calls.clear()

    def request(self, method, path, body=None, token=True, origin=True, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        request_headers = dict(headers or {})
        if token:
            request_headers.setdefault("X-Workbench-Token", self.server.token)
        if method == "POST":
            request_headers.setdefault("Content-Type", "application/json")
            if origin:
                request_headers.setdefault("Origin", self.server.origin)
            if isinstance(body, (dict, list)):
                body = json.dumps(body).encode()
        connection.request(method, path, body=body, headers=request_headers)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_loopback_page_token_and_fixture_frame(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")
        status, headers, page = self.request("GET", "/", token=False)
        self.assertEqual(status, 200)
        self.assertIn(self.server.token.encode(), page)
        self.assertNotIn(b"__WORKBENCH_SESSION_TOKEN__", page)
        self.assertIn(b"Gen5W VM Workbench 0.3.2", page)
        self.assertEqual(headers["Cache-Control"], "no-store")
        status, headers, frame = self.request("GET", "/api/v1/frame")
        self.assertEqual((status, frame), (200, b"fixture-png"))
        self.assertEqual(headers["X-Frame-Source"], "host-fixture")
        self.assertEqual(headers["X-Frame-Width"], "1920")
        self.assertEqual(headers["X-Frame-Stale"], "false")

    def test_simulation_requires_displayed_frame_for_pointer(self):
        self.backend.simulation_mode = True
        try:
            status, _, page = self.request('GET', '/', token=False)
            self.assertEqual(status, 200)
            self.assertIn(b'SIMULATED - NO RADIO', page)
            self.assertIn(b'const wifiSimulation = true;', page)
            self.assertIn(b'simulationInputPending = true;', page)
            self.assertIn(b'if (wifiSimulation && simulationInputPending)', page)
            self.assertIn(b'pending.finally(() => { simulationInputPending = false; });', page)
            path = '/api/v1/input/pointer'
            self.assertEqual(self.request('POST', path, {'action':'click','x1':120,'y1':435})[0],400)
            self.assertEqual(self.request('POST', path, {'action':'click','x1':120,'y1':435,'frame_sequence':True})[0],400)
            self.assertEqual(self.request('POST', path, {'action':'click','x1':120,'y1':435,'frame_sequence':3})[0],200)
            self.assertEqual(self.backend.calls[-1][1]['frame_sequence'],3)
        finally:
            del self.backend.simulation_mode

    def test_authentication_origin_and_host_are_required(self):
        self.assertEqual(self.request("GET", "/api/v1/status", token=False)[0], 403)
        self.assertEqual(self.request("POST", "/api/v1/shutdown", {}, token=False)[0], 403)
        self.assertEqual(self.request("POST", "/api/v1/shutdown", {}, origin=False)[0], 403)
        self.assertEqual(self.request("POST", "/api/v1/shutdown", {}, headers={"Origin": "http://evil.invalid"})[0], 403)
        self.assertEqual(self.request("GET", "/", headers={"Host": "evil.invalid"})[0], 403)
        self.assertEqual(self.backend.calls, [])

    def test_configured_gen5w_authority_is_exact_and_stays_loopback(self):
        server = WorkbenchHTTPServer(FakeBackend(), 0, "gen5w.local")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            self.assertEqual(server.server_address[0], "127.0.0.1")
            self.assertEqual(server.authority, "gen5w.local:%d" % server.server_port)
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            connection.request("GET", "/", headers={"Host": server.authority})
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            response.read(); connection.close()

            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            connection.request("GET", "/", headers={"Host": "127.0.0.1:%d" % server.server_port})
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read(); connection.close()
        finally:
            server.shutdown(); server.server_close(); thread.join(3)
        with self.assertRaises(ValueError): WorkbenchHTTPServer(FakeBackend(), 0, "localhost")

    def test_pointer_key_and_module_are_strict_and_typed(self):
        path = "/api/v1/input/pointer"
        self.assertEqual(self.request("POST", path, {"action": "click", "x1": 1919, "y1": 719})[0], 200)
        self.assertEqual(self.backend.calls[-1][1]["x1"], 1919)
        for body in (
            {"action": "click", "x1": 1920, "y1": 0},
            {"action": "click", "x1": True, "y1": 0},
            {"action": "click", "x1": 0, "y1": 0, "extra": 1},
            {"action": "drag", "x1": 0, "y1": 0},
            {"action": "shell", "x1": 0, "y1": 0},
        ):
            self.assertEqual(self.request("POST", path, body)[0], 400, body)
        self.assertEqual(self.request("POST", "/api/v1/input/key", {"action": "tap", "key": "KeyA"})[0], 200)
        self.assertEqual(self.request("POST", "/api/v1/input/key", {"action": "tap", "key": "Shell"})[0], 400)
        for key in ("Home", "End", "PageUp", "PageDown", "Delete", "F1", "F12"):
            self.assertEqual(self.request("POST", "/api/v1/input/key", {"action": "tap", "key": key})[0], 400, key)
        self.assertEqual(self.request("POST", "/api/v1/modules/micom/acc", {"value": True})[0], 200)
        self.assertEqual(self.request("POST", "/api/v1/modules/micom/acc", {"value": 1})[0], 400)
        self.assertEqual(self.request("POST", "/api/v1/modules/micom/parking_status", {"value": True})[0], 200)
        self.assertEqual(self.request("POST", "/api/v1/modules/micom/parking_status", {"value": 1})[0], 400)
        self.assertEqual(self.request("POST", "/api/v1/modules/micom/firmware", {"value": "x"})[0], 403)
        self.assertEqual(self.request("POST", "/api/v1/modules/micom/mode", {"value": "unknown"})[0], 400)
        self.assertEqual(self.request("POST", "/api/v1/modules/micom/missing", {"value": 1})[0], 404)

    def test_confirm_once_accepts_only_approved_sequence(self):
        path = "/api/v1/input/confirm-once"
        for body in ({}, {"frame_sequence": True}, {"frame_sequence": 0},
                     {"frame_sequence": 1, "x1": 4}, {"frame_sequence": "1"},
                     {"frame_sequence": 1, "command": "click"}):
            self.assertEqual(self.request("POST", path, body)[0], 400)
        self.assertEqual(self.request("POST", path, {"frame_sequence": 3}, origin=False)[0], 403)
        self.assertEqual(self.backend.calls, [])
        self.assertEqual(self.request("POST", path, {"frame_sequence": 3, "correlation_id": "one"})[0], 200)
        self.assertEqual(self.backend.calls, [("confirm", {"frame_sequence": 3, "correlation_id": "one"})])

    def test_json_query_and_frame_fail_closed(self):
        path = "/api/v1/input/key"
        self.assertEqual(self.request("POST", path, b'{"key":"KeyA","key":"KeyB","action":"tap"}')[0], 400)
        self.assertEqual(self.request("POST", path, b"x" * (MAX_BODY + 1))[0], 413)
        self.assertEqual(self.request("POST", path, [], headers={"Content-Type": "text/plain"})[0], 415)
        self.assertEqual(self.request("GET", "/api/v1/events?after=0&limit=201")[0], 400)
        self.assertEqual(self.request("GET", "/api/v1/events?after=0&after=1")[0], 400)
        status, _, unsupported = self.request("DELETE", "/api/v1/modules/micom/acc")
        self.assertEqual(status, 404)
        self.assertEqual(json.loads(unsupported)["error"]["code"], "not_found")
        status, _, payload = self.request("GET", "/api/v1/events?after=1&limit=5")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)["events"][0]["correlation_id"], "op-1")
        original = self.backend.frame
        try:
            self.backend.frame = FrameSnapshot(1, 1, 10, 10, "text/html", b"<script>", "fixture", False)
            self.assertEqual(self.request("GET", "/api/v1/frame")[0], 503)
        finally:
            self.backend.frame = original

    def test_guest_observation_requires_session_origin_and_exact_route(self):
        path = "/api/v1/modules/micom/observe"
        self.assertEqual(self.request("POST", path, {}, token=False)[0], 403)
        self.assertEqual(self.request("POST", path, {}, origin=False)[0], 403)
        self.assertEqual(self.request("POST", path, {}, headers={"Origin": "http://evil.invalid"})[0], 403)
        self.assertEqual(self.request("POST", path, {"command": "anything"})[0], 400)
        self.assertEqual(self.request("POST", path, {"correlation_id": "bad space"})[0], 400)
        self.assertEqual(self.request("POST", "/api/v1/modules/unknown/observe", {})[0], 404)
        self.assertEqual(self.request("POST", "/api/v1/modules/plain/observe", {})[0], 403)
        self.assertEqual(self.request("POST", path + "/extra", {})[0], 404)
        self.assertEqual(self.request("POST", path + "?x=1", {})[0], 400)
        self.assertEqual(self.backend.calls, [])
        status, _, body = self.request("POST", path, {"correlation_id": "obs-1"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["command_id"], "op-1")
        self.assertEqual(self.backend.calls, [("observe", {"module_id": "micom", "correlation_id": "obs-1"})])
        self.assertEqual(self.request("POST", "/api/v1/modules/hmi/observe", {})[0], 200)
        self.assertEqual(self.backend.calls[-1], ("observe", {"module_id": "hmi", "correlation_id": None}))
        self.assertEqual(self.request("POST", "/api/v1/modules/hmi/diagnose", {}, token=False)[0], 403)
        self.assertEqual(self.request("POST", "/api/v1/modules/hmi/diagnose", {"command": "x"})[0], 400)
        self.assertEqual(self.request("POST", "/api/v1/modules/micom/diagnose", {})[0], 403)
        self.assertEqual(self.request("POST", "/api/v1/modules/hmi/diagnose", {"correlation_id": "diag"})[0], 200)
        self.assertEqual(self.backend.calls[-1], ("diagnose", {"module_id": "hmi", "correlation_id": "diag"}))


if __name__ == "__main__":
    unittest.main()
