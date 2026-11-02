# Passive CarPlay/iAP2 bench-readiness plan

## Objective

Extend the existing disconnected, read-only bench capture so a future owner-run
capture can bind the installed CarPlay/iAP2 stack and its runtime prerequisites
to the exact recovered EU `260128` identities. Add a deterministic host-side
assessor that keeps installed identity, active service state, configured
UID/SMACK context, transport availability, public-CVE applicability, code
execution, root, and persistence as separate claims.

## Non-goals

- No USB, iAP2, AirPlay, HTTP, RTSP, pairing, media, or authentication traffic.
- No opening `/dev/mfd-iap2`, `/dev/ttyIAP20`, or `/dev/i2c-1`.
- No service start/stop/restart, module loading, network or radio changes, uevent,
  mount, target-file write, or package installation.
- No malformed descriptors or protocol inputs, exploit, crash reproducer,
  shellcode, root transition, flash operation, custom image, or persistence.
- No inference that the owner's installed unit matches EU `260128` until its
  passive hashes are captured.
- No inference of CVE applicability from passive runtime state alone. The
  separate static review now establishes a matching `ekey` mechanism with
  third-party CVE-2025-24132 attribution, while vendor-confirmed fixed bytes and
  runtime delivery remain absent.

## Repository evidence

- The exact recovered image enables `carplay_iAP2.service` and launches
  `/app/bin/iAP2Service-2.0` after `/etc/iap2_mod.sh`.
- The normal script path selects `usb_f_ncm`, `usb_f_iap2`, and `mfd-iap2`.
- The service uses `/dev/mfd-iap2`; `/dev/ttyIAP20` is an alternate endpoint.
- The exact MFi certificate/signature implementation opens `/dev/i2c-1`; passive
  node metadata cannot prove that an authentication chip or exchange is present.
- Intended SMACK labels are `App::projection` for the service and
  `System::iap20` for the iAP2 devices.
- Exact service, application, library, policy, and module hashes are already
  bound by `tools/uk_fw/carplay_sdk_applicability.py`.
- `bench_state_bundle.py` already captures all processes, credentials,
  capabilities, units, interfaces, listeners, `/proc/modules`, metadata, hashes,
  and SMACK xattrs without modifying the target.

## Deliverables

1. Extend `tools/uk_fw/bench_state_bundle.py` to passively capture:
   - CarPlay/iAP2 and mDNS unit state;
   - relevant process command lines and PATH values;
   - iAP2 device metadata and SMACK xattrs, plus passive `/dev/i2c-1` metadata;
   - exact service, script, policy, application, library, and module hashes;
   - parsed `/proc/modules` facts.
2. Add `tools/uk_fw/bench_carplay_readiness.py`:
   - strict UTF-8/JSON with duplicate and non-finite rejection;
   - stable no-follow input reads and canonical digest validation;
   - exact hash, unit, process, credential, SMACK, device, module, and optional
     port-7000 gates;
   - exclusive output creation;
   - false verdicts for protocol delivery, CVE match, crash, code execution,
     unrestricted root, and persistence.
3. Add focused tests for capture coverage, safety audit, fact parsing, positive
   prerequisites, mismatches, missing fields, malformed input, encoding
   independence, and no-overwrite output.
4. Add evidence prose and update the disconnected bench runbook.

## Acceptance criteria

- The emitted target script remains read-only, passes its forbidden-command
  audit, and passes `/bin/sh -n`.
- Every installed-identity gate uses an exact recovered SHA-256.
- The active-prerequisite verdict requires exact hashes, the active service,
  an EUID-zero `App::projection` service process, `/dev/mfd-iap2` with
  `System::iap20`, and all three normal transport modules.
- `/dev/ttyIAP20`, `/dev/i2c-1`, mDNS, and port 7000 remain separately reported
  and do not overconstrain the recovered wired path.
- No positive gate can set CVE applicability, code execution, root, or
  persistence true.
- Focused tests, `py_compile`, encoding checks, `git diff --check`, and the
  canonical test suite pass.

## Delegation status

The installed OpenRouter Fable role failed its static routing doctor because its
catalog entry is not advertised as native-subagent v2. Direct native Fable child
creation was also blocked by the host tool's mutually exclusive argument
validation. No provider was silently substituted and no paid probe was run.
