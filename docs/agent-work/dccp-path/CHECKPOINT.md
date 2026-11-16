# Checkpoint — corrected CVE-2017-6074 DCCPv6 path applicability package

## Result

CVE-2017-6074 is rejected for the exact recovered EU `260128` stock package
only for the specific public request path requiring DCCP core (`input.o`) plus
DCCPv6/IPv6 (`ipv6.o`). Under applicable public Linux v4.1 Kconfig/Kbuild rules,
exact `IP_DCCP=n` excludes the whole named DCCP subtree. The canonical recovered
stock archive contains 163 regular `.ko` members and no canonical DCCP core or
DCCPv6 module.

The corrected model separates physical facts from the public CVE dependency.
DCCP-core physical state, DCCPv6 physical state, and complete named-path state
are classified even when the dependency is false. CVE rejection is exactly
`dependency && physical path absence`. Positive complete DCCPv6 functional
evidence overrides absence. Exact queried core/DCCPv6 symbol presence
establishes the corresponding translation unit. IPv4-only functional evidence
establishes core presence but not the CVE path.

`CONFIG_INET=y` and `CONFIG_IPV6=y`, so this is not general networking or IPv6
absence/safety. An `IPv6=n` input alone remains a bounded configuration fact and
does not establish general IPv6 absence. Disabled USER_NS is non-decisive. If
DCCP were built, ordinary DCCP socket creation would not be inherently
capability-gated; runtime policy remains separate and unobserved.

## Corrected model contract

Schema v2 has these 15 Boolean inputs:

1. `public_cve_requires_named_dccpv6_request_path`
2. `public_v4_1_build_rules_applicable`
3. `ip_dccp_config_enabled`
4. `inet_config_enabled`
5. `ipv6_config_enabled`
6. `user_ns_config_enabled`
7. `dccp_core_translation_units_built_in`
8. `dccpv6_translation_unit_built_in`
9. `recovered_module_inventory_complete`
10. `dccp_core_named_modules_shipped`
11. `dccpv6_named_module_shipped`
12. `queried_named_core_symbols_present`
13. `queried_named_dccpv6_symbols_present`
14. `functional_ipv4_only_dccp_path_present`
15. `functional_named_dccpv6_request_path_present`

Applicable public v4.1 rules plus `IP_DCCP=n` establish the exact-default
whole-subtree exclusion. A second formally complete component-specific absence
route combines a precise no-built-in fact with a complete module inventory
containing no corresponding named module. Positive built-in, named-module,
exact-symbol, or functional evidence takes precedence for its component and
records a conflict. Incomplete states remain unknown. One conclusively absent
required component establishes complete-path absence unless positive complete-
path evidence exists. Component presence alone does not prove complete
functional-path availability.

The CLI remains all-or-none and fail-closed. Output is deterministic explicit
UTF-8 with one final LF. Unnamed/vendor-equivalent routes, recovered-code fix
effects, installed identity, runtime reachability/behavior/policy, corruption,
privilege gain, root, and persistence remain `null`.

## Evidence hashes

### Exact recovered/public inputs

- recovered `vmlinux` SHA-256:
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`
- Build ID: `273378887b4cf563c10862fdf18b2292765df781`
- configuration SHA-256:
  `987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56`
- authoritative map SHA-256:
  `2cfba917c1c8e7444e393e8d94ebfe367e2ba348be4f35ce10fbb331822e3c1f`
- canonical decrypted stock archive SHA-256:
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`
- public v4.1 `net/dccp/Kconfig` SHA-256:
  `377e8d4e5dc101ea5a5d83b4c8c2ad64806c3c13f8947459b2e30755dd70949b`
- public v4.1 `net/Makefile` SHA-256:
  `83765cc8e3ee9ea64c98b3987d6eb9b3311639c6393ec559bb694830b21080af`
- public v4.1 `net/dccp/Makefile` SHA-256:
  `1eb466fb84ea75bcc7109ee8604166789a2e12a225f315f61eee4bdb5d05d042`
- retained official `ChangeLog-4.1.41` SHA-256:
  `4205336d83ed496dd809a692f5200a70c6e51007f5ca3ad60d9aed013ac471de`
- mainline fix commit: `5edabca9d4cff7f1f2b68f0bac55ef99d9798ba4`
- retained mainline patch SHA-256:
  `e5ac35f2d2b4129e3fca80a5b7d9200035bfd79f703b3045d7b28c9868179eb9`
- stable 4.1.y backport: `98442999b9671784e659b205be8b5b6be8e81629`
- retained stable patch SHA-256:
  `116e4a0d21907c0271cd76e45c2fda40c9c349ef8d0cb59184aba23bcc573c9c`

Both retained patches compare byte-for-byte with the pre-existing ignored
captures. The retained official `ChangeLog-4.1.41` identifies release commit
`4bd4cfc5210ef2f9002e54a16334a56acd295e4b`, dated 15 June 2017, and contains
the stable backport. The 15 June date is bound only to that retained official
ChangeLog release commit/date. The unretained archive-index claim was removed.

### Corrected package files

- retained exact static evidence SHA-256:
  `79b75516533d8a1a382f2c49cd8186d9c4329d19c5b58318711d38a420a9effc`
- assessment SHA-256:
  `4fcd7f0ac76e81195ddfd753bdc04030b23d4f1eb48959c8c3fd8e7b2d6c45b9`
