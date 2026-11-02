# AppLauncher configured credential and SMACK chain

## Result

The recovered EU `260128` configuration and exact recovered kernel close an
important part of V-028's privilege boundary. The stock installation predicts:

```text
initial task floor "_"
  → systemd floor
  → AppLauncher.sh floor, configured uid/gid 0/0
  → AppLauncher floor, configured uid/gid 0/0
  → successful direct-route QProcess exec retains floor
     when the executable has no SMACK64EXEC
```

The canonical rootfs archive contains no xattr-carrying PAX record. The stock
rootfs relabel sequence first removes access/execute attributes recursively and
then restores `SMACK64EXEC` only for enumerated applications. It labels
`AppUpgrade` as `App::upgrade`, but does not enumerate `AppLauncher`,
`AppLauncher.sh`, systemd, or `/sbin/init`. The exact recovered kernel changes a
task label on exec only when the inode's execute-label pointer is non-null.

This is an **exact-static configured same-uid application-domain-to-floor
transition candidate**, not a runtime-demonstrated unrestricted-root chain.
`smack_setup.sh` writes `Privileged` to `smackfs/onlycap`, so a floor task does
not gain the SMACK capability override merely from uid zero. Runtime Request
registration/delivery, writable executable identity at exec, successful
`QProcess` execution, effective capabilities, owner-unit labels, update-anchor
access, persistence, and boot acceptance remain unobserved.

Exact evidence:
`evidence/artifacts/application-candidates/applauncher-configured-privilege-chain-exact-static.txt`.

## Canonical archive and xattr provenance

Canonical rootfs:

- path: `work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz`;
- size: `879109759`;
- SHA-256: `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
- members: `66836`;
- normalized inventory SHA-256:
  `c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94`.

A stable no-follow descriptor scan found only:

- `55624` regular entries;
- `7208` symlinks;
- `4004` directories.

None of the `66836` members has a PAX header, xattr key, or SMACK key. Selected
canonical metadata is:

| Member | Type/mode | Owner | Link |
|---|---:|---:|---|
| `./sbin/init` | symlink `0777` | `0:0` | `/lib/systemd/systemd` |
| `./lib/systemd/systemd` | regular `0755` | `0:0` | — |
| `./app/bin/AppLauncher` | regular `0755` | `0:0` | — |
| `./app/bin/AppLauncher.sh` | regular `0755` | `0:0` | — |
| `./app/bin/AppUpgrade` | regular `0755` | `0:0` | — |
| `./tmp` | directory `01755` | `0:0` | — |

Mutable host extraction cannot prove target xattrs. Here the archive result is
positive: no xattr metadata exists to preserve. Installed labels must therefore
come from relabeling/runtime behavior.

## Stock delete-then-restore relabeling

For a rootfs target, `/etc/update_start_5w.sh.ori` calls, in order:

1. `delete_dir_label "${TARGET_DIR}"`;
2. `app_remove_label`;
3. `app_labeling ${TARGET_DIR}`;
4. `app_usr_labeling ${TARGET_DIR}`;
5. `app_usr_bin_labeling ${TARGET_DIR}`;
6. explicit `Privileged` labeling of the update anchor.

`delete_dir_label` sets the target access label to floor `_` and recursively
removes access and execute attributes using `chsmack -r -A -E`. The three
application helpers then set execute labels for fixed lists. Those lists contain
`AppUpgrade App::upgrade`, but no `AppLauncher`, `AppLauncher.sh`, systemd, or
init entry.

An exact-name absence alone would be weak. The stronger conclusion here comes
from the ordered operation: recursive execute-label deletion followed by an
enumerated restore that omits the launcher chain.

## Exact recovered-kernel behavior

Recovered `vmlinux`:

- SHA-256:
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`.

Recovered kallsyms binds `smack_known_floor` to
`0xffffffff81a2fb60` and `smack_onlycap` to `0xffffffff81c2aad8`. It also
binds:

| Function | Address |
|---|---:|
| `smack_privileged` | `0xffffffff811bac8c` |
| `smack_inode_init_security` | `0xffffffff811bb83a` |
| `smack_bprm_set_creds` | `0xffffffff811bbee7` |
| `smack_cred_prepare` | `0xffffffff811bd979` |
| `smack_inode_alloc_security` | `0xffffffff811bdddd` |
| `smack_init` | `0xffffffff81b1d754` |

Homebrew LLVM disassembly shows `smack_init` passing the same label pointer as
both task-label arguments to the task-Smack allocator, then storing the result
in the initial credential security field. This matches the authoritative Linux
v4.1 source's initialization to `smack_known_floor`.

In exact `smack_bprm_set_creds`:

- `0xffffffff811bbf26..0xffffffff811bbf2b` obtains the inode's execute-label
  pointer;
- `0xffffffff811bbf30..0xffffffff811bbf33` returns without a transition when
  that pointer is null;
- the transition path writes the execute label into the new credential at
  `0xffffffff811bbf8b..0xffffffff811bbf92`.

Thus absent `SMACK64EXEC` retains the inherited task label. A non-null execute
label is the transition mechanism.

Exact `smack_inode_alloc_security` calls the current-label helper and passes its
result into the new inode-Smack allocator. In the absence of a matching
transmuting-directory rule, a newly created file starts with its creator's task
label. This matters because an app-created file need not be floor-labeled for
the floor launcher to execute it: the recovered floor policy grants `_` `rwx`
to the enumerated `App::*` object labels.

