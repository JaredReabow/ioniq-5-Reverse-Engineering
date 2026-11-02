# Intel TXE first-fixed and later-version module comparison

## Scope and conclusion

The official ASUS X541NA BIOS archive now supplies an exact Apollo Lake TXE
**3.1.55.2269** image at Intel-SA-00125's first unaffected `3.1.55` boundary.
A public Intel NUC capsule separately supplies later **3.1.94.3086**. This closes
the previous first-fixed artifact gap and permits a three-way signed-module
comparison against the EU ABL's affected **3.1.50.2222** image.

The first-fixed result excludes two previously open theories and identifies one
new exact candidate:

- the complete affected and first-fixed HECI modules are byte-identical after
  normalizing only 369 external `rel32` call/jump immediates, each of which
  shifts its target by exactly five bytes;
- the complete affected and first-fixed busdrv modules are likewise identical
  after normalizing only 96 external `rel32` call immediates to 26 syslib
  import stubs, again shifted by exactly five bytes;
- all 42 syslib destination bodies directly imported by those HECI branches
  are byte-identical after normalizing 37 reviewed `rel32` address operands
  and one indexed-jump-table base operand;
- all 29 new internal first-level callees reached by the 96 reviewed direct
  calls from those bodies are likewise identical after reviewed address
  normalization;
- the named RBE/OEM-key-manifest/microcode anti-rollback FPF fields seen in
  `3.1.94` are absent by name from both affected and first-fixed FPF; and
- first-fixed VFS newly opens the already defined `ndl_critical` and
  `ndl_counting` storage channels, then passes both descriptors to a new
  syslib thread-context setter.

Therefore the later HECI header/extended-parser changes and named FPF fields
are not the `3.1.55` fixes. The VFS/syslib NDL hookup is a high-priority exact
candidate for CVE-2018-3655's anti-replay/data-integrity repair, but exact
transaction semantics, physical reachability, and advisory attribution remain
unproved. CVE-2018-12147 still requires changed-function and reachability
analysis in indirect dispatch targets, deeper syslib callees, kernel/service
implementations, another signed module, or downstream signed clients; local
busdrv opcodes and non-address data are now excluded too.

No firmware module, MEI/HECI endpoint, update capsule, or target executable was
run. All work was passive host-side parsing, strict decompression, hashing,
embedded-signature verification, disassembly, and decompilation.

## Official first-fixed artifact provenance

ASUS's current X541NA support page lists BIOS `321`, release date `2018-11-13`,
and serves:

- URL: `https://dlcdnets.asus.com/pub/ASUS/nb/X541NA/X541NAAS321.zip`;
- downloaded ZIP size: `5,742,372` bytes;
- ZIP SHA-256:
  `26819e607f0ee9a9fd3b26518c9f9efa2c2e05bcca2a460992311826e603e1b7`;
- sole ZIP member: `X541NA-AS.321`, size `8,390,656` bytes, internal timestamp
  `2018-08-24 18:18`;
- member SHA-256:
  `bfc75d03e113184b84078a00f09be75779e80c6d0d14fb2f63dba350e31690c6`;
- 8 MiB IFWI after the `0x800`-byte capsule prefix, SHA-256:
  `db9325168976e1e68cba25924e82c2aeb2db85fb7a678de5fd66e200ab7643b9`.

ME Analyzer and the independently parsed, validly self-signed NFTP manifest
identify TXE `3.1.55.2269`, date `2018-07-16`, and TCB SVN `3`. The outer image
also contains build/version `3.1.55.2270` dated `2018-08-24`; module comparison
is bound to signed NFTP `3.1.55.2269`.

For neighboring official provenance, ASUS BIOS `318` from `2018-05-08` contains
signed NFTP `3.1.50.2238`, while BIOS `323` from `2019-06-06` retains signed
NFTP `3.1.55.2269`. Their archive and extracted identities remain under ignored
`work/`; the canonical first-fixed input is BIOS `321` above.

## Later public artifact provenance

Internet Archive item:

