# Remediation report — findings that can be fixed from configuration

**Scope:** the recovered EU `NE_E.EUR.S5W_L.001.001.260128` image, analysed statically and in a QEMU projection. No test has been run on a vehicle.
**Purpose:** the register (`Ioniq5-VULNERABILITIES.md`) records *what* is wrong; this report orders the fixes by cost and consequence so a platform team can act
without reading forty entries.

Each item gives the finding, the measured evidence, what it exposes, the fix, and how to verify the fix. Items are ordered by **fix cost**, cheapest first,
because the cheapest ones also happen to remove the most.

---

## Tier 1 — configuration changes, hours not weeks

### 1. Applications run under the one SMACK label that is exempt from the policy

**Evidence.** `/etc/smack/accesses.d/` ships **27 rule files, 636 rules, 28 labels** and the boot loads them
(`Smack service loads smack rules in /etc/smack/accesses.d`). Every application observed — `AppHomeScreen`, `AppLauncher`, `keeper`, `ApplicationManager` — carries
the label **`_`**, runs as uid 0 with the full capability mask, and under the authentic boot a `_` process **read and wrote** a file labelled `Log::dlt`:

```
SMACKPROBE label=_ rules=27 read=[secret] write=[ok]
```

**Exposes.** The policy constrains something, but not the applications — the components that parse attacker-supplied input. Anything an application can reach,
the policy does not protect: vehicle logs, other applications' data, the trust anchors below.

**Fix.** The label vocabulary already exists (`App::bluetooth`, `App::upgrade`, `App::usbautomount`, …). Give application processes a real `App::*` label, add the
rules they legitimately need, and stop running them under the wildcard.

**Verify.** On a unit: `cat /proc/<AppHomeScreen pid>/attr/current` returns a domain label, not `_`; then confirm that process **cannot** read a `Log::*` object.

**Measured both ways already, in the projection.** With the policy permissive (`optUNECE=0`) a `_` process read and wrote a `Log::dlt` object. With it **enforcing**
(`optUNECE=1`) the same probe still succeeded, while 40 other access decisions were **denied** — so the policy constrains some subjects but never this one, and
flipping the enforcing switch will produce service failures among components developed against the permissive default. Fix the label first, then enforce.

### 2. The account database lives in a world-writable tmpfs

**Evidence.** `/etc/passwd -> /tmp/passwd`, `/etc/shadow -> /tmp/shadow`, rebuilt at boot by `esinit`; `/tmp` is `1777`. Appending one line produced a working
uid-0 account (`id audit0` → `uid=0(audit0)`; `getent passwd audit0` resolved it). "Secure console" is a **file copy** of `passwd.legacy` (root → `/bin/sh`) or
`passwd.secure` (root → nologin) into that tmpfs.

**Exposes.** Any write to `/tmp` becomes account takeover for anything that resolves names through NSS, and the console-shell policy becomes a writable file.

**Fix.** Keep the account database in read-only storage; make account changes explicit and authenticated; decide console policy by capability, not by which text
file was copied.

**Verify.** `/etc/passwd` resolves to read-only storage, and an attempt to create an account fails rather than succeeding silently.

### 3. The compositor loads modules named in a file that lives in `/tmp`

**Evidence.** `/etc/xdg/weston/weston.ini -> /tmp/weston.ini`, created at boot by `install_westonPngLogo.sh`, and the file selects `shell=`, `backend=` and
`ivi-module=` — all loadable objects loaded by a **root** process.

