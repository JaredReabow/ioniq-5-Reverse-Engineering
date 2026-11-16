# Plan — exact-static CVE-2015-1805 pipe iterator applicability

## Objective

Determine whether CVE-2015-1805 applies to the exact recovered EU `260128`
kernel by comparing the complete pipe copy paths and complete iterator helpers
with the public source-level architecture, without executing recovered code or
performing any pipe, vector-copy, fault, concurrency, or exploit operation.

## Public contract

1. Retain and hash introducing commit
   `f6762b7ad8edd6abc802542ce845d3bc8adcb92f`, which introduced the legacy
   mutable-iovec atomic-copy fallback required by CVE-2015-1805.
2. Retain and hash mainline read-side iterator conversion
   `637b58c2887e5e57850865839cc75f59184b23d1` and write-side iterator
   conversion `f0d1bec9d58d4c038d0ac958c9af82be6eb18045`.
3. Verify from exact public v4.1 source that ordinary upstream Linux 4.1 already
   contains both iterator conversions. The first fully iterator-based upstream
   line is 3.16. Version history is context, not a vendor-kernel verdict.
4. Treat legacy stable adaptations and the CVE-2016-0774 follow-up as contextual
   alternatives, not required Linux 4.1 fixes.

## Exact-static method

1. Bind `work/eu-260128/vmlinux`, `kernel.config`, and authoritative
   `kallsyms.tsv` by SHA-256 and record the kernel Build ID.
2. Use authoritative-map successors to bound complete `pipe_write`,
   `pipe_read`, `copy_page_from_iter`, and `copy_page_to_iter` ranges.
3. Regenerate all four ranges from the exact ELF and compare byte-for-byte with
   the existing ignored static captures.
4. Bind all three direct pipe copy calls: two write-side calls to exact
   `copy_page_from_iter` and one read-side call to exact
   `copy_page_to_iter`.
5. For both complete helpers, bind argument registers, iterator fields,
   descriptor base/length loads and 16-byte traversal, copy-residual accounting,
   atomic-to-fallback progress, final iterator state stores, and the absence of
   descriptor-field stores. Preserve non-iovec branches and every function
   boundary.
6. Record exact-name absence of the two legacy helper symbols only as bounded
   corroboration, never as sole proof or a universal renamed/inlined absence.
7. Add a schema-v2 Boolean-only classifier with deterministic explicit UTF-8/LF,
   all-or-none fail-closed CLI, tri-state unknown for incomplete fixed-effect
   facts, an explicit broken-legacy-path fact with precedence, an optional
   progress-preserving legacy alternative, explicit ordinary-local-pipe scope,
   null runtime/impact outcomes, and exhaustive assertions for every emitted
   classification field.
8. Integrate the narrow exact-kernel rejection into the artifact index, exploit
   inventory, handover, and IONIQ changelog.
9. Run only focused tests, bytecode compilation, exact hash/patch/disassembly
   checks, and `git diff --check` with
   `python3` where Python is required. Do not run
   the complete suite or public harness and do not claim independent acceptance.

## Acceptance criteria

- All three public patches are byte-for-byte copies of the ignored captures and
  their hashes match the contract.
- The retained static artifact contains all four complete successor-bounded
  ranges and exact source-to-register/field bindings.
- The verdict rejects CVE-2015-1805 for this recovered kernel because all three
  pipe copy sites use iterator helpers and both complete helpers preserve
  bounded progress.
- The conclusion does not rely on the `4.1.27-abl` banner and does not claim
  general pipe/iov-iterator safety, absence of every vendor-equivalent defect,
  installed-device identity, runtime policy, successful triggering,
  corruption, root, or persistence.
- Incomplete fixed-effect facts yield unknown; explicit broken legacy-path
  evidence prevents rejection even when fixed facts are also supplied; an
  explicit progress-preserving legacy alternative can independently support a
  narrow rejection.
- The model report contains only non-operational classification metadata.

## Non-goals and safety boundary

No recovered-target execution; no pipes or iovecs; no target pipe operations;
no induced copy failure; no trigger, race, grooming, allocation strategy,
payload, or exploit code. The unrelated MICOM source and binary are excluded
from discovery, editing, execution, staging, attribution, and cleanup. No
commit, push, reset, checkout, stash, or removal is authorized.

## Execution status

Implementation began at `bbd3ae93d93a120e720e46b7c747f21ced233ef4` on
`main`. Concurrent work advanced the integration base first to
`844657d1c80fafac2be581af7af834708dd922f7` and then to
`0bf70dad0ae7bcd8189dc0cc0640343c970b85e5`, incorporating the pre-review and
final-validation changelog updates. The installed `astra_terra_builder_deepseek_flash` route is
static-ready for `deepseek/deepseek-v4.1-flash`, but runtime routing remains
unverified and no DeepSeek inference ran. This root exposes native delegation:
the exact package was implemented by a `codex-router/gpt-daybreak-blue-latest`
worker. Generic public research was delegated separately to Astra without
private target details. The root session coordinated, integrated, and reviewed
the package.
