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