- item: <https://archive.org/details/ay-0076>;
- downloaded file: `AY0076.bio`;
- size: `11,841,568` bytes;
- SHA-1: `8e9feff09ea65840388b2116349ccb8185e3214a`;
- SHA-256: `ab8caa3fe9e5b3d14afb765e6a806d48d5918d21d85c3bff083b6b17ea4e7ec2`;
- captured Archive metadata JSON SHA-256:
  `c0d6eb024713980071b52307877b145d5a683821e1386054edfb0a40c7ecac55`.

The Archive metadata identifies creator `INTEL`, title “NUC6CAYH BIOS 0076,”
and the retired Intel download page
`https://www.intel.com/content/www/us/en/download/18820/bios-update-ayaplcel.html`.
The capsule itself contains `AYAPLCEL.86A.0076.2023.0710.1018`. This is public
provenance, not a claim that the current Intel site still serves the file or
that the Archive uploader is an authoritative distribution channel.

`uefi-firmware-parser` exposed the authenticated-capsule firmware volume. Its
large compressed FFS member
`file-a80ba8f1-a1ba-4dc2-9953-56190495826f/section0/section0.raw` yielded:

- extracted full IFWI size: `16,773,120` bytes;
- SHA-256: `75a866331d8f23d023bbdcf9efdfee7b57bf4727eb50f6162940a2a51cb57b4a`.

ME Analyzer v1.312.0 r378, run under a pseudo-TTY, reports:

- family: CSE TXE;
- version: `3.1.94.3086`;
- date: `2023-01-02`;
- TCB SVN: `3`;
- ARB SVN: `7`;
- VCN: `112`;
- chipset support: Apollo Lake;
- production-ready, OEM-configured extracted image.

The signed NFTP manifest independently encodes version `3.1.94.3086` and date
`2023-01-02`; its embedded RSA signature verifies.

A separate current MrChromebox `reef` full ROM was also resolved and checked:

- filename: `coreboot_edk2-reef-mrchromebox_20261027.rom`;
- size: `16,777,216` bytes;
- SHA-1, matching its sidecar:
  `c03750a3fbbea57ce7a72fa855c1912481afe233`;
- SHA-256: `b34bc938f5533a1876ee1463036d9d580d06fe45a9b0005998007af1ef91230d`.

Despite the modern coreboot release date, its TXE region remains
`3.1.50.2237/3.1.50.2238` and carries the already known byte-identical HECI,
busdrv, and syslib modules. It is useful independent occurrence evidence but
not a fixed-version diff.

## Deterministic signed-chain comparison

`tools/uk_fw/txe_fixed_module_diff.py` consumes only the exact affected ABL,
official first-fixed ASUS IFWI, and extracted later NUC IFWI. It:

1. opens stable regular-file descriptors with no-follow semantics;
2. validates the expected FTPR and NFTP CPD structures;
3. extracts `FTPR.man`, `NFTP.man`, module metadata, and module bytes;
4. verifies each embedded `$MN2` RSA signature;
5. verifies `manifest → reverse-SHA-256(metadata)` and
   `metadata → reverse-SHA-256(compressed module)` bindings;
6. strictly decompresses Intel CSE LZMA members, requiring EOF, no unused data,
   and the exact declared size; and
7. compares decompressed HECI, busdrv, storage, policy, fpf, dal_sdm, VFS, and
   syslib identities.

Reviewed report:

- path: `evidence/artifacts/update-candidates/txe-fixed-module-diff.json`;
- schema: `ioniq-txe-fixed-module-diff/v5`;
- size: `125,543` bytes;
- SHA-256: `ed7f9ee0f93d1afa3a353560fe034510ceacc303fa3589405341bb0f62e5171f`.

Reviewed byte-free disassembly/decompiler excerpts are retained as:

- path: `evidence/artifacts/update-candidates/txe-fixed-heci-exact-static.txt`;
- size: `15,113` bytes;
- SHA-256: `cef4f22d92995e44e18eb75fa024bf6e936581a67d5b8c31cb73bf3029a1cbf3`.

The exact decompressed identities are:

| module | affected `3.1.50.2222` SHA-256 | first-fixed `3.1.55.2269` SHA-256 | later `3.1.94.3086` SHA-256 | sizes |
|---|---|---|---|---:|
| HECI | `82b7be7bb8069aebfb2c9f7a0e994500fe10d631e67a16f5a5fec71d29679125` | `16afeb7e9a9328bd22b5c8b383b5e003bcce2e4d46db18ea1737606bffa3ed31` | `04dceeb0b42db7910d913545b9b2342e9a26349c8e9d2e2bede201af62bf3b8f` | `0x9000 / 0x9000 / 0x9000` |
| busdrv | `f226a92dd219a020bca96aeca3b54d8b0870f230128b7cb206c3389d5096ad21` | `0e995c76f16f1f86240f85416059ca32e5c6fd0155eb1d3132b90505e8646fc0` | `9ca422bdab58503743f9c28ddaef42e73b375947c56934057abe1a2627b5180c` | `0x6000 / 0x6000 / 0x6000` |
| storage | `e7496ebc6f2c8d56ef80f77f8c5638457e1150d57e9afe39887c1c7a5b735ec7` | `e24219876ea4bab8640387b6ffaf5ab72d4617de8c484e0294408cb761ff153e` | `de773f376beec0e44f7ca60547b1e5a71c1d967672decad34022f882b2cfb871` | `0x11000 / 0x11000 / 0x11000` |
| policy | `ce25f7a1dc6e6aa4d33d60801a653e36cee0338ba60b3143c596d44ca278c49b` | `5cc5297c5e117f9d6a7549445ae361a38574c836bf5a402d7620b73d1b5908a0` | `5de19a139270b6b7f17b6e793868ff98a470255fcf6d5363c14df6cc4347ff7c` | `0xc000 / 0xc000 / 0xc000` |
| fpf | `9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9` | `e8f635d1ae1db00fb686fcacece4f2684109b9b8a32f852bc00f383218f784b8` | `2c188d8f1c0ee1a0eab08e716599149b370305033d2435c3745c7f399909713d` | `0x6000 / 0x6000 / 0x6000` |
| dal_sdm | `04c4f9833276bc4fe26969ba4fa195b1e330efba4d97f178987c8c4b170335ba` | `128944632790d729691b4297d712a30a76905089bc9d7068848a0c847e18f1cf` | `e68257a6bad5215343bc9e778653c7afab374396251a99883762abb1f5bea6cb` | `0xe000 / 0xf000 / 0x10000` |
| vfs | `59b0ee9381860d1700f6c4638b0e165e3dba27d97d5017b8118b82a18f77f91b` | `52e0773d3115581d16b039e7c7e65c5dcbddf9d332cd98bdc9bb1ab6f6ff9e68` | `c5775a79d72c6f6d35656d6cd56a2648a17093f8436809b309d44229f107bc3b` | `0x1d000 / 0x1f000 / 0x1f000` |
| syslib | `dba068b882c11783af4e2c0b7911b3a0db90f9b22808f42ac3e8768e2dda961c` | `1f4722eeaab64eee5b6febe1b7e6d21565794c929173a56ff4bb9a01f96b00c8` | `d0f68eb4c9096ef6d7ed0c3046404b2b70efce9c7b4d065b8dde29f3bde0dfdd` | `0x13000 / 0x13000 / 0x13000` |

Every selected module changed by the first-fixed release, so even the
`3.1.50 → 3.1.55` release is not a single-function patch. Exact range-level
comparison is required.

## Exact affected-to-first-fixed HECI result

Affected and first-fixed HECI are both `0x9000` bytes at code base `0x26000`.
The deterministic comparison verifies three exact primary-path ranges:

