# AppFUMO boot-image pairing and early-boot repair boundary

## Scope

This note closes an exact-static boundary between four previously separate
observations:

1. AppFUMO already has a copied partition record for writer index `1` (root);
2. a later routine maps that record's target pathname to an `iasImage*`
   basename;
3. another routine stages the chosen basename and its `_sub` companion; and
4. stock early userspace contains PLK1/PLK2 repair copying for `iasImage`.

It does **not** execute AppFUMO or `esinit`, copy an image, mount a partition,
reset the unit, or establish persistent boot activation.

## Canonical identities

The analyzer binds:

- embedded AppFUMO ELF:
  - size `5,066,264`;
  - SHA-256
    `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`;
  - Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`;
- canonical rootfs archive:
  - size `879,109,759`;
  - SHA-256
    `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
  - `66,836` members;
  - inventory SHA-256
    `c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c`;
- unique canonical member `./lib/systemd/esinit`:
  - regular file, root-owned in the archive, mode `0755`;
  - size `17,894`;
  - SHA-256
    `9f39947ec144322b29c0366bb681f0452ae3696139589bc2f4a2f05bf44afa52`.

The rootfs archive is streamed through one no-follow file descriptor. Complete
archive hashing, inventory construction, selected-member extraction, and final
identity revalidation use that same descriptor. Selected-member aliases,
duplicates, links and special nodes fail closed.

## 1. Root target to boot-image filename

Raw AppFUMO function `[0xa2480,0xa2c17)` has SHA-256
`b0c155bb9f8b81ca5bba4035166690ea44d959277d75bbaf66e3633126905b57`.

At `0xa24e0` it calls the already-bound record-copy helper with literal index
`1`. The function compares copied-record field `+0x28` against three root
partition pathnames and combines the match with display-mode value
`0x6d20b0`:

| Copied root-record target | Mode `3` | Mode `1` | Modes `2` or `4` |
|---|---|---|---|
| `/dev/mmcblk0p3` | `iasImage` | `iasImage_1280` | `iasImage_1920_12` |
| `/dev/mmcblk0p5` | `iasImage_p5` | `iasImage_p5_1280` | `iasImage_p5_1920_12` |
| `/dev/mmcblk0p7` | `iasImage_p7` | `iasImage_p7_1280` | `iasImage_p7_1920_12` |

Other display-mode values return the initially empty string on the reviewed
paths.

This is filename pairing, not content verification. In particular, the `p5`
and `p7` names strongly encode an intended root target but the function never
opens or authenticates the named image.

For the previously closed two-slot root cases, the pairing is consistent with:

- current root `p3` -> inactive root `p5`, inactive boot partition `p2`, and an
  `iasImage_p5*` filename; and
- current root `p5` -> inactive root `p3`, inactive boot partition `p1`, and an
  unsuffixed/size-suffixed `iasImage*` filename.

The function also contains a `p7` name family, but this package does not by
itself prove when a `p7` root record is selected or that a matching payload is
available.

## 2. Normal and `_sub` staging

Raw staging function `[0xa2ef0,0xa3e83)` has SHA-256
`40971ac6025a7c7e8fbfbeacb6143809789dcfb408b517c55f278d9e7e1bf42b`.
The broad preparation function calls it at `0xaaac1` and stores its Boolean
result.

The routine:

1. derives a source directory by appending the bound HU image-directory suffix
   to its package base;
2. derives a temporary update boot-image destination directory;
3. calls the filename selector at `0xa30b5`;
4. derives the companion name by appending `_sub`;
5. checks for both selected source names;
6. calls the same copy helper for the normal name at `0xa3370`; and
7. calls it again for the `_sub` name at `0xa396e`.

Those call paths prove construction and conditional staging logic only. They do
not prove the recovered EU package supplies either source, that the routine ran,
or that either copy succeeded.

## 3. Copy-helper integrity contract

