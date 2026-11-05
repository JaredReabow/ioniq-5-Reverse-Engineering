# Stock gesture in the VM — the About-screen tap, tested on the authentic projection

Date: 2026-11-05. Workspace: `work/vm/gesture` (a CoW clone of `work/vm/stockui`; no other
workspace was touched). Runner: `tools/uk_fw/vm_partimg/run-gesture.py`
(copy of `run-stockui.py` with `WS` pointed at `work/vm/gesture`, a `ttyS2`
lossless PNG channel, and `--smp 4` as default). The guest script that performs the
captures and clicks is the injected `/weston-apps-check.sh` (staged at
`work/vm/gesture/inject-new/stage/weston-apps-check.sh`, written into `p5` of the GPT image by
`inject-stockui.sh`).

## Verdict (read this first)

**I did not reach an About/software-version screen, and the tap gesture could not be exercised in
the projection — for two independently measured reasons:**

1. **The Settings navigation affordance does not work in this projection.** The home screen paints
   (title bar, `STR_CAMERA_ALERT2`, KIA logo — 120,556–120,565-byte captures), but its bottom menu
   bar (the "All Menu" → Settings entry, code-derived centre `(771, 613)`) renders **black** (theme
   image assets are not loaded) and injected clicks **fall through to the compositor's own client**
   (`weston.real`, pid ~793–797), never to `AppHomeScreen`. So the UI cannot be driven by the
   synthetic touch path beyond "the input module accepts the click".
2. **Even a direct launch of the Settings app (`AppSetup`) does not present a frame.** Launching
   `AppSetup` over the session bus (`com.lge.avn.applauncher /Request …request.launch`, app ids 13 /
   50 / 56 / 58) starts the process (multiple `AppSetup` pids appear), but the capture stays the
   129,844-byte early background — `AppSetup` never attaches a buffer (the same "never shown"
   handshake gap this project has documented for the other apps). Its version screen is therefore
   unreachable in the projection.

An **exhaustive static sweep of the whole `/app/share` QML tree** (the user's sweep, re-run and
confirmed here) settles the gesture question without needing a reachable version screen. Every QML
file in the image with a tap/click counter:

- `/app/share/AppEngineerMode/qml/AutoTest/AppEngineerMode_GhostTouchTest.qml` — engineering mode's own touch-test screen
- `/app/share/AppEngineerMode/qml/AutoTest/AppEngineerMode_TouchTest.qml` — engineering mode's own touch-test screen
- `/app/share/AppHomeScreen/qml_new2.0/NMode/PerformanceTimer/Q_NMode_PT_Lap_Main_Track.qml` — the N-mode lap timer, whose five-tap counter (`_clickCount >= 5`) toggles `AppNModeModel.isNaviTestingMode`, a cosmetic flag (swaps a checkbox image and a translucent overlay)

**Three files, all accounted for — and none is near About, General, or a software-version string.**
The only thresholds in that enumeration are `5` (the lap timer) and `0` (an initialiser). `AppSetup`
(the Settings app, whose `qml_new2.0/general/Q_AppSettingSysInfoVersion.qml` is the "Version info"
screen `STR_SETUP_SYSINFO_VERSION_INFO`) contains **zero** tap/click counters — re-verified with a
`grep` over `app/share/AppSetup/qml_new2.0` that returns nothing for tap/click/press/counter patterns.

**Result: the About-screen tap gesture is not present in this build's QML.** It is not something a
better navigation path would have uncovered; the gesture was inherited from a sibling platform and
this build does not implement it in QML. The one observation static analysis cannot give — whether a
C++ handler hides behind the version string — **remains open here**, because this projection never
presents the version screen (the Settings affordance is dead and `AppSetup` does not paint), so there
is no capture of the version string reacting or not reacting. §3 records the full enumeration plus the
one nearby-but-different tap sequence in the telematics app.

---

## 1. Boot and capture method (unchanged from the session's measured path)

