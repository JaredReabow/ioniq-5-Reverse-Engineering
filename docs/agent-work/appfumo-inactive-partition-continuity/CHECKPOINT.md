# Checkpoint — AppFUMO inactive-partition continuity

## Completed

- Bound the exact embedded ELF by size, SHA-256, and GNU Build ID.
- Reconstructed both inactive root mappings from the 20-pointer relocated
  table.
- Bound selected record `+0x20` → name lookup → writer index → jump table.
- Bound root index `1` → same-predicate record copy → copied-record `+0x28` →
  root target string construction.
- Added deterministic verifier, report, exact-static excerpts, evidence note,
  and negative tests.
- Focused validation: `7 passed`.

## Validation

- Focused: `7 passed`.
- Full suite: `922 passed, 352185 subtests passed in 130.43s`.
- Full-suite log:
  `work/local-validation/pytest-full-appfumo-inactive-continuity.log`, size
  `1167`, SHA-256
  `45f78bb8d3196e09dbd1df077babbe28df0b0f3c1a0477772cc267e82916c02c`.
- Python compilation, normal/`PYTHONIOENCODING=utf-16` byte identity,
  path-limited `git diff --check`, strict UTF-8, LF-only, final-newline, NUL,
  and trailing-whitespace checks passed.
- No independent acceptance is claimed.

## Boundary

Closed: exact-static selector/index/inactive-root-target continuity.

Open: authentication-to-writer object/byte continuity, final partition
integrity, write success, activation, boot acceptance, health, mark-good,
rollback, recovery, root, and persistence.
