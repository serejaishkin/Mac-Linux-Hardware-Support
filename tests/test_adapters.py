from installer.adapters import AltAdapter, AptAdapter, get_adapter


def test_ubuntu_uses_apt_adapter():
    adapter = get_adapter({"distribution": "ubuntu"})
    assert isinstance(adapter, AptAdapter)


def test_debian_plans_kernel_headers_and_dkms():
    plan = AptAdapter().plan_kernel_headers("6.8.0-test")
    assert "linux-headers-6.8.0-test" in plan.packages
    assert "dkms" in plan.packages
    assert all("sudo apt-get install" in cmd for cmd in plan.commands)


def test_alt_uses_apt_rpm_without_execution():
    adapter = get_adapter({"distribution": "altlinux"})
    assert isinstance(adapter, AltAdapter)
    plan = adapter.plan_packages(["dkms", "dkms", "gcc"])
    assert plan.packages == ("dkms", "gcc")
    assert "apt-get install" in plan.commands[0]
