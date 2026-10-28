#!/usr/bin/env python3
"""LG Gen5W TE2 OTA envelope parser/decryptor plus the historical unit-derived decryptor harness.

Two modes are provided.

Native TE2 mode (``inspect`` / ``decrypt``)
-------------------------------------------
The opaque Gen5W payloads are AES-128-CBC envelopes with a fixed trailing
metadata trailer. This tool parses and decrypts those envelopes **directly**
(no unit-derived binary required) using only the evidence established for the
validated LG TE2 container:

* trailer size             0x4024 (16,420 bytes)
* magic/version            ``metadata[0:4]``; validated files start ``b'TE2'``
                           and the fourth byte is an **opaque discriminator**
                           (reported, not semantically named)
* metadata integrity       ``SHA256(iv + metadata[36:])`` compared to
                           ``metadata[4:36]``
* AES final-block material ``metadata[36:52]``
* IV                       first 16 bytes of
                           ``SHA256((basename + signed_int32(body_size)).encode('utf-8'))``
* body size                ``file_size - 0x4024``
* cipher                   AES-128-CBC; the established content key is
                           ``60a93d70f73302a63e5ed0d0ea38be22``

For a body whose size is not a multiple of 16 the stored final ciphertext
fragment is completed with ``metadata[36:36+pad_len]`` before AES decryption,
and only the original fragment length is emitted. Metadata is never stripped
from the input and inputs are never modified. Outputs are explicit, parent
directories are created, existing outputs are refused unless ``--force`` is
given, and any partial output created by a failed decrypt is removed. Body data
is streamed in block-aligned chunks and never read wholly into memory.

Historical external mode (``plan`` / ``run`` / ``verify``)
----------------------------------------------------------
Before the TE2 envelope was validated, decryption relied on the unit's own
``DecryptToPIPE`` binary plus ``decryption_key.der``. That path is retained for
compatibility only: it orchestrates an external binary, models nothing about the
TE2 trailer, and does not apply to the native envelope handled above. The
documented invocation, taken from the public ``update_decryptor``
``entrypoint.sh``, is::

    DecryptToPIPE -d <keyfile> <input> 0 > <output>

Override it with ``--template`` if your build differs. Safety: this mode writes
only under ``--out`` and never modifies the package directory.

Subcommands
-----------
    inspect   report the parsed TE2 metadata trailer (read-only)
    decrypt   native AES-128-CBC decryption of a TE2 envelope
    plan      show the exact external commands that would run (no execution)
    run       execute the external decryptor for each payload and verify outputs
    verify    check that a decrypted directory looks like real plaintext

The external command is supplied as a template so this tool makes no assumption
about the vendor binary's interface:

    --template 'DecryptToPipe --key {key} --in {input} --out {output}'

Placeholders: ``{input}``, ``{output}``, ``{key}``, ``{footer}``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

META_SIZE = 0x4024  # 16,420-byte trailing metadata trailer
BLOCK_SIZE = 16  # AES block size in bytes
MAGIC = b"TE2"  # validated metadata prefix; metadata[3] is an opaque discriminator
DEFAULT_KEY_HEX = "60a93d70f73302a63e5ed0d0ea38be22"
DEFAULT_CHUNK_SIZE = 4 * 1024

# Structural trailer regions (offsets are from the start of the trailer).
SIGNATURE_STORE_OFFSET = 52
SIGNATURE_STORE_END = 8228
SIGNATURE_STORE_SIZE = SIGNATURE_STORE_END - SIGNATURE_STORE_OFFSET  # 8,176
KEY_STORE_OFFSET = 8228
KEY_STORE_END = META_SIZE
KEY_STORE_SIZE = KEY_STORE_END - KEY_STORE_OFFSET  # 8,192

DEFAULT_FILES = [
    "AppUpgrade",
    ".lge.upgrade.xml",
    "HU/firmware/update.tar.gz",
    "HU/images/mango-rootfs.tar.gz",
    "HU/images/mango-rwdata.tar.gz",
    "HU/images/new_gui.tar.gz",
    "HU/images/navi_eu/appnavi.tar",
]


class DecryptError(Exception):
    """Raised when a native inspect/decrypt operation cannot proceed."""


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def detect_footer_size(paths: List[Path]) -> int:
    """Largest trailing window shared by at least two payloads, capped at 64 KiB."""

    tails = {}
    for p in paths:
        with open(p, "rb") as fh:
            size = p.stat().st_size
            fh.seek(max(0, size - 65536))
            tails[p] = fh.read(65536)
    best = 0
    items = list(tails)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = tails[items[i]], tails[items[j]]
            n = 0
            limit = min(len(a), len(b))
            while n < limit and a[-1 - n] == b[-1 - n]:
                n += 1
            best = max(best, n)
    return best


def build_plan(root: Path, out: Path, files: List[str], template: str,
               key: Optional[Path]) -> Dict[str, object]:
    present = [root / rel for rel in files if (root / rel).is_file()]
    if not present:
        raise SystemExit(f"no payloads found under {root}")
    footer = detect_footer_size(present)
    footer_note = None
    if footer:
        footer_note = (f"detected {footer}-byte trailing window (heuristic only; "
                       f"the validated TE2 metadata trailer is {META_SIZE} bytes)")
    plan = {
        "root": str(root),
        "out": str(out),
        "footer": footer,
        "footer_note": footer_note,
        "key": str(key) if key else None,
        "steps": [],
    }
    for src in present:
        rel = src.relative_to(root)
        dst = out / rel
        cmd = template.format(input=src, output=dst, key=key or "", footer=footer)
        plan["steps"].append({
            "input": str(src),
            "output": str(dst),
            "size": src.stat().st_size,
            "has_footer": footer > 0,
            "command": cmd,
        })
    return plan


def run_plan(plan: Dict[str, object], timeout: int) -> Dict[str, object]:
    out = Path(plan["out"])
    results = []
    for step in plan["steps"]:  # type: ignore[index]
        dst = Path(step["output"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        # The documented invocation redirects stdout, so run it through bash.
        record = {"input": step["input"], "output": step["output"], "command": step["command"]}
        try:
            proc = subprocess.run(["bash", "-c", step["command"]],
                                  capture_output=True, text=True, timeout=timeout)
            record["returncode"] = proc.returncode
            record["stderr"] = proc.stderr[-2000:]
            if dst.is_file():
                data = dst.read_bytes()
                record["output_size"] = len(data)
                record["output_entropy"] = round(entropy(data[:65536]), 3)
                record["looks_plaintext"] = is_plaintext(data[:65536])
        except FileNotFoundError:
            record["error"] = "decryptor binary not found"
        except subprocess.TimeoutExpired:
            record["error"] = f"timeout after {timeout}s"
        results.append(record)
    return {"steps": results}


def is_plaintext(sample: bytes) -> bool:
    if not sample:
        return False
    printable = sum(1 for b in sample if 9 <= b <= 13 or 32 <= b < 127)
    return printable / len(sample) > 0.85 and entropy(sample) < 6.0


def verify_dir(path: Path) -> Dict[str, object]:
    rows = []
    for p in sorted(path.rglob("*")):
        if not p.is_file():
            continue
        with open(p, "rb") as fh:
            sample = fh.read(65536)
        rows.append({
            "path": str(p.relative_to(path)),
            "size": p.stat().st_size,
            "entropy": round(entropy(sample), 3),
            "plaintext_like": is_plaintext(sample),
        })
    decompressed = sum(1 for r in rows if r["plaintext_like"])
    return {"root": str(path), "files": len(rows), "plaintext_like": decompressed, "rows": rows}


# ---------------------------------------------------------------------------
# Native TE2 parser/decryptor
# ---------------------------------------------------------------------------

def signed_int32(value: int) -> int:
    """Two's-complement int32 view matching the public xcrypt helper."""
    base = 1 << 32
    value %= base
    if value.bit_length() == 32:
        value -= base
    return value


