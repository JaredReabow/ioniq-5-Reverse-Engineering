# Passive bench root-readiness checkpoint

Status: implemented and locally validated on 2026-11-09; no physical bench input
exists yet and no runtime transition was attempted.

## Completed

- Added `tools/uk_fw/bench_root_readiness.py` version `1.0.0`.
- Strictly validates `ioniq-bench-state/v1` input size, UTF-8, duplicate keys,
  finite JSON values, schema, capture digest, and recomputed canonical digest.
- Emits deterministic `ioniq-bench-root-readiness/v1` JSON using fixed UTF-8/LF
  bytes and exclusive host-side output creation.
- Keeps complete capture, anchor identity/metadata, access label, execute label,
  Bash/loader identity, live onlycap, mount execution, live App-domain caller,
  policy read/execute, capability observation, and effective MAC-capability
  prerequisites as separate gates.
- Keeps credential commitment, complete ELF loading, effective override, root,
  and persistence false because the passive input cannot observe them.
- Validates capability hex/value consistency and does not infer missing ambient
  capabilities, no-new-privileges, or securebits.
- Exposes `/bin/date` and `/usr/bin/date` only as fixed observations, not runtime
  PATH resolution.
- Added 15 focused tests covering positive, fail, unknown, malformed, duplicate,
  oversized, non-finite, noncanonical section order, noexec, policy, capability,
  deterministic encoding, and exclusive-output cases.
- Expanded the passive collector with metadata/hash/`SMACK64`/`SMACK64EXEC`
  coverage for the anchor, shell/Bash, loader link/target, fixed date candidates,
  and relabel/setup scripts. The probe remains stdout-only and passes its static
  forbidden-token and `sh -n` audits.
- Added `evidence/bench-root-readiness-assessment.md`, including the public-only
  Linux/Gen5W route refresh and applicability limits.

## Validation

- combined focused suites:
  `40 passed, 22 subtests passed in 3.53s`;
- full suite:
  `906 passed, 351663 subtests passed in 127.79s (0:02:07)`;
- full-suite log SHA-256:
  `e6d738b7397206632f9dd47d9e83b9f00ab0b41f7c4ebc2638ebf2ead5005e96`;
- emitted passive probe size: `26125` bytes;
- emitted passive probe SHA-256:
  `ffecb19856528e01cf2ad81812d339e32913176094446b78f65714605babde8c`;
- probe audit: no violations; shell syntax valid;
- `py_compile`: passed;
- focused `git diff --check`: passed.

## Public-only refresh

- upstream Linux v4.1 Smack documentation SHA-256:
  `12537c124264758cc79ad003bea99b2384d0b7a3b787d1429bafb6999a730112`;
- upstream Linux v4.1 `fs/proc/array.c` SHA-256:
  `83432532e46d09c269eca0c892b39e3d677868830d9ceea2779f4951fc0a4662`;
- public heads observed: `g4933/wideopen` `ca2edcc`,
  `g4933/gen5w/navi_extended` `7605d04`, `xwtk/hmg_nemesis` `419d7e8`, and
  `g4933/gen5w/update-patcher` main `92f5193`.

No public repository was executed against recovered firmware. NEMESIS remains an
Android/AVNT-family route rather than evidence for this recovered Linux rootfs.
The update-patcher experimental branch was not executed, ported, or promoted to
an authentication-bypass claim.

## Delegation/routing

The requested Fable route check failed before delegation:
`openrouter/claude-fable-5.1` exists in the catalogue but is not advertised for
native subagents with `multi_agent_version=v2`. No paid probe, route substitution,
router change, or private external disclosure occurred. Work continued locally
rather than stalling.

## Boundaries

- no recovered-target execution;
- no D-Bus request, process signal, mount, target write, or label change;
- no malformed input, exploit payload, replacement executable, or command-search
  object;
- no updater invocation, signature bypass, partition write, flash command, slot
  change, persistence mechanism, radio interaction, or production network use.

## Next exact action

When a disconnected owner bench and an already-authorized console are available,
run the reviewed stdout-only collector, parse the capture on the host, then run
the readiness assessor. A passing report permits only a separately reviewed
bounded runtime-observation design; it is not authorization or evidence to invoke
the anchor.
