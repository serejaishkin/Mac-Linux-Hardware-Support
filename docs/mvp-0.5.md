# MVP 0.5 — Distribution adapters and safe repair planning

The project now has read-only package/module adapters for:

- Ubuntu / Debian — APT/DEB
- ALT Linux — apt-rpm
- Fedora-family RPM — DNF
- Arch-family — pacman
- openSUSE — zypper
- Alpine — apk
- Gentoo — emerge/ebuild

Adapters generate package prerequisites and module-load commands but never execute them.

## Safe repair transaction

`repair_transaction()` produces an auditable dry-run containing:

- preflight re-detection;
- package-manager availability;
- matching kernel development files;
- architecture compatibility;
- separate firmware verification;
- current driver/module bindings;
- proposed package/module commands;
- rollback requirement.

`maclinux repair <component>` currently prints this transaction plan. It does **not** install packages, load modules, overwrite firmware, or change configuration.

## Next

The next implementation stage is real transaction execution with explicit opt-in, backups, dependency checks, post-install functional validation and rollback. Privileged execution should remain disabled until those pieces exist.