def _ascii_safe(data: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in data)


def derive_iv(path, body_size: int) -> bytes:
    """First 16 bytes of SHA256((basename + signed_int32(body_size)).encode('utf-8'))."""
    basename = os.path.basename(os.fspath(path))
    material = f"{basename}{signed_int32(body_size)}".encode("utf-8")
    return hashlib.sha256(material).digest()[:BLOCK_SIZE]


def parse_key(key_hex: str) -> bytes:
    if not isinstance(key_hex, str) or not key_hex:
        raise DecryptError("key must be a non-empty hex string")
    try:
        key = bytes.fromhex(key_hex)
    except ValueError as exc:
        raise DecryptError(f"key is not valid hexadecimal: {exc}") from exc
    if len(key) != BLOCK_SIZE:
        raise DecryptError(
            f"key must be {BLOCK_SIZE} bytes (AES-128); got {len(key)} bytes")
    return key


def _crypto():
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        return Cipher, algorithms, modes
    except ImportError as exc:
        raise DecryptError(
            "native TE2 decryption requires the 'cryptography' package, which is "
            "not importable in this interpreter; install it first (no network or "
            "install action is performed by this tool).") from exc


def _read_exact(fh, n: int) -> bytes:
    """Read exactly n bytes or raise DecryptError on a premature end of stream."""
    buf = bytearray()
    while len(buf) < n:
        chunk = fh.read(n - len(buf))
        if not chunk:
            raise DecryptError(
                f"incomplete read: expected {n} bytes, got {len(buf)}")
        buf.extend(chunk)
    return bytes(buf)


