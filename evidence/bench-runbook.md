# Bench runbook: from unboxing to verified assessment

Status: operating procedure for the owner's Gen5W AVN on an isolated bench. Each
phase is read-first and gated: do not start a phase until the previous phase's
evidence exists. Tool paths are relative to this project root.

## Phase 0 — physical preparation

1. Photograph the board and all connectors; record silkscreen IDs and PCB revision.
2. Identify `ttyS2` pads (the console is configured in the recovered command
   line) and the USB service port.
3. Before applying power, confirm the unit is on an isolated supply and not
   connected to any vehicle harness.
4. Prepare a USB-UART adapter at **115200 8N1**.

Evidence to keep: photographs, pad map, adapter identity.

## Phase 1 — first boot, serial capture

```
python3 tools/uk_fw/bench_serial.py list
python3 tools/uk_fw/bench_serial.py capture --port <PORT> -o work/bench/boot.log
```

Record: boot loader banner, whether autoboot is interruptible, `oemkm=` presence,
the `esinit` handoff, and the login prompt. The command line recovered from the
package does **not** contain `oemkm=`; the boot loader appends it. Capture it.

If a boot loader prompt appears, stop and record `printenv` before changing
anything.

Evidence to keep: `boot.log`, a note of the exact `oemkm=` value observed.

## Phase 2 — network surface (only if the unit reaches a network)

```
python3 tools/uk_fw/net_surface.py --target <UNIT_IP> --authorised --json work/bench/network.json
```

Triage the captured version strings against `evidence/child-notes/06-daemon-fingerprint-triage.md`.
Do not send exploit traffic; capture versions and banners first.

## Phase 3 — storage acquisition (read-only)

Dump every readable partition before any write. Record per-partition SHA-256 and
a sorted-tree digest. This is the restore baseline; without it, later phases are
irreversible.

**The update system is A/B.** Files are written to the inactive partition and
`/etc/fstab` is rewritten at the end to boot it; the previous partition is left
in place. On a bench unit this is a real rollback path for a rootfs experiment:
if a modified rootfs fails to boot, restore `fstab` (or boot the other partition)
from the console. It is **not** a rollback path for a bad boot image — that image
is RSA-signed and will be rejected rather than rolled back.

Capture `/etc/fstab` and, if the `/update` partition is readable, its flag files
(`activeNaviPath`, `activeResourcePath`, `updateVersionInfo`,
`system_update_completed`) to identify which of `mmcblk0p3` / `mmcblk0p5` is
currently active.

```
# once a rootfs tree exists (extracted or mounted read-only)
python3 tools/uk_fw/dump_survey.py --root <ROOTFS> --json work/bench/rootfs.json
```

`dump_survey.py` reports accounts, empty-password accounts, setuid/setgid,
capabilities, SMACK policy files, systemd units, boot command line, debug nodes,
persistence paths and world-writable files.

Priority outputs:
- `/dev/keystore` mode and SMACK label (see the SMACK note: devtmpfs makes an
  unlabelled node default to `*`).
- `appnavi` / `AppNavi` launcher and `esinit`.
- SMACK rules, if any exist as files.

## Phase 4 — key capture and decryption

The rootfs and application payloads are AES-CBC-128. Nothing in the package or
in the public toolchain contains the key; it is produced by the unit's own
updater and handed to `DecryptToPIPE` at a **random `/tmp` path on every update**.
The documented capture relies on that:

1. Back up the genuine decryptor. It lives at
   **`/app/share/AppUpgrade/DecryptToPIPE`**. Copy it twice — to
   `DecryptToPIPE_OG` beside it and to the USB. Losing it means the unit can
   never update again.
2. Remount `/` read-write, install a patched copy (the public tooling calls it
   `DecryptToPIPE_FK`) in its place, remount read-only, reboot.
3. Trigger a normal update from USB. The unit invokes the decryptor as:
   `DecryptToPIPE -d /tmp/<32 hex> /media/usb/1/<model>/AppUpgrade 0`.
   The patched copy writes that temporary key file to the USB.
4. On finding a `*_key_*.der` on the USB, restore `DecryptToPIPE_OG`, remount
   read-only, reboot.

Then decrypt offline:

```
DecryptToPIPE -d <keyfile> <input> 0 > <output>
```

`DecryptToPIPE` is a glibc x86-64 binary; on a Mac it needs a Linux container (the
public image is Alpine plus `gcompat`). `tools/uk_fw/gen5w_decrypt.py` already
wraps this for a whole package.

Do not attempt to derive the key from the package: entropy, keystream and
block-equality tests already exclude an offline break.

## Phase 5 — component triage

With plaintext:

1. Record exact versions of `dnsmasq`, `hostapd`, `wpa_supplicant`, `BusyBox`,
   `dropbear`, `miniupnpd`, `OpenSSL` and the projection stack.
2. Map each to `evidence/child-notes/01-component-cve-corpus.md` and
   `06-daemon-fingerprint-triage.md`.
3. Hash `AppUpgrade`, `AppDMClient`, `micomd` and compare against the
   `211214`-era components described by CVE-2023-26243…26246.
4. Audit the update envelope parser and the iAP2/CarPlay handlers per
   `evidence/child-notes/07-usb-gadget-protocol-surface.md`.

## Phase 6 — boot image acceptance experiment
Only after a verified restore path exists.

```
python3 tools/uk_fw/ipk_tool.py verify <OEM_IMAGE>
python3 tools/uk_fw/ipk_tool.py resign <OEM_IMAGE> -o work/test-sub --key work/test-key.pem \
    --cmdline "root=/dev/mmcblk0p3 rootfstype=ext4 rootwait init=/bin/sh console=ttyS2,115200n8"
```

The question is what the loader does with a correctly formed but differently
signed container. Outcomes:

| Observation | Meaning |
|---|---|
| Rejected, stock boots | Loader pins the OEM key (expected) |
| Accepted, shell appears | Loader trusts the embedded modulus — critical finding |
| Rejected with an integrity error | Signature covers content as characterised |

Record the exact console output in every case.

## Phase 7 — disclosure

Any confirmed defect goes to Hyundai PSIRT / KISA with a minimal reproducer.
Do not publish a working chain before the vendor has had a reasonable window.

## Gates

1. No write without a full dump and a rehearsed restore.
2. No vehicle connection at any point.
3. No network testing beyond the isolated AP.
4. Every claim bound to captured evidence, not inference.
5. The first gate for the public entry path is **downgrade**: the AppNavi USB
   install is only offered on unpatched builds, and the `>=` version check blocks
official downgrades on a stock unit. Establish whether `260128` offers it before
   planning anything downstream.

## If the public entry path becomes available

The documented sequence is: install a replacement `AppNavi` through Engineering
Mode, which runs `main_loop.sh` from USB root; copy `DecryptToPIPE` and
`decryption_key.der` to the USB; decrypt the OTA offline; patch the rootfs; and
keep every future official update patched. The SSH persistence path is to add
keys to `/etc/dropbear/authorized_keys`, run the shipped publickey installer and
relax the `dropbear@.service` condition. Record each step's evidence; do not skip
the key backup.

## What is already known going in

- Console: `ttyS2`, 115200 8N1; early console at MMIO `0xfc000000`.
- Boot container: RSA-2048 / PKCS#1 v1.5 / SHA-256 over header+payload+tag.
- OEM key manifest: firmware-provided, located by `oemkm=<size>@<phys>`.
- Firmware trust is a userland decision; the kernel only verifies manifests.
- Rootfs AES-encrypted; no offline key recovery.
