# 08 — SMACK and device-node access

**Exact build:** `NE_E.EUR.S5W_L.001.001.260128` — x86-64 Linux **4.1.27**, LSM = SMACK.
**Kernel config facts (this build):** `CONFIG_SECURITY_SMACK=y`,
`CONFIG_SECURITY_SMACK_BRINGUP=y`, `CONFIG_DEFAULT_SECURITY_SMACK=y`,
`CONFIG_DEFAULT_SECURITY="smack"`, `CONFIG_AUDIT=y`, `CONFIG_NETLABEL=y`,
`CONFIG_TMPFS_XATTR=y`, `CONFIG_DEVTMPFS=y`, `CONFIG_DEVTMPFS_MOUNT=y`,
`CONFIG_EXT4_FS_SECURITY=y`, `# CONFIG_SECURITYFS is not set`.

**Scope.** Read-only analysis and offline kernel-source/decompilation guidance only.
No exploit code, no policy-bypass tooling, no device contact.

**Motivation (this device).** The LG keystore driver is built into the kernel
(`keystore_ioctl @ 0xffffffff811c44e0`, `keystore_open @ 0xffffffff811c1747`).
`keystore_open()` performs only `nonseekable_open()` — **no capability check** —
so whether a process can reach `keystore_ioctl()` is decided entirely by (a) the
Unix DAC mode bits on the device node, and (b) the SMACK label of the device node
vs. the SMACK label of the calling process. This note explains SMACK precisely
enough to reason about that device node.

All kernel-source citations below are from the Linux **v4.1** tree, matching the
head-unit kernel version.

---

## 1. Labels, access rules, special labels, transmute

### 1.1 Labels

SMACK labels are unstructured, case-sensitive ASCII strings, compared only for
equality (no hierarchy, no MLS semantics built in). From
`Documentation/security/Smack.txt` and `security/smack/smack.h`:

- Recommended maximum 23 characters (`SMK_LABELLEN = 24` including NUL);
  the long form allows up to 255 (`SMK_LONGLABEL = 256`).
- Labels may not contain unprintable chars, `/`, `\`, `'`, `"`, and may not
  begin with `-` (reserved for options such as `-CIPSO`).
- The only operation performed on labels is string equality; there is no
  sensitivity ordering. A process with the **same label** as an object always
  has full access to it.

The five reserved labels are defined as `struct smack_known` in
`security/smack/smack_access.c`:

| Label | Pronunciation | Meaning |
|---|---|---|
| `_` | floor | Data on the floor: unlabelled/least-sensitive object data. |
| `^` | hat | The unprivileged task label; unlabelled process data. |
| `*` | star | Kernel/privileged data (see the asymmetric subject/object rules below). |
| `?` | huh | Invalid/uninitialised label. |
| `@` | web | Internet/incoming-network data (CIPSO ambient related). |

(There is also an internal empty-string `smack_known_invalid` used when a secid
cannot be resolved.)

### 1.2 Access rules

An access rule is a triple **`subject-label object-label rwxatlb`** (the access
letters are `r` read, `w` write, `x` execute, `a` append, `t` transmute, `l`
lock, `b` bringup; `-` is a placeholder). Rules are stored per-subject-label in
`struct smack_known.smk_rules` and matched by `smk_access_entry()`
(`security/smack/smack_access.c`). The write path that installs a global rule is
`smk_write_rules_list()` → `smk_set_access()` (`security/smack/smackfs.c`):
a new rule is appended; an existing `subject/object` pair has its access bits
**OR-ed in / masked out** (`smk_set_access` does `|= access1; &= ~access2`).

The authoritative decision function is `smk_access()` (`security/smack/smack_access.c`).
The hardcoded checks, in order, are:

1. Subject label `*` → **deny everything** (even with an explicit rule).
2. Object label `@` (web) → **allow any access**; subject label `@` → **allow any
   access** to any object. (Tasks cannot normally obtain `@`.)
3. Object label `*` (star) → **allow any access** to any subject.
4. `subject == object` → **allow any access**.
5. If the request is only read/execute (`MAY_ANYREAD = MAY_READ|MAY_EXEC`) or
   lock (`MAY_LOCK`): a **floor (`_`) object** is readable/executable by any
   subject, and a **hat (`^`) subject** may read/execute/lock any object.
