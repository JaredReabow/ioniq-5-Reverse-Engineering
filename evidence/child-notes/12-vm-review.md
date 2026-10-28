# 12 — Review: is "vendor UI in QEMU" achievable?

> **Historical review; conclusions superseded in part (2026-10-20).** The parent
> reproduced controller binding, ext4 root mounting and interactive userspace
> using a verified VM-memory-only PCI-table adaptation. This review's permanent
> impossibility and key-unobtainability claims were stronger than the evidence.
> The vendor UI remains unrecovered, not proved forever impossible. See
> [`../vendor-kernel-vm.md`](../vendor-kernel-vm.md) for the measured result and
> corrections. A later userspace diagnostic also produced verified graphics
> and keyboard interaction: [`../vendor-kernel-graphics.md`](../vendor-kernel-graphics.md).
> That directly refutes the blanket no-display claim below, without recovering
> the vendor UI. This child was not verified as a Fable-routed reviewer.

Reviewer/planner note. No code written, no experiments run. This is a critique of
the current VM effort plus a forward plan, derived only from the three evidence
documents and the recovered `work/eu-260128/kernel.config`.

---

## 1. Blunt assessment

**"Boot the infotainment UI in QEMU" is not achievable, now or ever, with this
kernel image.** It fails on three independent walls, and the root-device problem
the team is currently fighting is only the first and the *only solvable one*.

**Wall A — the userland is encrypted and unobtainable.** The Qt/QML HMI, the
navigation app and the systemd service set live inside AES-encrypted payloads
(`new_gui.tar.gz`, `appnavi.tar`, `mango-rootfs.tar.gz`). The key is
device-resident (`DecryptToPIPE` + `decryption_key.der`), and the evidence is
explicit that it is not recoverable from the package. Even a perfect root mount
therefore gives us *our own* rootfs, never the vendor userland.

**Wall B — there is no display path QEMU can drive.** This is the one that
kills the goal even if Wall A magically disappeared:

- `CONFIG_FB is not set` — no framebuffer core at all.
- `CONFIG_VGA_CONSOLE not set`, no `FRAMEBUFFER_CONSOLE` — no text console on a
  VGA/text device either. Only `CONFIG_DUMMY_CONSOLE` (80x25, renders nowhere).
- `CONFIG_DRM=y`, `CONFIG_DRM_I915=y` — the *only* display driver is Intel i915
  (Apollo Lake iGPU), which QEMU cannot emulate. There is no `DRM_BOCHS`,
  `DRM_QXL`, `DRM_CIRRUS_QEMU`, or `DRM_VIRTIO_GPU` (all absent), and no
  `VIRTIO_PCI` to carry a virtio-gpu anyway.
- `CONFIG_DRM_FBDEV_EMULATION not set` — even if i915 bound, there would be no
  fbdev shim to put a console on.

So the kernel literally has no output device that exists in QEMU. The only real
console is the serial 8250 console (`CONFIG_SERIAL_8250=y`,
`CONFIG_SERIAL_8250_CONSOLE=y`), which the team has already used.

**Wall C — root device.** `CONFIG_BLK_DEV_INITRD`, `CONFIG_BLK_DEV_RAM`,
`CONFIG_VIRTIO_PCI`, `CONFIG_BLK_DEV_NVME`, `CONFIG_ROOT_NFS`, `E1000/E1000E`,
`NET_9P` are all absent; `CONFIG_ATA/SCSI/BLK_DEV_SD` are `=m` (modules live in
the encrypted rootfs — a chicken-and-egg). The *only* built-in block path is
MMC/SDHCI (`CONFIG_MMC=y`, `MMC_BLOCK=y`, `MMC_SDHCI=y`, `MMC_SDHCI_PCI=y`,
`EXT4_FS=y`, `DEVTMPFS=y`). This wall is real but **it is a QEMU device-ID
matching problem, not a kernel limitation** — solvable (Section 3).

**Verdict:** the honest, achievable objective is *"boot the stock vendor kernel
to a shell in QEMU and interact with it over serial."* That is genuinely useful
for kernel research. It is **not** "the UI of the infotainment system," and any
progress report that implies otherwise will be misleading.

---

## 2. Critique of the plan so far

**Pursuing SD+ext4 was the right call — in fact it was forced.** Given the
config, there is no other built-in block path. Ruling out initrd/ramdisk/virtio/
ATA/SCSI/USB/network root by reading the config was correct and efficient. The
`debugfs`-populated power-of-two SD image trick is sound. Credit where due.

What was missed or mishandled:

