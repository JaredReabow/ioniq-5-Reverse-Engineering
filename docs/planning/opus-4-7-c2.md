# Post-run consultation: the unowned `com.lge.avn.appmanager.registration`

Date: 2026-11-06. Written after reading `docs/kernel/31`, `docs/kernel/32`,
`docs/vm/52`, `docs/trust-anchors-in-writable-runtime-paths.md`, and
`app/bin/Dbuslaunch.sh`. No experiments.

## 1. Why a Qt D-Bus service binary containing the interface would not claim the name

The XML and the symbol presence inside the 3.96 MB `ApplicationManager` binary
prove the interface is *reachable* from that process, not that the process is
the one that calls `registerService()` for the name. Doc 32 itself lists three
hypotheses ("arguments incomplete, needs its own D-Bus service setup, or is the
wrong process for that interface"); ranked by what the evidence in hand
supports, with trade-offs made explicit:

1. **Wrong session bus.** `Dbuslaunch.sh` writes `/tmp/session_appmgr` with no
   mode and no ownership check; every consumer does
   `` DBUS_SESSION_BUS_ADDRESS=`cat /tmp/session_appmgr` ``, and the trust-anchors
   document names this file as the "same defect" that produces an unowned
   registration name. A manual `-cv:0 -vv:0` from a research shell inherits
   whatever `DBUS_SESSION_BUS_ADDRESS` the shell had - which, in a projection
   whose login path does not source `.env`, is either empty (so the binary
   fell back to the per-user default, e.g. `$XDG_RUNTIME_DIR/bus`) or the
   *previous* boot's stale file. On that bus the name is claimed just fine;
   nobody is looking at that bus. On the launcher's bus it stays unowned.
2. **Launcher-provided startup context missing.** The binary runs as launcher
   app id 2, which the launcher starts with a group argument, a bus env file
   (`/tmp/session_appmgr.env`), and almost certainly an app-id/group pair
   the Qt code uses before `registerService()`. `-cv:0 -vv:0` provides only
   two integers; the service-registration path can be gated on a readiness
   signal, a config file at a launcher-chosen location, or an id the launcher
   passes. If the registration call is late in the init, the process can be
   up, connected to the right bus, and still not own the name.
3. **SMACK exec label on the name-claim path.** `AppHomeScreen` was killed by
   a PHEV denial until it carried `App::home`; the manual AM was started
   unlabelled, floor `_`. The session bus policy can refuse a name claim for
   `_` while allowing method calls; the symptom would be exactly a connected
   client that never becomes an owner.
4. **Fast exit, unobserved.** "No manager output" is consistent with the
   binary dying before calling `registerService()` (missing config, missing
   dependency, failed `QDBusConnection::sessionBus().isConnected()`); the run
   did not capture stdout/stderr, so this cannot be ruled out but is cheap to
   rule out.
5. **Wrong process, right XML.** Qt's generated proxy and adaptor headers
   share the XML. `ApplicationManager` carrying the interface proves it uses
   it; it does not prove it owns it. The vendor's stock owner could be
   `AppLauncher` or a third binary, with AM a *client*. See section 5.

**The single observation that separates (1) and (2)** - the one measurement that
decides it without another full boot cycle is:

```
cat /proc/$(pgrep -nx ApplicationManager)/environ | tr '\0' '\n' | grep DBUS_SESSION_BUS_ADDRESS
cat /tmp/session_appmgr
```

If the two strings differ, it is **(1) wrong bus**, full stop. If they match,
AM is on the launcher's bus and the name is still unowned - which is **(2)
missing startup context**, and the next question is what the launcher passes
that `-cv:0 -vv:0` does not. The measurement is one `cat` per side; the mistake
in doc 32 was taking it at +10 s when AM had not started yet.

## 2. The cheapest next run

Given the budget (~15 min per boot, one already burnt on an untaken
measurement), the cheapest decisive probe is a **single boot that gates on
presence instead of on wall-clock time** and captures AM's bus from its own
`/proc` entry. Concretely, the probe should:

1. Poll `pgrep -nx ApplicationManager` with a 60 s deadline and a 500 ms
   interval; **do nothing** until it returns a pid. This closes doc 32's
   non-measurement.
2. Immediately on non-empty pid: capture
   - `cat /proc/$PID/environ` filtered to `DBUS_SESSION_BUS_ADDRESS` and
     anything beginning with `APP` or `LGE`;
   - `cat /tmp/session_appmgr` and `cat /tmp/session_appmgr.env`;
   - `ls -la /tmp/session_appmgr*` (mode/owner - also closes the V-065 side);
   - `cat /proc/$PID/attr/current` (SMACK label);
   - `readlink /proc/$PID/fd/1 /proc/$PID/fd/2` (is stdout captured anywhere);
   - `dbus-send --session --dest=org.freedesktop.DBus --print-reply \
      /org/freedesktop/DBus org.freedesktop.DBus.ListNames` against **each**
     address that appeared above.
3. Only then warm-launch `AppHomeScreen` and capture frame + registration log.

**One boot, five artefacts, every outcome names its own next step.** If the two
addresses differ, the fix is on the projection side: make the research init
source `.env` before `applauncher` starts, or symlink
`/tmp/session_appmgr` into the shell's `DBUS_SESSION_BUS_ADDRESS` lookup.
If they match and `ListNames` on AM's bus does *not* list
`com.lge.avn.appmanager.registration`, the launcher is passing something
`-cv:0 -vv:0` omits - and the launcher binary names it (it is the caller).

This probe does **not** consume the display-timeout budget, so it can run with
or without the warm/power-on sequence after it.

## 3. If the name cannot be claimed - the honest fallback

A stand-in that implements `registration`/`deregistration` and returns a
plausible `result` would unblock the display thread, and the project has
already paid the price for stand-ins that hid vendor behaviour (the micom and
lge-board shims in `docs/kernel/04`). The honest version is a stand-in that
cannot hide behaviour because it does not pretend to be the vendor:

- **Scope is minimal and declared.** Implement only `registration` and
  `deregistration`. Leave `appbase`, `audiotransition`, `broadcast`, `info`,
  `screentransition` **deliberately unowned** so the next missing call
  surfaces as a measurable denial rather than a silent success.
- **It is labelled a projection crutch, not a measurement.** A file in
  `work/vm/kbuild/ws/partimg-build/` (not under `/app/bin`), a service name
  that includes the string `projection` in its process title, and a log line
  on every call naming the arguments received and the result returned.
- **Results are constant and documented.** Return `result=0` for both methods,
  record every (appid, appname, servicename, objectpath, plane) tuple so the
  divergence from vendor behaviour is auditable from the log alone.
- **The vendor `ApplicationManager` keeps running in parallel.** The stand-in
  only claims the *name*, not the binary's slot. This lets the bus check
  continue to tell the truth: whichever side wins `NameHasOwner` is the one
  the probe reports.
- **No measurement taken through the stand-in counts as a vendor
  measurement.** Any doc produced from a stand-in-driven boot is labelled
  `(projection, standin-registration)` in its title.

That is the fallback that would not damage this project. It should be built
only after the probe in section 2 has run and both (1) and (2) have been ruled
out - because if (1) is true the stand-in is unnecessary and would itself
become one more consumer of the wrong bus.

## 4. The missing `chmod` on the bus files - before or after the display closes

**After, with the patch written now.** Four reasons, from the trust-anchors
document and the current projection state:

- **The fix is a three-line change** (`umask 077`, `install -m 600`, pin the
  daemon's absolute path) already drafted in the trust-anchors document's
  "The fix, which is small" section; it does not require a boot to draft the
  patch or the patchable-register entry. The register gets its entry today;
  the ioctl waits.
- **Applying it mid-debug changes the variable.** The current question is
  *which bus the AM is on*. Changing the mode of `/tmp/session_appmgr`
  changes who can read it; if the research init runs as a user other than the
  one that wrote the file, a `0600` fix during this debug will **break the
  readers that currently work** and the symptom shifts under the measurement.
  The project has repeatedly lost a boot to a variable changing under a
  probe.
- **Fail-closed consumers are the actual fix.** The trust-anchors document is
  explicit: the valuable remediation is "every consumer refuses a path that
  is not a regular file owned by root with mode 0600, and fails closed". That
  is a vendor-side change touching eleven units (V-058), not something the
  projection can apply unilaterally without masking the very defect it is
  supposed to measure. Drafting the patch for the register is work on paper;
  applying it in the projection is work on the wrong layer.
- **Doc 31 names this exact file as the mechanism.** The trust-anchors
  document already links `/tmp/session_appmgr` to the unowned registration
  name. The patchable-register entry can cite doc 31 as the measurement
  and the three-line fix as the remediation, today, without a boot.

So: write the V-065 register entry now, including the one-line probe output
when it exists; apply the chmod in the projection only after the display
thread's blocker is closed, and only with a measurement of the *previous*
behaviour recorded in the same doc.

## 5. One thing this project is likely still wrong about

**That `ApplicationManager` is the process meant to own
`com.lge.avn.appmanager.registration` in the stock flow.** The evidence trail
reads as if this is settled, and it is not:

- The XML and the method symbols being in the AM binary prove it uses the
  interface, not that it owns the name. Qt D-Bus generates the same XML into
  both the proxy and adaptor headers; a client ships the adaptor XML with its
  binary as a matter of course.
- Doc 32 lists "wrong process for that interface" as one of three
  possibilities after the manual launch did not claim the name, then the
  project proceeded as if the other two were the only live options.
- The observed vendor behaviour is already consistent with the launcher
  owning the name: in every captured run the launcher's timeout path
  *registers the app* and the second `[REGISTERED]` is the application's own
  announce colliding with it. The "duplicate guard kills it" reading
  presumes the first registration is a workaround; the alternative reading is
  that **the launcher registering is the stock flow**, and the application's
  own call - which this project has been working to make faster - is the
  duplicate that stock images never produce because the application never
  calls it in the stock boot.
- `com.lge.avn.applauncher` clearly owns itself (section 2 of doc 52 uses it
  to request launches); the project has never measured whether the same
  launcher also owns `com.lge.avn.appmanager.registration`. `NameHasOwner`
  returns a boolean; `GetConnectionUnixProcessID` returns the owning pid.
  The project has only run the first.

If this is true, the entire "warm start beats the timeout" framing from
doc 52 is correct about the race but wrong about the direction of the fix:
the honest fix is not making the application faster, it is stopping the
application from registering itself at all and relying on the launcher's
load-time registration the way the vendor does. That would also explain why
`-cv:0 -vv:0` did not claim the name - because that binary never does.

**The one measurement that would settle it,** cheap and part of section 2's
probe:

```
dbus-send --session --print-reply --dest=org.freedesktop.DBus \
    /org/freedesktop/DBus org.freedesktop.DBus.GetConnectionUnixProcessID \
    string:com.lge.avn.appmanager.registration
```

run **when the name is owned** (i.e. right after the launcher's timeout path
registers on the app's behalf, before the duplicate kill). If the returned
pid is the launcher's, the project has been patching the wrong side of the
race for two sessions.

---

## Final verdict

- **Top cause**: the manual `ApplicationManager` connected to a different
  session bus than the launcher's children, because `Dbuslaunch.sh` publishes
  the address through a world-writable file with no mode and no consumer
  validation, and the research shell's `DBUS_SESSION_BUS_ADDRESS` is not that
  file.
- **The single separating observation**: compare
  `/proc/$(pgrep -nx ApplicationManager)/environ`'s `DBUS_SESSION_BUS_ADDRESS`
  against `/tmp/session_appmgr` at the instant AM is alive. Differ -> wrong
  bus (projection fix). Match -> missing launcher-provided startup context
  (vendor-binary fix, offset-trade required, name it in the launcher).
- **Stand-in verdict**: only as a declared, scoped, logged projection crutch
  that owns the name while the real binary runs in parallel, implementing
  only `registration`/`deregistration` and returning `result=0`, with every
  call logged; built **only** after section 2's probe has ruled out the
  wrong-bus and wrong-owner explanations - because if either is true the
  stand-in masks the real fix and reintroduces the class of harm doc 04
  recorded.
