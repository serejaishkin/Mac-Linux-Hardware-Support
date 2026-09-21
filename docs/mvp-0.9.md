# MVP 0.9 — Package Engine

MVP 0.9 introduces a common package-artifact model and distribution backend interface.
Package generation is separate from installation.

Pipeline:

detect -> resolve -> build -> validate artifact -> package artifact -> package build -> install (future)

## Common artifact

Every package artifact carries driver and package name/version, package ecosystem,
CPU architecture, exact target kernel release, source SHA-256, module list,
dependencies, firmware requirements, provenance metadata and a deterministic artifact ID.

## Backends

| Ecosystem | Backend | Output |
|---|---|---|
| Debian/Ubuntu | DebBackend | DEB metadata/build recipe |
| Fedora/RHEL/ALT/openSUSE | RpmBackend | RPM spec/build recipe |
| Arch | ArchBackend | PKGBUILD |
| Alpine | ApkBackend | APKBUILD |
| Gentoo | GentooBackend | ebuild |
| Unknown/generic | GenericBackend | manifest + tar bundle plan |

ALT and openSUSE keep separate ecosystem identifiers even when using RPM format.

## Safety boundary

The Package Engine does not install packages, run package managers, load modules,
modify DKMS state, sign kernel modules or download proprietary firmware.

A generated recipe is not proof that the target distribution accepts the package.
Actual package builds, distro-specific dependencies, DKMS integration, signing and
functional hardware tests remain separate validation gates.
