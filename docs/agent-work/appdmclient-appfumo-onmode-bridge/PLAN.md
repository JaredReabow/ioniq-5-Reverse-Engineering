# AppDMClient -> AppFUMO onModePriority bridge plan

## Objective

Produce a deterministic, execution-free, fail-closed exact-static package that
binds the recovered AppDMClient producer to the embedded AppFUMO session-bus
subscription, local Qt row-69 consumer, package-base globals, readiness predicate,
and conditional `copyWhatsNewFiles()` call.

The package must correct two previously provisional labels:

1. AppFUMO's `onModePriority` subscription call is `0xe308b` in session-bus FDE
   `[0xe2c30,0xe3296)`. It has empty service/path QString filters and fixed
   interface/member filters.
2. `0xe2fc5` is an unrelated fixed-service/fixed-path `sleep_status`
   subscription, not the `onModePriority` subscription.

## Exact inputs

- Canonical rootfs stream:
  `work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz`
  - size `879109759`
  - SHA-256 `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`
  - normalized inventory SHA-256
    `c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c`
- AppDMClient:
  - canonical member `/app/bin/AppDMClient`
  - reviewed copy
    `work/decrypted-eu-260128/extracted-partial-bsdtar/mango-rootfs/app/bin/AppDMClient`
  - SHA-256 `9a1fb796d7ac24fcce71c16e3dbee9306c888f43e705ee081f41b7d473978bd0`
  - Build ID `b2dbcc5231f444d8f1dd68eb7a2376323ce805df`
- Canonical outer AppUpgrade member `/app/bin/AppUpgrade`:
  - SHA-256 `5295c6e4c41fb9c03760cf006c58b66fcd11aeb4e6e889af6e31b062549b6df0`
- Structurally selected embedded AppFUMO:
  - outer offset `0x5721c8`
  - size `5066264`
  - SHA-256 `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`
  - Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`
- Homebrew LLVM tools, identity-bound by the strict manifest.
- Canonical session-bus configuration from the rootfs stream.

## Static contracts to bind

### AppDMClient

- FDEs:
  - sender `[0x4f1c0,0x4f58a)`;
  - checker `[0x67e30,0x69144)`;
  - staging `[0x7ff60,0x830e4)`;
  - mounted callback `[0x84700,0x84e2d)`;
  - state sender `[0x85340,0x85a90)`;
  - generated metadata dispatch containing row 84.
- Sender body constructs a signal with fixed path/interface/member, appends
  logical arguments in `int, QString, QString` order, obtains `sessionBus()`, and
  calls `send()`.
- Whole-text direct-call inventory to the sender body is exactly the four known
  sites. Keep generated row-84 forwarding separate from implementation callers.
- At selected call `0x685e7`, the accepted-state enumerand is fixed, the second
  QString comes from the checker input source string, and the first QString
  comes from the parsed/reference-version path.
- Staging copies its source QString and passes it to the checker at `0x8079d`.
  The port/index-1 mounted callback passes its first QString into staging at
  `0x849a7` after copying it into `this+0x128`.
- The two state-sender calls in `[0x85340,0x85a90)` use empty QString arguments;
  they are not removable-path producers.

### Embedded AppFUMO

- Session-bus subscription FDE `[0xe2c30,0xe3296)` obtains `sessionBus()` and
  calls `QDBusConnection::connect` at `0xe308b` with independently empty service
  and path QStrings, fixed interface/member values, the local object, and the
  row-69 old-style slot.
- The interface/member byte digests must equal the AppDMClient emitter's exact
  interface/member byte digests. AppDMClient's fixed signal path is not compared
  because AppFUMO's path filter is empty.
- The separate call at `0xe2fc5` must remain classified as the unrelated
  `sleep_status` subscription with nonempty service/path/interface filters.
- Generated row 69 forwards logical `(status, usbVer, usbPath)` to body
  `0x10f4a0` with the exact SysV register mapping.
- Body `[0x10f4a0,0x10fa30)` stores:
  - status into global mode state `0x6d4fb8`;
  - `usbVer` into global QString `0x6d4fb0`;
  - `usbPath` into global QString `0x6d4fa8`.
- The accepted-state case is conditional. It checks object state, invokes
  readiness predicate `0xfed10`, and calls `copyWhatsNewFiles()` at `0x10f995`
  only when that predicate returns nonzero. The alternate local request path is
  not a copy invocation and must not be promoted to one.
- Predicate FDE `[0xfed10,0xff280)` selects global `0x6d4fa8` in accepted mode
  and checks the package-base What's New directory/archive classes.
- `copyWhatsNewFiles()` FDE `[0x101110,0x104c1b)` selects global `0x6d4fa8` as
  package base in accepted mode, then constructs the top-level archive class
  `<package-base>/.whatsnew.tar.gz`; reuse but independently verify the accepted
  producer-provenance anchors rather than assigning meaning from literals alone.

## Canonical session-bus boundary

Stream and parse canonical `etc/dbus-1/session.conf`; require its exact selected
member identity, default-policy shape, `EXTERNAL` authentication declaration,
Unix temporary-directory listener class, `session.d` directory state, and
optional local-include state. Report policy permission separately from runtime
socket reachability, same-bus identity, uid, and SMACK labels.

## Public-output/privacy contract

Tracked reports must not expose supplied filesystem paths, target instruction
bytes, callable D-Bus coordinates, signal numeric values, commands, requests,
payloads, packets, or actuation steps. Fixed D-Bus values are retained only as
normalized roles, lengths, and SHA-256 values. The assessment may publish
link-time code addresses and normalized data-flow roles, as existing evidence
does, but not a trigger recipe.

Do not execute recovered targets, contact a bus, create/send a signal or method,
create media, modify firmware, flash, persist, or interact with a device.

## Deliverables

Worker-owned paths:

- `tools/uk_fw/appdmclient_appfumo_onmode_bridge.py`
- `tests/test_appdmclient_appfumo_onmode_bridge.py`
- `evidence/appdmclient-appfumo-onmode-bridge.md`
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-manifest.json`
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge.json`
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-exact-static.txt`
- `docs/agent-work/appdmclient-appfumo-onmode-bridge/WORKER.md`

