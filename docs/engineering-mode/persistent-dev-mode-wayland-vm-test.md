# Developer-state initializer: authentic-Wayland VM follow-up

## Why this is a different test

The completed offscreen test in `persistent-dev-mode-vm-test.md` showed that both the unmodified control and the modified copy fault before `setEngType()`. The extracted stock launcher explicitly sets `QT_QPA_PLATFORM=wayland` and `XDG_RUNTIME_DIR=/var/run/user/root`; the research projection's authentic launch records set Wayland display `wayland-0`. Offscreen is therefore a diagnostic environment, not the production application path.

## Precommitted run

Create a fresh CoW clone of `work/vm/kbuild/ws-run68`. Install the separately modified `AppEngineerMode-dev-probe` whose source hash, exact one-byte difference and modified hash are retained in the prior test record. Preserve the unmodified control at `/app/bin/AppEngineerMode`. Start `dev-mode-wayland-probe.sh` before authentic esinit. The probe waits up to 180 guest seconds for `/run/user/root/wayland-0`, then runs control, modified and modified-restart applications using the stock-relevant environment, each for 60 guest seconds.

Retain the dedicated ttyS3 trace, host serial/result records, changed-byte manifest and launcher identity. No input or menu action; no update, encryption marker, AppUpgrade, AppDMClient, ABL, vehicle, MICOM or physical-unit operation. The VM's real radio and input remain absent, and application rendering is independently unresolved. If a process crashes, record the control comparison. If it lives, report only process/initializer log evidence, not visible menus or persistence. Host stop limit is 420 seconds; the exact completion marker is `DEV_MODE_WAYLAND_PROBE_COMPLETE`.

## Stop rule

One run only. If the socket never appears or control and modified application still fail before the initializer, stop. Do not create a platform shim or false callback to force progress. Hardware deployment remains unjustified until stock-path initialization and menu selection are demonstrated.

## Result — initializer condition established; visible presentation remains unresolved

Run `1794578477560093000` completed in 195.82 host seconds: dedicated trace received the exact terminal marker and `timeout=false`. The harness's unrelated `userspace` boolean remained false because its ordinary shell readiness marker was not emitted; do not confuse that with absent vendor userspace—the probe, esinit, Weston socket and applications demonstrably ran.

| Launch | Outcome | What is established |
| --- | --- | --- |
| unmodified control | SIGSEGV / 139 before `setEngType` | Does not control the patched initializer because it failed earlier at EGL/platform setup |
| modified | exit 1 after EGL/Wayland failure | Reached `[setEngType] No Develop Version`, then **`initConnmanIface()`** immediately after it |
| modified restart | SIGSEGV / 139 after a Wayland protocol error | Again reached `[setEngType] No Develop Version`, then **`initConnmanIface()`** |

The `No Develop Version` text by itself is not evidence of production state: static analysis shows it is logged before the instruction. The immediately following `initConnmanIface()` log is the critical runtime evidence that `setEngType()` returned. Its only store to `this+0x13c` is the verified instruction whose immediate is `00` in the modified binary. Therefore, on **both modified launches**, the initializer set the per-instance field to **0**. `checkSOPVersion()` returns `(field == 1)`, so it returns false; the shipped QML condition selects the non-SOP/developer menu models. This establishes the initialization and application-restart condition from retained byte identity plus execution order. It does **not** establish visible menus, input operation, all developer features, or hardware behaviour.

The follow-on failures are consistent with the independently measured graphics blocker: all application logs contain `DRI2: failed to open swrast` and `failed to initialize EGL display`; a later modified launch reports `wl_display@1: error 0: invalid object 18`. No platform shim, false callback or EGL substitute was introduced. Direct launch also has D-Bus registration errors, so this is not a complete stock-launch-chain test.

Retain the trace, result, launch command, patch manifest and hashes under `evidence/dev-mode-wayland-vm-2026-11-13/`. The source and modified executable remain private VM artifacts. The result meets neither the visual-menu nor physical-unit acceptance condition.

## Production interpretation

A boot script should **not write a fixed RAM address**: `this+0x13c` is object-relative and changes per process. The persistent mechanism, if ever authorized for a matching production build, is a **verified modified application copy** staged into the volatile override location before the normal launch of app id 301. `/tmp` is tmpfs, so it must be rebuilt or copied from a persistent owner-controlled location on every boot before `AppLauncher` evaluates its `/tmp/app/bin/AppEngineerMode` preference. The boot copy must verify the source application's exact hash and expected byte at `0x73726e`, write a new file then atomically rename it, set restrictive root ownership/mode, and fail closed on a version mismatch. The established launcher preference is necessary for that mechanism; the QEMU direct-launch result does not re-test it.

This is a design conclusion, **not a live-unit procedure or authorization**. It is only applicable to the exact validated build or a separately revalidated successor. Official updates can replace the binary; startup ordering, integrity checks, true menu visibility and rollback remain untested. It enables the engineering application's non-SOP menu selection only; it does not create a global system developer mode or disable ABL/update signature enforcement.
