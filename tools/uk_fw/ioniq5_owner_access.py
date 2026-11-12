#!/usr/bin/env python3
"""Compose the selected Ethernet/authentication recovery firmware overlay.

Each channel module owns its defaults and validation. This coordinator combines
their public outputs and rejects conflicting members. It does not flash a car,
arm USB media, change the Radxa image, or include Wi-Fi/TTL network alternatives.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import stat
import sys
import tempfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.uk_fw.ioniq5_owner_ssh import ioniq5_owner_ssh_generate
from tools.uk_fw.ioniq5_owner_console import ioniq5_owner_console_generate

_VERSION = "4.0.2"


def ioniq5_owner_access_provision_web_credentials(directory: Path) -> dict[str, Path]:
    """Create a distinct browser password and stable private TLS identity once."""
    directory = Path(directory)
    if directory.is_symlink() or stat.S_IMODE(directory.stat().st_mode) != 0o700:
        raise ValueError("credential directory must be private mode 0700")
    paths = {name: directory / filename for name, filename in {
        "password": "owner_web_password.txt", "certificate": "owner_web_tls.crt",
        "key": "owner_web_tls.key"}.items()}
    if any(os.path.lexists(path) for path in paths.values()):
        raise ValueError("browser credentials already exist; reuse retained credentials")
    private = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "IONIQ5 Owner Recovery")])
    import ipaddress
    now = datetime.now(timezone.utc)
    certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
        .public_key(private.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=2)).not_valid_after(now + timedelta(days=3650))
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("10.42.0.1"))]),
                       critical=False).sign(private, hashes.SHA256()))
    values = {
        "password": secrets.token_urlsafe(15).encode() + b"\n",
        "certificate": certificate.public_bytes(serialization.Encoding.PEM),
        "key": private.private_bytes(serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8, serialization.NoEncryption()),
    }
    created = []
    try:
        for name, path in paths.items():
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            created.append(path)
            with os.fdopen(fd, "wb") as stream:
                stream.write(values[name])
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException:
        for path in created:
            path.unlink()
        raise
    return paths


def ioniq5_owner_access_generate(*, dropbear: Path, public_key: Path, host_key: Path,
                                password_hash: Path, web_binary: Path, web_password: Path,
                                tls_cert: Path, tls_key: Path, output: Path) -> dict:
    """Combine independent Ethernet, SSH, browser and local terminal modules."""
    from tools.uk_fw.ioniq5_owner_web import ioniq5_owner_web_generate
    output = Path(output)
    if ".." in output.parts or output.name in ("", ".", ".."):
        raise ValueError("unsafe output path")
    output = output.parent.resolve(strict=True) / output.name
    manifest_path = output.with_name(output.name + ".manifest.json")
    if os.path.lexists(output) or os.path.lexists(manifest_path):
        raise ValueError("output or manifest already exists")
    temporary = Path(tempfile.mkdtemp(prefix=".owner-access-", dir=output.parent))
    merged = temporary / "merged"
    merged.mkdir(mode=0o700)
    published = False
    try:
        parts = []
        wired = temporary / "wired"
        parts.append((wired, ioniq5_owner_ssh_generate(
            dropbear=dropbear, public_key=public_key, host_key=host_key,
            password_hash=password_hash, output=wired,
            independent_access=True, web_console=True)))
        console = temporary / "console"
        parts.append((console, ioniq5_owner_console_generate(output=console)))
        web = temporary / "web"
        parts.append((web, ioniq5_owner_web_generate(
            binary=web_binary, password_file=web_password, tls_cert=tls_cert,
            tls_key=tls_key, output=web)))
        files, links, modules = {}, {}, []
        for root, fragment in parts:
            modules.append({"module": fragment.get("module", fragment.get("transport")),
                            "version": fragment["version"]})
            for name, metadata in fragment["files"].items():
                source = root / name
                data = source.read_bytes()
                if hashlib.sha256(data).hexdigest() != metadata["sha256"]:
                    raise ValueError(f"fragment content changed: {name}")
                if name in files or name in links:
                    raise ValueError(f"conflicting overlay member: {name}")
                target = merged / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                target.chmod(int(metadata["mode"], 8))
                files[name] = metadata
            for name, target in fragment.get("symlinks", {}).items():
                if name in files or name in links:
                    raise ValueError(f"conflicting overlay link: {name}")
                path = merged / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(target)
                links[name] = target
        for directory in merged.rglob("*"):
            if directory.is_dir() and not directory.is_symlink():
                directory.chmod(0o700 if directory.name in ("keys", "web") else 0o755)
        report = {
            "format": 3, "version": _VERSION, "modules": modules,
            "primary_transport": "external-usb-ethernet",
            "ssh_authentication": ["publickey", "nonempty-password"],
            "independent_recovery": ["HTTPS browser terminal password", "USB-keyboard local terminal"],
            "excluded": ["Wi-Fi access point", "Radxa ECM", "TTL/serial console"],
            "archive_ownership": {"uid": 0, "gid": 0},
            "files": dict(sorted(files.items())), "symlinks": dict(sorted(links.items())),
            "limitations": ["Installed car login and local terminal visibility still require head-unit verification.",
                            "Browser TLS identity is self-signed; verify its retained certificate fingerprint."],
        }
        staged_manifest = temporary / "manifest.json"
        staged_manifest.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        staged_manifest.chmod(0o600)
        # Publish without replacing an existing user artifact. Roll back our
        # manifest if output publication fails; prior firmware is untouched.
        os.link(staged_manifest, manifest_path)
        published = True
        output.mkdir(mode=0o700)
        try:
            merged.rename(output)
        except BaseException:
            output.rmdir()
            raise
        return report
    except BaseException:
        if published:
            manifest_path.unlink()
        raise
    finally:
        shutil.rmtree(temporary)


def ioniq5_owner_access_main(argv: list[str] | None = None) -> int:
    """Build the selected recovery overlay using explicit retained inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("dropbear", "public-key", "host-key", "password-hash", "web-binary",
                 "web-password", "tls-cert", "tls-key", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    ioniq5_owner_access_generate(**vars(args))
    print(f"Created owner authentication recovery overlay {_VERSION}: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(ioniq5_owner_access_main())
