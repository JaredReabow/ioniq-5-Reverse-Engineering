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
