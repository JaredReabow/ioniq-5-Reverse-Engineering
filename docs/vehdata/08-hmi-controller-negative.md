# Adding `hmi-controller.so` to the ivi-module list: negative, and the clone is restored

Date: 2026-11-05.

## Why it was tried

The effective compositor configuration is **not** `/etc/xdg/weston/weston.ini` - that is a symlink to
`/tmp/weston.ini`, and `/etc/install_westonPngLogo.sh:73` creates it:

```
ln -sf /etc/xdg/weston/weston_${LCD_TYPE}.ini /tmp/weston.ini
```

So the file that decides the shell's behaviour is **`/etc/xdg/weston/weston_1920.ini`**, and its ivi module
list was:

```
ivi-module=ivi-window-manager.so,ivi-controller.so
```

`hmi-controller.so` **ships in the image** (183,720 bytes) but was **not loaded** - and in weston 1.10 that
module is what creates and manages the HMI layers that application surfaces get placed on. It also names a
shell user interface that is **missing from the image entirely**:

```
ivi-shell-user-interface=/usr/lib/weston/weston-ivi-shell-user-interface    MISSING
```

(and, separately, `/usr/libexec/weston-keyboard` is missing too, which is the respawn storm in the log.)

## What happened

The module was added to the list, the image rebuilt, and the authentic path booted. **The application stack
never came up**: at +105 s, `pidof AppHomeScreen`, `AppCamera` and `AppSetup` were **all empty**, and the run
logged **no mention of `ApplicationLauncher` or `AppHomeScreen`** at all. The compositor itself did load its
modules, so this is not "the compositor died" - it is "the launcher chain did not start".

**And I cannot yet say whether `hmi-controller.so` loaded**, because my own capture truncated the module
list at 300 characters and it cut off exactly there. That is a measurement defect, not a result.

## What this establishes

- **`hmi-controller.so` in the ivi-module list is not a free win.** Combined with the missing user-interface
  binary, that configuration does not produce a working stack in the projection.
- The **mode of failure is the launcher chain, not the compositor** - which is a different failure than every
  other compositor experiment in this project.
- The clone has been **reverted** to the known-good `ivi-module` line so it stays usable.

## Next, properly

1. Boot once with `hmi-controller.so` added and capture the **whole** module list and the compositor's own
   errors, unfiltered - the truncation above is the reason this run cannot be judged.
2. Check what `hmi-controller.so` needs from the missing `weston-ivi-shell-user-interface` before concluding
   either way; a module that expects a client that is not shipped may be waiting on it.
3. If the HMI layer path is unavailable in this projection, say so plainly and stop treating "place the
   surface" as a solvable problem here - the honest alternative is to accept the background-only output and
   document that the projection cannot present the vendor UI, which is a different claim from "the UI does
   not render".

---

## 9. The unfiltered run: init fails, and the compositor goes with it

Rerun with the module added and the log captured **whole** (no truncation this time):

```
[00:00:05.057] Loading module '/usr/lib/weston/ivi-window-manager.so'
[00:00:05.235] Loading module '/usr/lib/weston/ivi-controller.so'
[00:00:05.320] ivi-controller: No ivi-input-module set
[00:00:05.322] Loading module '/usr/lib/weston/hmi-controller.so'
[00:00:05.334] Failed to initialize hmi-controller
```

And at +110 s:

```
home= cam= setup= launcher= mgr= weston=        ALL EMPTY
```

**`hmi-controller` fails to initialise and the compositor exits with it.** So the previous run's "the launcher chain did not start" was really "the compositor was already gone at 5.3 seconds". That is a cleaner finding than the one I recorded, and it is the kind of thing the unfiltered capture was meant to settle.

## 10. Correction: the shell user-interface is present, just not where the ini says

I wrote that `/usr/lib/weston/weston-ivi-shell-user-interface` is "missing from the image". It is missing **at that path**. The binary exists:

```
/usr/libexec/weston-ivi-shell-user-interface      PRESENT
/usr/libexec/weston-screenshooter                 PRESENT
/usr/libexec/weston-simple-im                     PRESENT
/usr/libexec/weston-desktop-shell                 PRESENT
/usr/libexec/weston-keyboard                      MISSING   (the respawn storm)
```

So the ini's `ivi-shell-user-interface=` points into `/usr/lib/weston/`, where it does not exist, while the real client lives in `/usr/libexec/`. Whether that mismatch is *why* init fails is unproven, but it is a concrete, checkable discrepancy in the vendor's own configuration.

## 11. The lead that matters: "permission denied" is in the module's own strings

`hmi-controller.so` contains the literal string:

```
hmi-controller failed: permission denied
```

That is a **permission** failure path compiled into the module, and this image enforces SMACK (V-056) on a **permissive** policy (`smack_setup.sh` switches to permissive when `optUNECE=0`, and the measured value is 0). The audit log is live - the same boot logged `lsm=SMACK ... action=granted subject="_" object="Log::dlt"` for the DLT daemon.

**So the next measurement is specific and cheap:** run once with `hmi-controller.so` enabled and grep the audit stream for `action=denied` entries naming `weston` or the compositor's comm. If a denial appears, the module's init failure is explained and the fix is a rule, not a code change. If none appears, the failure is a missing/bad configuration input and the `/usr/libexec` versus `/usr/lib/weston` discrepancy is the first thing to correct.
