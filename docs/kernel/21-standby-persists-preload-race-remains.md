# With the surface composited, the power-on call still does not leave standby — the preload race remains

Date: 2026-11-06. Doc 20 proved the surface-id patch composited the home screen. This run applied the
full refined sequence (stability gate → surface-id precondition → place → call → confirm → capture) to
land the power-on on the instance owning surface 2080.

## The run

```
[both] PID_STABLE_GATE=yes pid=[3021] after +60s   (longer: 2316→2475→2696→2803→3021)
[both] SURFACE_ASSIGNED=[QT_WAYLAND_SET_SURFACE_ID=2110]      ← grep artifact (matched AppID 110)
[both] SURFACES=[30000|2080|1001|1002|2080|1004]              ← surface 2080 present (twice: relaunches)
[both] APP_SURFACE_ID=[2080]
[both] IVI_WM_RC=0
[both] SET_POWER_SENT
[both] AFTER_CALL pid=[3021] (was 3021) preload=[int32 1]     ← the call landed on the stable instance
[both] CAP_30s pid=[4584] bytes=120460
[both] CAP_60s pid=[5198] bytes=120460
[both] CAP_90s/120s pid=[] bytes=120460                       ← the instance is gone by +90s
```

(`SURFACEID_LINES` confirms the real assignment: `AppID : 11, Set to QT_WAYLAND_SET_SURFACE_ID=2080` at
21:23:19, 21:24:02, 21:24:14 — the `SURFACE_ASSIGNED=[2110]` line is a grep bug: `'AppID : 11'` also
matches `AppID : 110`.)

## The result

The power-on call landed on a pid-stable, preload-complete instance that owned surface 2080. The frame
is still **120,460 bytes — the standby class** (the user opened it: title bar with `STR_CAMERA_ALERT2`,
KIA logo on black). And the pid is still in the deregister loop (3021 → 4584 → 5198 → gone).

## The honest reading

This is the "title bar and logo again" outcome the user predicted — but the reason is **not new**: the
instance that received the call (3021) was deregistered ~25 s later by the same preload-deadline race
(doc 13), so the power-on state dies with it and the relaunched instances start in standby. The
surface-id patch removed the "no surface" blocker (doc 19); the **preload-deadline race is the remaining
blocker**, and it is now the only one.

## What this closes and what it does not

- **Closed:** the launcher now reads the table for AppHomeScreen, surface 2080 is created and placed, and
  the app's standby chrome is genuinely composited (doc 20). That step was blocked for ten entries.
- **Not closed:** leaving standby. That is the preload-complete deadline (doc 13), which needs the
  deadline patch (option 2) or the preload signal stub (option 3) — not a third reordering.

## Files

- `work/vm/kbuild/boot45-final.log` — the run.
- `work/vm/kbuild/ws/partimg-build/both-halves.sh` — the refined script.
