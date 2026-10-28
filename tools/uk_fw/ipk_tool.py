#!/usr/bin/env python3
"""Parse, verify and re-sign Hyundai Gen5W ``ipk.`` boot containers.

Format (derived from the EU ``260128`` package, all six ``iasImage*_sub`` files)
---------------------------------------------------------------------------
    offset 0            "ipk." magic
    offset 0x04         u32  format version          (0x00030300)
    offset 0x08         u32  reserved                 (0)
    offset 0x0c         u32  payload+header size      (0x005ebfcc)
    offset 0x10         u32  header size              (0x34)
    offset 0x14         u32  duplicate of 0x0c
    offset 0x18         u32  format/build id          (0x42f08d94, constant)
    offset 0x1c         u32  command-line length      (953)
    offset 0x20         u32  command-line offset area (0x005148e0)
    offset 0x24         u32  reserved                 (0)
    offset 0x28         u32  (0x0e36)
    offset 0x2c         u32  (0x04f8)
    offset 0x30         u32  (0x000d6000)
    offset 0x34         char command line (NUL-terminated inside clen)
    ...                 payload (legacy LZ4 kernel stream at 0x445e)
    hdr+tot             u32  variant tag              (included in signature)
    hdr+tot+4           252 bytes 0xFF padding
    hdr+tot+0x100       256 bytes RSA-2048 signature over bytes [0, hdr+tot+4)
    hdr+tot+0x200       256 bytes RSA-2048 modulus
    hdr+tot+0x300       u32  public exponent (65537)

Signature scheme: RSA-2048, PKCS#1 v1.5, SHA-256. The signed byte range starts
at offset 0 and ends after the 4-byte variant tag. The public key travels inside
the container; it is **not** present in the shipped kernel image, so any pinning
lives in the boot loader or the encrypted main image.

Subcommands
-----------
    info     parse and print every header field, the command line and trailer
    verify   check the embedded signature (read-only)
    extract  write the payload and/or the decompressed kernel
    resign   write a modified container, re-signed with a supplied key

``resign`` exists so a *bench* unit can be tested with a self-signed image. It
does not defeat OEM signature verification; it produces a correctly formed
container under a different key, which is what an acceptance experiment needs.

Read-only by default: ``info``, ``verify`` and ``extract`` never modify the input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional

MAGIC = b"ipk."
HDR_MIN = 0x34
SIG_LEN = 256
KEY_LEN = 256
PAD_LEN = 252

DIGESTINFO_SHA256 = bytes.fromhex("3031300d060960864801650304020105000420")


class ContainerError(Exception):
    pass


def parse(path: Path) -> Dict[str, object]:
    raw = path.read_bytes()
    if raw[:4] != MAGIC:
        raise ContainerError(f"{path} does not start with {MAGIC!r}")
    (version, reserved0, total, hdrsz, total2, build_id,
     clen, cl_off_a, reserved1, f28, f2c, f30) = struct.unpack_from("<12I", raw, 4)
    if not (HDR_MIN <= hdrsz < 0x1000):
        raise ContainerError(f"implausible header size {hdrsz:#x}")
    cmdline = raw[hdrsz:hdrsz + clen].split(b"\x00")[0].decode("latin1")
    trailer_off = hdrsz + total
    if trailer_off + 0x304 > len(raw):
        raise ContainerError("container shorter than its declared trailer")
    trailer = raw[trailer_off:]
    tag = trailer[0:4]
    signature = trailer[0x100:0x200]
    modulus = trailer[0x200:0x300]
    exponent = struct.unpack_from("<I", trailer, 0x300)[0]
    return {
        "path": str(path),
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "header": {
            "version": f"0x{version:08x}",
            "reserved0": reserved0,
            "total": total,
            "header_size": hdrsz,
            "total2": total2,
            "build_id": f"0x{build_id:08x}",
            "cmdline_len": clen,
            "f20": f"0x{cl_off_a:08x}",
            "f28": f"0x{f28:08x}",
            "f2c": f"0x{f2c:08x}",
            "f30": f"0x{f30:08x}",
        },
        "cmdline": cmdline,
        "trailer_offset": trailer_off,
        "tag": tag.hex(),
        "exponent": exponent,
        "modulus_sha256": hashlib.sha256(modulus).hexdigest(),
        "modulus_bits": int.from_bytes(modulus, "big").bit_length(),
        "signed_range": [0, trailer_off + 4],
        "_raw": raw,
        "_signature": signature,
        "_modulus": modulus,
    }


def verify(info: Dict[str, object]) -> Dict[str, object]:
    raw = info["_raw"]  # type: ignore[index]
    n = int.from_bytes(info["_modulus"], "big")  # type: ignore[index]
    e = int(info["exponent"])  # type: ignore[arg-type]
    s = int.from_bytes(info["_signature"], "big")  # type: ignore[index]
    if not (n.bit_length() == 2048):
        return {"ok": False, "reason": f"modulus is {n.bit_length()} bits, expected 2048"}
    if s >= n:
        return {"ok": False, "reason": "signature is not smaller than the modulus"}
    encoded = pow(s, e, n).to_bytes(SIG_LEN, "big")
    prefix_ok = encoded.startswith(b"\x00\x01") and DIGESTINFO_SHA256 in encoded
    digest = encoded[-32:]
    start, end = info["signed_range"]  # type: ignore[misc]
    computed = hashlib.sha256(raw[start:end]).digest()
    return {
        "ok": bool(prefix_ok and computed == digest),
        "pkcs1_v15_block": encoded[:16].hex(),
        "digestinfo_present": DIGESTINFO_SHA256 in encoded,
        "digest_matches": computed == digest,
        "signed_sha256": digest.hex(),
        "computed_sha256": computed.hex(),
        "signed_range": [hex(start), hex(end)],
        "modulus_sha256": info["modulus_sha256"],
    }


def extract(info: Dict[str, object], outdir: Path, kernel: bool) -> Dict[str, object]:
    raw = info["_raw"]  # type: ignore[index]
    outdir.mkdir(parents=True, exist_ok=True)
    hdrsz = info["header"]["header_size"]  # type: ignore[index]
    total = info["header"]["total"]  # type: ignore[index]
    payload = outdir / "payload.bin"
    payload.write_bytes(raw[hdrsz:hdrsz + total])
    written = {"payload": str(payload), "payload_sha256": hashlib.sha256(payload.read_bytes()).hexdigest()}
    if kernel:
        off = raw.find(b"\x02\x21\x4c\x18")
        if off < 0:
            raise ContainerError("no legacy LZ4 stream found")
        with tempfile.NamedTemporaryFile(suffix=".lz4", delete=False) as tmp:
            tmp.write(raw[off:])
            tmp_path = Path(tmp.name)
        try:
            out = outdir / "vmlinux"
            res = subprocess.run(["lz4", "-d", "-f", str(tmp_path), str(out)],
                                 capture_output=True, text=True)
            if not out.exists():
                raise ContainerError(f"lz4 failed: {res.stderr.strip()}")
            written["kernel"] = str(out)
            written["kernel_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
            written["lz4_offset"] = hex(off)
        finally:
            tmp_path.unlink(missing_ok=True)
    return written


def encode_pkcs1_v15_sha256(digest: bytes, em_len: int) -> bytes:
    if len(digest) != 32:
        raise ContainerError("digest must be 32 bytes")
    t = DIGESTINFO_SHA256 + digest
    ps_len = em_len - len(t) - 3
    if ps_len < 8:
        raise ContainerError("modulus too small for PKCS#1 v1.5")
    return b"\x00\x01" + b"\xff" * ps_len + b"\x00" + t


def resign(info: Dict[str, object], out: Path, key_pem: Path,
           new_cmdline: Optional[str], new_tag: Optional[str]) -> Dict[str, object]:
    """Write a container with the same layout, re-signed by *key_pem*."""

    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding, rsa
    except ImportError as exc:  # pragma: no cover
        raise ContainerError("the 'cryptography' package is required for resign") from exc

    raw = bytearray(info["_raw"])  # type: ignore[index]
    hdrsz = info["header"]["header_size"]  # type: ignore[index]
    clen = info["header"]["cmdline_len"]  # type: ignore[index]
    if new_cmdline is not None:
        encoded = new_cmdline.encode("latin1")
        if len(encoded) > clen:
            raise ContainerError(f"new command line is {len(encoded)} bytes; field is {clen}")
        raw[hdrsz:hdrsz + clen] = encoded.ljust(clen, b"\x00")
    if new_tag is not None:
        trailer_off = info["trailer_offset"]  # type: ignore[index]
        raw[trailer_off:trailer_off + 4] = bytes.fromhex(new_tag)

    trailer_off = hdrsz + info["header"]["total"]  # type: ignore[index]
    signed = bytes(raw[:trailer_off + 4])
    digest = hashlib.sha256(signed).digest()

    key = serialization.load_pem_private_key(key_pem.read_bytes(), password=None)
    if not isinstance(key, rsa.RSAPrivateKey):
        raise ContainerError("key is not an RSA private key")
    numbers = key.private_numbers()
    n = numbers.public_numbers.n
    mod_bytes = n.to_bytes(KEY_LEN, "big")
    em = encode_pkcs1_v15_sha256(digest, KEY_LEN)
    sig = pow(int.from_bytes(em, "big"), numbers.d, n).to_bytes(SIG_LEN, "big")

    raw[trailer_off + 0x100:trailer_off + 0x200] = sig
    raw[trailer_off + 0x200:trailer_off + 0x300] = mod_bytes
    struct.pack_into("<I", raw, trailer_off + 0x300, 65537)
    out.write_bytes(bytes(raw))
    return {
        "output": str(out),
        "sha256": hashlib.sha256(bytes(raw)).hexdigest(),
        "signed_range": [hex(0), hex(trailer_off + 4)],
        "signed_sha256": digest.hex(),
        "new_modulus_sha256": hashlib.sha256(mod_bytes).hexdigest(),
        "self_signed": True,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_info = sub.add_parser("info", help="print header, command line and trailer")
    p_info.add_argument("image", type=Path)
    p_info.add_argument("--json", action="store_true")

    p_ver = sub.add_parser("verify", help="verify the embedded signature")
    p_ver.add_argument("image", type=Path)
    p_ver.add_argument("--json", action="store_true")

    p_ext = sub.add_parser("extract", help="write payload and optionally the kernel")
    p_ext.add_argument("image", type=Path)
    p_ext.add_argument("-o", "--outdir", type=Path, required=True)
    p_ext.add_argument("--kernel", action="store_true")

    p_res = sub.add_parser("resign", help="write a re-signed container (bench testing)")
    p_res.add_argument("image", type=Path)
    p_res.add_argument("-o", "--out", type=Path, required=True)
    p_res.add_argument("--key", type=Path, required=True, help="PEM RSA private key")
    p_res.add_argument("--cmdline", help="replacement kernel command line")
    p_res.add_argument("--tag", help="replacement 4-byte tag as hex")

    args = ap.parse_args(argv)
    try:
        info = parse(args.image)
        if args.cmd == "info":
            printable = {k: v for k, v in info.items() if not k.startswith("_")}
            if args.json:
                print(json.dumps(printable, indent=2))
            else:
                for k in ("path", "size", "sha256", "modulus_bits",
                          "modulus_sha256", "tag", "exponent", "signed_range"):
                    print(f"{k:16} {printable[k]}")
                print("header:")
                for k, v in printable["header"].items():  # type: ignore[index]
                    print(f"  {k:14} {v}")
                print("cmdline:")
                print("  " + str(printable["cmdline"]))
            return 0
        if args.cmd == "verify":
            result = verify(info)
            print(json.dumps(result, indent=2) if args.json else
                  ("VERIFIED" if result["ok"] else "FAILED") + f"  {result}")
            return 0 if result["ok"] else 1
        if args.cmd == "extract":
            print(json.dumps(extract(info, args.outdir, args.kernel), indent=2))
            return 0
        if args.cmd == "resign":
            print(json.dumps(resign(info, args.out, args.key, args.cmdline, args.tag), indent=2))
            return 0
    except ContainerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
