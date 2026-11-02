# ABL IAS key-manifest provenance checkpoint

## Status

Exact CSE BUP FIT content production, runtime object type, IBBL FIT handoff, type-`0x0b` relocation, selector bit, manifest layout, stored FTPR `oem.key`, and `ABL.oemkm` export are closed. The BUP-to-IBBL address mapping, runtime-to-stored-object byte binding, and pre-IBBL authentication remain open.

## Findings

- Exact FTPR CSE BUP SHA-256: `cee77bc172a9df1c4088d5f716b9e55cda539a26656d07a92268c3cd5d4f0165`.
- BUP initializes a FIT, looks up `oem_key_man`, copies it to payload offset `0x1000`, and appends type `0x0b` at published address `0xfffe1000`.
- Its key resolver couples persistent name `oem.key` with object name `oem_key_man`, but does not prove byte identity in the executed publication path.
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
- Exact recovered code does not yet prove that runtime FIT type `0x0b` points to this stored `oem.key`; the mismatch is not a package boot or rejection verdict.

## Frozen artifacts

- `tools/uk_fw/abl_ias_key_provenance.py`
- `tests/test_abl_ias_key_provenance.py`
- `evidence/abl-ias-key-manifest-provenance.md`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance.json`
  - size `10,382`
  - SHA-256 `73459a4376b9ae12f0fcf3d4828960859eefe4e1683c2cc3033988e14addb984`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `17,667`
  - SHA-256 `56ea91be8c7b7f03a71e042a3129ed0df096e4331b02af2ef62a26444386c666`

## Validation

- focused package: `12 passed, 7 subtests passed`;
- ABL/update integration: `55 passed, 23 subtests passed`;
- canonical suite: `1010 passed, 352213 subtests passed in 169.98s`;
- canonical log SHA-256: `b043c0747a369c31d70a73ac23618a6e9457c231944354a46ac9ee045a184cd5`;
- UTF-16 environment determinism, `py_compile`, and `git diff --check` passed.

## Boundary

Exact CSE BUP is now the proved FIT content producer, but recovered code does not map its published table/payload addresses to IBBL's `0xfef80000`, bind `oem_key_man` bytes to stored FTPR `oem.key`, or establish the external root that authenticates the manifest before use. Boot Guard, ACM, fuse, ROM, and installed-manifest provenance remain open until earlier code or a passive installed-unit capture binds them.

## Next work

1. Trace the mapping from BUP's FIT buffer and `0xfffe1000` payload address to IBBL's `0xfef80000` source through CSE/ROM handoff evidence.
2. Recover the exact executed rule that materializes `oem_key_man` and determine whether it copies or transforms FTPR `oem.key`.
3. On a future disconnected bench, record `/proc/cmdline` and the exact `ABL.oemkm` value without attempting a physical-memory read unless separately authorized and safely bounded.
4. Determine whether the installed/runtime OEM key manifest matches the exact stored FTPR object and verify its external provisioning chain host-side.
5. Keep this separate from boot attempts, image modification, key replacement, flashing, and persistence.
