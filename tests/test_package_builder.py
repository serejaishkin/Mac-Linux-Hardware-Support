from maclinux.package_builder import execute_package_build, plan_package_build
from maclinux.packaging import PackageArtifact


def _artifact():
    return PackageArtifact(
        driver="demo", package_name="maclinux-demo", package_version="1.0.0",
        ecosystem="generic", architecture="x86_64", kernel_release="6.8.0",
        source_sha256="abc", modules=("demo",),
    )


def test_package_build_is_dry_run(tmp_path):
    module = tmp_path / "demo.ko"
    module.write_bytes(b"fixture")
    result = execute_package_build(_artifact(), (str(module),))
    assert result["status"] == "dry-run"
    assert result["executed"] is False


def test_package_build_blocks_missing_module(tmp_path):
    plan = plan_package_build(_artifact(), (str(tmp_path / "missing.ko"),))
    assert plan.status == "blocked"
    assert any("module artifact not found" in x for x in plan.blockers)


def test_package_build_generic_executes_without_install(monkeypatch, tmp_path):
    module = tmp_path / "demo.ko"
    module.write_bytes(b"fixture")
    monkeypatch.setattr("maclinux.package_builder.shutil.which", lambda tool: "/usr/bin/" + tool)
    result = execute_package_build(
        _artifact(), (str(module),), output_dir=str(tmp_path / "dist"), execute=True
    )
    assert result["status"] in {"built", "package-build-failed"}
    assert result["executed"] is True
    assert result["status"] != "blocked"
