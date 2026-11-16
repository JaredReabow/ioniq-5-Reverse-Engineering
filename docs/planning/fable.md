# fable.md — experiments and stopping rules

Date: 2026-11-06. Author: Fable 5.1, one of three independent planners (see `planning/README.md`).
Read-only plan. No experiment was run and no vendor binary was patched to produce it. Every claim
below cites a file I read: `docs/CURRENT-STATE.md`, `docs/vm/45-backend-is-forced-not-chosen.md`
(§§54-65), `docs/kernel/25-registration-warm-fast-but-still-killed.md`,
`docs/kernel/26-second-kill-is-sigsegv.md`, `docs/REMEDIATION-REPORT.md`,
`docs/root-access-paths.md`, `docs/defences/controls-inventory.md`.

**The baseline these experiments build on** (`45-…md` §§48-51, `kernel/20`, screenshot
`docs/vm/49-surface-id-patched-app-standby-composited-2026-11-06.png`): rebuilt `4.1.27-abl`,
`bochs-drm` → `/dev/dri/card0` at native 1920x720, vendor `drm-backend.so` binds it, the seat fix
gives a Wayland socket, and the **one-entry surface-id row for app id 11** in `AppLauncher`'s
`(appId, surfaceId)` table (`AppLauncher.patched.bin`) composites the app's standby face
(120,452 bytes). What is *not* reached is the laid-out home screen: the warm instance faults ~24 s
into the power-on layout (`kernel/26`).

**Two standing cautions, both paid for already.** (1) Add **exactly one instrument at a time** and
never process-wide — the `/etc/ld.so.preload` CAN shim and a racing `ivi-wm` placement each killed the
app under test and were read as vendor behaviour (`CURRENT-STATE.md`, top box). Every shim below is
**scoped to the app or launcher only**. (2) **Check the text before the pixels** — frame *size* is not
an identifier (standby measured 114,782 / 120,562 / 131,845), so no capture counts until the named log
line has been read (`45-…md` §8, §12, §18).

---

## 1. The next three display experiments

All three move the warm, surface-id-patched instance from the standby face toward the laid-out home
screen. Doc `kernel/26` names the ~24 s fault's two candidate causes — *CAN-backed widget data* or a
*DRM-side rendering surface* — so the order below tests the more likely (data) first, then the two
concrete, app-named device gaps. Each changes **one variable**, is **one boot**, is **projection-side**
(no new vendor offset), and has its textual gate stated before any capture.

### Experiment 1 — CAN SOC frame present vs absent

- **Single variable:** whether the application's raw-CAN widget feed carries one real frame.
- **Exact change/command:** app-scoped only — `LD_PRELOAD=/opt/can_shim.so /app/bin/AppHomeScreen`
  (never `/etc/ld.so.preload`, per the top-box warning), delivering the frame pinned from the
  real-vehicle logs: **`0x2fc`, byte 7 = 119 → 59.5 %** (`CURRENT-STATE.md` §"SOC frame is pinned";
  path is `AppPHEVModel`→`slot_CR_Bms_DisplaySoc` via `connectCanListenerSignals`,
  `docs/vehdata/01-battery-range-data-path.md`). Trigger the layout with the established
  `set_power_on_status int32:1 int32:0` **after** app 11 owns its bus name (`CURRENT-STATE.md` §0).
- **Textual check before any pixels:** in the app/launcher log for the 24 s window after registration,
  `[ERR CODE:1] App has been Crashed` and `appProcessFinishedSlot [*][0][1][11]` must be **absent**, and
  `injectWidgetItemToAdvancedPage … FOUND` must advance past the fault site without a following
  `Trace/breakpoint trap` or SIGSEGV (`kernel/26`). Only then capture.
