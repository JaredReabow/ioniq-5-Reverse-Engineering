# Opus 4.7, consultation 4: after the label is measured and the warm instance registers in time

Date: 2026-11-06. Read-only basis: `docs/kernel/34-label-measured-warm-registers-in-time.md`,
`docs/vm/55-the-duplicate-is-not-the-killer.md`, `docs/vm/54-retention-correlation-and-the-seven-gates.md`,
`docs/MEASUREMENT-DISCIPLINE.md` rules 17-19. No experiments, no git.

Astra's seven gates are the spine. Gate 1 (lifecycle closure) is done on raw evidence: pid 2516,
`[REGISTERED]` with **no preceding `[TIMEOUT]`**, `ClearTimeoutLoading : 11, PID : 2516` on its own pid,
`LABEL=[App::home]`, `PS_LABEL=[App::home]`, alive past 60 s (doc 34). Gate 2 (power-on consumed, not merely
sent) is where this consultation lives.

---

## 1. The single most likely thing to be wrong next

Ranked, cheapest discriminating check first.

**(a) The capture is reading the wrong surface.** Highest probability. The launcher was told `1010`,
the compositor reported `APP_SURFACE_ID=[1005]`, and this is **unreconciled** (task preamble). Every
previous "home frame" in this project was later found to be either standby chrome or, once,
`AppCamera` on the colliding `2080` (doc 54 gate 4). The raw symptom - "power-on sent, nothing on
screen, process alive, label right" - is exactly what surface-capture drift produces.

*Cheapest discriminating check.* One retained dump of the compositor's surface registry with
**owner pid** alongside each surface id, taken while 2516 is alive. If pid 2516 owns `1005`, the shell
assigned its own id and 1005 is the surface to capture; if pid 2516 owns `1010`, the launcher's id is
authoritative; if it owns neither, the fault is upstream of layout. One `ivi-wm` list retained raw -
no probe-assembled summary, rule 19 - settles all three.

**(b) Power-on was received but the application is waiting on a non-Wayland dependency.** AVN home
screens typically block layout on at least one of: a vehicle-signal token (CAN/IPC gateway), a
`UserProfileManager` ready signal, a `LocationManager` fix, or a persistent-store read. The register
shows all of these as separate appids (40, 400, 312); if any of them is `[REGISTERED]` but not yet
`emitted READY`, AppHomeScreen will sit on standby chrome indefinitely. Discriminator: retain the
launcher stderr for pid 2516 for 90 s and `grep -n` for the first line that follows `power-on`;
"waiting for X" is diagnostic without any further probe.

**(c) Power-on was delivered to the dead cold instance (2331), not the warm one (2516).** Lower
probability because doc 34 shows `ClearTimeoutLoading` on 2516, but the launcher's power-on routing
is a separate code path from its timeout-clearing code path, and the duplicate-registration record
(doc 55) proves the manager holds **both** registrations transiently. Discriminator: in the retained
launcher log, find the `power-on` dispatch and read the `PID` on the same line. Free if the log is
already retained.

**(d) A denial at the layout path.** SMACK exec-label is now right (doc 34), but a *second* object
class - the Wayland socket, an SHM pool, or a specific `/dev/dri/*` node - may still deny under the
new label. Rule 2 is a warning that policy lives in files, not in writes. Discriminator: `dmesg -T |
grep -i 'smack\|avc'` for 2516's uid in the 10 s window around power-on. Free.

The top check (a) costs one retained surface dump and discriminates the fault that has the strongest
prior given this project's history (two previous frames were mis-identified for exactly this reason).

---

## 2. The surface-id reconciliation: benign or diagnostic?

**Verdict: not yet determined, and the project cannot afford to assume benign.** Wayland
`wl_surface` ids are client-local and the IVI shell routinely re-ids them server-side; a launcher
request of `1010` becoming a compositor-assigned `1005` would be benign in most shells. But:

- the only previous time this project resolved a surface mismatch, the "home" frame was
  `AppCamera` at `2080` (doc 54, preamble);
- `APP_SURFACE_ID=[1005]` was "seen once" (preamble) - a single observation, no retention qualifier,
  from a probe that this project has already caught assembling conclusions (rule 19);
