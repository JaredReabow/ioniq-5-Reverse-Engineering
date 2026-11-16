# Evidence

Confidence tags: **[LOG]** the car's own logs · **[RE]** decompiled/strings from the real
binary · **[NATIVE]** genuine binaries executed · **[INFER]** reasoned.

## From the real binary (`appupg_engine.so`) — [RE]
- The `.rodata` contains the **separate** shell templates: `ionice -c3 md5sum %1 | awk`
  (check) and `/app/share/AppUpgrade/DecryptToPIPE %1 | tar -xvm -C %2` + `dd if=%1 …`
  (install). Separate `system()`/`popen()` → separate `open("%1")`s.
- The RSA step is `PKCS#1 sig. verify`, signature type `md5WithRSAEncryption` (RSA over an
  MD5 digest).

## From the car's own DLT / upgrade logs — [LOG]
- The system rootfs source is `/media/usb/.../HU/images/mango-rootfs.tar.gz`, **processed
  in place** — only the ~6 MB boot images are copied to `/tmp`.
- **No system-partition re-hash after write:** post-install "verify" is source-side
  (`RB_FS_navi_verify` reads the *source* `navi_deltapath`); "System Update Verify" = **46
  ms** vs navi map verify = **336 s**. 46 ms cannot hash an 879 MB partition.
- Three completed same-version firmware updates each ended `[USB-UPDATE] SWAP FINISH`
  (A/B swap applied) — the update type that reaches the rootfs does complete the swap.
- `collectUSBPartitionImages: update source is encrypt file: mango-rootfs.tar.gz` — the
  HU engine recognizes the rootfs as a real install target of the same-version update.

## From native / VM execution — [NATIVE]
The Gen5W_L HU is **Intel x86-64** (rootfs loader `ld-linux-x86-64.so.2`; kernel
`iasImage` → `bzImage 4.1.27-abl`), so the real HU binaries run natively on a PC.

- **Two-open TOCTOU, real binaries:** the genuine x86-64 `DecryptToPIPE` (via the HU's own
  `ld-2.25.so` + `libssl/libcrypto 1.0.2`) and real `md5sum` were run against a file swapped
  genuine→evil between the two opens. Verify accepted genuine (`md5 7f510002…` = signed);
  install re-read consumed EVIL (`DTP stream f83bdd… ≠ genuine 1bea17…`), which decrypts to
  the patched rootfs. `DecryptToPIPE` argv = `-d <keyfile> <input> 0`; the key arg must be an
  existing readable file (contents irrelevant) — a missing path yields a different stream.
  No re-hash of the installed stream. (Bench harness not included in this repo — see note below.)
- **Genuine OS boots on the real kernel** (Tiers A/B): the decrypted `mango-rootfs` boots to
  a genuine `systemd 225` + SMACK + D-Bus multi-user under `qemu-system-x86_64`. The genuine
  `AppUpgrade` updater runs true-to-life (decrypt, headless Qt, SMACK label, A/B active-set
  via `root=mmcblk0p3`, disk prechecks, dbus connect) up to the vendor D-Bus service
  ecosystem (automount/micom/app-manager) and the GPU-gated HMI — an architectural wall in
  CPU-only emulation (Mesa ships only the i965 Intel DRI, no software rasterizer). The
  re-read **behavior** is already proven byte-exact by the native run above; the full
  orchestrator sequencing needs the real GPU / the car.

## The byte-exact evil envelope — [NATIVE]
A real malicious `mango-rootfs.tar.gz` can be built that is byte-size- and IV-identical to
the genuine signed envelope (so it occupies the same USB extent and decrypts on the unit):
genuine decrypt → inject `wideopen.service` → recompress → pad → TE2-encrypt. Identical
envelope size (879,126,179), body (879,109,759), IV (derived from basename
`mango-rootfs.tar.gz`), TE2 metadata valid. Size-fit gotcha: the OEM packs tighter than
`gzip -9`; **libdeflate L10** (concatenated gzip members) fits with ~18.7 MiB headroom.

## Honest residual
- The exact RSA `signFileVerify` coverage for the *system* image is confirmed only to the
  "separate re-open" level, not pinned to one decompiled instruction (virtual dispatch).
- "Persistent root on the device" is demonstrated as a **mechanism** (native two-open race +
  no post-write verify + no dm-verity), not yet as a completed on-car install — see the
  field journal for the operational state.

## Note on the bench harness
The native two-open validation (real x86-64 `DecryptToPIPE` + `md5sum` against a
genuine→evil swapped file) and the genuine-OS boot tiers were run on an x86-64 bench, not a
Pi. Those exploratory harnesses are not part of this reproduction repo. The same real
`DecryptToPIPE` path is exercised by `pizero/preflight.py` **check C**, which runs
automatically on an x86-64 host (and auto-skips on the ARM Pi).