```
python3.13 tools/uk_fw/vm_partimg/run-gesture.py --init /init-authentic-hmi.sh --smp 4 --timeout 900
```

The authentic chain (vendor kernel → `/init-authentic-hmi.sh` → `esinit` → `weston --tty=1` →
systemd → `ApplicationLauncher` → `ApplicationManager` → `AppHomeScreen`) reaches Multi-User, and
the managed `AppHomeScreen` owns `com.lge.hkmc.avn.appfunc.AppHomeScreen`.

Captures are taken with the vendor screenshooter **after `cd /tmp`**, and streamed losslessly out
`/dev/ttyS2` (host `out.b64`) as base64. Two capture-size landmarks are used throughout:

| bytes | meaning |
| --- | --- |
| 129,844 | early background / splash |
| ~120,5xx | the painted `AppHomeScreen` (120,556 / 120,565 measured this session) |

### The surface-selection trap, confirmed again

The application's ivi surface id is **not stable across boots**, and the "newest surface" is the
background (created last). In this session the app's painted surface was **2080** in three runs
(120,556–120,565 bytes when placed) but **1005 / 1007** in another, and in two runs the only
"newest" 1926×753 surface was the splash. Every capture below was taken by placing the surface that
*painted* (~120,5xx), not the newest one.

---

## 2. What appeared at each step (click sequence and captures)

All times are guest-relative. `click X Y` writes to `/tmp/weston-vm-input`; the compositor
acknowledges with `VM_INPUT_CLICK_ACCEPTED` and a `VM_INPUT_FOCUS_BEFORE_MOVE pid=<n>` line in
`/tmp/weston-real.log`.

### Step 0 — home screen baseline (no click)

`ivi-wm 2080`, then screenshooter.

- capture **120,556** / **120,565** bytes → `docs/vm/34-gesture-home-screen-painted-2026-11-05.png`
  (and `33-…-home-screen-authentic-…`, 120,565).
- OCR: `STR_CAMERA_ALERT2` (the camera widget title), the KIA logo, the blue title bar. The bottom
  menu bar region (x 642–1908, y 522–705) is **pure black** (mean RGB 0,0,0 — the theme images
  `home_allmenu_99_n`, `bg_title` are not loading), and the left navi widget is white (map plugin not
  rendering).

### Step 1 — click the "All Menu" affordance at (771, 613)

Code-derived from `QHMI_HomeScreenMain_Wide.qml` (`HOME_1920_MENU_X=642`, `HOME_1920_MENU_Y=522`,
item width 250 / height 183 → centre ≈ (771, 613)).

```
click 771 613
```

- `VM_INPUT_CLICK_ACCEPTED`; `VM_INPUT_FOCUS_BEFORE_MOVE pid=2420 uid=0`.
- `AppHomeScreen` pid at that time: 2487 (later reaped to 2727). **2420 ≠ AppHomeScreen** — the
  click was delivered to another client, not the home screen.
- capture **120,514** bytes → `docs/vm/35-gesture-after-allmenu-click-no-nav-2026-11-05.png`.
  OCR still `STR_CAMERA_ALERT2`; **no navigation** (the All Menus grid did not appear).

### Step 2 — click a *rendered* area (camera widget) at (959, 321)

To rule out "the menu bar was just unrendered", the click was repeated on the camera widget that
*is* painted.

```
click 959 321
```

- `VM_INPUT_FOCUS_BEFORE_MOVE pid=2475` (boot 5) / `pid=797` (boot 6), and in boot 6 the focus pid
  is identified: **`comm=weston.real`, `exe=/usr/bin/weston.real`** — the compositor's own process.
- `AppHomeScreen` pid at the same moment (boot 6): 2390, `comm=AppHomeScreen`. **The click never
  reaches `AppHomeScreen`; it lands on the compositor's background surface.**
- capture **120,453** bytes → `docs/vm/36-gesture-after-camera-widget-click-no-nav-2026-11-05.png`.
  Still `STR_CAMERA_ALERT2`; no navigation.

