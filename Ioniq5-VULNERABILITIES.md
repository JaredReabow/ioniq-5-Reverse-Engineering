# IONIQ 5 infotainment vulnerability and remediation register

Updated: 2026-10-28. Internal defensive research; no disclosure or vendor contact is implied.

## Scope and evidence rules

Target: official European Gen5W **Linux** `NE_E.EUR.S5W_L.001.001.260128`, vendor kernel `4.1.27-abl`. The owner's installed head-unit build is unknown. No physical or network head-unit access is available. VM observations do not establish hardware exploitability.

This 2026-10-26 backfill predates the sanitized owner USB finding: the later
export identified installed infotainment build `NE_E.EUR.S5W_L.001.001.250604`.
The `260128` package remains an official European research target, not an
observed installed build. See `evidence/vehicle-usb/README.md`.

This is a backfill from existing research, **not a new vulnerability discovery pass**. Entries distinguish verified behavior, static observations, unvalidated candidates, rejected hypotheses, and modification-created hazards. No numeric severity is assigned without reachability and impact evidence. Never infer missing security fixes from the kernel version alone. See `evidence/corrections-log.md` before relying on historical reports.

**Unverified actor reports.** Entries V-006, V-007 and V-008 originate from a third-party advisor summary supplied 2026-10-28 and are **hypotheses, not observations**. No code path, process identity, console device or reproduction accompanied them, and none has been validated in the recovered image. They are recorded so the claims can be tested and so they are not rediscovered from scratch. Nothing here should be treated as established until the listed validation is performed on the isolated VM or offline against the recovered rootfs.

## V-001 — Unsigned kernel modules execute after privileged loading

- **Status:** existing VM-verified behavior; hardware applicability untested.
- **Evidence:** `work/ui-recovery/SECURITY-FINDING-module-load.md`; `work/eu-260128/kernel.config`; `work/ui-recovery/SUMMARY-and-runbook.md`.
- **Observation:** kernel configuration enables modules but not module signatures. Prior QEMU experiments record module initialization executing against the vendor kernel. The VM boot uses the separately documented SDHCI guest-RAM adaptation; this is not a complete stock-device boot.
- **Preconditions:** module-loading privilege, or a separately established privileged loader accepting attacker-controlled modules. No unprivileged entry is established.
- **Potential impact:** a prior privileged foothold can extend into kernel execution; sensitive kernel state and enforcement may then be exposed. Persistent installation, actual key extraction, and physical-unit compromise are not demonstrated by this result.
- **Remediation:** enforce signatures against a protected module trust store; remove unused module loading; restrict loading privileges and writable module paths; consider disabling further loading after required boot modules initialize. Preserve required vendor drivers and recovery behavior.
- **Acceptance:** required signed modules load; unsigned and modified modules fail before initialization; unprivileged loading fails; legitimate update/recovery still works. Test only on disposable VM snapshots until device recovery is established.

## V-002 — Keystore test/debug/secure-boot-ignore build options

- **Status:** configuration observation; security impact unvalidated.
- **Evidence:** `work/eu-260128/kernel.config`; `Ioniq5-CHANGELOG.md` 0.39.0; `evidence/eu-keystore-manifest-root-of-trust.md`.
- **Observation:** historical analysis records `KEYSTORE_TESTMODE`, `KEYSTORE_TEST_MIGRATION`, `KEYSTORE_DEBUG`, and `KEYSTORE_SECURE_BOOT_IGNORE` enabled. Names alone do not establish a usable bypass or disclosure.
- **Preconditions / gaps:** trace compiled call sites, runtime gates, device-node permissions, SMACK policy, and actual debug activation. No unauthenticated reachability is established.
- **Potential impact:** test-only operations or sensitive logging could weaken production isolation if reachable.
- **Remediation:** disable production test/migration/debug paths unless essential; remove secret-bearing logging; verify secure-boot enforcement through the entire boot chain rather than a configuration label.
- **Acceptance:** negative tests for test-only ioctls and secret logs; signed boot/update positive controls; demonstrate that production enforcement remains active under the intended threat model.

## V-003 — Keystore device authorization depends on external policy

