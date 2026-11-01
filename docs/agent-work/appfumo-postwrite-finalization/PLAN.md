# AppFUMO post-write finalization plan

## Goal

Close the exact-static boundary between AppFUMO's selected inactive-root writer
path and its completion reporting. Determine what `PartitionUpdater::finish`
maintains, whether it performs a persistent boot-slot selection, and whether
completion progress is equivalent to successful finalization.

## Safety boundary

- Do not execute the recovered updater, helper, service, boot component, or any
  target executable.
- Do not mount, write, trim, unmount, reset, flash, select a slot, or create an
  update package.
- Use only stabilized host-side byte parsing, exact Homebrew LLVM disassembly,
  advisory read-only Ghidra output, hashing, and deterministic tests.
- Keep source bytes and full disassembly under ignored `work/`; retain only
  reviewed, byte-suppressed excerpts and normalized reports.

## Work

1. Bind the exact embedded AppFUMO ELF identity and GNU Build ID.
2. Bind the fstab-helper and `finish` FDEs and the virtual dispatch relocation.
3. Trace inactive-root derivation, mount-state comparison, mount maintenance,
   fstab rewriting, trim/unmount paths, resume-marker cleanup, progress 99/100,
   and the returned status byte.
4. Distinguish VR fstab consistency from persistent root-slot activation.
5. Verify whether a fstab-helper failure terminates or rejoins completion flow.
6. Implement a deterministic analyzer with stable no-follow input handling,
   frozen code hashes, relocation/literal/direct-call/branch validation,
   deterministic UTF-8/LF JSON, and exclusive output creation.
7. Add negative tests for identity, ELF, instruction, call, literal, relocation,
   symlink, encoding, and output-replacement failures.
8. Document only bounded exact-static conclusions.

## Acceptance

- Exact ELF size, SHA-256, and Build ID match the recovered artifact.
- The virtual finish relocation, selected code ranges, literals, direct calls,
  result-byte branch, and 99/100 progress anchors are machine-checked.
- Evidence clearly separates attempted maintenance from successful effects.
- Evidence does not claim final partition integrity, activation, boot
  acceptance, mark-good, rollback, root, or persistence.
- Focused and canonical `pytest -q tests` suites pass.
- Python compilation, deterministic-output, UTF-8/LF/final-newline,
  whitespace, and path-limited diff checks pass.
