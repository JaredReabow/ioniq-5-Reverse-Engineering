#!/usr/bin/env python3
"""Serve a read-only local dashboard for the IONIQ Radxa update media.

The dashboard observes files published by the USB controller.  It never arms
the update media, changes the USB gadget, writes firmware, or hashes payloads.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time
from typing import Callable, Mapping, Sequence
from urllib.parse import urlsplit


DASHBOARD_VERSION = "1.0.7"
API_VERSION = "1.0.0"
API_SCHEMA = "ioniq-radxa-dashboard/v1"
CONTROLLER_STATE_SCHEMA = "ioniq-radxa-usb-state/v4"
PREPARED_CACHE_SCHEMA = "ioniq-radxa-prepared-content/v1"
PREPARED_CACHE_TOOL_VERSION = "1.2.1"
SESSION_SCHEMA = "ioniq-radxa-session/v1"
DEFAULT_STATE_ROOT = Path("/run/ioniq-toctou")
DEFAULT_PERSISTENT_ROOT = Path("/var/lib/ioniq5-update")
DEFAULT_SYSFS_ROOT = Path("/sys")
DEFAULT_PROC_ROOT = Path("/proc")
DEFAULT_SERVICE_NAME = "ioniq-update-media.service"
DEFAULT_WEB_UI = Path(__file__).with_name("WEB_UI_radxa_dashboard.html")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_STATE_BYTES = 2 * 1024 * 1024
MAX_PREPARED_CACHE_BYTES = 1024 * 1024
MAX_PREPARED_CACHE_ENTRIES = 256
MAX_PREPARE_LOG_BYTES = 128 * 1024
MAX_SESSION_BYTES = 64 * 1024
MAX_LOG_BYTES = 512 * 1024
MAX_UI_BYTES = 2 * 1024 * 1024
MAX_PROC_CMDLINE_BYTES = 8192
MAX_LOG_LINES = 120
MAX_LOG_LINE_CHARS = 600
SYSTEMCTL_TIMEOUT_SECONDS = 1.0
CLIENT_STALE_AFTER_SECONDS = 5.0
SAFE_IDENTIFIER_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]*")
NBD_NAME_RE = re.compile(r"nbd[0-9]+")
READ_RE = re.compile(
    r"^(?P<time>[0-9]+(?:\.[0-9]+)?)\s+"
    r"(?P<source>[BR])\s+off=(?P<off>[0-9]+)\s+"
    r"len=(?P<len>[0-9]+)\s+pass=(?P<pass>[0-9]+)\s+"
    r"region=(?P<region>[0-9]+)\s*$"
)
EVENT_RE = re.compile(
    r"(?:^|\s)region@(?P<region>[0-9]+)\s+pass=(?P<pass>[0-9]+)\s+"
    r"(?P<kind>start|switch|end)(?:\s+(?P<body>.*))?$"
)
MONO_RE = re.compile(r"(?:^|\s)mono=(?P<time>[0-9]+(?:\.[0-9]+)?)")
PREPARE_BYTES_RE = re.compile(
    r"\bprepare bytes=(?P<bytes>[0-9]+) total=(?P<total>[0-9]+) file=(?P<file>.+?)\s*$"
)
PREPARE_TOTAL_RE = re.compile(r"\bprepare(?:\s+start)?\s+total=(?P<total>[0-9]+)")
SENSITIVE_RE = re.compile(
    r"(?i)\b(password|passwd|passphrase|psk|secret|token|"
    r"api[_-]?key|private[_-]?key|authorization)\b"
    r"(\s*[:=]\s*)([^\s,;]+)"
)
BEARER_RE = re.compile(r"(?i)\bbearer\s+[^\s,;]+")
URI_USERINFO_RE = re.compile(r"(?i)(https?://)[^/\s@]+@")


class DashboardError(RuntimeError):
    """Raised when the dashboard cannot safely serve its local interface."""


@dataclass(frozen=True)
class DashboardConfig:
    """Filesystem and service coordinates used by the read-only collector."""

    state_root: Path = DEFAULT_STATE_ROOT
    persistent_root: Path = DEFAULT_PERSISTENT_ROOT
    sysfs_root: Path = DEFAULT_SYSFS_ROOT
    proc_root: Path = DEFAULT_PROC_ROOT
    service_name: str = DEFAULT_SERVICE_NAME
    web_ui_path: Path = DEFAULT_WEB_UI
    systemctl: str = "systemctl"


CommandRunner = Callable[[Sequence[str], float], subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class _FileSnapshot:
    text: str
    exists: bool
    size: int
    mtime: float | None
    truncated: bool
    error: str | None = None


def radxa_dashboard_version() -> str:
    """Return the installed dashboard implementation version."""

    return DASHBOARD_VERSION


def radxa_dashboard_api_version() -> str:
    """Return the status API schema compatibility version."""

    return API_VERSION


def _bounded_file(
    path: Path,
    *,
    limit: int,
    tail: bool,
    reject_symlink: bool = True,
) -> _FileSnapshot:
    """Read a bounded regular file without following an untrusted symlink."""

    flags = os.O_RDONLY
    if reject_symlink and hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        return _FileSnapshot("", False, 0, None, False)
    except OSError as exc:
        return _FileSnapshot("", True, 0, None, False, str(exc))
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            return _FileSnapshot("", True, metadata.st_size, metadata.st_mtime, False,
                                 "not a regular file")
        start = max(0, metadata.st_size - limit) if tail else 0
        os.lseek(descriptor, start, os.SEEK_SET)
        payload = os.read(descriptor, max(0, metadata.st_size - start))
        return _FileSnapshot(
            payload.decode("utf-8", "replace"),
            True,
            metadata.st_size,
            metadata.st_mtime,
            start > 0 or len(payload) < metadata.st_size,
        )
    except OSError as exc:
        return _FileSnapshot("", True, 0, None, False, str(exc))
    finally:
        os.close(descriptor)


def _redact(text: str) -> str:
    """Remove credential-shaped values from externally sourced text."""

    text = SENSITIVE_RE.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", text)
    text = BEARER_RE.sub("Bearer [REDACTED]", text)
    text = URI_USERINFO_RE.sub(r"\1[REDACTED]@", text)
    return text


def _safe_line(value: str) -> str:
    """Return one printable, bounded and redacted log line."""

    value = "".join(
        character if character.isprintable() or character == "\t" else "?"
        for character in value
    ).strip()
    value = _redact(value)
    return value[:MAX_LOG_LINE_CHARS]


def _bounded_lines(text: str, limit: int = MAX_LOG_LINES) -> list[str]:
    """Return the newest meaningful log lines in chronological order."""

    lines = [_safe_line(line) for line in text.splitlines() if line.strip()]
    return lines[-limit:]


def _as_mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, dict) else {}


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _as_int(value: object) -> int | None:
    if type(value) is int:
        return value
    return None


def _json_object_without_duplicates(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    """Build a JSON object while rejecting ambiguous duplicate field names."""

    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _strict_json(text: str) -> object:
    return json.loads(text, object_pairs_hook=_json_object_without_duplicates)


def _run_systemctl(config: DashboardConfig, runner: CommandRunner | None) -> dict[str, object]:
    """Collect service health with a short bound and fixed argument list."""

    command = [
        config.systemctl,
        "show",
        config.service_name,
        "--no-pager",
        "--property=LoadState,ActiveState,SubState,UnitFileState,ExecMainPID,StatusText",
    ]
    execute = runner or (
        lambda argv, timeout: subprocess.run(
            list(argv),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "LC_ALL": "C"},
        )
    )
    try:
        result = execute(command, SYSTEMCTL_TIMEOUT_SECONDS)
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "available": False,
            "active": None,
            "state": "unavailable",
            "error": f"service query failed: {_safe_line(str(exc))}",
        }
    values: dict[str, str] = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition("=")
        if separator and key:
            values[key] = value
    active_state = values.get("ActiveState", "unknown")
    return {
        "available": result.returncode == 0,
        "active": active_state == "active" if result.returncode == 0 else None,
        "state": _safe_line(active_state),
        "sub_state": _safe_line(values.get("SubState", "unknown")),
        "load_state": _safe_line(values.get("LoadState", "unknown")),
        "unit_file_state": _safe_line(values.get("UnitFileState", "unknown")),
        "main_pid": _as_int(int(values["ExecMainPID"]))
        if values.get("ExecMainPID", "").isdigit()
        else None,
        "status_text": _safe_line(values.get("StatusText", "")),
        "error": None if result.returncode == 0 else "service query returned an error",
    }


def _read_state(config: DashboardConfig) -> tuple[Mapping[str, object], _FileSnapshot, str | None]:
    """Read only the controller state document and classify basic validity."""

    snapshot = _bounded_file(config.state_root / "state.json", limit=MAX_STATE_BYTES, tail=False)
    if not snapshot.exists:
        return {}, snapshot, None
    if snapshot.error:
        return {}, snapshot, f"runtime state unavailable: {_safe_line(snapshot.error)}"
    try:
        value = json.loads(snapshot.text)
    except (TypeError, ValueError) as exc:
        return {}, snapshot, f"runtime state is invalid JSON: {_safe_line(str(exc))}"
    if not isinstance(value, dict):
        return {}, snapshot, "runtime state is not a JSON object"
    if value.get("schema") != CONTROLLER_STATE_SCHEMA:
        return value, snapshot, "runtime state uses an unsupported schema"
    return value, snapshot, None


def _identity(info: os.stat_result) -> list[int]:
    """Return the controller's exact persisted file-identity tuple."""

    return [
        info.st_dev,
        info.st_ino,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
        info.st_mode,
        info.st_uid,
    ]


