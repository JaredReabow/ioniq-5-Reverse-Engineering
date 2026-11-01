# AppFUMO system-swap completion checkpoint

## Status

Implementation and canonical validation complete. Publication remains.

## Findings

- `getRootUpdated()` returns update-state object byte `+0x45`.
- A requested swap calls raw `0x148e70`; true stores handler byte `+0x240`.
- False rejoins the handler's current-latch log and does not abort the handler.
- External-unit handling requires `+0x240`, but its `QProcess::execute()` result
  is ignored.
- Navigation/resource handling and `/update/system_update_completed` marker
  handling follow without a `+0x240` gate.
- A downstream `UPDATE FINISH` path exists in the same handler, subject to
  additional state/file/scheduling predicates.
- Current public Android Gen5W `troubleShooter` research is inapplicable to the
  recovered x86-64 Linux/SMACK firmware by exact OS, architecture, service, and
  updater prerequisites.

## Paths

- `tools/uk_fw/appfumo_system_swap_completion.py`
- `tests/test_appfumo_system_swap_completion.py`
- `evidence/appfumo-system-swap-completion.md`
- `evidence/artifacts/update-candidates/appfumo-system-swap-completion.json`
- `evidence/artifacts/update-candidates/appfumo-system-swap-completion-exact-static.asm`
- `docs/agent-work/appfumo-system-swap-completion/PLAN.md`

## Validation

- focused: `7 passed`;
- related AppFUMO suites: `39 passed, 2 subtests passed`;
- canonical suite: `961 passed, 352187 subtests passed in 142.73s`;
- canonical log SHA-256:
  `928d00bf90aa048227b432f1410351df26a0976d861b0dc15caa2bac735f93e2`;
- report SHA-256:
  `85ae1e1bce51a275906708b294a400d9266c1e294d13ded5337be55459e57a06`;
- excerpt SHA-256:
  `090046925fcef57e58f0d6646c35532726ef6007e7cd6fe42745d41e22ec9cde`.

## Boundary

No target binary, update, public exploit, mount, copy, pipeline, reset, selector,
or partition operation was executed. Runtime effects, boot selection,
ABL/MICOM acceptance, health, mark-good, rollback, root and persistence remain
unknown.
