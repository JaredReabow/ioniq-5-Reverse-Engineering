# Controlled run 4 — result: the synchronised observer was the wrong instrument, and the export trigger is misaligned

Date: 2026-11-08. Run `1794058777482602000`, workspace `work/vm/kbuild/ws-run64` (fresh CoW clone).
Driver committed at `9cd7818` (sha256 `f4640b92…`). Artifacts in
`evidence/controlled-run-4-2026-11-08/`.

Run 4 was designed to answer run 3's open question — why does a registered surface not reach the
visible output — by taking a protocol inventory at the same instant as a frame. **It did not answer
it**, for two separate reasons. Both are worth more than a null would have been.

## What ran

| Channel | Result |
|---|---|
| Display | frames at +10 s, +60 s, +110 s, all 129,844 B, `shooter_rc=0` |
| IVI probe (`ivi-place --list`) | ran at the same three ticks, `rc=0`, output framed and retained |
| Export | `EXPORT_CALL_OK at_s=30 rc=0`, payload 98,122 B |
| Persistence | sampled over 120 s |

## Reason 1 — the observer is known to be blind, and it was used anyway

All three IVI inventories report:

```
ivi_place: bound ivi_controller (registry name 15, version 1)
ivi_place: announced by ivi_controller: 0 layers, 0 surfaces, 0 screens
ivi_place: layer ids:   (none)     surface ids: (none)     screen ids:  (none)
```

That looks like an answer and is not one. `docs/kernel/39-40` already established that `ivi_place`
binds only `ivi_controller` and **not** `wl_output`, that the inspected server only sends controller
screen resources to a client holding a matching output resource, and that the tool reports after its
initial registry roundtrip without a post-bind roundtrip. Its zero counts are **observer-specific**,
not a system census.

So this run's IVI data establishes only that `ivi-place` still reports zero to a client of this shape.
It does **not** establish that the compositor had no layers or surfaces, and it does not say anything
about the AppHomeScreen surface.

The instrument choice was wrong, and the project had already written down why. The synchronised-probe
*idea* was sound; `ivi-place` as the probe was not.

## Reason 2 — the export trigger is wall-clock, the milestone is protocol-time

The export fires at `EXPORT_AT_S = 30` measured from first sight of the app process. The milestone
reference (96,445 ms) is measured from the first `create_hmi_client` **in protocol time**. Those are
different clocks, and run 4 shows they diverge:

| Run | Export trigger | Captured window after precursor | Verdict |
|---|---|---:|---|
| 3 | +30 s from first sight | reached the milestone | `REGISTRATION_PRESENT` |
| 4 | +30 s from first sight | **35,944 ms** (60,501 ms short) | `CAPTURE_TRUNCATED` |

Same trigger, opposite adequacy. The compositor had simply advanced much less by that wall-clock
offset in run 4.

**This is the Astra C11 error class reappearing on the trigger side.** Astra rejected an absolute
offset imposed on a differently-paced run as the *verdict* criterion; run 4 shows a wall-clock offset
is equally unreliable as the *trigger*.

What the frozen verifier did with it is exactly right:

```
CAPTURE_TRUNCATED marker absent and the capture extends 35944 ms past the precursor,
60501 ms short of the 96445 ms milestone reference
```

**Unresolved, not absent.** Without the per-cause null this run would have read as "Home did not
register", which would have been a confident negative from a window that had not reached the stage.

## What run 4 does establish

- The six clients that registered in this window: `AppOSDManager` ×2, `AppDMClient` ×2,
  `AppStandbyClock`, `AppCamera`. **`AppHomeScreen` is not among them** — and because the window is
  truncated, that absence is **unresolved**, not a negative.
- 72 `ivi_controller.layer(...)` lines, 3 `set_display_plane`, 9 `create_surface` in the payload: the
  IVI server was announcing layout objects while the visible output was still the splash. That is
  consistent with run 3 and is *server-side* evidence, not the blind observer's.
- Combined with run 3, the app's registration is **not stable across runs**. Run 3: present at +30 s.
  Run 4: not present, window truncated. Two runs do not establish a rate.

## What is still not established

Why a registered surface does not reach the visible output. Run 4's IVI probe could not address it,
and the compositor payload is the better source — it carries the server's own layer and surface
announcements.

## The next exact action, and it is offline

Do not run again yet. Two things are now known and cheap:

1. **Analyse the retained export payloads** from runs 3 and 4 for surface lifecycle and layer
   placement around the registration — buffer attach/commit, `set_display_plane`, layer assignment.
   That is server-side evidence already in `evidence/controlled-run-{3,4}-2026-11-08/` and needs no
   boot.
2. **Re-anchor the export trigger to protocol progress** rather than wall-clock: fire the export once
   the compositor log has advanced a fixed number of protocol-ms past the first `create_hmi_client`,
   with that number declared before the run. That directly removes the run 3/run 4 divergence.

A further run before those two are done would produce another frame of the same splash and another
verdict that says more about the trigger than about the app.
