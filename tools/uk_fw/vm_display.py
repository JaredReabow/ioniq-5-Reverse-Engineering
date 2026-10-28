#!/usr/bin/env python3
"""Build and verify an explicitly non-vendor, QEMU-only graphics diagnostic.

Local LLVM + Python stdlib only. Not an infotainment UI, i915 emulation, DRM
compatibility layer, or a way to recover encrypted application binaries.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import zlib

WIDTH, HEIGHT = 800, 480
COLORS = {"idle": (34, 68, 102), "red": (194, 55, 55),
          "green": (43, 156, 111), "blue": (50, 103, 200)}
SOURCE = Path(__file__).with_name("guest") / "qemu_display.S"
# A tiny 5x7 diagnostic font, not extracted or recreated vendor UI assets.
FONT = {
    " ": "00000000000000", "-": "0000001f000000", ":": "00040400040400",
    "A": "0e11111f111111", "B": "1e11111e11111e", "C": "0e11101010110e",
    "D": "1e11111111111e", "E": "1f10101e10101f", "F": "1f10101e101010",
    "G": "0e11101711110f", "H": "1111111f111111", "I": "0e04040404040e",
    "J": "0702020212120c", "K": "11121418141211", "L": "1010101010101f",
    "M": "111b1515111111", "N": "11191513111111", "O": "0e11111111110e",
    "P": "1e11111e101010", "Q": "0e11111115120d", "R": "1e11111e141211",
    "S": "0f10100e01011e", "T": "1f040404040404", "U": "1111111111110e",
    "V": "11111111110a04", "W": "1111111515150a", "X": "11110a040a1111",
    "Y": "11110a04040404", "Z": "1f01020408101f",
}


def background() -> bytes:
    pixels = bytearray(bytes((30, 22, 17, 0)) * WIDTH * HEIGHT)

    def rect(x, y, w, h, color):
        r, g, b = color
        row = bytes((b, g, r, 0)) * w
        for yy in range(y, y + h):
            pos = (yy * WIDTH + x) * 4
            pixels[pos:pos + w * 4] = row

    def text(x, y, message, scale, color):
        for char in message:
            for row, mask in enumerate(bytes.fromhex(FONT[char])):
                for col in range(5):
                    if mask & (1 << (4 - col)):
                        rect(x + col * scale, y + row * scale, scale, scale, color)
            x += 6 * scale

    rect(0, 0, WIDTH, 8, (81, 179, 194))
    text(40, 36, "VENDOR KERNEL", 4, (235, 241, 245))
    text(40, 80, "GRAPHICS CHECK", 4, (235, 241, 245))
    text(40, 136, "NOT THE INFOTAINMENT UI", 3, (255, 194, 103))
    text(80, 200, "R RED   G GREEN   B BLUE", 2, (196, 208, 218))
    rect(78, 238, 644, 164, (110, 135, 153))
    rect(80, 240, 640, 160, COLORS["idle"])
    text(80, 420, "Q RETURNS TO THE SERIAL SHELL", 2, (196, 208, 218))
    text(80, 450, "QEMU DISPLAY - OWN TEST PROGRAM", 2, (139, 157, 174))
    return bytes(pixels)


def expected_rgb(state: str) -> bytes:
    """Exact intended frame, used only as an oracle for QEMU screenshots."""
    r, g, b = COLORS[state]
    frame = bytearray(background())
    row = bytes((b, g, r, 0)) * 640
    for y in range(240, 400):
        pos = (y * WIDTH + 80) * 4
        frame[pos:pos + len(row)] = row
    rgb = bytearray(WIDTH * HEIGHT * 3)
    rgb[0::3], rgb[1::3], rgb[2::3] = frame[2::4], frame[1::4], frame[0::4]
    return bytes(rgb)


def text_from_object(raw: bytes) -> bytes:
    """Accept only an x86-64 relocatable ELF with resolved, nonempty .text."""
    if len(raw) < 64 or raw[:6] != b"\x7fELF\x02\x01":
        raise ValueError("assembler output is not ELF64 little-endian")
    if struct.unpack_from("<HH", raw, 16) != (1, 62):
        raise ValueError("assembler output is not x86-64 ET_REL")
    shoff = struct.unpack_from("<Q", raw, 40)[0]
    entsize, count, names_index = struct.unpack_from("<HHH", raw, 58)
    if (entsize != 64 or not 0 < count <= 4096 or names_index >= count
            or shoff + count * entsize > len(raw)):
        raise ValueError("invalid object section table")
    sections = [struct.unpack_from("<IIQQQQIIQQ", raw, shoff + i * 64)
                for i in range(count)]
    for section in sections:
        if section[1] != 8 and section[4] + section[5] > len(raw):
            raise ValueError("object section outside file")
        if section[1] in (4, 9) and section[5]:
            raise ValueError("unresolved relocations; refusing to make an executable")
    names_section = sections[names_index]
    names = raw[names_section[4]:names_section[4] + names_section[5]]
    text = []
    for section in sections:
        name = names[section[0]:].split(b"\0", 1)[0]
        if name == b".text":
            if section[1] != 1 or section[2] & 6 != 6:
                raise ValueError("unexpected .text section type/flags")
            text.append(raw[section[4]:section[4] + section[5]])
        elif section[2] & 2 and section[5]:
            raise ValueError("additional allocated section requires a linker")
    if len(text) != 1 or not text[0]:
        raise ValueError("expected one nonempty .text section")
    return text[0]


def executable(code: bytes) -> bytes:
    """Wrap position-independent code in one RX LOAD plus a non-executable stack."""
    if not 0 < len(code) <= 1024 * 1024:
        raise ValueError("invalid diagnostic code length")
    ident = b"\x7fELF\x02\x01\x01" + bytes(9)
    header = struct.pack("<16sHHIQQQIHHHHHH", ident, 2, 62, 1, 0x401000,
                         64, 0, 0, 64, 56, 2, 0, 0, 0)
    load = struct.pack("<IIQQQQQQ", 1, 5, 0, 0x400000, 0x400000,
                       4096 + len(code), 4096 + len(code), 4096)
    stack = struct.pack("<IIQQQQQQ", 0x6474e551, 6, 0, 0, 0, 0, 0, 16)
    return (header + load + stack).ljust(4096, b"\0") + code


def build_probe(out: Path) -> dict:
    mc = shutil.which("llvm-mc")
    if not mc:
        installed = Path("/opt/homebrew/opt/llvm/bin/llvm-mc")
        if installed.is_file():
            mc = str(installed)
    if not mc:
        raise ValueError("llvm-mc is unavailable; no downloads are performed")
    out.mkdir(parents=True, exist_ok=False)
    obj = out / "qemu_display.o"
    cmd = [mc, "-triple=x86_64-pc-linux-gnu", "-filetype=obj", str(SOURCE), "-o", str(obj)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / "assembler.log").write_bytes(result.stdout)
    if result.returncode:
        raise ValueError("display assembly failed; see assembler.log")
    (out / "vm-display").write_bytes(executable(text_from_object(obj.read_bytes())))
    (out / "vm-display").chmod(0o755)
    (out / "vm-display.bgra").write_bytes(background())
    meta = {"scope": "QEMU-only diagnostic; NOT vendor UI", "command": cmd,
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "sha256": {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
                       for name in ("qemu_display.o", "vm-display", "vm-display.bgra")}}
    (out / "build.json").write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def parse_ppm(raw: bytes) -> tuple[int, int, bytes]:
    """Parse QEMU's plain P6 header, refusing oversized or truncated frames."""
    match = re.match(rb"P6[ \r\n\t]+(\d+)[ \r\n\t]+(\d+)[ \r\n\t]+255(?:\r\n|[ \r\n\t])", raw)
    if not match:
        raise ValueError("expected QEMU P6/255 screenshot")
    width, height = map(int, match.groups())
    if not 0 < width <= 4096 or not 0 < height <= 4096:
        raise ValueError("screenshot dimensions out of bounds")
    rgb = raw[match.end():]
    if len(rgb) != width * height * 3:
        raise ValueError("screenshot pixel length mismatch")
    return width, height, rgb


