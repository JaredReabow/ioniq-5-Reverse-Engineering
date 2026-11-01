# GStreamer parser backport exact-static audit plan

## Objective

Bind two exact GStreamer plugin members directly to the canonical EU 260128
rootfs tar and determine, from exact machine code, whether:

1. the CVE-2017-5842-associated nonzero-length fix is present in subparse; and
2. the CVE-2016-9811-associated initial 18-byte guard and later 22-byte
   correction are present in the Windows icon typefinder.

## Boundaries

- Offline static analysis only; never load or execute a recovered plugin.
- Do not create media, parser input, malformed bytes, or a trigger recipe.
- Bind public conclusions to the canonical tar, not a development extraction.
- Fail closed on archive/member aliases, duplicates, links, special nodes,
  unsafe names, identity drift, and changing or oversized inputs.
- Pin tool identity, complete instruction/FDE identities, selected FDEs, and
  exact semantic anchors in a strict manifest.
- State exploit and delivery outcomes as unknown; do not claim execution,
  disclosure, root access, persistence, or production delivery.
- Retain no full binary or full disassembly.

## Work

1. Verify canonical archive and exact selected-member identities.
2. Compare public upstream source/patch semantics with the reviewed exact
   function machine code.
3. Implement one deterministic strict analyzer that streams the tar directly.
4. Add fail-closed schema, archive, tool, instruction, FDE, determinism, and
   privacy tests.
5. Publish a deterministic JSON report, bounded reviewed excerpt, evidence
   narrative, and narrow media-candidate index entry.
6. Run only the focused test module and leave changes unstaged.

## Acceptance

- The subparse result binds the zero test, branch, last-byte address, terminal
  quote checks, and write in FDE `[0xb7b0,0xb9bf)`.
- The typefind result binds get-length, the 17 comparison, short return,
  six-byte peek, and source-offset-18 read in FDE `[0x2ca0,0x2d8b)`.
- The report distinguishes initial fix present, later correction absent, and
  the bounded 1-to-4-byte residual for total lengths 18 through 21.
- Exact SHA-256, Build IDs, complete instruction/FDE count/hash, and canonical
  tar identity are enforced.
- Output is deterministic UTF-8/LF and contains no operational parser material.
