# Attack-surface prioritisation for the `260128` bench unit

Status: historical prioritisation, corrected 2026-11-01 with current recovery
and kernel evidence. No physical-device interaction. For the current finding
inventory use `evidence/exploit-inventory.md`.

## Former blocking dependency — resolved offline

The original encrypted-payload blocker no longer applies. The EU `260128`
payloads were recovered and the authentic userspace now boots in the isolated
VM. This enables exact userland and module review, but does not provide an OEM
signature bypass, installed-device execution, or evidence about the owner's
unknown installed firmware.

## Ranked routes

### 1. CVE-2026-40225 udev hardware-property injection — strongest static physical root path

- Exact shipped `v4l_id` and `scsi_id` binaries contain the
  direct, pre-fix prints of kernel-provided product/serial fields without the
  control-character checks added upstream in 2026.
- Installed rules import both helpers. Block devices are tagged for systemd and
  the image contains `debug-shell.service`, configured to start `/bin/sh` as
  root on `/dev/tty9` if `ConditionPathExists=/dev/tty9` passes. The upstream
  SCSI route can inject `SYSTEMD_WANTS`, so no new unit file is required.
- This is independent of V-006's blocked shell interpolation: it uses different
  helpers and property boundaries, not sanitized `usb_id` `ID_SERIAL_SHORT`.
- A fixed benign parser control retained the leading-space second property. A
  matched synthetic-event VM control then used exact `systemd-udevd` and PID 1
  systemd: only the positive `SYSTEMD_WANTS` property started the transient
  marker unit; the negative run did not. Shipped vulnerable helper rules were
  masked and no pre-existing property-selected unit was requested. Another control confirmed
  `/dev/tty9` exists as character device `4:9`; it did not start the shell unit.
  Remaining gates are malicious supported hardware, hardware bytes reaching the
  shipped helper, and a practical production VT9/display/input route.
  No head-unit event, root transition, or physical console access was observed.
- Evidence: `evidence/systemd-udev-cve-2026-40225.md`.

### 2. BusyBox CVE-2015-9261 — exact pre-auth removable-update parser defect

- AppScomoDM's recovered USB path examines one first iterator result matching
  `S5W_SYSTEM_*_*_*.zip`, then invokes bare `unzip` to extract `AppUpgrade` and
  `.lge.upgrade.xml` before authenticating either extracted member.
- Original `/usr/bin/unzip -> /bin/busybox` resolves to stock SHA-256
  `95bab633...bd9ebc`, BusyBox 1.23.2. Independent review found that the 1.35.0
  file under the current integrated tree is a VM-injected helper; it is excluded
  from stock conclusions.
- Exact stock `unzip` accepts methods 0/8 and rejects method 12. Method 8 reaches
  dynamic `huft_build`, whose exact `v+n` cursor bound at `0x4788a` can read an
  uninitialized `v[]` slot at `0x47938`; initial fix
  `1de25a6e87e0e627aa34298105a3d17c60a1f44e` and corrective sentinel
  follow-up `6bd3fff51aa74e2ee2d87887b12182a3b09792ef` are absent.
- The configured launcher context defaults to uid 0 and intended policy labels
  AppScomoDM `App::upgrade`. Runtime route selection, inherited `PATH`, process
  identity/label, and the owner's installed hash remain physical-state gates.
- No ZIP/DEFLATE fixture was made and no target ran. The strongest supported
  impact is likely `unzip` child crash/update DoS; no memory write, RCE, root,
  signature bypass, package acceptance, partition write, or persistence was
  demonstrated.
- Evidence: `evidence/busybox-unzip-cve-2015-9261.md`.

### 3. ConnMan DHCPv6 DOMAIN_LIST overwrite — strongest static adjacent-network candidate

- Exact RPM metadata identifies `connman-1.29+5w.master.38-r1`, but the finding
  does not rely on that version. Exact shipped instructions at `connmand+0x1f150`
  implement CVE-2026-115863's fixed 1,025-byte copy and unbounded DNS-label
  cursor/store; option-24 dispatch is exact at `+0x1f211`.
