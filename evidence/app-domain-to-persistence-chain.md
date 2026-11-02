# App-domain to persistence chain: exact-static boundary

## Scope and conclusion

This note extends the configured AppLauncher result toward the requested
post-entry root and persistence chain. It is offline, exact-build, and
non-operational. No recovered executable, D-Bus method, updater, malformed
input, flash command, target write, or persistence mechanism was executed.

The current result is **not a complete root or custom-firmware chain**. Static
configuration supports a stronger hypothesis than previously recorded: stock
application processes are configured to run as UID/GID zero and, absent a
credential reduction not yet observed at runtime, ordinary Linux 4.1 exec
semantics predict broad permitted/effective capabilities. V-028 can
conditionally change the task's SMACK domain from an `App::*` label to floor
`_` without changing UID. But `_` is not `Privileged`,
`onlycap=Privileged` restricts SMACK override eligibility, and update/boot trust
remain independent gates.

The useful result is therefore a precise chain with explicit stop conditions:

```text
initial stock App::* execution
  -> runtime UID/capability confirmation                    [open]
  -> owner-unit /Request registration and D-Bus delivery   [open]
  -> stable caller-controlled executable object            [open]
  -> V-028 successful QProcess exec                         [open]
  -> floor '_' task label, same UID                         [configured prediction]
  -> explicitly authorized floor-accessible object         [partly mapped]
  -> writable update/persistence anchor                     [open]
  -> authenticated update or direct persistent bytes       [open]
  -> inactive-slot write and activation                     [open]
  -> ABL/MICOM acceptance, health, mark-good, rollback      [open]
```

## Canonical identities

All selected rootfs members in the accompanying exact-static record were read
from the canonical archive through one no-follow file descriptor with pre/post
identity revalidation:

- `work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz`
- size `879109759`
- SHA-256
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`

Key exact artifacts include:

| Artifact | Size | SHA-256 |
|---|---:|---|
| `/lib/systemd/systemd` | 1,552,488 | `a7f5290180223def9e09570edac76f50a1bfe40b63480153daad1f22d54032b5` |
| `/lib/systemd/esinit` | 17,894 | `9f39947ec144322b29c0366bb681f0452ae3696139589bc2f4a2f05bf44afa52` |
| `/etc/init.d/checkroot.sh` | 3,581 | `cd9d224eb1e46cb63271f2dcad166f3147c901b3b023535ab7f1cacf82e4ade2` |
| `/etc/fstab_emmc` | 1,847 | `93c4af1a0ffb0f36c9ff64c6252cfbd950e7615d2f32f85dcab0af17cf9af74e` |
| `/etc/update_start_5w.sh.ori` | 3,933 | `06c3ab7e24b082c24a81299f0627245c0281bc5d519005cd921c13707eb5e838` |
| `/app/bin/AppUpgrade` | 10,787,256 | `5295c6e4c41fb9c03760cf006c58b66fcd11aeb4e6e889af6e31b062549b6df0` |

The recovered kernel remains:

- `work/eu-260128/vmlinux`
- SHA-256
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`
- `cap_bprm_set_creds = 0xffffffff811b85a2`
- `cap_bprm_secureexec = 0xffffffff811b89d6`
- `smack_bprm_set_creds = 0xffffffff811bbee7`
- `smack_privileged = 0xffffffff811bac8c`
- `smack_onlycap = 0xffffffff81c2aad8`
- `smack_known_floor = 0xffffffff81a2fb60`

## 1. Configured UID and capabilities

`ApplicationLauncher.service` has no `User=`, `Group=`,
`SmackProcessLabel=`, `CapabilityBoundingSet=`, `AmbientCapabilities=`,
`NoNewPrivileges=`, or namespace-isolation directive. `AppLauncher.sh` starts
`/app/bin/AppLauncher 3` without changing credentials. Exact AppLauncher imports
`QProcess::start` but no direct `setuid`, `setgid`, `setresuid`, `setresgid`,
`capset`, `setgroups`, or `initgroups` API.

