# Chimaera technique: analysis of the open-access primary source

Source: Costantino, Matteucci et al., *"A vehicle firmware security vulnerability:
an IVI exploitation"*, Journal of Computer Virology and Hacking Techniques 20(4),
681–696 (2024), DOI `10.1007/s11416-024-00522-4`. Open Access (hybrid).
Subject build: `AE_E_PE_EUR.S5W_L001.001.211214`.

This note summarises the published technique and reconciles it with this
programme's independent ciphertext measurements. It contains no exploit code.

## The finding in one line

`DecryptToPIPE` statically links **mbedtls**, which leaves an unused
`mbedtls_printf("Unexpected error, return code = %08X")` reachable by patching.
Patching the binary to print the register that holds the key material leaks the
**AES-CBC-128 key**; the authors then reproduce the key-unwrapping and IV
derivation in C and decrypt any package offline.

## Published phases

1. **Firmware structure analysis.** Download the official package, identify
   hidden files, and recover "the decrypted files … using a 'public' RSA key".
2. **Reverse engineering `DecryptToPIPE` (I).** The start function calls three
   functions, renamed `RSA_decrypt_and_AES_key`, an allocator, and
   `AES_and_SHA`. `RSA_decrypt_and_AES_key` reads a **`Key_file`** containing the
   RSA public key and the encrypted AES key.
3. **Key extraction.** Inject assembly at a point after the target value to make
   the dormant `mbedtls_printf` print registers; the injected code frequently
   segfaults, which is tolerated because the value is read first. Then, in C,
   reproduce the read of the public key and the encrypted AES key, apply the
   mbedtls RSA operation with the published `n` and `e`, and print the
   **AES-CBC-128** key.
4. **Crypto reproduction.** Compute SHA-256 per file, discover the **IV
   generation algorithm**, and reproduce both `encrypt` and `decrypt`.
5. **File-structure analysis.** Each firmware file is described as *content + a
   terminator string + a SHA + a digital signature*. This is what makes it
   possible to modify content and repack it.
6. **Bypass.** Patch `AppDMClient`, `AppUpgrade` and `DecryptToPIPE` to skip
   digital-signature checks, then install the modified firmware.
7. **Post-exploitation.** Remote command injection affecting M-, B- and C-CAN;
   requires a 1-day (AppNavi) entry or the custom firmware.

The authors state the entry precondition explicitly: the chain works "only
leveraging 1-Day exploit (AppNavi) or using our custom firmware".

## What this changes

**The encryption is AES-CBC-128, not AES-256.** Our entropy and block analysis
is consistent with this; it does not distinguish key size, but the published
figure settles it.

**The key is recoverable with public material plus one device file.** The
published unwrap uses the RSA **public** key (`n`, `e`) to recover the AES key.
That means the confidentiality of the OTA package rests on the `Key_file` being
kept on the device, not on any secret held by the verifier. Practically:

- Copying `DecryptToPIPE` **and** the `Key_file`/`.der` material off a unit is
  sufficient for complete offline decryption — no further reverse engineering is
  required.
- The blob we identified as `decryption_key.der` is therefore likely the
  *public* half plus the wrapped AES key, which is why the public toolchain only
  asks for that file pair.

**The IV is derived, not random.** This matches our observation that the
14,059-byte footer is byte-identical across three files in one package and
completely different between packages: a deterministic IV over a
package-constant plaintext produces exactly that pattern.

## A tension with our own measurement

The paper says each file carries *content + terminator + SHA + signature*. If the
SHA were per-file and lived in the trailing block, trailing blocks would differ
between files. We measured the opposite: `AppUpgrade`, `.lge.upgrade.xml` and
`update.tar.gz` share an **identical 14,059-byte tail**, and `.lge.upgrade.xml`
is only 3,611 bytes of content.

Two readings remain open:

1. The shared tail is a **package-level** certificate/signature blob, and the
   per-file SHA sits just before it inside the "content" region (so it is
   encrypted and therefore invisible to us).
2. The published description is approximate, and the shared tail is the
   per-package descriptor rather than per-file metadata.

Either way there is no contradiction in practice: per-file SHA is computed over
the file's content, encrypted inside the file, and the package-level blob is
appended verbatim. Deciding between the readings needs one decrypted package.

## Consequences for this programme

- The "cryptographic wall" is not a wall on the device: it is a wall on
  *access to two files*. Everything else is documented and reproducible.
- The entry problem is unchanged and is the real bottleneck: obtaining those
  files requires code execution on the unit first, and the public entry
  (`navi_extended` via AppNavi) needs an unpatched build.
- Once `DecryptToPIPE` and the key file exist, `tools/uk_fw/gen5w_decrypt.py`
  is the orchestration point, and the FOOTER-aware layout in
  `evidence/eu-ota-container-structure.md` is the packing model.

## What is deliberately not reproduced here

The injected assembly listings, the C key-unwrap implementation, and the patch
offsets. They are published under an open licence, but reproducing them in this
repository would create a ready-to-use key extractor rather than a research
record. The citation above is sufficient for a researcher to consult the source.

## Verification status

Every claim above is attributed to the paper. The independent cross-checks from
this programme are: AES-CBC-compatible entropy profile, deterministic
package-level footer, absence of ECB, and a `.ver` manifest whose integrity value
is CRC-32 (proven forgeable, but computed over ciphertext, so post-execution
only).
