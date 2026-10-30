# Navigation status: what is measured, and what still blocks the transition

Recorded 2026-10-29. Build `NE_E.EUR.S5W_L.001.001.260128`, x86-64, kernel
`4.1.27-abl`. Everything below is measured in the project's isolated QEMU VM unless
stated otherwise.

## Where the VM is

The vendor kernel boots, the recovered userspace runs, the authentic launcher chain
passes the standby and profile-confirm gates, and the genuine `AppHomeScreen` renders
with real tiles. AppNavi starts and can render genuine map pixels into its own
surface. **Home ↔ Navigation does not transition**, and this document records why the
remaining gap is narrower than it was.

## What is now measured rather than inferred

### 1. The EGL dimension ordering defect

An in-VM hardware-breakpoint observer attached to the authentic `AppCamera` inside the
real launcher chain and captured two stages of vendor `libEGL`'s software path, reading
the surface fields at `+0x2c` (width) and `+0x30` (height):

| Stage | Location | width | height |
| --- | --- | --- | --- |
| before the width cache | `libEGL+0x16f16` | **-1** | **-1** |
| immediately after `swrast_update_buffers` returns | `libEGL+0x16f1e` | **1920** | **720** |

Same surface pointer at both stages. So `swrast_update_buffers` populates the
dimensions *during* that invocation, while the copy path had already derived its stride
from `Width = -1`, yielding `-4` bytes. The stale-stride ordering defect is measured,
not deduced.

Scope: the affected code is the vendor's **Wayland software (swrast) display path**. The
binary contains separate constructors for the hardware paths
(`dri2_wl_create_window_surface`, `dri2_drm_create_window_surface`) which do not share
that vtable, so this evidence does not implicate the i965/i915 path. Tracked as I-001.

### 2. A Qt hide cannot produce the background notification

ApplicationManager only latches its navigation window byte on a **background** (BG)
window notification, and the compositor classifies a surface as BG only when both
dimensions are non-positive. `usr/bin/weston` retains DWARF for `weston_surface`, which
fixes the layout (`width` `0x68`, `height` `0x6c`, `width_from_buffer` `0x104`,
`height_from_buffer` `0x108`).

A null-buffer attach — what a Qt `hide()` becomes — zeroes the `_from_buffer` pair, but
the commit size block at `0x40f470` runs **before** that zeroing, so the surface keeps
its previous positive size and still classifies as foreground. A subsequent commit
without a new attach does not re-enter that block.

**Conclusion: a bare `hide()` is insufficient; a genuine transition to `0x0` is
required**, which matches the earlier Camera/Standby control that drove
`1926x753 → 0x0 → BG`.

### 3. Guest hardware breakpoints work

Execute breakpoints via `ptrace` on `DR0`/`DR7` function correctly under QEMU TCG with
this kernel: four slots arm and fire in program order, slot replacement works,
`DR4`/`DR5` are rejected, `DR6` reports per-slot bits and is clearable, single step
works, and debug registers are **per thread**.

One behavioural finding matters for any observer: **`PTRACE_DETACH` with a slot still
armed leaves the breakpoint live and kills the tracee.** Disarm, verify the readback,
then detach — that sequence is proven safe.

## The remaining blocker

A scoped adapter was built to drive AppNavi's parent surface to a real `0x0` configure:
an `LD_PRELOAD` interposer on `wl_surface_attach` that suppresses buffer attachment
once a hold condition is met. Two useful things were learned building it, and one
problem remains.

**Injection is solved.** The launcher's own interposer calls
`unsetenv("LD_PRELOAD")` when running as AppLauncher, so vendor children inherit a clean
environment and no `LD_PRELOAD` on the launcher command line reaches an app. Injection
must go through that interposer's `execve` hook, which rewrites `envp` for AppNavi
alone. A variant doing exactly that is included here
(`launcher_appnavi_navibg_preload.c`).

**The adapter loads.** With direct exec, AppNavi's own log records the adapter loading
with its hold parameters.

**AppNavi still never attaches a surface.** In both the full launcher chain and the
standalone render probe, AppNavi loads libraries and then produces no attach. The
manager reports drawing application `0` throughout. This is the blocker: there is no
surface for the compositor to classify, so neither the adapter nor the BG path can be
exercised yet.

## The interposer is cleared, and AppNavi paints nothing

