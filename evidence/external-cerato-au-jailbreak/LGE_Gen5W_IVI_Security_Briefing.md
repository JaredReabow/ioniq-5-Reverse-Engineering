# LGE Gen5W IVI Head Unit — Security Research Briefing

You are assisting with authorized security research on a personally-owned 2022 Kia Cerato (AU market) in-vehicle infotainment (IVI) head unit. The goal is to identify zero-day vulnerabilities or exploitable existing vulnerabilities that can be triggered with the physical access constraints described below. This is the researcher's own vehicle.

---

## System Overview

### Hardware
- **Platform**: LGE Gen5W IVI (marketed as HKMC Premium AVN 2.1)
- **SoC**: Intel Apollo Lake x86-64
- **Display**: Touchscreen, driven by Weston compositor (IVI Shell) with fbdev backend
- **Connectivity**: Bluetooth, USB-A port (single), AM/FM antenna, GPS
- **No WiFi. No USB-C. No Ethernet. No cellular data modem exposed to the IVI OS.**

### Software
- **OS**: OpenEmbedded 1.0 "mango"
- **Kernel**: Linux 4.1.27-abl (x86_64)
- **Libc**: glibc 2.25
- **Init**: systemd 225
- **Firmware version**: BD_PE.AUS.S5W_L.001.001.260319 (March 2026 build — latest available)
- **Display server**: Weston compositor with IVI Shell extension
- **Audio**: PulseAudio
- **IPC**: D-Bus (system bus), extensive use throughout all LGE services
- **Package format**: No package manager. Read-only rootfs (ext4, remountable rw as root). All software is baked into the firmware image.

### Key Services & Binaries
| Binary | Role | Notes |
|---|---|---|
| `AppDMClient` | Firmware update detection daemon | Monitors USB for `.lge.upgrade.xml`, triggers AppUpgrade. ~2.2MB ELF. |
| `AppUpgrade` | Firmware update executor | Parses XML, mounts/extracts images. ~10.8MB ELF. Contains `system()` calls with format strings. Uses Qt for XML parsing (QDomDocument). |
| `usb-automount` | USB mount handler | Detects USB insert via udev/D-Bus, mounts at `/media/usb`. Calls `system()` for mount operations. Supports FAT32, exFAT, NTFS. |
| `LMS` (lightmediascanner) | Media file scanner | Auto-scans USB media files as root. Parses ID3, FLAC, MP4, OGG, etc. Uses plugin `.so` libraries (id3.so, mp4.so, flac.so, ogg.so, etc.) |
| `AppMode` / `AppModeIF` | Application mode manager | Manages IVI application states |
| `AppNavi` | Navigation application | Large Qt application |
| `AppMedia` | Media player | Handles audio/video playback from USB |
| `AppPhone` | Bluetooth phone interface | Handles BT HFP/A2DP |
| `micom-ipc` | Microcontroller IPC | Communicates with vehicle CAN gateway MCU |
| `connman` | Network manager | Manages Bluetooth PAN/networking |
| `bluetoothd` (BlueZ) | Bluetooth stack | BlueZ 5.x, handles pairing, profiles |
| `pulseaudio` | Audio server | Runs as root |
| `weston` | Display compositor | IVI Shell, runs as root |

### D-Bus Services (partial list)
- `com.lge.hkmc.avn.appfunc` — Application function interface (OSD notifications, system popups)
- `com.lge.hkmc.avn.upgrade.fota` — Firmware upgrade service at `/fotaInterface`
- `com.lge.hkmc.avn.mode` — Application mode management
- `com.lge.hkmc.avn.media` — Media service
- `com.lge.hkmc.avn.navi` — Navigation service
- Various ConnMan, BlueZ, PulseAudio, systemd D-Bus interfaces

### Filesystem Layout
```
/ (ext4, mounted ro by default, remountable rw)
/media/usb/ — USB automount point
/update/usb/ — Firmware update staging directory
/update/usb/bin/ — Update binary staging
/lib/systemd/system/ — Systemd unit files
/usr/lib/ — Shared libraries
/usr/bin/ — System binaries
/dev/fb0 — Framebuffer device
/run/user/root/ — XDG runtime (Wayland socket)
```