6. An explicit rule in the subject's rule list containing the requested bits →
   allow.
7. Otherwise → **deny**.

`smk_tskacc()` / `smk_curacc()` wrap `smk_access()` and add the capability
override (see §4). Note `smk_access()` itself does **not** apply capabilities.

The `Documentation/security/Smack.txt` whitepaper lists these as seven rules but
omits the `@` case and the lock allowance; treat `smk_access()` source as
authoritative.

### 1.3 Special-label implications for a device node

For a device node (a `struct inode` opened via `/dev/...`), the label that
matters is the inode label from `smk_of_inode()`. Consequences of the hardcoded
rules:

- Device node labelled **`*`** → *any* process can open it at the MAC layer
  (subject/object asymmetry: star **object** is open; star **subject** is denied).
- Device node labelled **`@`** → *any* process, *any* access.
- Device node labelled **`_`** (floor) → any process may read/execute it; write
  requires same-label, an explicit rule, or CAP_MAC_OVERRIDE.
- Device node labelled **`^`** (hat) → a `^`-labelled subject has full
  (same-label) access; other subjects may read/execute/lock it.
- Device node with a **vendor-specific label** (e.g. `System`, `keystore`) →
  governed only by explicit rules + same-label + CAP_MAC_OVERRIDE.

### 1.4 Transmute (`t`) and directory semantics

- A rule may carry `t` (`MAY_TRANSMUTE`). By itself `t` grants nothing; it is a
  flag consulted at inode creation.
- `smack_inode_init_security()` (`security/smack/smack_lsm.c`) is the creation
  hook: when a process (label `S`) creates an object in a directory (label `D`),
  it looks up the rule `S D ...` in the subject's rule list. If that rule
  includes `t` **and** the directory carries the `SMACK64TRANSMUTE=TRUE` xattr
  (`SMK_INODE_TRANSMUTE` flag), the new object is labelled **with the directory's
  label `D`** instead of the creating process's label. (If the new object is a
  directory, the transmute xattr is set on it too.)
- So the transmute rule is written as **`creating-process-label directory-label ...t`**,
  i.e. `subject=creator, object=directory`.

---

## 2. How a device node's label is set (and what a root/unlabelled process sees)

### 2.1 Inode label resolution (`smack_d_instantiate`, `security/smack/smack_lsm.c`)

When an inode is first instantiated, its label comes from, in order of
precedence: the `SMACK64` xattr (if present) → filesystem-specific default →
superblock default (`smk_default`, initially `_`). The filesystem cases that
matter here:

- **tmpfs / devtmpfs** (`TMPFS_MAGIC`): default label is **`*`**, then it falls
  through to try the `SMACK64` xattr. The source comment is explicit: *"Device
  labels should come from the filesystem, but watch out, because they're
  volatile, getting recreated on every reboot."*
- **devtmpfs** `/dev` is backed by shmem/tmpfs
  (`drivers/base/devtmpfs.c::dev_mount()` calls `shmem_fill_super` when
  `CONFIG_TMPFS=y`), so a device node in `/dev` with **no `SMACK64` xattr gets
  label `*`** — i.e. open to every subject at the MAC layer.
- devpts → the creating/attached task's label; procfs → superblock default
  (`_`); smackfs/pipefs/sockfs/cgroupfs → `*`; sockets → `*`.

**Practical consequence:** on this build (`CONFIG_DEVTMPFS_MOUNT=y`), every
`/dev` node is recreated at boot and reverts to `*` unless something re-applies
a `SMACK64` xattr after boot (udev rule, systemd `tmpfiles.d`, or an init
script using `chsmack`/`attr`/`setfattr`). Whether the keystore device node is
labelled at all is therefore a userland policy question, not a kernel default.

### 2.2 xattrs (persistent labels)

Smack stores labels in the `security.*` xattr namespace
(`Documentation/security/Smack.txt`):

- **`security.SMACK64`** — the object's access-control label (the one used for
  a device node).
- `security.SMACK64EXEC` — label a process assumes on `exec()` of this file
  (handled in `smack_bprm_set_creds`).
