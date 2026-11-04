# ApplicationManager MICOM replies: what was answered, and the named blocker that remains

This is the follow-up to `engineering-data-services.md` and `engineering-paint.md`.
It records the second half of the paint problem: once the six engineering-mode data
asks are answered, `ApplicationManager` still will not show the engineering window,
because its *own* MICOM conversation came back `reply is not VALID`. This note records
which methods were added to the stand-in, with what reply types, which ones moved the
manager past `reply is not VALID`, and what the manager is still missing.

Work was done in a private CoW clone `work/vm/micomsim` (copied from
`work/vm/softbackend`; no shared work tree was touched). The stand-in is
`tools/uk_fw/guest/eng_data_sim.c`, rebuilt with `build-eng-data-sim.sh` and injected
into the clone's `rootfs.img` with `debugfs`, as `/eng-data-sim`. The run wrapper
`tools/uk_fw/guest/run-micomsim.sh` (injected as `/run-micomsim.sh`) and the host
runner `tools/uk_fw/guest/run-micomsim-host.py` boot the chain, launch engineering
mode (appId 301, retried every 12 s), and stream the capture over `/dev/ttyS2`.

## Reply types were recovered, not guessed

For every unanswered method the reply *type* was taken from the requesting binaries,
as the task required. The authoritative source is the real MICOM server's own D-Bus
introspection XML, which ships verbatim inside
`/app/bin/micommanager_userspace` (the process the stand-in replaces):

```
<method name="AskDebuggingMode">      <arg direction="out" type="ay"/>
<method name="AskEtcAdmSettingValue"> <arg direction="out" type="ay"/>
<method name="AskSysUpmID">           <arg direction="out" type="ay"/>
<method name="AskCameraSetting">      <arg direction="in" type="ay"/> <arg direction="out" type="ay"/>
<method name="AskCameraBrightness">   <arg direction="out" type="ay"/>
<method name="AskEtcLcdThemaInfo">    <arg direction="in" type="ay"/> <arg direction="out" type="ay"/>
<method name="AskLCDSetInfoValue">    <arg direction="out" type="ay"/>
<method name="AskETCEcallStatus">     <arg direction="out" type="ay"/>
```

`SetFCEVInitialRequest` is a void method (from AppHomeScreen's introspection,
`<method name="SetFCEVInitialRequest"/>`, exactly like its `SetDATCInitialRequest`
sibling). `AmebaEnable` is `out b` (from AppVH's introspection,
`<interface name="com.lge.avn.appvh.AmebaEnable"><method name="AmebaEnable"><arg direction="out" type="b" name="enable"/>`).

The two manager-critical reply *values* were confirmed by disassembling the manager's
reply-parsing slots in `ApplicationManager` (stripped, but the slot code is reachable
via the string xrefs):

- `AskDebugCntSlot` reads `argumentAt(0)` as a `QByteArray` (`userType 0xc`), checks
  `size >= 1`, and takes **byte[0] as the debug count**. `<= 0` skips the follow-up
  `SetSysDebuggingMode` call, so byte[0] = `0x00` is the normal "debug off" answer.
- `ADMOffSettingSlot` reads `argumentAt(0)` as a `QByteArray`, checks `size >= 1`,
  and takes **byte[0] as the ADM-off value**. Non-zero drives it toward
  "change power to Logic OFF", so byte[0] = `0x00` is the safe answer.

## What was added to `eng_data_sim.c`

| method | bus / path / iface | reply type | reply value |
| --- | --- | --- | --- |
| `AskDebuggingMode` | system `/Ihu` `com.lge.car.micom.ihu` | `ay` | `{ 0x00 }` (debug count 0) |
| `AskEtcAdmSettingValue` | system `/Ihu` `com.lge.car.micom.ihu` | `ay` | `{ 0x00 }` (ADM-off disabled) |
| `AskSysUpmID` | system `/Ihu` `com.lge.car.micom.ihu` | `ay` | `{ 0x00 }` |
| `AskCameraSetting` | system `/Ihu` (in `ay`) | `ay` | `{ 0,0,0,0 }` |
| `AskCameraBrightness` | system `/Ihu` | `ay` | `{ 0x50, 0x00 }` |
| `AskEtcLcdThemaInfo` | system `/Ihu` (in `ay`) | `ay` | `{ 0,0,0,0 }` |
| `SetFCEVInitialRequest` | system `/Can` | void | empty |
| `AmebaEnable` | session `/com/lge/hkmc/avn/AppVR` | `b` | `false` |
| `AskLCDSetInfoValue` | system `/Ihu` | `ay` | 8 zero bytes (manager `askLcdInfo`, added proactively) |
| `AskETCEcallStatus` | system `/Ihu` | `ay` | `{ 0x00 }` (appeared as a new UNKNOWN on iteration 2) |

## Which replies unblocked the manager

