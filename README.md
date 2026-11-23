# Gen5W VM Workbench

Gen5W VM Workbench is a source-only developer preview that runs the existing
interactive Gen5W virtual-machine backend and exposes its terminal output in a
browser at gen5w.local. It includes launchers for macOS, Linux, and Windows
through WSL2 plus explicit dependency, progress, and shutdown reporting.

This directory is a frozen, sanitized, parentless publication snapshot for
version 0.4.8. It contains no private Git history, firmware, prepared disks,
vendor binaries, credentials, raw captures, or private backups.

## Start here

- Read [the setup and limitations](docs/gen5w-vm-server.md).
- Download gen5w-vm-server-v0.4.8.tar.gz from the
  [0.4.8 prerelease](https://github.com/JaredReabow/ioniq-5-Reverse-Engineering/releases/tag/gen5w-vm-server-v0.4.8).
- Use one of the launchers in launchers/ after following the documented host
  and prepared-asset requirements.

The launcher does not download or create the prepared Gen5W assets. The
interactive VM requires the exact compatible user-supplied prepared profile
described in the setup guide. This is not a stock-update converter.

## Qualification boundary

Version 0.4.8 keeps terminal failures visible for browser Stop and bounds a
headless or disconnected failure to 30 seconds before owned-resource cleanup.
The exact 205,723-byte archive with SHA-256
`0f786f312012eccf6a46950816e7755dfdeed9149cc06bb12473328d5ec2b558`
was extracted and passed 125 tests with one expected native-PowerShell skip.

The visible macOS launcher then ran from that exact extraction with the verified
local assets. It reused the Zig cache, reached 100 percent with guest networking
disabled, returned the unauthenticated 403 refusal, served fresh 1920x720
guest-compositor frames at sequences 2 and 3, and completed a same-origin click
whose following frame changed at sequence 4. Stop returned the exact 166-byte
receipt, 100 event IDs were contiguous, the launcher exited 0 after 206.43
seconds, and no owned listener or QEMU process remained.

Native Windows execution, human desktop interaction and physical installation,
recovery, restoration and radio behavior remain unverified. SCOURGE is at 0/6.

## Licence and attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) and the preserved
[licence text](LICENSES/AGPL-3.0-only.txt).
