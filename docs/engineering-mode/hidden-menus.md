# Hidden and diagnostic menus — LGE Gen5W "mango" (EU `260128`)

Static analysis only: no VM boots, no QEMU runs, no hardware. Every claim is tagged
**[E]** (evidenced: quoted string, file:line, or address/instruction) or **[I]**
(inferred from the evidence).

Image analysed: `work/decrypted-eu-260128/extracted-safe/mango-rootfs`
(kernel `4.1.27-abl`, x86-64, Qt5/QML, SMACK). Addresses are ELF virtual addresses of
the named binary; on these binaries the `.rodata` file offset equals the VMA, so
`strings -t x` offsets and `objdump` targets agree.

---

## 0. Corrections to prior assumptions

1. **`AppSetup` `0x573194` is not the app-id compare.** That instruction is
   `cmpl $0x12d,%esi` inside `QCANControllerListener::onCAN_data_received2D(const SQCanFrameList&)`
   (function range `0x572f90`–`0x57c150`), and `%esi` there is a **CAN message id**
   extracted at `0x573008`–`0x573022`:
   `mov ebx,[rdx]` / `and esi,0x1fffffff` / `and eax,0x7ff` / `cmovb esi,eax`.
   So `0x12D` in that switch is a CAN frame id (11/29-bit arbitration id), not app
   id 301. **[E]**
   The app-id-301 compare lives in `ApplicationManager`, not `AppSetup`
   (`0x1f619e: mov esi,0x12d`, §1). **[E]**
2. **No tap-count threshold exists in this build's Settings UI.** `AppSetup` QML
   (`app/share/AppSetup/qml_new2.0/general/Q_AppSettingSysInfoVersion.qml`,
   `general/systeminfo/Q_AppSettingSysInfoWebManual.qml`) contains no gesture counter;
   the only clicked-counter patterns in the whole Setup QML tree are list-length
   helpers (`_count++` in `wifi/Q_AppSettingWifi.qml:27`). `AppSetup`'s only
   engineering-related strings are factory-reset plumbing
   (`APP_SETTING_FACTORY_RESET_ENGINEERMODE`, `slotNotifyFactoryResetEngineerMode`). **[E]**
3. **The engineer PIN on this build is `19480717`, not `19491003`.** The stored
   engineer digest equals SHA-256 of `19480717` (§5). **[E]**

---

## 1. What "engineering mode" is, and how it is launched

| Fact | Evidence |
|---|---|
| App id 301 (`0x12D`) is `APP_ENGINEERMODE` | enum string `APP_ENGINEERMODE` @ `ApplicationManager` `0x2fd84f`; sibling states `APP_NAVIGATION_ENGINEERMODE` @ `0x2fd287`, `APP_ENGINEERMODE` used with `0x12d` in the launcher |
| Launcher entry point | `ApplicationManager` `0x1f6160`: `0x1f619e mov esi,0x12d` → `call 0x18e7b0` (is-app-running); `0x1f6360 mov edx,0x12d` / `0x1f63ae` / `0x1f63f0` → `0x1f9a10` / `0x1f9c00` (request launch) |
| Process path | `ApplicationManager` `"/app/bin/AppEngineerMode"` @ `0x308d04`, log `"EngineerMode Full Path : %1"` @ `0x308d1d`; `AppLauncher` `"/tmp/app/bin/AppEngineerMode"` @ `0x46fee`, `"killAll AppEngineerMode"` @ `0x48bfc` |
| QML root | `"/app/share/AppEngineerMode/qml/main.qml"` @ `AppEngineerMode` `0x982b68`; startup log `"AppEngineerMode App Start !!"` @ `0x981890` |
| Launch variants | `0x1f6160` takes an argument: `1` → `0x1f6340` (`0x1f9a10`), `2` → `0x1f6388` (`0x1f9c00`, push `1`), `5` → `0x1f63c8` (`0x1f9c00`, `r9d=1`, push `0`). **[E]** |

