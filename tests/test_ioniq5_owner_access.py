"""Check recovery-overlay composition and private credential provisioning."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

from cryptography import x509
from cryptography.hazmat.primitives import serialization

from tools.uk_fw import ioniq5_owner_access as access


class OwnerAccessTests(unittest.TestCase):
    """Use a clearly labelled web-interface stub until its independent tests run."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.addCleanup(self.temporary.cleanup)

    def test_browser_credentials_are_private_stable_and_independently_random(self):
        private = self.root / "private"
        private.mkdir(mode=0o700)
        paths = access.ioniq5_owner_access_provision_web_credentials(private)
        password = paths["password"].read_bytes()
        self.assertGreaterEqual(len(password.strip()), 16)
        certificate = x509.load_pem_x509_certificate(paths["certificate"].read_bytes())
        key = serialization.load_pem_private_key(paths["key"].read_bytes(), password=None)
        self.assertEqual(certificate.public_key().public_numbers(), key.public_key().public_numbers())
        for path in paths.values():
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        with self.assertRaisesRegex(ValueError, "already exist"):
            access.ioniq5_owner_access_provision_web_credentials(private)
        self.assertEqual(password, paths["password"].read_bytes())

    def test_composition_uses_independent_auth_and_excludes_network_alternatives(self):
        def fragment(**kwargs):
            output = kwargs["output"]
            output.mkdir()
            target = output / "web-interface-stub"
            target.write_bytes(b"fixture")
            return {"module": "stub-web-interface", "version": "fixture",
                    "files": {"web-interface-stub": {
                        "sha256": hashlib.sha256(b"fixture").hexdigest(),
                        "mode": "0o600", "uid": 0, "gid": 0}}, "symlinks": {}}
        stub = types.SimpleNamespace(ioniq5_owner_web_generate=fragment)
        arguments = {name: self.root / name for name in (
            "dropbear", "public_key", "host_key", "password_hash", "web_binary",
            "web_password", "tls_cert", "tls_key")}
        # This tests the composition contract; each real channel has its own
        # execution/integration tests. No peer's in-flight web source is imported.
        with mock.patch.dict("sys.modules", {"tools.uk_fw.ioniq5_owner_web": stub}):
            with mock.patch.object(access, "ioniq5_owner_ssh_generate", side_effect=fragment) as wired:
                with mock.patch.object(access, "ioniq5_owner_console_generate", return_value={
                    "module": "local-only", "version": "fixture", "files": {}, "symlinks": {}}):
                    # Give the SSH fragment a different member to check merging.
                    def wired_fragment(**kwargs):
                        result = fragment(**kwargs)
                        output = kwargs["output"]
                        (output / "web-interface-stub").rename(output / "wired-interface-stub")
                        result["files"]["wired-interface-stub"] = result["files"].pop("web-interface-stub")
                        return result
                    wired.side_effect = wired_fragment
                    output = self.root / "merged"
                    report = access.ioniq5_owner_access_generate(**arguments, output=output)
        self.assertTrue(wired.call_args.kwargs["independent_access"])
        self.assertTrue(wired.call_args.kwargs["web_console"])
        self.assertEqual(set(report["files"]), {"web-interface-stub", "wired-interface-stub"})
        self.assertIn("TTL/serial console", report["excluded"])
        self.assertIn("Wi-Fi access point", report["excluded"])
        self.assertEqual(json.loads(output.with_name("merged.manifest.json").read_text()), report)
        self.assertEqual(list(self.root.glob(".owner-access-*")), [])


if __name__ == "__main__":
    unittest.main()