- **Status:** static observation; not a confirmed vulnerability.
- **Evidence:** `evidence/pre-disclosure-security-assessment.md` §3; `evidence/eu-keystore-manifest-root-of-trust.md`; corrections C8/C9.
- **Observation:** reviewed `keystore_open` lacks a capability check. Device mode, SMACK label/policy, and individual operation checks determine access; absence of an open-time capability check alone is not a defect.
- **Gap:** re-audit permissions and policy using the now-recovered rootfs and guest runtime. Older reports calling userspace inaccessible are stale.
- **Potential impact:** unauthorized key operations only if an inappropriate caller can reach a sensitive operation lacking further authorization.
- **Remediation:** least-privilege device permissions and SMACK rules; operation-specific authorization; regression tests from actual service identities.
- **Acceptance:** unauthorized identities cannot perform sensitive operations; required authorized services continue functioning; public-key-only operations are not misclassified as secret disclosure.

## V-004 — Boot trust inputs and embedded public-key binding

- **Status:** confirmed format/mechanism observations; trust bypass unproven.
- **Evidence:** `evidence/eu-boot-container-signature.md`; `evidence/eu-keystore-manifest-root-of-trust.md`; `evidence/vendor-kernel-vm.md`; corrections C12.
- **Observation:** boot containers carry a modulus; vendor manifest initialization consumes `ABL.oemkm` physical-memory input. Synthetic VM inputs initialize subsystems, but do not demonstrate acceptance by the real bootloader.
- **Gap:** establish authenticated binding of the manifest, command line, and verification key to a hardware-protected root. No bootloader dump or acceptance test establishes a missing binding.
- **Potential impact:** attacker-selected trust roots only if the preceding trusted stage permits substitution.
- **Remediation:** authenticate the full handoff and pin verification keys to a protected trust anchor; prevent untrusted command-line overrides.
- **Acceptance:** reject substituted manifests/keys/command lines before use, retain known-good signed boot and recovery controls.

## V-005 — Update integrity / rollback binding candidates

- **Status:** unvalidated current-build candidates, not demonstrated bypasses.
- **Evidence:** `evidence/pre-disclosure-security-assessment.md` §1; `evidence/community-field-evidence.md`; `evidence/eu-ota-container-structure.md`; corrections C4/C5/C13/C14.
- **Observation:** manifest CRC-32/size is not cryptographic authentication. A repaired CRC alone does not establish package acceptance; field evidence reports rejection despite repair. Older public rollback reports do not validate this build.
- **Gap:** trace recovered updater signature/digest/version binding and anti-rollback state. Native decryption recovery is not equivalent to a signature bypass.
- **Additional unvalidated source:** the owner's channel summary reports a 25–26 October updater-execution attempt stopped by signature checks followed by reboot. No message links, exact artifact identity, execution trace or demonstrated bypass were supplied. This does not promote V-005 to a confirmed vulnerability; provenance and platform caveats are retained in `evidence/community-chat-leads.md`.
- **Potential impact:** unauthorized or obsolete payload acceptance only if authenticated metadata does not bind payload identity and policy.
- **Remediation:** cryptographically bind all payload hashes, target identity, dependencies and version; enforce authenticated rollback policy with a supported recovery design.
- **Acceptance:** reject modified payloads, mixed-release metadata, wrong-target packages, and disallowed rollback; accept genuine supported upgrades and recovery.

## H-001 — Third-party USB root runner (not a vendor defect)

- **Status:** confirmed public modification behavior, **not established as present in stock firmware or installed in the current VM**.
- **Evidence:** `evidence/wideopen-payload-and-persistence.md`; `evidence/navi-extended-binary-analysis.md`; `Ioniq5-CHANGELOG.md` 0.25–0.29.
- **Risk:** the modification's privileged service executes scripts from removable media without authenticating them. This introduces a root execution hazard after installation; it must not be attributed to the vendor image.
- **Remediation:** do not include it in a deployable image; isolate bench-only tools; remove the service and verify both boot slots before returning any modified unit to use.
- **Acceptance:** no privileged removable-media autorun; check unit files, installed binaries and both slots; verify that removing the modification does not break authentic services.

## I-001 — EGL software-rendering copy bounds investigation