**Launch chain (compressed):** trigger → `ApplicationManager::…Launcher(arg)`
`0x1f6160` → checks `isAppRunning(0x12d)` → builds `QStringList` argv → calls the
app-launcher D-Bus adaptor → `AppLauncher` spawns `/tmp/app/bin/AppEngineerMode`
(surface argv/`QT_WAYLAND_SET_SURFACE_ID` scheme seen in `AppLauncher` `0x46edf`
`"APPID"`, `0x46ee5` `"QT_WAYLAND_SET_SURFACE_ID"`) → `main.qml` →
`AppEngineerMode_Main.qml` (PIN pad) → `AppEngineerMode_FullMain.qml` (engineer menu)
or `AppDealerMode_Main.qml` (dealer menu). **[E]** for each hop, **[I]** for the
strict ordering of the two D-Bus adaptor calls.

---

## 2. Entry points into AppEngineerMode (all found)

| # | Trigger | Mechanism | Evidence |
|---|---|---|---|
| E1 | **Dedicated D-Bus method** `show_engineermode` | ApplicationManager exposes `com.lge.avn.appmanager.info` with `show_engineermode`, `hide_engineermode`, `show_engineermode_dtc` | introspection `ApplicationManager` `0x339faf/0x339fd6/0x339ffd`, `<interface name="com.lge.avn.appmanager.info">` @ `0x334574`; method-name table @ `0x32984b/0x32985d/0x32986f` **[E]** |
| E1a | …called from other apps in the image | proxy strings present in `navi/Bin/AppNavi` (`show_engineermode` @ file 0x60d95eb, `hide_engineermode` @ 0x60d937f), `LocationManager` (`0x7695f`, `0x80790`), `AppMPAutoTest` (`0x1a6075`, `0x1aff6e`) | **[E]** strings; caller-side code is via QDBusInterface proxies, so it is **[I]** which user action fires it |
| E2 | **Front-panel "special key"** | micom D-Bus signal `NotifyKeyFrontSpecialEvent` (`com.lge.car.micom.can`) → `HWKeyInterface::SpecialKeySlot` → eng launch | `micommanager_userspace` introspection `<signal name="NotifyKeyFrontSpecialEvent">` @ `0x66990`; `ApplicationManager` `HWKeyInterface::SpecialKeySlot` `0x206090`, calls `0x1f6160` at `0x2062f8`, `0x2063ca`, `0x2065aa` **[E]** |
| E2a | Payload decoding of E2 | `0x206308`: two payload bytes → `r13d` (byte 0), `ebp` (byte 1). `0x2061d8 cmpl $0x1,%r13d; je 0x2062a0` — byte 0 must be `1`; then `0x2062a0 cmpl $0x1,%ebp` / `0x2062a9 cmpl $0xa` / `0x2062b2 cmpl $0x5`. Subtype `1` → set `[engine+0x14]=1` and `Launcher(1)`; subtype `5` → only if `0x23f760()/0x22da80(...,0x47)==1`, then `Launcher(5)`; subtype `0xa` → if running, `0x1cb910(iface,0x12d,0xbe,0)` (hide/terminate path) else `[+0x14]=0` + `Launcher(1)` | **[E]** for constants/addresses; **[I]** for the semantic names of subtypes |
| E2b | …injectable from any session-bus client | `micommanager_userspace` exposes **test methods** `TestNotifyKeyFrontSpecialEvent` (also `TestNotifyKeyFrontPannelEvent`, `TestNotifyKeyCCPEvent`, `TestNotifyKeyRRCEvent`, `TestNotifyKeySWRCEvent`, `TestNotifyKeyREAREvent`) | introspection @ `0x6752a` etc. **[E]** |
| E3 | **Key-event id 0x48** | `UserInputHandler::handleEvent` (`ApplicationManager` `0x1aff70`): `0x1b0c58 cmpl $0x48,0x20(%rsp)` → `je 0x1b12d5` → `[engine+0x14]=1` → `Launcher(1)` (`0x1b12eb`) | **[E]**; which physical key maps to eid 0x48 is **[I]** (HMI event enum is compiled in, not present as data) |
| E4 | **Standby-clock easter egg** `GoXXXStandBy::calcHistory` | `ApplicationManager` `0x1b7cb0`: reads persistent setting `APP_ENG_MODE_EMMCTEST_WRITE_ENABLE` (`0x1b7d08`, string @ `0x303848`), `QVariant::toInt`; if non-zero and `0x22da80(...,0x22)==0` → `Launcher(2)` (`0x1b7d8e`) and logs `"GoXXXStandBy::calcHistory Excute ENG"` (@ `0x303870`); otherwise logs `"GoXXXStandBy::calcHistory Dont excute ENG"` (@ `0x303898`) | **[E]** |
| E5 | Already running guard | `0x1f61a6 call 0x18e7b0` with `esi=0x12d`; `AppEngineerMode` also traps re-entry via `checkExecutMode` (`0x981c80`) | **[E]** |

