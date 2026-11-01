# Passive bench root-readiness assessment

## Objective

Build a deterministic host-side assessor for a completed
`ioniq-bench-state/v1` JSON capture. The assessor turns passive runtime evidence
into explicit gates for the configured direct SMACK transition, while keeping
UID, Linux capabilities, SMACK access admission, execute-label selection,
credential commitment, complete ELF loading, effective MAC override, root, and
persistence separate.

## Non-goals

- no target execution, D-Bus call, process signal, mount, write, label change,
  updater invocation, malformed input generation, exploit payload, flash command,
  persistence action, or network/radio operation;
- no claim that a static recovered image matches the owner unit;
- no automatic recommendation to execute the update anchor;
- no inference of securebits, tracing state, shared-fs state, successful
  interpreter loading, or post-transition access from capability masks;
- no treatment of `onlycap=Privileged` as capability acquisition.

## Inputs and trust boundary

The only input is JSON emitted by `tools/uk_fw/bench_state_bundle.py parse`.
The assessor must reject duplicate JSON object keys, oversized input, wrong
schema, malformed top-level structures, malformed digests, or a mismatched
`canonical_sha256`. An incomplete capture remains analyzable only as unknown
runtime state and can never produce a ready verdict.

Expected recovered identities are constants with documented provenance:

- `/etc/update_start_5w.sh.ori` SHA-256
  `06c3ab7e24b082c24a81299f0627245c0281bc5d519005cd921c13707eb5e838`;
- `/bin/bash` (and a hash-followed `/bin/sh`) SHA-256
  `783a69b9b27fae5da3fa93e441467160d6e760f3a79048a4dd02d98b571ad0aa`;
- `/lib/ld-2.25.so` (and a hash-followed loader symlink) SHA-256
  `0dfa16d8b5c9b35fb161a6f5dab48e7b267531ecf8ec3bf3ac74de61ce2ad99e`.

## Gate model

Each gate is `pass`, `fail`, or `unknown`; missing observations are never zero or
false. The report separately assesses:

1. complete/canonical capture identity;
2. installed anchor hash and root-owned mode `0700` metadata;
3. installed anchor `SMACK64=_` and `SMACK64EXEC=Privileged`;
4. Bash and dynamic-loader identities;
5. live `onlycap=Privileged`;
6. a live `App::* -> _` rule granting both read and execute for each candidate;
7. root-mount pathname execution not blocked by an observed `noexec` option;
8. live `App::*` caller candidates and their UID/GID, capability, seccomp,
   optional no-new-privileges, and PATH observations;
9. effective `CAP_MAC_OVERRIDE`/`CAP_MAC_ADMIN` as a separate usefulness gate;
10. fixed stock `date` candidates only as observations, never as proof of runtime
    PATH resolution.

A bounded runtime-chain-ready verdict requires the capture, identity, label,
policy, mount, and source-credential gates. Effective MAC override remains a
separate verdict and is not required merely to observe the same-UID label
transition.

## Files

- `tools/uk_fw/bench_root_readiness.py`
- `tests/test_bench_root_readiness.py`
- `evidence/bench-root-readiness-assessment.md`
- `docs/agent-work/bench-root-readiness/CHECKPOINT.md`

## Acceptance criteria

- strict duplicate-key and size rejection;
- canonical-input identity verification;
- deterministic UTF-8/LF JSON independent of `PYTHONIOENCODING`;
- explicit positive, mismatch, and unavailable tests for every critical gate;
- no import from mutable analysis helpers or execution of capture contents;
- output never calls a candidate exploitable or proves root/persistence;
- focused and complete repository tests pass.

## Verification

```sh
/Users/leo/.platformio/penv/bin/python3 -m pytest -q tests/test_bench_root_readiness.py
/Users/leo/.platformio/penv/bin/python3 -m pytest -q tests
/Users/leo/.platformio/penv/bin/python3 -m py_compile \
  tools/uk_fw/bench_root_readiness.py tests/test_bench_root_readiness.py
git diff --check -- \
  tools/uk_fw/bench_root_readiness.py \
  tests/test_bench_root_readiness.py \
  evidence/bench-root-readiness-assessment.md \
  docs/agent-work/bench-root-readiness
```
