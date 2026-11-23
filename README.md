# Gen5W VM Workbench

Gen5W VM Workbench is a source-only developer preview that runs the existing
interactive Gen5W virtual-machine backend and exposes its terminal output in a
browser at gen5w.local. It includes launchers for macOS, Linux, and Windows
through WSL2 plus explicit dependency, progress, and shutdown reporting.

This directory is a frozen, sanitized, parentless publication snapshot for
version 0.4.6. It contains no private Git history, firmware, prepared disks,
vendor binaries, credentials, raw captures, or private backups.

## Start here

- Read [the setup and limitations](docs/gen5w-vm-server.md).
- Download gen5w-vm-server-v0.4.6.tar.gz from the
  [0.4.6 prerelease](https://github.com/JaredReabow/ioniq-5-Reverse-Engineering/releases/tag/gen5w-vm-server-v0.4.6).
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

Workbench 0.4.6 retains the rule that a matching component timeout is non-fatal only when the
validated capture is bound and the marker's complete DLT timestamp is strictly
later than that capture. Pre-capture, equal-time, malformed, undated,
out-of-range and unbound markers still fail. The exact public 0.4.5 Linux
ARM64 run passed receipt and output validation but crossed the old 20-second
verification boundary during its second log scan at 23.3 seconds; it failed
closed, published no frame, admitted no input and completed authenticated
cleanup. Version 0.4.6 extends only that boundary to 30 seconds.

The 0.4.6 runtime archive from source `0eb4bf8d80183eab23bf3f9dd9cd2d6081e0cdd6`
has SHA-256 `5ff6dc0a1b70c2559ace7c72aa18140511c5769cedd989ece2204a914e7aa8f1`
and ran four times on Linux ARM64. Its controlled dedicated-port execution
cleared reason-11, IVI and native/model submission, validated the manifest and
QEMU CPU profile, then failed closed at 78 percent with typed probe_receipt.
Two earlier executions reached reason-11/DBUS_NO_REPLY. No fresh frame was
published and zero input was admitted. Authenticated Stop and complete resource
cleanup succeeded. A later documentation-only checkpoint produced the
downloadable 0.4.6 archive below; every runtime source path is byte-identical.
Successful Linux rendering remains unverified. Windows native deployment and
on-device radio, installation, recovery, and restoration remain unverified.
SCOURGE is at 0/6.

## Licence and attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) and the preserved
[licence text](LICENSES/AGPL-3.0-only.txt).