- Exact control flow also closes the main static activation question: on a
  connected managed network, RA Managed/Other flags reach stateful DHCPv6 or
  information-request startup, and the information path explicitly requests
  DOMAIN_LIST option 24.
- The installed service defaults to uid 0 and does not exclude intended `wlan0`.
  A reply must still match live transaction, client/server identity, message
  type, and state. Production IPv6/interface state and physical on-link delivery
  are unknown.
- PIE, NX stack, stack canary, full RELRO, and `Restart=on-failure` constrain the
  practical result. No packet, crash, controlled execution, or root transition
  has been demonstrated. Treat this as a disconnected-bench validation target,
  not network-to-root.
- Evidence: `evidence/connman-cve-2026-115863.md`.

A second exact ConnMan result, V-016/CVE-2023-28488, is **not** ranked as a root
candidate. Ordinary IPv4 startup does reach its pre-fix L2 total-length path,
but this exact build calls `__memcpy_chk` with the 628-byte object size and exact
libc reaches `__chk_fail` before an underflowed copy. Its strongest current
classification is conditional adjacent-network service termination/availability,
not memory corruption or code execution. See
`evidence/connman-cve-2023-28488.md`.

### 4. oFono TPDU and QMI bounds — strongest static cellular/modem candidates

- V-017 exact shipped instructions retain the destination checks fixed by
  CVE-2023-4232 through CVE-2023-4235, CVE-2023-2794, and CVE-2024-7547. This
  is exact-code evidence, not an inference from the old package label.
- Compiled `lgeqmimodem` callbacks pass direct indications and stored/raw-read
  TPDUs into incoming decoding. Deliver, submit-report, and status-report writes
  complete before the handler's late DELIVER type check. Deliver-report and
  command are outgoing-only, with exact local transmit-queue and SIM-Toolkit
  callers rather than the ordinary incoming SMS callback.
- V-018 separately retains CVE-2024-7537 in the QMI WMS message-list callback.
  Its 32-bit overflow diagnostic falls through to a four-byte allocation while
  a copy loop uses the original count. That input is modem-originated metadata,
  not a TPDU and not
  proven directly controllable by an SMS sender or base station.
- Message-free exhaustive models confirm writes beyond the relevant objects.
  No dynamic crash or control-flow result is claimed.
- The conditional service defaults to uid 0 and is assigned SMACK `App::tms`.
  Telematics/no-ISA markers, unit enablement, modem/QMI state, byte preservation,
  SIM-Toolkit state, owner-device applicability, RCE, SMACK escape, and
  unrestricted root remain unknown.
- Evidence: `evidence/ofono-sms-decoder-cves.md` and
  `evidence/ofono-qmi-message-list-cve-2024-7537.md`.

### 5. USB storage via AppNavi replacement — published but installation-gated

- Mechanism: `navi_extended` replaces `AppNavi`; on launch it runs
  `main_loop.sh` from the root of an exFAT USB.
- Why first: it is the only published mechanism that yields arbitrary code
  execution on Gen5W_L, and it is a *storage* vector, matching the requested
  scope.
- Gate: Engineering Mode. Two layers on `MASS_PRODUCT` — an SOP check that
  fires before the PIN, then QML PINs `21`/`11`. Documented alternates: UART,
  GDS, older build.
- Unknown: whether `260128` still accepts the replacement, and whether the SOP
  gate can be cleared without already having execution.

### 6. Other Wi-Fi/network daemon candidates — exact review rejects two P2P CVEs

The recovered RPM Btree contains 1,679 records and identifies, among others,
`wpa-supplicant-2.5+56-r1`, `busybox-1.23.2-r0mango12`,
`dropbear-2020.81-r8mango2`, and `openssl-1.0.2k-r0`. V-020 still illustrates
why records are only leads, but in the opposite direction from the first draft:
the stock 1.23.2 bytes had to be separated from a VM-injected 1.35.0 helper
before exact CVE-2015-9261 review. Exact review of
wpa_supplicant, SHA-256
`6ad96a34c09b66c29ed2f9ad7ae73dee8389c81064a30dfd36a1212c52a21212`,
shows why these package labels are leads rather than verdicts: its
`p2p_add_device()` gates the SSID copy on length at most 32, fixing
CVE-2015-1863, and its Provision Discovery Request handler unconditionally
re-fetches the peer after `p2p_add_device()`, fixing CVE-2021-27803.

