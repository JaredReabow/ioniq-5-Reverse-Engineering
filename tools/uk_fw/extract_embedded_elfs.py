#!/usr/bin/env python3.13
"""Extract ELF images embedded inside another ELF's data.

`/app/bin/AppUpgrade` is a ~16 KB wrapper plus a 10.7 MB `.rodata` blob that contains the two real
updaters as complete ELF binaries - SCOMO (tagged `###[scomo]`) and FUMO (tagged `###[newota]`). Any
claim about "the updater's code" has to be made against those, not against the wrapper's string table:
the wrapper's own `.text` is 16,243 bytes and every interesting string lives in data.

Usage:
    python3.13 tools/uk_fw/extract_embedded_elfs.py <outer-binary> <out-dir>
"""
from __future__ import annotations
import struct
import sys
from pathlib import Path

ELF_MAGIC = b"\x7fELF"


def sections(d: bytes) -> None:
    e_shoff, = struct.unpack_from("<Q", d, 0x28)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", d, 0x3A)
    strtab = e_shoff + e_shstrndx * e_shentsize
    _, _, _, _, so, _ = struct.unpack_from("<IIQQQQ", d, strtab)
    for i in range(e_shnum):
        b = e_shoff + i * e_shentsize
        name, typ, flags, addr, off, size = struct.unpack_from("<IIQQQQ", d, b)
        nm = d[so + name:d.index(b"\0", so + name)].decode("latin-1")
        print(f"  [{i:2}] {nm:22} off=0x{off:08x} size={size}")


def extract(outer: Path, out: Path) -> int:
    d = outer.read_bytes()
    out.mkdir(parents=True, exist_ok=True)
    found = 0
    start = 0
    while True:
        off = d.find(ELF_MAGIC, start)
        if off < 0:
            break
        start = off + 4
        if off == 0:                 # the outer binary itself, not an embedded image
            continue
        if d[off + 4] != 2 or d[off + 5] != 1:      # 64-bit, little-endian only
            continue
        e_shoff, = struct.unpack_from("<Q", d, off + 0x28)
        e_shentsize, e_shnum = struct.unpack_from("<HH", d, off + 0x3A)
        size = e_shoff + e_shentsize * e_shnum
        if not (0 < size <= len(d) - off):
            continue
        blob = d[off:off + size]
        tag = "scomo" if b"###[scomo]" in blob else ("newota(fumo)" if b"###[newota]" in blob else "unknown")
        target = out / f"embedded-{off:#010x}-{tag}"
        target.write_bytes(blob)
        print(f"extracted {target.name}  {size} bytes")
        found += 1
    return found


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    n = extract(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"embedded ELF images written: {n}")
