#!/usr/bin/env python3.13
"""verify_interval_capture.py - decide the per-cause outcome of an interval capture.

This is precondition 5 of docs/kernel/42. The guest-side wrapper
(tools/uk_fw/guest/interval-capture.sh) deliberately refuses to judge its own capture; it only
reports what it can prove. This verifier is what converts a receipt into one of five named
outcomes, and it refuses to say REGISTRATION_ABSENT unless the capture window demonstrably
reached the milestone.

The distinction it exists to enforce:

    "AppHomeScreen is absent from the capture"        <- always knowable, cheap
    "AppHomeScreen did not register"                  <- requires the window to reach the milestone

boot65 collapsed those two and produced a confident negative from a stream that ended 22.7 s
short. The third outcome below is the one that would have been correct.

Outcomes (exactly one is printed):

    HARNESS_MISMATCH      harness identity or generation binding is not proven
    SNAPSHOT_NOT_CLOSED   export did not round-trip to the measured size
    CAPTURE_TRUNCATED     window provably ends before the milestone offset
    REGISTRATION_ABSENT   window provably reaches the milestone and the marker is absent
    REGISTRATION_PRESENT  the marker is present

Exit status: 0 REGISTRATION_PRESENT, 10 REGISTRATION_ABSENT, 11 CAPTURE_TRUNCATED,
20 HARNESS_MISMATCH, 21 SNAPSHOT_NOT_CLOSED, 2 usage/parse error.

Usage:
    verify_interval_capture.py --receipt receipt.txt --log decoded-interval.bin \
        --marker 'AppHomeScreen' --milestone-offset-ms 186397
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field

TS_RE = re.compile(r"^\[(\d+)\.(\d+)\]", re.MULTILINE)

HARNESS_MISMATCH = "HARNESS_MISMATCH"
SNAPSHOT_NOT_CLOSED = "SNAPSHOT_NOT_CLOSED"
CAPTURE_TRUNCATED = "CAPTURE_TRUNCATED"
REGISTRATION_ABSENT = "REGISTRATION_ABSENT"
REGISTRATION_PRESENT = "REGISTRATION_PRESENT"

EXIT = {
    REGISTRATION_PRESENT: 0,
    REGISTRATION_ABSENT: 10,
    CAPTURE_TRUNCATED: 11,
    HARNESS_MISMATCH: 20,
    SNAPSHOT_NOT_CLOSED: 21,
}


@dataclass
class Receipt:
    self_algo: str | None = None
    self_digest: str | None = None
    gen_count: int | None = None
    target_binding: str | None = None
    capture_bytes: int | None = None
    first_ts_ms: int | None = None
    last_ts_ms: int | None = None
    snapshot_closed: bool = False
    outcomes: list[str] = field(default_factory=list)

    @property
    def window_ms(self) -> int | None:
        if self.first_ts_ms is None or self.last_ts_ms is None:
            return None
        return self.last_ts_ms - self.first_ts_ms


def _ts_to_ms(text: str) -> int | None:
    """Convert a protocol timestamp like '824313.371' to integer milliseconds.

    UNIT NOTE, because getting this wrong silently rescales every verdict by 1000x: the whole
    part of these stamps is ALREADY milliseconds, and the three decimals are sub-millisecond
    resolution. So '824313.371' is 824,313 ms plus a fraction, not 824,313 seconds.

    Cross-check against the retained runs: boot58 spans 637916.158 to 824425.000. Subtracting
    the whole parts gives 186,509 ms, about 186 seconds, which is consistent with a run whose
    capture phase lasted a few minutes. Treating the whole part as seconds would make the same
    window 51 hours and the comparison meaningless.
    """
    try:
        whole, _frac = text.split(".", 1)
        return int(whole)
    except (ValueError, AttributeError):
        return None


def parse_receipt(text: str) -> Receipt:
    r = Receipt()
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("SELF "):
            meta = _kv(line[5:])
            r.self_algo = meta.get("algo")
            r.self_digest = meta.get("digest")
        elif line.startswith("GEN_COUNT "):
            meta = _kv(line[10:])
            try:
                r.gen_count = int(meta.get("count", ""))
            except ValueError:
                r.gen_count = None
        elif line.startswith("TARGET "):
            r.target_binding = _kv(line[7:]).get("binding")
        elif line.startswith("CAPTURE "):
            meta = _kv(line[8:])
            try:
                r.capture_bytes = int(meta.get("bytes", ""))
            except ValueError:
                r.capture_bytes = None
            r.first_ts_ms = _ts_to_ms(meta["first_ts"]) if meta.get("first_ts", "none") != "none" else None
            r.last_ts_ms = _ts_to_ms(meta["last_ts"]) if meta.get("last_ts", "none") != "none" else None
        elif line.startswith("SNAPSHOT_CLOSED "):
            r.snapshot_closed = _kv(line[16:]).get("match") == "yes"
        elif line.startswith("OUTCOME "):
            r.outcomes.append(line[8:].strip())
    return r


def _kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for token in text.split():
        if "=" in token:
            k, v = token.split("=", 1)
            out[k] = v
    return out


def decide(receipt: Receipt, log_text: str, marker: str, milestone_offset_ms: int | None) -> tuple[str, str]:
    """Return (outcome, reason). Order matters: prove the instrument before believing its answer."""
    # 1. Harness identity. An unidentifiable harness reproduces the boot58 defect exactly.
    if receipt.self_algo in (None, "", "none") or not receipt.self_digest or receipt.self_digest == "none":
        return HARNESS_MISMATCH, "harness digest unavailable, so the run cannot be attributed to a script"

    # 2. Generation binding. Name-only binding cannot distinguish generations, which is how
    #    boot65 ended up reporting a capture pid that matched neither its cold nor its warm pid.
    if receipt.target_binding != "pinned_pid_and_starttime":
        return HARNESS_MISMATCH, f"capture bound by {receipt.target_binding or 'nothing'}, not a pinned (pid, starttime)"

    # 3. Snapshot closure. A streamed file is not a snapshot.
    if not receipt.snapshot_closed:
        return SNAPSHOT_NOT_CLOSED, "export did not round-trip to the measured size"

    # 4. A capture with no parseable protocol timestamps cannot be placed on the timeline.
    if receipt.window_ms is None:
        return HARNESS_MISMATCH, "capture carries no parseable protocol timestamps"

    present = marker in log_text
    if present:
        return REGISTRATION_PRESENT, f"marker {marker!r} found inside a closed, identified capture"

    # 5. The decisive test. Absence only becomes a negative if the window provably reaches the
    #    milestone. Without a stated milestone offset we cannot make that call at all.
    if milestone_offset_ms is None:
        return CAPTURE_TRUNCATED, "marker absent and no milestone offset supplied, so the window cannot be shown to reach it"
    if receipt.window_ms < milestone_offset_ms:
        return CAPTURE_TRUNCATED, (
            f"marker absent but window is {receipt.window_ms} ms, {milestone_offset_ms - receipt.window_ms} ms "
            f"short of the {milestone_offset_ms} ms milestone offset"
        )
    return REGISTRATION_ABSENT, (
        f"marker absent and window is {receipt.window_ms} ms, reaching the {milestone_offset_ms} ms milestone offset"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--receipt", required=True, help="receipt text emitted by interval-capture.sh")
    ap.add_argument("--log", required=True, help="decoded interval log")
    ap.add_argument("--marker", required=True, help="literal marker whose presence is being tested")
    ap.add_argument(
        "--milestone-offset-ms",
        type=int,
        default=None,
        help="protocol-ms offset from stream start at which the marker is expected",
    )
    args = ap.parse_args(argv)

    try:
        with open(args.receipt, encoding="utf-8", errors="replace") as fh:
            receipt_text = fh.read()
    except OSError as exc:
        print(f"error: cannot read receipt: {exc}", file=sys.stderr)
        return 2
    try:
        with open(args.log, encoding="utf-8", errors="replace") as fh:
            log_text = fh.read()
    except OSError as exc:
        print(f"error: cannot read log: {exc}", file=sys.stderr)
        return 2

    receipt = parse_receipt(receipt_text)
    outcome, reason = decide(receipt, log_text, args.marker, args.milestone_offset_ms)
    print(f"{outcome} {reason}")
    return EXIT[outcome]


if __name__ == "__main__":
    sys.exit(main())
