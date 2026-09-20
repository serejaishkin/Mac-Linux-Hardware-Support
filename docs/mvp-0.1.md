# MVP 0.2 — Hardware inventory and driver resolution

## Implemented in 0.2

- Unified normalized hardware records for the resolver.
- PCI discovery through `lspci -nnk`, including bound kernel driver/module data when available.
- USB discovery through `lsusb`.
- Loaded-kernel-module inventory through `/proc/modules`.
- Sysfs bus inventory through `/sys/bus`.
- Exact PCI IDs take precedence over model-level guesses.
- Model-aware component catalog for the reference MacBookPro11,1.
- Driver candidate resolution across camera, Wi-Fi, Bluetooth, audio, keyboard, trackpad, SMC/thermal, graphics, storage, Thunderbolt and power.
- `maclinux inventory` for machine-readable normalized hardware inventory.
- `maclinux resolve` for machine-readable driver candidates.
- Existing `maclinux diagnose` and `maclinux plan` now use the resolver.
- Repair remains disabled until distribution adapters and functional validation are implemented.

## Design rules

1. Mainline drivers are preferred where the kernel already provides the subsystem.
2. Exact hardware IDs outrank model-name assumptions.
3. External drivers are treated as integrations, not copied into this repository.
4. Firmware is checked separately from driver selection.
5. Secure Boot is a compatibility constraint for external modules.
6. Detection and resolution remain distribution-neutral.
7. Installation must not happen merely because a candidate driver exists.

## Next stage: distribution-neutral installation planning

1. Define a common package/module adapter interface.
2. Implement read-only Ubuntu/Debian APT/DEB planning.
3. Implement read-only ALT apt-rpm/RPM planning.
4. Add Fedora/RPM, Arch/pacman and openSUSE/zypper adapters.
5. Add Alpine/apk and Gentoo/ebuild adapters.
6. Add kernel-version rules and driver provenance metadata.
7. Add firmware acquisition/validation plans without bundling proprietary Apple blobs.
8. Add functional test definitions for each hardware component.
9. Add fixture-based detection tests for real Mac inventories.
10. Only then enable privileged repair workflows.

## Important limitation

The project does not copy upstream Linux drivers into this repository. The compatibility engine records which driver should be considered and why; actual installation remains a separate, auditable stage.
