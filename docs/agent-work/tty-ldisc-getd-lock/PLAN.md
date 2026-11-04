# Plan — exact CVE-2016-0723 retained line-discipline reference audit

## Objective

Determine whether exact recovered `vmlinux` retains the unlocked
line-discipline dereference fixed by CVE-2016-0723, without running recovered
targets, issuing target operations, creating terminals/threads/races, or
constructing trigger material.

## Method

1. Bind exact kernel identity, configuration, authoritative recovered map, and
   upstream fix `5c17c861a357e9458001f021a7afa7aab9937439`.
2. Retain the complete real `tty_ioctl` range and prove command `0x5424`
   dispatches to the reviewed path.
3. Bind wait-reference acquisition, post-acquisition `ldisc->ops->num` loads,
   exact four-byte user copy, same-object dereference, and common return order.
4. Prove every normal path after successful wait reaches dereference, including
   the user-copy error return.
5. Retain complete `tty_ldisc_ref_wait`, `tty_ldisc_ref`, and
   `tty_ldisc_deref` ranges and bind their exact read-lock calls.
6. Copy the authoritative public patch and record exact ELF, map,
   configuration, patch, assembly, and deterministic-report hashes.
7. Add a schema-v2 Boolean-only classifier with all-or-none fail-closed CLI,
   tri-state unknown for incomplete fixed-effect facts, an explicit contrary
   unlocked-dereference fact, null runtime/impact observations, and exhaustive
   assertions for every emitted classification field.
8. Integrate the narrow fixed-effect rejection into the candidate artifact
   index, exploit inventory, handover, and IONIQ changelog.
9. Run focused tests with `python3`, bytecode
   compilation, and `git diff --check`.
10. Leave the complete suite, public harness, and final independent acceptance
    pending for root review.

## Acceptance criteria

- Exact dispatch and all stated direct call identities match the recovered ELF
  and authoritative map.
- The retained assembly uses real half-open boundaries and includes complete
  ranges sufficient to review success and copy-error cleanup.
- Incomplete model facts do not become an affected or fixed assertion without
  the explicit contrary fact or all fixed-effect facts, respectively.
- Model output is deterministic UTF-8/LF and contains no addresses, target
  operation, terminal/race schedule, command, payload, target instructions, or
  firmware bytes.
- Documentation states fixed-effect rejection only, not broad TTY safety or
  patch provenance.

## Non-goals and safety boundary

No recovered target execution; no target operation; no terminal, thread, race,
trigger material, payload, crash attempt, privilege action, or persistence.
Installed-device identity, runtime policy, concurrency, stale access, impact,
and general TTY safety remain outside the conclusion.
