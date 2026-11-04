# Engineering-mode data services

How the black engineering-mode page body was fixed, which D-Bus calls had to be
answered, and what the window renders now.

## The problem

AppEngineerMode launched and drew its title bar, but the page body stayed black.
Twenty seconds after start it issues a burst of D-Bus queries and, because
nothing owned the other ends, every async reply came back empty. Its DLT log said:

```
SysInfoEng::ResponseAskSysVersionEng        AskVer Pending Err
SysInfoEng::ResponseWipidInfo               wipid Pending Err
SysInfoEng::ResponseTracedateInfo           trace-date Pending Err
SystemProxyMethodEng::resRecvMicomPartInfo  Part Info Pending Err
EngAutoTestRefactor::resRecvUserModeInfo    User Mode Info Pending Err
AppEngineerModeEngine::Response_VH_VRVersion  retVal Error! - VR Version
```

## What the queries actually call

Recovered from the AppEngineerMode binary itself: its Qt D-Bus proxy vtables
(`strings | grep 'method name='`) and, for the VR version, by disassembling the
call site that constructs the proxy (the interface string
`com.lge.avn.appvh.atversionvrreq` is loaded at `0x952b9a` and the constructor
at `0x780b73` is fed `service = "com.lge.hkmc.avn.AppVR"` and
`path = "/com/lge/hkmc/avn/AppVR"` on the **session** bus).

| DLT message | bus | service | path | interface | method | reply |
| --- | --- | --- | --- | --- | --- | --- |
| `AskVer Pending Err` | system | `com.lge.car.micom` | `/Ihu` | `com.lge.car.micom.ihu` | `AskSysVersion` | `ay` |
| `wipid Pending Err` | system | `com.lge.car.micom` | `/Can` | `com.lge.car.micom.can` | `AskAutotestWIPID` | `ay` |
| `trace-date Pending Err` | system | `com.lge.car.micom` | `/Ihu` | `com.lge.car.micom.ihu` | `AskTraceDate` | `ay` |
| `Part Info Pending Err` | system | `com.lge.car.micom` | `/Ihu` | `com.lge.car.micom.ihu` | `AskPartNumberInfo` | `ay` |
| `User Mode Info Pending Err` | system | `com.lge.car.micom` | `/Ihu` | `com.lge.car.micom.ihu` | `AskFactoryModeInfo` | `ay` |
| `retVal Error! - VR Version` | session | `com.lge.hkmc.avn.AppVR` | `/com/lge/hkmc/avn/AppVR` | `com.lge.avn.appvh.atversionvrreq` | `AtVersionVrReq` / `AtVersionVrReqAll` | `s` |

