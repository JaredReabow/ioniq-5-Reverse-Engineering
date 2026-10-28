#!/usr/bin/env python3
"""Build a modified Gen5W rootfs package from a decrypted tree.

Context
-------
The public operating model (`evidence/gen5w-public-operating-model.md`) shows two
update paths:

  * normal: payloads are AES-encrypted and decrypted by the unit's
    `DecryptToPipe` before extraction;
  * unchecked: if `/update/disableEncryptionUpdate` exists, `AppUpgrade` performs
    **no decryption** and expects an entirely plaintext package. The
    `.lge.upgrade.xml` version check still runs.

This tool covers the second path. It takes a decrypted `mango-rootfs.tar.gz`,
injects files (a systemd unit, SSH authorised keys, an application), and repacks
in the exact format the upgrader expects:

    tar --format=ustar --numeric-owner -cf - ./ | gzip

It then reports the size and CRC-32 that the `.ver` manifest must carry for the
rebuilt file, and optionally rewrites a copy of the manifest.

It does **not** encrypt, does not produce a signed package, and does not write to
the unit. Shipping the result still requires the target unit to accept
unencrypted updates and to pass its own version check.

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
from pathlib import Path
from typing import Dict, List, Optional

DROPBEAR_KEYS = "etc/dropbear/authorized_keys"


def _member_name(path: str) -> str:
    """tar members are stored as ./relative paths, matching the vendor archive."""

    return "./" + path.lstrip("./")


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
    out.parent.mkdir(parents=True, exist_ok=True)
    added: List[str] = []

    with tempfile.TemporaryDirectory(prefix="gen5w-rootfs-") as temp:
        stage = Path(temp) / "stage"
        stage.mkdir()
        with tarfile.open(src, "r:gz") as tf:
            try:
                tf.extractall(stage, filter="tar")  # local staging dir only
            except TypeError:  # Python < 3.12
                tf.extractall(stage)

        def put(rel: str, data: bytes, mode: int) -> None:
            target = stage / rel.lstrip("./")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            os.chmod(target, mode)
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

        # Repack exactly as the vendor tooling expects.
        tmp_tar = Path(temp) / "rootfs.tar"
        subprocess_tar = shutil.which("tar")
        if not subprocess_tar:
            raise SystemExit("the tar binary is required")
        import subprocess
        proc = subprocess.run([subprocess_tar, "--format=ustar", "--numeric-owner",
                               "--exclude=*.DS_Store", "-C", str(stage),
                               "-cf", str(tmp_tar), "."],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit(f"tar failed: {proc.stderr.strip()}")
        with open(tmp_tar, "rb") as fin, gzip.open(out, "wb", compresslevel=6) as fout:
            shutil.copyfileobj(fin, fout)

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
        write.write_text("\n".join(result) + "\n", encoding="utf-8")
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
