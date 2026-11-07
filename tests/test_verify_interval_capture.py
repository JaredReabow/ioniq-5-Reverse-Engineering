from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/uk_fw/verify_interval_capture.py"

spec = importlib.util.spec_from_file_location("verify_interval_capture", TOOL_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
# A @dataclass resolves its own module through sys.modules while decorating, so the module must
# be registered before exec_module or dataclasses raises AttributeError on None.
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

# Real measured values from the retained runs, docs/kernel/42 Findings 3 and 5.
BOOT58_FIRST_TS = "637916.158"
BOOT58_LAST_TS = "824425.000"
BOOT58_WINDOW_MS = 186509
BOOT58_HOME_OFFSET_MS = 186397

BOOT65_FIRST_TS = "1233868.000"
BOOT65_LAST_TS = "1397571.000"
BOOT65_WINDOW_MS = 163703


def receipt(
    *,
    algo: str = "sha256",
    digest: str = "a" * 64,
    binding: str = "pinned_pid_and_starttime",
    closed: bool = True,
    first_ts: str | None = BOOT58_FIRST_TS,
    last_ts: str | None = BOOT58_LAST_TS,
) -> str:
    lines = [
        "RECEIPT v1",
        f"SELF path=/interval-capture.sh algo={algo} digest={digest}",
        "GEN_COUNT count=1 app=AppHomeScreen",
        f"TARGET generation=1 pid=2667 starttime=12345 binding={binding}",
        f"CAPTURE file=/tmp/weston-real.log bytes=1000 digest=deadbeef "
        f"first_ts={first_ts or 'none'} last_ts={last_ts or 'none'} b64_len=1336 seq=1",
        f"SNAPSHOT_CLOSED bytes=1000 decoded=1000 match={'yes' if closed else 'no'}",
        "OUTCOME CAPTURED bytes=1000 generation=1",
    ]
    return "\n".join(lines) + "\n"


class TestTimestampConversion(unittest.TestCase):
    def test_weston_timestamp_whole_part_is_milliseconds(self) -> None:
        # The whole part is already ms; the decimals are sub-ms. Getting this wrong rescales
        # every verdict by 1000x, which is why the assertion is explicit.
        self.assertEqual(mod._ts_to_ms("824313.371"), 824313)

    def test_fraction_does_not_change_the_millisecond_value(self) -> None:
        self.assertEqual(mod._ts_to_ms("100.5"), 100)
        self.assertEqual(mod._ts_to_ms("100.999"), 100)

    def test_unparseable_returns_none(self) -> None:
        self.assertIsNone(mod._ts_to_ms("none"))
        self.assertIsNone(mod._ts_to_ms(""))


class TestRealRunReproduction(unittest.TestCase):
    """The decisive regression: the verifier must reproduce the boot58/boot65 verdicts."""

    def test_boot58_shape_reports_present(self) -> None:
        # boot58's window reached its own registration, which sits 112 ms before the end.
        r = mod.parse_receipt(receipt())
        self.assertEqual(r.window_ms, BOOT58_WINDOW_MS)
        outcome, _ = mod.decide(r, "create_hmi_client(1, 1006, \"AppHomeScreen\")", "AppHomeScreen", BOOT58_HOME_OFFSET_MS)
        self.assertEqual(outcome, mod.REGISTRATION_PRESENT)

    def test_boot65_shape_is_truncated_not_absent(self) -> None:
        # This is the whole point of the tool. boot65's window is 163,703 ms against a
        # 186,397 ms milestone offset, so silence must be CAPTURE_TRUNCATED, never a negative.
        r = mod.parse_receipt(receipt(first_ts=BOOT65_FIRST_TS, last_ts=BOOT65_LAST_TS))
        self.assertEqual(r.window_ms, BOOT65_WINDOW_MS)
        outcome, reason = mod.decide(r, "no marker here", "AppHomeScreen", BOOT58_HOME_OFFSET_MS)
        self.assertEqual(outcome, mod.CAPTURE_TRUNCATED)
        self.assertIn("22694", reason)


class TestHarnessGates(unittest.TestCase):
    def test_missing_digest_blocks_conclusion(self) -> None:
        r = mod.parse_receipt(receipt(algo="none", digest="none"))
        outcome, _ = mod.decide(r, "AppHomeScreen", "AppHomeScreen", 186397)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)

    def test_name_only_binding_blocks_conclusion(self) -> None:
        r = mod.parse_receipt(receipt(binding="name_only"))
        outcome, _ = mod.decide(r, "AppHomeScreen", "AppHomeScreen", 186397)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)

    def test_unclosed_snapshot_blocks_conclusion(self) -> None:
        r = mod.parse_receipt(receipt(closed=False))
        outcome, _ = mod.decide(r, "AppHomeScreen", "AppHomeScreen", 186397)
        self.assertEqual(outcome, mod.SNAPSHOT_NOT_CLOSED)

    def test_no_timestamps_blocks_conclusion(self) -> None:
        r = mod.parse_receipt(receipt(first_ts=None, last_ts=None))
        outcome, _ = mod.decide(r, "AppHomeScreen", "AppHomeScreen", 186397)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)

    def test_gate_order_prefers_harness_over_presence(self) -> None:
        # A present marker in an unidentifiable harness is still not a valid measurement.
        r = mod.parse_receipt(receipt(algo="none", digest="none"))
        outcome, _ = mod.decide(r, "AppHomeScreen", "AppHomeScreen", 186397)
        self.assertEqual(outcome, mod.HARNESS_MISMATCH)


class TestAbsenceRequiresWindow(unittest.TestCase):
    def test_absence_without_offset_is_not_a_negative(self) -> None:
        r = mod.parse_receipt(receipt())
        outcome, _ = mod.decide(r, "no marker", "AppHomeScreen", None)
        self.assertEqual(outcome, mod.CAPTURE_TRUNCATED)

    def test_absence_with_sufficient_window_is_absent(self) -> None:
        r = mod.parse_receipt(receipt())
        outcome, _ = mod.decide(r, "no marker", "AppHomeScreen", 180000)
        self.assertEqual(outcome, mod.REGISTRATION_ABSENT)

    def test_window_exactly_at_offset_counts_as_reaching_it(self) -> None:
        r = mod.parse_receipt(receipt())
        outcome, _ = mod.decide(r, "no marker", "AppHomeScreen", BOOT58_WINDOW_MS)
        self.assertEqual(outcome, mod.REGISTRATION_ABSENT)

    def test_window_one_ms_short_is_truncated(self) -> None:
        r = mod.parse_receipt(receipt())
        outcome, _ = mod.decide(r, "no marker", "AppHomeScreen", BOOT58_WINDOW_MS + 1)
        self.assertEqual(outcome, mod.CAPTURE_TRUNCATED)


class TestExitCodes(unittest.TestCase):
    def test_every_outcome_has_a_distinct_exit_code(self) -> None:
        self.assertEqual(len(mod.EXIT), 5)
        self.assertEqual(len(set(mod.EXIT.values())), 5)

    def test_present_is_zero(self) -> None:
        self.assertEqual(mod.EXIT[mod.REGISTRATION_PRESENT], 0)


if __name__ == "__main__":
    unittest.main()