- the capture pipeline is addressed by surface id, not by pid. If the capture reads `1010` and the
  shell draws on `1005`, the capture will **always** show the previous frame on 1010 (standby
  chrome, held by another layer). That exactly matches the observed symptom.

**What settles it in one run.** Retain the compositor's complete surface table with owner pid and
intended geometry (`ivi-wm -l` or the shell's equivalent dump, captured raw to the host-retained
evidence volume, Astra's contract in doc 54 §Second). Then, in the same run, retain the pid→fd→
socket mapping for 2516 (`ls -l /proc/2516/fd | grep wayland`). Two retained artefacts, one
reconciliation:

- if pid 2516 owns `1005` with geometry 1920x720 → benign, the capture pipeline is reading the
  wrong id, fix is projection-side (point the capture at `1005`);
- if pid 2516 owns `1010` and `1005` is owned by the shell itself → benign *and* the launcher id is
  authoritative, fix is to re-run the capture against `1010`;
- if pid 2516 owns neither → the app is drawing nowhere the compositor serves, the fix is a vendor
  patch in the home screen's surface-acquire path (name the offset, trade for a projection-side
  shim that assigns on behalf of the app only in the engineering build).

One run, one dump, no further probes. This is the discriminator in doc 54's §Fourth table reused
for a different question.

---

## 3. Honesty risk: probability the next "success" is also an artefact

**Base rate from the last hour.** Three instrument-induced false negatives (rules 17, 18, 19) plus
doc 55's withdrawal of `WARM_DUPLICATE=1`. All four looked like vendor faults; all four were the
probe. Rules 11 and 14 add two more recent misreads (PNG byte-size as state, counter without the
logfile size). That is **six probe-induced wrong findings in roughly 24 h**, against which the only
verified positive (doc 34's label and registration) was earned by *retaining the raw launcher log
and reading it directly*.

**Estimate.** If the next capture is published without the retention/negative-control discipline
of doc 34, the prior that it is also an artefact is roughly **50-60 %** - the honest base rate
from the sample. If it is published with doc 34's discipline (raw retention, both-clocks
correlation, pid-named surface, negative control for the standby frame), the prior drops to around
**15-20 %** - the residual being genuine vendor faults that the project has not yet seen.

**The pre-commitment that protects against it.** Written before the run, hashed into the evidence
volume at boot, four lines:

1. **The literal success string**, in words a second reader can check without the artefact -
   e.g. "AppHomeScreen pid 2516 owns surface S, S is 1920x720, the frame at S contains the Battery
   gauge and the Range readout placed in their home-layout positions, not the KIA logo and not
   dark chrome" (rule 11's "KIA logo and no widgets" negative control, inverted).
2. **The negative control**, also in words: "a standby frame at S looks like <describe>, and that
   counts as *not yet success* even if the byte size is new" (rule 6, rule 11 corollary).
3. **The retention manifest** that must exist after the run: raw launcher log, raw compositor
   surface dump, pid→fd map, the PNG itself with its owning surface id and pid recorded in the
   filename (`run/<runid>/pid2516-surface1005-frame.png`), both-clocks marker (doc 54 §Third).
4. **The instrument's positive control**, pre-run: the capture pipeline is proven to read a
   known-good surface from a known-good pid *in the same run*, before the measurement that counts
   (rule 17's "the instrument must first read a value it already knows").

Any success claim that cannot cite all four lines is treated as `NOT MEASURED`, exactly as rule 17
specifies for the instrument side.

---

## 4. Three highest-value security hours, with the display thread nearly closed

The register has 75 entries and 26 items; most are catalogue. With Gate 1 closed and only
reconciliation and consumption between the project and a verified home screen, security attention
should return to the three surfaces that the vehicle actually exposes to an attacker:

**Hour 1 - the FDE engagement path.** Rule 3's case is still partly open: encryption engages when
`optUNECE=1` is read from a module parameter, and that parameter's provenance (who writes it, with
what authority, whether a user-controlled input can flip it) was never finished. One hour of reading
the esinit path and the module-parameter write sites answers the single question that matters for
every other data-at-rest finding in the register: **is the perimeter authentic, or is it a
projection-only property of the engineering harness?** Rule 3 explicitly warns that this project's
own instrument once forced `optUNECE=1`; the hour pays for itself by retiring that confound.

