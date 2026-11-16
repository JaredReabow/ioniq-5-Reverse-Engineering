# Partitioned eMMC image: the authentic esinit chain now hands over to systemd

This closes the gap left open in `vendor-userspace-boot.md` and `vendor-kernel-boot.md`: a
**GPT-partitioned disk image** whose `p1…p17` layout lets the vehicle's own init
(`/lib/systemd/esinit`) run its eMMC recovery and then `exec /lib/systemd/systemd` on its own,
instead of systemd being started directly. The image lives in `work/vm/partimg/rootfs.img`
(a CoW clone of `work/vm/vkernel`; the other workspaces are untouched).

## Result

`init=/lib/systemd/esinit` with `root=/dev/mmcblk0p5` reaches systemd and multi-user, with
**every fstab partition mounted** and **no emergency mode**:

```
[    0.597745]  mmcblk0: p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17
[    2.686642] VFS: Mounted root (ext4 filesystem) on device 179:5.
[eMMC] ***** New partition(rw_data=/dev/mmcblk0p11)
[eMMC] ***** Last Shutdown was OK !!!
[eMMC] ***** Set Check Interval (/dev/mmcblk0p11)
[eMMC] ***** eMMC RW_DATA Partition Check and Recovery Complete!!!
[   10.606623] LGE fan driver initialization
[   11.170715] systemd[1]: systemd 225 running in system mode. (-PAM -AUDIT -SELINUX +IMA …)
[   14.100372] systemd[1]: Reached target Local File Systems.
[   18.316896] systemd[1]: Reached target Basic System.
[   18.332679] systemd[1]: Reached target Login Prompts.
[   75.943989] systemd[1]: Reached target Multi-User System.
```

`local-fs.target` (14.1 s) is the specific thing the single-partition clone could never reach;
it now succeeds because the fstab partitions exist. `dlt-daemon` is actively writing
`/log_data/kernel/kernel_*.dlt` on `mmcblk0p8` at ~296 s (SMACK `granted` lines), i.e. the
`/log_data` mount is live. `result.json` is `"timeout": true` only because the vendor systemd
idles in multi-user, exactly as in the proven `init=/lib/systemd/systemd` run.

## Partition layout

The kernel in a real vehicle announces all 17 partitions on one line (2024-10 field dump,
`evidence/upstream/Ioniq5_Gen5W_Log_Dump/.../kernel/*.dlt`, message split across three DLT
records):

```
mmcblk0: p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17
```

Roles come from `/etc/fstab_emmc`, `/etc/fstab_emmc_fde`, `/lib/systemd/esinit`,
`/etc/fsck_rw_partitions_v2*.sh`, and the AppFUMO inactive-partition table
(`evidence/appfumo-inactive-partition-continuity.md`). Sizes for `p8…p13` are **measured** from
the vehicle's own `e2fsck 1.43.4` logs in `evidence/upstream/.../fs_log/p{8,9,10,11,12,13}.log`
(block size 4096). The rest are documented best-effort estimates.

| p | role | size | basis |
|---|---|---|---|
| 1 | boot/iasImage (PLK1) | 64 MiB | esinit `fsck.ext2/mke2fs -b 4096` on `p1`; iasImage splash (~few MB) |
| 2 | boot/iasPreload (PLK2) | 64 MiB | esinit recovery copies `p2/iasImage ↔ p1/iasImage`; `iasPreload.images.tar.gz` 4.3 MB |
| 3 | **inactive root** slot A | 8 GiB | AppFUMO: active `p5` → inactive root `p3`, inactive boot `p1`, inactive VR `p6` |
| 4 | unknown (never named anywhere) | 16 MiB | placeholder; present in the kernel listing only |
| 5 | **active root** (booted) | 8 GiB | `DMClient.log`: `Current ROOT partition : "/dev/mmcblk0p5"`; `fsck_rw_partition_format.sh` comment “rootfs … mmcblk0p5 for new partition” |
| 6 | VR (slot for p5) | 64 MiB | AppFUMO: active `p5` → inactive VR `p6`; fstab mounts `p6` at `/vr` |
| 7 | VR (slot for p3) | 64 MiB | AppFUMO: active `p3` → inactive VR `p7` |
| 8 | `/log_data` | 2 GiB | measured `524286 × 4K ≈ 2 GiB` (p8.log) |
| 9 | `/update` | 12 GiB | measured `3145726 × 4K ≈ 12 GiB` (p9.log) |
| 10 | `/voicememo` | 150 MiB | measured `38398 × 4K ≈ 150 MiB` (p10.log) |
| 11 | `/rw_data` | 1280 MiB (1.25 GiB) | measured `327678 × 4K ≈ 1280 MiB` (p11.log) |
| 12 | `/Data/mnt-c` **and** `/Data/mnt-wt` | 40 MiB | measured `10238 × 4K ≈ 40 MiB` (p12.log); fstab mounts the same device twice |
| 13 | `/Data/mnt-backup` | 40 MiB | measured `10238 × 4K ≈ 40 MiB` (p13.log) |
| 14 | `/navi` (ro) | 2 GiB | holds AppNavi `Bin/` (488 MiB in the shipped `appnavi.tar`) |
| 15 | `/navi2` (ro) | 2 GiB | fstab second navi slot |
| 16 | unknown (ext4, mounted w/o journal, repeatedly) | 64 MiB | placeholder; kernel logs `EXT4-fs (mmcblk0p16): mounted filesystem without journal` |
| 17 | `/space` (ro) | 256 MiB | fstab |