def _load_metadata(path, body_size: int) -> bytes:
    with open(path, "rb") as fh:
        fh.seek(body_size)
        return _read_exact(fh, META_SIZE)


def _analyze(path):
    """Parse the trailing metadata trailer and return ``(report, metadata)``.

    ``metadata`` is the raw trailer bytes, or ``None`` when the file is too
    small or unreadable. The report always carries every field that could be
    derived so callers can inspect a damaged envelope.
    """
    path = Path(path)
    report: Dict[str, object] = {"source": str(path)}
    try:
        total_size = path.stat().st_size
    except OSError as exc:
        report["error"] = f"cannot stat input: {exc}"
        report["magic_valid"] = False
        report["integrity_valid"] = False
        return report, None

    report["total_size"] = total_size
    report["metadata_size"] = META_SIZE
    body_size = total_size - META_SIZE
    report["body_size"] = body_size
    if body_size <= 0:
        report["error"] = (f"file too small to hold a TE2 envelope "
                           f"({total_size} <= {META_SIZE} metadata bytes)")
        report["magic_valid"] = False
        report["integrity_valid"] = False
        return report, None

    try:
        metadata = _load_metadata(path, body_size)
    except (OSError, DecryptError) as exc:
        report["error"] = f"metadata read failed: {exc}"
        report["magic_valid"] = False
        report["integrity_valid"] = False
        return report, None

    report["magic_hex"] = metadata[:4].hex()
    report["magic_ascii"] = _ascii_safe(metadata[:4])
    report["byte3"] = metadata[3]
    report["byte3_hex"] = f"0x{metadata[3]:02x}"
    report["magic_valid"] = metadata[:3] == MAGIC

    iv = derive_iv(path, body_size)
    report["iv"] = iv.hex()

    stored = metadata[4:36]
    report["stored_metadata_sha256"] = stored.hex()
    computed = hashlib.sha256(iv + metadata[36:]).digest()
    report["calculated_metadata_sha256"] = computed.hex()
    report["integrity_valid"] = stored == computed

    report["padding_hex"] = metadata[36:52].hex()
    report["signature_store_size"] = SIGNATURE_STORE_SIZE
    report["signature_store_sha256"] = hashlib.sha256(
        metadata[SIGNATURE_STORE_OFFSET:SIGNATURE_STORE_END]).hexdigest()
    report["key_store_size"] = KEY_STORE_SIZE
    report["key_store_sha256"] = hashlib.sha256(
        metadata[KEY_STORE_OFFSET:KEY_STORE_END]).hexdigest()

    if not report["magic_valid"]:
        report["error"] = (f"magic/version mismatch: expected prefix {MAGIC!r}, "
                           f"got {metadata[:4]!r}")
    elif not report["integrity_valid"]:
        report["error"] = "metadata integrity check failed"
    return report, metadata


def analyze_envelope(path) -> Dict[str, object]:
    """Return the inspect/report dictionary for a TE2 envelope (read-only)."""
    return _analyze(path)[0]


def _require_valid(report: Dict[str, object]) -> None:
    if report.get("error"):
        raise DecryptError(str(report["error"]))
    if not report.get("magic_valid"):
        raise DecryptError("magic/version mismatch")
    if not report.get("integrity_valid"):
        raise DecryptError("metadata integrity check failed")


