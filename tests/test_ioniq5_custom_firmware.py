"""Synthetic end-to-end tests for the IONIQ custom rootfs builder."""

from __future__ import annotations

import gzip
import importlib.util
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock


TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "ioniq5_custom_firmware.py"
SPEC = importlib.util.spec_from_file_location("ioniq5_custom_firmware", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CustomFirmwareFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.genuine = self.root / MODULE.DEVICE_BASENAME
        self._make_genuine()

    def _make_genuine(self) -> None:
        raw_tar = self.root / "rootfs.tar"
        with tarfile.open(raw_tar, "w", format=tarfile.USTAR_FORMAT) as archive:
            content = b"stock\n"
            info = tarfile.TarInfo("./etc/stock-release")
            info.size = len(content)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(content))
        compressed = self.root / "rootfs.tar.gz"
        with raw_tar.open("rb") as source, compressed.open("wb") as raw_output:
            with gzip.GzipFile(
                filename="", fileobj=raw_output, mode="wb", compresslevel=9, mtime=0
            ) as output:
                output.write(source.read())
        padded = self.root / "rootfs.padded"
        padded.write_bytes(compressed.read_bytes())
        with padded.open("r+b") as handle:
            handle.truncate(128 * 1024)
        MODULE.CRYPT.encrypt_native(
            padded,
            self.genuine,
            scratch=True,
            force=True,
            chunk_size=4096,
        )

    def decrypt_members(self, candidate: Path) -> dict[str, tuple[tarfile.TarInfo, bytes]]:
        device_name = self.root / "verify" / MODULE.DEVICE_BASENAME
        device_name.parent.mkdir(exist_ok=True)
        if device_name.exists():
            device_name.unlink()
        os.link(candidate, device_name)
        plain = self.root / "verify" / "plain.tar.gz"
        MODULE.CRYPT.decrypt_native(device_name, plain, force=True, chunk_size=4096)
        result: dict[str, tuple[tarfile.TarInfo, bytes]] = {}
        with tarfile.open(plain, "r:gz") as archive:
            for member in archive.getmembers():
                handle = archive.extractfile(member) if member.isfile() else None
                result[member.name] = (member, handle.read() if handle else b"")
        return result