**[I]** E1 and E2 are the two routes a technician can reach without a working
"SOP" bypass: E1 is a plain system/session D-Bus call, E2 is the front-panel special
key (and E2b lets any process forge it).

---

## 3. The gesture: what actually exists

**Finding:** on this build the documented "tap the software version 5–10 times" gesture
is **not present** in the Settings app — neither in QML nor in `AppSetup`'s binary. **[E]**

Evidence:
* `AppSetup` `qml_new2.0/general/Q_AppSettingSysInfoVersion.qml` — the version screen has
  only `onReleased` → `QML_Handler.qmlSendEvtKey(HMIEVENTS.KEY_EVT_SETTUP_SYSTEMIN_UPDATE)`
  (update button, line 326) and a virtual-knob `MouseArea` → `AppSettingModel.sendVirtualPressComand(0x02)`
  (line 344). No counter, no threshold, no engineering request. **[E]**
* `qml_new2.0/general/systeminfo/Q_AppSettingSysInfoWebManual.qml` (the Manual/QR screen
  used by the "numpad on the manual panel" folklore) contains no touch grid and no
  hidden-key handling. **[E]**
* `AppSetup` binary contains no code path that requests app 301: its engineering strings
  are only `APP_SETTING_FACTORY_RESET_ENGINEERMODE` (`0x9af0c0`),
  `slotNotifyFactoryResetEngineerMode` (`0x9bb8f0`), `checkFactoryResetEngineermode`
  (`0x9b7120`). **[E]**

**What this build does implement instead** (each `[E]` by address above):
1. Front-panel **special key** → `HWKeyInterface::SpecialKeySlot`, payload `{1, 1|5|10}` (E2/E2a).
2. **eid 0x48** through `UserInputHandler::handleEvent` (E3).
3. **Standby-clock easter egg** `calcHistory`, gated on persistent flag
   `APP_ENG_MODE_EMMCTEST_WRITE_ENABLE` (E4).
4. Direct D-Bus `show_engineermode` (E1).

**On the PIN pad itself** the second factor is real and non-trivial: 8 digits engineer,
4 digits dealer, 5-strike lockout (§5). **[E]**

**[I]** The widely-cited tap gesture most likely belongs to a different product line or
an earlier S5W build; it should not be presented as this image's entry. The nearest
touch-level equivalent here is the special-key channel, which is a *hardware* key event
rather than a screen tap.

---

## 4. Menu inventory (AppEngineerMode QML tree)

Mode selector: `Global.nEngineerAppMode` ∈ {`APP_MODE_ENGINEER`, `APP_MODE_DEALER`}
(`qml/AppEngineerMode_Main.qml`, `gotoMain()`), loaded from
`AppEngineerMode_FullMain.qml` or `AppDealerMode_Main.qml`. **[E]**
`Global.getLoaderQmlPathByMenuName(name)` maps menu names to QML paths inside the
binary (`AppEngineerMode` string table `0x982b68`–`0x9849xx`). **[E]**

Pre-menu gates:
* PIN → `AppEngineerModeEngine.checkPassWord(...)`: `21` = engineer, `11` = dealer
  (`AppEngineerMode_PinCodeKeypad.qml:391`, `:396`, `:411`). **[E]**
* Warning popups before the menu: `AppEngineerMode_EnterWarningPopup.qml` (engineer),
  `AppEngineerMode_Dealer_EnterWarningPopup.qml` (dealer); only the engineer path is
  used when `checkSOPVersion()` is true (`PinCodeKeypad.qml:391-404`). **[E]**

### 4.1 Engineer top-level (`qml/AppEngineerMode_FullMain.qml`)

Gate for the whole page: `property bool bIsSOPVersion : AppEngineerModeEngine.checkSOPVersion()` (line 18). **[E]**

