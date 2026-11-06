# The duplicate registration is not the killer: it happened to 2 of 15 apps and killed neither

Date: 2026-11-06. Read from a **raw, retained** launcher log (211,792 B) rather than from a probe's summary string - which is what rule
19 now requires and what this project had stopped doing.

## The evidence

`work/vm/vendor-userspace-260128/micom-contract/full-chain-timeout120-legal-reason11-llvmpipe-home-navi-home-deadline-piefix-1536-evidence/launcher-chain/launcher.log`

```
appId  name                 REGISTERED  DUP_ERR  TERMINATED
    2  ApplicationManager            1        0           0
   10  AppStandbyClock               1        0           0
   11  AppHomeScreen                 1        0           0     <- registered cleanly, never terminated
   12  AppCamera                     1        1           0     <- duplicate, NOT terminated
   17  NotificationManager           1        0           0
   22  AppOSDManager                 2        0           0
   30  AppNavi                       1        1           0     <- duplicate, NOT terminated
   40  AppVH                        10        0           0
   60  AppSetup                      1        0           0
   77  AppEURadio                    1        0           0
  121  BluetoothHMI                 1        0           0
  200  TmsGuiApp                    1        0           0
  311  AppDMClient                  1        0           0
  312  LocationManager              1        0           0
  400  UserProfileManager            1        0           0
```

**Fifteen apps registered. Two produced `[REGISTERED ERROR] Already registered`. Zero were terminated.**

## What that overturns

1. **The duplicate is a vendor behaviour, not our artefact.** It happened to `AppCamera` and `AppNavi` in a chain that ran without our
   surface-id patch and without the label fix. So it is normal, and it is **survivable**.
2. **`[REGISTERED ERROR] Already registered` does not cause the kill.** Neither app that produced it was terminated. The earlier reading -
   duplicate guard terminates the app - was a correlation in a probe summary, not a causality on a raw log.
3. **App 11 has registered cleanly in this project before.** In that chain it registered once, cleared its loading timeout, and was never
   terminated. So the failure in our recent runs is **specific to how app 11 is being started now**, not to app 11.

## The shape that survives

In the good chain the order is:

```
[REGISTERED] ... AppId[12][AppCamera] | time 00:00:35.842
ClearTimeoutLoading : 12, PID : 785   | time 00:00:35.842
[REGISTERED ERROR] Already registered | time 00:00:35.895
```

**`ClearTimeoutLoading` immediately follows registration** - the launcher clears its own deadline because the app was in time. The duplicate
arrives 53 ms later and is ignored.

In our failing runs the order starts with `[TIMEOUT] [2 Group] AppID : 11`, and the registration is the launcher's own fallback. **So the
difference is not the duplicate; it is whether the app beat the timeout** - which is the 39.8 s vs 48.58 s cold / 1.17-8.13 s warm arithmetic
already recorded in `docs/vm/52`.

## What that means for the next run

**`ALIVE_60S=yes` in `docs/kernel/31` may already have been the success case.** That run was warm and the instance survived 60 s; its
`WARM_DUPLICATE=1` came from a probe-assembled string (rule 19) and is now suspect. **The duplicate may not have happened at all.**

So the next run is not "fix the duplicate". It is:

1. **retain the raw launcher log** (host volume, verified export);
2. warm start, **power-on sent**, and read the **raw** order: does `[TIMEOUT]` precede `[REGISTERED]` for app 11, or does
   `ClearTimeoutLoading` follow it directly as it does for the healthy apps?
3. if `ClearTimeoutLoading` follows `[REGISTERED]` directly, **the registration blocker was already closed** and the display thread is at Astra's
   gate 2 (power-on consumed), not gate 1.

**And the honest note:** three documents were built on a duplicate that (a) is not fatal, (b) occurs in stock-ish chains, and (c) may not even
have happened in the run that reported it. **The raw log was on disk the whole time**, in this project's own workspace, from an earlier chain.
