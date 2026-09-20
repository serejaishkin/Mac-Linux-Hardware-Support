"""Kernel build-tree and ABI metadata detection."""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class KernelInfo:
    release: str
    version: str
    architecture: str
    build_tree: str
    headers_present: bool
    config_present: bool
    modules_symvers_present: bool
    compiler: str
    localversion: str
    vermagic: str
    config: dict[str, str]
    compiler_id: str
    symvers: dict[str, tuple[str, str, str, str]]

    def to_dict(self) -> dict:
        return asdict(self)


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().strip()
    except OSError:
        return ""


def _compiler_id(tree: str) -> str:
    text = _read(f"{tree}/include/generated/compile.h")
    match = re.search(r'LINUX_COMPILER\\s+"([^"]+)"', text)
    return match.group(1).strip() if match else ""


def _symvers(tree: str) -> dict[str, tuple[str, str, str, str]]:
    path = f"{tree}/Module.symvers"
    if not os.path.isfile(path):
        return {}
    values = {}
    for line in _read(path).splitlines():
        fields = line.split()
        if len(fields) >= 4:
            crc, symbol, module, export = fields[:4]
            namespace = fields[4] if len(fields) >= 5 else ""
            values[symbol] = (crc, module, export, namespace)
    return values


def _module_vermagic() -> str:
    modinfo = shutil.which("modinfo")
    if not modinfo:
        return ""
    try:
        p = subprocess.run([modinfo, "-F", "vermagic", "kernel"], text=True,
                           capture_output=True, check=False, shell=False)
        return p.stdout.strip() if p.returncode == 0 else ""
    except OSError:
        return ""


def _kernel_config(tree: str, release: str) -> dict[str, str]:
    candidates = (f"{tree}/.config", f"/boot/config-{release}")
    path = next((p for p in candidates if os.path.isfile(p)), "")
    if not path:
        return {}
    values: dict[str, str] = {}
    for line in _read(path).splitlines():
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value.strip()
        elif line.startswith("# CONFIG_") and line.endswith(" is not set"):
            key = line[2:-len(" is not set")].strip()
            values[key] = "n"
    return values


def detect_kernel(build_tree: str | None = None) -> KernelInfo:
    release = platform.release()
    tree = build_tree or f"/lib/modules/{release}/build"
    config = f"/boot/config-{release}"
    makefile = _read(f"{tree}/Makefile")
    generated_release = _read(f"{tree}/include/config/kernel.release")
    generated_uts = _read(f"{tree}/include/generated/utsrelease.h")
    local = generated_release or generated_uts or _read(f"{tree}/include/config/auto.conf.cmd")
    compiler = _read(f"{tree}/include/generated/compile.h")
    symvers = os.path.isfile(f"{tree}/Module.symvers")
    vermagic = _module_vermagic()
    values = _kernel_config(tree, release)
    compiler_id = _compiler_id(tree)
    symvers_map = _symvers(tree)
    return KernelInfo(
        release=release,
        version=_extract_kernel_version(makefile, generated_release or release),
        architecture=platform.machine(),
        build_tree=tree if os.path.isdir(tree) else "",
        headers_present=os.path.isdir(tree),
        config_present=bool(values) or os.path.exists(config),
        modules_symvers_present=symvers,
        compiler=compiler[:200],
        localversion=local[:200],
        vermagic=vermagic[:200],
        config=values,
        compiler_id=compiler_id,
        symvers=symvers_map,
    )


def required_config_missing(info: KernelInfo, requirements: tuple[str, ...]) -> tuple[str, ...]:
    missing = []
    for requirement in requirements:
        value = info.config.get(requirement)
        if value not in {"y", "m"}:
            missing.append(requirement)
    return tuple(missing)


def _extract_kernel_version(makefile: str, fallback: str) -> str:
    vals = {}
    for key in ("VERSION", "PATCHLEVEL", "SUBLEVEL", "EXTRAVERSION"):
        match = re.search(rf"^\s*{key}\s*=\s*(.*)$", makefile, re.M)
        if match:
            vals[key] = match.group(1).strip()
    if vals:
        return ".".join(vals.get(k, "0") for k in ("VERSION", "PATCHLEVEL", "SUBLEVEL")) + vals.get("EXTRAVERSION", "")
    return fallback


def kernel_major_minor(release: str) -> tuple[int, int] | None:
    match = re.match(r"(\d+)\.(\d+)", release)
    return (int(match.group(1)), int(match.group(2))) if match else None


def kernel_in_range(release: str, minimum: str | None = None, maximum: str | None = None) -> bool:
    current = kernel_major_minor(release)
    if not current:
        return False
    for bound, lower in ((minimum, True), (maximum, False)):
        if not bound:
            continue
        parsed = kernel_major_minor(bound)
        if not parsed:
            return False
        if lower and current < parsed:
            return False
        if not lower and current > parsed:
            return False
    return True
