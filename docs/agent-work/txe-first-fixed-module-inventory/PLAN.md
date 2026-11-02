# TXE first-fixed signed-module inventory plan

## Objective

Build a deterministic, hash-bound affected `3.1.50.2222` versus official first-fixed `3.1.55.2269` NFTP module inventory. Identify modules that are byte-identical, differ only by the reviewed five-byte syslib-export insertion relocation, or retain unexplained bytes requiring deeper static review.

## Non-goals

- No CSE module execution, HECI/MEI access, malformed input, payload, signature bypass, firmware modification, or flash procedure.
- No CVE attribution from module names, timing, or version alone.
- No claim that address-normalized local bytes imply transitive behavioral identity.

## Contracts

1. Inputs are stable no-follow regular files with exact reviewed SHA-256 identities.
2. Both NFTP manifests and every usable `manifest -> metadata -> module` chain are verified before comparison.
3. Strict decompression requires exact declared size, EOF, and no trailing bytes.
4. A relocation-only classification requires complete byte coverage, normalized full-module identity, target translation by exactly `+5`, and affected/fixed targets that decode as syslib `jmp rel32` export stubs.
5. Modules unsupported by the existing strict extractor remain explicit opaque entries rather than being guessed or silently omitted.
6. Output is deterministic JSON and remains byte-identical under normal and UTF-16 `PYTHONIOENCODING` settings.

## Deliverables

- `tools/uk_fw/txe_first_fixed_module_inventory.py`
- `tests/test_txe_first_fixed_module_inventory.py`
- `evidence/artifacts/update-candidates/txe-first-fixed-module-inventory.json`
- `evidence/intel-txe-first-fixed-module-inventory.md`
- `docs/agent-work/txe-first-fixed-module-inventory/CHECKPOINT.md`

## Acceptance

- Canonical exact inputs produce the reviewed module set and comparison counts.
- The report identifies all fully relocation-only modules without normalizing any unexplained byte.
- Exact identical and opaque module cases are represented explicitly.
- Focused tests, canonical test suite, `py_compile`, `git diff --check`, and encoding determinism pass.
