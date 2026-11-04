#!/usr/bin/env python3.13
"""Check that every markdown link/reference between tracked documents resolves.

Documentation that cites a file which no longer exists is worse than no citation, and this tree has been reorganised several times. Only local paths are checked; URLs are skipped.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

LINK = re.compile(r"(?:\]\(|`)(\.{0,2}/?[A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|sh|c|json|log|png|ppm|xml|txt))(?:\)|`)")


def tracked_markdown(root: Path) -> list[Path]:
    # -z and NUL splitting: the repository has paths containing spaces (e.g. "engineering mode/")
    out = subprocess.run(["git", "ls-files", "-z", "*.md"], cwd=root,
                         capture_output=True, text=True, check=True).stdout
    return [root / p for p in out.split("\0") if p]


def allowlist(root: Path) -> dict[tuple[str, str], str]:
    """{(document, reference): 'CATEGORY reason'} for references deliberately skipped."""
    f = root / "tools/doc_link_allowlist.txt"
    out: dict[tuple[str, str], str] = {}
    if not f.exists():
        return out
    for line in f.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        head, _, why = line.partition("|")
        doc, _, ref = head.partition("->")
        out[(doc.strip(), ref.strip())] = why.strip()
    return out


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    allowed = allowlist(root)
    bad: list[tuple[str, str]] = []
    skipped: list[tuple[str, str, str]] = []
    checked = 0
    for doc in tracked_markdown(root):
        text = doc.read_text(errors="replace")
        for ref in sorted(set(LINK.findall(text))):
            if ref.startswith("http"):
                continue
            # Absolute paths are guest-image paths (/etc/fde_test_v2.sh, /bin/check-mount.sh), not
            # repository files. Only treat them as references if they resolve inside the repo.
            if ref.startswith("/") and not (root / ref.lstrip("/")).exists():
                continue
            # Bare filenames in prose ("see appnavi-bg-probe.sh") are not links; only path-shaped
            # references are checked. A reference with a directory separator is a claim about location.
            if "/" not in ref:
                continue
            # Only references into this repository are checkable. Citations of upstream source trees
            # (ABL, AirPlay, third-party code) and guest-image paths are not our files and are skipped.
            REPO_ROOTS = ("docs/", "evidence/", "tools/", "tests/", "./", "../", "Ioniq5-")
            if not ref.startswith(REPO_ROOTS):
                continue
            # Guest-image paths are documented without a leading slash (etc/fde_test_v2.sh, app/bin/...).
            GUEST_PREFIXES = ("etc/", "app/", "usr/", "bin/", "sbin/", "lib/", "system/", "opt/", "proc/", "sys/", "dev/",
                              "R/", "./app/", "./etc/", "./usr/", "./lib/", "./system/")
            if ref.startswith(GUEST_PREFIXES):
                continue
            checked += 1
            candidates = [doc.parent / ref, root / ref, doc.parent / ref.lstrip("./")]
            if not any(c.exists() for c in candidates):
                key = (str(doc.relative_to(root)), ref)
                if key in allowed:
                    skipped.append((key[0], key[1], allowed[key]))
                else:
                    bad.append(key)
    print(f"documents: {len(tracked_markdown(root))}  references checked: {checked}  unresolved: {len(bad)}")
    for doc, ref in bad[:30]:
        print(f"  {doc} -> {ref}")
    if skipped:
        print(f"skipped {len(skipped)} listed reference(s):")
        for doc, ref, why in skipped:
            print(f"  [{why.split()[0]}] {doc} -> {ref}")
    print("RESULT:", "all references resolve" if not bad else "UNRESOLVED REFERENCES")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
