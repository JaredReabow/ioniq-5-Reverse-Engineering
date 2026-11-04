# Tuxera filesystem-driver probe (V-057): crafted-media sweep against `texfat` / `tntfs`

**Date:** 2026-11-05 · **Build:** EU NE.EUR.S5W_L.001.001.260128 · **Kernel:** 4.1.27-abl (vendor)

## Verdict

**No fault observed.** Twenty crafted images across nine mutation classes were mounted through the vendor
kernel's own closed-source Tuxera drivers (`texfat.ko` 3016.6.23.3, `tntfs.ko` 3016.7.1.2.3). Every image was
either mounted cleanly or rejected cleanly by the driver's own validation. No crafted image drove either
module into an oops, panic, BUG, or general-protection fault: zero fault lines landed in `texfat`/`tntfs`
across all 23 boots. The drivers were demonstrably reachable and parsing (both clean images mounted with
the driver's own `info`/`version` lines), so the negative is not an artifact of the drivers failing to load.

---

## 1. Method

### 1.1 Workspace

A CoW clone of the vendor-kernel workspace, used exclusively (the parent was never touched):

```
cp -cR work/vm/vkernel work/vm/tuxfuzz
```

`work/vm/tuxfuzz/bzImage` is the vendor kernel (sha256 `2fec2121…`). The pinned-kernel hash is overridden
at run time rather than editing the harness:

```python
import hashlib, sys; sys.path.insert(0, 'tools/uk_fw'); import vm_boot as vb
ws = Path('work/vm/tuxfuzz').resolve()
vb.KERNEL_SHA256 = hashlib.sha256((ws/'bzImage').read_bytes()).hexdigest()
vb.run(ws, True, "sh /run-tuxera.sh texfat", timeout=200, memory_mib=2048,
       extra_devices=[...])
```

USB stick attachment (verified this session, `TUXFUZZ_DEV_FINAL=/dev/sda` every run):

```
-device piix3-usb-uhci,id=u0
-drive if=none,id=stick,format=raw,snapshot=on,file=<image>
-device usb-storage,bus=u0.0,drive=stick,serial=TESTSTICK
```

`snapshot=on` means a guest write can never persist back into a crafted image (and the probe also mounts
`ro,nodev,nosuid,noexec`).

### 1.2 Guest probe

`work/vm/tuxfuzz/probe-scripts/run-tuxera.sh` is injected into the rootfs at `/run-tuxera.sh` via
`/opt/homebrew/opt/e2fsprogs/sbin/debugfs` (never `/tmp`), and `prepare.json`'s `sha256.rootfs.img` is
refreshed after each injection (`work/vm/tuxfuzz/inject.sh`). The probe:

1. `insmod` in the verified order — `usb-common.ko`, `usbcore.ko`, `scsi_mod.ko`, `sd_mod.ko`,
   `uhci-hcd.ko`, `usb-storage.ko` — then `insmod` the Tuxera module by path
   (`/lib/modules/4.1.27-abl/kernel/fs/texfat.ko` or `tntfs.ko`).
2. Waits for `/dev/sda`, then `mount -n -t texfat|tntfs -o ro,nodev,nosuid,noexec /dev/sda /tuxmnt`.
3. Records the mount return code, the `/proc/mounts` line, `ls -lan /tuxmnt`, then reads every file with
   `md5sum` (bounded by `timeout 8`) so that directory-entry parsing **and** the data/cluster-chain read path
   are both exercised.
4. Dumps `dmesg` lines matching `texfat|tntfs|BUG:|Oops|panic|general protection|unable to handle|KASAN`.

Markers (`TUXFUZZ_*`) are grepped from the serial log; the vendor's `lge_gps_driver`/`gpio-ctl` warning
flood is filtered rather than read linearly. The filesystem type strings the modules register are `texfat`
and `tntfs` (from `alias=fs-texfat` / `alias=fs-tntfs`; both `depends=` empty).

The host driver (`work/vm/tuxfuzz/run_probe.py`) and batch runner (`work/vm/tuxfuzz/batch-run.py`) drive
`vm_boot.run`, parse the serial markers, and write `work/vm/tuxfuzz/results.json` + `results.csv`.

### 1.3 Test-image provenance

- **exFAT (clean):** `hdiutil create -megabytes 32 -fs ExFAT -volname TXF -layout NONE` → raw 32 MiB
  superfloppy (no partition table), 512-byte sectors, 8 sectors/cluster (4096 B), 8160 clusters, root at
  cluster 5. sha256 `97fa5942…d409912`.
- **exFAT (with files):** the clean image attached read-write (`hdiutil attach`), then `HELLO.TXT` (12 B),
  `BIG.BIN` (100 KiB, 25 contiguous clusters), and a 255-char-name file written, then detached.
  sha256 `c6b6eac8…a93e8788`.
- **NTFS (clean):** no `mkntfs` exists on macOS; the 64 MiB image was produced by the parallel lineage's
  Alpine `ntfs-3g-progs 2026.9.18` `mkntfs` (`work/public-vuln-research-20261101/fs-probes/clean-ntfs-64m.img`,
  volume name `TUXNTFS`, NTFS 3.1, 4096-byte clusters). Copied to `work/vm/tuxfuzz/images/tux-ntfs-base.img`,
  sha256 `220ad1d0…295cde`.
- **Crafted images:** `work/vm/tuxfuzz/images/gen-mutations.py` copies a baseline and applies exactly one
  documented byte-range edit (or one truncation) per image, writing `manifest.json` with the source, the
  sha256 of every output, and the byte range changed. Directory-entry mutations that alter an entry set also
  **recompute the exFAT entry-set checksum** so the mutation reaches the deep parser instead of being
  rejected at the checksum gate.

All 20 crafted images and their byte-level edits are listed in
`work/vm/tuxfuzz/images/manifest.json`.

---

## 2. Baseline (the instrument produces a positive)

Both clean images mount through the drivers, so a later "nothing happened" cannot mean "the driver never ran".

**exFAT — `TUXFUZZ_MOUNT_RC=0`:**

```
[    6.789734] texfat info: exFAT volume name 'TXF' version 1.0.
/dev/sda on /tuxmnt type texfat (ro,nosuid,nodev,noexec,relatime,uid=0,gid=0,umask=0022,codepage=437,iocharset=utf8,min_prealloc_size=64k,max_prealloc_size=32640,writeback_boundary=4M,readahead=4M,fail_safe,hidden=show,errors=continue)
```

**NTFS — `TUXFUZZ_MOUNT_RC=0`:**

```
[    7.002691] tntfs info (device sda, pid 768): load_system_files(): NTFS volume name 'TUXNTFS', version 3.1 (cluster_size 4096, PAGE_SIZE 4096).
/dev/sda on /tuxmnt type tntfs (ro,nosuid,nodev,noexec,relatime,uid=0,gid=0,umask=022,nls=utf8,min_prealloc_size=64k,max_prealloc_size=65532,readahead=4M,user_xattr,case_sensitive,fail_safe,hidden=show,dotfile=show,errors=continue,mft_zone_multiplier=1)
```

The `files` baseline (which contains a 255-character filename — the format's maximum — and a 100 KiB file)
also mounts and reads cleanly, exercising the name-length and multi-cluster read paths without a fault.

---

## 3. Results table

`rc` is the `mount` return code (`0` = mounted; `255` = driver/VFS rejected the volume). "Kernel message"
is the first driver-attributable line (address/module range or a message naming the driver's own parser).
**No row produced a fault line.**

| Image | Class | rc | Kernel message (verbatim, driver-attributable) |
| --- | --- | --- | --- |
| `tux-exfat-base.img` | baseline | 0 | `texfat info: exFAT volume name 'TXF' version 1.0.` |
| `tux-exfat-files.img` | baseline (files + 255-char name) | 0 | same volume line; all files read cleanly |
| `tux-ntfs-base.img` | baseline | 0 | `tntfs info … NTFS volume name 'TUXNTFS', version 3.1` |
| `exfat-fatlen-huge.img` | truncated allocation table (FatLength=0xFFFFFFFF) | 255 | `mount … failed: Invalid argument` |
| `exfat-clustercount-huge.img` | entry count > table (ClusterCount=65536, FAT holds 16384) | 255 | `mount … failed: Invalid argument` |
| `exfat-rootcluster-past.img` | root dir cluster past volume (0xFFFFFFF0) | 255 | `mount … failed: Invalid argument` |
| `exfat-spc-25.img` | absurd cluster size (SectorsPerClusterShift=25) | 255 | `mount … failed: Invalid argument` |
| `exfat-bps-12.img` | absurd sector size (BytesPerSectorShift=12) | 255 | `mount … failed: Invalid argument` |
| `exfat-truncated-body.img` | valid header, body truncated to 256 sectors | 255 | `mount … failed: Invalid argument` |
| `exfat-root-fat-cycle.img` | cluster chain cycles (root-dir FAT[5]=5) | 255 | `texfat error … exfat_map_cluster_chain(): infinite chain`; `… Inode 0x10 has corrupt cluster chain.` (→ EIO) |
| `exfat-file-fat-cycle.img` | cluster chain cycles (file 11→12→11) | 0* | `texfat error … exfat_map_cluster_chain(): infinite chain`; `exfat_file_open(): Failed to map cluster chain … (error 5)` |
| `exfat-file-datalen-huge.img` | file DataLength=2⁶⁴−1, ValidDataLength=12 | 0* | `texfat error … has valid_data_length 0xc which exceeds the file_size 0xffffffffffffffff. Inode is corrupt.` |
| `exfat-file-firstcluster-past.img` | file first cluster past volume | 0* | (no error; file exposed as size 0, read as empty) |
| `exfat-name-overread.img` | NameLength=255 with 2 secondary entries | 0* | `texfat error … File record has invalid number of secondary entries (must be at least 18 but have only 2)` |
| `exfat-secondarycount-huge.img` | 63 secondary entries claimed, 2 present | 0* | `texfat error … Expected secondary, in-use directory entry but got entry of type 0x85.` |
| `ntfs-totalsectors-huge.img` | boot sector claims 2⁶⁴ sectors | 255 | `mount … failed: Invalid argument` |
| `ntfs-mftcluster-huge.img` | $MFT cluster past volume | 255 | `tntfs error … parse_ntfs_boot_sector(): MFT LCN (281474976710655, 0xffffffffffff) is beyond end of volume. Weird.` |
| `ntfs-spc-huge.img` | sectors-per-cluster 255 | 255 | `mount … failed: Invalid argument` |
| `ntfs-mftrecsize-huge.img` | 127 clusters per MFT record | 255 | `mount … failed: Invalid argument` |
| `ntfs-mft-data-allocsize-huge.img` | $MFT DATA allocated size 2⁶⁴−1 | 255 | `tntfs error … ntfs_mapping_pairs_decompress(): Corrupt attribute. deltaxcn = 0x6, max_cluster = 0xfffffffffffffffe` |
| `ntfs-mft-runlen-huge.img` | attribute run length 255 clusters | 255 | `tntfs error … ntfs_mapping_pairs_decompress(): Invalid length in mapping pairs array.` |
| `ntfs-attrlen-huge.img` | attribute length field 65535 (walker runs off record) | 255 | `tntfs error … ntfs_attr_find_in_mft_record(): Inode is corrupt. Run ntfsck.` |
| `ntfs-truncated-body.img` | valid boot sector, body truncated to 300 sectors | 255 | `mount … failed: Invalid argument` |

\* Rows marked `0*` mounted successfully; the driver then rejected the *individual mutated file* during
`ls`/`md5sum` (EIO to userspace) while the volume itself stayed mounted — i.e. the fault, if any, would
have shown at read time, and none did.

---

## 4. Raw evidence

Every mount was clean or cleanly rejected. The interesting cases are the ones that reached the deep
parser, because those are the only ones that *could* have faulted:

**exFAT root-directory FAT cycle** (`exfat-root-fat-cycle.img`) — explicit cycle detection, then EIO:

```
[    7.024631] texfat error (device sda, pid 766): exfat_map_cluster_chain(): infinite chain
[    7.025482] texfat error (device sda, pid 766): exfat_map_cluster_chain(): Inode 0x10 has corrupt cluster chain.
mount: mounting /dev/sda on /tuxmnt failed: I/O error
```

**exFAT file cluster-chain cycle** (`exfat-file-fat-cycle.img`) — the same guard fires on the read path:

```
[    6.995422] texfat error (device sda, pid 779): exfat_map_cluster_chain(): infinite chain
[    6.996589] texfat error (device sda, pid 779): exfat_map_cluster_chain(): Inode 0x23180 has corrupt cluster chain.
[    6.996940] texfat error (device sda, pid 779): exfat_file_open(): Failed to map cluster chain for inode 0x23180 (error 5).
md5sum: can't open '/tuxmnt/BIG.BIN': I/O error
```

**exFAT oversized DataLength** (`exfat-file-datalen-huge.img`) — length sanity check at inode setup:

```
[    6.836240] texfat error (device sda, pid 776): exfat_setup_locked_inode(): Inode 0x230c0, LBO 0x230c0 has valid_data_length 0xc which exceeds the file_size 0xffffffffffffffff.  Inode is corrupt.
[    6.836658] texfat error (device sda, pid 776): exfat_lookup(): Failed to get inode (error 5).
```

**exFAT secondary-entry over-reads** (`exfat-secondarycount-huge.img`, `exfat-name-overread.img`):

```
[    6.832233] texfat error (device sda, pid 776): exfat_dir_entry_set_checksum(): Expected secondary, in-use directory entry but got entry of type 0x85.
[    6.832540] texfat error (device sda, pid 776): exfat_setup_locked_inode(): Failed to calculate checksum for inode 0x230c0, LBO 0x230c0.  Inode is corrupt.
…
[    6.791967] texfat error (device sda, pid 777): exfat_readdir(): File record has invalid number of secondary entries (must be at least 18 but have only 2) in directory inode 0x10.
```

**NTFS oversized MFT run list** (`ntfs-mft-data-allocsize-huge.img`, `ntfs-mft-runlen-huge.img`):

```
[    6.936662] tntfs error (device sda, pid 768): ntfs_mapping_pairs_decompress(): Corrupt attribute.  deltaxcn = 0x6, max_cluster = 0xfffffffffffffffe
[    6.937115] tntfs error (device sda, pid 768): ntfs_mapping_pairs_decompress(): Corrupt mapping pairs array in non-resident attribute.
[    6.937661] tntfs error (device sda, pid 768): ntfs_read_inode_mount(): ntfs_mapping_pairs_decompress() failed with error code -5.  $MFT is corrupt.
```

**NTFS oversized attribute length** (`ntfs-attrlen-huge.img`):

```
[    6.745454] tntfs error (device sda, pid 768): ntfs_attr_find_in_mft_record(): Inode is corrupt.  Run ntfsck.
```

### Attribution note

The vendor kernel floods every boot with unrelated `lge_gps_driver`/`gpio-ctl`/`sysfs` WARNING traces
(`gpiod_direction_output_raw: invalid GPIO`, `sysfs: cannot create duplicate filename
'/devices/platform/gpio-ctl/gpio_emmc_WDT_pin'`). These are platform-device warnings present in the clean
baselines too, are not oopses/panics, and name no filesystem driver; they are excluded. The clone also
inherited two pre-existing vkernel run logs (run IDs `1793786029…` and `1793786250…`, both
`init=/lib/systemd/esinit`) that contain a `NULL pointer dereference` — these predate this probe, carry no
`tuxfuzz-probe.json`, and are the vendor esinit chain failing in the projection, not the filesystem
drivers. They are excluded from this probe's results.

The complete per-run evidence lives in `work/vm/tuxfuzz/runs/<run-id>/serial.log` and
`work/vm/tuxfuzz/results.json`; the crafted images and their exact byte edits are in
`work/vm/tuxfuzz/images/manifest.json`.

---

## 5. Scope and honesty

This is a **weaker negative**, not a proof of absence. What was and was not covered:

- **Covered:** the two shipped closed-source drivers were loaded and mounted against 20 images spanning
  nine classes — truncated allocation tables, cyclic cluster chains (root and file), entry counts larger
  than the table, attribute/fragment run lengths exceeding the cluster/volume, root-directory and file
  clusters pointing past the volume, absurd sector/cluster sizes, an oversized MFT attribute list/run list,
  filename-length at the limit, and a valid header with a truncated body. All were parsed by the driver
  (the clean baselines prove the instrument works) and none faulted.
- **Not covered:** mutations were single-field edits, not a coverage-guided sweep; the driver was mounted
  read-only; write-path and truncate-path bugs, decompression paths, and deep directory-tree traversal were
  not exercised; and a corrupted image that happens to *still mount* and fault later in a specific syscall
  is the shape of bug this kind of one-edit sweep is least likely to find.

The one-paragraph verdict: **a crafted image did not drive `texfat` or `tntfs` into any fault state** — both
modules repeatedly detected and rejected the malformed structures through their own validation (explicit
`infinite chain` and bounds/`Inode is corrupt` checks) and returned EIO/EINVAL to the mount or the read,
with the kernel surviving all 23 boots.
