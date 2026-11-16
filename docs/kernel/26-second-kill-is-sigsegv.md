# The second termination is a SIGSEGV crash, not a watchdog — the warm instance dies in the layout

Date: 2026-11-06. Doc 25 showed a warm relaunch is SIGTERMed ~24 s after registering. The 24 s window
in the launcher log names the mechanism, and it is a crash.

## The decisive window (boot 46)

```
21:40:33.644  [REGISTERED] AppId[11][AppHomeScreen]          ← warm relaunch 2606 registers (5.97 s)
21:40:33.644  ClearTimeoutLoading : 11, PID : 2606            ← deadline cleared, app registered in time
… groups 3/4/5 launch …
21:40:57.198  [ERR CODE:1] App has been Crashed.              ← the launcher reports a crash
21:40:57.199  AppID : 11, PID : 2606, State : 0
21:40:57.199  appProcessFinishedSlot [11][0][1][11]           ← exit code 11 = SIGSEGV
21:40:57.202  notifyAppTerminate [AppHomeScreen][11]
21:40:57.203  requestAppDeregister appId[11]
```

`appProcessFinishedSlot [11][0][1][11]` — the leading **11 is SIGSEGV**. The warm instance did not time
out and was not SIGTERMed by the duplicate guard; it **crashed** ~24 s after registering, during the
power-on layout.

## What this means

- The registration-time hypothesis (doc 25) stands: cold 48.58 s, warm 1–8 s.
- The "second termination mechanism" is not a second policy — it is **the app itself faulting**
  (SIGSEGV) after a fast registration, in the same layout stage where the earlier runs showed
  `SCREEN_STATE: START DRAW` → `injectWidgetItemToAdvancedPage … FOUND` → `Trace/breakpoint trap`. The
  SIGTRAP then and the SIGSEGV now are the same crash at two different points of the widget/EGL path.
- This is a **stand-in problem**, as the user predicted: the app reaches the layout and faults where it
  expects something the projection does not yet provide (the CAN-backed widget data, or a DRM-side
  rendering surface). It is no longer a timing problem.

## The honest summary of the whole display effort

The cold start is 48.6 s and the warm start is 1–8 s, so **the projection's own warm-up is what crossed
the vendor's deadline**; once warm, the app registers well inside the deadline and then faults in the
layout. Both facts are measurements, and together they are the fairest account of a failure that looked
like a vendor fault for a dozen entries: one timing artefact (fixed by warm-up) and one crash in the
widget/EGL layout (still open).

## Files

- `work/vm/kbuild/boot46-deadline.log` — the run whose launcher log contains this window.
