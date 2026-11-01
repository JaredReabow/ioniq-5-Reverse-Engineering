# Configured SMACK `Privileged` exec-transition chain

## Scope

This package asks one narrow exact-static question: does the recovered EU 260128
configuration contain a direct path by which an already-running enumerated
`App::*` task can execute the stock update relabel anchor and select the SMACK
label named by `smackfs/onlycap`, without using AppLauncher or the session bus?

The answer is **yes as a configured transition candidate**, subject to runtime
admission and credential gates. This is not a demonstrated owner-unit execution,
UID escalation, effective SMACK override, unrestricted root result, update
acceptance, or persistence result.

No recovered target was executed. The analyzer performs host-side canonical-tar,
ELF-byte, text, and public-source checks only. It emits no payload, replacement
pathname, label-changing command, update package, flash operation, or persistence
mechanism.

## Canonical inputs

The analyzer binds its result to one stable no-follow description of:

- `work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz`
- size: `879109759`
- SHA-256: `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`
- members: `66836`
- normalized inventory SHA-256:
  `c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c`

The selected shell and loader identities are:

| Role | Size | SHA-256 | Build ID |
|---|---:|---|---|
| `/bin/bash` | 946216 | `783a69b9b27fae5da3fa93e441467160d6e760f3a79048a4dd02d98b571ad0aa` | `bbe47288a3fee7f0979fed1eb2794e5596f33113` |
| `/lib/ld-2.25.so` | 149184 | `0dfa16d8b5c9b35fb161a6f5dab48e7b267531ecf8ec3bf3ac74de61ce2ad99e` | not asserted here |

`/bin/sh` is the canonical absolute symlink to `/bin/bash`; bash's PT_INTERP is
`/lib/ld-linux-x86-64.so.2`, which canonically resolves to `ld-2.25.so`.

The Linux semantic model is hash-bound to upstream tag `v4.1`, annotated tag
object `8c36ccaef5b771db296df5d8ef1ecf03037b80f8`, peeled commit
`b953c0d234bc72e8489d3bf51a276c5c4ec85345`. Bash is bound to the recovered
GNU Bash 3.2.57 binary and hash-bound 3.2.57 source; loader filtering is bound to
hash-bound glibc 2.25 source.

## Configured label contract

The canonical relabel/setup scripts establish this installation contract:

| Object or setting | Configured value |
|---|---|
| `smackfs/onlycap` | `Privileged` |
| update anchor ordinary access label | `_` |
| update anchor `SMACK64EXEC` label | `Privileged` |
| update anchor owner/mode | root:root, `0700` |
| update anchor interpreter | `/bin/sh` |

The canonical archive itself preserves no SMACK xattrs. The values above are a
relabel/configuration contract, not proof of the xattrs or `onlycap` value on a
running unit.

The strict policy parser identifies 636 rules across 27 canonical policy files.
It finds 27 distinct `App::* -> _` rules. Every one grants both `r` and `x`.
That matters because Linux v4.1 exec admission is not controlled by the future
execute label:

1. the caller's **pre-transition** SMACK label and the inode's ordinary access
   label control the inode permission check for execute;
2. `smack_file_open()` separately requires read access to that same ordinary
   inode label, unless the pre-transition caller is already eligible for the
   applicable SMACK capability override;
3. `security.SMACK64EXEC` is not substituted for the inode's ordinary object
   label during those checks.

DAC, directory traversal, mount `noexec`, regular-file, tracing/unsafe-exec,
IMA if configured, and other VFS gates remain separate.

## Exec-transition semantics

Linux v4.1 `smack_bprm_set_creds()` first runs generic capability exec
processing. On the first script preparation, a distinct inode execute label is
placed into the **proposed** credentials. The script handler then opens and
prepares `/bin/sh`; because `cred_prepared` is already set, the later interpreter
preparation does not replace the selected SMACK transition.

The label becomes current only when the ELF loader reaches
`install_exec_creds()` and `commit_creds()`. This is later than opening the
script and earlier than all possible remaining ELF-loader work. Consequently:

- “the transition occurs at file open” is incorrect;
- “the transition occurs only after a completely successful exec” is also too
  strong, because later loader processing can still fail after credential
  commitment.

`SMACK64EXEC` changes the task's SMACK label. It does not itself change real or
effective UID, capability masks, mount state, or file bytes.

## UID, capabilities, and `onlycap`

