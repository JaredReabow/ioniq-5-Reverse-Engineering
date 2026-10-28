"""Local-only tests for the non-vendor QEMU graphics diagnostic."""
from __future__ import annotations

import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

PROJECT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT / "tools/uk_fw"))
import vm_boot as VM
import vm_display as DISPLAY


def object_fixture(code=b"\x90\xc3", extra_type=None, extra_flags=0):
    names = b"\0.text\0.shstrtab\0.extra\0"
    data = bytearray(bytes(64) + code + names)
    sections = [(0,) * 10,
                (1, 1, 6, 0, 64, len(code), 0, 0, 1, 0),
                (7, 3, 0, 0, 64 + len(code), len(names), 0, 0, 1, 0)]
    if extra_type is not None:
        offset = len(data)
        data += bytes(24)
        sections.append((17, extra_type, extra_flags, 0, offset, 24, 0, 0, 8, 0))
    while len(data) % 8:
        data.append(0)
    shoff = len(data)
    for section in sections:
        data += struct.pack("<IIQQQQIIQQ", *section)
    ident = b"\x7fELF\x02\x01\x01" + bytes(9)
    data[:64] = struct.pack("<16sHHIQQQIHHHHHH", ident, 1, 62, 1, 0, 0, shoff,
                           0, 64, 0, 0, 64, len(sections), 2)
    return bytes(data)


