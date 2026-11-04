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

### 7c. A raw state observation (State R / wchan=0) — recorded, and then shown not to discriminate

On the `-smp 2` authentic run the main thread was sampled in **R (running)** with `wchan=0`, ten worker threads
sleeping, and the same instance did not answer introspection and was later reaped:

```
[apps-check] APPHOME_WCHAN=[0]
[apps-check] APPHOME_STATUS=[State:  R (running);Threads:  11; ...]
[apps-check] APPHOME_TASK_STATES=[      1 R;     10 S;]
[apps-check] APPHOME_WCHAN_TASKS=[0, pipe_wait, futex_wait_queue_me, poll_schedule_timeout, ...]
INTRO_SESSION_HOME_com_lge_hkmc_avn_appfunc_appInterface=[Error org.freedesktop.DBus.Error.NoReply: Did not receive a reply...]
APPM_LWP[2257]: XXXXXXXXXX Registration::deregistration() a_nSigNum[9] a_strName[AppHomeScreen] XXXXXXXXXX
```

(`a_nSigNum[9]` = SIGKILL.) These are real and kept. **But the state is not the cause.** A control in
`work/vm/softbackend` loaded the shipped SMACK policy, ran the same chain23, placed 2080, and captured a **painted**
frame (17,874 bytes — in the known painted range 17,586 / 17,870 / 17,874) **while the main thread was in exactly the
same state**:

```
SMACK_RULES_LOADED=636
HOME_AT=60s home_pid=815
SHOT=17874                    <- painted
State:  R (running)           <- same state
Threads: 13
wchan: 0                      <- same wchan
audit_denied=0
```

So `State R` + `wchan=0` is the normal state of a *working* AppHomeScreen and does **not** discriminate paint from
no-paint. The earlier reading — “R/wchan=0, therefore it never enters its event loop, therefore it never renders” — is
withdrawn as a correlation, not a cause (and it repeated in CHANGELOG §4.78.0, so the correction is shared).

---

## 7d. What actually differs is still open, narrowed by two controls and one measurement

Three measured facts, in order:

1. **The identical binary paints under the research-init chain** — `docs/vm/25-home-screen-placed-clean-2026-11-04.png`
   (17,586 B) and `docs/vm/31-home-screen-STR_CAMERA_ALERT2-2026-11-04.png` (17,870 B, crisp title text), touch
   delivered (`evidence/vm-bringup/interactive-touch-2026-11-04.log`).
2. **It also paints with the SMACK policy loaded** (the §7c control: `SMACK_RULES_LOADED=636`, `audit_denied=0`,
   `SHOT=17874`) — so policy loading does not by itself break the paint.
3. **On the authentic path the app accrues real CPU during init, then idles** (`-smp 4`):

```
[apps-check] CPU_DELTA_30s utime=389 stime=236 total=625 ticks (clk=100, ~6s CPU over 30s wall)
            wchan_t0=[0] wchan_t30=[poll_schedule_timeout]        # …1793811409658169000
[apps-check] SAMPLE_+80s … +240s pid=[2634] state=[S] wchan=[poll_schedule_timeout]   # …1793812134562822000
[apps-check] APPHOME_STACK=[[poll_schedule_timeout] [do_select] [core_sys_select] [SyS_pselect6] [system_call_fastpath]]
[apps-check] CAPTURE_final bytes=129844 magic=89504e470d0a1a0a
```

The thread state does **not** discriminate (a working instance is R/wchan=0; the black instance reaches poll and idles),
so the paint difference is neither “the thread is starved” nor “it is parked in a DLT FIFO write”. What still differs
between the two configurations is: **systemd + the full vendor unit set competing for 2 vCPUs (contention), audit
logging + SMACK enforcement, `dlt-daemon` with the app's multi-MB DLT traffic, and the projection wrappers**
(`/init-authentic-hmi.sh`, the weston wrapper, the pixman shim). The SMACK control narrows that to **contention, DLT,
or one of the wrappers**.

Cheapest next discriminators, in order:
- **utime+stime delta on the authentic path** (done above): the app *does* accrue ~4–6 s CPU per 30 s during init and
  then drops to ~0.5 % after reaching the loop — so its own thread is neither a spin nor a permanent block; the no-paint
  is not CPU starvation of that thread. That is consistent with contention/DLT/wrapper delaying or withholding the show
  handshake rather than the app being unable to run.
- **Launch the app by hand** on the authentic path (`/app/bin/AppHomeScreen` with the environment the launcher gives
  it) instead of through `AppLauncher`. If it paints when launched by hand, the difference is in what the launcher does
  or in the manager's reaping, not in the app. (Not yet run.)

The `-smp 4` override in `tools/uk_fw/vm_partimg/run-stockui.py` is the only new projection-only change here.

## 7e. The readiness control, and the env/bus differential

A readiness control on the *working* (research) path: the app reaches surface 2080 at 55 s, answers D-Bus introspection
on the first probe, and paints:

```
SURFACE_2080_AT=55s
READY_AT=1s after first probe (attempt 1)     <- answers Introspect immediately
SHOT=17764                                   <- painted
```

So there is no slow-startup window to blame on the software-rendered QML: a working instance is introspectable and
painting essentially at once. That makes the authentic path's startup a symptom, not the app.

The env/bus hypothesis is now **disconfirmed** by measurement on the authentic path (`…1793814291074215000`, `-smp 4`).
The two files agree and the launcher and app both carry the same address:

```
SESSION_APPMGR_RAW=[unix:abstract=/tmp/dbus-gZBcGZyZFg,guid=58e62bc2…]
SESSION_APPMGR_ENV=[DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-gZBcGZyZFg,guid=58e62bc2…]
APPLAUNCHER_DBUS=[DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-gZBcGZyZFg,guid=58e62bc2…]
APPHOME_ENVIRON=[… DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-gZBcGZyZFg,guid=58e62bc2…
                 XDG_RUNTIME_DIR=/var/run/user/root WAYLAND_DISPLAY=wayland-0 QT_QPA_PLATFORM=wayland …]
```

So the app is **not** misdirected to a different bus. But the same early probe shows its well-known name is not yet
owned, and introspection answers `ServiceUnknown`:

```
LISTNAMES_HOME=[com.lge.hyundai.avn.appmanager]           <- the manager only, no AppHomeScreen
INTRO_HOME_NOW rc_dt=1s out=[Error … ServiceUnknown: The name com.lge.hkmc.avn.appfunc.AppHomeScreen was not provided by any .service files]
```

and that first instance is then reaped (`APPHOME_PID_CHANGED 2491 -> 2760 at +20s`) before it registers the name; the
restarted instance reaches `poll_schedule_timeout` as before. So the app is **slow to register its bus name on the
authentic path** (it stalls before name registration) even though its address is correct — matching plain CPU
contention (its init thread sits in `wait_on_page_bit`/`futex_wait_queue_me` rather than idle).

Remaining candidates, narrowed to three: **plain CPU contention** (the full vendor unit set on 2 vCPUs), **DLT load**
(the app's multi-MB DLT traffic), or **one of the projection wrappers** (`/init-authentic-hmi.sh`, the weston wrapper,
the pixman shim). SMACK policy loading and a wrong/missing session-bus address are both out.

The cleanest remaining A/B is the one still on the list: launch `/app/bin/AppHomeScreen` by hand on the authentic path
with the same environment and socket, bypassing `AppLauncher`; if it then registers its name and paints, the difference
is in the launcher/manager path or the reap, not in the app or its bus.

## 7f. The vendor's own `Dbuslaunch.sh` creates the env file — and on this chain it is correct

`/app/bin/Dbuslaunch.sh` (run by `Dbuslaunch.service`) is the thing that creates both files, and six units read the
second via `EnvironmentFile=/tmp/session_appmgr.env` (`ApplicationLauncher`, `CryptoService`, `MediaBrowser`,
`credman`, `mediamanager`, `mof`):

```sh
dbus-daemon --session --print-address --fork > $SESSION_BUS_FILE   # /tmp/session_appmgr
session_addr=`cat $SESSION_BUS_FILE`
echo "DBUS_SESSION_BUS_ADDRESS=$session_addr" > $SESSION_ENV_FILE  # /tmp/session_appmgr.env
```

The trap would be: a chain that starts its own session `dbus-daemon` and writes `/tmp/session_appmgr` by hand makes the
vendor's `dbus-daemon --session --fork` fail or produce a different address, leaving the `.env` file missing or pointing
at a bus nothing else is on. **This chain does not trip that trap.** The projection scripts only *read*
`/tmp/session_appmgr` (verified by grep — no `dbus-daemon` start and no `session_appmgr` write in `work/vm/stockui`'s
injected files). The vendor script runs normally and the three strings match exactly (`…1793814291074215000`):

```
boot:  [   14.402430] systemd[1]: Started HKMC Preminum AVN 2.1 -Launcher.   (Dbuslaunch.service)
       [   46.967505] systemd[1]: Started HKMC Preminum AVN 2.1 -Launcher.   (ApplicationLauncher.service)
       (no "Failed to load environment files" anywhere in the boot log)

SESSION_APPMGR_RAW=[unix:abstract=/tmp/dbus-gZBcGZyZFg,guid=58e62bc2…]
SESSION_APPMGR_ENV=[DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-gZBcGZyZFg,guid=58e62bc2…]
APPLAUNCHER_DBUS=[DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-gZBcGZyZFg,guid=58e62bc2…]
APPHOME_ENVIRON=[… DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-gZBcGZyZFg,guid=58e62bc2… …]
```

and the address resolves to a live daemon (`dbus-send --session … ListNames` returned a reply carrying the manager's
name). So the app's environment is correct and the missing-env-file hypothesis is out for this chain. It stays a real
trap for any chain that pre-empts `Dbuslaunch.service` (e.g. the research chain, which starts its own session bus), and
is worth keeping in the checklist.

## Repro

```sh
# already injected into work/vm/stockui:
#   sh work/vm/stockui/inject-stockui.sh        (debugfs writes + sync-partition.py)
python3.13 tools/uk_fw/vm_partimg/run-stockui.py --init /init-authentic-hmi.sh --timeout 560
```

Evidence directories: `work/vm/stockui/runs/1793805121692994000/` (surface 2080, capture, no focus trace — old
`.so`), `work/vm/stockui/runs/1793805905108459000/` (rebuilt `.so` — `VM_INPUT_FOCUS_* pid=769`, no
`touch_down`), the follow-up runs `…1793807664591927000` / `…1793808390896928000` / `…1793809092146051000`
(manager introspection, `Properties.GetAll`, and the State R/wchan=0 observation in §7c), the `-smp 4` runs
`…1793811409658169000` / `…1793812134562822000` (CPU-time delta and `poll_schedule_timeout` samples in §7d), and
`…1793814291074215000` (env/bus differential and the early `ServiceUnknown` in §7e).
