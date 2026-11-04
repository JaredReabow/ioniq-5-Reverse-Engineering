# Engineering-mode "DEV mode": what it is and how it activates

**Method:** static analysis of the shipped binary plus the shipped QML, from the EU 260128 extraction. No VM run was needed for the conclusion. Every claim below quotes the artefact it came from.

## 1. What the user sees is a build-state gate, not a mode switch

`/app/share/AppEngineerMode/qml/Update/AppEngineerMode_UpdateLeftList.qml` defines **two list models**:

```qml
ListModel{ id:updateList
    ListElement { name:"Force Update" }
    ListElement { name:"Encryption Update" }        <- the item in question
    ListElement { name:"Scheduled Update List" }
    ListElement { name:"Scheduled Update Test" }
    ListElement { name:"VESS Logging" } … }

ListModel{ id:updateList_sop
    ListElement { name:"Scheduled Update List" } … }
```

and every module picks between them with one call:

```qml
model:   (AppEngineerModeEngine.checkSOPVersion() === true) ? hardwareListSop : hardwareList
visible: (AppEngineerModeEngine.checkSOPVersion() === true) ? false : true
```

So "the SOP/production build hides Encryption Update" is exactly `checkSOPVersion() == true`. The development state is `checkSOPVersion() == false`.

## 2. What `checkSOPVersion()` actually does

At `0x737400` in `/app/bin/AppEngineerMode` (the function that logs the literal `bool AppEngineerModeEngine::checkSOPVersion()`):

```
73740d: movl 0x13c(%rdi), %r13d      ; read member field
7374fa: cmpl $0x1, 0x13c(%r12)       ; compare with 1
737503: sete %al                     ; return (field == 1)
```

**It returns true iff the int at `this + 0x13c` equals 1.** A sibling function at `0x7373c0` is a plain getter for the same field (`movl 0x13c(%rdi), %eax; ret`).

## 3. What sets that field — the activation mechanism

The only write to `0x13c` in the whole binary is at `0x737268`, inside the function that logs `void AppEngineerModeEngine::setEngType(...)`:

```
73725e: leaq 0x228(%rbp), %rsi            ; member QString at +0x228
737265: movq %r12, %rdi
737268: movl $0x1, 0x13c(%rbp)            ; default: SOP = 1
737272: call QString::trimmed()
...
737287: leaq 0x98518f(%rip), %rdx         ; literal string
737295: call QString::compare_helper(...)
7372a4: testl %ebp, %ebp
7372a6: je 0x7372e0                       ; equal -> DEVELOP branch
                                          ; not equal -> return with SOP = 1
```

and the literal at `0x98518f` is:

```
/tmp/app/bin/AppEngineerMode
```

So `setEngType()` compares a member string at `this + 0x228` — which the surrounding code populates from the process's own executable path — against **`/tmp/app/bin/AppEngineerMode`**. If it matches, the function takes the develop branch and the SOP field ends up 0; if it does not match, the field stays 1. The develop branch is also what emits the neighbouring literal `[setEngType] No Develop ...` for the non-matching case.

## 4. How to activate it on a real device

**Deploy the engineering binary at `/tmp/app/bin/AppEngineerMode` and start it from there.** The path itself is the switch; nothing else is consulted for this decision.

Caveats, stated plainly:

- The field is a **member**, so it is evaluated when `setEngType()` runs at start-up. Whatever starts engineering mode normally passes a real path such as `/app/bin/AppEngineerMode`; a copy under `/tmp/app/bin/` is what flips the build state.
- `/tmp` is volatile on this system, so this is a **per-boot** state, which is consistent with a development workflow rather than a shipped configuration.
- Not yet verified at runtime in the VM: the conclusion is from disassembly of the shipped binary, and it is strong because the comparison literal is the executable path and the only alternative branch is the SOP default. A runtime confirmation is one experiment (start the app from that path, read the update list).

## 5. What dev mode then unlocks

`/app/share/AppEngineerMode/qml/Update/AppEngineerMode_Encryption_Update.qml` (879 bytes):

```qml
property bool statusFile: UpgradeVerInfo.checkUpdateFile(10)
UpgradeVerInfo.enableUpdateFile(10);      // Enable / Disable buttons
```

