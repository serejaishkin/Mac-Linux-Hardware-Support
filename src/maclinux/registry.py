"""Small dependency-free hardware registry used by the MVP."""

MODELS = {
    "MacBookPro11,1": {
        "vendor": "Apple",
        "family": "MacBook Pro",
        "generation": "Late 2013",
    },
}

DEVICES = {
    "14e4:1570": {
        "id": "facetimehd",
        "name": "Broadcom 720p FaceTime HD Camera",
        "class": "multimedia",
        "driver": "facetimehd",
        "status": "investigation",
        "firmware_required": True,
        "architectures": ["x86_64"],
    },
}

DRIVER_SOURCES = {
    "facetimehd": {
        "upstream": "https://github.com/patjak/facetimehd",
        "firmware": "https://github.com/patjak/facetimehd-firmware",
        "module": "facetimehd",
    }
}
