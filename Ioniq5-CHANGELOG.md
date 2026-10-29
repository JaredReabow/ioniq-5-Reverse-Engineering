# IONIQ 5 changelog

All entries describe the IONIQ 5 research programme. The root `CHANGELOG.md`
belongs to the parallel Kona programme and is not modified by IONIQ work.

## 0.70.0 - AppNavi stops between create_surface and ivi surface_create

- Located the stop precisely by counting protocol markers in AppNavi's own Wayland debug
  log: it binds `wl_display`, enumerates 71 registry lines, binds `wl_compositor`, `wl_shm`
  and `ivi_application`, creates a `wl_surface`, and then **never calls
  `ivi_application.surface_create`** and never attaches or commits.
- **`wl_drm` is absent entirely** — the compositor runs headless with pixman, so no GPU
  buffer interface is offered. Cause or coincidence is not established.
- `QT_WAYLAND_SET_SURFACE_ID_FORCED=1` in addition to the id yields a second `wl_surface`
  but still zero `surface_create`, so that path alone does not clear the stop.
- Ruled out: gpio440 polling, the preload adapter, ApplicationManager presence, and the
  current command-line flags. The forced-env probe is published as
  `tools/uk_fw/guest/appnavi_forced_probe.sh`.
- Method note: marker counting is much cheaper than transporting log text over the serial
  console and should be the default for this kind of diagnosis.

## 0.69.0 - the missing gpio440 node, and a privacy-checker fix

- Published the reason AppNavi never paints: its client log ends in a repeated read
  failure on `/sys/class/gpio/gpio440/value`. That node cannot exist here —
  `/sys/class/gpio` holds only `export` and `unexport`, and exporting `440` returns
  **EINVAL** because no gpiochip registers the pin, matching the kernel log where the GPS
  driver defers with `-517`. The emulated board lacks a GPIO the firmware expects.
- **Adaptor:** a tmpfs over `/sys/class/gpio` with an inert `gpio440` node. The `gpio440`
  errors then vanish from AppNavi's log — the first demonstrated case in this project of a
  simulated hardware dependency unblocking a firmware startup path. Necessary but not yet
  sufficient: surface creation appeared in one run and not the next.
- Fixed a privacy-checker false positive: the email pattern matched Wayland object
  notation, so captured protocol logs were reported as leaked addresses. The domain must
  now begin with a letter, with a regression test added. The checker was fixed rather than
  the evidence rewritten, since every Wayland capture would hit the same thing.
- The adaptor probe is published as `tools/uk_fw/guest/appnavi_gpio_probe.sh`.

## 0.68.0 - why AppNavi idles: surface id and visibility are injected from outside

- Added a section to `docs/navigation-status.md` explaining the alive-but-paints-nothing
  state. AppNavi links `libivi-platform-interface.so.1`, which resolves its ivi surface id
  **only from the environment** via `QT_WAYLAND_SET_SURFACE_ID` and its `_FORCED` and
  `USE_PID_FOR_SURFACE_ID` variants; on the vehicle `AppLauncher` injects that value
  together with `APPID`. With it unset the library enters an uncapped
  `blockingReadEvents` loop waiting for an id reply — matching the observed symptom of a
  live, silent, surface-less process rather than a crash.
- Visibility is external too: `QWindow::setVisible()` is only reachable from an
  `ivi_surface.visibility` event, which the window manager emits only for that app's id.
- Ruled out: ApplicationManager's absence, every command-line flag in the current
  invocation, and `APPID`. AppNavi reads exactly one environment variable itself,
  `MD_CONA40_ON`.
- Flagged an open point: the VM logs show the surface created under id **30000** while the
  helper programmes **3000**, so visibility may be requested for a non-existent id. Next
  step narrowed to one instrumented boot that records the id actually received.

## 0.67.0 - A/B shows AppNavi paints nothing at all

- Ran the A/B the previous entry left open, since an empty log is not proof that nothing
  rendered. Three runs of the same probe with the captured frame compared: with the
  adapter (AppNavi alive, 1 log line), baseline without it (AppNavi alive, 0 lines), and a
  control with **AppNavi not launched at all**.
- The screenshot is byte-identical (`b316a82a…0b9a83`) between the baseline and the
  no-AppNavi control. So AppNavi renders nothing: it is alive, silent, and contributes no
  pixels. It is not rendering anonymously, it is not rendering.
- Conclusion recorded in `docs/navigation-status.md`: the adapter is not implicated, and
  the compositor contract, the `0x0` hold and the BG notification cannot be exercised
  until AppNavi paints. The next step is to find why it is alive but idle, starting with
  the environment and arguments the launcher normally gives it.
- Also fixes a documentation inconsistency: an earlier `git reset --hard` in the public
  clone discarded an uncommitted doc edit, so this file still presented the question as
  open while the private copy already carried the baseline result. Both now agree.

## 0.66.0 - baseline clears the adapter; AppNavi is silent on its own

- Ran the control that the published open question called for: the identical render probe
  with **no** preload. AppNavi's log came back empty and the manager reported drawing
  application `0`, the same as the run with the adapter loaded apart from the adapter's
  single load record. The interposer is therefore **not** what stops AppNavi.
- Stated with it: an empty log is **not** proof that nothing rendered. AppNavi may log to
  DLT or a file, and the captured frame has not been inspected, so "renders silently" and
  "never renders" both remain open.
- `docs/navigation-status.md` updated accordingly, and the baseline probe added as
  `tools/uk_fw/guest/appnavi_baseline_probe.sh` so the control can be reproduced.

## 0.65.0 - navigation status published: two questions closed, one blocker left

- Added `docs/navigation-status.md` recording what is now measured about the
  Home-to-Navigation gap, and published the research helpers behind it.
- **EGL dimension ordering measured** on the authentic client. A hardware-breakpoint
  observer captured vendor `libEGL` at `+0x16f16` (width `-1`, height `-1`) and
  `+0x16f1e` (width `1920`, height `720`) on the same surface pointer, so
  `swrast_update_buffers` populates the dimensions during the invocation while the copy
  stride was already derived from `Width = -1`. Scoped to the Wayland **software** path:
  the hardware constructors do not share that vtable.
- **A Qt hide cannot produce the background notification.** DWARF fixes the
  `weston_surface` layout, and read order in `weston_surface_commit_state` shows the
  size block stores the previous positive size before the null-buffer branch zeroes the
  `_from_buffer` pair. A genuine `0x0` transition is required.
- **Guest hardware breakpoints work under TCG**, including four slots, slot
  replacement, `DR4`/`DR5` rejection, per-slot `DR6` bits, single step and per-thread
  scoping. One trap worth knowing: detaching with a slot still armed leaves the
  breakpoint live and kills the tracee.
- Two practical findings for anyone injecting into vendor apps: the launcher's
  interposer unsets `LD_PRELOAD` for AppLauncher so children inherit a clean
  environment, and a musl-linked `.so` will not load into the vendor's glibc process.
- Remaining blocker stated plainly: **AppNavi never attaches a surface** in either the
  full chain or the standalone render probe, so nothing reaches the compositor to be
  classified. The open question is whether the interposer itself is preventing AppNavi
  from rendering; a baseline run without it is the next step.

## 0.64.0 - disclosure reduction for the physical-access entries

- Reduced V-006, V-007 and V-008 in this public tree to status entries with no
  operational detail, following triage of the third-party claims that produced
  them. Confirmed detail remains in a private record pending coordinated vendor
  contact.
- Verified this public tree contains no occurrence of the affected service name,
  the affected property name, or the command-construction mechanism.
- Note: the engineering-mode entry sequence and PIN were already published in this
  tree by earlier work, before this change, in
  `evidence/owner-engineering-mode-pin-observation.md` and
  `evidence/vehicle-usb/README.md`. That is pre-existing content and was left
  unaltered rather than silently removed; it is flagged for the owner's decision.

## 0.63.0 - VM status, screenshots and physical-access leads

- Published two further inspected screenshots under `vm/evidence/screenshots/`:
  the authentic launcher profile/confirm screen and a navigation-window frame that
  still shows Home. Evidence manifest re-hashed (45 entries).
- Expanded the root README with a per-area VM status table, the mandatory run
  configuration and the recovered ApplicationManager/window-byte contract that
  explains why Navigation does not composite yet.
- Added V-006/V-007/V-008 to the defensive register from a third-party advisor
  summary: USB descriptor strings into a privileged mount script, media parsing as
  root, and a hashed-password root serial console. All three are labelled
  **unverified actor reports**; no code path, process identity, console device or
  reproduction was supplied and none was validated in this session.
- Recorded the engineering caveats that bound them: USB string descriptors are
  UTF-16LE (metacharacters arrive NUL-interleaved) and `udev` sanitises
  `ID_SERIAL`/`ID_MODEL`, so a vulnerable consumer would have to be custom; the
  126-code-unit descriptor limit still admits a ~40-character payload, making
  encoding and shell quoting rather than length the binding constraint.
- All three require physical access; none is remote. No hardware was touched, no
  experiment was run for this publication, and no attack tooling was built.
- Note: entries 0.60.0–0.62.0 were previously appended at the end of this file
  rather than in newest-first order; this entry is inserted in the documented
  position without rewriting those historical entries.

## 0.40.0 - 2026-10-21

- Reached interactive BusyBox userspace on the **VM-adapted vendor kernel**:
  one verified guest-RAM SDHCI table change, a compatible ext4 SD root and
  explicit `/init`. Original firmware/boot-image files remain unchanged.
- Added an 800×480 direct-QEMU-VGA diagnostic with R/G/B/Q keyboard input.
  QMP captures match every expected pixel. This is explicitly **not the
  infotainment UI**, which remains unrecovered.
- Replaced the old launcher with a local-input-only, hash-checked preparation
  and run harness; retained unpatched and failing-command controls. Fixed
  foreground programs consuming the launcher's separate status-command input.
- Tested two additional recovery hypotheses using existing resources: the
  boot RSA public key against 38 opaque payload edges (zero matching type-1
  blocks), and two installed Mac updater AES constant pairs against bounded
  payload-start hypotheses (zero validated plaintext candidates). Retained
  scan scopes, synthetic controls and the rejected gzip-marker matches.
- Full suite: **137 tests pass**. Fresh serial and graphics VM checks pass;
  prepared artifacts and earlier evidence hashes remain unchanged.
- Replaced the stale handover and corrected categorical VM impossibility,
  sparse-log PCI-enumeration, anti-tamper-panic and footer-stripping claims.
  Entries 0.36–0.39 below preserve historical conclusions, not current findings.
- No head-unit access, new downloads, genuine firmware decryption, flashing,
  signature bypass, Fable review or new Council acceptance is claimed. Legacy
  accepted-input hashes were not refreshed.

## 0.39.0 - 2026-10-19

- Commissioned an independent reviewer/planner pass (child note 12) on the VM
  goal. Its verdict matches the measurements: **running the vendor UI under
  emulation is not achievable**, for three reasons — the userland is encrypted,
  the kernel has no display path at all, and no block device binds.
- Stated the ceiling explicitly in `vendor-kernel-vm.md`: this kernel's only
  console is 8250 serial; `CONFIG_FB` is not set, there is no VGA or framebuffer
  console, and the sole display driver is i915, which QEMU cannot emulate. The
  achievable outcome is an interactive **serial shell on the stock kernel**, not
  a picture — and calling it "the UI" would misrepresent it.
