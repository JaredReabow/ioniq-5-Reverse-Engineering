# USB volumes and on-screen gestures: every route to the engineering/develop state

Read-only static analysis of EU Gen5W Linux `NE_E.EUR.S5W_L.001.001.260128`, x86-64.
No VM was booted, nothing was executed, no image or unit was modified.

Path shorthand: `$ROOTFS` = `work/decrypted-eu-260128/extracted-safe/mango-rootfs`.
Addresses are virtual addresses inside the named ELF. In every binary used here the
first `PT_LOAD` has `p_vaddr == p_offset`, so file offset and VA are interchangeable.

Confidence labels: **[E]** evidenced (string, instruction or file quoted with its
location); **[I]** inferred (reasoning only, no measurement). Every hypothesis carries
an explicit *falsified if* condition.

Builds on, and does not re-derive, `docs/engineering-mode/dev-mode.md` (the `+0x13c`
token, `setEngType()`, the launcher `/tmp` preference) and
`evidence/appdmclient-fumo-usb-eligibility.md` (FUMO/SCOMO separation, TE/TE2 trailer,
`-404`/`-403` verifier results). Two corrections to those notes are in §1.5.

---

## 0. Bottom line

1. **The `VarUpgrade` container is the earliest USB-content branch in `AppDMClient`,
   and it is entered only when the normal package verification *failed*.** It then
   requires the container itself to pass the same `teruten5_pub.key` verifier, so a
   payload cannot be attacker-chosen — but the *path* to it can, and that path is
   interpolated into an unquoted shell command. **[E]** for the literals and the
   ordering, **[I]** for end-to-end reachability.
2. **Six processes react to a USB insertion; five of them run as root, and three of
   them parse attacker-supplied file content.** `lightmediascannerd` is the broadest
   (12 format plugins over the whole tree). **[E]** for services, labels and plugin
   inventory, **[I]** for the uid mapping.
3. **The three most promising odd-input vectors** are (a) the mount-path/volume-label
   string reaching `system()` unquoted in `AppDMClient` and `usb-automount`, (b) the
   LightMediaScanner format plugins (`asf`, `id3`, `mp4`, `matroska`, `jpeg`, `png`,
   `m3u`, `pls`) parsing untrusted files as root, (c) a USB directory layout that makes
   the unit treat the stick as an update carrier (`AppUpgrade` + `.lge.upgrade.xml` +
   `VarUpgrade` + `HU/images/startFromUsb`).
4. **The documented "tap the software version 5–10 times, then PIN" gesture does not
   exist in `AppSetup` in this image.** There is no tap counter and no PIN keypad
   anywhere outside `AppEngineerMode` itself. A 5-tap counter *does* exist, but on the
   N-Mode Manual screen in `AppHomeScreen`, and it opens a performance-timer test menu,
   not engineering mode. **[E]**

---

## 1. Task 1 — what `AppDMClient` requires to accept a `<usb>/VarUpgrade`

### 1.1 Where the branch sits

All of this is inside `int AppDMClientEngine::launchAppUpgrade(QString)` (FDE
`0x7ff60..0x830e4`; every log line inside it embeds the string
`"int AppDMClientEngine::launchAppUpgrade(QString)"`). The function is called directly
from the USB-mount slot, so this is a mount-time path.

Order of operations, with the branch decisions:

| VA | Instruction | Meaning |
|---|---|---|
| `0x80165`–`0x80196` | `"%1/AppUpgrade"` (`0x17397f`, 13 B) + `.arg(<usb path>)` | source `<usb>/AppUpgrade` |
| `0x801ab`–`0x801ef` | `"/update/usb/bin"` + `"%1/AppUpgrade"` | destination `/update/usb/bin/AppUpgrade` |
| `0x8020c`–`0x80292` | `"%1/.lge.upgrade.xml"` (`0x17531e`, 21 B) | source `<usb>/.lge.upgrade.xml` |
| `0x802db` | `call 0x34870` | `errAppUpgrade` → `[rsp+0x10]` |
| `0x80320` | `call 0x34870` | `errXML` → `[rsp+0x18]` |
| `0x804d7`–`0x804e3` | `cmp`-helper `0x8b0b0` | `<usb path>` is-null → bail out `0x823e0` |
| `0x804f8`–`0x8050d` | compare with `"/update/sysroot"` (`0x174968`) | local sysroot source → skip the VarUpgrade block, jump `0x807d0` |
| `0x8051b` | `"%1/VarUpgrade"` (**`0x17534d`**, 13 B) | `<usb>/VarUpgrade`, stored at `[rsp+0x28]` |
| `0x80552`/`0x80569` | `"/tmp/app/bin"` (`0x17535b`, 12 B) + `"%1/AppEngineerMode"` (**`0x175368`**, 18 B) | `/tmp/app/bin/AppEngineerMode`, stored at `[rsp+0x20]` |
| `0x805a0`–`0x805a8` | `or eax,[rsp+0x18] ; jne 0x80fc0` | **either verifier result nonzero → the VarUpgrade handler** |
| `0x805a8`→`0x80656` | log `"No Hash error with AppUpgrade and XML => Will Go to Normal USB Upgrade !!!"` (`0x178f08`, line `0x6cf`) | both zero → normal signed-package path |