| Button (`firstText`) | Target screen | Gate / note |
|---|---|---|
| `Software` | `Software` | — **[E]** |
| `Hardware` | `Hardware5w` | — **[E]** |
| `Dynamics` | `Global.setMainAppScreen(VariantSetting.variantString, false)` | per-variant QML; `Dynamic/AppEngineerMode_DynamicMain{EU,Ko,AUS,RUS,NoModemEU,NoModemAUS}.qml` **[E]** |
| `S/W Update` | `Update` | — **[E]** |
| `Diagnostic` | `Diagnosis` | also starts `CpuDegree.startGetDegree()` **[E]** |
| `System Config.` | `SystemConfig` | if not SOP: `SystemInfo.sscAskSoundSetupInfo(18)` first **[E]** |
| `Log System` | `LogSetting` | — **[E]** |
| `AutoTest` | `AutoTest_Sop` if `bIsSOPVersion` else `AutoTest` | **[E]** |
| `Variant` | `Variant` | `visible: (bIsSOPVersion === true)?false:true` — hidden on SOP **[E]** |

### 4.2 Engineer sub-lists and their model gates

| Menu | Items | Gate |
|---|---|---|
| Software (`Software/AppEngineerMode_SoftwareLeftModel.qml`) | `Head Unit`, `Peripherals` | none **[E]** |
| Hardware 5W (`Hardware/AppEngineerMode_HardwareLeftList_5w.qml:35`) | full: `Version`, `Connect Status`, `Car Signal`, `Memory`, `PWM Duty`, `EMMC`; SOP: same minus `PWM Duty` | `model: (AppEngineerModeEngine.checkSOPVersion() === true)?hardwareListSop:hardwareList` **[E]** |
| S/W Update (`Update/AppEngineerMode_UpdateLeftList.qml:57`) | full (`updateList`): `Force Update`, `Encryption Update`, `Scheduled Update List`, `Scheduled Update Test`, `VESS Logging`, `ADP Logging`, `AMP Logging`; SOP (`updateList_sop`): `Scheduled Update List`, `VESS Logging`, `ADP Logging`, `AMP Logging` | same `checkSOPVersion()` ternary **[E]** |
| Diagnostic (`Diagnosis/AppEngineerMode_DiagnosisLeftList.qml:45`) | full: `DTC`, `Command`, `HU`, `AMOS`; SOP: `DTC`, `Command`, `HU` (`AMOS` dropped; `MOST` is commented out) | `checkSOPVersion()` ternary **[E]** |
| System Config. (`SystemConfig/AppEngineerMode_SystemMain.qml:253+`, `SystemConfigLeftList.qml:20`) | full (16): `Log Data`, `Sound`, `VCRM Log`, `SW Config`, `Screen Capture`, `Kernel Setting`, `EV Reset`, `Display Setting`, `CPU WDT Reset`, `Climate LCD`, `Camera Tuning Mode`, `Test Config N Mode`, `Navi/TTS Output Setting`, `Date/Time Setting`, `SPI Log`, `OTA Initialize`; SOP (2): `Screen Capture`, `OTA Initialize` | `checkSOPVersion()` ternary **[E]** |
| AutoTest (`AutoTest/AppEngineerMode_AutoTest.qml`, `AppEngineerMode_AutoTest_page2.qml`, `AppEngineerMode_AutoTest_Sop.qml`) | page 1: `Agent State`, `IP Table Debug`, `Secure Console`, `eMMC WDT Count`, `ABL WDT Count`, `CPU WDT Count`, `IP Config`, `IP Config`+`shell script`, `Version`/`Check`, `Auto Test`, `FAN ON/OFF`, `ACC Mode Set`, `CPU WDT`, `SteerMode Set`; page 2: `BenchMode Set`, `User Mode Change`, `USB Mode Change`, `EMMC Log Write after Boot`, `Display Pattern Test`, `USB EYE Pattern`, `Key & Touch Test`, `Popup OSD Capture`, `eMMC Stress Test`, `LCD PRBS Test`, `LCD Color Test`, `Setting Target`, `Setting CML Level`; SOP page: `Secure Console`, `User Mode Change` | reachable only via `AutoTest` button; SOP build gets the reduced page **[E]** |
| Variant (`Variant/AppEngineerMode_VariantLeftList.qml`) | per-project model; each entry is `{name:"Vehicle", qmlFileName:"AppEngineerMode_Variant_Vehicle_<project>.qml"}` (e.g. `lx2` @ line 691, `sk3`, `dn8`, `ac3` + `Navi` @ 720 …) | hidden entirely on SOP; selection by `VariantSetting.variantInfo` **[E]** |
| Log System (`LogSetting/AppEngineerMode_LogMain.qml:27`) | log-mode page, `"Mode " + loggingMode`; several controls disabled when `UpgradeVerInfo.isCryptoKey()===0 && !checkSOPVersion()` (lines 976-977) | `bIsSOPVersion` local property **[E]** |
| IpConfig (`IpConfig/AppEngineerMode_IpConfigMain.qml`, `…_Shell.qml`) | IP address entry + `Set IP` / `Get IP`; separate "shell" variant page | launched from AutoTest page **[E]** |
| ImageViewer (`ImageViewer/*`) | image viewer incl. `…_FromUSB.qml` | not in the engineer main button set; **[I]** reached from Log/Update paths |

