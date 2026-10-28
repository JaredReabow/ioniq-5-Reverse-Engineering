#!/usr/bin/env python3
"""Bounded, read-only RSA-public-operation probe of opaque package edges.

Hypothesis only: a payload edge contains a PKCS#1 v1.5 type-1 block under
an *embedded boot-container public key*. Boot signing and payload wrapping
need not use the same key. This is not an RSA private-key recovery attack,
a firmware decryptor, or a proof of absence outside the selected ranges.

Requires the already-installed cryptography package. Reports hashes and
lengths of recovered data, not its bytes. Never modifies an input file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding, rsa

try:
    from . import ipk_tool
except ImportError:
    import ipk_tool


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def edge_ranges(size: int, window: int) -> list[tuple[int, int]]:
    """Return non-overlapping half-open ranges; short files are scanned whole."""
    if size < 0 or window < 256 or window > 1024 * 1024:
        raise ValueError("size must be nonnegative; window must be 256..1048576")
    if size <= 2 * window:
        return [(0, size)] if size else []
    return [(0, window), (size - window, size)]


def recover(key, block: bytes) -> bytes | None:
    """RSA public operation with strict type-1 padding, no digest assumption."""
    if len(block) != (key.key_size + 7) // 8:
        return None
    try:
        return key.recover_data_from_signature(block, padding.PKCS1v15(), None)
    except (InvalidSignature, ValueError):
        return None


def load_boot_key(path: Path):
    info = ipk_tool.parse(path)
    if len(info["_modulus"]) != 256 or info["modulus_bits"] != 2048:
        raise ValueError("expected an RSA-2048 boot-container key")
    key = rsa.RSAPublicNumbers(
        info["exponent"], int.from_bytes(info["_modulus"], "big")
    ).public_key()
    start, end = info["signed_range"]
    expected = ipk_tool.DIGESTINFO_SHA256 + hashlib.sha256(info["_raw"][start:end]).digest()
    if recover(key, info["_signature"]) != expected:
        raise ValueError("boot signature failed strict padding/digest positive control")
    return key, {
        "path": str(path), "sha256": info["sha256"],
        "modulus_sha256": info["modulus_sha256"], "exponent": info["exponent"],
        "positive_control": "strict PKCS1v1.5 SHA256 DigestInfo equals signed-range digest",
    }


def scan_bytes(data: bytes, key, orders=("big", "little")) -> dict:
    if not orders or len(set(orders)) != len(orders) or any(o not in ("big", "little") for o in orders):
        raise ValueError("orders must contain unique big/little values")
    width = (key.key_size + 7) // 8
    positions = max(0, len(data) - width + 1)
    hits = []
    for offset in range(positions):
        block = data[offset:offset + width]
        for order in orders:
            recovered = recover(key, block if order == "big" else block[::-1])
            if recovered is not None:
                is_digest = (len(recovered) == 51 and recovered.startswith(ipk_tool.DIGESTINFO_SHA256))
                hits.append({
                    "offset": offset, "byte_order": order,
                    "block_sha256": sha256(block), "recovered_length": len(recovered),
                    "recovered_sha256": sha256(recovered),
                    "classification": "sha256-DigestInfo-shaped" if is_digest else "unclassified-type1-data",
                })
    return {"positions": positions, "rsa_attempts": positions * len(orders), "hits": hits}


def scan_file(path: Path, key, window: int) -> dict:
    regions = []
    hits = []
    with path.open("rb") as stream:
        stream.seek(0, 2)
        size = stream.tell()
        for start, end in edge_ranges(size, window):
            stream.seek(start)
            data = stream.read(end - start)
            if len(data) != end - start:
                raise ValueError("input shortened during scan")
            result = scan_bytes(data, key)
            regions.append({"start": start, "end": end, "sha256": sha256(data),
                            "positions": result["positions"], "rsa_attempts": result["rsa_attempts"]})
            hits.extend({**hit, "offset": start + hit["offset"]} for hit in result["hits"])
    return {"path": str(path), "size": size, "regions": regions, "hits": hits}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", type=Path, required=True)
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--window", type=int, default=16384)
    parser.add_argument("--output", type=Path, required=True, help="new JSON path; refuses overwrite")
    args = parser.parse_args(argv)
    edge_ranges(0, args.window)
    if args.output.exists():
        parser.error("output already exists")
    key, source = load_boot_key(args.container)
    files = [scan_file(path, key, args.window) for path in args.input]
    report = {
        "schema": 1, "key_source": source, "window_bytes": args.window,
        "byte_orders": ["big", "little"], "stride": 1, "files": files,
        "summary": {
            "files": len(files),
            "bytes_read": sum(r["end"] - r["start"] for f in files for r in f["regions"]),
            "rsa_attempts": sum(r["rsa_attempts"] for f in files for r in f["regions"]),
            "hits": sum(len(f["hits"]) for f in files),
        },
        "limitations": [
            "Only fully contained 256-byte blocks in the recorded edge ranges were tested.",
            "Only the selected boot public key and PKCS1v1.5 type-1 padding were tested.",
            "Payload wrapping may use another key, padding, encoding, or location.",
            "Region hashes identify sampled bytes; they are not whole-input hashes.",
            "A type-1 hit is not by itself an AES key or a successful firmware decryption.",
        ],
    }
    with args.output.open("x") as out:
        json.dump(report, out, indent=2)
        out.write("\n")
    print(json.dumps(report["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
