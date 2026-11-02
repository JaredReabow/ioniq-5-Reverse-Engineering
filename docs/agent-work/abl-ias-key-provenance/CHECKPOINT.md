# ABL IAS key-manifest provenance checkpoint

## Status

Exact CSE RBE UEP-field extraction and OEM-key authentication, persistent-object materialization, BUP FIT content production, BUP-to-IBBL FIT mapping, exact IBB ring producer/consumer, runtime object type, type-`0x0b` relocation, selector bit, manifest layout, stored FTPR `oem.key`, and `ABL.oemkm` export are closed. Installed-unit identity and external trust/fuse precedence governing the selected UEP source remain open.

## Findings

- Exact `RBEP.man → rbe.met → rbe` and `FTPR.man → bup.met → bup` hash chains are byte-bound; both `$MN2` embedded signatures verify, but their external key anchors remain unproved.
- Exact FTPR signed-package metadata has no direct `oem.key` name/digest coverage and FTPR CPD has no `oem.key.met`; this bounded absence is not proof of no external authentication.
- Exact BPDT type-17 UEP contains three copies of the `oem.key` public-key digest, including a contiguous copy at `+0xcc`; comparative Apollo Lake tooling names that field an OEM public-key-hash record.
- Exact RBE creates `ifp_uep`; hardware-window selection is `((dword[0xf6170810] >> 24) & 0x0c) != 0 && ((dword[0xf6170810] >> 24) & 0x03) != 0`, otherwise it uses BPDT UEP primary/fallback. It extracts field `0x20` (256 bits) to global `0x6048038` and requires the `oem.key` modulus-plus-exponent hash to match before RSA and extension validation.
- Pre-IBBL `oem.key` authentication against the selected UEP field is proved; external UEP authentication, FPF/fuse precedence, and override policy remain unproved.
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
  - size `28,206`
  - SHA-256 `f8a84d935e251da4c838e3664f6fb0c570ace9854307aa357666ab5b7521364d`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `87,570`
  - SHA-256 `668fb27cfa9b5bd08f9424e3558586a4c9d985a1ddb5b9a99d6ca89146f9872c`

## Validation

- focused package: `13 passed, 10 subtests passed`;
- ABL/update integration: `56 passed, 26 subtests passed`;
- canonical suite: `1011 passed, 352216 subtests passed in 172.15s`;
- canonical log SHA-256: `9b2d0b0db06bb9295c82b452531461bf6d86d50a6dbb352153a94018b87cd2d4`;
- UTF-16 environment determinism, `py_compile`, and `git diff --check` passed.

## Boundary

Exact CSE RBE authenticates stored FTPR `oem.key` against the selected UEP OEM-key field, binds those bytes to `oem_key_man`, and exact BUP/IBBL code carries that FIT type `0x0b` object through `0xfffe0000`, `0xfef80000`, and `0xc10c0` to stage 1. Exact producer/consumer code also closes the separate IBB ring destination. Recovered bytes still do not establish whether the selected UEP source is authenticated or fuse-backed, or bind installed-unit identity. Boot Guard, ACM, fuse, ROM, and installed-firmware provenance remain open.

## Next work

1. Trace external authentication and FPF/fuse precedence for the selected UEP source now that the persistent-to-runtime FIT byte path is closed.
2. Trace the exact mode source controlling hardware-window versus BPDT UEP selection and determine FPF/fuse precedence or cryptographic protection of the selected UEP bytes.
3. On a future disconnected bench, record `/proc/cmdline` and the exact `ABL.oemkm` value without attempting a physical-memory read unless separately authorized and safely bounded.
4. Determine whether the installed/runtime OEM key manifest matches the exact stored FTPR object and verify its external provisioning chain host-side.
5. Keep this separate from boot attempts, image modification, key replacement, flashing, and persistence.
