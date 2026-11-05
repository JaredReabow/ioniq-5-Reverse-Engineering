# Combining the two halves: the stable instance has no surface to place, and dies on the call

Date: 2026-11-06. Doc 17 gave a stable, preload-complete instance but no layout; doc 11 gave a placed
surface with the app's chrome. This run combined both: pid-stability gate → place the surface → check the
pid → power-on → capture.

## The run

```
[both] NAME_OWNED=yes at +85s
[both] PID_STABLE_GATE=yes pid=[2238] after +0s
[both] STABLE_PID=[2238]
[both] SURFACES=[Surface id(30000)|Surface id(1000)|Surface id(1001)]
[both] APP_SURFACE_ID=[]          ← no application surface exists
[both] PID_AFTER_PLACE=[2238] (was 2238) PLACE_SURVIVED=yes
[both] SET_POWER_SENT
[both] AFTER_CALL pid=[] (was 2238) preload=[int32 1]   ← the instance died on the call
[both] CAP_30s/60s/90s/120s pid=[2635] bytes=129844
```

## What it shows

1. **There is no application surface to place.** `weston-real.log` lists only `Surface id(30000)`,
   `1000`, `1001` — the ivi-shell's own surfaces — so `APP_SURFACE_ID` is empty and the placement step
   was a no-op. This differs from doc 11, where an app surface id existed. So the *stable* instance here
   (2238) never created its Wayland surface.
2. **The call kills the instance.** After `set_power_on_status`, `pidof AppHomeScreen` is empty; a new
   instance (2635) appears later. The deregister race is still present even against the instance the
   gate called "stable".
3. Every capture is 129,844 bytes — the early background (no blue bar), consistent with there being no
   app surface to composite.

## Honest reading

The combined test did **not** reach the laid-out frame. The two halves do not actually compose yet: the
instance that is pid-stable at gate time has no surface, and it is deregistered on the power-on call.
The placement step (doc 11) only ever had a surface because the *old* monitor ran against a different,
already-painting instance.

## Where this leaves the thread

The blocker is now clearly earlier than placement: **the surviving AppHomeScreen instance does not create
a surface** (and the power-on call deregisters it anyway). The next measurement is *why no surface* —
check `weston-real.log` for the app's `wl_surface` creation vs. only the ivi-shell surfaces, and whether
the app's own stderr (the launcher log, per doc 13) shows the surface/EglSurface creation failing. The
launcher log was the answer the last three times, and it is the natural next thing to read.

## Files

- `work/vm/kbuild/boot43-both.log` — the run.
- `work/vm/kbuild/ws/partimg-build/both-halves.sh` — the combined script.
