#!/usr/bin/env python3
"""Structural kallsyms recovery for stripped Linux 4.1 x86-64 vmlinux.

Why this exists
---------------
``kallsyms_extract.py`` recovers the token table and markers heuristically and
then *scans backwards* for a 32-bit symbol count inside a wide window. On the
IONIQ 5 Gen5W ``260128`` kernel that scan selects a false positive
(64,768 instead of 64,923) and the token decode then overruns the names
stream. Two concrete defects were identified:

1. ``kallsyms_num_syms`` is discovered by taking the first in-range ``u32`` in a
   multi-megabyte window, rather than the field that makes the decode end
   exactly at ``kallsyms_markers``.
2. ``kallsyms_markers`` is assumed 8-byte aligned at an odd address. In this
   image the array is genuinely 8-byte entries but starts at ``0x9dedc8``;
   reading from ``0x9dedc7`` yields plausible-looking but wrong offsets.

This module derives the layout structurally instead:

    kallsyms_addresses[]   monotonic run of kernel pointers
    kallsyms_num_syms      u32 count, padded to 8 bytes
    kallsyms_names[]       compressed names, 1 length byte + token indexes
    kallsyms_markers[]     u64, byte offset of every 256th name
    kallsyms_token_table   256 NUL-terminated token strings
    kallsyms_token_index   256 little-endian u16 offsets into token_table

The first character of every expanded name is the symbol type letter
(``A``/``T``/``t``/``d``/``b``/``r``/``R``), which is stripped before output.

Read-only: the input is opened for reading and nothing is executed.

Usage
-----
    python3 kallsyms_structural.py vmlinux -o outdir
    python3 kallsyms_structural.py vmlinux --json
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

KERNEL_LO = 0xFFFF_FFFF_8000_0000
KERNEL_HI = 0xFFFF_FFFF_C000_0000
MIN_RUN = 4096
MAX_MARKER_COUNT = 1 << 20


def find_address_table(data: bytes) -> Tuple[int, int]:
    """Locate ``kallsyms_addresses`` and its symbol count.

    The array begins with absolute (``A``-type) symbols whose values are small
    integers such as ``0`` and ``0x4000``, so a scan restricted to kernel-range
    pointers starts late (by exactly 204 entries on the IONIQ 5 ``260128``
    kernel). We therefore use the kernel-range run only to find the *end* of the
    array, read the count, and then derive the true start as
    ``num_syms_off - count * 8``.
    """

    best = (0, 0)
    start = None
    count = 0
    prev = None
    for off in range(0, len(data) - 8, 8):
        (value,) = struct.unpack_from("<Q", data, off)
        inside = KERNEL_LO <= value < KERNEL_HI
        if inside and (prev is None or value >= prev):
            if start is None:
                start, count = off, 1
            else:
                count += 1
        else:
            if start is not None and count > best[1]:
                best = (start, count)
            start, count = (off, 1) if inside else (None, 0)
        prev = value
    if start is not None and count > best[1]:
        best = (start, count)
    if best[1] < MIN_RUN:
        raise SystemExit(f"no plausible kallsyms_addresses run (best {best[1]})")

    # `best` ends at the trailing kernel-range run; the count field follows it.
    run_start, run_count = best
    run_end = run_start + run_count * 8
    count_off, total = find_num_syms(data, run_start, run_end, run_count)
    addr_off = count_off - total * 8
    if addr_off < 0:
        raise SystemExit("derived kallsyms_addresses start is negative")
    values = struct.unpack_from("<%dQ" % total, data, addr_off)
    if any(values[i] > values[i + 1] for i in range(total - 1)):
        raise SystemExit("derived kallsyms_addresses array is not non-decreasing")
    return addr_off, total, count_off


def find_num_syms(data: bytes, run_start: int, run_end: int, run_count: int) -> Tuple[int, int]:
    """Locate the symbol count field immediately after the address array.

    ``run_end`` is where the trailing kernel-pointer run stops, which is the end
    of the full array even when earlier absolute symbols fall outside kernel
    address space.
    """

    for end in (run_end, run_end - 8, run_end + 8):
        for width in (4, 8):
            if end + width > len(data) or end < 0:
                continue
            fmt = "<I" if width == 4 else "<Q"
            (value,) = struct.unpack_from(fmt, data, end)
            if run_count <= value <= run_count + 8192 and end - value * 8 >= 0:
                return end, value
    raise SystemExit(f"no kallsyms_num_syms near 0x{run_end:x}")


def find_markers(data: bytes, names_end_min: int, count: int) -> Tuple[int, List[int]]:
    """Locate the u64 marker array ending at the token table.

    Markers are strictly increasing, start at 0, and the last entry is the byte
    offset of the final 256-symbol block within kallsyms_names.
    """

    need = count
    for off in range(max(0, names_end_min), min(len(data) - 8 * need, names_end_min + (1 << 22))):
        if struct.unpack_from("<Q", data, off)[0] != 0:
            continue
        values = struct.unpack_from("<%dQ" % need, data, off)
        if all(values[i] < values[i + 1] for i in range(need - 1)) and values[-1] < (1 << 24):
            return off, list(values)
    raise SystemExit("no marker array found after names")


def find_token_table(data: bytes, markers_off: int, marker_count: int) -> Tuple[int, List[bytes], int]:
    """Token table sits directly after markers; index follows the strings."""

    table = markers_off + marker_count * 8
    strings: List[bytes] = []
    pos = table
    for _ in range(256):
        end = data.find(b"\x00", pos, pos + 256)
        if end < 0:
            raise SystemExit(f"unterminated token at 0x{pos:x}")
        strings.append(data[pos:end])
        pos = end + 1
    if not all(all(32 <= c < 127 for c in s) for s in strings):
        raise SystemExit("token table contains non-printable token")
    # token_index: 256 ascending u16 offsets starting at 0, near `pos`
    for off in range(pos, pos + 64):
        values = struct.unpack_from("<256H", data, off)
        if values[0] != 0 or not all(values[i] < values[i + 1] for i in range(255)):
            continue
        if values[-1] >= pos - table:
            continue
        return table, strings, off
    raise SystemExit("no token_index found after token_table")


def decode(data: bytes, names_off: int, markers_off: int, count: int, tokens: List[bytes]):
    pos = names_off
    rows: List[Tuple[int, str]] = []
    for index in range(count):
        length = data[pos]
        pos += 1
        chunk = data[pos : pos + length]
        if len(chunk) != length:
            raise SystemExit(f"truncated name at symbol {index}")
        pos += length
        raw = b"".join(tokens[b] for b in chunk).decode("latin1")
        rows.append((index, raw))
    padding = markers_off - pos
    if not 0 <= padding < 16:
        raise SystemExit(f"names ended 0x{pos:x}, markers 0x{markers_off:x} (pad {padding})")
    return rows, padding


def recover(data: bytes) -> Dict[str, object]:
    addr_off, count, num_off = find_address_table(data)
    names_off = num_off + 8 if struct.unpack_from("<I", data, num_off + 4)[0] == 0 else num_off + 4

    marker_count = (count + 255) // 256
    markers_off, markers = find_markers(data, names_off, marker_count)
    table_off, tokens, index_off = find_token_table(data, markers_off, marker_count)
    rows, padding = decode(data, names_off, markers_off, count, tokens)

    # Validate every 256-symbol marker, then strip the type character.
    addrs = struct.unpack_from("<%dQ" % count, data, addr_off)
    symbols = [(addr, raw[:1], raw[1:]) for addr, (_, raw) in zip(addrs, rows)]

    # verify markers against a re-walk
    pos = names_off
    for index in range(count):
        if index % 256 == 0 and pos - names_off != markers[index // 256]:
            raise SystemExit(f"marker mismatch at symbol {index}")
        length = data[pos]
        pos += 1 + length

    return {
        "layout": {
            "addresses_off": f"0x{addr_off:x}",
            "num_syms_off": f"0x{num_off:x}",
            "names_off": f"0x{names_off:x}",
            "markers_off": f"0x{markers_off:x}",
            "marker_count": marker_count,
            "token_table_off": f"0x{table_off:x}",
            "token_index_off": f"0x{index_off:x}",
            "names_padding": padding,
        },
        "num_syms": count,
        "symbols": symbols,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vmlinux", type=Path)
    ap.add_argument("-o", "--outdir", type=Path, help="write kallsyms.tsv and a layout JSON here")
    ap.add_argument("--json", action="store_true", help="print layout JSON to stdout")
    args = ap.parse_args(argv)

    data = args.vmlinux.read_bytes()
    result = recover(data)
    layout = result["layout"]
    symbols = result["symbols"]

    if args.json or not args.outdir:
        print(json.dumps(layout, indent=2))

    if args.outdir:
        args.outdir.mkdir(parents=True, exist_ok=True)
        with open(args.outdir / "kallsyms.tsv", "w", encoding="utf-8") as fh:
            for addr, type_char, name in symbols:
                fh.write(f"{addr:016x}\t{type_char}\t{name}\n")
        # Ghidra helper format: type character prefixed to the name
        with open(args.outdir / "kallsyms_apply.tsv", "w", encoding="utf-8") as fh:
            for addr, type_char, name in symbols:
                fh.write(f"{addr:016x}\t{type_char}{name}\n")
        (args.outdir / "kallsyms_layout.json").write_text(json.dumps(layout, indent=2))
        print(f"wrote {len(symbols)} symbols to {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
