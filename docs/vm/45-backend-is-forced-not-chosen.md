# The headless backend is forced, not chosen

Date: 2026-11-05. This bounds what "as close to stock as reasonable" can mean for the display, and it was
established with two static reads and no boot.

## What the vendor ships, and what we have been using

```
/usr/lib/weston/drm-backend.so        536,992 bytes
/usr/lib/weston/fbdev-backend.so      348,776 bytes
/usr/lib/weston/gl-renderer.so        202,016 bytes
/usr/lib/weston/ias-backend.so        644,064 bytes     <- the vehicle's own backend
/usr/lib/weston/headless-backend.so    92,400 bytes     <- what this projection runs
```

The projection runs the **least faithful** of the five: `headless-backend` with `--use-pixman`, plus a
solid-fill shim. The vehicle runs `ias-backend` with a GPU.

## Why the faithful one cannot be used, and why the next best cannot either

`ias-backend.so` needs the vendor's IAS/GPU interface, which QEMU does not provide. The obvious fallback is
`drm-backend.so` on a QEMU-provided DRM device - except:

```
CONFIG_DRM=y
CONFIG_DRM_KMS_HELPER=y
CONFIG_DRM_I915=y                       the only DRM driver this kernel has
CONFIG_DRM_BOCHS is not set
CONFIG_DRM_QXL is not set
CONFIG_DRM_VIRTIO_GPU                   not present in the configuration at all
CONFIG_FB_VESA                          not present in the configuration at all
```

**The vendor kernel's only DRM driver is `i915` - the Intel GPU in the real unit.** QEMU cannot present an i915
device, and the two drivers that *would* work under QEMU (bochs, virtio-gpu) are **not built**, with
`CONFIG_DRM_VIRTIO_GPU` not even present in the config.

So there is **no DRM device path in this projection**. `drm-backend.so` ships and cannot be used. `headless` is
therefore **not a preference - it is the only backend that runs**, and the same is true of the software renderer
path that follows from it.

## What this means for the failing start-up sequence

The previous note concluded that the vendor's own start-up path is running against a backend it was not written
for. **This measurement shows that cannot be fixed by switching backends inside QEMU.** The options are:

| option | what it needs | fidelity |
|---|---|---|
| rebuild the vendor kernel with `CONFIG_DRM_VIRTIO_GPU` | a 4.1.27 tree matching `vendor.config` - **this project has no kernel tree**, and building one is a multi-hour job with an uncertain module ABI | high: a real DRM device, `drm-backend.so`, no pixman shim |
| patch the vendor's IVI start-up path | modifying vendor binaries, which this project has a standing rule against, and which the wrapper experiment showed is fragile | low - no longer the vehicle's code |
| accept headless and document the consequence | nothing | **what is true today** |

## The honest statement for the record

**The projection can run the vendor kernel, init, compositor modules and application, and cannot give them the
display hardware they were written for.** Everything downstream of that - the surface creation the compositor
rejects, the standby/splash frames, the missing widgets - is downstream of a substitution that the vendor kernel's
own configuration makes unavoidable.

That is a materially different claim from "the UI does not render", and it is the claim the evidence supports.

---

## 2. The framebuffer path is closed too, so there is no display device at all

The remaining hope was `fbdev-backend.so` - a plain framebuffer needs no DRM and QEMU's standard VGA can provide
one. The vendor kernel says no:

```
CONFIG_FB_CMDLINE=y
# CONFIG_FB is not set          <- the entire framebuffer subsystem is disabled
```

**Not "the driver is missing" - the framebuffer subsystem is compiled out.** So in this kernel there is:

| device class | availability |
|---|---|
| DRM | `i915` only, which QEMU cannot present |
| framebuffer | **subsystem disabled** |
| vendor IAS backend | needs the vendor's GPU interface, absent in QEMU |

**Every display path is closed.** `headless-backend` is not merely the best available - it is the only one that
can exist, and this is now a closed question rather than a standing assumption.

## 3. What that does to the phrase "as close to stock as reasonable"

It defines the ceiling precisely, and honestly:

- **stock**: the vendor's kernel, `esinit`, compositor, modules, applications, service graph, D-Bus contracts,
  filesystem layout, boot chain - all of which this projection runs
- **not stock, and cannot be**: the display hardware. The vendor's compositor is built for a GPU the emulator
  cannot offer, and the kernel has no fallback compiled in
- **therefore**: anything that depends on the display path - surface creation, painting, touch hit-testing -
  is running against a substitution, and the failures observed there are attributable to it

That is the sentence this project should use from now on, in place of "the UI does not render", which implies a
defect where there is a hardware absence.

---

