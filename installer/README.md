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

The first adapter implementation will be read-only planning: it reports required packages and commands without changing the system. Actual installation will be a separate privileged operation after compatibility checks pass.