P2P remains compiled into wpa_supplicant and ConnMan, and an enabled path unit
conditionally starts `supplicantmanager` when `/tmp/no_unece` exists. Production
marker state, arguments, interface ownership, P2P find/listen state, and radio
reachability are unknown. These two CVEs are rejected for recovered `260128`;
Dropbear's exact activation review is also complete for the recovered image:
its package record, socket-fed template, installer, and static root authorized
public key remain, but `dropbear`/`dropbearmulti`, the socket unit, host-key
service/key, and enable links are absent. It is dormant, not a listener or
version-derived CVE route. Remaining BusyBox, OpenSSL, and other daemon
candidates still require exact file, activation, listener, and route review.
ConnMan's `--nodnsproxy`, for example, removes older DNS-proxy CVE routes even
when package-age matching suggests them.

`tools/uk_fw/rpm_nvra_inventory.py` deterministically parses preserved
`db_dump -p` output. `tools/uk_fw/net_surface.py` remains the physical-bench
listener and banner capture tool. No public end-to-end Wi-Fi-to-root for this
Gen5W_L build has been established.

### 7. Bluetooth BSA BNEP — exact parser defect, but recovered PAN configuration is dormant

Both PCB-selected daemons contain CVE-2017-0782's pre-fix
`bnep_process_control_packet()` control flow. They read the BNEP extension and
control fields before the field-by-field remaining-length checks added by public
fix `1b08775917413f1674882130a948add1ae44cc91`; the same code exists in
`BSA0107_00.51.00` and `BSA0107_00.63.00`. `vbtd.service` is enabled, has a
configured uid-0 default, restarts always, and recovered policy intends
`App::bluetooth`; mandatory `/tmp/session_appmgr.env` is a runtime gate.

Both engineering profiles explicitly say `PAN : N/A`. Startup calls
`BNEP_Init`, but bounded review found no direct `BNEP_Register` reference. This
is V-019, dormant/conditionally reachable exact code—not a radio-to-root result.
An indirect/runtime profile registration would still need an active adapter,
accepted ACL/L2CAP channel, and parser delivery. Pairing/authorization,
allocation-bound OOB, disclosure, write primitive, RCE, and owner applicability
remain unknown. See
`evidence/broadcom-bsa-bluetooth-cves.md`.

### 8. USB gadget / iAP2 / CarPlay — recovered, parser review still needed

Kernel config enables `USB_F_IAP2`, `USB_U_IAP2`, `USB_G_SERIAL`,
`GADGETFS`, `USB_F_MASS_STORAGE`, `USB_DWC3` dual-role. These are modules and the
userspace has now been recovered. iAP2 is a bounded, length-prefixed protocol
parser and remains an exact-code review target; no
finding has yet been established.
Note: `CONFIG_LGE_CARPLAY=y` in the kernel, yet no `carplay` symbols exist in
`vmlinux`, so the parsing is userland.

### 8.5. AppLauncher on-demand D-Bus launch — strongest post-local-execution domain-amplification candidate

V-028 corrects a literal-path-only negative. Exact `com.lge.avn.applauncher` Request adaptor code accepts runtime `applocation`, forwards it to dispatcher `[0x1ffd0,0x205b3)`, overwrites AppProcess program field `+0x58`, sets direct-launch byte `+0x1c`, and reaches a `QProcess::start` call site without either identified verifier call. The new-object helper checks only appid range and path existence before construction; a relevant existing appid object skips those create gates. Runtime Request registration, object construction, QProcess acceptance, successful exec and resulting privilege/label remain separate gates.