def _path_contains_symlink(path: Path) -> bool:
    """Return true when any existing path component is a symlink."""

    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            return False
        except OSError:
            return True
        if stat.S_ISLNK(info.st_mode):
            return True
    return False


def _cache_snapshot(path: Path) -> tuple[_FileSnapshot, str | None]:
    """Read the private metadata cache without following or writing it."""

    if _path_contains_symlink(path):
        return _FileSnapshot("", True, 0, None, False), (
            "prepared-content cache path contains a symlink"
        )
    try:
        before = path.lstat()
    except FileNotFoundError:
        return _FileSnapshot("", False, 0, None, False), None
    except OSError as exc:
        return _FileSnapshot("", True, 0, None, False, str(exc)), (
            f"prepared-content cache is unavailable: {_safe_line(str(exc))}"
        )
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_uid != os.geteuid()
        or stat.S_IMODE(before.st_mode) != 0o600
        or before.st_size > MAX_PREPARED_CACHE_BYTES
    ):
        return _FileSnapshot("", True, before.st_size, before.st_mtime, False), (
            "prepared-content cache must be a private owner-0600 regular file"
        )
    snapshot = _bounded_file(
        path,
        limit=MAX_PREPARED_CACHE_BYTES,
        tail=False,
    )
    if snapshot.error:
        return snapshot, (
            f"prepared-content cache is unavailable: {_safe_line(snapshot.error)}"
        )
    try:
        after = path.lstat()
    except OSError as exc:
        return snapshot, (
            f"prepared-content cache changed while opening: {_safe_line(str(exc))}"
        )
    if _identity(before) != _identity(after):
        return snapshot, "prepared-content cache changed while opening"
    return snapshot, None


