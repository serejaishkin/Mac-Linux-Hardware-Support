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
    distribution_versions: dict[str, tuple[str, ...]]
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


DEFAULT_VERSIONS = {
    "ubuntu": ("20.04", "22.04", "24.04", "26.04"),
    "debian": ("11", "12", "13"),
    "altlinux": ("p10", "p11"),
    "fedora": ("40", "41", "42", "43"),
    "arch": ("rolling",),
    "opensuse": ("Leap 15.6", "Leap 16", "Tumbleweed"),
}
RECIPE_DISTROS = tuple(DEFAULT_VERSIONS)


RECIPES = {
    "facetimehd": Recipe(
        "facetimehd", "facetimehd", ("camera",), ("x86_64",), RECIPE_DISTROS,
        DEFAULT_VERSIONS, "4.0", None, "kbuild/dkms",
        ("compiler", "make", "kernel-devel"), ("facetimehd",),
        ("facetimehd-firmware",), hardware_ids=("14e4:1570",),
    ),
    "snd_hda_macbookpro": Recipe(
        "snd_hda_macbookpro", "snd_hda_macbookpro", ("audio",), ("x86_64",), RECIPE_DISTROS,
        DEFAULT_VERSIONS, "4.0", None, "kbuild",
        ("compiler", "make", "kernel-devel"), ("snd-hda-macbookpro",),
    ),
    "applespi": Recipe(
        "applespi", "applespi", ("keyboard", "trackpad"), ("x86_64", "aarch64"), RECIPE_DISTROS,
        DEFAULT_VERSIONS, "4.0", None, "kbuild/dkms",
        ("compiler", "make", "kernel-devel"), ("applespi",),
    ),
}


def get_recipe(driver: str) -> Recipe | None:
    return RECIPES.get(driver)


def version_supported(recipe: Recipe, distribution: str, version: str) -> bool:
    allowed = recipe.distribution_versions.get(distribution)
    if allowed is None:
        return False
    if not version:
        return False
    return version in allowed or "rolling" in allowed and version.lower() == "rolling"


def recipe_status(
    recipe: Recipe | None,
    *,
    distribution: str,
    architecture: str,
    kernel: str,
    version: str = "",
    hardware_id: str | None = None,
) -> str:
    if recipe is None:
        return "unknown"
    if hardware_id and recipe.hardware_ids and hardware_id not in recipe.hardware_ids:
        return "unsupported"
    if architecture not in recipe.architectures:
        return "unsupported"
    if distribution not in recipe.distributions:
        return "unsupported"
    if not version_supported(recipe, distribution, version):
        return "unsupported"
    from .kernel import kernel_in_range
    if not kernel_in_range(kernel, recipe.kernel_min, recipe.kernel_max):
        return "patch-required"
    return "buildable"
