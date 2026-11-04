#!/usr/bin/env python3.13
"""Consistency check for the vulnerability register.

The register has been edited by hand dozens of times, cross-referenced from a dozen documents, and corrected nine times in one session. This catches the two failure modes that
matter: a numbered entry that has been duplicated or lost, and a document citing an entry number that no longer exists.

It deliberately does not judge content. A green run means "the numbering and references are coherent", not "the findings are right".

Usage:
    python3.13 tools/check_register_consistency.py [--root .]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ENTRY = re.compile(r"^## (V-\d{3})\b(.*)$", re.M)
REF = re.compile(r"\bV-(\d{3})\b")
STATUS_HINTS = ("demonstrated", "confirmed", "candidate", "latent", "unproven", "withdrawn", "corrected", "measured")


def status_of(body: str) -> str:
    """Best-effort status label: the first hint word found in the entry's opening lines."""
    head = "\n".join(body.splitlines()[:12]).lower()
    for hint in STATUS_HINTS:
        if hint in head:
            return hint
    return "(no status word)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    register = root / "Ioniq5-VULNERABILITIES.md"
    if not register.exists():
        print(f"no register at {register}", file=sys.stderr)
        return 2
    text = register.read_text()
    matches = list(ENTRY.finditer(text))

    ids = [m.group(1) for m in matches]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    entries: dict[str, str] = {}
    for idx, m in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        entries[m.group(1)] = text[m.start():end]

    numeric = sorted(int(i.split("-")[1]) for i in ids)
    gaps = [n for n in range(min(numeric), max(numeric) + 1)
            if n not in set(numeric)] if numeric else []

    print(f"entries: {len(ids)}  range: V-{min(numeric, default=0):03d}..V-{max(numeric, default=0):03d}")
    print(f"duplicates: {dupes or 'none'}")
    print(f"gaps in numbering: {['V-%03d' % n for n in gaps] or 'none'}")

    by_status: Counter[str] = Counter()
    print("\nstatus by entry:")
    for m in matches:
        st = status_of(entries[m.group(1)])
        by_status[st] += 1
        title = m.group(2).strip(" —-:")[:74]
        print(f"  {m.group(1)}  {st:<16} {title}")
    print("\nsummary:", ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())))

    # cross-references from every markdown document
    known = set(ids)
    bad: list[tuple[str, str]] = []
    for doc in sorted(root.rglob("*.md")):
        if ".git" in doc.parts or "work" in doc.parts:
            continue
        for ref in set(REF.findall(doc.read_text(errors="replace"))):
            vid = f"V-{ref}"
            if vid not in known:
                bad.append((str(doc.relative_to(root)), vid))
    print(f"\ndangling references: {len(bad)}")
    for doc, vid in sorted(set(bad))[:20]:
        print(f"  {doc} -> {vid}")

    ok = not dupes and not gaps and not bad
    print("\nRESULT:", "coherent" if ok else "NEEDS ATTENTION")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
