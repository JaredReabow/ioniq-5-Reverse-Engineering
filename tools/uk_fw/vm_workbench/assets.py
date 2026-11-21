"""Admit and stage compatible local Gen5W VM data by exact digest."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import errno
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import sys
from typing import BinaryIO, Callable

from .wifi_sim.integration import ADVANCED_SHA256, PAGE_SHA256, PAYLOAD_SHA256
from .wifi_sim.session import MANIFEST_SHA256


class AssetError(ValueError):
    """The bundle is missing, incompatible, or cannot be copied safely."""


@dataclass(frozen=True)
class AssetMember:
    """One verified input selected from the supported VM profile."""

    name: str
    size: int
    sha256: str


@dataclass(frozen=True)
class Assets:
    """Verified bundle location and members for one workspace preparation."""

    directory: Path
    members: tuple[AssetMember, ...]

    @property
    def recipe(self) -> Path:
        return self.directory / "startup.sh"

    @property
    def guest_dbus(self) -> Path:
        return self.directory / "libdbus-1.so.3"

    @property
    def wifi_sim_dir(self) -> Path | None:
        if any(member.name.startswith("wifi-sim/") for member in self.members):
            return self.directory / "wifi-sim"
        return None


_MANIFEST = "gen5w-assets.json"
_PROFILE = "gen5w-eu-260128"
_MIB = 1024**2
_CHUNK = 8 * _MIB
_MANIFEST_LIMIT = 8192
_WORKSPACE_INPUTS = ("bzImage", "rootfs.img", "manifest.bin", "seed_dev.bin", "seed_user.bin")
_NONCLONE_ERRORS = {errno.ENOTSUP, errno.ENOSYS, errno.ENOTTY, errno.EXDEV, errno.EINVAL}


def _fixture(value: bytes) -> tuple[str, int]:
    """Digest the same synthetic fixtures used by vm_boot.py."""
    return hashlib.sha256(value).hexdigest(), len(value)


_BASE_PINS = {
    "bzImage": ("85e0086202758117015437a5ce7b580d7d32484807d1953c3a16e571f65f3f59", 16 * _MIB),
    "rootfs.img": ("4953a005683e009e84390bbf07d65a6a3313cc6abd692a3023e6b660066d036f", 32 * 1024 * _MIB),
    "manifest.bin": _fixture(struct.pack("<II", 0xe, 0x24).ljust(64, b"\0")),
    "seed_dev.bin": _fixture(b"IONIQ-VM-ONLY-dev".ljust(64, b"\0")),
    "seed_user.bin": _fixture(b"IONIQ-VM-ONLY-user".ljust(64, b"\0")),
    "startup.sh": ("25a2ee9726d160c03b52c8dc3c5a76aaba33dd57d7d4be7ecba6f9b2f34485ae", _MIB),
    "libdbus-1.so.3": ("36697a6178ee8e1d952bf74d20d3edb2b89695a032502819c0d161026bb82083", _MIB),
}
_WIFI_PINS = {
    "wifi-sim/payload.tar.gz": (PAYLOAD_SHA256, 64 * _MIB),
    "wifi-sim/payload-hashes.json": (MANIFEST_SHA256, _MIB),
    "wifi-sim/WifiPage.qml": (PAGE_SHA256, _MIB),
    "wifi-sim/advanced-live.qml": (ADVANCED_SHA256, _MIB),
}
Progress = Callable[[str, int, int], None]


def assets_manifest(*, wifi_sim: bool = False) -> dict:
    """Return the exact public manifest for this supported profile."""
    pins = {**_BASE_PINS, **(_WIFI_PINS if wifi_sim else {})}
    return {"schema": 1, "profile": _PROFILE,
            "files": {name: details[0] for name, details in pins.items()}}


def _object_without_duplicates(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise AssetError("Gen5W asset manifest has duplicate keys")
        result[key] = value
    return result


def _invalid_number(_: str) -> None:
    raise AssetError("Gen5W asset manifest contains an invalid number")


def _canonical_directory(directory: Path) -> Path:
    """Resolve system aliases while refusing a symlink as the selected directory."""
    directory = Path(directory)
    try:
        normalized = directory.resolve(strict=True)
        if directory.is_symlink() or not normalized.is_dir():
            raise AssetError("Expected a regular Gen5W directory")
        return normalized
    except (OSError, RuntimeError):
        raise AssetError("Gen5W directory is missing or unavailable") from None


@contextmanager
def _open_directory(path: Path | str, *, parent: int | None = None):
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, dir_fd=parent)
    except OSError:
        raise AssetError("Gen5W directory is missing, linked, or unreadable") from None
    try:
        yield fd
    finally:
        os.close(fd)


@contextmanager
def _open_file(directory: int, filename: str, label: str, limit: int):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        fd = os.open(filename, flags, dir_fd=directory)
    except OSError:
        raise AssetError("Missing, linked, or unreadable Gen5W asset: " + label) from None
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise AssetError("Gen5W asset must be a single-link regular file: " + label)
        if not 0 < info.st_size <= limit:
            raise AssetError("Gen5W asset size out of bounds: " + label)
        yield stream, info


@contextmanager
def _open_member(directory: int, name: str, limit: int):
    if name.startswith("wifi-sim/"):
        with _open_directory("wifi-sim", parent=directory) as wifi:
            with _open_file(wifi, name.removeprefix("wifi-sim/"), name, limit) as file:
                yield file
    else:
        with _open_file(directory, name, name, limit) as file:
            yield file


def _stable(stream: BinaryIO, initial: os.stat_result, name: str) -> None:
    current = os.fstat(stream.fileno())
    fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns", "st_nlink")
    if any(getattr(initial, key) != getattr(current, key) for key in fields):
        raise AssetError("Gen5W asset changed while reading: " + name)


def _digest(stream: BinaryIO, info: os.stat_result, name: str,
            progress: Progress | None) -> str:
    sha256 = hashlib.sha256()
    total = info.st_size
    done = 0
    if progress:
        progress(name, done, total)
    stream.seek(0)
    while done < total:
        data = stream.read(min(_CHUNK, total - done))
        if not data:
            raise AssetError("Gen5W asset ended during verification: " + name)
        sha256.update(data)
        done += len(data)
        if progress:
            progress(name, done, total)
    _stable(stream, info, name)
    return sha256.hexdigest()


def _manifest_pins(directory: int, wifi_sim: bool) -> dict[str, tuple[str, int]]:
    with _open_file(directory, _MANIFEST, _MANIFEST, _MANIFEST_LIMIT) as (stream, info):
        raw = stream.read(_MANIFEST_LIMIT + 1)
        _stable(stream, info, _MANIFEST)
    try:
        manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_without_duplicates,
                              parse_constant=_invalid_number)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise AssetError("Invalid Gen5W asset manifest JSON") from None
    if (not isinstance(manifest, dict) or set(manifest) != {"schema", "profile", "files"}
            or type(manifest["schema"]) is not int or manifest["schema"] != 1
            or manifest["profile"] != _PROFILE or not isinstance(manifest["files"], dict)):
        raise AssetError("Invalid schema or unsupported Gen5W asset profile")
    file_names = set(manifest["files"])
    optional = set(_WIFI_PINS)
    if file_names == set(_BASE_PINS) | optional:
        pins = {**_BASE_PINS, **_WIFI_PINS}
    elif file_names == set(_BASE_PINS) and not wifi_sim:
        pins = _BASE_PINS
    else:
        raise AssetError("Gen5W asset manifest must name exactly the supported files")
    for name, (expected, _) in pins.items():
        if manifest["files"][name] != expected:
            raise AssetError("Gen5W asset manifest pin mismatch: " + name)
    return pins


def assets_admit(directory: Path, *, wifi_sim: bool = False,
                 progress: Progress | None = None) -> Assets:
    """Verify the local manifest and every listed asset against the supported pins."""
    directory = _canonical_directory(directory)
    try:
        members = []
        with _open_directory(directory) as bundle:
            for name, (expected, limit) in _manifest_pins(bundle, wifi_sim).items():
                with _open_member(bundle, name, limit) as (stream, info):
                    if not hmac.compare_digest(_digest(stream, info, name, progress), expected):
                        raise AssetError("Gen5W asset hash mismatch: " + name)
                    members.append(AssetMember(name, info.st_size, expected))
        return Assets(directory, tuple(members))
    except OSError:
        raise AssetError("Could not read the Gen5W asset bundle") from None


def _try_linux_reflink(source: BinaryIO, target: BinaryIO) -> bool:
    if not sys.platform.startswith("linux"):
        return False
    import fcntl
    try:
        # Linux FICLONE operates on descriptors, so checked names stay opaque.
        fcntl.ioctl(target.fileno(), 0x40049409, source.fileno())
    except OSError as error:
        if error.errno not in _NONCLONE_ERRORS:
            raise
        return False
    return True


def _try_macos_clone(source: BinaryIO, info: os.stat_result, destination: int,
                     filename: str) -> bool:
    """Use Apple's descriptor-relative clone when the filesystem supports it."""
    if sys.platform != "darwin" or getattr(info, "st_flags", 0):
        return False
    import ctypes
    try:
        clone = ctypes.CDLL(None, use_errno=True).fclonefileat
    except AttributeError:
        return False
    clone.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32)
    clone.restype = ctypes.c_int
    if clone(source.fileno(), destination, os.fsencode(filename), 0) == 0:
        return True
    code = ctypes.get_errno()
    if code in _NONCLONE_ERRORS or code == errno.EPERM:
        return False
    raise OSError(code, os.strerror(code))


