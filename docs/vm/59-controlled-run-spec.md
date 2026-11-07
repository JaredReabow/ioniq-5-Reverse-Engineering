# Controlled run specification — intervals fixed before launch

Date: 2026-11-08. Specification only. **No run has been performed under this spec yet.**

This exists because Astra C11 required that the next piece of work be a controlled run rather than a
fourth revision of the capture harness, and that the run use **two evidence channels** with the
persistence interval **fixed before launch**. Fixed-before-launch means these numbers are committed
now, before any result exists, and are not tuned afterwards.

## Why a new driver was written at all

boot58's fatal flaw was that the script driving it was never retained (`docs/kernel/42`): its sleeps,
poll structure and relaunch logic are unrecoverable, which is why the boot58/boot65 comparison
dead-ended. Any new run that reuses an unretained driver repeats that verdict regardless of result.

So the driver is now a **tracked file**: `tools/uk_fw/guest/interval-run.sh`. It is committed before
the run, and its SHA-256 is recorded in a manifest generated from the actual bytes by
`tools/uk_fw/make_run_manifest.py` — not hand-written, because a hand-written manifest proves nothing
(Astra C10).

## Values fixed before launch

| Constant | Value | Meaning |
|---|---:|---|
| `PERSIST_S` | **120** | persistence observation interval |
| `SAMPLE_S` | **5** | liveness sample period (24 samples over the interval) |
| `SETTLE_S` | **20** | quiet period before the export snapshot |
| generation binding | `(pid, starttime)` | recorded by the driver at first sight, supplied to the helper exactly as recorded |
| marker | `create_hmi_client\([^)]*"AppHomeScreen"` | registration grammar, not a bare substring |
| `--milestone-after-precursor-ms` | **96445** | derived in `docs/kernel/43` from boot58, relative to the first `create_hmi_client` |

These are committed now. If a future run wants different values, it needs its own spec and its own
pre-commitment; it may not retro-fit these.

## The two channels, and what each may claim

### Runtime channel — the only channel that may speak about behaviour

Produced by `interval-run.sh` and retained as raw output:

- `GEN n=… pid=… starttime=… observed_at_cs=…` — each observed generation, recorded at first sight.
- `SAMPLE n=… at_cs=… pid=… starttime=… alive=… same_generation=…` — one line per 5 s.
- `PERSISTENCE_RESULT samples=… alive=… of=… interval_s=120`.
- Continuous display recording over the same window, plus a recorded input and its visible response
  **if** interactivity is claimed.
- An external execution record tying the run to the frozen launch chain.

This channel may support: *the process with this `(pid, starttime)` was alive for N of M samples
across 120 s*, and, if the display recording shows the laid-out Home screen, *Home rendered*.
It may **not** on its own support: *Home registered* (that is the export channel's narrow claim) or
*the UI was interactive* (that needs a recorded input and its response).

### Export channel — narrow claim only

One invocation of the frozen helper with the recorded `(pid, starttime)`. That yields exactly the
narrow claim in `docs/planning/astra-c11.md`, and nothing more.

## Reporting rule, fixed before launch

**Marker presence is an artifact result. Registration, persistence and interaction are separate
runtime conclusions.** Anything the evidence cannot establish is reported as **unresolved** — not
absent, and not a reason to tune the harness.

Specifically, none of these may be written on this run's authority:

- "This is a generation-attributed capture."
- "The manifest proves that the driver ran."
- "This is an atomic snapshot of the compositor log."
- "The capture contains all activity during the observation interval."
- "`REGISTRATION_PRESENT` proves that authentic Home persisted."
- "`REGISTRATION_ABSENT` proves that Home did not register."
- "A truncated window confirms absence."
- "The boot58/boot65 comparison is now attributable."

## Prerequisites, in order

1. Build the frozen pair and confirm identity:
   ```
   python3.13 tools/uk_fw/make_run_manifest.py --run-id interval-r1 \
       --driver tools/uk_fw/guest/interval-run.sh \
       --helper tools/uk_fw/guest/interval-capture.sh \
       --output <stage>/interval-manifest.txt
   ```
   The generator hashes the real bytes; the helper verifies its own digest against the manifest and
   re-verifies the driver's bytes, so a manifest describing different files is refused.
2. Stage into the image: `interval-run.sh`, `interval-capture.sh`, and the generated manifest, then
   the init script that launches the driver. The staging mechanism is the documented `debugfs` path in
   `tools/uk_fw/vm_partimg/inject-stockui.sh`, used with a new stage directory.
3. Boot from a **CoW clone**. The base image is immutable.
4. Retain everything: the driver and helper bytes as staged, the manifest, the raw receipt, the
   received payload, the verifier result, the runtime log, and the display recording.

## What each outcome means, committed in advance

| Export result | Runtime result | Report |
|---|---|---|
| `REGISTRATION_PRESENT` | process alive across the interval, Home visible | registered and persisted; interactivity unresolved unless an input was recorded |
| `REGISTRATION_PRESENT` | process died mid-interval | registered but **not** persisted; state the generation that died |
| `CAPTURE_TRUNCATED` | any | **unresolved** — the window was too short; this is never a negative |
| `REGISTRATION_ABSENT` | any | Home did not register **within this payload**, provided the precursor was reached; do not generalise beyond the payload |
| `HARNESS_MISMATCH` / `SNAPSHOT_NOT_CLOSED` / `RECEIPT_INCOMPLETE` / `LOG_RECEIPT_MISMATCH` | any | **no conclusion about Home**; the instrument failed, report the instrument failure |

## Current status

- Frozen pair: committed. `interval-run.sh` (driver), `interval-capture.sh` (helper),
  `verify_interval_capture.py` (verifier), `make_run_manifest.py` (manifest).
- Tests: `tests/test_interval_capture_script.py`, `tests/test_verify_interval_capture.py`,
  `tests/test_make_run_manifest.py` — including two that run the chain end-to-end on the retained
  boot58/boot65 logs.
- **The run itself has not been performed.** Staging the driver, helper and manifest into the image
  and booting is the next action, and it is the reason this document is a specification rather than a
  result.
