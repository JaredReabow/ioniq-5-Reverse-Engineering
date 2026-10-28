"""Boundary scan for live secrets and visibility-sensitive identifiers.

Findings never carry the matched text: reports name the file, line, and
category only, so a scan cannot itself leak the value it found.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from . import common

TEXT_SUFFIXES = frozenset(
    {".md", ".json", ".txt", ".yaml", ".yml", ".toml", ".csv", ".tsv", ".gitignore"}
)
PUBLIC_TEXT_SUFFIXES = TEXT_SUFFIXES | frozenset(
    {".py", ".sh", ".asm", ".log", ".java", ".c", ".s", ".inf", ".update", ".qml", ".cmd", ".cmds"}
)
PUBLIC_RAW_SUFFIXES = frozenset({
    ".zip", ".gz", ".dlt", ".dat", ".dump", ".core", ".img", ".qcow2",
    ".vmdk", ".iso", ".bin", ".so", ".o", ".tar", ".tgz", ".xz", ".zst",
})
PUBLIC_PERSONAL_HOME = re.compile(r"/Users/(?!researcher/|USER/|example/)[^/\s]+/")
PROHIBITED_SUFFIXES = frozenset(
    {
        ".pem",
        ".key",
        ".p12",
        ".pfx",
        ".mobileprovision",
        ".jks",
        ".keystore",
    }
)
# Public or reserved addresses that are provenance, not personal identifiers.
EMAIL_ALLOWLIST = (
    "users.noreply.github.com",
    "noreply.github.com",
    "example.com",
    "example.org",
    "example.net",
)
EXCLUDED_PARTS = frozenset({"kona_research", ".git", "tests"})

SECRET_PATTERNS = (
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("api-key", re.compile(r"\b(?:sk|rk)-[A-Za-z0-9]{20,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("bearer-token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}")),
    (
        "credential-assignment",
        re.compile(r"\b(?:password|passwd|passphrase|secret)\b\s*[:=]\s*[\"']?[^\s\"'`]{6,}", re.I),
    ),
)
PUBLIC_CODE_CREDENTIAL = re.compile(
    r"\b(?:password|passwd|passphrase|secret)\b\s*[:=]\s*['\"][^'\"\s]{6,}['\"]",
    re.I,
)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
VIN_PATTERN = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
MAX_FINDINGS = 200


def privacy_scope_files(root: Path, *, tracked_only: bool = False) -> list[Path]:
    """Return Ioniq-owned files in scope; public mode inspects Git's index."""
    root = Path(root)
    files: list[Path] = []
    if not root.is_dir():
        return files
    if tracked_only and (root / ".git").exists():
        paths = subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "-z", "--cached"]
        ).decode("utf-8").split("\0")
        # Scan the entire public index, including VM reproduction sources.
        # A new top-level folder must not silently bypass privacy checks.
        return [
            root / path
            for path in paths
            if path and not set(Path(path).parts) & EXCLUDED_PARTS
        ]
    for path in sorted(root.iterdir()):
        if path.is_file():
            files.append(path)
    for name in ("evidence", "council", "tools"):
        directory = root / name
        if directory.is_dir():
            files.extend(sorted(item for item in directory.rglob("*") if item.is_file()))
    scoped = []
    for path in files:
        parts = set(path.relative_to(root).parts)
        if parts & EXCLUDED_PARTS:
            continue
        scoped.append(path)
    return scoped


def privacy_email_allowed(address: str) -> bool:
    """True for reserved or public no-reply domains used as provenance."""
    domain = address.rsplit("@", 1)[-1].lower()
    return any(domain == allowed or domain.endswith("." + allowed) for allowed in EMAIL_ALLOWLIST)


def privacy_vin_like(token: str) -> bool:
    """Heuristic: a 17-character token mixing letters and digits (VIN shape)."""
    if not re.search(r"[A-Z]", token) or not re.search(r"[0-9]", token):
        return False
    return True


