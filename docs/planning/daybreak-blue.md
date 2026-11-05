# Daybreak Blue — remediation-first advisory plan

Date: 2026-11-06

## Scope and decision rule

This plan is for the owner of the recovered EU `NE_E.EUR.S5W_L.001.001.260128` image. It ranks changes by **risk removed per engineering hour**, not by finding number or novelty. It does not treat the QEMU projection as a vehicle: no finding has been reproduced on a vehicle, and the latest VM result still has two independent application-termination mechanisms (a cold-start deadline and a warm-relaunch SIGTERM). The VM is therefore useful for image-policy checks, not as proof of in-vehicle reachability. Sources: `../CURRENT-STATE.md`; `../kernel/25-registration-warm-fast-but-still-killed.md`; `../MEASUREMENT-DISCIPLINE.md` rules 1, 3, 5, 6, 8 and 14.

A fix receives priority when it removes a writable trust decision, removes an unauthenticated root boundary, or contains several otherwise independent defects. Existing controls must remain intact: system D-Bus stays deny-by-default, SMACK rules stay loaded, the image stays free of setuid/setgid files, and no new world-writable directory is introduced. Source: `../defences/controls-inventory.md`.

**Counting note.** `../REMEDIATION-REPORT.md` exposes 26 entries when `3b` is counted, and its visible Tier-1 list contains 13 entries. Its closing table says “13” Tier 1 and “11” Tier 2, although the visible Tier-2 entries total 13 (`7–13`, `17–20`, `24–25`). Release planning should use the entries, not the stale `13 + 11` summary. This is a documentation count, not a security conclusion.

## 1. The five changes to do first

### 1 — Item 16 / V-065: move all nine `/etc` trust anchors out of shared `/tmp`

**Why first.** This is the best risk reduction per unit of effort. One storage-pattern correction closes the demonstrated account-database problem (V-054), the compositor configuration problem (V-055), and the systemic nine-anchor problem (V-065). It also removes writable inputs used by the console policy and reduces the value of compromising any one root service. Sources: `../REMEDIATION-REPORT.md`, items 2, 3 and 16; `../../Ioniq5-VULNERABILITIES.md`, V-054, V-055 and V-065.

**What it closes.** Resolution of the account database, shell list, resolver, mount table, ECNR configuration, compositor module selection, and front/rear display assets through names in a shared `1777` directory. It does not by itself cure services already running as root.

**Exact image change.** In `lib/systemd/esinit`, `etc/smack_setup.sh`, `etc/setup_ecnr_engine_db.sh`, and `etc/install_westonPngLogo.sh` (or their owner-source equivalents), create `/run/etc` as `root:root 0700`, create generated files as `root:root 0600`, and change these link targets from `/tmp/...` to `/run/etc/...`:

- `/etc/passwd`
- `/etc/shadow`
- `/etc/shells`
- `/etc/fstab`
- `/etc/resolv.conf`
- `/etc/ecnr/config`
- `/etc/xdg/weston/weston.ini`
- `/etc/front_lcd.png`
- `/etc/rear_lcd.png`

Where a consumer genuinely needs wider read access, grant only the required read mode or group on that file; do not widen `/run/etc`. Keep Weston module paths absolute and restricted to the signed, read-only module directory.

**Ten-minute owner check.** On a candidate image, run `readlink -f` and `stat -c '%U:%G %a %n'` for all nine names and their resolved targets. The targets must be under `/run/etc`, owned by root, and not group/world-writable. From a non-root test uid, an append to the resolved passwd target and a replacement of `weston.ini` must fail; `getent passwd` and a normal compositor start must still work. This is a negative-control pair, not an account-creation demonstration.

### 2 — Item 21 / V-071: make production console and SSH fail closed

**Why second.** A single boot marker currently selects four security outcomes, is created on every boot, and lives in a world-writable directory. Removing that default also narrows V-049 and V-067. Sources: `../REMEDIATION-REPORT.md`, items 5, 18 and 21; `../root-access-paths.md`, routes 1 and 5; `../../Ioniq5-VULNERABILITIES.md`, V-071.

