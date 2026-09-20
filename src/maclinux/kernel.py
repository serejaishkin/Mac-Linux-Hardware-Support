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

    def to_dict(self) -> dict:
        return asdict(self)


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().strip()
    except OSError:
        return ""


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
    return KernelInfo(
        release=release,
        version=_extract_kernel_version(makefile, generated_release or release),
        architecture=platform.machine(),
        build_tree=tree if os.path.isdir(tree) else "",
        headers_present=os.path.isdir(tree),
        config_present=os.path.exists(config) or os.path.exists(f"{tree}/.config"),
        modules_symvers_present=symvers,
        compiler=compiler[:200],
        localversion=local[:200],
        vermagic=vermagic[:200],
    )


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