1. **The goal was never gated on the block device.** The team framed the
   blocker as "root filesystem," but the display wall (Section 1, Wall B) makes
   the stated UI goal unreachable regardless of whether `mmc0` ever appears. The
   project has been spending effort on the one solvable part while the headline
   objective was already dead on arrival. This should be reframed with the owner.

2. **The decisive experiment (reading the driver's ID table) was deferred
   instead of done.** The evidence says "22 `sdhci_pci_*` symbols, no `mmc0`, so
   the device ID is not in the 4.1 table." That is an *inference*. The team has
   the recovered `vmlinux`, kallsyms (64,923 entries) and Ghidra. The
   `sdhci_pci` `pci_device_id` array (the `pci_ids[]` table) is a small rodata
   array that can be dumped in minutes and would convert the inference into a
   measured fact — including whether a trailing class-code match exists (see
   Section 3). This should have been step one the moment the device failed to
   bind.

3. **QEMU's actual class/vendor/device for `sdhci-pci` was never recorded.**
   A single `info pci` (monitor) or `lspci` capture would distinguish "ID not in
   table" from "class code wrong / device absent." Without it, the failure mode
   is ambiguous.

4. **`CONFIG_MMC_SDHCI_ACPI not set` is a red herring for this setup.** ACPI
   enumeration matters for *platform* SDHCI devices (e.g., the on-SoC Apollo
   Lake eMMC), not for QEMU's PCI device, which is enumerated by the PCI core.
   Chasing the ACPI path would be wasted effort.

5. **Internal documentation inconsistency.** `evidence/vendor-kernel-vm.md`
   opens by claiming the kernel "mounts an ext4 root from an emulated SD card,
   and then panics by design," while the same file's later section correctly
   states the current state is `VFS: Unable to mount root fs` with no `mmc0`.
   The intro overstates progress and should be corrected.

6. **Minor: `CONFIG_LGE_SD_NOTSUPPORT=y` is unexplained.** It sits in the
   `CONFIG_LGE_DRIVER` block and is probably board-specific (no physical SD slot
   on some variants), but it is worth a 5-minute check that it does not gate the
   generic `MMC_BLOCK`/`sdhci-pci` path before more time is spent. It likely
   does not, but "likely" should be confirmed.

7. **The plan under-weighted the "what runs after root mounts" question.** With
   the vendor rootfs unavailable, the substitute userspace is everything. The
   relevant constraint set (no framebuffer, `CONFIG_UNIX=m`, no built-in NIC,
   SMACK default LSM) was never enumerated before picking the root-device fight.

---

## 3. How to make QEMU's `sdhci-pci` bind to the 4.1 driver

**The ID-matching problem.** `sdhci-pci` is built-in (`CONFIG_MMC_SDHCI_PCI=y`),
so its `module_init` runs at boot and registers a `pci_driver` with an
`id_table`. The PCI core only calls `sdhci_pci_probe` if the device's
vendor/device/subvendor/subdevice/class/class_mask match an entry in that table.
QEMU's `sdhci-pci` (`hw/sd/sdhci-pci.c`) reports **Red Hat `0x1b36:0x0007`**
with class `0x0805` (SD Host Controller). `0x1b36:0x0007` is not in the 4.1
table, so nothing binds, no `mmc0`, no `mmcblk0`, no root.

Two facts are still unknown and both are cheap to establish:

- Does this vendor build carry the trailing **class-based generic match**
  (`PCI_DEVICE_CLASS(PCI_CLASS_SYSTEM_SDHCI << 8, 0xFFFF00)`), which upstream
  `sdhci-pci` has carried for a long time? If present, it would bind *any* class
  `0x0805` device regardless of vendor/device.
- What class does QEMU 11.1.2 actually report for `sdhci-pci` on `q35`? If it is
  not `0x0805`, even a class-based match would miss.

**Realistic options, ranked:**

1. **Dump `pci_ids[]` from the recovered `vmlinux` (do this first, decisive).**
   Find the `sdhci-pci` driver's `pci_device_id` array (Ghidra / the kallsyms
   base, near the `sdhci_pci_driver` struct; 4.1's `struct pci_device_id` is
   32 bytes: vendor, device, subvendor, subdevice, class, class_mask,
   driver_data). Emit every `(vendor, device)` and whether any entry has
   `class = 0x0805` / mask `0xFFFFFF`. This yields the exact spoofable ID list
   and settles whether class matching exists. *Information gain: maximal,
   near-zero effort.*

2. **Record QEMU's view of the device.** Boot once with `-monitor stdio` and run
   `info pci` (or add `-d pci` / use `lspci` from a host tool). Confirm the
   device is actually on the bus and record its class/vendor/device. *Cheap,
   removes ambiguity.*

