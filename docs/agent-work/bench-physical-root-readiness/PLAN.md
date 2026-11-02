# Passive physical-root readiness assessment plan

## Objective

Extend the existing read-only disconnected-bench state bundle and add a host-side assessor for the exact recovered CVE-2026-40225 SCSI/udev/systemd/debug-console chain. The result must distinguish observed installed prerequisites from physical delivery, root access, and persistence.

## Non-goals

- No malicious USB/SCSI/V4L descriptor, injected udev property, or exploit payload.
- No target write, service start, uevent, helper execution, unit request, VT switch, network/radio action, mount, flash, or boot modification.
- No claim that the owner's installed unit is affected until a complete passive capture matches the recovered identities.
- No claim of root access, practical console interaction, HECI reachability, or persistence.

## Repository evidence

- `evidence/systemd-udev-cve-2026-40225.md` binds the exact recovered helper instructions, rules, `debug-shell.service`, and benign VM controls.
- `tools/uk_fw/bench_state_bundle.py` emits and parses the canonical read-only `ioniq-bench-state/v1` capture.
- `tools/uk_fw/bench_root_readiness.py` demonstrates fail-closed canonical report validation and pass/fail/unknown gates.

## Design

1. Extend the existing probe only with passive metadata, unit-state, and SHA-256 observations for:
   - `scsi_id`, `v4l_id`, `systemd-udevd`, and PID 1 systemd;
   - the four exact udev rule files;
   - `debug-shell.service`;
   - `/dev/tty9`;
   - `debug-shell.service` load/active/unit-file state.
2. Add `tools/uk_fw/bench_physical_root_readiness.py`:
   - strict UTF-8, duplicate-key, non-finite-value, size, schema, and canonical-digest validation;
   - exact recovered-reference identity gates;
   - exact `/dev/tty9` character-device `4:9` metadata gate;
   - debug-shell load-state gate without requiring activation;
   - separate SCSI root-console and V4L property-injection prerequisite verdicts;
   - immutable false verdicts for physical delivery, root, and persistence.
3. Add focused unit tests for positive, missing, mismatch, malformed, duplicate-key, oversized-input, UTF-16 determinism, CLI no-overwrite, and passive-probe safety coverage.
4. Document use and limitations in `evidence/bench-physical-root-readiness.md` and update the existing bench runbook only in the owned passive-assessment command block.

## Failure behavior

- Malformed/corrupt canonical JSON is rejected.
- A complete capture with an observed mismatch yields `fail`.
- Missing/unavailable observations yield `unknown`, never implicit pass or fail.
- An incomplete/warned capture prevents a positive chain verdict.
- Output files are created exclusively and never overwritten.

## Acceptance criteria

- Existing probe safety audit and shell syntax tests pass.
- New observations appear in the emitted probe and canonical parsed facts.
- The assessor can positively identify all recovered SCSI root-console prerequisites from a synthetic sealed report while keeping physical delivery/root/persistence false.
- Missing and mismatched observations remain correctly separated.
- Normal and `PYTHONIOENCODING=utf-16` CLI output is byte-identical.
- Focused and canonical pytest suites pass.

## Routing

Astra owns architecture, safety boundaries, review, integration, commit, and push. The requested Fable builder is not dispatchable: the installed `openrouter/claude-fable-5.1` catalog entry is not advertised for native v2 subagents. No provider substitution or paid-route probe is permitted, so implementation proceeds in the root thread with this bounded plan.
