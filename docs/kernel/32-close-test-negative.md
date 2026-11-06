# The ordering check ran too early, and starting ApplicationManager did not claim the name

Date: 2026-11-06. The close test ran: check the two bus addresses, restart the vendor ApplicationManager
if needed, then warm + power-on + capture. The result is a negative with two clear causes.

## The run

```
[close] AM_PID=[] AM_ADDR=[]            at +10 s  ← ApplicationManager not yet launched
[close] LA_PID=[] LA_ADDR=[]            at +10 s  ← launcher not yet launched either
[close] ADDR_DIFFER=no                   ← cannot compare two empty addresses
[close] RESTARTING_AM                    ← so the script started the vendor binary early
[close] NAME_OWNED=[boolean false]       ← still false after the restart
[close] WARM_REG=[[REGISTERED] 00:46:52.064 | [REGISTERED ERROR] Already registered 00:46:52.081 | …]
[close] WARM_DUPLICATE=1
[close] ALIVE_60S=yes   PHEV_DENIAL=0
[close] FRAME bytes=129844                ← standby even after set_power_on_status
```

## What it shows

1. **The ordering check was taken too early.** At +10 s neither ApplicationManager nor AppLauncher has
   started (the launcher launches ApplicationManager as app id 2 in group 0, later), so `ADDR_DIFFER=no`
   is a non-measurement, not "addresses match".
2. **Starting `/app/bin/ApplicationManager -cv:0 -vv:0` did not claim the name** — `NameHasOwner` stayed
   `false`. Either the arguments are incomplete, the binary needs its own D-Bus service setup, or it is
   the wrong process for that interface.
3. The duplicate persists, and the app now **survives** (`ALIVE_60S=yes`, `PHEV_DENIAL=0`) but stays
   **standby even after power-on** — consistent with the app still being unable to reach the manager's
   signals, because the registration name is unowned.

## Honest state

The warmth + label progress (doc 31) holds: the app survives. The remaining blocker is unchanged and
now sharper: **the registration name is unowned, and simply launching the vendor binary does not make it
owned.** The next step is to find *why* — take the address comparison at the right time (after the
launcher and app id 2 are up), and read the ApplicationManager's own startup output for how it fails to
claim the interface — before any further fix.

## Files

- `work/vm/kbuild/boot53-close.log` — the run.
- `work/vm/kbuild/ws/partimg-build/close-test.sh` — the probe.
