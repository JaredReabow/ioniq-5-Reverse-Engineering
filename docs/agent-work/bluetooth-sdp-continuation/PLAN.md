# Plan — exact Broadcom BSA SDP continuation CVE-2017-0785 audit

## Objective

Determine whether the public CVE-2017-0785 continuation-offset underflow /
out-of-bounds handle-read mechanism is present in the exact recovered
`process_service_search` functions in both PCB-selectable Broadcom BSA daemons.
The decision is bounded to the named mechanism and exact FDE ranges. It is not a
claim of general SDP safety or runtime Bluetooth exposure.

## Baseline and preservation

- Integration base and analysis HEAD: `a790800dba1e292a2aa27eae3e3a52c316643c9b`.
- Preserve all unrelated dirty residue. In particular, do not inspect, edit,
  stage, commit, or otherwise operate on
  `tools/uk_fw/ias_backend_soft/micom_service.c` or
  `tools/uk_fw/ias_backend_soft/micom-service`.
- Do not stage, commit, push, reset, stash, or discard any path.
- Do not execute a recovered target, make target syscalls, open a Bluetooth
  endpoint, use a radio, construct a packet/PDU or malformed fixture, or create
  exploit material. Host test subprocesses are permitted and must be described
  as host subprocesses, not target execution.

## Exact evidence contract

1. Bind the exact recovered ELFs:
   - `vbtd-51`: SHA-256
     `55e21d077082e97f56fb113a1d3b216c0f2e63aa02fc4cd754a6593bc6cec9e0`,
     Build ID `12175aa88ccff70cc56498e0208c9a51aac0c9e9`;
   - `vbtd-63`: SHA-256
     `c56b68fdd35b16b95688ab54a48ffb9f18034d925c057e86f8b9fe304f8b26b9`,
     Build ID `04141ed222ee8f150c0eb0e46fdb73624d168920`.
2. Use `/opt/homebrew/opt/llvm/bin/llvm-objdump` and `llvm-readelf` only for
   static ELF inspection. Regenerate and hash the FDE-bounded functions:
   - `vbtd-51 [0x841a40,0x841dbe)`, raw SHA-256
     `c91b38ace847bee71d0ab971c7f90d5d3fe5d5347296991b6961e91780cae5f4`;
   - `vbtd-63 [0x842230,0x8425a6)`, raw SHA-256
     `c35ecefa9aa2f28268df0c697c79e31c4fe000a1fc56c6ab9aff004dd1a36ef7`.
3. Preserve the public patch byte-for-byte as
   `evidence/artifacts/network-candidates/226ea26684d4cd609a5b456d3d2cc762453c2d75.patch`.
   Its required SHA-256 is
   `6f80d9cd3534d00e24c9c33717a282f1e6ae180f05f833e502c7a361e86b2721`.
   The relevant source change rejects when either the continuation offset does
   not equal the CCB expected offset or the recomputed result count is less than
   the continuation offset, before computing the unsigned difference.
4. Prove instruction semantics, not source-name recovery:
   - successful result accumulation binds `num_rsp_handles` to `%bp`;
   - continuation parsing binds `cont_offset` to `%r13w`;
   - the compare operand order and unsigned `ja` reject exactly when
     `cont_offset > num_rsp_handles`, not on equality;
   - the separate CCB `+0xb6` comparison enforces expected-offset equality;
   - both checks route to the shared code-5 error and dominate the subtraction;
   - both checks also dominate later use of the remaining count for handle
     indexing on the accepted path.
5. Record exact addresses for both variants, including offset assembly, bound
   compare/branch, expected-offset comparison, code-5 error call, subtraction,
   and bounded later indexing. Equality must be classified as safe for the
   subtraction because it yields zero remaining handles.
6. Treat direct fix-shaped behavior as evidence of effect only, not proof of an
   upstream cherry-pick. Missing exact source names are non-decisive.

## Deterministic finite model contract

Add `tools/uk_fw/bluetooth_sdp_continuation_model.py` and exhaustive tests. The
model is pure host control/arithmetic classification and emits no target or
operational Bluetooth material.

The finite input domain separates:

- Boolean syntax/continuation-path availability;
- an abstract continuation-offset/result-count relation: less than, equal, or
  greater than (no concrete protocol bytes or packet construction);
- bound-check semantics: legacy expected-offset-only versus unsigned
  result-count bound followed by expected-offset validation;
- Boolean match/mismatch with the current CCB expected continuation offset.

The classification must independently report the bound decision, expected-
offset decision, subtraction reachability, abstract subtraction result
(positive, zero, unsigned-underflow candidate, or not reached), later-indexing
gate status, and a tri-state named-mechanism verdict. The exact recovered state
must bind both binaries to the fixed semantics. Equality is accepted by the
unsigned bound, reaches a zero remainder when the other gates pass, and is
never classified as the named underflow mechanism.

Public APIs must require exactly the documented keys, reject missing or unknown
keys, reject invalid types (including integer stand-ins for Booleans), and reject
out-of-domain state strings. CLI arguments must be all-or-none, non-abbreviated,
and non-duplicated. Output must be deterministic sorted JSON encoded explicitly
as UTF-8 with one LF through `sys.stdout.buffer`, independent of
`PYTHONIOENCODING`.

Tests must exhaust the complete finite domain and independently assert every
output field, fail-closed parser/API behavior, deterministic report bytes and
hash, fixed public/static evidence facts, equality handling, branch polarity,
claim boundaries, and absence of operational material.

## Documentation and integration

Add:

- `evidence/broadcom-bsa-sdp-continuation-cve-2017-0785.md`;
- a sanitized exact-static excerpt under
  `evidence/artifacts/network-candidates/`;
- the byte-identical public patch;
- this plan and a final `CHECKPOINT.md`.

Minimally update the existing Bluetooth summary, network-candidate index,
exploit inventory, handover, and changelog. Re-check the changelog's existing
non-monotonic top order and insert the next entry without rewriting concurrent
history.

The bounded conclusion may reject the named continuation-offset
underflow/out-of-bounds information-disclosure mechanism for the two exact
functions. It must leave unknown: general SDP safety, direct cherry-pick
provenance, runtime handler/channel reachability, installed identity, adapter
and channel policy, malformed-input behavior, actual disclosure, code
execution, unrestricted root, persistence, and owner-device applicability.

## Validation and acceptance

Use `python3` and do not set a project-local
`TMPDIR` for boundary tests. Required checks:

1. focused model tests;
2. `py_compile` of model and test;
3. exact ELF identity, Build ID, FDE, bounded disassembly regeneration/address,
   branch-polarity, and raw-range hash checks;
4. retained-patch byte comparison and hash;
5. deterministic report regeneration and hash;
6. `python3 -m pytest -q tests`;
7. `git diff --check`;
8. the public harness if feasible.

Root review must inspect every changed/new path, verify the complete finite
matrix and both exact instruction paths, and confirm that only the reviewed
package plus pre-existing protected residue remains. No Git staging or commit is
part of acceptance.
