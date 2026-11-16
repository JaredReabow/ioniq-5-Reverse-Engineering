# Post-run consultation 3: after the handshake was captured

Date: 2026-11-06. Written after reading `docs/kernel/33-unowned-name-was-instrument-error.md`,
`docs/kernel/31-warm-survives-registration-name-unowned.md`, `docs/vm/53-the-qualified-run.md`,
and `docs/planning/opus-4-7-c2.md`. No experiments.

The monitor started before the launch and recorded a real call from the app
`:1.36` to `com.lge.hyundai.avn.appmanager` on `/registration` with interface
`com.lge.avn.appmanager.registration` and member `deregistration`
(doc 33). The addresses match (`ADDR_DIFFER=no`, doc 33). The duplicate still
occurs 266 ms after the first `[REGISTERED]` (doc 31). Three of c2's live
hypotheses are therefore settled and one is sharpened.

## 1. What produces the duplicate now that the handshake flows

Four plausible sources of a second registration notification for one pid; only
one of them survives first contact with the captured traffic once the trace is
retained in full.

1. **Manager callback fan-out.** `ApplicationManager` receives
   `registration(appid, appname, servicename, objectpath, plane)` and emits a
   signal on `com.lge.avn.appmanager.registration` that `AppLauncher`
   consumes as its `[REGISTERED] registeredFromNativeApp AppId[11]`. The
   266 ms gap is consistent with a second signal from the same manager -
   either because the manager emits once from the method handler and again
   from a readiness watcher, or because two `AppLauncher` subscribers on the
   same connection each get a `[REGISTERED]` line and the dedup is per-logline
   not per-event. Signature: both `[REGISTERED]` lines carry the same
   AppId[11], and the monitor shows **one** call from `:1.36`.
2. **The app's `launched` inform landing as a second registration.** The app
   carries `com.lge.avn.applauncher.inform` with `launched` (user note 4).
   If the launcher treats `inform.launched` as a registration event (the
   name `informLaunchedFromNativeApp` is plausible given the symmetry with
   `registeredFromNativeApp`), two different paths - the manager's signal
   and the launcher's own `inform` handler - produce two `[REGISTERED]`
   lines for one pid. Signature: the monitor shows **two** method calls
   from `:1.36`, one to `com.lge.hyundai.avn.appmanager` on
   `/registration`, one to whichever bus name owns
   `com.lge.avn.applauncher.inform`, with the second arriving just before
   the second `[REGISTERED]`.
3. **The launcher's own timeout/pre-register path firing in parallel.** c2 §5
   ranked the possibility that the launcher pre-registers the app on its
   behalf and the app's own call is the duplicate stock units never produce.
   Signature: the **first** `[REGISTERED]` precedes any method call from the
   app on the monitor; the app's call lands between the two `[REGISTERED]`
   lines or after both.
4. **Session-bus re-delivery.** The app owns a transient connection
   (`:1.36`); a reconnect inside its Qt init would issue a second
   `RequestName`/`registration` call under a different unique name.
   Signature: the monitor shows two calls, from **different** unique names
   both resolving to the same pid via `GetConnectionUnixProcessID`.

**The single discriminating capture** is the retained `/tmp/dbus-monitor.log`
read start-to-finish, with timestamps, filtered to everything from `:1.36`
(and whichever unique name resolves to the app pid) and everything to
`com.lge.hyundai.avn.appmanager` and `com.lge.avn.applauncher`. One call
from the app before the first `[REGISTERED]` and nothing else from it before
the second rules out (2) and (4) and points at (1). Two calls from the app
with different destinations around the two `[REGISTERED]` lines proves (2).
A first `[REGISTERED]` before any call from the app proves (3). The capture
exists; it is the file c2 and doc 33 both named.

## 2. What to filter the retained monitor log for

