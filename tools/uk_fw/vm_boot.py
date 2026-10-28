#!/usr/bin/env python3
"""Offline QEMU harness for the recovered EU 260128 kernel, not its vendor UI.

prepare: extract a boot-protocol image and build a BusyBox/ext4 SD root from
local inputs. No downloads, host mounts, root privileges or firmware writes.
run: boot the prepared guest; --sdhci-compat explicitly enables one verified
PCI-ID-table adaptation in guest RAM. The original bzImage stays unchanged.

This replaces the earlier non-working initramfs/default-vmlinux launcher.
All generated files, sockets and QEMU temporary overlays stay in the project.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack, contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import select
import shutil
import socket
import struct
import subprocess
import sys
import time
import uuid

PROJECT = Path(__file__).resolve().parents[2]
KERNEL_SHA256 = "85e0086202758117015437a5ce7b580d7d32484807d1953c3a16e571f65f3f59"
DRIVER_INIT = 0xffffffff81b24bac
TABLE_ENTRY = 0xffffffff8164d100  # entry 61 of table at 0xffffffff8164c960
EXPECTED_ENTRY = struct.pack("<6IQ", 0x1022, 0xffffffff, 0xffffffff, 0xffffffff,
                             0x080500, 0xffff00, 0xffffffff8164d140)
COMPAT_ENTRY = struct.pack("<6IQ", 0x1b36, 7, 0xffffffff, 0xffffffff,
                           0x080500, 0xffff00, 0)
EXT4_FEATURES = ("none,has_journal,ext_attr,resize_inode,dir_index,filetype,extent,"
                 "flex_bg,sparse_super,large_file,huge_file,dir_nlink,extra_isize")
ARTIFACTS = ("bzImage", "rootfs.img", "manifest.bin", "seed_dev.bin", "seed_user.bin")
DEFAULT_COMMAND = ("/bin/busybox uname -r; /bin/busybox id; "
                   "/bin/busybox cat /proc/partitions; "
                   "/bin/busybox ls /sys/kernel/abl")
INIT = """#!/bin/busybox sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
BB=/bin/busybox
$BB mount -t proc proc /proc
$BB mount -t sysfs sysfs /sys
$BB mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
$BB mkdir -p /sys/fs/smackfs
$BB mount -t smackfs smackfs /sys/fs/smackfs 2>/dev/null || true
$BB uname -a
$BB cat /proc/mounts
echo IONIQ_VM_USERSPACE_READY
# This is a research shell, not the infotainment interface.
export PS1='ioniq-vm# '
exec $BB sh
"""


def sha256(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def project_output(path: Path) -> Path:
    path = path.resolve()
    if path == PROJECT or not path.is_relative_to(PROJECT):
        raise ValueError("output must be a subdirectory of the project")
    # QEMU uses commas to separate option values, including file paths.
    if any(c in str(path) for c in (",", "\n", "\r")):
        raise ValueError("output path cannot contain commas or newlines")
    return path


def extract_boot_image(raw: bytes) -> bytes:
    """Validate the IPK bounds and locate one embedded Linux boot header."""
    if len(raw) < 0x34 or raw[:4] != b"ipk.":
        raise ValueError("expected a plaintext ipk. boot container")
    total, header, total2 = struct.unpack_from("<III", raw, 0x0c)
    clen = struct.unpack_from("<I", raw, 0x1c)[0]
    end = header + total
    start_min = (header + clen + 3) & ~3
    if (total != total2 or not 0x34 <= header < 0x1000
            or not start_min < end <= len(raw) - 0x304):
        raise ValueError("invalid/truncated IPK bounds")
    candidates = []
    pos = start_min
    while True:
        pos = raw.find(b"HdrS", pos, end)
        if pos < 0:
            break
        start = pos - 0x202
        if (start >= start_min and start % 4 == 0
                and raw[start + 0x1fe:start + 0x200] == b"\x55\xaa"
                and pos + 8 <= end):
            protocol = struct.unpack_from("<H", raw, start + 0x206)[0]
            setup = raw[start + 0x1f1] or 4
            if protocol >= 0x200 and start + (setup + 1) * 512 < end:
                candidates.append(start)
        pos += 4
    if len(candidates) != 1:
        raise ValueError(f"expected one validated boot image, got {len(candidates)}")
    return raw[candidates[0]:end]


def validate_busybox(path: Path) -> None:
    """Require a static little-endian x86-64 ELF, not a host executable."""
    data = path.read_bytes()
    if len(data) < 64 or data[:6] != b"\x7fELF\x02\x01":
        raise ValueError("BusyBox must be a static ELF64 x86-64 binary")
    if struct.unpack_from("<H", data, 18)[0] != 62:
        raise ValueError("BusyBox is not x86-64")
    phoff = struct.unpack_from("<Q", data, 32)[0]
    entsize, count = struct.unpack_from("<HH", data, 54)
    if entsize < 56 or count == 0 or phoff + entsize * count > len(data):
        raise ValueError("invalid ELF program headers")
    if any(struct.unpack_from("<I", data, phoff + i * entsize)[0] == 3
           for i in range(count)):
        raise ValueError("BusyBox needs a dynamic loader; supply a static build")


def find_mkfs() -> str:
    found = shutil.which("mkfs.ext4")
    fallback = Path("/opt/homebrew/opt/e2fsprogs/sbin/mkfs.ext4")
    if found:
        return found
    if fallback.is_file():
        return str(fallback)
    raise ValueError("mkfs.ext4 is not installed; this tool does not download it")


def prepare(container: Path, busybox: Path, workspace: Path,
            graphics_probe: bool = False) -> Path:
    workspace = project_output(workspace)
    image = extract_boot_image(container.read_bytes())
    if hashlib.sha256(image).hexdigest() != KERNEL_SHA256:
        raise ValueError("this harness supports only the measured EU 260128 kernel")
    validate_busybox(busybox)
    mkfs = find_mkfs()
    workspace.mkdir(parents=True, exist_ok=False)  # Never overwrite earlier work.
    (workspace / "bzImage").write_bytes(image)
    tree = workspace / "rootfs-tree"
    for name in ("bin", "sbin", "proc", "sys", "dev", "tmp", "etc", "run", "opt",
                 "usr/bin", "usr/sbin"):
        (tree / name).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(busybox, tree / "bin/busybox")
    (tree / "bin/busybox").chmod(0o755)
    (tree / "bin/sh").symlink_to("busybox")
    (tree / "sbin/init").symlink_to("../init")
    (tree / "init").write_text(INIT)
    (tree / "init").chmod(0o755)
    (tree / "tmp").chmod(0o1777)
    display_meta = None
    if graphics_probe:
        from vm_display import build_probe
        display_meta = build_probe(workspace / "display-build")
        shutil.copyfile(workspace / "display-build/vm-display", tree / "bin/vm-display")
        (tree / "bin/vm-display").chmod(0o755)
        shutil.copyfile(workspace / "display-build/vm-display.bgra", tree / "opt/vm-display.bgra")
    with (workspace / "rootfs.img").open("xb") as f:
        f.truncate(256 * 1024**2)
    command = [mkfs, "-F", "-b", "4096", "-I", "256", "-O", EXT4_FEATURES,
               "-E", "lazy_itable_init=0,lazy_journal_init=0", "-d", str(tree),
               str(workspace / "rootfs.img")]
    with (workspace / "mkfs.log").open("wb") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    # Synthetic inputs for the emulator only: no authentic device keys.
    manifest = bytearray(64)
    struct.pack_into("<II", manifest, 0, 0xe, 0x24)
    (workspace / "manifest.bin").write_bytes(manifest)
    for kind in ("dev", "user"):
        (workspace / f"seed_{kind}.bin").write_bytes(
            f"IONIQ-VM-ONLY-{kind}".encode().ljust(64, b"\0"))
    meta = {"schema": 1, "container": str(container.resolve()),
            "container_sha256": sha256(container), "busybox_sha256": sha256(busybox),
            "mkfs_command": command, "synthetic_seeds": True,
            "display_probe": display_meta,
            "sha256": {name: sha256(workspace / name) for name in ARTIFACTS}}
    (workspace / "prepare.json").write_text(json.dumps(meta, indent=2) + "\n")
    return workspace


def verify_workspace(workspace: Path) -> None:
    meta = json.loads((workspace / "prepare.json").read_text())
    if meta.get("schema") != 1 or set(meta.get("sha256", {})) != set(ARTIFACTS):
        raise ValueError("invalid prepared workspace manifest")
    for name in ARTIFACTS:
        if (workspace / name).is_symlink():
            raise ValueError(f"prepared artifact cannot be a symlink: {name}")
        if sha256(workspace / name) != meta["sha256"][name]:
            raise ValueError(f"prepared artifact changed: {name}")
    if meta["sha256"]["bzImage"] != KERNEL_SHA256:
        raise ValueError("kernel is not the supported exact build")


@contextmanager
def connect_unix(directory: Path, name: str):
    """Use a short relative socket name within macOS's sockaddr_un limit."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    previous = Path.cwd()
    try:
        sock.settimeout(30)
        try:
            os.chdir(directory)
            sock.connect(name)
        finally:
            os.chdir(previous)
        yield sock
    finally:
        sock.close()


