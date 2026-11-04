# Authentic HMI apps: the MICOM stand-in opens the gate, but the home screen never presents a frame

This records the projection-only work in `work/vm/stockui` (a CoW clone of `work/vm/stockhmi`; the other
workspaces are untouched) to get the vendor HMI application stack running on the **authentic** boot path —
vendor kernel → `/init-authentic-hmi.sh` → authentic `/lib/systemd/esinit` → esinit's own `/usr/bin/weston --tty=1`.

**Result, in one line:** the `com.lge.car.micom` stand-in route works — `dbus-com.lge.car.micom.service` reaches
`active`, `ApplicationLauncher` starts and brings up `ApplicationManager` **and** `AppHomeScreen` under systemd, and
a click is delivered to a real compositor client — but **AppHomeScreen creates its ivi surface (id 2080) and never
attaches a buffer**, so the captured frame is still the 129,844-byte early-background and the click lands on that
background (pid 769), not on the home screen.

---

## 1. The projection-only unit override

`/etc/systemd/system/dbus-com.lge.car.micom.service` (the `/lib/systemd/system/` vendor unit is untouched and is
shadowed by this override):

```ini
# PROJECTION-ONLY override of dbus-com.lge.car.micom.service.
# Satisfies the bus name com.lge.car.micom with the /eng-data-sim stand-in
# (tools/uk_fw/guest/eng_data_sim.c) instead of the vendor
# /app/bin/micommanager_userspace, which exits 1 because no live MICOM is
# reachable over the platform SPI bus in QEMU.  ApplicationLauncher.service
# Requires this unit, so the stand-in is what lets the launcher/HMI start.
# The ExecStart wraps the stand-in in sh so its stdout/stderr land in a file
# (systemd 225 predates StandardOutput=file:/append:).  NOT part of the shipped
# system.
[Unit]
Description=System service for micommanager (projection stand-in)
Requires=dbus.service dlt.service
After=dbus.service dlt.service

[Service]
Type=dbus
BusName=com.lge.car.micom
ExecStart=/bin/sh -c 'exec /eng-data-sim >> /tmp/eng-data-sim.log 2>&1'
```

`/eng-data-sim` is the existing `tools/uk_fw/guest/eng_data_sim.c` stand-in (rebuilt with
`build-eng-data-sim.sh`), which owns `com.lge.car.micom` on the system bus. Because it acquires `BusName`, systemd's
`Type=dbus` activation completes and `ApplicationLauncher.service`'s `Requires=dbus-com.lge.car.micom.service` is
satisfied. Measured:

```
[apps-check] MICOM_IS_ACTIVE=[active]
[apps-check] MICOM_SHOW=[Result=success;ExecMainStatus=0;ActiveState=active;SubState=running;]
[apps-check] MICOM_FAILURE_LINE=[● dbus-com.lge.car.micom.service ... Active: active (running) ... Main PID: 1729 (eng-data-sim); CGroup: /system.slice/dbus-com.lge.car.micom.service; └─1729 /eng-data-sim;]
```

The vendor failure (`Failed to start System service for micommanager.`) is gone.

## 2. What else had to be provided (the `ENG_DATA_SIM_UNKNOWN` work list)

`ApplicationLauncher`'s own startup asks were already answered by `eng_data_sim.c` (`AskSysBootinfo` with the
35-byte v2 NE/EUR profile, `AskNaviOutermostRegion`, `AskSettingInfoValue`, `AskCustomSetting`,
`AskAMPSupportInfo`, the transport acks). Two more had to be added, and the reply types were recovered from the
vendor's own introspection XML inside `/app/bin/micommanager_userspace`:

| new call (verbatim from the log) | interface | reply |
| --- | --- | --- |
| `ENG_DATA_SIM_CALL ... member=AskAudioLastMemory signature=` | `com.lge.car.micom.audio` `/com/lge/car/micom` | `ay`, 8 zero bytes (polled ~5x by `ApplicationManager` until answered) |
| `ENG_DATA_SIM_CALL ... member=AskAMPSupportInfo` / `AskAudioMuteInfo` | audio | `ay`, 4/8 bytes (the audio-mute ask was also added) |

