# The power-on call lands, but the app crashes during the layout — the laid-out frame was not captured

Date: 2026-11-06. The seat fix (doc 09) got weston serving and AppHomeScreen connecting. This run made
the `set_power_on_status` call and tried to capture the laid-out home screen. It did not appear.

## The call, made correctly

Sequence earned so far: boot authentic (`--smp 4`, patched kernel 1920×720, fixed `weston-vm-input.so`),
poll the bus name, then the call. Measured:

```
[poweron] SOCKET_UP after 2s
[poweron] BUS_AT_+10s=[unix:abstract=/tmp/dbus-51EHZDmqU0,guid=af74df…]
[poweron] NAME_OWNED=yes at +100s          (polled NameHasOwner, not a fixed sleep)
[poweron] APPHOME_PID=[2328]
[poweron] ASK_POWER_BEFORE=[method return … int32 1]
[poweron] SET_POWER=[method return …]      ← accepted
```

So the call **landed** (the setter returned `method return`). `ask_power_status` reads 1 before, exactly
as the docs say — not used as a pass/fail.

## The capture: five samples, all the standby face

Capture at +5/+15/+30/+60/+90 s after the call (screenshooter, sent base64 over `/dev/ttyS2`):

```
CAP_5s  pid=[2328] bytes=129844 magic=89504e470d0a1a0a
CAP_15s pid=[2328] bytes=129844 …
CAP_30s pid=[2564] bytes=129844 …          ← pid changed: the instance crashed and was replaced
CAP_60s pid=[2564] bytes=129844 …
CAP_90s pid=[2564] bytes=129844 …
```

**129,844 bytes is the early-background/standby size** (the project's own reference). All five frames are
the standby face, never the laid-out home screen (16,062 bytes). Decoded samples are byte-exact.

## What happened: the instance crashes between +15 s and +30 s

`AppHomeScreen` pid goes 2328 → 2564 between the +15 s and +30 s captures. The instance that received
`set_power_on_status` (2328) dies before it finishes laying out, and the launcher restarts it (2564) in
the standby state. So the frame stays the standby face.

## Honest verdict, against the decision table

This is a **fourth outcome**, not one of the three predicted:

- not the light laid-out frame (never reached);
- not "the call did not land" (it did — `method return`, and the pid change proves the app was live);
- **the app crashes during the power-on layout**, before it reaches the laid-out state.

The laid-out-frame goal is blocked by an **AppHomeScreen crash during layout** on the DRM backend — a new
problem, distinct from the seat, the mode, and the socket (all of which are now fixed and working).

## Two facts that bound the next step (not conclusions)

1. The crash is **not** accompanied by `invalid object` text in any log I captured this run — but the
   launcher-started app's stderr goes to the launcher's own log (`/tmp/applauncher-stdio.log`), which this
   script did not dump. The `invalid object 19` fault (doc 09) was about connection; a *second* such fault
   during layout (more surfaces/widgets created) is not ruled out.
2. A screenshooter gotcha, recorded so it is not lost: it writes `wayland-screenshot.png` to **CWD**, so
   the capture must `cd /tmp` first (missing this made the first four capture attempts in the previous
   run silently produce nothing).

## Files

- `work/vm/kbuild/painted-1920x720.png` — the standby face at 1920×720 (144,501 bytes, doc 11).
- `work/vm/kbuild/boot37-cd.log` — the power-on run above.
- `work/vm/kbuild/ws/partimg-build/poweron-capture.sh` — the capture script.
