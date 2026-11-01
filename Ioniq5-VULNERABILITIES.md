# IONIQ 5 infotainment vulnerability and remediation register

Updated: 2026-11-03. Internal defensive research; no disclosure or vendor contact is implied.

## Numbering and provenance

This register is edited by more than one workstream, and entries have been appended concurrently. Two
consequences, both worth knowing before citing a number:

- **Entry numbers are not stable over time.** A finding added early may later sit at a different number as other
  entries are inserted ahead of it. When referencing an entry in the changelog or in correspondence, cite it by
  **title as well as number**, and treat the title as authoritative.
- **Late amendments carry the number of the entry they amend**, in headings of the form
  `## Amendment to V-0NN (X) — …`. These are not separate findings; they belong to the entry named.
- **Entries imported from the parallel repository carry their original number in a provenance line** directly
  under the heading, of the form `(Imported from the parallel repository, where this was numbered V-0NN.)`. That
  original number is not this file's number for the entry. The two lineages had independently used several of the
  same numbers for different findings, so imported entries were renumbered rather than reusing a number already
  taken here. An old citation therefore still resolves, by reading its provenance line, to the correct finding;
  but the heading number in this file is the authoritative one, and numbering is not stable in either lineage.

A collision was found and corrected on 2026-10-31: three appended sections had re-used `V-012`, `V-013` and `V-014`
while the sequence had already advanced past them. They now appear as **V-033** (production compositor ships full
DWARF), **V-034** (update trust anchor on a writable root) and **V-035** (root media parsers link ageing codec
libraries). References in the changelog written before that date use the old numbers and should be read by title.

## Scope and evidence rules

Target: official European Gen5W **Linux** `NE_E.EUR.S5W_L.001.001.260128`, vendor kernel `4.1.27-abl`. The owner's installed head-unit build is unknown. No physical or network head-unit access is available. VM observations do not establish hardware exploitability.

This register began as a backfill and now also records continuing exact-build review. Entries distinguish verified behavior, static observations, unvalidated candidates, rejected hypotheses, and modification-created hazards. No numeric severity is assigned without reachability and impact evidence. Never infer missing security fixes from a package or kernel version alone. See `evidence/corrections-log.md` before relying on historical reports.

**Validation status of the 2026-10-28 advisor report.** The three claims supplied as a third-party summary were tested offline against the recovered rootfs on 2026-10-28. None was accepted as stated:

- **V-006 is not a USB-to-root command-injection path in this build.** The MTP branch constructs unquoted `system()`/`popen()` commands, but `usb_id` calls both `util_replace_whitespace()` and `util_replace_chars(..., NULL)`. The second call restricts `ID_SERIAL_SHORT` to alphanumerics plus `#+-.:=@_`. A full VM run delivered the MTP event to the authentic root automounter and rewrote command separators/substitution characters to `_`; no command executed. The unsafe shell construction remains a latent defect and denial-of-service surface.
- **V-007 was confirmed as a configuration fact** (media parsers default to uid 0 with no isolation) and reclassified as informational hardening, not a vulnerability.
- **V-008 was confirmed as shipped configuration** (a password-gated root console) but **not** as a vulnerability; the SHA-512 hash is sound and no bypass was found.

Nothing here was demonstrated on a running unit or on hardware. Evidence lives under `work/vm/vendor-userspace-260128/validation-261028/`.

## V-001 — Unsigned kernel modules execute after privileged loading

- **Status:** existing VM-verified behavior; hardware applicability untested.
- **Evidence:** `work/ui-recovery/SECURITY-FINDING-module-load.md`; `work/eu-260128/kernel.config`; `work/ui-recovery/SUMMARY-and-runbook.md`.
- **Observation:** kernel configuration enables modules but not module signatures. Prior QEMU experiments record module initialization executing against the vendor kernel. The VM boot uses the separately documented SDHCI guest-RAM adaptation; this is not a complete stock-device boot.
- **Preconditions:** module-loading privilege, or a separately established privileged loader accepting attacker-controlled modules. No unprivileged entry is established.
- **Potential impact:** a prior privileged foothold can extend into kernel execution; sensitive kernel state and enforcement may then be exposed. Persistent installation, actual key extraction, and physical-unit compromise are not demonstrated by this result.
- **Remediation:** enforce signatures against a protected module trust store; remove unused module loading; restrict loading privileges and writable module paths; consider disabling further loading after required boot modules initialize. Preserve required vendor drivers and recovery behavior.
- **Acceptance:** required signed modules load; unsigned and modified modules fail before initialization; unprivileged loading fails; legitimate update/recovery still works. Test only on disposable VM snapshots until device recovery is established.

## V-002 — Keystore test/debug/secure-boot-ignore build options

- **Status:** exact status-gate semantics confirmed; security impact remains conditional.
- **Evidence:** `work/eu-260128/kernel.config`; `evidence/eu-keystore-secure-boot-ignore.md`; `evidence/eu-keystore-manifest-root-of-trust.md`.
- **Observation:** `KEYSTORE_TESTMODE`, `KEYSTORE_TEST_MIGRATION`, `KEYSTORE_DEBUG`, and `KEYSTORE_SECURE_BOOT_IGNORE` are enabled. Exact instructions now bind the IGNORE option narrowly: keystore initialization and kernel-client registration proceed without a platform secure-boot-status query, while seed/client setup failures and the separate OEM signature-verifier chain remain. It is not a general update or verified-boot bypass.
- **Preconditions / gaps:** device-node permissions, SMACK policy, actual debug activation, and whether a caller gains a security-relevant operation from status-gate removal remain unknown. No unauthenticated reachability is established.
- **Potential impact:** clients may use keystore services when the platform reports secure boot disabled; test-only operations or sensitive logging could further weaken production isolation if reachable. No signature acceptance or root transition is shown.
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
- **Observation:** boot containers carry a modulus; vendor manifest initialization consumes `ABL.oemkm=<size>@<physical-address>` input. The loader-supplied value is absent from the signed packaged command line. The manifest provides public-key digest/usage admission policy for a trusted-only keyring rather than automatically inserting certificates. Synthetic VM inputs initialize subsystems but do not demonstrate acceptance by the real bootloader.
- **Additional exact candidates:** copied size accepts `1..0x4000000`; conditional header/extension reads are not fully bound to that allocation; and feasible header rejection frees `base + 0x24` rather than the allocation base. These are conditional boot-time OOB-read and invalid-free/crash-or-corruption candidates.
- **Gap:** establish authenticated binding of the manifest, loader-added command line, and physical-memory blob to a hardware-protected root. Runtime input control, controlled allocator corruption, certificate admission, and bootloader acceptance remain unproved.
- **Potential impact:** attacker-selected admission policy, boot crash, or kernel corruption only if the preceding trusted stage permits substitution. No controlled write, code execution, first root, or persistence is established.
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

## I-001 — EGL copy-path ordering defect (measured on the authentic binary)

- **Status:** **mechanism measured**, still not a demonstrated exploitable vulnerability. No severity or CVE claim. Updated 2026-10-29.
- **Affected stack:** vendor `/usr/lib/libEGL.so.1.0.0` (SHA-256 `0c373e50…0e3d53`) on its **Wayland software (swrast) display path**, running with the project's Mesa 18 software DRI module.
- **Scope refinement (2026-10-29):** the binary contains four distinct surface constructors — `dri2_create_window_surface`, `dri2_drm_create_window_surface`, `dri2_wl_create_window_surface` and `dri2_wl_swrast_create_window_surface`. The `-1` sentinel is written by the **swrast-specific** constructor, and the affected `put_image2`/`get_image`/`swap_buffers` functions all belong to the `dri2_wl_swrast_*` family. The hardware paths use different constructors and do not share this vtable, so **this evidence does not implicate the i965/i915 hardware path**. The defect should therefore be read as specific to the software-rendering path that this VM necessarily uses, not as a defect shown to affect cars with working Intel graphics.
- **Measurement:** an in-VM hardware-breakpoint observer captured two stages on the authentic `AppCamera` inside the real launcher chain — `libEGL+0x16f16` (before the width cache) and `libEGL+0x16f1e` (immediately after `swrast_update_buffers` returns) — reading the surface fields at `+0x2c`/`+0x30`:
  - **P1:** same surface pointer `0x3ac74f68e0`, width **-1**, height **-1**
  - **P2:** same surface pointer, width **1920**, height **720**
- **Conclusion:** the dimensions are the creation sentinel at P1 and the real geometry at P2, so `swrast_update_buffers` populated them *during this invocation*, while the copy path had already derived its stride from `Width = -1` (yielding `-4`). The stale-stride ordering defect is therefore **measured**, not inferred. This supersedes earlier statements that width change had not been observed.
- **Threat/impact boundary:** local VM application termination is established. Attacker influence over the dimension values, stock-driver reachability, arbitrary writes, code execution and persistence remain unestablished. Do not describe this as a remotely reachable defect.
- **Remediation direction:** validate the surface dimensions before deriving a copy stride, or re-derive the stride after `swrast_update_buffers` returns; treat a non-positive width or height as "no copy" rather than converting it into a byte count. Reject negative and overflowing sizes in the copy loop.
- **Validation still needed:** reproduce with stock Intel graphics; test zero-size and first-swap buffers specifically; confirm that rejecting non-positive dimensions does not regress legitimate rendering.

## V-006 — Unsafe MTP shell construction, descriptor injection blocked (LATENT DEFECT)

- **Status:** the shell sink and physical MTP branch are VM-confirmed, but **USB descriptor-to-command execution is rejected for this exact build**. This supersedes the 2026-10-28 static classification.
- **Severity framing:** defects are not scored numerically here. Physical USB can reach and disrupt this root helper, but root command execution through `ID_SERIAL_SHORT` is not established.
- **Affected component:** `/app/bin/usb-automount` (43,136-byte stripped x86-64 ELF), started by `lib/systemd/system/usb-automount.service`, which contains **no `User=` directive** and therefore uses the system-service default of uid 0.
- **Evidence:** `work/vm/vendor-userspace-260128/validation-261028/v006/` (report, udev inventory, sanitiser excerpt, disassembly). Independently re-verified with `llvm-objdump`:
  - `0x5326` `__sprintf_chk` builds `"%s %s %s %s &"` (`.rodata 0x7928`) from `"/usr/bin/go-mtpfs"`, `"--dev"`, **`ID_SERIAL_SHORT`**, and `"/media/mtp/<ID_SERIAL_SHORT>"`; `system()` is called at `0x535f`. No quoting or escaping.
  - `0x53b9` `popen()` runs `"cat /proc/mounts | grep %s"` (`.rodata 0x7936`) using the same serial-derived string.
  - `ID_SERIAL_SHORT` is read at `0x4146` via `udev_device_get_property_value` (`.rodata 0x760c`).
  - Branch selection at `0x44c3`–`0x44cf` requires `ID_USB_INTERFACES` to contain `060101` (PTP/Still-Image) or `ffff00` (vendor-specific). Plain mass-storage-only devices take a different branch that uses `mount(2)`/`umount2(2)`/`mkdir(2)` and no shell. The unsafe MTP sink is real; descriptor-based command injection is blocked downstream by udev sanitization.
- **Corrected sanitizer analysis:** after `util_replace_whitespace` at `0x1c334`, `builtin_usb_id` calls `0x22a00` at `0x1c33e` with `rsi = NULL`. That second function calls the predicate at `0x29d80`, whose built-in allowlist at `0x537c9` is exactly `#+-.:=@_`, in addition to ASCII letters and digits. Other printable bytes become `_`. A literal `\\x` pair can survive, but the shell treats it as an escaped `x`, not a hexadecimal byte escape. The earlier analysis mislabelled `0x22a00` as trimming and therefore reached the wrong security conclusion.
- **Dynamic result:** QEMU `usb-mtp` presented raw serial `a;id>/tmp/v006.id;echo${IFS}V006KMSG>/dev/kmsg;#`; sysfs retained it, while udev emitted `a_id__tmp_v006.id_echo__IFS_V006KMSG__dev_kmsg_#`. The authentic uid-0 automounter stayed alive and reached the MTP `system()` branch, but created no marker and executed no injected command. A broader matrix preserved only `[A-Za-z0-9#+\-.:=@_]` and rewrote separators, substitutions, redirections, quotes, globs and slashes. Logs: `v006-exploit-host.log` SHA-256 `568f3197ff178cbf8356674c74a149b66ec1bfd96eedd5f2098a830c84adb27a`; matrix SHA-256 `de0757442ca4a74d3a3f87db79e8c3eb2b16b101dc47131d266af71ac734b0a1`.
- **Residual impact and preconditions:** physical PTP/MTP access can reach the root shell sink. A leading `#` can truncate the helper command as a comment, so denial of service is plausible. No surviving descriptor sequence found can introduce a new shell word, substitution, redirection or command.
- **Remediation:** remove both `system()` and `popen()`. Launch an absolute path with `execve()`/`posix_spawn()` and a fixed argument vector plus controlled environment. Read `/proc/mounts` directly and compare decoded fields instead of shelling out to `grep`. Derive mount-directory names independently of the raw serial; constrain paths beneath an owned directory and prevent traversal and symlink races. Treat serial validation as defence in depth, never as a substitute for removing the shell. Disable the MTP branch cleanly when the helper is absent. Move descriptor handling and helper execution out of root, retaining only narrowly scoped privileged mount operations.
- **Acceptance / regression:** shell metacharacters, separators, `${IFS}`-style expansion, over-long serials, comma and non-ASCII serials, and a missing helper must all produce no shell interpretation; legitimate PTP and mass-storage mount and unmount must still work; no privileged child of the automounter should exist.
- **Validation boundary:** do not describe V-006 as "USB-to-root" or as an exploitable CWE-78 on `260128`. Re-test other firmware builds because the sanitizer is defence in depth rather than a substitute for removing the shell.

**Decisive re-test of the merged V-006 claim (2026-10-31).** The merged register entry from the external PR
states that root command execution was demonstrated in the QEMU harness using
`ID_SERIAL_SHORT="pwn;id>/tmp/VM-PWNED"` with `ID_USB_INTERFACES=:060101:`. That exact payload was re-run here
through a **real device descriptor** — QEMU `usb-mtp` with `serial=pwn;id>/tmp/VM-PWNED`, which presents the PTP
interface class the branch requires. Measured result:

- Raw descriptor serial as presented to the guest: `pwn;id>/tmp/VM-PWNED` (the payload is intact on the wire).
- Property actually delivered to `usb-automount`: **`ID_SERIAL_SHORT=pwn_id__tmp_VM-PWNED`** — `;`, `>` and `/`
  each rewritten to `_`, consistent with the allow-list recorded below.
- `ID_USB_INTERFACES=:060101:` was present, so the MTP branch condition was satisfied.
- **No marker was created.** `/tmp/VM-PWNED` does not exist after the automounter ran and the add event was
  re-triggered.

Conclusion: the payload is not deliverable to the sink **from a device**. The external result is therefore most
consistently explained by a synthetic event or a directly injected `ID_SERIAL_SHORT`, which bypasses
`builtin_usb_id` and its sanitiser — a property a real USB device cannot produce. Under that reading the
external demonstration is a **harness artefact**, and V-006 remains a latent defect rather than a
device-reachable root path. Both parties agree the source defect (unquoted `sprintf` into `system()`) is real
and must be removed; the disagreement is purely about reachability, and reachability is what severity rests on.

**Runtime amendment (2026-10-29) — the metacharacter pass-through claim above is falsified.**

Dynamic confirmation was attempted in the isolated VM and reached the vulnerable sink without
executing injected code. Three things were established, in order:

1. **Reachability is real.** A QEMU `usb-mtp` device presents `bInterfaceClass=06 SubClass=01
   Protocol=01`, udev records `E:ID_USB_INTERFACES=:060101:`, and the automounter takes the MTP branch,
   emitting `sh: /usr/bin/go-mtpfs: No such file or directory`. That message can only be produced by
   the `system()` call at `0x535f`, so the unquoted `sprintf` path is confirmed reachable at runtime,
   not merely in disassembly.
2. **The delivered property is heavily sanitised.** udev hands over
   `ID_SERIAL_SHORT=a_id__tmp_v006.id_echo__IFS_V006KMSG__dev_kmsg_#` for a submitted
   `a;id>/tmp/v006.id;echo${IFS}V006KMSG>/dev/kmsg;#`. A second sanitiser exists beyond
   `util_replace_whitespace`: an allow-list of alphanumerics plus `#+-.:=@_` is present in
   `lib/systemd/systemd-udevd` and `lib/libudev.so.1.6.4`, and every other printable byte is rewritten
   to `_`. Semicolons, redirects, `$`, backticks, braces and `${IFS}` therefore cannot survive.
3. **The payload itself is sound.** Feeding the identical string directly to the guest's `/bin/sh`
   yields `uid=0(root) gid=0(root)`, so the failure is the property sanitiser, not the payload, the
   guest, or the harness.

**Revised status.** The source defect stands: `sprintf` into `system()` with no quoting, plus `popen`
with a serial-derived string, are genuine CWE-78 patterns and must be removed. But this entry is
**downgraded from "confirmed exploitable-by-construction" to a latent defect that is not exploitable on
260128 through the udev property path**, because the value reaching the sink is reduced to
`[A-Za-z0-9#+-.:=@_]`. It becomes exploitable again under any of: a udev version or rule set without
that allow-list, a path that reads the raw descriptor instead of the property, or a caller that passes
an unsanitised string. Treat the allow-list as accidental defence in depth, not as the fix. The earlier
statement in this register that shell metacharacters "pass through unchanged" is withdrawn.