def _cache_key(value: object) -> tuple[str, Path, int, int] | None:
    """Validate one cache key while retaining its absolute path privately."""

    if not isinstance(value, str):
        return None
    try:
        parsed = _strict_json(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if (
        not isinstance(parsed, list)
        or len(parsed) != 3
        or not isinstance(parsed[0], str)
        or type(parsed[1]) is not int
        or type(parsed[2]) is not int
    ):
        return None
    path_text = parsed[0]
    offset = parsed[1]
    length = parsed[2]
    if (
        not path_text.startswith("/")
        or "\0" in path_text
        or os.path.normpath(path_text) != path_text
        or offset < 0
        or length < 0
    ):
        return None
    return path_text, Path(path_text), offset, length


def _cache_entry(
    cache_key: object,
    cache_value: object,
) -> tuple[dict[str, object] | None, str | None]:
    """Validate one cache record and compare it with a metadata-only lstat."""

    parsed_key = _cache_key(cache_key)
    if parsed_key is None:
        return None, "cache contains an invalid path/extent key"
    path_text, path, offset, length = parsed_key
    if not isinstance(cache_value, dict):
        return None, "cache entry must be a JSON object"
    expected = cache_value.get("identity")
    digest = cache_value.get("sha256")
    if (
        not isinstance(expected, list)
        or len(expected) != 7
        or any(type(item) is not int or item < 0 for item in expected)
        or not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        return None, "cache entry identity or sha256 is invalid"
    if offset + length > expected[2]:
        return None, "cache entry extent exceeds its recorded file size"
    if _path_contains_symlink(path):
        return {
            "path": path,
            "name": _safe_line(path.name or "unnamed"),
            "offset": offset,
            "length": length,
            "size": expected[2],
            "sha256": digest,
            "current": False,
            "reason": "symlink_path",
        }, None
    try:
        current_info = path.lstat()
    except FileNotFoundError:
        return {
            "path": path,
            "name": _safe_line(path.name or "unnamed"),
            "offset": offset,
            "length": length,
            "size": expected[2],
            "sha256": digest,
            "current": False,
            "reason": "missing",
        }, None
    except OSError:
        return {
            "path": path,
            "name": _safe_line(path.name or "unnamed"),
            "offset": offset,
            "length": length,
            "size": expected[2],
            "sha256": digest,
            "current": False,
            "reason": "unavailable",
        }, None
    if not stat.S_ISREG(current_info.st_mode):
        current = False
        reason = "not_regular"
    elif _identity(current_info) != expected:
        current = False
        reason = "changed"
    elif offset + length > current_info.st_size:
        current = False
        reason = "short_extent"
    else:
        current = True
        reason = "current"
    return {
        "path": path,
        "name": _safe_line(path.name or "unnamed"),
        "offset": offset,
        "length": length,
        "size": expected[2],
        "sha256": digest,
        "current": current,
        "reason": reason,
        "path_text": path_text,
    }, None


def _preparation_artifacts(entries: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Aggregate private extents into basename-only API artifacts."""

    grouped: dict[str, dict[str, object]] = {}
    for entry in entries:
        name = str(entry["name"])
        item = grouped.get(name)
        if item is None:
            item = {
                "label": "Prepared artifact",
                "name": name,
                "size": int(entry["size"]),
                "sha256": str(entry["sha256"]),
                "extents": 1,
                "current": bool(entry["current"]),
            }
            grouped[name] = item
        else:
            item["extents"] = int(item["extents"]) + 1
            item["current"] = bool(item["current"]) and bool(entry["current"])
            if item["sha256"] != entry["sha256"]:
                item["sha256"] = ""
    return list(grouped.values())


def _prepare_progress(log_file: _FileSnapshot) -> tuple[dict[str, object], list[str]]:
    """Parse measured preparation bytes while keeping paths out of the API."""

    if not log_file.exists or log_file.error:
        return {
            "available": False,
            "percent": None,
            "bytes": None,
            "total": None,
            "file": "",
            "basis": "prepare.log unavailable; no synthetic progress",
        }, []
    total: int | None = None
    latest: tuple[int, int, str] | None = None
    display: list[str] = []
    for raw_line in log_file.text.splitlines():
        match = PREPARE_BYTES_RE.search(raw_line)
        if match:
            progress_total = int(match.group("total"))
            progress_bytes = int(match.group("bytes"))
            filename = _safe_line(Path(match.group("file")).name)
            latest = (progress_bytes, progress_total, filename)
            total = progress_total
            display.append(
                f"prepare bytes={progress_bytes} total={progress_total} file={filename}"
            )
            continue
        header = PREPARE_TOTAL_RE.search(raw_line)
        if header:
            total = int(header.group("total"))
            display.append(f"prepare total={total}")
    display = display[-MAX_LOG_LINES:]
    if latest is None:
        percent = 100.0 if total == 0 else None
        return {
            "available": total is not None,
            "percent": percent,
            "bytes": 0 if total is not None else None,
            "total": total,
            "file": "",
            "basis": "prepare.log header only" if total is not None else "no measured prepare progress",
        }, display
    measured, measured_total, filename = latest
    percent = round(min(100.0, measured * 100.0 / measured_total), 2) if measured_total else None
    return {
        "available": True,
        "percent": percent,
        "bytes": measured,
        "total": measured_total,
        "file": filename,
        "basis": "Actual prepare bytes from bounded prepare.log",
    }, display


def radxa_dashboard_preparation_status(
    config: DashboardConfig | None = None,
) -> dict[str, object]:
    """Return metadata-only persistent preparation status."""

    config = config or DashboardConfig()
    cache_path = config.persistent_root / "validation-cache.json"
    prepare_log_path = config.persistent_root / "prepare.log"
    snapshot, cache_error = _cache_snapshot(cache_path)
    prepare_file = _bounded_file(
        prepare_log_path,
        limit=MAX_PREPARE_LOG_BYTES,
        tail=True,
    )
    measured_progress, prepare_lines = _prepare_progress(prepare_file)
    if not snapshot.exists:
        return {
            "status": "missing",
            "cache": {
                "present": False,
                "valid": False,
                "schema": "",
                "tool_version": "",
                "entries": 0,
                "current_entries": 0,
                "changed_entries": 0,
                "changed_names": [],
                "error": None,
            },
            "artifacts": [],
            "progress": measured_progress,
            "log": prepare_lines,
            "detail": "No persistent prepared-content cache exists; run explicit preparation.",
        }
    if cache_error:
        return {
            "status": "invalid",
            "cache": {
                "present": True,
                "valid": False,
                "schema": "",
                "tool_version": "",
                "entries": 0,
                "current_entries": 0,
                "changed_entries": 0,
                "changed_names": [],
                "error": cache_error,
            },
            "artifacts": [],
            "progress": measured_progress,
            "log": prepare_lines,
            "detail": cache_error,
        }
    try:
        value = _strict_json(snapshot.text)
    except (TypeError, ValueError, json.JSONDecodeError):
        value = None
    if (
        not isinstance(value, dict)
        or value.get("schema") != PREPARED_CACHE_SCHEMA
        or value.get("tool_version") != PREPARED_CACHE_TOOL_VERSION
        or not isinstance(value.get("entries"), dict)
    ):
        detail = (
            "Prepared-content cache schema, tool version, or entries are invalid; "
            "run explicit preparation again."
        )
        return {
            "status": "invalid",
            "cache": {
                "present": True,
                "valid": False,
                "schema": _safe_line(_as_text(_as_mapping(value).get("schema"))),
                "tool_version": _safe_line(
                    _as_text(_as_mapping(value).get("tool_version"))
                ),
                "entries": 0,
                "current_entries": 0,
                "changed_entries": 0,
                "changed_names": [],
                "error": detail,
            },
            "artifacts": [],
            "progress": measured_progress,
            "log": prepare_lines,
            "detail": detail,
        }
    entries_value = value["entries"]
    assert isinstance(entries_value, dict)
    if len(entries_value) > MAX_PREPARED_CACHE_ENTRIES:
        detail = (
            f"Prepared-content cache exceeds the bounded {MAX_PREPARED_CACHE_ENTRIES}-entry "
            "status budget."
        )
        return {
            "status": "invalid",
            "cache": {
                "present": True,
                "valid": False,
                "schema": PREPARED_CACHE_SCHEMA,
                "tool_version": PREPARED_CACHE_TOOL_VERSION,
                "entries": len(entries_value),
                "current_entries": 0,
                "changed_entries": 0,
                "changed_names": [],
                "error": detail,
            },
            "artifacts": [],
            "progress": measured_progress,
            "log": prepare_lines,
            "detail": detail,
        }
    valid_entries: list[dict[str, object]] = []
    invalid_entries = 0
    for key, item in entries_value.items():
        entry, entry_error = _cache_entry(key, item)
        if entry_error:
            invalid_entries += 1
        elif entry is not None:
            valid_entries.append(entry)
    if invalid_entries:
        detail = (
            f"Prepared-content cache contains {invalid_entries} invalid entry or entries; "
            "run explicit preparation again."
        )
        return {
            "status": "invalid",
            "cache": {
                "present": True,
                "valid": False,
                "schema": PREPARED_CACHE_SCHEMA,
                "tool_version": PREPARED_CACHE_TOOL_VERSION,
                "entries": len(entries_value),
                "current_entries": sum(bool(item["current"]) for item in valid_entries),
                "changed_entries": sum(not bool(item["current"]) for item in valid_entries),
                "changed_names": sorted(
                    {str(item["name"]) for item in valid_entries if not item["current"]}
                ),
                "error": detail,
            },
            "artifacts": _preparation_artifacts(valid_entries),
            "progress": measured_progress,
            "log": prepare_lines,
            "detail": detail,
        }
    # Preparation retains old extent keys when a file changes size. A current
    # whole-file record supersedes stale extents of that exact path; a current
    # partial extent alone must never hide an invalid whole-file identity.
    current_whole_files = {
        item["path"] for item in valid_entries
        if item["current"] and item["offset"] == 0 and item["length"] == item["size"]
    }
    valid_entries = [
        item for item in valid_entries
        if item["current"] or item["path"] not in current_whole_files
    ]
    if not valid_entries:
        detail = "Prepared-content cache is empty; run explicit preparation."
        status = "invalid"
    else:
        current_entries = sum(bool(item["current"]) for item in valid_entries)
        changed_entries = len(valid_entries) - current_entries
        if changed_entries:
            detail = (
                f"{changed_entries} prepared file identity or identities changed; "
                "run explicit preparation again."
            )
            status = "changed"
        else:
            detail = (
                "Prepared-content cache is current. Paths and files were checked "
                "with metadata only; this is a trusted-local cache, not a fresh hash."
            )
            status = "current"
    if status == "current":
        progress = {
            "available": True,
            "percent": 100.0,
            "bytes": None,
            "total": None,
            "file": "",
            "basis": "Current persistent prepared-content cache",
        }
    else:
        progress = measured_progress
    return {
        "status": status,
        "cache": {
            "present": True,
            "valid": status != "invalid",
            "schema": PREPARED_CACHE_SCHEMA,
            "tool_version": PREPARED_CACHE_TOOL_VERSION,
            "entries": len(valid_entries),
            "superseded_entries": len(entries_value) - len(valid_entries),
            "current_entries": sum(bool(item["current"]) for item in valid_entries),
            "changed_entries": sum(not bool(item["current"]) for item in valid_entries),
            "changed_names": sorted(
                {str(item["name"]) for item in valid_entries if not item["current"]}
            ),
            "error": None if status != "invalid" else detail,
        },
        "artifacts": _preparation_artifacts(valid_entries),
        "progress": progress,
        "log": prepare_lines,
        "detail": detail,
    }


def _session_status(config: DashboardConfig) -> dict[str, object]:
    """Read the lightweight boot/session journal without mutating it."""

    path = config.persistent_root / "session.json"
    snapshot = _bounded_file(path, limit=MAX_SESSION_BYTES, tail=False)
    if not snapshot.exists:
        return {
            "status": "missing",
            "state": "",
            "boot_relation": "none",
            "updated_at": "",
            "interrupted_previous_session": False,
            "error": None,
        }
    if snapshot.error:
        return {
            "status": "invalid",
            "state": "",
            "boot_relation": "unknown",
            "updated_at": "",
            "interrupted_previous_session": False,
            "error": f"session journal unavailable: {_safe_line(snapshot.error)}",
        }
    try:
        value = _strict_json(snapshot.text)
    except (TypeError, ValueError, json.JSONDecodeError):
        value = None
    boot_file = _bounded_file(
        config.proc_root / "sys" / "kernel" / "random" / "boot_id",
        limit=128,
        tail=False,
    )
    current_boot = boot_file.text.strip() if boot_file.exists and not boot_file.error else ""
    if (
        not isinstance(value, dict)
        or value.get("schema") != SESSION_SCHEMA
        or not isinstance(value.get("boot_id"), str)
        or value.get("state") not in {"arm_requested", "armed", "stopped", "arm_failed"}
        or not isinstance(value.get("updated_at"), str)
    ):
        return {
            "status": "invalid",
            "state": "",
            "boot_relation": "unknown",
            "updated_at": "",
            "interrupted_previous_session": False,
            "error": "session journal schema or fields are invalid",
        }
    try:
        updated = datetime.fromisoformat(value["updated_at"].replace("Z", "+00:00"))
    except ValueError:
        return {
            "status": "invalid",
            "state": "",
            "boot_relation": "unknown",
            "updated_at": "",
            "interrupted_previous_session": False,
            "error": "session journal timestamp is invalid",
        }
    if not current_boot:
        relation = "unknown"
    elif value["boot_id"] == current_boot:
        relation = "current"
    else:
        relation = "previous"
    state = str(value["state"])
    return {
        "status": relation,
        "state": state,
        "boot_relation": relation,
        "updated_at": updated.isoformat(),
        "interrupted_previous_session": (
            relation == "previous" and state in {"arm_requested", "armed"}
        ),
        "error": None,
    }


def _artifact(record: object, label: str) -> dict[str, object] | None:
    """Project one controller file record without exposing its directory."""

    value = _as_mapping(record)
    path_text = _as_text(value.get("path"))
    sha256 = _as_text(value.get("sha256"))
    size = _as_int(value.get("size"))
    if not path_text or not sha256 or size is None:
        return None
    return {
        "label": label,
        "name": _safe_line(Path(path_text).name),
        "size": max(0, size),
        "sha256": sha256 if re.fullmatch(r"[0-9a-fA-F]{64}", sha256) else "",
    }


def _artifacts(state: Mapping[str, object]) -> list[dict[str, object]]:
    """Return the artifact identities published by the controller."""

    content = _as_mapping(state.get("bound_content"))
    result: list[dict[str, object]] = []
    for key, label in (
        ("baseline", "Baseline image"),
        ("manifest", "Serve manifest"),
        ("plugin", "Dynamic media backend"),
        ("regions", "Region policy"),
    ):
        item = _artifact(content.get(key), label)
        if item:
            result.append(item)
    replacements = content.get("replacements")
    if isinstance(replacements, list):
        for index, replacement in enumerate(replacements, start=1):
            record = _as_mapping(replacement).get("replacement")
            item = _artifact(record, f"Replacement {index}")
            if item:
                result.append(item)
    return result


def _regions(state: Mapping[str, object]) -> list[dict[str, object]]:
    """Project replacement-region metadata from bound controller state."""

    content = _as_mapping(state.get("bound_content"))
    replacements = content.get("replacements")
    if not isinstance(replacements, list):
        return []
    result: list[dict[str, object]] = []
    for item in replacements:
        value = _as_mapping(item)
        offset = _as_int(value.get("offset"))
        length = _as_int(value.get("length"))
        switch_after = _as_int(value.get("switch_after_pass"))
        mode = _as_text(value.get("mode"))
        if offset is None or length is None or length <= 0:
            continue
        result.append(
            {
                "offset": offset,
                "length": length,
                "switch_after_pass": switch_after or 0,
                "mode": _safe_line(mode),
            }
        )
    return result


def _backend_log_paths(
    state: Mapping[str, object], state_root: Path
) -> tuple[Path | None, Path | None, str | None]:
    """Read configured log paths from nbdkit argv without trusting arbitrary paths."""

    command = state.get("nbdkit_command")
    if not isinstance(command, list):
        return None, None, "controller state does not publish nbdkit log paths"
    root = state_root.resolve()
    found: dict[str, Path] = {}
    for argument in command:
        if not isinstance(argument, str):
            continue
        key, separator, value = argument.partition("=")
        if not separator or key not in {"log", "reads"} or not value:
            continue
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            continue
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError:
            continue
        found[key] = resolved
    missing = [key for key in ("log", "reads") if key not in found]
    note = "controller state omits: " + ", ".join(missing) if missing else None
    return found.get("log"), found.get("reads"), note


def _connection(
    name: str,
    status: str,
    value: str,
    detail: str,
) -> dict[str, str]:
    return {"name": name, "status": status, "value": value, "detail": detail}


def _process_status(
    state: Mapping[str, object], proc_root: Path
) -> tuple[str, str]:
    pid = _as_int(state.get("nbdkit_pid"))
    if pid is None or pid <= 0:
        return "waiting", "Backend PID not published"
    cmdline = _bounded_file(
        proc_root / str(pid) / "cmdline",
        limit=MAX_PROC_CMDLINE_BYTES,
        tail=False,
    )
    if not cmdline.exists:
        return "error", "Published nbdkit process is absent"
    if cmdline.error:
        return "warning", "Published nbdkit process could not be inspected"
    arguments = [item for item in cmdline.text.split("\0") if item]
    plugin = _as_text(state.get("nbdkit_plugin"))
    if plugin and plugin not in arguments:
        return "error", "Published PID belongs to a different process"
    return "healthy", f"nbdkit running as PID {pid}"


def _usb_status(
    state: Mapping[str, object], sysfs_root: Path
) -> tuple[str, str]:
    udc = _as_text(state.get("udc"))
    gadget = _as_text(state.get("gadget_name"))
    if not SAFE_IDENTIFIER_RE.fullmatch(udc):
        return "waiting", "UDC not selected"
    if not SAFE_IDENTIFIER_RE.fullmatch(gadget):
        return "warning", "USB gadget identity is unavailable"
    udc_state = _bounded_file(sysfs_root / "class" / "udc" / udc / "state", limit=128, tail=False)
    binding_path = (
        sysfs_root
        / "kernel"
        / "config"
        / "usb_gadget"
        / gadget
        / "UDC"
    )
    binding = _bounded_file(binding_path, limit=256, tail=False)
    bound_to = binding.text.strip()
    if bound_to == udc:
        state_text = _safe_line(udc_state.text.strip() or "bound")
        return "healthy", f"Bound to {udc} ({state_text})"
    if binding.exists:
        return "warning", "USB gadget is unbound"
    return "waiting", "USB gadget is not present"


def _nbd_status(
    state: Mapping[str, object], sysfs_root: Path
) -> tuple[str, str]:
    name = _as_text(state.get("nbd_name"))
    if not NBD_NAME_RE.fullmatch(name):
        return "waiting", "NBD device not published"
    pid = _bounded_file(sysfs_root / "block" / name / "pid", limit=128, tail=False)
    if pid.exists and pid.text.strip():
        return "healthy", f"{name} attached (pid {_safe_line(pid.text.strip())})"
    if state.get("nbd_attached") is True:
        return "error", f"{name} is recorded attached but live pid is absent"
    return "waiting", f"{name} not attached"


def _parse_events(lines: Sequence[str]) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for index, line in enumerate(lines):
        match = EVENT_RE.search(line)
        if not match:
            continue
        event: dict[str, object] = {
            "index": index,
            "region": int(match.group("region")),
            "pass": int(match.group("pass")),
            "kind": match.group("kind"),
        }
        mono = MONO_RE.search(line)
        if mono:
            event["time"] = float(mono.group("time"))
        body = match.group("body") or ""
        for key in ("reads", "baseline_bytes", "replacement_bytes"):
            value = re.search(rf"\b{key}=([0-9]+)", body)
            if value:
                event[key] = int(value.group(1))
        duration = re.search(r"\bduration=([0-9]+(?:\.[0-9]+)?)s", body)
        if duration:
            event["duration"] = float(duration.group(1))
        source = re.search(r"\bsource=([A-Za-z_]+)", body)
        if source:
            event["source"] = source.group(1)
        mode = re.search(r"\bmode=([A-Za-z_]+)", body)
        if mode:
            event["mode"] = mode.group(1)
        events.append(event)
    return events


def _parse_reads(lines: Sequence[str]) -> list[dict[str, object]]:
    reads: list[dict[str, object]] = []
    for line in lines:
        match = READ_RE.match(line)
        if not match:
            continue
        reads.append(
            {
                "time": float(match.group("time")),
                "source": match.group("source"),
                "offset": int(match.group("off")),
                "length": int(match.group("len")),
                "pass": int(match.group("pass")),
                "region": int(match.group("region")),
            }
        )
    return reads


def _union_bytes(intervals: Sequence[tuple[int, int]]) -> int:
    """Return byte coverage for possibly duplicated and overlapping reads."""

    if not intervals:
        return 0
    ordered = sorted(intervals)
    total = 0
    start, end = ordered[0]
    for next_start, next_end in ordered[1:]:
        if next_start <= end:
            end = max(end, next_end)
        else:
            total += end - start
            start, end = next_start, next_end
    return total + end - start


def _progress(
    regions: Sequence[Mapping[str, object]],
    events: Sequence[Mapping[str, object]],
    reads: Sequence[Mapping[str, object]],
    now_monotonic: float,
) -> dict[str, object]:
    """Calculate honest USB-read coverage for each configured region."""

    region_progress: list[dict[str, object]] = []
    for region in regions:
        offset = int(region["offset"])
        length = int(region["length"])
        end = offset + length
        matching_events = [event for event in events if event.get("region") == offset]
        matching_reads = [item for item in reads if item.get("region") == offset]
        pass_values = [int(item["pass"]) for item in matching_events]
        pass_values.extend(int(item["pass"]) for item in matching_reads)
        current_pass = max(pass_values) if pass_values else 0
        current_reads = [item for item in matching_reads if item["pass"] == current_pass]
        current_events = [item for item in matching_events if item["pass"] == current_pass]
        intervals: list[tuple[int, int]] = []
        for item in current_reads:
            start = max(offset, int(item["offset"]))
            finish = min(end, int(item["offset"]) + int(item["length"]))
            if finish > start:
                intervals.append((start, finish))
        covered = min(length, _union_bytes(intervals))
        finished = any(item.get("kind") == "end" for item in current_events)
        switched = any(item.get("kind") == "switch" for item in current_events)
        percent: float | None
        if finished:
            percent = 100.0
        elif current_reads:
            percent = round((covered / length) * 100.0, 2)
        else:
            percent = None
        times = [float(item["time"]) for item in current_reads]
        duration = max(times) - min(times) if len(times) > 1 else None
        raw_bytes = sum(int(item["length"]) for item in current_reads)
        read_rate = raw_bytes / duration if duration and duration > 0 else None
        last_end = max(
            (
                int(item["baseline_bytes"]) + int(item["replacement_bytes"])
                for item in current_events
                if item.get("kind") == "end"
            ),
            default=0,
        )
        latest_age = max(0.0, now_monotonic - max(times)) if times else None
        replacement = sum(1 for item in current_reads if item["source"] == "R")
        baseline = sum(1 for item in current_reads if item["source"] == "B")
        region_progress.append(
            {
                "offset": offset,
                "length": length,
                "pass": current_pass,
                "percent": percent,
                "measured_bytes": covered,
                "raw_read_bytes": raw_bytes,
                "end_reported_bytes": last_end,
                "read_rate_bytes_per_s": round(read_rate, 1) if read_rate else None,
                "latest_read_age_seconds": round(latest_age, 2)
                if latest_age is not None
                else None,
                "reads": len(current_reads),
                "baseline_reads": baseline,
                "replacement_reads": replacement,
                "latest_source": current_reads[-1]["source"] if current_reads else "waiting",
                "switched": switched,
                "pass_finished": finished,
                "switch_after_pass": int(region.get("switch_after_pass", 0)),
                "mode": _safe_line(str(region.get("mode", ""))),
                "progress_basis": "USB read-byte coverage in the bounded log tail",
            }
        )
    current = max(
        region_progress,
        key=lambda item: (
            int(item["pass"]),
            float(item["latest_read_age_seconds"] or 10**9)
            * -1,
        ),
        default=None,
    )
    total_bytes = sum(int(item["length"]) for item in region_progress)
    measured_bytes = sum(int(item["measured_bytes"]) for item in region_progress)
    overall_percent = (
        round((measured_bytes / total_bytes) * 100.0, 2)
        if total_bytes and any(item["percent"] is not None for item in region_progress)
        else None
    )
    return {
        "available": current is not None,
        "percent": overall_percent,
        "measured_bytes": measured_bytes,
        "total_bytes": total_bytes,
        "pass": current["pass"] if current else 0,
        "pass_finished": current["pass_finished"] if current else False,
        "latest_source": current["latest_source"] if current else "waiting",
        "read_rate_bytes_per_s": current["read_rate_bytes_per_s"] if current else None,
        "latest_read_age_seconds": current["latest_read_age_seconds"] if current else None,
        "regions": region_progress,
        "car_write_status": "unknown",
        "car_write_detail": (
            "The dashboard can measure Radxa-to-car USB reads. It cannot observe "
            "the head unit's validation, internal write, or completion state."
        ),
    }


def radxa_dashboard_collect_status(
    config: DashboardConfig | None = None,
    *,
    command_runner: CommandRunner | None = None,
    now_monotonic: Callable[[], float] = time.monotonic,
    now_wall: Callable[[], datetime] | None = None,
) -> dict[str, object]:
    """Collect one bounded read-only dashboard status snapshot."""

    config = config or DashboardConfig()
    wall = now_wall() if now_wall else datetime.now(timezone.utc)
    monotonic_now = now_monotonic()
    errors: list[str] = []
    state, state_file, state_error = _read_state(config)
    preparation = radxa_dashboard_preparation_status(config)
    session_journal = _session_status(config)
    if state_error:
        errors.append(state_error)
    if preparation["status"] == "invalid":
        errors.append(str(_as_mapping(preparation.get("cache")).get("error")))
    elif preparation["status"] == "changed":
        errors.append(str(preparation["detail"]))
    if session_journal.get("error"):
        errors.append(str(session_journal["error"]))
    service = _run_systemctl(config, command_runner)
    if service.get("error"):
        errors.append(str(service["error"]))

    process_health, process_detail = (
        _process_status(state, config.proc_root) if state else ("waiting", "No runtime state")
    )
    nbd_health, nbd_detail = (
        _nbd_status(state, config.sysfs_root) if state else ("waiting", "No runtime state")
    )
    usb_health, usb_detail = (
        _usb_status(state, config.sysfs_root) if state else ("waiting", "No runtime state")
    )

    log_path, read_path, log_path_note = _backend_log_paths(state, config.state_root)
    if log_path_note and state:
        errors.append(log_path_note)
    event_file = (
        _bounded_file(log_path, limit=MAX_LOG_BYTES, tail=True) if log_path else None
    )
    read_file = (
        _bounded_file(read_path, limit=MAX_LOG_BYTES, tail=True) if read_path else None
    )
    event_lines = _bounded_lines(event_file.text) if event_file else []
    read_lines = _bounded_lines(read_file.text) if read_file else []
    events = _parse_events(event_lines)
    reads = _parse_reads(read_lines)
    if event_file and event_file.error:
        errors.append(f"event log unavailable: {_safe_line(event_file.error)}")
    if read_file and read_file.error:
        errors.append(f"read log unavailable: {_safe_line(read_file.error)}")

    regions = _regions(state)
    progress = _progress(regions, events, reads, monotonic_now)
    cleanup = _as_mapping(state.get("cleanup"))
    cleanup_active = any(value is True for value in cleanup.values())
    reconciliation = state.get("reconciliation_required")
    service_active = service.get("active") is True
    service_starting = service.get("state") in {"activating", "reloading"}
    service_current = service_active or service_starting
    state_exists = state_file.exists
    runtime_interrupted = state_exists and (
        not service_current or cleanup_active or bool(reconciliation)
    )
    previous_session_interrupted = (
        not state_exists
        and session_journal.get("boot_relation") == "previous"
        and session_journal.get("state") in {"arm_requested", "armed"}
    )
    current_session_unresolved = (
        not state_exists
        and session_journal.get("boot_relation") == "current"
        and session_journal.get("state") in {"arm_requested", "armed"}
    )
    interrupted = runtime_interrupted or previous_session_interrupted
    cache_current = preparation["status"] == "current"
    runtime_status = (
        "prepared"
        if state and service_current and not runtime_interrupted
        else "interrupted"
        if state_exists
        else "not_armed"
    )
    state_age = (
        max(0.0, time.time() - state_file.mtime)
        if state_file.mtime is not None
        else None
    )

    activity = progress.get("latest_read_age_seconds")
    if runtime_interrupted:
        headline = "Interrupted runtime state preserved"
        phase = "Controller state is inactive; no automatic reuse or re-arm occurs"
        level = "warning"
    elif previous_session_interrupted:
        headline = "Previous boot session did not stop cleanly"
        phase = (
            "The persistent journal records an arm request without current runtime "
            "state. The dashboard will not auto-arm; car-side result remains unknown."
        )
        level = "warning"
    elif current_session_unresolved:
        headline = "Session journal expects media that is not running"
        phase = "No current runtime state exists; no automatic re-arm or write claim is made"
        level = "warning"
    elif not state and cache_current:
        headline = "Prepared media ready; not armed"
        phase = (
            "The persistent validation cache and file identities are current. "
            "Controller runtime is absent and no car update is inferred."
        )
        level = "waiting"
    elif (
        not state
        and preparation["progress"]["available"]
        and preparation["progress"]["percent"] is not None
        and preparation["progress"]["percent"] < 100
    ):
        headline = "Preparation progress observed"
        phase = (
            "Measured bytes come from prepare.log. The controller is not armed and "
            "the dashboard does not infer that preparation is still running."
        )
        level = "waiting"
    elif not state and preparation["status"] == "changed":
        headline = "Prepared file identities changed"
        phase = "Run explicit preparation again; the dashboard will not rebuild or hash on startup"
        level = "warning"
    elif not state and preparation["status"] == "invalid":
        headline = "Prepared-content cache needs repair"
        phase = "Run explicit preparation again; no automatic cache rewrite occurs"
        level = "warning"
    elif not state:
        headline = "Prepared media is not available"
        phase = "Run explicit preparation once; the dashboard never builds, hashes, or arms automatically"
        level = "waiting"
    elif service_starting:
        headline = "Controller is preparing the USB media"
        phase = "Systemd is activating the controller; no completion is inferred"
        level = "waiting"
    elif not service_active:
        headline = "Controller service is not active"
        phase = "Published state is stale until the controller publishes a fresh session"
        level = "warning"
    elif usb_health != "healthy":
        headline = "USB chain is not connected"
        phase = "Backend and runtime state are visible; waiting for a bound USB gadget"
        level = "waiting"
    elif activity is not None and activity <= CLIENT_STALE_AFTER_SECONDS:
        headline = "Car is reading the prepared USB media"
        phase = f"Measured USB read pass {progress['pass']}; car-side write remains unknown"
        level = "active"
    elif progress.get("pass_finished"):
        headline = "USB read pass finished"
        phase = "The head unit's ingestion and write result are not observable here"
        level = "waiting"
    else:
        headline = "USB media is ready; waiting for car reads"
        phase = "No car-side flash or completion claim is made from elapsed time"
        level = "waiting"

    connections = [
        _connection(
            "Controller service",
            "healthy"
            if service_active
            else "waiting"
            if service_starting
            else "error"
            if state_exists
            else "waiting",
            str(service.get("state", "unknown")),
            config.service_name,
        ),
        _connection("Backend process", process_health, process_detail, "nbdkit ownership probe"),
        _connection("NBD transport", nbd_health, nbd_detail, "Controller block backend"),
        _connection("USB output", usb_health, usb_detail, "Car-facing gadget binding"),
        _connection(
            "Event log",
            "healthy" if event_file and event_file.exists and not event_file.error else "warning",
            f"{len(event_lines)} recent lines",
            "Bounded and credential-redacted",
        ),
        _connection(
            "Read log",
            "healthy" if read_file and read_file.exists and not read_file.error else "warning",
            f"{len(read_lines)} recent lines",
            "Actual byte-offset observations",
        ),
        _connection(
            "Preparation cache",
            "healthy"
            if preparation["status"] == "current"
            else "warning"
            if preparation["status"] in {"changed", "invalid"}
            else "waiting",
            str(preparation["status"]),
            str(preparation["detail"]),
        ),
        _connection(
            "Session journal",
            "healthy"
            if session_journal["boot_relation"] == "current"
            else "warning"
            if session_journal["boot_relation"] == "previous"
            or session_journal["status"] == "invalid"
            else "waiting",
            (
                f"{session_journal['boot_relation']}: {session_journal['state']}"
                if session_journal["state"]
                else str(session_journal["status"])
            ),
            "Does not prove car-side write; previous armed state never auto-arms",
        ),
    ]
    timeline = [
        {
            "label": "Controller",
            "status": "done"
            if service_active
            else "waiting"
            if service_starting
            else "error"
            if state_exists
            else "waiting",
            "detail": str(service.get("state", "unknown")),
        },
        {
            "label": "Prepared media",
            "status": "done"
            if state or cache_current
            else "warning"
            if preparation["status"] in {"changed", "invalid"}
            else "waiting",
            "detail": (
                f"{len(_artifacts(state))} runtime identities published"
                if state
                else f"{preparation['cache']['current_entries']} cached identities current"
                if cache_current
                else str(preparation["detail"])
            ),
        },
        {
            "label": "USB chain",
            "status": "done" if usb_health == "healthy" and nbd_health == "healthy" else "warning",
            "detail": usb_detail,
        },
        {
            "label": "Car read",
            "status": "active"
            if activity is not None and activity <= CLIENT_STALE_AFTER_SECONDS
            else "done"
            if progress.get("pass_finished")
            else "waiting",
            "detail": "Measured from nbdkit read offsets",
        },
        {
            "label": "Car write result",
            "status": "unknown",
            "detail": "Not observable over the storage link",
        },
    ]

    return {
        "schema": API_SCHEMA,
        "dashboard_version": radxa_dashboard_version(),
        "api_version": radxa_dashboard_api_version(),
        "generated_at": wall.isoformat(),
        "client_stale_after_seconds": CLIENT_STALE_AFTER_SECONDS,
        "headline": headline,
        "phase": phase,
        "level": level,
        "errors": list(dict.fromkeys(errors)),
        "service": service,
        "runtime": {
            "status": runtime_status,
            "interrupted": interrupted,
            "interrupted_previous_session": previous_session_interrupted,
            "journal_relation": session_journal.get("boot_relation"),
            "journal_state": session_journal.get("state"),
            "state_age_seconds": round(state_age, 2) if state_age is not None else None,
            "reconciliation_required": bool(reconciliation),
            "cleanup_started": cleanup_active,
            "controller_version": _safe_line(_as_text(state.get("tool_version"))),
        },
        "preparation": preparation,
        "connections": connections,
        "timeline": timeline,
        "progress": progress,
        "artifacts": _artifacts(state) if state else preparation["artifacts"],
        "logs": {
            "event": event_lines,
            "read": read_lines,
            "prepare": preparation["log"],
            "event_truncated": bool(event_file and event_file.truncated),
            "read_truncated": bool(read_file and read_file.truncated),
            "bounded_lines": MAX_LOG_LINES,
            "redaction": "Credential-shaped values are removed before serving.",
        },
    }


class _DashboardHandler(BaseHTTPRequestHandler):
    """Serve the standalone UI and one read-only JSON status endpoint."""

    server_version = f"IoniqRadxaDashboard/{DASHBOARD_VERSION}"
    protocol_version = "HTTP/1.1"
    dashboard_config: DashboardConfig
    status_provider: Callable[[], dict[str, object]]

    def _headers(self, status: HTTPStatus, content_type: str, length: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; connect-src 'self'; "
            "img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'",
        )
        self.end_headers()

    def _send(self, status: HTTPStatus, content_type: str, payload: bytes) -> None:
        self._headers(status, content_type, len(payload))
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _json(self, status: HTTPStatus, value: object) -> None:
        payload = (json.dumps(value, sort_keys=True) + "\n").encode("utf-8")
        self._send(status, "application/json; charset=utf-8", payload)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        """Serve only the UI and read-only status endpoint."""

        path = urlsplit(self.path).path
        if path in {"/", "/index.html", "/WEB_UI_radxa_dashboard.html"}:
            ui = _bounded_file(
                self.dashboard_config.web_ui_path,
                limit=MAX_UI_BYTES,
                tail=False,
                reject_symlink=False,
            )
            if not ui.exists or ui.error:
                self._json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "dashboard UI unavailable"})
                return
            self._send(HTTPStatus.OK, "text/html; charset=utf-8", ui.text.encode("utf-8"))
            return
        if path == "/api/status":
            try:
                payload = self.status_provider()
            except Exception:
                self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "status collection failed"})
                return
            self._json(HTTPStatus.OK, payload)
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        """Serve GET headers without writing the body."""

        self.do_GET()

    def _read_only(self) -> None:
        self._json(
            HTTPStatus.METHOD_NOT_ALLOWED,
            {"error": "dashboard is read-only"},
        )

    do_POST = _read_only
    do_PUT = _read_only
    do_PATCH = _read_only
    do_DELETE = _read_only

    def log_message(self, fmt: str, *args: object) -> None:
        """Write a bounded request log without query strings."""

        path = urlsplit(self.path).path
        print(f"dashboard request {self.command} {path} {fmt % args}", flush=True)


def radxa_dashboard_create_server(
    config: DashboardConfig | None = None,
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> ThreadingHTTPServer:
    """Create a loopback-only dashboard server."""

    if host != DEFAULT_HOST:
        raise ValueError("dashboard must bind exclusively to 127.0.0.1")
    config = config or DashboardConfig()
    handler = type(
        "BoundDashboardHandler",
        (_DashboardHandler,),
        {
            "dashboard_config": config,
            "status_provider": staticmethod(
                lambda: radxa_dashboard_collect_status(config)
            ),
        },
    )
    server = ThreadingHTTPServer((host, port), handler)
    server.daemon_threads = True
    return server


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--state-root", type=Path, default=DEFAULT_STATE_ROOT)
    parser.add_argument("--sysfs-root", type=Path, default=DEFAULT_SYSFS_ROOT)
    parser.add_argument("--proc-root", type=Path, default=DEFAULT_PROC_ROOT)
    parser.add_argument("--check", action="store_true", help="print one status snapshot")
    return parser


def radxa_dashboard_main(argv: Sequence[str] | None = None) -> int:
    """Run the dashboard server or one read-only status check."""

    args = _parser().parse_args(argv)
    config = DashboardConfig(
        state_root=args.state_root,
        sysfs_root=args.sysfs_root,
        proc_root=args.proc_root,
    )
    print(
        f"Radxa dashboard {radxa_dashboard_version()} "
        f"(API {radxa_dashboard_api_version()})",
        flush=True,
    )
    if args.check:
        print(json.dumps(radxa_dashboard_collect_status(config), indent=2, sort_keys=True))
        return 0
    server = radxa_dashboard_create_server(config, port=args.port)
    print(f"Listening on http://{DEFAULT_HOST}:{args.port}", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(radxa_dashboard_main())
