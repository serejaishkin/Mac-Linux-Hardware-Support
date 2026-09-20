# Driver Development Strategy

## Do not create one giant Mac driver

Mac Linux Hardware Support is a compatibility and orchestration layer.

PCI/USB/ACPI/DMI -> hardware identity -> driver selection -> kernel compatibility -> distribution adapter -> functional test.

## Mainline-first

If Linux already contains the required driver, the project should not copy its source.

Examples include i915, amdgpu, nvme, thunderbolt, applesmc, applespi, hid-apple, bcm5974, snd-hda-intel and brcmfmac.

The project adds the missing Apple-specific knowledge around them.

## External-driver integrations

Examples: facetimehd, snd_hda_macbookpro where applicable, and model-specific SPI/bridge drivers where mainline support is insufficient.

External drivers must be pinned to a known source revision before automated installation.

## Firmware

Firmware is never assumed to be bundled. Classify it as distro-provided, redistributable, extractable from Apple software, user-provided, missing or incompatible.

## Kernel compatibility

Compatibility rules must come from actual build/test evidence rather than guesses.

## Testing levels

- detection
- module binding
- firmware loading
- functional operation
- suspend/resume
- kernel update/rebuild
- distribution packaging