**Reproduction status (updated 2026-10-30).** QEMU `usb-mtp`, the authentic udev database, system D-Bus and `usb-automount` now run together. `ID_USB_INTERFACES=:060101:` and the missing-`go-mtpfs` shell error prove MTP-branch reachability. The sanitizer—not missing hardware, D-Bus or payload syntax—is the reason command injection does not occur.

## V-007 — Media parsing runs as an unprivileged-separation gap (CONFIRMED configuration, not a demonstrated exploit)

- **Status:** **confirmed configuration, informational.** Root execution of a parser is a risk amplifier rather than a vulnerability by itself. A separate, dynamically reproduced ASF parser defect is now recorded as V-010; this entry remains the privilege-separation finding. Triaged 2026-10-28.
- **Evidence:** `work/vm/vendor-userspace-260128/validation-261028/v007/` (report, component table, evidence excerpts).
- **Observation:** none of the media service units specify `User=` (the only templated unit in the image is `user@.service`). `lightmediascannerd`, `thumbnail_extractor`, `mediamanager`, `playerengine` (GStreamer 1.8.3 with 160 plugins plus libav) and `MediaBrowser` (libmediainfo) are therefore configured for uid 0. No `CapabilityBoundingSet=`, `NoNewPrivileges=` or `SystemCallFilter=` is present, no `libseccomp` exists in the image, and the image contains **zero setuid binaries**. The only confinement is SMACK labelling (`App::mediaplayer`, `App::usbautomount`), which does not change uid.
- **What is not established:** production-hardware runtime uid; that missing unit directives prove the absence of inherited or directly-installed seccomp filtering; automatic V-010 reachability through the production scanner/thumbnail D-Bus workflow; or media-triggered code execution rather than the VM-confirmed crash.
- **Remediation:** run scanners, thumbnail workers, players and their D-Bus activation paths under dedicated non-root accounts; put privileged device and mount management behind a narrow broker; restrict filesystem writes and network access; tighten SMACK rules; apply the hardening this systemd-225 build actually supports; backport parser fixes and fuzz hostile media.
- **Acceptance:** media components run under distinct non-root identities; a parser crash cannot reach privileged state; legitimate playback, indexing and thumbnail generation still work.

## V-008 — Conditional root serial console, password-gated (shipped configuration, not an auth bypass)

- **Status:** **shipped configuration confirmed; status as a vulnerability unresolved.** A password-authenticated root console is normal engineering practice. It is **not** an authentication bypass, and no defective hashing was found. Triaged 2026-10-28.
- **Evidence:** `work/vm/vendor-userspace-260128/validation-261028/v008/` (report plus machine-readable summary with per-file digests).
- **Observation:** `etc/esinit_agetty.sh:6` starts `agetty -8 -L ttyS2 115200 xterm`; the autologin alternative on line 5 is commented out. `etc/securetty` permits `ttyS2`, and `etc/passwd.legacy` gives root `/bin/sh`. `etc/shadow.Global` holds a `$6$` SHA-512-crypt verifier with a unique 10-character salt, no explicit rounds parameter, and no locked marker; the other 18 accounts are locked with `*` or `!`. `lib/systemd/esinit` creates `/tmp/secure_console_disable` and then launches the getty when that file exists, which is fail-open ordering; the MICOM parameter `secure_console=1` would suppress it by removing `/dev/ttyS2`.
- **Latent trust material:** `etc/dropbear/authorized_keys` ships one static `ssh-rsa` key, and the RPM database retains a Dropbear package record, but the recovered product filesystem has no `dropbear`/`dropbearmulti` executable, socket unit, host-key unit/key, or enable link. The socket-fed template is inert. This is dormant configuration, not a backdoor: a public key is not a private key and no reachable SSH service exists. See `evidence/dropbear-activation-and-authentication.md`.
- **What is not established:** that `esinit` executes on a production unit (no unit, generator or init script in the rootfs references it; `sbin/init` is systemd, so an external trigger such as a bootloader `init=` would be required); that `passwd.legacy`/`shadow.Global` are the active databases; that production units ship the console enabled; that the UART is physically exposed; and anything about password strength or per-unit uniqueness.
- **Remediation:** identify the real production boot caller and the active account database first. Disable the serial getty by default in production. Replace the inverted temporary-file gate with an explicit authenticated service-mode decision that defaults to disabled on error or missing state, and do not rely solely on deleting a device node. Remove `ttyS2` root-login permission and lock direct root login where unnecessary, using controlled and auditable maintenance access instead. Remove unused authorized-key material and ensure future SSH enablement cannot silently trust it.
- **Acceptance:** no root login on a production serial line; maintenance access remains auditable; enabling the console requires an explicit authenticated decision that cannot be reached by creating a file; no dormant key material ships.

## V-009 — Password database lives at a volatile, world-facing path (CANDIDATE, unverified)

`/etc/passwd` in `NE_E.EUR.S5W_L.001.001.260128` is a **symlink to `/tmp/passwd`**, confirmed by
inspecting the recovered rootfs; `/etc/group` is a normal file. A fresh boot therefore has no user
database at all until init populates it, which is observable: `dbus-daemon --system` refuses to start
with `Could not get password database information for UID of current process: User "???" unknown`,
and `usb-automount` dies three seconds later as a consequence.

Two distinct concerns, neither demonstrated:

1. **Availability / fail-open reasoning.** Every NSS consumer in the system depends on a file in
   volatile storage being created correctly before it is needed. Anything that reads the user database
   earlier than init's population step sees no users, and services fail in ways their authors did not
   intend.
2. **Potential integrity of authorization inputs.** If `/tmp` is world-writable at runtime on a real
   unit, as is conventional, then an unprivileged process that wins the race to create `/tmp/passwd`
   supplies the user and group database that NSS subsequently answers from. That would let a local
   attacker define or alter identity records consulted by authorization checks, including the
   `messagebus` account this very service relies on.

**Status: candidate.** Not verified: the runtime mode and ownership of `/tmp` on hardware, whether
init recreates the file with restrictive ownership, whether any consumer caches the database before
init runs, and whether a local unprivileged context is reachable at all. Stated as a design hazard
worth checking on real hardware, not as an exploit. Evidence: `work/vm/vendor-userspace-260128/
dbus-automount-findings.md` and the `dbus-automount-probe.py` driver.

## V-010 — Null-pointer dereference in `sbi_apl_commit` wedges the platform bus (DOWNGRADED: bring-up defect, not security)

Loading the vendor module `lge_usb_adapter` on emulated hardware faults immediately:

```
BUG: unable to handle kernel NULL pointer dereference at 000000000000000c
IP: [<ffffffff8105913b>] sbi_apl_commit+0x60/0x2bc
```

`/etc/esinit-modprobe.sh` runs that load during init, and the process is killed. The fault occurs while
holding the platform `device` lock, which is then orphaned: the next platform driver to register
(`lge_fan_init`, reached via `/sbin/modprobe fan`) blocks indefinitely in state `D` inside
`__driver_attach`, and the system stops one line short of starting systemd. The hung-task detector is
compiled out, so the stall produces no diagnostic.

**Impact as observed:** a denial of service against boot, triggered by an in-tree module load rather
than by attacker input, so it is a robustness defect first. Severity is not scored: reaching it
requires the ability to load a module, which already implies privileged context.

**Why it is in the register anyway:** `sbi_apl_commit` reaches a null pointer at offset `0x0c` through
sideband access paths, and the argument that matters is whether any of the reachable paths can be
influenced by unprivileged input or by device-supplied data. If they can, this is an arbitrary
null-dereference or worse in a driver that runs before the HMI; if they cannot, it is a
bring-up defect. That question is open.

**Status: downgraded 2026-10-29.** Follow-up analysis resolved the open question in the negative: the faulting pointer is the global `0xffffffff81bd5460`, assigned only from `dev.platform_data` at `0x810594c2`, and no attacker-reachable path to it was found. The driver asserts hardware presence that emulation does not provide, so this is a bring-up defect and an illustration that the driver trusts platform data. Kept in the register for that lesson, not as a finding. Evidence: `evidence/vm-bringup/esinit-bringup-findings.md`.

## V-011 — Automounted Tuxera NTFS omits `nodev` (HARDENING GAP; DEVICE INTERPRETATION CONFIRMED)

- **Status:** the flag omission and exact Tuxera NTFS special-file behavior are now confirmed. A disposable NTFS image retained an inert character node across unmount/remount; without `nodev`, uid/gid 65534 opened it read-only, while the same open was denied with `nodev`. This remains a post-execution/DAC-bypass primitive, not a demonstrated first-step root path.
- **Where:** `/app/bin/usb-automount`, mass-storage mounts at `0x4d70`/`0x4df1`. Flag words `0xC0ED000A` and `0xC0ED000B` contain `MS_NOSUID | MS_NOEXEC` (plus read-only on retry) but omit `MS_NODEV` (`0x4`). There is no positive `MS_DEV` flag; device interpretation is enabled by omission of `nodev`.
- **Filesystem constraint:** the function constructs only vendor driver names `tntfs` and `texfat` for NTFS/exFAT. FAT/exFAT do not natively carry POSIX device inodes. Exact Tuxera NTFS `3016.7.1.2.3`, however, accepted an NTFS 3.1 control, created `inert-null` as character device `1:3`, and reproduced it as `root:root` mode `0755` after remount. The representation was generated by this same Tuxera driver; portability to arbitrary third-party NTFS authoring tools is not yet claimed.
- **Harmless dynamic control:** the no-`nodev` mount showed the character type and `1:3`, and a process reduced to numeric uid/gid 65534 with SMACK label `_` opened it read-only (`dd` rc 0). The `ro,nodev,nosuid,noexec` control retained the inode metadata but denied the open (`Permission denied`, rc 1). The target was QEMU `/dev/null`; no eMMC or sensitive emulated device was accessed.
- **Impact boundary:** a crafted NTFS volume can therefore activate VFS device semantics on this driver when `nodev` is omitted. A device node does not execute itself. Production impact still requires a local process that can reach the mount and a useful major/minor plus access mode; application-specific SMACK domains, mounted-path permissions, useful write access, and any root consequence remain unverified.
- **Evidence:** clean NTFS image SHA-256 `220ad1d065856ae49d971c5d014ab527aca36aa1367f9e8709ceb9d446295cde`; clean read-only mount log SHA-256 `e9d19e192700398c00b2fd083cc39fea726b8170ca0d5eb5e81f2a85ee17d036`; special-file log SHA-256 `4d68550b5cb8420622e25cdfd35ccb9fee194b48fb16f946090607c3f784a494`; numeric-uid control log SHA-256 `8c41d9025183781ade987cd688d4724d48d6964cb876492004649803eb2403f3`.
- **Remediation:** add `MS_NODEV` while retaining `nosuid,noexec`; isolate removable mounts in a namespace and expose only ordinary files to unprivileged media workers.

## V-012 — GStreamer ASF >32-stream object overwrite (VM-CONFIRMED SERVICE CRASH; RCE UNPROVEN)

- **Status:** CVE-2026-2920's affected path is dynamically reached in the recovered `260128` userspace through both authentic `gst-discoverer-1.0` and the authentic uid-0 PlayerEngine D-Bus service. A 32-stream boundary control survives; 33- and 34-stream files terminate PlayerEngine with signal 11. Exact static analysis also establishes an explicit `MediaBrowser requestThumbnails(as) → thumbnail_extractor Start(as) → VideoContext → uridecodebin` route eligible to select the shipped ASF plugin. Arbitrary code execution is **not** demonstrated. Automatic scan/UI invocation, dynamic thumbnail-parser reachability, and installed-device applicability remain unverified.
- **Component:** `/usr/lib/gstreamer-1.0/libgstasf.so`, SHA-256 `05e887731708f0b0a52ff9fc75767a00fda9984e422983e5ff1d672f4b1af45d`, GStreamer ABI `1.8.3`. PlayerEngine library SHA-256: `28987e1accfa7a7d04557b3d81dab7f8cd2aabb84a9c5aab7e1c8c4bc85510a0`. The firmware predates upstream's 11 February 2026 fix.
- **Mechanism:** `GstASFDemux` has `stream[32]`. The affected parser accepts stream 33 and creates `audio_32`. Exact vendor instructions show a 208-byte stream stride, array base `GstASFDemux+0x1a8`, `flowcombiner` at `+0x1bb0`, and `old_stream[0]` at `+0x1bb8`. The 33rd stream's vendor-only field store at plugin `0x990d` zeros the low 32 bits of `flowcombiner`; this corrects the earlier public-source-only 200-byte/pad-pointer-transplant interpretation.
- **Direct dynamic proof:** a bounded probe duplicated one valid WMA Stream Properties object to IDs 1–33. Authentic `gst-discoverer-1.0` logged `Found stream 33`, created its pad, continued into the data object, and exited `139`; the kernel recorded `asfdemux0:sink[...] segfault at e00000000 ... in libglib-2.0.so.0.4400.1`. Probe SHA-256: `9c5aaa1f7ad2a4e8526066f6f22e2b3737b912de93f94ab1aa858e3a9ec32518`; direct host-log SHA-256: `b98b05560207193831fe1d47ed8cc093d5ffcc46b48e2b1c0e23c4ee22da6225`.
- **PlayerEngine proof:** the accepted option is `{"option":{"mediatype":"audio"}}`, not the earlier flat JSON. Stock `alsasink`/`media_mixer` fails only because QEMU has no soundcard. A VM-only `/etc/asound.conf` mapping `pcm.media_mixer` to ALSA `type null` preserves the stock factory/device contract. With `file:///tmp/input.wma`, valid one-stream and 32-stream controls return `true` and survive; 33- and 34-stream inputs return `true`, reach the vulnerable range, then die. The 33-stream signal backtrace is `g_queue_push_head+0x1d <- libgstasf.so+0xb6cc <- libgstasf.so+0x1305d`. Exact code at `0xb6c0..0xb6c7` loads the corrupted `flowcombiner` and calls `gst_flow_combiner_add_pad`.
- **URI control:** under the corrected nested option and working ALSA-null environment, `file:///tmp/input.wma` succeeds while plain `/tmp/input.wma` returns `false`. This supersedes the old comparison confounded by a flat option and unavailable sink.
- **Impact boundary:** NVD/ZDI classify the generic defect as potential remote code execution in the current process. Here, root-context parser memory corruption and process death are proven. No attacker-selected pointer, instruction-pointer control, shell, persistence, SMACK bypass, CAN access, or safety-system impact was obtained. The ALSA-null mapping is a VM compatibility shim, not evidence about production hardware.
- **Automatic reachability boundary:** LightMediaScanner startup scanning of `/media/usb` is confirmed, but it uses its own direct-I/O `asf.so` metadata plugin (SHA-256 `f4b42a8eacb73990d35439e27513c28f1d31257488d0c130e6e1a936cb9bb219`) with no GStreamer dependency. It processed the 33-stream file with zero reported errors and remained alive; a full session-bus capture showed no PlayerEngine or thumbnail call. The thumbnail route is statically explicit but client-request driven: reviewed scan callbacks do not call it, and bounded VM attempts did not deliver `Start` or map `libgstasf`. Manual PlayerEngine D-Bus invocation remains the only dynamically proven production-service route.
- **Tooling:** `tools/uk_fw/asf_stream_probe.py` safely duplicates one valid ASF stream object, updates header/file sizes, and audits the upstream rejection marker. It refuses malformed templates, in-place overwrite and stream counts outside `1..127`. Generated files carry no command payload or shellcode.
- **Remediation:** backport upstream `37d7991168a223d0810fd1f4493ec6a8b6a510d3` for both audio and video stream objects; reject `num_streams >= G_N_ELEMENTS(demux->stream)` before any pad or stream state is created. Run media parsing under a dedicated unprivileged, sandboxed worker. Disable ASF parsing if the format is not required.
- **Acceptance:** 32-stream positive control parses as before; 33+ streams fail cleanly before pad creation; malformed/repeated headers do not crash; production thumbnail, scanner and playback paths are tested under non-root identities.
- **Evidence:** `evidence/gstreamer-cve-2026-2920.md`; reviewed excerpts `evidence/artifacts/media-candidates/playerengine-asf-service-evidence.txt` and `evidence/artifacts/media-candidates/thumbnail-extractor-asf-route-evidence.txt`. PlayerEngine 32-/33-/34-stream log SHA-256 values: `949d069052de525f24b4a2995b06d62ee4592cbcce3dcdd4a2a8cc9329799b36`, `16ff6f1241899846ccbfb3d9bae54a5f50994543c07a044625b846f19e598993`, `eee3b52e2ef458d67638b2bbf6f7e99d8ac2824bc3347411957e5001f0895908`.

## V-013 — ALSA sequencer port-creation race (EXACT PRE-FIX CODE; ENTRY POINT REACHABLE)

