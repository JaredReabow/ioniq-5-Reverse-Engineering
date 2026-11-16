# Warm + labelled survives, and the decisive bus check is clean: the registration name is unowned

Date: 2026-11-06. The warmth experiment (doc 52's plan) was run: cold launch as expendable pre-warm, then
a warm relaunch through the launcher's own interface.

## The decisive bus check (dbus-send, which works)

```
[warm] AM_BUS_OWNER=[method return … boolean false]
```

**`com.lge.avn.appmanager.registration` is unowned.** ApplicationManager runs (doc 30, app id 2), but it
does **not** own the registration bus name — so the application's announce reaches nobody, which is the
root cause of the duplicate, not the cold start.

## The warm relaunch

```
[warm] COLD_PID=[2317] at +80s
[warm] COLD_KILLED at +120s (was 2317, now empty)
[warm] WARM_PID=[2563]
[warm] WARM_REG=[[REGISTERED] 00:36:36.824 | [REGISTERED ERROR] Already registered 00:36:37.090 | [REGISTERED] 00:36:44.596]
[warm] WARM_DUPLICATE=1
[warm] ALIVE_60S=yes
[warm] PHEV_DENIAL=0
[warm] FRAME bytes=129844
```

- **Alive at 60 s** (`ALIVE_60S=yes`) and **no PHEV denial** (`PHEV_DENIAL=0`) — so warm + the `App::home`
  label is sufficient to stop the SIGSEGV. The app now survives.
- **The duplicate persists** (`WARM_DUPLICATE=1`, `Already registered` 266 ms after the first register),
  because the registration name is unowned.
- The frame is 129,844 (standby) because this probe deliberately did **not** send `set_power_on_status` —
  it measured survival, not layout.

## What this closes and what it names

- Closed: the PHEV SIGSEGV (doc 27/28) is gone, and a warm labelled instance survives.
- Named: the remaining blocker is **ApplicationManager not owning
  `com.lge.avn.appmanager.registration`**. The fix is to start the vendor's `ApplicationManager` the way
  it is meant to run (`/app/bin/ApplicationManager -cv:0 -vv:0`, per
  `tools/uk_fw/guest/appnavi_baseline_probe.sh:55`) so it claims the name — a fidelity gain, not a
  substitution.

## Files

- `work/vm/kbuild/boot52-warm.log` — the run.
- `work/vm/kbuild/ws/partimg-build/warm-test.sh` — the probe.
