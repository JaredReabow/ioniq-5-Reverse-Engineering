# DecryptToPIPE output-integrity checkpoint

## Status

Implementation and canonical validation complete. Publication remains.

## Findings

- Canonical stock helper identity is bound directly from the canonical rootfs
  archive: size `559,192`, SHA-256
  `e3110811e83701368e638947e6d8887f59321707e70f6288adf0790090d929c0`,
  Build ID `4303e27a93f0acfb308146a5d034dafbffa064d0`.
- All six normal EU boot images select the `TE2` decryption path.
- All six plaintext `_sub` images select exact parser result `-404` and the
  raw-copy fallback.
- AppFUMO supplies fallback offset `0`.
- Both 512-byte stdout loops reject only negative writes; shorter nonnegative
  writes are not completed.
- Parser/decrypt/read/write results do not reach process exit; main returns zero
  after the stream call.
- AppFUMO independently discards the shell/pclose status and performs no final
  boot-destination byte verification.

## Paths

- `tools/uk_fw/decrypttopipe_output_integrity.py`
- `tests/test_decrypttopipe_output_integrity.py`
- `evidence/decrypttopipe-output-integrity.md`
- `evidence/artifacts/update-candidates/decrypttopipe-output-integrity.json`
- `evidence/artifacts/update-candidates/decrypttopipe-output-integrity-exact-static.asm`
- `docs/agent-work/decrypttopipe-output-integrity/PLAN.md`

## Validation

- focused: `8 passed, 5 subtests passed`;
- related suites: `31 passed, 5 subtests passed`;
- canonical suite: `977 passed, 352192 subtests passed in 147.37s`;
- canonical log SHA-256:
  `c574c1fac0c1e1f1752bf7fe433eb32252411f70c9986724ef9fa5b21e913346`;
- report SHA-256:
  `b52ed73601091f541541aa50aecd90886e5249f6b3f48c43fadaa2b85f9fc0cb`;
- exact-static excerpt SHA-256:
  `ddfab55d2670e80d133490568207d42a46849d823837dc83139c55d8a2633f70`.

## Boundary

No recovered helper or target executable was run. No pipeline, `dd`, update,
modified image, mount, partition write, reset, boot operation, root action, or
persistence mechanism was created or executed. Runtime completeness, final
bytes, boot acceptance, health, mark-good, rollback, root and persistence remain
unknown.