def decode_rsp(data: bytes) -> bytes:
    result = bytearray()
    i = 0
    while i < len(data):
        c = data[i]
        if c in (ord("}"), ord("*")):
            i += 1
            if i == len(data):
                raise ValueError("truncated RSP escape/repeat")
            if c == ord("}"):
                result.append(data[i] ^ 0x20)
            else:
                if not result or data[i] < 29:
                    raise ValueError("invalid RSP repeat")
                result.extend(result[-1:] * (data[i] - 29))
        else:
            result.append(c)
        i += 1
    return bytes(result)


class RSP:
    def __init__(self, sock):
        self.sock = sock

    def read_exact(self, count):
        data = bytearray()
        while len(data) < count:
            chunk = self.sock.recv(count - len(data))
            if not chunk:
                raise EOFError("QEMU debug connection closed")
            data.extend(chunk)
        return bytes(data)

    def request(self, command: str) -> str:
        payload = command.encode("ascii")
        self.sock.sendall(b"$" + payload + b"#" + f"{sum(payload) & 255:02x}".encode())
        while True:
            c = self.read_exact(1)
            if c == b"$":
                break
            if c == b"-":
                raise ValueError("QEMU rejected RSP checksum")
        packet = bytearray()
        while True:
            c = self.read_exact(1)
            if c == b"#":
                break
            packet.extend(c)
            if len(packet) > 65536:
                raise ValueError("RSP packet too large")
        if int(self.read_exact(2), 16) != sum(packet) & 255:
            raise ValueError("QEMU RSP checksum mismatch")
        self.sock.sendall(b"+")
        return decode_rsp(packet).decode("ascii")


