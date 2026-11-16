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

## 7g. The audit-volume hypothesis is out — by rate, not just by experiment

The authentic path audits every log-object access by `dlt-daemon`: **600 audit records in a ~615 s boot, of which 599
are SMACK** (334 on `Log::dlt_vcrm`, 265 on `Log::dlt`), all `comm="dlt-daemon"`, all granted. That is **~1 record per
second** — negligible, and it cannot starve a Qt event loop. (Note the trailing `audit(615.831:21528)`: `21528` is the
kernel audit **serial number**, not a count; `grep -c` gives 600.) So the audit volume is already eliminated by
arithmetic, ahead of any experiment.

For completeness the experiment agrees: with `-smp 4 --audit-off` (`…1793817865938068000`) the audit subsystem is gone
from the boot — **zero** `audit: type=1400` records — yet the frame is unchanged:

```
boot: audit: type=1400 count = 0        (was 600)
[apps-check] CAPTURE_final bytes=129844 magic=89504e470d0a1a0a      <- still the early-background, not painted
[apps-check] PIDS_FINAL AppLauncher=[2144] AppHomeScreen=[2633] ApplicationManager=[2202]
```

So audit is out on both grounds. Remaining candidates: **CPU contention** and **the launcher/manager path** (the show
handshake). The by-hand launch A/B separates them: run `/app/bin/AppHomeScreen` by hand on the authentic path with the
same environment and socket; if it then paints, the difference is in the launcher/manager path (or the reap), not in the
app or in system overhead.

(`--audit-off` and `--smp` are runner overrides in `tools/uk_fw/vm_partimg/run-stockui.py`.)

## 7h. The by-hand A/B: a relaunched app registers, introspects, and intermittently paints — the boot-time launch does not

The by-hand A/B (kill the launcher-started `AppHomeScreen`, relaunch `/app/bin/AppHomeScreen` with the environment
captured from `/proc/<pid>/environ`) was run five times (`…1793818763548084000`, `…1793819454386039000`,
`…1793820173885782000`, `…1793820881107851000`, `…1793821607874858000`). The relaunched instance behaves differently
from the boot-time one:

```
BASELINE_LISTNAMES=[com.lge.hyundai.avn.appmanager]                 <- no AppHomeScreen, as before
BASELINE_INTRO=[Error … ServiceUnknown: … AppHomeScreen was not provided …]   <- boot-time app never registered

BYHAND_NAME_OWNED=[com.lge.hkmc.avn.appfunc.AppHomeScreen]           <- registered (5/5 runs)
BYHAND_INTRO=[method return … Introspectable …]                      <- answers introspection (4/5 runs)
BYHAND_CAPTURE bytes=120562 / 120556                                 <- frame changed from 129844 (2/5 runs)
BYHAND_CAPTURE bytes=129844                                          <- unchanged (3/5 runs)
BYHAND_LOG_TAIL=[… ClimateWidget … CPCallWidget … VoiceMemoWidget … setAutoLight …]  <- QML actively rendering
```

So a *relaunched* `AppHomeScreen` registers its bus name and answers introspection — which the boot-time instance
never does (`ServiceUnknown`) — and in two of five runs the capture changes to ~120,5xx bytes, i.e. a surface got a
buffer and painted, while the app's QML was concurrently updating widgets. (The painted frames could not be decoded
on the host: the base64 stream over the serial console is corrupted by interleaved kernel output; the clean decodes
were the 129,844-byte early-background. The byte-count change is the paint signal.)