Coordinator-owned paths:

- this `PLAN.md`
- `docs/agent-work/appdmclient-appfumo-onmode-bridge/CHECKPOINT.md`

No changelog/history/vulnerability-summary edits, commits, staging, pushes,
resets, stashes, or unrelated file changes.

## Analyzer requirements

- Explicit UTF-8 and fixed LF output through `sys.stdout.buffer`, independent of
  `PYTHONIOENCODING`.
- Reject non-regular, changing, oversized, aliased, linked, special, duplicate,
  or unexpected inputs/members.
- Reject duplicate JSON keys, schema drift, unknown/missing fields,
  Boolean-as-integer values, malformed literals/instructions/FDEs, unsupported
  provenance, contradictory states, identity/count/hash drift, anchor drift,
  direct-transfer drift, canonical inventory drift, and privacy-sensitive output.
- Bind supplied AppDMClient bytes to the canonical member.
- Bind supplied AppFUMO bytes to the structural extent of the selected embedded
  ELF in the canonical outer AppUpgrade member; do not include trailing resource
  metadata or a following ELF.
- Bind complete instruction and FDE inventories for both ELFs and exact LLVM tool
  identities.
- Keep runtime facts `null`/unknown rather than inferred from static permission.

## Required tests

- Exact report regenerates byte-for-byte and matches the retained report under a
  hostile `PYTHONIOENCODING`.
- Focused exact run validates canonical stream, both ELFs, structural extraction,
  Build IDs, complete instruction/FDE inventories, selected FDEs, direct-call
  inventories, anchor hashes, cross-binary literal-hash equality, and normalized
  findings.
- Mutation tests cover manifest schema/key/type/Boolean drift, binaries, rootfs,
  tool identity, instruction/FDE/direct-transfer/anchor/literal drift, embedded
  structural extent drift, canonical member drift, and privacy scanning.
- Unit tests cover strict JSON, strict tar naming/types, session policy parsing,
  wildcard-filter classification, and contradiction rejection.
- Focused command:
  `<platformio-env>/bin/python3 -m pytest -q tests/test_appdmclient_appfumo_onmode_bridge.py`
- Integration command after acceptance:
  `<platformio-env>/bin/python3 -m pytest -q tests`

## Acceptance criteria

1. Exact static continuity is established from the mounted callback's source
   QString through staging/checker, AppDMClient signal construction, AppFUMO's
   wildcard service/path subscription, row-69 assignments, readiness predicate,
   and conditional copy call.
2. `0x6d4fa8` is explicitly bound to row-69 logical `usbPath`; `0x6d4fb0` is
   explicitly bound to `usbVer`.
3. The sender and receiver interface/member byte identities match exactly.
4. The `0xe2fc5` mislabel is corrected and regression-tested.
5. Runtime delivery, same-bus reachability, sender influence, verifier success,
   command success, root, partition writes, boot acceptance, and persistence
   remain unclaimed.
6. The analyzer fails closed and tracked outputs satisfy the privacy contract.
7. Focused tests and the repository tests-scoped suite pass without executing a
   recovered target.
