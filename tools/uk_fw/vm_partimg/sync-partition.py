#!/usr/bin/env python3.13
"""Copy only the *changed* blocks of a partition file back into a GPT disk image.

Used to inject files into p5 of the 36 GiB partitioned image without rewriting
the whole 8 GiB partition.  The host APFS volume is nearly full, and a CoW
clone allocates new blocks on every write even when the bytes are unchanged
(measured), so a full sparse_copy of p5 would need ~5 GiB of fresh blocks.
Instead we diff the freshly-injected p5.img against the p5 region already in
rootfs.img and write back only the 1 MiB chunks that differ.

Usage:
    python3.13 tools/uk_fw/vm_partimg/sync-partition.py work/vm/stockhmi [PARTITION]

After running it, prepare.json's sha256.rootfs.img is refreshed in place so the
workspace passes vm_boot.verify_workspace.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
CHUNK = 1024 * 1024


def main() -> int:
    ws = (PROJECT / sys.argv[1]).resolve() if len(sys.argv) > 1 else (PROJECT / "work/vm/stockhmi")
    part_num = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    layout = json.loads((ws / "layout.json").read_text())
    entry = next(x for x in layout if x["partition"] == part_num)
    offset = int(entry["byte_offset"])
    part = ws / "partimg-build" / f"p{part_num}.img"
    img = ws / "rootfs.img"

    total = part.stat().st_size
    written = 0
    changed = 0
    with part.open("rb") as fp, img.open("r+b") as fi:
        pos = 0
        while pos < total:
            a = fp.read(CHUNK)
            if not a:
                break
            fi.seek(offset + pos)
            b = fi.read(len(a))
            if a != b:
                fi.seek(offset + pos)
                fi.write(a)
                fi.flush()
                written += len(a)
                changed += 1
            pos += len(a)
    print(f"sync: partition p{part_num}: {changed} changed chunk(s), "
          f"{written} bytes written to rootfs.img at offset {offset}")

    prep = json.loads((ws / "prepare.json").read_text())
    prep.setdefault("sha256", {})
    prep["sha256"]["rootfs.img"] = hashlib.file_digest(
        (ws / "rootfs.img").open("rb"), "sha256").hexdigest()
    (ws / "prepare.json").write_text(json.dumps(prep, indent=2) + "\n")
    print("refreshed prepare.json sha256.rootfs.img")
    return 0


if __name__ == "__main__":
    sys.exit(main())
