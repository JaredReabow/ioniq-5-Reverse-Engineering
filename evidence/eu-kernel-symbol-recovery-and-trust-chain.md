# European `260128` kernel: symbol recovery and trust-chain anatomy

Status: static analysis of the plaintext boot payload in the official EU package.
No device was used, no firmware was executed, and no encrypted payload was
decrypted (the key is not present in the package).

## 1. Kallsyms recovery was broken, and is now fixed

The committed `tools/uk_fw/kallsyms_extract.py` fails on this exact kernel with
`names stream overran at symbol 36946`. Three defects were identified and fixed
in `tools/uk_fw/kallsyms_structural.py`:

| # | Defect | Effect | Fix |
|---|---|---|---|
| 1 | `kallsyms_num_syms` chosen as the first in-range `u32` in a 1.5 MB window | selected 64,768 instead of 64,923 | use the trailing kernel-pointer run end, then read the count field there |
| 2 | markers assumed to start at an odd address | array decoded at `0x9dedc7` instead of `0x9dedc8` | search for an 8-aligned monotonic `u64` array |
| 3 | address array start taken at the first *kernel-range* pointer | starts 204 entries late, because leading absolute (`A`) symbols hold small values | derive start as `num_syms_off − count × 8` |

Defect 3 is the serious one: it silently mispaired **every** symbol with an
address 204 entries away. Prologues still looked plausible, so the error was
invisible without an independent cross-check.

### Verification

`__ksymtab` is independent of `kallsyms`. Parsing 4,375 exported symbols
(`struct kernel_symbol`, 16-byte absolute form) and comparing each exported
address to the recovered table gives:

- **4,369 / 4,375 exact address-and-index matches**
- **0 residual mismatches**
- 6 entries with a ±1 duplicate-name ambiguity only

Corrected layout:

```
kallsyms_addresses   0x89f158   (64,923 × u64)
kallsyms_num_syms    0x91de30   = 64923
kallsyms_names       0x91de38   (790,415 bytes, 12.17 B/symbol)
kallsyms_markers     0x9dedc8   (254 × u64)
kallsyms_token_table 0x9df5b8
kallsyms_token_index 0x9df940
```

### Consequence for earlier work

Because defect 3 is silent, any prior Ghidra naming derived from a
run-start-based extraction should be treated as **unverified** and re-derived.
This session re-imported the kernel and re-applied the corrected table
(25,033 functions renamed, 41 priority functions decompiled). Findings below are
from that corrected run.

## 2. Trust chain: the kernel verifies *manifests*, not firmware

`verify_oem_signature(data, len, sig, siglen)`:

1. rejects null arguments (`-EFAULT`);
2. `keystore_sha256_block()` → 32-byte SHA-256 digest;
3. `keystore_hexdump("Digest", …)` and `keystore_hexdump("Signature", …)`
   under dynamic-debug control;
4. `manifest_key_verify_digest(digest, 32, sig, siglen,
   "OEM: Keystore: <hex>", 0x2f)`.

`manifest_key_verify_digest`:

1. derives an index from the usage bits (`usage >> 5`, must be < 4) and sets a
   single bit at `usage & 0x1f`;
2. `keyring_search(manifest_keyring, &key_type_asymmetric, description)`;
3. requires an asymmetric key with both validate and verify operations;
4. `bin2hex("OEMKEY")` → `strstr` in the key description → `hex2bin` 16 bytes at
   `+0xc` → `check_usage_bits()` against the requested bit;
5. `mpi_read_raw_data(signature)` → `verify_signature(key, …)`, which invokes
   the asymmetric verify op at `key->type+0x28`.

**Reachability:** `verify_oem_signature` is called only by `keystore_backup`
and `keystore_generate_mkey`. It is **not exported**. Therefore:

> Firmware/update trust is decided in **userland** (`AppUpgrade`,
> `AppDMClient`, `.lge.upgrade.xml` handling). The kernel keystore supplies
> primitives and protects key backup/migration, and is not the place where a
> modified update package is accepted or rejected.