def decrypt_native(input_path, output_path,
                   key_hex: str = DEFAULT_KEY_HEX,
                   chunk_size: int = DEFAULT_CHUNK_SIZE,
                   force: bool = False) -> Dict[str, object]:
    """Decrypt a TE2 envelope to an explicit output path, streaming the body.

    Raises ``DecryptError`` on any validation/decrypt failure and removes a
    partially written output file in that case. Never modifies the input.
    """
    input_path = os.path.abspath(os.fspath(input_path))
    output_path = os.path.abspath(os.fspath(output_path))
    if os.path.realpath(input_path) == os.path.realpath(output_path):
        raise DecryptError("input and output resolve to the same path")

    key = parse_key(key_hex)
    if chunk_size <= 0 or chunk_size % BLOCK_SIZE != 0:
        raise DecryptError(
            f"chunk size must be a positive multiple of {BLOCK_SIZE}; got {chunk_size}")

    report, metadata = _analyze(input_path)
    _require_valid(report)
    assert metadata is not None  # guarded by _require_valid

    body_size = int(report["body_size"])
    iv = bytes.fromhex(str(report["iv"]))
    pad_len = (BLOCK_SIZE - body_size % BLOCK_SIZE) % BLOCK_SIZE
    pad = metadata[36:36 + pad_len]

    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    Cipher, algorithms, modes = _crypto()

    try:
        fout = open(output_path, "wb" if force else "xb")
    except FileExistsError as exc:
        raise DecryptError(
            f"output already exists (use --force to overwrite): {output_path}") from exc
    except OSError as exc:
        raise DecryptError(f"cannot create output {output_path}: {exc}") from exc

    written = 0
    try:
        with open(input_path, "rb") as fin:
            decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
            remaining = body_size
            while remaining > 0:
                want = min(chunk_size, remaining)
                data = _read_exact(fin, want)
                remaining -= want
                if remaining == 0 and pad_len:
                    plain = decryptor.update(data + pad)[:len(data)]
                else:
                    plain = decryptor.update(data)
                fout.write(plain)
                written += len(plain)
            tail = decryptor.finalize()
            if tail:
                fout.write(tail)
                written += len(tail)
    except BaseException:
        fout.close()
        try:
            os.unlink(output_path)
        except OSError:
            pass
        raise
    else:
        fout.close()

    return {
        "input": input_path,
        "output": output_path,
        "total_size": report["total_size"],
        "body_size": body_size,
        "bytes_written": written,
        "iv": report["iv"],
        "padding_hex": report["padding_hex"],
        "cipher": "AES-128-CBC",
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("plan", "run"):
        p = sub.add_parser(name)
        p.add_argument("--root", type=Path, required=True)
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--files", nargs="*", default=None)
        p.add_argument("--template",
                       default="DecryptToPIPE -d {key} {input} 0 > {output}",
                       help="external command template (run through bash)")
        p.add_argument("--key", type=Path, help="decryption_key.der")
        p.add_argument("--timeout", type=int, default=900)
        p.add_argument("--json", type=Path)

    p_ver = sub.add_parser("verify")
    p_ver.add_argument("path", type=Path)
    p_ver.add_argument("--json", action="store_true")

    p_ins = sub.add_parser("inspect",
                           help="report the parsed TE2 metadata trailer (read-only)")
    p_ins.add_argument("input", type=Path)
    p_ins.add_argument("--json", type=Path, help="write the JSON report to this path")

    p_dec = sub.add_parser("decrypt", help="native AES-128-CBC TE2 decryption")
    p_dec.add_argument("input", type=Path)
    p_dec.add_argument("output", type=Path)
    p_dec.add_argument("--key", default=DEFAULT_KEY_HEX,
                       help="AES-128 key as hex (default: established TE2 content key)")
    p_dec.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE,
                       help="read buffer in bytes; must be a positive multiple of 16")
    p_dec.add_argument("--force", action="store_true",
                       help="overwrite an existing output file")
    p_dec.add_argument("--json", type=Path, help="write the JSON report to this path")

    args = ap.parse_args(argv)

    if args.cmd == "verify":
        result = verify_dir(args.path)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for row in result["rows"]:
                flag = "plain" if row["plaintext_like"] else "binary/encrypted"
                print(f"  {row['path']:50} {row['size']:>12}  H={row['entropy']:.2f}  {flag}")
            print(f"{result['plaintext_like']}/{result['files']} look like plaintext")
        return 0

    if args.cmd == "inspect":
        report = analyze_envelope(args.input)
        if args.json:
            args.json.write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        return 0 if (report.get("magic_valid") and report.get("integrity_valid")
                     and "error" not in report) else 1

    if args.cmd == "decrypt":
        try:
            result = decrypt_native(args.input, args.output, args.key,
                                    args.chunk_size, args.force)
        except DecryptError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            args.json.write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        return 0

    plan = build_plan(args.root, args.out, args.files or DEFAULT_FILES,
                      args.template, args.key)
    if args.cmd == "plan":
        if args.json:
            args.json.write_text(json.dumps(plan, indent=2))
        print(json.dumps(plan, indent=2))
        return 0

    result = run_plan(plan, args.timeout)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2))
    failed = [r for r in result["steps"] if r.get("returncode") not in (0,)]
    for r in result["steps"]:
        state = r.get("error") or f"rc={r.get('returncode')}"
        extra = f" out={r.get('output_size')} H={r.get('output_entropy')}" if "output_size" in r else ""
        print(f"  {Path(r['input']).name:28} {state}{extra}")
    print(f"{len(result['steps']) - len(failed)}/{len(result['steps'])} succeeded")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
