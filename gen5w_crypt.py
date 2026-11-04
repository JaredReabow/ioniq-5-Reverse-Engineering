#!/usr/bin/env python3
"""LG Gen5W TE2 OTA envelope decryptor + encryptor (native AES-128-CBC).

Companion to the research decrypt tool. Works on a single file on its own.

Envelope layout:  [ body (AES-128-CBC) ][ metadata trailer, 0x4024 bytes ]

Trailer (offsets from the start of the trailer):
    [0:3]      magic  b"TE2"
    [3]        opaque discriminator byte
    [4:36]     integrity hash = SHA256(iv + metadata[36:])
    [36:52]    final-block material; metadata[36:36+pad_len] completes the body
    [52:...]   signature store + key store. Never read or verified as a
               signature; these bytes only feed the [4:36] integrity hash.
               From-scratch encrypt leaves this whole region zeroed.

IV:   first 16 bytes of SHA256((basename + signed_int32(body_size)).encode())
      where basename is the file's own name, so decrypt/encrypt must use the
      same name for a file (output name on encrypt == input name on decrypt).

Encrypt obtains the trailer in one of three ways, in this order of preference:
    --from ENVELOPE     lift the trailer from an existing encrypted envelope
    --trailer FILE      use a raw 0x4024-byte trailer (e.g. from decrypt --save-trailer)
    <input>.te2meta     auto-detected sidecar next to the plaintext
    (otherwise)         from scratch: TE2 + discriminator + ZEROED stores
Scratch output is accepted by this decryptor but is not device-faithful because
the signature/key stores are zeroed. Preserve the real trailer (--from / sidecar)
for the best chance of device acceptance.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

META_SIZE = 0x4024          # 16,420-byte trailing metadata trailer
BLOCK_SIZE = 16
MAGIC = b"TE2"
DEFAULT_KEY_HEX = "60a93d70f73302a63e5ed0d0ea38be22"
DEFAULT_CHUNK_SIZE = 4 * 1024


class CryptError(Exception):
    pass


# --- shared helpers -------------------------------------------------------
def signed_int32(value: int) -> int:
    base = 1 << 32
    value %= base
    if value.bit_length() == 32:
        value -= base
    return value


def derive_iv(path, body_size: int) -> bytes:
    basename = os.path.basename(os.fspath(path))
    material = f"{basename}{signed_int32(body_size)}".encode("utf-8")
    return hashlib.sha256(material).digest()[:BLOCK_SIZE]


def parse_key(key_hex: str) -> bytes:
    if not isinstance(key_hex, str) or not key_hex:
        raise CryptError("key must be a non-empty hex string")
    try:
        key = bytes.fromhex(key_hex)
    except ValueError as exc:
        raise CryptError(f"key is not valid hexadecimal: {exc}") from exc
    if len(key) != BLOCK_SIZE:
        raise CryptError(f"key must be {BLOCK_SIZE} bytes (AES-128); got {len(key)}")
    return key


def _crypto():
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        return Cipher, algorithms, modes
    except ImportError as exc:
        raise CryptError("requires the 'cryptography' package; install it first") from exc


def _read_exact(fh, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = fh.read(n - len(buf))
        if not chunk:
            raise CryptError(f"incomplete read: expected {n}, got {len(buf)}")
        buf.extend(chunk)
    return bytes(buf)


def _validate_chunk(chunk_size: int) -> None:
    if chunk_size <= 0 or chunk_size % BLOCK_SIZE != 0:
        raise CryptError(f"chunk size must be a positive multiple of {BLOCK_SIZE}; got {chunk_size}")


# --- inspect / decrypt ----------------------------------------------------
def analyze(path) -> Tuple[Dict[str, object], Optional[bytes]]:
    path = Path(path)
    report: Dict[str, object] = {"source": str(path)}
    try:
        total = path.stat().st_size
    except OSError as exc:
        report.update(error=f"cannot stat input: {exc}", magic_valid=False, integrity_valid=False)
        return report, None
    body_size = total - META_SIZE
    report.update(total_size=total, metadata_size=META_SIZE, body_size=body_size)
    if body_size <= 0:
        report.update(error=f"file too small to hold a TE2 envelope ({total} <= {META_SIZE})",
                      magic_valid=False, integrity_valid=False)
        return report, None
    with open(path, "rb") as fh:
        fh.seek(body_size)
        meta = _read_exact(fh, META_SIZE)
    iv = derive_iv(path, body_size)
    report["magic_hex"] = meta[:4].hex()
    report["byte3_hex"] = f"0x{meta[3]:02x}"
    report["magic_valid"] = meta[:3] == MAGIC
    report["iv"] = iv.hex()
    stored = meta[4:36]
    computed = hashlib.sha256(iv + meta[36:]).digest()
    report["stored_metadata_sha256"] = stored.hex()
    report["calculated_metadata_sha256"] = computed.hex()
    report["integrity_valid"] = stored == computed
    report["padding_hex"] = meta[36:52].hex()
    if not report["magic_valid"]:
        report["error"] = f"magic/version mismatch: expected {MAGIC!r}, got {meta[:3]!r}"
    elif not report["integrity_valid"]:
        report["error"] = "metadata integrity check failed"
    return report, meta


def decrypt_native(input_path, output_path, key_hex: str = DEFAULT_KEY_HEX,
                   chunk_size: int = DEFAULT_CHUNK_SIZE, force: bool = False,
                   save_trailer: bool = False) -> Dict[str, object]:
    input_path = os.path.abspath(os.fspath(input_path))
    output_path = os.path.abspath(os.fspath(output_path))
    if os.path.realpath(input_path) == os.path.realpath(output_path):
        raise CryptError("input and output resolve to the same path")
    key = parse_key(key_hex)
    _validate_chunk(chunk_size)
    report, meta = analyze(input_path)
    if report.get("error"):
        raise CryptError(str(report["error"]))
    assert meta is not None
    body_size = int(report["body_size"])
    iv = bytes.fromhex(str(report["iv"]))
    pad_len = (BLOCK_SIZE - body_size % BLOCK_SIZE) % BLOCK_SIZE
    pad = meta[36:36 + pad_len]
    Cipher, algorithms, modes = _crypto()
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    try:
        fout = open(output_path, "wb" if force else "xb")
    except FileExistsError as exc:
        raise CryptError(f"output already exists (use --force to overwrite): {output_path}") from exc
    written = 0
    try:
        with open(input_path, "rb") as fin:
            dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
            remaining = body_size
            while remaining > 0:
                want = min(chunk_size, remaining)
                data = _read_exact(fin, want)
                remaining -= want
                if remaining == 0 and pad_len:
                    plain = dec.update(data + pad)[:len(data)]
                else:
                    plain = dec.update(data)
                fout.write(plain)
                written += len(plain)
            tail = dec.finalize()
            if tail:
                fout.write(tail)
                written += len(tail)
    except BaseException:
        fout.close()
        try: os.unlink(output_path)
        except OSError: pass
        raise
    else:
        fout.close()
    result = {"input": input_path, "output": output_path, "body_size": body_size,
              "bytes_written": written, "iv": report["iv"], "cipher": "AES-128-CBC"}
    if save_trailer:
        trailer_path = output_path + ".te2meta"
        with open(trailer_path, "wb" if force else "xb") as tf:
            tf.write(meta)
        result["trailer"] = trailer_path
    return result


# --- encrypt --------------------------------------------------------------
def _load_trailer_from_envelope(envelope_path) -> bytes:
    size = os.path.getsize(envelope_path)
    if size < META_SIZE:
        raise CryptError(f"'{envelope_path}' is smaller than the {META_SIZE}-byte trailer")
    with open(envelope_path, "rb") as fh:
        fh.seek(size - META_SIZE)
        trailer = _read_exact(fh, META_SIZE)
    if trailer[:3] != MAGIC:
        raise CryptError(f"'{envelope_path}' does not end with a TE2 trailer (magic {trailer[:3]!r})")
    return trailer


def _load_raw_trailer(trailer_path) -> bytes:
    data = Path(trailer_path).read_bytes()
    if len(data) != META_SIZE:
        raise CryptError(f"trailer file must be exactly {META_SIZE} bytes; got {len(data)}")
    if data[:3] != MAGIC:
        raise CryptError(f"trailer file is not a TE2 trailer (magic {data[:3]!r})")
    return data


def _scratch_trailer(discriminator: int) -> bytes:
    meta = bytearray(META_SIZE)        # zeroed signature + key stores
    meta[0:3] = MAGIC
    meta[3] = discriminator & 0xFF
    return bytes(meta)


def _resolve_trailer(plaintext_path, from_envelope, trailer_file, scratch,
                     discriminator) -> Tuple[bytes, str]:
    if from_envelope:
        return _load_trailer_from_envelope(from_envelope), "envelope"
    if trailer_file:
        return _load_raw_trailer(trailer_file), "trailer-file"
    sidecar = os.fspath(plaintext_path) + ".te2meta"
    if not scratch and os.path.isfile(sidecar):
        return _load_raw_trailer(sidecar), "sidecar"
    return _scratch_trailer(0 if discriminator is None else discriminator), "scratch"


def encrypt_native(plaintext_path, output_path, key_hex: str = DEFAULT_KEY_HEX,
                   chunk_size: int = DEFAULT_CHUNK_SIZE, force: bool = False,
                   from_envelope=None, trailer_file=None, scratch: bool = False,
                   discriminator: Optional[int] = None) -> Dict[str, object]:
    plaintext_path = os.path.abspath(os.fspath(plaintext_path))
    output_path = os.path.abspath(os.fspath(output_path))
    if os.path.realpath(plaintext_path) == os.path.realpath(output_path):
        raise CryptError("plaintext and output resolve to the same path")
    key = parse_key(key_hex)
    _validate_chunk(chunk_size)
    body_size = os.path.getsize(plaintext_path)
    if body_size == 0:
        raise CryptError("plaintext is empty; nothing to encrypt")
    trailer, trailer_source = _resolve_trailer(plaintext_path, from_envelope,
                                               trailer_file, scratch, discriminator)
    iv = derive_iv(output_path, body_size)          # IV binds to the OUTPUT name
    pad_len = (BLOCK_SIZE - body_size % BLOCK_SIZE) % BLOCK_SIZE
    Cipher, algorithms, modes = _crypto()
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    try:
        fout = open(output_path, "wb" if force else "xb")
    except FileExistsError as exc:
        raise CryptError(f"output already exists (use --force to overwrite): {output_path}") from exc
    written = 0
    try:
        enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
        hold = b""                                   # keep the trailing pad_len cipher bytes back
        with open(plaintext_path, "rb") as fin:
            remaining = body_size
            while remaining > 0:
                want = min(chunk_size, remaining)
                data = _read_exact(fin, want)
                remaining -= want
                c = enc.update(data + b"\x00" * pad_len) if (remaining == 0 and pad_len) else enc.update(data)
                hold += c
                if len(hold) > pad_len:
                    emit = hold[:len(hold) - pad_len]
                    fout.write(emit); written += len(emit)
                    hold = hold[len(hold) - pad_len:]
            tail = enc.finalize()
            if tail:
                hold += tail
                if len(hold) > pad_len:
                    emit = hold[:len(hold) - pad_len]
                    fout.write(emit); written += len(emit)
                    hold = hold[len(hold) - pad_len:]
        if len(hold) != pad_len:
            raise CryptError(f"internal error: held {len(hold)} pad bytes, expected {pad_len}")
        if written != body_size:
            raise CryptError(f"internal error: wrote {written} body bytes, expected {body_size}")
        pad = hold
        meta = bytearray(trailer)
        meta[0:3] = MAGIC
        if discriminator is not None:
            meta[3] = discriminator & 0xFF
        if pad_len:
            meta[36:36 + pad_len] = pad
        digest = hashlib.sha256(iv + bytes(meta[36:])).digest()
        meta[4:36] = digest
        fout.write(bytes(meta))
    except BaseException:
        fout.close()
        try: os.unlink(output_path)
        except OSError: pass
        raise
    else:
        fout.close()
    return {"plaintext": plaintext_path, "output": output_path, "trailer_source": trailer_source,
            "device_faithful": trailer_source != "scratch",
            "body_size": body_size, "pad_len": pad_len, "iv": iv.hex(),
            "padding_hex": pad.hex() if pad_len else "", "metadata_sha256": digest.hex(),
            "total_size": body_size + META_SIZE, "cipher": "AES-128-CBC"}


# --- recursive ------------------------------------------------------------
def walk_tree(src_root, out_root, mode: str, files: Optional[List[str]],
              key_hex: str, chunk_size: int, force: bool, orig_root=None,
              save_trailer: bool = False, scratch: bool = False,
              discriminator: Optional[int] = None) -> Dict[str, object]:
    src_root, out_root = Path(src_root), Path(out_root)
    orig_root = Path(orig_root) if orig_root else None
    rels = [Path(f) for f in files] if files else \
        sorted(p.relative_to(src_root) for p in src_root.rglob("*") if p.is_file())
    steps = []
    for rel in rels:
        src, dst = src_root / rel, out_root / rel
        rec: Dict[str, object] = {"input": str(src), "output": str(dst)}
        try:
            if not src.is_file():
                raise CryptError("input not found")
            if mode == "decrypt":
                info = decrypt_native(src, dst, key_hex, chunk_size, force, save_trailer)
            else:
                from_env = str(orig_root / rel) if orig_root and (orig_root / rel).is_file() else None
                info = encrypt_native(src, dst, key_hex, chunk_size, force,
                                      from_envelope=from_env, scratch=scratch,
                                      discriminator=discriminator)
                rec["trailer_source"] = info["trailer_source"]
            rec["status"] = "ok"
            rec["total_size"] = info.get("total_size") or info.get("body_size")
        except CryptError as exc:
            rec["error"] = str(exc)
        steps.append(rec)
    return {"mode": mode, "src_root": str(src_root), "out": str(out_root), "steps": steps}


# --- CLI ------------------------------------------------------------------
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("inspect", help="report the parsed TE2 trailer (read-only)")
    pi.add_argument("input", type=Path)
    pi.add_argument("--json", type=Path)

    pd = sub.add_parser("decrypt", help="decrypt one TE2 envelope")
    pd.add_argument("input", type=Path)
    pd.add_argument("output", type=Path)
    pd.add_argument("--key", default=DEFAULT_KEY_HEX)
    pd.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    pd.add_argument("--save-trailer", action="store_true",
                    help="also write <output>.te2meta so a faithful re-encrypt is possible")
    pd.add_argument("--force", action="store_true")
    pd.add_argument("--json", type=Path)

    pe = sub.add_parser("encrypt", help="encrypt one plaintext into a TE2 envelope")
    pe.add_argument("input", type=Path)
    pe.add_argument("output", type=Path)
    pe.add_argument("--from", dest="from_envelope", type=Path,
                    help="lift the trailer from this existing envelope")
    pe.add_argument("--trailer", type=Path, help="use this raw 0x4024-byte trailer file")
    pe.add_argument("--scratch", action="store_true",
                    help="force a from-scratch trailer with zeroed stores (not device-faithful)")
    pe.add_argument("--discriminator", type=lambda s: int(s, 0), default=None,
                    help="set metadata[3] (default: keep source byte, or 0x00 for scratch)")
    pe.add_argument("--key", default=DEFAULT_KEY_HEX)
    pe.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    pe.add_argument("--force", action="store_true")
    pe.add_argument("--json", type=Path)

    for name in ("decrypt-tree", "encrypt-tree"):
        pt = sub.add_parser(name, help=f"recursively {name.split('-')[0]} a directory")
        pt.add_argument("--root", type=Path, required=True, help="directory of inputs")
        pt.add_argument("--out", type=Path, required=True)
        pt.add_argument("--files", nargs="*", default=None)
        pt.add_argument("--key", default=DEFAULT_KEY_HEX)
        pt.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
        pt.add_argument("--force", action="store_true")
        pt.add_argument("--json", type=Path)
        if name == "decrypt-tree":
            pt.add_argument("--save-trailer", action="store_true")
        else:
            pt.add_argument("--orig-root", type=Path,
                            help="directory of original envelopes (same relative paths) for faithful trailers")
            pt.add_argument("--scratch", action="store_true")
            pt.add_argument("--discriminator", type=lambda s: int(s, 0), default=None)

    args = ap.parse_args(argv)

    def emit(obj, code):
        if getattr(args, "json", None):
            args.json.write_text(json.dumps(obj, indent=2))
        print(json.dumps(obj, indent=2))
        return code

    try:
        if args.cmd == "inspect":
            report, _ = analyze(args.input)
            ok = report.get("magic_valid") and report.get("integrity_valid") and "error" not in report
            return emit(report, 0 if ok else 1)
        if args.cmd == "decrypt":
            return emit(decrypt_native(args.input, args.output, args.key, args.chunk_size,
                                       args.force, args.save_trailer), 0)
        if args.cmd == "encrypt":
            return emit(encrypt_native(args.input, args.output, args.key, args.chunk_size,
                                       args.force, args.from_envelope, args.trailer,
                                       args.scratch, args.discriminator), 0)
    except CryptError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.cmd in ("decrypt-tree", "encrypt-tree"):
        mode = args.cmd.split("-")[0]
        result = walk_tree(args.root, args.out, mode, args.files, args.key, args.chunk_size,
                           args.force, orig_root=getattr(args, "orig_root", None),
                           save_trailer=getattr(args, "save_trailer", False),
                           scratch=getattr(args, "scratch", False),
                           discriminator=getattr(args, "discriminator", None))
        if args.json:
            args.json.write_text(json.dumps(result, indent=2))
        failed = [r for r in result["steps"] if r.get("status") != "ok"]
        for r in result["steps"]:
            extra = f" [{r['trailer_source']}]" if "trailer_source" in r else ""
            state = r.get("error") or f"ok total={r.get('total_size')}{extra}"
            print(f"  {r['output']:50} {state}")
        print(f"{len(result['steps']) - len(failed)}/{len(result['steps'])} {mode}ed")
        return 0 if not failed else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