**The trigger condition is inverted relative to what "VarUpgrade" suggests**: the
handler is entered when `<usb>/AppUpgrade` *or* `<usb>/.lge.upgrade.xml` failed
verification. It is the "unverified package" fallback, which is also why it is the
earliest branch that touches attacker-chosen USB bytes. **[E]**

### 1.2 The handler's requirements, in execution order

Handler FDE starts at `0x80fc0` (adjacent to `launchAppUpgrade`, same frame).

| # | Check | VA | Literal | On failure |
|---|---|---|---|---|
| 1 | `QFile::exists(<usb>/VarUpgrade)` | `0x80fc0`–`0x80fcc` | — | `je 0x80675` → normal USB upgrade, no message |
| 1b | *(log only)* | `0x8107a` | `"VarUpdate is Exist in USB Memory => Run VarUpgrade !!!"` (`0x178f58`, line `0x6d5` = 1749) | — |
| 2 | `errVarUpdate = 0x34870(<usb>/VarUpgrade)` | `0x810ba`–`0x810c5` | verifier wrapper builds `"/app/share/AppUpgrade/"` + `"teruten5_pub.key"` (`0x172c…`, 16 B key name) | see #3 |
| 3 | `test r12d,r12d ; jne 0x82240` | `0x811a7`–`0x811aa` | log `"errVarUpdate : "` (`0x17537b`, line `0x6d8`) then `"VarUpdate hash fail!! : "` (**`0x1753c1`**, line `0x6f7`) and `"GO Ahead for USB Update !!!"` (`0x1753da`) | falls through to the *normal* USB-upgrade path at `0x8066d`; the VarUpgrade is simply not applied |
| 4 | `QProcess::execute("mkdir -p /tmp/app/bin")` | `0x811b0`–`0x81217` | `"mkdir -p %1"`, `"/tmp/app/bin"` | — |
| 5 | `getKeyFile()` via `0x365b0` (3 attempts, 100 ms apart) | `0x8123a`–`0x81269` | — | `jne 0x82990` → `"getKeyFile() is fail!!!!"` (**`0x1753a8`**, line `0x6f1`) → return `-4` |
| 6 | `system(<pipeline>)` | `0x81454`–`0x814a0` (call at `0x814a0`) | `"/app/share/AppUpgrade/DecryptToPIPE"`, `"%1 -d %2 %3 0 | "`, `"dd of=%1 bs=512"` | return status ignored |
| 7 | `QFile::remove(<key temp>)` | `0x814bd`–`0x814cd` | — | — |
| 8 | `QProcess::execute("chmod +x /tmp/app/bin/AppEngineerMode")` | `0x814e2`–`0x81524` | `"chmod +x %1"` (**`0x17539c`**) | — |
| 9 | `system("dbus-send …")` | `0x81529`–`0x81584` | `"dbus-send --system --type=signal /com/lge/car/micom/can com.lge.car.micom.can.NotifyKeyFrontSpecialEvent array:byte:1,10,1"` (`0x178fb8`) | — |

The assembled shell command (built by three chained `QString::arg` calls at
`0x8126f`–`0x81344`, `QString::append` at `0x81344`, stored at `[rsp+0xa0]`) is
exactly:

```
/app/share/AppUpgrade/DecryptToPIPE -d <key-temp> <usb>/VarUpgrade 0 | dd of=/tmp/app/bin/AppEngineerMode bs=512
```

* `%1` of `"dd of=%1 bs=512"` = `[rsp+0x20]` = the string built from
  `"%1/AppEngineerMode".arg("/tmp/app/bin")` at `0x80578` — i.e. the *destination* is
  `/tmp/app/bin/AppEngineerMode`. **[E]**
* `%2` = `[rsp+0x38]`, a temp path generated under `/tmp` (`"/tmp"` at `0x800da` →
  helper `0x32c20`), removed at step 7. **[E]**
* `%3` = `[rsp+0x28]` = `<usb>/VarUpgrade`. **[E]**
* Nothing in the pipeline quotes `%3`. **[E]**

### 1.3 What the verifier at `0x34870` actually checks

`0x34870` is shared with the normal path (called at `0x802db` and `0x80320`). It builds
`/app/share/AppUpgrade/teruten5_pub.key` from `"/app/share/AppUpgrade/"` and the literal
`"teruten5_pub.key"` via `"%1%2"` (`0x34870`–`0x34911`), loads the key, and calls the
linked verifier at `0x121040`, whose trailer parser (`0x11fe20`) seeks to
`file_size - 0x4024`, requires the fixed suffix to begin `TE` with third byte `R` or `2`,
and returns `-404` when no such trailer exists, `-401`/`-402` for size/read failures and
`-403` when the 32-byte comparison fails (established in
`evidence/appdmclient-fumo-usb-eligibility.md`; not re-derived here). **[E]** via that
note.

For `VarUpgrade` only the literal value `0` passes (`test r12d,r12d ; jne fail`). Note
this is *stricter* than the normal path, where `-404/-404` is an accepted plaintext
mode when `/update/disableEncryptionUpdate` is present. So:

* a **plaintext** (unsigned) `VarUpgrade` file is rejected at step 3; **[I]** from the
  `== 0` test, falsified if a `-404` container ever reaches step 4;
* what passes must be a `TE`/`TE2` container signed by the vendor key and encrypted
  with the credman-derived key.