### Step 3 — the click-routing fact, pinned down (boots 6/7)

`/proc/<focus_pid>/comm` was read immediately after each click:

```
click 959 321   -> VM_INPUT_FOCUS_BEFORE_MOVE pid=793  -> comm=weston.real exe=/usr/bin/weston.real
click 771 613   -> VM_INPUT_FOCUS_BEFORE_MOVE pid=793  -> comm=weston.real exe=/usr/bin/weston.real
AppHomeScreen pid = 2639  comm=AppHomeScreen exe=/app/bin/AppHomeScreen
```

So the synthetic-touch path delivers clicks to the compositor's own client (`weston.real`), **not** to
the ivi-shell application surface, even when `AppHomeScreen` is alive and painting. This is a
stronger statement than the session's earlier "a click reaches a real client pid=797" (§5.2.0): the
"real client" is the **compositor**, and the vendor app does not receive the touch.

### Step 4 — bypass the grid: launch `AppSetup` directly over D-Bus

The launcher interface was introspected (`com.lge.avn.applauncher /Request`,
`request.launch(appid:i, appname:s, applocation:s)`), then `AppSetup` was launched with app ids
recovered from the `ApplicationManager` app-name table (13, and the `APP_SETUP_*` family 50/56/58):

```
dbus-send --session --dest=com.lge.avn.applauncher /Request \
  com.lge.avn.applauncher.request.launch int32:13 string:AppSetup string:/app/bin/AppSetup
```

- Every launch returned `method return` (success), and each started **new `AppSetup` processes**
  (pids 2966, 3102, 3163, 3262, 3351, 3527 …).
- capture after the launches: **129,844** bytes → `docs/vm/37-gesture-after-appsetup-dbus-launch-splash-2026-11-05.png`.
  **`AppSetup` never paints** — no Settings UI, no left menu, no version screen. (The same
  "launched but never shown, so never attaches a buffer" gap the project has recorded for the other
  apps on this path.)

---

## 3. Static corroboration: the gesture is not in this build's QML (exhaustive)

An exhaustive sweep of the whole `/app/share` QML tree (the user's sweep, re-run here against
`work/decrypted-eu-260128/extracted-safe/mango-rootfs`), searching for tap/click counters, returns
exactly these, all accounted for:

| file | counter | what it does |
| --- | --- | --- |
| `app/share/AppEngineerMode/qml/AutoTest/AppEngineerMode_GhostTouchTest.qml` | `touchCount` (reset to `0`) | engineering mode's own ghost-touch test screen |
| `app/share/AppEngineerMode/qml/AutoTest/AppEngineerMode_TouchTest.qml` | `touchCount` (reset to `0`) | engineering mode's own touch-test screen |
| `app/share/AppHomeScreen/qml_new2.0/NMode/PerformanceTimer/Q_NMode_PT_Lap_Main_Track.qml` | `_clickCount` (`>= 5`) | toggles `AppNModeModel.isNaviTestingMode` — a cosmetic flag (checkbox image + translucent overlay) |

**No tap counter exists anywhere near About, General, or a software-version string.** `AppSetup`'s
version screen (`qml_new2.0/general/Q_AppSettingSysInfoVersion.qml`, 22,104 bytes, title
`STR_SETUP_SYSINFO_VERSION_INFO`) contains **exactly one `MouseArea`**, a virtual rotary-knob
emulator — not a gesture:

```qml
/* Virtual knob button */
MouseArea{ visible: isDefaultState; width: 141; height: 78; y: 400; x: 763
    onClicked: { console.log("Clicked!!!"); AppSettingModel.sendVirtualPressComand(0x02); } }
```

Its only other click handler is the update button's `onReleased`
(`KEY_EVT_SETTUP_SYSTEMIN_UPDATE`). **There is no handler on the version rows themselves** — the
`modelData` list (platform, model, SW, FW, navi, map, device id) is rendered by read-only delegates.
A `grep` of the whole `app/share/AppSetup/qml_new2.0` tree for tap/click/press/counter patterns
returns **nothing**. `AppSetup`'s binary also contains no code path that requests app 301
(`AppEngineerMode`) — only factory-reset plumbing (`APP_SETTING_FACTORY_RESET_ENGINEERMODE`,
`checkFactoryResetEngineermode`).

