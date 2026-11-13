# Developer-state initializer: authentic-Wayland VM follow-up

## Why this is a different test

The completed offscreen test in `persistent-dev-mode-vm-test.md` showed that both the unmodified control and the modified copy fault before `setEngType()`. The extracted stock launcher explicitly sets `QT_QPA_PLATFORM=wayland` and `XDG_RUNTIME_DIR=/var/run/user/root`; the research projection's authentic launch records set Wayland display `wayland-0`. Offscreen is therefore a diagnostic environment, not the production application path.

## Precommitted run

Create a fresh CoW clone of `work/vm/kbuild/ws-run68`. Install the separately modified `AppEngineerMode-dev-probe` whose source hash, exact one-byte difference and modified hash are retained in the prior test record. Preserve the unmodified control at `/app/bin/AppEngineerMode`. Start `dev-mode-wayland-probe.sh` before authentic esinit. The probe waits up to 180 guest seconds for `/run/user/root/wayland-0`, then runs control, modified and modified-restart applications using the stock-relevant environment, each for 60 guest seconds.

Retain the dedicated ttyS3 trace, host serial/result records, changed-byte manifest and launcher identity. No input or menu action; no update, encryption marker, AppUpgrade, AppDMClient, ABL, vehicle, MICOM or physical-unit operation. The VM's real radio and input remain absent, and application rendering is independently unresolved. If a process crashes, record the control comparison. If it lives, report only process/initializer log evidence, not visible menus or persistence. Host stop limit is 420 seconds; the exact completion marker is `DEV_MODE_WAYLAND_PROBE_COMPLETE`.

## Stop rule

One run only. If the socket never appears or control and modified application still fail before the initializer, stop. Do not create a platform shim or false callback to force progress. Hardware deployment remains unjustified until stock-path initialization and menu selection are demonstrated.

## Result

Pending.
