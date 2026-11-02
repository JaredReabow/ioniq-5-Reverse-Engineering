#!/usr/bin/env python3
"""Assess passive bench evidence for the recovered physical root-console chain.

This host-side tool reads only canonical ``ioniq-bench-state/v1`` JSON. It does
not execute capture contents, generate a malicious device descriptor, start a
unit, emit a uevent, access a target, or claim root. A positive prerequisite
verdict means only that the installed identities and dormant console endpoint
match the exact recovered CVE-2026-40225 candidate chain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "ioniq-bench-state/v1"
OUTPUT_SCHEMA = "ioniq-bench-physical-root-readiness/v1"
TOOL_VERSION = "1.0.0"
MAX_INPUT_BYTES = 64 * 1024 * 1024
HEX64_RE = re.compile(r"[0-9a-f]{64}")
VALID_STATES = frozenset(("pass", "fail", "unknown"))
EXPECTED_SECTION_ORDER = (
    "meta",
    "identity",
    "processes",
    "smack",
    "units",
    "interfaces",
    "cellular",
    "bluetooth",
    "dropbear",
    "storage",
    "hashes",
    "complete",
)

REFERENCE_HASHES = {
    "/lib/systemd/systemd": "a7f5290180223def9e09570edac76f50a1bfe40b63480153daad1f22d54032b5",
    "/lib/systemd/systemd-udevd": "f32f6296ea20d959ac046ae80724f39e317aaaf492a5c7eedd9270b5b2abab0d",
    "/lib/udev/scsi_id": "85aa83a73d44f19f6b60162a53ee896854b71e7882848819aad20c1ccf079b32",
    "/lib/udev/v4l_id": "afb756b457284578c29960d4abd57f9612020fb45a14fbc285f5061da90a7125",
    "/lib/udev/rules.d/50-udev-default.rules": "c90d7b298f009b82995fdcb288cd717e6d196640b0c8d3d1505b9cb402de7039",
    "/lib/udev/rules.d/60-persistent-storage.rules": "5757bc1da0b3e07ee1769faa266af7720b8eef21006212051a8720c02eab5a8e",
    "/lib/udev/rules.d/60-persistent-v4l.rules": "219eb6b4c0df4d8701cc5a316b2ddf63797d4c1b689bc0b289d5cb8063a7034e",
    "/lib/udev/rules.d/99-systemd.rules": "87799b92929bed3766a2c6f7a186035886043e62f93fa3bf9995cc8ca66fdd5c",
    "/lib/systemd/system/debug-shell.service": "b277d7ffcfdbc9198af6935b64c167c8f7d50ec9ec9acb93b5f7b5d815cfe518",
}


class AssessmentError(ValueError):
    """Fail-closed report or output error."""


def _reject_constant(value: str) -> None:
    raise AssessmentError(f"non-finite JSON constant rejected: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AssessmentError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def load_report_bytes(data: bytes) -> dict[str, Any]:
    if len(data) > MAX_INPUT_BYTES:
        raise AssessmentError(f"input exceeds {MAX_INPUT_BYTES} byte limit")
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise AssessmentError(f"input is not strict UTF-8: {exc}") from exc
    try:
        report = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise AssessmentError(f"invalid JSON: {exc}") from exc
    if not isinstance(report, dict):
        raise AssessmentError("top-level JSON value must be an object")
    if report.get("schema") != INPUT_SCHEMA:
        raise AssessmentError(f"input schema must be {INPUT_SCHEMA}")
    for name in ("capture_sha256", "canonical_sha256"):
        value = report.get(name)
        if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
            raise AssessmentError(f"{name} must be 64 lowercase hex characters")
    subject = dict(report)
    supplied = subject.pop("canonical_sha256")
    computed = hashlib.sha256(_canonical_bytes(subject)).hexdigest()
    if supplied != computed:
        raise AssessmentError(
            f"canonical_sha256 mismatch: expected {computed}, observed {supplied}"
        )
    return report


def load_report(path: Path) -> dict[str, Any]:
    with path.open("rb") as source:
        return load_report_bytes(source.read(MAX_INPUT_BYTES + 1))


def _gate(
    gate_id: str,
    status: str,
    summary: str,
    *,
    observed: Any = None,
    expected: Any = None,
) -> dict[str, Any]:
    if status not in VALID_STATES:
        raise AssertionError(f"invalid gate status: {status}")
    return {
        "id": gate_id,
        "status": status,
        "summary": summary,
        "observed": observed,
        "expected": expected,
    }


def _facts(report: dict[str, Any]) -> dict[str, Any]:
    value = report.get("facts")
    if not isinstance(value, dict):
        raise AssessmentError("facts must be an object")
    return value


def _dict_fact(facts: dict[str, Any], name: str) -> dict[str, Any]:
    value = facts.get(name, {})
    if not isinstance(value, dict):
        raise AssessmentError(f"facts.{name} must be an object")
    return value


def _capture_gate(report: dict[str, Any]) -> dict[str, Any]:
    complete = report.get("complete")
    warnings = report.get("warnings")
    section_order = report.get("section_order")
    if not isinstance(complete, bool):
        raise AssessmentError("complete must be Boolean")
    if not isinstance(warnings, list) or not all(isinstance(x, str) for x in warnings):
        raise AssessmentError("warnings must be an array of strings")
    if not isinstance(section_order, list) or not all(
        isinstance(x, str) for x in section_order
    ):
        raise AssessmentError("section_order must be an array of strings")
    passed = complete and not warnings and section_order == list(EXPECTED_SECTION_ORDER)
    return _gate(
        "capture.complete",
        "pass" if passed else "fail",
        "capture is complete, warning-free, and canonically ordered"
        if passed
        else "capture is incomplete, warned, or noncanonically ordered",
        observed={
            "complete": complete,
            "warnings": warnings,
            "section_order": section_order,
        },
        expected={
            "complete": True,
            "warnings": [],
            "section_order": list(EXPECTED_SECTION_ORDER),
        },
    )


def _hash_gate(hashes: dict[str, Any], path: str, gate_id: str) -> dict[str, Any]:
    observed = hashes.get(path)
    expected = REFERENCE_HASHES[path]
    if observed is None or observed in ("absent", "unavailable"):
        return _gate(
            gate_id,
            "unknown",
            "runtime identity was not captured",
            observed=observed,
            expected=expected,
        )
    if not isinstance(observed, str) or not HEX64_RE.fullmatch(observed):
        return _gate(
            gate_id,
            "fail",
            "runtime identity is malformed",
            observed=observed,
            expected=expected,
        )
    passed = observed == expected
    return _gate(
        gate_id,
        "pass" if passed else "fail",
        "runtime identity matches the recovered reference"
        if passed
        else "runtime identity differs from the recovered reference",
        observed=observed,
        expected=expected,
    )


def _parse_file_state(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    fields = value.split("|", 8)
    if len(fields) != 9 or fields[0] != "present":
        return None
    return {
        "state": fields[0],
        "mode": fields[1],
        "uid": int(fields[2]) if fields[2].isdigit() else fields[2],
        "gid": int(fields[3]) if fields[3].isdigit() else fields[3],
        "size": int(fields[4]) if fields[4].isdigit() else fields[4],
        "kind": fields[5],
        "device_major": fields[6].lower(),
        "device_minor": fields[7].lower(),
        "link_target": fields[8],
    }


def _tty9_gate(files: dict[str, Any]) -> dict[str, Any]:
    raw = files.get("/dev/tty9")
    expected = {
        "state": "present",
        "kind": "character special file",
        "device_major": "4",
        "device_minor": "9",
    }
    if raw is None or raw in ("absent", "unavailable"):
        return _gate(
            "console.tty9",
            "unknown",
            "the tty9 endpoint was not observed",
            observed=raw,
            expected=expected,
        )
    parsed = _parse_file_state(raw)
    if parsed is None:
        return _gate(
            "console.tty9",
            "fail",
            "tty9 metadata is malformed or not present",
            observed=raw,
            expected=expected,
        )
    passed = (
        parsed["kind"] == expected["kind"]
        and parsed["device_major"] == "4"
        and parsed["device_minor"] == "9"
    )
    return _gate(
        "console.tty9",
        "pass" if passed else "fail",
        "tty9 is the expected character device 4:9"
        if passed
        else "tty9 metadata differs from the recovered endpoint",
        observed=parsed,
        expected=expected,
    )


def _debug_unit_gate(units: dict[str, Any]) -> dict[str, Any]:
    observed = units.get("debug-shell.service")
    expected = "LoadState=loaded"
    if observed is None or observed == "systemctl-unavailable":
        return _gate(
            "debug_shell.loaded",
            "unknown",
            "debug-shell load state was not observed",
            observed=observed,
            expected=expected,
        )
    if not isinstance(observed, str):
        raise AssessmentError("facts.units.debug-shell.service must be a string")
    fields: dict[str, str] = {}
    malformed = False
    for field in observed.split(";"):
        if not field:
            continue
        if "=" not in field:
            malformed = True
            continue
        key, value = field.split("=", 1)
        fields[key] = value
    if malformed or "LoadState" not in fields:
        return _gate(
            "debug_shell.loaded",
            "fail",
            "debug-shell unit-state record is malformed",
            observed=observed,
            expected=expected,
        )
    passed = fields["LoadState"] == "loaded"
    return _gate(
        "debug_shell.loaded",
        "pass" if passed else "fail",
        "debug-shell unit is loaded; activation is not required by this passive gate"
        if passed
        else "debug-shell unit is not loaded",
        observed=fields,
        expected={"LoadState": "loaded"},
    )


def assess(report: dict[str, Any]) -> dict[str, Any]:
    facts = _facts(report)
    hashes = _dict_fact(facts, "hashes")
    files = _dict_fact(facts, "files")
    units = _dict_fact(facts, "units")

    gates = [
        _capture_gate(report),
        _hash_gate(hashes, "/lib/systemd/systemd", "manager.systemd_identity"),
        _hash_gate(hashes, "/lib/systemd/systemd-udevd", "manager.udevd_identity"),
        _hash_gate(hashes, "/lib/udev/scsi_id", "scsi.helper_identity"),
        _hash_gate(
            hashes,
            "/lib/udev/rules.d/60-persistent-storage.rules",
            "scsi.import_rule_identity",
        ),
        _hash_gate(
            hashes,
            "/lib/udev/rules.d/99-systemd.rules",
            "systemd.block_tag_rule_identity",
        ),
        _hash_gate(
            hashes,
            "/lib/systemd/system/debug-shell.service",
            "debug_shell.unit_identity",
        ),
        _debug_unit_gate(units),
        _tty9_gate(files),
        _hash_gate(hashes, "/lib/udev/v4l_id", "v4l.helper_identity"),
        _hash_gate(
            hashes,
            "/lib/udev/rules.d/60-persistent-v4l.rules",
            "v4l.import_rule_identity",
        ),
        _hash_gate(
            hashes,
            "/lib/udev/rules.d/50-udev-default.rules",
            "v4l.remove_rule_identity",
        ),
    ]
    statuses = {gate["id"]: gate["status"] for gate in gates}
    scsi_gate_ids = (
        "capture.complete",
        "manager.systemd_identity",
        "manager.udevd_identity",
        "scsi.helper_identity",
        "scsi.import_rule_identity",
        "systemd.block_tag_rule_identity",
        "debug_shell.unit_identity",
        "debug_shell.loaded",
        "console.tty9",
    )
    v4l_gate_ids = (
        "capture.complete",
        "manager.systemd_identity",
        "manager.udevd_identity",
        "v4l.helper_identity",
        "v4l.import_rule_identity",
        "v4l.remove_rule_identity",
    )
    result: dict[str, Any] = {
        "schema": OUTPUT_SCHEMA,
        "tool_version": TOOL_VERSION,
        "input": {
            "schema": report["schema"],
            "capture_sha256": report["capture_sha256"],
            "canonical_sha256": report["canonical_sha256"],
        },
        "reference_hashes": REFERENCE_HASHES,
        "gates": gates,
        "gate_counts": {
            state: sum(gate["status"] == state for gate in gates)
            for state in ("fail", "pass", "unknown")
        },
        "verdict": {
            "scsi_root_console_prerequisites_observed": all(
                statuses[gate_id] == "pass" for gate_id in scsi_gate_ids
            ),
            "v4l_property_injection_prerequisites_observed": all(
                statuses[gate_id] == "pass" for gate_id in v4l_gate_ids
            ),
            "hardware_control_bytes_observed": False,
            "property_injection_observed": False,
            "debug_shell_activation_observed": False,
            "interactive_console_observed": False,
            "root_access_demonstrated": False,
            "persistence_demonstrated": False,
        },
        "boundaries": [
            "A positive prerequisite verdict binds passive installed identities only; it does not execute a helper or demonstrate hardware-controlled bytes.",
            "The assessor never treats a disabled or inactive but loaded debug-shell unit as activation evidence.",
            "No injected property, service request, virtual-terminal switch, command execution, root transition, or persistence is inferred.",
            "Owner-unit applicability still depends on a complete capture from the disconnected physical bench.",
        ],
    }
    result["canonical_sha256"] = hashlib.sha256(_canonical_bytes(result)).hexdigest()
    return result


def _write_json_exclusive(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="canonical bench-state JSON")
    parser.add_argument("-o", "--output", type=Path, help="create this JSON report")
    args = parser.parse_args(argv)
    try:
        result = assess(load_report(args.report))
        data = json.dumps(
            result, ensure_ascii=False, indent=2, sort_keys=True
        ).encode("utf-8") + b"\n"
        if args.output is None:
            sys.stdout.buffer.write(data)
        else:
            _write_json_exclusive(args.output, data)
    except (AssessmentError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
