# ApplicationManager is running (launcher app id 2) — but its bus-name ownership is NOT MEASURED

Date: 2026-11-06. The registration authority was traced to `ApplicationManager` (doc 51). This run
measured whether it runs and owns the bus name.

## What the run found

```
[amcheck] AM_PID=[]            at +10 s   ← not yet launched
[amcheck] AM_BIN=[-rwxr-xr-x … 3956056 … /app/bin/ApplicationManager]   ← vendor binary present
[amcheck] BUS_REG=[Failed to get credentials: No such device or address]  ← busctl failed
[amcheck] AM_PID_LATER=[2009]  at +120 s  ← running later
```

The launcher log (boot 50) also shows ApplicationManager is **launcher-managed app id 2**, registered at
~23:02:25 (group 0), i.e. it is launched early by the launcher itself, before AppHomeScreen (group 2).
So the "ApplicationManager is not running" half of the hypothesis is **refuted**: it runs, as app id 2,
ahead of the home screen.

## What is still NOT MEASURED

The decisive check — who owns `com.lge.avn.appmanager.registration` — came back
`Failed to get credentials: No such device or address` from `busctl`. That is an instrument failure
(the session-bus address in `/tmp/session_appmgr` did not work for `busctl` the way it does for
`dbus-send`), so the bus-name owner is **NOT MEASURED**, not "no owner". Under rule 17, the correct next
instrument is `dbus-send … NameHasOwner string:com.lge.avn.appmanager.registration` (which is known to
work in this image), not another `busctl` attempt.

## The corrected next step

The question has narrowed from "is ApplicationManager running" (it is) to "does the running
ApplicationManager own `com.lge.avn.appmanager.registration`". One `dbus-send NameHasOwner` call at the
moment of the duplicate answers it. If the name is unowned, the fix is the vendor's component at the
right time; if it is owned, the duplicate is the app's own double-announce and the `dbus-monitor` count
of `launched` calls is the next measurement.

## Files

- `work/vm/kbuild/boot51-amcheck.log` — the run.
- `work/vm/kbuild/ws/partimg-build/amcheck.sh` — the probe.
