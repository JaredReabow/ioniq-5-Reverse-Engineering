# Astra C6 — separate startup failure from the vendor-layout test

Read-only post-run consultation. This document is the only write; no experiments, guest actions, or git operations were performed.

## Decision

**Make the next action one bounded startup/layout diagnostic using the retained `weston.ini.vendor`, with vendor AppLauncher bytes preserved.** Do not rerun the long warm-launch script, add `hmi-controller`, repair IAS, or change surface IDs in this run. First establish that this exact projection reaches a functioning compositor and that its layout can be measured. Neither boot63 nor boot64 tested that question successfully.

## Evidence and assessment

Sources actually read:

- **[K38]** `docs/kernel/38-hmi-controller-is-ivi-module-init-fails-no-screens.md`, Steps 1–2.
- **[B63]** `work/vm/kbuild/boot63-layers.log`, partition-check startup at lines 471–472, repeated `mmcblk0p16` mounts and pending partition job in the late log, final JSON at lines 1250–1264.
- **[B64]** `work/vm/kbuild/boot64-diag.log`, `[diag] WESTON LOG BEGIN` through `DIAG_DONE`, and final JSON. The fatal is timestamped `03:03:19.128`.
- **[V]** `work/vm/kbuild/ws/partimg-build/weston.ini.vendor`, complete file.
- **[K37]** `docs/kernel/37-revert-restored-surface-config-key-dead.md`, Results 1–3 and artifact identity.
- **[S]** Staged `diag-weston.sh`, `lay-run.sh`, and `weston-wrap-drm.sh` in `work/vm/kbuild/ws/partimg-build/`.
- **[C]** Staged `weston_1920.ini.host`, `weston_1920.ini.drm`, and `weston_1920.ini.fixed` in that directory.
- **[C5]** `docs/planning/astra-c5.md`, prior observer audit; its deployed-binary caveat remains material.

### Is the retained configuration faithful?

**Yes as a minimal VM projection of the supplied vendor-template contract; not as a byte-identical vendor configuration or a demonstrated working layout.** [V] retains:

- `shell=ivi-shell.so` and only `/weston-vm-input.so` in core `modules=`;
- vendor `ivi-module=ivi-window-manager.so,ivi-controller.so`;
- layer IDs 1000/2000/3000/4000, shell surface IDs 1001–1007 and workspace-background ID 2001;
- `ivi-shell-user-interface=/usr/libexec/weston-ivi-shell-user-interface`;
- `Virtual-1`, 1920x720, and workspace background color `0x99000000`.

The VM input helper, virtual output, corrected UI path and removal of the IAS backend selection are explicit projection accommodations, not vendor behavior established on hardware. [C] corroborates the layer/module/key structure, but those files are already adapted variants; this consultation did not identify and compare an independently pristine shipped template. Accordingly, fidelity is qualified by the supplied vendor-template facts.

Relative to the longer staged variants, [V] also omits `idle-time=0`, cursor settings, transition duration and image-path keys. That is reasonable for a bounded backend/layout diagnostic, **not proof of equivalent appearance or idle behavior**. The omitted assets/defaults would matter to any later claim of a faithful visible home UI. Do not silently restore or vary them in this run.

Removing `backend=ias-backend.so` avoids explicitly selecting the exact loader failure in [B64]. It does **not** prove which backend will be selected next. Check the actual wrapper, arguments and default-selection path before boot; record the loaded backend at runtime. The staged DRM wrapper itself adds `--use-pixman` but no backend override, and its comment points to `weston_1920.ini`, whereas [B64] explicitly reports reading `/etc/xdg/weston/weston.ini`. A filename or wrapper comment is not sufficient provenance. [S, B64]

Do not enable `hmi-controller`. [K38] establishes why it cannot be a core module and reports failure when added as an IVI module; it does not establish that the vendor template requires it. Its no-screens explanation is a consistency argument, not a demonstrated cause, particularly given the earlier inventory-observer caveat [C5]. Likewise, retaining the UI-path key does not guarantee a UI process: [K37] reports that the loaded vendor components did not consume that key.

Keep vendor AppLauncher bytes. [K37] records the restored `receive_id(1006)` → `surface_create(1006, ...)` → `create_hmi_client(..., "AppHomeScreen")` chain after the revert. Its vendor artifact SHA-256 is `c8d6d56bc254ad0731e81f40bd83aa9b3be6b49bcbd8efb291157a06c4a84268`. Do not reinterpret the configuration's `random-id=1006` as permission for another application-ID patch: the historical surface mapping is evidence to follow, not a fixed ownership rule for every subsequent run.

### Does boot63 implicate this configuration in the partition wait?

**No direct causal evidence does.** Boot63 did not reach Weston (supplied run fact); its completion record says `root_mounted=true`, `timeout=true`, `elapsed_seconds=300.18`, `command_exit_code=null`, `serial_completion_marker=null`, and `serial_completion_seen=false`. `qemu_returncode=0` does not turn that into a completed layer test. “Weston Process Crash Monitoring” starting is not compositor startup. [B63]

The pending partition-mount-check job says **“no limit”**; 300 seconds is the outer run budget, not evidence of a 300-second Weston or systemd configuration timeout. Repeated `mmcblk0p16` mounts are a storage/startup-loop clue, not proof of corruption or a particular bad partition. Clone provenance, mount mappings, persistent state, concurrent writers and checker predicates are plausible investigation targets, not diagnosed causes. [B63]

