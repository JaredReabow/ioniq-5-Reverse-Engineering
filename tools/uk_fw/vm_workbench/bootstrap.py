"""Plan and run the local Gen5W launcher without elevating the VM service."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
from urllib.request import urlopen

_HOST = "gen5w.local"
_IP = "127.0.0.1"
_DEFAULT_PORT = 8765
_HOSTS = Path("/etc/hosts")
_HOSTS_LINE = b"127.0.0.1 gen5w.local # Gen5W Workbench\n"
_PROJECT = Path(__file__).resolve().parents[3]
_ZIG_VERSION = "0.13.0"
_ZIG_DOWNLOADS = {
    ("macos", "x86_64"): (48857012, "8b06ed1091b2269b700b3b07f8e3be3b833000841bae5aa6a09b1a8b4773effd"),
    ("macos", "aarch64"): (44892040, "46fae219656545dfaf4dce12fb4e8685cec5b51d721beee9389ab4194d43394c"),
    ("linux", "x86_64"): (47082308, "d45312e61ebcc48032b77bc4cf7fd6915c11fa16e4aad116b66c9468211230ea"),
    ("linux", "aarch64"): (43090688, "041ac42323837eb5624068acd8b00cd5777dac4cf91179e8dad7a7e90dd0c556"),
}


class BootstrapError(RuntimeError):
    """A setup step cannot continue."""


@dataclass(frozen=True)
class BootstrapStep:
    """One visible action and its explicit side effects."""

    key: str
    description: str
    weight: int
    argv: tuple[str, ...] = ()
    destination: Path | None = None
    confirm: bool = False
    elevated: bool = False


@dataclass(frozen=True)
class BootstrapPlan:
    """An ordered plan with no filesystem or process side effects."""

    steps: tuple[BootstrapStep, ...]
    package_manager: str | None
    state_dir: Path
    assets: Path
    notes: tuple[str, ...]


def bootstrap_package_manager(family, *, which=shutil.which):
    """Identify an available package manager on the supported host."""
    managers = {
        "macos": (("brew", "brew"),),
        "linux": (("apt", "apt-get"), ("dnf", "dnf"), ("pacman", "pacman")),
        "wsl2": (("apt", "apt-get"), ("dnf", "dnf"), ("pacman", "pacman")),
    }
    if family not in managers:
        raise BootstrapError("Use the Windows launcher for WSL2, or run natively on macOS or Linux.")
    for name, command in managers[family]:
        executable = which(command)
        if executable:
            return name, executable
    return None


def bootstrap_plan(*, family, state_dir, assets, manager, packages=(),
                   zig_target=None, configure_hostname=False, wifi_sim=False,
                   python=sys.executable, sudo=None, assume_yes=False, extra_notes=()):
    """Describe setup commands and local files before applying any changes."""
    if family not in ("macos", "linux", "wsl2"):
        raise BootstrapError("Supported backends are macOS, Linux and Windows through WSL2.")
    if configure_hostname and family == "wsl2":
        raise BootstrapError("Set up gen5w.local in the Windows launcher, which checks the Windows hosts file.")
    state_dir = Path(state_dir)
    venv = state_dir / ".venv"
    steps = []
    manager_name = manager[0] if manager else None
    if packages:
        if manager is None:
            raise BootstrapError("No supported package manager found. See docs/gen5w-vm-server.md.")
        name, executable = manager
        formats = {"brew": ("install",), "apt": ("install",),
                   "dnf": ("install",), "pacman": ("-S", "--needed")}
        if name not in formats or (name != "brew" and not sudo):
            raise BootstrapError("Package setup requires a supported package manager and sudo on Linux.")
        needs_sudo = name != "brew"
        # --yes is explicit consent, not an authentication bypass. A remote
        # caller must have cached sudo credentials; otherwise sudo -n fails.
        prefix = ((sudo, "-n") if assume_yes else (sudo,)) if needs_sudo else ()
        consent = {"brew": (), "apt": ("-y",), "dnf": ("-y",),
                   "pacman": ("--noconfirm",)}[name] if assume_yes else ()
        if name == "apt":
            steps.append(BootstrapStep("update", "Refresh APT package indexes", 1,
                                       prefix + (executable, "update"), confirm=True, elevated=True))
        steps.append(BootstrapStep("packages", "Install missing system dependencies", 3,
                                   prefix + (executable,) + formats[name] + consent + tuple(packages),
                                   confirm=True, elevated=needs_sudo))
    if zig_target:
        url, target, size, digest = zig_target
        steps.append(BootstrapStep("zig", f"Download and verify Zig {_ZIG_VERSION} ({size:,} bytes, SHA-256 {digest})",
                                   2, (url,), target))
    steps.append(BootstrapStep("venv", "Create or reuse the local Python environment (standard library only)", 1,
                               (python, "-I", "-m", "venv", "--without-pip", str(venv)), venv))
    if configure_hostname:
        host_command = ((sudo, "-n", "/usr/bin/tee", "-a", str(_HOSTS)) if assume_yes else
                        (sudo, "/usr/bin/tee", "-a", str(_HOSTS))) if sudo else ()
        steps.append(BootstrapStep("hostname", "Offer a local-only gen5w.local hosts entry", 1,
                                   host_command,
                                   _HOSTS, confirm=True, elevated=True))
    steps.append(BootstrapStep("server", "Select a loopback URL and start the server in this terminal", 2,
                               (str(venv / "bin/python"), "-s", "-B", "-m", "vm_workbench",
                                "--server", "--assets", str(assets)) + (("--wifi-sim",) if wifi_sim else ())))
    return BootstrapPlan(tuple(steps), manager_name, state_dir, Path(assets), (
        "Ctrl+C stops the foreground service. Keep this terminal open while using the VM.",
        "A browser Stop VM action shuts down the guest. The server prints its final state.",
        "To undo an optional hosts edit, remove only the exact Gen5W Workbench entry added during setup.",
        "System packages remain under your package manager. Project-local tools and logs are under the state directory.",
    ) + tuple(extra_notes))


def bootstrap_hosts_mapping(contents: bytes) -> str:
    """Return missing, loopback, or conflict for exact hosts-file aliases."""
    mappings = set()
    for line in contents.decode("utf-8", errors="replace").splitlines():
        address, *aliases = line.partition("#")[0].split() or ("",)
        if any(alias.rstrip(".").casefold() == _HOST for alias in aliases):
            mappings.add(address)
    if not mappings:
        return "missing"
    return "loopback" if mappings <= {_IP, "::1"} else "conflict"


def _hosts_mapping(path=_HOSTS):
    with path.open("rb") as stream:
        contents = stream.read(1024 * 1024 + 1)
    if len(contents) > 1024 * 1024:
        raise BootstrapError("The hosts file exceeds the launcher inspection limit.")
    return bootstrap_hosts_mapping(contents)


def _verify_alias(resolve=socket.getaddrinfo):
    try:
        addresses = {record[4][0] for record in resolve(_HOST, None, type=socket.SOCK_STREAM)}
    except OSError:
        return False
    # The listener is IPv4-only. Accept an additional IPv6 loopback address,
    # while retaining numeric IPv4 fallback for an IPv6-only alias.
    return _IP in addresses and addresses <= {_IP, "::1"}


def _bound_port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind((_IP, port))
    except OSError:
        return False
    return True


def bootstrap_address(requested_port, alias_verified, *, fallback_port=_DEFAULT_PORT,
                      available=_bound_port_available):
    """Return the effective port, verified alias, and a fallback explanation."""
    if type(requested_port) is not int or not 1 <= requested_port <= 65535:
        raise BootstrapError("Port must be an integer from 1 to 65535.")
    if type(fallback_port) is not int or not 1024 <= fallback_port <= 65535:
        raise BootstrapError("The fallback port must be unprivileged.")
    host = _HOST if alias_verified else None
    if requested_port == 80 and not alias_verified:
        return (fallback_port if available(fallback_port) else 0), host, (
            "gen5w.local is unavailable. Using an unprivileged numeric loopback URL.")
    if available(requested_port):
        return requested_port, host, None if host else "gen5w.local is unavailable. Using numeric loopback."
    fallback = fallback_port if requested_port != fallback_port and available(fallback_port) else 0
    description = f"Loopback port {fallback}" if fallback else "An available loopback port"
    return fallback, host, f"Port {requested_port} is busy or needs privileges. {description} will be used."


def _zig_target(config):
    system = "macos" if config.family == "macos" else "linux"
    arch = {"arm64": "aarch64", "amd64": "x86_64"}.get(config.architecture, config.architecture)
    entry = _ZIG_DOWNLOADS.get((system, arch))
    if entry is None:
        raise BootstrapError("The host architecture has no pinned Zig download. See docs/gen5w-vm-server.md.")
    name = f"zig-{system}-{arch}-{_ZIG_VERSION}"
    return (f"https://ziglang.org/download/{_ZIG_VERSION}/{name}.tar.xz",
            config.cache_dir / name, *entry)


def _cached_zig(record):
    _, destination, _, expected_hash = record
    marker, binary = destination / "release.sha256", destination / "zig"
    if destination.is_symlink() or marker.is_symlink() or binary.is_symlink():
        return None
    if not binary.is_file() or not os.access(binary, os.X_OK) or not (destination / "lib").is_dir():
        return None
    try:
        with marker.open("rb") as stream:
            receipt = stream.read(66)
    except FileNotFoundError:
        return None
    return binary if receipt == expected_hash.encode("ascii") + b"\n" else None


def _progress(complete, total, label, started):
    cells = 20 * complete // total
    print(f"[{'#' * cells}{'-' * (20 - cells)}] {100 * complete // total:3}%  "
          f"{time.monotonic() - started:6.1f}s  {label}", flush=True)


def _download_zig(record, *, download=urlopen):
    url, destination, length, expected_hash = record
    if destination.is_symlink() or destination.exists():
        raise BootstrapError(f"Zig setup destination already exists: {destination}")
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".zig-", dir=destination.parent) as staging:
        archive = Path(staging) / "release.tar.xz"
        sha = hashlib.sha256()
        received = 0
        next_update = 0
        with download(url, timeout=45) as response, archive.open("xb") as stream:
            if response.geturl() != url:
                raise BootstrapError("Unexpected Zig download redirect.")
            started = time.monotonic()
            while data := response.read(1024 * 1024):
                received += len(data)
                if received > length:
                    raise BootstrapError("The Zig download exceeded its pinned size.")
                sha.update(data)
                stream.write(data)
                if received >= next_update or received == length:
                    _progress(received, length, "Downloading Zig", started)
                    next_update += max(1, length // 10)
        if received != length or sha.hexdigest() != expected_hash:
            raise BootstrapError("Zig download size or SHA-256 did not match the pinned release.")
        unpacked = Path(staging) / "unpacked"
        unpacked.mkdir(mode=0o700)
        with tarfile.open(archive, mode="r:xz") as payload:
            for index, member in enumerate(payload):
                path = PurePosixPath(member.name)
                if (index >= 100_000 or path.is_absolute() or not path.parts
                        or path.parts[0] != destination.name or ".." in path.parts):
                    raise BootstrapError("Unexpected path in the pinned Zig archive.")
                output = unpacked.joinpath(*path.parts)
                if member.isdir():
                    output.mkdir(mode=0o755, parents=True, exist_ok=True)
                elif member.isfile():
                    output.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
                    with payload.extractfile(member) as source, output.open("xb") as target:
                        shutil.copyfileobj(source, target, 1024 * 1024)
                    output.chmod(0o755 if member.mode & 0o111 else 0o644)
                else:
                    raise BootstrapError("Only directories and regular files are admitted in the Zig archive.")
        build = unpacked / destination.name
        if not (build / "zig").is_file() or not (build / "lib").is_dir():
            raise BootstrapError("The Zig archive is missing its tool or standard library.")
        with (build / "release.sha256").open("x", encoding="ascii") as marker:
            marker.write(expected_hash + "\n")
        build.rename(destination)
    return destination / "zig"


def _print_plan(plan, out=print):
    out("Gen5W local server setup")
    out(f"  Assets: {plan.assets}")
    out(f"  State and setup logs: {plan.state_dir}")
    out(f"  Package manager: {plan.package_manager or 'none needed or available'}")
    for index, step in enumerate(plan.steps, 1):
        elevated = " (uses administrator permission)" if step.elevated else ""
        out(f"  {index}. {step.description}{elevated}")
        if step.argv:
            out(f"     {shlex.join(step.argv)}")
        if step.destination:
            out(f"     Writes: {step.destination}")
    for sentence in plan.notes:
        out(f"  {sentence}")


def _ask(message):
    try:
        return sys.stdin.isatty() and input(message + " [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def _command(argv, log, *, runner=subprocess.run, **kwargs):
    command = shlex.join(argv)
    print(f"> {command}", flush=True)
    started = time.monotonic()
    log.write(f"> {command}\n")
    log.flush()
    try:
        result = runner(argv, check=False, **kwargs)
        status = result.returncode
    except (OSError, KeyboardInterrupt) as error:
        log.write(f"  {type(error).__name__} after {time.monotonic() - started:.2f}s\n")
        log.flush()
        raise
    line = f"  Exit {status} in {time.monotonic() - started:.2f}s"
    print(line, flush=True)
    log.write(line + "\n")
    log.flush()
    if status:
        raise BootstrapError(f"Command stopped with exit {status}. Review the output above.")


def _configured_alias(family, windows_alias):
    if family == "wsl2":
        return windows_alias
    try:
        return _hosts_mapping() == "loopback" and _verify_alias()
    except (BootstrapError, OSError):
        return False


def _ensure_venv(step, log, *, runner):
    venv = step.destination
    executable = venv / "bin/python"
    if venv.is_symlink():
        raise BootstrapError("The local Python environment must be a directory owned by this project.")
    if executable.is_file() and (venv / "pyvenv.cfg").is_file():
        _command((str(executable), "-I", "-c", "import sys; assert sys.version_info >= (3, 10)"),
                 log, runner=runner)
        return
    if venv.exists():
        raise BootstrapError(f"Local Python environment is incomplete. Move {venv} aside and relaunch.")
    _command(step.argv, log, runner=runner)


def bootstrap_apply(plan, *, config, zig_target=None, cached_zig=None, port=_DEFAULT_PORT,
                    fallback_port=_DEFAULT_PORT, windows_alias=False, open_browser=True, ask=_ask,
                    runner=subprocess.run, discover=None, missing=None, assume_yes=False):
    """Apply a displayed plan. Only package installs and optional hosts entry use sudo."""
    _print_plan(plan)
    if (any(step.key == "packages" for step in plan.steps) and not assume_yes
            and not ask("Install the listed system packages?")):
        raise BootstrapError("System dependency setup was declined.")
    plan.state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    log_root = plan.state_dir / "logs"
    if log_root.is_symlink():
        raise BootstrapError("The setup log directory must not be a symbolic link.")
    log_root.mkdir(mode=0o700, exist_ok=True)
    descriptor, filename = tempfile.mkstemp(dir=log_root, prefix="bootstrap-", suffix=".log", text=True)
    print(f"Setup log: {filename}", flush=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(_PROJECT / "tools/uk_fw")
    env["GEN5W_STATE_DIR"] = str(plan.state_dir)
    if cached_zig is not None:
        env["GEN5W_ZIG"] = str(cached_zig)
    total = sum(step.weight for step in plan.steps)
    complete = 0
    started = time.monotonic()
    with os.fdopen(descriptor, "w", encoding="utf-8") as log:
        _print_plan(plan, lambda value: log.write(value + "\n"))
        if cached_zig is not None:
            message = f"Reusing the cached Zig {_ZIG_VERSION} installation at {cached_zig}."
            print(message, flush=True)
            log.write(message + "\n")
        for step in plan.steps:
            _progress(complete, total, step.description, started)
            if step.key == "zig":
                env["GEN5W_ZIG"] = str(_download_zig(zig_target))
                log.write(f"Verified Zig and installed it at {env['GEN5W_ZIG']}\n")
            elif step.key == "venv":
                _ensure_venv(step, log, runner=runner)
            elif step.key == "hostname":
                mapping = _hosts_mapping()
                if mapping == "conflict":
                    print("Hosts file has a conflicting gen5w.local entry. Leaving it in place.", flush=True)
                elif mapping == "missing" and step.argv:
                    print(_HOSTS_LINE.decode("ascii").rstrip(), flush=True)
                    if assume_yes or ask("Append the displayed Gen5W entry to the hosts file?"):
                        if _hosts_mapping() != "missing":
                            raise BootstrapError("The hosts file changed during setup. Review its entries and relaunch.")
                        _command(step.argv, log, runner=runner, input=b"\n" + _HOSTS_LINE,
                                 stdout=subprocess.DEVNULL)
            elif step.key == "server":
                if discover is not None and missing is not None:
                    missing_tools = missing(discover(env))
                    if missing_tools:
                        raise BootstrapError("Required tools are still missing: " + ", ".join(missing_tools))
                alias_verified = _configured_alias(config.family, windows_alias)
                selected, host, explanation = bootstrap_address(port, alias_verified, fallback_port=fallback_port)
                if explanation:
                    print(explanation, flush=True)
                    log.write(explanation + "\n")
                argv = step.argv + ("--port", str(selected))
                if host:
                    argv += ("--host-name", host)
                if open_browser:
                    argv += ("--open-browser",)
                complete += step.weight
                _progress(complete, total, "Setup complete. Starting the browser service and VM.", started)
                _command(argv, log, runner=runner, cwd=_PROJECT, env=env)
                return
            else:
                _command(step.argv, log, runner=runner, env=env)
            complete += step.weight
            _progress(complete, total, f"Finished: {step.description}", started)


def bootstrap_main(argv=None):
    """Command-line entry point shared by the three visible launchers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=_PROJECT / ".gen5w/assets",
                        help="local asset directory containing gen5w-assets.json")
    parser.add_argument("--plan", action="store_true", help="show the setup plan without applying it")
    parser.add_argument("--yes", action="store_true",
                        help="accept displayed setup actions; sudo must already be authorized")
    parser.add_argument("--no-pause", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--port", type=int, default=_DEFAULT_PORT, help="preferred loopback port")
    parser.add_argument("--setup-hostname", action="store_true", help="offer to add a loopback hosts alias")
    parser.add_argument("--windows-alias", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--windows-fallback-port", type=int, default=_DEFAULT_PORT, help=argparse.SUPPRESS)
    parser.add_argument("--no-browser", action="store_true", help="print the URL without opening it")
    parser.add_argument("--wifi-sim", action="store_true", help="enable available local Wi-Fi simulation assets")
    parser.add_argument("--print-asset-manifest", action="store_true", help="print the supported asset manifest JSON")
    args = parser.parse_args(argv)
    try:
        if args.print_asset_manifest:
            from .assets import assets_manifest
            print(json.dumps(assets_manifest(wifi_sim=args.wifi_sim), indent=2))
            return 0
        from .platform_config import (platform_config_dependency_packages, platform_config_discover,
                                      platform_config_missing, platform_config_virtualization_notes)

        if sys.version_info < (3, 10):
            raise BootstrapError("Python 3.10 or newer is required.")
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            raise BootstrapError("Launch as your regular user. In WSL, finish Ubuntu's first-run account setup.")
        if not 1 <= args.port <= 65535:
            raise BootstrapError("Port must be an integer from 1 to 65535.")
        config = platform_config_discover(_PROJECT)
        if config.family == "wsl2" and "GEN5W_STATE_DIR" not in os.environ:
            # Keep Unix sockets and POSIX permissions on WSL's Linux filesystem.
            install_id = hashlib.sha256(os.fsencode(_PROJECT)).hexdigest()[:16]
            state = (Path.home() / ".gen5w" / install_id).resolve()
            config = platform_config_discover(_PROJECT, environment={**os.environ, "GEN5W_STATE_DIR": str(state)})
        if (args.windows_alias or args.windows_fallback_port != _DEFAULT_PORT) and config.family != "wsl2":
            raise BootstrapError("Windows browser setup flags require WSL2.")
        if not 1024 <= args.windows_fallback_port <= 65535:
            raise BootstrapError("The Windows fallback port must be unprivileged.")
        assets = args.assets.expanduser().absolute()
        if not args.plan and not (assets / "gen5w-assets.json").is_file():
            raise BootstrapError(f"Missing {assets / 'gen5w-assets.json'}. See docs/gen5w-vm-server.md.")
        manager = bootstrap_package_manager(config.family)
        missing = platform_config_missing(config, wifi_sim=args.wifi_sim)
        system_missing = set(missing) - {"zig"}
        packages = (platform_config_dependency_packages(config, manager[0], wifi_sim=args.wifi_sim)
                    if manager and system_missing else ())
        if importlib.util.find_spec("venv") is None and manager and manager[0] == "apt":
            packages = tuple(dict.fromkeys((*packages, "python3-venv")))
        if system_missing and not packages:
            raise BootstrapError("No installation recipe for missing tools: " + ", ".join(sorted(system_missing)))
        zig_target = _zig_target(config) if "zig" in missing else None
        cached_zig = _cached_zig(zig_target) if zig_target else None
        if cached_zig is not None:
            zig_target = None
        plan = bootstrap_plan(family=config.family, state_dir=config.state_dir, assets=assets,
                              manager=manager, packages=packages, zig_target=zig_target,
                              configure_hostname=args.setup_hostname, wifi_sim=args.wifi_sim,
                              sudo=shutil.which("sudo"), assume_yes=args.yes,
                              extra_notes=platform_config_virtualization_notes(config))
        if args.plan:
            _print_plan(plan)
            if cached_zig is not None:
                print(f"  Reuse cached Zig {_ZIG_VERSION} at {cached_zig}.")
            return 0
        bootstrap_apply(plan, config=config, zig_target=zig_target, port=args.port,
                        cached_zig=cached_zig,
                        fallback_port=args.windows_fallback_port,
                        windows_alias=args.windows_alias, open_browser=not args.no_browser,
                        assume_yes=args.yes,
                        discover=lambda env: platform_config_discover(_PROJECT, environment=env),
                        missing=lambda host: platform_config_missing(host, wifi_sim=args.wifi_sim))
        return 0
    except KeyboardInterrupt:
        print("\nGen5W setup or server stopped.", file=sys.stderr)
        return 130
    except (BootstrapError, ValueError, OSError, tarfile.TarError) as error:
        print(f"Gen5W setup stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(bootstrap_main())
