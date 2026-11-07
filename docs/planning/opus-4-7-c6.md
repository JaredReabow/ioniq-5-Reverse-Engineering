# opus‑4‑7‑c6 — post‑run consultation on vendor‑template boots (boot63, boot64)

Date: 2026‑11‑06. Read‑only consult. No experiments, no git.

## What the two logs actually say

- `boot63-layers.log` (host wrapper record at tail: `timeout: true, elapsed_seconds: 300.18, serial_completion_seen: false, userspace: false`).
  - systemd was blocked on `A start job is running for partitio...ck service` for `3min 17s … 3min 40s`.
  - The service does finish — line `[  230.468172] systemd[1]: Started partition mount check service.` followed by `Startup finished in 7.384s (kernel) + 3min 43.084s (userspace) = 3min 50.469s.`.
  - That is **~230 s VM‑clock**, which the host wrapper interprets as **>300 s wall** (QEMU slip). Weston was never reached because the host wrapper cut the run before the compositor target ran.
  - The tail‑probe line `[lay] SOCKET after 240s = []` / `IVI_EARLY=[]` confirms the wait‑probe fired before weston started. No weston output in the log at all.

- `boot64-diag.log` (reaches weston):
  - `[03:03:18.432] weston 1.10.0`
  - `[03:03:18.488] Using config file '/etc/xdg/weston/weston.ini'` — **not** the retained `weston.ini.vendor`.
  - `[03:03:18.502] Loading module '/usr/lib/weston/ias-backend.so'`
  - `[03:03:19.128] Failed to load module: /usr/lib/weston/ias-backend.so: undefined symbol: drmModeRGBA`
  - `[03:03:19.128] fatal: failed to create compositor backend`
  - Weston crash‑monitor restarts observed (3× bursts), i.e. weston is in a short restart loop against the same config.

## Reading of the retained `weston.ini.vendor`

The retained file is well‑formed for an ivi‑shell load path and is consistent with the doc‑38 findings:

- `[core] shell=ivi-shell.so` and `modules=/weston-vm-input.so` — core input module only, correct.
- `[ivi-shell] ivi-module=ivi-window-manager.so,ivi-controller.so` — vendor ivi modules only; `hmi-controller.so` deliberately omitted. Correct per doc‑38 (controller_module_init failed in prior runs; there is no vendor‑template evidence to re‑include it).
- Four layer IDs (`1000/2000/3000/4000`) plus the panel/background/tile/sidebyside/fullscreen/random/home ids, `ivi-shell-user-interface=/usr/libexec/weston-ivi-shell-user-interface`, `[output] name=Virtual-1 mode=1920x720`. All consistent with the UI binary and virt‑GPU output.
- **What the retained file does not specify**: `[core] backend=`. That is the crux of boot64.

The retained config is **structurally correct**, but by itself it does not prevent `ias-backend.so` from being chosen: in boot64 Weston loaded `/etc/xdg/weston/weston.ini` — i.e. the target image's shipped config, not our file — and that shipped file selects `ias-backend.so` (either by `backend=` or by weston.service CLI arg). Our retained bytes never participated in boot64.

## Facts that must be verified in the clone/image before QEMU is fired again

These are the only pre‑boot checks that matter; everything else is premature.

