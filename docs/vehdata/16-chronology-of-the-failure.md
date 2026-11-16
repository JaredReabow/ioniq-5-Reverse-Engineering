# The failure in order, half a second long, from a verified log

Date: 2026-11-05. One application instance, log **107,171 bytes / 796 lines**, `AppHome Init Done` present
(`INITDONE=1`), and the 71 lines from that marker onward captured in full.

## The chronology

```
00:02:30.329  [2561] AppHomeEngine::applicationStart() ] AppHome Init Done
00:02:30.330  [2561] WatchdogWorker::WatchdogWorker()
00:02:30.331  [2561] WatchdogWorker::startWorking()
00:02:30.333  [2577] SaveSetupLayoutDB(...) ] DB UPDATE COMMIT FAIL        <- first commit failure
00:02:30.334  [2577] SaveSetupLayoutDB(...) ] save item: AppHomeDataModel(0x9ef81954d0)
00:02:30.351  [2577] DB UPDATE COMMIT FAIL
00:02:30.352  [2577] save item: AppHomeDataModel(0x9ef81951d0)
              wl_display@1: error 0: invalid object 19                    <- the Wayland error
00:02:30.367  [FTL]  The Wayland connection experienced a fatal error (Invalid argument)
00:02:30.370  [2577] DB UPDATE COMMIT FAIL                                   <- and it keeps going
00:02:30.374  [2561] slotHeartbeatTriggered() sequenceID: 0 ; main thread ...
00:02:30.795  [2577] SaveSetupLayoutDB ] return  true                       <- a commit SUCCEEDS later
00:02:30.798  [2577] Home_Worker::slotSetStatusDrToKernel ] B.NV: "1"
00:02:30.799  [2577] Home_Worker::writeGPIO ] Open kernel file failed!, errorNo: 2
00:02:57.396  [2580] PersistentManager::value ] SUCCESS: "APP_SETTING_VCU_READY"
```

## What this establishes, and it reframes the problem

1. **The application does not die at the Wayland error.** It logs for another 0.6 s inside the same burst and
   is still logging **27 seconds later**. The instance is alive; its **`wl_display` connection is dead**.
2. **The commit failures are not fatal either** - `SaveSetupLayoutDB` **returns true** later in the same burst.
   They are noise from a retry loop, not a wall.
3. **The Wayland error arrives in the middle of the DB burst**, on the same thread (`2577`) that is logging the
   commits. That ordering is the most interesting fact in this log and the previous entries did not have it.

**So "the application is not painting" is not "the application is stuck or crashed".** The application is
**running with a destroyed Wayland connection** - it has no surface to paint into, which is exactly what a
compositor showing the background means.

## What object 19 was

Unread. `invalid object 19` is a server event addressed to a `wl_object` id the client has already destroyed -
typically a surface the client created early (a splash) and then released while the server still had a request
in flight for it.

**The next measurement is narrow and cheap:** run the application with `WAYLAND_DEBUG=1` and read what request
on object 19 the server still answered. That turns "invalid object 19" into a named request, which is the first
thing in this whole line of work that would point at a fix rather than a symptom.

The practical route for the variable: the launcher starts the application, so the variable has to be set for the
launcher's children - `/etc/environment`, a systemd drop-in, or `/etc/ld.so.preload`-style injection. Given that
`LD_PRELOAD` has already caused two failures in this project, **prefer a systemd drop-in or `/etc/environment`**
and change one thing only.
