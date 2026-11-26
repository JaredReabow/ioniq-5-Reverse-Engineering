"""Integration boundary tests that do not launch QEMU or access hardware."""

import io
import json
import base64
import hashlib
import os
import re
import shlex
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import struct
import zlib
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/uk_fw"))
from vm_workbench.cli import KeyboardTapBackend, vm_workbench_hash, vm_workbench_prepare, vm_workbench_spawn, vm_workbench_prepare_foreground, vm_workbench_require_probe_workspace, vm_workbench_capture_loop, vm_workbench_run, vm_workbench_write_acquisition_failure, PROBE_SOURCE_HASH, PROBE_SCRIPT_HASH
from vm_workbench.contracts import CommandReceipt
from vm_workbench.guest_shell import GuestStandbyError
from vm_workbench.guest_shell import GuestShell, GuestAcquisitionError, VM_IVI_CAPTURE_DEADLINE_MS, VM_IVI_VERIFICATION_DEADLINE_MS, vm_guest_acquisition_command, vm_guest_dbus_timeouts, vm_guest_parse_acquisition, vm_guest_decode_capture, vm_guest_parse_debugging_mode, vm_guest_parse_confirm_geometry, vm_guest_parse_startup_receipt, vm_guest_parse_standby_readiness, vm_guest_standby_readiness_command, vm_guest_parse_probe_failure, vm_guest_probe_failure_command, vm_guest_validate_probe_arm, vm_guest_probe_output_png, vm_guest_ivi_frame_export_command, _REASON11_SNAPSHOT_STATES

CONFIRM = (b"VM_OBSERVE_CONFIRM geometry root 0 0 1920 720 bg 0 0 1920 720 "
           b"txt 462 100 1458 620 buttonLocal 10 529 690 63 buttonRoot 479 629 "
           b"enabled true modelEnableBtn 1 visible true wide true dimmed false driving false calling false")
DLT_PREFIX = b"1970/01/01 00:01:11.297223 712970 050 MANG STAN STAN log info V 1 ["
LEGACY_IVI_SCREENSHOT_BUDGET = 'remaining=$(((failure_cutoff-elapsed)/1000)); [ "$remaining" -ge 1 ] || fail capture_budget\n'
IVI_VERIFY_GATE = '\nnow && [ "$elapsed" -lt 30000 ] || fail probe_deadline\nemit "VERIFY_START'
PIPEFAIL_SHELL = "/bin/bash"
REASON11_PHASE_BLOCK = re.compile(
    r"^[^\n]*REASON11_PHASE_([A-Z_]+)_BEGIN\n.*?^[^\n]*REASON11_PHASE_\1_END\n",
    re.M | re.S)
FOREGROUND_DBUS_TIMEOUTS = re.compile(
    r"timeout [0-9]+ /usr/bin/dbus-send --session --print-reply "
    r"--reply-timeout=[0-9]+ --dest=com[.]lge[.]hkmc[.]avn[.]appfunc[.]AppStandbyClock "
    r"/com/lge/hkmc/avn/appfunc/standby "
    r"com[.]lge[.]avn[.]appmanager[.]appbase[.]show_window_fg")


def normalize_generated_dbus_timeouts(script):
    """Replace the one profile-selected foreground timeout pair for stable hashing."""
    normalized, count = FOREGROUND_DBUS_TIMEOUTS.subn(
        "timeout <DBUS_PROFILE> /usr/bin/dbus-send --session --print-reply "
        "--reply-timeout=<DBUS_PROFILE> --dest=com.lge.hkmc.avn.appfunc.AppStandbyClock "
        "/com/lge/hkmc/avn/appfunc/standby "
        "com.lge.avn.appmanager.appbase.show_window_fg",
        script)
    if count != 1:
        raise AssertionError("generated acquisition must contain one foreground D-Bus timeout")
    return normalized


class Backend:
    def __init__(self):
        self.calls = []

    def send_key(self, **kwargs):
        self.calls.append(kwargs)
        return CommandReceipt("fake", True, "completed", "injected", 1, 2)


class OwnedFakeProcess:
    """Fake exact child with observable wait, signal, and pipe state."""
    def __init__(self, timeout_first=False):
        self.stdin, self.stdout, self.stderr = io.BytesIO(), io.BytesIO(), io.BytesIO()
        self.timeout_first, self.returncode = timeout_first, None
        self.signals, self.waits = [], 0

    def poll(self):
        return self.returncode

    def terminate(self):
        self.signals.append("terminate")
        if not self.timeout_first:
            self.returncode = 0

    def kill(self):
        self.signals.append("kill")
        self.returncode = -9

    def wait(self, timeout):
        self.waits += 1
        if self.timeout_first and self.waits == 1:
            raise subprocess.TimeoutExpired("fake-qemu", timeout)
        return self.returncode