### 4.3 Dealer top-level (`qml/AppDealerMode_Main.qml`)

`Diagnostics` (→ `DiagnosisDealerMode`), `Radio`, `Navigation`, `Media` (→ `MediaMode`),
`Update` (→ `DealerswUpdate`), `System Info` (→ `DealerSoftware`), `S/W History`
(→ `UpdateHistory`), `Connected Car Service`, `Factory Reset` (→ `DealerFactoryReset`),
`System Config` (→ `DealerSysConfig`). All labels via `Global.getTrText("STR_ENG_*")`. **[E]**

Dealer-only extra surfaces: `Diagnosis/AppEngineerMode_Dealer_Reset_Command.qml`,
`Dealer_SysInfo_ErrorHistory*`, `Dealer_CCarService*`, `Software/AppEngineerMode_Dealer_*`. **[E]**

### 4.4 Runtime-overridable menu data

`/app/data/AppEngineerMode/dynamicmenu` and `/app/data/AppEngineerMode/feedbackupdate`
are read/created at runtime (`AppEngineerMode` `0x991b80`, `0x991ba8`, log
`"Can not open file :: /app/data/AppEngineerMode/dynamicmenu"` `0x991c58`,
`"Create file :: …"` `0x991c98`, `"[USM] DynamicMenu Update Value : "` `0x991c30`).
**[E]** — **[I]** the Dynamics/USM menu content can therefore be changed by writing a
file rather than by reflashing.

---

## 5. PIN verification and lockout

| Claim | Evidence |
|---|---|
| Keypad collects 8 digits (engineer) or 4 (dealer) | `AppEngineerMode_PinCodeKeypad.qml:379-389`: `bIsDealerMode ? txtCheck1..4 : txtCheck1..8`; `bIsDealerMode: AppEngineerModeEngine.checkDealerMode()` (line 39) **[E]** |
| Result codes `21` / `11` | `checkPassWord` returns `21` (engineer) and `11` (dealer) — QML `:391`, `:396`, `:411`; literals in binary: `"21"` @ `0x9801f4`, `"11"` @ `0x97f863` **[E]** |
| Algorithm | helper `0x746850`: `QString::toUtf8` → `QCryptographicHash::hash(QByteArray, 4)` (`0x746902`, `4 = Sha256`) → `QByteArray::toHex` (`0x746925`) → `QString::compare(...,Qt::CaseInsensitive=1)` (`0x7469fd`, `0x746a9d`) **[E]** |
| **Not salted** | the QByteArray fed to the hash is built only from the entered text: `QString::toUtf8_helper` (`0x7468d5`) → `QByteArray::append` (`0x7468e5`); the two 64-byte constants are the *expected* values used by `compare`, not mixed into the digest **[E]** |
| Engineer expected value | `.rodata` `0x982660` = `a3946c514cd940553a8401d0cf74dbf74861824e5f337735b56218bcb99c307c` = SHA-256("19480717") (recomputed) **[E]** |
| Dealer expected value | `.rodata` `0x9826a8` = `8350242b2df439d296a664c7c59b117507d0b3c537fa293304c84d84eb85cc43` = SHA-256("2400") (recomputed) **[E]** |
| Storage type | static hex constants in `.rodata`; comparison is case-insensitive string compare — **no KDF, no per-unit salt, no device binding** **[E]** |
| Attempt counter | `AppEngineerModeEngine::getBadPasswordCnt()`, `setBadPasswordInfo(QString,QString)`, `cleartBadPasswordInfo()`, `startBadPassword()`, `getBadPasswordDiff()`, `getBadPasswordTime()` (moc names @ `0x99e051`, `0x99e334`, `0x99e35a`, `0x985712`); counter file **`/tmp/eng_limit_check.txt`** (`0x9857fd`), logs `"wrong password log open sucess"` `0x984af0`, `"wrong password file clear success"` `0x982638` **[E]** |
| Lockout policy | `wrongpasswordCnt > 4` → `startBadPassword()` + timer (`PinCodeKeypad.qml:192-196`, `:245-252`); countdown via `getBadPasswordDiff()` `"HH:MM"` (`:204-230`) **[E]**; exact lock duration is computed in the binary and was not decoded **[I]/open** |

