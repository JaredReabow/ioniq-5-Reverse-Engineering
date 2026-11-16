#!/usr/bin/env python3
"""Prepare a vendor-userspace workspace from the extracted EU 260128 trees.

prepare: assemble the recovered root (vendor libs, /app, /system/new_gui, /navi)
with a research init that brings up D-Bus, weston and AppLauncher, then build the
ext4 SD image. run: reuse vm_boot's launch, so the kernel, the guest-RAM SDHCI
patch and the serial protocol stay identical across both workspaces.

This is the vendor chain, not the vendor product: the init script is ours, no
vehicle bus input is fabricated, and nothing outside the project is written.
All sources are local extracted trees under ignored work/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import vm_boot  # noqa: E402

DEFAULT_TREE_ROOT = PROJECT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"
DEFAULT_NEW_GUI = PROJECT / "work/decrypted-eu-260128/extracted-safe/new_gui/system/new_gui"
DEFAULT_NAVI = PROJECT / "work/decrypted-eu-260128/extracted-safe/appnavi"
DEFAULT_WORKSPACE = PROJECT / "work/vm/vendor-userspace-260128"
# The guest attaches rootfs.img as an SD card, and QEMU accepts only a power-of-two
# card size, so the assembled root (about 5.2 GiB) needs an 8 GiB image.
DEFAULT_IMAGE_MIB = 8192
# Every binary the chain needs inside the guest; the builder and its tests share
# this list so a new helper cannot be added to one and forgotten in the other.
HELPER_BUILDS = (
    ("navi-bg-0x0.so", "navi_bg_0x0.c"),
    ("launcher-appnavi-navibg.so", "launcher_appnavi_navibg_preload.c"),
)
HELPER_PROGRAMS = (
    ("interpose-probe", "interpose_probe.c"),
    ("guest-client-probe", "guest_client_probe.c"),
)
HELPER_BINARIES = tuple(name for name, _ in HELPER_BUILDS + HELPER_PROGRAMS)
HELPERS = PROJECT / "tools/uk_fw/guest"

WESTON_INI = """[core]
backend=headless-backend.so
shell=ivi-shell.so
idle-time=0
[ivi-shell]
ivi-module=ivi-window-manager.so,ivi-controller.so
ivi-shell-user-interface=/bin/true
base-layer-id=1000
workspace-background-layer-id=2000
workspace-layer-id=3000
application-layer-id=4000
transition-duration=0
workspace-background-color=0xff000000
[output]
name=headless
mode=1920x720
"""

INIT = """#!/bin/busybox sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/opt/vm
BB=/bin/busybox
$BB mount -t proc proc /proc
$BB mount -t sysfs sysfs /sys
$BB mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
$BB mkdir -p /sys/fs/smackfs
$BB mount -t smackfs smackfs /sys/fs/smackfs 2>/dev/null || true
$BB mkdir -p /run/dbus /run/lock /run/user/root /tmp /rw_data/var/volatile/log \
    /rw_data/var/volatile/tmp /rw_data/dlt /log_data
