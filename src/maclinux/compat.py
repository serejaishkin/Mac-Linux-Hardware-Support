"""Non-invasive compatibility checks for hardware integrations."""

from __future__ import annotations

import shutil
from pathlib import Path


def _secure_boot() -> str:
    path = Path("/sys/firmware/efi")
    if not path.exists():
        return "not-uefi"
    candidate = Path(
        "/sys/firmware/efi/efivars/"
        "SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c"
    )
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
    if not headers.exists() and device.get("source") == "external":
        blockers.append("kernel-build-tree-missing")
        actions.append("install matching kernel headers/devel package")

    if device.get("firmware_required"):
        firmware_name = device.get("firmware_name", module)
        roots = [Path(f"/lib/firmware/{firmware_name}"), Path(f"/usr/lib/firmware/{firmware_name}")]
        if not any(root.is_dir() for root in roots):
            blockers.append("firmware-not-found")
            actions.append(f"prepare {firmware_name} firmware")

    if device.get("source") == "external" and shutil.which("dkms") is None:
        actions.append("install dkms or use native kernel-module packaging")

    secure_boot = _secure_boot()
    if device.get("source") == "external" and secure_boot == "enabled":
        blockers.append("secure-boot-enabled")
        actions.append("enroll/sign the kernel module before loading it")
    elif device.get("source") == "external" and secure_boot == "unknown":
        actions.append("verify Secure Boot state before installing an out-of-tree module")

    status = "ready" if not blockers else "blocked"
    return {
        "device": device["id"],
        "driver": module,
        "kernel": kernel,
        "secure_boot": secure_boot,
        "status": status,
        "blockers": blockers,
        "actions": actions,
    }
