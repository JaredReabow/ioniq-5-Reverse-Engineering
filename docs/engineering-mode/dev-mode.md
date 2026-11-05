# Engineering-mode "DEV mode": the token, what it unlocks, and how (if at all) it activates

Read-only investigation. Build analysed: EU Gen5W Linux `NE_E.EUR.S5W_L.001.001.260128`,
x86-64 (`work/decrypted-eu-260128/extracted-safe/mango-rootfs`). No VM run, no hardware.

Path shorthand: `$ROOTFS` = `work/decrypted-eu-260128/extracted-safe/mango-rootfs`.
Every address below is a virtual address inside the named ELF (file offset = vaddr for
the first `PT_LOAD` segment in these binaries, so the two are interchangeable here).

Confidence labels: **[E]** evidenced — the string / instruction / file is quoted;
**[I]** inferred — reasoning only, no measurement.

---

## 0. Bottom line

- A "dev mode" **does exist in code**, but it is not a stored user setting. It is a
  build-state integer on the engineering-mode engine, exposed to QML as
  `AppEngineerModeEngine.getEngType()` / `checkSOPVersion()`. **[E]**
- The token is the **"Run Version"** field at `engine + 0x13c`; value `1` = SOP /
  "No Develop Version", anything else = develop. **[E]**
- It is set exactly once, at start-up, by `void AppEngineerModeEngine::setEngType()`,
  which in **this 260128 binary writes `1` unconditionally** and only *logs* differently
  when the running executable is `/tmp/app/bin/AppEngineerMode`. So on 260128 the
  develop state is **not reachable by re-launching the shipped binary from `/tmp`**. **[E]**
- The container that would deliver a develop binary is real and still present:
  `AppLauncher` prefers `/tmp/app/bin/AppEngineerMode` for app id `301`, and
  `AppDMClient` constructs `/tmp/app/bin/AppEngineerMode` from a `<usb>/VarUpgrade`
  directory with key/hash checks. **[E]** for the literals, **[I]** for the end-to-end flow.
- Independent of any dev mode, `/update/disableEncryptionUpdate` can be created by
  `AppMPAutoTest` on the MICOM event `EVT_MP_ENCRYPTION_DISABLE_REQ`. **[E]**

---

## 1. The token that represents dev mode

### 1.1 QML-visible token

`$ROOTFS/app/share/AppEngineerMode/qml/Update/AppEngineerMode_UpdateLeftList.qml:57`:

```qml
model: (AppEngineerModeEngine.checkSOPVersion() === true)?updateList_sop:updateList
```

`checkSOPVersion()` is the single QML boolean that separates the production menu from the
develop menu. It is used in 35 QML files. The integer shape of the same state is exposed
as `getEngType()`; the only remaining references are commented out
(`qml/Hardware/AppEngineerMode_HardMain_5w.qml:18`,
`qml/Hardware/AppEngineerMode_HardwareLeftList_5w.qml:13`):

```qml
//property var versiontype: AppEngineerModeEngine.getEngType()
```

Both names are in the engine's Qt meta-object string table in `$ROOTFS/app/bin/AppEngineerMode`
(contiguous run `… checkDealerMode | getEngType | checkSOPVersion | isMPAirConditionerScreen …`). **[E]**

### 1.2 The field itself

`AppEngineerModeEngine::checkSOPVersion()` at `0x737400` (the function that logs the literal
`bool AppEngineerModeEngine::checkSOPVersion()`, `0x987d40`):

```
73740d: movl 0x13c(%rdi), %r13d     ; read member
7374fa: cmpl $0x1, 0x13c(%r12)      ; == 1 ?
737503: sete %al                    ; return (field == 1)
```

`AppEngineerModeEngine::getEngType()` at `0x7373c0` is the same field unboxed:

```
7373d4: movl 0x13c(%rdi), %eax
7373da: retq
```

The value is logged with the label `Run Version ` (`0x9851c1`), printed at `0x7374dd`
inside `checkSOPVersion()`:

```
7374bc: leaq  "]"              (0x984d0f)
7374cb: leaq  "Run Version "   (0x9851c1)
7374dd: movl  %r13d,%esi ; QTextStream::operator<<(int)
```

So the token, verbatim, is `Run Version` / `getEngType()` / `checkSOPVersion()`, backed by
`this+0x13c`. **[E]**

### 1.3 The only writer

`AppEngineerModeEngine::setEngType()` at `0x737180` (logs `0x987d80`):

