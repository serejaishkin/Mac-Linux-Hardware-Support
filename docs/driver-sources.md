# Driver Sources

The project covers the **whole Apple hardware stack**, not only camera and audio.

The key rule is to distinguish three cases:

1. **Already in Linux mainline** — we do not fork the driver. We detect it, validate model quirks, kernel compatibility, firmware and packaging.
2. **Out-of-tree open-source driver** — we integrate it through a controlled source manifest, kernel compatibility layer and distribution adapter.
3. **Firmware/configuration only** — we manage detection, acquisition instructions, validation and installation without redistributing proprietary blobs.

## Current source map

| Area | Linux component | Source type | Project work |
|---|---|---|---|
| Camera | facetimehd | external | firmware, kernel compatibility, DKMS, V4L2 |
| Wi-Fi | brcmfmac / model-dependent wl | mainline/external | PCI mapping, firmware, conflicts, distro packaging |
| Bluetooth | btusb / Broadcom support | mainline + firmware | firmware and power/resume quirks |
| Audio | snd-hda-intel + Cirrus | mainline/external | codec quirks, PipeWire profiles, kernel compatibility |
| Keyboard | hid-apple | mainline | model detection and quirks |
| Trackpad | bcm5974 / applespi | mainline | bus detection and model quirks |
| SMC | applesmc | mainline | sensors, fans, battery and thermal integration |
| GPU | i915 / amdgpu | mainline | model detection, firmware and display validation |
| Backlight | Linux backlight subsystem | mainline | Apple model quirks |
| Storage | nvme / ahci | mainline | APST/quirk detection where required |
| Thunderbolt | thunderbolt | mainline | controller/security/runtime validation |
| SPI/I2C | Intel LPSS and related drivers | mainline | platform dependency detection |
| Suspend/resume | kernel PM + platform drivers | mainline + quirks | automated regression tests |
| Sensors | hwmon / IIO / HID sensor | mainline | sensor mapping |
| T1/T2 bridges | apple-bce / related projects | external/model-specific | only on hardware that actually has the bridge |

## Important

A row in this table is a **source to investigate**, not a claim that every Mac model supports it.

The hardware database decides which driver applies to a specific machine.
