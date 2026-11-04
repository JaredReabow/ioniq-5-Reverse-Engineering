# Checkpoint — exact-static CVE-2015-1805 pipe iterator applicability

## Result

CVE-2015-1805 is rejected for the exact recovered EU `260128` kernel because
complete machine code uses iterator architecture at all three pipe copy sites
and both complete CVE-relevant iovec helper paths preserve bounded progress.
The conclusion does not rely on the `4.1.27-abl` banner.

Exact `pipe_write [0xffffffff81117bf4,0xffffffff81117f83)` calls
`copy_page_from_iter` at `0xffffffff81117ce3` for merge and
`0xffffffff81117dce` for a new buffer. Exact
`pipe_read [0xffffffff81117f83,0xffffffff811181ac)` calls
`copy_page_to_iter` at `0xffffffff8111803d`. Complete helper bounds are
`copy_page_from_iter [0xffffffff8120d9d9,0xffffffff8120dc1a)` and
`copy_page_to_iter [0xffffffff8120e40e,0xffffffff8120e67e)`.

Both complete iovec paths clamp against iterator count at `+0x10`, read base and
length from fixed 16-byte descriptors, account actual progress as requested
minus copy residual, carry advanced page/user positions and remaining budget
into fallback, and finally commit iterator offset/count/descriptor/remaining-
segments state at `+0x8`, `+0x10`, `+0x18`, and `+0x20`. Neither complete
range stores into descriptor `iov_base` or `iov_len`.

No exact authoritative-map row is named `pipe_iov_copy_to_user` or
`pipe_iov_copy_from_user`. This is bounded corroboration only. Ordinary local
pipe functionality remains compiled and statically callable in the abstract.
Public source-level impact for affected code was unprivileged local memory
corruption/privilege escalation; installed identity, runtime policy, successful
triggering, corruption, root, and persistence remain unobserved.

## Public contract and context

- legacy mutable-iovec atomic-copy introduction:
  `f6762b7ad8edd6abc802542ce845d3bc8adcb92f`
- read-side iterator conversion:
  `637b58c2887e5e57850865839cc75f59184b23d1`
- write-side iterator conversion:
  `f0d1bec9d58d4c038d0ac958c9af82be6eb18045`
- exact public v4.1 `fs/pipe.c` SHA-256:
  `caee56c1f24f0d08e0a52a3257781423ced61db51acf60651426d562fa130723`
- exact public v4.1 `lib/iov_iter.c` SHA-256:
  `ea04df8ba5083d9ecb53a965a98ef424ecb08686bb9d1df2cec2ca5797b3b2ae`

The exact public v4.1 sources contain two `copy_page_from_iter` pipe call sites,
one `copy_page_to_iter` pipe call site, and neither legacy pipe-local helper.
The first fully iterator-based upstream line is 3.16; ordinary upstream 4.1
inherited both conversions and needs no 4.1.y CVE-2015-1805 backport. Legacy
stable adaptations and CVE-2016-0774 are contextual alternatives, not required
4.1 fixes. Version history remains context rather than a vendor verdict.

## Exact input and retained evidence hashes

