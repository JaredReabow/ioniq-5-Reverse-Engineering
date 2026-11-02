# Exact ABL IAS embedded-key trust boundary

## Result

The exact EU ABL **pins the public key carried by a signed IAS image**. The
recovered `rel.1714-HF3` stage hashes the carried 256-byte modulus and four-byte
exponent, compares the 32-byte digest with a selected external runtime
hash-record, returns failure on mismatch, and reaches RSA payload-signature
verification only after that comparison succeeds.

The exact type-3 OS-image path invokes this routine with hash selector `0x27`.
Consequently, the twelve package signatures prove more than self-consistency
only when their carried key also matches the provisioned digest. An arbitrary
new self-signed IAS key is not accepted by this exact code path.

A follow-on exact-static package now identifies the runtime descriptor as a FIT
type-`0x0b` key manifest copied by IBBL from a pre-existing FIT handoff at
`0xfef80000` to `0xc10c0`. The exact flash also contains an FTPR `oem.key`
Extension-14 manifest whose usage-39 digest differs from the package carried-key
candidate, but recovered code does not yet bind that stored object to the
runtime FIT pointer. The handoff producer and pre-IBBL authentication remain
open. See `evidence/abl-ias-key-manifest-provenance.md`.

## Canonical identities

The analyzer binds the canonical decrypted firmware archive:

- `HU/firmware/update.tar.gz`
- size `42,101,042`
- SHA-256 `1e67344a714708733a9158a52ef5d4def95b126e5725d070669ea64e0644c4c8`

It uniquely selects:

- `./abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin`
- regular member, UID/GID `8100/8100`, mode `0755`
- size `8,388,608`
- SHA-256 `f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac`
- build strings `rel.1714-HF3` and `release/GP1.0.1_LGE`

It also binds canonical rootfs member `./bin/ias_image_app`:

- size `39,664`
- SHA-256 `849b6b575ab76f865684d44f49977cf6c4b5fa60ae2cfb70c49a4a66424368d8`
- GNU Build ID `adbd4f651cf1d63e7e5f52f7a32dc54fb507bd48`

## Exact firmware topology

The exact flash contains the expected Intel primary BPDT at `0x100000`. Its
IBBP entry points to a CPD at flash `0x187000`, whose four entries are:

| Entry | CPD-relative offset | Size |
|---|---:|---:|
| `IBBP.man` | `0x70` | `0x2ec` |
| `BPM.met` | `0x380` | `0xb4` |
| `IBBL` | `0x440` | `0x4000` |
| `IBB` | `0x4440` | `0x34000` |

The IBB begins with an IAS `ipk.` container at flash `0x18b440`. Its four
stored subimage sizes are `0xc0`, `0x172d2`, `0x44a9`, and `0x18493`. The final
three are raw LZ4 blocks with a four-byte decompressed-size prefix and a
four-byte trailer. Strict host-side decompression produces:

| Stage | Size | SHA-256 |
|---|---:|---|
| 1 | `130,560` (`0x1fe00`) | `3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2` |
| 2 | `35,584` (`0x8b00`) | `d1e6d5da3a95a1634ec6a98703775f464044e335e0000f5f1477062f5d91d564` |
| 3 | `172,352` (`0x2a140`) | `3a8a2ddef16dfefb17b4a28878df601f4e9f5a85fb53e2eecf11c3b4dcf4aa9e` |

A unique absolute pointer to `ABL.oemkm` binds stage 1's load base to `0xe0000`.
That stage contains the `ipk.` parser and the exact signed-image authentication
routine. This resolves the earlier executable-boundary/load-address block for
the relevant verifier.

## Exact key pin and RSA order

The stage-1 routine at file range `[0x157a3,0x159fe)` (runtime
`[0xf57a3,0xf59fe)`) has SHA-256
`4b71d5c95ff2bcf4210ba23a96883f3ce3524fb31b40f037a00991a6c14a7f30`.
It:

1. requires the signed-image flag;
2. walks a runtime descriptor table and selects descriptor type `0x0b`;
3. applies the caller's selector as a usage bitmap over `0x44`-byte records;
4. copies a 32-byte expected digest from record offset `0x24`;
5. reverses the stored 256-byte modulus, appends the stored four-byte exponent,
   and SHA-256 hashes those `0x104` bytes;
6. compares exactly 32 bytes and returns failure on mismatch;
7. only after equality, prepares the modulus/exponent and calls RSA verification
   over the IAS signed-data digest and 256-byte signature.

The complete direct-call inventory is at stage file offsets `0xa1f8`, `0xa560`,
`0xc1ea`, `0xc9e0`, and `0xd4fe`, using selectors `0x25`, `0x28`, `0x27`,
`0x27`, and `0x28`. At `[0xc1e4,0xc20c)`, the selector-`0x27` authentication
result is checked before the subsequent image-type-3 branch. This binds the
exact package's signed type `0x30300` to the pinned-key route.

