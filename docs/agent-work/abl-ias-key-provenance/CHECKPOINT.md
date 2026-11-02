# ABL IAS key-manifest provenance checkpoint

## Status

Exact CSE RBE persistent-object materialization, BUP FIT content production, runtime object type, IBBL FIT handoff, type-`0x0b` relocation, selector bit, manifest layout, stored FTPR `oem.key`, and `ABL.oemkm` export are closed. The BUP-to-IBBL address mapping, installed-unit identity, and pre-IBBL authentication remain open.

## Findings

- Exact RBEP CSE RBE SHA-256: `ec4c2ea54c2943f6f6ffed4b4157b7b03cbccf6ca2cc9b21ccc3dd62adc88cc1`.
- RBE selects FTPR `oem.key`, creates `oem_key_man` at the exact source length, transfers that length without a visible transform, and checks the destination manifest dword length against it.
- Exact FTPR CSE BUP SHA-256: `cee77bc172a9df1c4088d5f716b9e55cda539a26656d07a92268c3cd5d4f0165`.
- BUP initializes a FIT, looks up `oem_key_man`, copies it to payload offset `0x1000`, and appends type `0x0b` at published address `0xfffe1000`.
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
  - size `12,690`
  - SHA-256 `86f3936c41b75fde136bdd68e24a0253a5192072ea9eb06d0b30148908b9014b`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `31,647`
  - SHA-256 `f888b0c5b13020625be4550a069ef22a2070cfe4a2e742385b0535b3aeff46de`

## Validation

- focused package: `12 passed, 7 subtests passed`;
- ABL/update integration: `55 passed, 23 subtests passed`;
- canonical suite: `1010 passed, 352213 subtests passed in 175.53s`;
- canonical log SHA-256: `78c4f10c1b7ab487db5bedc7179ad45579af4b2e117b5af4743d5f3dc9bea911`;
- UTF-16 environment determinism, `py_compile`, and `git diff --check` passed.

## Boundary

Exact CSE RBE now binds stored FTPR `oem.key` bytes to `oem_key_man`, and exact BUP binds that object to its published FIT type `0x0b`. Recovered code still does not map BUP's table/payload addresses to IBBL's `0xfef80000` or establish the external root that authenticates RBE, FTPR, or the manifest before use. Boot Guard, ACM, fuse, ROM, and installed-firmware provenance remain open until earlier code or a passive installed-unit capture binds them.

## Next work

1. Trace the mapping from BUP's FIT buffer and `0xfffe1000` payload address to IBBL's `0xfef80000` source through CSE/ROM handoff evidence.
2. Trace authentication of RBE, FTPR, and `oem.key` through exact RBEP/FTPR manifests, CSE policy, and any fuse- or ROM-backed root.
3. On a future disconnected bench, record `/proc/cmdline` and the exact `ABL.oemkm` value without attempting a physical-memory read unless separately authorized and safely bounded.
4. Determine whether the installed/runtime OEM key manifest matches the exact stored FTPR object and verify its external provisioning chain host-side.
5. Keep this separate from boot attempts, image modification, key replacement, flashing, and persistence.
