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
publishes type `0x0b` at `0xfffe1000`. Before that copy, RBE obtains a
CRC-checked UEP through an exact hardware-window or BPDT route, extracts its
256-bit OEM-key field, and requires the `oem.key` modulus-plus-exponent digest
to match before RSA and extension validation. Exact BUP also resolves `IBBL`
and places the exact `0x4000`-byte member at buffer offset `0x1c000`, which is
SRAM alias `0xffffc000`. IBBL's embedded descriptor at runtime `0xffffe760`
is now recovered as `{ destination=0xfeffc000, count=0x1000 dwords,
source=0xffffc000 }`: it self-relocates IBBL. BUP also writes FIT-base pointer
`0xfffe0000` at buffer offset `0x1ffc0`; self-relocation carries it to
`0xfeffffc0`, where exact IBBL reads it and copies/relocates the FIT into
`0xfef80000`. The persistent-to-runtime type-`0x0b` byte path is therefore
closed. External trust or fuse precedence governing the selected UEP bytes
remains unproved.

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

Before this caller executes, exact IBBL startup configures memory types for the
`0xfffe0000` CSE SRAM region and the `0xfef80000` temporary region, clears the
latter, and invokes its three-dword copy helper on the embedded descriptor at
`0xffffe760`. The descriptor is statically present at IBBL file offset `0x2760`
and copies `0x1000` dwords from `0xffffc000` to `0xfeffc000`: exactly one
`0x4000`-byte IBBL image. IBBL then reads the preserved FIT pointer from
`0xfeffffc0` and copies the bounded FIT from `0xfffe0000` to `0xfef80000`.
This proves both self-relocation and the separate FIT byte mapping. The package
carried-key candidate digest remains absent verbatim from the stored update
ABL, IBBL, and decompressed stage 1.

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

BUP separately resolves `IBBL` and `IBB`, rejects an IBBL larger than `0x9000`,
and loads IBBL at `fit_buffer + 0x20000 - ibbl_size`. The exact IBBL size is
`0x4000`, so it occupies buffer offset `0x1c000`. With BUP's `0xfffe0000` SRAM
alias, the exact runtime base is `0xffffc000`. This equals the source in IBBL's
embedded self-relocation descriptor, independently joining BUP placement to
IBBL execution identity.

BUP also supplies the exact IBB producer side. It takes source offset and size
from the resolved `IBB` member descriptor, divides the same `0x20000`-byte SRAM
buffer into four `0x8000`-byte slots, reads at most `0x8000` bytes into
`fit_buffer + (ring_index & 3) * 0x8000`, advances source position, and uses a
hardware handshake before reusing each slot. Its response encodes chunk-count
value 3 in bits 29..28 (meaning four slots), IBB size in bits 27..14, and ring
state through the low four XOR handshake bits. Exact IBBL implements the
matching consumer through PCI configuration addresses `0x80007870` and
`0x80007860`, copies ring slots from the `0xfffe0000` SRAM alias into a buffer
beginning at `0xfefbd900`, acknowledges each slot, and accepts up to `0x38000`
bytes. This closes the proprietary producer/consumer ring protocol and exact
host destination.

The FIT follows a separate, now exact path. BUP writes `0xfffe0000` at buffer
offset `0x1ffc0`. Because IBBL occupies buffer offset `0x1c000`, the pointer is
at IBBL-relative offset `0x3fc0`. IBBL self-relocation copies it to
`0xfeffffc0`. Before requesting the IBB stream, exact IBBL reads that pointer,
calls its bounded FIT validator/copier with source `0xfffe0000` and destination
`0xfef80000`, then relocates referenced payloads in mode 0. Later it copies that
FIT to `0xc10c0` and relocates type `0x0b` in mode 2. This closes the BUP FIT
buffer to runtime stage-1 key-manifest mapping.

Historical Apollo Lake Slim Bootloader source at the same hash-bound commit
independently matches the exact producer/consumer protocol: chunk-count field,
value-3-to-four-slots rule, size field, low-four-bit XOR handshake, ring index,
slot geometry, source expression, acknowledgement, and PCI configuration
offsets. It is corroboration; the exact target instructions above provide the
mapping proof.

## Exact CSE signed-module byte chains

Host-side verification closes two self-contained module-integrity chains:

- `RBEP.man` (SHA-256 `80b5c254b9349d3bb716122f8dce36873e0ecb1a0576231fc74057eb90fcde79`)
  has a valid embedded RSA-2048 PKCS#1 v1.5 SHA-256 signature, contains the
  reversed SHA-256 of `rbe.met`, and `rbe.met` contains the reversed SHA-256 of
  exact RBE bytes;