For an ordinary root execution without file capabilities, upstream Linux v4.1
`cap_bprm_set_creds()` derives the permitted set from the old bounding set when
the effective UID is zero, then copies permitted into effective. The recovered
exact function occupies
`[0xffffffff811b85a2, 0xffffffff811b89d6)`. This strengthens the configured
prediction from merely “UID zero” to “UID zero with broad capabilities unless a
separate runtime reduction occurs.”

It does **not** establish the live owner-unit values. Unit generators, vendor
systemd changes, PAM-like helpers, securebits, a reduced manager bounding set,
indirect library behavior, or a different installed build could change the
result. Runtime `CapInh`, `CapPrm`, `CapEff`, `CapBnd`, `NoNewPrivs`,
`Seccomp`, securebits, namespaces, and task labels remain mandatory evidence.

## 2. Why broad Linux capabilities still do not mean SMACK escape

`/etc/smack_setup.sh` writes `Privileged` to
`/sys/fs/smackfs/onlycap`. The recovered `smack_privileged()` requires both the
requested Linux capability and eligibility under `onlycap`. Therefore:

- UID zero is not a SMACK bypass;
- floor `_` is not `Privileged`;
- possession of `CAP_MAC_OVERRIDE` or `CAP_MAC_ADMIN` bits is insufficient for a
  floor task when `onlycap` names another label;
- ordinary DAC, mount, process, module, and raw-I/O capability checks remain
  separate from SMACK access to the affected object.

The recovered rules do give floor reciprocal explicit access to enumerated
application domains, including `App::manager`, `App::navi`,
`App::mediaplayer`, and `App::upgrade`. `App::upgrade` itself has broad rules to
`*`, `_`, and `Privileged`. That makes an authenticated transition into the
upgrade service worth tracing, but it does not collapse floor and
`App::upgrade` into one domain.

## 3. V-028's exact incremental value

The relabel script deletes labels recursively and restores `SMACK64EXEC` only
for an enumerated list. It assigns `App::upgrade` to `AppUpgrade` but omits
systemd, init, `AppLauncher.sh`, and AppLauncher. The recovered kernel retains
the current task label when an executed inode has no execute-label pointer.

Consequently, if all V-028 runtime gates are satisfied and the selected
executable object has no `SMACK64EXEC`, the new task is predicted to retain
AppLauncher's floor `_` label and configured UID zero. This is a
same-UID **SMACK-domain amplification** from `App::*` to `_`; it is not a new UID
escalation and not unrestricted SMACK root.

The executable object must remain stable through AppLauncher's pathname-based
validation and `QProcess` reopen. A caller-controlled string is not proof of a
caller-controlled inode or bytes. DAC, parent-directory search, symlink
resolution, mount namespace, transmutation, `SMACK64`, `SMACK64EXEC`, and
replacement/race state must all be captured or excluded.

## 4. Persistence and custom-firmware boundary

The recovered boot command line uses `root=/dev/mmcblk0p3`, ext4, and
`init=/lib/systemd/esinit` without an explicit `ro` or `rw`. The kernel default
is read-only until userspace remounts it. `checkroot.sh` defaults its root
mode/options to `rw`, but the owner unit's actual boot path and root flags are
unobserved. The selected fstab statically configures `/log_data`, `/update`,
`/voicememo`, `/rw_data`, and three `/Data/*` mounts without a read-only option;
configuration does not prove successful mounts, labels, actual write access, or
useful executable persistence.

The exact kernel configuration lacks dm-verity, IMA appraisal, EVM, and module
signature enforcement. That rejects those named runtime integrity mechanisms
only. It does not prove:

1. the root partition is writable;
2. arbitrary bytes survive update-time relabeling;
3. a modified executable is reached at boot;
4. final partition bytes match bytes previously authenticated;
5. the inactive slot is selected;
6. ABL/MICOM accepts the result;
7. health checks mark it good rather than roll it back; or
8. recovery remains available.

The OEM private signing key is not in the rootfs. The `ABL.oemkm`/`oemkm`
physical-memory handoff, update signature gates, manifest verification, boot
container acceptance, anti-rollback, and mark-good logic remain separate.
Runtime root access could expose or alter mutable public-key/configuration
material, but that is a post-root enabler, not evidence of an OEM-signature
bypass or a bootable custom image.