| range | affected SHA-256 | first-fixed SHA-256 | raw differing bytes |
|---|---|---|---:|
| dispatcher `0x277c8..0x27dc9` | `89d34094c7c72571ae5a5790b95c1570a81acc31a48105aa0092fb3017f05dc7` | `203b2c1b83c63e939cd73d451a9656ae21544c2ce875842506c928e99bfa128b` | 18 |
| FIFO copy `0x2868d..0x287b7` | `d8df2a82e6f71db82616c63898b8e3a3cb46cf4bb524ae5bd93d573ad889e362` | `99811a48487433d89db5ce8eaa90fd74c7be94f1a45577e73adcea88003159d8` | 2 |
| payload consumer `0x28a2d..0x28e78` | `5c77d1e0db46ff8847d0a232ef6efa074767d5fe24aaa41727f595997831c419` | `b5079daa3220f61e3eea68fefc12fdc3cdd7477cd6ac67a1fd236c5fbbf7f7fc` | 12 |

Every one of the 32 raw differences in these ranges lies inside one of 31
enumerated `rel32` call immediates. At every call, the first-fixed displacement
is affected+5. After zeroing only those exact four-byte immediates, each range
is byte-identical.

The module-wide result is stronger: all 377 raw differing bytes across the
complete `0x9000`-byte HECI module lie inside 369 same-offset external `rel32`
encodings—366 calls and three tail jumps—to 42 affected targets spanning
`0x6460..0x67b2`. Every first-fixed target is affected+5. Zeroing only those
selected immediates makes the complete affected and first-fixed HECI modules
byte-identical. No HECI-local opcode or data byte changed.

The first-fixed dispatcher also retains the exact affected behavior:

- nine-bit payload extraction and rejection above `0x1fc`;
- top-header-byte mask `0x80`, testing only complete bit 31;
- aligned control geometry `4..8`; and
- no later bit-29 rejection, bit-28-on-control rejection, 40-byte control
  maximum, or extended-header parser.

This excludes HECI-local code as the location of CVE-2018-12147's `3.1.55`
fix.

## Exact affected-to-first-fixed busdrv result

Affected and first-fixed busdrv are both `0x6000` bytes at code base `0x26000`.
They have SHA-256 identities
`f226a92dd219a020bca96aeca3b54d8b0870f230128b7cb206c3389d5096ad21`
and
`0e995c76f16f1f86240f85416059ca32e5c6fd0155eb1d3132b90505e8646fc0`.
Across the complete modules:

- 97 raw bytes differ;
- all differences lie within 96 same-offset call `rel32` encodings;
- those calls reference 26 affected external syslib import stubs spanning
  `0x6465..0x67ad`;
- every first-fixed target is its affected target plus five; and
- zeroing only those selected call displacements makes both complete modules
  byte-identical.

Thus no busdrv-local opcode or non-address-data byte changed at the first-fixed
boundary. This excludes busdrv-local code as the direct CVE-2018-12147 fix,
without excluding changed transitive syslib or kernel services, another signed
module, or downstream clients.

## Exact HECI-imported syslib destination result

The 42 affected HECI external targets are syslib export stubs at
`0x6460..0x67b2`. The corresponding first-fixed stubs are each at affected+5.
Directly decoding every affected/fixed `jmp rel32` stub resolves 42 unique
syslib destination bodies. Their entry-address movement is structural rather
than a logic signal:

- 33 destination entries move by `+5`;
- two move by `+8`; and
- seven move by `+34` (`0x22`).

The deterministic report binds each affected and first-fixed runtime range,
raw range hash, HECI reference count, and normalized range hash. Across the 42
next-entry-bounded bodies:

- `4,410` body bytes are reviewed;
- only `39` raw bytes differ;
- 37 same-relative-position `call/jmp rel32` operands account for all but one
  changed address operand;
- the remaining changed operand is the indexed-jump-table base
  `0x18994 → 0x189b8` in body `0x6abc..0x6fbf`; and
- after zeroing only those reviewed address operands, all 42 body pairs are
  byte-identical.

The changed `rel32` targets are themselves restricted to reviewed address
translations: unchanged kernel/syscall gates `0x102e` and `0x103d`, or syslib
locations moving by `+5`, `+8`, or `+34`. Therefore none of the 42 directly
imported bodies contains an affected-to-first-fixed opcode or non-address-data
change.

