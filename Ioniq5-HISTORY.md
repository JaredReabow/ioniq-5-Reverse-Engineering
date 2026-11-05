# IONIQ 5 research history

This file is append-only. It records the IONIQ 5 research programme only.
The root `HISTORY.md` and `CHANGELOG.md` belong to the parallel Kona programme
and are not modified by IONIQ work.

## 2026-10-19 — project-directory consolidation

- Moved the complete IONIQ-owned project tree into `ioniq research/`, including
  the dedicated plan, ledger, history, changelog, evidence, Council review
  packages, test harness and analysis tools.
- Kept the IONIQ directory internally self-contained: paths such as
  `evidence/**`, `council/**`, `tests/**` and `tools/**` remain relative to the
  IONIQ project root.
- Preserved the separate Kona workspace, root `README.md`, root `HISTORY.md`
  and root `CHANGELOG.md` without modification.

## 2026-10-18

- Established the confidential IONIQ 5 research scope for the owner's 2021
  Australian NE1 in Daybreak Blue.
- Recorded the rule that vehicle research covers architecture, interfaces,
  evidence, and risk, while operational theft or live-intrusion procedures are
  outside scope.
- Accepted T1: the published Australian family is Standard Gen5W, model
  `NEAE.S5BLN.AAU`, with software `NE_E.AUS.S5W_L.001.001.260319` and map
  `AUS.19.41.47.011.611.0`. The installed build on the car remains unread.
- Catalogued the public method landscape as T3, separating Android `S5W_M`
  from Linux `S5W_L` and recording that many public recovery claims are author
  statements rather than proven restores.
- Accepted T4: the passive-to-bench route map, including owner-visible
  readback, official media metadata, dealer documentation, spare-unit work, and
  the separation of physical restoration from persistent software state.
- Accepted T5: the NE1 trust-zone and subsystem map, including the smart key,
  immobilizer, body controller, gateway, diagnostics, telematics, ADAS, chassis,
  VCU, BMS/HV, HVAC, camera/audio, and network domains.

## 2026-10-19
- Repaired and ran the official Hyundai Navigation Updater on macOS, moved an
  off-screen updater window back onto the primary display, and downloaded the
  official Australian 2021-23 IONIQ 5 package for read-only inspection.
- Confirmed the package identity: 36 files, 9,514,830,930 bytes, 35 manifest
  payload records, all sizes and IEEE/zlib CRC-32 values matching, a verified
  Australian map, two verified voice-resource MD5 values, and both front-key
  CRC-32/MPEG-2 values matching. The sorted-tree SHA-256 is
  `bc3013e5fc1499612cec76777aa736e0973a0b8a337c6619aace9af5a4d9652a`.
- Recorded that nineteen package files are high-entropy opaque envelopes, that
  six `*_sub` files are plaintext x86-64 Linux 4.1.27 IPK containers, and that
  no decryption, USB write, or vehicle action occurred.
- Accepted T2 after an independent review reproduced the inventory, digest,
  manifest records, MD5 values, and archive format checks.
- Accepted T7: `hmg_nemesis` is a real Android/TCC803x root path but is not an
  applicable method for this Linux `S5W_L` family; its Gate 4 and recovery
  limitations are transferable, its operational mechanism is not.
- Accepted the Council generation 10 review of frozen batch 8, fingerprint
  `9c410e07d2a130c967ac567f5e32788731c909ca2e2c684fc856fc8c3080198b`, with
  Astra, a labelled DeepSeek V4.1 Flash Grok replacement, and a labelled
  DeepSeek V4 Flash Vision Fable replacement all returning COMPLETE.
- Completed the T6 integration draft: `Ioniq5-research-plan.md` traces R1-R11
  to accepted evidence, covers every named vehicle subsystem, defines Phases
  0-8 with exit criteria, closes the T6 portion of ASTRA-G7-S01 through a
  four-part Gate 4 conjunction, and separates physical restoration from
  persistent software-state coverage.
- Added dedicated IONIQ history and changelog documents plus a root
  `.gitignore` that excludes firmware, package and extraction trees, dumps,
  captures, credentials, identifiers, and personal-data workspaces while
  retaining text evidence.
- Recorded that no live vehicle entry, diagnostic session, USB write, firmware
  flash, or actuation was performed. T6 review, staged-content verification,
  commit, and push to the private `Ioniq-5` repository remain coordinator
  actions.
- Revised the private-repository retention policy at the owner's request:
  firmware, extracted analysis trees, captures, device-specific dumps, vehicle
  identifiers, and analysis workspaces may now be deliberately committed. The
  downloaded 9.5 GB official package tree and live credentials/private keys
  remain excluded, and Kona-owned paths remain outside Ioniq commits.
- Corrected the active vehicle scope to the owner's UK-origin 2021 IONIQ 5 and
  selected the official European Standard Gen5W package
  `NE_E.EUR.S5W_L.001.001.260128`; retained the Australian package as comparison
  evidence rather than rewriting the earlier accepted record.
- Verified all 17 completed European payloads against their manifest CRC-32
  values and recorded the interrupted map-download state without deleting the
  11 GB cache.
- Repaired, ad-hoc signed and registered an isolated Navigation Updater copy,
  resumed the existing European cache through LaunchServices, and observed it
  rewrite interrupted segments and advance through new parts beyond `.z964`.
- Recovered all 64,923 kallsyms entries from the exact European x86-64 Linux
  4.1.27 kernel. Applied 25,068 names in Ghidra and decompiled 48 priority
  security functions, including the LG keystore and OEM-signature chain.
- Assessed published Gen5W root/application-loading methods against build
  `260128`. No public stock-to-root path is presently confirmed; published
  persistence, decryption and SSH components require prior execution.
- Added the interim EU/AUS byte comparison and region-transition gates. The
  Australian package is not established as a safe cross-region install.
- Completed the official European package: all 35 payload sizes and signed
  CRC-32 values match, the map and both voice MD5 sidecars match, and the
  36-file SHA-256 inventory digest is
  `f06752ea7cbf296ef7d7d7482f5ba96a3349161fc7ad0d60b36b042f62ef5b51`.
- Completed the EU/AUS file matrix: six of 32 common paths are byte-identical,
  nineteen are equal-size but byte-different, seven differ in size and bytes,
  and four paths are region-specific to each package.
- Confirmed that corresponding EU and AUS boot targets use the same x86-64
  Linux 4.1.27 kernel configuration but different kernel and signed-container
  bytes and different January/March 2026 build dates.
- Added a defensive custom-firmware and privileged-access feasibility report.
  It documents prerequisites, trust boundaries, published-method applicability
  and candidate audit surfaces without implementing an exploit, bypass,
  modified image, flash procedure or live vehicle action.

### (other lineage, same date)

- Repaired and ran the official Hyundai Navigation Updater on macOS, moved an
  off-screen updater window back onto the primary display, and downloaded the
  official Australian 2021-23 IONIQ 5 package for read-only inspection.
- Confirmed the package identity: 36 files, 9,514,830,930 bytes, 35 manifest
  payload records, all sizes and IEEE/zlib CRC-32 values matching, a verified
  Australian map, two verified voice-resource MD5 values, and both front-key
  CRC-32/MPEG-2 values matching. The sorted-tree SHA-256 is
  `bc3013e5fc1499612cec76777aa736e0973a0b8a337c6619aace9af5a4d9652a`.
- Recorded that nineteen package files are high-entropy opaque envelopes, that
  six `*_sub` files are plaintext x86-64 Linux 4.1.27 IPK containers, and that
  no decryption, USB write, or vehicle action occurred.
- Accepted T2 after an independent review reproduced the inventory, digest,
  manifest records, MD5 values, and archive format checks.
- Accepted T7: `hmg_nemesis` is a real Android/TCC803x root path but is not an
  applicable method for this Linux `S5W_L` family; its Gate 4 and recovery
  limitations are transferable, its operational mechanism is not.
- Accepted the Council generation 10 review of frozen batch 8, fingerprint
  `9c410e07d2a130c967ac567f5e32788731c909ca2e2c684fc856fc8c3080198b`, with
  Astra, a labelled DeepSeek V4.1 Flash Grok replacement, and a labelled
  DeepSeek V4 Flash Vision Fable replacement all returning COMPLETE.
- Completed the T6 integration draft: `Ioniq5-research-plan.md` traces R1-R11
  to accepted evidence, covers every named vehicle subsystem, defines Phases
  0-8 with exit criteria, closes the T6 portion of ASTRA-G7-S01 through a
  four-part Gate 4 conjunction, and separates physical restoration from
  persistent software-state coverage.
- Added dedicated IONIQ history and changelog documents plus a root
  `.gitignore` that excludes firmware, package and extraction trees, dumps,
  captures, credentials, identifiers, and personal-data workspaces while
  retaining text evidence.
- Recorded that no live vehicle entry, diagnostic session, USB write, firmware
  flash, or actuation was performed. T6 review, staged-content verification,
  commit, and push to the private `Ioniq-5` repository remain coordinator
  actions.
- Revised the private-repository retention policy at the owner's request:
  firmware, extracted analysis trees, captures, device-specific dumps, vehicle
  identifiers, and analysis workspaces may now be deliberately committed. The
  downloaded 9.5 GB official package tree and live credentials/private keys
  remain excluded, and Kona-owned paths remain outside Ioniq commits.
- Corrected the active vehicle scope to the owner's UK-origin 2021 IONIQ 5 and
  selected the official European Standard Gen5W package
  `NE_E.EUR.S5W_L.001.001.260128`; retained the Australian package as comparison
  evidence rather than rewriting the earlier accepted record.
- Verified all 17 completed European payloads against their manifest CRC-32
  values and recorded the interrupted map-download state without deleting the
  11 GB cache.
- Repaired, ad-hoc signed and registered an isolated Navigation Updater copy,
  resumed the existing European cache through LaunchServices, and observed it
  rewrite interrupted segments and advance through new parts beyond `.z964`.
- Recovered all 64,923 kallsyms entries from the exact European x86-64 Linux
  4.1.27 kernel. Applied 25,068 names in Ghidra and decompiled 48 priority
  security functions, including the LG keystore and OEM-signature chain.
- Assessed published Gen5W root/application-loading methods against build
  `260128`. No public stock-to-root path is presently confirmed; published
  persistence, decryption and SSH components require prior execution.
- Added the interim EU/AUS byte comparison and region-transition gates. The
  Australian package is not established as a safe cross-region install.
- Completed the official European package: all 35 payload sizes and signed
  CRC-32 values match, the map and both voice MD5 sidecars match, and the
  36-file SHA-256 inventory digest is
  `f06752ea7cbf296ef7d7d7482f5ba96a3349161fc7ad0d60b36b042f62ef5b51`.
- Completed the EU/AUS file matrix: six of 32 common paths are byte-identical,
  nineteen are equal-size but byte-different, seven differ in size and bytes,
  and four paths are region-specific to each package.
- Confirmed that corresponding EU and AUS boot targets use the same x86-64
  Linux 4.1.27 kernel configuration but different kernel and signed-container
  bytes and different January/March 2026 build dates.
- Added a defensive custom-firmware and privileged-access feasibility report.
  It documents prerequisites, trust boundaries, published-method applicability
  and candidate audit surfaces without implementing an exploit, bypass,
  modified image, flash procedure or live vehicle action.

- 2026-10-28: Prepared a public-safe snapshot by removing the owner USB exports and upstream raw diagnostic dump from reachable Git history, anonymizing local user paths, and retaining only sanitized firmware findings. Publication remains gated on GitHub server-side cleanup of previously cached raw commits.

- 2026-10-28: Prepared an independent public repository from that sanitized
  snapshot with a fresh Git history. The earlier private repository and its
  unresolved historical objects remain separate. The public push is subject
  to the public privacy and Git-scope harness.

## VM continuation history imported from the private working tree

## 2026-10-26 — retrospective backfill and continuation contract

This entry is appended on 2026-10-26. The existing history through 2026-10-19
is preserved byte-for-byte. Dates below describe recorded milestones, not new
runs performed during this backfill. Sources are the existing changelog,
HANDOVER.md, Git history and named evidence; historical errors remain in place
and are superseded by corrections rather than silently rewritten.

### Backfill: 2026-10-20–21 — vendor-kernel VM and bounded recovery

- Consolidated the project as its own Git root. Git commits through `852c168`
  record boot-parameter research, VM boot and graphics harness work.
- Recovered the `ABL.` parameter collection mechanism and synthetic manifest/
  seed initialization. Later evidence corrected the earlier anti-tamper-panic
  attribution: the observed fatal failure was root mounting, not proof of a
  security bypass. Synthetic inputs are not recovered device keys.
- Reached interactive userspace with an exact-build guest-RAM SDHCI PCI-table
  adaptation and compatible ext4 root. Kept boot-image files unchanged and
  classified this as a VM-adapted vendor kernel, not stock-device boot.
- Demonstrated keyboard/pixel-verified direct-QEMU-VGA diagnostics, explicitly
  not vendor HMI or a DRM/EGL backend.
- Retained bounded negative RSA/updater-constant recovery experiments without
  claiming that all offline recovery was impossible. Corrections C12–C14 and
  changelog 0.40.0 supersede the categorical older ceiling claims.
- Sources: `evidence/vendor-kernel-vm.md`, `evidence/vendor-kernel-graphics.md`,
  `evidence/local-ui-recovery.md`, `evidence/corrections-log.md`.

### Backfill: recorded 2026-10-22 continuation — module and envelope work

- Existing local notes record envelope-format refinements and unsigned module
  initialization in QEMU against the vendor kernel. This requires privileged
  module loading; it does not establish an unprivileged or remote entry path.
- Source: `work/ui-recovery/SUMMARY-and-runbook.md` and
  `work/ui-recovery/SECURITY-FINDING-module-load.md`. Their contemporaneous
  claims that userspace recovery was device-gated are superseded below.

### Backfill: 2026-10-25 — recovered authentic userspace and visible map

- Native TE2/xcrypt decryption recovered EU/AU payload userspaces. Existing
  review records 28 focused decryptor tests, 165 repository tests, and a real
  EU descriptor output matching independently preserved recovered bytes.
- Recovered Weston/IVI plus project-local Mesa rendered authentic Home; bounded
  EU map/core/skin resources allowed AppNavi engine initialization and genuine
  836×720 map-widget pixels. The IVI hierarchy helper and zero-MSAA adaptation
  remain explicitly VM infrastructure, not stock behavior.
- Source: changelog 0.41.0 and the visible-navigation milestone at
  `work/vm/vendor-userspace-260128/ivi-link-navi-widget-build/visible-navigation-milestone.json`.

### Backfill: 2026-10-26 — launcher, Confirm and Navigation integration

- Fixed the duplicated `ivi:ivi` environment and added isolated micom serial
  transport. Reconstructed an exact 35-byte `AskSysBootinfo` reply and a
  fail-closed simulator; data-bearing CAN simulation remains incomplete.
- Authentic Confirm dispatch succeeded with two-thread llvmpipe: standby
  status 12, agreement true, cleared filters, authentic Home show/response,
  current/drawing Home 11, and visible composition. A bounded manager pause
  avoids a slow-TCG false liveness kill; no successful reply or pixels are
  fabricated. Immediate transition value 255 alone is not a rejection verdict.
- AppLauncher-owned, signature-checked AppNavi reached engine/EGL success and
  surfaces 3000/4903 through a targeted preload. A guarded PIE-aware in-memory
  startup deadline adaptation ruled out the original 22,999 ms timeout as the
  sole cause of incomplete Navigation transition. The signed file stayed intact.
- Latest recorded launch notification remains status 5/window 0. Manager state
  is `11/11 → 35/11 → 11/11`; full Home↔Navigation is not demonstrated.
- Sources: changelog 0.42.0–0.45.0, current HANDOVER top sections, correction C15.
  Latest complete archive SHA-256:
  `a0e2100ca5a0eb72426db6179c88a27e34abe5928d8a364ce9f14d0e9bfd52b8`.
  Recorded rootfs SHA-256:
  `4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f`.
  These are inherited evidence identities, not newly rehashed VM artifacts.

### Current continuation setup

- Owner reaffirmed the goal: authentic full-system VM operation with simulated
  adapters, drivers and OS support, plus editable changelog, append-only history,
  and a separate vulnerability document for patching.
- Added `Ioniq5-VULNERABILITIES.md` from existing security research, with explicit
  verification levels, remediation and acceptance criteria. No new vulnerability
  experiment or live-device validation was performed.
- Added `PROJECT-OPERATIONS.md`, documenting current milestones, exact next
  Navigation contract investigation, same-chat-only continuation and proposed
  scheduled instruction. Interval and active-work behavior await confirmation;
  no scheduled task was created during this setup.
- Routing doctor using Python 3.13 reports the installed DeepSeek Flash role as
  statically ready, runtime unverified. Current tools provide child threads but
  no native role-selectable worker interface. No threads were created, no
  workers invoked, and no router/model settings changed. Security restrictions
  will not be evaded through model switching.
- Preserved all pre-existing dirty/untracked source and research work. No image
  mutations, VM runs, commits, pushes, physical-device actions or flashes.

### Continuation-setup validation

- All 168 repository unit tests pass using the documented test interpreter.
- `git diff --check` passes. The original 6,819-byte history prefix was verified
  unchanged (SHA-256 `f15420373116d5c314ea9e88c4fc6ac96a813652f75121ab21ca7b478d1e508a`).
- Test output: `work/test-tmp/continuation-setup-unittest.log`. No VM feature
  acceptance or Council acceptance is implied by these checks.

## 2026-10-26 - existing scheduled-task continuation request

- Owner requested retaining the existing recurring task and no new chat threads.
- Listing showed task `206efda3-54ed-456c-a4f5-07b272247cc9` (keep going) active;
  the named IONIQ check-in and heartbeat tasks were paused.
- Updates with explicit same-chat-only instructions were rejected by scheduler
  validation (workspace target, then interval-incompatible time/timezone fields).
  No successful update, replacement task, or thread creation is claimed.
- Original cadence was not exposed by listing. The attempted 30-minute setting
  was rejected and is not evidence of the original cadence. Stopped retries;
  scheduler API repair or UI editing is needed. No pause/delete was performed.

## 2026-10-26 - bounded Navigation notification review

- Reviewed existing saved SendToAppLauncherNaviLaunchedToExcute disassembly.
  The function constructs a QVariant from literal 5 at 0x2c08e31, appends it to
  a signal and sends it after an initial one-shot flag gate. It does not select
  this value from engine state in the reviewed normal flow. Enum semantics and
  exact message strings remain unresolved; this is not proof of success.
- Added evidence/navigation-launch-status-contract.md and updated handover and
  editable changelog. Next resolve message identities and manager receiver/window
  producer. No guest execution, image mutation, thread creation, or new security
  finding occurred. git diff --check passes; prior 168-test result is not a new run.

## 2026-10-26 - exact AppNavi notification identities

- Read-only ELF section mapping resolved seven strings from original AppNavi,
  SHA-256 62d6e0b3119b99b3fe322ec3bbe03366e9f71ed40dc18b0323d2a9da0e7fa1a3.
- Saved code first calls launcher /Inform launched(30), then emits
  /navigation_map com.lge.hkmc.avn.appnavi.naviboot.SendNaviBootFail(5).
  Process registration and boot notification are distinct messages. Enum meaning,
  selected caller path and manager window-state producer remain unresolved.
- Retained raw address/offset/string mapping in the project-local notification
  JSON and updated evidence/navigation-launch-status-contract.md, handover and
  changelog. Located original ApplicationManager for subsequent receiver analysis.
- Mapping JSON parsed and seven entries checked; git diff --check passes.
  No guest execution, image change, new threads or new vulnerability claims.

## 2026-10-26 - ApplicationManager receiver triage

- Mapped SendNaviBootFail, notifyNaviLaunched and the boot interface strings in
  original ApplicationManager (SHA-256
  5d71539f61a3982b8aac6132a2de14c083fa9ac129792bae750a526ebd771cbc).
  Six literal matches retained in manager-notification-string-locations.json;
  they are not function addresses or proof of receiver behavior.
- No matching handler names exposed by ordinary/dynamic symbol inspection.
  REA reports Ghidra unconfigured, Hopper absent and IDA unconfigured. No installs
  or configuration changes made. Existing LLVM/Qt metadata remains a viable path.
- Updated Navigation evidence note and changelog. No guest execution, VM mutation,
  new thread, scheduler change or new vulnerability claim. git diff --check passes.

## 2026-10-26 - recovered Navigation window notification gate

- Original ApplicationManager LLVM disassembly establishes a Qt subscription
  using slot string 1notifyNaviLaunched(int). Diagnostic routine at 0x287e70
  reads window from receiver byte +0x20, caches incoming status at +0x1c and
  gates downstream dispatch when the byte is zero.
- Adjacent routine at 0x288070 logs vendor naviWindoeCreate, stores the incoming
  byte at +0x20 and invokes status handling with the cached status. Direct caller
  0x19108d is the next producer to trace. This is static control-flow evidence,
  not proof of successful VM transition or complete enum recovery.
- Retained original-binary disassembly and bounded extracts, updated Navigation
  evidence, changelog and handover. No synthetic success, flag patch, guest run,
  image mutation, new thread or new vulnerability claim. diff whitespace check
  passes; no fresh full-suite execution was needed for these research notes.

## 2026-10-26 - window-create producer narrowed

- Traced caller 0x19108d into routine 0x190c70, identified by exact diagnostic
  slotNotifyBGInfo surface_id/display/app_id. Display/string helper success,
  nonzero global 0x5c5028 and case-sensitive AppNavi containment precede the
  window-created notification; the global is cleared after notification.
- Global initialization, matching helper semantics and upstream caller 0x2d6611
  remain to be traced. A host-log-only negative search does not establish absent
  guest callbacks. Updated bounded Navigation evidence and editable changelog.
- No target execution, image mutation, forced state, new threads or security
  findings. git diff --check passes.

## 2026-10-26 - correlated FG/BG notification mismatch

- Recovered display-record selection and exact QString app-list equality.
  Pending gate 0x5c5028 initializes to 0xffffffff, not zero; no claim that an
  initially zero gate explains the missing notification remains supported.
- Scanned all 123,763 lines of retained latest DLT log, SHA-256
  02fa2f7268f574184745739afaa8a3e5e4db61c3b7093f70991e9e93d7a0d972.
  AppNavi surface 3000 produces FG info and manager slotNotifyFGInfo before
  status 5/window 0. Zero BG-info/window-created-latch diagnostic matches in
  that file; lossless collection is not established by the search.
- Recorded parent dimensions 1926x753 without attributing causality; harness
  already disables Qt window decorations. Next trace compositor FG/BG decision.
- Retained hashed correlation JSON and matcher disassembly; updated evidence,
  handover and editable changelog. No VM run, mutation, new threads or new
  vulnerability. git diff --check passes.

## 2026-10-26 - compositor notification classification recovered

- Original recovered compositor module copies match SHA-256
  e1ce4d479f1fb84cc44d2faebad748206bdf3003b48a9ccf90e76da17a553bd0.
  Local callback 0xf8e0 selects FG for any positive width or height, BG only
  when both are non-positive. It does not test exact screen resolution.
- This refines the geometry hypothesis: correcting 1926x753 to 1920x720 would
  not alter this notification selection. Next inspect initial zero-size
  configure lifecycle and verify the guest loaded the same module bytes.
- Saved disassembly, updated Navigation evidence, handover and changelog.
  No fabricated BG event, property change, VM run, new thread or vulnerability
  claim. git diff --check passes.

## 2026-10-26 - current-image compositor provenance and host timeout

- Read-only debugfs extraction of both current-image compositor paths matches
  original SHA-256 e1ce4d479f1fb84cc44d2faebad748206bdf3003b48a9ccf90e76da17a553bd0.
  Latest retained Weston log records loading the /usr/lib/weston path. This is
  current-image/path corroboration, not a historical in-memory digest.
- Subsequent shell-module disassembly and a follow-up command each timed out
  at 15 seconds. Their completion is unverified; any output may be partial.
  Stop retries and check host/process responsiveness before more analysis or VM runs.
- Existing keep-going task again listed active; prompt update again rejected
  by interval/time-field validation. No successful schedule change is claimed.
- Updated Navigation evidence and history. No guest execution, image mutation,
  new threads or vulnerability discovery. No new test result is claimed.

## 2026-10-27 - host recovery and shell configure semantics

- Host shell responsive; process snapshot found no matching QEMU or LLVM worker.
  Fresh bounded shell disassembly completed, superseding the outstanding timeout
  blocker without claiming that the original timed-out commands completed.
- Current image IVI shell extracted read-only and matches original SHA-256
  8b57db4baa1f35a1a08cffc6de221101a92b37528123d7250c774db03a3b7697.
- Original create routine initializes size cache to 0/0; configure returns when
  both dimensions match. An initial zero-size surface does not itself produce
  a layout configure/BG event through this path. The previous initial-zero
  hypothesis is narrowed, not accepted as root cause.
- Next compare retained positive BG events against AppNavi hide/unmap/buffer
  lifecycle. Updated evidence, handover and editable changelog. No VM execution,
  image mutation, new threads or security findings. git diff --check passes.

## 2026-10-27 - revised orchestration ceiling and Fable route check

- Owner raised DeepSeek worker ceiling from 20 to 30 and requested Astra/Fable
  planning, decisions, guidance and review, with nonduplicated efficient tasks.
- Updated operations contract and prompt draft. Existing no-new-chat-thread rule
  remains; native role-selectable delegation is not exposed in this session.
- Read-only Fable doctor failed: exact openrouter/claude-fable-5.1 route exists
  but is not advertised as native-subagent v2. No config changes, paid tests,
  worker launches or substituted model claims. Actual requested orchestration
  remains blocked pending host/tool routing support.

## 2026-10-27 - positive retained BG controls

- Older retained Camera/Standby logs show initial 1926x753 FG configure followed
  by zero-size configure, BG emission and manager BG receipt. Thirteen selected
  events retained with log digest and line provenance in navigation-contract-audit/
  positive-bg-event-control.json. Different-run control, not an AppNavi fix.
- This demonstrates a working earlier VM BG path. Next focus on AppNavi's
  onVisibleChanged(0), buffer detach/commit and zero-size configure lifecycle.
- Latest repeated owner message specifies up to 20 workers; operations ceiling
  adjusted accordingly while preserving the earlier 30-worker request in history.
  No workers launched, VM mutations, new threads or vulnerability claims.

## 2026-10-27 - AppNavi visibility versus unmapping distinction

- Bounded original-binary analysis shows onVisibleChanged(false) updates the
  first-hide flag, may call the one-shot boot notifier and calls clearScreen.
  The inspected clearScreen path clears and swaps renderer buffers; it does
  not prove a null Wayland attach or parent Qt-window hide. Virtual downstream
  implementations remain unresolved, not asserted absent.
- Retained logs corroborate callback execution. Next identify its source and
  parent-window hide path separately from native-map rendering operations.
- Updated evidence and editable changelog; appended this history entry. No VM
  run, image change, new thread or new vulnerability. git diff --check passes.

## 2026-10-27 - authentic Qt hide path located

- Located QWindow::hide at 0x3362275 in AppNavi onForeground, gated by base
  foreground handling and screen-specific control flow. Retained symbols and
  bounded create/foreground/base listings. This is distinct from renderer clear.
- Latest PID-908 foreground log scan exposes widget screens 6/9/10, not a
  matching primary-screen hide diagnostic; coverage does not prove invocation
  absence. Next trace constructor signal connection and primary foreground
  requests/deduplication, then actual Wayland null-buffer evidence.
- Updated Navigation note and editable changelog; no VM run, image edits,
  new threads or vulnerability claim. git diff --check passes.

## 2026-10-27 - Qt signal wiring and conditional Wayland detach

- Constructor strings/control flow confirm same-object visibleChanged(bool)
  connection to onVisibleChanged(bool), refining earlier signal-source uncertainty.
- Recovered QtWayland setVisible(false) explicitly attaches null/commits only
  when virtual slot +0x60 returns zero. Recovered EGL plugin inherits the handler
  and its slot implementation returns one, skipping that branch. Retained exact
  library identity, disassembly and plugin relocations in Navigation evidence.
- Actual guest byte identity/backend/instance remains to verify; no sole-root-
  cause or runtime fix claim. Next observe the authentic hide path and explain
  older positive BG controls before implementing a scoped compatibility adapter.
- Updated evidence, handover and editable changelog. No VM run, image changes,
  new threads or vulnerability claims. git diff --check passes.

## 2026-10-27 - current-image QtWayland identities verified

- Read-only extraction confirms current QtWayland client/EGL plugin match the
  recovered originals analyzed in the hide-path investigation. Digests and
  retained copies recorded in Navigation evidence.
- Runtime selected backend remains unknown: saved launcher log lacks explicit
  load identity, no AppNavi process-map snapshot found in inspected evidence,
  and alternate library directories precede /usr/lib. Do not equate image file
  identity with actual loaded objects.
- Next bounded run should capture mapped identities and actual hide/Wayland
  behavior observationally before changing it. No VM execution, image mutation,
  new thread or vulnerability. Updated evidence/changelog; git diff --check passes.

## 2026-10-27 - completed observational backend VM experiment

- Ran observation-only wrapper (SHA-256
  4ddf1fee3a7fcb5b3fc8b0873ab0d5dac625ccfacf45a973bfab6947df279880)
  around unchanged baseline runner; QEMU no-NIC/snapshot, 1536 MiB, host bound
  900 seconds. Harness completed in 404.87 seconds, command exit 0, no timeout.
- Collected 26 AppNavi maps snapshots and strictly allowlisted environment.
  Actual mapped QtWayland client and EGL plugin match analyzed originals.
  AppNavi environment has QT_WAYLAND_DISABLE_WINDOWDECORATION=1:1 and decoration
  plugin is mapped; parser effect remains to verify.
- Inspected authentic visible Home before Navigation. Manager sequence again
  11/11 -> 35/11 -> 11/11 with FG delivery and status 5/window 0. Final return
  screenshot inspected black, not accepted as restored Home despite manager state.
- No raw Wayland request trace in inspected logs despite WAYLAND_DEBUG=1; actual
  null-attach path remains unobserved. Late Camera/Radio crash messages retained
  without unsupported cause or vulnerability attribution.
- Complete archive SHA-256
  6019ec6e42cacce8a41fdc79c7dd9705487efdc0a53b741313e6b5b7aad01d84;
  serial-announced digest matches decoded bytes; extracted with safe data filter.
  Host log SHA-256
  2e961f8277683f21d40172b9e6c34816c04c28893519c4f1ccb3a82417464085.
- Rehashed base rootfs unchanged at
  4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f.
  All 168 repository tests pass; shell syntax and git diff --check pass. Updated
  evidence, handover and editable changelog. No new threads, image writes,
  synthetic state/callbacks, commits or new vulnerability claims.

## 2026-10-27 - decoration-disable scalar parser identified

- QtWayland supportsWindowDecoration reads the decoration-disable variable via
  QByteArray::toInt(nullptr,10), caches nonzero as disabled. Retained bounded
  original-binary disassembly. The observed 1:1 is not a supported scalar form;
  expected invalid-to-zero result remains inference until exact-library execution.
- Proposed future control: avoid pre-setting a scalar AppLauncher appends, verify
  child value exactly 1 before first Qt initialization. No setting changed; do
  not equate decoration correction with solving the separate BG/hide contract.
- Updated evidence/changelog and appended history. No VM run, image mutation,
  new threads or vulnerability claims. git diff --check passes.

## 2026-10-27 - negative decoration-unset environment control

- Verified baseline runner digest, changed only the pre-set decoration export
  to unset, transferred control/observer into snapshot guest /tmp. Same prior
  compatibility behavior otherwise; no base image injection.
- Harness completed command exit 0/no timeout in 474.71 seconds, but feature
  result failed: repeated Camera/Standby crashes, no authentic agreement, no
  AppNavi snapshots, manager 0/0 and all screenshots splash. Do not adopt this
  change or call it a Navigation fix. Early-client environment/crash context was
  not captured by the AppNavi-specific observer.
- Complete archive SHA-256
  648b5d30c169b2e4adaa2e8cf069742fd5b3d779b0ef1d6d7e63fead7f6910e9;
  digest independently matches serial announcement; safe extraction completed.
  Host-log SHA-256
  9df711936074c3be7b129b8c80b55f1a8a9f102e910d35c4e1c15228499162dc.
- Exact source delta and semantic summary retained. Base image independently
  rehashed unchanged at
  4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f.
  Original working baseline preserved; no automatic retry. Next use an early-
  client-focused control, not the whole sequence, for the environment failure.
- Updated handover/evidence/changelog; no new threads, commits or vulnerability
  claim. Shell syntax and git diff --check pass; prior 168-test result retained,
  not presented as a fresh test run for this shell-only experiment.

## 2026-10-27 - bounded crash-site analysis

- Recovered libc offset 0x128dde decodes to vmovntdq ymm0,(r9), a vector store
  in bulk-copy-style code. Retained exact libc digest and bounded disassembly.
  Memory-write fault is not SIGILL; caller/length/register context unresolved.
  No unsupported-AVX, QEMU-defect or vendor-vulnerability conclusion follows.
- Canonical piefix and both new run command manifests share max/GenuineIntel
  CPU and 1536 MiB. Older no-AVX2 runs are separate controls, not this baseline.
- Updated evidence/changelog; no new VM run, image change or thread. Next use
  short early-client crash observation rather than repeat the failed full flow.
  git diff --check passes.

## Delegation correction - recorded after the 2026-10-27 checkpoint

- Earlier explanations that no inline model-selectable worker tool was exposed
  were wrong: spawn_worker is exposed and does not create a chat thread.
- Dispatched one bounded read-only early-crash investigation requesting exact
  configured deepseek/deepseek-v4.1-flash, high reasoning. Host tool returned
  store.runWorkerToolResult is not a function. No worker findings, completion
  or inference routing metadata were obtained; underlying execution is unknown.
- Stopped rather than duplicate the dispatch, switch routes or create a child
  thread. Actual blocker is host worker integration, not the no-new-thread rule.
- Corrected operations, handover and editable changelog while preserving this
  history's older entries. No new VM action, image edit or vulnerability claim.

## Crash-capture planning follow-up

- Recovered guest inventory has strace but no gdb/gdbserver found. Vendor kernel
  configuration enables ELF core dumping and procfs. Planned a short snapshot-
  only early-client core-note capture rather than writing/installing a debugger.
- Bounded/header-only core filtering can capture registers/signal/map notes but
  not a reliable stack backtrace; output completeness needs validation. No procfs
  setting changed and no new experiment launched. Updated evidence/changelog;
  no new threads, image mutation or vulnerability claim. git diff --check passes.

## Supplied community-chat evidence reconciliation

- Owner supplied a summary of #general-g5w-linux and #userful-resources-linux,
  including AppNavi replacement/menu removal, tentative CV_E 220721 recollection,
  unsuccessful updater attempt/signature checks, xcrypt and downloader reports.
  Recorded in evidence/community-chat-leads.md without claiming channel access,
  repository reinspection, raw-message provenance or hardware validation.
- Kept CV_E distinct from NE_E and decryption distinct from authenticated update
  acceptance. Historical downloads remain model/region/time dependent. No new
  current-build entry, downgrade or vulnerability was established.
- Added warnings to three older notes to prevent stale plaintext/device-key/API
  conclusions from being reused as VM blockers. Current native recovery already
  supplies userspace. Linked unvalidated updater-attempt provenance to V-005 and
  updated handover/changelog. No external fetch, VM execution, image change,
  new thread, firmware installation or disclosure occurred.

## Focused early-client core experiment completed

- Ran snapshot-only early startup with bounded core settings, no agreement or
  Navigation sequence. Harness elapsed 44.83 seconds, command exit 0/no timeout.
  Captured one 81,920-byte AppCamera core with eight thread status notes.
- ELF64 note/program-header bounds validated. Fault SIGSEGV/SEGV_MAPERR at libc
  offset 0x128dde, R9/fault address 64 bytes below writable mapping start RDI.
  Core stack segment has no stored bytes; caller/original copy length unresolved.
  Modified in-loop RDX is not claimed as an original negative argument.
- Verified early-client decoration value exactly 1. Requested filter 0x10 read
  back 00000000; report actual coverage rather than assume filter semantics.
- Complete archive SHA-256
  10fbb21b674ab1795c5e2b52d4e04ad47611f8674c4ac5ed43d283322c24987c;
  decoded digest matches serial announcement and safe extraction completed.
  Core summary/script/run manifest retained in navigation-contract-audit.
- Rehashed base image unchanged at
  4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f.
  Updated evidence, handover and editable changelog. Shell syntax and whitespace
  checks pass; no fresh unit-suite result asserted. No new thread, image mutation
  or vendor-vulnerability claim. Next bounded fault-time stack/caller capture.

## Resumed work - bounded stack capture and EGL caller

- Added VM-only ptrace_crash_observe.c, explicit early-client path allowlist,
  bounded SEIZE-based main-thread observation, 64 stack words, bounded maps,
  original fatal signal redelivered. Cross-compiled with project Zig/musl and
  warnings-as-errors; initial type-format errors fixed before guest execution.
- Short snapshot run completed in 43.7 seconds, command exit 0/no timeout.
  Guest invalid-PID and disallowed-executable tests pass; real Camera SIGSEGV
  captured with 64 readable stack words and original signal 11 re-delivered.
  Timeout/cancellation/group-stop paths not dynamically exercised.
- Top stack return location immediately follows real memcpy call at vendor EGL
  dri2_wl_swrast_put_image2. Width-derived stride cached before buffer update,
  which can replace width; captured stride/count registers -4. Original memcpy
  entry arguments and exact initialization remain to measure, not invented.
- Qualified mixed-stack investigation I-001 added to vulnerability register,
  with stock-hardware reachability/impact explicitly unproven. Updated evidence,
  handover, operations and editable changelog. No Navigation-success claim.
- Complete archive SHA-256
  e0884a3c11582ed2b986db28f2673b7fde9297a1871f2633ad13672b2dfdeaae;
  host-log SHA-256
  45b07d1dd3f87b00cb306e1d56f3253beccbb819eea239df105b7a887daab86a.
  Digest verification and safe extraction pass. All 168 repository tests pass.
  Base image independently rehashed unchanged at
  4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f.
- No new chat threads, image writes or commits. Delegated host tool remains
  blocked; no independent Astra/Fable/DeepSeek review is claimed. Next bounded
  update-time geometry and copy-entry observation before adapter changes.


## 2026-10-27 — Parallelism and Council plan review

- Activated the requested Parallelism and three-seat Council workflow without
  creating chat threads. Astra-high planned; Astra-high and two independent
  Sol-medium reviewers completed independent and reconciliation rounds against
  the same frozen package.
- Council checker rehashed the package and returned COMPLETE for the plan only.
  Fingerprint c59ac8a0d4ece96fd8fab5fe8a6795789697c95394d6e548a02dc8484052bbb5;
  packet SHA-256
  528649b5b337fb0b76bafd6cb9b020e572851ec33136c6d0927a5c38a12ef790.
- Corrected the interpretation boundary: captured -4 does not prove original
  width -1 or that width changed during that invocation. Accepted plan requires
  raw pre/post dimensions and update state, EGL call-site arguments, and actual
  resolved copy-entry arguments with PLT/IFUNC-aware attribution.
- Council retained nonblocking downstream requirements: record vendor EGL and
  project Mesa identities together; numerical capture caps; debugger-state
  restoration; and host-owned VM termination after timeout/restoration failure.
- Attempts to dispatch EC-01/EC-02 to the catalog-suggested
  opencode/deepseek-v4.1-flash route failed because no API key is configured.
  No DeepSeek work ran, no alternate model was substituted, and the ledger marks
  both tasks blocked. No observer implementation or authentic VM run occurred.
- Latest scheduler listing showed the retained keep-going task paused. Its prompt
  update again failed because the API requires time/timezone fields while also
  rejecting those fields for an interval schedule. No active heartbeat claimed.


## 2026-10-27 — direct DeepSeek provider policy correction
- Owner clarified that all DeepSeek workers must use the direct DeepSeek API
  provider, not OpenCode. Updated Parallelism and Council skills, protocols,
  README, installation guidance and invocation metadata to require provider-
  qualified `deepseek/...` routes and fail closed instead of using OpenCode,
  OpenRouter, Codex Router or another intermediary fallback.
- Corrected the current project checkpoint: the earlier OpenCode no-key result is
  historical route probing, not the authorized worker route. The live worker
  tool previously rejected `deepseek/deepseek-v4.1-flash` as unknown. EC-01 and
  EC-02 remain blocked pending an exposed/authenticated direct DeepSeek model.
- Parallelism unit tests: 148 pass. Council unit tests: 93 pass. Both packaging
  validators reached their external validation step but failed because PyYAML is
  absent from that validator environment; no package was installed to bypass it.

### (other lineage, same date)

- Owner clarified that all DeepSeek workers must use the direct DeepSeek API
  provider, not OpenCode. Updated Parallelism and Council skills, protocols,
  README, installation guidance and invocation metadata to require provider-
  qualified `deepseek/...` routes and fail closed instead of using OpenCode,
  OpenRouter, Codex Router or another intermediary fallback.
- Corrected the current project checkpoint: the earlier OpenCode no-key result is
  historical route probing, not the authorized worker route. The live worker
  tool previously rejected `deepseek/deepseek-v4.1-flash` as unknown. EC-01 and
  EC-02 remain blocked pending an exposed/authenticated direct DeepSeek model.
- Parallelism unit tests: 148 pass. Council unit tests: 93 pass. Both packaging
  validators reached their external validation step but failed because PyYAML is
  absent from that validator environment; no package was installed to bypass it.

- 2026-10-28: Published the authored VM sources, bounded evidence and current
  technical handover in the separate public repository; local firmware images,
  extracted vendor trees, raw captures and private working records remain local.

## 2026-10-28 — VM sources, evidence and screenshots published
- Published the authored VM reproduction sources and bounded evidence under vm/,
  with source and evidence manifests binding every published file to a SHA-256.
- Added two further inspected screenshots: the authentic launcher profile/confirm
  screen and a navigation-window frame that still shows Home, which is the visible
  symptom of the unresolved Home-to-Navigation transition.
- Expanded the root README with a per-area status table (kernel boot, userspace,
  launcher, Home, AppNavi, compositing, audio, CAN/MICOM, persistence, input), the
  mandatory run configuration (TCG, max,vendor=GenuineIntel, 1536 MiB, snapshot
  disk, no NIC) and the recovered ApplicationManager/window-byte contract.
- No new experiment was run for this publication. All screenshots and evidence
  were already captured by earlier snapshot runs; the base rootfs hash is unchanged.

## 2026-10-28 — unverified physical-access vectors recorded
- Received a third-party advisor summary asserting three physical-access vectors:
  USB descriptor strings reaching a privileged mount script; media file parsing
  running as root; and a root serial console gated by a hashed password.
- No logs, script excerpts, device identity, process identity, console device or
  reproduction accompanied the claims. None was validated against the recovered
  image in this session. Recorded as V-006, V-007 and V-008 with explicit
  "unverified actor report" status so they are neither lost nor treated as
  established findings.
- Technical caveats recorded with each: USB string descriptors are UTF-16LE so
  ASCII metacharacters arrive NUL-interleaved, and udev sanitises ID_SERIAL /
  ID_MODEL, so a vulnerable path needs a custom consumer; the 126-code-unit
  descriptor limit would still admit a ~40 character payload, making encoding and
  quoting, not length, the binding constraint. A hashed root console password is
  ordinary practice and only becomes a finding if the hash is weak, reused,
  bypassable, or its material is extractable.
- All three require physical access and none is a remote vector. Validation is
  scoped to the isolated VM snapshot or offline analysis of the recovered rootfs.
  No experiment was run against hardware.

### (other lineage, same date)

- Received a third-party advisor summary asserting three physical-access vectors:
  USB descriptor strings reaching a privileged mount script; media file parsing
  running as root; and a root serial console gated by a hashed password.
- No logs, script excerpts, device identity, process identity, console device or
  reproduction accompanied the claims. None was validated against the recovered
  image. Recorded as V-006, V-007 and V-008 marked "unverified actor report" so
  they are neither lost nor treated as established findings.
- Caveats recorded: USB string descriptors are UTF-16LE so ASCII metacharacters
  arrive NUL-interleaved, and udev sanitises ID_SERIAL/ID_MODEL, so a vulnerable
  path needs a custom consumer; the 126-code-unit descriptor limit would still
  admit a ~40 character payload, making encoding and quoting rather than length
  the binding constraint. A hashed root console password is ordinary practice and
  only becomes a finding if weak, reused, bypassable, or its material extractable.
- All three require physical access; none is remote. Validation is scoped to the
  isolated VM snapshot or offline analysis of the recovered rootfs. No experiment
  was run against hardware and no attack tooling was built.

## 2026-10-28 — advisor claims validated offline against the recovered rootfs

- Tested the three third-party claims of 2026-10-28 against the recovered
  `260128` rootfs. None was accepted as originally stated; one was upgraded to a
  confirmed vulnerability on different mechanics.
- V-006 upgraded to a CONFIRMED static command injection (CWE-78) in
  `/app/bin/usb-automount`. `__sprintf_chk` at 0x5326 builds `"%s %s %s %s &"`
  from `ID_SERIAL_SHORT` and `system()` is called at 0x535f; `popen()` at 0x53b9
  runs `cat /proc/mounts | grep %s` with the same string. Reachable only on the
  PTP (`060101`) or vendor-specific (`ffff00`) branch; the mass-storage branch
  uses mount(2)/umount2/mkdir with no shell. The advisor's "mount script"
  mechanism was wrong.
- The usual udev mitigation does not apply: `usb_id` sanitises through
  `util_replace_whitespace` and tests only the `_ISspace` ctype bit at 0x22b72,
  so only whitespace is rewritten. The serial filter at 0x1c2df allows
  0x20-0x7f and rejects comma, which neutralises literal spaces and comma-list
  brace expansion but not parameter expansion. The advisor's literal payload
  would therefore have failed; a parameter-expansion variant would not.
- Aggravating: `/tmp` is tmpfs read-write from `esinit:10`; `/usr/bin/go-mtpfs`
  is absent but the shell expands the whole line before execution, so a missing
  helper does not block an injected command. Service has no `User=` so runs as
  uid 0.
- V-007 confirmed as configuration only: no media unit sets `User=`,
  lightmediascannerd/thumbnail_extractor/mediamanager/playerengine/MediaBrowser
  are configured uid 0, no seccomp or capability restrictions exist and the
  image has zero setuid binaries. Reclassified as informational hardening, not a
  demonstrated vulnerability; no parser defect was found and runtime uid was not
  observed.
- V-008 confirmed as shipped configuration, not as a vulnerability: agetty on
  ttyS2 115200 with autologin commented out, securetty permits ttyS2,
  passwd.legacy gives root /bin/sh, and shadow.Global root is a $6$ SHA-512-crypt
  verifier with a unique salt and no locked marker; the other 18 accounts are
  locked. esinit is fail-open because it creates the enable marker before testing
  it. Dropbear is absent and inert despite one static authorized_keys entry.
- Astra triaged the three findings and corrected several overstatements: a
  system-service default is not an observed uid; absence of seccomp directives is
  not proof of no filtering; comma rejection blocks only comma-list brace forms;
  and a password verifier is not evidence of password weakness. Astra also
  advised that head-unit root does not establish vehicle-bus, safety-system or
  key-material access, and recommended holding V-006/7/8 technical dossiers
  privately pending vendor contact. The public mirror was left unchanged at its
  conservative "unverified" text.
- Fable was requested twice for this triage and returned neither text nor the
  requested output file, so no Fable execution is claimed. Astra performed the
  triage instead and is attributed as such.
- No VM was booted and no device was touched; all evidence is static.


## 2026-10-29 — EC-02 blocked by over-specification

- Reviewed the EC-02 hardware-breakpoint mechanism four times. Round 3 took the
  instructed change of approach: a normative machine-readable state machine
  (17 states, 48 transitions, 21-row classify-only decision table, mechanically
  derived budget) became the single source of truth, with the prose report and
  facts reduced to citations.
- Round 4 still returned REQUEST_CHANGES. Defects found were structural rather
  than editorial: absent pre-arm and subsequent revalidation failure edges; no
  ST_SEIZE -> ST_STOP0 transition and no initial interrupt; already-forwarded
  signals left pending and therefore redeliverable; budget operation sums that
  disagree with their own declarations plus unreachable maxima; a detach-error
  terminal that falsely reports the tracee detached; classifier row 8 shadowing
  nested and protocol rows; and inconsistent single-step routing and activation
  counters.
- Recorded the root cause instead of running a fifth textual round: the spec is
  over-specified for its purpose. The mechanism report grew from 771 to 1,931
  lines and gained a 1,187-line state machine for what is a bounded diagnostic
  observer, and each correction surfaces a new edge because edge policy is being
  authored with no implementation feedback.
- Recommendation recorded: rescope EC-03 to a minimal verifiable core - SEIZE,
  the four hardware observation points, bounded capture, restoration and a
  host-owned timeout - then let EC-04 fixtures settle the remaining edge policy
  empirically. EC-03 stays gated pending the owner's decision.
- No VM was booted, no target executed, no fixture run and no EGL behaviour
  measured. Ledger validates; EC-02 artifacts re-hashed in the ledger.


## 2026-10-29 — guest hardware breakpoints proven under TCG

- Stopped specifying and measured instead. Wrote a VM-only capability probe,
  tools/uk_fw/guest/dr_breakpoint_probe.c, that forks a tracee, stops it before
  user code, arms DR0 to an execute address and sets DR7.L0, continues, and checks
  the resulting trap, RIP and DR6 before restoring and requiring a clean exit.
- Built static x86-64 with the project Zig toolchain under -Wall -Wextra -Werror,
  and ran it through tools/uk_fw/vm_boot.py in a synthetic busybox workspace using
  the measured EU 260128 kernel with the documented --sdhci-compat adaptation.
  The first attempt without that adaptation stalled waiting for /dev/mmcblk0.
- Result: SUPPORTED. DR7 baseline 0x0 became 0x401; the trap arrived as SIGTRAP
  with RIP equal to the armed address 0x1002eb0 and DR6=0x1 reporting B0; after
  restoring DR7 and clearing DR0 the tracee exited 0 with no further trap; and
  PTRACE_SINGLESTEP advanced RIP from 0x10040be to 0x10040c1. Command elapsed
  3.64 s with exit code 0 and no timeout.
- This resolves EC-02 finding C-07, the single load-bearing unknown for the
  hardware-breakpoint mechanism. EC-02 was never blocked on capability; the
  remaining blockers are specification defects. The EC-04 fixture that the
  question had been deferred to is cheap and needs no vendor userspace.
- Bounds recorded rather than glossed: the probe ran against a synthetic tracee at
  user addresses, not against vendor libEGL observation points. Per-thread four
  slot capacity and slot-replacement semantics were not independently exercised,
  DR6 semantics beyond B0 and detach-time teardown of ptrace_bps remain unverified.
  No vendor binary executed, no navigation state claimed, no hardware touched.
- One authoring self-correction is recorded: the first draft of the probe omitted
  stdarg.h and left its tracee parked after the trap, so it was rewritten as a
  single arm/trap/restore/clean-exit sequence before any VM run.


## 2026-10-29 — detach discipline measured; four-slot behaviour verified

- Extended the hardware-breakpoint capability probe to the behaviours round 1 had
  explicitly left unexercised, since the EC-02 observer depends on each: four-slot
  capacity, slot replacement, invalid debug-register rejection, detach behaviour,
  and the safe detach sequence. Nine checks now pass in 3.85 s with exit 0.
- Four slots armed together (DR7 0x455) fired in program order at the correct
  RIPs, but only because the fired slot was disarmed before each resume. An
  execute breakpoint retriggers while enabled, so disarm-before-resume is a
  measured requirement, not a preference.
- Slot replacement was demonstrated: slot 0 fired at one function, then at a
  different address after reprogramming.
- DR4 and DR5 were rejected with errno 5 EIO, so the valid ptrace index set is
  0-3,6,7. This invalidates EC-02 fixture V-03's assumption that a fifth slot
  could be exercised through DR4.
- Detach behaviour was the significant result. With a slot still armed,
  PTRACE_DETACH left the breakpoint live and the untraced process was killed by
  SIGTRAP. EC-02's C-09 concern about kernel teardown of ptrace_bps is therefore
  confirmed rather than merely defensive.
- The safe exit was then proven: clear the DR7 enables, clear the address
  register, verify the readback reads zero, then detach. The tracee completed with
  exit 0. Both the failure mode and the remedy are now measured.
- Bounds recorded: synthetic tracee at user addresses with no vendor observation
  point; per-TID scoping and DR6 semantics beyond B0 remain unexercised; no vendor
  binary executed and no hardware touched.


## 2026-10-29 — community chat transcribed and leads triaged

- Transcribed eight owner-supplied Discord screenshots into a single de-duplicated
  transcript at evidence/community-chat-transcript-261029.md. The images were
  overlapping scrolls of one channel rather than eight conversations, so they were
  merged by timestamp with attribution preserved and relative labels left as shown.
- Recorded the transcript as unverified participant reports. It is useful for
  provenance, not as evidence that any method works, and several of its claims are
  contradicted by our own measurements.
- The transcript is the origin of the three exploit bullets captured as V-006, V-007
  and V-008. Cross-referenced each: V-006 confirmed but through system() in
  usb-automount on the PTP branch rather than a mount script, with the literal
  payload in the chat failing because spaces become underscores; V-007 confirmed only
  as configuration; V-008 confirmed as shipped password-gated configuration with no
  bypass.
- Ran cheap offline checks on the remaining leads. AppEngineerMode exists at
  /app/bin/AppEngineerMode with QML under /app/share/AppEngineerMode/qml, but the
  reported PIN 19480717 and the tap sequence 3 2 8 9 6 5 are absent as text from that
  binary and from QML/JS/conf under app and usr/share, so the entry handler is most
  plausibly the Settings application behind System info -> Manual.
- /tool/velix_aes.key and /tool/public.crt do not exist in the rootfs; those paths sit
  inside the AppUpgrade payload and belong to its decrypted tree. The claim that the
  IV is derived from the SHA-256 of the encrypted file name and size remains
  untested and is the most directly checkable item, to be compared against
  tools/uk_fw/gen5w_decrypt.py.
- Publication caution recorded: the transcript contains an engineering-mode PIN, a
  claimed VM image digest and a partial key-like hex string, so PUBLIC-RELEASE.md
  applies before mirroring. No disclosure decision was taken.


## 2026-10-29 — DR6 attribution verified; transcript IV claim corroborated

- Completed the hardware-breakpoint capability matrix with a DR6 test. With slots
  0 and 1 armed at different addresses, the first trap reported DR6=0x1 identifying
  B0, a POKEUSER write of 0 to DR6 read back as 0x0, and the second trap reported
  DR6=0x2 identifying B1. Ten checks pass in 3.83 s with exit 0.
- This settles a point the EC-02 specification had disputed: the observer can
  attribute a trap to a specific slot from DR6 and can clear stale status between
  stages, instead of inferring the slot from RIP alone.
- Per-TID scoping remains the only unexercised capability item: one traced thread
  while a sibling executes the same code.
- Checked the community transcript's most concrete claim against our own tooling.
  The chat states the update IV is derived from the SHA-256 of the encrypted file
  name and size. tools/uk_fw/gen5w_decrypt.py, derived independently from the
  envelope evidence, computes the IV as the first 16 bytes of
  SHA256((basename + signed_int32(body_size))) with body size file_size - 0x4024,
  and produces working decryptions. The claim is consequently recorded as
  corroborated, with the precise semantics, rather than as an open lead.
- No disclosure decision was taken and no VM image was modified.


## 2026-10-29 — capability matrix complete: per-thread scoping verified

- Closed the last unexercised item in the hardware-breakpoint capability matrix.
  Debug registers were shown to be per thread: the traced main thread trapped at an
  armed execute address, was single-stepped past with the slot temporarily
  disabled, the slot was then deliberately re-armed, and an untraced sibling thread
  executed the same function with no effect. The process exited 0. Eleven checks
  pass in 3.94 s with exit 0.
- The test was sequenced rather than raced, with the sibling spinning on a flag set
  only after the traced thread had been stepped past, so the two possible outcomes
  are distinguishable: an unaffected sibling yields a clean exit, whereas a
  process-wide slot would kill the untraced sibling on SIGTRAP, the same signature
  T8 established for untraced breakpoint hits.
- Consequence for EC-02: observing a single main thread is sound and needs neither
  thread-group control nor PTRACE_O_TRACECLONE. That removes an open design
  question rather than adding one.
- One authoring correction: the edit that introduced the threading headers replaced
  stdarg.h rather than extending the include list, which -Werror caught at build
  time before any VM run.
- Bounds stated explicitly: only execute breakpoints were exercised, data
  read/write watchpoints were not, and behaviour with many threads or
  PTRACE_O_TRACECLONE was not examined.
- No disclosure decision taken; no VM image modified; no vendor binary executed by
  the probe.

## 2026-10-29 — null-buffer BG question narrowed, with a reversed inference

- Returned to the main navigation workstream, which is independent of the EC-02
  gate, to settle whether a Qt hide can ever produce the BG notification that
  ApplicationManager requires.
- Established by disassembly that the FG/BG predicate lives in ivi-window-manager.so
  at 0xf981 and tests the surface size fields 0x68 and 0x6c, reproducing the known
  rule that any positive dimension selects FG. ivi_layout_surface_configure in
  ivi-shell.so at 0x81a0 only fans out to listeners and performs no classification.
  The two size fields are written only by surface_set_size in usr/bin/weston at
  0x40d4a0, whose three call sites all lie inside weston_surface_commit_state.
- The first inference, that a null buffer leaves the size positive and therefore
  cannot produce BG, was contradicted by two additional checks and is recorded as
  reversed. surface_attach at 0x40df20 treats a NULL resource by setting buffer to
  NULL and still setting the pending buffer-attached flag at pending+0x00, and
  commit_state at 0x40f32c enters the size block whenever that flag is set. A
  null-buffer commit therefore does reach surface_set_size.
- Whether that call writes 0x0 depends on fields 0x104 and 0x108 of the surface
  struct, whose meaning after a null attach is not yet established. A hidden surface
  yielding 0x0 and hence BG is consequently plausible rather than excluded, which
  raises the value of pursuing AppNavi's authentic hide path instead of assuming a
  resize adapter is required.
- A delegated worker was interrupted mid-analysis by the pi-gui restart after
  writing six disassembly excerpts and no report. The excerpts were retained and the
  analysis was completed by the coordinator from them plus direct llvm-objdump
  checks. No rootfs file was modified and no VM was booted.

## 2026-10-29 — skills updated, public disclosure reduced, EC-03 minimal core built

- Installed the Sol 6.1 skill bundle supplied by the owner. It moves default
  reviewers to gpt-6.1-sol and replaces Astra throughout examples and fixtures. The
  bundle did not include the operator's requirement that DeepSeek workers use the
  direct API provider and still referenced the superseded router route
  deepseek/deepseek-v4.1-flash, so that policy was re-applied across SKILL.md,
  references/protocol.md, README.md, docs/INSTALLATION.md, agents/openai.yaml and
  The Council, using the verified direct route deepseek/deepseek-flash.
- Both skills re-validated after the edit: 148 and 93 unit tests pass, and the
  packaging validator reports each skill valid. The earlier validator failure was
  traced to a Python interpreter without PyYAML rather than to the skills.
- The owner authorised the two pending decisions. For disclosure, the public mirror
  now carries status-only entries for V-006, V-007 and V-008 with no component
  names, property names, code locations or payload detail; the public tree was
  checked to contain no occurrence of the affected service or property names. The
  full dossiers remain private. Pre-existing publication of the engineering-mode
  entry sequence and PIN in that tree was noted rather than silently removed,
  because deleting it would not undo the exposure.
- For the rescope, EC-02 was stopped rather than reviewed a fifth time, and the
  EC-03 minimal core was implemented instead: tools/uk_fw/guest/ec03_observer.c
  performs SEIZE on a single thread, arms up to four execute breakpoints addressed
  as module substring plus offset, captures registers at each hit, disarms a slot
  after it fires, tears down with the mandated disarm/verify/detach sequence, and
  enforces both a deadline and a stop bound.
- The observer was validated end to end in the VM against a synthetic target. Without
  --once the tracee outlives the observer and teardown is reported unverifiable
  because the tracee is gone; with --once the observer detaches while the tracee is
  stopped and reports teardown verified with detach ok. Both runs exit 0.
- Three defects were found and fixed during that validation: a missing stddef.h
  include for offsetof; module-base resolution that had wrongly required an
  offset-zero mapping, which static non-PIE text does not have; and teardown being
  attempted against an already-exited tracee. The guest image also lacks busybox
  applet symlinks, so the driver now invokes applets through /bin/busybox.
- EC-02 is recorded as blocked and superseded rather than accepted, and the ledger
  validator's refusal to accept an important task without independent verification
  was respected rather than worked around.

## 2026-10-29 — second skill bundle pulled; policy patcher added

- Pulled and installed the second Sol 6.1 skill bundle supplied by the owner. The
  substantive difference from the first is Council behaviour: three Sol 6.1
  reviewers at xhigh reasoning by default, Astra-medium supported as an explicit
  seat, and sol aliasing Sol 6.1.
- The bundle shipped once more without the operator's direct-DeepSeek-provider
  requirement and still referenced the superseded deepseek/deepseek-v4.1-flash
  route. Because this had now happened twice, the correction was automated as an
  idempotent patcher rather than repeated by hand: it enforces the policy across
  SKILL.md, both protocol references, README, the installation guide and the
  invocation metadata, tries several candidate anchors because the Council protocol
  wording changes between bundles, and exits non-zero if it cannot find an anchor
  rather than silently skipping.
- Re-validated afterwards: 148 and 93 unit tests pass and both skills report as
  valid.
- Nine occurrences of the stale route id were left in place because they are test
  fixtures and a ledger example rather than policy text, and changing them could
  break assertions bound to the literal.

## 2026-10-29 — observer gains field capture

- Implemented the increment the ledger recorded next for EC-03: int32 field capture
  at an observation hit. Two fields are read from a struct pointer supplied either as
  an absolute address or as a register name, defaulting to the EC-01 contract offsets
  0x2c for width and 0x30 for height, with overrides. This is the shape required to
  capture the vendor dri2_surf dimensions before and after the buffer update.
- Validated in the VM across three cases, all exiting 0 in 12.87 s: without --once the
  tracee outlives the observer so teardown is reported unverifiable because the
  tracee is gone; with --once teardown is verified with detach ok; and an unknown
  register name is reported as status unknown-register instead of being guessed.
- The measurement itself confirmed the instrument reads the intended fields: FIELDS
  status ok with a=1926 and b=753 at offsets 0x2c and 0x30.
- Bounded honestly: the register-held pointer mode was validated only on its error
  path, because a synthetic target cannot reliably place a chosen value in a
  callee-saved register at a breakpoint. Its real exercise is the authentic AppCamera
  stage, where r15 holds the surface pointer.
- One defect was found and fixed: an unused field_regs global that -Werror rejected,
  removed rather than suppressed.

## 2026-10-29 — authentic measurement of the EGL dimension ordering

- Ran the EC-03 observer against the authentic AppCamera inside the real launcher
  chain and captured both EC-01 stages on the same surface pointer. At
  libEGL+0x16f16, before the width cache, the surface fields at +0x2c and +0x30 read
  -1 and -1. At libEGL+0x16f1e, immediately after swrast_update_buffers returns, the
  same struct read 1920 and 720. Teardown reported verified with detach ok.
- This measures the ordering defect behind I-001 rather than inferring it. The copy
  path derived its stride from Width=-1, giving -4 bytes, while the update populated
  the real geometry during the same invocation. It supersedes the earlier position,
  including my own correction two turns ago, that a width change had not been
  observed on this path.
- I-001 in the defensive register was rewritten to match: mechanism measured, still
  not a demonstrated exploitable vulnerability, with stock-driver reachability,
  attacker influence over the values, and any link to navigation failure explicitly
  left unestablished.
- Method notes retained because they cost real time: the canonical vendor image must
  not be modified and a plain copy costs 23 GB, so the run used an APFS copy-on-write
  clone, made in 0.031 s, with two files injected through debugfs. An earlier attempt
  to stream the binary over the serial console failed because the whole command
  became a single 80 KB line that the line discipline truncated.
- Two genuine defects were found and fixed. The driver inherited an argument-guard
  block that still invoked the previous crash observer, and the observer resolved
  libEGL before the client had mapped it. The second is a real race, since AppCamera
  becomes visible before its graphics libraries load, and is now handled by a bounded
  wait for the module with the tracee left running.

## 2026-10-29 — null-buffer question resolved; hide does not produce BG

- Settled the remaining navigation question using DWARF instead of inference. The
  weston binary retains debug information for weston_surface (weston 1.10.0-r21,
  compositor.h:1066), which fixes the layout as width at 0x68, height at 0x6c,
  width_from_buffer at 0x104 and height_from_buffer at 0x108. This confirms that the
  FG/BG predicate tests the surface's own size fields and that the commit path feeds
  them from the _from_buffer pair.
- A null-buffer attach does zero both _from_buffer fields at 0x40f813, reached when
  the buffer pointer is null. An earlier correction stopped at that point and
  concluded that BG was reachable, which was incorrect: the size block at 0x40f470
  executes before that zeroing, so it stores the previous positive size and the
  surface remains positive.
- The conclusion is therefore that a bare hide does not produce BG, and a genuine
  transition to non-positive dimensions is required, which matches the earlier
  Camera/Standby control that drove 1926x753 to 0x0 and then BG. The integration
  route consequently needs a scoped resize adapter rather than the authentic hide
  path.
- The reversal is recorded rather than tidied away: the withdrawn reasoning remains in
  the analysis report with an explicit note that it is superseded.
- Method notes: the DWARF inspection required llvm-dwarfdump with a byte-window scan,
  and several earlier greps silently matched nothing because objdump separates its
  columns with tabs rather than spaces.

## 2026-10-29 — I-001 scoped to the swrast path

- Established that no Intel hardware is required to continue. The same check narrowed
  I-001: vendor libEGL defines four surface constructors, and the -1 sentinel belongs
  to the swrast-specific one, while put_image2, get_image and swap_buffers all belong
  to the dri2_wl_swrast family. The hardware constructors are separate and do not
  share that vtable.
- The honest consequence was recorded: the evidence does not implicate the i965/i915
  path, so I-001 is a defect of the vendor's Wayland software-rendering path, which is
  the path this VM necessarily uses. That reduces rather than increases its real-world
  severity, and the register was updated to say so rather than leaving an implied
  hardware claim.
- The vendor image ships its own DRI drivers for i965, i915 and iu3d9, so the earlier
  mixed-stack caveat concerns which module loads in emulation, not an absence of
  vendor graphics code.
- No Intel machine is needed for the remaining authorised work: the navigation 0x0
  adapter, service reconstruction, audio, CAN/MICOM and persistence all execute in the
  VM.

## 2026-10-29 — navigation 0x0 adapter built; timing still wrong

- Began the integration piece the BG analysis called for: a scoped adapter that drives
  AppNavi's parent surface to a genuine 0x0 configure so the compositor classifies it
  BG. The mechanism follows from the earlier ordering finding: one null attach is
  insufficient because the size block stores the previous width_from_buffer before the
  null branch zeroes it, so two consecutive null attaches are required.
- Implemented as an LD_PRELOAD interposer on wl_surface_attach that forces a NULL
  buffer on two consecutive attaches. It drives only the vendor compositor and never
  calls the manager, writes the window byte, or synthesises a notification.
- Two runs completed with exit 0 in about 412 seconds each, and both still reported
  manager 11/11. Two defects were found and fixed: the preload is inherited by every
  launcher child, so the first attempt collapsed the wrong application, now gated to
  AppNavi through /proc/self/cmdline; and the trigger fired before the client had
  painted, so AppNavi never foregrounded, now gated behind a minimum attach count.
- Status recorded honestly: the plumbing is proven end to end, since the interposer
  loads under the vendor glibc 2.25, is correctly scoped, the chain still completes and
  manager state is queryable at the chosen moment. BG was not reached and the
  Home-to-Navigation transition is unchanged. The paint-first variant is built but not
  yet exercised.
- Built against x86_64-linux-gnu.2.25 rather than musl, since a musl-linked shared
  object will not load into the vendor glibc process.

## 2026-10-29 — engineering mode research published; navi 0x0 still not reaching BG

- Recorded the engineering-mode entry and PIN research in
  evidence/engineering-mode-research.md and published the same document to the public
  repository after the owner authorised releasing the PINs and entry methods.
- The entry gesture is Settings, General settings, System info, Manual, then taps on the
  left panel carrying the QR code and text in the order 3-2-8-9-6-5, which opens an
  eight-digit keypad. The engineering-mode PIN recorded is 19480717, reported accepted
  on a UK-origin 2021 IONIQ 5 whose installed build was later identified as 250604, so
  acceptance there does not establish the 260128 package.
- Dealer mode and full engineering mode are distinct with different codes, and two
  public references disagree about rotating codes. The SOP-gate claim, previously
  single-source, is now corroborated at code level: the binary really does contain
  bool AppEngineerModeEngine::checkSOPVersion().
- The PIN check was located: AppEngineerMode_PinCodeKeypad.qml calls
  AppEngineerModeEngine.checkPassWord at line 391 and branches on the return value, where
  21 and 11 are menu selectors rather than entered PINs. Lockout machinery is present,
  so failures are rate-limited by design. The binary is stripped but retains 111 C++
  signature strings, which is how those methods were identified.
- A full scan of 408,412 files across all five extracted components, including 444
  expanded archives, found the PIN in none of five encodings. The most probable
  explanation is that the reported PIN belongs to the owner's 250604 build rather than
  the 260128 package being analysed.
- The entry gesture is not implemented in QML, since Screen_Manual.qml has no MouseArea
  or onClicked handler, and no binary contains the literal AppEngineerMode, so the
  gesture is handled natively and the application is launched through the launcher
  registry.
- AppNavi update feasibility remains undetermined. The older capability is recorded as
  Engineering Mode, Config, Update AppNavi from USB, and four decision gates were
  written down, with the launcher executable inspection identified as the cheapest
  decisive test.
- The paint-first navi 0x0 run was also recorded: it completed with exit 0 but the
  manager still reported 11/11, so BG was not reached and the Home-to-Navigation
  transition is unchanged. Triggering on an attach count rather than on an observed
  event is the likely remaining flaw.

## 2026-10-29 — navi 0x0 adapter never fired; diagnosis narrowed

- Replaced the attach-count trigger with a sustained hold: while the trigger file
  exists, every attach on AppNavi's target surface is replaced by a null-buffer attach,
  holding the surface at 0x0 rather than flipping it for one frame. The hold lasted six
  seconds, then was released and observed again.
- The manager reported 11/11 during the hold and 11/11 after release, so BG was again
  not reached.
- Because "no manager change" and "adapter never ran" were indistinguishable, the
  interposer was given an audit write on first hold. The run produced no audit file at
  all, which shows the interposer never executed a hold. The manager readings from both
  attempts therefore say nothing about whether BG is reachable by this route.
- Two candidate causes remain indistinguishable. Either the preload never reaches
  AppNavi, which could happen if AppLauncher execs child applications with a sanitised
  environment, or SMACK denies access to the trigger file and the audit path for
  AppNavi's label, failing silently in exactly the observed way.
- The next step was recorded: take the filesystem out of the probe, logging to stderr
  which the launcher captures, and deriving the trigger from a monotonic clock or a
  launch-time environment variable so neither SMACK policy nor exec environment handling
  can block it without leaving a trace.
- Build and injection remain clean, the chain completes with exit 0 in about 418
  seconds, and screenshots were captured both during the hold and after release.

## 2026-10-29 — navi 0x0 injection unblocked

- Found the root cause behind every earlier "adapter never ran" result. The launcher
  liveness interposer deliberately calls unsetenv on LD_PRELOAD when it runs as
  AppLauncher, so vendor children inherit a clean environment. Any LD_PRELOAD placed on
  the launcher command line therefore never reaches AppNavi, which explains four
  consecutive attempts that produced no effect and no trace.
- The fix uses that same interposer's execve hook, which rewrites envp for AppNavi only.
  A variant now injects the navi-bg library ahead of the existing EGL compatibility
  entry for AppNavi alone, and the source was added to tools/uk_fw/guest.
- Injection is verified: the kernel log records navi-bg loading inside AppNavi at
  pid 857 with the configured hold window. The adapter demonstrably executes.
- The probe was also made filesystem-free, with the hold window derived from a
  monotonic clock and launch-time environment variables and the timeline written to
  /dev/kmsg, so neither SMACK policy nor exec environment handling can block it
  silently.
- Remaining gap: no first-attach record followed, so AppNavi did not attach a buffer on
  the elected surface within the window, and the manager still reported 11/11. The next
  step is to log every attach plus a destructor summary so a zero-attach run cannot be
  confused with a timing miss, then to align the window with real rendering.
- A method correction is recorded: an earlier conclusion that the library never loaded
  was wrong, because it depended on AppNavi's stderr appearing in launcher.log, where it
  does not. The kernel log is the reliable channel and overturned that diagnosis.

## 2026-10-29 — BG experiment repositioned; AppNavi does not render in the full chain

- Moved the navi-bg experiment to after the chain's own navigation transition request,
  because its previous placement ran before AppNavi had been asked to come forward. The
  hold also changed from a wall-clock window, which is measured from process start and
  was long past at that point, to an attach-count window anchored there.
- The wait then ran its full 180 seconds without observing a first surface attach. No
  interposer timeline was produced and the navi-live screenshots hashed identically to
  the earlier Home frames.
- The conclusion recorded is that AppNavi never becomes a rendering Wayland client in
  this full-chain configuration, so no surface exists for the adapter to hold. That is
  the Home-to-Navigation blocker itself rather than a defect in the adapter.
- A strategic correction was written down: the full chain is the wrong vehicle for this
  experiment. The standalone AppNavi render probe already present in the image is
  documented to produce genuine map pixels and should host the adapter, reusing the
  execve-hook injection that is now proven to work.
- A measurement caveat was also recorded: dmesg is unreliable as a late-run probe
  because the kernel ring buffer can wrap during a run of several hundred seconds, so an
  absent line near the end is weak evidence. Process state or a log file should be
  preferred for near-real-time checks.

## 2026-10-29 — adapter moved to the render probe; AppNavi still never attaches

- Built a variant of the standalone AppNavi render probe, which runs a session bus,
  weston-headless with the IVI shell and a real ApplicationManager before execing AppNavi
  directly, so the adapter no longer depends on the launcher hook.
- The first attempt launched AppNavi through the busybox timeout applet and lost the
  preload across that extra exec hop. Launching AppNavi directly corrected it, and
  AppNavi's own log now records the adapter loading with the configured hold parameters.
- No surface attach followed. That single line is the whole AppNavi log, and the manager
  reported drawing application 0 both before and after, which is not the behaviour of a
  rendering Qt client.
- An important open question was recorded: whether the interposer itself now prevents
  AppNavi from rendering. The cheapest discriminator is a baseline run of the same probe
  without the preload, comparing AppNavi's log and behaviour, and that is the next step.
- A method note was added: in this probe stderr reaches appnavi.log reliably while
  /dev/kmsg produced nothing, so an absent dmesg entry here reflects the channel rather
  than proving absence.

## 2026-10-29 — navigation status published to both repositories

- Published docs/navigation-status.md in the public repository along with the research
  helpers behind it, and kept the same document here as evidence/navigation-status.md so
  the private record matches what was released.
- The document states the three measured results of this session and, plainly, the one
  remaining blocker: AppNavi never attaches a surface, so nothing reaches the compositor
  to be classified, and the open question is whether the interposer itself prevents
  rendering.
- The new files were checked before publication for personal paths, VIN-shaped tokens and
  credentials, and the public harness passed on the clone before the push. No
  vulnerability register, raw evidence, ledger or firmware was published.

## 2026-10-29 — working tree committed and probes published

- Committed the working tree that had been preserved uncommitted through the VM work:
  the harness additions in vm_boot.py, the TE2 decryptor work in gen5w_decrypt.py, their
  tests, the eleven guest research helpers and the operations contract.
- One personal path in the operations contract was replaced with a placeholder before the
  commit. Everything else in the set was checked for personal paths, VIN-shaped tokens
  and credentials and came back clean. Harness and the full 171-test suite pass.
- Three further research instruments were published to the public repository, closing the
  gap between the private and public tool sets, namely the breakpoint capability probe,
  the minimal observer and its synthetic target.
- The vulnerability register, raw evidence tree, task ledger and all firmware remain
  private; the public tree carries neither firmware nor credentials.

## 2026-10-29 — baseline clears the interposer

- Ran the control that the open question called for: the identical render probe with no
  preload at all. AppNavi's log came back empty, zero lines, and the manager reported
  drawing application 0, which is the same outcome as the run with the adapter loaded
  apart from the adapter's own single load record.
- The interposer is therefore cleared of causing AppNavi's silence, and the fault lies in
  AppNavi's own startup in this probe.
- A caveat was recorded alongside it because it changes what can be claimed: an empty log
  does not prove nothing rendered. AppNavi may log to DLT or to a file, or not at all, and
  the probe's screenshot had not been inspected. Rendering silently and never rendering
  both remain open possibilities.
- The next steps were written down: inspect the captured frame and check whether AppNavi
  logs to DLT before drawing conclusions about its startup.
- docs/navigation-status.md was updated in both repositories so the published open
  question is replaced by this baseline result.

## 2026-10-29 — public disclosure reduction for the physical-access entries
- Reduced V-006, V-007 and V-008 in the public tree to status entries carrying no
  operational detail. The earlier entries here described these as unverified
  third-party claims; offline validation has since confirmed V-006 as a genuine
  command-construction defect reached from a privileged USB service, and reduced
  V-007 and V-008 to configuration observations.
- The detailed dossiers, including component names, property names, code locations
  and reproduction notes, are retained privately pending coordinated vendor
  contact. This public tree was checked and contains no occurrence of the affected
  service name or property name.
- Pre-existing publication noted rather than altered: the engineering-mode entry
  sequence and PIN were already present in this tree from earlier work. Removing
  them now would not undo that exposure, so they were left in place and flagged.

## 2026-10-29 — navigation status published
- Published docs/navigation-status.md together with the research helpers behind it, so
  the current Home-to-Navigation gap is documented from measurement rather than
  inference.
- The EGL dimension ordering is now measured on the authentic client: the surface fields
  read -1/-1 immediately before the width cache and 1920/720 immediately after
  swrast_update_buffers returns, on the same surface pointer. The defect is scoped to the
  vendor's Wayland software path, because the hardware constructors are separate and do
  not share that vtable.
- A Qt hide is shown to be insufficient for the background notification. With the
  weston_surface layout fixed by DWARF, the commit path stores the previous positive size
  before the null-buffer branch zeroes the buffer-derived fields, so a genuine 0x0
  transition is required.
- Guest hardware breakpoints are confirmed working under TCG, with four slots, slot
  replacement, rejected DR4/DR5, per-slot DR6 status, single step and per-thread scoping.
  Detaching with a slot still armed leaves it live and kills the tracee, so disarm and
  verify before detaching.
- Two injection facts were published because they cost time to learn: the launcher
  interposer unsets LD_PRELOAD for AppLauncher so vendor children inherit a clean
  environment, and a musl-linked shared object will not load into the vendor glibc
  process.
- The remaining blocker is stated plainly: AppNavi never attaches a surface in either
  configuration, so nothing reaches the compositor. Whether the interposer itself
  prevents rendering is recorded as the open question, with a baseline run without it as
  the next step.

## 2026-10-29 — baseline clears the adapter
- Ran the control the published open question called for: the identical render probe with
  no preload. AppNavi's log came back empty and the manager reported drawing application
  0, matching the with-adapter run apart from the adapter's single load record, so the
  interposer is not what stops AppNavi.
- Recorded with it that an empty log does not prove nothing rendered, since AppNavi may
  log to DLT or a file and the captured frame had not been inspected. Rendering silently
  and never rendering both remain open.
- The navigation status document was updated so the published open question is replaced
  by this result, and the baseline probe was added to the public tools so the control can
  be reproduced.

## 2026-10-29 — A/B shows AppNavi paints nothing at all
- Tested the previous entry's caveat with an A/B across three runs of the same probe: with
  the adapter, without it, and with AppNavi not launched at all. The captured frame is
  byte-identical between the baseline and the no-AppNavi control.
- The conclusion is that AppNavi renders nothing. It is alive, silent and contributes no
  pixels, so the adapter is not implicated and the compositor contract, the zero-size hold
  and the background notification cannot be exercised until AppNavi paints.
- The next step was narrowed to finding why AppNavi is alive but idle, by comparing the
  environment and arguments the launcher normally supplies against this probe's direct
  launch.
- An inconsistency between the two repositories was corrected: an earlier hard reset in the
  public clone discarded an uncommitted edit to the navigation status document, so the
  public copy still described the question as open while this copy already carried the
  baseline result. Both now agree.

### (other lineage, same date)

- Because an empty log does not prove that nothing rendered, the previous entry's caveat
  was tested directly with an A/B across three runs of the same probe: with the adapter,
  without it, and with AppNavi not launched at all. The captured frame is byte-identical
  between the baseline and the no-AppNavi control.
- The conclusion recorded is that AppNavi renders nothing. It is alive, silent and
  contributes no pixels, so the adapter is not implicated and the compositor contract, the
  zero-size hold and the background notification cannot be exercised until AppNavi paints.
- The next step was narrowed accordingly: find why AppNavi is alive but idle, starting with
  the environment and arguments that the launcher normally supplies compared with this
  probe's direct launch.
- A documentation inconsistency was also corrected. An earlier hard reset in the public
  clone discarded an uncommitted edit to the navigation status document, so the public copy
  still described the question as open while the private copy already carried the baseline
  result; both copies now agree.

## 2026-10-29 — why AppNavi idles: surface id and visibility are injected from outside

- Analysed the "alive but paints nothing" blocker and retained the report as
  evidence/appnavi-startup-analysis.md with the working excerpts alongside it.
- The leading cause is that AppNavi links libivi-platform-interface.so.1 directly, and
  that library resolves the ivi surface id only from the environment, via
  QT_WAYLAND_SET_SURFACE_ID and its FORCED and USE_PID variants. On the vehicle the value
  is injected by AppLauncher, which also sets APPID. Both the NEEDED entry and the three
  variable names were verified independently.
- With the variable unset the library enters an uncapped blockingReadEvents loop waiting
  for an id reply, which matches the observed symptom of a process that is alive, silent
  and produces no surface, rather than one that crashes.
- Several candidates were ruled out: ApplicationManager's absence, because the project's
  no-AppManager run still committed a 1920x720 buffer; all command-line flags in the
  current invocation; and APPID, which AppLauncher reads rather than AppNavi. AppNavi
  itself reads only MD_CONA40_ON.
- A significant open point was flagged: the VM logs show the ivi surface created under id
  30000 while the ivi-fg helper programmes 3000, so visibility may be requested for an id
  that does not exist. The offset's origin lives in .bss and was not established
  statically.
- The cheapest next test was written down: one boot with QT_WAYLAND_SET_SURFACE_ID=3000 and
  no ApplicationManager, checking which id the surface actually receives and re-driving the
  helper with that id.

## 2026-10-29 — first hardware-dependency adaptor found and stubbed

- With Wayland client debugging enabled, AppNavi's own log shows it connects, enumerates the
  registry including the ivi application global, and then never creates a surface. The tail
  of the log is a repeated failure to read /sys/class/gpio/gpio440/value.
- Confirmed in the VM that the node cannot exist: the gpio class holds only export and
  unexport, and exporting 440 returns EINVAL because no gpiochip registers that pin, which
  matches the kernel log where the GPS driver defers with -517 and never acquires it. The
  emulated board lacks hardware the firmware expects rather than being misconfigured.
- Built an adaptor in the form of a tmpfs over the gpio class with an inert gpio440 node.
  The gpio440 errors then vanish from AppNavi's log, which is the first demonstrated case in
  this project of a simulated hardware dependency unblocking a firmware startup path.
- Recorded honestly that it is not yet sufficient: surface creation appeared in one run and
  not the next, so either another dependency also gates the render path or the timing is
  racy. The stub is necessary and reproducible; further work is needed.

## 2026-10-29 — privacy checker corrected for Wayland object notation

- The harness reported five private email addresses in the retained AppNavi startup
  analysis. Investigation showed they were false positives caused by Wayland client debug
  output, which writes protocol objects as object@<id>.method, so field names like
  wl_surface@3.attach were parsed as addresses.
- The email pattern was tightened so the domain must start with a letter. Genuine addresses
  continue to match and the Wayland forms no longer do. A regression test was added so
  future protocol captures can be retained without tripping the privacy gate.
- The checker was corrected rather than the evidence rewritten: every Wayland capture would
  otherwise produce the same false positive, and editing quoted log text to satisfy a
  scanner would corrupt the evidence.

## 2026-10-29 — AppNavi's stop point isolated to the ivi surface creation

- With the gpio440 adaptor in place, protocol markers were counted in AppNavi's own Wayland
  debug log rather than shipping log text over the console, which is both cheaper and
  sufficient to locate the stop.
- The measured sequence is that AppNavi binds the display, enumerates 71 registry lines,
  binds wl_compositor, wl_shm and ivi_application, creates a wl_surface, and then never
  calls ivi_application.surface_create and never attaches or commits.
- wl_drm is absent entirely, because the compositor runs headless with pixman and offers no
  GPU buffer interface. Whether that causes the stop or merely accompanies it remains
  unestablished.
- Setting QT_WAYLAND_SET_SURFACE_ID_FORCED in addition to the surface id produced a second
  wl_surface but still no surface_create, so the forced environment path alone does not
  clear the stop.
- Ruled out along the way: gpio440 polling, now stubbed; the preload adapter, whose removal
  changes nothing; ApplicationManager presence; and the current command-line flags. The next
  hypotheses are libivi's id acquisition, a missing buffer integration under pixman
  headless, or a later unmet startup requirement upstream of surface creation.

## 2026-10-29 — wl_drm ruled out; a working harness identified

- Ruled out the absent wl_drm as the reason AppNavi stops before creating its ivi surface. A
  prior successful run used the same weston-headless pixman stack with no ApplicationManager
  and reached surface_create for ids 3000, 30000 and 4903 with 26 attach calls, which proves a
  client can create ivi surfaces and attach buffers on this compositor without any DRM
  interface.
- The same evidence settles the earlier 3000-versus-30000 puzzle: AppNavi creates both ids,
  plus 4903 and 4900 for the map widget, so there was never a single expected id to match.
- A working harness was identified and is still present in the image, namely the valet-stub
  probe paired with the valet-stub runner. The next step is to diff that harness against the
  current probe rather than continue debugging, since the delta between them is what is
  missing.

## 2026-10-29 — why AppNavi idles, published
- Published the startup analysis into docs/navigation-status.md: AppNavi obtains its ivi
  surface id only from the environment through libivi-platform-interface, which on the
  vehicle is injected by AppLauncher together with APPID, and with the variable unset the
  library blocks in an uncapped read-events loop rather than crashing.
- Also published that window visibility is externally driven, arriving only as an
  ivi_surface.visibility event for the matching surface id.
- Ruled-out candidates were published as negative results: ApplicationManager's absence,
  the current command-line flags, and APPID. AppNavi itself reads only MD_CONA40_ON.
- The open point about the surface id being created as 30000 while the helper programmes
  3000 was also published, together with the single instrumented boot that would settle it.

## 2026-10-29 — missing gpio440 node identified and stubbed
- Published the reason AppNavi never paints: its Wayland client log ends with a repeated
  failure to read /sys/class/gpio/gpio440/value. The node cannot exist in this VM, since
  the gpio class holds only export and unexport and exporting 440 returns EINVAL because no
  gpiochip registers that pin, which matches the GPS driver deferring with -517.
- An adaptor consisting of a tmpfs over the gpio class with an inert gpio440 node removes
  the errors from AppNavi's log. It is the first demonstrated case here of a simulated
  hardware dependency unblocking a firmware startup path, and it is recorded as necessary
  but not yet sufficient because surface creation appeared only in one of two runs.
- A privacy checker false positive was also corrected, since the email pattern matched
  Wayland object notation and reported captured protocol logs as leaked addresses. The
  pattern now requires the domain to begin with a letter and a regression test covers it.
  The checker was fixed rather than the evidence rewritten.

## 2026-10-29 — AppNavi's stop published
- Published the precise stop point in docs/navigation-status.md, established by counting
  protocol markers rather than transporting log text: AppNavi binds the display, enumerates
  the registry, binds the compositor, shm and ivi application interfaces, creates a
  wl_surface, and then never creates the ivi surface and never attaches a buffer.
- Also published that wl_drm is entirely absent because the compositor runs headless with
  pixman, with cause and coincidence left open, and that the forced surface-id environment
  variable produces a second wl_surface without reaching surface_create.
- The forced-environment probe was added to the published tools so the result can be
  reproduced.

## 2026-10-29 — wl_drm ruled out and a working harness identified
- Ruled out the absent wl_drm as the gate for AppNavi's missing ivi surface. A prior run on
  the same pixman headless compositor, without ApplicationManager, reached surface_create for
  ids 3000, 30000 and 4903 with 26 attach calls, proving a client can create ivi surfaces and
  attach buffers here without any DRM interface.
- That also settles the 3000 against 30000 question: AppNavi creates both ids, plus 4903 and
  4900 for the map widget.
- The working harness used the valet-stub probe and runner, both still in the image, so the
  next step is to diff that harness against the current probe to find what is missing.

## 2026-10-29 — correction: AppNavi does create surfaces
- Withdrew the earlier conclusion that AppNavi never creates its ivi surface. That conclusion
  came from counting markers in the client's Wayland debug log, but the client does not emit
  those requests in this build, so their absence there was never evidence.
- Counting the compositor log for the same run shows two surface creations, seven ivi surface
  references, and attach and commit calls. AppNavi does render.
- The recipe that reproduces this is the one the retained milestone used: the gpio440
  adaptor, the valet-status D-Bus boolean stub, and the widget-linking helper replacing the
  plain foreground helper.
- The open question therefore moves from surface creation to visibility: whether a foreground
  request reaches the surface ids that exist and on which plane.

### (other lineage, same date)

- Withdrew the earlier published claim that AppNavi never calls ivi_application.surface_create.
  It rested on marker counts from the client Wayland debug log, which does not emit those
  requests in this build, so their absence there proved nothing.
- Compositor-log counts for the same run show two surface creations, seven ivi surface
  references, and attach and commit calls, so AppNavi does render.
- The reproduction uses the gpio440 adaptor, the valet-status D-Bus boolean stub and the
  widget-linking helper, matching the retained milestone. The open question becomes
  visibility rather than surface creation.

## 2026-10-29 — visibility requests issued but never bound to a surface
- Counted visibility markers in the compositor log during the valet-stub run: sixteen
  set_surface_visible calls, sixteen set_visible_for_qtwayland calls, eight foreground
  requests and sixteen layout calls, but zero ivi_surface_visibility events.
- The only surface id logged as created is 30000, whereas the helper programmes visibility for
  3000. The requests are therefore issued correctly and never bind to a surface that exists,
  which matches the manager continuing to report drawing application 0.
- The 3000-versus-30000 discrepancy is consequently promoted from a suspicion to the leading
  explanation, now backed by the visibility event count rather than by inference.
- The next step is to establish how the environment value maps to the created id, then either
  point the helper at the id that exists or make AppNavi create the id the helper expects.

### (other lineage, same date)

- Compositor-log counts during the valet-stub run show sixteen set_surface_visible and sixteen
  set_visible_for_qtwayland calls, eight foreground requests and sixteen layout calls, but
  zero ivi_surface_visibility events.
- The only surface id logged as created is 30000 while the helper programmes visibility for
  3000, so the requests never bind to a surface that exists, matching the manager reporting
  drawing application 0.
- The id discrepancy is therefore the leading explanation, supported by the event count. Next
  step is to establish the environment-to-id mapping and align the two.

## 2026-10-29 — surface id fixed at 30000 regardless of the environment variable

- Ran AppNavi with QT_WAYLAND_SET_SURFACE_ID set to 0 and the created surface id was still
  30000, identical to the run with 3000. The variable therefore does not determine the id in
  this path.
- Combined with the earlier marker counts this closes the diagnosis: AppNavi creates surface
  30000 and attaches buffers, the helper programmes visibility for 3000, and sixteen
  set_surface_visible calls consequently produce zero ivi_surface.visibility events.
- The fix is to address the id that exists, by rebuilding the widget-linking helper with
  parent 30000, which is cheaper than establishing where 30000 originates and making it
  configurable.

## 2026-10-29 — surface id fixed at 30000 regardless of the environment value
- A run with QT_WAYLAND_SET_SURFACE_ID set to 0 still produced surface id 30000, identical to
  the run with 3000, so the variable does not determine the id in this path.
- Together with the visibility marker counts this closes the diagnosis: AppNavi creates 30000
  and attaches buffers, the helper programmes visibility for 3000, and sixteen visibility
  requests yield zero visibility events.
- The fix is to address the id that exists, by rebuilding the widget-linking helper with
  parent 30000 rather than trying to make the client create 3000.

## 2026-10-29 — retargeting the helper to 30000 does not produce visibility
- Rebuilt the widget-linking helper with parent id 30000 and ran it through the same harness.
  The visibility request counts were unchanged at sixteen set_surface_visible and eight
  foreground requests, and ivi_surface.visibility events remained at zero.
- The conclusion recorded is that addressing the id that exists is necessary but not
  sufficient. The mismatch was real, but some further condition governs whether the window
  manager emits a visibility event for this surface.
- Candidate causes were written down in cost order: the helper's requests possibly not reaching
  the owning window-manager instance, its log being empty throughout and therefore suspicious;
  visibility requiring a later state change such as another commit or a layout change; or 30000
  not being the parent surface at all.
- The next discriminator is to confirm the helper connects and its first request is accepted,
  by capturing both its output and the compositor's response.

### (other lineage, same date)

- The widget-linking helper was rebuilt with parent id 30000 and run through the same harness.
  Visibility request counts were unchanged and ivi_surface.visibility events remained zero.
- Addressing the id that exists is therefore necessary but not sufficient; some further
  condition governs whether the window manager emits a visibility event for this surface.
- Candidates recorded in cost order: requests not reaching the owning window-manager instance,
  whose log has been empty; visibility requiring a later state change; or 30000 not being the
  parent surface. Next step is to confirm the helper connects and its first request is accepted.

## 2026-10-29 — correction: visibility is granted
- Withdrew the published claim that no visibility events are emitted. The compositor logs
  ivi_surface@7.visibility(1) twice; the earlier zero came from searching a different string.
  This is the second marker-string error in this investigation and both are recorded.
- Also noted that the harness runs without an ApplicationManager, so its empty manager query
  proves nothing, and that the retained milestone screenshot shows genuine map pixels.
- The standalone harness therefore already reaches visible authentic AppNavi rendering, and the
  remaining gap is integration into the full launcher chain rather than rendering itself.
- Next: carry the gpio440 adaptor, the valet-status D-Bus boolean stub and the widget visibility
  helper into the full chain and observe whether the manager latches the navigation window.

## 2026-10-29 — physical HID is dropped by the shell
- Explained the reported mouse and keyboard behaviour from the firmware. The weston configuration
  selects ias-backend with ivi-shell and has no input section; the backend supports pointer,
  keyboard and touch fully, and udev is stock apart from a touchscreen symlink rule.
- ivi-shell contains no pointer or keyboard focus implementation, so the cursor is drawn by
  virtue of a pointer seat existing but is never moved and never focuses a surface, and keys are
  dropped for lack of a focus surface. The caps-lock LED change on plug-in is device-open LED
  state rather than key handling.
- Input therefore has to be simulated at the touch layer, which is where the project's input
  helpers already aim.

## 2026-10-29 — correction: visibility is granted and the harness has no ApplicationManager

- Withdrew the claim that no visibility events are emitted. The count came from searching for
  ivi_surface_visibility, whereas the compositor logs ivi_surface@7.visibility(1) twice, so the
  surface is in fact made visible. This is the second occasion in this investigation where a
  wrong marker string inverted the conclusion, and both are now on record.
- Noted as well that this harness deliberately runs without an ApplicationManager, so its empty
  manager query says nothing about the manager's view; the earlier drawing-application-zero
  observation came from a different configuration.
- With the retained milestone screenshot showing genuine map pixels, the standalone harness
  already reaches visible authentic AppNavi rendering.
- The remaining gap is therefore integration rather than rendering. The full launcher chain
  starts AppNavi through AppLauncher with different environment and ordering, and does not
  reproduce this harness's ingredients.
- The next step is to carry the three essentials into the full chain: the gpio440 adaptor, the
  valet-status D-Bus boolean stub, and the widget visibility helper.

## 2026-10-29 — physical HID identified as dropped by the shell

- Investigated the reported behaviour that a mouse pointer appears but never moves and a keyboard
  is ignored. The weston configuration selects ias-backend with ivi-shell and contains no input
  section, while the backend itself fully supports pointer, keyboard and touch through libinput
  and libevdev, and udev is stock apart from a touchscreen symlink rule.
- The gap is ivi-shell, which contains no pointer or keyboard focus implementation at all; the
  only keyboard logic in the window manager concerns the on-screen keyboard surface.
- Consequently the cursor is drawn because a pointer seat exists, but nothing moves it or grants
  pointer focus, and keys are consumed by the compositor with no focus surface and dropped. The
  caps-lock LED change on plug-in reflects device-open LED state rather than key handling.
- The consequence recorded is that input has to be simulated at the touch layer, which the GUI
  accepts, rather than by presenting a mouse or keyboard. A short VM experiment with the existing
  input helpers would confirm this at runtime.

## 2026-10-29 — USB root test plan written, private

- Wrote a lab procedure for the owner's own head unit covering the three USB vectors worth
  testing. It is held privately because it contains an exploit payload; the public mirror keeps
  the status-only V-006 entry.
- The serial-injection payloads were validated at the shell level against the exact command the
  firmware builds, and checked against both real filters: the 126-character descriptor limit,
  the 0x20 to 0x7f charset, the comma rejection and the whitespace rewriting.
- The useful two-stage result is a credential overwrite: /etc/shadow is a symlink into /tmp, so
  a root command writing the shipped field layout with an empty hash, combined with securetty
  already permitting root on ttyS2, gives an interactive root login over the serial console. The
  change lives in tmpfs and is cleared by a reboot.
- A drafting error was corrected before committing: the first payload used passwd field order
  against the shadow file. The shipped line is now mirrored exactly.
- Hardware guidance was recorded. An ESP32-S3 running TinyUSB is the right tool because the
  trigger requires an arbitrary interface class of 06/01/01 or ff/ff/00, which stock Pi Zero
  gadget functions cannot present. USB Ethernet is supported by the kernel but useless alone
  since the image has neither a DHCP client nor a remote-login daemon.
- The recommended first step is to pass the device through to QEMU so the real automounter,
  udev and payload path are exercised before the vehicle is involved.

## 2026-10-29 — live ESP design for interactive root over USB

- Reworked the USB plan for a reprogrammable ESP. Because descriptors are fixed at enumeration
  and TinyUSB can re-enumerate in software, changing the payload becomes a live operation, so the
  approach turns from a blind one-shot into an interactive channel.
- Two findings made the interactive form possible. First, the payload can end with a comment so
  that the template's trailing ampersand is swallowed, leaving the injected command as system()
  foreground child, which allows a shell payload. Second, the kernel has USB ACM as a module, so
  a CDC-ACM interface provides a data channel without requiring the automounter to mount
  anything.
- That second point matters because the automounter's filesystem strings cover only ntfs, exfat
  and ext4, so a FAT volume presented by a microcontroller is not obviously accepted, whereas an
  ACM node needs no mount at all.
- The composite descriptor was specified as a vendor-specific interface to satisfy the branch
  test, a CDC-ACM interface for the data channel, and the payload in iSerialNumber, with three
  payloads validated for length and charset including an interactive root shell.
- A drafting error was caught by the validator: a stray space in one probe payload would have been
  rewritten to an underscore. The corrected form has no spaces.
- Caveats were recorded about module autoloading, the device-add timing relative to the automount
  service, and the fact that an open shell blocks the automounter.

## 2026-10-29 — USB test plumbing added, disk exhaustion blocks further runs

- Added an opt-in extra-device argument to the VM harness so research runs can attach additional
  QEMU devices, keeping flag and value pairs together and rejecting multi-line arguments, with two
  tests covering it.
- The reason is that QEMU's usb-serial model accepts a serial property that sets iSerialNumber on a
  vendor-class device, so the serial-injection path could be exercised without any hardware. The
  first attempt reached QEMU and failed for an environmental reason: the q35 machine in this
  configuration exposes no USB bus, so a controller must be added and the kernel USB modules loaded.
- The volume then proved to be completely full, with roughly five hundred megabytes free. The vendor
  workspace contains seventy per-experiment pre-run image backups totalling 2.4 terabytes apparent,
  which is what consumed the space. Deleting my own derived workspaces reclaimed only thirty-three
  megabytes because they were copy-on-write clones.
- One suite test now fails with no space left on device; that is the disk rather than the change, and
  the VM command tests pass in isolation.
- The backups were deliberately not deleted. They are pre-existing work from earlier sessions and
  pruning them is the owner's decision, with the recommendation being to retain the canonical image
  and a few checkpoints and archive the remainder externally.

## 2026-10-29 — disk investigation: the backups were clones

- Pruned the fifteen earliest superseded control-chain backups after ranking by usefulness, keeping
  seven images tied to retained milestones. The removal changed the apparent size by 480 GiB and
  freed no space at all, because those files are copy-on-write clones sharing their blocks with the
  canonical image.
- Local snapshots were checked and there are none, so nothing is pinning the blocks. The container
  is full across the machine rather than because of the project: application support, the Codex and
  codex directories, downloads and the research tree together account for the capacity.
- The earlier statement that the backups were the cause of the disk exhaustion is corrected here. It
  was inferred from apparent size rather than allocated blocks.
- Further VM work remains blocked until about fifty gigabytes is freed elsewhere, since more backup
  pruning cannot release anything.

## 2026-10-29 — the USB harness enumerates, and two of my own assumptions were wrong

- Worked through why the emulated serial adapter never appeared. Three distinct causes had been
  collapsed into one: a null chardev stops QEMU presenting the device at all, an EHCI bus is rejected
  outright for a full-speed device, and QEMU's xHCI oopses in the vendor's own driver. UHCI, a file
  chardev and a real wait are enough to get a stable enumeration with the serial string under control.
- The keyboard enumerating beside the adapter mattered: it proved the bus, the port reset and the
  enumeration path all worked, which shifted suspicion from the guest kernel to the device
  configuration. Without that control the oops would have looked like the whole story.
- Two corrections to my own reasoning from earlier the same day. First, the serial string does not
  reach a shell: `usb-automount` is a Qt and D-Bus service, and the documented V-006 mechanism is the
  MTP branch. Second, a null chardev is not an inert detail, it is the specific reason nothing
  enumerated, so the earlier observations of a device that never appeared were an artefact of the
  harness rather than of the guest.
- Practical consequence: reproducing V-006 needs an emulated MTP device with a crafted serial, plus a
  running system bus so the service stays alive long enough to act.

## 2026-10-29 — the mount service is alive, and the reason it never was

- Delegated the D-Bus question and got an answer with a control behind it rather than an assertion.
  The daemon was not blocked by policy; it was blocked by a password database that does not exist at
  boot, because `/etc/passwd` is a symlink into volatile storage. Supplying the two required entries
  lets the system bus come up, and `usb-automount` then holds `com.lge.car.automount` indefinitely.
- The control run is the part worth keeping. With the bus up and the password file absent the client
  still died in three seconds, which isolates the password database as the cause instead of leaving
  two plausible explanations stacked on top of each other.
- This changes the shape of the work. The mount request surface is now reachable in the VM, so the
  remaining V-006 question is about the MTP branch's processing of the serial string, not about
  getting a service to run at all.
- The symlink is interesting on its own account and went into the register as a candidate rather than
  a finding. What matters is the permission and ownership of `/tmp` on real hardware, which this
  environment cannot establish.

## 2026-10-29 — the injection sink is reachable and the exploit is not

- Two workers ran in parallel, one on the VM and one on static analysis, which worked because the
  static job needed no image access. Both came back with evidence rather than conclusions.
- The security result inverted the entry it was meant to confirm. The vulnerable `system()` call is
  reachable at runtime — proven by the shell complaining about the missing helper, which only that
  call can produce — but the string arriving there has already been reduced to an allow-listed
  alphabet by udev, so nothing resembling a metacharacter survives. The register had asserted the
  opposite, and that assertion is now withdrawn rather than quietly left in place.
- What made this decidable was the positive control: the same payload executed perfectly when handed
  straight to `/bin/sh`. Without it there were two candidate explanations for the silence, the payload
  and the sanitiser, and the wrong one could easily have been recorded as fact.
- The through-line of the day is that three separate things I had treated as working were not: the
  serial device never enumerated, the mount service never started, and the injection could not reach
  the sink. Each had a specific, findable cause, and each had been masked by an earlier assumption.
- On the HMI question the analysis reframed the problem. The VM has never run the authentic init
  chain, so the missing `/tmp` state that keeps breaking services is a symptom of the harness rather
  than a series of unrelated faults. The display is the hard blocker: the vendor compositor wants an
  Intel i915 CRTC that nothing in the VM provides.

## 2026-10-29 — display architecture decided, and the analysis corrected by it

- The gap analysis proposed that a generic DRM node with software rasterisation would satisfy the
  vendor compositor. Reviewing it against the kernel tree and the backend binary rejected that: the
  backend carries Intel-specific paths, so a plain card node is not the device it wants. The decision
  is to replace only the backend's output path with a software implementation, keeping stock weston,
  the IVI modules and the IAS protocol intact.
- The value of asking for a decision rather than a menu showed here. The cheap option, a virtual KMS
  module, looked attractive on paper and would have consumed weeks before revealing that GBM, scanout,
  planes and vblank are the actual work, not device registration.
- What this buys is a path that can plausibly be called the infotainment system running in a VM,
  rather than a headless compositor standing in for it. The distinction matters because the IAS control
  path is part of what is being studied.
- Recorded risk, for cheap falsification next: that the IVI modules depend only on the Weston backend
  ABI and the `ias_crtc` interface. One run with the software backend and a `wrandr --crtc=1` call will
  settle it.

## 2026-10-29 — the real init chain runs, and dies on a kernel fault

- Booting the authentic esinit rather than the research shim changed the diagnosis again. Everything
  the services had been complaining about, the missing password file, fstab, weston configuration,
  turned out to be produced correctly by esinit in seconds. The harness had been feeding the system
  nothing and then attributing the resulting failures to individual services.
- The new blocker is deeper and more interesting than any of those. A vendor module, loaded by a
  vendor script during init, dereferences a null pointer on non-vendor hardware and orphans a lock on
  the platform bus. Every subsequent platform driver then waits forever, and because the hung-task
  detector is compiled out, nothing is printed. Progress looks like silence.
- What made the silence readable was the pair of controls: the same module loads fine on a clean guest,
  and a non-platform module still loads after the oops. That narrowed a whole-system stall to one bus.
- The MICOM work moved from folklore to a contract. The 35 bytes are the answer, not the question, and
  the framing is a five-byte header with an XOR checksum. The honest part of that document is the
  weakest link it names: static evidence cannot separate two readings of why the daemon stays silent,
  and one hex dump would settle it.
- Also corrected a housekeeping error of my own: the repository ignores `/work/`, so the analysis
  documents I believed I had committed were not in the repository at all. They are now under
  `evidence/vm-bringup/`.

## 2026-10-29 — systemd at last, and a quieter kind of finding

- Suppressing one module load was enough to let the authentic boot reach systemd, which reframes the
  whole bring-up: the vendor userspace has been ready to run for some time and one driver asserting
  hardware presence was holding it shut. Doing it on a CoW clone kept the canonical image untouched.
- systemd then failed in the least interesting place, the fstab. A projection with one partition cannot
  satisfy units that want `mmcblk0p8`, and systemd behaves exactly as documented: dependency failure,
  emergency mode, no drama. That is a good sign — the failures are now ordinary and legible rather than
  silent kernel faults.
- On the security side the valuable find was the least dramatic one. The MTP injection is dead, the
  kernel oops turned out to be unreachable, and what remains is a mount performed without `MS_NODEV`.
  No bug, no clever string, just a flag that lets a device node from a plugged-in filesystem reach
  storage that file permissions were supposed to protect.
- Worth noting the shape of that: three candidate attacks were investigated today and two dissolved
  under evidence, while the one that survived was visible in a constant at a single offset. Evidence
  keeps selecting for the boring answer.

## 2026-10-30 — a real media corruption path, and another scope correction

- The shipped ASF demuxer accepted a 33rd stream into a fixed 32-entry array and crashed authentic
  `gst-discoverer-1.0`. This is the first current-build parser memory-corruption condition reproduced
  dynamically rather than inferred from a version string. It is V-012 because V-011 was already
  assigned concurrently to the missing-`nodev` mount finding.
- A source-layout reconstruction shows the first out-of-range `AsfStream` aliases the live
  `flowcombiner` pointer with a newly allocated `GstPad *` and corrupts several fields of
  `old_stream[0]`. The file does not directly supply those pointer values, so the result is a strong
  crash primitive, not yet an attacker-chosen write or code-execution proof.
- Authentic thumbnail and PlayerEngine services were started as root and their D-Bus methods were
  recovered. Bounded calls failed before ASF pad creation in the incomplete VM media environment.
  Production-service reachability is therefore still open rather than being inferred from the library
  link alone.
- The previous missing-`nodev` interpretation was also narrowed. The automounter accepts vendor
  `tntfs`/`texfat`; FAT/exFAT cannot natively store POSIX device inodes, Tuxera's NTFS special-file
  semantics are untested, and a local process must still open the node. V-011 remains a hardening
  defect and post-execution candidate, not a proven first-step USB root path.

## 2026-10-29 — the vendor system boots

- Multi-user, first time. The two things holding it back were both trivial to look at and easy to miss:
  a mount check script shipped without an execute bit, and a partition layout the projection did not
  provide. After those, systemd did what systemd does, and the log reads like an ordinary embedded
  boot rather than a research harness.
- Worth recording what this changes. Until now every service failure had a plausible excuse, the
  harness had not prepared the ground. That excuse is gone. What fails now fails for its own reasons,
  on a system that booted the way the vendor intended.
- The two survivors are the ones the analysis predicted: no MICOM daemon, and no compositor. Both are
  now specific engineering tasks with named files rather than open questions.
- The `Requires=` on `micommanager` is worth noting as a design observation: the launcher cannot come
  up without the vehicle interface daemon, so the simulator is not a nice-to-have for the HMI path, it
  is the gate.

## 2026-10-29 — the MICOM speaks, and it speaks first

- The question the contract could not answer statically was whether the daemon waits for the vehicle
  before it talks. With a real serial boundary on the now-booting system it emitted 103 valid frames
  immediately. It does not wait. A silent peer is enough to reach the ask stage, which means the
  simulator is a listener that answers rather than something that must pretend to boot.
- Every frame checksummed correctly, which is worth more than it sounds. A protocol transcribed from
  disassembly that produces 103 frames with zero XOR errors on first contact was understood correctly.
  That confidence is what makes the remaining question tractable.
- The command ids are now known from traffic rather than inferred from code, including the ids that
  appeared exactly once at startup. The one thing still missing is which id is the boot-info ask, and
  the launcher's own call order narrows it to two candidates.
- A worker on this task was cut off mid-sentence and produced nothing. Rather than present the round as
  organised work, the measurement was taken directly and the record says so.

## 2026-11-01 — exact parser and backport evidence replaces version guesses

- A new offline harness now exercises the recovered commercial Tuxera modules
  against project-local raw images without mounting them on the host. QEMU opens
  parser inputs read-only, the guest uses `ro,nodev,nosuid,noexec`, and the
  canonical root remains snapshot-backed. Sixteen malformed exFAT fixtures
  produced no detected kernel fault; that is a bounded negative result, not a
  parser-safety claim.
- The clean NTFS control settled V-011's central filesystem question. Exact
  Tuxera NTFS retained a character node across remount. Without `nodev`, a
  process reduced to uid/gid 65534 under SMACK `_` opened the harmless QEMU
  `/dev/null` target; with `nodev`, VFS denied it. The omission therefore has a
  real policy effect, while still not providing execution, a useful target, or
  a first-step root path by itself.
- The old kernel banner was again a poor vulnerability oracle. Direct binary
  checks found the Dirty COW fix, both ranked AF_PACKET locking fixes, and the
  1 MiB Stack Clash guard-gap backport in the recovered `4.1.27-abl` image.
  Those four local-root candidates are rejected for EU `260128`; no substitute
  local-root path was claimed.

## 2026-11-01 — one reachable local UAF candidate, without calling it root

- Exact `snd-seq.ko` instructions show that the CVE-2017-15265 use-lock fix is
  absent. A small freestanding diagnostic then established the practical entry
  boundary: uid/gid 65534 can open the mode-0644 sequencer node and complete a
  client-ID/create/delete sequence in the offline vendor-kernel VM.
- The deliberately bounded race is equally important evidence. Two processes
  issued 200,000 create and 400,000 delete attempts without a kernel fault. That is
  not proof of safety and does not override the missing lifetime operation, but
  it prevents the report from turning a static UAF mechanism into a claimed
  exploit. V-013 is a local memory-safety candidate; root remains unproven.
- The same exact-code discipline split two other candidates cleanly. The
  CVE-2016-0728 keyring reference release is backported, so that path is
  rejected. The CVE-2017-1000112 IPv4/IPv6 UFO guards are absent, so that bug is
  retained, but `CONFIG_USER_NS=n` blocks the published unprivileged root setup
  and production UFO interface reachability is unknown.
- The tracked sequencer tool performs only one benign create/delete operation,
  keeps QEMU offline and snapshot-backed, and records a machine-readable
  classification. The race source and all generated binaries/logs remain in
  ignored `work/`; no exploit payload was added to the repository.

## 2026-11-01 — adjacent ALSA candidates separate code from usable access

- The next PCM candidate dissolved under the same exact-code check. Shipped
  `snd-pcm.ko` takes the per-device open mutex around `snd_pcm_info_user`, which
  is the complete CVE-2017-0861 fix. Another version-derived root candidate is
  therefore rejected.
- CVE-2018-1000004 went the other way at the instruction layer: the shipped
  native ioctl path lacks the later Linux 4.1 per-client serialization. But its
  published sequence needs `write()` to the sequencer pool, and recovered
  intended node mode gives ordinary users no write permission. V-013 ioctls
  working through a manually modeled `O_RDONLY` descriptor do not silently imply
  this sibling trigger is reachable.
- This is a useful three-way outcome from one subsystem: one exact UAF candidate
  with ioctls reachable through `O_RDONLY` (V-013), one exact fix (CVE-2017-0861), and
  one path missing the official serialization whose required access is blocked
  by DAC (CVE-2018-1000004). None is promoted to root.

## 2026-11-01 — PlayerEngine reaches the ASF bug, and the binary corrects the source model

- The earlier PlayerEngine failure was two independent setup errors: a flat JSON
  option that the service does not accept, and QEMU's missing `media_mixer` PCM.
  With the nested audio option and a disposable ALSA-null mapping for the stock
  PCM name, a valid WMA returns true and reaches the authentic ASF demuxer.
- The boundary controls are now clean. One stream and 32 streams survive under
  the same environment. A 33-stream file and a 34-stream file both terminate
  the uid-0 PlayerEngine service with signal 11. A plain path still fails while
  the `file://` URI succeeds, so the prior confounded URI conclusion is retired.
- The service's own crash handler recorded the useful transition:
  `g_queue_push_head+0x1d` called from `libgstasf.so+0xb6cc`. Exact plugin
  instructions show that `+0xb6cc` is the return from
  `gst_flow_combiner_add_pad` after loading the corrupted combiner pointer.
- Exact binary layout also overturned one source-only detail. The vendor stream
  stride is 208 bytes rather than public 1.8.3's 200. The 33rd stream zeros the
  low half of `flowcombiner`; its pad pointer overwrites `old_stream[0]` instead
  of becoming the combiner pointer itself. That is why offsets remain
  binary-derived facts, even when public source explains the control flow.
- Nothing in this run demonstrates instruction-pointer control or RCE. Manual
  D-Bus service reachability is now closed; automatic USB indexing,
  LightMediaScanner, thumbnail handoff, and physical-unit behavior remain open.

## 2026-11-01 — the automatic scanner takes a different ASF path

- Putting the 33-stream file under `/media/usb/probe` answered the next routing
  question. LightMediaScanner's configured startup scan found the USB directory,
  processed one file with zero reported errors, committed it, and stayed alive.
- The parser identity explains why. The registered `asf.so` is a separate
  LightMediaScanner metadata parser that reads with `open`/`read`/`lseek` and
  writes to SQLite through scanner APIs. It neither links GStreamer nor imports
  a `gst_*` function, so accepting this file does not reach V-012's `asfdemux`.
- A full session-bus capture showed only the scanner's D-Bus lifecycle,
  properties, explicit scan, and progress traffic; no PlayerEngine or thumbnail
  call appeared. That narrows the remaining automatic route to post-index
  media-manager/browser, playback, or thumbnail behavior.
- This is negative evidence for one route, not a safety claim for removable
  media. The exact file still kills PlayerEngine when sent manually under the
  established service contract.

## 2026-11-01 — a different udev helper boundary restores a static physical root path

- A deterministic privilege-surface scanner first reduced the recovered tree to
  reviewable facts: no host-visible or archive setuid/setgid entries, 102
  service files (101 using default root identity), 129 writable-executable-mode
  files mostly on normally read-only `/navi`, and 46 permissive/non-root udev
  rule assignments. The scanner records extraction and xattr limitations rather
  than treating host metadata as production truth.
- Online CVE triage tied to the exact shipped helpers identified
  CVE-2026-40225. Vendor `v4l_id` prints `v2cap.card` directly as
  `ID_V4L_PRODUCT`; vendor `scsi_id` prints `unit_serial_number` directly as
  `ID_SCSI_SERIAL`. Exact disassembly shows neither control-character guard
  added by the upstream 2026 fixes.
- The installed rules complete the static chain: hardware events invoke those
  helpers, block devices receive the systemd tag, and the generic removal rule
  executes `REMOVE_CMD`. More importantly, the image ships
  `debug-shell.service`, configured as an unauthenticated `/bin/sh` on
  `/dev/tty9` under the system-service default root identity, conditional on
  that device path existing. The advisory's SCSI
  `SYSTEMD_WANTS` route can therefore request an existing root unit rather than
  install one.
- Version evidence is intentionally not simplified. The PID 1 banner/pkg-config
  say `225`; embedded OpenEmbedded paths say `systemd/1_249.3-r0`. The finding
  rests on exact instructions and installed rules, not either version label.
- A bounded offline VM control then closed only the unit's path condition:
  `/dev/tty9` existed as `root:root` mode `0600`, character device `4:9`, under
  the recovered vendor kernel/userspace and research init. The service was not
  started and no udev property was injected.
- This became V-014, the strongest static physical root path in recovered EU
  `260128`. It is not a head-unit reproduction: no malicious device, injected
  authentic udev event, systemd unit request, VT9 interaction, root command,
  persistence, or applicability to the owner's unknown installed firmware was
  demonstrated.
- V-006 remains rejected as originally claimed. Its `usb_id`
  `ID_SERIAL_SHORT` allowlist does not protect the separate `v4l_id`/`scsi_id`
  line-oriented property boundary, so the two findings are not contradictory.

## 2026-11-01 — the exact udev parser retains the benign second property

- A new fixed-input diagnostic isolated the next V-014 boundary without running
  either vulnerable helper or any service. It hash-verified the recovered
  `udevadm` and `systemd-udevd`, installed one temporary rule and synthetic
  helper in the snapshot-backed VM, and invoked only `udevadm test` against the
  existing emulated root block device.
- The helper emitted `ID_SCSI_SERIAL=V014_BENIGN_CONTROL` followed by
  ` SYSTEMD_WANTS=v014-benign-nonexistent.service`, including the advisory-
  relevant leading ASCII space. Authentic test output recorded that raw line and
  retained a normalized separate `SYSTEMD_WANTS` property.
- The marker unit was verified absent, no udev daemon or systemd manager ran, no
  kernel uevent was sent, and the temporary helper, rule, and log were removed before
  completion. Classification was `benign-second-property-retained`.
- This closed downstream import-parser semantics only. Hardware delivery through
  SCSI, execution of shipped `scsi_id`, authentic udevd persistence, systemd
  device activation, the root-shell unit, and interactive VT9 remained untested
  at that checkpoint.

## 2026-11-01 — matched controls confirm synthetic benign unit activation

- A second fixed-input diagnostic handed PID 1 from the research shell to exact
  recovered systemd, started exact systemd-udevd through installed sysinit, and
  requested one synthetic add event for emulated `mmcblk0` after coldplug settled.
- Before coldplug, transient `/run` masks shadowed the installed persistent-
  storage and V4L helper rules. The root was remounted read-only, QEMU remained
  NIC-free and snapshot-backed, and the only property-selected unit was a
  transient BusyBox touch/echo marker with no shell command.
- The negative run stored fixed `ID_SCSI_SERIAL` but no `SYSTEMD_WANTS`; the
  marker remained absent/inactive. The positive run stored fixed
  `SYSTEMD_WANTS=v014-benign-marker.service`; PID 1 logged the unit starting and
  marker-file plus active-state checks passed. Root remained read-only in both.
- This closes the synthetic udevd database/device-unit and manager-activation
  boundary. Hardware bytes reaching shipped helpers, physical hotplug, the
  installed shell-unit request, production VT9 access, and root remain untested.

## 2026-11-01 — exact thumbnail routing corrects the V-012 media boundary

- Exact MediaBrowser code maps public `requestThumbnails(as)` to the session-bus
  destination `com.lge.thumbnailextractor`, object
  `/com/lge/thumbnailextractor/service`, interface
  `com.lge.thumbnailextractor.service`, method `Start(as)`.
- Exact extractor code queues every `Start` path and selects `VideoContext`
  without an extension branch. The earlier inference that `.wma` selected the
  audio/TagLib context was corrected; that context handles cover-art work.
- Exact `libthumbnailextractor.so` builds an `uridecodebin ... appsink` pipeline.
  Its custom autoplug callback excludes only factory names beginning with `mfx`,
  so the shipped vulnerable `asfdemux` remains eligible.
- The recovered edge is explicit but request-driven. Reviewed scan callbacks
  forward progress/file events without requesting thumbnails. Bounded VM
  attempts did not observe service-name acquisition, a delivered `Start`, an ASF
  plugin map, cache output, or a natural crash.
- This strengthens static post-index reachability while preserving the dynamic
  boundary: automatic USB/UI invocation and thumbnail-process corruption remain
  unproven; manual uid-0 PlayerEngine remains the only dynamically confirmed
  production-service V-012 route.

## 2026-10-29 — the dependency was never a dependency

- The launcher's hard requirement on the MICOM daemon looked like the central problem: satisfy a serial
  protocol correctly enough to keep a vendor daemon alive. It turned out that the daemon starts perfectly
  well when the device node it opens exists. The failure had been the environment, not the contract, and
  the whole reply-simulator effort was set aside as unnecessary for this gate.
- That is the third time in this project that a blocker attributed to a service was really the harness
  failing to provide something. The pattern is consistent enough to be a rule now: before believing a
  vendor component is broken, check whether it was ever given the thing it opens.
- What is left is honest and specific. The UI process needs a compositor, and nothing in this image
  starts one, because the vendor starts weston from its own init branch behind an SPI validation that
  emulation fails. The remaining work is to create that runtime environment deliberately.
- Two workers were dispatched and neither returned anything. Rather than dress that up, the records note
  it, and the round's actual finding came from an existing log.

## 2026-10-29 — the UI connects

- The compositor turned out to be a non-problem. The image ships a headless backend next to the Intel
  one, so the vendor's own weston runs with no DRM device at all, and the socket appears. The build
  that had been estimated in weeks was unnecessary for reaching the next gate.
- The UI process then did the thing that matters: it stopped complaining about the display. That single
  changed line, an error that is no longer printed, is the first evidence that the vendor stack is
  talking to itself rather than to a substitute.
- Two failures along the way were both configuration, not capability: weston wanted a shell this
  product does not use, and the IAS shell wanted a config path that `HOME` normally supplies.
- The remaining gap is now narrow and named. The shell needs its configuration to initialise outputs,
  and scanout still has to become real for anything to be seen.

## 2026-10-29 — the shell comes up, and a permission boundary turns out to be thinner than stated

- The IAS shell now initialises with its own configuration. The detail that mattered was unglamorous:
  the config is read from `$XDG_CONFIG_HOME/ias.conf` directly, and the vendor ships it one directory
  deeper, so the value of that variable is what makes the difference. Renaming the CRTC to the headless
  output's name was the other half.
- The security question of the day resolved against optimism. `/media` is a plain tmpfs with defaults
  and nothing sets a mode, so the kernel default applies and it is very likely world-writable. The
  earlier entry leaned on "probably 0755 root" as reassurance; that assumption is gone and the entry now
  says so.
- What survived is worth stating plainly: the mount lacks `nodev`, and node permissions are chosen by
  whoever built the filesystem. That combination is a boundary failure regardless of how tidy the rest
  of the permission model is.
- Escalation still requires physical access. Being accurate about that matters as much as being accurate
  about the defect.

## 2026-10-29 — the interface is live, the pixels are not

- The compositor answered for itself today: the IAS shell interface appears in the registry and an
  output exists. That is the strongest statement available while running headless, and it means the
  vendor control path is coherent — the thing this project actually wants to study.
- The scanout question closed in the least dramatic way: the kernel simply has no driver that could
  provide a framebuffer on this virtual hardware. i915 is built in and binds nothing, and every fbdev
  and virtual GPU option is compiled out. No amount of configuration was going to produce an image.
- Worth noting there were no failures to chase here. Reading the config answered in a minute what
  experiments could have circled for hours, and it retired an option that looked cheap.
- The boundary is now precise: the system runs, its interfaces are live, and the only thing missing is
  a device that can present pixels. That is a well-posed problem rather than a vague one.

## 2026-11-01 — exact package recovery exposes a conditional DHCPv6 parser path

- Recovered the firmware's RPM package inventory from its Berkeley DB rather than
  inferring component age from strings. The preserved index contains 1,679
  records, including the exact vendor ConnMan package identity.
- Version matching produced a lead, not a conclusion. Exact `connmand`
  instructions then confirmed CVE-2026-115863's fixed-size DOMAIN_LIST copy,
  unbounded label walk/store, and option-24 dispatch.
- The main reachability question narrowed from generic Wi-Fi speculation to a
  specific conditional path: a connected ConnMan network accepts RA flag state,
  starts the DHCPv6 information request, and asks for the affected option. Live
  transaction and client/server identifiers remain required.
- The service is configured for uid 0, but the binary also carries PIE, NX stack,
  a stack canary, and full RELRO. No traffic was generated and no process was
  crashed. The result is a static adjacent-network candidate, not root access.
- Added deterministic dump tooling and kept the database, source, downloads,
  disassembly, and decompiler output in ignored `work/`. Physical and dynamic
  validation remains deferred until a disconnected bench exists.

## 2026-11-01 — both PCB-selected Bluetooth daemons retain an old BNEP parser

- The product does not ship one generic Bluetooth binary. Its setup script reads
  MICOM PCB state: versions 11/12 select BSA `00.63.00` with one of two
  controller patchrams; other values select BSA `00.51.00` and a third patchram.
- Exact comparison avoided relying on either BSA version. Both exported
  `bnep_process_control_packet()` implementations read the extension/control
  bytes before the remaining-length checks later added for CVE-2017-0782. The
  same pre-fix order persists in later multi-byte control fields.
- The daemon unit is enabled with a configured uid-0 default, while recovered
  policy intends `App::bluetooth`. Contrary reachability evidence matters:
  both engineering profiles say `PAN : N/A`, startup calls `BNEP_Init`, and no
  direct `BNEP_Register` reference was found. The parser is therefore dormant
  pending evidence of indirect/runtime registration. Adapter state, pairing/
  authorization, accepted channel, and controller byte preservation remain unknown.
- No Bluetooth process, adapter, pairing, packet, malformed input, crash, or
  disclosure was used. V-019 records exact conditional parser behavior without
  promoting Android's generic critical-RCE rating to a vehicle exploit claim.

## 2026-11-01 — Dropbear package remnants do not form a listener

- The RPM inventory's Dropbear version initially looked like another old daemon
  candidate. Filesystem reconciliation changed the conclusion: there is no
  `dropbear` or `dropbearmulti` executable, socket unit, host-key service/key, or
  enable link in recovered `260128`.
- The remaining template documents intended per-connection socket mode with
  passwords disabled. Its pre-start script would overwrite root's authorized
  keys with one shipped static public key, while the default does not disable
  root public-key login. That is latent trust material, not usable authentication
  without the private key and a restored server/socket chain.
- The default init branch creates the template's condition marker, so the marker
  is not the decisive blocker. Missing executable and activation dependencies
  are. No process, port, banner, or login was exercised.

## 2026-11-01 — exact wpa_supplicant code rejects two version-derived P2P findings

- The recovered package and binary advertise wpa_supplicant 2.5, but exact
  instructions contain later security backports. In `p2p_add_device()`, the
  every SSID copy is gated on the peer-controlled element length being at most 32,
  matching the CVE-2015-1863 fix.
- CVE-2021-27803 required a more careful control-flow comparison. The recovered
  Provision Discovery Request handler calls `p2p_add_device()`, then on every
  successful return unconditionally calls `p2p_get_device(p2p, sa)` and replaces
  the old pointer. This is the fixed flow; it is not conditional on the prior
  pointer being NULL.
- P2P is still a real compiled surface. ConnMan contains peer, find, listen,
  provision-discovery, and GO-negotiation machinery, and an enabled path unit
  can conditionally launch supplicantmanager. This capability evidence does not
  undo the exact fixed-code conclusions or prove production radio exposure.
- No target process, interface, P2P discovery, frame, or malformed input was
  used. The next physical evidence is passive capture of installed hashes,
  marker/arguments, process label, interface ownership, and find/listen state on
  a disconnected bench.

## 2026-11-01 — exact fortification changes an old ConnMan overflow into an abort

- Followed the same package lead into CVE-2023-28488, but stopped at exact code.
  The shipped DHCPv4 receiver does retain the upstream pre-fix mistake: it checks
  the real read length for 28 header bytes, replaces that count with untrusted
  `ip.tot_len`, and subtracts 28 without checking the replacement again.
- Normal IPv4 acquisition does reach the affected L2 callback. The exact client
  start enters `INIT_SELECTING`; mode 1 opens and binds an `AF_PACKET` datagram
  listener and registers the reviewed receive function.
- The compiler materially changes the consequence. The copy is
  `__memcpy_chk(..., 0x274)`, and every selected checked-copy implementation in
  the recovered libc branches to `__chk_fail` before an underflowed size can
  write the stack object. This exact build therefore supports conditional daemon
  termination, not the generic stack-overflow/RCE claim.
- A packet-free model partitioned all possible 16-bit total lengths and read
  lengths up to the exact 656-byte cap. No socket, frame, target execution, or
  NIC-enabled VM was used. V-016 records the availability boundary and leaves
  production interface state and the owner's installed build for a disconnected
  bench.

## 2026-11-01 — cellular SMS decoding adds a separate conditional root-daemon surface

- The RPM inventory pointed to an old oFono build, but the package label was
  only the start. Exact `ofonod` instructions retain both missing destination
  checks fixed for CVE-2023-4233 and CVE-2023-2794.
- The route is product-specific rather than hypothetical upstream code. Two
  callbacks in the compiled LG QMI modem driver pass direct indications and
  stored/raw-read SMS data into `ofono_sms_deliver_notify`, then the affected
  deliver decoder.
- Exact layout narrows the generic advisory. The address path can write 257
  bytes into 23; deliver data can copy 255 into 140. Both can leave the local
  `sms` object, but neither maximum directly reaches this caller's canary. The
  deliver copy is plain `memcpy`, so the fortify result that constrained V-016
  does not apply here.
- The service would be uid 0 but executes under SMACK `App::tms`, and its unit
  is marker-gated. No recovered path-unit enable link was found. Activation,
  modem/QMI state, carrier delivery, dynamic corruption, RCE, and unrestricted
  root remain open rather than assumed.
- Added a packet-free arithmetic model, exhaustive tests, reviewed evidence,
  and a disconnected-bench observation plan. No target binary, modem input,
  PDU, packet, or privilege action was used.
- Fable remained unavailable. DeepSeek Flash's route doctor was static-ready,
  but native dispatch failed as an unknown model; no substitute model or failed
  output was used.

## 2026-10-29 — the control protocol, read out of the binary

- The IAS interface had been inferred from wrandr's help text. It is now read directly: five methods and
  four events on ias_crtc, one method on ias_mode, with signatures. The interesting part is how well
  they line up with wrandr — brightness, contrast, gamma, mode and transparency all present — which
  confirms the tool is the intended driver of this protocol rather than something adjacent to it.
- Getting there took a correction. The first parse produced nonsense because a pointer into the data
  section coincided with a relocation entry; resolving vaddr to file offset through the program headers
  fixed it. Worth remembering that a plausible-looking struct at the wrong address is still wrong.
- The slice is now specified before any code exists, including how it will be refuted: a CRTC in
  wrandr's listing, a successful enable, and a 1920x720 output seen by weston-info. Writing the
  falsification first is cheaper than discovering afterwards that a backend "ran" without proving
  anything.
- The blocker is unglamorous and immediate: pixman headers are absent, so the first build decision is
  where that small amount of header surface comes from.

## 2026-10-29 — the toolchain answers first, as it should

- Before writing a backend it was worth knowing whether one could be built at all: an arm64 host with no
  cross-gcc, targeting a 2015 embedded x86_64 userspace. The bundled zig does it, and the proof is an
  ELF file exporting the right symbol rather than an opinion about compilers.
- The remaining blockers came from reading the source's own include list. That is a minute of work that
  would otherwise have been an afternoon of compiler errors, and it named the one genuinely missing piece
  on this machine: there is no wayland-scanner here.
- The pixman skew is the kind of detail that silently poisons a result later. Headers newer than the
  runtime will compile cleanly and then misbehave in ways that look like a backend bug, so it is written
  down now, with the fallback stated.
- Also a small housekeeping correction: the scaffold was first written under work/, which this repository
  ignores, so it would have been lost from history. It now lives under tools/.

## 2026-10-29 — the tool was inside the image all along

- The missing dependency was shipped with the product. The vendor rootfs carries wayland-scanner, so the
  guest can generate its own protocol headers, and a host install that had been the obvious next step
  turned out to be unnecessary.
- Getting the output back out taught a harness lesson worth its own line: the guest writes to a
  throwaway overlay, so a file produced inside disappears with the snapshot. Nothing about that is
  visible from inside the guest, where the file plainly exists. The extraction that worked streams the
  bytes over the console instead.
- The integrity check mattered more than usual here, because console transfer is lossy in ways that are
  easy to miss — wrapped lines, echoed commands, prompts in the middle of data. The decoded size matching
  the in-guest size exactly, plus the expected count of interface definitions, is the difference between
  a header and a plausible-looking corruption.
- Two build items remain rather than four, and both are small.

## 2026-10-29 — it builds

- The first real artefact: a backend plugin for this 2015 embedded guest, compiled from an arm64 laptop
  with no cross-compiler installed. The undefined-symbol count is the detail that makes it a plugin
  rather than a binary — those 31 symbols are weston's, resolved when it loads us.
- Every dependency on the way was discovered by failing, in this order: config.h, wayland headers,
  a protocol header the tarball does not ship, xkbcommon, then pixman. None of those would have been
  guessed in advance, and each is now written down so the next build starts from them.
- Homebrew refusing wayland on macOS was the surprise. The formula is a Linux compositor library and the
  bottle system simply will not build it here, so the release tarball was the way in.
- The extraction channels were worth testing properly instead of trusting the first one. Console transfer
  looked fine at 8 KB and silently corrupted at 23 KB; the socket capture looked authoritative and ate
  bytes. Both would have produced a header that compiled and then behaved strangely, which is the worst
  kind of wrong.

## 2026-11-01 — oFono directionality changes what “reachable” means

- `sms_decode` does not defer work until its caller accepts the decoded type.
  Incoming TP-MTI selects deliver, submit-report, or status-report decoding and
  completes the selected copy first. The QMI delivery handler's later DELIVER
  check therefore cannot protect CVE-2023-4232 or CVE-2023-4234.
- The reverse distinction matters equally. Deliver-report and command decoders
  are selected only for `outgoing=TRUE`, so they do not belong to the ordinary
  incoming SMS route. Exact callers were found in transmit-queue deserialization
  and SIM-Toolkit Send SMS parsing. That establishes shipped routes without
  pretending they are unauthenticated radio paths.
- Exact instructions retain all six reviewed TPDU decoder bounds. The expanded
  arithmetic model quantifies each destination. Incoming-decoder maxima do not
  directly reach the reviewed delivery caller's canary; outgoing-only caller
  frames remain separate and unresolved. That narrows impact without erasing
  corruption.
- The QMI WMS list callback proved to be a separate boundary. It reads the TLV
  length but does not validate it. A vendor overflow diagnostic uses a wrapping
  32-bit product and then falls through to a four-byte allocation, while
  iteration follows the original count. This confirms V-018, but the controlling
  metadata comes from the modem, not directly from an SMS TPDU.
- Both results remain static and conditional: no modem input, QMI message, PDU,
  target execution, crash, payload, SMACK escape, or root transition occurred.

## 2026-10-29 — our backend, the vendor shell on top of it

- The compositor that came up is ours. The vendor's own weston loaded our module, the vendor's IAS shell
  layered onto it, and the registry filled with vendor interfaces. That is the architecture the display
  decision was aiming at, running.
- The build gap was a useful one: option parsing belongs inside the module, not in the executable. One
  undefined symbol, one file added to the compile.
- Worth noting what turned up unasked: a screenshooter interface. If the vendor stack can hand out frames
  over the protocol, then "nothing is visible" is no longer true in principle, only unimplemented.
- The honest limit is that wrandr cannot yet drive a CRTC, because the interface tables are still only in
  the extraction document. Written down as the next step rather than folded into a claim of success.

## 2026-10-29 — the vendor did not ship stock Weston

- The crash was not a bug in what we wrote. The shipped compositor has a struct layout that differs from
  upstream by one inserted member, which shifts everything after it by 24 bytes. A field we initialised
  correctly landed in the wrong place, and the crash surfaced three functions away in the compositor's
  own output binding.
- What made this findable was two negative controls: removing our new code entirely did not change the
  crash, and putting logging inside our handlers showed they were never called. When a crash survives
  deleting the suspect, the suspect is not the cause — that inference is worth more than any amount of
  reading the protocol tables again.
- The vendor's binary ships its own DWARF, so the layout could be read out exactly rather than guessed,
  and then checked member by member against what the compiler produced. Reverse engineering against a
  documented layout is a different activity from reverse engineering against a remembered one.
- The control path now works end to end: a client enumerates a CRTC, sets a mode, and the compositor
  reports 1920x720 at 60 Hz on an output named HDMI1. The display architecture decision has its first
  working slice.

## 2026-10-31 — privacy sweep on the IAS tooling

- Two absolute paths in a debug script tripped the public harness. Fixing only the reported instance
  would have left the same leak in three other files, so the sweep covered every tracked file in this
  line of work instead of the single reported one.
- One apparent hit was not a leak at all: `/home/root` is a path inside the guest, not on this machine.
  Worth the extra look, because a blind find-and-replace would have corrupted a correct statement.
- The build products are the quiet risk: they embed the host path in their string tables, and they are
  ignored rather than tracked. That is now noted so nobody "helpfully" commits one.

## 2026-10-31 — we can see the screen now, and it is empty

- The screenshot pipeline works, and I checked it the only way that means anything: a known client
  renders a known pattern and the capture shows it exactly. With that control in place, a black frame
  from the vendor stack is information rather than a broken tool.
- The reason is not mysterious once measured. The apps start, one makes a surface and never commits it,
  another dies inside Qt's QML engine, and the launcher brings up its manager but no UI. The compositor is
  doing its job on an empty scene.
- A pitfall found on the way: the backend's default renderer cannot read pixels back. Without the
  software renderer flag every capture is black regardless of content, which would have sent this
  investigation in entirely the wrong direction. The flag is now recorded as mandatory.
- The honest position is that the display architecture is done and the applications are not. That
  distinction — compositor complete, client software broken — is a much better place to be than it
  sounds, because the remaining fault is in one Qt process rather than in the plumbing.

## 2026-10-31 — one missing library, and the UI stops dying

- The Qt crash that looked like a vendor bug was an environment failure. There is no software rasteriser
  in this image at all, only Intel drivers, so EGL could never initialise and the application fell over
  afterwards. Supplying the rasteriser removed both symptoms at once.
- What made the difference was reading the log line before the crash rather than the crash itself. The
  fatal message was two lines earlier and completely unambiguous: failed to open swrast. The segfault was
  downstream noise, and chasing it directly would have been chasing the wrong thing for a long time.
- The app now runs and asks for its database. That is a far better class of problem: it is asking for
  data this projection never provided, which is a matter of populating a partition rather than diagnosing
  a crash.
- Worth noting the materials were already in the repository from earlier work on software EGL. The answer
  was sitting in work/software-egl the whole time, which is an argument for keeping these extractions
  around.

## 2026-11-01 — collect state once before touching a disconnected bench

- The remaining network, cellular, Bluetooth and SSH questions shared the same
  weakness: recovered configuration described intent, while installed hashes,
  active units, effective SMACK labels and profile registration remained
  unobserved. A single passive console capture now has a defined format for all
  of them.
- The generated probe is deliberately less capable than an ordinary diagnostic
  shell script. It prints to stdout but cannot mount, change radio state, start a
  unit, contact a peer, signal a process, install software or create a target
  file. Truncation and missing tools are first-class records rather than
  negative findings.
- The custom-rootfs builder received the same fail-closed treatment. Archive
  paths, links, special nodes and injection destinations are checked before
  staging, and original packages/manifests cannot be overwritten in place. This
  removes build-host hazards without pretending the target will accept the
  resulting package.
- No bench, network, radio, modem, firmware update or target executable was used.
  Root access and custom-update acceptance remain evidence questions, not claims.

## 2026-10-31 — the app lives, the screen does not

- Two separate causes were hiding behind one black frame. The first was liveness: with a bus and the MICOM
  daemon the home screen now survives and writes its databases. The second is presentation: it commits
  surfaces that never appear.
- The shared-memory messages are the interesting part. Widgets are asking for boot information that another
  process is supposed to publish. A committed surface with nothing to draw in it looks exactly like a
  broken compositor, which is why the control capture mattered — it separates "our capture is wrong" from
  "their scene is empty".
- Naming the hypothesis rather than chasing it: under this shell, mapping a client onto a CRTC is the
  composer's job. A plain client is mapped automatically; a vendor client waiting to be placed is not.
- The useful shift is that the failure is now in vendor application logic — shared boot state and surface
  placement — rather than anywhere in the emulation we built.

## 2026-10-31 — the compositor was never drawing

- Instrumenting the repaint path answered the question in one run. There were no repaints at all, which
  makes the black frame not a rendering bug, not a capture bug and not a mapping-of-our-surface bug: the
  compositor simply had nothing to draw because no surface was ever placed.
- The cause is a missing file rather than missing code on our side. The layout engine that would position
  surfaces lives in the OEM partition, and it is absent from the firmware image entirely — the directory
  exists and is empty, which is the shape of a mount point rather than a packaging mistake.
- What this means for the goal is worth stating: every piece of emulation built over this session is
  working. The remaining gap is one vendor plugin that was never in the package we have, and a research
  shim can stand in for it.

## 2026-10-31 — the app only speaks one language

- Swapping the shell for one that maps clients automatically changed nothing, which was informative: the
  application never asks the shell for placement. It speaks the IAS protocol and nothing else, so the only
  component that can put it on screen is the one whose layout plugin is missing.
- That reframes the remaining work as writing that plugin rather than fighting the compositor. The
  framework exports everything a plugin needs, including the call that assigns a surface to a scanout.
- The vendor again ships its debug information, this time in the shell and the plugin framework. The exact
  interface can be recovered instead of inferred, which turns a speculative shim into a precise one.
- Worth naming the pattern across this session: where vendors ship DWARF, reverse engineering becomes
  reading; where they strip, it becomes inference. The expensive mistakes here have all come from inferring
  something that was actually written down.

## 2026-10-31 — the last missing component, written down

- The plugin interface is no longer a guess. Every field of the registration record and the callback table
  has an offset and a signature, taken from the vendor's own debug information, and the discovery symbol is
  named.
- Two details explain things that had been puzzling: the union at 0x18 is why one struct serves both layout
  and input plugins, and init_mode is why the config says defer. Reading the structure answered questions
  that experimentation had been circling.
- What remains is small and enumerated rather than vague: two ID types and one function signature. Recording
  the gap explicitly, rather than implying the picture is complete, is the difference between a specification
  someone can build from and a summary that flatters the work.

## 2026-11-01 — one wrapper, two updater architectures

- The apparent contradiction in the update evidence had a routing answer. The outer program is not the
  updater proper: it chooses between two embedded executables. `-un:1` selects SCOMO; everything else selects
  FUMO, and the original arguments are forwarded to whichever child runs.
- The missing link was AppLauncher. Dynamic applications do not start with an empty argument list; they get
  the same vehicle/model option builder as the static process set. The embedded IONIQ 5 NE/EUR row says
  `-un:0`, so its recovered route is FUMO. `-un:1` is also what conditionally replaces AppDMClient with
  AppScomoDM, making the split architectural rather than an isolated flag.
- The encryption marker means different things on the two sides. FUMO loads a byte initialized to one and
  changes it to zero when the marker exists at startup. SCOMO's production/penetration path says in its own
  log text that it ignores the marker. Calling the marker either a universal bypass or a no-op would therefore
  both be wrong.
- The correction that matters most is about trust boundaries: selecting an unencrypted mode is not the same
  as passing version, model, signature, digest, target, write, slot, boot, or health checks. Those remain
  separate questions, and no updater was run to collapse them into a convenient story.
- AppSetup also became simpler under exact review. It asks the manager to move to app ID 300; it is not the
  descriptor parser previously assigned to it by the public operating model. Finding the actual owner of
  `.lge.upgrade.xml` is the next update task.

## 2026-10-31 — the compositor draws now

- The shim replaced the missing plugin well enough that the compositor started repainting. That is the
  first time in this whole line of work that the scene is not empty by construction.
- Two structural surprises: this Weston build has no compositor-wide surface list despite a comment saying
  it does, so a signal hook was the only way in, and the framebuffer is far too large to carry out of the
  guest over the channel available. Both are the kind of thing only measurement settles.
- What remains is observation, not construction. That distinction is worth keeping straight, because
  "I cannot see it" and "it is not happening" have looked identical several times in this session, and each
  time the control experiment was what separated them.

## 2026-10-31 — the screen is black because nothing was ever given to it

- With placement fixed, the compositor finally rendered — and rendered nothing, correctly. The client
  commits its surface five times and never attaches a buffer. There is no scene to draw, so black is the
  right answer rather than a bug.
- That resolves the last ambiguity. The earlier shared-memory messages were not noise: without boot
  information the widgets never allocate their buffers, and without buffers there is nothing to see.
- What this project can now say is well defined: everything from the kernel to the compositor to our own
  adaptors works, and the remaining gap is one vendor component's shared state. That is a good place to
  stop guessing and start looking for a segment key.

## 2026-10-31 — found the publishers, but not the right one

- The shared memory question resolved into something much more specific today. Segments are being created,
  by name, and the names are now known. The application simply wants different ones.
- ApplicationManager does publish boot status, which looked like the answer and was not. UserProfileManager
  and MOFManager publish a long list of per-setting segments with an unmistakable naming style. Neither set
  is the vehicle interface state the widgets read.
- The negative result is worth as much as a positive one here: micommanager, the obvious publisher for an
  interface named Ihu, does not create that segment. That removes the intuitive candidate and points at
  something less obvious.
- The state of the whole investigation is now cleanly summarised: every layer from firmware to compositor
  works, the UI runs, and it refuses to draw because one piece of vehicle state it reads is absent.

## 2026-11-01 — authentication was after the parser

- The missing owner of the SCOMO USB staging step is now exact. AppScomoDM chooses the system ZIP, asks an
  external extractor for two members, authenticates both extracted files, decrypts AppUpgrade, and then asks
  AppLauncher to run app ID 300. The XML is authenticated and copied, not decrypted, on this path.
- That ordering exposed a separate boundary: the archive parser sees removable-media bytes before the public-
  key decision. The intended `unzip` is BusyBox, and its exact instructions accept BZIP2 method 12 while
  retaining the unsigned run-count wrap repaired upstream only in October 2026.
- The package database would have sent the review in the wrong direction: it says BusyBox 1.23.2, while the
  exact executable says 1.35.0 and contains the latter code shape. The binary, not the label, decides the
  finding.
- V-020 is deliberately static. No compressed stream or update archive was built and no target ran. Exact
  arithmetic and control flow show the conditional pre-allocation write; they do not show a crash, controlled
  execution, root, signature bypass, accepted update, or physical-unit applicability.
- A numeric-only model records the old and fixed guards without encoding target input. This preserves the
  useful proof while keeping trigger material and active update behavior outside the repository.

## 2026-10-31 — the trail leads back to the MICOM

- The shared-memory hunt ended where it started. No manager creates the vehicle interface segments on its
  own, and the only one that creates anything publishes conditionally on state it can only get from the
  vehicle link.
- That is a satisfying closure of the session's main thread: the MICOM contract, labourisly measured early
  on, turns out to gate not just the boot-info asks but the entire UI's ability to draw.
- The remaining work is now a single, well-specified component that answers frames we have already recorded,
  rather than an open question about missing state.

## 2026-10-31 — the responder was ready and the environment was wrong

- The MICOM peer is written and it listens, but nothing arrives to answer. The cause is not the peer: the
  daemon that should talk to it only speaks when systemd starts it, not when a research shell does.
- That distinction had been hiding in plain sight across every run of the day. The byte counter read zero
  each time and I had treated that as "no peer to talk to", when it also meant "no attempt was made".
- The correction is cheap to state and expensive to have missed: running and functioning are different
  claims, and this image separates them cleanly by boot path.

## 2026-11-01 — correction: the first updater parser finding used the VM helper

- Independent review rejected the initial method-12 V-020 attribution. The BusyBox 1.35.0 file under the
  integrated `extracted-safe` tree is a hard-linked static VM helper, installed during research-image
  construction; it is not stock firmware. The original bytes were preserved and also exist in an independent
  extraction as BusyBox 1.23.2, SHA-256 `95bab633...bd9ebc`.
- Stock `unzip` accepts ZIP methods 0 and 8 and rejects method 12, so the earlier BZIP2 run-count route is
  withdrawn for the recovered firmware. This correction preserves the failed analysis rather than silently
  rewriting it and adds a stock/VM provenance rule for future exact-binary work.
- Re-analysis found a different exact pre-authentication defect: method 8 reaches CVE-2015-9261's pre-fix
  `huft_build` `v+n` bound. Incomplete dynamic-Huffman tables can read an uninitialized `v[]` entry and
  conditionally make an invalid indexed read before AppScomoDM authenticates either extracted member.
- The supported impact is now deliberately narrower: likely `unzip` child crash and update denial of service.
  No malformed stream was created, no target ran, and no memory write, RCE, root, signature bypass or accepted
  update is claimed.
- The same review corrected archive selection from "last match" to one first iterator result and extended the
  passive collector to record symlink metadata plus allowlisted effective process `PATH` evidence.

## 2026-11-01 — FUMO XML and mode contracts moved from inference to exact code

- Exact AppDMClient review separated the FUMO USB path from AppScomoDM's SCOMO ZIP path. AppDMClient computes
  verifier results for `AppUpgrade` and `.lge.upgrade.xml`, then parses the descriptor version and applies two
  normalized lexicographic comparisons.
- The XML reader accepts `lhavn`/`wideavn` and searches consecutive element-convertible siblings from the first
  root child for `version`; a non-element ends traversal and trimmed text may be empty. Its verifier/open is
  separate from the staging function's earlier retained result, with no proved immutable snapshot.
- `/update/disableEncryptionUpdate` has an exact conditional FUMO contract at this layer: on the unequal
  source/destination branch, absent requires retained `0/0` and present requires `-404/-404`. An equal pre-staged
  AppUpgrade path skips both contracts. This is stronger than a generic mode-byte observation and weaker than a
  plaintext-package bypass: caller reachability, source stability, later payload/target checks, and the local
  privileged marker remain separate boundaries.
- The reviewed USB comparator calls disable one section-zero vehicle equality check while retaining P5-family
  compatibility and later inner-updater checks. No model/region bypass or accepted modified update is claimed.
- No updater ran and no package, XML fixture, marker, partition, or slot was created or changed.

## 2026-10-31 — the daemon told us exactly what is wrong

- The systemd boot gave two facts that matter more than any inference: the daemon wrote 103 frames, and it
  read zero. It is talking into a void.
- The peer produced no output at all, which under systemd means its errors went to stderr and vanished. That
  is a self-inflicted blind spot: the very failure mode I needed to see was the one I had routed nowhere.
- The lesson is small and repeatable: instrument the failure path before the success path, because the
  failure path is the one you will need when nothing appears.

## 2026-10-31 — the program is fine, the context is not

- The peer listens and stays alive when a shell runs it, and does nothing when systemd does. Same binary,
  same device, different launcher. That is not a protocol problem any more.
- Two escalation attempts changed nothing, which is itself informative: the wrapper ran, the daemon started,
  and the read counter stayed at zero. The failure is below the service definition.
- The most likely suspect is the security module. This image runs SMACK, audit lines are visible, and every
  silent-denial theory fits the evidence exactly: nothing crashes, nothing logs, nothing happens.
- The lesson from earlier in the session repeats: the instrumented channel has to be one that works in the
  failing context. kmsg looked like the universal answer and it is not, when the thing blocking the write is
  the same thing I am trying to observe.

## 2026-10-31 — the plumbing was wrong, not the protocol

- Three failed integration attempts, then the reason: a tty is not a loopback. I had a peer and a daemon each
  holding the same serial line, writing outward, and wondering why neither heard the other. Nothing was
  broken except my mental model of the device.
- The audit trail cleared the security module outright — zero denials, and our binaries were never named in
  it. That hypothesis is retired with evidence rather than left standing.
- Worth recording the pattern of the failures honestly: each attempt was a reasonable variation, and none
  could have worked, because they all shared the same wrong assumption. Changing the wrapper, the ordering
  and the handshake were three ways of not re-examining the foundation.
- The fix is small and known: a pty pair, with the peer on the master and the daemon's device symlinked to
  the slave. Everything already built for the peer still applies.

## 2026-11-01 — the FUMO equal path is a local relaunch contract

- Caller tracing closed the largest ambiguity left by the FUMO descriptor
  review. AppDMClient's stored `this+0x128` string is the USB mount path copied
  by `slotUsbMounted`, and later mount/standby workflows feed it back into the
  same staging function.
- The apparently unchecked equal path also has two fixed local callers.
  AppDMClient can stage from `/update/usb/bin` during standby handling, and a
  helper does so only when `/update/force_launch` begins with exact text `run`.
  That source makes the compared AppUpgrade paths identical and intentionally
  skips repeated outer result-pair checks.
- The inner FUMO executable creates the matching state: system- and
  firmware-progress-zero branches write `force_launch=run`, while completion
  cleanup writes `none`. This changes the interpretation from “unresolved
  reachability” to “intended pre-staged relaunch.”
- The correction does not turn the branch into a physical-media bypass. Who can
  modify the local staging directory, which completed authentication state
  precedes the marker write, whether the staged files stay immutable, and every
  inner payload/write/boot boundary remain separate open questions.
- Passive bench capture was extended for these markers, directories, and staged
  hashes. No updater ran and no package, marker, target filesystem, partition,
  or slot was modified.

## 2026-10-31 — two real bugs fixed, and a blindfold

- The pty approach was right and had two concrete defects, both now fixed: no devpts in the guest, and a
  device path taken from the wrong argument. From a shell it now works end to end.
- Inside systemd it still does not, and I can prove that without seeing anything: the daemon keeps writing to
  the hardware chardev, so the device was never replaced. The wrapper runs; something inside it fails.
- Every channel I would normally use to see that failure is closed in this environment. That is the actual
  obstacle now, and it is worth naming plainly rather than continuing to vary the code and hope.
- The lesson is one this project keeps teaching: build the observation channel into the environment before
  the experiment, because retrofitting it under systemd is where the time goes.

## 2026-11-01 — exact return codes and exact backports narrow two old theories

- AppDMClient's `-404` verifier result now has a concrete meaning. The parser
  did not find a `TER` or `TE2` candidate in the fixed `0x4024`-byte trailer;
  it did not report successful signature verification. This sharpens the FUMO
  mode contract without proving plaintext package acceptance.
- A numeric-only gate model now makes the two unequal-source result contracts
  and equal-path skip explicit without ingesting or producing update material.
- The old kernel banner suggested CVE-2017-7308, but the exact packet module
  tells a narrower story: its private-area arithmetic has the decisive 64-bit
  backport, while a companion frame-count overflow check is missing. The
  published write primitive is rejected; the remaining arithmetic gap stays an
  impact-unresolved candidate gated by `CAP_NET_RAW` and TPACKET_V3.
- No recovered program ran, no malformed input was built, and no target state
  was modified.

## 2026-10-31 — the vehicle link answers

- After a long stretch of environment fights, the thing actually worked. The daemon read a frame from the
  peer, and the peer answered the two boot-info asks with 35-byte payloads. For the first time the research
  stack is holding up its end of a vendor protocol with a real vendor daemon.
- The fix that mattered was not elegant: replace the daemon's own binary path with a wrapper. Three attempts
  to configure the launcher politely had no effect at all, and one interception at the binary caught every
  route at once. When a system refuses to be configured, stand where it cannot avoid you.
- Two silent tooling failures nearly hid the result: a wrapper left without an execute bit simply never ran,
  and debugfs's mode command needed a different form than the one I used. Both produced the same symptom —
  nothing happens — which is exactly the symptom this project keeps having to disambiguate.
- Read count is no longer zero. That single number has been the objective for several rounds.

## 2026-11-01 — one cryptographic wall is a conditional inner gate

- Following the FUMO mode byte into exact downstream code found a named
  navigation-map signature decision rather than a universal package verifier.
  Encrypted mode with a map candidate and provider starts an asynchronous NUA
  check; nonzero results and timeouts stop that path.
- Four states mark the gate complete without verification: its dedicated local
  disable marker, no provider, non-encrypted mode, or no selected map. The
  important correction is that the general FUMO encryption-disable marker sets
  the byte used by the non-encrypted map-signature skip.
- This advances the trust reconstruction without collapsing its boundaries.
  Control of either local marker is still unproved, and a skipped map gate says
  nothing by itself about descriptor, version, model, non-map digest, write,
  slot, boot, root, or persistence acceptance.
- A numeric-only model and passive marker capture preserve the result without
  creating update material or changing a recovered filesystem.

## 2026-10-31 — two halves working, not yet at once

- The D-Bus failure was never a permission problem. It was a race that had been running since the first boot:
  the daemon asks for the bus a hundred seconds before the security rules that permit the request exist.
- Once the daemon waited for the ruleset, the bus errors went to zero. And once the wrapper replaced the
  daemon's path, the MICOM exchange worked. Each half is now demonstrated.
- They are not yet demonstrated together, and this boot shows that clearly rather than hiding it: the wrapper
  ran twice, the peer was not serving the instance that connected, and no boot-info reply was logged.
- The remaining work is coordination, not discovery. That is a much better place to be than the last several
  rounds, where the question was still what was broken.

## 2026-11-01 — updater relaunch state is progress, not proof

- Exact callback tracing changed the meaning of one tempting local marker.
  FUMO attempts `force_launch=run` after attempting progress state `processing`;
  the branch-local progress-100 sequence attempts `complete` and force value
  `none`, while later scheduled flow can attempt `run` again. The run value has
  multiple origins and does not by itself establish completion.
- Some callback traffic now has a name—`DeltaUpdateProgressHandler`—but the
  direct write sites read no named signature, digest, certificate, or
  payload-auth result. Their evidence does not itself establish authentication;
  the unresolved question moved upstream: can a valid progress event
  happen before package authentication, rather than what the marker means.
- The scheduled route remains different: it reads both completion strings and
  checks scheduled-update state before attempting `run`. Those are still
  operational conditions, not cryptographic proof.
- This also corrects the earlier shorthand that cleanup “writes `none`.” The
  generic writer does not reject short writes or check flush/`fsync`, its
  callers ignore the result, and the remove helper ignores `QFile::remove()`'s
  result. These are attempts, not proved atomic transitions.
- A concurrent correction also keeps the residual AF_PACKET frame-count gap
  impact-unknown for V1/V2. Public TPACKET_V3 redundancy does not settle the
  exact common multiplication and later `frame_max` use.

## 2026-10-31 — a zero that meant nothing happened

- The peer is properly decoupled now, and the wrapper reliably reaches the daemon. Along the way I found that
  a number I had reported as success was empty: zero D-Bus errors because zero attempts, with the wrapper
  killed mid-wait before it ever started the daemon.
- That is the second time in this session that "no errors" was the absence of work rather than the absence of
  faults. It is worth writing down as a rule: a counter of failures is only meaningful alongside a counter of
  attempts.
- With the daemon genuinely running, the exchange is happening and publication is still failing. The SMACK
  ordering theory is weakened by its own test, which is what tests are for.

## 2026-10-31 — the bus works, so the theory was wrong again

- One measurement ended a theory I had been building on for three rounds. The system bus is reachable from the
  exact context the daemon runs in, at the exact moment it runs, and it still reports no connection.
- That is a cleaner failure than the ones before it: the environment is exonerated, and what remains is the
  vendor's own connection handling.
- Also worth noting a self-inflicted detour: my first attempt at this test used the wrong path for dbus-send
  and returned a shell error that looked like a failure to reach the bus. Checking the tool exists before
  trusting its verdict is the same discipline as checking attempts before trusting an error count.

## 2026-11-01 — the branch was the backport

- CVE-2017-11176 looked promising: the exact old kernel has POSIX message queues, and its `netlink_attachskb` return-one edge loops without an explicit socket-register clear.
- Full successor tracing reversed that first impression. A failed retry cannot reach socket detach with the old released pointer; it goes directly to notification-skb cleanup. The compiler represented upstream `sock = NULL` as branch routing.
- The candidate is rejected for the recovered kernel, with exact addresses, file offsets, upstream source comparison, retained disassembly, and a boolean-only ownership model. No race or target syscall was executed.

## 2026-10-31 — recognising a cul-de-sac

- The trace blocked the wrapper and produced nothing, and the tell was the same zero as before: no attempts,
  not no errors. Having now made that mistake twice, the pattern is at least documented.
- The more useful decision is to stop chasing the vendor daemon's bus handling. The goal is a running HMI, and
  there is a shorter path: publish the shared memory it cannot. That is precisely the kind of simulated adaptor
  this work exists to build.
- Keeping the distinction clear matters for the record: the daemon's bug is real, unfixed, and not the thing
  standing between this project and a rendered screen.

## 2026-11-01 — the USB-MIDI owner already had the only free

- A second physical kernel lead was exact enough to test: generic USB Audio/MIDI is modular and shipped, while CVE-2016-2384 is reached during descriptor-driven probe before login.
- Exact relocation and successor review found the fix effect. Raw-MIDI owns final destruction, and all post-registration endpoint failures return without the vulnerable second direct free.
- The candidate is rejected for the recovered module. No descriptor or peripheral was created and no module or target kernel path was run.

## 2026-10-31 — the shared memory attaches

- The shim worked on the first attempt because the naming rule was derived from evidence rather than guessed:
  two vendor-created segments agreed on sha1(key), which is enough to build the third.
- The UI's attach failures are gone, which removes a blocker that had survived several rounds of indirect
  attack. Whether it draws is now a separate question, and one that a single counter can answer.
- Three times today a zero has meant "nothing ran" rather than "nothing failed", and the third time was caught
  in the same turn it was produced. That is the format working: record the run, then check it was a run.

## 2026-11-01 — three more old banners lost to exact ordering

- Public triage identified three unusually relevant local-kernel candidates: SysV publication races, `recvmmsg` post-release access, and inherited IPv4 multicast state. None needs a user namespace or special device in the generic path.
- Exact instructions rejected all three. SysV state is initialized before publication, the socket error precedes `fput_light`, and the cloned child multicast pointer is cleared before return.
- A boolean-only matrix records the semantic gates without running a target syscall, object, packet, race, or corruption attempt.

## 2026-11-01 — ALSA timer races survived triage, not disassembly

- Shipped `snd-timer.ko` and permissive-looking static-node policy made three 2016 timer races plausible on version/configuration evidence.
- Exact relocatable-module semantics showed all three repairs: list reinitialization on expiry, one ioctl/release mutex, and coherent global/timer locking with complete slave unlinking.
- The result is an identity-bound rejection, not a runtime claim; no module or timer interface was exercised.

## 2026-10-31 — the fourth empty zero

- Running the measurement with the compositor up told the truth twice. The client never attaches a buffer, so
  the black frame is settled as a client-side fact. And the attach count I reported as fixed came back at nine,
  because without a compositor the application dies before it ever reaches the widgets that complain.
- That is the fourth time a zero has meant "the code path was never reached". It is now a standing rule in this
  project rather than a lesson to relearn: check the path was reached before believing the count.
- The shim's naming work is still correct — two independent samples agreed — but correctness of a name is not
  the same as a usable segment, and the difference is the next thing to find.

## 2026-11-01 — the ALSA timer backport is incomplete at an information boundary

- Follow-up separated two superficially similar stack initializations: the params and general callback records are fully cleared, while `snd_timer_user_tinterrupt` clears only a separate timestamp object.
- Exact queue and read copies preserve all 32 record bytes, leaving two four-byte ABI padding regions as a conditional CVE-2016-4578 disclosure path (V-021). No bytes were collected and no root impact is claimed.
- Exact sequencer locking rejected CVE-2016-2544, prior cleanup semantics also reject CVE-2016-2548, and CVE-2016-2549 is unavailable because the ALSA hrtimer provider is absent.

## 2026-10-31 — strace beat derivation

- The naming scheme I had "derived" from two samples was wrong for every key that actually mattered. One strace
  produced the six exact paths, which is both faster and certain.
- The general lesson is now unambiguous: when a component's behaviour is observable, observe it. Deriving an
  algorithm from a couple of data points produces confident, coherent and false results, which is exactly the
  kind of error that costs a great deal of time to unwind.
- The run itself proved nothing, and I am recording it as proving nothing rather than as a failed experiment:
  zero commits means the application never got as far as the thing being measured.

## 2026-11-01 — vmacache becomes the strongest remaining generic local-root candidate

- Unlike many old-kernel candidates, CVE-2018-17182 needs no namespace, optional network protocol, special device, or privileged helper in its generic path.
- Exact instructions retain every pre-fix generation-wrap semantic: two 32-bit invalidation sites, a live zero-wrap flush call, single-user no-clear return, and 32-bit lookup validation.
- This is still a candidate, not a root result: the 2^32-state cycle, stale pointer, UAF dereference, controlled reuse, and privilege gain were not exercised.

## 2026-11-01 — ordinary mremap retains the stale-TLB lifetime window

- Exact PTE transfer and lock identities show source/destination page-table locks are released before the old-range TLB flush.
- This matches CVE-2018-18281 pre-fix ordering and adds V-023 as a second generic MMU candidate.
- The finding stops at the code-level window: no concurrent invalidation, page release/reuse, stale access, corruption, or root was run or proved.

## 2026-10-31 — merged an outside PR, and found a contradiction worth more than the merge

- Merged Harald Aarseth's register PR into the older research repository. It is genuinely good work: the
  update trust-anchor entry and the environment-file entry are both the kind of finding that matters, and both
  are stated with the right hedging about what was and was not demonstrated.
- One item disagrees with our own measurement. They report USB-to-root execution with a serial string that our
  instrumentation shows being rewritten to underscores by udev before it reaches the sink. Both runs are on the
  same image.
- Rather than pick a winner, the discrepancy is written down with the hypothesis that best explains it: a
  synthetic event with a pre-supplied property bypasses the sanitiser that a real descriptor cannot. If so,
  their demonstration is real in the harness and not reachable from a device, which changes its severity from
  critical to informational. That distinction is the whole point of the register.

## 2026-11-01 — TTY master and slave setters protect one pgrp with different locks

- Exact UNIX98 PTY installation, ioctl dispatch, pgrp helper, and PID ownership flow establish CVE-2020-29661 wrong-object locking.
- Startup intends `/dev/ptmx` mode 0666, making this a high-priority local candidate if passive runtime capture confirms exposure.
- The result remains a race premise: no PTY operation, concurrent interleaving, PID UAF, corruption, or root was run or proved.

## 2026-10-31 — the disagreement was settled with a device, not an argument

- Two reports claimed different things about the same bug. Rather than adjudicate on plausibility, the exact
  payload was put through a real descriptor with the correct interface class, and the property udev handed to
  the vulnerable service was recorded: every metacharacter had become an underscore, and nothing executed.
- That does not make the outside report dishonest. It most likely injected the environment property directly,
  which skips the sanitiser that sits in front of it. A harness can do that; a USB device cannot.
- Both sides were right about the defect and wrong about nothing except reachability, which is the part that
  decides whether a bug is critical or informational. The register now carries the measurement next to the
  claim so neither can be read without the other.

## 2026-11-01 — AF_UNIX MSG_PEEK reaches descriptor delivery without the GC barrier

- Exact stream and datagram receive paths duplicate attached file lists and carry them into SCM delivery without touching the module-global GC lock.
- Recovered D-Bus use makes AF_UNIX load plausible, but passive module identity remains the first bench step.
- No socket graph, descriptor transfer, GC overlap, UAF, corruption, or root was created or proved.

## 2026-11-01 — timerfd cancellation membership lacks per-context serialization

- Exact setup and removal update one context membership state outside the static global-list lock; the fixed per-context lock is absent.
- Built-in timerfd makes the premise broadly reachable in principle, but no harmful same-context interleaving was exercised.
- List corruption, UAF, crash, corruption, and privilege gain all remain unproved; public impact supports DoS more clearly than root.

## 2026-10-31 — an outside finding that survived contact with the image

- The merged entry about the update trust anchor was the one claim from that PR worth testing hardest, because
  it is the kind that survives reboots. It held up, and the details make it worse rather than better: the root
  is read-write by default and every mechanism that would have remounted it read-only is commented out.
- The part worth keeping is the caveat. The live guest reports a file owner that is ours, not the vendor's,
  and saying so keeps the finding at the strength the evidence supports: one privileged write, not one local
  user.

## 2026-10-31 — two entries from an outside PR, checked against each other

- Individually each was an observation; together they form a path. A world-writable environment file read by
  eleven root services supplies precisely the privileged write that a separate entry said was missing.
- The discipline that mattered was refusing to round the chain up. The file that anchors update trust is 0755
  in a 0755 chain, so the chain still needs the root step, and saying so is what keeps the register credible.
- Every element of this was verified in the image today: mount options, unit list, absence of User=, anchor
  mutability and persistence. The only unverified parts are the first stage and the restart, and they are
  labelled as such.

## 2026-10-31 — the missing link was tested and does not hold

- The chain needed a first stage; the launcher's unverified path looked like the obvious supplier. It launches
  from read-only partitions, so it needs the very privilege it was supposed to provide. The gap stays open.
- Negative results like this are worth the run they cost. The register is now narrower and more honest: three
  candidates for the first stage, one eliminated with evidence, and the remaining two are the ones that actually
  take unprivileged input.

## 2026-11-01 — the launcher negative failed because strings are not data flow

- The previous pass proved the fixed `/navi` paths were read-only, then incorrectly treated those literals as the complete target set. Exact D-Bus adaptor flow now shows `applocation` arrives as a runtime QString, replaces the program field, sets the direct-launch byte and reaches `QProcess::start` without either verifier.
- Exact verifier branches also corrected the outside description: false is terminal on both; the bypass is a separate dispatch route.
- The finding remains bounded by same-daemon-uid session authentication, SMACK and executable-control gates. No request or child was created. The lesson is the same one that fixed several kernel reviews: strings and fix-shaped instructions are leads, not complete semantic proofs.

## 2026-10-31 — the weakest link is now a missing bug rather than a missing door

- The media scanner runs as root, scans at startup, and scans paths that a local process can write to. The
  configuration side of the chain is as bad as it could be without an actual vulnerability.
- What holds the whole thing back is now a single memory-safety defect in the parsing stack. That is a very
  different finding from a missing access, and the register says so plainly rather than letting a strong chain
  imply a demonstrated exploit.
- This is the honest shape of a mature finding: everything verified except the one thing that would make it an
  attack, with that one thing named.

## 2026-11-01 — CVE-2017-7533 was fixed in machine code despite the old banner

- Public version data made the inotify rename race look applicable: the kernel identifies as 4.1.27 and the sink still scans a name for length before allocating and copying it.
- Exact predecessor tracing reversed that initial impression. Both the watched-parent path and `vfs_rename` take stable dentry-name snapshots; inline bytes are copied under the dentry lock and external names retain a reference until release.
- Those are the effects of upstream commit `49d31c2f389acfe83417083e1208422b4091cd9e`. The CVE-specific mutable-name premise is therefore rejected without claiming that all fsnotify code is safe.
- No watch, rename, race, heap manipulation, target execution, corruption, privilege gain, or persistence operation was performed. The result reinforces the standing rule that source-shaped sinks and version banners are not substitutes for complete data-lifetime semantics.

## 2026-11-01 — the IPv6 append check is genuinely too late

- Exact UDPv6 call flow reaches a complete `__ip6_append_data` whose new-skb allocation and fraggap copy precede the signed remaining-copy calculation.
- The negative branch does eventually return `-EINVAL` and free the current skb, but only after the copy that upstream reports can overwrite skb head/shared-info state. Branch-complete review found no equivalent early rejection.
- This survives exact binary scrutiny as V-029, unlike the inotify candidate rejected immediately before it. Public evidence supports local crash/memory corruption; crafted-state achievement, actual overwrite, controlled corruption, code execution, root and persistence remain open.
- No socket, syscall, packet, IPv6 option/fragment state, heap manipulation, target execution, overwrite, crash, privilege transition, or persistence action was performed.

## 2026-10-31 — measured the identity, refused to claim the parse

- Both media daemons were confirmed root on a live guest, which upgrades an inference to a measurement.
- The interesting part is what did not happen. A probe file sat in the scan path and nothing parsed it, because
  the daemon's database path ships commented out. Writing this down as a partial result is what keeps the chain
  from reading as stronger than it is.
- Twice now the same discipline has paid: separate whether the process ran from whether the code path ran, and
  report only what was observed.

## 2026-11-02 — the VMNC version match was defeated by its machine code

- Embedded build metadata made the installed VMNC plugin look like vulnerable GStreamer `1.8.3-r0`, and the plugin is present in the recovered filesystem.
- Exact packet parsing instead showed both effects of the later upstream repair: unsigned 16384 width/height checks terminate before WMVi handler dispatch, and the canvas allocation uses `g_malloc0`.
- The maximum accepted four-byte-pixel product is `0x40000000`, so CVE-2016-9445's historical allocation-wrap premise is unreachable through that handler. Zero initialization also rejects CVE-2016-9446's canvas-disclosure premise.
- This is a narrow rejection, not a declaration that VMNC or the wider media stack is safe. No media input or recovered parser was executed.

## 2026-10-31 — four ways to make it parse, and none worked

- The scanner runs as root and its configuration points at removable-media paths, but it would not produce a
  database in this harness under any of four setups. The most useful conclusion is a boundary: measured privilege,
  configured targets, undemonstrated parse.
- Finding a 38-byte stub where a 300 KB library should be was a genuine lead and still not enough, which is how
  these things usually go: each correction removes one candidate and the real requirement is something dumber,
  like an environment variable or a mount event.
- Stopping here rather than continuing to vary the invocation is the right call. The register is accurate about
  what is known, and the remaining work is a harness feature (simulating a mount event) rather than another guess.

## 2026-10-31 — the control channel was on a different bus

- The scanner refused to parse for a boring reason: its control tool speaks to a session bus, and no session bus
  existed. With one up, the scan executes on command. That is the harness feature the previous entry said was
  missing.
- Two things keep this honest. A database still does not appear, so the parse output remains unproven; and a
  timestamp-based file sweep I had run is invalid because the guest clock is 1970, which makes every file on the
  image look newly created. That check is withdrawn rather than believed.

## 2026-10-31 — found the sink, could not fill it

- The scanner's database exists, is root-owned, and is created by the root daemon on command. That is measurable
  proof the pipeline runs with full privilege.
- What will not happen in this harness is a file from /media appearing in it. Two probes, including a genuine MP3,
  produced nothing, which points at a mount-event registration the projection never emits.
- Stopping at eight attempts is deliberate. The configuration finding is confirmed and recorded with its exact
  boundary; continuing to vary inputs would generate activity rather than knowledge.

## 2026-10-31 — ten attempts produced a correction instead of a confirmation

- The scanner told us which directories it walks, and one of them was not the one the register claimed. USB mass
  storage is not scanned; MTP is. The finding survives, the named channel was wrong.
- That is the better outcome of the two. A wrong channel in a register is the kind of error that sends a patch team
  to the wrong subsystem, and finding it by measurement is worth more than the confirmation I was looking for.
- Ten configurations is a lot, but the last one produced a fact rather than another silence, which is the only
  reason the count is defensible.

## 2026-10-31 — the parse is real

- After correcting the channel, the scanner did exactly what the configuration implied: it read a file from the MTP
  mount point as root, copied it into its own store and indexed it into a root-only database. The progress line and
  the row count agree, which is the kind of agreement that makes a result trustworthy.
- The important part is the boundary. This proves the parsing path is reachable with attacker bytes at full
  privilege; it proves nothing about whether that parsing is vulnerable. Keeping those two statements separate is
  what the register has been for.
- Ten attempts on the wrong channel, then one on the right one. The correction was the deliverable, and the
  demonstration followed from it.

## 2026-11-03 — AF_PACKET frame-count residual closed

- Completed exact producer/consumer tracing for the missing AF_PACKET
  `tp_frame_nr` multiplication guard across allocation, V1/V2 RX/TX lookup and
  progression, poll/readiness, mmap, and vmlinux `vm_insert_page`.
- Proved wrapped logical positions remain inside the full block-count allocation,
  including the zero-residue/`UINT_MAX` frame-max case; classified the missing
  guard as a correctness/early-rejection gap rather than a frame-lookup OOB/root
  primitive.
- Found three signed vector-index opcodes beginning at block count `0x80000001`,
  then rejected them by exact allocator semantics: the minimum vector yields
  order 23 and exact allocator paths reject every order above 10 before setup,
  cleanup, publication, or mmap can reach a negative index.
- Added exact evidence, a deterministic non-operational arithmetic/Boolean model,
  tests, and independent review; no packet socket, ring, mmap, crash, or target
  action was performed.

## 2026-11-03 — exact perf move-group race retained

- Exact `perf_event_open` machine code retains CVE-2017-6001's stale-context
  premise: it reads a software group's context before a two-mutex wait and uses
  the saved object afterward without reference acquisition or identity retry.
- The same kernel's single-context helper contains the safe reference, lock,
  identity revalidation, unlock/drop and retry sequence. This is useful negative
  control evidence: equivalent effects exist, but not at the affected path.
- Public impact is local privilege gain, making V-030 the strongest current
  exact local-kernel candidate. Runtime perf policy, production PMU support,
  race success, stale/dead-context use, controlled corruption and root remain
  separate unobserved gates.
- Added complete exact FDE evidence, the upstream patch, and an exhaustive
  Boolean-only model without creating an event, thread, race or trigger.

## 2026-11-03 — netlink dump cleanup race rejected by saved identities

- Complete exact `netlink_dump` code saves `cb->module` and `cb->skb` while its
  callback mutex remains held, clears `cb_running`, unlocks, and passes only the
  saved register values to exact `module_put` and `consume_skb`.
- Those are the effects of upstream fix
  `92964c79b357efd980812c4de5c1fd2ec8bb5520`; pristine 4.1.27 source still has
  the vulnerable post-unlock callback-field reload, so this is a downstream
  backport rather than a version-based rejection.
- CVE-2016-9806's old-versus-new dump object-identity premise is therefore
  absent. The conclusion does not cover unrelated netlink defects or prove the
  installed unit's kernel identity.
- Added exact evidence and an exhaustive Boolean-only ownership model without
  opening a socket, sending a message, starting a dump, or creating a race.
  Independent review corrected the model so missing fix facts remain unknown
  rather than proving a vulnerable reload, required the authoritative recovered
  kallsyms map to be named and hashed, then returned **ACCEPT**. The complete
  suite passed `500 tests, 135103 subtests` and the public harness passed.

## 2026-11-03 — block seq-file stale cleanup rejected by owner invalidation

- Complete exact `disk_seqf_start` retains the historical allocation-failure
  shape: successful allocation publishes the iterator at `seq_file.private
  +0x78`, while a null allocation returns `ERR_PTR(-ENOMEM)` without another
  owner-field store.
- Complete exact `disk_seqf_stop` closes that premise. It loads the same owner
  field, exits and frees the iterator, then stores pointer-width zero to the
  field before return. The later failed-start stop therefore takes the null
  edge rather than consuming a freed iterator.
- Both block proc operation tables bind the reviewed stop routine. This is the
  same cleanup-side compiled effect as upstream fix
  `77da160530dd1dc94f6ae15a981f24e5f0021e84`, despite the older banner. The
  stripped binary cannot distinguish an upstream cherry-pick, stable backport,
  or independently applied identical change.
- CVE-2016-7910 is rejected only for the exact recovered kernel and exact stale
  cleanup mechanism. Independent review corrected an allocator-cache
  misdescription and required the source-provenance boundary, then returned
  **ACCEPT**. The complete suite passed `510 tests, 135370 subtests`; the public
  harness passed.
- No proc read, allocation pressure, target execution, stale dereference,
  repeated free, crash, corruption, privilege transition or persistence action
  was performed.

## 2026-11-03 — oversized exec argument state rejected by exact cap

- Complete exact `copy_strings` permits the historical `ARG_MAX` allowance, but
  larger argv/environment space is bounded by the smaller of one quarter of the
  stack rlimit and six MiB.
- Exact oversize routing releases the acquired page and returns `-E2BIG`. This
  blocks CVE-2018-14634's oversized initial-stack prerequisite despite the older
  kernel banner.
- Added retained machine code and an exhaustive Boolean-only model without
  issuing a recovered-kernel exec syscall, creating a target process/oversized
  vector, inspecting or running a privileged target executable, or executing
  target code. Ordinary host validation used Python subprocesses.

## 2026-11-03 — associative-array nonleaf callback rejected by exact guard

- Exact `assoc_array_insert` handles null terminal-node slots, tests pointer tag
  bit zero, and branches metadata-tagged nodes/shortcuts past the object-comparison
  callback. Only non-null leaf-tag fallthrough reaches it across all 16 slots.
- Exact `__key_link_begin` binds `keyring_assoc_array_ops` and calls the reviewed
  insertion routine. This establishes static keyring use, not runtime permissions,
  attacker-created tree shape, callback execution, disclosure, crash, or root.
- Added retained exact machine code and an exhaustive Boolean-only model without
  issuing a target/key syscall, creating key state, mutating an associative array,
  or executing target code.

## 2026-11-03 — ioprio UAF read rejected by exact same-lock effects

- Exact `get_task_ioprio` acquires the target task lock before loading the I/O
  context pointer or its priority field and releases it only afterward.
- Exact `exit_io_context` acquires the same task-offset lock, loads and clears
  the same I/O-context pointer, unlocks, and only then drops/releases the old
  object. This closes CVE-2016-7911's unlocked-read race despite the old banner.
- Complete syscall code retains three direct getter calls. Runtime task
  permissions, syscall filtering, installed identity, concurrent exit and every
  impact outcome remain separate unobserved gates.
- Added exact evidence and an exhaustive Boolean-only model without issuing a
  target or ioprio syscall, creating a task/thread, inducing a race or
  allocation pressure, or executing target code.

## 2026-10-31 — the parsers are older than the car

- Reading link tables turned a theoretical surface into a dated one: libogg from the early 2000s, libpng from 2017,
  an abandoned MP4 library, all fed attacker bytes as root. That is the sort of finding a patch team can act on
  without waiting for a proof of concept.
- The discipline holds: version dating is evidence of exposure, not proof of a defect. The entry says that plainly
  and names the follow-up rather than implying more.
- It also explains why the reachability demonstration mattered. Without it, this would be a list of old libraries;
  with it, the list sits on a path that has been shown to consume attacker files as root.

## 2026-10-31 — the CVE match was wrong, and that is the finding

- Automated matching produced a high-severity hit on libpng, and inspection killed it: the defect lives in a
  contrib utility that is not shipped in the image at all. A report built on the machine output would have been
  confidently false.
- Everything else came back empty, which says more about the sparsity of advisory coverage for old libraries than
  about the safety of the image. Both halves of that are now written down.
- The register ends where it should: a dated, privileged, reachable parsing stack, with no invented vulnerability
  attached to it.

## 2026-10-31 — a run that produced nothing is not a negative result

- Two trace attempts came back empty, and the correct reading is that the instrumentation did not capture anything,
  not that the client withheld configure events. This is the rule this project keeps having to relearn, applied
  before the numbers were interpreted this time.
- The VM question is now well posed and externally unanswerable: the client commits without attaching. Pushing
  further from outside the process is wasted effort; the decisive move is to supply the missing buffer from a shim
  and see whether the scene lights up.

## 2026-10-31 — built the adaptor, then failed to exercise it

- The shim exists and does exactly one thing: if the client commits without a buffer, it supplies one. That is the
  whole hypothesis, expressed in code.
- The trial proved nothing because the application did not reach the compositor, and I compounded it by grepping
  the wrong log for evidence. Both are written down rather than smoothed over.
- Leaving this at "unexercised" is more useful than another attempt tonight: the next session can verify one line
  of shim output before drawing any conclusion at all.

## 2026-10-31 — a shim that kills the target proves nothing

- The symbol problems were real and are fixed: everything resolves at runtime now and the object loads.
- But the client dies silently under it, which makes the shim useless as evidence. Adding instrumentation that
  breaks the thing being measured is the opposite of progress, and it is better to say so than to keep running it.
- The correction is clear: touch only the commit path, take the display lazily, and make any failure visible on
  stderr before attempting the experiment again.

## 2026-10-31 — the hook that could never fire

- The object was loaded, the client was healthy, and nothing happened. The reason is a detail of wayland's client
  API: the functions one would naturally interpose are inline wrappers, so the symbol is never called by anyone
  compiled against the header.
- This is the third distinct explanation for the same symptom — no output — after "the client did not start" and
  "the log was in the wrong place". Each was cheap to disprove once the right question was asked, and the
  questions were only obvious in hindsight.
- The corrected hook point is a level lower, at the marshalling function every call actually goes through.

## 2026-11-03 — pathname verification is not object identity

- Exact AppDMClient caller review closed the static half of the updater source-
  stability question. The verifier returns an integer; later AppUpgrade staging
  and XML parsing resolve pathnames again, without carrying an open description
  or revalidating object identity.
- That is a necessary TOCTOU structure, not proof that a source can change in a
  real run. Runtime mount policy, ownership, uid/SMACK access, serialization,
  timing, a changed object, later inner authentication, update acceptance, root,
  boot acceptance and persistence remain separate gates.
- Added V-031, retained exact machine code, and an exhaustive bounded model that
  leaves runtime substitution feasibility unknown absent explicit mutability or
  immutability evidence. No updater, pathname race, launch request, package,
  target execution, partition or slot operation was exercised.

## 2026-10-31 — some doors are closed, and saying so is the work

- Three interposition points, three structural reasons they cannot work. The last one is the interesting one: the
  function that must be hooked is variadic, and C cannot forward an unknown argument list. That is not a missing
  idea, it is a language limit.
- The valuable output of this stretch is the closed list: what was tried, why each failed, what remains. That is
  more useful to whoever picks this up than another evening of attempts.
- This is the fourth time in this thread that a silent zero turned out to be an instrument problem rather than a
  target problem. The pattern is now well documented, which is its own deliverable.

## 2026-10-31 — a test that produced almost nothing, and says so

- Feeding junk at a root parser is the obvious next move and it produced the obvious non-answer: no crash, which
  means nothing at all. Recording it as worthless is more honest than dressing five truncated files up as a fuzzing
  campaign.
- One real thing came out of it: images never reach a parser on this path, because the scan directory is typed for
  audio. The inventory in V-014 implied a broader surface than the configuration actually exposes.
- The instrument was the problem again, in a new form: crude mutations cannot find bugs that require valid
  structure. The next attempt needs a generator, not more bit flips.

## 2026-10-31 — clean merges, colliding meaning

- The register had grown to V-032 under another workstream while three of my sections reused V-012, V-013 and V-014.
  Every merge succeeded and every number was wrong, which is the failure mode version control cannot see.
- Renumbered, converted the leftovers into clearly-marked amendments, and wrote a provenance note so that citing a
  bare number stops being possible in good conscience.
- Worth keeping as a general lesson for shared documents: identifiers allocated by position are not identifiers at
  all once more than one author appends.

## 2026-10-31 — my conclusion was wrong, and the register caught it

- I had eliminated the launcher as a first stage because every target I could find was a literal on read-only media.
  The register's newer entry shows the target is a string supplied over D-Bus at runtime, which a literal survey
  could never see.
- This is the most useful kind of correction: it does not just fix a fact, it revives a chain. The same-uid HMI
  boundary in that entry is precisely what the environment-file and trust-anchor entries need.
- Writing down that my own commit was refuted is the point of keeping a register with evidence grades. A record that
  only ever accumulates confirmations is not a record, it is a press release.

## 2026-10-31 — three threads turned out to be one thread

- The launcher test failed for a reason that explains several earlier failures at once: it waits for the vehicle
  daemon, and the daemon cannot reach the bus. The ask sequence in its output is the one measured from the MICOM link
  weeks of work ago.
- Reading the vendor startup scripts also closed the V-012 mechanism properly: the session-bus environment file is
  written by the vendor's own script into world-writable /tmp, so the exposure is their design, not an inference.
- The chain is not disproven, it is behind a bug we cannot fix without vendor source. That is a better statement
  than "unverified".

## 2026-10-31 — the vehicle link answered a real client

- A small adaptor took the bus name the vendor daemon holds but never serves, and the launcher immediately started
  getting answers to the asks that had blocked it every previous run.
- That is the first time in this project that the vehicle-interface dependency has been satisfied at runtime rather
  than simulated in a transcript. The asks in the log are the same three names that appeared as failures for rounds.
- The launcher still had not finished starting when the run ended, so the launch-bypass test remains unrun. But the
  blocker has moved from "the daemon cannot publish" to "the launcher needs longer", which is progress of the useful
  kind.

## 2026-10-31 — the launcher came up

- Poll six: the name appeared. A vendor client that had refused to start in every previous attempt is now running,
  because a small adaptor answered the questions it asks of a board we do not have.
- It even began dispatching app requests of its own, which is the difference between "registered a name" and "working".
- The launch-bypass test still did not fire: my call used guessed argument types and produced nothing. But that is a
  signature question now, not a blocker, and the interface is reachable to introspect.

## 2026-10-31 — the signature, not the exploit

- Introspection gave the exact five-argument signature, which retires a guess I had been making for two rounds. The
  call now reaches the service cleanly and still does not execute anything.
- The interesting result is elsewhere: the launcher unit reports "Started" for the first time. A dependency that has
  been blocking this work from the start was satisfied by an adaptor we built, not by anything from the vendor.
- Naming three candidate reasons for the remaining gap is more useful than another blind attempt, and each is
  checkable in one run.

## 2026-10-31 — a matrix that only half ran

- Three variants were queued and only one reached the log, so the honest label is inconclusive rather than negative.
  Reading the surrounding output explains it: the launcher spends that window walking /app/bin to build its registry,
  which is precisely the table that decides what a launch means.
- The practical lesson is sequencing: waiting a fixed number of seconds was fine for registration but wrong for
  issuing requests, and the correct signal is the registry sweep completing.
- Also worth recording: our displacement of the vendor daemon works but provokes systemd to restart it and log a
  registration failure. Functional, not tidy.

## 2026-10-31 — the calls fired, and the answer was in the setup

- With proper sequencing two of three variants actually reached the launcher and neither launched anything. That is a
  real negative for those two, finally.
- The reason looks structural rather than adversarial: the launcher enumerates /app/bin at startup to build the table
  it dispatches from, and our probe files were created after that enumeration. Offering a target that was never in
  the registry cannot succeed whatever appid is supplied.
- This is the same class of error that has dogged the whole VM thread — the instrument and the target disagreeing
  about when things exist — and it is now a one-line fix rather than a mystery.

## 2026-10-31 — the hypothesis was good and the answer was still no

- The registry explanation was tidy and testable, and testing it produced another silent no. Three attempts now, each
  with a better-founded setup than the last, and none executed.
- The right response is to stop rather than invent a fourth. What remains is either a security module decision that
  needs a real unit to observe, or a dispatch precondition buried in vendor logic we cannot see.
- Being clear that the static finding stands while the runtime claim is unmade is the whole discipline of this
  register. A plausible route is not an exploit, and three failed reproductions are the evidence for saying so.

## 2026-10-31 — reading the log beat another attempt

- Two of the three candidate causes were resolved by inspection instead of experiment: no SMACK denial exists anywhere
  in the boot, and our request never appears in the dispatcher's log at all.
- The launcher is visibly stuck retrying appId 2 every 1.7 seconds, which explains both silences at once and points at
  a fix that has nothing to do with the launch call.
- This is the better way to end a stretch: not a fourth probe, but a reading of evidence that narrows the field and
  names the next action.

## 2026-10-31 — closing a line on evidence rather than hope

- The fourth premise was as good as the previous three and failed the same way: the call is accepted and never
  dispatched, while the launcher loops on an application that is now demonstrably running.
- That combination is the strongest available signal that the obstacle is inside vendor logic we cannot see, not in
  the emulation and not in my experimental design.
- Recording the full list of four attempts, with what each eliminated, is the deliverable. The next person should not
  have to rediscover that SMACK is innocent, the registry is innocent, and the dependency is innocent.

## 2026-10-31 — the thing that was actually broken

- What looked like a dozen separate failures in the launcher resolved into one behaviour: it retries an application it
  cannot start, forever, and dispatches nothing while it does. Twenty retries in a single boot, with the dependency
  running.
- Recording it changes the meaning of earlier negatives. V-028's runtime tests were measuring this loop, not the launch
  path, and now the register says so in both places rather than leaving me to remember it.
- The honest part is the boundary: observed in emulation, not characterised on hardware, no security impact claimed —
  and yet still the most useful thing learned about the launcher all session.

## 2026-10-31 — the better sentence was the wrong one

- I wrote that the launcher's retry loop persisted "even when its dependency is running". It is a stronger finding than
  what I actually measured, and I reached for it because it was stronger.
- The measurement could not support it: the process check was lost behind a systemd spinner and no exit was recorded, so
  liveness is simply unknown. The entry now says that, and so does its list of what is not established.
- This is the same failure this whole session kept producing, in its smallest form: preferring a satisfying reading to a
  supported one. At least this time it was caught before it left the building.

## 2026-10-31 — measured it properly the second time

- Capturing the pid to a file instead of letting a spinner eat it produced the number I had guessed at earlier: the
  application was running before the launcher, a different instance was running after, and the loop still ran twenty
  times.
- The improvement did not come from a better idea, it came from recording the value somewhere the console could not
  overwrite. That is a small lesson with a lot of history in this session.
- The caveat survives the better measurement: a changing pid cannot prove a spawned instance stays alive across
  retries, so the entry keeps its limit even while gaining its evidence.

## 2026-10-31 — the caveat resolved the other way

- Ten samples over twenty seconds returned nothing, which is the clearest kind of evidence: the dependency is simply not
  there while the launcher keeps retrying it.
- So the loop is a failure loop, not a poll. The entry that had been hedging in the right direction now states the
  opposite conclusion, and the hedge is retired because it was tested rather than carried.
- That leaves one log file to read, which is the cheapest possible next step and exactly where this should stop.

## 2026-10-31 — thirty-five bytes, and a lesson about shared files

- The whole stall reduced to one sentence from a log I had never opened: the next component asks for boot information and
  rejects the answer we invented. Every layer we built works; the data is wrong.
- It also caught me committing badly. A blanket add swept a parallel workstream's changelog entry into my commit under my
  own message, and my register edit had silently not applied because the anchor had changed. Clean merges, wrong
  contents — the same failure the numbering collision taught, in a different disguise.
- From here: stage only my files, and verify each anchor matched rather than trusting a green commit.

## 2026-10-31 — an assumption corrected before it wasted anyone's time

- I had written that the next step was easy because the binary carried debug information. It does not: no debug sections
  at all. The corrected plan is harder and is now stated as harder.
- What the disassembly did yield was a map: the strings, their references, and a comparison against 0x1c right before the
  validity log. That is a foothold rather than a finding, and it is labelled as such.

## 2026-10-31 — the check I found was not the one rejecting us

- The length comparison looked like the answer and is not: our payload passes it comfortably. The rejection is further
  down, and the more likely culprit is a shared-memory object that does not exist rather than bytes that are wrong.
- The next move is one this project has already used successfully: watch which qipc files the binary opens. Guessing
  produced six wrong segment names once; strace produced the right ones immediately.

## 2026-10-31 — the tool that worked before was the wrong shape this time

- openat found no qipc path because there is no file: ApplicationManager's boot-info attach is shm or D-Bus, and the file
  tracing that cracked AppHomeScreen simply does not see it.
- Recording the failure of a favourite technique is worth as much as recording its success — otherwise the next attempt
  starts from the same wrong assumption I did.

## 2026-10-31 — the index is not mine

- A commit of mine swallowed eleven files belonging to a parallel workstream, because their content was already staged and
  a paths-scoped `git add` does not shrink an index. Everything landed intact, and they have recorded the provenance
  themselves, but the mechanism is worth writing down.
- This is the same error as the earlier swept-changelog-entry, and the same root cause: assuming `git add` scopes a
  commit. It does not. Only `git commit -- <paths>` does, and checking the staged set beforehand is cheaper than
  discovering it afterwards.
- Held off all staging while the other workstream corrected the record, then wrote this note into a clean tree so it could
  not contaminate their commit. That part at least was done in the right order.

## 2026-10-31 — the bus was fine, and my last trace was worthless

- Inside the real boot the connections succeed and the failure persists, which retires the D-Bus explanation cleanly.
- More important: the openat trace I built the previous conclusion on was taken from a process that had already exited. The
  conclusion drawn from it, that the attach is not file-backed, was therefore unsupported and is withdrawn rather than
  quietly left standing.
- Two of my last three hypotheses have now been killed by my own measurements. That is the process working, however
  it feels.

## 2026-10-31 — knowing when to stop building instruments

- With a validated setup the answer was still no: no shared-memory file, no device socket, and the buses already proven
  reachable. Two mechanisms are now excluded by evidence instead of argument, which is progress of the durable kind.
- The instruction to stop matters as much as the result. Each new instrument for this question has first been wrong in a
  subtle way, and the cost of discovering that has exceeded what the question is worth today.
- What remains is bounded and nameable, and the next attempt should be a full syscall trace or vendor source, not another
  experiment of my own design.

## 2026-10-31 — the untargeted trace answered what four targeted ones did not

- One full trace named the failing step: the interface is valid, the call is retried, and with a peer present the reply is
  still rejected. Everything about reachability is now settled, and what is left is the content of thirty-five bytes.
- Four instruments, three invalid first. The lesson is not "trace harder", it is that targeted tracing kept constraining
  the view to what I already believed, while the untargeted one showed me the sentence I needed.

## 2026-10-31 — five instruments, five invalidities

- The oracle test ran cleanly and proved the service was not running, which means the payload question is exactly where it
  was. Recording that as a failure to run the experiment rather than a finding about the payload is the only honest
  reading, and it is the fifth time this question has been blocked by my own setup.
- What has been genuinely settled is narrower but real: not the bus, not the file-backed attach, not the interface. The
  remaining unknown is the content of thirty-five bytes, and it needs either a live peer or a static reading of the
  parser.

## 2026-10-31 — six failures, then a real answer

- The peer never started because I had installed it in one workspace and tested in another. One stat call would have shown
  it at any point in the last five attempts, and instead I built four increasingly elaborate instruments around a missing
  file.
- With that fixed, the payload question answered itself: the peer answers, the client asks, and the reply is rejected. The
  blocker has been the content of thirty-five bytes all along, which nothing I ran before could have shown.
- The lesson is the least flattering of the session: check the binary exists before tracing what it does.

## 2026-10-31 — the oracle works and the guessing does not

- Three payload variants, five client instances, one answer: rejected. The instrument is finally sound, which makes the
  negative credible rather than another artefact.
- Stopping here is the right call. Thirty-five bytes with unknown meaning is not a search space to brute-force, and the
  next real step is reading the parser on a stripped binary — work with a defined shape, not another experiment.

## 2026-10-31 — handing off rather than grinding

- One more step into the parser showed why it is slow: the rejection is silent and the validity block has no direct branch
  into it. That is a real difficulty, recorded as such, rather than a lack of effort.
- The value of this stretch is the consolidated hand-off: three mechanisms excluded by measurement, the blocker confirmed,
  three payloads tested and rejected, an oracle that works, and anchors with the specific obstacle named.
- Stopping here is right. The remaining task has a defined shape and needs disassembly time, not another design of mine.

## 2026-10-31 — checking the repository is part of the work

- A read-only pass confirmed what matters for a public repository: no duplicate register numbers, no host paths in the
  documents I maintain, tool sources tracked, binaries ignored.
- The worktree also holds a parallel workstream's uncommitted edits, which I have left exactly alone and noted here so the
  record does not imply otherwise.

## 2026-10-31 — the parser was never the whole story

- Reading further into the same log produced the most useful line of the day: after failing the boot-info attach, the
  client initialises a MICOM shared-memory region and reports its source pointer as NULL. The missing thing is a provider
  of that region, not a nicer D-Bus payload.
- That single line explains two earlier puzzles at once — why every payload variant was rejected, and why no qipc file was
  ever opened. I had been looking for a file when the code wanted a pointer.
- The narrower claim I was about to hand off would have sent the next person into the parser for a fault that lives one
  layer below it.

## 2026-10-31 — my own reframing was wrong, and the disassembly said so

- I had concluded that a missing shared-memory provider explained everything. The code shows a QSharedMemory being detached
  three instructions earlier: it is a destination, and pszSrc is the data that should have filled it.
- So the failure is still the boot-info retrieval, exactly where it was, and the previous entry's tidy explanation is
  withdrawn rather than left to mislead.
- Worth noting the shape: the wrong answer was more satisfying than the right one — a hidden provider is a better story
  than a retrieval call that fails. That is why it needed checking.

## 2026-10-31 — another good hypothesis, another clean no

- The missing /dev/shm looked like the answer, since a missing /dev/pts had genuinely broken things earlier in this project.
  Providing it changed nothing, which is a clean elimination rather than a vague result.
- Two things are worth keeping from it: the environment gap as its own small finding, and the growing list of eliminated
  candidates for the retrieval failure — bus, /dev/shm, peer, payload, file-backed paths.

## 2026-10-31 — a fix that was really an empty run

- One configuration made the failure line disappear, and the reason was that the code never reached it. Checking the log
  for the function's own entry line turned a would-be celebration into a correction.
- The ordering in the log is worth more than either error message: the shared-memory initialisation happens before the
  D-Bus ask, and its NULL source is the failure that reproduces. That points at a MICOM status region whose name the binary
  itself mentions.

## 2026-10-31 — the last easy answer, gone

- Creating the named segment changed nothing, which is the useful part: existence was the final cheap hypothesis and it is
  now measured and excluded.
- What remains is a structure layout, and this project already knows what a rejected structure looks like — the zero-filled
  D-Bus payload that a validating parser would not accept. The same reasoning now applies to the region.
- Stopping here is deliberate. Everything environmental is excluded by measurement, the instruments are documented, and
  what is left is disassembly time on a stripped binary.

## 2026-10-31 — the shortcut was worth testing and does not exist

- Harvesting a populated region from the vendor daemon would have answered the layout question by observation instead of
  reading assembly. The daemon creates no such region, so the shortcut is closed and the honest route is disassembly.
- Worth recording precisely because it was the best remaining idea: knowing it is unavailable stops the next person from
  spending a session on it.

## 2026-10-31 — publishing, with the one thing I would not do silently

- The README now carries the session's outcome with two real captures: one showing the compositor rendering through our
  backend, one showing the black HMI frame and saying why it is black.
- Publishing to the second repository required a judgement: it shares no history with this one and is nineteen commits
  ahead in its own right, so a main push would have destroyed work. A branch is the reversible option, and reversible is
  what an unasked-for force-push is not.

## 2026-10-31 — combining two histories without erasing either

- The repositories had no common ancestor, so the only honest way to join them was a merge commit with both mains as
  parents: each side fast-forwards onto it and neither loses a commit. That is the difference between combining and
  overwriting.
- Thirty-nine files had to be chosen between because unrelated histories make every difference a conflict. Newest-won, with
  the losing versions still reachable from the parents, and presence checks run afterwards on artefacts from both sides
  rather than trusting the merge to have done the right thing.

## 2026-10-31 — combining properly, and being told when I had not

- The first merge took the newer side per file and called it a combination. It was not: it sacrificed one lineage's text in
  every conflicted file. Combining means both, and that is what this round did, with eight workers on disjoint files.
- The register was the delicate part. Nine findings arrived numbered V-006 to V-013 and I-001 — numbers this lineage already
  used for different findings. They are now V-037 to V-044 and I-002, each carrying a line naming its original number, so old
  citations still resolve and no claim was dropped.
- Where the two lineages disagree on facts, both statements survive with a marker for a human. A merge that silently picks a
  winner is how a register stops being a record.
- Two things were deliberately not merged and are written down: the parallel rootfs patch internals, because ours is a
  safety superset, and a failing privacy test that fails identically in both lineages.

## 2026-10-31 — the failing test had two causes, not one

- The inherited failure looked like a single scope omission. It was two: vm/ was outside the scan, and .qml was outside the
  text suffixes, so a QML file would have been skipped even with the directory in scope. Fixing only the first would have
  looked like a fix and changed nothing.
- The remaining five suite errors are a missing pytest, not a merge defect — the tool modules are present on both sides. That
  distinction matters because the instinct is to attribute every red test to the merge.

## 2026-10-31 — the suite is green, and the inherited code is verified by it

- Five modules had been reporting as errors for want of pytest and cryptography. In a virtual environment they run, and all
  seventy-eight of their tests pass — which also proves the code that came across from the parallel lineage actually works
  rather than merely existing.
- Recording the commands and the expected count matters more than the number itself: a red suite that is red for a missing
  dependency trains people to ignore it.

## 2026-10-31 — the trace was lying, and the profile was already on disk

- Two corrections in one round. The instrument was wrong: QSharedMemory resolves its key with stat, so an openat trace could
  never see the file it wanted, and I had recorded that absence as a finding. And the payload I was trying to derive had
  already been decoded from the vendor's own logs in a document sitting in the tree.
- Even with both fixed, the client still rejects the reply and still reports a NULL source. Progress that stops at "now we
  are asking the right question" is still progress, but it is not an answer, and the entry says so.

## 2026-10-31 — one more excluded, two kept

- Creating every path the client complained about changed nothing, which closes the missing-input theory honestly.
- The sweep did produce two facts worth having on their own: the client wants a second MMC device, and it wants the /Data
  resource table. Both are fidelity gaps in the projection rather than bugs in the client.
- The remaining question is inside one function, and no further external experiment will reach it.

## 2026-10-31 — the answer was in four instructions

- Reading the branch that prints the NULL message showed what it actually tests: data() on the client's own shared-memory
  object. No external provider exists, and every theory I pursued was a stand-in for that simple fact.
- Both environment strategies then failed against it, which is the useful form of a negative: it localises the fault to the
  attach call rather than to the world around it.
- This should have been the second thing I did, not the twentieth. Disassembly costs minutes; the experiments cost rounds.

## 2026-10-31 — names from the binary, and the environment stops mattering

- Reading two call sites gave both keys and both attach idioms: one attaches a pre-existing region, the other creates a
  size-8 region first. With the region supplied, both succeed and the log's own error counter reads zero.
- The remaining NULL therefore belongs to a third handle rather than to anything I could create, inspect or mount. That is
  the narrowest this has been, and it came from reading four call sites rather than from another evening of experiments.

## 2026-10-31 — knowing where the snippets stop helping

- The last structural theory — that the NULL handle is a copy of an attached one — is dead: there is no copy constructor
  imported at all, so each handle carries its own key and the third one simply has not been attributed yet.
- That is the right place to stop this line. Three rounds of call-site reading each narrowed the question without closing it,
  and the difference between "one more grep" and "an hour in a constructor" is worth naming rather than ignoring.

## 2026-10-31 — closing a line rather than circling it

- All four shared-memory regions the client names now exist and are seeded, and it still reports the one handle as NULL. That
  is the signal to stop treating this as an environment problem: the objects are there, and the client's own logic concludes
  otherwise.
- Nine rounds of exclusion produced a precise description of a vendor defect and no workaround. That is a legitimate outcome
  and it is written as one, with the facts retained and the speculation kept out.

## 2026-10-31 — combining found the same bug twice, which is what independent work looks like

- Six of the imported entries described findings this lineage already had. That is not an error by either side; it is what
  happens when two teams look at the same firmware. Marking them as duplicates with both bodies kept is the honest handling:
  the corroboration is worth something, and the evidence does not disappear.
- Three imports were genuinely new, including the environment-file mechanism that had been described inside another entry for
  rounds without ever getting its own number.
- I also caught myself writing a summary count from memory rather than counting, and corrected it against grep before
  committing. A register's headline number is the part most likely to be quoted out of context.

## 2026-10-31 — the merge put two verdicts on one bug

- Duplicate entries were easy enough to mark. Duplicate entries that disagree about whether the bug is exploitable are a
  different problem, and that is what V-037 and V-006 were doing side by side.
- Resolving it meant keeping both texts and putting the reconciliation where a reader would hit it, because deleting the
  imported claim would have hidden that it was ever made. The defect is real; the reachability is not; the register now says
  both, in the right order.

## 2026-10-31 — checking the citations survive the merge

- A register whose entries point at files that no longer exist is worse than one with fewer entries, so every cited path was
  resolved after the combination. All one hundred and one are present.
- That closes the merge: content combined, duplicates marked, the contradictory severity reconciled, the count corrected
  against grep, and the citations verified.

## 2026-11-07 — the harness removed the EGL hide transition it needed

- The primary Navigation window is no longer an unknown Shm/Egl instance.
  AppNavi constructs a QQuickView, Qt Quick requests an OpenGL surface, and the
  launcher/compositor bind it to surface 3000. That makes the recovered Wayland
  EGL path—not the common Shm detach branch—the relevant backend.
- The decisive difference was in the harness environment. The retained
  integrated Home→Navigation runs that exhibited the blocker forced Qt Quick's
  basic render loop. Exact vtable binding shows basic hide only fires
  `aboutToStop`; it does not release
  the GL context or invalidate the EGL surface. The authentic false-visibility
  log was real, but the expected null attachment could not follow through that
  selected route.
- The threaded path has the missing static chain. Its obscure event calls
  `QOpenGLContext::doneCurrent()`, the recovered Wayland EGL context invokes
  `QWaylandEglWindow::invalidateSurface`, and the vendor implementation destroys
  the EGL surface then attaches null and commits. That is precisely the route
  capable of producing the zero-size/BG notification that replays cached status
  5 through ApplicationManager.
- This explains the retained basic-loop behavior without inventing BG or a
  success callback. It is not runtime acceptance: an integrated threaded run has
  not yet shown the obscure event, backend invalidation, BG, latch replay,
  Navigation ID 30, or valid composition, and the mixed graphics stack remains
  an explicit boundary.
- A second correction removes a false narrative from the old sequence. The
  return to Home was requested by the harness with event 302/reason 322; it was
  not an autonomous Navigation loading/fallback timeout. The status consumer
  itself still has no direct Home-ID-11 edge.

## 2026-11-02 — status 5 was not the failure value

- Corrected an interpretation that the sender's `SendNaviBootFail` name had left
  unresolved. ApplicationManager's concrete map and menu callbacks treat 5 as
  the only positive launch status: 5 enables their handoff path, while every
  other value clears play-enable and returns.
- The real gate is the separately latched window byte. With window zero the
  manager caches 5 but never calls the map/menu handlers. Its authentic BG path
  sets the byte to one and replays the cached value, exactly the sequence absent
  from the retained VM runs.
- This narrows the integration task to genuine first-hide/unmap/BG behavior. It
  also separates the later Home fallback from the status consumer, which has no
  direct Home-ID-11 edge in the inspected routines.
- The next static branch explains why a visibility callback is not enough. The
  recovered QtWayland client explicitly detaches on hide only for a Shm window;
  its Egl path skips that commit. Public v5.4.1 did not have that condition.
  AppNavi mapped the exact EGL plugin, but the primary window instance's class at
  first hide remains to be observed before blaming the mixed VM graphics stack.
  No synthetic event, target execution, VM mutation, or new vulnerability claim
  was used to reach these corrections.

## 2026-10-31 — reading the other lineage's script ended a week of guessing

- The parallel lineage had already solved both of this thread's blockers and published the script. Running it here produced a
  live AppHomeScreen, a dispatching launcher, and a MICOM region with the authentic profile and twelve attachments.
- The four differences that mattered were all mundane: which shell module, which software EGL tree, unsetting a variable the
  vendor appends to, and two extra passwd entries. None of them were discoverable by reasoning about the failure.
- The lesson is uncomfortable and worth keeping: after the merge, I searched this repository for clues about the blockers and
  found the contract document, but I did not read the reproduction script that had already fixed them.

## 2026-11-08 — the first hide was not waiting where the logs made us look

- The next action had been framed as finding the primary
  `onForeground(false,...)` call. That was incomplete. The exact AppNavi direct-
  call inventory has two Qt window hides, not one: the foreground override and a
  type-`0x103` visibility-event handler.
- The base foreground method can create that same visibility event on a bounded
  Gen5/platform branch, and the Linux event handler maps zero to hide and
  nonzero to show. This recovers an authentic queued route without inventing a
  compositor notification or manager callback.
- Saved ordering changed the runtime question. The false-visibility callback
  appears immediately after compositor FG and before accepted status 5, while
  every retained Linux-screen foreground diagnostic arrives more than two
  seconds later. The later screen-6/9/10 calls cannot identify the earlier
  callback's producer.
- The evidence still stops at the right boundary: absent event-handler
  diagnostics and possible dropped logs mean neither hide call is proved at
  runtime. A future observation must distinguish them, then follow the real
  threaded EGL invalidation and BG sequence. No VM run or event synthesis was
  used to close the static architecture.

## 2026-10-31 — the screen is not black after all

- A real 1920x720 frame came out of the VM: the Hyundai splash, painted by the vendor compositor. For most of this session I
  had been recording "the client never attaches a buffer" as a vendor defect, when the actual cause was my own backend and
  shell choice.
- The correction matters more than the image. It means the emulation stack is further along than the records said a day ago,
  and that the honest description of the remaining gap is "the compositor stays on the splash layer" rather than "nothing
  draws".
- Second capture byte-identical at 155 seconds, which is the useful kind of duplicate: it says the splash is stable, not that
  the capture failed.

## 2026-10-31 — a window, but not yet a screen

- The later chain produced a mapped, decorated client window with an empty content area. That is progress of a specific kind:
  the compositor is presenting a client surface, and the application is not painting into it.
- Keeping both captures matters. The splash says the compositor can paint vendor artwork; the decorated window says a client
  is mapped. Neither alone would tell the next person where to look.

## 2026-10-31 — the root path works

- A single D-Bus call with a caller-supplied path produced a root shell's output in a marker file. After a day of failed
  attempts at a different method, the working entry point turned out to be one the published chain already used.
- The discipline that matters here is what the register now says alongside it: the caller in this test was root, so what has
  been demonstrated is the code path, not an escalation from an unprivileged subject. The severity question moves to the bus
  policy, and it stays open until that is tested.
- Worth noting the contrast with V-037, where a claim of demonstrated root execution turned out to rest on a harness artefact.
  The difference is that this one was reproduced from a clean state, with the evidence being a file the target process wrote.

## 2026-10-31 — confirming the capability and then its limit

- The root execution is real: a caller-supplied path runs as uid zero. The next question was whether anyone who is not already
  root could trigger it, and the answer is no — the session bus will not even answer a uid-1000 client.
- What remains on the record is the difference between "a genuine defect" and "an exploitable one". The missing validation is
  worth fixing regardless; what does not survive is the idea that it lifts an unprivileged user to root.
- Notably the parallel lineage had reached the same boundary independently, which is more reassuring than my own measurement
  alone.

## 2026-10-31 — the app is alive and registered, and the simulator is refusing questions

- AppHomeScreen registers with the launcher as a live app, so the failure is not that it never arrives; it arrives and then
  paints nothing.
- The launcher's log also shows the chain's MICOM simulator rejecting the settings asks outright, while this project's own
  service answers them. That is the first concrete candidate for the blank content that is not another layer of the display
  stack, and it is a one-line substitution to test.

## 2026-10-31 — the lever moved and the needle did not

- Replacing the simulator with our own service removed every "method not implemented" complaint and answered seven calls. That
  is real, and it is not the finding I was looking for.
- The application had not started when the frame was taken, so the screenshot is the splash again. An identical image after a
  meaningful change is the easiest thing in this work to misread as confirmation.

## 2026-10-31 — a two-minute delay is a result too

- With our own service answering, the application still arrives and registers — just much later. That reframes the
  substitution from "does it help" to "it changes timing", which is the kind of observation that only comes from running the
  longer window.
- The frame still was not captured, and I am recording the required window size rather than pretending the earlier attempt
  counted.

## 2026-10-31 — the script was deleting the evidence before I looked

- The chain kills every process it started and archives what it captured. Waiting for it to finish and then screenshotting was
  never going to work, and the empty screenshot directory made that plain.
- Both captures I do have came from external screenshooter calls against a live chain. That is the method, and it is now
  written down rather than rediscovered.

## 2026-10-31 — three frames, one sentence

- Splash, then black, then a decorated empty window, captured at three stages of one run. Together they say something simple and
  useful: the compositor works at every step, and the application never paints.
- That is the cleanest description of the VM gap produced all session, and it came from capturing at the right moments rather
  than from any new tooling.

## 2026-10-31 — asking two stronger models, then testing what they said

- Astra and Opus 5.5 were reachable after all, via the model catalogue rather than a tool description. Both ranked causes, and
  both corrected me on the same point: the decorations are Qt client-side and the white area is the default clear colour, so the
  client is very likely committing frames.
- Testing that produced the real answers. The launcher sends the app's stdout and stderr to /dev/null, which is why no QML or
  EGL error was ever visible; strace saw the buffers instead and showed the app alive and requesting QML loads at two and a half
  minutes. And the splash is simply never dismissed — identical frames at 185 and 230 seconds.
- So the failure is not the display stack. It is a splash that nothing removes, and an app whose messages are being discarded.
  Both are specific, and neither would have been found by another round of screenshotting.

## 2026-10-31 — two faults, not one

- The splash turned out to be a program, `/usr/bin/early-background`, holding an IVI surface with the boot image and never
  exiting. Killing it changed the frame from the splash to black, which settles that question and immediately opens another.
- With the splash gone for two and a half minutes, the application still paints nothing. So there were two independent faults
  the whole time, and every earlier "blank screen" observation was describing whichever one happened to be in front.
- Naming them separately is the useful outcome. The next test distinguishes the last two possibilities for the second fault,
  and it can be done from the buffers the launcher throws away rather than from screenshots.

## 2026-10-31 — nothing to draw, because nothing was drawn

- The client never attaches or commits a buffer. Not slow, not misplaced, not stuck on a frame callback: it simply never hands
  the compositor a frame.
- That retires a great deal of the session's reasoning in one measurement. The compositor, the backend, the pixman renderer, the
  software GL stack and the IVI layer assignment were all being investigated for a fault that lives entirely in the client.
- The honest version of today's earlier entries is that they were describing the absence of a frame in ever finer detail. This
  is the first one that names the party responsible.

## 2026-10-31 — three causes, and the last one was a single environment variable

- The vendor launcher preloads its own libEGL into every child. With that in place the application never commits a frame, no
  matter how long it runs; without it, the same binary against the same compositor builds the home screen and paints.
- That is the most consequential line of the day, and it arrived from Astra's ranked list, tested rather than believed. Its
  advice to ignore the splash until frames appeared was equally load-bearing: chasing the splash would have hidden this.
- The honest summary of the blank screen is now three independent faults and no fault in the display stack.

## 2026-10-31 — the application finally gets to speak

- Bypassing the launcher stopped it throwing away the app's diagnostics. Reading them for the first time shows nine widgets
  failing on missing shared-memory keys, which is the same region family the MICOM work had already mapped.
- So the rendering fault and the simulation work were never separate problems. The screen is blank for want of data, and the data
  is the thing this project spent its effort learning to fabricate.
- The combination attempt was inconclusive and is recorded as such rather than as a result.

## 2026-10-31 — a fault narrowed to two milliseconds

- Seeding the MICOM region removed all nine shared-memory failures, which confirms that line of work end to end. What replaced
  them was a segfault with an address, and the vendor symbol table placed it inside qmlEngine(), fourteen bytes in.
- Vendor code trusted a QObject that was never created. Finding the fault took a kernel log line and a symbol lookup rather
  than another screen capture, and it moved the problem from "nothing renders" to "one component does not exist".
- Also worth remembering that a probe of mine reported zero seeded bytes because I read the wrong stream; the shim was working
  the first time.

## 2026-10-31 — the application said what was missing, and it was a directory

- Its own log named the file it could not find. The shipped tree has the home screen under qml_new2.0; the binary falls back to an
  unversioned qml/ path that nothing in the image creates. One symlink and the segfault disappeared.
- Five independent causes have now been found and removed, each one measured rather than assumed, and the application survives
  where it used to crash. It does not yet paint, but it no longer dies, and the log is the instrument to use next.

## 2026-10-31 — healthy, idle, and still invisible

- With the QML path fixed the application is demonstrably well: widgets load, the variant database opens, the heartbeat runs at
  1 Hz. It simply never presents a window.
- Removing the preload in the direct configuration makes it paint; removing it inside the full chain does not. The difference
  between the two is ApplicationManager, which narrows the remaining problem to appbase rather than to graphics.
- Recorded as a negative result, because the chain fix I expected to work did not.

## 2026-10-31 — a plan corrected before it wasted a night

- Inside the chain the app does more than standalone: it creates and shares an IVI surface. It still commits no buffer, so the surface
  is prepared and never given content.
- The wrapper idea I had committed to would not have worked. In chain mode stderr carries only Wayland protocol debug, because the
  launcher routes application logging to DLT. Better to find that out from one traced run than to build the wrapper and wonder why the
  log stayed empty.

## 2026-10-31 — the experiment answered its question, and the answer was no

- With ApplicationManager running and the app started by hand, clean and loggable, the screen still stayed black. So appbase being
  present is not the trigger; something specific has to ask the app to show itself.
- The app was healthier than in any previous run while being invisible, which is its own kind of result: health and visibility are
  decoupled here, and only the request matters.
- The caveat is recorded too: ApplicationManager had adopted the older process, so this excludes the simple hypothesis, not the
  hypothesis in every form.

## 2026-10-31 — the app answers the request and still does not appear

- The show request exists, the object exists, and the call returns one. It is the first time the application has acknowledged an
  instruction from us, and it did not change the screen.
- The same experiment killed the app outright when I used the shorter overload, which is a genuine security finding rather than a
  curiosity: any peer on that bus can terminate the driver-facing display with one message. It is in the register as V-045.
- Two things learned in one run, one of them about our problem and one about theirs.

## 2026-10-31 — the contract lied, and I had believed it

- The app's own introspection describes three signatures for showing and hiding its window. Only an undocumented fourth form works,
  and the documented hide call terminates the process. That is worse than a crash: the interface invites it.
- My earlier register entry repeated the introspection's claim of a four-argument overload. It was wrong, and it is corrected in place
  with a note rather than quietly edited.
- On our own problem: the app acknowledges the show request in both boolean states and still paints nothing, so the request is not
  what completes the picture.

## 2026-10-31 — thirty-seven arguments we were not passing

- The launcher hands the home screen a long list of variant flags. We had been starting it bare and wondering why the variant path
  mattered.
- Both configurations sit at zero commits in steady state, which also revises what that earlier light frame meant: it was a transient
  during startup, not a steady state we had achieved.
- The next comparison is obvious and cheap: the same binary, the same environment, the real argument list.

## 2026-10-31 — the graphics were finished some time ago

- The scene graph builds textures for a real window; the window is never shown. Every graphic-layer suspect had already been cleared, and
  this confirms the problem lives in the service landscape instead.
- The app subscribes to a hundred and eighty signals and waits. Building the rest of that world is the same craft as the MICOM responder:
  find what it expects, provide it, verify by observation.
- Astra's advice was to distinguish construction from visibility before doing anything else. Cheap version of that test settled it in one
  run.

## 2026-10-31 — the silence was our own unanswered mail

- The app's pending calls are asks our stub receives and ignores. Four methods implemented, dozens expected.
- That reframes the last several hours of graphics work: nothing was wrong with the picture, the system was never told to draw.
  The same lesson as the MICOM transport, arriving from the other end of the stack.

## 2026-10-31 — the pictures were in the machine and unreachable

- The UI images are shipped, but reached through a symlink into /tmp that nothing populates. Pointing it at the real tree removed every
  texture failure at once.
- That is the fourth missing boot-time step in this projection, after the splash, the QML variant path and the shared-memory regions, and it
  is the first one that explains a log line we had been reading past for hours.
- Also corrected a claim I made an hour earlier: the pending MMUS calls complete, they do not hang. The evidence for that was already in the
  log and I read it backwards.

## 2026-10-31 — fixing the pictures did not fix the screen

- The image path is genuinely the vendor's own, and nothing in the shipped system creates its target. That makes our reproduction step a
  documented assumption rather than a discovery of intent, which is how it is now written down.
- With assets loading and the splash gone, the frame is still black and the client still submits nothing. The one remaining fault is now
  narrow, stubborn, and out of reach of the instruments the image provides: there is no debugger in it.
- Astra's probe needs a gdbserver we do not have. Rather than pretend otherwise, the next attempt goes at the signal side, which is the only
  other surface left that can change the application's state from outside.

## 2026-10-31 — it was asking for a screen that may not exist

- The client binds the layout controller, requests screen nine, enumerates layers, and gives up. That is the first concrete thing it has been
  seen to look for and not find.
- It also weakens yesterday's signal theory: the signal it could not connect is its own.
- If the vendor expects a screen id this compositor never creates, then the fault is configuration on our side again, which is familiar ground.

## 2026-10-31 — the screen it wants is a position in a list

- Read the shell source and found the whole mystery of "screen nine": screens are numbered by output order, so a single-output compositor can
  only ever have screen zero.
- That converts the problem into something we control. Our backend can present more outputs; the vendor shell will number them; the app will
  find the one it asks for.
- The measurement is the request. The explanation is a hypothesis until a ten-output compositor says otherwise.

## 2026-10-31 — ten screens, and a compositor that stops on the first empty one

- The multi-output backend works: the layout finally has the screens the vendor app asks for. It also walked the compositor into an assertion it
  had never reached before, on a surface with no buffer.
- Something new and useful came out of it: in this configuration the splash program exits on its own for the first time, which suggests it was
  waiting for a layout it could recognise.
- The hypothesis about screen nine is still unproven. The compositor fell over first, and that is what the record says.

## 2026-10-31 — ten screens, no crash, no picture

- Running the app alone against ten outputs composites cleanly and produces a wide, pale image. Nothing in it came from the application, which
  still submits no buffer.
- The crash in the previous run needed the splash to die mid-composite, which is why it appeared only when the whole chain ran.
- Honest reading: the layout problem is closer to solved, the application problem has not moved.

## 2026-10-31 — the question was real, and the answer is a compositor crash

- With the launcher driving it, the app asks for screen nine ten times. The hypothesis had a real premise after all.
- But the compositor aborts on surface destruction even with the splash removed, so the ten-screen layout that makes the request answerable is also
  what exposes the crash.
- That is a vendor defect in how destroyed surfaces are composited, and it stands between us and the thing we actually want to see.

## 2026-10-31 — caught it in the act

- The log names the moment: a repaint across seventeen views, two surfaces whose destination rectangles had just been zeroed, an invisible ivi
  surface, and a client mid-way through creating a buffer. Then the assertion.
- That is a race in the vendor compositor, and it only bites because ten outputs make it composite many views at once.
- The way forward is not to fix their compositor but to stop asking it to do that work: present ten screens, render one.

## 2026-10-31 — two levers, both pulled, neither enough

- The repaint gate works and the shim gate works, and the compositor still dies. That is a clean negative result and worth more than another
  theory.
- What it says is that the ten-screen layout changes how the vendor stack talks to its clients, and the crash comes from that, not from anything
  we added.
- The next question is small and cheap: does it die with ten screens and no application at all?

## 2026-10-31 — the layout is innocent

- Ten screens, one splash, no application: everything survives. Add the application stack and the compositor dies.
- So the last several hours of layout work were not wasted but they were not the fault either. The fault travels with a client.
- The question is now small enough to bisect by disabling one program at a time, which is the sort of question that has an answer.

## 2026-10-31 — not that one either

- Remove the home screen and the compositor still dies, so the thing we have been trying to see is not the thing that kills it.
- Also caught myself trusting a probe whose baseline was wrong: weston was reported dead because it had not started yet. Two runs lost to a five-second
  race, and the record says so.

## 2026-10-31 — the compositor stops dying

- Our own backend named the culprit in one line per view: no client, no buffer, scissored. The vendor shell was compositing its own colour fills through
  a path that asserts on them.
- Opus called that exactly, and the fix needed no vendor surgery — a two-dozen-line interposer that gives a solid fill an actual format.
- Ten screens now run without aborting. The picture is still absent, but for the first time the ground under it is stable.

## 2026-10-31 — a third time, and caught each time

- A binary from another workstream rode into a commit because the shared index still held it. Checked the staged list, then committed anyway.
- It is kept, because it is the tool behind a cited security measurement, and its lack of source is written down instead of assumed away.

## 2026-10-31 — it never asks for a surface at all

- Not "asks and is refused", not "draws and is lost": the application never requests a compositor surface. The window exists as an object and is never shown.
- The show request over D-Bus changes nothing, and a slightly different one kills the process instead.
- The question has narrowed to a single internal condition, which is a question a binary can answer.

## 2026-10-31 — the number I kept quoting meant nothing

- The vendor HMI module was missing nine config keys and had silently never loaded. With those set it initialises and the compositor stays up.
- The static analysis then dismantled a claim I had repeated: the D-Bus reply I read as acknowledgement is only the echo of an argument I passed. Several
  entries in this log leaned on it. They are corrected here rather than left standing.
- What actually gates the picture is ignition status, which the application says it cannot obtain. That line has been in the log for hours.

## 2026-10-31 — four doors, all locked

- Emitting the ignition signals changed nothing, and the app already receives a power status of one. The correct app id in the show call changed nothing.
  Removing the competing application changed nothing.
- Each of those was a reasonable theory and each is now closed by measurement rather than by argument.
- What remains is the internal condition the static analysis could reach but not resolve: which reason and app id the app itself uses when the home screen
  is genuinely current. It also produced a second way to kill the process, which widens the security entry rather than narrowing it.

## 2026-10-31 — it was trying all along

- The tracer shows show() called, the window visible, and the vendor shell integration entering createShellSurface. The application was never the one
  refusing.
- Every earlier conclusion that the window "is never shown" was an inference from the absence of a surface. The absence is real; the cause is one layer
  further down, in code that ships as a library and reads an environment variable the launcher sets to zero.
- Astra's warning was the useful part: not having a surface does not mean nobody asked for one.

## 2026-10-31 — two failures, not one

- The environment-variable experiment could not conclude, because the application died at the moment it reached the thing being tested.
- The deaths are heap corruption inside free(), at an identical offset in two different vendor applications. They also happen in the untouched single-output
  configuration, to a third application we were not even looking at.
- So this environment has been quietly killing its clients all along, and several "no result" observations today were that, not a failure of the hypothesis.

## 2026-10-31 — the missing service in the middle of everything

- Three applications die in free(), and the vendor libraries they share turn out to depend on a service that is simply not present in this projection. The
  image ships the client, the interface and the policy, and no daemon.
- That is the same shape of gap this project has closed before, so it is worth a stub. Whether it explains the heap corruption is a question a run will answer.

## 2026-10-31 — the instrument broke before it measured anything

- The stub that was going to answer the heap-corruption question fell over at four seconds, jumping to the base of its own binary. No service, no test.
- Recorded as untested rather than as a negative: the difference between "the hypothesis failed" and "the experiment never ran" is the whole value of keeping this
  log.
- Also noted a measurement whose window was shorter than the failure it was looking for, which is the same mistake as the five-second race earlier today.

## 2026-10-31 — the service was not the cause

- With persistence actually running and serving, the camera application still dies in the same free(). The hypothesis is dead, and it died properly: measured past
  the failure latency, with the service confirmed alive.
- The stub stays, because the image genuinely lacks that service. It is not a cure and will not be described as one.
- Two questions remain and one of them is new: what the two remaining shared libraries do, and why the home screen vanishes without a segfault of its own.

## 2026-10-31 — supervision, not a crash

- The application that kept disappearing was being stopped by the manager after a sibling died, which is the manager doing its job. No fault, no leak, no OOM.
- Corrected my own previous entry, which had floated it as a possible defect. The evidence against that was already in the memory numbers.
- Also fixed a debugging tool that was drowning the console it was supposed to be observed through. Worth remembering that an instrument can be the problem.

## 2026-10-31 — the manager was fighting the experiment

- A hand-started application dies quickly whenever the chain's application manager is running, because the manager supervises the window owner and stops an instance
  it did not launch.
- That single fact quietly undermines a measurement method used all day. Several results were the supervisor, not the hypothesis.
- Third time today the instrument was the problem: a flooded console, a five-second race, and now a supervisor that treats my experiment as a rogue process.

## 2026-10-31 — the client was never the problem; the environment was

- The application creates surfaces, attaches a buffer and commits the moment it is given a forced, non-zero surface id. Without that it enters the vendor shell
  integration, declines, and returns.
- This has been the answer to "why does nothing appear" for the entire investigation, and it is two environment variables set by the vendor launcher to zero.
- Recorded with its caveats: the process died, no frame was captured, and the id I used collides with our layer numbering. But the surfaces exist now, and they are
  the application's own.

## 2026-10-31 — surfaces, a commit, and then a destructor

- With a surface id the application finally draws: surfaces created and a frame committed. It then destroys its weather widget and crashes inside that widget's own
  destructor.
- The surface question is closed. What is left is a plugin teardown fault that happens after the first frame, which is a different and much smaller problem than the
  one we have been carrying for days.
- Noted for the security side: if a signal can trigger that teardown, it is a way to take the display down.

## 2026-10-31 — the four megabyte black rectangle

- Eight identical frames, four megabytes each, and I nearly wrote "captured the home screen" in this log. Every pixel was zero. The file was large because it was
  text, not because it was detailed.
- The honest finding is better anyway: the application draws and commits, and nothing places its surface on a layer, so the screen stays black.
- Removed the mislabelled artifact. A wrong file in the record is worse than a missing one.

## 2026-10-31 — the manager builds its own environment

- The interposer that would have supplied the surface id could not reach the application, because the manager does not pass its own environment through. The launcher
  script is not the place where a child's variables are decided.
- That is a clean negative and it closes a route rather than a theory.
- What remains is genuinely two problems, both now named: supply the id somewhere the manager cannot strip it, and place the surface that results.

## 2026-10-31 — a tool that can place, and no id to place

- The placement client binds every vendor global and reports what it sees. What it sees is nothing, because this protocol announces objects as they are created and
  says nothing to a client that arrives afterwards.
- It also turned up a correction: the layer ids in our own configuration are not the layer ids the vendor layout uses.
- So this is blocked on discovering an id, not on building anything. That is a smaller and more honest problem than the one at the start of the day.

## 2026-10-31 — the vendor had a word for what we were missing

- The thing this project kept trying to build by hand already exists as a shipped protocol, with requests named for exactly what we want: make this surface visible,
  put it in the foreground, lay it out at this rectangle.
- That changes the shape of the remaining work from inventing a mechanism to driving the vendor's own one, which is the same lesson as the MICOM transport and the
  environment variable: the machinery is usually there, and the missing part is the driver for it.

## 2026-10-31 — building the tool raised a question worth filing

- The window-manager interface takes a surface id from the caller instead of deriving it from the caller's own connection. That shape allows cross-client window
  control unless it is checked somewhere, and nothing in the description suggests it is.
- It is filed as a candidate with every caveat attached: no cross-client attempt has been made, and the tool that would make one is the tool just built.
- Worth recording that this came out of solving a display problem rather than from looking for vulnerabilities. The register grows where the work goes.

## 2026-10-31 — accepted, and still black

- The compositor takes the placement requests without complaint, and the frame changes from exactly zero to single digits out of 255. Nothing above nine. That is not a
  picture.
- Worth recording that I measured it rather than eyeballing a screenshot and calling a dark frame "the night theme".
- One incidental observation for the security entry: requests naming surfaces the caller does not own were accepted. That is suggestive, and it is written down as
  suggestive, not as proof.

## 2026-10-31 — behind one crash is another

- Suppressing the weather widget's destructor fault revealed a heap corruption in free(). Two unrelated ways for the application to die, both inside a minute.
- Also learned that chmod cannot disable anything for a process running as root, which cost a run to re-learn.
- The honest position: the client draws and the window manager is driven. What is missing is a stable application and a surface actually shown on the screen.

## 2026-10-31 — one violation, not two bugs

- The application was never crashing for two unrelated reasons. Forcing a single surface id onto a multi-surface application made the surfaces collide, the compositor raised a fatal
  protocol error, and everything that looked like a crash was teardown happening after the connection had already been killed.
- Using the pid as the id removes the collision: the application stays up, creates its surfaces, commits, and the compositor names a window with real dimensions.
- The screen is still black. But for the first time the thing that should be on it exists in the compositor, and the reason it is not there is a placement question rather than a
  survival one.

## 2026-10-31 — the screen had content in it

- Found the recipe the archive was built from, reproduced it on a clone of the untouched reference image, and the capture has the application's own drawing in it: the night
  background, the wave, and two large text keys.
- They are untranslated keys, so this is a partial render rather than the archived screen. But it is the application's pixels, captured from the compositor, on an image whose
  hash was checked before and after.
- The difference from this week's runs was not a bug I fixed. It was an id the vendor declares, used without forcing it, and no variant arguments.

## 2026-10-31 — facts handed over with their limits attached

- The iAP2 socket is root-owned and world-writable, so file permissions are not what gates it. The service runs as root with no unit-level confinement, and SMACK policy
  labels only the device nodes.
- The one thing that would matter most — what label the process and socket actually carry on the vehicle — is exactly what this projection cannot provide, and the record
  says so instead of reporting the research init's default as if it were the vehicle's.

## 2026-10-31 — the socket only appears when the service is unconfined

- Labelling the process as System::iap20 stops it publishing the socket at all, reproducibly, even with rules that should permit the path. Unconfined, it publishes
  instantly.
- That is a constraint worth handing over: it means the service's vehicle label cannot be a confinement that blocks /tmp, and the unit declares no label.
- The admission test itself still cannot be run, because in the labelled runs there was nothing to connect to. Recorded as unmeasured rather than as a negative.

## 2026-10-31 — small facts, named dead ends

- The launcher path really does produce vendor surface ids: 1000, 1001, 2080. That is worth knowing and it is new.
- Three ways of getting the working surface id into the chain-launched application failed, and each failure narrowed where the value is actually set. The one
  injection point that can survive the manager's environment handling is replacing the binary with a wrapper; it is installed and not yet proven.
- Also closed a localization theory before spending longer on it: the archived full-tile run logged the same language-load failure, so raw string keys were never the
  difference.

## 2026-10-31 — I was measuring the wrong thing and calling it black

- A broken pixel metric made two captured frames look empty. Both had content. One of them shows the application's own window with its status bar, spinner and page
  dots. I had written "still black" about it.
- The second one is a field of diagonal stripes, which is what a stride mismatch looks like. That is a real, nameable defect and probably the reason a correct window
  turns into garbage on screen.
- This is the fourth instrument error in this project: a flooded console, a five second race, a supervising manager, and now a text parser applied to binary data. The
  habit that catches them is reading the file rather than trusting the summary of it.

## 2026-10-31 — zero by zero

- The screen size the vendor interface publishes is zero in every configuration tried, single output or ten. If the application sizes itself from that, the strange window
  geometry stops being mysterious.
- The vendor's own HMI client exists in the image and is the obvious thing to restore, but restoring it is not enough: started with no arguments it exits at once, so it needs
  the invocation the real unit uses.
- Recorded as an open lead with its failed first test, rather than as progress it is not.

## 2026-10-31 — the vendor config answered questions and killed three theories

- The real weston configuration was in the image all along. It explains the mysterious surface id (home-id 1007), gives the layer ids we had been guessing, and reveals that
  the vehicle has two screens, not one.
- It also let three plausible explanations for the zero screen size be tested and killed in sequence: output count, the HMI client, and output naming.
- What remains is narrower and specific: either the vendor DRM backend supplies that size, or the user-interface client at the path the config names does. Neither is running
  here, and the config names a path the image does not contain.

## 2026-10-31 — the stripes were probably my capture, not their compositor

- Four explanations for the zero screen size are dead. The likely answer is the vendor backend we deliberately do not run.
- More importantly, the sheared frame that sent me chasing a stride mismatch is much more likely a capture taken at the wrong width. A correct unsheared application
  window exists in the same family of runs, which is the evidence that settles it.
- Recording both because the second one corrects a diagnosis I had already written down.

## 2026-10-31 — the stripes were the camera

- The capture tool had 1920 by 720 written into it as constants and never asked the compositor what size its output was. Everything it saw at another size came out sheared.
- That is the fifth instrument fault in this project and the second one today that produced a false diagnosis. It is fixed, and the fix also makes black frames state their mean
  instead of leaving me to infer from bytes.
- The uncomfortable conclusion is recorded plainly: any capture taken at a size other than 1920 by 720 has to be re-measured before it is trusted, including the ones I used to
  argue the screen was empty.

## 2026-10-31 — two settings, two wrong answers

- Naming the outputs as the vendor config expects turns a black frame into a sheared one. Naming them the old way turns it back to black. Neither is a picture.
- That is progress of the honest kind: the fault is no longer "somewhere in the display path", it is a stride disagreement in our own backend's handling of a named output.
- Also worth saying plainly: after correcting two wrong diagnoses today, the display work is back to "not correct yet", and the record should not pretend otherwise.

## 2026-10-31 — placing it made it appear, and it appeared wrong

- Without the placement request the capture is empty. With it, forty percent of the frame has content, and every row is shifted relative to the last.
- That is the most useful pair of measurements of the day: the request works, and what it reveals is a geometry fault between a 1926-wide surface and a 1920-wide output.
- The one clean picture from earlier remains unexplained against the current behaviour, and rather than pick whichever story is convenient, both are written down.

## 2026-10-31 — matching the sizes changed nothing

- Setting the output to exactly the width the surface reports leaves the stripes exactly where they were. So this was never a negotiation problem.
- The slope is the clue that matters: one pixel of drift per line. That is a stride bug, and the likeliest place for it is our own backend, where the buffer is allocated from one
  width and read with another.
- Five explanations are dead. The sixth is in a file I can open, which is a better position than this afternoon.

## 2026-10-31 — the application is not lying about its own buffer

- It declares 1926 by 753 with a stride of exactly four bytes per pixel. Whatever is wrong, it is not the application misreporting its geometry.
- That leaves one seam: between the vendor renderer and the framebuffer our backend provides. Two stride values, logged side by side, will settle it.
- Six explanations are dead. The seventh is a comparison I can print.

## 2026-10-31 — the instrument is ready and the subject keeps leaving

- The stride comparison is built and deployed, and cannot fire because the compositor does not repaint when nothing is displayed. That is consistent with everything measured
  today: the placement request is what makes the application visible.
- Three separate runs were lost to the application exiting before the checkpoint. That is now the binding constraint on progress, not any missing knowledge.
- The next attempt polls instead of sleeping. Recorded because otherwise the next person repeats the same three runs.

## 2026-10-31 — our software was not at fault

- The number I predicted would settle a seam settled it the other way: mode, image and buffer strides all agree. The backend did not cause the stripes.
- With the application's own buffer also verified correct, the only component left in the path is the vendor's pixman renderer — the same one that needed an interposer to stop
  aborting last week.
- So the next test is not a measurement but a substitution: run the same scene through the GL renderer and see whether the stripes follow the renderer or the scene.

## 2026-10-31 — the substitute was not installed

- Asking weston for its GL renderer makes it exit before it draws anything, so the pixman hypothesis could not be tested. That is an infrastructure gap, not an answer, and the
  distinction goes in the record.
- One useful accident: the capture tool produced a frame from a compositor that was already dead. Any capture now needs to be paired with proof the compositor was alive.
- The next move is probably the one that has worked all along here: interpose in the vendor's pixman path rather than try to replace its renderer.

## 2026-10-31 — the suspicious thing was deliberate

- A one-pixel-per-row image inside the renderer looked like the answer. Forcing it to the natural stride killed the compositor, which proves the trick is intentional and therefore not
  the fault.
- Reverted the experiment and left the reasoning in the file, because this is precisely the sort of finding that gets rediscovered and re-broken later.
- Printing found the anomaly; changing behaviour explained it. Both were cheap, and only the second one makes the first trustworthy.

## 2026-10-31 — the last axis I could reach is closed

- The compositor will not run on its GL renderer here, with or without the flag. Everything reachable in this image has now been examined, and the stripes remain.
- That is where the day's work honestly ends: not with a picture, but with the list of things that are not the cause being longer than the list of things that might be.
- The suggestion worth carrying forward is not another theory but another measurement: read the application's own buffer instead of the composited frame, which would tell apart a
  rendering fault from a compositing fault without needing a renderer I do not have.

## 2026-10-31 — the hook did not exist

- The plan to read the application's own pixels needed to interpose functions that are not functions. Wayland's protocol bindings are inline wrappers around a generic marshaller, so
  there is no symbol to replace.
- That is worth knowing permanently: interposing by name works for libdbus and libpixman and does not work for libwayland protocol calls. The next attempt hooks the marshaller
  itself.
- Nothing broke, which is the one thing that went right.

## 2026-10-31 — a better instrument than the one I planned

- Instead of hooking a marshaller that does not exist as a symbol, the application's framebuffer can simply be read out of its own file descriptors. No interposition, nothing to
  break, and it works for any client in the image.
- The first attempt missed only because I put the call at the end of the script and the application had already gone. Ordering, not engineering.

## 2026-10-31 — reading a live process is possible; finding its picture is not yet

- The fd route was wrong because the library closes the descriptor after mapping. The memory route works and dumped the application's address space without hooking anything.
- Three selection heuristics later, the dump is still noise or zeros. The framebuffer is in there somewhere — the tool prints every candidate with a name and a score, so the next
  person should read that list instead of adding another guess.
- Recorded as an unfinished instrument rather than a result, because that is what it is.

## 2026-10-31 — the pixels are not where a shared-memory client would put them

- The listing showed one region in the right size class and it was too small for a frame, which is why earlier scans skipped it. Relaxing the threshold produced the same noise.
- The useful conclusion is not about the tool: the application very likely renders through EGL and shares its surface rather than drawing into a CPU-visible buffer. That changes
  which component is the suspect for the shear.
- Stopped rather than adding a fourth heuristic. The instrument stays because what it demonstrated — reading a live process without hooking anything — is reusable.

## 2026-10-31 — it was the EGL path all along

- Forcing the application onto Qt Quick's software renderer produced a clean, correctly shaped frame for the first time: blue bar, black strip, white content. No stripes.
- That exonerates the compositor, the renderer, our backend and the placement work in one measurement, and puts the fault where the evidence kept pointing: a GL-backed surface
  being composited wrongly.
- The frame is not the finished UI — it is mostly empty white — so this establishes where the fault lives rather than delivering the finished picture.

## 2026-10-31 — the software path was never going to work

- The blank white area was not a missing effect: the vendor's own texture factory fails on every image when the window is software rendered. It is a GL-only component, and no amount of
  provisioning will change that.
- So the only route left is the EGL one, which means the shear has to be understood inside the vendor's surface-sharing code rather than worked around.
- Worth noting the shape of this: two days of the wrong suspect, then one experiment (software backend) that both localised the fault and ruled out the alternative route. The cheap
  substitution was the decisive one.

## 2026-10-31 — the map, at the end of the display investigation

- The sharing code is a Weston extension plus a Qt binding, not the platform library I had assumed. That saves the next attempt from being aimed at the wrong file.
- The list of things exonerated is now long and each item was measured: compositor, renderer, backend, placement, capture, application geometry, application buffer. What is left is a
  GL path that this image cannot render on one side and cannot test on the other.
- Written down plainly for whoever continues: two real options, neither quick, and neither of them another screenshot.

## 2026-10-31 — the option does not exist

- Three of my GL attempts were invalid for boring reasons: a config missing ivi-module, a config file written in a previous boot when /tmp is fresh, and a log I read only partially. Each
  produced a confident "GL does not work" that was not yet earned.
- With a complete config the answer is one line: the vendor headless backend does not accept --use-gl. It cannot render through GL at all, which closes that route by measurement.
- Left with one route, and a note to self about config files in a tmpfs.

## 2026-10-31 — the buffer is shared through Mesa, and the numbers finally line up

- The pixels live in a 5.8 MB mesa-shared segment, not in any Wayland shm pool. The three small weston-shared segments are the vendor's state, not the picture.
- With the application's window 1926 wide and the compositor assuming 1920, the disagreement is 24 bytes per row. That is a mundane explanation and the first one in days that does not
  require anything exotic.
- I tried to confirm it by measuring the shear slope and could not: the frames are noise after the drift. The arithmetic is written down as arithmetic, not as proof.

## 2026-10-31 — the fifth empty run, and the pattern is the point

- Full argument list, swapped only the variant, protocol logging on. No buffer, no surface, two live processes. Compared against the two configurations that have ever worked, the
  difference is not the arguments — it is who starts the program.
- So the argument question cannot be answered by hand at all: it needs the launcher and a DLT log reader. That is the real next step, and it is bigger than a shell script.
- Five empty runs in a row, each one an invocation fault rather than a system fault. Writing that down as the finding, because otherwise the next person burns another five.

## 2026-10-31 — the log was there the whole time, and it says I have been looking at the wrong screen

- Twenty thousand lines of the vendor's own logging, generated by the chain on every run, unread because I assumed the launcher's discarding of stdout meant the log was lost.
- It says the screens are 1920x720, that launcher-managed surfaces are 1920x720, and that the application sits on screen nine — while every capture I have taken reads output zero.
- Two days of "the composite is sheared" may be a picture of the wrong output. The next run decides it.

## 2026-10-31 — my own instrument is now the suspect

- Output selection works, and the answer is that output nine is black while output zero holds a dim splash — and that the application exists for about a second before exiting.
- The earlier note that the chain renders 1920x720 surfaces was wrong: those were the vendor's notification surface. The application's window is 1926x753 here too.
- More importantly, the application used to survive minutes in the chain and now survives a second. That changed after the wrapper and the ten-output backend went in, so the next thing to
  test is whether my own instrumentation is what is killing it.

## 2026-10-31 — the wrapper was the problem, and the control proved it

- Restoring the vendor binary brought the application back to a survival time measured in minutes. The wrapper I added to inject a surface id was killing it, and only a deliberate control
  run could show that.
- Capturing across outputs showed the screenshooter answers for output zero and times out for the rest, so some of yesterday's black frames were capture failures rather than black screens.
- The next step is the one combination never tried: vendor binary, application alive, surface placed on output zero, capture output zero.

## 2026-10-31 — the stripes were the corpse of the splash

- The sheared frame after killing the splash is the splash's own logo, drawn diagonally. The thing I destroyed is the thing I was photographing.
- That explains the pixman assertion, the clean software-rendered frame, the width-independence, and every black or striped capture taken after a splash kill. One defect, seen from four
  directions across two days.
- The practical rule is immediate: never kill the splash to clear the screen. Killing it is what drew the stripes I spent two days explaining.

## 2026-10-31 — the application finally appears, and it tells us where to look

- Hiding the splash instead of killing it, and placing the application's own surface, produced a frame with the application in it for the first time: its bar, its window, and one of its
  strings.
- The string is sharp and the background image is not. That single contrast moves the fault from the compositor to the texture upload path — the vendor component that already failed
  outright when we forced software rendering.
- So the end of this stretch is not a picture but a coordinate: one function, one pitch value, and a stripe pattern that follows from it arithmetically.

## 2026-10-31 — the loader will preload into anything, and the uploads are honest

- The environment problem that blocked instrumenting the launcher's children for days has a one-line answer: /etc/ld.so.preload. Every process reads it, including the one I could not reach.
- With it installed, the GL trace shows correctly sized uploads and no row-length override at all — so the texture upload geometry is not the fault, and that hypothesis is retired.
- What is left is inside the vendor's own conversion code, which needs a different instrument than GL calls.

## 2026-10-31 — the images are compressed, and the GL stack probably cannot decompress them

- The vendor ships its art as ASTC blocks and uploads them with glCompressedTexImage2D. A driver without ASTC does not error visibly; it fills the texture with nothing and sampling it produces
  patterns that look exactly like the stripes I have been chasing.
- That also fits the software-rendering result: there the uncompressed factory failed outright, here the compressed one fails quietly.
- One extension string check decides it. After two days of geometry theories, the answer may simply be a format the software GL never advertised.

## 2026-10-31 — the answer was a format only the real GPU had

- ASTC support lives in the Intel drivers and nowhere else. Our software GL never advertised it, so the vendor's art could not be decoded, and the stripes were the sampled remains of textures
  that were never filled.
- That is an emulation limit rather than a defect in their software, and it explains every image-related observation in this log, including the messages I read in the first hours and moved past.
- The way forward is to convert the assets offline and let the vendor's own uncompressed path load them. No vendor code touched, and the same capture pipeline proves it.

## 2026-10-31 — the neat explanation failed its own test

- Removing the splash entirely showed the stripes were the application's own background, not the ghost of the logo. Denying ASTC changed nothing. The explanation I had just written up was wrong,
  and a two-by-two test said so in one run.
- What is left is a short, honest list: the stripes are in the application's images, not its text, and not in the splash, the asset format, the capture path or the compositor.
- The next instrument should print the upload format and sampler state, not the dimensions. That is a fact about which argument I have been logging, and it took this correction to see it.

## 2026-10-31 — every upload parameter checked, and all of them are correct

- Alignment toggles properly, no row-length override exists, formats are ordinary, and the surfaces are uploaded at exactly the width the compositor reports. The upload path is clean end to end.
- So the fault is on the draw side, which needs a different and much larger instrument. That is where this line of work honestly stops for now.
- The list of exonerated components now covers both the asset formats and every upload parameter. What remains is one unbuilt tracer and a stripe pattern, and saying so plainly is more useful than another theory.

## 2026-10-31 — not the art either

- The working recipe's own asset tree produces the same stripes, so the theme was never the difference and another tidy answer is gone.
- The frame does leave one clue worth keeping: crisp horizontal lines survive inside the striped field, so whatever is wrong happens inside the sampling of a single drawn quad.
- Closed the display investigation here for now. The state is written down rather than a theory, and the next instrument is named.

## 2026-10-31 — no difference, and no proof the change was applied

- Forcing llvmpipe produced the same stripes. That would exclude the driver, except that nothing confirms the override reached Mesa, so the run supports a weaker claim than it looks.
- Written as "no difference observed" rather than "driver excluded", because those are different statements and only one of them is earned here.
- The verification for this is trivial and I did not do it first. That is the same mistake as the invalid GL runs, arriving from a different direction.

## 2026-10-31 — the check that made the last run mean something

- Ten queries, each answered llvmpipe. The override worked, the earlier run was valid, and the rasteriser is now excluded rather than merely unproven.
- One build and one run turned an uninterpretable result into a firm exclusion, which is exactly the ratio this work rewards.
- What is left is the draw call and its texture coordinates, and a constraint from the frame: horizontal lines stay crisp inside the stripes.

## 2026-10-31 — the silence is the finding

- The stderr tap recovered 4,682 bytes and every one of them belonged to a different process. The application itself says nothing on stderr, and Mesa reports no GL error while drawing the
  stripes.
- That fits what has been suspected for days: the operations succeed, and the result is wrong anyway. There is nothing to catch because nothing fails.
- The instrument also proved itself in the same run by catching another process's output, which is the difference between a real null result and a broken tap.

## 2026-10-31 — a number at last

- Three pixels per row, on every row pair sampled, with a method built to survive a noisy field.
- That is twelve bytes of drift per row and over two thousand pixels across the image, which is far too much to be the width mismatch I spent yesterday calculating. The arithmetic that felt
  convincing is retired by a measurement that took ten minutes.
- The first quantitative constraint of the investigation, and it points at the texture coordinates rather than at any buffer's stride.

## 2026-10-31 — checking whether the tool already exists

- Before building the largest instrument of this investigation, checked whether Mesa already contains it. Gallium has a trace module driven by environment variables, and this project already has
  a way to answer getenv inside a process the launcher starts.
- Delegated the capture and the parser. The test is now arithmetic rather than visual: do consecutive rows differ by three texels in the coordinates the vendor supplies?

## 2026-10-31 — loaded, present, and never asked

- The interposer was in the process four times over and the driver contains the option name, but nothing queried it. One plausible reason is that Mesa reads its options through a different lookup
  function than the one I replaced.
- Recorded as a cause not yet established rather than as tracing being unavailable, because that distinction decides whether the next attempt needs a hand-written tracer at all.

## 2026-10-31 — the free instrument was not installed

- Both lookups interposed, both verified exported, neither was called. The driver has the option's name and nothing that implements it. The trace module simply is not in this build.
- So the draw trace has to be written by hand, and writing it means solving the same problem that defeated the libwayland interposition: the vendor reaches GL through a function table, not through
  exported symbols.
- Recorded as the next instrument rather than begun at the end of a long day, with the target unchanged: three texels per row.

## 2026-10-31 — the hard part has a known shape

- The draw cannot be interposed by symbol because it is reached through a function table. The way round that is to interpose the table's loader, which this project has not tried and which is the
  same obstacle that stopped the libwayland attempt.
- Delegated with a falsification condition attached, and with permission to report that the technique cannot work rather than deliver something that cannot.

## 2026-10-31 — the loader works, and the function has a name

- Three lookups, and one of them is the batched draw. The technique is viable and the target is exact. A tracer built around the obvious function name would have recorded nothing at all.
- Told the subagent mid-task, which is cheaper than reading its report tomorrow and discovering the target was wrong.
- Second time in two turns that one small probe saved a large instrument from being aimed at the wrong thing.

## 2026-10-31 — draws at last, and the layout of the quad

- Eight indexed draws and six array draws, with interleaved position and texture coordinates at a stride of sixteen bytes. The geometry path is finally visible.
- The first attempt recorded zero draws and only the wrap marker made that interpretable; without it I would have concluded the application does not draw at all.
- The coordinates themselves live in a buffer object, which is one more interposition away and is the smallest instrument left in this chain.

## 2026-10-31 — the first look at what the application actually tells GL

- Decoded vertex data: positions in pixels, texture coordinates in texels, a consistent 1.636 texels per pixel. Not normalised coordinates at all.
- It is the first measurement of the interaction rather than of a component's innocence, and it opened two candidates rather than closing one.
- Honest limit recorded: this buffer holds icons, not the full-screen background. The question that started this is still unanswered.

## 2026-10-31 — the first data that looks wrong

- Full-screen quads in normalised device coordinates, carrying texture coordinates that belong to other corners. The position and the texture data disagree.
- It might be explained by a shader computing coordinates from an attribute this trace did not decode, so it is recorded as an inconsistency rather than a cause. But it is the first piece of evidence in this whole investigation that is itself anomalous rather than merely inconclusive.

## 2026-10-31 — the repository still stands up

- Eleven hundred tests and three hundred thousand subtests pass after days of instrument work. The guest was modified heavily; the repository was not, and that separation held.
- Worth checking occasionally, because the tempting alternative was to keep editing things in place.

## 2026-10-31 — the shader explains the conventions and leaves the data as the suspect

- Both attributes are vec4 and the shader takes texCoords.xy, which matches the two-component bindings in the trace. The clip-space positions are explained too.
- What is left is the buffer: its corners pair positions with other corners' coordinates. If that is the buffer this shader draws, the quad is transposed rather than offset.
- First time the evidence points at the vendor's own data rather than at our instruments.

## 2026-10-31 — the tool works and the answer is still no

- Rewriting the shader changed the picture, which proves the instrument. Swapping the texture axes did not fix the stripes, which refutes the tidy version of the transposition theory.
- Two days ago the question was whether anything at all could be changed from outside. Now a vendor shader can be rewritten in memory in one run and the result measured.
- The next hypotheses cost one run each instead of one evening each.

## 2026-10-31 — one sign, and the stripes are gone

- Negating the u coordinate removed the artefact completely. A clean window, no stripes, for the first time in this investigation.
- The other rewrite merely rearranged it, so the difference between the two is the finding: the sampler is being handed a coordinate that walks the texture the wrong way.
- The corrected frame is mostly empty, which means the mapping is not a pure mirror; a short sweep will find the rest.

## 2026-10-31 — the stripes are in the picture being sampled

- Normalising the coordinates moved the striped band from the full width to a third of it, in proportion. The artefact follows the mapping, which means the mapping is not corrupting a clean image.
- What is being sampled is already striped. That points one layer further back, at the offscreen surface the application renders before it uploads it — which this log already measured as a 1926 by 753
  BGRA upload.
- The next instrument reads that texture's pixels directly, and it decides whether any of the quad work could ever have fixed this.

## 2026-10-31 — the texture is clean, and my last inference was wrong

- Dumped the application's own 1926 by 753 upload. It is a blue bar and a black body. No stripes. The image was never the problem.
- That refutes what I wrote one entry ago, and the correction is in the record rather than quietly dropped.
- What is left fits every measurement now: a clean texture, a mapping proportional in effect, and a sampler that wraps. The likely mechanism is a texture matrix the vendor sets and this stack does not honour.

## 2026-10-31 — no matrix, and a rule that is being broken

- The texture matrix does not exist. What does exist is a 1926-wide texture used with coordinates outside 0..1, in an OpenGL ES 2.0 stack where wrapping a non-power-of-two texture is undefined
  behaviour rather than an error. That fits silence, stripes, and a picture that changes with the mapping.
- The next test forces clamp-to-edge on non-power-of-two textures. If the stripes clear, the vendor was relying on something the vehicle's GPU tolerated and the emulation does not.

## 2026-10-31 — the blocker list, written down

- Five things stand between here and a fully working VM, and only one of them is the fault being chased today.
- The hardest is not a bug at all: this VM can only render with pixman, so anything the vendor's driver tolerated and pixman does not has to be designed around rather than fixed.

## 2026-10-31 — a plan ordered by what each step costs to learn

- Five blockers, three of them cheap tests that can each delete a whole category. One of those, the DRM device, could turn the structural blocker into a solvable one.
- The plan says what not to re-derive as clearly as what to do, because most of this week's cost was re-derivation.
- Only one blocker is throughput, and that one is four independent adaptors, which is what the workers are for.

## 2026-10-31 — two shaders, one trivial, and one more hypothesis gone

- The fragment shader samples with the varying directly. There is no normalisation in the pipeline at all, which is now certain rather than inferred.
- Dividing by the texture size did not help, so the pixel-space theory does not explain the background. The sampler-state test is still the one that has not been run.
- Astra's caution about the earlier u negation was right: that frame was clean because it was empty.

## 2026-10-31 — a week of guessing ended by one stack trace

- With no debugger in the image, every client crash so far had been inferred from a single kernel line. The signal-handler shim turned that into a named function and a named call.
- AppNavi dies asking for the valet-mode state and calling toBool on nothing. That is a missing reply, not a fault in the application, and it was predicted from the service landscape argument rather
  than discovered by staring at the crash.
- The instrument took an hour to write. The answer had been sitting behind the missing tool all week.

## 2026-11-02 — the dev mode was a path check

- Three instructions decide whether the head unit thinks it is a production build: read a member, compare with one, return it. The only thing that writes that member compares the executable's own path.
- Run the engineering binary from /tmp/app/bin and the full menu appears, including the switch that disables update encryption. That is a surprising amount of authority for a choice of directory.
- Static only so far, and recorded as such. The runtime confirmation is one experiment away.

## 2026-11-02 — the dev mode is documented, and the first fix attempt was properly refuted

- Wrote up dev mode completely: it is a path check, the launcher has a developer override, and every route in — boot hook, one-byte patch, stock gesture, USB, modified firmware, Ethernet — now has a
  measured status rather than a guess.
- Tried to clear the striped rendering first so the screenshots would be worth looking at. Forced clamp-to-edge, verified the shim reached GL, and the stripes stayed. A refutation that can be trusted
  because the instrument was proven to fire.
- The screenshot included is the engineering app running from the dev path with the stripes still on it. It documents the entry, not the menu, and it is labelled that way.

## 2026-11-04 — the dev-mode claim was half wrong, and the correction is the valuable part

- The launcher hook is real, but on this build the binary writes the SOP field unconditionally. Relaunching it from /tmp changes a log line and nothing else.
- Found the actual switch: a file at /update/disableEncryptionUpdate, created by a test app on a named MICOM event. That is a state transition you can observe, unlike a path comparison.
- Recorded the mistake rather than editing it out. The pattern that produced it is the same one this log has been warning about for days.

## 2026-11-04 — the flag is gated by build mode, and the paper's precondition is present

- The encryption-disable flag is a file, created by a test application on a named MICOM event, and the updater says in plain text that mass-production and penetration builds ignore it.
- Nothing yet ties it to signature verification, so the researcher's instinct was right: encryption and signing are separate walls here.
- The updater is also a fully static binary with mbedtls inside, which is precisely the condition the 2024 Gen5W_L paper exploits. That is worth knowing before spending more nights hunting for new bugs elsewhere.

## 2026-11-04 — every way of fetching the texture, and none of them matter

- Collapsing the sample by a factor of a thousand left the stripes exactly as they were. Six sampling tests, six refutations, one of them with the instrument proven to fire.
- That moves the question off the sampler entirely: the pattern is either in the data being sampled or introduced after it. The clean texture dump says it is not simply the data.
- So the next step is bookkeeping rather than theory: dump every large upload and find which one is striped.

## 2026-11-04 — it was us all along

- The vendor recipe renders the same application cleanly, hours later, on the same machine. The stripes came from our own ten-output backend, introduced when we moved off the vendor backend to explore the IVI screen
  question.
- Every sampling test in the last stretch was therefore doomed before it ran. That is worth admitting plainly: six careful experiments, all aimed at a component that was never being exercised.
- The engineering-mode screenshot needs the chain run against the vendor backend with one output. That combination has never been tried, and it is one run away.

## 2026-11-04 — the right idea, the wrong recipe

- The chain does not survive on the vendor backend: the compositor exits while the home screen keeps running, so engineering mode never starts and the capture is an empty frame.
- The comparison that identified the stripes is unaffected. This is a recipe problem, and the next step is to read the compositor's own log rather than guess at the cause.

## 2026-11-04 — the clean frame exists, and another project found the same things we did

- The reference capture is banked: clean vendor-backend frame, no stripes.
- A second project on the same platform documents the engineering-mode gesture and PINs, and independently quotes the same MASS_PRODUCT string we pulled out of our binary. Two methods, one answer.
- That also means the stock unit does have a UI route into engineering mode, which we had only inferred. The PIN being an unsalted hash is already in our register.

## 2026-11-04 — peripherals: the keyboard is the useful one, the serial port is switched off

- The kernel carries a full HID stack as modules, which is exactly what a scripted keyboard-style device needs. The only input udev rule is for the
  touch panel, and nothing filters keyboards.
- The USB serial path is explicitly commented out in the vendor's own rules, so that route is closed by design rather than by accident.
- Mass storage is still the more serious surface: insertion alone reaches a D-Bus-activated indexer and an old GStreamer ASF demuxer.
- In the projection HID could not be demonstrated yet because udev does not run and the module stack would not load by hand. Recorded as a limit of the
  harness, not as a property of the vehicle.

## 2026-11-04 — reading the log paid three times over

- The shim was being inherited by helper children that have no pixman, and killing them. The user-interface client was /bin/true, which exits and takes the compositor with it. And two helper binaries are
  missing from our clone, one because we deleted it ourselves.
- Three faults, each found by reading rather than guessing, and none of them the fatal one. Weston still exits with no complaint it is willing to print.
- Next is to measure its exit status instead of inferring, and to remember that the chain kills the compositor itself after its dwell.

## 2026-11-04 — force update only opens one of three gates

- The menu is real, but the string says exactly what it does: pass the version compare. Signature verification is untouched, and production builds disable the facility anyway.
- So the answer is no: there is no forced-update vector that does not first require a privileged write to replace the trust anchor.
- The rollback angle is the interesting leftover — force update would accept an older package that is still correctly signed.

## 2026-11-04 — the compositor was never dead, and the engineering mode is alive

- `pidof weston` cannot match a process called weston-headless. Several conclusions about the compositor exiting were built on that, and all of them are withdrawn.
- With the check corrected, engineering mode launches from the developer path under a real launcher, and its own log shows it counting PIN entries. That is the entry vector exercising itself for the
  first time here.
- The frame is still black, but black is not striped, and that difference confirms which of the two faults is which.

## 2026-11-04 — the VM can be touched now

- The vendor ships its own input module, and the chain simply was not loading it. With it loaded, an injected click is accepted, delivered to the seat and reported complete.
- It arrives with pid=NO_VIEW, which is the black screen described from the pointer's side: the click is fine, there is nothing underneath it.
- That matters because the stock entry vector is touch-driven. A working click path plus a visible view is all it needs — no USB keyboard, so the udev gap stops mattering.

## 2026-11-04 — the vectors were always there, behind an integer

- The engineering application ships Force Update, Encryption Update and Scheduled Update Test. Production units get a different list, and one comparison decides which.
- The deciding value is written with a single immediate that a one-byte change flips. That is the whole difference between a technician's menu and a development one.
- The patch was injected but the application had not appeared by the time I checked, so the effect is unobserved. Static finding, runtime unconfirmed, and written down that way.

## 2026-11-04 — the interface renders, and the thing that starts applications trusts /tmp

- Placement, not drawing, was the missing step: the surface existed at 1926x753 and simply was not on screen. With it placed, the vendor backend produced a clean frame of the real interface, and a clean EV page, neither with a single stripe.
- The application manager verifies each binary against a key path in world-writable /tmp, then starts the binary with the verification returning 1. It was stopped by a registration timeout instead. That is the first root-access candidate here that needs no memory corruption and no removable media.
- Requesting the engineering application at appId 301 eight times across two minutes produced no log line at all, so the earlier success is state-dependent and its trigger is still unknown.

## 2026-11-04 — the entry vector runs, as root, and tells us what it is waiting for

- appId 301 launched the engineering binary from /tmp/app/bin, the manager logged the request and the path, and the process ran as uid 0. The window drew its "Engineering Mode" title bar and took an injected click at 960x400.
- The application's own log names the reason the body is black: version, Wi-PID, trace date, MICOM part info, user mode and VR version all return empty. We have not simulated those services yet. The list is now bounded.
- Its PIN gate reads a wrong-password counter and reports no limit file, so the lockout is file-backed.
- The launch is flaky: one run succeeded on the first request, three others produced nothing.

## 2026-11-04 — the console was always the way in

- The serial console is a root login gated by a runtime parameter read from /sys, not by a fuse or a build decision. Its only usable account is root, with one SHA-512 hash shipping identically on every unit from this image.
- Sixty plausible defaults failed, which is not an answer. A fixed salt and an identical hash across the fleet is the finding, not the guess count.
- The WiFi is complete hardware - driver, firmware, CLM blob, NVRAM with a MAC address - switched off by a blacklist, a GPIO and a MICOM gate, with the enable tooling shipped.
- CAN has a core and no controller. USB ethernet has drivers and no address path, and no dropbear binary at all.

## 2026-11-04 — it ran as root

- A binary we compiled, signed with a key we generated, and accompanied by a public key we wrote to /tmp was launched by the application manager on the first request and reported its own uid as 0.
- The verifier finds its .sign section by name, hashes the file with those bytes zeroed, and RSA-verifies a PEM key from /tmp. The authentic key is pinned in the binary and copied to /tmp once, after which the copy is trusted and the resource is never consulted again.
- The manager also believes the caller about where the binary lives. Both halves of V-048 are now demonstrated rather than inferred, and the correction about the sense of the return value is recorded.

## 2026-11-04 - the console is live, and two ghosts were in the room

- A live console now exists: type into the guest, get output back. Verified with the prompt and a typed echo.
- Building it exposed that the boot depends on a debug-socket patch for the SD card; without it the kernel waits for a root device forever. And six abandoned QEMU processes were starving the emulator, which is why a forty-second boot looked like a hang.

## 2026-11-04 - the console gate was open the whole time

- The parameter that decides whether a root login exists on the serial line reads 0 on this build, with the module loaded and the device present. It is on by default and switched off only at runtime.
- The agetty line requires a password; an autologin line sits in the file, commented out.
- /tmp/shells looked like a writable privilege path and is not: nothing reads it. Written down so it is not chased again.

## 2026-11-04 - the prompt, in bytes

- Running the vendor's own agetty script on ttyS2 produced OpenEmbedded 1.0 (none) ttyS2 and a login prompt on the far side of the port. Captured raw.
- It is a login and not a shell: the autologin line is commented out. The prompt existing by default is the point, and it is now shown rather than argued.

## 2026-11-04 - the check was never reached

- A payload with no signature section, run with the key deleted, was executed as root by the application manager. App id 10, an ordinary vendor app, was enough; our own path was the binary.
- So V-048 had the narrower half of the problem. The manager trusts the caller about which file to run, and does not verify it, which no amount of key pinning would fix.
- What remains is the ability to send one message on the session bus. Nothing else.

## 2026-11-04 - the last precondition was the default

- The session bus ships the stock policy that allows everything to be sent and anyone to own anything, with no vendor rule for the launcher. So nothing restricts who may ask it to run a binary.
- That closes the chain as a local escalation: any code execution on the unit, then one message, then root. Not remote, and not a shell out of nothing.

## 2026-11-04 - correcting myself: the bus only talks to root

- Non-root cannot connect to the session bus: EXTERNAL authentication accepts only the daemon's own uid, and the daemon is root. Measured with nobody: connection refused, no proof file.
- So what I said last turn was wrong. This is not an escalation from any user; it is a persistence primitive for code that already has root, and a way out of the label such code would be confined to.
- Worth writing down as a correction rather than quietly changing the claim.

## 2026-11-04 - how the radio would come on, and what is not listening

- The WiFi procedure is now written from the image's own machinery: two modprobes, the regulator pin at GPIO 466 that supplicantmanager drives, the /tmp/no_unece trigger its path unit watches, then supplicant and dhcp. None of it run on hardware, and none of it possible in QEMU.
- Scanning for network services found none. No adbd, no ssh server, no telnetd, no hostapd, no dnsmasq, no TCP socket units. Only mdnsd and AppSDS, and those only once the radio is up.
- That bounds every remote claim in this project, so it is written down rather than assumed.

## 2026-11-04 - the outside opinion was right about the PIN

- Two models were asked which weaknesses are reachable on an unmodified unit. Both said USB; they disagreed on which USB path. Neither offered exploit code, which is not what was wanted.
- One of them contradicted a value this repository had quoted from a sibling platform. Checked against the binary's own two SHA-256 constants: it does not match either. The dealer code does. Every document now carries the correction, and the plaintext stays out of the public tree.
- The same opinion established that the IpConfigShell screen is dead QML, its button only present in the QML variant that production does not load. That hope is closed, which is worth more than another week of looking for it.
- The tap gesture on About may not exist on this build at all. It has always been inference from elsewhere; that has not changed.

## 2026-11-04 - the wrong kernel was the whole problem

- USB never worked because we were booting the research kernel, which does not export what the vendor modules need. The image carries the vendor's own kernel. Booting it enumerated a USB stick and the vendor scsi_id read its serial.
- The module load order was my mistake too: one module first, then the core, then the host controller.
- That sets a bound on the USB property-injection vector: the emulator will not carry control characters in a SCSI serial, so that half needs real hardware with a programmable bridge. Written down so it is not chased again.
- The kernel's own warning also gave up the build string, which is now recorded.

## 2026-11-04 - udev stands up on its own

- Starting the vendor's udevd by hand works, and a plugged USB stick goes through the shipped rules to the shipped scsi_id, producing ID_BUS, ID_SERIAL and ID_SERIAL_SHORT. The real chain, not a synthetic one.
- Two traps, both mine: the control file must be a socket made by udevd, not a directory I create first; and the gps driver warning loop buries the console output.
- The USB property-injection vector still needs hardware for the crafted serial. Everything downstream of it is now testable here.

## 2026-11-04 - the machine comes up

- Booting the vendor kernel with systemd as init brings the authentic rootfs up to Basic System with udev running and login prompts reached. That is the first time this has been true.
- It also means the sysemd question that blocked every USB idea is finally askable in the projection rather than by argument.
- Two corrections from the media probe: the stick must be built without metadata_csum for a 4.1 kernel, and the indexer does have an ASF plugin - I had looked for the wrong filename.
- The indexer runs as root but will not scan without the session bus and media manager, so the parser is reachable but not yet exercised.

## 2026-11-04 - the thing at the end of that chain is a shell with no password

- The unit the USB property-injection chain would start is debug-shell.service: no dependencies, an existence check on /dev/tty9, and ExecStart=/bin/sh. It is not enabled, which is the only reason it never runs.
- Its neighbours require authentication. This one does not.
- That makes "remove it" better advice than "leave it disabled", since a SYSTEMD_WANTS property names units directly rather than going through the enable links.
- The partitioning work is delegated to a worker; it is mechanical iteration, not judgement.

## 2026-11-04 - the right answer to the wrong question

- The data adaptor work succeeded: the app's queries all answered, the pending-error count went to zero, and the page body stayed black anyway.
- The screenshots that appeared to show success were the home screen's EV page, not the engineering window. Checking which surface is which cost one run and saved a wrong conclusion.
- So the blank body is a paint fault, not a data fault, and the next thing to read is the app's own qmlLog lines rather than building more adaptors.

## 2026-11-04 - the layout is fine, so the fault is lower down

- The app's own qmlLog proves the QML loads, lays out at 1920x720 and runs its transitions. It is not a data problem and not a layout problem.
- A click now reports no client under the pointer, which is a sharper symptom than no view: whatever is on screen is not receiving at that coordinate.
- The paint question is delegated with a specific plan, because enumerating surfaces and reading one wayland log is mechanical work rather than judgement.

## 2026-11-04 - the confinement is decided by a filesystem probe

- The system decides whether it is subject to UNECE by asking whether the data partition is LUKS, and if that answer is no it switches its mandatory access control to permissive. Measured 0 in the projection.
- A corrupt or replaced header therefore produces less confinement rather than a refusal to start, which is the wrong way for that decision to fail.
- The same flag also enables the wireless daemon, so one derived value governs both confinement and radio.
- Whether real units take the permissive branch is unknown and recorded as unknown. The mechanism is what is confirmed.

## 2026-11-04 - the click arrives

- A synthetic click reaches the running application and the application's own Qt log records it as touch_down and touch_up with its own pid, then takes action. That is the interactive VM, demonstrated.
- The earlier failures were placement, not input: an unplaced surface makes the compositor report no view or no client, which looks exactly like a broken input path.
- Recorded with the raw log, because this is the claim most worth being able to check.

## 2026-11-04 - the vehicle's own boot runs

- A partitioned image with the real layout lets the vendor init do its recovery and hand to systemd itself, reaching multi-user with every filesystem mounted. That is the difference between booting the machine and booting its own sequence.
- Eight partition sizes are measured from the vehicle's own fsck logs, and the active/inactive slot map is now a named fact rather than an inference.
- One vendor driver oopses on non-vendor hardware and deadlocks the init until it is neutralised. Worth remembering that the fix was one line and the failure looked like a hang.
- The root token had to name the active partition, because a partition table overwrites the superblock at a fixed offset. Recorded rather than quietly patched.

## 2026-11-04 - one value stands between multi-user and the UI

- The vendor init refuses to start the display server until a MICOM parameter says the SPI handshake succeeded, which never happens under emulation. Supplying it on the command line was accepted, but nothing in the log shows the gate opening.
- Two explanations fit equally and neither was tested, so both are written down. The next move is to instrument the display server rather than guess again.
- That makes this one value the last barrier to the vendor interface actually running.

## 2026-11-04 - the gate is understood, and the UI never needed it

- The parameter is writable, but the driver puts it back to 0 during probe, and the init polls it before any userspace can write. So it can only be opened between the kernel and the init.
- That wrapper exists now and is labelled as a stand-in for hardware, not part of the shipped system.
- Installing it means moving eight gigabytes through an image for a fidelity improvement, and the interface already runs in the projection. Recorded rather than done, because saying so is more useful than a heroic injection.

## 2026-11-04 - the encryption key was in the script

- Asking whether the previous finding applied to real units led to the encryption routine itself: it formats the data and log partitions with a four-digit literal that ships in the same image.
- So a dump of the storage opens both, and the thing it protects is application data and the vehicle logs that accumulate within minutes of boot. The cipher mode is a legacy one.
- Recorded what is not known too - whether units reach this path, and whether another keying path exists. Neither was found, which is not the same as not existing.

## 2026-11-04 - the key was checked, not assumed

- Ran the shipped cipher and passphrase: the container it makes opens with the literal and refuses a wrong one. The refusal is what makes it evidence rather than a guess.
- The vendor's own encryption script also ran end to end in the projection, formatting the partition and creating a filesystem inside it before the run ended.
- What remains unknown is unchanged: whether real units go through this path.

## 2026-11-04 - five findings, one mistake

- Swept for the pattern instead of waiting to trip over it, and found the account database itself living in /tmp, rebuilt each boot, with the console policy decided by which text file gets copied there.
- Its practical weight is small today because everything here runs as root. What makes it worth fixing is that it is the fifth instance of the same shape, and any future lesser-privileged write turns it into account takeover.
- Wrote the framing document, because the pattern is the argument the vendor can act on: none of the five needs signed code touched, four are a single file or parameter, and all of them fail in the unsafe direction.

## 2026-11-04 - the display server starts, and its config is a symlink into tmp

- Standing in for the MICOM handshake worked: the vendor init took its OK branch and started the real compositor for the first time here. It cannot run without a display device the projection does not have, so boot stalls short of multi-user.
- Checking what backend it wanted found the sixth instance of the same shape: the compositor's configuration is a symlink into tmp, and it names the shared objects a root process loads.
- Two limits recorded rather than implied: nothing restarts the compositor automatically, so a changed config waits for the next start, and no non-root writer to that directory has been shown on this build.

## 2026-11-04 - writing down the three substitutions

- The fidelity work is delegated, and the reason it is fiddly is itself a finding: the compositor's config is one step removed from the file weston reads, through a symlink into tmp.
- Recorded the three substitutions that remain between this projection and a vehicle - a software backend, a simulated handshake, and one neutralised driver - together, so the boundary is stated once and plainly rather than scattered across entries.

## 2026-11-04 - checking the assumption under everything else

- Every one of these findings rested on the directory being writable, which nobody had measured. It is: 1777 on tmpfs.
- That does not make them live, and the entries now say so more precisely - the anchors are reachable by any code execution, but the only code execution here is root already.
- Also noted that this projection does not enforce the MAC layer at all, so nothing about enforcement should be inferred from these runs.

## 2026-11-04 - maybe the barrier is capabilities, and maybe the anchors are the way around it

- The policy only lets one label hold capabilities, and nothing labels the applications. If that holds, an app is root without being able to ignore file permissions, and the only things it can still write are the world-writable files that hold every trust anchor in this document.
- That would turn six curiosities into one coherent route back to full root. It is written as a hypothesis, with the two commands that would settle it on a real unit, because this projection cannot answer it.
- Said plainly what is missing: no policy loaded here, and the stock path stalls before a compositor exists.

## 2026-11-04 - the elegant explanation did not survive contact

- Half of it held: the applications do carry the floor label rather than the privileged one. Half of it did not: setting the restriction at runtime left a new unlabelled process with full capabilities and the ability to write a root-owned file.
- So the two findings stay latent. The measurement that would decide it on a real unit is named, and the refutation is written down so the next reader does not spend a week on the tidy version.

## 2026-11-04 - testing the refutation twice, and finding a better question

- The first refutation had a hole in it, so it was redone with the image's own labelling tool and a real exec-time transition. The labels took effect and the capabilities stayed full anyway.
- So the tidy theory is dead in two configurations. What replaces it is a question worth more: if the restriction does not strip capabilities even when applied properly, what is the MAC layer actually enforcing here?
- Recorded what could change the answer - LSM boot parameters and a populated rule table, neither of which is present - instead of asserting the stronger claim.

## 2026-11-04 - the containment is a label scheme with nothing behind it

- A process carrying the floor label read and wrote a file labelled otherwise, with no denial and no audit. That label is the wildcard, so processes carrying it are outside the rule system entirely.
- Every application carries it. And the image assigns labels to directories, files and one binary without ever loading a single access rule, which means anything not at the wildcard would simply be denied - so wildcard everywhere is the only configuration that works, and it is the same as no MAC.
- That is the missing piece under the last two findings, and it is measured rather than inferred.

## 2026-11-04 - the correction that matters more than the claim

- I wrote that the handshake stand-in worked and that the vendor init had started its own display server. The log I quoted from contained the line proving otherwise: the file the wrapper writes did not exist yet when it ran.
- So the guard was false, the block was skipped, and the branch taken was the one that starts nothing. My sentence was wrong and the evidence was in the same file.
- The weston activity in that log is now recorded as unexplained rather than as proof. A worker found this; I should have.

## 2026-11-04 - two corrections, and neither one is the answer

- Fixed the wrapper to mount sysfs before writing, and its error went away. But the decision messages never appear, because they go through a device that is not reliably there yet, and the one line I had used as evidence appears in both the broken and the fixed run.
- So the correction I made is not established either. What is established is that one value has never been read at the moment it matters, and that is now written down as the state rather than guessed at.
- Two attempts, two plausible stories, one unmeasured number. That is the honest score.

## 2026-11-04 - writing the page I would want to find

- The session got long enough that the changelog stopped being a good entry point, so I wrote one page: what works with a pointer to the proof, what is blocked, the three substitutions, the register with statuses, and the corrections.
- The corrections are in it deliberately. Someone finding only the first of three entries about the SPI gate would be actively misled.
- I stopped working that one value. Three entries and one unmeasured number is enough; the recipe is written down and a worker has the parallel task.

## 2026-11-04 - the diagnostic was written to the wrong file

- The message that would have told me which branch ran has been going to a file called kmsg in the working directory, because the redirect is missing its leading slash. The success paths do it correctly.
- So two of my readings were inferences from a line the code cannot print. The defect is worth reporting on its own account: a technician whose display server fails gets nothing in the log to explain it.
- The measurement still has to happen, and now I know it must avoid that channel too.

## 2026-11-04 - resolved, with the instrument where it can be read

- Put the probe inside a script the init calls after the decision and before the branch, writing to the serial port instead of the kernel log the vendor's own failure path writes wrongly.
- Shut by default: no OK file, NOK present, parameter zero. With the corrected wrapper: OK present, NOK gone, parameter one. So the first claim was wrong, the correction was right, and the stand-in does work.
- Two things stay untidy and are written that way: something invokes the compositor even with the gate shut, and with the gate open the boot now stalls on the compositor's own display requirement - which is the worker's job.

## 2026-11-04 - the account file does what it looks like it does

- Appended one line to the account file, which points into tmpfs, and the system immediately resolved the new name to uid zero, both by id and by getent. The shadow entry appends the same way.
- So the finding is a working account entry rather than a corrupted file, and its status changed accordingly. What remains missing is not the mechanism but a non-root writer, since everything here is already root.
- Updated the state page, which still described the gate as unmeasured after it had been settled.

## 2026-11-04 - the dark window was waiting to be shown

- The trace is only twelve writes, all teardown: the application never sends a frame because something else is supposed to tell it to appear. That something is the app manager, which our chain does not run.
- So the black body was never a rendering fault. It is a missing message, and the registers show every attempt going to a name nothing owns.
- Two fixes, one cheap: send the show call ourselves to the app's own connection, or run the real manager.

## 2026-11-04 - the cheap fix kills the app

- Captured what the application registers, resolved its live connection by asking the bus which connection belongs to which process, and sent the show call to exactly that.
- One path replies never, another accepts the call and then the connection is gone. So the cheap route is closed, and it closes in a way that corroborates a much older entry about that call crashing its peer.
- Which leaves the real manager as the only honest route, and that is now stated rather than worked around.

## 2026-11-04 - the manager speaks, and says what it is waiting for

- Started the real application manager, which our chain had never run. It works, logs its registrations, and talks to the micom interface - every answer comes back invalid.
- The window's body still does not paint, but the frame is now the title bar only rather than pure black, and the manager's own log names the reason: it never gets past the point of showing the app because the replies it needs are missing.
- That is the first failure on this thread with a specific cause instead of an observation, and it points at the same stand-in work as everything else here.

## 2026-11-05 - the vehicle's own path renders, and the password holds

- With the handshake stand-in opening the gate, the vendor init launches its own display server and the machine reaches multi-user with the compositor alive and a frame captured. The blocker was the vendor's own pixman assertion, which a vehicle never hits because it uses GL.
- The password attempt began with a broken tool: this host's crypt only does DES and ignored the salt, so the first negative meant nothing. Redone properly, the hash survives ten thousand pins, thirty-four thousand dates and a word list.
- Two results, one positive and one honest negative, and both only after checking the instrument first.

## 2026-11-05 - the platform boots, the product does not

- With the authentic path rendering, I checked whether the applications come up: they do not, not once. The gate is the vendor manager's service, which exits with failure and takes the whole interface chain with it.
- That is the last structural gap, and it is the tractable kind: only a bus name has to exist, and a stand-in that owns it already ships. A worker is trying exactly that.

## 2026-11-05 - the public tree had my username in it

- Audited the repository instead of assuming it was sanitised: no keys, but forty-one places carrying the real username, mostly a copied interpreter path in old plans.
- Fixed by deriving paths from the file location rather than substituting text, because the plain substitution broke the scripts when run from elsewhere - caught before committing.
- The two affected tests could not be run because the test runner is not installed here, so the change is verified structurally only. Said so rather than implying otherwise.

## 2026-11-05 - following the gate changed the answer

- Traced who turns the data encryption on: nothing does. The only caller runs it when the partition is already encrypted, which it is not, and the factory data ships as plain files.
- So the likely field state is no encryption at all, and the mac posture that keys off that same check is the permissive one. That is a different finding from the one the entry was written as.
- Kept both readings, because weak encryption and no encryption with a disabled mac layer need different fixes, and quietly replacing one with the other would lose the distinction.

## 2026-11-05 - the rules were there all along

- Claimed the policy layer had no rules. It has six hundred and thirty-six of them across twelve files, and the authentic boot loads them visibly.
- I missed them because I looked for the mechanism - writes to a kernel interface - instead of the artefact, which was a directory of data files. That is the third time this session that pattern produced a false absence.
- Withdrew the test that appeared to prove the old claim, since it ran without the rules loaded. What stays open is whether an application's floor label is subject to them at all.

## 2026-11-05 - measured instead of argued

- Put a probe on the authentic boot, after the policy loads, and asked whether the label the applications actually use is confined. It is not: the process read and wrote an object the rules were written to protect.
- So the finding's conclusion was right and its reasoning was wrong twice over. Both wrong numbers are fixed too - twenty-seven rule files, not twelve.
- The lesson keeps repeating: check the artefact, then measure the effect, and do not trust a count taken from a truncated listing.

## 2026-11-05 - making the findings usable

- The register had become something only its author could navigate, so I wrote the version a platform team can act on: nine findings ordered by cost to fix, each with its evidence, its exposure, the fix and how to verify it.
- Cheapest first, because here the cheapest fixes also remove the most: five are configuration, three need a release, and the data protection one is murky in a way the report states plainly.
- It ends with the one sentence the whole register supports, and the readme now points at it.

## 2026-11-05 - a bound on the finding I had just settled

- The policy is written per application domain, and nothing in the shipped artifact applies those labels: no labelling command for any application binary, no unit setting one, no xattrs in the shipping archive.
- So the measurement stands - a floor-labelled process read and wrote a protected object - but the conclusion narrows: either a step outside the artifact labels them, or they genuinely run unlabelled. The projection cannot tell.
- Wrote down the one command that does tell, rather than letting a bounded finding read as a settled one.

## 2026-11-05 - both branches, same answer

- Ran the probe under the enforcing branch as well as the permissive one. The floor-labelled process read and wrote the protected object in both cases, so the exemption belongs to the label, not to the switch.
- Enforcement is nevertheless real: forty access decisions were denied in the enforcing run while the probe passed. So the policy works, on subjects that are not the applications.
- That makes the advice concrete and ordered: label the applications first, then enforce, because enforcing first breaks services and confines nothing.

## 2026-11-05 - my own probe was the thing that was wrong

- I reported that a floor-labelled process could read a protected object, and called it proof that the label is exempt from the policy. The probe never checked that the relabelling had actually worked, so it may have read an unlabelled file and proved nothing.
- The audit records from the enforcing run say the opposite: every denial in that boot is that same label being refused, mostly the logging daemon. So the policy does constrain it.
- Withdrew the claim, marked the question unproven rather than measured, and wrote down the version of the probe that checks its own precondition first. That is the second time this session I believed an instrument I had not verified.

## 2026-11-05 - the contradiction was my own instrument

- One run said the data was never encrypted; a later one showed the mappers active. Both were right, and the difference was a flag I had forced in one of them.
- The init reads that flag rather than recomputing it, and the encryption script formats anything not already encrypted with the four-digit literal. So the code is reachable, and the flag decides everything.
- Named the cause in the record: forcing a variable changed the behaviour being studied. Two of my own runs disagreed because of it.

## 2026-11-05 - two blockers named, and an old explanation demoted

- A worker answered every micom method the manager was asking for, with reply types taken from the shipping binaries rather than guessed. The gate is now open - zero invalid replies across a run - and the window still does not paint.
- Two compounding reasons: the trigger lives on an interface the manager never registers here, and the liveness watchdog removes the unshown app before anything could show it.
- That also demotes an older explanation: the app vanishing after our call may not be the call's fault but the watchdog reaping it. Both readings kept, one now has a log line behind it.

## 2026-11-05 - nine corrections is a pattern, so I wrote the pattern down

- Every correction this session had the same shape: a confident conclusion from a measurement that could not have supported it. That deserved its own document rather than nine scattered notes.
- Eight rules with the actual cases attached: check the instrument, search for the artefact, one variable at a time including my own, black is a conclusion, look for the emitting code, use negative controls, verify the marker, label the instrument.
- The two that would have saved the most time were checking a tool before believing its negative, and remembering which parameters I had forced myself.

## 2026-11-05 - the markers were worse than the examples

- Swept all ten path units and the init checks: seven privileged behaviours depend only on whether a file exists in a world-writable directory.
- Two stand out. One enters manufacturing test mode. The other starts the telematics remote-control service, which means a temporary-file write decides whether a remote-command consumer is running.
- Not an open port - the service talks over the vehicle bus - but a module that only exists when somebody writes a file is a module an attacker can summon.

## 2026-11-05 - half a demonstration, and the interesting half is elsewhere

- Tested one of the marker files properly. The path units fired, the service was attempted, and it failed on an unmet dependency - so the trigger works and the payload does not.
- More interesting: the marker had already been set before my probe ran, and no script in the image sets it. If the platform sets it itself, the remote path opens with no attacker at all, and the question becomes what sets it.
- Recorded the caveat next to the table rather than letting a static list read as a capability.

## 2026-11-05 - the marker had an owner, and it was the launcher

- The file that existed before any probe touched it is created by the launcher, next to the value it depends on: an ISA reading from the platform.
- So it is a platform-state decision that opens the telephony and telematics remote services, not an attacker summoning them. The real question moved to whatever can influence that value.
- The design still keys the decision on a file existing, so anything able to create the path gets the same outcome. Narrowed the claim, kept the structural point.

## 2026-11-05 - correcting the document people would act on

- The remediation report was still citing the probe I had withdrawn. Fixed that first, because an invalid measurement matters more in the document a platform team reads.
- Rewrote the first item around what is solid and what is not, and ordered the fix: verify on a unit, then label, then enforce - because enforcing first measures forty denials and confines nothing.
- Added the marker pattern as its own item with the caveats attached, so it reads as a design weakness rather than a demonstrated capability.

## 2026-11-05 - the one vector that needs nothing but a stick

- Every finding so far needs code execution already, or a console. There is one class that needs neither and was sitting unremarked: closed-source third-party kernel filesystem drivers, auto-mounted.
- Filed it as a candidate with no defect claimed and no CVE asserted, because the reason it matters is the required capability, not any bug I have shown.
- The test is finally possible: usb works under the vendor kernel, so malformed images can be mounted with the logs watched.

## 2026-11-05 - handing the fuzz job out, and fixing a stale table

- The kernel-driver finding only matters if a crafted image actually reaches a defect, so that is now a delegated investigation with a strict honesty bar: baseline first, one field class at a time, only faults inside those modules count, and a clean negative is a result.
- The state page had stopped at the fifth finding and still described one of them using a reason I had since withdrawn. Refreshed it with every entry and its real status.
- Being able to delegate this at all is the payoff of the kernel work this morning: the drivers could not be loaded before, so the most reachable vector in the register was untestable.

## 2026-11-05 - thirty documents needed a map

- Wrote an index that says what each document answers, starting with the four that matter: where things stand, what to fix, whether to trust the numbers, and how to run it.
- Grouped by the questions people actually ask rather than by folder, and link-checked it before committing, which caught three bad references.
- An index with dead links is worse than none, and this session has enough unverified instruments in its history to know better.

## 2026-11-05 - checking the register's own plumbing

- Fifty-seven entries, no duplicates, no gaps, no document citing one that does not exist. That survived a session of edits, which was worth confirming rather than assuming.
- The check found a stale heading: one entry still asserted the exact conclusion I had withdrawn, because the body was corrected and the heading - the part that appears in every summary - was not.
- Wrote down the tool's limitation too: its status column is a keyword guess, so it is a spell-checker for numbering, not a verdict on the findings.

## 2026-11-05 — the append-only log was not append-only

Added a checker that walks this file's git history and asserts every stored version is a prefix of the next, which is what "append-only" means. It found **21 violations**, all of them
between 2026-10-28 and 2026-11-02: entries were inserted mid-file rather than appended, and dates are consequently out of order in places.

None of the 21 are from this session — every entry I added today sits at the end and the checker confirms the file grew monotonically through those commits.

It also found a **future-dated entry**: `## 2026-11-07 — the harness removed the EGL hide transition it needed`, embedded at line 3688. Today is 2026-11-05, so that date is either a
typo or was written on a machine with a wrong clock. It is left exactly where it is.

I am not fixing either problem by rewriting. Editing history to make an append-only log look like it was always append-only would destroy the only property that makes it worth
keeping. The defects are recorded here instead, which is the one repair this file permits.

## 2026-11-05 - the product's own software runs, and the black windows are one bug

- Standing in for the micom bus name was enough for the whole chain: the launcher starts, and it brings up the manager and the home screen under the vendor init. A click reaches a real client.
- The home screen then never attaches a frame, for exactly the same reason the engineering app never did. Two applications, two launch paths, one missing handshake - which turns a per-app mystery into a single defect.
- Also found a wrong reply worth fixing: a property enumeration comes back as an unknown method instead of an empty dictionary.

## 2026-11-05 - three checks, one command, and three real defects found while building it

- The link checker found a one-character typo in the citation for the only evidence behind the console finding, and stale references to screenshots I had renamed. Nothing was checking either.
- It took four passes to stop it crying wolf about paths with spaces, guest-image paths, prose filenames and other repositories' source trees. Only then did the remaining hits split cleanly into six external citations and five real gaps.
- The five gaps are recorded as gaps rather than quietly ignored, and the history check now fails on regressions against a recorded baseline instead of being permanently red.

## 2026-11-05 - a check nobody runs is decoration

- The three consistency checks were only discoverable by reading the changelog, which is the problem they exist to prevent. Put them in the readme, the index and the first line of the state page.
- Verified the suite works from any directory, because one that only works from the repository root will be run from somewhere else and then distrusted.
- Two workers continue on the HMI follow-ups and the filesystem fuzzing, both on their own clones.

## 2026-11-05 - the stick did not break the drivers

- Swept the closed-source filesystem drivers with twenty crafted images across nine mutation classes. No fault in either module, and the drivers were demonstrably parsing because clean images mounted.
- Recorded as a weaker negative with its limits spelled out: single-field edits, read-only mounts, no deep traversal, and the kind of bug this method misses is exactly the kind that still mounts first.
- So the finding keeps its surface and loses its promise. Twenty images is a reason to stop calling it promising, not to call it safe.

## 2026-11-05 - paying off one of the recorded debts

- The link checker had listed five documents this repository promised and never wrote. Wrote the one that matters most now: the application-to-manager contract, with a citation on every claim.
- It records the registration call, the show interface, the liveness watchdog that reaps unshown apps, the micom methods with their reply types, and what is still missing. It also gives an older finding a competing explanation worth keeping open.
- Deleted its place in the allowlist so the checker enforces the file's existence instead of tolerating its absence. That is what the missing category is for - a visible debt that disappears when it is paid.

## 2026-11-05 - separating what was seen from why it happened

- One entry's heading claimed a call terminates an application. The disappearance is demonstrated three times over; the explanation is not, and there is now a competing one with a log line behind it.
- Changed the heading and the status to say the observation stands while the attribution is disputed, keeping both readings. Same failure shape as the stale heading found earlier, but subtler: the seeing was sound, only the reasoning was in doubt.

## 2026-11-05 - the missing handshake was in the wrong place

- I said the manager never registered the interface the app waits on. It does register what it should, on the session bus, and the interface belongs to the application - the manager is its client. My diagnosis put it in the wrong component.
- The real problem is inside the app: its main thread is running rather than waiting in its event loop, so it never renders, never answers, and gets killed. That may be an artefact of emulating a software-rendered QML app rather than a property of the vehicle.
- Which turns the remaining work from building another adaptor into giving the emulated app enough progress to run its own loop - a better problem to have.

## 2026-11-05 - the control case was sitting in our own screenshots

- Learned that the home screen's main thread spins on the authentic path instead of waiting in its event loop. Before chasing that, noticed the same binary paints fine on the research chain, from screenshots we already had.
- So emulation alone does not explain it. The difference is what the two paths load around the app - service contention, audit logging, or a slow logging pipe - and that distinction decides whether the missing frame is ours or the vehicle's.
- Handed the control case to the worker so it cannot be missed, along with the three candidates ordered by how cheap they are to test.

## 2026-11-05 - the offensive view, written down

- The register answers what is wrong and the report answers what to fix. Neither answered what someone would actually try on a unit, so I wrote that page: nine routes, ranked by what each one costs.
- Ranked honestly, it is a discouraging list for an attacker. The cheapest route has no way in, and the reliable one needs a screwdriver and a password that resisted forty-five thousand guesses.
- Which sharpens what the register really says: not that the unit is easy to enter, but that everything it trusts can be rewritten by anyone already inside. That is a persistence problem wearing an entry problem's clothes.

## 2026-11-05 - dating a summary so it stops arguing with the register

- A summary written mid-investigation still claimed the media parser was unproven because one filename was absent, when the plugin ships under a different name. A summary that contradicts the register is worse than none.
- Added a status note naming the claims that measurement has since narrowed, and corrected the plugin inline. Kept the reasoning, dated the conclusions.
- Same principle as separating what was seen from why it happened: a document can be honest about what it thought, as long as it says when.

## 2026-11-05 - the symptom was the normal state

- Before a worker published a diagnosis, I ran the control case in my own workspace: with the full policy loaded, the home screen painted a complete frame while sitting in exactly the thread state that was being blamed for it not painting.
- So the state is normal, not diagnostic. The policy loading is eliminated as the cause; what remains is contention, the logging daemon, or one of my own instruments.
- Sent the correction with the next discriminators, including launching the app by hand to see whether the launcher or the manager is what differs.

## 2026-11-05 - ready in one second, so slowness is not the story

- Measured the working path's readiness: the app answers introspection almost immediately and paints straight after. That retires the idea that software rendering is too slow for the manager's watchdog.
- With the audit and policy candidate already eliminated, three remain: plain contention, the logging daemon, or the environment the launcher gives the app - and the last one is the cheapest test and the most likely.
- A launcher environment pointing at a bus that is not there would explain every symptom at once, including a busy thread that never renders.

## 2026-11-05 - the missing frame may be a file we failed to let the vendor write

- Chased the environment hypothesis to a vendor script: the one thing that writes the session-bus environment file that six services read. Our chain starts that bus itself, so the script's own attempt either fails or points somewhere else.
- Every symptom follows from a unit starting without a usable bus: no introspection, no frame, a reaped process, and a thread that looks busy because it is retrying. The state I blamed two entries ago is what that looks like.
- Asked for the three strings to be compared and the file fixed if it is wrong. If the home screen then paints, the block was ours and the fix is one line of ordering.

## 2026-11-05 - the frame hunt produced a finding instead

- Reading the script behind the missing frame showed that eleven services take their bus address from a file in the world-writable runtime directory. Filed it.
- The previous anchors each subverted one decision. This one redirects the bus the whole application stack talks on, so it buys interception and impersonation of every component at once - and it needs no defect in any of them, just the shipped configuration.
- Same precondition as the others, so it is breadth rather than escalation. It is now the biggest row in the framing document.

## 2026-11-05 - keeping the two documents in step

- A new finding had gone into the register but not into the document a platform team schedules from. Added it in the configuration tier, next to the anchors whose fix it shares.
- It sits above the code changes because the fix is a unit-file edit while what it protects is wider than anything else in that tier: eleven services and every application at once.
- A finding that exists in only one of the two documents is either unpublishable or unfixed, which is a silly way to lose work.

## 2026-11-05 - a clean no, with the comparison done properly

- The most likely explanation for the missing frame was that our chain had pre-empted the vendor script that writes the session-bus environment file. Checked on the authentic path: the script runs, three strings match exactly, and the address resolves to a live daemon. Eliminated.
- The hypothesis stays in the checklist because it is real for the other chain, which does start its own bus. It does not weaken the finding about who may write that file - only the claim that we had made it wrong here.
- Two candidates left, and one A/B that settles a lot: launch the app by hand, bypassing the launcher.

## 2026-11-05 - the instructions described the path we no longer recommend

- The runbook was written when the research chain was the only way to see anything. Added the authentic path: two commands, what each reaches, the three instruments and why each exists.
- Included the two traps that cost real time: pre-starting the session bus, and the root device with a partition table on it.
- And listed the four explanations already eliminated for the missing frame, because a runbook saying only 'black, unknown' invites the same four investigations again.

## 2026-11-05 - my instrument failed, and the run still paid

- Cloned the worker's workspace to run the outstanding A/B rather than make it redo its setup. My probe never executed - the unit carrying it exited with failure and produced none of my markers while the clone's own instrumentation kept printing.
- Two facts came out anyway. The app's thread state differs between boots: this run had it sleeping in its event loop, the earlier one had it running, and a painting instance also looked like the latter. So that signal is noise in both directions.
- And the logging daemon is audited on every access to the log objects - 599 granted records in one boot - which is a volume problem rather than a denial one, and testable in a single boot.

## 2026-11-05 - one record per second is not starvation

- The next experiment on the list was to disable audit and see whether the home screen paints. Counted the records instead and saved the boot: six hundred in ten minutes, one per second, all from the logging daemon.
- Nearly wrote twenty-one thousand, because the audit serial number sat exactly where a record count goes. Counted lines instead of reading the number that looked like one.
- Added that as the shortest rule in the discipline document, since it is a new shape: not a broken instrument or a leap of inference, just the wrong field.

## 2026-11-05 - the app was never rendering because it never had a renderer

- Ran the by-hand launch properly and the app's own log answered: it cannot initialise EGL, because the software driver is not on its search path. Everything else in its log is downstream noise.
- The compositor gets the software GL environment from a wrapper; the applications get nothing, and inherit a search path containing only a stub. Copying the driver into place changed nothing, which showed the library path is what matters, not the file's location.
- Five hypotheses died before this one and all were correctly eliminated - the app was failing at EGL before any of them could matter. The fix is one environment variable for the launcher.

## 2026-11-05 - the checks now check themselves

- A night of editing scripts is how a file ends up with a syntax error nobody notices until it is needed. The suite now parses every tracked python file and syntax-checks every shell script as a fourth stage.
- It passed first time, which was worth confirming rather than assuming, since tonight's changes touched the suite itself and three checkers.
- Kept the stage deliberately narrow: it answers whether the files load, nothing more. A check that does too much is a check people run once.

## 2026-11-05 - the update container is now readable and writable

- Added the OTA envelope tool after auditing it for host paths and secrets, then exercising it rather than trusting it: inspect validates the shipped envelope, decrypt yields plaintext that starts with a package header, and re-encrypting reproduces the original byte for byte.
- Two traps recorded: the initialisation vector comes from the file name, so the output name matters on encrypt; and one dependency is missing on this host, which a throwaway environment fixes.
- The README says as plainly what it does not do: it signs nothing, so the signature check, the version gate and any rollback protection are exactly where they were. Reproducing a container is not the same as earning trust for its contents.

## 2026-11-05 - somebody else's claim that our image corroborates

- An external project claims a verify-then-install race in the USB update path. Every command string its mechanism depends on is present in our copy of the same build, including the separate re-read that is the whole vulnerability, and there is no boot-time rootfs integrity to catch the result.
- Filed it with that corroboration and imported their documentation only, not their tooling. The dynamic demonstration is theirs and is not reproduced here; the entry says so plainly.
- Checking it turned up a string upstream does not mention: a skip path for the post-install verification. Recorded as uninvestigated, because one grep would settle it and nobody has run it.

## 2026-11-05 - walking back a lead, and following a finding into the documents it changes

- Called a set of skip strings an uninvestigated bypass. There are four, one per component, each keyed on whether that component is present - the boring reading is the right one, and the entry now says so.
- The finding itself then had to propagate: the downgrade document's central bound only holds for the ordinary path, and the root-access ranking gained a route above the serial console that needs no key at all.
- Also let the imported upstream text keep its own internal links rather than editing someone else's document, and reworded one of my own sentences that looked like a link to a file we do not have.

## 2026-11-05 - from strings to code sites

- The finding was corroborated by the presence of command strings, which is weaker than it looks: it shows the commands exist, not that the check and the install are separate operations.
- Scanned the binary for displacements resolving exactly to each string. The check resolves to one site, the install to another, about a megabyte apart. The separation is structural, not textual.
- Recorded the method's own limit and what remains theirs rather than ours: the sequencing of the two sites and the hardware demonstration.

## 2026-11-05 - the same line, twice

- The applications cannot start a renderer because one vendor script preloads the vendor libEGL into every child, and a preload outranks any library path we set. Both the fix that did nothing and the copy that did nothing are explained by it.
- That exact line had already been identified once, for a different symptom, and the two notes were never connected. Naming causes rather than symptoms is the discipline that would have caught it.
- Handed the one-line fix to the worker with a note about which log to watch - the child's, not the parent's.

## 2026-11-05 - what the exploit asks of a gadget, and what no board can fix

- Wrote up the hardware feasibility for the update race: the device must survive a full sequential read for the check, notice the phase, and serve different bytes to the second open, holding two images.
- The board choice comes down to link speed - full-speed boards need half an hour per pass, a high-speed one about a minute - and the microcontroller cannot help with the page cache, which may mean the second read never touches the device at all.
- Named the three questions that settle it before anyone buys hardware, all of them answerable without any hardware.

## 2026-11-05 - one line left between the two environments

- Compared the working and failing GL environments field by field. They agree on the library path, the driver path and the gallium driver; the only difference is that one has a preload line and the other does not.
- Both libraries are the same Mesa build at the same size, so this was never an ABI story. The preload pins the loader, and the research chain deliberately runs without it.
- Removed it in my clone and armed a probe, which fired before the launcher had started. Untested rather than refuted, and handed to the worker whose timing is right.

## 2026-11-05 - the authentic path paints

- On the vendor kernel through the vendor init and the vendor compositor, the home screen now registers its name, answers introspection and paints a frame that is not the background. The last substitution was the software-GL driver path, one variable.
- My confident explanation was wrong again: the preload line is not the cause, the library it pins is the same Mesa build and works. What the launcher does is strip the driver path from its children.
- What remains on that path is not rendering but ownership - the manager kills the instance systemd started while a hand-started one paints.

## 2026-11-05 - the front page was underselling the result

- The readme's fidelity section still described the state before the frame painted. Corrected it to state the chain, quote the evidence, name the three substitutions in one place, and say what is still wrong.
- A front page that undersells by a milestone is still inaccurate, just in the safer direction. It gets checked against the record like any other claim.

## 2026-11-05 - the managed instance starts and never registers

- Probed the managed path properly this time: the process is running but does not own its bus name and creates no surface, while a hand-started instance registers and paints.
- So the difference is what the launcher gives its children, not the app or the libraries - the same libraries work when the app is started by hand. The launcher's log meanwhile shows it reaping other apps on timeouts, so starvation cannot be ruled out either.
- Both possibilities are one run apart and handed over: diff the two environments, and if they match, the answer is CPU.

## 2026-11-05 - two of my own instruments failed on the last gap

- Probed the managed path twice and got nothing useful both times. The first run lost its diagnostic lines to a busy console that drops small writes; the second wrote to a serial port that was never attached, because my runner tested for a flag name with two dashes while the harness emits one.
- Fixed the guard and recorded both faults, since the channel has to be verified before its silence means anything - the same lesson three other entries tonight already carry.
- Stopped rather than spending a third cycle on my own plumbing. What is measured about the managed path stands; the run that would settle it is one attempt away for the next person.

## 2026-11-05 - the environment was fine all along, and the console appeared on its own

- Got the lossless channel working and read the managed child's environment: driver path, gallium driver, Mesa library path, Qt platform and bus address are all correct, and every file it needs is present. So the launcher does not strip the driver path after all.
- What remains is sequencing and starvation - the launcher starts the whole application set at once against two emulated cores while a single hand-started instance has the machine to itself.
- The same channel captured something unplanned: the serial login prompt, on the vendor's own init, with none of our instrumentation involved. That finding had been proven by running a script by hand until now.

## 2026-11-05 - four cores are enough to register

- Ran the confirming experiment: the managed home screen owns its bus name with four emulated cores and did not with two. So the last gap is emulated CPU, not configuration - the vendor launches its whole application set at once and two cores cannot finish Qt startup before the manager's timers fire.
- That is a property of the projection, not the vehicle.
- The surface check in that run was wrong again: I read the research chain's log path while the authentic compositor writes to the kernel log, so whether the managed instance paints is untested rather than refuted - and written down that way.

## 2026-11-05 - a surface exists, and my capture looked elsewhere

- With four cores and the compositor's real log, the managed home screen is running and an IVI surface exists on the authentic compositor. That is further than it got with two cores, where it never owned its name.
- The capture failed because the screenshot tool writes into the current directory and I looked in a temporary one. Fourth instrument detail in a row on this one question, each caught by noticing silence.
- Stopped there deliberately: the goal is demonstrated, this last step is about the managed instance, and the return on my own plumbing is now lower than the value of writing it down for the next attempt.

## 2026-11-05 - two runs, two different surfaces, and the discipline to stop

- Ran the managed-path capture twice with identical settings. One placed the application's surface and captured a frame fifteen kilobytes larger than the background; the other placed the background's own surface and captured the background.
- So the result depends on which surface happens to be newest when the probe looks. The honest statement is that the managed instance has a surface and one capture differs from the background - not that it paints, because nobody has looked at the image.
- Stopped after five attempts on one question, all five failing on my instrument choosing the wrong thing. The goal is demonstrated; this is polish, and writing down how to do it properly is worth more than a sixth attempt that might again capture the background.

## 2026-11-05 - the key was not needed after all

- Asked whether the encryption key for the update container ships in the image. It does not - it is read at run time from the update partition - while the public verification key does ship, as public keys do.
- That splits the requirement in two, and the second half is the finding: installing a genuine older image needs no key at all, because it is already encrypted with the key the unit holds, and the version gate was satisfied against the different bytes that the check pass read.
- So the downgrade question this project has carried open since its first document has an answer, and it came from the gap between two reads rather than from the version selector or the signature chain.
- Also cleaned up a duplicated paragraph caused by my own edit landing silently and a fallback appending a second copy.

## 2026-11-05 - the biggest finding was not where people look for fixes

- The update race was in the register and in the ranking but not in the document a platform team schedules from. Second time tonight that a finding lived in only one of the two, and second time it was caught by looking.
- Added it with both halves kept separate, because they need different responses: arbitrary content is bounded by a key that does not ship, while a genuine older image needs nothing and sidesteps rollback protection entirely.
- Sharpened the ranking to match: the cost is a programmable stick, and for a downgrade that is the whole cost.

## 2026-11-05 - the front page still said there was no way in

- The readme's downgrade section opened by saying there was no route and that the answer depended on unresolved rollback protection. Both were true when written; the update race has made the second one moot.
- Rewrote it to lead with the route that works and to keep the other rows honest about what still fails.
- Third document tonight corrected because a later finding overtook it. The check suite watches numbering, the history invariant and links; nothing watches a front page for meaning.

## 2026-11-05 - the cache question had an answer in the binary

- The weakest point of the update race was the page cache: if the checked file stays cached, the install never touches the device and nothing swaps. The binary answers it - cache dropping exists, but only in the older updater, and this vehicle uses the newer one which never mentions it.
- So on the path the vehicle takes, the swap depends on the payload not fitting in memory. That makes the technique size-dependent rather than guaranteed, and it names the cheapest check on a rig: does the install pass generate any traffic at all.
- The flaw itself is unchanged - the two reads are separate in our own binary. What varies is how easily the second one can be made to differ.

## 2026-11-05 - the payload is bigger than the memory, which is convenient

- Measured the payloads in our own package: the system image is 879 megabytes and the interface image is 2.09 gigabytes. The first confirms the external project's number exactly.
- The second answers the cache worry: a two-gigabyte payload cannot stay resident in a head unit, so the install pass has to come back to the medium whatever the cache policy does. Choosing the big payload makes the swap deterministic rather than size-dependent.
- It also settles the board choice in one line: forty-four minutes per pass on a cheap microcontroller against a minute and a half on a high-speed gadget.

## 2026-11-05 - the verification was real and pointed elsewhere

- Said last entry that post-install verification was too short to matter. The binary shows a long-running checksum thread with a checksum file, cancellation paths and error handling - all of it for navigation.
- So the payload choice is not simply 'the biggest one': navigation is checked, the interface payload is cache-safe but may be inside the checksummed tree, and the system image is the cheap route with the cache risk.
- The question that would settle it is what the checksum file lists, not anything about hardware. Written into the entry rather than leaving the easier advice standing.

## 2026-11-05 - the checksums guard the small things

- The open question was which files the checksum lists cover. They ship for two components only, both small firmware binaries delivered as individual files: 152 entries for the micom and two for the front keypad.
- Neither large payload appears in any checksum file, so the interface payload is both too big to stay cached and not checksummed - which is the best case for the attack and the worst for the vendor.
- My first instinct on this was the same conclusion, arrived at without evidence. It only stands now because the scope was measured; three entries ago it was a guess that happened to be right.

## 2026-11-05 - the finding now fits on one sheet

- Eight entries built this finding one measurement at a time. Put all of it on a single evidence page: the binary's hash, each string check, the two reference sites with offsets, the payload sizes, the checksum contents, and the method behind the scan.
- Included what is not established - no reproduction, one open checksum scope, one attribution to upstream - because a single sheet is where overstatement would be hardest to catch later.

## 2026-11-05 - the stock path takes input

- Sent a click on the vendor boot path and it landed on a real client with a real pid, running as root. The input module was already in the vendor compositor's configuration; what was missing before was a surface under the pointer.
- That completes the VM goal on both axes it was set on: the vehicle's own boot path, and interaction with it.

## 2026-11-05 - the front page caught up with the last two hours

- The readme described the research chain's click as the interaction proof, which was true and had just been superseded by the same proof on the vendor path. Added it, with the two facts that make it useful.
- Stated the goal's completion next to the caveat in one breath, so a reader gets both the achievement and exactly what is not the vendor's.
- Fourth front-page correction tonight, same pattern: right when written, overtaken by a measurement, caught by checking rather than by writing.

## 2026-11-05 - the one part of the finding still on trust

- The update race rests on the install reading the same removable medium the check read. Looking for that in the binary turned up a staging area and mount points, so the strings support either an in-place read or a staged local copy - and a staged copy would make the race impossible here.
- Recorded it as open rather than inheriting the external claim, and named the cheap measurement that settles it: watch which path the check opens and which the install opens, during a real update.
- Seven parts of this finding are measured here and one is still on someone else's word. Saying which is which is the difference between a register and a rumour.

## 2026-11-05 - the product's own instance paints its own interface

- The managed application now paints: capturing each surface by identity rather than taking the newest showed the background's surface is created last and had been winning every attempt. The application's own surface renders the title bar, a widget label, and the vendor's KIA logo.
- So the chain from the vehicle's init through its launcher and manager to the home screen produces a real frame, on the vendor kernel, under the vendor compositor.
- Five failures had one cause: asking which surface was newest instead of which surface it was.

## 2026-11-05 - making the result rebuildable instead of remembered

- The working image depended on an injection script and staged files that lived only in ignored directories. Moved the script into the tool tree, parameterised it, and wrote a page naming where every staged file comes from.
- The honest part of that provenance table: five of the staged artefacts are host Mesa files, because the vendor image ships only a stub driver. That is the single machine-specific dependency and it is now stated rather than implied.
- Also recorded the boot flag that matters and the measurement trap that cost five attempts, so a future rebuild can identify the application's surface by measurement instead of luck.

## 2026-11-05 - testing my own reproducibility claim found a silent failure

- Ran the newly documented injection script against a base that did not have the injects. It reported every file missing and then exited successfully - a failure that announces itself and proceeds anyway, which is the worst kind.
- Two faults, both mine: the image path was composed against the wrong directory after my parameterisation, and my test base had never been through the partitioned build at all.
- Added preconditions that exit with instructions, and verified both behaviours: a bad base now fails loudly before touching anything, and re-running on an already-injected workspace changes nothing.
- A full from-scratch build is stated as outstanding rather than implied, because it writes a thirty-six gigabyte image and takes tens of minutes.

## 2026-11-05 - the instructions named a file the script did not make

- Validated the reproduction script against a workspace with none of the projection files. The writes work, the guard works, the re-run is idempotent - and the script never injected the init file that the documented boot command names.
- It also never wrote the preserved vendor script, so its own verify loop reported both missing on every run and carried on. The instructions were internally inconsistent.
- Fixed and re-verified on the empty base: zero missing, and every expected file present including the init with its execute bit. Third defect in a tool written an hour earlier, all found by running it.

## 2026-11-05 - the procedure works, after three bugs in a tool an hour old

- Rebuilt a working image from a workspace with none of the projection files, and booted it to multi-user with the launcher running and the micom stand-in active.
- It took four attempts. One bug made the script report success while doing nothing; one pointed the write step at the wrong directory; and one hardcoded a different workspace in the sync call, so it kept reporting that other workspace's state as the target's.
- The last one is the memorable kind: the tool reported another directory's idempotency as if it were this directory's success, and only a kernel panic exposed it.

## 2026-11-05 - the wrapper was not the program

- Tried to disassemble the updater's install path and found almost no code: the binary is sixteen kilobytes of code around ten megabytes of data, with two complete updater programs embedded inside it.
- That means my earlier claim - that the check and the install sit in different parts of the program - was wrong, because the two places I found them are in data, not in code. Withdrawn, with the reason.
- The scan was accurate and the conclusion was still wrong, because I never asked which section the addresses were in. One command would have said so before it was written down.

## 2026-11-05 - the same scan, one filter more, a right answer

- Extracted both embedded updaters and reran the reference scan inside the one the vehicle actually runs, keeping only sites in its code section. The check and the extraction are different instructions about a megabyte apart.
- Two things came out of doing it properly: the install command quoted all evening belongs to the other updater, and the one in use performs an extra listing pass over the same file, so the pattern is slightly wider than filed.
- The correction of an hour ago is now demonstrated rather than asserted: identical method, one extra filter, wrong claim becomes right one and a third read appears.

## 2026-11-05 - reading around the site, not just finding it

- Located the extraction sites in the updater the vehicle runs, then looked at what the code around them does: they are a copy helper for whatsnew files, not the partition install. Withdrew that identification.
- The real apply step is a pipeline that decrypts the payload and writes it to a partition device, opening the payload again - which is the check-then-use shape, now located in the right program.
- Its stream is rate-limited to eight megabytes a second by the command itself, which gives the hardware question a real number for the first time.
- Third attempt on the same question. A string maps to a site, a site maps to a function, and only the last one says what the code does.

## 2026-11-05 - the last open question, and the strings running out

- Named the components of the apply stage from the strings its code site references: the shipped decryptor, the key read at apply time, and a rate-limited write to a device.
- The one thing it still does not decide is what the source argument points at - the removable medium or a local file staged first. One message hints a file is resized, which leans towards staging and against what the external project reports.
- Recorded that as a hint rather than a measurement, and named the runtime observation that would settle it. Nothing in the strings will.

## 2026-11-05 - the summary was the vague version of a sharper sentence

- The leading finding got materially more specific tonight, and the front pages still described it in its earlier form. Updated both to name the two commands and the measured rate limit.
- The state page now states the finding in one paragraph, points at the full measurements, and says plainly that the remaining question needs a runtime observation rather than more reading.
- Fifth catch-up of the night, same trigger each time: specificity that stays in the register is specificity nobody acts on.

## 2026-11-05 - the evidence pointed the other way again

- Went looking for the mount path in the updater, expecting it to settle the last question. Found the local staging path seven times for every mention of the mount - the opposite of the direction I was looking for.
- Neither path settles where the payload is read from, so the question stays open, but the leaning is now recorded against the external report rather than for the answer I wanted.
- Third time on this question that checking produced the opposite of the expected direction, and the first time the check ran before the sentence was written.

## 2026-11-05 - the corrected claim was still standing where it mattered

- Audited the documents for the phrasing of a claim withdrawn two entries earlier and found it in the remediation report, which is the page a platform team acts from, while the register and the evidence sheet had been fixed.
- Replaced it with the measured commands and the extractor, and annotated the register's earlier list so the commands quoted there are marked as belonging to the other updater.
- The check suite cannot see a superseded sentence surviving in the most-read document. This one was found by looking for it deliberately, which is a habit rather than a script.

## 2026-11-05 - the two explanations were the same one

- For three entries I treated a staged copy and a mounted medium as competing answers. The updater's own log calls the directory a mount path, and the filesystem is one whose subdirectory can host the mounted stick, so they were always the same answer.
- That reconciles the seven references to the directory with the absence of any payload copy: there was never anything to copy.
- The lesson worth more than the finding: read how a path is used, not just that it appears. The disagreement was mine, not the firmware's.

## 2026-11-05 - a rule about believing the checks

- The last fault of the night was a verification that ran, answered zero, and was ignored while I committed anyway. That belongs in the discipline document, not just the changelog.
- Added as a tenth rule: assert the exact phrase and fail if absent, and when a check returns something unexpected, stop rather than rewording the search.
- Every rule in that document is now paid for by a specific mistake here, and the newest is about the habit the other nine depend on.

## 2026-11-05 - the gesture is finally worth trying

- Every note about engineering-mode entry carried the same caveat: the About-screen tap was inferred from a sibling platform because the interface it belongs to never rendered or took input here. Both of those stopped being true tonight.
- Delegated the navigation with one instruction above the rest: look at each frame before choosing the next click. Guessing coordinates blind is how this project has wasted runs, and it looks identical to a gesture that does nothing.
- A null result is a real result: it would turn an inherited assumption into a checked absence, which is worth more than another entry repeating the assumption.

## 2026-11-05 - there is a hidden five-tap toggle, and it is cosmetic

- Checked the static half of the gesture question. The external triage said this image has no tap counter; it has one, on the N-mode lap timer rather than on About, and it is reachable by touch alone.
- Every use of the flag it flips only changes the lap timer's own presentation. No path to anything privileged, so it is recorded as a real hidden toggle that is not a security finding.
- That is more useful than the claim it replaces, and it narrows the standing question: if the About entry is on this build at all, it is somewhere else - which is what the dynamic navigation is testing.

## 2026-11-05 - the gesture everybody described is not in this build

- Enumerated every tap counter in the shipped QML instead of guessing at a screen: three exist, all accounted for, and none is anywhere near About or a version string.
- So the stock entry vector as described on a sibling platform is absent here. That is stronger than a failed search because the tree was searched by pattern rather than sampled by hand.
- What remains possible is a handler in compiled code, which one observation settles and no amount of reading will. Redirected the worker accordingly.

## 2026-11-05 - engineering mode cannot be reached from the screen

- Checked the compiled interface after the QML enumeration: the application that owns the settings and About screens has no engineering entry point at all, only data paths used by the engineering app itself and a factory-reset notification delivered while already inside it.
- So the About tap everyone describes is not a stock entry vector on this firmware, and the ranking that called engineering mode a no-privilege route was overstating it. Corrected in place.
- Second external claim tonight that this image refutes, and the plainest answer yet to a question asked several times: no, not from the screen.

## 2026-11-05 - the right answer from the wrong binary

- Concluded there was no engineering entry point from one application. That application does not own the settings or About screens; the one that does is a different binary, and I had never checked it.
- Widened to every binary that mentions engineering mode and classified each: the app itself, manufacturing test, the manager's launch-by-request, factory-reset integration inside, and foreground detection by another app. No gesture anywhere.
- The conclusion held, the scoping sentence did not. That is the kind of error that sends the next reader to the wrong file, so it is corrected where it was written.

## 2026-11-05 - the page people start from was describing a world that ended

- The state page still said the HMI does not start, hours after it painted. Replaced with what happens, including the two details that cost five failed attempts: the core count and choosing the surface by identity rather than by recency.
- Added the finding that the About gesture does not exist on this build, and refreshed three register rows whose status had moved.
- Sixth front-page update of the night. The automated checks cannot see a document describing a stale world, which is why these get re-read.

## 2026-11-05 - resolved was one word too strong

- Called the source-path question resolved on the strength of the updater calling the directory a mount path. Following the method that has worked all night, the only mount call resolves to a helper that mounts VR and rw_data content, not the stick.
- So the evidence is naming only, and a copy into that directory is not excluded. Softened in both the register and the evidence sheet.
- Recorded because resolved is the word that ends investigation, and here it was ending it on a log message while the obvious next check disagreed. The confirmation step is the one most likely to be skipped once a satisfying answer exists.

## 2026-11-05 - the mount was delegated, which is why it was not there

- Withdrew a resolution two entries ago because the updater's only mount call mounts VR content. The reason there was no mount call for the stick is that another process mounts it: the flow asks the automount service during its prepare stage and unmounts afterwards.
- Naming and code are now consistent: the mount point the application logs is a subdirectory of the update partition, and the volume is mounted there by the daemon.
- Three attempts on one question, and the middle one - withdrawing a claim that was probably right - is what made the third possible.

## 2026-11-05 - what is actually on the version screen

- Mapped the About page itself: three items, and one clickable region that is a virtual rotary-knob emulator which logs a line and sends a knob press. The version text has no handler at all.
- Third independent confirmation of the same conclusion, and it explains what a person would see on a stock unit: nothing, however many times they tap it.
- Told the worker to stop clicking and write up the captures it obtained, since further runs would only add to the same negative.

## 2026-11-05 - reading the long entry back

- Read the leading finding end to end after ten rewrites. No contradictions: each correction sits above the sentence it replaces and the final resolution matches everything below it.
- One bullet had been overtaken: it still called the container requirement merely plausible, when the apply stage was afterwards measured invoking the decryptor. Sharpened, with the genuinely open half kept open.
- A long, much-edited entry is where a stale hedge survives unnoticed, because nothing contradicts it - it is only older than the evidence.

## 2026-11-05 - the interface paints a title bar and a logo, not a home screen

- Two independent captures from two workers show the same frame: title bar, left panel, vendor logo, and no home content at all. That is the steady state in the projection, not a timing artefact.
- Which corrects what I had been saying: the application paints, the home screen does not. It also explains why clicks had nothing to navigate to.
- The likely cause is state rather than rendering: the layout is gated on the vehicle power status, and our stand-in answers queries without driving that state machine. Supplying it is the next named step.

## 2026-11-05 - the app asks the manager, and the manager was never told

- Read the application's own API to find why the home layout never appears: it asks the application manager for power status, and has slots for power, ACC and ignition changes.
- So the chain is the vehicle bus feeding the manager, and the manager feeding the app. Our stand-in answers the app's queries but never drives the manager's state, so the manager says off and the app shows standby branding.
- The manager exposes an incoming setter for exactly this, so the candidate fix is one call. My own attempt collided with the harness again; handed it to the worker with the working one.

## 2026-11-05 - power was already on, and a D-Bus entry is accepted

- Asked the running manager two questions. It reports the vehicle as on, which refutes my power-state hypothesis for the missing home layout, and it accepts the show_engineermode call with a normal reply.
- That is the first D-Bus engineering entry seen accepted here, and it is a stock-reachable path that involves no screen gesture at all.
- Whether it starts the engineering application is unobserved: the home screen had not started when the call was made, so the test has to be repeated after it does.

## 2026-11-05 - no filter on the path that reaches the shell

- Traced the command builder that substitutes the package path into a shell string: the path arrives as an argument and goes straight into the string substitution with no validation between them.
- Counted the whole payload for comparisons against shell metacharacters. Pipe and backtick are never compared against anywhere, and the two semicolon comparisons turned out to be integer range and enum tests read in context.
- So the consumer side of the primitive is complete. What remains is the copy step that fills the staging directory, and whether it preserves a filename verbatim.

## 2026-11-05 - the path comes from the filesystem and nothing filters it

- Followed the substituted path back to what feeds it. Both extraction templates take their source from a filesystem entry's absolute path, which then goes straight into the string substitution.
- One command that looked like an attacker-controlled copy into the executable directory turned out to copy the payload's own binary, so that lead is closed rather than open.
- With no character-class test in either payload, and with FAT permitting semicolons and dollar signs in filenames, the remaining question is the staging copy, and nothing else.

## 2026-11-05 - the staging copy renames, and the filename route closes

- Chased the last link in the injection question and found the answer already in the repository: the update logs show every staged and installed artefact carrying a fixed name.
- So the copy renames, the path substituted into the shell is a constant, and a crafted filename on a stick cannot reach it. The route is closed rather than open.
- That is a severity correction recorded in place. What survives is the part that never needed injection: the version and signature decisions and the keyless downgrade.

## 2026-11-05 - the SOPVersion patch site was wrong

- Read the instructions around the byte I had chosen to patch for the development menu, and found it stores into a stack slot inside QDebug logging and a string trim. That is a local flag, not the engine's SOP state.
- So the patch was never established, and the runtime result I had recorded as an unobserved effect is better read as a wrong site.
- Recorded the corrected route: the method is invokable, so its address lives in the metacall dispatch rather than beside its name.

## 2026-11-05 - the home screen lays out

- One call to the application manager produced the real home screen: a light layout with battery and range widgets in place, where every earlier capture had been the app's powered-down face.
- That explains the black menu bar and the clicks falling through - there had been nothing to click.
- My own prediction for how it would work was wrong: the power query read one before and after the call, so the setter pushes a state change rather than changing a stored value. Recorded in place.
- What remains is placeholder data under the widgets, which is the same kind of adaptor work the rest of this has been.

## 2026-11-05 - the D-Bus engineering entry is accepted and does nothing

- Called the engineering-mode method on the manager with the home screen actually running this time. It answered cleanly and the engineering application never started, in eighty-four seconds of polling.
- The earlier attempt had been inconclusive because the app was not up yet; that caveat is now gone.
- Noted the route that should have come first: the micom manager exposes test methods for the front-panel special key, which means any client on the session bus can forge a technician's key press.
- The run's capture was the known background rather than the application, and that is stated rather than glossed, because the conclusion rests on the process check instead.

## 2026-11-05 - the special-key signal has no sender check

- Read how the manager subscribes to the front-panel special key and found it passes empty service and empty path, which means any sender and any path. So nothing authenticates who delivers a key event to it.
- Tried it in the projection with nine payloads and no engineering mode appeared. The service that normally emits was not running, so the payload semantics or a downstream gate is the remaining obstacle, not authentication.
- Recorded as a new register entry with the disassembly and the measured negative both stated plainly.

## 2026-11-05 - README brought up to date

- The README had two overlapping status tables and both had drifted, still calling navigation the open problem and input unwired. Rewrote the status section to the measured state, with both goals, the three substitutions and their reasons, and the two real open problems.
- Narrowed two claims rather than leave them flattering: a click target that was the compositor rather than the application, and an input row that said unwired when the path demonstrably works.

## 2026-11-05 - a standard for the last gap

- The home widgets still show dashes, and it occurred to me that when a value finally arrives I would have no way to say whether it was right. The repository already held the answer: 545 log files from a real vehicle, 321 value pairs from the application's own model.
- Recorded the observed pairs and the relationship between battery and range, so an injected pair can be judged rather than merely observed.
- The important detail is that zeros are the pre-data state, the same thing as a dash, so a run producing zero has demonstrated nothing.

## 2026-11-05 - the special-key payload is decoded

- Read the manager's decode of the forged key event. The engineering-mode request is two bytes, and the path runs through app id 301 with two state checks in front of it.
- That means the sweep I ran earlier already contained the correct payload and still did nothing, so the failure was delivery rather than format. A cleaner obstacle, and a different question to ask.
- Recorded the next test as one that watches whether the signal arrives at all, rather than whether the screen changes.

## 2026-11-05 - delivery works, so the gate is logical

- Ran the test as designed, with a monitor on the interface before emitting so the question would be delivery rather than outcome. The monitor saw the signal and the application did not start.
- That excludes transport by measurement instead of assumption and leaves three named preconditions from the decode to compare.
- Also wrote down that a signal emission returns no reply, because the error text looks like a failure and is not one.

## 2026-11-05 - the fix list now points at the evidence

- Noticed the register and the remediation report had no link between them: not one fix item cited a register entry, and the newest finding was missing from the fix list altogether.
- Added the engineering-mode item with its evidence, its one-function fix and a verify step, and a cross-reference table mapping all thirteen items to the entries that prove them.
- Wrote down why the ordering matters: the impact today is limited by a state gate, so the sender check should land before anyone finds that gate satisfiable.

## 2026-11-05 - the state page contradicted itself

- Found the page meant to be read first arguing with itself: one section said the home screen lays out, a later one still said the call was not demonstrated. The stale one was mine.
- Fixed it in place, keeping the API mapping and stating that my mechanism was wrong, and added where engineering mode actually stands, the standard for the remaining gap, and the missing register rows.
- Named the pattern: the checks catch broken links and numbering, not a page disagreeing with itself. Reading the page before adding to it does.

## 2026-11-05 - the one-hour list was recommending closed work

- The actionable section of the state page still told the reader to run measurements that had already been closed and to try the gesture that was refuted. That would have cost the next person an hour re-deciding settled questions.
- Replaced it with a ranked list by what each item would settle, plus a short table of things not to spend time on and why.
- Also found the stand-in binary had reappeared in the index, so untracked it again and restated the reason it does not belong in the repository.

## 2026-11-05 - a rebuild with host paths reached a pushed commit

- A concurrent worker was rebuilding and staging the stand-in binary while I was staging its deletion, so my removal was undone and the commit captured a new binary carrying six host paths rather than a deletion.
- Told the worker not to run git at all, since commits are mine and we collided tonight, and restated that the source is tracked while the compiled binary never is.
- Left the remaining exposure on the record rather than smoothing it: the blob is still at head until staging stops, and also in history from an earlier commit, which needs a rewrite the user should decide on.

## 2026-11-05 - the host paths are out of the artefact, not just the commit

- Chasing the built binary out of the repository kept losing to a worker restaging it, so I fixed the build instead: no debug info, prefix maps, a post-build pass that overwrites any leftover build root, and the hardcoded host include paths replaced with environment or pkg-config lookup.
- Verified the flags on a small test program first rather than assuming the toolchain honoured them, and measured zero host paths in a rebuild.
- Recorded the point: the artefact was the leak and the fix belongs in the build, not in a command that loses a race.

## 2026-11-05 - the interaction recipe written down in one place

- The knowledge needed to actually interact with the VM was spread across four documents, so no single one of them was enough. Wrote one recipe covering boot, the power-on call that makes the layout appear, clicking, capturing by surface, and what is not yet established.
- Kept the honest part: clicks are accepted and routed, but on the standby frame the focus target was the compositor rather than the application, and whether a click lands on a widget after the layout appears is still unmeasured.

## 2026-11-05 - the root-access ranking had engineering mode wrong

- The ranked list still sent the reader toward an app-manager launch request, which requires root already and so cannot be a route to root. Replaced that row with the front-panel key signal: a system-bus write, no gesture and no PIN to request, reaching the engineering application which the manager runs as root.
- Kept the status honest, that the signal is delivered and the handler declines on internal state, and noted that the separate method route is inert so nobody retries it.
- The point worth keeping: a ranked list is read as an instruction, and that row was pointing the wrong way.

## 2026-11-05 - a byte size was standing in for the image

- Opened a delegate's capture that had been treated as proof an injection worked. It was the application's powered-off face, so the run had never got far enough for the injection to show anything.
- That also broke a shortcut used for days: one standby frame measured eleven kilobytes larger than the size we had been quoting as standby, a spread bigger than the difference between two states we treat as distinct.
- Added a rule that a size tells you something new was captured but only the image tells you what, and noted the delegation lesson: a worker told to compare sizes will read a size mismatch as a state change.

## 2026-11-05 - the last gap is a transport, not an adaptor

- The mapping came back with a finding that changes the shape of the remaining work: the widgets read the application's own raw CAN listener, not the D-Bus interface every adaptor so far has been built against.
- Verified the premises myself: no CAN interface exists in the projection, the micom driver is built into the kernel, and every CAN device driver in the config is disabled.
- Recorded the two routes honestly, including that the shortcut needs a kernel tree this project does not have, and that the faithful route is the vendor's own micom link.

## 2026-11-05 - why can0 never appears

- Booted the authentic path and read the driver state instead of reasoning about it. The CAN stack and the micom driver are both loaded, but there is no SPI device and no platform device for the driver to bind to, so the probe that creates the network interfaces never runs.
- That puts the faithful route behind a device-level change rather than a handshake, and turns up a fidelity gap: userspace reports the SPI check as fine while the kernel has no SPI device at all.
- Named the cheaper third route: interpose on the application's CAN socket calls, the same substitution pattern as the backend, the micom service and the GL driver path.

## 2026-11-05 - the CAN shim intercepts the application's own CAN setup

- Built a shared object that stands in for the CAN transport and logs every interposed call. The application opened its CAN sockets, set the interface index and bound them, which confirms from its own syscalls what the disassembly only argued.
- Did not get a picture: I streamed a 129 kilobyte capture as base64 over a console that cannot carry it, a trap already written down. Recorded that as my mistake rather than the shim's, with the fix being to write the file to a partition and read it from the host.
- Also recorded the smaller mistake: looking for markers in the kernel log when the instrument writes to the serial console.

## 2026-11-05 - frames come off the guest losslessly now

- Two dead ends, one of them mine to have remembered: the console cannot carry a capture, and writing to a partition does not persist because the disk is a snapshot.
- The working method is a second file-backed serial device carrying base64. Raw binary corrupted there because the serial rewrites newline into carriage-return plus newline, which showed up in the image magic rather than in the length.
- The first real frames show the day theme active and no widgets, so the power-on call took effect but the layout did not settle. Recorded the two candidate explanations and the two cheap tests that separate them.

## 2026-11-05 - the frame settles at ninety seconds

- Captured the same surfaces at thirty, ninety and a hundred and fifty seconds and found the frame only stops changing at about ninety. Every reading before that, including my own, was a transitional state.
- The settled frame turned out to be more informative than the CAN work: a title bar showing a translation key as literal text and a black region, which points at a resource model that never loaded rather than at missing vehicle data.
- Added a rule after writing an elided path twice in one session, and then broke that rule inside its own text, which the link checker caught.

## 2026-11-05 - the frame I called the home screen was the camera app

- Checked where the string in the title bar actually comes from and found it in exactly one application, the camera one, in fifty-four files. The home screen's own strings are present in all of its translation files, so its translations were never missing.
- The black region is a camera preview with nothing attached, not missing theme images. Corrected the claim in place rather than quietly.
- Noted why the captures could not have told me: every surface returned the same size, so the ids identified nothing and the compositor log is what has to be read.

## 2026-11-05 - screenshooter was never capturing a surface

- Pulled the compositor log off the guest and read it. It dates every surface and shows three applications running at once, which explains why a window I analysed belonged to the camera app.
- It also shows the capture tool composites the entire output regardless of which surface was placed first, so a method used for days was never doing what its name suggested, and a rule about which surface to avoid was wrong in its premise.
- Found the compositor respawning a keyboard binary that does not exist, which burns CPU and perturbs timing measurements.

## 2026-11-05 - the controller announces nothing to a late client

- Ran our own placement tool against the running compositor and found it sees no layers and no surfaces at all, while every protocol global is present and three applications are running.
- The composited output in that run was the early background, so the applications are not on a visible layer, and every earlier capture came from surfaces that happened to be placed rather than from control we had.
- Named the likely cause as ordering: the controller notifies clients that are bound when objects are created, so binding at boot is the next single test.

## 2026-11-05 - hmi-controller, a negative and a truncated measurement

- Found which file really decides the compositor configuration: the ini everyone names is a symlink, and the resolution-specific file underneath it is the one that matters. Its module list omits a module that ships in the image, and the shell user interface it names does not exist at all.
- Added the module and booted: the application stack never started, which is a failure mode unlike the others, and my own capture truncated the module list exactly where it mattered, so the run cannot be judged.
- Reverted the clone and wrote the honest alternative into the note: if the layer path is unavailable here, document that the projection cannot present the vendor interface rather than implying the interface is broken.

## 2026-11-05 - hmi-controller kills the compositor in five seconds

- Captured the log whole as the previous entry said was needed, and it changed the conclusion: the compositor was already gone at five seconds, so the earlier reading about the launcher chain was wrong.
- Corrected my own claim that the shell user interface is missing: it exists, just in a different directory from the one the configuration names. Only the keyboard binary is genuinely absent.
- Found a permission-denied failure string compiled into the module, and the audit log is live, so the next test is to look for a denial rather than to keep experimenting.

## 2026-11-05 - both hmi-controller hypotheses are dead

- Tested the permission theory and the path theory in one run each. Neither is right: no denial appears in the audit buffer, and correcting the path to where the binary actually lives does not stop the init failure or the compositor dying.
- Which forced the obvious point I had been missing: the vehicle's own configuration loads only two modules, and the placement protocol we already have a working tool for is a different one that has worked here before.
- So the likelier explanation is stacking rather than placement, and the next test is to stop the applications that start later and see whether the home screen is underneath them. Reverted both experimental changes rather than leave them in the clone.

## 2026-11-05 - placement works and the standby face is my own sequencing bug

- Captured the same screen three times in one run: before placing the application surface, after placing it, and after killing the other applications. Placing it changed the output, so the placement mechanism works and the module investigation was unnecessary.
- The other applications came back within seconds of being killed, so clearing them is not a strategy.
- The frame is the application's powered-off face, and the likely reason is that my probe sends the power-on call at a fixed second rather than after the application owns its bus name. Recorded the corrected sequence.

## 2026-11-05 - the app keeps dying, and the console said where the log was

- Tried the corrected ordering and an explicit off-then-on edge. Neither produced the laid-out screen, but the process ids gave the reason: the application is being restarted repeatedly, with two instances alive at once and a third later, so any state event lands on an instance that is gone.
- That makes the restart the obstacle and everything else downstream of it.
- The console log contained the literal redirection telling me where the application's own stderr goes, and I had been reading the console without following it. That file is the next thing to read.

## 2026-11-05 - the restart loop was my own shim

- Read the log file the console had been naming for days. The application initialises completely and then dies on a Wayland protocol error, so the restart loop was a client crash rather than a state problem.
- Then tested the obvious suspect, my own preloaded library, and the application held one process id for the whole window with it removed and churned through several with it present. The shim was the cause.
- Revised what the shim can be used for: not process-wide, and it must not override close. Recorded the lesson, that the log was named in output I was already reading and the instrument I trusted was what broke the system under test.

## 2026-11-05 - the tool I photograph with is killing the app

- Removed the preload and the application still restarted. The difference from the stable run was exactly one thing: that run made no placement calls, and this one places the surface before every capture.
- So the placement tool races the client's surface and kills it, which explains why every placed capture showed a powered-off screen: I was photographing a freshly restarted instance and calling it the state of the system.
- Wrote down both findings against our own instruments, and the honest test that follows: capture repeatedly with nothing of ours interfering and see what is actually on screen.

## 2026-11-05 - with nothing of ours in the way the app is stable and shows a splash

- Removed every instrument and captured repeatedly. The application held one process id for a hundred and five seconds, so the instability was ours, and the screen is a logo with no chrome: the application's splash, a third distinct frame rather than the standby or the layout.
- So the application is not crashing, it is waiting. The three frames are now distinguishable by what they look like rather than by size.
- The log pulled earlier already contains the first real candidate: the application fails to commit its own layout database repeatedly, which would explain a fresh instance never restoring a home screen.

## 2026-11-05 - the layout database had no directory

- Followed the database failure from the application's log to a real gap: its store lives on the data partition under a directory that does not exist, and a database cannot create its own parent directory.
- Created the directory in the clone and marked it clearly as a change to the projection rather than the image.
- The run afterwards still restarted the application, so the gap was real and not the whole cause, and I had failed to capture the log the change was meant to affect, which is the same mistake in a new place.

## 2026-11-05 - the directory fix worked and the commits still fail

- Pulled the log as planned. The database file now exists, so the missing directory really was blocking creation, but the commit failures continue and print no error detail.
- The same tail shows the application opening kernel GPIO nodes that do not exist here, which is the same kind of gap as the missing CAN interface and also a thing we could stub with files.
- So the question now has two named candidates from the application's own logging rather than from my reading of frames.

## 2026-11-05 - the record was behind the work

- Stopped and corrected the two documents people read first, because eight turns had overturned the model they described.
- Added a warning at the top naming both of our instruments that kill the application, with the numbers from both runs, and the instruction to add one instrument at a time. Every capture taken with either active is now marked suspect, including ones already committed.
- Narrowed two README rows that were no longer true, and rebuilt the one-hour list from what is actually open plus an explicit list of things closed today so nobody revisits them.

## 2026-11-05 - the layout database is not the blocker

- Pulled the database out of the guest and inspected it. The schema exists, the layout table holds twenty-five entries, and only the two widget settings tables are empty, so the failing commits are the widget inserts and not the layout.
- That withdraws my suggestion that the missing directory might explain the splash: the layout is on disk and the screen is still splash. The second plausible cause this session to survive one check and die on the next.
- Noted the untried half of the same interface: the application listens for a power status signal and this project has only ever called the method.

## 2026-11-05 - two instances of the app run at once

- Tested emitting the signal instead of calling the method. It changed nothing measurable, and the honest reading is that the emission did not reach the application rather than that the signal is irrelevant.
- The pid columns showed something I had read past for hours: two instances of the application alive at the same time, from before anything of ours ran.
- That single fact explains both the Wayland fatal error and the database commit failures without inventing anything, which means the last two entries were diagnosing symptoms of a duplicate process.

## 2026-11-05 - the duplicate instance was the cause

- Killed down to one instance and the two error families went to zero: no Wayland fatal errors and no database commit failures, where two instances had produced both.
- That makes the last two entries symptoms of two processes competing rather than causes of anything, which is recorded rather than quietly dropped.
- Also recorded that plain kill did not remove the process: I announced the same process id killed six times while it was still running, the same class of mistake as trusting a capture without looking at it.

## 2026-11-05 - retraction: the duplicate is not the cause

- Withdrew yesterday's conclusion that the duplicate process caused the Wayland crash and the database commit failures. The zero counters it rested on came from a log file that each new instance truncates, and the tell was in the same line I quoted.
- A run with one instance and a real ninety-nine kilobyte log still contains both failures, so the duplicate is at most a contributing factor.
- Made it a rule that a count is not evidence unless the size and identity of the file it came from are recorded beside it, because zero is indistinguishable from an empty file.

## 2026-11-05 - the failure in order

- Captured the sixty seconds around the error from a log whose size and instance were verified first, and the whole failure fits in half a second.
- It shows the application surviving: it logs on for another twenty-seven seconds with a dead compositor connection, and a database commit succeeds after the failures, so neither the crash nor the commit is a wall.
- That reframes the problem as an application running without a surface rather than one that is stuck, and names the next measurement as reading which request on the dead object the server was answering.

## 2026-11-05 - the launcher strips the environment and the database has two writers

- Tried to enable protocol tracing through a service drop-in and found the launcher does not pass its environment to the application, which matches how it strips the graphics variables.
- The run was still useful because the compositor error did not occur in it: the log shows the application holding two database handles and one of them failing transactions with a statement error while the other commits.
- That makes the commit failures a defect in the application rather than in the projection, and takes them off the list of candidate causes for the missing screen.

## 2026-11-05 - the wrapper stops the app launching

- Put a wrapper in place of the application binary to get protocol tracing, and the application never started at all. Whether the launcher refuses non-binaries or checks integrity is unproven, and an integrity check would be a finding in itself.
- Destroyed the vendor binary in the clone on the way, because I assumed a filesystem tool had a rename command it does not have. Recovered from the pristine extraction and recorded the two-step rule that avoids it.
- Noted that every instrument added to this project so far has damaged the thing it was measuring, and moved the next attempt to the compositor side where the failing event is actually delivered.

## 2026-11-05 - the protocol exchange, seen from the compositor

- Turned on the compositor's own protocol trace, which required touching only our wrapper, and the failing exchange is four lines: the application binds the window manager interface, asks the controller to create a surface with its own object id, and the compositor reports an object it does not know.
- Did the cheap static check first and it weakened my own theory: there is one wayland client library in the image and we did not inject it, and the application reaches wayland through the Qt platform plugin rather than directly. The protocol definition is not shipped at all.
- Named the measurement that separates the two remaining readings, which needs no new instrument: read the running process's library map and see which wayland library it actually has.

## 2026-11-05 - the client I blamed is probably not the application

- The runtime check I named came back empty, most likely because the system's mandatory access control stops one domain reading another's memory map, so I fell back to a static check.
- That check contradicted my own attribution: neither Qt wayland plugin contains any of the ivi protocol strings, so the client in the trace cannot be the application I had been blaming for three entries.
- Kept what survives, that protocol tracing on the compositor works and found a real failure, and made the next measurement about ordering: when the interface is bound relative to the application's first log line.

## 2026-11-05 - the ordering test settles the attribution

- Compared line numbers in the compositor log against a marker taken the instant the application appeared, since that log only ever appends.
- The window-manager binds happen in the first hundred and fifty lines, and the application does not exist until line fourteen hundred and thirty, so a startup client owns them and the application is at most a recipient of the later error.
- Named the next read as four lines of context from the compositor log, where its own launch message should name the startup client directly.

## 2026-11-05 - the startup client connects at six seconds

- Used the compositor's own uptime clock to place the suspect bind in time: a client connects at about six seconds and enumerates the globals, minutes before any application exists.
- The compositor's launch lines in that window name only the failing keyboard and the splash client, so the suspect is one of those.
- Noted what that would imply if confirmed: the splash client this project wrote would be breaking the application's connection, which is a defect in the projection rather than in the vendor software, and a materially different claim.

## 2026-11-05 - the startup client is the vendor's

- Checked whose client the launch line names, statically and with no boot: it is a vendor binary shipped in the pristine image, launched by a vendor module that also carries the surface creation calls.
- That refutes the speculation from the previous entry, that our own splash client might be the defect. Written down as a possibility before the check, and killed by the check.
- Left the thread in an honest place: the application is not crashing, our instruments are not involved in this error, the database is not the cause, and the remaining difference from a vehicle is the display backend the vendor's start-up sequence is running against.

## 2026-11-05 - the headless backend is forced

- Checked which display backends the vendor ships and which DRM drivers its kernel has. It ships a DRM backend and cannot use it, because the kernel's only DRM driver is the Intel one and the drivers that would work under emulation are not built, one not even present in the configuration.
- So the least faithful backend is not a preference but the only one that runs, which confirms from the other direction that the vendor's start-up sequence is running against a display path it was not written for, and shows it cannot be fixed inside the emulator.
- Wrote down the claim the evidence supports: the projection runs the vendor's kernel, init, compositor and application, and cannot give them the display hardware they were written for. Two of the three substitutions are forced by the kernel's configuration rather than chosen.

## 2026-11-05 - every display path is closed

- Checked the last remaining option, a plain framebuffer, and the vendor kernel has the whole framebuffer subsystem compiled out, so no display device of any kind can exist under emulation.
- That turns the headless backend from the best available into the only one possible, and makes the ceiling a measured fact rather than a standing assumption.
- Wrote the sentence the project should use from now on: everything the vendor ships is running except the display hardware, and failures that depend on the display path are attributable to that absence rather than to a defect.

## 2026-11-05 - the first real defence in the image

- Went back to the security goal with a question the virtual machine work raised: why a replaced application binary refused to run. The answer is a hash and challenge-response mechanism in the launcher, tied to the micom and backed by OpenSSL, which is the first genuine anti-tamper control found in the shipped image.
- It sits beside the earlier finding that the launch path runs any caller-named path as root rather than contradicting it: the platform has the parts for verification even where the launch path does not use them.
- Hedged the finding properly. Enforcement is unproven, the observation that prompted it is equally consistent with an exec requirement, and the control is probably inert under emulation because the events it depends on never arrive.

## 2026-11-05 - a second app refuses the wrapper too

- Replaced a different application's binary with a wrapper, copying and verifying the original first as the rule requires, and it also failed to start while the untouched application kept running.
- So the behaviour is general rather than per-application, which weakens the targeted-integrity suspicion and points at an exec or format requirement instead. Recorded that it weakens rather than kills the hypothesis.
- The direct test of the hash mechanism did not run because I omitted the session bus address from that probe, and that is written down rather than quietly retried.

## 2026-11-05 - the hash answers and the comparison lives in micom

- Retested the cipher interface properly and it returned a thirty-two byte digest from the projection itself, which corrects the earlier hedge that it was probably inert without a micom.
- The launcher's own strings name every application binary beside the SHA-256 calls, so the digest fingerprints the installed application set, which is the shape of a real tamper check.
- Found no reference manifest anywhere and the comparison path runs through micom, so the control cannot be enforced in the projection and the wrapper refusal is not explained by integrity. Also noted that the hash is callable by any client on the root-only session bus, which makes it an oracle for whether tampering was noticed.

## 2026-11-05 - the integrity hash filed as an oracle

- Filed the exposure as a register entry: the application-set digest is queryable by any client on the session bus, which makes it an oracle for whether tampering changed the platform's view, and an unchanged value would tell an attacker which of their changes are invisible.
- Bounded it honestly to low severity, since the bus is root-only and no content leaks, and kept it separate from the integrity design itself, which is the right shape and cannot be tested here because the reference lives in micom firmware.
- Added it to the fix list with a verify step a hardware owner can run in a minute, and noted that an unchanged digest would itself be a finding about coverage.

## 2026-11-05 - a sweep found a third engineering route

- Replaced hypothesis-driven reading with a systematic sweep of every embedded D-Bus interface for write or execute shaped methods. Thirty-four interfaces came back and one was new.
- The settings application asks the micom, through an argument-free method, whether engineering mode may be entered. That is a third route to the same place, and enforcement sits on the micom side either way.
- It also names a concrete gap in our own work: the stand-in that answers the micom interface in the projection does not implement the engineering interface at all, so that question currently goes unanswered. Recorded both without claiming the route works.

## 2026-11-05 - the modem's factory interfaces are open to anything running as root

- Followed the sweep's most security-relevant hit: the modem daemon ships factory methods that set the subscriber identity and erase stored cell records, and its bus policy allows root while denying everyone else.
- On this unit root is the ambient privilege level of the whole application stack rather than a privileged subset, so that policy separates applications from outsiders and not from each other.
- Filed it at low fix cost with the honest bounds, and recorded the pattern it completes: three findings now rest on the same non-boundary, which strengthens the existing argument about controls placed where they do not separate anything.

## 2026-11-05 - nine bus policies re-open services to everyone

- Read the eighteen bus policy files, which is where the platform's boundary decisions actually live. The system bus is deny by default, but half the service files then add a default-context allow.
- Three of those belong to the vendor and expose state-changing or data-writing methods to any process on the bus without root, including the platform's own node and session state service.
- One file ships a developer's account name that does not exist in the password database, which dates the policy and explains the shape of it better than the misconfiguration alone. Added as a fix item with a one-command verification, and noted that the boundaries I had been hunting inside binaries were sitting in eighteen small text files I had never read.

## 2026-11-05 - one hundred and six services run as root with no hardening

- Applied the same sweep to the unit files. Of one hundred and seven services, one has a user line and it belongs to systemd itself, no unit sets no-new-privileges, and none of the vendor's own units set a single hardening directive.
- That names the cause behind a pattern this register recorded six times without explaining: a root-only bus is not a boundary between anything that matters when nearly every service is root.
- Filed it with the fix ordered by leverage, all of it configuration only, and added it to the trust-anchors argument as the reason that argument is urgent rather than tidy.

## 2026-11-05 - nine trust anchors point into the world-writable temp directory

- Swept the configuration layer for the pattern found twice before and found nine instances: the account database, the mount table, the resolver configuration, the valid shell list, the compositor configuration and three images are all symlinks into the world-writable temporary directory.
- Read the reason fairly: the root filesystem is read-only at runtime, so a generated file does need somewhere writable. The error is the destination, not the symlink, and root-only writable locations exist and are used elsewhere.
- Ranked them by cost, with the resolver first because its consumers read continuously, and wrote the single change that fixes all nine: point them at a root-only directory. Added as a fix item with its cross reference.

## 2026-11-05 - the navigation payload is world-writable

- Swept file permissions and found one hundred and twenty-eight world-writable files, two of which are the navigation binary and a startup shell script. Directory modes prevent creating files there, but the file modes permit modifying those two in place.
- Normal boot leaves that partition read-only, but the application launcher itself remounts it read-write at runtime, so the window exists. The same launcher builds a navigation verification key in the temporary directory, which matches the earlier finding where a temporary key let a signed binary run as root.
- Separated what is measured from what is not: the key may be read from the tree it verifies, and whether the check gates execution is unknown. Filed both with a fix that is two lines of image build plus shipping the key.

## 2026-11-05 - the temporary-key family is enumerated

- Asked how many verification keys the platform trusts from a writable path. Four binaries verify anything, and only one of them reads keys from the temporary directory, with exactly two keys involved, both already filed.
- That turns the family from a sample into a complete set, and means the two fixes close it. An enumerated weakness is a different thing from a sampled one, and tells a platform team when to stop looking.
- Recorded as a scope note rather than an entry, with the incidental build-host path found in the navigation updater and the small piece of evidence it gives against one open hypothesis.

## 2026-11-05 - two sweeps came back empty

- Looked for setuid binaries and for world-writable directories and found none of either outside the volatile areas.
- That narrows an existing finding rather than adding one: the world-writable navigation binary is an anomaly in two files, not a permissions model applied to a tree, so the fix is two targeted permission changes instead of a tree audit. The fix item now says so.
- Also recorded why the platform needs one specific recommendation rather than generic hardening, since every escalation in the register goes through ordinary file access or a service and none through privilege bits. Three of the last four sweeps have ended useful and smaller than feared, which is what enumeration does.

## 2026-11-05 - a static root ssh key ships in the image

- Sweeping for marker files in the temporary directory turned up one referenced by an ssh service template. Following it found a root public key shipped in the image, an ssh unit whose only gate is that marker, and root logins not disabled.
- It cannot run today because the daemon binary is absent, and that is recorded first so the severity is not overstated. What remains is a static shared credential that would become a root login the moment the package is added for field debugging.
- Filed with the four measured facts, the honest bounds, and a cheap fix: remove the key and the units, provision per-device credentials if remote access is needed, and treat the shipped key as compromised by distribution.

## 2026-11-05 - embedded private keys and a certificate authority on a writable partition

- Asked what other credential material ships and found two things. Four application binaries carry private keys, one of them alongside certificates, which makes at least one a complete client identity and all of them compromised by distribution.
- The second is the more serious: the certificate authority used for navigation updates is a group-writable file on a writable partition, so a single file write could let an attacker sign a package the unit accepts, and that payload runs as root. Recorded as the cheapest persistent root path here, with the one measurement that would settle it named.
- Deliberately did not reproduce any key material, and recorded that the consistency checker caught a forward reference I had written before the entry existed.

## 2026-11-05 - the navigation certificate is managed by the updater itself

- Answered part of the open question statically rather than with another boot. The updater's own code names that file as the TomTom root CA and copies one into place only when none is present.
- Since the image ships the file, the trusted certificate is the shipped one, which means on a fresh unit trust never bootstraps from a package being verified. That narrows the finding to the writability of the file rather than the update protocol.
- Recorded the half still unmeasured: whether the package signature specifically is checked against it, since the code path is the upgrade flow rather than an isolated verification routine.

## 2026-11-05 - a script path on a persistent writable partition

- Swept everything the binaries reference under the writable partitions and found the manufacturing test application pointing at a shell script in a directory that persists across reboots and does not ship.
- Combined with the known trigger for that application, that would be unattended root execution surviving reboot: persistence rather than escalation, and precisely what an attacker who already has root wants next.
- Recorded that the execution link itself is unproven, named the five-minute test that settles it, and gave the fix in one sentence: never execute scripts from a persistent writable partition.

## 2026-11-05 - a referenced config file that does not exist

- Closed the writable path sweep with a negative: the launcher names a configuration file on the persistent partition that a running system does not have, so there is nothing in it to tamper with and nothing to read.
- Recorded that the inference behind it was weak from the start, because the strings that looked like configuration keys are also the parameter names of the launch interface.
- Tabulated the whole family of writable path trust anchors with their state, three of five absent or already covered by a fix, so the list can be scheduled rather than feared.

## 2026-11-05 - the root-access ranking was five findings out of date

- Refreshed the ranked route table, which predated five of today's findings. Two routes moved to the top, and the cheapest is no longer the one that needs programmable hardware.
- Added the sentence the ranking needed: because nearly every service runs as root, a file write is not a high bar but the ambient condition, so the cheapest routes are persistence and pivot options for someone who already has root.
- Kept each entry's unproven parts visible in the status column, since a ranking that hides them is a ranking someone acts on wrongly. The old table told a reader the cheapest path needed hardware, which is a different risk conversation and a different fix.

## 2026-11-05 - the entry documents were quoting old numbers

- Found the readme and the state page both stale by ten register entries and eight fix items, and the readme still naming the old strongest finding.
- Rewrote both around the three entries that set the frame now: the service hardening count that explains why the others are severe, the writable certificate authority that is the cheapest path, and the shipped ssh key. Kept the two refutations beside them so nobody chases what was already disproved.
- Noted honestly that this is the third time the record lagged the work in one session, and that the checks cannot catch a document that is internally consistent but out of date.

## 2026-11-05 - the manufacturing script test came back negative

- Stopped calling the manufacturing script entry unproven and tested it: staged the payload, created the trigger marker, and started the binary as root. It ran for a full minute and never executed the script.
- So the cheapest reading of that finding is refuted, and the entry now says so. What remains is a possibility whose trigger is something else, most likely a media eject given the file name, which is where the next reader should look.
- Noted that two of the last three entries have been narrowed by measurement rather than widened by inference, and that a register becoming smaller in its claims as it grows in entries is the right direction.

## 2026-11-05 - the stand-in's backlog measured, and a correction to my own description of it

- Returned to the virtual machine goal with the gap I had named. Corrected the description first: the stand-in does implement the engineering interface, just not the one method in question, and that is now one added row in its acknowledgement table.
- Measured the backlog from the simulator's own rejection log: sixty calls across ten distinct methods during one boot, each with a caller that wanted it. That makes the remaining adaptor work a ranked list with known consumers rather than a guess.
- Recorded a limit of my own instrument immediately: it logs only rejections, so the absence of the method after the fix is consistent with success and with never being called. The next change is to log accepted calls.

## 2026-11-05 - the simulator now logs accepted calls

- The simulator reported only rejections, which made a silent log look like a working fix. Rebuilt it to log acceptances as well, and the same boot now shows three hundred and ninety-three accepted calls against fifty-seven rejected.
- The accepts are concentrated: one can polling method accounts for three hundred and thirty of them, which explains why that data path matters to the widgets and why its absence looks like missing data rather than an error.
- The engineering entry check added earlier was never called during a normal boot, so it is recorded as implemented and unreached rather than verified. Noted the loop it closes: the virtual machine needs engineering mode to test the method, and the method exists to enter engineering mode.

## 2026-11-05 - the application has two data paths and we substitute one

- Read the application's own log to settle a question answered two different ways earlier. It initialises a raw can socket and also holds a valid micom interface over the bus, and status values arrive over the bus from our stand-in.
- So the stand-in is doing real work and is not inert; what it cannot supply is frame data, which travels over the socket path that does not exist in the emulator.
- Recorded both conclusions together: the remaining adaptor work is the ten state methods in the backlog, and the values need a transport the vendor kernel's configuration makes impossible here.

## 2026-11-05 - the stand-in answers every call the stack makes

- Implemented all ten backlog methods, taking reply types from the calling binaries' own introspection and marking the reply values as assumptions. Rebuilt, injected, booted.
- The simulator now records four hundred and three accepted calls and zero rejections, and the new handlers were reached sixty-one times, so this is not a silent no-op.
- Recorded the distinction that keeps it honest: the adaptor is complete in shape, not complete in values, and the reason a value could be wrong has changed from a missing method to an assumed zero. That is the precondition for comparing against real hardware.

## 2026-11-05 - four of the assumed replies had evidence in the repository

- Checked the vehicle's own log dump for the methods whose reply values I had called unrecoverable, and found four of them: an eight byte count for the spdif version, three reply fields with a manual value of two for the lcd sensor, and a value of two for the usm setting.
- Corrected the stubs, rebuilt, booted: still zero rejections and the handlers were reached, so the corrected replies broke nothing.
- Recorded the lesson, which is the same as the configuration sweeps: I called something unrecoverable while holding five hundred and forty-five log files of it. Honest state now four replies evidence-based, one known unreferenced, one placeholder, and none of it proof of correctness.

## 2026-11-05 - a second vendor application fails the same way

- Tried to settle the top-ranked finding's open question by running the updater from a directory I controlled, so its relative certificate path would point at a file I had planted. It never got that far.
- The updater is a Qt application and dies with the same fatal display error as the home screen, an invalid object twenty rather than nineteen, which corroborates that the failure is not specific to one application but to the vendor's client stack meeting this display path.
- Recorded that the open question is now blocked by the same hardware absence that blocks the widget values: two different goals waiting on one thing, stated plainly instead of rediscovered later.

## 2026-11-05 - mapping what the display ceiling blocks

- Wrote down once what had been discovered three times at the cost of a run each: five open items are blocked by a single absence, the display path, rather than by their own difficulty.
- The leverage is now unambiguous. A kernel rebuild with the virtual gpu driver would unblock all five, and it needs a kernel tree this project does not have, which makes acquiring one the highest-leverage action available.
- Listed what is not blocked and worth doing instead: adaptor completeness measured without a display, static security work, and the record itself.

## 2026-11-05 - the kernel tree was already in the repository

- Corrected an entry from a turn ago: I said the project had no matching kernel tree. It has one, sitting in the working directory alongside earlier build outputs and logs.
- So the highest-leverage action changed from acquiring a tree to building from the one in hand, and that is now delegated with the trade-offs written down in advance rather than discovered: the vendor-only symbols fall out of the config, which costs the built-in driver that would have created the can interface.
- Named the pattern, because it is the third time this session: the reply values, the bus policies and now the kernel tree were all already in the repository while I looked only at the binaries.

## 2026-11-05 - the root console and ssh hang on one file the init script creates every boot

- Read the init script properly, having only read fragments of it before, and found the mechanism behind two earlier entries: it creates a marker file on every boot whose name reads like a hardening flag, and the code that would remove it is commented out.
- That one file switches four things: a valid login shell, the shell-bearing password database instead of the nologin one, the serial root console, and the eligibility of the ssh service. The only thing that turns it off is a single value from the micom, which measures zero here.
- Recorded it as the strongest root-access statement in the register, and kept the honest bound: the field value of that parameter is unmeasured, and the console password may not even be the binding constraint.

## 2026-11-05 - the marker grants eligibility not access

- Looked for field evidence of the micom console parameter in the vehicle logs and found none, because the init script writes to the serial port rather than to those logs.
- Then read the script that starts the console and found that the autologin line is commented out, and so is a second console on the usb gadget serial port. That made one sentence of the finding too strong, and it is corrected in place.
- What remains is a fail open design: safe behaviour depends on a single value from the micom, the marker lives where anyone can write it, and three mechanisms inherit its state. Noted that three turns running, looking for the bound has found the bound is real.
