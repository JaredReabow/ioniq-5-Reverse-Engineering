"""Top-level read-only runner for the Ioniq 5 research validation harness.

Usage:
    python3 tests/run_all.py              # human-readable report
    python3 tests/run_all.py --json       # deterministic JSON report
    python3 tests/run_all.py --only json  # run a subset by check name

Exit codes: 0 when every check passes (pending/info are allowed), 1 when a
validation check fails or an Ioniq push is blocked, 2 when the harness itself
cannot run (missing tool, bad root, unexpected error).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from harness import artifacts, common, council, docs, gitscope, jsoncheck, ledger, privacy  # noqa: E402

CHECK_NAMES = ("ledger", "artifacts", "json", "council", "privacy", "docs", "gitscope")


def runner_collect(
    root: Path,
    *,
    only: list[str] | None = None,
    workflow_path: str | Path | None = None,
    checker_path: str | Path | None = None,
    command_runner=None,
    git_runner=None,
) -> dict:
    """Run the selected checks and aggregate a deterministic report."""
    root = Path(root)
    if not root.is_dir():
        raise common.HarnessError(f"project root does not exist: {root}")
    selected = [name for name in CHECK_NAMES if not only or name in only]
    unknown = sorted(set(only or []) - set(CHECK_NAMES))
    if unknown:
        raise common.HarnessError(f"unknown check name(s): {', '.join(unknown)}")
    ledger_path = root / "research-ledger.json"
    public_mode = (root / "PUBLIC-RELEASE.md").is_file()

    def run_check(name: str) -> dict:
        if public_mode and name in ("ledger", "artifacts", "council"):
            return common.common_result(name, common.STATUS_INFO, "private source records omitted from public snapshot", {})
        if public_mode and name == "json":
            if (root / ".git").exists():
                paths = subprocess.check_output(
                    ["git", "-C", str(root), "ls-files", "-z", "--cached"]
                ).decode("utf-8").split("\0")
                records = [root / path for path in paths if path.endswith(".json")]
            else:
                records = [p for p in root.rglob("*.json") if ".git" not in p.parts]
            invalid = []
            for path in records:
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError):
                    invalid.append(str(path.relative_to(root)))
            return common.common_result(
                name,
                common.STATUS_FAIL if invalid else common.STATUS_PASS,
                f"{len(records)} public JSON record(s) checked; {len(invalid)} invalid",
                {"invalid": invalid},
            )
        if public_mode and name == "docs":
            present = all((root / p).is_file() for p in ("Ioniq5-HISTORY.md", "Ioniq5-CHANGELOG.md"))
            return common.common_result(name, common.STATUS_PASS if present else common.STATUS_FAIL, "IONIQ history and changelog present" if present else "IONIQ history or changelog missing", {})
        if name == "ledger":
            return ledger.ledger_validate(
                ledger_path, workflow_path=workflow_path, runner=command_runner
            )
        if name == "artifacts":
            return artifacts.artifacts_check(ledger_path, root)
        if name == "json":
            return jsoncheck.jsoncheck_scan(root)
        if name == "council":
            return council.council_check_packages(
                root, checker_path=checker_path, runner=command_runner
            )
        if name == "privacy":
            return privacy.privacy_scan(root)
        if name == "docs":
            return docs.docs_check(ledger_path, root)
        if name == "gitscope":
            return gitscope.gitscope_check(root, runner=git_runner)
        raise common.HarnessError(f"unknown check name: {name}")

    results: list[dict] = []
    internal_errors: list[str] = []
    for name in selected:
        try:
            results.append(run_check(name))
        except common.HarnessError as exc:
            internal_errors.append(name)
            results.append(
                common.common_result(
                    name,
                    common.STATUS_FAIL,
                    f"harness error: {exc}",
                    {"harness_error": str(exc)},
                )
            )
        except Exception as exc:  # unexpected defect in the harness itself
            internal_errors.append(name)
            results.append(
                common.common_result(
                    name,
                    common.STATUS_FAIL,
                    f"harness error: {type(exc).__name__}",
                    {"harness_error": f"{type(exc).__name__}: {exc}"},
                )
            )

    counts = {status: 0 for status in common.STATUS_ORDER}
    for result in results:
        counts[result["status"]] += 1
    if internal_errors:
        overall, exit_code = "fail", 2
    elif counts[common.STATUS_FAIL]:
        overall, exit_code = "fail", 1
    elif counts[common.STATUS_BLOCKED]:
        overall, exit_code = "blocked", 1
    else:
        overall, exit_code = "pass", 0
    return {
        "schema_version": 1,
        "root": str(root.resolve()),
        "overall": overall,
        "exit_code": exit_code,
        "internal_errors": internal_errors,
        "counts": counts,
        "checks": results,
    }


def runner_render_json(report: dict) -> str:
    """Render the report as stable, sorted JSON with a trailing newline."""
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def runner_render_text(report: dict) -> str:
    """Render the same report for humans."""
    lines = [
        "Ioniq 5 research harness",
        f"root: {report['root']}",
        "",
    ]
    for result in report["checks"]:
        lines.append(f"{result['status'].upper():7s} {result['check']:9s} {result['summary']}")
        for entry in result["details"].get("entries", []):
            if entry.get("state") != "ok":
                lines.append(
                    f"        {entry.get('path')}: {entry.get('state')}"
                )
        for package in result["details"].get("packages", []):
            if package.get("status") in (common.STATUS_FAIL, common.STATUS_INFO):
                lines.append(f"        {package['package']}: {package['summary']}")
        for reason in result["details"].get("reasons", []):
            lines.append(f"        {reason['code']}: {reason['message']}")
    counts = report["counts"]
    lines.extend(
        [
            "",
            "summary: "
            + " ".join(f"{name}={counts[name]}" for name in common.STATUS_ORDER),
            f"result: {report['overall'].upper()} (exit {report['exit_code']})",
        ]
    )
    if report["internal_errors"]:
        lines.append("internal errors: " + ", ".join(report["internal_errors"]))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the checks, and return the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=str(HERE.parent),
        help="project root containing research-ledger.json (default: repository root)",
    )
    parser.add_argument("--json", action="store_true", help="emit deterministic JSON")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="run only these checks (repeatable or comma-separated)",
    )
    parser.add_argument(
        "--workflow",
        default=None,
        help="override the Parallelism workflow.py validator path",
    )
    parser.add_argument(
        "--checker",
        default=None,
        help="override the Council council.py checker path",
    )
    parser.add_argument("--list", action="store_true", help="list check names and exit")
    args = parser.parse_args(argv)
    if args.list:
        print("\n".join(CHECK_NAMES))
        return 0
    only: list[str] = []
    for item in args.only:
        only.extend(part.strip() for part in item.split(",") if part.strip())
    try:
        report = runner_collect(
            Path(args.root),
            only=only or None,
            workflow_path=args.workflow,
            checker_path=args.checker,
        )
    except common.HarnessError as exc:
        print(f"harness error: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(
        runner_render_json(report) if args.json else runner_render_text(report)
    )
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())

