# Development

## Workflow

1. Detect the physical Mac model.
2. Collect PCI, USB, ACPI and DMI information.
3. Identify the exact device and existing Linux driver.
4. Check kernel compatibility.
5. Check firmware requirements.
6. Build/install through the appropriate distribution adapter.
7. Run a functional hardware test.
8. Record the result in the compatibility database.

## Useful diagnostics

```bash
uname -a
cat /sys/devices/virtual/dmi/id/product_name
cat /sys/devices/virtual/dmi/id/product_version
lspci -nn
lsusb
dmesg
journalctl -k
v4l2-ctl --list-devices
lsmod
```

Hardware-dependent tests require real Apple machines. CI can additionally cover build-only compatibility.


## Distribution adapters

The installer layer is intentionally separated from hardware detection.

Current adapters:

- `apt` — Debian/Ubuntu-family planning.
- `apt-rpm` — ALT Linux planning.
- `generic` — fallback when no supported distribution is detected.

Use:

```bash
maclinux install-plan
```

The command is strictly read-only. It produces a machine-readable package/header plan and never invokes a package manager.

### Adapter rules

- Hardware modules must not call `apt`, `dnf`, `pacman`, or another package manager directly.
- An adapter may translate logical requirements into distribution-specific package names and commands.
- Commands are output as a plan, not executed.
- Kernel header/devel package names must be validated against the actual distribution and kernel packaging.
- External drivers must trigger DKMS/header requirements only when the selected integration actually needs them.
- Mainline-only components should not cause unnecessary DKMS installation.

The next adapter work is Fedora/RPM, Arch/pacman and openSUSE/zypper, followed by Alpine and Gentoo.
