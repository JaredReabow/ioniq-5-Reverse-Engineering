# European `260128` custom-firmware and privileged-access feasibility

Status: defensive feasibility research for the owner's UK-origin 2021 IONIQ 5.
This report documents what would have to be true for privileged access or
custom native applications to be possible. It does not provide an exploit,
crafted update, signature bypass, privileged payload, flash procedure, or live
vehicle-compromise instructions.

## Executive conclusion

The exact package is an x86-64 Linux `S5W_L` system, not Android. A custom
application would therefore be a native Linux/Qt program or service rather than
an APK. In principle, persistent custom software requires all four of these
conditions:

1. an initial execution path accepted by the stock system;
2. a privilege transition to an identity allowed to alter the application or
   system partitions;
3. a persistence path that survives boot, SMACK policy and integrity checks;
4. an update or storage mechanism that preserves a recoverable, authentic
   boot chain.

No inspected evidence demonstrates that complete chain on stock
`NE_E.EUR.S5W_L.001.001.260128`. Published Gen5W_L research establishes that
older sibling builds have contained serious update-path flaws, but it does not
establish that those flaws remain reachable on this January 2026 build.

## Exact artifact identity

The vehicle-family-correct official package is:

- software: `NE_E.EUR.S5W_L.001.001.260128`;
- package ID: `IONIQ5_EU`;
- model code: `101489`;
- completed-manifest SHA-256:
  `53da7ec0fbb3ec3a6876c98f3720588d8caf2ebf92561b1f96478e35e80ad7b3`;
- 35 of 35 payloads match their declared sizes and signed CRC-32 values;
- the map and both voice archives match their supplied MD5 sidecars;
- the frozen 36-file SHA-256 inventory digest is
  `f06752ea7cbf296ef7d7d7482f5ba96a3349161fc7ad0d60b36b042f62ef5b51`.

The representative exact-build boot container
`HU/images/iasImage_1280_sub` has SHA-256
`55e9a31be5ca734a7af111613ae6ce83cdc579b27138c5f54700f78263056eb0`.
Its recovered kernel has SHA-256
`f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`.

## Observed platform and trust boundaries

| Layer | Exact-build observation | Feasibility implication |
|---|---|---|
| CPU and OS | ELF64 x86-64, Linux `4.1.27-abl`, systemd init, ext4 root on `mmcblk0p3` | Android/TCC803x and APK-oriented methods are not applicable. |
| Application model | Public Gen5W_L evidence places Qt/QML applications under `/app/share` and AppNavi under navigation partitions | Sideloading means native binary/service deployment, not use of an Android package manager. Exact stock userland paths remain encrypted in the official package. |
| LSM | SMACK is compiled in and selected as the default security module | Unix root alone may not establish access to every IPC object, device node or labelled file. Exact policy must be recovered or observed. |
| Update trust | Exact kernel decompilation recovers `verify_oem_signature`, `manifest_key_verify_digest`, kernel asymmetric-key lookup and public-key signature verification | Patching only a userland updater is not sufficient evidence that a modified package will be accepted. |
| Key service | `keystore_ioctl` and `keystore_verify` are present in the kernel | Device-node ownership, SMACK labels, client registration and operation-specific checks remain decisive unknowns. |
| Modules | Modules are enabled and module signing is not configured | This is a post-privilege extension mechanism, not a demonstrated initial entry route. |
| Memory/debug | No KASLR; debugfs, `/dev/kmem`, `/proc/kcore`, kexec and non-strict `/dev/mem` are compiled in | These increase post-entry research value, but runtime permissions and SMACK policy determine reachability. |
| kexec | `sys_kexec_load` requires `CAP_SYS_BOOT` and honours `kexec_load_disabled` | It cannot be treated as an unprivileged boot-chain bypass. |

Exact-build symbol recovery produced 64,923 validated kallsyms entries. Ghidra
recognized 25,147 functions, renamed 25,068, and decompiled 48 of 49 selected
security-relevant functions. These are static observations; they do not prove
that a particular interface is reachable from an unprivileged process.

## Feasibility paths

| Path | What it could provide | Preconditions | Exact `260128` result |
|---|---|---|---|
| Official signed update | Supported persistent installation | Hyundai-authorized package, compatible region/model/version and intact trust chain | Observed mechanism; no authorization path for owner-created payloads is known. |
| Historical AppNavi replacement | Initial execution on some Linux Gen5W systems | A reachable Engineering/SOP path and a build that accepts the replacement | Family-compatible idea; exact-build gate and acceptance policy remain unverified. |
| Published Chimaera-class update flaws | Key disclosure or weakened signature/version enforcement on the tested sibling build | Vulnerable update components and a reachable path to exercise them | Demonstrated on `AE_E_PE_EUR.S5W_L001.001.211214`, not on `260128`; current patch state is unknown. |
| Device-derived decryptor workflow | Offline access to encrypted update payload contents | Prior access to the unit's `DecryptToPIPE` component and associated device-derived material | Downstream research tool, not an initial entry route. No required material is present in the package. |
| Rootfs/application replacement | Persistent native applications and systemd services | Prior privileged execution, decrypted contents, accepted repackaging and a recovery route | Publicly demonstrated as a post-compromise pattern; not established for stock `260128`. |
| Unsigned kernel module | Powerful post-root instrumentation | Sufficient privilege, writable module storage and policy permission | Kernel configuration permits unsigned modules; initial reachability is not demonstrated. |
| kexec or memory-device route | Alternate-kernel or deep diagnostic research | Root-equivalent capabilities, permissive runtime sysctls/nodes and policy | Static kernel features exist, but the required privilege and runtime policy are not established. |
| Hardware storage analysis | Frozen-state recovery of exact policy and applications | Correct board/storage identification, lawful bench access and a non-destructive acquisition method | Evidence route only; no physical procedure or write is part of this report. |

