# Exact ABL IAS embedded-key trust boundary

## Result

The exact EU ABL question is **not yet closed**. The twelve exact boot
containers all carry one RSA-2048 public key, and their signatures verify under
that carried key. That proves package self-consistency, not bootloader trust.

A highly relevant public Intel Apollo Lake bootloader implementation does **not**
accept an arbitrary carried IAS key: it hashes the carried modulus/exponent,
compares that digest with component `COMP_TYPE_PUBKEY_OS`, and only then verifies
the IAS payload signature. The digest is obtained from a component-key-hash HOB.
This establishes a concrete prerequisite and expected trust model, but it is not
promoted to the proprietary exact LGE ABL without an instruction or trust-store
match.

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

The IBB begins with an IAS `ipk.` container at flash `0x18b440`. Exact ABL
literals include `ipk.`, `iasImage`, and `oemkm`. These facts bind platform,
format, and boot-stage identity; literals and topology alone do not identify the
verification branch.

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

That candidate is not present verbatim in the exact 8 MiB flash image. This is
bounded negative evidence only: compressed modules, CSE/Boot Guard manifests,
a HOB supplied by an earlier authenticated stage, a transformed representation,
or another trust-store design remain possible.

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

This source is authoritative for that public implementation and strongly guides
exact-target reverse engineering. It is still comparative evidence because the
exact proprietary LGE `rel.1714-HF3` source and a byte/control-flow match have
not been recovered.

## Conclusions

- The package signatures are real RSA signatures, not merely unkeyed hashes.
- The public Intel Apollo Lake IAS implementation pins a digest of the carried
  OS key before accepting the payload signature.
- The exact LGE ABL's key pinning remains **unknown**.
- Acceptance of an arbitrary embedded key is **not proved**.
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

Tracked deterministic report:

- `evidence/artifacts/update-candidates/abl-ias-key-trust.json`
- size `4,422`
- SHA-256 `2e6096d14d54d06af4ddd2989e80de1558ff8de081b64e64306ada123658f3b7`

The analyzer is read-only with respect to all inputs. It does not execute an
updater, target helper, bootloader, constructor, firmware image, or package. It
does not create a modified/re-signed image or provide a flash or bypass path.
