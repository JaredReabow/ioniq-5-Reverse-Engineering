"""Read-only Git scope guard against pushing Ioniq work to the Kona repository.

The older shared checkout can keep the Kona repository as ``origin`` for
fetch and tracking. A Kona fetch origin is therefore not, by itself, a reason
to block an Ioniq push. This public snapshot uses its own ``origin`` and an
explicit ``ioniq`` remote. An Ioniq push is allowed only when the
configuration proves an explicit destination:

* an ``ioniq`` remote whose every URL is exactly ``JaredReabow/ioniq-5-Reverse-Engineering``;
* ``remote.pushDefault`` set to ``ioniq``;
* no branch ``pushRemote``/push URL and no URL rewrite rule that redirects the
  push to another repository;
* no staged ``kona_research/**`` path.

Anything missing, unsafe, or merely similar (a fork, another owner, a plain
HTTP URL, ``kona_ev`` style typos) still blocks. The guard only reads Git
state and never mutates it.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit

from . import common

KONA_PREFIX = "kona_research"
IONIQ_REMOTE = "ioniq"
IONIQ_OWNER = "jaredreabow"
IONIQ_REPO = "ioniq-5-reverse-engineering"
GITHUB_HOSTS = frozenset({"github.com", "www.github.com"})
INSECURE_SCHEMES = frozenset({"http", "git"})

_URL_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.\-]*://", re.IGNORECASE)
_SCP_RE = re.compile(r"^(?:([^@/]+)@)?([^:/]+):(?!//)(.+)$")
_REMOTE_KEY_RE = re.compile(r"^remote\.(.+)\.(url|pushurl)$", re.IGNORECASE)
_BRANCH_KEY_RE = re.compile(
    r"^branch\.(.+)\.(pushremote|pushurl|remote)$", re.IGNORECASE
)
_URL_REWRITE_KEY_RE = re.compile(
    r"^url\.(.+)\.(insteadof|pushinsteadof)$", re.IGNORECASE
)


def gitscope_parse_status(output: str) -> list[dict]:
    """Parse ``git status --porcelain=v1 -z`` into structured entries."""
    entries: list[dict] = []
    tokens = [token for token in output.split("\0") if token]
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if len(token) < 4:
            continue
        staged_char = token[0]
        worktree_char = token[1]
        entry = {
            "x": staged_char,
            "y": worktree_char,
            "path": token[3:],
            "original_path": None,
            "staged": staged_char not in " ?",
        }
        if staged_char in "RC" or worktree_char in "RC":
            if index < len(tokens):
                entry["original_path"] = tokens[index]
                index += 1
        entries.append(entry)
    return entries


def gitscope_parse_config(output: str) -> list[tuple[str, str]]:
    """Parse ``git config --list -z`` into ordered ``(key, value)`` pairs.

    Git separates an entry's key and value with a newline and terminates each
    entry with NUL. A valueless key keeps an empty value.
    """
    pairs: list[tuple[str, str]] = []
    for token in output.split("\0"):
        if not token:
            continue
        key, _, value = token.partition("\n")
        key = key.strip()
        if key:
            pairs.append((key, value))
    return pairs


def gitscope_is_kona_path(path: str) -> bool:
    """True when a repository-relative path belongs to the Kona workspace."""
    normalised = path.strip().lstrip("./")
    return normalised == KONA_PREFIX or normalised.startswith(KONA_PREFIX + "/")


def gitscope_url_scheme(url: str | None) -> str | None:
    """Return the lowercase URL scheme, or ``None`` for scp-like/local forms."""
    if not url:
        return None
    match = _URL_SCHEME_RE.match(url.strip())
    return match.group(0)[:-3].lower() if match else None


def gitscope_repo_identity(url: str | None) -> tuple[str, str, str] | None:
    """Return ``(host, owner, repo)`` lowercased for a Git remote URL.

    Understands ``https://``, ``ssh://`` and scp-like ``git@host:owner/repo``
    forms. Local paths and malformed URLs return ``None`` so they can never be
    mistaken for the GitHub destination.
    """
    if not url:
        return None
    text = url.strip()
    if not text:
        return None
    if gitscope_url_scheme(text) is not None:
        parts = urlsplit(text)
        host = parts.hostname or ""
        path = parts.path
    else:
        match = _SCP_RE.match(text)
        if not match:
            return None
        host = match.group(2)
        path = match.group(3)
    segments = [segment for segment in path.strip("/").split("/") if segment]
    if len(segments) < 2:
        return None
    owner, repo = segments[-2], segments[-1]
    if repo.lower().endswith(".git"):
        repo = repo[:-4]
    if not owner or not repo:
        return None
    return (host.lower(), owner.lower(), repo.lower())


def gitscope_is_ioniq_repo(url: str | None) -> bool:
    """True only for the exact ``JaredReabow/ioniq-5-Reverse-Engineering`` GitHub repository."""
    identity = gitscope_repo_identity(url)
    if identity is None:
        return False
    host, owner, repo = identity
    return host in GITHUB_HOSTS and owner == IONIQ_OWNER and repo == IONIQ_REPO


def gitscope_is_kona_remote(url: str | None) -> bool:
    """True when a remote URL names the Kona repository."""
    if not url:
        return False
    identity = gitscope_repo_identity(url)
    if identity is not None and "kona" in identity[2]:
        return True
    normalised = url.strip().lower().replace("_", "-")
    return "kona-ev" in normalised


def gitscope_is_insecure_url(url: str | None) -> bool:
    """True for transports that must never carry an Ioniq push."""
    return gitscope_url_scheme(url) in INSECURE_SCHEMES


def gitscope_sanitize_url(url: str | None) -> str | None:
    """Return a display URL with embedded credentials removed."""
    if not url:
        return url
    text = url.strip()
    scheme = gitscope_url_scheme(text)
    if scheme is not None:
        match = re.match(r"^([a-zA-Z][a-zA-Z0-9+.\-]*://)([^/]*)(.*)$", text)
        if not match:
            return text
        scheme_text, authority, rest = match.groups()
        if "@" in authority:
            userinfo, host = authority.rsplit("@", 1)
            keep_user = scheme in {"ssh", "git+ssh"} and userinfo.lower() == "git"
            authority = (userinfo if keep_user else "<redacted>") + "@" + host
        return scheme_text + authority + rest
    match = _SCP_RE.match(text)
    if match and match.group(1) and match.group(1).lower() != "git":
        return f"<redacted>@{match.group(2)}:{match.group(3)}"
    return text


def gitscope_remotes(pairs: list[tuple[str, str]]) -> dict[str, dict[str, list[str]]]:
    """Group ``remote.<name>.url``/``pushurl`` entries by remote name."""
    remotes: dict[str, dict[str, list[str]]] = {}
    for key, value in pairs:
        match = _REMOTE_KEY_RE.match(key)
        if not match:
            continue
        name, field = match.group(1), match.group(2).lower()
        remotes.setdefault(name, {"url": [], "pushurl": []})[field].append(
            value.strip()
        )
    return remotes


def gitscope_branch_config(
    pairs: list[tuple[str, str]],
) -> dict[str, dict[str, list[str]]]:
    """Group branch-scoped ``pushRemote``/``pushurl`` entries by branch name."""
    branches: dict[str, dict[str, list[str]]] = {}
    for key, value in pairs:
        match = _BRANCH_KEY_RE.match(key)
        if not match:
            continue
        name, field = match.group(1), match.group(2).lower()
        branches.setdefault(name, {}).setdefault(field, []).append(value.strip())
    return branches


def gitscope_url_rewrites(
    pairs: list[tuple[str, str]],
) -> list[tuple[str, str, str]]:
    """Collect ``url.<base>.insteadOf``/``pushInsteadOf`` rewrite rules."""
    rules: list[tuple[str, str, str]] = []
    for key, value in pairs:
        match = _URL_REWRITE_KEY_RE.match(key)
        if not match:
            continue
        base, kind = match.group(1).strip(), match.group(2).lower()
        prefix = value.strip()
        if base and prefix:
            rules.append((kind, base, prefix))
    return rules


def gitscope_apply_rewrites(url: str, rules: list[tuple[str, str, str]]) -> str:
    """Apply Git's longest-prefix URL rewrite for push resolution."""
    if not url:
        return url
    for kind in ("pushinsteadof", "insteadof"):
        matches = [
            rule for rule in rules if rule[0] == kind and url.startswith(rule[2])
        ]
        if matches:
            rule = max(matches, key=lambda candidate: len(candidate[2]))
            return rule[1] + url[len(rule[2]) :]
    return url