- `FTPR.man` (SHA-256 `ca4fc90c57b212daa077e8dec1bc7c4827638ff21da0e7224a3bbce2e57efdf4`)
  has a valid embedded signature, contains the reversed SHA-256 of `bup.met`,
  and `bup.met` contains the reversed SHA-256 of exact BUP bytes.

The manifest keys are carried inside their respective `$MN2` headers. Signature
validity therefore proves internal consistency and byte binding until their
expected key digest is connected to an earlier runtime object.

### Exact `ipub_key → rot.key → CSE manifests` chain

Exact RBE resolves runtime object `ipub_key`, reads selector byte `+0x12`, uses
it to select a pointer at `+0x16 + 4*selector`, and copies exactly 32 bytes to
`0x6047fa8`. It then passes that digest pointer and materialized `rot_key_man`
to the same fail-closed `$MN2` key-hash/RSA/extension validator with selector
`5`.

The resolver now narrows the earlier-stage boundary further. It reads a bounded
runtime-object handoff at `0x08200000`: the first dword supplies total size
(capped at `0x8000`), entries begin at `0x08200008`, names are compared across
`0x0c` bytes, enabled bit 0 is tested at entry `+0x0d`, the next-entry distance
is the word at `+0x0e`, and payload begins at `+0x12`. RBE also contains an
append routine for this same handoff, but its first early append is named
`cld_rst_blk`. Key initialization then requires existing entries named `bpdt`,
`pm_trans`, `ftpm_fuses`, `sss_em`, `rbe.man`, `pmc_ipc`, and `ipub_key`; a
missing optional `pmc_msg` is instead appended by RBE. The `ipub_key` path calls
the existing-entry lookup and does not create an `ipub_key` entry. The exact
RBE has only five direct static references to handoff base `0x08200000`, all in
these lookup/append routines.

The cap does not make the iterator structurally fail closed. The lookup does
not require a nonzero or minimum entry total and does not first require enough
remaining bytes for the name, state, and total fields. A nonmatching entry with
total zero leaves the cursor unchanged, while a short nonzero total can advance
into the current entry's own bytes. Thus malformed totals can produce
nonprogress or interior re-parsing before the bounded-end comparison. This is
an exact parser-integrity dependency; control of such an incoming entry is not
proved.

The append side also trusts the incoming 32-bit current total. It checks only
the wrapped sum with the new entry total and does not reject carry. RBE's first
append is the one-byte `cld_rst_blk`, whose entry total is `0x13`; incoming
totals `0xffffffed..0xffffffff` make the checked sum wrap to `0..0x12` and
place the destination at `0x081fffed..0x081fffff`. The header/payload write can
therefore begin before the declared handoff and overlap its total field. This
is a bounded pre-handoff write condition, not a demonstrated attacker-controlled
memory-corruption route.

The successful `ipub_key` path has a separate unchecked selection dependency.
It does not inspect the matched entry's total or derive a payload length before
reading selector byte `+0x12`, loading a dword pointer from
`entry + 0x16 + 4*selector`, and copying `0x20` bytes from that pointer. There
is no observed selector upper bound, pointer-field-within-entry check, or
selected-pointer range check. Selector zero requires entry total at least
`0x1a` merely to contain its four-byte pointer field; with the intended
`0x24`-byte payload, only selectors `0..7` keep that field within the payload.
Malformed-object attacker control, however, remains unproved.

This proves that RBE consumes `ipub_key` through an incoming handoff entry even
though RBE can append other entries later. It still does not identify who
populated the table before RBE, authenticate that producer, prove the memory
immutable, or establish ROM/fuse precedence. Absence of another direct address
constant cannot rule out an indirect earlier writer outside or inside another
stage.

The same handoff persists into the exact FTPR CSE kernel. `FTPR.man` contains
the reversed SHA-256 of exact `kernel.met`, and `kernel.met` contains the
reversed SHA-256 of exact `kernel` bytes. The kernel is flash member
`0x120000..0x131fff`, SHA-256
`cf7dd5fc9918f96ffd2352d09a3e303471a768b3a6ee056089dd7a3d5c00bfdf`;
its metadata declares code base and main entry `0x80000`. Startup passes
`0x08200000..0x08208000` through the same page-range helper used for other
memory ranges. Its handoff iterator then:

- stores base `0x08200000` in global `0x99dec`;
- treats total size `<= 8` as empty;
- otherwise initializes entry and payload cursors at `0x08200008`;
- advances by the word at entry `+0x0e` against base plus the handoff total;
- filters on the low two state bits at entry `+0x0d`, accepting state `1`.

