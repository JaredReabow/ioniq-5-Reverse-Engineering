"""Asset admission and staging tests with synthetic local data only."""

from dataclasses import replace
import errno
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/uk_fw"))
from vm_workbench import assets


class AssetAdmissionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name).resolve()
        self.bundle = self.parent / "private input folder"
        self.bundle.mkdir()
        self.manifest = self.bundle / "gen5w-assets.json"
        self.runtime = self.parent / "runtime"
        self.runtime.mkdir(mode=0o700)
        self.runtime.chmod(0o700)

        def _small_pins(names):
            return {name: (hashlib.sha256(self.member_bytes(name)).hexdigest(), 128)
                    for name in names}

        # Substitute small trusted inputs. The public manifest cannot supply
        # its own compatibility pins in either the fixture or the product.
        for key in ("_BASE_PINS", "_WIFI_PINS"):
            patch = mock.patch.object(assets, key, _small_pins(getattr(assets, key)))
            patch.start()
            self.addCleanup(patch.stop)
        self.write_bundle()

    @staticmethod
    def member_bytes(name):
        return f"fixture for {name}\n".encode()

    def write_bundle(self, wifi=False):
        manifest = assets.assets_manifest(wifi_sim=wifi)
        for name in manifest["files"]:
            path = self.bundle / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(self.member_bytes(name))
        self.manifest.write_text(json.dumps(manifest))

    def test_complete_bundle_copies_to_private_workspace_with_checked_metadata(self):
        progress = []
        admitted = assets.assets_admit(self.bundle, progress=lambda *data: progress.append(data))
        self.assertEqual(admitted.wifi_sim_dir, None)
        self.assertEqual(admitted.recipe, self.bundle / "startup.sh")
        self.assertEqual(admitted.guest_dbus, self.bundle / "libdbus-1.so.3")
        (self.bundle / "notes-ignored.txt").write_text("unlisted input")
        dest = self.runtime / "session with spaces"
        copied = []
        self.assertEqual(assets.assets_copy_workspace(
            admitted, self.runtime, dest, progress=lambda *data: copied.append(data)
        ), dest)
        self.assertEqual(progress, copied)
        self.assertEqual(len(progress), 2 * len(admitted.members))
        self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o700)
        self.assertFalse((dest / "notes-ignored.txt").exists())
        for member in admitted.members:
            self.assertEqual((dest / member.name).read_bytes(), self.member_bytes(member.name))
            self.assertEqual(stat.S_IMODE((dest / member.name).stat().st_mode), 0o600)
        metadata = json.loads((dest / "prepare.json").read_text())
        records = assets.assets_manifest()["files"]
        self.assertEqual(metadata, {"schema": 1, "synthetic_seeds": True,
                         "sha256": {name: records[name] for name in assets._WORKSPACE_INPUTS}})

    def test_wifi_is_a_complete_pinned_group(self):
        with self.assertRaisesRegex(assets.AssetError, "exactly the supported files"):
            assets.assets_admit(self.bundle, wifi_sim=True)
        self.write_bundle(wifi=True)
        admitted = assets.assets_admit(self.bundle, wifi_sim=True)
        self.assertEqual(admitted.wifi_sim_dir, self.bundle / "wifi-sim")
        dest = assets.assets_copy_workspace(admitted, self.runtime, self.runtime / "wifi")
        self.assertEqual((dest / "wifi-sim/WifiPage.qml").read_bytes(),
                         self.member_bytes("wifi-sim/WifiPage.qml"))
        self.assertEqual(stat.S_IMODE((dest / "wifi-sim").stat().st_mode), 0o700)
        manifest = assets.assets_manifest(wifi_sim=True)
        del manifest["files"]["wifi-sim/WifiPage.qml"]
        self.manifest.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(assets.AssetError, "exactly the supported files"):
            assets.assets_admit(self.bundle)

    def test_manifest_rejects_bad_schema_unknown_names_and_shifting_pins(self):
        for key, value, message in (("schema", True, "Invalid schema"),
                                    ("schema", 1.0, "Invalid schema"),
                                    ("profile", "other-image", "unsupported"),
                                    ("extra", "", "Invalid schema")):
            with self.subTest(key=key, value=value):
                manifest = assets.assets_manifest()
                manifest[key] = value
                self.manifest.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(assets.AssetError, message):
                    assets.assets_admit(self.bundle)
        for name, message in (("rootfs.img", "pin mismatch"), ("../secret", "supported files"),
                              ("credentials.json", "supported files")):
            with self.subTest(name=name):
                manifest = assets.assets_manifest()
                manifest["files"][name] = "0" * 64
                self.manifest.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(assets.AssetError, message):
                    assets.assets_admit(self.bundle)

    def test_strict_json_rejects_duplicates_excess_bytes_and_invalid_utf8(self):
        raw = json.dumps(assets.assets_manifest())
        cases = ((raw.replace('"schema": 1', '"schema": 1, "schema": 1').encode(), "duplicate keys"),
                 (raw.replace('"rootfs.img":', '"rootfs.img": "duplicate", "rootfs.img":').encode(),
                  "duplicate keys"), (b'{"schema":NaN}', "invalid number"),
                 (b" " * 8193, "size out of bounds"), (b"\xff", "manifest JSON"))
        for data, message in cases:
            with self.subTest(message=message):
                self.manifest.write_bytes(data)
                with self.assertRaisesRegex(assets.AssetError, message):
                    assets.assets_admit(self.bundle)

    def test_missing_oversized_replaced_and_nonregular_inputs(self):
        path = self.bundle / "rootfs.img"
        for mode, message in (("missing", "Missing"), ("oversize", "size out of bounds"),
                              ("altered", "hash mismatch"), ("fifo", "regular file")):
            with self.subTest(mode=mode):
                path.unlink(missing_ok=True)
                if mode == "oversize":
                    path.write_bytes(b"0" * 129)
                if mode == "altered":
                    path.write_bytes(b"untrusted image")
                if mode == "fifo":
                    os.mkfifo(path)
                with self.assertRaisesRegex(assets.AssetError, message) as caught:
                    assets.assets_admit(self.bundle)
                self.assertNotIn(str(self.bundle), str(caught.exception))

    def test_refuses_symlink_hardlink_and_linked_wifi_directory(self):
        path = self.bundle / "rootfs.img"
        external = self.parent / "external.img"
        path.rename(external)
        path.symlink_to(external)
        with self.assertRaisesRegex(assets.AssetError, "linked"):
            assets.assets_admit(self.bundle)
        path.unlink()
        os.link(external, path)
        with self.assertRaisesRegex(assets.AssetError, "single-link"):
            assets.assets_admit(self.bundle)
        external.unlink()
        bundle_alias = self.parent / "linked input"
        bundle_alias.symlink_to(self.bundle, target_is_directory=True)
        with self.assertRaisesRegex(assets.AssetError, "regular Gen5W directory"):
            assets.assets_admit(bundle_alias)
        self.write_bundle(wifi=True)
        wifi = self.bundle / "wifi-sim"
        wifi.rename(self.parent / "wifi elsewhere")
        wifi.symlink_to(self.parent / "wifi elsewhere", target_is_directory=True)
        with self.assertRaisesRegex(assets.AssetError, "linked"):
            assets.assets_admit(self.bundle, wifi_sim=True)

    def test_copy_refuses_escape_existing_destination_and_nonprivate_root(self):
        admitted = assets.assets_admit(self.bundle)
        outside = self.parent / "outside"
        with self.assertRaisesRegex(assets.AssetError, "new direct runtime child"):
            assets.assets_copy_workspace(admitted, self.runtime, outside)
        with self.assertRaisesRegex(assets.AssetError, "safe name"):
            assets.assets_copy_workspace(admitted, self.runtime, self.runtime / "dir,unsafe")
        existing = self.runtime / "existing"
        existing.mkdir()
        sentinel = existing / "owned-by-another-session"
        sentinel.write_text("preserve me", encoding="utf-8")
        with self.assertRaisesRegex(assets.AssetError, "already exists"):
            assets.assets_copy_workspace(admitted, self.runtime, existing)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve me")
        link = self.runtime / "linked"
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(assets.AssetError, "already exists"):
            assets.assets_copy_workspace(admitted, self.runtime, link)
        self.runtime.chmod(0o755)
        with self.assertRaisesRegex(assets.AssetError, "mode 0700"):
            assets.assets_copy_workspace(admitted, self.runtime, self.runtime / "uncreated")
        self.assertFalse(outside.exists())
        self.assertFalse((self.runtime / "uncreated").exists())

    def test_copy_rehashes_after_admission_and_removes_owned_partial_workspace(self):
        admitted = assets.assets_admit(self.bundle)
        source = self.bundle / "rootfs.img"
        replacement = b"x" * len(source.read_bytes())
        source.write_bytes(replacement)
        dest = self.runtime / "partial"
        with self.assertRaisesRegex(assets.AssetError, "copy hash mismatch"):
            assets.assets_copy_workspace(admitted, self.runtime, dest)
        self.assertFalse(dest.exists())
        self.assertEqual(source.read_bytes(), replacement)
        forged = replace(admitted, members=(replace(admitted.members[0], name="../bad"), *admitted.members[1:]))
        with self.assertRaisesRegex(assets.AssetError, "complete admitted profile"):
            assets.assets_copy_workspace(forged, self.runtime, self.runtime / "forged")

    def test_buffered_copy_handles_missing_sparse_seek(self):
        admitted = assets.assets_admit(self.bundle)
        with mock.patch.object(assets, "_try_macos_clone", return_value=False), \
                mock.patch.object(assets, "_try_linux_reflink", return_value=False), \
                mock.patch.object(assets.os, "lseek", side_effect=OSError(errno.EINVAL, "unsupported")):
            dest = assets.assets_copy_workspace(admitted, self.runtime, self.runtime / "buffered")
        self.assertEqual((dest / "rootfs.img").read_bytes(), self.member_bytes("rootfs.img"))

    def test_buffered_copy_rejects_insufficient_destination_space_and_cleans_up(self):
        admitted = assets.assets_admit(self.bundle)
        image = self.member_bytes("rootfs.img")
        available = len(image) - 1
        disk = SimpleNamespace(f_frsize=1, f_bavail=available)
        dest = self.runtime / "low-space"
        progress = []
        with (mock.patch.object(assets, "_try_macos_clone", return_value=False),
              mock.patch.object(assets, "_try_linux_reflink", return_value=False),
              mock.patch.object(assets.os, "fstatvfs", return_value=disk),
              mock.patch.object(assets.os, "lseek", side_effect=OSError(errno.EINVAL, "unsupported")),
              self.assertRaisesRegex(assets.AssetError,
                                     rf"rootfs\.img: {len(image)} bytes needed, {available} bytes available")):
            assets.assets_copy_workspace(admitted, self.runtime, dest,
                                         copy_progress=lambda *data: progress.append(data))
        self.assertEqual({name for name, _, _ in progress}, {"bzImage"})
        self.assertFalse(dest.exists())
        self.assertEqual((self.bundle / "rootfs.img").read_bytes(), image)

    def test_reflink_skips_buffered_space_check_and_still_verifies_digest(self):
        admitted = assets.assets_admit(self.bundle)
        image = self.member_bytes("rootfs.img")
        for altered in (False, True):
            with self.subTest(altered=altered):
                verified, copied = [], []
                dest = self.runtime / f"clone-{altered}"

                def clone(source, target):
                    content = source.read()
                    target.write(b"x" * len(content) if altered else content)
                    return True

                with (mock.patch.object(assets, "_try_macos_clone", return_value=False),
                      mock.patch.object(assets, "_try_linux_reflink", side_effect=clone),
                      mock.patch.object(assets, "_require_copy_space", wraps=assets._require_copy_space) as capacity):
                    def stage():
                        assets.assets_copy_workspace(admitted, self.runtime, dest,
                                                     progress=lambda *data: verified.append(data),
                                                     copy_progress=lambda *data: copied.append(data))

                    if altered:
                        with self.assertRaisesRegex(assets.AssetError, "copy hash mismatch: rootfs.img"):
                            stage()
                        self.assertFalse(dest.exists())
                    else:
                        stage()
                        self.assertEqual((dest / "rootfs.img").read_bytes(), image)
                self.assertNotIn("rootfs.img", {call.args[2].name for call in capacity.call_args_list})
                self.assertNotIn("rootfs.img", {name for name, _, _ in copied})
                self.assertIn(("rootfs.img", len(image), len(image)), verified)

    def test_buffered_copy_reports_intermediate_written_bytes_before_verifying(self):
        admitted = assets.assets_admit(self.bundle)
        dest = self.runtime / "copy-progress"
        image = self.member_bytes("rootfs.img")
        events = []

        def copied(name, done, total):
            if name == "rootfs.img":
                self.assertEqual((dest / name).stat().st_size, done)
                events.append(("copy", done, total))

        def verified(name, done, total):
            if name == "rootfs.img":
                events.append(("verify", done, total))

        with (mock.patch.object(assets, "_try_macos_clone", return_value=False),
              mock.patch.object(assets, "_try_linux_reflink", return_value=False),
              mock.patch.object(assets.os, "lseek", side_effect=OSError(errno.EINVAL, "unsupported")),
              mock.patch.object(assets, "_CHUNK", 8)):
            assets.assets_copy_workspace(admitted, self.runtime, dest,
                                         progress=verified, copy_progress=copied)
        self.assertEqual(events, [(phase, done, len(image)) for phase in ("copy", "verify")
                                  for done in (0, 8, 16, len(image))])
        self.assertEqual((dest / "rootfs.img").read_bytes(), image)

    def test_partial_buffered_copy_cleans_up_if_space_disappears_or_operator_stops(self):
        admitted = assets.assets_admit(self.bundle)
        for failure, expected, message in (
                (OSError(errno.ENOSPC, "full"), assets.AssetError, "disk space or quota"),
                (InterruptedError("operator stopped"), InterruptedError, "operator stopped")):
            with self.subTest(failure=failure):
                dest = self.runtime / "interrupted-copy"

                def copied(name, done, _total):
                    if name == "rootfs.img" and done > 0:
                        self.assertGreater((dest / name).stat().st_size, 0)
                        raise failure

                with (mock.patch.object(assets, "_try_macos_clone", return_value=False),
                      mock.patch.object(assets, "_try_linux_reflink", return_value=False),
                      mock.patch.object(assets, "_CHUNK", 8),
                      self.assertRaisesRegex(expected, message)):
                    assets.assets_copy_workspace(admitted, self.runtime, dest, copy_progress=copied)
                self.assertFalse(dest.exists())

    def test_sparse_capacity_uses_destination_fragments_for_written_ranges(self):
        total = 4 * 4096
        source, target = self.parent / "sparse-preflight-in", self.parent / "sparse-preflight-out"
        member = assets.AssetMember("rootfs.img", total, "unused by capacity check")
        disk = SimpleNamespace(f_frsize=4096, f_bavail=1)
        source.touch()
        with (source.open("rb") as original, target.open("w+b") as copied,
              mock.patch.object(assets.os, "fstatvfs", return_value=disk),
              mock.patch.object(assets, "_copy_extents", return_value=iter(((4096, 4097), (4100, 4104))))):
            assets._require_copy_space(original, copied, member)
            self.assertEqual(copied.tell(), 0)
        with (source.open("rb") as original, target.open("w+b") as copied,
              mock.patch.object(assets.os, "fstatvfs", return_value=disk),
              mock.patch.object(assets, "_copy_extents", return_value=iter(((4096, 4097), (8192, 8193)))),
              self.assertRaisesRegex(assets.AssetError, "8,192 bytes needed, 4,096 bytes available")):
            assets._require_copy_space(original, copied, member)

    def test_buffered_copy_retains_sparse_data_and_file_length(self):
        source = self.parent / "sparse-in"
        target = self.parent / "sparse-out"
        total = 4 * 1024**2
        with source.open("wb", buffering=0) as stream:
            stream.seek(1024**2)
            stream.write(b"MIDDLE")
            stream.truncate(total)
        with source.open("rb", buffering=0) as original, target.open("w+b", buffering=0) as copied:
            assets._copy_buffered(original, copied, total)
        self.assertEqual(target.read_bytes(), source.read_bytes())
        if hasattr(os, "SEEK_DATA"):
            with source.open("rb") as stream:
                try:
                    hole_is_queriable = os.lseek(stream.fileno(), 0, os.SEEK_DATA) > 0
                except OSError:
                    hole_is_queriable = False
            if hole_is_queriable:
                self.assertLess(target.stat().st_blocks * 512, total)


if __name__ == "__main__":
    unittest.main()
