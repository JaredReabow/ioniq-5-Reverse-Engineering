# EU 260128 boot-container matrix checkpoint

## Status

Implementation and canonical validation complete. Publication remains.

## Findings

- All twelve AppFUMO-selected `iasImage*` names exist in the original EU package.
- Six normal images are TE2 envelopes; six `_sub` images are already plaintext
  `ipk.` containers.
- All twelve plaintext containers are size `6,210,308`, pass embedded RSA-2048
  PKCS#1 v1.5 SHA-256 verification, and share modulus SHA-256
  `227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6`.
- Every container decompresses to recovered kernel SHA-256
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`.
- Normal LZ4 frames begin at `0x441a`; console-enabled `_sub` frames at `0x445e`.
- Root-target and serial-console command-line matrix is exact and report-bound.
- Payload presence and embedded signature validity do not prove external
  bootloader acceptance or activation.

## Paths

- `tools/uk_fw/eu260128_boot_container_matrix.py`
- `tests/test_eu260128_boot_container_matrix.py`
- `evidence/eu260128-boot-container-matrix.md`
- `evidence/artifacts/update-candidates/eu260128-boot-container-matrix.json`
- `docs/agent-work/eu260128-boot-container-matrix/PLAN.md`

## Validation

- focused: `8 passed`;
- related boot/update suites: `37 passed, 2 subtests passed`;
- canonical suite: `969 passed, 352187 subtests passed in 156.55s`;
- canonical log SHA-256:
  `a7d5947003e77fa9fbddd2d4c78ea084cf489c94b4b994e236f02f47d2c71feb`;
- report SHA-256:
  `b9ee11e01406d851bc7b284b16ba73139c10ebe557b7d3ce0b2b130ce642903d`.

## Boundary

All analysis was host-side. No modified/re-signed image, update package,
updater, recovered helper, mount, partition write, reset, selector change, or
boot operation was created or executed. External key pinning, final written
bytes, boot selection, acceptance, health, mark-good, rollback, root and
persistence remain unknown.
