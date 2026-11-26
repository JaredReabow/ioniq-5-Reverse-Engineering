# Public release boundary

This directory is a frozen, sanitized, parentless publication snapshot for
Gen5W VM Workbench 0.5.2. It is assembled from independently accepted source
commit `aafc9ebec4eb4130451e4a058ba39d6c04004b74`.

The downloadable source archive contains exactly the 55 paths in
`docs/gen5w-vm-server-files.txt`. The public Git snapshot contains those source
members plus five release wrapper documents: `ATTRIBUTION.md`, `CHANGELOG.md`,
`HISTORY.md`, `PUBLIC-RELEASE.md`, and `README.md`.

The archive and public snapshot exclude firmware, prepared disks, recovered
vendor binaries, compiled helpers, credentials, raw captures, private backups,
private manifests, workflow packets, and private-only tests. The Wi-Fi
simulator remains AGPL-3.0-only; the complete local licence text is included.

Version 0.5.2 adds the visible cross-platform asset-free preview, safer Windows
Python discovery, strict clipped-D-Bus rejection, an ARM64-specific bounded
foreground window, stable timeout classification, and the complete integration
matrix in the downloadable source. The synthetic preview and browser automation
are not QEMU guest evidence.

Two builds produced the byte-identical 281,255-byte archive with SHA-256
`08e4916e3ca0e77cfd51be366dc27b75e6f3596b6b93d4627d4cb26daa6ace61`.
The `PACKAGE-SHA256SUMS` file has SHA-256
`2f88ef7ef950a07e0720a63cf79f7fbf93f075700982f7d72b95994935271c2a`.
The exact archive passed 194 tests with two expected skips on macOS and Ubuntu
24.04 ARM64. The Windows 11 X1 launcher harness passed 163 assertions and its
contract test.

The source-equivalent Linux ARM64 replay cleared the former D-Bus timeout and
reached the separate `native_entry` gate. It published no vendor frame, admitted
no input, completed authenticated Stop, and removed its owned runtime resources.
This is not evidence of successful vendor-HMI entry. Physical head-unit
installation, recovery, restoration, CAN, MICOM and radio behavior remain
unqualified. Full SCOURGE remains 0/6.

The private full-research history checker still reports 27 findings against its
stale baseline of 22. Published records are preserved and this parentless public
snapshot does not carry the private history. No GitHub Actions run is required
or authorized.
