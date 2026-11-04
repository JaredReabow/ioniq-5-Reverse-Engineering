#!/usr/bin/env python3.13
"""Verify that Ioniq5-HISTORY.md has only ever grown.

The history log is supposed to be append-only. That is an invariant nobody can check by reading the file, because a rewrite looks exactly like an append once it has happened. This
walks the file's git history and asserts that every stored version is a **prefix** of the next one - which is precisely what "append-only" means and precisely what a silent
edit or a reordering would violate.

Usage:
    python3.13 tools/check_history_append_only.py [--file Ioniq5-HISTORY.md]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def revisions(path: str) -> list[tuple[str, str]]:
    """[(commit, blob sha)] oldest first, for every commit that touched the file."""
    shas = subprocess.run(
        ["git", "log", "--reverse", "--format=%H", "--", path],
        capture_output=True, text=True, check=True).stdout.split()
    out = []
    for commit in shas:
        blob = subprocess.run(["git", "rev-parse", f"{commit}:{path}"],
                              capture_output=True, text=True)
        if blob.returncode == 0:
            out.append((commit[:8], blob.stdout.strip()))
    return out


def content(blob: str) -> str:
    return subprocess.run(["git", "cat-file", "-p", blob],
                          capture_output=True, text=True, check=True).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="Ioniq5-HISTORY.md")
    ap.add_argument("--baseline", type=int, default=None,
                    help="known pre-existing violation count; only exceeding it is a failure")
    args = ap.parse_args()

    revs = revisions(args.file)
    if not revs:
        print(f"no history for {args.file}", file=sys.stderr)
        return 2
    print(f"{args.file}: {len(revs)} revisions, oldest {revs[0][0]} -> newest {revs[-1][0]}")

    violations = 0
    prev_commit, prev_blob = revs[0]
    prev = content(prev_blob)
    for commit, blob in revs[1:]:
        cur = content(blob)
        if not cur.startswith(prev):
            violations += 1
            # first difference, for a useful message
            i = next((k for k in range(min(len(prev), len(cur))) if prev[k] != cur[k]), min(len(prev), len(cur)))
            line = prev.count("\n", 0, i) + 1
            print(f"  VIOLATION at {commit}: not an append of {prev_commit}")
            print(f"    first difference at byte {i} (line {line}); {len(prev)} -> {len(cur)} bytes")
            print(f"    previous: {prev[max(0,i-40):i+40]!r}")
            print(f"    current : {cur[max(0,i-40):i+40]!r}")
        prev_commit, prev = commit, cur

    total = len(content(revs[-1][1]))
    print(f"final size {total} bytes; violations: {violations}")
    baseline = args.baseline
    if baseline is None:
        b = Path("tools/history_append_baseline.txt")
        if b.exists():
            baseline = int(b.read_text().split()[0])
    if baseline:
        regressions = max(0, violations - baseline)
        print(f"baseline: {baseline} known pre-session rewrites (recorded in the log entry of 2026-11-05)")
        print("RESULT:", "no new rewrites" if regressions == 0 else f"{regressions} NEW REWRITE(S)")
        return 0 if regressions == 0 else 1
    print("RESULT:", "append-only" if violations == 0 else "REWRITTEN AT LEAST ONCE")
    return 0 if violations == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