This closes cross-stage geometry continuity from RBE into the signed FTPR
kernel. It still does not show who populated or authenticated the table before
RBE, and the embedded manifest chain remains externally anchored only if the
incoming `ipub_key` itself is anchored.

Exact BUP exposes a matching ingestion contract. It clears list head `0xa014c`,
repeatedly calls an external reader until it returns no object, requires an
exact `0x12`-byte header, obtains total entry size from header `+0x0e`, then
requires an exact read of `total_size - 0x12` payload bytes before prepending
the materialized object. This exactly matches the FTPR kernel's sequential
entry-boundary stream geometry. The exact materializer zero-extends the u16
total and subtracts `0x12` without first requiring `total >= 0x12`; values
`0..0x11` therefore wrap the requested payload length modulo 2^32. No explicit
maximum check is observed either.

The FTPR reader does not preserve each entry boundary as a caller read
boundary. It clamps one copy to the current entry, advances to the next
accepted entry, and continues filling the same request. A state-1 entry whose
total is `0x10` or `0x11` can therefore contribute its complete 16 or 17 bytes
to BUP's 18-byte header request, with the next accepted entry contributing the
last two or one bytes. The synthesized header still contains total `0x0010` or
`0x0011`, so BUP computes payload length `0xfffffffe` or `0xffffffff` on
the exact bound reader path.

That binding is now closed. Both BUP read sites call runtime `0x659b`. The
manifest-bound FTPR `syslib` is placed at the call-compatible base `0x6000`, so
this address is raw syslib stub `+0x59b`; it jumps to raw wrapper `+0x10fb3`.
The wrapper packs BUP's first three arguments into a four-dword request, uses
selector byte zero and request size `0x10`, and calls the encoder which emits
syscall value `0x00010010` before `int 0x80`. Exact kernel dispatch takes the
high byte as a 12-byte table index. Entry zero at runtime `0x90d24` is
`{flags=5, size=0x10, handler=0x8ed23}`, and the dispatcher calls handler `+8`.
This is the exact previously analyzed FTPR read handler.

That handler validates the process buffer before calling the stream copier. Its
exact validator rejects either destination offset or requested length above
`0x01800000`; both wrapped payload lengths are therefore rejected before
stream copying, after which BUP takes its reader-error cleanup branch. The
underflow is therefore an exact bounded rejection on this artifact, not proved
memory corruption. Attacker control of the pre-RBE malformed stream remains
unproved.

BUP startup also fixes the runtime order. Main calls phase dispatcher `0x28932`
for phase zero. That phase has 22 functions at table `0x54744`; ingestion
function `0x2891a` is index 7 and the `ifp_uep` consumer at `0x32a1b` is index
10. The dispatcher calls ascending indices, after which main calls `0x3ac94`
to free every object and clear list head `0xa014c`. Thus exact BUP ingests the
runtime-object stream before resolving `ifp_uep`, copies its route header and
`0x100`-byte payload during phase zero, and only then destroys the transient
list.

The `ifp_uep` consumer does not test lookup success or payload size before its
fixed 8-byte header and `0x100`-byte payload copies. The list is built by
prepending each ingested object, while named lookup returns the first 12-byte
name match; the last ingested duplicate name therefore wins. Exact RBE appends
a fresh stock `ifp_uep` at the handoff's then-current end and allocates the
required `0x108` bytes. Therefore, if FTPR-to-BUP ordering is preserved, this
stock object is ingested after every pre-RBE same-name entry, prepended later,
and shadows it during first-match lookup. No post-RBE mutation or reordering is
proved. The unchecked consumer is thus a bounded integrity dependency rather
than a demonstrated pre-RBE duplicate override.

The reader binding proves that BUP's phase-zero materializer consumes the exact
FTPR handoff stream. It still does not establish that every later generic
`ipub_key` resolution occurs while the transient list is nonempty; list cleanup
can select the `/snowball/ipub_key` branch at a later call site. Exact
verification-call timing and snowball fallback authority therefore remain
open.

The signed NFTP `dal_sdm` module independently consumes the same persistent
namespace:

- `NFTP.man` contains the reversed SHA-256 of exact `dal_sdm.met`;
- `dal_sdm.met` contains the reversed SHA-256 of the exact compressed module;
- strict Intel-CSE-LZMA decompression yields the exact `0xe000`-byte module,
  SHA-256 `04c4f9833276bc4fe26969ba4fa195b1e330efba4d97f178987c8c4b170335ba`;
- exact code opens `/snowball/ipub_key` with flags zero and follows the content
  path only after an exact `0x24`-byte read;
- it tests object byte `+1` bit 0 and, when set, requires dword `+4` to be zero;
- the result gates later reads of one nonzero byte from `/snowball/oem_sign`
  and at most `0x1000` bytes from `/snowball/oem_key_man`.