def adapt_sdhci(rsp: RSP) -> dict:
    """Stop at the driver's initcall; replace exactly one checked table record."""
    def ok(command):
        response = rsp.request(command)
        if response != "OK":
            raise ValueError(f"QEMU rejected {command.split(',')[0]}: {response}")
    rsp.request("?")
    ok(f"Z1,{DRIVER_INIT:x},1")
    stop = rsp.request("c")
    if not stop.startswith(("T05", "S05")):
        raise ValueError(f"unexpected stop before SDHCI init: {stop}")
    actual = bytes.fromhex(rsp.request(f"m{TABLE_ENTRY:x},20"))
    if actual != EXPECTED_ENTRY:
        raise ValueError("SDHCI table bytes differ; refusing the guest-memory write")
    ok(f"M{TABLE_ENTRY:x},20:{COMPAT_ENTRY.hex()}")
    if bytes.fromhex(rsp.request(f"m{TABLE_ENTRY:x},20")) != COMPAT_ENTRY:
        raise ValueError("guest-memory readback does not match")
    ok(f"z1,{DRIVER_INIT:x},1")
    ok("D")  # Detach resumes the guest.
    return {"address": hex(TABLE_ENTRY), "breakpoint": hex(DRIVER_INIT),
            "original": EXPECTED_ENTRY.hex(), "replacement": COMPAT_ENTRY.hex(),
            "scope": "guest RAM only; removes AMD quirks for QEMU's generic controller"}


