# Exact ABL IAS key-manifest handoff provenance

## Result

The runtime table used by the exact `rel.1714-HF3` IAS verifier is now
identified: it is an Intel Firmware Interface Table (FIT), and the selected
runtime object is FIT type `0x0b`.

The exact IBB loader (`IBBL`) accepts a pre-existing FIT-format handoff at
physical address `0xfef80000`, checks its `_FIT_   ` header and bounded entry
count, copies the table to `0x000c10c0`, appends a type-`0x7f` entry, and
relocates referenced payloads into the low-memory copy. Its relocation mode
skips FIT type `1`, but not type `0x0b`; a present type-`0x0b` payload is
therefore copied and its FIT address rewritten.

The decompressed stage then walks that relocated table, selects type `0x0b`,
parses a key-manifest extension at offsets matching a CSE Extension 14 R1 key
manifest, applies selector `0x27` as usage bit **39**, and copies the selected
record's 32-byte digest before comparing it with the carried IAS public-key
digest. Public Intel FIT definitions name type `0x0b`
`FIT_TYPE_0B_KEY_MANIFEST`; hash-bound ME Analyzer source names usage 39
`OS Kernel`. The latter names are public-source corroboration, while the table
addresses, layout, bit selection, digest offset, and compare path are proved by
exact target instructions.

The exact CSE RBE and BUP now close the persistent-to-published byte path. RBE
selects FTPR CPD member `oem.key`, creates `oem_key_man` at that exact length,
transfers the source bytes without a visible transformation, and checks the
manifest dword length. BUP then copies `oem_key_man` into a FIT payload and
publishes type `0x0b` at `0xfffe1000`. IBBL later consumes a FIT at `0xfef80000`.
The physical mapping between those addresses remains unproved, as does any
earlier CSE, Boot Guard, ACM, fuse, or ROM authentication.

## Canonical identities

The result binds the canonical decrypted update archive:

- `HU/firmware/update.tar.gz`
- size `42,101,042`
- SHA-256 `1e67344a714708733a9158a52ef5d4def95b126e5725d070669ea64e0644c4c8`

It uniquely selects:

- `./abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin`
- size `8,388,608`
- SHA-256 `f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac`
- build `rel.1714-HF3 / release/GP1.0.1_LGE`

Relevant exact stages are:

| Object | Size | SHA-256 |
|---|---:|---|
| IBB loader (`IBBL`) | `16,384` (`0x4000`) | `394c442368c67f82f17e84854575bf07abafac2b8fbf2fda7dca68b182f91b93` |
| decompressed IBB stage 1 | `130,560` (`0x1fe00`) | `3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2` |

## Exact IBBL FIT handoff

The IBBL routine at file range `[0xf3,0x171)`:

1. checks source dwords for `_FIT_   `;
2. reads the FIT header's 24-bit size/count field;
3. accepts at most 21 source entries;
4. copies `count * 0x10` bytes to the destination;
5. appends a zeroed type-`0x7f` entry;
6. stores the payload-relocation destination in that appended entry; and
7. increments the copied FIT header count.

The caller at `[0x4ef,0x54c)` supplies:

- source `0xfef80000`;
- destination `0x000c10c0`;
- relocation mode `2`.

The relocator at `[0x40,0xf3)` walks entries after the header and before the
appended final entry. In mode 2 it skips type `1` and copies other referenced
payloads, rewrites their entry addresses, and advances the packed destination
with 16-byte alignment. FIT type `0x0b` is therefore included when present.

This establishes a volatile handoff and low-memory copy. It does not establish
where the bytes at `0xfef80000` originated or whether its type-`0x0b` payload is
the exact stored `oem.key` described below. The package carried-key candidate
digest remains absent verbatim from the stored update ABL, IBBL, and
decompressed stage 1.

## Exact stage-1 key-manifest consumer

The exact IAS authentication routine reads:

- FIT count from `0x000c10c8 & 0x00ffffff`;
- FIT entries from `0x000c10c0` in `0x10`-byte strides;
- entry type from offset `0x0e`, masked by `0x7f`;
- selected type `0x0b`;
- manifest pointer from entry offset `0`.

For the selected manifest it uses:

| Field | Exact offset/value |
|---|---:|
| extension start | `manifest + 0x284` |
| extension size | dword at `manifest + 0x288` |
| first entry | `manifest + 0x2a8` |
| entry size | `0x44` |
| digest | entry `+ 0x24`, 32 bytes |

For selector `0x27`, the routine computes:

- byte index `0x27 >> 3 = 4`;
- mask `1 << (0x27 & 7) = 0x80`.

The exact type-3 OS caller pushes this selector before calling the carried-key
and payload verifier. The selected digest is then compared with SHA-256 over
`reverse(stored 256-byte IAS modulus) || stored four-byte exponent`; RSA payload
verification follows only after equality, as established in the earlier key
trust package.

