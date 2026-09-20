from maclinux.hardware import HardwareDevice
from maclinux.resolver import resolve


def test_reference_model_resolves_full_stack():
    system = {"model": "MacBookPro11,1"}
    plans = resolve(
        system,
        [
            HardwareDevice(
                bus="pci",
                address="01:00.0",
                vendor_id="14e4",
                device_id="1570",
                class_id="0401",
            )
        ],
    )
    components = {item["component"]: item for item in plans}
    assert "camera" in components
    assert components["camera"]["selection"] == "hardware-id"
    assert "facetimehd" in components["camera"]["candidates"]


def test_unknown_model_still_exposes_known_hardware():
    system = {"model": "unknown"}
    plans = resolve(
        system,
        [
            HardwareDevice(
                bus="pci",
                address="00:00.0",
                vendor_id="14e4",
                device_id="1570",
            )
        ],
    )
    assert plans[0]["component"] == "camera"