def _copy_extent(source: BinaryIO, target: BinaryIO, start: int, end: int) -> None:
    source.seek(start)
    target.seek(start)
    remaining = end - start
    while remaining:
        block = source.read(min(remaining, _CHUNK))
        if not block:
            raise AssetError("Gen5W asset ended during copying")
        if target.write(block) != len(block):
            raise AssetError("Could not write a complete Gen5W asset block")
        remaining -= len(block)


def _copy_buffered(source: BinaryIO, target: BinaryIO, total: int) -> None:
    """Copy sparse extents when supported, falling back to buffered file I/O."""
    if not hasattr(os, "SEEK_DATA") or not hasattr(os, "SEEK_HOLE"):
        _copy_extent(source, target, 0, total)
        return
    cursor = 0
    while cursor < total:
        try:
            start = os.lseek(source.fileno(), cursor, os.SEEK_DATA)
            end = min(total, os.lseek(source.fileno(), start, os.SEEK_HOLE))
        except OSError as error:
            if error.errno == errno.ENXIO:
                break  # The remainder is a hole.
            if error.errno not in _NONCLONE_ERRORS:
                raise
            _copy_extent(source, target, cursor, total)
            return
        if not cursor <= start < end <= total:
            raise AssetError("Invalid extent while copying a Gen5W asset")
        _copy_extent(source, target, start, end)
        cursor = end
    target.truncate(total)