This does not yet outrank V-014 as a physical entry because it starts after local code execution. It is stronger than the V-012 service-restart amplifier if its runtime gates hold: the private session bus defaults to the daemon's uid, many HMI applications/services are configured uid zero but SMACK-separated, and effective bus/socket/target labels remain unobserved. Prioritize passive installed hash, service/unit state, AppLauncher/caller uid and labels, `/tmp/session_appmgr{,.env}` metadata, and target-path execute access; leave service-name ownership and Request registration unknown because the probe does not connect to the bus. Do not send a launch request on the owner unit. See `evidence/applauncher-dbus-launch-bypass.md`.

### 8.6. AppDMClient update source identity — exact static boundary, runtime substitution unknown

V-031 establishes that the recovered AppDMClient verifier contract carries only
integer status, while later staging and XML parsing resolve pathnames again.
Exact staging calls verify at `0x802db`/`0x80320` and later execute a pathname
copy at `0x8296b`; the XML reader verifies at `0xe1ff7` and separately opens at
`0xe22d5` or `0xe281f`. No retained open description or identity revalidation
binds the consumed object to the verified object.

This is a conditional update-path TOCTOU structure, not a root or signature-
bypass result. Runtime filesystem mutability, actor permission, serialization,
an actual object mismatch, successful staging/launch, and later inner FUMO
authentication remain unknown. Prioritize passive installed identity, mount,
uid/SMACK, and staged-file metadata collection. Do not attempt a pathname race
or modified update on the owner unit. See
`evidence/appdmclient-source-identity-boundary.md`.

### 9. Kernel — analysed; conditional post-execution candidates remain

- 64,923 symbols recovered and cross-validated (4,369/4,375 exports exact).
- 41 priority functions decompiled with corrected names.
- Trust chain: `verify_oem_signature` → SHA-256 → `manifest_key_verify_digest`
  → keyring lookup + usage bits → asymmetric verify. Reachable only from
  `keystore_backup` and `keystore_generate_mkey`, not exported.
- **Firmware acceptance is a userland decision.** A kernel signature bypass is
  not required to install a modified package.
- `/dev/keystore` (26 ioctls) is defensively coded: size gate, overflow-checked
  user pointers, matching alloc/copy lengths, post-dispatch zeroing. No
  memory-safety defect found in the reviewed set.
- Open question that matters: `keystore_open` has **no capability check**. If
  the device node is world-accessible and SMACK-permitted, any process can issue
  keystore ioctls, including `BACKUP` (which requires an OEM signature) and the
  `RUN_TESTS` path. Device-node mode and label are inside the encrypted rootfs.
- Built-in reachable code: netfilter/xtables (1,610 symbols), TCP (588),
  IPv6 (525), CAN (306, including `micom_*`), UDP (161).
