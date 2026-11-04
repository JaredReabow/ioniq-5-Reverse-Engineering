import os
import shutil
#!/usr/bin/env python3.13
"""Build a GPT-partitioned eMMC image for the EU 260128 vendor rootfs.

Reproduces the p1..p17 eMMC layout recovered from the vehicle's own kernel and
fsck logs (see docs/vm/partitioned-image.md).  The active root (p5) is populated
from work/decrypted-eu-260128/extracted-safe/mango-rootfs; rw_data (p11) and navi
(p14) are populated from the same tree's /rw_data and /navi subtrees.  Every
filesystem is created with the 4.1-kernel-safe feature set
(-O ^metadata_csum,^64bit,^flex_bg).

The only guest-visible addition is /etc/modprobe.d/zz-vm-research-no-lge-usb.conf
("install lge_usb_adapter /bin/true"), the measured one-line fix that keeps the
authentic esinit from deadlocking the platform bus on QEMU (no vendor hardware).
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]        # repository root; no absolute host path
WS = PROJECT / "work/vm/partimg"
E2FS = Path(os.environ.get("E2FS_SBIN", shutil.which("mkfs.ext4") or ".")).parent
#                        ^ set E2FS_SBIN if mkfs.ext4 is not on PATH
MKFS = E2FS / "mkfs.ext4"
DEBUGFS = E2FS / "debugfs"
SGDISK = Path(os.environ.get("SGDISK", shutil.which("sgdisk") or "/usr/sbin/sgdisk"))
ROOTFS_TREE = PROJECT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"

# (number, size_mib, label, source_dir or None)
# Sizes p8..p13 are measured from the vehicle's own e2fsck logs (4096-byte blocks).
# Others are documented best-effort estimates; see the write-up.
LAYOUT = [
    (1,   64, "plk1_iasImage",   None),           # boot/ias splash, PLK1
    (2,   64, "plk2_iasPreload", None),           # boot/ias splash, PLK2
    (3, 8192, "rootfs_a",        None),           # inactive root slot
    (4,   16, "misc_unknown",    None),           # role unknown (never named)
    (5, 8192, "rootfs_b_active", ROOTFS_TREE),    # ACTIVE root (boots p5)
    (6,   64, "vr_a",            None),           # VR slot A
    (7,   64, "vr_b",            None),           # VR slot B
    (8, 2048, "log_data",        None),           # measured: 524286 x 4K ~ 2 GiB
    (9, 12288, "update",         None),           # measured: 3145726 x 4K ~ 12 GiB
    (10,  150, "voicememo",      None),           # measured: 38398 x 4K ~ 150 MiB
    (11, 1280, "rw_data",        ROOTFS_TREE / "rw_data"),  # 327678 x 4K ~ 1280 MiB
    (12,   40, "mnt_c",          None),           # measured: 10238 x 4K ~ 40 MiB
    (13,   40, "mnt_backup",     None),           # measured: 10238 x 4K ~ 40 MiB
    (14, 2048, "navi",           ROOTFS_TREE / "navi"),   # AppNavi Bin tree
    (15, 2048, "navi2",          None),
    (16,   64, "unknown16",      None),           # ext4 w/o journal, role unknown
    (17,  256, "space",          None),
]

MKFS_OPTS = ["-O", "^metadata_csum,^64bit,^flex_bg"]


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, **kw)


def sparse_copy(src: Path, dst: Path, offset: int) -> None:
    """Copy src into dst at byte offset, preserving holes (zero blocks)."""
    CHUNK = 1024 * 1024
    total = src.stat().st_size
    with src.open("rb") as fin, dst.open("r+b") as fout:
        fout.seek(offset)
        pos = 0
        while pos < total:
            data = fin.read(CHUNK)
            if not data:
                break
            if data == b"\0" * len(data):
                fout.seek(len(data), 1)   # skip hole
            else:
                fout.write(data)
            pos += len(data)


def mkfs_partition(part_file: Path, src: Path | None, label: str) -> None:
    cmd = [str(MKFS), "-F", "-b", "4096", "-L", label, *MKFS_OPTS]
    if src is not None:
        cmd += ["-d", str(src)]
    cmd.append(str(part_file))
    run(cmd)


def main() -> int:
    total_mib = 1 + sum(size for _, size, _, _ in LAYOUT) + 1  # head + data + tail
    total_bytes = total_mib * 1024 * 1024
    image = WS / "rootfs.img"
    print(f"total image: {total_mib} MiB ({total_bytes} bytes)", flush=True)

    # 1. sparse container + GPT
    with image.open("wb") as f:
        f.truncate(total_bytes)
    sg_args = ["--zap-all"]
    for num, size, label, _ in LAYOUT:
        sg_args += ["-n", f"{num}::+{size}M", "-t", f"{num}:8300", "-c", f"{num}:{label}"]
    run([str(SGDISK), *sg_args, str(image)])

    # 2. read back partition byte offsets
    out = subprocess.run([str(SGDISK), "-p", str(image)], check=True,
                         capture_output=True, text=True).stdout
    starts: dict[int, int] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit():
            starts[int(parts[0])] = int(parts[1]) * 512
    assert set(starts) == {n for n, *_ in LAYOUT}, starts

    # 3. build each filesystem and place it
    build_dir = WS / "partimg-build"
    build_dir.mkdir(exist_ok=True)
    for num, size, label, src in LAYOUT:
        part_file = build_dir / f"p{num}.img"
        with part_file.open("wb") as f:
            f.truncate(size * 1024 * 1024)
        mkfs_partition(part_file, src, label)
        if num == 5:
            override = build_dir / "zz-vm-research-no-lge-usb.conf"
            override.write_text("install lge_usb_adapter /bin/true\n")
            # debugfs -R splits its command string on whitespace, so the source
            # must be a space-free relative path (the project path has spaces).
            run([str(DEBUGFS), "-w", "-R",
                 "write zz-vm-research-no-lge-usb.conf "
                 "/etc/modprobe.d/zz-vm-research-no-lge-usb.conf",
                 str(part_file)], cwd=str(build_dir))
            # debugfs returns 0 even on a usage error; verify the write landed.
            chk = subprocess.run(
                [str(DEBUGFS), "-R", "stat /etc/modprobe.d/zz-vm-research-no-lge-usb.conf",
                 str(part_file)], capture_output=True, text=True)
            if chk.returncode != 0 or "Inode:" not in chk.stdout:
                raise RuntimeError(f"modprobe.d override write failed: {chk.stdout}{chk.stderr}")
        sparse_copy(part_file, image, starts[num])
        print(f"  p{num} ({label}) {size} MiB -> offset {starts[num]}", flush=True)

    # 4. record layout + artifact hashes
    layout = []
    for num, size, label, src in LAYOUT:
        layout.append({
            "partition": num, "label": label, "size_mib": size,
            "byte_offset": starts[num],
            "source_dir": str(src) if src else None,
        })
    (WS / "layout.json").write_text(json.dumps(layout, indent=2) + "\n")

    import hashlib
    def sha(p: Path) -> str:
        return hashlib.file_digest(p.open("rb"), "sha256").hexdigest()
    artifacts = ("bzImage", "rootfs.img", "manifest.bin", "seed_dev.bin", "seed_user.bin")
    meta = {
        "schema": 1,
        "purpose": "GPT-partitioned eMMC projection (p1..p17) for authentic esinit boot",
        "layout": "layout.json",
        "active_root": "/dev/mmcblk0p5",
        "root_arg_change": "root=/dev/mmcblk0 -> root=/dev/mmcblk0p5 (documented in docs/vm/partitioned-image.md)",
        "source_rootfs": str(ROOTFS_TREE),
        "mkfs_options": MKFS_OPTS,
        "guest_additions": {
            "/etc/modprobe.d/zz-vm-research-no-lge-usb.conf":
                "install lge_usb_adapter /bin/true",
        },
        "sha256": {name: sha(WS / name) for name in artifacts},
    }
    (WS / "prepare.json").write_text(json.dumps(meta, indent=2) + "\n")
    print("wrote layout.json and prepare.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
