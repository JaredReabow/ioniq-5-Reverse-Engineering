# 2022 Kia Cerato AU — Linux Head Unit Firmware Analysis

**Target:** `BD_PE.AUS.S5W_L.001.001.260319` (build 2026-03-19)  
**Platform:** LGE Gen5W IVI (HKMC Premium AVN 2.1)  
**Analyst notes:** Full static analysis of the Linux-side firmware. The Android side (handled by the gen5w/navi\_extended community) is out of scope.

---

## 1. Firmware Package Structure

```
2022_Cerato_AU/
├── .lge.upgrade.xml          ← encrypted XML manifest (xcrypt TE2)
├── .whatsnew.tar.gz           ← encrypted
├── 2022_Cerato_AU.ver         ← plaintext version/checksum list
├── AppUpgrade                 ← encrypted (OpenPGP signature envelope)
└── HU/
    ├── firmware/
    │   ├── update.tar.gz      ← encrypted: peripheral updater package
    │   ├── modem/             ← modem firmware (au_le22, eu_le22, eu)
    │   └── frontkey/          ← front panel key MCU firmware
    └── images/
        ├── mango-rootfs.tar.gz   ← encrypted: MAIN LINUX ROOT FILESYSTEM (879 MB)
        ├── mango-rwdata.tar.gz   ← encrypted: writable data partition image
        ├── new_gui.tar.gz        ← encrypted: GUI assets (~2 GB)
        ├── iasImage*             ← encrypted: Intel Automotive Splash images
        ├── vrau/, vreu/          ← voice recognition data (AU/EU)
        └── navi_au/              ← navigation data + maps
```

### 1.1 Encryption Scheme (Fully Broken)

All `.tar.gz` and asset blobs use **AES-128-CBC** with:

| Parameter | Value |
|-----------|-------|
| **Key** | `60a93d70f73302a63e5ed0d0ea38be22` (hardcoded, shared across all LGE HKMC units) |
| **IV** | `SHA256(basename + int32_signed(payload_size))[:32]` (per-file, deterministic) |
| **Metadata** | 0x4024-byte `TE2` footer appended to each file |
| **Integrity** | `SHA256(IV \|\| metadata[36:])` stored at metadata[4:36] |
| **Padding** | Last incomplete 16-byte block padded with bytes from metadata[36:52] |

