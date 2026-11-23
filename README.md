# Gen5W VM Workbench

Gen5W VM Workbench is a source-only developer preview that runs the existing
interactive Gen5W virtual-machine backend and exposes its terminal output in a
browser at gen5w.local. It includes launchers for macOS, Linux, and Windows
through WSL2 plus explicit dependency, progress, and shutdown reporting.

This directory is a frozen, sanitized, parentless publication snapshot for
version 0.4.7. It contains no private Git history, firmware, prepared disks,
vendor binaries, credentials, raw captures, or private backups.

## Start here

- Read [the setup and limitations](docs/gen5w-vm-server.md).
- Download gen5w-vm-server-v0.4.7.tar.gz from the
  [0.4.7 prerelease](https://github.com/JaredReabow/ioniq-5-Reverse-Engineering/releases/tag/gen5w-vm-server-v0.4.7).
- Use one of the launchers in launchers/ after following the documented host
  and prepared-asset requirements.

The launcher does not download or create the prepared Gen5W assets. The
interactive VM requires the exact compatible user-supplied prepared profile
described in the setup guide. This is not a stock-update converter.

## Qualification boundary

The retained 0.3.5 macOS candidate completed exact asset admission, guest
acquisition, historical then fresh 1920x720 frame publication, visible Gen5W
Home rendering, and clean shutdown in one changed zero-input run.

Version 0.4.7 extends only the bounded foreground capture-observation window
from 15 to 30 seconds. The exact tested archive, SHA-256
`9d47be5627c9927449e511c75af0ed0380d99788d25a12029d46d8438beee1e9`,
completed one controlled Ubuntu 24.04.5 ARM64 run with QEMU 8.2.2 TCG. It
reached 100 percent, returned the unauthenticated 403 refusal, served two fresh
1920x720 guest-compositor frames, admitted zero input, completed an exact
166/166-byte authenticated Stop response, exited 0 and left no owned listener,
socket or process group. A staging-only first attempt using a mutated prior
runtime rootfs failed closed with `asseterror` before the controlled run.

The final downloadable archive, SHA-256
`2fa4373c807c68943356bec86fe98b444ca6bc26c6cbf381938f4a63108d35cc`,
contains documentation changes only after the qualified runtime commit. Every
runtime source blob is byte-identical to the tested archive. The extracted
package passes 124 tests with 123 passing and one expected native-PowerShell
skip.

Pointer delivery, human desktop interaction, native Windows execution and
physical installation, recovery, restoration and radio behavior remain
unverified. SCOURGE is at 0/6.

## Licence and attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) and the preserved
[licence text](LICENSES/AGPL-3.0-only.txt).
