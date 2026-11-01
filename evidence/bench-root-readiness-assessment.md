# Passive bench root-readiness assessment

Status: host-side implementation complete; synthetic validation only. No physical
unit, target network, recovered executable, update, or exploit input was used.

## Purpose

`tools/uk_fw/bench_root_readiness.py` consumes the deterministic JSON produced by
`tools/uk_fw/bench_state_bundle.py parse`. It answers a narrower question than a
root exploit: whether one passive owner-bench capture contains the runtime
prerequisites predicted by the independently accepted static
`App::* -> _ -> SMACK64EXEC=Privileged` analysis.

The output deliberately does not call a candidate exploitable. It separates:

1. ordinary read/execute admission to the floor-labelled anchor;
2. execute-label selection and the configured interpreter chain;
3. a live source task's UID/GID and capability observations;
4. `onlycap=Privileged` label eligibility;
5. possession of `CAP_MAC_OVERRIDE` or `CAP_MAC_ADMIN`;
6. credential commitment, complete ELF loading, effective override, root, and
   persistence, which a passive capture cannot observe.

## Static identities used for comparison

| Object | Expected SHA-256 | Meaning |
|---|---|---|
| `/etc/update_start_5w.sh.ori` | `06c3ab7e24b082c24a81299f0627245c0281bc5d519005cd921c13707eb5e838` | recovered update anchor |
| `/bin/bash` and hash-followed `/bin/sh` | `783a69b9b27fae5da3fa93e441467160d6e760f3a79048a4dd02d98b571ad0aa` | recovered Bash 3.2.57 interpreter |
| `/lib/ld-2.25.so` and hash-followed loader link | `0dfa16d8b5c9b35fb161a6f5dab48e7b267531ecf8ec3bf3ac74de61ce2ad99e` | recovered glibc 2.25 loader |

These identities are references, not owner-unit observations. The assessor treats
an observed mismatch as `fail`, absence/query failure as `unknown`, and never
silently substitutes mutable extracted-tree bytes.

## Input hardening

The assessor:

- caps input at 64 MiB;
- decodes strict UTF-8;
- rejects duplicate JSON object keys and non-finite JSON constants;
- requires exact schema `ioniq-bench-state/v1`;
- validates lowercase 64-hex capture and canonical digests;
- recomputes the input report's canonical digest before using facts;
- validates relevant object/list/record types;
- checks capability hex/value consistency instead of trusting capability names;
- never executes or imports capture contents;
- writes deterministic UTF-8/LF JSON through `sys.stdout.buffer`;
- creates a requested output file exclusively rather than overwriting it.

## Runtime gates

A report's `runtime_chain_prerequisites_observed` value can become true only when
all of the following are `pass`:

- the source capture is complete and warning-free;
- anchor hash, root ownership, regular-file type, and mode `0700` match;
- anchor `SMACK64` is `_` and `SMACK64EXEC` is `Privileged`;
- Bash and loader identities match the recovered references;
- live `onlycap` is exactly `Privileged`;
- the longest captured mount covering the anchor does not advertise `noexec`;
- at least one live `App::*` process has observed effective/filesystem UID zero,
  structurally complete capability sets, and a live `App::* -> _` rule granting
  both read and execute.

The separate `effective_mac_override_prerequisites_observed` value additionally
requires that an otherwise eligible caller has an observed effective
`CAP_MAC_OVERRIDE` or `CAP_MAC_ADMIN`. It still does not prove that a
`smack_privileged()` call occurred or succeeded.

`NoNewPrivs` and `CapAmb` remain nullable because stock Linux v4.1 normally omits
them from `/proc/PID/status`. Securebits are not present there and are not inferred.
Seccomp and available values are retained per caller.

## PATH and `date` boundary

The expanded passive collector records metadata, hashes, `SMACK64`, and
`SMACK64EXEC` state for `/bin/date` and `/usr/bin/date`, along with the captured
PATH for each allowlisted process. The assessor exposes those fixed objects as
observations only. It does not claim that either is the first runtime resolution,
that PATH is caller-controlled, or that a command would execute. Non-default PATH
directories remain an explicit bench follow-up rather than triggering dynamic
pathname enumeration in the passive probe.

## Collector extension

The same read-only collector now also records metadata, hash, `SMACK64`, and
`SMACK64EXEC` state for:

- `/bin/sh`, `/bin/bash`;
- `/lib/ld-linux-x86-64.so.2`, `/lib/ld-2.25.so`;
- `/etc/smack-relabel-ro.sh`, `/etc/smack_setup.sh`, and
  `/etc/smack_setup_recovery.sh`;
- `/etc/update_start_5w.sh.ori`;
- `/bin/date`, `/usr/bin/date`.

Symlink metadata remains explicit. Hashing follows the current target and therefore
cannot replace the link-target observation.

## Public-source refresh

A generic public-only refresh was performed without sending private firmware
identities or findings to an external model:

- Linux v4.1 `Documentation/security/Smack.txt`, fetched from the upstream
  Torvalds repository, SHA-256
  `12537c124264758cc79ad003bea99b2384d0b7a3b787d1429bafb6999a730112`;
- Linux v4.1 `fs/proc/array.c`, SHA-256
  `83432532e46d09c269eca0c892b39e3d677868830d9ceea2779f4951fc0a4662`;
- public `g4933/gen5w/navi_extended` still resolved to `7605d04` in the fetched
  history; no new Linux entry route was identified;
- public `g4933/wideopen` resolved to `ca2edcc`, with the recent visible history
  consisting of documentation changes;
- `xwtk/hmg_nemesis` advanced to `419d7e8`, but its documented DSP-OTA/NEMESIS
  route remains the Android/AVNT family previously classified as a platform
  mismatch for this recovered Linux rootfs;
- `g4933/gen5w/update-patcher` main remained `92f5193`. An experimental encrypted
  patch branch exists, but it was not executed, ported, or treated as proof of
  authentication bypass on this recovered build.

Repository search is discovery evidence only. Names, README claims, and commit
freshness do not establish applicability or owner-unit execution.

## Use

```sh
PY="${PYTHON:-$HOME/.platformio/penv/bin/python3}"
"$PY" tools/uk_fw/bench_state_bundle.py parse work/bench/state.log \
  --json work/bench/state.json
"$PY" tools/uk_fw/bench_root_readiness.py work/bench/state.json \
  -o work/bench/root-readiness.json
```

The output path is created exclusively. Review or move an existing report instead
of asking the tool to overwrite it.

## Limits

Even a fully passing passive report does not establish:

- invocation of the anchor;
- successful pathname traversal, open, or exec at the later observation time;
- script credential preparation or ELF credential commitment;
- complete Bash/loader startup;
- safe tracing/shared-fs/securebits state;
- caller control of environment or PATH;
- successful `date` resolution or command execution;
- effective SMACK override on a useful object;
- unrestricted root, update authentication, partition writing, slot activation,
  boot acceptance, mark-good, rollback, recovery, or persistence.

No payload, replacement executable, malformed input, D-Bus request, label change,
mount, flash command, or persistence mechanism was produced.
