"""Owned-process tests for the VM workbench, without starting QEMU."""

import json
import os
import subprocess
from contextlib import contextmanager
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/uk_fw"))
from vm_workbench.runtime import WorkbenchRuntime
from vm_workbench.contracts import CommandReceipt
from vm_workbench.guest_shell import GuestShell


class FakeProcess:
    pid = 12345
    returncode = None
    stdin = None

    def poll(self):
        return self.returncode

    def terminate(self):
        self.returncode = 0

    def wait(self, timeout):
        return self.returncode

    def kill(self):
        self.returncode = -9


class RuntimeTests(unittest.TestCase):
    def test_shutdown_timeout_after_kill_returns_failure_and_keeps_process_owned(self):
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu)
        process = mock.Mock()
        process.poll.return_value = None
        process.wait.side_effect = subprocess.TimeoutExpired("fixture-owned-process", 5)
        runtime._process = process
        receipt = runtime.shutdown()
        self.assertFalse(receipt.accepted)
        self.assertEqual(receipt.state, "error")
        self.assertIs(runtime._process, process)
        self.assertEqual(runtime.get_status()["state"], "running")
        self.assertEqual(process.wait.call_count, 2)
        process.terminate.assert_called_once()
        process.kill.assert_called_once()
        process.stdin.close.assert_called_once()
        self.assertEqual(runtime.get_events(after_id=0, limit=10)[-1].event, "stop_failed")

    def test_shutdown_reaps_after_kill_and_reports_completed(self):
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu)
        process = mock.Mock()
        process.poll.side_effect = [None, -9]
        process.wait.side_effect = [subprocess.TimeoutExpired("fixture-owned-process", 5), -9]
        process.returncode = -9
        runtime._process = process
        receipt = runtime.shutdown()
        self.assertTrue(receipt.accepted)
        self.assertEqual(receipt.state, "completed")
        self.assertEqual(runtime.get_events(after_id=0, limit=10)[-1].event, "stopped")
        process.stdin.close.assert_called_once()

    def test_diagnostic_publication_precedes_release_under_preemption(self):
        """A paused older release cannot publish after a later diagnostic."""
        for first_kind in ("completed", "error", "timeout", "stale"):
            with self.subTest(first=first_kind):
                released, resume = threading.Event(), threading.Event()
                class PausingLock:
                    def __init__(self):
                        self.lock = threading.Lock()
                    def acquire(self, blocking=True):
                        return self.lock.acquire(blocking=blocking)
                    def release(self):
                        self.lock.release()
                        if threading.current_thread().name == "older-diagnostic":
                            released.set()
                            if not resume.wait(3):
                                raise TimeoutError("fixture timed out")
                runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                           hmi_observer=lambda: {})
                runtime._process = FakeProcess()
                runtime._diagnostic_lock = PausingLock()
                calls, receipts = [], {}
                def diagnose():
                    calls.append(len(calls) + 1)
                    if calls[-1] == 1:
                        if first_kind == "stale":
                            runtime._hmi_observer = lambda: {}
                        if first_kind in ("error", "timeout"):
                            return {"status": "error", "failed_stage": "fixture", "reason": first_kind}
                    return {"status": "completed", "sequence": calls[-1]}
                runtime._hmi_diagnoser = diagnose
                def run_first():
                    receipts["older"] = runtime.diagnose_module(module_id="hmi", correlation_id="older")
                older = threading.Thread(target=run_first, name="older-diagnostic")
                older.start()
                try:
                    self.assertTrue(released.wait(1), "first diagnostic did not release")
                    # The first publication must already be visible at release.
                    events = runtime.get_events(after_id=0, limit=20)
                    terminal = [e for e in events if e.correlation_id == "older" and e.event != "diagnostic_requested"]
                    self.assertEqual(len(terminal), 1)
                    reader = threading.Thread(target=lambda: (runtime.get_status(), runtime.get_modules()))
                    reader.start(); reader.join(1); self.assertFalse(reader.is_alive())
                    receipts["newer"] = runtime.diagnose_module(module_id="hmi", correlation_id="newer")
                    self.assertTrue(receipts["newer"].accepted)
                finally:
                    resume.set(); older.join(3)
                self.assertFalse(older.is_alive())
                fields = {f.name: f.value for f in runtime.get_modules()[1].fields}
                self.assertEqual(fields["last_diagnostic"]["sequence"], 2)
                events = runtime.get_events(after_id=0, limit=20)
                terminals = [(e.correlation_id, e.event) for e in events if e.event != "diagnostic_requested"]
                self.assertEqual(terminals, [("older", "diagnostic_completed" if first_kind == "completed" else "diagnostic_error"),
                                             ("newer", "diagnostic_completed")])
                self.assertEqual(receipts["older"].state,
                                 "completed" if first_kind == "completed" else "disconnected" if first_kind == "stale" else "error")

    def test_diagnostic_success_failure_stale_and_responsive_reads(self):
        entered, release = threading.Event(), threading.Event()
        success = {"status": "completed", "stages": {}, "new_record": True}
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                   hmi_observer=lambda: {}, hmi_diagnoser=lambda: success)
        runtime._process = FakeProcess()
        fields = lambda: {f.name: f.value for f in runtime.get_modules()[1].fields}
        self.assertTrue(runtime.diagnose_module(module_id="hmi").accepted)
        self.assertEqual(fields()["last_diagnostic"], success)
        runtime._hmi_diagnoser = lambda: {"status": "error", "failed_stage": "before", "reason": "timeout"}
        self.assertEqual(runtime.diagnose_module(module_id="hmi", correlation_id="fail").state, "error")
        self.assertEqual(fields()["last_diagnostic"], success)
        self.assertEqual(runtime.get_events(after_id=0, limit=10)[-1].detail["diagnostic"]["failed_stage"], "before")
        def slow():
            entered.set(); release.wait(3); return success
        for change in ("observer", "diagnoser", "simulator", "process", "shutdown"):
            entered.clear(); release.clear()
            runtime._process, runtime._sim_shutdown, runtime._hmi_diagnoser = FakeProcess(), False, slow
            results = []
            worker = threading.Thread(target=lambda: results.append(runtime.diagnose_module(module_id="hmi")))
            worker.start()
            try:
                self.assertTrue(entered.wait(1))
                reader = threading.Thread(target=lambda: (runtime.get_status(), runtime.get_modules()))
                reader.start(); reader.join(1); self.assertFalse(reader.is_alive())
                self.assertEqual(runtime.diagnose_module(module_id="hmi").state, "busy")
                if change == "observer": runtime._hmi_observer = lambda: {}
                elif change == "diagnoser": runtime._hmi_diagnoser = lambda: success
                elif change == "simulator": runtime._simulator = object()
                elif change == "process": runtime._process = FakeProcess()
                else: runtime.shutdown()
            finally:
                release.set(); worker.join(3)
            self.assertFalse(worker.is_alive())
            self.assertEqual(results[0].state, "disconnected")
            self.assertEqual(fields()["last_diagnostic"], success)

    def test_hmi_observation_preserves_value_on_failure_and_stale_completion(self):
        sample = {"buttonRoot": [479, 629, 690, 63], "enabled": True, "modelEnableBtn": 1,
                  "visible": True, "wide": True, "dimmed": False, "driving": False, "calling": False}
        entered, release = threading.Event(), threading.Event()
        def slow():
            entered.set()
            if not release.wait(3):
                raise TimeoutError("fixture timed out")
            return {**sample, "enabled": False}
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu, hmi_observer=lambda: sample)
        runtime._process = FakeProcess()
        fields = lambda: {f.name: f.value for f in runtime.get_modules()[1].fields}
        self.assertIsNone(fields()["buttonRoot"])
        self.assertTrue(runtime.observe_module(module_id="hmi", correlation_id="hmi-ok").accepted)
        self.assertEqual(fields()["buttonRoot"], [479, 629, 690, 63])
        event = runtime.get_events(after_id=0, limit=10)[-1]
        self.assertEqual((event.correlation_id, event.detail["state"]["enabled"]), ("hmi-ok", True))
        runtime._hmi_observer = lambda: (_ for _ in ()).throw(ValueError("failure"))
        self.assertEqual(runtime.observe_module(module_id="hmi").state, "error")
        self.assertEqual(fields()["enabled"], True)
        bridge = GuestShell.__new__(GuestShell)
        with mock.patch.object(bridge, "_run", side_effect=RuntimeError("guest operation failed with status 1")):
            runtime._hmi_observer = bridge.observe_confirm_geometry
            self.assertEqual(runtime.observe_module(module_id="hmi").state, "error")
            self.assertEqual(fields()["enabled"], True)
        for mutation in ("observer", "shutdown"):
            entered.clear(); release.clear()
            runtime._process, runtime._sim_shutdown, runtime._hmi_observer = FakeProcess(), False, slow
            results = []
            worker = threading.Thread(target=lambda: results.append(runtime.observe_module(module_id="hmi")))
            worker.start()
            try:
                self.assertTrue(entered.wait(1))
                reader = threading.Thread(target=lambda: (runtime.get_status(), runtime.get_modules()))
                reader.start(); reader.join(1)
                self.assertFalse(reader.is_alive())
                if mutation == "shutdown":
                    runtime.shutdown()
                else:
                    runtime._hmi_observer = lambda: sample
            finally:
                release.set(); worker.join(3)
            self.assertFalse(worker.is_alive())
            self.assertEqual(results[0].state, "disconnected")
            self.assertEqual(fields()["enabled"], True)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.workspace = self.directory / "workspace"
        self.workspace.mkdir()
        self.qemu = self.directory / "qemu"
        self.qemu.write_bytes(b"fake")
        self.qemu.chmod(0o755)

    def test_missing_prerequisites_name_paths(self):
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu)
        with self.assertRaises(FileNotFoundError) as caught:
            runtime.start(compatibility=False)
        self.assertIn(str(self.workspace / "rootfs.img"), str(caught.exception))
        self.assertFalse((self.directory / "run").exists())

    def test_start_enforces_existing_snapshot_command_and_stops_owned_process(self):
        for name in ("prepare.json", "bzImage", "rootfs.img", "manifest.bin", "seed_dev.bin", "seed_user.bin"):
            (self.workspace / name).write_bytes(b"fixture")
        base = (self.workspace / "rootfs.img").read_bytes()
        process = FakeProcess()
        calls = []
        def factory(argv, **kwargs):
            calls.append((argv, kwargs))
            return process
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu, process_factory=factory)
        cpu_profile = "max,vendor=GenuineIntel,-avx2"
        with mock.patch("vm_workbench.runtime.platform_config_qemu_cpu_profile",
                        return_value=cpu_profile) as select_cpu, \
             mock.patch("importlib.util.module_from_spec") as loader:
            boot = loader.return_value
            boot.qemu_command.return_value = [str(self.qemu), "-nic", "none", "-drive", "file=fixture,snapshot=on"]
            with mock.patch("importlib.util.spec_from_file_location") as spec:
                runtime.start(compatibility=False)
                boot.verify_workspace.assert_called_once_with(self.workspace.resolve())
                select_cpu.assert_called_once_with()
                boot.qemu_command.assert_called_once_with(
                    self.workspace.resolve(), str(self.qemu.resolve()), False,
                    display="none", qmp=True, memory_mib=1536, cpu=cpu_profile)
                self.assertEqual(runtime.get_status()["state"], "running")
                self.assertEqual(runtime.get_status()["cpu_profile"], cpu_profile)
                started = runtime.get_events(after_id=0, limit=10)[0]
                self.assertEqual(started.detail["cpu_profile"], cpu_profile)
                self.assertTrue(runtime.shutdown().accepted)
                self.assertEqual(runtime.get_status()["state"], "stopped")
                self.assertEqual((self.workspace / "rootfs.img").read_bytes(), base)
                self.assertEqual(len(calls), 1)
                self.assertEqual((self.directory / "run").stat().st_mode & 0o777, 0o700)
                spec.return_value.loader.exec_module.assert_called_once()

    def test_run_directory_privacy_failure_precedes_process_creation(self):
        for name in ("prepare.json", "bzImage", "rootfs.img", "manifest.bin", "seed_dev.bin", "seed_user.bin"):
            (self.workspace / name).write_bytes(b"fixture")
        factory = mock.Mock()
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu, process_factory=factory)
        with mock.patch("importlib.util.module_from_spec") as loader, \
             mock.patch("importlib.util.spec_from_file_location"), \
             mock.patch("vm_workbench.runtime.os.fchmod", side_effect=PermissionError("fixture")):
            loader.return_value.qemu_command.return_value = [str(self.qemu), "-nic", "none", "-drive", "file=fixture,snapshot=on"]
            with self.assertRaises(PermissionError):
                runtime.start(compatibility=False)
        factory.assert_not_called()
        self.assertEqual(runtime.get_status()["state"], "not_started")

    def test_compatibility_requires_setup_before_start(self):
        for name in ("prepare.json", "bzImage", "rootfs.img", "manifest.bin", "seed_dev.bin", "seed_user.bin"):
            (self.workspace / name).write_bytes(b"fixture")
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu)
        with self.assertRaisesRegex(ValueError, "compatibility setup"):
            runtime.start()
        self.assertFalse((self.directory / "run").exists())

    def test_disconnected_input_and_module_are_explicit(self):
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu)
        self.assertEqual(runtime.send_pointer(action="click", x1=1, y1=2).state, "disconnected")
        self.assertEqual(runtime.set_module_field(module_id="micom", field="debug_count", value=1).state, "disconnected")
        with self.assertRaises(ValueError):
            runtime.set_module_field(module_id="micom", field="unknown", value=1)
        self.assertEqual(runtime.get_modules()[0].integration, "disconnected")

    def test_module_writable_only_while_owned_process_is_live(self):
        simulator = object()
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                   simulator=simulator)
        module = runtime.get_modules()[0]
        self.assertEqual(module.integration, "disconnected")
        self.assertFalse(module.fields[0].writable)
        process = FakeProcess()
        runtime._process = process
        module = runtime.get_modules()[0]
        self.assertEqual(module.integration, "guest-integrated simulator")
        self.assertTrue(module.fields[0].writable)
        process.returncode = 0
        module = runtime.get_modules()[0]
        self.assertEqual(module.integration, "disconnected")
        self.assertFalse(module.fields[0].writable)

    def test_parking_status_api_distinguishes_unknown_and_acknowledged(self):
        class Simulator:
            def request(self, value, correlation_id, *, field):
                self.call = (value, field)
                return CommandReceipt(correlation_id, True, "completed", "ack", 1, 2), value
        sim = Simulator()
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu, simulator=sim)
        runtime._process = FakeProcess()
        fields = {f.name: f for f in runtime.get_modules()[0].fields}
        self.assertIsNone(fields["parking_status"].value)
        self.assertTrue(runtime.set_module_field(module_id="micom", field="parking_status", value=True).accepted)
        self.assertEqual(sim.call, (1, "parking_status"))
        fields = {f.name: f for f in runtime.get_modules()[0].fields}
        self.assertIs(fields["parking_status"].value, True)
        self.assertIs(fields["parking_status_configured"].value, True)
        for value in (0, 1, "true", None):
            with self.assertRaises(ValueError):
                runtime.set_module_field(module_id="micom", field="parking_status", value=value)

    def test_observation_distinguishes_requested_acknowledged_and_observed(self):
        class Simulator:
            def request(self, value, correlation_id):
                return CommandReceipt(correlation_id, True, "completed", "ack", 1, 2), value
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                   simulator=Simulator(), observer=lambda: 9)
        runtime._process = FakeProcess()
        receipt = runtime.set_module_field(module_id="micom", field="debug_count", value=9, correlation_id="set9")
        self.assertTrue(receipt.accepted)
        fields = {f.name: f for f in runtime.get_modules()[0].fields}
        self.assertEqual((fields["debug_count_configured"].value, fields["debug_count"].value,
                          fields["debug_count_dbus_observed"].value), (9, 9, None))
        result = runtime.observe_module(module_id="micom", correlation_id="observe9")
        self.assertTrue(result.accepted)
        self.assertEqual(result.command_id, "observe9")
        fields = {f.name: f for f in runtime.get_modules()[0].fields}
        self.assertEqual(fields["debug_count_dbus_observed"].value, 9)
        self.assertEqual(fields["debug_count"].evidence, "guest-mailbox-acknowledged; recovered-consumer-byte0")
        self.assertEqual(fields["debug_count_configured"].evidence, "operator-requested; not guest acknowledgement")
        self.assertEqual(fields["debug_count_dbus_observed"].evidence, "guest-system-bus AskDebuggingMode reply byte0; VM-only observation")
        self.assertFalse(fields["debug_count_dbus_observed"].writable)
        events = runtime.get_events(after_id=0, limit=10)
        self.assertEqual([(e.correlation_id, e.event) for e in events],
                         [("observe9", "observation_requested"), ("observe9", "completed")])

    def test_observation_mismatch_errors_and_disconnect_are_explicit(self):
        class Simulator:
            def request(self, value, correlation_id):
                return CommandReceipt(correlation_id, True, "completed", "ack", 1, 2), value
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                   simulator=Simulator(), observer=lambda: 7)
        runtime._process = FakeProcess()
        runtime.set_module_field(module_id="micom", field="debug_count", value=9, correlation_id="set")
        result = runtime.observe_module(module_id="micom", correlation_id="different")
        self.assertEqual((result.accepted, result.state), (False, "mismatch"))
        fields = {f.name: f.value for f in runtime.get_modules()[0].fields}
        self.assertEqual((fields["debug_count"], fields["debug_count_dbus_observed"]), (9, 7))
        self.assertTrue(runtime.get_events(after_id=0, limit=10)[-1].detail["mismatch"])
        runtime._observer = lambda: (_ for _ in ()).throw(ValueError("bad reply"))
        self.assertEqual(runtime.observe_module(module_id="micom", correlation_id="bad").state, "error")
        fields = {f.name: f.value for f in runtime.get_modules()[0].fields}
        self.assertEqual(fields["debug_count_dbus_observed"], 7)
        with self.assertRaises(ValueError):
            runtime.observe_module(module_id="unknown")
        runtime._process.returncode = 0
        self.assertEqual(runtime.observe_module(module_id="micom").state, "disconnected")
        self.assertEqual(runtime.set_module_field(module_id="micom", field="debug_count", value=4).state, "disconnected")
        fields = {f.name: f.value for f in runtime.get_modules()[0].fields}
        self.assertEqual((fields["debug_count_configured"], fields["debug_count"],
                          fields["debug_count_dbus_observed"]), (4, 9, 7))

    def test_reads_remain_responsive_during_blocked_simulator_and_observer(self):
        for operation in ("set", "observe"):
            with self.subTest(operation=operation):
                entered, release = threading.Event(), threading.Event()
                results = []

                class Simulator:
                    def request(self, value, correlation_id):
                        entered.set()
                        if not release.wait(3):
                            raise TimeoutError("fixture timed out")
                        return CommandReceipt(correlation_id, True, "completed", "ack", 1, 2), value

                def observer():
                    entered.set()
                    if not release.wait(3):
                        raise TimeoutError("fixture timed out")
                    return 9

                runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                           simulator=Simulator(), observer=observer)
                runtime._process = FakeProcess()
                def run_operation():
                    if operation == "set":
                        results.append(runtime.set_module_field(module_id="micom", field="debug_count", value=9, correlation_id="slow"))
                    else:
                        results.append(runtime.observe_module(module_id="micom", correlation_id="slow"))
                worker = threading.Thread(target=run_operation, daemon=True)
                worker.start()
                try:
                    self.assertTrue(entered.wait(1), "fixture did not enter I/O")
                    reads = []
                    reader = threading.Thread(target=lambda: reads.append((runtime.get_status(), runtime.get_modules())), daemon=True)
                    start = time.monotonic()
                    reader.start()
                    reader.join(1)
                    self.assertFalse(reader.is_alive(), "status/module read blocked behind guest I/O")
                    self.assertLess(time.monotonic() - start, 1)
                    self.assertEqual(reads[0][0]["state"], "running")
                finally:
                    release.set()
                    worker.join(3)
                self.assertFalse(worker.is_alive())
                self.assertTrue(results[0].accepted)

    def test_stale_results_after_disconnect_or_replacement_are_refused(self):
        for operation in ("set", "observe"):
            for change in ("disconnect", "shutdown", "process", "adapter", "observer"):
                if operation == "set" and change == "observer":
                    continue
                with self.subTest(operation=operation, change=change):
                    entered, release = threading.Event(), threading.Event()
                    results = []

                    class Simulator:
                        def request(self, value, correlation_id):
                            entered.set()
                            if not release.wait(3):
                                raise TimeoutError("fixture timed out")
                            return CommandReceipt(correlation_id, True, "completed", "ack", 1, 2), value

                    def observer():
                        entered.set()
                        if not release.wait(3):
                            raise TimeoutError("fixture timed out")
                        return 9

                    runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                               simulator=Simulator(), observer=observer)
                    runtime._process = FakeProcess()
                    runtime._sim_value, runtime._sim_observed = 3, 4
                    def run_operation():
                        if operation == "set":
                            results.append(runtime.set_module_field(module_id="micom", field="debug_count", value=9, correlation_id="stale"))
                        else:
                            results.append(runtime.observe_module(module_id="micom", correlation_id="stale"))
                    worker = threading.Thread(target=run_operation, daemon=True)
                    worker.start()
                    try:
                        self.assertTrue(entered.wait(1), "fixture did not enter I/O")
                        if change == "shutdown":
                            runtime.shutdown()
                        else:
                            with runtime._sim_lock:
                                if change == "disconnect":
                                    runtime._process.returncode = 0
                                elif change == "process":
                                    runtime._process = FakeProcess()
                                elif change == "adapter":
                                    runtime._simulator = Simulator()
                                else:
                                    runtime._observer = lambda: 9
                    finally:
                        release.set()
                        worker.join(3)
                    self.assertFalse(worker.is_alive())
                    self.assertEqual((results[0].accepted, results[0].state, results[0].command_id),
                                     (False, "disconnected", "stale"))
                    fields = {f.name: f.value for f in runtime.get_modules()[0].fields}
                    self.assertEqual((fields["debug_count"], fields["debug_count_dbus_observed"]), (3, 4))
                    if operation == "set":
                        self.assertEqual(fields["debug_count_configured"], 9)
                    self.assertEqual(runtime.get_events(after_id=0, limit=10)[-1].correlation_id, "stale")

    def test_concurrent_sets_publish_in_serial_guest_io_order(self):
        entered, release = threading.Event(), threading.Event()
        calls, results = [], []

        class Simulator:
            def request(self, value, correlation_id):
                calls.append(value)
                if value == 1:
                    entered.set()
                    if not release.wait(3):
                        raise TimeoutError("fixture timed out")
                return CommandReceipt(correlation_id, True, "completed", "ack", 1, 2), value

        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu, simulator=Simulator())
        runtime._process = FakeProcess()
        def set_value(value):
            results.append(runtime.set_module_field(module_id="micom", field="debug_count", value=value,
                                                    correlation_id=f"set{value}"))
        first = threading.Thread(target=set_value, args=(1,), daemon=True)
        second = threading.Thread(target=set_value, args=(2,), daemon=True)
        first.start()
        try:
            self.assertTrue(entered.wait(1))
            second.start()
            deadline = time.monotonic() + 1
            while time.monotonic() < deadline:
                fields = {f.name: f.value for f in runtime.get_modules()[0].fields}
                if fields["debug_count_configured"] == 2:
                    break
                time.sleep(.005)
            self.assertEqual(fields["debug_count_configured"], 2)
            self.assertEqual(calls, [1])
        finally:
            release.set()
            first.join(3)
            second.join(3)
        self.assertFalse(first.is_alive() or second.is_alive())
        self.assertTrue(all(r.accepted for r in results))
        self.assertEqual(calls, [1, 2])
        fields = {f.name: f.value for f in runtime.get_modules()[0].fields}
        self.assertEqual((fields["debug_count_configured"], fields["debug_count"]), (2, 2))

    def test_fifo_admission_survives_pause_before_io_gate(self):
        for second_kind in ("set", "observe"):
            with self.subTest(second=second_kind):
                first_admitted, second_admitted, release_first = threading.Event(), threading.Event(), threading.Event()
                calls, results = [], {}

                class Simulator:
                    def request(self, value, correlation_id):
                        calls.append(("set", value))
                        return CommandReceipt(correlation_id, True, "completed", "ack", 1, 2), value

                def observe():
                    calls.append(("observe", None))
                    return 1

                runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                           simulator=Simulator(), observer=observe)
                runtime._process = FakeProcess()
                original = runtime._sim_turn

                @contextmanager
                def delayed_turn(ticket):
                    # Pause the first call *after* admission and configured=1,
                    # but before its turn context is entered (the T9 race).
                    if threading.current_thread().name == "fifo-first":
                        first_admitted.set()
                        if not release_first.wait(3):
                            raise TimeoutError("fixture timed out")
                    else:
                        second_admitted.set()
                    with original(ticket):
                        yield

                def first_call():
                    results["first"] = runtime.set_module_field(module_id="micom", field="debug_count", value=1, correlation_id="first")

                def second_call():
                    if second_kind == "set":
                        results["second"] = runtime.set_module_field(module_id="micom", field="debug_count", value=2, correlation_id="second")
                    else:
                        results["second"] = runtime.observe_module(module_id="micom", correlation_id="second")

                first = threading.Thread(target=first_call, name="fifo-first", daemon=True)
                second = threading.Thread(target=second_call, name="fifo-second", daemon=True)
                with mock.patch.object(runtime, "_sim_turn", side_effect=delayed_turn):
                    first.start()
                    try:
                        self.assertTrue(first_admitted.wait(1))
                        self.assertEqual({f.name: f.value for f in runtime.get_modules()[0].fields}["debug_count_configured"], 1)
                        second.start()
                        self.assertTrue(second_admitted.wait(1))
                        second.join(.1)
                        self.assertTrue(second.is_alive(), "later admitted operation overtook the first")
                        self.assertEqual(calls, [])
                        self.assertEqual(runtime.get_status()["state"], "running")
                    finally:
                        release_first.set()
                        first.join(3)
                        second.join(3)
                self.assertFalse(first.is_alive() or second.is_alive())
                self.assertTrue(results["first"].accepted and results["second"].accepted)
                self.assertEqual(calls, [("set", 1), ("set", 2) if second_kind == "set" else ("observe", None)])
                fields = {f.name: f.value for f in runtime.get_modules()[0].fields}
                self.assertEqual(fields["debug_count"], 2 if second_kind == "set" else 1)
                self.assertEqual(fields["debug_count_configured"], 2 if second_kind == "set" else 1)

    def test_failed_effect_releases_fifo_turn(self):
        class Simulator:
            def request(self, value, correlation_id):
                if value == 1:
                    raise ValueError("fixture failure")
                return CommandReceipt(correlation_id, True, "completed", "ack", 1, 2), value
        runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu, simulator=Simulator())
        runtime._process = FakeProcess()
        with self.assertRaisesRegex(ValueError, "fixture failure"):
            runtime.set_module_field(module_id="micom", field="debug_count", value=1)
        self.assertTrue(runtime.set_module_field(module_id="micom", field="debug_count", value=2).accepted)
        self.assertEqual(len(runtime._sim_turns), 0)

    def test_io_exception_after_disconnect_returns_disconnected(self):
        for operation in ("set", "observe"):
            with self.subTest(operation=operation):
                entered, release = threading.Event(), threading.Event()
                results = []
                def fail():
                    entered.set()
                    if not release.wait(3):
                        raise TimeoutError("fixture timed out")
                    raise OSError("closed guest channel")
                class Simulator:
                    def request(self, value, correlation_id):
                        return fail()
                runtime = WorkbenchRuntime(self.workspace, self.directory / "run", self.qemu,
                                           simulator=Simulator(), observer=fail)
                runtime._process = FakeProcess()
                runtime._sim_value, runtime._sim_observed = 3, 4
                def run_operation():
                    if operation == "set":
                        results.append(runtime.set_module_field(module_id="micom", field="debug_count", value=9, correlation_id="closed"))
                    else:
                        results.append(runtime.observe_module(module_id="micom", correlation_id="closed"))
                worker = threading.Thread(target=run_operation, daemon=True)
                worker.start()
                try:
                    self.assertTrue(entered.wait(1))
                    runtime.shutdown()
                finally:
                    release.set()
                    worker.join(3)
                self.assertFalse(worker.is_alive())
                self.assertEqual(results[0].state, "disconnected")
                fields = {f.name: f.value for f in runtime.get_modules()[0].fields}
                self.assertEqual((fields["debug_count"], fields["debug_count_dbus_observed"]), (3, 4))


if __name__ == "__main__":
    unittest.main()