### 1.4 What an attacker would therefore need to place on the stick

| Element | Required | Evidence |
|---|---|---|
| A mounted volume under `/media/usb/<port>/` | yes | `usb-automount` mount path, §2 |
| `VarUpgrade` at the **root of that volume** (file or directory; `QFile::exists` is true for both) | yes | `0x17534d`, `0x80fc5` |
| `<vol>/AppUpgrade` **or** `<vol>/.lge.upgrade.xml` present-but-failing verification, so that `errAppUpgrade \| errXML != 0` | yes | `0x805a0` |
| `VarUpgrade` carrying a valid `TE`/`TE2` trailer under `teruten5_pub.key` | yes | `0x34870`, `0x11fe20` |
| The credman key service answering `getKeyFile()` | yes | `0x365b0`, `0x82990` |
| A volume label that survives into the mount path unquoted | no — but it changes *what command runs* | `0x812f0`, `0x814a0` |

**Conclusion.** As a *payload* route the `VarUpgrade` container is cryptographically
gated: the attacker needs a vendor-key-signed TE2 container. As a *command* route it is
not gated at all, because the mount path is interpolated into `system()` without quoting
(§3, H1). **[E]** for both halves.

After a successful deployment the binary sits at `/tmp/app/bin/AppEngineerMode`, and
`AppLauncher` will use it in preference to the shipped one for app id `301`
(`0x173c5`–`0x17420`: `QFile::exists("/tmp/app/bin/AppEngineerMode")` at `0x173e1`,
`cmp dword ptr [rbx+0x20], 0x12d` at `0x173ea`, `jne 0x17ec0` at `0x17420`, and at
`0x17ec0` a bare `QProcess::start(<program>, <args>, mode=3)` with no hash, signature or
size check). Note the develop state itself still cannot be reached by *relaunching the
shipped* binary (§ dev-mode.md §1.3); this route is about running a *different* binary.

`AppDMClient` also removes the deployed file in at least one cleanup path: `0x85c08`–
`0x85da3` rebuilds `/tmp/app/bin/AppEngineerMode` (`0x17535b` + `0x175368`), logs
`"VarUpgrade is exist in /tmp."` (`0x175a6f`, line `0x535` = 1333) and calls
`QFile::remove` (`0x1c320`). So the `/tmp` deployment is transient. **[E]** for the code,
**[I]** for which event drives it.

### 1.5 Two corrections to the earlier notes

* `QFile::copy` is **imported but never called**. The `.rela.plt` entry is
  `_ZN5QFile4copyERK7QStringS2_` at stub `0x1d0d0`, and a full scan of
  `.text` (`0x1d1b0..0x1723b3`) finds **no** `call 0x1d0d0`. The copy the earlier note
  inferred is a shell command: `system("cp -f %1 %2")` at `0x82913`–`0x8296b`, with
  `%1` = `<src>/AppUpgrade` and `%2` = `/update/usb/bin/AppUpgrade`. **[E]**
* The note "a nonzero pair can enter an optional `VarUpgrade` branch" is right, but the
  consequence deserves to be spelled out: nonzero means *verification failed*, so
  `VarUpgrade` is not a "second signed channel", it is the failure handler. **[E]**

---

## 2. Task 2 — everything that runs on USB insertion

`usb-automount` is a `Restart=always` system service
(`lib/systemd/system/usb-automount.service`, `ExecStart=/app/bin/usb-automount`,
`After=dbus-com.lge.car.micom.service`). No unit in `$ROOTFS/lib/systemd/system/` uses
`User=` or `Group=` except `user@.service`, and every media/upgrade consumer sets
`XDG_RUNTIME_DIR=/var/run/user/root`. **All of the processes below therefore run as
root**; SMACK labels come from `etc/smack-relabel-ro.sh`. **[E]** for the units, **[I]**
for "root by systemd default".

