# Public release boundary

This directory is a frozen, sanitized, parentless publication snapshot for
Gen5W VM Workbench 0.4.7. It is assembled from source commit cb7fab9adf444b307065844dfca3e1c997838fde.

The downloadable source archive contains exactly the 50 paths in
docs/gen5w-vm-server-files.txt. The public Git snapshot contains those 50
source members plus five release wrapper documents: ATTRIBUTION.md,
CHANGELOG.md, HISTORY.md, PUBLIC-RELEASE.md, and README.md.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains AGPL-3.0-only; the complete local licence text is included.

Version 0.4.7 extends only the foreground capture-observation deadline from 15
to 30 seconds. The exact runtime archive with SHA-256
`9d47be5627c9927449e511c75af0ed0380d99788d25a12029d46d8438beee1e9`
from source `1e5fbccdb028e802b482457ebdb1968e75f0b5ae` completed one
controlled Ubuntu 24.04.5 ARM64 Linux run with QEMU TCG. It reached 100
percent, served two fresh 1920x720 guest-compositor frames, admitted zero input,
returned an authenticated 166/166-byte Stop response, exited 0, retained 289
contiguous events and left no owned listener, socket or process group.

After qualification, a documentation-only checkpoint advanced source to
`cb7fab9adf444b307065844dfca3e1c997838fde` and produced the final deterministic 205,175-byte archive with
SHA-256
`2fa4373c807c68943356bec86fe98b444ca6bc26c6cbf381938f4a63108d35cc`.
Every runtime source path is byte-identical to the tested archive. The final
archive was extracted and passed 124 tests with one expected native-PowerShell
skip. Pointer delivery, human desktop interaction, native Windows execution,
physical installation, recovery, restoration and radio behavior remain
unverified. SCOURGE is at 0/6.

Publication uses the exact archive bound by SHA-256
`2fa4373c807c68943356bec86fe98b444ca6bc26c6cbf381938f4a63108d35cc` after
coordinator review. No GitHub Actions run is required or authorized.
