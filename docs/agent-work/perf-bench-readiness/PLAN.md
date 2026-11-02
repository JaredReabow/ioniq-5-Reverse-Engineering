# Plan — passive CVE-2017-6001 bench readiness

## Objective

Extend the disconnected, read-only bench evidence path so a future isolated capture can distinguish the runtime prerequisites for the exact recovered CVE-2017-6001 perf move-group candidate without invoking `perf_event_open`, creating an event, starting a thread, scheduling a race, or running recovered target code.

## Design

1. Extend `bench_state_bundle.py` with a passive inventory of `/sys/bus/event_source/devices/*`:
   - source name;
   - numeric `type` state/value;
   - optional `cpumask` state/value;
   - optional read-only `device` symlink state/value;
   - explicit source count.
2. Preserve the existing probe safety contract: stdout only, no target writes, no device opens, no sysfs writes, no service/radio/network action, and no perf syscall.
3. Add a host-only assessor which consumes only canonical `ioniq-bench-state/v1` JSON and classifies:
   - installed version-banner match separately from exact kernel identity;
   - observed `perf_event_paranoid` value and the narrow historical per-task policy implication;
   - registered `software` and `cpu` event sources;
   - unresolved syscall acceptance, compatible event construction, race, memory corruption, privilege gain, root, and persistence.
4. Use stable no-follow bounded input reads, strict UTF-8/JSON, duplicate/non-finite rejection, canonical digest validation, deterministic canonical output, and exclusive no-overwrite file creation.
5. Add focused tests for positive, negative, missing, malformed, duplicate, deterministic, and no-overwrite cases.

## Non-goals

- No perf event attributes, syscall wrapper, event creation, race schedule, timing code, heap grooming, crash attempt, exploit payload, credential change, or persistence.
- No claim that a banner, sysctl value, or registered PMU establishes exact installed bytes or exploitability.
- No physical-device or network interaction while the bench is unavailable.

## Acceptance

- The emitted probe still passes its static safety audit and POSIX-shell syntax check.
- Event-source records are explicit and fail closed on malformed required fields.
- The assessor is deterministic and retains all runtime/impact outcomes as unknown unless directly present in the passive capture.
- Focused tests and the canonical repository suite pass.
- Changes are reviewed path-by-path and committed without including unrelated worktree changes.

## Delegation status

The requested Fable worker route could not be used: the installed named Fable binding fails the native-subagent `multi_agent_version=v2` doctor check, and the host `create_child_thread` API rejects both documented argument forms because its exposed schema simultaneously requires conflicting top-level and structured selection fields. No provider was silently substituted.