**[I]** Because the check is an unsalted SHA-256 of a short numeric string held in
readable `.rodata`, the effective secret is the 4/8-digit space, not a cryptographic
boundary. The 5-strike lockout (state in `/tmp`, i.e. volatile, cleared on reboot) is
the only rate limiting.

---

## 6. Command / shell-capable menus

| Surface | What it can run | Evidence |
|---|---|---|
| `IpConfig/AppEngineerMode_IpConfigMain_Shell.qml` | `IPInfo.handleSetIPMakeShell(newIP, netmask, gateway)` — shell command assembled from three user-entered strings | QML line 323, labels `"IP address"`, `"Gateway"`, `"Enter the new IP address."`, buttons `"Set IP."` / `"Get IP."` **[E]**; exact command line not recovered **[I]** |
| AutoTest page `"IP Config" / "shell script"` | opens the shell IP page (`Global.setMainAppScreen("IpConfig", true)`) | `AutoTest/AppEngineerMode_AutoTest.qml:421-465` **[E]** |
| WiFi throughput test (`Dynamic/AppEngineerMode_WiFiTput.qml`) | `QProcess` runs `iperf`/`iperf3` after **`/usr/sbin/iptables -P INPUT ACCEPT`** and **`/usr/sbin/iptables -F`** (firewall flush), search paths `/usr/bin`, `/usr/local/bin`, `/usr/local/sbin`, `/usr/sbin`, work dir `/rw_data/wifi/tmp_tput_test` | `AppEngineerMode` `.rodata` `0x999110`, `0x9992b2`, `0x999264`-`0x9992db`, `IperfHandler::*` @ `0x9993a0` **[E]** |
| Shell interpreter availability inside the app | `/bin/sh` @ `0x98aae0`, `/bin/bash` @ `0x997aae`, `"Please check the location of shell program."` (adjacent) | **[E]** |
| Update path shell script | `app/share/AppEngineerMode/constants/iasimage_update.sh` — `mount /dev/mmcblk0p1 /dev/mmcblk0p2` into `/tmp/p1`/`/tmp/p2` for sub-image (kernel) update | **[E]** |
| `Diagnosis/AppEngineerMode_Diagnosis_Command.qml` | `Reset System`, `Factory Reset`, `Delete Navi Persistence` (→ `AppEngineerMode_Diagnosis_DeleteNaviPopUp.qml`), `DSP Type` | QML lines 22/79/133/187 **[E]** |
| `Diagnosis/AppEngineerMode_Dealer_Reset_Command.qml` | dealer reset commands (paired with `Diagnosis_Command`) | file present, **[E]** existence, **[I]** contents |
| `Diagnosis/AppEngineerMode_Diagnosis_AMOS.qml` + `app/bin/AMOS.tar` | AMOS diagnostic transport (engineer only; removed from SOP list) | **[E]** |
| Screen capture | `AppEngineerModeEngine::captureEngineerModeScreen(QString)`, `setEngineerModeCapture(bool)`, flag file `/tmp/ENG_CAPTURE_ENABLE`, output dir `mkdir /log_data/CaptureImage`, signals `CaptureEngineerModeScreen` / `NotifyScreenCaptureOnOff`; banner `"===== [Background Start] Display Capture!!"` | `0x98…` strings (see quote list) **[E]** |
| `bin/factory-mic-test.sh` | factory mic loopback test script, takes mic index → `mic_fac_1`/`mic_fac_2` | **[E]** |
| `bin/AppTestAgent.sh` | `/usr/libexec/weston-screenshooter /home/root/screencapture.png` — one-shot screen capture agent | **[E]** |

