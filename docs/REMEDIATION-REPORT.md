# Remediation report — findings that can be fixed from configuration

**Scope:** the recovered EU `NE_E.EUR.S5W_L.001.001.260128` image, analysed statically and in a QEMU projection. No test has been run on a vehicle.
**Purpose:** the register (`Ioniq5-VULNERABILITIES.md`) records *what* is wrong; this report orders the fixes by cost and consequence so a platform team can act
without reading forty entries.

Each item gives the finding, the measured evidence, what it exposes, the fix, and how to verify the fix. Items are ordered by **fix cost**, cheapest first,
because the cheapest ones also happen to remove the most.

---

## Tier 1 - configuration and image changes, hours not weeks

These are fixes a platform team can land without touching application code: policy files, unit directives, symlink targets, permissions and boot-script defaults. **Items 15, 16, 21 and 22 are the leverage**: between them they contain a large fraction of this report's impact.

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


### 14. Nine bus policies allow the default context, including state-changing services

**Evidence.** The system bus is deny-by-default (`/etc/dbus-1/system.conf`), but **9 of 18** per-service policy files
add a `<policy context="default">` containing an `<allow>`. The vendor's own among them:

| file | allowed to anyone | methods of note |
|---|---|---|
| `org.genivi.persistence.admin_svc.conf` | `send_destination=…admin_svc` | **`SetSessionState`**, `GetNodeState`, `GetApplicationMode` |
| `org.genivi.NodeStateManager.conf` | `send_destination`, `send_interface=…LifeCycleConsumer` | node lifecycle registration |
| `vcrm.conf` | `send_destination=com.lge.hkmc.tms.vcrmapp` | `setUsageData` |

`vcrm.conf` also ships `<policy user="byungsu">` - a developer's account name, with no such account in `/etc/passwd`.

**Exposes.** Any process on the system bus, **without root**, can ask the platform's node/session state service to
change state and can register as a life-cycle consumer. Practical impact today is small because almost the whole
application stack runs as `uid=0`, but it is a deviation from the platform's own deny-by-default pattern, and
`pas-daemon` state should not be settable from anywhere.

**Fix.** Remove every `context="default"` allow that is not an intentional public query interface; require an
authorised caller for anything that changes state.

**Verify.** From a non-root uid, call `org.genivi.persistence.admin_svc.SetSessionState` and observe whether it is
accepted; `AccessDenied` means a narrower rule exists elsewhere.

### 15. One hundred and six services run as root with no hardening - the leverage item

**Evidence, counted from `/lib/systemd/system/*.service`:**

```
107 units total            User= in 1 (systemd's own user@.service)
NoNewPrivileges 0          RestrictAddressFamilies 0        SystemCallFilter 0
CapabilityBoundingSet 4    ReadOnlyPaths 0                  ProtectSystem/Home/PrivateTmp 3 each
```

**Every unit with any hardening is stock systemd** (`locale1`, `machine1`, `timedate1`, `bus-proxyd`, `localed`,
`timedated`, `machined`). **Not one vendor service sets a single directive.**

**Exposes.** Not a vulnerability in itself - it is why the others are as severe as they are. A compromise of the media
browser, the DLT logger, the thumbnail extractor, the location manager, the radio, the Bluetooth HMI, the telematics
stack or the update path is a compromise of everything: there is no privilege separation between components and no
systemd containment. A service that needs only to write a log has the privileges of one that flashes firmware.

**Fix, in order of value** - all configuration-only, no application code:
1. `NoNewPrivileges=yes` on every unit where it does not break the component.
2. `CapabilityBoundingSet=` reduced per service; most need none.
3. `ProtectSystem=strict` with explicit `ReadWritePaths=`, and `PrivateTmp=yes` - which also neutralises several
   `/tmp`-anchored findings at once.
4. `User=` for components that do not need root (logger, thumbnail extractor, media browser).
5. Later: `SystemCallFilter=`, `RestrictAddressFamilies=`.

