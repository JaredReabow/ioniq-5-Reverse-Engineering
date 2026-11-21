# Changelog

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

This release remains a developer preview. Windows WSL setup, dependency
installation, hostname setup, browser operation, prepared guest rendering and
input, physical radio behavior, installation, and restoration are not
qualified. SCOURGE is 0/6.
