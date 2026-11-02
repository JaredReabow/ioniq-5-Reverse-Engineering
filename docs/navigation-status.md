# Navigation status: what is measured, and what still blocks the transition

Recorded 2026-10-31. Build `NE_E.EUR.S5W_L.001.001.260128`, x86-64, kernel
`4.1.27-abl`. Everything below is measured in the project's isolated QEMU VM unless
stated otherwise.

## Latest full-chain status

The authentic launcher chain reaches Home. In the latest AppLauncher-owned AppNavi
run, the navigation engine initializes and creates parent surface `3000` plus widget
surface `4903`; genuine map pixels have also been verified in the widget surface.
The Home-to-Navigation transition is still incomplete: ApplicationManager receives
`notifyNaviLaunched[5] window[0]`, remains at current/drawing AppID `35/11`, and does
not reach `APP_NAVI` (`30`). A return request restores visible Home.

The current boundary is the genuine launch/window contract, not process startup or
surface creation. Do not patch status `5`, force the window byte, or synthesize a
success callback. The experiment sections below preserve intermediate hypotheses and
corrections; later corrections supersede earlier negative conclusions. See
[HANDOVER.md](../HANDOVER.md) for the consolidated run and evidence hashes.

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

## Earlier probe: the scoped adapter had no surface to act on

This intermediate probe was superseded by the later corrected AppNavi surface and
visibility measurements below. A scoped adapter was built to drive AppNavi's parent
surface to a real `0x0` configure:
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

The observer's commit observation used to be described as best-effort, which made a
bypass indistinguishable from silence. It now proves the interposition at run time:
`wl_surface_commit`'s wrapper compares its `dlsym(RTLD_NEXT, …)` resolution with the
global-scope definition and reports `verdict=observed|shadowed|unverified|idle` with
`complete=0/1` at unload. `unverified` means commits were **not observed** and must
never be read as "no commit happened". `tests/test_navi_bg_observer.py` pins both
outcomes with native clients: the linked client must report `interposed=1` and
`complete=1`, while a client that commits through a `dlopen` handle must report
`verdict=unverified` and `complete=0`.

That proof also runs inside the recovered guest, and it exposed a wrong assumption.
The vendor `libwayland-client` (1.10, `0.3.0`) exports **no `wl_surface_commit` or
`wl_surface_attach` symbol at all** — they are header inlines over
`wl_proxy_marshal`, which the guest probe reports as `PROBE surface_symbol=0`.
Wrapping those symbols could therefore never observe a vendor client's commit; the
object that ships here now interposes `wl_proxy_marshal`, decodes the call from the
interface's own signature (validated against `wl_proxy_get_class`, so no struct
layout is trusted blind) and forwards once through `wl_proxy_marshal_array`.

With that hook, a real client inside the guest produces
`null-attach surface#0 target=1 … attach=1`, `commit-after-null-attach … commit=1`
and `verdict=observed commits=2 interposed=1 complete=1`, all asserted by
`tests/test_vm_vendor_e2e.py`. The chain also reaches the authentic launcher stack
(`ApplicationManager`, `UserProfileManager`, `AppOSDManager`, `AppHomeScreen`) and
starts `AppNavi` with the observer mapped into it.

AppNavi's own hide path is still unobserved, and this is what the guest actually
shows. The observer hook is live inside the process (`navi-bg: loaded pid=…`,
`marshal … interposed=1`) and the client maps `libEGL.so.1.0.0`, `libGLESv2.so.2.0.0`
and `libwayland-egl.so.1.0.0` (`APPNAVI_RENDER_MAPS=12`), yet no `wl_surface` attach or
commit reaches it (`OBSERVER_NAVI_LINES=0` over 120 seconds). Other vendor clients do
reach the compositor in the same run: weston's debug log records
`WESTON_CREATE_SURFACE=40`, hundreds of `get_registry` calls, and commits from surfaces
that are not AppNavi's. The cause is not established; the runs that recorded surfaces
`3000`/`4903` used the project software EGL from `/opt/software-egl*` (absent from these
extracted trees, which carry only vendor `libEGL`/`libGLESv2` and the `i965` DRI driver)
and drove the standby/profile-confirm transition this chain does not.

