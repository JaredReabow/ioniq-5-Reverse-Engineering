#!/usr/bin/env python3.13
"""stage-interval.py - stage the controlled run into a CoW clone and inject it.

Steps, in order, each failing loudly rather than continuing:

  1. verify the workspace is a clone, not the base projection (refuses to write the base image);
  2. generate the manifest from the REAL tracked bytes, recording in-guest paths;
  3. write the init script;
  4. inject the four files into p5.img with debugfs;
  5. sync only the changed 1 MiB chunks of p5 back into rootfs.img and refresh prepare.json.

Usage:
    python3.13 tools/uk_fw/vm_partimg/stage-interval.py --workspace work/vm/kbuild/ws-run61
    python3.13 tools/uk_fw/vm_partimg/stage-interval.py --workspace ... --check   # verify only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
DRIVER = PROJECT / "tools/uk_fw/guest/interval-run.sh"
HELPER = PROJECT / "tools/uk_fw/guest/interval-capture.sh"
MANIFEST_TOOL = PROJECT / "tools/uk_fw/make_run_manifest.py"
SYNC_TOOL = PROJECT / "tools/uk_fw/vm_partimg/sync-partition.py"

# The base projection. Staging must never write here: it is the reference the clone is compared to.
BASE_WORKSPACE = (PROJECT / "work/vm/kbuild/ws").resolve()

GUEST_DRIVER = "/interval-run.sh"
GUEST_HELPER = "/interval-capture.sh"
GUEST_MANIFEST = "/interval-manifest.txt"
GUEST_INIT = "/init-interval-run.sh"

# PROJECTION-ONLY runtime libraries. The staged swrast_dri.so needs these, and the vendor image has
# them only in /opt/software-egl18/lib, which AppLauncher.sh discards when it overwrites
# LD_LIBRARY_PATH (docs/kernel/46). Placing them in /usr/lib puts them where the vendor libEGL already
# searches, and touches no vendor file.
#
# Provenance: both are third-party ELF shared objects already used by this projection. The host
# candidates below are the existing staged copies; the guest path is the vendor search path.
EXTRA_LIBS = (
    ("libsensors.so.4", "/usr/lib/libsensors.so.4", (
        PROJECT / "work/vm/kbuild/ws/inject-new/stage/libsensors.so.4",
        PROJECT / "work/vm/kbuild/ws/inject/egl-lib/libsensors.so.4",
    )),
    ("libLLVM-6.0.so.1", "/usr/lib/libLLVM-6.0.so.1", (
        PROJECT / "work/vm/kbuild/ws/inject/egl-lib/libLLVM-6.0.so.1",
    )),
    # Transitive dependencies. libLLVM needs libedit; libedit needs libbsd. Both exist only under
    # /opt/software-egl18/lib, so the same trap applies one and two levels down. libedit's other
    # dependency (libncurses.so.5) is already on the vendor path, so it is not listed.
    ("libedit.so.2", "/usr/lib/libedit.so.2", (
        PROJECT / "work/vm/kbuild/ws/inject-new/stage/libedit.so.2",
    )),
    ("libbsd.so.0", "/usr/lib/libbsd.so.0", (
        PROJECT / "work/vm/kbuild/ws/inject-new/stage/libbsd.so.0",
    )),
)


def resolve_extra_libs() -> list[tuple[Path, str]]:
    """Return (host_path, guest_path) pairs, failing loudly if a library cannot be located."""
    found: list[tuple[Path, str]] = []
    missing: list[str] = []
    for name, guest, candidates in EXTRA_LIBS:
        for candidate in candidates:
            if candidate.is_file():
                found.append((candidate, guest))
                break
        else:
            missing.append(name)
    if missing:
        raise FileNotFoundError(
            "projection runtime libraries not found: " + ", ".join(missing)
            + " (see docs/kernel/46 for why they are needed)"
        )
    return found

INIT_TEMPLATE = """#!/bin/sh
# PROJECTION-ONLY init for the controlled interval run (docs/vm/59-controlled-run-spec.md).
#
# Launches the RETAINED driver in the background, then hands control to the authentic esinit so the
# vendor boot proceeds normally. The driver waits for the compositor socket itself, so nothing here
# depends on timing.
#
# Two channels: the driver reports to ttyS2 (vendor getty, prefixed lines are fine) and
# hands the helper ttyS3, which is pristine so the receipt transaction is uncontaminated.
( {driver} --manifest {manifest} --helper {helper} \\
    --log /tmp/weston-real.log --out /dev/ttyS2 --export-out /dev/ttyS3 ) &
