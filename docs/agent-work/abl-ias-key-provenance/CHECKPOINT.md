# ABL IAS key-manifest provenance checkpoint

## Status

Exact CSE RBE incoming-handoff `ipub_key → rot.key` pinning, shared CSE-manifest key identity, UEP-field extraction and OEM-key authentication, OEM Boot Policy validation through exact IBBL/IBB bytes, selected-UEP handoff through BUP into signed NFTP FPF shadow state, persistent-object materialization, BUP FIT production, BUP-to-IBBL mapping, IBB ring producer/consumer, runtime type-`0x0b` relocation, selector, stored FTPR `oem.key`, and `ABL.oemkm` export are closed. Installed-unit identity and the pre-RBE authority supplying the handoff and selected UEP source remain open.

## Findings

- Exact `RBEP.man → rbe.met → rbe` and `FTPR.man → bup.met → bup` hash chains are byte-bound; both `$MN2` embedded signatures verify.
- Exact RBE resolves `ipub_key` from a bounded incoming runtime-object handoff at `0x08200000`, copies a selector-chosen 32-byte digest to `0x6047fa8`, and requires `rot.key`'s modulus-plus-exponent digest to match before RSA verification.
- The handoff lookup caps traversal at `0x8000`, begins entries at `0x08200008`, compares `0x0c`-byte names, tests enabled bit 0 at `+0x0d`, steps by the word at `+0x0e`, and exposes payload at `+0x12`. RBE first appends `cld_rst_blk`, then requires existing `bpdt`, `pm_trans`, `ftpm_fuses`, `sss_em`, `rbe.man`, `pmc_ipc`, and `ipub_key` entries; only missing optional `pmc_msg` is appended.
- `FTPR.man → kernel.met → kernel` reverse-SHA-256 bindings close the exact FTPR kernel byte chain. That kernel processes `0x08200000..0x08208000`, initializes its first entry at `0x08200008`, and advances using the same `+0x0d` state and `+0x0e` size fields. This proves cross-stage handoff continuity, not the pre-RBE producer/authenticator.
- BUP clears list head `0xa014c`, loops its object materializer until null, requires an exact `0x12`-byte header with total size at `+0x0e`, and then requires the exact payload remainder. This matches FTPR's handoff stream geometry. The materializer zero-extends the u16 total and subtracts `0x12` without a minimum-size guard. Exact FTPR concatenates accepted entries to satisfy one read, so a state-1 total `0x10` or `0x11` plus the next entry can reach BUP as a full header retaining that short total. BUP then asks for `0xfffffffe` or `0xffffffff`; the exact standard FTPR-kernel read handler rejects both above its `0x01800000` process-buffer maximum before stream copying. The BUP import binding and attacker control of the malformed stream remain unproved, so memory corruption is not claimed.
- Exact startup order is now closed inside BUP: main runs phase zero; its 22-entry function table executes ingestion at index 7 and `ifp_uep` consumption at index 10; main then frees the transient list. The `ifp_uep` consumer checks neither lookup success nor payload size before fixed 8-byte and `0x100`-byte copies. Prepend-order ingestion plus first-match lookup means the last ingested duplicate wins. Exact RBE supplies the stock object at `0x108` bytes, while malformed/duplicate attacker control remains unproved. The BUP external-reader import is not yet bound to the exact kernel function, so BUP `ipub_key` provenance and snowball exclusion remain open.
- Exact signed NFTP `dal_sdm` independently opens `/snowball/ipub_key`, reads exactly `0x24` bytes on the content path, checks byte `+1` bit 0 and dword `+4`, then gates reads of `/snowball/oem_sign` and `/snowball/oem_key_man`. This proves shared CSE policy-object consumption, not its producer, writability, replay behavior, or fuse/ROM authority.
- All nine exact-ABL little-endian `0x08200000` byte occurrences are classified: five RBE consumer references, three FTPR-kernel consumer references, and one unaligned PMCP cross-dword match spanning dwords `0x20000000`/`0xff171908`. No other plain static base literal remains; computed, indirect, ROM, and external producers remain possible.
- FTPR `rot.key` is at flash `0x17b000`, size `0x3fc`, SHA-256 `5530da6cbec43a441466478a6069b7a5d39afe9453f34923c633ad07b4613a14`.
- `rot.key`, `RBEP.man`, `FTPR.man`, and `NFTP.man` share public-key digest `f2eb8fc44e30f6132631df884020abd685ce8843ee205d0a22eb6493f78a54cf`; all embedded signatures verify. The runtime producer/authority of `ipub_key` remains open.
- Exact BUP initializes global `0xa014c` as an empty runtime-object-list head and materializes received objects with size/pointer/next fields at `+0x14/+0x18/+0x1c`; its generic manifest path resolves `ipub_key` from that list while nonempty or constructs `/snowball/ipub_key` while empty. Correction: the `0x23` comparison requires resolved length greater than `0x23` (runtime payload size or snowball read return count); it is not a selector bound. BUP then uses byte 0 as an unchecked selector for the pointer at `4 + 4*selector` and supplies 32 bytes from that pointer to its verifier. Neither selector nor pointer-field bounds are checked in this path; attacker-controlled malformed-object reachability remains unproved.
- Digest `f2eb8fc4...` occurs statically in the exact ABL only in `rot.key` at `0x17b2cc`; BUP branch selection, snowball writability/authentication, and identity with RBE's earlier object remain unproved.
- Exact FTPR signed-package metadata has no direct `oem.key` name/digest coverage and FTPR CPD has no `oem.key.met`; this bounded absence is not proof of no external authentication.
- Exact BPDT type-17 UEP contains three copies of the `oem.key` public-key digest, including a contiguous copy at `+0xcc`; comparative Apollo Lake tooling names that field an OEM public-key-hash record.
- Exact RBE creates `ifp_uep`; hardware-window selection is `((dword[0xf6170810] >> 24) & 0x0c) != 0 && ((dword[0xf6170810] >> 24) & 0x03) != 0`, otherwise it uses BPDT UEP primary/fallback. It extracts field `0x20` (256 bits) to global `0x6048038` and requires the `oem.key` modulus-plus-exponent hash to match before RSA and extension validation.
- Pre-IBBL `oem.key` authentication against the selected UEP field is proved; external UEP authentication, FPF/fuse precedence, and override policy remain unproved.
- Exact RBE publishes its selected `0x100`-byte UEP payload through `ifp_uep`, with a hardware-route `REAL` header or the validated flash-route `$UEP`/CRC header; exact BUP records whether the header is `REAL` without rejecting the alternative in this range, initially copies the payload byte-for-byte into global `0xa37f8`, may update that shadow through field assembly, and publishes the resulting `0x880` bytes through special file `bup_fpf`.
- Signed `NFTP.man → fpf.met → compressed fpf` hashes bind exact decompressed NFTP `fpf` SHA-256 `9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9`.
- Exact `fpf` requires `/dev/bup_fpf` length `0x880`, opens `/dev/flash/uep`, and uses shadow global `0x366e4` while hardware-mode global `0x36f60` is zero.
- `OemLock`'s callback sets hardware mode before a fixed field sequence, but this later state is not yet equated to RBE's earlier `0xf6170800` window.
- Exact BUP selects the OEM Extension-14 usage-bit-32 record, compares the `IBBP.man` modulus-plus-exponent digest before RSA, verifies `IBBP.man`, verifies its signed `BPM.met` hash, and checks `BPM.met`'s exact IBBL and IBB hashes.
- `IBBP.man` SHA-256 is `f224328529c3662c8c3ba490ad2a3c8143a34d0c9a531d2568f94d639058f615`; exact IBB SHA-256 is `4fba3004219bbfe3a94baa23467c7076d87f4ad76fdb6687ccdbf93455e365ed`.
- Exact RBEP CSE RBE SHA-256: `ec4c2ea54c2943f6f6ffed4b4157b7b03cbccf6ca2cc9b21ccc3dd62adc88cc1`.
- RBE selects FTPR `oem.key`, creates `oem_key_man` at the exact source length, transfers that length without a visible transform, and checks the destination manifest dword length against it.
- Exact FTPR CSE BUP SHA-256: `cee77bc172a9df1c4088d5f716b9e55cda539a26656d07a92268c3cd5d4f0165`.
- BUP initializes a `0x20000`-byte FIT-bearing buffer, looks up `oem_key_man`, copies it to payload offset `0x1000`, and appends type `0x0b` at published address `0xfffe1000`.
- Exact BUP resolves `IBBL`/`IBB`, bounds IBBL to at most `0x9000`, and places the exact `0x4000`-byte IBBL at buffer offset `0x1c000`, or SRAM alias `0xffffc000`.
- IBBL's descriptor at runtime `0xffffe760` is statically embedded at file offset `0x2760` as `{ destination=0xfeffc000, count=0x1000 dwords, source=0xffffc000 }`; it relocates exactly one IBBL image and is not the FIT transfer to `0xfef80000`.
- Exact BUP streams the resolved `IBB` member through four `0x8000`-byte slots spanning its `0x20000`-byte SRAM buffer, with source advancement, ring-index advancement, and hardware handshaking.
- Exact IBBL implements the matching PCI-config consumer at `0x80007870`/`0x80007860`, copies the stream to `0xfefbd900`, and permits `0x38000` bytes.
- BUP writes pointer `0xfffe0000` at buffer offset `0x1ffc0`; IBBL self-relocation carries it to `0xfeffffc0`, where exact IBBL reads it and copies/relocates the FIT into `0xfef80000`.
- Hash-bound public Apollo Lake host code independently matches exact BUP/IBBL chunk-count, size, low-four-bit XOR state, ring index, slot geometry, source, acknowledgement, and PCI configuration offsets bit for bit.
- Combined RBE/BUP instructions prove byte identity between exact FTPR `oem.key` and BUP's published `oem_key_man` payload.
- IBBL SHA-256: `394c442368c67f82f17e84854575bf07abafac2b8fbf2fda7dca68b182f91b93`.
- IBBL validates `_FIT_   ` at source `0xfef80000` and copies up to 21 source entries to `0xc10c0`.
- It appends type `0x7f` and invokes relocation mode 2.
- Mode 2 skips type `1`, not type `0x0b`; a key-manifest payload is copied and its FIT pointer rewritten.
- Stage 1 reads the count from `0xc10c8`, walks `0x10`-byte entries at `0xc10c0`, masks type with `0x7f`, and selects `0x0b`.
- The selected manifest layout is extension `+0x284`, size `+0x288`, entries `+0x2a8`, entry size `0x44`, digest `+0x24` for 32 bytes.
- Selector `0x27` selects bit 39: byte 4, mask `0x80`.
- Public Intel FIT source names type `0x0b` Key Manifest; hash-bound ME Analyzer source names usage 39 OS Kernel.
- Globals `0xc1060`/`0xc1064` cache the extension pointer/size, later exported as kernel command-line field `ABL.oemkm=%x@%x`.
- FTPR contains `oem.key` at flash `0x17c000`, size `0x61c`, SHA-256 `a72a5d867185852be1466a9d3d2e97bb11bd6b0a89b48f5454220def946814bd`.
- Its embedded `$MN2` RSA-2048 signature verifies, proving self-consistency only.
- Its usage-39 digest is `9b0a59c842ba70857b595ed8115630d3a342a10c9d4437f9ff4807517693e0af`, equal to its stored manifest public-key digest.
- The package carried-key candidate `437008c1...` does not match that stored record and remains absent from the update ABL, IBBL, and decompressed stage 1.
- Exact RBE/BUP/IBBL code binds the runtime type `0x0b` payload byte-for-byte to this stored `oem.key`; installed-unit identity still prevents an owner-unit boot or rejection verdict.