- `security.SMACK64MMAP` — mmap domain restriction.
- `security.SMACK64TRANSMUTE` — value `TRUE`, marks a directory transmuting.
- `security.SMACK64IPIN` / `security.SMACK64IPOUT` — socket labels.

Setting/removing these requires `smack_privileged(CAP_MAC_ADMIN)` **and** SMACK
write access to the object itself (`smack_inode_setxattr`). Setting `SMACK64`
may use any label including `*`/`@`; `SMACK64EXEC`/`SMACK64MMAP` may **not** be
`*` or `@` (`smack_d_instantiate`, `smack_inode_setxattr`).

### 2.3 smackfs control files (how policy is administered)

From `smk_fill_super()` (`security/smack/smackfs.c`), the files under
`/sys/fs/smackfs/` and their DAC modes:

| File | Purpose | DAC mode |
|---|---|---|
| `load` | add/replace global rule, fixed 24-byte format `subject(24)object(24)rwxat` | 0644 |
| `load2` | add/replace global rule, long-label `subject object rwxat` | 0644 |
| `access` | **query only** — write a rule, read back `1`/`0` (fixed fmt) | 0666 |
| `access2` | query only, long-label form | 0666 |
| `load-self` / `load-self2` | per-task (self-only) rules; can only further restrict | 0666 |
| `change-rule` | modify existing rule: `subject object enable disable` | 0644 |
| `revoke-subject` | zero all rules with a given subject label | 0644 |
| `onlycap` | label required for CAP_MAC_OVERRIDE/ADMIN to be effective (empty = any) | 0644 |
| `ambient` | label applied to unlabelled inbound packets | 0644 |
| `cipso` / `cipso2` | label ↔ CIPSO level/category mapping | 0644 |
| `doi` / `direct` / `mapped` / `netlabel` | CIPSO DOI, direct/mapped levels, single-label hosts | 0644 |
| `logging` | audit state (`0..3`) | 0644 |
| `ptrace` | ptrace policy (`0/1/2`) | 0644 |
| `syslog` | label restricted to `syslog()` | 0644 |
| `unconfined` | (BRINGUP only) a label that bypasses checks | 0644 |

Write handlers gate on `smack_privileged(CAP_MAC_ADMIN)` (so `onlycap` also
applies — see §4) except `access`/`access2` (pure query, no privilege needed)
and `load-self`/`load-self2` (self-restriction only). Reading any of these files
is DAC-only in practice because the smackfs inodes are labelled `*` (any subject
may access a `*` object).

### 2.4 Process labels and the unlabelled/root case

- The init task starts with label **`_`** (floor):
  `smack_init()` → `new_task_smack(&smack_known_floor, ...)`.
- Labels are inherited across `fork()`/`exec()` (`smack_cred_prepare`), and an
  `exec()` may transition via `SMACK64EXEC` (`smack_bprm_set_creds`).
- A process reads its label from `/proc/self/attr/current`
  (`smack_getprocattr`); a process with `smack_privileged(CAP_MAC_ADMIN)` may
  write **its own** label there (`smack_setprocattr`), but never `@`.
- **"Root" is not privileged under SMACK by itself.** Being `uid 0` only helps
  with DAC and capability checks; SMACK treats a `_`-labelled root exactly like
  any other `_`-labelled subject for MAC decisions. If a root process also holds
  `CAP_MAC_OVERRIDE`/`CAP_MAC_ADMIN` (in its capability sets) then the overrides
  in §4 apply — still gated by `onlycap`.
- An **unlabelled process** (one whose label was never set) is `_` (floor) by
  inheritance from init. An **unlabelled device node** (no `SMACK64` xattr) on
  devtmpfs is `*`, which is accessible to every subject.

---

## 3. Read-only enumeration of the running policy

Everything below is read-only; `access`/`access2` writes are query transactions
that do not modify policy. (This device has `# CONFIG_SECURITYFS is not set`, so
smackfs is **not** under `/sys/kernel/security` — it is its own mount at
`/sys/fs/smackfs`.)

1. **Is smackfs mounted?** `cat /proc/mounts | grep smackfs` (or `mount | grep smack`).
   If absent, no runtime policy readout via smackfs is available.