- Recovered significant keystore configuration from the same config:
  `CONFIG_KEYSTORE_TESTMODE=y`, `CONFIG_KEYSTORE_TEST_MIGRATION=y`,
  `CONFIG_KEYSTORE_DEBUG=y`, `CONFIG_KEYSTORE_SECURE_BOOT_IGNORE=y` alongside
  `CONFIG_SECURE_BOOT=y`, `CONFIG_KEYSTORE_SEED_SIZE_64=y`,
  `CONFIG_KEYSTORE_DEVICE_AND_USER_SEED=y`, and
  `CONFIG_KEYSTORE_OEM_KEY_USAGE_BIT=47` with the exact
  `CONFIG_KEYSTORE_OEM_KEY_IDENTIFIER` string seen in `verify_oem_signature`.
  Production firmware shipping with keystore test mode, debug and secure-boot
  ignore enabled is a notable configuration finding.
- Corrected the stale introduction in `vendor-kernel-vm.md`, which still claimed
  an ext4 mount and a deliberate panic.
- Also established that PCI devices are barely enumerated under this kernel in
  QEMU (one quirk line on q35, nine on `-machine pc`, no device registrations),
  which is a prerequisite problem for the SD controller binding.
- No exploit, key, decryption or device action is included.

## 0.38.0 - 2026-10-19

- **Solved the boot-parameter mechanism.** `setup_abl_params` is registered with
  the `__setup` string **`ABL.`** (trailing dot), confirmed by reading the string
  at `__setup_str_setup_abl_params`. The handler splits the remainder on `=` and
  stores name/value pairs in a 16-entry list. The correct command line is
  `ABL.oemkm=<hex size>@<hex phys>` and `ABL.seed=<hex phys>,<hex phys>`.
- **The anti-tamper is now satisfied under emulation**: with those parameters and
  the blobs loaded at physical addresses, the kernel reports
  `keystore_init completed successfully` and `manifest: init Completed
  Successfully`, and no longer panics on them. This corrects the documentation
  that recorded the parameters as bare `oemkm=` / `seed=`.
- Found the introspection interface: `abl_cmdline_init` exposes every collected
  parameter under **`/sys/kernel/abl/`**.
- Located the mechanism by a proper xref pass: a new `FindXrefs.java` Ghidra
  script showed a WRITE to `params_list` inside `setup_abl_params`, which is how
  the vendor hook was identified after the earlier dead end.
- Remaining VM gap is a root device, not the anti-tamper: sdhci core and the
  22 `sdhci_pci_*` symbols are present but QEMU's `sdhci-pci` device ID is not in
  the 4.1 driver's table, so no `mmc0` binds and root mounting fails. Recorded the
  next step: present a controller ID the driver recognises.
- No exploit, key, decryption or device action is included.

## 0.37.0 - 2026-10-19

- Extracted the exact boot-parameter contract by decompiling
  `get_apl_seed_offsets` and reading `keystore_fill_seeds`. The two parameters use
  **different separators**: `oemkm=<hex size>@<hex phys>` and
  `seed=<hex phys>,<hex phys>`. `keystore_fill_seeds` copies two **64-byte** seeds
  out of physical memory (device → `sec_seed`, user → keystore state) and then
  **zeroes both source regions**; an absent device seed is fatal, an absent user
  seed is tolerated.
- Derived a minimal manifest blob that satisfies `manifest_init`'s validation:
  0x40 bytes, word 0 = `0xE`, byte `0x13` = 0, words 5 and 6 = 0, word 1 =
  end-of-entries offset.
- **Tested it and it did not work.** With both parameters supplied and the blobs
  loaded via QEMU `-device loader`, the kernel still reports both missing, even
  though it prints the command line verbatim. `params_list` is an empty
  `LIST_HEAD` at `0xffffffff81a1e330` and stock `unknown_bootoption` never
  populates it, so the vendor's collection hook is elsewhere and has not been
  located. Recorded so the next attempt starts from that point.
- Recorded an environment fault: Homebrew Python 3.14 became unusable mid-session
  (`posix_spawn` error) and `python3` now resolves to it; all tools still run
  under `/opt/homebrew/bin/python3.13`.
- No exploit, key, decryption or device action is included.

## 0.36.0 - 2026-10-19

- Added `tools/uk_fw/fat_harness.py`: a from-scratch FAT16/FAT32 image builder,
  independent inspector, and 17-case semantic corruption corpus targeting the
  checks a filesystem driver must perform. Images were validated by mounting them
  on macOS, which reads and executes their contents correctly. Seven unit tests.
- Added `tools/uk_fw/vm_boot.py` and **got the vendor kernel booting under
  QEMU 11.1.2**: `4.1.27-abl #1`, built 2026-01-28, initialising SMP, ACPI, PCI,
  serial console and an ext4 root on an emulated SD card.
- Two obstacles solved and documented: the `ipk.` payload is a bzImage at offset
  **1008** (protocol 2.13, `setup_sects` 30), and this kernel **cannot use an
  initramfs** because `CONFIG_BLK_DEV_INITRD` is not set — no VIRTIO, no built-in
  ATA/SCSI, no NFS root. The only bootable root is ext4 on an SD card, which also
  mirrors the real unit's `mmcblk0`.
- **Discovered a boot-time anti-tamper**: without its parameters the kernel prints
  `keystore: d/u-seed info missing in cmdline`, `manifest: Key manifest info
  missing in cmdline` and panics with a vendor-modified message, "Invalid
  configuration from end user prevents continuing". It refuses to run rather than
  degrading. This confirms `oemkm` is mandatory at runtime and names the second
  required input (device/user seed material).
- Recovered the internal build provenance from a surviving path string:
  `26RU1_001`, built 2026-01-21, branch tag `s5w.26ru1.251203`, kernel source at
  `security/keystore/seed.c`.
- No exploit, key, decryption or device action is included.

## 0.35.0 - 2026-10-19

- Added `evidence/exploit-inventory.md`: a single table of every known technique
  for this platform with what it yields, its precondition, and whether it can be
  used as a **first** step. Consolidates Chimaera CVE-2023-26243/44/45/46,
  `navi_extended`, `disableEncryptionUpdate`, `wideopen.service`, the QML patch,
  boot-image substitution, CVE-2020-8539, `hmg_nemesis`, the kernel CVEs and the
  unverified Wi-Fi daemon classes.
- States the circularity plainly: every named CVE is a binary patch and therefore
  requires prior execution. The only non-circular entry is the Engineering Mode
  AppNavi installation, which is a feature rather than a vulnerability.
- Maps the two capabilities raised by the owner — a USB payload and a modified
  firmware image — and shows both are gated: the USB payload needs a replacement
  `AppNavi` installed, and custom firmware is a persistence capability (key or
  `disableEncryptionUpdate`), not an entry capability.
- Identifies the genuine pre-authentication surface: the USB update path, with the
  filesystem parser as the only stage that touches attacker bytes before any
  cryptographic gate.
- No exploit, key, decryption or device action is included.

## 0.34.0 - 2026-10-19

- Added `evidence/network-root-feasibility.md` in answer to a direct question:
  whether the Linux version yields a network path to root. Answer: vulnerabilities
  certainly exist, a network root does not follow.
- Recorded the config filter that removes most of the remote-RCE catalogue:
  `USER_NS`, `NF_TABLES`, `BLUETOOTH`, `SCTP`, `DCCP`, `RDS`, `TIPC`, `NFC`,
  `AX25`, `X25`, `INET_ESP`, `XFRM_USER`, `TCP_MD5SIG` and `INET_DIAG` are all
  absent; `AF_PACKET` is a module and needs `CAP_NET_RAW`. What remains
  pre-authenticated is IPv4/IPv6 parsing, TCP, UDP, ICMP, fragment reassembly and
  netfilter hooks — a surface that yields DoS, not code execution.
- **Discovered that the kernel is not a pristine 4.1.27:** the symbol
  `sysctl_tcp_challenge_ack_limit` is present, introduced by the CVE-2016-5696 fix
  in **4.1.32**. The vendor cherry-picks network fixes, so version-string
  reasoning is unreliable in both directions and per-fix verification is required.
- Recorded two false-inference traps for future work: the upstream GRO recursion
  helpers are `static inline` so their absence is suggestive, not conclusive; and
  `tcp_gso_segs` is a struct field, not a symbol, so its absence proves nothing.
- No exploit, key, decryption or device action is included.

## 0.33.0 - 2026-10-19

- Added `evidence/corrections-log.md`: an explicit, claim-oriented record of the
  eleven things this programme got wrong or superseded, each with what replaced
  it and why. Eleven entries cover the kallsyms 204-entry mispairing, the
  `0x18` pseudo-checksum, the A/B partition misreading, the downgrade conclusion,
  the weakened CRC hypothesis, the header entropy misreading, the guessed
  decryptor invocation, the `iasImage` decomposition, the absent kernel IAS
  driver, and two attempted vulnerabilities that were tested and **rejected**
  (`TEST_VERIFY_ECC_SIGNATURE` uninitialised fields and `keystore_get_ksm_key`
  buffer aliasing).
- The log states which evidence documents are affected by each correction, so a
  reader landing on an older document knows whether to trust it.
- It closes with the five practices that produced the corrections — cross-check
  against an independent table, disassemble before calling something a bug, check
  the entropy maximum, treat field reports as evidence against a hypothesis, and
  record rejections as well as findings.
- No exploit, key, decryption or device action is included.

## 0.32.0 - 2026-10-19

- Delivered the `workflow-normalized.csv` export that was requested earlier and
  never produced. Added `tools/uk_fw/ledger_export.py`, which flattens the nested
  ledger into two deterministic tables: `workflow-normalized.csv` (one row per
  task-artifact pair, 19 rows, tasks without artifacts retained) and
  `requirements-normalized.csv` (16 rows with the tasks citing each
  requirement).
- The export is byte-idempotent — re-running on an unchanged ledger produces
  identical files — and supports ``--check`` so drift between ledger and exports
  is detectable. Line terminator is LF so the files diff cleanly.
- Fixed a bug found during development: `--check` disagreed with the writer
  because CSV defaults to CRLF while `read_text` normalises newlines.
- Added five unit tests; the suite now runs 74 tests.
- No exploit, key, decryption or device action is included.

## 0.31.0 - 2026-10-19

- Added `evidence/pre-disclosure-security-assessment.md` in place of a further
  exploitation pass. It is an **internal assessment, not a disclosure**: no vendor
  was contacted and nothing was published.
- It records four candidate issues with explicit confidence levels — CRC-32 as the
  declared manifest integrity value (confirmed mechanism, unproven impact), the
  `oemkm=` command-line trust root (confirmed), the absent capability check in
  `keystore_open` (confirmed), and the boot container's embedded modulus
  (confirmed structure, unproven pinning) — and states for each what evidence
  would make it disclosable.
- It explicitly separates the **modification-created** root runner from vendor
  defects, so a report is not padded with an artefact of the mod itself.
- It records what was established as *not* vulnerable, so the assessment is not
  one-sided.
