# The id value is not the fault: AppHomeScreen never registers a surface, while every other app does

Date: 2026-11-06. The single-variable experiment: only the patched id changed, 1010 → 2170. Everything
else (label, warmth, power-on call, both monitors) frozen.

## Results

- **Gate 2 again closed**: `GATE2_POWER_STATUS=11` — power-on consumed.
- **No surface at 2170.** `GATE5_SURFACES=[Surface id(30000)|Surface id(1002)|Surface id(1003)]`.
- **The full weston log (217,977 bytes) names every surface — and AppHomeScreen is absent.**

```
create_hmi_client … 1000, "AppDMClient"        ×2
create_hmi_client … 1001, "AppDMClient"
create_hmi_client … 1002, "AppOSDManager"      ×2
create_hmi_client … 1003, "AppOSDManager"
create_hmi_client … 1004, "AppStandbyClock"
create_hmi_client … 1004, "BluetoothHMI"
create_hmi_client … 1005, "AppEURadio"
create_hmi_client … 1030, "NotificationManager"
create_hmi_client … 2080, "AppCamera"          ×2
```

`AppHomeScreen` appears **0 times** in the whole log. No `surface_create` for 1010 or 2170. And `2080`
is unambiguously `AppCamera`'s id — so the surface that appeared in the earlier 2080 run was AppCamera's,
never the home screen's.

## What this settles

The decision tree's second branch, confirmed and sharpened: **the id value is not the fault.** The warm,
labelled, power-on-consumed home screen never registers a surface with `ivi_application`, while
AppDMClient, AppOSDManager, AppStandbyClock, BluetoothHMI, AppEURadio, NotificationManager and AppCamera
all do. The surface-id patch (2080 → 1010 → 2170) was chasing a variable that is not in the creation path
at all: the app does not create/register a surface regardless of the requested id.

The fault is upstream of the id — AppHomeScreen's Wayland/EGL path does not reach
`ivi_application.surface_create`. That is the next, and now precisely-bounded, question.

## Files

- `work/vm/kbuild/boot57-2170.log` — the run.
- `work/vm/kbuild/ws/partimg-build/endgame.sh` — the probe.
- the weston log was exported to the run's `dbg-out.txt` (`BEGIN weston 217977 … ENDweston`); decoded to
  `work/vm/kbuild/ws/runs/1793930191302252000/exported-weston.bin`.
