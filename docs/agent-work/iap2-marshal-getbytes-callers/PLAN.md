# Plan: iAP2 marshal byte callers

## Objective

Complete an exact-static inventory of `iAp2MarshalGetBytes` in the recovered EU
`260128` corpus, trace every direct recovered caller, and distinguish the
helper-local bounds, transaction-initializer bounds, and caller-side allocation,
copy, arithmetic, logging, and downstream-dispatch semantics.

## Constraints

- Offline static analysis only.
- Do not execute recovered target code.
- Do not construct or transmit iAP2, CarPlay, USB, network, pairing, or media
  inputs.
- Bind conclusions to exact identities, addresses, FDE ranges, bytes, and
  hashes.
- Do not claim physical delivery, admission, crash, disclosure, code execution,
  root, persistence, CVE identity, or installed-unit impact.
- Preserve all unrelated dirty and staged worktree paths.

## Work packages

1. Identify every recovered exact symbol carrier and binary identity.
2. Reconstruct the complete helper and aligned-span-accessor semantics.
3. Enumerate all direct PLT calls and map each to its FDE-bounded caller.
4. Classify pointer/length storage, allocation, copies, arithmetic, logging,
   cleanup, and downstream dispatch.
5. Trace any caller-side candidate to exact command handlers without creating a
   protocol input.
6. Build a deterministic no-follow verifier and focused tests.
7. Publish a bounded evidence note and reproducible JSON artifact.
