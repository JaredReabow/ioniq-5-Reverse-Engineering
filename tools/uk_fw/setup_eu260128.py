#!/usr/bin/env python3
"""Prepare EU 260128 inputs and a minimal kernel shell in one command.

The default workflow is offline after package acquisition. ``--setup-qemu`` may
fetch Ubuntu Jammy packages into the ignored project workspace without installing
anything system-wide. No vendor payload is executed or modified; the resulting
shell is not the full authentic HMI runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Any

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import gen5w_decrypt  # noqa: E402  (sibling modules, resolved above)
import ver_manifest  # noqa: E402
import vm_boot  # noqa: E402

PACKAGE_ID = "IONIQ5_EU"
SOFTWARE_VERSION = "NE_E.EUR.S5W_L.001.001.260128"
MODEL_CODE = "101489"
DEFAULT_PACKAGE = PROJECT / "work/firmware/IONIQ5_EU"
DEFAULT_WORKSPACE = PROJECT / "work/decrypted-eu-260128"
DEFAULT_BOOT_WORKSPACE = PROJECT / "work/vm/bootable-eu260128"
DEFAULT_QEMU_INSTALL = PROJECT / "work/tools/qemu"
QEMU_APT_PACKAGES = (
    "qemu-system-x86", "qemu-system-common", "qemu-system-data",
    "libaio1", "libfdt1", "libibverbs1", "libpmem1", "librdmacm1",
    "libslirp0", "liburing2", "libndctl6", "libdaxctl1", "libnl-route-3-200",
    "seabios", "ipxe-qemu", "ipxe-qemu-256k-compat-efi-roms",
)
ARCHIVES = (
    ("HU/images/mango-rootfs.tar.gz", "mango-rootfs"),
    ("HU/images/mango-rwdata.tar.gz", "mango-rwdata"),
    ("HU/images/new_gui.tar.gz", "new_gui"),
    ("HU/images/navi_eu/appnavi.tar", "appnavi"),
    ("HU/firmware/update.tar.gz", "update"),
)


class SetupError(RuntimeError):
    """Raised when local package preparation must stop without guessing."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def package_check(package: Path) -> tuple[dict[str, Any], str]:
    manifest_path = package / f"{PACKAGE_ID}.ver"
    if not manifest_path.is_file():
        raise SetupError(f"package manifest not found: {manifest_path}")
    parsed = ver_manifest.parse(manifest_path)
    identity = parsed["package"]
    expected = {
        "version": SOFTWARE_VERSION,
        "package_id": PACKAGE_ID,
        "model_code": MODEL_CODE,
    }
    if any(identity.get(key) != value for key, value in expected.items()):
        raise SetupError(f"unexpected EU package identity: {identity}")
    result = ver_manifest.verify(parsed, package, skip_over=0, include_all=True)
    summary = result["summary"]
    if summary["mismatch"] or summary["missing"] or summary["ok"] != 35:
        raise SetupError(f"package verification failed: {summary}")
    return {"identity": identity, "summary": summary}, sha256(manifest_path)


