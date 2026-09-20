# MVP 0.1 — Detection and FaceTime HD diagnostics

## Implemented

- Python package with dependency-free Linux detection.
- DMI Mac model detection.
- PCI device discovery through `lspci -nn`.
- Registry entry for Broadcom FaceTime HD PCI ID `14e4:1570`.
- Detection of loaded `facetimehd` module.
- Detection of installed FaceTime HD firmware directories.
- Distribution/package-manager detection.
- `maclinux detect --json`.
- `maclinux diagnose`.

## External components identified

The upstream FaceTime HD driver is the `patjak/facetimehd` project. Its current DKMS metadata declares module `facetimehd`, version `0.7.0.1`, and blacklists `bdc_pci`. Its Makefile builds against the running kernel's module build directory.

The companion `patjak/facetimehd-firmware` repository provides firmware extraction/download tooling and a Debian packaging template.

## Important limitation

The project does **not** copy the upstream driver into this repository at this stage. It records the integration and performs detection/diagnostics. This keeps licensing, provenance and upstream update handling explicit.

## Next step

Implement a distribution-neutral installation plan:

1. detect kernel headers/build tree;
2. detect Secure Boot/module-signing state;
3. select a supported facetimehd source revision;
4. prepare firmware;
5. build a DKMS or kernel module;
6. install it through a distro adapter;
7. load the module;
8. validate V4L2 and camera device nodes;
9. record the result.
