"""Tests for the ledger CSV exporter."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "ledger_export.py"
SPEC = importlib.util.spec_from_file_location("ledger_export", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

LEDGER = {
    "requirements": [
        {"id": "R1", "text": "first  requirement", "source": "objective"},
        {"id": "R2", "text": "second", "source": "objective"},
    ],
    "tasks": [
        {"id": "T1", "type": "research", "state": "accepted",
         "owner": {"actor": "w1", "model": "m"}, "depends_on": [],
         "requirements": ["R1", "R2"], "acceptance": [{"id": "A1"}], "evidence": [{"id": "E1"}]},
        {"id": "T2", "type": "integration", "state": "draft",
         "owner": {"actor": "w2", "model": "m"}, "depends_on": ["T1"],
         "requirements": ["R1"], "acceptance": [], "evidence": []},
    ],
    "artifacts": [
        {"id": "ART-T1", "task_id": "T1", "path": "a.md", "sha256": "aa", "kind": "note"},
        {"id": "ART-T1B", "task_id": "T1", "path": "b.txt", "sha256": "bb", "kind": "inv"},
    ],
}


class LedgerExportTests(unittest.TestCase):
    def test_one_row_per_task_artifact_pair(self) -> None:
        rows = MODULE.workflow_rows(LEDGER)
        self.assertEqual(len(rows), 3)  # T1 twice, T2 once
        self.assertEqual([r["task_id"] for r in rows], ["T1", "T1", "T2"])

    def test_task_without_artifact_still_appears(self) -> None:
        rows = MODULE.workflow_rows(LEDGER)
        t2 = [r for r in rows if r["task_id"] == "T2"][0]
        self.assertEqual(t2["artifact_id"], "")
        self.assertEqual(t2["state"], "draft")

    def test_joins_and_counts(self) -> None:
        rows = MODULE.workflow_rows(LEDGER)
        self.assertEqual(rows[0]["requirement_ids"], "R1;R2")
        self.assertEqual(rows[0]["acceptance_count"], "1")
        self.assertEqual(rows[0]["evidence_count"], "1")
        self.assertEqual(rows[2]["depends_on"], "T1")

    def test_requirements_whitespace_collapsed(self) -> None:
        rows = MODULE.requirement_rows(LEDGER)
        self.assertEqual(rows[0]["text"], "first requirement")
        self.assertEqual(rows[0]["cited_by_tasks"], "T1;T2")

    def test_export_is_byte_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "ledger.json"
            ledger.write_text(json.dumps(LEDGER))
            out = Path(temp) / "out"
            MODULE.main(["--ledger", str(ledger), "--outdir", str(out)])
            first = {p.name: p.read_bytes() for p in out.iterdir()}
            MODULE.main(["--ledger", str(ledger), "--outdir", str(out)])
            second = {p.name: p.read_bytes() for p in out.iterdir()}
            rc = MODULE.main(["--ledger", str(ledger), "--outdir", str(out), "--check"])
        self.assertEqual(first, second)
        self.assertEqual(rc, 0)
        self.assertEqual(len(first), 2)


if __name__ == "__main__":
    unittest.main()