This proves `/snowball/ipub_key` is a shared CSE policy object rather than a
BUP-only pathname. The exact paths above are reads, not a demonstrated producer
or write route. They do not establish owner writability, replay behavior, or
physical ROM/fuse authority.

A whole-image literal search finds nine byte occurrences of little-endian
`0x08200000`: five are the exact RBE lookup/append references and three are the
FTPR-kernel range/iterator references. The ninth starts one byte into PMCP dword
`0x20000000` and crosses into following dword `0xff171908`; it is not an aligned
address literal. Thus no other plain static handoff-base literal remains in the
exact 8 MiB ABL. This bounded absence does not exclude a computed address,
indirect pointer, ROM producer, or producer outside the recovered image.

Host-side parsing establishes:

- FTPR `rot.key` at flash `0x17b000`, size `0x3fc`, SHA-256
  `5530da6cbec43a441466478a6069b7a5d39afe9453f34923c633ad07b4613a14`;
- its public modulus-plus-exponent digest is
  `f2eb8fc44e30f6132631df884020abd685ce8843ee205d0a22eb6493f78a54cf`;
- its first Extension-14 record covers usage bits 0 and 1, publicly named
  `CSE BUP` and `CSE Main`, and carries that same digest;
- `rot.key`, `RBEP.man`, `FTPR.man`, and `NFTP.man` all use that exact public
  key digest and all four embedded RSA signatures verify.

Thus exact RBE binds `rot.key` to the selected runtime `ipub_key` digest before
using the RoT manifest to authorize CSE BUP/Main signing keys. The remaining
boundary has narrowed to the producer and authority of the incoming
`0x08200000` handoff: the recovered RBE consumes `ipub_key` from it but does not
show whether ROM, immutable CSE code, fuses, or another earlier authenticated
object supplies it.

Exact BUP independently exposes more of the same object contract in its generic
manifest-verification path. Global `0x000a014c` is initialized as an empty
runtime-object-list head. The object materializer prepends received objects with
payload size at `+0x14`, payload pointer at `+0x18`, and next pointer at `+0x1c`.
The resolver then applies this exact rule:

- while the list head is nonzero, resolve the named runtime object and return
  its payload pointer and size;
- only while the list head is zero, construct and read
  `/snowball/ipub_key`;
- the caller requires the resolved length to be greater than `0x23`—the value
  is runtime payload size or snowball read return count, and the comparison is
  a minimum-length check, not a selector bound;
- it then takes selector byte 0 and loads the pointer at
  `object + 4 + 4*selector`, with no observed selector upper bound or check
  that the pointer field remains within the returned object;
- exactly 32 expected-digest bytes from the selected pointer are supplied to
  the later manifest validator.

The digest `f2eb8fc4...` occurs statically in the exact 8 MiB ABL only once, in
`rot.key`'s Extension-14 record at flash `0x17b2cc`. This rules out a second
plain static copy in this image, but it does not establish which BUP resolver
branch is active or where RBE's earlier runtime object originated. In
particular, the `/snowball/ipub_key` path name alone does not prove that the
object is writable, unauthenticated, selected on this platform, or usable to
replace the root key. For the minimum accepted `0x24`-byte object, only
selectors `0..7` keep the four-byte pointer field inside the object. The absent
bound is an exact parser-integrity dependency, but attacker-controlled malformed
object reachability is not proved.

Exact `FTPR.man` contains neither the name `oem.key` nor its SHA-256 in forward
or reversed byte order, and FTPR CPD has no `oem.key.met` member. This is bounded
absence of direct coverage in that signed-package metadata, not proof that no
other authenticated CSE policy or hardware root covers `oem.key`.

## Exact BPDT type-17 UEP key-hash candidate

The exact BPDT type-17 `UEP` member is at flash `0x100210`, size `0x108`,
SHA-256 `184e01883e7f9233d5e50104a52620ec45e44c79ae3255fdeeaf8a44d5e8edc3`.
It stores the exact `oem.key` public-key digest
`9b0a59c842ba70857b595ed8115630d3a342a10c9d4437f9ff4807517693e0af`
in three records: split across offsets `+0x34` and `+0x40`, split across
`+0x7c` and `+0x90`, and contiguously at `+0xcc`.