## 3. Scope correction - the ceiling was the *vendor kernel's configuration*, and a rebuilt kernel removes it

This document concludes that "the headless backend is the only one that can exist" because the vendor kernel's only DRM
driver is `i915`, `CONFIG_DRM_BOCHS`/`QXL` are not set, and the framebuffer subsystem is compiled out. **All of that is true
of `vendor.config` - and all of it stopped being true the moment a kernel was built with those options enabled.**

A boot of the vendor rootfs on such a kernel, captured by the delegated worker (`work/vm/kbuild/boot4-authentic.log`):

```
[    0.519360] [drm] Initialized drm 1.1.0 20060810
[    0.522973] [drm] Found bochs VGA, ID 0xb0c5.
[    0.523278] [drm] Framebuffer size 16384 kB @ 0xfd000000, mmio @ 0xfebf0000.
[    0.540897] bochs-drm 0000:00:01.0: fb0: bochsdrmfb frame buffer device
Reached target Local File Systems
Reached target Basic System
Reached target Login Prompts
Reached target Multi-User
```

**A DRM/KMS driver bound, a framebuffer device registered, and the vehicle's own boot path reached Multi-User.** So:

| backend | before | with this kernel |
|---|---|---|
| `ias-backend.so` | impossible (no GPU) | still impossible |
| `drm-backend.so` | **impossible** (no DRM device) | **possible** - bochs-drm is a KMS driver |
| `fbdev-backend.so` | **impossible** (`# CONFIG_FB is not set`) | **possible** - `fb0: bochsdrmfb` |
| `headless-backend.so` | the only option | still available |

**So the honest correction is this:** the display ceiling was **the vendor kernel's configuration**, not the hardware. It
was a real ceiling for anyone booting the shipped kernel, and it is not a ceiling for this project any more - **a rebuilt
kernel with `CONFIG_DRM_BOCHS` gives both a DRM and a framebuffer device under QEMU**, which is a materially different
situation from the one this document was written to describe.

**Not yet established:** that `/dev/dri/card0` and `/dev/fb0` exist as nodes, that `drm-backend.so` (or `fbdev-backend.so`)
accepts that device, and whether either removes the `wl_display@1: error 0: invalid object N` that killed the application.
The next measurements are, in order: `ls /dev/dri /dev/fb*`, then a weston run with `drm-backend`, then the application.

---

## 4. The device node exists - `drm-backend` now has something to bind to

The previous section said the nodes were unverified. They are verified now, from the delegated boot
(`work/vm/kbuild/boot5-parts.log`, listing `/dev/dri`):

```
crw------- 1 0 root 226,  0  card0
crw------- 1 0 root 226, 64  controlD64
```

and the kernel side of the same boot:

```
[    0.548997] [drm] Found bochs VGA, ID 0xb0c5.
[    0.566980] bochs-drm 0000:00:01.0: fb0: bochsdrmfb frame buffer device
[    0.567558] [drm] Initialized bochs-drm 1.0.0 20130925 for 0000:00:01.0 on minor 0
```

**A KMS device node at `/dev/dri/card0` (major 226, minor 0), a control node, and a framebuffer, on a kernel that boots
the vehicle's own rootfs to Multi-User.**

So the statement this document was written to make - *"the headless backend is the only one that can exist"* - is now
**false for this project**, and it was only ever true of the shipped kernel's configuration.

## 5. What this does and does not change

**Changes:** `drm-backend.so` and `fbdev-backend.so` are reachable. The vendor compositor can be given a real output. The
substitution that this document blamed for the application's `wl_display@1: error 0: invalid object N` no longer has to be
the headless backend - and that error has a chance of not occurring, which it never did before.

**Does not change:** the vendor's `ias-backend.so` still cannot run (no vendor GPU interface); the firmware, init,
compositor modules and application are still the vendor's own; and nothing here is *stock* - a rebuilt kernel is a
substitution too, just a smaller and better-understood one than the headless backend.

**The next measurement is the one this whole line of work exists for:** run the vendor compositor with `drm-backend` and
see whether the application stops receiving `invalid object N`. Everything else in this document is now upstream of that
answer.

---

## 6. The vendor compositor runs on `drm-backend`, and the Wayland fatal error is absent

From the delegated run `work/vm/kbuild/boot8-drm.log`:

```
Loading module '/usr/lib/weston/drm-backend.so'
Output Virtual-1
Failed to initialize backlight
failed to create input device '/dev/input/event0'
warning: no input devices on entering Weston
Reached target Multi-User          (twice)
fatal error | invalid object        (0 occurrences)
```

**The vendor compositor loaded its own `drm-backend.so`, found a connected output, and reached Multi-User with no Wayland
fatal errors in the capture** - where every headless run ended with `wl_display@1: error 0: invalid object N`.

