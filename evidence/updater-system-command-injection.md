# AppUpgrade `system()` command construction and `fota_script.txt` execution

Build analysed: `NE_E.EUR.S5W_L.001.001.260128` (EU, Jan 2026), Gen5W, x86-64.
Source of truth: the **decrypted** `AppUpgrade` recovered from the EU package,
`work/decrypted-eu-260128/AppUpgrade`
(sha256 `5295c6e4c41fb9c03760cf006c58b66fcd11aeb4e6e889af6e31b062549b6df0`).

Static analysis only. Nothing was executed on a unit.

## 1. Structure of the binary

`AppUpgrade` is a thin outer ELF (`ET_DYN`, Build ID `167190fb42e2c0eda6e2a3f2c2130759d4484145`)
whose `.text` is only 16,243 bytes; its `.rodata` is 10,746,536 bytes and contains two
complete embedded second-stage executables:

| outer offset | extracted size | sha256 (of embedded extent) |
|---|---|---|
| `0x7c64` | 5,678,432 | `dc11f293e4e8465fe3c23a55c6c6878925104576a719f9bba44cabd24e0d9d39` |
| `0x5721c8` | 5,066,264 | `464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7` |

Extraction was done with the existing repo tool, which stops at each embedded ELF's
structural file extent and never copies sibling bytes:

```
python3 tools/uk_fw/embedded_elf.py work/decrypted-eu-260128/AppUpgrade --extract-dir <dir> --pretty
```

All offsets below are **within the `0x7c64` embedded image**, which is the one that
carries the updater filesystem logic.

## 2. `system()` call sites in the `0x7c64` stage

`system@plt` resolves to `0x2b470`, `popen@plt` to `0x2a290`. All 16 `system()` call
sites were enumerated and their command source resolved:

| call site | command |
|---|---|
| `0x5a935` | `sudo mount -o loop -t ext4 %s %s` (**interpolated**) |
| `0x5a9af` | `sudo umount %s` (**interpolated**) |
| `0x5aa28` | `sudo mount -o remount,rw %s` (**interpolated**) |
| `0x5b6e1` | `echo 1 > /proc/sys/vm/drop_caches` |
| `0x7b3c9`, `0x7b904` | command built in a register via QProcess/QString path |
| `0x150de3`, `0x15dbbf` | `echo [USB-UPDATE] UPDATE FINISH >/dev/kmsg` |
| `0x150dfc`, `0x15dbd8` | `touch /update/headUnitVersionChanged` |
| `0x17f18e` | `killall %1` (Qt `.arg()` template) |
| `0x199950`/`0x199966`/`0x1999aa`/`0x1999df` | `echo {0,1} > /sys/class/gpio/gpio{440,442}/value` |
| `0x1ac603` | popen, mode `"r"` |

The three interesting ones share one code shape: a `__snprintf_chk()` into a 0x400-byte
stack buffer followed **immediately** by `system()` on that buffer.

## 3. The mount helper

Function at embedded offset `0x5a8f0` (thin wrapper at `0x25a2c0`, gated on a global at
`0x8761f0`):

```
5a8f0: push rbx
5a8f1: mov  r9, rdi                 ; 1st arg  -> first %s
5a8f4: mov  edx, 1                  ; __snprintf_chk flag
5a8f9: mov  ecx, 0x400              ; slen
5a8fe: lea  r8, [rip+0x21eecb]      ; 0x2797d0 = "sudo mount -o loop -t ext4 %s %s"
5a905: sub  rsp, 0x418
5a91f: lea  rbx, [rsp+0x8]          ; buffer
5a924: push rsi                     ; 2nd arg  -> second %s
5a92d: call __snprintf_chk
5a932: mov  rdi, rbx
5a935: call system
```

So the effective signature is `mount_image(const char *image, const char *mountpoint)`
and **both arguments reach the shell unmodified**. The sibling helpers at `0x5a970`
(`sudo umount %s`) and `0x5a9e0` (`sudo mount -o remount,rw %s`) are the same shape.

A targeted search of the whole embedded image for any shell-quoting, shell-escaping or
path-sanitising helper (patterns `shell_escape|shell_quote|sanitiz|escapeShell|quoteShell|
valid.*path|filter.*cmd`) returned **zero hits**. There is no quoting layer between the
`%s` substitution and `/bin/sh -c`.

## 4. Where the arguments come from

The only caller of the mount helper chain is inside `_PrepareTargetFS`, at embedded
offset `0x252c78`. The function names itself via a debug string:

```
0x4ecda0: '../packages/processor/updater/updater_fs.c'
0x4ecd80: '[VELIX] : _PrepareTargetFS in\n'
0x4ecdf0: '[VELIX] : _PrepareTargetFS out\n'
```

At the mount call site:

```
2531f0: mov  r9, [r12]              ; scratch buffer base
...     rep stosq                   ; zero a 0x400 buffer
253225: mov  rdi, [r12-0x48]        ; image path   (object member)
25322a: call MountIso_wrapper       ; rsi already = rbp (stack mount point buffer)
```

So the **source image path is an object member at `[r12-0x48]`** and the mount point is a
stack buffer. The ultimate origin of `[r12-0x48]` has **not** been traced in this pass —
see §6.

## 5. `fota_script.txt` is executed from inside the mounted image

Immediately after a successful mount, `_PrepareTargetFS` does:

