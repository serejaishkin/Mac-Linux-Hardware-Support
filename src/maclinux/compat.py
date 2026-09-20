"""Compatibility checks for hardware integrations."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def _secure_boot() -> str:
    path = Path("/sys/firmware/efi")
    if not path.exists():
        return "not-uefi"
    candidates = [
        Path("/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c"),
    ]
    for candidate in candidates:
        try:
            data = candidate.read_bytes()
            if len(data) >= 5:
                return "enabled" if data[4] == 1 else "disabled"
        except OSError:
            pass
    return "unknown"


def compatibility(system: dict, device: dict) -> dict:
    actions = []
    blockers = []
    module = device["driver"]
    kernel = system["kernel"]

    if system["architecture"] not in device["architectures"]:
        blockers.append("architecture-not-supported")

    headers = Path(f"/lib/modules/{kernel}/build")
    if not headers.exists():
        blockers.append("kernel-build-tree-missing")
        actions.append("install matching kernel headers/devel package")

    if device.get("firmware_required"):
        firmware_dir = Path("/lib/firmware/facetimehd")
        alt_dir = Path("/usr/lib/firmware/facetimehd")
        if not firmware_dir.is_dir() and not alt_dir.is_dir():
            blockers.append("firmware-not-found")
            actions.append("prepare facetimehd firmware")

    if shutil.which("dkms") is None:
        actions.append("install dkms or use native kernel-module packaging")

    secure_boot = _secure_boot()
    if secure_boot == "enabled":
        blockers.append("secure-boot-enabled")
        actions.append("enroll/sign the kernel module before loading it")
    elif secure_boot == "unknown":
        actions.append("verify Secure Boot state before installing an out-of-tree module")

    status = "ready-to-build" if not blockers else "blocked"
    return {
        "device": device["id"],
        "driver": module,
        "kernel": kernel,
        "secure_boot": secure_boot,
        "status": status,
        "blockers": blockers,
        "actions": actions,
    }
