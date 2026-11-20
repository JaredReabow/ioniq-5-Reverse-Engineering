"""Host-only tests for the startup-aware browser service facade."""

from __future__ import annotations

from pathlib import Path
import sys
import threading
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/uk_fw"))

from vm_workbench.contracts import CommandReceipt, EventRecord, FrameSnapshot
from vm_workbench.service import WorkbenchServiceBackend, service_run_worker


class FakeBackend:
    simulation_mode = True

    def __init__(self):
        self.calls = []
        self.frame = FrameSnapshot(1, time.time_ns(), 1, 1, "image/png",
                                   b"\x89PNG\r\n\x1a\n", "fixture", False)

    def get_status(self): return {"state": "running", "pid": 7, "snapshot": True, "guest_network": False}
    def get_frame(self): return self.frame
    def get_modules(self): return []
    def get_events(self, *, after_id, limit):
        event = EventRecord(1, 2, "guest", "runtime", "ready", {})
        return [event] if after_id < 1 and limit else []
    def _receipt(self, name, values):
        self.calls.append((name, values))
        return CommandReceipt("id", True, "completed", name, 1, 2)
    def send_pointer(self, **values): return self._receipt("pointer", values)
    def observe_and_confirm_once(self, **values): return self._receipt("confirm", values)
    def send_key(self, **values): return self._receipt("key", values)
    def set_module_field(self, **values): return self._receipt("field", values)
    def observe_module(self, **values): return self._receipt("observe", values)
    def diagnose_module(self, **values): return self._receipt("diagnose", values)
    def shutdown(self): return self._receipt("shutdown", {})


class ServiceTests(unittest.TestCase):
    def test_progress_is_monotonic_and_bounded(self):
        service = WorkbenchServiceBackend()
        service.service_mark_progress("assets", 10, "Checking assets")
        service.service_mark_progress("prepare", 60, "Preparing workspace")
        status = service.get_status()
        self.assertEqual((status["state"], status["stage"], status["progress"]),
                         ("starting", "prepare", 60))
        with self.assertRaises(ValueError): service.service_mark_progress("bad", 59, "Backwards")
        with self.assertRaises(ValueError): service.service_mark_progress("bad\n", 61, "Bad")
        with self.assertRaises(ValueError): service.service_mark_progress("bad", 100, "Too far")

    def test_attach_proxies_existing_contract_and_offsets_events(self):
        service, backend = WorkbenchServiceBackend(), FakeBackend()
        service.service_mark_progress("prepare", 75, "Preparing")
        startup_count = len(service.get_events(after_id=0, limit=20))
        service.service_attach_backend(backend)
        self.assertTrue(service.simulation_mode)
        self.assertEqual(service.get_status()["service_state"], "ready")
        self.assertIs(service.get_frame(), backend.frame)
        receipt = service.send_key(action="tap", key="Enter", correlation_id="key-1")
        self.assertTrue(receipt.accepted)
        self.assertEqual(backend.calls[-1][0], "key")
        receipt = service.send_pointer(action="click", x1=1, y1=2, frame_sequence=7,
                                       correlation_id="pointer-1")
        self.assertTrue(receipt.accepted)
        self.assertEqual(backend.calls[-1], ("pointer", {"correlation_id": "pointer-1",
                                                         "action": "click", "x1": 1, "y1": 2,
                                                         "x2": None, "y2": None,
                                                         "frame_sequence": 7}))
        events = service.get_events(after_id=0, limit=20)
        self.assertGreater(len(events), startup_count)
        self.assertEqual([event.event_id for event in events], sorted({event.event_id for event in events}))
        self.assertGreater(events[-1].event_id, startup_count)

    def test_inputs_refuse_before_ready_and_stop_cancels(self):
        service = WorkbenchServiceBackend()
        receipt = service.send_pointer(action="click", x1=1, y1=2, correlation_id="p")
        self.assertFalse(receipt.accepted)
        self.assertEqual(receipt.state, "starting")
        stop = service.shutdown()
        self.assertFalse(stop.accepted)
        self.assertTrue(service.cancelled.is_set())
        self.assertEqual(service.get_status()["state"], "stopped")
        with self.assertRaises(RuntimeError): service.service_attach_backend(FakeBackend())

    def test_failure_is_terminal_and_sanitized(self):
        service = WorkbenchServiceBackend()
        service.service_fail("missing_assets", "Compatible local assets are missing")
        self.assertEqual(service.get_status()["error_code"], "missing_assets")
        with self.assertRaises(RuntimeError): service.service_fail("again", "Again")
        with self.assertRaises(ValueError): WorkbenchServiceBackend().service_fail("bad", "line\nbreak")

    def test_worker_attaches_or_publishes_failure(self):
        service, backend = WorkbenchServiceBackend(), FakeBackend()
        ready = threading.Event()
        thread = service_run_worker(service, lambda: backend, lambda _: ready.set())
        thread.join(2)
        self.assertFalse(thread.is_alive())
        self.assertTrue(ready.is_set())
        self.assertEqual(service.get_status()["service_state"], "ready")

        failed = WorkbenchServiceBackend()
        thread = service_run_worker(failed, lambda: (_ for _ in ()).throw(RuntimeError("failed safely")), lambda _: None)
        thread.join(2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(failed.get_status()["state"], "failed")
        self.assertEqual(failed.get_status()["error_code"], "runtimeerror")


if __name__ == "__main__":
    unittest.main()
