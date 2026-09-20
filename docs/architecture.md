# Architecture

## Layer model

```text
                 maclinux CLI
                      |
        +-------------+-------------+
        |                           |
   Detection                    Diagnostics
        |                           |
        +-------------+-------------+
                      |
               Hardware Database
                      |
             Driver Integration
                      |
          Kernel Compatibility Layer
                      |
        +-------------+-------------+
        |                           |
    Firmware                 Distribution Adapter
                                    |
       +----------+---------+-------+-------+
       |          |         |       |       |
      DEB       RPM       ALT     Arch    Generic
```

## Core rule

Hardware detection, compatibility decisions and driver metadata must not depend on APT, DNF, pacman or another package manager.

Distribution adapters translate a generic installation plan into native package/build operations.

## Driver strategy

The project should normally integrate an existing Linux driver instead of reimplementing a driver from scratch. A driver integration can contain upstream source reference, compatibility patches, firmware tooling, DKMS/module packaging, build rules, diagnostics and tests.

## Compatibility

Compatibility is evaluated across Mac model × device × architecture × kernel × distribution × driver version × firmware state.

Suggested states: supported, supported-with-quirks, patch-required, build-failure, firmware-required, unsupported, not-tested.