- **What each result means:** crash gone → the ~24 s death was the missing-CAN stand-in gap
  (`kernel/26`'s leading hypothesis confirmed), and the widgets should now read ≈59.5 % / ≈287 km
  instead of `---` (ground truth ≈4.4 km/pt, `evidence/vehdata-ground-truth.md`). Crash unchanged *at
  the same site* → the fault is EGL/DRM-side, not data → Experiment 2.

### Experiment 2 — the GPIO kernel nodes the app opens and cannot find

- **Single variable:** whether `Home_Worker::writeGPIO`'s computed kernel paths resolve.
- **Exact change/command:** app-scoped `open()` interposer (one shim, launcher's child only) returning a
  writable temp fd for the computed GPIO node paths the app opens, or `mknod` those nodes before launch.
  This is the concrete lever the app's own log names: `Home_Worker::writeGPIO -> Open kernel file
  failed!, errorNo: 2` (`CURRENT-STATE.md` §6.2 "If you have one hour"), and the page notes **stubbing
  them is cheaper than a driver**.
- **Textual check before any pixels:** `Open kernel file failed!, errorNo: 2` disappears from the app
  log and the layout stage proceeds past where it previously stopped. Only then capture.
- **What each result means:** line gone and layout advances → a missing GPIO node was a layout
  precondition (cheap projection-side fix, no kernel driver). Line gone but the frame is still the
  standby/background → GPIO was not load-bearing for layout; the fault is deeper in the EGL path →
  Experiment 3.

### Experiment 3 — the SQLite commit the app retries 23 times

- **Single variable:** whether the home-screen DB commit succeeds.
- **Exact change/command:** give the app a writable DB location with correct ownership (projection-side:
  stage the 36,864-byte DB file on a `rw` path the app can `COMMIT` to) and raise SQLite's own error
  text, which is currently suppressed (`CURRENT-STATE.md` §6.2: `DB UPDATE COMMIT FAIL` ×23, "no error
  text is printed; the next read is the SQLite error itself").
- **Textual check before any pixels:** the `DB UPDATE COMMIT FAIL` count drops to 0, **or** the boot now
  prints the underlying SQLite error string. Only then capture.
- **What each result means:** commits succeed → one recurring layout precondition removed, and the
  captured frame is the real test. Still failing → the boot has at least *named the errno* (read-only
  FS, locked DB, disk-full), which is the next fix rather than a fourth guess (`45-…md` §59).

---

## 2. The ~24 s second termination, and the one log read that separates the candidates

A warm instance (pid 2606) registers at `21:40:33.644` and is gone at `21:40:57.199` — ~24 s later, on
a fixed interval independent of the 45 s preload deadline (`kernel/25`, `45-…md` §65). **The project's
own record disagrees on the mechanism, and the disagreement is exactly what the window read settles:**
`kernel/25` and `45-…md` §65 report `appProcessFinishedSlot [15][0][1][11]` (exit 15 = **SIGTERM**);
`kernel/26`, written three minutes later, reports `[ERR CODE:1] App has been Crashed` then
`appProcessFinishedSlot [11][0][1][11]` (exit 11 = **SIGSEGV**). Both cite the same pid and the same
timestamp. One of them misread the leading byte.

**Candidate mechanisms, in likelihood order:**

1. **The application faults (SIGSEGV) in the power-on widget/EGL layout** — `kernel/26`'s reading, and
   the same crash family as the earlier `SCREEN_STATE: START DRAW` → `injectWidgetItemToAdvancedPage …
   FOUND` → `Trace/breakpoint trap`. This is a **stand-in problem** (missing CAN data or DRM surface),
   which is the class this project builds for, and it is why §1 leads with CAN.
2. **An app-alive / liveness watchdog SIGTERMs the unshown instance** — the manager's
   `AB010512*time*…-hang` → `appTerminateSlot` pattern already seen for engineering mode
   (`CURRENT-STATE.md` §1b). Exit 15, but driven by a second *policy*, not by a fault.
3. **The duplicate-registration guard re-fires** — `onDemandAppKill` / `[REGISTERED ERROR] Already
   registered`, the same guard that killed the cold instance (`45-…md` §62, `kernel/25`). Also exit 15,
   but it would recur on a fixed re-arm rather than once.

**The one log read, `21:40:33` → `21:40:57` (boot 46 launcher log, `work/vm/kbuild/boot46-deadline.log`):**
read the **leading byte of `appProcessFinishedSlot [N][0][1][11]`** together with whichever of three
lines precedes it in the window:

- `N == 11` with `[ERR CODE:1] App has been Crashed` → **candidate 1** (crash; stand-in problem) —
  confirms `kernel/26`, refutes §65.
- `N == 15` with `AB010512…hang` / `appTerminateSlot` → **candidate 2** (liveness watchdog).
- `N == 15` with `[REGISTERED ERROR] Already registered` / `onDemandAppKill` → **candidate 3**
  (duplicate guard) — confirms §65, refutes `kernel/26`.

That single byte-plus-preceding-line read decides which section-1 work is on the critical path, and it
costs no boot: the log already exists.

---

## 3. Stopping rule for the display thread

Phrased so a future reader can decide **continue or stop** without re-deriving the history:

> **Continue** only while each boot does one of two things: (a) carries the application **past a
> textually-named failure line it did not previously pass** (e.g. the `[TIMEOUT] [2 Group]`,
> `App has been Crashed`, `Open kernel file failed!`, or `DB UPDATE COMMIT FAIL` lines above), or
> (b) converts a *mystery* into a **named, patchable cause** (a specific errno, offset, or missing
> device node). A saved frame is **never** evidence on its own — the governing log line must be read
> first (`45-…md` §8, §12, §18; size is not an identifier).
>
> **Stop, and declare the blocker** (named, with the instrument that would settle it, as in `45-…md`
> §59) when **either**: the laid-out home screen is captured with Battery/Range showing **non-placeholder
> values** (≈59.5 % / ≈287 km, not `---`) and the governing log line confirms it — *the display goal is
> met*; **or** two consecutive boots each change their single variable **without** moving the first
> textual failure line **and without** naming a new cause — *the thread has reached a limitation, not a
> mystery, and a third guess is wasted effort* (`45-…md` §57, §59; the surface-id table was a right
> guess, the app-load timer was a wrong one twice over — reading a constant and reading its effect are
> different skills).

The honest current reading of this rule: the thread is **not** yet at "stop." The warm/cold split
(`45-…md` §64) removed the timing miss as a cause, Experiment 1 tests `kernel/26`'s named crash cause,
and neither has been run — so progress is still available by the (a)/(b) test.

---

## 4. The five remediation items a platform team should do first

From the 26 items in `REMEDIATION-REPORT.md` (Tier-1 leverage items are 15, 16, 21, 22; controls
#1/#2 in `defences/controls-inventory.md` are the *correct-in-form-but-unenforced* ones). Ranked for a
platform team by **impact per hour of config-only work**, because the cheapest here also remove the
most:

1. **Item 15 / V-064 — harden the 106 root services** (`NoNewPrivileges=yes`, reduced
   `CapabilityBoundingSet=`, `ProtectSystem=strict` + `PrivateTmp=yes`, `User=` where root is not
   needed). This is the report's named leverage item: it is *why* "root-only bus" is not a boundary, and
   `PrivateTmp=yes` alone **neutralises several `/tmp`-anchored findings at once**. Config-only, no
   application code. Verify: `NoNewPrivileges=` count across `/lib/systemd/system/*.service` must be
   non-zero.

2. **Item 16 / V-065 — repoint the nine `/etc` trust anchors out of world-writable `/tmp`** to
   `/run/etc/*` (0700 dir, 0600 root-owned). **One change fixes all nine**, and the consequence is
   already demonstrated (a `uid=0` account appended to `/tmp/passwd` resolved via NSS, V-054). The
   destination is the only mistake — the read-only-root reason for a writable config is legitimate.

3. **Item 4 / V-052 — stop a filesystem probe from turning MAC permissive.** Derive `optUNECE` from a
   signed build property or fuse, not from `cryptsetup isLuks` on a data partition that ships as plain
   tar. **Correct in form but unenforced:** SMACK is loaded with 636 specific rules
   (`controls-inventory.md` #2), but `smack_setup.sh` switches it to **permissive** when the probe reads
   0 (measured 0). Fixing the probe makes the *existing* policy effective rather than replacing it, and
   makes an unrecognised partition fail **closed**.

4. **Item 21 / V-071 — invert the console/SSH default.** `esinit` `touch`es
   `/tmp/secure_console_disable` **every boot**, and that one marker gates the root `ttyS2` console, the
   shell-bearing `passwd.legacy` account database, and `dropbear@.service` (V-067). Create it only when
   MICOM reports a debug state, move it to a root-owned path, and drop `passwd.legacy` from production.
   **Fail-open default** closed with one script change; one chain, three capabilities.

5. **Item 1 / V-056 — apply the `App::*` SMACK labels the policy already defines**, then (only then)
   enforce. **Correct in form but unenforced:** the 636-rule, 28-label policy loads at boot, but nothing
   in the artifact applies the labels (no `chsmack -e`, no `SmackLabel=`, no xattrs in
   `mango-rootfs.tar.gz`), so applications run as `_` and the policy constrains nothing that parses
   attacker input. Verify first on a unit (`getfattr -n security.SMACK64EXEC /app/bin/AppHomeScreen`);
   label before enabling, because the enforcing branch already shows 40 denied decisions.

**Which of the five are already correct in form, only unenforced:** items **4** and **1** (and, in the
same family, item 14 / V-063's `context="default"` allows). `controls-inventory.md` states it directly —
"#1 and #2 are already correct in form; the fixes in V-063 and V-052 make them effective rather than
replacing them." Items **15, 16, 21** are structural fixes that move a decision off untrusted state.
All five serve the report's single sentence: *never resolve a security decision from a writable path,
and make every such check fail closed.*

---

## 5. Checks that would make an external reviewer trust the register more

1. **Publish the output of `sh tools/check_all.sh`** alongside the register. `CURRENT-STATE.md` says the
   suite verifies the register's numbering and cross-references, that the history log has not been
   rewritten, and that every document reference resolves — and that it "exists because three defects
   survived careful reading." A register that **mechanically self-verifies**, with the run attached, is
   worth more to a reviewer than one asserted to be consistent.

2. **Mark every claim as projection-only or vehicle-confirmed, and reproduce at least one anchor off the
   projection.** `root-access-paths.md` opens with "Nothing here has been tried on a vehicle," and
   `REMEDIATION-REPORT.md` item 1 concedes the shipped archive carries **no xattr records**, so the
   projection "necessarily shows `_`" whether a real unit does or not. The "demonstrated" anchors
   (V-054 account append, V-052 `optUNECE=0`) presently rest on the projection alone; one measured
   reproduction on hardware — or an explicit per-entry projection-only tag — closes the gap a reviewer
   will probe first.

3. **Reconcile the register's own contradictions and its drifting counts.** The second-kill exit code is
   reported as both SIGTERM `[15]` (`kernel/25`, `45-…md` §65) and SIGSEGV `[11]` (`kernel/26`) for the
   same pid and timestamp (§2 above resolves it with one read). Separately, the finding count is quoted
   as 75, 70, 60 and "13 relevant," and fix items as 20 and 26, across `CURRENT-STATE.md`,
   `REMEDIATION-REPORT.md` and `controls-inventory.md`. A single authoritative count and a resolved
   exit-code byte — the kind of drift `check_all.sh` is meant to catch — are the cheapest signals that
   the record tracks the measurements rather than the momentum.

---

## Final message

**Three experiments (one line each):**
1. CAN SOC frame present vs absent — app-scoped `can_shim.so` delivering `0x2fc` byte 7 = 119 (59.5 %); gate: `App has been Crashed`/`appProcessFinishedSlot [*][0][1][11]` absent and `injectWidgetItemToAdvancedPage … FOUND` advances, then capture.
2. GPIO kernel nodes — app-scoped `open()` stub (or `mknod`) for `Home_Worker::writeGPIO`'s computed paths; gate: `Open kernel file failed!, errorNo: 2` gone and layout advances, then capture.
3. SQLite commit — writable DB path + raised error text; gate: `DB UPDATE COMMIT FAIL` count → 0 or the SQLite errno printed, then capture.

**Single most valuable next action:** read the leading byte of `appProcessFinishedSlot [N][0][1][11]`
and its preceding line in the `21:40:33`→`21:40:57` window of `work/vm/kbuild/boot46-deadline.log` —
it costs no boot, resolves the project's own `[11]`-vs-`[15]` contradiction, and decides whether the
remaining display work is a stand-in problem (crash → Experiment 1) or a policy kill (watchdog/duplicate
guard).

**Stopping rule:** continue only while each boot carries the app past a textually-named failure line it
had not passed, or converts a mystery into a named cause; stop when the laid-out home screen is captured
with real Battery/Range values (goal met) or when two consecutive single-variable boots move neither the
first failure line nor name a new cause (limitation, not mystery — declare the blocker rather than guess
a fourth time). A saved frame is never evidence until its governing log line is read.