- **Status:** reproducible VM crash and instruction/caller evidence; **not a confirmed exploitable vendor vulnerability**. No severity/CVE claim.
- **Affected observed stack:** original recovered vendor `/usr/lib/libEGL.so.1.0.0` (SHA-256 `0c373e50d1a4700c2161628c2a2b61a25a9b5abbcd7bb52ccc763cf5020e3d53`) with the project's non-stock Mesa 18 software DRI module. Decoration-unset control triggers early Camera/Standby crashes; stock Intel-driver applicability is untested.
- **Evidence:** `evidence/navigation-launch-status-contract.md`; complete core archive `10fbb21b…24987c` and bounded ptrace archive `e0884a3c…fdeaae` (full digests in that note).
- **Observation:** faulting memcpy vector store targets an unmapped address 64 bytes before a writable buffer. Top captured stack word follows `memcpy@plt` in `dri2_wl_swrast_put_image2`. A width-derived stride is cached before a buffer update that can change the width; captured stride/count registers are -4. Original memcpy entry arguments and upstream invalid-size source are not yet directly measured.
- **Threat/impact boundary:** local VM application termination is established. Attacker influence, hardware reachability, arbitrary writes, code execution and persistence are not. Do not attribute a compatibility-induced failure to stock firmware without a stock-path reproduction.
- **Remediation direction:** verify dimensions after initialization/update; reject negative/overflowing dimensions, byte counts and out-of-range rectangles; refresh cached stride when width changes. Select a scoped VM adaptation only after confirming the ordering defect; do not weaken libc checks or force manager state.
- **Validation needed:** capture width before/after update and copy-entry arguments; test first swap, resize, zero-size hide/unhide, undecorated/decorated clients and normal positive-size buffers. Preserve existing Home/navigation controls and observe native return-to-Home pixels, not manager integers alone.

## V-006 — USB descriptor strings reach a privileged mount script (candidate)

