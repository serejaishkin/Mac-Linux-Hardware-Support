from maclinux.registry import DEVICES, MODELS


def test_reference_model():
    assert "MacBookPro11,1" in MODELS


def test_facetimehd_pci_id():
    assert DEVICES["14e4:1570"]["driver"] == "facetimehd"