The 500 char console truncation (doc 33) is a projection artefact; the full
log is at `/tmp/dbus-monitor.log` in the guest. The app and the launcher
log on different clocks (monitor timestamps are the bus's; launcher lines
are `00:36:36.824` wall) so correlation has to be by **unique name and
method**, not by time.

Concrete filter, in order:

1. `grep -nE 'sender=:1\.36|-> :1\.36' /tmp/dbus-monitor.log` to list every
   message touching the app's unique name, with line numbers.
2. For each of those lines, read ±5 lines of context to recover the
   `path=/…; interface=…; member=…` header the monitor emits on the line
   above the arguments.
3. `grep -nE 'member=(registration|deregistration|launched|inform)' ` on the
   same file to list every call of those names regardless of sender, so a
   launcher-originated registration (hypothesis 3) is visible.
4. `grep -nE 'NameOwnerChanged|RequestName' /tmp/dbus-monitor.log` to catch
   hypothesis 4's reconnect.

**The correlation** is: find the two `[REGISTERED]` lines in the retained
launcher log (`docs/kernel/31` cites `WARM_REG=[… | …]` with both
timestamps); subtract the monitor's first `method call` timestamp from the
launcher's first `[REGISTERED]` to get the monitor-to-launcher clock
offset; then every subsequent monitor event can be placed before or after
each `[REGISTERED]` by adding that offset. The order of events, not the
absolute times, is the evidence - and the order only needs to be read
between (a) the app's first call, (b) the launcher's first `[REGISTERED]`,
(c) any second call from the app or any launcher-origin call, (d) the
launcher's `[REGISTERED ERROR] Already registered`. Four points, one
offset, no clock sync needed.

## 3. Vendor defect or projection artefact

**Both the manager call and the `launched` inform exist in the app binary**
(user notes 3-4); this is not disputed. The question is whether a stock unit
also produces a duplicate from the same two announcements.

- **Projection artefact if**: in the retained monitor log the launcher's
  own pre-register (hypothesis 3) does not appear, and the two
  `[REGISTERED]` lines are produced by the manager's signal plus the
  launcher's `inform.launched` handler (hypothesis 2) - because both paths
  exist in the app, the duplicate is expected behaviour whose guard the
  stock launcher must either tolerate or short-circuit. The projection
  would then be missing a vendor-side suppression (a config flag, a slot
  state the launcher expects to see, or a `launched` destination the
  projection's `AppLauncher` does not own, so the inform is misrouted into
  the registration handler). Tell: the stock launcher's own log, which this
  project has not read, will show whether vendor units log the same
  `Already registered` line benignly.
- **Vendor defect if**: the two `[REGISTERED]` lines both come from the
  manager (hypothesis 1), the dedup is on the launcher side, and nothing
  the projection does changes the manager's emission count. Tell: the
  second `[REGISTERED]` has no corresponding second call in the monitor
  log, and the gap is deterministic across warm runs.
- **Likely in this projection**: hypothesis 2. The app carries both calls;
  the launcher's known handler names map one-to-one onto them; the 266 ms
  gap is the latency of the inform path versus the registration path, not
  of a timer. If the projection's `AppLauncher` owns both bus names, both
  inform and registration land in the same process and the duplicate guard
  fires; a stock unit's `AppLauncher` plausibly only treats `registration`
  as a registration event and routes `launched` to a launch bookkeeper that
  is absent or differently configured here.

**How to tell without a stock unit**: look at the second `[REGISTERED]`
line's text. If it is textually identical to the first
(`registeredFromNativeApp AppId[11]`), hypothesis 1 or 2 with a reused log
format; if the second reads `informLaunched…` or similar and the duplicate
guard treats it as a registration anyway, it is a projection-local
mishandling of the inform path and the fix is to split the handler.
Either way the fix is projection-side (routing / handler table), not a
vendor patch to trade for an offset.

## 4. The same shape of mistake, still live

This project has now twice read a false negative as a finding: interface
string passed to `NameHasOwner` (docs 30-32), and the wrong-bus hypothesis
inferred from captures taken before the process existed. Other items in the
current chain with the same shape:

- **Dedup "proof" from truncated logs.** `WARM_DUPLICATE=1` in doc 31 was
  derived from a `WARM_REG=[…]` string that the probe itself assembled by
  grepping the launcher log in place. If the probe's grep pattern or its
  truncation cut out a third `[REGISTERED]` or a different log line that
  explains the sequence, the "duplicate" count is an artefact of the
  filter, not the system. Guard: read the full retained launcher log.
- **"Alive at 60 s" as sufficiency.** Doc 31's `ALIVE_60S=yes` applies to
  the second warm instance that re-registered after the kill; it is not
  evidence that one instance can survive without the kill-and-reregister.
  Reading it as "warm fixes the SIGSEGV" is already a stretch, and the
  same stretch would read "duplicate is cosmetic" from the fact that the
  display eventually comes up - which it does not yet.
- **The addresses matching as proof of same-bus.** `ADDR_DIFFER=no` in
  doc 33 compared the `DBUS_SESSION_BUS_ADDRESS` strings from AM and
  AppLauncher environments. Two processes can print the same abstract
  socket string and still have reached the session bus through different
  paths (one via the env var, one via `/tmp/session_appmgr` resolved at a
  different time against a stale file) if the socket name happened to be
  recycled. The strings are equal; whether both connections live on the
  same `dbus-daemon` pid is a different measurement
  (`fuser` / `ss -xp` on the abstract socket), and this project has not
  taken it.
- **"The handshake is happening."** The monitor captured a
  `deregistration` call, not a `registration` call. User note 3 quotes
  `member=deregistration`; user note 4 lists both methods as present in
  the app. Taking the `deregistration` capture as proof that registration
  flows is the same move as taking the interface's non-ownership as proof
  that the name is unowned - the string observed and the string assumed
  are different, and the conclusion rides on them being the same.
  **This one is live and material**: the next read of the retained log
  must confirm a `member=registration` call from `:1.36` before any
  conclusion about which hypothesis in §1 is true.
- **`launched` inform as a second registration.** Hypothesis 2 above is
  itself a guess from method-name symmetry. If the projection concludes
  "the inform is the duplicate" without seeing the second call in the
  monitor, that is the same false-negative shape in the opposite
  direction: an absence inferred from a plausibility, not a capture.

## 5. One sentence for the register

> Measurement discipline: `NameHasOwner` takes a **bus name**, not an
> interface - `com.lge.hyundai.avn.appmanager` is the name,
> `com.lge.avn.appmanager.registration` is the interface on that name; this
> project read `false` on the interface string three times before the
> captured monitor traffic (doc 33) showed the destination and corrected
> the probe.

---

## Final message

**The duplicate's likely source**: the app carries both
`registration` and `com.lge.avn.applauncher.inform.launched`, the
projection's `AppLauncher` plausibly handles both in paths that each emit
`[REGISTERED]` for AppId[11], and the 266 ms gap is the inform path
catching up to the registration path - a projection-local handler-routing
artefact, not a vendor race worth trading an offset for.

**The discriminating capture**: the full retained `/tmp/dbus-monitor.log`,
filtered to every message sent by or to `:1.36` and every call with
member in `{registration, deregistration, launched, inform*}`, with the
clock offset established by aligning the first monitor `method call` to
the first launcher `[REGISTERED]`. One call before the first `[REGISTERED]`
and no second call from the app proves manager fan-out (hypothesis 1); two
calls with different destinations proves inform-as-registration
(hypothesis 2); a `[REGISTERED]` before any app call proves the launcher
pre-registers (hypothesis 3).

**What else might be the same class of error**: that the monitor captured
`deregistration` is being read as proof the `registration` call reaches
the manager - a different string, assumed equivalent, exactly the shape
of the interface-versus-name mistake; the next read of the retained log
must confirm `member=registration` from the app's unique name before any
hypothesis in §1 is treated as settled.