| # | Component | Trigger | User / SMACK | Parses attacker file **content**? |
|---|---|---|---|---|
| 1 | kernel + udev (`lib/udev/rules.d/60-persistent-storage.rules`, `60-block.rules`, …) | block device add | root (udev) | **No.** Consumes superblock metadata only to populate `ID_FS_*`; the only `RUN+=` rules that execute host scripts are gated on `TEST==` of fixed host paths (`99-static-ip.rules`, `10-mirrorlink_rename.rules`), not on USB content. **[E]** |
| 2 | `usb-automount` (`app/bin/usb-automount`) | udev netlink, `KERNEL=="d*"`/partition, `SUBSYSTEM` block | root, `App::usb-automount` (`etc/smack/accesses.d/usb-automount`) | **Indirectly yes.** Mounts with `mount(2)` (no shell) but builds the mount point from `ID_FS_LABEL` / `ID_FS_UUID` and later interpolates the resulting path into `system()`/`popen()` in the MTP branch. **[E]** |
| 2b | `usb-automount` D-Bus | emits `UsbMount` / `UsbUnMount` on `com.lge.car.automount` at `/com/lge/car/automount` | root | names only (mount path, port index, uuid/label strings) |
| 3 | `AppDMClient` (`app/bin/AppDMClient`, `App::upgrade`) | `registerUsbAutoMount()` (`void AppDMClientEngine::registerUsbAutoMount()`, literal at `0x17…`) connects `1slotUsbMounted(QString,int,QString,QString)` to that signal (`0x4b5cc`–`0x4b651`); `UsbUnMount` to `0x4b73f` | root, `App::upgrade` (`smack-relabel-ro.sh` `APP_09`) | **Yes.** Verifies `<usb>/AppUpgrade` + `<usb>/.lge.upgrade.xml`, parses the XML descriptor, and in the `VarUpgrade` branch runs an unquoted `system()` on a path it does not control. **[E]** |
| 4 | `mediamanager` (`app/bin/mediamanager`, genivi `org.genivi.mediamanager` `IndexerStub`/`PlayerStub`) | `mediamanager.service`; consumes the LMS sqlite index and the automount notification | root, `App::mediaplayer` (`APP_07`) | **No, not directly.** It reads the index (`IndexerStub`) and parses stored URIs (`lge::mm::playlist::ParseUtils::ParseUri`, `ParseParentDirectory`, `libmediamanager_playlist.so`). Any parse of media bytes happens upstream in LMS. **[E]** for the symbols, **[I]** for "no container parsing here" |
| 5 | `lightmediascannerd` (`app/bin/lightmediascannerd`, LMS `0.5.1-5w.master.18-r13`, build path string in the binary) | D-Bus activation, `usr/share/dbus-1/services/org.lightmediascanner.service` (`Name=org.lightmediascanner`, `Exec=/app/bin/lightmediascannerd`); `startup-scan=true` | root, `App::mediaplayer` (`APP_04`) | **Yes — the broadest surface.** `app/bin/lightmediascanner.conf` sets `directory=audio:/media/usb/` (plus `/usr_data/media/`, `/media/mtp/`) and a skip list; the plugin directory holds `asf.so id3.so mp4.so matroska.so ogg.so flac.so wave.so aiff.so jpeg.so png.so m3u.so pls.so`. **[E]** |
| 6 | `MediaBrowser` (`app/bin/MediaBrowser`) | `MediaBrowser.service` | root, `App::mediaplayer` (`APP_03`) | **Indirect.** Queries the LMS database (SQL literals quoting `/media/usb`); thumbnail requests go to `com.lge.thumbnailextractor` → `ThumbnailService::Start()` → a `uridecodebin … appsink` GStreamer pipeline (`evidence/artifacts/media-candidates/README.md`). GStreamer then parses the file. **[E]** via that note |
| 7 | `AppUpgrade` / `AppScomoDM` | not from the mount signal; only after `AppDMClient` stages and verifies (launch at `0x4b9d0` from `launchAppUpgrade`) | root, `App::upgrade` (`APP_10`) | **Yes**, but only after staging: `.lge.upgrade.xml`/package parsing, and `runSmackRuleScriptFromUsb()` executing `"%1/etc/update_start_5w.sh %2"` (`0x2872f3`, `0x28e914`) with `%1 = /rw_data/mnt/root`. **[E]** for the literals, **[I]** for "only reachable post-verification" |
| 8 | `AppMediaPlayer` | active-source UI | root, `App::mediaplayer` (`APP_02`) | **Yes on user action** (playback). Carries the literal `/media/usb/1`. **[E]** |

Notes that matter for ranking:

* Only #3, #5 and #7 (plus #6 via GStreamer) actually consume file *bytes*; #1, #2 and
  #4 consume names/IDs. **[E]**
* `slotUsbMounted` (`0x84700..0x84e2d`) only proceeds when the signal's integer index is
  exactly `1` (`cmp r12d,1 ; je 0x848d8` at `0x84874`/`0x848d2`); the accepted index is
  then stored in `this+0x128` and the same mount path is passed straight to
  `launchAppUpgrade` at `0x849a7`, *before* any version comparison. Two side doors are
  checked first: `/update/extInfoUpdate/ext_units` (`0x848f3`) and
  `/update/force_ua_test.txt` (`0x84945`), both local `/update` markers. **[E]**
* `usb-automount` uses two port directories: the literals `"%s/1"` (`0x71fe`) and
  `"%s/3"` (`0x7203`), matching `/media/usb/1/` and `/media/usb/3/` in
  `app/bin/AMOS.tar` and `/media/usb/1` in `AppMediaPlayer`. So index `1` is one of the
  two physical ports. **[E]** for the literals, **[I]** that index `1` is `front1`
  (`etc/usb-automount.conf`, `front1=…/usb1/1-1/1-1`). *Falsified if* a rear-port
  insertion is observed to produce index `1`.

### 2.1 The mount path itself

`etc/usb-automount.conf` fixes the base and the policy:

```
[mount]
usb=/media/usb
[fs]
rw_mode=enable
[quirk]
support_no_uuid=enable
```

The udev handler (`0x3ef0`ff.) reads `ID_FS_TYPE`, `ID_FS_LABEL`, `ID_FS_UUID`,
`ID_MODEL`, `ID_SERIAL_SHORT`, `ID_ATA_SATA`, `ID_PART_ENTRY_NUMBER` (`0x40f6`–`0x4186`)
and calls `0x3a50(action, port, devnode, fstype, uuid, label, flag)`, which for `"add"`
jumps to `0x4c00(port, devnode, fstype, uuid, label, flag)`. That function:

