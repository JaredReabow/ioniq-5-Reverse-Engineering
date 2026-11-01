# DecryptToPIPE output-integrity plan

## Objective

Freeze the stock `DecryptToPIPE` process semantics used by AppFUMO boot-image
pipelines, including TE2 detection, plaintext fallback applicability to every EU
`*_sub` image, numeric offset `0`, short-write handling, and process exit status.

## Inputs

- canonical EU rootfs archive;
- exact embedded AppFUMO ELF;
- exact twelve-file EU boot-image source directory.

## Safety

Static parsing only. Do not execute `DecryptToPIPE`, AppFUMO, `dd`, a shell
pipeline, updater, mount helper, or boot component. Do not generate a modified
container, update, signature bypass, flash command, or persistence payload.

## Questions

1. Does each normal image select the TE2-decrypt branch?
2. Does each plaintext `_sub` image select the raw-copy fallback?
3. What offset does AppFUMO supply to that fallback?
4. Are short nonnegative stdout writes handled completely?
5. Do parser/decrypt/write failures affect `DecryptToPIPE` exit status?
6. Does any of this prove final boot-partition bytes? (No.)

## Acceptance

The analyzer must bind the canonical archive and selected member metadata,
DecryptToPIPE SHA-256/Build ID/FDE hashes, AppFUMO identity and pipeline literal,
all twelve boot-source identities and trailer classes, exact branches/calls, and
deterministic path-private output. Archive aliases, duplicates, links, special
nodes, ownership or mode drift, input mutation, malformed ELF, and tool drift
must fail closed.
