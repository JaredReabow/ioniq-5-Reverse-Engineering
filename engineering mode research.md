# Engineering mode research

Status: **partial, with the PIN and entry path documented.** This records the known
engineering-mode entry methods and PINs, what the recovered firmware shows about the
PIN check, and whether the older "update AppNavi from engineering mode" capability can
be brought forward to the `260128` build.

Build analysed: EU Gen5W Linux `NE_E.EUR.S5W_L.001.001.260128`, x86-64, kernel
`4.1.27-abl`. Static analysis of the recovered rootfs. No VM run, no hardware.

The owner has approved publishing the PINs and entry methods recorded here.

## 1. Entry methods and known PINs

### Standard Gen5W (S5W_L) — Linux/Qt unit

**Gesture.** Settings → General settings → System info → Manual. On the Manual
screen, tap the **left** side — the panel with the QR code and text, not the vehicle
image on the right — as if a nine-key number pad were overlaid on it, in the order
**3, 2, 8, 9, 6, 5**. The eight-digit PIN keypad then appears.

**PIN (engineering mode, 8 digits):** `19480717`

This value was reported by the owner as accepted on a UK-origin 2021 IONIQ 5, and is
recorded in `evidence/owner-engineering-mode-pin-observation.md`. It is user-reported
vehicle evidence, not an independently captured screenshot. The build installed on
that car was later identified from a USB log as `NE_E.EUR.S5W_L.001.001.250604`, so
the code's acceptance does **not** prove it works on `260128`; the `260128` package is
only comparison evidence.

### Dealer mode is a different, lesser mode

Dealer mode and full engineering mode are distinct surfaces with different entry and
different codes. Two public references disagree on the details:

- Oviradio (page dated 2026-10-01) lists a dealer-mode PIN plus a **rotating set** for
  full engineering mode, and states that current Gen5W passcodes work on the `250604`,
  `251204` and `260128` EUR builds.
- laralbir (June 2026 analysis) states that Standard Gen5W uses a **short fixed PIN**
  while Premium AVNT uses an 8-digit rotating PIN, and that `MASS_PRODUCT` builds from
  about November 2021 fail a separate SOP check **before** the PIN pad, so they cannot
  enter without a rootfs patch.

Both may be right about different menus or variants. The rotating values themselves
are not recorded in this repository, and individual rotating codes stop working.

### SOP gate — now corroborated in code

The SOP-gate claim was previously single-source. The recovered `260128` binary
contains a real method:

```
bool AppEngineerModeEngine::checkSOPVersion()
```

That is direct code-level support for a build gate that runs separately from the PIN.
It does not by itself prove the gate fails on `MASS_PRODUCT`, but it confirms the
mechanism the claim describes exists in this build.

## 2. What the firmware shows about the PIN check

- The keypad is `app/share/AppEngineerMode/qml/AppEngineerMode_PinCodeKeypad.qml`,
  1,087 lines. At line 391 it calls the native method:

  ```
  enterMenu = AppEngineerModeEngine.checkPassWord(changeLockNum)
  ```

  The QML then branches on the **return value** — `21` and `11` are menu selectors,
  not entered PINs. The entered digits are assembled from the keypad, with whitespace
  stripped at line 104.
- Lockout machinery exists alongside it: `startBadPassword()`,
  `setBadPasswordInfo(QString, QString)`, `getBadPasswordDiff()`,
  `cleartBadPasswordInfo()` and `getEnterPasswordCnt()`. The keypad displays a
  wrong-password timer, so repeated failures are rate-limited by design.
- The binary is stripped of its symbol table but retains 111 C++ signature strings of
  the form `AppEngineerModeEngine::<method>`, which is how these methods were
  identified. `checkPassWord` itself appears only as a Qt meta-object name, so its
  implementation still has to be located by cross-reference.

### The PIN is not a literal in the shipped filesystem

A full scan searched **408,412 files across all five extracted firmware components**
(`mango-rootfs`, `appnavi`, `new-gui`, `mango-rwdata`, `update`) and expanded **444
nested archives** (gzip and tar members included). Zero hits for the 8-digit value in
any of five encodings: ASCII, UTF-16LE, uint32 little-endian, uint64 little-endian, and
hex.

So the accepted PIN is **not stored as a constant** anywhere in these components.
Consistent explanations, none yet proven:

1. `checkPassWord()` derives or transforms the expected value at runtime rather than
   comparing against a literal.
2. The expected value lives outside these components — a separate partition, a
   persistent data area, or state delivered by the MCU.
3. The reported PIN is valid for the owner's installed build and is not this package's
   value.

Point 3 is the most likely single explanation, because the owner's unit was identified
as `250604` while this analysis is of `260128`.

## 3. Where the entry gesture is handled

The reported gesture does not appear in the Manual screen's QML:

- `Screen_Manual.qml` ships in three UI variants under
  `app/share/AppMediaPlayer/<variant>/screens/setting/`. The `qml_new2.0` and
  `qml_genesis` variants contain **no `MouseArea` and no `onClicked`** (240 and 280
  lines).
- `MP_Main.qml` references `SCREEN_ID_MANUAL` only as a screen identifier.

The tap sequence is therefore consumed natively, most plausibly by an input filter that
sees press coordinates before the QML scene does.

Separately, **no binary in the image contains the literal string `AppEngineerMode`**,
so the application is started through the launcher's application registry (path or id
table) rather than by a hard-coded name in the caller. That matches the launcher's
documented id scheme, where AppNavi is id 30 and the standby client id 10.

## 4. Updating AppNavi from engineering mode

### What the older capability was

The repository's exploit inventory records the mechanism precisely: the older
engineering mode exposed **Engineering Mode → Config → "Update AppNavi from USB"**, and
the public `navi_extended` project used exactly that page to run a script from
`/media/usb` under the AppNavi identity. That was a vendor feature, not a
vulnerability. June–October 2026 participants report that newer firmware removes or
patches the page.

### State on `260128`

**Not established.** The engineering screen does carry an `SW Update` tile, but what it
invokes, what it authenticates, and whether it can target a single application rather
than the whole unit have not been traced in this pass.

### Gates that decide portability, in cost order

1. Does `SW Update` accept a per-component payload at all, or only a full signed
   package? (`AppUpgrade` handles the signed unit-level TE2 envelope; see
   `evidence/eu-ota-container-structure.md`.)
2. If it accepts a component, what authenticates it — the unit-level signature, a
   per-app signature, or an integrity list?
3. Would a replaced `AppNavi` then pass the launcher's own executable inspection? The
   launcher rejects a modified `AppNavi` before a process is created, which is
   documented from earlier experiments in this repository.
4. Is the application area writable from that context, or on a read-only or verified
   mount?

A payload that satisfies (1) and (2) but fails (3) still will not run, so gate 3 is the
cheapest decisive check and should be settled before any further work.

## 5. Next steps

1. Cross-reference the `checkPassWord` meta-object string in the binary to find its
   implementation, then read the comparison and the `21`/`11` return paths.
2. Read `checkSOPVersion()` to see what it actually tests and whether `260128`
   `MASS_PRODUCT` satisfies it.
3. Locate the launcher application registry entry for the engineering app.
4. Trace the `SW Update` tile to the binary that performs the update — this answers
   gate 1 directly.

## 6. Bounds

- Static analysis only; nothing was executed, booted or modified.
- The gesture and PINs come from community reporting plus one owner report, not from
  this analysis. Which exact menu the accepted PIN opened on the owner's car was never
  captured, and remains an open question in the original record.
- "Not found" means not found by the searches described, with file and encoding
  coverage stated — not proven absent from the firmware.
