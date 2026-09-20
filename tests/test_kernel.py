from maclinux.kernel import KernelInfo, _compiler_id, _symvers, kernel_in_range, kernel_major_minor, required_config_missing


def test_kernel_range():
    assert kernel_major_minor("6.8.0-generic") == (6, 8)
    assert kernel_in_range("6.8.0", "5.15", "6.11")
    assert not kernel_in_range("4.19.0", "5.15", None)


def test_required_config_missing():
    info = KernelInfo("6.8", "6.8", "x86_64", "", True, True, True, "gcc", "", "", {
        "CONFIG_SND": "y",
        "CONFIG_INPUT": "m",
        "CONFIG_MEDIA_SUPPORT": "n",
    })
    assert required_config_missing(info, ("CONFIG_SND", "CONFIG_INPUT")) == ()
    assert required_config_missing(info, ("CONFIG_MEDIA_SUPPORT",)) == ("CONFIG_MEDIA_SUPPORT",)


def test_compiler_id_and_symvers(tmp_path):
    tree = tmp_path / "build"
    (tree / "include/generated").mkdir(parents=True)
    (tree / "include/generated/compile.h").write_text(
        '#define LINUX_COMPILER "gcc (GCC) 14.2.1 20240910 (Red Hat 14.2.1-3)"\n',
        encoding="utf-8",
    )
    (tree / "Module.symvers").write_text(
        "0x1234\tfoo_symbol\tvmlinux\tEXPORT_SYMBOL\n"
        "0x5678\tbar_symbol\tother\tEXPORT_SYMBOL_GPL\tNS\n",
        encoding="utf-8",
    )
    assert "gcc (GCC) 14.2.1" in _compiler_id(str(tree))
    assert _symvers(str(tree))["foo_symbol"][0] == "0x1234"
    assert _symvers(str(tree))["bar_symbol"][3] == "NS"