- No exploit, key, decryption or device action is included.

## 0.30.0 - 2026-10-19

- Read the final two public toolchain scripts, completing the read-through.
  `update_navi_manually.sh` answered the last open structural question: **the
  navigation application lives in the map partitions, not the rootfs** — at
  `/navi/Bin/AppNavi` and `/navi2/Bin/AppNavi`.
- Consequence recorded: the A/B pairing extends to the navigation app, so a
  custom `AppNavi` must be installed into **both** partitions or it disappears
  when the unit switches map partitions. The script also replaces `AppNavi`
  directly on the partition, bypassing the Engineering Mode dialog — but it needs
  an execution context, so it is a re-install path, not an entry bypass.
- `HANDOVER.md` now carries the navigation paths in the target table and the
  alternative in the chain diagram.
- Every script in the public toolchain has now been read. No new avenues remain
  in that corpus.
- No exploit, key, decryption or device action is included.

## 0.29.0 - 2026-10-19

- Consolidated six passes of findings into the two deliverables a returning
  operator actually reads. This is documentation work, not new discovery.
- Rewrote `HANDOVER.md`: seven findings instead of five, a line-level chain with
  the real paths and commands (entry at `/media/usb`, persistence unit, QML patch,
  decryptor path, `/tmp/<32 hex>` key capture, repack command), the corrected
  tool table, and four more rows in the established-negatives table.
- Added an explicit **safety warning** to the handover: `wideopen.service` is a
  root service that executes any `wideopen_service.sh` from any mounted USB with
  no authentication, and it survives official updates. Safe on a bench, an
  unauthenticated root backdoor if the image returns to a vehicle.
- Made `evidence/bench-runbook.md` Phase 4 concrete: the four-step key-capture
  procedure, the double-backup requirement for `DecryptToPIPE_OG`, the exact
  offline decrypt command, and the glibc/`gcompat` constraint.
- No new exploit research; no device action.

## 0.28.0 - 2026-10-19

- Recovered the **exact key-extraction mechanism** from `extract_keys.sh` and
  `spoof_decrypttopipe.sh`, including the real invocation the unit uses:
  `/app/share/AppUpgrade/DecryptToPIPE -d /tmp/<32 hex> /media/usb/1/<model>/AppUpgrade 0 | dd of=/update/usb/bin/AppUpgrade bs=512`.
  The decryptor path, the per-update random `/tmp` key path, and the output target
  are now all recorded.
- Documented the two-stage procedure: back up the genuine decryptor, install a
  patched `DecryptToPIPE_FK`, reboot, let the unit's own update call it with the
  temporary key, collect `*_key_*.der` from the USB, restore the original.
- Established that the public `update_decryptor` repository ships **placeholders,
  not the artifacts**: `DecryptToPIPE` is a 129-byte shell stub and
  `decryption_key.der` is a 193-byte `EMPTY_DECRYPTION_KEY` text file. This closes
  the last possibility of an offline decryption path — neither the binary nor the
  key is public.
- Recorded the defensive design of the extraction scripts (flag files, mandatory
  backup checks) and the warning that losing `DecryptToPIPE_OG` permanently breaks
  the unit's update path.
- No key, binary, decryption or device action is included.

## 0.27.0 - 2026-10-19

- Recovered the **real decryptor invocation** from `update_decryptor`'s
  `entrypoint.sh`: `DecryptToPIPE -d <keyfile> <input> 0 > <output>`. Output is on
  stdout, every file in the package is handed over whole (the footer is *not*
  stripped), and the binary is glibc x86-64 run under Alpine + `gcompat`.
  `tools/uk_fw/gen5w_decrypt.py` was corrected accordingly — it had guessed a
  different syntax and wrongly assumed the footer must be removed first.
- Recovered the complete payload and persistence chain from `navi_extended`'s
  `USB_FILES` and `update-patcher`'s scripts: `main_loop.sh` runs
  `main_loop_code.sh` every 10 s; `install_wideopen_service.sh` remounts `/` rw,
  installs and enables `wideopen.service`, remounts ro; the unit is a
  **root** service with `Restart=always`/`RestartSec=5` whose `ExecStart` runs
  `find /media/usb -iname 'wideopen_service.sh' -exec bash {} \;`.
- **Stated plainly in the evidence:** once installed, any USB stick carrying
  `wideopen_service.sh` yields root execution with no authentication. Safe on a
  bench, an unauthenticated root backdoor if the image ever returns to a vehicle.
- Recovered the exact Engineering Mode patch set: PIN comparisons `enterMenu ==
  21`/`== 11` removed, `checkSOPVersion() ===` inverted to `!==`, the
  engine call replaced with `false`, plus a `dropbear` → `dropbearmulti` symlink.
  This is what removes the gate permanently after one patched install.
- Confirmed the repack command and added its `*.DS_Store` exclusion to
  `rootfs_patch.py`; 69 tests still pass.
- No exploit, key, decryption or device action is included.

## 0.26.0 - 2026-10-19

- Disassembled the `navi_extended` application assembly in full using
  `dnfile` + `dncil` installed into a local venv under `work/` (nothing global),
  with **every metadata token resolved**. The behaviour is now exact rather than
  inferred from strings.
- Exact logic: an infinite loop that every **5 seconds** runs
  `Directory.GetFiles("/media/usb", …, SearchOption.AllDirectories)` +
  `FirstOrDefault` for **`install_wideopen_service.sh`**, then for
  **`main_loop.sh`**, and — if the first is non-null — executes them with
  `ExecuteBash`, which escapes only `"`, builds
  `/bin/bash -c "<path>"` with `RedirectStandardOutput`, `UseShellExecute=false`
  and `CreateNoWindow=true`, then `ReadToEnd` and `WaitForExit`.
- Operational consequences recorded: the script is **re-executed every five
  seconds**; `install_wideopen_service.sh` takes precedence and is the documented
  persistence step; only the first match of each name is used; the argument is
  the file **path**, not its contents; a blocking script holds the helper inside
  `ReadToEnd`.
- Recorded a command-injection seam in the tool (only `"` is escaped, not
  backticks or `$(...)`) and why it is moot: the operator already supplies the
  script.
- Corrected the previous note, which had described the matching predicate and
  poll interval as unconfirmed.
- No binary committed; hashes and behavioural description only. No device action
  and no execution of the artifact.

## 0.25.0 - 2026-10-19

- The GitLab rate limit cleared, so the **actual entry binary was obtained and
  analysed statically** (never executed). `AppNavi` release 0.2.0 is
  35,201,155 bytes, SHA-256 `9198abf2…85c7`, an ELF x86-64 .NET **6**
  self-contained single-file bundle; the application assembly `navi_extended.dll`
  is only **5,632 bytes** (SHA-256 `dc2ef0dc…4bc7`), recovered by parsing the
  trailing bundle table and inflating the entry.
- Established what the binary actually is: a file scan under **`/media/usb`** for
  **`main_loop.sh`** (and `install_wideopen_service.sh`), executed via
  `/bin/bash -c` with output redirected, in a sleep loop. There is **no
  vulnerability and no memory-corruption exploit in it** — it is a deliberate
  drop-in trampoline that runs a USB script.
- Consequence recorded: the entry primitive is a **legitimate app substitution**,
  so the entire chain rests on the unit's own AppNavi update path. The software
  barrier is trivial; the installation gate is everything.
- Recorded the unit's USB mount point and payload script name, which are required
  for any custom application and otherwise cost bench time to discover.
- No binary is committed; only hashes and behavioural description. No device
  action and no execution of the artifact.

## 0.24.0 - 2026-10-19

- Reviewed the second open-access primary source for this platform,
  Costantino & Matteucci, *"Reversing Kia Motors Head Unit to discover and
  exploit software vulnerabilities"* (JCVHT 19:33–49, 2023, DOI
  `10.1007/s11416-022-00430-5`, 17 pages, full text extracted). It documents
  four vulnerabilities in the **Android/Telechips** Kia IVI lineage
  (`micom`-centric, 116 references; no `AppNavi`, no AES, no `update` mechanism).
  It is the earlier KOFFEE work already covered by child note 04 and does **not**
  transfer to the Linux `S5W_L` path this programme targets. Recorded so it is
  not re-examined.
- `navi_extended` source and release binaries remain unobtainable: GitLab returns
  HTTP 429 on the API, the web tree endpoint and the archive endpoint alike.
  Recorded as an external rate limit rather than a dead end.
- No exploit, OEM key, decryption or device action is included.

## 0.23.0 - 2026-10-19

- Closed two remaining completeness questions as clean negatives and recorded
  them permanently in `HANDOVER.md` so they are not retried.
- **Package completeness:** both the EU `260128` and AU `260319` packages list
  exactly 35 files with **zero unlisted and zero missing**; only the map archive
  and its MD5 sidecar differ by region. There is no hidden or unmanifested
  payload.
- **No key material in the package:** 223 plaintext artifacts scanned for PEM
  headers, base64 X.509 prefixes, PKCS#7 and X.509 signature OIDs and SSH keys —
  no hits (three generic `30 82` byte pairs in binary data are coincidental).
  Key material is device-resident only, which confirms the published technique.
- Retried the `navi_extended` source archive from a different endpoint; still
  HTTP 429. Recorded as an external limit, not a dead end.
- Added an "Established negatives" table to `HANDOVER.md` covering ten ruled-out
  avenues, so future work starts from the right place.
- No exploit, OEM key, decryption or device action is included.

## 0.22.0 - 2026-10-19

- Added `HANDOVER.md` at the project root: a single read-first document covering
  the target identity, the five findings that matter, the end-to-end chain, the
  tool inventory, the three questions that unblock progress, the bench order, and
  an explicit statement of what is deliberately absent and where the honest limits
  are. Written because 25 evidence documents and 11 subagent notes are too much to
  wade through on return.
- No exploit, OEM key, decryption or device action is included.

## 0.21.0 - 2026-10-19

- Closed the boot-image format question with an exact decomposition:
  `iasImage` = **3,385-byte header + 6,210,308-byte payload + 13,035-byte
  trailer** = 6,226,728 bytes, where the payload length is exactly the plaintext
  `_sub` size. The header is variant-specific with no plaintext fields (a search
  for 6,210,308, 3,385, 13,035, 52, 953 and `0x42f08d94` as little-endian words
  finds nothing); the trailer is identical across five variants and package-scoped.
- Corrected an intermediate reading in this session: the header's per-64-byte-block
  entropy of ~5.7 looks structured only because 6.0 is the maximum for a 64-byte
  block; the region is in fact random, i.e. encrypted.
- Established a clean negative: the Linux kernel contains **no** IAS-related
  symbol, string or config option, so `ipk.`/`iasImage` verification is a **boot
  loader** function performed before Linux runs. The format therefore cannot be
  reverse engineered without the SPI flash contents; the boot path is closed
  offline and the OTA path remains the open one.
- No exploit, OEM key, decryption or device action is included.

## 0.20.0 - 2026-10-19

- Added `tools/uk_fw/rootfs_patch.py`, closing the *build* half of custom
  firmware: `list` inspects a rootfs package, `inject` installs a systemd unit,
  appends SSH keys (mode 0600) to `/etc/dropbear/authorized_keys`, or copies
  arbitrary payloads, and `meta` computes the rebuilt file's size and signed
  CRC-32 and rewrites the matching `.ver` record.