"Encryption Update" is **file id 10** through `UpgradeVerInfo`, matching the user's screenshots: `Encryption Update: Disable` with Enable and Disable buttons.

## 6. Security relevance

Enabling this state requires only that the binary be **started from a writable path** (`/tmp/app/bin/`), not a signed configuration change. What it exposes is the ability to **disable update encryption/signing** through the engineering UI, and engineering mode is reported to run as root.

That is worth filing alongside the existing update-integrity entry (**V-034**, update signature trust anchor) rather than as a separate curiosity, because the two combine: a trust-anchor weakness matters more when the UI that disables update encryption is reachable by choosing where to launch a binary from. No new register entry filed on disassembly alone — recommend confirming at runtime first.

## 7. Related artefacts seen while reading

- `AutoTest/AppEngineerMode_AutoTest_Sop.qml`, `bool AppEngineerModeEngine::checkSOPVersion()`, `static void AppUtil::writeLogFunctionRunatSOP(QString)`, `ENG SOP LogFileName :` — the SOP state is used in several places, not only the update list.
- `/tmp/ENG_CAPTURE_ENABLE`, `/tmp/eng_limit_check.txt`, `/tmp/upgrade_msg_srv` — other `/tmp` sentinels in the same binary; none of them governs this gate.

## 8. Running it on a physical head unit

**Prerequisite: a shell on the unit.** This project has verified nothing on physical hardware — every step below is a procedure to try, not a tested recipe, and the access it assumes is itself
unproven here. The leads in the user's own notes are the candidates: an enabled debug network (`ip_setup.sh`, 192.168.1.100 via 192.168.1.1), a dropbear key installed on the unit, or the Linux root
credential recovered from `/etc/shadow`. Whichever is used, the command below must run **as root**, because engineering mode does.

**A copy is required, not a symlink.** The compared value comes from the process's own executable path, which on Linux resolves through `/proc/self/exe` and therefore follows symlinks. A symlink at
`/tmp/app/bin/AppEngineerMode` pointing at `/app/bin/AppEngineerMode` would resolve to the real path and still report SOP. The file must physically be at the `/tmp` path. *(This is inference from how
Qt obtains the application path, not a measurement; if the state does not change, test the symlink case to confirm it.)*

```sh
mkdir -p /tmp/app/bin
cp /app/bin/AppEngineerMode /tmp/app/bin/AppEngineerMode
chmod 755 /tmp/app/bin/AppEngineerMode

export XDG_RUNTIME_DIR=/run/user/root
export WAYLAND_DISPLAY=wayland-0
export LD_LIBRARY_PATH=/app/lib:/usr/lib:/lib
export QT_QPA_PLATFORM=wayland
unset QT_WAYLAND_SHELL_INTEGRATION

/tmp/app/bin/AppEngineerMode &
```

Notes that matter in practice:

- Start it **directly from a shell**, not through the vendor launcher: the launcher would pass the real `/app/bin/...` path and the check would pass as SOP again.
- `QT_WAYLAND_SHELL_INTEGRATION` is deliberately unset. This project measured that the vendor launcher appends `:ivi` for children, and that pre-setting it produces an invalid `ivi:ivi` value; the same
  failure mode would apply here.
- Engineering mode is reported to run as root, so the launch should be from a root shell; a non-root launch may fail before reaching the menu.
- If `/tmp` is small or mounted `noexec` on the unit, the copy will not run. `mount | grep ' /tmp '` answers that in one line; a `noexec` mount would need a different writable path that the check
  accepts — and the check names exactly one path, so this would then be a dead end rather than a workaround.

**What to look for:** `Engineer Mode > Update` should now list **Force Update**, **Encryption Update**, **Scheduled Update List**, **Scheduled Update Test**, VESS/ADP/AMP Logging. Selecting
Encryption Update should show `Encryption Update: Disable` with Enable / Disable buttons calling `UpgradeVerInfo.enableUpdateFile(10)`.

**To revert:** delete `/tmp/app/bin/` (or reboot — `/tmp` is volatile, which is why this is a per-boot development state). Nothing persistent is written by the check itself.

