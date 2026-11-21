# Gen5W VM Workbench

Gen5W VM Workbench is a source-only developer preview that runs the existing
interactive Gen5W virtual-machine backend and exposes its terminal output in a
browser at `gen5w.local`. It includes launchers for macOS, Linux, and Windows
through WSL2 plus explicit dependency, progress, and shutdown reporting.

This branch is a sanitized, parentless publication snapshot for version 0.3.4.
It contains no private Git history, firmware, prepared disks, vendor binaries,
credentials, raw captures, or private backups.

## Start here

- Read [the setup and limitations](docs/gen5w-vm-server.md).
- Download the exact source archive from the
  [0.3.4 prerelease](https://github.com/JaredReabow/ioniq-5-Reverse-Engineering/releases/tag/gen5w-vm-server-v0.3.4).
- Use one of the launchers in `launchers/` after following the documented
  host and prepared-asset requirements.

The launcher does not download or create the prepared Gen5W assets. The
interactive VM requires the exact compatible user-supplied prepared profile
described in the setup guide. This is not a stock-update converter.

## Qualification boundary

This source-only developer preview has not established Windows WSL,
dependency installation, hostname setup, or browser operation on a real host.
Prepared guest rendering and input remain unqualified. Physical radio,
installation, and restoration behavior remain unqualified; SCOURGE is 0/6.

## Licence and attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) and the preserved
[licence text](LICENSES/AGPL-3.0-only.txt).
