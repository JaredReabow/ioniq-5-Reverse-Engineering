# ABL IAS key-manifest provenance plan

## Objective

Resolve the exact runtime object behind the ABL IAS expected-key digest without executing target firmware or creating an acceptance bypass.

## Inputs

- canonical EU `260128` decrypted update archive;
- exact `rel.1714-HF3` 8 MiB ABL flash;
- exact BPDT type-17 UEP, RBEP CSE RBE, FTPR CSE BUP, IBB loader, and decompressed stage 1;
- hash-bound public Intel FIT definitions;
- hash-bound public ME Analyzer key-manifest layout and usage nomenclature;
- hash-bound public coreboot Apollo Lake IFWI UEP/OEM-key construction logic.

## Acceptance criteria

1. Identify the exact structure at `0xc10c0`/`0xc10c8` from instruction semantics.
2. Trace it backward through IBBL to the earliest recovered source address.
3. Prove whether FIT type `0x0b` payload bytes are copied or merely referenced.
4. Identify the exact recovered producer of the FIT content and trace its source object from persistent bytes through BUP's `0xfffe0000` pointer, IBBL's `0xfef80000` copy, and the low-memory runtime table, while distinguishing the separate IBBL self-relocation and IBB ring paths.
5. Bind selector `0x27` to its record bit, byte, and mask.
6. Explain `0xc1060`/`0xc1064` and any exact observation surface.
7. Keep public names separate from exact target proof.
8. Fail closed on canonical-archive drift and source drift.
9. Emit deterministic UTF-8/LF evidence and focused tests.
10. Trace pre-IBBL OEM-key authentication while separating exact UEP consumption from still-unproved external UEP authentication and fuse precedence.
11. Trace the CSE signing-key and Boot Policy chains through runtime `ipub_key`, `rot.key`, OEM usage bit 32, `IBBP.man`, `BPM.met`, and exact IBBL/IBB bytes without claiming an external ROM/fuse anchor that is not recovered.
12. Trace the selected UEP into BUP/NFTP FPF provisioning, bind the exact signed `fpf` module, and distinguish its later shadow/hardware state from RBE's earlier hardware window unless byte identity is proved.
13. Trace every exact `ipub_key` consumer and fallback path, including the incoming RBE handoff at `0x08200000` and its later FTPR-kernel consumer; distinguish cross-stage runtime-object continuity and internal snowball storage from proof of pre-RBE producer identity, branch selection, writability, authentication, or immutable authority.

## Safety boundary

Host-side archive parsing, hashing, strict LZ4 decompression, source inspection, and disassembly only. Do not execute ABL, an updater, a target helper, or a firmware image. Do not construct or sign a modified image, bypass a signature, flash a device, alter boot state, or develop persistence.

## Routing

The current catalogue advertises `anthropic/claude-fable-5-1` and `openai-codex/gpt-6-astra`, but native child creation rejects the harness-required argument shape: supplying both top-level model fields and `selection` reports “Pass either … not both”, while omitting either side is rejected by schema or dependency validation. Multiple generic, non-private research prompts were attempted without launching a child. No paid route probe or silent substitution was used; work continued in the root thread against public and exact-static inputs.
