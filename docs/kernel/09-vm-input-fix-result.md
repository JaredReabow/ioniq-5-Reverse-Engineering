# The seat fix closes the display thread: socket appears, the app connects and draws, `invalid object` is gone

Date: 2026-11-06. Doc 08 identified the cause: `weston-vm-input.so` returned −1 on an empty seat list,
tearing weston down before it served. The module was rebuilt to defer instead of fail
(`VM_INPUT_NO_SEAT_DEFERRED`, `bind_first_seat()`, `VM_INPUT_SEAT_BOUND`). This is the boot result.

## Exact payload booted

- **Kernel**: `work/vm/kbuild/bzImage`, sha256 `893e1a6b…a6392` (`4.1.27-abl`, gzip, bochs-drm, micom
  stand-in, `CONFIG_UNIX=y`).
- **Replacement input module**: `/weston-vm-input.so`, **13,008 bytes**, sha256
  `514da5dedb0f7f94bdb018de884920f8abcda473860dc671614838fc6bcbd58c`, markers
  `VM_INPUT_READY`, `VM_INPUT_SEAT_BOUND`, `VM_INPUT_NO_SEAT_DEFERRED` all present (built by the
  project, injected at the path `weston_1920.ini` already names).
- **Config**: `backend=drm-backend.so`, `modules=/weston-vm-input.so`,
  `ivi-shell-user-interface=/usr/libexec/weston-ivi-shell-user-interface`, `[output] name=Virtual-1`.
- **Boot**: `run-kbuild.py --init /init-authentic-hmi.sh --smp 4 --timeout 360`, vendor rootfs
  (`ws/rootfs.img`, `snapshot=on`), `-device VGA` (bochs-drm).

## The check, in the required order

1. **Socket** — appeared **before** any application check:
   `[apps-check] WAYLAND_SOCKET_UP after 2s`. (The first time a wayland socket has appeared on a
   real-output backend in this whole line of work.)
2. **Apps** — `[apps-check] APPLAUNCHER_PID=[1953] at +45s after socket`, then
   `[apps-check] APPHOME_PID=[2205] at +30s after AppLauncher`, and
   `PIDS_FINAL AppLauncher=[1953] AppHomeScreen=[2420] ApplicationManager=[1995]`.
3. **Connected and drawing** — the app log shows a live Wayland-EGL client reaching its main UI, not
   dying at connect: `Using Wayland-EGL`, `SCREEN_STATE: START DRAW`, `constructMenuModel`,
   `prepareAdvancedDisplayList … numItemsPerPage: 12`, `injectWidgetItemToAdvancedPage …
   itemWidgetPlaceHolder FOUND!!!`; D-Bus name owned (`com.lge.hkmc.avn.appfunc.AppHomeScreen`); and
   three PNG captures (`BYHAND_CAPTURE1/2/3`, magic `89504e470d0a1a0a`, 87,8xx bytes — a new size, not
   the 129,844-byte early background or the 120,5xx-byte standby face).
4. **`invalid object`** — **0 occurrences** (`grep -aciE 'invalid object|wl_display@1: error'` = 0).
   No `wl_display@1: error 0: invalid object N`, no protocol-error text, and no server-side client
   error in the weston log.

## Verdict

Per the decision table this is the **first** outcome: **socket + app running + no `invalid object`** —
the Wayland fault was the empty seat all along, and the display thread is closed. The DRM device,
`drm-backend.so`, and the vendor app stack all work once the projection input module stops failing on an
empty seat list.

## Honest caveats (recorded, not glossed)

- The monitor's **manual relaunch** instance (PID 2278, from its own `cd /app/bin; while read …`
  launch at line 86) crashed ~26 s later with `Trace/breakpoint trap (core dumped)`; a fresh instance
  (PID 2420) was running at the end. That SIGTRAP produced **no** `invalid object` text, so it is a
  *different* crash than the one this thread chased — plausibly a pre-existing app fault (its log also
  shows SQLite `commit Fail` / `DELETE FAIL … no such table`) or a manual-relaunch-environment artefact.
  It is **not** evidence of the Wayland error.
- The socket appeared 2 s after weston start, before any app was launched, so the "no error from a
  client that never connected" trap is not in play here.

## Files

- `docs/kernel/08-weston-vm-input-empty-seat.md` — the cause.
- `docs/kernel/09-vm-input-fix-result.md` — this result.
- `work/vm/kbuild/boot26-fixedvmi.log` — the boot log (size + identity: the socket/app markers above).