## Candidate vulnerability-research surfaces

These are audit targets, not claimed vulnerabilities. A finding requires exact
code evidence, reachability, attacker-controlled input, impact and a safe local
reproducer before it can be treated as more than a hypothesis.

1. **Update-envelope parsing.** Inspect integer bounds, path handling,
   manifest parsing, archive extraction and error cleanup in the userland update
   components once plaintext exact-build code is lawfully available.
2. **Kernel keystore interface.** Determine device-node mode, owner/group,
   SMACK label, client-registration rules and per-operation authorization.
   Absence of one global `capable()` check is not proof of unprivileged access.
3. **AppNavi and Engineering/SOP dispatch.** Establish the exact launcher,
   version gate, input validation, file-acceptance rules and process identity.
4. **Privileged IPC.** Inventory D-Bus, local sockets, shared memory and custom
   RPC used by updater, navigation, telematics and system services; test only
   extracted parsers or mocks for authorization and memory-safety errors.
5. **SMACK mediation gaps.** Compare service labels, filesystem labels and
   rules for unintended write or IPC paths. Kernel configuration alone cannot
   answer this question.
6. **Native dependency age.** Recover exact library versions and build flags,
   then compare them with published advisories. Version matching is triage, not
   proof of exploitability.
7. **Boot and rollback policy.** Identify whether bootloader verification,
   anti-rollback counters, recovery partitions and OEM key usage are separate
   from the kernel-level update verifier.
8. **Region and provisioning inputs.** Trace where region, modem, carrier,
   navigation licensing and telematics provisioning are read and enforced.

## Evidence needed to move a hypothesis forward safely

The next decisive evidence is:

- plaintext exact-build rootfs, AppNavi, GUI and update components obtained
  through a legitimate static or device-owner acquisition route;
- complete service units, users/groups, file capabilities and SMACK rules;
- exact `/dev/keystore` metadata and IPC authorization;
- installed-car version-screen readback to bind the package analysis to the
  vehicle's current state;
- bootloader, recovery and storage-layout evidence from documentation or an
  isolated spare/bench unit;
- local harnesses for individual parsers and policy decisions, using synthetic
  non-vehicle inputs;
- independent review of any suspected new vulnerability before disclosure or
  further testing.

## EU/AUS implications

The European and Australian packages each contain 36 files. Thirty-two paths
are common: six are byte-identical, nineteen have equal size but different
SHA-256 values, and seven differ in both size and content. The different-size
set includes `AppUpgrade`, `update.tar.gz`, `mango-rootfs.tar.gz`,
`mango-rwdata.tar.gz`, `new_gui.tar.gz`, `.lge.upgrade.xml`, and
`.whatsnew.tar.gz`.

The matching EU and AUS `iasImage_1280_sub` kernels share the same extracted
configuration hash and broad security posture, but their boot containers and
kernel bytes differ. EU was built on 28 January 2026; AUS was built on
19 March 2026. Shared architecture therefore does not imply safe artifact
interchangeability. Region transition remains gated on bootloader policy,
OEM-key usage, modem and telematics provisioning, navigation licensing,
rollback behaviour and a recoverable stock restore route.

## Published-method sources

| Mechanism | Inspected source and identity | Version scope used here |
|---|---|---|
| `navi_extended` | g4933, GitLab `gen5w/navi_extended`, inspected commit `7605d04b5ff8cba52ec2fe325105068f439df2d1` | Historical Linux `S5W_L` AppNavi replacement; exact `260128` gate unproved. |
| `update_decryptor` | g4933, GitLab `gen5w/update_decryptor`, inspected commit `a5102dc83bafe8ebdefaf8b22dde76c1460c1d2d` | Requires device-derived `DecryptToPIPE` and key material. |
| `update-patcher` | g4933, GitLab `gen5w/update-patcher`, inspected commit `92f5193e3ec4de98e9a8f368a91e7f5fb316d4b0` | Post-compromise rootfs/update persistence. |
| Wi-Fi/SSH loop | g4933 Gen5W repository, inspected commit `dadcd7126a78f05b0d5b09e02e55fe7951910b26` | Post-entry access; no exact `260128` demonstration. |
| Chimaera/CVE-2023-26243 through -26246 | Costantino, De Vincenzi and Matteucci, *A vehicle firmware security vulnerability: an IVI exploitation*; CVE and GitHub Advisory records linked in `evidence/community-entry-methods.md` section 13 | Demonstrated on `AE_E_PE_EUR.S5W_L001.001.211214`, not this build. |
| NEMESIS | `https://github.com/xwtk/hmg_nemesis`, inspected shallow-clone head `fe2db9396b34f279a8900591e9994fd538d30f9a` | Android 4.4.2/TCC803x, author-tested firmware `260507`; platform mismatch. |

The full source descriptions, URLs, evidence grades and limitations are in
`evidence/community-entry-methods.md` sections 12–14. The independent NEMESIS
artifact and commit review is in `evidence/hmg-nemesis-compatibility.md`
sections 2, 11 and 13. Exact-build kernel claims in this report are bound to
`evidence/eu-kernel-decompilation.md`, not inferred from those public methods.

## Decision

Custom native applications are technically plausible after authorized
privileged execution because the system is a conventional x86-64 Linux/Qt and
systemd platform. The unresolved problem is the complete, exact-build path from
stock state to such execution while preserving the OEM trust and recovery
model. Current evidence supports continued static audit and isolated parser or
policy testing. It does not support constructing a flashable modified image or
claiming a working stock-to-root route.
