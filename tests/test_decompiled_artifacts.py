"""Check the published decompilation claims against the decompiled output.

The Ghidra runs themselves are manual and their output lives under ignored
`work/`, so these tests are skipped when it is absent. What they assert is the
link between an evidence note and the artifact it describes: if the decompiled
tree changes, the note's numbers stop matching and this fails.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
IVI = ROOT / "work/decompiled/ivi-shell"
LAUNCHER = ROOT / "work/decompiled/AppLauncher"
AUDIT = ROOT / "vm/evidence/vendor-userspace-260128/ivi-shell-input-audit.txt"


def function_files(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.c")) if directory.is_dir() else []


@unittest.skipUnless(IVI.is_dir(), "run tools/uk_fw/decompile.py on ivi-shell.so first")
class IviShellAuditTests(unittest.TestCase):
    def test_audit_note_exists_and_is_manifested(self):
        self.assertTrue(AUDIT.is_file())
        manifest = json.loads((ROOT / "vm/evidence-manifest.json").read_text())
        published = {record["published"] for record in manifest["files"]}
        self.assertIn(str(AUDIT.relative_to(ROOT)), published)

    def test_function_count_matches_the_note(self):
        files = function_files(IVI)
        self.assertGreaterEqual(len(files), 400)
        self.assertIn("400 functions", AUDIT.read_text())

    def test_no_keyboard_or_pointer_dispatch_is_decompiled(self):
        """The note's central claim: zero protocol keyboard/pointer handling."""
        pattern = re.compile(r"wl_keyboard|wl_pointer|notify_key|notify_button")
        offenders = [path.name for path in function_files(IVI)
                     if pattern.search(path.read_text(errors="replace"))]
        self.assertEqual(offenders, [])

    def test_activation_and_input_panel_code_is_present(self):
        names = " ".join(path.name for path in function_files(IVI))
        for expected in ("activate_binding", "click_to_activate_binding",
                         "touch_to_activate_binding", "show_input_panel_surface"):
            self.assertIn(expected, names)


APNAVI = ROOT / "work/decompiled/AppNavi"


@unittest.skipUnless(APNAVI.is_dir(), "run the AppNavi decompile first")
class AppNaviInventoryTests(unittest.TestCase):
    """The inventory must account for every body-bearing function."""

    def inventory(self):
        path = APNAVI / "functions.tsv"
        self.assertTrue(path.is_file(), "functions.tsv is the inventory of record")
        rows = [line.split("\t") for line in
                path.read_text(errors="replace").splitlines()[1:] if line.strip()]
        return rows

    def test_every_body_bearing_function_has_an_artifact(self):
        import re
        import zlib

        def base(entry, name):
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
            return f"{entry}_{safe[:60]}_{zlib.crc32(safe.encode()) & 0xffffffff:08x}"

        rows = self.inventory()
        without = [row for row in rows
                   if not (APNAVI / (base(row[0], row[1]) + ".c")).exists()
                   and not (APNAVI / (base(row[0], row[1]) + ".asm")).exists()]
        self.assertEqual(without, [], f"{len(without)} functions have no artifact")

    def test_refusals_are_published_as_listings_with_a_reason(self):
        listings = sorted(APNAVI.glob("*.asm"))
        self.assertTrue(listings, "refusals must be published, not dropped")
        for path in listings:
            header = path.read_text(errors="replace").splitlines()[1]
            self.assertIn("decompiler refused:", header)


@unittest.skipUnless(LAUNCHER.is_dir(),
                     "run tools/uk_fw/decompile.py on AppLauncher first")
class AppLauncherDecompileTests(unittest.TestCase):
    def test_launcher_has_no_direct_exec_or_fork_import(self):
        """Children are spawned through Qt, which is why the execve shim works."""
        pattern = re.compile(r"PTR_(execve|execv|fork|posix_spawn|vfork)")
        self.assertGreater(len(function_files(LAUNCHER)), 1000)
        offenders = [path.name for path in function_files(LAUNCHER)
                     if pattern.search(path.read_text(errors="replace"))]
        self.assertEqual(offenders, [])

    def test_signature_check_strings_are_recovered(self):
        matches = [path for path in function_files(LAUNCHER)
                   if "CheckSign" in path.read_text(errors="replace")]
        self.assertTrue(matches)


if __name__ == "__main__":
    unittest.main()
