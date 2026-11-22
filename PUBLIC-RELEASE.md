# Public release boundary

This directory is a frozen, sanitized, parentless publication candidate for
Gen5W VM Workbench 0.4.1. It is assembled from source commit
`e5fa1cf19cfd1aa9e6b2e17c7c7800dd8fe213b0`.

The downloadable source archive contains exactly the 50 paths in
`docs/gen5w-vm-server-files.txt`. The public Git snapshot contains those 50
source members plus five release wrapper documents: `ATTRIBUTION.md`,
`CHANGELOG.md`, `HISTORY.md`, `PUBLIC-RELEASE.md`, and `README.md`.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains `AGPL-3.0-only`; the complete local licence text is included.

Workbench 0.4.1 removes an unused standalone screenshot budget check from
the IVI capture path. The IVI capture and verification deadlines remain
15 and 20 seconds respectively. Successful Linux or Windows rendering remains
unverified. Physical radio, installation, recovery, and restoration remain
unverified. SCOURGE is at 0/6.

Publication must use the exact archive bound by
SHA-256 `03f4a93c5faaf46eeb75b7bcf61b668197764f435556a31da90266ba37b80bd9`,
after coordinator review. No GitHub Actions run is required or authorized.
