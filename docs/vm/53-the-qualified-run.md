# The qualified run: three captures, taken before the thing they observe

Date: 2026-11-06. Astra and Opus 4.7 were given the same negative result independently and converged: **do not build a stand-in yet, and do
not measure anything after the fact.** Both put the top cause on the same defect this project documented from the other direction.

## The convergence

**Opus 4.7's ranking** puts **the wrong session bus** first: `Dbuslaunch.sh` writes `/tmp/session_appmgr` with no mode and no ownership
check, consumers read it unvalidated, and a component that starts before the file is written connects elsewhere silently. It rules the
stand-in **inadmissible until** that and the wrong-owner explanations are excluded, and then only as a *declared, scoped, logged* crutch
that owns the name while the real binary runs alongside it.

**Astra's answer to the same negative** is procedural: build the collection **before** the launcher and manager start, capture three things in
a fixed order, and never attach a probe after the fact - which is exactly how boot53 produced `ADDR_DIFFER=no` from two empty addresses.

**Both agree on one thing that matters more than the mechanism:** the last run measured nothing because the instrument arrived late and left
no log. **The next run's job is to make a null result informative.**

## The three captures, in order

**Capture 0 - qualify the instrument before the system starts.** The wrapper emits its own pre-exec marker through the real stdout/stderr
destinations and records its pid and the address it will read from. *If this step alone fails, the run stops* - that is the rule the project
learned from seven instrument failures, applied.

**Capture 1 - startup and both bus identities.** Collectors start **before** the vendor stack. **Do not start `ApplicationManager` by hand**:
the launcher starts it as app id 2, and a manual start measures a different configuration. Capture by pid, not by name, at the moment app id 2
appears:

```
for p in $appmanager_pid $applauncher_pid $apphomescreen_pid; do
  tr '\0' '\n' < /proc/$p/environ | grep '^DBUS_SESSION_BUS_ADDRESS='
done
dbus-send --session --dest=org.freedesktop.DBus /org/freedesktop/DBus \
    org.freedesktop.DBus.NameHasOwner string:com.lge.avn.appmanager.registration
```

**The comparison is the whole experiment**: if the manager's address differs from the launcher's, the cause is confirmed and the fix is
ordering, not code.

**Capture 2 - the call itself.** `dbus-monitor "interface=com.lge.avn.appmanager.registration"` running **from before the first launch**, so
the capture separates *nobody heard the announce* from *somebody said no*. A monitor started after the event produces a confident zero,
which this project has already mistaken for a finding three times.

**Capture 3 - the outcome, textually.** `[REGISTERED]` without a preceding `[TIMEOUT]`, absence of `Already registered`, `ALIVE_60S`,
`PHEV_DENIAL=0`, and the launcher log **retained in the run directory** rather than only grepped in place.

## Their stopping rules, merged

**Close the blocker** only when the intended vendor owner is identified **on the app's actual bus**, the warm app registers without a timeout
preceding it, and it is alive at 60 s.

**Continue once** only if the run names a new testable mechanism - wrong bus, unclaimed name, or a refusal from a reachable owner.

**Stop and document** if the run reproduces none of those and the monitor saw no call at all: at that point the honest conclusion is that this
projection cannot complete the vendor's registration handshake, and the display thread closes as a **documented limitation with two named
mechanisms** rather than an open question.

## And the security finding is the same defect

**This is the first time tonight that the display blocker and a register entry are the same thing.** `V-058` says eleven services take their bus
address from `/tmp`; the projection blocks because one of them did. **The projection fix and the remediation are identical** - set a mode,
validate the path, start consumers after the writer, fail closed - so the work serves both goals instead of competing with them.
