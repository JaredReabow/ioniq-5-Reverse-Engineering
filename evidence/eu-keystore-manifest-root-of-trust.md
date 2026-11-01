# Keystore root of trust: `.manifest_keyring` and the `ABL.oemkm` handoff

Status: static analysis of the exact EU `260128` kernel with corrected symbols
(64,923 recovered, cross-validated against `__ksymtab`). All findings are from
Ghidra decompilation of specific addresses, with instruction-level checks where
a construct looked suspicious.

## The boot-time chain

`manifest_init` (`0xffffffff81b1ddd2`, an initcall) runs at boot:

1. `get_apl_manifest_offsets(&size, &phys)` scans the ABL parameter list for an
   internal entry named **`oemkm`** and parses its value with
   `sscanf("%x@%x")`. The public matching source registers that list through
   `__setup("ABL.", setup_abl_params)`, so the full kernel-command-line form is
   `ABL.oemkm=<size>@<physical-address>`, not bare `oemkm=`.
   <!-- disagreement: the parallel repository recorded the parameter as bare `oemkm=` (`oemkm=<size>@<physical-address>`) against the same address and the same `strcmp("oemkm")`. Both forms are preserved; adjudication needs the `__setup` expansion confirmed against the exact image. -->
2. Bounds-check the size using `size - 1 <= 0x3ffffff`, accepting
   `1 .. 0x4000000` bytes inclusive (64 MiB).
   <!-- disagreement: the parallel repository stated the accepted range as `1 .. 0x3ffffff` (64 MiB); this analysis derives `1 .. 0x4000000` inclusive from `size - 1 <= 0x3ffffff`. Both bounds are preserved. -->
3. `__kmalloc(size)` then `memcpy_from_ph(dest, phys, size)` — a direct copy out
   of physical memory through the direct map.
4. Validate a small header: word 0 must equal `0xe`; the byte at `+0x13` and
   words 5 and 6 must be zero.
5. Walk up to **101** entries, where each entry's stride comes from a `u16` at
   `entry + 0x22`, and record each entry pointer in
   `key_manifest_extension_data`. The internal declared length is not checked
   against the copied allocation; see `eu-keystore-secure-boot-ignore.md` for
   the exact conditional out-of-bounds-read classification.
6. `prepare_kernel_cred(0)` → **root credentials**, then
   `keyring_alloc(".manifest_keyring", 0, 0, cred, 0x1f0f0000, 2)`.
7. Store the keyring in the BSS global `manifest_keyring` and keep the cred in
   `manifest_keyring_cred`.

`get_apl_manifest_offsets` (`0xffffffff8105986e`) is explicit: it iterates
`params_list`, `strcmp`s against the internal literal `"oemkm"`, and requires
exactly two hex conversions. Public source at vendor commit
`0c9640bba6a841f524f5947d0741386792674577` supplies the missing registration
context: `__setup("ABL.", setup_abl_params)`. If the ABL parameter is absent the
function returns `-0x3d` (ENODATA) and no keyring is created.

## The parameter is not in the package

`ABL.oemkm=` does **not** appear in any of the six packaged command lines
(verified by scanning the first 1200 bytes of each `iasImage*_sub`). It is
therefore appended by the boot loader, which also places the manifest in
physical memory. The packaged command line and the trust root are supplied by
two different stages.

## Consumers

- `manifest_key_verify_digest` → `keyring_search(manifest_keyring, …)`.
- `verify_x509_cert_against_manifest_keyring` →
  `x509_request_asymmetric_key(manifest_keyring, description, 0)`.
- Both then locate `bin2hex("OEMKEY")` inside the key description, parse 16 bytes
  of usage bits at `+0xc`, and call `check_usage_bits`.
- `check_usage_bits(requested, allowed)` is a clean subset test over four 32-bit
  words: `requested[i] == (allowed[i] & requested[i])`. A key with an all-ones
  mask authorises every usage; a restrictive mask does not.

<!-- disagreement: the parallel repository concluded from the same code that "the OEM public key is not in the root filesystem and not in the kernel image" and that "anything at that address that parses becomes the trusted key set", whereas this analysis finds only that the manifest supplies digest/usage policy and that absent certificate bytes are not proven. Both readings are retained in full. -->

The boot manifest does not directly populate the keyring with certificate
objects. Matching public source shows that it carries public-key hashes and
usage permissions; a self-signed X.509 certificate is admitted as trusted only
after its self-signature verifies and its public-key digest/usages match the
manifest. Delegated certificates must verify under an already admitted parent
and use a subset of its usage bits. The source of the certificate objects is a
separate runtime question.

Thus the OEM **trust policy** is not in the packaged kernel command line or
ordinary rootfs configuration: the bootloader supplies the manifest's physical
location. This does not by itself prove that every certificate byte is absent
from the filesystem.

## Scope of `CONFIG_KEYSTORE_SECURE_BOOT_IGNORE`

The exact `keystore_init` instructions show that this option skips a
secure-boot-**status prerequisite** before seed filling. It does not remove the
separate `manifest_init` initcall or the SHA-256 → manifest-key signature
verifier chain. The option is therefore not a general package, update, or boot
signature bypass. See `eu-keystore-secure-boot-ignore.md`.

## Assessment

Strengths:

- At kernel initialization the public-key digest/usage allowlist arrives through
  a bootloader-populated DRAM handoff rather than an ordinary rootfs pathname.
  Its source of record and storage protection are unknown. Gaining root after
  this copy does **not** by itself rewrite the retained policy without a separate
  kernel-memory or reboot-handoff primitive.
  <!-- disagreement: the parallel repository stated this more strongly — that the key material sitting outside the writable filesystem means root on the rootfs does not let an attacker substitute the OEM key at all, and called that a meaningful hardening choice. This analysis stops at "does not by itself rewrite the retained policy". Both are preserved. -->
