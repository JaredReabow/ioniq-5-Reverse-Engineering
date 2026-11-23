# Public release boundary

This directory is a frozen, sanitized, parentless publication snapshot for
Gen5W VM Workbench 0.4.5. It is assembled from source commit 7a38b3421f52880f4069c100dba34c49f914f475.

The downloadable source archive contains exactly the 50 paths in
docs/gen5w-vm-server-files.txt. The public Git snapshot contains those 50
source members plus five release wrapper documents: ATTRIBUTION.md,
CHANGELOG.md, HISTORY.md, PUBLIC-RELEASE.md, and README.md.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains AGPL-3.0-only; the complete local licence text is included.

Workbench 0.4.5 accepts a matching timeout marker only when the same complete,
in-range DLT timestamp is strictly later than a validated probe capture.
Pre-capture, equal-time, malformed, undated, out-of-range and unbound markers
remain fatal. The change does not alter the capture, frame, input, identity,
deadline or recovery gates.

The exact public 0.4.4 source archive was run on Linux ARM64. It reached 78
percent and stopped with typed guestacquisitionerror / native_timeout, published
no fresh frame and admitted zero input. It then acknowledged Stop and cleaned
up all owned resources. Version 0.4.5 has passed source, synthetic and
extracted-package tests, but no successful 0.4.5 live rendering has yet been
qualified. Windows native deployment, successful Linux rendering, physical
radio behavior, installation, recovery and restoration remain unverified.
SCOURGE is at 0/6.

Publication uses the exact archive bound by SHA-256 8bfed51454844baec442ccd5ea25f44a73a8f5c01c5f74cb6e8f923cf95ce4bd, after
coordinator review. No GitHub Actions run is required or authorized.
