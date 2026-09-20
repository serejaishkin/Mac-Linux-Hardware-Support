from maclinux.kernel import kernel_in_range, kernel_major_minor


def test_kernel_range():
    assert kernel_major_minor("6.8.0-generic") == (6, 8)
    assert kernel_in_range("6.8.0", "5.15", "6.11")
    assert not kernel_in_range("4.19.0", "5.15", None)