$BB chmod 700 /run/user/root
$BB chmod 1777 /tmp
$BB uname -a
$BB cat /proc/mounts
# vm_boot.run waits for this exact line before it types the command.
echo IONIQ_VM_USERSPACE_READY
echo IONIQ_VM_VENDOR_READY
export PS1='ioniq-vendor# '
exec $BB sh
"""

CHAIN = """#!/bin/busybox sh
# Vendor userspace chain, driven by the research harness. Every stage reports a
# marker so a failing stage is visible instead of collapsing into one result.
BB=/bin/busybox
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/opt/vm
export LD_LIBRARY_PATH=/app/lib:/usr/lib:/lib
export XDG_RUNTIME_DIR=/run/user/root
export WAYLAND_DISPLAY=wayland-0
export QT_QPA_PLATFORM=wayland
unset QT_WAYLAND_SHELL_INTEGRATION
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
$BB mkdir -p /tmp/chain /run/dbus /run/user/root /rw_data/dlt
$BB chmod 700 /run/user/root
echo VENDOR_CHAIN_BEGIN
echo STAGE loader
/usr/bin/weston --version >/tmp/chain/weston-version.txt 2>&1 && echo LOADER_OK || echo LOADER_FAILED
$BB cat /tmp/chain/weston-version.txt
echo STAGE dbus
# /etc/passwd is a symlink into /tmp, and the vendor root ships the real
# database as passwd.legacy: without it every NSS lookup makes dbus-daemon
# abort with "Unknown username". /var is a symlink into rw_data.
$BB cp /etc/passwd.legacy /tmp/passwd
# The recovered profile users exist in the vendor bus policy but not in the
# legacy database; their absence only produces bus configuration warnings.
echo 'xuser:x:1000:100:xuser:/home/xuser:/bin/sh' >>/tmp/passwd
echo 'byungsu:x:1001:100:byungsu:/home/byungsu:/bin/sh' >>/tmp/passwd
$BB mkdir -p /var/run/dbus /var/lib/dbus /run/dbus
/usr/bin/dbus-uuidgen --ensure >/tmp/chain/dbus-uuid.txt 2>&1
/usr/bin/dbus-daemon --system --fork 2>/tmp/chain/system-dbus.err && echo DBUS_SYSTEM_OK || echo DBUS_SYSTEM_FAILED
/usr/bin/dbus-daemon --session --print-address --fork >/tmp/chain/session-address.txt 2>/tmp/chain/session-dbus.err \
    && echo DBUS_SESSION_OK || echo DBUS_SESSION_FAILED
DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/chain/session-address.txt)
export DBUS_SESSION_BUS_ADDRESS
echo DBUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS
echo DBUS_SYSTEM_ERR=$($BB cat /tmp/chain/system-dbus.err 2>/dev/null)
echo DBUS_SESSION_ERR=$($BB cat /tmp/chain/session-dbus.err 2>/dev/null)
$BB ls -l /usr/bin/dbus-daemon /usr/share/dbus-1/system.conf /etc/machine-id /var/lib/dbus/machine-id 2>&1
echo STAGE interposition
LD_PRELOAD=/opt/vm/navi-bg-0x0.so /opt/vm/interpose-probe /usr/lib/libwayland-client.so.0
echo STAGE weston
# weston 1.10 selects its backend from the config file, not from a flag.
/usr/bin/weston --config=/opt/vm/weston.ini --use-pixman --socket=wayland-0 \
    --idle-time=0 --debug >/tmp/chain/weston.log 2>&1 &
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    [ -S /run/user/root/wayland-0 ] && break
    $BB sleep 1
done
[ -S /run/user/root/wayland-0 ] && echo WESTON_SOCKET_OK || echo WESTON_SOCKET_MISSING
# The observer's attach/commit path, exercised against a real vendor Wayland
# client on a fresh compositor: weston-simple-shm is the only vendor client whose
# libraries the recovered root still carries (the rest need libwebp.so.5). The
# hold forces the null attach this project cares about.
echo STAGE guest-client
# A real client on the vendor libwayland: it sends a client-requested null
# attach and its commit through the same exported symbols the observer wraps.
NAVI_BG_CLIENT_MATCH=guest-client-probe \
    NAVI_BG_LOG_FILE=/tmp/navi-bg-client.log \
    LD_PRELOAD=/opt/vm/navi-bg-0x0.so \
    /opt/vm/guest-client-probe >/tmp/chain/client.log 2>&1
echo CLIENT_RC=$?
$BB cat /tmp/chain/client.log 2>/dev/null
$BB grep 'navi-bg:' /tmp/navi-bg-client.log 2>/dev/null | $BB tail -n 30
echo GUEST_CLIENT_LINES=$($BB grep -c 'navi-bg:' /tmp/navi-bg-client.log 2>/dev/null)
echo STAGE dlt
/usr/bin/dlt-daemon -d >/tmp/chain/dlt.log 2>&1 &
$BB sleep 1
echo DLT_PIDS=$(pidof dlt-daemon 2>/dev/null | $BB tr '\n' ' ')
# The vendor EGL needs an i965 GPU, which QEMU does not emulate. The software stack
# is bound over the vendor entry points only when the workspace marker is present
# (vendor_rootfs.py run --software-gl), because the substitution is experimental:
# the vendor libraries carry an RPATH that beats LD_LIBRARY_PATH.
if [ -e /opt/vm/enable-software-gl ]; then
    export LD_LIBRARY_PATH=/opt/swrast/lib:$LD_LIBRARY_PATH
    export LIBGL_DRIVERS_PATH=/opt/swrast/dri
    export GALLIUM_DRIVER=llvmpipe
    export LIBGL_ALWAYS_SOFTWARE=1
    export EGL_PLATFORM=wayland
    for swrast_lib in libEGL.so.1 libGLESv2.so.2 libwayland-egl.so.1 libglapi.so.0; do
        if [ -e /usr/lib/$swrast_lib ] && [ -e /opt/swrast/lib/$swrast_lib ]; then
            $BB mount --bind /opt/swrast/lib/$swrast_lib /usr/lib/$swrast_lib 2>/dev/null \
                && echo SWRAST_BOUND=$swrast_lib
        fi
    done
    echo SOFTWARE_GL=enabled
