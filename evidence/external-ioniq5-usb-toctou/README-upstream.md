# IONIQ 5 USB-update TOCTOU

> Lots of credit to https://github.com/JaredReabow/ioniq-5-Reverse-Engineering and the nice people on the Gen5W discord.

A time-of-check/time-of-use vulnerability in the IONIQ 5 (Gen5W_L) head-unit USB
firmware-update path, with a runnable demonstration and the real dynamic-USB hardware
rig that exploits it.

**The flaw in one line:** AppUpgrade **verifies** an update file and then **installs** it
in a *separate process that re-opens the same file*, while the file lives on
attacker-controlled removable media — so a device that returns different bytes on the
second read installs unsigned content after a signed check has already passed. The system
rootfs has no boot-time integrity (no dm-verity), so the swapped image simply runs at next
boot.

> **Scope & authorization.** This is right-to-repair / own-device security research on the
> author's **own, decommissioned, off-road** IONIQ 5 head unit (build 260128). The payload
> is a **benign** proof marker (a root service that writes a log file). No OEM private key
> is used or forged. See [`SECURITY.md`](SECURITY.md).

---

## Why it works (the four facts)

1. **Check and use are separate re-reads.** The check is `ionice -c3 md5sum %1 | awk`
   plus a `PKCS#1 sig. verify`; the install is `/app/share/AppUpgrade/DecryptToPIPE %1 |
   tar` — distinct `system()`/`popen()` calls, so `%1` is `open()`ed twice with the
   integrity decision made in between.
2. **The big image is read in place from the USB stick**, not copied to local storage
   (only the ~6 MB boot images go to `/tmp`). So both reads hit attacker media.
3. **No post-write verification of the system partition.** The post-install "verify" is
   source-side; "System Update Verify" measures **46 ms** — far too short to re-hash an
   879 MB partition.
4. **No rootfs integrity at boot.** The rootfs is plain ext4 (A/B on `mmcblk0p3`/`p5`),
   no dm-verity; the bootloader RSA covers only the boot image, which we leave genuine.

The attacker needs **no RSA private key** (the genuine signed image passes the check) and
already holds the TE2 AES content key, so the swapped-in blob is a valid-looking encrypted
envelope that decrypts to an attacker rootfs. Full detail: [`docs/01-vulnerability.md`](docs/01-vulnerability.md).

## The exploit rig

A Raspberry Pi Zero 2 W presents to the head unit as a USB mass-storage stick whose bytes
are **dynamic per read pass**:

```
   HU USB host  ──►  dwc2 UDC (gadget)  ──►  configfs f_mass_storage  lun.0 = /dev/nbd0
                                                                            │
                                            nbd-client ◄── nbdkit (Python plugin) ◄── usb.img (27 GB exfat)
                                                                            │
                                   nbdkit_toctou.py serves the rootfs byte-region GENUINE on
                                   read-pass #1 (the md5 check) and EVIL from read-pass #2
                                   (the install) — "verify A, install B".
```

The swap trigger, the offline-robust logging, and every bug found bringing this up on real
hardware are in [`docs/04-field-journal.md`](docs/04-field-journal.md). Deployment runbook:
[`pizero/DEPLOY.md`](pizero/DEPLOY.md).

---

## Repo map

| Path | What |
|---|---|
| [`REPRODUCE.md`](REPRODUCE.md) | **Rebuild from zero** — the from-nothing runbook (firmware + key + a Pi → running rig). |
| [`docs/01-vulnerability.md`](docs/01-vulnerability.md) | The TOCTOU flaw, why the bytes can differ, why it persists, and an honest evidence grading. |
| [`docs/02-attack-chain.md`](docs/02-attack-chain.md) | End-to-end attack chain + the Pi dynamic-USB gadget architecture and swap logic. |
| [`docs/03-evidence.md`](docs/03-evidence.md) | What's proven from the binary, the car's own DLT logs, and native/VM execution. |
| [`docs/04-field-journal.md`](docs/04-field-journal.md) | Chronological bring-up on real hardware: every bug and fix (swap trigger, watchdog reboot, offline logging, DLT timeline analysis). |
| [`docs/05-mitigations.md`](docs/05-mitigations.md) | The fix patterns (verify-and-use-the-same-bytes, dm-verity). |
| [`poc/`](poc/) | **No-car** runnable demo: reproduces the two-pass race with real `md5sum`/`openssl`/`dd`/`tar`. |
| [`pizero/`](pizero/) | The real dynamic-USB gadget: nbdkit swap plugin, build/deploy scripts, systemd unit, host config, and the vendored `gen5w_decrypt.py` / `te2_encrypt.py` crypto tools. |

