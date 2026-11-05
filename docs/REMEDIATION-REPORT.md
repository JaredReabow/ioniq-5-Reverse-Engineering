# Remediation report — findings that can be fixed from configuration

**Scope:** the recovered EU `NE_E.EUR.S5W_L.001.001.260128` image, analysed statically and in a QEMU projection. No test has been run on a vehicle.
**Purpose:** the register (`Ioniq5-VULNERABILITIES.md`) records *what* is wrong; this report orders the fixes by cost and consequence so a platform team can act
without reading forty entries.

Each item gives the finding, the measured evidence, what it exposes, the fix, and how to verify the fix. Items are ordered by **fix cost**, cheapest first,
because the cheapest ones also happen to remove the most.

---

## Tier 1 — configuration changes, hours not weeks

### 1. Applications may not be running under the policy that was written for them

**Evidence.** `/etc/smack/accesses.d/` ships **27 rule files, 636 rules over 28 labels** and the boot loads them
(`Smack service loads smack rules in /etc/smack/accesses.d`). The policy is written per application domain (`App::home`, `App::engineermode`, `App::camera`, …).
In the projection, every application observed — `AppHomeScreen`, `AppLauncher`, `keeper`, `ApplicationManager` — carries the label **`_`** and runs as uid 0 with
the full capability mask.

**What is not established, and why it matters.** Nothing in the shipped artifact applies those labels: no `chsmack -e` for any `/app/**` binary, no `SmackLabel=`
in any unit, no SMACK strings in `AppLauncher`, and the shipping archive `/HU/images/mango-rootfs.tar.gz` contains **no xattr records** - so the projection, which
was built from that archive, necessarily shows `_` whether or not a real unit does. An earlier version of this report cited a probe that appeared to show a `_`
process reading a `Log::dlt` object; **that probe is withdrawn** because it never verified that the object had actually been relabelled.

**Exposes.** If applications run unlabelled on a unit, the 636-rule policy constrains services but not the components that parse attacker-supplied input. If they
run labelled, the policy is doing its job. The difference is one command.

**Fix, in order.** First verify which is true on a unit. If applications are unlabelled, give them the `App::*` labels the policy already defines, and only then
consider enforcement — the enforcing branch measures **40 denied access decisions** in the projection, so switching it on before labelling will break services while
confining nothing.

**Verify.**

```
getfattr -n security.SMACK64EXEC /app/bin/AppHomeScreen
cat /proc/$(pidof AppHomeScreen)/attr/current
```

A domain label means the policy applies. `_` means it does not.

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

### 3b. Eleven services take their session-bus address from a world-writable file

**Evidence.** `/app/bin/Dbuslaunch.sh` writes `/tmp/session_appmgr.env`, and **eleven units** read their address from it via `EnvironmentFile=`:
`ApplicationLauncher`, `CryptoService`, `MediaBrowser`, `credman`, `mediamanager`, `mof`, `nua`, `ofono`, `remote`, `vbtd`, `watchdogd`. The script `rm`s and rewrites the file at
every boot, so its content is whatever ran last.

**Exposes.** Unlike the other writable anchors, which each subvert one decision, this redirects the bus the **entire application ecosystem** uses. A process able to write that file
before those units start can point all eleven at a bus it owns — intercepting every `registration`, data query and command, and impersonating `com.lge.car.micom`,
`ApplicationManager` or `AppHomeScreen` on the names the real components expect. No component needs a defect; the systemd configuration itself names a writable path as the source of a
privileged environment variable.

**Fix.** Deliver the address over a channel that cannot be pre-created — a systemd `Environment=` value set by the unit that owns the daemon, or a file in a directory only that unit can
write (`/run/user/0`, mode 0700). A file that decides where eleven services connect must not be world-writable.

**Verify.** On a unit, confirm the file is absent from `/tmp` and that the units still resolve their bus; then confirm a non-privileged writer cannot influence it.

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

### 6. Seven privileged behaviours are keyed on "does this file exist in `/tmp`"

**Evidence.** Ten systemd `.path` units ship, and several start a service purely because a file exists in a `1777` tmpfs:

| marker | effect |
| --- | --- |
| `/tmp/no_isa` | starts `ofono.service` and `remote.service` (`TmsRemoteApp`, the telematics remote-command consumer) |
| `/tmp/AppMPAutoTest/do_mpauto` | enters manufacturing auto-test mode (`NotifyMPAutoModeTestStartEvent`) |
| `/tmp/spi_validation_NOK` | starts a validation service and suppresses the compositor |
| `/tmp/no_unece` | starts the WiFi daemon |
| `/tmp/weston.crash` | dumps diagnostics, messages the MICOM watchdog |
| `/tmp/secure_console_disable` | decides whether root gets a console shell |

