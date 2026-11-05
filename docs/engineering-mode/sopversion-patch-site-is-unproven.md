# The SOPVersion patch site is unproven (correction, 2026-11-05)

The plan for opening the development menu was: patch one immediate so that
`model: (checkSOPVersion() === true) ? updateList_sop : updateList`
selects the development list. The site chosen was `0x73726e` in
`app/bin/AppEngineerMode`, whose bytes are:

```
737268: c7 85 3c 01 00 00 01 00 00 00    movl $0x1, 0x13c(%rbp)
                          ^^ ^^         <- the immediate that was patched 01 -> 00
```

**Reading the surrounding instructions shows this is not the SOP decision:**

```
737259: callq QDebug::~QDebug()
73725e: leaq  0x228(%rbp), %rsi
737268: movl  $0x1, 0x13c(%rbp)        <- a boolean stack local set during string handling
737272: callq QString::trimmed()
737287: leaq  0x24df01(%rip), %rdx
```

It sits in the middle of QDebug logging and a `QString::trimmed()` call, and stores into a **stack
slot** (`0x13c(%rbp)`), which cannot be the engine's SOP state - that would be a member. So the
immediate is a local flag in unrelated code, and the earlier claim that patching it selects the
development list was **never established**.

This matches the only runtime observation we have: the patch was injected, and the check afterwards
returned `ENG=` empty - which I had recorded as "effect unobserved" when the likelier reading is
"wrong site".

## How to find the real one

`bool AppEngineerModeEngine::checkSOPVersion()` is a `Q_INVOKABLE`, so its address is not stored
next to its name. The name appears twice:

```
0x987d40  "bool AppEngineerModeEngine::checkSOPVersion()"     the style/pretty name
0x99e24e  "checkSOPVersion"                                   the stringdata entry
```

The route is Qt's own dispatch: find `AppEngineerModeEngine::qt_metacall`, locate the `switch (_id)`
case whose constant corresponds to the `checkSOPVersion` entry in `staticMetaObject`'s method table,
and the function is in that case body. Patching the *return* there (`xor eax,eax` before the
epilogue, or flipping the conditional) is a defensible target; patching an arbitrary `movl $1` is
not.

## What this changes

Nothing about the VM's current blocker - engineering mode has still not been opened in the projection,
which is the gate in front of this question either way. It changes what I will claim when it is
opened: **the menu will show the production list unless the real decision is patched**, and the
one-byte patch recorded earlier should be treated as unproven until that is done.
