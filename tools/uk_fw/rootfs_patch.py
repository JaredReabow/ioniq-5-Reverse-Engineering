#!/usr/bin/env python3
"""Build a modified Gen5W rootfs package from a decrypted tree.

Context
-------
Public tooling documents a plaintext update mode
(`evidence/gen5w-public-operating-model.md`), and the exact recovered `260128`
analysis (`evidence/appupgrade-update-trust.md`) constrains it. The public
operating model shows two update paths:

  * normal: payloads are AES-encrypted and decrypted by the unit's
    `DecryptToPipe` before extraction;
  * unchecked: if `/update/disableEncryptionUpdate` exists, `AppUpgrade` performs
    **no decryption** and expects an entirely plaintext package. The
    `.lge.upgrade.xml` version check still runs.

The recovered wrapper selects FUMO unless exact `-un:1` selects SCOMO, and only
the FUMO startup path maps `/update/disableEncryptionUpdate` to its zero-valued
"Unencryption" mode. The recovered SCOMO production/penetration path explicitly
ignores that marker. Neither route establishes that version, model, signature,
digest, write, slot, boot, or health checks are absent.

This tool only builds the plaintext rootfs archive used by the public workflow.
It takes a decrypted `mango-rootfs.tar.gz`, injects files (a systemd unit, SSH
authorised keys, an application), and repacks in the format the upgrader expects:

    tar --format=ustar --numeric-owner -cf - ./ | gzip

It then reports the size and CRC-32 that the `.ver` manifest must carry for the
rebuilt file, and optionally rewrites a copy of the manifest.

It does **not** encrypt, does not produce a signed package, and does not write to
the unit. Using the result would still require the target to select the FUMO
route, to accept unencrypted updates, and to pass every independent eligibility,
authentication, integrity, installation, boot, and health check (its own version
check included).

Usage
-----
    # inspect an existing package
    python3 rootfs_patch.py list mango-rootfs.tar.gz

    # inject a unit and an SSH key, repack, and report manifest values
    python3 rootfs_patch.py inject mango-rootfs.tar.gz -o out/mango-rootfs.tar.gz \
        --unit-file wideopen.service --unit-name wideopen.service \
        --ssh-key ~/.ssh/id_ed25519.pub

    # rewrite a copy of the .ver with the new size/CRC
    python3 rootfs_patch.py meta out/mango-rootfs.tar.gz --manifest IONIQ5_EU.ver \
        --write-manifest out/IONIQ5_EU.ver
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import shutil
import stat
import sys
import tarfile
import tempfile
import zlib
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional

DROPBEAR_KEYS = "etc/dropbear/authorized_keys"


class ArchiveSafetyError(ValueError):
    """Raised when an input archive or injection destination can escape staging."""


def _safe_relative_path(name: str, *, allow_root: bool = False) -> Path:
    """Convert one archive-style path to a bounded host-relative path."""

    if not name or "\\" in name or "\x00" in name:
        raise ArchiveSafetyError(f"unsafe path: {name!r}")
    pure = PurePosixPath(name)
    if pure.is_absolute():
        raise ArchiveSafetyError(f"absolute path rejected: {name!r}")
    parts = tuple(part for part in pure.parts if part not in ("", "."))
    if any(part == ".." for part in parts):
        raise ArchiveSafetyError(f"parent traversal rejected: {name!r}")
    if parts and parts[0].endswith(":"):
        raise ArchiveSafetyError(f"drive-qualified path rejected: {name!r}")
    if not parts:
        if allow_root:
            return Path()
        raise ArchiveSafetyError(f"empty destination rejected: {name!r}")
    return Path(*parts)


def _safe_extract(tf: tarfile.TarFile, stage: Path) -> Dict[Path, Dict[str, object]]:
    """Extract regular files/directories only and retain numeric tar metadata."""

    stage_root = stage.resolve()
    metadata: Dict[Path, Dict[str, object]] = {}
    for member in tf.getmembers():
        relative = _safe_relative_path(member.name, allow_root=True)
        if relative in metadata:
            raise ArchiveSafetyError(f"duplicate archive member rejected: {member.name!r}")
        if not member.isdir() and not member.isfile():
            raise ArchiveSafetyError(
                f"links and special members are rejected: {member.name!r} type={member.type!r}"
            )
        metadata[relative] = {
            "kind": "dir" if member.isdir() else "file",
            "mode": member.mode & 0o7777,
            "uid": member.uid,
            "gid": member.gid,
            "mtime": int(member.mtime),
        }
        if relative == Path():
            if not member.isdir():
                raise ArchiveSafetyError(f"archive root is not a directory: {member.name!r}")
            continue
        target = stage / relative
        try:
            target.resolve(strict=False).relative_to(stage_root)
        except ValueError as exc:
            raise ArchiveSafetyError(f"path escapes staging: {member.name!r}") from exc

        if member.isdir():
            if target.exists() and not target.is_dir():
                raise ArchiveSafetyError(f"directory conflicts with file: {member.name!r}")
            # Keep staging directories writable. The archived mode is restored
            # from metadata while repacking, after all descendants exist.
            target.mkdir(parents=True, exist_ok=True, mode=0o700)
            continue
        if target.exists():
            raise ArchiveSafetyError(f"archive member conflicts with existing path: {member.name!r}")
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        for parent in target.parents:
            if parent == stage.parent:
                break
            if parent.is_symlink():
                raise ArchiveSafetyError(f"symlink parent rejected: {member.name!r}")
        source = tf.extractfile(member)
        if source is None:
            raise ArchiveSafetyError(f"could not read regular member: {member.name!r}")
        with source, open(target, "xb") as output:
            shutil.copyfileobj(source, output)
    return metadata


def _default_metadata(kind: str, mode: int) -> Dict[str, object]:
    return {"kind": kind, "mode": mode, "uid": 0, "gid": 0, "mtime": 0}


def _record_parent_directories(metadata: Dict[Path, Dict[str, object]], relative: Path) -> None:
    parents = [parent for parent in relative.parents if parent != Path()]
    for parent in reversed(parents):
        metadata.setdefault(parent, _default_metadata("dir", 0o755))


def _write_ustar(stage: Path, metadata: Dict[Path, Dict[str, object]], output: Path) -> None:
    """Write a numeric-owner USTAR using retained metadata, never host ownership."""

    metadata.setdefault(Path(), _default_metadata("dir", 0o755))
    for target in stage.rglob("*"):
        relative = target.relative_to(stage)
        _record_parent_directories(metadata, relative)
        if relative not in metadata:
            if target.is_dir():
                metadata[relative] = _default_metadata("dir", 0o755)
            elif target.is_file():
                metadata[relative] = _default_metadata("file", 0o644)
            else:
                raise ArchiveSafetyError(f"unexpected staged object: {relative}")

    indexed = list(enumerate(metadata.items()))
    ordered = sorted(
        indexed,
        key=lambda item: (
            0 if item[1][0] == Path() else 1,
            0 if item[1][1]["kind"] == "dir" else 1,
            len(item[1][0].parts),
            item[0],
        ),
    )
    with tarfile.open(output, "w", format=tarfile.USTAR_FORMAT) as tf:
        for _, (relative, meta) in ordered:
            target = stage if relative == Path() else stage / relative
            expected_dir = meta["kind"] == "dir"
            if expected_dir and not target.is_dir():
                raise ArchiveSafetyError(f"staged directory missing: {relative}")
            if not expected_dir and not target.is_file():
                raise ArchiveSafetyError(f"staged regular file missing: {relative}")
            arcname = "." if relative == Path() else _member_name(relative.as_posix())
            info = tarfile.TarInfo(arcname)
            info.mode = int(meta["mode"])
            info.uid = int(meta["uid"])
            info.gid = int(meta["gid"])
            info.uname = ""
            info.gname = ""
            info.mtime = int(meta["mtime"])
            if expected_dir:
                info.type = tarfile.DIRTYPE
                tf.addfile(info)
            else:
                info.size = target.stat().st_size
                with open(target, "rb") as source:
                    tf.addfile(info, source)


def _bounded_target(stage: Path, destination: str) -> Path:
    relative = _safe_relative_path(destination)
    target = stage / relative
    stage_root = stage.resolve()
    try:
        target.resolve(strict=False).relative_to(stage_root)
    except ValueError as exc:
        raise ArchiveSafetyError(f"destination escapes staging: {destination!r}") from exc
    for parent in target.parents:
        if parent == stage.parent:
            break
        if parent.is_symlink():
            raise ArchiveSafetyError(f"destination has a symlink parent: {destination!r}")
    return target


def _paths_alias(first: Path, second: Path) -> bool:
    """Detect same path, symlink aliases, and existing hard-link aliases."""

    if first.resolve() == second.resolve():
        return True
    try:
        return os.path.samefile(first, second)
    except (FileNotFoundError, OSError):
        return False


def _member_name(path: str) -> str:
    """Tar members use one literal ``./`` prefix without changing dotfiles."""

    return path if path.startswith("./") else "./" + path


def list_package(path: Path, limit: int) -> Dict[str, object]:
    with tarfile.open(path, "r:gz") as tf:
        members = tf.getmembers()
    rows = []
    for m in members[:limit]:
        rows.append({"name": m.name, "size": m.size, "mode": oct(m.mode),
                     "uid": m.uid, "gid": m.gid,
                     "type": "dir" if m.isdir() else "file" if m.isfile() else "other"})
    return {
        "path": str(path),
        "members": len(members),
        "total_uncompressed": sum(m.size for m in members),
        "showing": len(rows),
        "rows": rows,
    }


def _add_bytes(tar: tarfile.TarFile, name: str, data: bytes, mode: int, uid: int, gid: int) -> None:
    info = tarfile.TarInfo(_member_name(name))
    info.size = len(data)
    info.mode = mode
    info.uid = uid
    info.gid = gid
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    tar.addfile(info, io.BytesIO(data))


def inject(src: Path, out: Path, additions: List[Path], unit_file: Optional[Path],
           unit_name: Optional[str], ssh_key: Optional[Path],
           dropbear_script: Optional[Path]) -> Dict[str, object]:
    if _paths_alias(src, out):
        raise ArchiveSafetyError("output must not overwrite the input package")
    if out.exists() or out.is_symlink():
        raise ArchiveSafetyError("output already exists; choose a new path")
    out.parent.mkdir(parents=True, exist_ok=True)
    added: List[str] = []

    with tempfile.TemporaryDirectory(prefix="gen5w-rootfs-") as temp:
        stage = Path(temp) / "stage"
        stage.mkdir()
        with tarfile.open(src, "r:gz") as tf:
            metadata = _safe_extract(tf, stage)

        def put(rel: str, data: bytes, mode: int) -> None:
            target = _bounded_target(stage, rel)
            if target.exists() and not target.is_file():
                raise ArchiveSafetyError(f"injection destination is not a regular file: {rel!r}")
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.write_bytes(data)
            relative = target.relative_to(stage)
            _record_parent_directories(metadata, relative)
            metadata[relative] = _default_metadata("file", mode)
            added.append(rel)

        if unit_file:
            name = unit_name or unit_file.name
            put(f"etc/systemd/system/{name}", unit_file.read_bytes(), 0o644)
        if ssh_key:
            existing = stage / DROPBEAR_KEYS
            payload = ssh_key.read_bytes()
            if existing.exists():
                old = existing.read_bytes()
                payload = old.rstrip(b"\n") + b"\n" + payload
            put(DROPBEAR_KEYS, payload, 0o600)
        if dropbear_script:
            put("etc/dropbear/dropbear_publickey_installer.sh",
                dropbear_script.read_bytes(), 0o755)
        for spec in additions:
            if ":" not in str(spec):
                raise SystemExit(f"addition must be <source>:<destination>: {spec}")
            source, dest = str(spec).split(":", 1)
            put(dest, Path(source).read_bytes(), 0o755)

        # Repack as numeric-owner USTAR without inheriting host uid/gid/modes.
        tmp_tar = Path(temp) / "rootfs.tar"
        _write_ustar(stage, metadata, tmp_tar)
        with open(tmp_tar, "rb") as source, open(out, "xb") as carrier:
            with gzip.GzipFile(filename="", mode="wb", fileobj=carrier,
                               compresslevel=6, mtime=0) as compressed:
                shutil.copyfileobj(source, compressed)

    crc = 0
    total = 0
    with open(out, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            crc = zlib.crc32(block, crc)
            total += len(block)
    signed = crc & 0xFFFFFFFF
    if signed & 0x80000000:
        signed -= 1 << 32
    return {
        "output": str(out),
        "added": added,
        "size": total,
        "crc32": f"0x{crc & 0xFFFFFFFF:08x}",
        "crc32_signed": signed,
        "manifest_note": "update the matching record in the .ver with size and crc32_signed",
    }


def update_manifest(manifest: Path, rebuilt: Path, write: Optional[Path],
                    filename: str) -> Dict[str, object]:
    if write is not None:
        if _paths_alias(manifest, write) or _paths_alias(rebuilt, write):
            raise ArchiveSafetyError(
                "manifest output must not overwrite the input manifest or rebuilt package"
            )
        if write.exists() or write.is_symlink():
            raise ArchiveSafetyError("manifest output already exists; choose a new path")
    data = rebuilt.read_bytes()
    crc = zlib.crc32(data) & 0xFFFFFFFF
    signed = crc - (1 << 32) if crc & 0x80000000 else crc
    lines = manifest.read_text(encoding="utf-8").splitlines()
    changed = 0
    result = []
    for line in lines:
        fields = line.split("|")
        if len(fields) >= 6 and fields[1] == filename:
            fields[3] = str(signed)
            fields[4] = str(len(data))
            changed += 1
            line = "|".join(fields)
        result.append(line)
    if write:
        with open(write, "x", encoding="utf-8") as output:
            output.write("\n".join(result) + "\n")
    return {
        "manifest": str(manifest),
        "filename": filename,
        "records_updated": changed,
        "size": len(data),
        "crc32_signed": signed,
        "written": str(write) if write else None,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list members of a rootfs package")
    p_list.add_argument("package", type=Path)
    p_list.add_argument("--limit", type=int, default=40)
    p_list.add_argument("--json", action="store_true")

    p_inj = sub.add_parser("inject", help="inject files and repack")
    p_inj.add_argument("package", type=Path)
    p_inj.add_argument("-o", "--out", type=Path, required=True)
    p_inj.add_argument("--add", action="append", default=[], metavar="SRC:DEST")
    p_inj.add_argument("--unit-file", type=Path)
    p_inj.add_argument("--unit-name")
    p_inj.add_argument("--ssh-key", type=Path)
    p_inj.add_argument("--dropbear-script", type=Path)

    p_meta = sub.add_parser("meta", help="compute manifest values for a rebuilt file")
    p_meta.add_argument("rebuilt", type=Path)
    p_meta.add_argument("--manifest", type=Path)
    p_meta.add_argument("--write-manifest", type=Path)
    p_meta.add_argument("--filename", default="mango-rootfs.tar.gz")

    args = ap.parse_args(argv)

    if args.cmd == "list":
        result = list_package(args.package, args.limit)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for row in result["rows"]:
                print(f"  {row['type']:5} {row['mode']:>7} {row['uid']:>5}:{row['gid']:<5} "
                      f"{row['size']:>10}  {row['name']}")
            print(f"{result['members']} members, {result['total_uncompressed']} bytes uncompressed")
        return 0

    if args.cmd == "inject":
        print(json.dumps(inject(args.package, args.out, args.add, args.unit_file,
                                args.unit_name, args.ssh_key, args.dropbear_script),
                         indent=2))
        return 0

    if args.cmd == "meta":
        if not args.manifest:
            raise SystemExit("meta requires --manifest")
        print(json.dumps(update_manifest(args.manifest, args.rebuilt,
                                         args.write_manifest, args.filename), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
