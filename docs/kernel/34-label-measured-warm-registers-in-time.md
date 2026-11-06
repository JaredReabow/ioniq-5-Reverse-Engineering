# The label is measured, and the warm instance registers in time — the registration blocker is closed

Date: 2026-11-06. The read, not a fix: warm relaunch, power-on, raw order, label while alive, raw log
retained (167,815 bytes).

## The label, now measured (not NOT MEASURED)

```
[read] LABEL=[App::home]
[read] PS_LABEL=[App::home]
```

The warm instance runs as `App::home`. That closes the label check that boot 50 could only mark
NOT MEASURED, and confirms the SMACK exec-label fix (doc 27/28) end-to-end.

## The raw order for app 11

```
[TIMEOUT] [2 Group] AppID : 11, PID : 2331                         01:26:38.462   ← cold
[REGISTERED] registeredFromNativeApp AppId[11]                     01:26:38.509
ClearTimeoutLoading : 11, PID : 0                                  01:26:38.509   ← cold fallback cleared
[REGISTERED ERROR] Already registered AppId[11]                    01:26:38.544   ← duplicate, survivable
[REGISTERED] registeredFromNativeApp AppId[11]                     01:26:44.021   ← warm
ClearTimeoutLoading : 11, PID : 2516                               01:26:44.021   ← cleared, the warm pid
```

- The **cold** instance (2331) is the familiar failure: `[TIMEOUT]` first, then `[REGISTERED]` 47 ms
  later, then the duplicate.
- The **warm** instance (2516) is the healthy pattern the user's raw chain showed: `[REGISTERED]` then
  `ClearTimeoutLoading : 11, PID : 2516` **directly, with no preceding `[TIMEOUT]`**. It registered in
  time and the timeout was cleared against its own pid.

## What this means

The registration blocker is **closed** — the warm instance beats the timeout and is cleared by the
launcher itself. The duplicate is present but is vendor behaviour and survivable (the warm instance is
the same pid both before and after). The only question left is **the frame**: whether the power-on that
was sent to the warm instance is consumed into a laid-out home screen, which this read deliberately did
not capture.

## Files

- `work/vm/kbuild/boot55-read.log` — the run.
- `work/vm/kbuild/ws/partimg-build/read-raw.sh` — the probe.
- the raw launcher log was exported to the run's `dbg-out.txt` (`BEGIN raw 167815 … ENDraw`).
