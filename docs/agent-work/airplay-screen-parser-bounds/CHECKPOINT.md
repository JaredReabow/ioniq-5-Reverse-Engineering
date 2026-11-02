# AirPlay screen parser bounds audit checkpoint

## Status

Implementation and validation are complete; publication is pending.

## Exact identities

- `libAirPlay.so`: 215,896 bytes,
  `ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0`.
- `libCarPlayMediaFramework.so`: 162,392 bytes,
  `69690210d1aa4dec33c77b0e80f1d3368f8a70bcb507c1b158b6245dc29eb2f3`.
- `libCoreUtils.so`: 1,200,368 bytes,
  `9104e2c16ee27e647fac090ee7f3aa4cc686b8caaea1dc24763af2950c0ebfae`.

## Closed findings

- The 128-byte screen header and uint32 body are read from an established
  `NetSocket` before opcode dispatch.
- Opcode 1 reaches exact `ScreenStreamSetAVCC`; opcode 0 reaches exact
  `ScreenStreamProcessData`.
- Screen context is `calloc`-zeroed; AVCC conversion retains header length `H`
  and prefix width `p`; start sets the one-time prepend flag.
- The growth path allocates and records exactly `2*S` bytes.
- The retained-header copy and each four-byte-start-code-plus-NAL write have no
  output-used-versus-capacity check.
- The bounded input helper accepts `p` in `{1,2,4}`, accepts zero NAL length,
  and advances input by `p`.
- For `S=p*N+L`, output is `H+S+(4-p)*N`; it exceeds `2*S` when
  `H+(4-p)*N>S`.
- The exact uint32-to-x86-64 socket route rules out a `2*S` arithmetic wrap.
  The candidate is output-capacity under-accounting, classified as exact-static
  CWE-787.

## Deliverables

- `tools/uk_fw/airplay_screen_parser_bounds_audit.py`
- `tests/test_airplay_screen_parser_bounds_audit.py`
- `evidence/airplay-screen-parser-bounds.md`
- `evidence/artifacts/projection-candidates/airplay-screen-parser-bounds.json`
- `docs/agent-work/airplay-screen-parser-bounds/PLAN.md`
- `docs/agent-work/airplay-screen-parser-bounds/CHECKPOINT.md`

## Current validation

- Focused tests: `6 passed`.
- Projection-focused tests: `14 passed`.
- Canonical suite: `1084 passed, 352357 subtests passed in 168.01s (0:02:48)`.
- Canonical log SHA-256:
  `f77938cd656708f855874ae91181d1bf040079537b399b909d260fc3a48bac36`.
- `py_compile`, path-limited `git diff --check`, strict JSON/ASCII parsing,
  deterministic reproduction, normal-versus-UTF-16 output identity, and
  exclusive no-overwrite behavior: passed.
- Artifact size: 18,092 bytes.
- Artifact file SHA-256:
  `2ae2670a770508816d22159f9ae6c1185f6dac598d51c304a0ccc57c7e1f8e00`.
- Embedded canonical SHA-256:
  `a01793627cae6f52c6befaf58c4e6c01cabfffd8e5a7494f3801fc00e5dcea54`.

## Boundaries retained

No protocol input was created or transmitted. No recovered code was executed.
Authentication, live delivery, crash/process behavior, reliable control-flow
influence, CVE identity, root, persistence, and installed-unit applicability
remain unproved.

A requested Fable independent review could not be launched because the child
thread tool rejected both supported argument forms (`Pass either
model/thinkingLevel or selection, not both` / `thinkingLevel requires model`).
No provider substitution was used.
