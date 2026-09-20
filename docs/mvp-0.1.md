# MVP 0.1 — Detection, diagnostics and compatibility planning

## Implemented

- Dependency-free Python core.
- DMI Mac model detection.
- PCI discovery through `lspci -nn`.
- Registry entry for Broadcom FaceTime HD PCI ID `14e4:1570`.
- Detection of loaded `facetimehd` module.
- Detection of FaceTime HD firmware directories.
- Distribution/package-manager detection.
- `maclinux detect --json`.
- `maclinux diagnose`.
- `maclinux plan`.
- Kernel build-tree check.
- Architecture check.
- DKMS availability check.
- UEFI Secure Boot state check when exposed through EFI variables.

## External components identified

The upstream FaceTime HD driver is `patjak/facetimehd`. Its current repository metadata declares module `facetimehd`, version `0.7.0.1`, and blacklists `bdc_pci`. Its Makefile builds against the kernel module build directory.

The companion `patjak/facetimehd-firmware` repository provides firmware extraction/download tooling and Debian packaging metadata.

## Important limitation

The project does **not** copy the upstream driver into this repository. It records the integration and performs detection/diagnostics/planning. This keeps licensing, provenance and upstream update handling explicit.

## Next implementation stage

1. Add a distribution adapter interface.
2. Implement Ubuntu/Debian adapter.
3. Implement ALT Linux adapter.
4. Implement RPM and Arch adapters.
5. Add kernel compatibility rules for facetimehd.
6. Add safe firmware acquisition workflow without bundling proprietary firmware.
7. Add DKMS/native module installation.
8. Add V4L2 functional validation.
9. Add hardware-test result format.