```
737247: leaq "[setEngType] No Develop Version"   (0x982560)   ; logged first, unconditionally
73725e: leaq 0x228(%rbp), %rsi                                 ; member QString (own exe path)
737268: movl $0x1, 0x13c(%rbp)                                 ; <-- the write
737272: call QString::trimmed()
737287: leaq "/tmp/app/bin/AppEngineerMode"      (0x98518f)
737295: call QString::compare_helper(..., Qt::CaseSensitivity=1 /* insensitive */)
7372a4: testl %ebp,%ebp
7372a6: je    0x7372e0                                         ; equal -> "USB Run" branch
7372a8: retq                                                   ; not equal -> return
...
737371: leaq "[setEngType] USB Run"              (0x9851ac)
737380-737388: ~QDebug(); jmp 0x7372a8                          ; log only, no store
```

A byte-level scan of the whole binary for the displacement `3c 01 00 00` finds exactly one
store to it (`0x73726a`, the `movl $0x1` above); every other hit is a jump displacement,
an immediate, or data. **`Run Version` is therefore `1` on every start of this binary.**
Source line numbers embedded in the log calls are `0xcef` (3311) for the first message,
`0xcfc` (3324) for the `USB Run` message, `0xd08` (3336) for `checkSOPVersion()`. **[E]**

`setEngType()` is called once, from `void AppEngineerModeEngine::initAppication()` (log
literal `0x989120`, line `0x2e4` = 740) at `0x74db11`, immediately before that function
returns. **[E]**

> **Correction to an existing note.** `evidence/engineering-mode-dev-activation.md` §3 states
> that when the executable path matches `/tmp/app/bin/AppEngineerMode` "the develop branch
> [is taken] and the SOP field ends up 0". The disassembly does not support that: the store
> is placed *before* the comparison, so it executes on both branches, and the `USB Run`
> branch contains only a `qDebug` and a `retq`. What the binary evidences is that 260128
> *recognises* the `/tmp` run and still reports SOP. The earlier document's §1, §2, §4–§10
> (launcher hook, DM staging literals, root-shell prerequisite) remain correct and are
> reused below.

---

## 2. What dev mode unlocks — the encryption/update-signing path

### 2.1 The QML component

`$ROOTFS/app/share/AppEngineerMode/qml/Update/AppEngineerMode_Encryption_Update.qml`
(entire file, 26 lines):

```qml
property bool statusFile: UpgradeVerInfo.checkUpdateFile(10)
Component.onCompleted:{ idEncryptionUpdateInfo.strSelectText = statusFile ? "Disable" : "Enable" }
...
strTitleText: "Encryption Update: "
strFirstButtonText:  "Enable"
strSecondButtonText: "Disable"
aliasFirstButton.onClickOrKeySelected:  { UpgradeVerInfo.disableUpdateFile(10); strSelectText = "Enable"  }
aliasSecondButton.onClickOrKeySelected: { UpgradeVerInfo.enableUpdateFile(10);  strSelectText = "Disable" }
```

Note the label/verb mismatch that is visible in the shipped source: the button labelled
**Enable** calls `disableUpdateFile(10)` and the button labelled **Disable** calls
`enableUpdateFile(10)`. The displayed state string is consequently inverted relative to
the verb. Whether the intended meaning is "Enable encryption update" or "the current
encryption-update state is Enable" cannot be settled from this file; see §2.3. **[E]** for
the literals, **[I]** for the semantics.

Sibling screen `AppEngineerMode_ScheduledUpateTest.qml` uses the same object with ids
`11` and `12`: `UpgradeVerInfo.checkUpdateFile(11)` → `Test Time Mode`, `(12)` →
`Controller Update`.

The menu entries live in `AppEngineerMode_UpdateLeftList.qml`
(`updateList` = `Force Update`, `Encryption Update`, `Scheduled Update List`,
`Scheduled Update Test`, `VESS Logging`, `ADP Logging`, `AMP Logging`;
`updateList_sop` = `Scheduled Update List`, `VESS Logging`, `ADP Logging`, `AMP Logging`
— i.e. the SOP model is the production model and simply omits `Encryption Update`). **[E]**

### 2.2 The C++ side — mostly absent from this build

`UpgradeVerInfo` is a QML context property registered in
`AppEngineerModeEngine::initAppication()`; the name literal is `0x986030`. The object is an
`UpgradeXMLParser` instance (context-construction list contains `new UpgradeXMLParser`,
`0x36079`), whose own logging strings enumerate its members:

