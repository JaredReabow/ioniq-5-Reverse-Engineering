# Attribution and licensing

Gen5W VM Workbench is authored and maintained by Jared Reabow as part of the
IONIQ 5 reverse-engineering project.

This 0.5.2 publication snapshot was assembled from independently accepted
product source at commit `aafc9ebec4eb4130451e4a058ba39d6c04004b74`. Its
deterministic source-only archive is 281,255 bytes with SHA-256
`08e4916e3ca0e77cfd51be366dc27b75e6f3596b6b93d4627d4cb26daa6ace61`.
The exact archive passed 194 extracted `test_vm*.py` tests with two expected
skips on macOS and Ubuntu 24.04 ARM64. The Windows 11 X1 launcher harness passed
163 assertions and its contract test. A source-equivalent Linux ARM64 replay
cleared the former D-Bus timeout, stopped at the separate `native_entry` gate
without frame or input, and completed an authenticated Stop with clean process
resource reaping.

The public Git history begins at this snapshot and does not include the
predecessor private history. The private full-research history checker reports
27 findings against its stale baseline of 22; this release preserves published
records and does not rewrite them to hide that discrepancy.

The Wi-Fi simulator source retains the SCOURGE Project contributors' copyright
notice and its AGPL-3.0-only SPDX identifier. The local licence text is
preserved at `LICENSES/AGPL-3.0-only.txt`. Host dependencies are installed from
the platform package manager during an explicitly accepted setup step and are
not bundled in this snapshot.
