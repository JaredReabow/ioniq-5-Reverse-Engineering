# Opus 4.7 C8 — REJECT: the verifier still trusts the instrument it was built to distrust

Read-only review, 2026-11-08, of `tools/uk_fw/verify_interval_capture.py` and
`tests/test_verify_interval_capture.py` only. Reviewed at commit `38069e6`. No file was written by
the consultation; no QEMU, no git.

Scoped to the verifier alone, with Astra reviewing the guest script in parallel and deliberately
not shared, so the two findings are independent.

## Verdict

**REJECT.** Opus's sharpest observation is a self-inflicted tell:

> `TS_RE` … is defined at module scope and **never used anywhere in the file.** Someone drew that
> check and didn't wire it.

That is accurate. The regex exists precisely so the verifier can re-derive the window bounds from
the log instead of believing the receipt, and it was left dead. The consequence is that the
verifier reproduces the boot65 defect *inside itself*: a guest that computed `first_ts`/`last_ts`
from the unbounded file sails through.

## Answer to the question I asked

**Can `REGISTRATION_ABSENT` ever be safely reported?** Opus: **no — not as specified.** Its reason is
the synthesis point of both reviews:

> Safe reporting requires the "milestone" to be an *intrinsic* predecessor event observable in the
> current stream …, not a wall-clock offset copied from a prior run. Only then does "silence past the
> precursor" become a defensible negative. As written, `REGISTRATION_ABSENT` conflates "enough
> protocol-ms elapsed" with "the system under test reached the stage at which registration would have
> occurred," and those are not the same claim.

## Blocking defects

### 1. Guest-supplied timestamps trusted without cross-check (the most important)

Lines 110–111 read the window bounds from the receipt; nothing validates them against `--log`.
`TS_RE` is unused. Permitted wrong answers:

- a guest that derived bounds from the unbounded file passes silently;
- a truncated log paired with a non-truncated receipt passes;
- a non-monotonic stream yields a bogus `window_ms` with no complaint.

**Fix:** scan `--log` with `TS_RE`, take first and last matches, assert monotonicity, and require
exact agreement with the receipt. Disagreement → `HARNESS_MISMATCH`.

### 2. The milestone offset is a prior-run constant imposed on a different run

`window_ms < milestone_offset_ms` treats a **time budget** as a proxy for a **state milestone**. A
slower run where registration would occur at 220,000 ms passes a 190,000 ms window, finds no marker,
and is reported `REGISTRATION_ABSENT`. That is the exact failure the tool exists to prevent,
reintroduced through an operator-supplied constant.

**Fix:** parameterise with an in-stream **precursor** event that precedes registration. Report
`REGISTRATION_ABSENT` only when the precursor is observed and the target marker is not. Keep the
offset only as a soft sanity floor.

### 3. Bare substring on the log is unsafe grammar

`marker in log_text` is "theatre dressed as a test". Real false positives enumerated:

- `AppHomeScreenController`, `AppHomeScreenHandler`, `AppHomeScreenProxy` — Qt/QML class-name logging;
- paths: `/app/bin/AppHomeScreen`, `exec(/app/bin/AppHomeScreen)`;
- **death notices**: `killed AppHomeScreen pid=…`, `AppHomeScreen exited with signal …`;
- startup registries or app-list dumps;
- quoted errors: `couldn't create AppHomeScreen client: timeout` — an inversion of the truth.

**Fix:** match the registration **grammar**:
`re.search(r'create_hmi_client\([^)]*"AppHomeScreen"\)', log_text)`.

### 4. `target_binding` string equality is self-attestation

The guest writes `binding=pinned_pid_and_starttime`; a guest that bound by name can print the same
string. Equality on a self-reported field is "decoration" until the receipt carries the evidence —
the `pid`/`starttime` pair captured at capture-start — and the verifier re-derives that it existed
and matched.

### 5. No cross-binding between `--log` and `--receipt`

Two independent paths. Nothing stops boot58's log being passed with boot65's receipt. **Fix:**
re-digest `--log` and compare to the receipt's declared `CAPTURE digest`; mismatch is a new
`LOG_RECEIPT_MISMATCH` outcome or folds into `SNAPSHOT_NOT_CLOSED`.

### 6. `errors="replace"` is unsafe on a possibly-binary log

Silently rewrites non-UTF-8 bytes to U+FFFD, which can fabricate or erase substring boundaries.
**Fix:** open as bytes and search for the ASCII-encoded pattern.

### 7. Negative `window_ms` unhandled

A non-monotonic stream makes the window negative, which compares as "less than the milestone" and
silently reports `CAPTURE_TRUNCATED` when the real fault is timestamp integrity. **Fix:** negative or
non-monotonic → `HARNESS_MISMATCH`.

### 8. `_ts_to_ms` truncates the fractional millisecond

Up to ~2 ms of window error, which bites at the exact-boundary test case.

## The uncomfortable corollary, which Opus raised and I accept

> by the author's own evidence, boot58's positive sat 19,494 bytes past its declared length, so a
> strict `SNAPSHOT_NOT_CLOSED` rule would have thrown out the only `AppHomeScreen` observation this
> project has.

That is true and it is the correct trade. The fix is not to relax the gate but to make the discard
**visible**: the reason string should state whether the marker's grammar form was present in an
unclosed capture, so an operator sees what was thrown away instead of it vanishing.

## Gate order

Agreed in principle — prove the instrument before believing its answer, and a marker found through
an unidentified harness is not a measurement. Two corrections:

1. **Log/receipt binding must be gate 0.** Nothing downstream means anything if the two arguments do
   not describe the same capture.
2. **Timestamp sanity must precede any use of `window_ms`.**

Proposed order:

```
0. LOG_RECEIPT_MISMATCH
1. HARNESS_MISMATCH          (SELF digest + binding, with evidence not a label)
2. TIMESTAMP_SANITY          (re-derive from log, assert monotonic, assert agreement)
3. SNAPSHOT_NOT_CLOSED
4. PRECURSOR_PRESENT
5. REGISTRATION_PRESENT      (structured grammar)
6. CAPTURE_TRUNCATED vs REGISTRATION_ABSENT
```

## The one change that matters most

Wire `TS_RE`. Re-derive bounds from the log, assert monotonicity, require exact agreement with the
receipt, reject disagreement as `HARNESS_MISMATCH`.

> Fix that one thing and the tool goes from "stops yesterday's defect only if the guest cooperates"
> to "stops yesterday's defect even when the guest is lying."

## Note on the precursor

Opus and Astra reached the precursor conclusion independently. This session had already measured
that one exists and is stable, before either review landed: the **first `create_hmi_client` event**
occurs at offset 89,952 ms in boot58 and 89,289 ms in boot65 — a 663 ms (0.7%) drift — whereas the
stream-start offsets the absolute rule depends on are arbitrary. See `docs/kernel/43` for the
measurement.
