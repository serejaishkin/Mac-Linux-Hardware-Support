# MVP 0.8 — Kernel ABI and isolated builds

MVP 0.8 adds the build-integrity layer required before package generation.

## Implemented

- compiler identity from `include/generated/compile.h`;
- kernel release from the kernel build tree when available;
- `Module.symvers` parsing;
- undefined-symbol validation for built `.ko` files;
- kernel symbol CRC validation when module version metadata is available;
- isolated temporary build workspace;
- SHA-256 fingerprint of the supplied source tree;
- build artifact validation remains non-installing and non-loading.

## Build states

A successful compiler invocation is not enough to call a driver supported.

The pipeline is:

`source provenance → kernel ABI preflight → isolated build → ELF → vermagic → symbols → CRC → artifact`

Functional hardware testing and firmware validation are separate gates.

## Security

The build engine does not install, load, sign, or modify kernel modules. The temporary workspace is copied from the explicitly supplied source directory.

Automatic source download is intentionally not part of this MVP. Repository/revision/checksum metadata remains declarative until a dedicated acquisition layer is implemented.
