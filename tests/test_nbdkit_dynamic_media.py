"""Fixture tests for the clipped dynamic-media nbdkit backend."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "nbdkit_dynamic_media.py"
SPEC = importlib.util.spec_from_file_location("nbdkit_dynamic_media", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class DynamicMediaFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.baseline = bytes(range(256)) * 4
        self.baseline_path = self.root / "usb.img"
        self.baseline_path.write_bytes(self.baseline)
        self.replacement = bytes([0xE7]) * 128
        self.replacement_path = self.root / "replacement.bin"
        self.replacement_path.write_bytes(self.replacement)
        MODULE.nbdkit_dynamic_media_reset()
        self.addCleanup(MODULE.nbdkit_dynamic_media_reset)

    def open_backend(
        self,
        *,
        offset: int = 256,
        length: int = 128,
        switch_after_pass: int = 2,
        mode: str = "benign_then_evil",
        extra_regions: list[dict[str, object]] | None = None,
    ) -> object:
        regions: list[dict[str, object]] = [
            {
                "off": offset,
                "len": length,
                "evil": str(self.replacement_path),
                "switch_after_pass": switch_after_pass,
                "mode": mode,
            }
        ]
        if extra_regions:
            regions.extend(extra_regions)
        regions_path = self.root / "regions.json"
        regions_path.write_text(json.dumps(regions), encoding="utf-8")
        MODULE.config("baseline", str(self.baseline_path))
        MODULE.config("regions", str(regions_path))
        MODULE.config("log", str(self.root / "dynamic.log"))
        MODULE.config("reads", str(self.root / "reads.log"))
        MODULE.config_complete()
        return MODULE.open(False)

    def read(self, handle: object, count: int, offset: int) -> bytes:
        result = MODULE.pread(handle, count, offset)
        assert isinstance(result, bytes)
        return result

    def full_region_sweep(self, handle: object, offset: int = 256, length: int = 128) -> bytes:
        return b"".join(
            self.read(handle, min(16, offset + length - current), current)
            for current in range(offset, offset + length, 16)
        )


class BoundaryReadTests(DynamicMediaFixture):
    def test_left_boundary_keeps_baseline_prefix(self) -> None:
        handle = self.open_backend(switch_after_pass=1)
        got = self.read(handle, 32, 240)
        self.assertEqual(got, self.baseline[240:256] + self.replacement[:16])

    def test_right_boundary_keeps_baseline_suffix(self) -> None:
        handle = self.open_backend(switch_after_pass=1)
        self.read(handle, 16, 256)  # Enter the configured replacement phase.
        got = self.read(handle, 32, 368)
        self.assertEqual(got, self.replacement[112:128] + self.baseline[384:400])

    def test_request_spanning_entire_region_is_clipped_on_both_sides(self) -> None:
        handle = self.open_backend(switch_after_pass=1)
        got = self.read(handle, 192, 224)
        self.assertEqual(
            got,
            self.baseline[224:256] + self.replacement + self.baseline[384:416],
        )

    def test_nbdkit_writable_buffer_api(self) -> None:
        handle = self.open_backend(switch_after_pass=1)
        output = bytearray(32)
        self.assertIsNone(MODULE.pread(handle, output, 240))
        self.assertEqual(bytes(output), self.baseline[240:256] + self.replacement[:16])


class SweepTests(DynamicMediaFixture):
    def test_complete_replay_is_genuine_then_modified(self) -> None:
        handle = self.open_backend()
        first = self.full_region_sweep(handle)
        second = self.full_region_sweep(handle)
        third = self.full_region_sweep(handle)
        self.assertEqual(first, self.baseline[256:384])
        self.assertEqual(second, self.replacement)
        self.assertEqual(third, self.replacement)

    def test_tail_first_read_does_not_switch_early(self) -> None:
        handle = self.open_backend()
        self.assertEqual(self.read(handle, 16, 368), self.baseline[368:384])
        first = self.full_region_sweep(handle)
        self.assertEqual(first, self.baseline[256:384])
        second = self.full_region_sweep(handle)
        self.assertEqual(second, self.replacement)

    def test_repeated_near_start_reads_do_not_increment_pass(self) -> None:
        handle = self.open_backend()
        for _ in range(5):
            self.assertEqual(self.read(handle, 16, 256), self.baseline[256:272])
        self.assertEqual(self.read(handle, 16, 368), self.baseline[368:384])
        self.assertEqual(self.read(handle, 16, 256), self.replacement[:16])

    def test_evil_then_benign_mode_reverses_sources(self) -> None:
        handle = self.open_backend(mode="evil_then_benign")
        self.assertEqual(self.full_region_sweep(handle), self.replacement)
        self.assertEqual(self.full_region_sweep(handle), self.baseline[256:384])

    def test_non_region_bytes_never_change(self) -> None:
        handle = self.open_backend(switch_after_pass=1)
        self.assertEqual(self.read(handle, 64, 64), self.baseline[64:128])


class ValidationTests(DynamicMediaFixture):
    def configure_raw(self, regions: object) -> None:
        path = self.root / "regions.json"
        path.write_text(json.dumps(regions), encoding="utf-8")
        MODULE.config("baseline", str(self.baseline_path))
        MODULE.config("regions", str(path))

    def test_rejects_overlap(self) -> None:
        second = self.root / "second.bin"
        second.write_bytes(bytes(64))
        self.configure_raw([
            {"off": 256, "len": 128, "evil": str(self.replacement_path)},
            {"off": 320, "len": 64, "evil": str(second)},
        ])
        with self.assertRaisesRegex(MODULE.DynamicMediaError, "overlap"):
            MODULE.config_complete()

    def test_rejects_replacement_size_mismatch(self) -> None:
        self.configure_raw([
            {"off": 256, "len": 127, "evil": str(self.replacement_path)},
        ])
        with self.assertRaisesRegex(MODULE.DynamicMediaError, "does not equal"):
            MODULE.config_complete()

    def test_rejects_region_outside_baseline(self) -> None:
        self.configure_raw([
            {"off": 960, "len": 128, "evil": str(self.replacement_path)},
        ])
        with self.assertRaisesRegex(MODULE.DynamicMediaError, "exceeds baseline"):
            MODULE.config_complete()

    def test_rejects_unknown_config_and_out_of_bounds_read(self) -> None:
        with self.assertRaisesRegex(MODULE.DynamicMediaError, "unknown config"):
            MODULE.config("unexpected", "value")
        handle = self.open_backend()
        with self.assertRaisesRegex(MODULE.DynamicMediaError, "outside image"):
            self.read(handle, 32, len(self.baseline) - 16)


if __name__ == "__main__":
    unittest.main()
