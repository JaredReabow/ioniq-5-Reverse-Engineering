# Kia Cerato 2022 AU — Updated Jailbreak Strategy

## Key Discovery: Engineer Mode Has Encryption Toggle

The engineer mode "S/W Update" menu (accessible from the MAIN engineer mode
screen, NOT the "Log System" menu) contains these options:

1. **Previous Version** — view previous firmware versions
2. **Encryption Update** — **TOGGLE TO DISABLE ENCRYPTION FOR USB UPDATES**
3. **Update From USB** — trigger USB firmware update directly
4. **Scheduled Update Test** — test time mode toggle
5. VESS/ADP/AMP Logging

### The Encryption Update Toggle

Located at: `S/W Update → Encryption Update` in engineer mode

- **"Disable" button** → Creates `/update/disableEncryptionUpdate` → **DISABLES
  encryption checks** for firmware update files
- **"Enable" button** → Removes the flag → re-enables encryption

**HOWEVER:** On MASS_PRODUCT builds (which your car almost certainly is), the
string `"MASS_PRODUCT or PENETRATION Build mode -> Ignore disableEncryptionUpdate"`
appears in the code. This means the flag MAY be ignored.

**BUT:** There's also `force_ua_test.txt` at `/update/force_ua_test.txt` which
triggers the `"### Unencryption Update. ####"` path and this check may NOT
be blocked by MASS_PRODUCT mode.

## Strategy A: Disable Encryption via Engineer Mode (Try First)

### Step 1: Enter Engineer Mode
1. Go to Settings → General → About
2. Tap software version 5-10 times rapidly
3. Enter PIN: `19190301`

### Step 2: Navigate to S/W Update (on the MAIN screen)
- From the main engineer mode screen, look for "S/W Update" button
- It should be one of: Software, Hardware, Dynamic, **S/W Update**, Diagnostic,
  System Config, Log System, Auto Test
- **Do NOT go to "Log System"** — that's a different menu

### Step 3: Disable Encryption
- Select "Encryption Update" from the left menu
- Press the **"Disable"** button
- This creates `/update/disableEncryptionUpdate`

### Step 4: Plug in USB with Update Package
- USB must be FAT32
- Root contains: `.lge.upgrade.xml` (the encrypted XML from the firmware)
- This should activate the normal Settings update button OR the engineer
  mode "Update From USB" option

### Step 5: If disableEncryptionUpdate is Ignored (MASS_PRODUCT)
Try using the **"Update From USB"** option in engineer mode instead of the
normal Settings update. Engineer mode may have a separate code path
(`LaunchUpgradeViaUSB`) that respects the encryption disable flag.

## Strategy B: USB Update with Original Encrypted Firmware

If encryption can't be disabled, use the REAL encrypted firmware files:

### What You Need on USB (FAT32, 32GB):
```
USB_ROOT/
├── .lge.upgrade.xml         ← (17812 bytes, encrypted, from firmware dump)
├── HU/
│   ├── images/
│   │   ├── mango-rootfs.tar.gz    ← (879MB, encrypted)
│   │   ├── mango-rwdata.tar.gz    ← (16MB, encrypted)
│   │   ├── mango-vr_fixed.tar.gz  ← from vrau/ (570MB)
│   │   ├── mango-vr.tar.gz        ← from vrau/ (45MB)
│   │   ├── new_gui.tar.gz         ← (2GB, encrypted)
│   │   ├── iasImage               ← (6MB)
│   │   ├── iasImage_sub           ← (6MB)
│   │   └── ... (other iasImage variants)
│   └── firmware/
│       ├── update.tar.gz           ← (70MB, encrypted)
│       └── modem/au_le22/modem_au_le22.tar.gz ← (127MB)
└── .whatsnew.tar.gz          ← (325KB, encrypted)
```

Total: ~3.7GB (AU-specific files only, skip EU modem/VR files)

### The Firmware Update:
- Version in XML: `5W.XXX.S5W_L.001.001.260319` (HIGHER than your `240710`)
- This is a REAL firmware update from Kia — it will update your head unit
- The update process extracts and runs `update_start_5w.sh` as root
- This doesn't give us arbitrary code execution, but it updates to the
  newer firmware which may have different exploitable behaviors

## Strategy C: force_ua_test.txt (Advanced)

The binary checks for `/update/force_ua_test.txt` before deciding encryption
mode. When this file exists (`g_bfotaUaTest` is true), the
`"### Unencryption Update. ####"` path is taken.

This file is NOT blocked by the MASS_PRODUCT check (separate code path).

### How to Create It:
You'd need write access to `/update/` which requires:
- Root shell access (which we don't have yet), OR
- A bug in one of the engineer mode features that writes to `/update/`

The engineer mode already writes to `/update/`:
- `touch /update/eng_progress_enable`
- `/update/test_region.txt`
- `/update/eng_soc_level`

If we can find a way to make it write `force_ua_test.txt`...

## Decrypted XML Format (for reference)

```xml
<?xml version="1.0" encoding="utf-8"?>
<wideavn>
    <upgrade-mode>developer</upgrade-mode>
    <build-date>2026-03-19</build-date>
    <version>5W.XXX.S5W_L.001.001.260319</version>
    <car-variant>..._bdpe_...</car-variant>
    <partition>newpartition3rd</partition>
    <newfirmware>newfirmwarestructure</newfirmware>
    <firmware version="" src="/HU/images/mango-vr_fixed.tar.gz">vrfix</firmware>
    <firmware version="" src="/HU/firmware/modem">modem</firmware>
    <firmware version="0.7.13.13470" src="/HU/firmware/dab">dab</firmware>
    <firmware version="6.12.01" src="/HU/firmware/gps">gps</firmware>
    <firmware version="2.1f" src="/HU/firmware/frontkey/nx4" vehicle="nx4">jf</firmware>
    <firmware version="2.22" src="/HU/firmware/frontkey/us4hev" vehicle="us4hev">jf</firmware>
    <firmware version="170912" src="/HU/firmware/micom">micom</firmware>
</wideavn>
```

### Encryption Details:
- **AES-128-CBC**, key: `60a93d70f73302a63e5ed0d0ea38be22`
- **IV for .lge.upgrade.xml**: `85c3626b2553c354fd2bfc023c8c1438`
  (derived from filename + filesize, exact formula TBD)
- **RSA**: 2048-bit, `teruten5_pub.key` (we only have the PUBLIC key)
- All .tar.gz files are also encrypted (not just the XML)

## Recommended Order of Attack

1. **Enter engineer mode** (`19190301`)
2. **Go to S/W Update** (main screen, NOT Log System)
3. **Try "Encryption Update → Disable"** to disable encryption
4. **Copy original encrypted .lge.upgrade.xml to FAT32 USB**
5. **Try "Update From USB"** in engineer mode
6. If that doesn't work, try the **normal Settings update button**
7. If encryption disable is ignored → need full firmware on USB (Strategy B)
8. If that works → intercept the update process for code execution
