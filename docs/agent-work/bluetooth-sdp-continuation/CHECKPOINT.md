# Checkpoint — Broadcom BSA SDP continuation CVE-2017-0785 audit

## State — final implementation-worker self-review checkpoint

- Integration base and analysis HEAD:
  `a790800dba1e292a2aa27eae3e3a52c316643c9b`.
- Implementation and self-review ran in parent-assigned Daybreak child thread
  `06b3775a-bbc2-4080-8ffd-ecbda0b5d874`. Inside that child, a configured
  DeepSeek Flash worker dispatch was attempted after static route checks, but
  native dispatch rejected the model as unknown; no DeepSeek worker ran and no
  substitute provider/model was used. The parent then performed root review and
  obtained a separate read-only Daybreak worker review.
- Existing unrelated dirty residue was preserved. The protected
  `tools/uk_fw/ias_backend_soft/micom_service.c` and
  `tools/uk_fw/ias_backend_soft/micom-service` paths were not inspected,
  modified, staged, or included.
- Nothing was staged, committed, or pushed.

## Accepted bounded result

Both exact complete FDEs have the decisive public-fix effect:

- `vbtd-51 [0x841a40,0x841dbe)`, raw SHA-256
  `c91b38ace847bee71d0ab971c7f90d5d3fe5d5347296991b6961e91780cae5f4`;
- `vbtd-63 [0x842230,0x8425a6)`, raw SHA-256
  `c35ecefa9aa2f28268df0c697c79e31c4fe000a1fc56c6ab9aff004dd1a36ef7`.

Instruction data flow binds BP to the current recomputed successful-result
count and R13W to the parsed continuation offset. In both functions,
`cmpw %bp,%r13w; ja error` rejects exactly unsigned offset greater than count.
A separate CCB `+0xb6` compare rejects current expected-offset mismatch. Both
routes converge on code-5 error handling and have no edge to the subtraction or
later continuation handle indexing. Only dual-check fallthrough reaches those
operations.

Equality is not rejected by unsigned `ja`: the subtraction yields zero remaining
handles and the loop-entry comparison skips the indexed read. The named
CVE-2017-0785 continuation-offset unsigned-underflow / out-of-bounds handle-read
information-disclosure mechanism is therefore rejected for these two exact
functions.

This is direct fix-shaped behavior, not evidence of a direct public-commit
cherry-pick. It does not establish general SDP safety or runtime exposure.

## Delivery set

New files:

- `tools/uk_fw/bluetooth_sdp_continuation_model.py`
- `tests/test_bluetooth_sdp_continuation_model.py`
- `evidence/broadcom-bsa-sdp-continuation-cve-2017-0785.md`
- `evidence/artifacts/network-candidates/broadcom-bsa-sdp-continuation-exact-static.txt`
- `evidence/artifacts/network-candidates/226ea26684d4cd609a5b456d3d2cc762453c2d75.patch`
- `docs/agent-work/bluetooth-sdp-continuation/PLAN.md`
- `docs/agent-work/bluetooth-sdp-continuation/CHECKPOINT.md`

Minimally updated integrations:

- `evidence/broadcom-bsa-bluetooth-cves.md`
- `evidence/artifacts/network-candidates/README.md`
- `evidence/exploit-inventory.md`
- `HANDOVER.md`
- `Ioniq5-CHANGELOG.md`

`.gitattributes` already marks
`evidence/artifacts/network-candidates/*.patch -diff`; no change was needed.
The new changelog entry is `1.82.0`. It was added at the top without reordering
or rewriting the pre-existing non-monotonic concurrent entries.

## Model contract

The pure finite model has 24 cases:

- syntax/continuation path available: false or true;
- continuation offset relative to current result count: less than, equal, or
  greater than;
- expected-offset-only or fixed unsigned-bound-then-expected-offset semantics;
- current CCB expected offset mismatch or match.

It separately reports path state, operand roles/relation, unsigned-bound
presence and decision, expected-offset decision, subtraction reachability,
abstract difference, post-check indexing gate, and a tri-state named-mechanism
verdict. It requires exactly the documented mapping keys, rejects unknown or
missing keys, rejects invalid types and out-of-domain states, and uses an
all-or-none/non-abbreviated/non-duplicated CLI. It emits sorted JSON as explicit
UTF-8 bytes with one LF through `sys.stdout.buffer`, independent of
`PYTHONIOENCODING`. It emits no target or operational Bluetooth material.

## Validation

All required checks passed with
`python3`; no project-local `TMPDIR` was set.

- Focused test:
  `11 passed, 56 subtests passed`.
- `py_compile` for the model and test: passed.
- Exact-static/report script: `45` assertions passed, covering both ELF
  SHA-256 values, both Build IDs, both FDE bounds, both raw range hashes, all
  required operand/branch/error/subtraction/index instructions, patch byte
  identity/hash, and deterministic report hash.
- Required tests-scoped suite:
  `637 passed, 318312 subtests passed`.
- Public harness:
  `pass=3 info=4 pending=0 blocked=0 fail=0`.
- Independent narrow read-only package review: **ACCEPT**, no blocking findings.
- `git diff --check`: passed.
- Byte-identical retained patch SHA-256:
  `6f80d9cd3534d00e24c9c33717a282f1e6ae180f05f833e502c7a361e86b2721`.
- Deterministic default report SHA-256:
  `d7db08cc11dd1affbf5bfd086bdbac166c28854ff419b49cebe6717aefeb04ec`.

Final key file hashes:

| File | SHA-256 |
|---|---|
| model | `0e158d1d9eb75f4113113bd9fc8542e89cd5ca8b22d0d8c30c14bb404b13ab19` |
| tests | `7e479fefec209b213544b2cd379aaf3eefbc65fba4cd7051675639c44cafe88b` |
| assessment | `814811c34a6fe84b7b981f4a859dc50cd6f4a2f971aed89b02fd52c4a3e04704` |
| exact-static artifact | `a694c11543b8fdc8ad62c469133e2a9e670959a7dcbc5dc0f9def1bf084fefb4` |
| retained public patch | `6f80d9cd3534d00e24c9c33717a282f1e6ae180f05f833e502c7a361e86b2721` |

## Unresolved boundaries

Unknown and explicitly unclaimed:

- direct upstream cherry-pick provenance;
- general SDP, database, allocator, or other-handler safety;
- installed daemon identity and owner-device applicability;
- process startup, SDP registration, handler/channel reachability;
- adapter state, discoverability/connectability, pairing, authentication,
  authorization, and channel policy;
- malformed-input behavior outside the bounded instruction mechanism;
- actual out-of-bounds access, information disclosure, crash, code execution,
  unrestricted root, or persistence.

SDP code presence and configured `vbtd.service` do not establish any of those
runtime facts. Host-side tests used host Python subprocesses only. No recovered
target, target syscall, Bluetooth endpoint, radio, packet/PDU, malformed
fixture, payload, or exploit material was executed, used, or created.

## Resume action

No implementation action remains. If future owner-authorized work addresses
runtime exposure, begin with passive installed-identity and service/profile
configuration evidence; do not infer reachability from code presence. Do not
stage, commit, or push this package under the present instruction.