- Enforced the vendor archive constraints recovered from the public patcher:
  `--format=ustar` and `--numeric-owner`, since the reader rejects pax/GNU
  extensions and name-resolved ownership. Inputs are never modified.
- Added `evidence/custom-firmware-build-path.md`, separating the two independent
  problems: the cipher (bypassed entirely by the `disableEncryptionUpdate` path)
  and acceptance (the version gate plus the package descriptor binding).
- Added four unit tests for the repacker; the suite now runs 69 tests.
- Recorded that the `navi_extended` release binaries would reveal the exact
  `AppNavi` interface but GitLab returned HTTP 429 during this session, so the
  fetch was backed off rather than retried aggressively.
- No exploit, OEM key, decryption or device action is included.

## 0.19.0 - 2026-10-19

- **Corrected the previous conclusion that downgrade is blocked.** The
  anti-rollback analysis (child note 10) separates the two siblings: on the
  **Linux `S5W_L`** path the version gate is a single userland string comparison
  in `AppSetup`, evaluated after `DecryptToPipe` handles `.lge.upgrade.xml`, and
  the public `navi_extended` FAQ documents a substitution method — older official
  payloads paired with the **latest** `.lge.upgrade.xml` for the same vehicle, so
  a genuine signed newer manifest satisfies the `>=` check while older content is
  written. On the **Android Gen5W** sibling the `update_info` inside
  `system_package` is signed and binds the package, which is why the EV6 report
  was rejected even with corrected `.ver` CRCs.
- Recorded the three remaining obstacles on the Linux path, none of which are
  cryptographic: (a) the feed — the update API currently returns 503, so older
  packages cannot be enumerated; (b) distance — the entry precondition is a
  pre-November-2021 build, five years of package-format change away from
  `260128`; (c) the method is documented against 2021–2022 packages and is
  unconfirmed on 2026 packages.
- Recorded that no monotonic anti-rollback counter (fuse/OTP) is publicly
  demonstrated for this variant, so rollback protection is software-only, matching
  CVE-2023-26245.
- No exploit, OEM key, decryption or device action is included.

## 0.18.0 - 2026-10-19

- Characterised the encrypted boot wrapper (`iasImage` without `_sub`): all six
  variants are 6,226,728 bytes (16,420 more than the plaintext payload); five
  share an identical **13,035-byte trailer** (SHA-256 `41885928…`, entropy 7.976)
  while `iasImage_p5_1920_12` has a different tail; the trailer is package-scoped
  (EU and AU share no suffix) and contains no plaintext exponent marker, unlike
  `_sub`.
- Recorded that this mirrors the OTA footer pattern and supports a single packing
  model: encrypted content plus a package-level descriptor appended verbatim.
- No exploit, OEM key, decryption or device action is included.

## 0.17.0 - 2026-10-19

- Reviewed the public issue trackers of the Gen5 Wide-Open projects. Recorded
  that **downgrade remains unsolved in public**: `navi_extended` issue #2
  ("How do I downgrade?", open since 2022-10-30) reports that editing
  `update.info` did not work, and no answer was published.
- Recorded field evidence that **weakens this programme's own CRC hypothesis**:
  issue #3 (2023-09-23) describes repairing the `.ver` CRC and file size and the
  unit still refusing to install. The arithmetic result (CRC-32 is forgeable)
  stands; the exploitable reading is now treated as unlikely on its own. The
  hypothesis document was amended accordingly rather than left standing.
- Confirmed newer packages ship `appnavi.tar` (not `appnavi.tar.gz`), matching our
  `260128` package; scripts globbing the old name silently do nothing.
- Probed the official update API with the public tool's local-token scheme:
  `apieu.map-care.com` and `api.map-care.com` both return **HTTP 503**;
  `oem-euupload.map-care.com` returns 404/connection failure; two 2023 issues
  report "no cars available on any region". Older-build acquisition is therefore
  at risk, which removes the feedstock for a downgrade even if one became legal.
- Net effect on the plan: the entry gate is unchanged, the integrity gate is
  demonstrably stronger than the `.ver` CRC, and the pre-authentication parser
  surface remains the most promising target.
- No exploit, OEM key, decryption or device action is included.

## 0.16.0 - 2026-10-19

- Analysed the **open-access primary source** for this platform: *"A vehicle
  firmware security vulnerability: an IVI exploitation"* (DOI
  `10.1007/s11416-024-00522-4`, JCVHT 20(4):681–696). Recorded the published
  technique: `DecryptToPIPE` statically links mbedtls and retains an unused
  `mbedtls_printf`, whose register leak exposes the **AES-CBC-128** key; the
  `Key_file` holds the RSA public key plus the wrapped AES key; each file is
  described as content + terminator + SHA + signature; and `AppDMClient`,
  `AppUpgrade` and `DecryptToPIPE` are patched to skip signature checks.
- Established that the OTA key is recoverable with **public** RSA material plus
  one device file, so offline decryption needs only the `DecryptToPIPE` and key
  pair — no further reverse engineering.
- Closed the cross-build ciphertext avenue with measurements: no ECB anywhere
  (zero duplicate 16-byte blocks in 16 MiB samples), no same-offset block
  agreement between EU and AU, and the package footer identical within a package
  but completely different across packages — consistent with a derived IV over a
  package-constant plaintext.
- Recorded a tension: the paper implies a per-file SHA in the trailing block,
  yet the measured tail is identical across three files; the per-file SHA is
  therefore most likely inside the encrypted content. Left explicitly open.
- Extracted the AU boot containers for the first time: same command lines and
  build id as EU, but the kernels differ (126,510 differing bytes, 2,122 ranges).
- Confirmed two dead ends so they are not retried: `navi-updates-lfs` contains
  only a README, and stock Ghidra 12.1.4 has no RL78 processor module (M16C only),
  so the frontkey MCU is not decompilable without a third-party module.
- No exploit code, patch offsets, key-unwrap implementation or device action is
  reproduced.

## 0.15.0 - 2026-10-19

- **Proved that CRC-32 is not an integrity control** for this package format.
  `tools/uk_fw/crc32_forge.py` computes the 4-byte correction that forces any
  chosen CRC-32, and the demonstration preserved the manifest value across a real
  content change: original `0xa09a265d`, modified content gave `0x0338bbdf`,
  correction at offset 8 restored `0xa09a265d` with differing bytes
  `[8,9,10,11,20]`.
- Refined the earlier hypothesis: because `.ver` CRC-32 values are computed over
  **ciphertext**, a CRC-preserving modification still requires the decryption key,
  so this is a **post-execution** persistence mechanism, not a route to first
  execution. That distinction is recorded explicitly.
- Added `tools/uk_fw/gen5w_decrypt.py`, an orchestration harness around the
  unit-derived decryptor with `plan` / `run` / `verify` subcommands. It makes no
  assumption about the vendor binary's interface (the command is a caller-supplied
  template), strips the detected package footer from the model, and classifies
  outputs by entropy and printability.
- Added four unit tests for CRC forging (property, no-op, out-of-range offset,
  arbitrary targets). The full suite now runs 65 tests.
- No exploit, OEM key, decryption or device action is included.

## 0.14.0 - 2026-10-19

- Discovered the OTA container structure from ciphertext alone: each package
  appends a package-scoped **footer** of 14,059 bytes (EU `260128`) or 14,315
  bytes (AU `260319`) to exactly `AppUpgrade`, `.lge.upgrade.xml` and
  `update.tar.gz`. Footer digests:
  `fc1c07cc…` (EU) and `81c18efd…` (AU). The four large payloads carry no shared
  suffix and there is no shared prefix anywhere.
- Established that `.lge.upgrade.xml` is almost entirely footer: only 3,611 bytes
  (EU) / 3,497 bytes (AU) are its own encrypted content, consistent with
  `AppSetup` decrypting it first to read the version.
- Profiled the footer: entropy 7.98 overall and 7.1–7.3 per 256-byte block, no
  gzip/zlib/DER/PEM/X.509 markers and no printable runs, i.e. a structured but
  encrypted descriptor.
- Recorded a **hypothesis** (explicitly not a finding): because the `.ver`
  manifest carries only size and signed CRC-32, and the large payloads are not
  separately signed, per-file integrity may reduce to CRC-32, which is trivially
  forgeable. Falsified if the descriptor holds a cryptographic digest per file or
  the upgrader re-hashes decrypted content.
- Added `tools/uk_fw/ota_structure.py`, which reports shared regions, the
  detected footer, its digest and entropy, and per-file unique sizes, reading only
  64 KiB windows per file.
- No exploit, OEM key, decryption or device action is included.

## 0.13.0 - 2026-10-19

- Recovered the documented Gen5W operating model from the public
  `g4933/wideopen` wiki and `g4933/gen5w` projects, which fills the gap that the
  encrypted userland was hiding.
- Recorded the update flow: `AppSetup` reads `.lge.upgrade.xml`, decrypts it with
  `DecryptToPipe`, and proceeds only when the version is **greater than or equal
  to** the installed version; `AppUpgrade` then performs filesystem, map and
  firmware stages and finally rewrites `/etc/fstab`.
- Corrected an earlier interpretation: the two roots in the recovered command
  line (`mmcblk0p3`, `mmcblk0p5`) are the **A/B system partitions**, not merely
  display variants. A rootfs write goes to the inactive partition, so a failed
  rootfs experiment is recoverable by restoring `fstab`, while a bad boot image
  is rejected by the signed container rather than rolled back.
- Recorded `disableEncryptionUpdate` semantics: it disables decryption only; the
  `.lge.upgrade.xml` version check still runs.
- Recorded the public entry preconditions (`navi_extended` as a replacement
  `AppNavi` installed through Engineering Mode, requiring an unpatched build and
  therefore a downgrade on newer units) and the documented SSH persistence path
  (`/etc/dropbear/authorized_keys`, publickey installer, relaxed
  `dropbear@.service` condition).
- Identified the first gate for the public path: whether `260128` still offers
  "Update AppNavi from USB", and whether any rollback counter exists outside
  `AppUpgrade` (none found in the recovered kernel configuration or symbols).
- Updated `evidence/bench-runbook.md` with the A/B recovery path, the downgrade
  gate and the persistence procedure.
- No exploit, OEM key, decryption or device action is included.


- Added `tools/uk_fw/bench_assess.py`, a read-only orchestrator that runs the
  serial capture, network surface, rootfs survey and boot-container inspection in
  a fixed safe order and writes a single `report.json` plus per-step artifacts.
  Steps are independent and skipped steps are recorded explicitly.
- Verified the orchestrator offline: the image step reports `signature_ok=True`
  and the OEM modulus digest for the packaged container.
- Added `evidence/bench-runbook.md`, the phased operating procedure from physical
  preparation through disclosure, with read-first gates and the exact commands for
  each tool.
- No exploit, OEM key, decryption or device action is included.


- Recovered the keystore root of trust. `manifest_init` (boot initcall)
  `strcmp`s the kernel parameter **`oemkm`**, parses `oemkm=<size>@<phys>` with
  `sscanf("%x@%x")`, copies a 64 MiB-bounded blob out of physical memory via
  `memcpy_from_ph`, validates only a four-field header (type word `0xe`), then
  creates `.manifest_keyring` with `prepare_kernel_cred(0)` **root credentials**.