That is the first time in this project that the application stack has had a real display backend underneath it.

## 7. What is *not* yet established - and each is a separate measurement

- **Whether the application itself started.** The capture shows Multi-User and the backend, not `AppHomeScreen`; the worker's
  `05-drm-backend-result.md` is where that will be settled.
- **Input.** `failed to create input device '/dev/input/event0'` and *"no input devices"* - so even with a display there is
  nothing to click with yet. The injection module (`/weston-vm-input.so`) is a separate path and was not exercised here.
- **Backlight.** `Failed to initialize backlight` is expected on a virtual output and is not fatal.
- **What the display shows.** No capture was taken on the DRM path in this log.

**So the honest sentence is: the display ceiling is gone, the compositor accepts the device, and the Wayland failure that
killed the application in every headless run is absent from this capture - but nobody has yet seen the application paint on
it.**

That is a very different position from the one this document opened with, and it was reached by a rebuilt kernel with
`bochs-drm`, not by anything the vendor's own kernel could do.

## 8. Correction to §6 - the error is absent because no client ever connected

Section 6 read "*zero* `fatal error` / `invalid object` occurrences" as progress. **The delegated isolation run shows a
different explanation, and it is the correct one:**

```
[apps-check] NO_WAYLAND_SOCKET after 240s
weston_pid=690 alive=yes       the process is alive
find-wayland=[]                no wayland-* socket anywhere in /run /tmp /var/run
wchan=[hrtimer_nanosleep]      main thread asleep, not crashed
```

**`drm-backend.so` initialises the DRM device - and then weston stalls before it ever binds its listening socket.** With no
socket, the application stack cannot connect at all, so:

- the `invalid object N` comparison **cannot be made** on this backend;
- the absence of that error is **"nothing connected"**, not "the problem is fixed".

**This is the third time this session that an absence of errors was really an absence of activity** - after the log a fresh
process truncated (rule 14) and the 30-second boot that could not reach userspace. The pattern is consistent enough to name:
**before reading a zero, ask what would have produced a non-zero.**

**Where that leaves the display ceiling:** the *device* half is done - `/dev/dri/card0` exists and the vendor's
`drm-backend.so` accepts it. The *compositor* half is not: weston stalls before serving. The application question is
therefore still open, and it is blocked on a stall rather than on hardware.

## 9. A second backend with no page-flip path, and why that is the cheaper experiment

The worker's stall hypothesis is that `drm-backend` waits for a vblank or page-flip event that **bochs KMS under QEMU TCG
never delivers** - measurably consistent (`alive`, `wchan=hrtimer_nanosleep`, no socket) and explicitly labelled a
hypothesis by the worker.

**`fbdev-backend.so` ships in the same module set** (348,776 bytes) and the same kernel that provides `card0` also provides
a framebuffer:

```
[    0.566980] bochs-drm 0000:00:01.0: fb0: bochsdrmfb frame buffer device
```

**fbdev writes into a mapped framebuffer on a timer - there is no vblank wait, no page-flip, no atomic commit** - so the
hypothesised stall mechanism **cannot occur on it**. That makes it a two-for-one experiment:

1. if weston serves a client on fbdev, the **application question** gets answered;
2. and if it does not, the stall is **not about vblank**, which is worth knowing *before* anyone traces ioctls.

**The order of checks matters and is the lesson of §8:** socket first, then application registration, then the error. An
`invalid object` verdict on a backend that never served a client is not a verdict.

**Status:** delegated as a suggestion with those three checks named; whether fbdev serves is the next measurement, and a
negative is a result.

## 10. My "cheaper experiment" failed twice - fbdev needs `weston-launch`, and that produced nothing

Section 9 proposed `fbdev-backend.so` as a faster answer than tracing page flips, on the reasoning that it has no vblank
path. **Two runs, both negative:**

**Run 1 - the backend refuses on principle:**

```
Loading module '/usr/lib/weston/fbdev-backend.so'
initializing fbdev backend
fatal: fbdev backend should be run using weston-launch binary or as root
fatal: failed to create compositor backend
```

`/dev/fb0` and `/dev/dri/card0` both exist, so the device half is fine - the *compositor* refuses to use fbdev unless it is
launched through `weston-launch` (which ships at `/usr/bin/weston-launch`, 69,296 bytes, **not setuid**, so it only helps a
root caller).

**Run 2 - the `weston-launch` hop produced nothing at all:**

```
FB1_SOCKET=[]      no wayland socket
FB1_WLOG=[]        /tmp/weston-real.log was never created
```