This is consistent with CVE-2023-26244/26245/26246, which target userland
binaries, and it explains why no kernel signature bypass would be required.

### Usage-bit enforcement

The key description carries a 16-byte usage-bits field parsed by `hex2bin`.
A key authorises a requested usage only if `check_usage_bits` passes. Whether
the shipped OEM key uses a permissive mask (e.g. all-ones) is not determinable
from the package: the manifest keyring and its descriptions live in the
encrypted rootfs.

## 3. Keystore ioctl surface

`/dev/keystore` exposes 26 ioctls (`_IOC_TYPE 0x37`), including
`REGISTER`, `GENERATE_KEY`, `WRAP_KEY`, `LOAD_KEY`, `UNLOAD_KEY`,
`ENCRYPT`/`DECRYPT` (+`_SIZE`), `SIGN`/`VERIFY`, `PUBKEY`, `BACKUP`,
`GEN_MKEY`, `MIGRATE`, `UNWRAP_WITH_BACKUP`, `REWRAP`, `GET_KSM_KEY`, and
`RUN_TESTS`.

Boundary review of `keystore_ioctl`:

- declared size is gated at `size < 0x319` (792) against a 0x318-byte stack
  region ending at the canary — the copy fits exactly;
- the user pointer is overflow-checked (`CARRY8(param_3, size)`) and only then
  handed to `copy_from_user`, with an `access_ok`-style limit comparison for
  negative (read) request numbers;
- handlers that allocate use the same variable for `kmalloc` size and copy
  length (`0x412037c9`, `0xc0183706`, `0xc15837cb`), so no length/alloc
  mismatch is present on those paths;
- the 0x318-byte staging buffer is zeroed after each dispatch.

A hypothesis that the 288-byte `TEST_VERIFY_ECC_SIGNATURE` request left its
tail fields uninitialised was tested and **rejected**: decoded size is `0x120`,
which covers offsets 0x88–0x94 that the handler reads.

Not found: a memory-safety defect in the reviewed set. This is a bounded
negative result over 41 decompiled functions, not a proof of absence.

### Access control

`keystore_open` performs only `nonseekable_open()` — no capability check.
Access therefore depends entirely on the device node's mode and SMACK label in
the encrypted rootfs. Exported for module use: `keystore_verify`,
`keystore_register` (4,375 total exports).

## 4. Reachable built-in surface

| Subsystem | Symbols | Notes |
|---|---|---|
| netfilter / xtables | 1,610 | full iptables, NAT, conntrack |
| TCP | 588 | |
| IPv6 | 525 | |
| CAN | 306 | `RAW`, `BCM`, `GW`; plus `micom_*` (24) |
| UDP | 161 | |
| keystore | 129 | trust primitives |
| lge_* | 93 | i2c, GPIO, touch, eMMC, LCD, meminfo |
| portmux | 14 | Intel DRCFG USB role mux |

Modules (in the encrypted rootfs, not covered): `usb_f_iap2`, `usb_f_mass_storage`,
`gadgetfs`, `vfat`, `cfg80211`, `usb_storage`, `usb_dwc3`. No `exfat` and no
`fuse` in the kernel configuration.

## 5. What remains blocked

Everything in the update path that actually parses attacker-supplied packages —
`AppUpgrade`, `AppDMClient`, `.lge.upgrade.xml`, `update.tar.gz`, `appnavi.tar`,
`new_gui.tar.gz` — is AES-encrypted with entropy 8.00 and no offline break.
Static analysis of those components requires the unit-derived key.

The kernel is therefore **analysable but not the weak link**; the exploitable
surface for the stated goals is in the encrypted userland.

## 6. Reproducible artifacts

```
work/eu-260128/vmlinux              sha256 f5ee9c2f…6b102b
work/eu-260128/kernel.config        4,238 lines
work/eu-260128/kallsyms.tsv         64,923 symbols (address, type, name)
work/eu-260128/kallsyms_apply.tsv   Ghidra format
work/eu-260128/kallsyms_layout.json
work/eu-260128/decomp/              41 decompiled functions + call graph
```