**What is not established.** No marker has been shown starting a privileged service end to end: the units fire and then fail on unmet dependencies in the
projection. And `/tmp/no_isa` is written by **`AppLauncher`** from an ISA value it reads, so at least that one is a platform-state decision rather than an
attacker action - whether that value can be influenced is a MICOM-boundary question and is open.

**Exposes.** The design keys privileged outcomes on file existence in a world-writable directory, so anything else able to create the same path gets the same
outcome. That is a structural weakening even where the intended writer is benign, and hardening one path leaves the others.

**Fix.** Drive these transitions through an authenticated mechanism (a message on a privileged bus, or a file in a directory only the platform can write) rather
than by existence checks in `/tmp`.

**Verify.** On a unit, create each marker as a non-privileged process and confirm no service starts.

---

## Tier 2 — code changes, requiring a release

### 8. The application manager executes a caller-named path as root, unverified

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

### 9. The signature check itself trusts a key in `/tmp`

**Evidence.** The manager verifies with `RSA_verify(NID_sha256, …)` against a **PEM key read from `/tmp/app_normal.key`**. The authentic keys are pinned as Qt
resources (`:/app_normal.key`) but are copied to `/tmp` once and the copy is trusted thereafter without comparison.

**Exposes.** Where the check *is* applied (binaries launched from `/app/bin`), the trust anchor is replaceable. A binary signed with a key generated during this
work was accepted and ran as uid 0.

**Fix.** Verify against the pinned resource; never read a key from a writable directory.

**Verify.** Replacing `/tmp/app_normal.key` has no effect on verification.

### 10. The installed `debug-shell.service` is an unauthenticated root shell

**Evidence.** `DefaultDependencies=no`, `ConditionPathExists=/dev/tty9`, `ExecStart=/bin/sh`. Not enabled — and `SYSTEMD_WANTS` names units directly, ignoring
enable links. Neighbours are the safe pattern: `console-shell.service` runs `sulogin`, `console-getty.service` runs `agetty`.

**Exposes.** Any device property that reaches `SYSTEMD_WANTS=debug-shell.service` yields a root shell with no password. The upstream advisory for the udev
property-injection defect names exactly that property.

**Fix.** Remove the unit from production rather than leaving it disabled.

**Verify.** `systemctl cat debug-shell.service` fails on a production image.

---

### 7. The updater verifies a file and then installs it from a second read of the same file

**Evidence.** `app/bin/AppUpgrade` is a 16 KB wrapper whose data contains the two real updaters as complete ELF images: **SCOMO** (5,678,432 bytes at `0x7c64`) and **FUMO** (5,066,264 bytes at
`0x5721c8`). This vehicle's launcher row selects FUMO. In **FUMO's own code** the check and the apply are separate invocations that each name the same input file:

```
0x13a550   ionice -c3 md5sum %1 | awk '{print $1}'                                     the check
0x60f0b    DecryptToPIPE -d <src> <off> 0 | pv -q -L 8m | dd of=<partition> bs=512      the apply
```

The apply pipeline opens the payload again, decrypts it and writes it to a **partition device**, and the stream is **rate-limited to 8 MB/s by its own command**. The payload sits on removable
media the user supplies. Extract both updaters with `tools/uk_fw/extract_embedded_elfs.py`; the full measurements are in `evidence/v059-evidence.md`.

**Exposes.** A programmable USB device that serves the genuine image during the check and different bytes during the apply installs content that was never verified. Two consequences, which need
different responses:

- **arbitrary content** needs the unit's TE2 content key (`velix_aes.key`), which does **not** ship in the package;
- **a genuine older image** needs **nothing** - it is already encrypted with the key the unit holds, and the version gate and anti-rollback were satisfied against the genuine current bytes.

**Fix.** Never verify a file and then re-open it: hash during the install over the same handle that writes, or copy once into protected storage and verify *and* install from that copy. Give the
rootfs a boot-time integrity mechanism so "installed unverified content" is not the same as "runs at next boot".

**Verify.** On a unit, confirm the install consumes the bytes it verified - hash the source while writing and compare against the check digest, or refuse a file whose contents changed since the
check.

### 11. The data encryption passphrase is `1234`, and in the shipped flow it never runs

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
