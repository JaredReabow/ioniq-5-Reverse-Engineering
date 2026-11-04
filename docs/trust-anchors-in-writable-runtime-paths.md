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
`evidence/fde/passphrase-1234-2026-11-04.log`, `evidence/serial-console/tty2-login-prompt-2026-11-04.log`,
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