def member_path(name: str) -> tuple[str, ...] | None:
    if "\x00" in name or "\\" in name:
        raise SetupError(f"unsupported archive path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute():
        raise SetupError(f"absolute archive member path: {name!r}")
    parts = tuple(part for part in path.parts if part not in ("", "."))
    if any(part == ".." for part in parts):
        raise SetupError(f"archive member escapes destination: {name!r}")
    if parts and ":" in parts[0]:
        raise SetupError(f"drive-qualified archive path: {name!r}")
    return parts or None


def link_target(link_path: tuple[str, ...], target: str, *, hardlink: bool) -> tuple[str, ...]:
    if "\x00" in target or "\\" in target:
        raise SetupError(f"unsupported archive link target: {target!r}")
    parsed = PurePosixPath(target)
    if hardlink and parsed.is_absolute():
        raise SetupError(f"absolute hardlink target: {target!r}")
    parts = [] if hardlink or parsed.is_absolute() else list(link_path[:-1])
    for part in parsed.parts:
        if part in ("", ".", "/"):
            continue
        if part == "..":
            if not parts:
                raise SetupError(f"archive link escapes destination: {target!r}")
            parts.pop()
        else:
            parts.append(part)
    return tuple(parts)


def ensure_directory(root: Path, parts: tuple[str, ...]) -> Path:
    current = root
    for part in parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if current.is_symlink() or not current.is_dir():
                raise SetupError(f"archive path crosses a non-directory: {current}")
        else:
            current.mkdir(mode=0o755)
    return current


def safe_extract_tar(archive: Path, destination: Path) -> dict[str, int]:
    """Extract regular files first; rebase guest-root symlinks inside destination."""
    destination.mkdir(parents=True, exist_ok=False)
    root = destination.resolve()
    types: dict[str, str] = {}
    links: list[tuple[tuple[str, ...], str, bool]] = []
    files = directories = symlinks = hardlinks = total_bytes = 0

    with tarfile.open(archive, "r:*") as stream:
        for member in stream:
            parts = member_path(member.name)
            if parts is None:
                continue
            key = "/".join(parts)
            kind = (
                "dir" if member.isdir() else
                "file" if member.isfile() else
                "symlink" if member.issym() else
                "hardlink" if member.islnk() else
                "unsupported"
            )
            previous = types.get(key)
            if previous is not None:
                if previous == kind == "dir":
                    continue
                raise SetupError(f"duplicate/conflicting archive member: {member.name}")
            if kind == "unsupported":
                raise SetupError(f"unsupported special archive member: {member.name}")
            types[key] = kind

            if kind == "dir":
                directory = ensure_directory(root, parts)
                os.chmod(directory, member.mode & 0o777)
                directories += 1
            elif kind in ("symlink", "hardlink"):
                links.append((parts, member.linkname, kind == "hardlink"))
            else:
                parent = ensure_directory(root, parts[:-1])
                target = parent / parts[-1]
                if target.exists() or target.is_symlink():
                    raise SetupError(f"archive file collides with an existing path: {member.name}")
                source = stream.extractfile(member)
                if source is None:
                    raise SetupError(f"cannot read archive member: {member.name}")
                with source, target.open("xb") as output:
                    while True:
                        block = source.read(1 << 20)
                        if not block:
                            break
                        output.write(block)
                        total_bytes += len(block)
                os.chmod(target, member.mode & 0o777)
                files += 1

    link_keys = {"/".join(parts) for parts, _, _ in links}
    for key in types:
        path = PurePosixPath(key)
        for parent in path.parents:
            parent_key = parent.as_posix()
            if parent_key in link_keys:
                raise SetupError(f"archive member is nested under a link: {key}")

    pending_hardlinks = []
    for parts, target_name, is_hardlink in links:
        parent = ensure_directory(root, parts[:-1])
        destination_path = parent / parts[-1]
        if destination_path.exists() or destination_path.is_symlink():
            raise SetupError(f"archive link collides with an existing path: {'/'.join(parts)}")
        target_parts = link_target(parts, target_name, hardlink=is_hardlink)
        source_path = root.joinpath(*target_parts)
        if is_hardlink:
            pending_hardlinks.append((destination_path, source_path, parts))
            continue
        relative_target = os.path.relpath(source_path, parent)
        os.symlink(relative_target, destination_path)
        symlinks += 1

    for destination_path, source_path, parts in pending_hardlinks:
        if source_path.is_symlink() or not source_path.is_file():
            raise SetupError(f"hardlink target is not a regular file: {'/'.join(parts)}")
        os.link(source_path, destination_path, follow_symlinks=False)
        hardlinks += 1

    return {
        "files": files,
        "directories": directories,
        "symlinks": symlinks,
        "hardlinks": hardlinks,
        "bytes": total_bytes,
        "ownership_preserved": False,
    }


def decrypt_and_extract(package: Path, workspace: Path, package_info: dict[str, Any],
                        manifest_sha256: str) -> dict[str, Any]:
    raw_root = workspace / "decrypted"
    extracted_root = workspace / "extracted-safe"
    decrypted = {}
    for relative in gen5w_decrypt.DEFAULT_FILES:
        source = package / relative
        target = raw_root / relative
        if not source.is_file():
            raise SetupError(f"TE2 input missing: {source}")
        result = gen5w_decrypt.decrypt_native(source, target)
        decrypted[relative] = {
            "output": target.relative_to(workspace).as_posix(),
            "bytes": result["bytes_written"],
            "sha256": sha256(target),
        }

    extracted = {}
    for relative, directory in ARCHIVES:
        source = raw_root / relative
        target = extracted_root / directory
        extracted[relative] = safe_extract_tar(source, target)

    required = (
        extracted_root / "mango-rootfs/app/bin/ApplicationManager",
        extracted_root / "appnavi/Bin/AppNavi",
        extracted_root / "new_gui/system/new_gui",
    )
    missing = [str(path.relative_to(workspace)) for path in required if not path.exists()]
    if missing:
        raise SetupError("expected vendor files not found after extraction: " + ", ".join(missing))

    return {
        "package": package_info,
        "manifest_sha256": manifest_sha256,
        "decrypted": decrypted,
        "extracted": extracted,
        "analysis_tree": "extracted-safe",
        "rootfs_ownership_preserved": False,
    }


def boot_workspace_status(package: Path, path: Path, busybox: Path | None,
                          no_boot: bool) -> dict[str, Any]:
    if no_boot:
        return {"status": "skipped", "reason": "--no-boot requested"}
    if busybox is None or not busybox.is_file():
        return {"status": "skipped", "reason": "static BusyBox not found"}
    container = package / "HU/images/iasImage_1280_sub"
    if not container.is_file():
        return {"status": "skipped", "reason": "iasImage_1280_sub missing"}
    if path.exists():
        meta_path = path / "prepare.json"
        if not meta_path.is_file():
            return {"status": "conflict", "reason": f"workspace exists without {meta_path.name}"}
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if (meta.get("container_sha256") == vm_boot.sha256(container)
                and meta.get("busybox_sha256") == vm_boot.sha256(busybox)):
            return {"status": "reused", "workspace": str(path)}
        return {"status": "conflict", "reason": "existing boot workspace inputs differ"}
    try:
        vm_boot.prepare(container, busybox, path)
    except (OSError, ValueError, vm_boot.subprocess.SubprocessError) as exc:
        return {"status": "failed", "reason": str(exc)}
    return {"status": "prepared", "workspace": str(path)}


def write_report(workspace: Path, report: dict[str, Any]) -> None:
    temp = workspace / "setup.json.tmp"
    temp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(workspace / "setup.json")


def setup_qemu_local(destination: Path) -> dict[str, Any]:
    """Download and unpack Jammy QEMU packages without installing system-wide."""
    system_qemu = shutil.which("qemu-system-x86_64")
    if system_qemu:
        version = subprocess.run([system_qemu, "--version"], capture_output=True,
                                 text=True, timeout=30, check=False)
        return {"status": "system", "path": system_qemu,
                "version": version.stdout.splitlines()[0] if version.stdout else "unknown"}
    if not sys.platform.startswith("linux") or os.uname().machine != "x86_64":
        raise SetupError("local QEMU bootstrap supports Linux x86_64 only")
    apt_get = shutil.which("apt-get")
    dpkg_deb = shutil.which("dpkg-deb")
    if not apt_get or not dpkg_deb:
        raise SetupError("apt-get and dpkg-deb are required for local QEMU bootstrap")
    release = {}
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                release[key] = value.strip().strip('"')
    except OSError as exc:
        raise SetupError(f"cannot identify the Linux package source: {exc}") from exc
    if release.get("ID") != "ubuntu" or release.get("VERSION_CODENAME") != "jammy":
        raise SetupError("local QEMU package bootstrap is pinned to Ubuntu 22.04 (jammy) x86_64")

    destination = vm_boot.project_output(destination)
    wrapper_path = destination / "bin/qemu-system-x86_64"
    if destination.exists():
        if wrapper_path.is_file() and os.access(wrapper_path, os.X_OK):
            probe = subprocess.run([str(wrapper_path), "-machine", "help"],
                                   capture_output=True, text=True, timeout=30, check=False)
            if probe.returncode == 0 and "q35" in probe.stdout:
                version = subprocess.run([str(wrapper_path), "--version"],
                                         capture_output=True, text=True, timeout=30, check=False)
                return {"status": "local-reused", "path": str(wrapper_path),
                        "version": version.stdout.splitlines()[0] if version.stdout else "unknown"}
        raise SetupError(f"local QEMU directory already exists but is not usable: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".qemu-eu260128-", dir=destination.parent))
    try:
        deb_dir = stage / "debs"
        root = stage / "root"
        deb_dir.mkdir()
        root.mkdir()
        downloaded = subprocess.run(
            [apt_get, "download", *QEMU_APT_PACKAGES], cwd=deb_dir,
            capture_output=True, text=True, timeout=900, check=False,
        )
        if downloaded.returncode != 0:
            detail = (downloaded.stderr or downloaded.stdout)[-1500:]
            raise SetupError(f"apt-get download failed: {detail}")
        debs = sorted(deb_dir.glob("*.deb"))
        if not debs:
            raise SetupError("apt-get did not download any QEMU packages")
        for deb in debs:
            extracted = subprocess.run(
                [dpkg_deb, "-x", str(deb), str(root)],
                capture_output=True, text=True, timeout=120, check=False,
            )
            if extracted.returncode != 0:
                raise SetupError(f"dpkg-deb failed for {deb.name}: {extracted.stderr[-1000:]}")

        qemu_binary = root / "usr/bin/qemu-system-x86_64"
        qemu_share = root / "usr/share/qemu"
        seabios_share = root / "usr/share/seabios"
        module_dir = root / "usr/lib/x86_64-linux-gnu/qemu"
        if not qemu_binary.is_file() or not qemu_share.is_dir() or not module_dir.is_dir():
            raise SetupError("downloaded QEMU package set is incomplete")
        for bios in seabios_share.glob("*.bin"):
            link = qemu_share / bios.name
            if not link.exists() and not link.is_symlink():
                os.symlink(os.path.relpath(bios, qemu_share), link)

        wrapper_dir = stage / "bin"
        wrapper_dir.mkdir()
        wrapper = wrapper_dir / "qemu-system-x86_64"
        wrapper.write_text(
            """#!/bin/sh
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/../root" && pwd)
export LD_LIBRARY_PATH="$root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export QEMU_MODULE_DIR="$root/usr/lib/x86_64-linux-gnu/qemu"
exec "$root/usr/bin/qemu-system-x86_64" -L "$root/usr/share/qemu" "$@"
""",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        environment = {**os.environ, "LD_LIBRARY_PATH": str(root / "usr/lib/x86_64-linux-gnu"),
                       "QEMU_MODULE_DIR": str(module_dir)}
        probe = subprocess.run([str(wrapper), "-machine", "help"], env=environment,
                               capture_output=True, text=True, timeout=30, check=False)
        if probe.returncode != 0 or "q35" not in probe.stdout:
            raise SetupError(f"local QEMU smoke check failed: {probe.stderr[-1200:]}")
        version = subprocess.run([str(wrapper), "--version"], env=environment,
                                 capture_output=True, text=True, timeout=30, check=False)
        if version.returncode != 0 or not version.stdout:
            raise SetupError(f"local QEMU version probe failed: {version.stderr[-1200:]}")
        (stage / "packages.json").write_text(json.dumps({"packages": [p.name for p in debs]},
                                                        indent=2) + "\\n", encoding="utf-8")
        stage.rename(destination)
        return {"status": "local-installed", "path": str(destination / "bin/qemu-system-x86_64"),
                "version": version.stdout.splitlines()[0], "packages": len(debs)}
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def run_boot_test(boot_workspace: Path, qemu_path: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["PATH"] = str(Path(qemu_path).parent) + os.pathsep + env.get("PATH", "")
    command = [
        sys.executable,
        str(HERE / "vm_boot.py"),
        "run",
        "--workspace",
        str(boot_workspace),
        "--sdhci-compat",
        "--timeout",
        "60",
    ]
    result = subprocess.run(command, cwd=PROJECT, env=env, capture_output=True,
                            text=True, timeout=180, check=False)
    run_dir = next((line.split(": ", 1)[1] for line in result.stdout.splitlines()
                    if line.startswith("Run artifacts: ")), None)
    log_path = (Path(run_dir) / "setup-boot-test.log" if run_dir
                else boot_workspace / "setup-boot-test.log")
    log_path.write_text(result.stdout + "\nBOOT_TEST_STDERR\n" + result.stderr,
                        encoding="utf-8")
    return {
        "status": "passed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "run_directory": run_dir,
        "log": str(log_path),
    }


def setup(package: Path, workspace: Path, boot_workspace: Path,
          busybox: Path | None, no_boot: bool, setup_qemu: bool,
          boot_test: bool) -> dict[str, Any]:
    package = package.resolve()
    workspace = vm_boot.project_output(workspace)
    boot_workspace = vm_boot.project_output(boot_workspace)
    package_info, manifest_sha = package_check(package)

    if workspace.exists():
        report_path = workspace / "setup.json"
        if not report_path.is_file():
            raise SetupError(f"workspace exists without setup.json; choose another path: {workspace}")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("manifest_sha256") != manifest_sha:
            raise SetupError("existing setup workspace belongs to a different package manifest")
    else:
        workspace.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=".setup-eu260128-", dir=workspace.parent))
        try:
            report = decrypt_and_extract(package, stage, package_info, manifest_sha)
            report["boot_workspace"] = {"status": "pending"}
            report["qemu_available"] = shutil.which("qemu-system-x86_64") is not None
            report["full_hmi_chain_reconstructed"] = False
            report["limitations"] = [
                "Extracted trees preserve data but not original file ownership.",
                "The boot workspace is a minimal serial shell, not the authentic HMI.",
                "Original run images, generated helpers, logs and full launcher adaptations are not recreated.",
            ]
            write_report(stage, report)
            if workspace.exists():
                raise SetupError(f"workspace appeared during setup: {workspace}")
            stage.rename(workspace)
        except BaseException:
            shutil.rmtree(stage, ignore_errors=True)
            raise

    report["boot_workspace"] = boot_workspace_status(
        package, boot_workspace, busybox, no_boot
    )
    qemu_info = (
        setup_qemu_local(DEFAULT_QEMU_INSTALL)
        if setup_qemu or boot_test
        else ({"status": "system", "path": shutil.which("qemu-system-x86_64")}
              if shutil.which("qemu-system-x86_64")
              else {"status": "missing", "path": None})
    )
    report["qemu"] = qemu_info
    report["qemu_available"] = bool(qemu_info.get("path"))
    report["boot_test"] = {"status": "not-requested"}
    if boot_test:
        if report["boot_workspace"]["status"] not in ("prepared", "reused"):
            report["boot_test"] = {"status": "blocked", "reason": "boot workspace is not ready"}
        elif not qemu_info.get("path"):
            report["boot_test"] = {"status": "blocked", "reason": "QEMU is unavailable"}
        else:
            report["boot_test"] = run_boot_test(boot_workspace, qemu_info["path"])
    report["full_hmi_chain_reconstructed"] = False
    write_report(workspace, report)
    return report


def render(report: dict[str, Any], workspace: Path) -> None:
    summary = report["package"]["summary"]
    boot = report["boot_workspace"]
    qemu = report["qemu"]
    boot_test = report["boot_test"]
    print(f"EU260128_SETUP_READY package={SOFTWARE_VERSION} files={summary['ok']}/{summary['total']}")
    print(f"analysis_tree={workspace / 'extracted-safe'}")
    print(f"boot_workspace={boot['status']}" + (f" path={boot['workspace']}" if boot.get("workspace") else ""))
    print(f"qemu={qemu['status']}" + (f" path={qemu['path']}" if qemu.get("path") else ""))
    print(f"boot_test={boot_test['status']}")
    print("full_hmi_chain_reconstructed=false")
    if boot.get("reason"):
        print(f"note={boot['reason']}")
    if qemu.get("reason"):
        print(f"qemu_note={qemu['reason']}")
    if boot_test.get("log"):
        print(f"boot_test_log={boot_test['log']}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument("--boot-workspace", type=Path, default=DEFAULT_BOOT_WORKSPACE)
    parser.add_argument("--busybox", type=Path)
    parser.add_argument("--no-boot", action="store_true")
    parser.add_argument("--setup-qemu", action="store_true",
                        help="download Ubuntu Jammy QEMU packages into ignored work/tools/ without root")
    parser.add_argument("--boot-test", action="store_true",
                        help="set up QEMU if needed and run the minimal kernel shell test")
    args = parser.parse_args(argv)
    if args.no_boot and args.boot_test:
        parser.error("--boot-test cannot be combined with --no-boot")
    busybox = args.busybox
    if busybox is None:
        busybox = Path(shutil.which("busybox")) if shutil.which("busybox") else None
    try:
        report = setup(args.package, args.workspace, args.boot_workspace, busybox,
                       args.no_boot, args.setup_qemu, args.boot_test)
    except (OSError, SetupError, tarfile.TarError, gen5w_decrypt.DecryptError,
            subprocess.SubprocessError, ValueError, json.JSONDecodeError) as exc:
        print(f"setup_eu260128: {exc}", file=sys.stderr)
        return 2
    render(report, vm_boot.project_output(args.workspace))
    if report["boot_test"]["status"] == "failed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
