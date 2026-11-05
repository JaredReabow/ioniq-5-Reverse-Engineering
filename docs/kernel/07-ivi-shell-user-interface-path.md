# The `ivi-shell-user-interface` path is a real bug — but not the cause of the missing socket

Date: 2026-11-06. Doc 06 established that both real-output backends fail identically after loading the
ivi modules while headless succeeds. The next hypothesis to check: the shell user-interface binary path.
This documents the one-change test and its result: **fixing the path does not make the socket appear.**

## The hypothesis, verified as a real bug first

The vendor `weston_1920.ini` names a path that does not exist:

```
ivi-shell-user-interface=/usr/lib/weston/weston-ivi-shell-user-interface   ← config
/usr/lib/weston/weston-ivi-shell-user-interface: File not found by ext2_lookup
/usr/libexec/weston-ivi-shell-user-interface     215,480 bytes, 0755, present
```

So the configuration bug is real (this is a third wrong/absent vendor config value, alongside the
`backend=ias-backend.so` substitution and the `HDMI1`/`HDMI2` outputs this project already corrected).

## The test: fix the path, keep drm-backend, one variable

Changed `ivi-shell-user-interface=/usr/libexec/weston-ivi-shell-user-interface` (and kept
`backend=drm-backend.so`, wrapper `weston.real --use-pixman --tty=1`), injected into the CoW clone,
booted, and measured.

## Result: the socket still does not appear

```
ALIVE=y                              # weston.real still running at +8 s
SOCKFILES=                           # find /run -type s  →  empty
RUNUSER= ( /run/user/50/ empty )     # no wayland-0
FDS= 0→/dev/null 1→/tmp/w.log 2→/tmp/w.log 19→socket:[2066] 26→timerfd 27→dltpipe
PS= 691 weston.real, 693 weston.real <defunct>
```

The one socket fd (`19→socket:[2066]`) and the defunct child are the **keyboard** launch
(`launching '/usr/libexec/weston-keyboard'` → `executing ... failed: No such file`), not the shell UI.
There is still **no listening socket and no epoll fd**. So fixing the path changed nothing observable:
the compositor still never enters its serving loop.

## Why the path cannot be the cause (source-verified)

The shell user-interface is not launched eagerly. In the ivi-shell's hmi-controller
(`hmi-controller.c`):

```c
controller_module_init(...) {
    ...
    wl_event_loop_add_idle(loop, launch_hmi_client_process, hmi_ctrl);   /* line 2018 */
}
static void launch_hmi_client_process(void *data) {
    hmi_ctrl->user_interface = weston_client_start(compositor,
                                                   hmi_ctrl->hmi_setting->ivi_homescreen);
}
```

`launch_hmi_client_process` is an **idle callback on the event loop**. It only runs once weston enters
`wl_display_run` — the same loop that would have created the epoll fd. Since weston never reaches that
loop (no epoll fd, main thread in `nanosleep`), the homescreen client is never spawned, correct path or
not. The wrong path is therefore **dormant**: a genuine config bug, but downstream of the actual failure.

## Refinement on the `ttm_bo_vm_open` thread

The earlier note flagged `ttm_bo_vm_open` as "the only kernel-side difference". That is now measured to
be **fbdev-specific**: the drm-backend run emits **zero** TTM warnings (`grep -c ttm_bo_vm_open` = 0)
and still fails the same way. So the TTM warning is not the common thread either — it is a side-effect of
mmap'ing the bochs fb0 (a TTM buffer object), which only the fbdev backend does.

## Where this leaves the failure

- The wrong `ivi-shell-user-interface` path is real, and worth fixing, but it is not the cause.
- The failure is a **userspace weston startup stall** common to drm and fbdev, absent in headless, with
  **no kernel-side warning in the drm case**.
- The strongest single piece of evidence remains: **no epoll fd** — the compositor never entered its
  serving loop. Next step is to find where in the real-output startup path (between the last module load
  and `weston_compositor_wake`/`wl_display_run`) weston enters its `nanosleep`, e.g. one instrument on
  the weston side (strace of the main thread), not a kernel change.
