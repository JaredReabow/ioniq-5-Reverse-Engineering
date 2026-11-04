# Plan — exact Broadcom BSA SDP small-maximum CVE-2017-13255/13256 review

## Objective

Determine whether the public `max_list_len < 4` out-of-bounds-write mechanisms
for CVE-2017-13255 (`process_service_attr_req`) and CVE-2017-13256
(`process_service_search_attr_req`) exist in either PCB-selectable recovered
Broadcom BSA daemon (`vbtd-51` and `vbtd-63`). Base the verdict on complete exact
machine-code effects, including the vendor GKI allocation contract, rather than
on BSA/AOSP genealogy, version strings, or the source-like guard alone.

## Baseline and preservation

- Analysis starting baseline: `0a9a7f2fd1cb3b25d928fe9f32fe65cac055d121`.
- Pre-delivery integration HEAD at root review:
  `30f6cace8d2c776b2501c88791b7e54dd4da9055`. The recovered binaries and
  ignored static inputs were unchanged across this interval. Concurrent commit
  `30f6cac` accidentally absorbed a preliminary SDP changelog entry; the final
  delivery must correct it and record that integration event without rewriting
  shared history.
- Preserve unrelated concurrent changes in
  `tools/uk_fw/ias_backend_soft/micom_service.c` and the untracked
  `tools/uk_fw/ias_backend_soft/micom-service`; do not read, modify, stage, or
  include either path.
- Do not execute either recovered daemon, open a Bluetooth endpoint, use a radio,
  construct a packet/PDU, pair/connect, create malformed input, or claim dynamic
  reachability.
- Keep complete disassemblies, downloaded public records, and intermediate
  source under ignored `work/`; retain only reviewed excerpts, authoritative
  public patch evidence, documentation, deterministic tools, and tests.
- Do not commit, push, stage, reset, stash, or delete during implementation.

## Exact evidence contract

1. Bind both exact ELFs by path, SHA-256, Build ID, BSA version, PIE image-base
   convention, and relevant half-open FDE/function ranges.
2. Retain the authoritative Android March 2018 bulletin classification and the
   exact shared fix commit `f0edf6571d2d58e66ee0b100ebe49c585d31489f`.
   Preserve the patch byte-for-byte and record its SHA-256. The public fix adds
   `max_list_len < 4` rejection to both named functions.
3. Confirm in both ELFs that the source-like `< 4` rejection is absent, but do
   not stop there. Trace the exact request-derived maximum, new-request and
   continuation branches, scratch-buffer allocation operand, first body-space
   tests, fixed three-byte sequence-header writes, response copy length, and
   successor routing.
4. Establish exact vendor allocator effects:
   - each SDP scratch allocation requests the connection's remote-MTU-sized
     value, not the peer's small `max_list_len`;
   - `GKI_getbuf[_r]` chooses the first public pool whose configured capacity is
     at least the requested size;
   - pool 0 has exact user capacity `0x40` bytes in both variants;
   - the returned pointer is the pool's user-data pointer, after its allocator
     metadata.
5. For each named handler and both initial/continuation states, prove or reject
   the public small-maximum overwrite using exact feasible writes for
   `max_list_len` values `0..3`. Distinguish a protocol/list-length contract
   violation from a write outside the physical GKI user buffer.
6. Do not generalize the result to arbitrary SDP safety, negotiated-MTU defects,
   allocator corruption, other malformed values, other Bluetooth CVEs, runtime
   profile exposure, installed identity, or vendor-equivalent unnamed paths.

## Deterministic model contract

Add a packet-free pure arithmetic/control model for only the four small maximum
values. It must:

- accept a handler (`service-attr` or `service-search-attr`),
  `max_list_len` in `0..3`, and initial-versus-continuation state;
- encode only proven exact upper bounds: initial replies reserve/write at most
  the fixed three-byte sequence header before copying; continuation body writes
  are bounded by the supplied small maximum and do not rewrite the initial
  sequence header;
- bind both binary hashes, exact relevant ranges/addresses, public fix commit,
  and the exact 64-byte minimum GKI user capacity;
- report logical requested-limit exceedance separately from physical GKI-buffer
  overflow;
- reject Booleans-as-integers and all values outside the bounded domain;
- emit deterministic explicit UTF-8 bytes with fixed LF using
  `sys.stdout.buffer`, independent of `PYTHONIOENCODING`;
- emit no packet, PDU, radio, socket, malformed fixture, executable, or target
  operational material.

Tests must exhaust both handlers, both request states, and all four maximum
values; independently assert every classification field, deterministic output,
encoding independence, all-or-none CLI behavior, fail-closed input validation,
evidence bindings, and absence of operational material.

## Documentation and integration

- Add a focused assessment and a retained exact-static artifact under the
  Bluetooth/network candidate evidence paths.
- Update `evidence/broadcom-bsa-bluetooth-cves.md`, the network-candidate artifact
  index, `evidence/exploit-inventory.md`, `Ioniq5-CHANGELOG.md`, and `HANDOVER.md`
  with the bounded verdict.
- If exact tracing supports it, classify both public small-maximum OOB-write
  mechanisms as rejected by allocator/caller effects despite the missing
  source-like guard. Explicitly preserve V-019's separate dormant BNEP defect.
- Record that SDP code presence, intended uid 0 service configuration, and the
  generic Android RCE classification do not establish owner-device radio
  delivery, process corruption, code execution, unrestricted root, or
  persistence.

## Validation and acceptance

Run, in order:

1. focused tests for the new model;
2. `py_compile` for the model and test;
3. exact static regeneration/hash/address checks against both ignored ELFs;
4. `git diff --check`;
5. `python3 -m pytest -q tests`;
6. the repository public harness if applicable.

Review must inspect the actual diff and independently verify that every
small-maximum path stays within the proven physical GKI capacity, that no
negative conclusion relies only on missing source-like opcodes, and that the
working tree still contains only the preserved unrelated MICOM residue plus the
reviewed delivery set.

## Subagent status

Generic public candidate ranking came from Astra child
`e0ed907e-7e23-42f2-a8cd-fe46ef6b975c`. Exact implementation is assigned only
to `codex-router/gpt-daybreak-blue-latest`; no DeepSeek runtime inference is
claimed. The root retains final acceptance, Git staging, commit, and push.
