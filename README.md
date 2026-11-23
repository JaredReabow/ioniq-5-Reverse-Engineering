# Gen5W VM Workbench

Gen5W VM Workbench is a source-only developer preview that runs the existing
interactive Gen5W virtual-machine backend and exposes its terminal output in a
browser at gen5w.local. It includes launchers for macOS, Linux, and Windows
through WSL2 plus explicit dependency, progress, and shutdown reporting.

This directory is a frozen, sanitized, parentless publication snapshot for
version 0.4.5. It contains no private Git history, firmware, prepared disks,
vendor binaries, credentials, raw captures, or private backups.

## Start here

- Read [the setup and limitations](docs/gen5w-vm-server.md).
- Download gen5w-vm-server-v0.4.5.tar.gz from the
  [0.4.5 prerelease](https://github.com/JaredReabow/ioniq-5-Reverse-Engineering/releases/tag/gen5w-vm-server-v0.4.5).
- Use one of the launchers in launchers/ after following the documented host
  and prepared-asset requirements.

The launcher does not download or create the prepared Gen5W assets. The
interactive VM requires the exact compatible user-supplied prepared profile
described in the setup guide. This is not a stock-update converter.

## Qualification boundary

The retained 0.3.5 macOS candidate completed exact asset admission, guest
acquisition, historical then fresh 1920x720 frame publication, visible Gen5W
Home rendering, and clean shutdown in one changed zero-input run. The exact
public 0.4.4 archive later ran on Linux ARM64, reached 78 percent, and stopped
with typed guestacquisitionerror / native_timeout; it published no fresh frame
and admitted zero input before authenticating Stop and cleaning up.

Workbench 0.4.5 treats a matching component timeout as non-fatal only when the
validated capture is bound and the marker's complete DLT timestamp is strictly
later than that capture. Pre-capture, equal-time, malformed, undated,
out-of-range and unbound markers still fail. Version 0.4.5 has passed source,
synthetic and extracted-package tests, but no successful 0.4.5 live rendering
has yet been qualified. Windows native deployment, successful Linux rendering,
and on-device radio, installation, recovery, and restoration remain
unverified. SCOURGE is at 0/6.

## Licence and attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) and the preserved
[licence text](LICENSES/AGPL-3.0-only.txt).
