# Plan — AppFUMO inactive-partition continuity

1. Bind analysis to the exact embedded EU `260128` AppFUMO ELF.
2. Trace selected record/index/selector fields into writer dispatch.
3. Reconstruct the inactive root mapping table from ELF relocations.
4. Prove table-population and record-copy branches use the same predicate.
5. Bound the root branch's reuse of index `1` and target `+0x28`.
6. Implement a fail-closed deterministic verifier and negative tests.
7. Preserve authentication/write/activation/boot/persistence boundaries.
8. Run focused and full validation before any path-limited commit.