- Established that `oemkm=` is **absent from all six packaged command lines**, so
  the boot loader places the manifest and injects the parameter. The OEM key is
  therefore not in the root filesystem and not in the kernel image.
- Consequence recorded: root on the rootfs does **not** grant signing capability.
  The OEM public key is firmware-pinned; a signature bypass must be a userland
  decision, matching CVE-2023-26244/26245/26246 and the `update-patcher` approach.
- Recorded a design observation: the manifest blob is trusted implicitly and its
  location is a plain command-line value not covered by the `ipk.` container
  signature. Whoever controls `oemkm=` controls the trusted key set. With
  `CONFIG_KEXEC=y` this is a research direction post-root, not a persistence path.
- Verified **`check_usage_bits`** is a clean four-word subset test
  (`requested == allowed & requested`); a key with an all-ones mask authorises
  every usage.
- Studied **`keystore_backup`**: it gates key export on an OEM signature over a
  user-supplied 136-byte blob, then encrypts the 64-byte client key material to
  the host key and signs the result; the key material is hexdumped under dynamic
  debug before being zeroed.
- Tested a suspected uninitialised-copy defect in **`keystore_get_ksm_key`** at
  instruction level and **rejected it**: the buffer is `[68-byte private][136-byte
  public]`, the code zeroes the private half and returns the public half.
- Subagent research completed: daemon version-fingerprinting triage (dnsmasq,
  hostapd/wpa_supplicant, miniupnpd, dropbear, BusyBox) and SMACK device-access
  analysis. The SMACK note establishes that `/dev` is devtmpfs, so an unlabelled
  node defaults to the `*` label, which combined with the absence of a capability
  check in `keystore_open` makes `/dev/keystore` reachability purely a
  mode-plus-label question once the rootfs is decrypted.
- No exploit, OEM key, decryption or device action is included.


- Added `tools/uk_fw/ver_manifest.py` and verified both official packages end to
  end against their own manifests: EU `NE_E.EUR.S5W_L.001.001.260128` and AU
  `NE_E.AUS.S5W_L.001.001.260319` each report 33/35 files matching size and
  signed CRC-32, **0 mismatches, 0 missing**, with the two files larger than
  2 GB skipped (EU map archive and EU `mango-vr_fixed.tar.gz`).
- Documented the manifest path convention: the record carries the directory in
  the Windows-style field and the filename separately, and the package name
  prefix must be stripped before resolving against a package root.
- Added unit tests: `tests/test_ipk_tool.py` (8 tests covering parsing, signature
  verification, payload tampering, tag tampering, non-`ipk.` rejection,
  re-signing and oversized command-line rejection) and
  `tests/test_ver_manifest.py` (5 tests covering prefix stripping, clean
  verification, mismatches, missing files and large-file skipping). 13 tests
  pass.
- No exploit, OEM key, decryption or device action is included.


- Fully characterised the plaintext `ipk.` boot container. Field `0x018` is a
  constant format/build id, **not** a checksum: it is identical across all six
  `iasImage*_sub` variants whose command lines differ. Earlier zlib and
  CRC-32/MPEG-2 checksum hypotheses were wrong for that reason.
- Established that the six variants differ by only 261–274 bytes (command line,
  one byte at `0x46`, and the trailer), i.e. one kernel serves 1280, 1920/12 and
  p5 layouts.
- Recovered and verified the container signature: **RSA-2048, PKCS#1 v1.5,
  SHA-256**, signed over `[0, hdr+total+4)` = header + payload + 4-byte variant
  tag. `pow(sig, 65537, n)` yields the expected DigestInfo block and the trailing
  digest matches. OEM modulus SHA-256
  `227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6`.
- Established that this modulus appears **only** in the six containers and is
  **absent from the kernel image**, so any pinning lives in the boot loader or
  the encrypted main `iasImage`. Whether trust is pinned or self-referential
  cannot be decided offline and is the highest-value bench question.
- Added `tools/uk_fw/ipk_tool.py` with `info`, `verify`, `extract` and
  `resign`. Verified end-to-end: the OEM image verifies, and a modified
  `init=/bin/sh` image re-signed with a generated test key verifies under the new
  modulus. `resign` produces a correctly formed container for an acceptance
  experiment; it does not defeat OEM verification.
- Added `tools/uk_fw/bench_serial.py` driving the recovered `ttyS2` 115200 8N1
  console (capture, send, port enumeration) so the boot log can be recorded the
  moment the unit is available.
- Dispatched four research subagents: kernel 4.1.27 backport gap, daemon
  version-fingerprint triage, USB gadget/iAP2 protocol surface, and SMACK device
  access.
- No exploit, OEM key, decryption, simulated boot on a vehicle, or device action
  is included.


- Repaired kallsyms recovery for the exact EU kernel. `tools/uk_fw/kallsyms_extract.py`
  fails on this image; three defects were identified: false-positive
  `kallsyms_num_syms`, an odd-aligned marker array, and — most seriously — an
  address-array start taken at the first kernel-range pointer, which mispaired
  **every** symbol by 204 entries while still producing plausible prologues.
- Added `tools/uk_fw/kallsyms_structural.py`, which derives the layout
  structurally and recovers 64,923 symbols in 0.3 s.
- Cross-validated the recovered table against the independent `__ksymtab`
  export table: 4,369 of 4,375 exports match exactly with zero residual
  mismatches. Corrected layout: addresses `0x89f158`, num_syms `0x91de30`,
  names `0x91de38`, markers `0x9dedc8`, token table `0x9df5b8`, index `0x9df940`.
- Because the mispairing was silent, prior Ghidra naming derived from a
  run-start extraction is recorded as unverified and was re-derived. The
  corrected import renamed 25,033 functions and decompiled 41 priority
  functions.
- Established the trust-chain anatomy: `verify_oem_signature` SHA-256s the
  input, then `manifest_key_verify_digest` performs a `manifest_keyring` lookup,
  parses 16 usage-bit bytes from the key description, and calls the asymmetric
  verify op. It is reachable only from `keystore_backup` and
  `keystore_generate_mkey` and is not exported, so **firmware trust is decided
  in userland**, consistent with CVE-2023-26244/26245/26246.
- Reviewed the 26-ioctl `/dev/keystore` boundary. It is defensively written:
  a `size < 0x319` gate against a 0x318-byte staging area ending at the canary,
  overflow-checked user pointers, matching allocation and copy lengths, and
  post-dispatch zeroing. No memory-safety defect was found in the reviewed set
  — a bounded negative result, not proof of absence. A hypothesis about
  uninitialised tail fields in `TEST_VERIFY_ECC_SIGNATURE` was tested and
  rejected (decoded size 0x120 covers the offsets read).
- Recorded that `keystore_open` performs no capability check, so access depends
  on the device-node mode and SMACK label, which remain inside the encrypted
  rootfs. `keystore_verify` and `keystore_register` are exported.
- Confirmed the EU map ZIP is plaintext (1,335 entries) but data-only, that the
  VR package is plaintext TTS/ASR data with no executables, and that the map
  package ships a Gladman Rijndael licence — a hint at the AES implementation
  family, not a key.
- Re-stamped `ART-T6-CHANGELOG` after this documentation update. The frozen T6
  acceptance is therefore stale and requires re-review; this entry records the
  change rather than concealing it.
- No exploit, key, decryption, modified image, flash procedure, or device
  action is included.


- Established that the official `260128` userland is soundly encrypted: entropy
  ~8.00 per envelope, no keystream reuse between files, and no plaintext magic
  in any encrypted payload. Confirmed the manifest checksum is `zlib.crc32`
  against the plaintext `Checksum.txt`.
- Recovered the complete kernel command line from the plaintext
  `iasImage*_sub` containers: serial console `ttyS2` at 115200 8N1, early console
  at MMIO `0xfc000000`, `init=/lib/systemd/esinit`, dual root (`p3`/`p5`),
  Intel DRCFG USB0 mux, `ramoops` at `0x50000000`, and Intel Broxton platform.
- Integrated the public Gen5W prior art (`laralbir` EU standard Gen5W and the
  `gitlab.com/g4933/gen5w` tool group): the `navi_extended` → `DecryptToPIPE` +
  `decryption_key.der` → `update_decryptor` → `update-patcher` chain.
- Recorded the two MASS_PRODUCT Engineering Mode gates (SOP check plus QML PIN
  `21`/`11`) and the published alternative routes (UART, GDS, older build).
- Recorded the published ciphertext-level structure: re-sealed 16,417-byte
  modem trailers, stable container prefixes (14,048 / 14,122 / 640 / 112 bytes),
  and which payloads changed functionally between `251204` and `260128`.
- Confirmed `mango-vr_fixed.tar.gz` is real gzip but TTS/ASR data only (49
  entries in the AU package, no executables); frontkey MCUs are Renesas RL78.
- Added `evidence/known-exploits-and-cve-survey.md`,
  `evidence/gen5w-public-exploit-ecosystem.md`, `evidence/bench-hardware-root-path.md`,
  and `evidence/network-surface-and-wifi-root.md`, plus four child-thread notes.
- Reinforced the scope boundary: no exploit, decryptor key, modified image,
  flash procedure, or live-vehicle action is included.


- Recorded the active target as an AVN bench unit removed from the vehicle, and
  scoped research to that unit with no vehicle connected.
- Added `tools/uk_fw/dump_survey.py`, a read-only survey of a rootfs dump or
  ext4 image covering accounts, setuid/setgid, file capabilities, SMACK
  policy, systemd units, boot command line, debug surfaces, persistence paths
  and world-writable files.
- Added `tools/uk_fw/net_surface.py`, a TCP surface mapper with banner, HTTP,
  TLS-certificate, SSDP and mDNS discovery for an owned bench unit.
- Added `evidence/bench-hardware-root-path.md` with the UART / bootloader /
  storage / software ladder, the interface survey checklist, and the Gate 4
  recovery preconditions applied at bench scale.
- Added `evidence/network-surface-and-wifi-root.md` mapping Wi-Fi exposure
  modes, service-to-vulnerability classes, and the evidence each class needs.
- No exploit, payload, credential attack, flash procedure, or live-vehicle
  action is included.

## 0.5.1 - 2026-10-19

- Consolidated every IONIQ-owned research artifact, evidence file, Council
  package, test, analysis tool, ledger, plan, history, changelog and repository
  policy under the top-level `ioniq research/` directory.
- Preserved all relative paths inside the IONIQ project so evidence references,
  artifact hashes and test commands continue to resolve from that directory.
- Left the Kona root documents and every `kona_research/**` file in place and
  did not incorporate concurrent Kona changes into the IONIQ reorganization.

## 0.5.0 - 2026-10-19

- Verified completion of the exact European `260128` package: 35/35 payload
  sizes, 35/35 signed CRC-32 values, and all three supplied MD5 sidecars.
- Added the complete 36-file SHA-256 inventory identity.
- Replaced the interim EU/AUS comparison with the complete matrix and exact
  corresponding-kernel comparison.
