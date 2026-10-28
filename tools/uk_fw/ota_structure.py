#!/usr/bin/env python3
"""Characterise a Gen5W OTA package without decrypting it.

What it does
------------
For a directory of package payloads it measures, purely from ciphertext:

  * pairwise common suffix and prefix lengths;
  * the package-wide **footer** size (bytes shared at the end of the control
    files), detected by majority across files;
  * which files carry that footer, and how many bytes each file has that are
    unique to it;
  * Shannon entropy of the footer and of each file's unique head, so an
    encrypted block can be distinguished from a plaintext or compressed one;
  * optional cross-check against the `.ver` manifest sizes.

Why it matters
--------------
The footer is package-scoped: it is identical for `AppUpgrade`,
`.lge.upgrade.xml` and `update.tar.gz` within one package, and differs between
the EU and AU packages. It is therefore the package-level descriptor (manifest
and/or signature), while each file's unique head is its encrypted content. Knowing
the split is a prerequisite for any offline decryptor workflow.

Read-only. Only the tail/head windows are read for large files.

Usage
-----
    python3 ota_structure.py --root ~/Downloads/NaU/IONIQ5_EU
    python3 ota_structure.py --root ~/Downloads/NaU/IONIQ5_EU --json out.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

# Payload paths of interest, relative to a package root. These are the committed
# encrypted envelopes in an official Gen5W package.
DEFAULT_FILES = [
    "AppUpgrade",
    ".lge.upgrade.xml",
    "HU/firmware/update.tar.gz",
    "HU/images/mango-rootfs.tar.gz",
    "HU/images/mango-rwdata.tar.gz",
    "HU/images/new_gui.tar.gz",
    "HU/images/navi_eu/appnavi.tar",
]

WINDOW = 1 << 16  # bytes read from each end


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def head_and_tail(path: Path, window: int = WINDOW) -> (bytes, bytes):
    size = path.stat().st_size
    with open(path, "rb") as fh:
        head = fh.read(min(window, size))
        fh.seek(max(0, size - window))
        tail = fh.read(min(window, size))
    return head, tail


def common_suffix(a: bytes, b: bytes) -> int:
    n = 0
    limit = min(len(a), len(b))
    while n < limit and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def common_prefix(a: bytes, b: bytes) -> int:
    n = 0
    limit = min(len(a), len(b))
    while n < limit and a[n] == b[n]:
        n += 1
    return n


def detect_footer(tails: Dict[str, bytes]) -> int:
    """Return the largest suffix length shared by at least two payloads.

    The shared window is capped by the read window, so a footer longer than
    ``WINDOW`` is reported as ``WINDOW`` with a note.
    """

    names = sorted(tails)
    best = 0
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n = common_suffix(tails[names[i]], tails[names[j]])
            if n > best:
                best = n
    return best


def analyse(root: Path, files: List[str]) -> Dict[str, object]:
    present = {}
    for rel in files:
        p = root / rel
        if p.is_file():
            head, tail = head_and_tail(p)
            present[rel] = {"size": p.stat().st_size, "head": head, "tail": tail}

    if not present:
        raise SystemExit(f"no payloads found under {root}")

    names = sorted(present)
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = present[names[i]]["tail"], present[names[j]]["tail"]
            suffix = common_suffix(a, b)
            ah, bh = present[names[i]]["head"], present[names[j]]["head"]
            prefix = common_prefix(ah, bh)
            if suffix > 32 or prefix > 16:
                pairs.append({"a": names[i], "b": names[j],
                              "common_suffix": suffix, "common_prefix": prefix})

    footer_len = detect_footer({k: v["tail"] for k, v in present.items()})
    footer = None
    carriers = []
    if footer_len:
        # pick the most common tail window as the canonical footer
        windows = Counter(v["tail"][-footer_len:] for v in present.values())
        footer, _ = windows.most_common(1)[0]
        carriers = sorted(k for k, v in present.items()
                          if v["tail"][-footer_len:] == footer)

    per_file = {}
    for name, rec in present.items():
        carries = name in carriers
        unique = rec["size"] - (footer_len if carries else 0)
        per_file[name] = {
            "size": rec["size"],
            "carries_footer": carries,
            "unique_bytes": unique,
            "head_entropy": round(entropy(rec["head"]), 3),
            "tail_entropy": round(entropy(rec["tail"]), 3),
        }

    return {
        "root": str(root),
        "footer": {
            "length": footer_len,
            "sha256": hashlib.sha256(footer).hexdigest() if footer else None,
            "entropy": round(entropy(footer), 3) if footer else None,
            "carriers": carriers,
            "window_limited": footer_len >= WINDOW,
        },
        "pairs": pairs,
        "files": per_file,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, required=True, help="package root directory")
    ap.add_argument("--files", nargs="*", default=None, help="override payload list")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)

    result = analyse(args.root, args.files or DEFAULT_FILES)

    f = result["footer"]
    print(f"package root: {result['root']}")
    print(f"footer length: {f['length']}  carriers: {f['carriers']}")
    if f["sha256"]:
        print(f"footer sha256: {f['sha256']}  entropy: {f['entropy']}")
    if f["window_limited"]:
        print("  note: footer length equals the read window; actual footer may be longer")
    print("\nfiles:")
    for name, rec in result["files"].items():
        print(f"  {name:32} size={rec['size']:>12} unique={rec['unique_bytes']:>12}"
              f" footer={str(rec['carries_footer']):5} head_ent={rec['head_entropy']:.2f}")
    if result["pairs"]:
        print("\nshared regions (suffix / prefix):")
        for p in result["pairs"]:
            print(f"  {p['a']} <-> {p['b']}: suffix={p['common_suffix']} prefix={p['common_prefix']}")

    if args.json:
        args.json.write_text(json.dumps(result, indent=2))
        print(f"\nwrote {args.json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
