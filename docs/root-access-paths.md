# Root access: every route found, ranked by what it costs to use

The register (`../Ioniq5-VULNERABILITIES.md`) is organised by finding. The remediation report (`REMEDIATION-REPORT.md`) is organised by fix cost. This page is organised the
way an attacker — or a researcher with a unit in front of them — actually thinks: **what would I try, in what order, and what does each attempt require?**

Nothing here has been tried on a vehicle. Each row cites the evidence that exists and says what is still missing.

---

## The short version

| # | Route | Costs | Gets you | Status |
| --- | --- | --- | --- | --- |
| 0 | **USB update TOCTOU (V-059)** | a programmable USB stick. For a **downgrade: nothing else**; for arbitrary content also the unit's TE2 key | installing content that was never verified; **a genuine older image installs with no key and without anti-rollback applying** | **corroborated statically**; not reproduced here |
| 1 | **Serial console (`ttyS2`)** | physical access to UART pads + the root password | a root login prompt | **prompt captured**, password uncracked |
| 2 | **Engineering mode** | **not reachable by gesture on this build** - see below; only via an app-manager request for app id 301 (root, session bus) or a developer path | diagnostic menus | gesture **excluded by enumeration** in QML and in the binary |
| 3 | **A write to `/tmp`** | *any* code execution, any user | root, via three separate anchors | mechanisms demonstrated; **no non-root writer exists here** |
| 4 | **`request.launch` from the bus** | root already (bus is root-only) | arbitrary binary as root, re-launched | **executed as uid 0** |
| 5 | **Removable-media kernel drivers** | a USB stick | potential ring-0 parsing | **20 crafted images, no fault** |
| 6 | **USB SCSI property injection** | a programmable SCSI bridge | a root unit started by udev | payload confirmed (root shell unit); emulator cannot produce the input |
| 7 | **Media parser (GStreamer/LMS)** | a crafted media file | root, if a parser is reachable | components exist and run as root; **parser never exercised** |
| 8 | **WiFi** | root first (three software gates) | a network interface, no shell | hardware present, enable tooling ships |
| 9 | **Firmware downgrade** | a signed older image | an older, possibly weaker build | version gate strict; **anti-rollback unresolved** |

---

## 1. Serial console — the only route that needs no vulnerability at all

**What it needs.** Physical access to the UART pads behind the dashboard, and the root password.

**What is established.** `/etc/esinit_agetty.sh` runs `setsid /sbin/agetty -8 -L ttyS2 115200 xterm`; `/etc/securetty` lists `ttyS2`; the gate is the runtime parameter
`/sys/module/micom/parameters/secure_console`, which **reads 0 by default**, so `esinit` keeps the device and the login proceeds. The prompt was captured from the far
side of the port: `OpenEmbedded 1.0 (none) ttyS2` then `(none) login:` (`../evidence/serial-console/`).

**What is missing.** The password. One SHA-512-crypt hash at a **fixed image-wide salt** in `/etc/shadow.Global`, so one crack covers every unit. Attempted and **failed**:
10,000 four-digit PINs, 34,334 date permutations, and a vendor word list (`CHANGELOG` §4.50.0). That is a statement about 45,000 candidates, not about the hash.

**Cheapest next step.** An offline dictionary/GPU attack on that hash. Because the salt is shared, it is a *fleet* attack, not a per-unit one.

## 2. Engineering mode — **not reachable by the reported gesture on this build**

**Correction (2026-11-05).** The About-screen tap that the field describes is **absent from this firmware**, checked twice: every tap counter in the shipped QML tree was enumerated (three exist,
none near About), and `AppHomeScreen` - the application that owns the settings and About screens - contains **no engineering-mode entry point at all**, only two data paths used by the engineering
application and a slot for a factory reset *while already inside* it.

**What entering it actually needs on this build:** an app-manager launch request for **app id 301** naming a binary - which requires a **root** process on the session bus - or the
developer-path container. Neither is a no-privilege route.

**What it needs (as previously written).** The stock About-screen gesture and a PIN. No cable, no privilege.

**What is established.** The launcher will run `AppEngineerMode` as **root** (`appId 301` from `/tmp/app/bin`), the PIN gate runs (`getEnterPasswordCnt`), and the app's window
is created — it just never attaches a buffer, because its main thread never enters the Qt event loop on this path (`vm/authentic-hmi-apps.md` §7c).

**What is missing.** A shell-bearing menu item. `IpConfigShell` — the facility an external sibling-platform project describes as command execution — does **not** function on
this build: its button lives only in the QML variant production does not load, and the binary's meta-object lacks the slot (`advisory/stock-vector-triage.md`). The production
menu is the short list: scheduled-update history, diagnostics, system config, logging, auto-test.

**So on a stock unit this route gets a technician's menus, not root** — which is what the user suspected, and it is now measured rather than assumed.

## 3. A write to `/tmp` — three independent anchors, one precondition

**What it needs.** Any code execution, at any privilege level, plus the ability to create a file in `/tmp`. `/tmp` is a **`1777` tmpfs** (measured).