- Added `evidence/eu-custom-firmware-feasibility.md`, separating initial
  execution, privilege transition, persistence, trust, recovery and regional
  compatibility prerequisites.
- Documented candidate defensive vulnerability-audit surfaces and exact
  evidence requirements without an exploit chain, crafted update, modified
  firmware image, flashing procedure or vehicle interaction.

## 0.4.0 - 2026-10-19

- Corrected the active vehicle to a UK-origin 2021 IONIQ 5 and added the exact
  European `260128` package acquisition and resume evidence.
- Added complete 64,923-symbol kernel recovery and symbol-aware Ghidra
  decompilation, including the LG keystore/OEM-signature trust anchor.
- Added the exact-build published-root-method and native Linux application-
  loading applicability assessment.
- Added an interim byte-level EU/AUS package comparison and explicit region-
  transition feasibility gates.
- Preserved the accepted Australian work as historical comparison evidence and
  made no Kona-owned changes, vehicle writes, media writes or firmware flashes.

## 0.3.0 - 2026-10-19

- Changed the private-repository retention policy so raw firmware, extracted
  analysis trees, captures, device-specific dumps, vehicle identifiers, and
  analysis workspaces may be deliberately staged and committed.
- Narrowed `.gitignore` to retain the downloaded 9.5 GB official package tree,
  live credentials/private keys, and regenerable cache noise outside Git.
- Kept exact-stage review, private-remote verification, provenance manifests,
  Kona path separation, and third-party-data controls in force.

## 0.2.0 - 2026-10-19

- Added `Ioniq5-research-plan.md`, the integrated car-specific research plan.
- Bound every accepted evidence artifact to its SHA-256 and traced R1-R11 to
  the accepted T1-T5, T7, and T2 work.
- Recorded the exact official Australian package identity, including the
  36-file inventory, the sorted-tree digest, all 35 manifest records, the map
  and voice MD5 values, the front-key CRC-32/MPEG-2 check, and the nineteen
  opaque envelopes.
- Added a subsystem register covering the AVN, cluster, smart key, keyless
  entry, immobilizer, body controller, gateway, CAN domains, diagnostics,
  telematics, ADAS, chassis safety controllers, VCU, BMS/HV/charging, HVAC,
  camera/audio, USB and projection, and the update supply chain.
- Added Phases 0-8 with passive-first exit criteria and stop conditions.
- Closed the T6 portion of ASTRA-G7-S01 by defining Gate 4 as a four-part
  conjunction, separating physical restoration from persistent software-state
  coverage, rejecting claims of an exclusive recovery route, and making Gate 4
  a hard stop before any state-changing stage.
- Added privacy and confidentiality handling for raw captures, identifiers,
  personal data, storage images, and credentials.
- Added a root `.gitignore` excluding firmware and archive formats, package and
  extraction trees, dumps and captures, credentials, identifiers, and
  personal-data workspaces.
- Recorded Council generation 10 acceptance of frozen batch 8 with three
  COMPLETE seats and truthful DeepSeek replacement labels.
- No USB medium was written, no firmware was flashed, no vehicle was connected,
  and no actuation was performed.

## 0.1.0 - 2026-10-19

- Initialized the dedicated IONIQ 5 research history and changelog.
- Recorded accepted T1 identity, T3 method catalogue, T4 passive and hardware
  route map, T5 trust-boundary and subsystem map, and T7 NEMESIS compatibility
  assessment.
- Established the rule that the car's installed build is read before method
  selection and that published-family evidence is not installed-car evidence.

- Prepared a public release snapshot: removed raw owner and upstream diagnostic exports, removed full-text third-party artifacts, anonymized local paths, and added a sanitized owner USB finding note. Public visibility awaits cached-history cleanup.

## Public repository snapshot - 2026-10-28

- Initialized a fresh public Git history from the sanitized tree so earlier
  private commits are absent from this repository.
- Pointed the Git-scope guard and its tests at
  `JaredReabow/ioniq-5-Reverse-Engineering`.
- Added a public entry point and clarified the publication boundary.

## Imported VM milestones from the private working tree - 2026-10-28

## 0.61.0 - Parallelism/Council measurement-plan checkpoint

- Activated the requested Parallelism + three-seat Council workflow using inline
  workers only. Astra-high led planning; Astra-high and two independent Sol-medium
  seats reviewed and reconciled the same frozen package. The Council checker
  returned `COMPLETE` for the **plan only**, with package fingerprint
  `c59ac8a0d4ece96fd8fab5fe8a6795789697c95394d6e548a02dc8484052bbb5`
  and packet SHA-256
  `528649b5b337fb0b76bafd6cb9b020e572851ec33136c6d0927a5c38a12ef790`.
- Corrected the experimental claim boundary: captured `-4` supports an invalid
  width-derived copy count, but does not yet prove width changed during that
  update or that the original width was `-1`. The accepted plan distinguishes
  EGL call-site arguments from the actual resolved libc entry and requires
  PLT/IFUNC-aware evidence before a fix.
- DeepSeek EC-01/EC-02 did not run. The live tool rejects the required direct
  provider route `deepseek/deepseek-v4.1-flash` as unknown; its suggestion of an
  OpenCode route is not authorized. Parallelism and Council policy now requires
  direct `deepseek/...` provider routes and forbids intermediary fallback. No
  substitute model, implementation, VM run, new thread or bypass routing was
  used. Both tasks remain blocked in the validated ledger.
- Council suggestions require downstream contracts to record both mapped vendor
  EGL and project Mesa identities, numerical capture caps, debugger restoration,
  and host-owned disposable-VM termination. The scheduler still lists the prior
  heartbeat paused; update remains impossible because the exposed API requires
  fields it simultaneously rejects for interval schedules.

## 0.60.0 - bounded fault-time stack and EGL caller

- Added VM-only `ptrace_crash_observe.c`: explicit target allowlist, SEIZE rather
  than group SIGSTOP, bounded 64-word stack/64 KiB maps and original fatal-signal
  redelivery. Compiles statically with warnings-as-errors. Timeout/cancellation/
  group-stop paths remain dynamically untested and are not broadly accepted.
- Completed a short snapshot experiment with guest invalid-PID/disallowed-target
  tests and actual Camera fault capture; 64 stack words read, SIGSEGV re-delivered.
- Identified immediate memcpy call site in vendor EGL software put-image code.
  Cached width-derived stride precedes an update that can change the width;
  captured stride/count registers are -4. Original entry arguments/order remain
  to be measured before a fix. Added qualified investigation I-001 to the
  defensive register, not a confirmed exploitable vendor vulnerability.
- Complete archive SHA-256:
  `e0884a3c11582ed2b986db28f2673b7fde9297a1871f2633ad13672b2dfdeaae`.
  Safe extraction/digest checks pass; 168 repository tests pass; base rootfs
  independently rehashed unchanged. No new threads, commits or fabricated state;
  no independent-model review obtained due the recorded host worker error.

## 0.59.0 - focused early-client core capture

- Completed a short no-NIC/snapshot early-startup experiment in 44.83 seconds,
  capturing one 80 KiB AppCamera core with eight thread-register notes. No full
  agreement/Navigation sequence was attempted. Verified early-client decoration
  value is `1`; this does not validate AppNavi startup.
- Core notes/program headers confirm SIGSEGV/SEGV_MAPERR at libc offset
  `0x128dde`: vector-store destination lies 64 bytes below a writable mapping.
  Fault-thread stack bytes are absent; caller/original copy length remains unknown.
  Modified loop counter is not asserted to be an original argument.
- Requested coredump filter `0x10` read back zero; actual stored memory coverage
  is reported instead of assuming filter behavior. Retained validated core-note
  report, complete archive and exact scripts. Base rootfs rehashed unchanged.
- Archive SHA-256:
  `10fbb21b674ab1795c5e2b52d4e04ad47611f8674c4ac5ed43d283322c24987c`.
  Shell syntax/diff whitespace checks pass. No new thread, image mutation,
  vulnerability classification or Navigation-success claim.

## 0.58.0 - community-source reconciliation

- Recorded the owner's supplied channel-summary leads in
  `evidence/community-chat-leads.md`, explicitly not independently accessed or
  validated. Separated known tools from new compatibility/acquisition leads.
- Retained the tentative CV_E 220721 recollection as different-model comparison
  evidence, not an IONIQ install/downgrade recommendation. Bounded historical
  downloader availability by model, region, endpoint and time.
- Added current-reading warnings to three older evidence notes whose plaintext-
  recovery/API conclusions are superseded or too broad for current VM work.
- Added the reported signature-blocked updater attempt as unvalidated provenance
  for V-005, not a confirmed vulnerability. No fetching, new hardware testing,
  firmware installation or VM run occurred from these chat leads.

## 0.57.0 - 2026-10-27

- Corrected the delegation explanation: inline `spawn_worker` is exposed and
  supports model selection without new chat threads. Earlier statements that
  only child-thread delegation existed were wrong. A useful read-only dispatch
  requesting the configured DeepSeek route failed with host error
  `store.runWorkerToolResult is not a function`; no worker result or runtime
  routing was verified. Operations/handover now identify the actual blocker.
- Executed a snapshot-only decoration-unset control, preserving all other
  baseline flow and existing compatibility behavior. Complete archive recovered
  and digest-verified; harness exit 0 is not feature acceptance.
- Negative semantic result: repeated Camera/Standby crashes, agreement false,
  AppNavi not launched, manager queries 0/0 and all screenshots remain splash.
  The intended child value/geometry was not verified. Do not adopt this change
  or infer a Navigation fix; early-client environment/crash observation is missing.
- Mapped the repeated crash site to libc non-temporal vector store
  `vmovntdq %ymm0,(%r9)` at offset `0x128dde`. Caller/length/register context is
  unknown; this is a write fault, not proof of unsupported AVX or a vendor bug.
  Verified canonical and both new run manifests use the same CPU/memory profile.
- Identified a lower-overhead next capture: vendor kernel supports ELF cores,
  while guest has no inventoried gdb/gdbserver. Proposed bounded snapshot-only
  early-client core-note capture before writing a new sampler; not yet executed.
  Header-only filtering will not provide a complete stack backtrace.
- Complete archive SHA-256:
  `648b5d30c169b2e4adaa2e8cf069742fd5b3d779b0ef1d6d7e63fead7f6910e9`.
  Retained exact source delta, summary, logs and evidence. Base image rehashed
  unchanged; baseline preserved, no new threads or vulnerability claim.

## 0.56.0 - 2026-10-27

- Ran an observation-only wrapper around the unchanged baseline launcher flow in
  isolated QEMU snapshot mode. Completed command exit 0 without timeout; captured
  26 AppNavi maps snapshots and allowlisted environment/mapped-file hashes.
- Runtime maps confirm the analyzed QtWayland client and EGL plugin load. Actual
  AppNavi environment has decoration-disable `1:1`; decoration plugin also loads.
  Parser effect and causal impact are unverified, not a completed fix.
- Authentic Home visibly renders before Navigation. Manager again follows
  `11/11 → 35/11 → 11/11` with FG delivery and status 5/window 0. Final return
  screenshot is black: manager-state return is not visible-Home acceptance.
- Follow-up static review confirms decoration-disable is parsed as a decimal
  scalar via QByteArray::toInt and cached, not as a colon-separated list. The
  inherited `1:1` is malformed for this consumer; exact-library execution of the
  parser remains untested. No environment correction has yet been applied.