- Exact checks reject CVE-2015-7613, CVE-2016-0728, physical USB-MIDI
  CVE-2016-2384, CVE-2016-7117, CVE-2016-7910, CVE-2016-7911, CVE-2016-7914, CVE-2016-9806, CVE-2017-7533, CVE-2017-8890, CVE-2017-11176, CVE-2018-14634, Dirty COW,
  both ranked AF_PACKET races, CVE-2017-7308's published private-area
  primitive, ALSA PCM CVE-2017-0861, and the generic missing Stack Clash
  guard-gap premise despite the old banner. The three newer built-in checks
  establish pre-publication SysV initialization, pre-`fput` `recvmmsg` error
  storage, and child multicast-list clearing. Exact `snd-seq.ko` rejects
  CVE-2016-2544, and exact `snd-timer.ko` carries CVE-2016-2545 through
  CVE-2016-2548 list-state, ioctl-serialization, and slave-locking fixes;
  CVE-2016-2549's provider is absent. CVE-2016-2384's
  modules and physical probe surface exist, but exact post-registration endpoint
  failures return without the second object free. CVE-2017-11176 is a
  semantic-control-flow result: the
  return-one retry lacks an explicit socket-register clear, but failed retry
  lookup routes to skb-only cleanup and cannot pass the stale socket to detach.
  CVE-2017-7533 is also rejected semantically: exact parent and rename paths
  stabilize both inline and external dentry names before the separate inotify
  length/copy operations. CVE-2016-9806 is rejected by exact saved-object
  ownership: `netlink_dump` captures the callback module and skb under its
  mutex, then uses only those saved values for cleanup after unlock.
  CVE-2016-7910 is separately rejected by the exact block seq-iterator owner
  invalidation: after iterator exit and exact `kfree`, `disk_seqf_stop` stores
  pointer-width zero to the same `seq_file.private +0x78` field. A later
  allocation failure and framework stop therefore cannot consume the freed
  iterator through that slot. CVE-2016-7911 is rejected separately: exact
  `get_task_ioprio` protects the I/O-context pointer and priority read with the
  same task lock that exact `exit_io_context` uses to detach the pointer before
  object release. CVE-2016-7914 is also rejected: exact associative-array
  insertion branches metadata-tagged terminal-node slots past the compare
  callback and calls it only for non-null leaf-tag fallthrough. CVE-2018-14634's
  prerequisite is rejected separately because exact `copy_strings` caps larger
  argument space at the smaller of a quarter-stack rlimit and six MiB.
  The companion AF_PACKET frame-count multiplication guard is absent, but the
  exact V1/V2 consumer trace is now complete. Allocation uses the full block
  count, and every position bounded by wrapped `frame_max` remains inside the
  allocated vector and block, including wrapped count zero. Separate mmap size
  wrap reaches exact `vm_insert_page` VMA rejection. This is a correctness and
  early-rejection gap, not a demonstrated OOB/root path. Three signed vector-
  index opcodes begin at block count `0x80000001`, but the minimum vector yields
  allocation order 23 and exact `__rmqueue` plus `__alloc_pages_nodemask` reject
  every order above 10. `__kmalloc` returns null before setup, cleanup, or mmap
  can reach a negative index.
- V-030/CVE-2017-6001 is now the highest-priority exact local-kernel escalation
  candidate. The perf move-group path loads a group context before waiting for
  two mutexes and lacks live-reference, identity-revalidation/retry, and
  post-lock move-state checks; the exact safe single-context helper exists
  elsewhere in the same binary. Public impact is local privilege gain and the
  initialized policy is `perf_event_paranoid=1`, but installed/runtime policy,
  PMU support, accepted event combinations, a winning race, stale/dead-context
  use, controlled corruption and root remain unobserved. Keep all active race
  validation off the owner unit.
- V-022/CVE-2018-17182 is exact pre-fix code on an ordinary MMU/thread surface:
  32-bit generations wrap into a live single-user flush helper that can retain
  cache pointers, and lookup validates only the same 32-bit generation. Public
  impact includes possible privilege gain. It requires a 2^32-state cycle and
  careful lifetime conditions; no target wrap, stale VMA, controlled reuse,
  corruption, or root is established. It remains a priority only for a
  disposable instrumented environment, not the owner unit.
- V-029/CVE-2017-9242 is exact pre-fix IPv6 append-data ordering on an ordinary
  UDPv6 call path: skb allocation and the fraggap copy precede the signed
  remaining-copy rejection. It is a strong static local memory-corruption/DoS
  candidate, but required internal state, actual overwrite, controlled bytes,
  code execution and root are unobserved. Keep below V-022 as a root candidate
  until a disposable instrumented kernel establishes more than public crash/DoS.
- V-027/CVE-2020-29660 is an exact TTY session-pointer locking defect, but the
  authoritative four-byte disclosure description names `PREEMPT=y` and this
  build has only voluntary preemption. Keep as conditional information
  disclosure below V-024 unless runtime evidence or disposable-kernel analysis
  establishes a realizable harmful overlap.
- V-026/CVE-2017-10661 is an exact built-in timerfd race premise requiring no
  device/module/namespace. Same-context membership transitions lack the fixed
  per-context lock, but public impact is more clearly list corruption/DoS than
  privilege gain. Keep below V-022 through V-025 until disposable sanitizer
  work can establish an actual invariant violation.