For an ordinary Linux v4.1 exec by an euid-zero caller, with `SECURE_NOROOT`
clear, no relevant file capabilities, no bounding/inheritable reduction, and no
unsafe or `no_new_privs` truncation, generic capability processing predicts the
usual root-compatible permitted/effective capability result. That prediction is
not caused by SMACK and is not runtime evidence.

After a committed label transition to `Privileged`, `smack_privileged(cap)`
requires both:

1. the relevant capability in the effective capability set; and
2. `onlycap` unset or matching the task's current SMACK label.

Thus the configured label match creates **eligibility** to use effective
`CAP_MAC_OVERRIDE`/`CAP_MAC_ADMIN` at `smack_privileged()` call sites. It does
not manufacture those capability bits. It also does not globally mask or alter
the Linux capability sets. At least one specialized SMACK path uses a different
capability test, so `onlycap` must not be described as a universal kernel
capability filter.

## Shell and environment boundary

The stock anchor does not assign `PATH` and reaches an unqualified utility lookup
on its invalid-argument path. The exact bash identity and hash-bound Bash source
establish that command lookup consults the shell's `PATH` variable.

SMACK's label-only transition predicts secure-exec handling for the dynamic
loader. Hash-bound glibc 2.25 loader source, the generic removal list, and the
applicable x86-64 `EXTRA_UNSECURE_ENVVARS` definition establish the complete
configured removal-list composition. It removes named dangerous variables,
including `LD_LIBRARY_PATH`, `LD_PRELOAD`, and the x86-64-specific
`LD_PREFER_MAP_32BIT_EXEC`, but does not include `PATH`.

Bash's own privileged-mode decision is based on UID/GID mismatch, not a SMACK
label change or the loader's secure-exec state. With equal IDs, the hash-bound
source permits ordinary environment import and also contains its guarded
environment-function import path. This is a static semantic boundary only. It
does not establish that a relevant runtime caller controls the environment, that
a function import is applicable, that PATH resolves a different executable, or
that any resulting command starts successfully.

No environment value, function definition, candidate pathname, or executable
content is included in the retained report.

## Bounded conclusion

The recovered configuration supports this conditional chain:

```text
enumerated App::* task
  -> ordinary read + execute admission to floor-labeled anchor
  -> first script preparation selects SMACK64EXEC=Privileged
  -> interpreter preparation preserves that proposed label
  -> ELF credential commit changes the task label to Privileged
  -> onlycap label matches at later smack_privileged() checks
```

This route is independent of V-028 and the session bus. It is also narrower than
“root”: the source UID is not raised, Linux capability masks are separate,
credential commitment is not complete interpreter success, and an effective
SMACK override still requires the relevant capability bit.

## Runtime facts still required

A passive owner-unit capture must establish at least:

- installed artifact hashes and loaded policy identity;
- live access and execute xattrs on the anchor;
- live `onlycap`;
- source task UID/GID/groups, task label, parent, namespaces, capability masks,
  securebits, `no_new_privs`, and tracing/shared-fs state;
- pathname traversal, DAC, mount, and successful read/execute admission;
- whether credential commit and complete interpreter loading occur;
- the inherited environment and whether any relevant value is caller-influenced;
- resulting task UID, capability sets, SMACK label, and effective
  `smack_privileged(CAP_MAC_OVERRIDE)` outcome;
- a concrete useful object reachable after the transition;
- separately, any authenticated update, final-byte, write, slot, boot, health,
  mark-good, rollback, recovery, or persistence result.

Stock Linux v4.1 normally omits `NoNewPrivs` and securebits from
`/proc/PID/status`; absence must remain unavailable rather than inferred as zero.

## Deterministic package

- analyzer: `tools/uk_fw/smack_privileged_exec_chain.py`
- tests: `tests/test_smack_privileged_exec_chain.py`
- retained report:
  `evidence/artifacts/application-candidates/smack-privileged-exec-chain-report.json`
- report SHA-256:
  `c4cfa148c93a437ce3eb87656c6d7458e4c7b3869c9270be33c28df5933b46cf`
- report size: `9790` bytes

The analyzer owns and therefore hash-binds its archive hashing, stat-identity,
member-canonicalization, and inventory primitives. It fails closed on archive
identity/inventory drift, member aliases and duplicates, selected links or
special nodes, nested/aliased policy members, policy duplicates or malformed
rows, source/hash drift, input replacement during streaming, ELF-note drift, and
encoding-dependent output. Focused negative tests exercise selected aliases,
unsafe single-dot and dot-dot spellings, duplicate canonical identities, nested
policy aliases, and selected link and special-node types.