```
void UpgradeXMLParser::runLoggingSecurityKey(int)   bool UpgradeXMLParser::clearLogFile(int)
void UpgradeXMLParser::checkrunCrypto()             void UpgradeXMLParser::startLogPopUp()
...
```

**None of `checkUpdateFile`, `enableUpdateFile`, `disableUpdateFile` exists anywhere in the
260128 `AppEngineerMode` binary** (byte scan; the only firmware component containing any of
those three names is `AppLogExtractor`). **[E]**

Consequence, and it matters for the QML-patch route: on this build, forcing the develop
menu by editing the QML reveals the `Encryption Update` row, but the screen's
`Component.onCompleted` binding calls into an object that has no such methods, so the row
cannot act on the marker. Anything that appears to work after a QML-only patch has to be
verified at runtime. **[I]** from the missing symbols.

The one binary that *does* implement it is `$ROOTFS/app/bin/AppLogExtractor`:

```
void AppLogExtractor_CopyLogThrd::disableUpdateFile(int)      (0x52f.. area, signature string)
rm -rf /update/disableEncryptionUpdate
rm -rf /update/test_scheduled_time
rm -rf /update/test_scheduled_controller
rm -rf /update/updateCompleteTime
```

The three marker paths line up one-for-one with the QML ids 10 / 11 / 12, and the same
three markers appear in `AppMPAutoTest` and `AppUpgrade`. That is consistent with a develop
build of `AppEngineerMode` carrying the same class, but it is **[I]** — the develop binary
is not in this package. **[E]** for the strings.

### 2.3 The marker and what the updater does with it

`/update/disableEncryptionUpdate` is the real switch, not the menu label. Existing
repository evidence (already reviewed at instruction level, not re-derived here):

- `evidence/appupgrade-update-trust.md`, `evidence/gen5w-public-operating-model.md` §
  "`disableEncryptionUpdate`: public claim and recovered correction": in the inner FUMO
  child, marker presence at process start flips a shared mode byte from `1` to `0` and logs
  `Unencryption Update`; the mode byte later short-circuits the navigation-map NUA signature
  gate (`evidence/corrections-log.md` C29, FUMO `0x128070`).
- The same marker is **explicitly ignored** on the SCOMO production path: literal at file
  offset `0x2867a4` in `$ROOTFS/app/bin/AppUpgrade`:
  `MASS_PRODUCT or PENETRATION Build mode -> Ignore disableEncryptionUpdate`.

So "disable signing" is accurate only for the FUMO route; it does not disable package
authentication in general. Recommendation: keep the existing wording in
`evidence/exploit-inventory.md:45-46` and `:459` (which already carries the route
qualification) rather than the unqualified public claim.

---

## 3. How it is activated on a real unit — candidates, ranked

| # | Mechanism | Status | Where |
|---|---|---|---|
| A | Shipped binary picks the develop state from its own path | **Refuted for 260128** | `AppEngineerMode` `0x737268` |
| B | A *develop build* of `AppEngineerMode` placed at `/tmp/app/bin/` and launched | **Evidenced container, dev binary absent** | `AppLauncher` `0x173c5`; `AppDMClient` literals |
| C | Build-time variant (the develop build simply contains a different constant) | **Inferred, best fit** | as above |
| D | MICOM / MP-test channel writes the marker directly (no UI dev mode) | **Evidenced** | `AppMPAutoTest` |
| E | QML patch on the rootfs | **Evidenced recipe, blocked in this build** | `evidence/wideopen-payload-and-persistence.md:182`; §2.2 |
| F | Persisted QSettings/D-Bus/persistent-DB dev flag | **Not found** | see §3.6 |
| G | Hidden tap gesture that toggles dev mode | **Not found** (gesture opens the PIN pad only) | §3.7 |

### 3.1 (A) Re-launch the shipped binary from `/tmp/app/bin` — refuted

`setEngType()` compares the process path to `/tmp/app/bin/AppEngineerMode` but the store to
`+0x13c` happens before the comparison and is always `1` (§1.3). Running the same file from
that path on 260128 changes a log line and nothing else. **[E]**

### 3.2 (B) The launcher's own `/tmp` override for app id 301 — evidenced

`$ROOTFS/app/bin/AppLauncher`, `0x173c5`:

```
173c5: leaq "/tmp/app/bin/AppEngineerMode" (0x46fee, len 0x1c)
173e1: call QFile::exists(QString const&)
173e6: testb %al,%al ; je 0x173f4
173ea: cmpl $0x12d, 0x20(%rbx)        ; app id 301
173f1: sete %al
17419: testb %al,%al
17420: jne 0x17ec0                    ; developer override
1745d: call QProcess::start(...)      ; normal path
...
17ec0: leaq "/tmp/app/bin/AppEngineerMode" (0x46fee, len 0x1c)
17ee9: call QProcess::start(...)      ; dev path
```

i.e. **if `/tmp/app/bin/AppEngineerMode` exists, launching engineering mode (id `0x12d`)
runs that file instead of `/app/bin/AppEngineerMode`.** This is a vendor dev-insertion hook,
and it is the only stock-UI-adjacent route to a develop build. **[E]**

### 3.3 (B) Who can put a file there — `AppDMClient` `VarUpgrade`

Literals inside `$ROOTFS/app/bin/AppDMClient`, all reachable from one staging function
around `0x80513`–`0x8069b`:

```
%1/VarUpgrade                  (0x17534d)
/tmp/app/bin                   (0x17535b)
%1/AppEngineerMode             (0x175368)
copy VarUpgrade                (0x17538b)
chmod +x %1                    (0x17539c)
getKeyFile() is fail!!!!       (0x1753a8)
VarUpdate hash fail!! :        (0x1753c1)
```

The same function builds `QString("%1/VarUpgrade").arg(<usb path>)` and
`QString("%1/AppEngineerMode").arg("/tmp/app/bin")`, then logs `copy VarUpgrade ` and
`chmod +x`. **Inferred [I]:** the intent is "a USB bundle's `VarUpgrade` directory carries
an `AppEngineerMode` binary; verify key/hash, copy to `/tmp/app/bin`, make it executable",
after which §3.2 makes the next engineering-mode launch the develop build. What is *not*
established: whether the USB route reaches this code without a signed package, what
`getKeyFile()`/`VarUpdate hash` actually verify, and whether the copy target is exactly
`/tmp/app/bin/AppEngineerMode` (the two strings are built adjacently, not proven to be
joined).

Also in the same binary, adjacent to `verifyKeyFile = ` (0x175377 region):

```
/update/showEncryptionMenu      (0x175b8b, ...)
```

### 3.4 (D) The MICOM / MP-test channel — writes the marker with no dev mode at all

`$ROOTFS/app/bin/AppMPAutoTest`, event handler `onNotifyMPAutoTestEvt(int, QByteArray)`
(receives MICOM events on `/Eng`, `com.lge.car.micom`):

```
] EVT_MP_ENCRYPTION_ENABLE_REQ
rm -rf /update/disableEncryptionUpdate
] EVT_MP_ENCRYPTION_DISABLE_REQ
touch /update/disableEncryptionUpdate
] EVT_MP_SECURE_CONSOLE_DISABLE_REQ!   → AT+SECURE_CONSOLE_DISABLE_RES:1
] EVT_MP_SECURE_CONSOLE_ENABLE_REQ!    → AT+SECURE_CONSOLE_ENABLE_RES:1
] EVT_MP_MODEM_PORT_FORWARDING_REQ!    → socat -d -d tcp-l:9997,reuseaddr,fork /dev/ttyUSB0,...
```

So the encryption gate can be turned off, and the debug console toggled, from the
manufacturing test channel alone — no engineering UI, no dev mode. **[E]** for the strings
and event names; **[I]** for how a party would inject those MICOM events (needs the MICOM
side or the D-Bus caller path; the MICOM protocol itself is out of scope here).

Related start-up plumbing in the same package:
`lib/systemd/system/mpauto.path` → `PathExists=/tmp/AppMPAutoTest/do_mpauto` →
`mpauto.service` → `etc/mpauto.sh`, which loops
`dbus-send --system --type=signal /Eng com.lge.car.micom.eng.NotifyMPAutoModeTestStartEvent`.

`/update/showEncryptionMenu` is written and removed by `AppDMClient` and `AppScomoDM`:
in `AppScomoDM` at `0xc1860`, both directions are present —
`QProcess::execute("rm -f /update/showEncryptionMenu")` (string `0x146020`),
`QProcess::execute("rm -f /update/disableEncryptionUpdate")` (`0x146068`), and
`QProcess::execute("touch /update/showEncryptionMenu")` (`0x146090`), with
`QFile::exists("/update/showEncryptionMenu")` / `.../disableEncryptionUpdate"` guards and
`sync()` on the removal path. The branch is selected by an integer derived from a
`-cv`-keyed lookup at `0xc18a5`–`0xc1907`; **I did not resolve that selector**, so the
direction is stated as "one branch creates it, the other removes it". **[E]** for the
commands, **[I]** for the condition.