Exact RBE creates object `ifp_uep` with size `0x108`. It reads mode nibble
`(dword[0xf6170810] >> 24) & 0x0f`; the hardware route is selected exactly when
`(nibble & 0x0c) != 0 && (nibble & 0x03) != 0`. Its source path then either
copies from hardware window `0xf6170800..0xf61708ff`, or loads BPDT type-17 UEP
with a descriptor-`+0x1000` fallback. Both flash
candidates must pass `$UEP` magic and CRC-16 checks. RBE then invokes its
bitfield extractor with input `UEP + 8`, field index `0x20`, bit length `0x100`,
and table bit offset `0x160`; the resulting 32 bytes are stored at global
`0x6048038`.

The OEM-key validation caller requires `oem.key` presence to agree with a
nonzero extracted digest. It passes the manifest and UEP digest to the exact
`$MN2` validator, which hashes the carried `0x100`-byte modulus plus four-byte
exponent, compares the result with the UEP digest, and reaches embedded RSA
verification only after equality. Extension selector `6` is validated
afterward. This proves pre-IBBL authentication of the exact stored `oem.key`
against the selected UEP field.

The current public coreboot Apollo Lake/Gemini Lake IFWI constructor's
`create_uep()` independently calls the `+0xcc` value an **OEM public-key-hash
record** and requires a 32-byte public-key hash. Exact target consumption is now
proved; the remaining boundary is whether the selected UEP source is externally
authenticated, fuse-backed, or overrideable on an installed production unit.

## Exact OEM Boot Policy chain

The same OEM public-key digest also anchors the recovered IBB package:

- `IBBP.man`, flash `0x187070`, size `0x2ec`, SHA-256
  `f224328529c3662c8c3ba490ad2a3c8143a34d0c9a531d2568f94d639058f615`,
  uses the same public key as FTPR `oem.key` and has a valid embedded RSA
  signature;
- exact BUP finds the OEM key-manifest Extension 14, selects its usage-bit-32
  record, computes the IBBP modulus-plus-exponent digest, compares it with that
  record before RSA verification, and fails closed on mismatch;
- the signed IBBP manifest contains reversed SHA-256 of `BPM.met`;
- exact BUP stages `BPM.met`, hashes it, reverses the calculated digest, and
  compares it with the signed expected value;
- `BPM.met`, flash `0x187380`, size `0xb4`, SHA-256
  `4a82dcd20e5ad30e80b11637c767a9a9140b3e570d5144cda9407390b9618738`,
  is Extension 19 and directly contains the exact IBBL and IBB SHA-256 values;
- the exact IBB SHA-256 is
  `4fba3004219bbfe3a94baa23467c7076d87f4ad76fdb6687ccdbf93455e365ed`.

This proves the recovered set's byte chain
`selected UEP digest → oem.key → usage bit 32 → IBBP.man → BPM.met → exact
IBBL and IBB`. It does not independently authenticate the selected UEP source.

## Exact selected-UEP to NFTP FPF provisioning handoff

The selected UEP also feeds a separate later provisioning path:

1. Exact RBE creates runtime object `ifp_uep` with size `0x108`.
2. On the hardware-window route RBE places marker `REAL` at object offset zero;
   on the flash route the validated `$UEP`/CRC header remains there. Both routes
   place the selected `0x100`-byte payload at offset `+8`.
3. Exact BUP resolves `ifp_uep`, copies the eight-byte header, compares its first
   dword with `REAL`, and records the result at global `0x000a4074`. A non-`REAL`
   header selects zero rather than causing a rejection in this range. BUP then
   copies the `0x100`-byte payload exactly into global `0x000a37f8`.
4. BUP's later field-assembly path can update the same shadow, so full initial
   payload byte identity at final publication is not claimed.
5. BUP metadata defines special file `bup_fpf`, major 30, minor 7. Exact BUP
   publishes `0x880` bytes from global `0x000a37f8` through that endpoint.
6. The exact NFTP `fpf` process requires an exact `0x880`-byte read from
   `/dev/bup_fpf` into shadow global `0x000366e4` and separately opens
   `/dev/flash/uep`.

The `fpf` process is itself byte-bound by the signed NFTP chain:

- `NFTP.man`, flash `0x203688`, size `0x9a0`, SHA-256
  `d89f510f91eb9191e4b1e4a1a17b4675e3823953067ded257a6d78b2fb340ea4`;
- `fpf.met`, flash `0x205f6c`, size `0x10c`, SHA-256
  `2f5ecd89cfd900abf8dda056ee19b7d373bdda7a6a1ea0092e38404268de51ec`;
- compressed `fpf`, flash `0x268000`, size `0x2a51`, SHA-256
  `40e9da01431dc7a40e82ba6a33e1ee7d9891c9ffa0cda02efb5ff56387681e47`;
- strictly decompressed `fpf`, size `0x6000`, SHA-256
  `9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9`.