def png(width: int, height: int, rgb: bytes) -> bytes:
    if (not 0 < width <= 4096 or not 0 < height <= 4096
            or len(rgb) != width * height * 3):
        raise ValueError("invalid RGB image")
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))
    rows = b"".join(b"\0" + rgb[y * width * 3:(y + 1) * width * 3] for y in range(height))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


class QMP:
    def __init__(self, sock):
        self.sock = sock
        self.stream = sock.makefile("rb")
        self.transcript = []
        self.sequence = 0
        try:
            greeting = self.receive()
            if "QMP" not in greeting:
                raise ValueError("QMP greeting missing")
            self.request("qmp_capabilities")
        except Exception:
            self.close()
            raise

    def close(self):
        self.stream.close()

    def receive(self):
        raw = self.stream.readline(1024 * 1024)
        if not raw:
            raise EOFError("QEMU QMP connection closed")
        message = json.loads(raw)
        self.transcript.append({"received": message})
        return message

    def request(self, command, arguments=None):
        self.sequence += 1
        message = {"execute": command, "id": self.sequence}
        if arguments is not None:
            message["arguments"] = arguments
        self.transcript.append({"sent": message})
        self.sock.sendall((json.dumps(message) + "\n").encode())
        for _ in range(1000):
            reply = self.receive()
            if reply.get("id") != self.sequence:
                continue
            if "error" in reply:
                raise ValueError(f"QMP {command} failed: {reply['error']}")
            if "return" not in reply:
                raise ValueError("malformed QMP reply")
            return reply["return"]
        raise ValueError("no matching QMP response")

    def key(self, key):
        if key not in ("r", "g", "b", "q"):
            raise ValueError("unsupported diagnostic key")
        return self.request("send-key", {"keys": [{"type": "qcode", "data": key}], "hold-time": 50})


