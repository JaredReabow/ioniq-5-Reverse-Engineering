# Public release boundary

This directory is a frozen, sanitized, parentless publication candidate for
Gen5W VM Workbench 0.4.4. It is assembled from source commit
`ca7d6f0c72a340a50412d8ca645c3442992d7571`.

The downloadable source archive contains exactly the 50 paths in
`docs/gen5w-vm-server-files.txt`. The public Git snapshot contains those 50
source members plus five release wrapper documents: `ATTRIBUTION.md`,
`CHANGELOG.md`, `HISTORY.md`, `PUBLIC-RELEASE.md`, and `README.md`.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains `AGPL-3.0-only`; the complete local licence text is included.

Workbench 0.4.4 retains one complete, canonical, nonce-bound producer-failure
envelope and exposes only fixed typed timeout, observation, callback,
comparison and elapsed-time fields. Malformed, duplicate, truncated, oversized
or context-mismatched evidence leaves the original acquisition failure in
place. It never qualifies pixels, converts output, publishes a frame or admits
input. The IVI capture and verification deadlines remain 15 and 20 seconds.
The retained Linux foreground transcript was produced from 0.4.3 source.
Live 0.4.4, Windows and Linux rendering, and physical radio, installation,
recovery, and restoration remain unverified. SCOURGE is at 0/6.

Publication must use the exact archive bound by
SHA-256 `95607cafb96e147c330c0101eb8a056fed2cfcd0b852752ea42d776517d458c4`,
after coordinator review. No GitHub Actions run is required or authorized.
