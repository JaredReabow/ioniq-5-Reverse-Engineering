# Opus 4.7, consultation 5: the surface that is not there

Date: 2026-11-06. Read-only basis: `docs/kernel/35-gate2-closed-gate5-no-surface.md`,
`docs/vm/56-endgame-runbook.md`, `docs/planning/opus-4-7-c4.md`,
`docs/vm/55-the-duplicate-is-not-the-killer.md`. No experiments, no git. This consultation
discharges the "surface/capture drift is the most likely next fault" call I made in c4 §1(a) and
§Final, and makes the next run concrete.

The state I am writing against (task preamble + doc 35):

- app 11 pid 2561 warm, labelled `App::home`, alive past 60 s;
- gate 2 **closed**: `power_status int32 1` observed after `set_power_on_status` - power-on
  consumed, not merely delivered (doc 35, doc 56 §Gate 2);
- gate 5 reads **no surface for pid 2561**: `ivi_place` returns 0/0/0, the only surfaces present are
  ivi-shell's own `30000, 1000, 1001` (doc 35);
- the id requested in our current patch - `1010` - **appears nowhere** in any list;
- the earlier run with a different id patch (`113 -> 2080`) *did* produce a surface
  (`SURFACES=[30000|2080|1001|1002|2080|1004]`, frame 120,452 B) - but `2080` is the vendor
  table's `AppCamera` slot (task preamble), so that frame was almost certainly AppCamera's chrome,
  not AppHomeScreen's layout. That is the same `2080`/`AppCamera` collision c4 §2 and doc 54
  gate 4 warned about;
- the ivi-shell binary contains a `surface_id_offset` string (task preamble) - **the shell
  computes effective surface ids with an offset**, which changes the meaning of every raw id
  number we have been reasoning about.

---

## 1. Why a warm, labelled, powered-on app creates no compositor surface - ranked

Five mechanisms. The top three are variants of "the id we patched collides with the shell's own
id arithmetic"; (d) covers "surface exists but is not listed by `ivi_place`"; (e) covers "the id
patch broke surface creation entirely". Every mechanism has a check that reads an artefact, not a
summary string.

### (a) The `surface_id_offset` mechanism remaps or rejects `1010`. Highest likelihood.

The presence of the literal `surface_id_offset` in the ivi-shell binary (task preamble) is a strong
signal that the shell computes a surface's effective id as `client_requested_id + offset` (or
indexes into a reserved window `[base, base + N)`). Two sub-cases, both consistent with doc 35's
null:

- *remapped*: the surface exists under `1010 + offset`, and `ivi_place` only enumerates ids
  outside that window, so the surface is live but invisible to our probe. This is a listing
  artefact and would be c4 §2's "benign id mismatch" generalised to an offset instead of a
  straight re-id;
- *rejected*: `1010` falls inside the shell's own reserved band (which contains `1000` and `1001`,
  task preamble), the shell refuses the client's `ivi_surface_create` with that id, and no
  surface is created at all. The log line for the refusal lives in weston; doc 35 did not
  retain weston's surface-create path.

