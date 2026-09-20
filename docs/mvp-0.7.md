# MVP 0.7 — Platform and Kernel Build Engine

## Goal

Move from a package/install abstraction to a reproducible decision chain:

Mac hardware -> exact device -> driver source -> kernel compatibility -> CPU architecture -> Linux distribution/version -> package ecosystem -> build environment -> recipe -> build artifact -> validation.

## Platform model

The project records separately:

- distribution ID and version;
- package ecosystem and native package manager;
- running kernel release;
- kernel build tree and configuration;
- compiler/build tools;
- CPU architecture.

Ubuntu 24.04 and a 6.8 kernel are therefore two different compatibility dimensions.

## Build states

- `buildable`: recipe and local prerequisites match;
- `blocked`: required build environment is absent;
- `patch-required`: recipe does not cover the detected kernel range;
- `unsupported`: hardware/architecture/distribution is outside the recipe;
- `unknown`: there is not enough evidence;
- `build-failed`: an explicit build was attempted and failed.

## Safety

`maclinux build <driver>` is dry-run by default. `--execute` only runs an allow-listed build command. It does not install, load, unload, sign, or modify kernel/module state.

Firmware remains a separate input. The existence of a firmware file is not treated as proof that the device can initialize.

## Current scope

The engine currently has recipes for selected external integrations (`facetimehd`, `applespi`, `snd_hda_macbookpro`). Mainline drivers remain represented as integrations rather than copied kernel source.

This is infrastructure, not a claim that every listed distro, kernel, Apple model, or driver is already tested.