The 42 bodies contain 105 raw `0xe8` bytes. Full linear instruction review
classifies 96 as direct-call boundaries and nine as incidental operand/data
bytes. The 96 calls resolve to 33 target pairs:

- 12 references to unchanged external gates `0x102e` and `0x103d`;
- six references to already reviewed syslib bodies `0x7972` and `0x118b0`; and
- 78 references to 29 new internal first-level callees.

The 29 new next-entry-bounded callee bodies add another `3,911` reviewed bytes.
Their 34 raw differing bytes are wholly contained in 29 reviewed `rel32`
address operands and four indexed-table base operands. All 29 pairs become
byte-identical after only those operands are normalized. This excludes an
opcode or non-address-data change in the directly imported bodies and their
new direct first-level callees.

This materially narrows CVE-2018-12147, but does not identify its fix. Indirect
calls/jumps, indexed dispatch targets, deeper callees, kernel/service handlers
behind `0x102e`/`0x103d`, another signed module, and downstream HECI clients
remain open. Address normalization proves bounded body identity, not end-to-end
behavioral identity.

## Exact first-fixed VFS/syslib NDL integration

The signed affected and first-fixed `storage.met` both already define special
files `ndl_critical` (minor `32`) and `ndl_counting` (minor `33`). The affected
VFS, size `0x1d000`, contains neither corresponding `/dev/` path. First-fixed
VFS grows to `0x1f000` and contains exactly one occurrence each of:

- `/dev/ndl_critical` at runtime address `0x37224`; and
- `/dev/ndl_counting` at runtime address `0x37236`.

First-fixed VFS initializer `0x3655f..0x365aa`, SHA-256
`fe4f7355232906a4402174f535a32b292b0c263c8c1552f00e42cb6bc319c675`,
opens both paths. It preserves failure as negative descriptors and calls syslib
stub `0x6451` with both results at `0x3659c`.

That syslib slot changed materially. Affected stub `0x6451` targets `0x16689`.
First-fixed stub `0x6451` instead targets new function `0x16691..0x166ab`,
SHA-256
`31433029861d3307d6f82d871b5356220452e18f390306d408ea1abb0256920c`.
The function obtains a thread-context structure, sets flag bit `0x04` at byte
`+1`, and stores the two arguments at offsets `+4` and `+8`. The displaced
legacy export is retained at the newly inserted next stub `0x6456`, targeting
`0x166ab`. VFS calls both the shifted legacy stub and the new setter during its
conditional initialization path.

First-fixed VFS also adds a 25-pointer critical-name table at
`0x37154..0x371b8`, SHA-256
`dd0ed2254567b2c42599b10f00890e8b387b936905cc02bfbecb8421c5dde693`.
It covers `fTDisClear`, `fTReadOnly`, `fTEnrsHier`, five RSA key-cache names,
`pr_tee_clock`, LSPCON/HDCP/WiDi/Widevine state, ten `widi_km` names, and
`pnd_m4_msg` (with `wv_gen_num` referenced twice). Classifier
`0x33b0a..0x33b6b`, SHA-256
`cf68f0c685de3283670936fe1c3cfbe8e2e19c525b61663891b08a807fb4a42d`,
copies the 100-byte pointer array to a local buffer and performs 25 bounded
12-byte comparisons. Affected VFS contains corresponding names within full
paths but lacks this bare pointer-table representation.

This is an exact first-fixed integration change, not merely a string lead: VFS
begins consuming two pre-existing NDL storage channels and registers both
descriptors in syslib thread state. The `critical`/`counting` names and exact
first-fixed timing make it the strongest current CVE-2018-3655
anti-replay/data-file-integrity candidate. They do **not** yet prove the NDL
transaction grammar, monotonic-counter semantics, power-loss behavior,
attacker-controlled producer, physical-interface reachability, or exact
advisory attribution.

## Exact later HECI receive-path changes

The later HECI retains code base `0x26000`. The reviewed instruction ranges are
hash-bound in the JSON report, including:

- receive dispatcher `0x2789a..0x27ef8`, SHA-256
  `4aea1addeb7e4e4fef929be25f3eb879a0114673e7572ec8c4b1d9dcff03fe64`;
