# Gen5W operating model: update flow, A/B recovery and persistence

Status: synthesis of the public "Gen5 Wide-Open" documentation with this
programme's static findings. Sources are public GitLab projects and the public
wiki (`g4933/wideopen`, `g4933/gen5w/*`). No device was used and no exploit was
executed.

## Why this matters

The userland is AES-encrypted, so the operating model could not be derived
offline. It is nevertheless **publicly documented**, and that documentation
answers most of the questions the ciphertext was hiding: how an update is
validated, how it is applied, where the version check lives, and how persistence
survives an official update.

## Documented update flow

1. On USB insertion, **`AppSetup`** scans the USB root for `.lge.upgrade.xml`.
2. It invokes **`DecryptToPipe`** — a binary outside `AppUpgrade` — to decrypt
   that file.
3. It reads the version and proceeds only if it is **greater than or equal to**
   the installed version.
4. `AppUpgrade` copies the USB `AppUpgrade` into `/update/usb/` and hands control
   to that copy.
5. The new `AppUpgrade` performs three independent operations:
   - **filesystem**: for each file in `images/`, checksum → decrypt → extract →
     copy to the **inactive** partition;
   - **maps**: extract `appnavi.tar` (encrypted) and `naviX.tar` into `/navi/` or
     `/navi2/` according to `/update/activeNaviPath` and
     `/update/activeResourcePath`; the newly written directory is always the one
     **not** currently active;
   - **firmware**: take the unencrypted `frontkey` binary, decrypt and extract
     `modem_{REGION}.tar.gz` and `update.tar.gz`.
6. On completion it updates `activeNaviPath` / `activeResourcePath`, clears the
   `/update` flag files, **rewrites `/etc/fstab` to boot the new partitions**, and
   reboots.
7. The previous partition and previous navigation directory are left in place as
   a fallback.

Flag files in `/update` include `disableEncryptionUpdate`, `activeNaviPath`,
`activeResourcePath`, `updateVersionInfo`, `system_update_completed`,
`resumeBlockNumber`, `force_launch` and others.

## A/B recovery — the important safety fact

The filesystem is written to the **inactive** partition and the switch happens by
rewriting `/etc/fstab` at the end. Consequences:

- A modified rootfs that fails to boot can be rolled back by restoring `fstab`
  (or by selecting the previous partition) **from a bench console**.
- This substantially reduces the brick risk of a rootfs modification, provided
  the console or storage is reachable.
- A write that corrupts the *bootloader* or the active boot image is a different
  matter: the boot container is RSA-signed (see
  `evidence/eu-boot-container-signature.md`), so a bad boot image is rejected
  rather than rolled back.

## `disableEncryptionUpdate`

If `/update/disableEncryptionUpdate` exists, `AppUpgrade` performs an
**unencrypted** update:

- no decryption is attempted, so the package must be entirely plaintext;
- **the version check via `.lge.upgrade.xml` still runs**;
- the upgrade is otherwise identical.

The public patcher creates that file by running a shell script, which itself
requires pre-existing code execution.

## Entry mechanism (public)

`navi_extended` is a replacement for `AppNavi` placed in `/Bin`. It is installed
through **Engineering Mode → Dynamics → Navigation → Config → "Update AppNavi
from USB"**. It finds the USB and runs `main_loop.sh` from its root. The script
copies `DecryptToPIPE` and `decryption_key.der` off the unit.

Documented preconditions:

- an **unpatched/older** build; if the Config entry shows "This feature is
  currently unavailable", the unit must be **downgraded** first;
- an official update on the USB, because the navigation app is extracted from it;
- exFAT-formatted USB.

## Persistence

- Patch `AppNavi` to call `navi_extended` before its normal work, so future
  updates keep the entry point.
- Install `wideopen.service`.
- Every subsequent official update must be re-patched, or the unit loses the
  modification.
- Public SSH path: remount `/` read-write, add keys to
  `/etc/dropbear/authorized_keys` (the shipped key lacks a trailing newline), run
  `/etc/dropbear/dropbear_publickey_installer.sh`, and edit
  `dropbear@.service` to drop its `ConditionPathExists` guard.

## Cross-reference with the static findings

| Public statement | Static confirmation |
|---|---|
| Version check happens in the upgrader | Consistent: the kernel verifies *manifests* using `.manifest_keyring`; it does not compare firmware versions |
| `DecryptToPipe` is a separate binary | Consistent with the kernel providing keystore primitives while the OTA format is userland-owned |
| Update writes to an inactive partition | Consistent with the recovered command line exposing two roots (`mmcblk0p3` for 1280 units, `mmcblk0p5` for 1920/p5) |
| `frontkey` is unencrypted | Confirmed: the `MKBD_*.bin` files are plaintext Renesas RL78 firmware |
| `.lge.upgrade.xml` is decrypted by `DecryptToPipe` | Confirmed: the file has entropy 8.0 in the package |

The two roots in the recovered command line are therefore the A/B pair, not just
display variants. This is a correction to the earlier interpretation: `p3` and
`p5` are the two system partitions of the same device family.

## What this changes for the plan

1. **Downgrade is the first gate.** The public entry requires a build where the
   AppNavi USB install is still offered. A `260128` unit likely presents "This
   feature is currently unavailable", and the documented remedy is a downgrade —
   which the `>=` version check blocks on a stock unit.
2. **The version check is userland and is the real anti-rollback control.** No
   kernel rollback counter was found in the recovered configuration or symbols.
3. **A/B gives a genuine recovery route** for rootfs experiments, which is the
   single most useful safety fact discovered so far.
4. **Key extraction is the pivot.** Everything downstream — decryption, patching,
   custom firmware — depends on obtaining `DecryptToPIPE` and
   `decryption_key.der`, and the only documented route to those needs code
   execution first.

## Open questions

- Does a stock `260128` still offer "Update AppNavi from USB", or has it been
  removed? This decides whether downgrade is required at all.
- Is the version comparison `>=` on a normalized tuple, and is it per package or
  per file?
- Does the device enforce any rollback counter outside `AppUpgrade`?
- Is `.lge.upgrade.xml` itself signed, and if so, by the same key as the boot
  container?
- On the bench unit, which of `mmcblk0p3` / `mmcblk0p5` is active at capture time?

## Sources

- `gitlab.com/g4933/gen5w/navi_extended` (README, releases)
- `gitlab.com/g4933/gen5w/update-patcher` (README, `disable_encryption.sh`)
- `gitlab.com/g4933/gen5w/update_decryptor` (README)
- `gitlab.com/g4933/wideopen` wiki: `Software/Update_Process`, `Software/Network`,
  `Unit/Pinouts`, `Hardware/lowlevel`
- `g4933.gitlab.io/wideopen` landing page
