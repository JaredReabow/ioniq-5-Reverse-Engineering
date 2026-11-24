# Changelog

## 0.4.9 - 2026-11-24

- Add an explicit WSL1 software-emulation fallback for Windows hosts where
  nested virtualization is unavailable. WSL2 remains preferred, and both paths
  retain the snapshot-backed, no-network QEMU TCG guest contract.
- Match the compiled foreground probe to the WSL1 slow-profile's inclusive
  59,999 ms window, gzip-compress only its raw source/output evidence transfer,
  enforce bounded decompression, and retain the original uncompressed hashes.
- Pass the consolidated 19-suite Workbench gate, the 15 compositor-probe tests,
  the 40 focused bootstrap/platform tests and 68 Windows launcher assertions.
- Complete a Windows 11 ARM64 WSL1 run at 100 percent with guest networking
  disabled. It served fresh 1920x720 compositor frames, acknowledged
  same-origin pointer and Escape dispatch, returned an exact 166-byte
  authenticated Stop, exited 0 after 880.63 seconds and left no owned QEMU,
  listener or socket.
- Package exactly 50 source files in the deterministic 206,122-byte archive
  from source `d0a0c2f` with SHA-256
  `b0e0305532d94f9272a1798ad6d362a325fb6835dca6e93f510169d70624146e`.
  The extracted archive passed 127 tests with 126 passing and one expected
  native-PowerShell skip; its launcher plan also completed.

The pointer moved into the Confirm control, but no application transition was
observed. Visibly effective input, human desktop interaction and every physical
installation, recovery, restoration and radio behavior remain separate
boundaries. SCOURGE is at 0/6.

## 0.4.8 - 2026-11-23

- Keep terminal service failures visible for browser Stop while bounding a
  headless or disconnected failure to 30 seconds before service and
  owned-listener cleanup.
- Add a fast regression test for the bounded failure path, bump the Workbench
  version to 0.4.8, and pass the consolidated 19-suite Workbench gate.
- Package exactly 50 source files in the deterministic 205,723-byte archive
  from source `940c280b` with SHA-256
  `0f786f312012eccf6a46950816e7755dfdeed9149cc06bb12473328d5ec2b558`.
- Extract the exact archive and pass 125 tests with 124 passing and one expected
  native-PowerShell skip.
- Run the visible macOS launcher from the exact archive with the verified local
  assets: 100 percent readiness, disabled guest networking, unauthenticated
  403, fresh 1920x720 compositor frames at sequences 2 and 3, completed
  same-origin click, changed frame 4, exact 166-byte Stop, 100 contiguous event
  IDs and launcher exit 0 after 206.43 seconds with no owned listener or QEMU
  process.

Native Windows execution, human desktop interaction and physical installation,
recovery, restoration and radio behavior remain separate boundaries. SCOURGE is
at 0/6.

## 0.4.7 - 2026-11-23

- Extend only the bounded foreground capture-observation window from 15 to 30
  seconds in both the shell transaction and the guest Weston probe. Keep every
  receipt, identity, hash, visibility, frame, input, verification and cleanup
  gate unchanged.
- Run the exact 0.4.7 archive with SHA-256
  `9d47be5627c9927449e511c75af0ed0380d99788d25a12029d46d8438beee1e9`
  in a fresh Ubuntu 24.04.5 ARM64 Lima VM with QEMU 8.2.2 TCG. A staging-only
  attempt using a prior mutated runtime rootfs failed closed at 10 percent with
  `asseterror`; the pristine pinned assets were then used for the controlled
  run.
- Reach 100 percent, return the unauthenticated HTTP 403 refusal and serve two
  fresh 1920x720 guest-compositor frames at sequences 2 and 3. Admit zero input,
  return an authenticated 166/166-byte Stop response, exit the launcher with 0,
  retain 289 contiguous events and leave no owned listener, socket or process
  group. The controlled run completed in 297.104 seconds.
- Package exactly 50 source files in the deterministic 205,175-byte archive
  with SHA-256
  `2fa4373c807c68943356bec86fe98b444ca6bc26c6cbf381938f4a63108d35cc`.
  The extracted archive passes 124 tests with 123 passing and one expected
  native-PowerShell skip. Every runtime source blob is byte-identical to the
  qualification commit; only public documentation changed afterward.

Pointer delivery, human desktop interaction, native Windows execution and all
physical installation, recovery, restoration and radio behavior remain
separate qualification boundaries. SCOURGE is at 0/6.

## 0.4.6 - 2026-11-23

- Record the exact 0.4.5 Linux ARM64 run. Asset admission and startup passed,
  the receipt and output checks completed, and the second bounded log scan
  reached 23.3 seconds before the old 20-second verification deadline refused
  the acquisition. The browser then authenticated Stop and all owned runtime
  resources were removed.
- Extend only the bounded verification window from 20 to 30 seconds so the
  unchanged mandatory checks can complete under ARM64 TCG emulation. Keep the
  15-second capture boundary, target identity, receipt, hash, visibility,
  frame, input and cleanup gates unchanged.
- Bump the terminal and browser version to 0.4.6. The generated-shell boundary
  matrix, workbench suites and 124-test extracted package cover the new limit.
