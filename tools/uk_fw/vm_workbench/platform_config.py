"""Discover host tools and local storage for the public Gen5W VM launcher."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import platform
import re
import shutil
import sys
from typing import Mapping


class PlatformConfigError(ValueError):
    """The current host or its configured state directory is unsupported."""


@dataclass(frozen=True)
class HostConfig:
    """Resolved host tool paths. An absent executable or header is None."""

    family: str
    architecture: str
    state_dir: Path
    cache_dir: Path
    runtime_dir: Path
    python: Path | None
    qemu: Path | None
    qemu_img: Path | None
    debugfs: Path | None
    shell: Path | None
    zig: Path | None
    dbus_inc: Path | None
    dbus_arch_inc: Path | None
    file_tool: Path | None
    musl_cc: Path | None
    magick: Path | None
    distro: str = ""


def platform_config_virtualization_notes(config: HostConfig, *, kvm=Path("/dev/kvm"),
                                         access=os.access) -> tuple[str, ...]:
    """Describe the actual launcher accelerator and optional nested KVM access.

    The retained vendor guest always uses QEMU TCG. KVM availability therefore
    informs host setup only, and never promises acceleration for this guest.
    """
    notes = ["The Gen5W x86 guest uses QEMU TCG software emulation; this launcher does not select KVM."]
    if config.family == "wsl2":
        if not kvm.exists():
            notes.append("WSL2 preflight: /dev/kvm is absent. Nested virtualization is not exposed to this distribution.")
        elif not access(kvm, os.R_OK | os.W_OK):
            notes.append("WSL2 preflight: /dev/kvm exists but this Linux user cannot read and write it.")
        else:
            notes.append("WSL2 preflight: /dev/kvm is accessible; KVM VM creation has not been tested.")
        notes.append("Optional nested KVM setup uses [wsl2] nestedVirtualization=true in your Windows .wslconfig; review existing settings before editing. A distribution restart may be needed.")
    if config.architecture != "x86_64":
        notes.append("ARM64 host virtualization cannot accelerate the x86 Gen5W guest.")
    return tuple(notes)


_NORMAL_TOOLS = ("python", "qemu", "qemu_img", "debugfs", "shell", "zig", "dbus_inc",
                 "dbus_arch_inc", "file_tool")
_SIM_TOOLS = ("musl_cc", "magick")
_WSL2_RELEASE = re.compile(r"(?:microsoft-standard|microsoft.*wsl2|wsl2.*microsoft)",
                           re.IGNORECASE)
_ARCHITECTURES = {"amd64": "x86_64", "x86_64": "x86_64", "arm64": "aarch64",
                  "aarch64": "aarch64"}
_MULTIARCH = {"x86_64": "x86_64-linux-gnu", "aarch64": "aarch64-linux-gnu"}
_PACKAGES = {
    "brew": (
        ("python", "python"), ("qemu", "qemu"), ("qemu_img", "qemu"),
        ("debugfs", "e2fsprogs"), ("dbus_inc", "dbus"), ("dbus_arch_inc", "dbus"),
        ("magick", "imagemagick"),
    ),
    "apt": (
        ("python", "python3"), ("qemu", "qemu-system-x86"),
        ("qemu_img", "qemu-utils"), ("debugfs", "e2fsprogs"), ("shell", "dash"),
        ("file_tool", "file"), ("dbus_inc", "libdbus-1-dev"),
        ("dbus_arch_inc", "libdbus-1-dev"), ("musl_cc", "musl-tools"),
        ("magick", "imagemagick"),
    ),
    "dnf": (
        ("python", "python3"), ("qemu", "qemu-system-x86-core"),
        ("qemu_img", "qemu-img"), ("debugfs", "e2fsprogs"), ("shell", "bash"),
        ("file_tool", "file"), ("dbus_inc", "dbus-devel"),
        ("dbus_arch_inc", "dbus-devel"), ("magick", "ImageMagick"),
    ),
    "pacman": (
        ("python", "python"), ("qemu", "qemu-system-x86"), ("qemu_img", "qemu-img"),
        ("debugfs", "e2fsprogs"), ("shell", "bash"), ("file_tool", "file"),
        ("dbus_inc", "dbus"), ("dbus_arch_inc", "dbus"), ("magick", "imagemagick"),
    ),
}


def _family(system: str, release: str, environment: Mapping[str, str]) -> str:
    if system == "Darwin":
        return "macos"
    if system == "Windows":
        raise PlatformConfigError("Native Windows needs the Gen5W WSL2 launcher")
    if system != "Linux":
        raise PlatformConfigError("Gen5W requires macOS, Linux, or Windows WSL2")
    if _WSL2_RELEASE.search(release):
        return "wsl2"
    if "microsoft" in release.lower() or environment.get("WSL_INTEROP"):
        raise PlatformConfigError("Gen5W requires a WSL2 kernel")
    return "linux"


def _absolute(value: str | os.PathLike | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else None


def _qemu_state_path(project: Path, environment: Mapping[str, str]) -> Path:
    state_override = environment.get("GEN5W_STATE_DIR")
    state = _absolute(state_override) if state_override is not None else project / ".gen5w"
    if state is None:
        raise PlatformConfigError("GEN5W_STATE_DIR must be an absolute path")
    try:
        resolved = state.resolve()
    except (OSError, RuntimeError):
        raise PlatformConfigError("Gen5W state directory cannot be resolved") from None
    if resolved != state:
        raise PlatformConfigError("Gen5W state directory must be canonical and contain no symlinks")
    # QEMU's key-value device options embed the workspace as one argument.
    if any(character in str(resolved) for character in ",\r\n"):
        raise PlatformConfigError("Gen5W state directory cannot contain commas or line breaks")
    return resolved


def _executable(*candidates: Path | None) -> Path | None:
    for candidate in candidates:
        if candidate is not None and candidate.is_file() and os.access(candidate, os.X_OK):
            # Keep the invocation name for venv launchers and toolchain shims.
            return candidate
    return None


def _header(include_dirs: tuple[Path, ...], filename: str) -> Path | None:
    return next((path.resolve() for path in include_dirs if (path / filename).is_file()), None)


def _distribution() -> str:
    try:
        return platform.freedesktop_os_release().get("ID", "")
    except (OSError, AttributeError):
        return ""


def platform_config_discover(project: Path, *, environment: Mapping[str, str] | None = None,
                             system: str | None = None, release: str | None = None,
                             machine: str | None = None) -> HostConfig:
    """Discover dependencies with filesystem checks and return a read-only plan."""
    environment = os.environ if environment is None else environment
    family = _family(system or platform.system(), release or platform.release(), environment)
    architecture = _ARCHITECTURES.get((machine or platform.machine()).lower())
    if architecture is None:
        raise PlatformConfigError("Gen5W requires an x86-64 or ARM64 host")
    try:
        project = Path(project).resolve(strict=True)
    except (OSError, RuntimeError):
        raise PlatformConfigError("Gen5W project directory is unavailable") from None
    if not project.is_dir():
        raise PlatformConfigError("Gen5W project directory is unavailable")
    state = _qemu_state_path(project, environment)
    # Keep relative and empty PATH entries out of discovery. The launcher must
    # use an explicit project cache location for locally provisioned tools.
    path = os.pathsep.join(filter(os.path.isabs, environment.get("PATH", "").split(os.pathsep)))
    search_path = path or os.pathsep.join(("/usr/bin", "/bin", "/usr/sbin", "/sbin"))
    local_bin = state / "cache" / "bin"

    def tool(name: str, *fallbacks: Path, override: str | None = None) -> Path | None:
        if override is not None and override in environment:
            explicit = _absolute(environment[override])
            if explicit is None:
                raise PlatformConfigError(override + " must be an absolute executable path")
            return _executable(explicit)
        return _executable(local_bin / name, _absolute(shutil.which(name, path=search_path)), *fallbacks)

    if family == "macos":
        brew_prefixes = (_absolute(environment.get("HOMEBREW_PREFIX")), Path("/opt/homebrew"),
                         Path("/usr/local"))
        package_dirs = tuple(prefix for prefix in brew_prefixes if prefix is not None)
        debugfs_fallbacks = tuple(prefix / "opt/e2fsprogs/sbin/debugfs" for prefix in package_dirs)
        includes = tuple(prefix / "include/dbus-1.0" for prefix in package_dirs)
        arch_includes = tuple(prefix / "lib/dbus-1.0/include" for prefix in package_dirs)
        distro = ""
    else:
        package_dirs = (Path("/usr/local"), Path("/usr"))
        debugfs_fallbacks = (Path("/usr/sbin/debugfs"), Path("/sbin/debugfs"))
        includes = tuple(prefix / "include/dbus-1.0" for prefix in package_dirs)
        arch_includes = tuple(prefix / libdir / "dbus-1.0/include" for prefix in package_dirs
                              for libdir in ("lib/" + _MULTIARCH[architecture], "lib64", "lib"))
        distro = _distribution()
    header_override = _absolute(environment.get("GEN5W_DBUS_INC"))
    arch_override = _absolute(environment.get("GEN5W_DBUS_ARCH_INC"))
    for name, resolved in (("GEN5W_DBUS_INC", header_override),
                           ("GEN5W_DBUS_ARCH_INC", arch_override)):
        if name in environment and resolved is None:
            raise PlatformConfigError(name + " must be an absolute header directory")
    bin_dirs = tuple(prefix / "bin" for prefix in package_dirs)
    musl_cc = tool("x86_64-linux-musl-gcc", override="GEN5W_MUSL_CC")
    if musl_cc is None and "GEN5W_MUSL_CC" not in environment and family != "macos" and architecture == "x86_64":
        musl_cc = tool("musl-gcc")
    return HostConfig(
        family=family, architecture=architecture, state_dir=state,
        cache_dir=state / "cache", runtime_dir=state / "runtime",
        python=_executable(_absolute(sys.executable)) or tool("python3"),
        qemu=tool("qemu-system-x86_64", *(directory / "qemu-system-x86_64" for directory in bin_dirs),
                  override="GEN5W_QEMU"),
        qemu_img=tool("qemu-img", *(directory / "qemu-img" for directory in bin_dirs)),
        debugfs=tool("debugfs", *debugfs_fallbacks, override="GEN5W_DEBUGFS"),
        shell=tool("sh", Path("/bin/sh")),
        zig=tool("zig", *(directory / "zig" for directory in bin_dirs), override="GEN5W_ZIG"),
        dbus_inc=_header((header_override,) if header_override else includes, "dbus/dbus.h"),
        dbus_arch_inc=_header((arch_override,) if arch_override else arch_includes,
                              "dbus/dbus-arch-deps.h"),
        file_tool=tool("file", Path("/usr/bin/file")),
        musl_cc=musl_cc,
        # ImageMagick 6 packages (for example Ubuntu 24.04) expose convert.
        magick=(tool("magick", *(directory / "magick" for directory in bin_dirs))
                or tool("convert-im6.q16", *(directory / "convert-im6.q16" for directory in bin_dirs))),
        distro=distro,
    )


def platform_config_missing(config: HostConfig, *, wifi_sim: bool = False) -> tuple[str, ...]:
    """List missing normal startup tools and optional Wi-Fi simulator tools."""
    names = _NORMAL_TOOLS + (_SIM_TOOLS if wifi_sim else ())
    return tuple(name for name in names if getattr(config, name) is None)


def platform_config_require(config: HostConfig, *, wifi_sim: bool = False) -> None:
    """Reject incomplete setup with stable tool names suitable for the launcher."""
    missing = platform_config_missing(config, wifi_sim=wifi_sim)
    if missing:
        raise PlatformConfigError("Missing Gen5W dependencies: " + ", ".join(missing))


def platform_config_dependency_packages(config: HostConfig, manager: str,
                                        *, wifi_sim: bool = False) -> tuple[str, ...]:
    """Return deduplicated package names for missing tools provided by a manager."""
    if manager not in _PACKAGES or (manager == "brew") != (config.family == "macos"):
        raise PlatformConfigError("Unsupported package manager for this Gen5W host")
    missing = set(platform_config_missing(config, wifi_sim=wifi_sim))
    packages = (package for tool, package in _PACKAGES[manager] if tool in missing and
                (tool != "musl_cc" or config.architecture == "x86_64"))
    return tuple(dict.fromkeys(packages))
