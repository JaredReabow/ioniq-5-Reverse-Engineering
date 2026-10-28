#!/usr/bin/env python3
"""Harness around the unit-derived OTA decryptor.

The Gen5W OTA payloads are AES-encrypted. The only public route to plaintext is
to run the unit's own decryptor on a PC with the key material extracted from the
unit (`DecryptToPIPE` plus `decryption_key.der`). This tool does not implement or
break any cipher; it orchestrates that external binary, models the container
layout, and validates what comes back.

Container model and the documented invocation
---------------------------------------------
Each package appends a package-scoped **footer** (14,059 bytes for EU `260128`,
14,315 bytes for AU `260319`) to `AppUpgrade`, `.lge.upgrade.xml` and
`update.tar.gz`. The footer is detected here for *reporting only*: the vendor
decryptor consumes the whole file and parses the container itself, so nothing is
stripped before decryption.

The documented invocation, taken from the public `update_decryptor`
`entrypoint.sh`, is:

    DecryptToPIPE -d <keyfile> <input> 0 > <output>

i.e. decrypt, key file, input path, a numeric mode, output on stdout. That is the
default template below; override it with ``--template`` if your build differs.

Subcommands
-----------
    plan      show the exact external commands that would run (no execution)
    run       execute the decryptor for each payload and verify the outputs
    verify    check that a decrypted directory looks like real plaintext

The external command is supplied as a template so this tool makes no assumption
about the vendor binary's interface:

    --template 'DecryptToPipe --key {key} --in {input} --out {output}'

Placeholders: ``{input}``, ``{output}``, ``{key}``, ``{footer}``.

Safety: writes only under ``--out``; never modifies the package directory.
"""

from __future__ import annotations

import argparse
import json
import math
import shlex
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_FILES = [
    "AppUpgrade",
    ".lge.upgrade.xml",
    "HU/firmware/update.tar.gz",
    "HU/images/mango-rootfs.tar.gz",
    "HU/images/mango-rwdata.tar.gz",
    "HU/images/new_gui.tar.gz",
    "HU/images/navi_eu/appnavi.tar",
]
KNOWN_FOOTERS = {14059, 14315}


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def detect_footer_size(paths: List[Path]) -> int:
    """Largest trailing window shared by at least two payloads, capped at 64 KiB."""

    tails = {}
    for p in paths:
        with open(p, "rb") as fh:
            size = p.stat().st_size
            fh.seek(max(0, size - 65536))
            tails[p] = fh.read(65536)
    best = 0
    items = list(tails)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = tails[items[i]], tails[items[j]]
            n = 0
            limit = min(len(a), len(b))
            while n < limit and a[-1 - n] == b[-1 - n]:
                n += 1
            best = max(best, n)
    return best


def build_plan(root: Path, out: Path, files: List[str], template: str,
               key: Optional[Path]) -> Dict[str, object]:
    present = [root / rel for rel in files if (root / rel).is_file()]
    if not present:
        raise SystemExit(f"no payloads found under {root}")
    footer = detect_footer_size(present)
    footer_note = None
    if footer and footer not in KNOWN_FOOTERS:
        footer_note = (f"detected footer {footer} is not a known value "
                       f"({sorted(KNOWN_FOOTERS)}); treat it as provisional")
    plan = {
        "root": str(root),
        "out": str(out),
        "footer": footer,
        "footer_note": footer_note,
        "key": str(key) if key else None,
        "steps": [],
    }
    for src in present:
        rel = src.relative_to(root)
        dst = out / rel
        cmd = template.format(input=src, output=dst, key=key or "", footer=footer)
        plan["steps"].append({
            "input": str(src),
            "output": str(dst),
            "size": src.stat().st_size,
            "has_footer": footer > 0,
            "command": cmd,
        })
    return plan


def run_plan(plan: Dict[str, object], timeout: int) -> Dict[str, object]:
    out = Path(plan["out"])
    results = []
    for step in plan["steps"]:  # type: ignore[index]
        dst = Path(step["output"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        # The documented invocation redirects stdout, so run it through bash.
        record = {"input": step["input"], "output": step["output"], "command": step["command"]}
        try:
            proc = subprocess.run(["bash", "-c", step["command"]],
                                  capture_output=True, text=True, timeout=timeout)
            record["returncode"] = proc.returncode
            record["stderr"] = proc.stderr[-2000:]
            if dst.is_file():
                data = dst.read_bytes()
                record["output_size"] = len(data)
                record["output_entropy"] = round(entropy(data[:65536]), 3)
                record["looks_plaintext"] = is_plaintext(data[:65536])
        except FileNotFoundError:
            record["error"] = "decryptor binary not found"
        except subprocess.TimeoutExpired:
            record["error"] = f"timeout after {timeout}s"
        results.append(record)
    return {"steps": results}


def is_plaintext(sample: bytes) -> bool:
    if not sample:
        return False
    printable = sum(1 for b in sample if 9 <= b <= 13 or 32 <= b < 127)
    return printable / len(sample) > 0.85 and entropy(sample) < 6.0


def verify_dir(path: Path) -> Dict[str, object]:
    rows = []
    for p in sorted(path.rglob("*")):
        if not p.is_file():
            continue
        with open(p, "rb") as fh:
            sample = fh.read(65536)
        rows.append({
            "path": str(p.relative_to(path)),
            "size": p.stat().st_size,
            "entropy": round(entropy(sample), 3),
            "plaintext_like": is_plaintext(sample),
        })
    decompressed = sum(1 for r in rows if r["plaintext_like"])
    return {"root": str(path), "files": len(rows), "plaintext_like": decompressed, "rows": rows}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("plan", "run"):
        p = sub.add_parser(name)
        p.add_argument("--root", type=Path, required=True)
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--files", nargs="*", default=None)
        p.add_argument("--template",
                       default="DecryptToPIPE -d {key} {input} 0 > {output}",
                       help="external command template (run through bash)")
        p.add_argument("--key", type=Path, help="decryption_key.der")
        p.add_argument("--timeout", type=int, default=900)
        p.add_argument("--json", type=Path)

    p_ver = sub.add_parser("verify")
    p_ver.add_argument("path", type=Path)
    p_ver.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)

    if args.cmd == "verify":
        result = verify_dir(args.path)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for row in result["rows"]:
                flag = "plain" if row["plaintext_like"] else "binary/encrypted"
                print(f"  {row['path']:50} {row['size']:>12}  H={row['entropy']:.2f}  {flag}")
            print(f"{result['plaintext_like']}/{result['files']} look like plaintext")
        return 0

    plan = build_plan(args.root, args.out, args.files or DEFAULT_FILES,
                      args.template, args.key)
    if args.cmd == "plan":
        if args.json:
            args.json.write_text(json.dumps(plan, indent=2))
        print(json.dumps(plan, indent=2))
        return 0

    result = run_plan(plan, args.timeout)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2))
    failed = [r for r in result["steps"] if r.get("returncode") not in (0,)]
    for r in result["steps"]:
        state = r.get("error") or f"rc={r.get('returncode')}"
        extra = f" out={r.get('output_size')} H={r.get('output_entropy')}" if "output_size" in r else ""
        print(f"  {Path(r['input']).name:28} {state}{extra}")
    print(f"{len(result['steps']) - len(failed)}/{len(result['steps'])} succeeded")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
