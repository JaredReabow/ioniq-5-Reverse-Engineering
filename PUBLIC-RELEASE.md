# Public release boundary

This repository is a fresh Git snapshot of the sanitized IONIQ 5 research
tree. It has no commits from the earlier private repository. The older
private repository remains private while GitHub Support reviews removal of
its raw historical objects.

The public tree excludes raw owner USB exports, imported third-party
diagnostic dumps, compressed core dumps, driving and location traces, exact
private manifests, private workflow and Council packets, and full-text
third-party paper artifacts. Source material remains in a local private
archive. Historical research notes may describe the earlier private
workspace; those retention rules do not grant permission to publish raw
material here.

The authored VM code, experiment scripts, bounded findings and inspected
screenshots are published under `tools/`, `tests/`, `evidence/` and `vm/`.
The local VM work tree contains large generated disks, recovered vendor
binaries, raw logs and core dumps. Those artifacts are represented by hashes
and findings, not copied into this public Git history.

Before every push, run `python3 tests/run_all.py` and the unit suite. Public
mode checks tracked text for secrets, personal paths and VIN-shaped tokens,
and rejects raw evidence paths.

#### From the parallel repository

The public source tree intentionally excludes raw owner USB exports, imported third-party diagnostic dumps, compressed core dumps, raw driving/location traces, exact private manifests, private workflow and Council packets, and full-text third-party paper artifacts. The source material remains in the operator's local private archive. Local user paths have been anonymized.

The snapshot is prepared for public release, but GitHub may continue serving old imported raw commits by SHA after a force update. Verify server-side cleanup of those cached objects before changing visibility. The repository stays private until that verification succeeds.

Run `python3 tests/run_all.py` and the unit suite before any push. The integrated harness uses public mode when this file exists, checks all published text for secrets, personal paths and VIN-shaped tokens, and rejects raw evidence paths.
