#!/usr/bin/env python3
"""Assess passive bench-state evidence for the configured SMACK exec chain.

This host-side tool parses JSON only. It never executes capture contents or a
recovered target. A positive report means that named prerequisites were observed;
it is not proof of successful exec, root access, MAC override, update acceptance,
or persistence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

INPUT_SCHEMA = "ioniq-bench-state/v1"
OUTPUT_SCHEMA = "ioniq-bench-root-readiness/v1"
TOOL_VERSION = "1.0.0"
MAX_INPUT_BYTES = 64 * 1024 * 1024
HEX64_RE = re.compile(r"[0-9a-f]{64}")

ANCHOR = "/etc/update_start_5w.sh.ori"
BASH_PATHS = ("/bin/sh", "/bin/bash")
LOADER_PATHS = ("/lib/ld-linux-x86-64.so.2", "/lib/ld-2.25.so")
DATE_PATHS = ("/bin/date", "/usr/bin/date")
ANCHOR_SHA256 = "06c3ab7e24b082c24a81299f0627245c0281bc5d519005cd921c13707eb5e838"
BASH_SHA256 = "783a69b9b27fae5da3fa93e441467160d6e760f3a79048a4dd02d98b571ad0aa"
LOADER_SHA256 = "0dfa16d8b5c9b35fb161a6f5dab48e7b267531ecf8ec3bf3ac74de61ce2ad99e"
MAC_CAPABILITIES = frozenset(("CAP_MAC_OVERRIDE", "CAP_MAC_ADMIN"))
VALID_GATE_STATES = frozenset(("pass", "fail", "unknown"))
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


class AssessmentError(ValueError):
    """Fail-closed input or schema error."""


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
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise AssessmentError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise AssessmentError("top-level JSON value must be an object")
    if value.get("schema") != INPUT_SCHEMA:
        raise AssessmentError(f"input schema must be {INPUT_SCHEMA}")
    capture_digest = value.get("capture_sha256")
    if not isinstance(capture_digest, str) or not HEX64_RE.fullmatch(capture_digest):
        raise AssessmentError("capture_sha256 must be 64 lowercase hex characters")
    supplied = value.get("canonical_sha256")
    if not isinstance(supplied, str) or not HEX64_RE.fullmatch(supplied):
        raise AssessmentError("canonical_sha256 must be 64 lowercase hex characters")
    canonical_subject = dict(value)
    del canonical_subject["canonical_sha256"]
    computed = hashlib.sha256(_canonical_bytes(canonical_subject)).hexdigest()
    if computed != supplied:
        raise AssessmentError(
            f"canonical_sha256 mismatch: expected {computed}, observed {supplied}"
        )
    return value


def load_report(path: Path) -> dict[str, Any]:
    with path.open("rb") as source:
        data = source.read(MAX_INPUT_BYTES + 1)
    return load_report_bytes(data)


def _gate(
    gate_id: str,
    status: str,
    summary: str,
    *,
    observed: Any = None,
    expected: Any = None,
) -> dict[str, Any]:
    if status not in VALID_GATE_STATES:
        raise AssertionError(f"invalid gate state: {status}")
    return {
        "id": gate_id,
        "status": status,
        "summary": summary,
        "observed": observed,
        "expected": expected,
    }


def _typed_facts(report: dict[str, Any]) -> dict[str, Any]:
    facts = report.get("facts")
    if not isinstance(facts, dict):
        raise AssessmentError("facts must be an object")
    return facts


def _dict_fact(facts: dict[str, Any], name: str) -> dict[str, Any]:
    value = facts.get(name, {})
    if not isinstance(value, dict):
        raise AssessmentError(f"facts.{name} must be an object")
    return value


def _list_fact(facts: dict[str, Any], name: str) -> list[Any]:
    value = facts.get(name, [])
    if not isinstance(value, list):
        raise AssessmentError(f"facts.{name} must be an array")
    return value


def _records(report: dict[str, Any], key: str) -> list[str]:
    sections = report.get("sections")
    if not isinstance(sections, list):
        raise AssessmentError("sections must be an array")
    values: list[str] = []
    for section in sections:
        if not isinstance(section, dict):
            raise AssessmentError("every section must be an object")
        records = section.get("records", [])
        if not isinstance(records, list):
            raise AssessmentError("section records must be an array")
        for record in records:
            if not isinstance(record, dict):
                raise AssessmentError("every record must be an object")
            record_key = record.get("key")
            record_value = record.get("value")
            if not isinstance(record_key, str) or not isinstance(record_value, str):
                raise AssessmentError("record key and value must be strings")
            if record_key == key:
                values.append(record_value)
    return values


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
        "bench-state capture is complete, warning-free, and has the exact section order"
        if passed
        else "bench-state capture is incomplete, warned, or has a noncanonical section order",
        observed={"complete": complete, "warnings": warnings, "section_order": section_order},
        expected={
            "complete": True,
            "warnings": [],
            "section_order": list(EXPECTED_SECTION_ORDER),
        },
    )


def _hash_gate(
    hashes: dict[str, Any], gate_id: str, paths: Iterable[str], expected: str
) -> dict[str, Any]:
    observed: dict[str, Any] = {}
    valid: list[str] = []
    mismatches: list[str] = []
    for path in paths:
        value = hashes.get(path)
        observed[path] = value
        if value is None or value in ("absent", "unavailable"):
            continue
        if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
            mismatches.append(path)
        elif value == expected:
            valid.append(path)
        else:
            mismatches.append(path)
    if mismatches:
        status = "fail"
        summary = "one or more observed identities differ from the recovered reference"
    elif valid:
        status = "pass"
        summary = "at least one observed pathname matches the recovered reference"
    else:
        status = "unknown"
        summary = "no usable runtime identity was captured"
    return _gate(gate_id, status, summary, observed=observed, expected=expected)


def _parse_file_state(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    fields = value.split("|", 8)
    if not fields or fields[0] != "present" or len(fields) < 9:
        return None
    return {
        "state": fields[0],
        "mode": fields[1],
        "uid": int(fields[2]) if fields[2].isdigit() else fields[2],
        "gid": int(fields[3]) if fields[3].isdigit() else fields[3],
        "size": int(fields[4]) if fields[4].isdigit() else fields[4],
        "kind": fields[5],
        "device_major": fields[6],
        "device_minor": fields[7],
        "link_target": fields[8],
    }


def _anchor_metadata_gate(files: dict[str, Any]) -> dict[str, Any]:
    raw = files.get(ANCHOR)
    parsed = _parse_file_state(raw)
    expected = {"mode": "700", "uid": 0, "gid": 0, "kind": "regular file"}
    if parsed is None:
        return _gate(
            "anchor.metadata",
            "unknown",
            "anchor metadata is absent or unavailable",
            observed=raw,
            expected=expected,
        )
    matches = (
        parsed["mode"] in ("700", "0700")
        and parsed["uid"] == 0
        and parsed["gid"] == 0
        and parsed["kind"] == "regular file"
    )
    return _gate(
        "anchor.metadata",
        "pass" if matches else "fail",
        "anchor is a root-owned mode-0700 regular file"
        if matches
        else "observed anchor metadata differs from the recovered contract",
        observed=parsed,
        expected=expected,
    )


def _xattr_gate(
    xattrs: dict[str, Any], gate_id: str, path: str, name: str, expected: str
) -> dict[str, Any]:
    path_value = xattrs.get(path)
    if not isinstance(path_value, dict):
        return _gate(
            gate_id,
            "unknown",
            "xattr observation is missing",
            observed=None,
            expected={"state": "present", "value": expected},
        )
    item = path_value.get(name)
    if not isinstance(item, dict):
        return _gate(
            gate_id,
            "unknown",
            "xattr observation is missing",
            observed=item,
            expected={"state": "present", "value": expected},
        )
    state = item.get("state")
    value = item.get("value")
    if state != "present":
        status = "unknown" if state in ("path-absent", "provider-unavailable", "query-error") else "fail"
    else:
        status = "pass" if value == expected else "fail"
    return _gate(
        gate_id,
        status,
        "observed xattr matches the configured label"
        if status == "pass"
        else "observed xattr does not establish the configured label",
        observed=item,
        expected={"state": "present", "value": expected},
    )


def _onlycap_gate(report: dict[str, Any]) -> dict[str, Any]:
    values = _records(report, "smack-onlycap")
    if not values:
        return _gate(
            "smack.onlycap",
            "unknown",
            "live onlycap was not captured",
            observed=[],
            expected=["Privileged"],
        )
    status = "pass" if values == ["Privileged"] else "fail"
    return _gate(
        "smack.onlycap",
        status,
        "onlycap names Privileged" if status == "pass" else "onlycap differs from Privileged",
        observed=values,
        expected=["Privileged"],
    )


def _policy_rules(report: dict[str, Any]) -> dict[tuple[str, str], set[str]]:
    rules: dict[tuple[str, str], set[str]] = {}
    for line in _records(report, "smack-rule"):
        fields = line.split()
        if len(fields) < 3:
            continue
        subject, obj, permissions = fields[:3]
        rules.setdefault((subject, obj), set()).update(permissions)
    return rules


def _policy_status(rules: dict[tuple[str, str], set[str]], label: str) -> dict[str, Any]:
    permissions = rules.get((label, "_"))
    if permissions is None:
        return {"status": "unknown", "permissions": None}
    return {
        "status": "pass" if {"r", "x"}.issubset(permissions) else "fail",
        "permissions": "".join(sorted(permissions)),
    }


def _valid_capability_object(value: Any) -> bool:
    if not isinstance(value, dict) or value.get("malformed"):
        return False
    hex_value = value.get("hex")
    numeric = value.get("value")
    names = value.get("names")
    return bool(
        isinstance(hex_value, str)
        and re.fullmatch(r"[0-9a-f]{1,16}", hex_value)
        and isinstance(numeric, int)
        and numeric >= 0
        and int(hex_value, 16) == numeric
        and isinstance(names, list)
        and all(isinstance(item, str) for item in names)
    )


def _capability_status(security: Any) -> dict[str, Any]:
    if not isinstance(security, dict):
        return {"status": "unknown", "effective": None, "matching": []}
    effective = security.get("cap_effective")
    if not _valid_capability_object(effective):
        return {"status": "unknown", "effective": effective, "matching": []}
    names = effective["names"]
    matching = sorted(MAC_CAPABILITIES.intersection(names))
    return {
        "status": "pass" if matching else "fail",
        "effective": effective,
        "matching": matching,
    }


def _credential_status(credentials: Any) -> str:
    if not isinstance(credentials, dict):
        return "unknown"
    required = ("ruid", "euid", "suid", "fsuid", "rgid", "egid", "sgid", "fsgid")
    if any(not isinstance(credentials.get(name), int) for name in required):
        return "unknown"
    return "pass" if credentials["euid"] == 0 and credentials["fsuid"] == 0 else "fail"


def _security_status(security: Any) -> str:
    if not isinstance(security, dict):
        return "unknown"
    required = ("cap_inheritable", "cap_permitted", "cap_effective", "cap_bounding")
    if any(not _valid_capability_object(security.get(name)) for name in required):
        return "unknown"
    if not isinstance(security.get("ppid"), int):
        return "unknown"
    if security.get("no_new_privs") is not None and not isinstance(
        security.get("no_new_privs"), int
    ):
        return "unknown"
    if not isinstance(security.get("seccomp"), int):
        return "unknown"
    return "pass"


def _callers(report: dict[str, Any], facts: dict[str, Any]) -> list[dict[str, Any]]:
    processes = _list_fact(facts, "processes")
    credentials = _dict_fact(facts, "process_credentials")
    security = _dict_fact(facts, "process_security")
    paths = _dict_fact(facts, "process_paths")
    rules = _policy_rules(report)
    callers: list[dict[str, Any]] = []
    for process in processes:
        if not isinstance(process, dict):
            raise AssessmentError("every facts.processes item must be an object")
        label = process.get("smack_label")
        pid = process.get("pid")
        if not isinstance(label, str) or not label.startswith("App::"):
            continue
        pid_key = str(pid)
        caller_credentials = credentials.get(pid_key)
        caller_security = security.get(pid_key)
        caller_path = paths.get(pid_key)
        policy = _policy_status(rules, label)
        credential_status = _credential_status(caller_credentials)
        security_status = _security_status(caller_security)
        mac = _capability_status(caller_security)
        no_new_privs = caller_security.get("no_new_privs") if isinstance(caller_security, dict) else None
        seccomp = caller_security.get("seccomp") if isinstance(caller_security, dict) else None
        caller_ready = (
            policy["status"] == "pass"
            and credential_status == "pass"
            and security_status == "pass"
        )
        callers.append(
            {
                "pid": pid,
                "comm": process.get("comm"),
                "exe": process.get("exe"),
                "smack_label": label,
                "credentials": caller_credentials,
                "credential_status": credential_status,
                "security": caller_security,
                "security_status": security_status,
                "policy_to_floor": policy,
                "path": caller_path if isinstance(caller_path, str) else None,
                "path_observed": isinstance(caller_path, str) and bool(caller_path),
                "no_new_privs": no_new_privs,
                "seccomp": seccomp,
                "mac_capability_prerequisite": mac,
                "runtime_source_prerequisites_observed": caller_ready,
            }
        )
    callers.sort(key=lambda item: (str(item["pid"]), item["smack_label"]))
    return callers


def _caller_gate(callers: list[dict[str, Any]]) -> dict[str, Any]:
    if any(item["runtime_source_prerequisites_observed"] for item in callers):
        status = "pass"
        summary = "at least one live App-domain task has observed root credentials, capability sets, and floor read/execute policy"
    elif not callers:
        status = "unknown"
        summary = "no live App-domain task was captured"
    elif all(
        item["credential_status"] == "fail" or item["policy_to_floor"]["status"] == "fail"
        for item in callers
    ):
        status = "fail"
        summary = "captured App-domain tasks fail an observed source prerequisite"
    else:
        status = "unknown"
        summary = "captured App-domain tasks have incomplete source evidence"
    return _gate(
        "source.app_domain_task",
        status,
        summary,
        observed=[
            {
                "pid": item["pid"],
                "smack_label": item["smack_label"],
                "credential_status": item["credential_status"],
                "security_status": item["security_status"],
                "policy_status": item["policy_to_floor"]["status"],
            }
            for item in callers
        ],
        expected="one App::* task with euid/fsuid 0, complete capability observations, and App::* -> _ read+execute",
    )


def _mount_unescape(value: str) -> str:
    return re.sub(
        r"\\([0-7]{3})",
        lambda match: chr(int(match.group(1), 8)),
        value,
    )


def _mount_gate(report: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for line in _records(report, "smack-mounts"):
        fields = line.split()
        if len(fields) < 4:
            continue
        source, mountpoint, fs_type, options = fields[:4]
        mountpoint = _mount_unescape(mountpoint)
        prefix = mountpoint.rstrip("/") + "/"
        if mountpoint == "/" or ANCHOR.startswith(prefix):
            candidates.append(
                {
                    "source": _mount_unescape(source),
                    "mountpoint": mountpoint,
                    "type": fs_type,
                    "options": sorted(options.split(",")),
                }
            )
    if not candidates:
        return _gate(
            "mount.anchor_exec",
            "unknown",
            "no mount covering the anchor was captured",
            observed=[],
            expected="covering mount without noexec",
        )
    selected = max(candidates, key=lambda item: len(item["mountpoint"]))
    status = "fail" if "noexec" in selected["options"] else "pass"
    return _gate(
        "mount.anchor_exec",
        status,
        "covering mount does not advertise noexec"
        if status == "pass"
        else "covering mount advertises noexec",
        observed=selected,
        expected="no noexec option",
    )


def _date_observations(hashes: dict[str, Any], files: dict[str, Any], xattrs: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in DATE_PATHS:
        result.append(
            {
                "path": path,
                "hash": hashes.get(path),
                "metadata": _parse_file_state(files.get(path)),
                "smack64": xattrs.get(path, {}).get("SMACK64")
                if isinstance(xattrs.get(path), dict)
                else None,
                "smack64exec": xattrs.get(path, {}).get("SMACK64EXEC")
                if isinstance(xattrs.get(path), dict)
                else None,
            }
        )
    return result


def assess(report: dict[str, Any]) -> dict[str, Any]:
    facts = _typed_facts(report)
    hashes = _dict_fact(facts, "hashes")
    files = _dict_fact(facts, "files")
    xattrs = _dict_fact(facts, "smack_xattrs")

    gates = [
        _capture_gate(report),
        _hash_gate(hashes, "anchor.identity", (ANCHOR,), ANCHOR_SHA256),
        _anchor_metadata_gate(files),
        _xattr_gate(xattrs, "anchor.smack64", ANCHOR, "SMACK64", "_"),
        _xattr_gate(
            xattrs,
            "anchor.smack64exec",
            ANCHOR,
            "SMACK64EXEC",
            "Privileged",
        ),
        _hash_gate(hashes, "interpreter.bash_identity", BASH_PATHS, BASH_SHA256),
        _hash_gate(hashes, "interpreter.loader_identity", LOADER_PATHS, LOADER_SHA256),
        _onlycap_gate(report),
        _mount_gate(report),
    ]
    callers = _callers(report, facts)
    gates.append(_caller_gate(callers))
    gate_map = {item["id"]: item for item in gates}
    required_ids = (
        "capture.complete",
        "anchor.identity",
        "anchor.metadata",
        "anchor.smack64",
        "anchor.smack64exec",
        "interpreter.bash_identity",
        "interpreter.loader_identity",
        "smack.onlycap",
        "mount.anchor_exec",
        "source.app_domain_task",
    )
    ready = all(gate_map[item]["status"] == "pass" for item in required_ids)
    useful_override = ready and any(
        item["runtime_source_prerequisites_observed"]
        and item["mac_capability_prerequisite"]["status"] == "pass"
        for item in callers
    )
    counts = {state: sum(item["status"] == state for item in gates) for state in sorted(VALID_GATE_STATES)}
    result: dict[str, Any] = {
        "schema": OUTPUT_SCHEMA,
        "tool": "bench-root-readiness",
        "tool_version": TOOL_VERSION,
        "input": {
            "schema": report["schema"],
            "canonical_sha256": report["canonical_sha256"],
            "capture_sha256": report.get("capture_sha256"),
        },
        "expected_recovered_identities": {
            ANCHOR: ANCHOR_SHA256,
            "/bin/bash": BASH_SHA256,
            "/lib/ld-2.25.so": LOADER_SHA256,
        },
        "gates": gates,
        "gate_counts": counts,
        "callers": callers,
        "fixed_date_observations": _date_observations(hashes, files, xattrs),
        "verdict": {
            "runtime_chain_prerequisites_observed": ready,
            "effective_mac_override_prerequisites_observed": useful_override,
            "credential_commit_observed": False,
            "complete_interpreter_loading_observed": False,
            "root_access_demonstrated": False,
            "persistence_demonstrated": False,
        },
        "limits": [
            "A passive capture cannot observe the anchor exec, credential commitment, or complete ELF loading.",
            "onlycap supplies SMACK-label eligibility and does not grant Linux capabilities.",
            "Capability masks do not expose securebits and do not prove an effective SMACK override call.",
            "Fixed date-path observations do not prove runtime PATH resolution or caller control of PATH.",
            "No update authentication, partition write, slot activation, boot acceptance, root, or persistence action is performed.",
        ],
    }
    result["canonical_sha256"] = hashlib.sha256(_canonical_bytes(result)).hexdigest()
    return result


def report_bytes(result: dict[str, Any]) -> bytes:
    return (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="parsed ioniq-bench-state/v1 JSON")
    parser.add_argument("-o", "--output", type=Path, help="exclusive host output path; defaults to stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = assess(load_report(args.input))
        payload = report_bytes(result)
        if args.output is None:
            sys.stdout.buffer.write(payload)
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("xb") as target:
                target.write(payload)
    except (AssessmentError, OSError) as exc:
        sys.stderr.buffer.write((f"error: {exc}\n").encode("utf-8", "replace"))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
