# V-059 evidence sheet — every measurement, with the command that produced it

One page so the finding can be re-derived without reading the changelog. Everything here was produced from
`work/decrypted-eu-260128/extracted-safe/mango-rootfs` (EU `NE_EUR.S5W_L.001.001.260128`) on this host. The upstream project that documented the technique is
`CloudPapi/ioniq5-usb-toctou`; its **dynamic-media demonstration has not been reproduced here**, and nothing was installed on any unit.

## The subject

```
app/bin/AppUpgrade
  size    10,787,256 bytes
  sha256  5295c6e4c41fb9c03760cf006c58b66fcd11aeb4e6e889af6e31b062549b6df0
```

It wraps two updaters, distinguished by the `##[scomo]` and `##[newota]` log tags: **764** SCOMO strings and **138** FUMO (`newota`). The vehicle's launcher row supplies `-un:0`, which
selects **FUMO** (`evidence/appupgrade-update-trust.md`).

## 1. The two updaters are ELF images inside the wrapper's data, not code in the wrapper

```
objdump -h app/bin/AppUpgrade
  .text    00003f73   (16,243 bytes)
  .rodata  00a3faa8   (10,746,536 bytes)
```

Two complete ELF binaries are embedded in `.rodata`, extractable with `tools/uk_fw/extract_embedded_elfs.py`:

| offset | bytes | identity | .text |
| --- | --- | --- | --- |
| `0x7c64` | 5,678,432 | SCOMO (764 `###[scomo]` lines) | 0x24cf83 |
| `0x5721c8` | 5,066,264 | FUMO / newota (138 `###[newota]` lines) | 0x1e5203 |

The two command strings that carry the mechanism are present and each names `%1`:

```
ionice -c3 md5sum %1                 present (2)
pv -q %1 | tar -xvm -C %2            present (1)
nice -n 19 dd if=%1 bs=4k skip=%2    present (4)
```

**Measured in FUMO's code** (the updater this vehicle selects), filtering the same scan to its `.text` range `0x24830..0x209a33`:

```
ionice -c3 md5sum %1     string 0x22c4e0   code sites: 0x13a550
tar xf %1 -C %2          string 0x20be5a   code sites: 0x633e0, 0x101d2f
tar -tvf %1              string 0x20b358   code sites: 0x5ea1c        <- a third read of the same file
pv -q                    string 0x210fc8   code sites: 0x70c75
```

Note that `pv -q %1 | tar -xvm -C %2` belongs to **SCOMO**. The two FUMO `tar xf` sites are a **copy/whatsnew helper** (`copyWhatsNewFiles`, `cp -a %1 %2`, `whatsnew_usb.json`), not the partition
install - an earlier note in this sheet said otherwise.

**FUMO's actual apply step:**

```
%1 -d %2 %3 0 | pv -q -L 8m | dd of=%4 bs=512      <- decrypt the payload, write it to a partition device
%1 -d %2 %3 0 | dd of=%4 bs=512
mount p3 original, p6 original, p5 mnt, p7 mnt
mkfs.ext4 -E nodiscard -j /dev/mmcblk0p16
```

A fresh invocation opens the payload again, separate from the `md5sum` site at `0x13a550`.

**Where that second open points: naming says mount, the code found so far says otherwise.** FUMO's own log string is `mountPath is /update/usb/bin CloseApp called !` and it carries a generic `mount %1 %2`, so
`/update/usb/bin` is a **mount point** - the path counts that looked like staging were pointing at the mounted USB volume. The caveat is that `mount %1 %2` is generic and could mount a local
loop image, so a runtime `lsof`/`inotify` is still the definitive check.

Earlier phrasing kept for the record: the path counts lean towards staging rather than the mount: `/update/usb` appears 7 times in FUMO against `/media/usb` 1 (SCOMO: 12 and 1).
`/update/usb` is on the local `/update` partition, so its presence is a staging hint - against the external report, which describes an in-place read. The stream is **rate-limited to 8 MB/s** by its own `pv -L 8m`, so 879 MB needs ~110 s and 2.09 GB
~260 s of apply, and a gadget never has to exceed 8 MB/s to saturate the stage.

