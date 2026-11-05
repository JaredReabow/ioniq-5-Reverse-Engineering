# Part B — D-Bus `NotifyCANTPRECVMsg` injection attempt — **not a valid test**

Date: 2026-11-05. Workspace: `work/vm/vehdata`. Run: `work/vm/vehdata/runs/1793857420103938000`.

**Verdict: this run is invalid as an injection test.** The captured frame is the app's
**powered-off presentation** (dark background, title bar, KIA logo, no widgets), not the laid-out
home screen. `set_power_on_status` did not take effect, so the injected frames were never going to
be visible. The capture must therefore not be read as evidence for or against the D-Bus path.

## What was attempted

After `set_power_on_status`, the guest emitted these system-bus signals
(`dbus-send --system --type=signal /Can com.lge.car.micom.can.NotifyCANTPRECVMsg <ay>`):

```
# SOC frame: CAN id 0x2fc, DLC 8, data 00 00 12 00 00 00 00 77  (byte 7 = 119 -> 59.5 %)
array:byte:0x02,0xfc,0x08,0x00,0x00,0x12,0x00,0x00,0x00,0x00,0x77
# DTE candidates on ids the app requested via AskCANMMCANMicomReq
array:byte:0x01,0x9e,0x08,0x04,0x01,0x00,0x00,0x00,0x00,0x00,0x00
array:byte:0x01,0x9f,0x08,0x04,0x01,0x00,0x00,0x00,0x00,0x00,0x00
array:byte:0x01,0xa0,0x08,0x04,0x01,0x00,0x00,0x00,0x00,0x00,0x00
array:byte:0x01,0x2f,0x08,0x50,0x00,0x00,0x00,0x00,0x00,0x00,0x00
```

## Why the test never exercised the widgets

- `NAME_OWNED=[com.lge.hkmc.avn.appfunc.AppHomeScreen]` — the app owned its name before the call.
- `SET_POWER_ON_RESULT=[method return …]` — the call landed and was accepted.
- Power/acc/ign were already `int32 1` before and after — the value did not move.
- The app's 1926×753 surface (id 1004) stayed the standby face; no laid-out surface appeared.

So `method return` on `set_power_on_status` did not drive the app off its standby presentation in
this run, and the injection had no laid-out Battery/Range widgets to act on. The byte-size lesson
is recorded in `01-battery-range-data-path.md` §3: the standby face is **131,845 bytes** here
(not 120,5xx), so size alone does not identify state — only image content does
(KIA logo + no widgets = standby; Battery/Range with `---` = laid out).
