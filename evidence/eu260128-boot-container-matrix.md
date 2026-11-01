# EU 260128 complete boot-container matrix

## Result

The original EU `260128` package contains all twelve `iasImage*` filenames used
by the exact AppFUMO selector. Their earlier absence from
`work/decrypted-eu-260128/HU/images/` was a limitation of that selected
decryption output, not absence from the source package.

This package copied the originals into ignored `work/` and performed host-side,
read-only cryptographic analysis. The original download was not modified.

## Wrapper split

The twelve files form two classes:

- six normal names are `6,226,728`-byte TE2 AES-128-CBC envelopes;
- six `_sub` names are already `6,210,308`-byte plaintext `ipk.` containers.

The validated TE2 metadata integrity check and established package content key
decrypt every normal file to exactly `6,210,308` bytes. No recovered target
helper was required or executed.

This corrects the older interpretation that the normal-image wrapper could not
be handled offline. It is the same TE2 envelope already recovered for the other
EU package artifacts.

## Authentication

All twelve plaintext containers have:

- `ipk.` magic;
- format version `0x00030300`;
- header size `0x34`;
- total field `0x005ebfcc`;
- build/format ID `0x42f08d94`;
- signed range `[0, 0x5ec004)`;
- a valid embedded RSA-2048 PKCS#1 v1.5 SHA-256 signature;
- public exponent `65537`;
- the same embedded modulus, SHA-256
  `227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6`.

Embedded-signature validity proves package self-consistency. It does not prove
that ABL or MICOM pins or accepts that modulus; that verifier remains outside
the recovered package.

## Kernel identity

The normal images' shorter command lines place the legacy LZ4 frame at
`0x441a`; the serial-console `_sub` images place it at `0x445e`. Host-side LZ4
decompression of every frame produces exactly the recovered kernel:

- size `16,398,376`;
- SHA-256
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`.

Thus all twelve variants differ in command-line/trailer material but carry the
same kernel bytes.

## Command-line matrix

| Filename family | Root target | Serial console |
|---|---|---|
| `iasImage`, `_1280`, `_1920_12` | `/dev/mmcblk0p3` | no |
| `iasImage_sub`, `_1280_sub` | `/dev/mmcblk0p3` | yes |
| `iasImage_1920_12_sub` | `/dev/mmcblk0p5` | yes |
| `iasImage_p5`, `_p5_1280`, `_p5_1920_12` | `/dev/mmcblk0p5` | no |
| all `iasImage_p5*_sub` | `/dev/mmcblk0p5` | yes |

Every command line uses `init=/lib/systemd/esinit`. `_sub` variants additionally
carry `console=ttyS2,115200n8` and the recovered early-console configuration.

The asymmetry in `iasImage_1920_12_sub` is exact package evidence, not a naming
inference: that file names root partition p5 while its normal partner names p3.
It does not by itself identify when ABL selects `iasImage_sub` instead of
`iasImage`.

## Update-chain effect

This closes a previously conditional prerequisite:

`AppFUMO selector filename`
`-> source-package member exists`
`-> TE2 plaintext or already-plaintext ipk container`
`-> valid embedded signature`
`-> exact recovered kernel and root command line`.

It still does not establish:

- runtime source pathname/object stability;
- same-byte continuity through staging, decryption pipeline and `dd`;
- final boot-partition bytes or durability;
- external ABL/MICOM key pinning or image acceptance;
- selection between normal and `_sub` files;
- persistent activation, health, mark-good, rollback, root, or persistence.

## Deterministic analyzer

`tools/uk_fw/eu260128_boot_container_matrix.py` fails closed on the exact twelve
names, file type, symlinks, source size/hash, TE2 metadata integrity, plaintext
hash, `ipk.` fields, command-line bounds, embedded RSA signature/key, root
partition, console contract, LZ4 output size, and recovered-kernel hash.

```sh
PY="<platformio-env>/bin/python3"
"$PY" tools/uk_fw/eu260128_boot_container_matrix.py \
  work/appfumo-iasimage-eu260128/encrypted \
  -o work/eu260128-boot-container-matrix.json
"$PY" -m pytest -q tests/test_eu260128_boot_container_matrix.py
```

No modified or re-signed image was created. No updater, target decryptor, mount,
partition writer, reset, or boot component was executed.