**What is established, each demonstrated:**

- **`/etc/passwd` and `/etc/shadow` are symlinks into `/tmp`.** Appending one line produced a working account: `id audit0` → `uid=0(audit0) gid=0(root)`, and `getent` resolved
  it (V-054).
- **`/etc/xdg/weston/weston.ini -> /tmp/weston.ini`** names `shell=`, `backend=` and `ivi-module=`, so the file decides which shared objects the **root** compositor loads
  (V-055). Effect waits for the next compositor start.
- **`/tmp/app_normal.key`** is the trust anchor for binary verification, trusted over the pinned Qt resource (V-048).

**What is missing.** A non-root context to exploit it *from*. Every vendor process observed runs as uid 0, so today this is a *persistence and re-launch* primitive rather than
an escalation. Any future sandboxed component, media parser or lesser user changes that immediately.

## 4. `request.launch` — root code execution, for something that is already root

**What is established.** The application manager executes **any path the caller names**, unverified. A payload with no signature section, launched with the verification key
deleted, ran as `uid=0 euid=0 gid=0` (V-051). The binary's path comes from the request: `Request::launch … appLocation[/tmp/app/bin/AppEngineerMode]`.

**What is missing.** Reachability from a lesser user. The session bus uses `<auth>EXTERNAL</auth>` and accepts only the daemon's own uid — measured: uid 65534 **cannot
connect**. So this is the mechanism to *re-launch* and *persist*, not to enter.

## 5. Removable-media kernel drivers — tested, and nothing broke

**What is established.** `texfat.ko` (Tuxera exFAT, 3016.6.23.3) and `tntfs.ko` (3016.7.1.2.3) parse media that `usb-automount` mounts without user interaction. **20 crafted
images across 9 mutation classes** produced **no fault** in either module; both rejected the malformed structures with their own checks (`vm/tuxera-fs-probe.md`).

**What is missing.** A defect. This is the only route whose required capability is "hand someone a stick", so it remains worth a coverage-guided sweep, but the one-edit sweep
found nothing and the entry says so.

## 6. USB SCSI property injection — the payload is a root shell, the input is hardware

**What is established.** `V-014`'s chain would start the installed `debug-shell.service`, which is `DefaultDependencies=no`, `ConditionPathExists=/dev/tty9`,
`ExecStart=/bin/sh` — an **unauthenticated root shell**. `SYSTEMD_WANTS` names units directly, so "not enabled" does not protect it.

**What is missing.** A device that can put control characters into a SCSI serial field. QEMU cannot (the property parser drops them; `usb-storage` caps the serial at 20
characters and `usb-bot`+`scsi-hd` silently falls back to `device_id`), so this needs a programmable SCSI bridge on real hardware.

## 7. Media parsers — components exist, none has been exercised

**What is established.** `lightmediascanner` runs as **uid 0** and its `asf.so` plugin ships; GStreamer 1.8.3 with `libgstasf.so` is present; USB media auto-mounts at
`/media/usb`. The indexer blocks on the DLT FIFO until `dlt-daemon` runs, then expects the session bus and media manager to drive it.

**What is missing.** Any demonstration that a crafted file reaches a parser. Presence is not reachability, and no crafted file has been tried.

## 8. WiFi — hardware present, three software gates, and no shell at the end

`bcmdhd.ko` + firmware + CLM blob + NVRAM for a **CYW88359** ship; a `modprobe.d` blacklist, GPIO **466** (`WLAN_REG_ON`) and a MICOM state gate keep it off. The enable path
ships too (`supplicantmanager`, `wpa_supplicant`), triggered by `/tmp/no_unece`. **But there is no sshd, no dropbear binary, no telnetd and no TCP listener in the image** — so
enabling the radio buys a network interface, not a shell (`wifi-enable-procedure.md`).

## 9. Downgrade — the ceiling is anti-rollback

`AppUpgrade` wraps SCOMO and FUMO; the vehicle's row selects FUMO. The version gate is strict-newer, modified packages are rejected by RSA verification, and engineering
"Force Update" — which does pass the version compare — is gated `DEV -> MP` and off on production. Whether an **authentic older signed image** installs is decided by
anti-rollback, which is **unresolved** (`DOWNGRADE-POSSIBILITIES.md`).

---

## What this page is really saying

Ranked by cost, the honest conclusion is uncomfortable for an attacker and good for an owner:

- **The cheapest route (#3, a `/tmp` write) has no way in.** Everything that could write to `/tmp` is already root.
- **The most reliable route (#1, the console) needs a screwdriver** and a password that resisted 45,000 plausible candidates.
- **The routes that need nothing but a file or a stick (#5, #7) have no demonstrated defect** — one tested clean, the other never exercised.
- **Engineering mode, the only no-privilege UI route, gives menus rather than execution** on this build.

The register's real finding is not that the unit is easy to enter. It is that **every trust anchor it relies on lives somewhere an attacker who is already inside can rewrite** —
which is a persistence problem, and a remediation problem, rather than an entry problem.