- V-025/CVE-2021-0920 is an exact AF_UNIX local candidate. Both MSG_PEEK
  attached-file receive paths omit the GC serialization added upstream, and
  recovered D-Bus usage makes runtime module loading plausible. Confirm
  `/proc/modules`, exact module hash, uid/SMACK, and limits passively; GC overlap,
  UAF, corruption, and root remain unproved.
- V-024/CVE-2020-29661 is an exact local TTY candidate. Master- and slave-side
  setters update one referenced slave pgrp field under distinct object locks;
  SMP is enabled and startup intends `/dev/ptmx` mode `0666`. Runtime node,
  mount, SMACK, job-control, successful concurrency, UAF, and root remain
  unobserved. Capture the newly added passive PTY metadata before any testing.
- V-023/CVE-2018-18281 is a second ordinary-MMU candidate. Exact PTE transfer
  releases both bound page-table locks before the only old-range TLB flush.
  Turning that window into stale page access requires concurrent invalidation,
  page release/reuse, and suitable timing; none is observed. Prioritize exact
  feasibility study beside V-022 in a disposable instrumented kernel, without
  treating the static window as corruption or root.
- V-013/CVE-2017-15265 remains pre-fix in exact `snd-seq.ko`; a benign VM
  diagnostic confirmed uid/gid-65534 create/delete ioctl reachability, but a
  bounded race did not fault and no root primitive is established.
- V-021 is an exact conditional local information disclosure: one
  `snd_timer_user_tinterrupt` path omits initialization of eight ABI padding
  bytes that the queue and read code copy in full. Intended DAC is `0644`, but
  module load, effective SMACK, provider/event generation, and owner-build
  identity remain unobserved. It is a possible information-leak component, not
  root or code execution.
- ALSA sequencer CVE-2018-1000004 lacks the official ioctl serialization, but
  the published pool sequence requires a write-capable sequencer fd and
  recovered intended policy grants ordinary users no write permission.
- CVE-2017-1000112's IPv4/IPv6 UFO guards are absent, but
  `CONFIG_USER_NS=n` blocks the published unprivileged root setup and production
  interface UFO features are unknown.

### 10. MICOM / CAN — post-exploitation

`micom_*` (24 symbols) includes a user-writable sysfs handler
(`micom_sys_spidump_store`). CVE-2020-8539 (`micomd`) is a **local** issue:
the public KOFFEE report confirms it needs code execution first, then reaches
`/dev/socket/micomd` to emit M-CAN frames. Not an entry vector.

## What is not available

- No public Wi-Fi-to-root for Gen5W_L.
- No public copy of the Chimaera report or tooling (the IIT host is unreachable;
  only the 2024 journal version, DOI `10.1007/s11416-024-00522-4`, and the CVE
  records are readable). The KOFFEE report *was* recovered via the Wayback
  Machine.
- No evidence that `260128` retains the `211214` bypasses.
- No public end-to-end validation of the `navi_extended` chain on physical
  hardware.

## Decisive next evidence, in order

1. Preserve V-014's remaining helper-input, physical-port, production-tty, and
   display/input gates for a disconnected bench with a benign marker—not the
   installed shell unit. Parser and synthetic udevd-to-systemd semantics are
   complete; do not describe them as physical-device reproduction.
2. For V-020, passively record installed BusyBox/AppScomoDM hashes, the
   `/usr/bin/unzip` provider, effective `PATH`, SCOMO/FUMO selection, and runtime
   uid/SMACK label. Do not place a malformed update archive on the owner unit;
   reserve sanitizer fixtures for a disposable vendor regression environment.
3. For V-015 and V-016, preserve the current NIC-free VM. On a disconnected
   bench, first record installed `connmand` and libc hashes, interface ownership,
   IPv4/IPv6 state, and benign DHCP/RA behavior. Do not move to a malformed
   control unless restart and recovery are proven, and do not develop a
   privilege payload. Exact fortification already constrains V-016 to an abort
   before the reviewed copy.