class GraphicsSmoke:
    """Observe guest output, inject actual virtual keyboard events, verify pixels."""
    def __init__(self, qmp: QMP, directory: Path):
        self.qmp = qmp
        self.directory = directory
        self.frames = []
        self.complete = False

    def advance(self, text: str):
        states = ("idle", "red", "green", "blue")
        markers = ("VM_DISPLAY_READY 800x480 BGRX32 - DIAGNOSTIC ONLY",
                   "VM_DISPLAY_RED", "VM_DISPLAY_GREEN", "VM_DISPLAY_BLUE")
        step = len(self.frames)
        if step == len(states):
            self.complete = bool(re.search(r"^VM_DISPLAY_EXIT$", text, re.M))
            return
        if not re.search(r"^" + re.escape(markers[step]) + r"$", text, re.M):
            return
        state = states[step]
        ppm = self.directory / f"display-{state}.ppm"
        self.qmp.request("screendump", {"filename": str(ppm), "format": "ppm"})
        width, height, rgb = parse_ppm(ppm.read_bytes())
        if (width, height) != (WIDTH, HEIGHT):
            raise ValueError(f"guest display is {width}x{height}, expected 800x480")
        pos = (320 * width + 400) * 3
        color = tuple(rgb[pos:pos + 3])
        if color != COLORS[state]:
            raise ValueError(f"display {state}: expected {COLORS[state]}, observed {color}")
        if rgb != expected_rgb(state):
            raise ValueError(f"display {state}: full frame differs from diagnostic oracle")
        target = ppm.with_suffix(".png")
        target.write_bytes(png(width, height, rgb))
        self.frames.append({"state": state, "width": width, "height": height,
                            "center_rgb": color, "full_frame_verified": True, "png": target.name,
                            "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        self.qmp.key(("r", "g", "b", "q")[step])

    def report(self):
        return {"passed": self.complete, "scope": "diagnostic pixels and virtual keyboard only",
                "frames": self.frames, "qmp": self.qmp.transcript}
