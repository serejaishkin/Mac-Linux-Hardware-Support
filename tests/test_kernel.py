from maclinux.kernel import KernelInfo, kernel_in_range, kernel_major_minor, required_config_missing


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
