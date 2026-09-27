from installer.adapters import (
    ApkAdapter,
    AltAdapter,
    AptAdapter,
    DnfAdapter,
    GentooAdapter,
    PacmanAdapter,
    ZypperAdapter,
    get_adapter,
)
from installer.requirements import RequirementMapper


def test_ubuntu_maps_logical_requirements():
    plan = RequirementMapper("ubuntu").map(["compiler", "make", "kernel-devel", "dkms", "compiler"])
    assert plan.packages == ("build-essential", "linux-headers-$(uname -r)", "dkms")


def test_alt_maps_kernel_development_requirements():
    plan = RequirementMapper("altlinux").map(["compiler", "make", "kernel-devel"])
    assert plan.packages == ("gcc", "make", "kernel-headers")
    assert any("ALT" in note for note in plan.notes)


def test_all_target_ecosystems_have_adapters():
    cases = {
        "ubuntu": AptAdapter,
        "altlinux": AltAdapter,
        "fedora": DnfAdapter,
        "arch": PacmanAdapter,
        "opensuse": ZypperAdapter,
        "alpine": ApkAdapter,
        "gentoo": GentooAdapter,
    }
    for distro, expected in cases.items():
        assert isinstance(get_adapter({"distribution": distro}), expected)


def test_fedora_requirement_plan_is_native():
    adapter = DnfAdapter()
    plan = adapter.plan_requirements(["compiler", "kernel-devel", "dkms"])
    assert plan.packages == ("gcc", "kernel-devel", "dkms")


def test_arch_requirement_plan_uses_base_devel():
    plan = PacmanAdapter().plan_requirements(["compiler", "kernel-headers"])
    assert plan.packages == ("base-devel", "linux-headers")


def test_gentoo_requirement_plan_uses_atoms():
    plan = GentooAdapter().plan_requirements(["compiler", "dkms"])
    assert plan.packages == ("sys-devel/gcc", "sys-kernel/dkms")


def test_unknown_requirement_is_reported_without_execution():
    plan = RequirementMapper("ubuntu").map(["compiler", "future-requirement"])
    assert "build-essential" in plan.packages
    assert any("future-requirement" in note for note in plan.notes)
