#!/usr/bin/env python3.13
"""verify_interval_capture.py - decide the per-cause outcome of an interval capture.

This is precondition 5 of docs/kernel/42. The guest-side wrapper
(tools/uk_fw/guest/interval-capture.sh) deliberately refuses to judge its own capture; it only
reports what it can prove. This verifier converts a receipt into one of six named outcomes.

REVISION 2. The first version was rejected by Opus 4.7 (docs/planning/opus-4-7-c8.md) for four
defects, all of which are fixed here:

  1. TS_RE was defined and never used, so the window bounds were taken from the receipt instead of
     re-derived from the log. That reproduced the boot65 defect inside the verifier: a guest that
     measured an unbounded region could lie and be believed. The bounds are now re-derived from the
     log, monotonicity is asserted, and any disagreement with the receipt is HARNESS_MISMATCH.
  2. There was no binding between --log and --receipt, so boot58's log could be paired with boot65's
     receipt. The log is now re-digested and must equal the receipt's declared CAPTURE digest.
  3. The marker was a bare substring, so `AppHomeScreenController`, `/app/bin/AppHomeScreen` and
     `killed AppHomeScreen` would all have read as a successful registration. The marker now has to
     match a supplied regular expression, defaulting to the registration grammar.
  4. The milestone was an absolute offset copied from a previous run, which imposes one run's pacing
     on another. It is now anchored to an in-stream PRECURSOR event, with the absolute offset demoted
     to an optional sanity floor.

Outcomes:

    LOG_RECEIPT_MISMATCH  --log and --receipt do not describe the same capture
    HARNESS_MISMATCH      harness identity, generation binding, or timestamp integrity unproven
    SNAPSHOT_NOT_CLOSED   export did not round-trip to the measured size
    CAPTURE_TRUNCATED     the precursor was not reached, so silence means nothing
    REGISTRATION_ABSENT   precursor reached, window reached the milestone, marker absent
    REGISTRATION_PRESENT  the marker matched the structured pattern

Exit status: 0 PRESENT, 10 ABSENT, 11 TRUNCATED, 20 HARNESS_MISMATCH, 21 SNAPSHOT_NOT_CLOSED,
22 LOG_RECEIPT_MISMATCH, 2 usage/parse error.

Usage:
    verify_interval_capture.py --receipt r.txt --log interval.bin --marker AppHomeScreen \\
        --precursor 'create_hmi_client' --milestone-after-precursor-ms 96445
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass, field

# Protocol stamps look like [824313.371]. The whole part is ALREADY milliseconds and the three
# decimals are sub-millisecond resolution. Reading the whole part as seconds rescales every verdict
# by 1000x; see docs/kernel/43 for the cross-check that pins the unit.
TS_RE = re.compile(rb"^\[(\d+)\.(\d+)\]", re.MULTILINE)

# The observed registration form is:
#   ...create_hmi_client(1, 1006, "AppHomeScreen", new id ivi_hmi_client@21)
# so the name is followed by a comma and further arguments, not by the closing paren. A first draft
# required "NAME" immediately before ')' and therefore reported REGISTRATION_ABSENT against the only
# real positive this project has (boot58). Caught by running the verifier against the retained log
# rather than only against synthetic fixtures. The pattern now requires the call and the quoted name,
# and tolerates trailing arguments; it still cannot match a class name, a path, or a death notice,
# because those do not appear inside a create_hmi_client( ... ) call.
DEFAULT_MARKER_PATTERN = r'create_hmi_client\([^)]*"{marker}"'

LOG_RECEIPT_MISMATCH = "LOG_RECEIPT_MISMATCH"
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
    LOG_RECEIPT_MISMATCH: 22,
}


@dataclass
class Receipt:
    self_algo: str | None = None
    self_digest: str | None = None
    gen_count: int | None = None
    target_binding: str | None = None
    capture_bytes: int | None = None
    capture_digest: str | None = None
    first_ts_ms: int | None = None
    last_ts_ms: int | None = None
    snapshot_closed: bool = False
    outcomes: list[str] = field(default_factory=list)

    @property
    def window_ms(self) -> int | None:
        if self.first_ts_ms is None or self.last_ts_ms is None:
            return None
        return self.last_ts_ms - self.first_ts_ms


def _ts_to_ms(whole: bytes) -> int:
    """Whole part of a protocol stamp, which is already milliseconds."""
    return int(whole)


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
            r.capture_digest = meta.get("digest")
            r.first_ts_ms = _meta_ts(meta.get("first_ts"))
            r.last_ts_ms = _meta_ts(meta.get("last_ts"))
        elif line.startswith("SNAPSHOT_CLOSED "):
            r.snapshot_closed = _kv(line[16:]).get("match") == "yes"
        elif line.startswith("OUTCOME "):
            r.outcomes.append(line[8:].strip())
    return r


def _meta_ts(value: str | None) -> int | None:
    if not value or value == "none":
        return None
    try:
        return int(value.split(".", 1)[0])
    except ValueError:
        return None


def _kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for token in text.split():
        if "=" in token:
            k, v = token.split("=", 1)
            out[k] = v
    return out


def ts_bounds_from_log(log_bytes: bytes) -> tuple[int, int] | None:
    """Re-derive the first and last protocol stamps from the log itself.

    Returns None when the log carries no stamps or when the stamps are not non-decreasing, because a
    window derived from a non-monotonic stream is meaningless rather than merely imprecise.
    """
    stamps = [_ts_to_ms(m.group(1)) for m in TS_RE.finditer(log_bytes)]
    if not stamps:
        return None
    if any(b < a for a, b in zip(stamps, stamps[1:])):
        return None
    return stamps[0], stamps[-1]


def first_match_offset_ms(log_bytes: bytes, pattern: bytes) -> int | None:
    """Offset from the stream start to the first match of `pattern`, in protocol ms."""
    m = pattern.search(log_bytes)
    if m is None:
        return None
    head = log_bytes[: m.start()]
    stamps = list(TS_RE.finditer(head))
    if not stamps:
        return None
    return _ts_to_ms(stamps[-1].group(1)) - _ts_to_ms(TS_RE.search(log_bytes).group(1))


def decide(
    receipt: Receipt,
    log_bytes: bytes,
    marker_pattern: re.Pattern[bytes],
    precursor_pattern: re.Pattern[bytes] | None,
    milestone_after_precursor_ms: int | None,
    milestone_offset_ms: int | None = None,
) -> tuple[str, str]:
    """Return (outcome, reason). Prove the instrument, then believe its answer."""

    # Gate 0: do --log and --receipt describe the same capture at all?
    actual_digest = hashlib.sha256(log_bytes).hexdigest()
    if receipt.capture_digest and receipt.capture_digest != "none":
        if receipt.capture_digest != actual_digest:
            return LOG_RECEIPT_MISMATCH, (
                f"receipt declares capture digest {receipt.capture_digest[:16]}… but --log hashes to "
                f"{actual_digest[:16]}…; these arguments describe different captures"
            )
    if receipt.capture_bytes is not None and receipt.capture_bytes != len(log_bytes):
        return LOG_RECEIPT_MISMATCH, (
            f"receipt declares {receipt.capture_bytes} bytes but --log is {len(log_bytes)} bytes"
        )

    # Gate 1: harness identity and generation binding.
    if receipt.self_algo in (None, "", "none") or not receipt.self_digest or receipt.self_digest == "none":
        return HARNESS_MISMATCH, "harness digest unavailable, so the run cannot be attributed to a script"
    if receipt.target_binding != "pinned_pid_and_starttime":
        return HARNESS_MISMATCH, (
            f"capture bound by {receipt.target_binding or 'nothing'}, not a pinned (pid, starttime)"
        )

    # Gate 2: timestamp integrity, re-derived from the log and cross-checked against the receipt.
    bounds = ts_bounds_from_log(log_bytes)
    if bounds is None:
        return HARNESS_MISMATCH, "log carries no protocol timestamps, or its stamps are not monotonic"
    log_first, log_last = bounds
    if receipt.first_ts_ms is not None and receipt.first_ts_ms != log_first:
        return HARNESS_MISMATCH, (
            f"receipt first_ts={receipt.first_ts_ms} disagrees with the log's first stamp {log_first}; "
            "the window bounds were not derived from these bytes"
        )
    if receipt.last_ts_ms is not None and receipt.last_ts_ms != log_last:
        return HARNESS_MISMATCH, (
            f"receipt last_ts={receipt.last_ts_ms} disagrees with the log's last stamp {log_last}"
        )
    window = log_last - log_first
    if window < 0:
        return HARNESS_MISMATCH, f"non-monotonic window of {window} ms"

    # Gate 3: snapshot closure.
    if not receipt.snapshot_closed:
        present_note = ""
        if marker_pattern.search(log_bytes):
            present_note = " Note: the marker pattern IS present in this unclosed capture; it is being discarded."
        return SNAPSHOT_NOT_CLOSED, f"export did not round-trip to the measured size.{present_note}"

    # Gate 4: did the run reach the stage at which the milestone is even possible?
    if precursor_pattern is None:
        return CAPTURE_TRUNCATED, (
            "no precursor pattern supplied, so the capture cannot be shown to have reached the "
            "stage at which the marker would occur"
        )
    prec_offset = first_match_offset_ms(log_bytes, precursor_pattern)
    if prec_offset is None:
        return CAPTURE_TRUNCATED, (
            "precursor absent: the run never reached the stage that precedes the marker, so the "
            "marker's absence carries no information"
        )

    # Gate 5: presence, matched against the structured pattern rather than a bare substring.
    if marker_pattern.search(log_bytes):
        return REGISTRATION_PRESENT, (
            f"marker matched {marker_pattern.pattern.decode()!r} inside a closed, identified capture "
            f"(precursor at {prec_offset} ms)"
        )

    # Gate 6: absence becomes a negative ONLY when the window has demonstrably passed the milestone,
    # measured from the in-stream precursor.
    #
    # The absolute offset deliberately has no decision role. Opus 4.7 (docs/planning/opus-4-7-c8.md)
    # required it be demoted to a sanity floor, and an early draft of this revision still let it
    # decide when no precursor-relative figure was supplied — an internal test caught that, because
    # it meant an operator could restore exactly the criterion the review rejected by passing one
    # flag. If the precursor-relative reference is absent, the honest answer is "cannot decide".
    tail_after_precursor = window - prec_offset
    if milestone_after_precursor_ms is None:
        return CAPTURE_TRUNCATED, (
            f"marker absent and no --milestone-after-precursor-ms reference supplied, so the "
            f"{tail_after_precursor} ms of tail after the precursor cannot be shown to reach the "
            "stage at which the marker would occur"
        )
    if tail_after_precursor < milestone_after_precursor_ms:
        return CAPTURE_TRUNCATED, (
            f"marker absent and the capture extends {tail_after_precursor} ms past the precursor, "
            f"{milestone_after_precursor_ms - tail_after_precursor} ms short of the "
            f"{milestone_after_precursor_ms} ms milestone reference"
        )

    note = ""
    if milestone_offset_ms is not None:
        note = (
            f" (an absolute offset of {milestone_offset_ms} ms was also supplied but is not used as "
            "the deciding criterion)"
        )
    return REGISTRATION_ABSENT, (
        f"precursor observed at {prec_offset} ms and the capture extends {tail_after_precursor} ms past it, "
        f"reaching the {milestone_after_precursor_ms} ms milestone reference, yet the marker pattern is "
        f"absent{note}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--receipt", required=True, help="receipt text emitted by interval-capture.sh")
    ap.add_argument("--log", required=True, help="decoded interval log (read as bytes)")
    ap.add_argument("--marker", required=True, help="app name whose registration is under test")
    ap.add_argument(
        "--marker-pattern",
        default=None,
        help="regex for a positive match; default is the registration grammar create_hmi_client(…\"NAME\")",
    )
    ap.add_argument(
        "--precursor",
        default=r"create_hmi_client",
        help="regex for an event that necessarily precedes the marker; empty string disables",
    )
    ap.add_argument(
        "--milestone-after-precursor-ms",
        type=int,
        default=None,
        help="protocol-ms after the precursor at which the marker is expected",
    )
    ap.add_argument(
        "--milestone-offset-ms",
        type=int,
        default=None,
        help="protocol-ms from stream start; sanity floor only, not the deciding criterion",
    )
    args = ap.parse_args(argv)

    try:
        with open(args.receipt, encoding="utf-8", errors="replace") as fh:
            receipt_text = fh.read()
    except OSError as exc:
        print(f"error: cannot read receipt: {exc}", file=sys.stderr)
        return 2
    try:
        with open(args.log, "rb") as fh:
            log_bytes = fh.read()
    except OSError as exc:
        print(f"error: cannot read log: {exc}", file=sys.stderr)
        return 2

    marker_src = args.marker_pattern or DEFAULT_MARKER_PATTERN.format(marker=re.escape(args.marker))
    try:
        marker_pattern = re.compile(marker_src.encode())
    except re.error as exc:
        print(f"error: bad --marker-pattern: {exc}", file=sys.stderr)
        return 2
    precursor_pattern = None
    if args.precursor:
        try:
            precursor_pattern = re.compile(args.precursor.encode())
        except re.error as exc:
            print(f"error: bad --precursor: {exc}", file=sys.stderr)
            return 2

    receipt = parse_receipt(receipt_text)
    outcome, reason = decide(
        receipt,
        log_bytes,
        marker_pattern,
        precursor_pattern,
        args.milestone_after_precursor_ms,
        args.milestone_offset_ms,
    )
    print(f"{outcome} {reason}")
    return EXIT[outcome]


if __name__ == "__main__":
    sys.exit(main())