`NFTP.man` contains reversed SHA-256 of exact `fpf.met`; `fpf.met` contains
reversed SHA-256 of the exact compressed module. The metadata exposes `fpf`
and `fpf_hw_use` as major-23 minors 0 and 1.

Exact `fpf` maintains hardware-mode global `0x00036f60`. Its field-read path
uses the BUP-provided shadow while that byte is zero and a hardware-access path
when it is nonzero. The callback associated with table entry `OemLock` sets the
hardware-mode byte before processing a fixed field sequence. This proves that
the selected RBE UEP is carried into later signed FPF provisioning logic. It
does **not** yet prove that NFTP's later hardware state is the producer of, or
byte-identical to, RBE's earlier `0xf6170800..0xf61708ff` hardware window.
Nor does it prove that the earlier selected UEP source is fuse-authenticated.

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

This is now an exact mismatch between the recovered ABL's runtime expected
usage-39 digest and the package IAS carried-key candidate. Exact RBE, BUP, and
IBBL bind FTPR `oem.key` byte-for-byte to the runtime FIT at `0xfef80000` and
then to the low-memory table consumed by stage 1. It is still not an
installed-unit verdict: the package may be applied under an
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

Four public sources are hash-bound and kept separate from exact-target proof:

1. Slim Bootloader commit
   `5f5c14b10ae6bd3cd0cf7e274142767dc2635a06`:
   - `BootloaderCorePkg/Include/FirmwareInterfaceTable.h`, SHA-256
     `0e0f1fff576e4edc48d2918d14bb1292526d3c01d3547d38305ea435543722ef`,
     defines 16-byte FIT entries, `_FIT_   `, type `0x0b` Key Manifest, and
     type `0x10` CSE Secure Boot;
   - `Platform/ApollolakeBoardPkg/Library/LoaderLib/LoaderLib.c`, SHA-256
     `8f4c30f671559937a660dedee4abd31a04d5cfa4425fa942b30c5aa07391cbcd`,
     defines the `0x20000`-byte SRAM remapping at `0xfffe0000` and the
     CSE-to-IBB ring-buffer copy;
   - `Platform/ApollolakeBoardPkg/BoardConfig.py`, SHA-256
     `72b04ce00e9deb24952bfb01b6a37f4da1bf290ab48f8ed469d9a28da7c96212`,
     places Stage1A at `0xfef80000`.
2. ME Analyzer commit
   `d27ccdba0aadbad490f47b5b631c369b682a7ef5`, file `MEA.py`, SHA-256
   `ed2dfb3b9efe58431609b4d3eefe6908b3124228288163dd4fd667dd17d5f4ef`.
   Its reverse-engineered CSE Extension 14 R1 entry is `0x44` bytes with a
   16-byte usage bitmap and 32-byte hash at offset `0x24`; its usage dictionary
   names bit 39 `OS Kernel`.
3. `DylanBeMe/Security-Processor-Research` commit
   `1abcfffb6fa619e135977642453f08a35c1e74bc`:
   - `ME/README.md`, SHA-256
     `8475971cb9b90aca25568becded8e02194bad4f855695a4d18b396759818e2bb`;
   - `ME/notes/09-cve-hunt.md`, SHA-256
     `c93e2faa28374f092369ce7055ebd704cb565568436cece890208c686b7ec92c`;
   - its independent CSME 11.8 analysis reports a low syslib region, a
     five-byte-stride jump PLT, and loader-generated cross-module imports. That
     is useful comparison for a later CSME generation but does not identify this
     artifact's exact import policy.
4. Positive Technologies' public `ptresearch/unME11` commit
   `fa6b4d73a53be10b199b0b87ec7d45f0e38b1333` and linked TROOPERS 2017
   presentation *Intel ME: The Way of the Static Analysis*:
   - `unME11.py` SHA-256
     `cce3a3fb7c6278b1507b9062a4c03e7f40e515cd8b8a70a34d662b840c1416df`;
   - presentation PDF SHA-256
     `c313ce296ad674b6385df954d918a10a33feba91c0b0fad461a9dad2aeba66a3`;
   - the presentation independently states that TXE v3 uses non-kernel module
     base `0x26000` and loads firmware syslib at `0x6000`. Those values match
     exact BUP and the exact call-to-raw-stub mapping, but the handler binding
     above is proved from recovered bytes rather than the public slide.

The exact proprietary instructions independently establish the target
structures and reader binding. Public names and comparative loader observations
do not prove the target's earlier authentication policy or persistent
provisioning implementation.

A current public coreboot Apollo Lake/Gemini Lake IFWI constructor provides
separate comparative corroboration:

- commit `4f3d2b564c8675a05d555d27740d62e0257cbd5c`;
- `util/apl_ifwi/apl_ifwi.py` SHA-256
  `824497f98ed0f6475b13aebd2b798244e6ab09b55349e7004496ffe9138f296a`;