**What it closes.** Default eligibility for the root serial login, selection of the shell-bearing legacy passwd file, inclusion of `/bin/sh` in the generated shell list, and the condition that would permit Dropbear if its binary were later added.

**Exact image change.** In `lib/systemd/esinit`:

1. delete the unconditional `touch /tmp/secure_console_disable`;
2. stop copying `/etc/passwd.legacy` in production and always select `/etc/passwd.secure` (root `nologin`);
3. do not invoke `/etc/esinit_agetty.sh` in a production profile;
4. if a service profile is required, use a positive marker such as `/run/platform-debug/secure-console-enabled` in a `root:root 0700` directory, create it only after an authenticated debug-state decision, and default to absence on missing, invalid, or unavailable MICOM state.

Remove `dropbear@.service`, `dropbearkey.service`, and `/etc/dropbear/authorized_keys` from production images as item 18 already recommends. If the units must remain in a service image, change `ConditionPathExists=/tmp/secure_console_disable` to the root-only positive marker and disallow root login.

**Ten-minute owner check.** Boot the production candidate and inspect: `getent passwd root`, the process list for `agetty`/`dropbear`, `/proc/cmdline`, and the marker paths. Pass means root resolves to `nologin`, no `agetty` or Dropbear process is present, the old `/tmp/secure_console_disable` is absent, and loss or invalidity of MICOM state does not enable either service. A QEMU serial endpoint is sufficient; no vehicle UART is needed.

### 3 — Item 15 / V-064, beginning with item 22 / V-072: contain vendor services

**Why third.** V-064 is the blast-radius multiplier for almost every other entry: 106 of 107 units default to root and no vendor unit uses even one listed systemd hardening directive. Applying a common baseline also directly fixes the mDNS daemon’s privilege posture and limits access to the writable anchors while item 16 is deployed. Sources: `../REMEDIATION-REPORT.md`, items 15 and 22; `../defences/controls-inventory.md`; `../../Ioniq5-VULNERABILITIES.md`, V-064 and V-072.

**What it closes.** It does not prove parser safety, but it turns compromise of a logger, thumbnailer, browser, mDNS parser, media service, or telematics component from automatic platform-wide root access into a service-local incident. `PrivateTmp=yes` also cuts many services off from the shared `/tmp` anchor family.

**Exact directive change.** Add reviewed unit drop-ins for every vendor service, with this minimum default:

```ini
[Service]
NoNewPrivileges=yes
CapabilityBoundingSet=
ProtectSystem=strict
PrivateTmp=yes
```

Then add only explicit `ReadWritePaths=` and capabilities proven necessary. Add `User=`/`Group=` for services that do not require root, starting with `lib/systemd/system/carplay_mdnsd.service`: `User=nobody`, the four directives above, and an interface/address-family restriction appropriate to CarPlay. Set `Group=` only to a group verified to exist in the production account database. Next move media indexing, thumbnailing, logging, and browsing services to dedicated users. Preserve the existing no-setuid/no-setgid property; do not compensate for a broken unit by adding a setuid helper. Add `RestrictAddressFamilies=` and `SystemCallFilter=` only after the first baseline boots cleanly.

**Ten-minute owner check.** Static: count `NoNewPrivileges=`, `CapabilityBoundingSet=`, `ProtectSystem=`, `PrivateTmp=`, and `User=` across vendor units and compare with an allow-listed manifest; no count may regress. Dynamic: `systemctl show` one changed service and `carplay_mdnsd.service` for `User`, `NoNewPrivileges`, `CapabilityBoundingSet`, `ProtectSystem`, and `PrivateTmp`; run `systemd-analyze security` on both. `ps -o user= -p $(pidof mdnsd)` must not report root. A normal service smoke test is the positive control.

### 4 — Item 19 / V-068 and V-069: remove mutable and fleet-shared update credentials

**Why fourth.** The writable navigation CA is the cheapest claimed persistent path if it is actually the package-verification anchor. Even before that final link is demonstrated, a root CA managed by the updater must not remain group-writable on `/rw_data`. The same release should remove private keys distributed in four application binaries. Sources: `../REMEDIATION-REPORT.md`, item 19; `../root-access-paths.md`, route 0; `../defences/controls-inventory.md`, control 5; `../../Ioniq5-VULNERABILITIES.md`, V-068 and V-069.