The first five are all on `com.lge.car.micom`, which the launcher also depends on
for `AskSysBootinfo`. So the adaptor is a superset of the proven
`tools/uk_fw/guest/micom_dbus_sim.c`: it keeps the boot-info and transport-ack
answers and adds the six engineering-mode asks. The VR version is a separate
name on the session bus (AppVH's name; AppVH is not started by this chain).

## The adaptor

- `tools/uk_fw/guest/eng_data_sim.c` — single fail-closed simulator. Owns
  `com.lge.car.micom` on the system bus (`/Ihu`, `/Can`, `/Eng`,
  `/com/lge/car/micom`) and `com.lge.hkmc.avn.AppVR` on the session bus
  (`/com/lge/hkmc/avn/AppVR`). Logs every call and every answer to stdout.
- `tools/uk_fw/guest/build-eng-data-sim.sh` — cross-builds with zig against the
  guest's own `libdbus-1.so.3` (extracted from the EU 260128 rootfs).
- `tools/uk_fw/guest/run-engdata-chain.sh` — the launcher/weston chain, with
  `/eng-data-sim` as the single `com.lge.car.micom` owner.
- `tools/uk_fw/guest/run-engdata.sh` — launches AppEngineerMode (appId 301,
  retried every 12 s), waits, places the rendered surface, and captures.
- `tools/uk_fw/guest/run-engdata-host.py` — `vb.run` harness entry point; the
  screenshot base64 streams over `/dev/ttyS2` (`-chardev file` on
  `isa-serial,index=2`) to `/tmp/engdata-shot.b64`.

### Invented reply values

The UI only needs a well-formed, non-empty reply to stop being black, and every
field here is an ASCII identifier the QML renders verbatim. None is authentic
firmware data; they are self-consistent with the EU 260128 build under test:

| value | reply | notes |
| --- | --- | --- |
| `NE_E.EUR.S5W_L.001.001.260128` | System SW version | matches the build under test |
| `WIPID-5AE0001234` | Wi-PID | invented |
| `2026.01.28` | manufacturing/trace date | invented |
| `96560-GI000` | part number | invented, plausible Hyundai AVN part number |
| `01 00 00 00 00 00 00 00` | user mode | byte 0 = `1` => QML shows "Customer" |
| `VR_SW_6.1.0.0` | VR version | invented |

The 35-byte `AskSysBootinfo` payload is **not** invented: it is the v2 NE/EUR
profile already recovered and used by `micom_service.c`.

## Verified result

The same run's DLT log shows the six handlers no longer report an error:

```
SysInfoEng::ResponseWipidInfo            mWipid_info -> "WIPID-5AE0001234"
SystemProxyMethodEng::resRecvMicomPartInfo  Receive Part Info size : 11
EngAutoTestRefactor::resRecvUserModeInfo  Receive User Mode size : 8 | mode : 1
```

and the adaptor log shows `AskSysVersion`, `AskTraceDate`, `AskAutotestWIPID`,
`AskPartNumberInfo`, `AskFactoryModeInfo`, `AtVersionVrReq`/`AtVersionVrReqAll`
all answered. The "Pending Err" lines are gone.

### The window now renders

`docs/vm/29-engineering-mode-rendered-2026-11-04.png` (1920x720 PNG, 14 908
bytes). Measured on the decoded pixels:

- white: **94.90 %** (the body is drawn, not black)
- black: **0.0071 %** (98 px) — previously 100 % (the §4.9.0 image was a
  4 117-byte all-black frame)
- blue title band across the top and a 1 px blue left border
- a handful of small text glyph clusters in the body (the PIN keypad's labels)

The three AppEngineerMode surfaces are `1004` (front window), `1005` (rear
window) and `1006` (the content surface). Surfaces `1004`/`1005` are still pure
black — `docs/vm/29b-engineering-mode-window-surface-black-2026-11-04.png`
(4 117 bytes) — but **surface 1006 is the one that draws**, and it is the newest
`Surface id(N)` in weston.log, exactly as the runbook says. Placing 1006 with
`ivi-wm` and capturing with `weston-screenshooter` yields the rendered screen.

### What is on the screen, and what is not

The window renders the **PIN entry screen** (`AppEngineerMode_PinCodeKeypad.qml`;
the DLT shows `PinCodeKeypad.qml] Component.onCompleted` and `wrongCnt : 0`).
So the body is now live, but the **engineering menu list is not visible** — it is
behind the PIN gate, which was not entered.

Two things remain unresolved and are independent of the data adaptors:

1. **The keypad button images do not load** in this projection, so the number
   keys render as blank areas on white (only the labels show). This is the same
   image-loading gap already recorded for the home screen, not a data-service
   failure.
2. **The menu list** (`Force Update`, `Encryption Update`, `Scheduled Update
   List`, …) is reachable only after the PIN is accepted. No touch/keyboard
   entry of the PIN was attempted in this task.

### Still unanswered (non-blocking)

The eng app also asks `AskTuningVersion`, `AskETCEcallStatus`, `AskSysUpmID`,
`AskExternalSPDIFAMPVersion` and the GPS `GetMountAngleFileInfo`; those still
return `Pending Err`. They populate the *Software → Head Unit* version list and
do not gate the entry screen.

## Correction (2026-11-04, after the fix was measured)

The adaptor work in this document is real: with the simulator running, the DLT `Pending Err` count drops to **zero**, so all six queries are
answered.

**It did not fix the black page body.** The engineering window (the first surface created after the launch, e.g. `1004`) still captures at
**4,117 bytes** - an `Engineering Mode` title bar over a black body - and injecting clicks gives
`VM_INPUT_FOCUS_BEFORE_MOVE pid=NO_CLIENT`, i.e. no client view under the pointer at all.

The screenshots originally referenced here as the rendered engineering screen are the **home screen's EV page** (surface `2080`, Battery and
Range widgets). See `docs/vm/SCREENSHOT-LABELS.md`.

What the app's own `qmlLog` shows is that the QML loads and lays out correctly:

```
"[main.qml]:  main.qml : Component.onCompleted"
"[main.qml]: screen_Transition() : screenNext = QQmlComponent(0xb1c6e762a0)"
"idAppRoot.onWidthChanged : idAppRoot.width 1920"
"idAppRoot.onWidthChanged : idAppRoot.height 720"
"AppMain.qml : Component.onCompleted"
"[main.qml]: loader_1.onLoaded"
```

So the blank body is a **paint/surface-lifecycle** problem, not a data problem. That is the next investigation.