[Suspicious but unproven] The IP-shell page interpolates three free-text fields into a
command; whether it quotes/validates them is in `IPInfo::handleSetIPMakeShell`, not
recovered here. Treated as **[I]** injection-capable by construction.

---

## 7. Diagnostics outside AppEngineerMode

| Surface | What it is | How it starts | Evidence |
|---|---|---|---|
| **AppMPAutoTest** | factory/bench auto-test agent; logs to `/log_data/AppMPAutoTest/`, opens eng mode itself | `app/bin/mpautotest.sh` (surface id `10010`), D-Bus `com.lge.hkmc.avn.appfunc.autotest.engmode` @ `/com/lge/hkmc/avn/appfunc/autotest/engmode`; also `show_engineermode` proxy; config `/app/data/AppEngineerMode/TestAgent/autotest.conf` (`AppLauncher` `0x52410`); `ApplicationManager` log `"Request to AppLauncher to start MPAutoTest"` @ `0x30aa48`, path `0x308d5a`, `0x308e54 "/tmp/AppMPAutoTest/do_mpauto"` | **[E]** |
| **AppAutoKey** | key-injection harness: calls micom test methods `TestNotifyKeyFrontPannelEvent`, `TestNotifyKeyCCPEvent`, `TestNotifyKeyRRCEvent`, `TestNotifyKeySWRCEvent` over the system bus; `onGenerateKey()` | `app/bin/AppAutoKey.sh` (surface id `11000`) | **[E]** |
| **micommanager_userspace** | origin of all key/panel signals; exposes `TestNotify*` injectors and `AskAutotestWIPID`, `SetAutoTestKeyControl`, `SetAutoTestWIPIDControl`, `AskDTCClearRequest`, `AskDTCReadRequest` | always running (system bus `com.lge.car.micom*`) | **[E]** (introspection XML) |
| **Navi-side engineer mode** (`Navi::EngineerMode`) | a *separate* hidden menu family inside the map app: pages (`getCurrentPage`/`getPrevPage` over `ecNaviEngineerMenuId`), `enterSimpleEngineeringMode`, `getDealerMode`, `action(...)`, map/GPS debug (`getMapMatchingGraphInfo`, `getGPSDRMMState`, `engineerModeDebugInfo`), `hippoLogSimulation*` | inside `navi/Bin/AppNavi`; the same binary also proxies `show_engineermode` | **[E]** symbols/strings; exact key/gesture **[I]/open** |
| **LocationManager** | can `show_engineermode` / `hide_engineermode` (proxy) | system service | **[E]** proxy strings, **[I]** trigger |
| **AppSetup copy-log special key** | `MMUSControl::registerListenSpecialKeyForCopyLog()` registers a listener for micom `NotifyKeyFrontSpecialEvent` (interface `com.lge.car.micom.can`, slot `1slotNotifyKeyFrontSpecialEvent(QByteArray)`); handler logs `"Request show copy log popup!!!"` and is gated by `"Not SOP version, can handle copy log special key!!!"` | hardware special key | **[E]** `AppSetup` `0x3efe60` (`QDBusConnection::connect` at `0x3f0009`), strings `0x9d4440`, `0x9d4470`, `0x9d4548`, `0x9d58c0` |
| **AppEngineerMode internal special key** | `AppEngineerModeEngine::specialkeySlot(QByteArray)` (moc `0x988560`), wired to a `key_iface` signal (`"Can not Connect key_iface Signal <-> Slot: specialkeySlot"` `0x989ef8`); also `"Screen is hidden. Ignore CCP key"` `0x981f80` | hardware key while eng app is foreground | **[E]** |
| **AppSetup factory-reset engineer hook** | `APP_SETTING_FACTORY_RESET_ENGINEERMODE`, `checkFactoryResetEngineermode()`, `slotNotifyFactoryResetEngineerMode(int)`, `"Reset after factory rese engineermode"` | post-factory-reset flow | **[E]** |
| **AppSFC** | **not present** in this image (no `AppSFC` binary or QML) | — | **[E]** (absence; `app/bin` has 192 entries, none match `*SFC*`) |

