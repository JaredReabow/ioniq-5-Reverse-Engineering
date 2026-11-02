# ABL IAS key-manifest provenance checkpoint

## Status

Exact CSE RBE `ipub_key → rot.key` pinning, shared CSE-manifest key identity, UEP-field extraction and OEM-key authentication, OEM Boot Policy validation through exact IBBL/IBB bytes, persistent-object materialization, BUP FIT production, BUP-to-IBBL mapping, IBB ring producer/consumer, runtime type-`0x0b` relocation, selector, stored FTPR `oem.key`, and `ABL.oemkm` export are closed. Installed-unit identity and the external authority supplying `ipub_key` and the selected UEP source remain open.

## Findings

- Exact `RBEP.man → rbe.met → rbe` and `FTPR.man → bup.met → bup` hash chains are byte-bound; both `$MN2` embedded signatures verify.
- Exact RBE resolves runtime `ipub_key`, copies a selector-chosen 32-byte digest to `0x6047fa8`, and requires `rot.key`'s modulus-plus-exponent digest to match before RSA verification.
- FTPR `rot.key` is at flash `0x17b000`, size `0x3fc`, SHA-256 `5530da6cbec43a441466478a6069b7a5d39afe9453f34923c633ad07b4613a14`.
- `rot.key`, `RBEP.man`, `FTPR.man`, and `NFTP.man` share public-key digest `f2eb8fc44e30f6132631df884020abd685ce8843ee205d0a22eb6493f78a54cf`; all embedded signatures verify. The runtime producer/authority of `ipub_key` remains open.
- Exact FTPR signed-package metadata has no direct `oem.key` name/digest coverage and FTPR CPD has no `oem.key.met`; this bounded absence is not proof of no external authentication.
- Exact BPDT type-17 UEP contains three copies of the `oem.key` public-key digest, including a contiguous copy at `+0xcc`; comparative Apollo Lake tooling names that field an OEM public-key-hash record.
- Exact RBE creates `ifp_uep`; hardware-window selection is `((dword[0xf6170810] >> 24) & 0x0c) != 0 && ((dword[0xf6170810] >> 24) & 0x03) != 0`, otherwise it uses BPDT UEP primary/fallback. It extracts field `0x20` (256 bits) to global `0x6048038` and requires the `oem.key` modulus-plus-exponent hash to match before RSA and extension validation.
- Pre-IBBL `oem.key` authentication against the selected UEP field is proved; external UEP authentication, FPF/fuse precedence, and override policy remain unproved.
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
  - size `36,563`
  - SHA-256 `0154bec1847242874e032b3e1009ef76bd17c045977606f9f3bf775845f4afb7`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `93,196`
  - SHA-256 `7550669453ba498fceff2243b48bd0513026ec6a9f833ec1845f7ea8235ecd33`

## Validation

- focused package: `13 passed, 10 subtests passed`;
- ABL/update/bench integration: `82 passed, 46 subtests passed`;
- canonical suite: `1011 passed, 352216 subtests passed in 169.15s`;
- canonical log SHA-256: `85bad908a8148874175fae3183a98d822562bb0c1f6b0ba9c8a7a0d7ea576395`;
- UTF-16 environment determinism, `py_compile`, and `git diff --check` passed.

## Boundary

Exact RBE binds `rot.key` to runtime `ipub_key`; the RoT key is shared by RBEP/FTPR/NFTP manifests. Exact RBE separately authenticates FTPR `oem.key` against the selected UEP digest. Exact BUP carries that OEM key through Boot Policy usage bit 32 to signed `IBBP.man`, `BPM.met`, and exact IBBL/IBB bytes, then publishes the OEM manifest through FIT type `0x0b` for stage 1. Recovered bytes still do not establish who supplies or authenticates runtime `ipub_key`, whether the selected UEP source is fuse-backed, or installed-unit identity. Boot Guard, ACM, fuse, ROM, and installed-firmware provenance remain open at those earlier boundaries.

## Next work

1. Trace the producer and immutable authority of runtime `ipub_key`, including whether ROM, CSE kernel, FPFs, or another authenticated object supplies its selector and digest array.
2. Trace exact authentication and FPF/fuse precedence for the hardware-window versus BPDT UEP source.
3. On a future disconnected bench, record `/proc/cmdline` and the exact `ABL.oemkm` value without attempting a physical-memory read unless separately authorized and safely bounded.
4. Determine whether the installed/runtime OEM key manifest matches the exact stored FTPR object and verify its external provisioning chain host-side.
5. Keep this separate from boot attempts, image modification, key replacement, flashing, and persistence.
