# The duplicate registration is the same pid — the stand-in's handshake, not two instances

Date: 2026-11-06. The launcher log's registration sequence was extracted with timestamps. It answers
the two-instances vs retry question: it is a retry from one pid.

## The sequence (boot 50, app 11, pid 2303)

```
23:03:09.771  m_AppProcess->start(/app/bin/AppHomeScreen) PID[2303]
23:03:49.566  [TIMEOUT] [2 Group] AppID : 11, PID : 2303
23:03:49.596  [REGISTERED] registeredFromNativeApp AppId[11][AppHomeScreen]
23:03:49.606  [REGISTERED ERROR] Already registered AppId[11][AppHomeScreen]   ← 10 ms later
23:03:49.630  AppID : 11, PID : 0, State : 0
23:03:49.631  notifyAppTerminate [AppHomeScreen][15]  →  requestAppDeregister
23:03:49.920  m_AppProcess->start(/app/bin/AppHomeScreen)   ← the next launch is after the kill
```

There is **one** `start(…AppHomeScreen) PID[2303]` before the duplicate, and the next launch is after the
kill. So the `REGISTERED` and `REGISTERED ERROR` are the **same pid (2303) registering twice, 10 ms
apart** — not two live instances.

## What this means

This is the user's third hypothesis, measured: the projection **replaced the real `ApplicationManager`
with a D-Bus stand-in**, and `RequestRegister` is called, gets no ack the way the real manager would
send, and is retried — producing one `REGISTERED` followed by `REGISTERED ERROR` from the same pid, then
the duplicate-guard `onDemandAppKill`. The fix is projection-side and small: **make the stand-in answer
the registration method** (ack it) so the launcher does not retry, rather than touching the launcher.

## Checks 1 and 3, corrected to "not measured"

Doc 28 flagged `APP_LABEL=[]` and `PHEV_DIR=Permission denied`. Both are **instrument defects, not vendor
behaviour**: the monitor ran unlabelled (`_`), so (a) it read the label after the pid was dead, and (b) it
could not list a `Data::commonphev` directory under `App::home * → ----t-`. They are recorded here as
**NOT MEASURED**, not as failures; the next monitor must itself run under a label that can see them.

## Files

- the sequence above is from boot 50's launcher log (re-derived).
