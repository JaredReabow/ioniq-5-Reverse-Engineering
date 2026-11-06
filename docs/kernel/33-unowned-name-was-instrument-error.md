# The "unowned name" was an instrument error: the bus name is `com.lge.hyundai.avn.appmanager`, not the interface

Date: 2026-11-06. The qualified run (monitor started before the launch) captured the registration
traffic and corrected the name we were checking.

## The qualified run

```
[q] CAP0 pid=683                       ← instrument qualified
[q] BUS_AT_+8s addr=[unix:abstract=/tmp/dbus-Gt0Yb61Ggf,…]
[q] DBUS_MONITOR_PID=[1496]             ← monitor started BEFORE the first launch
[q] AM_PID=[2167] at +39s
[q] AM_ADDR=[…/tmp/dbus-Gt0Yb61Ggf,…]
[q] LA_ADDR=[…/tmp/dbus-Gt0Yb61Ggf,…]   ← the SAME address
[q] ADDR_DIFFER=no                      ← ordering hypothesis REFUTED
[q] NAME_OWNED=[boolean false]          ← but checked the wrong name (see below)
[q] DBUS_MON=[ … method call sender=:1.36 -> dest=com.lge.hyundai.avn.appmanager serial=8
              path=/registration; interface=com.lge.avn.appmanager.registration;
              member=deregistration int32 12 string "AppCamera" | … ]
```

## The correction

The captured traffic shows the **destination is `com.lge.hyundai.avn.appmanager`** (the well-known bus
name), while `com.lge.avn.appmanager.registration` is the **interface** on that name. Every previous
`NameHasOwner` check in docs 30–32 asked whether a process owned the *interface* string as a bus name —
which no process does — and read `false` as "the name is unowned". That was an instrument error, not a
missing owner. The addresses also **match** (ordering is refuted), and the monitor shows the handshake is
**happening**: the app calls `deregistration` (and more, truncated) on the manager.

## The corrected next check

`NameHasOwner` for the **bus name** `com.lge.hyundai.avn.appmanager` — not the interface. And the full
`dbus-monitor` log (this run kept only the first 500 chars on the console; the rest is in the guest's
ephemeral `/tmp/dbus-monitor.log`) must be retained to see the whole `launched`/`deregistration` order,
which is what distinguishes "delivered and refused" from "delivered and answered".

## Files

- `work/vm/kbuild/boot54-q.log` — the run.
- `work/vm/kbuild/ws/partimg-build/qualified.sh` — the probe.
