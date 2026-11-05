#!/usr/bin/env python3.13
"""Report documents whose heading count fell between two commits.

Written after a mechanical rebuild silently dropped six sections from
docs/REMEDIATION-REPORT.md while its cross-reference table kept listing them. The
lesson was that a document can look verified and be missing whole sections, so this
tool asks the cheapest possible structural question of history: **did any document
lose headings and then keep going?**

A decrease is not automatically a defect - sections are sometimes merged or removed
deliberately - but every decrease deserves one look, and this lists them instead of
leaving that to memory.

Usage: python3.13 tools/check_doc_shrinkage.py [N_COMMITS] [PATH_FILTER]
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def headings(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.startswith("#"))


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    filt = sys.argv[2] if len(sys.argv) > 2 else ""
    log = subprocess.run(
        ["git", "-C", str(ROOT), "log", f"-{n}", "--name-only", "--pretty=format:__COMMIT__ %h"],
        capture_output=True, text=True).stdout

    commits, current = [], None
    for line in log.splitlines():
        if line.startswith("__COMMIT__ "):
            current = (line.split()[1], [])
            commits.append(current)
        elif line.strip() and current:
            current[1].append(line.strip())

    flagged = 0
    for sha, files in commits:
        for f in files:
            if not f.endswith(".md") or (filt and filt not in f):
                continue
            # compare consecutive COMMITS, not commit-to-worktree: a loss that was later
            # repaired is invisible to a worktree comparison, which is exactly how the six
            # missing report items went unnoticed for two turns.
            def show(rev):
                r = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{f}"],
                                   capture_output=True, text=True)
                return r.stdout if r.returncode == 0 else ""
            before, after = show(f"{sha}~1"), show(sha)
            if not before or not after:
                continue
            b, a = headings(before), headings(after)
            if a < b:
                print(f"  {sha}  {f}: {b} headings -> {a}   (delta {a-b})")
                flagged += 1

    print(f"  checked {len(commits)} commits; {flagged} document(s) with fewer headings at a later commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