def qemu_command(workspace: Path, qemu: str, compat: bool,
                 display: str = "none", qmp: bool = False) -> list[str]:
    if display not in ("none", "cocoa"):
        raise ValueError("supported display backends: none, cocoa")
    command = [qemu, "-machine", "q35", "-accel", "tcg", "-cpu", "max,vendor=GenuineIntel",
               "-m", "1024", "-smp", "2", "-nic", "none",
               "-vga", "none", "-device", "VGA,id=display0,addr=01.0",
               "-kernel", str(workspace / "bzImage")]
    for name, address in (("manifest.bin", "0x20000000"), ("seed_dev.bin", "0x21000000"),
                          ("seed_user.bin", "0x21000040")):
        command += ["-device", f"loader,file={workspace / name},addr={address}"]
    command += ["-device", "sdhci-pci,id=sdhci0", "-drive",
                f"if=none,id=sd0,format=raw,file={workspace / 'rootfs.img'},snapshot=on",
                "-device", "sd-card,drive=sd0", "-append",
                "root=/dev/mmcblk0 rootwait rootdelay=2 rootfstype=ext4 rw init=/init "
                "console=ttyS0,115200 panic=-1 loglevel=7 "
                "ABL.oemkm=40@20000000 ABL.seed=21000000,21000040",
                "-display", display, "-serial", "stdio", "-monitor", "none", "-no-reboot"]
    if compat:
        command += ["-gdb", "unix:gdb.sock,server=on,wait=off", "-S"]
    if qmp:
        command += ["-qmp", "unix:qmp.sock,server=on,wait=off"]
    return command


def shell_script(command: str, end_marker: str) -> str:
    # Parse the whole group before execution. A separate status line can be
    # consumed as input by an interactive child such as the display diagnostic.
    return f"{{\n{command}\n}}; rc=$?; printf '\\n{end_marker}:%s\\n' \"$rc\"\n"