- recovered `vmlinux` SHA-256:
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`
- Build ID: `273378887b4cf563c10862fdf18b2292765df781`
- configuration SHA-256:
  `987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56`
- authoritative map SHA-256:
  `2cfba917c1c8e7444e393e8d94ebfe367e2ba348be4f35ce10fbb331822e3c1f`
- retained introducing patch SHA-256:
  `ad43bba30d7d3be2e15c17b605f6d17d92f17fa3ebb239bd2bdc457b10746aec`
- retained read-conversion patch SHA-256:
  `d44d40a61f9746ec3a8fd2ab6c88f74f0ce09617786ac27f59174effbabaeb5c`
- retained write-conversion patch SHA-256:
  `c5966a0a700deb343e5599a716fb116988a85238134099925ced6fda3524340a`
- regenerated/ignored complete `pipe_write` listing SHA-256:
  `978454d7f6b59b6c04f3ce0791d885a1b639e182fd3fb3699c4afc7aaa813a76`
- regenerated/ignored complete `pipe_read` listing SHA-256:
  `9185b4e7d30d1675f381fa12a12f3fef87883708bd9f9955a69a4839945f1391`
- regenerated/ignored complete `copy_page_from_iter` listing SHA-256:
  `89757162a5a28ef8618e4aa964b51f8bd1c30bac70f804bf70dbc41c7ad21df2`
- regenerated/ignored complete `copy_page_to_iter` listing SHA-256:
  `3a150c737e8fb2fe78a691d69eaf344e6e46099f67627f604d5cc51ef0261fca`
- retained combined static artifact SHA-256:
  `e79391d6592ce772f18cf02d97cdbba00e58b68ec8340e67409840470bfff552`
- assessment SHA-256:
  `fb25171a5a07daf0cb85fa77d8399fdd21921a735fa9418ce3531d47adb3d6c8`
- model source SHA-256:
  `aea929dee71d2d6b196024cc8d238dbb67872e2a75b2dd2be9545747be0e5f3c`
- focused test source SHA-256:
  `ec0128e2364300534383a770c0cbe7c5dc4decf64eacabf7d13c69c7e76023ce`
- deterministic default model-report SHA-256:
  `3f5dd658e3bdb5dab12e91537c9d26455d11b43826e7dce22932ab0ebc8649b0`
- plan SHA-256:
  `d2cd0099526b08de4c7147725651e3edeaa9e74510110f1ef267a0adb0945b40`
- artifact index SHA-256:
  `f8748c3322aed9473ca2eb80ce58f6a93efa9332c7f5d6813e33f4120ef49952`
- exploit inventory SHA-256:
  `f837f3e2340c4f026fc9c195f28c09d4544d7f668c673d5029b5b33d064ae0e4`
- handover SHA-256:
  `3fafc0a45357afe253e237a3bdc3629d5affe304ac4754e7949283d585eed2b3`
- IONIQ changelog SHA-256:
  `be45ac2d71aac83d0cbcc207d321c888a4c26225c5ade32f66dd4b93d23e9420`

All three retained patches compare byte-for-byte equal to the ignored public
captures. All four regenerated disassemblies compare byte-for-byte equal to the
ignored exact captures. After omitting only each standalone `llvm-objdump`
file's leading separator newline, all four complete listings in the retained
combined artifact compare byte-for-byte with the regeneration.

## Model contract

Schema v2; 17 Boolean inputs; deterministic explicit UTF-8/LF; all-or-none
fail-closed CLI; tri-state unknown for incomplete fixed-effect facts; explicit
broken-legacy-path precedence; optional progress-preserving legacy alternative;
explicit ordinary-local-pipe-presence scope; null installed/runtime/corruption/
privilege/root/persistence outcomes; and exhaustive assertions for every emitted
classification field. The report emits only non-operational classification
metadata and no recovered-code material.

## Validation

Required interpreter: `python3`.

- Focused unit validation: **PASS**, `10 tests, 131109 subtests`, zero
  failures/errors/skips. Subtests comprise 131072 exhaustive Boolean states, 14
  individually removed required fixed facts, 2 legacy-alternative states, 2
  ordinary-functionality states, 4 CLI rejection cases, 3 output-encoding
  cases, and 12 report-content exclusions.
- Bytecode compilation of model and focused test: **PASS**.
- Exact input hashes and Build ID: **PASS**.
- Exact patch hashes, commit headers, and byte-for-byte comparisons: **PASS**.
- Four exact successor bounds and two zero-row legacy exact-name queries:
  **PASS**.
- Fresh LLVM 23.1.3 regeneration of four complete ranges and byte-for-byte
  comparison with ignored captures and retained listing bodies (excluding only
  the standalone files' leading separator newline): **PASS**.
- Public v4.1 source call/helper counts and helper-effect patterns: **PASS**.
- Scoped `git diff --check` over every authorized package path: **PASS**.
- Complete suite with the required Python: **PASS**, `604 tests, 285411
  subtests`, zero failures/errors/skips.
- The initial complete public-harness run: **FAIL**, because a previously
  committed XFRM official-changelog excerpt contained public maintainer email
  addresses that were outside the tracked-index privacy scope during its
  pre-commit validation. The excerpt now redacts those addresses while
  preserving the complete source hash, source ranges, and all non-email
  content. Privacy-only rerun: **PASS**, three informational public/no-reply
  identifiers and zero blocking findings. Final complete harness: **PASS**,
  `pass=3 info=4 pending=0 blocked=0 fail=0`.
- Independent read-only review on frozen base `844657d`: **ACCEPT**, no blocking
  findings. The technical verdict was supportable. Its nonblocking moving-base
  bookkeeping correction is integrated; optional retention of a raw map-query
  transcript was not required because the positive complete function/call-site
  evidence controls the verdict. Final delivery review on `844657d` also
  returned **ACCEPT** with no blocking findings; its terminal-blank-line
  precision and handover-date notes were corrected. The later concurrent base
  advance to `0bf70da` changed only `Ioniq5-CHANGELOG.md` and
  `Ioniq5-HISTORY.md`, absorbing the final pipe changelog update; no technical
  package path changed.

The installed `astra_terra_builder_deepseek_flash` binding is static-ready for
`deepseek/deepseek-v4.1-flash`, but runtime routing remains unverified and no
DeepSeek inference ran. This root exposes native delegation: the exact package
was implemented by a `codex-router/gpt-daybreak-blue-latest` worker. Generic
public research was delegated separately to Astra without private target
details. The root session coordinated, integrated, and reviewed the package.

## Current delivery paths

- `evidence/artifacts/kernel-candidates/cve-2015-1805-introducing.patch`
- `evidence/artifacts/kernel-candidates/cve-2015-1805-read-iterator-fix.patch`
- `evidence/artifacts/kernel-candidates/cve-2015-1805-write-iterator-fix.patch`
- `evidence/artifacts/kernel-candidates/kernel-pipe-cve-2015-1805.asm`
- `evidence/vendor-kernel-pipe-cve-2015-1805.md`
- `tools/uk_fw/pipe_iov_iterator_model.py`
- `tests/test_pipe_iov_iterator_model.py`
- `docs/agent-work/pipe-iov-iterator/PLAN.md`
- `docs/agent-work/pipe-iov-iterator/CHECKPOINT.md`
- `evidence/artifacts/kernel-candidates/README.md`
- `evidence/exploit-inventory.md`
- `HANDOVER.md`
- `evidence/artifacts/kernel-candidates/cve-2017-7184-linux-4.1.49-changelog.txt`
- `evidence/vendor-kernel-xfrm-cve-2017-7184.md`
- `docs/agent-work/xfrm-user-path/CHECKPOINT.md`

## Workspace and safety boundary

The task began at baseline `bbd3ae93d93a120e720e46b7c747f21ced233ef4`
on `main`. Concurrent work advanced the base first to
`844657d1c80fafac2be581af7af834708dd922f7` and then to
`0bf70dad0ae7bcd8189dc0cc0640343c970b85e5`, incorporating both the pre-review
and final-validation CVE-2015-1805 changelog updates. `Ioniq5-CHANGELOG.md` is
therefore integration context, not a current uncommitted delivery path. No
reset, checkout, stash, or deletion was performed by this task. The two user-designated MICOM paths remained outside
every discovery, read, execution, edit, validation, staging, and attribution
path set.

No recovered target was executed. No target pipe or target iovec was created;
no target pipe operation, induced copy fault, trigger, race, grooming,
memory-pressure action, payload, or exploit code was created or exercised.

## Remaining uncertainty

Direct source-commit provenance cannot be inferred from stripped machine code.
Installed/running kernel identity, runtime local access policy, every renamed,
inlined, or vendor-equivalent defect, and general pipe/iterator correctness
remain unknown. Successful triggering, a copy fault, memory corruption,
privilege escalation, unrestricted root, and persistence remain unobserved. The
exact-name symbol query is bounded corroboration rather than universal absence,
and ordinary compiled pipe functionality is not evidence of installed runtime
reachability.