4. For V-017, record installed `ofonod`, unit/marker state, uid/SMACK label,
   modem devices, QMI services, and benign SMS behavior before any malformed
   control. Treat any later test as crash-only on a disconnected disposable
   state; do not develop a payload.
5. Identify an authentic post-index caller of V-012 playback or MediaBrowser's
   explicit `requestThumbnails(as)`, and repair the bounded VM thumbnail
   service-name/delivery boundary. Exact static code maps that request to
   `VideoContext → uridecodebin → eligible asfdemux`, while LightMediaScanner
   startup indexing uses a separate non-GStreamer ASF plugin. Manual authentic
   PlayerEngine D-Bus reachability is proven, but no automatic media-to-root path
   or RCE is established. Do not prioritize VMNC CVE-2016-9445/9446: exact
   every feasible WMVi path in the recovered code passes the 16384 dimension
   checks before dispatch, and the allocation uses `g_malloc0`, despite its
   `1.8.3-r0` metadata.
6. Determine production DAC/SMACK access to `/dev/snd/seq` and analyze V-013's
   first post-free use without attempting or claiming a root exploit.
7. Measure production interface features before treating CVE-2017-1000112 as a
   reachable path; keep the current VM NIC-free.
8. If physical bench access later becomes available, capture UART and installed
   version state before any write or engineering-mode experiment.

## Sources

- `evidence/eu-kernel-symbol-recovery-and-trust-chain.md`
- `evidence/gen5w-public-exploit-ecosystem.md`
- `evidence/known-exploits-and-cve-survey.md`
- `evidence/bench-hardware-root-path.md`
- `evidence/network-surface-and-wifi-root.md`
- `evidence/child-notes/01…04`

#### From the parallel repository

The parallel lineage ranked the same attack surface before the EU payloads were
recovered. Its ranking, its component table and its remaining notes are
preserved below, with every conflict against the recovered-evidence ranking
above marked for adjudication.

<!-- disagreement: the parallel version says every interesting code path lives inside AES-encrypted payloads and that analysis "is impossible without the unit-derived DecryptToPIPE + decryption_key.der". This document says the EU 260128 payloads were recovered and the authentic userspace now boots in the isolated VM. Both statements are kept: the encrypted-only claim describes the pre-recovery state, and the recovered-payload claim does not establish installed-device parity. -->

##### Status and former blocking dependency (parallel version)

Status: synthesis of this session's static work plus four completed subagent
surveys. No device interaction. This ranks the routes that remain open and names
the single dependency that blocks all of them.

## The blocking dependency

Every interesting code path — `AppUpgrade`, `AppDMClient`, `.lge.upgrade.xml`,
the update parser, the Wi-Fi daemons, the USB gadget stack, Android Auto and
CarPlay — lives inside AES-encrypted payloads (entropy 8.00, no keystream reuse,
no known plaintext). Analysis of those components is impossible without the
unit-derived `DecryptToPIPE` + `decryption_key.der`. This is a cryptographic
dependency, not an effort limit.

##### Wi-Fi remote — component CVEs, version-gated (parallel ranking)

### 2. Wi-Fi remote — component CVEs, version-gated

No public Wi-Fi-to-root exists for Gen5W_L. The realistic classes are old
daemons whose exact versions are encrypted. Survey totals (2015–2020):
dnsmasq 15, hostapd 26, wpa_supplicant 30, dropbear 12, BusyBox 24, miniupnpd 9,
OpenSSL 95.

| Candidate | Component | Type | Reachable when |
|---|---|---|---|
| CVE-2017-14491 | dnsmasq | heap overflow, DNS response | unit runs DHCP/DNS in AP mode |
| CVE-2017-14493 | dnsmasq | stack overflow, DHCPv6 | same |
| CVE-2016-2148 | BusyBox `udhcpc` | heap overflow, OPTION_6RD | unit joins a hostile AP as client |
| CVE-2015-1863 | wpa_supplicant | heap overflow, SSID in P2P frames | radio range |
| CVE-2016-6309 | OpenSSL 1.1.0 | TLS state-machine UAF | any TLS listener |

