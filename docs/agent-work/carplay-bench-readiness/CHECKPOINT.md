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
- Kept `/dev/ttyIAP20`, mDNS, and port 7000 separate from the exact wired
  `/dev/mfd-iap2` prerequisite contract.
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

- focused CarPlay/state scope: `37 passed, 20 subtests passed in 2.01s`;
- `py_compile`: passed;
- path-limited `git diff --check`: passed;
- emitted probe audit and `/bin/sh -n`: passed; probe SHA-256
  `77d77a36f71ede78f0bc4a9b54fcc39b3c10853e58ebecf0e6270f03eeabeb8b`;
- normal-versus-UTF-16 assessor output: byte-identical, SHA-256
  `09611825c8d5f2583fb29f2338820ef6b4638e2aa5d5c8437877b75d63af5f71`;
- canonical suite: `1074 passed, 352357 subtests passed in 174.10s (0:02:54)`;
  log SHA-256
  `fc46638764d0a4c7890aa1bb68e6d6a138f85cce20263843be2e6d43febbf9a2`.

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
