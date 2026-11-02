# Passive physical-root readiness checkpoint

## Status

Implemented and accepted locally. This phase adds passive installed-prerequisite assessment for the exact recovered CVE-2026-40225 SCSI/udev/systemd/debug-console chain. It does not add or execute an exploit.

## Completed

- Extended `tools/uk_fw/bench_state_bundle.py` to capture only read-only metadata, hashes, and unit state for:
  - systemd and systemd-udevd;
  - scsi_id and v4l_id;
  - the four reviewed udev rule files;
  - debug-shell.service;
  - `/dev/tty9`;
  - debug-shell load/active/sub/unit-file state.
- Added `tools/uk_fw/bench_physical_root_readiness.py` with:
  - strict canonical bench-report validation;
  - exact recovered identity gates;
  - tty9 character-device `4:9` validation;
  - loaded-unit validation that does not treat inactive/disabled state as activation;
  - separate SCSI root-console and V4L property-injection prerequisite verdicts;
  - explicit false root, hardware-delivery, activation, interactive-console, and persistence verdicts;
  - deterministic UTF-8/LF output and exclusive output creation.
- Added focused tests in `tests/test_bench_physical_root_readiness.py` and extended `tests/test_bench_state_bundle.py` safety coverage.
- Added `evidence/bench-physical-root-readiness.md` and updated the passive command/coverage portion of `evidence/bench-runbook.md`.

## Validation

- focused: `34 passed, 20 subtests passed in 3.30s`;
- canonical: `1034 passed, 352351 subtests passed in 170.21s`;
- canonical log SHA-256: `b08b1dbde0d22c37834820696e794748a294925301a1e21296536f953674475a`;
- `py_compile`: passed;
- `git diff --check`: passed;
- emitted probe safety audit and POSIX-shell syntax: covered by focused tests;
- normal versus `PYTHONIOENCODING=utf-16` assessor stdout: byte-identical in focused tests.

## Routing

The requested Fable role was checked with the installed Astra doctor. The bound `openrouter/claude-fable-5.1` route exists but is not advertised for native v2 subagents. No provider was substituted and no paid/live probe was run. Implementation remained in the Astra root thread under the bounded plan.

## Remaining boundary

A future disconnected physical bench must establish installed identity and benign hardware-byte delivery. No malicious descriptor, helper execution, uevent, property injection, unit request, VT switch, command execution, root transition, target write, or persistence mechanism was produced or exercised.

## Resume action

1. Run the existing passive state capture on the isolated owner bench.
2. Parse it and run `bench_physical_root_readiness.py`.
3. If exact prerequisites pass, characterize control-character preservation with a benign nonexistent unit/marker only before considering any coordinated-disclosure reproducer.
