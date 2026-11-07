# Opus 4.7 — Consultation C7 (post-boot65)

Date: 2026-11-06. Read-only review of boot65. Every claim here is cited to a file
read this turn; no file was written except this one.

## 1. Root cause of "zero screens", ranked

The evidence restricts the fault to a very narrow region: a screen for
`Virtual-1` is never created, and neither of the two currently-loaded ivi
modules has a path that would create one.

| Rank | Hypothesis | Evidence for | Evidence against |
|---|---|---|---|
| **1 (strongest)** | **No stock IVI-controller client is running, so nothing ever calls `ivi_controller.screen_create`.** | `docs/kernel/39` static: `ivi-controller.so` exports `create_screen` as the protocol entry point, i.e. screens are created *by a client*. `ivi-window-manager.so` exports layer-management symbols but has **no `output_created` symbol**, so there is no auto screen path from the drm output. `docs/kernel/37` confirms *none* of the loaded modules nor `weston.real` reads `ivi-shell-user-interface`, and `pgrep -f ivi-shell-user-interface` was empty — the client that would normally talk to ivi-controller is simply not launched. | None in the files read. |
| 2 | **Missing hmi-controller (or its stock equivalent).** The vendor template does not load `hmi-controller.so`, and when boot62 forced it in, `hmi_controller_create` failed with "Failed to initialize hmi-controller". | `docs/kernel/38`: hmi-controller is the only loaded component that *reads* `ivi-shell-user-interface` and calls `create_layer` — but it calls `create_layer`, not `create_screen`, and its init requires screens to already exist (boot62 failed exactly because `0 screens`). | Evidence shows hmi-controller is downstream of screen creation, not its author. It cannot itself be the screen producer. |
| 3 | **Output/listener ordering** (ivi-layout registers its output listener after the drm output already exists, so a one-shot `output_created` edge is missed). `docs/kernel/39` raises this as "the next check". | Plausible on paper. | Falsified by the same static read: `ivi-window-manager.so` has **no `output_created` symbol at all**, so there is nothing to miss the edge of. Ordering can only be a secondary amplifier of (1), not an independent cause. |
| 4 | **Wrong output identity** (Virtual-1 named differently than the stock expects). | `docs/kernel/39` confirms drm names the output `Virtual-1`. | Would at most change which screen is created, not whether any screen is created, given (1). No file shows a name filter in a loaded module. |
| 5 (weakest) | **`ivi_place` is an invalid observer** (lying about zero). | — | `docs/kernel/39`: `ivi_place --list` exits 0 with "0 layers, 0 surfaces, 0 screens"; `docs/kernel/38` reports the same count across runs; boot62 even saw hmi-controller init fail in a way only consistent with zero screens being real. The observer is corroborated by an independent failure path. |

**Verdict: (1) is the single root cause the evidence supports — a stock client
that invokes `ivi_controller.screen_create` is not running.** (2) is a
downstream symptom (hmi-controller cannot build layers without screens);
(3)–(5) are not independently supported.

## 2. Cheapest discriminating no-boot analysis

Attribution of `screen_create` to a stock component, no VM, no boot.

Searches to run against the already-extracted firmware tree
(`work/vm/kbuild/ws/partimg-build/` and the rootfs it was staged from):

1. **Who references `ivi_controller.screen_create` on the wire.**
   - `rg -a --files-with-matches 'screen_create|ivi_controller.*screen' /usr/bin /usr/libexec /usr/lib /opt` in the extracted rootfs tree.
   - `rg -a --files-with-matches 'ivi_controller_interface|wl_ivi_controller' …` to find every linker of the ivi-controller protocol *client* glue.
   - **Attribution standard**: a binary that (a) contains the symbol/string for `screen_create` or the generated marshalling for the `ivi_controller` request, and (b) is reachable from a launcher. This is the classic "find the client of a server-side protocol method" move.

2. **Who reads the `ivi-shell-user-interface` key.**
   - `rg -a --files-with-matches 'ivi-shell-user-interface' /usr /opt` across every binary, .so, .conf, systemd unit, and init script. `docs/kernel/37` has already shown this returns nothing in the loaded weston modules; expand to launchers and scripts.
   - Any hit **outside** the already-cleared set (`ivi-shell.so`, `ivi-window-manager.so`, `ivi-controller.so`, `weston.real`) is the stock reader.

