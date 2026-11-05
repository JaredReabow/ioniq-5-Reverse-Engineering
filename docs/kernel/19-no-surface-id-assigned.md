# The launcher never assigns AppHomeScreen a surface id — "why no surface", answered

Date: 2026-11-06. Doc 18 narrowed the blocker to "the surviving instance creates no surface". One read
of the launcher log settles it.

## The read

`grep QT_WAYLAND_SET_SURFACE_ID` over the launcher log (boot 38, saved at
`work/vm/kbuild/applauncher-stdio-crash.log`):

```
AppID : 12,  Set to QT_WAYLAND_SET_SURFACE_ID=2080   (AppCamera, ×several relaunches)
AppID : 30,  Set to QT_WAYLAND_SET_SURFACE_ID=3000   (AppOSDManager)
AppID : 110, Set to QT_WAYLAND_SET_SURFACE_ID=2110   (AppMediaPlayer)
AppID : 17,  Set to QT_WAYLAND_SET_SURFACE_ID=1030   (NotificationManager)
```

**There is no such line for `AppID : 11` (AppHomeScreen).** Every other managed app gets a Wayland
surface id from the launcher; AppHomeScreen never does. That is the direct answer to "why no surface":
the app is launched without the surface id the ivi-shell needs to composite it, so nothing it draws
appears, and the frames stay the 129,844-byte background.

## Which of the two readings it is

This is the **first** of the user's two cases — *no surface was ever created*, not *a surface that
existed for 3 ms and was photographed in the gap*. There is no point in the log where AppHomeScreen is
given a surface id, before or after the deregister. So the thread ends where doc 13 pointed: the
application is not demonstrably broken; the projection's remaining gap is a vendor launcher/controller
timing-and-assignment behaviour under TCG — a named limitation, not an unexplored fault.

## The whole path, in one table

| step | state | evidence |
|---|---|---|
| matching kernel source builds | ✓ | doc 01, `4.1.27-abl` bzImage |
| `/dev/dri/card0` (bochs-drm) | ✓ | doc 02 |
| native 1920×720 mode | ✓ | doc 11 (bochs_kms patch) |
| vendor `drm-backend.so` binds `card0` | ✓ | doc 05 |
| wayland socket (seat fix) | ✓ | doc 08/09 |
| app connects, Wayland-EGL, `START DRAW` | ✓ | doc 09 |
| app chrome painted (standby face) | ✓ | doc 11 (144,501 bytes, blue bar) |
| app surface composited after power-on | ✗ | doc 18 — no surface, no surface id |
| laid-out home screen (Battery/Range) | ✗ | docs 17/18 — never reached |

## The five instrument-caused failures, in my own words

Five times this session, an instrument or a premise looked like a property of the vendor's system and
was not. **The process-wide `LD_PRELOAD`** (the pixman shim) broke every non-pixman process it leaked
into, and its `undefined symbol` looked like a compositor fault. **The placement tool** (`ivi-wm`) was
the thing that made a surface visible in the first place, so "no frame" was once "not placed". **A
truncated log** (the 2,500-char monitor line) read as "no error" when the error was just past the cut.
**`CONFIG_DRM_VIRTIO_GPU`** is a symbol that does not exist in 4.1.27, and two builds chased it before
that was measured. **The input module's `return -1`** on an empty seat list tore the whole compositor
down and looked, from outside, like a display failure. Each of the five was found by reading a log or a
symbol table, not by reasoning about the UI.

## Files

- `work/vm/kbuild/applauncher-stdio-crash.log` — the launcher log.
- `docs/kernel/18-combined-no-surface.md` — the run this explains.
