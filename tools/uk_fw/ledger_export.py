#!/usr/bin/env python3
"""Export the research ledger as flat, diffable CSV.

The ledger is a nested JSON document (tasks, acceptance criteria, evidence,
artifacts, requirements). That is correct for governance but poor for review: you
cannot sort it, diff it, or read it in a spreadsheet.

This produces two normalised tables:

  workflow-normalized.csv      one row per (task, artifact) pair; tasks with no
                               artifact still get a row so nothing is dropped
  requirements-normalized.csv  one row per requirement, with the tasks that cite it

Output is deterministic: tasks in ledger order, artifacts in ledger order, no
timestamps. Re-running on an unchanged ledger produces byte-identical files.

Ordering constraint
-------------------
The exports embed artifact hashes, including the changelog hash. Any edit to a
tracked artifact (notably the changelog) changes the ledger and therefore this
output. Regenerate **after** the ledger is final:

    1. edit artifact (changelog, evidence, ...)
    2. re-stamp the ledger
    3. python3 ledger_export.py --ledger research-ledger.json --outdir .
    4. python3 ledger_export.py --check      # must pass before committing

``--check`` exists precisely to catch a stale export.

Read-only with respect to the ledger.

Usage
-----
    python3 ledger_export.py --ledger research-ledger.json --outdir .
    python3 ledger_export.py --ledger research-ledger.json --outdir /tmp --check
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

WORKFLOW_COLUMNS = [
    "task_id", "task_type", "state", "owner_actor", "owner_model",
    "depends_on", "requirement_ids", "acceptance_count", "evidence_count",
    "artifact_id", "artifact_kind", "artifact_path", "artifact_sha256",
]

REQUIREMENT_COLUMNS = [
    "requirement_id", "source", "cited_by_tasks", "text",
]


def _join(values) -> str:
    if not values:
        return ""
    if isinstance(values, str):
        return values
    return ";".join(str(v) for v in values)


def load(path: Path) -> Dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def workflow_rows(ledger: Dict) -> List[Dict[str, str]]:
    artifacts_by_task: Dict[str, List[Dict]] = {}
    for art in ledger.get("artifacts", []):
        artifacts_by_task.setdefault(art.get("task_id", ""), []).append(art)

    rows: List[Dict[str, str]] = []
    for task in ledger.get("tasks", []):
        owner = task.get("owner") or {}
        base = {
            "task_id": task.get("id", ""),
            "task_type": task.get("type", ""),
            "state": task.get("state", ""),
            "owner_actor": owner.get("actor", ""),
            "owner_model": owner.get("model", ""),
            "depends_on": _join(task.get("depends_on")),
            "requirement_ids": _join(task.get("requirements")),
            "acceptance_count": str(len(task.get("acceptance") or [])),
            "evidence_count": str(len(task.get("evidence") or [])),
        }
        arts = artifacts_by_task.get(task.get("id", ""))
        if not arts:
            rows.append({**base, "artifact_id": "", "artifact_kind": "",
                         "artifact_path": "", "artifact_sha256": ""})
            continue
        for art in arts:
            rows.append({
                **base,
                "artifact_id": art.get("id", ""),
                "artifact_kind": art.get("kind", ""),
                "artifact_path": art.get("path", ""),
                "artifact_sha256": art.get("sha256", ""),
            })
    return rows


def requirement_rows(ledger: Dict) -> List[Dict[str, str]]:
    cited: Dict[str, List[str]] = {}
    for task in ledger.get("tasks", []):
        for rid in task.get("requirements") or []:
            cited.setdefault(rid, []).append(task.get("id", ""))
    rows = []
    for req in ledger.get("requirements", []):
        rid = req.get("id", "")
        rows.append({
            "requirement_id": rid,
            "source": req.get("source", ""),
            "cited_by_tasks": _join(cited.get(rid, [])),
            "text": " ".join(str(req.get("text", "")).split()),
        })
    return rows


def write_csv(path: Path, columns: List[str], rows: List[Dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", type=Path, default=Path("research-ledger.json"))
    ap.add_argument("--outdir", type=Path, default=Path("."))
    ap.add_argument("--check", action="store_true",
                    help="compare with existing files instead of overwriting")
    args = ap.parse_args(argv)

    ledger = load(args.ledger)
    args.outdir.mkdir(parents=True, exist_ok=True)
    wf_path = args.outdir / "workflow-normalized.csv"
    rq_path = args.outdir / "requirements-normalized.csv"

    wf_rows = workflow_rows(ledger)
    rq_rows = requirement_rows(ledger)

    if args.check:
        import io
        problems = []
        for path, columns, rows in ((wf_path, WORKFLOW_COLUMNS, wf_rows),
                                    (rq_path, REQUIREMENT_COLUMNS, rq_rows)):
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
            expected = buf.getvalue()
            if not path.is_file():
                problems.append(f"{path} is missing")
            elif path.read_text(encoding="utf-8") != expected:
                problems.append(f"{path} is out of date")
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        if not problems:
            print("  exports are up to date")
        return 1 if problems else 0

    write_csv(wf_path, WORKFLOW_COLUMNS, wf_rows)
    write_csv(rq_path, REQUIREMENT_COLUMNS, rq_rows)
    print(f"{wf_path}: {len(wf_rows)} rows")
    print(f"{rq_path}: {len(rq_rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
