from maclinux.platform import detect_platform, package_backend, normalize_distribution, read_os_release


def test_normalize_and_backend():
    assert normalize_distribution("linuxmint") == "ubuntu"
    assert package_backend("altlinux", {"ID_LIKE": "rpm"}) == ("rpm", "apt-get")
    assert package_backend("fedora", {}) == ("rpm", "dnf")


def test_detect_platform_from_os_release():
    info = detect_platform({
        "ID": "ubuntu",
        "VERSION_ID": "24.04",
        "VERSION_CODENAME": "noble",
        "ID_LIKE": "debian",
    })
    assert info.distribution == "ubuntu"
    assert info.version == "24.04"
    assert info.ecosystem == "deb"
    assert info.architecture
