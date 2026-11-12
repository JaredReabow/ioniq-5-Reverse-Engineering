"""Fixture-only tests for the independent HTTPS owner terminal overlay."""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import importlib.util
import ipaddress
import json
import lzma
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID


REPOSITORY = Path(__file__).parents[1]
TOOL = REPOSITORY / "tools/uk_fw/ioniq5_owner_web.py"
SPEC = importlib.util.spec_from_file_location("ioniq5_owner_web", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load owner web tool")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture_elf() -> bytes:
    """Build a structural static ELF carrying the exact console version."""
    payload = b"IONIQ5_OWNER_WEB_VERSION=1.0.2\0" + b"\0" * 128
    ident = b"\x7fELF\x02\x01\x01" + b"\0" * 9
    header = struct.pack(
        "<16sHHIQQQIHHHHHH",
        ident,
        2,
        62,
        1,
        0x400078,
        64,
        0,
        0,
        64,
        56,
        1,
        0,
        0,
        0,
    )
    program = struct.pack(
        "<IIQQQQQQ",
        1,
        5,
        120,
        0x400000,
        0,
        len(payload),
        len(payload),
        0x1000,
    )
    return header + program + payload


class OwnerWebFixtureTests(unittest.TestCase):
    """Exercise generation policy without executing target code."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.original_digest = MODULE._PINNED_BINARY_SHA256
        MODULE._PINNED_BINARY_SHA256 = hashlib.sha256(fixture_elf()).hexdigest()

    @classmethod
    def tearDownClass(cls) -> None:
        MODULE._PINNED_BINARY_SHA256 = cls.original_digest

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="owner-web-test-")
        self.root = Path(self.temporary.name).resolve()
        self.binary = self.root / "owner-web-console"
        self.binary.write_bytes(fixture_elf())
        self.binary.chmod(0o700)
        self.password = self.root / "recovery-password.txt"
        self.password.write_text("fixture recovery password\n")
        self.password.chmod(0o600)
        self.cert, self.key = self.write_certificate()
        self.output = self.root / "overlay"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_certificate(
        self, *, san: str = "10.42.0.1", issuer_mismatch: bool = False
    ) -> tuple[Path, Path]:
        """Create a matching P-384 self-signed test certificate and key."""
        key = ec.generate_private_key(ec.SECP384R1())
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "IONIQ owner web")])
        issuer = (
            x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "unexpected issuer")])
            if issuer_mismatch
            else subject
        )
        now = dt.datetime.now(dt.timezone.utc)
        certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - dt.timedelta(minutes=5))
            .not_valid_after(now + dt.timedelta(days=3650))
            .add_extension(
                x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(san))]),
                critical=False,
            )
            .sign(key, hashes.SHA384())
        )
        cert_path = self.root / f"tls-{san}-{issuer_mismatch}.pem"
        key_path = self.root / f"tls-{san}-{issuer_mismatch}.key"
        cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        key_path.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        cert_path.chmod(0o600)
        key_path.chmod(0o600)
        return cert_path, key_path

    def generate(self, output: Path | None = None) -> dict:
        """Call the public generator with fixture inputs."""
        return MODULE.ioniq5_owner_web_generate(
            binary=self.binary,
            password_file=self.password,
            tls_cert=self.cert,
            tls_key=self.key,
            output=output or self.output,
        )

    def test_generated_fragment_is_independent_and_contains_no_plaintext(self) -> None:
        manifest = self.generate()
        self.assertEqual(manifest["version"], "1.0.3")
        self.assertEqual(manifest["listen"], "10.42.0.1:8443")
        self.assertEqual(manifest["authentication"], "independent-pbkdf2-sha256")
        self.assertEqual(manifest["symlinks"], {})
        self.assertEqual(manifest["archive_ownership"], {"uid": 0, "gid": 0})
        self.assertNotIn("SSH authentication", " ".join(manifest["excluded"]))
        for forbidden in ("ssh", "dropbear", "passwd", "wifi", "telnet"):
            self.assertNotIn(forbidden, MODULE._UNIT.lower())
        self.assertIn(
            "BindsTo=ioniq-owner-ethernet.service "
            "sys-subsystem-net-devices-ownerusb0.device",
            MODULE._UNIT,
        )
        self.assertIn("--listen=10.42.0.1:8443", MODULE._UNIT)
        self.assertIn("KillMode=control-group", MODULE._UNIT)

        credentials = (
            self.output / "opt/ioniq-owner/web/credentials.json"
        ).read_bytes()
        self.assertNotIn(b"fixture recovery password", credentials)
        policy = json.loads(credentials)
        salt = base64.b64decode(policy["password"]["salt"], validate=True)
        expected = hashlib.pbkdf2_hmac(
            "sha256",
            b"fixture recovery password",
            salt,
            policy["password"]["iterations"],
            32,
        )
        self.assertEqual(
            expected,
            base64.b64decode(policy["password"]["hash"], validate=True),
        )
        self.assertEqual(policy["session"]["max_terminals"], 4)
        self.assertNotIn("fixture recovery password", json.dumps(manifest))

        for name, metadata in manifest["files"].items():
            path = self.output / name
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), metadata["sha256"]
            )
            self.assertEqual(path.stat().st_mode & 0o777, int(metadata["mode"], 8))
            self.assertEqual((metadata["uid"], metadata["gid"]), (0, 0))
        self.assertEqual(
            (self.output / "opt/ioniq-owner/web").stat().st_mode & 0o777,
            0o700,
        )
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertFalse(
            (self.output / "etc/systemd/system/ioniq-owner-auth.service").exists()
        )

    def test_private_inputs_and_password_shape_are_enforced(self) -> None:
        bad_cases = (
            b"",
            b"\n",
            b"line one\nline two\n",
            b"contains\x00nul\n",
            b"x" * 258,
        )
        for index, value in enumerate(bad_cases):
            with self.subTest(index=index):
                self.password.write_bytes(value)
                self.password.chmod(0o600)
                with self.assertRaises(ValueError):
                    self.generate(self.root / f"bad-password-{index}")

        self.password.write_text("good password\n")
        self.password.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "permissions"):
            self.generate(self.root / "public-password")

        self.password.chmod(0o600)
        link = self.root / "password-link"
        link.symlink_to(self.password)
        with self.assertRaises(OSError):
            MODULE.ioniq5_owner_web_generate(
                binary=self.binary,
                password_file=link,
                tls_cert=self.cert,
                tls_key=self.key,
                output=self.root / "symlink-password",
            )

    def test_tls_policy_rejects_wrong_san_issuer_and_mismatch(self) -> None:
        wrong_cert, wrong_key = self.write_certificate(san="10.42.0.2")
        with self.assertRaisesRegex(ValueError, "IP SAN"):
            MODULE.ioniq5_owner_web_generate(
                binary=self.binary,
                password_file=self.password,
                tls_cert=wrong_cert,
                tls_key=wrong_key,
                output=self.root / "wrong-san",
            )
        issuer_cert, issuer_key = self.write_certificate(issuer_mismatch=True)
        with self.assertRaisesRegex(ValueError, "self-signed"):
            MODULE.ioniq5_owner_web_generate(
                binary=self.binary,
                password_file=self.password,
                tls_cert=issuer_cert,
                tls_key=issuer_key,
                output=self.root / "wrong-issuer",
            )
        with self.assertRaisesRegex(ValueError, "do not match"):
            MODULE.ioniq5_owner_web_generate(
                binary=self.binary,
                password_file=self.password,
                tls_cert=self.cert,
                tls_key=wrong_key,
                output=self.root / "mismatch",
            )

    def test_binary_digest_and_static_elf_are_required(self) -> None:
        with mock.patch.object(MODULE, "_PINNED_BINARY_SHA256", self.original_digest):
            with self.assertRaisesRegex(ValueError, "digest"):
                self.generate(self.root / "wrong-digest")
        self.binary.write_bytes(b"not an elf")
        with mock.patch.object(
            MODULE,
            "_PINNED_BINARY_SHA256",
            hashlib.sha256(self.binary.read_bytes()).hexdigest(),
        ):
            with self.assertRaisesRegex(ValueError, "ELF64"):
                self.generate(self.root / "wrong-elf")

    def test_existing_output_and_manifest_are_never_overwritten(self) -> None:
        self.output.mkdir()
        sentinel = self.output / "keep"
        sentinel.write_text("keep")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.generate()
        self.assertEqual(sentinel.read_text(), "keep")
        sentinel.unlink()
        self.output.rmdir()
        manifest = self.output.with_name(self.output.name + ".manifest.json")
        manifest.write_text("keep manifest")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.generate()
        self.assertEqual(manifest.read_text(), "keep manifest")

    def test_cli_exposes_version_without_secret_arguments(self) -> None:
        result = subprocess.run(
            [sys.executable, str(TOOL), "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "1.0.3")
        source = TOOL.read_text()
        self.assertNotIn("--password ", source)
        self.assertIn("--password-file", source)

    def test_compressed_launcher_and_service_paths_are_executable_on_target(self) -> None:
        """Catch relative systemd paths and verify the packed bytes round-trip."""
        manifest = self.generate()
        root = self.output / "opt/ioniq-owner"
        self.assertEqual(lzma.decompress((root / "bin/owner-web-console.xz").read_bytes()),
                         self.binary.read_bytes())
        launcher = root / "bin/owner-web-console"
        result = subprocess.run(["/bin/sh", "-n", str(launcher)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(manifest["binary_sha256"], launcher.read_text())
        unit = (self.output / "etc/systemd/system/ioniq-owner-web.service").read_text()
        command = next(line.split("=", 1)[1] for line in unit.splitlines()
                       if line.startswith("ExecStart="))
        self.assertTrue(command.startswith("/opt/ioniq-owner/bin/owner-web-console "))
        for flag in ("credentials", "tls-cert", "tls-key"):
            self.assertIn(f"--{flag}=/opt/ioniq-owner/web/", command)

    @unittest.skipUnless(
        os.environ.get("IONIQ5_OWNER_WEB_DOCKER_SMOKE") == "1",
        "set IONIQ5_OWNER_WEB_DOCKER_SMOKE=1 for the exact binary smoke test",
    )
    def test_exact_linux_binary_serves_https_over_loopback(self) -> None:
        """Start the exact packaged ELF and query its status from the same container."""
        binary = REPOSITORY / "work/owner-web-build/bin/owner-web-console-v1.0.2"
        if not binary.is_file():
            self.skipTest("the pinned linux/amd64 binary has not been built")
        with mock.patch.object(
            MODULE, "_PINNED_BINARY_SHA256", self.original_digest
        ):
            smoke_directory = Path(
                tempfile.mkdtemp(
                    prefix="exact-smoke-",
                    dir=REPOSITORY / "work/owner-web-build",
                )
            )
            self.addCleanup(shutil.rmtree, smoke_directory)
            output = smoke_directory / "overlay"
            MODULE.ioniq5_owner_web_generate(
                binary=binary,
                password_file=self.password,
                tls_cert=self.cert,
                tls_key=self.key,
                output=output,
            )
        script = """
set -eu
cp -a /fragment/. /tmp/root
chown -R 0:0 /tmp/root
cp -a /tmp/root/opt/. /opt/
test -x /tmp/root/opt/ioniq-owner/bin/owner-web-console
mkdir -p /run/ioniq-owner-web
chmod 700 /run/ioniq-owner-web
HOME=/run/ioniq-owner-web \
  /tmp/root/opt/ioniq-owner/bin/owner-web-console \
  --listen=127.0.0.1:18443 \
  --credentials=/tmp/root/opt/ioniq-owner/web/credentials.json \
  --tls-cert=/tmp/root/opt/ioniq-owner/web/tls-cert.pem \
  --tls-key=/tmp/root/opt/ioniq-owner/web/tls-key.pem &
server=$!
trap 'kill "$server" 2>/dev/null || true; wait "$server" 2>/dev/null || true' EXIT
python3 - <<'PY'
import json
import ssl
import time
import urllib.request

context = ssl._create_unverified_context()
url = "https://127.0.0.1:18443/api/status"
for _ in range(40):
    try:
        with urllib.request.urlopen(url, context=context, timeout=1) as response:
            status = json.load(response)
        break
    except Exception:
        time.sleep(0.1)
else:
    raise SystemExit("owner web console did not answer on loopback")
assert status["version"] == "1.0.2", status
assert status["authenticated"] is False, status
assert status["csrf"], status
print("EXACT_OWNER_WEB_LOOPBACK_OK")
PY
"""
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "-v",
                f"{output}:/fragment:ro",
                "ioniq-owner-auth-fixture:bookworm",
                "sh",
                "-euc",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("EXACT_OWNER_WEB_LOOPBACK_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
