# Ioniq 5 research validation harness

Read-only checks over the research ledger, evidence artifacts, frozen Council
packages, and pre-push Git scope. The harness never writes project files, never
runs anything from the ledger, and never mutates Git state (`git status` is
invoked with `--no-optional-locks`).

## Run

```bash
python3 tests/run_all.py              # human-readable report
python3 tests/run_all.py --json       # deterministic JSON report
python3 tests/run_all.py --only json,artifacts
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Exit codes: `0` all checks pass or report expected state (`info`/`pending`),
`1` a validation failure or blocked Ioniq push, `2` the harness itself could not
run (missing tool or bad root).

## Checks

| Check | What it proves |
| --- | --- |
| `ledger` | `workflow.py validate --json` exits 0 with no errors (warnings report as `info`) |
| `artifacts` | every ledger artifact re-hashes to its declared SHA-256; missing, stale, unsafe, or malformed entries fail |
| `json` | the ledger and every council packet, task, receipt, and manifest parse as JSON |
| `council` | each `council/review-batch-*/` with a packet is checked against its frozen directory: unusable packets, unsafe or mismatched artifacts, and fingerprint mismatches fail; a verified package with a non-`COMPLETE` history reports as `info` |
| `privacy` | scoped files contain no live secrets or private-key containers; identifiers are reported as private-repository information, and raw firmware/archive/capture files are permitted; findings name only file, line, and category |
| `docs` | dedicated Ioniq history/changelog exist once `T6` leaves the queued states; earlier it reports `pending` |
| `gitscope` | staged `kona_research/**` paths block; otherwise an Ioniq push passes only when an explicit `ioniq` remote resolves exactly to `JaredReabow/ioniq-5-Reverse-Engineering`, `remote.pushDefault` is `ioniq`, and no branch `pushRemote`, push URL, or URL rewrite redirects it |

`council/`, `evidence/`, and the root documents are in privacy scope.
`kona_research/` and `tests/` are excluded so Kona work stays untouched and
fixture strings cannot self-flag.

## Git scope acceptance

This public repository keeps both `origin` and the explicit `ioniq` remote
on the same destination. The guard reads one `git config --list -z`
snapshot and only echoes the destination fields it verifies, with any
embedded credentials redacted. The older shared private checkout may still
have a Kona `origin`; that historical configuration does not apply here.

A push passes only when all of these hold:

- `remote.ioniq.url` (and every `remote.ioniq.pushurl`, if any) is exactly
  `JaredReabow/ioniq-5-Reverse-Engineering` on `github.com`, over HTTPS or SSH;
- `remote.pushDefault` is `ioniq`;
- the current branch has no `pushRemote` or `pushurl` that overrides that
  destination, and no other branch pushes to Kona;
- no `url.*.insteadOf` or `url.*.pushInsteadOf` rule rewrites the Ioniq URL;
- no `kona_research/**` path is staged.

Blocking reason codes: `staged-kona-path`, `missing-ioniq-remote`,
`ioniq-remote-mismatch`, `insecure-ioniq-remote`, `ioniq-pushurl-mismatch`,
`push-default-not-ioniq`, `push-remote-kona-ev`, `branch-push-remote-overrides`,
`branch-push-remote-kona-ev`, `branch-push-remote-insecure`,
`branch-pushurl-mismatch`, `effective-push-mismatch`, `url-rewrite-redirect`,
`config-unavailable`, `status-unavailable`, and `branch-unavailable`.
Near matches (a fork, another owner, `Ioniq5`, a plain HTTP URL) all block. A
successful report exposes `verified_destination`; when the Kona `origin` is
present but inert it is flagged by `origin_kona` and `origin_kona_ignored`.

## Ioniq document ownership

The root `HISTORY.md` and `CHANGELOG.md` belong to the parallel Kona project.
The `docs` check therefore requires a dedicated Ioniq pair:
`Ioniq5-HISTORY.md` and `Ioniq5-CHANGELOG.md` by default, or explicitly
Ioniq-named paths declared in `T6.write_paths` (for example
`ioniq5/HISTORY.md`). Root Kona documents reported through the ledger are
recorded in `details.kona_owned_rejected` and never count as Ioniq proof; a
dedicated file that is a symlink to a Kona root document is rejected as
`details.kona_owned_alias`.

## Tool paths

The harness calls the installed skill CLIs:

- `IONIQ_WORKFLOW_VALIDATOR` (default `$HOME/.codex/skills/parallelism/scripts/workflow.py`)
- `IONIQ_COUNCIL_CHECKER` (default `$HOME/.codex/skills/the-council/scripts/council.py`)

`--workflow` and `--checker` override them per run.

## Expected live state

With the explicit `ioniq` remote and `remote.pushDefault=ioniq` configured,
`gitscope` passes when both remotes point at this public repository.
Removing or mismatching the explicit remote, overriding the push destination on
a branch, or staging `kona_research/**` reports `blocked`. Frozen Council
generations reviewed before a final reconciliation report `info` with
`BLOCKED`/`CHANGES_NEEDED` histories while their artifact bytes verify; only a
defective package or fingerprint mismatch fails.

## Public snapshot mode

When `PUBLIC-RELEASE.md` exists, the private ledger and frozen Council packets are excluded. The runner marks those checks `info`, validates the published history and changelog directly, and applies stricter public privacy checks. This is not a validation of the original private acceptance hashes.
