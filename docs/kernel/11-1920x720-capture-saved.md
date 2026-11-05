# 1920×720 capture saved — mode fixed, frame described, but still not the full home screen

Date: 2026-11-06. Doc 10 said the frame was 1024×768 (bochs default) and captured after the app died.
This run fixed the mode and the channel, and kept a 1920×720 frame.

## What was changed (two variables, both necessary)

1. **Mode.** `-device VGA,edid=on,xres=1920,yres=720` did nothing, because bochs-drm 4.1.27 calls
   `drm_add_modes_noedid()` and never reads EDID, and 1920×720 is not in the standard mode list. So I
   patched the kernel (`work/vm/kbuild/linux-4.1.27/drivers/gpu/drm/bochs/bochs_kms.c`): `defx/defy`
   defaults → 1920/720, and `bochs_connector_get_modes()` now adds a CVT 1920×720@60 mode and marks it
   preferred. Rebuilt (`bzImage` 3,980,448 bytes, sha256 `86aafb71…abb1d`). Verified:
   `/sys/class/drm/card0-Virtual-1/modes` now reads
   `1920x720 1600x1200 1680x1050 … 1024x768 …` — **1920x720 first**.
2. **Channel.** `/dev/ttyS3` (img-out.bin) is smack-relabelled `System::GPS` by the vendor's udev rules
   in the authentic boot, so the monitor's write was denied (`smack_inode_permission action=denied …
   name="ttyS3"`, `chsmack` could not relabel it). `/dev/ttyS2` (dbg-out.txt) is writable, so the
   capture base64 now goes there (`BEGIN painted <bytes> … ENDpainted`). Decoded host-side by byte
   offset, exact match.

## The capture

- **Saved to**: `work/vm/kbuild/painted-1920x720.png`
- **Bytes**: 144,501 (`BYHAND_CAPTURE1 bytes=144501`, decoded exactly)
- **sha256**: `59253cf623d3124b5e3c1100cc5e8c9ed89cbec78867e32122491e270f6ddce3`
- **Identity**: `PNG image data, 1920 x 720, 8-bit/color RGB`, magic `89 50 4e 47 0d 0a 1a 0a`

## What the pixels show (programmatic; this session's model cannot render images)

- ~**93 % black** (`#010001`).
- A **full-width blue bar along the very top** (a blue gradient: `#256D9B`, `#1B5071`, `#3686B8`) — a
  title/status bar.
- In the **upper-centre**, a block of **large anti-aliased text** (a heading) with a smaller text line
  above and below it (a crop of x780–1140, y200–470 shows bold glyphs ~50 px tall plus a thin
  breadcrumb line above).
- Grey text tones (`#C8CACD`, `#737B83`, `#48545F`); no orange accent this time.

So it is a **1920×720 frame with a blue title bar and large text**, not the light day-theme home screen
with a left panel, vendor logo and Battery/Range widgets (the `docs/vm/38` reference is 16,062 bytes and
flat; this is 144,501 bytes of gradient + anti-aliased text on black). The mode is now right — the
layout spans the full width — but the *content* is a text screen, not the widget grid.

## The timing is still not catching the painted home screen

- The new **alive-capture** (added before any kill, `ALIVE_AT_CAPTURE pid=… alive=yes`) produced
  `ALIVE_CAPTURE_FAILED` — `weston-screenshooter` wrote no PNG at that early point (the compositor/app
  is CPU-starved then; it only succeeds ~1 min later).
- `BYHAND_CAPTURE1` (the frame above) is still from **after** the by-hand relaunch died
  (`BYHAND_ALIVE=[no]`), so what is on screen is a launcher-restarted instance (`PIDS_FINAL
  AppHomeScreen=[2438]`) in a text state.

## One caveat that belongs in the record, from the same boot

`/dev/ttyS2` also carries the S4 SCOMO probe output, which shows the `invalid object` fault is **not**
universally gone — it is app-specific:

```
S4_HEAD=[ … |libEGL warning: DRI2: failed to open swrast (search paths /usr/lib/dri)|failed to
          initialize EGL display|wl_display@1: error 0: invalid object 18| ]
```

`scomo-test` still dies with `invalid object 18` — but that probe does **not** set
`LIBGL_DRIVERS_PATH=/opt/software-egl18/dri`, so its EGL init fails first (`/usr/lib/dri`), a different
failure than AppHomeScreen's. Doc 09's claim was about AppHomeScreen (`invalid object 19`), which
connects and draws; this is a separate app and a separate thread.

## Honest bottom line

The frame is saved, at the right 1920×720 resolution, and shows a blue title bar with large text — but
it is **not** the fully-painted home screen. The next one-run fix is to make the alive-capture succeed
(longer settle, or retry the screenshooter) so the frame is taken while the launcher-started app is
painted, and to look at that frame before any further claim.
