# Worker record: AppDMClient → AppFUMO priority-mode bridge

## Assignment

Implement the worker-owned deterministic exact-static analyzer, focused tests,
manifest, retained JSON report, exact-static record, and bounded assessment from
the coordinator-owned `PLAN.md`. Do not edit the plan or create the coordinator
checkpoint.

## Execution mode

The configured native Flash route could not be dispatched. The exact native
child-tool error was `Unknown child model: deepseek/deepseek-v4.1-flash`.
No worker inference occurred. Per the orchestration fallback, implementation was
completed sequentially in the current thread without changing path ownership.

## Implemented paths

- `tools/uk_fw/appdmclient_appfumo_onmode_bridge.py`
- `tests/test_appdmclient_appfumo_onmode_bridge.py`
- `evidence/appdmclient-appfumo-onmode-bridge.md`
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-manifest.json`
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge.json`
- `evidence/artifacts/update-candidates/appdmclient-appfumo-onmode-bridge-exact-static.txt`
- this record

The coordinator-owned `PLAN.md` was not edited. No `CHECKPOINT.md` was created.

## Implementation summary

The analyzer:

- streams and hashes the complete canonical rootfs archive;
- validates its complete normalized tar inventory and selected-member metadata;
- binds the supplied AppDMClient to the canonical member;
- binds the supplied AppFUMO to the exact structural extent selected from the
  canonical outer updater;
- validates Build IDs and identity-bound Homebrew LLVM tools;
- hashes complete instruction and FDE inventories for both ELFs;
- checks selected FDEs, machine anchors, and direct-transfer inventories;
- validates the mounted-callback → staging → checker → sender producer chain;
- validates sender argument order, session-bus acquisition, and signal send;
- corrects the priority-mode subscription to `0xe308b` and preserves `0xe2fc5`
  as a distinct unrelated fixed-filter subscription;
- compares emitter and receiver interface/member values by length and SHA-256
  without retaining raw values in public output;
- validates generated row-69 forwarding, global assignments, readiness gating,
  the conditional copy call, accepted-mode package-base selection, and the
  bounded archive-path class;
- strictly parses the canonical session configuration and separates policy
  permission from runtime reachability and sender identity;
- emits fixed UTF-8/LF bytes and privacy-scans its normalized report.

## Validation

Pre-review validation performed in this thread:

- manifest generation from the exact supported inputs;
- one complete exact analyzer run: PASS;
- retained report SHA-256:
  `3a6fce587a17d0787ec75d863b46d66844295660af4b7fc58b095b68aa09d1d9`;
- manifest SHA-256:
  `9a3b105a9e5e7bacb3f179f5162b1dfb860caf1cebce2a45c1709e5266f9bc24`;
- focused unit subset before retained-package completion:
  `11 passed, 6 deselected, 24 subtests passed`.

Final focused and tests-scoped results are intentionally left for the
coordinator/reviewer checkpoint after independent read-only acceptance.

## Safety and scope

No recovered target executable was run. Only host-side hashing, tar streaming,
ELF parsing, LLVM disassembly/unwind reading, JSON/XML parsing, and tests were
used. No bus was contacted and no signal, method, media, packet, update action,
flash operation, or persistence mechanism was created. No changelog, history,
vulnerability summary, unrelated work, staged state, commit, or remote was
modified.
