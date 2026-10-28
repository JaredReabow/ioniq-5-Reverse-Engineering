"""Tests for the rootfs repacker."""

from __future__ import annotations

import gzip
import importlib.util
import io
import tarfile
import tempfile
import unittest
import zlib
from pathlib import Path

TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "rootfs_patch.py"
SPEC = importlib.util.spec_from_file_location("rootfs_patch", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def make_package(path: Path, files: dict) -> None:
    with tarfile.open(path, "w:gz") as tf:
        for name, data in files.items():
            info = tarfile.TarInfo("./" + name)
            info.size = len(data)
            info.mode = 0o644
            info.uid = info.gid = 0
            tf.addfile(info, io.BytesIO(data))


def members(path: Path):
    with tarfile.open(path, "r:gz") as tf:
        return sorted(m.name for m in tf.getmembers())


class RootfsPatchTests(unittest.TestCase):
    def test_list_counts_members(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            pkg = Path(temp) / "rootfs.tar.gz"
            make_package(pkg, {"etc/hostname": b"hu", "app/a.txt": b"x"})
            result = MODULE.list_package(pkg, 10)
        self.assertEqual(result["members"], 2)

    def test_inject_adds_file_and_preserves_original(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pkg = root / "rootfs.tar.gz"
            make_package(pkg, {"etc/hostname": b"hu"})
            src = root / "payload.bin"
            src.write_bytes(b"\x00\x01\x02")
            out = root / "out" / "rootfs.tar.gz"
            result = MODULE.inject(pkg, out, [f"{src}:opt/payload.bin"], None, None, None, None)
            names = members(out)
            size = out.stat().st_size
        self.assertIn("./opt/payload.bin", names)
        self.assertIn("./etc/hostname", names)
        self.assertEqual(result["size"], size)

    def test_ssh_key_is_appended_with_mode_600(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pkg = root / "rootfs.tar.gz"
            make_package(pkg, {MODULE.DROPBEAR_KEYS: b"ssh-ed25519 OLD\n"})
            key = root / "id.pub"
            key.write_bytes(b"ssh-ed25519 NEW bench\n")
            out = root / "o.tar.gz"
            MODULE.inject(pkg, out, [], None, None, key, None)
            with tarfile.open(out, "r:gz") as tf:
                data = tf.extractfile("./" + MODULE.DROPBEAR_KEYS).read()
                mode = tf.getmember("./" + MODULE.DROPBEAR_KEYS).mode
        self.assertIn(b"OLD", data)
        self.assertIn(b"NEW bench", data)
        self.assertEqual(mode, 0o600)

    def test_meta_updates_manifest_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rebuilt = root / "mango-rootfs.tar.gz"
            rebuilt.write_bytes(b"payload-bytes")
            manifest = root / "x.ver"
            manifest.write_text(
                "+|1|V|HM|IONIQ5_EU|101489|1\n"
                "IONIQ5_EU\\HU\\images|mango-rootfs.tar.gz|341174|0|13|1\n"
                "IONIQ5_EU\\AppUpgrade|AppUpgrade|341142|0|5|1\n"
            )
            written = root / "out.ver"
            result = MODULE.update_manifest(manifest, rebuilt, written, "mango-rootfs.tar.gz")
            text = written.read_text()
        crc = zlib.crc32(b"payload-bytes") & 0xFFFFFFFF
        signed = crc - (1 << 32) if crc & 0x80000000 else crc
        self.assertEqual(result["records_updated"], 1)
        self.assertIn(f"|{signed}|13|1", text)
        self.assertIn("|0|5|1", text)  # unrelated record untouched


if __name__ == "__main__":
    unittest.main()
