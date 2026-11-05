# fbdev-backend result: also no wayland socket — the stall is NOT vblank/page-flip

Date: 2026-11-06. `drm-backend.so` (doc 05) initialised the DRM device but weston never served a client,
with the leading hypothesis that drm-backend stalls on a vblank/page-flip that bochs-drm under TCG never
delivers. This is the control the hypothesis demanded: `fbdev-backend.so` has **no vblank wait, no
page-flip, no atomic commit** — it maps `/dev/fb0` and repaints on a timer — so the hypothesised stall
mechanism cannot occur on it. If fbdev also fails, the stall is not about vblank.

**Result: fbdev also fails. The stall is not about vblank.**

## Setup

Same kernel, same image, one change: `/etc/xdg/weston/weston_1920.ini` `backend=drm-backend.so` →
`backend=fbdev-backend.so`, and the `/usr/bin/weston` wrapper changed to
`weston.real --backend=fbdev-backend.so --tty=1` (kept the pixman solid-fill shim; fbdev uses the pixman
renderer). The bochs-drm driver provides `/dev/fb0` (`bochs-drm 0000:00:01.0: fb0: bochsdrmfb frame buffer
device`, `crw------- 1 0 root 29, 0 /dev/fb0`), confirmed before the test.

## What weston did (full log, verbatim, manual run with the ivi-shell config)

```
[17:01:50.117] Loading module '/usr/lib/weston/fbdev-backend.so'
[17:01:50.401] initializing fbdev backend
[17:01:50.408] Creating fbdev output.
[17:01:50.411] Mapping fbdev frame buffer.
[17:01:50.428] fbdev output 1024×768 px
[17:01:50.466] Compositor capabilities: …
[17:01:50.472] Loading module '/usr/lib/weston/ivi-shell.so'
[17:01:50.514] Loading module '/usr/lib/weston/ivi-window-manager.so'
[17:01:50.712] Loading module '/usr/lib/weston/ivi-controller.so'
[17:01:50.815] ivi-controller: No ivi-input-module set
[17:01:50.819] Loading module '/weston-vm-input.so'
VM_INPUT_NO_SEAT
[17:01:50.824] Destroying fbdev output.
[17:01:50.825] Disabling fbdev output.
[17:01:50.825] Destroying fbdev frame buffer.
```

So fbdev got **further** than drm: it created the output, mapped the framebuffer, and reported a real
1024×768 output. Then it loaded every ivi module, printed `VM_INPUT_NO_SEAT` (from the projection input
module `tools/uk_fw/guest/weston_vm_input.c`, which found no seat), and immediately destroyed the output.

## The decisive measurements

- **No wayland socket.** `find /run /tmp /var/run -name 'wayland-*'` → empty, at 8 s and 16 s.
- **No listening socket fd.** `/proc/<weston>/fd` shows `0→/dev/null, 1→/tmp/fbdev.log, 2→/tmp/fbdev.log,
  13→timerfd, 23→timerfd, 24→dltpipe` — **no unix socket.**
- **No epoll fd — the strongest single observation.** The absence of an `anon_inode:[eventpoll]` fd in
  `/proc/<weston>/fd` proves the compositor **never entered its serving loop** (`wl_display_run`/
  `epoll_wait`). That is a stronger statement than "no socket found": weston is not a server that
  refused clients, it is a process stuck before the point where a server can exist.
- **The process then exits** (alive at +8 s, gone by +16 s) — a teardown, not a live-but-stalled server.
- In the authentic esinit path, weston crash-restarts repeatedly (crash-monitor "Started" 8×) and the
  monitor would report `NO_WAYLAND_SOCKET` — the same observable as the drm run.

## What this means

1. **The vblank/page-flip hypothesis is refuted.** The failure is identical in shape on a backend with no
   vblank/page-flip/atomic path. Page-flip tracing is therefore **not** the next step.
2. **The failure is downstream of the backend.** Both real-output backends (drm, fbdev) fail after
   loading all ivi modules; the headless backend (a virtual output) succeeds (`WAYLAND_SOCKET_UP`). The
   common factor is the ivi-shell/compositor startup over a *real* output, not how the backend scans out.
3. **The three client-side questions stay unanswered for the same reason as doc 05:** no socket means no
   client can connect, so AppLauncher/AppHomeScreen never register and `invalid object N` cannot be
   produced by a connected client. Absence of the error is still not evidence about the error.
4. A secondary observation, now measured to be **fbdev-specific, not the common thread**: the bochs
   framebuffer map emits `WARNING: ... drivers/gpu/drm/ttm/ttm_bo_vm.c:265 ttm_bo_vm_open` (bochs-drm's
   TTM buffer-object mmap path), but the drm-backend run emits **zero** TTM warnings and still fails the
   same way (doc 07). So there is no kernel-side warning in the drm failure; the common cause is a
   userspace weston startup stall over a real output.

## Negative is recorded

fbdev-backend **also fails**. That is the result: the stall is not vblank. The next step is to find where
in the real-output startup path (after the last module load, before `wl_display_run`) weston's main thread
enters its `nanosleep` — one userspace instrument (e.g. strace of the main thread), not a kernel change and
not drm ioctl tracing.