**What it closes.** Replacement of the TomTom trust root by a writer to `/rw_data`, plus fleet-wide reuse of private material embedded in `AppProjection`, `AppUpgrade`, `AppScomoDM`, and `AppDMClient`. It restores the value of the update signature control rather than replacing that control.

**Exact file/change.** Stop reading or preserving `/rw_data/navi_data/certificates/TomTom_Root_CA.crt` as an authority. Put the navigation verification CA in a signed read-only image location, owned `root:root` and mode `0444`, and change SCOMO’s lookup/copy logic to use only that path; an existing mutable copy must neither override nor suppress installation of the immutable CA. If field CA rotation is required, accept only a CA object signed by a separate read-only root. Remove PEM private-key blocks from the four named binaries and provision per-device credentials at manufacture into protected storage; rotate the distributed keys and their server-side trust.

**Ten-minute owner check.** Static image CI must find no authoritative CA under `/rw_data`, no `BEGIN .*PRIVATE KEY` block in `/app/bin`, and exactly the approved CA fingerprint at the immutable path. In a candidate boot, changing or adding the old `/rw_data/.../TomTom_Root_CA.crt` must not change the verifier’s selected CA fingerprint. A known-good vendor-signed navigation test package remains the positive control.

### 5 — Item 7 / V-059: make update verification and installation consume one immutable byte stream

**Why fifth.** This is the highest-consequence release fix, although its risk-per-hour ranks below the configuration changes because runtime use of the removable path is still unresolved. The extracted FUMO code has a check invocation and a separate apply invocation; the owner should remove that class even if a runtime trace ultimately shows local staging. Sources: `../REMEDIATION-REPORT.md`, item 7; `../root-access-paths.md`, route 1; `../../Ioniq5-VULNERABILITIES.md`, V-059.

**What it closes.** Check/use substitution between package verification and partition writing, including the candidate keyless downgrade. It also gives the updater a clean, auditable invariant: the bytes accepted are the bytes installed.

**Exact implementation change.** In the owner source that builds the FUMO payload embedded in `app/bin/AppUpgrade`, replace the separate `md5sum <source-path>` check and later `DecryptToPIPE <source-path> ... | ... | dd ...` reopen with one of these designs:

1. copy once from removable media to a root-only, non-replaceable staging file, `fsync` it, close write access, verify that exact staged object, and install only from that object; or
2. stream through one owner-held descriptor while computing the authenticated digest over the same bytes delivered to the installer, and commit the target only after verification succeeds.

Do not rely on path, timestamp, inode, size, or a pre-install MD5 comparison. Retain the existing package signature check, and add boot-time integrity enforcement for installed rootfs content as a separate defence.

**Ten-minute owner check.** In an owner test build with partition output redirected to a disposable image, record file opens for one update. Pass means the removable source is opened once for ingestion, verification and apply reference the same immutable staged object or descriptor, and changing the removable object after ingestion cannot alter the output. A known-good package must still install to the disposable target; a changed package must be rejected. No vehicle hardware is required.

## 2. Three claims that need a demonstration before acceptance

