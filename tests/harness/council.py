"""Council checker wrapper that separates frozen-package defects from history.

A historical non-``COMPLETE`` outcome is reportable state: the record simply
says the panel never finished. It only becomes a harness failure when the
packet is unusable, the frozen bytes cannot be verified, an artifact path is
unsafe, or the declared fingerprint does not match the packet contents.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from . import common

DEFAULT_CHECKER = str(Path.home() / ".codex/skills/the-council/scripts/council.py")

# Problem codes that mean the record or its frozen bytes cannot be trusted.
# Historical review state (missing verdicts, unrun checks, open findings) is
# deliberately absent: it is reported, not treated as a harness defect.
HARD_PROBLEM_CODES = frozenset(
    {
        "artifact_path_unsafe",
        "artifact_unreadable",
        "artifact_missing",
        "artifact_hash_mismatch",
        "artifact_hash_format",
        "artifact_duplicate_path",
        "artifact_shape",
        "artifacts_unverified",
        "fingerprint_mismatch",
        "package_shape",
        "task_manifest_missing",
    }
)


def council_checker_path(env: dict | None = None) -> str:
    """Resolve the Council checker script, honouring an env override."""
    source = os.environ if env is None else env
    return source.get("IONIQ_COUNCIL_CHECKER") or DEFAULT_CHECKER


def council_package_dirs(root: Path) -> list[Path]:
    """Return ``council/review-batch-*`` directories in natural order."""
    council_root = Path(root) / "council"
    if not council_root.is_dir():
        return []
    return sorted(
        (
            path
            for path in council_root.iterdir()
            if path.is_dir() and path.name.startswith("review-batch-")
        ),
        key=lambda item: common.common_natural_key(item.name),
    )


def council_problem_codes(problems: list[str]) -> dict[str, int]:
    """Count problem-code prefixes such as ``artifact_path_unsafe``."""
    counts: dict[str, int] = {}
    for problem in problems:
        code = str(problem).split(":", 1)[0].strip()
        counts[code] = counts.get(code, 0) + 1
    return dict(sorted(counts.items()))


def council_check_packages(
    root: Path,
    *,
    checker_path: str | Path | None = None,
    runner=None,
) -> dict:
    """Run the checker CLI against every frozen council package with a packet."""
    root = Path(root)
    checker = Path(checker_path or council_checker_path())
    if not checker.is_file():
        raise common.HarnessError(f"council checker not found: {checker}")
    run = runner or common.common_run
    records: list[dict] = []
    skipped: list[dict] = []
    failures = 0
    complete = 0

    for directory in council_package_dirs(root):
        relative = common.common_relative(root, directory)
        packet_path = directory / "council-packet.json"
        if not packet_path.is_file():
            skipped.append({"package": relative, "reason": "no council-packet.json"})
            continue
        argv = [
            sys.executable,
            str(checker),
            str(packet_path),
            "--json",
            "--package-dir",
            str(directory),
        ]
        outcome = run(argv)
        record = {
            "package": relative,
            "status": common.STATUS_FAIL,
            "outcome": None,
            "package_verified": None,
            "fingerprint": None,
            "reviewer_verdicts": {},
            "problem_codes": {},
            "problems": [],
            "summary": "",
        }
        if outcome.get("error"):
            record["summary"] = f"checker could not run: {outcome['error']}"
            failures += 1
            records.append(record)
            continue
        exit_status = outcome.get("exit_status")
        if exit_status == 2:
            record["summary"] = "unusable packet (checker exit 2)"
            record["stderr_tail"] = (outcome.get("stderr") or "").strip()[-400:]
            failures += 1
            records.append(record)
            continue
        stdout = (outcome.get("stdout") or "").strip()
        try:
            report = json.loads(stdout) if stdout else None
        except json.JSONDecodeError:
            report = None
        if not isinstance(report, dict):
            record["summary"] = "checker output was not a JSON report"
            failures += 1
            records.append(record)
            continue
        problems = [str(item) for item in (report.get("problems") or [])]
        codes = council_problem_codes(problems)
        hard = {code: count for code, count in codes.items() if code in HARD_PROBLEM_CODES}
        record.update(
            {
                "outcome": report.get("outcome"),
                "package_verified": report.get("package_verified"),
                "fingerprint": report.get("package_fingerprint"),
                "reviewer_verdicts": dict(report.get("reviewer_verdicts") or {}),
                "problem_codes": codes,
                "problems": problems[:40],
                "problem_total": len(problems),
                "exit_status": exit_status,
            }
        )
        if hard:
            record["summary"] = (
                "frozen package defective: "
                + ", ".join(f"{code} x{count}" for code, count in hard.items())
            )
            record["hard_problem_codes"] = hard
            failures += 1
        elif report.get("package_verified") is not True:
            record["summary"] = "frozen artifact bytes were not verified"
            failures += 1
        elif report.get("outcome") == "COMPLETE":
            record["status"] = common.STATUS_PASS
            record["summary"] = "COMPLETE with verified artifacts"
            complete += 1
        else:
            record["status"] = common.STATUS_INFO
            record["summary"] = (
                f"historical outcome {report.get('outcome')} "
                "(artifacts verified; review record incomplete)"
            )
        records.append(record)

    details = {
        "packages": records,
        "skipped": skipped,
        "package_count": len(records),
        "complete_count": complete,
        "failure_count": failures,
    }
    if failures:
        return common.common_result(
            "council",
            common.STATUS_FAIL,
            f"{failures} council package(s) failed integrity checks",
            details,
        )
    if complete:
        return common.common_result(
            "council",
            common.STATUS_PASS,
            f"{complete}/{len(records)} council package(s) COMPLETE with verified artifacts",
            details,
        )
    return common.common_result(
        "council",
        common.STATUS_INFO,
        (
            f"{len(records)} frozen package(s) verified; no COMPLETE review recorded yet"
            if records
            else "no frozen council packages found"
        ),
        details,
    )

