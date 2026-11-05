# `ivi_controller` announces no layers or surfaces to a late client

Date: 2026-11-05. Injected our `ivi_place` (73,088 bytes, from `tools/uk_fw/ias_backend_soft/`) into the
clone at `/usr/bin/ivi_place`, then ran it 100 s after the power-on call with three applications up.

## What the compositor says

```
ivi_place: connecting to /run/user/root/wayland-0
ivi_place: bound ivi_controller (registry name 17, version 1)
ivi_place: announced by ivi_controller: 0 layers, 0 surfaces, 0 screens
ivi_place:   global ivi_application      present (version 1)
ivi_place:   global ivi_window_manager   present (version 1)
ivi_place:   global ivi_hmi_requester    present (version 1)
ivi_place:   global ivi_info_requester   present (version 1)
```

**The globals are all there; the controller simply announced zero objects** - while `AppHomeScreen` (2599),
`AppCamera` (2602) and `AppSetup` (3074) were running. Every `ivi_place <id> 4000 --visibility N` call then
reported only the layer's own defaults and changed nothing.

## What that explains

The composited output in that run was **129,844 bytes - the early background** - even though three
applications were alive. So the applications' surfaces are not on a visible layer in this projection, and
the screenshot is honest about that: it is showing what the compositor is actually displaying.

Everything this project has captured before therefore came from surfaces that happened to be placed, not
from a placement this project controlled.

## The likely cause, and the test that would settle it

Weston 1.10's `ivi_controller` sends layer/surface **creation notifications to clients bound at the time the
objects are created**. A client that binds later - which is what a 100-second `--list` is - receives none,
and so sees an empty world.

**So the next test is ordering, not plumbing:** bind the controller at **boot**, before the applications start,
hold the connection open, and let it observe the creations. If ids appear, visibility control becomes
available and a capture can finally be aimed at the home screen. If they still do not, `ivi_controller` is
not the right lever in this configuration and `ivi_window_manager` (the global the vendor's own
`ivi-window-manager.so` uses) is, which is what our `/usr/bin/ivi-wm` already speaks.

**Not established:** whether binding at boot reveals the objects. **Established:** a late binder sees zero
objects, and the composited output is the background even with the applications running.
