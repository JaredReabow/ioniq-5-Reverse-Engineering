"""Ledger validation through the existing Parallelism ``workflow.py`` CLI."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from . import common

DEFAULT_WORKFLOW = str(Path.home() / ".codex/skills/parallelism/scripts/workflow.py")


def ledger_workflow_path(env: dict | None = None) -> str:
    """Resolve the validator script path, honouring an env override."""
    source = os.environ if env is None else env
    return source.get("IONIQ_WORKFLOW_VALIDATOR") or DEFAULT_WORKFLOW


def ledger_validate(
    ledger_path: Path,
    *,
    workflow_path: str | Path | None = None,
    runner=None,
) -> dict:
    """Run ``workflow.py validate --json`` and classify its report.

    Exit 0 with an ``ok`` body passes; warnings downgrade to ``info`` so they
    stay visible without failing a planning-mode ledger. Exit 1, exit 2, or
    unparsable output is a validation failure.
    """
    ledger_path = Path(ledger_path)
    workflow = Path(workflow_path or ledger_workflow_path())
    if not workflow.is_file():
        raise common.HarnessError(f"ledger validator not found: {workflow}")
    run = runner or common.common_run
    argv = [
        sys.executable,
        str(workflow),
        "validate",
        "--ledger",
        str(ledger_path),
        "--json",
    ]
    outcome = run(argv)
    details = {
        "command": argv,
        "exit_status": outcome.get("exit_status"),
        "ok": None,
        "errors": [],
        "warnings": [],
    }
    if outcome.get("error"):
        return common.common_result(
            "ledger",
            common.STATUS_FAIL,
            f"validator could not run: {outcome['error']}",
            details,
        )
    stdout = (outcome.get("stdout") or "").strip()
    try:
        report = json.loads(stdout) if stdout else None
    except json.JSONDecodeError:
        report = None
    if not isinstance(report, dict):
        details["stderr_tail"] = (outcome.get("stderr") or "").strip()[-400:]
        return common.common_result(
            "ledger",
            common.STATUS_FAIL,
            "validator output was not a JSON report",
            details,
        )
    errors = list(report.get("errors") or [])
    warnings = list(report.get("warnings") or [])
    details.update(
        {
            "ok": bool(report.get("ok")),
            "errors": errors[:50],
            "warnings": warnings[:50],
            "error_count": len(errors),
            "warning_count": len(warnings),
        }
    )
    status_code = outcome.get("exit_status")
    if status_code == 2:
        return common.common_result(
            "ledger", common.STATUS_FAIL, "validator rejected the ledger as unusable", details
        )
    if status_code != 0 or not report.get("ok") or errors:
        return common.common_result(
            "ledger",
            common.STATUS_FAIL,
            f"ledger invalid ({len(errors)} error(s), {len(warnings)} warning(s))",
            details,
        )
    if warnings:
        return common.common_result(
            "ledger",
            common.STATUS_INFO,
            f"ledger valid with {len(warnings)} warning(s)",
            details,
        )
    return common.common_result("ledger", common.STATUS_PASS, "ledger valid", details)

