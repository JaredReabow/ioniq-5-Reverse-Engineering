# Checkpoint — passive CVE-2017-6001 bench readiness

## Completed

- Extended the existing stdout-only disconnected-bench probe with a passive
  `/sys/bus/event_source/devices/*` inventory.
- Each observed source records its name, required numeric type state/value,
  optional CPU-mask state/value, optional device-symlink state/value, and an
  explicit inventory count.
- Added `tools/uk_fw/bench_perf_readiness.py`, which consumes only complete
  canonical `ioniq-bench-state/v1` JSON and classifies the version banner,
  `perf_event_paranoid`, registered `software` source, and registered `cpu`
  hardware source.
- The assessor uses stable no-follow bounded input reads, strict UTF-8/JSON,
  duplicate/non-finite rejection, canonical and per-section digest validation,
  deterministic canonical output, and exclusive no-overwrite creation.
- Updated the bench runbook and exact CVE-2017-6001 evidence.

## Safety boundary

The probe and assessor do not invoke `perf_event_open`, create or enable an
event, start a thread, schedule a race, open a device, write sysfs, contact a
target, or emit event attributes, trigger material, a payload, or firmware
bytes. Positive passive gates do not establish exact installed kernel bytes,
syscall acceptance, a compatible event combination, stale context use,
corruption, privilege gain, root, or persistence.

## Validation

- Focused tests: `30 passed, 20 subtests passed`.
- Generated probe safety audit and POSIX-shell syntax: pass.
- Generated probe size: `31,487` bytes.
- Generated probe SHA-256:
  `b13cf99ee0c64aba244ae72f6a0ca9eeebcb9eccb0d785974b7df2771b05076a`.
- `py_compile`: pass.
- `git diff --check`: pass.
- Canonical repository suite: `1099 passed, 352357 subtests passed in 174.43s`.
- Canonical suite-log SHA-256:
  `3f1028f0f83d29cddbf25d6ed8043406e9a8ec745f199d7a545c7a5535ebcfe7`.

## Delegation

The named Fable binding was not usable because its configured route fails the
native-subagent `multi_agent_version=v2` doctor check. Direct child creation was
also blocked by the host API's conflicting required argument forms. No worker
ran, no private project context was sent to an external provider, and no route
was silently substituted.

## Resume action

Run the complete suite, review the path-limited diff, update final validation
values, and commit only the new perf-readiness paths plus the bounded collector,
runbook, and CVE evidence changes.
