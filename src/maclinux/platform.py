"""Linux distribution/platform detection and version-aware build environment metadata."""

from __future__ import annotations

import os
import platform as py_platform
import shutil
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class PlatformInfo:
    distribution: str
    version: str
    codename: str
    id_like: tuple[str, ...]
    ecosystem: str
    package_manager: str
    architecture: str
    kernel: str
    kernel_tree: str
    compiler: str
    build_tools: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def read_os_release(path: str = "/etc/os-release") -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                values[key] = value.strip().strip('"')
    except OSError:
        pass
    return values


def normalize_distribution(value: str) -> str:
    value = (value or "unknown").lower()
    aliases = {
        "linuxmint": "ubuntu",
        "pop": "ubuntu",
        "pop_os": "ubuntu",
        "altlinux": "altlinux",
        "rhel": "rhel",
        "centos": "centos-stream",
        "rocky": "rocky",
        "almalinux": "almalinux",
        "opensuse-tumbleweed": "opensuse",
        "opensuse-leap": "opensuse",
        "manjaro": "manjaro",
    }
    return aliases.get(value, value)


def package_backend(distribution: str, values: dict[str, str]) -> tuple[str, str]:
    distro = normalize_distribution(distribution)
    if distro in {"debian", "ubuntu", "mint"} or "debian" in values.get("ID_LIKE", ""):
        return "deb", "apt-get"
    if distro == "altlinux":
        return "rpm", "apt-get"
    if distro in {"fedora", "rhel", "rocky", "almalinux", "centos-stream"}:
        return "rpm", "dnf"
    if distro in {"arch", "manjaro", "endeavouros"}:
        return "arch", "pacman"
    if distro == "opensuse":
        return "rpm", "zypper"
    if distro == "alpine":
        return "apk", "apk"
    if distro == "gentoo":
        return "ebuild", "emerge"
    return "generic", "unknown"


def detect_platform(os_release: dict[str, str] | None = None) -> PlatformInfo:
    values = os_release or read_os_release()
    distribution = normalize_distribution(values.get("ID", "unknown"))
    ecosystem, manager = package_backend(distribution, values)
    kernel = py_platform.release()
    tree = f"/lib/modules/{kernel}/build"
    tools = tuple(x for x in ("make", "gcc", "clang", "ld", "pkg-config", "dkms") if shutil.which(x))
    compiler = "gcc" if shutil.which("gcc") else ("clang" if shutil.which("clang") else "unknown")
    return PlatformInfo(
        distribution=distribution,
        version=values.get("VERSION_ID", ""),
        codename=values.get("VERSION_CODENAME", values.get("UBUNTU_CODENAME", "")),
        id_like=tuple(values.get("ID_LIKE", "").split()),
        ecosystem=ecosystem,
        package_manager=manager if shutil.which(manager) else "unknown",
        architecture=py_platform.machine(),
        kernel=kernel,
        kernel_tree=tree if os.path.isdir(tree) else "",
        compiler=compiler,
        build_tools=tools,
    )


def platform_supported(info: PlatformInfo) -> bool:
    return info.distribution != "unknown" and info.version != ""