- **Status:** CVE-2017-15265's pre-fix lifetime logic is present in the exact shipped module. A benign offline VM diagnostic confirmed that numeric uid/gid 65534 can open `/dev/snd/seq` and complete one client-ID, create-port, and delete-port sequence under the recovered `root:root 0644` DAC mode. No use-after-free, root transition, or code execution was observed.
- **Component:** `/lib/modules/4.1.27-abl/kernel/sound/core/seq/snd-seq.ko`, SHA-256 `ccc802452bb4ac4527d2def96ddef463211c03ae2c07d9003fdc7ebed9eb091d`; `CONFIG_SND_SEQUENCER=m`; aliases `devname:snd/seq` and `char-major-116-1`.
- **Mechanism:** shipped `snd_seq_create_port` publishes the new port without the use-lock reference added by upstream fix `71105998845fb012937332fe2e806d443c09e026`. Shipped `snd_seq_ioctl_create_port` consequently lacks both matching unlock paths. Another caller sharing the client can delete the port before later create-ioctl dereferences.
- **Dynamic reachability:** the tracked diagnostic contains no race, fork/clone, heap grooming, payload, or privilege operation. It produced `ALSA_SEQ_OPEN_OK`, `ALSA_SEQ_CLIENT_ID_OK`, `ALSA_SEQ_CREATE_PORT_OK`, `ALSA_SEQ_DELETE_PORT_OK`, and `ALSA_SEQ_UNPRIV_RC=0`. Probe SHA-256: `f12c99be0fd854d5ef7d1402c9ffd2292afe74a1a7b138d4c71d84735c42e5b1`; tool host-log SHA-256: `1f8d3dc1d29534945f9de21f02cbc8dbfb0f7a83307829a6c4ec11568ce4b23f`.
- **Negative control:** a bounded disposable race made 200,000 create and 400,000 delete attempts and completed without a kernel fault. This does not negate the missing lifetime guard, but it means no dynamic UAF is claimed. Race host-log SHA-256: `605a284973e62dfe0acb9ce8e5ff58af371313bec942ed98f1eee52d2474feb4`.
- **Impact boundary:** this is a local kernel memory-safety and denial-of-service surface and a conditional post-execution escalation candidate. The VM modeled the recovered DAC rule but does not prove access from every production SMACK domain. No controlled object reuse, arbitrary read/write, instruction-pointer control, or root path is demonstrated; installed-device firmware remains unknown.
- **Tooling:** `tools/uk_fw/alsa_seq_probe.py` builds, hash-verifies, transfers, and runs the single-create/delete diagnostic in the offline snapshot-backed VM. Source: `tools/uk_fw/guest/alsa_seq_reachability.S`; tests: `tests/test_alsa_seq_probe.py`.
- **Remediation:** backport upstream `71105998845fb012937332fe2e806d443c09e026`; remove or restrict the static sequencer node if untrusted applications do not require it; apply least-privilege DAC and SMACK policy.
- **Evidence:** `evidence/alsa-sequencer-cve-2017-15265.md`.

## V-014 — systemd/udev hardware-property injection reaches an installed root-shell unit (EXACT PRE-FIX CODE; SYNTHETIC BENIGN ACTIVATION CONFIRMED; PHYSICAL PATH UNTESTED)

- **Status:** exact CVE-2026-40225 pre-fix instructions and the installed rule/service chain are present in recovered EU `260128`. Fixed benign offline diagnostics confirmed both leading-space second-property retention and a matched synthetic `systemd-udevd` → PID 1 systemd activation: the positive run started only an otherwise-unreferenced transient marker unit, while the negative run did not. This remains the strongest static malicious-device-to-conditional-root-console path; physical hardware, shipped vulnerable helper execution, the installed shell unit, and the owner's unknown build remain untested.
- **Components:** `systemd-udevd` SHA-256 `f32f6296ea20d959ac046ae80724f39e317aaaf492a5c7eedd9270b5b2abab0d`; `v4l_id` `afb756b457284578c29960d4abd57f9612020fb45a14fbc285f5061da90a7125`; `scsi_id` `85aa83a73d44f19f6b60162a53ee896854b71e7882848819aad20c1ccf079b32`. Version evidence is mixed: the compiled PID 1 banner/pkg-config report `225`, while embedded OpenEmbedded source/recipe paths say `systemd/1_249.3-r0`. Neither banner is the vulnerability premise; exact instructions are.
- **Exact pre-fix code:** after `VIDIOC_QUERYCAP`, shipped `v4l_id` passes `v2cap.card` directly to `ID_V4L_PRODUCT=%s` at `0x14e5..0x14f8`. Shipped `scsi_id` passes `unit_serial_number` directly to `ID_SCSI_SERIAL=%s` at `0x273c..0x275b`. Neither path calls the UTF-8/control-character checks introduced by fixes `16325b35fa6ecb25f66534a562583ce3b96d52f3` and `54f880b02ecf7362e630ffc885d1466df6ee6820`.
- **Installed chain:** `60-persistent-v4l.rules` imports `v4l_id`; `50-udev-default.rules` executes nonempty `REMOVE_CMD` on removal. `60-persistent-storage.rules` imports `scsi_id` for `sd*`/`sr*`; `99-systemd.rules` tags block devices for systemd. The image ships `debug-shell.service`, with no `User=`, configured to run `/bin/sh` on `/dev/tty9` only when `ConditionPathExists=/dev/tty9` passes. Its preset disables default enablement but not an explicit unit request. The recovered kernel has `CONFIG_VT=y`, `CONFIG_VT_CONSOLE=y`, `CONFIG_USB_HID=m`, and `CONFIG_HID_GENERIC=m`.
- **Strongest path:** the upstream advisory states that a malicious SCSI serial can introduce `SYSTEMD_WANTS`. In this image that property can name the already-installed `debug-shell.service`; no attacker-written service file is required. The parser control retained the fixed benign second property. A second matched control used exact udevd and PID 1 systemd: only the positive synthetic property started the transient BusyBox marker unit, and the negative run kept it inactive. A separate control confirmed `/dev/tty9` exists as `root:root` mode `0600`, character device `4:9`. Hardware bytes reaching shipped `scsi_id`, a request for the installed shell unit, production-node existence, virtual-terminal selection, visible output, and keyboard interaction remain untested.
- **Relation to V-006:** V-006 remains blocked. Its `usb_id` `ID_SERIAL_SHORT` allowlist is not used here. V-014 crosses separate `v4l_id`/`scsi_id` line-oriented property boundaries that exact shipped instructions leave unsanitized.
- **Impact boundary:** a VM-only synthetic add event and benign transient unit request were demonstrated. No malicious USB device, hardware-controlled helper output, physical port, installed shell-unit request, observed root transition, interactive command, persistence, network path, CAN access, or safety impact was demonstrated. The V4L route also depends on choosing a useful existing executable and was not validated dynamically.
- **Remediation:** backport both upstream control-character validation fixes; remove `debug-shell.service` from production rather than merely leaving it disabled; allowlist hardware-originated `SYSTEMD_WANTS`; remove generic `REMOVE_CMD` execution; disable unnecessary V4L/SCSI/USB classes.
- **Evidence:** `evidence/systemd-udev-cve-2026-40225.md`; reviewed excerpts under `evidence/artifacts/udev-candidates/`.

## V-015 — ConnMan DHCPv6 DOMAIN_LIST stack overwrite (EXACT PRE-FIX CODE; CONDITIONAL ON-LINK ROUTE STATICALLY CONFIRMED)

- **Status:** the exact shipped `connmand` contains CVE-2026-115863's affected `get_domains` implementation, exact DHCPv6 option-24 dispatch, and the conditional Router Advertisement Managed/Other path that starts DHCPv6 on a connected managed network. No packet was sent, no dynamic crash occurred, and code execution/root access are not claimed.
- **Component:** `/usr/sbin/connmand`, SHA-256 `d82d4018bfa9d8f8d67407453bd783a3c896f6764f147dcf23cf06b978024c28`; recovered package-index record `connman-1.29+5w.master.38-r1.corei7_64`. The installed unit has no `User=` directive, so it uses the uid-0 system-service default, and has `Restart=on-failure`.
- **Mechanism:** `connmand+0x1f150` calls `strncpy` with fixed length `0x401`, then replaces each DNS-label byte with `'.'` and advances by that byte plus one without comparing the cursor to the option or local-buffer end. The caller beginning at `+0x1f211` tests bit 24 (`0x1000000`) and dispatches DOMAIN_LIST data to this function.
- **Static route:** the exact callback at `+0x574e0` requires a connected network, then routes RA Managed and Other flags to stateful DHCPv6 (`+0x856f0`) or information-request (`+0x855a0`). The latter's routine at `+0x84770` explicitly registers option 24. The service excludes many interfaces but not intended `wlan0`. A reply must still match the live transaction ID, CLIENTID/DUID, SERVERID, message type, and state.
- **Mitigations/impact boundary:** the exact ELF is PIE with a non-executable stack, stack canaries, and full RELRO. Those protections constrain straightforward execution but do not prevent the parser's out-of-bounds accesses. At present, a conditional root-daemon crash is the defensible impact; no stable disclosure/write primitive, instruction-pointer control, shell, persistence, or safety impact was demonstrated. Production Wi-Fi/IPv6 state and the owner's installed build remain unknown.
- **Remediation:** replace the parser with a strictly length-aware DNS-label decoder; reject cursor/label/expanded-name overflow and missing termination; update ConnMan when the upstream fix is available; disable unneeded DHCPv6; reduce daemon privilege; retain restart-rate and crash diagnostics.
- **Evidence:** `evidence/connman-cve-2026-115863.md`; reviewed excerpt `evidence/artifacts/network-candidates/connman-cve-2026-115863-static-evidence.txt`; deterministic RPM dump parser `tools/uk_fw/rpm_nvra_inventory.py`.

## V-016 — ConnMan DHCPv4 total-length underflow (EXACT PRE-FIX ORDER; FORTIFY BLOCKS THE STACK COPY)

- **Status:** the exact shipped `connmand` retains CVE-2023-28488's pre-fix ordering and reaches the affected L2 callback through ordinary IPv4 `INIT_SELECTING`. Exact `_FORTIFY_SOURCE` output changes the reviewed outcome: no oversized stack copy occurs because `__memcpy_chk` reaches `__chk_fail` first. No packet was generated and no dynamic abort occurred.
- **Component:** `/usr/sbin/connmand`, SHA-256 `d82d4018bfa9d8f8d67407453bd783a3c896f6764f147dcf23cf06b978024c28`, with `/lib/libc-2.25.so`, SHA-256 `04946077dfd7554a20438ee581367e3995931b26c9ee516ffeeecdc0ee9f331f`.
- **Mechanism:** the receiver requires the original read to contain 28 IPv4+UDP header bytes, replaces that count with untrusted 16-bit `ip.tot_len`, rejects only totals greater than the read, then computes `size_t(ip.tot_len - 28)`. The exact call supplies a 628-byte destination size to `__memcpy_chk`.
- **Static route:** normal IPv4 startup sets state `INIT_SELECTING`, selects listening mode 1, creates an `AF_PACKET` datagram socket, binds it to the interface/IPv4 protocol, and registers the affected callback. Runtime exposure still requires a ConnMan-managed interface to be acquiring an IPv4 lease and a frame to pass protocol, header, port/length, and checksum checks.
- **Mitigations/impact boundary:** all totals below 28 produce a 64-bit underflow larger than 628. Every exact libc checked-copy implementation reviewed branches to non-returning `__chk_fail`/`__fortify_fail` before copying. Totals 28..656 copy at most 628 bytes, while larger totals are rejected. Conditional unauthenticated daemon termination is statically plausible; a stack overwrite, RCE, root access, persistence, and applicability to the owner's installed build are not established. `Restart=on-failure` limits but does not eliminate availability impact.
- **Remediation:** backport upstream `99e2c16ea1cced34a5dc450d76287a1c3e762138`; retain fortification but do not use a fatal bound check as the parser fix; reduce daemon privilege and rate-limit/review restart failures.
- **Evidence:** `evidence/connman-cve-2023-28488.md`; reviewed excerpt `evidence/artifacts/network-candidates/connman-cve-2023-28488-fortify-evidence.txt`; packet-free arithmetic model `tools/uk_fw/connman_length_model.py`.

## V-017 — oFono SMS TPDU decoder overflows (EXACT PRE-FIX CODE; DIRECTIONAL ROUTES STATICALLY CONFIRMED)

- **Status:** the exact shipped `ofonod` retains missing destination checks for CVE-2023-4232 through CVE-2023-4235, CVE-2023-2794, and CVE-2024-7547. No modem input, target execution, dynamic crash, controlled execution, or root transition occurred.
- **Component:** `/usr/sbin/ofonod`, SHA-256 `3f6daee7c2ccd4b4e222c73d3d22478a997ec336e8a9d65042805625d987ac32`, Build ID `f596c565c77e4abb24d6b5b516ffb2bd6110b1ee`, package `ofono-0.6.8+5w.master.199-r1.corei7_64`. The embedded vendor path identifies `drivers/lgeqmimodem/sms.c`.
- **Exact incoming route and directionality:** QMI calls at `0x4a8d6` and `0x4a9e7` reach `ofono_sms_deliver_notify`; `0xa55ee` calls `sms_decode(..., FALSE, ...)` at `0xae8a0`. Incoming TP-MTI selects deliver, submit-report, or status-report decoding before `0xa55fb..0xa5601` rejects any returned type other than DELIVER. This route therefore reaches CVE-2023-4233/CVE-2023-2794, CVE-2023-4234, and CVE-2023-4232 before the late check.
- **Exact incoming writes:** the address decoder at `0xada70` can write 257 bytes to a 23-byte array; deliver `memcpy` at `0xaddb0` can copy 255 bytes to 140 bytes; status-report `memcpy` at `0xaeb1d` can copy 255 bytes to 143 bytes; submit-report `memcpy` at `0xaec48` can copy 255 bytes to 152-/151-byte ACK/ERROR arrays. Their maxima end 21, 64, 83, and 22 bytes beyond the `0x128`-byte `sms` object, respectively.
- **Outgoing-only writes and callers:** CVE-2023-4235 remains pre-fix at decoder `0xaeea8`, with maxima ending three/four bytes beyond `sms`; CVE-2024-7547 remains pre-fix at `0xaeda0`, with a maximum command copy ending 48 bytes beyond `sms`. They cannot be selected by the incoming QMI call. Exact `outgoing=TRUE` callers exist at `0xb1953` for local transmit-queue deserialization and `0xd8cbb` for SIM-Toolkit Send SMS parsing; the latter checks SUBMIT/COMMAND only after decoding.
- **Mitigations/impact boundary:** the ELF is PIE with NX stack, full RELRO/BIND_NOW, and stack canaries. In the incoming delivery caller, `sms` begins at `rsp+0x30`, later scratch at `rsp+0x160`, and the canary at `rsp+0x1f8`; none of the incoming decoder maxima directly reaches that canary. Outgoing-only caller frames have not yet been reconstructed, so their object-relative overruns must not be projected onto this layout. Exact corruption does not establish instruction-pointer control or RCE.
- **Activation/privilege boundary:** `ofono.service` has no `User=` and would run as uid 0, gated by `/tmp/telematics_code_TELEMATICS`; `ofono.path` additionally watches `/tmp/no_isa`. No recovered enable link for `ofono.path` was identified. `smack-relabel-ro.sh` assigns `App::tms`. Owner-vehicle activation, installed hashes, modem/QMI state, byte preservation, malicious SIM/STK or local queue input, direct radio reachability of outgoing decoders, and unrestricted root remain unknown.
- **Remediation:** backport `1a5fbefa59465bec80425add562bdb1d36ec8e23`, `a90421d8e45d63b304dc010baba24633e7869682`, `5209fd65ff41653d7725e407ccc359c54bb3121f`, `2ff2da7ac374a790f8b2a0216bcb4e3126498225`, `8d74bc66146ea78620d140640a0a57af86fc8936`, `02aa0f9bad3d9e47a152fc045d0f51874d901d7e`, and `305df050d02aea8532f7625d6642685aa530f9b0`; isolate modem-controlled parsing from uid 0; narrow `App::tms`; add sanitizer-backed boundary tests.
- **Evidence:** `evidence/ofono-sms-decoder-cves.md`; reviewed excerpt `evidence/artifacts/network-candidates/ofono-sms-decoder-evidence.txt`; message-free model `tools/uk_fw/ofono_sms_bounds_model.py`.

## V-018 — oFono QMI WMS message-list bounds (EXACT PRE-FIX CODE; MODEM TRUST BOUNDARY)

- **Status:** the exact vendor QMI callback retains CVE-2024-7537's missing equality check between returned TLV length and `4 + count*5`. It supplies a 16-bit length-output pointer to the accessor but never reads that output afterward. No QMI message, modem input, target execution, dynamic crash, or root transition occurred.
- **Exact mechanism:** around `0x48d61..0x48d6c`, the callback computes `count*5` modulo `2^32`. A small product allocates `4 + product` at `0x48d78..0x48d7c`; the overflow diagnostic at `0x48e40` falls through to the same call with a four-byte allocation rather than rejecting. The original 32-bit count controls the loop at `0x48da0..0x48db6`. Every count above 13,107—4,294,954,188 values—under-allocates; short lengths overread the selected TLV and can proceed beyond the backing QMI result.
- **Boundary:** this is a modem-supplied QMI WMS result, not ordinary incoming TPDU decoding. A defective or compromised modem is the established precondition; direct SMS/base-station control is unproven. The conditional process is uid 0 under `App::tms`, not demonstrated unrestricted root.
- **Remediation:** backport `e6d8d526d5077c0b6ab459efeb6b882c28e0fdeb`; use checked `size_t` multiplication/addition; reject short or mismatched TLVs before allocation or iteration; cap count; test with mocked QMI results under sanitizers.
- **Evidence:** `evidence/ofono-qmi-message-list-cve-2024-7537.md`; reviewed excerpt `evidence/artifacts/network-candidates/ofono-qmi-list-evidence.txt`; message-free model `tools/uk_fw/ofono_qmi_list_bounds_model.py`.