- it derives one `public_hash`, passes that same value to both
  `create_oem_key_manifest(...)` and `create_uep(...)`, names the resulting
  manifest `oem_key`, and replaces FTPR CPD member `oem.key`.

That modern public constructor corroborates the persistent member's purpose but
is not evidence of exact source lineage or of the target's runtime authentication
root.

## Exact TXE identity and advisory boundary

The signed FTPR manifest itself encodes version components `3, 1, 50, 2222`,
date `0x20170926`, and TCB SVN `3`. This identifies the recovered firmware as
Intel TXE `3.1.50.2222`, independently matching the exact `0x26000` BUP and
`0x6000` syslib layout.

Intel-SA-00086 lists `3.1.50.2222` as its resolved Apollo Lake TXE production
release, so CVE-2017-5707 and CVE-2017-5710 are rejected as version-only
candidates for this artifact. Intel-SA-00125 explicitly covers TXE 3.0 through
3.1.50 and says TXE 3.1.55 replaces `3.1.50.2222`. That makes
CVE-2018-12147 an exact-version privileged-local HECI lead. Intel names
anti-replay bypass, TXE data-file tampering, and firmware rollback as
CVE-2018-3655 physical-access consequences, making persistent policy rollback a
strong lead but not proving identity with the exact `/snowball` objects.
Neither advisory proves an unprivileged Linux-root route, a reachable MEI
client, or control over the handoff, UEP, or snowball objects. Detailed source hashes and bench prerequisites are in
`intel-txe-3.1.50-advisory-applicability.md`.

## Security boundary

What is now proved:

- the runtime descriptor table is FIT-format;
- exact RBE consumes `ipub_key` from a bounded incoming runtime-object handoff
  at `0x08200000` and uses its selected 32-byte digest to pin `rot.key` before
  RSA verification;
- the RBE iterator lacks minimum-total, nonzero-progress, and remaining-header
  checks; its first append does not reject current-total addition overflow and
  can begin up to `0x13` bytes before the handoff for wrapped incoming totals;
- its `ipub_key` path lacks entry-size, selector, pointer-field, and
  selected-pointer bounds; malformed producer control remains unproved;
- `rot.key`, `RBEP.man`, `FTPR.man`, and `NFTP.man` use the same exact
  modulus-plus-exponent digest `f2eb8fc4...` and have valid embedded signatures;
- exact BUP can resolve `ipub_key` from a runtime object or
  `/snowball/ipub_key`, requires resolved length greater than `0x23`, then uses
  an unchecked byte-0 selector for the pointer at `4 + 4*selector` and passes a
  selected 32-byte digest to its manifest verifier;
- the exact root digest occurs statically only in `rot.key`; runtime branch
  selection and snowball writability/authentication remain unproved;
- RBE's `ipub_key` path looks up an existing handoff entry rather than appending
  it, and the exact manifest-bound FTPR kernel later consumes the same base,
  first-entry address, state byte, and entry-size geometry;
- exact FTPR streaming and BUP runtime-object ingestion agree on `0x12`-byte
  header, total-size-at-`+0x0e`, payload remainder, and entry boundaries;
- BUP subtracts `0x12` from the zero-extended u16 total without a minimum-size
  guard; FTPR can synthesize a complete BUP header from state-1 totals `0x10`
  or `0x11` plus the next entry; exact BUP target `0x659b` binds through syslib
  selector zero to kernel handler `0x8ed23`, whose process-buffer validator
  rejects the resulting `0xfffffffe`/`0xffffffff` request before copy;
  malformed-stream attacker control remains unproved;
- BUP phase zero ingests that transient object list at function index 7,
  consumes `ifp_uep` at index 10, and frees the list only after the phase;
- the `ifp_uep` consumer has no lookup-null or payload-size check and duplicate
  names resolve last-ingested-first, but exact RBE appends the stock `0x108`-byte
  object after all preexisting entries, so it shadows a pre-RBE duplicate when
  FTPR/BUP sequence is preserved; post-RBE mutation or reordering is unproved;
- the BUP reader-import/FTPR-kernel-function binding is exact through the
  manifest-bound syslib stub, syscall encoder, table index zero, and handler
  `0x8ed23`;
- signed NFTP `dal_sdm` reads an exact `0x24`-byte
  `/snowball/ipub_key` policy object before OEM authorization objects, but no
  producer or write path is proved;
- all plain little-endian `0x08200000` byte occurrences in the exact ABL are
  classified as RBE/FTPR consumers or one unaligned cross-dword PMCP match;