### Security Posture
- **Everything runs as root.** There is no user separation, no unprivileged services.
- **No MAC/SELinux/AppArmor.** No mandatory access control enforcement.
- **No ASLR confirmation** — kernel 4.1.27 era, likely minimal ASLR.
- **Read-only rootfs** — but trivially remountable: `mount -o remount,rw /`
- **No compiler, no Python, no package manager** on the device. Only BusyBox utilities.
- **Firmware images are AES-128-CBC encrypted** with key `60a93d70f73302a63e5ed0d0ea38be22`
- **Firmware signature verification exists** but has known bypass (CVE-2023-26246 — hash check failure falls through to normal upgrade path: "No Hash error with AppUpgrade and XML => Will Go to Normal USB Upgrade !!!")

---

## Physical Access Constraints

This is critical context. The researcher has:

### Available
- **Physical access** to the vehicle and head unit
- **USB-A port** — can insert any USB drive (FAT32/exFAT/NTFS)
- **Bluetooth** — can pair phones/devices to the head unit
- **Touchscreen** — can interact with the head unit UI
- **Engineer mode access** — accessed via Settings → About → tap version 10x → Dealer PIN `2400`, Engineer PIN `19491003` (AU variant also `19190301`). Provides diagnostic info, log viewing, some settings. **There is NO firmware update option and NO shell access in engineer mode.**
- **Firmware dump** — full firmware package extracted and available for static analysis (all binaries, rootfs, configs)
- **Cross-compiler** — can build static x86-64 Linux ELF binaries (musl-gcc) to deploy via USB

### NOT Available
- **No serial console** on the actual car (would require physical board access/soldering)
- **No SSH/telnet/network shell** — no WiFi, no ethernet, no exposed network interface
- **No ADB or debug bridge**
- **No JTAG/SWD** without hardware modification
- **No way to run arbitrary commands** unless code execution is first achieved through an exploit

This means: **any exploit must be triggerable purely through USB insertion, Bluetooth interaction, or touchscreen/UI interaction.** There is no way to "just run a script" without first achieving code execution through a vulnerability.

---

## Known Attack Surface

### 1. USB Firmware Update Chain (Most Promising)
**Flow**: USB insert → `usb-automount` mounts at `/media/usb` → D-Bus `UsbMount` signal → `AppDMClient` checks for `.lge.upgrade.xml` → copies to `/update/usb/` → launches `AppUpgrade`

**Known vulnerability**: CVE-2023-26246 — firmware digital signature bypass. Hash verification failure in AppDMClient falls through to normal upgrade path instead of aborting.

**Command injection in AppUpgrade**: The binary contains `system("sudo mount -o loop -t ext4 %s %s")` where the first `%s` comes from the `<SrcFullPath>` XML element parsed from `.lge.upgrade.xml`. The XML is parsed with Qt's QDomDocument. The function `mfGetUpdateSrcPath()` reads this element.

**Open questions**:
- Does AppDMClient validate the XML is encrypted before passing it on? The original USB had AES-128-CBC encrypted XML.
- Does a path prefix get prepended to SrcFullPath before the system() call?
- Are shell metacharacters (`;`, `#`, spaces, backticks) sanitized anywhere in the path?
- What is the exact nesting level expected for `<SrcFullPath>` in the XML DOM?
- Are there other `system()` or `popen()` calls in AppUpgrade with attacker-controllable input?

### 2. USB Media File Parsing (LMS — Light Media Scanner)
LMS auto-scans all media files on inserted USB drives as root. It uses plugin shared libraries:
- `id3.so` — ID3v1/v2 tag parsing (MP3). Known to have an integer underflow in APIC (album art) parsing: `strndup(data, size)` where `size` can underflow to `(size_t)-1`. However, glibc 2.25's strndup handles this safely (scans for null terminator).
- `mp4.so` — MP4/M4A container parsing
- `flac.so` — FLAC metadata parsing
- `ogg.so` — OGG/Vorbis parsing
- `jpeg.so` — JPEG EXIF parsing
- `png.so` — PNG metadata
- `gif.so` — GIF parsing
- `asf.so` — ASF/WMA/WMV parsing
- `avi.so` — AVI container parsing
- `wav.so` — WAV header parsing
- `m3u.so` — M3U playlist parsing
- `pls.so` — PLS playlist parsing
- Various video codec parsers

