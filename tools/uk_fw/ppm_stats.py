#!/usr/bin/env python3
"""Report simple statistics for a PPM frame, correctly for both P3 (ASCII) and P6 (binary).

Why this exists
---------------
Earlier in this project a frame was judged "black" or "has content" from an awk one-liner
that scanned whitespace-separated numbers after the header. That is valid only for **P3**
(ASCII) PPM. `ias-shot` also emits **P6** (binary), where the same awk reads raw bytes as
if they were decimal text and reports meaningless values (an observed "max=999" on an
8-bit image proves the number came from header/pixel bytes, not from pixel values).

So: never judge a frame by a text scan. Use this, which parses the header and reports
statistics over the actual pixel payload, for both formats.

Usage:
    ppm_stats.py <file.ppm> [--threshold N]

Output is one line of key=value pairs, suitable for logging next to a run.
"""

from __future__ import annotations

import sys


def load_ppm(path: str) -> tuple[str, int, int, int, bytes | list[int]]:
    raw = open(path, "rb").read()
    if raw[:2] not in (b"P3", b"P6"):
        raise SystemExit(f"{path}: not a P3/P6 PPM (magic {raw[:2]!r})")
    magic = raw[:2].decode()

    # Header: magic, width height, maxval. Comments (#...) may appear between fields.
    pos = 2
    fields: list[int] = []
    while len(fields) < 3:
        while pos < len(raw) and raw[pos : pos + 1].isspace():
            pos += 1
        if raw[pos : pos + 1] == b"#":
            while pos < len(raw) and raw[pos] != 0x0A:
                pos += 1
            continue
        start = pos
        while pos < len(raw) and not raw[pos : pos + 1].isspace():
            pos += 1
        fields.append(int(raw[start:pos]))
    while pos < len(raw) and raw[pos : pos + 1].isspace():
        pos += 1

    width, height, maxval = fields
    payload = raw[pos:]

    if magic == "P6":
        return magic, width, height, maxval, payload
    return magic, width, height, maxval, [int(v) for v in payload.split()]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[0])
        return 2
    path = sys.argv[1]
    threshold = 32
    if "--threshold" in sys.argv:
        threshold = int(sys.argv[sys.argv.index("--threshold") + 1])

    magic, width, height, maxval, data = load_ppm(path)
    values = list(data) if magic == "P6" else data
    total = len(values)
    if total == 0:
        raise SystemExit(f"{path}: empty payload")

    scale = 255.0 / maxval if maxval else 1.0
    peak = max(values)
    nonzero = sum(1 for v in values if v > 0)
    bright = sum(1 for v in values if v * scale > threshold)

    print(
        f"format={magic} {width}x{height} maxval={maxval} samples={total} "
        f"peak={peak} peak8={round(peak * scale)} "
        f"nonzero={nonzero} ({nonzero * 100 / total:.2f}%) "
        f"bright>{threshold}={bright} ({bright * 100 / total:.2f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
