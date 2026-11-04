#!/usr/bin/env python3.13
"""Add a `.sign` section to an ELF and sign it the way AppLauncher verifies it.

Recovered verifier behaviour (docs/engineering-mode/app-signature-check.md):

  * the `.sign` section is found by walking the section header string table
  * its bytes are copied to /tmp/<basename>.sign and its sh_offset is remembered
  * the file is hashed with the `.sign` bytes treated as zero (SHA-256)
  * RSA_verify(NID_sha256, ...) is run against the PEM key at /tmp/app_normal.key
    (PKCS#1 v1.5, 256-byte signature for a 2048-bit key)

So signing means: hash the file while `.sign` is all zeroes, RSA-sign that digest,
then write the 256-byte signature into the section. This tool does both steps and
never needs objcopy (which is not present on this host).

Usage:
  poc_sign.py add   <in> <out>                  # append a zeroed 256-byte .sign section
  poc_sign.py sign  <file> <private.pem>        # sign in place
  poc_sign.py info  <file>                      # show .sign offset/size and payload bytes
"""
import hashlib
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

SIGN_NAME = b".sign"
SIGN_SIZE = 256


def parse(d):
    e_shoff, = struct.unpack_from("<Q", d, 0x28)
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", d, 0x3A)
    shdrs = []
    for i in range(e_shnum):
        b = e_shoff + i * e_shentsize
        name, typ, flags, addr, off, size = struct.unpack_from("<IIQQQQ", d, b)
        shdrs.append(dict(idx=i, hdr_off=b, name=name, type=typ, flags=flags,
                          addr=addr, off=off, size=size))
    strtab = shdrs[e_shstrndx]
    names = []
    for s in shdrs:
        start = strtab["off"] + s["name"]
        names.append(d[start:d.index(b"\0", start)].decode("latin-1"))
    return e_shoff, e_shentsize, e_shnum, e_shstrndx, shdrs, names


def find_sign(d):
    *_, shdrs, names = parse(d)
    for s, n in zip(shdrs, names):
        if n == ".sign":
            return s["off"], s["size"]
    return None


def add_section(src, dst):
    d = bytearray(Path(src).read_bytes())
    e_shoff, e_shentsize, e_shnum, e_shstrndx, shdrs, names = parse(d)
    if ".sign" in names:
        raise SystemExit(".sign already present")

    # 1. place the 256 zero bytes at the end, 16-byte aligned
    while len(d) % 16:
        d.append(0)
    sign_off = len(d)
    d.extend(b"\0" * SIGN_SIZE)

    # 2. new string table = old + ".sign\0", appended after the section body
    old_str = bytes(d[shdrs[e_shstrndx]["off"]:shdrs[e_shstrndx]["off"] + shdrs[e_shstrndx]["size"]])
    new_str = old_str + SIGN_NAME + b"\0"
    name_off = len(old_str)
    while len(d) % 8:
        d.append(0)
    str_off = len(d)
    d.extend(new_str)

    # 3. copy the section headers, repoint .shstrtab, append the .sign header,
    #    then append a rewritten .shstrtab header
    shdrs_raw = [bytearray(d[s["hdr_off"]:s["hdr_off"] + e_shentsize]) for s in shdrs]
    struct.pack_into("<QQ", shdrs_raw[e_shstrndx], 0x18, str_off, len(new_str))  # sh_offset, sh_size
    sign_hdr = bytearray(e_shentsize)
    struct.pack_into("<IIQQQQIIQQ", sign_hdr, 0,
                     name_off, 1, 0, 0, sign_off, SIGN_SIZE, 0, 0, 1, 0)
    shdrs_raw.append(sign_hdr)
    str_idx = len(shdrs_raw)
    str_hdr = bytearray(e_shentsize)
    struct.pack_into("<IIQQQQIIQQ", str_hdr, 0,
                     name_off + len(SIGN_NAME) + 1 if False else shdrs[e_shstrndx]["name"],
                     3, 0, 0, str_off, len(new_str), 0, 0, 1, 0)
    shdrs_raw.append(str_hdr)

    while len(d) % 8:
        d.append(0)
    new_shoff = len(d)
    for h in shdrs_raw:
        d.extend(h)

    struct.pack_into("<Q", d, 0x28, new_shoff)
    struct.pack_into("<H", d, 0x3C, len(shdrs_raw))
    struct.pack_into("<H", d, 0x3E, str_idx)

    Path(dst).write_bytes(d)
    print(f"added .sign at 0x{sign_off:x} ({SIGN_SIZE} bytes); {len(shdrs_raw)} sections")


def digest_with_zeroed_sign(d):
    off, size = find_sign(d) if isinstance(d, (bytes, bytearray)) else (None, None)
    if off is None:
        raise SystemExit("no .sign section: run `add` first")
    buf = bytearray(d)
    buf[off:off + size] = b"\0" * size
    return hashlib.sha256(bytes(buf)).hexdigest(), off, size


def sign(path, priv):
    d = Path(path).read_bytes()
    _hexdigest, off, size = digest_with_zeroed_sign(d)
    with tempfile.TemporaryDirectory() as td:
        t = Path(td) / "zeroed"
        buf = bytearray(d)
        buf[off:off + size] = b"\0" * size
        t.write_bytes(buf)
        sig = Path(td) / "sig.bin"
        subprocess.run(["openssl", "dgst", "-sha256", "-sign", priv, "-out", str(sig), str(t)], check=True)
        blob = sig.read_bytes()
    if len(blob) > size:
        raise SystemExit(f"signature {len(blob)} bytes exceeds section {size}")
    buf = bytearray(d)
    buf[off:off + len(blob)] = blob
    Path(path).write_bytes(buf)
    print(f"signed: {len(blob)} bytes written at 0x{off:x}")


def info(path):
    d = Path(path).read_bytes()
    found = find_sign(d)
    if not found:
        raise SystemExit("no .sign section")
    off, size = found
    sig = d[off:off + size]
    nonzero = sum(1 for b in sig if b)
    print(f".sign file_offset=0x{off:x} size={size} nonzero_bytes={nonzero}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "add" and len(sys.argv) == 4:
        add_section(sys.argv[2], sys.argv[3])
    elif cmd == "sign" and len(sys.argv) == 4:
        sign(sys.argv[2], sys.argv[3])
    elif cmd == "info" and len(sys.argv) == 3:
        info(sys.argv[2])
    else:
        raise SystemExit(__doc__)
