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
