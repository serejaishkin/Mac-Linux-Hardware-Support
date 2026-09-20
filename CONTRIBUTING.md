# Contributing

Thanks for contributing to Mac Linux Hardware Support.

## Principles

- Prefer upstream Linux drivers and fixes.
- Do not copy proprietary Apple driver code.
- Keep hardware-specific knowledge in metadata where possible.
- Keep package-manager logic outside the hardware/driver core.
- Document kernel and distribution assumptions.
- Prefer reproducible diagnostics over manual guesswork.
- Do not claim hardware support without a reproducible test result.

## Repository structure

```text
database/     Hardware and driver metadata
docs/         Architecture and development documentation
drivers/      Driver integrations and compatibility work
firmware/     Firmware tooling and documentation
installer/    Distribution/package adapters
tools/        Detection, diagnostics and tests
tests/        Automated and hardware-integration tests
```

## Testing

Every hardware change should identify the Mac model, Linux distribution, kernel version, architecture, device identifier where available, test procedure and observed result.

Do not mark a component as supported merely because it builds.

## Pull requests

Keep changes focused. Explain the hardware, kernel and distribution combinations that were tested.
