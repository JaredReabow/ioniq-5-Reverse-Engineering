# AppFUMO boot-partition write checkpoint

## Status

Implementation and canonical validation complete. Publication remains.

## Frozen findings

- `swapSystem` `[0x148e70,0x14bba6)` constructs p1/p2 mount commands and writes
  the selected normal image to both boot partitions; p2 also receives `_sub`.
- Mode zero uses the size-checking direct copy helper. Mode nonzero constructs a
  `DecryptToPIPE` to `dd` pipeline.
- Mount dispatch waits indefinitely for `QProcess` completion but does not call
  `QProcess::exitCode()` or propagate child exit status.
- Correction: the pipeline helper does drain output and call `pclose()`; it
  ignores the returned status and returns void.
- Direct-copy failures and nonzero unmount results are logged but do not affect
  the common continuing-tail result.
- Common-tail formula is
  `1 XOR ((key_failures > 1) AND (mode_byte & 1))`.
- For observed mode zero/one semantics, mode zero's common tail is true
  regardless of copy results; mode one is false only when both key retrievals
  fail.
- Two production callers latch a nonzero return into object offset `+0x240`.

## Paths

- `tools/uk_fw/appfumo_boot_partition_write.py`
- `tests/test_appfumo_boot_partition_write.py`
- `evidence/appfumo-boot-partition-write.md`
- `evidence/artifacts/update-candidates/appfumo-boot-partition-write.json`
- `evidence/artifacts/update-candidates/appfumo-boot-partition-write-exact-static.asm`
- `docs/agent-work/appfumo-boot-partition-write/PLAN.md`

## Current validation

- focused suite: `8 passed`;
- related AppFUMO suites: `32 passed, 2 subtests passed`;
- canonical suite: `954 passed, 352187 subtests passed in 140.24s`;
- canonical log SHA-256:
  `863c7862bfe5baaa81973685005bd73d80b859438f17ef9d0068252fea218ec2`;
- report SHA-256:
  `0ded08b2f0e74c818f7a07e96923aa7e078d55915e2173676d69e5da481af53d`;
- exact-static excerpt SHA-256:
  `53cc7b18eb9ffa5064ae7eb8358355c049d27edf8ec9cfac1c437659f3ecf709`.

## Boundary

No recovered executable, mount, pipeline, copy, updater, boot image, reset,
selector or partition writer was executed. Successful mount, copied/decrypted
bytes, final partition integrity, durability, boot selection, ABL/MICOM
acceptance, health, mark-good, rollback, root and persistence remain unknown.

## Reviewer routing

Fable remains unavailable through native subagent v2. No alternate provider was
substituted.
