# Checkpoint — exact CVE-2017-7184 XFRM-user path applicability audit

## Result

CVE-2017-7184 is rejected for the recovered EU `260128` package only for the
upstream/named `CONFIG_XFRM_USER` `XFRM_MSG_NEWAE -> xfrm_new_ae` update path.
The exact configuration disables `XFRM_USER`, so upstream v4.1 build rules do
not select `net/xfrm/xfrm_user.c`. A fresh read-only inventory directly against
the canonical decrypted stock archive establishes 163 regular `.ko` member
names and no `xfrm_user.ko`; the mutable extracted staging tree is not used to
prove stock identity.

The authoritative map has no exact-name row for any of the complete eight-name
query inventory. This bounded inventory does not globally exclude every inline,
renamed, or vendor-equivalent route. `CONFIG_XFRM=y`; complete
`xfrm_init_replay [0xffffffff8151979d,0xffffffff815197f6)`, state/policy/replay
symbols, and three IPv6 XFRM mode modules remain. This is not a whole-XFRM
absence or safety verdict. Separately disabled `CONFIG_NET_KEY` is not treated
as the named implementation.

## Evidence hashes

- recovered `vmlinux` SHA-256:
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`
- Build ID: `273378887b4cf563c10862fdf18b2292765df781`
- configuration SHA-256:
  `987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56`
- authoritative map SHA-256:
  `2cfba917c1c8e7444e393e8d94ebfe367e2ba348be4f35ce10fbb331822e3c1f`
- canonical decrypted stock archive SHA-256:
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`
- introducing commit (context):
  `d8647b79c3b7e223ac051439d165bc8e7bbb832f`
- historical incomplete verifier commit (context):
  `e2b19125e94124daaeda1ddcf9b85b04575ad86f`
- initial fix commit: `677e806da4d916052585301785d847c3b3e6186a`
- retained initial patch SHA-256:
  `5d419e4862b608a9372f4c93bf27c9a3014fe6598d38f148fa8eeea71fab905e`
- required follow-up commit: `f843ee6dd019bcece3e74e76ad9df0155655d0df`
- retained follow-up patch SHA-256:
  `3e0699ff6c4811470a4007bdb7bff86a72b12ddad739d01a3cc135e3b17ccd75`
- official stable 4.1.y backports (context):
  `438db92d7f2792e3bad17be70e6edf0f44a081f0`,
  `171a957989c4f398adb41078dbfff73b0821e383`; both first in Linux
  4.1.49 (22 January 2018)
- retained introducing patch SHA-256:
  `64bccd3fe44942e8b100dd66b9e43c73aed1ebb6b809db868a5e41c046a73581`
- retained historical-verifier patch SHA-256:
  `88a0a46c099de374e5ca19f5a44ca8d1aaa4e1c08538d71471bdaf2375f56d6a`
- retained stable initial-backport patch SHA-256:
  `a764b411fcbaa2db8d8ea7420a38d88749dac82f7a17b2b24d997e65485f9232`
- retained stable follow-up-backport patch SHA-256:
  `de91f9ab7bc874defccec57c723740eadfc7f55923dc279a26c0ef0118da92e1`
- retained Linux 4.1.49 release patch SHA-256:
  `344a344b15c2a05330399ce4694a82876765db1031eb1f7a7d700cd9de366963`
- retained reviewed official changelog excerpt SHA-256:
  `f3623a119582dfe97f9132560f640763abd0c8324545762a74ef0449a421fdcb`
  (public maintainer email addresses redacted; complete downloaded changelog
  SHA-256
  `c0b794ff48313e9c1a2e74de71efdf6eade44c229b00839d077392e821026323`)
- ignored regenerated disassembly SHA-256:
  `1633989b84ff0156505385f136fd609dcc70f9148dd4c634b1430021203f3bd5`
- retained exact artifact SHA-256:
  `9ea9205be67b246aff6d88be2d5b00f3d022cec60a686dcf6a010974136fd34e`
- assessment SHA-256:
  `b378bc71cddddab8ce19f8f387a20f06e0cf8671e3b1a74d52576b020a71ab8b`
- model source SHA-256:
  `d74f5b722a2ad62a263474525e3a13af329d005a6aae453ad55fee800b081abc`
- focused test source SHA-256:
  `d7804ea8c67d1406841babd4a8f7315acf74f1dce0561ea46c4fc207d64d8ba1`
- deterministic default model-report SHA-256:
  `0a62022f8e95045fed37132684c5979e2845c1bbea997a9f8d9cbad5b2da9645`
- plan SHA-256:
  `d8fcb65da9b07286c6597f704445c0b938a09e8a759915bf88cbd8ff00221b74`

Both retained patches compare byte-for-byte equal to their pre-existing ignored
public captures. The regenerated complete `xfrm_init_replay` disassembly also
matches the ignored exact disassembly after normalizing only boundary newlines.
Version history is contextual only; exact absent-path evidence controls. The
historical verifier alone is not remediation. Both mainline fix effects, or exact
equivalents, would be required if the named path existed.

## Model contract

