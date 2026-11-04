# Field journal — bringing the rig up on real hardware

A chronological record of getting the dynamic-USB gadget working against the physical head
unit: every bug, the wrong turn, and the fix. Dates 2026-10-31 → 2026-11-04.

## 0. Proving the mechanism before touching hardware (10-31 → 11-02)
- **Local PoC** (`poc/run_poc.sh`): the two-pass race with real `md5sum`/`openssl`/`dd`/`tar`
  and a read-close-triggered swap — check passes on benign, installer consumes evil.
- **Native two-open run** (bench, x86-64, not included here): the genuine `DecryptToPIPE` +
  real `md5sum` verify genuine / install evil. The HU is Intel x86-64, so these are the real
  binaries, not stand-ins.
- **Byte-exact evil envelope**: a real `mango-rootfs.tar.gz` identical in size/IV to the
  genuine signed envelope, decrypting to a rootfs with `wideopen.service`. The "could you
  even build the swapped image?" gap is closed.
- **Correction folded in:** the rootfs is opened **exactly twice** (md5 check, then
  DecryptToPIPE install); the RSA verify is over `md5sum.txt`, not a third rootfs re-read.
  So `switch_after_pass = 2`, and an earlier off-by-one in the pass counter (which would
  have served `G,G,E` → installer reads genuine → silent no-op) was fixed to 1-based
  physical passes (`G,E,E`).

## 1. Pi provisioning (11-03 → 11-04)
Pi Zero 2 W at `10.10.10.153` (host `toctou`), Debian 13 arm64, kernel 6.18. Installed
`nbdkit` + `nbdkit-plugin-python` + `nbd-client`. SSH is password-only (no key installed).

**Bug — no UDC appeared.** `config.txt` had `dtoverlay=dwc2,dr_mode=host` (wrong), and later
the overlay sat under the **`[cm5]`** filter section, so on a Pi Zero 2 W it was ignored and
the controller fell through to the `dwc_otg` *host* driver — no gadget possible.
**Fix:** append `dtoverlay=dwc2,dr_mode=peripheral` under **`[all]`** and reboot. Now `dwc2`
owns `3f980000.usb` and `/sys/class/udc` is populated. (A lesson: an empty `ls /sys/class/udc`
is easy to misread as "ready" — check the driver actually bound.)

## 2. Gadget bring-up (`03_deploy_gadget.sh`) (11-04)
Three bugs fixed on the live Pi:
1. **`test -S /dev/null` under `set -euo pipefail`** — `/dev/null` is a char device, not a
   socket, so `-S` is false and the script aborted after starting nbdkit. → `test -c`.
2. **LUN ordering** — the script wrote `lun.0/file` before `lun.0/ro`; `ro` can't change once
   a backing file is attached → "Device or resource busy". → write the file **last**.
3. **nbd-client boot race** — `getaddrinfo(127.0.0.1)` fails "Address family … not supported"
   before `::1` is up at boot. → 15×/2 s retry loop + `After=network-online.target`.

Result: gadget bound (`configfs-gadget.ioniq_toctou`), `/dev/nbd0` = 27 GB, VID:PID
`0781:5591` "USB DISK", removable rw.

## 3. Auto-start service (11-04)
`toctou-gadget.service` (Type=oneshot, RemainAfterExit, KillMode=none, ExecStart=03,
ExecStop=99, ExecStartPre waits for the UDC). Verified across two reboots the gadget
auto-presents with the pass counter clean.

**Bug — every real read threw `TypeError: int + memoryview`.** The plugin declared
`API_VERSION = 2` but implemented the v1 `pread` (took an int count, returned bytes); real
nbdkit 1.42.3 passes a **writable buffer**. → split the logic into `_serve(count, offset)`;
`pread` now does `buf[:] = _serve(len(buf), offset)`.
**Critical lesson:** the preflight's check D imports the plugin and calls `pread` with an int
— so it passed while the live path was broken. **Always smoke-test *through* nbdkit**, not
just the plugin in isolation.

## 4. Offline-robust logging (11-04)
The first real car session produced an ambiguous log (untimed, volatile journal; NTP even
stepped the clock backwards). Hardened logging: monotonic timestamps, `boot_id` session
headers, per-pass byte tallies, and (added later) a per-read log of every rootfs-region read.
Made journald persistent (overriding the RPi vendor `40-rpi-volatile` drop-in) and installed
`fake-hwclock` so the wall clock stays roughly sane offline. See `docs/02` and `DEPLOY.md`.

