# Gate 2 is closed — power-on is consumed — and Gate 5 names the last fault: the app has no surface

Date: 2026-11-06. The endgame runbook's two gates. Pre-committed nulls: gate 2 = method but no
`power_status` signal; gate 5 = app 11's pid with no compositor surface.

## Gate 2: CONSUMED

The monitor, started before the call, captured:

```
signal sender=:1.39 … path=/Information; interface=com.lge.avn.appmanager.info; member=power_status int32 1
```

`GATE2_POWER_STATUS=7`. The `power_status` signal (status 1) **follows** `set_power_on_status`. For the
first time in this thread, power-on is proven consumed, not merely delivered — the state machine moved.

## Gate 5: the app has no surface

```
GATE5_IVI=[ivi_place: … 0 layers, 0 surfaces, 0 screens … surface ids: (none)]
GATE5_SURFACES=[Surface id(30000)|Surface id(1000)|Surface id(1001)]   ← ivi-shell's own, no app surface
APP_PID_AT_GATE5=[2561]
CAP bytes=129844 pid=[2561]
```

App 11's pid (2561) is alive, labelled `App::home`, warm, power-on consumed — and the compositor has **no
surface for it**: the ivi-controller lists zero surfaces, and `weston-real.log` contains only the
ivi-shell's own `30000/1000/1001`. The requested `1010` never appears.

## The honest conclusion

This is Gate 5's null, exactly as the runbook defined it: **the app draws where nothing reads.** The
whole lifecycle is now closed — kernel, DRM device, 1920×720, seat, socket, registration, label,
power-on consumption — and the one remaining fault is that the warm app never creates a compositor
surface, which is why every capture is the 129,844-byte background. That is a named limitation with one
mechanism, not an open question.

## Files

- `work/vm/kbuild/boot56-end.log` — the run.
- `work/vm/kbuild/ws/partimg-build/endgame.sh` — the probe (with the pre-committed nulls).
