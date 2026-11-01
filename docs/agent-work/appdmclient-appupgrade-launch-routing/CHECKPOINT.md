# AppDMClient AppUpgrade launch-routing checkpoint

## Status

Implementation, deterministic exact-static evidence, focused tests, full
tests-scoped integration validation, remediation, and fresh independent
read-only review are complete. Reviewer thread
`6dfde6fb-3433-43ff-8be7-8bb5b3d9493e` returned **ACCEPT** with no blocking
findings against the exact remediated path/hash set below.

The first review returned `CHANGES_REQUIRED` because archive hashing and member
extraction used separate pathname opens. Tool version `1.0.1` remediates that
finding by using one stable no-follow descriptor for both operations and by
revalidating descriptor and pathname identity afterward. The fresh review
explicitly accepted that remediation and its deterministic replacement
regression.

Nothing was staged, committed, or pushed for this package at acceptance and
checkpoint creation. `HEAD`, `main`, and `ioniq/main` were
`a42a512aff4dd408500c619fdbb1d1c61dc21df2`. Concurrent history and unrelated
worktree paths were preserved.

## Accepted static result

The exact canonical AppDMClient establishes a launch proxy with a hidden
`QDBusPendingReply<>` return object and logical arguments:

```text
(int appId, QString appName, QString appLocation)
```

The complete direct-transfer inventory to helper `[0x8c0c0,0x8c2ab)` contains
four calls and no direct jumps. All four calls use app ID `300` and fixed first
QString role `AppUpgrade`. Three use the fixed staged AppUpgrade path; the
terminal marker-present staging call uses the source-root-derived AppUpgrade
path.

Within staging `[0x7ff60,0x830e4)`, the logical source-root argument is retained
in `%r13`; stack slot `0x0` holds the source-derived executable and stack slot
`0x8` holds the staged executable. The terminal routing is:

```text
source-derived executable exists
  → marker present: request source-derived path
  → marker absent: validate staged path
      → validator true: request staged path
      → validator false: no request
```

The local validator establishes path existence, successful read-open, four-byte
ELF magic, and executable permission. It is not authentication or signature
verification. Staged-path existence is checked earlier but is not a common
terminal gate; its true branch adds permission handling before control rejoins
the marker split.

## Canonical and exact-static binding

The analyzer binds directly to the canonical EU `260128` rootfs archive. It
opens that archive once using `O_RDONLY`, `O_CLOEXEC` where available, and
`O_NOFOLLOW` where available; validates the pre-open pathname against the open
descriptor; hashes the complete archive through that descriptor; rewinds the
same file description; streams the selected regular AppDMClient member through
that same handle; and revalidates descriptor and pathname identity, regular-file
type, link count, size, and nanosecond modification time after parsing.

The supplied AppDMClient must be byte-identical to canonical member
`./app/bin/AppDMClient`. The package also binds exact ELF size, SHA-256, Build
ID, LLVM identities, complete instruction and FDE inventories, selected FDEs,
130 machine anchors, five literal roles, exact QVariant order, the UTF-16
method object, pending-reply handling, and the complete direct-transfer
inventory.

## Validation

Focused coordinator validation:

```text
PYTHONDONTWRITEBYTECODE=1 /Users/leo/.platformio/penv/bin/python3 \
  -m pytest -q tests/test_appdmclient_appupgrade_launch_routing.py
```

Result after remediation: **12 passed in 18.37s**.

Independent review reran the focused suite with the pytest cache disabled:
**12 passed in 17.82s**. It independently regenerated report SHA-256
`7584e9a7f4107f451bd690e05babefb60f6d20928ab27c5eb3efe4eb310b2449`,
which exactly matched the retained report.

Full tests-scoped integration validation after remediation:

```text
/Users/leo/.platformio/penv/bin/python3 -m pytest -q tests
```

Result: **868 passed, 351661 subtests passed in 115.01s**.

Hostile `PYTHONIOENCODING=utf-16` regeneration was byte-identical to the
retained UTF-8/LF report. `git diff --check`, UTF-8 decoding, terminal-LF,
no-CR, and no-NUL checks passed for the package. The deterministic regression
replaces the rootfs pathname after hashing but before member streaming and
requires fail-closed rejection with `changed during hash/member streaming`.

## Frozen reviewed paths

- `docs/agent-work/appdmclient-appupgrade-launch-routing/PLAN.md`
  - SHA-256 `2d275bb1df95d5c1650251fbbdec60ce695825ceb9991efd4fc89910277b1658`
- `docs/agent-work/appdmclient-appupgrade-launch-routing/WORKER.md`
  - SHA-256 `b6aafcc1d022c61e6518393de786f882227df210409ce895774fcf4ab49a8c67`
- `tools/uk_fw/appdmclient_appupgrade_launch_routing.py`
  - SHA-256 `4ba1b2157717bd13ae3e82b8553b7551e9d8db83f40ba1e81adb2a462ec86862`
- `tests/test_appdmclient_appupgrade_launch_routing.py`
  - SHA-256 `73e0912e9d3f47036ac453f0ccbf4005d1b77ddedbead18207a8e81a00545d4e`
- `evidence/appdmclient-appupgrade-launch-routing.md`
  - SHA-256 `97fd68c1bb70a41808b79ae955691b0f8bd9d629fdde2b1bff8dbb959c613e63`
- `evidence/artifacts/update-candidates/appdmclient-appupgrade-launch-routing-manifest.json`
  - SHA-256 `61f3c6327bfeb521df2970f9fd281f828c0bd11ee219fc1ba98b5f29be53bf62`
- `evidence/artifacts/update-candidates/appdmclient-appupgrade-launch-routing-report.json`
  - SHA-256 `7584e9a7f4107f451bd690e05babefb60f6d20928ab27c5eb3efe4eb310b2449`
- `evidence/artifacts/update-candidates/README.md`
  - SHA-256 `a76bd520aa8eada6409443a25e81ea040bc5ce959ec9803ea3f59d3938d1d997`

## Preserved runtime boundary

Static construction of the asynchronous launch call does not establish
session-bus socket reachability, same-bus participation, sender identity,
service ownership, uid/SMACK admission, message delivery, AppLauncher object
registration or dispatch, generated argv, child creation, successful `exec`,
resulting credentials/label, update authentication or acceptance, partition
writes, slot activation, boot acceptance, rollback behavior, root, or
persistence. Those facts remain unknown.

No recovered target executable was run, no bus or device was contacted, and no
request, media image, update package, executable payload, malformed input,
signature-bypass change, partition write, slot change, flash action, or
persistence mechanism was created during this package or its review.