def gitscope_last(values: list[str]) -> str | None:
    """Return the last configured value, as Git's single-value reader does.

    A trailing empty value means the key is effectively unset; it must not
    fall back to an earlier (for example global) value that Git would ignore.
    """
    if not values:
        return None
    return values[-1].strip() or None


def gitscope_resolve_remote_urls(
    name: str | None, remotes: dict[str, dict[str, list[str]]]
) -> list[str]:
    """Resolve a remote name (or literal URL) to the URLs it pushes to."""
    if not name:
        return []
    remote = remotes.get(name)
    if remote is not None:
        # ``pushurl`` replaces ``url`` for pushes when present.
        return remote["pushurl"] or remote["url"]
    return [name] if gitscope_repo_identity(name) is not None else []


def gitscope_check(root: Path, *, runner=None) -> dict:
    """Verify staged scope and an explicit, non-Kona Ioniq push destination."""
    root = Path(root)
    run = runner or common.common_run

    def call(*args: str) -> dict:
        return run(["git", "-C", str(root), *args])

    top = call("rev-parse", "--show-toplevel")
    if top.get("exit_status") != 0:
        return common.common_result(
            "gitscope",
            common.STATUS_PENDING,
            "not a Git work tree; push scope cannot be checked",
            {"git_available": False},
        )

    scope_reasons: list[dict] = []

    status = call("--no-optional-locks", "status", "--porcelain=v1", "-z")
    if status.get("exit_status") != 0:
        scope_reasons.append(
            {
                "code": "status-unavailable",
                "message": "git status failed; staged scope cannot be verified",
                "error": (status.get("stderr") or "").strip()[-200:],
            }
        )
        entries: list[dict] = []
    else:
        entries = gitscope_parse_status(status.get("stdout") or "")

    config_run = call("config", "--list", "-z")
    if config_run.get("exit_status") != 0:
        scope_reasons.append(
            {
                "code": "config-unavailable",
                "message": "git config failed; push destination cannot be verified",
                "error": (config_run.get("stderr") or "").strip()[-200:],
            }
        )
        pairs: list[tuple[str, str]] = []
    else:
        pairs = gitscope_parse_config(config_run.get("stdout") or "")

    # ``symbolic-ref`` also names the branch before the first commit, where
    # ``rev-parse --abbrev-ref HEAD`` still fails.
    branch_run = call("symbolic-ref", "--short", "-q", "HEAD")
    if branch_run.get("exit_status") != 0:
        branch_run = call("rev-parse", "--abbrev-ref", "HEAD")
    branch = (
        (branch_run.get("stdout") or "").strip()
        if branch_run.get("exit_status") == 0
        else None
    )
    if not branch:
        scope_reasons.append(
            {
                "code": "branch-unavailable",
                "message": "current branch cannot be resolved; push overrides unknown",
            }
        )

    staged = [entry for entry in entries if entry["staged"]]
    kona_staged = sorted(
        {
            path
            for entry in staged
            for path in (entry["path"], entry["original_path"])
            if path and gitscope_is_kona_path(path)
        }
    )
    if kona_staged:
        scope_reasons.append(
            {
                "code": "staged-kona-path",
                "message": "Kona-owned paths are staged for an Ioniq commit",
                "paths": kona_staged,
            }
        )

    remotes = gitscope_remotes(pairs)
    branch_config = gitscope_branch_config(pairs)
    rewrites = gitscope_url_rewrites(pairs)
    push_default = gitscope_last(
        [value for key, value in pairs if key.lower() == "remote.pushdefault"]
    )

    origin = next(iter(remotes.get("origin", {}).get("url", [])), None)
    ioniq = remotes.get(IONIQ_REMOTE, {"url": [], "pushurl": []})
    ioniq_urls = ioniq["url"]
    ioniq_pushurls = ioniq["pushurl"]

    destination_reasons: list[dict] = []

    if not ioniq_urls:
        destination_reasons.append(
            {
                "code": "missing-ioniq-remote",
                "message": (
                    "no explicit 'ioniq' remote; configure one that targets "
                    "JaredReabow/ioniq-5-Reverse-Engineering before an Ioniq push"
                ),
            }
        )
    for url in ioniq_urls:
        if not gitscope_is_ioniq_repo(url):
            destination_reasons.append(
                {
                    "code": "ioniq-remote-mismatch",
                    "message": "remote.ioniq.url is not exactly JaredReabow/ioniq-5-Reverse-Engineering",
                    "url": gitscope_sanitize_url(url),
                }
            )
            continue
        if gitscope_is_insecure_url(url):
            destination_reasons.append(
                {
                    "code": "insecure-ioniq-remote",
                    "message": "remote.ioniq.url uses an insecure transport",
                    "url": gitscope_sanitize_url(url),
                }
            )
            continue
        rewritten = gitscope_apply_rewrites(url, rewrites)
        if not gitscope_is_ioniq_repo(rewritten):
            destination_reasons.append(
                {
                    "code": "url-rewrite-redirect",
                    "message": "a URL rewrite rule redirects the Ioniq remote",
                    "configured": gitscope_sanitize_url(url),
                    "effective": gitscope_sanitize_url(rewritten),
                }
            )
    for url in ioniq_pushurls:
        effective = gitscope_apply_rewrites(url, rewrites)
        if not gitscope_is_ioniq_repo(effective):
            destination_reasons.append(
                {
                    "code": "ioniq-pushurl-mismatch",
                    "message": "remote.ioniq.pushurl is not exactly JaredReabow/ioniq-5-Reverse-Engineering",
                    "url": gitscope_sanitize_url(url),
                    "effective": gitscope_sanitize_url(effective),
                }
            )

    if push_default != IONIQ_REMOTE:
        destination_reasons.append(
            {
                "code": "push-default-not-ioniq",
                "message": "remote.pushDefault must be 'ioniq'",
                "value": gitscope_sanitize_url(push_default),
            }
        )

    current_branch_config = branch_config.get(branch or "", {})
    branch_push_remote = gitscope_last(
        current_branch_config.get("pushremote", [])
    )
    branch_pushurl = gitscope_last(current_branch_config.get("pushurl", []))

    effective_remote = branch_push_remote or push_default
    effective_urls = [
        gitscope_apply_rewrites(url, rewrites)
        for url in gitscope_resolve_remote_urls(effective_remote, remotes)
    ]

    if branch_push_remote and branch_push_remote != IONIQ_REMOTE:
        destination_reasons.append(
            {
                "code": "branch-push-remote-overrides",
                "message": f"branch.{branch}.pushRemote overrides remote.pushDefault",
                "branch": branch,
                "push_remote": gitscope_sanitize_url(branch_push_remote),
            }
        )
    if any(gitscope_is_kona_remote(url) for url in effective_urls):
        destination_reasons.append(
            {
                "code": "push-remote-kona-ev",
                "message": "the effective push destination resolves to Kona",
                "urls": [gitscope_sanitize_url(url) for url in effective_urls],
            }
        )
    elif effective_urls and any(
        not gitscope_is_ioniq_repo(url) for url in effective_urls
    ):
        destination_reasons.append(
            {
                "code": "effective-push-mismatch",
                "message": "the effective push destination is not the Ioniq repository",
                "urls": [gitscope_sanitize_url(url) for url in effective_urls],
            }
        )
    if branch_pushurl:
        effective = gitscope_apply_rewrites(branch_pushurl, rewrites)
        if not gitscope_is_ioniq_repo(effective):
            destination_reasons.append(
                {
                    "code": "branch-pushurl-mismatch",
                    "message": f"branch.{branch}.pushurl is not the Ioniq repository",
                    "branch": branch,
                    "url": gitscope_sanitize_url(branch_pushurl),
                    "effective": gitscope_sanitize_url(effective),
                }
            )

    inactive_branch_pushes: list[dict] = []
    for name, config in sorted(branch_config.items()):
        push_remote = gitscope_last(config.get("pushremote", []))
        push_urls = [
            gitscope_apply_rewrites(url, rewrites)
            for url in gitscope_resolve_remote_urls(push_remote, remotes)
        ]
        for push_url in config.get("pushurl", []):
            push_urls.append(gitscope_apply_rewrites(push_url, rewrites))
        if any(gitscope_is_kona_remote(url) for url in push_urls):
            destination_reasons.append(
                {
                    "code": "branch-push-remote-kona-ev",
                    "message": f"branch {name!r} pushes to the Kona repository",
                    "branch": name,
                    "push_remote": gitscope_sanitize_url(push_remote),
                    "urls": [gitscope_sanitize_url(url) for url in push_urls],
                }
            )
        elif any(gitscope_is_insecure_url(url) for url in push_urls):
            destination_reasons.append(
                {
                    "code": "branch-push-remote-insecure",
                    "message": f"branch {name!r} pushes over an insecure transport",
                    "branch": name,
                    "urls": [gitscope_sanitize_url(url) for url in push_urls],
                }
            )
        elif name != branch and push_remote and push_remote != IONIQ_REMOTE:
            inactive_branch_pushes.append(
                {
                    "branch": name,
                    "push_remote": gitscope_sanitize_url(push_remote),
                    "urls": [gitscope_sanitize_url(url) for url in push_urls],
                }
            )

    reasons = scope_reasons + destination_reasons
    destination_ok = not destination_reasons and bool(ioniq_urls)

    details = {
        "git_available": True,
        "branch": branch,
        "origin": gitscope_sanitize_url(origin) if origin else None,
        "origin_kona": gitscope_is_kona_remote(origin),
        "push_default": gitscope_sanitize_url(push_default),
        "effective_push_remote": (
            gitscope_sanitize_url(effective_remote) if effective_remote else None
        ),
        "effective_push_urls": [
            gitscope_sanitize_url(url) for url in effective_urls
        ],
        "ioniq_remote": {
            "name": IONIQ_REMOTE,
            "url": gitscope_sanitize_url(ioniq_urls[0]) if ioniq_urls else None,
            "pushurls": [gitscope_sanitize_url(url) for url in ioniq_pushurls],
        },
        "verified_destination": (
            {
                "remote": IONIQ_REMOTE,
                "url": gitscope_sanitize_url(ioniq_urls[0]),
                "push_urls": [
                    gitscope_sanitize_url(url)
                    for url in (ioniq_pushurls or ioniq_urls)
                ],
            }
            if destination_ok
            else None
        ),
        "inactive_branch_push_remotes": inactive_branch_pushes,
        "staged_paths": sorted(entry["path"] for entry in staged),
        "push_blocked": bool(reasons),
        "reasons": reasons,
    }
    # Make the accepted-fetch/inert-config situation explicit rather than
    # leaving a reader to infer why ``origin`` no longer appears in reasons.
    details["origin_kona_ignored"] = bool(
        details["origin_kona"] and destination_ok
    )

    if reasons:
        return common.common_result(
            "gitscope",
            common.STATUS_BLOCKED,
            "Ioniq push BLOCKED: " + "; ".join(reason["code"] for reason in reasons),
            details,
        )
    verified = details["verified_destination"]["url"]
    return common.common_result(
        "gitscope",
        common.STATUS_PASS,
        (
            f"push scope clean on branch {branch or 'unknown'}; "
            f"verified destination {IONIQ_REMOTE} -> {verified}"
        ),
        details,
    )