else
    echo SOFTWARE_GL=disabled
fi
echo STAGE launcherecho STAGE launcher
# AppLauncher drops LD_PRELOAD for itself, so the launcher-local shim is the only
# way to hand the observer to its AppNavi child.
$BB mkdir -p /tmp/launcher-chain
[ -e /navi/navi/Bin ] || $BB ln -sfn /navi /navi/navi
( cd /app/bin && LD_PRELOAD=/opt/vm/launcher-appnavi-navibg.so /app/bin/AppLauncher 3 \
    >/tmp/chain/launcher.log 2>&1 & )
$BB sleep 20
echo APPLAUNCHER_PIDS=$(pidof AppLauncher 2>/dev/null | $BB tr '\n' ' ')
# Sample the manager while it is alive: a later snapshot cannot show a process that
# has since exited, so the assertion is taken at launch time, not at the end.
echo LAUNCHER_MANAGER=$($BB ps 2>/dev/null | $BB grep -c 'ApplicationManager')
echo STAGE navigation
# The vendor BusyBox has no timeout applet; dbus-send bounds its own reply wait.
/usr/bin/dbus-send --session --print-reply --reply-timeout=20000 \
    --dest=com.lge.avn.applauncher /Request \
    com.lge.avn.applauncher.request.launch int32:30 string:AppNavi \
    string:/navi/navi/Bin/AppNavi >/tmp/chain/nav-request.txt 2>&1 \
    && echo NAVI_REQUEST_OK || echo NAVI_REQUEST_FAILED
$BB cat /tmp/chain/nav-request.txt
$BB sleep 25
echo APPNAVI_PIDS=$(pidof AppNavi 2>/dev/null | $BB tr '\n' ' ')
echo STAGE observer
NPID=$($BB pidof AppNavi 2>/dev/null | $BB cut -d' ' -f1)
echo APPNAVI_PID=$NPID
if [ -n "$NPID" ]; then
    echo APPNAVI_ENV=$($BB tr '\0' '\n' < /proc/$NPID/environ 2>/dev/null | $BB grep -E 'LD_PRELOAD|NAVI_BG_LOG_FILE')
    echo APPNAVI_UID=$($BB grep '^Uid:' /proc/$NPID/status 2>/dev/null)
    echo APPNAVI_MAPS=$($BB grep -c 'navi-bg-0x0' /proc/$NPID/maps 2>/dev/null)
    echo APPNAVI_CMDLINE=$($BB tr '\0' ' ' < /proc/$NPID/cmdline 2>/dev/null)
