# What the display ceiling blocks, item by item

Date: 2026-11-05. Written because the same conclusion has now been reached three times from three directions, and each
time it cost a run: **several open items are blocked by one absence**, not by their own difficulty.

## The absence

`docs/vm/45-backend-is-forced-not-chosen.md`: the vendor kernel's only DRM driver is `i915`, QEMU cannot present one,
the framebuffer subsystem is compiled out entirely, and the vendor's own `ias-backend` needs a GPU interface that does not
exist here. **The projection runs `headless-backend` + `--use-pixman`, and every vendor Qt application we start dies with
`wl_display@1: error 0: invalid object N`** - measured for `AppHomeScreen` (19) and for SCOMO (20), the second started
independently by hand.

## The blocked items

| open item | what it needs | why the ceiling stops it |
|---|---|---|
| **Widget values** (Battery, Range) | `can0` frames | the CAN transport is a *different* absence, but the *result* cannot be seen without a working display either |
| **Engineering mode entry** (V-060 / `SetEnginnerModeEntryCheck`) | AppSetup to navigate toward settings | AppSetup dies with the same Wayland error; the method is never called (measured: 0 calls in a boot) |
| **V-069 end-to-end** (is the navi signature checked against `./tool/public.crt`?) | SCOMO to run far enough to load keys | SCOMO is a Qt app and dies on `invalid object 20` before touching `./tool/` |
| **V-070 trigger** (does `eject.sh` ever run?) | an eject event in the manufacturing app | the app ran but needs a real UI event; nothing can be clicked |
| **Interactive tapping** | a painted, placed application | placement works, but what it places is standby/splash, and placing races the client |

## What would unblock each, and at what cost

1. **A kernel rebuild with `CONFIG_DRM_VIRTIO_GPU`** - needs a 4.1.27 tree matching `vendor.config`. This project has
   **no kernel tree**. It unblocks *all five*: `drm-backend.so` ships and would then have a device.
2. **A physical unit** - unblocks the security-side items *and* settles the widget values, though not the VM goal.
3. **Acquiring a 4.1.27 tree is the single highest-leverage action available to this project.** Nothing else on this
   list can be finished without either it or hardware.

## What is *not* blocked, and is worth doing instead

- **More adaptor completeness**: the stand-in answers 100% of what the stack asks; extending it to the *replies the
  vehicle logged* is measurable without a display (this was done for four of the five backlog methods).
- **Static security work**: V-069's remaining question has static evidence; every sweep so far has been static.
- **The record**: enumerating families and narrowing claims, which is what the last several turns did.

## The honest sentence

**The VM goal is at its ceiling, and the ceiling is a kernel configuration.** Everything above is written down so that
the next person does not spend a run rediscovering it - which is what I did three times, at roughly one run per
rediscovery.

## Update - the kernel tree was already here

I wrote above that the project "does not have" a matching kernel tree. **That was wrong, and it was wrong in the
repository's own `work/` directory:** `work/kbuild/linux-4.1.27.tar.xz` is present, alongside previous build outputs
(`bzImage-gcc11`, `bzImage-noreloc`, `bzImage-4.1.27-abl-vdisp`) and `work/kbuild/*.log`.

So the highest-leverage action is not "acquire a tree" - it is **build from the tree we already have**. That work is
delegated (child thread `d5d41ed2`, workspace `work/vm/kbuild/`), with the risks named in advance:

- reconciling `vendor.config` against vanilla 4.1.27 **drops the vendor-only symbols** (`CONFIG_LGE_*`, `micom`, `ias`) -
  and losing `micom` means losing the built-in driver that would have created `can0`, which is a trade to state rather
  than discover;
- module vermagic must stay close to `4.1.27-abl` or the vendor modules stop loading;
- the image's own `esinit` must remain the init path.

**The lesson is the same one as the log values and the bus policies:** I asserted a resource was missing without
looking in the place the project keeps its resources. That is the third time this session - the pattern is mine, not
the repository's.

## Update 2 - a kernel that already claims the right version, and a config detail I omitted

Two more things were sitting in `work/kbuild/` and neither was in the brief I gave the build worker:

1. **`bzImage-gcc11` (5,941,712 bytes) reports `version 4.1.27-abl`** - a 4.1.27 tree was successfully built with
   `EXTRAVERSION=-abl`, which is the vermagic the vendor's modules need. **`bzImage-4.1.27-abl-vdisp`** (5,934,912) also
   exists, and its name suggests a virtio-display attempt. **The first thing to try is therefore not a build at all: it is
   booting those images with `-device virtio-gpu-pci` and checking for `/dev/dri/card0`.**
2. **`vendor.config` has `# CONFIG_VIRTIO_PCI is not set` and `# CONFIG_VIRTIO_MMIO is not set`.** So
   `CONFIG_DRM_VIRTIO_GPU=y` alone produces nothing - `VIRTIO`, `VIRTIO_PCI` and `VIRTIO_RING` must be enabled too, and
   the result must be verified **in the built kernel's `.config`**, because `make olddefconfig` silently drops symbols it
   cannot satisfy. A "virtio-gpu build" that ships without virtio-gpu is exactly the failure mode this project keeps
   mis-labelling as "the vendor code does not work".

Both are recorded here rather than only in a message, because the pattern in this document is now explicit: **three times
the thing I called missing was in the repository, and once the thing I called a blocker was a compiler flag.** The cost of
each was a run; the cost of writing it down is nothing.

## Update 3 - the build "failure" is the path, not the kernel

The delegated build failed four times, and the fourth failure names the cause plainly:

```
fixdep: error opening config file: engineering/ioniq: No such file or directory
fixdep: mmap: Invalid argument
```

**`engineering/ioniq` is the middle of this repository's path** - `/Users/leo/Documents/ChatGPT/reverse engineering/ioniq research`
contains two spaces. 4.1's kbuild host tools do not quote paths, so the build splits on the space and looks for a file
called `engineering/ioniq`. It is a known limitation of old kernels, it is not a compiler problem, and it may be what the
earlier `relocs` failures were too.

**The fix is one line of setup:** build in a space-free directory (`/tmp/kb/linux-4.1.27`) and copy only the resulting
`bzImage` back into the repository. Nothing else about the tree needs to live here - the deliverable is text.

**And a note on delegation:** I gave the worker a brief that warned about instruments, git and stray QEMU, but not about
the **directory path it would build in** - which turned out to be the blocker. The lesson generalises: when a task fails
repeatedly and the failure looks like toolchain trouble, check the environment the tool is running in before the tool.

## Update 4 - the delegated boot was measuring the wrong thing for 30 seconds

The worker's first two boot attempts used the harness defaults:

```
"init": "/init"            the bare research entry, not the vendor one
"userspace": false
"root_mounted": false
"elapsed_seconds": 30.24
```

**`/init` is not the authentic path**, and **30 seconds cannot reach userspace on this image** - `docs/VM-RUNBOOK.md`
records Local File Systems at ~14 s, Basic System at ~18 s, and **Multi-User at 76-97 s**. A 30-second verdict cannot
distinguish a working kernel from a broken one, and `root_mounted: false` at that point means nothing at all.

The three corrections sent: `--init /init-authentic-hmi.sh`, `--timeout 300+`, the vendor rootfs, plus
`-device virtio-gpu-pci` in the copied runner argv. And the instruction that matters most: **boot the two candidate images
that already exist before compiling anything.**

**Why this belongs in the document and not just in a message:** it is the same class of error as the truncated log and the
30-second capture - **a measurement that cannot distinguish success from failure, read as a failure.** Twice now the
answer was "look at what the harness is actually doing", not "look at the kernel".