The two methods the manager's own log had named as `reply is not VALID` are now
answered, and the manager logs the *valid* path instead (from the run's manager log):

```
"APPM_LWP[1160]: MicomInterfaceM::ADMOffSettingSlot reply value [0]"
"APPM_LWP[1160]: EventFlow2 --> Information::send_adm_off_setting Status[0]"
"APPM_LWP[1160]: MicomInterfaceM::AskDebugCntSlot reply cnt [0]"
```

`reply is not VALID` is **zero** across the run, and the stand-in's own
`ENG_DATA_SIM_UNKNOWN` tally is empty after the second iteration. The manager then
reaches `welcomeReady`, `initWaylandConnection`, and starts its app-alive watchdog —
so the MICOM gate itself is open.

## Whether the window painted

**No.** `show_window_fg` is never delivered on `com.lge.avn.appmanager.appbase`, the
engineering surface never carries a buffer, and the app is killed ~30 s after it
registers. Three measured facts, each captured in the run:

1. The manager **pings** the app but never shows it. Session-bus monitor:

   ```
   method call sender=:1.3 -> dest=com.lge.hkmc.avn.appfunc.AppEngineerMode ... path=/com/lge/hkmc/avn/appfunc/engineermode; interface=org.freedesktop.DBus.Peer; member=Ping
   ```
   and there is **no** `show_window_fg` / `show_window` / `engineermode` method call
   anywhere in the session-bus log.

2. The manager's alive-check declares the app hung and deregisters it, ~30 s after
   registration:

   ```
   "APPM_LWP[1474]: XXXXXXXXXX Registration::deregistration() a_nSigNum[15] a_strName[AppEngineerMode] XXXXXXXXXX"
   "APPM_LWP[1474]: EventFlow --> Information::requestIDTCData AB010512*time*AppEngineerMode-5-hang"
   ```
   A 90 s liveness watch shows the app's PID present at +10 s and +20 s, then gone:
   `T+10s eng=1033 ... T+20s eng=1033 ... T+30s eng=  (empty)`.

3. The `show_engineermode` trigger cannot be delivered at all. The manager exports
   `show_engineermode` (no args) on `com.lge.avn.appmanager.appbase`, but that
   interface is **not registered** on the session bus in this projection —
   introspecting `com.lge.hyundai.avn.appmanager` shows only the nodes
   `FactoryFanControl, Information, audiotransition, broadcast, registration,
   transition`, no `appbase`, and delivering the trigger returns:

   ```
   Error org.freedesktop.DBus.Error.UnknownObject: No such object path '/appbase'
   Error org.freedesktop.DBus.Error.UnknownInterface: No such interface 'com.lge.avn.appmanager.appbase' at object path '/'
   ```

## The named blocker

The manager's MICOM gate is open (`reply is not VALID` is gone), but the window still
does not paint because **the manager never issues `show_window_fg` for the engineering
app**, for two compounding reasons that are now named precisely:

1. **The `show_engineermode` trigger is unreachable.** It lives on the manager's
   `com.lge.avn.appmanager.appbase` interface, which the manager does not register on
   the session bus in this projection (verified by introspection and by the
   `UnknownObject`/`UnknownInterface` errors on every candidate path). So there is no
   D-Bus way to ask the manager to show engineering mode.
2. **The manager's app-alive watchdog then kills the app.** Because the app is never
   shown, its liveness handshake with the manager (`set_application_alive_chcek` /
   `askAlive`, see `Application::slot_AppAliveResponse` / `slot_AppAliveTimeOut` in
   the manager's strings) is not satisfied, so the manager logs
   `AB010512*time*AppEngineerMode-5-hang`, runs `appTerminateSlot`, and deregisters
   `AppEngineerMode` (`a_nSigNum[15]`). The app is gone before it can be shown even
   by a later trigger.

This is not a missing MICOM reply any more. It is the next handshake up the stack:
the app-manager *show* path (`show_engineermode` → `show_window_fg`), which this
projection does not deliver, followed by the app-alive watchdog that removes the
unshown app.

## Capture

The engineering surface capture (newest post-launch `Surface id`, placed with
`ivi-wm`, `timeout 25 /usr/libexec/weston-screenshooter`) is **14 907 bytes**, magic
`89504e470d0a1a0a` (`\x89PNG` — this build's weston-screenshooter writes PNG, not
PPM). That size is the home screen showing through the empty engineering surface,
i.e. the engineering window is still transparent; it never attached a buffer. The
home control surface (2080) captured in a companion run is 17 869 bytes, matching
the known painted home-screen size from `engineering-paint.md`. The engineering
surfaces are `1004`/`1005`/`1006` across runs, all `W(1926), H(753)`, all transparent.

## Reproducibility

```
cp -cR work/vm/softbackend work/vm/micomsim
./tools/uk_fw/guest/build-eng-data-sim.sh
# debugfs: write tools/uk_fw/guest/eng-data-sim -> /eng-data-sim (mode 0755)
# debugfs: write tools/uk_fw/guest/run-micomsim.sh -> /run-micomsim.sh (mode 0755)
# refresh work/vm/micomsim/prepare.json rootfs.img sha256 after every injection
python3.13 tools/uk_fw/guest/run-micomsim-host.py
```