- model source SHA-256:
  `075ea6178d6d0d9fa2b8e156cbbaa22c54fad5bd715b6ad9f3213bb55ceca10f`
- focused test source SHA-256:
  `aec5f54f439c6765c773813e44fe7d3dc3c11a370bc3f54326510a4aa0ad6fb0`
- deterministic default model-report SHA-256:
  `34874b60979ffda6a01ff527ddb36b26a7bdf2eb2f723217e0921ee84862df4e`
- plan SHA-256:
  `b7b99586051cf0b8d2c7255675fa45c9ceac5141083a5f8aec916bdcd42f5ab2`
- artifact README SHA-256:
  `b033625beaf3ef3ff6a3be956f7c88a1dd4e07bb241088873cbaaf929ac493ea`
- exploit inventory SHA-256:
  `d8494212b4673b8bc8b6afd4ed5e8607ae2dc1854b636918f80a380dfc393ece`
- handover SHA-256:
  `6241a228cfd3daff4ff0273eb22c26a84ad1c42e74c31e99d91b4ea255210f98`
- IONIQ changelog SHA-256:
  `a31e9a87060b2dd3802a09590c943385d9bb0e5e32ac7883f7358f96531d2c26`

## Validation

- Focused model validation with `python3`:
  **PASS**, 13 tests, zero failures/errors/skips.
- Exhaustive classification: **PASS**, every emitted classification field
  asserted over all `2^15 = 32,768` Boolean states.
- Directed cases: **PASS** for dependency false with physical absence retained;
  queried core-symbol presence; queried DCCPv6-symbol presence; core present but
  DCCPv6 absent; IPv4-only functionality; and positive complete DCCPv6
  functionality overriding absence.
- Bytecode compilation for model and focused test: **PASS**.
- Exact hashes: **PASS**, ten bound input/patch/ChangeLog files.
- Exact configuration: **PASS**, all five required lines.
- Public build/path contract: **PASS**, including core `input.o`, DCCPv6
  `ipv6.o`, and the two public functions.
- Complete split authoritative-map inventory: **PASS**, ten declared names and
  zero exact rows.
- Fresh read-only canonical archive inventory: **PASS**, 163 regular `.ko`
  members and zero DCCP-named members.
- Retained patch byte equality: **PASS**, both patches.
- Retained official ChangeLog release commit/date and stable-backport presence:
  **PASS**.
- Build ID and deterministic report/default classification: **PASS**.
- Deterministic UTF-8/LF and operational-material exclusion tests: **PASS**.
- `git diff --check`: **PASS**.
- Complete suite with the required Python: **PASS**, `617 tests, 318204
  subtests`, zero failures/errors/skips.
- Public harness: **PASS**, `pass=3 info=4 pending=0 blocked=0 fail=0`.
- Initial independent review: **REJECT**, for coupling physical path absence to
  the CVE dependency, under-specifying the DCCPv6 prerequisite, and incorrect
  orchestration provenance. All three were corrected. Corrected independent
  rereview: **ACCEPT**, no blocking findings.

## Orchestration provenance

Generic public research used Astra. The correction implementation ran in the
active pi session identified by `PI_PROVIDER=codex-router` and
`PI_MODEL=gpt-daybreak-blue-latest`; implementation provenance is therefore
`codex-router/gpt-daybreak-blue-latest`.

The installed `astra_terra_builder_deepseek_flash` binding was checked with the
orchestration doctor and is **static-ready** for
`deepseek/deepseek-v4.1-flash`. Its runtime routing remains unverified, no
inference request was made, and DeepSeek did not run. No substitute agent CLI or
paid probe was used. Corrected independent rereview returned **ACCEPT** with no
blocking findings.

## Changed paths

- `evidence/artifacts/kernel-candidates/cve-2017-6074-mainline-fix.patch`
- `evidence/artifacts/kernel-candidates/cve-2017-6074-stable-4.1-fix.patch`
- `evidence/artifacts/kernel-candidates/kernel-dccp-cve-2017-6074.txt`
- `evidence/vendor-kernel-dccp-cve-2017-6074.md`
- `tools/uk_fw/dccp_path_model.py`
- `tests/test_dccp_path_model.py`
- `docs/agent-work/dccp-path/PLAN.md`
- `docs/agent-work/dccp-path/CHECKPOINT.md`
- `evidence/artifacts/kernel-candidates/README.md`
- `evidence/exploit-inventory.md`
- `HANDOVER.md`

## Workspace and boundary

The package correction began at required HEAD `5ba7c1d`. Concurrent work later
advanced the integration base to `8df8d775f3ee3fbb3d2f8f4939465069d45babd0`
and incorporated the DCCP changelog block without changing a technical package
path. `Ioniq5-CHANGELOG.md` is therefore integration context, not a current
uncommitted delivery path. Pre-existing concurrent MICOM/IAS work remained
outside scope and was not read, modified, staged, or included. No reset, stash,
deletion, recovered-target execution, or target interaction was performed by
this task.

The supported conclusion is limited to the specific public DCCPv6 request path
under exact recovered stock-package evidence. General networking/IPv6 safety,
every inline/renamed/vendor-equivalent path, installed/running identity, runtime
reachability/behavior/policy, fix provenance/effects, corruption, privilege
gain, unrestricted root, and persistence are not established.
