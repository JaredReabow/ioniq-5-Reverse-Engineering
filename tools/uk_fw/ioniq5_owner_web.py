#!/usr/bin/env python3
"""Stage the independent HTTPS owner terminal overlay.

The browser terminal is an authentication recovery path over the already
proven USB-Ethernet link. It has its own PBKDF2 verifier, TLS key, session
policy, root PTY, and systemd service. It does not use SSH, PAM, ``/etc/passwd``,
Wi-Fi, serial, or OEM account configuration.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import lzma
import os
from pathlib import Path
import secrets
import shutil
import stat
import struct
import tempfile

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
_BASE = "opt/ioniq-owner"
_VERSION = "1.0.3"
_BINARY_VERSION = "1.0.2"
_SERVICE = "ioniq-owner-web.service"
_NETWORK_SERVICE = "ioniq-owner-ethernet.service"
_DEVICE = "sys-subsystem-net-devices-ownerusb0.device"
_LISTEN = "10.42.0.1:8443"
_PBKDF2_ITERATIONS = 600_000
_PASSWORD_MAXIMUM = 256
_PINNED_BINARY_SHA256 = (
    "18c6ac2eb0f5e3d92661bcf979f447e6bd211ab7541bc83847f5efb26c8e807b"
)

_UNIT = f'''[Unit]
Description=IONIQ5 independent HTTPS root terminal {_VERSION}
BindsTo={_NETWORK_SERVICE} {_DEVICE}
After={_NETWORK_SERVICE} {_DEVICE}
ConditionPathExists=/sys/class/net/ownerusb0
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
Type=simple
User=root
UMask=0077
RuntimeDirectory=ioniq-owner-web
RuntimeDirectoryMode=0700
Environment=HOME=/run/ioniq-owner-web
ExecStart=/{_BASE}/bin/owner-web-console --listen={_LISTEN} --credentials=/{_BASE}/web/credentials.json --tls-cert=/{_BASE}/web/tls-cert.pem --tls-key=/{_BASE}/web/tls-key.pem
Restart=on-failure
RestartSec=2s
KillMode=control-group
TimeoutStopSec=12s
'''

_LAUNCHER = r'''#!/bin/sh
# Expand the prebuilt binary once into private RAM; no compilation or image
# rebuilding occurs. Verify its exact hash before every execution.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
umask 077
base=/opt/ioniq-owner
run=/run/ioniq-owner-web
[ ! -L "$run" ] && [ -d "$run" ] || exit 1
[ "$(stat -c '%u:%g:%a' "$run")" = 0:0:700 ] || exit 1
binary="$run/owner-web-console"
[ ! -L "$binary" ] || exit 1
valid=
if [ -f "$binary" ] && [ "$(stat -c '%u:%g:%a' "$binary")" = 0:0:700 ]; then
    current=$(sha256sum "$binary")
    [ "${current%% *}" != @SHA256@ ] || valid=1
fi
if [ -z "$valid" ]; then
    temporary=$(mktemp "$run/.console.XXXXXX")
    trap 'rm -f "$temporary"' EXIT HUP INT TERM
    xz -dc "$base/bin/owner-web-console.xz" >"$temporary"
    current=$(sha256sum "$temporary")
    [ "${current%% *}" = @SHA256@ ] || { echo 'Owner browser binary integrity failure' >&2; exit 1; }
    chmod 700 "$temporary"
    mv -f "$temporary" "$binary"
    trap - EXIT HUP INT TERM
fi
exec "$binary" "$@"
'''

_SESSION = {
    "session_ttl_seconds": 900,
    "idle_timeout_seconds": 300,
    "max_sessions": 4,
    "max_terminals": 4,
    "max_login_attempts": 5,
    "login_window_seconds": 60,
    "ticket_ttl_seconds": 30,
    "websocket_read_seconds": 60,
}


def _read_regular(path: Path, limit: int, *, private: bool = True) -> bytes:
    """Read one bounded regular private file without following symlinks."""
    path = Path(path)
    if ".." in path.parts:
        raise ValueError("parent traversal is not allowed")
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= limit:
            raise ValueError("input must be a nonempty, bounded regular file")
        if private and stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError("private input permissions must exclude group and other")
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("input exceeds its size limit")
    return data


def _binary_version(binary: Path) -> str:
    """Validate the reviewed static binary and return its exact pinned digest."""
    data = _read_regular(binary, 64 * 1024 * 1024, private=False)
    if len(data) < 64 or data[:7] != b"\x7fELF\x02\x01\x01":
        raise ValueError("expected a little-endian ELF64 executable")
    kind, machine, version, entry, phoff = struct.unpack_from("<HHIQQ", data, 16)
    ehsize, phsize, phnum = struct.unpack_from("<HHH", data, 52)
    if (
        kind not in (2, 3)
        or machine != 62
        or version != 1
        or ehsize != 64
        or phsize != 56
        or not 0 < phnum <= 1024
        or phoff < 64
        or phoff + phsize * phnum > len(data)
    ):
        raise ValueError("invalid x86-64 ELF header or program-header table")
    executable_entry = False
    for position in range(phoff, phoff + phsize * phnum, phsize):
        ptype, flags, offset, address, _, size, memory_size, _ = struct.unpack_from(
            "<IIQQQQQQ", data, position
        )
        if ptype == 3:
            raise ValueError("PT_INTERP is forbidden; the console must be static")
        if offset + size > len(data) or (ptype == 1 and size > memory_size):
            raise ValueError("ELF segment is outside the executable")
        if ptype == 1 and flags & 1 and address <= entry < address + size:
            executable_entry = True
    if not executable_entry:
        raise ValueError("ELF entry is not in an executable load segment")
    if b"IONIQ5_OWNER_WEB_VERSION=" + _BINARY_VERSION.encode() not in data:
        raise ValueError("binary is missing the exact owner-console version marker")
    digest = hashlib.sha256(data).hexdigest()
    if digest != _PINNED_BINARY_SHA256:
        raise ValueError("console digest does not match the reviewed static build")
    return digest


def _password_verifier(password_file: Path) -> dict[str, object]:
    """Create a salted PBKDF2 verifier without staging the plaintext file."""
    raw = _read_regular(password_file, _PASSWORD_MAXIMUM + 2)
    password = raw
    if password.endswith(b"\r\n"):
        password = password[:-2]
    elif password.endswith((b"\n", b"\r")):
        password = password[:-1]
    if b"\n" in password or b"\r" in password:
        raise ValueError("recovery password file must contain exactly one line")
    if not 1 <= len(password) <= _PASSWORD_MAXIMUM:
        raise ValueError("recovery password must contain between 1 and 256 bytes")
    if any(byte < 32 or byte == 127 for byte in password):
        raise ValueError("recovery password must not contain control characters")
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password, salt, _PBKDF2_ITERATIONS, 32)
    return {
        "algorithm": "pbkdf2-sha256",
        "iterations": _PBKDF2_ITERATIONS,
        "salt": base64.b64encode(salt).decode("ascii"),
        "hash": base64.b64encode(derived).decode("ascii"),
    }


def _tls_material(certificate_file: Path, key_file: Path) -> tuple[bytes, bytes]:
    """Require a matching, currently valid, pinned self-signed IP certificate."""
    certificate_data = _read_regular(certificate_file, 64 * 1024)
    key_data = _read_regular(key_file, 32 * 1024)
    try:
        certificate = x509.load_pem_x509_certificate(certificate_data)
        private_key = serialization.load_pem_private_key(key_data, password=None)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid PEM certificate or private key") from exc
    now = dt.datetime.now(dt.timezone.utc)
    if not certificate.not_valid_before_utc <= now <= certificate.not_valid_after_utc:
        raise ValueError("TLS certificate is outside its validity window")
    try:
        san = certificate.extensions.get_extension_for_class(
            x509.SubjectAlternativeName
        ).value
        addresses = san.get_values_for_type(x509.IPAddress)
    except x509.ExtensionNotFound as exc:
        raise ValueError("TLS certificate must include IP SAN 10.42.0.1") from exc
    if any(str(address) == "10.42.0.1" for address in addresses) is False:
        raise ValueError("TLS certificate must include IP SAN 10.42.0.1")
    if certificate.subject != certificate.issuer:
        raise ValueError("TLS certificate must be self-signed")
    try:
        certificate.verify_directly_issued_by(certificate)
    except (ValueError, TypeError) as exc:
        raise ValueError("TLS certificate signature is not self-valid") from exc
    certificate_public = certificate.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    private_public = private_key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    if certificate_public != private_public:
        raise ValueError("TLS certificate and private key do not match")
    if isinstance(private_key, rsa.RSAPrivateKey):
        if private_key.key_size < 3072:
            raise ValueError("RSA TLS keys must be at least 3072 bits")
    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        if not isinstance(
            private_key.curve, (ec.SECP256R1, ec.SECP384R1, ec.SECP521R1)
        ):
            raise ValueError("EC TLS keys must use P-256, P-384, or P-521")
    elif not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise ValueError("unsupported TLS private-key algorithm")
    return certificate_data, key_data


def _credentials_json(password_file: Path) -> bytes:
    """Serialize the private runtime policy with no plaintext credential."""
    config = {
        "format": 1,
        "password": _password_verifier(password_file),
        "session": dict(_SESSION),
    }
    return (json.dumps(config, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _manifest(
    files: dict[str, tuple[bytes, int]], binary_sha256: str
) -> dict[str, object]:
    """Build target ownership and security metadata for the overlay fragment."""
    return {
        "format": 1,
        "fragment": True,
        "module": "owner-web-console",
        "version": _VERSION,
        "transport": "usb-ethernet",
        "archive_ownership": {"uid": 0, "gid": 0},
        "listen": _LISTEN,
        "authentication": "independent-pbkdf2-sha256",
        "session": dict(_SESSION),
        "binary_sha256": binary_sha256,
        "binary_compression": "xz",
        "binary_version": _BINARY_VERSION,
        "ui_embedded": True,
        "files": {
            name: {
                "sha256": hashlib.sha256(data).hexdigest(),
                "mode": oct(mode),
                "uid": 0,
                "gid": 0,
            }
            for name, (data, mode) in sorted(files.items())
        },
        "symlinks": {},
        "hardware_limits": [
            "One matching USB Ethernet adapter at a time; main owns link admission and the 8443 firewall rule.",
            "At most four concurrent authenticated browser sessions and four root PTYs.",
            "One active PTY per browser session; tickets are one-use and expire after 30 seconds.",
        ],
        "limitations": [
            "Head-unit TLS listener, browser compatibility, and PTY behavior require target/product verification.",
            "The browser must accept the pinned self-signed certificate for IP address 10.42.0.1.",
            "The client must statically configure 10.42.0.2/24; the browser console provides no DHCP or routing.",
            "The root terminal intentionally exposes full root command execution to an authenticated owner.",
            "Archive every overlay member as root:root with the manifest modes; host staging metadata is not target metadata.",
        ],
        "excluded": [
            "SSH, Dropbear, .ssh, PAM, and /etc/passwd authentication",
            "Wi-Fi, Radxa CDC-ECM, USB gadget, and USB-serial transports",
            "unauthenticated shell, Telnet, file manager, and remote-control API",
            "vehicle-control code and hardware action",
        ],
    }


def ioniq5_owner_web_generate(
    *,
    binary: Path,
    password_file: Path,
    tls_cert: Path,
    tls_key: Path,
    output: Path,
) -> dict[str, object]:
    """Validate private inputs and stage the HTTPS owner-console overlay.

    The destination parent must exist. Existing output and sibling manifest
    paths, including dangling links, are rejected. Supplied files are never
    executed; the manifest carries target root ownership for the firmware
    packer to apply.
    """
    output = Path(output)
    if ".." in output.parts or output.name in ("", ".", ".."):
        raise ValueError("unsafe output path")
    output = output.parent.resolve(strict=True) / output.name
    manifest_path = output.with_name(output.name + ".manifest.json")
    if os.path.lexists(output) or os.path.lexists(manifest_path):
        raise ValueError("output or sibling manifest already exists")

    binary = Path(binary)
    password_file = Path(password_file)
    tls_cert = Path(tls_cert)
    tls_key = Path(tls_key)
    binary_sha256 = _binary_version(binary)
    binary_data = _read_regular(binary, 64 * 1024 * 1024, private=False)
    if hashlib.sha256(binary_data).hexdigest() != binary_sha256:
        raise ValueError("console binary changed after validation")
    certificate_data, key_data = _tls_material(tls_cert, tls_key)
    credentials = _credentials_json(password_file)
    files = {
        f"{_BASE}/bin/owner-web-console": (_LAUNCHER.replace("@SHA256@", binary_sha256).encode("ascii"), 0o755),
        f"{_BASE}/bin/owner-web-console.xz": (lzma.compress(binary_data, preset=9), 0o644),
        f"{_BASE}/web/credentials.json": (credentials, 0o600),
        f"{_BASE}/web/tls-cert.pem": (certificate_data, 0o600),
        f"{_BASE}/web/tls-key.pem": (key_data, 0o600),
        f"etc/systemd/system/{_SERVICE}": (_UNIT.encode("ascii"), 0o644),
    }
    manifest = _manifest(files, binary_sha256)

    staging = Path(tempfile.mkdtemp(prefix=".ioniq-owner-web-", dir=output.parent))
    manifest_created = False
    output_created = False
    try:
        for name, (data, mode) in files.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(mode)
            if hashlib.sha256(target.read_bytes()).hexdigest() != manifest["files"][name]["sha256"]:
                raise OSError(f"staged digest mismatch: {name}")
        (staging / f"{_BASE}/web").chmod(0o700)
        (staging / f"{_BASE}/bin").chmod(0o755)
        for directory in (
            staging / "opt",
            staging / "opt/ioniq-owner",
            staging / "etc",
            staging / "etc/systemd",
            staging / "etc/systemd/system",
        ):
            directory.chmod(0o755)
        staging.chmod(0o700)
        staging.rename(output)
        output_created = True
        manifest_path.write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest_path.chmod(0o600)
        manifest_created = True
        with manifest_path.open("rb") as stream:
            os.fsync(stream.fileno())
        return manifest
    except BaseException:
        if manifest_created:
            manifest_path.unlink(missing_ok=True)
        if output_created:
            shutil.rmtree(output)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def _main() -> int:
    """Expose a narrow staging CLI for reproducible overlay assembly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--password-file", type=Path, required=True)
    parser.add_argument("--tls-cert", type=Path, required=True)
    parser.add_argument("--tls-key", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", action="version", version=_VERSION)
    arguments = parser.parse_args()
    manifest = ioniq5_owner_web_generate(
        binary=arguments.binary,
        password_file=arguments.password_file,
        tls_cert=arguments.tls_cert,
        tls_key=arguments.tls_key,
        output=arguments.output,
    )
    print(
        f"owner-web-console {manifest['version']} "
        f"{manifest['binary_sha256']} {arguments.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
