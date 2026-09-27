"""Logical build/runtime requirements and distribution-specific package mapping.

The resolver and driver recipes speak in logical requirements (compiler, make,
kernel-devel, dkms, firmware tooling). Adapters translate those requirements
to package names without executing a package manager.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


LOGICAL_REQUIREMENTS = {
    "compiler",
    "make",
    "kernel-devel",
    "kernel-headers",
    "dkms",
    "git",
    "v4l2",
    "firmware-tools",
}


@dataclass(frozen=True)
class RequirementPlan:
    requirements: tuple[str, ...]
    packages: tuple[str, ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "requirements": list(self.requirements),
            "packages": list(self.packages),
            "notes": list(self.notes),
        }


class RequirementMapper:
    """Translate logical requirements into native package names."""

    def __init__(self, distribution: str):
        self.distribution = (distribution or "unknown").lower()

    def map(self, requirements: Iterable[str]) -> RequirementPlan:
        requested = tuple(dict.fromkeys(requirements))
        unknown = [r for r in requested if r not in LOGICAL_REQUIREMENTS]
        known = [r for r in requested if r in LOGICAL_REQUIREMENTS]

        if self.distribution in {"ubuntu", "debian", "linuxmint", "pop"}:
            mapping = {
                "compiler": "build-essential",
                "make": "build-essential",
                "kernel-devel": "linux-headers-$(uname -r)",
                "kernel-headers": "linux-headers-$(uname -r)",
                "dkms": "dkms",
                "git": "git",
                "v4l2": "v4l-utils",
                "firmware-tools": "linux-firmware",
            }
        elif self.distribution in {"alt", "altlinux"}:
            mapping = {
                "compiler": "gcc",
                "make": "make",
                "kernel-devel": "kernel-headers",
                "kernel-headers": "kernel-headers",
                "dkms": "dkms",
                "git": "git",
                "v4l2": "v4l-utils",
                "firmware-tools": "firmware-linux",
            }
        elif self.distribution in {"fedora", "rhel", "centos", "centos-stream", "rocky", "almalinux"}:
            mapping = {
                "compiler": "gcc",
                "make": "make",
                "kernel-devel": "kernel-devel",
                "kernel-headers": "kernel-headers",
                "dkms": "dkms",
                "git": "git",
                "v4l2": "v4l-utils",
                "firmware-tools": "linux-firmware",
            }
        elif self.distribution in {"arch", "manjaro", "endeavouros"}:
            mapping = {
                "compiler": "base-devel",
                "make": "base-devel",
                "kernel-devel": "linux-headers",
                "kernel-headers": "linux-headers",
                "dkms": "dkms",
                "git": "git",
                "v4l2": "v4l-utils",
                "firmware-tools": "linux-firmware",
            }
        elif self.distribution in {"opensuse", "opensuse-leap", "opensuse-tumbleweed"}:
            mapping = {
                "compiler": "gcc",
                "make": "make",
                "kernel-devel": "kernel-default-devel",
                "kernel-headers": "kernel-devel",
                "dkms": "dkms",
                "git": "git",
                "v4l2": "v4l-utils",
                "firmware-tools": "kernel-firmware",
            }
        elif self.distribution == "alpine":
            mapping = {
                "compiler": "build-base",
                "make": "build-base",
                "kernel-devel": "linux-headers",
                "kernel-headers": "linux-headers",
                "dkms": "dkms",
                "git": "git",
                "v4l2": "v4l-utils",
                "firmware-tools": "linux-firmware",
            }
        elif self.distribution == "gentoo":
            mapping = {
                "compiler": "sys-devel/gcc",
                "make": "sys-devel/make",
                "kernel-devel": "sys-kernel/gentoo-sources",
                "kernel-headers": "sys-kernel/linux-headers",
                "dkms": "sys-kernel/dkms",
                "git": "dev-vcs/git",
                "v4l2": "media-video/v4l-utils",
                "firmware-tools": "sys-kernel/linux-firmware",
            }
        else:
            mapping = {}

        packages = tuple(dict.fromkeys(mapping[r] for r in known if r in mapping))
        notes = []
        if unknown:
            notes.append("Unknown logical requirements: " + ", ".join(unknown))
        if not mapping and known:
            notes.append("No native package mapping is defined for this distribution.")
        if self.distribution in {"alt", "altlinux"} and "kernel-devel" in known:
            notes.append("ALT kernel package naming must be validated against the installed kernel branch.")
        return RequirementPlan(requested, packages, tuple(notes))
