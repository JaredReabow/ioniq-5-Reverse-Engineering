# Stock BusyBox unzip bounds checkpoint

Date: 2026-11-01

## Completed

- Corrected artifact provenance after independent review. The current
  `extracted-safe/.../bin/busybox` is a VM-injected static helper hard-linked to
  `work/vm/busybox`; it is not stock firmware.
- Bound stock `/usr/bin/unzip -> /bin/busybox` to canonical original bytes:
  SHA-256 `95bab633630fb158344497af52dc112e9e777458b810860068d4daa257bd9ebc`,
  two GNU Build ID notes `42e0a4c7631667cf9106ca36a4f2e7886f6f72b0` and
  `dc25533aa5ad984ec9a7ed388925f24d328c1836`, BusyBox 1.23.2.
- Confirmed stock `unzip` accepts only methods 0 and 8 at
  `0x45da8..0x45dbe`; method 12 is rejected.
- Confirmed method 8 reaches exact pre-fix CVE-2015-9261 `huft_build`:
  recovered code compares the cursor with `v+n` at `0x4788a`, then can read an
  uninitialized `v[]` entry at `0x47938` and use it for indexed reads at
  `0x47970`/`0x47974`. The initial `v_end` fix was corrected four days later by
  stable `UINT_MAX` sentinel initialization; neither correction is present.
- Confirmed AppScomoDM decompresses the selected two members before invoking its
  public-key-backed verifier for each.
- Corrected archive selection: helper `0xb8a10` examines one first iterator
  result only; it does not loop or choose the last result.
- Added a pure numeric model of recovered `v+n`, a conceptual populated-prefix
  count, and the stable `UINT_MAX` sentinel correction. It does not model the
  short-lived `v_end` implementation as exact fixed behavior.
- Extended the passive bench collector for stock/update identities, symlink
  metadata, selected process arguments, and allowlisted process `PATH` capture.

## Safety record

No recovered executable was run. No malformed ZIP/DEFLATE stream, package,
payload, shellcode, packet, or heap-grooming input was created. No VM, rootfs,
partition, slot, marker, or original firmware file was modified or deleted.
Public-source clones and generated JSON remain ignored under `work/`.

## Remaining

1. Complete independent re-review after all provenance and model corrections.
2. On a disconnected owner-controlled bench, capture installed BusyBox and
   AppScomoDM hashes, `/usr/bin/unzip` link target, effective `PATH`, selected
   route, uid, and SMACK label before any active test.
3. Treat any future malformed-stream validation as crash-only in a disposable
   sanitizer/vendor environment; do not place it on the owner unit.
4. Continue child-updater version/model/signature/write/slot/boot/health analysis
   independently. CVE-2015-9261 does not bypass those controls.

## Verification

```sh
python3 -m pytest -q tests/test_busybox_huft_bounds_model.py
python3 -m pytest -q tests
git diff --check
```
