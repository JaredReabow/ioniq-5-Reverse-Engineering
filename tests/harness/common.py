"""Shared result shapes and process helpers for the Ioniq 5 research harness.

The harness is read-only: helpers here only read files, hash bytes, and invoke
the existing validator/checker CLIs. Every check returns one plain dict so the
top-level runner can aggregate state deterministically and tests can assert on
structured output instead of rendered text.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

STATUS_PASS = "pass"
STATUS_INFO = "info"
STATUS_PENDING = "pending"
STATUS_BLOCKED = "blocked"
STATUS_FAIL = "fail"

STATUS_ORDER = (
    STATUS_PASS,
    STATUS_INFO,
    STATUS_PENDING,
    STATUS_BLOCKED,
    STATUS_FAIL,
)

# ``blocked`` is a real failure for exit-code purposes (an Ioniq push must not
# proceed), but it stays a distinct label so a push gate is never mistaken for
# a research-evidence defect.
FAILING_STATUSES = frozenset({STATUS_BLOCKED, STATUS_FAIL})


class HarnessError(RuntimeError):
    """Raised when a check cannot run at all: missing tool, bad root, no Python."""


def common_result(check: str, status: str, summary: str, details: dict | None = None) -> dict:
    """Build one normalised check result."""
    if status not in STATUS_ORDER:
        raise ValueError(f"unknown status {status!r}")
    return {
        "check": check,
        "status": status,
        "summary": summary,
        "details": details or {},
    }


def common_sha256(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file's bytes."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def common_natural_key(text: str) -> tuple:
    """Sort key ordering ``review-batch-2`` before ``review-batch-10``."""
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", text)
    )


def common_relative(root: Path, path: Path) -> str:
    """Return ``path`` relative to ``root`` when possible, else as given."""
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except (OSError, ValueError):
        return Path(path).as_posix()


def common_run(argv: list[str], cwd: Path | None = None, timeout: int = 300) -> dict:
    """Run a read-only command and capture its result without raising.

    Returns ``exit_status=None`` plus an ``error`` string when the process could
    not be started or timed out, so callers never need to catch exceptions.
    """
    try:
        completed = subprocess.run(
            [str(part) for part in argv],
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "argv": [str(part) for part in argv],
            "exit_status": None,
            "stdout": "",
            "stderr": "",
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {
        "argv": [str(part) for part in argv],
        "exit_status": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "error": None,
    }


def common_read_json(path: Path) -> tuple[object | None, str | None]:
    """Return ``(document, error)`` for a JSON file without raising."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"unreadable: {exc.strerror or type(exc).__name__}"
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        # The decoder reports position only; document content is never echoed.
        return None, f"invalid JSON at line {exc.lineno}, column {exc.colno}"