```
0x4d1a  __sprintf_chk(mountpoint, 1, 0x200, "%s/%d/%s", <base>, port, <label>)   ; 0x78a6
0x4d31  umount2(mountpoint, 3)
0x4d4d  mkdir(mountpoint, 0x1ff)
0x4d70  mount(devnode, mountpoint, "t<fstype>", 0xc0ed000b, "utf8=1")
0x4e34  <declare "UsbMount" signal>(mountpoint, port, …)
```

with `"NoLabel"` (`0x78bb`) as the label fallback and an alternative-UUID path for media
without one (`"USB storage without UUID are detected."`, `"using alternative UUID for
mount."`, `0x77a8`/`0x77d0`). No sanitisation of the label appears between the udev
property read and the `sprintf`. **The mount point is therefore
`/media/usb/<port>/<volume-label>` for a labelled volume.** **[E]** for the format string
and argument order, **[I]** that the third `%s` is the raw `ID_FS_LABEL`; *falsified if* a
volume labelled `L` mounts at a path whose last component is not `L`.

---

## 3. Task 3 — odd inputs, ranked

Ranking is by (reachability without authentication) × (impact if true) ÷ (cost of the
deciding experiment). Each item states what must be true and how to kill it.

### H1 — Volume label reaches `system()` unquoted (highest value)

**Claim.** Two independent sinks take a mount path derived from the volume label into a
shell command without quoting.

* `AppDMClient` `0x814a0`: `system("<DecryptToPIPE> -d <key> <mount>/VarUpgrade 0 | dd
  of=/tmp/app/bin/AppEngineerMode bs=512")`, with `<mount>` = `/media/usb/1/<label>`
  (`0x812f0`, `0x81344`, `%3`).
* `usb-automount` `0x531f` → `system(0x2160)`: `"%s %s %s %s &"` with the MTP mount path
  `"%s/%s"` (`0x52e8`) built from the configured MTP base and the same udev label
  string; and `0x5388`: `popen("cat /proc/mounts | grep %s")` with that path.

