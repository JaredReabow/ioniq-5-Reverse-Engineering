# Runtime test: does the application manager launch an attacker-supplied binary? (V-048)

Status: **measured in the QEMU projection** (work/vm/signprobe, a CoW clone of work/vm/softbackend).
Dynamic test, not static analysis. No hardware. No RSA signature was forged; a freshly generated
2048-bit public key was planted only to observe whether the check's `ret` value changes.

**Verdict: CONFIRMED as a root-code-execution vector — but by a stronger mechanism than V-048
described.** For app id 301 (0x12d, the "dev-override" engineering hook), the manager executes
`/tmp/app/bin/AppEngineerMode` — whatever bytes an attacker placed there — **as uid 0, with no
signature-check line at all**. The check V-048 observed is on the normal startup path only, and its
`ret = 1` is a *pass*, not a failure (see §6). The caller-supplied D-Bus path is not what gets
executed; the fixed dev-override path is.

---

## 1. What was run

Harness: `tools/uk_fw/vm_boot.py`, `vb.run(Path(workspace), True, cmd, timeout=…, memory_mib=2048,
extra_devices=[…])`, python3.13, `init=/init`, `snapshot=on` (guest writes never persist).

Lossless binary channel: `-chardev file,id=…,path=/tmp/signprobe*-out.b64` on
`isa-serial,chardev=…,index=2`, with `busybox base64 … > /dev/ttyS2` in the guest; the guest
evidence log was decoded from that file. Console base64 was not relied on for evidence.

Payload: a **static x86-64 musl ELF** built with zig (`work/vm/signprobe-build/signprobe-payload`,
no `.sign` section, no interpreter), injected into the rootfs as `/run-signprobe-payload`. On start it
writes `/proc/self` identity to `/tmp/signproof-<pid>.txt` and sleeps 90 s. It is placed at
`/tmp/app/bin/AppEngineerMode` (and, for the path-honouring test, at `/tmp/app/bin/sp1…sp12`).

Trigger: the recovered session-bus API
`dbus-send --session --dest=com.lge.avn.applauncher /Request
com.lge.avn.applauncher.request.launch int32:301 string:<name> string:<path>`.

The known-good chain (`/run-chain23.sh` semantics) was reproduced: weston-headless headless backend,
session/system dbus, `micom-dbus-sim`, `persistence-admin-stub`, `dlt-daemon`, then
`/app/bin/AppLauncher 3` (pid 746 in run 1, 757 in run 2, 753 in run 3).

---

## 2. Run 1 — the dev-override launch and process ownership (baseline key state)

`/tmp/app_normal.key` was **not** pre-created (the manager copies its embedded key to `/tmp` on first
use). Thirteen launch requests for app id 301 were sent at uptimes ~29 s through ~270 s, using names
`sp1…sp12` and `AppEngineerMode`. **Every request was accepted** (each produced an `AppID : 301 …
State : 2` transition and a pid).

The manager's own log for the very first request (`sp1`, path `/tmp/app/bin/sp1`):

```
"m_AppProcess->start(/tmp/app/bin/sp1) | time 00:00:29.644"
"AppID : 301, PID : 0, State : 1, Name : sp1 | time 00:00:29.661"
"m_AppProcess->start(/tmp/app/bin/sp1) PID[800] | time 00:00:29.743"
"AppID : 301, PID : 800, State : 2, Name : sp1 | time 00:00:29.767"
```

**No `section name`, no `signCheck`, no `CheckSign` line precedes this launch** (the preceding
`CheckSign` in the log belongs to `/app/bin/AppStandbyClock` at `00:00:24.290`, a different app).

Crucially, the process that actually ran is **not** `/tmp/app/bin/sp1`. The payload's own proof file
and `/proc/<pid>/status` show the dev-override path was executed instead:

```
SIGNPROBE_PAYLOAD_RAN
PID=800 PPID=746 UID=0 EUID=0 GID=0 EGID=0
ARGV0=/tmp/app/bin/AppEngineerMode
EXE=/tmp/app/bin/AppEngineerMode
```

