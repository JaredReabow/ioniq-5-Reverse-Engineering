# TOCTOU USB Gadget Attack Plan

## Why the Current Approach Fails

`checkHash` in AppUpgrade performs RSA-2048 signature verification on **every firmware
file** BEFORE extraction begins. The RSA signature in the TE2 trailer was computed by
LGE over the original encrypted data. Our re-encrypted rootfs has different ciphertext,
so the signature doesn't match → error -403.

**Cannot be bypassed in software:**
- AppDMClient RSA-verifies AppUpgrade before executing it → can't patch AppUpgrade
- AppDMClient RSA-verifies .lge.upgrade.xml → can't modify the XML
- No RPATH/RUNPATH → can't inject libraries
- MASS_PRODUCT build mode → ignores `/update/disableEncryptionUpdate`
- No public leak of Teruten RSA private key

## The TOCTOU (Time-of-Check-to-Time-of-Use) Attack

### Concept

checkHash verifies ALL files, THEN extraction starts. There's a window between
verification and use. If we serve the **genuine** file during checkHash and swap
to our **modified** file before extraction reads it, the signature check passes
but our payload gets extracted.

### Verified Timeline (from upgrade_log)

```
T+0s    [checkHash] iasImage                    → (0) PASS   ~5s
T+5s    [checkHash] mango-rootfs.tar.gz         → (0) PASS   ~61s  
T+66s   [checkHash] mango-vr.tar.gz             → (0) PASS
T+66s   [checkHash] mango-rwdata.tar.gz         → (0) PASS
...
T+66s   [slotHashCheck] all passed
T+66s   [startInstall] begins
T+81s   DecryptToPIPE ... mango-rootfs.tar.gz   → EXTRACTION
```

**Window**: ~15 seconds between last checkHash pass and DecryptToPIPE reading rootfs.

### Hardware Required

- **Raspberry Pi Zero 2 W** (~$15 AUD) — has USB OTG via micro-USB port
- **USB-A male to micro-USB male adapter/cable** (OTG adapter)
- **MicroSD card** (8GB+ for the firmware image)

### How It Works

1. Pi Zero configured as USB mass storage gadget (`g_mass_storage`)
2. Backing file is a FAT32/exFAT disk image containing the genuine firmware
3. Pi monitors SCSI block read commands via a custom gadget driver or userspace
4. **Phase 1 (checkHash)**: Serve genuine `mango-rootfs.tar.gz` blocks
5. **Detect transition**: After observing full sequential read of rootfs (884MB),
   detect the pause between checkHash completion and install start
6. **Phase 2 (Swap)**: Replace rootfs blocks in the backing image with our
   re-encrypted version, then trigger SCSI "Unit Attention: Media Changed"
   to invalidate the host's VFS cache
7. **Phase 3 (Extraction)**: Host re-reads file metadata, gets our modified rootfs,
   DecryptToPIPE decrypts it → patched rootfs extracted

### Cache Invalidation Strategy

The Linux kernel caches USB mass storage reads. To force re-read:

**Option A**: SCSI Unit Attention
- Modify the gadget function to send `UNIT ATTENTION` sense data with
  ASC/ASCQ `0x28/0x00` ("Not ready to ready change, medium may have changed")
- Host kernel invalidates all cached pages for the block device
- Next read goes through to the gadget

**Option B**: funcfs/configfs gadget swap
- Unbind and rebind the mass storage function
- Host sees device disconnect/reconnect
- USB re-enumeration, fresh mount
- More disruptive but guaranteed cache invalidation

**Option C**: Block-level interception (most elegant)
- Custom gadget driver that tracks which blocks are being read
- First read of rootfs blocks → serve original
- Second read of same blocks → serve modified
- No cache invalidation needed; the gadget itself serves different data

### Implementation: Custom FunctionFS Gadget (Option C)

```python
#!/usr/bin/env python3
"""TOCTOU USB Mass Storage Gadget for Kia Gen5W jailbreak"""

# This runs on the Pi Zero 2 W
# Uses Linux USB gadget framework with a custom block-serving layer

# Key idea: maintain TWO disk images
# - genuine.img: original firmware USB contents
# - modified.img: same but with our re-encrypted mango-rootfs.tar.gz
#
# Track read patterns. When the same LBA range (rootfs file blocks) is
# read a SECOND time, switch to serving from modified.img for those blocks.

ROOTFS_OFFSET = ...  # LBA offset of mango-rootfs.tar.gz on the FAT filesystem
ROOTFS_SIZE = ...    # Size in blocks

read_count = {}  # LBA → read count

def handle_read(lba, length):
    for block in range(lba, lba + length):
        read_count[block] = read_count.get(block, 0) + 1
    
    # If any rootfs block has been read before, serve from modified image
    if any(read_count.get(b, 0) > 1 for b in range(lba, lba + length)
           if ROOTFS_OFFSET <= b < ROOTFS_OFFSET + ROOTFS_SIZE):
        return read_from(modified_img, lba, length)
    else:
        return read_from(genuine_img, lba, length)
```

### Simpler Alternative: Manual Swap with Two USB Sticks

If the Pi Zero approach is too complex:

1. Format two USB sticks as exFAT with the **same volume label** "KIAUSB"
2. USB-A: contains genuine firmware (all original files)
3. USB-B: contains modified firmware (our re-encrypted rootfs, updated .ver)
4. Plug in USB-A → update starts → checkHash begins
5. Watch for checkHash to finish ALL files (takes ~70 seconds from start)
6. **Quickly** pull USB-A and insert USB-B
7. If the system re-reads from USB-B, extraction uses our modified rootfs

**Risk**: The system might abort on USB disconnect, or mount USB-B at a different
path. This is much less reliable than the Pi Zero approach.

### Files Needed on the Gadget

The Pi Zero needs two filesystem images:
1. **genuine.img** — exact copy of current KIAUSB with all original files
2. **modified.img** — same layout but `HU/images/mango-rootfs.tar.gz` is our
   re-encrypted version, and `2022_Cerato_AU.ver` has updated CRC32/size

Both images must have identical FAT layout (same cluster allocation for the rootfs
file) so the block-level swap works cleanly.

## Payload Redesign Needed

Current payload starts a socat TCP listener on port 4444 — **useless without WiFi**.

New payload options:
1. **USB serial gadget shell**: After jailbreak, plug in Pi Zero configured as
   USB CDC ACM (serial) device → `getty` on `/dev/ttyGS0` → serial console
2. **Bluetooth RFCOMM shell**: Start `rfcomm` listener → connect from phone
3. **USB ethernet gadget**: Pi Zero as USB RNDIS/ECM network adapter →
   socat shell accessible over USB network link
4. **Write SSH keys + enable dropbear**: More permanent access method

**Recommended**: USB ethernet gadget (RNDIS) — gives a full network link over USB,
making the socat shell approach viable after all.

## Risk Assessment

- **Brick risk**: Low — A/B partition scheme preserves current system
- **Detection risk**: Low — update logs show failure, not tampering
- **Success probability**: Medium-High if cache invalidation works
- **Reversibility**: Full — reflash original firmware from USB