| Priority | Claim | Cheapest honest demonstration | What a negative means |
|---|---|---|---|
| 1 | **V-059: the static check/apply separation is a usable removable-media race, especially a keyless downgrade.** | First, in an owner updater harness or recoverable bench unit, trace the exact object opened by the check and by `DecryptToPIPE`; record device, inode and mount provenance. If both are attacker-controlled media, use two harmless, correctly formed owner test envelopes and redirect `dd` to a disposable image to show that bytes accepted in the check can differ from bytes delivered to apply. Calling it a *downgrade* additionally requires an authentic older package to pass every later rollback/boot check on a recoverable unit. | If both stages consume one protected local copy, the reported race does not exist in this flow; retain the single-object fix as hardening but withdraw “keyless downgrade.” If substitution works but an independent rollback/boot check refuses the older image, narrow the result to check/use substitution, not downgrade. |
| 2 | **V-069: the mutable TomTom CA authorizes navigation-package signatures.** | In the owner’s update test environment, replace only the mutable CA with a lab CA, present a harmless metadata-only navigation test package signed by that lab CA, and log the trust anchor selected by the verifier. Use an unchanged vendor-signed package as the positive control and a package signed by an unrelated CA as the negative control. | Rejection means the path is updater-managed data but not the package-signature root, or a second immutable root/pin dominates. The writable file remains bad key hygiene, but the persistent-root chain and “sign a package the unit accepts” claim must be withdrawn. |
| 3 | **V-073: either shipped command becomes an unauthenticated TCP-to-serial service in a production-relevant state.** | In an isolated owner test image, provide a pseudoterminal as `/dev/ttyUSB0`, enter the documented manufacturing/TMS state through supported controls, and inspect `ss -ltnp` plus the owning process. Connect from a second network namespace and verify only that a benign text token traverses both directions. This proves command-path and listener behavior without a modem or vehicle. | No listener means the strings are dead, disabled, or require another unrecorded state; downgrade to “dormant bridge command ships.” A loopback-only listener removes remote reachability. A listener with no production `/dev/ttyUSB0` leaves device identity and production impact unproved. |

Sources: `../../Ioniq5-VULNERABILITIES.md`, V-059, V-069 and V-073; `../REMEDIATION-REPORT.md`, items 7, 19 and 23; `../root-access-paths.md`, routes 0 and 1.

## 3. The two statements most likely to be wrong

### A. V-059’s “keyless downgrade stands” / “does not depend on anti-rollback” wording

The same V-059 entry says the decisive runtime fact is unresolved: the check and apply may both read a staged local copy. Static separation of shell invocations proves two opens in code, not that an attacker controls both objects at both times. It also cannot prove that no later bootloader or package rollback decision exists.

**Settling check.** Trace both opens during a real owner update and identify the backing object. Then run an authentic older package only on a recoverable owner unit and record every version/rollback decision through first boot. Until both checks pass, call this a **candidate removable-media check/use flaw with a possible keyless downgrade consequence**, not a demonstrated or standing downgrade.

Source: `../../Ioniq5-VULNERABILITIES.md`, V-059, especially “The one thing this still does not decide” and “Which path the two reads actually open is not settled here.”

### B. V-056’s residual statement that applications run under an “exempt” `_` label

V-056’s correction records enforcing audit denials against a `_` subject, so `_` is not exempt. The projection also cannot preserve a `security.SMACK64EXEC` attribute that is absent from the shipping tar records; production provisioning may add it. The entry’s later “Why it matters” paragraph therefore outruns its own correction.

**Settling check.** On two production units or final factory filesystem images, run:

```sh
getfattr -n security.SMACK64EXEC /app/bin/AppHomeScreen
cat /proc/$(pidof AppHomeScreen)/attr/current
```

Then, under enforcement, have the owner’s test application attempt one explicitly disallowed read and one explicitly allowed read, verifying the object label before either access. If the executable/process carries `App::home`, narrow V-056 to a projection/provisioning uncertainty. If it carries `_`, report the actual `_` grants and denials; do not call `_` exempt.

Sources: `../REMEDIATION-REPORT.md`, item 1; `../../Ioniq5-VULNERABILITIES.md`, V-056; `../MEASUREMENT-DISCIPLINE.md`, rules 1, 2 and 6.

## 4. Platform verification plan for every Tier-1 item

### Deliverable the platform team should publish

Create one reproducible CI bundle against the final production rootfs and one booted QEMU/reference-board job. It should emit:

1. image/build identifier and SHA-256 of the rootfs manifest;
2. a static manifest of file type, target, owner, group, mode, capabilities and SMACK execution label;
3. parsed systemd and D-Bus policy reports, not grep-only pass/fail output;
4. a boot report containing the tested process uid, label, capabilities, namespaces and selected unit properties;
5. a result for every row below with a positive control and a negative control where applicable.

A zero count is accepted only when the report also identifies the input image and shows a known-good line from the same run. That follows `../MEASUREMENT-DISCIPLINE.md` rules 1, 6, 9, 10 and 14.

