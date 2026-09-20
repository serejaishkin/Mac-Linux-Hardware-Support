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
    "8086:0a2e": {
        "id": "i915-haswell-ult",
        "name": "Intel Haswell-ULT Iris Graphics 5100",
        "component": "graphics",
        "class": "display",
        "driver": "i915",
        "source": "mainline",
        "status": "mainline-integration",
        "architectures": ["x86_64"],
    },
    "8086:0a0c": {
        "id": "intel-haswell-ult-hda",
        "name": "Intel Haswell-ULT HD Audio Controller",
        "component": "audio",
        "class": "multimedia",
        "driver": "snd-hda-intel",
        "source": "mainline",
        "status": "mainline-integration",
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
        "camera": {"drivers": ["facetimehd"], "notes": ["PCI 14e4:1570 is the known FaceTime HD integration; firmware/calibration remains separate."]},
        "wifi": {"drivers": ["broadcom-wl"], "notes": ["For BCM4360 14e4:43a0 the Linux Wireless table maps the device to wl; exact subsystem/revision must still be detected."]},
        "bluetooth": {"drivers": ["btusb", "bluetooth-broadcom"], "notes": ["Resolve from USB identity and firmware state."]},
        "audio": {"drivers": ["snd-hda-intel", "snd-hda-codec-cirrus"], "notes": ["MacBookPro11,1 uses Cirrus CS4208; use the mainline mbp11 fixup first. snd_hda_macbookpro targets CS8409 systems and is not a default recipe for this model."]},
        "keyboard": {"drivers": ["hid-apple"], "notes": ["MacBookPro11,1 is a pre-SPI-Apple-keyboard generation; confirm actual HID topology."]},
        "trackpad": {"drivers": ["bcm5974"], "notes": ["MacBookPro11,1 uses the older USB Apple multi-touch path; confirm actual USB topology."]},
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
