# Gen5W VM Workbench

Gen5W VM Workbench is a source-only developer preview that runs the existing
interactive Gen5W virtual-machine backend and exposes its terminal output in a
browser at `gen5w.local`. It includes launchers for macOS, Linux, and Windows
through WSL2 plus explicit dependency, progress, and shutdown reporting.

This directory is a frozen, sanitized, parentless publication candidate for
version 0.4.3. It contains no private Git history, firmware, prepared disks,
vendor binaries, credentials, raw captures, or private backups.

## Start here

- Read [the setup and limitations](docs/gen5w-vm-server.md).
- Use `gen5w-vm-server-v0.4.3.tar.gz` as the exact deterministic source archive.
- Use one of the launchers in `launchers/` after following the documented host
  and prepared-asset requirements.

The launcher does not download or create the prepared Gen5W assets. The
interactive VM requires the exact compatible user-supplied prepared profile
described in the setup guide. This is not a stock-update converter.

## Qualification boundary

The retained 0.3.5 macOS candidate completed exact asset admission, guest
acquisition, historical then fresh 1920x720 frame publication, visible Gen5W
Home rendering, and clean shutdown in one changed zero-input run. A full-assets
0.4.2 Linux ARM64 run stopped at `reason11` / `DBUS_NO_REPLY` before frame or
input qualification. Workbench 0.4.3 can report the furthest ordered native
phase from complete records bounded around a failing IVI foreground request.
The fixed label describes sampled log activity. Causality and reply delivery
remain unresolved. The IVI capture and verification deadlines still apply.
Live 0.4.3, Windows and Linux rendering, and on-device radio, installation,
recovery, and restoration remain unverified. SCOURGE is at 0/6.

## Licence and attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) and the preserved
[licence text](LICENSES/AGPL-3.0-only.txt).
