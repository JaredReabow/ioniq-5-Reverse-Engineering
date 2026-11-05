# The CAN shim was crashing the application: the app's own log says so

Date: 2026-11-05. The launcher redirects the application's stderr; the console had been printing the
redirection all along:

```
AppHomeScreen ) >> /tmp/apphome-byhand.log 2>&1
```

## What the log says, 98,087 bytes in

The application **initialises completely** and then dies:

```
[ERR] [ void AppHomeEngine::applicationStart() ][ 901 ] AppHome Init Done
[FTL] wl_display@1: error 0: invalid object 19
[FTL] [QtMsg] The Wayland connection experienced a fatal error (Invalid argument)
[FTL] [QtMsg] The Wayland connection experienced a fatal error (Invalid argument)
```

So the restart loop this project spent three runs blaming on power state is a **Wayland protocol error**:
`invalid object 19` on `wl_display@1`. The app exits, the launcher restarts it, and every state event sent
to the previous instance goes nowhere.

## The A/B test, and the result is against my own work

The prime suspect was the shim I added: `/etc/ld.so.preload` containing `can_shim.so`, which interposes
`socket`, `bind`, `ioctl`, `setsockopt` and `close` process-wide and opens an `AF_UNIX` socketpair with a
feeder thread for **every** `PF_CAN` socket the application asks for (81 of them in one run).

| configuration | application pids over ~90 s | verdict |
|---|---|---|
| **with** `can_shim.so` preloaded | 2452 -> 2619; then 2581 **and** 2500 together; then 3225 | **restart loop** |
| **without** the preload | **3015 -> 3015 -> 3015** (`same_pid=yes`, twice) | **stable** |

**My shim was the cause of the instability.** The application held one pid for the whole observation window
once it was removed, and the Wayland fatal errors in the log are consistent with a client whose connection is
being disturbed by a library that overrides `close()` and hands out socketpairs in place of the sockets the
Wayland client expects.

## What this corrects

- **"The app keeps restarting, so no state fix survives"** was right as an observation and wrong as a cause:
  the restart was caused by my instrument, not by the vendor's software or by the projection's power state.
- **The CAN shim is not usable as written.** It has to be scoped to the application only (not
  `/etc/ld.so.preload` process-wide), and it must not override `close()` globally. Until then it does more
  damage than the missing CAN frames it stands in for.
- The 114,782-byte frame is the **application's standby face**, so the power-on call still did not produce
  the laid-out screen in this run - and that question is now separable, because the application can be made
  to stay alive.

## Next

1. Scope the shim: `LD_PRELOAD` for `AppHomeScreen` only, or better, match `socket(PF_CAN)` and leave `close()`
   alone - it is the `close()` override that can disturb an unrelated file descriptor.
2. With a stable application and no shim, re-run the power-on call and capture at +30/+60/+120 s. That
   isolates whether the standby face is a real state problem or was an artefact of the crash loop.

---

## 16. The shim was one cause; `ivi-wm` is another - and it is the tool I place with

Removed `/etc/ld.so.preload` and re-ran the power-on test with captures at +30/+60/+120 s. The application
**still churned**:

```
V1_APP_UP=0s pid=[2442]
V1_pid30=2518      V1_pid60=2640      V1_pid120=2640 (then a new pid later)
wayland_errs=3
```

But the difference from the run where the pid was **stable** (3015 -> 3015 -> 3015) is one thing: **that run
made no `ivi-wm` calls**. This one calls `ivi-wm 2080` immediately before every capture, because the capture
helper places the surface first.

**So the placement tool is the second crash source.** `ivi-wm` drives `ivi_window_manager` against a live
surface; the client then reports `wl_display@1: error 0: invalid object 19` and dies. That is consistent with
a protocol operation on a surface whose object the client has already replaced or destroyed - the tool wins
the race sometimes (earlier, placement did change the output) and kills the client other times.

**Which explains the most confusing observation in this series**: every "placed" capture showed the
**standby** face because placing the surface **restarted the application**, and what got photographed was a
freshly started instance that had received no state at all.

## 17. What this leaves

- **Do not call `ivi-wm` against a live application surface** while diagnosing it. It is destructive often
  enough to invalidate any conclusion drawn from a capture that follows it.
- The projection **may not need placement at all**: `ivi-window-manager.so` places surfaces itself, and the
  application is the main surface. The honest test is to **capture repeatedly with no `ivi-wm` calls at all**
  and watch the pid and the frame.
- If the app then stays alive and the frame is the standby face, the standby question is real and separable.
  If the frame is the laid-out home screen, then the UI was working all along and this project was photographing
  it with a tool that kept knocking it over.

**Established:** two of this project's own instruments - the process-wide preload and the placement tool -
each independently kill the application under test. **Not established:** what the projection shows when
nothing of ours interferes.