## V-019 — Broadcom BSA BNEP control-packet bounds (EXACT PRE-FIX CODE IN BOTH PCB VARIANTS; RADIO ROUTE CONDITIONAL)

- **Status:** both PCB-selectable `vbtd` binaries retain CVE-2017-0782's pre-fix `bnep_process_control_packet()` field reads. The Bluetooth service is enabled and BNEP/PAN code is linked, but no adapter, radio, packet, pairing, connection, crash, disclosure, or controlled execution was used.
- **Components:** `vbtd-51`, SHA-256 `55e21d077082e97f56fb113a1d3b216c0f2e63aa02fc4cd754a6593bc6cec9e0`, Build ID `12175aa88ccff70cc56498e0208c9a51aac0c9e9`, `BSA0107_00.51.00`; `vbtd-63`, SHA-256 `c56b68fdd35b16b95688ab54a48ffb9f18034d925c057e86f8b9fe304f8b26b9`, Build ID `04141ed222ee8f150c0eb0e46fdb73624d168920`, `BSA0107_00.63.00`. PCB 11/12 selects `vbtd-63`; other values select `vbtd-51`.
- **Exact mechanism:** in `vbtd-51`, the exported parser at `0x8c5020` reads the extended packet's first and second bytes at `0x8c5056` and `0x8c5062` after subtracting lengths but before its first wrap comparison at `0x8c507c`; the non-extended path also reaches `0x8c5062` without a one-byte bound. Later field reads at `0x8c5130`/`0x8c5139` retain the same pre-fix structure. `vbtd-63` matches at parser `0x8c7480`, reads `0x8c74b6`/`0x8c74c2`, first compares only at `0x8c74dc`, and retains later reads at `0x8c7590`/`0x8c7599`. These are the missing pre-read checks added by upstream `1b08775917413f1674882130a948add1ae44cc91`, with related bulletin fixes `4e47f3db62bab524946c46efe04ed6a2b896b150` and `c568fa9088ded964e0ac99db236e612de5d82177`.
- **Activation/privilege boundary:** `vbtd.service` is enabled by `multi-user.target`, has no `User=`/`Group=`, and restarts always; it has a configured uid-0 default, while recovered relabel policy intends `App::bluetooth` if it starts. Mandatory `/tmp/session_appmgr.env` is a runtime gate. Setup chooses a PCB-specific controller patchram and binary, then the service uses `/dev/ttyS0`.
- **Reachability boundary:** both engineering profile files say `PAN : N/A`; startup calls `BNEP_Init`, but bounded reference review found no direct call to exported `BNEP_Register`. This does not exclude indirect/runtime registration, but V-019 is dormant pending BNEP PSM/profile evidence. A live route would additionally require an ACL link and accepted L2CAP BNEP/PAN channel. Adapter state, pairing/bonding, authorization, controller preservation, selected PCB, installed owner hash, and restart behavior are unknown.
- **Impact boundary:** reads beyond the parser's declared packet/remaining-length boundary and 16-bit underflow are established. They may remain within backing GKI allocation slack. The Android bulletin's generic critical-RCE classification is not reproduced here. No allocation-bound OOB read, process crash, disclosure contents, overwrite, instruction-pointer control, shell, SMACK escape, unrestricted root, persistence, CAN access, or safety impact is demonstrated.
- **Remediation:** apply all three bulletin-linked CVE-2017-0782 fixes to both BSA variants; exact evidence directly proves the missing field-by-field parser checks, not independent absence of every mechanism in the other two commits. Disable unused PAN/BNEP, require authenticated/authorized channels, reduce privilege/narrow `App::bluetooth`, and regression-test both branches with sanitizer-backed boundary fixtures.
- **Evidence:** `evidence/broadcom-bsa-bluetooth-cves.md`; reviewed excerpt `evidence/artifacts/network-candidates/vbtd-cve-2017-0782-bnep-evidence.txt`.

## V-020 — BusyBox CVE-2015-9261 before USB-update member authentication (EXACT PRE-FIX CODE; STATIC USB PATH CONFIRMED; PHYSICAL ROUTE CONDITIONAL)

- **Status:** exact affected method-8 code and AppScomoDM's pre-authentication USB extraction order are present in recovered EU `260128`. No ZIP/DEFLATE stream, update package, target execution, crash, memory write, code execution, root transition, or signature bypass was produced.
- **Components/provenance:** stock `/bin/busybox`, SHA-256 `95bab633630fb158344497af52dc112e9e777458b810860068d4daa257bd9ebc`, two GNU Build ID notes `42e0a4c7631667cf9106ca36a4f2e7886f6f72b0` and `dc25533aa5ad984ec9a7ed388925f24d328c1836`, banner `BusyBox v1.23.2`; `/app/bin/AppScomoDM`, SHA-256 `c44da21eb39987e88d71c648f625338722b8458f0ff8ecfe29e3321cf6d62046`, Build ID `496a47fae4cca227723b1f4037be918cae18473c`. The current `extracted-safe/.../bin/busybox` is a VM-injected 1.35.0 helper, not stock; canonical stock bytes come from the independent original extraction. Original `/usr/bin/unzip` points to `/bin/busybox`.
- **Pre-authentication route:** `AppScomoDM::launchAppUpgrade` examines one first iterator result matching `S5W_SYSTEM_*_*_*.zip` and executes `unzip -o <archive> -d /update/usb/temp AppUpgrade .lge.upgrade.xml` at `0xbfaf2`. Only afterward does it call public-key-backed verifier wrapper `0x28580` for both extracted files at `0xbfe82` and `0xbfebc`; both results must be zero. Thus DEFLATE parsing precedes member authentication. A separate FOTA route uses `/usr/bin/unzip64` and is not assigned this finding.
- **Exact method route:** stock `unzip` at `0x45da8..0x45dbe` accepts only methods 0 and 8 and explicitly rejects method 12. Method 8 reaches `inflate_block` and dynamic `huft_build` calls at `0x47f01`, `0x48052`, and `0x48097`.
- **Exact CVE mechanism:** `huft_build` initializes only the nonzero-code-length prefix of stack-local `v[]`, but exact code computes/stores `v+n` at `0x475d1..0x475e0`, compares the cursor against that bound at `0x4788a`, and can read an uninitialized slot at `0x47938`. An indeterminate value at least `s` reaches indexed extra/base table reads at `0x47970`/`0x47974`. Initial fix `1de25a6e87e0e627aa34298105a3d17c60a1f44e` introduced a `v_end` bound; corrective follow-up `6bd3fff51aa74e2ee2d87887b12182a3b09792ef` replaced it with initialized `UINT_MAX` sentinels after breakage. Neither correction is present.
- **Impact boundary:** the strongest supported outcome is a likely `unzip` child segmentation fault and update denial of service. The uninitialized stack value is not claimed attacker-selected. No target crash, memory write, instruction-pointer control, AppScomoDM compromise, RCE, SMACK escape, unrestricted root, persistence, package acceptance, partition write, slot switch, boot-trust effect, or owner applicability is established.
- **Privilege/runtime boundary:** `ApplicationLauncher.service` has no `User=` and starts AppLauncher in the uid-0 system-service context; relabel policy intends AppScomoDM `App::upgrade`. Runtime uid/label, selected `-un` route, effective `PATH`, and physical discovery remain unobserved.
- **Hardening:** stock BusyBox is PIE/`ET_DYN`, has NX stack, full RELRO/BIND_NOW, fortified imports, and a canary in `huft_build`. The initial flaw is an uninitialized read within the frame and later direct indexed reads, so these mitigations do not prevent a child crash.
- **Tooling:** `tools/uk_fw/busybox_huft_bounds_model.py` compares recovered `p<n` with a conceptual populated prefix and the stable follow-up's initialized-sentinel behavior using numeric states only; it does not model the short-lived `v_end` implementation and emits no archive, compressed stream, packet, command, or payload. Tests: `tests/test_busybox_huft_bounds_model.py`.
- **Remediation:** backport both `1de25a6e87e0e627aa34298105a3d17c60a1f44e` and corrective follow-up `6bd3fff51aa74e2ee2d87887b12182a3b09792ef`, or use a maintained inflater; authenticate member digests before decompression; isolate extraction as non-root; invoke an absolute maintained extractor and check its complete exit status; use fresh transactional outputs; retain malformed regression fixtures only in a controlled sanitizer/vendor environment.
- **Evidence:** `evidence/busybox-unzip-cve-2015-9261.md`; reviewed excerpt `evidence/artifacts/update-candidates/busybox-unzip-cve-2015-9261-evidence.txt`.

## V-021 — ALSA timer event padding disclosure (EXACT PARTIAL BACKPORT; RUNTIME EVENT ROUTE UNOBSERVED)

- **Status:** exact `snd-timer.ko` fixes the CVE-2016-4569 early-event record and the CVE-2016-4578 general callback, but its timer-interrupt callback retains both uninitialized four-byte ABI padding regions. No module, device, ioctl, timer, event, read, target bytes, or disclosure was exercised.
- **Component:** SHA-256 `3b2fa4e722ff210c2643089b2035a4ba93134ad1624e0c520bafa6debac46a91`, Build ID `42457bdb4c6cd4911a707afac6912e23d735b68a`, x86-64 `ET_REL`; `.text` file offset `0x64`, size `0x2d44`.
- **Exact mechanism:** `snd_timer_user_tinterrupt` `[0xcc3,0xe43)` clears only a separate 16-byte timestamp at `[rbp-0x68]`. Its 32-byte record starts at `[rbp-0x58]`; resolution and tick branches write named fields but not padding bytes `4..7` or `28..31`. `snd_timer_user_append_to_tqueue` `[0xb9b,0xbdf)` copies eight dwords, and `snd_timer_user_read` later copies all `0x20` bytes to userspace. `snd_timer_user_ccallback` and the params early-event path independently clear all eight dwords and are fixed.
- **Static route:** `CONFIG_SND_TIMER=m`; shipped policy intends `root:root 0644` for sound nodes, and exact open/ioctl code has no `FMODE_WRITE` gate. Thus a read-only descriptor is sufficient at the generic file-operation layer if effective policy permits it. Module load, node metadata, SMACK, provider, filter, timer/event generation, and read success remain unobserved.
- **Impact boundary:** conditional disclosure of up to eight uninitialized kernel-stack padding bytes per emitted record. No actual bytes, pointer value, KASLR defeat, corruption, controlled write, RCE, root, policy escape, update acceptance, or persistence is established.
- **Remediation:** apply `e4ec8cc8039a7063e24204299b462bd1383184a5` plus complete dominating initialization equivalent to `a8c006aafead3c45ae5d5601e3717055bccf41bc`; initialize full records before every queue append; restrict timer-node access; add sanitizer/KMSAN regression coverage in a disposable environment.
- **Evidence:** `evidence/vendor-kernel-alsa-timer-follow-up.md`; reviewed excerpt `evidence/artifacts/kernel-candidates/snd-timer-padding-cve-2016-4569-4578.asm`; Boolean-only model `tools/uk_fw/alsa_tread_padding_model.py`.

## V-022 — Linux vmacache generation-wrap use-after-free (EXACT PRE-FIX CODE; TARGET WRAP/UAF UNPROVEN)

- **Status:** exact recovered `vmlinux` retains all four CVE-2018-17182 premises: 32-bit invalidation increments, zero-wrap calls, the `mm_users==1` cache-clear skip, and 32-bit lookup generation validation. No mapping cycle, thread lifecycle, counter wrap, stale pointer, dereference, corruption, or privilege transition was executed.
- **Component:** SHA-256 `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`, Build ID `273378887b4cf563c10862fdf18b2292765df781`; `.text` VA `0xffffffff81000000`, file offset `0x200000`; `CONFIG_MMU=y`.
- **Exact mechanism:** `vma_adjust` and `do_munmap` increment dword `mm+0x10` and call live `vmacache_flush_all` only when it wraps to zero. The helper `[0xffffffff810e96d2,0xffffffff810e9797)` returns without clearing task cache pointers when the exact mm user count at `mm+0x48` equals one. `vmacache_find` `[0xffffffff810e97c8,0xffffffff810e9864)` compares and stores only dword mm/task generations before using four cached VMA pointers. Upstream `7a9cdebdcc17e426fb5287e4a82db1dfe86339b2` instead widens both generations to 64 bits and removes the wrap helper.
- **Reachability:** generic upstream reachability uses ordinary MMU mappings and thread lifecycle with no user namespace, network protocol, special device, setuid binary, or optional module. It is post-entry escalation: local unprivileged execution is still required. A full cycle contains 4,294,967,296 generation states; runtime limits and practicality are unmeasured.
- **Impact boundary:** NVD describes use-after-free with possible privilege gain. Exact static code establishes generation aliasing semantics only—not completed wrap, stale VMA survival/dereference, controlled reuse, write, RCE, root, SMACK escape, persistence, or owner-build applicability.
- **Remediation:** backport `7a9cdebdcc17e426fb5287e4a82db1dfe86339b2` or an equivalent 64-bit generation/removal fix; validate with vendor MM stress and memory-safety instrumentation in a disposable environment; do not exercise the wrap path on the owner unit.
- **Evidence:** `evidence/vendor-kernel-vmacache-cve-2018-17182.md`; reviewed excerpt `evidence/artifacts/kernel-candidates/kernel-vmacache-cve-2018-17182.asm`; Boolean-only model `tools/uk_fw/vmacache_wrap_model.py`.

## V-023 — Linux mremap stale-TLB lifetime window (EXACT PRE-FIX ORDER; PAGE RELEASE/REUSE UNPROVEN)

- **Status:** exact `move_page_tables` retains CVE-2018-18281's ordinary-PTE ordering: source PTEs are moved, both bound PTLs are released, a deferred flag is set, and exact old-range TLB flush occurs only at outer exit. No mapping, remap, concurrent invalidation, page release/reuse, stale access, corruption, or privilege transition was executed.
- **Component:** exact `vmlinux` SHA-256 `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`, Build ID `273378887b4cf563c10862fdf18b2292765df781`; `CONFIG_MMU=y`; transparent huge pages are disabled but the affected ordinary PTE path is present.
- **Exact mechanism:** `move_page_tables` `[0xffffffff810f5067,0xffffffff810f54b0)` locks source and distinct destination PTLs, clears each source PTE and writes it to the destination at `0xffffffff810f53fc..0xffffffff810f5400`, then releases those same locks at `0xffffffff810f5418..0xffffffff810f542b`. Only afterward it sets a deferred flag at `0xffffffff810f5448`; outer exit calls exact `flush_tlb_mm_range` with the original old range at `0xffffffff810f5479`. Full function disassembly has no earlier TLB flush.
- **Reachability:** the generic path uses ordinary local mappings and no user namespace, special device, optional protocol/module, or privileged helper. A useful stale access still requires concurrent invalidation and physical-page release/reuse in the unlocked interval. Runtime filesystem behavior, scheduling, resource limits, seccomp, SMACK, memory pressure, and owner-build identity are unobserved.
- **Impact boundary:** exact static evidence establishes a stale-translation window only. It does not establish a populated stale TLB entry, released/reused target page, read/write access, controlled data, corruption, RCE, root, SMACK escape, persistence, or safety impact.
- **Remediation:** backport `eb66ae030829605d61fbef1909ce310e29f78821` or equivalent ordering that flushes every present PTE before releasing both PTLs; validate only in a disposable instrumented kernel environment.
- **Evidence:** `evidence/vendor-kernel-mremap-cve-2018-18281.md`; reviewed excerpt `evidence/artifacts/kernel-candidates/kernel-mremap-cve-2018-18281.asm`; Boolean-only model `tools/uk_fw/mremap_tlb_order_model.py`.

## V-024 — TTY process-group wrong-object lock (EXACT CVE-2020-29661 PREMISE; RACE/UAF UNPROVEN)

- **Status:** exact `TIOCSPGRP` machine code retains CVE-2020-29661's wrong-object lock. Master-side and slave-side setters can update the same referenced slave pgrp field while holding distinct master/slave locks. No PTY was opened and no ioctl, concurrent interleaving, PID lifetime manipulation, UAF, corruption, or privilege transition was executed.
- **Component:** exact `vmlinux` SHA-256 `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`, Build ID `273378887b4cf563c10862fdf18b2292765df781`; `CONFIG_TTY=y`, `CONFIG_UNIX98_PTYS=y`, `CONFIG_SMP=y`, and voluntary preemption.
- **Exact mechanism:** `tty_ioctl` `[0xffffffff812871f8,0xffffffff81287d46)` keeps target TTY in `rbx` and substitutes linked real TTY in `r13` for a PTY master. `TIOCSPGRP` locks `rbx+0x128` at `0xffffffff8128795e`, releases/replaces the PID reference at `r13+0x1d0`, and unlocks `rbx+0x128`. `tty_get_pgrp` independently binds `+0x128` as the pgrp-protecting lock and `+0x1d0` as pgrp; `pty_unix98_install` proves distinct reciprocal peer objects at `+0x218`.
- **Reachability:** shipped boot scripts intend `/dev/ptmx` mode `0666` and a `devpts` mount. Runtime script execution, node/mount metadata, uid, SMACK policy, controlling-terminal state, resource limits, and installed kernel remain unobserved. The passive bench bundle now records `/dev/ptmx`, `/dev/pts`, and mount state before active testing.
- **Impact boundary:** exact static evidence establishes the wrong-lock/same-field race premise only. It does not establish a successful race, PID reference imbalance, UAF, controlled reuse, disclosure, corruption, RCE, root, SMACK escape, persistence, or safety impact.
- **Remediation:** backport `54ffccbf053b5b6ca4f6e45094b942fab92a25fc` or an exact equivalent that locks `real_tty->ctrl_lock`; validate with race and memory-safety instrumentation only on a disposable test kernel.
- **Evidence:** `evidence/vendor-kernel-tty-pgrp-cve-2020-29661.md`; focused instructions `evidence/artifacts/kernel-candidates/kernel-tty-pgrp-cve-2020-29661.asm`; Boolean-only model `tools/uk_fw/tty_pgrp_lock_model.py`.