**No component in this package reads `/update/showEncryptionMenu`**: the file is created and
deleted by the DM apps and consumed by nothing. `AppEngineerMode` never opens it (a scan of
its strings and of every QML file finds no `/update/` path at all). That is consistent with
the consumer being the develop build's `UpgradeVerInfo`, but it is **[I]**, and it is a
reason to treat "show the encryption menu" as an *unfinished or dev-only* mechanism rather
than a live feature of 260128.

### 3.5 (E) Rootfs/QML patch

`evidence/wideopen-payload-and-persistence.md:182` records the public patcher's edits:
`enterMenu == 21` → `enterMenu`, and `checkSOPVersion() ===` → `checkSOPVersion() !==`
(resp. `: false`). On 260128 that yields the menu but not a working toggle (§2.2), because
the engine lacks the three `UpgradeVerInfo` methods. **[E]** for the edits, **[I]** for
the outcome.

### 3.6 (F) No persisted setting, D-Bus method or build flag was found for this state

- No `QSettings`/persistent-DB key exists for it. The persisted keys in the engine are
  `APP_ENG_MODE_EMMCTEST_*`, `APP_ENG_MODE_SPLIT_SCREEN_ON_OFF`,
  `APP_ENG_MODE_AMP_DC_BLOCK_HISTORY`, `APP_ENG_MODE_CAMERA_RESET_HISTORY` — none related.
- No `getenv` import at all in `AppEngineerMode`, so no environment variable switch.
- No D-Bus method or signal named for SOP/dev was found; the SOP state is a local member.
- `/tmp` sentinels that do exist in the engine are unrelated to this gate:
  `/tmp/ENG_CAPTURE_ENABLE`, `/tmp/eng_limit_check.txt`, `/tmp/upgrade_msg_srv`.
- **[E]** for the searches above within `AppEngineerMode` and its QML; "not found" means
  not found by these searches, not proven absent everywhere.

### 3.7 (G) No gesture toggles dev mode

`AppEngineerMode_PinCodeKeypad.qml:40` reads `checkSOPVersion()` but only to choose the
post-PIN screen:

```qml
if(enterMenu == 21) {                       // PIN accepted
    if (bIsSOPVersion == true) { Global.setMainAppScreen("EngineerModeWarning", true) }
    else                       { Global.setMainAppScreen("EngineerModeMain",  true) }
}
```

`EngineerModeWarning` is `AppEngineerMode_EnterWarningPopup.qml`, whose `OK` button does
`Global.setMainAppScreen("EngineerModeMain", true)` — the same destination. So on 260128 the
SOP state does **not** block engineering-mode entry; it inserts a liability warning and
reduces menu content. This contradicts the claim recorded in
`evidence/attack-surface-prioritisation.md:129` ("an SOP check that fires before the PIN")
and the community note in `work/public-ui-research-20261022/laralbir/.claude/memory/engineering_mode_notes.md`
("`checkSOPVersion()` … EM bloqueado aunque el PIN sea correcto"). The gesture opens the
PIN pad; it does not switch the build state. **[E]**

### 3.8 A different "DEV" token exists in the updater, and it is a version-string class

`$ROOTFS/app/bin/AppUpgrade` (strings live in the embedded payload region of its `.rodata`):

```
###[scomo][%s:%d] %s() MP <-> DEV check    System Version : <%s>    Update Version : <%s>
###[scomo][%s:%d] %s() [FORCE_UPDATE_FUCTION_ENABLE] DEV -> MP
[%s] First Production force update.
[%s] Block SOP -> Dev version update.
[%s] m_prm5_product_version_mode : (%d)
```

This is a *build classification of the software version string* (`MP` = mass production,
`DEV` = development), used to decide whether a production unit may accept a dev-version
package — a different mechanism from the engineering-menu state, and the one that actually
policed "MP <-> DEV" transitions. **[E]** for the literals; the parsing rule itself was not
traced in this pass.

---

## 4. How SOP/production builds differ (the condition that hides the item)

The condition is exactly `checkSOPVersion() == true`, i.e. `Run Version == 1`, i.e. "the
shipped constant". Quoted check (`AppEngineerMode_UpdateLeftList.qml:57`):

```qml
model: (AppEngineerModeEngine.checkSOPVersion() === true)?updateList_sop:updateList
```

and the right-hand pane selects a parallel path list in
`AppEngineerMode_UpdateMain.qml:24`:

```qml
if (AppEngineerModeEngine.checkSOPVersion() === true) { var qmlPath = idLoadQmlList_sop.get(index).loadQmlPath }
```

Observations worth keeping:

- In SOP mode the item **labelled** `Scheduled Update List` loads
  `AppEngineerMode_Update_FromUSB.qml` (`idLoadQmlList_sop[0]`), which renders
  `AppEngineerMode_Update_History_ListView` — i.e. the SOP first row's label does not
  describe its content, and the update-history view is reachable from it. **[E]**
- `Update_FromUSB` also sits at `idLoadQmlList[2]` under the non-SOP list, so the same
  screen has two different labels depending on build state.
- The same gate trims `SystemConfig`, `Hardware`, `Diagnosis`, `Software`, `LogSetting`,
  and the regional `Dynamic` menus (35 QML files), and it suppresses
  `isWifi` / `isOtaTest` in `DynamicMainEU/AUS/RUS/NoModem*`
  (`property bool isOtaTest: (bIsSOPVersion===false) && AppEngineerModeEngine.getIsUNECE_Value()`). **[E]**
- The updater's *production* build additionally ignores the marker the dev menu would set:
  `MASS_PRODUCT or PENETRATION Build mode -> Ignore disableEncryptionUpdate`
  (`AppUpgrade`, offset `0x2867a4`). So even a develop-build menu whose toggle succeeds has
  no effect on a production/penetration SCOMO route — only the FUMO route consumes it.
  **[E]** for the literal; **[E]** via repository evidence for the routing.

---

## 5. Cheapest verification for each candidate

Read-only; none of these is a hardware recipe, and this project has verified none of them
on a unit.

| Candidate | Cheapest check | Cost / caveat |
|---|---|---|
| A (path switch) | Run `AppEngineerMode` twice in the QEMU projection — as `/app/bin/AppEngineerMode` and as `/tmp/app/bin/AppEngineerMode` — and read the `Run Version ` log line from the engine (`checkSOPVersion()` prints it). Static answer is already "both print `1`". | Minutes; decisive against A. Use the existing headless-launch pattern in `vm/repro/vendor-userspace-260128/appnavi-render-probe.sh` as the template; no new file is added by this report. |
| B (launcher override) | In the projection, place any executable at `/tmp/app/bin/AppEngineerMode`, then trigger app id `0x12d` through the launcher and check the child process path (`/proc/<pid>/exe`). | Minutes; validates §3.2 without needing a real dev build. |
| B (DM staging) | Trace `AppDMClient`'s `QFile::copy` call sites (`0x80513` region) to see the source argument, and run one USB-prepare in the projection with a `VarUpgrade` directory present. | Requires a staged USB image; medium. |
| C (dev build) | Compare the shipped `AppEngineerMode` against any other build's binary at offset `0x737268` (`c7 85 3c 01 00 00 01 …` vs a different immediate) — a five-byte diff answers it. | Cheapest decisive test of "is the constant build-time?", but needs a second build; none is in this repository. |
| D (MP channel) | In the projection, `dbus-send` the MICOM-side event that `AppMPAutoTest` maps to `EVT_MP_ENCRYPTION_DISABLE_REQ` and watch `/update/disableEncryptionUpdate`. Simpler: check `AppMPAutoTest`'s D-Bus introspection XML for the event entry point. | Minutes to read, but the event encoding is MICOM-specific. |
| E (QML patch) | Patch the two `checkSOPVersion()` comparisons in a scratch rootfs, open Engineer Mode → Update, select `Encryption Update`, and watch for a QML `TypeError` on `checkUpdateFile`. | Decisive for §2.2; must be a disposable copy, and it changes update-integrity posture of that image. |
| F/G | Already answered negatively by the searches in §3.6/§3.7. | — |

---

## 6. Security relevance, and what the register already covers

**What the state grants, if it can be reached.** Engineering mode as root plus a working
encryption-update toggle. The toggle only writes `/update/disableEncryptionUpdate`, and per
the recovered routing that marker changes the FUMO encryption mode and skips the
navigation-map NUA signature check — it is **not** a general package-signature bypass
(`evidence/appupgrade-update-trust.md`, `evidence/corrections-log.md` C29,
`evidence/exploit-inventory.md:459,491`).

**Why the activation surface is worth recording.** The three candidate entry points are all
"ordinary file placement, no signed configuration change":

1. `/tmp/app/bin/AppEngineerMode` + app id 301 (§3.2) — a launcher hook that prefers a
   writable-path binary.
