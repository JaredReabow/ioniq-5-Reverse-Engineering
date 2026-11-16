# Kernel rebuild: 4.1.27-abl with a DRM device — build, config delta, boot result

Date: 2026-11-06. This is the record of rebuilding a bootable replacement kernel for the EU 260128
Gen5W image from the matching source tarball, with the vendor config reconciled against upstream, and
the measured result: the vendor rootfs boots to Multi-User and a `/dev/dri/card0` exists.

## The input materials (already in the repo)

- `work/kbuild/linux-4.1.27.tar.xz` — the matching upstream source tarball (83,080,176 bytes).
- `work/kbuild/vendor.config` — the vendor's own kernel config (113,598 bytes, 4,238 lines,
  `CONFIG_LOCALVERSION="-abl"`, `CONFIG_SMP=y`, `CONFIG_PREEMPT_VOLUNTARY=y`, `CONFIG_MODULES=y`).

Workspace: `work/vm/kbuild/` (a CoW clone `work/vm/kbuild/ws/` is the boot workspace). Nothing outside
`work/vm/kbuild/` was modified; `work/vm/byhand`, `partimg`, `repro2`, `stockui`, `gesture` are untouched.

## The build

The host is macOS arm64, so this is a cross-build with the Homebrew `musl-cross` GCC (14.2.0) targeting
`x86_64-linux-musl`. Three macOS-specific source patches were required and are recorded in
`work/vm/kbuild/kernel.patch` (details in `03-macos-cross-build-workarounds.md`).

```
# in a no-space copy of the tree (the repo path contains spaces, which the
# kernel build cannot handle — see 03-macos-cross-build-workarounds.md):
make ARCH=x86_64 CROSS_COMPILE=x86_64-linux-musl- olddefconfig   # from vendor.config
# then the config edits in the next section, then:
make ARCH=x86_64 CROSS_COMPILE=x86_64-linux-musl- -j16 bzImage
```

Result:

```
Setup is 16188 bytes (padded to 16384 bytes).
System is 3872 kB
Kernel: arch/x86/boot/bzImage is ready  (#3)
```

- `bzImage` = **3,980,640 bytes**, sha256 `893e1a6ba7fd8fa42a2433b9b6e65730ef3e19d2a56d2154beade80d403a6392`
- kernel self-identifies as `Linux version 4.1.27-abl (leo@Leo.local) (gcc version 14.2.0 (GCC) ) #3 SMP`
  — i.e. `4.1.27-abl` vermagic, `SMP`, `PREEMPT_VOLUNTARY`, matching the vendor's build string.

## Config delta (vendor.config → reconciled .config)

`make olddefconfig` drops every symbol that does not exist in **upstream** 4.1.27, because the vendor
tree was patched (LGE/MICOM/IAS/keystore/SecureBoot/IPU4/Broxton). It also re-derives a few values the
vendor could only have held with its patches applied. The full dropped list (207 symbols) is
`work/vm/kbuild/dropped-symbols.txt`; the consequential ones are categorised below.

Deliberate changes (this is the config delta that matters for the deliverable):

| symbol | vendor.config | final | why |
|---|---|---|---|
| `CONFIG_DRM_BOCHS` | not set | `=y` | **the DRM device driver** — drives QEMU's existing `-device VGA` (Bochs dispi) |
| `CONFIG_DRM_QXL` / `CONFIG_DRM_CIRRUS_QEMU` / `CONFIG_DRM_VMWGFX` | not set | `=y` | alternate QEMU DRM drivers, for completeness |
| `CONFIG_VIRTIO` / `CONFIG_VIRTIO_PCI` | absent / not set | `=y` | requested; note there is **no virtio-gpu** (see 02) |
| `CONFIG_UNIX` / `CONFIG_PACKET` | `=m` | `=y` | systemd 225 is built `-KMOD` and cannot load `unix.ko`; with `=m` it dies with `Address family not supported by protocol` and device units time out |
| `CONFIG_KERNEL_GZIP` | not set | `=y` | Homebrew `lz4` v1.10.0 removed `-l` (legacy) output; the 4.1 LZ4 decompressor only reads the legacy format, so the payload did not decode (`Decoding failed`) |
| `CONFIG_KERNEL_LZ4` | `=y` | not set | see previous row |

Side effect of reconciling against upstream (not a deliberate choice): `CONFIG_FB` came out **`=y`**,
because upstream 4.1.27's `CONFIG_DRM_I915` selects `FB` through `DRM_KMS_FB_HELPER`/`DRM_I915_FBDEV`.
The vendor's tree could build i915 with `# CONFIG_FB is not set` only because it had the 4.3-era
`CONFIG_DRM_FBDEV_EMULATION` knob backported. This reopens the framebuffer path that
`docs/vm/45-backend-is-forced-not-chosen.md` reported closed — a real, if accidental, change.

