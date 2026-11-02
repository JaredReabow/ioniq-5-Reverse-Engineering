# AirPlay session-setup divisor audit checkpoint

## Status

Implementation and canonical validation complete.

## Exact findings

- Library SHA-256: `ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0`.
- ELF `AirPlayReceiverSessionSetup`: `0x1998a..0x1c24a`, size `0x28c0`, SHA-256 `31f794fd8074bde88c42fea984664430b3c1a38b2ae43835936e2f25c6a56f41`.
- Ghidra `0x11998a` is the same function under image base `0x100000`.
- `SETUP` callback calls setup at `0x10632`.
- Encryption getter error and encryption type None branch to setup without the MFi-SAP decrypt path.
- MainHighAudio type is `0x66`.
- Exact recovered key `spf` is read and stored at session offset `+0x434`.
- `redundantAudio == 0` reaches `0x1a647` divisor load and `0x1a6c0 div ecx` without a divisor-zero guard.
- A zero ECX divisor produces architectural `#DE`.

## Deliverables

- `tools/uk_fw/airplay_session_setup_divisor_audit.py`
- `tests/test_airplay_session_setup_divisor_audit.py`
- `evidence/airplay-session-setup-divisor.md`
- `evidence/artifacts/projection-candidates/airplay-session-setup-divisor.json`
- `docs/agent-work/airplay-session-setup-divisor/PLAN.md`
- `docs/agent-work/airplay-session-setup-divisor/CHECKPOINT.md`

## Artifact identity

- File size: `10,231` bytes.
- File SHA-256: `2c9de034982def8e707689cb3be8b09342c3128a1c1fc4d831f392b84eafbc7a`.
- Canonical SHA-256: `e4eb3df14e54bd65c9fe3b52ea839d579eccae6989a495afab0fb2b8bbc7d527`.

## Validation

- Focused pytest: `4 passed`.
- JSON strict parse: passed.
- Deterministic output and exclusive no-overwrite behavior: covered by tests.
- Canonical pytest: `1078 passed, 352357 subtests passed in 174.77s (0:02:54)`.
- Canonical pytest log SHA-256: `220a9e29e05d3e7612018e96405d680b84ed32133c8cb5fa29f06f8dc9df3836`.
- `py_compile` and path-limited `git diff --check`: passed.
- Deterministic reproduction, normal-versus-UTF-16 output identity, and strict JSON parse: passed.

## Boundaries

No live delivery, authentication state, listener exposure, process termination, restart behavior, CVE identity, memory corruption, code execution, root, SMACK escape, persistence, or installed-unit impact is demonstrated. No protocol input was created or transmitted.

## Independent review

A Fable 5.1 review was requested, but the native child-thread interface rejected all accepted-looking argument forms with mutually contradictory model/selection validation. No child review ran and no provider substitution was attempted.