The obvious suspicion was that an `LD_PRELOAD` wrapping `wl_surface_attach` was itself
breaking the client. A baseline run of the identical probe **without** the preload
settles it, and a control run with AppNavi **not launched at all** settles the next
question too:

| Run | AppNavi process | AppNavi log | screenshot SHA-256 |
| --- | --- | --- | --- |
| with the adapter | alive | 1 line (adapter load) | (not captured) |
| baseline, no adapter | **alive** | 0 lines | `b316a82a…0b9a83` |
| **control, AppNavi not launched at all** | absent | n/a | `b316a82a…0b9a83` |

Two conclusions follow. The adapter is **not** what stops AppNavi, because AppNavi is
equally silent with it removed. And the frame is **byte-identical with AppNavi absent**,
so AppNavi renders nothing at all: it is alive, silent, and contributes no pixels. It is
not rendering anonymously — it is not rendering.

That moves the blocker one level earlier. The compositor contract, the `0x0` hold and the
BG notification cannot be exercised until AppNavi actually paints, and the adapter is
irrelevant to that.

## Why AppNavi idles

An analysis of the alive-but-paints-nothing state found that the missing inputs come from
outside the process.

AppNavi links `libivi-platform-interface.so.1` directly, and that library resolves its ivi
surface **id only from the environment**, via `QT_WAYLAND_SET_SURFACE_ID` and its
`_FORCED` and `USE_PID_FOR_SURFACE_ID` variants. On the vehicle the value is injected by
`AppLauncher`, which also sets `APPID`. Verified here: the library is a direct `NEEDED` of
AppNavi and contains all three variable names. With the variable unset, the library enters
an **uncapped `blockingReadEvents` loop** waiting for an id reply — which matches the
observed symptom exactly: alive, silent, no surface, no crash.

Visibility is likewise external. `QWindow::setVisible()` is reachable only through
`IviShellSurfacePrivate::ivi_surface_visibility()`, i.e. only on `ivi_surface.visibility`
events, which the window manager emits only after `set_surface_visible` /
`set_visible_for_qtwayland` for that app's id. The VM fakes this trigger with a small
helper.

Ruled out: ApplicationManager's absence (a no-AppManager run still committed a
1920×720 buffer), every command-line flag in the current invocation, and `APPID` (read by
AppLauncher, not by AppNavi or libivi). AppNavi reads exactly one environment variable
itself: `MD_CONA40_ON`.

**Open point, and it is significant:** the VM logs show the ivi surface created under id
**30000** while the project's helper programmes **3000**. If real, visibility is requested
for an id that does not exist, which would explain byte-identical screenshots even in the
configuration believed to be working.

## A missing hardware adaptor: the gpio440 node

AppNavi's client log showed why it never paints. With Wayland debugging enabled it
connects, enumerates the registry (including the ivi application global) and then stops,
with the tail of the log a repeated read failure:

```
sh: /sys/class/gpio/gpio440/value: No such file or directory
```

That node cannot exist in this VM. `/sys/class/gpio` contains only `export` and
`unexport`, and writing `440` to `export` returns **EINVAL** because no gpiochip
registers that pin — consistent with the kernel log, where the GPS driver defers with
`-517` and never acquires it. The emulated board genuinely lacks a GPIO the firmware
expects, which is exactly the class of problem this project exists to solve.

**Adaptor:** a tmpfs mounted over `/sys/class/gpio` carrying an inert `gpio440` node.
With it, the `gpio440` errors disappear from AppNavi's log entirely — the first
demonstrated case here of a simulated hardware dependency unblocking a firmware startup
path.

It is necessary but **not yet sufficient**: surface creation appeared in one run and not
the next, so either a further dependency gates the render path or the timing is racy.
That is the current frontier.

## Where AppNavi actually stops

Counting protocol markers in AppNavi's own Wayland debug log — far cheaper than shipping log
text over the console — locates the stop precisely:

| Marker | Count |
| --- | --- |
| `wl_display` | 15 |
| `wl_registry` | 71 |
| `wl_compositor` | 7 |
| `wl_shm` | 11 |
| **`wl_drm`** | **0** |
| `ivi_application` | 7 |
| `wl_surface` / `create_surface` | 1 / 1 |
| **`ivi_application.surface_create`** | **0** |
| `attach` / `commit` | 0 / 0 |