def run(workspace: Path, compat: bool, command: str, timeout: float,
        interactive: bool = False, display: str = "none",
        graphics_smoke: bool = False) -> int:
    workspace = project_output(workspace)
    verify_workspace(workspace)
    qemu = shutil.which("qemu-system-x86_64")
    if not qemu:
        raise ValueError("qemu-system-x86_64 is not installed")
    if timeout < 0 or (timeout == 0 and not interactive):
        raise ValueError("timeout must be positive (or zero for interactive mode)")
    if graphics_smoke:
        if interactive:
            raise ValueError("graphics smoke and interactive modes are separate")
        if not json.loads((workspace / "prepare.json").read_text()).get("display_probe"):
            raise ValueError("prepare a new workspace with --graphics-probe first")
        command = "/bin/vm-display"
    run_dir = workspace / "runs" / f"{time.time_ns()}"
    run_dir.mkdir(parents=True)
    argv = qemu_command(workspace, qemu, compat, display, graphics_smoke)
    (run_dir / "command.json").write_text(json.dumps(argv, indent=2) + "\n")
    print(f"Run artifacts: {run_dir}", flush=True)
    token = uuid.uuid4().hex
    end_marker = f"VM_COMMAND_END_{token}"
    result = {"userspace": False, "root_mounted": False, "command_exit_code": None,
              "compatibility_patch": compat, "timeout": False, "error": None}
    start = time.monotonic()
    sent = False
    captured = bytearray()
    proc = None
    resources = ExitStack()
    smoke = None
    try:
        with (run_dir / "serial.log").open("wb") as log:
            proc = subprocess.Popen(argv, cwd=run_dir, stdin=subprocess.PIPE,
                                    stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, "TMPDIR": str(run_dir)})
            if compat:
                for _ in range(100):
                    if (run_dir / "gdb.sock").exists():
                        break
                    if proc.poll() is not None:
                        raise RuntimeError("QEMU exited before debug socket was ready")
                    if timeout and time.monotonic() - start >= timeout:
                        raise TimeoutError("debug socket deadline exceeded")
                    time.sleep(.05)
                with connect_unix(run_dir, "gdb.sock") as sock:
                    if timeout:
                        sock.settimeout(max(.01, min(30, timeout - (time.monotonic() - start))))
                    patch = adapt_sdhci(RSP(sock))
                (run_dir / "patch.json").write_text(json.dumps(patch, indent=2) + "\n")
            if graphics_smoke:
                from vm_display import GraphicsSmoke, QMP
                sock = resources.enter_context(connect_unix(run_dir, "qmp.sock"))
                sock.settimeout(5)
                qmp = QMP(sock)
                resources.callback(qmp.close)
                smoke = GraphicsSmoke(qmp, run_dir)
            with (run_dir / "serial.log").open("rb") as reader:
                while True:
                    chunk = reader.read()
                    if chunk:
                        captured.extend(chunk)
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.buffer.flush()
                    text = captured.decode("utf-8", errors="replace").replace("\r", "")
                    result["userspace"] = "\nIONIQ_VM_USERSPACE_READY\n" in text
                    result["root_mounted"] = "VFS: Mounted root (ext4 filesystem)" in text
                    if smoke:
                        smoke.advance(text)
                    matched = re.search(r"^" + end_marker + r":(\d+)$", text, re.M)
                    if matched:
                        result["command_exit_code"] = int(matched[1])
                        if not interactive:
                            break
                    if proc.poll() is not None:
                        break
                    if timeout and time.monotonic() - start >= timeout:
                        result["timeout"] = True
                        break
                    if result["userspace"] and not sent:
                        script = shell_script(command, end_marker)
                        proc.stdin.write(script.encode()); proc.stdin.flush()
                        sent = True
                    if interactive and sent and select.select([sys.stdin], [], [], 0)[0]:
                        line = sys.stdin.readline()
                        if not line:
                            break
                        proc.stdin.write(line.encode()); proc.stdin.flush()
                    time.sleep(.05)
    except KeyboardInterrupt:
        result["error"] = "interrupted"
    except Exception as exc:
        result["error"] = str(exc)
        if isinstance(exc, TimeoutError):
            result["timeout"] = True
    finally:
        if graphics_smoke:
            result["graphics_passed"] = bool(smoke and smoke.complete)
        if smoke:
            (run_dir / "graphics.json").write_text(json.dumps(smoke.report(), indent=2) + "\n")
        resources.close()
        if proc is not None:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait()
            proc.stdin.close()
            result["qemu_returncode"] = proc.returncode
        result["elapsed_seconds"] = round(time.monotonic() - start, 2)
        (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print("\n" + json.dumps(result, indent=2))
    return 0 if (result["userspace"] and result["root_mounted"]
                 and result["command_exit_code"] == 0 and not result["error"]
                 and not result["timeout"] and result.get("graphics_passed", True)) else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare", help="build an offline workspace from existing files")
    prep.add_argument("--container", type=Path, required=True)
    prep.add_argument("--busybox", type=Path, default=PROJECT / "work/vm/busybox")
    prep.add_argument("--workspace", type=Path, default=PROJECT / "work/vm/bootable")
    prep.add_argument("--graphics-probe", action="store_true", help="add our QEMU-only display diagnostic, NOT vendor UI")
    boot = sub.add_parser("run", help="boot and test the guest serial shell")
    boot.add_argument("--workspace", type=Path, default=PROJECT / "work/vm/bootable")
    boot.add_argument("--sdhci-compat", action="store_true", help="adapt one PCI table entry in guest RAM")
    boot.add_argument("--cmd", default=DEFAULT_COMMAND)
    boot.add_argument("--timeout", type=float, default=60)
    boot.add_argument("--interactive", action="store_true", help="forward terminal input; Ctrl-C stops QEMU")
    boot.add_argument("--display", choices=("none", "cocoa"), default="none")
    boot.add_argument("--graphics-smoke", action="store_true", help="verify diagnostic pixels and QEMU keyboard input")
    args = parser.parse_args(argv)
    try:
        if args.action == "prepare":
            print(prepare(args.container, args.busybox, args.workspace, args.graphics_probe))
            return 0
        if args.graphics_smoke and args.cmd != DEFAULT_COMMAND:
            raise ValueError("--graphics-smoke supplies its own command; omit --cmd")
        return run(args.workspace, args.sdhci_compat, args.cmd, args.timeout,
                   args.interactive, args.display, args.graphics_smoke)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"vm_boot: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
