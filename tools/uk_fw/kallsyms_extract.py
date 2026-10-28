#!/usr/bin/env python3
"""Recover the compressed kallsyms table from a stripped vmlinux ELF.

Pure standard library. Read-only: the input file is opened for reading and
never modified, and nothing from the image is executed.

Layout emitted by scripts/kallsyms.c (v4.1.x, 64-bit):
    kallsyms_addresses[]   (u64, one per symbol, ascending)
    kallsyms_num_syms      (u64 in 4.1 output, PTR-sized)
    kallsyms_names[]       (compressed: len byte + token indexes)
    kallsyms_markers[]     (u64, names offset of every 256th symbol)
    kallsyms_token_table   (256 NUL-terminated token strings)
    kallsyms_token_index   (256 little-endian u16 offsets into token_table)

Discovery is structural, then the whole table is re-validated: markers must
match the decoded offsets exactly, and addresses must be monotonic.
"""

import json
import struct
import sys
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from elf_reader import Elf64  # noqa: E402

TOKEN_CHARS = set(
    b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.$"
)


def _find_token_index(data: bytes, lo: int, hi: int) -> List[int]:
    """Locate kallsyms_token_index: 256 strictly ascending LE u16 values."""
    hits: List[int] = []
    for off in range(lo, hi, 2):
        (first,) = struct.unpack_from("<H", data, off)
        if first != 0:
            continue
        values = struct.unpack_from("<256H", data, off)
        prev = -1
        for value in values:
            if value <= prev:
                break
            prev = value
        else:
            hits.append(off)
    return hits


def _locate_token_table(
    data: bytes, token_index_off: int, values: Tuple[int, ...]
) -> Optional[Tuple[int, List[bytes]]]:
    """Find the token_table whose strings those indexes address.

    Return the earliest start that validates: the table is dense, so a start
    shifted forward by a few bytes can also look printable. The real table
    begins immediately after the markers array, and any earlier start would
    run into marker bytes.
    """
    window_lo = max(0, token_index_off - (values[-1] + 1600))
    best: Optional[Tuple[int, List[bytes]]] = None
    for start in range(window_lo, token_index_off - values[-1] + 1):
        strings: List[bytes] = []
        valid = True
        for value in values:
            pos = start + value
            if pos >= token_index_off:
                valid = False
                break
            end = data.find(b"\x00", pos, token_index_off)
            if end < 0:
                valid = False
                break
            token = data[pos:end]
            if any(byte not in TOKEN_CHARS for byte in token):
                valid = False
                break
            strings.append(token)
        if not valid:
            continue
        last_pos = start + values[255]
        last_end = data.find(b"\x00", last_pos, token_index_off)
        if last_end < 0:
            continue
        # Token table is followed by at most one alignment fill before the index.
        if not (last_end + 1 <= token_index_off <= last_end + 16):
            continue
        best = (start, strings)
        break
    return best


def _locate_markers(data: bytes, end: int, floor: int) -> Optional[List[int]]:
    """Walk back from `end` collecting the ascending u64 markers array."""
    collected: List[Tuple[int, int]] = []
    for step in range(0, 4096):
        pos = end - 8 * (step + 1)
        if pos < floor:
            return None
        (value,) = struct.unpack_from("<Q", data, pos)
        if collected and value >= collected[-1][1]:
            break
        collected.append((pos, value))
    # `collected` is newest-first. Require the oldest element to be the 0 seed.
    if collected[-1][1] != 0:
        return None
    return [value for _, value in reversed(collected)]


def _locate_num_syms(
    data: bytes, markers_start: int, symbol_hint: Tuple[int, int], max_segment: int
) -> Optional[Tuple[int, int]]:
    """Find the symbol count field sitting immediately before kallsyms_names."""
    window = range(markers_start - max_segment, markers_start + 1)
    for pos in window:
        (count,) = struct.unpack_from("<I", data, pos)
        if not (symbol_hint[0] < count <= symbol_hint[1]):
            continue
        return pos, count
    return None