Raw helper `[0x1413f0,0x141b28)` has SHA-256
`88d727d519722aeb8f621abcf4db6ba5eb730203fdeb9fe44d813cd84b018a85`.
Its exact sequence is:

1. remove an existing destination if present;
2. require the source to exist and open it read-only;
3. open the destination with the reviewed write-mode flags;
4. call `QIODevice::readAll()` on the source;
5. pass that buffer pointer and its recorded length directly to
   `QIODevice::write()`;
6. reject a negative write return immediately;
7. call `flush()`, obtain the destination handle, and call `fsync()`;
8. close source and destination;
9. reopen pathname objects for `QFile::size()` and require source and
   destination sizes to be equal; and
10. apply source permissions to the destination and require that operation to
    succeed before returning true.

### Correction of the earlier advisory short-write lead

The earlier advisory lead stopped at the negative-only check immediately after
`write()`. That local check is incomplete: the helper later compares source and
destination sizes and returns false on mismatch. Therefore a simple shorter
nonnegative write is **not** accepted as helper success if the later sizes are
stable and accurately reported.

The corrected result is still weaker than final byte integrity:

- neither `flush()` nor `fsync()` has its return value checked;
- the helper does not read destination bytes back;
- it computes no destination digest or signature;
- the later check reopens pathname objects and compares only sizes;
- it binds no stable source/destination device-and-inode identity across the
  complete operation; and
- same-size source mutation, pathname replacement, filesystem behavior, and
  durable media effects are outside this static proof.

Accordingly, the helper predicts a direct source-buffer write plus final
same-size and permission checks. It does not authenticate staged bytes or prove
durability.

## 4. Stock `esinit` is repair, not activation

The canonical `esinit` file contains comments mapping `ABL.boot` values `0..3`
to ELK, CLI, PLK1 and PLK2. Those comments have no runtime effect. The adjacent
`ABL.boot=2` command-line probe is also commented out.

The active probe instead observes the current kernel command line for the
`ABL.bdev` marker naming `iasImage`. On the true branch, the script checks boot
partition `p1`, mounts both boot partitions, and copies `iasImage` from `p2` to
`p1`. This is consistent with repair after a fallback boot, because the kernel
whose command line is being read is already running.

A separate `i915` splash-error branch checks boot partition `p2` and copies
`iasImage` in the opposite direction, from `p1` to `p2`. It is splash/preload
repair logic, not evidence of the next persistent root or boot target.

The exact file contains none of the bounded names `fw_setenv`, `abctl`,
`systemd-bless-boot`, `mark-good`, or `bootcount`. That exact-name absence is
corroboration only; it does not exclude an unnamed, external, MICOM, ABL, or
hardware implementation.

## Result

The exact-static chain now closes as:

`copied root record index 1 + target field`
`-> root-target/display-mode filename matrix`
`-> normal and _sub source checks`
`-> two calls to one size-checking copy helper`
`-> temporary boot-image staging`

Stock early userspace separately contains bidirectional `iasImage` repair
between boot partitions `p1` and `p2` based on already-observed boot/splash
state.

The chain does **not** establish:

- presence or identity of the required `iasImage*` package payloads;
- authentication of staged bytes;
- successful copy, flush, `fsync`, permission update, or durable media effects;
- a write from the staging directory to either boot partition;
- a persistent selector/index change;
- reset or recovery execution;
- ABL or MICOM image acceptance;
- boot health, attempt counters, mark-good, rollback, root, or persistence.

## Reproduction

```sh
PY="<platformio-env>/bin/python3"
"$PY" tools/uk_fw/appfumo_boot_image_pairing.py \
  work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf \
  work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz \
  -o work/appfumo-boot-image-pairing.json
"$PY" -m pytest -q tests/test_appfumo_boot_image_pairing.py
```

Tracked evidence:

- `evidence/artifacts/update-candidates/appfumo-boot-image-pairing.json`;
- `evidence/artifacts/update-candidates/appfumo-boot-image-pairing-exact-static.asm`.
