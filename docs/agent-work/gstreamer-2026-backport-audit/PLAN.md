# GStreamer 2026 backport exact-static audit plan

## Scope

Create a separate, offline, fail-closed audit package for the exact canonical
`work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz` archive and the named
CVE-2026-2921 / CVE-2026-2922 implementation-fix semantics. The package will
not execute recovered targets, create or parse media, retain binaries or full
disassemblies, or provide trigger/delivery procedures.

## Implementation

1. Pin the canonical archive size, SHA-256, member count, and inventory digest.
2. Stream only the selected RIFF and RealMedia regular members from the tar,
   rejecting selected aliases, duplicates, links, special nodes, missing
   members, identity drift, and changing/nonregular/oversized inputs.
3. Pin exact Homebrew LLVM executable bytes and version; cap tool input/output
   and temporary work; parse disassembly, unwind FDEs, build IDs, and the RIFF
   exported symbol fail-closed.
4. Pin full instruction/FDE counts and canonical digests plus bounded reviewed
   anchors. Validate the RIFF multiplication width/order/default path and the
   RealMedia index/check/store/adapter-overlap and local extent-copy argument
   sequence.
5. Derive three separate verdicts (`riff_palette`, `rm_fragment_index`, and
   `rm_fragment_extent`) with implementation patch state distinct from the
   exact invariant, architecture effect, exploitability, and runtime outcome.
6. Emit deterministic UTF-8/LF JSON through `sys.stdout.buffer`, independent of
   `PYTHONIOENCODING`.

## Evidence and tests

- Add a strict manifest, deterministic report, bounded exact-static excerpt,
  and a public-lineage/claim-boundary evidence note.
- Add unit tests for schema/JSON strictness, archive safety, changing and
  bounded files, exact LLVM identity, malformed/duplicate/truncated tool
  output, complete identity and semantic drift, contradictory states,
  deterministic hostile-encoding output, privacy/non-operational content, and
  exact report equality when canonical artifacts are available.
- Run the focused test file with `/Users/leo/.platformio/penv/bin/python3`,
  `py_compile`, two deterministic regenerations (including hostile
  `PYTHONIOENCODING`), UTF-8/LF checks, and `git diff --check`.

## Claim boundary

The supported exact state may establish only the requested local machine-code
invariants and bounded object-field fact. Delivery, parser execution, crash,
information disclosure, code execution, privilege/root, persistence, and exact
installed/runtime reachability remain unknown. No downstream library behavior
or exact RIFF downstream memory effect will be inferred.