### Tier-1 acceptance matrix

| Report item | Hardware-free confirmation the platform team can run | Release gate |
|---|---|---|
| **1 / V-056 — application SMACK labels** | Preserve xattrs in the final image artifact; inspect `security.SMACK64EXEC` for every `/app/bin` executable. In the boot job, compare each application’s `/proc/<pid>/attr/current` with the policy manifest. Run one owner-authored allowed/denied file-access pair after verifying the object labels. | Every covered application has its intended `App::*` label; enforcement remains enabled; the allowed case works and the denied case is denied. No claim is inferred from the projection tar alone. |
| **2 / V-054 — account database** | Resolve `/etc/passwd` and `/etc/shadow`, inspect every path component and mode, and attempt a benign append from a non-root uid in QEMU. Compare `getent passwd` before/after. | Targets are in read-only storage or root-only `/run`; the write fails and NSS output is unchanged. Root is `nologin` in production. |
| **3 / V-055 — Weston configuration** | Resolve `/etc/xdg/weston/weston.ini`, inspect ownership/mode, and parse `shell=`, `backend=` and `ivi-module=`. Start the compositor with the approved file, then confirm that a non-root writer cannot replace it. | File is root-only; every module path is absolute and under the approved signed/read-only directory; approved compositor start succeeds. |
| **3b / V-058 — session-bus environment file** | Parse the 11 named units (`ApplicationLauncher`, `CryptoService`, `MediaBrowser`, `credman`, `mediamanager`, `mof`, `nua`, `ofono`, `remote`, `vbtd`, `watchdogd`) and inspect effective `Environment`/`EnvironmentFile`. Boot and resolve the expected bus names. | No privileged unit reads `/tmp/session_appmgr.env` or another world-writable address source; a non-root-created file cannot influence the address; all expected names still resolve. |
| **4 / V-052 — fail-closed SMACK posture** | Boot three disposable data images: valid encrypted, missing/unrecognised, and corrupt. Record `optUNECE`, `/sys/fs/smackfs/bringup-switch`, audit behavior, and boot disposition. | Valid production data boots enforcing; missing, corrupt or unrecognised data remains enforcing and enters recovery/refuses normal service. No error path relaxes MAC. |
| **5 / V-049 — production serial console** | Static image check: no production getty launch for `ttyS2`, no `ttyS2` in `/etc/securetty`, and no shell-bearing production root account. Boot with QEMU’s serial port attached and inspect processes/output. | No login prompt or `agetty` appears and root remains `nologin`, regardless of missing/invalid MICOM state. |
| **6 / V-042 — privileged `/tmp` markers** | Parse all `.path` units and boot scripts for `PathExists=`/existence tests under `/tmp`. In QEMU as a non-root uid, create the six documented names one at a time while recording unit state; reset between cases. | No privileged unit starts and no security posture changes from an untrusted marker. Supported platform transitions still work through the authenticated replacement channel. |
| **14 / V-063 — default-context D-Bus allows** | XML-parse all 18 system policy files. Allow-list intentional public read-only methods; reject vendor state-changing `context="default"` allows. In QEMU, call `SetSessionState`, lifecycle registration, and `setUsageData` from a non-root uid, then repeat from the authorised identity. | Unauthorised calls return `AccessDenied`; authorised calls retain expected behavior. The top-level system bus remains deny-by-default. |
| **15 / V-064 — service privilege and hardening** | Parse every vendor `.service` effective unit, including drop-ins. Produce counts and exceptions for `User`, `NoNewPrivileges`, `CapabilityBoundingSet`, `ProtectSystem`, `PrivateTmp`, `ReadWritePaths`, `RestrictAddressFamilies` and `SystemCallFilter`; run `systemd-analyze security`. Boot representative media, network, logging, update and telematics services. | No unexplained root service; every exception has an owner and required capability/path evidence; the baseline directives are non-zero and cannot regress. Existing no-setuid/no-setgid and no-world-writable-directory controls remain zero. |
| **16 / V-065 — nine `/etc` anchors** | Resolve and stat all nine paths and every parent directory. Run non-root write/replace attempts and normal consumer smoke tests (NSS, resolver, mount parsing, ECNR startup, compositor startup, image read). | No target is under shared `/tmp`; generated targets are root-owned and minimally readable; all negative writes fail and all positive consumer checks pass. |
| **21 / V-071 — console/SSH marker** | Parse `lib/systemd/esinit` for the old marker and legacy passwd selection; inspect Dropbear units and keys. Boot with debug state absent, invalid and explicitly authorised in separate jobs. | Production never creates `/tmp/secure_console_disable`, never selects `passwd.legacy`, and starts neither console nor SSH. Only the service profile’s authenticated positive state can enable a constrained service. |
| **22 / V-072 — mDNS privilege** | Inspect effective `carplay_mdnsd.service`; boot it on an isolated virtual network; inspect uid, capabilities, mount/tmp isolation and UDP 5353 binding. Send a normal mDNS query as the positive functional check. | `mdnsd` is not root, has no unnecessary capabilities or writable system paths, uses a private tmp, is limited to intended interfaces, and still answers the approved query. No parser vulnerability is implied either way. |
| **23 / V-073 — TCP-to-serial bridge** | Static release check for the two `socat tcp-l:9997` command forms and production feature configuration. Boot manufacturing/TMS states in an isolated network with a pseudoterminal, then inspect listeners and authentication/bind behavior. | Production has no bridge, or it is loopback-only/authenticated according to an explicit requirement. No unauthenticated wildcard listener exists. The test does not infer what a real `/dev/ttyUSB0` would be. |

