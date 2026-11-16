# Phase 2 result: `drm-backend.so` binds `/dev/dri/card0`, but weston never serves a client

Date: 2026-11-06. The DRM device was created (docs 01–02). This is what happened when the vendor's
own `drm-backend.so` was pointed at it, measured two ways (the authentic esinit path, and a manual run).

## What was changed for this test

In the CoW clone `work/vm/kbuild/ws/` only, two projection files were rewritten (and synced back into
partition p5 with `sync-partition.py`):

- `/etc/xdg/weston/weston_1920.ini`: `backend=headless-backend.so` → `backend=drm-backend.so`, and the
  `[output]` section renamed `HDMI1` → `Virtual-1` (the bochs connector name; `HDMI1`/`HDMI2` do not
  exist on this device). `mode=1920x720` was left, but weston chose the connector's preferred
  1024×768.
- `/usr/bin/weston` (the wrapper): kept esinit's `--tty=1`, dropped the headless-only
  `--width/--height`, and added `--use-pixman` (the pixman renderer path, since there is no GPU for
  the GL renderer). The `pixman-solid-shim.so` preload was retained.

No vendor binary was modified; `esinit` and `weston.real` are the shipped ones.

## Result 1 — the vendor `drm-backend.so` initialises the new DRM device

Weston's own log (authentic binary, verbatim, from the esinit path):

```
Loading module '/usr/lib/weston/drm-backend.so'
initializing drm backend
using /dev/dri/card0
Output Virtual-1, (connector 20, crtc 18)
        mode 1024x768@60.0, preferred, current
        mode 1600x1200@60.0 … 640x480@59.9
Compositor capabilities: arbitrary surface rotation: yes; screen capture uses y-flip: yes …
Loading module '/usr/lib/weston/ivi-shell.so'
Loading module '/usr/lib/weston/ivi-window-manager.so'
Loading module '/usr/lib/weston/ivi-controller.so'
ivi-controller: No ivi-input-module set
Loading module '/weston-vm-input.so'
```

So the vendor's `drm-backend.so` — the thing this whole line of work wanted to use instead of
`headless-backend.so` — **does load, does open `/dev/dri/card0`, and does enumerate the bochs
`Virtual-1` output.** The DRM device is real and usable by the vendor backend at the KMS level.

## Result 2 — but weston never reaches a usable compositor

The same boot's monitor reports, after waiting the full 240 s:

```
[apps-check] NO_WAYLAND_SOCKET after 240s
```

and a manual run (research init, weston launched directly) confirms it is not a monitor-path problem:

```
weston_pid=690 alive=yes          # weston.real is still running
find-wayland=[]                   # no wayland-* socket anywhere in /run /tmp /var/run
wchan=[hrtimer_nanosleep]         # main thread is asleep, not crashed
```

Weston loaded every module and then **stalls with its main thread in `nanosleep` and no wayland socket
ever created.** It is not a crash (the process stays alive); it is a stall before `weston` binds its
listening socket. Because there is no socket, the vendor application stack (AppLauncher →
AppHomeScreen) has nothing to connect to, so it cannot run at all against drm-backend in this
configuration.

## What this means for the `invalid object N` question

**Not yet answerable.** The `wl_display@1: error 0: invalid object N` failure this project is chasing
happens when a Qt client connects to the compositor. With `headless-backend.so` the compositor comes up
(measured, docs/vm/authentic-hmi.md and this run's `[apps-check] WAYLAND_SOCKET_UP`), so the client
gets far enough to die with `invalid object`. With `drm-backend.so` the compositor does not come up at
all, so the client never connects and the error cannot be compared. The DRM-device half of Phase 2 is
done; the "did it change the app's behaviour" half is blocked on weston actually serving a client over
the DRM backend.

## Why weston stalls (hypothesis, labelled as such)

The measured facts are: alive, `wchan=hrtimer_nanosleep`, no socket. The natural reading is that the
drm-backend's first modeset/repaint is waiting for a vblank or page-flip event that the bochs KMS
device — a software framebuffer with no hardware scanout under QEMU TCG — does not deliver, so weston
sleeps forever in its frame scheduler before it finishes binding the socket. That is a hypothesis about
mechanism, **not** a measured claim: I did not capture the page-flip wait directly. What is measured is
the observable symptom (alive, nanosleep, no socket).

A likely next step, if this is pursued: run weston with `WAYLAND_DEBUG=server` (already exported by the
wrapper) and a `strace` of the page-flip/vblank ioctls, or try `drm-backend` with the
`DRM_CAP_ATOMIC`/vblank path traced — one instrument, not two.

## Honest summary

| question | answer |
|---|---|
| does the vendor `drm-backend.so` bind the new DRM device? | **yes** — `using /dev/dri/card0`, `Output Virtual-1` |
| does weston then serve a client? | **no** — no wayland socket, main thread in `nanosleep` |
| did `drm-backend` change the `invalid object N` behaviour? | **unmeasurable** — the app cannot connect because weston never binds its socket |
