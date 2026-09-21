from maclinux.packaging import PackageArtifact, get_package_backend, package_plan, render_package


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
    assert package_plan("unknown-linux", "facetimehd").ecosystem == "generic"


def test_backend_selection_covers_all_ecosystems():
    assert get_package_backend("deb").package_format == "deb"
    assert get_package_backend("rpm").package_format == "rpm"
    assert get_package_backend("alt").package_format == "rpm"
    assert get_package_backend("rpm-zypper").package_format == "rpm"
    assert get_package_backend("arch").package_format == "pkg.tar.zst"
    assert get_package_backend("apk").package_format == "apk"
    assert get_package_backend("gentoo").package_format == "ebuild"
    assert get_package_backend("generic").package_format == "tar"


def test_rendered_package_contains_provenance():
    artifact = PackageArtifact(
        driver="facetimehd", package_name="maclinux-facetimehd", package_version="0.1.0",
        ecosystem="deb", architecture="x86_64", kernel_release="6.8.0-test",
        source_sha256="abc123", modules=("facetimehd",), dependencies=("dkms",),
        firmware=("facetimehd-firmware",),
    )
    output = render_package(artifact)
    assert "source-sha256: abc123" in output.recipe
    assert "kernel: 6.8.0-test" in output.recipe
    assert output.build_commands == ("dpkg-buildpackage -us -uc",)
    assert artifact.artifact_id