2. **Full rule set:** `cat /sys/fs/smackfs/load2` (long form) and
   `cat /sys/fs/smackfs/load` (24-byte form). `smk_rule_show()` hides rules whose
   labels are too long for the interface and rules with zero access bits.
3. **Per-process label:** `cat /proc/<pid>/attr/current` and `/proc/self/attr/current`.
4. **onlycap:** `cat /sys/fs/smackfs/onlycap` (empty = capabilities effective for
   any label).
5. **ambient:** `cat /sys/fs/smackfs/ambient`.
6. **unconfined (BRINGUP):** `cat /sys/fs/smackfs/unconfined` (empty = not set;
   **non-empty is a full bypass for that label**).
7. **ptrace policy:** `cat /sys/fs/smackfs/ptrace` (0 default, 1 exact, 2 draconian).
8. **syslog label:** `cat /sys/fs/smackfs/syslog`.
9. **logging state:** `cat /sys/fs/smackfs/logging` (0 off, 1 denied, 2 accepted,
   3 both).
10. **CIPSO/netlabel:** `cat /sys/fs/smackfs/doi`, `direct`, `mapped`, `cipso2`,
    `netlabel`.
11. **Policy oracle (query, no change):** write `subject object rwxat` to
    `/sys/fs/smackfs/access2`, read back `1` (permitted by `smk_access`) or `0`
    (denied). Note this reports the **MAC decision only**, without the
    CAP_MAC_OVERRIDE override.
12. **Object labels on disk:** `getfattr -n security.SMACK64 <path>` (and
    `SMACK64EXEC`/`SMACK64MMAP`/`SMACK64TRANSMUTE`) for any readable filesystem —
    especially `/dev/<node>` and `/etc`/`/system` if a rootfs is mounted.
    (Requires CAP_MAC_ADMIN to *set*, but reading is ordinary `getxattr`.)
13. **Startup policy files (if present):** `cat /etc/smack/accesses` (rules
    loaded at boot), `/etc/smack/cipso` (CIPSO map). The `smackutil` tools
    (`chsmack`, `smackctl`, `smackaccess`) are optional userland helpers, not
    required for the kernel policy.
14. **Kernel static policy hints:** `CONFIG_SECURITY_SMACK_BRINGUP=y` means the
    `unconfined` and `b`-rule machinery is compiled in; check whether it is
    actually used at runtime via (6) and any `b`-flagged rules in (2).

**DAC note:** the smackfs files are 0644/0666 and the smackfs inodes are `*`
(open to all), so an unprivileged process can read the entire policy and use the
`access2` oracle — SMACK does not hide its own policy.

---

## 4. DAC vs SMACK, and CAP_MAC_OVERRIDE / CAP_MAC_ADMIN

**SMACK combines with (restricts) DAC; it never overrides DAC.** In Linux 4.1
the permission order is fixed in `fs/namei.c::__inode_permission()`:

1. `IS_IMMUTABLE` check,
2. DAC: `do_inode_permission()` (mode bits / ACLs),
3. device cgroup (`devcgroup_inode_permission`),
4. LSM: `security_inode_permission()` → `smack_inode_permission()`.

A device open therefore needs **both** the DAC mode bits (or `CAP_DAC_OVERRIDE`
for r/w, `CAP_DAC_READ_SEARCH` for read/search) **and** SMACK approval. SMACK
capabilities do not relax DAC, and DAC capabilities do not relax SMACK.

SMACK's own capability handling is in `security/smack/smack.h::smack_privileged()`:

```
smack_privileged(cap) = capable(cap) && (onlycap == NULL || onlycap == current_label)
```

- **CAP_MAC_OVERRIDE** — bypasses a SMACK denial. Applied in
  `smk_tskacc()`/`smk_curacc()` (the wrapper used by `smack_inode_permission`
  and `smack_file_ioctl`) and directly in `smack_file_open()` (which returns 0
  early if `smack_privileged(CAP_MAC_OVERRIDE)`). Effective only if `onlycap` is
  empty or matches the process label.
- **CAP_MAC_ADMIN** — required (via `smack_privileged`) to change SMACK data:
  write rules (`load`/`load2`/`change-rule`/`revoke-subject`), set labels via
  xattr or `/proc/self/attr/current`, set `onlycap`/`ambient`/`unconfined`/etc.
  Also gated by `onlycap`.