3. **Who launches `/usr/libexec/weston-ivi-shell-user-interface` (or any sibling).**
   - `ls /usr/libexec | rg -i 'ivi|shell|hmi|home'` — enumerate candidate clients.
   - `rg -a 'weston-ivi-shell-user-interface|/usr/libexec/weston-' /etc /lib/systemd /usr/lib/systemd /opt` — find systemd units, rc-scripts, or wrapper shell scripts that exec it.
   - Dump the libexec client itself: `nm -D` / `strings` for `screen_create`, `ivi_controller`, `wl_display_connect`. If it contains the `screen_create` marshalling, it **is** the stock screen producer and the missing piece is only its launcher.

4. **Cross-check against the hmi-controller trail.**
   - `docs/kernel/38` already shows `controller_module_init` in `hmi-controller.so` reads `[ivi-shell]` keys and calls `create_layer`. Confirm by `rg -a 'ivi-shell-user-interface'` inside `hmi-controller.so`: if it's there, the key is read by hmi-controller **as a launch instruction** for a separate client (not by weston-core). That is a one-line test that reconciles (1) and (2).

**What counts as attribution** (stop as soon as all three are true):
- A named ELF binary (path on rootfs) contains either the string
  `screen_create` or the `ivi_controller` request-wire glue;
- Its startup is caused by a named file we can point to (systemd unit, init
  script, or a module that `fork/exec`s it);
- Nothing else in the rootfs claims the same role.

This is cheaper than any boot: it is `rg` and `nm` against files already on
disk, bounded by the number of libexec binaries and systemd units.

## 3. AppHomeScreen regression (boot65 vs boot58)

In `docs/kernel/37` (boot58) the surface was created via the normal
`ivi_hmi_requester` path:
`request_id("QTAPP")` → `receive_id(1006)` → `surface_create` →
`create_hmi_client(1, 1006, "AppHomeScreen")`. The change that made that
work was the **revert of the `QT_WAYLAND_SET_SURFACE_ID` patch**, not any
config key — writing `ivi-shell-user-interface=` into `weston.ini` did
nothing (the key is dead; `docs/kernel/37`, "Result 2").

In `docs/kernel/39` (boot65) the config was replaced with
`weston_1920.ini.drm` + `backend=drm-backend.so` +
`ivi-module=ivi-window-manager.so,ivi-controller.so` and `HOME_CLIENT=[]`.

A regression this clean, against a known-working revert, is most likely a
boot-timeline / environment regression, not an independent fault:

- the launcher binary was described as "untouched" in boot65, but boot58's
  fix lives in **bytes in `AppLauncher`** that must remain reverted
  (`AppLauncher.vendor.bin`, sha256 `c8d6d56b…a84268` per `docs/kernel/37`);
- the shell-UI launcher path (`/usr/libexec/weston-ivi-shell-user-interface`)
  was written into `weston.ini` in boot58 and boot65, but it is a no-op in
  both — it cannot explain either pass or fail;
- if the launcher is untouched **and** nothing started the ivi-controller
  client (root cause 1), then the `ivi_hmi_requester` protocol path that
  AppHomeScreen rode in boot58 may itself depend on that client being up
  — i.e. the regression is the **same root cause**, surfaced one layer up.

**Exact comparisons to make, no boot:**

1. **sha256 of the launcher binary** actually on the boot65 image vs
   `AppLauncher.vendor.bin` (c8d6d56b…a84268). If they differ, the revert
   was lost between runs; this alone explains the regression.
2. **Diff** `work/vm/kbuild/ws/partimg-build/weston.ini.known-good` (boot65)
   against `work/vm/kbuild/ws/partimg-build/weston.ini.final` (boot58). Any
   line that touches `modules=`, `ivi-module=`, `shell=`, `backend=`, or
   the `[ivi-shell]` keys is a candidate.
3. **Diff the environment** of the launcher between the two runs — whether
   `QT_WAYLAND_SET_SURFACE_ID` is present again, whether `WAYLAND_DISPLAY`
   or `XDG_RUNTIME_DIR` changed, whether the launcher's unit file is the
   same. `docs/kernel/37` names `QT_WAYLAND_SET_SURFACE_ID` as the exact
   knob that suppressed `surface_create` previously.
4. **Timeline**: in `boot58-hmi.log` and `boot65-final.log`, match the
   timestamps of `wl_display_connect`, `ivi_application.surface_create`,
   `request_id("QTAPP")`. If in boot65 the launcher tries and no
   `ivi_hmi_requester` global is advertised, that confirms the
   dependency on the (missing) controller client, i.e. regression = (1).

