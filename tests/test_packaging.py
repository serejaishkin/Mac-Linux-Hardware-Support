from maclinux.packaging import package_plan


def test_ubuntu_external_driver_plan_is_read_only():
    plan = package_plan("ubuntu", "facetimehd")
    assert plan.ecosystem == "deb"
    assert "dkms" in plan.packages
    assert any("apt-get install" in cmd for cmd in plan.commands)


def test_alt_plan_uses_alt_ecosystem():
    plan = package_plan("altlinux", "facetimehd")
    assert plan.ecosystem == "alt"
    assert "kernel-headers" in plan.packages


def test_unknown_distribution_is_generic():
    plan = package_plan("unknown-linux", "facetimehd")
    assert plan.ecosystem == "generic"