## V-025 — AF_UNIX MSG_PEEK/garbage-collector race (EXACT CVE-2021-0920 PREMISE; UAF UNPROVEN)

- **Status:** exact shipped `unix.ko` retains both pre-fix CVE-2021-0920 receive paths. Datagram and stream `MSG_PEEK` duplicate attached file lists and pass the resulting SCM cookie toward descriptor delivery without serializing against exact module-global `unix_gc_lock`. No socket, descriptor transfer, GC pass, concurrency, UAF, corruption, or privilege transition was executed.
- **Component:** `/lib/modules/4.1.27-abl/kernel/net/unix/unix.ko`, SHA-256 `e1841632fee9f70eb8f97204cf629a2b34c9e21136fda9236a971ca2d8758ecb`, Build ID `cc807f3b2bce8d7023b7945ec2919698f1034e42`; x86-64 `ET_REL`; `CONFIG_UNIX=m`.
- **Exact mechanism:** `unix_stream_recvmsg` `[.text+0x23a6,.text+0x2a8f)` calls relocation-bound `scm_fp_dup` at `+0x29c3`; `unix_dgram_recvmsg` `[.text+0x355b,.text+0x3824)` calls it at `+0x37b9`. Both are dominated by saved `flags & 0x2`, store the duplicate at SCM-cookie base plus eight, and pass that exact cookie to `scm_recv`. Exact `unix_gc_lock` is `.bss+0x102e`; neither interval references it directly or through an intervening callee.
- **Reachability:** AF_UNIX is a normal local-process surface and the recovered D-Bus configuration strongly implies operational use. Runtime module load/hash, process uid, SMACK policy, resource limits, scheduling, and owner build remain unobserved. The passive bundle now records `/proc/modules` and hashes exact `unix.ko` without loading it.
- **Impact boundary:** exact static evidence establishes missing GC serialization only. It does not establish an overlapping GC pass, candidate graph, premature free, stale use, UAF, controlled reuse, disclosure, corruption, RCE, root, policy escape, persistence, or safety impact.
- **Remediation:** backport `cbcf01128d0a92e131bd09f1688fe032480b65ca` or equivalent post-duplication serialization against the same GC lock on both PEEK routes; validate only in a disposable instrumented kernel environment.
- **Evidence:** `evidence/vendor-kernel-unix-peek-cve-2021-0920.md`; focused instructions `evidence/artifacts/kernel-candidates/kernel-unix-peek-cve-2021-0920.asm`; Boolean-only model `tools/uk_fw/unix_peek_gc_model.py`.

## V-026 — timerfd cancellation-list race (EXACT CVE-2017-10661 PREMISE; CORRUPTION/UAF UNPROVEN)

- **Status:** exact built-in timerfd code retains pre-fix CVE-2017-10661 membership/list serialization. Same-file operations resolve one live context, but setup/removal decide and change `might_cancel` outside the only global-list lock and without a common context-derived cancel lock. No timerfd, shared descriptor, concurrency, list corruption, UAF, crash, or privilege transition was executed.
- **Component:** exact `vmlinux` SHA-256 `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`, Build ID `273378887b4cf563c10862fdf18b2292765df781`; `CONFIG_TIMERFD=y`, `CONFIG_SMP=y`.
- **Exact mechanism:** `timerfd_remove_cancel.part.5` `[0xffffffff8114551c,0xffffffff81145570)` clears `ctx+0xd0` before locking static `0xffffffff81c27410` and unlinking `ctx+0xc0`. In `sys_timerfd_settime` `[0xffffffff81145a49,0xffffffff81145e35)`, setup stores membership before that global lock; the alternate branch calls the same removal helper. The `ctx+0x88` waitqueue lock is acquired only afterward. Creation has no second context-lock initialization equivalent to the upstream fix.
- **Reachability:** timerfd is built in and needs no device, module, namespace, network, or setuid program. Effective syscall filtering, uid/SMACK state, limits, scheduling, and installed owner kernel remain unobserved.
- **Impact boundary:** exact static evidence establishes missing same-context serialization only. It does not establish a winning interleaving, list invariant violation, list corruption, UAF, controlled reuse, crash, disclosure, RCE, root, policy escape, persistence, or safety impact. Public assessments treat denial of service as clearer than privilege escalation.
- **Remediation:** backport `1e38da300e1e395a15048b0af1e5305bd91402f6` or equivalent context-derived locking continuously covering membership and nested global-list operations; validate only with race and memory-safety instrumentation on a disposable kernel.
- **Evidence:** `evidence/vendor-kernel-timerfd-cve-2017-10661.md`; focused instructions `evidence/artifacts/kernel-candidates/kernel-timerfd-cve-2017-10661.asm`; Boolean-only model `tools/uk_fw/timerfd_cancel_lock_model.py`.

## V-027 — TTY session-pointer locking defect (EXACT CVE-2020-29660 PREMISE; DISCLOSURE UNPROVEN)

- **Status:** exact `TIOCGSID` machine code reads and dereferences the real TTY session PID without the control lock or a retained PID reference, while exact writers release the referenced PID before clearing or replacing the same field. No PTY, ioctl, concurrency, stale dereference, disclosure, or privilege transition was executed.
- **Component:** exact `vmlinux` SHA-256 `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`, Build ID `273378887b4cf563c10862fdf18b2292765df781`; `CONFIG_TTY=y`, `CONFIG_UNIX98_PTYS=y`, `CONFIG_SMP=y`, `CONFIG_PREEMPT_VOLUNTARY=y`, and full `CONFIG_PREEMPT` unset.
- **Exact mechanism:** ioctl `0x5429` dispatches to `0xffffffff812879a9`; the branch null-tests `real_tty+0x1d8`, calls `might_fault`, reloads the field, and passes it to exact `pid_vnr` with no control lock/reference acquisition. `pid_vnr` reaches PID-object field reads. Exact `__proc_set_tty` releases the old reference under `tty+0x128`, unlocks, and only afterward stores the replacement; `disassociate_ctty` independently releases then clears the same field under that lock.
- **Reachability:** upstream says an unprivileged user on `PREEMPT=y` can theoretically read four bytes of freed memory. That documented configuration is absent here. SMP leaves other concurrency questions open, but runtime PTY exposure, an eligible writer, and a harmful overlap remain unobserved.
- **Impact boundary:** exact static evidence establishes the locking defect and stale-session read premise only. It does not establish a stale dereference, four-byte return, useful disclosure, controlled write, corruption, RCE, root, SMACK escape, persistence, or safety impact.
- **Remediation:** backport `c8bcd9c5be24fb9e6132e97da5a35e55a83e36b9` or equivalent consistent session-field locking/reference ownership; validate only on a disposable instrumented kernel.
- **Evidence:** `evidence/vendor-kernel-tty-session-cve-2020-29660.md`; focused instructions `evidence/artifacts/kernel-candidates/kernel-tty-session-cve-2020-29660.asm`; Boolean-only model `tools/uk_fw/tty_session_lock_model.py`.

## V-028 — AppLauncher D-Bus caller path bypasses both identified verifier calls (EXACT STATIC ROUTE; RUNTIME EXEC UNOBSERVED)

- **Status:** exact recovered AppLauncher exports session-bus `launch(appid, appname, applocation, ...)` methods. The runtime `applocation` reaches the AppProcess program field; the dispatcher sets byte `+0x1c`; and that byte selects a route to a `QProcess::start` call site without either identified verifier call. No D-Bus request, executable, target launch, credential/label transition, trust-anchor write, update, or persistence action was created.
- **Component:** `/app/bin/AppLauncher`, SHA-256 `c8d6d56bc254ad0731e81f40bd83aa9b3be6b49bcbd8efb291157a06c4a84268`, Build ID `0452df1033bd1bbae15727a83d4d56576d8b9444`; x86-64 `ET_DYN`.
- **Exact mechanism:** startup registers service `com.lge.avn.applauncher`; `/Request` exports the caller path. Relocation-bound vtable slot `+0x68` reaches dispatcher `[0x1ffd0,0x205b3)`. Existing objects have path `+0x58` overwritten directly; new objects accept appids 1..1024 and require only `QFile(applocation).exists()`. The dispatcher stores one to `+0x1c` and calls start routine `[0x163f0,0x1854d)`, where nonzero falls through to `QProcess::start` at `0x1745d` and zero selects verification.
- **Correction boundary:** commit `3090f69` incorrectly constrained launch targets from literal strings on read-only `/navi`; the path is a runtime QString. Conversely, the older public claim that failed verification does not stop launch is too broad: false from the ordinary helper at `0x17e78` or navigation helper at `0x1812f` branches to failure, while only true reaches their start sites. V-028 is a separate bypass path.
- **Authorization/runtime boundary:** the service has configured uid-zero default. The recovered session bus uses EXTERNAL and, with no user connection rule, defaults to the daemon's uid; it is not arbitrary cross-uid access. The candidate is relevant to same-uid, SMACK-separated HMI code only if service-name ownership, Request-object registration, successful bus authentication, effective SMACK access, a relevant existing or successfully constructed AppProcess object, caller control of executable bytes at exec time, launcher execute access, QProcess acceptance and effective launcher privilege retention hold. Runtime uid/capabilities/sandbox state, resulting label and installed owner identity remain unobserved.
- **Impact boundary:** exact static evidence establishes a caller-selected route that bypasses both identified AppLauncher verifier calls and can reach `QProcess::start` after the runtime gates. It does not establish that no other platform enforcement exists, successful `exec`, unrestricted root/SMACK escape, controlled update-anchor substitution, modified-update acceptance, partition writes, slot switching, boot acceptance, mark-good or persistence.
- **Remediation:** eliminate caller-supplied executable paths; resolve appids through an immutable root-owned registry; authorize senders explicitly; run applications under distinct non-root uids; and bind mandatory verification to the exact opened executable immediately before every exec.
- **Evidence:** `evidence/applauncher-dbus-launch-bypass.md`; reviewed excerpt `evidence/artifacts/application-candidates/applauncher-dbus-launch-evidence.txt`; Boolean-only model `tools/uk_fw/applauncher_dbus_launch_model.py`.

## V-029 — IPv6 append-data check occurs after skb copy (EXACT CVE-2017-9242 ORDERING; RUNTIME OVERWRITE UNPROVEN)

- **Status:** exact `__ip6_append_data` allocates a current skb and can call `skb_copy_and_csum_bits` with `fraggap` before calculating and rejecting negative `datalen - transhdrlen - fraggap`. The `-EINVAL`/`kfree_skb` cleanup is after the copy. No syscall, packet, overwrite, crash, or target execution was created.
- **Component:** exact `vmlinux` SHA-256 `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`, Build ID `273378887b4cf563c10862fdf18b2292765df781`; `CONFIG_IPV6=y`.
- **Exact mechanism:** exact `udpv6_sendmsg` calls `ip6_append_data`; the complete wrapper calls `__ip6_append_data.isra.28`. The affected function reaches `sock_alloc_send_skb` or `sock_wmalloc`, then exact `skb_copy_and_csum_bits` and possible trim, before computing the signed `copy` value. The branch-complete function contains no equivalent early rejection dominating allocation/copy; upstream `232cd35d0804cc241eb887bb8d4d9b3b9881c64a` moves that check before allocation.
- **Reachability boundary:** ordinary UDPv6 static call flow is established. Installed owner-unit kernel identity, uid/capabilities, SMACK, seccomp/socket policy, and achievement of the required internal skb/fraggap state remain unobserved.
- **Impact boundary:** NVD supports local denial of service and the upstream commit records skb head/shared-info overwrite. Static affected ordering does not establish an actual overwrite, controlled bytes/extent, reliable crash, code execution, privilege escalation, root, SMACK escape, update acceptance, or persistence.
- **Remediation:** backport `232cd35d0804cc241eb887bb8d4d9b3b9881c64a` or equivalent early rejection before allocation/copy; validate only in a disposable instrumented kernel environment.
- **Evidence:** `evidence/vendor-kernel-ipv6-cve-2017-9242.md`; reviewed/complete assembly under `evidence/artifacts/kernel-candidates/kernel-ipv6-cve-2017-9242*.asm`; Boolean-only model `tools/uk_fw/ipv6_append_bounds_model.py`.

## V-030 — perf move-group context race (EXACT CVE-2017-6001 MECHANISM; RUNTIME RACE/ROOT UNPROVEN)

- **Status:** exact `perf_event_open` software-group-to-hardware-context migration loads `group_leader->ctx` before waiting for two mutexes and uses that saved context after the wait without a live-reference acquisition, identity revalidation/retry, or post-lock group-state check. No event, thread, race, crash, or privilege transition was created.
- **Component:** exact `vmlinux` SHA-256 `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`, Build ID `273378887b4cf563c10862fdf18b2292765df781`; `CONFIG_PERF_EVENTS=y`, `CONFIG_SMP=y`; exact initialized `perf_event_paranoid` is 1 but its installed runtime value is unknown.
- **Exact mechanism:** `SYSC_perf_event_open [0xffffffff810cd747,0xffffffff810ce12f)` reads the group context at `0xffffffff810cde81`, locks old/new context mutexes at `0xffffffff810cdea4`/`0xffffffff810cdeac`, then begins removal/migration without re-reading the group context. Exact `perf_event_ctx_lock_nested.isra.60 [0xffffffff810c7996,0xffffffff810c7a14)` separately demonstrates the compiled nonzero-reference, lock, identity-check, unlock/drop/retry discipline, but the move-group path bypasses it. Upstream `321027c1fe77f892f4ea07846aeae08cefbbb290` adds the missing two-context effects and post-lock state validation.
- **Reachability boundary:** public records classify this as local privilege gain. Static syscall/configuration and initial policy are established; installed identity, runtime policy, PMU availability, accepted unprivileged event combinations, scheduling, and a winning interleaving are unobserved.
- **Impact boundary:** the exact pre-fix mechanism does not establish stale/dead-context use, crash, controlled corruption, credential modification, SMACK transition, unrestricted root, update acceptance, or persistence.
- **Remediation:** backport `321027c1fe77f892f4ea07846aeae08cefbbb290` or equivalent live-reference/identity/retry and post-lock move-state validation; restrict unprivileged perf access as defense in depth; validate only on a disposable instrumented kernel.
- **Evidence:** `evidence/vendor-kernel-perf-cve-2017-6001.md`; complete exact assembly `evidence/artifacts/kernel-candidates/kernel-perf-cve-2017-6001.asm`; upstream patch `evidence/artifacts/kernel-candidates/cve-2017-6001-fix.patch`; Boolean-only model `tools/uk_fw/perf_move_group_race_model.py`.

## V-031 — AppDMClient verifies a pathname but later consumes it by pathname again (EXACT STATIC IDENTITY BOUNDARY; RUNTIME SUBSTITUTION UNPROVEN)

- **Status:** exact recovered AppDMClient caller data flow proves that verifier wrapper `0x34870` returns only integer status. The staging path later constructs a pathname copy and calls `QProcess::execute` at `0x8296b`; the XML reader verifies at `0xe1ff7` and later opens at `0xe22d5` or `0xe281f`. No retained open description, inode/device comparison, or object-identity revalidation binds these later consumers to the object examined by the earlier verifier. No updater, pathname race, changed object, launch request, partition write, or target execution was created.
- **Component:** `/app/bin/AppDMClient`, SHA-256 `9a1fb796d7ac24fcce71c16e3dbee9306c888f43e705ee081f41b7d473978bd0`, Build ID `b2dbcc5231f444d8f1dd68eb7a2376323ce805df`; x86-64 PIE.
- **Exact mechanism:** staging calls the verifier for AppUpgrade/XML at `0x802db`/`0x80320` and retains integers. Wrapper `[0x34870,0x34d43)` passes target-path and key bytes to linked verifier `0x121040`, destroys its local file object, and returns `%eax`. Later `0x82913..0x8296b` formats a two-path copy command and executes a separate process. XML-reader `[0xe1e90,0xe3166)` independently performs verify-then-open/parse sequences. Complete reviewed callers contain no identity token handed from verification to consumption.
- **Reachability boundary:** the ordinary unequal staging and XML-reader code paths are static. Both recovered eMMC fstab branches configure `/update` as a writable ext4 partition, and boot setup conditionally creates `/update/usb/bin` plus staged executable placeholders. This proves writable-filesystem structure, not actor write access: mounted-directory uid/gid/mode, effective `SMACK64`, process credentials/labels, loaded policy, update serialization, timing, and an actual verified/consumed object mismatch remain unobserved. The intended equal `/update/usb/bin` relaunch remains a separate route that skips repeated pair checks but is not itself first-entry control.
- **Impact boundary:** this establishes a conditional pathname-substitution structure, not successful substitution. It does not establish authentication bypass, successful staging or child creation, modified-update acceptance, partition writes, slot switching, boot acceptance, root, mark-good, or persistence. V-032 inventories all direct inner FUMO verifier/hash calls, but parameterized verifier-target provenance, indirect/external checks, and final payload binding remain under reconstruction.
- **Remediation:** verify and consume one immutable open object; where subprocess boundaries prevent descriptor use, copy into a root-owned non-replaceable staging object and authenticate that exact staged object immediately before launch, with identity/metadata changes treated as failure.
- **Evidence:** `evidence/appdmclient-source-identity-boundary.md`; `evidence/update-source-runtime-policy.md`; exact retained assembly `evidence/artifacts/update-candidates/appdmclient-source-identity-boundary.asm`; Boolean-only model `tools/uk_fw/update_source_identity_model.py`; passive collector `tools/uk_fw/bench_state_bundle.py`.

