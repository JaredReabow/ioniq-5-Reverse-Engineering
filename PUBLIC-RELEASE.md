# Public release boundary

This directory is a frozen, sanitized, parentless publication candidate for
Gen5W VM Workbench 0.4.3. It is assembled from source commit
`7c6e548e1740658e13733c4d061d1f66f1b8c3a6`.

The downloadable source archive contains exactly the 50 paths in
`docs/gen5w-vm-server-files.txt`. The public Git snapshot contains those 50
source members plus five release wrapper documents: `ATTRIBUTION.md`,
`CHANGELOG.md`, `HISTORY.md`, `PUBLIC-RELEASE.md`, and `README.md`.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains `AGPL-3.0-only`; the complete local licence text is included.

Workbench 0.4.3 samples the IVI log boundaries around the foreground request.
On `reason11` failure it can report the furthest verified ordered native phase
from complete records within those boundaries. The fixed phase label describes
sampled log activity. The cause of a timeout and D-Bus reply delivery remain
unresolved. The IVI capture and verification deadlines remain 15 and 20
seconds respectively. Live 0.4.3, Windows and Linux rendering, and physical
radio, installation, recovery, and restoration remain unverified. SCOURGE
is at 0/6.

Publication must use the exact archive bound by
SHA-256 `2c71c0d56a993fe8742db6cb60f7ba212baca8b3a09b4be9adc94520f3c3f9b7`,
after coordinator review. No GitHub Actions run is required or authorized.