fi
echo LIVENESS_LOG=$($BB tail -n 3 /tmp/launcher-chain/appnavi-liveness-compat.log 2>/dev/null)
if [ -n "$NPID" ]; then
    # Where the client's own output goes, and what renderer it managed to map:
    # this is the measurement behind the navigation status, not a guess.
    echo APPNAVI_STDOUT=$($BB readlink /proc/$NPID/fd/1 2>/dev/null)
    echo APPNAVI_STDERR=$($BB readlink /proc/$NPID/fd/2 2>/dev/null)
    APPNAVI_OUT=$($BB readlink /proc/$NPID/fd/2 2>/dev/null)
    case "$APPNAVI_OUT" in
        /*) $BB tail -n 12 "$APPNAVI_OUT" 2>/dev/null ;;
    esac
    echo APPNAVI_RENDER_MAPS=$($BB grep -cE 'libEGL|libGLESv2|swrast|i965|libwayland-egl' /proc/$NPID/maps 2>/dev/null)
    # A connected Wayland client's fd shows socket:[N], never a path, so the socket
    # table cannot attribute a client to the compositor. Count the raw sockets and
    # read the compositor's own debug log instead; only that log can say who asked.
    echo APPNAVI_SOCKET_FDS=$($BB ls -l /proc/$NPID/fd 2>/dev/null | $BB grep -c 'socket:\\[')
    echo APPNAVI_SWRAST_MAPS=$($BB grep -cE 'swrast_dri|libLLVM' /proc/$NPID/maps 2>/dev/null)
    echo APPNAVI_GL_LIBS=$($BB grep -oE 'lib(EGL|GLESv2|wayland-egl|i965_dri)|swrast_dri|libLLVM[^ ]*' /proc/$NPID/maps 2>/dev/null | $BB sort -u | $BB tr '\n' ' ')
fi
echo OPT_DIR=$($BB ls /opt 2>/dev/null | $BB tr '\n' ' ')
echo DMESG_TOTAL=$($BB dmesg 2>/dev/null | $BB wc -l)
$BB dmesg 2>/dev/null | $BB grep 'navi-bg' | $BB tail -n 25
echo OBSERVER_SUMMARY_LINES=$($BB dmesg 2>/dev/null | $BB grep -c 'navi-bg:')
# The observer writes to /dev/kmsg and to stderr; a child inherits the launcher's
# stderr, so both channels are read rather than trusting one of them.
echo OBSERVER_STDERR_LINES=$($BB grep -c 'navi-bg:' /tmp/chain/launcher.log 2>/dev/null)
$BB grep 'navi-bg:' /tmp/chain/launcher.log 2>/dev/null | $BB tail -n 20
echo OBSERVER_FILE_LINES=$($BB grep -c 'navi-bg:' /tmp/navi-bg.log 2>/dev/null)
$BB grep 'navi-bg:' /tmp/navi-bg.log 2>/dev/null | $BB tail -n 25
# AppNavi needs its Qt/EGL stack and TCG is slow: give it a real window before
# reading the observation lines again.
# Diagnosis for the software-GL path: the launcher discards the child's output, so
# the same client is run directly with the launcher's session bus and a log file.
# Only runs when the workspace opts into the experimental stack.
if [ -e /opt/vm/enable-software-gl ]; then
    echo STAGE appnavi-direct
    if [ -s /tmp/session_appmgr ]; then
        DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr) \
            LD_LIBRARY_PATH=/opt/swrast/lib:/app/lib:/usr/lib:/lib \
            LIBGL_DRIVERS_PATH=/opt/swrast/dri GALLIUM_DRIVER=llvmpipe \
            LIBGL_ALWAYS_SOFTWARE=1 EGL_PLATFORM=wayland \
            /navi/Bin/AppNavi -cv:0 -vv:0 -sv:0 -dt:0 -l:0 -ck:0 -gui:1 -usm:1 \
            -sc:0 -vc:65 >/tmp/chain/appnavi-direct.log 2>&1 &
        $BB sleep 40
        echo DIRECT_ALIVE=$($BB pidof AppNavi 2>/dev/null | $BB tr '\n' ' ')
        $BB tail -n 12 /tmp/chain/appnavi-direct.log 2>/dev/null
    else
        echo DIRECT_SKIPPED=no-session-address
    fi
fi
12289echo STAGE observer-late
$BB sleep 75
echo APPNAVI_ALIVE=$($BB pidof AppNavi 2>/dev/null)
echo WESTON_SURFACES_LATE=$($BB grep -c 'create_surface' /tmp/chain/weston.log 2>/dev/null)
echo OBSERVER_NAVI_LINES=$($BB grep -c 'navi-bg: surface' /tmp/navi-bg.log 2>/dev/null)
$BB dmesg 2>/dev/null | $BB grep 'navi-bg' | $BB tail -n 30
echo OBSERVER_LATE_LINES=$($BB dmesg 2>/dev/null | $BB grep -c 'navi-bg:')
echo OBSERVER_LATE_STDERR=$($BB grep -c 'navi-bg:' /tmp/chain/launcher.log 2>/dev/null)
# The compositor's own protocol log is the only place that shows which client asked
# for a surface, so it is the measurement the navigation status rests on.
echo WESTON_CREATE_SURFACE=$($BB grep -c 'create_surface' /tmp/chain/weston.log 2>/dev/null)
echo WESTON_COMMITS=$($BB grep -c 'wl_surface@[0-9]*\\.commit' /tmp/chain/weston.log 2>/dev/null)
echo WESTON_REGISTRIES=$($BB grep -c 'get_registry' /tmp/chain/weston.log 2>/dev/null)
echo WESTON_SURFACE_TAIL=$($BB grep -E 'create_surface|wl_surface@[0-9]+\\.(attach|commit)' /tmp/chain/weston.log 2>/dev/null | $BB tail -n 6 | $BB tr '\n' '|')
echo OBSERVER_LATE_FILE=$($BB grep -c 'navi-bg:' /tmp/navi-bg.log 2>/dev/null)
$BB grep 'navi-bg:' /tmp/navi-bg.log 2>/dev/null | $BB tail -n 30
# AppNavi itself needs its EGL stack, which the recovered root does not carry, so
# the same observation is exercised here against a genuine vendor Wayland client:
# the hold forces the null attach this project cares about.
echo STAGE weston-log
$BB tail -n 20 /tmp/chain/weston.log 2>/dev/null
echo STAGE launcher-log
$BB tail -n 20 /tmp/chain/launcher.log 2>/dev/null
echo STAGE processes
$BB ps > /tmp/chain/processes.txt 2>/dev/null
$BB cat /tmp/chain/processes.txt
echo VENDOR_CHAIN_END
"""


class VendorError(RuntimeError):
    pass


def hardlink_or_copy(source: str, destination: str) -> str:
    """Keep the assembled tree cheap: hardlink files, copy when that is refused."""
    try:
        os.link(source, destination)
        return destination
    except OSError:
        return shutil.copy2(source, destination)


def overlay(source: Path, destination: Path) -> None:
    """Replace a placeholder directory from the base root with a real tree."""
    if not source.is_dir():
        raise VendorError(f"vendor tree is missing: {source}")
    if destination.is_symlink() or destination.is_file():
        destination.unlink()
    elif destination.is_dir():
        # The base root ships empty placeholders at these paths.
        shutil.rmtree(destination)
    shutil.copytree(source, destination, symlinks=True, copy_function=hardlink_or_copy)


def build_helpers(destination: Path, source: Path) -> dict[str, object]:
    """Cross-build the guest helpers for the vendor glibc floor.

    The vendor root is glibc 2.2x: a host-gcc build would need GLIBC_2.34 and
    would not load. zig supplies its own glibc and targets 2.25 explicitly.
    """
    zig = shutil.which("zig")
    prefix: list[str] = [zig] if zig else []
    if not zig:
        try:
            import ziglang  # noqa: F401
        except ImportError as exc:
            raise VendorError(
                "no guest toolchain: install zig (pip install --user ziglang) "
                "or pass --helpers with prebuilt guest binaries"
            ) from exc
        prefix = [sys.executable, "-m", "ziglang"]
    destination.mkdir(parents=True, exist_ok=True)
    common = prefix + ["cc", "-target", "x86_64-linux-gnu.2.25", "-O2",
                       "-Wall", "-Wextra", "-Werror"]
    commands = []
    for name, source_name in HELPER_BUILDS:
        commands.append(common + ["-shared", "-fPIC", "-o", str(destination / name),
                                  str(source / source_name), "-ldl"])
    for name, source_name in HELPER_PROGRAMS:
        commands.append(common + ["-o", str(destination / name),
                                  str(source / source_name), "-ldl"])
    for command in commands:
        built = subprocess.run(command, capture_output=True, text=True, check=False)
        if built.returncode != 0:
            raise VendorError("guest helper build failed: " + (built.stderr or "")[-800:])
    return {"toolchain": " ".join(prefix), "source": str(source),
            "binaries": list(HELPER_BINARIES)}


def assemble(tree_root: Path, new_gui: Path, navi: Path, helpers: Path | None,
             tree: Path) -> dict[str, object]:
    """Build the guest root: vendor root plus the two app trees and our helpers."""
    for name, path in (("root", tree_root), ("new_gui", new_gui), ("navi", navi)):
        if not path.is_dir():
            raise VendorError(f"missing local input {name}: {path}")
    shutil.copytree(tree_root, tree, symlinks=True, copy_function=hardlink_or_copy)
    overlay(new_gui, tree / "system/new_gui")
    overlay(navi, tree / "navi")
    if not (tree / "app/bin/AppLauncher").is_file():
        raise VendorError("AppLauncher is missing from the assembled root")
    if not (tree / "usr/lib/libwayland-client.so.0").exists():
        raise VendorError("the vendor Wayland client library is missing")
    binary = tree / "opt/vm"
    binary.mkdir(parents=True, exist_ok=True)
    toolchain = None
    wanted = HELPER_BINARIES
    prebuilt = helpers is not None and all((helpers / name).is_file() for name in wanted)
    if prebuilt:
        toolchain = {"toolchain": "prebuilt", "source": str(helpers)}
    else:
        toolchain = build_helpers(binary, HELPERS)
    for name in wanted:
        if prebuilt and not (binary / name).is_file():
            shutil.copyfile(helpers / name, binary / name)
        (binary / name).chmod(0o755)
    (tree / "opt/vm/vendor-chain.sh").write_text(CHAIN, encoding="utf-8")
    (tree / "opt/vm/vendor-chain.sh").chmod(0o755)
    (tree / "opt/vm/weston.ini").write_text(WESTON_INI, encoding="utf-8")
    (tree / "init").write_text(INIT, encoding="utf-8")
    (tree / "init").chmod(0o755)
    for name in ("proc", "sys", "dev", "tmp", "run/user/root", "rw_data/var/volatile/log",
                 "rw_data/var/volatile/tmp", "rw_data/dlt", "log_data"):
        (tree / name).mkdir(parents=True, exist_ok=True)
    (tree / "tmp").chmod(0o1777)
    return {"tree": str(tree), "chain": str(tree / "opt/vm/vendor-chain.sh"),
            "helpers": toolchain}


def build_image(tree: Path, image: Path, size_mib: int) -> list[str]:
    if size_mib <= 0 or size_mib & (size_mib - 1):
        raise VendorError(f"SD image size must be a power of two MiB, got {size_mib}")
    mkfs = vm_boot.find_mkfs()
    with image.open("xb") as handle:
        handle.truncate(size_mib * 1024**2)
    command = [mkfs, "-F", "-b", "4096", "-I", "256", "-O", vm_boot.EXT4_FEATURES,
               "-E", "lazy_itable_init=0,lazy_journal_init=0", "-d", str(tree), str(image)]
    with (image.parent / "mkfs.log").open("wb") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    return command


def prepare(container: Path, tree_root: Path, new_gui: Path, navi: Path,
            helpers: Path | None, workspace: Path, image_mib: int) -> Path:
    workspace = vm_boot.project_output(workspace)
    if workspace.exists():
        raise VendorError(f"workspace already exists, choose another path: {workspace}")
    image = vm_boot.extract_boot_image(container.read_bytes())
    if hashlib.sha256(image).hexdigest() != vm_boot.KERNEL_SHA256:
        raise VendorError("this harness supports only the measured EU 260128 kernel")
    workspace.mkdir(parents=True)
    (workspace / "bzImage").write_bytes(image)
    tree = workspace / "rootfs-tree"
    layout = assemble(tree_root, new_gui, navi, helpers, tree)
    command = build_image(tree, workspace / "rootfs.img", image_mib)
    manifest = bytearray(64)
    struct.pack_into("<II", manifest, 0, 0xe, 0x24)
    (workspace / "manifest.bin").write_bytes(manifest)
    for kind in ("dev", "user"):
        (workspace / f"seed_{kind}.bin").write_bytes(
            f"IONIQ-VM-ONLY-{kind}".encode().ljust(64, b"\0"))
    meta = {"schema": 1, "container": str(container.resolve()),
            "container_sha256": vm_boot.sha256(container),
            "mkfs_command": command, "synthetic_seeds": True,
            "vendor_tree": {"root": str(tree_root), "new_gui": str(new_gui),
                            "navi": str(navi), "chain": layout["chain"],
                            "helpers": layout["helpers"], "image_mib": image_mib},
            "sha256": {name: vm_boot.sha256(workspace / name) for name in vm_boot.ARTIFACTS}}
    (workspace / "prepare.json").write_text(json.dumps(meta, indent=2) + "\n")
    return workspace


# Directory trees copied into the image by refresh(): the software GL stack the
# chain loads for AppNavi, which is too large to rebuild the image for.
SYNC_TREES = ("opt/swrast",)

REFRESHED = ("init", "opt/vm/vendor-chain.sh", "opt/vm/weston.ini",
             "opt/vm/interpose-probe", "opt/vm/navi-bg-0x0.so",
             "opt/vm/launcher-appnavi-navibg.so", "opt/vm/guest-client-probe")


def refresh(workspace: Path, tree: Path | None = None) -> dict[str, object]:
    """Replace the harness-owned files inside an existing image.

    Rebuilding the 8 GiB image costs about ten minutes, and only these files ever
    change while the chain is tuned, so patch them in place with debugfs and keep
    the manifest honest.
    """
    import re

    workspace = vm_boot.project_output(workspace)
    tree = vm_boot.project_output(tree) if tree else workspace / "rootfs-tree"
    image = workspace / "rootfs.img"
    if not image.is_file():
        raise VendorError(f"no image to refresh: {image}")
    debugfs = shutil.which("debugfs") or "/usr/sbin/debugfs"
    for relative in REFRESHED:
        source = tree / relative
        if not source.is_file():
            raise VendorError(f"refreshed file is missing from the tree: {relative}")
        target = "/" + relative
        # debugfs tokenises its -R string on whitespace, and the project path
        # contains a space, so every path has to be quoted.
        subprocess.run([debugfs, "-w", "-R", f'rm "{target}"', str(image)],
                       capture_output=True, check=False)
        written = subprocess.run(
            [debugfs, "-w", "-R", f'write "{source}" "{target}"', str(image)],
            capture_output=True, text=True, check=False)
        stat = subprocess.run([debugfs, "-R", f'stat "{target}"', str(image)],
                              capture_output=True, text=True, check=False)
        if written.returncode != 0 or "File not found" in stat.stdout:
            raise VendorError(
                f"debugfs could not replace {relative}: "
                f"{(written.stdout + written.stderr)[-400:]}")
        inode = re.search(r"Inode:\s*(\d+)", stat.stdout)
        if inode:
            subprocess.run([debugfs, "-w", "-R", f"sif <{inode[1]}> mode 0100755",
                            str(image)], capture_output=True, check=False)
    for relative in SYNC_TREES:
        source_root = tree / relative
        if not source_root.is_dir():
            raise VendorError(f"synced tree is missing from the work tree: {relative}")
        # The tree root itself is not part of rglob("*"), and debugfs mkdir does not
        # create parents, so both are done explicitly, deepest last.
        subprocess.run([debugfs, "-w", "-R", f'mkdir "/{relative}"', str(image)],
                       capture_output=True, check=False)
        entries = sorted(source_root.rglob("*"),
                         key=lambda path: (len(path.relative_to(source_root).parts), str(path)))
        for entry in entries:
            target = "/" + str(entry.relative_to(tree))
            relative_target = str(entry.relative_to(source_root))
            # debugfs does not reliably create symlinks, and the guest only needs the
            # SONAME file to exist, so a link is materialised as a copy of its target
            # while the written name stays the link's own path.
            source_path = entry.resolve() if entry.is_symlink() else entry
            if source_path.is_dir():
                created = subprocess.run(
                    [debugfs, "-w", "-R", f'mkdir "{target}"', str(image)],
                    capture_output=True, text=True, check=False)
                if "File exists" in (created.stdout + created.stderr):
                    continue
                if created.returncode or "File not found" in (created.stdout + created.stderr):
                    raise VendorError(f"debugfs could not create {relative_target}: "
                                      f"{(created.stdout + created.stderr)[-300:]}")
                continue
            subprocess.run([debugfs, "-w", "-R", f'rm "{target}"', str(image)],
                           capture_output=True, check=False)
            written = subprocess.run(
                [debugfs, "-w", "-R", f'write "{source_path}" "{target}"', str(image)],
                capture_output=True, text=True, check=False)
            stat = subprocess.run([debugfs, "-R", f'stat "{target}"', str(image)],
                                  capture_output=True, text=True, check=False)
            if written.returncode != 0 or "Inode:" not in stat.stdout:
                raise VendorError(
                    f"debugfs could not write {relative_target}: "
                    f"{(written.stdout + stat.stdout + written.stderr + stat.stderr)[-300:]}")
            inode = re.search(r"Inode:\s*(\d+)", stat.stdout)
            mode = "0100755" if os.access(source_path, os.X_OK) else "0100644"
            if inode:
                subprocess.run([debugfs, "-w", "-R", f"sif <{inode[1]}> mode {mode}",
                                str(image)], capture_output=True, check=False)
    meta_path = workspace / "prepare.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["sha256"] = {name: vm_boot.sha256(workspace / name) for name in vm_boot.ARTIFACTS}
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    return {"workspace": str(workspace), "refreshed": list(REFRESHED),
            "synced": list(SYNC_TREES)}


SOFTWARE_GL_MARKER = "opt/vm/enable-software-gl"


def set_software_gl(workspace: Path, enabled: bool) -> dict[str, object]:
    """Toggle the experimental software-GL substitution inside the image."""
    workspace = vm_boot.project_output(workspace)
    image = workspace / "rootfs.img"
    if not image.is_file():
        raise VendorError(f"no image to toggle: {image}")
    debugfs = shutil.which("debugfs") or "/usr/sbin/debugfs"
    target = "/" + SOFTWARE_GL_MARKER
    subprocess.run([debugfs, "-w", "-R", f'rm "{target}"', str(image)],
                   capture_output=True, check=False)
    if enabled:
        marker = workspace / SOFTWARE_GL_MARKER
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("enabled\n", encoding="utf-8")
        written = subprocess.run(
            [debugfs, "-w", "-R", f'write "{marker}" "{target}"', str(image)],
            capture_output=True, text=True, check=False)
        stat = subprocess.run([debugfs, "-R", f'stat "{target}"', str(image)],
                              capture_output=True, text=True, check=False)
        if written.returncode != 0 or "Inode:" not in stat.stdout:
            raise VendorError("could not enable the software GL marker in the image")
        marker.unlink()
    return {"software_gl": enabled}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare", help="assemble and image the vendor root")
    prep.add_argument("--container", type=Path, required=True)
    prep.add_argument("--root", type=Path, default=DEFAULT_TREE_ROOT)
    prep.add_argument("--new-gui", type=Path, default=DEFAULT_NEW_GUI)
    prep.add_argument("--navi", type=Path, default=DEFAULT_NAVI)
    prep.add_argument("--helpers", type=Path, default=None,
                      help="directory with prebuilt guest helpers; omit to cross-build with zig")
    prep.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    prep.add_argument("--image-mib", type=int, default=DEFAULT_IMAGE_MIB)
    patched = sub.add_parser("refresh", help="patch the harness files inside an existing image")
    patched.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    patched.add_argument("--tree", type=Path, default=None)
    boot = sub.add_parser("run", help="boot the vendor workspace")
    boot.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    boot.add_argument("--cmd", default="/opt/vm/vendor-chain.sh")
    boot.add_argument("--timeout", type=float, default=180)
    boot.add_argument("--memory-mib", type=int, default=1536)
    boot.add_argument("--display", choices=vm_boot.DISPLAY_CHOICES, default="none",
                      help="none, a window (gtk/sdl/cocoa), or vnc on 127.0.0.1:0")
    boot.add_argument("--interactive", action="store_true",
                      help="forward your terminal into the guest shell")
    boot.add_argument("--software-gl", action="store_true",
                      help="experimental: bind the llvmpipe stack over the vendor EGL entry points")
    args = parser.parse_args(argv)
    try:
        if args.action == "prepare":
            print(prepare(args.container, args.root, args.new_gui, args.navi,
                          args.helpers, args.workspace, args.image_mib))
            return 0
        if args.action == "refresh":
            print(json.dumps(refresh(args.workspace, args.tree)))
            return 0
        set_software_gl(args.workspace, getattr(args, "software_gl", False))
        return vm_boot.run(args.workspace, True, args.cmd, args.timeout,
                           getattr(args, "interactive", False),
                           getattr(args, "display", "none"), False,
                           vm_boot.VM_CPU_CHOICES[0], False, args.memory_mib)
    except (OSError, ValueError, subprocess.SubprocessError, VendorError) as exc:
        print(f"vendor_rootfs: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