Total image 36.05 GiB (38 713 425 920 bytes). The 2024 field unit's eMMC is 128 GB
(`mmcblk0: mmc0:0001 DA6128 116 GiB`), so the true 260128 geometry is likely larger than this
projection (larger roots/navi); the ordering, the eight measured sizes, and the A/B slot map are
what esinit depends on, and those are exact.

## Recipe

### 1. Build the image (reproducible)

```
python3.13 work/vm/partimg/build-partitioned-image.py
```

It `sgdisk --zap-all` + 17 `8300` entries, then `mkfs.ext4 -b 4096 -O ^metadata_csum,^64bit,^flex_bg`
per partition. `p5` is populated from `work/decrypted-eu-260128/extracted-safe/mango-rootfs`,
`p11` from its `/rw_data` subtree, `p14` from its `/navi` subtree; the others are empty ext4.
One guest-visible addition is written into `p5` only:

```
/etc/modprobe.d/zz-vm-research-no-lge-usb.conf
    install lge_usb_adapter /bin/true
```

This is the measured one-line neutralisation from `evidence/vm-bringup/esinit-bringup-findings.md`
§9: without it, `lge_usb_adapter`'s probe oopses on non-vendor hardware and leaves the platform
device lock held, so esinit's later `/sbin/modprobe fan` deadlocks forever and esinit never
reaches systemd. (Note: `debugfs -R` splits its command on whitespace, so the source path must be
space-free — the project path contains spaces; the script uses a relative filename and verifies
the write.)

`layout.json` records every partition's byte offset; `prepare.json` carries the current sha256
of `bzImage`/`rootfs.img`/`manifest.bin`/`seed_*.bin`.

### 2. Boot (harness overrides, no `vm_boot.py` edit)

`work/vm/partimg/run-esinit.py` does three things, all visible and recorded in `prepare.json`:

* `vb.KERNEL_SHA256 = sha256(bzImage)` (the vendor kernel `2fec2121…`),
* `vb.INIT_CHOICES = ("/init", "/lib/systemd/esinit", "/lib/systemd/systemd")`,
* monkeypatches `vb.qemu_command` to rewrite the single append token
  `root=/dev/mmcblk0 ` → `root=/dev/mmcblk0p5 `.

That third point is unavoidable and is the **one** documented change to the fixed command line:
`vm_boot` hard-codes `root=/dev/mmcblk0` (whole device). A GPT puts its header/entry array in
LBA 1–33, which overwrites the ext4 superblock at byte 1024, so the whole-device root cannot
mount; the root must be the active-root partition. It is noted here rather than edited silently
in the harness.

```
python3.13 work/vm/partimg/run-esinit.py --init /lib/systemd/esinit --timeout 300
python3.13 work/vm/partimg/run-esinit.py --init /init --timeout 180   # sanity: mounts every pN
```

The `--init /init` sanity run reports `P1_OK … P17_OK` (each `mmcblk0pN` mounts ext4) and
`command_exit_code: 0`, proving the GPT is parsed and every partition is a valid filesystem
before the esinit run is attempted.

## How far esinit gets (this run: `runs/1793789872347394000`)

1. Kernel enumerates `p1…p17`; root mounts from `179:5` (`mmcblk0p5`).
2. esinit completes its pre-flight (OEM/car/ECO/country detection, zram swap,
   `modprobe xhci_pci/lgivi_qmi`, `esinit-modprobe.sh` with `lge_usb_adapter` neutralised).
