#!/usr/bin/env python3
"""Build a size-identical IONIQ 5 Gen5W rootfs envelope with a safe overlay.

The builder decrypts a genuine ``mango-rootfs.tar.gz`` TE2 envelope, appends a
small overlay to its tar archive, recompresses it, pads the plaintext back to the
original body length, and re-encrypts it while preserving the genuine trailer.
The default overlay only installs a one-shot proof service.  It does not enable
network access, add credentials, change vehicle-control software, or alter boot
images.

An optional overlay directory can add ordinary files, directories, and relative
symlinks.  Paths are archived below ``/`` and are validated before the build.
The output is encrypted for the on-device basename ``mango-rootfs.tar.gz`` even
when the host output file uses a different name.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tarfile
import tempfile
from typing import Iterable, NamedTuple


TOOL_VERSION = "1.0.2"
PAYLOAD_VERSION = "1.0.1"
DEVICE_BASENAME = "mango-rootfs.tar.gz"
COPY_CHUNK = 4 * 1024 * 1024


class CustomFirmwareError(RuntimeError):
    """Raised when an input or generated firmware artifact fails validation."""


def _load_crypt_module():
    source = Path(__file__).resolve().parents[2] / "gen5w_crypt.py"
    spec = importlib.util.spec_from_file_location("ioniq5_gen5w_crypt", source)
    if spec is None or spec.loader is None:
        raise CustomFirmwareError(f"cannot load TE2 implementation: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CRYPT = _load_crypt_module()


class _OverlayEntry(NamedTuple):
    """Describe one validated tar member to append."""

    name: str
    kind: str
    mode: int
    data: bytes = b""
    linkname: str = ""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(COPY_CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def _copy_stream(source, destination) -> None:
    while True:
        block = source.read(COPY_CHUNK)
        if not block:
            return
        destination.write(block)


def _ioniq5_source_identity(info: os.stat_result) -> tuple[int, ...]:
    """Bind identity and modification metadata, excluding read-induced atime."""
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _ioniq5_check_source(source, path: Path, identity: tuple[int, ...], digest: str) -> None:
    """Reject replacement or mutation of the source retained by this build."""
    source.seek(0)
    current = hashlib.sha256()
    for block in iter(lambda: source.read(COPY_CHUNK), b""):
        current.update(block)
    if (current.hexdigest() != digest
            or _ioniq5_source_identity(os.fstat(source.fileno())) != identity
            or _ioniq5_source_identity(path.lstat()) != identity):
        raise CustomFirmwareError("genuine envelope changed during build")


def _ioniq5_target_identity(path: Path) -> tuple[int, ...] | None:
    """Inspect a final target without following symlinks or accepting devices."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode):
        raise CustomFirmwareError(f"output must be a regular file: {path}")
    return _ioniq5_source_identity(info)


def _ioniq5_sync_directory(path: Path) -> None:
    """Persist directory entries before declaring publication successful."""
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _ioniq5_publish_pair(candidate: Path, report: dict, output: Path, manifest: Path,
                         identities: dict[Path, tuple[int, ...] | None],
                         source_check) -> None:
    """Stage both files, then publish with rollback on catchable failures.

    Two independent filenames cannot be atomically committed across a crash.
    Consumers must verify the manifest hash. Private same-filesystem backups
    are retained with their paths reported if rollback itself is unavailable.
    """
    stages: dict[Path, Path] = {}
    directories: list[Path] = []
    backups: dict[Path, Path] = {}
    installed: dict[Path, tuple[int, int]] = {}
    retain_backups = False
    try:
        for target in (output, manifest):
            directory = Path(tempfile.mkdtemp(prefix=f".{target.name}.build-", dir=target.parent))
            directories.append(directory)
            stage = directory / "candidate"
            stages[target] = stage
            fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as destination:
                if target == output:
                    with candidate.open("rb") as source:
                        _copy_stream(source, destination)
                else:
                    destination.write((json.dumps(report, indent=2) + "\n").encode("utf-8"))
                destination.flush()
                os.fsync(destination.fileno())
        if (_sha256(stages[output]) != report["custom"]["sha256"]
                or stages[output].stat().st_size != report["custom"]["size"]):
            raise CustomFirmwareError("staged firmware differs from verified candidate")
        source_check()
        for target in (output, manifest):
            if _ioniq5_target_identity(target) != identities[target]:
                raise CustomFirmwareError(f"output changed during build: {target}")
            if identities[target] is not None:
                backup = stages[target].parent / "previous"
                os.link(target, backup, follow_symlinks=False)
                backups[target] = backup
                # link() changes ctime; retain the post-link identity for commit.
                identities[target] = _ioniq5_target_identity(backup)
        for target in (output, manifest):
            if _ioniq5_target_identity(target) != identities[target]:
                raise CustomFirmwareError(f"output changed before commit: {target}")
            info = stages[target].stat()
            stage_inode = (info.st_dev, info.st_ino)
            try:
                if identities[target] is None:
                    # Atomic no-clobber publication if another writer won the race.
                    os.link(stages[target], target)
                else:
                    os.replace(stages[target], target)
            finally:
                # Also recover if a syscall completes just before interruption.
                if target.exists():
                    info = target.lstat()
                    if (info.st_dev, info.st_ino) == stage_inode:
                        installed[target] = stage_inode
        for parent in {output.parent, manifest.parent}:
            _ioniq5_sync_directory(parent)
    except BaseException as exc:
        errors = []
        for target, inode in reversed(list(installed.items())):
            try:
                info = target.lstat()
                if (info.st_dev, info.st_ino) != inode:
                    raise CustomFirmwareError("published file was replaced by another writer")
                if target in backups:
                    os.replace(backups[target], target)
                else:
                    target.unlink()
            except BaseException as rollback_error:
                errors.append(f"{target}: {rollback_error}")
        if errors:
            retain_backups = True
            raise CustomFirmwareError(
                "publication failed; rollback incomplete: " + "; ".join(errors)
                + "; recovery directories: " + ", ".join(map(str, directories))
            ) from exc
        raise
    finally:
        if not retain_backups:
            for directory in directories:
                shutil.rmtree(directory)