- **onlycap** — if set to label `L`, then `CAP_MAC_OVERRIDE`/`CAP_MAC_ADMIN`
  have effect only for processes whose label is exactly `L`. Default (empty) =
  capabilities effective for any label. `smk_write_onlycap()` additionally
  requires that once set, only a process already holding the `onlycap` label can
  change or clear it.

**Hook-level detail relevant to a device node** (all in `security/smack/smack_lsm.c`):

- `smack_inode_permission()` masks the request to `MAY_READ|MAY_WRITE|MAY_EXEC|
  MAY_APPEND` and calls `smk_curacc(inode_label, mask)`. This is the main open-time
  MAC gate (read for O_RDONLY, write for O_WRONLY, both for O_RDWR).
- `smack_file_open()` additionally requires `MAY_READ` on the inode **regardless
  of open mode** (or `smack_privileged(CAP_MAC_OVERRIDE)`). So even O_WRONLY
  requires read access at the MAC layer.
- `smack_file_ioctl()` re-checks per ioctl direction bits: `_IOC_WRITE` →
  `MAY_WRITE`, `_IOC_READ` → `MAY_READ`. The keystore ioctl codes observed
  (`0xc00837ca`, `0xc0183706`, `0xc15837cb`, …) all carry `_IOC_READ|_IOC_WRITE`,
  so each `keystore_ioctl()` call needs **read+write** SMACK access to the device
  node (or CAP_MAC_OVERRIDE).
- `smack_file_permission()` returns 0 — already-open fds are not re-checked by
  SMACK (see §6).

**Net for the keystore device:** the open handler's lack of a capability check is
only half the story. Reaching `keystore_ioctl()` requires, absent
CAP_MAC_OVERRIDE (with `onlycap`), SMACK read+write on the device inode. If the
node is `*`/`@` (or the process shares its label / has an explicit rule), the MAC
layer is satisfied and only DAC mode bits remain.

---

## 5. Functions worth decompiling (symbols + expected insight)

Symbols and addresses are from this build's `work/eu-260128/kallsyms_fixed.tsv`.
Addresses are KASLR-free (no KASLR on this kernel), so they are the runtime
addresses. Decompiling these confirms the default labels/rules and the exact
access logic used by the shipped kernel rather than relying on upstream v4.1
source.

**Core decision logic (in `smack_access.c`):**

| Function | Address | Expected insight |
|---|---|---|
| `smk_access` | 0xffffffff811c7e1a | The hardcoded label comparisons (§1.2). Confirm the shipped kernel has the same star-object/web/floor/hat/same-label allowances; confirm no vendor modification. |
| `smk_access_entry` | 0xffffffff811c7d93 | Rule lookup: which list is searched and how `MAY_WRITE⇒MAY_LOCK` is derived. Confirms rules live per-subject-label. |
| `smk_tskacc` | 0xffffffff811c7e22 | Where `CAP_MAC_OVERRIDE` (via `smack_privileged`) is applied on top of `smk_access`. |
| `smk_curacc` | 0xffffffff811c7e2d | Current-task wrapper used by inode/file hooks. |
| `smk_import_entry` / `smk_find_entry` / `smk_insert_entry` | 0xffffffff811c8682 / 0xffffffff811c8127 / 0xffffffff811c7e57 | Label internment and secid assignment; confirms no label deletion (labels are never removed). |
| `smk_parse_smack` | 0xffffffff811c83d8 | Label validity rules (charset, leading `-`, length). |

**smackfs policy interface (in `smackfs.c`):**