My read of the files: **not independent.** The simplest hypothesis that
fits every observation is that AppHomeScreen's boot58 success rode on an
ivi-side protocol flow that is absent in boot65's stricter config, and
the controller-client gap is the same gap that leaves screens at zero.
Steps 1–4 above distinguish that from a silent launcher re-patch.

## 4. The `ivi-shell-user-interface` config key

The question is who reads it. `docs/kernel/37` has a direct answer:

> None of the loaded modules (nor the compositor core) reads the
> `ivi-shell-user-interface` config key.

Static grep over `ivi-shell.so`, `ivi-window-manager.so`,
`ivi-controller.so`, and `weston.real` found `ivi-module` but **not**
`ivi-shell-user-interface` or `user-interface`.

Where it **does** appear (`docs/kernel/38`, Step 2 disasm of
`controller_module_init`) is inside **`hmi-controller.so`**, alongside
`ivi-launcher`, `workspace-id`, `layout_surface`, etc. The reference
upstream weston behaviour is that this key is a path that
`hmi-controller` forks/execs as its user-interface client.

But `hmi-controller.so` is **not loaded** on stock (per the vendor
template, `docs/kernel/39`). So the key, in the stock configuration,
has no reader at all. Writing it into `weston.ini` on this image is a
no-op — exactly what boot58's `pgrep` confirmed.

**Implication**: do not infer that a component "should" launch the UI
from a key that no loaded component reads. On stock this platform, the
UI client is almost certainly started by **something outside weston**
(systemd unit, init script, or another binary in `/usr/libexec`), and
that launcher is what §2 must find. The `ivi-shell-user-interface` key
is a red herring until and unless hmi-controller is in the module list —
which the vendor template says it isn't.

## 5. Another run now? — No

Static attribution first. Justification, strictly from the read files:

- `docs/vm/56-endgame-runbook.md` pre-commits a rule: *the run that closes
  this must state, before it starts, which gate it is testing and what
  a null looks like. Three false negatives in one hour came from runs
  whose null was not defined in advance.* Boot65 is already a
  pre-committed null ("layers still zero") on a known-good config;
  another run without a new variable will produce the same null.
- The current root-cause ranking says the author of `screen_create` is a
  named-but-unknown binary. A boot without that name adds no bit: with
  or without the config key, with or without `hmi-controller.so`, the
  controller-client is still unidentified, and the hmi-controller path
  is downstream of screens anyway (`docs/kernel/38`).
- The cheapest next bit is `rg`/`nm` over the rootfs, not a boot.

**Stop condition on static work (do not boot until all three):**

1. A named ELF (path on the extracted rootfs) has been shown to contain
   either the string `screen_create` or the generated `ivi_controller`
   request-side marshalling.
2. A named launcher file (systemd unit, init script, or a parent
   process) has been shown to exec that ELF.
3. The sha256 of the on-image launcher binary matches
   `AppLauncher.vendor.bin` (c8d6d56b…a84268), confirming boot58's
   revert is still present, and `weston.ini` has been diffed boot58 vs
   boot65 with every delta annotated.

If any of 1–3 cannot be produced from the extracted firmware alone, the
problem is a missing artifact (not a missing boot), and the right next
step is re-extraction — still not a run.

**If and only if** 1–3 are satisfied, the next run has a defined gate
(does loading the attributed client produce ≥1 screen and ≥1 layer on
`ivi_place --list`) and a defined null (same binary, still zero
screens → the client is not the cause and the screen author is
elsewhere, e.g. inside the drm backend's output lifecycle).

---

## Final summary

- **Most likely root cause:** no stock IVI-controller client is running, so
  `ivi_controller.screen_create` is never called; no loaded module creates
  screens automatically from the drm output
  (`docs/kernel/39`, `docs/kernel/37`, `docs/kernel/38`).
- **One no-boot test:** `rg -a 'screen_create|ivi_controller' /usr/bin
  /usr/libexec /usr/lib /opt` in the extracted rootfs, cross-checked with
  `rg -a 'ivi-shell-user-interface' /etc /lib/systemd /usr/lib/systemd`
  and `nm -D /usr/libexec/weston-ivi-shell-user-interface`. Attribution
  = one ELF contains the client-side glue **and** a named file exec()s it.
- **Run/no-run verdict:** **no run.** Static attribution first; the
  stop-condition above is the gate to the next boot.
