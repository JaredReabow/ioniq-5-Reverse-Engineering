"""Ioniq HISTORY/CHANGELOG readiness, gated on the integration task state.

The repository root also holds the Kona project's ``HISTORY.md`` and
``CHANGELOG.md``. Those files belong to the Kona research programme, so they can
never satisfy Ioniq integration. This check therefore resolves a dedicated
Ioniq pair (``Ioniq5-HISTORY.md`` / ``Ioniq5-CHANGELOG.md`` by default, or an
explicit Ioniq-named path declared in ``T6.write_paths``) and reports the Kona
documents only as a rejected alias.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from . import common

INTEGRATION_TASK = "T6"
# Dedicated Ioniq documents used when the ledger does not name its own pair.
DEFAULT_DOCS = ("Ioniq5-HISTORY.md", "Ioniq5-CHANGELOG.md")
# Root documents owned by the parallel Kona programme; never acceptable proof.
KONA_OWNED_DOCS = ("HISTORY.md", "CHANGELOG.md")
KONA_OWNED_KEYS = frozenset(name.lower() for name in KONA_OWNED_DOCS)
# States that mean integration has actually started or finished.
ACTIVE_STATES = frozenset({"running", "ready_for_review", "accepted", "complete"})


def docs_doc_kind(path: str) -> str | None:
    """Return ``"history"``/``"changelog"`` for a Markdown doc path, else None."""
    name = PurePosixPath(path.replace("\\", "/")).name.lower()
    if not name.endswith(".md"):
        return None
    stem = name[: -len(".md")]
    if stem.endswith("history"):
        return "history"
    if stem.endswith("changelog"):
        return "changelog"
    return None


def docs_is_ioniq_named(path: str) -> bool:
    """True when a path is explicitly Ioniq-scoped rather than a shared root doc."""
    parts = PurePosixPath(path.replace("\\", "/")).parts
    if not parts:
        return False
    # A bare ``Ioniq5-HISTORY.md`` at the root is fine, and so is
    # ``ioniq5/HISTORY.md``. A shared root ``HISTORY.md`` is not, and neither is
    # anything outside the project.
    if PurePosixPath(path).is_absolute() or ".." in parts:
        return False
    return any(part.lower().startswith("ioniq") for part in parts)


def docs_select_required(
    write_paths: list[str] | None,
) -> tuple[dict[str, str], list[str], list[str]]:
    """Pick the dedicated Ioniq history/changelog pair.

    Returns ``({kind: path}, rejected, from_ledger)``. ``rejected`` lists
    declared root Kona documents that were refused; ``from_ledger`` lists the
    dedicated paths that actually came from the ledger rather than defaults.
    """
    selected: dict[str, str] = {}
    rejected: list[str] = []
    for raw in write_paths or []:
        if not isinstance(raw, str):
            continue
        kind = docs_doc_kind(raw)
        if kind is None:
            continue
        normalised = PurePosixPath(raw.replace("\\", "/")).as_posix()
        # Root Kona documents are recorded, but never adopted as Ioniq proof.
        if normalised.lower() in KONA_OWNED_KEYS:
            rejected.append(normalised)
            continue
        if not docs_is_ioniq_named(raw):
            continue
        selected.setdefault(kind, normalised)
    for default in DEFAULT_DOCS:
        kind = docs_doc_kind(default)
        selected.setdefault(kind, default)
    return selected, rejected, [path for path in selected.values() if path not in DEFAULT_DOCS]


def docs_check(ledger_path: Path, root: Path) -> dict:
    """Require a dedicated Ioniq history/changelog once T6 is no longer queued."""
    root = Path(root)
    document, error = common.common_read_json(Path(ledger_path))
    if error:
        return common.common_result(
            "docs", common.STATUS_FAIL, f"ledger unreadable: {error}", {"error": error}
        )
    tasks = document.get("tasks") if isinstance(document, dict) else None
    task = None
    if isinstance(tasks, list):
        task = next(
            (
                item
                for item in tasks
                if isinstance(item, dict) and item.get("id") == INTEGRATION_TASK
            ),
            None,
        )
    state = task.get("state") if isinstance(task, dict) else None
    write_paths = task.get("write_paths") if isinstance(task, dict) else None
    required, rejected, from_ledger = docs_select_required(
        write_paths if isinstance(write_paths, list) else []
    )
    present = {name: (root / name).is_file() for name in required.values()}
    missing = [name for name, exists in present.items() if not exists]
    # A symlink is not a dedicated document when it resolves to the Kona file.
    kona_resolved = {
        name: (root / name).resolve() for name in KONA_OWNED_DOCS
    }
    aliased = [
        name
        for name in required.values()
        if (root / name).is_file()
        and (root / name).resolve() in kona_resolved.values()
    ]
    details = {
        "integration_task": INTEGRATION_TASK,
        "integration_state": state,
        "required_docs": required,
        "required_source": "ledger" if from_ledger else "default",
        "ledger_selected": from_ledger,
        "files": present,
        "missing": missing,
        "kona_owned_rejected": rejected,
        "kona_owned_alias": aliased,
        "reasons": [],
    }
    if rejected:
        details["reasons"].append(
            {
                "code": "kona-owned-path-declared",
                "message": (
                    "T6 declares root Kona documents; dedicated Ioniq paths are required"
                ),
            }
        )
    if state is None:
        return common.common_result(
            "docs", common.STATUS_PENDING, "T6 is not in the ledger yet; docs pending", details
        )
    if state not in ACTIVE_STATES:
        return common.common_result(
            "docs",
            common.STATUS_PENDING,
            f"T6 state={state}; dedicated Ioniq history/changelog not required yet",
            details,
        )
    if missing or aliased:
        details["reasons"].append(
            {
                "code": "missing-ioniq-docs",
                "message": "dedicated Ioniq history/changelog documents are missing",
            }
        )
        missing_text = ", ".join(missing or aliased)
        return common.common_result(
            "docs",
            common.STATUS_FAIL,
            f"T6 state={state} but missing dedicated Ioniq docs: {missing_text}",
            details,
        )
    return common.common_result(
        "docs",
        common.STATUS_PASS,
        "dedicated Ioniq history/changelog present for T6 state=" + str(state),
        details,
    )

