from maclinux.validation import validate_component


def test_unknown_component_is_explicit():
    result = validate_component("future-component")[0]
    assert result.status == "unknown"


def test_camera_is_non_invasive():
    results = validate_component("camera")
    assert results
    assert all(r.status in {"pass", "fail", "skip", "unknown"} for r in results)


def test_storage_validator():
    result = validate_component("storage")[0]
    assert result.component == "storage"
    assert result.check == "block-device"