Why it ranks first: it is the one hypothesis that *predicts* the exact listing observed in doc 35
(the shell's own `30000/1000/1001` present, no app surface) **and** the `surface_id_offset` string
is already in evidence. The `2080` run worked because `2080` is outside the shell's reserved
band - not because it was AppCamera's slot.

### (b) The id patch landed in a reserved band but outside the offset path.

Narrower variant of (a) that does not require the offset mechanism. ivi-shells commonly reserve
`[1000, 1100)` for shell-managed surfaces (background, panel, overlay). `1010` falls in that
window; `2080` and `2170` do not. The shell silently drops a client's attempt to claim a
reserved id.

Why it ranks second: it does not require the offset mechanism to also exist; it needs only a
reserved-band table, which is normal for ivi shells and consistent with `30000/1000/1001` being
the shell's own ids.

### (c) The patch at `0x475e8` overwrote one half of a pair and the app refuses to proceed.

The original bytes `71 00 00 00 7a 08 00 00` are **two** little-endian int32s: `113` (= app-id
for AppHomeScreen) and `2170` (= a second id, matching our `2170` unused-slot candidate). The
app-side code may read the pair as `{primary_surface, secondary_surface}` or
`{appid, surface_id_hint}`. Our current patch replaces the first word with `1010`
(`f2 03 00 00`) and leaves the second (`2170`) alone. If the app checks that `primary == appid`
or validates the pair, the mismatch (`1010, 2170`) fails the check and `ivi_surface_create` is
never called.

Why it ranks third: it is the simplest way the patch could have *broken creation entirely*
(the task preamble asked for this to be considered), and it is testable by looking at how the
two neighbouring words are used in the launcher binary before any further patching.

### (d) Surface created and committed, but `ivi_place` filters it out.

`ivi_place`'s "0 layers, 0 surfaces, 0 screens" is suspicious: zero *layers* is impossible if the
compositor is painting anything, so the probe is reporting an empty view, not an empty
compositor. `ivi_place` probably enumerates a particular controller scope (e.g. ids visible to
the current seat, or a named layer); a surface created in the shell's internal scope would not
appear. This is the "surface exists but is not listed by `ivi_place`" possibility the task asked
me to include.

Why it ranks fourth: it fully explains the probe output but is inconsistent with "the capture is
the 129,844-byte background" - the background would still be composited from *something*, so a
listing that omits the layer(s) involved is likely a scope issue inside `ivi_place` rather than
genuinely-empty compositor state. The capture pipeline reads a different path than `ivi_place`,
so both can disagree.

### (e) The app is still blocked on a non-Wayland dependency after power-on.

c4 §1(b) raised this: `UserProfileManager` (400), `LocationManager` (312), or a vehicle-signal
token not yet emitted. If the app got power-on but is still waiting on one of these, it will
never call `ivi_application.surface_create`, and the compositor will correctly report no
surface. The app process remains alive and labelled - consistent with doc 35.

Why it ranks fifth and not higher given gate 2: gate 2 closed means the *manager* saw power-on,
not that *AppHomeScreen* has completed its own readiness handshake. But if this were the cause,
the earlier `2080` run should also have failed to produce a surface, and it did not. It is still
on the list because the `2080` frame was almost certainly AppCamera's, not app 11's, so that
positive is weak evidence.

---

## 2. The decisive experiment, and its pre-committed null

### Your candidate: `1010 -> 2170`, everything else frozen

This is a well-posed swap - `2170` is the second word already at `0x475e8`, so the vendor
authored it as a legitimate value in that slot - and it discriminates (b) and part of (a). But
it does **not** discriminate (c): if the pair-consistency check in (c) is real, `(2170, 2170)`
is as wrong as `(1010, 2170)`. And it still leaves us arguing about a patched build.

### My replacement: a **two-run** experiment, both pre-committed, both baseline

The cheaper, cleaner question is not "which replacement id works" but "**does the vendor's own
id arithmetic produce a surface at all when we stop intervening?**" The `surface_id_offset`
string says the vendor already has a mechanism for assigning surface ids; our patches have been
fighting it blind.

**Run A - revert the id patch entirely.** Restore `0x475e8` to `71 00 00 00 7a 08 00 00`
(`113, 2170`). No other change. Run the full lifecycle. Retain:

1. `ivi_place` (same as doc 35);
2. **the raw weston log**, specifically every `ivi_application` and `ivi_surface` request/event
   for the 10 s after power-on - this is where surface-create success or refusal is logged;
3. `/proc/<pid 11>/fd | grep wayland` - proves the wl_display connection exists;
4. the compositor's complete surface table dumped from `ivi-wm -l` (or equivalent) **with owner
   pid per surface** - c4 §1(a)'s check, promoted to mandatory;
5. a `strings`-level dump of the launcher's references to `surface_id_offset` and the
   neighbouring code (one-time, host-side).

**Pre-committed null for Run A:** app 11's pid owns **no** surface in the complete
compositor-side dump (not `ivi_place`, which has already been caught scoping), **and** weston's
raw log shows no `ivi_surface_create` request from app 11's wl_client. Both must be true to
call the null. Either one alone is ambiguous.

**Pre-committed success for Run A:** app 11's pid owns one surface *S*, S's effective id equals
`113 + offset` (or `2170 + offset`, depending on which word the launcher passes), geometry
1920x720, with at least one buffer attached - the full c4 §2 reconciliation discharged with the
retained artefacts, not a probe summary.

**Run B - only if Run A's null fires:** then and only then swap `1010 -> 2170` as your
candidate does, with the same five retained artefacts. This becomes a *second* data point about
how the shell treats patched ids, not the headline experiment.

Why two runs ordered this way: Run A is the cleaner baseline (see §3), the more informative
single run (its artefacts contain `surface_id_offset`'s actual value, settling §1(a) directly),
and the one that has never been performed. Run B is your proposal, retained as fallback.

---

## 3. Baseline: revert, do not substitute

**Use Run A as the baseline.** Reasons, each traceable:

- **c4 §Final already said this**: "the fix is projection-side" wherever possible, and
  "name the offset and trade for a vendor patch" only when the vendor path is understood. Our
  current id patch was authored *before* we knew about `surface_id_offset`. It is a vendor
  patch made without understanding the vendor mechanism - exactly the move c4 warned against.
- **Doc 55's lesson**, applied generally: the probe-authored narrative ("duplicate kills the
  app") was overturned by reading the raw vendor log. Our id-patch narrative ("app 11 cannot
  be given the colliding `2080`, so change it to `1010`") was authored on the same basis -
  a probe summary of what ids *appear* to be in use, without reading the shell's own id
  arithmetic. Reverting restores the vendor's authored state so the raw log is interpretable
  without our intervention as a confound.
- **The `2080` positive is poisoned**: the surface that appeared in that run was in
  AppCamera's slot and almost certainly AppCamera's chrome (task preamble, c4 §2, doc 54
  gate 4). So "patching produced a surface once" is not a credit toward "keep patching"; it is
  a near-miss that should have been a red flag at the time.
- **Degrees of freedom**: the current approach picks one of several unused ids and hopes;
  revert collapses the id dimension to the vendor's own choice, leaving one variable - whether
  the vendor pipeline produces a surface at all - as the measured quantity. Fewer variables,
  higher-information run, Astra's discipline in doc 56 §Gate 5.

Substituting `1010 -> 2170` is still a patched build, and it still assumes the patch *should*
exist. Reverting asks whether the patch should exist at all. That is the cleaner baseline and the
one Run A tests.

---

## 4. Judging gate 5's null: "the app draws where nothing reads"

**Premature.** Doc 35 phrases it as "the honest conclusion" and "a named limitation with one
mechanism, not an open question". On the evidence actually retained - `ivi_place` output plus the
weston surface list showing only shell-owned ids - the stronger claim it supports is:

> Under the current id patch and under `ivi_place`'s scope, no surface attributable to app 11 is
> listed, and the captured frame is the 129,844-byte background.

Four reasons the stronger claim "the app draws where nothing reads" is not yet earned:

1. **`ivi_place` reported 0 layers**, which cannot be true if the background is being composited -
   so `ivi_place` is scoped, not comprehensive (§1(d)). Doc 35 treats its output as a complete
   compositor census; it isn't.
2. **Pid-owned surface mapping was not retained.** c4 §1(a) asked for `ivi-wm -l` with owner pid
   or equivalent; doc 35 shows only id lists without pid attribution. "No surface for pid 2561"
   is inferred from the absence of `1010` plus the absence of ids that aren't the shell's own -
   but a shell that uses `surface_id_offset` would list app surfaces under `offset + requested`,
   none of which we have the offset for.
3. **weston's surface-create path was not retained raw.** If the app tried to create a surface
   and was refused, the reason is in weston's log; doc 35 does not cite it. Without that, we
   cannot distinguish "never tried" from "tried and was refused" from "tried, was granted, and
   `ivi_place` does not list it".
4. **`/proc/2561/fd` not reported.** The cheapest discriminator for "app has a wl_display
   connection at all" is one `ls` line. Doc 35 did not retain it.

**Honest reformulation for the changelog**, in the spirit of doc 55's withdrawal of
`WARM_DUPLICATE=1`:

> The one retained compositor probe shows no app-11 surface and the capture is background. We
> have not yet retained the artefacts (pid-mapped surface table, raw weston log,
> `surface_id_offset` value) that distinguish "the app did not create a surface" from "the shell
> re-ided it outside our probe's scope". Gate 5's null is **not yet called**.

This is exactly rule 17-19's discipline applied to *our own* conclusion rather than to the
vendor's behaviour.

---

## 5. When Run A fails too: next mechanism, and the stopping rule

### Next mechanism if Run A null fires on both criteria (no owning surface in pid-mapped table *and* no `ivi_surface_create` from app 11's wl_client in raw weston log)

Then the fault is **upstream of surface creation**, and §1(e) is promoted: the app's QML
scene-graph is not reaching the point where it would call into Wayland. Two concrete candidates
to probe in that order:

1. **A readiness dependency the app is blocked on after power-on consumption.** `UserProfileManager`
   (400), `LocationManager` (312), `TmsGuiApp` (200), or a vehicle-signal token on a separate
   bus. Discriminator: retain app 11's own stderr for the full 90 s window and `grep` for the
   first line that *follows* the `power_status` signal. "Waiting for X" or "X not available" is
   diagnostic without any further probe (c4 §1(b)).
2. **A QML/graphics initialisation failure that keeps the app alive but non-rendering** - EGL
   context creation, `QT_QPA_PLATFORM` mismatch under bochs-drm, or a missing font/image resource
   that the scene-graph is still trying to load. Discriminator: `strace -f -e trace=open,openat`
   on pid 2561 for the 10 s after power-on, retained raw; a tight loop on a missing path is
   diagnostic.

### The two-sentence stopping rule for the whole display thread

> If Run A (id patch reverted) produces no surface owned by app 11's pid in a pid-mapped
> compositor dump **and** no `ivi_surface_create` request from app 11's wl_client in the raw
> weston log, and if the follow-up readiness probe shows no "waiting for" line and the open-trace
> shows no tight-loop on a missing resource, then the HMI image is not reconstructible under the
> current vendor binaries without new reverse-engineering of the home-screen's surface-acquire
> path. In that case, publish the retained lifecycle evidence (kernel + DRM + seat + socket +
> registration + label + power-on-consumed) as the achieved milestone, record `surface_id_offset`
> as the next entry point for any future attempt, and move the project to its security-register
> items (c4 §4: FDE engagement, SMACK accesses.d re-audit under `App::home`, and the
> `com.lge.hyundai.avn.appmanager` trust-boundary review).

This is the first stopping rule in this thread. It is here because every gate from doc 56 is now
either closed or has a concrete, falsifiable next check; past this point the project is spending
effort *inside* a boundary (the home-screen's graphics stack) whose reverse-engineering cost
exceeds the security-register items' value.

---

## Final message

**Ranked cause:** the most likely reason a warm, labelled, powered-on app creates no visible
compositor surface is the **`surface_id_offset` mechanism** - the ivi-shell computes effective
surface ids by offset (the binary literally contains that string), our patched `1010` either
collides with the shell's reserved band or is remapped outside the scope `ivi_place` enumerates,
and the "no surface" reading is partly a probe-scope artefact (`ivi_place` reports 0 layers,
which is impossible if the background is being painted). Second-most-likely is the same
mechanism's rejection path: `1010` is inside the shell's reserved band and the shell silently
refuses the create. Third is that our patch broke creation entirely by overwriting one word of a
two-word pair at `0x475e8` (the original `71 00 00 00 7a 08 00 00` is `{113, 2170}`, a pair the
launcher may validate).

**Decisive experiment:** **Run A - revert the id patch entirely** (restore `0x475e8` to
`71 00 00 00 7a 08 00 00`, i.e. let the vendor's own `{113, 2170}` stand) and retain five
artefacts in one run: `ivi_place`, the raw weston log scoped to `ivi_application` /
`ivi_surface`, `/proc/2561/fd`, a pid-mapped compositor surface dump (`ivi-wm -l` or equivalent),
and a one-time `strings`-level dump of the launcher's `surface_id_offset` references. **Pre-committed
null:** app 11's pid owns no surface in the pid-mapped dump **and** weston's raw log shows no
`ivi_surface_create` from app 11's wl_client. **Pre-committed success:** app 11's pid owns one
surface at 1920x720 with a buffer attached, whose effective id is `offset + 113` or
`offset + 2170`. Your `1010 -> 2170` swap is Run B, kept as a fallback only if Run A's null
fires.

**Baseline recommendation:** **revert** (your option 3). Substituting a different unused id is
still a vendor patch authored without understanding `surface_id_offset`, which is exactly the
move c4 §Final advised against ("name the offset and trade for a vendor patch" - we had not
named the offset, so we should not have patched). Reverting collapses the id dimension to the
vendor's own choice, leaves surface creation as the single measured quantity, and makes the raw
weston log interpretable without our patch as a confound. If, after Run A, the home screen
genuinely never creates a surface, the stopping rule in §5 applies and the display thread ends -
honestly, with the lifecycle milestone retained and the security-register items as the next
hour's work.