@contextmanager
def _create_file(directory: int, filename: str):
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    fd = os.open(filename, flags, 0o600, dir_fd=directory)
    with os.fdopen(fd, "w+b", buffering=0) as stream:
        os.fchmod(stream.fileno(), 0o600)
        yield stream


@contextmanager
def _copy_target(workspace: int, filename: str, source: BinaryIO,
                 info: os.stat_result, is_image: bool):
    if is_image and _try_macos_clone(source, info, workspace, filename):
        fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=workspace)
        with os.fdopen(fd, "rb", buffering=0) as target:
            copied = os.fstat(target.fileno())
            if not stat.S_ISREG(copied.st_mode) or copied.st_nlink != 1 or copied.st_uid != os.geteuid():
                raise AssetError("Cloned Gen5W image is not a locally owned regular file")
            os.fchmod(target.fileno(), 0o600)
            yield target, True
    else:
        with _create_file(workspace, filename) as target:
            yield target, is_image and _try_linux_reflink(source, target)


def _copy_member(bundle: int, workspace: int, member: AssetMember,
                 limit: int, progress: Progress | None) -> None:
    with _open_member(bundle, member.name, limit) as (source, info):
        if info.st_size != member.size:
            raise AssetError("Gen5W asset changed before copying: " + member.name)
        filename = member.name.rsplit("/", 1)[-1]
        with _copy_target(workspace, filename, source, info, member.name == "rootfs.img") as (target, cloned):
            if not cloned:
                # Unbuffered source reads are unnecessary, but SEEK_DATA changes
                # the underlying fd position. Use an unbuffered view for extents.
                with os.fdopen(os.dup(source.fileno()), "rb", buffering=0) as view:
                    _copy_buffered(view, target, info.st_size)
            _stable(source, info, member.name)
            copied = os.fstat(target.fileno())
            if copied.st_size != info.st_size or not hmac.compare_digest(
                    _digest(target, copied, member.name, progress), member.sha256):
                raise AssetError("Gen5W asset copy hash mismatch: " + member.name)