- Raw Wayland requests were not captured despite WAYLAND_DEBUG; next observe
  actual hide/attach execution without changing behavior. Retained late cleanup-
  vicinity Camera/Radio crash messages without calling them vulnerabilities.
- Complete archive SHA-256:
  `6019ec6e42cacce8a41fdc79c7dd9705487efdc0a53b741313e6b5b7aad01d84`.
  Decode digest verified; extracted safely. Base rootfs independently rehashed
  unchanged. All 168 tests, shell syntax check and diff whitespace check pass.
  No new threads, image mutation, synthetic callbacks or commits.

## 0.55.0 - 2026-10-27

- Confirmed constructor connection of the same Qt object's visibleChanged(bool)
  to AppNavi onVisibleChanged(bool), refining the prior signal-source uncertainty.
- Traced recovered QtWayland false-visibility handling: explicit null-buffer
  attach/commit occurs only when a virtual discriminator returns zero. Recovered
  EGL plugin inherits that handler and its discriminator returns one, skipping
  that branch. Retained disassembly, relocation evidence and exact signal strings.
- Read-only extraction confirms current-image QtWayland library and EGL plugin
  bytes match the analyzed originals. Runtime selection remains unverified:
  launcher logs inspected lack backend-load identity and alternate library
  search paths precede `/usr/lib`. Next run must first capture mapped identities
  and hide requests without changing behavior.
- This is not yet a guest-backend/root-cause proof. Next verify runtime library
  selection and actual commits; explain older positive controls before
  proposing a narrowly scoped VM adapter. No vendor state or callback fabricated,
  no images changed, no new threads or vulnerability claims.

## 0.54.0 - 2026-10-27

- Host execution recovered; no QEMU/LLVM worker was found in the process check.
  Fresh bounded shell disassembly and read-only current-image extraction passed.
- Current-image IVI shell matches the recovered original. Surface creation
  initializes cached size to 0/0; configure suppresses unchanged dimensions and
  calls layout configure only after a size change. This narrows the prior
  initial-zero hypothesis: no automatic BG event is expected solely from a
  newly created zero-size surface through this path.
- Positive retained controls now show Camera and Standby each configure
  1926×753 → 0×0, then emit BG successfully and reach the manager. Retained
  hashed event excerpts. This demonstrates an earlier working VM transport and
  narrows the next task to AppNavi's hide/unmap/buffer-commit sequence.
- AppNavi visibility follow-up: `onVisibleChanged(false)` sets first-hide state,
  may send the one-shot boot notification, and calls renderer clear/swap. This
  does not prove parent Qt-window unmapping or a null Wayland buffer commit.
  Retained bounded disassembly; next separate the native map-screen callback
  from the parent-window hide path.
- Located authentic `QWindow::hide()` at `0x3362275` in AppNavi foreground
  handling, behind base-result and screen gates. Latest PID-specific logs show
  widget foreground activity but no matching primary-screen hide diagnostic;
  this remains a bounded log observation, not proof of absent invocation.
- Updated evidence and handover. No VM/image edits, new threads or vulnerability
  claims; `git diff --check` passes.

## 0.53.0 - 2026-10-26

- Follow-up provenance: read-only extraction of both compositor paths from the
  current image matches the original module digest; retained Weston log records
  loading the `/usr/lib/weston` path. This is not a historical memory digest.
- Shell-module follow-up commands timed out; completion is unverified. Resume
  only after checking host/process health; do not start duplicate analysis/VM
  runs. Existing scheduled task remains observed active, but prompt update is
  still rejected by scheduler validation.
- Recovered the original compositor callback's final FG/BG branch: any positive
  width or height emits FG; BG requires both non-positive. Exact full-screen
  dimensions are not tested, so changing 1926×753 to 1920×720 would not repair
  that branch. No geometry fix was applied based on the prior hypothesis.
- Hash-identified byte-identical recovered compositor copies and retained LLVM
  disassembly. Next inspect initial configure ordering and verify guest loaded
  module identity. Distinguish the local callback from the nearby exported
  function despite LLVM nearest-symbol labels. No runtime experiment, image
  mutation, synthetic BG event, new thread or vulnerability claim occurred.

## 0.52.0 - 2026-10-26

- Recovered exact QString-list membership after display matching; the subsequent
  AppNavi substring check is a separate predicate. Pending global initializes
  nonzero (`0xffffffff`), so initial zero state is not established as the cause.
- Correlated the full retained latest DLT log: authentic AppNavi surface 3000
  produces an FG callback received by ApplicationManager before status 5/window
  0. The log has no BG-info or naviWindoeCreate diagnostic matches. This narrows
  the next investigation to compositor FG/BG classification/routing.
- Recorded 1926×753 parent geometry as an observation, not a causal conclusion;
  decoration-disable environment is already set. Retained hashed event summary
  and matcher disassembly; updated evidence and handover. No VM changes or new
  runtime run; no new vulnerability claim. `git diff --check` passes.

## 0.51.0 - 2026-10-26

- Traced the window-setter caller into `slotNotifyBGInfo`, whose diagnostic
  identifies surface-ID, display and app-ID inputs. The AppNavi notification
  path additionally requires a display/string helper match, a nonzero global
  gate, and case-sensitive `AppNavi` containment; it clears that gate afterward.
- Recorded exact control-flow addresses and unknown matcher/global semantics
  in the Navigation evidence note. Next trace the upstream event caller and
  gate initialization rather than force a notification. No VM mutation or new
  runtime acceptance is claimed; diff whitespace validation passes.

## 0.50.0 - 2026-10-26

- Recovered ApplicationManager's exact Qt subscription to
  `notifyNaviLaunched(int)` and the routine producing the recorded diagnostic.
- Identified `window[%2]` as a separately latched receiver byte (+0x20), not a
  second boot-signal argument or a surface ID. Zero gates downstream dispatch.
  Adjacent vendor `naviWindoeCreate` code updates the byte and replays cached
  status (+0x1c); next trace direct caller `0x19108d` to recover its producer.
- Retained full LLVM disassembly and bounded extracts; updated Navigation
  evidence and handover. Status-5 enum semantics and runtime acceptance remain
  unresolved. No flags were forced and no VM/image/thread changes occurred.

## 0.49.0 - 2026-10-26

- Identified original ApplicationManager by SHA-256 and mapped six matching
  notification/interface string locations for receiver triage. No handler address
  or enum semantics is claimed from literal strings alone.
- Ordinary/dynamic symbol searches did not expose named handlers. REA deep
  providers are unavailable in the current environment configuration; no tooling
  configuration was changed. Retained raw locations and evidence limits in the
  Navigation contract note and project-local JSON. No target execution or image
  mutation occurred; `git diff --check` passes.

## 0.48.0 - 2026-10-26

- Resolved notification string references against SHA-256-identified original
  recovered AppNavi using read-only ELF section mapping. The function first
  calls `com.lge.avn.applauncher` `/Inform` interface
  `com.lge.avn.applauncher.inform` method `launched(30)`, then emits
  `/navigation_map` interface `com.lge.hkmc.avn.appnavi.naviboot` signal
  `SendNaviBootFail(5)`. These are distinct registration/status messages.
- Retained raw mappings in `work/vm/vendor-userspace-260128/appnavi-notification-strings.json`
  and conclusions in `evidence/navigation-launch-status-contract.md`.
  Located original ApplicationManager for the next receiver analysis. Enum
  semantics, caller selection and window-state producer remain unresolved.
- No target execution, image modification, new threads or security findings.

## 0.47.0 - 2026-10-26

- Reviewed existing saved AppNavi notification disassembly. This function sends
  literal status `5` after an initial one-shot gate; it does not derive that
  integer from engine state within the reviewed function. Exact enum semantics,
  message identity and manager window-state producer remain unresolved.
- Added `evidence/navigation-launch-status-contract.md` with instruction
  addresses, bounded conclusions and next exact receiver/string-mapping work.
  No image mutation, fresh VM run, new thread or vulnerability claim occurred.
- Existing active scheduled-task prompt update was rejected by tool validation;
  no successful update or replacement schedule is claimed. See operations/history.

## 0.46.0 - 2026-10-26

- Reconciled current progress against the existing handover, detailed changelog,
  append-only history, corrections, Git history and security notes. Retained
  existing milestones; no fresh firmware or VM success is claimed.
- Backfilled the history after its 2026-10-19 cutoff with source-labelled
  retrospective milestones, including the corrected VM boot, module-loading
  observation, native userspace recovery, authentic Home and incomplete
  Home↔Navigation integration.
- Added `Ioniq5-VULNERABILITIES.md`, a separate defensive register with evidence,
  preconditions, remediation and acceptance tests. It distinguishes previously
  VM-verified unsigned-module loading from unvalidated keystore/trust/update
  candidates, rejected hypotheses and third-party modification hazards.
- Added `PROJECT-OPERATIONS.md` with the full-VM objective, current blocker,
  append-only rules and an explicit existing-chat-only scheduled prompt draft.
  Scheduling awaits owner confirmation of interval and active-work behavior.
- Read-only routing inspection found the installed DeepSeek Flash builder
  statically ready, but inference routing remains unverified. This session lacks
  native role-selectable subagent tools; no child threads or workers were
  created, and no model/router configuration was changed.
- Preserved the pre-existing dirty source tree, untracked research artifacts,
  firmware and VM images. No commits, pushes, flashes or new VM runs occurred.
- Validation: 168 repository unit tests pass; `git diff --check` passes. Verified
  that the history's original 6,819-byte prefix remains byte-identical.

## 0.45.0 - 2026-10-26

- Added a launcher-local `execve` interposer that supplies the EGL compatibility
  preload only to AppLauncher's original signature-checked AppNavi child. It
  does not directly launch a duplicate AppNavi and does not preload unrelated
  vendor applications.
- The original AppLauncher-owned AppNavi reached map-engine success, selected
  logical `Samples: 2`, created parent surface `3000` with `AID(AppNavi)`, and
  created child surface `4903` while AppLauncher and ApplicationManager remained
  responsive.
- Recovered AppNavi's exact startup decision in
  `NimoExSLApplicationLinux::onInitializeDone()`: offset `0x33b48be` compares
  elapsed startup with `0x59d7` (22,999 ms), and the slow path invokes
  `SendToAppLauncherNaviLaunchedToExcute()`.
- Added a fail-closed, sentinel-gated, executable-scoped VM timing control. It
  validates the expected four immediate bytes and changes only the in-memory
  startup deadline from 22,999 to 180,000 ms using the PIE load base; the signed
  AppNavi file is unchanged. The first non-PIE-aware attempt is retained as a
  negative control because it caused AppNavi `SIGSEGV`/restart churn.
- With the corrected control, AppNavi completed initialization at 106,464 ms,
  created its parent window, and entered the launch-status path only after the
  authentic window event. This ruled out the 22,999 ms timeout ordering as the
  sole cause of the incomplete manager transition.
- The launch path still emitted `SendNaviBootFail(5)` and ApplicationManager
  logged `notifyNaviLaunched[5] window[0]`. Manager state remained `35/11`, no
  Navigation frame was foregrounded, and the authentic return request restored
  state `11/11` plus visible Home. Full Home↔Navigation acceptance remains
  unproven.