Crucially, boot64 also shows the pending partition job and repeated mounts, yet its diagnostic captured an actual Weston startup and the IAS undefined-symbol fatal. Thus the partition job is not demonstrated to be an unconditional prerequisite for Weston in this setup. The two failures can coexist; do not claim the partition wait itself explains every missing compositor. [B64]

An **indirect** relationship remains possible if config installation touched the wrong image/partition, copying occurred during use, or a startup/check script actually consumes this file or waits on graphics. None is shown here. Distinguish deployment side effects from the semantics of Weston INI keys. Establishing a direct dependency requires the actual unit/script and ordering evidence; the logs alone do not supply it.

Boot64's `DIAG_DONE` proves that diagnostic body reached its final print, not that the harness accepted completion: its JSON still has no configured completion marker, `serial_completion_seen=false`, `timeout=true`, and `elapsed_seconds=120.13`. [B64, S]

## Before boot: mandatory verification gates

These are proposed checks, not checks performed in this consultation.

1. **Exact image and installation:** identify the parent and disposable clone, verify no concurrent writer or live-guest copy, and check partition/mount mappings and available space. Read back `/etc/xdg/weston/weston.ini` from the actual clone and compare its bytes/hash to [V]. Check aliases, symlinks and boot-time replacements. Do not assume changing the staged file changed the guest.
2. **Effective launch:** inspect the actual guest wrapper/unit/argv and environment. Confirm no IAS override, no extra `hmi-controller`, and a known VM-capable backend selection path with compatible renderer arguments. If deletion merely falls back to IAS or backend choice is unresolved, stop before boot rather than introduce another hidden variable. Verify referenced modules and UI executable exist.
3. **Vendor bytes:** verify the guest AppLauncher against [K37]'s retained vendor artifact/hash and confirm the reverted surface-ID forcing has not returned through an environment shim. Preserve all other vendor binaries and known-working launch/label settings.
4. **Observer and completion:** use one startup diagnostic reachable without waiting for the global systemd job queue to clear. Give every probe a timeout, retain raw output and exit status, and configure a unique serial completion token that the harness actually recognizes. [S]'s `lay-run.sh` has serial waits of 240 + 300 + 300 + 150 + 60 seconds, before capture; it is not a 300-second bounded test. Do not reuse it unchanged.
5. **Inventory validity:** establish the deployed inventory tool's provenance and post-bind synchronization, or arrange independent compositor/protocol evidence. [C5] reports a source-level early-roundtrip defect, not proof of the current executable's behavior. Without validated observation, an all-zero listing cannot be a decisive no-screens result.

## One bounded run and its gates

**Scope:** startup and layout only, no warm relaunch, power-state manipulation, forced placement, or ID changes. Keep the image/launch baseline fixed except for installing the retained configuration and bounded diagnostics.

- **Budget:** hard host deadline of 180 seconds from VM launch; readiness deadline at 90 seconds, evidence collection complete by 150 seconds, remaining time for export and shutdown. These are diagnostic bounds, not claims about required vendor boot speed. No automatic retry or extension.
- **Startup gate:** capture the effective config hash, actual Weston argv, PID/start time, complete fresh Weston log, selected backend, renderer and `Virtual-1` mode. Require a live compositor and a successful Wayland connection, not just a socket inode. A backend fatal ends the layout test immediately.
- **Failure branch:** if readiness fails by 90 seconds, collect bounded process/unit state, pending jobs, mount state and the partition-check unit's status/journal plus the Weston log. Record `STARTUP_BLOCKED` or `BACKEND_FAILED`; do not proceed to app conclusions.
- **Layout gate:** after readiness, collect two synchronized inventories approximately ten seconds apart, including screen/output association, layer IDs and surfaces, with raw errors and statuses. Corroborate using same-run compositor/protocol events or a known live surface on the same socket. Record whether the four configured layer IDs actually exist; keys alone do not instantiate them.
- **Home evidence, if present naturally:** preserve the same-run AppHomeScreen PID/start-time/client association, assigned surface ID, and any buffer/layer/output evidence. Do not assign ownership from a cumulative log or numeric ID alone. A screenshot is supplementary; a background-only frame is not a no-surface result. This startup test does not by itself certify the full home UI.
- **Completion gate:** export evidence, emit the configured terminal token with outcome (`READY_LAYOUT`, `READY_LAYOUT_NULL`, `BACKEND_FAILED`, `STARTUP_BLOCKED`, or `OBSERVER_INVALID`), and require the harness record to show the token seen and command exit status, without timeout. Stop immediately after evidence completion, on a fatal, on invalid observation, or at the hard deadline. Deadline termination remains an incomplete run even if QEMU exits zero.

## What null means

- **No startup/completion gate:** infrastructure or acquisition null; the vendor-layout hypothesis was not tested. Boot63 belongs here.
- **Backend fatal:** backend/load compatibility failure; no conclusion about layer IDs, Home or a missing HMI controller. Boot64 belongs here.
- **Live backend/output, but invalid inventory:** observer null; do not repeat “0 screens” as an established layout fact.
- **Validated zero screens/layers after startup:** this minimal vendor-template projection is insufficient to expose/create the expected IVI layout in this VM during the measured interval. It does not establish that the vendor template is wrong, identify the partition-wait cause, or justify adding `hmi-controller`.
- **Expected layout exists, Home absent/unplaced:** startup/layout boundary passed; Home creation/association/presentation remains unresolved at the precise boundary actually measured. Do not undo the vendor-byte revert.

**Stop after this one run.** A further run needs a newly localized failure and a discriminating observation, not a longer timeout or another speculative configuration/module change.