Plus `ApplicationManager`'s state-machine asks, already present in the shared source (commit `2a55e11`):
`AskEtcAdmSettingValue` (ADM-off), `AskDebuggingMode` (debug count), `AskLCDSetInfoValue`, `AskSysUpmID`, etc.
After the additions the manager's `reply is not VALID` for the MICOM gate is gone (consistent with CHANGELOG
§4.61.0).

A software-GL stack also had to be completed before `AppHomeScreen` stopped crashing on every launch (it is a heavy
Qt Quick app that needs an EGL context). The injected `/opt/software-egl18` set from the stockhmi workspace was
missing four dependencies of `swrast_dri.so` / `libLLVM-6.0.so.1`; these were added to `/opt/software-egl18/lib`:
`libsensors.so.4`, `libedit.so.2`, `libbsd.so.0` (from `work/software-egl/extracted/…`), and a
`libstdc++.so.6.0.22` (the guest's 6.0.21 lacks `GLIBCXX_3.4.22` required by `libLLVM-6.0.so.1`). After that
`ldd /opt/software-egl18/dri/swrast_dri.so` reports no unresolved library, and `AppHomeScreen` stays alive.

`/app/bin/AppLauncher.sh` was replaced with a projection-only version (the authentic script is preserved as
`/app/bin/AppLauncher.sh.vendor`) that adds the software-GL environment (`GALLIUM_DRIVER=softpipe`,
`LIBGL_ALWAYS_SOFTWARE=1`, `LIBGL_DRIVERS_PATH=/opt/software-egl18/dri`, `LD_LIBRARY_PATH` prepended with
`/opt/software-egl18/lib`) and the proven Qt stability flags (`QSG_RENDER_LOOP=basic`,
`QT_WAYLAND_DISABLE_WINDOWDECORATION=1`), and appends the launcher's stdio to `/tmp/applauncher-stdio.log`.

Two runtime resource links the shipped rootfs lacks were recreated in `/init-authentic-hmi.sh` before `exec esinit`:
`/app/share/AppHomeScreen/qml -> qml_new2.0` and a bind mount of `/system/new_gui/new2.0/hmc/night` over
`/app/share/images/hmc` (verified: `QML_SYMLINK=[… qml -> qml_new2.0]`, `IMAGES_HMC_COUNT=[28]`).

The `/etc/xdg/weston/weston_1920.ini` gains `modules=/weston-vm-input.so` so the compositor accepts the synthetic
click, and `/weston-vm-input.so` was rebuilt from the current `tools/uk_fw/guest/weston_vm_input.c` (the shipped
`.so` predates the `VM_INPUT_FOCUS_*` focus trace). All are labelled projection-only.

## 3. What starts

In `work/vm/stockui/runs/1793805121692994000` / `…1793805905108459000` (`--init /init-authentic-hmi.sh`):

```
[apps-check] APPLAUNCHER_PID=[2129] at +45s after socket
[apps-check] PIDS_FINAL AppLauncher=[2135] AppHomeScreen=[2755] ApplicationManager=[2207]
```

and from the launcher's own log (captured to `/tmp/applauncher-stdio.log`):

```
"[REGISTERED] registeredFromNativeApp AppId[11][AppHomeScreen] onDemand[0] groupNum[2]"
"ClearTimeoutLoading : 11, PID : 2755"
"======================================== [Group 2] Launch complete"
```

So `AppLauncher`, `ApplicationManager` and `AppHomeScreen` all come up under systemd. (Success criteria 1 and 2.)

## 4. The capture and the surface

`AppHomeScreen` creates a real ivi surface, but it is empty:

```
[apps-check] SURFACE_IDS=[... Surface id(30000), Weston surface W(1920), H(720); ... Surface id(2080), Weston surface W(1926), H(753);]
[apps-check] HOME_SURFACE_ID=2080
[apps-check] PLACING_HOME=2080 rc_out=[ivi_wm: connecting ... bound ivi_window_manager ...]
[apps-check] CAPTURE_home bytes=129844 magic=89504e470d0a1a0a sample_nonzero=70/512
```

The capture is **129,844 bytes, PNG** (`89 50 4e 47 …`) — byte-for-byte the early-background splash, **not** the home
screen. Surface 2080 (1926×753) is created and `ivi-wm 2080` round-trips, but the home screen never attaches a
buffer to it, so nothing new is composited. This is the same paint/surface-lifecycle gap recorded for the
engineering app in `docs/engineering-mode/engineering-data-services.md` ("Correction") and CHANGELOG §4.47.0:
the app waits to be shown.

## 5. The touch result

With the rebuilt `weston-vm-input.so`, a click at (960,400) reaches a **real client pid** — but that client is the
early-background, not `AppHomeScreen`:

```
[apps-check] VM_INPUT_LOG=[VM_INPUT_READY;VM_INPUT_CLICK_ACCEPTED;
            VM_INPUT_FOCUS_BEFORE_MOVE pid=769 uid=0;
            VM_INPUT_FOCUS_AFTER_MOVE pid=769 uid=0;
            VM_INPUT_CLICK_DONE;]
[apps-check] APPHOME_TOUCH_LOG=[]
```

`pid=769` is the early-background client (surface 30000). `AppHomeScreen` is pid 2755, and its own Qt log records
**no** `QWaylandInputDevice::Touch::touch_down`. The click is delivered (not `NO_CLIENT`/`NO_VIEW`), but it lands on
the background because the home surface has no content to take focus. Criterion 4's "real pid" half is met; the
"touch_down in the app's own log" half is not, for the same reason as criterion 3.

## 6. The remaining gap, named

`ApplicationManager` runs, but the home screen is never shown. The DLT log (`/log_data/dltlog/*.dlt`) shows the
home screen's own models loading and then stalling on the manager handshake:

```
[2] [ void AppStatusbarModel::updateVisibleChanged(int, bool) ][ 1981 ] FRONT  true
[2] [ BigInfoErrorCodeController::askMicomBigInfoFaultCode(int)::<lambda(QDBusPendingCallWatcher*)> ][ 305 ] reply.isValid():  false
```

The first line is the home screen laying out; the second is one more unanswered MICOM ask (`askMicomBigInfoFaultCode`
→ the micom method behind it is still `ENG_DATA_SIM_UNKNOWN`). The decisive gap, though, is the **show handshake**:
`AppHomeScreen` registers (`registeredFromNativeApp`) and creates surface 2080, but never commits a frame because
`ApplicationManager` never sends the show call — the same two named blockers already recorded on the engineering
thread in CHANGELOG §4.61.0 (the manager does not register `com.lge.avn.appmanager.appbase`, so the show trigger is
unreachable, and the watchdog reaps apps that never answer the app-alive handshake).

One more benign-but-real item for the work list: the app also introspects the stand-in and gets an error back:

```
ENG_DATA_SIM_CALL bus=system sender=:1.16 path=/Ihu interface=org.freedesktop.DBus.Properties member=GetAll signature=s
ENG_DATA_SIM_UNKNOWN path=/Ihu interface=org.freedesktop.DBus.Properties member=GetAll signature=s
```

`GetAll` on `org.freedesktop.DBus.Properties` is answered as `UNKNOWN_METHOD` rather than an empty property dict; it
did not block the app stack (AppHomeScreen still launched), but it is on the list. **Resolved in §7a.**

---

## 7. Follow-up: `Properties.GetAll` answered, and the "unreachable trigger" claim was a misdiagnosis

Three follow-up runs in the same clone (`…1793807664591927000`, `…1793808390896928000`,
`…1793809092146051000`).

### 7a. `Properties.GetAll` now returns an empty property map

The stand-in now answers `org.freedesktop.DBus.Properties.GetAll` (and `Get`) instead of `UNKNOWN_METHOD`:

```
ENG_DATA_SIM_ANSWER Properties.GetAll -> {} (empty a{sv})
```

So introspecting the stand-in is no longer a wrong reply on the work list.

### 7b. The manager registers its name and the `registration` interface; `appbase` is the app's interface

`ApplicationManager` owns `com.lge.hyundai.avn.appmanager` **on the session bus**, and it is absent on the system bus:

```
INTRO_SYSTEM_APPMGR_ROOT=[Error org.freedesktop.DBus.Error.ServiceUnknown:
    The name com.lge.hyundai.avn.appmanager was not provided by any .service files]
```

Its object tree at `/` (session bus) is:

```
<node name="FactoryFanControl"/> <node name="Information"/> <node name="audiotransition"/>
<node name="broadcast"/> <node name="registration"/> <node name="transition"/>
```

`/registration` exports `com.lge.avn.appmanager.registration` (methods `registration`, `deregistration`). There is **no
appbase object** — `/appbase` answers `Error org.freedesktop.DBus.Error.UnknownObject: No such object path '/appbase'`.

But appbase is **not a manager interface**: the manager is the appbase *client*. Its own log shows it speaking the
app-side contract to `AppHomeScreen`'s path `/com/lge/hkmc/avn/appfunc/appInterface`:

```
interface="com.lge.avn.appmanager.appbase", member="registerfaceplatekey", signature="", contents=({318, 322})
member="registertouchkey", ... contents=({30, 43, 44, 58, 5123, 5130, ...})
```

So the earlier claim (CHANGELOG §4.61.0) that "the manager does not register `com.lge.avn.appmanager.appbase`, so the
show trigger is unreachable" is **a misdiagnosis of where appbase lives**. The manager registers what it should (bus
name + `registration` + `broadcast`/`info`), and appbase is the app's side of the contract. The show trigger is on the
app, not on the manager.