Two honest caveats. First, the paint is **intermittent** (~2/5), so the relaunch is still marginal — residual
contention or a race — not a clean fix. Second, in several runs the by-hand process itself was reaped
(`BYHAND_ALIVE=[no]`) and the name was then owned by the launcher's own restarted instance, which is the one that
introspected and painted; the manager/launcher SIGKILLs a foreign `AppHomeScreen` (§7c's `a_nSigNum[9]`).

**Conclusion: the app is not intrinsically broken in this projection.** A (re)launch — by hand or by the launcher's
own restart — can register, introspect, and intermittently paint, while the boot-time launch never does. That points
the remaining cause at the boot-time launch path (the launcher/manager's boot-time state, or the residual contention
around the first launch), not at the app, the bus, SMACK, audit, or DLT.

---

## 8. Root cause found: AppHomeScreen never initialises EGL — and the launcher-level drop-in is insufficient

The app's own stderr (head of the by-hand log, `…1793824685011102000`) shows the real failure and confirms the
diagnosis:

```
[01-01-70 00:02:04:737][FTL]  Using Wayland-EGL
libEGL warning: DRI2: failed to open swrast (search paths /usr/lib/dri)
[01-01-70 00:02:04:825][FTL]  [QtMsg] failed to initialize EGL display
```

`AppHomeScreen` never initialises EGL, so it never reaches the commit-a-frame code; the `NoReply`, no-surface,
no-frame, `ServiceUnknown` symptoms are all downstream of this. The eliminated hypotheses (SMACK policy loading, audit
volume, DLT load, the session-bus environment/file, and thread state) were correctly eliminated and were downstream
noise from a Qt app with no renderer.

The proposed drop-in was tried and is **insufficient on its own**. The launcher (`AppLauncher 3`) receives the full
software-GL environment — the drop-in plus `AppLauncher.sh` both set it:

```
LAUNCHER_ENVIRON_GL=[LD_PRELOAD=/usr/lib/libEGL.so.1; LP_NUM_THREADS=1; LIBGL_DRIVERS_PATH=/opt/software-egl18/dri;
                     LD_LIBRARY_PATH=/opt/software-egl18/lib:…; GALLIUM_DRIVER=softpipe; LIBGL_ALWAYS_SOFTWARE=1]
```

but its child does not. `AppHomeScreen`'s environ keeps `GALLIUM_DRIVER`, `LD_LIBRARY_PATH` and `LD_PRELOAD`, yet
drops `LIBGL_DRIVERS_PATH` / `LIBGL_ALWAYS_SOFTWARE` / `LP_NUM_THREADS` (the vendor launcher filters the child
environment):

```
APPHOME_ENVIRON=[DBUS_SESSION_BUS_ADDRESS=…; QT_QPA_PLATFORM=wayland; LD_PRELOAD=/usr/lib/libEGL.so.1;
                 GALLIUM_DRIVER=softpipe; XDG_RUNTIME_DIR=…; WAYLAND_DISPLAY=wayland-0;
                 LD_LIBRARY_PATH=/usr/lib/media-libva/:/opt/software-egl18/lib:…]
```

So the child loads the preloaded vendor `libEGL`, has no `LIBGL_DRIVERS_PATH`, searches `/usr/lib/dri`, and fails —
exactly the warning above. The library-path fix has to reach the *child* (or provide a Mesa-ABI-compatible `libEGL`),
which the launcher-level drop-in does not do.

**Next (unresolved):** get the Mesa-ABI-compatible GL stack (libEGL + swrast + its LLVM/glapi deps) into the child
process, or make the vendor libEGL load a working swrast from its default `/usr/lib/dri` — the vendor libEGL is ABI-
incompatible with the injected Mesa-18 swrast (tested: copying swrast into `/usr/lib/dri` does not change the warning).

## 9. The EGL root cause is closed: the swrast was unreachable, not the preload

The cause is confirmed and §8's “preload” framing is corrected. The child's log with the software-GL driver path
restored is clean:

```
[FTL]  Using Wayland-EGL          <- no “libEGL warning: DRI2: failed to open swrast” any more
```

and the by-hand app then registers, answers introspection, and paints (`…1793829575437696000`):

```
BYHAND_NAME_OWNED=[com.lge.hkmc.avn.appfunc.AppHomeScreen]
BYHAND_INTRO=[method return … Introspectable …]
BYHAND_CAPTURE1..3 bytes=120556   <- frame changed from the 129844 early-background (painted)
```

The cause was **not** the `LD_PRELOAD` line. The preloaded `libEGL.so.1.0.0` is the vendor's own Mesa build
(849,912 bytes — the same Mesa as the research chain), and it works once it can find a swrast. What was missing is
`LIBGL_DRIVERS_PATH` **in the child** — the vendor launcher strips `LIBGL_*` from its children (§8's launcher-vs-child
split) — so the libEGL searched only `/usr/lib/dri` and found the i965 stub. Restoring the swrast path
(`LIBGL_DRIVERS_PATH=/opt/software-egl18/dri`, run20, removes the warning) or placing `swrast_dri.so` in
`/usr/lib/dri` (run21) both clear the warning, and in run21 the app registers, introspects, and paints.

So the last substitution is the software-GL environment (one path), not the preload. The preload line remains a real
difference from the research chain but is not the cause; the same line that cost the earlier buffer-commit
investigation is, again, not the culprit here — the swrast search path is.

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
`…1793811409658169000` / `…1793812134562822000` (CPU-time delta and `poll_schedule_timeout` samples in §7d),
`…1793814291074215000` (env/bus differential and the early `ServiceUnknown` in §7e), `…1793817865938068000`
(`--audit-off`: zero audit records but still no paint, §7g), and the by-hand A/B runs `…1793818763548084000` /
`…1793819454386039000` / `…1793820173885782000` / `…1793820881107851000` / `…1793821607874858000` (§7h), and
`…1793824685011102000` (the app's EGL log and the launcher-vs-child environment split, §8),
`…1793826961162159000` (`LIBGL_DRIVERS_PATH` restores EGL with the preload kept, §9), and `…1793829575437696000`
(swrast in `/usr/lib/dri`: registers, introspects, paints 120,556 bytes, §9).