The two distinct thresholds in the counter enumeration are `5` (the lap timer) and `0` (an
initialiser).

**One nearby-but-different tap sequence, recorded for completeness (it is not the About tap).** The
telematics/UVO app `TmsGuiApp` has its own hidden-menu counter, gated by
`TmsEngModel.setting.onHiddenMenu`:

- `app/share/TmsGuiApp/qml/components/screen/QHMI_ScreenMenu.qml` — a 2×2 grid of four transparent
  150×150 touch zones; each press calls `checktHiddenCount(clickcount, index)` and, when
  `canHiddenMenu(clickcount, index)` is true, sends `KEY_EVT_ENGMODE_ENTERANCE_REQUEST`.
- `app/share/TmsGuiApp/qml/components/QHMI_Screen_with_Menu.qml` — two 50×50 hidden zones
  (`hidden1`/`hidden2`); clicking the zones in order, at `clickcount === 5`, sends
  `EVT_GOTO_ENGMODE_ENTERANCE`.

This is a telematics-side, sequence-based engineering entrance (its exact threshold/order lives
partly in C++ `TmsEngModel`), in a different app and screen from the infotainment Settings/About
screen. It does not change the conclusion: **the Settings → About → tap-the-version-string gesture
is not present in this build's QML.**

So the gesture being tested here was an inherited assumption from a sibling platform, and this build
does not implement it.

## Final verdict

**The About-screen tap gesture is absent from this build.** The version screen
(`Q_AppSettingSysInfoVersion.qml`) has no QML handler on the version rows — its single `MouseArea`
is a virtual-knob emulator that only logs and sends a knob-press event — and `AppSetup` contains no
entry point that requests engineering mode (app id 301). The only engineering route is an
app-manager request for app id 301 from a process on the session bus; nothing in the Settings UI
triggers it. A keypad never appeared, and none is claimed.

---

## 4. Capture inventory

| file (docs/vm/) | bytes | what it shows |
| --- | --- | --- |
| `33-gesture-home-screen-authentic-2026-11-05.png` | 120,565 | home screen painted (title bar, `STR_CAMERA_ALERT2`, KIA logo) |
| `34-gesture-home-screen-painted-2026-11-05.png` | 120,556 | same, the clean baseline for the clicks |
| `35-gesture-after-allmenu-click-no-nav-2026-11-05.png` | 120,514 | after `click 771 613` — unchanged, no All Menus grid |
| `36-gesture-after-camera-widget-click-no-nav-2026-11-05.png` | 120,453 | after `click 959 321` — unchanged, click reached `weston.real` |
| `37-gesture-after-appsetup-dbus-launch-splash-2026-11-05.png` | 129,844 | after launching `AppSetup` via D-Bus — still the background, no Settings UI |

## 5. Honest limitations

- The click *delivery* mechanism works (`VM_INPUT_CLICK_ACCEPTED` / `CLICK_DONE`), but the delivered
  target is the compositor's own client, not the vendor app — so "interactive" on this projection
  currently means "accepts synthetic clicks", not "drives the vendor UI".
- `AppSetup` launching-but-not-painting is a projection limitation (the show handshake never fires
  for on-demand apps), not proof that the version screen is absent from the vehicle; the absence of
  the *tap gesture* is proven by the static analysis, not by the projection.
- No keypad appeared in any capture. **No keypad image exists, and none is claimed.**
- **I did not reach a settings/About screen**, so I cannot report what the version string looks like
  or whether it reacts to a tap. The remaining question from the static result — whether a C++-side
  handler (rather than a QML one) hides behind the version string — is therefore **not settled by
  these captures**; it would need the version screen to present, which this projection does not do
  (`AppSetup` launches but never paints).
