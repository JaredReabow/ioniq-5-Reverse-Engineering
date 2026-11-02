# Intel TXE later-version module comparison

## Scope and conclusion

A public Apollo Lake Intel NUC BIOS capsule has now supplied a hash-bound,
strictly extracted TXE image newer than Intel-SA-00125's first unaffected
`3.1.55` boundary. The recovered image is **TXE 3.1.94.3086**. This closes the
previous “no fixed-version artifact” gap and permits an exact signed-module
comparison against the EU ABL's affected **3.1.50.2222** image.

It does **not** identify either advisory defect. Version `3.1.94` is years newer
than the first fixed `3.1.55` release and contains many intervening changes.
The exact HECI differences described below are candidates for further study,
not attribution to CVE-2018-12147. Changed storage and policy modules likewise
do not identify CVE-2018-3655's anti-replay/data-file-integrity defect.

No firmware module, MEI/HECI endpoint, update capsule, or target executable was
run. All work was passive host-side parsing, strict decompression, hashing,
embedded-signature verification, disassembly, and decompilation.

## Public artifact provenance

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

`tools/uk_fw/txe_fixed_module_diff.py` consumes only the exact affected ABL and
extracted later IFWI. It:

1. opens stable regular-file descriptors with no-follow semantics;
2. validates the expected FTPR and NFTP CPD structures;
3. extracts `FTPR.man`, `NFTP.man`, module metadata, and module bytes;
4. verifies each embedded `$MN2` RSA signature;
5. verifies `manifest → reverse-SHA-256(metadata)` and
   `metadata → reverse-SHA-256(compressed module)` bindings;
6. strictly decompresses Intel CSE LZMA members, requiring EOF, no unused data,
   and the exact declared size; and
7. compares decompressed HECI, busdrv, storage, policy, fpf, dal_sdm, and syslib
   identities.

Reviewed report:

- path: `evidence/artifacts/update-candidates/txe-fixed-module-diff.json`;
- schema: `ioniq-txe-fixed-module-diff/v1`;
- size: `20,002` bytes;
- SHA-256: `668eb1ed65e8da20172de3aaa2260cb088ae1095dc4a5b7066ff13814ee636d6`.

Reviewed byte-free disassembly/decompiler excerpts are retained as:

- path: `evidence/artifacts/update-candidates/txe-fixed-heci-exact-static.txt`;
- size: `5,840` bytes;
- SHA-256: `237bab9d1108085a78c093bec2a7ab420ff37db6d6e6ddc988130bea88e98b82`.

The exact decompressed identities are:

| module | affected `3.1.50.2222` SHA-256 | later `3.1.94.3086` SHA-256 | old/new size |
|---|---|---|---:|
| HECI | `82b7be7bb8069aebfb2c9f7a0e994500fe10d631e67a16f5a5fec71d29679125` | `04dceeb0b42db7910d913545b9b2342e9a26349c8e9d2e2bede201af62bf3b8f` | `0x9000 / 0x9000` |
| busdrv | `f226a92dd219a020bca96aeca3b54d8b0870f230128b7cb206c3389d5096ad21` | `9ca422bdab58503743f9c28ddaef42e73b375947c56934057abe1a2627b5180c` | `0x6000 / 0x6000` |
| storage | `e7496ebc6f2c8d56ef80f77f8c5638457e1150d57e9afe39887c1c7a5b735ec7` | `de773f376beec0e44f7ca60547b1e5a71c1d967672decad34022f882b2cfb871` | `0x11000 / 0x11000` |
| policy | `ce25f7a1dc6e6aa4d33d60801a653e36cee0338ba60b3143c596d44ca278c49b` | `5de19a139270b6b7f17b6e793868ff98a470255fcf6d5363c14df6cc4347ff7c` | `0xc000 / 0xc000` |
| fpf | `9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9` | `2c188d8f1c0ee1a0eab08e716599149b370305033d2435c3745c7f399909713d` | `0x6000 / 0x6000` |
| dal_sdm | `04c4f9833276bc4fe26969ba4fa195b1e330efba4d97f178987c8c4b170335ba` | `e68257a6bad5215343bc9e778653c7afab374396251a99883762abb1f5bea6cb` | `0xe000 / 0x10000` |
| syslib | `dba068b882c11783af4e2c0b7911b3a0db90f9b22808f42ac3e8768e2dda961c` | `d0f68eb4c9096ef6d7ed0c3046404b2b70efce9c7b4d065b8dde29f3bde0dfdd` | `0x13000 / 0x13000` |

Every compared module changed. This is not a minimal security-patch diff.

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

These are real exact deltas in a later unaffected release and strengthen the
case for studying header-state validation rather than a simple oversized
fragment. They do not establish that the old handling of bits 28/29 was
security-sensitive, host reachable, or CVE-2018-12147. The widened control
message set and new extension format may reflect ordinary protocol evolution.
Only a first-fixed `3.1.55` image or an intermediate-release bisect can separate
security fixes from later feature work defensibly.

## Exact later FPF anti-rollback schema fields

The signed later FPF contains six structured field records whose names do not
occur in the exact affected FPF:

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
`9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9`.
This proves a later schema capability for explicit RBE, OEM key-manifest, and
microcode anti-rollback enable/SVN fields. It does **not** prove that these
fields were introduced by SA-00125, that any corresponding physical FPF was
burned on the public NUC or target, or that they address CVE-2018-3655's exact
defect. A first-fixed or intermediate image and exact provisioning-state
consumer analysis remain required.

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

- A hash-bound, signed TXE version later than `3.1.55` is now available.
- A first-fixed `3.1.55` image is still not available.
- The affected and later primary HECI paths both reject a simple payload length
  above `0x1fc`; no direct oversized nine-bit stack copy is observed.
- The later HECI adds exact header-bit validation and bounded extension parsing.
- The later FPF adds explicit RBE, OEM key-manifest, and microcode anti-rollback
  enable/SVN schema records absent by name from the affected FPF.
- CVE-2018-12147's exact defect remains unidentified.
- CVE-2018-3655's exact storage/anti-replay defect remains unidentified.
- No exploit, malformed request, HECI message, flash image, or persistence
  mechanism was created or executed.