**Must be true.** (a) The automount label string is attacker-chosen and unsanitised
(§2.1). (b) A label containing shell metacharacters survives `mkdir`/`mount` — true for
`mount(2)`, which takes a path, not a command line. (c) For the DM sink, a `VarUpgrade`
entry must exist at the volume root so `QFile::exists` passes. (d) Injection text must be
representable in the filesystem's label field (allowed in FAT/exFAT/NTFS labels: `;`,
`$`, `` ` ``, spaces, parentheses; `FAT` limits to 11 bytes and forbids `/`).

**Impact if true.** Arbitrary command execution as root, on insertion, before any
authentication. **[I]** — this is the single most valuable hypothesis in this report and
it is cheap to settle.

**Cheapest in-guest experiment** (disposable projection only, never a vehicle):
1. Build a small FAT32 image whose volume label contains a metacharacter sequence that
   writes a sentinel file (e.g. a label ending in `;` plus a `touch`), with a `VarUpgrade`
   directory at the root and no `AppUpgrade`/`.lge.upgrade.xml`.
2. Insert into the **front** port. Observe: `AppDMClient` log lines
   `"VarUpdate is Exist in USB Memory => Run VarUpgrade !!!"` (proves the branch was
   entered) and whether the sentinel file appears.
3. Repeat with the label neutralised and confirm no sentinel.

**Falsified if** the sentinel never appears *while* the `VarUpdate is Exist …` line does,
or if the mount point turns out not to contain the label (§2.1 falsifier). A second,
purely static falsifier: find a sanitiser between `0x40f6` and `0x4d1a` that rewrites the
label — none was found, but the udev property read → `0x3a50` argument shuffle was not
fully unrolled.

### H2 — Media metadata parsed as root by the LMS plugin set

**Claim.** `lightmediascannerd` walks `/media/usb/` and hands every candidate file to a
per-format plugin in-process, as root, with no sandbox.

**Must be true.** (a) The scan covers the inserted volume (it does:
`directory=audio:/media/usb/`, `startup-scan=true`). (b) The plugins are the ones that
open and parse content — `asf.so`, `id3.so`, `mp4.so`, `matroska.so`, `ogg.so`,
`flac.so`, `wave.so`, `aiff.so`, `jpeg.so`, `png.so` all import `lms_db_audio_*`/
`lms_db_video_*` and `lms_plugin_open`, and the repo already records ASF parsing under
`/media/usb` in `evidence/artifacts/media-candidates/lightmediascanner-asf-evidence.txt`.
(c) At least one defect exists in the exact shipped plugin. The repo's
`ZERODAY_ASF_REPORT.md` claims two `asf.c` bugs with a ~4 GB `lightmediascanner_apic_save`
size, which the ASF evidence above did **not** reproduce (the scan completed with zero
errors), so this is live but unproven. **[I]**

**Impact if true.** Heap corruption in a root process during indexing; the most direct
path from "file on a stick" to privileged code execution.

**Cheapest experiment.** In the projection, place one file per plugin family at the
volume root and read `lightmediascannerd`'s exit status and dmesg; then, per family,
bisect with a single mutated field. The decisive (cheap) step is not a crash hunt but a
*reachability* check: confirm the daemon's pid, uid (`/proc/<pid>/status`) and the fact
that it opened the file (`/proc/<pid>/fd`), which is minutes of work and settles (a)/(b)
for good. Everything beyond that is fuzzing.

**Falsified if** the daemon turns out to run as a non-root uid, or if `jpeg`/`png`/`m3u`
turn out not to be loaded for a `audio:all-category` parser selection — `parser=` is set
to `audio:all-category` in the shipped config, so image plugins may not be invoked at all
for audio indexing. **This is the most likely way H2 collapses, and it should be checked
first.**

### H3 — Directory layout that makes the unit treat the stick as an update carrier

**Claim.** The unit reads update state from fixed top-level names on the volume, so
layout alone (no valid package) drives the DM into staged/update states.

The layout facts, all **[E]**:

| Path on the volume | Literal | Consumed at | Effect |
|---|---|---|---|
| `<usb>/AppUpgrade` | `0x17397f` | `0x80165` | verified, then staged to `/update/usb/bin/AppUpgrade` |
| `<usb>/.lge.upgrade.xml` | `0x17531e` | `0x8020c` | verified; supplies the descriptor `version` |
| `<usb>/VarUpgrade` | `0x17534d` | `0x8051b` | the fallback container, §1 |
| `<usb>/HU/images/startFromUsb` | `0x175445` | `0x80d18`, `0x80f20` | **marker only**: if present, the `cp -f` staging step at `0x82913` is skipped and the DM jumps straight to the launch log `"just copy : strAppUpgradeXmlPath = "` (`0x80e16`) |

`_system_SWUP.txt` is *produced* by the updater (`" Copy, Temp File -> *_system_SWUP.txt"`
in `AppDMClient` and `AppUpgrade`), not read from the volume; `.ver` was not found as a
consumed name in either binary. The literal `"/update/VCRM_SW_UPDATE_TYPE"` (`0x175229`)
is a local `/update` marker. So the interesting element is `HU/images/startFromUsb`,
which lets an attacker tell the DM "the caller already staged `AppUpgrade`", removing one
copy step from the flow.

**Must be true.** That skipping the copy has an observable effect on which binary is
executed (the launch target is fixed at `/update/usb/bin/AppUpgrade` either way, so this
looks like a no-op for an attacker). **[I]** that it is low-impact.

**Cheapest experiment.** With a volume containing only `HU/images/startFromUsb` plus a
non-verifying `AppUpgrade`, diff the DM log against the same volume without the marker;
look for `"just copy"` and for the presence/absence of `fileCopy : strAppUpgradeFullPath`.

**Falsified if** the two logs are identical — then the marker is decorative.

### H4 — Playlists whose entries are dereferenced

**Claim.** `.m3u`/`.pls` files on the stick cause the unit to open further paths,
including absolute or `..`-relative ones.

**What is evidenced.** `m3u.so` and `pls.so` exist and import `lms_db_playlist_new`,
`lms_db_playlist_add`, `lms_db_playlist_start`; they therefore *parse* playlist text and
store entries. They do **not** import `open`/`fopen` beyond the scanner's own
`lms_plugin_open`, and no instruction path from `lms_db_playlist_add` to a file open was
traced. **[E]** for the imports, **[I]** for "parsed but not dereferenced at index time".

**Must be true.** That a downstream consumer (`mediamanager` playlist builder or
`AppMediaPlayer`) resolves stored entries and opens them, and that a `..`/absolute entry
escapes `/media/usb`. If `lms_db_playlist_add` stores only the raw string and the player
resolves it later, the impact is a file-existence/read oracle, not memory corruption.

**Cheapest experiment.** Place `A.m3u` containing a single absolute path to a file
outside `/media/usb` (e.g. under `/app`) and a second entry pointing at a deliberately
malformed media file. Watch whether *that* file is opened (`/proc/*/fd`, DLT logs) even
though it lives outside the scan root.

**Falsified if** the entry strings appear in the LMS database but no process ever opens
the referenced path.

### H5 — Filenames with unusual characters, very long names, format-string characters, traversal

**Claim.** A filename itself (`%n`, `%s`, 4 KB names, `../`) affects a privileged
formatter or path join.

**What is evidenced.** LMS passes names through `lms_charset_conv` with
`chardet-level=3` and `lms_which_extension` for dispatch — encoding conversion, not
`printf`. LMS skip-dirs are literal (`/lost+found/`, `/$RECYCLE.BIN/`, …). No `%n`
format sink into which a filename flows was found in the mount-time set; the two
`system()` sinks take a *directory* path (H1), not a filename. Mount points are created
with `mkdir(2)` and mounted with `mount(2)`, so `..` in a label collapses the path
(`/media/usb/1/..` = `/media/usb`) rather than escaping it. **[E]** for `mount(2)`/
`mkdir(2)`, **[I]** for "no format-string sink".

**Impact if true.** Low-to-moderate (path confusion or a charset-conversion crash), and
strictly dominated by H1 unless H1 is falsified.

**Cheapest experiment.** One volume with: an 11-byte FAT label of `..`; a 255-byte
filename containing `%n%n%s` and a newline; and a nested directory named `..%2f..`. Then
read `AppDMClient`'s `a_strFullPath: [` log (`0x8008c`) to see the exact string that
reaches the verifier and the shell.

**Falsified if** the logged `a_strFullPath` is normalised, or if the label `..` mount
fails harmlessly.

### H6 — `VarUpgrade` accepted with an attacker-chosen payload

**Claim.** The container's key/hash check can be satisfied by a well-formed but
attacker-made payload.

**Status.** Refuted as stated for a *payload* attack: only verifier result `0` passes
(`0x811a7`), and `0` requires the fixed `TE`/`TE2` trailer to validate under
`teruten5_pub.key`. **[E]**

**Falsified if** a `VarUpgrade` that returns `-404` (plaintext, no trailer) is observed to
reach step 4 (`mkdir -p /tmp/app/bin`). This is a one-line observation, and the earlier
`-404/-404` plaintext contract on the *normal* path makes it worth confirming rather than
assuming.

**Note on interaction.** The repo's only plaintext lever is
`/update/disableEncryptionUpdate`, a *local* `/update` marker that `AppDMClient`'s helper
`0x696f0` tests (`QFile::exists` inverse, called at `0x80bbb`). Nothing on a USB volume
creates it; `AppMPAutoTest` does, on MICOM event `EVT_MP_ENCRYPTION_DISABLE_REQ`. So H6
collapses into "first get a local privileged marker write", i.e. it is not a USB vector.

### H7 — On-screen interaction reaching the develop state

**Claim.** A gesture sequence toggles `AppEngineerModeEngine+0x13c` or selects a
develop binary.

**Status.** No such gesture exists in this image — see §4. The `+0x13c` field is written
only by `setEngType()`, which stores `1` unconditionally, and the QML that reads it only
*shapes* the menu. So the only on-screen contribution available is "start app id 301",
which is a prerequisite for the `/tmp` override, not a state change. **[E]** per
dev-mode.md §1.3 and §4 below.

---

## 4. Task 4 — the About-screen gesture in this image

### 4.1 `AppSetup` has no tap counter and no PIN path

* `app/share/AppSetup/` ships **2,346** `.qml` files across `qml_new2.0`, `qml_eco3.0`,
  `qml_genesis` and `localize`/`data`. A grep for `tapCount`, `tap_count`, `clickCount`,
  `clickedCount`, `pressCnt`, `tapCnt`, `secretCnt`, `hiddenCount` returns **zero** hits.
  **[E]**
* The software-version screen
  `app/share/AppSetup/qml_new2.0/general/Q_AppSettingSysInfoVersion.qml` (489 lines; the
  `qml_eco3.0` and `qml_genesis` variants are 490 and 494 lines) contains exactly **one**
  `MouseArea`, at lines 337–348:

  ```qml
  /* Virtual knob button */
  MouseArea{
      visible: isDefaultState
      width: 141
      height: 78
      y: 400
      x: 763

      onClicked: {
          console.log("Clicked!!!")
          AppSettingModel.sendVirtualPressComand(0x02);
      }
  }
  ```

  It sends a virtual knob press; it does not count taps and does not open a keypad.
  **[E]**
* `checkPassWord` — the only native entry point that consumes PIN digits — appears in
  exactly **one** QML file in the whole image:
  `app/share/AppEngineerMode/qml/AppEngineerMode_PinCodeKeypad.qml`. No `AppSetup`
  screen references `AppEngineerMode` at all; the binary's only engineering strings are
  `APP_SETTING_FACTORY_RESET_ENGINEERMODE`,
  `slotNotifyFactoryResetEngineerMode(int)`, `SetEngineerModeCameraBrightness` and the
  data paths `/app/data/AppEngineerMode/dynamicmenu`,
  `/app/data/AppEngineerMode/feedbackupdate`. **[E]**
* The literal `19491003` does not occur anywhere in the extracted firmware tree
  (recursive grep over `$ROOTFS` and the sibling `appnavi`, `new-gui`, `mango-rwdata`,
  `update` trees returns nothing). That is consistent with the earlier finding that the
  accepted PIN is not stored as a constant, and it means the "19491003" figure cannot be
  confirmed or refuted from these components. **[E]** for the absence, **[I]** for the
  interpretation.

**Conclusion for `AppSetup`:** the documented gesture (Settings → General → About → tap
the version 5–10 times → PIN keypad) is **absent** from `AppSetup` in this image. If it
exists on a real unit, it is not in `AppSetup`'s QML and must be either a native input
filter in a different binary or a feature of another build.

### 4.2 The three related gestures that *do* exist, and where they lead

| Gesture | Location | Destination | Engineering mode? |
|---|---|---|---|
| 5 taps on the bottom-right 200×90 region of the N-Mode **Manual** screen | `app/share/AppHomeScreen/qml_new2.0/HomeScreen/Screen_HomeScreen_Manual.qml:22` (`property int _count: 0`), `:337`–`:346` (`_count++; if(_count === 5) QML_Handler.qmlChangeTopMsg(HMIEVENTS.EVT_GOTO_N_MODE_TEST)`) | `EVT_GOTO_N_MODE_TEST` → `AppHome_Enum.E_OPT_N_MODE_TEST_LIST` in `qml_new2.0/popup/QOptionMenu.qml:713`, i.e. the N-mode **performance-timer** list (`NMode/PerformanceTimer/Q_NMode_PT.qml`) | **No** |
| 3-2-8-9-6-5 tap pattern on the Manual panel | **not present**: all three `AppMediaPlayer/…/screens/setting/Screen_Manual.qml` variants contain **zero** `MouseArea` and zero `onClicked` (240/247/280 lines) | — | **No** (consumed natively, if at all) |
| Back-key sequence | `app/bin/AppCamera`: `UseBackKeyForEngMode`, `connectEngModeBrightness`, `1slotAppLaunchOverEngMode(int)` | AppCamera's own engineering brightness page | **No** — a per-app settings page, not the develop state |

The `_count` gesture exists only in the `qml_new2.0` variant; `qml_eco3.0` and
`qml_genesis` have no `_count` at all. **[E]**

### 4.3 What this means for the develop state

Because `setEngType()` writes `1` unconditionally on every start of the shipped binary,
no gesture can flip `+0x13c` on this build; a gesture can only (a) open the PIN pad
inside `AppEngineerMode`, which selects between `EngineerModeWarning` and
`EngineerModeMain` after the PIN, or (b) cause `AppLauncher` to start app `301`, which is
only interesting once `/tmp/app/bin/AppEngineerMode` exists (§1.4). **[E]** for (a) and
(b), **[I]** for "no other gesture exists" — *falsified if* a native input filter that
counts taps is found in a UI binary other than the four named above.

---

## 5. Experiment plan

All steps are read-only or disposable-projection only. Nothing here should be attempted
on a vehicle or on the owner's installed unit. Order is cheapest-decisive first; each
step names the observation that ends the question.

| Order | Question | Method | Decisive observation | Kills |
|---|---|---|---|---|
| 1 | Does the mount path contain the volume label? | Static follow-through of `ID_FS_LABEL` → `0x3a50` → `0x4c00`; or in the projection, insert one labelled and one unlabelled volume. | `AppDMClient` log `a_strFullPath: [` (`0x8008c`) shows `/media/usb/1/<label>`; `mount` output agrees. | H1, H5 |
| 2 | Which port yields slot index `1`? | Insert into front, then rear; read `USB mount path:` / `, index:` (`0x84800`/`0x8481a`). | index `1` on the front port. | the §2 caveat and `dev-mode.md` §5 row B |
| 3 | Is `VarUpgrade` really only entered on verifier failure? | Place a volume with a `VarUpgrade` entry but *no* `AppUpgrade`; read for `"No Hash error with AppUpgrade and XML"` vs `"VarUpdate is Exist in USB Memory"`. | the second line appears without the first. | §1.1 |
| 4 | Does a plaintext (`-404`) `VarUpgrade` pass? | Volume with an unencrypted `VarUpgrade` and a failing `AppUpgrade`; watch for `"VarUpdate hash fail!! :  -404"` vs `mkdir -p /tmp/app/bin`. | `hash fail` appears. | H6 |
| 5 | Does LightMediaScanner actually scan and open USB files as root? | Process identity + `fd` table while a stick is inserted. | `/proc/<pid>/status` uid `0`; the file is in `fd/`; `parser=audio:all-category` means image plugins are *not* loaded. | H2 (both directions) |
| 6 | Are playlist entries dereferenced? | `A.m3u` with an out-of-root absolute path; watch `fd` tables and DLT. | the outside file is opened, or it is not. | H4 |
| 7 | Is `HU/images/startFromUsb` load-bearing? | Two volumes differing only by that marker; diff DM logs. | identical logs ⇒ decorative. | H3 |
| 8 | Is there any native tap filter? | Cross-reference the four known gesture sites against every UI binary's input handlers; specifically look for a counter compared to 5/7/10 near a mouse-event handler in `AppSetup`, `AppHomeScreen`, `AppMediaPlayer`, `ApplicationManager`. | a counter with a launch of app `301`. | §4.3 |

Evidence to capture in every step, so a negative result is still publishable: the
`AppDMClient` DLT/log stream around the insertion, `mount` output, `ps -eo pid,user,label,cmd`
plus `/proc/<pid>/status`, and the exact bytes/`sha256` of the volume image used.

---

## 6. Bounds of this report

* Static only. No `qemu`, no boot, no flash, no modification of the image, the owner's
  unit or any `vm/` artefact.
* One file created: this one. No other edit.
* Coverage: full disassembly of `AppDMClient::launchAppUpgrade` (`0x7ff60..0x830e4`) and
  the `VarUpgrade` handler, the verifier wrappers `0x34870`/`0x365b0`, the automount
  registration at `0x4b5cc`, `slotUsbMounted` (`0x84700`), the cleanup path at `0x85c08`;
  targeted disassembly of `usb-automount` (`0x3a50`, `0x3ef0`, `0x40f6`, `0x4c00`,
  `0x5280`), `AppLauncher` (`0x173c5`, `0x17419`, `0x17ec0`); string/xref sweeps of
  `AppUpgrade`, `mediamanager`, `MediaBrowser`, `lightmediascannerd`; a PLT/import map
  for `AppDMClient` and `usb-automount`; all 209 unit files; all `app/share/AppSetup`
  QML; the three `AppMediaPlayer` and three `AppHomeScreen` `*Manual.qml` variants; the
  twelve LMS plugins' import lists. "Not found" always means not found by these searches.
* Not settled, and named so it is not mistaken for settled: the `ID_FS_LABEL` →
  `0x4c00` argument shuffle was read but not unrolled instruction-by-instruction past
  `0x4431`; the event that drives the `/tmp/app/bin/AppEngineerMode` cleanup at `0x85c08`
  was not identified; whether the LMS daemon loads the image plugins under
  `parser=audio:all-category` was not determined; and no defect was confirmed in any
  shipped parser.
