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
