# One flaw shape, six findings: trust anchors placed in writable runtime paths

The most useful thing this project has produced is not any single vulnerability — it is that five separate findings are the **same
mistake**. In each, a security decision is resolved from state that lives somewhere the threat model says is untrusted: a tmpfs file, a
world-writable parameter, or an unauthenticated probe. None of them is a memory-corruption bug, and fixing the shape fixes all five
cheaply.

| # | Decision being made | Resolved from | State |
| --- | --- | --- | --- |
| V-048 | may this binary run as **root**? | PEM key at `/tmp/app_normal.key`, trusted over the pinned Qt resource | **a binary we signed ran as uid 0** |
| V-049 | is the root **console open**? | `/sys/module/micom/parameters/secure_console` (writable, default 0) | **login prompt captured** |
| V-052 | is **MAC enforced**? | `cryptsetup isLuks` on the data partition → `optUNECE` → `smack bringup-switch` | value measured 0 (permissive) |
| V-053 | is **data protected**? | the literal passphrase `1234` in `/etc/fde_test_v2.sh` | **opens with `1234`, refuses a wrong one** |
| V-055 | which **compositor modules load as root**? | `/etc/xdg/weston/weston.ini -> /tmp/weston.ini`, naming `shell=`, `backend=`, `ivi-module=` | file present; takes effect at next compositor start |
| V-054 | which **accounts exist**, and does root get a shell? | `/etc/passwd` and `/etc/shadow` are **symlinks into `/tmp`**, rebuilt from a flag at boot | file copy from `/etc/passwd.{legacy,secure}` |
| V-058 | **which D-Bus does the whole application ecosystem use?** | `/tmp/session_appmgr.env`, read by **eleven** units through `EnvironmentFile=` | confirmed from the units; would redirect every app's bus |

## The V-054 instance in detail

```
/etc/passwd -> /tmp/passwd
/etc/shadow -> /tmp/shadow
```

and `/lib/systemd/esinit` reconstructs them at every boot:

```sh
ln -s /etc/shadow.Global /tmp/shadow
...
if [ -f /tmp/secure_console_disable ]; then
        cp /etc/passwd.legacy /tmp/passwd     # root:x:0:0:root:/home/root:/bin/sh
else
        cp /etc/passwd.secure /tmp/passwd     # root:x:0:0:root:/home/root:/usr/sbin/nologin
fi
```

Three consequences:

1. **The console-shell policy is a file copy into tmpfs.** "Secure console" does not remove a capability; it copies a different text file
   into a writable location that `/etc/passwd` happens to point at. The default copy grants root `/bin/sh`.
2. **The account database is writable by anything that can write `/tmp`.** Any process that can write there can add a uid-0 entry or
   alter root's shell mid-session, and the next NSS lookup — by the console `agetty`, or by any service that resolves a name to a uid —
   sees the attacker's file. On this image every vendor process is already root, so the immediate gain is small; the point is that a
   *single* non-root `tmp` write, from any future sandbox or lesser-privileged component, becomes account takeover rather than nothing.
3. **It composes with V-049.** The console login is enabled by default and authenticates against `/etc/shadow` → `/tmp/shadow`. A writable
   account database plus an enabled console is a different proposition from either alone.

## Why this framing is worth the vendor's attention

