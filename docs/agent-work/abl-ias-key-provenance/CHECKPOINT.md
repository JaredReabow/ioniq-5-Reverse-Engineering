# ABL IAS key-manifest provenance checkpoint

## Status

Exact CSE RBE UEP-field extraction and OEM-key authentication, persistent-object materialization, BUP FIT content production, runtime object type, IBBL FIT handoff, type-`0x0b` relocation, selector bit, manifest layout, stored FTPR `oem.key`, and `ABL.oemkm` export are closed. The BUP-to-IBBL address mapping, installed-unit identity, and external trust/fuse precedence governing the selected UEP source remain open.

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
- Exact BUP separately streams the resolved `IBB` member through four `0x8000`-byte slots spanning its `0x20000`-byte SRAM buffer, with source advancement, ring-index advancement, and hardware handshaking; the host destination and FIT-table preservation remain open.
- Hash-bound historical Apollo Lake source independently defines `0x20000` bytes of CSE SRAM remapped at `0xfffe0000`, copies CSE IBB chunks into `IbbDst`, and places Stage1A at `0xfef80000`; this remains comparative support for the still-unrecovered FIT transfer.
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
- Exact RBE/BUP code binds the BUP-published type `0x0b` payload to this stored `oem.key`; the unproved BUP-to-IBBL physical mapping and installed-unit identity still prevent a package boot or rejection verdict.

## Frozen artifacts

- `tools/uk_fw/abl_ias_key_provenance.py`
- `tests/test_abl_ias_key_provenance.py`
- `evidence/abl-ias-key-manifest-provenance.md`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance.json`
  - size `25,061`
  - SHA-256 `11ec0d56b7ac912d67588778ce7b09647f7aba34a3ebd0a8973dc9f10dec2044`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `82,802`
  - SHA-256 `8fd1004319b20acca4877e0dbadfa020177b1b3023c0a47417e358770a606a5d`

## Validation

- focused package: `13 passed, 10 subtests passed`;
- ABL/update integration: `56 passed, 26 subtests passed`;
- canonical suite: `1011 passed, 352216 subtests passed in 163.33s`;
- canonical log SHA-256: `8c2069fff9ab1ac59a82c75dfa616c086c1f8bd0d2f8d5d81b8b813e677d9a28`;
- UTF-16 environment determinism, `py_compile`, and `git diff --check` passed.

## Boundary

Exact CSE RBE authenticates stored FTPR `oem.key` against the selected UEP OEM-key field, binds those bytes to `oem_key_man`, and exact BUP binds that object to its published FIT type `0x0b`. Signed-package metadata separately binds exact RBE/BUP bytes. Exact BUP/IBBL code now closes IBBL placement and self-relocation, but that descriptor does not transfer the FIT to `0xfef80000`; the intervening CSE/host path remains unresolved. Recovered bytes also do not establish whether the selected UEP source is authenticated or fuse-backed, or bind installed-unit identity. Boot Guard, ACM, fuse, ROM, and installed-firmware provenance remain open.

## Next work

1. Trace the exact host-side consumer of BUP's proved four-slot IBB ring and the mechanism that leaves or transfers the FIT table at `0xfef80000`; the recovered `0xffffe760` descriptor is IBBL self-relocation, not that transfer.
2. Trace the exact mode source controlling hardware-window versus BPDT UEP selection and determine FPF/fuse precedence or cryptographic protection of the selected UEP bytes.
3. On a future disconnected bench, record `/proc/cmdline` and the exact `ABL.oemkm` value without attempting a physical-memory read unless separately authorized and safely bounded.
4. Determine whether the installed/runtime OEM key manifest matches the exact stored FTPR object and verify its external provisioning chain host-side.
5. Keep this separate from boot attempts, image modification, key replacement, flashing, and persistence.
