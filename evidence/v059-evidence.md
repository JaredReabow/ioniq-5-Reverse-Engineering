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

## 1. Two separate reads of the same file

Both command strings are present, and a displacement scan of the binary resolves each to exactly **one** reference site:

| string | file offset | reference site |
| --- | --- | --- |
| `ionice -c3 md5sum %1` (the check) | `0x2abb44` | **`0x1877a8`** |
| `pv -q %1 \| tar -xvm -C %2` (the install) | `0x28c285` | **`0xbd744`** |

**~1.2 MB apart in a 10.8 MB binary.** The integrity decision and the install are constructed in different parts of the program, and each names `%1`, so the file is opened twice with the
decision made in between. Method: for every 32-bit RIP-relative displacement in the file, keep those that resolve exactly to the string's offset. No instruction decoding, so the limit is
stated: a coincidental displacement to a specific offset would be needed for a false positive, and one site each is what a real compiled reference looks like.

```
python3.13 - <<'EOF'
import struct; from pathlib import Path
d=Path('.../app/bin/AppUpgrade').read_bytes()
t=d.find(b'ionice -c3 md5sum %1')
print([hex(p) for p in range(len(d)-4) if p+4+struct.unpack_from('<i',d,p)[0]==t])
EOF
```

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
