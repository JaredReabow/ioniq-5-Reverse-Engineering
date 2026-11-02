# AppLauncher app-ID-300 argv exact-static plan

Status: coordinator-owned plan. Do not edit from a worker.

## Objective

Bind the recovered EU `260128` canonical-rootfs `AppLauncher` bytes to the exact
static path by which a newly constructed app-ID-300 process receives its
`QStringList` and reaches the identified `QProcess::start` site. Separately bind
the embedded option-table source, the canonical absence of the external
`CarOption.csv` override, and the recovered `NE`/EUR fallback row without
promoting that row to an owner-unit runtime observation.

## Evidence contract

The package must fail closed on canonical-rootfs replacement, aliases, links,
special members, duplicate tar names, archive/schema/type drift, Boolean-as-
integer input, supplied-binary mismatch, tool identity drift, Build-ID drift,
whole-instruction/FDE inventory drift, selected FDE drift, direct-transfer
drift, machine-anchor drift, embedded-table drift, selected-row ambiguity, and
input changes during analysis.

The rootfs archive must be opened once with no-follow semantics where available.
Hashing, member inventory, `AppLauncher` extraction, and external-option-file
absence checks must use that same stable file description, followed by
descriptor and pathname revalidation.

## Static questions

1. Which FDE constructs a new dynamic `AppProcess`, and where are app ID,
   executable, and generated arguments stored?
2. Which call invokes the option builder for that object, and which builder
   argument mode is used?
3. Does the builder append the selected option list at loader-object offset
   `+0x28` to the generated list returned to `AppProcess+0x60`?
4. Does the launch FDE pass `AppProcess+0x58` as the program and
   `AppProcess+0x60` as the argument list at the identified `QProcess::start`?
5. What exact byte range initializes the embedded fallback table, how is it
   parsed, and is `/app/bin/CarOption.csv` absent from the canonical archive?
6. Is there exactly one recovered `NE` row, and what normalized roles, token
   count/order digest, and update-mode token role does it contain?
7. What runtime facts remain unknown, including owner-unit row selection,
   installed identity, D-Bus delivery, successful process creation/exec,
   credentials/SMACK label, update acceptance, partition writes, boot
   acceptance, and persistence?

## Outputs

- `tools/uk_fw/applauncher_app300_argv.py`
- `tests/test_applauncher_app300_argv.py`
- `evidence/artifacts/application-candidates/applauncher-app300-argv-manifest.json`
- `evidence/artifacts/application-candidates/applauncher-app300-argv-report.json`
- `evidence/applauncher-app300-argv.md`
- `docs/agent-work/applauncher-app300-argv/WORKER.md`
- application-candidate README entry

Ignored binaries, complete disassembly, raw fallback-table bytes, and temporary
analysis remain under `work/` or `/tmp`.

## Safety and claim boundaries

Do not execute recovered targets. Do not create a D-Bus request, executable
payload, update package, filesystem image, malformed input, signature-bypass
patch, flash command, or persistence mechanism. Public retained JSON must not
contain supplied filesystem paths, raw target instruction bytes, complete table
rows, callable requests, commands, or actuation steps.

Treat recovered fallback data as exact static evidence only. Do not equate it
with owner-unit runtime fields, successful row selection, a delivered launch,
`QProcess` acceptance, successful `exec`, privilege, root, update acceptance,
partition writes, boot acceptance, rollback behavior, or persistence.

## Validation

Run focused tests, hostile-encoding byte-equality regeneration, privacy/LF
checks, `git diff --check`, and the full tests-scoped suite:

```sh
<platformio-env>/bin/python3 -m pytest -q tests/test_applauncher_app300_argv.py
<platformio-env>/bin/python3 -m pytest -q tests
```

A fresh independent read-only review is required before checkpointing or
publication.
