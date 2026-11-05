# `CONFIG_DRM_VIRTIO_GPU` does not exist in linux-4.1.27 — bochs-drm is the DRM device instead

Date: 2026-11-06. This corrects the central premise of the plan, and records the substitution that made
the DRM device possible anyway.

## The premise and the measurement that contradicted it

The plan said: "Enable at minimum `CONFIG_DRM_VIRTIO_GPU=y` … and add a QEMU display device if needed
(`-vga none -device virtio-gpu-pci`)". The vendor config's absence of the symbol was read (correctly) as
"the vendor kernel has no virtio-gpu", but the implied fix — turn the symbol on in the 4.1.27 tree — is
not available:

```
$ grep -rln "virtio_gpu\|VIRTIO_GPU" linux-4.1.27/
(no output)

$ ls linux-4.1.27/drivers/gpu/drm/
amd ast atmel-hlcdc bochs cirrus exynos gma500 i2c i915 imx mga mgag200 msm
nouveau omapdrm panel qxl r128 radeon rcar-du rockchip savage shmobile sis
sti tdfx tegra tilcdc ttm udl vgem via vmwgfx
```

There is **no `virtio` directory** under `drivers/gpu/drm/` and no `DRM_VIRTIO_GPU` Kconfig symbol in the
tree. The virtio-gpu DRM driver was merged in **Linux 4.2**; stable 4.1.x releases backport bug fixes, not
new drivers, so 4.1.27 does not contain it. `CONFIG_DRM_VIRTIO_GPU` was absent from `vendor.config` for
the same reason it is absent from my final `.config`: **it is not a symbol in this kernel at all.**

## What provides the DRM device instead

4.1.27 *does* contain four QEMU-capable KMS DRM drivers, all of which the vendor had disabled and all of
which I enabled:

- `CONFIG_DRM_BOCHS` — "DRM Support for bochs dispi vga interface (qemu stdvga)" — **the one that binds**.
- `CONFIG_DRM_QXL`, `CONFIG_DRM_CIRRUS_QEMU`, `CONFIG_DRM_VMWGFX` — also `=y`, unused (no matching device).

The runner's base argv already contains `-vga none -device VGA,id=display0,addr=01.0`, and QEMU's `VGA`
device *is* the Bochs dispi adapter (`[drm] Found bochs VGA, ID 0xb0c5`). So no runner edit was needed:
bochs-drm binds to the VGA device the harness was already presenting, and creates:

```
crw------- 1 0 root 226, 0 card0
/sys/class/drm/card0-Virtual-1/status=connected
```

The connector is named **`Virtual-1`** (not `HDMI1`/`HDMI2`, which is what the vendor's `weston_1920.ini`
names) — this matters for `drm-backend` output matching in doc `05-drm-backend-result.md`.

## Why this is still the goal, not a fallback

The plan's real objective was "a DRM device, so `drm-backend.so` can be used instead of `headless`".
bochs-drm provides exactly that: a genuine KMS device on `/dev/dri/card0`, a modeset-capable CRTC and a
connected connector, all reachable through the same `drmMode*`/`libdrm` API that Weston's `drm-backend.so`
uses. virtio-gpu was only ever the *means*; bochs-drm is a same-purpose means that actually exists in
this tree.

(If virtio-gpu is genuinely required for fidelity, it would have to be backported from 4.2, a larger
change than the display goal needs; nothing in this line of work blocks on it.)