- Package exactly 50 source files in the deterministic 204,845-byte archive
  with SHA-256 `2114ed1d4722fa3f649def46e88d6ffa28960eb2024bf06283aedd473f044362`.

The 0.4.6 runtime archive with SHA-256
`5ff6dc0a1b70c2559ace7c72aa18140511c5769cedd989ece2204a914e7aa8f1`, from
source `0eb4bf8d80183eab23bf3f9dd9cd2d6081e0cdd6`, ran four times on Linux
ARM64. Two executions stopped at reason-11/DBUS_NO_REPLY, one guest run was
invalidated by an observer port mismatch, and the controlled dedicated-port
run cleared reason-11, IVI and native/model submission before a typed
probe_receipt timeout. It published no fresh frame, admitted no input,
acknowledged Stop and removed all owned runtime resources. A later
documentation-only checkpoint advanced the source to
`79b214db40cb1b389c22965175ab07ccfb1fbe10` and produced the downloadable
2114 archive; every runtime source path is byte-identical. Successful Linux
rendering remains unverified.

## 0.4.5 - 2026-11-23

- Bind the validated probe capture time into the bounded DLT scanners and
  accept a matching component timeout marker only when its complete in-range
  timestamp is strictly later than that capture.
- Keep pre-capture, equal-time, malformed, undated, out-of-range and unbound
  markers fatal as native_timeout evidence. The capture, frame, input,
  identity, deadline and restoration gates are unchanged.
- Add synthetic end-to-end coverage for post-capture success, equal-time
  failure and malformed post-capture failure. The private consolidated gate
  passed 19 suites; the extracted public package passed 124 tests with one
  explicit skip.
- Freeze the deterministic 50-file source archive at 204,407 bytes
  with SHA-256 8bfed51454844baec442ccd5ea25f44a73a8f5c01c5f74cb6e8f923cf95ce4bd.
- Record that this source fix was motivated by the exact public 0.4.4 Linux
  ARM64 run, which failed closed at 78 percent with native_timeout and
  published no frame or input. Workbench 0.4.5 has no successful live-rendering
  claim until a changed archive run completes.

## 0.4.4 - 2026-11-23

- Accept one complete LF-framed, nonce-bound probe-failure envelope with
  canonical inventory ordering and exact PID, start, arm and deadline context.
- Retain only fixed typed timeout code, observation state, callback count,
  unchanged comparison count and elapsed-time fields. Malformed, duplicate,
  truncated, oversized and context-mismatched evidence remains unavailable.
- Preserve the original acquisition failure, both deadline layers, frame and
  input refusal. The summary never converts pixels, publishes a frame or
  qualifies success.
- Package 50 files in the 203,969-byte source archive with SHA-256
  `95607cafb96e147c330c0101eb8a056fed2cfcd0b852752ea42d776517d458c4`.

The retained Linux foreground transcript is 0.4.3 evidence. Live 0.4.4
rendering remains unverified.

## 0.4.3 - 2026-11-23

- Sample the log immediately before the IVI foreground request and again on
  `reason11` failure. Report the furthest ordered native phase using complete
  records within those boundaries.
- Refuse incomplete records, invalid boundaries, changed log identity, and
  contradictory phase sequences. Emit fixed phase labels and keep raw logs
  private.
- Preserve the foreground request, timeout layers, acquisition result, and
  frame and input checks. The phase label describes sampled activity and
  leaves reply delivery and causality unresolved.
- Package 50 files in the 203,590-byte source archive with SHA-256
  `2c71c0d56a993fe8742db6cb60f7ba212baca8b3a09b4be9adc94520f3c3f9b7`.

Live 0.4.3 rendering remains unverified.

## 0.4.2 - 2026-11-23

- Preserve the fail-closed `newline_check_failed` result and raw-trace refusal,
  while reporting fixed typed observations from valid complete DLT records
  before an incomplete final record.
- Skip a first fragment that crosses the acquisition boundary and reject wrong
  context, malformed, duplicate, swapped-channel, replaced, truncated,
  prefix-mismatched, oversized, or read-failed evidence.
- Report marker absence only as `not_observed_in_complete_prefix` with
  `absence_not_proven=true`. Change no foreground call, deadline, success,
  frame, capture, or input gate.
- Package 50 files in the 201,953-byte source archive with SHA-256
  `ab50eb06fd103f084d71367a4b8543ffea6172be85d2cd373446a734ec1f1bb8`.

Live 0.4.2 rendering remains unverified.

## 0.4.1 - 2026-11-22

- Remove the unused standalone screenshot budget check from the IVI capture
  path. Preserve the strict 15-second capture/receipt deadline, the 20-second
  verification deadline, and the rest of the admission checks.
- Verify the generated shell's `pipefail` behavior with an upstream-only
  `tail` failure. The generated shell's requirement for that option limits
  the earlier 0.4.0 changelog's statement about masked failures.
- Package 50 files in the 200,757-byte source archive with SHA-256
  `03f4a93c5faaf46eeb75b7bcf61b668197764f435556a31da90266ba37b80bd9`.

