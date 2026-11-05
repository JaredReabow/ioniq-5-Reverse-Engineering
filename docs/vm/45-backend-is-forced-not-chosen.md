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