**Withdrawn claim.** An earlier version said the check and the install were "constructed in different parts of the program, ~1.2 MB apart" on the strength of a displacement scan. Both sites it
found (`0x1877a8`, `0xbd744`) are in **`.rodata`** - data, not code. The scan cannot tell them apart, and on this binary nearly everything is data. Withdrawn; the separation is upstream's
`[RE]` finding against the embedded images, which are now extracted and analysable.

## 2. The signature step is MD5-with-RSA over the checked content

```
PKCS#1 sig. verify                  present
md5WithRSAEncryption                present
```

Consistent with the upstream reading: the genuine signed image satisfies the check, so an attacker needs **no RSA private key**.

## 3. The AES content key does not ship; the public key does

```
./tool/velix_aes.key                   (read at run time)
/update/fota/velix_aes.key             (the unit's copy)
VElix_GetAESKey KeySize : %d
getKeyFile() is fail.!!! (%d)
```

`velix_aes.key` is in **no shipped tarball** and nowhere in the rootfs. `app/share/AppUpgrade/teruten5_pub.key` **does** ship and is a 294-byte DER `SubjectPublicKeyInfo`,
2048-bit - a **public** key.

**Consequence:** arbitrary content needs the unit's key; a **genuine older package does not**, because it is already encrypted with the key the unit holds and the install pass accepts it.

## 4. Cache behaviour differs between the two updaters

```
[newota] tags containing drop_caches   0
[scomo]  tags containing drop_caches   2      (echo 1 > /proc/sys/vm/drop_caches, echo 3 > ...)
```

So on the **FUMO** path this vehicle uses, nothing explicitly evicts the checked file before the install re-reads it. That makes the technique depend on the payload not fitting in RAM - which
the payload sizes below settle.

## 5. Payload sizes, from this package

| payload | bytes | note |
| --- | --- | --- |
| `HU/images/mango-rootfs.tar.gz` | 879,109,759 | matches the upstream figure exactly |
| `HU/images/new_gui.tar.gz` | 2,091,925,601 | larger than any plausible head-unit RAM |
| `HU/images/update.tar.gz` | 42,101,042 | |
| `HU/images/mango-rwdata.tar.gz` | 16,721,058 | |

## 6. What is actually checksummed: the small binaries

`Checksum.txt` ships in two places only, both CRC32 lists of `.BIN` files:

```
update/micom/Checksum.txt      152 entries    HCR_PE.DV.260120.09.REVC.BIN  CRC32=0x31D8C50F
update/frontkey/Checksum.txt     2 entries    MKBD_2_1F_00_NX4.BIN          CRC32=0x0E969002
```

**Neither large payload appears in any checksum file**, and `appnavi.tar` carries none.

## 7. Which payload to target, therefore

- **`new_gui.tar.gz`, 2.09 GB** - too large to stay cached, and unchecksummed → **first choice**;
- **`mango-rootfs.tar.gz`, 879 MB** - unchecksummed but at the edge of what a unit may keep resident → second;
- **MICOM / frontkey `.BIN`** - CRC-verified; a swap of these fails.

## 8. What is not established

- No reproduction: the dynamic-media behaviour is the upstream project's, not measured here.
- The `NaviChecksumThread` in the binary parses a checksum file, but this package's navigation payload contains none - so its scope is open. It does not touch the interface or system payloads.
- **Which path the two reads open is unresolved here.** The binary shows a staging area (`/update/usb/bin`, `/update/usb/upgrade`), FUMO mount points (`/update/fota/mnt/rootfs`,
  `/update/fota/mnt/navi/system`), a manifest-only copy (`cp /update/usb/bin/.lge.upgrade.xml /tmp/`) and a family of `cp`/`mv`/`tar` commands on `%1`. A staged local copy would mean the
  race does not exist on this flow; a mount over the removable medium means it does. Upstream reports the latter and demonstrated it; this repository has strings that support either.
  **Settling it needs `lsof`/`inotify`/`strace` on a unit during a real update** - which path the `md5sum` opens, and which the `pv`/`dd` opens.

## 9. The fix this all points at

**Never verify a file and then re-open it.** Hash during the install over the handle that writes, or copy once into protected storage and verify *and* install from that copy. Plus a boot-time
rootfs integrity mechanism, so "installed unverified content" is not the same as "runs at next boot".
