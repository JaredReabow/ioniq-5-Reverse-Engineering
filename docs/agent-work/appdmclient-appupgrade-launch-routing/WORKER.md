# Worker record: AppDMClient AppUpgrade launch routing

## Assignment

Implement the deterministic exact-static analyzer, strict manifest, retained
report, focused tests, and bounded assessment from the coordinator-owned
`PLAN.md`. Do not execute recovered targets or create any callable bus request,
update package, payload, flash action, or persistence mechanism.

## Execution mode

The configured native Flash route failed before inference with the exact error
`Unknown child model: deepseek/deepseek-v4.1-flash`. No worker inference
occurred. The coordinator completed the sequential fallback under the same
bounded contract.

## Implemented paths

- `tools/uk_fw/appdmclient_appupgrade_launch_routing.py`
- `tests/test_appdmclient_appupgrade_launch_routing.py`
- `evidence/appdmclient-appupgrade-launch-routing.md`
- `evidence/artifacts/update-candidates/appdmclient-appupgrade-launch-routing-manifest.json`
- `evidence/artifacts/update-candidates/appdmclient-appupgrade-launch-routing-report.json`
- update-candidate README entry
- this record

## Implementation summary

The analyzer:

- opens the canonical EU `260128` rootfs once with no-follow semantics, hashes
  it and streams its selected regular AppDMClient member from the same stable
  descriptor, then revalidates descriptor and pathname identity;
- requires the supplied ELF to be byte-identical to the canonical member;
- validates exact ELF size/SHA-256/Build ID and identity-bound Homebrew LLVM;
- validates complete instruction and unwind/FDE inventories;
- enforces selected FDEs, 130 machine anchors, five exact literal roles, and the
  complete four-call/no-jump transfer inventory to `0x8c0c0`;
- separates the x86-64 SysV hidden return operand from the logical
  `(int, QString, QString)` tuple;
- validates QVariant type tags/order, the method object, async-call site, and
  pending-reply return handling;
- classifies all four app-ID-300 direct callers and both QString producers;
- binds source root to `%r13`, source-derived AppUpgrade to stack slot `0x0`,
  and staged AppUpgrade to stack slot `0x8`;
- corrects the provisional slot-`0x8` interpretation: it is the staged
  destination, not the source-root parameter;
- validates the terminal marker split, the marker-absent staged validator, the
  marker-present source-derived request, and the no-request validator-false
  branch;
- leaves bus delivery, AppLauncher dispatch/argv, process creation/exec,
  credentials/label, update acceptance, partition writes, boot acceptance,
  root, and persistence unknown;
- emits deterministic UTF-8/LF JSON without supplied filesystem paths, target
  bytes, commands, callable endpoint coordinates, or request recipes.

## Validation before review

- exact analyzer run: PASS;
- manifest SHA-256:
  `61f3c6327bfeb521df2970f9fd281f828c0bd11ee219fc1ba98b5f29be53bf62`;
- initial retained report SHA-256:
  `7702f94c669c9e029a7fc6277f631ffe8c2a916f2c050fecd7a48ed88141afcd`;
- initial focused tests: `11 passed in 17.85s`;
- hostile `PYTHONIOENCODING=utf-16` regeneration is included in the focused
  suite and matched the retained UTF-8/LF report exactly;
- report privacy checks reject project paths, supplied input paths, command
  text, and callable API symbol text.

The first independent review returned `CHANGES_REQUIRED` for a rootfs
path-replacement gap between archive hashing and member extraction. Version
`1.0.1` removes the second pathname open, uses one stable no-follow descriptor
for both operations, revalidates descriptor/path identity after parsing, and
adds a deterministic replacement regression. The regenerated report SHA-256 is
`7584e9a7f4107f451bd690e05babefb60f6d20928ab27c5eb3efe4eb310b2449`.
Remediated focused validation passed: `12 passed in 18.37s`. The full
`tests/` suite passed with `868 passed, 351661 subtests passed in 115.01s`.
Fresh independent acceptance remains a coordinator step.

## Safety and scope

No recovered target executable was run. Work was limited to host-side hashing,
tar streaming, ELF parsing, identity-bound LLVM disassembly/unwind reading,
strict JSON handling, deterministic report generation, and tests. No bus or
device was contacted; no request, media image, update package, executable
payload, malformed input, signature-bypass change, partition write, slot
change, flash operation, or persistence mechanism was created.
