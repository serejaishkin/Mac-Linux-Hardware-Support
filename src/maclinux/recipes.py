"""Declarative driver build recipes and compatibility decisions."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Recipe:
    driver: str
    source: str
    components: tuple[str, ...]
    architectures: tuple[str, ...]
    distributions: tuple[str, ...]
    kernel_min: str | None
    kernel_max: str | None
    build_system: str
    packages: tuple[str, ...]
    modules: tuple[str, ...]
    firmware: tuple[str, ...]
    kernel_config: tuple[str, ...] = ()
    hardware_ids: tuple[str, ...] = ()
    patches: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


RECIPES = {
    "facetimehd": Recipe(
        "facetimehd", "facetimehd", ("camera",), ("x86_64",),
        ("ubuntu", "debian", "altlinux", "fedora", "arch", "opensuse"),
        "4.0", None, "kbuild/dkms",
        ("compiler", "make", "kernel-devel"), ("facetimehd",),
        ("facetimehd-firmware",), conflicts=(), hardware_ids=("14e4:1570",),
    ),
    "snd_hda_macbookpro": Recipe(
        "snd_hda_macbookpro", "snd_hda_macbookpro", ("audio",), ("x86_64",),
        ("ubuntu", "debian", "altlinux", "fedora", "arch", "opensuse"),
        "4.0", None, "kbuild",
        ("compiler", "make", "kernel-devel"), ("snd-hda-macbookpro",),
        (),
    ),
    "applespi": Recipe(
        "applespi", "applespi", ("keyboard", "trackpad"), ("x86_64", "aarch64"),
        ("ubuntu", "debian", "altlinux", "fedora", "arch", "opensuse"),
        "4.0", None, "kbuild/dkms",
        ("compiler", "make", "kernel-devel"), ("applespi",),
        (),
    ),
}


def get_recipe(driver: str) -> Recipe | None:
    return RECIPES.get(driver)


def recipe_status(recipe: Recipe | None, *, distribution: str, architecture: str, kernel: str, hardware_id: str | None = None) -> str:
    if recipe is None:
        return "unknown"
    if hardware_id and recipe.hardware_ids and hardware_id not in recipe.hardware_ids:\n        return "unsupported"\n    if architecture not in recipe.architectures:
        return "unsupported"
    if distribution not in recipe.distributions:
        return "unsupported"
    from .kernel import kernel_in_range
    if not kernel_in_range(kernel, recipe.kernel_min, recipe.kernel_max):
        return "patch-required"
    return "buildable"
