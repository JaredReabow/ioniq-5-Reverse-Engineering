# Passive CarPlay/iAP2 bench-readiness checkpoint

## Completed

- Extended the disconnected stdout-only state probe with exact CarPlay/iAP2
  units, process command-line/PATH selection, device metadata, SMACK xattrs,
  service/application/library/module metadata and hashes.
- Added canonical `facts.modules` parsing for captured `/proc/modules` lines.
- Added deterministic `bench_carplay_readiness.py` with:
  - stable no-follow reads;
  - strict UTF-8/JSON, duplicate-key and non-finite rejection;
  - canonical input/output digests;
  - sixteen exact recovered identity gates;
  - loaded/active service, EUID/SMACK process, device, module, alternate tty,
    mDNS, and informational port-7000 gates;
  - exclusive no-overwrite output.
- Added passive `/dev/i2c-1` metadata/SMACK capture and a separate character-node
  verdict for the exact MFi certificate/signature transport.
- Kept `/dev/ttyIAP20`, `/dev/i2c-1`, mDNS, and port 7000 separate from the exact
  wired `/dev/mfd-iap2` prerequisite contract.
- Added focused positive, mismatch, missing-field, malformed-input, no-follow,
  encoding, and no-overwrite tests.
- Added evidence prose and integrated the assessor into the disconnected bench
  runbook.

## Safety and claim boundary

- The target probe remains read-only and passes its forbidden-command audit and
  POSIX-shell syntax test.
- No device is opened; no service/module/interface/radio state is changed; no
  packet, iAP2 frame, AirPlay request, or malformed input is sent.
- Positive results bind passive installed/runtime prerequisites only.
- The passive report does not decide CVE applicability. The separate static
  review now establishes an `ekey` stack-write mechanism with third-party
  CVE-2025-24132 attribution; vendor-confirmed fixed bytes, phone-to-parser
  delivery, crash, code execution, unrestricted root, flashing, and persistence
  remain absent.

## Validation

- focused CarPlay/state scope: `37 passed, 20 subtests passed in 1.52s`;
- `py_compile`: passed;
- path-limited `git diff --check`: passed;
- emitted probe audit and `/bin/sh -n`: passed; probe SHA-256
  `77f3439cf5238c4b8320698abac4a71148757dbcba3b4e09a31b19060d406c63`;
- positive fixture assessor output SHA-256:
  `5238691b464b0400eee976c43602757ef7062d1b309a86f25fa53d5d6657c138`;
- canonical suite: `1074 passed, 352357 subtests passed in 173.07s (0:02:53)`;
  log SHA-256
  `cd2a3534b0a9d13edbd484673e7c1a33b5567331f2dcb6ae103078b5952ddacd`.

## Files

- `tools/uk_fw/bench_state_bundle.py`
- `tools/uk_fw/bench_carplay_readiness.py`
- `tests/test_bench_state_bundle.py`
- `tests/test_bench_carplay_readiness.py`
- `evidence/carplay-bench-readiness.md`
- `evidence/bench-runbook.md`
- `evidence/carplay-iap2-sdk-applicability.md`
- `docs/agent-work/carplay-bench-readiness/PLAN.md`
- `docs/agent-work/carplay-bench-readiness/CHECKPOINT.md`

## Next actions

1. On a future disconnected owner bench, emit/audit the probe, capture stdout,
   parse it, and run the assessor before any protocol interaction.
2. If exact identities match, preserve the report and independently review
   active process capabilities, device major/minor values, interfaces, and
   listener ownership; do not infer CVE applicability.
3. Continue exact-static setup-dictionary consumer analysis and seek lawful
   affected/fixed SDK bytes.
4. Only after passive identity and restore prerequisites are independently
   reviewed should a separate, explicitly approved bench protocol plan be
   considered.

## Delegation

The configured OpenRouter Fable role remains blocked because its catalog entry
is not native-subagent v2. Direct Fable child creation also failed the host
API's mutually exclusive `model`/`selection` validation. No provider was
substituted and no paid probe was run.