Triage requires version strings; `tools/uk_fw/net_surface.py` captures them.

<!-- disagreement: the parallel table lists CVE-2015-1863 (wpa_supplicant heap overflow via SSID in P2P frames) as reachable at radio range, while the ranking above records that exact review of the shipped wpa_supplicant rejects CVE-2015-1863 (the p2p_add_device() SSID copy is length-gated at 32) and CVE-2021-27803. The parallel table also lists CVE-2016-6309 against OpenSSL 1.1.0, while the recovered RPM inventory records openssl-1.0.2k-r0. The dnsmasq rows (CVE-2017-14491/14493) are likewise in tension with the note above that ConnMan's --nodnsproxy removes older DNS-proxy routes even when package-age matching suggests them. -->

##### USB gadget / iAP2 / CarPlay — needs plaintext (parallel ranking)

### 3. USB gadget / iAP2 / CarPlay — needs plaintext

Kernel config enables `USB_F_IAP2`, `USB_U_IAP2`, `USB_G_SERIAL`,
`GADGETFS`, `USB_F_MASS_STORAGE`, `USB_DWC3` dual-role. These are modules, so the
code is in the encrypted rootfs. iAP2 is a bounded, length-prefixed protocol
parser — a classic memory-safety target, but auditable only after decryption.
Note: `CONFIG_LGE_CARPLAY=y` in the kernel, yet no `carplay` symbols exist in
`vmlinux`, so the parsing is userland.

<!-- disagreement: the parallel version says the iAP2/USB gadget modules are only auditable after decryption and that the device-node mode and label are "inside the encrypted rootfs"; the ranking above records that the userspace has been recovered and that iAP2 is now an exact-code review target with no finding yet established. -->

##### Kernel — analysed, and not the weak link (parallel ranking)

### 4. Kernel — analysed, and not the weak link

- **Firmware acceptance is a userland decision.** A kernel signature bypass is
  not required to install a modified package.



<!-- disagreement: the parallel version states flatly that "Firmware acceptance is a userland decision" and that a kernel signature bypass is not required to install a modified package, and it titles the kernel section "not the weak link". The ranking above and evidence/eu-kernel-symbol-recovery-and-trust-chain.md narrow userland acceptance to update packages, keeping boot-container signatures, loader policy, slot selection and boot-time acceptance as separate unresolved stages, and the ranking above additionally lists conditional post-execution kernel candidates (V-030/CVE-2017-6001 highest priority) that make the kernel non-trivial after local execution. Both statements are kept. The parallel section's remaining bullets (symbols recovered, trust chain, /dev/keystore review, built-in reachable code) are identical to item 9 above and are not repeated here. -->

##### Decisive next evidence (parallel version, pre-recovery ordering)

1. UART capture at `ttyS2`, 115200 8N1 (command line recovered from the
   plaintext `ipk.` header; early console at MMIO `0xfc000000`).
2. Engineering Mode state on the unit: does the SOP gate fire, and does PIN
   `21` reach the menu?
3. Unit-derived `DecryptToPIPE` + `decryption_key.der` → decrypt
   `mango-rootfs.tar.gz`.
4. With plaintext: `tools/uk_fw/dump_survey.py` on the extracted rootfs, then
   component version triage and USB/iAP2 parser audit.


These four parallel steps are retained as the physical-bench ordering. They are
compatible with, but not superseded by, the eight-item ordering above: UART
capture at `ttyS2` and Engineering Mode state remain the first physical actions,
while the decryptor step is already satisfied offline for EU `260128`.

##### Parallel section numbering (for cross-reference)

### 1. USB storage via AppNavi replacement — highest yield
### 2. Wi-Fi remote — component CVEs, version-gated
### 3. USB gadget / iAP2 / CarPlay — needs plaintext
### 4. Kernel — analysed, and not the weak link
### 5. MICOM / CAN — post-exploitation

Sections 1 and 5 have the same bodies as items 5 and 10 above; only their rank
numbers and the item 1 "highest yield" verdict differ.