### Reconciling with the retired shim

CHANGELOG 1.62.0 retired this approach, and the reasoning there is correct for the
point it tested: an external object **cannot** forward an unknown `va_list` to a
variadic callee, and `wl_proxy_marshal_array` is reached by a direct intra-library call
that never traverses the PLT. Both statements still hold, and neither is used here.

The wrapper that ships now never forwards through the variadic entry to relay a
message: it *receives* the call, reads the arguments typed from the interface's own
signature table, and passes a rebuilt `union wl_argument[]` to
`wl_proxy_marshal_array` — a non-variadic call it makes itself, so no `va_list`
survives the boundary. The variadic entry is used only for the last-resort replay of a
signature that cannot be read, where every wire argument is an integer slot, and
`tests/test_navi_bg_observer.py` covers that path separately.

Two facts from that work are worth carrying forward rather than rediscovering:

- `|'f'|` in a Wayland signature is `wl_fixed_t` — a 24.8 fixed-point **integer**,
  not a C `float` — so it needs no floating-point handling. A test now pins it.
- A hook that never fires is indistinguishable from a quiet client. The object
  therefore reports `interposed=1|0` plus a verdict at unload, and a client that
  bypasses the link chain is reported as `unverified`, never as "no commit happened".

## Decompiled confirmation of the input gap

The claim that `ivi-shell.so` has no pointer or keyboard focus implementation was
recorded from behaviour; it is now also decompiled evidence. With JDK 21 and Ghidra
12.1.4 (`tools/uk_fw/decompile.py --select ALL`) the module yields 400 functions, of
which 120 reference imported `PTR_*` slots. References to `wl_keyboard`, `wl_pointer`,
`notify_key` or `notify_button` number **zero**. What the shell does contain is
activation and input-panel plumbing — `terminate_binding(weston_keyboard *…)` at
`0x10a110`, `click_to_activate_binding(weston_pointer *…)` at `0x10a480`,
`touch_to_activate_binding` at `0x10a410`, and the input-panel bind/show/destroy
family — plus `weston_seat_get_keyboard` at `0x103260` as an imported stub the panel
path uses. See
[`vm/evidence/vendor-userspace-260128/ivi-shell-input-audit.txt`](../vm/evidence/vendor-userspace-260128/ivi-shell-input-audit.txt).

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

## Visibility: the requests are correct, the id is not

Counting visibility markers in the compositor log for the valet-stub run:

| Marker | Count |
| --- | --- |
| `surface_create` | 2 |
| `ivi_surface` | 7 |
| `set_surface_visible` | **16** |
| `set_visible_for_qtwayland` | **16** |
| `request_fg` | **8** |
| `set_surface_layout` | 16 |
| **`ivi_surface_visibility` events** | **0** |
| surface id actually logged as created | **30000** |

So visibility is not being neglected: the helper issues sixteen `set_surface_visible` and
sixteen `set_visible_for_qtwayland` calls across eight iterations, plus eight foreground
requests. Nothing is missing on the request side.

What is missing is the **binding**: not one `ivi_surface.visibility` event is emitted, and
the only surface id the compositor logs as created is **30000**, while the helper programmes
visibility for **3000**. The foreground requests therefore never resolve to the surface that
exists, which is exactly consistent with the manager continuing to report drawing
application `0`.

This converts the 3000-versus-30000 puzzle from a suspicion into the leading explanation,
now supported by the visibility event count rather than inference.

### The environment value does not control the surface id

One run settles it. Launching AppNavi with `QT_WAYLAND_SET_SURFACE_ID=0` still produces a
surface with id **30000**:

| `QT_WAYLAND_SET_SURFACE_ID` | surface id created |
| --- | --- |
| `3000` | **30000** |
| `0` | **30000** |

