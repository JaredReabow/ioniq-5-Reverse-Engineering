# Intel MEI historical backport audit plan

## Goal

Compare public Linux Intel MEI memory-safety fixes after Linux v4.1 with the
exact EU `260128` `mei.ko`, preserving exact-static evidence and runtime
reachability boundaries.

## Constraints

- Do not load a recovered module or execute target code.
- Do not open `/dev/mei*`, issue ioctls, enumerate clients actively, or send CSE
  messages.
- Do not produce a trigger, race harness, corruption primitive, payload,
  signature bypass, flash command, or persistence mechanism.
- Public commit subjects are leads; reject or retain them only through exact
  function semantics.
- Keep runtime node identity, DAC/SMACK access, installed byte identity,
  firmware influence, corruption, privilege escalation, and persistence as
  separate observations.

## Work

1. Enumerate upstream `drivers/misc/mei` fixes after v4.1.
2. Freeze public commit and patch identities under ignored `work/`.
3. Hash and identify the exact recovered module.
4. Compare callback lifetime, callback ownership, fragment arithmetic, and
   firmware-disconnect completion paths.
5. Track a minimal exact-static excerpt and a non-operational classification
   model.
6. Extend only passive future-bench collection for interface identity.

## Acceptance

- Exact module SHA-256, Build ID, symbol addresses, and excerpt hash recorded.
- Each rejected historical premise is tied to exact instruction ordering.
- Missing runtime identity and access remain explicit unknowns.
- Focused tests, encoding-independent output, `py_compile`, and
  `git diff --check` pass.