3. `cryptsetup -v isLuks /dev/mmcblk0p11` reports
   `Device /dev/mmcblk0p11 is not a valid LUKS device.` → `endFde=0` → the **non-FDE** recovery
   `fsck_rw_partitions_v2.sh` runs and succeeds (`Last Shutdown was OK`, `Set Check Interval`,
   `RW_DATA Partition Check and Recovery Complete` — p8 and p11 mount cleanly).
4. `modprobe fan` returns (`LGE fan driver initialization`; its `fail to request gpio` lines are
   benign QEMU no-GPIO noise, as is the known `lge_gps_driver` warning loop).
5. `exec /lib/systemd/systemd` → `systemd 225 running in system mode`, `Set hostname <prm-gen-5>`,
   then `Local File Systems` (14.1 s) → `Basic System`/`Login Prompts` (18.3 s) → `Multi-User`
   (75.9 s). All 11 fstab entries mount (10 unique partitions: `p6,p8,p9,p10,p11,p12`×2,
   `p13,p14,p15,p17`; `p12` is mounted at both `/Data/mnt-c` and `/Data/mnt-wt`), each with
   `EXT4-fs … mounted`.

### First failing line (verbatim)

The first failure is not esinit — esinit finishes. It is a systemd unit, the known vendor exec-bit
bug, and it does **not** gate boot (`check-mount.service` is a `local-fs.target` *Want*):

```
[   13.413109] systemd[1]: check-mount.service: Main process exited, code=exited, status=203/EXEC
[   13.432549] systemd[1]: check-mount.service: Failed with result 'exit-code'.
```

(`/bin/check-mount.sh` is mode 0644 in the vendor tarball — `evidence/vm-bringup/esinit-bringup-findings.md`
§10.1. Left authentic; it is not a boot gate.)

### Remaining failures (all environmental, none block the target)

| unit | first failure (verbatim) | cause |
|---|---|---|
| `auditd.service` | `auditd.service: Main process exited, code=exited, status=6/NOTCONFIGURED` | audit not configured in QEMU |
| `dbus-com.lge.car.micom.service` | `Failed to start System service for micommanager.` | no live MICOM over the platform bus (SPI never arrives) |
| `ApplicationLauncher` etc. | `Dependency failed for HKMC Preminum AVN 2.1 -Launcher.` | `Requires` micommanager |
| `TimeManager.service` | `TimeManager.service: Main process exited, code=exited, status=1/FAILURE` | depends on `pas-daemon`/`connman` |

No `emergency.target`, no `dev-mmcblk0p*.device` timeout, no `status=64` anywhere in the log.

## Caveats / what a fully faithful image still needs

* **`root=` change.** The active-root partition (`p5`) is correct for this build, but booting a
  GPT eMMC necessarily moves the root from the whole device to a partition; this is recorded, not
  hidden.
* **`p3` (inactive root) is empty.** Only the active slot is populated; an A/B-faithful image
  would duplicate the 5.2 GB rootfs into both `p3` and `p5`.
* **`p4` and `p16` roles are unknown.** They exist on the real device (kernel listing) but are
  never named by fstab/esinit/updater; they are placeholders here. `p16`'s observed
  "mounted without journal" behaviour is reproduced only as an empty ext4.
* **`p1/p2` (iasImage/iasPreload) are empty.** esinit's PLK1/PLK2 recovery only triggers on
  `spi_validation_OK` + `i915 splash_error`, neither of which occurs in QEMU (no real MICOM SPI
  data, and no i915 splash error).
* **No live MICOM.** The `micom` platform driver registers and its `oem_type`/`car_type`/`country`
  parameters read back defaults (`1`/`5`/`5`), but the real MICOM SPI handshake never completes
  (`[lge_lcd_init_func] Micom didn't sent SPI data`), so `spi_validation` never becomes 1. That
  keeps esinit's SPI gate in its `NOK` branch (so esinit still does not launch `weston --tty=1`)
  and is why `micommanager` exits 1. This is a hardware-boundary limitation, not an image defect;
  it is the same reason the earlier bind-mount run could not start the HMI.

## Evidence index

| path | content |
|---|---|
| `work/vm/partimg/build-partitioned-image.py` | deterministic GPT + per-partition ext4 builder |
| `work/vm/partimg/run-esinit.py` | harness overrides (kernel hash, init choices, `root=` token) |
| `work/vm/partimg/layout.json` | final p1…p17 sizes and byte offsets |
| `work/vm/partimg/prepare.json` | artifact sha256 + the one documented root-arg change |
| `work/vm/partimg/runs/1793789842554787000/` | `init=/init` sanity: `P1_OK…P17_OK`, exit 0 |
| `work/vm/partimg/runs/1793789872347394000/` | `init=/lib/systemd/esinit`: full handover, local-fs/multi-user |
