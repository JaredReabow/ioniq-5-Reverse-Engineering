# Surface identity from the compositor's own log, and two methods that were wrong

Date: 2026-11-05. Log pulled off the guest through the base64 channel (4,130 bytes, saved verbatim as
`evidence/vm-compositor/weston-real.log-2026-11-05.txt`).

## 1. The surfaces, by creation time and size

```
00:00:06  Surface id(30000)  W(1920) H(720)     early-background
00:01:55  Surface id(2080)   W(1926) H(753)     the application's main surface
00:02:39  Surface id(1000)   W(1926) H(123)     a bar, not a window
00:02:42  Surface id(1001)   W(1926) H(108)     another bar
00:03:04  Surface id(1006)   W(1926) H(753)     a window created later
00:03:16  Surface id(1007)   W(1926) H(753)     another
00:03:17  Surface id(1004)   W(1926) H(753)     created LAST
```

The three `1926x753` windows are **different applications**: in that run `AppHomeScreen` (2583),
`AppCamera` (2391) and `AppSetup` (3046) were **all running at once**.

**So surface id is not a stable name across runs.** 1004 was created last here and is not necessarily what
it was in an earlier run - which is exactly how I came to analyse a camera window and call it the home
screen.

## 2. `weston-screenshooter` captures the whole output, not a surface

Every capture in a run returns the **same byte size** whatever surface id was placed beforehand
(120,528 and 120,528 in the run above; 22,057 and 22,057 before that). That is not "the surfaces look the
same" - it is **the tool compositing the entire output each time**.

**Consequence:** "capture each non-layer surface" was never a thing this tool could do. The id passed to
`ivi-wm` controls **placement**, and the screenshot then shows **whatever is on top**. To photograph a
specific application, it has to be brought to the front - which is a *visibility* operation, not a capture
operation.

This also retires a phrase this project has repeated for days ("the background's surface is created last,
so do not capture the newest surface"): the background here was created **first**, and the newest surface
was a real application.

## 3. A defect in the projection worth naming

The log is dominated by a respawn storm:

```
launching '/usr/libexec/weston-keyboard'
compositor: executing '/usr/libexec/weston-keyboard' failed: No such file or directory
input_method disconnected, respawning...
```

**`/usr/libexec/weston-keyboard` does not exist in the image**, and the compositor respawns it forever.
That burns CPU in a software-rendered, 4-vCPU guest and it perturbs every timing measurement this project
takes, including the 90-second settling time.

## 4. The next measurement

`ivi_place` already speaks `ivi_controller` and can set a surface's **visibility** and a layer's render
order (see `tools/uk_fw/ias_backend_soft/ivi_place.c`). The next run should:

1. set the **other** `1926x753` surfaces invisible,
2. set surface **2080** visible on its layer,
3. capture - and confirm from the log that the surface created at `00:01:55` was the one on top.

Only then is a capture attributable to the home screen, and only then can the CAN shim's effect on the
widgets be judged at all.