## V-032 — Inner FUMO authentication coverage boundary (EXACT CALL INVENTORY; PARAMETERIZED TARGETS UNRESOLVED)

- **Status:** a whole-`.text` direct-call inventory in the exact embedded FUMO ELF found six calls to its public-key file verifier and two calls to its file-MD5 helper. Fixed/enumerated operands resolve to the update descriptor, firmware archive, firmware entries, or navigation files. Several signature-verifier routes accept caller-provided QStrings whose complete producer provenance is not yet bounded, so absence of a staged/running `AppUpgrade` operand remains unknown. Startup derives a resource directory from `argv[0]`; the worker relaunch wrapper calls `execv` without a direct pre-exec verifier/hash call inside that FDE. No updater, verifier, helper, target path, launch, update package, partition, slot, or target syscall was exercised.
- **Component:** exact embedded FUMO ELF SHA-256 `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`, Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`; x86-64 PIE.
- **Exact mechanism:** startup `[0x125800,0x126fe4)` calls `QCoreApplication::arguments` at `0x1259e3`, removes the application-name suffix at `0x125a45..0x125a4e`, and ultimately stores the base directory at object `+0x30` in initializer `[0x8dc60,0x8dd51)`. Verifier `[0x45820,0x45d75)` reads the fixed public key and calls signed-container driver `0x18f740`; its complete direct call set is `0x7be3a,0x80095,0x802f0,0x9d1d2,0x100bb0,0x140092`. At `0x100bb0`, the target derives from function argument `%rdx`; caller `0x16e030` forwards a QString from a meta-call argument structure, preventing a complete negative target classification. File-MD5 helper `[0x140f50,0x1413e4)` has only direct callers `0x1432f6` and `0x15170c`, both from navigation checksum paths. Relaunch wrapper `[0x6c9a0,0x6cab5)` calls `execv` at `0x6caa8` without invoking those helpers.
- **Trust boundary:** this maps V-031's later-authentication question but does not resolve it. Parameterized verifier-target producers, virtual/indirect calls, external credential/helper behavior, loader and boot-stage enforcement remain unknown. Later descriptor/archive/component authentication is real, but only exact operand binding can establish whether a check covers the outer executable or final consumed payload.
- **Impact boundary:** no runtime source mutability, changed executable, successful process creation, authentication bypass, package acceptance, partition write, slot switch, boot acceptance, privilege transition, root, mark-good, or persistence is established. Payload checks may still reject unauthenticated update data even if outer executable identity divergence were later proved.
- **Remediation:** bind pre-exec authentication to the exact immutable staged executable consumed by the launcher; independently bind every transformed payload and final partition image to authenticated metadata; keep boot acceptance and rollback enforcement as separate trust stages.
- **Evidence:** `evidence/appfumo-authentication-coverage.md`; exact retained assembly `evidence/artifacts/update-candidates/appfumo-authentication-coverage.asm`; Boolean-only model `tools/uk_fw/fumo_auth_coverage_model.py`.

## V-033 — Production compositor shipped unstripped with full DWARF (HARDENING, informational)

- **Status:** confirmed by inspection; informational hardening, not a vulnerability in itself.
- **Where:** `usr/bin/weston` in `NE_E.EUR.S5W_L.001.001.260128`, 1,052,408 bytes.
- **Scope:** confirmed on `usr/bin/weston` and also present in `usr/lib/weston/ias-shell.so` and
  `usr/lib/weston/ias_plugin_framework.so` (7 debug sections each), i.e. the components that decide what the
  vehicle display shows.
- **What:** the binary retains `.debug_info` (360,666 bytes), `.debug_loc` (286,264), `.debug_abbrev`,
  `.debug_str`, `.debug_aranges`, `.debug_ranges`, plus `.symtab` and `.strtab`. Full type definitions,
  struct member names and source line information are present in a production infotainment image.
- **Why it matters to a defender:** this is not exploitable on its own, but it removes most of the cost of
  reconstructing internal interfaces. In this project it enabled an exact, member-by-member ABI
  reconstruction that identified a 24-byte layout difference from upstream Weston, which was the cause of
  a compositor crash. An adversary attacking the compositor, its IPC, or any module loaded into it gets
  the same advantage for free, including struct layouts, function names and line tables for the
  highest-privileged graphical component in the vehicle.
- **Impact boundary:** information disclosure to anyone holding the firmware. No remote reachability is
  implied, and the firmware is already distributed to every vehicle.
- **Remediation:** strip debug information from shipped binaries, or ship it separately under a symbol
  server with access control. Verify the release build does not carry `-g` into the image, and audit other
  binaries in the image for the same condition.

## V-034 — Update trust anchor sits on a writable root (merged entry, runtime check)

The merged register entry states the update pipeline verifies its manifest against a public key held as an
ordinary file, and that replacing that file would let substitute-signed packages be accepted. Its stated
precondition is an existing privileged local write primitive. Both halves of that were checked here.

**The design claim holds.** Reconstructed pipeline agreement with the merged entry: manifest verified before
any payload is unpacked, which is sound; the weakness is the anchor's protection, not the verification order.

**The filesystem question is now answered, and it favours the finding.** Measured in the recovered image and
confirmed on a live boot:

- Kernel cmdline mounts root **`rw`**, and the running system reports `/ -> ext4 rw,noatime,data=ordered`.
- `etc/fstab` is **empty**, and the root line in `etc/fstab_emmc` (`#/dev/root / auto ro,…`) is **commented
  out**, so nothing remounts root read-only.
- `lib/systemd/esinit` lines 12-13, which would `mount -o remount,ro /`, are **commented out** as well.
- `app/share/AppUpgrade/teruten5_pub.key` is mode **0755**, 294 bytes, inside `/app` on that writable root.
  Writing into that directory from a root context succeeded on the live guest.

So the anchor is mutable at runtime **and the change persists across reboot**, because it lives on the eMMC root
rather than tmpfs. That is materially worse than a transient exposure: a substituted anchor survives the power
cycle that would otherwise clear an in-memory compromise.

**Caveat, stated rather than glossed:** the live guest reports the file as owned by uid 501 / group `dialout`,
which is an artefact of this project's extraction (ownership from the extracting user), not evidence about the
shipped image. The vendor's ownership is unverified here; only the mode (0755), the path, and the rw mount are
established. The precondition therefore remains "a privileged write primitive", not "any local user".

**Status:** precondition confirmed at the filesystem level; no write primitive demonstrated by this project.

## Chain analysis — V-012 lowers V-013's precondition from "root" to "local code execution"

V-013 states its precondition as an existing privileged write primitive. V-012, from the merged register,
supplies exactly that, and the two were checked against each other here.

**V-012 confirmed as stated, with the service list verified.** `lib/systemd/esinit:10` mounts `tmpfs` on `/tmp`
with **default options**, i.e. the kernel default root mode `01777` — world-writable and sticky. **Eleven**
enabled services read `EnvironmentFile=/tmp/session_appmgr.env`: `ApplicationLauncher`, `nua`, `MediaBrowser`,
`mediamanager`, `CryptoService`, `watchdogd`, `ofono`, `mof`, `vbtd`, `credman`, `remote`. None of them sets
`User=`, so all run as root; `ApplicationLauncher.service` was checked directly and carries no `User=` line.
The environment-file format accepts arbitrary variables, including dynamic-loader overrides.

**The resulting chain, stated end to end:**

1. Any local unprivileged code execution (a media parser, an application, or the launcher's unverified path in
   the merged V-009) writes `/tmp/session_appmgr.env` containing a loader override.
2. The next start of any of those eleven services loads attacker code **as root**.
3. That root context writes `app/share/AppUpgrade/teruten5_pub.key` — established earlier to be mutable at
   runtime and persistent across reboot.
4. Every subsequent update, wired or over-the-air, is verified against the substituted anchor.

