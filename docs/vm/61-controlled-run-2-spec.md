# Controlled run 2 — specification, fixed before launch

Date: 2026-11-08. Committed **before** run 2 starts. These values may not be tuned afterwards.

Run 1 (`docs/vm/60-controlled-run-1-result.md`) left three things unresolved and exposed one design
conflict. This specification addresses them, and it changes one number from run 1 — which is exactly
the kind of change that must be declared in advance and justified, not made after seeing a failure.

## What run 1 established

| Finding | Status |
|---|---|
| One `AppHomeScreen` process, `pid 2318 starttime 9042`, first seen 90.89 s | measured |
| Alive 11 of 24 samples; last alive 151.49 s, first dead 156.92 s | measured |
| Export refused with `BINDING_FAILED reason=pid_not_running` | measured |
| Registration / rendering / interactivity | **unresolved** |
| Why the process exited | **not established** |

## The design conflict run 1 exposed

Run 1 fixed `PERSIST_S=120` and `SETTLE_S=20`, so the export took its snapshot ~140 s after first
sight of the process. The process died ~66 s after first sight. The export therefore *could not* have
found a marker, whatever the truth about registration.

That is not an argument for shortening the interval. The two questions are different and were
conflated:

- **"Did the app register with the compositor?"** — needs a snapshot while the process is alive.
- **"Did it persist across 120 s?"** — needs observation across the whole interval.

Run 2 separates them. The export happens at a pre-committed **early** point; persistence remains the
runtime channel's job over the full interval.

## Values fixed before launch

| Constant | Value | Why this value |
|---|---:|---|
| `EXPORT_AT_S` | **30** | after first sight of the process. Run 1 put the export at ~140 s and the process died at ~66 s, so a marker was arithmetically impossible. 30 s is inside the observed lifetime and is declared now, not chosen from run 1's failure |
| `PERSIST_S` | **120** | unchanged from run 1 — this is the persistence question and it must not move |
| `SAMPLE_S` | **5** | unchanged (24 samples) |
| display capture | at **+10 s, +60 s, +110 s** after first sight | three pre-declared points inside and beyond the observed lifetime |
| display tool | `/usr/libexec/weston-screenshooter` | confirmed present in the staged image (`debugfs stat`); writes `/tmp/wayland-screenshot.png`, invoked with `busybox timeout 25` as earlier retained drivers did |
| display channel | the **runtime** channel (`ttyS2`) | only four UARTs exist (`ttyS0`–`ttyS3`); `ttyS3` must stay pristine for the export transaction. PNGs are base64-framed between explicit markers so the noise is parseable |
| marker | `create_hmi_client\([^)]*"AppHomeScreen"` | unchanged |
| milestone reference | 96,445 ms after the first `create_hmi_client` | unchanged (`docs/kernel/43`) |
| SDHCI compat | **`--no-compat`** | see below — still not independently justified |

### On `--no-compat`

Run 1 used it because the gdb patch never completed and `vm_boot` caps that socket at 30 s. The guest
mounted `mmcblk0p16` and reached systemd anyway, which is *suggestive* that the patch is unnecessary
for this image, not proof. Run 2 keeps `--no-compat` and treats it as a **stated limitation**: an
image that boots without a patch is not the same as an image that does not need it. Justifying it
properly needs an A/B comparison, which is a separate experiment and is not smuggled into this one.

## What each channel may claim in run 2

**Export channel (`ttyS3`)** — the frozen harness, one invocation at `EXPORT_AT_S = 30`. Yields only
the narrow claim from `docs/planning/astra-c11.md`. Critically, `REGISTRATION_PRESENT` would mean *a
marker of the registration form was present in a closed, identified capture* — it would **not** mean
Home persisted, and it would not be a "generation-attributed" capture.

**Runtime channel (`ttyS2`)** — generation records, 24 liveness samples, three display captures, and
the persistence result. This is the only channel that may speak about behaviour.

## Pre-committed reading of each outcome

| Export | Runtime | Display | Report |
|---|---|---|---|
| `REGISTRATION_PRESENT` | alive 24/24 | frames non-blank at +60 and +110 | marker present, process persisted, rendering observed; interactivity still unresolved |
| `REGISTRATION_PRESENT` | dies mid-interval | frames exist before death | marker present **and** the process did **not** persist; state the death sample |
| `CAPTURE_TRUNCATED` | any | any | **unresolved** — window too short; never a negative |
| `REGISTRATION_ABSENT` | any | any | the marker was not present **within this payload**, provided the precursor was reached; do not generalise beyond it |
| `BINDING_FAILED` / other instrument failure | any | any | **no conclusion about Home**; report the instrument failure |
| any | any | no frames or all-blank | rendering **unresolved**, and say so — a blank frame is not evidence of a blank screen |

A blank or missing frame is not a negative result about the UI. It is a statement about the capture.

## Still out of scope for run 2

- **Interactivity.** Needs an input injection path and a recorded response. The image has
  `/weston-vm-input.so`, but no input-injection method is yet qualified. Run 2 must not claim
  interactivity.
- **The 120 s persistence question for the *UI*.** Run 2 measures process lifetime; a live process is
  not a rendered, persistent Home screen.

## Prerequisites before launch

1. Extend the driver with `EXPORT_AT_S` and the three display captures, with tests. The driver is
   tracked, so its new SHA-256 goes into a freshly generated manifest — the frozen *harness*
   (`interval-capture.sh`, `verify_interval_capture.py`) is not touched.
2. Re-stage into a **new** CoW clone (`ws-run62`), never reusing `ws-run61`.
3. Confirm `/usr/libexec/weston-screenshooter` is present in that clone's `p5.img`.
4. Retain: driver and helper bytes as staged, manifest, raw receipt, received payload, verifier
   result, runtime channel including framed PNGs, serial log.
