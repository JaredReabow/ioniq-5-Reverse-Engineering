# Booting the vendor's own kernel in the projection

Until now the projection ran a research `bzImage`, which is why USB never worked: the vendor's modules are built against a kernel
whose USB core is modular, and the research kernel does not export the symbols they need (`usbcore: Unknown symbol usb_speed_string`).
The image ships the real thing.

## Where it is

```
work/decrypted-eu-260128/extracted-safe/mango-rootfs/boot/bzImage-4.1.27-abl      (5,327,072 bytes)
sha256 2fec21219b4e52c90d287687…
```

It identifies itself as `4.1.27-abl #1 SMP Wed Jan 28 16:00:10 KST 2026`, matching the `260128` build, and its own warnings disclose
the build tree:

```
/data001/vc.integrator/__EVENT_BUILD_s5w.26ru1.251203_MASS_PRODUCT_26RU1_001_260121101627/build-mango/BUILD/work-shared/5w/kernel-source/...
```

i.e. `s5w.26ru1.251203`, `MASS_PRODUCT`, `26RU1_001`, built 2026-01-21.

## How to boot it

`vm_boot` pins the research kernel by hash, so a vendor-kernel workspace overrides the check rather than editing the harness:

```python
import hashlib, sys; sys.path.insert(0, 'tools/uk_fw')
import vm_boot as vb
from pathlib import Path
ws = Path('work/vm/vkernel').resolve()          # a CoW clone with bzImage replaced
vb.KERNEL_SHA256 = hashlib.sha256((ws / 'bzImage').read_bytes()).hexdigest()
vb.run(ws, True, command, timeout=300.0, memory_mib=2048, extra_devices=[...])
```

`work/vm/vkernel/prepare.json` must carry the new `sha256.bzImage` value, which `verify_workspace` checks.

## What it fixes

USB works for the first time in this project. With `piix3-usb-uhci` plus `usb-storage`, and the vendor modules loaded by explicit
path, a USB stick enumerates:

```
ok usb-common.ko · ok usbcore.ko · ok scsi_mod.ko · ok sd_mod.ko · ok uhci-hcd.ko · ok usb-storage.ko
uhci_hcd 0000:00:02.0: new USB bus registered, assigned bus number 1
BLOCK=/dev/sda
0QEMU    QEMU HARDDISK   INJECT01          <- the vendor's own scsi_id reading the serial
```

Module load order matters: `usb-common.ko` **before** `usbcore.ko`, and both before `uhci-hcd.ko`. Getting that order wrong is what
made earlier attempts report `Unknown symbol` and conclude, wrongly, that USB was unavailable in principle.

## What it does not fix

- **`/lib/systemd/esinit` still does not reach systemd.** It recovers eMMC partitions `p8`–`p12`, then stops at
  `[FDE] ***** use fstab for non FDE`. Our clone has a single partition, so the fstab mounts it expects cannot succeed. Reaching udev
  therefore needs either a multi-partition image or a different, minimal path to start `systemd-udevd`.
- **QEMU cannot emit a crafted SCSI serial.** V-014's remaining half needs control characters inside the INQUIRY/product strings.
  `usb-storage` caps `serial` at 20 characters, and `usb-bot` + `scsi-hd` accepts 36 but the property parser will not carry a newline:
  passing `serial=\nSYSTEMD_WANTS=debug-shell.service` silently yields the `device_id` instead, and `scsi_id` prints one clean line

  ```
  0INJECT  INJECT          STICK01
  ```

  So the injection cannot be produced by this emulator. It needs a programmable SCSI bridge on real hardware, not a QEMU device.
