# Architecture

## Layer model

```text
                     maclinux CLI
                         |
        +----------------+----------------+
        |                |                |
    Detection        Resolution      Diagnostics
        |                |                |
        +----------------+----------------+
                         |
                  Hardware identity
                         |
                  Driver/source registry
                         |
                Kernel compatibility
                         |
                 CPU architecture
                         |
              Linux platform/version
                         |
             Package ecosystem/manager
                         |
                 Build environment
                         |
                    Recipe/patch
                         |
                       Build
                         |
                     Artifact
                         |
                    Validation
```

## Core rule

Hardware detection and compatibility decisions must not depend on a particular package manager. A distribution adapter translates generic requirements into native package/build operations.

## Compatibility dimensions

The matrix is explicitly multi-dimensional:

**Mac model × exact device × Linux distribution × distribution version × package ecosystem × running kernel × kernel configuration/build tree × CPU architecture × driver/source revision × patchset × firmware state × Secure Boot state.**

Distro version and kernel version are never conflated. A single Ubuntu release may run several supported kernel lines.

## Driver strategy

Mainline Linux drivers are integrated by metadata, quirks, kernel requirements, diagnostics and validation. Their kernel source is not copied into this repository.

Out-of-tree drivers use a provenance record, compatibility recipe, optional patches, build requirements, output module names and validation rules.

## Build engine

MVP 0.7 introduces platform/kernel detection and a declarative recipe layer. The build command is dry-run by default. Explicit execution only builds; installation, module loading and signing remain separate operations.

## Support states

- `supported` — validated on the exact relevant matrix entry;
- `supported-with-quirks` — validated with documented limitations;
- `buildable` — local build prerequisites and recipe match, but hardware functionality is not proven;
- `patch-required` — kernel/source mismatch requires a patchset;
- `blocked` — required build environment or security prerequisite is missing;
- `build-failure` — an explicit build attempt failed;
- `firmware-required` — firmware input is missing or unverified;
- `unsupported` — known incompatibility;
- `unknown` — insufficient evidence;
- `not-tested` — no real hardware test result.

A recipe or package plan alone never upgrades a component to `supported`.