## 5. Exact systemd version ambiguity

The exact `/lib/systemd/systemd` has Build ID
`f4b6c1c79802cce19d0c0ac0bae3c51a758563ee`. It embeds `systemd 225` banner
strings, while embedded build paths and RPM inventory identify
`systemd-249.3-r0mango134`. Exact relocations include `prctl`, `fsetxattr`,
`lsetxattr`, and `cap_set_proc`, but no `fgetxattr` or `getxattr` relocation was
found.

This ambiguity is a reason not to infer execution-label handling from either
upstream source tree alone. The present credential prediction instead rests on
the shipped unit, scripts, exact imports, recovered-kernel exec semantics, and
explicitly bounded runtime unknowns.

## 6. Passive bench closure

`tools/uk_fw/bench_state_bundle.py` now extends the existing read-only probe to
capture:

- each observed process's `PPid`, `CapInh`, `CapPrm`, `CapEff`, `CapBnd`,
  optional `CapAmb`, optional `NoNewPrivs`, and `Seccomp` fields; stock Linux
  v4.1 lacks the `NoNewPrivs` status line, so absence is explicit rather than a
  collection failure;
- deterministic host-side capability-name decoding through Linux v4.1
  `CAP_AUDIT_READ`, preserving unknown bits;
- `kexec_load_disabled`, `modules_disabled`, `dmesg_restrict`, and
  `mmap_min_addr` when exposed;
- hashes/metadata for systemd, `esinit`, `AppLauncher.sh`, and the relabel
  script; and
- `SMACK64`/`SMACK64EXEC` state for AppLauncher, its script, systemd, `/tmp`, and
  the relabel script in addition to the existing update objects.

The probe is still passive: it does not remount, create a file, call D-Bus,
start a unit, signal a process, change a label, query a modem control plane,
scan a radio, invoke an updater, or execute a recovered target.

One limitation remains deliberate: `/proc/PID/status` does not expose
securebits. Those require an additional already-authorized observation method;
they are not guessed from capability masks.

## Gate table

| Gate | Exact-static status | Runtime evidence needed |
|---|---|---|
| Initial stock app execution | candidate paths exist | exact installed hash, PID, executable, task label |
| UID/GID/groups | configured UID/GID zero | `/proc/PID/status` values |
| Capability sets | broad inheritance predicted | `CapInh/Prm/Eff/Bnd/Amb`, securebits |
| D-Bus reachability | permissive configured session policy | socket/task labels, peer UID, owner, `/Request` registration, delivery |
| Program pathname | V-028 transfers `applocation` | exact request bytes and selected runtime path |
| Executable object | not established | inode/device/mount, parent DAC/SMACK, xattrs, no replacement ambiguity |
| Successful exec | not established | child PID/exe identity and post-exec credentials |
| Floor transition | configured prediction | child task label `_`, executable lacks `SMACK64EXEC` |
| Useful floor access | explicit app-domain rules exist | concrete target object label and successful non-mutating access |
| Writable persistence anchor | configured writable mounts exist | live mount flags, labels, DAC, free space, policy |
| Update trust | several authentic gates recovered | same-object/same-byte continuity through final write |
| Slot activation | partial reset/recovery paths recovered | inactive target, next-boot slot, attempt counters |
| Boot acceptance | unresolved | ABL/MICOM decision, manifest/signature result |
| Health/mark-good | unresolved | health state, mark-good event, rollback behavior |
| Recovery | not tested | dump/restore rehearsal and bounded recovery observation |

## Verdict

The current exact-static chain materially narrows the next work:

- V-028 should be evaluated as a conditional domain transition, not a UID-root
  exploit;
- capability masks are now a first-class runtime gate rather than an unstated
  assumption;
- floor access must be traced to a concrete object before calling it useful;
- custom firmware remains blocked at final-byte authentication, slot activation,
  boot acceptance, health, rollback, and recovery even if runtime UID zero is
  confirmed.

The deterministic evidence record is:

- `evidence/artifacts/application-candidates/app-domain-to-persistence-exact-static.txt`