| Function | Address | Expected insight |
|---|---|---|
| `smk_write_load` / `smk_write_load2` | 0xffffffff811cd733 / 0xffffffff811cd6d6 | Rule-install path and its `CAP_MAC_ADMIN` gate; exact accepted format. |
| `smk_set_access` | 0xffffffff811cd489 | Rule add/replace semantics (`\|=` then `&= ~`) and where global rules are stored. |
| `smk_write_rules_list` | 0xffffffff811cd51a | Shared parser for load/load2/load-self/change-rule; per-subject vs per-task list routing. |
| `smk_write_change_rule` | 0xffffffff811cd622 | Rule mutation semantics (enable/disable masks). |
| `smk_write_revoke_subj` | 0xffffffff811cd7ff | Rule revocation; used to infer which subjects can be neutered. |
| `smk_write_onlycap` / `smk_read_onlycap` | 0xffffffff811cd846 / 0xffffffff811cbffb | onlycap set/clear semantics and current value; directly affects whether CAP_MAC_OVERRIDE/ADMIN work. |
| `smk_write_ambient` / `smk_read_ambient` | 0xffffffff811cd351 / 0xffffffff811cc29d | Network ambient label. |
| `smk_write_unconfined` / `smk_read_unconfined` | 0xffffffff811cd9f1 / 0xffffffff811cb7b6 | BRINGUP unconfined label — full-bypass indicator if non-empty. |
| `smk_write_access` / `smk_write_access2` / `smk_user_access` | 0xffffffff811cdb13 / 0xffffffff811cda8d / 0xffffffff811cda69 | The policy query oracle; confirm it performs no privilege check. |
| `smk_rule_show` | 0xffffffff811cc5b1 | What `load`/`load2` actually print (hidden/zero rules). |
| `smk_fill_rule` / `smk_parse_long_rule` / `smk_perm_from_str` | 0xffffffff811c9883 / 0xffffffff811c98aa / 0xffffffff811c8abb | Rule parsing and access-string→bitmap mapping. |

**LSM hooks (in `smack_lsm.c`):**

| Function | Address | Expected insight |
|---|---|---|
| `smack_d_instantiate` | 0xffffffff811c73c6 | **The device-node default-label logic** — confirm the `TMPFS_MAGIC → *` fallthrough and devtmpfs behaviour in the shipped kernel. |
| `smack_inode_permission` | 0xffffffff811c2b72 | Open-time MAC gate; exact request masking. |
| `smack_file_open` | 0xffffffff811c6256 | The unconditional `MAY_READ` (or CAP_MAC_OVERRIDE) requirement on every open. |
| `smack_file_ioctl` | 0xffffffff811c2553 | Per-direction-bit re-check; decisive for `keystore_ioctl` reachability. |
| `smack_file_permission` | 0xffffffff811c025b | Confirm it is a no-op (open-fd non-remediation). |
| `smack_inode_init_security` | 0xffffffff811c3219 | Transmute application logic (§1.4). |
| `smack_inode_setxattr` / `smack_inode_post_setxattr` | 0xffffffff811c3421 / 0xffffffff811c2073 | Who may set `SMACK64`, and how the inode label is swapped. |
| `smack_sb_kern_mount` / `smack_sb_copy_data` / `smack_sb_alloc_security` | 0xffffffff811c79ca / 0xffffffff811c3613 / 0xffffffff811c6fcf | Mount options (`smackfsdef=`, `smackfsroot=`, …) and superblock default labels. |
| `smack_bprm_set_creds` / `smack_bprm_committing_creds` / `smack_bprm_secureexec` | 0xffffffff811c390e / 0xffffffff811bfc6f / 0xffffffff811c374b | SMACK64EXEC transition rules and setuid handling. |
| `smack_cred_prepare` / `smack_cred_transfer` | 0xffffffff811c71c7 / 0xffffffff811c0d45 | Label inheritance across fork/exec. |
| `smack_kernel_act_as` / `smack_kernel_create_files_as` | 0xffffffff811c1204 / 0xffffffff811c0569 | Kernel-internal label assignment (e.g. what label kernel-created files get). |
| `smack_getprocattr` / `smack_setprocattr` | 0xffffffff811c1ee1 / 0xffffffff811c58af | `/proc/self/attr/current` read/write; confirms `@` is rejected and only-self is allowed. |
| `smack_privileged` | 0xffffffff811c1a06 (inline; constprop clone 0xffffffff811ccc84) | The exact onlycap gate for both capabilities. |
| `smk_fetch` | 0xffffffff811c7251 | xattr fetch used by `smack_d_instantiate`. |

Decompilation priority for the keystore question: `smack_d_instantiate`,
`smack_inode_permission`, `smack_file_open`, `smack_file_ioctl`, `smk_access`,
`smk_tskacc`, `smack_privileged`, `smk_read_onlycap`.

