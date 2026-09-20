"""Linux hardware detection without third-party Python dependencies."""

from __future__ import annotations

import os
import platform
import re
import subprocess
from pathlib import Path

from .registry import DEVICES, MODELS


def _read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""


def command_output(*args: str) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return ""


def dmi() -> dict[str, str]:
    return {
        "product_name": _read("/sys/devices/virtual/dmi/id/product_name"),
        "product_version": _read("/sys/devices/virtual/dmi/id/product_version"),
        "board_name": _read("/sys/devices/virtual/dmi/id/board_name"),
        "bios_version": _read("/sys/devices/virtual/dmi/id/bios_version"),
    }


def lspci_devices() -> list[dict[str, str]]:
    output = command_output("lspci", "-nn")
    devices = []
    pattern = re.compile(r"(?P<slot>[0-9a-f:.]+).*?\[(?P<class>[0-9a-f]{4})\]:.*?\[(?P<vendor>[0-9a-f]{4}):(?P<device>[0-9a-f]{4})\]")
    for line in output.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        item = {
            "slot": match.group("slot"),
            "class": match.group("class"),
            "vendor_id": match.group("vendor").lower(),
            "device_id": match.group("device").lower(),
            "raw": line.strip(),
        }
        item["pci_id"] = f"{item['vendor_id']}:{item['device_id']}"
        item["known"] = item["pci_id"] in DEVICES
        if item["known"]:
            item["integration"] = DEVICES[item["pci_id"]]["id"]
        devices.append(item)
    return devices


def detect() -> dict:
    info = dmi()
    model = info["product_name"] or "unknown"
    return {
        "os": _read("/etc/os-release"),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "dmi": info,
        "model": model,
        "model_known": model in MODELS,
        "devices": lspci_devices(),
    }


def module_loaded(module: str) -> bool:
    modules = _read("/proc/modules")
    return any(line.split(" ", 1)[0] == module for line in modules.splitlines())


def firmware_candidates(name: str) -> list[str]:
    roots = [
        "/lib/firmware/facetimehd",
        "/usr/lib/firmware/facetimehd",
    ]
    result = []
    for root in roots:
        path = Path(root)
        if path.is_dir():
            result.extend(str(p) for p in sorted(path.iterdir()) if p.is_file())
    return result
