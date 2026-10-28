"""Independent SHA-256 verification of every ledger-declared artifact."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from . import common


def artifacts_check(ledger_path: Path, root: Path) -> dict:
    """Re-hash each declared artifact and classify missing, stale, or unsafe paths."""
    root = Path(root)
    document, error = common.common_read_json(Path(ledger_path))
    if error:
        return common.common_result(
            "artifacts", common.STATUS_FAIL, f"ledger unreadable: {error}", {"error": error}
        )
    declared = document.get("artifacts") if isinstance(document, dict) else None
    if not isinstance(declared, list) or not declared:
        return common.common_result(
            "artifacts",
            common.STATUS_FAIL,
            "ledger declares no artifacts to verify",
            {"declared": 0},
        )
    entries: list[dict] = []
    counts = {"ok": 0, "missing": 0, "stale": 0, "unsafe": 0, "malformed": 0}
    for index, entry in enumerate(declared):
        record = {
            "index": index,
            "id": None,
            "path": None,
            "expected": None,
            "actual": None,
            "state": "malformed",
        }
        if not isinstance(entry, dict):
            counts["malformed"] += 1
            entries.append(record)
            continue
        record["id"] = entry.get("id")
        raw_path = entry.get("path")
        expected = str(entry.get("sha256") or "").lower()
        record["path"] = raw_path if isinstance(raw_path, str) else None
        record["expected"] = expected or None
        if (
            not isinstance(raw_path, str)
            or not raw_path
            or len(expected) != 64
            or any(ch not in "0123456789abcdef" for ch in expected)
        ):
            counts["malformed"] += 1
            entries.append(record)
            continue
        relative = PurePosixPath(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            record["state"] = "unsafe"
            counts["unsafe"] += 1
            entries.append(record)
            continue
        target = root / relative
        if not target.is_file():
            record["state"] = "missing"
            counts["missing"] += 1
            entries.append(record)
            continue
        try:
            actual = common.common_sha256(target)
        except OSError:
            record["state"] = "missing"
            counts["missing"] += 1
            entries.append(record)
            continue
        record["actual"] = actual
        if actual != expected:
            record["state"] = "stale"
            counts["stale"] += 1
        else:
            record["state"] = "ok"
            counts["ok"] += 1
        entries.append(record)

    details = {"counts": counts, "entries": entries, "declared": len(declared)}
    bad = counts["missing"] + counts["stale"] + counts["unsafe"] + counts["malformed"]
    if bad:
        return common.common_result(
            "artifacts",
            common.STATUS_FAIL,
            (
                f"{counts['ok']}/{len(declared)} verified; "
                f"{counts['stale']} stale, {counts['missing']} missing, "
                f"{counts['unsafe']} unsafe, {counts['malformed']} malformed"
            ),
            details,
        )
    return common.common_result(
        "artifacts",
        common.STATUS_PASS,
        f"{counts['ok']}/{len(declared)} artifacts match their declared SHA-256",
        details,
    )

