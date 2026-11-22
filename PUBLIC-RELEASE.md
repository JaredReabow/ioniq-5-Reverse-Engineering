# Public release boundary

This directory is a frozen, sanitized, parentless publication candidate for
Gen5W VM Workbench 0.4.0. It is assembled from source commit
`ad835a5a7693d6aed1ec57825120ac91e744fb05`.

The downloadable source archive contains exactly the 50 paths in
`docs/gen5w-vm-server-files.txt`. The public Git snapshot contains those 50
source members plus five release wrapper documents: `ATTRIBUTION.md`,
`CHANGELOG.md`, `HISTORY.md`, `PUBLIC-RELEASE.md`, and `README.md`.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains `AGPL-3.0-only`; the complete local licence text is included.

All 19 source suites passed before packaging. Workbench 0.4.0 adds a bounded
log snapshot diagnostic for a reported nonzero final-byte pipeline status.
The D-Bus timeout cause and successful Linux or Windows rendering remain
unverified. Physical radio, installation, recovery, and restoration remain
unverified. SCOURGE is at 0/6.

Publication must use the exact archive bound by
SHA-256 `89c716f6e5d321a3b16d538ca317f749308999293b80c5311aaa7d6cc00a6ae4`,
after coordinator review. No GitHub Actions run is required or authorized.
