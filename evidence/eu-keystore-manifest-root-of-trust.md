# Keystore root of trust: `.manifest_keyring` and the `oemkm` parameter

Status: static analysis of the exact EU `260128` kernel with corrected symbols
(64,923 recovered, cross-validated against `__ksymtab`). All findings are from
Ghidra decompilation of specific addresses, with instruction-level checks where
a construct looked suspicious.

## The boot-time chain

`manifest_init` (`0xffffffff81b1ddd2`, an initcall) runs at boot:

1. `get_apl_manifest_offsets(&size, &phys)` scans the kernel parameter list for a
   parameter named **`oemkm`** and parses its value with `sscanf("%x@%x")` —
   i.e. the form `oemkm=<size>@<physical-address>`.
2. Bounds-check the size (`1 .. 0x3ffffff`, 64 MiB).
3. `__kmalloc(size)` then `memcpy_from_ph(dest, phys, size)` — a direct copy out
   of physical memory through the direct map.
4. Validate a small header: word 0 must equal `0xe`; the byte at `+0x13` and
   words 5 and 6 must be zero.
5. Walk up to **101** entries, where each entry's stride comes from a `u16` at
   `entry + 0x22`, and record each entry pointer in
   `key_manifest_extension_data`.
6. `prepare_kernel_cred(0)` → **root credentials**, then
   `keyring_alloc(".manifest_keyring", 0, 0, cred, 0x1f0f0000, 2)`.
7. Store the keyring in the BSS global `manifest_keyring` and keep the cred in
   `manifest_keyring_cred`.

`get_apl_manifest_offsets` (`0xffffffff8105986e`) is explicit: it iterates
`params_list`, `strcmp`s against the literal `"oemkm"`, and requires exactly two
hex conversions. If the parameter is absent it returns `-0x3d` (ENODATA) and no
keyring is created.

## The parameter is not in the package

`oemkm=` does **not** appear in any of the six packaged command lines (verified by
scanning the first 1200 bytes of each `iasImage*_sub`). It is therefore appended
by the boot loader, which also places the manifest in physical memory. The
packaged command line and the trust root are supplied by two different stages.

## Consumers

- `manifest_key_verify_digest` → `keyring_search(manifest_keyring, …)`.
- `verify_x509_cert_against_manifest_keyring` →
  `x509_request_asymmetric_key(manifest_keyring, description, 0)`.
- Both then locate `bin2hex("OEMKEY")` inside the key description, parse 16 bytes
  of usage bits at `+0xc`, and call `check_usage_bits`.
- `check_usage_bits(requested, allowed)` is a clean subset test over four 32-bit
  words: `requested[i] == (allowed[i] & requested[i])`. A key with an all-ones
  mask authorises every usage; a restrictive mask does not.

So the OEM public key is **not** in the root filesystem and **not** in the kernel
image. It lives in a firmware-provided physical-memory region, and only the
location is passed to the kernel.

## Assessment

Strengths:

- The key material is outside the writable filesystem, so gaining root on the
  rootfs does **not** let an attacker substitute the OEM key. This is a
  meaningful hardening choice.
- The keyring is created with root credentials at boot, and lookups require an
  asymmetric key with both validate and verify operations.
- Usage bits restrict what a key may be used for, subject to the mask baked into
  the manifest.

Design observation worth recording:

- The root of trust is a **command-line-supplied physical address** whose
  contents are trusted implicitly. `manifest_init` validates only a tiny header
  (type word, three zero fields). The manifest blob itself is not signed or
  measured, so *anything* at that address that parses becomes the trusted key
  set.
- Consequence: whoever controls the `oemkm=` parameter controls the OEM keyring.
  Under the stock boot chain that is the boot loader, which is not attacker
  controlled. But the parameter is a single injection point, and it is not
  covered by the `ipk.` container signature (the container's command line does
  not contain it; the loader adds it afterwards).
- `CONFIG_KEXEC=y` is present. Post-root, `kexec` can boot a kernel with an
  arbitrary `oemkm=` pointing at a prepared page, which would install a
  substituted keyring for that boot. This requires `CAP_SYS_BOOT` and honours
  `kexec_load_disabled`, and it does not survive a cold boot. It is a research
  direction, not a persistence mechanism.

## What this means for custom firmware

1. **Root on the rootfs does not grant signing capability.** The OEM private key
   is not on the device; the public key is pinned in firmware memory; the
   rootfs holds neither.
2. **Signature bypass must therefore be a userland decision**, which is exactly
   what CVE-2023-26244/26245/26246 describe (`AppDMClient`, `AppUpgrade`), and
   what `update-patcher` implements.
3. **The `oemkm=` parameter is the highest-leverage single point** if the boot
   loader can be influenced at all. It is the only place where the trusted key
   set is chosen, and the choice is a plain-text command-line value.
4. Persistence after a clean boot still requires either patching the installed
   rootfs (and surviving official updates) or modifying a signed boot stage.

## Open questions

- Does the boot loader permit additional or overriding `oemkm=` values, and how
  does it order them against the packaged command line?
- Is the physical region holding the manifest protected by the firmware
  descriptor / lock registers, or is it merely conventional memory?
- What usage-bit mask does the shipped OEM key actually carry? With an all-ones
  mask, any consumer may use it for any purpose.
- Is `kexec_load_disabled` set by the installed userspace?

## Reproducible artifacts

Decompiled functions under `work/eu-260128/decomp/decompiled/`:
`manifest_init`, `get_apl_manifest_offsets`, `memcpy_from_ph`,
`manifest_key_verify_digest`, `verify_x509_cert_against_manifest_keyring`,
`check_usage_bits`, `keystore_backup`, `keystore_get_ksm_key`, `keystore_ioctl`.
