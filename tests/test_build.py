from maclinux.artifacts import validate_artifact
from maclinux.build import execute_build, plan_build
from maclinux.kernel import KernelInfo
from maclinux.platform import detect_platform


def test_build_is_dry_run_by_default():
    info = detect_platform({
        "ID": "ubuntu",
        "VERSION_ID": "24.04",
        "VERSION_CODENAME": "noble",
    })
    plan = plan_build("unknown-driver", info)
    result = execute_build(plan)
    assert result["status"] == "dry-run"
    assert result["executed"] is False


def test_unknown_driver_is_blocked():
    info = detect_platform({
        "ID": "ubuntu",
        "VERSION_ID": "24.04",
    })
    plan = plan_build("unknown-driver", info)
    assert plan.status == "unknown"
    assert "no build recipe" in plan.blockers


def test_artifact_missing_is_invalid():
    result = validate_artifact("/definitely/missing/module.ko", expected_module="module")
    assert result.status == "invalid"
    assert "artifact does not exist" in result.errors


def test_artifact_unresolved_symbols_are_reported(monkeypatch, tmp_path):
    artifact = tmp_path / "demo.ko"
    artifact.write_bytes(b"not-an-elf")
    monkeypatch.setattr("maclinux.artifacts._elf_machine", lambda _: "Advanced Micro Devices X86-64")
    monkeypatch.setattr("maclinux.artifacts._modinfo", lambda _p, field: {
        "name": "demo", "vermagic": "6.8.0 SMP", "depends": ""
    }.get(field))
    monkeypatch.setattr("maclinux.artifacts._undefined_symbols", lambda _: ("missing_symbol", "ok_symbol"))
    result = validate_artifact(
        str(artifact), expected_module="demo", expected_architecture="x86_64",
        expected_vermagic="6.8.0", exported_symbols={"ok_symbol"}
    )
    assert result.status == "invalid"
    assert result.unresolved_symbols == ("missing_symbol",)
    assert "missing_symbol" in result.errors[0]


def test_artifact_crc_mismatch_is_reported(monkeypatch, tmp_path):
    artifact = tmp_path / "demo.ko"
    artifact.write_bytes(b"fixture")
    monkeypatch.setattr("maclinux.artifacts._elf_machine", lambda _: "Advanced Micro Devices X86-64")
    monkeypatch.setattr("maclinux.artifacts._modinfo", lambda _p, field: {
        "name": "demo", "vermagic": "6.8.0 SMP", "depends": ""
    }.get(field))
    monkeypatch.setattr("maclinux.artifacts._undefined_symbols", lambda _: ())
    monkeypatch.setattr("maclinux.artifacts._module_symbol_versions",
                        lambda _: {"foo_symbol": "0x1111"})
    result = validate_artifact(
        str(artifact), expected_module="demo", expected_architecture="x86_64",
        expected_vermagic="6.8.0", exported_symbols={"foo_symbol"},
        exported_symbol_crcs={"foo_symbol": "0x2222"}
    )
    assert result.status == "invalid"
    assert "CRC mismatch" in result.errors[-1]
