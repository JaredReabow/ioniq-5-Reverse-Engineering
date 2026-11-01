# Checkpoint — SMACK privileged exec chain

## Status

Implementation and third-round remediation are complete. The first independent
read-only review returned `CHANGES_REQUIRED` on two package-integrity findings;
the second fresh review confirmed those repairs but returned `CHANGES_REQUIRED`
on glibc source-closure binding and explicit single-dot archive coverage. Both
new findings were addressed. A third fresh, strictly read-only review returned
`ACCEPTED` with no P0–P2 findings. The package is accepted but remains unstaged,
uncommitted, and unpushed.

## Result

The canonical configuration supports a conditional direct transition candidate:

```text
enumerated App::* task
  -> floor-labeled root-owned update anchor
  -> SMACK64EXEC=Privileged
  -> script-interpreter credential preservation
  -> ELF credential commit with task label Privileged
  -> onlycap label eligibility
```

All 27 canonical `App::* -> _` policy rules grant both read and execute. Linux
v4.1 checks the caller's pre-transition label against the inode's ordinary access
label for exec admission and separately performs a read check during file open.
The `SMACK64EXEC` label does not authorize opening the inode.

The transition changes the task's SMACK label, not UID or capability masks.
Effective SMACK override remains conditional on the applicable effective
capability and `onlycap` label eligibility.

The anchor does not reset PATH and reaches an unqualified command lookup. Exact
Bash/glibc identities and hash-bound loader source, generic secure-environment
list, and applicable x86-64 extra-variable definition establish the configured
loader filtering closure. Hash-bound Bash source establishes bash's UID/GID-based
privileged-mode predicate, ordinary environment import, guarded
environment-function import, and PATH-based lookup semantics. Runtime environment
influence and successful command execution remain unknown.

## Remediation completed

A public-source child memo identified the access-admission and credential-commit
boundaries. The package was corrected to:

- require both read and execute in every canonical App-to-floor rule;
- bind `smack_inode_permission()` and `smack_file_open()` semantics;
- distinguish ordinary access label admission from `SMACK64EXEC` transition;
- bind the exact ELF credential-commit source;
- state that credentials may commit before later loader failure;
- distinguish onlycap eligibility from effective override;
- preserve onlycap as a SMACK call-site gate, not a capability-set mask;
- bind bash's guarded environment-function import semantics without emitting a
  function definition or operational environment value;
- parse Bash's GNU Build ID from the already stable canonical byte buffer rather
  than reopening its pathname;
- internalize and hash-bind the archive hashing, stat-identity, member-name
  canonicalization, and inventory primitives instead of importing them from an
  unreviewed helper module;
- add explicit negative tests for a selected-member alias, unsafe single-dot and
  dot-dot names, duplicate canonical identity, nested policy alias, selected
  link, and selected special node;
- hash-bind and validate the applicable glibc x86-64
  `EXTRA_UNSECURE_ENVVARS` definition in addition to `rtld.c` and the generic
  removal list.

## Files

- `docs/agent-work/smack-privileged-exec-chain/PLAN.md`
- `docs/agent-work/smack-privileged-exec-chain/CHECKPOINT.md`
- `tools/uk_fw/smack_privileged_exec_chain.py`
- `tests/test_smack_privileged_exec_chain.py`
- `evidence/smack-privileged-exec-chain.md`
- `evidence/artifacts/application-candidates/smack-privileged-exec-chain-report.json`

## Current hashes

- analyzer: `49b2e96c0989f04510ed4b0ce5928763da4d092d27a6f3931a7424018abc6739`
- tests: `8174da93788da3da8bf3b0895c997301c58f4ebac85b05becbf616d1b4c70014`
- plan: `e08587ac3f0bcb21b92479ef79f20811de1d0ce855b70db400836d0c1c7647f0`
- assessment: `3097ade7eb03901e02834c0365266a3a3fe2e3a3029acfe6f66a22834f71d4ab`
- report: `c4cfa148c93a437ce3eb87656c6d7458e4c7b3869c9270be33c28df5933b46cf`
- report size: `9790` bytes

The checkpoint's own hash is recorded externally after prose freeze to avoid a
self-referential hash field.

## Validation

- focused pytest after third-round remediation: `15 passed in 6.76s`;
- Python compilation: passed;
- focused `git diff --check`: passed;
- retained report regeneration: byte-identical;
- report encoding: explicit UTF-8 bytes, LF-only, final LF;
- first independent review: `CHANGES_REQUIRED` on test coverage and imported
  helper identity; both findings remediated;
- second fresh review: `CHANGES_REQUIRED` on glibc source closure and explicit
  single-dot archive coverage; both findings remediated;
- full project suite after third-round remediation:
  `891 passed, 351661 subtests passed in 127.15s (0:02:07)`;
- retained full-suite log SHA-256:
  `ad78e7a4716eb0f858c9801c29951e3d0ab53a242a208fb1ec2bb6056ce663a0`;
- third fresh independent review: `ACCEPTED` with no P0–P2 findings;
- reviewer-focused suite: `15 passed in 6.76s`;
- reviewer-full suite: `891 passed, 351661 subtests passed in 128.55s`;
- post-acceptance focused suite after integration prose: `15 passed in 6.95s`;
- post-acceptance full suite after integration prose:
  `891 passed, 351661 subtests passed in 129.00s (0:02:08)`;
- post-acceptance full-suite log SHA-256:
  `4de45d1f3b9166d0038e2eded70ede3d1f1949701c8f0b8bbbb456c813600ea5`.

## Runtime limits

Not established: installed identity, loaded policy, live xattrs, source
credentials/capabilities/securebits/namespaces, `no_new_privs`, unsafe exec state,
path/mount admission, credential commit, complete interpreter loading,
environment influence, command execution, effective SMACK override, unrestricted
root, update acceptance, partition writes, slot activation, boot acceptance,
health, mark-good, rollback, recovery, or persistence.
