# AppLauncher app-ID-300 argv implementation record

Implementation was coordinator-owned because the requested Fable route was
unavailable and no silent model substitution was permitted.

## Implemented

- Added a deterministic analyzer bound to the canonical EU `260128` rootfs,
  canonical AppLauncher member, supplied-member equality, executable Build ID,
  identity-bound Homebrew LLVM, complete instruction/FDE inventories, selected
  FDEs, direct-transfer inventories, machine anchors, literals, embedded table,
  row shape, selected-option order, and runtime-unknown schema.
- Used one no-follow rootfs descriptor for archive hashing, complete normalized
  inventory, selected-member streaming, external-option-member absence, and
  descriptor/path identity revalidation.
- Resolved strict complete-disassembly parsing by requesting
  `--no-show-raw-insn`; malformed instruction records remain fail-closed.
- Bound embedded initialization at `[0x4ba10,0x523c5)`, active source `+0x18`,
  embedded fallback `+0x20`, external replacement, and bounded recursive
  external-to-embedded fallback at `0x38df0`.
- Bound caller source offsets and selector destination fields.
- Bound the normal row predicate to formatted vehicle argument 4, energy
  argument 7, and the non-performance-one branch selected by argument 12.
- Established that embedded vehicle role `0x26` and energy role `8` uniquely
  identify split component 50; its EUR column is data, not a predicate.
- Bound 17 ordered selected options to loader `+0x28`, option-builder append
  loop `0x35c8e..0x35cd2`, generated `AppProcess+0x60`, program
  `AppProcess+0x58`, and `QProcess::start` at `0x1745d`.
- Kept the whole runtime argv and all delivery/execution/privilege/update/boot
  facts explicitly unknown.

## Validation

Focused tests cover retained-report byte equality, hostile
`PYTHONIOENCODING=utf-16`, privacy/LF bounds, exact table shape and drift,
strict duplicate-key/Boolean/anchor/transfer rejection, and rootfs pathname
replacement during descriptor streaming.

Coordinator validation:

- focused: `6 passed in 7.38s`;
- full tests-scoped suite: `874 passed, 351661 subtests passed in 121.87s`;
- `git diff --check`: passed.

Run:

```sh
<platformio-env>/bin/python3 -m pytest -q tests/test_applauncher_app300_argv.py
<platformio-env>/bin/python3 -m pytest -q tests
```

## Review status

Fresh independent read-only acceptance is still required. The requested exact
Fable dispatch (`openrouter/claude-fable-5.1`, high) failed with
`Unknown child model: openrouter/claude-fable-5.1`. No substitute reviewer was
silently selected. Do not publish or checkpoint as accepted until review covers
the exact retained bytes and test results.
