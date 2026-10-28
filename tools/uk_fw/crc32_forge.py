#!/usr/bin/env python3
"""Demonstrate that CRC-32 is not an integrity control: patch 4 bytes to hit a target CRC.

Why this exists
---------------
The Gen5W `.ver` manifest records each payload's size and a signed CRC-32. If the
package signature covers only the manifest, then per-file integrity reduces to
CRC-32. CRC-32 is an affine function of the message bits, so for any desired
output there is a 4-byte patch that produces it. This tool computes that patch.

It is a measurement instrument for the hypothesis recorded in
`evidence/eu-ota-container-structure.md`, not an attack: it proves only that a
CRC-32 value can be preserved across a modification. It does **not** produce a
payload the unit will accept — the payload must still decrypt, and the package
footer must still verify.

Usage
-----
    # what is the CRC of this file?
    python3 crc32_forge.py info <file>

    # make a copy whose CRC equals the original's
    python3 crc32_forge.py forge <file> -o out.bin --patch-offset 4096

    # or target an explicit CRC value
    python3 crc32_forge.py forge <file> -o out.bin --target deadbeef --patch-offset 8192

The patch region must be 4 bytes and must not overlap the bytes you care about.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zlib
from pathlib import Path
from typing import List, Optional, Tuple

MAX_BYTES = 512 * 1024 * 1024


def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def baseline_and_columns(data: bytearray, offset: int) -> Tuple[int, List[int]]:
    """Treat the 4-byte region as free. f(r) is affine: f(r) = f(0) ^ L(r).

    Returns f(0) and the 32 columns of L, so the solver can compute the region
    value r that produces any desired CRC.
    """

    saved = bytes(data[offset:offset + 4])
    data[offset:offset + 4] = b"\x00\x00\x00\x00"
    zero_crc = crc32(bytes(data))
    columns = []
    for bit in range(32):
        probe = bytearray(4)
        probe[bit // 8] = 1 << (bit % 8)
        data[offset:offset + 4] = probe
        columns.append(crc32(bytes(data)) ^ zero_crc)
    data[offset:offset + 4] = saved
    return zero_crc, columns


def solve_gf2(columns: List[int], target: int) -> Optional[int]:
    """Return the 32-bit x with XOR of selected columns == target, or None."""

    # Build rows: for each output bit, the coefficients and the target bit.
    rows = []
    for out_bit in range(32):
        coeff = 0
        for col_bit in range(32):
            if (columns[col_bit] >> out_bit) & 1:
                coeff |= 1 << col_bit
        rows.append([coeff, (target >> out_bit) & 1])

    # Gaussian elimination over GF(2), tracking the solution vector.
    pivot_for = {}
    row = 0
    for col in range(32):
        pivot = None
        for r in range(row, 32):
            if (rows[r][0] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        for r in range(32):
            if r != row and (rows[r][0] >> col) & 1:
                rows[r][0] ^= rows[row][0]
                rows[r][1] ^= rows[row][1]
        pivot_for[col] = row
        row += 1

    for coeff, value in rows:
        if coeff == 0 and value == 1:
            return None

    x = 0
    for col, r in pivot_for.items():
        if rows[r][1]:
            x |= 1 << col
    return x


def forge(path: Path, out: Path, target: int, offset: int) -> Tuple[int, bytes]:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"file is {size} bytes; limit is {MAX_BYTES}")
    data = bytearray(path.read_bytes())
    if offset < 0 or offset + 4 > len(data):
        raise SystemExit(f"patch offset {offset} is outside the file")

    zero_crc, columns = baseline_and_columns(data, offset)
    mask = solve_gf2(columns, zero_crc ^ target)
    if mask is None:
        raise SystemExit("no solution found (this should not happen for CRC-32)")
    data[offset:offset + 4] = mask.to_bytes(4, "little")
    result = crc32(bytes(data))
    out.write_bytes(bytes(data))
    return result, mask.to_bytes(4, "little")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_info = sub.add_parser("info")
    p_info.add_argument("file", type=Path)

    p_forge = sub.add_parser("forge")
    p_forge.add_argument("file", type=Path)
    p_forge.add_argument("-o", "--out", type=Path, required=True)
    p_forge.add_argument("--target", help="target CRC-32 as hex; default: file's own CRC")
    p_forge.add_argument("--patch-offset", type=int, default=0,
                         help="where to place the 4-byte correction (default 0)")
    args = ap.parse_args(argv)

    if args.cmd == "info":
        data = args.file.read_bytes()
        print(f"{args.file}: size={len(data)} crc32=0x{crc32(data):08x} "
              f"signed={crc32(data) - (1 << 32) if crc32(data) & 0x80000000 else crc32(data)}")
        return 0

    if args.target:
        target = int(args.target, 16)
    else:
        target = crc32(args.file.read_bytes())
    result, correction = forge(args.file, args.out, target, args.patch_offset)
    ok = result == target
    print(f"wrote {args.out}")
    print(f"target 0x{target:08x}  result 0x{result:08x}  {'MATCH' if ok else 'MISMATCH'}")
    print(f"correction bytes at offset {args.patch_offset}: {correction.hex()}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
