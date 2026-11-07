# DRI compatibility audit: the blocker is a missing GLIBCXX symbol version, not a categorical Mesa mismatch

Date: 2026-11-08. **Offline ELF inspection only. No QEMU run.** Performed because Astra C12
(`docs/planning/astra-c12.md`) required one read-only compatibility audit before deferring
application-rendering work — and explicitly warned that *"Mesa release numbers are not themselves a
definitive DRI incompatibility test."*

That warning was correct, and `docs/kernel/47` overstated its conclusion. This document records what
the audit actually found and withdraws the overstatement.

## What `docs/kernel/47` claimed, and why the claim was too strong

It stated that the "real cause" was that the staged `swrast_dri.so` is Mesa 18.2.8 while the vendor
`libEGL` is Mesa 11.2.1, and that "a Mesa 18 driver cannot be loaded by a Mesa 11.2.1 DRI loader".

That was an inference from two version strings. The two runs before it (5 and 6) established only that
staging four dependency libraries **did not fix** the load. They did not establish a categorical
incompatibility. Withdrawing the stronger claim now.

## The audit

Read-only `llvm-readelf`/`strings` inspection of the staged `swrast_dri.so` and its transitive closure
against the vendor libraries actually selected by `AppLauncher.sh`.

| Check | Result |
|---|---|
| ELF class / machine, driver vs vendor `libEGL` | both **ELF64, x86-64** — no architecture mismatch |
| glibc symbol versions required by `swrast_dri.so` | highest **GLIBC_2.17** (2012), well inside the vendor's `libc-2.25` |
| `libglapi.so.0` | present in the vendor image |
| `libLLVM-6.0.so.1` required `GLIBCXX` | **`GLIBCXX_3.4.21`, `GLIBCXX_3.4.22`** |
| vendor `/usr/lib/libstdc++.so.6.0.21` provides | up to **`GLIBCXX_3.4.21`** only |

**So the concrete defect is:** `swrast_dri.so` → `libLLVM-6.0.so.1` → requires `GLIBCXX_3.4.22` →
the vendor `libstdc++` stops at `3.4.21`. The chain fails at symbol-version resolution, before any
DRI interface negotiation is reached.

That is a **specific, resolvable dependency defect**, not an unavoidable ABI conflict.

## What the projection already has

| Artifact | GLIBCXX provided |
|---|---|
| `work/vm/kbuild/ws/inject-new/stage/libstdc++.so.6` (1,566,168 B) | **`GLIBCXX_3.4.22`** |
| image `/usr/lib/libstdc++.so.6` → `libstdc++.so.6.0.21` (symlink created by our staging, uid 501) | `3.4.21` |

So a narrowly scoped correction is credible with artifacts already on hand: make a
`GLIBCXX_3.4.22`-providing `libstdc++` resolvable **for the EGL path**, and the next failure — if any —
will be a genuine DRI negotiation problem rather than a C++ runtime one.

Two candidate scopes, neither to be applied yet:

- **narrow:** a dedicated directory plus a driver-loader/`LD_PRELOAD` arrangement so only the graphics
  path sees the newer `libstdc++`;
- **wide:** repoint `/usr/lib/libstdc++.so.6` at a `3.4.22` build, which affects **every** vendor
  binary — normally backward compatible, but a large divergence to justify.

## Classification, per Astra's outcomes

Astra gave three readings of the audit. This result is the **first**: *"a specific dependency or
symbol-resolution defect appears: the release-mismatch explanation is incomplete. A narrowly scoped
loader/dependency correction becomes a credible cheaper route, subject to demonstrated compatibility
and provenance."*

So the correct forward position for rendering is **A-prime**: not a 2016 Mesa build, and not a
wholesale EGL replacement, but first supply a `GLIBCXX_3.4.22` `libstdc++` to the graphics closure and
re-observe. That is cheaper than either A or B as originally framed.

## What is NOT claimed

- Not that this fix will work. It removes one measured blocker; the DRI interface negotiation behind it
  is still untested, and `swrast_dri.so` carries 665 undefined symbols whose resolution was not
  individually audited.
- Not that the Mesa generations are compatible. Their compatibility remains **unproven**, in both
  directions.
- Not that application rendering is close. Two further blockers are documented independently: IVI
  `visibility(0)`/`layer(nil)` (`docs/kernel/44`) and unimplemented input injection.

## The honest statement of the VM's current state (adopted verbatim from Astra C12)

> The VM boots the vendor kernel to multi-user and runs vendor Weston 1.10.0 and the vendor IVI shell
> user-interface. In the controlled run, the shell rendered the 1920×720 KIA boot splash, with three
> byte-identical captures. Tested Qt applications failed EGL initialisation and did not create or
> commit application buffers. Application presentation through IVI visibility/layer assignment remains
> unresolved, and input injection has not been implemented. This demonstrates vendor userspace boot and
> shell rendering, not an interactive infotainment application environment. Application-rendering work
> is deferred while defensive root-access analysis proceeds independently.

## Next exact action

Per Astra C12: **do not acquire or build Mesa.** Record this audit, defer rendering, and move the next
sessions to the defensive root-access register — starting from the vendor startup configuration,
identifying root-running services, their entry points and trust boundaries, and tracing the
highest-exposure candidate into its authentication or authorisation logic.

For security findings, Astra's distinction is adopted: keep **statically identified candidate**,
**VM-validated behaviour**, and **production-device-validated path** as separate statuses, and never
treat VM root access supplied by the research setup as a vendor vulnerability.
