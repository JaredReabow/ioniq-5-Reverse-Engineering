# Plan — exact CVE-2017-16995 syscall-path applicability audit

## Objective

Determine whether the exact recovered kernel can dispatch the named syscall-based
eBPF verifier path required by CVE-2017-16995, without running recovered targets,
issuing target operations, loading code, creating communication endpoints,
constructing verifier input, or triggering the verifier.

## Method

1. Bind the exact kernel, configuration, authoritative symbol map, and upstream
   fix `95a762e2c8c942780948091f8f2a4f32fce1ac6f` by SHA-256.
2. Record `CONFIG_BPF=y`, disabled `CONFIG_BPF_SYSCALL`, and disabled
   `CONFIG_BPF_JIT` without turning those facts into a whole-BPF claim.
3. Bound the complete `sys_ni_syscall` range from the authoritative map and
   retain the weak `sys_bpf` alias plus its unconditional `-ENOSYS` return.
4. Independently bind native x86-64 syscall-table slot 321 to that exact stub.
5. Preserve contrary subsystem facts: classic BPF creation, validation,
   attachment, interpreter, and runtime-selection symbols remain compiled.
6. Treat the upstream commit message's v4.14 unprivileged-exploitability note as
   context only. Do not infer applicability from the vendor 4.1-derived banner
   and do not claim verifier internals were audited.
7. Add a schema-v2 Boolean-only classifier with an all-or-none fail-closed CLI,
   tri-state unknown for incomplete absence facts, explicit contrary functional
   syscall and alternate-entry facts, explicit classic-BPF scope, null runtime
   and impact outcomes, and exhaustive assertions for every classification field.
8. Integrate the narrow rejection into the retained artifact index, exploit
   inventory, handover, and IONIQ changelog.
9. Run focused tests and bytecode compilation with
   `python3`, then run `git diff --check`.
10. Leave the complete suite, public harness, and independent acceptance pending.

## Acceptance criteria

- The configuration, map range, native table base/slot, decoded slot pointer,
  and complete ENOSYS stub agree with the exact recovered artifacts.
- The verdict rejects CVE-2017-16995 only for the named syscall-based eBPF
  verifier path because the compile-time prerequisite is absent and native
  dispatch reaches the ENOSYS stub.
- Incomplete evidence yields `null`; an explicit functional syscall-path fact
  prevents rejection; an explicit alternate-entry fact is reported but does not
  become a global absence or unaudited CVE verdict.
- Classic BPF remains an explicit true input and output, preventing a general
  BPF-absence or safety claim.
- Model output is deterministic explicit UTF-8/LF and contains no address,
  invocation, constructed verifier input, communication endpoint, command,
  trigger, target bytes, race, or payload.
- Installed-device identity, all alternate eBPF entries, classic-BPF safety,
  verifier internals, runtime behavior, root, and persistence remain outside the
  conclusion.

## Non-goals and safety boundary

No recovered target execution; no target operation; no filter or program load;
no communication endpoint; no verifier input or instruction construction; no
verifier trigger; no race or payload; no crash attempt, privilege action, or
persistence. This is exact static applicability analysis of one named entry path,
not a verifier audit or a broad BPF safety assessment.
