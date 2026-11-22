# Public release boundary

This directory is a frozen, sanitized, parentless publication candidate for
Gen5W VM Workbench 0.4.2. It is assembled from source commit
`e0a559ce7f153b2471a8e84d087ec0cb29fc97c6`.

The downloadable source archive contains exactly the 50 paths in
`docs/gen5w-vm-server-files.txt`. The public Git snapshot contains those 50
source members plus five release wrapper documents: `ATTRIBUTION.md`,
`CHANGELOG.md`, `HISTORY.md`, `PUBLIC-RELEASE.md`, and `README.md`.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains `AGPL-3.0-only`; the complete local licence text is included.

Workbench 0.4.2 keeps an incomplete reason-11 trace rejected while exposing a
fixed, failure-only summary of valid complete DLT records before the partial
tail. Raw content remains private and absent markers only mean
`not_observed_in_complete_prefix`. The IVI capture and verification deadlines
remain 15 and 20 seconds respectively. Successful Linux or Windows rendering
remains unverified. Physical radio, installation, recovery, and restoration
remain unverified. SCOURGE is at 0/6.

Publication must use the exact archive bound by
SHA-256 `ab50eb06fd103f084d71367a4b8543ffea6172be85d2cd373446a734ec1f1bb8`,
after coordinator review. No GitHub Actions run is required or authorized.