So the variable does not determine the id in this path at all; 30000 is what the client
creates regardless. The helper, meanwhile, programmes visibility for 3000. The mismatch is
therefore not a configuration slip on our side but a hard difference between what AppNavi
creates and what the helper addresses, and it fully explains why sixteen visibility requests
produce zero visibility events.

**The fix is to address the id that exists.** Either rebuild the widget-linking helper with
parent 30000, or establish where 30000 comes from and make it configurable. Rebuilding the
helper is the cheaper of the two and follows directly from this measurement.

### Retargeting the helper to 30000 did not fix it either

The widget-linking helper was rebuilt with parent id 30000 instead of 3000 and run through the
same harness. Result: `set_surface_visible`=16 and `request_fg`=8 as before, and
**`ivi_surface.visibility` events still 0**.

So addressing the id that exists is **necessary but not sufficient**. The hypothesis is not
disproven — the mismatch was real — but on its own it does not produce visibility, which
means at least one more condition governs whether the window manager emits a visibility event
for this surface. Candidates, in cost order:

1. The helper's requests are not reaching the same `ivi_window_manager` instance that owns the
   surface (its log has been empty on these runs, which is suspicious in itself).
2. Visibility is emitted only after a further state change on the surface — a later commit, a
   layout change on the plane, or a `set_surface_visible` after the first buffer arrives.
3. The 30000 the compositor logs is not the parent surface the helper should address, and the
   real parent id is simply not being logged.

The next cheap discriminator is (1): confirm the helper actually connects and its requests are
accepted, by capturing its own output and the compositor's response to its first call.

### Correction 2: visibility IS granted, and this harness has no ApplicationManager

Counting `ivi_surface_visibility` returned zero, and I read that as "no visibility events".
Wrong again, and for the same reason as before: the wrong string. The compositor's own log
contains

```
[  5408.381]  -> ivi_surface@7.visibility(1)
[  5409.602] ivi_surface@7.visibility(1)
```

i.e. the surface **is** made visible, twice, with value 1.

Two further facts matter as much:

- This harness deliberately runs **no ApplicationManager** (it is the "no-appmgr" probe). Its
  manager query therefore returns nothing, and an empty answer here says nothing about the
  manager's view. The "manager reports drawing application 0" observation came from a
  *different* configuration.
- The retained milestone screenshot from this same family of runs shows **genuine map pixels**.

So the standalone harness already reaches visible authentic AppNavi rendering. The number that
was supposed to prove failure was an artefact of my own grep, twice over.

**What this changes:** the remaining gap is not rendering, not surfaces, not visibility and not
the surface id. It is **integration**: the full launcher chain starts AppNavi through
AppLauncher with different environment and ordering, and does not reproduce this harness's
ingredients.

**Next step:** carry this harness's three essentials into the full chain — the gpio440 adaptor,
the valet-status D-Bus boolean stub, and the widget/visibility helper — and see whether the
manager then latches the navigation window.

## Physical HID: mouse moves nothing, keyboard ignored

Reported behaviour: plugging a mouse shows a pointer that never moves; a keyboard is ignored
entirely. This is not a missing driver. The stack accepts the devices and then has nowhere to
deliver them.

**What is present.** `/etc/xdg/weston/weston_1920.ini` selects `backend=ias-backend.so` and
`shell=ivi-shell.so`, and contains **no `[input]` section at all**. The backend is capable:
`ias-backend.so` imports `weston_seat_init_pointer`, `weston_seat_init_keyboard`,
`weston_seat_init_touch`, `notify_motion`, `notify_key`, `notify_button`, `libinput` and
`libevdev`. Udev is stock apart from a Hyundai rule that only symlinks the i2c touchscreen to
`input/touch`.

**What is missing.** `ivi-shell.so` contains **no pointer or keyboard focus implementation** —
no `weston_pointer_set_focus`, no `wl_pointer` or `wl_keyboard` handling of any kind. The only
keyboard logic in the window manager is about the on-screen keyboard *surface*:
`is_keyboard_surface`, `check_and_show_keyboard`, `set_keyboard_surface_layout`. That is a
virtual keyboard, not physical keys.

