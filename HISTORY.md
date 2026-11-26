# Public release history

This append-only file records public Gen5W VM Workbench publication snapshots.
It intentionally excludes private project history.

## 2026-11-21 - Workbench 0.3.4 public snapshot

- Published a source-only developer preview with macOS, Linux, and Windows
  launchers.
- Created a parentless public snapshot from the independently accepted 0.3.4
  source archive.
- Preserved explicit qualification limits for host setup, prepared guest
  rendering and input, physical radio behavior, installation, and restoration.

## 2026-11-21 - Workbench 0.3.5 public snapshot

- Reduced guest acquisition verification subprocess overhead while preserving
  every identity, marker, hash, log-scan and deadline gate.
- Qualified one changed zero-input macOS run through historical and fresh frame
  publication, visible Home rendering and complete owned-resource shutdown.
- Published a new parentless source snapshot; Windows/Linux first-run and every
  physical installation or restoration boundary remained unqualified.

## 2026-11-21 - Workbench 0.3.6 public snapshot

- Kept startup available when the optional Windows browser handoff fails while
  preserving strict URL validation and explicit no-browser behavior.
- Added clone-first staging, destination-capacity admission, sparse-aware
  buffered copying, separate copy/verification progress, and owned-partial
  cleanup.
- Published a new parentless source snapshot after the consolidated 19-suite
  harness and independent review passed. Real Windows/Linux and every physical
  installation, recovery, restoration, and radio boundary remained
  unqualified.

## 2026-11-21 - Workbench 0.3.7 public snapshot

- Added bounded optional timing diagnostics around the unchanged post-receipt
  identity, output-digest and two log-scan phases.
- Preserved acquisition results and native failure evidence when optional timing
  metadata is malformed, duplicated, oversized or truncated.
- Published a new parentless source snapshot after the consolidated 19-suite
  harness and independent review passed. Live 0.3.7 timing, real Windows/Linux
  rendering and every physical installation, recovery, restoration and radio
  boundary remained unqualified.

## 2026-11-22 - Workbench 0.3.8 source candidate

- Selected `max,vendor=GenuineIntel,-avx2` only for Linux and WSL2 ARM64 QEMU
  TCG hosts while preserving `max,vendor=GenuineIntel` for macOS and x86-64.
- Propagated the selected profile through the runtime command, started event,
  and status response.
- Froze a deterministic 50-file source archive after independent source review.
  Publication review and the changed full-assets Linux ARM64 live run remain
  pending; this entry is not a publication claim.

## 2026-11-22 - Workbench 0.4.0 source candidate

- Record the 0.3.9 Linux ARM64 run, which reached HMI startup and stopped at
  `reason11` / `DBUS_NO_REPLY` before producing a frame or accepting input.
  Authenticated Stop completed with the full receipt and cleaned up its VM.
- Refine the bounded log snapshot diagnostic. A reported nonzero status from
  the final-byte pipeline now yields `read_failed`. A zero count still
  yields `newline_check_failed`.
- Prepare the 50-file source archive from the accepted 0.4.0 source. Linux
  rendering and the cause of the D-Bus timeout remain unverified.

## 2026-11-22 - Workbench 0.4.1 source candidate

- A full-assets 0.4.0 Linux ARM64 run stopped at `capture_budget`. The IVI
  capture path had inherited a whole-second budget check for a standalone
  screenshot it never takes.
- Remove that check from the IVI path. Keep the standalone screenshot path
  and the strict IVI capture and verification deadlines. Retained synthetic
  tests cover the cutoff at 15,000 ms and a clock crossing between checks.
- Confirm the generated shell enables `pipefail` and cover upstream-only
  `tail` failure in a synthetic test. Live 0.4.1 rendering remains unverified.

## 2026-11-23 - Workbench 0.4.2 source candidate

- Keep `newline_check_failed` and refuse the raw trace when the bounded
  reason-11 snapshot ends in an incomplete DLT record, while deriving only a
  fixed typed summary from validated complete records before that tail.
- Reuse the DLT context and handler policy, skip a first fragment that crosses
  the acquisition boundary, and independently require the copied scan length,
  original inode, prefix, size and line bounds, and stable owner identity.