**Hour 2 - the SMACK accesses.d audit through the lens of the new exec-label fix.** Rule 2: 27
files, 636 rules in `/etc/smack/accesses.d/`. The label fix in docs 27/28/34 changed the subject
label the warm instance runs under. One hour enumerating which of those 636 rules now grant
`App::home` access to objects that the previous (wrong) subject label never reached - and which of
*those* objects are user-reachable at runtime (sockets, device nodes, configuration files) - turns
the exec-label fix from "it now runs correctly" into "it now runs correctly *and here is what else
that means it can touch*". Higher value than catalogue items because the attack surface moved with
the fix and no one has re-measured.

**Hour 3 - the `com.lge.hyundai.avn.appmanager` registration bus, now that the duplicate is known
to be benign.** Doc 55 showed that `[REGISTERED ERROR] Already registered` does not terminate.
That is a vendor-side authentication weakness worth one hour: enumerate what an unprivileged peer
on the session bus can do on that interface - can it re-register as `AppHomeScreen`, inject its
own power-on, or shadow a legitimate app's surface claim? Rule 18 reminds us the interface was
misidentified three times; the counter-move is to **monitor the real interface for an unauthorised
caller**, with a retained `dbus-monitor` and a negative control (a deliberately-unauthorised peer's
attempt, under projection). Higher value than the rest of the register because it tests a
pre-authenticated code path on a bus the entire launcher state machine trusts.

**What makes these three higher value than the remaining 23 items.** Each one tests a *boundary*
that the recent fixes moved: FDE (the data perimeter), SMACK accesses.d (the containment surface
under a new subject label), and the registration bus (the trusted-peer boundary that the duplicate
proved is not strictly enforced). The remaining register entries are mostly measurements *inside*
those boundaries; they do not change when the boundary is re-measured, and they are not falsified
by the last 24 h of instrument lessons. The three above are.

---

## 5. Two-sentence changelog, for the six-month reader

> The warm instance of `AppHomeScreen` was proven, on a retained raw launcher log, to register
> in time (pid 2516, no preceding `[TIMEOUT]`, `ClearTimeoutLoading : 11, PID : 2516` paired on
> its own pid) and to run with the authentic SMACK exec label (`LABEL=[App::home]`,
> `PS_LABEL=[App::home]`), closing the registration and lifecycle blockers that had stood for the
> prior forty runs and the duplicate-registration red herring with them. No home frame was
> captured in this run; what remains between the project and an interactive screen is surface-id
> reconciliation (launcher `1010` vs compositor `APP_SURFACE_ID=[1005]`) and retained proof that
> power-on was *consumed*, not merely sent — not registration, and not the label.

---

## Final message

**Most likely next fault:** the capture is reading the wrong surface - the launcher's `1010` and
the compositor's `1005` are unreconciled, and this project's prior for "the frame looked wrong
because the capture read the wrong surface" is the strongest it has (the `2080`/`AppCamera`
collision set the precedent). Cheapest discriminator: one retained `ivi-wm` surface dump with
owner pid alongside each id, in the same run as the capture.

**Surface-id verdict:** not yet benign, not yet pathological - **unreconciled**, and the project
cannot assume benign given its own history. One retained run with the full compositor surface
table *and* `/proc/2516/fd` settles it; if pid 2516 owns `1005`, the fix is projection-side (point
the capture at `1005`), and nothing else needs to change. If it owns neither, name the offset in
the home screen's surface-acquire path and trade for a vendor patch.

**Closing statement (two sentences):** The warm instance of `AppHomeScreen` was proven, on a
retained raw launcher log, to register in time and to run under the authentic SMACK exec label,
closing the registration and lifecycle blockers that had stood for forty runs. What remains
between the project and an interactive screen is surface-id reconciliation and retained proof
that power-on was consumed - not registration, and not the label.