Each individual item can be argued down in isolation ("a key in /tmp is fine if nothing can write /tmp"; "the console needs physical
access"). The pattern cannot:

- **Every one of these anchors is replaceable without touching signed code.** No firmware modification, no update, no RSA bypass.
- **Four of the five are single-file or single-parameter changes to fix.** Pin the key to the embedded resource; treat
  `secure_console` as a build-time property; derive UNECE status from a fuse or signed property; move the account database out of tmpfs
  and stop choosing the root shell by file copy; derive a per-unit encryption key.
- **They fail open.** A corrupt LUKS header yields *permissive MAC*. A missing key file yields *launch anyway*. An absent lockout file
  yields *no lockout*. In each case the failure direction is the unsafe one, which is what turns an operational accident into a security
  event.

## The recommended single change

**Never resolve a security decision from a path that is writable at runtime.** Concretely: put the account database, the verification
key, the console policy and the encryption key in read-only storage or a hardware root of trust, and make every one of these checks fail
*closed* — refuse to launch, refuse to log in, stay enforcing, refuse to mount — when the anchor is missing or unreadable rather than
proceeding with the permissive branch.

## Provenance

Everything above is measured or quoted from the recovered EU `260128` image, with the demonstrations recorded at
`evidence/fde/passphrase-1234-2026-11-04.log`, `../evidence/serial-console/ttyS2-login-prompt-2026-11-04.log`,
`evidence/vm-bringup/interactive-touch-2026-11-04.log` and in V-048's entry. Field prevalence is labelled per entry; V-052 and V-053 in
particular state that whether production units reach those branches is not established.

## The premise, measured: `/tmp` really is world-writable

Every instance above depends on the same enabling condition, which was previously assumed. It was measured in the projection:

```
TMP_MODE=1777
tmpfs /tmp tmpfs rw,relatime 0 0
SELF_LABEL=_
```

So `/tmp` is a **`1777` world-writable tmpfs**, and a process under the research init carries SMACK's floor label `_` with no rules loaded
(`/sys/fs/smackfs/load2` empty). Two consequences for how these entries should be read:

- **The anchors are reachable by any code execution, not only by root.** The reason V-054 and V-055 are labelled *latent* is not that `/tmp`
  is protected — it is not — but that every vendor process observed on this build already runs as uid 0, so there is no lesser-privileged
  context to exploit them *from*. Any future sandboxed component, media parser or lesser user changes that immediately.
- **This projection does not enforce SMACK**, so no MAC claim can be made from these runs. On the stock path `smack_setup.sh` loads policy
  and then, per V-052, switches to permissive when `optUNECE` is 0 — which is what was measured. The research init skips that entirely.

That is the honest status: the *substrate* for these six findings is confirmed world-writable; the *attacker position* needed to use it is not
demonstrated on this build.

## The capability-stripping hypothesis, tested — and not supported here

The sweep suggested an attractive explanation: that `/etc/smack_setup.sh`'s `echo "Privileged" > /sys/fs/smackfs/onlycap` strips capabilities
from application processes (which carry no label), which would make the six anchors the capability-stripped app's route back to full root.
Two halves were measured. **The first holds; the second does not, in this configuration.**

**Half one, confirmed — applications carry the floor label, not `Privileged`:**

```
--- AppHomeScreen pid=926   label=_   Uid=0   CapEff=0000003fffffffff
--- AppLauncher             label=_   Uid=0   CapEff=0000003fffffffff
--- keeper                  label=_   Uid=0   CapEff=0000003fffffffff
--- ApplicationManager      label=_   Uid=0   CapEff=0000003fffffffff
```

So no vendor application is labelled `Privileged`, and `chsmack` never touches `/app/**` - consistent with the static reading.

**Half two, refuted here — setting `onlycap` did not strip capabilities:**

```
BEFORE_onlycap  self label=_  CapEff=0000003fffffffff
SET_OK          onlycap_now=Privileged
NEW PROCESS     child_label=_ child_CapEff=0000003fffffffff child_uid=0
WORLD_WRITABLE_OK     ROOT_OWNED_WRITE_OK
```

A brand-new process with label `_` still held **full capabilities** and could still write a root-owned file. So on this kernel and this boot
path, `onlycap` written at runtime does not confine an unlabelled uid-0 process.

### Why this is not the end of the question

The measurement is honest but its scope is narrow, and the caveats matter:

- **Our projection is not the stock boot.** `smack_setup.sh` never ran here; `onlycap` was empty beforehand, and it was set from a shell that
  already had capabilities. SMACK's `onlycap` semantics are applied during exec-time label transitions, and this kernel is 4.1 where the
  interaction with a runtime write is not what a stock boot performs.
- **The stock path loads policy first** (devices labelled `_`, `onlycap` set before applications start), so applications there are exec'd
  under the restriction rather than after it.

So the correct statement is: **the mechanism is not supported by the projection's measurement, and the stock-path measurement remains
outstanding.** On a unit, the two commands that decide it are unchanged:

```
cat /proc/<pid>/status | grep Cap        # CapEff for an application process
cat /proc/<pid>/attr/current             # expect "_", not "Privileged"
```

Until that is run, V-054 and V-055 stay **latent**, and this document will not upgrade them on the strength of a plausible story. The value of
recording the refutation is that the next reader does not spend a week believing the elegant version.

### Second attempt, with proper exec-time labels — same result

The first test was open to the objection that `onlycap` acts on **exec-time label transitions**, and the processes tested had inherited the floor label
rather than been labelled by execution. That objection was tested properly, using the image's own `/sbin/chsmack`:

```
floor attr: /tmp/lf/sh access="_" execute="_"
priv  attr: /tmp/pv/sh access="_" execute="Privileged"
onlycap=Privileged

floor: label=_          capEff=0000003fffffffff
priv : label=Privileged capEff=0000003fffffffff
```

Two binaries, one whose `SMACK64EXEC` is the floor label and one whose `SMACK64EXEC` is `Privileged`, both executed **after** `onlycap` was set.
The label transition is visible in `/proc/self/attr/current` — `_` for one, `Privileged` for the other — and **both kept full capabilities**
(`CapEff=0000003fffffffff`, the maximum mask for this kernel).

So the capability-stripping hypothesis is refuted in two configurations, not one.

### Which raises a more interesting question than the hypothesis did

If `onlycap` does not strip capabilities even for a correctly labelled exec, then the MAC restriction this image configures may not be
delivering the containment its design implies. **Caveats, stated rather than buried:** neither this harness nor the recovered boot material shows a
`security=smack` or `smack_onlycap=` boot parameter, and the full policy load (`load2` rules, which `smack_setup.sh` does not author in any case)
does not happen under the research init. A vehicle that boots with different LSM parameters could behave differently.

What can be said from measurement: **on this kernel and boot configuration, writing `onlycap` as `smack_setup.sh` does does not produce a
capability barrier**, and the two things that would change the answer — an LSM boot parameter and a populated rule table — are absent. That is
worth checking on a unit with the same two commands plus `cat /proc/cmdline`.

## The MAC question, settled by measurement under the authentic boot

An earlier version of this document argued the anchors were reachable because the MAC layer was inert, and a later correction found the layer is not inert at
all: `/etc/smack/accesses.d/` ships **27 rule files with 636 rules over 28 labels**, and the authentic boot loads them
(`Smack service loads smack rules in /etc/smack/accesses.d`). What was then open — whether an application process is subject to those rules — is now measured.

Under the authentic boot, with the policy loaded, in a process carrying the label the applications actually use:

```
SMACKPROBE label=_ rules=27 read=[secret] write=[ok]
```

A `_` subject **read and wrote** a file labelled `Log::dlt` without being refused. `_` is SMACK's floor label and doubles as a wildcard, so a process carrying
it sits outside the rule set. The policy is real, loaded, and does not cover the applications.

That is the accurate basis for V-054 and V-055 being reachable from an application: uid 0, wildcard subject label, and a measured `1777` `/tmp` holding every
anchor in this document.

---

## The same gate keeps appearing, and it is not a gate

Three findings in this project now rest on the same sentence: *the bus is root-only, so only root can call it.*

| finding | the gate |
|---|---|
| V-051 the manager executes a caller-named path | session bus is `EXTERNAL`-authenticated; uid 65534 refused |
| V-061 the application-set hash is queryable | session bus, root-only |
| V-062 the modem's factory interfaces | ofono policy: `allow user=root`, `deny context=default` |

**On this unit, root is not a privilege boundary - it is the ambient privilege level of the application stack.**
`AppHomeScreen` was measured running as `uid=0`; the touch-input path logs `uid=0`; the eleven services in V-058 all
connect to the same bus. So "only root can do this" means "**any application that is compromised can do this, and any
of the others can do it too**".

That is the same argument as the rest of this document, one layer up: the controls in this platform are placed on
boundaries that do not separate the things that need separating. A bus policy that only excludes non-root does not
protect one root component from another, and on this system root components are the majority.

**The recommendation does not change, it generalises:** put the check where the privileged action happens, make it
fail closed, and do not treat "the caller is root" as authorisation for a factory operation.

---

## The cause of the pattern, named

Every finding above that ends in "the bus is root-only" is narrower than it looks, and V-064 now names why: **106 of the
107 systemd services in the image run as root**, the single `User=` line belongs to systemd itself, and **no vendor unit
sets `NoNewPrivileges`, a capability bound, `ProtectSystem` or a syscall filter**.

So the platform's privilege model is not "a privileged core and contained components" - it is **"everything is root, and
some things are more root than others"**. Every component listed in this document is a peer of every other, and a
compromise of the least-important one is a compromise of the whole.

**That is what makes this document's recommendation urgent rather than tidy**: the writable-path anchors do not merely
weaken one check, they hand over a privilege level that the design already grants too widely.