- Keep marker channels distinct and reject malformed, duplicate, lone, or
  swapped diagnostic records without replacing the structured acquisition
  failure. Missing markers mean only `not_observed_in_complete_prefix`;
  `absence_not_proven` remains true.
- Preserve raw-trace rejection, acquisition outcome, foreground call, capture,
  input, error precedence, and the strict 15/20-second deadlines. Live 0.4.2
  rendering remains unverified.

## 2026-11-23 - Workbench 0.4.3 source candidate

- Sample optional log inode and size boundaries immediately before the
  IVI foreground request and at `reason11` failure.
- Report the furthest ordered native phase from complete records inside the
  sampled boundaries. The fixed label records observed activity. Reply delivery
  and causality remain unresolved.
- Preserve the foreground request, deadline, acquisition result, and
  frame and input checks. The private source passed all 19 Workbench suites.
  Live 0.4.3 rendering and physical behavior remain unverified.

## 2026-11-23 - Workbench 0.4.4 source candidate

- Require one complete, canonical, nonce-bound producer-failure envelope and
  retain a fixed typed timeout summary only after receipt and diagnostic-range
  validation.
- Reject malformed, duplicate, truncated, oversized, noncanonical and
  context-mismatched evidence without replacing the original acquisition
  failure or converting, publishing or accepting anything on the failure path.
- Preserve both strict deadlines and the 0.4.3 foreground behavior. The shared
  private source passed all 19 Workbench suites and the native producer receipt
  suite. Live 0.4.4 rendering and physical behavior remain unverified; the
  retained Linux foreground transcript is a 0.4.3 artifact.

## 2026-11-23 - Workbench 0.4.4 public archive Linux ARM64 evidence

- Run the exact 0.4.4 public archive with SHA-256
  95607cafb96e147c330c0101eb8a056fed2cfcd0b852752ea42d776517d458c4
  from source commit ca7d6f0c72a340a50412d8ca645c3442992d7571 in a
  disposable Ubuntu 24.04 ARM64 Lima guest.
- All eight compatible assets passed their manifest and SHA-256 checks. Browser
  and API bootstrap, authentication refusal, asset admission, QEMU TCG launch,
  receipt validation and cleanup worked. Acquisition reached 78 percent and
  stopped with typed guestacquisitionerror / native_timeout; it published no
  fresh frame and admitted zero input.
- Stop returned its exact acknowledgement and the run removed all owned
  listeners, sockets and processes after 223.499 seconds. The native timeout is
  failure evidence, not a rendering qualification.

## 2026-11-23 - Workbench 0.4.5 public source snapshot

- Distinguish a complete component timeout that occurs strictly after a valid
  capture from a timeout that can invalidate acquisition. Pre-capture,
  equal-time, malformed, undated, out-of-range and unbound evidence remains
  fatal.
- Add synthetic post-capture success, equal-time failure and malformed-time
  end-to-end cases. The source's consolidated 19-suite gate and the extracted
  package's 124 tests passed, with one explicit skip.
- Publish a parentless sanitized snapshot and deterministic 50-file source
  archive from commit 7a38b3421f52880f4069c100dba34c49f914f475.
  Successful 0.4.5 live rendering, Windows native deployment, and every
  physical installation, recovery, restoration and radio behavior remain
  unqualified. SCOURGE remains 0/6.

## 2026-11-23 - Workbench 0.4.6 public source snapshot

- Run the exact 0.4.5 public archive on Linux ARM64. Version 0.4.5 was shown,
  the exact manifest was admitted, the ARM64 no-AVX2 CPU profile matched, a
  valid receipt and output hash were observed, and zero input was admitted.
  The second bounded log scan finished after 23.3 seconds, beyond the old
  20-second verification cutoff, so the run failed closed as
  `verification_deadline` with HTTP 503 and published no fresh frame.
- Verify authenticated Stop returned HTTP 200 with `completed`; the launcher
  exited, all 281 event IDs were contiguous, and no listener, socket or
  process group remained.
- Extend only the verification boundary to 30 seconds. Preserve the capture
  deadline, mandatory identity checks, output and log hashes, visibility,
  frame publication, zero-input and cleanup gates.
