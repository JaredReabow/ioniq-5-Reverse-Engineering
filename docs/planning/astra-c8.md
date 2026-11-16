# Astra C8 — no run yet: the boot58 positive sits outside the window the script believed it had measured

Read-only consultation, 2026-11-08, requested after `docs/kernel/41` was drafted. Astra read
`docs/kernel/41`, `docs/planning/astra-c7.md`, `docs/planning/opus-4-7-c7.md`,
`docs/kernel/40-ivi-screen-create-client.md`, `docs/vm/56-endgame-runbook.md`, `docs/kernel/22`,
`docs/kernel/23`, `work/vm/kbuild/boot58-hmi.log`, and `final-run.sh`. No file was written by the
consultation, no QEMU was run. This document records its findings; the recommendations are adopted below
except where noted.

## Decision

**No run.** The scheduled boot78 was paused. Do the bounded offline lifecycle-and-capture audit first.

Astra's own note on its c7: c7 had *already* identified both the screen/layer announcements and the raw
Home-registration difference. Its remaining relevant recommendation was the offline Home lifecycle
comparison. **There is no reason to repeat the nonexistent `screen_create` client search.**

## The finding that changed the decision

The two `exported-weston.bin` exports are not atomic snapshots; `final-run.sh` measures the log and then
streams a still-growing file. Astra measured:

| Export property | boot58 | boot65 |
|---|---:|---:|
| Declared `BEGIN weston` byte length | 234,468 | 227,371 |
| Actual retained decoded length | 277,341 | 229,663 |
| Zero-based byte offset of `AppHomeScreen` | **253,974** | absent |

Boot58's positive occurs **beyond its export's initially declared length**. Astra's reading: this does not
invalidate the positive, but it establishes that **the effective observation boundary was not the initially
measured boundary**. Re-derived independently in this repository:

| Property | boot58 | boot65 |
|---|---:|---:|
| Growth during export | 42,873 B | 2,292 B |
| AppHomeScreen offset past declared length | 19,494 B | — |

So the observation window that would have had to contain boot65's registration was roughly **19× shorter**
than boot58's. "Absent from the export" and "never registered" are now distinct claims, and only the first
is measured.

## Astra's measured-vs-inferred split (adopted)

Measured: boot58 has one named Home request at `[824313.371]`; boot65 has none; both streams contain
controller screen announcements; both register `AppStandbyClock` using 1006, so the number alone does not
identify Home.

Process markers, which Astra stresses are **script observations, not connection-to-PID attribution**:

| Retained marker | boot58 | boot65 |
|---|---:|---:|
| Cold PID | 2268 | 2374 |
| PID present when cold disappearance detected | 2667 | 2546 |
| Reported warm PID | 2667 | 2546 |
| PID reported at screenshot capture | 2667 | **2677** |

Inferred, not established: that boot65's absence came from a launcher registration deadline rather than
capture coverage, replacement, identity/environment differences, or another failure.

## The four answers

### 1. Is boot78 the right single next test?

**Not as specified.** Offline audit first; a run can follow as the one bounded reproduction test.

The cheaper step is to reconstruct and compare the launch-generation and export-cutoff timelines for both
runs from their retained `boot*-*.log`, `serial.log`, `dbg-out.txt` and `exported-weston.bin`. For each run,
align — or explicitly mark as unalignable:

1. App-11 process start, PID **and start time**.
2. Launcher registration, timeout, kill and replacement.
3. Warm-launch request and its actual outcome.
4. Power request and observed `power_status`.
5. Home-associated protocol requests, if attribution exists.
6. Log-size measurement, export start/end, and last retained protocol event.

Immediate discriminating question: **did boot65 observe the equivalent launch generation through the
equivalent milestone at which boot58 registered Home?**

Astra's constraint, adopted: do not force a correlation from connection-local `@18`/`@21` numbers or
subtract unrelated clock origins. If the needed launcher records or clock anchors were not retained,
identify that exact gap and stop the offline pass.

### 2. Is the pre-committed null stated correctly?

**No — it was too strong.** "AppHomeScreen absent ⇒ registration timing confirmed" is not supported.
Absence is equally consistent with a capture-window artefact, a different app-identity path, or a launcher
child-environment difference. Adopted correction: the null must be restated per-cause, so that a capture
artefact is reported as `CAPTURE_TRUNCATED`, not as a confirmed negative.

### 3. What confound must a run control for?

The thing boot58 and boot65 did not hold equal: **the export window itself**. A future run must record the
log size at measurement, at export start, and at export end; must export a genuinely closed snapshot rather
than a streaming read; and must retain the launcher's own records so the observed launch generation is
identified rather than assumed.

### 4. What would make the run worthless?

Any result where the export boundary is not proven to post-date the milestone under test. That is
indistinguishable from a real negative unless the boundary is recorded in advance — which is exactly the
failure that produced this correction.

## Consequences applied

- Scheduled task `567ef556` (boot78) **paused**.
- `docs/kernel/41` corrected: the registration-timing conclusion is now labelled an inference, with the
  capture-window rival quantified.
- The ~48.58 s / ~39.8–45 s figures are marked as imported from `docs/kernel/22`, measured on a different
  run, and as stacked on a model `docs/kernel/23` already refuted. They may not be used to explain boot65's
  absence.

## Review-route note

The parallel Fable review of `docs/kernel/41` did not complete: the `anthropic/claude-fable-5-1` route
returned a usage/billing rejection ("Third-party apps now draw from your extra usage, not your plan
limits"). The block is recorded rather than silently substituted. Astra's review above stands on its own
and already covers the overclaim questions the Fable pass was meant to test.