```
A_STATUS: Name: AppEngineerMode PPid: 746 Uid: 0 0 0 0 Gid: 0 0 0 0
A_EXE=/tmp/app/bin/AppEngineerMode
```

All 19 proof files captured in run 1 report `UID=0 EUID=0 GID=0 EGID=0` and
`EXE=/tmp/app/bin/AppEngineerMode`, with `PPID=746` (the AppLauncher). So:

- **The manager launches the fixed dev-override path `/tmp/app/bin/AppEngineerMode`, not the path the
  D-Bus request supplied.** The request's name (`sp1`…) is echoed into the log, but the executed file
  is always `/tmp/app/bin/AppEngineerMode`.
- **It runs as root** (`Uid: 0 0 0 0`, `Gid: 0 0 0 0`).
- **No signature check runs on this path** — there is no `readSection`/`signCheck`/`CheckSign` line for
  `/tmp/app/bin/…`, in contrast to every `/app/bin/*` startup launch which is bracketed by a full
  section dump and a `CheckSign … ret = …` line.

Survival: each payload instance was killed by the manager's registration watchdog, not by a signature
decision:

```
"[TIMEOUT] [9 Group] AppID : 301, PID : 800 | time 00:00:40.002"
```

i.e. ~10 s after start (the payload sleeps 90 s; the ten-second timeout is the manager, matching the
V-048 observation). The manager then relaunches `/tmp/app/bin/AppEngineerMode` on its own (watchdog),
so the payload re-ran repeatedly throughout the window.

## 3. Run 2 — a zero-filled `/tmp/app_normal.key` crashes the launcher inside libcrypto

`/tmp/app_normal.key` and `/tmp/navi_public.key` were pre-planted as 256 zero bytes before the manager
started. The manager read the key and **segfaulted**:

```
[   12.175502] AppLauncher[757]: segfault at 74 ip 00007f886f96c7c4 sp 00007fff512665d0 error 4 in libcrypto.so.1.0.2[7f886f868000+251000]
/run-signprobe2.sh: line 101: 757 Segmentation fault /app/bin/AppLauncher 3
```

The last launcher log line was `signCheck second` (never reached `CheckSign … ret =`), and the explicit
301 request returned `rc=1` (name not owned) with no launch. This proves the verifier **consumes the key
file from `/tmp`** (it is not a fixed embedded read): the contents of `/tmp/app_normal.key` flow into
OpenSSL `libcrypto.so.1.0.2` key parsing.

## 4. Run 3 — a valid-format (wrong) key flips `ret` to 0 and blocks the normal path, but NOT 301

A freshly generated 2048-bit RSA public key (PEM SubjectPublicKeyInfo, `openssl rsa -pubout`, 451 bytes)
was planted at `/tmp/app_normal.key` and `/tmp/navi_public.key` before the manager started.

Normal startup apps now failed verification and were **not** launched:

```
"CheckSign : /app/bin/ApplicationManager /tmp/app_normal.key /tmp/ApplicationManager.sign ret = 0 | time 00:00:12.190"
…
"CheckSign : /app/bin/UserProfileManager /tmp/app_normal.key /tmp/UserProfileManager.sign ret = 0 | time 00:00:12.483"
"m_AppProcess->start(/app/bin/UserProfileManager) PID[0] | time 00:01:02.050"
```

`PID[0]` means no process was created. So on the enforced path **`ret = 0` ⇒ no launch**.

The app id 301 dev-override launch still worked, with no check line, against the same wrong key:

```
"m_AppProcess->start(/tmp/app/bin/AppEngineerMode) | time 00:00:47.024"
"AppID : 301, PID : 0, State : 1, Name : AppEngineerMode | time 00:00:47.028"
"m_AppProcess->start(/tmp/app/bin/AppEngineerMode) PID[782] | time 00:00:47.032"
"AppID : 301, PID : 782, State : 2, Name : AppEngineerMode | time 00:00:47.040"
```