1. **Which weston.ini does weston actually open?** boot64 printed `/etc/xdg/weston/weston.ini`. Cat that file from the mounted clone/image. Also read `weston.service` (and any `weston@.service` / drop‑ins under `/etc/systemd/system/*.service.d/`) to see whether it passes `--config=<path>` or `--backend=<name>`. If weston.service hard‑codes `--backend=ias-backend.so`, no `weston.ini` edit will change the backend — a different override surface is required and the "retained config" plan is incomplete.
2. **Where is the vendor's own IVI config?** If the image ships `/etc/xdg/weston/weston.ini` with ivi keys preserved, compare its bytes to `weston.ini.vendor`. Divergence other than the `[core] backend=` line must be reported before any write, because doc‑38 explicitly says *keep vendor bytes* (the `AppHomeScreen` surface only appeared after the surface‑id patch was reverted).
3. **Does the vendor's own template choose `ias-backend.so`?** Grep the clone for `ias-backend` to confirm it is the vendor's intended backend on real hardware. If yes, the regression under QEMU is not a config bug — it is `libdrm` symbol absence (`drmModeRGBA`) under virt. This then becomes a libdrm/sysroot question, not a weston.ini question. Do not paper over it by forcing `drm-backend.so` unless the vendor template itself supports that choice.
4. **What does `partition mount check service` wait on?** Read the unit file (`systemctl cat partition-mount-check.service` from the image's `/lib/systemd/system/` or `/etc/systemd/system/`) and its `ExecStart`. Boot63 shows ~3 min 40 s on it, but it *did* complete. Verify (a) the script's expected deps (which `/dev/mmcblk0pN` it polls, and whether the image's partition table under QEMU satisfies them), and (b) whether weston's target has `After=` / `Requires=` on this unit. If weston is unblocked only after this unit completes, the host wrapper's 300 s cap is the limiter, not the config.
5. **Serial completion marker.** The wrapper tail shows `serial_completion_marker: null, serial_completion_seen: false`. Confirm the init script actually emits a marker weston can land before and the wrapper watches for the marker rather than a wall‑clock 300 s. Without a marker the next boot will time out the same way even if weston loads cleanly.

Do not touch any of these — only verify.

## Judgment on the retained config

- **Correct in content**, insufficient in placement. The ivi key set is right; the backend question is unanswered.
- **Risk if written to `/etc/xdg/weston/weston.ini`** without first reading the vendor's own file: you overwrite vendor bytes we were told to preserve. The AppHomeScreen regression in doc‑38 came from exactly that kind of substitution.

## Single next action

Mount (or loop‑open) the authentic clone/image **read‑only** and extract, to `work/vm/kbuild/ws/vendor-captures/`:

- `/etc/xdg/weston/weston.ini` (verbatim)
- `/lib/systemd/system/weston.service`, `/lib/systemd/system/weston@.service`, every drop‑in under `/etc/systemd/system/weston*.service.d/`
- `/lib/systemd/system/partition-mount-check.service` (or whatever unit name the systemd log abbreviates) and the ExecStart script it points at
- Any `ivi-shell-user-interface` config the vendor UI binary reads (strings on the UI binary already identified the keys in doc‑38 — now capture the actual files from the image)

Then diff the shipped `weston.ini` against `weston.ini.vendor`. That diff decides the next write. No QEMU boot until the diff is produced.

## Pre‑boot verification gate (must pass before boot65)

All four must be true, from the captured files above:

1. The config path weston opens is identified and agreed. If weston.service passes `--config=`, our file must be placed at that exact path; otherwise at `/etc/xdg/weston/weston.ini`.
2. The vendor's shipped `weston.ini` has been read. Either (a) it already contains the ivi keys we have, in which case we do **not** overwrite — we only append or adjust the single `backend=` line via a drop‑in / override that is justified by vendor evidence; or (b) it is the generic sample with `backend=ias-backend.so` and no ivi keys, in which case the retained `weston.ini.vendor` legitimately replaces it. Decide in writing which case applies.
3. The ias‑backend vs. QEMU story is resolved: either (i) the vendor template itself has a drm‑backend fallback path we can use without inventing bytes, or (ii) we accept that boot64's `drmModeRGBA` failure is a sysroot/libdrm issue and open that as a separate work item rather than masking it in `weston.ini`.
4. `partition-mount-check.service`'s expected runtime under QEMU is bounded (unit log from the clone, or the script's own polling budget). The host wrapper's wall‑clock cap must be greater than that bound **and** the wrapper must key completion off a serial marker, not wall time.

## Bounded next run (boot65)

Only after the gate passes:

- One boot, same kernel/initrd/image, same cmdline, with:
  - whichever single file change the diff in step 2 justifies (no multi‑file edits),
  - host wrapper wall cap raised to at least `max(partition-mount-check observed completion from vendor clone, 300 s) + 120 s` safety,
  - wrapper success keyed to a serial marker emitted by the init script after weston's `[ivi-shell]` log line (or weston's own `compositor initialized` line), not wall time.
- Capture full weston stderr+stdout to `boot65-weston.log`, full dmesg to `boot65-dmesg.log`.

## Evidence / completion gates for boot65

PASS (stop, report, do nothing else):

- Weston prints `Using config file '<expected path>'` matching our placement, **and**
- Loads `ivi-shell.so` + `ivi-window-manager.so` + `ivi-controller.so` without `undefined symbol` or `Failed to initialize`, **and**
- Compositor backend is created (no `fatal: failed to create compositor backend`), **and**
- The ivi layer/surface probe (`[lay] …`) reports at least one screen bound to `Virtual-1`.

STOP‑AND‑CONSULT (do not iterate):

- Weston still opens `/etc/xdg/weston/weston.ini` instead of our placement → step 1 of the gate was wrong; re‑read weston.service.
- `ias-backend.so` still selected → weston.service `--backend=` is overriding the ini; config change is not the right surface.
- `drmModeRGBA` still undefined with a different backend selected → libdrm sysroot issue, not a weston config issue; open as separate item.
- `partition mount check` service runs past the wrapper's new cap → unit‑level investigation on the clone before another boot.
- `ivi_place` still reports `0 layers / 0 surfaces / 0 screens` with a healthy backend and vendor ivi modules loaded → this is the doc‑38 wall; **do not** add `hmi-controller.so`, do not invent surface IDs, do not re‑apply the reverted surface‑id patch. Return to vendor‑template static analysis to find the `create_screen` / drm output binding that the vendor init path performs before UI handoff.

## Explicitly rejected moves

- Re‑including `hmi-controller.so` in `ivi-module=`. Doc‑38 is unambiguous; no vendor‑template evidence supports it yet.
- Re‑applying the surface‑id patch. AppHomeScreen only appeared after reverting it.
- Forcing `backend=drm-backend.so` purely to dodge `drmModeRGBA` without vendor evidence.
- Overwriting the clone's `/etc/xdg/weston/weston.ini` before capturing and diffing it.
- Relying on wall‑clock completion. Boot63's 300 s wall cut off a userspace that was actually still progressing.

## One‑line summary

Do not boot again until the clone's `weston.service`, `/etc/xdg/weston/weston.ini`, and `partition-mount-check.service` are captured verbatim and diffed against the retained `weston.ini.vendor`; the next boot changes exactly one file justified by that diff, extends the host wall cap past the observed `partition-mount-check` runtime, and succeeds only if weston creates a compositor backend and the ivi probe sees ≥1 screen on `Virtual-1`.