def _normalise_archive_name(relative: Path) -> str:
    if relative.is_absolute() or not relative.parts:
        raise CustomFirmwareError(f"invalid overlay path: {relative}")
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise CustomFirmwareError(f"unsafe overlay path: {relative}")
    name = "./" + relative.as_posix()
    if len(name.encode("utf-8")) > 100:
        raise CustomFirmwareError(
            f"overlay path is too long for the retained ustar format: {relative}"
        )
    return name


def _proof_entries() -> list[_OverlayEntry]:
    service = f"""[Unit]
Description=IONIQ custom firmware proof {PAYLOAD_VERSION}
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/bin/sh /etc/ioniq-custom/proof.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
""".encode("utf-8")
    script = f"""#!/bin/sh
set -eu
umask 077
{{
    echo 'IONIQ5_CUSTOM_FIRMWARE_PROOF=1'
    echo 'PAYLOAD_VERSION={PAYLOAD_VERSION}'
    date -u '+UTC=%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || true
}} > /var/log/IONIQ5_CUSTOM_FIRMWARE_PROOF
sync /var/log/IONIQ5_CUSTOM_FIRMWARE_PROOF 2>/dev/null || sync
""".encode("utf-8")
    return [
        _OverlayEntry("./etc/ioniq-custom", "dir", 0o755),
        _OverlayEntry("./etc/ioniq-custom/proof.sh", "file", 0o755, script),
        _OverlayEntry(
            "./etc/systemd/system/ioniq-custom-proof.service",
            "file",
            0o644,
            service,
        ),
        _OverlayEntry(
            "./etc/systemd/system/multi-user.target.wants/ioniq-custom-proof.service",
            "symlink",
            0o777,
            linkname="../ioniq-custom-proof.service",
        ),
    ]


def _overlay_entries(root: Path) -> list[_OverlayEntry]:
    if not root.is_dir():
        raise CustomFirmwareError(f"overlay is not a directory: {root}")
    result: list[_OverlayEntry] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        name = _normalise_archive_name(relative)
        info = path.lstat()
        mode = stat.S_IMODE(info.st_mode)
        if stat.S_ISDIR(info.st_mode):
            result.append(_OverlayEntry(name, "dir", mode))
        elif stat.S_ISREG(info.st_mode):
            result.append(_OverlayEntry(name, "file", mode, path.read_bytes()))
        elif stat.S_ISLNK(info.st_mode):
            target = os.readlink(path)
            target_path = Path(target)
            if target_path.is_absolute() or ".." in target_path.parts:
                raise CustomFirmwareError(
                    f"overlay symlink must stay relative to its archive directory: {relative}"
                )
            result.append(_OverlayEntry(name, "symlink", mode, linkname=target))
        else:
            raise CustomFirmwareError(f"unsupported overlay file type: {relative}")
    return result