with the payload again reporting `UID=0 EUID=0 GID=0 EGID=0`, `EXE=/tmp/app/bin/AppEngineerMode`.

## 5. Answers to the four requested measurements

1. **Does the manager verify a binary it is asked to launch by an explicit request?** No. For app id 301
   (the explicit-request path) there is no `readSection`/`section name`/`signCheck`/`CheckSign` line for
   `/tmp/app/bin/*`. The verifier only runs on the startup-group path for `/app/bin/*` and `/navi/*`.
2. **Signature-check line and `ret` for the attacker binary.** None appears — there is no `ret` for it.
   The process starts and survives ~10 s, then is killed by `[TIMEOUT] [9 Group]` (registration
   watchdog), not by a signature rejection.
3. **Ownership.** The started child runs as root: `Uid: 0 0 0 0`, `Gid: 0 0 0 0`, and the payload's own
   `getuid/geteuid/getgid/getegid` all returned 0.
4. **Does writing `/tmp/app_normal.key` / `/tmp/<name>.sign` change the check?** Yes, for the *normal*
   path: baseline (embedded key copied to `/tmp`) ⇒ `ret = 1` and launch; wrong valid-format key ⇒
   `ret = 0` and no launch (`PID[0]`); zero-filled key ⇒ libcrypto segfault. It has **no effect on the
   301 dev-override path**, which never consults the key.

## 6. `ret` semantics — correction to the V-048 reading

V-048 read `CheckSign … ret = 1` as "verification failed but launched anyway". The runtime test shows
that reading is inverted, consistent with the static reconstruction in
`docs/engineering-mode/app-signature-check.md` (helpers return `(RSA_verify(...) == 1)`):

- `ret = 1` ⇒ signature **valid** ⇒ launch (the measured baseline; the vendor `.sign` sections verify
  against the embedded key that the manager copies to `/tmp/app_normal.key`). The copy happens only if
  `/tmp/app_normal.key` is absent: run 1 (absent) verified clean, while run 2/3 (pre-planted) read the
  pre-planted bytes instead — so a file an attacker writes to `/tmp/app_normal.key` is the key the
  verifier uses, it is not overwritten by the embedded key.
- `ret = 0` ⇒ signature **invalid** ⇒ **no launch** (run 3, enforced).
- malformed key ⇒ **segfault** in libcrypto (run 2).

So the normal path is fail-closed. The real root vector is not "failed check still launches"; it is that
**app id 301 skips the check entirely and executes the world-writable `/tmp/app/bin/AppEngineerMode` as
root.**

## 7. Reachability caveat (unchanged)

In the projection I trigger app id 301 over the session bus as root. On a stock unit the same app id is
reached through the Settings → General → About version-tap gesture + PIN (external documentation;
equivalent code path present in this image — see FINDINGS-SUMMARY §4) or a VarUpgrade deployment. A
write to `/tmp` is still required to place the binary, and the precise unprivileged path that can write
`/tmp/app/bin/AppEngineerMode` on a stock unit remains unestablished here. Those gaps are unchanged by
this test.

## 8. Artifacts

- `work/vm/signprobe/` — CoW clone used for all three runs (do not confuse with `work/vm/softbackend`).
- `work/vm/signprobe-build/` — payload source/binary, driver scripts, runner scripts, attacker keypair.
- Run 1: guest evidence decoded to `/tmp/signprobe-evidence1.txt`; serial to `/tmp/signprobe-run1-host.log`.
- Run 2: `/tmp/signprobe-evidence2.txt`; `/tmp/signprobe-run2-host.log`.
- Run 3: `/tmp/signprobe-evidence3.txt`; `/tmp/signprobe-run3-host.log`.
- QEMU per-run artifacts under `work/vm/signprobe/runs/<ts>/` (`serial.log`, `command.json`, `result.json`).