Live 0.4.1 rendering remains unverified.

## 0.4.0 - 2026-11-22

- Report `read_failed` when the bounded final-byte pipeline returns a failure
  status. A zero count still produces `newline_check_failed`. The status
  follows the final pipeline command, so a failed upstream read can still
  appear as a zero count.
- Retain the D-Bus request and its failure result, the two scans, and the
  existing deadlines and validation checks.
- Package exactly 50 source files in the 200,600-byte archive with SHA-256
  `89c716f6e5d321a3b16d538ca317f749308999293b80c5311aaa7d6cc00a6ae4`.

The 0.3.9 Linux ARM64 run stopped at `reason11` / `DBUS_NO_REPLY` with
no frame or input. The timeout cause and live 0.4.0 rendering remain
unverified.

## 0.3.8 - 2026-11-22

- Select `max,vendor=GenuineIntel,-avx2` only for Linux and WSL2 ARM64 QEMU
  TCG hosts; keep macOS and all x86-64 hosts on
  `max,vendor=GenuineIntel`.
- Pass the selected CPU profile to the shared VM boot command and report it in
  the runtime started event and status response.
- Publish a deterministic 50-file source archive, 199,971 bytes, with SHA-256
  `7cdb3ce9cbc836aa90dc5f9730eeef8d9cce74d7fc38e36bf88dbc333ffc5c83`.

This is a source-accepted candidate. The changed full-assets Linux ARM64 run
is still pending at the time of this snapshot, so this file does not claim that
the earlier llvmpipe/AppStandbyClock crash is fixed or that 0.3.8 is
live-qualified. The retained 0.3.5 macOS run remains the latest successful
guest qualification. Real Windows/Linux rendering and physical radio,
installation, recovery, and restoration remain unqualified. SCOURGE is 0/6.

## 0.3.7 - 2026-11-21

- Record bounded operation timings around the existing post-receipt identity,
  output-hash and two log-scan phases without adding external applet
  invocations or extending the 15/20-second deadlines.
- Keep timing metadata optional: malformed, duplicated, oversized or truncated
  samples cannot alter acquisition success/failure or replace retained native
  timeout evidence.
- Publish a deterministic 50-file source archive with SHA-256
  `275d227bc19e43dd7c24036445b8d2c048b341be4805f523d62e4714032c7da9`.

Version 0.3.7 was a diagnostic developer preview. The retained 0.3.5 Mac run
remained the latest successful guest qualification; live 0.3.7 timing,
Windows/Linux rendering and physical radio, installation, recovery, and
restoration remained unqualified. SCOURGE was 0/6.

## 0.3.6 - 2026-11-21

- Continue WSL VM preparation when optional Windows Explorer browser handoff
  cannot be validated or launched; warn and preserve the exact printed URL.
- Attempt clone-based workspace creation before capacity rejection. When a
  buffered copy is required, account for sparse extents, report bounded copy
  progress separately from digest verification, translate space/quota errors,
  and remove only the owned partial workspace.
- Publish a deterministic 50-file source archive with SHA-256
  `4b18f8626c78b751abc1d1b6b6c04aba4512a903609ae7807f08b53c5849603e`.

This release remained a developer preview. Windows/Linux first-run setup and
physical radio, installation, recovery, and restoration remained unqualified.
SCOURGE was 0/6.

## 0.3.5 - 2026-11-21

- Batch fixed-path metadata and digest queries during bounded guest acquisition
  while retaining both final log scans, every identity sample, substitution
  guard, marker failure and the exact 15/20-second deadlines.
- Reject truncated paired output, scratch replacement during hashing, malformed
  process-stat records and a timeout appended during final identity checking.
- Complete guest acquisition verification in 15,150 ms during one changed
  zero-input macOS run, publish historical then fresh 1920x720 compositor
  frames, render the Gen5W Home UI, and shut down without an owned listener,
  QEMU process, helper or task socket remaining.
- Publish a deterministic 50-file source archive with SHA-256
  `cf74874ba43d3ebb64a701e2da5a8ec3f873c24ea49910f12159b1c83a3fd9a8`.

This release remained a developer preview. Windows and Linux first-run setup,
physical radio behavior, installation, and restoration were not qualified.
SCOURGE was 0/6.

## 0.3.4 - 2026-11-21

- Add explicit noninteractive setup consent for the Windows/WSL launcher and
  show deferred UAC, reboot, and Ubuntu account prerequisites.
- Validate browser handoff paths, accept both loopback address families, and
  retain numeric loopback fallback.
- Report WSL `/dev/kvm` exposure without changing the fixed QEMU TCG launch
  policy.
- Add a PowerShell launcher fixture and preserve an existing host-file edit.
- Report incomplete owned-process shutdown and flush the shutdown JSON body
  before the foreground service exits.
- Publish a deterministic source-only archive with SHA-256
  `cb21b284e3557102119bdce35c339eade8b19ab699f90b2e8d8517011ef3dc17`.

This release remained a developer preview. Windows WSL setup, dependency
installation, hostname setup, browser operation, prepared guest rendering and
input, physical radio behavior, installation, and restoration were not
qualified. SCOURGE was 0/6.