```
0x253452: lea rsi, 0x4ecdd0          ; "[VELIX] : process script file\n"
0x25345d: lea rbp, 0x4ecae8          ; "fota_script.txt"
0x25346d: lea r8,  0x4eee7f          ; "%s/%s"
0x253493: mov r9,  [r10+0xa0]        ; mount point member
0x25349a: call __snprintf_chk        ; "<mountpoint>/fota_script.txt"
0x2534a2: call 0x256620              ; process script file
```

`0x256620` is attributed by its own debug string to
`'../services/package/package_mgr.c'`. It contains **no** direct `system()`, `popen()` or
`exec*()` call, so it dispatches the script's contents internally rather than handing the
file to a shell. The consequence is that the updater **takes an executable script from
inside the supplied update image** — this is intended vendor behaviour, and it is the
reason the image's authenticity check is the thing that actually matters.

## 6. Status of the third-party `<SrcFullPath>` claim

A public same-platform project (2022 Kia Cerato AU, Gen5W) publishes a `.lge.upgrade.xml`
containing:

```xml
<essentials><SrcFullPath>x;sh /media/usb/pwn.sh #</SrcFullPath></essentials>
```

i.e. the claim is that `SrcFullPath` is interpolated into a shell command. **That specific
mechanism does not apply to 260128**, on three independent grounds:

1. **`SrcFullPath` is not an XML attribute name in our build.** The XML configuration
   parser in the `0x5721c8` stage compares each attribute name against this set:
   `password`, `newfirmware`, `updatespeed`, `imagefiletype`, `src`, `lcdtype`, `vehicle`,
   `ccp`, `rrc`, `vess`, `build-date`, `essentials`, `upgrade-key`, `car-variant`
   (rodata run `0x212400`–`0x2124e0`). `essentials` is present; `SrcFullPath` is not.
2. **The parser reads attributes, not child elements.** The call at `0x7ec97` is
   `QDomElement::attribute(QString const&, QString const&)`, followed by
   `QString::trimmed()` and a name comparison. A `<SrcFullPath>` *child element* inside
   `<essentials>` is therefore never read as a value.
3. **`SrcFullPath` has a different role here.** In our binary it is a map key whose value
   is read with `QVariant::toString()` and compared against an **empty string**
   (`0x9be3d`–`0x9bf51`). If empty, the code issues a D-Bus method call and logs
   `[%s] Requery with another method call.` (`0x280ad8`); if non-empty it logs
   `[%s] SourcePath: %s` (`0x283c14`). The D-Bus target is
   service `com.lge.hkmc.avn.upgrade.fota`, path `/fotaInterface`, interface
   `com.lge.hkmc.avn.upgrade.fota.fotaInterface`, method `mfGetUpdateSrcPath`.
   So `SrcFullPath` is a **FOTA request/reply field**, not updater shell input.

The same project's own "Alternative Attack Vector #2" points at the string that *does*
exist in our build — `sudo mount -o loop -t ext4 %s %s` — but never proves it. The
present work locates and characterises that primitive.

## 7. Assessment

**Established exactly:**

- Our `AppUpgrade` does build shell commands by `snprintf` + `system()`, with `%s`
  substitution and **no** quoting or sanitisation anywhere in the binary.
- Three such commands are privileged filesystem operations on updater-supplied paths:
  `sudo mount -o loop -t ext4 %s %s`, `sudo umount %s`, `sudo mount -o remount,rw %s`.
- The updater executes a script file (`fota_script.txt`) taken from inside the supplied
  update image.

**Candidate, not yet proven — the shell-metacharacter injection:**

For this to be a real defect, an attacker-controlled string must reach one of the three
`%s` slots. That requires resolving `[r12-0x48]` (image path) upward to its origin, and
answering whether any component of it can contain `;`, `|`, `` ` ``, `$(` or newline.

Two guards already visible in the same binary constrain this and must be tested, not
assumed:

- `'[%s] NAVI MAP File [Warning] Filename template does not match'` — navi map filenames
  are compared against a template. Whether a mismatch is fatal or only logged is
  undetermined.
- `'rm -rf /update/HU /update/HU.tar* /update/micom /update/gps ...'` and
  `'/S5W_*.tar /update/usb/.lge.upgrade.xml /update/usb/temp ...'` show the USB side is
  addressed through **fixed** paths (`/update/usb/...`), not through the removable
  medium's volume label. That reduces — but does not eliminate — the chance that a USB
  volume label reaches the `%s` slots.

**Falsification test, in order of cost:**

1. Static: trace `[r12-0x48]` at `0x253225` back to its assignment; record the exact
   producer and whether any character class is filtered.
2. Static: determine whether the navi filename template check aborts or merely logs.
3. VM: run the decrypted `AppUpgrade` against a staged package whose image filename
   contains `;` and observe, from the process's own argv/shell trace, whether the
   injected command is executed. This is a behavioural test of our own binary in our own
   VM and does not require the unit.

**Do not** treat this as a root vector until step 1 or 3 succeeds. It is currently a
command-construction primitive with an untraced argument origin.

## 8. Bounds

- Static analysis of a decrypted vendor binary; no execution, no unit, no USB media, no
  network.
- No exploit payload, no injection string intended for use, no bypass procedure.
- The `fota_script.txt` behaviour is described as vendor design, not as a vulnerability.
- The third-party negative in §6 is a statement about **this** build only; it says nothing
  about the Cerato build it was written for.
