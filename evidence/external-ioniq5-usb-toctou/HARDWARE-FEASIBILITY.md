# V-059 hardware feasibility: what the exploit actually asks of a USB device

Companion to the imported upstream documentation. The question this answers: **what does the verify-then-install TOCTOU require of the fake USB device, and which cheap boards can satisfy it?**

Nothing here was run. It is an engineering assessment of the mechanism described in `01-vulnerability.md`, checked against what this repository knows about the shipped code.

---

## What the device must do

1. **Present as USB mass storage** and enumerate as an ordinary stick — same VID/PID/serial for the whole session, so the host never re-scans.
2. **Serve the genuine signed image** during the integrity check. That pass is `ionice -c3 md5sum %1`, i.e. a **full sequential read of the whole file**, plus a `PKCS#1 sig. verify` over the manifest (not the image).
3. **Notice the phase change** and serve **different bytes** to the second, independent open — `pv -q %1 | tar -xvm -C %2` for the system image, `dd if=%1 bs=4k skip=%2` for the others.
4. **Hold both images resident**: the genuine one to pass the check, the attacker one to be installed. For a ~879 MB system image that is ≳2 GB of backing store.

No RSA key is needed at any point: the check runs on genuine bytes.

## Throughput, which is where the board choice actually lies

| Board | USB device link | Realistic MSC rate | One full pass (~879 MB) | Two passes |
| --- | --- | --- | --- | --- |
| **ESP32-S3** | OTG **Full-Speed, 12 Mbit/s** | 0.5–1.2 MB/s | **12–29 min** | **25–60 min** |
| RP2040 / Pico | Full-Speed | 0.5–1 MB/s | 12–29 min | 25–60 min |
| **Pi Zero (dwc2)** | High-Speed, 480 Mbit/s | 20–30 MB/s | ~35 s | **~1.5 min** |

The S3 and the Pico are not incapable — they are **25× slower**, and that difference decides whether the demonstration is an afternoon or a ritual.

Technically the S3 is a good fit for *small*: USB OTG device mode with TinyUSB's MSC class, where the `read10` callback is user code, so "return whatever I want per LBA, per read, per phase" is exactly the thing you are writing anyway. Backing store should be an SD card over **SDMMC 4-bit**, not SPI, so the SD is never the bottleneck — USB Full-Speed will be.

## The two constraints that are not about the microcontroller

**1. Page cache.** `md5sum` reads through the page cache, and **nothing in the FUMO path evicts it**: `AppUpgrade` contains `drop_caches` code, but every reference is `[scomo]`-tagged, and
the `[newota]` (FUMO) strings - the updater this vehicle's launcher row selects - contain **zero** mentions of it. So the second read reaching the device depends on cache pressure, i.e. on
the payload not fitting in RAM. If the file is still cached when the install pass runs, the second read never reaches the device and the swap does nothing — on *any* board. Our extraction of `app/bin/AppUpgrade` contains `umount` and `fsync` but **no `drop_caches`**, so whether the media is genuinely re-read depends on whether the flow unmounts or remounts the stick between check and install. **This is the first thing to instrument on a rig**: watch whether the second pass produces USB traffic at all. If it does not, the vector as described does not work on this build and no amount of gadget engineering changes that.

**2. Update-path timing tolerance.** A 20–60 minute read is not a normal update. Any inactivity watchdog, progress timeout or user prompt in the flow will interrupt it. The upstream field journal is the place to look for how long the real flow tolerated; this repository does not know.

### The payload sizes, from our own package, and why the biggest one is the target

The manifest (`/HU/.lge.upgrade.xml`) and the payloads in our decrypted EU `260128` package give real numbers rather than a cited figure:

| payload | bytes | GiB | Pi Zero HS (~25 MB/s) | ESP32-S3 FS (~0.8 MB/s) |
| --- | --- | --- | --- | --- |
| `HU/images/mango-rootfs.tar.gz` | 879,109,759 | 0.82 | 0.6 min/pass | **18 min/pass** |
| `HU/images/new_gui.tar.gz` | 2,091,925,601 | 1.95 | 1.4 min/pass | **44 min/pass** |
| `HU/images/update.tar.gz` | 42,101,042 | 0.04 | seconds | 0.9 min |
| `HU/images/mango-rwdata.tar.gz` | 16,721,058 | 0.02 | seconds | 0.3 min |

Two things follow.

**The 879 MB figure in the upstream work is confirmed exactly** - `mango-rootfs.tar.gz` is 879,109,759 bytes - which is a useful independent check on their measurements.

**And the cache problem has a practical answer: target the big one.** The page-cache risk is that a payload small enough to stay resident is never re-read from the device. `new_gui.tar.gz` is
**2.09 GB**, which exceeds any plausible head-unit RAM (a Gen5W unit runs on roughly a gigabyte, and our projection boots comfortably in 2 GiB), so its install pass **must** come back to the
medium. A crafted swap of that payload is therefore the version of this attack that does not depend on cache pressure at all.

It also settles the board question in one line: **44 minutes per pass on an ESP32-S3 versus 1.4 minutes on a High-Speed gadget** for the same payload. The S3 is not disqualified, but nobody will
iterate on a two-hour loop.

## Recommendation

- **To reproduce or validate:** a **High-Speed** gadget board — Pi Zero (Linux `g_mass_storage`, two loop images, swap on phase) or any equivalent. Fast enough to iterate, and the phase logic lives on the host side where it is easy.
- **For a small, cheap, covert device:** the ESP32-S3 is genuinely viable — no OS, tiny, cheap — *if* the cache question resolves in favour of media re-reads and the flow tolerates the time. Its advantage is form factor, not capability.

## What would settle it before buying anything

1. Does the update flow unmount or remount the USB volume between the check and the install? (That both drops the cache and gives a clean phase boundary.)
2. What is the longest stall the update progress tolerates?
3. How large is the actual system image in a real package — the throughput maths above scales linearly, and half the size halves the problem.

All three are answerable from the shipped code and the upstream journal, without hardware.
