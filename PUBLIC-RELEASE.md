# Public release boundary

This directory is a frozen, sanitized, parentless publication snapshot for
Gen5W VM Workbench 0.4.9. It is assembled from measured source commit
d0a0c2fcad3352ca763137b271e74c30bec7b0d0.

The downloadable source archive contains exactly the 50 paths in
docs/gen5w-vm-server-files.txt. The public Git snapshot contains those 50
source members plus five release wrapper documents: ATTRIBUTION.md,
CHANGELOG.md, HISTORY.md, PUBLIC-RELEASE.md, and README.md.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains AGPL-3.0-only; the complete local licence text is included.

Version 0.4.9 adds a WSL1 software-emulation path when nested virtualization is
unavailable while retaining WSL2 preference and the same QEMU TCG guest
contract. The slow profile uses an explicit bound for its 60-second foreground
window, bounded gzip transfer for raw evidence, and strict preservation of the
uncompressed hashes and every safety gate.

Two builds produced the byte-identical 206,122-byte archive with SHA-256
`b0e0305532d94f9272a1798ad6d362a325fb6835dca6e93f510169d70624146e`.
The extracted archive passed 127 tests with 126 passing and one expected
native-PowerShell skip; its launcher plan also completed.

The same source candidate completed a Windows 11 ARM64 WSL1 run at 100 percent
with guest networking disabled. It served fresh 1920x720 compositor frames,
acknowledged a same-origin pointer click and Escape tap, returned an exact
166-byte authenticated Stop, exited 0 after 880.63 seconds and left no owned
QEMU process or listener. The pointer moved into the Confirm control but no
application transition was observed.

Human desktop interaction, visibly effective input, physical installation,
recovery, restoration and radio behavior remain unverified. SCOURGE is at 0/6.

Publication uses the exact archive bound by SHA-256
`b0e0305532d94f9272a1798ad6d362a325fb6835dca6e93f510169d70624146e` after
verification. No GitHub Actions run is required or authorized.