## Exact CSE RBE persistent-object materialization

The exact RBEP CPD contains executable member `rbe`:

- flash offset `0x105000`;
- size `0x9000` (`36,864`);
- SHA-256 `ec4c2ea54c2943f6f6ffed4b4157b7b03cbccf6ca2cc9b21ccc3dd62adc88cc1`;
- code base `0x40000` and main-thread entry `0x407a3`.

The main entry calls a fail-closed initialization chain that reaches `0x42f45`.
On the exact `oem.key` branch, that function passes:

- source name `oem.key`;
- source partition index `0`;
- destination object name `oem_key_man`; and
- an output slot for the materialized object

to the helper at `0x42e61`. That helper resolves the source CPD descriptor,
creates the destination object at the descriptor's exact byte length, transfers
that exact length from the source partition offset, and requires
`destination[+0x18] * 4` to equal the source length. The exact FTPR member is
`0x61c` bytes, and its manifest dword count is `0x187`, also `0x61c` bytes.
No transform is visible between source and destination in this path.

This proves byte continuity from the exact stored FTPR `oem.key` member to the
Snowball object named `oem_key_man`. It does not by itself prove who authenticated
FTPR, RBE, or the manifest before this copy.

## Exact CSE BUP FIT producer

The exact FTPR CPD also contains executable member `bup`:

- flash offset `0x145000`;
- size `0x33000` (`208,896`);
- SHA-256 `cee77bc172a9df1c4088d5f716b9e55cda539a26656d07a92268c3cd5d4f0165`;
- code base `0x26000` from its exact process metadata.

Its exact code:

1. initializes `_FIT_   ` and count 1 in an allocated table buffer;
2. looks up object `oem_key_man` and obtains its data pointer;
3. requires its dword length to fit in `0x1000` bytes;
4. copies the object to the FIT payload area at buffer offset `0x1000`;
5. appends a FIT entry with address `0xfffe1000`, the object length converted
   from dwords to bytes, and type `0x0b`; and
6. increments the FIT count through its generic 16-byte entry appender.

A separate exact BUP resolver couples names `rot.key`/`oem.key` with
`rot_key_man`/`oem_key_man`, locates Extension 14, validates key type 1 versus
2, and materializes usage/hash records. Combined with the RBE exact-length copy,
this proves that BUP's published type-`0x0b` object contains the exact FTPR
`oem.key` bytes.

IBBL's later source table is at `0xfef80000`, whereas BUP publishes the payload
address as `0xfffe1000`. The intervening physical mapping or handoff is not yet
recovered, so the exact address chain remains bounded at both ends.

## Exact stored FTPR `oem.key` manifest

The exact flash FTPR CPD contains:

- member `oem.key`;
- CPD-relative offset `0x5e000`;
- flash offset `0x17c000`;
- size `0x61c` (`1,564`);
- SHA-256 `a72a5d867185852be1466a9d3d2e97bb11bd6b0a89b48f5454220def946814bd`.

It is a `$MN2` manifest with a `0x284`-byte header and Extension 14 of size
`0x398`, containing thirteen `0x44`-byte key records. Host-side RSA-2048
PKCS#1 v1.5 SHA-256 verification of the embedded manifest signature succeeds
over the header-before-RSA plus protected extension bytes. This proves embedded
self-consistency, not an external root of trust.

Exactly one record sets usage bit 39. Its digest is:

`9b0a59c842ba70857b595ed8115630d3a342a10c9d4437f9ff4807517693e0af`

That value also equals SHA-256 over the stored manifest public modulus plus its
stored four-byte exponent. It does **not** equal the package IAS carried-key
candidate:

`437008c1b26fd821a7c7c0ec855aaba5587f62deaaa98d9b2fcbf6ad4179aa06`

This is an exact stored-object mismatch, not a boot verdict. The source FIT at
`0xfef80000` was not captured, and exact recovered code has not yet bound its
type-`0x0b` pointer to FTPR `oem.key`. The package may also be applied under an
already-installed ABL/key manifest rather than the ABL image present in the
same update archive. Therefore neither package acceptance nor rejection follows
from the mismatch alone.

## `ABL.oemkm` export

When the routine first obtains the type-`0x0b` object, it caches:

- extension pointer at global `0x000c1060`;
- extension size at global `0x000c1064`.

Later exact stage code formats those values as `%x@%x` and adds the kernel
command-line field `ABL.oemkm`. This proves an exact observation lead for a
future disconnected bench: `/proc/cmdline` may disclose the installed runtime
extension's size and address. It does not make the memory readable, recover the
manifest signature header, or prove that a user-space capture is permitted.

## Public structure corroboration

