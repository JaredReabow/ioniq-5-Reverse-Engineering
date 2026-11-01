# AppDMClient AppUpgrade launch routing — exact-static boundary

## Scope and result

This package binds the canonical EU `260128` rootfs member `/app/bin/AppDMClient` to its complete direct-call inventory for the launch proxy in unwind/FDE range `[0x8c0c0,0x8c2ab)`. It establishes the logical AppLauncher request tuple and the exact terminal branch that selects a staged AppUpgrade executable versus a source-root-derived AppUpgrade executable.

The supported bytes construct asynchronous launch requests. Static construction is **not** evidence that a session-bus daemon accepts or delivers a request, that the expected service or object is present, that AppLauncher creates a process, that `exec` succeeds, or that any update, partition write, boot acceptance, root access, or persistence follows.

## Canonical identities

- Rootfs archive:
  - size: `879109759`
  - SHA-256: `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`
- Canonical member: `./app/bin/AppDMClient`
  - size: `2226072`
  - SHA-256: `9a1fb796d7ac24fcce71c16e3dbee9306c888f43e705ee081f41b7d473978bd0`
  - GNU Build ID: `b2dbcc5231f444d8f1dd68eb7a2376323ce805df`
- Complete Homebrew LLVM instruction inventory:
  - count: `321113`
  - canonical SHA-256: `77c0187fc865feaf9ce6bac45ef22d6e3eef29981637190fdf1d225c6928a39d`
- Complete unwind/FDE inventory:
  - count: `2418`
  - canonical SHA-256: `48598865977ec790c555d4441e15c0ec7501d4999d5f66070d70b686f94c4301`

The analyzer opens the rootfs once through a no-follow descriptor, hashes the complete archive, rewinds that same stable file description, streams the selected regular member without writing it, and requires the supplied analysis ELF to be byte-identical to that canonical member. Descriptor and pathname identities are revalidated after member streaming so replacement between hashing and parsing fails closed.

## Launch proxy ABI and request construction

Unwind metadata places the helper at `[0x8c0c0,0x8c2ab)`; the next FDE begins at `0x8c2b0`. Under the x86-64 SysV C++ ABI, the helper operands are:

| Incoming operand | Role |
|---|---|
| `%rdi` | hidden return storage for `QDBusPendingReply<>` |
| `%rsi` | `QDBusAbstractInterface *` |
| `%edx` | logical integer application ID |
| `%rcx` | logical first `QString` (application name) |
| `%r8` | logical second `QString` (application location) |

The hidden return pointer is not a logical D-Bus argument.

The body constructs three `QVariant` objects:

1. type tag `2`, sourced from the saved integer;
2. type tag `10`, sourced from the first `QString`;
3. type tag `10`, sourced from the second `QString`.

Calls at `0x8c149`, `0x8c154`, and `0x8c15f` append them in exactly that order. The method object loaded at `0x8c18a..0x8c194` is the Qt static string whose UTF-16 data at `0x17c678` decodes to `launch`. `QDBusAbstractInterface::asyncCallWithArgumentList` is called at `0x8c199`.

The helper then constructs the pending-reply result in the hidden return storage and assigns the returned `QDBusPendingCall` at `0x8c19e..0x8c1ac`; it returns the result-storage address at `0x8c1f1`. This return handling does not report runtime delivery or success.

## Complete direct-caller inventory

There are exactly four direct transfers to `0x8c0c0`, and no direct jumps to it:

| Call site | Owning FDE | Logical app ID | First `QString` | Second `QString` |
|---|---|---:|---|---|
| `0x71a0a` | `[0x712c0,0x71c53)` | `300` | fixed `AppUpgrade` name | staged AppUpgrade path |
| `0x818f6` | `[0x7ff60,0x830e4)` | `300` | fixed `AppUpgrade` name | staged AppUpgrade path |
| `0x8201d` | `[0x7ff60,0x830e4)` | `300` | fixed `AppUpgrade` name | source-root-derived AppUpgrade path |
| `0x8817e` | `[0x87400,0x886e7)` | `300` | fixed `AppUpgrade` name | staged AppUpgrade path |

The common fixed name is constructed from the exact C string at `0x187644`; this address begins `AppUpgrade`, not the adjacent process-probe command text.

### Caller predicates

- `0x71a0a`: the object byte at `+0xe2` is nonzero, the staged path is built from the fixed staged base plus the AppUpgrade template, and helper `[0x70b50,0x712b9)` returns true.
- `0x818f6`: the staging function reaches its common terminal gates, the source-root marker is absent, and helper `[0x70b50,0x712b9)` returns true for the staged path.
- `0x8201d`: the staging function reaches its common terminal gates and the source-root marker is present. This branch passes the source-root-derived path and does not call the local staged-path validator at the terminal split.
- `0x8817e`: the ext-units path exists, the local route helper returns false, object bytes `+0x161` and `+0x160` are both zero, and helper `[0x70b50,0x712b9)` returns true for the staged path.

