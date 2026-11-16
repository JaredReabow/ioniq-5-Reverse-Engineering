# Kia Cerato 2022 AU — Head Unit Jailbreak Guide

## Target
- **Head Unit**: LGE Gen5W IVI (HKMC Premium AVN 2.1)
- **CPU**: Intel Apollo Lake x86-64
- **OS**: OpenEmbedded "mango" 1.0, kernel 4.1.27-abl, glibc 2.25
- **Security**: SMACK MAC, ASLR, stack canaries, PIE, partial RELRO

---

## Attack Vector 1: Engineer Mode PIN (Primary — No Exploit Needed)

The AppEngineerMode binary uses **unsalted SHA-256** to verify PINs. Both
PINs were recovered by brute-forcing the hashes found in the binary.

### PINs

| Mode | PIN | Access Level |
|------|-----|--------------|
| Dealer | `2400` | DTC diagnostics, camera config, factory reset, USB settings |
| Engineer | `19491003` | Full: IP config, shell commands, system config, IAS image update |

### How to Access Engineer Mode

1. **Start the car** (engine running or ACC on)
2. Go to **Settings** on the head unit
3. Navigate to **General** → **About** (or **Software Info**)
4. **Tap the software version number 5-10 times rapidly**
   - On some variants: tap the blank area at the bottom of the About screen
   - A PIN entry dialog should appear
5. Enter `19491003` for **full engineer mode**
   - Or `2400` for dealer mode (less access)
6. Press OK/Enter

### Once Inside Engineer Mode

Engineer mode exposes QML-based diagnostic menus:

- **IpConfig** → `AppEngineerMode_IpConfigMain.qml` — Network configuration
- **IpConfigShell** → `AppEngineerMode_IpConfigMain_Shell.qml` — **Shell command execution**
- **DealerSysConfig** → System configuration
- **DealerswUpdate** → Firmware update controls
- **DiagnosisDealerMode** → DTC read/clear
- **DealerFactoryReset** → Factory reset

### Getting a Root Shell

1. Navigate to the **IpConfig** or **IpConfigShell** section
2. The shell interface uses `runCommandShell_eng()` internally — a C++ function
   that executes shell commands as the AppEngineerMode process
3. AppEngineerMode runs as `App::engineermode` SMACK label with `rwxa` access
   to the floor label `_`, plus `System::iap20`, `System::i2c-1` access

**From the shell, try these commands to get persistent root access:**

```bash
# Check current user/permissions
id
whoami

# Remove the secure console disable flag
rm -f /tmp/secure_console_disable

# Start SSH (dropbear) if available
/usr/sbin/dropbear -R -p 22 -B

# Or check what's available
ls /usr/sbin/dropbear /usr/sbin/sshd /usr/bin/ssh 2>/dev/null

# Get the IP address
ip addr show

# Check network interfaces
ip link show
```

### If Shell Access Is Blocked (Secure Mode)

`EngIPConfigRefactor::getSecureMode()` may gate shell features. If the
IpConfigShell page isn't available:

1. Try **dealer mode** first (`2400`) — some functions may be less restricted
2. Look for a **"Secure Mode" toggle** in the system config menus
3. Try the firmware update page within engineer mode — it may allow loading
   update packages from USB without the normal signature checks

---

## Attack Vector 2: Firmware Update Path (Backup)

### What We Know

The firmware update pipeline:
1. USB inserted with update files at `/media/usb/`
2. AppUpgrade copies `.lge.upgrade.xml` and tar files to `/update/usb/`
3. **DecryptToPIPE** decrypts files (AES-128-CBC) and **verifies RSA signature** (2048-bit)
4. Files extracted to `/rw_data/mnt/root/`
5. **`runSmackRuleScriptFromUsb`** executes `/rw_data/mnt/root/etc/update_start_5w.sh`
   **with ZERO signature verification** — it trusts whatever was extracted

### The Barrier

DecryptToPIPE uses **mbedTLS RSA** with `teruten5_pub.key` (2048-bit, exponent
65537). We have the AES key (`60a93d70f73302a63e5ed0d0ea38be22`) but NOT the
RSA private key. Without the private key, we can't sign a crafted tar.

### Potential Bypasses

1. **Recovery path**: When SMACK `onlycap` is NOT set to "Privileged*",
   `update_start_5w.sh` takes a recovery path that **skips the anchor
   verification** and runs the extracted script directly
2. **Path traversal in tar**: If the tar extraction doesn't sanitize paths,
   a `../../etc/init.d/S99_backdoor` entry could write outside the target
3. **XML injection**: `.lge.upgrade.xml` is parsed by Qt XML — malformed XML
   could cause unexpected behavior

### Known Encryption Details

| Parameter | Value |
|-----------|-------|
| Algorithm | AES-128-CBC |
| Key | `60a93d70f73302a63e5ed0d0ea38be22` |
| IV derivation | `SHA256(basename + int32_signed(payload_size))[:32]` |
| RSA key | 2048-bit, exponent 65537 (`teruten5_pub.key`) |
| Signature | mbedTLS RSA-PKCS#1 v1.5 or PSS |

### USB Update File Structure

```
USB_ROOT/
├── .lge.upgrade.xml          ← Update manifest (XML)
├── HU.tar                    ← Main rootfs update (encrypted+signed)
├── S5W_*.tar                 ← Component updates
├── AppUpgrade                ← Updated AppUpgrade binary (optional)
└── HU/
    └── images*               ← IAS kernel images (optional)
```

---

## Attack Vector 3: SSH with Hardcoded Key (If SSH Is Running)

The firmware contains an LGE SSH authorized key (`rsa-key-20181102`) in the
root user's authorized_keys. If the corresponding private key exists in other
LGE firmware dumps or has been leaked, direct SSH access is possible.

Root password hash exists in `shadow.Global` — could be cracked if short/weak.

---

## Recommended Attack Order

1. **Try engineer mode PIN `19491003`** — zero risk, no exploit needed
2. **Try dealer mode PIN `2400`** — if engineer mode PIN was changed
3. If engineer mode works → use IpConfigShell for root commands
4. If shell is blocked → explore firmware update from within engineer mode
5. If engineer mode fails entirely → firmware update path (needs RSA bypass)
6. As last resort → continue media parser fuzzing with more exotic formats

---

## Security Mitigations Summary

| Feature | Status | Impact |
|---------|--------|--------|
| ASLR | Enabled | Randomizes library addresses |
| Stack canaries | Present | Blocks stack buffer overflows |
| PIE | Yes | Position-independent code |
| RELRO | Partial | GOT is writable (useful for exploits) |
| SMACK MAC | Enabled | Mandatory access control |
| Seccomp | **Not present** | No syscall filtering |
| Sandbox | **Not present** | No process isolation |
| Engineer Mode PIN | **Hardcoded unsalted SHA-256** | Crackable |
| AES firmware key | **Hardcoded** | Can decrypt any update |
| SSH authorized key | **Hardcoded** | Potential direct access |
