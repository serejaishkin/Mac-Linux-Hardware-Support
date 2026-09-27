"""Distribution-neutral, read-only installation planning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PackagePlan:
    manager: str
    packages: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "manager": self.manager,
            "packages": list(self.packages),
            "commands": list(self.commands),
            "notes": list(self.notes),
        }


class DistributionAdapter:
    id = "generic"

    def matches(self, system: dict) -> bool:
        return False

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        return PackagePlan(manager="generic", packages=tuple(packages))

    def plan_kernel_headers(self, kernel: str) -> PackagePlan:
        return PackagePlan(
            manager="generic",
            notes=(f"Install kernel headers/devel package matching {kernel}.",),
        )


class AptAdapter(DistributionAdapter):
    id = "apt"

    def matches(self, system: dict) -> bool:
        distro = system.get("distribution", "").lower()
        return distro in {"debian", "ubuntu", "linuxmint", "pop"}

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            manager="apt",
            packages=names,
            commands=(f"sudo apt-get install {' '.join(names)}",) if names else (),
            notes=("Read-only planning: commands are not executed.",),
        )

    def plan_kernel_headers(self, kernel: str) -> PackagePlan:
        return PackagePlan(
            manager="apt",
            packages=("linux-headers-" + kernel, "dkms"),
            commands=(f"sudo apt-get install linux-headers-{kernel} dkms",),
            notes=("Package names may differ on derivative distributions.",),
        )


class AltAdapter(DistributionAdapter):
    id = "alt-apt-rpm"

    def matches(self, system: dict) -> bool:
        distro = system.get("distribution", "").lower()
        return distro in {"altlinux", "alt"}

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            manager="apt-rpm",
            packages=names,
            commands=(f"su -c 'apt-get install {' '.join(names)}'",) if names else (),
            notes=("Read-only planning: commands are not executed.",),
        )

    def plan_kernel_headers(self, kernel: str) -> PackagePlan:
        return PackagePlan(
            manager="apt-rpm",
            packages=("kernel-headers-modules-" + kernel, "dkms"),
            commands=(f"su -c 'apt-get install kernel-headers-modules-{kernel} dkms'",),
            notes=("Exact ALT kernel package naming must be verified against the installed kernel package.",),
        )


class GenericAdapter(DistributionAdapter):
    id = "generic"

    def matches(self, system: dict) -> bool:
        return True


ADAPTERS = (AptAdapter(), AltAdapter(), GenericAdapter())


def get_adapter(system: dict) -> DistributionAdapter:
    for adapter in ADAPTERS:
        if adapter.matches(system):
            return adapter
    return GenericAdapter()