So AppNavi binds the display, enumerates the registry, binds `wl_compositor`, `wl_shm` and
`ivi_application`, creates a `wl_surface` — and then never creates the ivi surface and never
attaches a buffer.

Two things stand out. **`wl_drm` is absent entirely**: the compositor runs headless with
pixman and offers no GPU buffer interface, and whether that causes the stop or merely
accompanies it is not yet established. And setting `QT_WAYLAND_SET_SURFACE_ID_FORCED` in
addition to the id produces a second `wl_surface` but still zero `surface_create`, so the
forced environment path alone does not clear it.

Ruled out along the way: gpio440 polling (now stubbed), the preload adapter (identical
without it), ApplicationManager presence, and the current command-line flags.

## Correction: wl_drm absence is not the gate, and a working harness is known

Two deductions from existing evidence change the picture recorded above.

**`wl_drm` cannot be the gate.** A prior successful run
(`work/vm/vendor-userspace-260128/runs/1792908755653936000`, retained milestone
`screenshot.sha256 88e8403d…b8b4cb`) used the *same* `weston-headless` pixman stack, with
**no ApplicationManager**, and reached `surface_create` for ids **3000, 30000 and 4903**
with 26 `wl_surface.attach` calls. So a client can create ivi surfaces and attach buffers on
this compositor without any DRM interface. The current stop is configuration-specific, not a
missing GPU buffer path.

It also settles the earlier 3000-versus-30000 puzzle: AppNavi creates **both** ids, plus
4903/4900 for the map widget. There was never a single expected id.

**A working harness exists and can be diffed.** That run executed
`/appnavi-valet-stub-probe.sh` together with `/appnavi-valet-stub-run.sh`, both of which are
still in the image. The gap between that harness and the current probe is therefore the
thing to find, and it can be found by diffing rather than by further debugging.

## Correction: AppNavi does create surfaces — my earlier stop point was a measurement error

The previous section concluded that AppNavi never calls `ivi_application.surface_create`,
based on marker counts from the **client's** `WAYLAND_DEBUG` log. That conclusion is
withdrawn. The client does not emit those requests in this build, so their absence there
proved nothing.

Counting the **compositor's** log for the same run gives the real picture:

| Source | `surface_create` | `ivi_surface` | `attach` | `commit` |
| --- | --- | --- | --- | --- |
| client log (`WAYLAND_DEBUG`) | 0 | 0 | 0 | 0 |
| **compositor log (`weston.log`)** | **2** | **7** | **2** | **2** |

So AppNavi does create ivi surfaces, does attach, and does commit. The reproduced recipe —
gpio440 adaptor plus the valet-status D-Bus stub plus the widget-linking helper — reaches
rendering. The earlier "alive but paints nothing, stops before surface creation" narrative
was an artefact of reading the wrong log, and everything downstream of it should be
re-read with that in mind.

What remains is therefore **not** surface creation but whether the frame becomes visible:
whether visibility is requested for the surface ids that actually exist, and on which plane.

## Next steps, in cost order

1. One instrumented boot with `QT_WAYLAND_SET_SURFACE_ID=3000` and no
   ApplicationManager: record which id the surface actually receives, then re-drive the
   visibility helper with *that* id. This settles the 30000-versus-3000 question directly.
2. Once AppNavi paints, re-run the `0x0` hold and look for the BG notification.
3. Only then decide whether a compatibility adapter is needed at all.

## Reproducing

The probe used for these runs is `tools/uk_fw/guest/appnavi_bg_probe.sh`; the interposer
is `tools/uk_fw/guest/navi_bg_0x0.c` and builds against the vendor's glibc:

```sh
zig cc -target x86_64-linux-gnu.2.25 -shared -fPIC -O2 -Wall -Wextra -Werror \
    -o navi-bg-0x0.so navi_bg_0x0.c
```

A musl-linked `.so` will not load into the vendor's glibc process. All experiments run
in snapshot mode with no NIC, and the canonical vendor image is never modified — runs
use an APFS copy-on-write clone with helper binaries injected by `debugfs`.

## Bounds

- Static evidence and VM measurement only; no hardware was used.
- The adapter has not been shown to produce a BG notification, because it has not yet
  had a rendering client to act on.
- Nothing here demonstrates a change to a vehicle head unit.
