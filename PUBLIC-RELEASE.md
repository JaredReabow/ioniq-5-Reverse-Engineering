# Public release boundary

This directory is a frozen, sanitized, parentless publication candidate for
Gen5W VM Workbench 0.3.8. It is assembled from source commit
`eebe793fcd7d40c130740801f220209c536f577a`.

The downloadable source archive contains exactly the 50 paths in
`docs/gen5w-vm-server-files.txt`. The public Git snapshot contains those 50
source members plus five release wrapper documents: `ATTRIBUTION.md`,
`CHANGELOG.md`, `HISTORY.md`, `PUBLIC-RELEASE.md`, and `README.md`.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains `AGPL-3.0-only`; the complete local licence text is included.

This candidate is source-accepted only. The changed full-assets Linux ARM64
run is pending, so there is no 0.3.8 live qualification claim. Physical radio,
installation, recovery, and restoration remain unverified and SCOURGE remains
0/6.

Publication must use the exact archive bound by
SHA-256 `7cdb3ce9cbc836aa90dc5f9730eeef8d9cce74d7fc38e36bf88dbc333ffc5c83`,
after coordinator review. No GitHub Actions run is required or authorized.