- The keyring is created with root credentials at boot, and lookups require an
  asymmetric key with both validate and verify operations.
- Usage bits restrict what a key may be used for, subject to the mask baked into
  the manifest.

Design observation worth recording:

- The root policy input is a **command-line-supplied physical address** whose
  contents are trusted implicitly. `manifest_init` validates only a tiny header
  (type word, three zero fields). The manifest blob itself is not authenticated
  on this path, so a blob that parses can choose the public-key digests and usage
  masks against which later certificate admission is decided. It does not
  automatically insert a certificate object into `.manifest_keyring`.
- Consequence: whoever controls the `ABL.oemkm=` parameter and corresponding
  physical-memory handoff controls the manifest trust input.
  Under the stock boot chain that is the boot loader, which is not attacker
  controlled. But the parameter is a single injection point, and it is not
  covered by the `ipk.` container signature (the container's command line does
  not contain it; the loader adds it afterwards).
- `CONFIG_KEXEC=y` is present. Post-root, `kexec` can boot a kernel with an
  arbitrary `ABL.oemkm=` pointing at a prepared page, which could substitute
  the manifest trust input and, subject to certificate-admission rules, the
  substituted keyring for that boot. This requires `CAP_SYS_BOOT` and honours
  `kexec_load_disabled`, and it does not survive a cold boot. It is a research
  direction, not a persistence mechanism.

## What this means for custom firmware

1. **Root on the rootfs does not grant signing capability.** The OEM private key
   is not recovered from the device. The public-key digest/usage policy is
   supplied through firmware memory, and a substitute certificate still needs
   admission to the trusted-only manifest keyring.
2. **The currently demonstrated modified-package bypass is a userland
   decision**, which is what CVE-2023-26244/26245/26246 describe
   (`AppDMClient`, `AppUpgrade`) and what `update-patcher` implements. This does
   not exclude separate loader/handoff or boot-stage defects.
3. **The `ABL.oemkm=` parameter is the highest-leverage single point** if the boot
   loader can be influenced at all. It chooses the manifest policy input through
   a plain-text command-line location; successful substitution still requires a
   corresponding physical-memory blob and a certificate-admission path.
4. Persistence after a clean boot still requires either patching the installed
   rootfs (and surviving official updates) or modifying a signed boot stage.

## Open questions

- Does the boot loader permit additional or overriding `ABL.oemkm=` values, and how
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

#### From the parallel repository

##### # Keystore root of trust: `.manifest_keyring` and the `oemkm` parameter

The parallel copy titled this document as above rather than `... and the `ABL.oemkm` handoff`, and described the same recovered functions with the following wording and claims. None of it is deleted here; where it conflicts with the corrected analysis above, an inline `<!-- disagreement: ... -->` marker names the conflict.

##### Boot-time chain (parallel wording)

`get_apl_manifest_offsets(&size, &phys)` scans the kernel parameter list for a parameter named **`oemkm`** and parses its value with `sscanf("%x@%x")` — i.e. the form `oemkm=<size>@<physical-address>`.

Bounds-check the size (`1 .. 0x3ffffff`, 64 MiB).

`get_apl_manifest_offsets` (`0xffffffff8105986e`) is explicit: it iterates `params_list`, `strcmp`s against the literal `"oemkm"`, and requires exactly two hex conversions. If the parameter is absent it returns `-0x3d` (ENODATA) and no keyring is created.

##### Where the key material lives (parallel wording)

So the OEM public key is **not** in the root filesystem and **not** in the kernel image. It lives in a firmware-provided physical-memory region, and only the location is passed to the kernel.

##### Assessment (parallel wording)

- The key material is outside the writable filesystem, so gaining root on the rootfs does **not** let an attacker substitute the OEM key. This is a meaningful hardening choice.
- Usage bits restrict what a key may be used for, subject to the mask baked into the manifest.

##### Design observation (parallel wording)

- The root of trust is a **command-line-supplied physical address** whose contents are trusted implicitly. `manifest_init` validates only a tiny header (type word, three zero fields). The manifest blob itself is not signed or measured, so *anything* at that address that parses becomes the trusted key set.
- Consequence: whoever controls the `oemkm=` parameter controls the OEM keyring. Under the stock boot chain that is the boot loader, which is not attacker controlled. But the parameter is a single injection point, and it is not covered by the `ipk.` container signature (the container's command line does not contain it; the loader adds it afterwards).
- `CONFIG_KEXEC=y` is present. Post-root, `kexec` can boot a kernel with an arbitrary `oemkm=` pointing at a prepared page, which would install a substituted keyring for that boot. This requires `CAP_SYS_BOOT` and honours `kexec_load_disabled`, and it does not survive a cold boot. It is a research direction, not a persistence mechanism.

##### What this means for custom firmware (parallel wording)

1. **Root on the rootfs does not grant signing capability.** The OEM private key is not on the device; the public key is pinned in firmware memory; the rootfs holds neither.
2. **Signature bypass must therefore be a userland decision**, which is exactly what CVE-2023-26244/26245/26246 describe (`AppDMClient`, `AppUpgrade`), and what `update-patcher` implements.
3. **The `oemkm=` parameter is the highest-leverage single point** if the boot loader can be influenced at all. It is the only place where the trusted key set is chosen, and the choice is a plain-text command-line value.
4. Persistence after a clean boot still requires either patching the installed rootfs (and surviving official updates) or modifying a signed boot stage.

##### Open questions and artifacts (parallel wording)

The parallel copy carried the same four open questions (overriding `oemkm=`, firmware-descriptor protection of the manifest region, the shipped usage-bit mask, and `kexec_load_disabled`) and the same decompiled-function artifact list.