- the pre-RBE handoff producer, authentication, mutability, computed/indirect
  paths, and ROM/fuse authority remain unproved;
- exact FTPR signed-package metadata has no direct `oem.key` name/digest entry
  and FTPR CPD has no `oem.key.met` member;
- exact BPDT type-17 UEP contains three copies of the stored `oem.key` public-key
  digest, and exact RBE extracts the 256-bit OEM-key field to global
  `0x6048038`;
- exact RBE pins the `oem.key` modulus-plus-exponent digest to that UEP field
  before embedded RSA and Extension-14 validation;
- exact BUP selects OEM usage bit 32 to pin and verify `IBBP.man`, verifies its
  signed `BPM.met` hash, and verifies the metadata's exact IBBL/IBB hashes;
- UEP source authentication and hardware/fuse precedence remain open;
- exact RBE publishes its selected UEP as `ifp_uep`; exact BUP distinguishes a
  hardware-route `REAL` header from the flash-route header without rejecting the
  latter, copies the payload, and publishes `0x880` bytes as `bup_fpf`;
- the signed NFTP `fpf` module consumes that exact-size input and switches its
  field reads between the BUP shadow and a later hardware-access mode;
- NFTP's later FPF hardware state is not yet equated with RBE's earlier hardware
  window;
- exact CSE RBE copies FTPR `oem.key` at its exact source length into
  `oem_key_man`, with a matching manifest-length check;
- exact CSE BUP constructs a FIT type-`0x0b` entry from `oem_key_man` and
  publishes payload address `0xfffe1000`;
- exact CSE BUP couples names `oem.key` and `oem_key_man` in its key resolver;
- exact BUP places the `0x4000`-byte IBBL at SRAM alias `0xffffc000`;
- exact BUP streams the resolved `IBB` member through four `0x8000`-byte SRAM
  slots under a hardware handshake;
- exact IBBL consumes that four-slot ring through PCI configuration space and
  copies IBB into destination `0xfefbd900` with capacity `0x38000`;
- hash-bound public Apollo Lake host code independently matches the exact
  producer/consumer chunk-count, size, ring-state, slot-index, source, and
  acknowledgement fields bit for bit;
- IBBL's static descriptor relocates its own exact bytes to `0xfeffc000`;
- BUP's pointer at buffer offset `0x1ffc0` survives that self-relocation, and
  exact IBBL uses it to copy the FIT from `0xfffe0000` to `0xfef80000`;
- IBBL later copies that FIT from `0xfef80000` to `0xc10c0`;
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

- whether an installed unit executes this exact RBE/BUP/ABL set rather than a
  different installed manifest or firmware generation;
- whether CSE, Boot Guard, an ACM, ROM, physical FPFs, or another earlier stage
  authenticates or overrides the selected UEP source;
- whether BUP ever selects `/snowball/ipub_key`, how that internal object is
  authenticated, and whether its contents can differ from RBE's earlier runtime
  `ipub_key`;
- the exact producer and immutable provenance of RBE's `0xf6170800` hardware
  window, despite the now-proved later BUP/NFTP provisioning handoff;
- the actual runtime expected digest on an installed unit, although the exact
  recovered set now proves `9b0a59...` as its own runtime expected value;
- any writable or replaceable provenance path;
- custom-image acceptance, boot acceptance, root, persistence, health,
  mark-good, rollback, or recovery.

The exact package carried-key candidate remains
`437008c1b26fd821a7c7c0ec855aaba5587f62deaaa98d9b2fcbf6ad4179aa06`.
Its mismatch with the exact recovered set's runtime usage-39 record is proved.
Whether that mismatch affects the owner's unit remains bounded by installed
ABL/RBE/BUP/UEP identity and update-component selection.

## Reproduction

```sh
<platformio-env>/bin/python3 tools/uk_fw/abl_ias_key_provenance.py \
  --update-archive work/decrypted-eu-260128/HU/firmware/update.tar.gz \
  --sbl-repo work/online-slimbootloader-20261110 \
  --mea-repo work/online-meanalyzer-20261111
```

Tracked deterministic evidence:

- `evidence/artifacts/update-candidates/abl-ias-key-provenance.json`
  - size `65,471`
  - SHA-256 `fbb502a9fc0a7de410c209f91aee382b9008b74e860b72edc9b6c40a480ec558`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `122,227`
  - SHA-256 `09e04891ef801085750c1445773901c917682e858ad1c10bc971428a3a2d5c52`

The analyzer is read-only with respect to all inputs. It does not execute an
updater, bootloader, target helper, image constructor, firmware image, or target
binary and does not produce a modified image, signature bypass, flash procedure,
or persistence mechanism.
