# Exact ABL boot selection plan

## Goal

Freeze the exact ordered boot-option and fallback semantics connecting the
signed ABL configuration, decompressed proprietary IBB stage, `esinit`, and the
stored `iasImage_sub` object without running target code or producing a boot
image.

## Acceptance criteria

1. Bind canonical update/rootfs archives and exact selected-member metadata.
2. Parse and CRC-check the exact IAS type-`0x60000` ABL configuration.
3. Bind the ordered PLK1/PLK2 `iasImage` records.
4. Bind stage-1 selected-index masking, ordered-record callback, iterator, and
   selected-versus-actual command-line fields by exact range hashes.
5. Bind the exact tag-`0x04e` GPIO configuration and exact config-name mapping;
   preserve historical Apollo Lake GPIO-decoding source as comparative only.
6. Bind canonical `esinit` fallback detection and repair intent.
7. Bind the engineering normal/`_sub` promotion copies.
8. Keep exact runtime GPIO commitment, attempt, health, mark-good, durable
   repair, custom boot, root, and persistence explicitly unresolved.
9. Emit deterministic UTF-8/LF evidence and fail closed on archive aliases,
   links, metadata drift, CRC drift, malformed records, stage drift, or output
   encoding changes.