**What is established and what is not.** Established: the tmpfs mount options, the eleven services, the absence
of `User=`, the anchor's mutability and persistence, and that the directory chain to the anchor is `0755`
throughout (so step 3 genuinely needs step 2's root, not merely a local user). Not established: a concrete
first-stage execution primitive, and any service restart trigger in practice.

**The prior V-009 negative was incomplete and is superseded by V-028.** Commit `3090f69` searched literal path
references and correctly established that fixed `/navi` targets live on read-only partitions. It did not trace the
exported D-Bus `applocation` QString. Exact code now proves that this runtime caller path overwrites the launcher's
program field, sets its direct-launch byte, and reaches a `QProcess::start` attempt without either identified verifier call.

This removes the claimed fixed-read-only-path precondition, but it does not round the chain up to demonstrated root.
The private session bus defaults to the daemon's uid, and runtime service ownership, Request-object registration,
same-uid authentication, SMACK access, relevant AppProcess-object availability, QProcess acceptance, exec-time target
control/access, effective launcher privilege, successful exec, and resulting credentials/label remain unobserved. If
those gates hold for a compromised uid-zero/SMACK-separated HMI application, V-028 could supply a controlled privileged-
exec candidate without waiting for the V-012 service-restart route. Otherwise the established V-012 → V-013 chain still requires local code
execution plus one privileged service restart. See `evidence/applauncher-dbus-launch-bypass.md`.

## Amendment to V-007 (A) — the media scanners run as root over removable and world-writable paths

The merged register records media parsing without privilege separation. The service identity and the scan
targets were checked here and both confirm it:

- `lib/systemd/system/mediamanager.service` starts `/app/bin/mediamanager` with **no `User=` directive**, so it
  runs as **root** (the system-service default).
- `app/bin/lightmediascanner.conf` ships `startup-scan=true` and
  `directory=audio:/usr_data/media/;audio:/media/usb/;audio:/media/mtp/` — the scanner parses removable-media
  mount points by default **at startup**, before any user action.
- `/media` is a `tmpfs` mounted with `defaults` (established under V-011/V-013), i.e. kernel default root mode
  `01777`.

**Why the last point matters more than it looks.** The obvious reading of V-007 is "physical USB access required,
then a parser bug". Because `/media` is world-writable, a **local unprivileged process can place files there**
without any removable medium at all, and the root scanner will parse them on its next scan. That removes the
physical precondition for the parsing step and leaves only the parser defect itself.

**Live confirmation of the identity claim.** The static inference was checked on a running guest rather than
left as an absence-of-`User=` argument:

- `mediamanager` start → `pid=718 Uid: 0 0 0 0`
- `lightmediascannerd` driven directly → `pid=709 Uid: 0 0 0 0`

Both run as **root**, measured. So the separation is genuinely absent, not merely unset in a unit file.

**What is *not* demonstrated, and why it matters.** The parsing step — the one that would consume
attacker-supplied bytes — was attempted **four ways** and did not run in this harness:

1. default configuration (`db-path` ships commented out, so there is no destination);
2. a written config supplying `db-path=/tmp/lms.db` and `directory=audio:/media/usb/`;
3. the same with `LD_LIBRARY_PATH=/app/lib`, because `usr/lib/liblightmediascanner.so.0.5.1` is a **38-byte
   stub** while the real 300 KB library lives in `app/lib`;
4. the daemon driven directly, with a probe file present at `/media/usb/probe.mp3`.

In every case the process ran as **uid 0** and produced **no database and no diagnostic output at all**.

**The control channel was then identified and made to work.** `lightmediascannerctl` uses the **session** bus, not
the system bus — its first failure was literally `Could not get session bus connection … dbus-launch --autolaunch`.
With a session bus provided (`dbus-daemon --session --print-address --fork`), the daemon registers
`org.lightmediascanner` (verified: one matching name on the bus) and `lightmediascannerctl scan` **executes**:

`Server at :1.0, try to start scan` / `Elapsed time: 0.025 seconds`

So the scan is now invocable; a database still does not appear at the configured `db-path`, which points at a
compiled-in or differently-resolved location rather than the config value in this projection.

**One check in this investigation was invalid and is recorded as such:** a `find / -newer /media/usb/probe.mp3`
sweep cannot work on this guest because the guest clock reads 1970, so every image file appears "newer". That
result was discarded rather than interpreted.

**The database sink was then located.** `lightmediascannerd` creates `<HOME>/.config/lightmediascannerd/db.sqlite3`
— measured at **155,648 bytes, mode `0600`, owner `root:root`**, produced by the root daemon after
`lightmediascannerctl scan`. So the pipeline is real and the artefact is root-owned: a parsing defect here runs with
full privilege and writes a root-only database.

**Indexing of `/media/usb` is not merely undemonstrated — the daemon does not scan it at all.** The scanner's own
progress output names the directories it walks:

`Scan Progress audio:/usr_data/media/ …`
`Scan Progress audio:/media/mtp/ …`

`/media/usb` never appears, even with a genuine MP3 present **and** the path mounted as a separate filesystem, and
regardless of a `[daemon_configuration]` file placed at either `/app/bin/lightmediascanner.conf` or
`$HOME/.config/lightmediascanner.conf`. Probe files of both kinds produced zero rows in every attempt (ten
configurations). The effective scan set is therefore `/usr_data/media` and `/media/mtp`, which appear to be
compiled-in defaults rather than the `directory=` line in the shipped file.

**This corrects the premise of this entry and is recorded as a correction.** The removable-media channel here is
**MTP**, not USB mass storage: the scanner walks `/media/mtp/`, which is the mount point an attached phone or media
player presents, and it lives under the same world-writable `/media`. So the conclusion — a root process parses
attacker-supplied removable content — stands, but the channel named in the earlier text ("`media/usb`") was wrong.

**Final status for V-007.** Established: privilege (measured, uid 0), scan targets (sourced), scan invocation
(executes on command), database sink (measured, root-owned). Not established: that attacker-supplied bytes in
`/media` are actually consumed and recorded. The configuration defect is confirmed; the parsing reachability stops
one harness feature short, and this register claims no further.

**Chain status.** First stage candidate confirmed at the configuration level, with the root identity now measured:
root parser over attacker-supplied content, reachable locally via `/media`. What remains unproven is (a) that the
scan completes in a production configuration, and (b) a memory-safety defect in the parsing stack that converts a
parsed file into execution. Both are bug-hunts rather than configuration questions, and this register claims
neither. Stated precisely: the separation is absent, the reachability is local, and the
missing piece is a single parser vulnerability rather than any missing access.

## Amendment to V-007 (B) — parse reachability DEMONSTRATED (2026-10-31)

The configuration finding is now backed by a demonstration of the parsing itself, on the corrected channel.

Setup: `lightmediascannerd` started as root with a session bus and `lightmediascannerctl scan`; a genuine MP3 placed
at `/media/mtp/mtptest.mp3` on a filesystem mounted there.

Result, from the scanner's own progress line and the resulting database:

```
Scan Progress audio:/media/mtp/ commit=1, uptodate=1, processed=0, deleted=0, skipped=0, errors=0
mtptest rows: 5        (in /root/.config/lightmediascannerd/db.sqlite3, mode 0600, root:root)
```

So: **a root process read attacker-supplied content from a removable-media mount point, copied it into its store,
and indexed it into a root-owned database.** The parse is no longer "configured but unproven" — it is observed.

**What this does and does not establish.** It establishes reachability of the parsing path with attacker-controlled
bytes and full privilege, which is the precondition any parser memory-safety defect needs in order to matter. It
does **not** establish a parser vulnerability: no malformed input was crafted and no memory corruption was attempted.
The remaining step for a complete chain is a bug in the parsing stack, and that is a dedicated fuzzing exercise
rather than a reachability question.

**Corrected channel.** This was demonstrated via `/media/mtp` after `/media/usb` was proven not to be scanned. The
MTP mount point sits under the same world-writable `/media`, so a local process can populate it without any physical
device, subject to the listing above showing `/media/mtp` as scanned when mounted.

## V-035 — Root media-parsing stack links outdated third-party codec libraries

- **Status:** configuration and inventory confirmed by inspection; no exploit attempted or demonstrated. This is a
  supply-chain-ageing finding, not a claimed vulnerability in any specific library.
- **Where:** the parsers under `app/lib/lightmediascanner/plugins/`, loaded by `lightmediascannerd` /
  `mediamanager`, both of which run as **uid 0** (measured). Parse reachability with attacker-supplied content is
  **demonstrated** (see the V-007 section above: a file from `/media/mtp` was consumed, copied and indexed into a
  root-owned database).
- **What the parsers link, with versions read from the image:**

| library | version in image | note |
|---|---|---|
| `libpng16` | **1.6.32** | 2017 release; numerous memory-safety CVEs published after it |
| `libogg` | **0.8.2** | early-2000s vintage; current line is 1.3.x |
| `libvorbis` | **0.4.9** | correspondingly old; multiple historical CVEs in this line |
| `libtheoradec` | **1.1.4** | 2011-era decoder |
| `libmatroska` / `libebml` | **6.0.0 / 4.0.0** | container parsing |
| `libmp4v2` | **2.0.0** | upstream abandoned around 2012 |
| `libmagic` | **1.0.0** | file-type sniffing, itself a parser of attacker bytes |
| `libgdk_pixbuf` | present | image loading path |

- **Why it matters:** every one of those libraries parses attacker-controlled bytes, in a process with full
  privilege, over a path that a local process can populate. Ageing codec components are exactly where memory-safety
  defects accumulate, and this stack has not been updated to match the 2026 build date of the surrounding system.
- **What is *not* claimed:** that any specific CVE is present in these builds, or that any of them is reachable to
  code execution here. Version dating is evidence of exposure, not proof of a defect.
- **Advisory check performed, with the one hit rejected.** Each pinned version was queried against GitHub's advisory
  database (`/advisories?affects=<pkg>`) and compared against the published vulnerable ranges. Result:

  | package | version | advisories seen | applicable |
  |---|---|---|---|
  | libpng | 1.6.32 | 1 | **rejected — see below** |
  | libogg, libvorbis, libtheora, mp4v2, file | as listed | 0 | none returned |

  The single candidate was **CVE-2018-14550** (GHSA-qwwr-qc2p-6283, severity high 8.8, range `<= 1.6.35`). It is
  **not applicable**: the advisory text places the defect in `get_token` in **`pnm2png.c`**, a contrib/demo utility
  shipped with libpng sources — and `pnm2png` **does not exist anywhere in the image** (searched). Recording it
  would have been a false positive against code that is not deployed.

  **Caveat on the negatives:** GitHub's advisory database is sparse for older or less popular libraries, so
  "0 advisories" here is *not* evidence of absence. It means this particular source had nothing to return.
- **Consequence for status:** no specific CVE is asserted for these builds. V-014 stays a supply-chain-ageing
  finding — the exposure signal is the release dates and the privilege the parsing runs under, not a named bug.
  Confirming applicability would require version-exact matching against distro-level trackers (Debian/OpenEmbedded)
  for the same releases, which is a separate exercise.
- **Remediation direction:** update the codec stack to maintained versions; parse in a sandboxed, unprivileged,
  seccomp-confined helper and pass only metadata back; treat `libmagic` sniffing as untrusted input handling; and
  stop running media parsing under root at all, which fixes this class regardless of library age.

## Amendment to V-007/V-035 (C) — bounded malformed-input test (negative, weak instrument)

Two sets of deliberately malformed files were pushed through the demonstrated root parsing path.

- **Images are not reachable through this configuration.** Five malformed PNGs placed in `/media/mtp` produced
  `processed=0`: the scan directory is typed `audio:/media/mtp/`, so image parsers never run on that path. That
  corrects an implicit assumption — the reachable parsers are the **audio** ones (`id3`, `ogg`, `flac`, `mp4`), not
  `png`/`jpeg`.
- **Five malformed audio files did not crash the daemon.** Truncation at half and at 200 bytes, a 300-byte bit-flip
  run, 512 bytes of random data after the header, and a synthetic `ID3` header with a 2 GB declared size. Result:
  `commit=1, uptodate=5, errors=0`, the scanner process unchanged before and after (`pid 720` both times), and
  **zero segfaults in `dmesg`**.

**How much this is worth.** Very little, and it is recorded that way. Truncation and bit-flips are the crudest
possible mutations; a parser that survives them tells you almost nothing about memory safety, because the defects
that matter require structurally valid containers with hostile field values. A real answer needs structured
generation (valid container, mutated length/offset fields) or a coverage-guided harness driving the plugin
libraries directly — neither of which was attempted here.

**Status unchanged:** V-007's reachability stands (demonstrated), V-014's ageing-exposure framing stands. No parser
vulnerability is claimed, and this test does not move either entry.

## V-036 — ApplicationLauncher dispatch stalls behind an unstartable appId 2 (OBSERVED IN EMULATION)

- **Status:** behaviour observed repeatedly in the VM; not characterised against a live unit. Availability defect with a
  security consequence for this project's work, not a memory-safety or privilege issue.
- **What happens:** once `com.lge.avn.applauncher` is registered, the launcher loops on
  `ApplicationLauncher::getAppProcessByAppId appId[2][ApplicationManager]` roughly every 1.7 s and does not exit that
  loop — **twenty occurrences in one boot**. While the loop persists, **no external request is dispatched at all**: in
  the same boot, a well-formed `launch` call was accepted by the bus and produced **zero** `appId[999]` dispatch
  entries.
- **A correction to an earlier version of this entry, now re-measured.** It first stated the loop persisted "after
  `ApplicationManager` was started and running", which was unverified because a systemd progress line had obscured the
  process check. Re-measured with the pid captured to a file so the console could not swallow it, in one boot:

  `ALWRAPAM before_launcher pid=2079`
  `ALWRAPAM after_loop pid=2317`
  `appId[2][ApplicationManager]` occurrences: **20**

  So an `ApplicationManager` process was running before the launcher and a *different* process of the same name was
  running after it — i.e. the launcher spawns its own instance — and the loop still ran 20 times.

- **The caveat is now resolved, against the stronger reading.** Ten `pidof ApplicationManager` samples taken two seconds
  apart across twenty seconds, while the loop continued, produced **no pids at all** (`ALWRAPSEQ` empty). So during the
  retry window the dependent application is **not running**: the loop is a **spawn-fail retry**, not a poll of a live
  instance. Liveness across retries is not merely unproven, it is **disproven** for the sampled window.
- Consequence for the entry's framing: V-036 is not "the launcher polls a dependency that is present", it is "the
  launcher repeatedly fails to bring its own dependent application up, and dispatches nothing while retrying". The
  remaining question is why `ApplicationManager` exits, which its own log (`/tmp/am.log` in the harness) should answer
  and which this project has not yet read.
- **Why it matters beyond the emulation:** the launcher's dispatch path is what V-028 relies on, so this loop is the
  demonstrated reason V-028's runtime execution could not be reproduced here. Anything that prevents
  `ApplicationManager` from being observed as running — a crash, a missing dependency, or withholding it — plausibly
  keeps the launcher in this loop indefinitely, which is a local availability effect on the HMI.
- **What is *not* established:** that the loop is unconditional on hardware; that it persists when `ApplicationManager`
  is *confirmed* running (the capture cannot show this either way — see the correction above); or that any privileged
  action is denied rather than merely deferred. No security impact is claimed.
- **Relevance to V-028:** recorded as the specific, observed obstacle to reproducing V-028 at runtime. If this loop is
  cleared on a unit, the V-028 runtime test becomes meaningful; until then its negative results say more about this
  defect than about V-028 itself.
- **Remediation direction (defensive):** bound the launch retry with backoff and a terminal state, keep dispatching
  while a dependency is being retried, and surface a diagnosable error rather than looping silently.
- **Why `ApplicationManager` never stays up — answered by reading its own log.** Run alone with a compositor it starts
  (`pid 719`, alive) and then reports `ArgParserBase::initBootInfo attach fail`, retry counts 1–3, and
  `initBootInfo read error`. Its strings name the mechanism: `AskSysBootinfo`, `AskSysBootinfo Retry`,
  `AskSysBootinfo reply is VALID`, `parseMicomBootInfo`. Boot information comes from the MICOM service and is
  **validated**.
- **The break in this project's chain is therefore the payload, not the plumbing.** `micom-service` answers
  `AskSysBootinfo` with 35 zero bytes: enough for the launcher to register, **not valid** for
  `ApplicationManager`'s parser. AM fails, exits, the launcher retries `appId 2` forever and dispatches nothing — which
  is why V-028's runtime tests never saw their call processed.
- **Correction: `ApplicationManager` is stripped.** The previous line said it "carries debug information"; it has
  **0 `.debug_*` sections** and no `parseMicomBootInfo` symbol. That assumption was wrong and is corrected here — the
  analysis has to be done on disassembly, not DWARF.
- What disassembly gives instead, as concrete anchors for whoever continues: the log tag `parseMicomBootInfo` sits at
  vaddr `0x317c40` and is referenced at `0x25a7be` and `0x25a892`; `AskSysBootinfo` is at `0x31596a` (referenced at
  `0x257f55`) and `AskSysBootinfo reply is VALID` at `0x315993` (referenced at `0x258810`, inside the block at
  `0x258808` that logs validity). Immediately before that block the code compares a field at `+0x4` against **`0x1c`**
  (`cmpl $0x1c, 0x4(%rax)` at `0x258705`) and indexes bytes from `+0x1c` (`movzbl 0x1c(%rax,%rdx)` at `0x25872a`).
  That is the shape of a length-prefixed structure with payload starting at offset `0x1c` — a starting point for
  establishing what "VALID" requires, not the answer.
- **The length gate is passed, so the rejection is elsewhere.** Reading the block properly:
  `cmpl $0x1c, 0x4(%rax)` compares a **length** field against 28 and `jle` leaves on `<= 28`; the accepted path then
  reads `movzbl 0x1c(%rax,%rdx)` — **byte 28 of the payload**. Our reply is **35 bytes**, so `0x23 > 0x1c` and this gate
  is satisfied. Whatever rejects our payload happens **downstream** of it, in content checks or in a separate
  shared-memory attach.
- **`ApplicationManager` contains no literal boot-info segment key.** Its strings show no `BOOTINFO*` name, so if it
  attaches shared memory the key is composed at runtime — which is why the zero payload's *shape* may be irrelevant and
  the missing object is the real fault.
- **The `openat` trace came back empty of qipc paths, which is itself informative.** Running `ApplicationManager`
  detached under `strace -f -e trace=openat` while it reached the same failure (`initBootInfo attach fail`, retries 1–2)
  produced only **15 traced calls and no `qipc_sharedmemory_*` path at all**. So this attach is **not file-backed**: it
  is not the Qt key-file mechanism that `AppHomeScreen` used, and the technique that solved the earlier problem does
  not apply unchanged.
- That points at either a direct **`shmget`/`shmat`** with a key the process derives itself, or a **D-Bus** call — neither
  of which `openat` observes.
- **The D-Bus hypothesis is now eliminated by measurement.** Repeating the trace inside the **systemd** boot, where the
  bus exists, gives:

  `connect(9, {sun_path="/var/run/dbus/system_bus_socket"}) = 0`  ← bus reachable
  `connect(8, {sun_path=@"/tmp/dbus-GaG2OzbkNE"}) = 0`            ← session bus reachable
  `shmget(0x51121397, 416, IPC_CREAT|IPC_EXCL|0600) = 0`          ← creates its own segments

  and yet `ArgParserBase::initBootInfo attach fail` **still** occurs, with retries 1–3. So boot-info initialisation is
  **not** a bus problem, and the research-init `ENOENT` seen earlier was an artefact of that test (no bus was running),
  not the fault.
- **My earlier `openat` trace was invalid and is withdrawn.** It produced only 15 calls because `ApplicationManager`
  exited almost immediately in that configuration — the trace recorded a process that never reached the code of interest.
  Using it to conclude "the attach is not file-backed" was the same mistake as reading a zero from an unreached path.
- **File-backed attach eliminated under a validated instrument.** The trace was repeated with conditions verified rather
  than assumed: a system bus actually running (`/run/dbus/system_bus_socket` present), the compositor up, and
  `ApplicationManager` demonstrably reaching `initBootInfo` (its log shows `attach fail` and retry 1 at `00:00:12`).
  Result: **22 traced `openat` calls and no `qipc_sharedmemory_*` and no `/dev/shm/*` path**.
- Combined with the earlier run in which both bus connections succeeded, that eliminates **both** candidates this thread
  has been testing: it is not a D-Bus reachability problem, and it is not a Qt key-file shared-memory attach. What
  remains is either an object created by a component that never runs in this projection, or an in-process condition —
  neither of which `openat` or `connect` will show.
- **The untargeted trace then located the failing step, by name.** A full `strace -f` (3,465 calls) with the bus and
  compositor up shows `ApplicationManager` writing these to its log:

  `MicomInterfaceM::askSysBootInfo():iface is VALID`
  `AskSysBootinfo Retry = 0 / 1 / 2`

  So the **interface check passes** and the failure is in the **call**, not in constructing or reaching the interface.
  In that run no `com.lge.car.micom` owner was running, so the retries are "no peer" — which is consistent and separately
  confirmed by the boots where `micom-service` was up and the launcher consumed its answers.
- **Where that leaves the cause:** with a peer present the reply arrives (the launcher consumes it), and
  `ApplicationManager` *still* fails `initBootInfo`. The remaining candidate is therefore the **content** of the 35-byte
  `ay` — its validation in `parseMicomBootInfo` — rather than reachability, interface construction, or any shared-memory
  mechanism. Both file-backed and D-Bus reachability paths have now been excluded by measurement.
- **The oracle test was inconclusive for a mundane reason, and is recorded as such.** Running the peer and
  `ApplicationManager` together with clean console markers gave:

  `RESULT_SVC=` (empty) · `RESULT_ASK=4` · `RESULT_VALID=0` · `RESULT_ATTACH_FAIL=1` · `RESULT_SVC_ANSWERS=0`

  The peer **was not running** in that environment, so it answered nothing — meaning `ApplicationManager`'s four asks
  were again "no peer" and the **payload content remains untested**. This is not a negative about the payload; it is a
  failure to run the experiment.
- **Root cause of the "peer did not start": it was never installed there.** The `micom-service` binary had been injected
  into the **esinit** workspace but not into the **softbackend** workspace, so every research-init test invoked a
  non-existent path, which failed silently to a log that was therefore empty. Checked directly:
  `stat /usr/bin/micom-service` resolves in `esinit-fs` and does not in `softbackend`.
- **With it installed, the payload was tested against a live peer for the first time, and the result is a clean,
  interpretable negative:**

  `RESULT_SVC=720` · `RESULT_SVC_ANSWERS=1` · `RESULT_ASK=1` · `RESULT_VALID=0` · `RESULT_ATTACH_FAIL=1`

  The peer **ran** and **answered** `AskSysBootinfo`; `ApplicationManager` asked once, never logged
  `reply is VALID`, and still failed `initBootInfo attach`. So the 35 zero bytes are **received and rejected** — the
  payload's content is confirmed as the blocker, which every earlier attempt had failed to test.
- **Empirical variant probing does not converge, and is reported as such.** With the oracle working, `micom-service` was
  changed to cycle payload variants on successive asks and five `ApplicationManager` instances were run against it:

  `variant 0` (all zeros) → `valid=0`, attach fail · `variant 1` (byte 28 = `0x01`) → `valid=0`, attach fail ·
  `variant 2` (byte 28 = `0xFF`) → `valid=0`, attach fail

  So plausible single-field guesses are all rejected. The space is 35 bytes with unknown semantics, and blind variants
  will not find it — the signal is clean but the search is unguided.
- **Conclusion for this thread, stated plainly:** the payload's acceptance criteria must be **read from the parser**, not
  guessed. The anchors for that work are already recorded, and the binary is stripped, so it is genuine disassembly work —
  or vendor source. No further variant guessing is warranted.
- **A first step in that reading was taken and did not resolve it.** The `.rodata` neighbourhood of the VALID message
  contains `AskSysBootinfo`, `AskSysBootinfo Retry = %1` and `AskSysBootinfo reply is VALID` but **no "not valid"
  counterpart**, so the rejection path is silent rather than logged. Searching the disassembly for branches into the
  validity block at `0x258808` found **none**, which means it is reached by fall-through or a computed path rather than a
  direct conditional jump — so the deciding comparison is not adjacent to the message that reports it.
- **A fuller read of the same log reframes the failure toward shared memory.** With the peer answering
  (`AskSysBootinfo -> 35 bytes variant 0`), `ApplicationManager` logs in sequence:

  `initBootInfo attach fail` → `retryCount : 1/2/3` → `initBootInfo read error`
  → `askSoundSetupInfo():iface is VALID`
  → `initMicomShareMem() -> Start`
  → **`initMicomShareMem() -> pszSrc NULL`**

  The last line is the informative one: after the boot-info attempt, `ApplicationManager` initialises a **MICOM shared
  memory** region and finds its **source pointer NULL**. So the object it ultimately wants is a **shared-memory region
  populated by the MICOM side**, and a D-Bus `ay` reply alone does not satisfy it — which explains why every payload
  variant was rejected *and* why no `qipc` file open was ever seen: the region may be created by a component that never
  runs here, and consumed by pointer rather than by name.
- **Correction to the reading above, from the disassembly.** The block that emits `pszSrc NULL` sits immediately after
  `movq 0x40(%rbx), %rdi` and a call to **`QSharedMemory::detach`**, i.e. the `QSharedMemory` there is a **destination owned
  by `ApplicationManager`**, and `pszSrc` is its **source buffer**. So the NULL source is a **consequence** of the earlier
  boot-info failure, not evidence of a third-party provider that never runs.
- **Consequence, restated correctly:** the missing thing remains the **boot info itself**, obtained via the MICOM path that
  logs `attach fail` and `read error`. My previous sentence — that a *provider of the region* was missing — was wrong and
  is withdrawn. The `QSharedMemory` is the consumer side; the supply side is the boot-info retrieval that already fails
  before it.
- **`/dev/shm` is absent from the image and its absence is not the cause.** The image ships **no `/dev/shm`** at all — no
  `esinit` line mounts it and no `fstab` entry exists for it, the same class of gap as the missing `/dev/pts` found earlier.
  Mounting a `tmpfs` there (`chmod 1777`) before starting `ApplicationManager` changes nothing:
  `attach fail` and `read error` still occur, `reply is VALID` still never appears. So POSIX shared memory availability is
  excluded too.
- **Two separate findings, kept separate:** the missing `/dev/shm` is a genuine environment gap that may affect other
  components in this projection (worth fixing on principle, alongside `/dev/pts`), while the boot-info retrieval failure has
  now survived every environmental candidate tested — bus reachability, `/dev/shm`, peer presence, payload content, and
  file-backed segment paths.
- **A run where `attach fail` disappeared was checked and is *not* a fix.** With `ihu-shim` executed before the service, the
  oracle reported `attach fail = 0` and `read error = 0` — which looks like success. It is not: the same run shows
  `HAS_BOOTINFO=0`, i.e. **`ApplicationManager` never entered `initBootInfo` at all**. Verified rather than assumed, which
  is the only reason the false positive was caught.
- **What the ordered log shows instead, and it is order-independent across runs:**

  `initMicomShareMem() -> Start` → **`initMicomShareMem() -> pszSrc NULL`** → `askSysBootInfo():iface is VALID`

  Two useful facts follow. First, `initMicomShareMem` runs **before** the `AskSysBootinfo` call, so the D-Bus ask is not
  what supplies `pszSrc`. Second, the reliable, reproducible failure across orderings is the **NULL `pszSrc`**, not the
  attach: the attach failure appears only when a different path runs first.
- **New lead from the binary's own strings:** `ApplicationManager` contains the literal **`MICOM_STATUS_MESSAGE`**, which
  matches a segment name already seen in `AppHomeScreen`'s trace
  (`qipc_sharedmemory_MICOMSTATUSMESSAGE…`) and which `ihu-shim` is able to create. That makes a MICOM status region the
  most likely source for `pszSrc`, and testing it is a matter of ensuring that segment exists before the client starts.
- **The named segment was created and `pszSrc` stayed NULL.** With `ihu-shim` reporting six segments created including
  `qipc_sharedmemory_MICOMSTATUSMESSAGE…` (verified in its own output), a peer owning `com.lge.car.micom` and answering
  `AskSysBootinfo`, and the client running to 79 log lines, the result is `PSZNULL=1` with `ATTACHFAIL=0` and
  `HAS_BOOTINFO=0`.
- So **segment existence is not the missing condition**. The most likely remaining explanation is that the segment must
  contain a **valid structure**, not merely exist: `ihu-shim` creates it zero-filled, and everything this project has
  learned says a zero-filled structure is rejected by a parser that validates — exactly as the 35-byte D-Bus payload was.
- That collapses the last two open questions into one: whether the boot info arrives by `ay` reply or by shared region,
  what is missing is **the layout and validity rules of the MICOM status structure**. Reachability, environment, segment
  existence and payload length have all been excluded by measurement.
- **The "harvest a populated region from the vendor daemon" route was tested and is not available.** Running
  `micommanager_userspace` with a `/dev/ttyS1` peer and a system bus produced: daemon **running** (`pid 723`) but
  **zero `qipc_*` files created**. So the vendor daemon is not the publisher of the MICOM status region — consistent with
  the region name appearing in `ApplicationManager`'s own strings, i.e. the client creates it and the missing thing is the
  **data** it would fill it with. There is therefore no template to harvest from the daemon in this projection, and that
  route is closed.
- **The mechanism is `stat`, and that is why earlier traces missed it.** An untargeted trace shows
  `ApplicationManager` doing:

  `stat("/tmp/qipc_sharedmemory_MICOMSTATUSMESSAGEea9b2c48…") = -1 ENOENT`
  `open("/tmp/qipc_systemsem_MICOMSTATUSMESSAGE…", O_RDWR|O_CREAT|O_EXCL|O_CLOEXEC, 0640) = 7`

  Qt's `QSharedMemory` SysV backend resolves its key with **`ftok`, which calls `stat`**, not `openat` — so the earlier
  `-e trace=openat` sweep could never have seen the path, and "no `qipc` open" was a **false negative from the instrument**,
  not evidence about the client. With `ihu-shim` having created the region, the same client stops logging `attach fail`,
  confirming the file's existence is what the attach needs.
- **Two things still do not hold, and are recorded as failures rather than folded into progress:**
  1. The **authentic recovered profile** — `00000826050000051302000003c8140000000000000000000000020001000000000000`, 35
     bytes, taken from `work/vm/…/micom-contract/BOOTINFO-AND-SIM-V2.md` where it was decoded from AppLauncher's own BIS
     logs — served over D-Bus is **still rejected** (`reply is VALID` never logged).
  2. **Seeding those same 35 bytes into the `MICOMSTATUSMESSAGE` region at offset 0 does not clear `pszSrc NULL`.**
  So the region must exist *and* `pszSrc` comes from somewhere this thread has not yet located — most likely a second
  object, or a different offset/header inside this one.
- **The missing-input hypothesis was tested and does not explain `pszSrc`.** An untargeted `ENOENT` sweep showed what
  `ApplicationManager` looks for beyond the qipc region:
  `/Data/mnt-wt/Settings/shared_public/{GroupContent.json,resource-table-cfg.itz-lock}`,
  `/Data/mnt-c/Settings/BackupFileList.info`, `/log_data/backtrace/AppManager_info.txt`, `/rw_data/app_data/common/eng/…`,
  and **`/dev/mmcblk1p1`**. Creating those directories and placeholder files (`[]` and a header line) changed nothing:
  `PSZNULL=1`, `ATTACHFAIL=0`, `BOOTINFO=0`. So `pszSrc` is not sourced from any of those paths.
- **Two side-findings worth keeping for VM fidelity, independent of this bug:** the client expects a **second MMC device**
  (`/dev/mmcblk1p1`) that the projection does not provide, and a **`/Data` resource table** under
  `mnt-wt/Settings/shared_public` — matching the `/Data` item already ranked in the HMI gap analysis.
- **Hand-off state for V-036, complete:** reachability, interface construction and shared-memory mechanisms excluded by
  measurement; reply content confirmed as the blocker; three plausible payloads rejected against a live client; the oracle
  for testing further candidates exists and is documented; and the static anchors are listed with the specific difficulty
  (silent rejection path, no direct branch to the validity block, stripped binary) recorded so the next attempt starts
  where this one stopped rather than at the beginning.

## V-037 — Privileged USB handling contains a command-construction defect

(Imported from the parallel repository, where this was numbered V-006.)

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

## V-038 — Media parsing runs without privilege separation

(Imported from the parallel repository, where this was numbered V-007.)

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

## V-039 — Serial console is available and password-gated

(Imported from the parallel repository, where this was numbered V-008.)

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

## V-040 — Application launcher can start binaries without invoking signature verification

(Imported from the parallel repository, where this was numbered V-009.)

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

## V-041 — Engineering-mode keypad credential derives from static unsalted digests

(Imported from the parallel repository, where this was numbered V-010.)

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

## V-042 — Marker files under world-writable runtime paths trigger privileged actions

(Imported from the parallel repository, where this was numbered V-011.)

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

## V-043 — Privileged services import environment files from a world-writable location

(Imported from the parallel repository, where this was numbered V-012.)

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

## V-044 — Software-update signature trust anchor is stored unprotected

(Imported from the parallel repository, where this was numbered V-013.)

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

## I-002 — EGL software-rendering copy bounds investigation

(Imported from the parallel repository, where this was numbered I-001.)

- **Status:** reproducible VM crash and instruction/caller evidence; **not a confirmed exploitable vendor vulnerability**. No severity/CVE claim.
- **Affected observed stack:** original recovered vendor `/usr/lib/libEGL.so.1.0.0` (SHA-256 `0c373e50d1a4700c2161628c2a2b61a25a9b5abbcd7bb52ccc763cf5020e3d53`) with the project's non-stock Mesa 18 software DRI module. Decoration-unset control triggers early Camera/Standby crashes; stock Intel-driver applicability is untested.
- **Evidence:** `evidence/navigation-launch-status-contract.md`; complete core archive `10fbb21b…24987c` and bounded ptrace archive `e0884a3c…fdeaae` (full digests in that note).
- **Observation:** faulting memcpy vector store targets an unmapped address 64 bytes before a writable buffer. Top captured stack word follows `memcpy@plt` in `dri2_wl_swrast_put_image2`. A width-derived stride is cached before a buffer update that can change the width; captured stride/count registers are -4. Original memcpy entry arguments and upstream invalid-size source are not yet directly measured.
- **Threat/impact boundary:** local VM application termination is established. Attacker influence, hardware reachability, arbitrary writes, code execution and persistence are not. Do not attribute a compatibility-induced failure to stock firmware without a stock-path reproduction.
- **Remediation direction:** verify dimensions after initialization/update; reject negative/overflowing dimensions, byte counts and out-of-range rectangles; refresh cached stride when width changes. Select a scoped VM adaptation only after confirming the ordering defect; do not weaken libc checks or force manager state.
- **Validation needed:** capture width before/after update and copy-entry arguments; test first swap, resize, zero-size hide/unhide, undecorated/decorated clients and normal positive-size buffers. Preserve existing Home/navigation controls and observe native return-to-Home pixels, not manager integers alone.

## Rejected / out-of-scope items

- **Keystore ioctl tail disclosure:** rejected; decoded ioctl size is `0x120`, covering fields read (correction C8).
- **`keystore_get_ksm_key` stack disclosure:** rejected by instruction-level review; private/public sub-buffers were misread (C9).
- Android/Telechips `hmg_nemesis` and `micomd` findings are not findings against this Linux/x86-64 target.
- Historical published CVEs require exact-component/version and code-path validation; do not relabel them as newly found or confirmed on `260128`.
- wpa_supplicant CVE-2015-1863 and CVE-2021-27803 are rejected for the exact recovered `260128` binary. `p2p_add_device()` gates every SSID copy on length at most 32, and `p2p_process_prov_disc_req()` unconditionally re-fetches the peer after `p2p_add_device()`. P2P capability and conditional launch machinery remain present, but do not reverse these exact fixed-code conclusions. See `evidence/wpa-supplicant-p2p-cves.md`.
- Bluetooth CVE-2017-13262's named missing extension-length decrement is present in neither selectable BSA binary; both exact receive loops decrement before extension parsing. CVE-2018-9355's AOSP 512-byte local UUID-list shape is not present in the reviewed target function. CVE-2019-2025 is a local Binder-kernel flaw, not Bluetooth. CVE-2020-0022 names Android's absent `packet_fragmenter.cc` architecture. CVE-2017-0781/0783/0785 and CVE-2018-9588 remain unaccepted pending exact BSA fix comparison. These constraints do not alter V-019's separately proven CVE-2017-0782 BNEP parser defect. See `evidence/broadcom-bsa-bluetooth-cves.md`.
- ALSA PCM CVE-2017-0861 is rejected by the exact shipped open-mutex backport. ALSA sequencer CVE-2018-1000004 lacks the official per-client ioctl serialization, but its published sequence requires `write()` and recovered intended `/dev/snd/seq` mode `root:root 0644` grants ordinary users no write permission. See `evidence/vendor-kernel-alsa-follow-up-cves.md`.
- CVE-2015-7613, CVE-2016-7117, and CVE-2017-8890 are rejected for exact built-in code. SysV IPC credentials and message/shared-memory state are initialized before IDR publication; `recvmmsg` stores a delayed socket error before exact `fput_light`; and `inet_csk_clone_lock` clears the exact child multicast-list field used by `ip_mc_drop_socket`. See `evidence/vendor-kernel-socket-ipc-backports.md`.
- CVE-2016-2544 is rejected for exact `snd-seq.ko`: queue deletion holds its timer mutex across exact stop and close. CVE-2016-2545 through CVE-2016-2548 are rejected for exact `snd-timer.ko`; CVE-2016-2549 is unavailable because `CONFIG_SND_HRTIMER` is not set and the affected provider is absent. CVE-2016-4569 is fixed, while CVE-2016-4578's residual timer-interrupt path is tracked as V-021. See `evidence/vendor-kernel-alsa-timer-backports.md` and `evidence/vendor-kernel-alsa-timer-follow-up.md`.
- CVE-2016-2384 is rejected for exact `snd-usbmidi-lib.ko` despite `CONFIG_SND_USB_AUDIO=m` and shipped generic USB-audio/MIDI modules. After raw-MIDI ownership is installed, every reviewed endpoint-creation failure returns the error without directly freeing the USB-MIDI object; the owner's private-free callback remains for legitimate teardown. See `evidence/vendor-kernel-usb-midi-backport.md`.
- CVE-2017-11176 is rejected by exact shipped `sys_mq_notify` control flow despite `CONFIG_POSIX_MQUEUE=y`. `netlink_attachskb` drops the old socket reference before returning one, but both failed retry lookup paths bypass `netlink_detachskb` and enter skb-only cleanup. The compiler emits no explicit socket-register clear on the loop edge; branch routing provides the source fix's semantic effect. See `evidence/vendor-kernel-mq-notify-backport.md`.
- CVE-2017-7533 is rejected despite `CONFIG_INOTIFY_USER=y` and the old `4.1.27-abl` banner. Exact `__fsnotify_parent` and `vfs_rename` take and release stable dentry-name snapshots around notification; short names are copied under the dentry lock and external names retain an owner reference. The separate inotify length/copy operations therefore do not receive the CVE-specific mutable name. See `evidence/vendor-kernel-inotify-cve-2017-7533.md`.
- CVE-2016-9806 is rejected despite the old kernel banner. Exact `netlink_dump` saves `cb->module` and `cb->skb` while the callback mutex is held, clears `cb_running`, unlocks, and passes only the saved values to `module_put` and `consume_skb`. A new dump can reuse the callback after unlock without redirecting the completed invocation's cleanup to the new objects. See `evidence/vendor-kernel-netlink-cve-2016-9806.md`.
- CVE-2016-7910 is rejected despite the old kernel banner. Exact `disk_seqf_stop` loads the iterator from `seq_file.private +0x78`, passes it to exact `class_dev_iter_exit` and `kfree`, then stores pointer-width zero to that same owner field. A later `disk_seqf_start` allocation failure skips its store, but framework stop reloads null rather than the freed iterator. Both block proc operation tables bind this stop routine. See `evidence/vendor-kernel-block-cve-2016-7910.md`.
- CVE-2016-7911 is rejected despite the old kernel banner. Exact `get_task_ioprio` locks `task +0x630` before reading `task->io_context +0x678` and `io_context->ioprio +0x12`; exact `exit_io_context` uses the same task lock while loading and clearing the pointer, then unlocks before releasing the object. See `evidence/vendor-kernel-ioprio-cve-2016-7911.md`.
- CVE-2016-7914 is rejected despite the old kernel banner. In exact `assoc_array_insert`, metadata-tagged terminal-node slots branch past `ops->compare_object`; only non-null leaf-tag fallthrough reaches the callback, across all 16 slots. Exact `__key_link_begin` binds the reviewed routine to keyring operations. See `evidence/vendor-kernel-assoc-array-cve-2016-7914.md`.
- CVE-2018-14634's oversized argument-space prerequisite is rejected despite the old banner. Complete exact `copy_strings` preserves `ARG_MAX`, then limits larger space to `min(rlimit(RLIMIT_STACK)/4, 0x600000)` and routes oversize state through page release to `-E2BIG`. See `evidence/vendor-kernel-exec-cve-2018-14634.md`.
- CVE-2018-9568's wrong-cache socket-clone free is rejected for the exact recovered kernel by a direct fix-shaped effect, not by the old version banner. `sk_clone_lock` allocates through source current `sk_prot`, completes the only creator-overwriting copy, then overwrites clone `sk_prot_creator` with that same allocator protocol before every observed in-function post-copy `sk_free`; all non-null returns are corrected, so later caller cleanup is separate and post-return. Exact final release uses creator protocol `+0xf8` as its cache argument. `IPV6_ADDRFORM` divergence and the TCP disconnect/listen/child-clone route remain compiled, so this is positive correction evidence rather than an absent-route result. Runtime reachability, corruption, privilege escalation, unrestricted root, persistence, and owner-installed identity remain unobserved. See `evidence/vendor-kernel-socket-clone-cve-2018-9568.md`.
- The absent AF_PACKET companion frame-count guard remains a correctness gap but is rejected as a V1/V2 frame-lookup OOB primitive: full-block-count allocation dominates publication, wrapped `frame_max` positions remain within the vector and block even at wrapped zero, and exact `vm_insert_page` rejects the separate understated-VMA path. Three syntactic signed vector-index edges begin at block count `0x80000001`, but the minimum vector produces order 23 and exact `__rmqueue`/`__alloc_pages_nodemask` reject every order above 10; `__kmalloc` therefore returns null before any edge is reachable. See `evidence/vendor-kernel-af-packet-frame-count.md`.
- VM rendering slowness, watchdog timeouts and missing simulated CAN data are currently compatibility/integration issues, not established exploitable security defects.

## Maintenance

For each new issue record: stable ID, affected artifact/build and digest, source location, evidence type, caller/reachability, preconditions, bounded impact, remediation owner/status, regression test and remaining unknowns. Keep secrets and private keys out of reports. Append discovery/validation/correction events to `Ioniq5-HISTORY.md`; edit this register to reflect current conclusions. Preserve rejected findings to avoid rediscovery.