def _workspace_pins(assets: Assets) -> dict[str, tuple[str, int]]:
    names = tuple(member.name for member in assets.members)
    pins = {**_BASE_PINS, **_WIFI_PINS} if any(name in _WIFI_PINS for name in names) else _BASE_PINS
    if len(names) != len(pins) or set(names) != set(pins):
        raise AssetError("Gen5W workspace copy needs a complete admitted profile")
    for member in assets.members:
        digest, limit = pins[member.name]
        if member.sha256 != digest or type(member.size) is not int or not 0 < member.size <= limit:
            raise AssetError("Gen5W workspace copy input does not match the supported pins")
    return pins


def assets_copy_workspace(assets: Assets, output_root: Path, destination: Path,
                          *, progress: Progress | None = None) -> Path:
    """Copy verified inputs to a new private child and write boot verification metadata.

    This function owns only a child it successfully creates. It removes that
    partial child on failure and never removes a pre-existing collision.
    """
    pins = _workspace_pins(assets)
    root = _canonical_directory(output_root)
    source_root = _canonical_directory(assets.directory)
    destination = Path(destination)
    if (destination.name in ("", ".", "..") or _canonical_directory(destination.parent) != root
            or any(character in str(root / destination.name) for character in ",\r\n")):
        raise AssetError("Gen5W workspace must be a new direct runtime child with a safe name")
    result = root / destination.name
    if result == source_root or source_root in result.parents or result in source_root.parents:
        raise AssetError("Gen5W workspace must be separate from the asset directory")
    created = False
    try:
        with _open_directory(root) as out, _open_directory(source_root) as bundle:
            info = os.fstat(out)
            if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
                raise AssetError("Gen5W runtime directory must be owned locally with mode 0700")
            os.mkdir(destination.name, mode=0o700, dir_fd=out)
            created = True
            with _open_directory(destination.name, parent=out) as workspace:
                if any(name in pins for name in _WIFI_PINS):
                    os.mkdir("wifi-sim", mode=0o700, dir_fd=workspace)
                for member in assets.members:
                    limit = pins[member.name][1]
                    if member.name in _WIFI_PINS:
                        with _open_directory("wifi-sim", parent=workspace) as wifi:
                            _copy_member(bundle, wifi, member, limit, progress)
                    else:
                        _copy_member(bundle, workspace, member, limit, progress)
                metadata = {"schema": 1, "synthetic_seeds": True,
                            "sha256": {name: pins[name][0] for name in _WORKSPACE_INPUTS}}
                with _create_file(workspace, "prepare.json") as target:
                    payload = (json.dumps(metadata, indent=2) + "\n").encode("ascii")
                    if target.write(payload) != len(payload):
                        raise AssetError("Could not write complete Gen5W workspace metadata")
    except BaseException as exc:
        if created and result.parent == root and result.exists() and not result.is_symlink():
            shutil.rmtree(result)
        if isinstance(exc, FileExistsError):
            raise AssetError("Gen5W workspace already exists") from None
        if isinstance(exc, OSError):
            raise AssetError("Could not create or verify the Gen5W workspace copy") from None
        raise
    return result
