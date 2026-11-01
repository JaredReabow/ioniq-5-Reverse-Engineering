# AppFUMO boot-image pairing checkpoint

## Status

Implementation and canonical validation are complete. Publication remains to
be completed.

## Frozen findings

- Exact AppFUMO selector `[0xa2480,0xa2c17)` maps copied root-record target
  `p3`, `p5`, or `p7` plus display mode `1..4` to the complete `iasImage*`
  filename matrix.
- Exact staging function `[0xa2ef0,0xa3e83)` is called at `0xaaac1`, requires
  both the selected normal name and its `_sub` companion, and calls the same
  copy helper at `0xa3370` and `0xa396e`.
- Exact copy helper `[0x1413f0,0x141b28)` passes a `readAll()` buffer to one
  write, immediately rejects only negative write returns, then later requires
  source/destination size equality and successful permission copying.
- The prior advisory simple-short-write suspicion is corrected: later size
  equality prevents a shorter nonnegative write from being returned as success
  when final sizes are stable and accurate.
- The helper still performs no destination-byte readback, digest, or signature;
  ignores `flush()`/`fsync()` results; and does not preserve stable pathname
  object identity across the operation.
- Canonical rootfs `esinit` observes the already-running boot command line and
  performs bidirectional PLK1/PLK2 `iasImage` repair. It is not a proved
  persistent selector or mark-good implementation.

## Artifacts

- `tools/uk_fw/appfumo_boot_image_pairing.py`
- `tests/test_appfumo_boot_image_pairing.py`
- `evidence/appfumo-boot-image-pairing.md`
- `evidence/artifacts/update-candidates/appfumo-boot-image-pairing.json`
- `evidence/artifacts/update-candidates/appfumo-boot-image-pairing-exact-static.asm`
- `docs/agent-work/appfumo-boot-image-pairing/PLAN.md`

## Current hashes

- report: `cd4121a4cb47141281c9b83ecab96cdde4dde053e8e7ee5b9f54297f696f4292`
- exact-static excerpt:
  `8bcc05ae12df4ee5dc359ede2ca6097def2223b08f1367964540b3b23d7ace4e`

## Validation

- focused suite: `14 passed, 2 subtests passed`;
- related AppFUMO suites: `31 passed, 2 subtests passed`;
- canonical suite: `946 passed, 352187 subtests passed in 140.18s`;
- canonical log:
  `work/local-validation/pytest-full-appfumo-boot-image-pairing.log`;
- canonical log SHA-256:
  `3342f1ec55b1396c393e13c1e3748d54531dd14db37666433a9eeb69162de3d2`;
- exact analyzer run succeeded against the embedded ELF and canonical rootfs;
- canonical rootfs complete archive identity and inventory matched;
- `py_compile`, deterministic normal/`PYTHONIOENCODING=utf-16` output,
  strict UTF-8, LF-only, final newline, NUL, trailing-whitespace,
  executable-mode, path-limited diff and `git diff --check` checks passed.

## Boundaries retained

No updater, target helper, boot component, mount, partition writer, reset,
selector change, or boot image was executed. No replacement image, malformed
update, signature bypass, flash procedure, or persistence payload was created.

Payload presence, successful staging, staged-byte authentication, persistent
activation, ABL/MICOM acceptance, health, mark-good, rollback, root, and
persistence remain unknown.

## Reviewer routing

The requested Fable route remains unavailable because
`openrouter/claude-fable-5.1` is not advertised for native subagents with
`multi_agent_version=v2`. No alternate provider was substituted.