class BuildTests(CustomFirmwareFixture):
    def test_default_candidate_is_size_identical_and_contains_only_proof_payload(self) -> None:
        output = self.root / "custom.te2"
        report = MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assertEqual(output.stat().st_size, self.genuine.stat().st_size)
        self.assertNotEqual(report["custom"]["sha256"], report["genuine"]["sha256"])
        self.assertTrue(report["custom"]["te2_integrity_valid"])
        self.assertGreater(report["custom"]["zero_padding"], 0)
        members = self.decrypt_members(output)
        self.assertEqual(members["./etc/stock-release"][1], b"stock\n")
        self.assertIn("./etc/ioniq-custom/proof.sh", members)
        self.assertIn("IONIQ5_CUSTOM_FIRMWARE_PROOF", members["./etc/ioniq-custom/proof.sh"][1].decode())
        self.assertNotIn("dropbear", "\n".join(members))
        self.assertNotIn("authorized_keys", "\n".join(members))
        link = members[
            "./etc/systemd/system/multi-user.target.wants/ioniq-custom-proof.service"
        ][0]
        self.assertTrue(link.issym())
        self.assertEqual(link.linkname, "../ioniq-custom-proof.service")
        manifest = json.loads(Path(str(output) + ".manifest.json").read_text())
        self.assertEqual(manifest["custom"]["sha256"], report["custom"]["sha256"])

    def test_custom_overlay_is_root_owned_and_last_member_wins(self) -> None:
        overlay = self.root / "overlay"
        target = overlay / "etc" / "example.conf"
        target.parent.mkdir(parents=True)
        target.write_text("custom=true\n", encoding="utf-8")
        target.chmod(0o640)
        tool = overlay / "opt" / "owner" / "bin" / "tool"
        tool.parent.mkdir(parents=True)
        tool.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        tool.chmod(0o750)
        (tool.parent / "tool-link").symlink_to("tool")
        (overlay / "var" / "lib" / "owner-empty").mkdir(parents=True)
        output = self.root / "custom.te2"
        report = MODULE.ioniq5_custom_firmware_build(
            self.genuine, output, overlay=overlay, include_proof=False
        )
        members = self.decrypt_members(output)
        member, content = members["./etc/example.conf"]
        self.assertEqual(content, b"custom=true\n")
        self.assertEqual(member.mode, 0o640)
        self.assertEqual(
            set(report["overlay"]["members"]),
            {
                "./etc",
                "./etc/example.conf",
                "./opt",
                "./opt/owner",
                "./opt/owner/bin",
                "./opt/owner/bin/tool",
                "./opt/owner/bin/tool-link",
                "./var",
                "./var/lib",
                "./var/lib/owner-empty",
            },
        )
        for name in report["overlay"]["members"]:
            with self.subTest(member=name):
                archived = members[name][0]
                self.assertEqual(archived.uid, 0)
                self.assertEqual(archived.gid, 0)

    def test_existing_outputs_and_wrong_source_basename_are_refused(self) -> None:
        output = self.root / "custom.te2"
        output.write_bytes(b"keep")
        with self.assertRaisesRegex(MODULE.CustomFirmwareError, "already exists"):
            MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assertEqual(output.read_bytes(), b"keep")
        renamed = self.root / "renamed.te2"
        renamed.write_bytes(self.genuine.read_bytes())
        with self.assertRaisesRegex(MODULE.CustomFirmwareError, "device basename"):
            MODULE.ioniq5_custom_firmware_build(renamed, self.root / "other.te2")

    def test_manifest_cannot_alias_firmware_output(self) -> None:
        output = self.root / "custom.te2"
        with self.assertRaisesRegex(MODULE.CustomFirmwareError, "different files"):
            MODULE.ioniq5_custom_firmware_build(
                self.genuine,
                output,
                manifest=output,
            )
        self.assertFalse(output.exists())

    def test_absolute_or_parent_overlay_symlink_is_refused(self) -> None:
        overlay = self.root / "overlay"
        overlay.mkdir()
        (overlay / "bad").symlink_to("../outside")
        with self.assertRaisesRegex(MODULE.CustomFirmwareError, "stay relative"):
            MODULE.ioniq5_custom_firmware_build(
                self.genuine,
                self.root / "custom.te2",
                overlay=overlay,
                include_proof=False,
            )

    def test_no_selected_overlay_is_refused(self) -> None:
        with self.assertRaisesRegex(MODULE.CustomFirmwareError, "no overlay"):
            MODULE.ioniq5_custom_firmware_build(
                self.genuine, self.root / "custom.te2", include_proof=False
            )

    def assert_unpublished(self, output: Path) -> None:
        """A failed build must leave no final artifacts or private staging dirs."""
        self.assertFalse(output.exists())
        self.assertFalse(output.with_name(output.name + ".manifest.json").exists())
        self.assertEqual(list(self.root.glob(".*.build-*")), [])

    def test_original_mutation_after_validation_rejects_private_snapshot_build(self) -> None:
        output = self.root / "custom.te2"
        real_analyze = MODULE.CRYPT.analyze
        calls = []

        def analyze(path):
            calls.append(path)
            result = real_analyze(path)
            if len(calls) == 1:
                with self.genuine.open("r+b") as stream:
                    stream.seek(17)
                    stream.write(b"changed")
            return result

        with mock.patch.object(MODULE.CRYPT, "analyze", side_effect=analyze):
            with self.assertRaisesRegex(MODULE.CustomFirmwareError, "changed during build"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assertNotEqual(calls[0], self.genuine)
        self.assertEqual(calls[0].name, MODULE.DEVICE_BASENAME)
        self.assert_unpublished(output)

    def test_identical_byte_source_replacement_after_validation_is_rejected(self) -> None:
        output = self.root / "custom.te2"
        original_analyze = MODULE.CRYPT.analyze
        replaced = False

        def analyze(path):
            nonlocal replaced
            result = original_analyze(path)
            if not replaced:
                replacement = self.root / "replacement"
                replacement.write_bytes(self.genuine.read_bytes())
                os.replace(replacement, self.genuine)
                replaced = True
            return result

        with mock.patch.object(MODULE.CRYPT, "analyze", side_effect=analyze):
            with self.assertRaisesRegex(MODULE.CustomFirmwareError, "changed during build"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assert_unpublished(output)

    def test_foreign_partial_files_survive_success(self) -> None:
        output = self.root / "custom.te2"
        partials = [self.root / "custom.te2.partial", self.root / "custom.te2.manifest.json.partial"]
        for path in partials:
            path.write_bytes(b"foreign")
        MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        for path in partials:
            self.assertEqual(path.read_bytes(), b"foreign")
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)

    def test_manifest_serialization_failure_leaves_no_output(self) -> None:
        output = self.root / "custom.te2"
        with mock.patch.object(MODULE.json, "dumps", side_effect=OSError("manifest write failure")):
            with self.assertRaisesRegex(OSError, "manifest write failure"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assert_unpublished(output)

    def test_manifest_commit_failure_rolls_back_new_firmware(self) -> None:
        output = self.root / "custom.te2"
        manifest = output.with_name(output.name + ".manifest.json")
        real_link = os.link

        def link(source, target, **kwargs):
            if Path(target) == manifest:
                raise OSError("manifest commit failure")
            return real_link(source, target, **kwargs)

        with mock.patch.object(MODULE.os, "link", side_effect=link):
            with self.assertRaisesRegex(OSError, "manifest commit failure"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assert_unpublished(output)

    def test_force_manifest_commit_failure_restores_original_pair(self) -> None:
        output = self.root / "custom.te2"
        manifest = output.with_name(output.name + ".manifest.json")
        output.write_bytes(b"old firmware")
        manifest.write_bytes(b"old manifest")
        real_replace = os.replace

        def replace(source, target):
            if Path(target) == manifest and Path(source).name == "candidate":
                raise OSError("manifest commit failure")
            return real_replace(source, target)

        with mock.patch.object(MODULE.os, "replace", side_effect=replace):
            with self.assertRaisesRegex(OSError, "manifest commit failure"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output, force=True)
        self.assertEqual(output.read_bytes(), b"old firmware")
        self.assertEqual(manifest.read_bytes(), b"old manifest")
        self.assertEqual(list(self.root.glob(".*.build-*")), [])

    def test_force_staging_failure_preserves_original_pair(self) -> None:
        output = self.root / "custom.te2"
        manifest = output.with_name(output.name + ".manifest.json")
        output.write_bytes(b"old firmware")
        manifest.write_bytes(b"old manifest")
        with mock.patch.object(MODULE.json, "dumps", side_effect=OSError("serialize failed")):
            with self.assertRaises(OSError):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output, force=True)
        self.assertEqual(output.read_bytes(), b"old firmware")
        self.assertEqual(manifest.read_bytes(), b"old manifest")
        self.assertEqual(list(self.root.glob(".*.build-*")), [])

    def test_force_success_replaces_pair_with_matching_manifest(self) -> None:
        output = self.root / "custom.te2"
        manifest = output.with_name(output.name + ".manifest.json")
        output.write_bytes(b"old firmware")
        manifest.write_bytes(b"old manifest")
        result = MODULE.ioniq5_custom_firmware_build(self.genuine, output, force=True)
        self.assertEqual(json.loads(manifest.read_text()), result)
        self.assertEqual(MODULE._sha256(output), result["custom"]["sha256"])
        self.assertEqual(list(self.root.glob(".*.build-*")), [])

    def test_directory_sync_failure_rolls_back_both_new_outputs(self) -> None:
        output = self.root / "custom.te2"
        with mock.patch.object(MODULE, "_ioniq5_sync_directory", side_effect=OSError("sync failed")):
            with self.assertRaisesRegex(OSError, "sync failed"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assert_unpublished(output)

    def test_interruption_after_link_is_rolled_back(self) -> None:
        output = self.root / "custom.te2"
        real_link = os.link

        def link(source, target, **kwargs):
            result = real_link(source, target, **kwargs)
            if Path(target) == output:
                raise KeyboardInterrupt()
            return result

        with mock.patch.object(MODULE.os, "link", side_effect=link):
            with self.assertRaises(KeyboardInterrupt):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assert_unpublished(output)

    def test_concurrent_target_is_never_overwritten(self) -> None:
        output = self.root / "custom.te2"
        real_check = MODULE._ioniq5_check_source
        count = 0

        def check(*args):
            nonlocal count
            real_check(*args)
            count += 1
            if count == 2:
                output.write_bytes(b"another builder")

        with mock.patch.object(MODULE, "_ioniq5_check_source", side_effect=check):
            with self.assertRaisesRegex(MODULE.CustomFirmwareError, "output changed"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assertEqual(output.read_bytes(), b"another builder")
        self.assertFalse(output.with_name(output.name + ".manifest.json").exists())
        self.assertEqual(list(self.root.glob(".*.build-*")), [])

    def test_source_hardlink_and_output_symlink_are_rejected(self) -> None:
        output = self.root / "custom.te2"
        os.link(self.genuine, output)
        with self.assertRaisesRegex(MODULE.CustomFirmwareError, "alias"):
            MODULE.ioniq5_custom_firmware_build(self.genuine, output, force=True)
        output.unlink()
        output.symlink_to(self.genuine)
        with self.assertRaisesRegex(MODULE.CustomFirmwareError, "regular file"):
            MODULE.ioniq5_custom_firmware_build(self.genuine, output, force=True)

    def test_staged_copy_failure_removes_only_owned_files(self) -> None:
        output = self.root / "custom.te2"
        original_copy = MODULE._copy_stream

        def copy(source, destination):
            if isinstance(destination.name, int):
                destination.write(b"partial output")
                raise OSError("stage copy failed")
            return original_copy(source, destination)

        with mock.patch.object(MODULE, "_copy_stream", side_effect=copy):
            with self.assertRaisesRegex(OSError, "stage copy failed"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output)
        self.assert_unpublished(output)

    def test_manifest_fsync_failure_preserves_existing_pair(self) -> None:
        output = self.root / "custom.te2"
        manifest = output.with_name(output.name + ".manifest.json")
        output.write_bytes(b"old firmware")
        manifest.write_bytes(b"old manifest")
        real_fsync = os.fsync
        count = 0

        def fsync(fd):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("manifest fsync failure")
            return real_fsync(fd)

        with mock.patch.object(MODULE.os, "fsync", side_effect=fsync):
            with self.assertRaisesRegex(OSError, "manifest fsync failure"):
                MODULE.ioniq5_custom_firmware_build(self.genuine, output, force=True)
        self.assertEqual(count, 2)
        self.assertEqual(output.read_bytes(), b"old firmware")
        self.assertEqual(manifest.read_bytes(), b"old manifest")
        self.assertEqual(list(self.root.glob(".*.build-*")), [])

    def test_failed_rollback_retains_original_backup_and_reports_path(self) -> None:
        output = self.root / "custom.te2"
        manifest = output.with_name(output.name + ".manifest.json")
        output.write_bytes(b"old firmware")
        manifest.write_bytes(b"old manifest")
        real_replace = os.replace

        def replace(source, target):
            if Path(target) == manifest or Path(source).name == "previous":
                raise OSError("filesystem publication unavailable")
            return real_replace(source, target)

        with mock.patch.object(MODULE.os, "replace", side_effect=replace):
            with self.assertRaisesRegex(MODULE.CustomFirmwareError, "recovery directories:") as failure:
                MODULE.ioniq5_custom_firmware_build(self.genuine, output, force=True)
        backup = next(self.root.glob(".custom.te2.build-*/previous"))
        self.assertEqual(backup.read_bytes(), b"old firmware")
        self.assertIn(str(backup.parent), str(failure.exception))
        self.assertEqual(manifest.read_bytes(), b"old manifest")


if __name__ == "__main__":
    unittest.main()
