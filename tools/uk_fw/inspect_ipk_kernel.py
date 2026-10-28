#!/usr/bin/env python3
"""Inspect Hyundai Gen5W_L ``ipk.`` kernel containers without executing them.

The tool locates the legacy LZ4 stream embedded in an ``iasImage*_sub`` file,
decompresses it with the local ``lz4`` utility, and extracts the kernel's
embedded IKCONFIG payload.  It never mounts an image or runs target code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zlib
from pathlib import Path


IPK_MAGIC = b"ipk."
LZ4_LEGACY_MAGIC = b"\x02\x21\x4c\x18"
IKCONFIG_START = b"IKCFG_ST"


def sha256(data: bytes) -> str:
    """Return the lowercase SHA-256 digest for *data*."""

    return hashlib.sha256(data).hexdigest()


def decompress_gzip_member(data: bytes) -> bytes:
    """Decompress the first gzip member and ignore unrelated trailing bytes."""

    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    output = decoder.decompress(data) + decoder.flush()
    if not decoder.eof:
        raise ValueError("truncated gzip stream")
    return output


def inspect_ipk(path: Path) -> dict[str, object]:
    """Return reproducible kernel metadata extracted from one IPK container."""

    raw = path.read_bytes()
    if not raw.startswith(IPK_MAGIC):
        raise ValueError(f"{path} does not start with the ipk. magic")

    lz4_offset = raw.find(LZ4_LEGACY_MAGIC)
    if lz4_offset < 0:
        raise ValueError("legacy LZ4 stream not found")
    lz4 = shutil.which("lz4")
    if lz4 is None:
        raise RuntimeError("the lz4 command is required")

    with tempfile.TemporaryDirectory(prefix="ioniq-ipk-") as temp:
        temp_path = Path(temp)
        compressed = temp_path / "kernel.lz4"
        kernel = temp_path / "kernel.elf"
        compressed.write_bytes(raw[lz4_offset:])
        result = subprocess.run(
            [lz4, "-d", str(compressed), str(kernel)],
            capture_output=True,
            text=True,
            check=False,
        )
        # Hyundai appends signature/padding bytes after the legacy LZ4 frame.
        # lz4 reports that trailer as undecodable and returns non-zero even
        # though it has already emitted the complete ELF.  Validate the
        # produced bytes below instead of treating the trailer as failure.
        if not kernel.exists() or kernel.stat().st_size == 0:
            raise RuntimeError(f"lz4 decompression failed: {result.stderr.strip()}")
        kernel_bytes = kernel.read_bytes()

    if not kernel_bytes.startswith(b"\x7fELF"):
        raise ValueError("decompressed payload is not an ELF image")

    config_offset = kernel_bytes.find(IKCONFIG_START)
    if config_offset < 0:
        raise ValueError("IKCONFIG marker not found")
    gzip_offset = kernel_bytes.find(b"\x1f\x8b\x08", config_offset + len(IKCONFIG_START))
    if gzip_offset < 0 or gzip_offset > config_offset + len(IKCONFIG_START) + 32:
        raise ValueError("IKCONFIG gzip stream not found after marker")
    # Consume exactly one gzip member. ``gzip.GzipFile`` automatically follows
    # concatenated members and therefore mistakes the kernel's trailing
    # ``IKCFG_ED`` marker and unrelated bytes for another gzip header.
    config = decompress_gzip_member(kernel_bytes[gzip_offset:])
    config_text = config.decode("utf-8", errors="replace")

    banner = next(
        (
            line
            for line in kernel_bytes.decode("latin-1", errors="ignore").split("\x00")
            if line.startswith("Linux version ")
        ),
        None,
    )
    selected = {}
    names = {
        "CONFIG_64BIT",
        "CONFIG_X86_64",
        "CONFIG_IKCONFIG",
        "CONFIG_IKCONFIG_PROC",
        "CONFIG_MODULES",
        "CONFIG_MODULE_SIG",
        "CONFIG_RANDOMIZE_BASE",
        "CONFIG_STRICT_DEVMEM",
        "CONFIG_DEVKMEM",
        "CONFIG_PROC_KCORE",
        "CONFIG_DEBUG_FS",
        "CONFIG_KEXEC",
        "CONFIG_KEXEC_FILE",
        "CONFIG_SECURITY_SMACK",
        "CONFIG_SECURITY_SELINUX",
        "CONFIG_SECURITY_APPARMOR",
        "CONFIG_DEFAULT_SECURITY",
        "CONFIG_USER_NS",
        "CONFIG_SECCOMP",
        "CONFIG_SECCOMP_FILTER",
    }
    for line in config_text.splitlines():
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            if key in names:
                selected[key] = value
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            key = line[2 : -len(" is not set")]
            if key in names:
                selected[key] = "not-set"

    return {
        "container": str(path),
        "container_size": len(raw),
        "container_sha256": sha256(raw),
        "lz4_offset": lz4_offset,
        "kernel_size": len(kernel_bytes),
        "kernel_sha256": sha256(kernel_bytes),
        "elf_class": 64 if kernel_bytes[4] == 2 else 32,
        "elf_little_endian": kernel_bytes[5] == 1,
        "kernel_banner": banner,
        "config_sha256": sha256(config),
        "selected_config": selected,
    }


def main() -> int:
    """Command-line entry point."""

    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_ipk(args.image), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