2. `<usb>/VarUpgrade/AppEngineerMode` → `/tmp/app/bin` (§3.3) — a copy path in the update
   manager with key/hash checks whose coverage is unproven.
3. `EVT_MP_ENCRYPTION_DISABLE_REQ` (§3.4) — a privileged marker write driven by a
   test-channel event.

**Cross-references in the existing register (do not duplicate — recommend instead):**

- **V-042 — "Marker files under world-writable runtime paths trigger privileged actions"** is
  the right home for the *file-write→privileged-action* shape (cases 1–3). It already covers
  systemd path units over `/tmp`; the `/tmp/app/bin/AppEngineerMode` launcher override and
  the `/update/*` markers are the same class and are not yet named in it.
- **V-041 — "Engineering-mode keypad credential derives from static unsalted digests"** owns
  the menu-access question. Its "Validation needed on a unit" already asks whether the menu
  reaches update controls; §2.2 of this report sharpens that: on 260128 the *menu* can be
  reached but the *toggle* is not implemented in the shipped engine.
- **V-034 — "Update trust anchor sits on a writable root"** is the correct neighbour for the
  encryption/signing side: disabling encryption update and weakening the anchor compound.
- **V-008 / V-009** already own the console/credential material that any of these routes
  needs first (`etc/shadow.Global` `$6$…` root verifier; `etc/passwd.legacy` root `/bin/sh`
  vs `etc/passwd.secure` `/usr/sbin/nologin`; `/tmp/secure_console_disable`;
  `lib/systemd/esinit` fail-open ordering), and
  `evidence/dropbear-activation-and-authentication.md` already records that the shipped tree
  has `/etc/dropbear/authorized_keys` but **no** dropbear executable, socket unit or host key.
- The debug network the owner mentions is real but inert on its own:
  `lib/udev/rules.d/99-static-ip.rules` runs it only for a USB gadget NIC
  (`ENV{ID_VENDOR_ID}=="0424", ENV{ID_MODEL_ID}=="9e00"`, `KERNEL=="dbg*"`) and only if
  `/home/root/ip_setup.sh` exists — and `/home/root` ships empty. The script itself
  (`etc/ip_setup.sh`) sets `IP_ADDR="192.168.1.100"`, `NETMASK="255.255.255.0"`,
  `GATEWAY="192.168.1.1"`. This contradicts the earlier note in
  `evidence/engineering-mode-dev-activation.md` §9 ("Nothing invokes `/etc/ip_setup.sh`"):
  the *shipped* path `/etc/ip_setup.sh` has no caller, but the udev rule invokes a *different*
  path, `/home/root/ip_setup.sh`, if a copy is placed there. Recommend correcting that
  sentence rather than filing anything new.

**Recommendation (no new register entries).** Add the two evidenced literals
(`/tmp/app/bin/AppEngineerMode` in `AppLauncher`; `touch /update/disableEncryptionUpdate` in
`AppMPAutoTest`) as evidence links under V-042, note under V-041 that the shipped engine
does not implement the encryption toggle, and correct the `/etc/ip_setup.sh` sentence in
`evidence/engineering-mode-dev-activation.md`. Nothing here should be promoted until one
runtime confirmation exists — the cheapest being the path-switch test in §5 row A.

---

## 7. Bounds of this report

- Static analysis only. Nothing was executed, booted, flashed or modified. No VM image or
  `vm/repro` file was touched.
- One new file was created (`docs/engineering-mode/dev-mode.md`). No other file changed.
- Coverage: full `AppEngineerMode` disassembly (`objdump -d`), a byte-level scan for the
  `+0x13c` displacement, the whole `AppEngineerMode` QML tree (517 files), and targeted
  string/disassembly reads of `AppLauncher`, `AppDMClient`, `AppScomoDM`, `AppMPAutoTest`,
  `AppUpgrade`, `AppLogExtractor`. "Not found" always means not found by these searches.
- The develop build of `AppEngineerMode` is **not** in this package; every statement about
  what it contains is marked **[I]**.
- Unresolved items, named so they are not mistaken for settled: the `-cv` selector that
  chooses between creating and deleting `/update/showEncryptionMenu`; the exact semantics of
  the Enable/Disable inversion in `AppEngineerMode_Encryption_Update.qml`; whether
  `AppDMClient`'s `VarUpgrade` copy lands on `/tmp/app/bin/AppEngineerMode`; and how a party
  would inject `EVT_MP_*` events.

## A hidden 5-tap toggle that does exist, and what it actually does (2026-11-05)