No log, no socket, no process. `weston-launch` execs `/usr/bin/weston` itself, so the wrapper was given a recursion guard
(`WESTON_LAUNCHED=1`) - and with that in place the whole chain vanished without writing a line, which is a worse outcome
than a failure with a message.

## What this teaches, and it is at my expense

**The "cheaper" experiment cost two runs and answered nothing.** `drm-backend` had already got further than fbdev ever
did - it bound the device and found an output before stalling - so my suggestion was not cheaper, it was a detour around a
hypothesis that had not yet been tested.

**The honest position now:** the live question remains the worker's - *why does `drm-backend` stall after `Output
Virtual-1`* - and the page-flip hypothesis is still the best one, unmeasured. My contribution to it is a negative: **fbdev
is not an alternative route**, and anyone considering it should know it needs a launcher hop that, in this projection,
produced silence.

## 11. fbdev *does* work - in isolation, at 1024x768, which is the wrong size for this UI

The delegated worker got further than my two attempts, by invoking weston in a way that satisfies the launcher check and
booting the research init with a manual compositor (`work/vm/kbuild/boot20-fbdev4.log`, a 14.2-second run,
`"init": "/init"`, `userspace: true`):

```
Loading module '/usr/lib/weston/fbdev-backend.so'
initializing fbdev backend
Creating fbdev output.
Opening fbdev frame buffer.
Mapping fbdev frame buffer.
fbdev output 1024×768 px
failed to create input device '/dev/input/event0'
```

**So `fbdev-backend` is usable** - my §10 conclusion was too strong. What it needed was the right invocation, not a
different idea; the `weston-launch` refusal I hit is a launcher-detection problem, and the worker found an invocation that
passes it.

**But look at the output size: `1024×768`.** The vendor's UI is **1920×720** (`weston_1920.ini`, the capture geometry, the
`1926×753` surfaces). fbdev is bound to whatever the kernel's framebuffer is, and bochs-drm's default mode is 1024×768 - so
**fbdev can prove that a client connects, and cannot present this UI at its own resolution.**

That makes the two backends complementary rather than competing:

| backend | device | output control | use |
|---|---|---|---|
| `drm-backend.so` | `/dev/dri/card0` | **can set 1920×720** | the fidelity target - stalls after `Output Virtual-1` |
| `fbdev-backend.so` | `/dev/fb0` | **fixed 1024×768** | a **control experiment**: does a client connect at all |

**And that is the value of the worker's result**: a client connecting on fbdev would prove the application can run against a
real output in this projection, independent of the DRM stall - which would separate *"the app cannot connect"* from *"the
DRM backend stalls"*.

**My own two fbdev runs are superseded**; `work/vm/fbdev` and `run-fbdev.py` stay as the record of what did not work, and
the live line of work is the worker's.

## 12. The worker's control experiment refutes the vblank hypothesis and moves the failure downstream

My §9/§11 framing - that fbdev would be a cheap way around a page-flip stall - is **superseded by the measurement**. The
delegated result (`docs/kernel/06-fbdev-backend-result.md`) is:

> **fbdev-backend result: also no wayland socket - the stall is NOT vblank/page-flip.**

**The decisive evidence, and it is better than mine:**

```
find /run /tmp /var/run -name 'wayland-*'      -> empty at 8 s and 16 s
/proc/<weston>/fd  ->  0 /dev/null, 1 log, 2 log, 13 timerfd, 23 timerfd, 24 dltpipe
                       NO unix socket, NO epoll fd
