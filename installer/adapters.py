"""Distribution-neutral, read-only installation planning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .requirements import RequirementMapper, RequirementPlan


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
    manager = "generic"

    def matches(self, system: dict) -> bool:
        return False

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(self.manager, names)

    def plan_requirements(self, requirements: Iterable[str]) -> RequirementPlan:
        return RequirementMapper("unknown").map(requirements)

    def plan_kernel_headers(self, kernel: str) -> PackagePlan:
        return PackagePlan(
            self.manager,
            notes=(f"Install kernel development files matching {kernel}.",),
        )


class AptAdapter(DistributionAdapter):
    id = "apt"
    manager = "apt"

    def matches(self, system: dict) -> bool:
        return system.get("distribution", "").lower() in {"debian", "ubuntu", "linuxmint", "pop"}

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            self.manager,
            names,
            (f"sudo apt-get install {' '.join(names)}",) if names else (),
            ("Read-only planning: commands are not executed.",),
        )

    def plan_requirements(self, requirements: Iterable[str]) -> RequirementPlan:
        return RequirementMapper(self._distribution()).map(requirements)

    def _distribution(self) -> str:
        return getattr(self, "_current_distribution", "ubuntu")

    def plan_for_system(self, system: dict, requirements: Iterable[str]) -> PackagePlan:
        self._current_distribution = system.get("distribution", "ubuntu").lower()
        req = self.plan_requirements(requirements)
        names = req.packages
        return PackagePlan(
            self.manager,
            names,
            (f"sudo apt-get install {' '.join(names)}",) if names else (),
            req.notes + ("Read-only planning: commands are not executed.",),
        )

    def plan_kernel_headers(self, kernel: str) -> PackagePlan:
        return PackagePlan(
            self.manager,
            ("linux-headers-" + kernel, "dkms"),
            (f"sudo apt-get install linux-headers-{kernel} dkms",),
            ("Package names may differ on derivative distributions.",),
        )


class AltAdapter(DistributionAdapter):
    id = "alt-apt-rpm"
    manager = "apt-rpm"

    def matches(self, system: dict) -> bool:
        return system.get("distribution", "").lower() in {"altlinux", "alt"}

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            self.manager,
            names,
            (f"su -c 'apt-get install {' '.join(names)}'",) if names else (),
            ("Read-only planning: commands are not executed.",),
        )

    def plan_requirements(self, requirements: Iterable[str]) -> RequirementPlan:
        return RequirementMapper("altlinux").map(requirements)

    def plan_for_system(self, system: dict, requirements: Iterable[str]) -> PackagePlan:
        req = self.plan_requirements(requirements)
        names = req.packages
        return PackagePlan(
            self.manager,
            names,
            (f"su -c 'apt-get install {' '.join(names)}'",) if names else (),
            req.notes + ("Read-only planning: commands are not executed.",),
        )

    def plan_kernel_headers(self, kernel: str) -> PackagePlan:
        return PackagePlan(
            self.manager,
            ("kernel-headers-modules-" + kernel, "dkms"),
            (f"su -c 'apt-get install kernel-headers-modules-{kernel} dkms'",),
            ("Exact ALT kernel package naming must be verified against the installed kernel package.",),
        )


class DnfAdapter(DistributionAdapter):
    id = "dnf-rpm"
    manager = "dnf"

    def matches(self, system: dict) -> bool:
        return system.get("distribution", "").lower() in {
            "fedora", "rhel", "centos", "centos-stream", "rocky", "almalinux",
        }

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            self.manager, names,
            (f"sudo dnf install {' '.join(names)}",) if names else (),
            ("Read-only planning: commands are not executed.",),
        )

    def plan_requirements(self, requirements: Iterable[str]) -> RequirementPlan:
        return RequirementMapper(self._distribution).map(requirements)

    @property
    def _distribution(self) -> str:
        return "fedora"


class PacmanAdapter(DistributionAdapter):
    id = "pacman"
    manager = "pacman"

    def matches(self, system: dict) -> bool:
        return system.get("distribution", "").lower() in {"arch", "manjaro", "endeavouros"}

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            self.manager, names,
            (f"sudo pacman -S {' '.join(names)}",) if names else (),
            ("Read-only planning: commands are not executed.",),
        )

    def plan_requirements(self, requirements: Iterable[str]) -> RequirementPlan:
        return RequirementMapper("arch").map(requirements)


class ZypperAdapter(DistributionAdapter):
    id = "zypper-rpm"
    manager = "zypper"

    def matches(self, system: dict) -> bool:
        return system.get("distribution", "").lower() in {"opensuse", "opensuse-leap", "opensuse-tumbleweed"}

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            self.manager, names,
            (f"sudo zypper install {' '.join(names)}",) if names else (),
            ("Read-only planning: commands are not executed.",),
        )

    def plan_requirements(self, requirements: Iterable[str]) -> RequirementPlan:
        return RequirementMapper("opensuse").map(requirements)


class ApkAdapter(DistributionAdapter):
    id = "apk"
    manager = "apk"

    def matches(self, system: dict) -> bool:
        return system.get("distribution", "").lower() == "alpine"

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            self.manager, names,
            (f"sudo apk add {' '.join(names)}",) if names else (),
            ("Read-only planning: commands are not executed.",),
        )

    def plan_requirements(self, requirements: Iterable[str]) -> RequirementPlan:
        return RequirementMapper("alpine").map(requirements)


class GentooAdapter(DistributionAdapter):
    id = "emerge-ebuild"
    manager = "emerge"

    def matches(self, system: dict) -> bool:
        return system.get("distribution", "").lower() == "gentoo"

    def plan_packages(self, packages: Iterable[str]) -> PackagePlan:
        names = tuple(dict.fromkeys(packages))
        return PackagePlan(
            self.manager, names,
            (f"sudo emerge {' '.join(names)}",) if names else (),
            ("Read-only planning: commands are not executed.",),
        )

    def plan_requirements(self, requirements: Iterable[str]) -> RequirementPlan:
        return RequirementMapper("gentoo").map(requirements)


class GenericAdapter(DistributionAdapter):
    id = "generic"
    manager = "generic"

    def matches(self, system: dict) -> bool:
        return True


ADAPTERS = (
    AptAdapter(),
    AltAdapter(),
    DnfAdapter(),
    PacmanAdapter(),
    ZypperAdapter(),
    ApkAdapter(),
    GentooAdapter(),
    GenericAdapter(),
)


def get_adapter(system: dict) -> DistributionAdapter:
    for adapter in ADAPTERS:
        if adapter.matches(system):
            return adapter
    return GenericAdapter()