## Exact package key

All twelve exact EU package members carry:

- RSA modulus SHA-256
  `227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6`;
- exponent `65537`;
- valid RSA-2048 PKCS#1 v1.5 SHA-256 signatures.

For the byte transformation used by the public Slim Bootloader source, the hash
input is the reversed stored 256-byte modulus followed by the four stored
little-endian exponent bytes. Its candidate digest is:

`437008c1b26fd821a7c7c0ec855aaba5587f62deaaa98d9b2fcbf6ad4179aa06`

The exact ABL routine uses the same hash input. The candidate is not present
verbatim in the stored 8 MiB flash or any of the three decompressed IBB stages.
That is bounded negative evidence only. Follow-on exact instructions prove that
IBBL copies a pre-existing FIT handoff from `0xfef80000`, including a present
type-`0x0b` payload, before stage 1 consumes the key manifest. The exact flash's
stored FTPR `oem.key` has usage-39 digest `9b0a59...`, not the package candidate
`437008...`; the runtime binding and earlier authentication remain unresolved.

## Stock constructor boundary

Exact `ias_image_app` instructions load a supplied public key and verify a
signature against that key before constructing the signed IAS trailer. This is
a self-consistency check by an image-construction utility. It does not establish
what the bootloader trusts and is not evidence that arbitrary self-signed images
boot.

## Public Intel semantics

Two public Intel lineages are hash/commit bound:

- `intel/iasimage` commit
  `a4068106f9971ed1362def1f71a8eccf90fc4422` documents IAS as a format consumed
  by bootloaders and documents signed type `0x30300` with a private key.
- Slim Bootloader commit
  `5f5c14b10ae6bd3cd0cf7e274142767dc2635a06` contains the Apollo Lake IAS path.

The latter performs this order:

1. `IasImage.c` copies `IAS_PUBLIC_KEY` into an RSA key object and calls
   `DoRsaVerify(..., COMP_TYPE_PUBKEY_OS, ...)`.
2. `SecureBootRsa.c` normalizes modulus/exponent bytes and calls
   `DoHashVerify` on the key before payload signature verification.
3. `SecureBootHash.c` obtains the expected component digest through
   `GetComponentHash`, hashes the supplied key bytes, and compares the digest.
4. `PayloadLib.c` obtains the matching component entry from the
   `gPayloadKeyHashGuid` HOB.
5. Payload RSA verification follows only after the key digest succeeds.

This source remains comparative for names and provisioning architecture, but
its key-hash-before-RSA order is now independently corroborated by exact
`rel.1714-HF3` instructions. Follow-on exact IBBL analysis identifies the
descriptor as FIT type `0x0b` and its immediate source as a volatile handoff at
`0xfef80000`. It also recovers a stored FTPR `oem.key` candidate, but does not
prove the runtime pointer selects that object or prove the earlier
authentication of the handoff.

## Conclusions

- The package signatures are real RSA signatures, not merely unkeyed hashes.
- The public Intel Apollo Lake IAS implementation pins a digest of the carried
  OS key before accepting the payload signature.
- The exact LGE ABL's key pinning is **proved** for its signed IAS verifier.
- The exact type-3 OS-image path uses that pinned-key verifier with selector
  `0x27`.
- Acceptance of an arbitrary embedded key is rejected by the exact
  compare-before-RSA path.
- The immediate runtime source is a FIT type-`0x0b` key manifest copied from
  `0xfef80000`; a stored FTPR `oem.key` candidate is recovered, but its runtime
  binding, handoff producer, and pre-IBBL authentication remain unknown.
- Custom signed-image acceptance, boot acceptance, root, persistence,
  mark-good, rollback, and recovery are **not proved**.

## Reproduction

```sh
<platformio-env>/bin/python3 tools/uk_fw/abl_ias_key_trust.py \
  --update-archive work/decrypted-eu-260128/HU/firmware/update.tar.gz \
  --rootfs work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz \
  --boot-dir work/appfumo-iasimage-eu260128/encrypted \
  --sbl-repo work/online-slimbootloader-20261110 \
  --iasimage-repo work/online-intel-iasimage-20261110
```

Tracked deterministic evidence:

- `evidence/artifacts/update-candidates/abl-ias-key-trust.json`
  - size `7,824`
  - SHA-256 `df9d9a2f730efb2103a11113f028008ac3c36b1b05293602d72958f5612c5fa6`
- `evidence/artifacts/update-candidates/abl-ias-key-trust-exact-static.asm`
  - size `16,384`
  - SHA-256 `5c069c0b869288e38087ad25dc86c8efa18d2f16799a8c26434dc8d82515932b`

The analyzer is read-only with respect to all inputs. It does not execute an
updater, target helper, bootloader, constructor, firmware image, or package. It
does not create a modified/re-signed image or provide a flash or bypass path.
