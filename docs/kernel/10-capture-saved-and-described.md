# The frame is now saved — and, described honestly, it does not show a painted home screen

Date: 2026-11-06. Doc 09 left one hole: the frames were sized (`BYHAND_CAPTURE* bytes=…`) but not kept.
This run kept one, and looked at it as far as this session's tools allow.

## The capture, with size and identity

- **Saved to**: `work/vm/kbuild/painted-capture.png`
- **Bytes**: 87,944 (`BYHAND_CAPTURE1 bytes=87944`, matched exactly by the decoded file)
- **sha256**: `b51acb8b3537d3f52324faf18b38ef3b24b34d0124c35c9cf98558a88e40ca60`
- **Identity**: `PNG image data, 1024 x 768, 8-bit/color RGBA, non-interlaced`, magic `89 50 4e 47 0d 0a 1a 0a`
- **How it was kept**: the monitor's existing base64 block was redirected from the console to the
  file-backed `/dev/ttyS3` (`img-out.bin`), wrapped as `BEGIN painted <bytes> … ENDpainted`, base64 with
  no newlines. Decoded host-side to the exact byte count.

## What the pixels show (programmatic, since this session's model cannot render images)

- **~95 % black** (`#010001`); only 4.7 % of pixels are above the noise floor, 2.3 % bright.
- Non-black content is in two places: a small **text-like cluster in the upper-right-centre** (around
  x≈460–992, y≈180–340), and a thin **text-like band along the very bottom** (y≈620–660).
- Dominant colours beyond black: dark blue-grey `#5E6D76`, grey `#535B63`, light grey `#E5E5E5` and
  `#C6C2C1`, medium grey `#979CA2`, and a small amount of orange/coral `#C75F4C`.
- The trim bounding box of non-black content is `1024x516+0+252` — content in the bottom half only, the
  top ~252 rows are black.

So the frame is **not** a full-screen application: it is a mostly-dark compositor with sparse text-like
elements (upper-right and a bottom band), plus a trace of orange.

## The timing caveat that changes the reading

The capture was taken **after** the manually-relaunched AppHomeScreen had already died:

```
[apps-check] BYHAND_PID=2354
[apps-check] BYHAND_ALIVE=[no]          ← manual relaunch dead
… ~1 min later …
[apps-check] BYHAND_CAPTURE1 bytes=87944
```

The monitor keeps the first capture whose size is not 129,844 (the standby size) as `painted.png` — but
"not the standby size" is not the same as "the app's home screen". The app's own log says it connected and
drew (`Using Wayland-EGL`, `SCREEN_STATE: START DRAW`, `injectWidgetItemToAdvancedPage …
itemWidgetPlaceHolder FOUND`), but this saved frame was captured after that instance was gone, so what it
shows is a mostly-empty ivi-shell output, not a painted application surface.

## Verdict, in the project's own terms

- **Saved and identified**: yes — 87,944 bytes, sha256 above, at the path above.
- **Does the saved frame prove the app draws?** **No.** The app-draws claim in doc 09 rests on the app's
  own log (which is real evidence of connection and draw calls), not on this frame.
- **What would settle it**: capture **while** an AppHomeScreen instance is alive — the monitor already
  knows the timing (`BYHAND_PID=… alive`), so the capture must be moved to before the crash point (or the
  currently-alive instance `PIDS_FINAL AppHomeScreen=[2460]` captured instead of the dead 2354).

This is the honest state: the bytes are preserved, but the frame is a mostly-dark screen with text-like
content, and it does not by itself demonstrate a painted home screen.