**Exposes.** Whoever can write that path chooses the shared objects the display server loads. Effect applies at the next compositor start, not instantly
(`weston-crash.sh` dumps diagnostics and messages MICOM's watchdog; it does not restart weston).

**Fix.** Keep compositor configuration in read-only storage; require module paths to be absolute and inside a signed directory rather than whatever the config names.

**Verify.** The config is not writable by a non-privileged writer and a modified config is rejected.

### 4. A tampered data partition turns mandatory access control off

**Evidence.** `esinit` derives `optUNECE` from `cryptsetup isLuks` on the data partition, and `smack_setup.sh` switches SMACK to **permissive** when it reads 0:

```sh
if [ $CHECK_UNECE1 == "0" ]; then echo "1" > /sys/fs/smackfs/bringup-switch; fi
```

Measured `optUNECE=0` in the projection. The factory data partition ships as a **plain tar of plaintext files**, so a unit built from it is non-LUKS and takes
this branch.

**Exposes.** The failure direction is wrong: an unreadable, corrupt or replaced data partition yields *less* confinement rather than a refusal. Combined with item
1 this is the difference between "applications are constrained" and "applications are not".

**Fix.** Derive the UNECE posture from a signed build property or a fuse, never from a filesystem probe; and make an unrecognised partition a reason to stay
enforcing, not to relax.

**Verify.** Corrupt the data partition deliberately and confirm MAC stays enforcing and the boot fails closed.

### 5. The serial console is enabled by default and gated by a writable parameter

**Evidence.** `agetty` on `ttyS2` at 115200 8n1, `/etc/securetty` lists it, and the gate is `/sys/module/micom/parameters/secure_console`, which reads **0**;
`esinit` deletes the device only when it reads 1. The login prompt was captured on the far side of the port.

**Exposes.** Anyone at the UART pads gets a root login prompt. The password is a single SHA-512 hash at a **fixed image-wide salt**, so one crack covers the fleet.
Guessing was attempted and failed: 10,000 four-digit PINs, 34,334 date permutations, and a vendor word list did not match.

**Fix.** Do not create the console in production at all, rather than disabling it with a runtime parameter; give each unit a unique salt.

**Verify.** `/dev/ttyS2` does not exist on a production build.

---

## Tier 2 — code changes, requiring a release

### 6. The application manager executes a caller-named path as root, unverified

**Evidence.** `request.launch(appid, appname, applocation)` takes the binary's path **from the caller**. A payload with no signature section, launched with the
verification key deleted, ran as `uid=0`:

```
m_AppProcess->start(/poc/payload_plain) PID[952]
V048_PAYLOAD_RAN / uid=0 euid=0 gid=0
```

**Exposes.** Root code execution for anything able to send one session-bus message. Reachability is bounded: the session bus accepts only uid 0
(EXTERNAL auth, measured — uid 65534 cannot connect), so on this build it is a **persistence and re-launch primitive**, not an escalation from a lesser user. It
becomes an escalation the moment any non-root context exists.

**Fix.** Ignore `appLocation` from the request; resolve binaries by app id from a fixed read-only directory; verify the signature on the resolved path; treat
verification failure as fatal.

**Verify.** A launch request naming an arbitrary path is refused, and a correctly signed binary in the trusted directory still starts.

### 7. The signature check itself trusts a key in `/tmp`

**Evidence.** The manager verifies with `RSA_verify(NID_sha256, …)` against a **PEM key read from `/tmp/app_normal.key`**. The authentic keys are pinned as Qt
resources (`:/app_normal.key`) but are copied to `/tmp` once and the copy is trusted thereafter without comparison.

**Exposes.** Where the check *is* applied (binaries launched from `/app/bin`), the trust anchor is replaceable. A binary signed with a key generated during this
work was accepted and ran as uid 0.

**Fix.** Verify against the pinned resource; never read a key from a writable directory.

**Verify.** Replacing `/tmp/app_normal.key` has no effect on verification.

### 8. The installed `debug-shell.service` is an unauthenticated root shell

**Evidence.** `DefaultDependencies=no`, `ConditionPathExists=/dev/tty9`, `ExecStart=/bin/sh`. Not enabled — and `SYSTEMD_WANTS` names units directly, ignoring
enable links. Neighbours are the safe pattern: `console-shell.service` runs `sulogin`, `console-getty.service` runs `agetty`.

**Exposes.** Any device property that reaches `SYSTEMD_WANTS=debug-shell.service` yields a root shell with no password. The upstream advisory for the udev
property-injection defect names exactly that property.

**Fix.** Remove the unit from production rather than leaving it disabled.

**Verify.** `systemctl cat debug-shell.service` fails on a production image.

---

## Tier 3 — data protection: currently weaker than it appears

### 9. The data encryption passphrase is `1234`, and in the shipped flow it never runs

**Evidence.** `/etc/fde_test_v2.sh` formats `/rw_data` and `/log_data` with `echo "1234" | cryptsetup -c aes-cbc-essiv:sha256 luksFormat`, and the same literal
opens them. Demonstrated, with a negative control:

```
OPEN_WITH_1234_RC=0   OPEN_WITH_WRONG_RC=5   Cipher mode: cbc-essiv:sha256
```

But `esinit` invokes that script **only when the partition is already LUKS**, and the factory data partition is a plain tar of plaintext files. So in the shipped
flow the encryption likely never engages, which leaves the data **unencrypted** and simultaneously sets `optUNECE=0` (item 4).

**Exposes.** Two different problems with two different fixes, which is why both are stated: if encryption ever engages, the key is worthless; if it does not engage,
user data and vehicle logs are plaintext on the flash.

**Fix.** Per-unit key from a protected source (fuse/OTP or a hardware keystore), AEAD mode, and — separately — make sure it actually engages.

**Verify.** Dump the storage of a unit: it must not be readable without a per-unit secret.

---

## What is not claimed

- Nothing here has been reproduced on a vehicle. Every item is static analysis plus a QEMU projection, and each entry states its own limits.
- Whether application processes can be given real labels without breaking them is untested — that is the first thing to try for item 1, and it is cheap.
- The console password hash is **uncracked**; 45,000 plausible candidates failed, which says nothing about a determined offline attack at GPU speed.

## The single sentence for the platform team

Six of these findings are one mistake: **a security decision resolved from state the threat model treats as untrusted** — a key in `/tmp`, a writable kernel
parameter, a filesystem probe, a literal passphrase, a symlinked account database, a symlinked compositor config. Move those decisions onto read-only or
hardware-backed state, and make every one of them **fail closed**.