This matrix needs no project-owned hardware. Static checks run on the release artifact; behavior checks run in the platform team’s QEMU image, updater harness, or reference-board CI. Hardware-only consequences remain separately labelled and cannot be promoted by a passing emulator test.

## 5. What to stop claiming

| Current wording to retire | Honest sentence now | Trace |
|---|---|---|
| **“V-059 provides a downgrade path” and “does not depend on anti-rollback.”** | “FUMO contains separate check and apply opens, creating a candidate check/use flaw. This repository has not shown that both opens use attacker-controlled removable media, nor that an older image passes every later rollback and boot check.” | `../../Ioniq5-VULNERABILITIES.md`, V-059; `../root-access-paths.md`, routes 1 and 12. |
| **V-056’s residual assertion that `_` is exempt and therefore applications are outside SMACK policy.** | “The projection shows application processes labelled `_`; enforcing audit shows `_` can be denied. Production execution labels and the effective `_` rule set remain to be measured on a final unit/image.” | `../../Ioniq5-VULNERABILITIES.md`, V-056; `../REMEDIATION-REPORT.md`, item 1. |
| **“One CA write lets an attacker sign a navigation package the unit accepts” as an established V-069 consequence.** | “The updater manages a group-writable TomTom CA on `/rw_data`; whether navigation-package signature verification actually anchors to that file is not yet demonstrated.” | `../../Ioniq5-VULNERABILITIES.md`, V-069; `../REMEDIATION-REPORT.md`, item 19; `../root-access-paths.md`, route 0. |
| **“Anyone who can reach port 9997 gets a byte pipe” without the runtime qualifier.** | “Two shipped applications contain unauthenticated wildcard-listener command strings; neither command path, listener, reachable interface nor attached device has been demonstrated in a normal production state.” | `../../Ioniq5-VULNERABILITIES.md`, V-073; `../REMEDIATION-REPORT.md`, item 23. |
| **“The VIN leaves twice” for the voice backend.** | “VIN persistence in DLT logs is measured. Forwarding toward SDS is indicated by the function name and direction marker but has not been observed on the wire.” | `../../Ioniq5-VULNERABILITIES.md`, V-074; `../REMEDIATION-REPORT.md`, item 24. |

The first sentence is the most important downgrade. It does not erase V-059’s static evidence; it puts the consequence back behind the runtime observation the entry itself says is missing. That is the standard used elsewhere in this project: an observed string is not an executed path, a projection is not a vehicle, and a negative is valid only after its instrument has produced the corresponding positive.
