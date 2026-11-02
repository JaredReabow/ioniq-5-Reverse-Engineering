# ABL IAS key-manifest provenance plan

## Objective

Resolve the exact runtime object behind the ABL IAS expected-key digest without executing target firmware or creating an acceptance bypass.

## Inputs

- canonical EU `260128` decrypted update archive;
- exact `rel.1714-HF3` 8 MiB ABL flash;
- exact IBB loader and decompressed stage 1;
- hash-bound public Intel FIT definitions;
- hash-bound public ME Analyzer key-manifest layout and usage nomenclature.

## Acceptance criteria

1. Identify the exact structure at `0xc10c0`/`0xc10c8` from instruction semantics.
2. Trace it backward through IBBL to the earliest recovered source address.
3. Prove whether FIT type `0x0b` payload bytes are copied or merely referenced.
4. Bind selector `0x27` to its record bit, byte, and mask.
5. Explain `0xc1060`/`0xc1064` and any exact observation surface.
6. Keep public names separate from exact target proof.
7. Fail closed on canonical-archive drift and source drift.
8. Emit deterministic UTF-8/LF evidence and focused tests.
9. State clearly what remains unknown about persistent storage and pre-IBBL authentication.

## Safety boundary

Host-side archive parsing, hashing, strict LZ4 decompression, source inspection, and disassembly only. Do not execute ABL, an updater, a target helper, or a firmware image. Do not construct or sign a modified image, bypass a signature, flash a device, alter boot state, or develop persistence.

## Routing

The requested Fable builder was checked with the installed orchestrator doctor. It remains unavailable because `openrouter/claude-fable-5.1` is not advertised for native subagents with `multi_agent_version=v2`. No paid probe or substitute provider was used. Work therefore continued in the root thread against public and exact-static inputs.
