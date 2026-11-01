# AppFUMO wildcard D-Bus recovery-signal boundary checkpoint

Date: 2026-11-01
Status: implemented; independent exact-package review **ACCEPT**; committed as `98778f0` and published to both maintained repositories

## Delivered

- `tools/uk_fw/appfumo_dbus_recovery_signal_boundary.py`
  - exact ELF/Build-ID/kernel/rootfs/LLVM and complete instruction/FDE binding;
  - SysV subscription-argument, generated-dispatch, consumer-guard, and separate
    asynchronous-request-tail validation;
  - strict complete rootfs stream and D-Bus policy XML audit;
  - launcher, configured identity, executable-label, kernel MAC, and canonical
    bus-daemon named-string boundaries;
  - fixed UTF-8/LF normalized output with callable coordinates and values
    redacted.
- `tests/test_appfumo_dbus_recovery_signal_boundary.py`
  - exact generation/privacy tests; wildcard, conjunction, ordered override,
    scope-precedence, and undefined cross-file-order semantics; focused malformed
    XML/DOCTYPE, scope/ownership, manifest, kernel config, unit, archive-link,
    and system-local failures.
- retained artifacts under `evidence/artifacts/update-candidates/`
  - byte-free selected exact-static evidence;
  - strict manifest;
  - deterministic normalized report.
- `evidence/appfumo-dbus-recovery-signal-boundary.md`.
- plan/checkpoint and narrow README, public-ledger, and update-candidate index
  links.

## Findings

- The exact Qt 5 system-bus subscription has empty service/path filters and
  fixed hash-bound interface/member filters with a bound receiver/slot.
- Matching signals can reach the guarded local consumer; eligible local state
  may tail into a separate asynchronous recovery request.
- The canonical main policy allows all users to connect, permits signal send and
  receive, and denies method-call send by default.
- Main `system.conf` has 14 policy rules (10 allow, four deny); its default
  block has 13 rules (nine allow, four deny), including one connect allow, one
  method-call-send deny, and separate signal-send/signal-receive allows.
- Separately, all 18 canonical `system.d` policy members and 221 rules (208
  allow, 13 deny) were parsed. No directory member has an explicit
  normalized-filter or unconstrained general-signal rule.
- Named receive-sender signal rules split into 15 allows and one deny. One
  hash-bound sender is denied in default scope and allowed for root in one
  member. The default deny overrides the main receive allow for non-root; the
  root rule overrides that result for root. Installed consumer uid is unknown.
- All 137 `send_destination` values are named/non-wildcard, so none matches the
  normalized destination-less broadcast. Rule attributes are conjunctive,
  defined rule order uses last match, and material same-scope conflict across
  undefined-order included files resolves to unknown. Cross-file order is not
  material for the exact normalized signal inventory.
- The selected MICOM policy grants root ownership/named-destination sending but
  does not authenticate broadcast signal origins.
- The canonical archive has no system-local member; runtime replacement and
  dynamic include effects remain unknown.
- The launcher unit has no explicit user/group, so its configured systemd
  default is root. Canonical launcher/updater process-construction and label
  assignments are bound, while runtime pathname, uid, and labels remain
  conditional.
- The exact kernel enables SMACK and disables SELinux/AppArmor. The canonical
  bus daemon has SELinux-named strings and no Smack-named string; only named
  integration is rejected. Kernel socket mediation and arbitrary-label
  same-bus admission remain unknown.

## Preserved boundary

No signal was generated, no bus was contacted, and no request or external
recovery action was observed. The result does not establish message forgery,
cross-label reachability, code execution, root, unrestricted privilege, or
persistence. It is classified as a conditional wildcard-signal trust boundary,
not assigned a new vulnerability number.

## Validation

All Python tests and harnesses were run with `<platformio-env>/bin/python3`.

- corrected focused tests: **15 passed, 19 subtests passed**;
- full bounded repository `tests/` pytest suite: **797 passed, 351,505
  subtests passed**;
- integrated public harness: **PASS** (`pass=3`, `info=4`, no pending, blocked,
  or failed checks);
- tracked public privacy check: no blocking finding; a separate scan of all 11
  package/index files, including every untracked file and each added tracked
  line, found **0 blocking findings** and no published callable coordinate;
- two generations under distinct `PYTHONIOENCODING` values were byte-identical
  and matched the retained report;
- Python compilation, UTF-8/LF checks, and `git diff --check`: passed.

## Artifact identities

- byte-free selected evidence SHA-256:
  `4b0c525ee7ec862dfc65df2e4e0a991d5bb934708dfb8ba1f102110759a95ab7`;
- strict manifest SHA-256:
  `ff934574db6c0204c05f1e2a3766b83b5ea60394b366d2c9ec8c902db7b6e82c`;
- normalized report SHA-256:
  `826ed7c3fcfcd7077840fbad792a88737a2555ba9e2a528f1baf9179bd07a936`.

## Review and publication

Independent exact-package review first identified D-Bus policy-ordering,
wildcard/conjunction, and fail-closed XML-scope gaps. After correction and
regeneration, the reviewer returned **ACCEPT** for the hash-bound tool, tests,
evidence, manifest, and report listed above. The accepted package was committed
as `98778f0674cd0dc8a91d508100b3f955cbb04ba4` and fast-forward published to
both maintained `main` branches. Post-push checks matched local `HEAD`, both
tracking refs, and both remote branch heads.

The correction pass resumed from baseline
`8bfe50efa8a5e32493be4de3e4d2c4326f707e07`; concurrent unrelated history then
advanced through `2eec121` before this package commit. No reset, revert, or
history rewrite occurred. No recovered target code was executed. No bus,
signal, method, request, payload, packet, flash/update action, or persistence
was created. The `tools/uk_fw/ias_backend_soft/` subtree was not edited.