**Risks, stated plainly:** this is a research device procedure. Disabling update encryption from a root engineering UI changes the update-integrity posture of the unit, the action may be logged by the
update service, and the vendor launcher may restart the real `/app/bin/AppEngineerMode` behind the copy. None of those have been measured here.

## 9. Can a USB stick do this? No — and here is what the shipped system actually does

Checked directly, because the obvious question is whether the file can simply be carried in on a stick.

- **`usb-automount` only mounts and reports.** `/etc/usb-automount.conf` declares the hub and port topology; the binary's strings are about mounting, unmounting, MTP and reporting a mounted list over
  `com.lge.car.automount`. There is **no execution of anything from the device**, no `.sh` handler, no install path.
- **Nothing consumes the mount to run code.** The binaries that reference `/media/usb` are `AppUpgrade`, `MediaBrowser`, `AppMediaPlayer`, `AppLogExtractor` and the media scanner — i.e. update packages
  and media playback, not arbitrary executables.
- **Nothing invokes `/etc/ip_setup.sh`.** The script exists, but no unit and no binary references it: it must be run from a shell.
- **Console login units are present**: `console-getty.service`, `console-shell.service`, `getty@.service`. So the unit will hand a login prompt to anything that presents as its console.

**Therefore the honest answer: a stick gets files onto the unit, but nothing on the unit will run them.** Every route needs *code execution as root once*; after that the activation is the copy and
launch in §8. The routes, ranked by how much they depend on vendor behaviour:

1. **Serial console on the bench** (most reliable). Present as the unit's console, log in as root using the recovered credential or an installed dropbear key, then run §8. This depends on nothing
   except physical access to the UART.
2. **Debug network** — `192.168.1.100/24`, gateway `192.168.1.1` via `/etc/ip_setup.sh`. Strong lead, but the script has no caller, so it cannot be the first step unless something else enables sshd on
   that interface. Useful as a *second* step once a shell is obtained.
3. **Update package over USB** — `AppUpgrade` reads `/media/usb`, but update packages are signed, and disabling that signing is precisely what dev mode exposes: circular. The one non-circular variant is
   Engineering Mode's own **Force Update**, which may bypass version/signature checks; worth trying on a unit where engineering mode can already be opened, but unproven here.

**What this means practically:** the activation itself is trivial (six shell commands), and the access is the whole problem. No amount of preparing a stick substitutes for one root shell, and this
project has not verified any of the three routes on physical hardware.

## 10. Is there a stock-UI entry? Not for dev mode itself — but the launcher has a hook

Checked whether the unit can reach this from its own UI, without a shell.

- **`AppLauncher` prefers a copy at `/tmp/app/bin/AppEngineerMode`.** Disassembly at `0x173c5` loads the literal `/tmp/app/bin/AppEngineerMode`, calls `QFile::exists`, and the result is combined with
  `cmpl $0x12d, 0x20(%rbx)` — i.e. **app id `0x12D` (301)**. Only when the file exists *and* the launch is for that id does control jump to the `/tmp` branch. So the launcher has a deliberate
  developer-override hook: place a build there and the launcher runs it in preference to `/app/bin` when engineering mode is opened.
- **`AppDMClient` is the component that can put a file there.** It imports `QFile::copy(QString,QString)`, `QProcess::start/execute` and references `/tmp/app/bin`; its strings include
  `/update/usb/micom/…`, `/update/fota/install_param.txt`, OTA install prompts and — notably — **`DMC_DEV_INFO` and `TC_GET_DEV_INFO`**, i.e. it queries device/build information.
- **So the honest answer to "is there a dev-mode menu item": no.** The dev state is not a stored flag; it is *which file the launcher executes*. Nothing in the shipped UI writes
  `/tmp/app/bin/AppEngineerMode`, which is why no menu item can toggle it.
- **The one stock-UI leverage that exists** is the combination: if any update/installation path can deliver an app binary into `/tmp/app/bin` (AppDMClient is the candidate, and it already handles USB
  and FOTA installs), then simply opening engineering mode by its normal hidden gesture yields the development menu — no shell needed. That is **inference**, not a measurement: the DM copy path has not
  been shown to target `/tmp/app/bin`, only that it can copy and that the string appears in the binary.
