# Root cause: `weston-vm-input.so` returns −1 on an empty seat list, and weston shuts down before serving

Date: 2026-11-06. `strace` on weston's startup (manual run, drm-backend, pixman shim) answered the
question docs 05–07 left open. The stall is **not** a display-backend problem at all.

## The trace, in one sequence

With `/tmp/dlt` pre-created (so the DLT logging dependency does not mask what follows — see the caution
below), weston loads everything and then tears down cleanly:

```
697 17:45:40.912 write(2, "Loading module '/weston-vm-input.so'\n", 37)
697 17:45:40.916 write(2, "VM_INPUT_NO_SEAT\n", 17)
697 17:45:40.916 epoll_ctl(3, EPOLL_CTL_DEL, 25, NULL) = 0          ← teardown begins
697 17:45:40.920 ioctl(12, DRM_IOCTL_MODE_CURSOR, …)  = -1 ENXIO
697 17:45:40.920 ioctl(12, DRM_IOCTL_MODE_SETCRTC, …) = -1 ENOENT
697 17:45:40.921 ioctl(12, DRM_IOCTL_MODE_RMFB, …)     = 0
697 17:45:40.922 ioctl(12, DRM_IOCTL_MODE_DESTROY_DUMB, …) = 0
697 17:45:40.923 ioctl(10, KDSKBMODE, 0x3)             = 0
697 17:45:40.923 ioctl(10, KDSETMODE, 0)               = 0
697 17:45:40.923 ioctl(12, DRM_IOCTL_DROP_MASTER, 0)   = 0          ← drops DRM master
697 17:45:40.923 ioctl(10, VT_SETMODE, …)              = 0          ← restores VT
697 17:45:40.925 … epoll_ctl(3, EPOLL_CTL_DEL, …) × N                ← all fds removed
697 17:45:40.943 +++ exited with 1 +++
```

Weston is **not** hanging and **not** segfaulting. Immediately after `VM_INPUT_NO_SEAT` it performs a
clean shutdown — remove framebuffers, drop DRM master, restore the VT, unregister every fd — and exits 1.
That is the `goto out` teardown in `main()` when a module fails to load.

## The cause, source-verified

The projection's own input module, `tools/uk_fw/guest/weston_vm_input.c`, in its `module_init`:

```c
head = (struct wl_list *)((char *)compositor + SEAT_LIST_OFFSET);   /* compositor->seat_list */
link = head->next;
if (!link || link == head) {
    log_literal("VM_INPUT_NO_SEAT\n", 17);
    return -1;                       /* ← fatal to weston */
}
```

weston 1.10 treats a `module_init` returning a negative value as a failed module
(`load_modules` → `goto out`). So the empty seat list makes `weston-vm-input.so` fail, and weston shuts
down **before `weston_create_listening_socket`/`wl_display_run`** — which is exactly why there is no
wayland socket and no epoll fd (docs 06's decisive measurement).

## Why headless succeeds and drm/fbdev fail — the seat, not the scanout

In weston 1.10 the seat is created by the backend. The only backend that creates one unconditionally is
headless:

```c
/* compositor-headless.c */
weston_seat_init(&b->fake_seat, b->compositor, "default");   /* line 186 */
```

drm and fbdev do **not** call `weston_seat_init`; they rely on the libinput/udev path
(`libinput-seat.c`), which only creates a seat when udev reports an input device. Under QEMU there are no
input devices — the log says `failed to create input device '/dev/input/event0'` (the Power Button, "not
tagged as input device") — so `seat_list` stays empty, and `weston-vm-input.so` fails.

This is the complete, coherent explanation of docs 05–07:

| backend | seat | `weston-vm-input.so` | result |
|---|---|---|---|
| headless | fake seat created | finds it, returns 0 | weston serves (`WAYLAND_SOCKET_UP`) |
| drm | none (no udev input) | `VM_INPUT_NO_SEAT`, returns −1 | weston shuts down, no socket |
| fbdev | none (no udev input) | `VM_INPUT_NO_SEAT`, returns −1 | weston shuts down, no socket |

The display/scanout mechanism was never the issue. The whole "real-output vs virtual-output" framing in
docs 05–07 was a proxy for "has a seat vs does not".

## The DLT caution (why the first trace looked different)

The first `strace` (without touching `/tmp/dlt`) showed the main thread in a retry loop:

```
open("/tmp/dlt", O_WRONLY|O_NONBLOCK) = -1 ENOENT
nanosleep({0, 100000000}) = 0        /* 100 ms */
… repeats forever …
write(1, "…~DLT~ … FIFO /tmp/dlt cannot be opened. Retrying later...")
```

That is the GENIVI DLT logging library, and it only occurs because the **manual (research-init) run has
no dlt-daemon**, so `/tmp/dlt` never appears. It is an artifact of the manual harness, not the display
failure — and it masked the real teardown. Pre-creating `/tmp/dlt` (a FIFO with a reader) removed it and
exposed the `VM_INPUT_NO_SEAT → exit 1` path above. The authentic boot runs dlt-daemon, so it is
unaffected by the DLT stall.

## What this means

1. **The DRM device and `drm-backend.so` were working all along.** The vendor backend bound `card0`,
   created the `Virtual-1` output, and was ready to scan out. The thing that stopped weston was a
   projection input module returning −1 on an empty seat list.
2. **The fix is in the projection, not the kernel and not a vendor binary.** One line in
   `weston_vm_input.c`: return 0 (a no-op module) instead of −1 when `seat_list` is empty — or create a
   fake seat, as headless does. Either unblocks weston to reach its listening socket.
3. **The `invalid object N` question is now reachable.** Once `weston-vm-input.so` stops failing, weston
   should bind `/run/user/*/wayland-0` and the vendor app stack can connect; the client-side error can
   finally be measured for a client that actually connected (the trap called out in doc 05/06).

## Next step (one change)

Rebuild `weston-vm-input.so` with `return 0` (or a fake seat) on the empty-seat path, inject it, and
boot the authentic drm path; check for the wayland socket first, then AppLauncher/AppHomeScreen, then
`invalid object N`.