---

## 6. Known SMACK issues and public discussion

No widely-cited, SMACK-specific memory-safety CVE against 4.1 was identified in
the public record during this review; SMACK is niche and most published findings
are configuration/design observations rather than code defects. The relevant
documented weaknesses/gaps for a device-node analysis are:

1. **Empty `onlycap` is the default.** Until `onlycap` is set, `CAP_MAC_OVERRIDE`
   and `CAP_MAC_ADMIN` are effective for any label that holds them — so any
   capable root process (or any process retaining those caps) bypasses MAC
   entirely. A non-empty `onlycap` should be verified at runtime (§3.4).
2. **devtmpfs/tmpfs device nodes default to `*`.** `smack_d_instantiate` labels
   unlabelled tmpfs inodes `*`, and `/dev` is devtmpfs (tmpfs-backed). A `*`
   object is accessible to every subject (§1.3). Relabeling is volatile across
   reboot and depends on userland re-application. This is the single most
   important configuration risk for the keystore node.
3. **Star-object / web-object / floor-read / hat-read allowances.** The hardcoded
   `smk_access` rules make any object labelled `*` or `@` fully open, and `_`
   objects readable/executable by anyone. Same-label always grants full access,
   so SMACK provides **no confidentiality within a label** (it is not BLP/MLS).
4. **BRINGUP `unconfined` is compiled in.** `CONFIG_SECURITY_SMACK_BRINGUP=y`
   means the `unconfined` interface exists and, if set to a label, that label's
   subjects may access any object and any subject may access objects with that
   label (with audit logging). `Smack.txt` warns it "should never be used in
   production." Confirm it is empty at runtime (§3.6).
5. **No re-check of open file descriptors.** `smack_file_permission()` returns 0;
   an fd opened before a label/policy change remains usable, and only the ioctl
   direction-bit re-check (§4) and the `file_open` hook gate new opens. For a
   device kept open across a label change, ioctls are still re-checked by
   `smack_file_ioctl`.
6. **Hook-coverage limits.** SMACK enforces only what its registered
   `security_operations` hooks cover; operations without a hook (or hooks that
   return 0) are unmediated. The LSM is an additional restriction layer, not a
   replacement for DAC, so DAC weaknesses (e.g. world-writable `/dev` node,
   `CAP_DAC_OVERRIDE`) are orthogonal entry conditions.
7. **Public research landscape.** The authoritative references are
   `Documentation/security/Smack.txt` and the `security/smack/` sources (cited
   throughout), plus the smack-team userland at `github.com/smack-team/smack`.
   Automotive-IVI research in this project's corpus (e.g. the KOFFEE report
   IIT TR-20/2020, `evidence/child-notes/artifacts/`) concerns a Kia *Android*
   head unit and is not SMACK-specific. Treat "SMACK bypass" claims with
   scepticism unless they name a specific hook or configuration; most real-world
   findings reduce to items 1–5 above.

---

## References

- `Documentation/security/Smack.txt` (Linux v4.1) — labels, access rules,
  smackfs file list, xattrs, mount options, privilege, bringup/unconfined.
- `security/smack/smack.h` (v4.1) — `SMK_LABELLEN`/`SMK_LONGLABEL`, `MAY_*`,
  `smack_privileged()`, `struct smack_known`/`smack_rule`, `smk_of_inode`.
- `security/smack/smack_access.c` (v4.1) — `smack_known_*` labels, `smk_access`,
  `smk_access_entry`, `smk_tskacc`, `smk_curacc`.
- `security/smack/smack_lsm.c` (v4.1) — `smack_d_instantiate`,
  `smack_inode_permission`, `smack_file_open`, `smack_file_ioctl`,
  `smack_file_permission`, `smack_inode_init_security`, `smack_inode_setxattr`,
  `smack_bprm_set_creds`, `smack_cred_prepare`, `smack_kernel_act_as`,
  `smack_kernel_create_files_as`, `smack_getprocattr`/`smack_setprocattr`,
  `smack_init`.