**Verify.** Count `NoNewPrivileges=` across `/lib/systemd/system/*.service` and require it non-zero before release;
`systemd-analyze security` on a candidate unit gives the same assessment.

### 16. Nine `/etc` trust anchors point into world-writable `/tmp` - one change fixes all nine

**Evidence, counted:** `/etc/passwd`, `/etc/shadow`, `/etc/shells`, `/etc/fstab`, `/etc/resolv.conf`,
`/etc/ecnr/config`, `/etc/xdg/weston/weston.ini`, `/etc/front_lcd.png`, `/etc/rear_lcd.png` are all **symlinks into
`/tmp`**, written at boot by `esinit`, `smack_setup.sh`, `setup_ecnr_engine_db.sh` and `install_westonPngLogo.sh`.

**The reason is legitimate:** `esinit`'s remount lines are commented out, so the root filesystem is read-only at
runtime, and a generated config file needs a writable location. **The mistake is the destination** - `/tmp` is `1777`,
while root-only writable locations (`/run`, `/rw_data`) exist and are used elsewhere.

**Exposes.** Post-boot, any process that can write `/tmp` can replace the account database (V-054 **demonstrated**:
`uid=0` login), the DNS resolver config (continuous consumers - immediate traffic redirection), the mount table, the
valid-shell list, and the compositor configuration (V-055). Per V-064 that is any of 106 root services.

**Fix.** Point the nine symlinks at `/run/etc/*` with a `0700` directory and `0600` root-owned files, created by the
boot script that writes them. Alternatively `PrivateTmp=yes` on every unit that does not need the shared `/tmp`.

**Verify.** As a non-root process, attempt to append to `/tmp/passwd`; on this image `1777` permits it, and after the
fix it must fail. V-054 already carries the root-consequence reproduction.

### 21. One `/tmp` marker enables the root console and SSH, and the init script creates it every boot

**Evidence.** `lib/systemd/esinit` contains, verbatim:

```
#secure_console : use console login
touch /tmp/secure_console_disable
#check console=ttyS2 and earlycon=uart8250 for No Secure console Booting
#if [ $? = 0 ]; then  /bin/rm /tmp/secure_console_disable ; /bin/rm /dev/ttyS2 ; fi     <- commented out
```