def privacy_scan(root: Path) -> dict:
    """Reject live secrets while reporting identifiers without exposing values."""
    root = Path(root)
    public_mode = (root / "PUBLIC-RELEASE.md").is_file()
    findings: list[dict] = []
    scanned = 0
    truncated = False

    def add(path: Path, category: str, severity: str, line: int | None = None) -> None:
        nonlocal truncated
        if len(findings) >= MAX_FINDINGS:
            truncated = True
            return
        entry = {
            "path": common.common_relative(root, path),
            "category": category,
            "severity": severity,
        }
        if line is not None:
            entry["line"] = line
        findings.append(entry)

    for path in privacy_scope_files(root, tracked_only=public_mode):
        relative = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if path.is_symlink():
            add(path, "symlink-in-public-tree", common.STATUS_FAIL)
            continue
        if public_mode and (
            (relative.startswith("evidence/vehicle-usb/") and relative != "evidence/vehicle-usb/README.md")
            or relative.startswith("evidence/upstream/")
            or relative.startswith("evidence/child-notes/artifacts/")
            or relative.startswith("council/review-batch-")
            or suffix in PUBLIC_RAW_SUFFIXES
        ):
            add(path, "raw-evidence-in-public-tree", common.STATUS_FAIL)
            continue
        if suffix in PROHIBITED_SUFFIXES:
            add(path, "prohibited-file", common.STATUS_FAIL)
            continue
        try:
            head = path.read_bytes()[:512]
        except OSError:
            add(path, "unreadable-file", common.STATUS_FAIL)
            continue
        # Binary firmware, archives, captures, and dumps are permitted in the
        # private repository. Do not parse or echo their content here.
        if suffix not in (PUBLIC_TEXT_SUFFIXES if public_mode else TEXT_SUFFIXES):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            add(path, "unreadable-file", common.STATUS_FAIL)
            continue
        scanned += 1
        for number, line in enumerate(text.splitlines(), start=1):
            if public_mode and PUBLIC_PERSONAL_HOME.search(line):
                add(path, "operator-home-path", common.STATUS_FAIL, number)
            for category, pattern in SECRET_PATTERNS:
                if public_mode and suffix in {".py", ".sh", ".c", ".java"} and category == "credential-assignment":
                    pattern = PUBLIC_CODE_CREDENTIAL
                if pattern.search(line):
                    add(path, category, common.STATUS_FAIL, number)
            for match in EMAIL_PATTERN.finditer(line):
                category = (
                    "public-noreply-email"
                    if privacy_email_allowed(match.group(0))
                    else "email-address-private-repository"
                )
                severity = common.STATUS_FAIL if public_mode and not privacy_email_allowed(match.group(0)) else common.STATUS_INFO
                add(path, category, severity, number)
            for match in VIN_PATTERN.finditer(line):
                if privacy_vin_like(match.group(0)):
                    add(path, "vin-like-token-private-repository", common.STATUS_FAIL if public_mode else common.STATUS_INFO, number)

    findings.sort(key=lambda item: (item["path"], item.get("line", 0), item["category"]))
    blocking = [item for item in findings if item["severity"] == common.STATUS_FAIL]
    info_only = [item for item in findings if item["severity"] == common.STATUS_INFO]
    details = {
        "files_scanned": scanned,
        "findings": findings,
        "blocking_count": len(blocking),
        "info_count": len(info_only),
        "truncated": truncated,
    }
    if blocking:
        return common.common_result(
            "privacy",
            common.STATUS_FAIL,
            f"{len(blocking)} blocking finding(s) across {scanned} scoped file(s)",
            details,
        )
    if info_only:
        return common.common_result(
            "privacy",
            common.STATUS_INFO,
            f"{len(info_only)} public/reserved identifier(s); no blocking finding",
            details,
        )
    return common.common_result(
        "privacy", common.STATUS_PASS, f"{scanned} scoped file(s) clean", details
    )

