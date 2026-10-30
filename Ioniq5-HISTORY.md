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

- Withdrew the earlier published claim that AppNavi never calls ivi_application.surface_create.
  It rested on marker counts from the client Wayland debug log, which does not emit those
  requests in this build, so their absence there proved nothing.
- Compositor-log counts for the same run show two surface creations, seven ivi surface
  references, and attach and commit calls, so AppNavi does render.
- The reproduction uses the gpio440 adaptor, the valet-status D-Bus boolean stub and the
  widget-linking helper, matching the retained milestone. The open question becomes
  visibility rather than surface creation.

## 2026-10-29 — visibility requests issued but never bound to a surface

- Compositor-log counts during the valet-stub run show sixteen set_surface_visible and sixteen
  set_visible_for_qtwayland calls, eight foreground requests and sixteen layout calls, but
  zero ivi_surface_visibility events.
- The only surface id logged as created is 30000 while the helper programmes visibility for
  3000, so the requests never bind to a surface that exists, matching the manager reporting
  drawing application 0.
- The id discrepancy is therefore the leading explanation, supported by the event count. Next
  step is to establish the environment-to-id mapping and align the two.

## 2026-10-29 — surface id fixed at 30000 regardless of the environment value

- A run with QT_WAYLAND_SET_SURFACE_ID set to 0 still produced surface id 30000, identical to
  the run with 3000, so the variable does not determine the id in this path.
- Together with the visibility marker counts this closes the diagnosis: AppNavi creates 30000
  and attaches buffers, the helper programmes visibility for 3000, and sixteen visibility
  requests yield zero visibility events.
- The fix is to address the id that exists, by rebuilding the widget-linking helper with
  parent 30000 rather than trying to make the client create 3000.

## 2026-10-29 — retargeting the helper to 30000 does not produce visibility

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
