#!/usr/bin/env python3
"""Parse and verify a Hyundai Gen5W ``.ver`` package manifest.

Format
------
Line 1 is the package header::

    +|21393|NE_E.EUR.S5W_L.001.001.260128|HM|IONIQ5_EU|101489|1

Each following line describes one payload::

    <windows-path>|<filename>|<record-id>|<signed-crc32>|<size>|<flag>

``<signed-crc32>`` is a signed 32-bit value; interpreted as unsigned it equals
``zlib.crc32`` of the file's bytes. ``<windows-path>`` uses backslashes and
begins with the package name.

Verification
------------
``verify`` walks every record, hashes the file, and compares size and CRC-32.
Files larger than ``--skip-over`` MiB are skipped by default because the EU map
archive is 17 GB; pass ``--all`` to include everything.

Read-only: inputs are opened for reading only.

Usage
-----
    python3 ver_manifest.py parse  IONIQ5_EU.ver
    python3 ver_manifest.py verify IONIQ5_EU.ver --root ~/Downloads/NaU/IONIQ5_EU
    python3 ver_manifest.py verify IONIQ5_EU.ver --root ... --json out.json
"""

from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path
from typing import Dict, List, Optional


def parse(path: Path) -> Dict[str, object]:
    lines = [l for l in path.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    if not lines:
        raise SystemExit(f"{path} is empty")
    header = lines[0]
    parts = header.split("|")
    if len(parts) < 6 or parts[0] != "+":
        raise SystemExit(f"unexpected manifest header: {header[:80]!r}")
    package = {
        "record_count_field": parts[1],
        "version": parts[2],
        "brand": parts[3],
        "package_id": parts[4],
        "model_code": parts[5],
    }
    records: List[Dict[str, object]] = []
    for line in lines[1:]:
        f = line.split("|")
        if len(f) < 6:
            continue
        win_path, name, record_id, crc, size, flag = f[:6]
        rel = win_path.replace("\\", "/")
        # strip the leading package directory so records resolve under --root
        if rel == package["package_id"]:
            rel = ""
        elif rel.startswith(package["package_id"] + "/"):
            rel = rel[len(package["package_id"]) + 1:]
        elif "/" in rel:
            rel = rel.split("/", 1)[1]
        records.append(
            {
                "path": (rel + "/" + name) if rel else name,
                "record_id": int(record_id),
                "crc32_signed": int(crc),
                "crc32": int(crc) & 0xFFFFFFFF,
                "size": int(size),
                "flag": int(flag),
            }
        )
    return {"manifest": str(path), "package": package, "records": records}


def crc_file(path: Path, chunk: int = 1 << 20) -> (int, int):
    crc = 0
    total = 0
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            crc = zlib.crc32(block, crc)
            total += len(block)
    return crc & 0xFFFFFFFF, total


def verify(parsed: Dict[str, object], root: Path, skip_over: int, include_all: bool) -> Dict[str, object]:
    limit = None if include_all else skip_over * 1024 * 1024
    results = []
    ok = skipped = bad = missing = 0
    for rec in parsed["records"]:  # type: ignore[index]
        rel = rec["path"]
        target = root / rel
        entry = {"path": rel, "expected_size": rec["size"], "expected_crc32": f"0x{rec['crc32']:08x}"}
        if not target.is_file():
            entry["status"] = "missing"
            missing += 1
            results.append(entry)
            continue
        actual_size = target.stat().st_size
        if limit is not None and actual_size > limit:
            entry["status"] = "skipped-large"
            entry["actual_size"] = actual_size
            skipped += 1
            results.append(entry)
            continue
        crc, size = crc_file(target)
        entry["actual_size"] = size
        entry["actual_crc32"] = f"0x{crc:08x}"
        good = size == rec["size"] and crc == rec["crc32"]
        entry["status"] = "ok" if good else "mismatch"
        if good:
            ok += 1
        else:
            bad += 1
        results.append(entry)
    return {
        "root": str(root),
        "summary": {"ok": ok, "mismatch": bad, "missing": missing, "skipped_large": skipped,
                    "total": len(results)},
        "records": results,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_parse = sub.add_parser("parse", help="print the manifest as JSON")
    p_parse.add_argument("manifest", type=Path)
    p_ver = sub.add_parser("verify", help="check sizes and CRC-32 against files on disk")
    p_ver.add_argument("manifest", type=Path)
    p_ver.add_argument("--root", type=Path, required=True)
    p_ver.add_argument("--skip-over", type=int, default=2048, help="MiB limit (default 2048)")
    p_ver.add_argument("--all", action="store_true", help="include large files")
    p_ver.add_argument("--json", type=Path)
    args = ap.parse_args(argv)

    parsed = parse(args.manifest)
    if args.cmd == "parse":
        print(json.dumps(parsed, indent=2))
        return 0

    result = verify(parsed, args.root, args.skip_over, args.all)
    for rec in result["records"]:
        status = rec["status"]
        if status == "ok":
            continue
        print(f"  {status:14} {rec['path']}"
              + (f"  expected={rec['expected_size']}/{rec['expected_crc32']}"
                 f" actual={rec.get('actual_size')}/{rec.get('actual_crc32')}"
                 if status == "mismatch" else ""))
    s = result["summary"]
    print(f"package {parsed['package']['version']}  "
          f"ok={s['ok']} mismatch={s['mismatch']} missing={s['missing']} "
          f"skipped_large={s['skipped_large']} total={s['total']}")
    if args.json:
        args.json.write_text(json.dumps(result, indent=2))
        print(f"wrote {args.json}", file=sys.stderr)
    return 0 if s["mismatch"] == 0 and s["missing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