**All of these parse attacker-controlled file content as root with no sandboxing.**

### 3. USB Automount (`usb-automount`)
This binary calls `system()` with format strings for mount commands. If the USB volume label or filesystem metadata contains shell metacharacters, there may be command injection opportunities. The binary handles FAT32, exFAT, and NTFS filesystem types.

### 4. Bluetooth (BlueZ 5.x)
- BlueZ runs as root
- Handles HFP (Hands-Free Profile), A2DP (audio streaming), AVRCP (remote control), PBAP (phonebook), MAP (messages)
- The kernel is 4.1.27 — there are numerous known BlueZ/kernel Bluetooth vulnerabilities from this era (BlueBorne, BadBluetooth, KNOB, BrakTooth, etc.)
- **Research needed**: Which specific BlueZ version? Which kernel Bluetooth patches are applied? Are any known Bluetooth RCE CVEs applicable?
- Bluetooth exploits would need to work against a paired or pairing device

### 5. Weston Compositor / Wayland
- Weston runs as root
- IVI Shell extension may have custom protocol handlers
- Wayland socket at `/run/user/root/wayland-0`

### 6. ConnMan (Network Manager)
- Manages Bluetooth PAN networking
- May expose D-Bus interfaces that could be abused post-exploitation

### 7. PulseAudio
- Runs as root
- Handles audio routing including Bluetooth audio
- Processes audio data from USB media playback

### 8. Qt Libraries
- Extensive Qt usage across LGE applications
- QDomDocument XML parsing (used in AppUpgrade)
- Qt multimedia, networking modules

---

## Existing Exploit Attempt (Current Status)

A CVE-2023-26246 exploit has been built and deployed to USB but **not yet confirmed working**. The approach:

1. Place plaintext `.lge.upgrade.xml` on USB with command injection in `<SrcFullPath>`:
   ```xml
   <SrcFullPath>x;sh /media/usb/pwn.sh #</SrcFullPath>
   ```
2. This should be passed to `system("sudo mount -o loop -t ext4 x;sh /media/usb/pwn.sh # %s")`, executing the payload.
3. Payload script (`pwn.sh`) attempts display via framebuffer write, D-Bus OSD, D-Bus popup, and Weston terminal.

**Possible failure points**:
- AppDMClient may reject plaintext XML (original was AES-encrypted)
- SrcFullPath may get a directory prefix prepended, breaking the injection
- Shell metacharacters may be sanitized
- The CVE may be patched in the March 2026 firmware
- The XML nesting/structure may not match what AppUpgrade expects

**Alternative to try**: Encrypt the malicious XML with the known AES-128-CBC key so it passes any encryption check, gets decrypted, then parsed with the injection payload.

---

## What I Need From You

Analyze this system and identify:

1. **Zero-day vulnerability candidates** — based on the software versions, architecture, and attack surface described above, what are the most promising unexplored vulnerability classes?

2. **Bluetooth attack vectors** — given kernel 4.1.27 and BlueZ 5.x running as root with no MAC, which known Bluetooth CVEs could provide RCE? Pairing is possible.

3. **Media parser vulnerabilities** — LMS parses dozens of media formats as root with no sandboxing. What known vulnerabilities exist in the common parser libraries for this era (2017-era glibc 2.25, likely old versions of libid3tag, libflac, libvorbis, ffmpeg/libav components)?

4. **USB filesystem-level attacks** — can a crafted filesystem image (FAT32/NTFS) with malicious volume labels, filenames, or filesystem structures trigger command injection or memory corruption in usb-automount or the kernel's filesystem drivers?

5. **Improvements to the current exploit** — what modifications could make the AppUpgrade command injection more likely to succeed?

6. **Post-exploitation persistence** — once code execution is achieved, what are the best methods to maintain access given the read-only (but remountable) rootfs?

Prioritize approaches that work through **USB insertion only** (no serial console, no network, no prior setup on the device). Bluetooth-based approaches are secondary. Provide specific CVE numbers where applicable.
