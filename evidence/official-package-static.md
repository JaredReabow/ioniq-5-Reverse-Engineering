# Australian IONIQ 5 Gen5W: official package and read-only static analysis

- Task: T2 (research), requirements R1 and R2
- Dependency: T1 accepted, `evidence/identity-and-official-updates.md`
- Target: `2021-23 IONIQ 5`, Standard-class Gen5W, Australia
- Software: `NE_E.AUS.S5W_L.001.001.260319`
- Map: `AUS.19.41.47.011.611.0`
- Model string: `NEAE.S5BLN.AAU`
- Package root: `/Users/researcher/Downloads/NaU/2021_22_IONIQ_5_AU`
- Research date: 2026-10-19 (Australia/Sydney)
- Status: package obtained and statically inventoried. No firmware execution,
  filesystem mount, USB-media write, or vehicle interaction was performed.

## Bottom line

The official Navigation Updater acquired the Australian Gen5W package. The
package is a directory tree containing 36 files and 9,514,830,930 bytes:

| Property | Observation |
|---|---|
| Package files | 36 |
| Total bytes | 9,514,830,930 (8.861 GiB) |
| Payload records in `.ver` | 35 |
| Declared payload bytes | 9,514,828,145 |
| Manifest result | 35/35 file sizes and IEEE/zlib CRC-32 values match |
| Sorted-tree SHA-256 | `bc3013e5fc1499612cec76777aa736e0973a0b8a337c6619aace9af5a4d9652a` |
| Map MD5 | `6b0b80623b56581cae994b49c02660ce`, declared and observed |
| AU voice-resource MD5 | `8fa479c97e752b43c907c7838a7856ed`, declared and observed |
| EU voice-resource MD5 | `6303095ad812cef04e245a5d0aa9ac08`, declared and observed |
| Front-key checksums | both CRC-32/MPEG-2 values match |

The 36 files divide into five text descriptors, two front-key blobs, three
ordinary archives, six plaintext IPK boot/kernel containers, nineteen
high-entropy opaque envelopes, and one empty sentinel. The map is a valid PKZIP
archive. Both `mango-vr_fixed.tar.gz` files are valid gzip/tar streams. Most
other files ending in `.tar`, `.tar.gz`, or `.xml` are not plaintext containers
of that type.

This establishes the package identity, internal integrity relationships,
container boundaries, and several runtime strings. It does not establish an
encryption scheme for the opaque envelopes, a vendor signature chain over the
whole package, or behavior on the vehicle.

The complete per-file sizes, SHA-256 values, `file(1)` observations, entropy
samples, and terminal bytes are in
`evidence/package-metadata/official-package-inventory.txt`.

## Acquisition and updater flow

The official updater at `/Applications/Navigation Updater.app` reports:

| Property | Value |
|---|---|
| CFBundleIdentifier | `com.hyundai.update` |
| CFBundleShortVersionString | `261.015.0.215` |
| Main executable bytes | 67,950,208 |
| Main executable SHA-256 | `7b63734d60ca42648e81fcf12a9518c46077859554c050e2134dc27120e0f37c` |

The installed bundle still fails vendor signature verification on the current
host. That affects trust in the updater binary; it does not change the package
bytes or their internally verified manifest. The earlier installer repair and
signature evidence remain in `evidence/package-metadata/installer-identity.txt`.

The selected vehicle and destination were:

- Australia
- Hyundai
- `2021-23 IONIQ 5`
- `Standard-class Gen5W Navigation`
- Local destination `/Users/researcher/Downloads/NaU/2021_22_IONIQ_5_AU`

The updater's sanitized diagnostic log records the target and the software/map
identity:

```text
[D:4,T:07:28:48,NAME:2021-23 IONIQ 5]
[D:6,T:07:29:19,ST:HDD,VN:/Users/researcher/Downloads/NaU/2021_22_IONIQ_5_AU,SWV:,oldMapVer:]
[D:7,T:07:29:42,NAME:2021-23 IONIQ 5,mcode:1227,newSwVer:NE_E.AUS.S5W_L.001.001.260319,newMapVer:22389]
```

The updater UI displayed an update size of 9,062 MB. The completed tree is
9,514,830,930 bytes. These are retained as separate observations; this review
does not infer why the displayed requirement and final tree differ.

The updater binary contains the following flow identifiers and diagnostic
strings, observed with `strings`:

- `SCENE_UPDATE_SAVE_PATH`, `SCENE_UPDATE_DOWNLOAD`,
  `SCENE_UPDATE_DOWNLOAD_COMPLETE`