**Why the pointer appears but never moves.** The backend creates a pointer seat when a mouse is
added, and weston renders the cursor — but moving the cursor and giving surfaces pointer focus
is *shell* work, which desktop-shell does and ivi-shell does not. The cursor is drawn once and
stays where it was placed; clicks have no focused surface to land on.

**Why the keyboard is silent.** No keyboard focus is ever assigned to a surface, so key events
are consumed by the compositor and dropped. The caps-lock LED briefly changing on plug-in is
the kernel's LED state on device open, not evidence that keys are being read.

**Conclusion.** The vendor's IVI shell is touch-first by design: it manages surfaces and planes,
not user input. Physical HID reaches Linux and the compositor and stops there. Hardware keys on
a real vehicle do not come through this path at all — they arrive via the vehicle bus.

**Consequence for this project.** Input must be simulated at the **touch** layer, which is what
the GUI does accept, rather than by presenting a mouse or keyboard. That is already the
direction of the `weston_vm_input` and `qt_input_observe` helpers.

**How to confirm in the VM.** Run the same `weston` + `ivi-shell` combination, attach a synthetic
pointer, and observe that the backend reports the device while no client receives
`wl_pointer.enter` and the cursor never moves. That is a short experiment with the existing
input helpers, and it would convert the symbol-level conclusion above into a runtime fact.

## Next steps, in cost order

1. **Cheapest first — driver only, not the library.** The vendor `libEGL` contains its own
   Wayland software path (see the `-4`-byte stride defect above), so it may accept a
   `swrast_dri.so` placed on `LIBGL_DRIVERS_PATH` while the vendor `libEGL.so.1` stays in
   place. What was tried instead — binding a whole Mesa 17 `libEGL` over the vendor one —
   makes AppNavi exit before its first attach, and that substitution is now opt-in
   (`vendor_rootfs.py run --software-gl`). The untested variant is the vendor library with
   only the Mesa driver, which would also bypass the `-4` stride defect only if the vendor
   build accepts that driver ABI.
2. In the full AppLauncher-owned run, capture AppNavi's actual `visibleChanged(false)`
   call together with the selected QtWayland/EGL backend and the parent surface's
   configure, attach, and commit events. The current static hide-path analysis is not
   proof that the null-buffer path executes at runtime.
3. Compare that lifecycle with the retained positive-size Camera/Standby control that
   reaches `0×0` and `slotNotifyBGInfo`; determine whether AppNavi naturally emits the
   same background notification. Do not force a BG state or window byte.
4. Keep tracing the authentic `notifyNaviLaunched[5] window[0]` contract: establish
   the meaning and producer of each field and what legitimately advances manager state
   from `APP_NAVI_LOADING` (`35`) to `APP_NAVI` (`30`).

## Reproducing

The probe used for these runs is `tools/uk_fw/guest/appnavi_bg_probe.sh`; the interposer
is `tools/uk_fw/guest/navi_bg_0x0.c` and builds against the vendor's glibc:

```sh
zig cc -target x86_64-linux-gnu.2.25 -shared -fPIC -O2 -Wall -Wextra -Werror \
    -o navi-bg-0x0.so navi_bg_0x0.c
```

zig comes from `pip install --user ziglang`; a musl-linked `.so` will not load into the
vendor's glibc process. All experiments run in snapshot mode with no NIC, and the
canonical vendor image is never modified in place: `tools/uk_fw/vendor_rootfs.py`
assembles its own ext4 image and injects the helpers with `debugfs`, so a run always
starts from the same bytes.

## Bounds

- Static evidence and VM measurement only; no hardware was used.
- The adapter has not been shown to produce a BG notification, because it has not yet
  had a rendering client to act on.
- Nothing here demonstrates a change to a vehicle head unit.
