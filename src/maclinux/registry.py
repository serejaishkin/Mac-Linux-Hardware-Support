"""Dependency-free hardware and driver registry used by the compatibility engine."""

MODELS = {
    "MacBookPro11,1": {
        "vendor": "Apple",
        "family": "MacBook Pro",
        "generation": "Late 2013",
    },
}

# Exact hardware IDs take precedence over model guesses.
DEVICES = {
    "14e4:1570": {
        "id": "facetimehd",
        "name": "Broadcom 720p FaceTime HD Camera",
        "component": "camera",
        "class": "multimedia",
        "driver": "facetimehd",
        "source": "external",
        "status": "external-integration",
        "firmware_required": True,
        "architectures": ["x86_64"],
    },
    "14e4:43a0": {
        "id": "broadcom-bcm4360",
        "name": "Broadcom BCM4360 wireless",
        "component": "wifi",
        "class": "network",
        "driver": "detect-driver",
        "candidates": ["brcmfmac", "broadcom-wl"],
        "source": "model-dependent",
        "status": "id-dependent",
        "firmware_required": True,
        "architectures": ["x86_64"],
    },
}

MODEL_COMPONENTS = {
    "MacBookPro11,1": {
        "camera": {"drivers": ["facetimehd"], "notes": ["Exact camera ID and firmware must be validated."]},
        "wifi": {"drivers": ["brcmfmac", "broadcom-wl"], "notes": ["Select by exact PCI ID and kernel support; never install both blindly."]},
        "bluetooth": {"drivers": ["btusb", "bluetooth-broadcom"], "notes": ["Resolve from USB identity and firmware state."]},
        "audio": {"drivers": ["snd-hda-intel", "snd-hda-codec-cirrus", "snd_hda_macbookpro"], "notes": ["Mainline HDA/Cirrus first; external only after functional validation."]},
        "keyboard": {"drivers": ["hid-apple", "applespi"], "notes": ["Select from actual HID/SPI topology."]},
        "trackpad": {"drivers": ["bcm5974", "applespi"], "notes": ["Select from actual USB/SPI topology."]},
        "smc-thermal-fans": {"drivers": ["applesmc", "thermal"], "notes": ["Validate sensors, fan control and thermal zones separately."]},
        "graphics": {"drivers": ["i915"], "notes": ["Validate DRM acceleration, modesetting and backlight."]},
        "storage": {"drivers": ["nvme", "ahci"], "notes": ["Resolve from actual controller and block-device topology."]},
        "thunderbolt": {"drivers": ["thunderbolt"], "notes": ["Validate controller enumeration and security state."]},
        "power": {"drivers": ["intel-pstate", "thermal"], "notes": ["Validate cpufreq, thermal zones and suspend/resume."]},
    },
}

DRIVER_SOURCES = {
    "facetimehd": {"upstream": "https://github.com/patjak/facetimehd", "firmware": "https://github.com/patjak/facetimehd-firmware", "module": "facetimehd"},
    "brcmfmac": {"upstream": "https://wireless.docs.kernel.org/", "module": "brcmfmac"},
    "broadcom-wl": {"upstream": "https://www.broadcom.com/support/download-search", "module": "wl"},
    "applespi": {"upstream": "https://github.com/linux-surface/applespi", "module": "applespi"},
    "bcm5974": {"upstream": "https://docs.kernel.org/input/devices/bcm5974.html", "module": "bcm5974"},
    "applesmc": {"upstream": "https://docs.kernel.org/hwmon/applesmc.html", "module": "applesmc"},
}