Two public sources are hash-bound and kept separate from exact-target proof:

1. Slim Bootloader commit
   `5f5c14b10ae6bd3cd0cf7e274142767dc2635a06`, file
   `BootloaderCorePkg/Include/FirmwareInterfaceTable.h`, SHA-256
   `0e0f1fff576e4edc48d2918d14bb1292526d3c01d3547d38305ea435543722ef`.
   It defines 16-byte FIT entries, the `_FIT_   ` signature, type `0x0b` as
   `FIT_TYPE_0B_KEY_MANIFEST`, and type `0x10` as
   `FIT_TYPE_10_CSE_SECURE_BOOT`.
2. ME Analyzer commit
   `d27ccdba0aadbad490f47b5b631c369b682a7ef5`, file `MEA.py`, SHA-256
   `ed2dfb3b9efe58431609b4d3eefe6908b3124228288163dd4fd667dd17d5f4ef`.
   Its reverse-engineered CSE Extension 14 R1 entry is `0x44` bytes with a
   16-byte usage bitmap and 32-byte hash at offset `0x24`; its usage dictionary
   names bit 39 `OS Kernel`.

The exact proprietary instructions independently match these structural facts.
The public names do not prove the target's earlier authentication policy or
persistent provisioning implementation.

A current public coreboot Apollo Lake/Gemini Lake IFWI constructor provides
separate comparative corroboration:

- commit `4f3d2b564c8675a05d555d27740d62e0257cbd5c`;
- `util/apl_ifwi/apl_ifwi.py` SHA-256
  `824497f98ed0f6475b13aebd2b798244e6ab09b55349e7004496ffe9138f296a`;
- it creates an OEM Extension-14 manifest, names the resulting object
  `oem_key`, and replaces FTPR CPD member `oem.key`.

That modern public constructor corroborates the persistent member's purpose but
is not evidence of exact source lineage or of the target's runtime authentication
root.

## Security boundary

What is now proved:

- the runtime descriptor table is FIT-format;
- exact CSE RBE copies FTPR `oem.key` at its exact source length into
  `oem_key_man`, with a matching manifest-length check;
- exact CSE BUP constructs a FIT type-`0x0b` entry from `oem_key_man` and
  publishes payload address `0xfffe1000`;
- exact CSE BUP couples names `oem.key` and `oem_key_man` in its key resolver;
- IBBL copies a FIT from `0xfef80000` to `0xc10c0`;
- IBBL relocates a present type-`0x0b` payload;
- stage 1 selects FIT type `0x0b` as its IAS key-manifest source;
- selector `0x27` is usage bit 39;
- the record and digest layout are exact;
- the extension pointer/size are exported as `ABL.oemkm`;
- the exact flash contains a self-consistent, embedded-signature-valid FTPR
  `oem.key` Extension-14 manifest with usage bit 39;
- its stored usage-39 digest is `9b0a59...` and differs from the package
  carried-key candidate `437008...`;
- the selected runtime digest gates the later IAS RSA signature verification.

What remains unproved:

- how CSE BUP's FIT/payload addresses are mapped into IBBL's source handoff at
  `0xfef80000`;
- whether an installed unit executes this exact RBE/BUP/ABL set rather than a
  different installed manifest or firmware generation;
- whether and how CSE, Boot Guard, an ACM, ROM, or another earlier stage verifies
  it before IBBL;
- the actual runtime expected digest on an installed unit;
- any writable or replaceable provenance path;
- custom-image acceptance, boot acceptance, root, persistence, health,
  mark-good, rollback, or recovery.

The exact package carried-key candidate remains
`437008c1b26fd821a7c7c0ec855aaba5587f62deaaa98d9b2fcbf6ad4179aa06`.
Its absence from the update ABL and mismatch with the stored usage-39 record are
bounded evidence only until the runtime FIT object and installed ABL identity
are captured.

## Reproduction

```sh
<platformio-env>/bin/python3 tools/uk_fw/abl_ias_key_provenance.py \
  --update-archive work/decrypted-eu-260128/HU/firmware/update.tar.gz \
  --sbl-repo work/online-slimbootloader-20261110 \
  --mea-repo work/online-meanalyzer-20261111
```

Tracked deterministic evidence:

- `evidence/artifacts/update-candidates/abl-ias-key-provenance.json`
  - size `12,690`
  - SHA-256 `86f3936c41b75fde136bdd68e24a0253a5192072ea9eb06d0b30148908b9014b`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `31,647`
  - SHA-256 `f888b0c5b13020625be4550a069ef22a2070cfe4a2e742385b0535b3aeff46de`

The analyzer is read-only with respect to all inputs. It does not execute an
updater, bootloader, target helper, image constructor, firmware image, or target
binary and does not produce a modified image, signature bypass, flash procedure,
or persistence mechanism.
