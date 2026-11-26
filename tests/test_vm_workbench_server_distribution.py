"""Distribution-facing loopback service checks without launching QEMU."""

from __future__ import annotations

import http.client
import io
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/uk_fw"))

from vm_workbench.server import WorkbenchHTTPServer
from vm_workbench.service import WorkbenchServiceBackend
from vm_workbench.contracts import CommandReceipt
from vm_workbench import cli
from vm_workbench.guest_shell import vm_guest_parse_standby_readiness
from vm_workbench.preview import PreviewBackend


class DistributionServerTests(unittest.TestCase):
    def test_shutdown_body_flushes_before_foreground_service_process_exits(self):
        # Delay the body after sending Content-Length, recreating the Linux
        # race where the CLI exits while its daemon handler still owns a reply.
        code = '''
import json, time
from vm_workbench import cli
from vm_workbench.server import WorkbenchRequestHandler
original = WorkbenchRequestHandler._send_json
def delayed(self, status, value):
    if isinstance(value, dict) and value.get("command_id") == "shutdown":
        payload = json.dumps(value).encode("utf-8")
        self._headers(status, "application/json", len(payload))
        self.end_headers()
        time.sleep(.75)
        self.wfile.write(payload)
    else:
        original(self, status, value)
WorkbenchRequestHandler._send_json = delayed
def prepare(progress):
    raise FileNotFoundError("Missing compatible bzImage fixture")
raise SystemExit(0 if cli.vm_workbench_run_server(prepare, port=0) else 1)
'''
        env = {**os.environ, "PYTHONPATH": str(ROOT / "tools/uk_fw")}
        process = subprocess.Popen((sys.executable, "-u", "-c", code), cwd=ROOT, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            line = process.stdout.readline().strip()
            self.assertTrue(line.startswith("Gen5W browser service listening at http://127.0.0.1:"), line)
            port = int(line.rsplit(":", 1)[1])
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            connection.request("GET", "/")
            response = connection.getresponse()
            page = response.read().decode("utf-8")
            marker = "const token = '"
            # The page owns the same ephemeral token exposed to browser JS.
            token = page.split(marker, 1)[1].split("'", 1)[0]
            connection.close()
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            connection.request("POST", "/api/v1/shutdown", body=b"{}", headers={
                "Origin": f"http://127.0.0.1:{port}", "Content-Type": "application/json",
                "X-Workbench-Token": token,
            })
            response = connection.getresponse()
            payload = response.read()
            self.assertEqual(len(payload), int(response.getheader("Content-Length")))
            self.assertTrue(json.loads(payload)["accepted"])
            connection.close()
            self.assertEqual(process.wait(timeout=5), 1)
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()

    def setUp(self):
        self.backend = WorkbenchServiceBackend(simulation_mode=True)
        self.server = WorkbenchHTTPServer(self.backend, 0, "gen5w.local")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(3)

    def request(self, path, host=None, token=True):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Host": host or self.server.authority}
        if token: headers["X-Workbench-Token"] = self.server.token
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_page_is_available_during_startup_with_progress_ui(self):
        status, _, page = self.request("/", token=False)
        self.assertEqual(status, 200)
        for marker in (b'id="startupProgress"', b'id="startupMessage"',
                       b'let vmReady = false;', b'SIMULATED - NO RADIO'):
            self.assertIn(marker, page)
        status, _, payload = self.request("/api/v1/status")
        self.assertEqual(status, 200)
        data = json.loads(payload)
        self.assertEqual((data["state"], data["progress"], data["snapshot"], data["guest_network"]),
                         ("starting", 0, True, False))

    def test_progress_is_visible_and_wrong_host_is_rejected(self):
        self.backend.service_mark_progress("assets", 25, "Checking compatible assets")
        data = json.loads(self.request("/api/v1/status")[2])
        self.assertEqual((data["stage"], data["progress"]), ("assets", 25))
        self.assertEqual(self.request("/", host="evil.invalid", token=False)[0], 403)
        self.assertEqual(self.request("/", host="127.0.0.1:%d" % self.server.server_port, token=False)[0], 403)

    def test_simulation_frame_sequence_crosses_http_and_service_facade(self):
        guarded = mock.Mock(simulation_mode=True)
        guarded.send_pointer.return_value = CommandReceipt("p", True, "completed", "fixture", 1, 2)
        self.backend.service_attach_backend(guarded)
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        body = json.dumps({"action": "click", "x1": 120, "y1": 435,
                           "frame_sequence": 7}).encode()
        connection.request("POST", "/api/v1/input/pointer", body=body, headers={
            "Host": self.server.authority, "Origin": self.server.origin,
            "X-Workbench-Token": self.server.token, "Content-Type": "application/json",
        })
        response = connection.getresponse()
        payload = response.read()
        connection.close()
        self.assertEqual((response.status, json.loads(payload)["accepted"]), (200, True))
        guarded.send_pointer.assert_called_once_with(action="click", x1=120, y1=435,
                                                      x2=None, y2=None, correlation_id=None,
                                                      frame_sequence=7)


class DistributionCLITests(unittest.TestCase):
    def test_preview_backend_rejects_superseded_frame_when_sequence_is_bound(self):
        backend = PreviewBackend()
        original = backend.get_frame()
        opened = backend.send_pointer(
            action="click", x1=1410, y1=380, frame_sequence=original.sequence,
            correlation_id="bound-open",
        )
        stale = backend.send_pointer(
            action="click", x1=1410, y1=380, frame_sequence=original.sequence,
            correlation_id="bound-stale",
        )
        self.assertTrue(backend.requires_frame_sequence)
        self.assertFalse(backend.simulation_mode)
        self.assertEqual((opened.accepted, opened.state), (True, "completed"))
        self.assertEqual(backend.get_status()["fixture_page"], "details")
        self.assertEqual((stale.accepted, stale.state), (False, "stale"))
        self.assertEqual(stale.command_id, "bound-stale")

    def test_asset_free_preview_process_serves_guarded_interactive_fixture(self):
        env = {**os.environ, "PYTHONPATH": str(ROOT / "tools/uk_fw")}
        process = subprocess.Popen(
            (sys.executable, "-u", "-B", "-m", "vm_workbench", "--preview", "--port", "0"),
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        port = None
        try:
            lines = [process.stdout.readline().strip() for _ in range(3)]
            listener = next((line for line in lines
                             if line.startswith("Gen5W browser service listening at http://127.0.0.1:")),
                            None)
            self.assertIsNotNone(listener, lines)
            port = int(listener.rsplit(":", 1)[1])
            authority = f"127.0.0.1:{port}"
            origin = f"http://{authority}"

            def request(method, path, *, token=None, host=None, request_origin=None, body=None):
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
                headers = {"Host": host or authority}
                if token is not None:
                    headers["X-Workbench-Token"] = token
                if method == "POST":
                    headers.update({"Content-Type": "application/json",
                                    "Origin": request_origin or origin})
                connection.request(method, path, body=body, headers=headers)
                response = connection.getresponse()
                payload = response.read()
                result = response.status, dict(response.getheaders()), payload
                connection.close()
                return result

            status, _, page = request("GET", "/")
            self.assertEqual(status, 200)
            marker = b"const token = '"
            token = page.split(marker, 1)[1].split(b"'", 1)[0].decode("ascii")
            self.assertIn(b"const wifiSimulation = false;", page)
            self.assertNotIn(b"SIMULATED - NO RADIO", page)
            self.assertEqual(request("GET", "/", host="evil.invalid")[0], 403)
            self.assertEqual(request("GET", "/api/v1/status")[0], 403)
            refused_origin = request(
                "POST", "/api/v1/input/key", token=token, request_origin="http://evil.invalid",
                body=b'{"action":"tap","key":"Escape"}',
            )
            self.assertEqual(refused_origin[0], 403)

            status, _, payload = request("GET", "/api/v1/status", token=token)
            self.assertEqual(status, 200)
            data = json.loads(payload)
            self.assertEqual(
                (data["scope"], data["service_state"], data["snapshot"], data["guest_network"]),
                ("host-fixture", "ready", False, False),
            )

            status, headers, home = request("GET", "/api/v1/frame", token=token)
            self.assertEqual(status, 200)
            self.assertEqual((headers["X-Frame-Source"], headers["X-Frame-Width"],
                              headers["X-Frame-Height"]),
                             ("fixture", "1920", "720"))
            self.assertEqual(struct.unpack(">II", home[16:24]), (1920, 720))
            self.assertIn(b"Gen5W synthetic host fixture", home)
            self.assertGreater(int(headers["X-Frame-Sequence"]), 0)
            home_sequence = int(headers["X-Frame-Sequence"])

            status, _, payload = request(
                "POST", "/api/v1/input/pointer", token=token,
                body=json.dumps({
                    "action": "click", "x1": 1410, "y1": 380,
                    "frame_sequence": home_sequence,
                    "correlation_id": "click-details",
                }).encode(),
            )
            receipt = json.loads(payload)
            self.assertEqual((status, receipt["accepted"], receipt["command_id"]),
                             (200, True, "click-details"))

            status, _, details = request("GET", "/api/v1/frame", token=token)
            self.assertEqual(status, 200)
            self.assertNotEqual(home, details)
            self.assertEqual(json.loads(request("GET", "/api/v1/status", token=token)[2])["fixture_page"],
                             "details")

            status, _, payload = request(
                "POST", "/api/v1/input/key", token=token,
                body=b'{"action":"tap","key":"Escape","correlation_id":"escape-home"}',
            )
            escape = json.loads(payload)
            self.assertEqual((status, escape["accepted"], escape["command_id"]),
                             (200, True, "escape-home"))

            _, home_again_headers, home_again = request("GET", "/api/v1/frame", token=token)
            home_again_sequence = int(home_again_headers["X-Frame-Sequence"])
            status, _, payload = request(
                "POST", "/api/v1/input/pointer", token=token,
                body=json.dumps({
                    "action": "drag", "x1": 850, "y1": 545, "x2": 1180, "y2": 545,
                    "frame_sequence": home_again_sequence,
                    "correlation_id": "drag-control",
                }).encode(),
            )
            drag = json.loads(payload)
            self.assertEqual((status, drag["accepted"]), (200, True))
            _, _, dragged = request("GET", "/api/v1/frame", token=token)
            self.assertNotEqual(home_again, dragged)
            self.assertGreater(json.loads(request("GET", "/api/v1/status", token=token)[2])
                               ["control_percent"], 42)

            status, _, payload = request(
                "POST", "/api/v1/modules/fixture/fixture_level", token=token,
                body=b'{"value":77,"correlation_id":"fixture-level"}',
            )
            field_receipt = json.loads(payload)
            self.assertEqual((status, field_receipt["accepted"], field_receipt["command_id"]),
                             (200, True, "fixture-level"))
            changed_status = json.loads(request("GET", "/api/v1/status", token=token)[2])
            self.assertEqual(changed_status["fixture_level"], 77)
            _, _, updated = request("GET", "/api/v1/frame", token=token)
            self.assertNotEqual(dragged, updated)

            status, _, payload = request("GET", "/api/v1/events?after=0&limit=100", token=token)
            self.assertEqual(status, 200)
            events = json.loads(payload)["events"]
            by_correlation = {}
            for event in events:
                by_correlation.setdefault(event["correlation_id"], []).append(event)
            command_events = [
                (correlation, next(event for event in by_correlation[correlation]
                                   if event["event"] in ("completed", "refused")))
                for correlation in ("click-details", "escape-home", "drag-control",
                                    "fixture-level")
            ]
            self.assertEqual([event["detail"]["command_sequence"] for _, event in command_events],
                             [1, 2, 3, 4])
            self.assertEqual(by_correlation["fixture-level"][-1]["detail"]["frame_sequence"],
                             changed_status["frame_sequence"])

            status, headers, payload = request(
                "POST", "/api/v1/shutdown", token=token, body=b"{}",
            )
            self.assertEqual(status, 200)
            self.assertEqual(len(payload), int(headers["Content-Length"]))
            self.assertTrue(json.loads(payload)["accepted"])
            self.assertEqual(process.wait(timeout=5), 0)
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=.5)
            with self.assertRaises(OSError):
                connection.request("GET", "/")
            connection.close()
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            stdout, stderr = process.stdout.read(), process.stderr.read()
            process.stdout.close()
            process.stderr.close()
        self.assertEqual(stderr, "")
        self.assertTrue(any("preview ready" in line for line in lines),
                        lines + [stdout])

    def test_standby_receipt_reaches_browser_without_admitting_controls(self):
        captured, result = {}, []
        listening = threading.Event()
        token = "a" * 32
        message = "Gen5W HMI startup failed (standby_exited)."

        def capture_server(backend, port, host):
            server = WorkbenchHTTPServer(backend, port, host)
            captured["server"] = server
            listening.set()
            return server

        def start(_workspace, *, qemu, wifi_simulation, progress):
            progress("hmi", 78, "Gen5W HMI is launching")
            vm_guest_parse_standby_readiness(
                f"opaque_private_data\nWB_STANDBY_{token} FAIL standby_exited\n".encode("ascii"), token)

        def request(server, method, path, body=None):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            try:
                connection.request(method, path, body=body, headers={
                    "Host": server.authority, "Origin": server.origin,
                    "X-Workbench-Token": server.token, "Content-Type": "application/json",
                })
                response = connection.getresponse()
                return response.status, response.read()
            finally:
                connection.close()

        with (mock.patch.object(cli, "WorkbenchHTTPServer", side_effect=capture_server),
              mock.patch.object(cli, "vm_workbench_create_backend", side_effect=start),
              mock.patch.object(WorkbenchServiceBackend, "service_attach_backend", autospec=True) as attach):
            thread = threading.Thread(target=lambda: result.append(cli.vm_workbench_run_server(
                lambda _progress: (Path("/workspace"), None, Path("/qemu")), port=0)))
            thread.start()
            try:
                self.assertTrue(listening.wait(2))
                server = captured["server"]
                deadline = time.monotonic() + 3
                while True:
                    status, payload = request(server, "GET", "/api/v1/status")
                    self.assertEqual(status, 200)
                    data = json.loads(payload)
                    if data["service_state"] == "failed" or time.monotonic() >= deadline:
                        break
                    time.sleep(.01)
                self.assertEqual((data["service_state"], data["progress"], data["error_code"], data["message"]),
                                 ("failed", 78, "gueststandbyerror", message))
                self.assertNotIn(b"opaque_private_data", payload)
                status, events = request(server, "GET", "/api/v1/events?after=0&limit=100")
                self.assertEqual(status, 200)
                self.assertNotIn(b"opaque_private_data", events)
                self.assertIn(message.encode("ascii"), events)
                self.assertEqual(request(server, "GET", "/api/v1/frame")[0], 503)
                status, refused = request(server, "POST", "/api/v1/input/pointer",
                                          b'{"action":"click","x1":0,"y1":0}')
                self.assertEqual((status, json.loads(refused)["accepted"]), (200, False))
                attach.assert_not_called()
                self.assertTrue(thread.is_alive())
            finally:
                if "server" in captured:
                    captured["server"].backend.shutdown()
                thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(result, [False])

    def test_main_wires_public_server_arguments_without_legacy_paths(self):
        assets = Path("/tmp/public-gen5w-assets")
        with (mock.patch.object(cli, "vm_workbench_prepare_public") as prepare,
              mock.patch.object(cli, "vm_workbench_run_server", return_value=True) as run):
            result = cli.main(("--server", "--assets", str(assets), "--port", "8765",
                               "--host-name", "gen5w.local", "--open-browser", "--wifi-sim"))
        self.assertEqual(result, 0)
        self.assertFalse(prepare.called)
        call = run.call_args
        self.assertEqual(call.kwargs, {"port": 8765, "host_name": "gen5w.local",
                                      "open_browser": True, "simulation_mode": True})
        progress = mock.Mock()
        with mock.patch.object(cli, "vm_workbench_prepare_public",
                               return_value=(Path("/runtime/session"), "sim", Path("/qemu"))) as prepare:
            self.assertEqual(call.args[0](progress),
                             (Path("/runtime/session"), "sim", Path("/qemu")))
        prepare.assert_called_once_with(assets, wifi_sim=True, progress=progress)

    def test_server_keeps_failure_visible_until_browser_stop_and_returns_failure(self):
        class FakeServer:
            origin = "http://127.0.0.1:8765"

            def __init__(self, backend, port, host):
                captured["backend"] = backend
                self.stopped = threading.Event()

            def serve_forever(self, **_):
                self.stopped.wait(3)

            def shutdown(self):
                self.stopped.set()

            def server_close(self):
                pass

        for failure, code, message in ((ValueError("incompatible fixture"), "valueerror",
                                        "incompatible fixture"),
                                       (EOFError(), "eoferror", "VM startup failed")):
            with self.subTest(code=code):
                captured = {}

                def prepare(progress):
                    progress("assets", 12, "Checking fixtures")
                    raise failure

                result = []
                with mock.patch.object(cli, "WorkbenchHTTPServer", FakeServer):
                    thread = threading.Thread(target=lambda: result.append(cli.vm_workbench_run_server(prepare)))
                    thread.start()
                    deadline = time.monotonic() + 2
                    while "backend" not in captured and time.monotonic() < deadline:
                        time.sleep(.01)
                    backend = captured["backend"]
                    while backend.get_status()["service_state"] != "failed" and time.monotonic() < deadline:
                        time.sleep(.01)
                    self.assertEqual(backend.get_status()["error_code"], code)
                    self.assertEqual(backend.get_status()["message"], message)
                    self.assertTrue(thread.is_alive())
                    backend.shutdown()
                    thread.join(3)
                self.assertFalse(thread.is_alive())
                self.assertEqual(result, [False])

    def test_public_prepare_removes_only_its_partial_session_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, runtime, assets = root / "state", root / "state/runtime", root / "assets"
            assets.mkdir()
            config = SimpleNamespace(state_dir=state, runtime_dir=runtime, qemu=Path("/qemu"))
            admitted = SimpleNamespace()

            def copy(_admitted, output, destination, **_):
                self.assertEqual(output, runtime)
                destination.mkdir(mode=0o700)
                (destination / "partial").write_text("owned")
                return destination

            with (mock.patch("vm_workbench.platform_config.platform_config_discover", return_value=config),
                  mock.patch("vm_workbench.platform_config.platform_config_require"),
                  mock.patch("vm_workbench.assets.assets_admit", return_value=admitted),
                  mock.patch("vm_workbench.assets.assets_copy_workspace", side_effect=copy),
                  mock.patch.object(cli, "vm_workbench_prepare_portable",
                                    side_effect=RuntimeError("build failed"))):
                with self.assertRaisesRegex(RuntimeError, "build failed"):
                    cli.vm_workbench_prepare_public(assets, wifi_sim=False,
                                                    progress=lambda *_: None)
            self.assertEqual(list(runtime.iterdir()), [])
            self.assertTrue(assets.is_dir())

    def test_public_prepare_reports_copy_then_verification_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, runtime, asset_dir = root / "state", root / "state/runtime", root / "assets"
            asset_dir.mkdir()
            config = SimpleNamespace(state_dir=state, runtime_dir=runtime, qemu=Path("/qemu"))
            admitted = SimpleNamespace()
            events = []

            def copy(_admitted, _output, destination, **callbacks):
                destination.mkdir(mode=0o700)
                callbacks["copy_progress"]("bzImage", 0, 1024)
                callbacks["copy_progress"]("bzImage", 1024, 1024)
                callbacks["progress"]("bzImage", 0, 1024)
                callbacks["progress"]("bzImage", 1024, 1024)
                return destination

            with (mock.patch("vm_workbench.platform_config.platform_config_discover", return_value=config),
                  mock.patch("vm_workbench.platform_config.platform_config_require"),
                  mock.patch("vm_workbench.assets.assets_admit", return_value=admitted),
                  mock.patch("vm_workbench.assets.assets_copy_workspace", side_effect=copy),
                  mock.patch.object(cli, "vm_workbench_prepare_portable")):
                result, simulation, qemu = cli.vm_workbench_prepare_public(
                    asset_dir, wifi_sim=False,
                    progress=lambda stage, percent, message: events.append(
                        (stage, percent, message)))

            self.assertEqual(result.parent, runtime)
            self.assertIsNone(simulation)
            self.assertEqual(qemu, Path("/qemu"))
            workspace = [event for event in events if event[0] == "workspace"]
            self.assertTrue(any(message.startswith("Copying: bzImage")
                                for _, _, message in workspace))
            self.assertTrue(any(message.startswith("Verifying: bzImage")
                                for _, _, message in workspace))
            self.assertEqual([percent for _, percent, _ in workspace],
                             sorted(percent for _, percent, _ in workspace))

    def test_public_prepare_never_removes_a_preexisting_session_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, runtime, asset_dir = root / "state", root / "state/runtime", root / "assets"
            runtime.mkdir(parents=True, mode=0o700); asset_dir.mkdir()
            collision = runtime / "session-123"
            collision.mkdir(mode=0o700)
            sentinel = collision / "owned-by-another-session"
            sentinel.write_text("preserve me", encoding="utf-8")
            config = SimpleNamespace(state_dir=state, runtime_dir=runtime, qemu=Path("/qemu"))

            with (mock.patch("vm_workbench.platform_config.platform_config_discover", return_value=config),
                  mock.patch("vm_workbench.platform_config.platform_config_require"),
                  mock.patch("vm_workbench.assets.assets_admit", return_value=SimpleNamespace()),
                  mock.patch("vm_workbench.assets.assets_copy_workspace",
                             side_effect=ValueError("workspace already exists")),
                  mock.patch.object(cli.time, "time_ns", return_value=123),
                  self.assertRaisesRegex(ValueError, "already exists")):
                cli.vm_workbench_prepare_public(asset_dir, wifi_sim=False,
                                                progress=lambda *_: None)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve me")

    def test_unexpected_admitted_runtime_stop_stays_visible_and_returns_failure(self):
        captured, result = {}, []

        class Server:
            origin = "http://127.0.0.1:8765"

            def __init__(self, backend, _port, _host):
                captured["service"] = backend
                self.stopped = threading.Event()

            def serve_forever(self, **_): self.stopped.wait(3)
            def shutdown(self): self.stopped.set()
            def server_close(self): pass

        class Managed:
            simulation_mode = False

            def __init__(self):
                self.unexpected = threading.Event()
                self.server = None

            def __getattr__(self, _name):
                return lambda **_kwargs: CommandReceipt("fixture", False, "stopped", "fixture", 1, 2)

            def get_status(self): return {"state": "stopped"}
            def start_capture(self, server, *, defer_unexpected_shutdown=False):
                if not defer_unexpected_shutdown:
                    raise AssertionError("public server must defer unexpected listener shutdown")
                self.server = server
                self.unexpected.set()
            def vm_workbench_wait_runtime_stop(self, timeout): return self.unexpected.wait(timeout)
            def vm_workbench_runtime_stopped_unexpectedly(self): return self.unexpected.is_set()
            def shutdown(self):
                self.server.shutdown()
                return CommandReceipt("shutdown", True, "completed", "stopped", 1, 2)
            def close(self): pass

        with (mock.patch.object(cli, "WorkbenchHTTPServer", Server),
              mock.patch.object(cli, "vm_workbench_create_backend", return_value=Managed())):
            thread = threading.Thread(target=lambda: result.append(cli.vm_workbench_run_server(
                lambda _progress: (Path("/workspace"), None, Path("/qemu")))))
            thread.start()
            deadline = time.monotonic() + 2
            while ("service" not in captured or
                   captured["service"].get_status()["service_state"] != "failed") and time.monotonic() < deadline:
                time.sleep(.01)
            status = captured["service"].get_status()
            self.assertEqual((status["service_state"], status["error_code"]),
                             ("failed", "runtime_stopped"))
            self.assertTrue(thread.is_alive())
            captured["service"].shutdown()
            thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(result, [False])

    def test_unattended_failure_cleans_up_after_bounded_visibility_window(self):
        captured, result = {}, []

        class Server:
            origin = "http://127.0.0.1:8765"

            def __init__(self, backend, _port, _host):
                captured["service"] = backend
                self.stopped = threading.Event()

            def serve_forever(self, **_): self.stopped.wait(3)
            def shutdown(self): self.stopped.set()
            def server_close(self): pass

        class Managed:
            simulation_mode = False

            def __init__(self):
                self.unexpected = threading.Event()

            def __getattr__(self, _name):
                return lambda **_kwargs: CommandReceipt("fixture", False, "stopped", "fixture", 1, 2)

            def get_status(self): return {"state": "stopped"}
            def start_capture(self, server, *, defer_unexpected_shutdown=False):
                if not defer_unexpected_shutdown:
                    raise AssertionError("public server must defer unexpected listener shutdown")
                self.unexpected.set()
            def vm_workbench_wait_runtime_stop(self, timeout): return self.unexpected.wait(timeout)
            def vm_workbench_runtime_stopped_unexpectedly(self): return True
            def shutdown(self): return CommandReceipt("fixture", True, "completed", "stopped", 1, 2)
            def close(self): pass

        with (mock.patch.object(cli, "FAILURE_VISIBILITY_SECONDS", .05),
              mock.patch.object(cli, "WorkbenchHTTPServer", Server),
              mock.patch.object(cli, "vm_workbench_create_backend", return_value=Managed())):
            started = time.monotonic()
            thread = threading.Thread(target=lambda: result.append(cli.vm_workbench_run_server(
                lambda _progress: (Path("/workspace"), None, Path("/qemu")))))
            thread.start()
            thread.join(2)
            elapsed = time.monotonic() - started

        self.assertFalse(thread.is_alive())
        self.assertLess(elapsed, 2)
        self.assertEqual(result, [False])
        self.assertEqual(captured["service"].get_status()["error_code"], "runtime_stopped")
        self.assertTrue(captured["service"].cancelled.is_set())

    def test_browser_stop_after_admission_returns_success(self):
        self._assert_stop_after_admission_returns_success()

    def _assert_stop_after_admission_returns_success(self, *, open_browser=False):
        captured, result = {}, []

        class Server:
            origin = "http://127.0.0.1:8765"

            def __init__(self, backend, _port, _host):
                captured["service"] = backend
                self.stopped = threading.Event()

            def serve_forever(self, **_): self.stopped.wait(3)
            def shutdown(self): self.stopped.set()
            def server_close(self): pass

        class Managed:
            simulation_mode = False

            def __init__(self):
                self.unexpected = threading.Event()
                self.server = None

            def __getattr__(self, _name):
                return lambda **_kwargs: CommandReceipt("fixture", True, "completed", "fixture", 1, 2)

            def get_status(self): return {"state": "running"}
            def start_capture(self, server, *, defer_unexpected_shutdown=False):
                if not defer_unexpected_shutdown:
                    raise AssertionError("public server must defer unexpected listener shutdown")
                self.server = server
            def vm_workbench_wait_runtime_stop(self, timeout): return self.unexpected.wait(timeout)
            def vm_workbench_runtime_stopped_unexpectedly(self): return False
            def shutdown(self):
                self.server.shutdown()
                return CommandReceipt("shutdown", True, "completed", "stopped", 1, 2)
            def close(self): pass

        with (mock.patch.object(cli, "WorkbenchHTTPServer", Server),
              mock.patch.object(cli, "vm_workbench_create_backend", return_value=Managed())):
            thread = threading.Thread(target=lambda: result.append(cli.vm_workbench_run_server(
                lambda _progress: (Path("/workspace"), None, Path("/qemu")),
                open_browser=open_browser)))
            thread.start()
            deadline = time.monotonic() + 2
            while ("service" not in captured or
                   captured["service"].get_status()["service_state"] != "ready") and time.monotonic() < deadline:
                time.sleep(.01)
            status = captured["service"].get_status()
            captured["service"].shutdown()
            thread.join(3)
            self.assertEqual(status["service_state"], "ready")
        self.assertFalse(thread.is_alive())
        self.assertEqual(result, [True])

    def test_failed_browser_shutdown_returns_failing_launcher_status(self):
        captured, result = {}, []

        class Server:
            origin = "http://127.0.0.1:8765"
            def __init__(self, backend, _port, _host):
                captured["service"] = backend
                self.stopped = threading.Event()
            def serve_forever(self, **_): self.stopped.wait(3)
            def shutdown(self): self.stopped.set()
            def server_close(self): pass

        class Managed:
            simulation_mode = False
            def __getattr__(self, _name): return lambda **_kwargs: None
            def get_status(self): return {"state": "running"}
            def start_capture(self, server, **_): self.server = server
            def vm_workbench_wait_runtime_stop(self, timeout):
                time.sleep(min(timeout, .01))
                return False
            def vm_workbench_runtime_stopped_unexpectedly(self): return False
            def shutdown(self):
                self.server.shutdown()
                return CommandReceipt("shutdown", False, "error", "Fixture process remains alive", 1, 2)
            def close(self): pass

        with (mock.patch.object(cli, "WorkbenchHTTPServer", Server),
              mock.patch.object(cli, "vm_workbench_create_backend", return_value=Managed())):
            thread = threading.Thread(target=lambda: result.append(cli.vm_workbench_run_server(
                lambda _progress: (Path("/workspace"), None, Path("/qemu")))))
            thread.start()
            deadline = time.monotonic() + 2
            while ("service" not in captured or
                   captured["service"].get_status()["service_state"] != "ready") and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertFalse(captured["service"].shutdown().accepted)
            thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(result, [False])

    def test_legacy_managed_capture_closes_listener_on_runtime_loss(self):
        stopped = threading.Event()

        class Runtime:
            def get_status(self): return {"state": "stopped"}
            def shutdown(self): pass

        class Shell:
            def close(self): pass

        class Server:
            def shutdown(self): stopped.set()

        managed = cli._ManagedWorkbenchBackend(SimpleNamespace(simulation_mode=False),
                                               Runtime(), Shell())
        managed.start_capture(Server())
        self.assertTrue(stopped.wait(1))
        self.assertFalse(managed.vm_workbench_runtime_stopped_unexpectedly())
        managed.close()

    def test_portable_helper_build_updates_pins_with_discovered_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime, workspace = root / "runtime", root / "runtime/session"
            runtime.mkdir(mode=0o700)
            workspace.mkdir(mode=0o700)
            (workspace / "rootfs.img").write_bytes(b"root")
            (workspace / "libdbus-1.so.3").write_bytes(b"dbus")
            (workspace / "prepare.json").write_text(json.dumps({"schema": 1, "sha256": {
                "bzImage": "a", "rootfs.img": "b", "manifest.bin": "c",
                "seed_dev.bin": "d", "seed_user.bin": "e"}}))
            config = SimpleNamespace(runtime_dir=runtime, python=Path(sys.executable),
                                     zig=Path("/tools/zig"), debugfs=Path("/tools/debugfs"),
                                     shell=Path("/bin/sh"), file_tool=Path("/usr/bin/file"),
                                     dbus_inc=Path("/include/dbus-1.0"),
                                     dbus_arch_inc=Path("/lib/dbus-1.0/include"))
            commands = []

            def run(argv, **kwargs):
                commands.append((tuple(map(str, argv)), kwargs))
                if str(argv[0]) == "/bin/sh":
                    Path(kwargs["env"]["OUT"]).write_bytes(b"helper")
                    return subprocess.CompletedProcess(argv, 0)
                if "-R" in argv:
                    return subprocess.CompletedProcess(argv, 0, stdout="Type: regular Mode: 0755")
                return subprocess.CompletedProcess(argv, 0, stdout="debugfs")

            with (mock.patch("vm_workbench.platform_config.platform_config_require"),
                  mock.patch.object(cli.subprocess, "run", side_effect=run)):
                result = cli.vm_workbench_prepare_portable(workspace, config)
            self.assertEqual(result, workspace.resolve())
            metadata = json.loads((workspace / "prepare.json").read_text())
            self.assertEqual(metadata["sha256"]["rootfs.img"], cli.vm_workbench_hash(workspace / "rootfs.img"))
            self.assertEqual(metadata["workbench_frame_probe"]["rootfs_sha256"],
                             metadata["sha256"]["rootfs.img"])
            builds = [entry for entry in commands if entry[0][0] == "/bin/sh"]
            self.assertEqual(len(builds), 3)
            for _, kwargs in builds:
                self.assertEqual(kwargs["env"]["GUEST_LIBDBUS"],
                                 str(workspace.resolve() / "libdbus-1.so.3"))
                self.assertNotIn(str(cli.RESEARCH), kwargs["env"]["PATH"])

    def test_public_wifi_preparation_propagates_discovered_image_tool(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, runtime, asset_dir = root / "state", root / "state/runtime", root / "assets"
            asset_dir.mkdir()
            magick = root / "ImageMagick/bin/magick"
            config = SimpleNamespace(state_dir=state, runtime_dir=runtime, qemu=Path("/qemu"),
                                     magick=magick, musl_cc=Path("/musl-gcc"))

            def copy(_admitted, _output, destination, **_):
                destination.mkdir(mode=0o700)
                (destination / "wifi-sim").mkdir()
                (destination / "build").mkdir()
                return destination

            with (mock.patch("vm_workbench.platform_config.platform_config_discover", return_value=config),
                  mock.patch("vm_workbench.platform_config.platform_config_require"),
                  mock.patch("vm_workbench.assets.assets_admit", return_value=SimpleNamespace()),
                  mock.patch("vm_workbench.assets.assets_copy_workspace", side_effect=copy),
                  mock.patch.object(cli, "vm_workbench_prepare_portable", side_effect=lambda path, *_a, **_k: path),
                  mock.patch("vm_workbench.wifi_sim.session.wifi_sim_load_assets", return_value={"fixture": True}),
                  mock.patch("vm_workbench.wifi_sim.integration.wifi_sim_build_target"),
                  mock.patch("vm_workbench.wifi_sim.integration.wifi_sim_checked_bytes", return_value=b"target")):
                _, prepared, _ = cli.vm_workbench_prepare_public(asset_dir, wifi_sim=True,
                                                                 progress=lambda *_: None)
            self.assertEqual(prepared, ({"fixture": True}, b"target", magick))

    def test_legacy_server_stop_receipt_shuts_listener(self):
        events = []

        class Managed:
            def start_capture(self, server):
                self.server = server
                events.append("capture")

            def shutdown(self):
                events.append("backend-shutdown")
                self.server.shutdown()
                return CommandReceipt("stop", True, "completed", "stopped", 1, 2)

            def close(self):
                events.append("closed")

        class Server:
            origin = "http://127.0.0.1:1"

            def __init__(self, backend, port):
                self.backend = backend

            def serve_forever(self, **_):
                events.append("serve")
                self.backend.shutdown()

            def shutdown(self):
                events.append("listener-shutdown")

            def server_close(self):
                events.append("listener-closed")

        managed = Managed()
        with (mock.patch.object(cli, "vm_workbench_create_backend", return_value=managed),
              mock.patch.object(cli, "WorkbenchHTTPServer", Server)):
            cli.vm_workbench_run(Path("/fixture"))
        self.assertEqual(events, ["capture", "serve", "backend-shutdown", "listener-shutdown",
                                  "listener-closed", "closed"])

    def test_verified_windows_browser_handoff_uses_argument_list(self):
        with tempfile.TemporaryDirectory() as directory:
            browser = Path(directory) / "Windows/explorer.exe"
            browser.parent.mkdir()
            browser.write_bytes(b"fixture")
            browser.chmod(0o755)
            with (mock.patch.dict(os.environ, {"GEN5W_WINDOWS_BROWSER": str(browser)}),
                  mock.patch.object(cli.subprocess, "Popen") as launch,
                  mock.patch.object(cli.webbrowser, "open") as generic):
                self.assertTrue(cli.vm_workbench_open_browser("http://gen5w.local:8765"))
            launch.assert_called_once_with([str(browser), "http://gen5w.local:8765"],
                                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL, close_fds=True)
            generic.assert_not_called()

    def test_windows_browser_handoff_failure_warns_and_allows_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            windows = Path(directory) / "Windows"
            windows.mkdir()
            invalid = windows / "notepad.exe"
            invalid.touch(mode=0o755)
            explorer = windows / "explorer.exe"
            for executable, expected_error in (
                (invalid, "not a verified Windows explorer.exe path"),
                (explorer, "not a verified Windows explorer.exe path"),
                (explorer, "fixture Windows launch failed"),
            ):
                with self.subTest(executable=executable.name, error=expected_error):
                    should_launch = expected_error == "fixture Windows launch failed"
                    if should_launch:
                        explorer.touch(mode=0o755)
                    stderr = io.StringIO()
                    with (mock.patch.dict(os.environ, {"GEN5W_WINDOWS_BROWSER": str(executable)}),
                          mock.patch.object(cli.subprocess, "Popen", side_effect=OSError(expected_error)) as launch,
                          mock.patch.object(cli.webbrowser, "open") as generic,
                          mock.patch.object(sys, "stderr", stderr)):
                        self._assert_stop_after_admission_returns_success(open_browser=True)
                    self.assertEqual(launch.call_count, int(should_launch))
                    generic.assert_not_called()
                    self.assertIn(expected_error, stderr.getvalue())
                    self.assertIn("Open http://127.0.0.1:8765", stderr.getvalue())


class DistributionSourceTests(unittest.TestCase):
    def test_standalone_source_allowlist_is_complete_and_private_data_free(self):
        manifest = ROOT / "docs/gen5w-vm-server-files.txt"
        paths = tuple(line for line in manifest.read_text(encoding="utf-8").splitlines()
                      if line and not line.startswith("#"))
        self.assertEqual(paths, tuple(sorted(set(paths))))
        self.assertIn("docs/gen5w-vm-server-files.txt", paths)
        self.assertIn("tools/uk_fw/vm_boot.py", paths)
        self.assertIn("tools/uk_fw/guest/launch-vm-workbench.sh", paths)
        self.assertIn("launchers/Gen5W-Preview.cmd", paths)
        self.assertIn("launchers/Gen5W-Preview.command", paths)
        self.assertIn("launchers/Gen5W-Preview.desktop", paths)
        self.assertNotIn("tools/uk_fw/guest/eng-data-sim", paths)
        # Construct the sentinels so this audit module can audit itself without
        # embedding the private strings it rejects from the package.
        forbidden = (b"/Users/" + b"leo", b"/Volumes/" + b"PARTITION 2",
                     b"ioniq" + b" research", b"-----BEGIN " + b"PRIVATE KEY-----")
        for relative in paths:
            with self.subTest(path=relative):
                path = ROOT / relative
                self.assertTrue(path.is_file() and not path.is_symlink())
                data = path.read_bytes()
                for marker in forbidden:
                    self.assertNotIn(marker, data)

    def test_windows_checkout_keeps_hash_pinned_and_posix_sources_lf(self):
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        for rule in ("launchers/*.sh text eol=lf",
                     "launchers/*.command text eol=lf",
                     "tools/uk_fw/vm_workbench/wifi_sim/*.patch text eol=lf",
                     "tools/uk_fw/guest/build-weston-ivi-frame-probe.sh text eol=lf",
                     "tools/uk_fw/guest/weston_ivi_frame_probe.c text eol=lf"):
            self.assertIn(rule, attributes)


if __name__ == "__main__":
    unittest.main()
