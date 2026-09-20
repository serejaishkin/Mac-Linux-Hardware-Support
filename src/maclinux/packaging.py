"""Distribution-neutral package planning. No system changes are performed here."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackagePlan:
    ecosystem: str
    packages: tuple[str, ...]
    commands: tuple[str, ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "ecosystem": self.ecosystem,
            "packages": list(self.packages),
            "commands": list(self.commands),
            "notes": list(self.notes),
        }


COMMON = {
    "facetimehd": ("facetimehd",),
    "camera-firmware": ("facetimehd-firmware",),
    "kernel-build": ("kernel-headers",),
    "dkms": ("dkms",),
}


def package_plan(distribution: str, driver: str, source: str = "external") -> PackagePlan:
    distro = distribution.lower()
    if distro in {"ubuntu", "debian", "linuxmint", "pop"}:
        ecosystem = "deb"
        if driver == "facetimehd":
            packages = ("dkms", "git", "build-essential", "linux-headers-$(uname -r)")
            commands = (
                "sudo apt-get update",
                "sudo apt-get install dkms git build-essential linux-headers-$(uname -r)",
            )
            notes = ("Firmware is a separate acquisition step; do not bundle proprietary firmware in this project.",)
        else:
            packages = ("linux-headers-$(uname -r)",)
            commands = ("sudo apt-get install linux-headers-$(uname -r)",)
            notes = ()
    elif distro in {"alt", "altlinux"}:
        ecosystem = "alt"
        if driver == "facetimehd":
            packages = ("kernel-headers", "gcc", "make", "dkms")
            commands = ("apt-get update", "apt-get install kernel-headers gcc make dkms")
            notes = ("Exact ALT package names must be verified against the target branch before installation.",)
        else:
            packages = ("kernel-headers",)
            commands = ("apt-get install kernel-headers",)
            notes = ()
    elif distro in {"fedora", "rhel", "centos", "rocky", "almalinux"}:
        ecosystem = "rpm"
        packages = ("kernel-devel", "kernel-headers")
        commands = ("sudo dnf install kernel-devel kernel-headers",)
        notes = ("DKMS package availability varies by repository configuration.",)
    elif distro == "arch" or distro.startswith("manjaro"):
        ecosystem = "arch"
        packages = ("base-devel", "linux-headers")
        commands = ("sudo pacman -S base-devel linux-headers",)
        notes = ()
    elif distro in {"opensuse-tumbleweed", "opensuse-leap", "opensuse"}:
        ecosystem = "rpm-zypper"
        packages = ("kernel-default-devel", "kernel-devel")
        commands = ("sudo zypper install kernel-default-devel kernel-devel",)
        notes = ()
    elif distro == "alpine":
        ecosystem = "apk"
        packages = ("build-base", "linux-headers", "dkms")
        commands = ("sudo apk add build-base linux-headers dkms",)
        notes = ()
    elif distro == "gentoo":
        ecosystem = "gentoo"
        packages = ("sys-kernel/linux-headers",)
        commands = ("sudo emerge sys-kernel/linux-headers",)
        notes = ("Kernel source/configuration must also match the running kernel for external modules.",)
    else:
        ecosystem = "generic"
        packages = ("kernel development headers",)
        commands = ("Install the matching kernel development package using the distribution's package manager.",)
        notes = ("No automatic installation is supported for this distribution yet.",)

    return PackagePlan(ecosystem, tuple(packages), tuple(commands), tuple(notes))



def repair_transaction(plan: PackagePlan, *, dry_run: bool = True) -> dict:
    """Create an auditable transaction plan; never execute privileged operations."""
    return {
        "mode": "dry-run" if dry_run else "blocked",
        "safe_to_execute": False,
        "commands": list(plan.commands) + list(plan.module_commands),
        "rollback": "restore package/module state from the recorded preflight snapshot",
        "preflight": ["re-detect model, architecture and kernel", "verify package-manager availability",
                      "verify matching kernel development files", "verify driver architecture compatibility",
                      "verify firmware state separately", "record current driver/module bindings"],
        "reason": "Privileged repair execution is not enabled yet.",
    }
