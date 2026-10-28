#!/usr/bin/env python3
"""FAT/FAT32 image builder, inspector and mutation corpus generator.

Why this exists
---------------
The head unit's update path mounts a USB stick and parses its filesystem
**before any signature or version check**. On this unit the Linux kernel has no
exfat driver and no FUSE, so either a vendor module parses the filesystem or the
stick is vfat. Either way, filesystem metadata is the only attacker-controlled
input that reaches a parser with no cryptographic gate in front of it.

This tool produces *valid* FAT images from scratch (no mount privileges, no
external formatter), inspects them with an independent parser, and emits a corpus
of semantic corruptions targeted at the checks a filesystem driver must perform.

It does not exploit anything. It is a harness for testing a parser you own.

Subcommands
-----------
    build    write a valid FAT16 or FAT32 image containing named files
    inspect  parse an image independently and report anomalies
    mutate   apply one named corruption to an image
    corpus   write a directory of corruptions from a seed image

Usage
-----
    python3 fat_harness.py build --out seed.img --fat 16 --add README.txt:MAIN_LOOP.SH
    python3 fat_harness.py inspect seed.img
    python3 fat_harness.py corpus --seed seed.img --out corpus/
    python3 fat_harness.py mutate --seed seed.img --out one.img --case fat_loop

Corruptions are listed by `mutate --list-cases`. Every one targets a specific
validation a correct parser must perform; none is a payload.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SECTOR = 512
ATTR_DIRECTORY = 0x10
ATTR_ARCHIVE = 0x20
ATTR_LFN = 0x0F
EOC = 0x0FFFFFFF


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def _eight_three(name: str) -> Tuple[bytes, bytes]:
    name = name.upper()
    base, _, ext = name.partition(".")
    base = "".join(c for c in base if c not in ' ."*+,/:;<=>?[\\]|') or "FILE"
    ext = "".join(c for c in ext if c.isalnum())[:3]
    return base[:8].ljust(8).encode(), ext.ljust(3).encode()


def _dir_entry(name: str, attr: int, cluster: int, size: int, fat32: bool) -> bytes:
    base, ext = _eight_three(name)
    entry = bytearray(32)
    entry[0:8] = base
    entry[8:11] = ext
    entry[11] = attr
    struct.pack_into("<H", entry, 20, (cluster >> 16) & 0xFFFF if fat32 else 0)
    struct.pack_into("<H", entry, 26, cluster & 0xFFFF)
    struct.pack_into("<I", entry, 28, size)
    return bytes(entry)


def build_image(out: Path, files: List[Tuple[str, bytes]], fat_bits: int,
                clusters: Optional[int] = None) -> Dict[str, object]:
    spc = 1                      # sectors per cluster
    cluster_bytes = spc * SECTOR
    fats = 2
    reserved = 32 if fat_bits == 32 else 1
    root_entries = 0 if fat_bits == 32 else 512

    # Cluster need: root dir (FAT32) + one per file, then round up.
    data_clusters = 1 + sum(max(1, math.ceil(len(data) / cluster_bytes)) for _, data in files)
    if clusters is None:
        clusters = max(data_clusters + 8, 65525 if fat_bits == 32 else data_clusters + 8)

    entry_size = 4 if fat_bits == 32 else 2
    fat_size = 1
    for _ in range(16):
        total = reserved + fats * fat_size + root_entries * 32 // SECTOR + clusters
        fat_size = math.ceil((clusters + 2) * entry_size / SECTOR)
        if reserved + fats * fat_size + root_entries * 32 // SECTOR + clusters >= total:
            break
    total_sectors = reserved + fats * fat_size + root_entries * 32 // SECTOR + clusters

    image = bytearray(total_sectors * SECTOR)

    # Boot sector
    bs = memoryview(image)[:SECTOR]
    bs[0:3] = b"\xEB\x58\x90"
    bs[3:11] = b"MSWIN4.1"
    struct.pack_into("<H", bs, 11, SECTOR)
    image[13] = spc
    struct.pack_into("<H", image, 14, reserved)
    image[16] = fats
    struct.pack_into("<H", image, 17, root_entries)
    if fat_bits == 32 or total_sectors >= 0x10000:
        struct.pack_into("<H", image, 19, 0)
        struct.pack_into("<I", image, 32, total_sectors)
    else:
        struct.pack_into("<H", image, 19, total_sectors)
        struct.pack_into("<I", image, 32, 0)
    image[21] = 0xF8
    struct.pack_into("<H", image, 22, 0 if fat_bits == 32 else fat_size)
    struct.pack_into("<H", image, 24, 32)
    struct.pack_into("<H", image, 26, 64)
    struct.pack_into("<I", image, 28, 0)
    if fat_bits == 32:
        struct.pack_into("<I", image, 36, fat_size)
        struct.pack_into("<H", image, 40, 0)
        struct.pack_into("<H", image, 42, 0)
        struct.pack_into("<I", image, 44, 2)
        struct.pack_into("<H", image, 48, 1)
        struct.pack_into("<H", image, 50, 6)
        image[64] = 0x80
        image[66] = 0x29
        struct.pack_into("<I", image, 67, 0x12345678)
        image[71:82] = b"GEN5W      "
        image[82:90] = b"FAT32   "
    else:
        image[38] = 0x29
        struct.pack_into("<I", image, 39, 0x12345678)
        image[43:54] = b"GEN5W      "
        image[54:62] = b"FAT16   "
    struct.pack_into("<H", image, 510, 0xAA55)
    if fat_bits == 32:
        fsinfo = SECTOR
        struct.pack_into("<I", image, fsinfo + 0, 0x41615252)
        struct.pack_into("<I", image, fsinfo + 484, 0x61417272)
        struct.pack_into("<I", image, fsinfo + 488, 0xFFFFFFFF)
        struct.pack_into("<I", image, fsinfo + 492, 0xFFFFFFFF)
        struct.pack_into("<I", image, fsinfo + 508, 0xAA550000)
        image[6 * SECTOR:6 * SECTOR + SECTOR] = image[0:SECTOR]

    def fat_offset(n: int) -> int:
        return (reserved + n * fat_size) * SECTOR

    def cluster_offset(c: int) -> int:
        return (reserved + fats * fat_size + root_entries * 32 // SECTOR
                + (c - 2) * spc) * SECTOR

    # FAT32 reserves cluster 2 for the root directory; FAT16 has a fixed root area.
    cluster = 3 if fat_bits == 32 else 2
    allocations: List[Tuple[str, int, int]] = []
    for name, data in files:
        need = max(1, math.ceil(len(data) / cluster_bytes))
        allocations.append((name, cluster, len(data)))
        for i in range(need):
            off = cluster_offset(cluster + i)
            chunk = data[i * cluster_bytes:(i + 1) * cluster_bytes]
            image[off:off + len(chunk)] = chunk
            nxt = cluster + i + 1 if i + 1 < need else EOC
            for f in range(fats):
                struct.pack_into("<I" if fat_bits == 32 else "<H",
                                 image, fat_offset(f) + (cluster + i) * entry_size,
                                 (nxt & (EOC if fat_bits == 32 else 0xFFFF)))
        cluster += need

    if fat_bits == 32:
        # root directory lives in cluster 2
        root = cluster_offset(2)
        off = root
        for name, first, size in allocations:
            image[off:off + 32] = _dir_entry(name, ATTR_ARCHIVE, first, size, True)
            off += 32
        for f in range(fats):
            struct.pack_into("<I", image, fat_offset(f) + 2 * 4, EOC)
    else:
        root = (reserved + fats * fat_size) * SECTOR
        off = root
        for name, first, size in allocations:
            image[off:off + 32] = _dir_entry(name, ATTR_ARCHIVE, first, size, False)
            off += 32

    out.write_bytes(bytes(image))
    return {
        "output": str(out),
        "fat_bits": fat_bits,
        "total_sectors": total_sectors,
        "size": len(image),
        "clusters": clusters,
        "fat_size_sectors": fat_size,
        "reserved_sectors": reserved,
        "files": [{"name": n, "first_cluster": c, "size": s} for n, c, s in allocations],
    }


# ---------------------------------------------------------------------------
# Inspect
# ---------------------------------------------------------------------------

def inspect_image(path: Path) -> Dict[str, object]:
    data = path.read_bytes()
    if len(data) < SECTOR:
        return {"error": "shorter than one sector"}
    bps = struct.unpack_from("<H", data, 11)[0]
    spc = data[13]
    rsvd = struct.unpack_from("<H", data, 14)[0]
    nfats = data[16]
    root_ents = struct.unpack_from("<H", data, 17)[0]
    fatsz16 = struct.unpack_from("<H", data, 22)[0]
    fatsz32 = struct.unpack_from("<I", data, 36)[0]
    fatsz = fatsz32 if fatsz16 == 0 else fatsz16
    fat_bits = 32 if fatsz16 == 0 else 16
    root_clus = struct.unpack_from("<I", data, 44)[0] if fat_bits == 32 else None
    sig = struct.unpack_from("<H", data, 510)[0] if len(data) >= 512 else None
    anomalies: List[str] = []
    if bps != 512:
        anomalies.append(f"bytes-per-sector={bps}")
    if spc == 0 or spc & (spc - 1):
        anomalies.append(f"sectors-per-cluster={spc} (not a power of two)")
    if sig != 0xAA55:
        anomalies.append(f"boot signature=0x{sig:04x}" if sig is not None else "boot sector truncated")
    if fat_bits == 32 and root_clus not in (None, 2) and (root_clus or 0) < 2:
        anomalies.append(f"root cluster={root_clus}")
    tot16 = struct.unpack_from("<H", data, 19)[0]
    tot32 = struct.unpack_from("<I", data, 32)[0]
    declared = (tot32 if tot16 == 0 else tot16) * (bps or 512)
    if declared and declared > len(data):
        anomalies.append(f"declared size {declared} exceeds file size {len(data)}")
    return {
        "path": str(path),
        "size": len(data),
        "bytes_per_sector": bps,
        "sectors_per_cluster": spc,
        "reserved_sectors": rsvd,
        "num_fats": nfats,
        "root_entries": root_ents,
        "fat_bits": fat_bits,
        "fat_size_sectors": fatsz,
        "root_cluster": root_clus,
        "boot_signature": f"0x{sig:04x}" if sig is not None else None,
        "anomalies": anomalies,
    }


# ---------------------------------------------------------------------------
# Corruptions
# ---------------------------------------------------------------------------

def _fat_entry_offset(data: bytes, cluster: int) -> int:
    bps = struct.unpack_from("<H", data, 11)[0]
    rsvd = struct.unpack_from("<H", data, 14)[0]
    fatsz16 = struct.unpack_from("<H", data, 22)[0]
    fatsz = struct.unpack_from("<I", data, 36)[0] if fatsz16 == 0 else fatsz16
    width = 4 if fatsz16 == 0 else 2
    return (rsvd * bps) + cluster * width


CASES = {
    "bps_zero": "bytes-per-sector = 0",
    "bps_odd": "bytes-per-sector = 1000 (not a power of two)",
    "spc_zero": "sectors-per-cluster = 0",
    "spc_huge": "sectors-per-cluster = 255",
    "root_entries_bad": "FAT16 root entry count not a multiple of 16",
    "fatsz_zero": "FAT size = 0",
    "total_sectors_huge": "total sectors larger than the image",
    "boot_sig_bad": "boot signature replaced",
    "fat_loop": "FAT entry points at its own cluster (infinite chain)",
    "fat_out_of_range": "FAT entry points far past the data region",
    "fat_bad_cluster": "FAT entry marked 0x0FFFFFF7 (bad cluster)",
    "fat_reserved_value": "FAT entry uses a reserved high value",
    "dir_cluster_oob": "directory entry first cluster outside the volume",
    "dir_size_huge": "directory entry file size larger than the volume",
    "dir_name_weird": "directory entry name filled with 0xFF",
    "truncated": "image truncated mid-data",
    "cluster_chain_crosslink": "two directory entries share a cluster",
}


def apply_case(seed: bytes, case: str) -> bytes:
    data = bytearray(seed)
    if case == "bps_zero":
        struct.pack_into("<H", data, 11, 0)
    elif case == "bps_odd":
        struct.pack_into("<H", data, 11, 1000)
    elif case == "spc_zero":
        data[13] = 0
    elif case == "spc_huge":
        data[13] = 255
    elif case == "root_entries_bad":
        struct.pack_into("<H", data, 17, 1000)
    elif case == "fatsz_zero":
        struct.pack_into("<H", data, 22, 0)
        struct.pack_into("<I", data, 36, 0)
    elif case == "total_sectors_huge":
        struct.pack_into("<I", data, 32, 0xFFFFFFFF)
    elif case == "boot_sig_bad":
        struct.pack_into("<H", data, 510, 0x0000)
    elif case in ("fat_loop", "fat_out_of_range", "fat_bad_cluster", "fat_reserved_value"):
        off = _fat_entry_offset(data, 3)
        width = 4 if struct.unpack_from("<H", data, 22)[0] == 0 else 2
        value = {"fat_loop": 3, "fat_out_of_range": 0x0FFFFFF0,
                 "fat_bad_cluster": 0x0FFFFFF7, "fat_reserved_value": 0x0FFFFFF8}[case]
        if width == 2:
            value &= 0xFFFF
        struct.pack_into("<I" if width == 4 else "<H", data, off, value)
    elif case == "dir_cluster_oob":
        off = _first_dir_entry(data)
        if off is not None:
            struct.pack_into("<I", data, off + 26, 0x00FFFFFF)
    elif case == "dir_size_huge":
        off = _first_dir_entry(data)
        if off is not None:
            struct.pack_into("<I", data, off + 28, 0xFFFFFFFF)
    elif case == "dir_name_weird":
        off = _first_dir_entry(data)
        if off is not None:
            data[off:off + 11] = b"\xff" * 11
    elif case == "truncated":
        cut = max(SECTOR, len(data) // 2)
        data = data[:cut]
    elif case == "cluster_chain_crosslink":
        off = _first_dir_entry(data)
        if off is not None:
            struct.pack_into("<I", data, off + 26, 2)
    else:
        raise SystemExit(f"unknown case: {case}")
    return bytes(data)


def _first_dir_entry(data: bytes) -> Optional[int]:
    bps = struct.unpack_from("<H", data, 11)[0]
    rsvd = struct.unpack_from("<H", data, 14)[0]
    nfats = data[16]
    root_ents = struct.unpack_from("<H", data, 17)[0]
    fatsz16 = struct.unpack_from("<H", data, 22)[0]
    fatsz = struct.unpack_from("<I", data, 36)[0] if fatsz16 == 0 else fatsz16
    if fatsz16 == 0:
        spc = data[13]
        base = (rsvd + nfats * fatsz) * bps + (2 - 2) * spc * bps
    else:
        base = (rsvd + nfats * fatsz) * bps
    for i in range(16):
        off = base + i * 32
        if off + 32 > len(data):
            return None
        if data[off] == 0:
            return None
        if data[off] not in (0xE5,) and data[off + 11] != ATTR_LFN:
            return off
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build")
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--fat", type=int, choices=(16, 32), default=16)
    b.add_argument("--add", action="append", default=[], metavar="FILE:NAME")
    b.add_argument("--clusters", type=int)

    i = sub.add_parser("inspect")
    i.add_argument("image", type=Path)
    i.add_argument("--json", action="store_true")

    m = sub.add_parser("mutate")
    m.add_argument("--seed", type=Path, required=True)
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--case", required=True)
    m.add_argument("--list-cases", action="store_true")

    c = sub.add_parser("corpus")
    c.add_argument("--seed", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)

    args = ap.parse_args(argv)

    if args.cmd == "build":
        files = []
        for spec in args.add:
            src, _, name = spec.partition(":")
            files.append((name or Path(src).name, Path(src).read_bytes()))
        print(json.dumps(build_image(args.out, files, args.fat, args.clusters), indent=2))
        return 0

    if args.cmd == "inspect":
        result = inspect_image(args.image)
        print(json.dumps(result, indent=2) if args.json else
              "\n".join(f"{k:20} {v}" for k, v in result.items()))
        return 0

    if args.cmd == "mutate":
        if args.list_cases:
            for name, desc in sorted(CASES.items()):
                print(f"  {name:22} {desc}")
            return 0
        args.out.write_bytes(apply_case(args.seed.read_bytes(), args.case))
        print(f"{args.out}  ({args.case})")
        return 0

    if args.cmd == "corpus":
        seed = args.seed.read_bytes()
        args.out.mkdir(parents=True, exist_ok=True)
        index = {}
        for name, desc in sorted(CASES.items()):
            target = args.out / f"{name}.img"
            target.write_bytes(apply_case(seed, name))
            index[name] = {"file": target.name, "description": desc,
                           "size": target.stat().st_size}
        (args.out / "corpus.json").write_text(json.dumps(index, indent=2))
        print(f"{len(index)} cases written to {args.out}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