## 5. Reading the car logs — two wrong turns, corrected
- **Wrong turn #1:** I blamed *driving* for the failures ("the HU can't update in motion").
  **The owner corrected me — the IONIQ updates fine while driving.** Retracted. Re-analysis
  of the DLT export showed heavy, legitimate update activity for hours, with three completed
  firmware updates ending `SWAP FINISH`. The ~1 hour the owner felt was mostly the separate
  **17 GB navi map** (`NaviUpdateApp`), which is *not* in the rootfs swap region → served
  genuine → irrelevant to the payload.
- **Wrong turn #2:** I then blamed the car cutting *power* to the Pi at ignition. **The owner
  corrected me again — the Pi was on battery for the last three attempts.** Retracted.

Both corrections mattered: they ruled out the easy explanations and forced finding the real
two root causes below.

## 6. Root cause A — the swap never switched (fragile trigger) (11-04)
The per-read log from a real car update captured **429,264 rootfs-region reads ≈ two full
passes (check + install), ALL served GENUINE, zero evil** — the installer got the genuine
rootfs every time. This happened within one stable Pi boot, so it was **not** the reboots.

The bug: the old trigger required the previous pass to reach within 8 KB of the region
**end**. But the HU reads the file **tail first** and caches the last blocks, so the
sequential check read stops short of the end → pass #2 was never detected → never switched.

**Fix:** trigger on **return-to-start-after-deep** instead (see `docs/02`). Validated by
replaying the real 429 k-read trace through the patched plugin: the switch fires at read
**#214639** — exactly the install-pass start (214,638 genuine check reads, then evil).

## 7. First switch on the real car (11-04)
Next car attempt with the trigger fix: `PASS #1` read the full ~879 MB rootfs GENUINE
(md5 passes), then **`*** SWITCH at pass #2 ***`** — the install pass flipped to EVIL. The
return-to-start-after-deep trigger is now **proven on real HU reads**, not just replay. But
the Pi **rebooted ~23 s into the install** (new `boot_id`), so only ~14 % of the evil image
was delivered and that update aborted.

## 8. Root cause B — the reboot is the systemd hardware watchdog (11-04)
Not power (owner confirmed battery) and not a panic (`pstore` empty, `throttled=0x0`). The
prev-boot journal ends abruptly mid-run = a **hardware-watchdog reset**: systemd had
`RuntimeWatchdogUSec=1min` arming the BCM2835 wdt, and under the heavy install-pass I/O the
main loop stalled > 1 min → the wdt hard-reset the board → USB vanished → install aborted.

**Fix:** `/etc/systemd/system.conf.d/99-no-watchdog.conf` (`RuntimeWatchdogSec=0`,
`RebootWatchdogSec=0`). Validated under full load: re-armed and read the whole 879 MB region
**twice** via `/dev/nbd0` (check + install simulation) — `boot_id` **unchanged** (no reboot),
and the entire install pass served evil (genuine=214,645 / evil=214,631 reads).

**Follow-up gotcha (stuck at 0%):** the next car attempt still rebooted and the HU sat at 0%.
Cause: the watchdog disable had been applied **live** (`daemon-reexec`), which does **not**
reliably disarm an already-armed hardware watchdog — it only fully takes effect on the **next
boot**. On the fresh boot (`becbee6a`) systemd is confirmed not arming the wdt
(`RuntimeWatchdogUSec=0`, no "Using hardware watchdog" in dmesg).

## 9. Where it stands
- Mechanism proven (native two-open race); evil envelope built; gadget enumerates and
  auto-arms; **swap switches on the real head unit**; watchdog reboot fixed on a clean boot.
- **Open:** a single clean on-car run that stays up through the full multi-minute check +
  install so the *entire* evil rootfs lands, then confirm the on-device marker. If the Pi
  still resets with the watchdog confirmed off, the remaining suspect is a **dwc2 gadget
  hard-lock under the HU's sustained read** (an SoC reset with no `pstore`) — which would
  need serial/netconsole capture or dwc2 tuning. The local two-pass `/dev/nbd0` load test
  never reboots (it bypasses USB), so any residual instability is specific to the dwc2
  gadget path under the HU access pattern.