- `security/smack/smackfs.c` (v4.1) — `smk_fill_super`, `smk_write_load`,
  `smk_write_load2`, `smk_set_access`, `smk_write_change_rule`,
  `smk_write_revoke_subj`, `smk_write_onlycap`, `smk_write_ambient`,
  `smk_write_unconfined`, `smk_user_access`, `smk_read_*`, `smk_rule_show`.
- `fs/namei.c` (v4.1) — `__inode_permission()` DAC→devcgroup→LSM order.
- `drivers/base/devtmpfs.c` (v4.1) — `dev_mount()` → `shmem_fill_super` (tmpfs
  backing for `/dev`).
- This build's `work/eu-260128/kernel.config` and `kallsyms_fixed.tsv` — config
  and symbol addresses.
- Companion evidence: `evidence/eu-kernel-decompilation.md`,
  `evidence/eu-kernel-symbol-recovery-and-trust-chain.md` (keystore open/ioctl
  analysis and access-control unknowns).

---

## Read-only enumeration checklist

Run each item without modifying state; `access`/`access2` writes are queries.

**A. Static / offline (no device contact):**

- [ ] Confirm config: `CONFIG_SECURITY_SMACK=y`, `CONFIG_DEFAULT_SECURITY="smack"`,
      `CONFIG_SECURITY_SMACK_BRINGUP=y`, `CONFIG_DEVTMPFS_MOUNT=y`,
      `CONFIG_TMPFS_XATTR=y`, `CONFIG_AUDIT=y`, `# CONFIG_SECURITYFS is not set`.
- [ ] Decompile `smack_d_instantiate`, `smk_access`, `smack_inode_permission`,
      `smack_file_open`, `smack_file_ioctl`, `smk_read_onlycap` (addresses in §5)
      and compare against upstream v4.1 for vendor changes.
- [ ] From a recovered/plaintext rootfs: list `/dev` nodes and any
      `security.SMACK64` values applied by init/udev/systemd/tmpfiles; read
      `/etc/smack/accesses` and `/etc/smack/cipso` if present.

**B. Runtime (read-only, if a shell is available):**

- [ ] `cat /proc/mounts | grep -i smack` — is `/sys/fs/smackfs` mounted?
- [ ] `cat /sys/fs/smackfs/load2` (and `load`) — dump all rules.
- [ ] `cat /proc/self/attr/current` and `for p in /proc/[0-9]*; do cat $p/attr/current; done`
      — per-process labels.
- [ ] `cat /sys/fs/smackfs/onlycap` — empty vs set.
- [ ] `cat /sys/fs/smackfs/ambient`, `unconfined`, `ptrace`, `syslog`, `logging`.
- [ ] `cat /sys/fs/smackfs/doi`, `direct`, `mapped`, `cipso2`, `netlabel`.
- [ ] Query oracle (no policy change):
      `echo "<subj> <obj> rw" > /sys/fs/smackfs/access2; cat /sys/fs/smackfs/access2`
      (returns `1`/`0`). Repeat for the keystore node label × candidate process
      labels × `r`, `w`, `rw`, `x`.
- [ ] `getfattr -n security.SMACK64 /dev/<keystore-node>` (and any other device
      node under test); also `SMACK64EXEC`/`SMACK64MMAP`/`SMACK64TRANSMUTE`.
- [ ] Record the keystore node's DAC mode and ownership (`ls -l /dev/<node>`,
      `stat`), and the calling process's uid/gid and capability sets
      (`/proc/<pid>/status` CapEff) to determine the DAC/CAP_DAC_OVERRIDE half of
      the gate.
- [ ] Cross-check: label + mode + rules → expected SMACK decision for the ioctl's
      `_IOC_READ|_IOC_WRITE` request, using §1.2/§4.

**C. Interpretation for the keystore device:**

- [ ] If node label is `*`/`@` → SMACK is satisfied for everyone (DAC only).
- [ ] If node label is `_` → read/exec open to all; write needs rule/same-label/CAP_MAC_OVERRIDE.
- [ ] If node label is vendor-specific → need explicit rule, same label, or CAP_MAC_OVERRIDE (gated by `onlycap`).
- [ ] If `onlycap` empty and process holds CAP_MAC_OVERRIDE → SMACK bypassed.
- [ ] If `unconfined` set and matches process label → SMACK bypassed (BRINGUP).
