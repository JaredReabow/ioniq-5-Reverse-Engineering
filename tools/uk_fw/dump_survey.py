#!/usr/bin/env python3
"""Read-only survey of an IONIQ 5 Gen5W rootfs dump or extracted tree.

Purpose
-------
Given either an extracted/mounted root filesystem directory or an ext4 image,
produce a structured inventory of the facts that decide how a *bench* unit can
be rooted.  It never executes target code, never mounts anything read-write,
and never modifies the input.

It answers the questions that matter for privilege escalation on the bench:

  * which accounts exist and whether any have usable/empty passwords;
  * which binaries are setuid/setgid and which carry file capabilities;
  * what SMACK policy exists and where it is configured;
  * which systemd units run as root and what they execute;
  * what kernel command line / boot config is present;
  * whether debug/remote-access surfaces (sshd, telnetd, gdbserver, /dev/mem,
    /dev/kmem, /dev/kcore, debugfs) are present in the image;
  * which paths are world-writable or otherwise persistence-friendly.

Design constraints
------------------
* Standard library only.
* Read-only: files are opened for reading; images are queried via ``debugfs``
  in read-only mode (``-R`` with the ``-w`` flag never passed).
* Everything is best-effort and reported with an explicit ``confidence`` note
  where the host OS makes a check unreliable (notably file capabilities, which
  only survive on a Linux extraction that preserved xattrs).

Usage
-----
    python3 dump_survey.py --root /path/to/extracted/rootfs
    python3 dump_survey.py --root /Volumes/rootfs --json survey.json
    python3 dump_survey.py --image rootfs.ext4            # needs debugfs
    python3 dump_survey.py --root . --only accounts,smack
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

SECTIONS = (
    "identity",
    "accounts",
    "privilege",
    "capabilities",
    "smack",
    "systemd",
    "boot",
    "debug",
    "persistence",
    "writable",
)

# Paths that are interesting if present at all.
DEBUG_HINTS = [
    "dev/mem",
    "dev/kmem",
    "dev/kcore",
    "dev/keystore",
    "dev/kgsl",
    "dev/dri",
    "proc/kcore",
    "sys/kernel/debug",
    "sys/fs/smackfs",
    "usr/sbin/sshd",
    "usr/bin/sshd",
    "sbin/sshd",
    "usr/sbin/dropbear",
    "usr/sbin/telnetd",
    "usr/bin/gdbserver",
    "usr/bin/strace",
    "usr/bin/gdb",
    "bin/busybox",
    "usr/bin/busybox",
    "system/bin/sh",
]

# Unit names that commonly expose a shell or a privileged service.
SYSTEMD_INTEREST = (
    "ssh",
    "telnet",
    "debug",
    "factory",
    "engineering",
    "sop",
    "update",
    "recovery",
    "serial",
    "getty",
    "console",
    "flash",
    "ota",
    "diagnostic",
)


def _rel(root: Path, path: Path) -> str:
    try:
        return "/" + str(path.relative_to(root)).lstrip("/")
    except ValueError:
        return str(path)


def _read_text(path: Path, limit: int = 1 << 20) -> Optional[str]:
    try:
        data = path.read_bytes()[:limit]
    except (OSError, ValueError):
        return None
    return data.decode("utf-8", "replace")


# --------------------------------------------------------------------------
# Backends: a directory tree, or an ext4 image queried through debugfs.
# --------------------------------------------------------------------------


class DirBackend:
    """Survey an already-extracted or mounted root filesystem directory."""

    def __init__(self, root: Path):
        self.root = root
        self.kind = "directory"

    def exists(self, rel: str) -> bool:
        return (self.root / rel.lstrip("/")).exists()

    def read(self, rel: str) -> Optional[str]:
        p = self.root / rel.lstrip("/")
        return _read_text(p) if p.is_file() else None

    def walk_files(self) -> Iterable[str]:
        for dirpath, _dirnames, filenames in os.walk(self.root, followlinks=False):
            for name in filenames:
                p = Path(dirpath) / name
                yield _rel(self.root, p)

    def lstat(self, rel: str) -> Optional[os.stat_result]:
        try:
            return os.lstat(self.root / rel.lstrip("/"))
        except OSError:
            return None

    def getcap(self, rel: str) -> Optional[str]:
        """Best-effort file capability read; only meaningful on Linux."""

        if sys.platform != "linux":
            return None
        try:
            raw = os.getxattr(self.root / rel.lstrip("/"), "security.capability")
        except OSError:
            return None
        return raw.hex()

    def close(self) -> None:
        pass


class ImageBackend:
    """Survey an ext4 image read-only through ``debugfs``.

    ``debugfs`` is not shipped with macOS; install e2fsprogs via Homebrew or
    extract the image first, then use ``--root``.
    """

    def __init__(self, image: Path):
        self.image = image
        self.root = Path("/")
        self.kind = "image"
        exe = shutil.which("debugfs")
        if exe is None:
            raise RuntimeError(
                "debugfs not found. On macOS run 'brew install e2fsprogs', or "
                "extract the image (ext4fuse/7z) and use --root."
            )
        self.exe = exe
        # Copy to a temp path so a mounted/case-insensitive source cannot be
        # touched, and so debugfs never opens the original in write mode.
        self._tmp = tempfile.TemporaryDirectory(prefix="ioniq-img-")
        self._copy = Path(self._tmp.name) / "image.ext4"
        shutil.copyfile(image, self._copy)

    def _run(self, cmd: str) -> str:
        proc = subprocess.run(
            [self.exe, "-R", cmd, str(self._copy)],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.stdout + proc.stderr

    def exists(self, rel: str) -> bool:
        out = self._run(f"stat {rel.lstrip('/')}")
        return "Inode:" in out

    def read(self, rel: str) -> Optional[str]:
        if not self.exists(rel):
            return None
        out = self._run(f"cat {rel.lstrip('/')}")
        return out

    def walk_files(self) -> Iterable[str]:
        # debugfs 'ls -l -r' is awkward to parse reliably; recurse manually.
        stack = ["/"]
        seen = 0
        while stack and seen < 200_000:
            cur = stack.pop()
            listing = self._run(f"ls -p {cur.lstrip('/')}")
            for line in listing.splitlines():
                parts = line.split("/")
                # debugfs -p output: inode/mode/uid/gid/name/size
                if len(parts) < 6:
                    continue
                mode, name = parts[1], parts[5]
                if name in (".", "..", ""):
                    continue
                full = (cur.rstrip("/") + "/" + name) or "/" + name
                seen += 1
                if mode.startswith("d") if mode else False:
                    stack.append(full)
                else:
                    yield full

    def lstat(self, rel: str) -> Optional[os.stat_result]:
        return None  # not available for image backend

    def getcap(self, rel: str) -> Optional[str]:
        return None

    def close(self) -> None:
        self._tmp.cleanup()


# --------------------------------------------------------------------------
# Section collectors
# --------------------------------------------------------------------------


def collect_identity(be) -> dict:
    out: Dict[str, object] = {"files": {}}
    for rel in (
        "/etc/os-release",
        "/etc/version",
        "/etc/build",
        "/etc/buildinfo",
        "/etc/fw_version",
        "/etc/hyundai/version",
        "/proc/version",
        "/etc/issue",
    ):
        text = be.read(rel)
        if text:
            out["files"][rel] = text.strip()[:2000]
    return out


def collect_accounts(be) -> dict:
    out: Dict[str, object] = {"passwd": [], "shadow": [], "notes": []}
    passwd = be.read("/etc/passwd") or ""
    for line in passwd.splitlines():
        f = line.split(":")
        if len(f) >= 7:
            uid, gid = f[2], f[3]
            try:
                privileged = int(uid) == 0 or int(gid) == 0
            except ValueError:
                privileged = False
            out["passwd"].append(
                {"name": f[0], "uid": uid, "gid": gid, "shell": f[6], "root": privileged}
            )

    shadow = be.read("/etc/shadow") or be.read("/etc/shadow-")
    if not shadow:
        out["notes"].append("/etc/shadow absent from this view (likely needs root or image)")
    for line in shadow.splitlines():
        f = line.split(":")
        if len(f) < 2:
            continue
        pw = f[1]
        state = "empty" if pw == "" else "locked" if pw.startswith(("!", "*")) else "hash"
        out["shadow"].append({"name": f[0], "state": state})
        if state == "empty":
            out["notes"].append(f"account '{f[0]}' has an EMPTY password")
    return out


def collect_privilege(be) -> dict:
    out: Dict[str, object] = {"setuid": [], "setgid": [], "notes": []}
    for rel in be.walk_files():
        st = be.lstat(rel)
        if st is None:
            continue
        if st.st_mode & stat.S_ISUID:
            out["setuid"].append(rel)
        if st.st_mode & stat.S_ISGID:
            out["setgid"].append(rel)
    if be.kind == "image":
        out["notes"].append(
            "image backend cannot report setuid/setgid modes; extract and use --root"
        )
    return out


def collect_capabilities(be) -> dict:
    out: Dict[str, object] = {"files": {}, "notes": []}
    if sys.platform != "linux":
        out["notes"].append(
            "file capabilities require a Linux extraction with xattrs preserved; "
            "not reported on this host"
        )
        return out
    for rel in be.walk_files():
        cap = be.getcap(rel)
        if cap:
            out["files"][rel] = cap
    return out


def collect_smack(be) -> dict:
    out: Dict[str, object] = {"files": {}, "rules": [], "loads": [], "notes": []}
    for rel in (
        "/etc/smack/smack_access",
        "/etc/smack/accesses.d",
        "/etc/smack/cipso",
        "/etc/smack/netlabel",
        "/etc/smack/load",
        "/etc/smack/load2",
        "/etc/smack/onlycap",
        "/etc/smack/change-rule",
        "/etc/smack/ambient",
    ):
        text = be.read(rel)
        if text is None:
            continue
        out["files"][rel] = text.strip()[:4000]
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                out["rules"].append(line)
    if not out["files"]:
        out["notes"].append(
            "no /etc/smack policy files matched; policy may be compiled in, "
            "loaded from /sys/fs/smackfs, or delivered by a unit"
        )
    return out


def _parse_unit(text: str) -> dict:
    info: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            info.setdefault(k.strip(), v.strip())
    return info


def collect_systemd(be) -> dict:
    out: Dict[str, object] = {"units": [], "interesting": [], "notes": []}
    for base in ("/etc/systemd/system", "/usr/lib/systemd/system", "/lib/systemd/system"):
        if be.kind == "directory":
            for unit in (Path(be.root) / base.lstrip("/")).glob("*.service"):
                rel = "/" + str(unit.relative_to(be.root))
                text = be.read(rel) or ""
                info = _parse_unit(text)
                rec = {
                    "unit": unit.name,
                    "path": rel,
                    "exec": info.get("ExecStart", ""),
                    "user": info.get("User", "root"),
                    "type": info.get("Type", ""),
                }
                out["units"].append(rec)
                low = unit.name.lower()
                if any(k in low for k in SYSTEMD_INTEREST) or info.get("ExecStart", "").strip().startswith("/"):
                    out["interesting"].append(rec)
    if not out["units"]:
        out["notes"].append("no .service units readable in this view")
    return out


def collect_boot(be) -> dict:
    out: Dict[str, object] = {"cmdline": [], "files": {}}
    for rel in ("/proc/cmdline", "/boot/cmdline", "/etc/kernel/cmdline", "/boot/extlinux/extlinux.conf", "/boot/boot.scr"):
        text = be.read(rel)
        if text:
            out["files"][rel] = text.strip()[:2000]
    return out


def collect_debug(be) -> dict:
    out: Dict[str, object] = {"present": [], "absent": []}
    for rel in DEBUG_HINTS:
        if be.exists(rel):
            out["present"].append("/" + rel)
        else:
            out["absent"].append("/" + rel)
    return out


def collect_persistence(be) -> dict:
    out: Dict[str, object] = {"rc_local": None, "cron": [], "init": [], "notes": []}
    rc = be.read("/etc/rc.local")
    if rc:
        out["rc_local"] = rc.strip()[:2000]
    for rel in ("/etc/crontab",):
        text = be.read(rel)
        if text:
            out["cron"].append({rel: text.strip()[:2000]})
    for d in ("/etc/cron.d", "/etc/init.d", "/etc/rc2.d", "/etc/rc3.d", "/etc/rc5.d"):
        if be.kind == "directory":
            p = Path(be.root) / d.lstrip("/")
            if p.is_dir():
                out["init"].append({d: sorted(x.name for x in p.iterdir())[:60]})
    return out


def collect_writable(be) -> dict:
    out: Dict[str, object] = {"world_writable": [], "notes": []}
    if be.kind != "directory":
        out["notes"].append("world-writable scan requires the directory backend")
        return out
    for rel in be.walk_files():
        st = be.lstat(rel)
        if st and (st.st_mode & stat.S_IWOTH):
            out["world_writable"].append(rel)
    return out


COLLECTORS = {
    "identity": collect_identity,
    "accounts": collect_accounts,
    "privilege": collect_privilege,
    "capabilities": collect_capabilities,
    "smack": collect_smack,
    "systemd": collect_systemd,
    "boot": collect_boot,
    "debug": collect_debug,
    "persistence": collect_persistence,
    "writable": collect_writable,
}


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def render(name: str, data: dict) -> str:
    lines = [f"## {name}"]
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                continue
            lines.append(f"  {key}:")
            for item in value[:80]:
                lines.append(f"    - {item if not isinstance(item, dict) else json.dumps(item)}")
        elif isinstance(value, dict):
            if not value:
                continue
            lines.append(f"  {key}:")
            for k, v in list(value.items())[:40]:
                lines.append(f"    {k}: {v}")
        elif value not in (None, ""):
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--root", type=Path, help="extracted or mounted rootfs directory")
    src.add_argument("--image", type=Path, help="ext4 image (requires debugfs)")
    ap.add_argument("--json", type=Path, help="write the full result as JSON here")
    ap.add_argument("--only", default=",".join(SECTIONS), help="comma separated sections")
    ap.add_argument("--quiet", action="store_true", help="suppress the human summary")
    args = ap.parse_args(argv)

    sections = [s.strip() for s in args.only.split(",") if s.strip()]
    unknown = [s for s in sections if s not in COLLECTORS]
    if unknown:
        ap.error(f"unknown sections: {', '.join(unknown)}")

    be = DirBackend(args.root) if args.root else ImageBackend(args.image)
    if be.kind == "directory" and not be.root.is_dir():
        ap.error(f"not a directory: {be.root}")

    result: Dict[str, object] = {
        "source": str(args.root or args.image),
        "backend": be.kind,
        "host": sys.platform,
        "sections": {},
    }
    try:
        for name in sections:
            try:
                result["sections"][name] = COLLECTORS[name](be)
            except Exception as exc:  # keep going; one bad section must not abort
                result["sections"][name] = {"error": f"{type(exc).__name__}: {exc}"}
    finally:
        be.close()

    if not args.quiet:
        print(f"# IONIQ 5 rootfs survey — {result['source']} ({be.kind})\n")
        for name in sections:
            print(render(name, result["sections"][name]))
            print()

    if args.json:
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True))
        print(f"wrote {args.json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