The external triage recorded that "the exact `260128` image does not contain the claimed About-screen tap counter". That is right about **About**, and wrong about the image: there is a
five-tap counter in the shipped QML, just on a different screen.

`app/share/AppHomeScreen/qml_new2.0/NMode/PerformanceTimer/Q_NMode_PT_Lap_Main_Track.qml`:

```qml
MouseArea {
    anchors.fill: parent
    onClicked: {
        _clickCount++
        if(_clickCount >= 5)
            AppNModeModel.isNaviTestingMode = !AppNModeModel.isNaviTestingMode
    }
}
```

Five taps on the **N-mode lap-timer track** area toggle `AppNModeModel.isNaviTestingMode`. Reachable with touch alone, no PIN, no credential.

**What it does, measured from every use in that directory:** it changes the lap-timer's own presentation -

```qml
source:  AppNModeModel.isNaviTestingMode ? defineModel.co_btn_check_on_n : …   // a checkbox image
opacity: AppNModeModel.isNaviTestingMode ? 0.5 : 0                             // a translucent overlay
```

and nothing else. There is no path from this flag to a privileged action in the QML, and the flag lives in the application's own model.

**So: a real hidden toggle, and not a security finding.** It is recorded here because it is exactly the shape the external triage was looking for and had concluded was absent, and because
"the gesture exists but does something cosmetic" is a more useful answer than "the gesture does not exist".

## The About-screen gesture, checked exhaustively: it is not in this build's QML (2026-11-05)

The external project describes engineering-mode entry by tapping the software version 5-10 times on **Settings -> General -> About**, on a sibling platform. This project carried that
as an **inferred** stock entry vector all session. It is now checked against the whole shipped QML tree rather than a guessed path.

**Every QML file in `/app/share` containing a tap or click counter:**

```
/app/share/AppEngineerMode/qml/AutoTest/AppEngineerMode_GhostTouchTest.qml
/app/share/AppEngineerMode/qml/AutoTest/AppEngineerMode_TouchTest.qml
/app/share/AppHomeScreen/qml_new2.0/NMode/PerformanceTimer/Q_NMode_PT_Lap_Main_Track.qml
```

Three, and all three are accounted for: the two engineering-mode files are its own touch-test screens, and the third is the lap-timer toggle documented above. **The only thresholds anywhere in
that tree are `5` (the lap timer) and `0` (an initialiser).**

**Conclusion: the About-screen tap counter does not exist in this build's QML.** Not "we could not find it" - the tree was enumerated by pattern across every shipped QML file.

**What that does not rule out:** a handler implemented in C++ rather than QML. `AppHomeScreen` is a compiled binary and could bind a tap to a version label without any QML `MouseArea`. That is
the one thing static analysis cannot exclude, and it is settled by a single observation on a unit or in the projection: tap the version string repeatedly and see whether anything reacts.

So the stock vector narrows rather than closes: **the gesture as described on the sibling platform is absent**, and the remaining possibility is a C++-side equivalent elsewhere in the interface.

## And the binary has no entry point either: the About gesture is excluded twice over (2026-11-05)

The QML enumeration above left one possibility open - a handler in compiled code. That is now checked the same way.

**`AppHomeScreen` contains no engineering-mode entry point:**

```
grep -rniE 'engineer|engmode|secretMode|hidden|develop' app/share/AppHomeScreen/qml_new2.0/   -> no matches
strings app/bin/AppHomeScreen | grep -aiE 'engineer|secret|devmode|develop'                   ->
    /app/data/AppEngineerMode/dynamicmenu
    /app/data/AppEngineerMode/feedbackupdate
    virtual void AppHomeEngine::slotNotifyFactoryResetEngineerMode(int)
    virtual void AppEngineBase::slotNotifyFactoryResetEngineerMode(int)
```

The only engineering-related symbols are two **data paths** used by the engineering application itself, and a **notification slot** for a factory reset *while already in engineering mode*. There is
no "enter engineering mode" signal, slot, or property anywhere in the application that owns the settings and About screens.

**So on this build engineering mode cannot be entered from the touchscreen at all.** The gesture reported for a sibling platform is absent from both the QML and the compiled interface. The routes
that do exist are the ones this project has measured: an app-manager launch request for app id 301 pointing at a binary (as root, from the session bus), or the developer-path container.

This is the firmest negative in the engineering-mode section, and it is worth stating plainly because it is the opposite of what the field assumes: **the widely reported About-screen tap is not a
stock entry vector on this firmware.**