weston alive at +8 s, gone by +16 s            -> a teardown, not a live-but-stalled server
```

**The absence of an epoll fd proves the compositor never entered its serving loop** - a stronger statement than "no socket
found", and the kind of evidence this project should prefer.

**So both real-output backends (`drm`, `fbdev`) fail identically after loading all the ivi modules, while the headless
(virtual output) backend succeeds** (`WAYLAND_SOCKET_UP`, measured long ago). The common factor is **ivi-shell startup over a
real output**, not how a backend scans out.

## 13. The one thing that differs between virtual and real output: the shell user-interface binary

The vendor ini names it, and **the name is wrong**:

```
weston_1920.ini:  ivi-shell-user-interface=/usr/lib/weston/weston-ivi-shell-user-interface
that path:        MISSING
the binary:       /usr/libexec/weston-ivi-shell-user-interface   215,480 bytes, present
```

**With a virtual output the ivi-shell may never spawn that client; with a real output it plausibly does** - and a failed spawn
during shell init is the shape of a compositor that loads every module and then exits. That is the next single-change test,
and it comes from the vendor's own configuration rather than from a guess.

**And the fallback if it does not work is named in the same result**: the bochs framebuffer map emits
`ttm_bo_vm_open` warnings that are the **only kernel-side signal differing** between the working virtual-output case and the
failing real-output case.

## 14. My shell-UI hypothesis was tested and refuted — and it found a real, dormant vendor bug

The §13 hypothesis (fix `ivi-shell-user-interface=` and the socket appears) was checked in one run by the worker, documented
in `docs/kernel/07-ivi-shell-user-interface-path.md`:

> **The `ivi-shell-user-interface` path is a real bug - but not the cause of the missing socket.**

**The path is genuinely wrong** - the vendor ini names `/usr/lib/weston/weston-ivi-shell-user-interface`, which does not
exist, while the binary sits at `/usr/libexec/`. Correcting it **does not make the socket appear**.

**And the source says why it cannot**: the shell user interface is started by an **idle callback** on the compositor's event
loop (`wl_event_loop_add_idle(loop, launch_hmi_client_process, ...)` in the hmi-controller), which only runs once weston
enters `wl_display_run` - the same loop whose absence is proven by the missing epoll fd. **The client is never reached, and
the wrong path is therefore dormant**: a real configuration defect, downstream of the actual failure.

**So the record now holds two facts of different kinds:** a confirmed vendor defect that does nothing on this build, and a
refuted hypothesis of mine that at least produced the first one.

## 15. Where the real-output failure actually is

With vblank refuted (doc 06) and the shell path refuted (doc 07), the failure is **in weston's own startup between the last
module load and `wl_display_run`**, and the next instrument is named by the worker: **one userspace trace of the main
thread** - not a kernel change, not DRM ioctl tracing. That is the right next step, and both of tonight's cheaper ideas are
on record as having been tried first.

---

## 16. ROOT CAUSE: our own input module aborts the compositor when there is no seat

The `strace` the worker ran with `/tmp/dlt` pre-created answers the whole of §5-§15, and the answer is **not** the display
backend:

```
Loading module '/weston-vm-input.so'
VM_INPUT_NO_SEAT
epoll_ctl(3, EPOLL_CTL_DEL, 25, NULL) = 0            teardown begins
ioctl(12, DRM_IOCTL_DROP_MASTER, 0)    = 0
ioctl(10, VT_SETMODE, ...)             = 0
+++ exited with 1 +++
```

**`/weston-vm-input.so` - this project's own input module - returns -1 when the seat list is empty, and weston shuts down
before serving.** The trace shows the teardown starting on the line after the module's own message.

### Why headless worked and drm/fbdev did not

In weston 1.10, **the seat is created by the backend**, and only `headless` does it unconditionally:

```c
/* compositor-headless.c */
weston_seat_init(&b->fake_seat, b->compositor, "default");   /* line 186 */
```

`drm` and `fbdev` do not call `weston_seat_init`; they rely on the libinput/udev path, which creates a seat only when udev
reports an input device. **Under QEMU there are none** - the log's `failed to create input device '/dev/input/event0'` is the
Power Button, *"not tagged as input device"* - so `seat_list` stays empty and our module fails.

| backend | seat | `weston-vm-input.so` | result |
|---|---|---|---|
| headless | fake seat created | finds it, returns 0 | **serves** (`WAYLAND_SOCKET_UP`) |
| drm | none (no udev input) | `VM_INPUT_NO_SEAT`, returns -1 | exits, no socket |
| fbdev | none (no udev input) | `VM_INPUT_NO_SEAT`, returns -1 | exits, no socket |

**The display/scanout mechanism was never the issue.** The entire "real-output versus virtual-output" framing in §5-§15 was
a **proxy for "has a seat versus does not"** - and the variable that decided it is a `return -1` in a module this project
wrote.

### What this means, stated plainly

- **The DRM work was not wasted**: `/dev/dri/card0`, `bochs-drm` and the rebuilt kernel are real, reproducible, and the
  prerequisite for ever presenting this UI at 1920x720.
- **But none of the display failures were the vendor's, the kernel's, or the backend's.** They were ours, for the fifth time
  this session: an instrument that changed the system under test and was read as a property of the system.
- **The fix is a return value**: make `/weston-vm-input.so` tolerate an empty seat list - return 0 and attach when a seat
  appears, or create the seat itself as headless does - then retry `drm-backend`.

**And the application question is finally reachable**: with a seat and a socket on `drm-backend`, a Qt client can connect,
and `wl_display@1: error 0: invalid object N` becomes testable for the first time.

## 17. The fix is built, and the boot that tests it is specified

`tools/uk_fw/guest/weston_vm_input.c` now **defers** rather than failing:

- `module_init` logs `VM_INPUT_NO_SEAT_DEFERRED` and continues - weston is no longer torn down;
- `bind_first_seat()` attaches the first seat if one exists and is **called again from the existing `timer_handler`**, so touch attaches the moment a seat appears, without a restart;
- a new marker, `VM_INPUT_SEAT_BOUND`, records that it happened.

**Deferral was chosen over the "return 0 and do nothing" option** the analysis offered, because a no-op module would let weston serve while **silently losing input forever** on a backend that later gains a seat. The timer already runs every `POLL_MS`, so retrying costs nothing.

Built artefact: **13,008 bytes, zero host paths, both markers present**; reproducible with `tools/uk_fw/guest/build-weston-vm-input.sh`.

## 18. The one boot, and what each outcome means

Order of checks - the order is the lesson of §8, §12 and §15, all of which were failures to check causality before reading an absence:

1. `find /run /tmp /var/run -name 'wayland-*'`
2. `pidof AppLauncher` / `AppHomeScreen`
3. `/proc/<app>/fd` for a connected socket
4. **only then** `invalid object` in the application log

| outcome | means |
|---|---|
| socket + app running + no `invalid object` | **the Wayland fault was the seat all along**; the display thread is closed |
| socket + app running + `invalid object` | the fault is real and backend-independent, and **measurable for the first time on a connected client** |
| no socket | the deferral is wrong or insufficient - report `wchan`/fd and correct the module |

**And the record requirement:** the document must state the payload that was booted and whether the socket appeared before the application was checked. An `invalid object` verdict from a client that never connected is the mistake I made twice tonight.


---

## 19. RESULT: the seat fix closes the thread - socket, application, drawing, no Wayland error

The boot that tested the fix (`docs/kernel/09-vm-input-fix-result.md`, run `1793901922927628000`), payload stated as
required: kernel `bzImage` sha256 `893e1a6b...a6392`, module `/weston-vm-input.so` **13,008 bytes** sha256
`514da5de...bd58c` carrying `VM_INPUT_READY`, `VM_INPUT_SEAT_BOUND`, `VM_INPUT_NO_SEAT_DEFERRED`, config `backend=drm-backend.so`,
`modules=/weston-vm-input.so`, `ivi-shell-user-interface=/usr/libexec/weston-ivi-shell-user-interface`,
`[output] name=Virtual-1`, authentic init, `--smp 4`.

**Checked in the required order:**

```
1  WAYLAND_SOCKET_UP after 2s                  socket BEFORE any application check
2  APPLAUNCHER_PID=[1953] at +45s
   APPHOME_PID=[2205] at +30s
   PIDS_FINAL AppLauncher=[1953] AppHomeScreen=[2420] ApplicationManager=[1995]