3. **Patch QEMU's `sdhci-pci` to report a table-listed ID, then rebuild.** Edit
   `hw/sd/sdhci-pci.c` (vendor/device constants, and set class to `0x0805` if it
   is not already), rebuild `qemu-system-x86_64`, boot with
   `-device sdhci-pci -device sd-card,drive=sd0`. This is **entirely under our
   control and does not touch the vendor kernel.** If the table has the class
   match and QEMU's class is correct, no patch is needed at all. This is the
   path that actually unblocks `mmc0`/`mmcblk0`/ext4 root.

4. **`new_id` force-bind via sysfs — ruled out.** The driver is built-in and the
   root device must exist *before* `/sbin/init`; there is no shell to echo to
   `/sys/bus/pci/drivers/sdhci-pci/new_id`. Useless for the root problem.

5. **`generic-sdhci` (platform/SDHCI_PLTFM) — ruled out.** QEMU's
   `generic-sdhci` is a sysbus/MMIO device, not attachable to the `q35` PCI bus
   without a custom machine/device-tree; `CONFIG_MMC_SDHCI_PLTFM=y` is present
   but unreachable here.

6. **Alternative built-in PCI block controller — none exists.** Scan of the
   config shows no other `=y` block controller (SATA/PATA/SCSI/USB-storage are
   all `=m`; NVMe/virtio absent). `sdhci-pci` is the only lever.

Expected residual risk after the bind: QEMU's SDHCI register emulation vs. the
4.1 driver (SDHCI spec version, ADMA2, 64-bit DMA). QEMU 11.x should be
serviceable for a basic SD card, but a quirk mismatch is possible; that is the
next thing to watch after `mmc0` appears.

---

## 4. A substitute interactive UI — what serial-only can and cannot show

Once root mounts, the kernel runs `/sbin/init` from **our** SD image. The only
real console is `ttyS0`. So the ceiling is a serial terminal, not a display.

**What can actually run (built-in, no vendor modules):**

- `CONFIG_BINFMT_ELF=y`, `BINFMT_SCRIPT=y` — plain x86-64 binaries/shell
  scripts (note `CONFIG_IA32_EMULATION not set`: 64-bit only).
- `CONFIG_SERIAL_8250_CONSOLE=y` — a real login shell / getty on `ttyS0`.
- `CONFIG_EXT4_FS=y`, `TMPFS=y`, `PROC_FS`, `SYSFS`, `DEVTMPFS=y` +
  `DEVTMPFS_MOUNT=y` — a normal Linux userspace view.
- `CONFIG_BLK_DEV_LOOP=y`, `BLK_DEV_DM=y` (+ `DM_CRYPT`) — loop mounts and
  device-mapper are available *after* root, for extra images.
- `CONFIG_IKCONFIG_PROC=y` — `/proc/config.gz` self-documents the running kernel.
- `CONFIG_DEVMEM=y`, `DEVKMEM=y`, no `STRICT_DEVMEM` — `/dev/mem`, `/dev/kmem`,
  `/proc/kcore` for deep inspection (a research asset, see Section 6).
- `CONFIG_KEXEC=y`, `PSTORE` — alternate-kernel and panic-log research.

**Hard constraints on the substitute userland:**

- **No framebuffer, no pixels.** The most one can build is a *text-mode* TUI
  (ncurses/dialog-style menus, a `bash`/`busybox` shell, `dmesg`, `cat
  /proc/kcore`, reading `/sys/kernel/abl/*`). That is the entire "UI."
- **No network.** `CONFIG_INET=y` and `CONFIG_IP_PNP=y` exist, but **no NIC
  driver is built-in** (`E1000/E1000E/IGB` absent or `=m`; no virtio-net; no
  `NET_9P`; SLIP is `=m`). There is nothing for `ip=` to configure.
- **`CONFIG_UNIX=m`** — AF_UNIX is a *module*, and modules live in the encrypted
  vendor rootfs. A minimal `busybox` + `getty` works without it, but systemd,
  dbus, Wayland/X and most IPC-based services will not. Rebuilding a matching
  `unix.ko` for a patched 4.1.27 is a later, bounded effort — not needed for a
  shell demo.
- **Everything `=m` is unavailable** unless a matching `.ko` is rebuilt (USB
  host/storage, ATA/SATA, FAT/VFAT, sound, most netfilter). Rebuilding vendor
  modules is disproportionate effort and does not lead to a UI.
- **SMACK is the default LSM** (`CONFIG_DEFAULT_SECURITY="smack"`). A substitute
  rootfs without SMACK labels will exercise the bring-up path
  (`CONFIG_SECURITY_SMACK_BRINGUP=y`), which should permit an unlabeled
  busybox, but a hostile/empty policy interaction is a known unknown for the
  first userspace boot.

