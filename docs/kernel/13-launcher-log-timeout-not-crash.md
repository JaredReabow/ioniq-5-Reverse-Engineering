# The app is not crashing — it is deregistered by the launcher after a 3 ms registration timeout

Date: 2026-11-06. Doc 12 left the power-on crash unexplained and named two hypotheses (a SQLite
widget-settings failure, and a second `invalid object`). This run dumped the launcher's own stderr
(`/tmp/applauncher-stdio.log`, 149,673 bytes, saved as
`work/vm/kbuild/applauncher-stdio-crash.log`) after the crash. Both hypotheses are refuted, and the
real cause is in that log.

## What the launcher log shows (verbatim, the decisive 650 ms)

```
[TIMEOUT] [2 Group] AppID : 11, PID : 2305                                | 19:59:12.511
[REGISTERED] registeredFromNativeApp AppId[11][AppHomeScreen] …           | 19:59:12.514   (3 ms later)
… [Group 2] Launch complete                                               | 19:59:12.518
[REGISTERED ERROR] Already registered AppId[11][AppHomeScreen]            | 19:59:12.592
AppManagerInterface::requestAppDeregister appId[11][AppHomeScreen]        | 19:59:13.157   (terminated)
```

The same pattern repeats for every app in the group — AppStandbyClock, AppCamera, AppDMClient, and
AppHomeScreen:

```
[TIMEOUT] [1 Group] AppID : 12, PID : 2066   → [REGISTERED] … 2 ms later → … → Already registered → deregister
[TIMEOUT] [1 Group] AppID : 10, PID : 2070   → [REGISTERED] … 1 ms later → …
```

## What it means

AppHomeScreen is **not** crashing and is **not** faulting. It registers its native-app handle **~3 ms
after** the launcher's per-app registration timeout, so the launcher has already moved on; when the
registration then lands, the launcher logs `Already registered`, treats it as a duplicate, and
`requestAppDeregister` sends the app SIGTERM (exit 15). The pid change the earlier runs saw (2305 →
2481) is that deregister + relaunch loop, not a segfault.

## The two hypotheses, checked

- **SQLite failure** — refuted. `grep -iE 'COMMIT FAIL|BEGIN TRANSACTION|QSqlError|no such table|DELETE
  FAIL'` over the whole 149,673-byte log returns **empty**.
- **A second `invalid object`** — refuted. `grep -iE 'invalid object|wl_display@1|error 0'` returns
  **empty**. (The only "terminate" hits are the launcher's own `notifyAppTerminate` signal.)

So the power-on layout is **not** a display fault and **not** a database fault. It is a launcher
registration-timeout race, and the app is ~3 ms over the line under this backend.

## Why this fits the DRM-vs-headless difference

The laid-out frame (`docs/vm/38`, 16,062 bytes) was produced on **headless**. This run is on **drm** with
the bochs device and the pixman renderer, which costs the guest a little more CPU — enough that the app's
registration lands just past the launcher's timeout. That is a timing margin, not a backend capability.
The compositor, the app, the DRM device, the 1920×720 mode, and the seat all work (docs 01–11); the only
thing between here and the laid-out frame is the launcher deregistering the app ~3 ms too late.

## Next step (one variable)

Make the registration land inside the timeout — either raise the launcher's registration timeout (find
the timeout value/unit in the launcher config or binary), or reduce startup latency (more vCPUs, or
`taskset`/nice the app's launch). Then the power-on call should reach a live instance and the laid-out
frame can be captured.

## The session's most reusable finding

The app's own log was the answer for the third time: first `invalid object 19` (the seat), then the
crash loop (this deregister+relaunch), now the 3 ms timeout. **Every time this project has been stuck,
the answer was in a log nobody had collected.** The rule for the next person: before theorising about a
backend, collect the application's own stderr and read the last lines before the pid changes.

## Files

- `work/vm/kbuild/applauncher-stdio-crash.log` — the launcher log (149,673 bytes).
- `work/vm/kbuild/boot38-appcrash.log` — the boot.
- `work/vm/kbuild/ws/partimg-build/appcrash-dump.sh` — the capture script.