## Quick start — the no-car PoC

Needs only `sh`, `openssl`, `python3`, `tar`, `dd` (no car, no hardware):

```sh
poc/run_poc.sh
```

It generates a throwaway OEM keypair locally (only so a real `openssl` verify can run end
to end), signs a benign image, then runs the check and the install against a USB emulator
that swaps benign→evil on the verify read-close. Expected: **CHECK passes on benign bytes,
installer consumes evil bytes** — verified A, installed B.

## Rebuild from zero

**[`REPRODUCE.md`](REPRODUCE.md) is the from-nothing runbook** — assumes only the genuine
firmware package (fetch elsewhere), the TE2 content key (you have it), and a Pi Zero 2 W.
Everything else needed is in this repo, including the decrypt tool (`pizero/gen5w_decrypt.py`).
In brief:

1. Put the TE2 key in `pizero/key.local` (see `pizero/key.local.example`) or
   `export TE2_CONTENT_KEY=…`.
2. `pizero/01_make_evil_rootfs.sh` → build the byte-exact evil `mango-rootfs` envelope.
3. `pizero/02_build_usb_image.sh` → stream the genuine package into a 27 GB exfat `usb.img`
   with the rootfs written first (one contiguous extent); emits `regions.json`.
4. `pizero/04_preflight.sh` → go/no-go gate (baseline md5, evil extent/shape, dry-run swap).
5. `pizero/03_deploy_gadget.sh` (or enable `toctou-gadget.service`) → present the gadget.
6. Insert into the HU, start the update, read the log for `served=EVIL` on the install pass.

Deployment detail (offline logging, re-arm): [`pizero/DEPLOY.md`](pizero/DEPLOY.md).
Live status: [`pizero/STATUS.md`](pizero/STATUS.md).

## Secrets kept out of git

This repo is **publishable**: no key material is committed. The only secret is the **TE2
content key**, supplied at runtime via `pizero/key.local` or `$TE2_CONTENT_KEY` (gitignored).
The decrypt tool itself (`pizero/gen5w_decrypt.py`) is vendored and reads the key from there,
so the repo is self-contained given the firmware and the key.

## Status

- **Vulnerability:** well-evidenced from the real binary + the car's own DLT logs.
- **Mechanism:** proven winnable — the genuine x86-64 `DecryptToPIPE`/`md5sum` run natively
  against a swapped file verifies A and installs B (done on the bench; see docs/03).
- **On-car swap:** the dynamic-USB gadget has **switched on the real head unit** (install
  pass flipped to EVIL). Remaining work is purely operational: keeping the Pi stable for
  the full multi-minute check+install so the *entire* evil rootfs is delivered, then
  confirming the on-device marker. See [`docs/04-field-journal.md`](docs/04-field-journal.md).

## Disclaimer

No license is granted and no warranty is given. This repository is published **as is**, for
**educational and defensive security-research purposes only**. To the maximum extent permitted
by law, the author disclaims all warranties and accepts **no liability** for any damage, data
loss, bricked hardware, or other consequences arising from its use.

- **Use only on hardware you own or are explicitly authorized to test.** Modifying a vehicle
  head unit can brick it, void warranties, and — on a vehicle in service — affect safety.
- **You are solely responsible** for ensuring your use complies with all applicable laws and
  regulations in your jurisdiction. The author does not condone, and is not responsible for,
  any unauthorized or unlawful use by others.
- This work was carried out on the author's **own, decommissioned, off-road** unit with a
  **benign** proof-of-concept payload; it is not a turnkey attack against anyone else's
  vehicle. See [`SECURITY.md`](SECURITY.md) for the full scope and authorization statement.
- **No affiliation or endorsement.** Not affiliated with, authorized, or endorsed by Hyundai,
  Kia, HKMC, LG Electronics, or the credited projects and individuals. All trademarks belong
  to their respective owners.
