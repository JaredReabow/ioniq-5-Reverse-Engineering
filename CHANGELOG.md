# Changelog

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
