"""Normalized hardware records used by detection and driver resolution."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class HardwareDevice:
    bus: str
    address: str
    vendor_id: str | None = None
    device_id: str | None = None
    class_id: str | None = None
    name: str | None = None
    driver: str | None = None
    module: str | None = None
    component: str | None = None
    source: str = "sysfs"

    @property
    def id(self) -> str | None:
        if self.vendor_id and self.device_id:
            return f"{self.vendor_id}:{self.device_id}"
        return None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["id"] = self.id
        return value


def normalize_id(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower().removeprefix("0x")


def classify_pci(class_id: str | None) -> str | None:
    if not class_id:
        return None
    prefix = class_id.lower()[:2]
    return {
        "01": "storage",
        "02": "network",
        "03": "graphics",
        "04": "multimedia",
        "05": "memory",
        "06": "bridge",
        "0c": "serial-bus",
    }.get(prefix)


def device_from_pci(item: dict[str, str]) -> HardwareDevice:
    return HardwareDevice(
        bus="pci",
        address=item.get("slot", ""),
        vendor_id=normalize_id(item.get("vendor_id")),
        device_id=normalize_id(item.get("device_id")),
        class_id=normalize_id(item.get("class")),
        name=item.get("raw"),
        driver=item.get("driver"),
        module=item.get("module"),
        component=classify_pci(item.get("class")),
        source="lspci",
    )
