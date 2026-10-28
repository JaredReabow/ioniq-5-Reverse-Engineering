"""JSON syntax checks for the ledger and every council record on disk."""

from __future__ import annotations

from pathlib import Path

from . import common

COUNCIL_RECORD_NAMES = (
    "council-packet.json",
    "task.json",
    "validation-receipt.json",
    "manifest.json",
)


def jsoncheck_targets(root: Path) -> list[Path]:
    """Return the JSON files the project maintains, in deterministic order."""
    root = Path(root)
    targets: list[Path] = []
    ledger = root / "research-ledger.json"
    if ledger.is_file():
        targets.append(ledger)
    council_root = root / "council"
    if council_root.is_dir():
        for directory in sorted(
            (path for path in council_root.iterdir() if path.is_dir()),
            key=lambda item: common.common_natural_key(item.name),
        ):
            for name in COUNCIL_RECORD_NAMES:
                candidate = directory / name
                if candidate.is_file():
                    targets.append(candidate)
    return targets


def jsoncheck_scan(root: Path) -> dict:
    """Parse every maintained JSON file and report syntax failures."""
    root = Path(root)
    records: list[dict] = []
    bad = 0
    for target in jsoncheck_targets(root):
        _, error = common.common_read_json(target)
        record = {"path": common.common_relative(root, target), "ok": error is None}
        if error:
            record["error"] = error
            bad += 1
        records.append(record)
    details = {"files": records, "checked": len(records), "invalid": bad}
    if not records:
        return common.common_result(
            "json", common.STATUS_FAIL, "no ledger or council JSON records found", details
        )
    if bad:
        return common.common_result(
            "json",
            common.STATUS_FAIL,
            f"{bad}/{len(records)} JSON record(s) failed to parse",
            details,
        )
    return common.common_result(
        "json", common.STATUS_PASS, f"{len(records)} JSON record(s) parse cleanly", details
    )

