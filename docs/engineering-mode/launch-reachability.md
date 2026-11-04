# V-051 reachability — who can send the launch request, who runs non-root, and why CheckSign is skipped

Status: static analysis of the recovered EU `260128` rootfs
(`work/decrypted-eu-260128/extracted-safe/mango-rootfs`) plus one QEMU-projection measurement of the
session-bus uid gate. This answers **only** the three reachability questions below. The launch primitive
itself — `dbus-send … com.lge.avn.applauncher.request.launch int32:10 string:AppStandbyClock
string:/poc/payload_plain` → `m_AppProcess->start(/poc/payload_plain) PID[952]` running uid 0 — is V-051
(commit `ccd053e`) and is taken as established.

**Bottom line:** the only remaining gate for V-051 is the session bus, and the session bus is **root-only**.
The image provisions **no uid ≥ 1000 accounts** and starts **no vendor process non-root** (no `User=` in
units, and `AppLauncher` does not call any `set*uid`), so every local process is already uid 0. V-051 is
therefore a **persistence / re-launch / SMACK-label-escape primitive for already-root code**, not a
uid-escalation from a non-root attacker; and its trigger is either a root process or the on-screen
About-gesture+PIN, never a bare non-root process.

---

## 1. Session-bus policy — permissive *once connected*, but connection is uid-0-only

The launcher registers `com.lge.avn.applauncher` on the **session** bus (`QDBusConnection::sessionBus()`).
There is no `com.lge.avn.applauncher` policy file anywhere under `system.d/`, and the system bus default
denies `method_call`, so the session bus is the only route.

The only session-bus config in the image is `/etc/dbus-1/session.conf`; `session.d/` is empty and
`session-local.conf` is absent, so nothing overrides it:

```xml
<listen>unix:tmpdir=/tmp</listen>
<auth>EXTERNAL</auth>
…
<policy context="default">
  <!-- Allow everything to be sent -->
  <allow send_destination="*" eavesdrop="true"/>
  <!-- Allow everything to be received -->
  <allow eavesdrop="true"/>
  <!-- Allow anyone to own anything -->
  <allow own="*"/>
</policy>
```

So **no name-level restriction** applies to `com.lge.avn.applauncher`: any *connected* client may send to
it. The gate is connection, not policy. `<auth>EXTERNAL</auth>` with no `<user>` element means the daemon
authenticates by socket-credential uid and accepts only its own uid. The daemon is started by
`Dbuslaunch.service`, which has **no** `User=`/`Group=`:

```ini
# lib/systemd/system/Dbuslaunch.service
[Service]
Type=oneshot
RemainAfterExit=true
Environment=LD_LIBRARY_PATH=/app/lib
ExecStart=/app/bin/Dbuslaunch.sh
```

and `Dbuslaunch.sh` runs `dbus-daemon --session --print-address --fork > /tmp/session_appmgr`, so the
session daemon runs as **root** (systemd default uid 0).

Measured in the projection (`work/vm/signprobe`, `/run-busuid.sh`): the daemon's `/proc/<pid>/status` is
`Uid: 0 0 0 0 Gid: 0 0 0 0`; a **root** `dbus-send … ListNames` returns
`method return sender=org.freedesktop.DBus`, while the identical call as uid 1000 (setuid helper) is
refused:

```
Failed to open connection to "session" message bus: Did not receive a reply. Possible causes include:
the remote application did not send a reply, the message bus security policy blocked the reply, the
reply timeout expired, or the network connection was broken.
```

**Answer: permissive for any connected client, but only uid-0 processes can connect at all. No
`at_console` rule exists in `session.conf`. V-051's sender must already be uid 0 (or be issued by a root
actor / the human gesture).**

## 2. Who runs non-root — nobody of consequence; everything is uid 0

**Accounts.** The shipped passwd files contain **no uid ≥ 1000 account**. `etc/passwd.legacy`,
`etc/passwd.secure` and `etc/passwd-` are identical in this respect — the complete non-root set is the
standard system-daemon set plus `nobody`:

```
daemon:1:1  bin:2:2  sys:3:3  sync:4:65534  man:6:12  lp:7:7  mail:8:8  uucp:10:10
proxy:13:13  www-data:33:33  backup:34:34  list:38:38  irc:39:39  gnats:41:41
nobody:65534:65534
messagebus:999:998  systemd-journal-gateway:998:995  systemd-timesync:997:994
```

All of these are `nologin` system accounts (the only uid ≥ 1000 is `nobody:65534`, a conventional
placeholder, not a login). The names `xuser` and `byungsu` appear **only** as D-Bus policy usernames —
`etc/dbus-1/system.d/connman.conf` (`<policy user="xuser">`), `etc/dbus-1/system.d/vcrm.conf`
(`<policy user="byungsu">`), and `org.genivi.persistence.admin*.conf` — and have **no** matching
`passwd`/`group` entry and **no** provisioning component anywhere in the image (no `useradd`/`adduser`
invocation exists; `etc/group` has no `xuser`/`byungsu`). Those `<policy user=…>` blocks are inert unless
some non-root component absent from this image creates the accounts at runtime.

**Systemd units.** The only `User=`/`Group=` directive in the entire unit tree is the stock template
`lib/systemd/system/user@.service: User=%i`. **No vendor service drops to a non-root user.**

**Launcher credential handling.** `AppLauncher` imports **no** credential-dropping API —
`llvm-nm -D` shows no `setuid`/`setgid`/`setresuid`/`seteuid`/`setegid`/`setreuid` symbols — so it starts
every child as its own uid (root), with no drop. This matches the measured process table
(`app-signature-runtime-test.md`): `AppLauncher`, `ApplicationManager`, and the launched payload all show
`root` / `Uid: 0 0 0 0`.

The one genuinely non-root daemon is the **system** bus (`etc/dbus-1/system.conf` has
`<user>messagebus</user>`), but the launcher is not on that bus and the system bus default denies
`method_call`.

**Answer, stated plainly: literally everything relevant runs as uid 0.** The non-root accounts are
nologin system daemons (dbus messagebus, timesyncd, journal-gateway) that are not attacker processes and
cannot reach the root session bus. V-051's value is therefore **persistence and re-launch** (and a SMACK
app-domain → floor escape for label-confined root code), **not a uid escalation**.

## 3. Path restrictions — appLocation is used verbatim, and CheckSign is skipped by a direct-launch flag, not by path

`/app/bin/AppLauncher` (BuildID `0452df1033bd1bbae15727a83d4d56576d8b9444`). The on-demand dispatcher
installs the caller's `appLocation` into the process object verbatim, with **no prefix allow-list**:

- New-object helper `[0x1fd30,0x1ffcf)` — the only gates are appid range and existence:

  ```asm
  1fd51: leal -0x1(%rsi), %eax
  1fd5d: cmpl $0x3ff, %eax        # appid-1 <= 1023  =>  appid in [1,1024]
  1fd62: ja   0x1ff68             # else reject
  1fd7e: callq QFile::QFile(QString)   # QFile(appLocation)
  1fd86: callq QFile::exists()
  1fd8d: jne  0x1fe28             # proceed only if the path exists
  ```

  (No `/app/bin` or `/tmp/app/bin` prefix comparison — the 44 `/app/bin…` strings in the binary are the
  fixed entries of the startup app table.)

- Existing-object dispatcher `[0x1ffd0,…)` sets the direct-launch flag and copies the caller's path:

  ```asm
  20010: movb $0x1, 0x1c(%rax)    ; direct-launch flag = 1
  20020: movb $0x1, 0x1c(%rbx)    ; (shared tail of both branches)
  2003d: leaq 0x58(%rbx), %rdi
  20044: callq QString::operator= ; program(+0x58) = appLocation
  20076: movl %ebp, 0x20(%rbx)    ; appid(+0x20)
  ```

  The new-object branch (`0x204b5: callq 0x1fd30`, then `0x204d6: jmp 0x2001c`) rejoins this same tail,
  so **every** on-demand request sets `+0x1c = 1`.

**The condition that skips CheckSign** is byte `+0x1c` (the direct-launch flag), not the path string. In
the process-start routine `[0x163f0,0x1854d)`:

```asm
17419: movzbl 0x1f(%rsp), %eax   ; al = dev-override bool (exists("/tmp/app/bin/AppEngineerMode") && appid==0x12d)
1741e: testb %al, %al
17420: jne  0x17ec0              ; dev-override -> start the FIXED /tmp/app/bin/AppEngineerMode
17426: cmpb $0x0, 0x1c(%rbx)     ; direct-launch flag (+0x1c)
1742a: je   0x17e20              ; flag==0 -> SIGNATURE path
                                 ; flag!=0 -> fall through:
17430: movq 0x58(%rbx), %rax     ;   program = +0x58 (the caller's appLocation)
1745d: callq QProcess::start     ;   start(appLocation, args, mode)  -- NO readSection/CheckSign
```

The signature path is only reached when `+0x1c == 0` (startup-group launches, where the manager builds
the AppProcess itself with the flag zeroed by the constructor at `0x15612`):

```asm
17e4e: callq 0x158c0             ; build /tmp/<basename>.sign
17e78: callq 0x15b50             ; readSection() -> extract .sign + signCheck()
17e7d: testb %al, %al
17e7f: je   0x18088              ; verification failed -> error (NO launch)
17eb2: callq QProcess::start     ; verification passed -> launch
```

and the dev-override branch (`0x17420 → 0x17ec0`) also starts without any check:

```asm
17ec0: leaq 0x2f127(%rip), %rdi  # 0x46fee = "/tmp/app/bin/AppEngineerMode"
17ecc: callq QString::fromAscii_helper
17ee9: callq QProcess::start     ; start("/tmp/app/bin/AppEngineerMode", …)
```

**Answer: `appLocation` is used verbatim (existence-gated, no prefix check). CheckSign is reached only
on the `+0x1c == 0` branch; the on-demand D-Bus dispatcher always sets `+0x1c = 1`, so every
request-driven launch — any appid in [1,1024], any path — bypasses `readSection`/`signCheck`/`CheckSign`
entirely.** That is the mechanism of V-051. It is not keyed to the path being outside `/app/bin`; it is
keyed to the request being an on-demand launch rather than a startup-group launch.

## 4. Net reachability statement

- Sending the request requires a session-bus connection, which requires **uid 0** (§1).
- The image has no uid ≥ 1000 accounts and no non-root vendor process, and the launcher never drops
  privileges, so **everything local is already uid 0** (§2).
- The path is unrestricted and unchecked for any on-demand request (§3).

Therefore: **V-051 is not an escalation vector from a non-root uid.** A non-root attacker cannot reach
the root session bus, so it cannot fire the request at all. Its realistic value is (a) as a
**persistence / re-launch** primitive — any already-root, SMACK-confined process can re-exec an arbitrary
payload as a fresh root process under the floor label — and (b) combined with the About-gesture+PIN
(issued by root HMI code) after a payload is staged. The old `/tmp`-write framing is obsolete: V-051 needs
no key, no `.sign`, and no specific directory — only one session-bus message from a uid-0 context.

## 5. Evidence locations

- Session bus: `etc/dbus-1/session.conf`, `etc/dbus-1/system.conf`, `lib/systemd/system/Dbuslaunch.service`,
  `app/bin/Dbuslaunch.sh`; bus-uid measurement `work/vm/signprobe` `/run-busuid.sh`
  (`work/vm/signprobe-build/runas.c`, `run-busuid.sh`, `run_busuid.py`; decoded `/tmp/busuid-out.b64`).
- Accounts/units: `etc/passwd.legacy`, `etc/passwd.secure`, `etc/passwd-`, `etc/group`,
  `lib/systemd/system/*.service` (grep `User=`), `AppLauncher` dynamic symbols (`llvm-nm -D`).
- Disassembly (`llvm-objdump -d --no-show-raw-insn` of `AppLauncher`): `0x1fd30–0x1ffcf`, `0x20010`,
  `0x20020`, `0x17419–0x1745d`, `0x17e20–0x17eb2`, `0x17ec0–0x17ee9`; strings `/tmp/app/bin/AppEngineerMode`
  at `0x46fee`, `/tmp/app_normal.key` at `0x46e1e`.
