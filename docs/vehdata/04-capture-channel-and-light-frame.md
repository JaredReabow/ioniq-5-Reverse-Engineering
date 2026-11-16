# Getting frames off the guest losslessly, and what the first real frames show

Date: 2026-11-05.

## The channel, and the two traps it exposed

The console cannot carry a capture: base64 over a mixed console corrupted at 174,117 characters for a
129 KB PNG. Writing the PNG to `/log_data` did not work either - **guest writes never persist**, the disk is
mounted `snapshot=on`, so the file is gone when QEMU exits.

What works: a **second file-backed serial device** (`-chardev file,...,index=3`, guest `/dev/ttyS3`),
declared in `tools/uk_fw/vm_partimg/run-byhand.py`, with the PNG sent as **base64 with no newlines**.
Five frames decoded byte-exact from a 502,407-byte channel file.

**Trap 1, and it is the interesting one:** sending the PNG **raw** over that channel corrupted it, because
the line discipline rewrites `\n` (0x0A) to `\r\n`. The PNG magic came out as
`89504e47 0d0d0a 1a0d0a` instead of `89504e47 0d0a1a0a`. **A serial channel is a text channel unless you
turn the translation off**, and base64 sidesteps it because base64 contains no 0x0A.

**Trap 2:** `dmesg` is not where an instrument that writes to `/dev/ttyS2` leaves its output.

## What the frames show

With the CAN shim preloaded, the app powered on - and the theme switched to **light**, which is the
day-theme the laid-out home screen uses:

| surface | bytes | what it is |
|---|---|---|
| 2080, 1001, 1000 | 120,561 | the **standby** face (dark, KIA logo) |
| **1004, 1003** | **7,510** | a **light frame with a single placeholder glyph and no widgets** |

So **`set_power_on_status` took effect** (the theme switched) but **the home layout did not complete** in
this run. That is not the earlier "16,062-byte laid-out home screen", and it is not the standby frame either.

## The two candidate explanations, and how to separate them

1. **Timing.** The captures happen ~32 s after the power-on call. The earlier successful layout was seen
   later in its run. Cheap to test: capture again at +90 s.
2. **The shim itself.** It opened **81** `PF_CAN` sockets in that run, each with a feeder thread writing
   every 2 s. If the application blocks or retries on those, the layout may never settle. Cheap to test:
   run **without** `/etc/ld.so.preload` and compare the same surfaces at the same timestamps.

**Not established:** that the shim lets the layout settle, or that it prevents it. The channel that will
answer it now works, which is why this note exists.
