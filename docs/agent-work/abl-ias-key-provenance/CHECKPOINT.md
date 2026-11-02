# ABL IAS key-manifest provenance checkpoint

## Status

Exact runtime object type, IBBL FIT handoff, type-`0x0b` relocation, selector bit, manifest layout, stored FTPR `oem.key`, and `ABL.oemkm` export are closed. The runtime-to-stored-object binding and pre-IBBL authentication remain open.

## Findings

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
  - size `8,102`
  - SHA-256 `0c561c953d6478edf6343388dd89fb05a7d5c59c8a800b6cbddbd44c6ff4eea5`
- `evidence/artifacts/update-candidates/abl-ias-key-provenance-exact-static.asm`
  - size `8,637`
  - SHA-256 `8f415147ce70f627787d9a482c21a88f1135bf8fdd03aefd9d595f9a77263dac`

## Validation

- focused package: `12 passed, 7 subtests passed`;
- ABL/update integration: `49 passed, 26 subtests passed`;
- canonical suite: `1010 passed, 352213 subtests passed in 186.94s`;
- canonical log SHA-256: `54f96acc5b5af4800f61024ceba55c6227278660c00599260e5b53742d61ff44`;
- UTF-16 environment determinism, `py_compile`, and `git diff --check` passed.

## Boundary

Exact recovered code does not identify the producer of `0xfef80000`, bind its type-`0x0b` pointer to stored FTPR `oem.key`, or locally authenticate the key manifest before use. CSE, Boot Guard, ACM, fuse, ROM, and installed-manifest provenance remain hypotheses until earlier code or a passive installed-unit capture binds them.

## Next work

1. Trace the origin of `0xfef80000` through earlier ROM/CSE handoff evidence.
2. Search exact PDR/CSE configuration and source documentation for the FIT handoff producer and the FTPR `oem.key` loading rule.
3. On a future disconnected bench, record `/proc/cmdline` and the exact `ABL.oemkm` value without attempting a physical-memory read unless separately authorized and safely bounded.
4. Determine whether the installed/runtime OEM key manifest matches the exact stored FTPR object and verify its external provisioning chain host-side.
5. Keep this separate from boot attempts, image modification, key replacement, flashing, and persistence.