class Kallsyms:
    """Decoded kallsyms table plus the discovery metadata that proved it."""

    def __init__(self, elf: Elf64):
        self.elf = elf
        data = elf.data
        ro = elf.section(".rodata")
        if ro is None:
            raise SystemExit("no .rodata section")
        self.ro = ro
        lo, hi = ro.offset, ro.offset + ro.size

        index_hits = _find_token_index(data, lo, min(hi - 512, len(data) - 512))
        if not index_hits:
            raise SystemExit("no kallsyms_token_index candidate")

        self.token_index_off = -1
        self.token_table_start = -1
        self.tokens: List[bytes] = []
        for off in index_hits:
            values = struct.unpack_from("<256H", data, off)
            located = _locate_token_table(data, off, values)
            if located is None:
                continue
            self.token_index_off = off
            self.token_table_start, self.tokens = located
            self.token_values = values
            break
        if self.token_index_off < 0:
            raise SystemExit("no token_table matched a token_index candidate")

        markers = _locate_markers(data, self.token_table_start, lo)
        if markers is None:
            raise SystemExit("no ascending markers array before token_table")
        self.markers = markers
        markers_start = self.token_table_start - 8 * len(markers)
        self.markers_start = markers_start

        gaps = [markers[i + 1] - markers[i] for i in range(len(markers) - 1)]
        max_segment = (max(gaps) if gaps else 0) + 64
        hint = ((len(markers) - 1) * 256, len(markers) * 256)
        located_num = _locate_num_syms(data, markers_start, hint, max_segment)
        if located_num is None:
            raise SystemExit("no kallsyms_num_syms in the computed window")
        self.num_syms_off, self.num_syms = located_num
        self.names_start = self.num_syms_off + 4
        self.names_size = markers_start - self.names_start

        self.address_start = self.num_syms_off - self.num_syms * 8
        if self.address_start < lo:
            raise SystemExit("kallsyms_addresses would start before .rodata")

        self.symbols: List[Tuple[int, str]] = self._decode_all()

    def _decode_all(self) -> List[Tuple[int, str]]:
        data = self.elf.data
        tokens = self.tokens
        pos = self.names_start
        limit = self.markers_start
        symbols: List[Tuple[int, str]] = []
        marker_seen: List[int] = []
        for index in range(self.num_syms):
            if index % 256 == 0:
                marker_seen.append(pos - self.names_start)
            if pos >= limit:
                raise SystemExit(f"names stream overran at symbol {index}")
            length = data[pos]
            pos += 1
            if length & 0x80:
                length = (length & 0x7F) | (data[pos] << 7)
                pos += 1
            chunk = data[pos : pos + length]
            pos += length
            symbols.append((index, self._expand(chunk, tokens)))
        if pos != limit:
            raise SystemExit(
                f"names stream ended at 0x{pos:x}, expected 0x{limit:x}"
            )
        if marker_seen != self.markers:
            raise SystemExit("decoded marker offsets disagree with markers array")
        return symbols

    @staticmethod
    def _expand(chunk: bytes, tokens: List[bytes]) -> str:
        out = bytearray()
        for byte in chunk:
            out += tokens[byte]
        text = out.decode("latin-1")
        if "\x00" in text:
            text = text.split("\x00", 1)[1]
        return text

    def addresses(self) -> List[int]:
        data = self.elf.data
        return list(
            struct.unpack_from(f"<{self.num_syms}Q", data, self.address_start)
        )

    def validate(self) -> Dict[str, object]:
        raw = self.addresses()
        monotonic = all(raw[i] <= raw[i + 1] for i in range(len(raw) - 1))
        text_lo = 0xFFFFFFFF81000000
        text_hi = 0xFFFFFFFF81C5B000
        in_kernel = [a for a in raw if text_lo <= a < text_hi]
        absolute = [a for a in raw if a != 0]
        return {
            "monotonic": monotonic,
            "count": len(raw),
            "nonzero": len(absolute),
            "inside_kernel_window": len(in_kernel),
            "min_addr": min(absolute) if absolute else None,
            "max_addr": max(absolute) if absolute else None,
            "zero_addrs": len(raw) - len(absolute),
        }

    def vaddr_of(self, symbol: str) -> Optional[int]:
        raw = self.addresses()
        for name, addr in zip((s[1] for s in self.symbols), raw):
            if name == symbol:
                return addr
        return None


def load(path: str) -> Kallsyms:
    return Kallsyms(Elf64(path))


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("usage: kallsyms_extract.py <vmlinux.elf> [outdir]", file=sys.stderr)
        return 2
    elf = Elf64(argv[1])
    ks = Kallsyms(elf)
    report = {
        "input": argv[1],
        "token_index_off": hex(ks.token_index_off),
        "token_table_off": hex(ks.token_table_start),
        "markers_off": hex(ks.markers_start),
        "markers_count": len(ks.markers),
        "num_syms_off": hex(ks.num_syms_off),
        "num_syms": ks.num_syms,
        "names_off": hex(ks.names_start),
        "names_size": ks.names_size,
        "addresses_off": hex(ks.address_start),
        "validation": ks.validate(),
    }
    print(json.dumps(report, indent=2))
    if len(argv) > 2:
        outdir = argv[2]
        addrs = ks.addresses()
        with open(f"{outdir}/kallsyms.tsv", "w", encoding="utf-8") as handle:
            for (_, name), addr in zip(ks.symbols, addrs):
                handle.write(f"{addr:016x}\t{name}\n")
        with open(f"{outdir}/kallsyms.json", "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