## What olddefconfig dropped, and why it matters

The vendor-patched drivers are gone, because their source is not in the stock tarball. The trade is
concrete and was measured, not assumed:

1. **`CONFIG_LGE_MICOM` (and `CONFIG_LGE_EXTENDED_CAN_ID`, `CONFIG_LGE_MULTIPLE_CAN_INTERFACE`)** —
   the built-in driver that would have created `/sys/module/micom/parameters/*` **and the CAN
   interface (`can0`)**. Losing it means:
   - no `can0` (the CAN transport the widget-value work needs is gone from this kernel), **and**
   - esinit's SPI gate (`/sys/module/micom/parameters/spi_validation`) can never open, so esinit
     never starts weston. Measured: `100` copies of
     `/init-authentic-hmi.sh: line 20: /sys/module/micom/parameters/spi_validation: No such file or directory`.
   Both are fixed in this kernel by a projection-only `micom` stand-in (see
   `04-micom-and-lge-board-standins.md`).
2. **`CONFIG_LGE_BRD` / the `lge_board` module** — esinit's FDE script
   `/etc/fsck_rw_partitions_v2_fde.sh` reads `/sys/module/lge_board/parameters/lge_mnt_st`; without it
   the script mis-branches and reformats `p9`/`p10` (`[eMMC] Filesystem(/dev/mmcblk0p9) fsck recover
   failed ... force recoverstart[12]`). Harmless here only because the guest disk is `snapshot=on`.
3. **`CONFIG_KEYSTORE*`, `CONFIG_SECURE_BOOT`, `CONFIG_RPMB`, `CONFIG_ABL_*`** — the vendor trust/seed
   plumbing. Absent; the boot proceeds without them (the keystore seeds are loaded by the harness's
   `-device loader` and read by the image's own userspace, not by these kernel drivers).
4. **`CONFIG_INTEL_IPU4*`, `CONFIG_VIDEO_*`, `CONFIG_TOUCHSCREEN_*` (siw/melfas), `CONFIG_SND_SOC_INTEL_*`,
   `CONFIG_PINCTRL_BROXTON`, `CONFIG_INTEL_MEI*`, `CONFIG_USB_*` gadget drivers** — camera, audio,
   touch, pinmux and USB-gadget hardware drivers for the real unit. Not present under QEMU and not
   needed for the display goal.

The honest one-line statement: **this is a stock 4.1.27 kernel wearing the vendor's non-vendor-specific
config, plus the DRM drivers the vendor omitted.** It is not the vendor kernel; the vendor-only drivers
that the vendor's own userspace reads at boot are replaced by projection-only parameter stand-ins.

## Boot result (the deliverable)

Booted with the authentic init path (`--init /init-authentic-hmi.sh --smp 4`) against the 36 GiB GPT
image in `work/vm/kbuild/ws/` (CoW clone of `work/vm/byhand`, `snapshot=on`):

```
[    0.000000] Linux version 4.1.27-abl (leo@Leo.local) (gcc version 14.2.0 (GCC) ) #3 SMP
[    0.553817] [drm] Found bochs VGA, ID 0xb0c5.
[    0.571807] bochs-drm 0000:00:01.0: fb0: bochsdrmfb frame buffer device
[    0.572797] [drm] Initialized bochs-drm 1.0.0 20130925 for 0000:00:01.0 on minor 0
[    0.631805] micom: projection stand-in (spi_validation=1 lcd_type=3 oem_type=1)
[    2.66... ] VFS: Mounted root (ext4 filesystem) on device 179:5.
[   54.012871] systemd[1]: Reached target Multi-User System.
```

- **reaches Multi-User** at ~54 s (vendor kernel: ~97 s; this kernel is faster because it has far fewer
  drivers to probe).
- **`/dev/dri/card0` exists**: `crw------- 1 0 root 226, 0 card0`, with connector
  `/sys/class/drm/card0-Virtual-1/status=connected`. All 17 GPT partitions enumerate
  (`mmcblk0: p1 p2 ... p17`).
- **weston starts** (esinit's SPI gate is open via the micom stand-in; `[apps-check] WAYLAND_SOCKET_UP`
  and a 129,844-byte PNG capture confirm a live compositor).

## Files

- `work/vm/kbuild/bzImage` — the kernel (sha256 above).
- `work/vm/kbuild/build.config` — the final `.config`.
- `work/vm/kbuild/dropped-symbols.txt` — the 207 symbols olddefconfig dropped.
- `work/vm/kbuild/kernel.patch` — the four macOS source patches.
- `work/vm/kbuild/micom.c` — the micom parameter stand-in.
- `work/vm/kbuild/run-kbuild.py` — the boot runner (copy of `run-byhand.py`, `WS` retargeted and
  `compat=False` because the GDB sdhci patch is keyed to the vendor kernel's addresses).
