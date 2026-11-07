"""Tests for tools/uk_fw/verify_interval_capture.py (revision 2).

Revision 1 was rejected by Opus 4.7 (docs/planning/opus-4-7-c8.md). Every blocking finding from that
review has a test here, plus an end-to-end reproduction against the two retained logs when they are
available on this host.
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/uk_fw/verify_interval_capture.py"

spec = importlib.util.spec_from_file_location("verify_interval_capture", TOOL_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
# A @dataclass resolves its own module through sys.modules while decorating, so the module must be
# registered before exec_module or dataclasses raises AttributeError on None.
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

# Real measured values, docs/kernel/42 Findings 3 and 5 and docs/kernel/43.
BOOT58 = dict(run="1793931162561454000", first=637916, last=824425, precursor=89952)
BOOT65 = dict(run="1793944643111075000", first=1233868, last=1397571, precursor=89289)
MILESTONE_AFTER_PRECURSOR = 96445
RUNS_DIR = ROOT / "work/vm/kbuild/ws/runs"

MARKER = re.compile(mod.DEFAULT_MARKER_PATTERN.format(marker="AppHomeScreen").encode())
PRECURSOR = re.compile(b"create_hmi_client")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def receipt_bytes(
    data: bytes,
    *,
    first: int | None,
    last: int | None,
    algo: str = "sha256",
    binding: str = "pinned_pid_and_starttime",
    closed: bool = True,
    digest: str | None = None,
) -> mod.Receipt:
    """Build a Receipt as the guest would emit it, for the given log bytes."""
    lines = [
        "RECEIPT v1",
        f"SELF path=/interval-capture.sh algo={algo} digest={'a' * 64 if algo != 'none' else 'none'}",
        "GEN_COUNT count=1 app=AppHomeScreen",
        f"TARGET generation=1 pid=2667 starttime=12345 binding={binding}",
        f"CAPTURE file=/tmp/weston-real.log bytes={len(data)} digest={digest or _sha(data)} "
        f"first_ts={first if first is not None else 'none'} last_ts={last if last is not None else 'none'}",
        f"SNAPSHOT_CLOSED bytes={len(data)} decoded={len(data)} match={'yes' if closed else 'no'}",
        "OUTCOME CAPTURED",
    ]
    return mod.parse_receipt("\n".join(lines) + "\n")


def log_lines(stamps: list[int], body: str = "") -> bytes:
    return b"".join(f"[{s}.000] {body}\n".encode() for s in stamps)


REGISTRATION_BODY = b'  -> ivi_hmi_requester@18.create_hmi_client(1, 1006, "AppHomeScreen", new id ivi_hmi_client@21)\n'


def registration_line(stamp: int) -> bytes:
    """The exact retained registration form, at a caller-chosen stamp.

    Carrying a fixed stamp was a fixture bug: it made several tests non-monotonic, and the new
    timestamp gate correctly rejected them. That is the gate doing its job, not a reason to weaken
    the gate.
    """
    return b"[%d.000]" % stamp + REGISTRATION_BODY


def decide(r: mod.Receipt, data: bytes, *, precursor=True, ms=MILESTONE_AFTER_PRECURSOR):
    return mod.decide(r, data, MARKER, PRECURSOR if precursor else None, ms)


class TestGate0LogReceiptBinding(unittest.TestCase):
    """Opus finding 5: --log and --receipt were never bound together."""

    def test_wrong_log_is_rejected(self) -> None:
        measured = log_lines([1000, 2000])
        other = log_lines([1000, 2000], body="different content")
        r = receipt_bytes(measured, first=1000, last=2000)
        outcome, reason = decide(r, other)
        self.assertEqual(outcome, mod.LOG_RECEIPT_MISMATCH)
        self.assertIn("different captures", reason)

    def test_byte_count_mismatch_is_rejected(self) -> None:
        measured = log_lines([1000, 2000])
        r = receipt_bytes(measured, first=1000, last=2000)
        outcome, _ = decide(r, measured + b"extra")
        self.assertEqual(outcome, mod.LOG_RECEIPT_MISMATCH)


class TestGate1ReceiptCompleteness(unittest.TestCase):
    """A receipt is appended incrementally, so a killed run leaves one that looks finished.

    SNAPSHOT_CLOSED is written before the payload is appended to the channel, so without a terminal
    line a receipt can declare a closed snapshot that was never transmitted. Found by writing such a
    receipt by hand and observing that it verified as REGISTRATION_PRESENT.
    """

    def test_receipt_without_terminal_outcome_is_incomplete(self) -> None:
        data = b"[1000.000] start\n" + registration_line(1500) + b"[200000.000] end\n"
        text = "".join(
            line + "\n"
            for line in [
                "RECEIPT v2",
                f"SELF path=/x algo=sha256 digest={'a' * 64}",
                "TARGET binding=pinned_pid_and_starttime pid=1 starttime=1",
                f"CAPTURE bytes={len(data)} digest={_sha(data)} first_ts=1000 last_ts=200000",
                f"SNAPSHOT_CLOSED bytes={len(data)} decoded={len(data)} match=yes",
            ]
        )
        r = mod.parse_receipt(text)
        outcome, reason = decide(r, data)
        self.assertEqual(outcome, mod.RECEIPT_INCOMPLETE)
        self.assertIn("exactly one terminal outcome", reason)

    def test_failure_outcome_is_not_a_complete_capture(self) -> None:
        data = b"[1000.000] start\n" + registration_line(1500) + b"[200000.000] end\n"
        text = "".join(
            line + "\n"
            for line in [
                "RECEIPT v2",
                f"SELF path=/x algo=sha256 digest={'a' * 64}",
                "TARGET binding=pinned_pid_and_starttime pid=1 starttime=1",
                f"CAPTURE bytes={len(data)} digest={_sha(data)} first_ts=1000 last_ts=200000",
                f"SNAPSHOT_CLOSED bytes={len(data)} decoded={len(data)} match=yes",
                "OUTCOME CLOCK_UNAVAILABLE reason=cannot_read_uptime",
            ]
        )
        r = mod.parse_receipt(text)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.RECEIPT_INCOMPLETE)

    def _good_block(self, data: bytes) -> str:
        return "".join(
            line + "\n"
            for line in [
                f"SELF path=/x algo=sha256 digest={'a' * 64}",
                "TARGET binding=pinned_pid_and_starttime pid=1 starttime=1",
                f"CAPTURE bytes={len(data)} digest={_sha(data)} first_ts=1000 last_ts=200000",
                f"SNAPSHOT_CLOSED bytes={len(data)} decoded={len(data)} match=yes",
            ]
        )

    def test_stale_captured_from_an_earlier_transaction_does_not_count(self) -> None:
        # The receipt channel is append-only, so an earlier run's terminal line can sit above a later
        # truncated one. Only the last transaction may be considered.
        data = b"[1000.000] start\n" + registration_line(1500) + b"[200000.000] end\n"
        text = (
            "RECEIPT v2 id=old\n"
            + self._good_block(data)
            + "OUTCOME CAPTURED bytes=118\n"
            + "RECEIPT v2 id=new\n"
            + self._good_block(data)
        )
        r = mod.parse_receipt(text)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.RECEIPT_INCOMPLETE)

    def test_captured_followed_by_a_failure_is_incomplete(self) -> None:
        data = b"[1000.000] start\n" + registration_line(1500) + b"[200000.000] end\n"
        text = (
            "RECEIPT v2 id=t\n"
            + self._good_block(data)
            + "OUTCOME CAPTURED bytes=118\n"
            + "OUTCOME EXPORT_FAILED reason=payload_write_failed\n"
        )
        r = mod.parse_receipt(text)
        outcome, reason = decide(r, data)
        self.assertEqual(outcome, mod.RECEIPT_INCOMPLETE)
        self.assertIn("found 2", reason)

    def test_transaction_id_is_captured(self) -> None:
        data = b"[1000.000] start\n" + registration_line(1500) + b"[200000.000] end\n"
        text = "RECEIPT v2 id=run-1-t0c100000\n" + self._good_block(data) + "OUTCOME CAPTURED bytes=1\n"
        r = mod.parse_receipt(text)
        self.assertIn("id=run-1", r.transaction or "")

    def test_complete_receipt_passes_this_gate(self) -> None:
        data = b"[1000.000] start\n" + registration_line(1500) + b"[200000.000] end\n"
        r = receipt_bytes(data, first=1000, last=200000)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.REGISTRATION_PRESENT)


class TestGate2TimestampIntegrity(unittest.TestCase):
    """Opus finding 1: TS_RE was defined and never used."""

    def test_receipt_bounds_are_rederived_not_trusted(self) -> None:
        data = log_lines([1000, 2000])
        # Receipt claims a window far wider than the log actually contains.
        r = receipt_bytes(data, first=1000, last=999999)
        outcome, reason = decide(r, data)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)
        self.assertIn("disagrees with the log", reason)

    def test_first_stamp_disagreement_is_rejected(self) -> None:
        data = log_lines([1000, 2000])
        r = receipt_bytes(data, first=500, last=2000)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)

    def test_non_monotonic_stream_is_rejected(self) -> None:
        data = log_lines([2000, 1000])
        r = receipt_bytes(data, first=2000, last=1000)
        outcome, reason = decide(r, data)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)
        self.assertIn("monotonic", reason)

    def test_no_timestamps_is_rejected(self) -> None:
        data = b"no stamps here\n"
        r = receipt_bytes(data, first=None, last=None)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)


class TestGate3SnapshotClosure(unittest.TestCase):
    def test_unclosed_snapshot_blocks_conclusion(self) -> None:
        data = log_lines([1000, 2000])
        r = receipt_bytes(data, first=1000, last=2000, closed=False)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.SNAPSHOT_NOT_CLOSED)

    def test_unclosed_snapshot_still_reports_what_was_discarded(self) -> None:
        # Opus's corollary: boot58's only positive sat past its declared bound, so a strict rule
        # discards it. It must be visible rather than silent.
        data = b"[1000.000] start\n" + registration_line(1500) + b"[2000.000] end\n"
        r = receipt_bytes(data, first=1000, last=2000, closed=False)
        outcome, reason = decide(r, data)
        self.assertEqual(outcome, mod.SNAPSHOT_NOT_CLOSED)
        self.assertIn("IS present", reason)


class TestGate4Precursor(unittest.TestCase):
    """Opus finding 2 and Astra's concurrence: absolute offsets impose one run's pacing on another."""

    def test_no_precursor_pattern_means_no_negative(self) -> None:
        data = log_lines([1000, 2000])
        r = receipt_bytes(data, first=1000, last=2000)
        outcome, _ = mod.decide(r, data, MARKER, None, MILESTONE_AFTER_PRECURSOR)
        self.assertEqual(outcome, mod.CAPTURE_TRUNCATED)

    def test_missing_precursor_means_no_negative(self) -> None:
        # Premature HMI-client construction never happened; absence of the marker proves nothing.
        data = log_lines([1000, 200000])
        r = receipt_bytes(data, first=1000, last=200000)
        outcome, reason = decide(r, data)
        self.assertEqual(outcome, mod.CAPTURE_TRUNCATED)
        self.assertIn("precursor absent", reason)


class TestGate5StructuredMatch(unittest.TestCase):
    """Opus finding 3: the bare substring was unsafe grammar."""

    def test_death_notice_does_not_read_as_registration(self) -> None:
        data = (
            b"[1000.000]  -> ivi_hmi_requester@18.create_hmi_client(1, 1000, \"Other\", new id x)\n"
            b"[1100.000] killed AppHomeScreen pid=2667\n"
            b"[200000.000] end\n"
        )
        r = receipt_bytes(data, first=1000, last=200000)
        outcome, _ = decide(r, data)
        self.assertNotEqual(outcome, mod.REGISTRATION_PRESENT)
        self.assertEqual(outcome, mod.REGISTRATION_ABSENT)

    def test_path_does_not_read_as_registration(self) -> None:
        data = (
            b"[1000.000]  -> ivi_hmi_requester@18.create_hmi_client(1, 1000, \"Other\", new id x)\n"
            b"[1100.000] exec(/app/bin/AppHomeScreen)\n"
            b"[200000.000] end\n"
        )
        r = receipt_bytes(data, first=1000, last=200000)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.REGISTRATION_ABSENT)

    def test_class_name_does_not_read_as_registration(self) -> None:
        data = (
            b"[1000.000]  -> ivi_hmi_requester@18.create_hmi_client(1, 1000, \"Other\", new id x)\n"
            b"[1100.000] AppHomeScreenController constructed\n"
            b"[200000.000] end\n"
        )
        r = receipt_bytes(data, first=1000, last=200000)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.REGISTRATION_ABSENT)

    def test_real_registration_form_matches(self) -> None:
        # The exact retained form, with trailing arguments before the closing paren.
        data = (
            b"[1000.000]  -> ivi_hmi_requester@18.create_hmi_client(1, 1000, \"Other\", new id x)\n"
            + registration_line(1500)
            + b"[200000.000] end\n"
        )
        r = receipt_bytes(data, first=1000, last=200000)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.REGISTRATION_PRESENT)


class TestGate6AbsenceCriteria(unittest.TestCase):
    def test_absence_with_short_tail_is_truncated(self) -> None:
        # precursor at 1000, window to 51000 -> 50000 ms of tail, milestone 96445
        data = (
            b"[1000.000]  -> create_hmi_client(1, 1000, \"Other\", new id x)\n"
            b"[51000.000] end\n"
        )
        r = receipt_bytes(data, first=1000, last=51000)
        outcome, reason = decide(r, data)
        self.assertEqual(outcome, mod.CAPTURE_TRUNCATED)
        self.assertIn("46445 ms short", reason)

    def test_absence_with_long_enough_tail_is_a_negative(self) -> None:
        start = 1000
        prec = 1000
        end = prec + MILESTONE_AFTER_PRECURSOR
        data = b"".join(
            [
                b"[1000.000]  -> create_hmi_client(1, 1000, \"Other\", new id x)\n",
                f"[{end}.000] end\n".encode(),
            ]
        )
        r = receipt_bytes(data, first=start, last=end)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.REGISTRATION_ABSENT)

    def test_absolute_offset_alone_cannot_produce_a_negative(self) -> None:
        # The absolute offset must never be sufficient. A precursor IS present and the window is
        # long, so the only reason this cannot be a negative is that no precursor-relative
        # reference was supplied.
        data = (
            b"[1000.000]  -> create_hmi_client(1, 1000, \"Other\", new id x)\n"
            b"[500000.000] end\n"
        )
        r = receipt_bytes(data, first=1000, last=500000)
        outcome, reason = mod.decide(r, data, MARKER, PRECURSOR, None, 186397)
        self.assertEqual(outcome, mod.CAPTURE_TRUNCATED)
        self.assertIn("no --milestone-after-precursor-ms", reason)


class TestHarnessGates(unittest.TestCase):
    def test_missing_digest_blocks_conclusion(self) -> None:
        data = b"[1000.000] start\n" + registration_line(1500)
        r = receipt_bytes(data, first=1000, last=1500, algo="none")
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)

    def test_name_only_binding_blocks_conclusion(self) -> None:
        data = b"[1000.000] start\n" + registration_line(1500)
        r = receipt_bytes(data, first=1000, last=1500, binding="name_only")
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)

    def test_harness_outranks_presence(self) -> None:
        data = b"[1000.000] start\n" + registration_line(1500)
        r = receipt_bytes(data, first=1000, last=1500, algo="none")
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)


class TestBinarySafety(unittest.TestCase):
    """Opus finding 6: errors='replace' could fabricate or erase match boundaries."""

    def test_non_utf8_bytes_do_not_break_matching(self) -> None:
        data = (
            b"[1000.000] \xff\xfe garbage \x80\n"
            + registration_line(1500)
            + b"[200000.000] end\n"
        )
        r = receipt_bytes(data, first=1000, last=200000)
        outcome, _ = decide(r, data)
        self.assertEqual(outcome, mod.REGISTRATION_PRESENT)


class TestRealRunReproduction(unittest.TestCase):
    """End-to-end against the two retained logs. The decisive regression."""

    def _receipt_for(self, spec_: dict, data: bytes) -> mod.Receipt:
        return receipt_bytes(data, first=spec_["first"], last=spec_["last"])

    def test_boot58_registration_present(self) -> None:
        path = RUNS_DIR / BOOT58["run"] / "exported-weston.bin"
        if not path.is_file():
            self.skipTest("retained boot58 log not present")
        data = path.read_bytes()
        outcome, _ = decide(self._receipt_for(BOOT58, data), data)
        self.assertEqual(outcome, mod.REGISTRATION_PRESENT)

    def test_boot65_truncated_not_absent(self) -> None:
        path = RUNS_DIR / BOOT65["run"] / "exported-weston.bin"
        if not path.is_file():
            self.skipTest("retained boot65 log not present")
        data = path.read_bytes()
        outcome, reason = decide(self._receipt_for(BOOT65, data), data)
        self.assertEqual(outcome, mod.CAPTURE_TRUNCATED)
        self.assertIn("22031", reason)


class TestExitCodes(unittest.TestCase):
    def test_every_outcome_has_a_distinct_exit_code(self) -> None:
        self.assertEqual(len(mod.EXIT), 7)
        self.assertEqual(len(set(mod.EXIT.values())), 7)

    def test_present_is_zero(self) -> None:
        self.assertEqual(mod.EXIT[mod.REGISTRATION_PRESENT], 0)


if __name__ == "__main__":
    unittest.main()