- FIFO copy `0x287da..0x288d5`, SHA-256
  `5b8eafc086806a31c4d8adff2fd079d65b6ab205bd09a730cb7e252df7efa764`;
- payload consumer `0x28b46..0x29052`, SHA-256
  `6ef9be6f6d5d37d30dfab717dd8651118a7e8510ccce8455c72d83c473019d9e`;
- new extended-header parser `0x29ad2..0x29c0a`, SHA-256
  `f3ed29ecdcd43505ac0824e7b4762bde7bc29c477747a891f5646cb5a3e49e42`.

Compared with affected HECI dispatcher `0x277c8..0x27dc9` and payload consumer
`0x28a2d..0x28e78`, the later exact code:

- retains the nine-bit payload expression and rejects values above `0x1fc`;
- adds an explicit rejection of bit 29 before payload dispatch; later public
  MEI source names that bit `dma_ring`;
- for control messages, now requires `(top_header_byte & 0x90) == 0x80`, which
  requires bit 31 and rejects bit 28; later public MEI source names bit 28
  `extended`;
- expands aligned control-message geometry from `4..8` bytes to `4..40` bytes,
  so the later path is not merely a tightening of every bound;
- recognizes bit 28 on ordinary messages as an extended-header indicator;
- routes that extension through new parser `0x29ad2`;
- checks the encoded extension size against both the nine-bit payload and the
  `0x1fc` destination capacity;
- requires the recovered extension to have exact single-entry geometry before
  subtracting its dword count from the ordinary payload length; and
- retains client lookup, connection lookup, maximum-message-size checks,
  remaining-capacity checks, and a `0x1fc` local destination for the primary
  ordinary-fragment copy.

## Public MEI protocol lineage for bits 28 and 29

Public Linux source explains the later field names without proving proprietary
source identity:

- Linux v4.1 `drivers/misc/mei/hw.h`, SHA-256
  `b76d30a8e3f7bdbf537c3f56654f8aef76ae92bf47405e17b5ab106f1a814102`,
  defines nine length bits, five reserved bits (25..29), `internal` bit 30, and
  `msg_complete` bit 31;
- upstream commit `ee7aba5aba70dd98fc05697723167ebb858e7aba` dated
  `2018-07-31` defines command `0x12` and the 40-byte DMA-ring setup request;
  captured patch SHA-256
  `005bfdc48f35578b07f18695b66c7da5696d92974acceab1de7966a60f2f55a4`;
- upstream commit `9d89ddfc624649e200aeec57912635dbe259d07b` dated
  `2018-07-31` names bit 29 `dma_ring`; captured patch SHA-256
  `a395cafe4dd79a18d44a57b975691f2e6a9e3226a38022f493b0ed060ecba3b7`;
- upstream commit `e5cab1f974f2bfc286ad17d7839a569c79bb7c70` dated
  `2020-08-18` defines command `0x13` for the HBM capability handshake;
  captured patch SHA-256
  `ff146123b1cd029642bc9d6685a2ed034878809b45e97a4e38da0b57183d6693`;
- upstream commit `0cd7c01a60f850987e727b8f08683ace9546eac0` dated
  `2020-08-18` adds bit 28 `extended` plus a variable-length metadata/TLV header,
  initially for virtual tags; captured patch SHA-256
  `a1b7ba5cf27a15bbb276a69775ca707f10bd962fc8afde839678f8c8cb8f10cf`.

The later proprietary control dispatcher handles new command values `0x12` and
`0x13`, and its widened 40-byte maximum exactly accommodates the public DMA
setup request. Its exact single type-1 extension entry and returned two-byte
value are structurally consistent with public vtag extension handling. These
matches provide a protocol-evolution explanation for much of the
`3.1.50 → 3.1.94` delta, not proof of shared source or an advisory fix.

