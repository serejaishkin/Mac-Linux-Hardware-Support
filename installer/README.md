# Installer

Distribution-specific adapters.

The installer receives a distribution-neutral plan from the core and translates it into native package/build operations.

Planned adapters:

- `deb` — Debian / Ubuntu
- `alt` — ALT Linux apt-rpm
- `rpm` — Fedora / RHEL-like
- `arch` — Arch Linux
- `apk` — Alpine
- `gentoo` — Gentoo
- `generic` — manual/source workflow

Adapters must not contain Apple hardware detection logic.

The first adapter implementation is read-only planning in `src/maclinux/packaging.py`. It reports the package ecosystem, required development packages and example commands without changing the system. Ubuntu/Debian, ALT, RPM/DNF, Arch, openSUSE, Alpine and Gentoo are represented; package names remain conservative because exact kernel package names vary by release. Actual installation will be a separate privileged operation after compatibility checks and functional tests pass.