### 7c. The real blocker: AppHomeScreen's event loop is starved, and the manager reaps it

`AppHomeScreen`'s main thread is in state **R (running)** with `wchan=0` — it is not waiting in the Qt event loop
(which would be `poll_schedule_timeout`), while ten worker threads sleep (`pipe_wait`, `futex_wait_queue_me`,
`poll_schedule_timeout` ×8):

```
[apps-check] APPHOME_WCHAN=[0]
[apps-check] APPHOME_STATUS=[State:  R (running);Threads:  11; ...]
[apps-check] APPHOME_TASK_STATES=[      1 R;     10 S;]
[apps-check] APPHOME_WCHAN_TASKS=[0, pipe_wait, futex_wait_queue_me, poll_schedule_timeout, ...]
```

That is why `AppHomeScreen` does not answer introspection:

```
INTRO_SESSION_HOME_com_lge_hkmc_avn_appfunc_appInterface=[Error org.freedesktop.DBus.Error.NoReply: Did not receive a reply...]
INTRO_SESSION_HOME_com_lge_hkmc_avn_appfunc_AppHomeScreen=[Error ... NoReply: Message did not receive a reply (timeout by message bus)]
```

and why it never presents a frame (the starved main thread never runs the commit) and never answers the app-alive
handshake — so the manager kills and deregisters it:

```
APPM_LWP[2257]: XXXXXXXXXX Registration::deregistration() a_nSigNum[9] a_strName[AppHomeScreen] XXXXXXXXXX
```

(`a_nSigNum[9]` = SIGKILL.) No `show_window_fg` appears anywhere in the DLT log, so the manager never reaches the
show call — because the app never becomes ready for it.

This is the same one-cause-behind-both-black-windows: the app's QML main thread spins/stalls under the software-GL +
QV4-interpreter projection, starves its event loop, never renders, and is reaped. `show_window_fg` delivery was not
attempted: the app's appbase is registered but unresponsive (`NoReply`), and §4.48.0 already recorded that this exact
call at this exact path destroys the peer (V-045).

## Repro

```sh
# already injected into work/vm/stockui:
#   sh work/vm/stockui/inject-stockui.sh        (debugfs writes + sync-partition.py)
python3.13 tools/uk_fw/vm_partimg/run-stockui.py --init /init-authentic-hmi.sh --timeout 560
```

Evidence directories: `work/vm/stockui/runs/1793805121692994000/` (surface 2080, capture, no focus trace — old
`.so`), `work/vm/stockui/runs/1793805905108459000/` (rebuilt `.so` — `VM_INPUT_FOCUS_* pid=769`, no
`touch_down`), and the follow-up runs `…1793807664591927000` / `…1793808390896928000` / `…1793809092146051000`
(manager introspection, `Properties.GetAll`, and the starved-main-thread evidence in §7).