def _append_entries(raw_tar: Path, entries: Iterable[_OverlayEntry]) -> list[str]:
    appended: list[str] = []
    with tarfile.open(raw_tar, mode="a", format=tarfile.USTAR_FORMAT) as archive:
        for entry in entries:
            info = tarfile.TarInfo(entry.name)
            info.uid = 0
            info.gid = 0
            info.uname = "root"
            info.gname = "root"
            info.mode = entry.mode
            info.mtime = 0
            if entry.kind == "dir":
                info.type = tarfile.DIRTYPE
                info.size = 0
                archive.addfile(info)
            elif entry.kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = entry.linkname
                info.size = 0
                archive.addfile(info)
            elif entry.kind == "file":
                import io

                info.type = tarfile.REGTYPE
                info.size = len(entry.data)
                archive.addfile(info, io.BytesIO(entry.data))
            else:
                raise CustomFirmwareError(f"internal overlay type error: {entry.kind}")
            appended.append(entry.name)
    return appended


def _verify_plaintext_payload(plain_gzip: Path, expected: dict[str, bytes]) -> None:
    with tarfile.open(plain_gzip, mode="r:gz") as archive:
        members = archive.getmembers()
        for name, content in expected.items():
            matches = [member for member in members if member.name == name]
            if not matches:
                raise CustomFirmwareError(f"generated archive is missing {name}")
            member = matches[-1]
            handle = archive.extractfile(member)
            if handle is None or handle.read() != content:
                raise CustomFirmwareError(f"generated archive content mismatch: {name}")


def _verify_encrypted_candidate(candidate: Path, expected: dict[str, bytes], work: Path) -> dict[str, object]:
    device_name = work / "verify" / DEVICE_BASENAME
    device_name.parent.mkdir()
    os.link(candidate, device_name)
    decrypted = work / "verify" / "candidate.tar.gz"
    CRYPT.decrypt_native(device_name, decrypted, force=True, chunk_size=1 << 20)
    _verify_plaintext_payload(decrypted, expected)
    report, _ = CRYPT.analyze(device_name)
    if report.get("error") or not report.get("integrity_valid"):
        raise CustomFirmwareError(f"encrypted candidate verification failed: {report}")
    return report


