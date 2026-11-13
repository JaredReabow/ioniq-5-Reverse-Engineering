"""Exercise helper provisioning guards without a network, compiler, or device."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'tools/uk_fw/build-nbdfuse-direct.sh'


class NbdfuseDirectBuildTests(unittest.TestCase):
    """Source must be pinned and old builds must survive provisioning failures."""

    def test_version_getter_does_not_build_or_need_linux(self):
        result = subprocess.run(['/bin/bash', str(SCRIPT), '--helper-version'],
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), 'ioniq-nbdfuse-direct 1.14.2-ioniq-direct.1')

    def test_existing_build_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / 'keep-source-and-data'
            marker.write_text('retained')
            result = subprocess.run(['/bin/bash', str(SCRIPT), str(root)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(marker.read_text(), 'retained')
            self.assertEqual(list(root.iterdir()), [marker])

    def test_bad_source_hash_stops_before_extract_patch_or_compile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            commands = root / 'bin'
            commands.mkdir()
            log = root / 'calls'
            for name in ('curl', 'sha256sum', 'tar', 'patch', 'pkg-config', 'gcc', 'readelf'):
                body = '#!/bin/sh\nprintf "%s\\n" "${0##*/}" >>"$BUILD_TEST_LOG"\n'
                if name == 'curl':
                    body += 'for last in "$@"; do :; done\nprintf altered-source >"$last"\n'
                elif name == 'sha256sum':
                    body += 'cat >/dev/null\nexit 1\n'
                else:
                    body += 'exit 0\n'
                path = commands / name
                path.write_text(body)
                path.chmod(0o755)
            result = subprocess.run(['/bin/bash', str(SCRIPT), str(root / 'new-build')],
                                    env=os.environ | {'PATH': str(commands) + ':' + os.environ['PATH'],
                                                      'BUILD_TEST_LOG': str(log)},
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            called = log.read_text().splitlines()
            self.assertIn('curl', called)
            self.assertIn('sha256sum', called)
            self.assertNotIn('tar', called)
            self.assertNotIn('patch', called)
            self.assertNotIn('gcc', called)


if __name__ == '__main__':
    unittest.main()
