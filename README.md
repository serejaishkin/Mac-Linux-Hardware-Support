# Mac Linux Hardware Support

Universal hardware compatibility and support stack for Apple hardware on Linux.

The project is not a Boot Camp replacement and not a Linux distribution. Its goal is to make Apple hardware work reliably on Linux by combining existing upstream drivers, firmware handling, kernel compatibility, diagnostics, packaging and hardware-specific knowledge.

## Goals

- Detect Apple hardware and identify the exact Mac model.
- Reuse and improve existing Linux/open-source drivers instead of duplicating them.
- Handle firmware extraction, validation and installation where appropriate.
- Track Linux kernel compatibility and required patches.
- Provide diagnostics and repair workflows.
- Support multiple Linux distributions and package ecosystems.
- Maintain a machine-readable hardware compatibility database.
- Build reproducible packages and DKMS/modules where appropriate.
- Test across real Apple hardware and supported Linux kernels.

## Initial target

The first reference platform is **MacBookPro11,1** (Late 2013 / 13-inch Retina).

Initial hardware areas: FaceTime HD camera, Broadcom Wi-Fi/Bluetooth, Cirrus audio, Intel Iris 5100 graphics, keyboard/trackpad, SMC, battery, thermal, backlight, NVMe, Thunderbolt and suspend/resume.

The current implementation milestone is the hardware compatibility engine: inventory, exact hardware identification and model-aware driver resolution across the full Apple hardware stack. Camera support is only one integration among many.

## Architecture

1. Hardware database
2. Driver integrations
3. Firmware handling
4. Kernel compatibility
5. Distribution adapters
6. Diagnostics
7. Test matrix

A core design rule is that hardware logic must not depend on a particular package manager.

## Supported ecosystems

- Debian / Ubuntu — APT / DEB
- ALT Linux — apt-rpm / RPM
- Fedora / RHEL-like — DNF / RPM
- Arch Linux — pacman
- openSUSE — zypper / RPM
- Alpine — apk
- Gentoo — ebuild
- Generic/manual installation

These are architectural targets; listing an ecosystem does not mean every driver is already supported there.

## Architectures

The project is designed for x86_64, aarch64, armv7, riscv64, ppc64le and other architectures where the hardware and driver permit it.

## CLI direction

```text
maclinux detect
maclinux diagnose
maclinux repair camera
maclinux repair wifi
maclinux test
```

## Project status

Early architecture / MVP stage. The repository currently focuses on the foundation: hardware metadata, driver manifests, distribution abstraction and testing strategy.

## Contributing

See CONTRIBUTING.md.

## Security

See SECURITY.md.

## License

A project license has not yet been selected. Until a license is added, repository contents are not granted additional reuse rights beyond applicable GitHub functionality.
