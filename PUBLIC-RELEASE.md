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

Before every push, run `python3 tests/run_all.py` and the unit suite. Public
mode checks tracked text for secrets, personal paths and VIN-shaped tokens,
and rejects raw evidence paths.