**What a serial-only "UI" demonstrates:** full boot to userspace on the stock
kernel; interactive shell; kernel log (`dmesg`) and `/proc`/`/sys` inspection;
the keystore/manifest init output; `/sys/kernel/abl/` parameter exposure;
read-only probing of `/proc/kcore`, `/dev/mem`, `/dev/kmem`; kexec/pstore
behavior. That is a legitimate research harness.

**What it cannot demonstrate:** any pixel, the Qt/QML HMI, touch input, the
navigation app, systemd/dbus service behavior, network services, or any vendor
module. Anyone expecting "the infotainment UI" from this VM will be
disappointed by design.

---

## 5. Ranked plan — next 3 steps

1. **Dump and publish the `sdhci-pci` `pci_ids[]` table from `vmlinux`, and
   capture QEMU's `info pci` for `sdhci-pci`.**
   *Information gain:* converts "the ID isn't in the table" from assumption to
   fact; reveals the exact spoofable `(vendor,device)` set; reveals whether a
   class `0x0805` generic match exists; reveals whether QEMU's class is wrong.
   Decides step 2's shape with zero further guessing.

2. **Make `sdhci-pci` bind** (patch/rebuild QEMU's `hw/sd/sdhci-pci.c` to an
   ID from the table, or confirm class-match and change nothing), then boot to
   `mmcblk0` and an ext4 root mount.
   *Information gain:* the actual unblock — proves the "MMC is the only built-in
   block path" theory end-to-end and gets the kernel past
   `VFS: Unable to mount root fs`.

3. **Populate the SD image with a static x86-64 `busybox` (init + sh + getty on
   `ttyS0` + mount/proc/sys) and reach an interactive serial shell.**
   *Information gain:* the first real demonstration that the stock vendor
   kernel runs to userspace under our control; yields the serial research
   console for `/proc`, `/sys/kernel/abl/`, dmesg, `/proc/kcore`, etc.; and
   definitively shows the owner what the ceiling is (a serial shell, not a UI).

**Explicitly wasted effort (do not spend time on):**

- Retrying initrd/ramdisk, virtio-blk, SATA/ATA/SCSI, USB-storage, NVMe, or
  network root — all `=m` or absent; the config already rules them out.
- Any attempt to get a graphical console/framebuffer in QEMU — impossible with
  this config (no FB, no VGA console, only un-emulatable i915).
- Decrypting/repacking `new_gui.tar.gz` / `mango-rootfs.tar.gz` to run the real
  UI in the VM — key is device-resident and unobtainable.
- Chasing `CONFIG_MMC_SDHCI_ACPI` — irrelevant to a PCI-attached QEMU device.
- `new_id` force-bind before userspace — impossible without a shell, and moot
  for root mounting.

---

## 6. Safety and scope concerns to raise with the owner

1. **Reframe the objective before more work.** "Infotainment UI in QEMU" is not
   deliverable. Propose the achievable goal: a serial-interactive stock-kernel
   research harness. Get explicit sign-off so the team is not later accused of
   over-claiming.

2. **Do not present a serial shell as "the UI."** It would misrepresent
   progress to a non-technical owner and inflate expectations about what QEMU
   can show of this product.

3. **Keep the keystore/manifest emulation clearly scoped as bench-only.** The
   `ABL.oemkm=` / `ABL.seed=` synthetic parameters make the *emulated* kernel
   initialize; they do not weaken the real unit, yield real keys, or constitute
   a vehicle-security bypass. State this explicitly in any write-up, especially
   given `CONFIG_KEYSTORE_TESTMODE=y` and `CONFIG_KEYSTORE_SECURE_BOOT_IGNORE=y`
   also surfaced in the config — those are real-device findings to record, not
   something the VM exercises meaningfully.

4. **`/dev/mem` + `/dev/kmem` + `/proc/kcore` + no `STRICT_DEVMEM` + `KEXEC`
   are powerful post-entry primitives on real hardware.** In the VM they are
   safe; but any write-up connecting them to the vehicle should carry the same
   defensive caveats already used in `eu-custom-firmware-feasibility.md`
   (privilege + SMACK policy remain unproven on stock `260128`).

5. **Stay bench-only.** No hardware, no flashing, no vehicle. The current
   course is entirely emulator-side and legally/safety-clean; keep it that way,
   and keep the recovered build-path/keystore strings as documentation, not as
   an invitation to hunt for real key material.

6. **Fix the stale intro in `vendor-kernel-vm.md`** (it claims an ext4 mount +
   deliberate panic, which is no longer the current state) so the record matches
   reality and the next reader doesn't repeat the misread.