Finally, exact `smack_privileged` requires both `capable(cap)` and either no
`smack_onlycap` value or equality between the current label and
`smack_onlycap`. The recovered setup writes `Privileged` to `onlycap`. UID 0,
`CAP_MAC_OVERRIDE`, and floor label must therefore not be collapsed into one
notion of unrestricted access.

## Configured uid and capability boundary

`ApplicationLauncher.service` has:

- `ExecStart=/app/bin/AppLauncher.sh`;
- no `User=` or `Group=`;
- no `SmackProcessLabel=`;
- no per-unit capability bounding, `NoNewPrivileges`, `SecureBits`, namespace,
  or credential-reduction directive.

`AppLauncher.sh` executes `/app/bin/AppLauncher 3&` and performs no credential
or label change. Exact AppLauncher identity is:

- size: `407720`;
- SHA-256:
  `c8d6d56bc254ad0731e81f40bd83aa9b3be6b49bcbd8efb291157a06c4a84268`;
- GNU Build ID: `0452df1033bd1bbae15727a83d4d56576d8b9444`.

It imports the relevant `QProcess::start` overloads and no direct `setuid`,
`setgid`, `setresuid`, `setresgid`, `capset`, `setgroups`, `initgroups`,
`prctl`, `chroot`, `unshare`, or `setns` API. Configuration therefore predicts
uid/gid zero inheritance into launcher children. It does not replace a runtime
credential/capability observation, and library-internal or indirect behavior is
not excluded merely by import absence.

The same distinction applies to capabilities. No unit directive reduces them,
but the effective/permitted/bounding/ambient sets were not captured from an
owner unit. Moreover, SMACK's `onlycap` independently limits the MAC override.

## Session-bus reachability

`Dbuslaunch.service` also has no `User=`, `Group=`, or `SmackProcessLabel=` and
starts `/app/bin/Dbuslaunch.sh`. That script launches:

```text
dbus-daemon --session --print-address --fork
```

The recovered `session.conf`:

- listens on `unix:tmpdir=/tmp`;
- permits only `EXTERNAL` authentication;
- default-allows send, receive/eavesdrop, and ownership;
- has no recovered `session.d` restriction.

The daemon and launcher are therefore configured under uid zero and the floor
inheritance chain. Applications started by AppLauncher are also configured to
retain uid zero while their labeled executables transition them to their
`App::*` domains. This predicts same-daemon-uid `EXTERNAL` eligibility for stock
launcher children, not arbitrary non-root access.

Recovered policies contain both:

```text
App::<domain> _ rwx...
_ App::<domain> rwx---
```

for the relevant HMI domains, including manager, navigation, media player, and
upgrade. These rules predict application-domain access to floor-labeled
session-bus objects and floor-launcher execute access to app-labeled objects.
Canonical `/tmp` mode is `01755`; configured uid-zero application children are
the directory owner for DAC purposes.

Saved isolated-VM logs additionally show ownership and traffic for
`com.lge.avn.applauncher`. Static startup attempts service ownership at
`0xbb21..0xbb2f`, while Request constructor `[0x26250,0x26333)` attempts to
register `/Request` with `ExportAdaptors`. No adaptor-level sender authorization
was found. The saved run did not prove successful `/Request` registration, and
no request was sent for this assessment.

## What V-028 now predicts

V-028 already proves that the D-Bus `applocation` value reaches the program
field and that the on-demand path selects a direct `QProcess::start` branch that
bypasses both identified executable verifier calls.

Combining that result with the exact kernel/configuration record predicts:

1. a stock application process is same-bus uid zero but runs under an `App::*`
   task label;
2. the application/floor policy permits access to floor objects, while a newly
   created executable normally receives the creator's `App::*` label;
3. floor AppLauncher has explicit execute access to that app label;
4. a delivered direct-route request reaches a root/floor QProcess start attempt;
5. successful exec of an object with no `SMACK64EXEC` retains the launcher's
   floor task label and configured uid zero.

This closes the configured label prediction but not the dynamic gates.
Importantly, a compromised stock app is already configured uid zero and has an
explicit `App::* → _` `rwx` rule. The defensible incremental effect of the
launcher route is a transition to floor and corresponding access to other
explicitly enumerated application domains—not a newly demonstrated uid-zero
transition.

## Remaining chain gates

The following remain unproved:

- owner-unit `/Request` registration and method delivery;
- sender identity beyond same-uid bus authentication;
- runtime task/socket/file labels and transmute state;
- pathname/object stability through the `QProcess` exec;
- QProcess acceptance and successful `execve`;
- actual child uid/gid, supplementary groups, capability sets, namespaces, and
  securebits;
- access from floor to non-floor `Data::*`, `System::*`, `Privileged`, or other
  labels without an explicit rule;
- transition to `Privileged` under `onlycap`;
- writable update trust anchors, authenticated-byte substitution, partition
  writes, slot activation, boot acceptance, health/mark-good, rollback, or
  persistence.

Floor `_` is powerful in this policy, but it is not synonymous with
`Privileged`, universal SMACK override, accepted firmware, or persistence.

## Safety boundary

No D-Bus request, executable, script, payload, target process, filesystem write,
credential change, label change, mount, update, partition operation, flash,
slot change, boot action, or persistence mechanism was created or attempted.