Schema v2; ten Boolean inputs; deterministic explicit UTF-8/LF; all-or-none
fail-closed CLI; tri-state unknown for incomplete absence facts; explicit
contrary functional named-path and XFRM-core-present facts; separate NET_KEY
scope; null vendor-equivalent, fix-effect, installed-runtime, dynamic-policy,
and impact outcomes; exhaustive assertions for every emitted classification
field. Evidence metadata binds the canonical stock archive SHA without adding a
non-Boolean classification input. The report contains classification metadata
only and no operational or target material prohibited by the task contract.

## Validation

- Focused model validation with `python3`:
  **PASS**, `8 tests, 1056 subtests`, zero failures/errors/skips.
- Bytecode compilation for the model and focused test with the required Python:
  **PASS**.
- Exact `vmlinux`, configuration, and authoritative-map hash checks;
  configuration facts; and all eight zero-row named-symbol queries: **PASS**.
- Exact patch comparison: **PASS** for both retained patches.
- Exact normalized disassembly comparison: **PASS**.
- Fresh read-only canonical stock archive inventory: **PASS**, archive SHA-256
  matched; 163 regular `.ko` member names; zero `xfrm_user.ko`; zero
  `af_key.ko`; exactly three XFRM-named members.
- `git diff --check`: **PASS**.
- Complete suite with the required Python: **PASS**, `594 tests, 154302
  subtests`, zero failures/errors/skips.
- The pre-commit public harness originally passed while the changelog excerpt
  was outside Git's tracked-index privacy scope. A post-commit rerun correctly
  reported the excerpt's public maintainer email addresses as blocking. The
  retained excerpt now redacts those addresses while preserving its complete
  source hash, source ranges, and all non-email content. The privacy-only rerun
  passed with three informational public/no-reply identifiers and zero blocking
  findings. The final complete harness passed with
  `pass=3 info=4 pending=0 blocked=0 fail=0`.
- Initial independent read-only review: **REJECT**, limited to stale validation
  wording, a concurrently moving integration base, and missing retained local
  public-history captures. The technical path-only verdict, hashes, archive
  inventory, exact disassembly, model logic, exhaustive field assertions, and
  fail-closed CLI passed review. Those three package defects were corrected on
  frozen base `7074707`; corrected independent review returned **ACCEPT** with
  no blocking or nonblocking findings.

The installed `astra_terra_builder_deepseek_flash` binding was statically ready
for `deepseek/deepseek-v4.1-flash`, but this pi session exposed no native
subagent/delegation tool. No substitute route or paid probe was used, so worker
inference routing remains unverified.

## Changed paths

- `evidence/artifacts/kernel-candidates/cve-2017-7184-introducing.patch`
- `evidence/artifacts/kernel-candidates/cve-2017-7184-historical-verifier.patch`
- `evidence/artifacts/kernel-candidates/cve-2017-7184-initial-fix.patch`
- `evidence/artifacts/kernel-candidates/cve-2017-7184-followup-fix.patch`
- `evidence/artifacts/kernel-candidates/cve-2017-7184-stable-initial.patch`
- `evidence/artifacts/kernel-candidates/cve-2017-7184-stable-followup.patch`
- `evidence/artifacts/kernel-candidates/cve-2017-7184-linux-4.1.49.patch`
- `evidence/artifacts/kernel-candidates/cve-2017-7184-linux-4.1.49-changelog.txt`
- `evidence/artifacts/kernel-candidates/kernel-xfrm-user-cve-2017-7184.asm`
- `evidence/vendor-kernel-xfrm-cve-2017-7184.md`
- `tools/uk_fw/xfrm_user_path_model.py`
- `tests/test_xfrm_user_path_model.py`
- `docs/agent-work/xfrm-user-path/PLAN.md`
- `docs/agent-work/xfrm-user-path/CHECKPOINT.md`
- `evidence/artifacts/kernel-candidates/README.md`
- `evidence/exploit-inventory.md`
- `HANDOVER.md`
- `Ioniq5-CHANGELOG.md`

## Workspace and concurrency

The task began on clean tracked `main` at
`699570e6cb1d95652c3004faaaf5db7ed844ba14`, synchronized with `ioniq/main`.
Concurrent work first advanced the base to `d2c4596` and then to frozen base
`7074707` (`The launcher starts: MICOM adaptor satisfies its asks end to end`).
The latter concurrent commit incorporated the pre-review XFRM changelog block;
the current package modifies only that block's validation statement relative to
`7074707`. Unrelated concurrent modification of
`tools/uk_fw/ias_backend_soft/micom_service.c` and the untracked
`tools/uk_fw/ias_backend_soft/micom-service` remain outside this package. No
reset, checkout, stash, or deletion was performed, and no MICOM path is included
in the package's staging scope.

## Boundary and remaining uncertainty

Installed/running kernel identity, every inline/renamed/vendor-equivalent route,
live interface behavior, runtime capability policy, replay-verifier/fix effects,
corruption, privilege gain, unrestricted root, and persistence remain unknown or
unobserved. The canonical stock archive member inventory is recovered-package
evidence, not installed runtime state or sole decisive evidence. No recovered
target was run, and no socket, netlink/XFRM operation, message, attribute,
packet, module action,
namespace, capability request, trigger, race, payload, or firmware material was
created or exercised.