The recovered stock `mei.ko` closes the ordinary transmit side more strongly.
In exact `.text` range `0x4db1..0x4dd1`, SHA-256
`94cb14162af5acbd6b17cc7db5d000d2d2bf18805dcae3b1bfde2b9c2e35b831`,
its header-byte construction applies mask `0x41`, preserving/rebuilding only
the ninth length bit and internal bit while clearing full-header bits 25..29;
message-complete is set separately. The exact stock path therefore emits
neither later `extended` bit 28 nor `dma_ring` bit 29. Ordinary `/dev/mei`
payload writes do not give the caller those transport-header bits. Any
privileged direct-hardware route remains a separate unproved reachability
question.

These are real exact deltas in a later unaffected release, but the first-fixed
comparison now proves they postdate `3.1.55` and are not the primary-path
SA-00125 fix. The widened control set and extension format align with later
public protocol evolution. Separate first-fixed changes elsewhere still
require exact function-level analysis.

## Exact later FPF anti-rollback schema fields

The signed later FPF contains six structured field records whose names do not
occur in either the exact affected or exact first-fixed FPF:

| later field | record file offset | encoded width | encoded inclusive bit range |
|---|---:|---:|---:|
| `RbeArbEn` | `0x51c4` | 2 | `0x0a0..0x0a1` |
| `OemKmArbEn` | `0x51f0` | 2 | `0x0a4..0x0a5` |
| `UcodeArbEn` | `0x537c` | 2 | `0x0c8..0x0c9` |
| `RbeArbSvn` | `0x5694` | 12 | `0x280..0x28b` |
| `OemKmArbSvn` | `0x56c0` | 20 | `0x28c..0x29f` |
| `UcodeArbSvn` | `0x56ec` | 14 | `0x2a0..0x2ad` |

The deterministic tool validates each exact 44-byte record by name, width,
encoded bit range, and SHA-256, and requires zero occurrences of all six names
in affected FPF SHA-256
`9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9`
and first-fixed FPF SHA-256
`e8f635d1ae1db00fb686fcacece4f2684109b9b8a32f852bc00f383218f784b8`.
This proves a later schema capability for explicit RBE, OEM key-manifest, and
microcode anti-rollback enable/SVN fields and proves those named records were
**not** the `3.1.55` fix. It does not establish when they appeared, whether a
corresponding physical FPF was burned on the public NUC or target, or what
exact storage/anti-replay defect CVE-2018-3655 repaired.

## Storage and anti-replay boundary

The exact later `storage`, `policy`, `fpf`, `dal_sdm`, and syslib modules all
differ, `dal_sdm` grows by `0x2000`, and later `policy` adds the literal
`/dev/nvm_handoff`. This provides concrete material for future
`/snowball/pm_ctxt`, `ipub_key`, `oem_sign`, `oem_key_man`, and handoff
comparison. It does not yet show:

- which module or persistent object was affected by CVE-2018-3655;
- whether Intel's “data file integrity” wording refers to `/snowball`;
- a physical transaction, rollback sequence, or anti-replay record format;
- host or owner write authority; or
- any path to replace an OEM key, UEP, manifest, or boot policy.

## Current classification

- An official, hash-bound, signed first-fixed TXE `3.1.55.2269` image and a
  later `3.1.94.3086` image are now available.
- The affected and later primary HECI paths both reject a simple payload length
  above `0x1fc`; no direct oversized nine-bit stack copy is observed.
- The entire first-fixed HECI module differs only in 369 external `rel32`
  immediates and retains affected HECI-local code and data exactly after that
  relocation normalization.
- The entire first-fixed busdrv module differs only in 96 external `rel32` call
  immediates and likewise retains affected local code and data after reviewed
  relocation normalization.
- The later HECI adds exact header-bit validation and bounded extension parsing,
  proving those changes postdate the first-fixed release.
- The later FPF adds explicit RBE, OEM key-manifest, and microcode anti-rollback
  enable/SVN schema records absent by name from affected and first-fixed FPF.
- CVE-2018-12147's exact defect remains unidentified.
- CVE-2018-3655's exact storage/anti-replay defect remains unidentified.
- No exploit, malformed request, HECI message, flash image, or persistence
  mechanism was created or executed.
