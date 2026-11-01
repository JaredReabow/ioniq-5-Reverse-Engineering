# AppFUMO boot-image pairing plan

## Objective

Close the exact-static boundary between AppFUMO's selected inactive-root record,
its boot-image filename/staging logic, the staging copy helper's integrity checks,
and stock early-userspace PLK1/PLK2 recovery behavior.

The phase must determine what is paired and copied without promoting filename
selection, staging, fallback repair, comments, or progress to persistent boot-slot
activation.

## Non-goals and safety boundary

- Do not execute AppFUMO, `esinit`, a boot image, a helper, or any recovered
  target executable.
- Do not mount, copy to a target partition, flash, reset, select a slot, generate
  a replacement boot image, or create a persistence payload.
- Do not turn static paths into an operational update or recovery procedure.
- Do not claim that a filename authenticates content, that a same-size copy is
  byte-identical, or that post-boot repair selects the next boot slot.
- Keep full disassembly and advisory decompiler output under ignored `work/`.

## Inputs

1. Exact embedded AppFUMO ELF:
   - size `5,066,264`;
   - SHA-256
     `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`;
   - Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`.
2. Canonical rootfs archive:
   - size `879,109,759`;
   - SHA-256
     `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
   - inventory SHA-256
     `c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94`.
3. Canonical member `./lib/systemd/esinit`, required as one unique regular file
   with exact metadata and content identity.

## Exact-static questions

1. Does raw function `[0xa2480,0xa2c17)` use the copied root record's target to
   select `iasImage`, `iasImage_p5`, or `iasImage_p7` display variants?
2. Does `[0xa2ef0,0xa3e83)` require and stage both the selected normal filename
   and its `_sub` companion from the package image directory?
3. Is that staging routine reached by the reviewed preparation function?
4. Does copy helper `[0x1413f0,0x141b28)` require a full-size result, content
   equality, permissions continuity, or only weaker checks?
5. Does canonical `esinit` select a slot, mark a slot good, or instead perform
   post-boot PLK1/PLK2 repair based on the observed command line and splash state?
6. What remains external to AppFUMO and Linux userspace?

## Implementation

Create `tools/uk_fw/appfumo_boot_image_pairing.py` with:

- stable no-follow regular-file reads and same-descriptor identity revalidation;
- exact ELF, PT_NOTE Build-ID, PT_LOAD, section and relocation validation;
- frozen hashes for selector, staging and copy-helper machine-code ranges;
- fixed direct-call, branch, immediate and literal anchors;
- an explicit root-target/display-mode filename matrix;
- canonical rootfs streaming through one stable descriptor;
- complete archive hash, member count and inventory identity checks;
- selected-member canonicalization, alias, duplicate, link and special-node
  rejection;
- strict UTF-8/LF parsing of `esinit` and ordered exact snippets;
- deterministic UTF-8/LF JSON and exclusive output creation.

Add focused tests for identity, malformed ELF, range/call/literal drift, rootfs
alias/duplicate/link/special-node handling using small synthetic archives,
symlink rejection, deterministic output, and exclusive output creation.

## Acceptance

- The root-target/display-mode filename matrix is exact and machine-bound.
- Both normal and `_sub` staging calls are bound to the same selected filename.
- The copy helper's direct data flow and final validation are described exactly:
  source buffer to destination write, later source/destination size equality,
  and permission-copy result, but no destination-byte readback/hash.
- Canonical `esinit` is reported as post-boot repair/fallback behavior, not a
  persistent selector or mark-good operation.
- Missing boot-image content and ABL/MICOM behavior remain explicit unknowns.
- Focused and canonical `pytest -q tests` suites pass with deterministic-output,
  compilation, UTF-8/LF/final-newline, whitespace and diff checks.

## Routing status

The requested Fable route is blocked before delegation because
`openrouter/claude-fable-5.1` is not advertised for native subagents with
`multi_agent_version=v2`. No paid probe or alternate-provider substitution is
permitted. Root implementation proceeds under this written contract.