def ioniq5_custom_firmware_build(
    genuine_envelope: Path,
    output: Path,
    *,
    overlay: Path | None = None,
    include_proof: bool = True,
    force: bool = False,
    manifest: Path | None = None,
) -> dict[str, object]:
    """Build and verify one custom rootfs envelope.

    The source is never modified.  Existing output or manifest files are
    refused unless ``force`` is true.
    """

    genuine_envelope = genuine_envelope.expanduser().resolve()
    output = output.expanduser().absolute()
    output = output.parent.resolve() / output.name
    manifest = (
        manifest.expanduser().absolute()
        if manifest is not None
        else output.with_name(output.name + ".manifest.json")
    )
    manifest = manifest.parent.resolve() / manifest.name
    if genuine_envelope.name != DEVICE_BASENAME:
        raise CustomFirmwareError(
            f"genuine envelope must retain device basename {DEVICE_BASENAME!r}"
        )
    if not genuine_envelope.is_file():
        raise CustomFirmwareError(f"genuine envelope not found: {genuine_envelope}")
    if output == genuine_envelope or manifest == genuine_envelope:
        raise CustomFirmwareError("output and manifest must not alias the genuine envelope")
    if output == manifest:
        raise CustomFirmwareError("output and manifest must be different files")
    identities = {path: _ioniq5_target_identity(path) for path in (output, manifest)}
    source_inode = _ioniq5_source_identity(genuine_envelope.stat())[:2]
    for path, identity in identities.items():
        if identity is not None and identity[:2] == source_inode:
            raise CustomFirmwareError("output must not alias the genuine envelope")
        if identity is not None and not force:
            raise CustomFirmwareError(f"output already exists (use --force): {path}")
    entries: list[_OverlayEntry] = []
    if include_proof:
        entries.extend(_proof_entries())
    if overlay is not None:
        entries.extend(_overlay_entries(overlay.expanduser().resolve()))
    if not entries:
        raise CustomFirmwareError("no overlay entries were selected")

    expected = {
        entry.name: entry.data for entry in entries if entry.kind == "file"
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    fd = os.open(genuine_envelope, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as source_handle, tempfile.TemporaryDirectory(prefix="ioniq-custom-") as temporary:
        work = Path(temporary)
        info = os.fstat(source_handle.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise CustomFirmwareError("genuine envelope must be a regular file")
        source_identity = _ioniq5_source_identity(info)
        source_size = info.st_size
        # All cryptographic operations read this private snapshot, including
        # the basename-dependent decryptor and original-trailer lookup.
        snapshot = work / "source" / DEVICE_BASENAME
        snapshot.parent.mkdir(mode=0o700)
        digest = hashlib.sha256()
        with snapshot.open("xb") as destination:
            for block in iter(lambda: source_handle.read(COPY_CHUNK), b""):
                digest.update(block)
                destination.write(block)
        snapshot.chmod(0o400)
        source_hash = digest.hexdigest()
        def source_check():
            """Confirm the source and the immutable working copy still agree."""
            _ioniq5_check_source(source_handle, genuine_envelope, source_identity, source_hash)
            if _sha256(snapshot) != source_hash:
                raise CustomFirmwareError("private genuine envelope snapshot changed")
        source_check()
        source_report, _ = CRYPT.analyze(snapshot)
        if source_report.get("error") or not source_report.get("integrity_valid"):
            raise CustomFirmwareError(f"genuine envelope failed TE2 validation: {source_report}")
        body_size = int(source_report["body_size"])
        decrypted = work / "genuine.tar.gz"
        raw_tar = work / "rootfs.tar"
        compressed = work / "custom.tar.gz"
        padded = work / "custom.padded"
        encrypted = work / DEVICE_BASENAME

        CRYPT.decrypt_native(
            snapshot, decrypted, force=True, chunk_size=1 << 20
        )
        with gzip.open(decrypted, "rb") as source, raw_tar.open("wb") as destination:
            _copy_stream(source, destination)
        appended = _append_entries(raw_tar, entries)
        with raw_tar.open("rb") as source, compressed.open("wb") as raw_output:
            with gzip.GzipFile(
                filename="", fileobj=raw_output, mode="wb", compresslevel=9, mtime=0
            ) as destination:
                _copy_stream(source, destination)
        compressed_size = compressed.stat().st_size
        if compressed_size > body_size:
            raise CustomFirmwareError(
                f"custom rootfs is {compressed_size - body_size} bytes over the "
                f"{body_size}-byte plaintext ceiling"
            )
        shutil.copyfile(compressed, padded)
        with padded.open("r+b") as handle:
            handle.truncate(body_size)
        CRYPT.encrypt_native(
            padded,
            encrypted,
            force=True,
            from_envelope=snapshot,
            chunk_size=1 << 20,
        )
        if encrypted.stat().st_size != source_size:
            raise CustomFirmwareError("custom envelope size differs from the genuine envelope")
        _verify_encrypted_candidate(encrypted, expected, work)

        report = {
            "schema": "ioniq5-custom-firmware/v1",
            "tool": {"name": "ioniq5_custom_firmware", "version": TOOL_VERSION},
            "payload_version": PAYLOAD_VERSION,
            "device_basename": DEVICE_BASENAME,
            "genuine": {
                "path": str(genuine_envelope), "size": source_size,
                "sha256": source_hash, "body_size": body_size,
            },
            "custom": {
                "path": str(output), "size": encrypted.stat().st_size,
                "sha256": _sha256(encrypted), "compressed_size": compressed_size,
                "zero_padding": body_size - compressed_size, "te2_integrity_valid": True,
            },
            "overlay": {
                "proof_included": include_proof,
                "source": str(overlay) if overlay is not None else None,
                "members": appended,
            },
            "limitations": [
                "This verifies the offline envelope and payload bytes, not head-unit installation or boot.",
                "The output must be served to the head unit under the basename mango-rootfs.tar.gz.",
                "The default proof service only writes /var/log/IONIQ5_CUSTOM_FIRMWARE_PROOF.",
                "Publication rolls back catchable failures; two filenames are not crash-atomic. Verify hashes before use.",
            ],
        }
        _ioniq5_publish_pair(encrypted, report, output, manifest, identities, source_check)
        return report


def ioniq5_custom_firmware_main(argv: list[str] | None = None) -> int:
    """Run the command-line builder."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("genuine", type=Path, help="genuine mango-rootfs.tar.gz TE2 envelope")
    parser.add_argument("output", type=Path, help="custom envelope output path")
    parser.add_argument("--overlay", type=Path, help="optional root-relative overlay directory")
    parser.add_argument("--no-proof", action="store_true", help="omit the built-in proof service")
    parser.add_argument("--force", action="store_true", help="replace output and manifest")
    parser.add_argument("--manifest", type=Path, help="explicit JSON manifest path")
    arguments = parser.parse_args(argv)
    try:
        report = ioniq5_custom_firmware_build(
            arguments.genuine,
            arguments.output,
            overlay=arguments.overlay,
            include_proof=not arguments.no_proof,
            force=arguments.force,
            manifest=arguments.manifest,
        )
    except (CustomFirmwareError, CRYPT.CryptError, OSError, tarfile.TarError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(ioniq5_custom_firmware_main())
