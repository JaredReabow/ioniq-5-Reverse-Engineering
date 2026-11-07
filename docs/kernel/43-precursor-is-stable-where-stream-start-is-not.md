# The precursor is stable where the stream start is not: 663 ms of drift

Date: 2026-11-08. Offline measurement on the two retained captures. No QEMU.

This document exists because both reviewers of the capture harness independently rejected the
criterion it used, and both demanded the same replacement: a milestone must be judged against an
**in-stream precursor event**, not against a wall-clock offset copied from a previous run. This is
the measurement showing that such a precursor exists in the retained data.

## Why the absolute offset is the wrong reference

The original harness compared a capture's whole-window length against `milestone_offset_ms`, where
the offset was measured from the **first line of the protocol stream**. That origin is arbitrary: it
is whenever the logger happened to open and begin capturing, which depends on compositor start
timing, log buffering and boot load. A window measured from an arbitrary origin cannot be compared
across runs.

`docs/planning/opus-4-7-c8.md` states the consequence: the rule conflates "enough protocol-ms
elapsed" with "the system reached the stage at which registration occurs".

## The measurement

All values are milliseconds on the protocol stream's own clock, and offsets are relative to that
run's first captured event.

| Event | boot58 | boot65 |
|---|---:|---:|
| stream start | 637,916 | 1,233,868 |
| stream end | 824,425 | 1,397,571 |
| **first `create_hmi_client`** | **727,868** | **1,323,157** |
| first `surface_create(30000)` | 637,948 | 1,233,897 |
| `create_hmi_client(… "AppHomeScreen")` | 824,313 | absent |
| window length | 186,509 | 163,703 |

Expressed as offsets from each run's stream start:

| Offset from stream start | boot58 | boot65 | drift |
|---|---:|---:|---:|
| first `create_hmi_client` | 89,952 | 89,289 | **663 ms** |
| first `surface_create(30000)` | 32 | 29 | 3 ms |
| `AppHomeScreen` registration | 186,397 | absent | — |

## What this establishes

The first `create_hmi_client` event — the compositor's first HMI-client construction of any kind —
occurs at **89,952 ms** in boot58 and **89,289 ms** in boot65. That is a drift of 663 ms, or 0.7%,
across two runs whose stream origins are unrelated. It is a genuinely comparable reference.

Re-referencing the milestone to that precursor:

| Quantity | Value |
|---|---:|
| registration relative to the precursor (boot58) | **96,445 ms** |
| boot58's stream tail relative to the precursor | 96,557 ms |
| margin by which boot58's positive preceded its own capture end | **112 ms** |
| boot65's tail relative to the precursor | 74,414 ms |
| **shortfall relative to the precursor** | **22,031 ms** |

The 112 ms margin reproduces `docs/kernel/42` Finding 5 exactly, from an independent reference. That
is a useful cross-check: the precursor method is not producing a different story, it is producing the
same story on a reference that survives run-to-run pacing.

The 22,031 ms figure differs from the absolute-offset 22,694 ms by the 663 ms of anchor drift. The
precursor-relative figure is the defensible one.

## What this does NOT establish

- **One precursor pair is not a distribution.** Two runs give one drift measurement. 663 ms is
  evidence that the precursor is far more stable than the stream origin, not a bound on its variance.
  A single run must not be deemed "reached the precursor stage" and then trusted on a 96,445 ms
  budget without further samples.
- **The precursor is stable here, not necessarily causal.** "First HMI-client construction" being
  reproducible does not prove it sits at a fixed point in the application lifecycle; it may be a
  load-dependent coincidence that happens to be tighter than the origin.
- **It does not rescue the closed comparison.** boot65 still ends 22 s before the milestone even on
  the better reference, so `docs/kernel/42`'s conclusion is unchanged.

## Consequence for the harness

Both reviewers required `REGISTRATION_ABSENT` to be reported only when a precursor is observed and
the target marker is not. This measurement supplies the specific precursor to use
(`create_hmi_client` of any client) and the number to test against (96,445 ms after it, to be
re-derived per run rather than hardcoded where possible).

The harness must still treat the precursor as a **floor**, not a licence: observing the precursor
establishes that the run reached HMI-client construction, not that it reached the application's
registration stage.

## Files

- `work/vm/kbuild/ws/runs/1793931162561454000/exported-weston.bin` — boot58 decoded stream.
- `work/vm/kbuild/ws/runs/1793944643111075000/exported-weston.bin` — boot65 decoded stream.
- `docs/kernel/42-boot58-harness-not-retained.md` — Findings 3 and 5, the figures reproduced above.
- `docs/planning/opus-4-7-c8.md`, `docs/planning/astra-c9.md` — the reviews that required this.