- Publish a parentless sanitized snapshot and deterministic 50-file source
  archive from source commit 0eb4bf8d80183eab23bf3f9dd9cd2d6081e0cdd6.
  Successful 0.4.6 Linux rendering, Windows native deployment and every
  physical installation, recovery, restoration and radio behavior remain
  separate qualification boundaries. SCOURGE remains 0/6.

## 2026-11-23 - Workbench 0.4.6 Linux ARM64 controlled failure

- Exercise the 0.4.6 runtime archive with SHA-256
  `5ff6dc0a1b70c2559ace7c72aa18140511c5769cedd989ece2204a914e7aa8f1` from
  source `0eb4bf8d80183eab23bf3f9dd9cd2d6081e0cdd6` on Linux ARM64. Two
  executions stopped at reason-11/DBUS_NO_REPLY with stable owner, PID
  and process start time. One further guest execution was invalidated by a
  qualification-observer fixed-port mismatch and is not a release control.
- The controlled dedicated-port execution cleared reason-11, IVI and
  native/model submission, admitted the exact manifest and QEMU CPU profile,
  then failed closed at 78 percent with typed probe_receipt. It published no
  fresh frame and admitted zero input.
- Authenticated Stop returned the exact acknowledgement, the failure frame
  returned HTTP 503, all 281 event IDs were contiguous, and no owned listener,
  socket or process group remained. Successful Linux rendering, Windows
  native deployment, physical installation, recovery, restoration and radio
  behavior remain unqualified. SCOURGE remains 0/6.
- After qualification, a documentation-only checkpoint advanced source to
  `79b214db40cb1b389c22965175ab07ccfb1fbe10` and produced the downloadable
  204,845-byte archive with SHA-256
  `2114ed1d4722fa3f649def46e88d6ffa28960eb2024bf06283aedd473f044362`.
  Every runtime source path is byte-identical to the tested archive; the five
  changed files are documentation. The final archive passed 124 extracted
  tests with one expected native-PowerShell skip.

## 2026-11-23 - Workbench 0.4.7 successful Linux ARM64 qualification

- Extend only the foreground capture-observation boundary from 15 to 30 seconds
  in both the shell transaction and guest probe while preserving the 30-second
  verification boundary and every mandatory identity, receipt, hash,
  visibility, frame, input and cleanup gate.
- Exercise the exact runtime archive with SHA-256
  `9d47be5627c9927449e511c75af0ed0380d99788d25a12029d46d8438beee1e9`
  from source `1e5fbccdb028e802b482457ebdb1968e75f0b5ae` in a fresh
  Ubuntu 24.04.5 ARM64 Lima guest using QEMU 8.2.2 TCG.
- A staging-only first attempt copied a prior run's mutated runtime rootfs and
  failed closed at 10 percent with `asseterror`. The controlled attempt used
  the pristine pinned assets, admitted the exact eight-file manifest, reached
  100 percent, served two fresh 1920x720 compositor frames, admitted zero input,
  completed authenticated Stop with an exact 166/166-byte body, exited the
  launcher with status 0, retained 289 contiguous events, and left no owned
  listener, socket or process group. It completed in 297.104 seconds.
- Publish a parentless sanitized snapshot and deterministic 205,175-byte
  archive with SHA-256
  `2fa4373c807c68943356bec86fe98b444ca6bc26c6cbf381938f4a63108d35cc`
  from source commit cb7fab9adf444b307065844dfca3e1c997838fde. Every runtime source blob is
  byte-identical to the qualification commit; the extracted final package
  passes 124 tests with one expected native-PowerShell skip.
- Pointer delivery, human desktop interaction, native Windows execution and
  every physical installation, recovery, restoration and radio boundary remain
  unqualified. No manifest or CRC pin changed and full SCOURGE remains 0/6.

## 2026-11-23 - Workbench 0.4.8 public snapshot

- Bound terminal failure visibility to 30 seconds for a headless or
  disconnected service while preserving the failed state for an authenticated
  browser Stop. Add a fast regression test and pass all 19 Workbench suites.
- Freeze a deterministic 50-file archive from source commit `940c280b` at
  205,723 bytes with SHA-256
  `0f786f312012eccf6a46950816e7755dfdeed9149cc06bb12473328d5ec2b558`.
  The exact extracted package passed 125 tests with one expected native-PowerShell
  skip.
