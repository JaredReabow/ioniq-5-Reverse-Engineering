#!/usr/bin/env python3
"""Assess passive bench evidence for the CVE-2017-6001 perf candidate.

This host-only tool consumes canonical ``ioniq-bench-state/v1`` JSON produced by
the read-only disconnected-bench probe. It never contacts a target, opens a
device, invokes ``perf_event_open``, creates or enables an event, starts a thread,
schedules a race, or emits event attributes, trigger material, a payload, or
firmware bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "ioniq-bench-state/v1"
OUTPUT_SCHEMA = "ioniq-bench-perf-readiness/v1"
TOOL_VERSION = "1.0.0"
MAX_INPUT_BYTES = 64 * 1024 * 1024
HEX64_RE = re.compile(r"[0-9a-f]{64}")
SOURCE_NAME_RE = re.compile(r"[A-Za-z0-9_.-]+")
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
    """Fail-closed input or output error."""


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


def stable_read(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise AssessmentError(f"cannot open input: {exc}") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise AssessmentError("input must be a regular file")
        if before.st_size < 0 or before.st_size > MAX_INPUT_BYTES:
            raise AssessmentError(f"input exceeds {MAX_INPUT_BYTES} byte limit")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                raise AssessmentError("short input read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise AssessmentError("input grew during read")
        after = os.fstat(descriptor)
        before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if before_identity != after_identity:
            raise AssessmentError("input identity changed during read")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


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
    expected_top = {
        "schema",
        "capture_sha256",
        "capture_bytes",
        "complete",
        "section_order",
        "sections",
        "facts",
        "warnings",
        "canonical_sha256",
    }
    if set(report) != expected_top:
        raise AssessmentError("input top-level fields do not match producer schema")
    if report.get("schema") != INPUT_SCHEMA:
        raise AssessmentError(f"input schema must be {INPUT_SCHEMA}")
    if report.get("complete") is not True or report.get("warnings") != []:
        raise AssessmentError("input report is incomplete or has warnings")
    if not _is_plain_int(report.get("capture_bytes")) or report["capture_bytes"] < 0:
        raise AssessmentError("capture_bytes must be a non-negative integer")
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
    if report.get("section_order") != list(EXPECTED_SECTION_ORDER):
        raise AssessmentError("unexpected section order")
    sections = report.get("sections")
    if not isinstance(sections, list) or len(sections) != len(EXPECTED_SECTION_ORDER):
        raise AssessmentError("unexpected section count")
    for expected_name, section in zip(EXPECTED_SECTION_ORDER, sections):
        if not isinstance(section, dict) or set(section) != {
            "name",
            "complete",
            "end_status",
            "records",
            "raw",
            "captured_bytes",
            "sha256",
        }:
            raise AssessmentError(f"section fields are malformed: {expected_name}")
        if section.get("name") != expected_name:
            raise AssessmentError("section identity is malformed")
        if section.get("complete") is not True or section.get("end_status") != 0:
            raise AssessmentError(f"section is incomplete: {expected_name}")
        if not _is_plain_int(section.get("captured_bytes")) or section["captured_bytes"] < 0:
            raise AssessmentError(f"section byte count is malformed: {expected_name}")
        raw_lines = section.get("raw")
        if not isinstance(raw_lines, list) or any(not isinstance(line, str) for line in raw_lines):
            raise AssessmentError(f"section raw records are malformed: {expected_name}")
        supplied_section_hash = section.get("sha256")
        if not isinstance(supplied_section_hash, str) or not HEX64_RE.fullmatch(supplied_section_hash):
            raise AssessmentError(f"section SHA-256 is malformed: {expected_name}")
        section_subject = dict(section)
        section_subject.pop("sha256")
        if hashlib.sha256(_canonical_bytes(section_subject)).hexdigest() != supplied_section_hash:
            raise AssessmentError(f"section SHA-256 mismatch: {expected_name}")
        records = section.get("records")
        if not isinstance(records, list):
            raise AssessmentError(f"section records are malformed: {expected_name}")
        for record in records:
            if (
                not isinstance(record, dict)
                or set(record) != {"key", "value"}
                or not isinstance(record.get("key"), str)
                or not isinstance(record.get("value"), str)
            ):
                raise AssessmentError(f"malformed record in section: {expected_name}")
    if sections[0]["records"] != [{"key": "schema", "value": INPUT_SCHEMA}]:
        raise AssessmentError("meta schema record is missing or invalid")
    if sections[-1]["records"] != [{"key": "result", "value": "complete"}]:
        raise AssessmentError("terminal complete record is missing or invalid")
    if not isinstance(report.get("facts"), dict):
        raise AssessmentError("facts must be an object")
    return report


def load_report(path: Path) -> dict[str, Any]:
    return load_report_bytes(stable_read(path))


def _records(report: dict[str, Any], key: str) -> list[str]:
    return [
        record["value"]
        for section in report["sections"]
        for record in section["records"]
        if record["key"] == key
    ]


def _single_record(report: dict[str, Any], key: str) -> str | None:
    values = _records(report, key)
    if len(values) > 1:
        raise AssessmentError(f"conflicting {key} records")
    return values[0] if values else None


def _kernel_banner_match(report: dict[str, Any]) -> bool | None:
    value = _single_record(report, "uname")
    if value is None:
        return None
    fields = value.split()
    if len(fields) < 3 or fields[0] != "Linux":
        raise AssessmentError("malformed uname record")
    return fields[2] == "4.1.27-abl"


def _paranoid_value(report: dict[str, Any]) -> int | None:
    value = _single_record(report, "perf-event-paranoid")
    if value is None:
        return None
    if not re.fullmatch(r"-?[0-9]+", value):
        raise AssessmentError("malformed perf-event-paranoid record")
    parsed = int(value, 10)
    if parsed < -(2**31) or parsed > 2**31 - 1:
        raise AssessmentError("perf-event-paranoid is outside signed 32-bit range")
    return parsed


def _event_sources(report: dict[str, Any]) -> tuple[bool, dict[str, dict[str, Any]]]:
    count_text = _single_record(report, "perf-event-source-count")
    values = _records(report, "perf-event-source")
    if count_text is None:
        if values:
            raise AssessmentError("perf event sources present without inventory count")
        return False, {}
    if not re.fullmatch(r"[0-9]+", count_text):
        raise AssessmentError("malformed perf-event-source-count record")
    count = int(count_text, 10)
    sources: dict[str, dict[str, Any]] = {}
    for value in values:
        fields = value.split("|", 6)
        if len(fields) != 7:
            raise AssessmentError("malformed perf-event-source record")
        name, type_state, type_text, cpumask_state, cpumask, device_state, device = fields
        if not SOURCE_NAME_RE.fullmatch(name):
            raise AssessmentError("malformed perf event source name")
        if name in sources:
            raise AssessmentError(f"duplicate perf event source: {name}")
        if type_state not in {"present", "absent", "error", "malformed"}:
            raise AssessmentError(f"invalid type state for perf event source: {name}")
        if cpumask_state not in {"present", "absent", "error", "malformed"}:
            raise AssessmentError(f"invalid cpumask state for perf event source: {name}")
        if device_state not in {"present", "absent", "error", "unavailable"}:
            raise AssessmentError(f"invalid device state for perf event source: {name}")
        source_type: int | None = None
        if type_state == "present":
            if not re.fullmatch(r"[0-9]+", type_text):
                raise AssessmentError(f"invalid type value for perf event source: {name}")
            source_type = int(type_text, 10)
            if source_type > 2**31 - 1:
                raise AssessmentError(f"type value is too large for perf event source: {name}")
        elif type_text:
            raise AssessmentError(f"nonempty type value for unavailable perf event source: {name}")
        if cpumask_state == "present":
            if not cpumask or not re.fullmatch(r"[0-9a-fA-F,-]+", cpumask):
                raise AssessmentError(f"invalid cpumask for perf event source: {name}")
        elif cpumask:
            raise AssessmentError(f"nonempty cpumask for unavailable perf event source: {name}")
        if device_state != "present" and device:
            raise AssessmentError(f"nonempty device link for unavailable perf event source: {name}")
        sources[name] = {
            "type_state": type_state,
            "type": source_type,
            "cpumask_state": cpumask_state,
            "cpumask": cpumask if cpumask_state == "present" else None,
            "device_state": device_state,
            "device_link": device if device_state == "present" else None,
        }
    if count != len(sources):
        raise AssessmentError(
            f"perf event source count mismatch: expected {count}, observed {len(sources)}"
        )
    return True, sources


def _status(value: bool | None) -> str:
    return "pass" if value is True else "fail" if value is False else "unknown"


def _source_registered(
    inventory_observed: bool, sources: dict[str, dict[str, Any]], name: str
) -> bool | None:
    if not inventory_observed:
        return None
    source = sources.get(name)
    if source is None:
        return False
    if source["type_state"] != "present":
        return None
    return True


def build_report(source: dict[str, Any]) -> dict[str, Any]:
    banner_match = _kernel_banner_match(source)
    paranoid = _paranoid_value(source)
    inventory_observed, event_sources = _event_sources(source)
    software_registered = _source_registered(inventory_observed, event_sources, "software")
    cpu_registered = _source_registered(inventory_observed, event_sources, "cpu")
    per_task_user_space_not_blanket_denied = None if paranoid is None else True
    cpu_wide_without_capability_allowed = None if paranoid is None else paranoid <= 0
    kernel_sampling_without_capability_allowed = None if paranoid is None else paranoid <= 1
    passive_runtime_prerequisites = (
        None
        if None in (per_task_user_space_not_blanket_denied, software_registered, cpu_registered)
        else bool(per_task_user_space_not_blanket_denied and software_registered and cpu_registered)
    )

    report: dict[str, Any] = {
        "schema": OUTPUT_SCHEMA,
        "tool": {"name": "bench_perf_readiness.py", "version": TOOL_VERSION},
        "source": {
            "schema": source["schema"],
            "capture_sha256": source["capture_sha256"],
            "canonical_sha256": source["canonical_sha256"],
        },
        "observations": {
            "kernel_banner_match": banner_match,
            "perf_event_paranoid": paranoid,
            "cpu_wide_without_capability_allowed_by_v4_1_paranoid_check": cpu_wide_without_capability_allowed,
            "kernel_sampling_without_capability_allowed_by_v4_1_paranoid_check": kernel_sampling_without_capability_allowed,
            "per_task_user_space_not_blanket_denied_by_v4_1_paranoid_checks": per_task_user_space_not_blanket_denied,
            "event_source_inventory_observed": inventory_observed,
            "event_sources": event_sources,
        },
        "gates": [
            {
                "id": "kernel-banner",
                "status": _status(banner_match),
                "observed": banner_match,
                "expected": "4.1.27-abl banner only; exact installed vmlinux identity remains unknown",
            },
            {
                "id": "per-task-policy",
                "status": _status(per_task_user_space_not_blanket_denied),
                "observed": {
                    "perf_event_paranoid": paranoid,
                    "cpu_wide_without_capability_allowed": cpu_wide_without_capability_allowed,
                    "kernel_sampling_without_capability_allowed": kernel_sampling_without_capability_allowed,
                },
                "expected": "in exact Linux v4.1 semantics, values above 0 require a per-task event and values above 1 require kernel exclusion; these checks do not by themselves blanket-deny a per-task user-space-only event",
            },
            {
                "id": "software-event-source",
                "status": _status(software_registered),
                "observed": event_sources.get("software"),
                "expected": "registered software source with readable numeric type",
            },
            {
                "id": "cpu-event-source",
                "status": _status(cpu_registered),
                "observed": event_sources.get("cpu"),
                "expected": "registered CPU hardware source with readable numeric type",
            },
        ],
        "candidate_runtime_gates": {
            "candidate": "V-030 / CVE-2017-6001 perf move-group context race",
            "static_premise": "exact-recovered",
            "passive_policy_and_event_sources_observed": passive_runtime_prerequisites,
            "installed_kernel_exact_identity": None,
            "perf_event_open_syscall_acceptance": None,
            "compatible_software_group_and_hardware_event_acceptance": None,
            "concurrent_move_group_race": None,
            "stale_or_dead_context_use": None,
            "controlled_kernel_memory_corruption": None,
            "privilege_escalation": None,
            "unrestricted_root": None,
            "persistence": None,
        },
        "claim_boundary": {
            "establishes": [
                "classification of a complete canonical passive bench capture",
                "the recorded perf_event_paranoid scalar when present",
                "registered software and CPU perf event sources when their numeric type files were readable",
            ],
            "does_not_establish": [
                "installed vmlinux byte identity from a version banner",
                "perf_event_open syscall acceptance, an accepted event combination, or event scheduling",
                "a race, stale context, crash, corruption, code execution, privilege gain, root, or persistence",
            ],
            "executes_capture_contents": False,
            "contacts_target": False,
            "invokes_perf_event_open": False,
            "creates_or_enables_events": False,
            "emits_event_attributes_trigger_race_payload_or_firmware_bytes": False,
        },
    }
    report["canonical_sha256"] = hashlib.sha256(_canonical_bytes(report)).hexdigest()
    return report


def emit_report(report: dict[str, Any], output: Path) -> None:
    data = json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True).encode("ascii") + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(output, flags, 0o600)
    except OSError as exc:
        raise AssessmentError(f"cannot create output exclusively: {exc}") from exc
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise AssessmentError("short output write")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("report", type=Path, help="completed parsed bench-state JSON")
    parser.add_argument("-o", "--output", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        emit_report(build_report(load_report(args.report)), args.output)
    except AssessmentError as exc:
        raise SystemExit(f"error: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
