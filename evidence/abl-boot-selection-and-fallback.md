# Exact ABL boot selection, fallback, and `_sub` boundary

## Scope

This assessment binds the canonical decrypted EU `260128` update archive, the
exact signed 8 MiB `rel.1714-HF3` ABL flash image, its strictly decompressed IBB
stage, and two canonical rootfs scripts. It is static, host-side work. No
bootloader, updater, target executable, mount, copy, partition write, selector
change, reset, or boot attempt was executed.

Deterministic evidence:

- `evidence/artifacts/update-candidates/abl-boot-selection.json` — SHA-256
  `08de82b077da3c4f7543ae992a54afc80311947711ec2404e4a93d3d87a22bea`;
- `evidence/artifacts/update-candidates/abl-boot-selection-exact-static.asm` —
  byte-free exact-stage excerpt, SHA-256
  `efd46f8f7604daa73a9e51707efa7a1c44fb19aa6868208b2221720dd661899e`.

## Exact ABL configuration

The exact flash contains an IAS type-`0x60000` ABL-configuration container at
flash offset `0x102e6a`. Including its trailing payload CRC it is `0xa88` bytes,
SHA-256
`c9a592afcecb6adefc678d5503f98e946370948264690ef46c2bf39a7c718a9a`.
The analyzer verifies both CRC-32C values:

- header: `a242938d`;
- payload: `dd7740d8`.

The relevant ordered configuration records are:

| Boot index | Descriptor kind | Device instance | Basename | Predicate |
|---:|---:|---:|---|---|
| 2 | 2 | 1 | `iasImage` | `pcbver=10 lge.sign=1` |
| 3 | 2 | 2 | `iasImage` | `pcbver=10 lge.sign=1` |

Their exact record offsets are `0x34` and `0x60` within the configuration
payload. Both select the same basename but different device instances. The
canonical `esinit` comments independently identify boot index `2` as PLK1 and
index `3` as PLK2. Those comments corroborate the exact records; they are not
used alone to infer machine behavior.

## Exact selection and forward fallback

The decompressed stage-1 image is loaded at `0xe0000`, size `0x1fe00`, SHA-256
`3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2`.
The exact callback at file range `[0xae16,0xaff7)`:

1. reads the runtime byte at address `0x000c0214`;
2. masks it with `0x1f` to obtain the selected boot index;
3. increments the ordered-record index;
4. skips records earlier than the selected index;
5. returns zero after a selected loader returns with failure.

The exact configuration iterator at file range `[0xd576,0xd68b)` calls the
callback and, when that callback returns zero, advances to the next matching
record. The exact dispatch tail passes the same masked index to this
boot-option traversal. Therefore selection `2` makes the primary record
eligible first and, if its load path returns with failure, permits the later
secondary record.
Selection `3` skips the primary record and begins with the secondary record.
This is ordered forward fallback, not a symmetric A/B attempt algorithm.

The stage separately emits:

- `ABL.boot=<selected index in hexadecimal>`; and
- `ABL.bdev=<actual device and path>`.

That separation matters: the selected index need not identify the device that
ultimately booted after fallback.

## Userspace repair after secondary fallback

Canonical `./lib/systemd/esinit` is root-owned mode `0755`, size `17,894`,
SHA-256
`9f39947ec144322b29c0366bb681f0452ae3696139589bc2f4a2f05bf44afa52`.
It checks for exact command-line text `ABL.bdev=mmc2:/iasImage`. Its diagnostic
states that PLK2 booted after a PLK1 crash, and it then attempts to:

1. check or recreate the PLK1 filesystem;
2. mount PLK2 and PLK1;
3. copy `p2/iasImage` to `p1/iasImage`;
4. unmount and `sync`.

This is repair of the primary boot file from a successful secondary fallback.
It is not a proved mark-good transaction. Static call presence does not prove
mount, copy, sync, durability, or a future successful primary boot.

## What `_sub` means in the recovered stock paths

The exact ABL configuration names `iasImage`, not `iasImage_sub`. Neither the
configuration container nor the recovered stage contains a direct `_sub`
pathname literal.

Canonical
`./app/share/AppEngineerMode/constants/iasimage_update.sh` is root-owned mode
`0644`, size `1,224`, SHA-256
`a22efabdf3604cc57777fdba10ea00119bdc4721a5df8cecc1669b8480a78c2f`.
Its `sub` action explicitly copies:

```text
p2/iasImage_sub -> p1/iasImage
```

Its normal action copies:

```text
p2/iasImage -> p1/iasImage
```

Thus the exact recovered engineering route does not ask ABL to select a
`_sub` filename. It promotes the stored secondary image by overwriting the
primary basename that ABL already loads. AppFUMO's separate static path stages
`iasImage_sub` on p2, but successful staging and later promotion remain distinct
questions.

Literal absence is bounded evidence only. It does not prove that no dynamically
constructed proprietary route exists elsewhere, and the engineering script was
not executed.

## Security consequences and remaining boundary

The result closes an important architecture question:

- boot index `2` is primary PLK1 `iasImage`;
- boot index `3` is secondary PLK2 `iasImage`;
- a returned primary failure can fall forward to the secondary record;
- successful secondary boot triggers an attempted userspace repair of primary;
- the recovered `_sub` route is userspace promotion to the primary basename,
  not a direct configured ABL suffix selection.

It does **not** establish:

- where `0x000c0214` is provisioned or whether it is persistent;
- an attempt counter, decrement policy, health state, mark-good state, or
  rollback threshold;
- successful repair or durable activation;
- acceptance of an image under an untrusted key (the separate exact key-pinning
  assessment rejects that inference);
- custom-image boot, root, or persistence.
