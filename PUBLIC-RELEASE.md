# Public release boundary

This directory is a frozen, sanitized, parentless publication snapshot for
Gen5W VM Workbench 0.4.8. It is assembled from measured source commit
940c280b149b1ffc569bf2751d42c5c303fe194c.

The downloadable source archive contains exactly the 50 paths in
docs/gen5w-vm-server-files.txt. The public Git snapshot contains those 50
source members plus five release wrapper documents: ATTRIBUTION.md,
CHANGELOG.md, HISTORY.md, PUBLIC-RELEASE.md, and README.md.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains AGPL-3.0-only; the complete local licence text is included.

Version 0.4.8 preserves the visible failure state for browser Stop while
bounding a headless or disconnected terminal failure to 30 seconds before
service and owned-listener cleanup. Two builds from the source commit produced
the byte-identical 205,723-byte archive with SHA-256
`0f786f312012eccf6a46950816e7755dfdeed9149cc06bb12473328d5ec2b558`.

The exact archive was extracted and passed 125 tests with 124 passing and one
expected native-PowerShell skip. Its visible macOS launcher then reached 100
percent with guest networking disabled, served advancing fresh 1920x720
compositor frames at sequences 2 and 3, completed a same-origin click that
produced changed frame 4, returned the exact 166-byte Stop receipt, retained
100 contiguous event IDs and exited 0 after 206.43 seconds. No owned listener
or QEMU process remained. Native Windows execution, physical installation,
recovery, restoration and radio behavior remain unverified. SCOURGE is at 0/6.

Publication uses the exact archive bound by SHA-256
`0f786f312012eccf6a46950816e7755dfdeed9149cc06bb12473328d5ec2b558` after
verification. No GitHub Actions run is required or authorized.