- `DownloadService::requestDownloadUnzipCheck`
- `CopyService`
- `[DOWNLOAD][FILE][MAP][VERSION][MATCH][CHECK]`
- `[DOWNLOAD][FILE][COPY][VER][SIZE][STATUS]`
- `USB_COPY` and `[AUTODOWNLOAD][CHECKFREESIZE]`

These show that the client has explicit download, version-check, unzip-check,
copy, and removable-media stages. They do not show that any vehicle-side action
was performed. No USB medium was inserted or written during this task.

## Exact version descriptor

`2021_22_IONIQ_5_AU.ver` is plain ASCII. Its first line is:

```text
+|22389|NE_E.AUS.S5W_L.001.001.260319|HM|2021_22_IONIQ_5_AU|1227|1
```

Observed relationships:

- `22389` matches `newMapVer:22389` in the updater log and is associated with
  the Australian map in this package. Its broader server-side meaning is not
  established.
- `NE_E.AUS.S5W_L.001.001.260319` matches the T1 software identity.
- `HM` is the Hyundai brand code.
- `2021_22_IONIQ_5_AU` is the package/catalog name, while the updater UI calls
  the vehicle `2021-23 IONIQ 5`.
- `1227` matches the updater's `mcode:1227`; the public version table also used
  `data-idx="1227"` for this vehicle row.
- The final `260319` suffix matches the kernel build date, 19 March 2026. It is
  inferred, not proven, that this suffix encodes the build date.

The remaining 35 lines describe payload files. Each has a numeric record ID, a
signed decimal CRC field, a byte size, and a flag. Reinterpreting the signed
field as an unsigned 32-bit value and computing IEEE/zlib CRC-32 gives an exact
match for all 35 records:

```text
entries=35 match=35 mismatch=0
declared payload bytes=9514828145
```

The `.ver` file itself is the 36th file and is not one of its own payload
records.

## Front-key checksum correction

`HU/firmware/frontkey/Checksum.txt` contains:

```text
MKBD_2_1F_00_NX4.BIN    CRC32=0x0E969002
MKBD_2_22_00_US4.BIN    CRC32=0xBCFCC65D
```

The lower-case on-disk names are otherwise identical. Both values are exact
when computed as CRC-32/MPEG-2: polynomial `0x04C11DB7`, initial value
`0xFFFFFFFF`, MSB-first, no final XOR.

| File | Declared | Observed CRC-32/MPEG-2 | Result |
|---|---|---|---|
| `MKBD_2_1f_00_NX4.bin` | `0x0E969002` | `0x0E969002` | match |
| `MKBD_2_22_00_US4.bin` | `0xBCFCC65D` | `0xBCFCC65D` | match |

A standard IEEE/zlib CRC-32 gives different values and would create a false
mismatch. The two front-key records are internally correct. Earlier wording
that treated this as a packaging defect was using the wrong CRC family and has
been removed.

## Plaintext containers

### Australian map

`HU/images/navi_au/S5W_MAP_ALL_AUS_19_41_47_011_611_0.zip` is a PKZIP archive:

| Property | Observation |
|---|---|
| File bytes | 2,176,363,209 |
| SHA-256 | `f5414e71d4e81a4b6cd85d1d41eda5edcc0833e0743e7b1a29178bc93d576c1c` |
| `unzip -l` | 374 entries (tool count) |
| Expanded bytes | 4,267,615,968 |
| `unzip -t -qq` | exit 0 |
| MD5 file | `6b0b80623b56581cae994b49c02660ce`, matches |

The listing includes `DATA/COMMON/FONT`, `DATA/NATION/AUS/MAP`, map data such as
`VIT_AUS.hafp` and `VIT_AUS_ADAS.hafaip`, JSON policy files, and license text.
This is a readable map container, not an opaque envelope.

### Voice resources

Both `mango-vr_fixed.tar.gz` files are genuine gzip streams containing tar
archives:

| Region | Compressed bytes | Uncompressed bytes | Gzip test | MD5 |
|---|---:|---:|---|---|
| AU | 570,557,204 | 652,823,552 | pass | `8fa479c97e752b43c907c7838a7856ed` |
| EU | 2,365,067,377 | 2,707,097,088 | pass | `6303095ad812cef04e245a5d0aa9ac08` |

`tar -tzf` begins with `vr_fixed/LPTE/BASE/` and lists ASR, TTS, language,
symbol, and voice-engine assets. The MD5 manifests include this build-path
fragment:

```text
__EVENT_BUILD_s5w.26ru1.251203_MASS_PRODUCT_26RU1_001_260312102711
```

The unsuffixed `vrau/mango-vr.tar.gz` and `vreu/mango-vr.tar.gz` files are
different: both are high-entropy data without gzip magic. The `_fixed` files
are the readable resources in this package.

### IPK boot and kernel containers

The six `*_sub` files are 6,210,308 bytes each and begin with `ipk.`:

```text
00000000: 6970 6b2e 0003 0300 0000 0000 ccbf 5e00  ipk...........^.
00000010: 3400 0000 ccbf 5e00 948d f042 b903 0000  4.....^....B....
00000020: e048 5100 0000 0000 360e 0000 f804 0000  .HQ.....6.......
00000030: 0060 0d00 726f 6f74 3d2f 6465 762f 6d6d  .`..root=/dev/mm
```

Observed header facts:

- Magic `ipk.` is at offset 0.
- Bytes `0x04-0x07` are `00 03 03 00`.
- The 32-bit field at `0x10` is `0x00000034`, where the command line begins.
- The value at `0x0c` and `0x14` is `0x005EBFCC`, exactly 824 bytes less than
  the 6,210,308-byte file size.
- Other fields are `0x00000E36` at `0x28`, `0x000004F8` at `0x2c`, and
  `0x000D6000` at `0x30`.

The field semantics beyond that are not established. The container is not
opaque: it exposes a boot command line, an x86 boot sector, and a Linux kernel.
The real-mode boot sector starts at `0x3F0`; `HdrS` appears at `0x5F2`, and the
x86 signature `55 AA` appears at `0x5FE`.

The kernel version/build string at offset `0x3710` is:

```text
4.1.27-abl (vc.integrator 7a0c10c@LGEAVSCI40) #1 SMP Thu Mar 19 16:22:46 KST 2026
```

The `x86_64` machine string is also present. These are static package facts, not
evidence that the image was booted.

### Runtime and hardware strings

The same plaintext IPK containers carry the boot command line:

```text
root=/dev/mmcblk0p3 rootfstype=ext4 rootwait init=/lib/systemd/esinit
console=ttyS2,115200n8
i915.nuclear_pageflip=1
i915.enable_1920_720_mode=1
i915.splash=HDMI-A-1:splash_1920x720.data:1920,720,1920,0,0,1920,720
lge.lcd_res=1920,720
lge.lcd_type=3
```

The observed configuration links the package to an x86-64 Linux system with:

- an eMMC block device (`/dev/mmcblk0p3`)
- ext4 root filesystem
- systemd and an `esinit` entry point
- Intel i915 graphics
- a 1920 x 720 panel mode
- Intel DRM and display configuration

The `i915` firmware names included in the kernel strings are
`bxt_dmc_ver1.bin`, `bxt_guc_ver8.bin`, and `bxt_huc_ver01_07_2013.bin`.
Static strings do not prove which firmware files are present or loaded at
runtime.

## Opaque envelopes

Nineteen files have near-8-bit entropy and no plaintext archive signature at the
offset implied by their names. They include:

- `.lge.upgrade.xml`
- `.whatsnew.tar.gz`
- `AppUpgrade`
- three modem packages
- `HU/firmware/update.tar.gz`
- the six non-`_sub` `iasImage` variants
- `mango-rootfs.tar.gz`
- `mango-rwdata.tar.gz`
- `appnavi.tar`
- `new_gui.tar.gz`
- the two unsuffixed `mango-vr.tar.gz` files

This does not rely on names alone: `.lge.upgrade.xml` has no readable XML tag or
declaration text, `.whatsnew.tar.gz` has no gzip magic, `appnavi.tar` has no tar
header at offset 257, and the files listed above sample at approximately
`7.9998` bits per byte at both ends.

Fixed terminal values suggest grouping, but their semantics are unknown:

| Last 16 bytes | Opaque members |
|---|---|
| `a875ca661c8a4e2a48896378cd019577` | five non-`_sub` `iasImage` variants and `mango-rootfs.tar.gz` |
| `dccba2068664487a45b0c6972e0360dc` | `.lge.upgrade.xml`, `AppUpgrade`, `update.tar.gz` |
| `cbcccc4da6837ea97dcec77608f62933` | `.whatsnew.tar.gz`, `modem_au_le22.tar.gz` |
| `6063d951c5de02505f9c1fa70edbe717` | `mango-rwdata.tar.gz`, `new_gui.tar.gz` |

Six other opaque files have unique terminal values: `iasImage`,
`modem_eu.tar.gz`, `modem_eu_le22.tar.gz`, `appnavi.tar`,
`vrau/mango-vr.tar.gz`, and `vreu/mango-vr.tar.gz`.

The six plaintext `_sub` IPK files also share the terminal bytes
`2af67733d70617bf9532419501000100`. That shows a shared trailer does not by
itself imply encryption: those six are readable kernel containers.

The repeated tags and high entropy are consistent with a proprietary encoded or
encrypted envelope. The observations do not establish the cipher, key,
authentication mode, compression state, or the trailer's role. No decryption
was attempted.

## Integrity and trust

Established here:

- all 35 `.ver` payload records match their file sizes and IEEE/zlib CRC-32
- the map and both voice resources match their declared MD5 values
- both front-key binaries match their CRC-32/MPEG-2 values
- the map ZIP and both fixed voice archives pass their format validators
- the package tree is stable enough to identify by a sorted SHA-256 digest

Not established here:

- whether the internal manifest is vendor-signed independently of the payload
- whether any opaque envelope carries a signature, MAC, key wrap, or IV
- whether the package is a full image or a delta relative to a prior head-unit
  build
- whether the installed updater's invalid vendor code signature affects package
  acquisition semantics or only local client trust
- whether an OTA or dealer package differs from this downloaded build

CRC and MD5 matches establish internal consistency. They do not establish
vendor authenticity against an independent trust anchor.

## Observed, inferred, unknown

Observed:

- The updater selected `2021-23 IONIQ 5`, Standard-class Gen5W, Australia, and
  downloaded a 36-file package.
- The `.ver` identity is `NE_E.AUS.S5W_L.001.001.260319`.
- All 35 manifest sizes and IEEE CRC-32 values match.
- The map and both fixed voice resources match their MD5 manifests.
- The map is a 374-entry PKZIP with 4,267,615,968 expanded bytes.
- Both fixed voice resources are valid gzip/tar streams.
- Six `*_sub` files are plaintext `ipk.` containers with an x86 Linux 4.1.27
  kernel and i915/eMMC/ext4/systemd strings.
- Nineteen files are high-entropy opaque envelopes with distinctive terminal
  bytes.

Inferred:

- `260319` in the software string likely denotes the 19 March 2026 build date,
  matching the kernel build timestamp.
- The non-`_sub` `iasImage` variants are likely related display assets or
  encoded images, based on name, size, and the plaintext `_sub` counterparts.
  Their actual format was not decoded.
- The nineteen envelopes likely use a vendor encoding or encryption layer. The
  exact mechanism is not known.
- The presence of map, navigation application, GUI, root filesystem, modem, and
  boot components suggests a complete component set, but delta status cannot be
  proven without a baseline.

Unknown:

- Envelope format, keys, nonce/IV handling, authentication method, and trailer
  semantics.
- Why the base `iasImage` and other non-`_sub` images are opaque while the
  paired `_sub` files are plaintext.
- Meaning of `0x005EBFCC` in the IPK header and the exact field table of that
  wrapper.
- Full package signing/attestation chain and server-side authorization model.
- Head-unit part number and hardware revision. The package exposes platform and
  runtime details, but not a verified board part number.
- Whether the downloaded package is accepted by the vehicle. No vehicle
  interaction was performed.

## Read-only reproduction

Set the package root:

```bash
PKG=/Users/researcher/Downloads/NaU/2021_22_IONIQ_5_AU
```

Inventory, sizes, and hashes:

```bash
find "$PKG" -type f | wc -l
find "$PKG" -type f -exec stat -f '%z' {} + | awk '{s+=$1} END{print s}'
LC_ALL=C find "$PKG" -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256
LC_ALL=C find "$PKG" -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 |
  sed "s#$PKG/##" | shasum -a 256