No `dealer`, `self-test`, `dump` or `capture` binaries were found beyond the above; the
dealer surface is a *mode inside* `AppEngineerMode` (§4.3), not a separate app. **[E]**

---

## 8. Gate summary (`checkSOPVersion` and friends)

| Gate | Meaning | Where it bites |
|---|---|---|
| `AppEngineerModeEngine::checkSOPVersion()` | returns whether `engine+0x13c == 1` (per prior analysis); build shows `[BB_MODE_MASS_PRODUCT]` @ `0x98184b` and `"[Version Info - Build opion is MASS_PRODUCT]"` @ `0x9916c8` | hides `Variant`; switches Update / Hardware / Diagnosis / SystemConfig / AutoTest model sets; swaps engineer warning popup for direct menu entry **[E]** |
| `AppEngineerModeEngine::checkDealerMode()` | dealer vs engineer keypad width and 4-vs-8 digit PIN | PIN pad, dealer main page **[E]** |
| `VariantSetting.variantString` / `variant.country_code` | per-project (EU/Ko/AUS/RUS/no-modem) dynamic menu QML; per-project Variant QML | `Dynamics` button, Variant list **[E]** |
| `APP_ENG_MODE_EMMCTEST_WRITE_ENABLE` (persistent) | eMMC write-enable flag; doubles as the standby-easter-egg gate | `GoXXXStandby::calcHistory` (E4), eMMC test page **[E]** |
| `UpgradeVerInfo.isCryptoKey()` | crypto-key presence; disables certain Log System controls on non-SOP builds | `LogMain.qml:976-977` **[E]** |
| `VariantSetting.isReqTPMkbd()` / `ismkbdchecking` | 2G-CAN vs micom-keyboard hardware variant | PIN pad `Component.onCompleted` **[E]** |

---

## 9. Open items

1. The **exact user gesture** that produces eid `0x48` (E3) — the HMI event enum is
   compiled only; no name table in `.rodata`. **[open]**
2. Owner-side confirmation of E2 subtype semantics (`1` = enter, `5` = ?,
   `0xa` = exit) — the *code* paths are clear, the labels are not. **[I]**
3. `IPInfo::handleSetIPMakeShell` command template (quoting/validation). **[open]**
4. `Navi::EngineerMode` menu page list and its entry gesture inside `AppNavi`
   (143 MB binary; symbol-level inventory only). **[open]**
5. Exact lockout duration in `startBadPassword()` / `getBadPasswordDiff()`. **[open]**

---

## 10. Reproduction notes

```sh
R=work/decrypted-eu-260128/extracted-safe/mango-rootfs

# app id 301 = engineering mode
strings -a -t x $R/app/bin/ApplicationManager | grep -n "APP_ENGINEERMODE\|/app/bin/AppEngineerMode"
objdump -d $R/app/bin/ApplicationManager | grep -n "0x12d" | head

# engineering entry points
strings -a -t x $R/app/bin/ApplicationManager | grep -n "show_engineermode\|SpecialKeySlot\|calcHistory"
strings -a -t x $R/app/bin/micommanager_userspace | grep -n "TestNotify"

# menu models / gates
grep -n "checkSOPVersion\|ListElement" $R/app/share/AppEngineerMode/qml/*/*.qml

# PIN
python3 - <<'EOF'
import hashlib
for p in ("19480717","2400"):
    print(p, hashlib.sha256(p.encode()).hexdigest())
EOF
strings -a -t x $R/app/bin/AppEngineerMode | grep -n "eng_limit_check"
```

Note: `AppSetup` `0x573194` (`cmpl $0x12d,%esi`) is a **CAN id** dispatch inside
`QCANControllerListener::onCAN_data_received2D`, not an app-id check — see §0.