These are structural predicates. Names for unknown object fields are intentionally not inferred.

## Corrected staging-local provenance

The staging FDE starts at `0x7ff60`. Its logical source-root `QString` arrives in `%rsi` and is retained in `%r13` at `0x7ff69`.

Two different `QString` locals are then built:

1. At `0x80165..0x80196`, the AppUpgrade template is expanded with `%r13` (the source root), and the resulting **source-root-derived AppUpgrade path** is stored in stack slot `0x0` at `0x80192`.
2. At `0x801ab..0x801ef`, the fixed staged base is combined with the same AppUpgrade template, and the resulting **staged AppUpgrade path** is stored in stack slot `0x8` at `0x801ea`.

This corrects a provisional interpretation: **stack slot `0x8(%rsp)` is the staged destination, not the source-root parameter or source-derived executable**. The normal cleanup at `0x80a24..0x80a32` and exception cleanup at `0x82a9c..0x82aaa` destroy both locals.

## Terminal branch selection

Before the terminal split, the staging path has required existence of the source-root-derived executable (`0x80895..0x808a3`). It also checks the staged executable at `0x80eac..0x80ece`, but that check is **not** a common gate: a true result flows through permission handling at `0x815b0..0x815d2`, while a false result continues through state handling to the same terminal marker split. On the marker-absent branch, the later helper at `0x80f98` supplies the effective staged-path gate; on the marker-present branch, the source-derived executable is selected instead.

At `0x80f20..0x80f48`, the code expands a marker template with the retained source root and calls `QFile::exists` at `0x80f50`. The result is tested at `0x80f68`:

- **Marker present:** `0x80f6b → 0x81fe8`; call `0x8201d` receives app ID `300`, fixed name `AppUpgrade`, and stack slot `0x0`, the source-root-derived executable.
- **Marker absent:** the staged path from stack slot `0x8` is passed to `[0x70b50,0x712b9)` at `0x80f98`. A false result reaches `0x80fb0` without a launch request. A true result reaches `0x818c0`; call `0x818f6` receives app ID `300`, fixed name `AppUpgrade`, and the staged executable.

The local helper `[0x70b50,0x712b9)` structurally requires path existence, a successful read-open, four-byte ELF magic equality, and the `QFileInfo::isExecutable()` test. This local check is not an update signature check, does not authenticate executable content, and is not present on the terminal marker-present source-path branch.

## Relationship to AppLauncher evidence

The previously reviewed AppLauncher package independently binds dynamic app ID `300` to ordinary AppProcess construction: program location at `AppProcess+0x58`, generated options at `+0x60`, the option builder, and `QProcess::start`. That is a separate static binary edge. The AppDMClient async call does not itself prove that AppLauncher receives the message, selects the recovered fallback row, constructs any specific argv, starts a process, or successfully executes this location.

## Deterministic tooling

Tracked package:

- analyzer: `tools/uk_fw/appdmclient_appupgrade_launch_routing.py`
- tests: `tests/test_appdmclient_appupgrade_launch_routing.py`
- manifest: `evidence/artifacts/update-candidates/appdmclient-appupgrade-launch-routing-manifest.json`
- retained report: `evidence/artifacts/update-candidates/appdmclient-appupgrade-launch-routing-report.json`

The analyzer rejects schema/type drift, Boolean-as-integer values, duplicate JSON keys, linked or aliased inputs, rootfs/member/artifact identity drift, LLVM identity drift, Build-ID drift, complete instruction/FDE inventory drift, FDE-range drift, direct-caller drift, machine-anchor drift, literal drift, changing inputs (including rootfs pathname replacement between hashing and member streaming), and pre-existing output paths. Output is explicit UTF-8 with fixed LF through `sys.stdout.buffer`.

Public invocation form:

```text
<platformio-env>/bin/python3 tools/uk_fw/appdmclient_appupgrade_launch_routing.py \
  --rootfs <canonical-mango-rootfs.tar.gz> \
  --appdmclient <byte-identical-canonical-AppDMClient> \
  --manifest evidence/artifacts/update-candidates/appdmclient-appupgrade-launch-routing-manifest.json \
  --llvm-objdump <identity-bound-llvm-objdump> \
  --llvm-readelf <identity-bound-llvm-readelf>
```

No recovered target is executed.

## Bounded conclusion

The exact supported AppDMClient bytes contain a launch proxy that constructs a Qt asynchronous call with logical arguments `(300, AppUpgrade, selected executable path)`. Every direct caller is accounted for. In the staging terminal split, source-root marker presence selects the source-root-derived executable; marker absence selects the staged executable only after the local ELF/executable helper succeeds.

The package establishes static message construction and path selection only. Runtime bus participation, access policy in the actual process context, SMACK reachability, service ownership, object registration, authentication, queue acceptance, delivery, AppLauncher dispatch, process creation, successful execution, resulting credentials/label, update acceptance, partition writing, boot acceptance, rollback behavior, root impact, and persistence remain unknown.
