# MVP 1.0 — Native Package Build Boundary

The package engine now has a second stage after recipe generation:

`validated .ko -> PackageArtifact -> backend recipe -> staging -> native package builder`

## Safety

Package building is not installation. The package builder:

- never calls apt, dnf, pacman, zypper, apk or emerge;
- never installs a package;
- never loads a kernel module;
- never changes DKMS state;
- requires explicit `execute=True` / a future CLI `--execute`;
- stages modules in an isolated temporary directory.

## Current native builds

| Ecosystem | Current behavior |
|---|---|
| generic | native tar bundle |
| Debian/Ubuntu | native DEB build via `dpkg-deb` |
| RPM | canonical spec + staged modules; distro build context still required |
| Arch | canonical PKGBUILD + staged modules; build context still required |
| Alpine | canonical APKBUILD + staged modules; build context still required |
| Gentoo | canonical ebuild + staged modules; build context still required |

This deliberately does not claim that a generated RPM/PKGBUILD/APKBUILD/ebuild is
already distribution-valid. Each ecosystem still needs a fixture build in its own
supported version matrix.

## Kernel ABI boundary

The package artifact remains tied to an exact kernel release and source fingerprint.
A future package index will additionally record vermagic, compiler identity,
Module.symvers fingerprint and module CRC data.
