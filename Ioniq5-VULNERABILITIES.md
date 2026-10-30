# IONIQ 5 infotainment vulnerability and remediation register

Updated: 2026-10-30. Internal defensive research; no disclosure or vendor contact is implied.

## Scope and evidence rules

Target: official European Gen5W **Linux** `NE_E.EUR.S5W_L.001.001.260128`, vendor kernel `4.1.27-abl`. The owner's installed head-unit build is unknown. No physical or network head-unit access is available. VM observations do not establish hardware exploitability.

This 2026-10-26 backfill predates the sanitized owner USB finding: the later
export identified installed infotainment build `NE_E.EUR.S5W_L.001.001.250604`.
The `260128` package remains an official European research target, not an
observed installed build. See `evidence/vehicle-usb/README.md`.

This is a backfill from existing research, **not a new vulnerability discovery pass**. Entries distinguish verified behavior, static observations, unvalidated candidates, rejected hypotheses, and modification-created hazards. No numeric severity is assigned without reachability and impact evidence. Never infer missing security fixes from the kernel version alone. See `evidence/corrections-log.md` before relying on historical reports.

**Third-party claims and their disposition.** Three physical-access claims were
received from a third-party advisor summary and then tested offline against the
recovered firmware. One was confirmed as a genuine defect (V-006) but with a
different mechanism than claimed; the other two were reduced to configuration or
design observations (V-007, V-008). The detailed dossiers, including reproduction
notes and precise code locations, are withheld from this public tree pending
coordinated vendor contact.

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

## V-006 — Privileged USB handling contains a command-construction defect

- **Status:** confirmed: complete static call chain verified at instruction
  level, and **root command execution demonstrated end-to-end in the project
  QEMU research harness** (guest vendor `usb-automount` + vendor udev, root
  marker created from an injected device-supplied string, 2026-10-30). Not
  tested on physical hardware.
- **Disclosure status:** technical detail is withheld from this public tree pending
  coordinated vendor contact. Recorded here as a status entry only.
- **Summary:** reviewing the removable-media handling in the recovered userspace
  identified a code path where device-supplied identification data reaches a shell
  command construction without shell-safe handling. A device presenting the
  relevant interface type can therefore influence a command that runs in a
  privileged service context. The affected property, the upstream sanitizer's
  actual character policy, and the shipped service configuration have each been
  verified at instruction level in the research tree (withheld here).
- **Preconditions:** physical access to a configured USB port plus a suitably
  configured device descriptor. This is not a remote or unauthenticated network
  vector.
- **Remediation direction:** eliminate shell invocation on this path entirely,
  construct the helper command from a fixed argument vector, treat device-supplied
  strings as untrusted data rather than command text, and reduce the privilege of
  the device-handling service to the minimum required for mounting.
- **Validation still needed:** confirmation on the installed owner build
  (research package `260128` only) — deliberately not performed on hardware.

## V-007 — Media parsing runs without privilege separation

- **Status:** configuration observation; information-class only, not a
  vulnerability.
- **Summary:** media scanning, indexing, playback and metadata extraction are
  configured to run with the same identity as the rest of the system services,
  and no service-level sandboxing is configured. No parser defect has been
  identified.
- **Why it is recorded:** it is a risk amplifier. Any future memory-safety defect
  in a parser would not be contained by an unprivileged boundary.
- **Remediation direction:** run media parsing under a dedicated unprivileged
  identity with restricted filesystem and network access.

## V-008 — Serial console is available and password-gated

- **Status:** shipped configuration; unresolved as a vulnerability.
- **Summary:** a serial console login is present on this build and the boot
  script enables it by default on every boot (a marker file is created
  unconditionally; only a specific driver module parameter removes the console
  device). The runtime account file it installs grants the superuser account a
  login shell. The console is guarded by a password; the password storage uses
  a sound modern hashing scheme and no default value was recovered.
- **Why it is recorded:** it is a physical-access path to the unit that exists
  by design and by default. It becomes a finding only if the credential is
  weak, shared or bypassable, which has not been established.
- **Remediation direction:** disable the console by default in production
  builds, make the secure mode the default rather than the exception, and
  ensure any maintenance credential is unique per unit and cannot be
  re-enabled by an unauthenticated state change.

## V-009 — Application launcher can start binaries without invoking signature verification

- **Status:** statically confirmed control-flow defect; details withheld.
- **Disclosure status:** technical detail withheld from this public tree
  pending coordinated vendor contact; recorded as a status entry only.
- **Summary:** the navigation/application launcher's dispatcher selects between
  verified and unverified launch paths using an internal state value; on the
  unverified path the target binary is started without the signature routine
  ever executing, and on the verified path a failed check does not stop the
  launch. Verification key material is also read from a world-accessible
  runtime location rather than a protected store.
- **Preconditions:** write access to the application/navi media path, e.g. an
  SD/USB medium or a prior local foothold; alone this is a defense-in-depth
  failure against replacement of first-party applications.
- **Remediation direction:** make verification non-bypassable and
  unconditional, treat verification failure as terminal for the launch, keep
  trust anchors on read-only authenticated media, and pin key material.
- **Validation still needed:** end-to-end demonstration of a replacement
  binary launching under production state values on a unit.

