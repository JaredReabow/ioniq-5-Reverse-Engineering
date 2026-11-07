# Root cause of "no frame": the vendor launcher's LD_LIBRARY_PATH excludes the two libraries swrast needs

Date: 2026-11-08. **Offline only. No QEMU run this turn.** Evidence: the staged `p5.img`, the extracted
vendor rootfs, and the run-3 stderr already recorded in `docs/kernel/45`.

This is the precise mechanism behind `DRI2: failed to open swrast` → `failed to initialize EGL` →
`wl_surface.commit()` with no `attach()` → nothing drawn. It is a projection defect, not a vendor one.

## The chain, each link measured

### 1. The vendor launcher overwrites `LD_LIBRARY_PATH`

`<rootfs>/app/bin/AppLauncher.sh`:

```sh
export LD_LIBRARY_PATH=/app/lib:/navi/navi/Lib
export LD_PRELOAD=/usr/lib/libEGL.so.1
export XDG_RUNTIME_DIR=/var/run/user/root
export QT_QPA_PLATFORM=wayland
```

The assignment **replaces** whatever the unit environment provided. The projection's drop-in
(`50-vm-gl.conf`) sets `LD_LIBRARY_PATH=/opt/software-egl18/lib:/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib`
— and that value is discarded by the script before any app is exec'd.

### 2. The vendor `libEGL` is Mesa 11.2.1 and loads DRI drivers

`/usr/lib/libEGL.so.1 → libEGL.so.1.0.0`, built from `mesa/2_11.2.1-r3`, with `src/loader` and
`src/mesa/drivers/dri/common` present. Its DRI loader resolves a driver by name from its search paths,
which is why the error names `/usr/lib/dri`.

The vendor image's own `/usr/lib/dri` holds only `i965_dri.so`, `i965_drv_video.so`, `iu3d9_dri.so` —
**no software rasteriser at all**. There is no hardware path in a QEMU VM, so a swrast driver is
required and must be supplied.

### 3. A swrast *is* staged — and it cannot load

`/usr/lib/dri/swrast_dri.so` is present in the staged `p5.img` (inode 246663, 12,369,472 bytes). Its
`DT_NEEDED` list, from the staged bytes:

```
libz.so.1  libglapi.so.0  libsensors.so.4  libpthread.so.0  libdl.so.2
libexpat.so.1  libdrm_nouveau.so.2  libdrm_radeon.so.1  libdrm_amdgpu.so.1  libdrm.so.2
libLLVM-6.0.so.1
```

Every one of those resolves on the app's effective path (`/app/lib:/navi/navi/Lib`, `/usr/lib`, `/lib`)
**except two**:

| Needed library | Present in `/usr/lib`? | Present in `/opt/software-egl18/lib`? |
|---|---|---|
| `libsensors.so.4` | **no** | yes |
| `libLLVM-6.0.so.1` | **no** | yes |

So `dlopen("/usr/lib/dri/swrast_dri.so")` fails on the missing dependencies, the loader reports
`failed to open swrast`, `eglInitialize` returns false, the app never creates a buffer, and its
`wl_surface.commit()` arrives with nothing attached.

**The projection put those two libraries only in `/opt/software-egl18/lib`, and the vendor script
throws that directory away.** That is the whole fault.

## Why this is a projection defect, not a vendor one

On the real vehicle the vendor `libEGL` finds a hardware DRI driver (`i965`/`iu3d9`) and never needs
swrast. There is no `swrast_dri.so` in the image because the vendor never ships one. The software
path, and therefore the two extra libraries, are ours. Nothing here contradicts vendor behaviour.

## The fix, and why one option is preferred

| Option | Change | Assessment |
|---|---|---|
| **A (preferred)** | Stage `libsensors.so.4` and `libLLVM-6.0.so.1` into `/usr/lib` in the image, where the vendor loader already searches | Touches no vendor file; supplies missing shared objects where the existing search path looks. Matches the project rule to prefer projection-side fixes |
| B | Edit `AppLauncher.sh` to prepend `/opt/software-egl18/lib` | Works, but alters a vendor script the project already patches, and adds another vendor-byte divergence to track |

Option A is one staging addition. It should be recorded in `prepare.json`'s `guest_additions` like
every other projection-only file, so the divergence stays enumerated.

## What must NOT be concluded from this

- Not "the app is broken". It is a rendering environment that cannot load its rasteriser.
- Not "the IVI layout is the blocker". Gap 2 from `docs/kernel/45` — layout `visibility(0)`/`layer(nil)`
  — is separate and still open. Fixing EGL would give a committed buffer; it would not by itself make
  the surface visible or layered.
- Not "REGISTRATION_PRESENT means anything about rendering". Run 3 already demonstrated the opposite.

## Next exact action

1. **Stage the two libraries into `/usr/lib`** as a projection-only addition, recorded in
   `prepare.json` `guest_additions`, and verify with `debugfs` that both resolve from the vendor
   search path.
2. Then, and only then, a run. Its pre-commitment: the app should reach `eglInitialize` success and
   issue `wl_surface.attach(...)` before `commit()`. That is a **binary** observation available in the
   export payload with no new tooling — attach present or absent. If attach appears and the screen is
   still the splash, gap 2 is isolated as the remaining blocker.