The encryption is **fully reversible**: decrypt with the above parameters, re-encrypt by reversing the process. The `xcrypt.py` tool from [hkmcavn-tools](https://github.com/galaxy4public/hkmcavn-tools/tree/main/xcrypt) handles both directions. A faster single-pass implementation decrypts the 879 MB rootfs in ~7 seconds (vs. ~30 min for the original script's per-block Python loop).

### 1.2 Upgrade Manifest

The decrypted `.lge.upgrade.xml` contains:

```xml
<upgrade-mode>developer</upgrade-mode>
<version>5W.XXX.S5W_L.001.001.260319</version>
<car-variant>aehev_aephev_dehev_dephev_aeev_dn8_osev_sp2_deev_mq4_pdpe_ybpe_cn7_..._bdpe_...</car-variant>
<partition>newpartition3rd</partition>
<newfirmware>newfirmwarestructure</newfirmware>
```

The `developer` upgrade mode and multi-variant car support are notable — this is a mass-production firmware that covers dozens of HKMC vehicle models.

---

## 2. System Identity

| Component | Version / Detail |
|-----------|-----------------|
| **OS** | OpenEmbedded 1.0 "mango" |
| **Build timestamp** | 20260319071321 |
| **Kernel** | 4.1.27-abl (x86-64) |
| **SoC** | Intel Apollo Lake (stepping A0/B0/B1/D0 detected at boot) |
| **Init** | systemd 225 (+SMACK +SYSVINIT +UTMP +ACL +XZ +BLKID +KMOD) |
| **Compositor** | Weston 1.10.0 (Wayland) |
| **Network manager** | ConnMan 1.29 |
| **Media framework** | GStreamer 1.8.3 |
| **Media scanner** | lightmediascanner 0.5.1 |
| **SSH server** | Dropbear (socket-activated, per-connection) |
| **Bluetooth** | `vbtd` — custom HKMC daemon (not BlueZ), serial on `/dev/ttyS0` |
| **BusyBox** | 584 KB, provides shell utilities (not init) |
| **GUI toolkit** | Qt 5.x (QML/Wayland) with IVI shell integration |
| **Crypto** | mbedTLS (embedded in AppUpgrade), `/dev/keystore` hardware keystore |
| **MAC** | SMACK (Simplified Mandatory Access Control Kernel) |

### 2.1 Filesystem Layout

```
/               ← read-only ext4 rootfs (mango-rootfs.tar.gz)
/app/           ← LGE application binaries and libraries
  bin/          ← AppUpgrade, AppMediaPlayer, MediaBrowser, vbtd, usb-automount, ...
  lib/          ← Qt libs, lightmediascanner, GStreamer plugins, ...
  share/        ← QML files, splash screens, images
  data/         ← per-app persistent data
/rw_data/       ← writable ext4 partition (mango-rwdata.tar.gz)
  home/root/    ← root home directory
  var/          ← system variable data
  usr_data/     ← user media storage
/media/usb*/    ← USB automount points
/navi/          ← SD card mount (navigation)
/update/        ← firmware update staging area
/log_data/      ← diagnostic logs
```

---

## 3. Boot Sequence

The system boots through this chain:

```
ABL (bootloader) → kernel 4.1.27 → /lib/systemd/esinit (bash script) → /lib/systemd/systemd
```

### 3.1 esinit — The Critical Boot Script

`/lib/systemd/esinit` runs before systemd and performs all early hardware detection and security configuration. Key operations in order:

1. Mount `/proc`, `/sys`, `/run`, `/tmp`
2. Wait for micom SPI validation (up to 3 seconds)
3. Read car type, OEM type, LCD type, country code from `/sys/module/micom/parameters/*`
4. Link shadow password file: `ln -s /etc/shadow.Global /tmp/shadow`
5. Start Weston compositor
6. Start early camera
7. Configure zram swap (1228 MB)
8. **Security gate:** Check `secure_console` micom parameter
9. Configure passwd file (legacy vs. secure)
10. Start serial console (if unsecured)
11. Configure iptables firewall mode
12. Handle Full Disk Encryption (FDE/LUKS) if enabled
13. Run filesystem check on writable partitions
14. Load kernel crash dump (kexec)
15. `exec /lib/systemd/systemd`

### 3.2 The secure_console Gate

This is the most security-critical logic in esinit:

```bash
# DEFAULT: SSH and console are ENABLED
touch /tmp/secure_console_disable

# Only disabled if micom says so
if [ -f /sys/module/micom/parameters/secure_console ]; then
    secure_console_mode="$(cat /sys/module/micom/parameters/secure_console)"
    if [ "$secure_console_mode" = "1" ]; then
        /bin/rm /tmp/secure_console_disable    # lock it down
        /bin/rm /dev/ttyS2                      # remove serial device
    fi
fi
```

The **default state is insecure** — the file `/tmp/secure_console_disable` is created, and only removed if the micom MCU explicitly reports `secure_console=1`. When the file exists:

- Root shell is `/bin/sh` (from `passwd.legacy`)
- Dropbear SSH starts (`ConditionPathExists=/tmp/secure_console_disable`)
- Serial `agetty` runs on `ttyS2` at 115200 baud
- Firewall may run in debug mode

When the file is absent (secure mode):
- Root shell is `/usr/sbin/nologin` (from `passwd.secure`)
- Dropbear does not start
- No serial console

---

## 4. Credentials

### 4.1 Root Password

`/etc/shadow.Global` (symlinked to `/tmp/shadow` at boot):

```
root:$6$I6C6apC0ue$J1MSIq2VqvBFdJhPwZZBfSD5qkZxUBhkemElmQd6CYDQ0bRo5PDcKBKJF7EqL6zuFlYCCY3X1kGIcUe3W0Rm60:20531:0:99999:7:::
```

This is a SHA-512 crypt hash with salt `I6C6apC0ue`. It is shared across all units using this firmware build.

### 4.2 Hardcoded SSH Authorized Key

`/etc/dropbear/authorized_keys`:

```
ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEA1r6oDEO80xc8f2jtf9SCGXVkzolaBcVWFle
vBKfBjwlqXaokV1+I8la+xSMCvu5UqyNWRyaY8ypyXtUe/PIq9YNLvC+2M+fNrGfZYR3KAf
1IGHDXlFMnCtvuzH4M7HvEV2YsuJReJqsCTyV2jVRpVcmz+RJqkl6gouWwQX4LJYjs3pRfHD
T4BrIUyyZ0YE273EZE0tQvZC4eO9nCEbhi869CNnD0k3rIE8Fesa4kMtgEktbH3WspV18pv7
zAqOPkA8jq10HCGPSG8Jc4A/+MNrBiYc64Ud5Oc1dkntp5zbA/PduK0/HViexTr6T/sIqrqj
Uw0sSXGySeTeM3R0yRfQ== rsa-key-20181102
```

This is an LGE development RSA key from November 2018, baked into the rootfs. The `dropbear_publickey_installer.sh` copies it to `/home/root/.ssh/authorized_keys` on every boot. Anyone with the corresponding private key has passwordless root SSH access to every unit.

### 4.3 Dropbear Configuration

```ini
# /etc/default/dropbear
# Disallow root logins by default
# DROPBEAR_EXTRA_ARGS="-w"     ← COMMENTED OUT — root login IS allowed
```

The `-w` flag (disable root login) is commented out. Combined with the authorized key, this means root SSH login is explicitly permitted.

---

## 5. Running Services

### 5.1 System Services (multi-user.target)

| Service | Binary | Description |
|---------|--------|-------------|
| `ApplicationLauncher.service` | `/app/bin/AppLauncher.sh` | Main app launcher (Qt/Wayland) |
| `AudioManager.service` | Audio routing manager |
| `CryptoService.service` | `/app/bin/CryptoService` | Key management via `/dev/keystore` |
| `MediaBrowser.service` | `/app/bin/MediaBrowser` | GENIVI media browser (SQLite index) |
| `usb-automount.service` | `/app/bin/usb-automount` | USB device auto-mounting |
| `vbtd.service` | `/app/bin/vbtd` | Bluetooth daemon |
| `connman.service` | `/usr/sbin/connmand` | Network manager |
| `credman.service` | Credential manager |
| `pas-daemon.service` | Persistence admin service |
| `iptables-manager.service` | `/etc/init.d/iptables-manager.sh` | Firewall |
| `carplay_iAP2.service` | CarPlay/iAP2 connectivity |
| `carplay_mdnsd.service` | mDNS for CarPlay |
| `dlt.service` / `dlt-system.service` | GENIVI DLT diagnostic logging |
| `dropbear@.service` | `/usr/sbin/dropbear` | SSH (conditional on secure_console) |

### 5.2 udev Rules

| Rule file | Trigger | Action |
|-----------|---------|--------|
| `80-hyundai.rules` | PCI touch input | Creates `/dev/input/touch` symlink |
| `98-QHSUSB__BULK.rules` | USB device with product="QHSUSB__BULK" | Runs `/usr/bin/naddump.sh` |

The QHSUSB rule is for Qualcomm modem diagnostic USB mode — it auto-runs a shell script when a specific USB device is detected.

---

## 6. USB Attack Surface

### 6.1 USB Automount Flow

```
USB inserted
  → kernel detects block device
  → udev notifies usb-automount
  → usb-automount reads /etc/usb-automount.conf
  → mounts to /media/usb* (supports: vfat, ntfs, ext4, exfat)
  → sends D-Bus signal: com.lge.car.automount / UsbMount
  → MediaBrowser receives signal, triggers lightmediascanner
  → lightmediascanner scans files with plugins
  → GStreamer 1.8.3 generates thumbnails
  → AppUpgrade checks for update packages
```

**Key facts about usb-automount:**
- Runs as **root** (systemd service, no user sandboxing)
- Mounts with read-write enabled (`rw_mode=enable`, `fat_rw_mode=enable`)
- Supports external USB hubs (`ext_hub=enable`)
- Uses `popen()` and `system()` calls (visible in strings)
- Accepts devices without UUID (`support_no_uuid=enable`)
- Has a "Special Command" mode (`Special Command is enabled!` string)

### 6.2 Media Parsing Pipeline

**lightmediascanner 0.5.1** plugins (all run as root):

| Plugin | File types | Notes |
|--------|-----------|-------|
| `id3.so` | MP3 (ID3v1/v2 tags) | Parses arbitrary tag frames |
| `mp4.so` | MP4/M4A/MOV | Parses atom/box structure |
| `asf.so` | WMA/WMV/ASF | Microsoft container format |
| `aiff.so` | AIFF audio | Apple audio format |
| `matroska.so` | MKV/WebM | Complex container with many sub-parsers |
| `m3u.so` | M3U playlists | Text-based, may contain paths |
| `pls.so` | PLS playlists | INI-style playlist format |

**GStreamer 1.8.3** handles actual media decoding and thumbnail extraction via `/app/bin/thumbnail_extractor.sh`:

```bash
#!/bin/sh
export LD_LIBRARY_PATH=/usr/lib/media-libva/:/app/lib
/app/bin/thumbnail_extractor
```

### 6.3 USB Firmware Update Path

When `AppUpgrade` detects a USB stick via D-Bus `usbMounted` signal:

1. Scans the mount point for update package structure (`.ver` file, directory layout)
2. Reads the `.ver` file (plaintext checksums and file list)
3. Validates RSA signatures using embedded mbedTLS (the `VElix` library)
4. If valid, copies update to `/update/` staging area
5. Triggers the appropriate `*_fw_updater` binaries from `update/sbin/`

The update validation chain:
```
.ver file (CRC32 checksums) → RSA signature check (mbedTLS + VElix_GetPubKey) → xcrypt decryption → tar extraction → flashing
```

---

## 7. Bluetooth Attack Surface

### 7.1 vbtd — HKMC Bluetooth Daemon

```ini
ExecStart=/app/bin/vbtd -d /dev/ttyS0 -p /tmp/bt_patchram.hcd
```

- **Custom proprietary stack** — not standard BlueZ
- Communicates with BT chip via serial UART (`/dev/ttyS0`)
- Firmware patchram loaded from `.hcd` file at startup
- D-Bus interface for HMI control (`BluetoothHMI` binary)
- Runs as root under systemd with auto-restart

The BT patchram file is selected per car type by `/etc/setup_bt_patchram.sh`.

---

## 8. Network Configuration

### 8.1 ConnMan

```bash
connmand -n --nodnsproxy --nobacktrace \
  --nodevice=rmnet_usb1,...,can0,eth1,eth2,ncmF0,usb1,eth0,...
```

The `--nodevice` list excludes modem, CAN bus, and several Ethernet interfaces — but notably some interfaces are not excluded and may be reachable.

### 8.2 Firewall (iptables)

The iptables-manager loads rules from `/etc/default/iptables/*.conf` in sorted order. A debug mode exists controlled by the micom `iptable_debug` parameter — when enabled, rules may be more permissive.

---

## 9. Software Version Inventory (Known CVE Exposure)

| Component | Version | EOL / CVE Status |
|-----------|---------|-----------------|
| Linux kernel | 4.1.27 | EOL 2018. Hundreds of known CVEs |
| systemd | 225 | 2015-era. Multiple privilege escalation CVEs |
| GStreamer | 1.8.3 | Multiple buffer overflow CVEs in demuxers |
| Weston | 1.10.0 | 2015-era. Known vulnerabilities |
| ConnMan | 1.29 | Known remote code execution CVEs (CVE-2021-26675, CVE-2021-26676, etc.) |
| glibc | (2.6.32 target) | Ancient. Extensive CVE history |
| Dropbear | (unknown exact ver) | Depends on version; likely has known issues |
| Qt | 5.x | Depends on exact version |

---

## 10. Engineer Mode PINs (Extracted via Reverse Engineering)

### 10.1 Discovery

The `AppEngineerMode` binary (`/app/bin/AppEngineerMode`, 11 MB, stripped PIE x86-64 Qt5 QML app) contains a `checkPassWord` function that validates PINs by comparing their **SHA-256 hash** against two hardcoded hex digests. The function was located by tracing the Qt Meta-Object Compiler (MOC) dispatch tables:

```
QML checkPassWord(code)
  → qt_static_metacall (0x8e76e0) → jump table entry 85 → dispatch stub (0x8e7cfb)
  → sub_746ba0 (wrapper) → sub_746850 (core hash comparison)
```

The core logic at `sub_746850`:
1. Converts input PIN string to UTF-8
2. Computes `QCryptographicHash::hash(pin_bytes, QCryptographicHash::Sha256)` (algorithm enum = 4, confirmed at instruction 0x7468f7: `mov edx, 0x4`)
3. Converts hash to hex string
4. Compares against hardcoded hash for the selected mode

**No salt is used** — the PIN bytes are hashed directly.

### 10.2 Hardcoded Hashes and Cracked PINs

| Mode | Hash (SHA-256) | PIN |
|------|---------------|-----|
| **Dealer** (returns "11") | `8350242b2df439d296a664c7c59b117507d0b3c537fa293304c84d84eb85cc43` | **2400** |
| **Engineer** (returns "21") | `0d04d1de80bce9c632b0cfb197026958809e4c3f42c3543d35b0d56976124280` | **19491003** |

### 10.3 How to Enter

On the head unit:
1. Navigate to the hidden Engineer Mode menu (hold Setup button for 5+ seconds, or access via diagnostic shortcut)
2. The PIN keypad appears (`AppEngineerMode_PinCodeKeypad.qml`)
3. For **Dealer mode**: enter `2400` (4-digit PIN)
4. For **Engineer mode**: enter `19491003` (8-digit PIN)
5. After 5 wrong attempts, the keypad locks out (writes `/tmp/eng_limit_check.txt`)

### 10.4 What Engineer Mode Provides

Engineer mode (PIN `19491003`) gives access to low-level diagnostics and configuration including:
- Network settings (IP configuration via `IPInfo.handleSetIPMakeShell` — potential command injection vector)
- System version information
- Hardware diagnostics
- Logging controls
- Potentially: firmware update bypass, debug shell access

---

## 11. File Inventory for Further Analysis

Binaries most worth deeper reverse engineering (all x86-64 ELF, stripped):

| Binary | Size | Purpose |
|--------|------|---------|
| `/app/bin/AppUpgrade` | 10.8 MB | Firmware update validation and application |
| `/app/bin/usb-automount` | 43 KB | USB device mounting — uses `popen()`/`system()` |
| `/app/bin/MediaBrowser` | large | Media indexing, SQL queries on USB file paths |
| `/app/bin/vbtd` | — | Bluetooth daemon |
| `/app/bin/CryptoService` | 244 KB | Key management via `/dev/keystore` |
| `/app/bin/AppEngineerMode` | — | Engineering/diagnostic mode |
| `/app/lib/liblightmediascanner.so.0.5.1` | 300 KB | Media file metadata parser |
| `/app/lib/lightmediascanner/plugins/*.so` | various | Per-format parsing plugins |

---

## 11. Decryption Tooling

### Fast decrypt script

A vectorized one-shot Python decryption script was created at:
```
scratchpad/tools/fast_decrypt.py
```

Usage:
```bash
python3 fast_decrypt.py <encrypted_file> <output_file>
```

Decrypts the 879 MB rootfs in ~7 seconds (vs. ~30 minutes with the original xcrypt.py per-block loop).

### Extracted filesystem locations

```
scratchpad/decrypted/              ← all decrypted blobs
scratchpad/extracted/rootfs/       ← full Linux root filesystem
scratchpad/extracted/update/       ← peripheral update package
scratchpad/extracted/rwdata/       ← writable data partition
```

---

## Appendix A: Key File Paths in the Rootfs

```
/lib/systemd/esinit                    ← boot script (security gate)
/etc/shadow.Global                     ← root password hash
/etc/passwd.legacy                     ← insecure passwd (root has /bin/sh)
/etc/passwd.secure                     ← secure passwd (root has /usr/sbin/nologin)
/etc/dropbear/authorized_keys          ← hardcoded LGE SSH public key
/etc/dropbear/dropbear_publickey_installer.sh
/etc/usb-automount.conf                ← USB mount configuration
/etc/init.d/iptables-manager.sh        ← firewall loader
/etc/fde_test_v2.sh                    ← Full Disk Encryption script
/etc/fsck_rw_partitions_v2.sh          ← filesystem recovery
/lib/systemd/system/usb-automount.service
/lib/systemd/system/MediaBrowser.service
/lib/systemd/system/vbtd.service
/lib/systemd/system/dropbear@.service
/lib/systemd/system/ApplicationLauncher.service
/lib/systemd/system/CryptoService.service
/app/bin/AppUpgrade                    ← update validator (10.8 MB, contains mbedTLS)
/app/bin/usb-automount                 ← USB mounter (popen/system calls)
/app/bin/MediaBrowser                  ← media indexer
/app/bin/vbtd                          ← Bluetooth daemon
/app/bin/AppEngineerMode               ← engineering menu
/app/lib/lightmediascanner/plugins/    ← media parser plugins
```