- Latest runner SHA-256 is
  `906e734012a9a9cac35aed2e9258674215b407a93cdce9e58024a2f78bf8dd9f`;
  host-log SHA-256 is
  `de9977d671cb203f918d878f939777c1eea330bad90dd2ca0643b6ba57c60021`;
  complete evidence archive SHA-256 is
  `a0e2100ca5a0eb72426db6179c88a27e34abe5928d8a364ce9f14d0e9bfd52b8`.
- Current rootfs SHA-256 is
  `4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f`;
  `prepare.json` matches and `e2fsck -fn` passes.

## 0.44.0 - 2026-10-26

- Established the first semantically corroborated authentic profile-confirm
  path under global two-thread llvmpipe. AppStandbyClock logs
  `confirmSkPressed()`, `onPressedButton`, `onReleased`, and
  `HANDLER_CONFIRMSCREEN_BUTTON_CONFIRM_CLICKED` after bounded pointer input to
  the observed enabled Confirm control.
- Standby progresses from `14` to `12`; ApplicationManager explicitly logs
  `is_standby_agree_pressed standbyStatus[12] result[1]`. Exception-filter
  masks `66` and `161` both return zero, superseding the prior mask-`161`
  result `32` seen before agreement.
- The immediate Home-transition D-Bus out value remains `255`, but downstream
  evidence proves it is not sufficient to classify the asynchronous request
  as rejected: manager current AppID becomes Home `11`, Home returns `ret[1]`,
  drawing AppID becomes `11`, and IVI foregrounds run-specific surface `1001`.
- Added the separately named VM-only Home-settle control. It pauses only
  ApplicationManager for 55 seconds after authentic `requestShow(APP_HOME)` so
  the unmodified Home binary can finish its first frame without a false
  production-liveness kill under x86 TCG software rendering, then resumes the
  manager and repeats the authentic Home request. It does not fabricate an
  alive reply, acceptance state, manager result, application ID, or pixels.
- Captured visibly composed authentic Home at 1920×720. The final vehicle,
  battery/range, and Media Off frame has SHA-256
  `23ccd6e6002d8bceddac3a64b2c94538cb844cc9aa274b44d18ada876d2cc968`.
- Positive evidence archive SHA-256 is
  `87d81b278f8b1bb20236faedd17dda0493b49b6cfc1e0fd2f1acfe8b8d2c6f5e`;
  host-log SHA-256 is
  `2c6c7ed142cb84b7dcc5daf5a9adb01a2e86934c731ae5653efa5d0d80d93b95`.
- Full Home↔Navigation operation remains unproven. AppNavi, data-bearing
  micom/CAN methods, authentic persistence, and production-speed liveness
  behavior remain separate unresolved boundaries.
- Current rootfs SHA-256 is
  `8a686d4bf0b278d7e99dd5d94181a58e5b5ef147bff9f99444a25d0134e16756`;
  `prepare.json` matches and `e2fsck -fn` passes.

## 0.43.0 - 2026-10-26

- Reached and repeatedly foregrounded the authentic AppStandbyClock
  profile-confirm screen with restored production ASTC assets. Runtime QML
  observation places the enabled Confirm control at `x=471..1179`,
  `y=621..699`; the transformed pointer point is inside it.
- Added exact-build observational pointer-focus logging to
  `tools/uk_fw/guest/weston_vm_input.c`. Every phase of the bounded pointer
  gesture remains focused on the authentic AppStandbyClock PID, excluding a
  late AppEURadio/Home client as the current routing owner.
- Identified the authentic screen/Loader sizing defect in this VM: the loaded
  `QRootScreen` and parent Loader resolve to `0×0` while explicit-size children
  render outside them. A separately named VM compatibility control adds
  `anchors.fill: parent` to both alternating Loaders and yields a complete
  `1920×720` screen → Loader → main-root ancestry without changing the legal
  handler or model state.
- The Loader repair does not by itself deliver Qt Quick input. A direct
  full-screen observational MouseArea still receives no press even though
  Weston sends motion/down/up to the correct client.
- Added bounded syscall and RIP observers. The QtWayland thread receives the
  three expected Wayland input batches (`recvmsg` 20/72/24 bytes), while the
  main GUI thread remains runnable in userland. All 32 sampled instruction
  pointers map inside Mesa 18 `swrast_dri.so`; Qt cannot dispatch the queued
  input while synchronous software rasterization monopolizes the GUI thread.
- Negative VM controls—threaded render loop, `vblank_mode=0`, two softpipe
  threads, hidden live status bar/noninteractive layers, scheduler priority,
  temporary AppNavi quiescence, `SIGCONT`, and a 60-second post-input wait—do
  not produce the authentic Confirm handler. None is treated as acceptance.
- Standby remains `11`, the Home transition result remains `255`, and no legal
  confirmation, filter-bit clearance, or normal Home↔Navigation transition is
  claimed.
- Current rootfs SHA-256 is
  `32f4e81f3e637c7fc3c2b3457852b7b8473dda4f2cc0288bff11618cdda5abee`;
  `prepare.json` matches and `e2fsck -fn` passes.

## 0.42.0 - 2026-10-26

- Corrected the full-chain Qt/Wayland environment: the probe no longer
  pre-sets `QT_WAYLAND_SHELL_INTEGRATION=ivi` before authentic AppLauncher
  appends `:ivi`. The invalid `ivi:ivi` value is gone; Qt clients load
  `libivi.so` and log `Using the 'ivi' shell integration`.
- Added `--micom-serial` to the offline VM harness, providing guest
  `/dev/ttyS1` through a project-local Unix socket while retaining the no-NIC
  boundary. The authentic micom daemon now configures 115200-baud serial and
  registers `com.lge.car.micom`, although hardware-dependent boot-info calls
  still do not complete.
- Captured authentic `/Ihu` and `/Can` introspection and established the exact
  `AskSysBootinfo() -> ay` contract. Consumer disassembly and controlled runs
  confirm a 35-byte reply.
- Added fail-closed VM research helper
  `tools/uk_fw/guest/micom_dbus_sim.c`. It supplies only the exact boot-info
  data reply, exposes evidence-derived introspection, acknowledges only exact
  transport signatures, logs all byte-array/int32 arguments, and rejects
  unimplemented data-bearing methods. It is not recovered firmware or a full
  micom/CAN emulator.
- The corrected candidate profile makes AppLauncher select HMC, vehicle code
  `0x26`/38, Europe, 12.3-inch display, RHD, Navigation, Modem, and English
  instead of the prior LX2/Korea fallback. Remaining zero option fields are
  explicitly incomplete rather than claimed as an authentic Ultimate profile.
- Full-chain run `1792936845027660000` reached concurrent authentic activity:
  AppNavi reported engine success and created surfaces `3000` and `4903`;
  AppHomeScreen finished QML drawing and created surface `1004`;
  AppLauncher, ApplicationManager, and Home remained alive at the evidence
  checkpoint.
- Reclassified AppNavi's later `SIGTRAP`: ApplicationManager's liveness
  watchdog explicitly executes `killall -5 AppNavi` after missed responses.
  No spontaneous SIGSEGV/ABRT/BUS/ILL was found in that trace set.
- Direct-launch no-`strace` control run `1792937492664474000` reproduces the
  watchdog kill, excluding syscall tracing as the sole cause. Session-bus
  evidence identifies the exact liveness path: AppNavi answers the first
  `org.freedesktop.DBus.Peer.Ping` at `/navigation_map`, then fails to answer
  eight later Pings while software-rendered startup continues.
- Captured 301 micom calls over 34 method signatures, including exact CAN IDs,
  masks, registration records, CPU-alive transitions, boot-complete states,
  and DID/version writes. No CAN signals are fabricated yet; payload semantics
  must be mapped consumer-by-consumer first.
- The final frame remains splash. Home is still marked non-visible, AppNavi is
  watchdog-terminated, persistence resource tables are absent, and
  data-bearing micom/CAN transitions remain to be implemented and tested.
- Updated the current image identity to
  `817ca674b0e181209ca154236c9fc7d284b085caa0b045c5e4e66cd2fd081f5d`;
  copy-on-write checkpoints and `e2fsck -fn` controls passed.
- All 21 focused VM harness tests and all 167 repository tests pass; JSON
  manifests parse, Python compilation succeeds, and `git diff --check` passes.

## 0.41.0 - 2026-10-25

- Validated native TE2/xcrypt decryption for current EU/AU packages and
  recovered the authentic rootfs, GUI, AppNavi, updater and RW-data userspaces.
- Booted recovered Weston/IVI with project-local Mesa 18 `softpipe`; authentic
  `AppHomeScreen` now renders a complete 1920×720 frame, and pointer/touch
  events reach authentic Qt/QML.
- Recovered launcher identity for AppNavi: AppID `30`, parent IVI surface
  `3000`, launcher path `/navi/navi/Bin/AppNavi`.
- Added a bounded authentic EU map/core/skin subset. AppNavi reaches
  `### Navi Engine Init Success ###`, loads the authentic theme image and
  night skin, and renders an independently committed 836×720 map-widget
  surface `4903`.
- Captured the first visible authentic navigation-map pixels in run
  `1792908755653936000`: roads, buildings, water and the vehicle marker are
  visible at native 836×720 inside a 1920×720 compositor frame. PNG SHA-256:
  `88e8403d808b6936181465ee512aa9e124b75ccc7dbd625a221e41e75ab8b4cb`.
- Added exact-configuration VM helper
  `tools/uk_fw/guest/ivi_link_navi_widget.S`, which reconstructs the missing
  IVI relationship `3000 -> 4903`, restores the child's native destination,
  and foregrounds the parent. This helper is not recovered firmware.
- Preserved controls showing that skin data alone still produced the prior
  nearly black frame, a parent/child relationship without child layout reduced
  it to 1×1, and hiding/promoting the child full-screen produced a stretched
  but visible map. This isolates the composition issue from map rendering.
- The milestone remains VM-adapted: it uses an exact-build zero-MSAA AppNavi
  compatibility copy and a one-method `NotifyValetStatus` D-Bus responder.
  Unmodified AppNavi and the full `ApplicationManager` chain are not claimed.
- The full chain remains blocked on missing `MICOMSTATUSMESSAGE`
  shared-memory/semaphore state. Missing landmark/DEM/sqlite resources remain
  logged, although they do not prevent the first map frame. Binding the
  recovered new2.0 HMC asset tree removed all 15 named PNG-load failures but
  left the compositor screenshot byte-identical, ruling those files out as the
  current cause of the black parent region.
- Reviewed the native TE2 decryptor implementation: 28 focused tests and all
  165 repository tests pass. A real official EU `.lge.upgrade.xml` decryption
  is byte-identical to the independently preserved recovered output.


## 0.62.0 - public VM source and evidence publication

- Added authored guest helpers, VM experiment scripts, bounded navigation
  evidence, inspected screenshots, and provenance manifests to the separate
  public repository. Generated disk images, recovered vendor binaries, raw
  captures and core dumps remain local.
- Extended the public privacy scanner to cover every tracked folder,
  including VM source scripts and QML; retained the full local test suite.
