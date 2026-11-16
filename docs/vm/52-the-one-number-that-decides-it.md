# The one number that decides the display thread: 39.8 seconds

Date: 2026-11-06. Three separately-measured facts, put in the same units for the first time. They explain every kill this project has
recorded, and they say exactly what to try next.

## The three facts

| measurement | value | source |
|---|---|---|
| the launcher's **app-load timeout** for app 11: `start` -> `[TIMEOUT] [2 Group]` | **39.8 s** | boot50: `23:03:09.771` -> `23:03:49.566` |
| the app's **cold** announce (`START DRAW` -> registration) | **48.58 s** | `docs/kernel/25` |
| the app's **warm** announce, across every warm relaunch measured | **1.17 - 8.13 s** | `docs/kernel/25` |

## What those three numbers mean together

**Cold loses by 8.8 seconds. Warm wins by at least 31.7.**

When the app announces late, the launcher's app-load timeout fires first and **registers the app on its behalf** - the log sequence is
`[TIMEOUT] [2 Group] AppID : 11` then `[REGISTERED]`, 30 ms apart. The application's own announce then arrives and collides, producing
`[REGISTERED ERROR] Already registered`, and the duplicate guard terminates it. **That is the whole kill loop, and it is a race the
project has only ever entered cold.**

And the loop is self-reinforcing: the kill destroys the warm state, so the next start is cold again and loses again by ~9 s. **Nothing
in the vendor's system is broken here; a ~48 s cold start simply does not fit inside a ~40 s timeout.**

## Why warm has never been given a fair test

Every warm measurement this project has taken was **before the SMACK label fix**, and those instances died for a *different* reason - the
PHEV denial, `appProcessFinishedSlot [11][0][0][11]` -> SIGSEGV. So warm instances were killed by a fault that has since been removed.
**Warm + labelled is untested territory.**

## The experiment, and its single variable

**Warm the application, then let the managed launch happen, with the `App::home` label in place.**

```
1. boot; let the launcher start app 11 cold (it will time out and be killed - this instance is the pre-warm and is expendable)
2. immediately after the kill, request the relaunch through the launcher's own interface:
   dbus-send --session --dest=com.lge.avn.applauncher /com/lge/avn/applauncher \
       com.lge.avn.applauncher.request.launch int32:11 string:AppHomeScreen string:/app/bin
3. measure, in this order, with `tools/uk_fw/guest/measure.sh`:
     d_registered_before_timeout   whether [REGISTERED] appears WITHOUT a preceding [TIMEOUT]
     d_duplicate_error             whether [REGISTERED ERROR] Already registered appears at all
     d_phev_denial                 dmesg grep for object="Data::commonphev"
     d_alive_60s                   whether the pid is alive 60 s after registering
     d_frame                       capture size and whether the layout is present
```

**The single variable is warmth.** The label, the surface id, the kernel, the backend and the timeout constants all stay frozen.

## What each result would mean

- **Registered without a timeout, no duplicate, alive at 60 s** -> the display thread's blocker is closed, and the honest statement is
  that the vendor's HMI runs under TCG when the app is pre-warmed and correctly labelled. The remaining work is making warm-up part of
  the projection's launch sequence, which is a boot-script change, not a patch.
- **Registered in time but still SIGSEGV** -> warm-up is necessary but not sufficient, and the *next* denial or fault in `dmesg` names the
  next missing label or data source. That is progress with a named cause.
- **Still loses to the timeout while warm** -> the 39.8 s figure is wrong or the relaunch is not actually warm, and the check is the
  registration timestamp itself rather than the outcome.

**This is the cheapest decisive experiment available**: one boot, one variable, and every outcome names its own next step.