class IntegrationTests(unittest.TestCase):
    def test_slow_tcg_profile_is_explicit_and_bounded(self):
        module_root = Path(__file__).resolve().parents[1] / "tools/uk_fw"
        script = (
            "import json,sys;"
            f"sys.path.insert(0,{str(module_root)!r});"
            "from vm_workbench.guest_shell import VM_IVI_CAPTURE_DEADLINE_MS,"
            "VM_IVI_VERIFICATION_DEADLINE_MS,VM_DBUS_REPLY_TIMEOUT_MS,"
            "VM_DBUS_WRAPPER_TIMEOUT_SECONDS,VM_IVI_SETUP_DEADLINE_MS,"
            "VM_IVI_TRANSFER_COMPRESSED,VM_IVI_TRANSFER_TIMEOUT_SECONDS;"
            "print(json.dumps([VM_IVI_CAPTURE_DEADLINE_MS,VM_IVI_VERIFICATION_DEADLINE_MS,"
            "VM_DBUS_REPLY_TIMEOUT_MS,VM_DBUS_WRAPPER_TIMEOUT_SECONDS,VM_IVI_SETUP_DEADLINE_MS,"
            "VM_IVI_TRANSFER_COMPRESSED,VM_IVI_TRANSFER_TIMEOUT_SECONDS]))"
        )
        default_env = os.environ.copy()
        default_env.pop("GEN5W_SLOW_TCG", None)
        default = subprocess.check_output([sys.executable, "-c", script], env=default_env, text=True)
        slow = subprocess.check_output(
            [sys.executable, "-c", script],
            env={**os.environ, "GEN5W_SLOW_TCG": "1"}, text=True,
        )
        self.assertEqual(json.loads(default), [
            30000, 30000, *vm_guest_dbus_timeouts(slow_tcg=False), 10000, False, 120,
        ])
        self.assertEqual(json.loads(slow), [60000, 60000, 12000, 15, 60000, True, 180])
        self.assertEqual(vm_guest_dbus_timeouts(system="Linux", machine="aarch64",
                                                slow_tcg=False), (12000, 15))
        self.assertEqual(vm_guest_dbus_timeouts(system="Linux", machine="arm64",
                                                slow_tcg=False), (12000, 15))
        self.assertEqual(vm_guest_dbus_timeouts(system="Darwin", machine="arm64",
                                                slow_tcg=False), (4000, 5))
        self.assertEqual(vm_guest_dbus_timeouts(system="Linux", machine="x86_64",
                                                slow_tcg=False), (4000, 5))

    def test_acquisition_generated_scan_cache_equivalence_and_corruption(self):
        """Replay the implemented shell/state cache against the full AWK loop."""
        self._vm_test_acquisition_cache_replay()

    def test_acquisition_scan_cache_suffix_reader_failures(self):
        """A failed suffix reader cannot reuse READY or commit parser state."""
        self._vm_test_acquisition_cache_replay(reader_only=True)

    def _vm_test_acquisition_cache_replay(self, *, reader_only=False):
        """Exercise the generated cache with shared host filesystem fixtures."""
        from vm_workbench.guest_shell import _DLT_CONFIRM_ENVELOPE
        token = "e" * 32
        entry = DLT_PREFIX + b"AppStandbyClockEngine::inter_show_window_fg appid =  10 reason =  11 plane =  1 avmode =  -1 command =  0 temporal =  false]\n"
        show = DLT_PREFIX + b"QMLController::showScreen(QString) /app/share/AppStandbyClock/qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml]\n"
        draw = DLT_PREFIX + b"SCREEN_STATE: START DRAW]\n"
        model = DLT_PREFIX + CONFIRM + b"]\n"
        done = DLT_PREFIX + b"SCREEN_STATE: DRAW FINISHED]\n"
        returned = DLT_PREFIX + b"AppStandbyClockEngine::inter_show_window_fg return plane =  1]\n"
        valid = entry + show + draw + model + done + returned
        markers = (b"onTimeout Handler", b"AppStandbyClockEngine::onTimeoutHandler()", b"confirmSkPressed()")
        # The independent record loop is the pre-cache scanner. The policy
        # functions below come from the generated implementation, so this test
        # measures persisted state/iteration rather than a retyped policy.
        oracle_loop = r'''
{if(NR>8192) {bad="line_limit";exit} startpos=n;n+=length($0)+1;sub(/\r$/, "");if(NR>1 && !(partial && NR==2)) check(prev,prev_start);prev=$0;prev_start=startpos}
END {if(complete && NR && !(partial && NR==1)) check(prev,prev_start);__DECISION__}
'''
        with tempfile.TemporaryDirectory(prefix="wb-scan-cache-") as temp:
            directory = Path(temp)
            bb = directory / "busybox"
            bb.write_text('#!/usr/bin/python3\nimport os,sys\na=sys.argv[1:]\n'
                'if a[0]=="stat":\n'
                ' for path in a[3:]:\n'
                '  s=os.stat(path);fmt=a[2];v={"%d":str(s.st_dev),"%i":str(s.st_ino),"%s":str(s.st_size),"%u":"0","%a":oct(s.st_mode&0o777)[2:],"%h":str(s.st_nlink)}\n'
                '  for k,x in v.items(): fmt=fmt.replace(k,x)\n'
                '  print(fmt)\n'
                ' sys.exit(0)\n'
                'os.execvp(a[0],a)\n')
            bb.chmod(0o700)
            for probe in (False, True):
                generated = vm_guest_acquisition_command(token, ivi_probe=probe)
                scan_start = generated.index('check_lines() {')
                functions = generated[generated.index('    function validmodel(', scan_start):generated.index('    function uint(', scan_start)]
                self.assertEqual(hashlib.sha256(functions.rstrip().encode()).hexdigest(),
                    "dc9bd0ab7c746d136b801567dd73d6d997c37f8ba4da7096e7d8cf8d898ac027" if probe else
                    "c59c0b1b2f8a7e5ff345a111c5927a805de98cbfa06b3d61d02be89428d6718e")
                decision = generated.split('      if(bad!="") print "FAIL " bad;', 1)[1].split('\n', 1)[0]
                oracle = functions + oracle_loop.replace('__DECISION__', 'if(bad!="") print "FAIL " bad;' + decision)
                shell_functions = generated[generated.index('boundary() {'):generated.index('\n[ ! -e "$scan" ]')]

                def replay(payloads, *, baseline=b"history\n", change=None, corrupt=None, after_boundary=None):
                    """Run all snapshots in one parent shell, preserving anchors."""
                    log = directory / "log"
                    scan, state, scratch = (directory / name for name in ("scan.dlt", "state", "next"))
                    log.write_bytes(baseline)
                    scan.write_bytes(b"")
                    for path in (state, scratch):
                        path.unlink(missing_ok=True)
                    initial_partial = int(bool(baseline) and not baseline.endswith(b"\n"))
                    script = '\n'.join((
                        'set -o pipefail', 'BB=' + shlex.quote(str(bb)),
                        'log=' + shlex.quote(str(log)), 'scan=' + shlex.quote(str(scan)),
                        'cache=' + shlex.quote(str(state)), 'cache_next=' + shlex.quote(str(scratch)),
                        'cache_id=;cache_next_id=', 'verify_mark() { :; }', shell_functions,
                        "base_id=$($BB stat -c '%d:%i' \"$log\")", 'base=' + str(len(baseline)),
                        'partial=' + str(initial_partial), 'last_size=$base;last_hash=empty',
                        'base_len=256;[ "$base" -ge 256 ] || base_len=$base;base_at=$((base-base_len+1));base_hash=empty',
                        'if [ "$base_len" -gt 0 ];then base_hash=$(tail -c +"$base_at" "$log" | head -c "$base_len" | sha256sum);fi',
                        "trap 'scan_cache_cleanup' 0", 'scan_cache_init || exit 20'))
                    for index, payload in enumerate(payloads):
                        snapshot = directory / ("snapshot-" + str(index))
                        snapshot.write_bytes(baseline + payload)
                        script += '\n' + 'cat ' + shlex.quote(str(snapshot)) + ' > "$log"\n'
                        if change and index == 1:
                            script += change + '\n'
                        if corrupt and index == 1:
                            script += corrupt + '\n'
                        script += 'if ! boundary;then printf "FAIL log_changed\\n";exit 0;fi\n'
                        if after_boundary and index == 1:
                            script += after_boundary + '\n'
                            # A failed read or a policy FAIL must not commit
                            # the speculative state emitted by this scan.
                            script += 'reader_state_hash=$cache_hash;reader_cursor=$cache_cursor\n'
                            script += 'if ! scan_result;then set -- $(sha256sum "$cache");[ "$1" = "$reader_state_hash" ] && [ "$cache_cursor" = "$reader_cursor" ] || exit 21;printf "FAIL log_parse\\n";exit 0;fi\n'
                            script += 'set -- $(sha256sum "$cache");[ "$1" = "$reader_state_hash" ] && [ "$cache_cursor" = "$reader_cursor" ] || exit 22\n'
                        else:
                            script += 'if ! scan_result;then printf "FAIL log_parse\\n";exit 0;fi\n'
                        script += 'printf "%s\\n" "$result"\n'
                    run = subprocess.run(["/bin/bash"], input=script, text=True, capture_output=True,
                                         env=dict(os.environ, LC_ALL="C"), timeout=40)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    if corrupt and '"$cache.old"' in corrupt:
                        self.assertTrue(state.exists())  # a replaced inode is preserved
                    else:
                        self.assertFalse(state.exists())
                    if corrupt and '"$cache_next.old"' in corrupt:
                        self.assertTrue(scratch.exists())  # a replaced inode is preserved
                    else:
                        self.assertFalse(scratch.exists())
                    return run.stdout.splitlines()

                if reader_only:
                    native = DLT_PREFIX + b"onTimeout Handler]\n"
                    prefix = b"new prefix\n"
                    append = prefix + native
                    failed_reader = ('scan_read() { if [ "$1" = tail ] && [ "$2" = -c ] && '
                        '[ "$3" = "+$((cache_cursor+1))" ] && [ "$4" = "$scan" ];then __READ__;return __STATUS__;fi;'
                        '"$bb_original" "$@"; };bb_original=$BB;BB=scan_read')
                    for name, body, status, suffix, expected in (
                            ("zero output", ":", 1, append, "FAIL log_parse"),
                            ("partial output", "printf 'new prefix\\n'", 1, append, "FAIL log_parse"),
                            ("native policy failure", '"$bb_original" "$@"', 141, append,
                             "FAIL native_timeout native_marker=timeout_handler marker_offset=" + str(len(valid + prefix + DLT_PREFIX))),
                            ("early line-limit policy failure", '"$bb_original" "$@"', 141, b"x\n" * 8193,
                             "FAIL line_limit")):
                        with self.subTest(probe=probe, suffix_reader=name):
                            hook = failed_reader.replace('__READ__', body).replace('__STATUS__', str(status))
                            self.assertEqual(replay([valid, valid + suffix], after_boundary=hook)[-1], expected)
                    continue

                corpora = [valid, valid.replace(b"\n", b"\r\n"), b"ignored \xc3\xa9\n" + valid,
                    valid + DLT_PREFIX + b"VM_OBSERVE_CONFIRM visibleChanged false]\n",
                    valid + DLT_PREFIX + b"VM_OBSERVE_CONFIRM enabledChanged false 1]\n",
                    valid + DLT_PREFIX + b"drivingRestriction:true,AppID: 10]\n",
                    valid.replace(b"enabled true", b"enabled maybe"),
                    valid.replace(b"driving false", b"driving true"),
                    valid + DLT_PREFIX + b"AppStandbyClockModel::setCurrentScreenID(int) 1]\n",
                    b"bad VM_OBSERVE_CONFIRM geometry x\n", b"x" * 4097 + b"\n",
                    b"onTimeout Handler\n" + b"x\n" * 8192]
                corpora += [valid + DLT_PREFIX + marker + b"]\n" for marker in markers]
                serial_path = os.environ.get("VM_WORKBENCH_SCAN_REPLAY_SERIAL")
                if serial_path:
                    serial = Path(serial_path).read_bytes()
                    self.assertEqual(hashlib.sha256(serial).hexdigest(),
                        "e4ff3880dd298c8c302331ac68b5b184da16481608b88ef1f08ec7b8f68f9f33")
                    with self.assertRaises(GuestAcquisitionError) as retained:
                        vm_guest_parse_acquisition(serial, "5da4f64375124e21a8ecfbaafa48ccc8", ivi_probe=True)
                    trace = retained.exception.trace
                    self.assertEqual(hashlib.sha256(trace).hexdigest(),
                        "9a9b3e6fc6c866f8f41529e141491d651ea9e79e2cc012b5bc302c2ebb4f5e6a")
                    self.assertEqual(trace.index(b"onTimeout Handler"), 288896)
                    corpora.append(trace)
                comparisons = 0
                for baseline in (b"history\n", b"initial-partial"):
                    # The partial historical boundary needs its own EOF/CRLF
                    # cases; policy failures are already covered above it.
                    selected = corpora if baseline.endswith(b"\n") else corpora[:3] + [b"tail\n" + valid]
                    for payload in selected:
                        cuts = {0, 1, len(entry)-1, len(entry), len(payload)//2, len(payload)-1, len(payload)}
                        for marker in markers:
                            at = payload.find(marker)
                            if at >= 0:
                                cuts.update((at-1, at, at+1, at+len(marker)))
                        cuts = sorted(cut for cut in cuts if cut >= 0)
                        snapshots = [payload[:cut] for cut in cuts if cut <= len(payload)]
                        snapshots.insert(-1, snapshots[-2])  # repeated admitted snapshot
                        expected = []
                        for snapshot in snapshots:
                            run = subprocess.run(["/usr/bin/awk", "-v", "re=" + _DLT_CONFIRM_ENVELOPE,
                                "-v", "base=" + str(len(baseline)), "-v", "partial=" + str(int(not baseline.endswith(b"\n"))),
                                "-v", "complete=" + str(int(snapshot.endswith(b"\n"))), oracle],
                                input=snapshot, capture_output=True, env=dict(os.environ, LC_ALL="C"), timeout=10)
                            self.assertEqual(run.returncode, 0, run.stderr)
                            expected.append(run.stdout.decode().strip())
                        self.assertEqual(replay(snapshots, baseline=baseline), expected)
                        comparisons += len(snapshots)
                self.assertGreater(comparisons, 120)
                for mutation in ('printf corrupt > "$cache"', 'rm -f "$cache"',
                                 'mv "$cache" "$cache.old"; : > "$cache"',
                                 'chmod 644 "$cache"',
                                 'printf corrupt > "$cache";set -- $(sha256sum "$cache");cache_hash=$1'):
                    with self.subTest(probe=probe, mutation=mutation):
                        self.assertEqual(replay([valid, valid], corrupt=mutation)[-1], "FAIL log_parse")
                # Interrupted commit must fail on this invocation and clean both
                # owned files, even when a prefix reached the state inode.
                interrupted = 'scan_copy() { if [ "$1" = cat ] && [ "$2" = "$cache_next" ];then head -c 10 "$cache_next";return 1;fi;"$bb_original" "$@"; };bb_original=$BB;BB=scan_copy'
                with self.subTest(probe=probe, mutation="interrupted persistence"):
                    self.assertEqual(replay([valid, valid], corrupt=interrupted)[-1], "FAIL log_parse")
                for applet, condition in (
                        ("stat", '[ "$1" = stat ] && [ "$#" -eq 5 ] && [ "$3" = "%d:%i:%s:%u:%a:%h" ]'),
                        ("sha256sum", '[ "$1" = sha256sum ] && [ "$#" -eq 3 ] && [ "$2" = "$cache" ]')):
                    with self.subTest(probe=probe, short_pair=applet):
                        # A short successful response must not admit stale metadata
                        # or commit a cache with an unverified second record.
                        short_pair = ('pair_result() { if ' + condition +
                                      ';then "$bb_original" "$@" | head -n 1;else '
                                      '"$bb_original" "$@";fi; };bb_original=$BB;BB=pair_result')
                        self.assertEqual(replay([valid, valid], corrupt=short_pair)[-1], "FAIL log_parse")
                swapped_scratch = (
                    'hash_pair() { if [ "$1" = sha256sum ] && [ "$#" -eq 3 ] && [ "$2" = "$cache" ];then '
                    'mv "$cache_next" "$cache_next.old" && cp -p "$cache_next.old" "$cache_next" || return 1;fi; '
                    '"$bb_original" "$@"; };bb_original=$BB;BB=hash_pair')
                with self.subTest(probe=probe, mutation="scratch replaced while hashing"):
                    self.assertEqual(replay([valid, valid], corrupt=swapped_scratch)[-1], "FAIL log_parse")
                for change in ('mv "$log" "$log.old";cp "$log.old" "$log"', ': > "$log"',
                               'printf z | dd of="$log" bs=1 seek=0 conv=notrunc 2>/dev/null',
                               'printf z | dd of="$log" bs=1 seek=9 conv=notrunc 2>/dev/null'):
                    self.assertEqual(replay([valid, valid], change=change)[-1], "FAIL log_changed")

    def test_probe_output_png_channels_alpha_and_integrity(self):
        from vm_workbench.transport import vm_transport_png_dimensions
        def pixels(png):
            self.assertEqual(vm_transport_png_dimensions(png), (2, 1))
            offset, compressed = 8, bytearray()
            while offset < len(png):
                length = struct.unpack_from(">I", png, offset)[0]
                kind = png[offset + 4:offset + 8]
                payload = png[offset + 8:offset + 8 + length]
                crc = struct.unpack_from(">I", png, offset + 8 + length)[0]
                self.assertEqual(crc, zlib.crc32(kind + payload) & 0xffffffff)
                if kind == b"IDAT": compressed.extend(payload)
                offset += 12 + length
            return zlib.decompress(compressed)
        xrgb = vm_guest_probe_output_png(bytes((3, 2, 1, 0, 30, 20, 10, 91)), 2, 1, 0x20020888)
        self.assertEqual(pixels(xrgb), bytes((0, 1, 2, 3, 255, 10, 20, 30, 255)))
        argb = vm_guest_probe_output_png(bytes((0, 0, 0, 0, 32, 64, 128, 128)), 2, 1, 0x20028888)
        self.assertEqual(pixels(argb), bytes((0, 0, 0, 0, 0, 255, 128, 64, 128)))
        opaque = vm_guest_probe_output_png(bytes((3, 2, 1, 255)) * 2, 2, 1, 0x20028888)
        self.assertEqual(pixels(opaque), bytes((0, 1, 2, 3, 255, 1, 2, 3, 255)))
        for raw, width, height, fmt in ((b"", 2, 1, 0x20020888), (b"x" * 8, 0, 1, 0x20020888),
                                         (b"x" * 8, 2, 1, 0), (bytes((1, 0, 0, 0)) * 2, 2, 1, 0x20028888),
                                         (bytes((129, 0, 0, 128)) * 2, 2, 1, 0x20028888)):
            with self.subTest(raw=raw, width=width, height=height, fmt=fmt), self.assertRaises(ValueError):
                vm_guest_probe_output_png(raw, width, height, fmt)

    def test_readiness_parser_requires_one_complete_current_record(self):
        token = "a" * 32
        record = ("WB_STANDBY_" + token + " READY").encode()
        failure = record.replace(b" READY", b" FAIL standby_exited")
        vm_guest_parse_standby_readiness(b"[ 1.0] kernel message\n" + record + b"\nother\n", token)
        vm_guest_parse_standby_readiness(b"[ 1.0] kernel message\r\n" + record + b"\r\n", token)
        with self.assertRaisesRegex(GuestStandbyError, r"^Gen5W HMI startup failed \(standby_exited\)\.$") as caught:
            vm_guest_parse_standby_readiness(b"kernel message\r\n" + failure + b"\r\n", token)
        self.assertEqual(caught.exception.stage, "standby_exited")
        for bad in (b"", record, record + b"\n" + record + b"\n", record + b"\nWB_STANDBY_" + token.encode() + b" FAIL\n",
                    b"WB_STANDBY_" + b"b" * 32 + b" READY\n", record + b" extra\n",
                    failure, failure + b"\n" + failure + b"\n", record + b"\n" + failure + b"\n",
                    failure.replace(token.encode(), b"b" * 32) + b"\n",
                    record + b"\n" + failure.replace(token.encode(), b"b" * 32) + b"\n",
                    failure.replace(b"standby_exited", b"opaque_private_data") + b"\n",
                    b"prefix " + record + b"\n", record.replace(b" READY", b" UNKNOWN") + b"\n",
                    record + b"\n" + b"x" * 4097 + b"\n", b"x\n" * 32769, record + b"\ntruncated"):
            with self.subTest(data=bad[:100]):
                with self.assertRaises(ValueError) as rejected:
                    vm_guest_parse_standby_readiness(bad, token)
                self.assertNotIn("opaque_private_data", str(rejected.exception))

    def test_readiness_actual_serial_framing_and_terminal_shell_paths(self):
        token = "c" * 32
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            status, launch_log, receipt, shim = (folder / name for name in ("status", "launch.log", "receipt", "busybox"))
            shim.write_text('#!/bin/sh\nif [ "$1" = sleep ]; then\n'
                            '  if [ "$SCENARIO" = ready ]; then printf "%s\\n" WORKBENCH_STANDBY_PREREQUISITES_READY > "$TEST_LOG"; printf "0\\n" > "$TEST_STATUS"; fi\n'
                            '  if [ "$SCENARIO" = failure ]; then printf "7\\n" > "$TEST_STATUS"; fi\n'
                            '  exit 0\nfi\n'
                            'if [ "$1" = timeout ]; then shift 2; fi\n'
                            'if [ "$1" = stat ]; then exec "$TEST_PYTHON" -c \'import os, sys; s = os.lstat(sys.argv[1]); print(f"{s.st_dev}:{s.st_ino}:{s.st_size}:{s.st_mode & 0o777:o}:{s.st_nlink}")\' "$4"; fi\n'
                            'exec "$@"\n')
            shim.chmod(0o755)
            env = dict(os.environ, TEST_LOG=str(launch_log), TEST_STATUS=str(status), TEST_PYTHON=sys.executable)
            def adapt(command):
                for path, fixture in (("/bin/busybox", shim), ("/tmp/workbench-launch.status", status),
                                      ("/tmp/workbench-launch.log", launch_log), ("/tmp/workbench-launch.failure", receipt)):
                    command = command.replace(path, shlex.quote(str(fixture)))
                return command.replace("-lt 310", "-lt 3")
            ready = b"WORKBENCH_STANDBY_PREREQUISITES_READY\n"
            good_receipt = b"standby_exited\n"
            cases = (
                ("ready", None, None, b""),
                ("failure", None, None, b""),
                ("expiry", None, None, b""),
                ("receipt", "25", good_receipt, b""),
                ("legacy", "25", None, b""),
                ("wrong_status", "9", good_receipt, b""),
                ("status_unterminated", b"25", good_receipt, b""),
                ("status_extra_newline", b"25\n\n", good_receipt, b""),
                ("status_nul", b"2\x005\n", good_receipt, b""),
                ("status_alternate", b"025\n", good_receipt, b""),
                ("ready_nonzero", "25", good_receipt, ready),
                ("conflicting_receipt", "0", good_receipt, ready),
                ("ready_missing_marker", "0", None, b""),
                ("unterminated", "25", good_receipt[:-1], b""),
                ("embedded_nul", "25", b"standby_\x00exited\n", b""),
                ("crlf", "25", b"standby_exited\r\n", b""),
                ("duplicate", "25", good_receipt * 2, b""),
                ("extra_newline", "25", good_receipt + b"\n", b""),
                ("oversize", "25", good_receipt + b" " * 64, b""),
                ("unknown", "25", b"opaque_private_data\n", b""),
                ("public_mode", "25", good_receipt, b""),
                ("hardlink", "25", good_receipt, b""),
                ("symlink", "25", good_receipt, b""),
                ("dangling_link", "25", None, b""),
                ("fifo", "25", None, b""),
            )
            linked = folder / "link-target"
            for scenario, code, content, marker in cases:
                with self.subTest(scenario=scenario):
                    for path in (status, receipt, linked):
                        path.unlink(missing_ok=True)
                    launch_log.write_bytes(marker + b"opaque_private_data\n")
                    if code is not None:
                        status.write_bytes(code if isinstance(code, bytes) else (code + "\n").encode("ascii"))
                    if content is not None:
                        destination = linked if scenario in ("hardlink", "symlink") else receipt
                        destination.write_bytes(content)
                        destination.chmod(0o644 if scenario == "public_mode" else 0o600)
                    if scenario == "hardlink":
                        os.link(linked, receipt)
                    if scenario in ("symlink", "dangling_link"):
                        receipt.symlink_to(linked)
                    if scenario == "fifo":
                        os.mkfifo(receipt)
                    # The generated guest command deliberately requires pipefail, as does
                    # the BusyBox ash used in the VM.  Debian's /bin/sh is dash and exits
                    # before exercising the receipt protocol, so use the portable Bash
                    # fixture explicitly instead of depending on the host's sh provider.
                    proc = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, env=dict(env, SCENARIO=scenario))
                    serial = folder / (scenario + ".serial")
                    bridge = GuestShell(proc, serial, lambda *args: None)
                    original_run = bridge._run
                    def adapted(command, **kwargs):
                        # Reproduce the observed kernel lines inside real WB_BEGIN/WB_END framing.
                        return original_run("printf '[    3.184339] random: dbus-uuidgen urandom read with 17 bits of entropy available\\r\\n'; "
                                            "printf '[    3.373738] NET: Registered protocol family 1\\n'; " + adapt(command) +
                                            "; rc=$?; printf '[    3.341792] kernel warning\\n'; (exit \"$rc\")", **kwargs)
                    try:
                        with mock.patch.object(bridge, "_run", side_effect=adapted), \
                             mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()):
                            if scenario == "ready":
                                self.assertIsNone(bridge.wait_standby_prerequisites())
                            elif scenario == "receipt":
                                with self.assertRaises(GuestStandbyError) as failed:
                                    bridge.wait_standby_prerequisites()
                                self.assertEqual(failed.exception.stage, "standby_exited")
                            else:
                                with self.assertRaises(RuntimeError) as failed:
                                    bridge.wait_standby_prerequisites()
                                self.assertIs(type(failed.exception), RuntimeError)
                                self.assertEqual(str(failed.exception), "guest operation failed with status 1")
                    finally:
                        proc.terminate(); proc.wait(timeout=5); proc.stdin.close(); bridge.close(); proc.stdout.close()
                    self.assertNotIn(b"opaque_private_data", serial.read_bytes())

    def test_startup_receipt_strict_identity_and_correlation(self):
        valid = b"WB_IHU_STARTUP 1 sender=:1.42 owner=:1.3 request=7 reply=15 reply_serial=7 len=32 byte0=08 tail_zero=31\n"
        self.assertEqual(vm_guest_parse_startup_receipt(valid)["request_serial"], 7)
        boundary = valid.replace(b"request=7", b"request=4294967295").replace(b"reply_serial=7", b"reply_serial=4294967295")
        self.assertEqual(vm_guest_parse_startup_receipt(boundary)["request_serial"], 4294967295)
        for bad in (b"", valid + valid, valid.replace(b"reply_serial=7", b"reply_serial=8"),
                    valid.replace(b"owner=:1.3", b"owner=:1.42"), valid.replace(b"len=32", b"len=31"),
                    valid.replace(b"byte0=08", b"byte0=09"), valid[:-1],
                    boundary.replace(b"4294967295", b"4294967296")):
            with self.subTest(data=bad), self.assertRaises(ValueError):
                vm_guest_parse_startup_receipt(bad)

    def test_acquisition_protocol_is_ordered_and_failure_preserves_evidence(self):
        token, payload = "a" * 32, b"fixture"
        digest = hashlib.sha256(payload).hexdigest()
        stages = ["BEGIN owner=:1.4 pid=786", "REASON11_SENT 0", "REASON11_ACK 100 sender=:1.4 dest=:1.19 reply_serial=2",
                  "IVI_SENT 100", "IVI_ACK 200 status=0 ack=IVI_FG_REQUEST_SENT",
                  "NATIVE 300 entry=100 show=200 draw_start=300 model=400 draw_end=500 native_return=600 timestamps=00:00:01.000000,00:00:01.000001,00:00:01.000002,00:00:01.000003,00:00:01.000004,00:00:01.000005",
                  "MODEL 300 " + CONFIRM.decode(), "CAPTURE_START 300", "VISIBILITY 500 button_hidden=1",
                  f"CAPTURE_DONE 600 size={len(payload)} sha256={digest}", "OK 600"]
        def packet(rows):
            return ("\n".join("WB_ACQ_" + token + " " + row for row in rows) + "\n" +
                    f"WB_FRAME_{token} META {len(payload)} {digest}\nWB_FRAME_{token} CHUNK 1 {base64.b64encode(payload).decode()}\nWB_FRAME_{token} END 1\n").encode()
        model, frame, records = vm_guest_parse_acquisition(packet(stages), token)
        self.assertFalse(model["driving"]); self.assertEqual(frame, payload); self.assertEqual(len(records), 11)
        for rows in (stages[:3] + stages[2:], stages[:2] + stages[3:], stages[:-1],
                     stages[:-1] + ["FAIL 600 capture cutoff=10000 diagnostic_ms=700"], stages + ["FAIL 601 capture cutoff=10000 diagnostic_ms=700"],
                     stages[:6] + [stages[6].replace("MODEL 300", "MODEL 10000")] + stages[7:],
                     stages[:5] + [stages[5].replace("show=200", "show=100")] + stages[6:]):
            with self.assertRaises((ValueError, GuestAcquisitionError)):
                vm_guest_parse_acquisition(packet(rows), token)
        with self.assertRaises(ValueError):
            vm_guest_parse_acquisition(packet(stages) + ("WB_ACQ_" + token + "BAD\n").encode(), token)
        with self.assertRaises(GuestAcquisitionError) as caught:
            vm_guest_parse_acquisition(packet(stages[:4] + ["FAIL 150 ivi_ack cutoff=10000 diagnostic_ms=250"]), token)
        self.assertEqual(caught.exception.stage, "ivi_ack")
        self.assertEqual(caught.exception.records[-1]["detail"], "ivi_ack cutoff=10000 diagnostic_ms=250")
        self.assertEqual([r["stage"] for r in caught.exception.records], ["BEGIN", "REASON11_SENT", "REASON11_ACK", "IVI_SENT", "FAIL"])
        with self.assertRaises(GuestAcquisitionError) as enriched:
            vm_guest_parse_acquisition(packet(stages[:4] + [
                "FAIL 150 native_timeout native_marker=timeout_handler marker_offset=42 cutoff=10000 diagnostic_ms=250"]), token)
        self.assertEqual(enriched.exception.stage, "native_timeout")
        self.assertIn("native_marker=timeout_handler marker_offset=42", enriched.exception.records[-1]["detail"])
        for detail in (
                "native_timeout native_marker=unknown marker_offset=42 cutoff=10000 diagnostic_ms=250",
                "native_timeout native_marker=timeout_handler marker_offset=1048576 cutoff=10000 diagnostic_ms=250",
                "native_timeout marker_offset=42 native_marker=timeout_handler cutoff=10000 diagnostic_ms=250",
                "capture native_marker=timeout_handler marker_offset=42 cutoff=10000 diagnostic_ms=250"):
            with self.subTest(detail=detail), self.assertRaises(ValueError):
                vm_guest_parse_acquisition(packet(stages[:4] + ["FAIL 150 " + detail]), token)
        for truncated in ("FAIL", "FAIL 150"):
            with self.subTest(truncated=truncated), self.assertRaises(ValueError):
                vm_guest_parse_acquisition(packet(stages[:4] + [truncated]), token)
        with self.assertRaises(ValueError):
            vm_guest_parse_acquisition(packet(stages[:4] + ["FAIL 150 ivi_ack cutoff=10000 diagnostic_ms=149"]), token)
        evidence_encoded = base64.b64encode(b"evidence\n").decode()
        reason = (f"WB_ACQ_{token} BEGIN owner=:1.4 pid=786\nWB_ACQ_{token} REASON11_SENT 0\n"
                  f"WB_REASON11_{token} epoch=100000 owner=:1.4 pid=786 start=456 current_owner=:1.4 current_pid=786 current_start=456 snapshot=ok\n"
                  f"WB_TRACE_{token} {evidence_encoded}\nWB_ACQ_{token} FAIL 4000 reason11 cutoff=10000 diagnostic_ms=4200\n").encode()
        with self.assertRaises(GuestAcquisitionError) as reason_error:
            vm_guest_parse_acquisition(reason, token)
        self.assertEqual(reason_error.exception.stage, "reason11")
        self.assertEqual(base64.b64decode(reason_error.exception.reason11_diagnostic["trace_base64"]), b"evidence\n")
        self.assertEqual(reason_error.exception.reason11_diagnostic["complete_prefix"], {
            "evidence": "insufficient_evidence",
            "handler_entry_observation": "insufficient_evidence",
            "draw_progress_observation": "insufficient_evidence",
            "record_count": 0,
            "absence_not_proven": True,
        })
        newline_prefix = (f"WB_ACQ_{token} BEGIN owner=:1.4 pid=786\nWB_ACQ_{token} REASON11_SENT 0\n"
                          f"WB_REASON11_{token} epoch=100000 owner=:1.4 pid=786 start=456 current_owner=:1.4 current_pid=786 current_start=456 snapshot=newline_check_failed\n"
                          f"WB_REASON11_PREFIX_{token} evidence=complete_prefix handler_entry=observed draw_progress=observed records=2\n"
                          f"WB_ACQ_{token} FAIL 4000 reason11 cutoff=10000 diagnostic_ms=4200\n").encode()
        with self.assertRaises(GuestAcquisitionError) as prefix_error:
            vm_guest_parse_acquisition(newline_prefix, token)
        self.assertEqual(prefix_error.exception.trace, b"")
        self.assertEqual(prefix_error.exception.reason11_diagnostic["snapshot"], "newline_check_failed")
        self.assertEqual(prefix_error.exception.reason11_diagnostic["complete_prefix"], {
            "evidence": "complete_prefix",
            "handler_entry_observation": "observed",
            "draw_progress_observation": "observed",
            "record_count": 2,
            "absence_not_proven": True,
        })
        dispatched = newline_prefix.replace(
            f"WB_ACQ_{token} REASON11_SENT 0\n".encode(),
            (f"WB_ACQ_{token} REASON11_SENT 0\n"
             f"WB_ACQ_{token} REASON11_CALL 3900 rc=1 class=dbus_no_reply "
             "bytes=173 duration_ms=3900\n").encode(),
            1,
        )
        with self.assertRaises(GuestAcquisitionError) as dispatch_error:
            vm_guest_parse_acquisition(dispatched, token)
        self.assertEqual(dispatch_error.exception.reason11_diagnostic["dispatch"], {
            "exit_code": 1,
            "result": "dbus_no_reply",
            "response_bytes": 173,
            "clipped": False,
            "duration_ms": 3900,
        })
        self.assertEqual(
            str(dispatch_error.exception),
            "foreground acquisition failed: reason11 "
            "(D-Bus NoReply after 3900 ms; service identity unchanged)",
        )
        probe_dispatched = (
            f"WB_ACQ_{token} BEGIN owner=:1.4 pid=786\n"
            f"WB_ACQ_{token} PROBE_ARM 10 pid=786 start=456 epoch=100000 arm=100010 deadline=129999\n"
            f"WB_ACQ_{token} BASELINE 20 time=100020 size=16 format=537036936 "
            "buffer=0x30 surface=0x10 output=0x20 "
            "sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa "
            "ack_sha=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
            f"WB_ACQ_{token} REASON11_SENT 30 monotonic=100030\n"
            f"WB_ACQ_{token} REASON11_CALL 4380 rc=1 class=dbus_no_reply "
            "bytes=252 duration_ms=4350\n"
            f"WB_REASON11_{token} epoch=100000 owner=:1.4 pid=786 start=456 "
            "current_owner=:1.4 current_pid=786 current_start=456 snapshot=newline_check_failed\n"
            f"WB_REASON11_PREFIX_{token} evidence=insufficient_evidence "
            "handler_entry=insufficient_evidence draw_progress=insufficient_evidence records=0\n"
            f"WB_REASON11_PHASE_{token} phase=unavailable\n"
            f"WB_ACQ_{token} FAIL 7089 reason11 cutoff=30000 diagnostic_ms=11979\n"
        ).encode()
        with self.assertRaises(GuestAcquisitionError) as probe_error:
            vm_guest_parse_acquisition(probe_dispatched, token, ivi_probe=True)
        self.assertEqual(probe_error.exception.reason11_diagnostic["dispatch"]["result"],
                         "dbus_no_reply")
        self.assertEqual(probe_error.exception.reason11_diagnostic["dispatch"]["duration_ms"], 4350)
        for malformed_call in (
                f"WB_ACQ_{token} REASON11_CALL 3900 rc=0 class=dbus_no_reply bytes=173 duration_ms=3900",
                f"WB_ACQ_{token} REASON11_CALL 3900 rc=1 class=unknown bytes=173 duration_ms=3900",
                f"WB_ACQ_{token} REASON11_CALL 3900 rc=1 class=dbus_no_reply bytes=1025 duration_ms=3900",
                f"WB_ACQ_{token} REASON11_CALL 3900 rc=1 class=dbus_no_reply bytes=173 duration_ms=3901"):
            malformed = dispatched.replace(
                f"WB_ACQ_{token} REASON11_CALL 3900 rc=1 class=dbus_no_reply "
                "bytes=173 duration_ms=3900".encode(),
                malformed_call.encode(),
                1,
            )
            with self.subTest(malformed_call=malformed_call), self.assertRaises(ValueError):
                vm_guest_parse_acquisition(malformed, token)
        clipped_ack = (
            f"WB_ACQ_{token} BEGIN owner=:1.4 pid=786\n"
            f"WB_ACQ_{token} REASON11_SENT 0\n"
            f"WB_ACQ_{token} REASON11_CALL 3900 rc=0 class=reply "
            "bytes=1025 clipped=true duration_ms=3900\n"
            f"WB_ACQ_{token} REASON11_ACK 3900 sender=:1.4 dest=:1.19 reply_serial=2\n"
        ).encode()
        with self.assertRaises(ValueError):
            vm_guest_parse_acquisition(clipped_ack, token)
        for return_code in (124, 143):
            wrapper_timeout = dispatched.replace(
                f"WB_ACQ_{token} REASON11_CALL 3900 rc=1 class=dbus_no_reply "
                "bytes=173 duration_ms=3900".encode(),
                (f"WB_ACQ_{token} REASON11_CALL 4000 rc={return_code} "
                 "class=wrapper_timeout bytes=0 duration_ms=4000").encode(),
                1,
            )
            with self.assertRaises(GuestAcquisitionError) as timeout_error:
                vm_guest_parse_acquisition(wrapper_timeout, token)
            self.assertEqual(timeout_error.exception.reason11_diagnostic["dispatch"], {
                "exit_code": return_code,
                "result": "wrapper_timeout",
                "response_bytes": 0,
                "clipped": False,
                "duration_ms": 4000,
            })
        clipped = dispatched.replace(
            b"bytes=173 duration_ms=3900",
            b"bytes=1025 clipped=true duration_ms=3900",
            1,
        )
        with self.assertRaises(GuestAcquisitionError) as clipped_error:
            vm_guest_parse_acquisition(clipped, token)
        self.assertEqual(clipped_error.exception.reason11_diagnostic["dispatch"],
                         {"exit_code": 1, "result": "dbus_no_reply",
                          "response_bytes": 1025, "clipped": True, "duration_ms": 3900})
        boundary = dispatched.replace(
            b"bytes=173 duration_ms=3900",
            b"bytes=1024 clipped=false duration_ms=3900",
            1,
        )
        with self.assertRaises(GuestAcquisitionError) as boundary_error:
            vm_guest_parse_acquisition(boundary, token)
        self.assertEqual(boundary_error.exception.reason11_diagnostic["dispatch"],
                         {"exit_code": 1, "result": "dbus_no_reply",
                          "response_bytes": 1024, "clipped": False, "duration_ms": 3900})
        unavailable = dispatched.replace(
            b"bytes=173 duration_ms=3900",
            b"bytes=173 clipped=false duration_ms=unavailable",
            1,
        )
        with self.assertRaises(GuestAcquisitionError) as unavailable_error:
            vm_guest_parse_acquisition(unavailable, token)
        self.assertEqual(unavailable_error.exception.reason11_diagnostic["dispatch"]["duration_ms"],
                         "unavailable")
        for invalid_clip in (
                b"bytes=1025 clipped=false duration_ms=3900",
                b"bytes=1024 clipped=true duration_ms=3900",
                b"bytes=1026 clipped=true duration_ms=3900"):
            malformed = dispatched.replace(b"bytes=173 duration_ms=3900", invalid_clip, 1)
            with self.subTest(invalid_clip=invalid_clip), self.assertRaises(ValueError):
                vm_guest_parse_acquisition(malformed, token)
        for state in _REASON11_SNAPSHOT_STATES:
            with self.subTest(snapshot_state=state):
                transcript = reason.replace(b"snapshot=ok", b"snapshot=" + state.encode(), 1)
                if state != "ok":
                    transcript = transcript.replace(
                        f"WB_TRACE_{token} {evidence_encoded}\n".encode(), b"")
                with self.assertRaises(GuestAcquisitionError) as snapshot_error:
                    vm_guest_parse_acquisition(transcript, token)
                self.assertEqual(snapshot_error.exception.reason11_diagnostic["snapshot"], state)
                self.assertEqual(snapshot_error.exception.reason11_diagnostic["complete_prefix"]["evidence"],
                                 "insufficient_evidence")
        for prefix_record in (
                f"WB_REASON11_PREFIX_{token} evidence=complete_prefix handler_entry=observed draw_progress=observed records=2",
                f"WB_REASON11_PREFIX_{token} evidence=complete_prefix handler_entry=observed draw_progress=observed records=2049"):
            malformed_prefix = newline_prefix.replace(
                f"WB_REASON11_PREFIX_{token} evidence=complete_prefix handler_entry=observed draw_progress=observed records=2".encode(),
                prefix_record.encode())
            if prefix_record.endswith("records=2"):
                malformed_prefix = malformed_prefix.replace(b"draw_progress=observed records=2",
                                                             b"draw_progress=unknown records=2")
            with self.assertRaises(GuestAcquisitionError) as invalid_prefix:
                vm_guest_parse_acquisition(malformed_prefix, token)
            self.assertFalse(hasattr(invalid_prefix.exception, "reason11_diagnostic"))
        snapshot_line = next(line for line in newline_prefix.splitlines(keepends=True)
                             if line.startswith(f"WB_REASON11_{token} ".encode()))
        prefix_line = next(line for line in newline_prefix.splitlines(keepends=True)
                           if line.startswith(f"WB_REASON11_PREFIX_{token} ".encode()))
        snapshot_marker = f"WB_REASON11_{token}".encode()
        prefix_marker = f"WB_REASON11_PREFIX_{token}".encode()
        swapped_channels = newline_prefix.replace(snapshot_marker, b"WB_REASON11_SWAP", 1)
        swapped_channels = swapped_channels.replace(prefix_marker, snapshot_marker, 1)
        swapped_channels = swapped_channels.replace(b"WB_REASON11_SWAP", prefix_marker, 1)
        malformed_channels = (
            newline_prefix.replace(snapshot_line, b""),
            newline_prefix.replace(prefix_line, b"").replace(b"epoch=100000", b"invalid=100000", 1),
            swapped_channels,
        )
        for malformed_channel in malformed_channels:
            with self.assertRaises(GuestAcquisitionError) as channel_error:
                vm_guest_parse_acquisition(malformed_channel, token)
            self.assertFalse(hasattr(channel_error.exception, "reason11_diagnostic"))
        for bad in (reason.replace(b"pid=786 start=456", b"pid=787 start=456", 1),
                    reason.replace(b"epoch=100000", b"epoch=0", 1),
                    reason.replace(b"snapshot=ok", b"snapshot=invalid", 1),
                    reason.replace(evidence_encoded.encode(), b"%%%", 1),
                    reason.replace(("WB_TRACE_" + token).encode(), ("prefix WB_TRACE_" + token).encode(), 1),
                    reason.replace(evidence_encoded.encode(), b"A" * 129, 1)):
            with self.assertRaises(GuestAcquisitionError) as invalid:
                vm_guest_parse_acquisition(bad, token)
            self.assertEqual(invalid.exception.stage, "reason11")
            self.assertFalse(hasattr(invalid.exception, "reason11_diagnostic"))
        malformed_trace = (f"prefix WB_TRACE_{token} QQ==\n").encode()
        other_failure = packet(stages[:4] + ["FAIL 150 ivi_ack cutoff=10000 diagnostic_ms=250"])
        with self.assertRaises(ValueError):
            vm_guest_parse_acquisition(other_failure + malformed_trace, token)
        command = vm_guest_acquisition_command(token)
        self.assertEqual(command.count("com.lge.avn.appmanager.appbase.show_window_fg"), 1)
        self.assertEqual(command.count("/ivi-fg-standby1000"), 1)
        self.assertEqual(command.count("/usr/libexec/weston-screenshooter"), 1)
        self.assertLess(command.index('emit "MODEL'), command.index("weston-screenshooter"))
        self.assertEqual(command.count("|| reason_last=invalid"), 1)
        self.assertIn('elif [ "$reason_last" = invalid ]; then reason_status=read_failed', command)
        snapshot_pattern = re.compile(
            r"^[^\n]*REASON11_SNAPSHOT_CLASSIFY_BEGIN\n.*?^[^\n]*REASON11_SNAPSHOT_CLASSIFY_END\n",
            re.M | re.S)
        prefix_pattern = re.compile(
            r"^[^\n]*REASON11_COMPLETE_PREFIX_BEGIN\n.*?^[^\n]*REASON11_COMPLETE_PREFIX_END\n",
            re.M | re.S)
        self.assertEqual(command.count('$BB timeout 2 $BB wc -c < "$scan"'), 1)
        for probe, baseline_digest in ((False, "bc9858b98f20ef2c3284d2d154f659b23efbc3fba0e314d437f6d17e33da107f"),
                                       (True, "950c9ae9426e81b7f936b8b070bd68c1ab757794d5c5ae7b789d496924bad448")):
            with self.subTest(generated_core=probe):
                generated = vm_guest_acquisition_command(token, ivi_probe=probe)
                # A nonzero newline-check pipeline now retains its diagnostic state.
                # Restore the pre-0.4.1 fallback and remove the classifiers. The
                # digest includes the intentional 0.4.7 capture deadline.
                stripped = REASON11_PHASE_BLOCK.sub("", prefix_pattern.sub("", snapshot_pattern.sub("", generated))).replace(
                    "|| reason_last=invalid", "|| reason_last=0", 1)
                if probe:
                    stripped = stripped.replace(IVI_VERIFY_GATE, LEGACY_IVI_SCREENSHOT_BUDGET + IVI_VERIFY_GATE, 1)
                stripped = normalize_generated_dbus_timeouts(stripped)
                self.assertEqual(hashlib.sha256(stripped.encode()).hexdigest(), baseline_digest)
                syntax = subprocess.run(["/bin/bash", "-n"], input=generated, text=True, capture_output=True)
                self.assertEqual(syntax.returncode, 0, syntax.stderr)
        bridge = GuestShell.__new__(GuestShell)
        events = []
        bridge._event = lambda *args: events.append(args)
        with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
             mock.patch.object(bridge, "_run", return_value=packet(stages[:-1])):
            with self.assertRaises(ValueError):
                bridge.foreground_and_capture()
        self.assertEqual(events[-1][1], "acquisition_invalid")
        self.assertTrue(events[-1][2]["unvalidated_records"])

    def test_ivi_probe_deadline_allows_observed_native_transition_to_complete(self):
        token = "d" * 32
        command = vm_guest_acquisition_command(token, ivi_probe=True)
        self.assertEqual((VM_IVI_CAPTURE_DEADLINE_MS, VM_IVI_VERIFICATION_DEADLINE_MS), (30000, 30000))
        self.assertIn("deadline_ms=$((epoch_ms+29999))", command)
        self.assertIn("capture_deadline=30000 verification_deadline=30000", command)
        self.assertIn("failure_cutoff=10000", command)
        self.assertIn("probe_published=1\nfailure_cutoff=30000", command)
        self.assertIn('now && [ "$elapsed" -lt "$failure_cutoff" ] || fail baseline_deadline', command)
        self.assertIn('remaining=$(((failure_cutoff-elapsed)/1000))', command)
        self.assertNotIn('remaining=$(((10000-elapsed)/1000))', command)
        self.assertEqual(subprocess.run(["/bin/bash", "-n"], input=command, text=True,
                                        capture_output=True).returncode, 0)
        begin = {"owner": ":1.4", "pid": 786}
        detail = b"pid=786 start=456 epoch=100000 arm=105533 deadline=129999"
        self.assertEqual(vm_guest_validate_probe_arm(begin, detail, 5533)["deadline"], 129999)
        with self.assertRaises(ValueError):
            vm_guest_validate_probe_arm(begin, detail.replace(b"129999", b"124999"), 5533)
        failure_command = vm_guest_probe_failure_command(token, 786, 456, 100000, 129999)
        self.assertIn("WB_FAIL_", failure_command)
        self.assertEqual(subprocess.run(["/bin/bash", "-n"], input=failure_command, text=True,
                                        capture_output=True).returncode, 0)
        with self.assertRaises(ValueError):
            vm_guest_probe_failure_command(token, 786, 456, 100000, 124999)

    def test_ivi_verification_keeps_the_final_capture_millisecond(self):
        """Execute the generated post-model gates against fixed guest clock samples."""
        token = "d" * 32
        budget_function = 'budget() { now && [ "$elapsed" -lt "$failure_cutoff" ] || fail deadline; }'
        for probe, cutoff, first, second, expected in (
                (True, 30000, 29999, 29999, "VERIFY_START 29999 capture_deadline=30000 verification_deadline=30000 timing_schema=1"),
                (True, 30000, 30000, 30000, "deadline"),
                (True, 30000, 29999, 30000, "probe_deadline"),
                (False, 10000, 9001, 9001, "capture_budget"),
                (False, 10000, 9000, 9000, "CAPTURE_START 9000")):
            with self.subTest(probe=probe, first=first, second=second):
                command = vm_guest_acquisition_command(token, ivi_probe=probe)
                self.assertIn(budget_function, command)
                self.assertEqual(command.count("|| fail capture_budget"), 0 if probe else 1)
                self.assertEqual(command.count("|| fail ivi_budget"), 1)
                model = command.index('emit "MODEL $elapsed $model"\n')
                marker = command.index('emit "VERIFY_START ' if probe else 'emit "CAPTURE_START ', model)
                gates = command[command.index("\n", model) + 1:command.index("\n", marker)]
                fixture = (
                    f'failure_cutoff={cutoff}\nnext_sample={first}\n'
                    f'now() {{ elapsed=$next_sample; next_sample={second}; }}\n'
                    'fail() { printf "%s\\n" "$1"; exit 0; }\n'
                    'emit() { printf "%s\\n" "$1"; }\n'
                    f'{budget_function}\n{gates}\n'
                )
                run = subprocess.run([PIPEFAIL_SHELL], input=fixture, text=True,
                                     capture_output=True, timeout=5)
                self.assertEqual((run.returncode, run.stdout.strip()), (0, expected), run.stderr)

    def test_foreground_probe_binds_native_epoch_and_does_not_qualify_pixels(self):
        token, image = "a" * 32, bytes(1920 * 720 * 4)
        digest = hashlib.sha256(image).hexdigest()
        native = "entry=100 show=200 draw_start=300 model=400 draw_end=500 native_return=600 timestamps=00:00:01.000000,00:00:01.000001,00:00:01.000002,00:00:01.000003,00:00:01.000004,00:00:01.000005"
        arm = "PROBE_ARM 10 pid=786 start=456 epoch=100000 arm=100010 deadline=129999"
        base_sha = hashlib.sha256(b"baseline-content").hexdigest()
        ack_sha = hashlib.sha256((token + " 786 456 100020 16 537036936 0x30 0x10 0x20 " + base_sha + "\n").encode()).hexdigest()
        baseline = "BASELINE 20 time=100020 size=16 format=537036936 buffer=0x30 surface=0x10 output=0x20 sha256=" + base_sha + " ack_sha=" + ack_sha
        capture = ("PROBE_CAPTURE 600 capture=100500 sequence=1 width=1920 height=720 format=537004168 size=5529600 sha256=" + digest + " receipt_sha=" + "b" * 64 +
                   " baseline_time=100020 baseline_size=16 baseline_format=537036936 baseline_buffer=0x30 selected_buffer=0x30 observations=1 baseline_sha=" + base_sha + " ack_sha=" + ack_sha + " observation_start=100100 mode=source-content-change")
        stages = ["BEGIN owner=:1.4 pid=786", arm, baseline, "REASON11_SENT 30 monotonic=100030", "REASON11_ACK 100 sender=:1.4 dest=:1.19 reply_serial=2",
                  "OBSERVE 100 monotonic=100100", "IVI_SENT 100", "IVI_ACK 200 status=0 ack=IVI_FG_REQUEST_SENT", "NATIVE 300 " + native,
                  "MODEL 300 " + CONFIRM.decode(), "VERIFY_START 300 capture_deadline=30000 verification_deadline=30000",
                  "RECEIPT_BOUND 500 capture=100500", "VISIBILITY 500 button_hidden=0", capture,
                  "VERIFY_DONE 600 capture_deadline=30000 verification_deadline=30000", "OK 600"]
        def packet(rows):
            return ("\n".join("WB_ACQ_" + token + " " + row for row in rows) + "\n").encode()
        model, frame, records = vm_guest_parse_acquisition(packet(stages), token, ivi_probe=True)
        self.assertFalse(model["driving"]); self.assertEqual(frame, b"")
        self.assertEqual([row["stage"] for row in records][1:4], ["PROBE_ARM", "BASELINE", "REASON11_SENT"])
        # Schema 1 requires every completed verification boundary. Legacy
        # evidence deliberately retains its original all-or-nothing protocol.
        phase_names = ("VERIFY_IDENTITY", "VERIFY_OUTPUT", "VERIFY_IDENTITY_RECHECK",
                       "VERIFY_LOG_SCAN_1", "VERIFY_IDENTITY_FINAL", "VERIFY_LOG_SCAN_2")
        phase_rows = [name + " 500" for name in phase_names]
        timed = [row + " timing_schema=1" if row.startswith(("VERIFY_START ", "VERIFY_DONE ")) else row
                 for row in stages[:12] + phase_rows + stages[12:]]
        _, _, timed_records = vm_guest_parse_acquisition(packet(timed), token, ivi_probe=True)
        self.assertEqual([row["stage"] for row in timed_records][12:18], list(phase_names))
        prefix = ("WB_VERIFY_" + token + " ").encode()
        sample = b"identity.begin=100.50 identity.owner_query=100.51 identity.owner_parse=100.513\n"
        _, _, with_samples = vm_guest_parse_acquisition(packet(timed) + prefix + sample, token, ivi_probe=True)
        self.assertEqual(with_samples[11]["verification_timings"], [
            {"phase": "identity", "operation": "owner_query", "elapsed_ms": 510, "duration_ms": 10},
            {"phase": "identity", "operation": "owner_parse", "elapsed_ms": 513, "duration_ms": 3},
        ])
        for invalid in (
            b"identity.begin=100.48 identity.owner_query=100.51\n",
            b"identity.begin=100.50 identity.owner_query=0.51\n",
            b"identity.begin=100.50 identity.owner_query=100.61\n",
            b"identity.begin=100.50 identity.owner_parse=100.51\n",
            b"identity.begin=100.50 identity.owner_query=private-text\n",
            sample.rstrip(b"\n") + b" x" * 4096 + b"\n",
            sample.rstrip(b"\n"),
            sample + prefix + sample,
        ):
            with self.subTest(timing_sample=invalid[:80]):
                _, _, without_samples = vm_guest_parse_acquisition(packet(timed) + prefix + invalid, token, ivi_probe=True)
                self.assertEqual(without_samples, timed_records)
        with self.assertRaises(GuestAcquisitionError) as failed_with_samples:
            vm_guest_parse_acquisition(
                packet(timed[:12] + ["FAIL 513 owner_changed cutoff=30000 diagnostic_ms=600"]) + prefix + sample,
                token, ivi_probe=True)
        self.assertEqual(failed_with_samples.exception.records[11], with_samples[11])
        self.assertEqual(failed_with_samples.exception.stage, "owner_changed")

        # The optional timing channel cannot masquerade as a core marker,
        # even when the timing line is duplicated, oversized or truncated.
        success = packet(timed)
        native_trace = b"fixture evidence"
        trace_prefix = ("WB_TRACE_" + token + " ").encode()
        native_failure = (packet(timed[:12] + [
            "FAIL 513 native_timeout native_marker=timeout_handler marker_offset=42 cutoff=30000 diagnostic_ms=600",
        ]) + trace_prefix + base64.b64encode(native_trace) + b"\n")
        with self.assertRaises(GuestAcquisitionError) as expected_native:
            vm_guest_parse_acquisition(native_failure, token, ivi_probe=True)
        for core_marker in (("WB_ACQ_" + token).encode(), trace_prefix.rstrip()):
            collision = sample.rstrip() + b" " + core_marker + b" junk"
            for preceding in (b"", prefix + sample, (prefix + sample) * 2):
                for body in (collision, b"x" * 4096 + collision):
                    for ending in (b"\n", b""):
                        with self.subTest(core_marker=core_marker, preceding=len(preceding),
                                          length=len(body), ending=ending):
                            sidecar = preceding + prefix + body + ending
                            self.assertEqual(
                                vm_guest_parse_acquisition(success + sidecar, token, ivi_probe=True),
                                (model, frame, timed_records),
                            )
                            with self.assertRaises(GuestAcquisitionError) as observed_native:
                                vm_guest_parse_acquisition(native_failure + sidecar, token, ivi_probe=True)
                            self.assertEqual(observed_native.exception.stage, "native_timeout")
                            self.assertEqual(observed_native.exception.trace, native_trace)
                            self.assertEqual(observed_native.exception.records, expected_native.exception.records)
            for ending in (b"\n", b""):
                for transcript in (success, native_failure):
                    with self.subTest(core_only=core_marker, ending=ending), self.assertRaises(ValueError):
                        vm_guest_parse_acquisition(transcript + b"prefix " + core_marker + b" junk" + ending,
                                                   token, ivi_probe=True)

        malformed = [timed[:12] + timed[13:], timed[:13] + timed[12:],
                     timed[:12] + [timed[13], timed[12]] + timed[14:],
                     [row.replace("timing_schema=1", "timing_schema=2") for row in timed],
                     [row.replace(" timing_schema=1", "") for row in timed],
                     [row + " timing_schema=1" if row.startswith("VERIFY_START ") else row for row in stages]]
        for name in phase_names:
            for invalid in ("VERIFY_UNKNOWN 500", name + " 499", name + " 30000",
                            name + " -1", name + " 100000", name + " 500 extra"):
                malformed.append([invalid if row == name + " 500" else row for row in timed])
        for rows in malformed:
            with self.subTest(timing_rows=rows[10:19]), self.assertRaises(ValueError):
                vm_guest_parse_acquisition(packet(rows), token, ivi_probe=True)
        # Partial timing is valid diagnostic evidence only when followed by
        # the original terminal failure; it cannot become a successful capture.
        for completed in range(len(phase_rows) + 1):
            for failure in ("native_timeout native_marker=timeout_handler marker_offset=42",
                            "owner_changed", "probe_output", "verification_deadline"):
                rows = timed[:12 + completed] + ["FAIL 501 " + failure + " cutoff=30000 diagnostic_ms=600"]
                with self.subTest(completed=completed, failure=failure), self.assertRaises(GuestAcquisitionError) as failed:
                    vm_guest_parse_acquisition(packet(rows), token, ivi_probe=True)
                self.assertEqual(failed.exception.stage, failure.split()[0])
                self.assertEqual([row["stage"] for row in failed.exception.records][12:-1], list(phase_names[:completed]))
        for bad_arm, bad_capture in ((arm.replace("pid=786", "pid=787"), capture),
                                     (arm.replace("arm=100010", "arm=100200"), capture),
                                     (arm.replace("deadline=129999", "deadline=130000"), capture),
                                     (arm, capture.replace("100500", "100029")),
                                     (arm, capture.replace("100500", "100099")),
                                     (arm, capture.replace("100500", "129999")),
                                     (arm, capture.replace("sequence=1", "sequence=0")),
                                     (arm, capture.replace("sequence=1", "sequence=2")),
                                     (arm, capture.replace("sequence=1", "sequence=99999999999999999999")),
                                     (arm, capture.replace("format=537004168", "format=1")),
                                     (arm, capture.replace("size=5529600", "size=5529599"))):
            rows = [bad_arm if row == arm else bad_capture if row == capture else row for row in stages]
            with self.subTest(arm=bad_arm, capture=bad_capture), self.assertRaises(ValueError):
                vm_guest_parse_acquisition(packet(rows), token, ivi_probe=True)
        for change in ("driving true", "dimmed true", "calling true", "enabled false", "visible false"):
            field, value = change.split(); current = "true" if field in ("enabled", "visible") else "false"
            rows = [row.replace(field + " " + current, change) if row.startswith("MODEL ") else row for row in stages]
            with self.subTest(change=change), self.assertRaises(ValueError):
                vm_guest_parse_acquisition(packet(rows), token, ivi_probe=True)
        for invalid in (baseline.replace("ack_sha=" + ack_sha, "ack_sha=" + "0" * 64),
                        baseline.replace("time=100020", "time=100031"),
                        baseline.replace("size=16", "size=99999999")):
            rows = [invalid if row == baseline else row for row in stages]
            with self.assertRaises(ValueError): vm_guest_parse_acquisition(packet(rows), token, ivi_probe=True)
        for old, new in (("OBSERVE 100 monotonic=100100", "OBSERVE 100 monotonic=100099"),
                         ("observation_start=100100", "observation_start=100101")):
            rows = [row.replace(old, new) for row in stages]
            with self.assertRaises(ValueError): vm_guest_parse_acquisition(packet(rows), token, ivi_probe=True)
        # A receipt may arrive after the former 15-second limit while still
        # leaving the remaining bounded verification work below 30 seconds.
        late = [row.replace("RECEIPT_BOUND 500 capture=100500", "RECEIPT_BOUND 29998 capture=129998")
                .replace("VISIBILITY 500", "VISIBILITY 29999")
                .replace("PROBE_CAPTURE 600 capture=100500", "PROBE_CAPTURE 29999 capture=129998")
                .replace("VERIFY_DONE 600", "VERIFY_DONE 29999").replace("OK 600", "OK 29999") for row in stages]
        vm_guest_parse_acquisition(packet(late), token, ivi_probe=True)
        timed_late = [row + " timing_schema=1" if row.startswith(("VERIFY_START ", "VERIFY_DONE ")) else row
                      for row in late[:12] + [name + " 29999" for name in phase_names] + late[12:]]
        vm_guest_parse_acquisition(packet(timed_late), token, ivi_probe=True)
        # Verification must begin before the producer deadline even though later
        # read-only checks finish before the host verification deadline.
        ordered = [row.replace("NATIVE 300 ", "NATIVE 29999 ")
                   .replace("MODEL 300 ", "MODEL 29999 ")
                   .replace("VERIFY_START 300 ", "VERIFY_START 29999 ")
                   .replace("RECEIPT_BOUND 500 ", "RECEIPT_BOUND 29999 ")
                   .replace("VISIBILITY 500 ", "VISIBILITY 29999 ")
                   .replace("PROBE_CAPTURE 600 ", "PROBE_CAPTURE 29999 ")
                   .replace("VERIFY_DONE 600 ", "VERIFY_DONE 29999 ")
                   .replace("OK 600", "OK 29999") for row in stages]
        vm_guest_parse_acquisition(packet(ordered), token, ivi_probe=True)
        with self.assertRaises(ValueError):
            vm_guest_parse_acquisition(packet([row.replace("VERIFY_START 29999 ", "VERIFY_START 30000 ") for row in ordered]), token, ivi_probe=True)
        with self.assertRaises(ValueError):
            vm_guest_parse_acquisition(packet([row.replace("MODEL 29999 ", "MODEL 30000 ") for row in ordered]), token, ivi_probe=True)
        baseline_failure = packet([stages[0], arm,
                                   "FAIL 10169 baseline_deadline cutoff=30000 diagnostic_ms=10169"])
        with self.assertRaises(GuestAcquisitionError) as observed_failure:
            vm_guest_parse_acquisition(baseline_failure, token, ivi_probe=True)
        self.assertEqual(observed_failure.exception.stage, "baseline_deadline")
        self.assertIn("cutoff=30000", observed_failure.exception.records[-1]["detail"])
        with self.assertRaises(ValueError):
            vm_guest_parse_acquisition(
                packet([stages[0], arm, "FAIL 10169 baseline_deadline cutoff=10000 diagnostic_ms=10169"]),
                token, ivi_probe=True)
        for before, after in (("capture=129998", "capture=129999"), ("capture=129998", "capture=130000"), ("VERIFY_DONE 29999", "VERIFY_DONE 30000"),
                              ("OK 29999", "OK 30000"), ("OK 29999", "OK 30001"), ("RECEIPT_BOUND 29998", "RECEIPT_BOUND 30000")):
            with self.subTest(boundary=before), self.assertRaises(ValueError):
                vm_guest_parse_acquisition(packet([row.replace(before, after) for row in late]), token, ivi_probe=True)
        command = vm_guest_acquisition_command(token, ivi_probe=True)
        self.assertEqual(command.count("com.lge.avn.appmanager.appbase.show_window_fg"), 1)
        self.assertEqual(command.count("/ivi-fg-standby1000"), 1)
        self.assertEqual(command.count("/usr/libexec/weston-screenshooter"), 0)
        self.assertEqual(command.count('> "$d/request.tmp"'), 1)
        self.assertLess(command.index('emit "PROBE_ARM'), command.index('emit "REASON11_SENT'))
        self.assertLess(command.index('emit "REASON11_ACK'), command.index('> "$d/go.tmp"'))
        self.assertLess(command.index('emit "PROBE_ARM'), command.index('emit "PROBE_CAPTURE'))
        self.assertNotIn("notify_button", command)
        self.assertNotIn("baseline.raw", vm_guest_ivi_frame_export_command(token, ":1.4", 786, 456, "b" * 64))
        self.assertNotIn("baseline.raw", vm_guest_probe_failure_command(token, 786, 456, 100000, 129999))
        self.assertIn('$2 ""!=p ""', vm_guest_probe_failure_command(token, 786, 456, 100000, 129999))
        self.assertEqual(subprocess.run(["/bin/bash", "-n"], input=command, text=True, capture_output=True).returncode, 0)
        bridge = GuestShell.__new__(GuestShell)
        observed = {"pid": 786, "starttime": 456, "monotonic_ms": 100500, "sequence": 1, "surface_identity": "0x10", "output_identity": "0x20", "source": {"format": 537036936}, "output": {"width": 1920, "height": 720, "format": 537004168, "sha256": digest}, "baseline": {"time": 100020, "size": 16, "format": 537036936, "buffer": "0x30", "selected_buffer": "0x30", "observations": 1, "sha256": base_sha, "ack_sha": ack_sha, "observation_start": 100100}, "limitation": "unqualified"}
        with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
             mock.patch.object(bridge, "_run", side_effect=[packet(stages), b"export"]), \
             mock.patch("vm_workbench.guest_shell.vm_guest_parse_ivi_frame", return_value=(observed, b"\0" * 16, image)):
            returned_model, _, receipt, source, output, _ = bridge.foreground_and_probe()
        self.assertEqual((source, output), (b"\0" * 16, image))
        self.assertEqual(receipt["acquisition"]["status"], "pixels require independent inspection")
        self.assertEqual(receipt["acquisition"]["frame_source"], "probe-output")
        self.assertEqual((receipt["acquisition"]["capture_deadline_elapsed_ms"], receipt["acquisition"]["verification_deadline_elapsed_ms"], receipt["acquisition"]["verification_completed_elapsed_ms"]), (30000, 30000, 600))
        self.assertEqual(returned_model["acquisition_timing"]["verification_completed_elapsed_ms"], 600)
        self.assertNotIn("confirm_verified", receipt)
        with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
             mock.patch.object(bridge, "_run", side_effect=[packet(stages), b"export"]), \
             mock.patch("vm_workbench.guest_shell.vm_guest_parse_ivi_frame", return_value=(observed, b"source", image[:-1] + b"x")), \
             mock.patch("vm_workbench.guest_shell.vm_guest_probe_output_png") as convert:
            with self.assertRaises(ValueError): bridge.foreground_and_probe()
            convert.assert_not_called()
        for sequence in ("2", "99999999999999999999"):
            invalid = [row.replace("sequence=1", "sequence=" + sequence) if row == capture else row for row in stages]
            with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
                 mock.patch.object(bridge, "_run", return_value=packet(invalid)) as run, \
                 mock.patch("vm_workbench.guest_shell.vm_guest_probe_output_png") as convert:
                with self.assertRaises(ValueError): bridge.foreground_and_probe()
                self.assertEqual(run.call_count, 1)
                convert.assert_not_called()
        with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
             mock.patch.object(bridge, "_run", return_value=packet([row.replace("OK 29999", "OK 30000") for row in late])) as run, \
             mock.patch("vm_workbench.guest_shell.vm_guest_probe_output_png") as convert:
            with self.assertRaises(ValueError): bridge.foreground_and_probe()
            self.assertEqual(run.call_count, 1)
            convert.assert_not_called()
        probe_receipt = (token + " OK 786 456 1 100500 0x10 0x20 2 2 1 16 1920 720 1 5529600 0 0 1920 720 0 0\n").encode()
        evidence = (f"WB_FAIL_{token} BEGIN\nWB_FAIL_{token} ITEM receipt {len(probe_receipt)}\nWB_FAIL_{token} RECEIPT ".encode() + base64.b64encode(probe_receipt) + f"\nWB_FAIL_{token} END\n".encode())
        failure_packet = packet(stages[:10] + ["FAIL 500 probe_deadline cutoff=30000 diagnostic_ms=600"])
        for bad_arm in (arm.replace("pid=786", "pid=787"), arm.replace("arm=100010", "arm=100200"),
                        arm.replace("deadline=129999", "deadline=130000")):
            bad_packet = packet([bad_arm if row == arm else row for row in stages[:10]] + ["FAIL 500 probe_deadline cutoff=10000 diagnostic_ms=600"])
            with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
                 mock.patch.object(bridge, "_run", return_value=bad_packet) as bad_run:
                with self.assertRaises(ValueError): bridge.foreground_and_probe()
                self.assertEqual(bad_run.call_count, 1)
        def failure_evidence(payload):
            return (f"WB_FAIL_{token} BEGIN\nWB_FAIL_{token} ITEM receipt {len(payload)}\nWB_FAIL_{token} RECEIPT ".encode() + base64.b64encode(payload) + f"\nWB_FAIL_{token} END\n".encode())
        for invalid in (probe_receipt.replace(b"100500", b"100309"), probe_receipt.replace(b"100500", b"129999"),
                        probe_receipt.replace(token.encode(), b"b" * 32, 1),
                        probe_receipt.replace(b" 786 456 ", b" 787 456 ", 1),
                        probe_receipt.replace(b" 786 456 ", b" 786 457 ", 1)):
            with self.assertRaises(ValueError): vm_guest_parse_probe_failure(failure_evidence(invalid), token, 786, 456, 100310, 129999)
        fail_receipt = (token + " FAIL 786 456 0 0 (nil) (nil) 0 0 0 0 0 0 0 0 1 1 24 22 10050 1\n").encode()
        failed_evidence = failure_evidence(fail_receipt)
        failed_diagnostic = vm_guest_parse_probe_failure(failed_evidence, token, 786, 456, 100310, 129999)
        self.assertEqual((failed_diagnostic["qualification"], failed_diagnostic["receipt_status"]), ("UNQUALIFIED", "FAIL"))
        typed_probe_failure = {
            "schema": 1, "code": 1, "name": "timeout", "observation_enabled": True,
            "frame_callbacks": 24, "unchanged_comparisons": 22, "elapsed_ms": 10050,
        }
        self.assertEqual(failed_diagnostic["probe_failure"], typed_probe_failure)
        inventory_prefix = f"WB_FAIL_{token} ITEM ".encode()
        receipt_prefix = f"WB_FAIL_{token} RECEIPT ".encode()
        end_record = f"WB_FAIL_{token} END\n".encode()
        canonical_inventory = (
            f"WB_FAIL_{token} BEGIN\n".encode() +
            inventory_prefix + f"receipt {len(fail_receipt)}\n".encode() +
            inventory_prefix + b"source.raw 16\n" +
            inventory_prefix + b"output.raw 32\n" +
            receipt_prefix + base64.b64encode(fail_receipt) + b"\n" + end_record
        )
        self.assertEqual(
            vm_guest_parse_probe_failure(canonical_inventory, token, 786, 456, 100310, 129999)["probe_failure"],
            typed_probe_failure,
        )
        for invalid in (fail_receipt.replace(b"10050 1", b"10050 2"),
                        fail_receipt.replace(b"1 1 24 22 10050 1", b"11 1 24 22 10050 1"),
                        fail_receipt.replace(b"1 1 24 22 10050 1", b"1 2 24 22 10050 1"),
                        fail_receipt.replace(b"1 1 24 22 10050 1", b"1 1 24 25 10050 1")):
            with self.assertRaises(ValueError):
                vm_guest_parse_probe_failure(failure_evidence(invalid), token, 786, 456, 100310, 129999)
        duplicate_receipt = failed_evidence.replace(
            end_record, receipt_prefix + base64.b64encode(fail_receipt) + b"\n" + end_record, 1)
        inventory_after_receipt = canonical_inventory.replace(
            inventory_prefix + b"output.raw 32\n" + receipt_prefix,
            receipt_prefix + base64.b64encode(fail_receipt) + b"\n" +
            inventory_prefix + b"output.raw 32\n" + end_record, 1)
        for invalid in (b"unframed\n" + failed_evidence, failed_evidence + b"unframed\n",
                        failed_evidence.replace(end_record, b"", 1),
                        failed_evidence.rstrip(b"\n"),
                        failed_evidence.replace(b"\n", b"\r\n"),
                        failed_evidence.replace(b"BEGIN\n", b"BEGIN\n\n", 1),
                        failed_evidence.replace(b" RECEIPT ", b"  RECEIPT ", 1),
                        duplicate_receipt,
                        canonical_inventory.replace(
                            inventory_prefix + b"source.raw 16\n" + inventory_prefix + b"output.raw 32\n",
                            inventory_prefix + b"output.raw 32\n" + inventory_prefix + b"source.raw 16\n", 1),
                        canonical_inventory.replace(
                            inventory_prefix + b"source.raw 16\n", inventory_prefix + b"source.raw 016\n", 1),
                        canonical_inventory.replace(
                            inventory_prefix + b"source.raw 16\n",
                            inventory_prefix + b"source.raw 16\n" + inventory_prefix + b"source.raw 16\n", 1),
                        canonical_inventory.replace(
                            inventory_prefix + f"receipt {len(fail_receipt)}\n".encode(), b"", 1),
                        inventory_after_receipt,
                        canonical_inventory.replace(inventory_prefix, b"WB_FAIL_" + b"b" * 32 + b" ITEM ", 1),
                        failed_evidence + b"x" * 4096,
                        failure_evidence(fail_receipt.replace(b" FAIL ", b"  FAIL ", 1)),
                        failure_evidence(fail_receipt.replace(b" 786 456 ", b" 787 456 ", 1)),
                        failure_evidence(fail_receipt.replace(b" 786 456 ", b" 786 457 ", 1))):
            with self.assertRaises(ValueError):
                vm_guest_parse_probe_failure(invalid, token, 786, 456, 100310, 129999)
        for invalid_pid, invalid_start in ((True, 456), (786, False), (0, 456), (786, 0),
                                            (2147483648, 456), (786, -1)):
            with self.assertRaises(ValueError):
                vm_guest_parse_probe_failure(failed_evidence, token, invalid_pid, invalid_start, 100310, 129999)
        for invalid_arm, invalid_deadline in ((0, 129999), (100310, True), (100310, 100310),
                                               (129999, 129998), (100310, 0)):
            with self.assertRaises(ValueError):
                vm_guest_parse_probe_failure(failed_evidence, token, 786, 456, invalid_arm, invalid_deadline)
        with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
             mock.patch.object(bridge, "_run", side_effect=[failure_packet, evidence]) as run:
            with self.assertRaises(GuestAcquisitionError) as caught: bridge.foreground_and_probe()
        self.assertEqual(caught.exception.diagnostic["receipt"], probe_receipt.decode())
        self.assertEqual(caught.exception.diagnostic["probe_status"], "unqualified")
        self.assertEqual(caught.exception.diagnostic["qualification"], "UNQUALIFIED")
        self.assertEqual(run.call_count, 2)
        with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
             mock.patch.object(bridge, "_run", side_effect=[failure_packet, failed_evidence]) as run, \
             mock.patch.object(bridge, "publish_input") as admit_input, \
             mock.patch.object(bridge, "publish_simulator") as admit_simulator, \
             mock.patch("vm_workbench.guest_shell.vm_guest_probe_output_png") as convert, \
             mock.patch("vm_workbench.guest_shell.vm_guest_ivi_frame_export_command") as export, \
             mock.patch("vm_workbench.guest_shell.vm_guest_parse_ivi_frame") as parse_frame, \
             tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(GuestAcquisitionError) as typed_failure:
                bridge.foreground_and_probe()
            self.assertEqual(typed_failure.exception.diagnostic["failure"], "probe_deadline")
            self.assertEqual(typed_failure.exception.diagnostic["probe_failure"], typed_probe_failure)
            self.assertEqual(run.call_count, 2)
            convert.assert_not_called()
            export.assert_not_called()
            parse_frame.assert_not_called()
            admit_input.assert_not_called()
            admit_simulator.assert_not_called()
            path = vm_workbench_write_acquisition_failure(Path(directory), typed_failure.exception)
            persisted = json.loads(path.read_text())
            self.assertEqual(persisted["failure"], "probe_deadline")
            self.assertEqual(persisted["probe_failure"], typed_probe_failure)
            self.assertNotIn("source", persisted)
            self.assertNotIn("output", persisted)
            self.assertNotIn("frame", persisted)
        with mock.patch("vm_workbench.guest_shell.uuid.uuid4", return_value=type("U", (), {"hex": token})()), \
             mock.patch.object(bridge, "_run", side_effect=[failure_packet, b"unframed\n"]) as run, \
             mock.patch.object(bridge, "publish_input") as admit_input, \
             mock.patch.object(bridge, "publish_simulator") as admit_simulator, \
             mock.patch("vm_workbench.guest_shell.vm_guest_probe_output_png") as convert, \
             mock.patch("vm_workbench.guest_shell.vm_guest_ivi_frame_export_command") as export, \
             mock.patch("vm_workbench.guest_shell.vm_guest_parse_ivi_frame") as parse_frame:
            with self.assertRaises(GuestAcquisitionError) as malformed_failure:
                bridge.foreground_and_probe()
            self.assertEqual(malformed_failure.exception.stage, "probe_deadline")
            self.assertEqual(malformed_failure.exception.diagnostic["failure"], "probe_deadline")
            self.assertEqual(malformed_failure.exception.diagnostic["inventory_status"], "unavailable_or_invalid")
            self.assertNotIn("probe_failure", malformed_failure.exception.diagnostic)
            self.assertEqual(run.call_count, 2)
            convert.assert_not_called()
            export.assert_not_called()
            parse_frame.assert_not_called()
            admit_input.assert_not_called()
            admit_simulator.assert_not_called()
        with mock.patch.object(bridge, "_run", side_effect=TimeoutError("console")):
            with self.assertRaises(TimeoutError) as transport: bridge.foreground_and_probe()
        self.assertEqual(transport.exception.diagnostic["probe_status"], "unknown")

    def test_acquisition_process_start_requires_one_matching_record(self):
        """The generated parser accepts Linux comm delimiters and rejects wrong start evidence."""
        command = vm_guest_acquisition_command("d" * 32, ivi_probe=True)
        parser = command[command.index("process_start() {"):command.index("reason_failure_snapshot() {")]
        phases = ("VERIFY_IDENTITY", "VERIFY_OUTPUT", "VERIFY_IDENTITY_RECHECK",
                  "VERIFY_LOG_SCAN_1", "VERIFY_IDENTITY_FINAL", "VERIFY_LOG_SCAN_2")
        verification = command[command.index('emit "RECEIPT_BOUND'):command.index('emit "VISIBILITY', command.index('emit "RECEIPT_BOUND'))]
        self.assertEqual(re.findall(r'emit "(VERIFY_[A-Z0-9_]+) ', verification), list(phases))
        self.assertEqual(verification.count('current_start=$(process_start "$pid")'), 3)
        self.assertEqual(verification.count("boundary || fail log_changed\nscan_result || fail log_parse"), 2)
        # Removing the observation calls and classifiers, then restoring the
        # pre-0.4.1 fallback and IVI screenshot-only guard leaves the complete
        # 0.4.7 scanner policy, error precedence and deadlines under test.
        checks = re.sub(r"(?ms)^verify_phase=\nverify_samples=\nverify_mark\(\) \{.*?^\}\n\n",
                        "", command, count=1)
        checks = re.sub(r"(?m)^ *(?:verify_phase=[a-z_0-9]+; verify_mark begin|verify_mark [a-z_]+|verify_emit)\n",
                        "", checks)
        checks = re.sub(
            r"(?ms)^[^\n]*REASON11_SNAPSHOT_CLASSIFY_BEGIN\n.*?^[^\n]*REASON11_SNAPSHOT_CLASSIFY_END\n",
            "", checks, count=1)
        checks = re.sub(
            r"(?ms)^[^\n]*REASON11_COMPLETE_PREFIX_BEGIN\n.*?^[^\n]*REASON11_COMPLETE_PREFIX_END\n",
            "", checks, count=1)
        checks = REASON11_PHASE_BLOCK.sub("", checks)
        checks = checks.replace("|| reason_last=invalid", "|| reason_last=0", 1)
        checks = checks.replace(IVI_VERIFY_GATE, LEGACY_IVI_SCREENSHOT_BUDGET + IVI_VERIFY_GATE, 1)
        checks = normalize_generated_dbus_timeouts(checks)
        self.assertEqual(hashlib.sha256(checks.encode()).hexdigest(),
                         "af32d875d8513bdfdc2ed435d425621f0e228da5652d6e93d67175b00a999d52")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "procstat"
            suffix = " (" + "kernel ) writer (name)" + ") S " + "0 " * 18
            valid = "786" + suffix + "12345678901234567890 0\n"
            script = ('BB=fixture\nfixture() { "$@"; }\n' +
                      parser.replace('"/proc/$proc_pid/stat"', shlex.quote(str(path))) + "\nprocess_start 786\n")
            for record, expected in ((valid, "12345678901234567890"),
                                     (valid.replace("786 ", "787 ", 1), None),
                                     (valid + valid, None), ("786 (worker) S 0\n", None),
                                     ("786" + suffix + "0 0\n", None),
                                     ("786" + suffix + "456x 0\n", None)):
                with self.subTest(record=record):
                    path.write_text(record)
                    run = subprocess.run([PIPEFAIL_SHELL], input=script, text=True,
                                         capture_output=True, timeout=5)
                    self.assertEqual((run.returncode, run.stdout.strip()),
                                     (0, expected) if expected else (1, ""))

    def test_acquisition_reason11_native_phase_window(self):
        """Execute the generated failure classifier over exact byte intervals."""
        token = "f" * 32
        command = vm_guest_acquisition_command(token, ivi_probe=True)
        begin = command.index("reason_phase_fence() {")
        end = command.index("# REASON11_PHASE_HELPERS_END", begin)
        helper = command[begin:end]
        entry = DLT_PREFIX + b"AppStandbyClockEngine::inter_show_window_fg appid =  10 reason =  11 plane =  1 avmode =  -1 command =  0 temporal =  false]\n"
        show = DLT_PREFIX + b"QMLController::showScreen(QString) /app/share/AppStandbyClock/qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml]\n"
        draw = DLT_PREFIX + b"SCREEN_STATE: START DRAW]\n"
        model = DLT_PREFIX + CONFIRM + b"]\n"
        finish = DLT_PREFIX + b"SCREEN_STATE: DRAW FINISHED]\n"
        returned = DLT_PREFIX + b"AppStandbyClockEngine::inter_show_window_fg return plane =  1]\n"
        records = (entry, show, draw, model, finish, returned)
        labels = ("no_ordered_chain", "handler_entry", "confirm_show", "draw_start",
                  "valid_model", "draw_finish", "native_return")
        with tempfile.TemporaryDirectory() as temp:
            scan = Path(temp) / "scan"
            shell = (r'''
BB=bb
bb() {
  [ "$1:$3" = timeout:bb ] || exit 2
  shift 3
  if [ "$1" = stat ]; then
    [ "$PHASE_STAT_RC" = 0 ] || return "$PHASE_STAT_RC"
    printf '%s\n' "$PHASE_STAT"
  else
    command "$@"
  fi
}
base=100
base_id=1:2
log=$SCAN
scan=$SCAN
reason_size=$((base+BYTES))
reason_send_fence=$((base+LOWER))
reason_fail_fence=$((base+UPPER))
partial=$PARTIAL
reason_last=$COMPLETE
owner=:1.4
reason_owner=$OWNER
pid=786
reason_pid=786
reason_start=456
reason_current_start=456
proc_start=456
''' + helper)

            def classify(data, lower=0, upper=None, *, partial=0, complete=1, owner=":1.4"):
                scan.write_bytes(data)
                result = subprocess.run(
                    ["/bin/bash"], input=shell + "\nreason_native_phase || printf 'unavailable\\n'\n",
                    env=dict(os.environ, SCAN=str(scan), BYTES=str(len(data)), LOWER=str(lower),
                             UPPER=str(len(data) if upper is None else upper), PARTIAL=str(partial),
                             COMPLETE=str(complete), OWNER=owner),
                    text=True, capture_output=True, timeout=5,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout.strip()

            for index, label in enumerate(labels):
                with self.subTest(phase=label):
                    self.assertEqual(classify(b"".join(records[:index])), label)
            whole = b"".join(records)
            for name, data, lower, upper, partial, complete, owner, expected in (
                    ("isolated", draw, 0, None, 0, 1, ":1.4", "no_ordered_chain"),
                    ("before-send", whole, len(entry), None, 0, 1, ":1.4", "no_ordered_chain"),
                    ("crossing-send", whole, 4, None, 0, 1, ":1.4", "no_ordered_chain"),
                    ("baseline-partial", whole, 0, None, 1, 1, ":1.4", "no_ordered_chain"),
                    ("crossing-failure", whole, 0, len(entry + show) - 1, 0, 1, ":1.4", "handler_entry"),
                    ("after-failure", whole, 0, len(entry + show), 0, 1, ":1.4", "confirm_show"),
                    ("incomplete", whole[:-1], 0, None, 0, 0, ":1.4", "draw_finish"),
                    ("crlf", whole.replace(b"\n", b"\r\n"), 0, None, 0, 1, ":1.4", "native_return"),
                    ("changed-owner", whole, 0, None, 0, 1, ":1.9", "unavailable"),
                    ("reversed-fences", whole, 2, 1, 0, 1, ":1.4", "unavailable"),
                    ("truncation-after-failure", whole, 0, len(whole) + 1, 0, 1, ":1.4", "unavailable"),
                    ("duplicate-entry", entry + whole, 0, None, 0, 1, ":1.4", "unavailable"),
                    ("out-of-order", entry + draw, 0, None, 0, 1, ":1.4", "unavailable"),
                    ("wrong-confirm", entry + show.replace(b"_Profile.qml", b".qml"), 0, None, 0, 1, ":1.4", "unavailable"),
                    ("restricted-model", whole.replace(b"enabled true", b"enabled false"), 0, None, 0, 1, ":1.4", "unavailable"),
                    ("wrong-return", whole.replace(b"return plane =  1", b"return plane =  10"), 0, None, 0, 1, ":1.4", "unavailable"),
                    ("wrong-tuple", whole.replace(b"temporal =  false", b"temporal =  falsely"), 0, None, 0, 1, ":1.4", "unavailable"),
            ):
                with self.subTest(case=name):
                    self.assertEqual(classify(data, lower, upper, partial=partial, complete=complete,
                                              owner=owner), expected)

            for stat, rc, expected in (("1:2:100", 0, "100"), ("1:3:100", 0, "unavailable"),
                                       ("1:2:99", 0, "unavailable"), ("1:2:262245", 0, "unavailable"),
                                       ("1:2:bad", 0, "unavailable"), ("1:2:100", 124, "unavailable")):
                with self.subTest(stat=stat, rc=rc):
                    result = subprocess.run(
                        ["/bin/bash"], input=shell + "\nreason_phase_fence || printf 'unavailable\\n'\n",
                        env=dict(os.environ, SCAN=str(scan), PHASE_STAT=stat, PHASE_STAT_RC=str(rc)),
                        text=True, capture_output=True, timeout=5,
                    )
                    self.assertEqual((result.returncode, result.stdout.strip()), (0, expected), result.stderr)

    def test_acquisition_reason11_native_phase_protocol(self):
        """Only a dedicated, complete IVI failure record contributes a phase."""
        token = "6" * 32
        core = f"WB_ACQ_{token} "
        header = "".join(core + row + "\n" for row in (
            "BEGIN owner=:1.4 pid=786",
            "PROBE_ARM 10 pid=786 start=456 epoch=100000 arm=100010 deadline=129999",
            "BASELINE 20 time=100020 size=16 format=537036936 buffer=0x30 surface=0x10 output=0x20 sha256=" +
            "a" * 64 + " ack_sha=" + "b" * 64,
            "REASON11_SENT 30 monotonic=100030",
        ))
        snapshot_marker = f"WB_REASON11_{token} "
        snapshot = snapshot_marker + "epoch=100000 owner=:1.4 pid=786 start=456 current_owner=:1.4 current_pid=786 current_start=456 snapshot=ok\n"
        phase_marker = f"WB_REASON11_PHASE_{token} "
        phase = phase_marker + "phase=native_return\n"
        failure = core + "FAIL 4000 reason11 cutoff=30000 diagnostic_ms=4200\n"
        admitted_prefix = f"WB_REASON11_PREFIX_{token} evidence=complete_prefix handler_entry=observed draw_progress=observed records=6\n"
        trace = f"WB_TRACE_{token} " + base64.b64encode(b"valid fixture trace\n").decode() + "\n"

        def diagnostic(body, terminal=failure):
            with self.assertRaises(GuestAcquisitionError) as caught:
                vm_guest_parse_acquisition((header + body + terminal).encode(), token, ivi_probe=True)
            self.assertEqual(caught.exception.stage, terminal.split()[3])
            return caught.exception

        self.assertEqual(diagnostic(snapshot + phase + trace).reason11_diagnostic["native_phase"], "native_return")
        incomplete = snapshot.replace("snapshot=ok", "snapshot=newline_check_failed")
        accepted = diagnostic(incomplete + admitted_prefix + phase)
        self.assertEqual(accepted.reason11_diagnostic["native_phase"], "native_return")
        self.assertEqual(accepted.trace, b"")
        self.assertFalse(hasattr(diagnostic(phase), "reason11_diagnostic"))
        self.assertFalse(hasattr(diagnostic(snapshot + phase, failure.replace(" reason11 ", " deadline ")),
                                 "reason11_diagnostic"))
        self.assertFalse(hasattr(diagnostic(snapshot.replace(snapshot_marker, phase_marker, 1) +
                                           phase.replace(phase_marker, snapshot_marker, 1)), "reason11_diagnostic"))
        self.assertNotIn("native_phase", diagnostic(snapshot).reason11_diagnostic)
        for body in (
                snapshot + phase * 2, snapshot + "prefix " + phase, snapshot + phase.replace("native_return", "unknown"),
                snapshot + phase.replace("native_return", "x" * 150),
                snapshot + phase.replace("native_return", "native_return " + core + "junk"),
                snapshot.replace("current_start=456", "current_start=457") + phase,
                snapshot.replace("start=456", "start=457") + phase,
                snapshot.replace("epoch=100000", "epoch=100001") + phase,
                snapshot + phase.rstrip("\n") + "\r",
                snapshot + "not a separate line\r" + phase,
                incomplete + phase, phase + snapshot, snapshot + failure + phase,
                snapshot + failure + phase.rstrip("\n") + " " + core + "junk",
        ):
            with self.subTest(body=body[-100:]):
                terminal = "" if failure in body else failure
                with self.assertRaises(GuestAcquisitionError) as caught:
                    vm_guest_parse_acquisition((header + body + terminal).encode(), token, ivi_probe=True)
                self.assertEqual(caught.exception.stage, "reason11")
                self.assertEqual(caught.exception.reason11_diagnostic["native_phase"], "unavailable")

    def test_acquisition_real_shell_shared_clock_and_log_gates(self):
        """Run the generated guest transaction against fake local system edges."""
        token = "d" * 32
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            dlt, clock = d / "dlt", d / "uptime"
            record = DLT_PREFIX + CONFIRM + b"]\n"
            entry = DLT_PREFIX + b"[2] [ int AppStandbyClockEngine::inter_show_window_fg(int, int, int, int, int, bool) ][ 1871 ]  appid =  10  reason =  11  plane =  1  avmode =  -1  command =  0  temporal =  false]\n"
            show = DLT_PREFIX + b'[2] [ bool QMLController::showScreen(QString) ][ 48 ] "/app/share/AppStandbyClock/qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml"]\n'
            draw = DLT_PREFIX + b"[3] SCREEN_STATE: START DRAW]\n"
            hidden = DLT_PREFIX + b"VM_OBSERVE_CONFIRM visibleChanged false]\n"
            disabled = DLT_PREFIX + b"VM_OBSERVE_CONFIRM enabledChanged false 1]\n"
            driving = DLT_PREFIX + b"[3] drivingRestriction:true,AppID: 10]\n"
            visible = DLT_PREFIX + b"VM_OBSERVE_CONFIRM visibleChanged true]\n"
            done = DLT_PREFIX + b"[3] SCREEN_STATE: DRAW FINISHED]\n"
            native_return = DLT_PREFIX + b"[2] [ int AppStandbyClockEngine::inter_show_window_fg(int, int, int, int, int, bool) ][ 3011 ] return plane =  1]\n"
            sequence = entry + show + draw + record + hidden + done + native_return
            (d / "record").write_bytes(sequence)
            (d / "reason-handler").write_bytes(entry)
            (d / "reason-draw").write_bytes(draw)
            (d / "reason-handler-partial").write_bytes(entry[:-1])
            (d / "reason-handler-wrong-context").write_bytes(entry.replace(b"MANG STAN STAN", b"MANG OTHER CTXT", 1))
            (d / "reason-handler-malformed").write_bytes(
                DLT_PREFIX + b"[2] [ int AppStandbyClockEngine::inter_show_window_fg(int, int, int, int, int, bool) ][ 1871 ]  appid =  10]\n")
            (d / "session").write_text("fixture\n")
            (d / "procstat").write_text("786 (App Standby) S " + "0 " * 18 + "456 0\n")
            (d / "probe").mkdir(mode=0o700)
            bb = d / "busybox"
            bb.write_text('#!/usr/bin/python3\nimport os,sys,pathlib,base64,textwrap\na=sys.argv[1:]; d=pathlib.Path(os.environ["FIXTURE_DIR"])\n'
                'if a[0]=="stat":\n'
                ' mode=os.environ["MODE"]; fmt=a[2]\n'
                ' for path in a[3:]:\n'
                '  p=pathlib.Path(path); s=p.stat()\n'
                '  if p==d/"dlt" and mode=="probe_slow_boundary" and (d/"probe"/"go").exists(): (d/"uptime").write_text("130.0 0\\n")\n'
                '  if p.name=="receipt" and mode in ("probe_late_receipt", "probe_late_capture", "probe_verify_inside", "probe_verify_expired", "probe_hash_hidden", "probe_receipt_hidden", "probe_start_hash", "probe_owner_hash", "probe_bad_receipt", "probe_bad_output", "probe_start_flip", "probe_owner_flip"):\n'
                '   (d/"uptime").write_text(("129.99" if mode=="probe_verify_inside" else "130.0" if mode=="probe_verify_expired" else "125.0" if mode=="probe_late_receipt" else "110.5")+" 0\\n")\n'
                '  if fmt=="%u:%a" and p.is_dir() and mode in ("probe_refresh", "probe_refresh_expired"): (d/"uptime").write_text(("101.32" if mode=="probe_refresh" else "110.0")+" 0\\n")\n'
                '  perm="700" if p.is_dir() else oct(s.st_mode & 0o777)[2:] if p.name=="baseline.raw" else "600"\n'
                '  row=fmt\n'
                '  for key,value in {"%d":s.st_dev,"%i":s.st_ino,"%s":s.st_size,"%u":0,"%a":perm,"%h":s.st_nlink}.items(): row=row.replace(key,str(value))\n'
                '  print(row)\n'
                ' sys.exit(0)\n'
                'if a[0]=="mv" and a[-1].endswith("/request"):\n'
                ' src=pathlib.Path(a[-2]); dest=pathlib.Path(a[-1]); src.rename(dest); parts=dest.read_text().split(); now=round(float((d/"uptime").read_text().split()[0])*1000); mode=os.environ["MODE"]; raw=dest.parent/"baseline.raw"; raw.write_bytes(b"baseline-content"); raw.chmod(0o600);\n'
                ' if mode=="probe_baseline_mode": raw.chmod(0o644)\n'
                ' if mode=="probe_baseline_symlink":\n  raw.unlink(); (d/"baseline-target").write_bytes(b"baseline-content"); raw.symlink_to(d/"baseline-target")\n'
                ' if mode=="probe_baseline_late": now=int(parts[4])\n'
                ' if mode!="probe_baseline_missing": (dest.parent/"baseline.meta").write_text(" ".join(parts[:3]+[str(now),"16","537036936","0x"+"1"*17 if mode=="probe_baseline_malformed" else "0x30","0x10","0x20"])+"\\n")\n'
                ' sys.exit(0)\n'
                'if a[0]=="ln" and a[-1].endswith("/go"):\n'
                ' src=pathlib.Path(a[-2]); dest=pathlib.Path(a[-1]); os.link(src,dest); parts=(dest.parent/"request").read_text().split(); base=(dest.parent/"baseline.meta").read_text().split(); go=dest.read_text().split(); mode=os.environ["MODE"];\n'
                ' if mode!="probe_timeout":\n'
                '  captured=(129999 if mode=="probe_late_capture" else 124998 if mode in ("probe_late_receipt","probe_verify_inside","probe_verify_expired") else round(float((d/"uptime").read_text().split()[0])*1000)-(1 if mode=="probe_stale" else 0)); line=" ".join(parts[:3]+["1",str(captured),"0x10","0x20","2","2","537036936","16","1920","720","537004168","5529600","0","0","1920","720","0","0"]+[base[3],base[4],base[5],base[6],"0x30","1",go[1],go[2],go[3]]); (dest.parent/"receipt").write_text(parts[0]+" OK "+" ".join(line.split()[1:])+"\\n"); (dest.parent/"output.raw").write_bytes(bytes(5529600));\n'
                '  if mode=="probe_bad_receipt":\n   p=dest.parent/"receipt"; p.write_text(p.read_text().replace("537004168", "0537004168"))\n'
                '  if mode in ("probe_sequence_2", "probe_sequence_huge"):\n   p=dest.parent/"receipt"; v=p.read_text().split(); v[4]="2" if mode.endswith("_2") else "99999999999999999999"; p.write_text(" ".join(v)+"\\n")\n'
                '  if mode=="probe_bad_output": (dest.parent/"output.raw").write_bytes(b"short")\n'
                '  if mode=="probe_start_change": (d/"procstat").write_text("786 (App Standby) S "+"0 "*18+"457 0\\n")\n'
                '  if mode=="probe_start_flip": (d/"procstat").write_text("786 (App Standby) S "+"0 "*18+"457 0\\n")\n'
                '  if mode=="probe_owner_flip": (d/"owner-flipped").write_text("1")\n'
                ' sys.exit(0)\n'
                'if a[0]=="timeout":\n if len(a)>2 and a[2].endswith("screenshooter"): (d/"shot-timeout").write_text(a[1])\n if os.environ["MODE"]=="reason_fail_timeout" and (d/"reason").exists() and len(a)>3 and a[3]=="stat": sys.exit(124)\n'
                ' if a[1]=="1" and a[3:4]==["stat"] and a[-1].endswith("/dlt"):\n'
                '  (d/"phase-fences").open("a").write("post\\n" if (d/"reason").exists() else "pre\\n")\n'
                '  if os.environ["MODE"]=="probe_reason_fail_phase_timeout" and (d/"reason").exists(): sys.exit(124)\n'
                ' if os.environ["MODE"]=="reason_fail_newline_tail" and (d/"reason").exists() and a[3:6]==["tail","-c","1"]: sys.exit(124)\n'
                ' if os.environ["MODE"]=="reason_fail_after_malformed" and (d/"reason").exists() and len(a)>3 and a[3]=="stat":\n'
                '  p=d/"reason-stat"; n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1));\n'
                '  if n==1: print("1:2:not-a-size"); sys.exit(0)\n'
                ' if (d/"reason").exists() and len(a)>4 and a[3]=="wc" and a[4]=="-c":\n'
                '  p=d/"reason-wc"; n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1));\n'
                '  if os.environ["MODE"] in ("reason_fail_wc_first", "reason_fail_wc_both") and (os.environ["MODE"]=="reason_fail_wc_both" or n==0): sys.exit(124)\n'
                '  if os.environ["MODE"]=="reason_fail_newline_padded": print("999999"); sys.exit(0)\n'
                ' if os.environ["MODE"]=="reason_fail_awk_timeout" and (d/"reason").exists() and len(a)>3 and a[3]=="awk" and any("length($0)>4096" in x for x in a): sys.exit(124)\n'
                ' a=a[2:]\n'
                'if a[0]=="base64":\n print("\\n".join(textwrap.wrap(base64.b64encode(pathlib.Path(a[1]).read_bytes()).decode(),76))); sys.exit(0)\n'
                'if a[0]=="awk" and (a[-1].endswith(".dlt") or (a[-1]=="-" and any(x.startswith("nextstate=") for x in a))) and (d/"output-hashed").exists():\n'
                ' if os.environ["MODE"]=="probe_phase_timing":\n  p=d/"phase-scans"; n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1)); (d/"uptime").write_text(("102.0" if n==0 else "104.0")+" 0\\n")\n'
                ' (d/"postscan").write_text("1")\n'
                ' if os.environ["MODE"]=="probe_owner_postscan": (d/"owner-flipped").write_text("1")\n'
                ' if os.environ["MODE"]=="probe_start_postscan": (d/"procstat").write_text("786 (App Standby) S "+"0 "*18+"457 0\\n")\n'
                'if a[0]=="sha256sum" and a[-1].endswith("/baseline.raw"): (d/"baseline-hashed").write_text("1")\n'
                'if a[0]=="sha256sum" and a[-1].endswith("/baseline.raw") and os.environ["MODE"]=="probe_baseline_replace":\n p=pathlib.Path(a[-1]); p.rename(d/"baseline-old"); p.write_bytes(b"changed-content!")\n'
                'if a[0]=="awk" and a[-1]==str(d/"procstat") and os.environ["MODE"]=="probe_receipt_hidden":\n'
                ' p=d/"proc-reads"; n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1));\n'
                ' if n==3: (d/"dlt").open("ab").write((d/"hidden").read_bytes())\n'
                'if a[0]=="sha256sum" and a[-1].endswith("/output.raw"):\n'
                ' (d/"output-hashed").write_text("1")\n'
                ' if os.environ["MODE"] in ("probe_timeout_post_capture", "probe_timeout_at_capture", "probe_timeout_bad_timestamp"):\n'
                '  receipt=(d/"probe"/"receipt").read_text().split(); cap=int(receipt[5]); marker=cap+701 if os.environ["MODE"]=="probe_timeout_post_capture" else cap; stamp="%02d:%02d:%02d.%03d000"%(marker//3600000,(marker//60000)%60,(marker//1000)%60,marker%1000); stamp += "0" if os.environ["MODE"]=="probe_timeout_bad_timestamp" else ""; (d/"dlt").open("ab").write(("1970/01/01 "+stamp+" 712970 050 MANG STAN STAN log info V 1 [confirmSkPressed()]\\n").encode())\n'
                ' if os.environ["MODE"]=="probe_phase_timing": (d/"uptime").write_text("101.0 0\\n")\n'
                ' if os.environ["MODE"]=="probe_native_timeout": (d/"dlt").open("ab").write(b"1970/01/01 00:01:11.297223 712970 050 MANG STAN STAN log info V 1 [confirmSkPressed()]\\n")\n'
                ' if os.environ["MODE"]=="probe_start_flip": (d/"procstat").write_text("786 (App Standby) S "+"0 "*18+"456 0\\n")\n'
                ' if os.environ["MODE"]=="probe_owner_flip": (d/"owner-flipped").unlink(missing_ok=True)\n'
                ' if os.environ["MODE"]=="probe_start_hash": (d/"procstat").write_text("786 (App Standby) S "+"0 "*18+"457 0\\n")\n'
                ' if os.environ["MODE"]=="probe_owner_hash": (d/"owner-flipped").write_text("1")\n'
                'if a[0]=="sha256sum" and a[-1].endswith("/output.raw") and os.environ["MODE"]=="probe_hash_hidden": (d/"dlt").open("ab").write((d/"hidden").read_bytes())\n'
                'if a[0]=="sha256sum" and len(a)>1 and a[1]=="wayland-screenshot.png":\n'
                ' if os.environ["MODE"]=="hash_late": (d/"uptime").write_text("111.0 0\\n")\n'
                ' if os.environ["MODE"]=="hash_timeout": (d/"dlt").open("ab").write(b"1970/01/01 00:01:11.297223 712970 050 MANG STAN STAN log info V 1 [onTimeout Handler]\\n")\n'
                ' if os.environ["MODE"]=="probe_hash_hidden": (d/"dlt").open("ab").write((d/"hidden").read_bytes())\n'
                'if a[0]=="wc" and a[1]=="-l" and os.environ["MODE"]=="reason_fail_newline_read": sys.exit(124)\n'
                'if a[0]=="wc" and a[1]=="-l" and os.environ["MODE"]=="reason_fail_newline_padded": sys.stdin.buffer.read(); print("01"); sys.exit(0)\n'
                'if a[0]=="awk" and os.environ["MODE"]=="reason_fail_clock_unavailable" and (d/"reason").exists() and any("int((b-a)*1000)" in x for x in a): sys.exit(1)\n'
                'if a[0]=="sleep":\n'
                ' c=d/"uptime"; c.write_text(str(float(c.read_text().split()[0])+1)+" 0\\n");\n'
                ' if os.environ["MODE"]=="partial" and not (d/"completed").exists():\n'
                '  b=(d/"record").read_bytes(); (d/"dlt").open("ab").write(b[len(b)//2:]); (d/"completed").write_text("1")\n'
                ' sys.exit(0)\nos.execvp(a[0],a)\n')
            bb.chmod(0o755)
            dbus = d / "dbus-send"
            dbus.write_text('#!/usr/bin/python3\nimport os,sys,pathlib\nd=pathlib.Path(os.environ["FIXTURE_DIR"]); a=" ".join(sys.argv); mode=os.environ["MODE"]\n'
                'if "GetNameOwner" in a:\n'
                ' if mode=="probe_phase_timing" and (d/"output-hashed").exists(): (d/"uptime").write_text(("103.0" if (d/"postscan").exists() else "101.5")+" 0\\n")\n'
                ' p=d/"owners"; n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1));\n'
                ' if mode=="reason_fail_owner_timeout" and n>0: sys.exit(1)\n'
                ' if mode=="probe_reason_fail_phase_after" and (d/"reason").exists():\n  (d/"dlt").open("ab").writelines((d/"record").read_bytes().splitlines(keepends=True)[2:])\n'
                ' if mode=="probe_hidden_during_identity" and (d/"postscan").exists() and not (d/"hidden-injected").exists():\n  (d/"dlt").open("ab").write((d/"hidden").read_bytes()); (d/"hidden-injected").write_text("1")\n'
                ' if mode=="probe_timeout_during_identity" and (d/"postscan").exists():\n  (d/"dlt").open("ab").write(b"1970/01/01 00:01:11.297223 712970 050 MANG STAN STAN log info V 1 [onTimeout Handler]\\n")\n'
                ' owner=":1.9" if (mode in ("owner_change", "reason_owner_change") and n>0) or (mode in ("probe_owner_flip", "probe_owner_hash", "probe_owner_postscan") and (d/"owner-flipped").exists()) or (mode=="probe_ack_owner_change" and (d/"reason").exists()) else ":1.4"; print("method return sender=:1.0 -> dest=:1.1 reply_serial=1\\n   string \\\""+owner+"\\\"")\n'
                'elif "GetConnectionUnixProcessID" in a:\n'
                ' p=d/"pidqueries"; n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1)); pid=787 if (mode in ("pid_change", "reason_pid_change") and n>0) or (mode=="probe_pid_change" and n>=3) else 786; print("method return sender=:1.0 -> dest=:1.1 reply_serial=1\\n   uint32 "+str(pid))\n'
                'else:\n'
                ' if mode.startswith("probe_") and ((d/"probe"/"baseline.raw").exists() or (d/"probe"/"baseline.raw").is_symlink()): sys.exit(1)\n'
                ' if mode.startswith("probe_") and ((d/"probe"/"go").exists() or (d/"probe"/"go.tmp").exists()): (d/"early-go").write_text("1"); sys.exit(1)\n'
                ' (d/"reason").open("a").write("1");\n'
                ' if mode.startswith(("reason_fail", "probe_reason_fail")) or mode in ("reason_owner_change", "reason_pid_change", "reason_reply_clipped"):\n'
                '  scans=list(d.glob("wb-acq-*.dlt")); (d/"scan-mode").write_text(oct(scans[0].stat().st_mode & 0o777) if len(scans)==1 else "missing");\n'
                '  handler=(d/"reason-handler").read_bytes(); draw=(d/"reason-draw").read_bytes(); evidence=(handler+draw+b"unterminated tail" if mode=="reason_fail_prefix_complete" else handler[len(handler)//2:]+draw+b"unterminated tail" if mode=="reason_fail_prefix_boundary_partial" else (d/"reason-handler-partial").read_bytes() if mode=="reason_fail_prefix_tail_only" else draw+b"unterminated tail" if mode=="reason_fail_prefix_draw_only" else (d/"reason-handler-wrong-context").read_bytes()+draw+b"unterminated tail" if mode=="reason_fail_prefix_wrong_context" else (d/"reason-handler-malformed").read_bytes()+b"unterminated tail" if mode=="reason_fail_prefix_malformed" else b"reason11 handler evidence" + (b"" if mode=="reason_fail_newline_zero" else b"\\n"));\n'
                '  if mode.startswith("probe_reason_fail_phase_"):\n'
                '   native=(d/"record").read_bytes(); evidence=b"".join(native.splitlines(keepends=True)[:2]) if mode=="probe_reason_fail_phase_after" else native\n'
                '   if mode=="probe_reason_fail_phase_incomplete": evidence+=b"unterminated tail"\n'
                '   if mode=="probe_reason_fail_phase_replaced":\n    log=d/"dlt"; old=d/"dlt.replaced"; log.rename(old); log.write_bytes(old.read_bytes())\n'
                '  if mode=="reason_fail_replaced": dlt=d/"dlt"; old=d/"dlt.replaced"; dlt.rename(old); dlt.write_bytes(old.read_bytes())\n'
                '  if mode=="reason_fail_truncated": dlt=d/"dlt"; dlt.write_bytes(dlt.read_bytes()[:-20])\n'
                '  if mode=="reason_fail_prefix_mismatch":\n   dlt=d/"dlt"; data=bytearray(dlt.read_bytes()); data[-20]^=1; dlt.write_bytes(data)\n'
                '  (d/"dlt").open("ab").write(b"x"*262145 if mode=="reason_fail_oversize" else b"x"*4097+b"\\n" if mode=="reason_fail_malformed" else evidence);\n'
                '  if mode=="reason_fail": sys.stderr.write("Error org.freedesktop.DBus.Error.NoReply: Did not receive a reply.\\n"); sys.exit(1)\n'
                '  if mode=="reason_fail_wrapper124": sys.exit(124)\n'
                '  if mode=="reason_fail_wrapper143": sys.exit(143)\n'
                '  if mode in ("reason_fail_1024", "reason_fail_1025", "reason_fail_1025_lf_more"):\n'
                '   prefix="Error org.freedesktop.DBus.Error.NoReply: "; size=1025 if "1025" in mode else 1024; suffix="\\n" if mode=="reason_fail_1025_lf_more" else ""; sys.stderr.write(prefix + "x"*(size-len(prefix)-len(suffix)) + suffix + ("more\\n" if suffix else "")); sys.exit(1)\n'
                '  if mode=="reason_reply_clipped":\n'
                '   prefix="method return sender=:1.4 -> dest=:1.19 reply_serial=2\\n   int32 1\\n"; sys.stdout.write(prefix + "x"*(1025-len(prefix))); sys.exit(0)\n'
                '  if mode=="reason_fail_clock_unavailable": sys.stderr.write("Error org.freedesktop.DBus.Error.NoReply: Did not receive a reply.\\n"); sys.exit(1)\n'
                '  sys.exit(1)\n'
                ' if mode=="reason_late": (d/"uptime").write_text("111.0 0\\n")\n'
                ' b=(d/"record").read_bytes();\n'
                ' if mode in ("valid","large_history","crlf","late","hash_late","hash_timeout","capture_fail","typed_bad","missing_entry","missing_show","wrong_qml","wrong_context","out_of_order","prehandler","duplicate_model","screen_changed","timeout_clock") or mode.startswith("probe_"): (d/"dlt").open("ab").write((b.replace(b"enabled true",b"enabled maybe") if mode=="typed_bad" else b.replace(b"driving false",b"driving true") if mode=="probe_restricted" else b.replace(b"Screen_AppStandbyClock_Confirm_Profile.qml",b"Other.qml") if mode=="wrong_qml" else b.replace(b"MANG STAN STAN",b"MANG OTHER CTXT",1) if mode=="wrong_context" else b.replace(b"\\n",b"\\r\\n") if mode=="crlf" else b))\n'
                ' if mode.startswith(("probe_arm_", "probe_post_")): (d/"dlt").open("ab").write((d/"event").read_bytes())\n'
                ' if mode=="partial": (d/"dlt").open("ab").write(b[:len(b)//2])\n'
                ' print("method return sender=:1.4 -> dest=:1.19 reply_serial=2\\n   int32 "+("10" if mode in ("reason_bad", "probe_reason_bad") else "1"))\n')
            dbus.chmod(0o755)
            ivi = d / "ivi"
            ivi.write_text('#!/usr/bin/python3\nimport os,pathlib,sys\nd=pathlib.Path(os.environ["FIXTURE_DIR"]); mode=os.environ["MODE"]; (d/"ivi-count").open("a").write("1"); b=(d/"record").read_bytes()\n'
                'if mode=="ivi_fail": sys.exit(1)\n'
                'if mode=="ivi_late": (d/"uptime").write_text("111.0 0\\n")\n'
                'if mode in ("timeout","timeout_clock","malformed"): (d/"dlt").open("ab").write((b"1970/01/01 00:01:11.297223 712970 050 MANG STAN STAN log info V 1 [onTimeout Handler]\\n" if mode=="timeout" else b"1970/01/01 00:01:11.297223 712970 050 MANG STAN STAN log info V 1 \\xc3\\xa9 [AppStandbyClockEngine::onTimeoutHandler()]\\r\\n" if mode=="timeout_clock" else b"bad VM_OBSERVE_CONFIRM geometry x\\n"))\n'
                'if mode=="truncate": (d/"dlt").write_text("")\n'
                'if mode=="replace": (d/"dlt").rename(d/"dlt.old"); (d/"dlt").write_bytes(b)\n'
                'if mode=="rewrite": (d/"dlt").write_bytes(b"z"*len((d/"dlt").read_bytes())); (d/"dlt").open("ab").write(b)\n'
                'print("IVI_FG_REQUEST_SENT")\n')
            ivi.chmod(0o755)
            shot = d / "screenshooter"
            shot.write_text('#!/usr/bin/python3\nimport os,pathlib,sys\nd=pathlib.Path(os.environ["FIXTURE_DIR"]); (d/"shot-count").open("a").write("1");\n'
                'if os.environ["MODE"]=="capture_fail": sys.exit(1)\n'
                '(d/"wayland-screenshot.png").write_bytes(b"fixture");\n'
                'if os.environ["MODE"]=="probe_slow_pass": (d/"uptime").write_text("107.0 0\\n")\n'
                'if os.environ["MODE"]=="probe_start_change": (d/"procstat").write_text("786 (App Standby) S "+"0 "*18+"457 0\\n")\n'
                'if os.environ["MODE"].startswith("probe_post_"): (d/"dlt").open("ab").write((d/"event").read_bytes())\n'
                'if os.environ["MODE"]=="probe_late": (d/"uptime").write_text("110.0 0\\n")\n'
                'if os.environ["MODE"]=="late": (d/"uptime").write_text("120.0 0\\n")\n')
            shot.chmod(0o755)
            marker_expectations = {
                "timeout": ("timeout_handler", b"onTimeout Handler"),
                "timeout_clock": ("clock_engine_timeout", b"AppStandbyClockEngine::onTimeoutHandler()"),
                "hash_timeout": ("timeout_handler", b"onTimeout Handler"),
                "probe_native_timeout": ("confirm_sk_pressed", b"confirmSkPressed()"),
                "probe_timeout_at_capture": ("confirm_sk_pressed", b"confirmSkPressed()"),
                "probe_timeout_bad_timestamp": ("confirm_sk_pressed", b"confirmSkPressed()"),
                "probe_timeout_during_identity": ("timeout_handler", b"onTimeout Handler"),
            }
            for mode, expected in (("valid", "ok"), ("partial", "ok"), ("large_history", "ok"), ("crlf", "ok"), ("old_only", "model_deadline"),
                                   ("malformed", "wrong_context"), ("typed_bad", "model_malformed"), ("timeout", "native_timeout"),
                                   ("timeout_clock", "native_timeout"),
                                   ("missing_entry", "model_deadline"), ("missing_show", "native_draw_start"),
                                   ("wrong_qml", "native_show"), ("wrong_context", "wrong_context"),
                                   ("out_of_order", "native_draw_start"), ("prehandler", "native_draw_end"),
                                   ("duplicate_model", "native_model_order"), ("screen_changed", "native_screen_changed"),
                                   ("truncate", "log_changed"), ("replace", "log_changed"), ("rewrite", "log_changed"),
                                   ("owner_change", "owner_changed"), ("pid_change", "owner_changed"),
                                   ("reason_fail", "reason11"), ("reason_fail_wrapper124", "reason11"), ("reason_fail_wrapper143", "reason11"), ("reason_fail_1024", "reason11"), ("reason_fail_1025", "reason11"), ("reason_fail_1025_lf_more", "reason11"), ("reason_reply_clipped", "reason11"), ("reason_fail_clock_unavailable", "reason11"), ("reason_fail_umask000", "reason11"), ("reason_fail_umask022", "reason11"), ("probe_reason_fail_umask000", "reason11"), ("probe_reason_fail_umask022", "reason11"), ("reason_owner_change", "reason11"), ("reason_pid_change", "reason11"), ("reason_fail_oversize", "reason11"), ("reason_fail_malformed", "reason11"), ("reason_fail_timeout", "reason11"), ("reason_fail_wc_first", "reason11"), ("reason_fail_wc_both", "reason11"), ("reason_fail_awk_timeout", "reason11"), ("reason_fail_newline_padded", "reason11"),
                                   ("reason_fail_newline_zero", "reason11"), ("reason_fail_newline_read", "reason11"), ("reason_fail_newline_tail", "reason11"),
                                   ("reason_fail_prefix_complete", "reason11"), ("reason_fail_prefix_tail_only", "reason11"),
                                   ("reason_fail_prefix_draw_only", "reason11"), ("reason_fail_prefix_wrong_context", "reason11"),
                                   ("reason_fail_prefix_malformed", "reason11"), ("reason_fail_prefix_mismatch", "reason11"),
                                   ("reason_fail_prefix_boundary_partial", "reason11"),
                                   ("probe_reason_fail_phase_full", "reason11"), ("probe_reason_fail_phase_incomplete", "reason11"),
                                   ("probe_reason_fail_phase_after", "reason11"), ("probe_reason_fail_phase_timeout", "reason11"),
                                   ("probe_reason_fail_phase_replaced", "reason11"),
                                   ("reason_fail_replaced", "reason11"), ("reason_fail_truncated", "reason11"),
                                   ("reason_fail_after_malformed", "reason11"), ("reason_fail_owner_timeout", "reason11"), ("reason_bad", "reason11_ack"),
                                   ("reason_late", "deadline"), ("probe_reason_bad", "reason11_ack"), ("probe_ack_owner_change", "owner_changed"), ("ivi_fail", "ivi"), ("ivi_late", "deadline"),
                                   ("capture_fail", "capture"), ("late", "capture_deadline"),
                                   ("hash_late", "deadline"), ("hash_timeout", "native_timeout"),
                                   ("scan_collision", "log_preflight"),
                                   ("probe_valid", "ok"), ("probe_phase_timing", "ok"), ("probe_refresh", "ok"), ("probe_refresh_expired", "deadline"), ("probe_stale", "probe_deadline"), ("probe_slow_boundary", "deadline"),
                                   ("probe_timeout", "verification_deadline"), ("probe_restricted", "model_restricted"),
                                   ("probe_late_receipt", "ok"), ("probe_verify_inside", "ok"),
                                   ("probe_late_capture", "probe_deadline"), ("probe_verify_expired", "verification_deadline"),
                                   ("probe_bad_receipt", "probe_receipt"), ("probe_bad_output", "probe_output"),
                                   ("probe_native_timeout", "native_timeout"),
                                   ("probe_timeout_post_capture", "ok"),
                                   ("probe_timeout_at_capture", "native_timeout"),
                                   ("probe_timeout_bad_timestamp", "native_timeout"),
                                   ("probe_baseline_mode", "baseline_data"), ("probe_baseline_symlink", "baseline_data"),
                                   ("probe_baseline_replace", "baseline_data"), ("probe_baseline_late", "baseline_deadline"),
                                   ("probe_baseline_missing", "baseline_deadline"), ("probe_baseline_malformed", "baseline_meta"),
                                   ("probe_sequence_2", "probe_receipt"), ("probe_sequence_huge", "probe_receipt"),
                                   ("probe_start_flip", "probe_identity"), ("probe_owner_flip", "owner_changed"),
                                   ("probe_start_hash", "probe_identity"), ("probe_owner_hash", "owner_changed"),
                                   ("probe_start_postscan", "probe_identity"), ("probe_owner_postscan", "owner_changed"),
                                   ("probe_hidden_during_identity", "unqualified_state_changed"),
                                   ("probe_timeout_during_identity", "native_timeout"),
                                   ("probe_pid_change", "owner_changed"), ("probe_start_change", "probe_identity"), ("probe_hash_hidden", "unqualified_state_changed"), ("probe_receipt_hidden", "unqualified_state_changed"), ("probe_hidden", "unqualified_state_changed"),
                                   ("probe_disabled", "unqualified_state_changed"), ("probe_driving", "unqualified_state_changed"),
                                   ("probe_revisible", "unqualified_state_changed"),
                                   ("probe_arm_hidden", "unqualified_state_changed"), ("probe_arm_disabled", "unqualified_state_changed"),
                                   ("probe_arm_driving", "unqualified_state_changed"), ("probe_post_hidden", "unqualified_state_changed"),
                                   ("probe_post_disabled", "unqualified_state_changed"), ("probe_post_driving", "unqualified_state_changed")):
                with self.subTest(mode=mode):
                    for name in ("request", "request.tmp", "receipt", "output.raw", "baseline.raw", "baseline.meta", "baseline.meta.tmp", "baseline.ack", "baseline.ack.tmp", "go", "go.tmp"):
                        (d / "probe" / name).unlink(missing_ok=True)
                    for stale in d.glob("wb-acq-*"):
                        stale.unlink(missing_ok=True)
                    for name in ("owners", "pidqueries", "reason", "reason-wc", "reason-stat", "ivi-count", "shot-count", "shot-timeout", "completed", "dlt.old", "wayland-screenshot.png", "scan-mode", "post-stats", "proc-reads", "output-hashed", "baseline-hashed", "owner-flipped", "early-go", "postscan", "hidden-injected", "phase-scans", "phase-fences"):
                        (d / name).unlink(missing_ok=True)
                    (d / "procstat").write_text("786 (App Standby) S " + "0 " * 18 + "456 0\n")
                    baseline = (b"old history\n" * 200000 if mode == "large_history" else b"") + record
                    if mode == "reason_fail_prefix_boundary_partial":
                        handler = (d / "reason-handler").read_bytes()
                        baseline += handler[:len(handler) // 2]
                    dlt.write_bytes(baseline); clock.write_text("100.0 0\n")
                    (d / "hidden").write_bytes(hidden)
                    (d / "event").write_bytes(disabled if mode.endswith("disabled") else driving if mode.endswith("driving") else hidden)
                    (d / "record").write_bytes(
                        sequence.replace(entry, b"", 1) if mode == "missing_entry" else
                        sequence.replace(show, b"", 1) if mode == "missing_show" else
                        entry + draw + show + record + hidden + done + native_return if mode == "out_of_order" else
                        record + entry + show + draw + hidden + done + native_return if mode == "prehandler" else
                        sequence.replace(record, record + record, 1) if mode == "duplicate_model" else
                        sequence.replace(hidden, DLT_PREFIX + b"[2] [ void AppStandbyClockModel::setCurrentScreenID(int) ][ 2067 ] 1]\n" + hidden, 1) if mode == "screen_changed" else
                        sequence.replace(hidden, disabled if mode == "probe_disabled" else driving if mode == "probe_driving" else hidden + visible + record if mode == "probe_revisible" else hidden if mode == "probe_hidden" else b"", 1) if mode.startswith("probe_") else sequence)
                    scan = d / ("wb-acq-" + token + ".dlt")
                    if mode == "scan_collision": scan.write_text("preserve")
                    probe_mode = mode.startswith("probe_")
                    initial_log_size = dlt.stat().st_size
                    command = vm_guest_acquisition_command(token, ivi_probe=probe_mode).replace("BB=/bin/busybox", f"BB={shlex.quote(str(bb))}\nkill() {{ :; }}")
                    for old, new in (("/tmp/session_appmgr", str(d / "session")), ("/tmp/launcher-chain/dlt.log", str(dlt)),
                                     ("/tmp/wb-acq-", str(d / "wb-acq-")), ("/proc/uptime", str(clock)),
                                     ("/tmp/vm-ivi-frame-probe", str(d / "probe")), ("/proc/$proc_pid/stat", str(d / "procstat")),
                                     ("/usr/bin/dbus-send", str(dbus)), ("/ivi-fg-standby1000", str(ivi)),
                                     ("/usr/libexec/weston-screenshooter", str(shot)), ("/tmp/workbench-screenshot.log", str(d / "shot.log")),
                                     ("cd /tmp ||", f"cd {shlex.quote(str(d))} ||")):
                        command = command.replace(old, new)
                    inherited_umask = 0o022 if mode.endswith("umask022") else 0o000 if mode.endswith("umask000") else 0o077
                    run = subprocess.run(["/bin/bash"], input=command, text=True, capture_output=True,
                                         env=dict(os.environ, FIXTURE_DIR=temp, MODE=mode), timeout=30,
                                         preexec_fn=lambda: os.umask(inherited_umask))
                    self.assertEqual(run.returncode, 0, run.stderr)
                    if expected == "ok":
                        model, frame, records = vm_guest_parse_acquisition(run.stdout.encode(), token, ivi_probe=probe_mode)
                        self.assertEqual(frame, b"" if probe_mode else b"fixture"); self.assertFalse(model["driving"])
                        if mode == "probe_phase_timing":
                            timings = {row["stage"]: row["elapsed_ms"] for row in records if row["stage"].startswith("VERIFY_")}
                            self.assertEqual([timings[name] for name in (
                                "VERIFY_IDENTITY", "VERIFY_OUTPUT", "VERIFY_IDENTITY_RECHECK",
                                "VERIFY_LOG_SCAN_1", "VERIFY_IDENTITY_FINAL", "VERIFY_LOG_SCAN_2")],
                                [0, 1000, 1500, 2000, 3000, 4000])
                            bound = next(row for row in records if row["stage"] == "RECEIPT_BOUND")
                            detail = bound["verification_timings"]
                            self.assertEqual(len(detail), 41)
                            self.assertEqual([(row["phase"], row["operation"], row["duration_ms"])
                                              for row in detail if row["duration_ms"]], [
                                ("output", "digest", 1000),
                                ("identity_recheck", "owner_query", 500),
                                ("scan_1", "suffix_check", 500),
                                ("identity_final", "owner_query", 1000),
                                ("scan_2", "suffix_check", 1000),
                            ])
                        if mode == "probe_refresh":
                            arm = next(row for row in records if row["stage"] == "PROBE_ARM")
                            self.assertIn("epoch=100000 arm=101320", arm["detail"])
                            self.assertGreaterEqual(arm["elapsed_ms"], 1319)
                    else:
                        with self.assertRaises(GuestAcquisitionError) as failure:
                            vm_guest_parse_acquisition(run.stdout.encode(), token, ivi_probe=probe_mode)
                        self.assertEqual(failure.exception.stage, expected, run.stdout + run.stderr)
                        if mode in ("probe_sequence_2", "probe_sequence_huge", "probe_start_flip", "probe_owner_flip", "probe_bad_receipt", "probe_late_capture", "probe_verify_expired"):
                            self.assertFalse((d / "output-hashed").exists())
                        if mode.startswith(("reason_fail", "probe_reason_fail")) or mode in ("reason_owner_change", "reason_pid_change", "reason_reply_clipped"):
                            self.assertTrue(hasattr(failure.exception, "reason11_diagnostic"), run.stdout)
                            detail = failure.exception.reason11_diagnostic
                            if mode == "reason_fail":
                                self.assertEqual(detail["dispatch"]["result"], "dbus_no_reply")
                                self.assertEqual(detail["dispatch"]["exit_code"], 1)
                                self.assertGreater(detail["dispatch"]["response_bytes"], 0)
                                self.assertIn("D-Bus NoReply", str(failure.exception))
                            if mode in ("reason_fail_wrapper124", "reason_fail_wrapper143"):
                                expected_code = 124 if mode.endswith("124") else 143
                                self.assertEqual(detail["dispatch"]["result"], "wrapper_timeout")
                                self.assertEqual(detail["dispatch"]["exit_code"], expected_code)
                                self.assertEqual(detail["dispatch"]["response_bytes"], 0)
                                self.assertIn("D-Bus wrapper timed out", str(failure.exception))
                            if mode in ("reason_fail_1024", "reason_fail_1025", "reason_fail_1025_lf_more"):
                                expected_bytes = 1024 if mode == "reason_fail_1024" else 1025
                                self.assertEqual(detail["dispatch"]["response_bytes"], expected_bytes)
                                self.assertEqual(detail["dispatch"]["clipped"], expected_bytes == 1025)
                            if mode == "reason_fail_clock_unavailable":
                                self.assertEqual(detail["dispatch"]["clipped"], False)
                                self.assertEqual(detail["dispatch"]["duration_ms"], "unavailable")
                            if mode == "reason_reply_clipped":
                                self.assertEqual(detail["dispatch"]["result"], "reply")
                                self.assertEqual(detail["dispatch"]["response_bytes"], 1025)
                                self.assertTrue(detail["dispatch"]["clipped"])
                                self.assertNotIn("REASON11_ACK", [row["stage"] for row in failure.exception.records])
                            self.assertEqual((d / "scan-mode").read_text(), "0o600")
                            self.assertEqual((detail["qualification"], detail["epoch_ms"], detail["owner"], detail["pid"], detail["starttime"]), ("UNQUALIFIED", 100000, ":1.4", 786, 456))
                            self.assertEqual(detail["current_owner"], "unknown" if mode == "reason_fail_owner_timeout" else ":1.9" if mode == "reason_owner_change" else ":1.4")
                            self.assertEqual(detail["current_pid"], 0 if mode == "reason_fail_owner_timeout" else 787 if mode == "reason_pid_change" else 786)
                            self.assertEqual(detail["snapshot"],
                                             "log_identity_or_bounds" if mode == "reason_fail_oversize" else
                                             "line_check_failed" if mode in ("reason_fail_malformed", "reason_fail_awk_timeout") else
                                             "newline_check_failed" if mode in ("reason_fail_newline_zero",
                                                                               "probe_reason_fail_phase_incomplete",
                                                                               "reason_fail_prefix_complete", "reason_fail_prefix_tail_only",
                                                                               "reason_fail_prefix_draw_only", "reason_fail_prefix_wrong_context",
                                                                               "reason_fail_prefix_malformed", "reason_fail_prefix_boundary_partial") else
                                             "read_failed" if mode in ("reason_fail_newline_read", "reason_fail_newline_tail") else
                                             "byte_check_failed" if mode in ("reason_fail_wc_first", "reason_fail_wc_both",
                                                                             "reason_fail_newline_padded") else
                                             "prefix_mismatch" if mode in ("reason_fail_prefix_mismatch", "reason_fail_truncated") else
                                             "log_identity_or_bounds" if mode in ("reason_fail_after_malformed", "reason_fail_replaced", "probe_reason_fail_phase_replaced") else
                                             "read_failed" if mode == "reason_fail_timeout" else "ok")
                            expected_prefix = {
                                "probe_reason_fail_phase_incomplete": ("complete_prefix", "observed", "observed", 6),
                                "reason_fail_prefix_complete": ("complete_prefix", "observed", "observed", 2),
                                "reason_fail_prefix_draw_only": ("complete_prefix",
                                                                    "not_observed_in_complete_prefix", "observed", 1),
                                "reason_fail_prefix_boundary_partial": ("complete_prefix",
                                                                           "not_observed_in_complete_prefix",
                                                                           "observed", 1),
                                "reason_fail_prefix_tail_only": ("complete_prefix",
                                                                    "not_observed_in_complete_prefix",
                                                                    "not_observed_in_complete_prefix", 0),
                                "reason_fail_newline_zero": ("complete_prefix",
                                                                "not_observed_in_complete_prefix",
                                                                "not_observed_in_complete_prefix", 0),
                            }.get(mode, ("insufficient_evidence", "insufficient_evidence",
                                         "insufficient_evidence", 0))
                            self.assertEqual((detail["complete_prefix"]["evidence"],
                                              detail["complete_prefix"]["handler_entry_observation"],
                                              detail["complete_prefix"]["draw_progress_observation"],
                                              detail["complete_prefix"]["record_count"]), expected_prefix)
                            self.assertTrue(detail["complete_prefix"]["absence_not_proven"])
                            if mode.startswith("probe_reason_fail_phase_"):
                                self.assertEqual((d / "phase-fences").read_text().splitlines(), ["pre", "post"])
                                self.assertEqual(detail["native_phase"], {
                                    "probe_reason_fail_phase_full": "native_return",
                                    "probe_reason_fail_phase_incomplete": "native_return",
                                    "probe_reason_fail_phase_after": "confirm_show",
                                }.get(mode, "unavailable"))
                            elif probe_mode:
                                self.assertEqual(detail["native_phase"], "no_ordered_chain")
                            if mode.startswith("reason_fail_prefix_"):
                                self.assertEqual(failure.exception.trace, b"")
                            if mode in ("reason_fail_wc_first", "reason_fail_wc_both", "reason_fail_newline_padded"):
                                self.assertEqual((d / "reason-wc").read_text(), "1")
                            if mode == "reason_fail_after_malformed":
                                self.assertFalse((d / "reason-wc").exists())
                                self.assertEqual((d / "reason-stat").read_text(), "2")
                        if mode == "probe_slow_boundary":
                            diagnostic_command = vm_guest_probe_failure_command(token, 786, 456, 100000, 129999).replace("BB=/bin/busybox", f"BB={shlex.quote(str(bb))}").replace("/tmp/vm-ivi-frame-probe", str(d / "probe"))
                            evidence_run = subprocess.run(["/bin/bash"], input=diagnostic_command, text=True, capture_output=True, env=dict(os.environ, FIXTURE_DIR=temp, MODE=mode), timeout=10)
                            self.assertEqual(evidence_run.returncode, 0, evidence_run.stderr)
                            diagnostic = vm_guest_parse_probe_failure(evidence_run.stdout.encode(), token, 786, 456, 100000, 129999)
                            self.assertEqual(diagnostic["qualification"], "UNQUALIFIED")
                            self.assertTrue(diagnostic["receipt"].startswith(token + " OK 786 456 "))
                            bad_start = vm_guest_probe_failure_command(token, 786, 457, 100000, 129999).replace("BB=/bin/busybox", f"BB={shlex.quote(str(bb))}").replace("/tmp/vm-ivi-frame-probe", str(d / "probe"))
                            mismatch = subprocess.run(["/bin/bash"], input=bad_start, text=True, capture_output=True, env=dict(os.environ, FIXTURE_DIR=temp, MODE=mode), timeout=10)
                            self.assertNotEqual(mismatch.returncode, 0)
                            path = d / "probe" / "receipt"
                            original = path.read_bytes()
                            for invalid in (original.replace(token.encode(), b"a" * 32, 1), original.replace(b" OK ", b" BAD ", 1)):
                                path.write_bytes(invalid)
                                invalid_run = subprocess.run(["/bin/bash"], input=diagnostic_command, text=True, capture_output=True, env=dict(os.environ, FIXTURE_DIR=temp, MODE=mode), timeout=10)
                                self.assertNotEqual(invalid_run.returncode, 0)
                                with self.assertRaises(ValueError): vm_guest_parse_probe_failure(invalid_run.stdout.encode(), token, 786, 456, 100000, 129999)
                            path.write_bytes(original)
                        fail_record = failure.exception.records[-1]
                        if mode == "probe_timeout_during_identity":
                            completed = [row["stage"] for row in failure.exception.records]
                            self.assertIn("VERIFY_LOG_SCAN_1", completed)
                            self.assertIn("VERIFY_IDENTITY_FINAL", completed)
                            self.assertNotIn("VERIFY_LOG_SCAN_2", completed)
                            bound = next(row for row in failure.exception.records if row["stage"] == "RECEIPT_BOUND")
                            detail = bound["verification_timings"]
                            self.assertEqual((detail[-1]["phase"], detail[-1]["operation"]),
                                             ("scan_2", "suffix_check"))
                            self.assertTrue(any(row["phase"] == "scan_1" and row["operation"] == "cache_commit"
                                                for row in detail))
                        cutoff = (VM_IVI_VERIFICATION_DEADLINE_MS if any(row["stage"] == "VERIFY_START" for row in failure.exception.records) else
                                  VM_IVI_CAPTURE_DEADLINE_MS if any(row["stage"] == "PROBE_ARM" for row in failure.exception.records) else 10000)
                        self.assertIn("cutoff=" + str(cutoff), fail_record["detail"])
                        self.assertGreaterEqual(int(fail_record["detail"].split("diagnostic_ms=")[1]), fail_record["elapsed_ms"])
                        if mode in marker_expectations:
                            marker_name, marker_bytes = marker_expectations[mode]
                            expected_offset = dlt.read_bytes()[initial_log_size:].index(marker_bytes)
                            self.assertIn("native_marker=" + marker_name, fail_record["detail"])
                            self.assertIn("marker_offset=" + str(expected_offset), fail_record["detail"])
                            persisted = json.dumps({"failure": failure.exception.stage,
                                                    "records": failure.exception.records})
                            self.assertNotIn(marker_bytes.decode("ascii"), persisted)
                            self.assertLessEqual(expected_offset, 1048575)
                            if mode == "probe_native_timeout":
                                self.assertEqual(cutoff, VM_IVI_VERIFICATION_DEADLINE_MS)
                                stages_seen = [row["stage"] for row in failure.exception.records]
                                self.assertIn("VERIFY_START", stages_seen)
                                self.assertIn("RECEIPT_BOUND", stages_seen)
                        if mode in ("malformed", "timeout"):
                            self.assertTrue(failure.exception.trace)
                    if mode == "scan_collision":
                        self.assertEqual(scan.read_text(), "preserve")
                        self.assertFalse((d / "reason").exists())
                        scan.unlink()
                    elif mode != "probe_refresh_expired" and not mode.startswith("probe_baseline_"):
                        self.assertEqual((d / "reason").read_text(), "1")
                    if mode.startswith(("reason_fail", "probe_reason_fail", "probe_baseline_")) or mode in ("reason_owner_change", "reason_pid_change", "reason_reply_clipped", "reason_bad", "probe_reason_bad", "probe_ack_owner_change", "reason_late", "scan_collision", "probe_refresh_expired", "probe_slow_boundary"):
                        self.assertFalse((d / "ivi-count").exists())
                    else:
                        self.assertEqual((d / "ivi-count").read_text(), "1")
                    self.assertEqual((d / "shot-count").exists(), mode in ("valid", "partial", "large_history", "crlf", "late", "hash_late", "hash_timeout", "capture_fail"))
                    if mode == "probe_refresh_expired":
                        self.assertFalse((d / "probe" / "request").exists())
                    if probe_mode:
                        self.assertFalse((d / "probe" / "baseline.raw").exists())
                        self.assertFalse((d / "early-go").exists())
                        self.assertNotIn("baseline-content", run.stdout)
                        self.assertNotIn(base64.b64encode(b"baseline-content").decode(), run.stdout)
                    if mode.startswith("probe_baseline_"):
                        self.assertFalse((d / "reason").exists())
                    if mode.startswith("probe_reason_fail") or mode in ("probe_reason_bad", "probe_ack_owner_change"):
                        self.assertFalse((d / "probe" / "go").exists())
                    if mode == "probe_baseline_malformed":
                        self.assertFalse((d / "baseline-hashed").exists())
                    if mode.startswith("probe_post_"):
                        self.assertTrue((d / "probe" / "request").exists())

    def test_bounded_readiness_retry_expiry_and_terminal_failure(self):
        launcher = (Path(__file__).resolve().parents[1] / "tools/uk_fw/guest/launch-vm-workbench.sh").read_text()
        waiter = launcher[launcher.index("vm_wait_bounded() {"):launcher.index("vm_sim_probe() {")]
        # No real sleep: shell functions make the first two probes pending.
        prefix = "BB=bb\nbb() { :; }\n" + waiter
        for body, expected in (("probe() { n=$((n+1)); [ $n -ge 3 ]; }", "0 3"),
                               ("probe() { n=$((n+1)); return 1; }", "1 3"),
                               ("probe() { n=$((n+1)); return 2; }", "2 1")):
            program = prefix + "\nn=0\n" + body + "\nvm_wait_bounded 3 probe; rc=$?; printf '%s %s' \"$rc\" \"$n\"\n"
            result = subprocess.run([PIPEFAIL_SHELL], input=program, text=True,
                                    capture_output=True, timeout=3)
            self.assertEqual((result.returncode, result.stdout), (0, expected), result.stderr)
        self.assertLess(launcher.index("vm_wait_bounded 30 vm_sim_probe"), launcher.index("/app/bin/AppLauncher 3"))
        self.assertIn("kill -0 \"$sim_pid\"", launcher)
        self.assertIn("GetNameOwner", launcher)

    def test_host_readiness_propagates_terminal_launch_failure(self):
        bridge = GuestShell.__new__(GuestShell)
        calls = []
        def failed(command, **kwargs):
            calls.append((command, kwargs))
            raise RuntimeError("launcher exited")
        with mock.patch.object(bridge, "_run", side_effect=failed), self.assertRaises(RuntimeError):
            bridge.wait_standby_prerequisites()
        self.assertIn("workbench-launch.status", calls[0][0])
        self.assertEqual(calls[0][1]["timeout"], 320)

    def test_launch_preflight_refuses_preexisting_failure_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            receipt, target = directory / "receipt", directory / "missing"
            bridge = GuestShell.__new__(GuestShell)

            def run_isolated(command):
                for path, fixture in (("/tmp/workbench-launch.status", directory / "status"),
                                      ("/tmp/workbench-launch.failure", receipt)):
                    command = command.replace(path, shlex.quote(str(fixture)))
                # If admission falls through, leave a test marker instead of launching.
                command = command.split("|| exit 1; ")
                script = "|| exit 1; ".join(command[:-1]) + "|| exit 1; printf admitted)"
                result = subprocess.run([PIPEFAIL_SHELL, "-c", script], capture_output=True,
                                        timeout=3)
                self.assertEqual((result.returncode, result.stdout), (1, b""), result.stderr)

            with mock.patch.object(bridge, "_run", side_effect=run_isolated):
                receipt.write_bytes(b"standby_exited\n")
                bridge.launch(frame_probe=True)
                self.assertEqual(receipt.read_bytes(), b"standby_exited\n")
                receipt.unlink()
                receipt.symlink_to(target)
                bridge.launch(frame_probe=True)
                self.assertTrue(receipt.is_symlink())
                self.assertFalse(target.exists())

    def test_native_readiness_real_shell_probe_and_failure_gates(self):
        """Exercise the shipped shell probes with isolated fake bus and log."""
        root = Path(__file__).resolve().parents[1]
        launcher = (root / "tools/uk_fw/guest/launch-vm-workbench.sh").read_text()
        functions = launcher[launcher.index("vm_bus_identity() {"):launcher.index("export PATH=")]
        registered = '"[REGISTERED] registeredFromNativeApp AppId[10][AppStandbyClock] onDemand[0] groupNum[1] | time 00:01:07.446"\n'
        cleared = '"ClearTimeoutLoading : 10, PID : 786 | time 00:01:07.447"\n'
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            busybox = folder / "busybox"
            busybox.write_text('#!/usr/bin/python3\nimport os, sys\na=sys.argv[1:]\n'
                'if a[0]=="stat":\n s=os.stat(a[-1]); print(f"{s.st_dev}:{s.st_ino}:{s.st_size}"); sys.exit(0)\n'
                'if a[0]=="timeout": a=a[2:]\nos.execvp(a[0],a)\n')
            busybox.chmod(0o755)
            dbus = folder / "dbus-send"
            dbus.write_text('#!/usr/bin/python3\nimport os, pathlib, sys\n'
                'args=" ".join(sys.argv[1:]); d=pathlib.Path(os.environ["FIXTURE_DIR"]); mode=os.environ["FIXTURE_MODE"]\n'
                'if "GetNameOwner" in args:\n'
                ' p=d/"owners"; n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1));\n'
                ' if mode=="owner_disappears" and n>0: sys.exit(1)\n'
                ' owner=":1.9" if mode=="owner_change" and n>0 else ":1.4"; print("method return sender=:1.0 -> dest=:1.1 reply_serial=1\\n   string \\\""+owner+"\\\"")\n'
                'elif "GetConnectionUnixProcessID" in args:\n'
                ' p=d/"pidqueries"; n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1)); pid=787 if mode=="pid_change" and n>0 else 786; print("method return sender=:1.0 -> dest=:1.1 reply_serial=1\\n   uint32 "+str(pid))\n'
                'elif "Peer.Ping" in args:\n'
                ' (d/"pings").write_text(args);\n'
                ' if mode=="missing_ping": sys.exit(1)\n'
                ' print("x"*1025 if mode=="oversize_ping" else "malformed" if mode=="malformed_ping" else "method return sender=:1.4 -> dest=:1.1 reply_serial=2" + ("\\n   int32 1" if mode=="nonempty_ping" else ""))\n'
                'else: sys.exit(1)\n')
            dbus.chmod(0o755)
            functions = functions.replace("/usr/bin/dbus-send", str(dbus))
            functions = functions.replace('[ -S /run/user/root/wayland-0 ] && [ -x /ivi-fg-standby1000 ] || return 1', ':')
            for mode, content, expected, action in (
                ("owner_only", "", "1", ""),
                ("stale", "", "1", ""),
                ("matching", registered + cleared, "0", ""),
                ("wrong_pid", registered + cleared.replace("786", "785"), "2", ""),
                ("timeout", '[TIMEOUT] [1 Group] AppID : 10, PID : 786\n' + registered + cleared, "2", ""),
                ("nonempty_ping", registered + cleared, "2", ""),
                ("malformed_ping", registered + cleared, "2", ""),
                ("oversize_ping", registered + cleared, "2", ""),
                ("missing_ping", registered + cleared, "1", ""),
                ("owner_change", registered + cleared, "2", ""),
                ("owner_disappears", registered + cleared, "2", ""),
                ("pid_change", registered + cleared, "2", ""),
                ("exited", registered + cleared, "2", ""),
                ("oversize", "x" * 1048577, "2", ""),
                ("delayed", "", "0", f'printf %s {shlex.quote(registered + cleared)} >> "$vm_log"; vm_standby_probe; rc=$?'),
                ("truncate", "initial data\n", "2", ': > "$vm_log"; vm_standby_probe; rc=$?'),
                ("replace", "initial data\n", "2", 'mv "$vm_log" "$vm_log.old"; printf replacement > "$vm_log"; vm_standby_probe; rc=$?'),
                ("rewrite", "initial data\n", "2", 'printf "changed data\\n" > "$vm_log"; vm_standby_probe; rc=$?'),
            ):
                with self.subTest(mode=mode):
                    for name in ("owners", "pidqueries", "pings", "scan", "launch.log.old"):
                        (folder / name).unlink(missing_ok=True)
                    log = folder / "launch.log"
                    log.write_text(registered + cleared if mode == "stale" else "")
                    script = (f'BB={shlex.quote(str(busybox))}\n' + functions +
                        f'\nvm_log={shlex.quote(str(log))}; vm_scan={shlex.quote(str(folder / "scan"))}\n'
                        'vm_stat=$($BB stat -c %d:%i:%s "$vm_log"); vm_log_id=${vm_stat%:*}; vm_log_offset=${vm_stat##*:}; vm_prev_size=$vm_log_offset; '
                        'vm_prev_hash=$(vm_log_hash "$vm_prev_size"); vm_owner=; vm_pid=; sim_pid=100; launcher_pid=200\n'
                        'kill() { [ "$FIXTURE_MODE" != exited ] || [ "$2" != 786 ]; }\n' +
                        f'printf %s {shlex.quote(content)} >> "$vm_log"\n'
                        'vm_standby_probe; rc=$?\n' + action + '\nprintf "%s %s\\n" "$rc" "$vm_stage"\n'
                        '[ "$rc" != 0 ] || printf foreground >> "$FIXTURE_DIR/downstream"\n')
                    (folder / "downstream").unlink(missing_ok=True)
                    result = subprocess.run([PIPEFAIL_SHELL], input=script, text=True, capture_output=True,
                                            env=dict(os.environ, FIXTURE_DIR=temp, FIXTURE_MODE=mode), timeout=15)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.split()[0], expected, result.stderr + result.stdout)
                    self.assertEqual((folder / "downstream").exists(), expected == "0")
                    if mode == "matching":
                        ping = (folder / "pings").read_text()
                        self.assertIn("--dest=:1.4 /com/lge/hkmc/avn/appfunc/valetmode org.freedesktop.DBus.Peer.Ping", ping)

    def test_native_readiness_deadline_emits_terminal_failure(self):
        launcher = (Path(__file__).resolve().parents[1] / "tools/uk_fw/guest/launch-vm-workbench.sh").read_text()
        loop = launcher[launcher.index("while :; do\n  read -r vm_now"):]
        with tempfile.TemporaryDirectory() as temp:
            clock = Path(temp) / "uptime"
            receipt = Path(temp) / "receipt"
            loop = loop.replace("/proc/uptime", shlex.quote(str(clock))).replace(
                "/tmp/workbench-launch.failure", shlex.quote(str(receipt)))
            script = "vm_deadline=120\nvm_standby_probe() { vm_stage=standby_exited; return 2; }\n" + loop
            for uptime, stage in (("121.0", "deadline"), ("119.0", "standby_exited")):
                with self.subTest(stage=stage):
                    clock.write_text(uptime + " 0.0\n")
                    result = subprocess.run([PIPEFAIL_SHELL], input=script, text=True,
                                            capture_output=True, timeout=3)
                    self.assertEqual(result.returncode, 25)
                    self.assertIn("WORKBENCH_STANDBY_FAIL_" + stage, result.stdout)
                    self.assertEqual(receipt.read_text(), stage + "\n")
                    self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
                    # Subsequent writes cannot replace an existing receipt.
                    receipt.write_text("previous\n")
                    repeated = subprocess.run([PIPEFAIL_SHELL], input=script, text=True,
                                              capture_output=True, timeout=3)
                    self.assertEqual(repeated.returncode, 25)
                    self.assertEqual(receipt.read_text(), "previous\n")
                    receipt.unlink()
            missing = Path(temp) / "missing"
            receipt.symlink_to(missing)
            rejected = subprocess.run([PIPEFAIL_SHELL], input=script, text=True,
                                      capture_output=True, timeout=3)
            self.assertEqual(rejected.returncode, 25)
            self.assertTrue(receipt.is_symlink())
            self.assertFalse(missing.exists())

    def test_foreground_preparation_order_and_failure_are_closed(self):
        calls = []
        class Shell:
            def wait_standby_prerequisites(self): calls.append("ready")
            def capture(self): calls.append("transport")
            def read_startup_receipt(self): calls.append("receipt"); return {"byte0": 8}
            def foreground_and_probe(self): calls.append("foreground"); return {"driving": False}, b"frame", {"acquisition": {}}, b"private", b"private", []
        class Runtime:
            def record_event(self, *args): calls.append("evidence" if args[0] == "startup" else ("probe" if args[1] == "probe_acquired" else "model"))
            def publish_frame(self, *args, **kwargs):
                assert kwargs == {"historical": True}
                calls.append("publish")
        vm_workbench_prepare_foreground(Shell(), Runtime())
        self.assertEqual(calls, ["ready", "transport", "receipt", "evidence", "foreground", "model", "probe", "publish"])
        calls.clear()
        class ProbeFailure(Shell):
            def foreground_and_probe(self):
                calls.append("foreground")
                raise RuntimeError("probe failed")
        with self.assertRaisesRegex(RuntimeError, "probe failed"):
            vm_workbench_prepare_foreground(ProbeFailure(), Runtime())
        self.assertEqual(calls, ["ready", "transport", "receipt", "evidence", "foreground"])
        calls.clear()
        class BadShell(Shell):
            def read_startup_receipt(self): calls.append("receipt"); return {"byte0": 0}
        with self.assertRaises(RuntimeError):
            vm_workbench_prepare_foreground(BadShell(), Runtime())
        self.assertEqual(calls, ["ready", "transport", "receipt"])
        for failure in ("readiness", "capture", "receipt"):
            calls.clear()
            class FailureShell(Shell):
                def wait_standby_prerequisites(self):
                    calls.append("ready")
                    if failure == "readiness": raise ValueError("invalid readiness")
                def capture(self):
                    calls.append("transport")
                    if failure == "capture": raise ValueError("invalid screenshot")
                def read_startup_receipt(self):
                    calls.append("receipt")
                    raise ValueError("malformed receipt")
            with self.assertRaises(ValueError):
                vm_workbench_prepare_foreground(FailureShell(), Runtime())
            self.assertNotIn("foreground", calls)

    def test_probe_workspace_compatibility_and_capture_cadence(self):
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            (workspace / "build").mkdir()
            (workspace / "rootfs.img").write_bytes(b"root")
            (workspace / "build/weston-ivi-frame-probe.so").write_bytes(b"helper")
            root_hash = hashlib.sha256(b"root").hexdigest()
            metadata = {"sha256": {"rootfs.img": root_hash}, "workbench_frame_probe": {
                "source_sha256": PROBE_SOURCE_HASH, "script_sha256": PROBE_SCRIPT_HASH,
                "helper_sha256": hashlib.sha256(b"helper").hexdigest(), "rootfs_sha256": root_hash}}
            (workspace / "prepare.json").write_text(json.dumps(metadata))
            vm_workbench_require_probe_workspace(workspace)
            (workspace / "build/weston-ivi-frame-probe.so").unlink()
            with self.assertRaisesRegex(ValueError, "workspace is incompatible"):
                vm_workbench_require_probe_workspace(workspace)
            (workspace / "prepare.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "workspace is incompatible"):
                vm_workbench_require_probe_workspace(workspace)
        calls = []
        class Stop:
            def is_set(self): return len(calls) >= 4
            def wait(self, seconds): calls.append(("wait", seconds))
        class Runtime:
            def get_status(self): return {"state": "running"}
            def publish_frame(self, frame, source): calls.append(("publish", frame, source))
        class Shell:
            def capture(self): calls.append("capture"); return b"frame"
        vm_workbench_capture_loop(Stop(), Runtime(), lambda: Shell(), None)
        self.assertEqual(calls, ["capture", ("publish", b"frame", "guest-compositor"), ("wait", 3),
                                 "capture", ("publish", b"frame", "guest-compositor"), ("wait", 3)])

    def test_probe_source_pin_matches_disk_and_prepare_rejects_mismatches(self):
        source = Path(__file__).resolve().parents[1] / "tools/uk_fw/guest/weston_ivi_frame_probe.c"
        self.assertEqual(vm_workbench_hash(source), PROBE_SOURCE_HASH)
        with tempfile.TemporaryDirectory() as temp:
            for pinned_name in ("PROBE_SOURCE_HASH", "PROBE_SCRIPT_HASH"):
                with self.subTest(pinned_name=pinned_name), \
                     mock.patch("vm_workbench.cli.OUTPUT", Path(temp)), \
                     mock.patch("vm_workbench.cli.vm_workbench_prerequisites"), \
                     mock.patch("vm_workbench.cli.shutil.copy2"), \
                     mock.patch("vm_workbench.cli.subprocess.run"), \
                     mock.patch("vm_workbench.cli." + pinned_name, "0" * 64):
                    destination = Path(temp) / pinned_name.lower()
                    with self.assertRaisesRegex(ValueError, "pinned frame-probe source or build script mismatch"):
                        vm_workbench_prepare(destination, frame_probe=True)

    def test_diagnostic_stages_fail_closed_and_preserve_typed_results(self):
        bridge = GuestShell.__new__(GuestShell)
        names = ["applet_stat", "applet_wc", "applet_awk", "applet_sleep", "applet_tail", "applet_head", "shell_pipefail",
                 "before_exists", "before", "timer_wait", "after_exists", "after", "bounded_tail", "final_identity"]
        responses = [b"", b"", b"", b"", b"", b"", b"", b"1", b"2:3:100\n4\n2:3:100", b"",
                     b"1", b"2:3:200\n5\n2:3:200", b"1", b"2:3:200"]
        def run_fixture(fail_index=None, failure=RuntimeError):
            calls = []
            def run(command, timeout, *, timing, lock_timeout, quarantine_timeout, total_deadline):
                index = len(calls); calls.append(command)
                timing.update(lock_wait_s=.01, execution_s=.02)
                self.assertTrue(quarantine_timeout)
                self.assertGreater(lock_timeout, 0)
                if index == fail_index:
                    raise failure("fixture")
                return responses[index]
            with mock.patch.object(bridge, "_run", side_effect=run):
                return bridge.diagnose_confirm_observation()
        result = run_fixture()
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["before_exists"] and result["after_exists"] and result["identity_held"])
        self.assertTrue(result["size_nonshrinking"] and result["new_record"])
        self.assertEqual(result["bounded_tail_count"], 1)
        self.assertEqual(result["before"], {"device": 2, "inode": 3, "size": 100, "count": 4})
        for i, name in enumerate(names):
            for error in (RuntimeError, TimeoutError):
                with self.subTest(stage=name, error=error.__name__):
                    value = run_fixture(i, error)
                    self.assertEqual((value["status"], value["failed_stage"]), ("error", name))
                    self.assertEqual(value["reason"], "timeout" if error is TimeoutError else "stage_failed")
                    self.assertEqual(value["stages"][name]["lock_wait_s"], .01)

        for bad_after in (b"4:3:200\n5\n4:3:200", b"2:3:80\n5\n2:3:80"):
            replies = responses.copy(); replies[11] = bad_after
            with mock.patch.object(bridge, "_run", side_effect=replies):
                self.assertEqual(bridge.diagnose_confirm_observation()["failed_stage"], "after")
        for missing in (7, 10):
            replies = responses.copy(); replies[missing] = b"0"
            with mock.patch.object(bridge, "_run", side_effect=replies):
                value = bridge.diagnose_confirm_observation()
                self.assertFalse(value["before_exists" if missing == 7 else "after_exists"])
                self.assertEqual(value["failed_stage"], names[missing])
        replies = responses.copy(); replies[11] = b"2:3:2000000\n5\n2:3:2000000"
        with mock.patch.object(bridge, "_run", side_effect=replies):
            self.assertEqual(bridge.diagnose_confirm_observation()["failed_stage"], "bounded_tail")

    def test_diagnostic_lock_wait_is_separate_and_timed_out_guest_is_quarantined(self):
        with tempfile.TemporaryDirectory() as temp:
            proc = subprocess.Popen([PIPEFAIL_SHELL], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            bridge = GuestShell(proc, Path(temp) / "serial.log", lambda *args: None)
            held = threading.Event()
            def hold():
                with bridge._lock:
                    held.set(); time.sleep(.2)
            holder = threading.Thread(target=hold); holder.start()
            try:
                self.assertTrue(held.wait(1))
                short = {}
                with self.assertRaises(TimeoutError):
                    bridge._run("printf must-not-run", timeout=1, timing=short, lock_timeout=.03, quarantine_timeout=True)
                self.assertGreaterEqual(short["lock_wait_s"], .02)
                self.assertNotIn("execution_s", short)
                timing = {}
                self.assertEqual(bridge._run("printf ok", timeout=2, timing=timing, lock_timeout=1), b"ok")
                self.assertGreater(timing["lock_wait_s"], .1)
                self.assertLess(timing["execution_s"], 1)
                with self.assertRaises(TimeoutError):
                    bridge._run("sleep 1", timeout=.1, timing={}, lock_timeout=1, quarantine_timeout=True)
                with self.assertRaisesRegex(RuntimeError, "quarantined"):
                    bridge._run("printf must-not-run", timeout=1)
            finally:
                holder.join(); proc.terminate(); proc.wait(timeout=5); proc.stdin.close(); bridge.close(); proc.stdout.close()

    def test_diagnostic_fixed_commands_against_large_log_fixture(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            log, shim = folder / "dlt.log", folder / "busybox"
            log.write_bytes((b"ordinary log data\n" * 450000) + DLT_PREFIX + CONFIRM + b"]\n")
            self.assertGreater(log.stat().st_size, 7_000_000)
            appended = b"\n" + DLT_PREFIX + CONFIRM + b"]\n"
            shim.write_text("#!/usr/bin/python3\nimport os,sys,time\n"
                            "app=sys.argv[1]; args=sys.argv[2:]\n"
                            f"log={str(log)!r}\n"
                            f"record={appended!r}\n"
                            "if app=='sleep':\n"
                            " if args==['2']:\n  f=open(log,'ab'); f.write(record); f.close()\n"
                            " time.sleep(.01); sys.exit(0)\n"
                            "if app=='stat':\n s=os.stat(args[-1]); print(str(s.st_dev)+':'+str(s.st_ino)+':'+str(s.st_size)); sys.exit(0)\n"
                            "os.execvp(app,[app]+args)\n")
            shim.chmod(0o755)
            bridge = GuestShell.__new__(GuestShell)
            def execute(command, timeout, **kwargs):
                command = command.replace('/tmp/launcher-chain/dlt.log', str(log)).replace('/bin/busybox', str(shim))
                result = subprocess.run([PIPEFAIL_SHELL, '-c', command], capture_output=True,
                                        timeout=timeout)
                if result.returncode:
                    raise RuntimeError('guest operation failed')
                return result.stdout
            with mock.patch.object(bridge, '_run', side_effect=execute):
                result = bridge.diagnose_confirm_observation()
            self.assertEqual((result['status'], result['failed_stage']), ('completed', None))
            self.assertEqual((result['before']['count'], result['after']['count'], result['bounded_tail_count']), (1, 2, 1))
            self.assertTrue(result['identity_held'] and result['size_nonshrinking'] and result['new_record'])
            shim.write_text(shim.read_text().replace("os.execvp(app,[app]+args)",
                                                    "if app=='awk': sys.exit(127)\nos.execvp(app,[app]+args)"))
            with mock.patch.object(bridge, '_run', side_effect=execute):
                result = bridge.diagnose_confirm_observation()
            self.assertEqual((result['status'], result['failed_stage']), ('error', 'applet_awk'))

    def test_confirm_geometry_parser_and_fixed_guest_command(self):
        value = vm_guest_parse_confirm_geometry(CONFIRM + b"\n")
        self.assertEqual(value["buttonRoot"], [479, 629, 690, 63])
        self.assertEqual([value[k] for k in ("enabled", "visible", "driving", "calling")], [True, True, False, False])
        bridge = GuestShell.__new__(GuestShell)
        with mock.patch.object(bridge, "_run", return_value=CONFIRM) as run:
            self.assertEqual(bridge.observe_confirm_geometry(), value)
            command = run.call_args.args[0]
            self.assertIn("/tmp/launcher-chain/dlt.log", command)
            self.assertIn("/bin/busybox sleep 2", command)
            self.assertIn('test "$wb_growth" -le 1048576', command)
            self.assertIn('test "$1:$2" = "$wb_id"', command)
            self.assertIn('test "$wb_hash" = "$wb_hash_after"', command)
            self.assertNotIn('awk -v re="$wb_pattern" \'$0 ~ re', command)
            self.assertEqual(run.call_args.kwargs["timeout"], 10)
        for data in (b"", CONFIRM + b"\n" + CONFIRM, CONFIRM + b" extra",
                     CONFIRM.replace(b"enabled true", b"enabled 1"),
                     CONFIRM.replace(b"modelEnableBtn 1", b"modelEnableBtn true"),
                     CONFIRM.replace(b"modelEnableBtn 1", b"modelEnableBtn 2"),
                     CONFIRM.replace(b"buttonRoot 479", b"buttonRoot nan"),
                     CONFIRM.replace(b"buttonRoot 479", b"buttonRoot 1500"),
                     CONFIRM.replace(b"690 63", b"0 63"),
                     CONFIRM.replace(b"root 0 0 1920 720", b"root 0 0 800 480")):
            with self.subTest(data=data[-90:]), self.assertRaises(ValueError):
                vm_guest_parse_confirm_geometry(data)

    def test_confirm_probe_appended_regions_and_large_history(self):
        """Run the shipped shell command against actual append/race fixtures."""
        good = DLT_PREFIX + CONFIRM + b"]\n"
        newer = DLT_PREFIX + CONFIRM.replace(b"visible true", b"visible false") + b"]\n"
        bridge = GuestShell.__new__(GuestShell)
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            log, shim, count, trace = (folder / name for name in ("dlt.log", "busybox", "stat-count", "tail-offsets"))
            def execute_case(history, appended, mode="append"):
                log.write_bytes(history)
                count.write_text("0")
                trace.write_text("")
                shim.write_text("#!/usr/bin/python3\nimport os,sys,time\n"
                    "app=sys.argv[1]; args=sys.argv[2:]\n"
                    f"log={str(log)!r}; count={str(count)!r}; trace={str(trace)!r}\n"
                    f"record={appended!r}; future={newer!r}; mode={mode!r}\n"
                    "if app=='sleep':\n"
                    " if mode=='replace':\n  p=log+'.replacement'; open(p,'wb').write(record); os.replace(p,log)\n"
                    " elif mode=='regrow':\n  n=os.stat(log).st_size; open(log,'wb').write(b'Z'*(n+1)+record)\n"
                    " elif mode=='shrink': open(log,'wb').write(record[:1])\n"
                    " else: open(log,'ab').write(record)\n"
                    " sys.exit(0)\n"
                    "if app=='stat':\n"
                    " n=int(open(count).read())+1; open(count,'w').write(str(n))\n"
                    " if mode=='final_race' and n==3: open(log,'wb').write(b'X')\n"
                    " s=os.stat(args[-1])\n"
                    " if mode=='append_after_snapshot' and n==2:\n  f=open(log,'ab'); f.write(future+b'Z'*131072); f.close()\n"
                    " if mode=='final_boundary_race' and n==3:\n  f=open(log,'r+b'); f.seek(0); f.write(b'Z'*s.st_size); f.close()\n"
                    " print(str(s.st_dev)+':'+str(s.st_ino)+':'+str(s.st_size)); sys.exit(0)\n"
                    "if app=='tail': open(trace,'a').write(args[1]+'\\n')\n"
                    "os.execvp(app,[app]+args)\n")
                shim.chmod(0o755)
                def execute(command, timeout):
                    command = command.replace('/tmp/launcher-chain/dlt.log', str(log)).replace('/bin/busybox', str(shim))
                    result = subprocess.run([PIPEFAIL_SHELL, '-c', command], capture_output=True,
                                            timeout=timeout)
                    if result.returncode:
                        raise RuntimeError('guest operation failed')
                    return result.stdout
                with mock.patch.object(bridge, '_run', side_effect=execute):
                    start = time.monotonic()
                    try: result = bridge.observe_confirm_geometry()
                    except (RuntimeError, ValueError): result = None
                    return result, time.monotonic() - start, [int(x.lstrip('+')) for x in trace.read_text().splitlines()]
            for size in (15_600_000, 32_000_000):
                result, duration, offsets = execute_case(b'x' * (size - 1) + b'\n', good)
                self.assertTrue(result['visible'])
                self.assertLess(duration, 5)
                self.assertGreaterEqual(min(offsets), size - 255)
            cases = (
                (b'', good, 'append', True, True),
                (b'history\n', good, 'append', True, True),
                (b'history', b' suffix\n' + good, 'append', True, True),
                (good[:80], good[80:], 'append', False, None),
                (good[:80], good[80:] + good, 'append', True, True),
                (b'old\n', good + newer, 'append', True, False),
                (b'old\n', b'unrelated\n' + good + b'other\n' + newer + b'unrelated\n', 'append', True, False),
                (b'old\n', good + b'noise VM_OBSERVE_CONFIRM geomXtry\n', 'append', True, True),
                (b'old\n', good + b'garbage ' + newer, 'append', False, None),
                (b'old\n', b'garbage ' + newer + good, 'append', False, None),
                (b'old\n', good + (DLT_PREFIX + CONFIRM.replace(b'visible true', b'visible invalid') + b']\n'), 'append', False, None),
                (b'old\n', good + b'XVM_OBSERVE_CONFIRM geometry not-an-envelope\n', 'append', False, None),
                (b'old\n', good, 'append_after_snapshot', True, True),
                (b'old\n', good + b'partial', 'append', True, True),
                (b'old\n', good + b'bad VM_OBSERVE_CONFIRM geometry partial', 'append', True, True),
                (b'old\n', good[:-1], 'append', False, None),
                (b'old\n', b'unrelated\n', 'append', False, None),
                (b'old\n', b'', 'append', False, None),
                (b'old\n', b'x' * 1048577, 'append', False, None),
                (b'old\n', b'x\n' * 8193 + good, 'append', False, None),
                (b'old\n', good, 'replace', False, None),
                (b'old\n' * 100, good, 'regrow', False, None),
                (b'old\n' * 100, good, 'shrink', False, None),
                (b'old\n' * 100, good, 'final_race', False, None),
                (b'old\n' * 100, good, 'final_boundary_race', False, None),
            )
            for history, appended, mode, succeeds, visible in cases:
                with self.subTest(mode=mode, history=len(history), append=len(appended)):
                    result, _, _ = execute_case(history, appended, mode)
                    self.assertEqual(result is not None, succeeds)
                    if succeeds: self.assertEqual(result['visible'], visible)

    def test_fixed_confirm_probe_requires_new_record_and_rejects_truncation(self):
        # Execute the exact guest shell logic against an isolated log. The shim
        # supplies BusyBox applets and scales its two-second wait for fixtures.
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            log = folder / "launcher.log"
            shim = folder / "busybox"
            shim.write_text("#!/usr/bin/python3\nimport os,sys,time\n"
                            "app=sys.argv[1]; args=sys.argv[2:]\n"
                            "if app=='sleep': time.sleep(.3); sys.exit(0)\n"
                            "if app=='stat':\n s=os.stat(args[-1]); print(str(s.st_dev)+':'+str(s.st_ino)+':'+str(s.st_size)); sys.exit(0)\n"
                            "os.execvp(app,[app]+args)\n")
            shim.chmod(0o755)
            bridge = GuestShell.__new__(GuestShell)
            def execute(command, timeout):
                self.assertEqual(timeout, 10)
                command = command.replace("/bin/busybox", str(shim)).replace("/tmp/launcher-chain/dlt.log", str(log))
                result = subprocess.run([PIPEFAIL_SHELL, "-c", command], capture_output=True,
                                        timeout=5)
                if result.returncode:
                    raise RuntimeError("guest operation failed")
                return result.stdout
            def append_record():
                time.sleep(.15)
                with log.open("ab") as stream:
                    stream.write(DLT_PREFIX + CONFIRM + b"]\n")
            with mock.patch.object(bridge, "_run", side_effect=execute):
                log.write_bytes(DLT_PREFIX + CONFIRM + b"]\n")
                with self.assertRaises(RuntimeError):
                    bridge.observe_confirm_geometry()
                writer = threading.Thread(target=append_record)
                writer.start()
                try:
                    self.assertTrue(bridge.observe_confirm_geometry()["enabled"])
                finally:
                    writer.join()
                good = DLT_PREFIX + CONFIRM + b"]\n"
                bad_records = (
                    b"nonsense " + good,
                    good.replace(b"1970/01/01", b"1970/13/01"),
                    good.replace(b"00:01:11.297223", b"25:01:11.297223"),
                    good.replace(b".297223", b".29722"),
                    good.replace(b"712970", b"712x70"),
                    good.replace(b"050 MANG", b"999 MANG"),
                    good.replace(b"050 MANG", b"50 MANG"),
                    good.replace(b"MANG STAN STAN", b"MANG STAN FAIL"),
                    good.replace(b"log info V 1", b"log warn V 1"),
                    good.replace(b"log info V 1", b"log info V 2"),
                    good.replace(b"VM_OBSERVE_CONFIRM geometry", b"XVM_OBSERVE_CONFIRM geometry"),
                    good[:-1] + b" trailing\n",
                )
                for invalid in bad_records:
                    with self.subTest(invalid=invalid[:90]):
                        log.write_bytes(good)
                        def append_bad():
                            time.sleep(.15)
                            with log.open("ab") as stream:
                                stream.write(invalid)
                        writer = threading.Thread(target=append_bad)
                        writer.start()
                        try:
                            with self.assertRaises(RuntimeError):
                                bridge.observe_confirm_geometry()
                        finally:
                            writer.join()
                def append_malformed():
                    time.sleep(.15)
                    with log.open("ab") as stream:
                        stream.write(DLT_PREFIX + CONFIRM + b" extra]\n")
                writer = threading.Thread(target=append_malformed)
                writer.start()
                try:
                    with self.assertRaises(ValueError):
                        bridge.observe_confirm_geometry()
                finally:
                    writer.join()
                def truncate():
                    time.sleep(.15)
                    log.write_bytes(b"")
                writer = threading.Thread(target=truncate)
                writer.start()
                try:
                    with self.assertRaises(RuntimeError):
                        bridge.observe_confirm_geometry()
                finally:
                    writer.join()

    def test_debugging_mode_parses_one_byte_across_dbus_send_formats(self):
        header = b"method return time=1.0 sender=:1.0 -> destination=:1.1 serial=3 reply_serial=2\n"
        self.assertEqual(vm_guest_parse_debugging_mode(header + b'   array of bytes "" + \\0\n'), 0)
        for value in (1, 7, 9, 10, 13, 31, 127, 128, 255):
            data = header + b"   array of bytes [\n      " + f"{value:02x}".encode() + b"\n   ]\n"
            self.assertEqual(vm_guest_parse_debugging_mode(data), value)
        for value in range(32, 127):
            data = header + b'   array of bytes "' + bytes([value]) + b'"\n'
            self.assertEqual(vm_guest_parse_debugging_mode(data), value)

    def test_debugging_mode_rejects_missing_multiple_malformed_and_noise(self):
        header = b"method return time=1.0 sender=:1.0 -> destination=:1.1 serial=3 reply_serial=2\n"
        good = header + b"   array of bytes [\n      07\n   ]\n"
        for data in (b"", header, good + good, good + b"noise\n", b"noise\n" + good,
                     header + b"   array of bytes [\n      07 08\n   ]\n",
                     header + b"   array of bytes [\n      100\n   ]\n",
                     header + b"   array of bytes [\n   ]\n",
                     header + b'   array of bytes "AB"\n', b"x" * 4097):
            with self.subTest(data=data[:80]), self.assertRaises(ValueError):
                vm_guest_parse_debugging_mode(data)

    def test_debugging_mode_uses_only_fixed_system_bus_command(self):
        bridge = GuestShell.__new__(GuestShell)
        reply = b"method return time=1 sender=:1.0 -> destination=:1.1 serial=2 reply_serial=2\n   array of bytes [\n      09\n   ]\n"
        with mock.patch.object(bridge, "_run", return_value=reply) as run:
            self.assertEqual(bridge.observe_debugging_mode(), 9)
            command = run.call_args.args[0]
            self.assertEqual(command, "/bin/busybox timeout 5 /usr/bin/dbus-send --system --print-reply "
                             "--reply-timeout=3000 --dest=com.lge.car.micom /Ihu "
                             "com.lge.car.micom.ihu.AskDebuggingMode </dev/null 2>/dev/null")
            self.assertEqual(run.call_args.kwargs["timeout"], 10)
        with self.assertRaises(TypeError):
            bridge.observe_debugging_mode("; arbitrary command")
    def test_unadopted_child_reaped_when_real_bridge_log_open_fails(self):
        child = OwnedFakeProcess()
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "not-created"
            with self.assertRaises(FileNotFoundError):
                vm_workbench_spawn(["fake-qemu"], run_dir=missing, event=lambda *args: None,
                                   process_factory=lambda *args, **kwargs: child)
        self.assertEqual(child.signals, ["terminate"])
        self.assertEqual(child.waits, 1)
        self.assertIsNotNone(child.poll())
        self.assertTrue(all(stream.closed for stream in (child.stdin, child.stdout, child.stderr)))

    def test_partial_bridge_failure_kills_after_timeout_and_closes_log(self):
        child = OwnedFakeProcess(timeout_first=True)
        captured = []
        failure = RuntimeError("reader startup failed")

        class FailedBridge:
            def __init__(self, process, path, event):
                self._log = io.BytesIO()
                captured.append(self._log)
                raise failure

        with self.assertRaises(RuntimeError) as caught:
            vm_workbench_spawn(["fake-qemu"], run_dir="/tmp", event=lambda *args: None,
                               process_factory=lambda *args, **kwargs: child, bridge_type=FailedBridge)
        self.assertIs(caught.exception, failure)
        self.assertEqual(child.signals, ["terminate", "kill"])
        self.assertEqual(child.waits, 2)
        self.assertEqual(child.poll(), -9)
        self.assertTrue(captured[0].closed)
        self.assertTrue(all(stream.closed for stream in (child.stdin, child.stdout, child.stderr)))

    def test_actual_bridge_reader_start_failure_closes_acquired_log(self):
        child = OwnedFakeProcess()
        logs = []
        failure = RuntimeError("cannot start reader")
        real_fdopen = os.fdopen
        def capture_fdopen(*args, **kwargs):
            stream = real_fdopen(*args, **kwargs)
            logs.append(stream)
            return stream
        with tempfile.TemporaryDirectory() as directory, \
             mock.patch("vm_workbench.guest_shell.os.fdopen", side_effect=capture_fdopen), \
             mock.patch("vm_workbench.guest_shell.threading.Thread.start", side_effect=failure):
            with self.assertRaises(RuntimeError) as caught:
                vm_workbench_spawn(["fake-qemu"], run_dir=directory, event=lambda *args: None,
                                   process_factory=lambda *args, **kwargs: child)
        self.assertIs(caught.exception, failure)
        self.assertEqual(len(logs), 1)
        self.assertTrue(logs[0].closed)
        self.assertEqual(child.signals, ["terminate"])
        self.assertEqual(child.waits, 1)
        self.assertTrue(all(stream.closed for stream in (child.stdin, child.stdout, child.stderr)))

    def test_serial_log_is_private_and_existing_paths_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            child = OwnedFakeProcess()
            previous_umask = os.umask(0)
            try:
                process, bridge = vm_workbench_spawn(["fake-qemu"], run_dir=directory,
                    event=lambda *args: None, process_factory=lambda *args, **kwargs: child)
                bridge._reader.join(2)
                self.assertEqual((Path(directory) / "serial.log").stat().st_mode & 0o777, 0o600)
            finally:
                os.umask(previous_umask)
                for stream in (child.stdin, child.stdout, child.stderr):
                    stream.close()
            self.assertIs(process, child)
            original = (Path(directory) / "serial.log").read_bytes()
            second = OwnedFakeProcess()
            with self.assertRaises(FileExistsError):
                vm_workbench_spawn(["fake-qemu"], run_dir=directory, event=lambda *args: None,
                                   process_factory=lambda *args, **kwargs: second)
            self.assertEqual(second.signals, ["terminate"])
            self.assertEqual((Path(directory) / "serial.log").read_bytes(), original)

    def test_insecure_directory_or_log_mode_failure_stops_before_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory).chmod(0o755)
            child = OwnedFakeProcess()
            with self.assertRaises(PermissionError):
                vm_workbench_spawn(["fake-qemu"], run_dir=directory, event=lambda *args: None,
                                   process_factory=lambda *args, **kwargs: child)
            self.assertEqual(child.signals, ["terminate"])
            self.assertFalse((Path(directory) / "serial.log").exists())
            Path(directory).chmod(0o700)
            other = OwnedFakeProcess()
            with mock.patch("vm_workbench.guest_shell.os.fchmod", side_effect=PermissionError("fixture")):
                with self.assertRaises(PermissionError):
                    vm_workbench_spawn(["fake-qemu"], run_dir=directory, event=lambda *args: None,
                                       process_factory=lambda *args, **kwargs: other)
            self.assertEqual(other.signals, ["terminate"])
            self.assertEqual((Path(directory) / "serial.log").stat().st_size, 0)

    def test_successful_bridge_adoption_leaves_child_and_pipes_open(self):
        child = OwnedFakeProcess()

        class GoodBridge:
            def __init__(self, process, path, event):
                self.process = process

        process, bridge = vm_workbench_spawn(["fake-qemu"], run_dir="/tmp", event=lambda *args: None,
                                            process_factory=lambda *args, **kwargs: child, bridge_type=GoodBridge)
        self.assertIs(process, child)
        self.assertIs(bridge.process, child)
        self.assertEqual(child.signals, [])
        self.assertEqual(child.waits, 0)
        self.assertFalse(any(stream.closed for stream in (child.stdin, child.stdout, child.stderr)))
        for stream in (child.stdin, child.stdout, child.stderr):
            stream.close()

    def test_acquisition_failure_writer_is_private_exclusive_and_best_effort(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            diagnostic = {"qualification": "UNQUALIFIED", "failure": "reason11", "records": [{"stage": "MODEL"}]}
            exc = GuestAcquisitionError("reason11", diagnostic["records"])
            exc.diagnostic = diagnostic
            with mock.patch("builtins.print") as printed:
                path = vm_workbench_write_acquisition_failure(run_dir, exc)
            self.assertEqual(path, run_dir / "acquisition-failure.json")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(path.read_text()), diagnostic)
            self.assertIn(str(path), printed.call_args.args[0])

            original = path.read_bytes()
            replacement = GuestAcquisitionError("timeout", [])
            replacement.diagnostic = {"qualification": "UNQUALIFIED", "failure": "timeout"}
            self.assertIsNone(vm_workbench_write_acquisition_failure(run_dir, replacement))
            self.assertEqual(path.read_bytes(), original)

            self.assertIsNone(vm_workbench_write_acquisition_failure(run_dir, RuntimeError("invalid")))
            invalid = GuestAcquisitionError("invalid", [])
            invalid.diagnostic = {"failure": float("nan")}
            self.assertIsNone(vm_workbench_write_acquisition_failure(run_dir, invalid, "invalid.json"))
            self.assertFalse((run_dir / "invalid.json").exists())

            write_failure = GuestAcquisitionError("write", [])
            write_failure.diagnostic = {"qualification": "UNQUALIFIED", "failure": "write"}
            with mock.patch("vm_workbench.cli.os.open", side_effect=PermissionError("fixture")):
                self.assertIsNone(vm_workbench_write_acquisition_failure(run_dir, write_failure, "write.json"))
            self.assertFalse((run_dir / "write.json").exists())

    def test_normal_wifi_and_confirm_acquisition_failures_persist_then_reap_owned_fakes(self):
        cases = ((False, False, None), (False, True, None), (True, False, None),
                 (False, False, TimeoutError))
        for confirm, wifi_sim, error_type in cases:
            with self.subTest(confirm=confirm, wifi_sim=wifi_sim, error_type=error_type), \
                 tempfile.TemporaryDirectory() as directory:
                workspace = Path(directory)
                events = []
                if error_type is None:
                    failure = GuestAcquisitionError("reason11", [{"stage": "MODEL"}])
                    failure.diagnostic = {"qualification": "UNQUALIFIED", "failure": "reason11",
                                          "records": failure.records}
                else:
                    failure = error_type("transport timeout")
                    failure.diagnostic = {"qualification": "UNQUALIFIED", "failure": "acquisition_transport"}
                shell = mock.MagicMock()
                shell.wait_ready.side_effect = lambda: events.append("wait_ready")
                shell.wait_standby_prerequisites.side_effect = lambda: events.append("standby")
                shell.capture.side_effect = lambda: (events.append("capture"), b"frame")[1]
                shell.read_startup_receipt.side_effect = lambda: (events.append("receipt"), {"byte0": 8})[1]
                shell.foreground_and_probe.side_effect = lambda: (events.append("acquisition"), (_ for _ in ()).throw(failure))[1]
                shell.close.side_effect = lambda: events.append("bridge_closed")
                process = object()

                class FakeRuntime:
                    def __init__(self, _workspace, run_dir, _qemu, process_factory, compatibility_setup):
                        self.run_dir, self.process_factory = run_dir, process_factory

                    def start(self):
                        self.run_dir.mkdir(parents=True, mode=0o700)
                        self.process_factory(["fake-qemu"], cwd=str(self.run_dir))

                    def attach_channels(self, **_kwargs):
                        pass

                    def record_event(self, *_args):
                        pass

                    def shutdown(self):
                        events.append("runtime_shutdown")

                output = io.StringIO()
                wifi_simulation = (b"assets", b"target") if wifi_sim else None
                with mock.patch("vm_workbench.cli.vm_workbench_require_probe_workspace"), \
                     mock.patch("vm_workbench.cli.vm_workbench_spawn", return_value=(process, shell)), \
                     mock.patch("vm_workbench.cli.WorkbenchRuntime", FakeRuntime), \
                     mock.patch("vm_workbench.wifi_sim.session.wifi_sim_prepare_overlay") as prepare_overlay, \
                     mock.patch("vm_workbench.cli.time.time_ns", return_value=123), \
                     mock.patch("sys.stdout", output):
                    with self.assertRaises(type(failure)) as caught:
                        vm_workbench_run(workspace, diagnostic_ivi_confirm=confirm, wifi_simulation=wifi_simulation)
                if wifi_sim:
                    prepare_overlay.assert_called_once_with(shell, b"assets")
                else:
                    prepare_overlay.assert_not_called()
                run_dir = workspace / "runs" / "123"
                filename = "ivi-confirm-failure.json" if confirm else "acquisition-failure.json"
                path = run_dir / filename
                self.assertIs(caught.exception, failure)
                self.assertEqual(json.loads(path.read_text()), failure.diagnostic)
                self.assertIn(str(path), output.getvalue())
                self.assertEqual(events[-2:], ["runtime_shutdown", "bridge_closed"])
                self.assertNotIn("launch", events)
                shell._run.assert_not_called()
                shell.publish_input.assert_not_called()
                shell.publish_input_bounded.assert_not_called()
                shell.publish_simulator.assert_not_called()

    def test_post_create_write_failure_preserves_error_and_removes_partial_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace, events, streams = Path(directory), [], []
            failure = GuestAcquisitionError("reason11", [{"stage": "MODEL"}])
            failure.diagnostic = {"qualification": "UNQUALIFIED", "failure": "reason11",
                                  "records": failure.records}
            shell = mock.MagicMock()
            shell.close.side_effect = lambda: events.append("bridge_closed")

            class FakeRuntime:
                def __init__(self, _workspace, run_dir, _qemu, process_factory, compatibility_setup):
                    self.run_dir, self.process_factory = run_dir, process_factory

                def start(self):
                    self.run_dir.mkdir(parents=True, mode=0o700)
                    self.process_factory(["fake-qemu"], cwd=str(self.run_dir))

                def attach_channels(self, **_kwargs):
                    pass

                def record_event(self, *_args):
                    pass

                def shutdown(self):
                    events.append("runtime_shutdown")

            run_dir = workspace / "runs" / "789"
            destination = run_dir / "acquisition-failure.json"
            expected = (json.dumps(failure.diagnostic, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n").encode()
            real_fdopen = os.fdopen

            def capture_fdopen(*args, **kwargs):
                stream = real_fdopen(*args, **kwargs)
                streams.append(stream)
                return stream

            def fail_after_write(_fd):
                self.assertTrue(destination.is_file())
                self.assertEqual(destination.read_bytes(), expected)
                raise OSError("fixture fsync failure")

            with mock.patch("vm_workbench.cli.vm_workbench_require_probe_workspace"), \
                 mock.patch("vm_workbench.cli.vm_workbench_spawn", return_value=(object(), shell)), \
                 mock.patch("vm_workbench.cli.WorkbenchRuntime", FakeRuntime), \
                 mock.patch("vm_workbench.cli.vm_workbench_prepare_foreground", side_effect=failure), \
                 mock.patch("vm_workbench.cli.time.time_ns", return_value=789), \
                 mock.patch("vm_workbench.cli.os.fdopen", side_effect=capture_fdopen), \
                 mock.patch("vm_workbench.cli.os.fsync", side_effect=fail_after_write):
                with self.assertRaises(GuestAcquisitionError) as caught:
                    vm_workbench_run(workspace)
            self.assertIs(caught.exception, failure)
            self.assertEqual(len(streams), 1)
            self.assertTrue(streams[0].closed)
            self.assertFalse(destination.exists())
            self.assertEqual(events[-2:], ["runtime_shutdown", "bridge_closed"])

    def test_successful_startup_writes_no_failure_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace, events = Path(directory), []
            shell = mock.MagicMock()
            shell.wait_ready.side_effect = lambda: events.append("wait_ready")
            shell.launch.side_effect = lambda **kwargs: events.append("launch")
            shell.wait_standby_prerequisites.side_effect = lambda: events.append("standby")
            shell.capture.side_effect = lambda: (events.append("capture"), b"frame")[1]
            shell.read_startup_receipt.side_effect = lambda: (events.append("receipt"), {"byte0": 8})[1]
            shell.foreground_and_probe.side_effect = lambda: ({"model": "fixture"}, b"png",
                                                               {"acquisition": "bounded"}, b"source", b"output", [])
            shell.close.side_effect = lambda: events.append("bridge_closed")

            class FakeRuntime:
                def __init__(self, _workspace, run_dir, _qemu, process_factory, compatibility_setup):
                    self.run_dir, self.process_factory = run_dir, process_factory

                def start(self):
                    self.run_dir.mkdir(parents=True, mode=0o700)
                    self.process_factory(["fake-qemu"], cwd=str(self.run_dir))

                def attach_channels(self, **_kwargs):
                    pass

                def record_event(self, *_args):
                    pass

                def publish_frame(self, *_args, **_kwargs):
                    pass

                def shutdown(self):
                    events.append("runtime_shutdown")

            class FakeServer:
                origin = "http://127.0.0.1:1"

                def serve_forever(self, **_kwargs):
                    events.append("served")

                def server_close(self):
                    events.append("server_closed")

            with mock.patch("vm_workbench.cli.vm_workbench_require_probe_workspace"), \
                 mock.patch("vm_workbench.cli.vm_workbench_spawn", return_value=(object(), shell)), \
                 mock.patch("vm_workbench.cli.WorkbenchRuntime", FakeRuntime), \
                 mock.patch("vm_workbench.cli.WorkbenchHTTPServer", return_value=FakeServer()), \
                 mock.patch("vm_workbench.cli.vm_workbench_capture_loop"), \
                 mock.patch("vm_workbench.cli.time.time_ns", return_value=456):
                vm_workbench_run(workspace)
            run_dir = workspace / "runs" / "456"
            self.assertEqual(list(run_dir.glob("*failure*.json")), [])
            self.assertEqual([name for name in ("served", "server_closed", "runtime_shutdown", "bridge_closed")
                              if name in events], ["served", "server_closed", "runtime_shutdown", "bridge_closed"])

    def test_capture_accepts_numbered_chunks_amid_unrelated_serial_noise(self):
        token = "a" * 32
        raw = b"sample-png-bytes" * 20
        encoded = base64.b64encode(raw)
        chunks = [encoded[i:i + 76] for i in range(0, len(encoded), 76)]
        marker = ("WB_FRAME_" + token).encode()
        records = [marker + b" META " + str(len(raw)).encode() + b" " + hashlib.sha256(raw).hexdigest().encode()]
        for index, chunk in enumerate(chunks, 1):
            records += [b"[  3.25] guest kernel message", marker + b" CHUNK " + str(index).encode() + b" " + chunk]
        records.append(marker + b" END " + str(len(chunks)).encode())
        self.assertEqual(vm_guest_decode_capture(b"\n".join(records) + b"\n", token), raw)

    def test_capture_recovers_exact_interleaved_kernel_warning_and_still_checks_hash(self):
        token = "d" * 32
        marker = ("WB_FRAME_" + token).encode()
        raw = b"screenshot bytes" * 5
        encoded = base64.b64encode(raw)
        chunks = [encoded[i:i + 76] for i in range(0, len(encoded), 76)]
        records = [marker + b" META " + str(len(raw)).encode() + b" " + hashlib.sha256(raw).hexdigest().encode()]
        records += [marker + b" CHUNK " + str(i).encode() + b" " + chunk for i, chunk in enumerate(chunks, 1)]
        records.append(marker + b" END " + str(len(chunks)).encode())
        packet = b"\r\n".join(records) + b"\r\n"
        warning = b"[   28.751168] serial8250: too much work for irq4\r\n"
        # Real logs show warnings in the marker itself and the base64 data.
        packet = packet.replace(marker, marker[:15] + warning + marker[15:], 1)
        packet = packet.replace(chunks[0], chunks[0][:24] + warning + chunks[0][24:], 1)
        self.assertEqual(vm_guest_decode_capture(packet, token), raw)
        with self.assertRaises(ValueError):
            vm_guest_decode_capture(packet.replace(chunks[1], b"A" + chunks[1][1:], 1), token)
        with self.assertRaises(ValueError):
            vm_guest_decode_capture(packet.replace(b"irq4", b"irq5", 1), token)

    def test_capture_rejects_dropped_reordered_duplicate_and_corrupt_records(self):
        token = "b" * 32
        marker = ("WB_FRAME_" + token).encode()
        raw = b"a" * 60
        encoded = base64.b64encode(raw)
        meta = marker + b" META 60 " + hashlib.sha256(raw).hexdigest().encode()
        one, two = marker + b" CHUNK 1 " + encoded[:76], marker + b" CHUNK 2 " + encoded[76:]
        end = marker + b" END 2"
        for records in ([meta, one, end], [meta, two, one, end], [meta, one, one, two, end],
                        [meta, one, two], [meta.replace(b"META 60", b"META 61"), one, two, end],
                        [meta[:-1] + b"0", one, two, end], [meta, one[:-1] + b"*", two, end],
                        [meta, one, two, end, end], [meta, one, two, marker + b" END 3"]):
            with self.subTest(records=records), self.assertRaises(ValueError):
                vm_guest_decode_capture(b"\n".join(records), token)

    def test_capture_recovers_exact_hrtimer_warning_at_each_record_boundary(self):
        token = "e" * 32
        marker = ("WB_FRAME_" + token).encode()
        raw = bytes(range(256)) * 3
        encoded = base64.b64encode(raw)
        chunks = [encoded[i:i + 76] for i in range(0, len(encoded), 76)]
        records = [marker + b" META 768 " + hashlib.sha256(raw).hexdigest().encode()]
        records += [marker + b" CHUNK " + str(i).encode() + b" " + chunk
                    for i, chunk in enumerate(chunks, 1)]
        records.append(marker + b" END " + str(len(chunks)).encode())
        # Exercise split marker, length, digest, two-digit index, observed
        # base64 offset, END keyword and count, with both console line endings.
        positions = ((0, 15), (0, len(marker) + len(b" META 7")),
                     (0, len(marker) + len(b" META 768 ") + 23),
                     (12, len(marker) + len(b" CHUNK 1")),
                     (1, len(marker) + len(b" CHUNK 1 ") + 59),
                     (len(records) - 1, len(marker) + len(b" E")),
                     (len(records) - 1, len(marker) + len(b" END 1")))
        for ending in (b"\n", b"\r\n"):
            warning = b"[   66.820751] hrtimer: interrupt took 7168042 ns" + ending
            for record_index, offset in positions:
                with self.subTest(ending=ending, record=record_index, offset=offset):
                    split = list(records)
                    record = split[record_index]
                    split[record_index] = record[:offset] + warning + record[offset:]
                    self.assertEqual(vm_guest_decode_capture(ending.join(split) + ending, token), raw)

    def test_capture_rejects_hrtimer_near_matches_inside_authoritative_chunk(self):
        token = "f" * 32
        marker = ("WB_FRAME_" + token).encode()
        raw = b"screenshot bytes" * 8
        encoded = base64.b64encode(raw)
        chunks = [encoded[i:i + 76] for i in range(0, len(encoded), 76)]
        records = [marker + b" META " + str(len(raw)).encode() + b" " + hashlib.sha256(raw).hexdigest().encode()]
        records += [marker + b" CHUNK " + str(i).encode() + b" " + chunk
                    for i, chunk in enumerate(chunks, 1)]
        records.append(marker + b" END " + str(len(chunks)).encode())
        warning = b"[   66.820751] hrtimer: interrupt took 7168042 ns\n"
        invalid = (warning.replace(b"hrtimer", b"hrtimers"),
                   warning.replace(b"interrupt took", b"interrupt takes"),
                   warning.replace(b" ns", b" us"),
                   warning.replace(b"7168042", b"+7168042"),
                   warning.replace(b"7168042", b"-7168042"),
                   warning.replace(b"7168042", b"7168.042"),
                   warning.replace(b"7168042", b"0x6d600a"),
                   warning.replace(b" ns", b" ns extra"), warning[:-1])
        offset = len(marker) + len(b" CHUNK 1 ") + 59
        for malformed in invalid:
            with self.subTest(warning=malformed), self.assertRaises(ValueError):
                split = list(records)
                split[1] = split[1][:offset] + malformed + split[1][offset:]
                vm_guest_decode_capture(b"\n".join(split) + b"\n", token)

    def test_capture_hrtimer_normalization_preserves_transfer_integrity_gates(self):
        token = "1" * 32
        marker = ("WB_FRAME_" + token).encode()
        raw = b"a" * 60
        encoded = base64.b64encode(raw)
        meta = marker + b" META 60 " + hashlib.sha256(raw).hexdigest().encode()
        one, two = marker + b" CHUNK 1 " + encoded[:76], marker + b" CHUNK 2 " + encoded[76:]
        end = marker + b" END 2"
        warning = b"[   66.820751] hrtimer: interrupt took 7168042 ns\r\n"
        # Normalization cannot repair malformed framing or changed image bytes.
        for records in ([meta, one, end], [meta, two, one, end], [meta, one, one, two, end],
                        [meta, one, two], [meta.replace(b"META 60", b"META 61"), one, two, end],
                        [meta[:-1] + b"0", one, two, end], [meta, one[:-1] + b"*", two, end],
                        [meta, one[:-1] + b"B", two, end], [meta, one, two, end, end],
                        [meta, one, two, marker + b" END 3"]):
            with self.subTest(records=records), self.assertRaises(ValueError):
                packet = b"\r\n".join(records) + b"\r\n"
                packet = packet.replace(b" META ", b" ME" + warning + b"TA ", 1)
                vm_guest_decode_capture(packet, token)
        valid = b"\r\n".join((meta, one, two, end)) + b"\r\n"
        valid = valid.replace(b" META ", b" ME" + warning + b"TA ", 1)
        with self.assertRaisesRegex(ValueError, "token"):
            vm_guest_decode_capture(valid, "$(invalid)")

    def test_capture_hrtimer_retained_serial_regression_when_private_evidence_exists(self):
        # Raw VM captures stay private. Synthetic cases above always run; this
        # optional replay checks the exact retained failure without persisting PNG.
        serial = (Path(__file__).resolve().parents[1] /
                  "work/vm/interactive-hardware-simulation-20261116/runtime/"
                  "session-1795152147678734000/runs/1795152223549198000/serial.log")
        if not serial.is_file():
            self.skipTest("private 0.2.39 failure serial is not present")
        data = serial.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "f27cd925704844340c71c4b68fe92d871d2a43700c94ee2560e6844152cd20e7")
        self.assertEqual(data.count(b"[   66.820751] hrtimer: interrupt took 7168042 ns\r\n"), 1)
        raw = vm_guest_decode_capture(data, "38a1aaeb36d24b37b247a55e76a1edf4")
        self.assertEqual(len(raw), 177691)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "b316a82a1f8f726163c55705d6d6522603cbf9fbb3bb5b85a9d247876e0b9a83")

    def test_capture_rejects_oversized_and_invalid_identity(self):
        token = "c" * 32
        marker = ("WB_FRAME_" + token).encode()
        with self.assertRaisesRegex(ValueError, "size exceeds"):
            vm_guest_decode_capture(marker + b" META 4194305 " + b"0" * 64, token)
        with self.assertRaisesRegex(ValueError, "transcript exceeds"):
            vm_guest_decode_capture(b"x" * (24 * 1024 * 1024 + 1), token)
        raw = b"12345"
        payload = (marker + b" META 5 " + hashlib.sha256(raw).hexdigest().encode() + b"\n" +
                   marker + b" CHUNK 1 " + base64.b64encode(raw) + b"\n" + marker + b" END 1\n")
        with mock.patch("vm_workbench.guest_shell._MAX_ENCODED", 4):
            with self.assertRaisesRegex(ValueError, "encoded capture exceeds"):
                vm_guest_decode_capture(payload, token)
        with self.assertRaisesRegex(ValueError, "token"):
            vm_guest_decode_capture(b"", "$(invalid)")

    def test_key_down_up_is_one_tap_and_unmatched_release_fails(self):
        backend = Backend()
        adapter = KeyboardTapBackend(backend)
        self.assertEqual(adapter.send_key(action="press", key="KeyA").state, "pending")
        self.assertEqual(adapter.send_key(action="press", key="KeyA").state, "duplicate")
        self.assertTrue(adapter.send_key(action="release", key="KeyA").accepted)
        self.assertEqual([item["action"] for item in backend.calls], ["tap"])
        self.assertEqual(adapter.send_key(action="release", key="KeyA").state, "error")

    def test_existing_clone_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch("vm_workbench.cli.OUTPUT", Path(temp)):
                existing = Path(temp) / "existing"
                existing.mkdir()
                with self.assertRaisesRegex(ValueError, "new direct child"):
                    vm_workbench_prepare(existing)

    def test_serial_framing_and_mailbox_rejects_shell_text(self):
        with tempfile.TemporaryDirectory() as temp:
            proc = subprocess.Popen([PIPEFAIL_SHELL], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            bridge = GuestShell(proc, Path(temp) / "serial.log", lambda *args: None)
            try:
                self.assertEqual(bridge._run("printf 'fixture'", 3), b"fixture")
                with self.assertRaises(ValueError):
                    bridge.publish_input("seq 1 click 1 2; reboot\n")
                with self.assertRaises(ValueError):
                    bridge.publish_simulator("test SET debug_count 1; reboot\n")
                with self.assertRaises(ValueError):
                    bridge.publish_simulator("test SET parking_status 2\n")
            finally:
                proc.terminate()
                proc.wait(timeout=5)
                proc.stdin.close()
                bridge.close()
                proc.stdout.close()


if __name__ == "__main__":
    unittest.main()