## Frozen artifacts

- `tools/uk_fw/abl_ias_key_provenance.py`
- `tests/test_abl_ias_key_provenance.py`
- `evidence/abl-ias-key-manifest-provenance.md`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance.json`
  - size `58,131`
  - SHA-256 `9eb350a9b73a6fde4f6168b99acf17cc00db2f606fdbe343d65afdd147429d50`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `118,126`
  - SHA-256 `f4ed1845afbffc75646223105132d2c6c9b3fc685fed6dc0df1273d6c68ecf02`

## Validation

- focused package: `13 passed, 10 subtests passed`;
- selected provenance/trust/bench/MEI integration: `56 passed, 172 subtests passed`;
- canonical suite: `1019 passed, 352351 subtests passed in 615.30s`;
- canonical log SHA-256: `12b684f72acd0f2c4938826acf4b579b79969a8929cbd141b8bc94c228dce36c`;
- UTF-16 environment determinism, `py_compile`, and `git diff --check` passed.

## Boundary

Exact RBE binds `rot.key` to runtime `ipub_key`; the RoT key is shared by RBEP/FTPR/NFTP manifests. Exact RBE separately authenticates FTPR `oem.key` against the selected UEP digest. Exact BUP carries that OEM key through Boot Policy usage bit 32 to signed `IBBP.man`, `BPM.met`, and exact IBBL/IBB bytes, then publishes the OEM manifest through FIT type `0x0b` for stage 1. The selected UEP also reaches BUP's `bup_fpf` output and the signed NFTP `fpf` shadow, but that later hardware-mode state is not yet proved to produce RBE's earlier hardware window. Recovered bytes establish that RBE receives `ipub_key` through the incoming `0x08200000` handoff, but not who populated or authenticated that handoff, whether its memory is immutable, whether the selected UEP source is fuse-backed, or installed-unit identity. Boot Guard, ACM, fuse, ROM, and installed-firmware provenance remain open at those earlier boundaries.

## Next work

1. Trace the pre-RBE producer and immutable authority of the runtime-object handoff at `0x08200000`, including whether ROM, CSE kernel, FPFs, or another authenticated object supplies the `ipub_key` selector and digest array; determine what controls BUP global `0xa014c` and authenticates `/snowball/ipub_key` without assuming that fallback is selected or writable.
2. Trace exact authentication and FPF/fuse precedence for the hardware-window versus BPDT UEP source, using the closed `ifp_uep → bup_fpf → signed NFTP fpf` path without assuming the later FPF hardware state produced RBE's earlier window.
3. On a future disconnected bench, record `/proc/cmdline` and the exact `ABL.oemkm` value without attempting a physical-memory read unless separately authorized and safely bounded.
4. Determine whether the installed/runtime OEM key manifest matches the exact stored FTPR object and verify its external provisioning chain host-side.
5. Keep this separate from boot attempts, image modification, key replacement, flashing, and persistence.
