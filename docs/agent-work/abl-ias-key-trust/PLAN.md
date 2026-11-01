# ABL IAS embedded-key trust plan

## Objective

Determine whether the exact EU ABL accepts any public key embedded in an IAS
boot container or first authenticates that key against an external pinned
digest. Keep exact target evidence separate from public Intel Apollo Lake/Slim
Bootloader semantics.

## Inputs

- canonical decrypted `HU/firmware/update.tar.gz`;
- selected `./abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin`;
- the twelve exact EU `iasImage*` plaintext identities;
- canonical rootfs `./bin/ias_image_app`;
- Intel `iasimage` repository commit
  `a4068106f9971ed1362def1f71a8eccf90fc4422`;
- Slim Bootloader commit
  `5f5c14b10ae6bd3cd0cf7e274142767dc2635a06` and its
  `IasImage.c`, `SecureBootRsa.c`, `SecureBootHash.c`, and payload
  `GetComponentHash` implementation.

## Questions

1. Does the exact ABL firmware identify as Apollo Lake IAS/ABL and contain the
   expected BPDT/CPD/IBB layout?
2. Do exact boot containers carry a public modulus and exponent inside each
   signed container?
3. Does stock `ias_image_app` merely validate a signature against the supplied
   key before embedding both, or pin an external key?
4. What does authoritative public Intel bootloader source do with the embedded
   key?
5. Can that public-source key-digest prerequisite be matched to exact target
   instructions or an exact target hash-store record?

## Acceptance

- Stable no-follow identity and unique archive-member selection.
- Exact BPDT, CPD, IBB IAS header, ABL build-string and package-key identities.
- Hash-bound public source with exact lines/semantics.
- Explicitly classify exact target key pinning as proved, rejected, or still
  unresolved; never promote public-source behavior without prerequisite match.
- No target bootloader, updater, helper, image, or signature tool execution.
- No modified/re-signed image, flash command, signature bypass, boot attempt, or
  persistence payload.
