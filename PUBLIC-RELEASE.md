# Public release boundary

This directory is a frozen, sanitized, parentless publication snapshot for
Gen5W VM Workbench 0.4.6. It is assembled from source commit 79b214db40cb1b389c22965175ab07ccfb1fbe10.

The downloadable source archive contains exactly the 50 paths in
docs/gen5w-vm-server-files.txt. The public Git snapshot contains those 50
source members plus five release wrapper documents: ATTRIBUTION.md,
CHANGELOG.md, HISTORY.md, PUBLIC-RELEASE.md, and README.md.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains AGPL-3.0-only; the complete local licence text is included.

Workbench 0.4.6 preserves the 0.4.5 post-capture timeout distinction and keeps
the same target identity, receipt, hash, visibility, frame, input and cleanup
gates. The exact 0.4.5 Linux ARM64 run completed both bounded log scans, but
the second scan crossed the old 20-second verification deadline. Version 0.4.6
extends only that bounded verification window to 30 seconds for slower ARM64
TCG hosts.

The 0.4.6 runtime source was exercised four times on Linux ARM64 using archive
SHA-256 `5ff6dc0a1b70c2559ace7c72aa18140511c5769cedd989ece2204a914e7aa8f1`
from source `0eb4bf8d80183eab23bf3f9dd9cd2d6081e0cdd6`. Two executions
stopped at reason-11/DBUS_NO_REPLY, one guest execution was invalidated by an
observer fixed-port mismatch, and the controlled dedicated-port execution
cleared reason-11, IVI and native/model submission before a typed probe_receipt
timeout at 78 percent. No fresh frame was published and zero input was
admitted. Authenticated Stop and complete owned-resource cleanup succeeded.
After qualification, a documentation-only checkpoint advanced the source to
`79b214db40cb1b389c22965175ab07ccfb1fbe10` and produced the downloadable archive
below. Every runtime source path is byte-identical between those commits; the
five changed files are documentation. The final archive was extracted and
passed 124 tests with one expected native-PowerShell skip. Windows native
deployment, successful Linux rendering, physical radio behavior, installation,
recovery and restoration remain unverified. SCOURGE is at 0/6.

Publication uses the exact archive bound by SHA-256 2114ed1d4722fa3f649def46e88d6ffa28960eb2024bf06283aedd473f044362, after
coordinator review. No GitHub Actions run is required or authorized.