class BinaryTests(unittest.TestCase):
    def test_extracts_only_resolved_text(self):
        self.assertEqual(DISPLAY.text_from_object(object_fixture()), b"\x90\xc3")

    def test_refuses_relocations(self):
        for kind in (4, 9):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "relocations"):
                DISPLAY.text_from_object(object_fixture(extra_type=kind))

    def test_refuses_allocated_data_that_would_need_a_linker(self):
        with self.assertRaisesRegex(ValueError, "requires a linker"):
            DISPLAY.text_from_object(object_fixture(extra_type=1, extra_flags=3))

    def test_refuses_truncated_sections(self):
        with self.assertRaisesRegex(ValueError, "section table"):
            DISPLAY.text_from_object(object_fixture()[:-1])

    def test_refuses_wrong_architecture(self):
        raw = bytearray(object_fixture())
        struct.pack_into("<H", raw, 18, 183)
        with self.assertRaisesRegex(ValueError, "x86-64"):
            DISPLAY.text_from_object(bytes(raw))

    def test_refuses_missing_text(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            DISPLAY.text_from_object(object_fixture(code=b""))

    def test_executable_has_rx_load_and_nonexecuting_stack(self):
        raw = DISPLAY.executable(b"\xc3")
        self.assertEqual(raw[4096:], b"\xc3")
        self.assertEqual(struct.unpack_from("<Q", raw, 24)[0], 0x401000)
        self.assertEqual(struct.unpack_from("<H", raw, 56)[0], 2)
        self.assertEqual(struct.unpack_from("<II", raw, 64), (1, 5))
        self.assertEqual(struct.unpack_from("<II", raw, 120), (0x6474e551, 6))
        self.assertEqual(struct.unpack_from("<Q", raw, 40)[0], 0)

    def test_executable_refuses_empty_or_oversized_code(self):
        for code in (b"", bytes(1024 * 1024 + 1)):
            with self.assertRaises(ValueError):
                DISPLAY.executable(code)


class ImageTests(unittest.TestCase):
    def test_background_and_oracle_dimensions(self):
        bg = DISPLAY.background()
        self.assertEqual(len(bg), 800 * 480 * 4)
        for state, color in DISPLAY.COLORS.items():
            rgb = DISPLAY.expected_rgb(state)
            self.assertEqual(len(rgb), 800 * 480 * 3)
            pos = (320 * 800 + 400) * 3
            self.assertEqual(tuple(rgb[pos:pos + 3]), color)
        # The warning's first glyph pixel is orange, outside the color patch.
        pos = (136 * 800 + 40) * 3
        self.assertEqual(DISPLAY.expected_rgb("blue")[pos:pos + 3], bytes((255, 194, 103)))

    def test_font_rows_are_valid(self):
        for rows in DISPLAY.FONT.values():
            masks = bytes.fromhex(rows)
            self.assertEqual(len(masks), 7)
            self.assertTrue(all(value < 32 for value in masks))

    def test_ppm_does_not_discard_pixel_bytes_that_are_whitespace(self):
        pixels = bytes((10, 13, 32))
        for header in (b"P6\n1 1\n255\n", b"P6\r\n1 1\r\n255\r\n"):
            self.assertEqual(DISPLAY.parse_ppm(header + pixels), (1, 1, pixels))

    def test_invalid_ppm_rejected(self):
        for data in (b"P3\n1 1\n255\nabc", b"P6\n1 1\n65535\nabc",
                     b"P6\n0 1\n255\n", b"P6\n999999 1\n255\nabc",
                     b"P6\n1 1\n255\nab", b"P6\n1 1\n255\nabcd"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                DISPLAY.parse_ppm(data)

    def test_png_crc_and_pixels(self):
        pixels = bytes((255, 0, 0, 0, 255, 0))
        image = DISPLAY.png(2, 1, pixels)
        self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
        offset = 8
        chunks = {}
        while offset < len(image):
            size = struct.unpack_from(">I", image, offset)[0]
            kind = image[offset + 4:offset + 8]
            data = image[offset + 8:offset + 8 + size]
            crc = struct.unpack_from(">I", image, offset + 8 + size)[0]
            self.assertEqual(crc, zlib.crc32(kind + data) & 0xffffffff)
            chunks[kind] = data
            offset += 12 + size
        self.assertEqual(zlib.decompress(chunks[b"IDAT"]), b"\0" + pixels)
        self.assertEqual(struct.unpack_from(">II", chunks[b"IHDR"]), (2, 1))

    def test_png_invalid_dimensions_rejected(self):
        for w, h, data in ((0, 1, b""), (1, 1, b""), (4097, 1, b"")):
            with self.assertRaises(ValueError):
                DISPLAY.png(w, h, data)


class FakeSocket:
    def __init__(self, messages):
        self.reader = io.BytesIO(b"".join((json.dumps(m) + "\n").encode() for m in messages))
        self.sent = []

    def makefile(self, mode):
        return self.reader

    def sendall(self, data):
        self.sent.append(json.loads(data))


class QMPTests(unittest.TestCase):
    def test_handshake_and_events_with_ids(self):
        sock = FakeSocket([{"QMP": {}}, {"return": {}, "id": 1},
                           {"event": "STOP"}, {"return": {"status": "running"}, "id": 2}])
        qmp = DISPLAY.QMP(sock)
        self.assertEqual(qmp.request("query-status"), {"status": "running"})
        self.assertEqual(sock.sent[0]["execute"], "qmp_capabilities")
        qmp.close()
        self.assertTrue(sock.reader.closed)

    def test_errors_are_not_reported_as_success(self):
        sock = FakeSocket([{"QMP": {}}, {"return": {}, "id": 1},
                           {"error": {"desc": "failed"}, "id": 2}])
        qmp = DISPLAY.QMP(sock)
        with self.assertRaisesRegex(ValueError, "failed"):
            qmp.request("screendump")
        qmp.close()

    def test_bad_handshake_closes_stream(self):
        sock = FakeSocket([{"wrong": {}}])
        with self.assertRaisesRegex(ValueError, "greeting"):
            DISPLAY.QMP(sock)
        self.assertTrue(sock.reader.closed)

    def test_keyboard_command_is_virtual_not_serial_text(self):
        sock = FakeSocket([{"QMP": {}}, {"return": {}, "id": 1}, {"return": {}, "id": 2}])
        qmp = DISPLAY.QMP(sock)
        qmp.key("b")
        self.assertEqual(sock.sent[-1]["execute"], "send-key")
        self.assertEqual(sock.sent[-1]["arguments"]["keys"], [{"type": "qcode", "data": "b"}])
        with self.assertRaises(ValueError):
            qmp.key("arbitrary")
        qmp.close()


class FakeDisplay:
    def __init__(self, corrupt=False):
        self.keys = []
        self.transcript = []
        self.corrupt = corrupt

    def request(self, command, arguments):
        assert command == "screendump"
        state = ("idle", "red", "green", "blue")[len(self.keys)]
        pixels = bytearray(DISPLAY.expected_rgb(state))
        if self.corrupt:
            pixels[0] ^= 1  # Center is right; whole-frame validation must fail.
        Path(arguments["filename"]).write_bytes(b"P6\n800 480\n255\n" + pixels)

    def key(self, key):
        self.keys.append(key)


class SmokeTests(unittest.TestCase):
    def setUp(self):
        tmp = PROJECT / "work/test-tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=tmp, prefix="display-test-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def test_complete_keyboard_and_pixel_sequence(self):
        qmp = FakeDisplay()
        smoke = DISPLAY.GraphicsSmoke(qmp, self.path)
        for text in ("VM_DISPLAY_READY 800x480 BGRX32 - DIAGNOSTIC ONLY",
                     "VM_DISPLAY_RED", "VM_DISPLAY_GREEN", "VM_DISPLAY_BLUE"):
            smoke.advance(text + "\n")
        self.assertFalse(smoke.complete)
        smoke.advance("VM_DISPLAY_EXIT\n")
        self.assertTrue(smoke.complete)
        self.assertEqual(qmp.keys, ["r", "g", "b", "q"])
        self.assertEqual(len(smoke.frames), 4)
        self.assertTrue(all(row["full_frame_verified"] for row in smoke.frames))
        self.assertTrue((self.path / "display-blue.png").is_file())

    def test_echoed_marker_does_not_trigger_capture(self):
        qmp = FakeDisplay()
        smoke = DISPLAY.GraphicsSmoke(qmp, self.path)
        smoke.advance("echo 'VM_DISPLAY_READY 800x480 BGRX32 - DIAGNOSTIC ONLY'\n")
        self.assertEqual(smoke.frames, [])
        self.assertEqual(qmp.keys, [])

    def test_wrong_noncenter_pixels_fail(self):
        smoke = DISPLAY.GraphicsSmoke(FakeDisplay(corrupt=True), self.path)
        with self.assertRaisesRegex(ValueError, "full frame"):
            smoke.advance("VM_DISPLAY_READY 800x480 BGRX32 - DIAGNOSTIC ONLY\n")
        self.assertFalse(smoke.complete)


class LauncherTests(unittest.TestCase):
    def test_qemu_display_is_fixed_and_qmp_is_unix_only(self):
        cmd = VM.qemu_command(PROJECT / "work/vm/graphics", "qemu", True, "cocoa", True)
        self.assertIn("VGA,id=display0,addr=01.0", cmd)
        self.assertEqual(cmd[cmd.index("-display") + 1], "cocoa")
        self.assertEqual(cmd[cmd.index("-qmp") + 1], "unix:qmp.sock,server=on,wait=off")
        with self.assertRaises(ValueError):
            VM.qemu_command(PROJECT, "qemu", True, "vnc=0.0.0.0:0")

    def test_child_input_cannot_eat_status_commands(self):
        cmd = "read -r line; printf 'CHILD:%s\\n' \"$line\""
        script = VM.shell_script(cmd, "END") + "PAYLOAD\n"
        result = subprocess.run(["/bin/sh"], input=script, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CHILD:PAYLOAD\n", result.stdout)
        self.assertIn("\nEND:0\n", result.stdout)

    def test_group_preserves_command_failure(self):
        result = subprocess.run(["/bin/sh"], input=VM.shell_script("false", "END"),
                                text=True, capture_output=True)
        self.assertIn("\nEND:1\n", result.stdout)


if __name__ == "__main__":
    unittest.main()