The marker is then tested for **four** capabilities: it writes `/bin/sh` into `/tmp/shells`, installs
`/etc/passwd.legacy` (**root shell `/bin/sh`** rather than `/etc/passwd.secure`'s `nologin`), starts
`/etc/esinit_agetty.sh` (the `ttyS2` root console), and is the `ConditionPathExists` of `dropbear@.service` (V-067).
The **only** code that removes it is a MICOM parameter check: `secure_console == 1` -> `rm` the marker and `/dev/ttyS2`.

**Exposes.** The console, the shell-bearing account database and SSH eligibility all follow from **one file, created on
every boot, whose only off-switch is a MICOM value** - measured as `0` in this image (V-049). The marker also lives in a
world-writable directory (V-065), so even with `secure_console = 1` an attacker can recreate it after boot.

**Bounded by authentication, and this is measured:** the console is an ordinary `agetty` - the autologin line in
`/etc/esinit_agetty.sh` is **commented out** - and the USB-gadget console in `/etc/iap2_mod.sh` is commented out
too. So the marker grants *eligibility*, not access; what stands in the way is V-049's password or V-067's private
key. **The defect is fail-open design, not a bypass.**

**Fix.** Invert the default: create the marker only when MICOM reports a debug state. Move it out of `/tmp` to a
root-owned path. Drop `/etc/passwd.legacy` from production images and keep root `nologin` unconditionally.

**Verify.** On a unit, three commands: `cat /sys/module/micom/parameters/secure_console`,
`ls /tmp/secure_console_disable`, `getent passwd root`.

### 22. Apple's mDNSResponder is an enabled root network daemon with no sandboxing

**Evidence.** `lib/systemd/system/carplay_mdnsd.service` is in `multi-user.target.wants` and runs `/app/bin/mdnsd` -
`mDNSResponder (Engineering Build) (Jan 28 2026)`, Apple's mDNS responder on UDP 5353 - with **no `User=`, no
`NoNewPrivileges`, no `CapabilityBoundingSet`, no `ProtectSystem`**. `Requires=dbus-com.lge.car.micom.service`.

**Exposes.** A daemon that exists to parse unauthenticated multicast packets runs **as root with no containment**. Any
parsing defect in a component with a long advisory history becomes a root defect immediately. It is enabled by default,
not optional. Reachability depends on an interface; the WiFi path is gated (V-050) and the USB/Ethernet path is unmeasured.

**Fix.** `User=nobody` (**verified present** in both shipped passwd variants), plus `NoNewPrivileges=yes`,
`CapabilityBoundingSet=`, `ProtectSystem=strict`, `PrivateTmp=yes`, and interface restriction. Configuration only.

**Verify.** `ss -lunp | grep 5353` and `ps -o user= -p $(pidof mdnsd)`.

### 23. An unauthenticated TCP-to-serial bridge ships in two applications

**Evidence.** `app/bin/AppMPAutoTest` contains
`socat -d -d tcp-l:9997,reuseaddr,fork /dev/ttyUSB0,nonblock,rawer,waitlock=/var/run/ttyUSB0 &` and
`app/bin/TmsGuiApp` contains `socat tcp-l:9997,reuseaddr,fork file:/dev/ttyUSB0,nonblock,raw,echo=0,waitlock=...`.

**Exposes.** A **listening TCP port 9997** bridging a **USB serial device** byte-for-byte to any client on a reachable
interface, with `fork` (concurrent clients), `reuseaddr` (immediate rebind) and `waitlock` (device contention) - a
deliberate service shape, **with no authentication, TLS, allow-list or bind restriction**. It appears in **two** different
applications, so it is a pattern rather than one stray line. On a connected vehicle the attached device may be the modem or
a diagnostics channel.

**Fix.** Bind to loopback if local, else require authentication/TLS or a per-session token; remove from production images
if it exists only for manufacturing, which is the split the platform already makes for engineering mode.

**Verify.** `netstat -ltnp | grep 9997` on a unit, then attempt `socat - TCP:<unit>:9997` from another host: a connection
that succeeds without credentials is this finding.

## Tier 2 - code changes, requiring a release

These need a change in a shipped component: a verification routine, an execution path, or a build that no longer embeds credentials.

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

### 12. Engineering mode can be requested by any process on the system bus

**Evidence.** `ApplicationManager` subscribes to the front-panel special-key signal with an **empty service and an empty path**, so the match rule is interface plus member only (`0x214dc9`-`0x214e3e`). The handler takes a two-byte payload and the second byte selects the action (`0x206308`-`0x2062f8`); `payload[1] == 0x05` reaches `movl $0x12d` - app id **301**, the engineering application. Measured in the projection: the payload reaches the system bus (a monitor sees it) and the handler declines on internal state.

**Exposes.** Any process that can write a signal to the system bus can request engineering mode with two bytes, without a physical key or PIN. Practical severity today is bounded by the state gate - which is why the sender check belongs **before** that gate is found to be satisfiable.

**Fix.** Pass `com.lge.car.micom` as the connect service, or verify `message().service()` in the slot, and re-check payload length and byte range before dispatch.

**Verify.** Emit `[0x01, 0x05]` from a client that is not the owning service and confirm nothing happens; then from the owner and confirm unchanged behaviour.


### 13. The application-set hash is queryable by any session-bus client

**Evidence.** `com.lge.avn.applauncher` implements `com.lge.avn.applauncher.cipher.getIVDHash() -> ay`. The launcher holds every application binary's path beside `SHA256_Init/Update/Final` and labels the digest `SystemIVD`; a call returned a 32-byte value.

**Exposes.** The digest is a fingerprint of the installed application set, so for a process already running as root - most of the stack - it answers **"did my tampering change the platform's integrity view?"**, and an unchanged value discloses which changes are invisible to it. The bus is root-only, so no content leaks and no escalation is implied.

**Fix.** Restrict the interface to the MICOM bridge or drop the method from the public object; if attestation is required, make it a challenge-signed response rather than a stable digest.

**Verify.** Query the digest, change one byte in one application binary, query again: a changed value confirms the oracle, an unchanged value is a finding about coverage.


### 17. The navigation payload: world-writable binary and a verification key in `/tmp`

**Evidence.** `/navi/Bin/AppNavi` (143,718,392 bytes) and `/navi/Bin/CANService.sh` are `-rwxrwxrwx`, with 126 configuration files beside them. `/navi` is read-only in normal boot, but `app/bin/AppLauncher` carries `mount -o remount,rw /navi` / `remount,ro /navi`, so a **read-write window** opens at runtime. The same binary contains `/tmp/navi_public.key`, `:/navi_public.key` and `RSA_verify`, and **no navi public key ships in the image**.

**Exposes.** During the window any non-root process can modify the navigation binary or the startup shell script in place; and if the key is read from the tree it verifies, the check is self-referential. V-048 already demonstrated the consequence of trusting a `/tmp` key: a binary this project signed ran as `uid=0`.

**Fix.** `chmod go-w` on the two paths (the image has **no world-writable directories**, so this is two files, not a tree audit); mount `/navi` read-only unconditionally; move the key to a root-owned read-only location and **ship it**.

**Verify.** During the launcher's window, open `/navi/Bin/AppNavi` for writing from a non-root process; compare `/tmp/navi_public.key` against any key in the navi tree.


### 18. A static root SSH key ships in the image, behind a `/tmp` marker and a missing binary

**Evidence.** `/etc/dropbear/authorized_keys` ships with one RSA key (`rsa-key-20181102`). `dropbear@.service` exists with `ConditionPathExists=/tmp/secure_console_disable` as its only gate and `ExecStart=-/usr/sbin/dropbear -i -s ...`. `/etc/default/dropbear` has `# DROPBEAR_EXTRA_ARGS="-w"` **commented out**, and `-w` is "disallow root logins". `dropbear_publickey_installer.sh` copies the shipped key into `/home/root/.ssh/authorized_keys`. **The daemon binaries are absent and the unit is not enabled**, so it cannot run on this image.

**Exposes.** The credential is **static and shared**: every unit built from this image accepts the same private key, so one leak anywhere is root on all of them, with no per-device rotation. The gate is a file in a world-writable directory whose name reads like a hardening flag, and adding the `dropbear` package for field debugging completes the chain.

**Fix.** Remove `authorized_keys`, `dropbear@.service` and `dropbearkey.service` from production images; provision per-device credentials if SSH is required and gate on MICOM state; treat `rsa-key-20181102` as compromised by distribution.

**Verify.** `grep -c . /etc/dropbear/authorized_keys` on a unit: any non-zero result is this finding.


### 19. Embedded private keys, and a navigation CA on a writable partition

**Evidence.** Four application binaries carry PEM private-key blocks - `AppProjection` (2 keys + **3 certificates**), `AppUpgrade` (6), `AppScomoDM` (3), `AppDMClient` (3); one parsed block is **RSA 2048**, public-key SHA-256 beginning `af1e9a9a...`. Separately, `AppUpgrade` reads `/rw_data/navi_data/certificates/TomTom_Root_CA.crt`, which ships **1,588 bytes, mode `-rwxrwxr-x`, on the read-write partition**, and SCOMO's own code names that file as the TomTom root CA (copying one only when none exists).

**Exposes.** Everything shipped is **compromised by distribution** - identical on every unit, no rotation, and a backend authenticating by certificate cannot distinguish units. The CA is worse in practice: **one file write** could let an attacker sign a navigation package the unit accepts, and the payload runs as root.

**Fix.** Establish what the embedded keys authenticate and rotate them, reissuing per-device credentials; move key material to manufacture-time provisioning. Move the navi CA to read-only storage, or make it signed by a read-only-side key.

**Verify.** `grep -c 'BEGIN .*PRIVATE KEY' /app/bin/*` gives four files; compare public-key fingerprints across two units. For the CA: replace it, sign a navi package, attempt an update.


### 20. The manufacturing test application references a script on a persistent writable partition

**Evidence.** `app/bin/AppMPAutoTest` contains `/app/data/AppEngineeringMode/shell/eject.sh` and links `QProcess::start`, `startDetached` and `waitForFinished`. `/app/data` symlinks to **`/rw_data/app_data`**, which persists across reboots; the shell directory **is not shipped**. Manufacturing mode is already known to be triggered by a `/tmp` marker (V-042).

**Exposes.** *If* that path is executed, one directory plus one file on a persistent partition plus the known trigger would give **unattended root execution surviving reboot**. **Measured negative:** starting `AppMPAutoTest` as root with the script staged and the marker created did **not** run it, so the cheap reading is refuted; the trigger is some other event - the file is named `eject.sh`, so a media-eject path is the first place to look.

**Fix.** Never execute scripts from a persistent writable partition: ship field-diagnostic scripts read-only and run that path, or verify a signature with a key that is not itself writable (V-069's failure mode).

**Verify.** On a unit, stage the script with a marker command, trigger manufacturing mode, and observe whether it runs.


## Register cross-reference

The register (`Ioniq5-VULNERABILITIES.md`) is the evidence base; this report is the fix list. The mapping:

| item | register entry |
|---|---|
| 1 applications may not run under the policy written for them | V-056 |
| 2 the account database lives in a world-writable tmpfs | V-054 |
| 3 the compositor loads modules named in `/tmp` | V-055 |
| 3b eleven services take their bus address from `/tmp` | V-058 |
| 4 a tampered data partition turns mandatory access control off | V-052 |
| 5 the serial console is enabled by default | V-049 |
| 6 privileged behaviours keyed on a file in `/tmp` | V-042 |
| 7 the updater verifies then installs from a second read | V-059 |
| 8 the manager executes a caller-named path as root | V-051 |
| 9 the signature check trusts a key in `/tmp` | V-048 |
| 10 `debug-shell.service` is an unauthenticated root shell | V-014 |
| 11 the data encryption passphrase is `1234` | V-053 |
| 12 engineering mode is requestable by any system-bus process | V-060 |
| 13 the application-set hash is queryable on the session bus | V-061 |
| 14 nine bus policies allow the default context | V-063 |
| 15 106 of 107 services run as root with no systemd hardening | V-064 |
| 16 nine /etc trust anchors point into /tmp | V-065 |
| 17 world-writable navi binary and a navi key in /tmp | V-066 |
| 18 a static root SSH key ships in the image | V-067 |
| 19 embedded private keys, and a navi CA on a writable partition | V-068, V-069 |
| 20 a script path on a persistent writable partition, run by the manufacturing app | V-070 |
| 21 one tmp marker enables the root console and SSH, created every boot | V-071 |
| 22 an enabled mDNS responder runs as root with no sandboxing | V-072 |
| 23 an unauthenticated TCP-to-serial bridge on port 9997 | V-073 |
| 24 the VIN is persisted in logs and handed to the voice backend | V-074 |
| 25 nothing in userspace verifies the boot image; bootloader unassessed | V-075 |

## What is not claimed

- Nothing here has been reproduced on a vehicle. Every item is static analysis plus a QEMU projection, and each entry states its own limits.
- Whether application processes can be given real labels without breaking them is untested — that is the first thing to try for item 1, and it is cheap.
- The console password hash is **uncracked**; 45,000 plausible candidates failed, which says nothing about a determined offline attack at GPU speed.

## The single sentence for the platform team

Six of these findings are one mistake: **a security decision resolved from state the threat model treats as untrusted** — a key in `/tmp`, a writable kernel
parameter, a filesystem probe, a literal passphrase, a symlinked account database, a symlinked compositor config. Move those decisions onto read-only or
hardware-backed state, and make every one of them **fail closed**.

### 24. The VIN is persisted in logs and handed to the voice backend

**Evidence.** In the vehicle's own DLT dump:
`[VH_VoiceHandler::sendServerInfoVin(6165)]  [VH -> SDS] VIN KMHCX5LD3HT013710`, with the identifier appearing 78 times.
The logs live on `/log_data`, a persistent writable partition, and are exported by the offline-trace mechanism.

**Exposes.** The vehicle identity survives reboot on a writable partition and travels with any dump, service ticket or
returned unit; and the function name plus the `[VH -> SDS]` marker indicate the VIN is also sent toward the speech
backend - **not observed on a wire here**. Neither path is disclosed to the driver.

**Fix.** Log a hash or session id instead of the VIN unless a diagnostic build asks otherwise; treat `/log_data` as part of
the data-retention story; make any VIN in the voice session conditional on the feature and disclose it.

**Verify.** `grep -a 'VIN ' /log_data/dlt/*.dlt | head` on a unit proves persistence; capturing an assistant session would
prove transmission.

**Sampling note.** A loose sweep produced thousands of password, SSID, coordinate and phone-number hits; **all were noise or
imported forum text**, and only the VIN survived sampling. Recorded so nobody re-derives it.

### 25. Nothing in userspace verifies the boot image it maintains

**Evidence.** No `avb`/`vbmeta`/`dm-verity`/`verified boot` reference exists anywhere in `esinit` or `/etc/*.sh`. In the
crash-recovery path `esinit` runs `fsck.ext2 -fy /dev/mmcblk0p1`, formats it with `mke2fs -F` if fsck fails badly, and then
`cp /tmp/plk2/iasImage /tmp/plk1/iasImage` - a plain copy between two **read-write** partitions, with **no signature, hash
or version check**.

**Exposes.** Any process on this unit runs as root (V-064), so any compromised component can place a modified `iasImage`
into either A/B slot. **If the bootloader verifies it**, that is a refused boot; **if it does not, it is persistence that
survives a rootfs reinstall** - which would outrank V-069 as the cheapest persistent path. *(The `mke2fs` itself is a
recovery step followed by a restore, and is not a defect - recorded because I assumed otherwise before reading on.)*

**Fix.** Verify `iasImage` before it is copied (signature against a key on read-only storage), and confirm the bootloader
enforces the same. Report the bootloader's verification status as part of the security posture rather than leaving it
implicit.

**Not assessed:** whether ABL verifies `iasImage` or applies the anti-rollback counter to it. Closed firmware outside the
extracted image; the test is destructive if no verification exists and belongs to someone with a recoverable unit.

## Why the tiers were rebuilt (2026-11-05)

Items had been **appended** to this report without re-reading it, so by item 23 the structure said something false: a
dozen **configuration-only** fixes (bus policies, unit hardening, symlink targets, an inverted boot default, a daemon's
missing `User=`, an unauthenticated listener) sat under the heading *"code changes, requiring a release"*, and two items
were out of numeric order - item 11 at the very end, after item 23.

That matters because **the tier is the reader's only signal for cost**, and every one of those twelve is a change a
platform team could land in an afternoon.

The report is now:

| tier | items | what they are |
|---|---|---|
| **1 - configuration and image changes** | 13 | policy files, unit directives, symlink targets, permissions, boot-script defaults |
| **2 - code changes, requiring a release** | 11 | a verification routine, an execution path, or a build that stops embedding credentials |

and the four leverage items are named at the head of Tier 1 rather than being findable only by reading all of it.

**The lesson is the same one as the state page and the README:** a document that is only ever appended to will
eventually contradict itself, and the fix is to read it before adding - not to trust that the last edit was the whole
document. **This is the fourth time in this session that the record, not the work, was the thing that needed correcting.**