3  Using Wayland-EGL | SCREEN_STATE: START DRAW | constructMenuModel
   prepareAdvancedDisplayList ... numItemsPerPage: 12
   injectWidgetItemToAdvancedPage ... itemWidgetPlaceHolder FOUND!!!
   D-Bus name owned: com.lge.hkmc.avn.appfunc.AppHomeScreen
4  BYHAND_CAPTURE1 bytes=87818  2 bytes=88172  3 bytes=87883
   invalid object | wl_display@1: error   ->  0 occurrences
```

**So: the vendor's own application runs against a real DRM output, connects as a live Wayland-EGL client, and reaches its
drawing path.** The `invalid object` fault that this document spent fifteen sections on **was the empty seat all along**.

## 20. The gap in that result, stated rather than smoothed

**The frames were measured but not preserved.** The log carries `BYHAND_CAPTURE1 bytes=87818` and two more, and
`87,8xx` is a **new size** - not the 129,844-byte early background and not the 120,5xx-byte standby face - which is real
evidence that something different was on screen. **But no PNG of those frames was saved**: the run's `img-out.bin` is
0 bytes, and the one inline PNG that could be recovered from the serial log decodes to **6,145 bytes at 1024x768**, which is a
console framebuffer, not the application.

**By this project's own rule, a capture that was not kept is not evidence.** The log lines are strong and they are the
reason §19 is written as a result, but **"the application draws" will not be settled until someone saves the frame.** That is
one run with the image channel enabled, and it is the first item for whoever picks this up next.

## 21. My own attempt to save the frame did not reproduce, and the difference is the wrapper

Trying to close the one gap in §20 - a saved frame - I ran my own clone (`work/vm/fbdev`, the rebuilt kernel, the fixed
module injected, `compat=False`) with the compositor wrapper forcing the backend **on the command line**:

```
/usr/bin/weston.real --backend=drm-backend.so --use-pixman --width=1920 --height=720 $new
```

Result, at 150 s:

```
SHOT_SOCKET=[]                                   no wayland socket
SHOT_APPS home=[] launcher=[1981]                the launcher ran, the app did not
SHOT_TESTTOUCH=[0]                               no SEAT_BOUND or NO_SEAT_DEFERRED in the weston log
```

**No socket, no seat markers, and not even the module's deferral message** - which means weston did not reach module loading.
The most likely cause is that `--width`/`--height` are not valid options for `drm-backend` in weston 1.10 (they belong to the
headless/windowed backends) and the compositor aborted on the option, exactly the class of failure the wrapper itself exists to
strip for `--tty`.

**Not confirmed**, because weston's own log goes to `/tmp/weston-real.log` and dies with the snapshot. That is a real gap in
this project's observability: **the compositor's log is the one file most worth keeping and the only one never saved.**

**So the working configuration is the worker's, not mine**: backend selected by the **ini's `backend=` line**, with no CLI
override. The remaining task - save one frame - is specified to it with that difference called out, and with the instruction to
change one variable only.

## 22. The frame is saved, it does not show a painted application, and the mode explains why

The worker kept a frame (`docs/kernel/10-capture-saved-and-described.md`): **87,944 bytes, sha256 `b51acb8b...`, PNG 1024×768,
RGBA**, decoded exactly from the file-backed channel.

**What it shows, described rather than assumed:** ~95 % black; two text-like clusters (upper-right-centre and a thin band at
the bottom); dominant greys plus a trace of orange; the top ~252 rows entirely black.

**And it does not prove the application draws.** It was captured **after** the instance that logged `START DRAW` was gone, so it
shows a mostly-empty ivi-shell output. The doc says so itself, which is the right call.

## 23. Two causes, both concrete, and one of them is a resolution this project has had wrong all along

**1. The output is 1024×768, not 1920×720.** The vendor ini carries `[output] name=HDMI1 / mode=1920x720`, the app lays out
for `1926×753` surfaces, and the capture is **1024×768** - the bochs default. A 1920-wide layout drawn into a 1024-wide screen
looks exactly like what was described: sparse text pushed to the edges, everything else black.

`bochs-drm` takes its modes from **EDID**, and QEMU can advertise the right one:

```
-device VGA,edid=on,xres=1920,yres=720
```

then `/sys/class/drm/card0-Virtual-1/modes` should list `1920x720` and weston's log should report that mode on
`Output Virtual-1`.

**2. The capture must happen while an instance is alive**, not after the first one exits - the monitor already has the liveness
signal.

**Both are one run.** And the reference for what a correct frame looks like already exists: `docs/vm/38-gesture-home-layout-after-set-power-on-2026-11-05.png`
(**16,062 bytes at 1920×720**), the only fully-laid-out frame this project has captured, taken on the **headless** backend long
before tonight's kernel work.

## 24. The 1920x720 frame, looked at rather than described: it is the application's own standby face

The worker's doc 11 fixed two things properly and earned its frame:

- **The mode.** `-device VGA,edid=on,xres=1920,yres=720` **did nothing** - bochs-drm 4.1.27 calls `drm_add_modes_noedid()` and never reads EDID, and 1920×720 is not a standard mode. So the kernel source was patched (`bochs_kms.c`: `defx/defy` defaults, plus a CVT 1920×720@60 mode marked preferred), rebuilt, and verified: `/sys/class/drm/card0-Virtual-1/modes` now **lists `1920x720` first**.
- **The channel.** `/dev/ttyS3` is smack-relabelled `System::GPS` by the vendor's udev rules in the authentic boot, so the monitor's write was **denied**; the capture went over `/dev/ttyS2` instead.

The saved frame is `work/vm/kbuild/painted-1920x720.png` - **144,501 bytes, sha256 `59253cf6...`, PNG 1920×720** - and a copy is kept at
`docs/vm/48-drm-backend-1920x720-app-standby-face-2026-11-06.png`.

**The worker described it programmatically and concluded "a text screen, not the widget grid". I looked at it, and it is more specific than that:**

> **a full-width blue title bar, the KIA logo centred on black, and one small placeholder glyph at top centre.**

**That is the application's own standby face** - the same content as the 120,5xx-byte headless standby frames, but now rendered at the vendor's own 1920×720 on the vendor's own DRM backend. The logo is the application's asset and the bar is its chrome, so **the application is drawing**; it is simply in its powered-off presentation.

## 25. Which means the last step is the call found hours ago

The app shows standby because nothing has told it the vehicle is on. That is `set_power_on_status(1, 0)` on
`com.lge.hyundai.avn.appmanager` - **the exact call that produced `docs/vm/38-gesture-home-layout-after-set-power-on-2026-11-05.png` on the headless backend**, and the reason
that frame was laid out.

**So the DRM path is now behaviourally identical to the headless path**: compositor serving, application connected, application
painting its own standby frame. The one difference left is that nobody has made the power-on call *on this backend*.

**That is the next run, and it is one line**: after `AppHomeScreen` owns its bus name, call `set_power_on_status(1, 0)`, wait for
the frame to settle, then capture. **If it produces a 1920×720 frame with a left panel and Battery/Range widgets placed, the VM
goal's central claim is met on the stock display path.**

## 26. The one remaining line, and the reference frame it should reproduce

The application on the DRM backend is in **standby** - its own logo and chrome - because nothing has told it the vehicle is on.
**That is the same state the headless backend was in before the call that fixed it**, and the call is known:

```sh
dbus-send --session --print-reply --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.set_power_on_status int32:1 int32:0
```

**The reference is already in the repository** - `docs/vm/38-gesture-home-layout-after-set-power-on-2026-11-05.png`, **16,062
bytes at 1920×720**: light day theme, left panel, Battery and Range widgets placed with `---`. It was captured on **headless**
hours before the kernel work; the DRM path now needs to produce the same content at the same size.

**The sequence for that run, in the order this session earned:**

1. boot authentic, `--smp 4`, timeout 360+, patched kernel, fixed input module;
2. wait for `WAYLAND_SOCKET_UP` **and** for `AppHomeScreen` to own its bus name - **poll `NameHasOwner`, do not sleep a fixed
   interval** (the mistake that cost three runs earlier);
3. make the call;
4. let the frame settle (~90 s on headless), then capture **while that instance is alive**;
5. return it with its byte count.

## 27. What each outcome would mean

| outcome | reading |
|---|---|
| light frame, left panel, Battery/Range with `---` | **the VM goal's central claim, met on the stock display path at the stock resolution** |
| still standby | the call did not land - check that the name was owned at call time; **do not** use `ask_power_status` as pass/fail, it reads `1` before and after because the setter pushes an event |
| mostly black | state whether the mode was still 1920×720 and whether an instance was alive at capture |

**And a deliberate exclusion:** the widget *values* are not part of this run. They need the CAN transport, which the vendor
kernel's own configuration makes unreachable - the separate problem documented in `docs/vm/47-...`. **The target here is the
laid-out frame and nothing more.**

## 28. The power-on call lands, and the application dies during the layout

The run that made the call did everything right (`docs/kernel/12-power-on-call-result.md`):

```
SOCKET_UP after 2s
BUS_AT_+10s=[unix:abstract=...]
NAME_OWNED=yes at +100s              polled NameHasOwner, not a fixed sleep
APPHOME_PID=[2328]
ASK_POWER_BEFORE=int32 1             not used as a pass/fail
SET_POWER=method return              the call landed
```

**And five captures at +5/+15/+30/+60/+90 s were all `129,844` bytes - the standby size - with the pid changing from 2328 to
2564 between the +15 s and +30 s samples.**

So this is a **fourth outcome** the decision table did not anticipate: not the laid-out frame, not "the call did not land", but
**the application crashes during the power-on layout** and the launcher restarts it in standby. The seat, the mode and the socket
are all fixed; this is a new problem behind them.

## 29. Where the answer is, and it has been there every time

The worker's own bounding fact: **the launcher-started app's stderr goes to `/tmp/applauncher-stdio.log`, and this run did not
dump it.** That is the same route that produced `wl_display@1: error 0: invalid object 19` in the first place.

**And there is a specific hypothesis worth testing alongside it**, drawn from this session's own database work: during an earlier
layout the app logged `DB UPDATE COMMIT FAIL` **23 times**, plus `BEGIN TRANSACTION FAIL` and `DELETE FAIL QSqlError(...)`, and the
pulled database had **`WidgetSettingFront` and `WidgetSettingAdvList` empty** while `CustomLayoutFront` held 25 rows. **The
power-on layout is exactly the path that writes those two tables.** A SQLite failure in the widget-settings write would explain
all three observations at once: crash on the call, no Wayland error text, and "commits fail but the layout commit succeeds".

**The check costs no instrument:** grep the launcher log around the crash for `COMMIT FAIL` / `BEGIN TRANSACTION` / `QSqlError`,
and pull the database again to see whether those tables gain rows when the call lands.

## 30. The caution that keeps being needed

**Do not read the crash as "the laid-out layout does not exist on this backend".** It exists - `docs/vm/38-gesture-home-layout-after-set-power-on-2026-11-05.png`,
16,062 bytes, produced on **headless**. If DRM cannot reach it, the difference is something DRM-specific that has not been
measured, and the launcher log is where it will be found.
