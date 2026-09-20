"""Linux hardware detection without third-party Python dependencies."""

from __future__ import annotations

import platform
import re
import subprocess
from pathlib import Path

from .hardware import HardwareDevice
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
    # -nnk includes the currently bound kernel driver when available.
    output = command_output("lspci", "-nnk")
    devices = []
    current: dict[str, str] | None = None
    pattern = re.compile(
        r"(?P<slot>[0-9a-f:.]+).*?\[(?P<class>[0-9a-f]{4})\]:.*?\[(?P<vendor>[0-9a-f]{4}):(?P<device>[0-9a-f]{4})\]"
    )
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            if current:
                devices.append(current)
            current = {
                "slot": match.group("slot"),
                "class": match.group("class"),
                "vendor_id": match.group("vendor").lower(),
                "device_id": match.group("device").lower(),
                "raw": line.strip(),
            }
            current["pci_id"] = f"{current['vendor_id']}:{current['device_id']}"
            current["known"] = current["pci_id"] in DEVICES
            if current["known"]:
                current["integration"] = DEVICES[current["pci_id"]]["id"]
            continue
        if current:
            driver = re.search(r"Kernel driver in use:\s*(\S+)", line)
            module = re.search(r"Kernel modules:\s*(.+)", line)
            if driver:
                current["driver"] = driver.group(1)
            if module:
                current["module"] = module.group(1).strip()
    if current:
        devices.append(current)
    return devices


def usb_devices() -> list[dict[str, str]]:
    output = command_output("lsusb")
    result = []
    pattern = re.compile(
        r"ID\s+(?P<vendor>[0-9a-f]{4}):(?P<product>[0-9a-f]{4})\s*(?P<name>.*)$",
        re.I,
    )
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            result.append(
                {
                    "vendor_id": match.group("vendor").lower(),
                    "device_id": match.group("product").lower(),
                    "name": match.group("name").strip(),
                    "raw": line.strip(),
                }
            )
    return result


def loaded_modules() -> list[str]:
    modules = _read("/proc/modules")
    return [line.split(" ", 1)[0] for line in modules.splitlines() if line]


def sysfs_buses() -> dict[str, int]:
    result = {}
    root = Path("/sys/bus")
    if root.is_dir():
        for item in root.iterdir():
            if item.is_dir():
                result[item.name] = len(list((item / "devices").iterdir())) if (item / "devices").is_dir() else 0
    return result


def sysfs_devices(bus: str) -> list[dict[str, str]]:
    """Return stable identity/driver information from a sysfs bus.

    This deliberately avoids writing to sysfs and does not assume that every
    Apple internal device is PCI or USB.
    """
    root = Path("/sys/bus") / bus / "devices"
    result = []
    if not root.is_dir():
        return result
    for item in sorted(root.iterdir(), key=lambda p: p.name):
        record = {"bus": bus, "address": item.name}
        for key in ("modalias", "uevent", "vendor", "device", "class"):
            value = _read(str(item / key))
            if value:
                record[key] = value
        driver = item / "driver"
        if driver.is_symlink():
            try:
                record["driver"] = driver.resolve().name
            except OSError:
                pass
        result.append(record)
    return result


def platform_devices() -> list[dict[str, str]]:
    return sysfs_devices("platform")


def hid_devices() -> list[dict[str, str]]:
    return sysfs_devices("hid")


def spi_devices() -> list[dict[str, str]]:
    return sysfs_devices("spi")


def i2c_devices() -> list[dict[str, str]]:
    return sysfs_devices("i2c")


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
        "usb_devices": usb_devices(),
        "loaded_modules": loaded_modules(),
        "sysfs_buses": sysfs_buses(),
        "platform_devices": platform_devices(),
        "hid_devices": hid_devices(),
        "spi_devices": spi_devices(),
        "i2c_devices": i2c_devices(),
    }


def hardware_devices(result: dict) -> list[HardwareDevice]:
    return [HardwareDevice(**{
        "bus": "pci",
        "address": item.get("slot", ""),
        "vendor_id": item.get("vendor_id"),
        "device_id": item.get("device_id"),
        "class_id": item.get("class"),
        "name": item.get("raw"),
        "driver": item.get("driver"),
        "module": item.get("module"),
    }) for item in result.get("devices", [])]


def module_loaded(module: str, system: dict | None = None) -> bool:
    modules = system.get("loaded_modules", []) if system else loaded_modules()
    return module in modules


def firmware_candidates(name: str) -> list[str]:
    roots = [
        Path(f"/lib/firmware/{name}"),
        Path(f"/usr/lib/firmware/{name}"),
    ]
    result = []
    for root in roots:
        if root.is_dir():
            result.extend(str(p) for p in sorted(root.iterdir()) if p.is_file())
    return result
