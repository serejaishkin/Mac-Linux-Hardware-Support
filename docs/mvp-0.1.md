# MVP 0.3 — Non-invasive hardware validation

## Implemented in 0.3

- Added a distribution-neutral functional validation framework in `src/maclinux/validation.py`.
- Added normalized test results with `pass`, `fail`, `skip` and `unknown` states.
- Added component checks for camera/V4L2, audio/ALSA, Wi-Fi, Bluetooth, DRM/DRI graphics, keyboard/trackpad input, storage, Thunderbolt, SMC/thermal and CPU power.
- Optional command checks are used only when the relevant utility is installed.
- Validation reads sysfs/proc/device state and does not install packages, load modules, alter configuration or trigger suspend.
- Added `database/tests/catalog.yaml` as the declarative test catalog.
- Added `maclinux test [component]` and `maclinux test --json`.
- Added fixture-independent unit tests that remain runnable on ordinary CI hosts.

## Validation policy

1. A visible device node or subsystem is evidence of exposure, not proof of complete functionality.
2. Missing optional tools produce `skip`, not a false failure.
3. Firmware is not declared loaded merely because a firmware file exists.
4. Suspend/resume is currently capability-only; the framework never suspends the test machine automatically.
5. Functional validation is read-only and requires no root privileges.
6. Exact hardware/driver resolution remains separate from functional validation.

## Component coverage

| Component | Current checks |
|---|---|
| Camera | V4L2 device nodes, `v4l2-ctl --list-devices` |
| Audio | ALSA cards, `aplay -l` |
| Wi-Fi | wireless sysfs interface, `iw dev` |
| Bluetooth | Bluetooth controller sysfs |
| Graphics | DRM cards, DRI nodes, optional `glxinfo -B` |
| Keyboard | Linux input subsystem |
| Trackpad | Linux input subsystem |
| Storage | block devices |
| Thunderbolt | Thunderbolt sysfs |
| SMC/thermal | hwmon, thermal zones, Apple SMC platform device |
| Power | CPU cpufreq policy |

## Next stage: real hardware validation and installation adapters

1. Add model-specific fixtures for Apple hardware inventories.
2. Correlate resolved driver/module binding with each functional test.
3. Add conservative firmware-state evidence from kernel/sysfs sources.
4. Add distribution-specific package/module adapters for Ubuntu/Debian, ALT, Fedora/RPM, Arch, openSUSE, Alpine and Gentoo.
5. Add explicit kernel compatibility rules per driver and architecture.
6. Add safe repair transactions with dry-run, backup and rollback.
7. Add real Mac hardware CI/manual test reports where physical hardware is available.

## Important limitation

The project still does not copy upstream Linux drivers into the repository and does not automatically modify the host. The test framework establishes hardware exposure and functional evidence; it does not replace subsystem-specific tests or a human acceptance test on physical Macs.