```

Validate all 35 `.ver` payload records with IEEE/zlib CRC-32:

```bash
ruby -rzlib -e '
root=ARGV[0]; base=File.basename(root); ok=bad=0
File.foreach(File.join(root,"2021_22_IONIQ_5_AU.ver")).drop(1).each do |line|
  d,n,id,crc,size,flag=line.strip.split("|")
  next unless size
  rel=d==base ? n : d.sub(/^#{Regexp.escape(base)}[\\\/]/,"").tr("\\","/")+"/"+n
  c=0; File.open(File.join(root,rel),"rb"){|f|
    while (b=f.read(1048576)); c=Zlib.crc32(b,c); end
  }
  good=(c==(crc.to_i & 0xffffffff) && File.size(File.join(root,rel))==size.to_i)
  good ? ok+=1 : bad+=1
end
puts "entries=#{ok+bad} match=#{ok} mismatch=#{bad}"' "$PKG"
```

Validate the front-key CRC-32/MPEG-2 values:

```bash
for f in "$PKG"/HU/firmware/frontkey/nx4/*.bin \
         "$PKG"/HU/firmware/frontkey/us4hev/*.bin; do
  perl -e '$c=0xffffffff; open F,"<:raw",$ARGV[0] or die;
    while(read(F,$b,1048576)){for(unpack("C*",$b)){
      $c^=$_<<24; for(1..8){$c=(($c&0x80000000)?(($c<<1)^0x04c11db7):($c<<1))&0xffffffff}}}
    printf "%s 0x%08X\n",$ARGV[0],$c&0xffffffff' "$f"
done
```

Validate and list the plaintext archives:

```bash
unzip -t -qq "$PKG/HU/images/navi_au/S5W_MAP_ALL_AUS_19_41_47_011_611_0.zip"
unzip -l "$PKG/HU/images/navi_au/S5W_MAP_ALL_AUS_19_41_47_011_611_0.zip" | tail -3
md5 -q "$PKG/HU/images/navi_au/S5W_MAP_ALL_AUS_19_41_47_011_611_0.zip"
gzip -t "$PKG/HU/images/vrau/mango-vr_fixed.tar.gz"
gzip -t "$PKG/HU/images/vreu/mango-vr_fixed.tar.gz"
tar -tzf "$PKG/HU/images/vrau/mango-vr_fixed.tar.gz" | head -30
```

Inspect the plaintext IPK boot container and trailer groups:

```bash
xxd -l 64 "$PKG/HU/images/iasImage_sub"
strings -a -n 8 "$PKG/HU/images/iasImage_sub" | head -120
grep -Eaob 'HdrS|4.1.27-abl|x86_64' "$PKG/HU/images/iasImage_sub" | head

find "$PKG" -type f -size +0 -print0 | while IFS= read -r -d '' file; do
  printf '%s  ' "$(tail -c 16 "$file" | xxd -p | tr -d '\n')"
  printf '%s\n' "$file"
done | sort
```

The entropy values in the inventory were sampled over the first and last 1 MiB
with Shannon entropy in bits per byte. All commands above are read-only.

## Handling and scope boundary

- The package tree and any future extracted tree stay outside Git.
- Only compact inventories, hashes, and observations belong in
  `evidence/package-metadata/`.
- No byte of the package was executed, mounted, decrypted, modified, or written
  to removable media.
- No vehicle was connected, entered, commanded, updated, or otherwise touched.
- Static analysis can describe interfaces and content; it cannot establish live
  head-unit behavior or vehicle acceptance.

## Remaining gaps

1. Determine the envelope scheme from a public format description or an
   independently observable decoder path, without destructive guessing.
2. Establish whether any package-level signature or attestation exists outside
   the opaque `.lge.upgrade.xml` envelope.
3. Compare this build with an independently obtained prior or dealer build to
   distinguish full payload from delta.
4. Reconcile the updater UI's 9,062 MB requirement with the final
   9,514,830,930-byte tree.
5. Establish the head-unit part number and hardware revision from physical or
   service documentation; the package alone does not identify a board part
   number.

## Sources

Public page and installer metadata:

- S1: `https://update.hyundai.com/AU/EN/updateNoticePopup/aiD0Sq`
- S2: `https://update.hyundai.com/AU/EN/updateNoticeList`
- S3: `https://update.hyundai.com/AU/EN/updateNoticeView/yNDC3y`
- S17: `https://update.hyundai.com/AU/EN/navigationUpdate`
- S18:
  `https://oem-setup.map-care.com/update_program_download/nau_client/crossplatform/install/NavigationUpdaterInstaller.zip`
- S20: `https://update.hyundai.com/AU/EN/updateGuide/00`
- S21: `https://update.hyundai.com/AU/EN/updateGuide/03`
- S22: `https://update.hyundai.com/AU/EN/updateGuide/04`

Local, outside Git:

- Package root: `/Users/researcher/Downloads/NaU/2021_22_IONIQ_5_AU`
- Updater bundle: `/Applications/Navigation Updater.app`
- Sanitized updater diagnostic evidence:
  `/Users/researcher/Library/Application Support/Navigation Updater/error_log1.log`

The exact per-file inventory is
`evidence/package-metadata/official-package-inventory.txt`; the public-page and
installer inventory is
`evidence/package-metadata/official-metadata-inventory.txt`.