- **Status:** **unverified actor report.** No code path, script, or descriptor consumer has been located in the recovered image yet. Explicitly a lead, not a finding.
- **Source:** third-party advisor summary supplied 2026-10-28. No logs, script excerpt, device identity or reproduction were provided. Recorded here for validation, not relied upon.
- **Claim:** a USB storage device's descriptor strings (vendor/product/serial) are passed into a mount script without authentication or sanitisation, so shell metacharacters embedded in a USB ID could be interpreted. Suggested payload class: short `cp /bin/sh` plus `chmod 4755` into a writable path.
- **Why this is plausible but unproven:** several stock components would normally prevent it. `udev` sanitises `ID_SERIAL`/`ID_MODEL` by replacing unsafe characters with `_`; USB string descriptors are **UTF-16LE**, so ASCII metacharacters arrive as `<char> 0x00` and a naive C reader stops at the first NUL, breaking injection; `blkid`-style properties are likewise constrained. A vulnerable path therefore requires a *custom* script that reads a raw descriptor or a converted string and interpolates it unquoted into a shell command. That specific artifact has not been found.
- **Length caveat is probably not the binding constraint:** a USB string descriptor carries at most 126 UTF-16 code units, so ~126 ASCII characters. The reported payload class is roughly 40 characters and would fit. The real constraints are encoding (UTF-16LE → NUL interleaving), any NUL-stripping or `iconv` conversion on the consumer path, and shell quoting.
- **Preconditions:** physical USB access to the head unit at boot or on attach; a privileged mount/automount service; a descriptor consumer that both converts UTF-16 and fails to quote; success also requires that the target `/tmp` (or equivalent) is executable and not read-only-protected.
- **Potential impact if confirmed:** unauthenticated code execution as the mount service's user, likely root, from a commodity device such as a Pi Zero configured as a USB mass-storage gadget. Persistence would depend on filesystem writability.
- **Remediation:** never interpolate device metadata into shell command lines; pass values as separate `argv` elements or via environment; validate against an allowlist of `[A-Za-z0-9_-]`; mount by filesystem UUID only after validation; run the mount helper unprivileged with narrowly scoped mount rights; add `nodev,nosuid,noexec` to removable-media mounts.
- **Validation needed:** locate the actual automount/mount invocation in the recovered rootfs; determine whether it reads `udev` properties (sanitised) or raw descriptors; test descriptor strings containing `;`, `` ` ``, `$()` and NUL-interleaved UTF-16 against a VM replica only; confirm whether `udev` or the kernel already blocks the path. If no custom consumer exists, close this as not applicable to the vendor image.
- **Do not test on a vehicle.** Any USB-device experiment belongs on the isolated VM snapshot with no network.

## V-007 — Media file parsing executes as root (candidate)

- **Status:** **unverified actor report.** No parser, service, or privilege evidence has been examined. Not a confirmed vulnerability.
- **Source:** third-party advisor summary supplied 2026-10-28. Stated as "runs as the root user" with the memory-corruption route described as possible but "unclear".
- **Claim:** media file parsing (USB audio/video playback, artwork, possibly container/metadata parsing) runs with root privileges.
- **Why this matters if true:** a parser running as root converts any memory-corruption defect in decode or metadata handling into root code execution from a file the user simply plugs in. That is a materially worse posture than the same bug in a sandboxed media service.
- **What is not established:** which component parses the file (GStreamer plugins, a vendor media library, or the update-package parser); whether any such defect is reachable; whether a crash gives control of the instruction pointer; and whether mitigations (ASLR, NX, stack canaries, FORTIFY) are effective in this build.
- **Preconditions:** physical or logical delivery of a crafted media file, plus a reachable memory-safety defect in a root-owned parser.
- **Remediation:** run all media parsing under a dedicated unprivileged uid with a restricted filesystem view; apply seccomp/`no_new_privs`; keep the parser off the root-owned service if a helper split is feasible; add a hardened allocator and enable full RELRO/PIE/FORTIFY where the toolchain permits; fuzz the parser.
- **Validation needed:** identify the parsing process from the running VM (`/proc/<pid>/status` `Uid:`), confirm effective uid, then fuzz that binary in the snapshot VM. Our isolated VM is the correct venue — a crash there is safe and reproducible; a crash on a vehicle is not.
- **Interaction with I-001:** I-001 is a crash in a graphics copy path, not a media parser. Do not conflate them.

## V-008 — Serial console running as root, password-gated (candidate)

- **Status:** **unverified actor report**, and the weakest of the three: a password gate already exists.
- **Source:** third-party advisor summary supplied 2026-10-28. Location on the board was not identified; console device, baud rate and login service were not specified.
- **Claim:** a serial console exists on the board that provides a root login, protected by a hashed password.
- **Why it is bounded:** a hashed-password login is normal engineering practice, not a defect. It becomes a finding only if the hash is weak or crackable, if the hash is reused from a public or default credential, if the login can be bypassed (for example via boot arguments, init override, or single-user mode), or if the hash material is extractable from an image that is otherwise distributed. The hash also implies `/etc/shadow`-equivalent material is present in the recovered rootfs, which is checkable offline.
- **Preconditions:** physical access to UART pads or a service connector; plus either knowledge of the password, a crackable hash, or a bypass.
- **Potential impact if the gate fails:** full root shell on the head unit, with consequences for both the vehicle owner and any party relying on the unit's isolation.
- **Remediation:** verify the hashing algorithm and cost (reject legacy DES/MD5 crypt); ensure no default, shared or reused credential; disable or physically gate the console on production parts; where a console must remain for service, restrict it to a non-root account with an audited escalation path; treat the bootloader command line as a trusted input so `init=`/single-user override cannot bypass the gate.
- **Validation needed:** offline only, from the recovered rootfs. Enumerate console/login configuration and the shadow-equivalent file; identify the hash algorithm and cost; check for default or duplicate credentials across builds. Do not attempt console access on a vehicle.
- **Note on our own boot-parameter work:** this project already established control of the ABL boot parameters in the VM. That is a *research* capability on a copy, and it must not be described as a remote or unauthenticated attack on a vehicle.

## Rejected / out-of-scope items

- **Keystore ioctl tail disclosure:** rejected; decoded ioctl size is `0x120`, covering fields read (correction C8).
- **`keystore_get_ksm_key` stack disclosure:** rejected by instruction-level review; private/public sub-buffers were misread (C9).
- Android/Telechips `hmg_nemesis` and `micomd` findings are not findings against this Linux/x86-64 target.
- Historical published CVEs require exact-component/version and code-path validation; do not relabel them as newly found or confirmed on `260128`.
- VM rendering slowness, watchdog timeouts and missing simulated CAN data are currently compatibility/integration issues, not established exploitable security defects.

## Maintenance

For each new issue record: stable ID, affected artifact/build and digest, source location, evidence type, caller/reachability, preconditions, bounded impact, remediation owner/status, regression test and remaining unknowns. Keep secrets and private keys out of reports. Append discovery/validation/correction events to `Ioniq5-HISTORY.md`; edit this register to reflect current conclusions. Preserve rejected findings to avoid rediscovery.
