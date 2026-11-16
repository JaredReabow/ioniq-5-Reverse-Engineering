#!/usr/bin/env python3
"""Produce a TE2 envelope from plaintext, byte-compatible with the vendor format.

The inverse of ``gen5w_decrypt.decrypt_native``: the body is AES-128-CBC over the
plaintext zero-padded to a block boundary, truncated back to the plaintext length,
with the dropped ciphertext tail stored in the metadata padding field. The IV is
``sha256(basename + signed_int32(body_size))[:16]``, and the trailer's integrity
word is ``sha256(iv + metadata[36:])``. Passing an existing envelope as
``--template`` copies its magic discriminator and its signature/key stores.

This tool does not bypass anything. It produces a well-formed envelope, which is a
prerequisite — not a permission — for a unit to accept an update; the remaining
gates are documented in ``docs/update-deployment-feasibility.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gen5w_decrypt as gd


class EncryptError(Exception):
    """Raised when an envelope cannot be produced."""


def _pad_tail(plaintext_len: int) -> int:
    return (gd.BLOCK_SIZE - plaintext_len % gd.BLOCK_SIZE) % gd.BLOCK_SIZE


def build_metadata(body_size: int, iv: bytes, ciphertext_tail: bytes,
                   discriminator: int = 0, template: bytes | None = None) -> bytes:
    """Assemble the trailer word for word, including its own integrity check."""
    meta = bytearray(gd.META_SIZE)
    meta[0:3] = gd.MAGIC
    meta[3] = discriminator
    pad_len = len(ciphertext_tail)
    meta[gd.BLOCK_SIZE * 2 + 4:gd.BLOCK_SIZE * 2 + 4 + pad_len] = ciphertext_tail
    if template is not None and len(template) == gd.META_SIZE:
        # Keep the filler bytes and both stores so the result matches the vendor
        # envelope byte for byte when the payload matches.
        filler = template[gd.BLOCK_SIZE * 2 + 4:gd.SIGNATURE_STORE_OFFSET]
        meta[gd.BLOCK_SIZE * 2 + 4 + pad_len:gd.SIGNATURE_STORE_OFFSET] = \
            filler[pad_len:]
        meta[gd.SIGNATURE_STORE_OFFSET:gd.KEY_STORE_END] = \
            template[gd.SIGNATURE_STORE_OFFSET:gd.KEY_STORE_END]
    digest = hashlib.sha256(iv + bytes(meta[36:])).digest()
    meta[4:36] = digest
    return bytes(meta)


def encrypt_native(input_path, output_path, key_hex: str = gd.DEFAULT_KEY_HEX,
                   template_path=None, chunk_size: int = gd.DEFAULT_CHUNK_SIZE,
                   force: bool = False) -> dict[str, object]:
    """Encrypt ``input_path`` into a TE2 envelope at ``output_path``."""
    input_path = os.path.abspath(os.fspath(input_path))
    output_path = os.path.abspath(os.fspath(output_path))
    if os.path.realpath(input_path) == os.path.realpath(output_path):
        raise EncryptError("input and output resolve to the same path")

    key = gd.parse_key(key_hex)
    if chunk_size <= 0 or chunk_size % gd.BLOCK_SIZE != 0:
        raise EncryptError(
            f"chunk size must be a positive multiple of {gd.BLOCK_SIZE}")

    plaintext_size = os.path.getsize(input_path)
    pad_len = _pad_tail(plaintext_size)
    if plaintext_size == 0:
        raise EncryptError("refusing to encrypt an empty payload")
    iv = gd.derive_iv(output_path, plaintext_size)

    template = None
    discriminator = 0
    if template_path is not None:
        report, template_meta = gd._analyze(Path(template_path))
        if template_meta is None or not report.get("magic_valid"):
            raise EncryptError(f"template is not a TE2 envelope: {template_path}")
        template = template_meta
        discriminator = template[3]

    Cipher, algorithms, modes = gd._crypto()
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    try:
        fout = open(output_path, "wb" if force else "xb")
    except FileExistsError as exc:
        raise EncryptError(
            f"output already exists (use --force to overwrite): {output_path}") from exc
    except OSError as exc:
        raise EncryptError(f"cannot create output {output_path}: {exc}") from exc

    written = 0
    tail = b""
    try:
        with open(input_path, "rb") as fin:
            encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
            remaining = plaintext_size
            while remaining > 0:
                want = min(chunk_size, remaining)
                data = fin.read(want)
                if len(data) != want:
                    raise EncryptError(
                        f"short read: expected {want} bytes, got {len(data)}")
                remaining -= want
                final = remaining == 0 and pad_len
                cipher = encryptor.update(data + b"\x00" * pad_len if final else data)
                if final and len(cipher) > len(data):
                    tail = cipher[len(data):]
                    cipher = cipher[:len(data)]
                fout.write(cipher)
                written += len(cipher)
            extra = encryptor.finalize()
            if extra:
                raise EncryptError("unexpected trailing cipher block")
        metadata = build_metadata(plaintext_size, iv, tail, discriminator, template)
        fout.write(metadata)
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
        "plaintext_size": plaintext_size,
        "body_size": written,
        "total_size": written + gd.META_SIZE,
        "iv": iv.hex(),
        "ciphertext_tail": tail.hex(),
        "cipher": "AES-128-CBC",
        "template": str(template_path) if template_path else None,
    }


def verify_round_trip(envelope: Path, expected: Path) -> bool:
    """Decrypt the produced envelope in memory and compare with the payload."""
    import tempfile

    report, _ = gd._analyze(envelope)
    if not (report.get("magic_valid") and report.get("integrity_valid")):
        return False
    with tempfile.TemporaryDirectory() as directory:
        out = Path(directory) / "roundtrip.bin"
        gd.decrypt_native(envelope, out)
        return out.read_bytes() == Path(expected).read_bytes()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=None,
                        help="existing envelope whose stores and filler are reused")
    parser.add_argument("--key", default=gd.DEFAULT_KEY_HEX)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verify", action="store_true",
                        help="decrypt the result and compare it with the input")
    args = parser.parse_args(argv)
    try:
        report = encrypt_native(args.input, args.output, args.key, args.template,
                                force=args.force)
        if args.verify:
            report["round_trip"] = verify_round_trip(args.output, args.input)
    except (EncryptError, gd.DecryptError, OSError) as exc:
        print(f"gen5w_encrypt: {exc}", file=sys.stderr)
        return 2
    import json

    print(json.dumps(report, indent=2))
    return 0 if report.get("round_trip", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
