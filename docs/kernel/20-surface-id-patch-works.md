# The surface-id patch works: the home screen is composited (light frame, left panel, title bar)

Date: 2026-11-06. Doc 19 showed the launcher never assigned AppHomeScreen a surface id. The one-entry
patch in the launcher's `(appId, surfaceId)` table was applied, and this run proves it is read for the
home screen.

## The patch (fourth substitution)

- Binary: `/app/bin/AppLauncher`, 407,720 bytes. One entry, repurposed (the entry for `appId 113`, which
  never appears in any log — `grep -c 'AppID : 113'` = 0, and 73 also 0; 113 chosen as the media-player
  variant least likely to be used).
- Offset `0x475e8`: `71 00 00 00 7a 08 00 00` (appId=113, surfaceId=2170) →
  `0b 00 00 00 20 08 00 00` (appId=11, surfaceId=2080). **2080 is the surface id this project has
  observed for the home screen all along**, so the value is evidence, not a choice.
- sha256: `c8d6d56b…c4a84268` → `24f054dc…a232283`.

## The direct proof the table is read for AppHomeScreen

The launcher log now contains, for the first time in this session:

```
AppID : 11, Set to QT_WAYLAND_SET_SURFACE_ID=2080    (21:12:09.569, 21:12:54.917, 21:13:26.436, …)
```

Before the patch there was no `AppID : 11` surface line at all (doc 19).

## The surface exists and is placed

```
SURFACES=[Surface id(30000)|Surface id(2080)|Surface id(1001)|Surface id(1002)]
APP_SURFACE_ID=[2080]
IVI_WM_RC=0   (bound ivi_window_manager, placed)
```

## The frame changed class — light home, not standby

`CAP_30s/60s/90s` are **120,452 bytes** (saved `work/vm/kbuild/painted-light-home.png`, sha256
`dcf1ed0e…73e16`), 1920×720. Pixel histogram: ~85 % black, **a large white region (`#EEEEEE`,
~108 k px = the left panel)** and **blue (`#256D9B`/`#2B526B`/`#3686B8` = the title bar)**. The coarse
map shows a full-width blue bar on top and a white full-height left panel — the light day-theme chrome.
This is a different class from the two prior frames (129,844 = early background; 144,501 = dark standby
face).

## What remains

The app is **still** in the deregister loop — pid at the four captures runs 3010 → 4085 → 4700 → (empty)
— so the placed instance (2503) was replaced after the call, and the frame is the light chrome, not yet
the fully-populated 16,062-byte layout with Battery/Range placed. The surface-id patch removed the
"no surface" blocker; the preload-deadline race (doc 13) is the remaining one. Both are now named.

## Files

- `work/vm/kbuild/painted-light-home.png` — the light-frame capture (120,452 bytes).
- `work/vm/kbuild/boot44-patched.log` — the run.
- `work/vm/kbuild/ws/partimg-build/AppLauncher.patched.bin` — the patched launcher (sha256 above).