exec /lib/systemd/esinit
"""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_debugfs() -> str | None:
    found = shutil.which("debugfs")
    if found:
        return found
    candidate = Path("/opt/homebrew/opt/e2fsprogs/sbin/debugfs")
    return str(candidate) if candidate.is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True, type=Path)
    ap.add_argument("--run-id", default="interval-r1")
    ap.add_argument("--check", action="store_true", help="verify the stage inputs only; do not inject")
    args = ap.parse_args()

    ws = args.workspace
    if not ws.is_absolute():
        ws = (PROJECT / ws).resolve()
    if ws == BASE_WORKSPACE:
        print(f"error: refusing to stage into the base workspace {BASE_WORKSPACE}", file=sys.stderr)
        print("       create a clone first: cp -c <base>/{bzImage,rootfs.img,...} <clone>/", file=sys.stderr)
        return 2
    for name in ("rootfs.img", "bzImage", "prepare.json"):
        if not (ws / name).is_file():
            print(f"error: workspace missing {name}: {ws}", file=sys.stderr)
            return 2
    p5 = ws / "partimg-build" / "p5.img"
    if not p5.is_file():
        print(f"error: workspace missing partimg-build/p5.img: {ws}", file=sys.stderr)
        return 2

    for path in (DRIVER, HELPER, MANIFEST_TOOL, SYNC_TOOL):
        if not path.is_file():
            print(f"error: required tracked file missing: {path}", file=sys.stderr)
            return 2

    print(f"workspace      {ws}")
    print(f"driver         {DRIVER}  sha256={sha256_of(DRIVER)}")
    print(f"helper         {HELPER}  sha256={sha256_of(HELPER)}")

    if args.check:
        print("check only: inputs present, nothing injected")
        return 0

    stage = ws / "interval-stage"
    if stage.is_dir():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # 1. Manifest from the real bytes, naming in-guest paths.
    manifest = stage / "interval-manifest.txt"
    rc = subprocess.run(
        [sys.executable, str(MANIFEST_TOOL), "--run-id", args.run_id,
         "--driver", str(DRIVER), "--helper", str(HELPER),
         "--driver-guest-path", GUEST_DRIVER, "--helper-guest-path", GUEST_HELPER,
         "--output", str(manifest)],
        capture_output=True, text=True,
    )
    if rc.returncode != 0:
        print(f"error: manifest generation failed: {rc.stderr}", file=sys.stderr)
        return 3
    print("manifest:")
    for line in manifest.read_text(encoding="utf-8").splitlines():
        print(f"  {line}")

    # 2. Copies plus the init script, named without spaces because debugfs splits its command string.
    shutil.copyfile(DRIVER, stage / "interval-run.sh")
    shutil.copyfile(HELPER, stage / "interval-capture.sh")
    (stage / "init-interval-run.sh").write_text(
        INIT_TEMPLATE.format(driver=GUEST_DRIVER, manifest=GUEST_MANIFEST, helper=GUEST_HELPER),
        encoding="utf-8",
    )
    # Projection-only runtime libraries, copied into the stage with space-free names.
    try:
        extras = resolve_extra_libs()
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    lib_cmds = []
    for index, (host_lib, guest_lib) in enumerate(extras):
        local = f"extra-lib-{index}.so"
        shutil.copyfile(host_lib, stage / local)
        print(f"extra lib      {host_lib.name} -> {guest_lib}  sha256={sha256_of(host_lib)}")
        lib_cmds.append((local, guest_lib))

    # The staged bytes must equal the tracked bytes, or the manifest would describe something else.
    for staged, source in (("interval-run.sh", DRIVER), ("interval-capture.sh", HELPER)):
        if sha256_of(stage / staged) != sha256_of(source):
            print(f"error: staged {staged} does not match {source}", file=sys.stderr)
            return 3
    print("staged bytes match the tracked sources")

    debugfs = find_debugfs()
    if not debugfs:
        print("error: debugfs not found (install e2fsprogs)", file=sys.stderr)
        return 3

    cmds = stage / "debugfs.cmds"
    cmds.write_text(
        "\n".join(
            [
                f"rm {GUEST_DRIVER}",
                f"write interval-run.sh {GUEST_DRIVER}",
                f"set_inode_field {GUEST_DRIVER} mode 0100755",
                f"rm {GUEST_HELPER}",
                f"write interval-capture.sh {GUEST_HELPER}",
                f"set_inode_field {GUEST_HELPER} mode 0100755",
                f"rm {GUEST_MANIFEST}",
                f"write interval-manifest.txt {GUEST_MANIFEST}",
                f"rm {GUEST_INIT}",
                f"write init-interval-run.sh {GUEST_INIT}",
                f"set_inode_field {GUEST_INIT} mode 0100755",
            ]
            + [f"rm {guest_lib}" for _, guest_lib in lib_cmds]
            + [f"write {local} {guest_lib}" for local, guest_lib in lib_cmds]
            + [f"set_inode_field {guest_lib} mode 0100755" for _, guest_lib in lib_cmds]
            + [""]
        ),
        encoding="utf-8",
    )

    print("=== debugfs write into p5.img ===")
    written = subprocess.run([debugfs, "-w", "-f", str(cmds), str(p5)], cwd=str(stage), capture_output=True, text=True)
    if written.returncode != 0:
        print(f"error: debugfs failed rc={written.returncode}\n{written.stderr}", file=sys.stderr)
        return 4

    print("=== verify staged files in p5.img ===")
    for path in (GUEST_DRIVER, GUEST_HELPER, GUEST_MANIFEST, GUEST_INIT) + tuple(
        guest_lib for _, guest_lib in lib_cmds
    ):
        stat = subprocess.run([debugfs, "-R", f"stat {path}", str(p5)], capture_output=True, text=True)
        ok = "Inode:" in stat.stdout
        print(f"  {'OK ' if ok else 'MISSING'} {path}")
        if not ok:
            return 4

    print("=== sync changed chunks back into rootfs.img ===")
    sync = subprocess.run(
        [sys.executable, str(SYNC_TOOL), str(ws), "5"],
        capture_output=True, text=True,
    )
    if sync.returncode != 0:
        print(f"error: sync-partition failed rc={sync.returncode}\n{sync.stderr}", file=sys.stderr)
        return 5
    print((sync.stdout or "").strip()[-600:])

    meta = json.loads((ws / "prepare.json").read_text())
    root_sha = meta.get("sha256", {}).get("rootfs.img")
    actual = sha256_of(ws / "rootfs.img")
    print(f"prepare.json rootfs sha256 {'refreshed' if root_sha == actual else 'STALE'} ({actual[:16]}…)")
    print("staged successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
