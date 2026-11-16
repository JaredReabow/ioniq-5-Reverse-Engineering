# Attack chain and the dynamic-USB rig

## On-car chain (physical USB access only — no root, no private key)

1. **Pass the version gate.** Build a USB update the HU accepts (same-version reinstall of
   260128 works; the HU confirms `collectUSBPartitionImages: update source is encrypt file:
   mango-rootfs.tar.gz`, i.e. the rootfs *is* a real install target of this update).
2. **Leave the boot image genuine.** The bootloader RSA covers only `iasImage`; we never
   touch it, so its signature stays valid.
3. **Back the rootfs file with a dynamic block device.**
   - During `md5sum` + `PKCS#1 sig. verify` (the **check**) → serve the **genuine signed**
     `mango-rootfs.tar.gz` (TE2). The check passes on real, signed bytes.
   - During `DecryptToPIPE … | tar` (the **install**) → serve the **evil** TE2 envelope
     (same size/IV, encrypted with the known content key) carrying the attacker rootfs.
4. **A/B switch activates the swapped rootfs** (`[USB-UPDATE] SWAP FINISH`); it is plain
   ext4 with no dm-verity, so it mounts and runs at next boot = persistent root.

The rootfs file is opened **exactly twice** on the car (confirmed by native execution, see
`docs/03-evidence.md`): pass #1 = `ionice -c3 md5sum` (the RSA verify is over `md5sum.txt`,
not a re-read of the 879 MB rootfs), pass #2 = `DecryptToPIPE | tar`. So the correct swap
point is **`switch_after_pass = 2`**: md5 reads genuine, the installer reads evil.

## The rig: Raspberry Pi Zero 2 W as dynamic mass storage

```
  Head unit (USB host)
        │  USB
        ▼
  dwc2 UDC  (BCM2835, dr_mode=peripheral)        ← config.txt: dtoverlay=dwc2 under [all]
        │
  configfs USB gadget  (f_mass_storage)
        │   lun.0.file = /dev/nbd0   (removable, rw, VID:PID 0781:5591 "USB DISK")
        ▼
  /dev/nbd0  ──  nbd-client 127.0.0.1:10809  ──  nbdkit  (Python plugin)
                                                     │
                                          nbdkit_toctou.py  +  usb.img (27 GB exfat)
```

- **`usb.img`** is a 27 GB exfat filesystem (label `IONIQ5_EU`) holding the genuine
  package. The `mango-rootfs.tar.gz` is written **first** so it occupies one contiguous
  extent; `regions.json` records that extent (`off`, `len`) from `filefrag`.
- **`nbdkit_toctou.py`** serves `usb.img` verbatim **except** inside the rootfs region,
  where it returns genuine or evil bytes depending on the current read pass. The rootfs
  (~879 MB) exceeds Pi RAM (512 MB), so the host cannot cache it — every pass reaches the
  plugin.

## Swap trigger: return-to-start-after-deep

The decisive logic is *when* to flip from genuine to evil. The HU reads the big file
largely sequentially, but it reads the **tail first** and caches the last blocks, so a
naïve "previous pass reached the end" trigger never fires (the sequential read stops short
of the end). The robust trigger used in `nbdkit_toctou.py` is:

```python
near = offset <= region_start + min(0x10000, max(0x1000, len >> 3))
deep = max_offset_seen >= region_start + (len >> 1)     # previous reads went past halfway
new_sweep = near and not previously_near and (first_read or deep)
```

A **new sweep** = a read that returns to the region-start zone after the previous reads
went at least halfway in. This survives tail-first reads and block caching. Counting
sweeps 1-based, the plugin serves genuine for passes `< switch_after_pass` and evil from
`switch_after_pass` onward. This was validated by replaying a real 429 k-read car trace
through the plugin (switch fires exactly at the install-pass start) **and** confirmed on
the real head unit (the install pass flipped to EVIL). See `docs/04-field-journal.md`.

## Offline-robust logging

The car is out of Wi-Fi range and the Pi has no RTC, so logging is hardened to be readable
from the SD card alone:

- every line carries `<wall> mono=<CLOCK_MONOTONIC>` (monotonic orders events despite clock
  steps); key events are `fsync`'d;
- per-connection `SESSION START/END` headers carry the kernel **`boot_id`** — order cycles
  by `boot_id` + append position, never by wall clock (which can step backwards across a
  reboot);
- per-pass tallies: `PASS #n END … served=GENUINE|EVIL|MIXED bytes_evil=…`;
- every rootfs-region read is logged to `/var/log/toctou-reads.log` (persistent fd, periodic
  `fsync`) so an hour-long update is fully traceable even if power is cut.

The decisive evidence of success is the **install pass (#2, after the SWITCH)** showing
`served=EVIL` with `bytes_evil ≈ 879,109,759` (the rootfs body). Definitive on-device proof
remains the marker (`/var/log/TOCTOU_ROOT_PROOF`, or an IMEI/Modem-Info string).
