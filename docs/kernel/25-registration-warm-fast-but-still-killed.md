# Registration time collapses on warm relaunch — but the app is still terminated ~24 s later (SIGTERM)

Date: 2026-11-06. The "launch alone / pre-warm" hypothesis was tested by measuring registration time
across the launcher's own relaunches in the boot-46 log. The cold/warm split is decisive, and it
surfaces a second mechanism.

## The registration times (boot 46, AppHomeScreen appId 11)

| launch pid | launch time | registered time | **register took** |
|---|---|---|---|
| 2272 (cold, in group) | 21:39:22.948 | 21:40:11.526 | **48.58 s** |
| 2606 | 21:40:27.678 | 21:40:33.644 | 5.97 s |
| 2857 | 21:40:57.712 | 21:41:04.414 | 6.70 s |
| 3721 | 21:41:29.870 | 21:41:37.997 | 8.13 s |
| 4160 | 21:41:54.576 | 21:41:57.175 | 2.60 s |
| 4353 | 21:42:06.454 | 21:42:07.838 | 1.38 s |
| 4562 | 21:42:16.589 | 21:42:17.761 | 1.17 s |
| 4704 | 21:42:26.598 | 21:42:28.692 | 2.09 s |

**The 48.6 s is only the cold first launch.** Every warm relaunch registers in 1–8 s — far inside the
45 s deadline. The 167 ms margin is therefore a **cold-start/contention artifact**, exactly as the user
hypothesised.

## But the deregister loop continues on warm relaunches

The first instance (2272) is terminated at 21:40:27.199 with `appProcessFinishedSlot [15][0][1][11]` —
exit code **15 (SIGTERM)**, the duplicate-registration `onDemandAppKill`, not a crash. Then the warm
relaunch 2606 registers fast, `[Group 2] Launch complete` at 21:40:33.644, and is still terminated at
21:40:57.199 — **~24 s later, again SIGTERM**. So even a fast-registering instance is killed a fixed
interval after registration.

## The honest reading

- **Confirmed:** registration time is the variable that made the app miss its deadline; it drops from
  48.6 s to 1–8 s once warm. The deadline was never the only thing between the app and a stable surface.
- **New fact:** a warm, fast-registering instance is terminated ~24 s after registering (SIGTERM), so
  there is a **second termination mechanism** — the duplicate-registration guard re-fires, or a
  ~24 s watchdog — independent of the 45 s preload deadline. That is the next thing to name, and the
  launcher log around 21:40:33 → 21:40:57 is where it will be found (the same log that answered the last
  four questions).

## Files

- `work/vm/kbuild/ws/partimg-build/AppLauncher.patched.bin` — both patches (surface-id + deadline).
- the registration table above is from boot 46's launcher log (re-derived from the run).