## V-010 — Engineering-mode keypad credential derives from static unsalted digests

- **Status:** statically confirmed (machine-code verified); credential values
  withheld from this public tree.
- **Summary:** the engineering/dealer menu gate reduces to hashing the entered
  code with a single unsalted modern hash and comparing against two baked
  digest constants. At least one digest corresponds to a vendor default code
  that is identical across the build (no per-unit salt or derivation was
  found). Lockout logic is client-side rate limiting only.
- **Preconditions:** physical access to the screen/keypad. Impact class is
  unauthorized diagnostic control (device variant, partition selection,
  update/test triggers), not demonstrated direct code execution.
- **Remediation direction:** remove static default codes, bind credentials
  per unit to a protected secret, enforce lockout server-side, and reduce the
  privileged actions reachable from the menu.
- **Validation needed on a unit:** confirm the menu actually reaches
  partition/update controls on the owner build, and determine whether the
  second digest is a per-dealer code.

## V-011 — Marker files under world-writable runtime paths trigger privileged actions

- **Status:** configuration observation; candidates, each individually
  unvalidated.
- **Summary:** several enabled systemd path units watch marker files under the
  world-writable runtime directory and start root services, change firewall
  posture, or force a reboot when a marker appears; at least one forced-reboot
  trigger is reachable by any local process creating a zero-length file
  (local denial of service class). Related service code was observed
  containing command-execution templates with unvalidated substitution inputs
  (follow-up taint tracing required). A diagnostic network-port relaxation is
  gated only by one such marker.
- **Why it is recorded:** cheap local amplification surfaces; they are also
  persistence candidates for a modified unit.
- **Remediation direction:** move trigger state to root-owned authenticated
  locations; require an authenticated request for privileged actions; audit
  command-execution templates for unvalidated substitution inputs.
- **Validation needed:** per-unit-file reachability on a running unit, and
  taint traces for the command templates before any of these is promoted to
  a vulnerability.

## V-012 — Privileged services import environment files from a world-writable location

- **Status:** configuration defect confirmed in the shipped unit files;
  exploitation chain not demonstrated.
- **Summary:** more than ten enabled root-level services read their process
  environment from a fixed, predictable file under the world-writable runtime
  directory, which a support script also rewrites at boot with no ownership
  or permission protection. The environment-file format accepts arbitrary
  variables, including dynamic-loader overrides, so a low-privilege local
  process that writes this file can inject loader settings that take effect
  inside privileged processes when they next start. Mandatory-access labels
  observed in the image do not block the related service-to-unlabeled-process
  access.
- **Preconditions:** any local code execution (any application or the
  USB-facing services), plus a privileged service restart within the session.
- **Remediation direction:** keep service environment state in root-owned
  protected paths with restrictive modes, validate loader-variable
  allowlists, and run loader overrides inert for privileged services.
- **Validation needed:** confirm on a running unit which local subjects can
  write the file, and the practical restart triggers for each service.

## V-013 — Software-update signature trust anchor is stored unprotected

- **Status:** configuration defect confirmed in the recovered image; the
  swap scenario itself not demonstrated.
- **Summary:** the verified update pipeline was reconstructed end-to-end in
  the research tree: an update manifest from the USB path is cryptographically
  verified before any payload is unpacked or written, which is sound design.
  However, the verification public key is an ordinary file in an
  application-share directory on the read-write root filesystem rather than a
  protected store, and multiple update clients reference the same file. A
  privileged local write primitive can therefore replace the trust anchor and
  cause all future updates — wired and over-the-air paths — to accept
  packages signed by a substitute key. Encryption of update payloads is
  separate from and does not substitute for this anchor's protection.
- **Preconditions:** an existing privileged local write primitive; not a
  standalone remote or physical-USB-only attack.
- **Remediation direction:** keep trust anchors read-only or
  integrity-attested (verified boot measurements, read-only partition, or MAC
  confinement with explicit authorization), bind them per-unit, and make
  anchor changes an authenticated, logged event.
- **Validation needed:** runtime mount/label state of the anchor path on a
  unit, and per-client behavior when the anchor changes mid-session.

## Rejected / out-of-scope items

- **Keystore ioctl tail disclosure:** rejected; decoded ioctl size is `0x120`, covering fields read (correction C8).
- **`keystore_get_ksm_key` stack disclosure:** rejected by instruction-level review; private/public sub-buffers were misread (C9).
- Android/Telechips `hmg_nemesis` and `micomd` findings are not findings against this Linux/x86-64 target.
- Historical published CVEs require exact-component/version and code-path validation; do not relabel them as newly found or confirmed on `260128`.
- VM rendering slowness, watchdog timeouts and missing simulated CAN data are currently compatibility/integration issues, not established exploitable security defects.

## Maintenance

For each new issue record: stable ID, affected artifact/build and digest, source location, evidence type, caller/reachability, preconditions, bounded impact, remediation owner/status, regression test and remaining unknowns. Keep secrets and private keys out of reports. Append discovery/validation/correction events to `Ioniq5-HISTORY.md`; edit this register to reflect current conclusions. Preserve rejected findings to avoid rediscovery.