- **Cheapest checks to settle it**, in order: (1) in the QEMU projection, place a copy at `/tmp/app/bin/AppEngineerMode`, open engineering mode by whatever the stock trigger is, and confirm the update list
  gains Encryption Update — this validates the launcher hook end to end; (2) disassemble `AppDMClient`'s `QFile::copy` call sites to see what source path feeds `/tmp/app/bin`; (3) if it is a USB upgrade
  path, determine whether it requires a signature.

**Practical bottom line for a stock unit:** the normally-quoted route to this state on these head units is the USB/FOTA app-update channel placing a developer build, *not* a settings menu. Absent that
channel, a root shell is required, and the six commands in §8 do it in seconds.

## 11. The three checks, and the verdict for a stock unit

**Check 1 — the launcher hook works (measured in the QEMU projection).** Copied the vendor binary to `/tmp/app/bin/AppEngineerMode`, then requested app id **301** from
`com.lge.avn.applauncher` with that path. The launcher returned success, launched it, and `readlink /proc/<pid>/exe` reported **`/tmp/app/bin/AppEngineerMode`** — i.e. the developer
override is real and takes effect. The menu itself could not be read visually because the engineering screen renders through the same striped path as the home screen (blocker 1), and in a second run
the app had exited before the check; so this establishes that the *launch* side works, not yet that the update list gains Encryption Update. That final step needs either blocker 1 solved or an
input-injection route to the Update page.

**Check 2 — `AppDMClient` does copy, but not to where it matters.** It has two `QFile::copy` call sites, alongside `QFile::exists` and `QFile::remove`, and references `/tmp/app/bin`. The source
path is not visible in the immediate call-site neighbourhood (the arguments are prepared earlier), so the *target* directory of those copies is **not established**. Do not treat "DM copies into
`/tmp/app/bin`" as proven.

**Check 3 — USB updates are signed, and that is the point of the toggle.** `AppUpgrade` performs real signature work: `mbedtls_rsa_pkcs1_decrypt`, `PKCS#1 sig. verify`, `RSA key validation`,
`CheckEncryptFile` and the message **"this file is not encrypted"**. So an update package must be encrypted/signed to be accepted, and the engineering control the user photographed —
`Encryption Update: Disable` — is precisely what relaxes that requirement. That is the security-relevant pairing: the toggle exists to allow unencrypted updates, and it is what a technician would
flip to install an unsigned build.

### Verdict

- **There is no stock-UI or USB-only route into the dev state**, because the dev state is not a setting: it is *which file the launcher executes*. Nothing shipped writes
  `/tmp/app/bin/AppEngineerMode`; the launcher only *prefers* it if something else has put it there.
- **Engineering mode itself** is reachable from the stock UI — `AppSetup` references `AppEngineerMode`, and the surrounding signals (`NotifyKEYPressCounterEvent`, `registertouchkey`,
  `btnTouchPad`) indicate a touch/key sequence in the Setup application. That is the entry a service technician uses, and on a production build it shows the reduced (SOP) menu.
- **So the intended developer workflow is a deployment, not a gesture:** a build is pushed to `/tmp/app/bin` by a deployment tool or update channel (the launcher hook and `AppDMClient`'s copy
  machinery are the two halves of that workflow), and then the ordinary engineering-mode entry runs the development build.
- **The practical consequence for a stock unit:** either a **signed/encrypted update package** that performs the deployment, or **a root shell** to do it by hand (§8). A button combination alone cannot
  create the file, and the physics of the check make that a permanent property rather than a gap in our knowledge.

### What is still worth doing, cheapest first

1. Find the exact sequence in `AppSetup` that requests app id 301 — the stock engineering-mode entry. That is a concrete disassembly task with a definite answer, and it is what a service technician
   uses.
2. Confirm the menu difference once blocker 1 is solved (or via input injection), to close check 1 properly.
3. Trace `AppDMClient`'s copy arguments backwards to establish the source directory, which would show exactly which update channel feeds the developer path.