- Run the visible macOS launcher from the exact archive with the verified local
  assets. It reached 100 percent, kept guest networking disabled, returned the
  unauthenticated 403, served advancing fresh 1920x720 frames, completed a
  same-origin click, returned the exact 166-byte Stop receipt and exited 0 after
  206.43 seconds with no owned listener or QEMU process.
- Publish a parentless public snapshot. Native Windows execution, human desktop
  interaction and every physical installation, recovery, restoration and radio
  behavior remain unqualified. SCOURGE remains 0/6.

## 2026-11-24 - Workbench 0.4.9 public snapshot

- Add a WSL1 software-emulation fallback while preserving WSL2 preference and
  the exact snapshot-backed, no-network guest contract.
- Correct the WSL1 foreground-window contract, compress the slow-profile
  evidence transfer under bounded decompression, and retain every target,
  receipt, identity, visibility, frame, input and cleanup gate.
- Complete a Windows 11 ARM64 WSL1 run at 100 percent with disabled guest
  networking, fresh 1920x720 compositor frames, acknowledged same-origin
  pointer and Escape dispatch, an exact 166-byte Stop, launcher exit 0 and no
  residual QEMU, listener or socket. The pointer moved into the Confirm
  control, but no application transition was observed.
- Freeze and extract-test the deterministic 50-file source archive from source
  `d0a0c2fcad3352ca763137b271e74c30bec7b0d0`: 206,122 bytes, SHA-256
  `b0e0305532d94f9272a1798ad6d362a325fb6835dca6e93f510169d70624146e`,
  127 tests with 126 passing and one expected native-PowerShell skip.
- Publish a new parentless source snapshot. Human desktop interaction,
  visibly effective input, and all physical installation, recovery,
  restoration and radio behavior remain unqualified. No manifest or CRC pin
  changed and SCOURGE remains 0/6.

## 2026-11-26 - Workbench 0.5.0 asset-free preview

- Add a separate host-fixture preview with original synthetic 1920x720 frames,
  fixed browser chrome, collapsible panels, progress and event visibility, and
  guarded same-origin pointer and keyboard input.
- Serve synthetic frames with an explicit fixture source and keep preview mode
  isolated from OEM assets, QEMU, guest networking, firmware and physical
  evidence.
- Record automated real-browser coverage and retain every VM and hardware
  boundary.

## 2026-11-26 - Workbench 0.5.1 visible preview launchers

- Add discoverable preview launchers for macOS, Linux and native Windows.
- Reject incompatible preview flags before mutation and cover Python discovery,
  browser conflicts, Stop propagation, malformed ports and spaces in paths.

## 2026-11-26 - Workbench 0.5.2 public snapshot

- Preserve clipped D-Bus telemetry as typed failure evidence and restore the
  strict 1,024-byte success acknowledgement limit.
- Select the longer foreground window only on Linux ARM64; classify GNU and
  BusyBox timeout statuses, preserve trailing line feeds, and normalize only
  the profile-selected generated-script timeout.
- Harden Windows Python discovery without opening or probing Microsoft Store
  aliases, and include the integration matrix in the deterministic archive.
- Package exactly 55 source paths in a deterministic 281,255-byte archive with
  SHA-256 `08e4916e3ca0e77cfd51be366dc27b75e6f3596b6b93d4627d4cb26daa6ace61`
  and checksum-file SHA-256
  `2f88ef7ef950a07e0720a63cf79f7fbf93f075700982f7d72b95994935271c2a`.
- Pass 194 extracted tests with two expected skips on macOS and Ubuntu 24.04
  ARM64. The Windows 11 X1 launcher fixture passes 163 assertions and its
  contract.
- The exact Linux replay clears the former D-Bus timeout but stops at
  `native_entry`, publishing no frame and admitting no input. Authenticated Stop
  succeeds and owned resources are removed.
- Publish a parentless sanitized snapshot. The private full-research history
  checker remains at 27 findings against its stale baseline of 22; no published
  record is rewritten to conceal the discrepancy. Physical installation,
  recovery, restoration and full SCOURGE remain unqualified.
