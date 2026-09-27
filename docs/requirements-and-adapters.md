# Driver requirements and distribution adapters

Driver recipes declare logical build requirements such as:

- `compiler`
- `make`
- `kernel-devel`
- `kernel-headers`
- `dkms`
- `git`
- `v4l2`
- `firmware-tools`

`installer/requirements.py` translates these logical names into distribution packages. The adapter layer renders package-manager commands, but never executes them.

## Current mappings

| Ecosystem | Package manager | Examples |
|---|---|---|
| Debian / Ubuntu | apt | `build-essential`, `linux-headers-$(uname -r)`, `dkms` |
| ALT Linux | apt-rpm | `gcc`, `make`, `kernel-headers`, `dkms` |
| Fedora / RHEL-like | dnf | `gcc`, `kernel-devel`, `kernel-headers`, `dkms` |
| Arch / derivatives | pacman | `base-devel`, `linux-headers`, `dkms` |
| openSUSE | zypper | `gcc`, `kernel-default-devel`, `dkms` |
| Alpine | apk | `build-base`, `linux-headers`, `dkms` |
| Gentoo | emerge | Gentoo package atoms such as `sys-devel/gcc` and `sys-kernel/dkms` |
| unknown | generic | no automatic package mapping |

These names are planning candidates, not proof that a package exists in every repository or branch. Kernel development package naming is especially distribution- and kernel-branch-dependent.

## Design rule

A driver recipe must not contain package-manager commands.

Intended flow:

```text
driver recipe
    ↓
logical requirements
    ↓
RequirementMapper
    ↓
distribution adapter
    ↓
read-only PackagePlan
```

This keeps hardware and driver logic independent from package ecosystems.

## Safety

The adapter layer is planning-only. It returns commands as data and does not invoke a shell or package manager.

Privileged repair remains disabled until preflight, transaction logging, rollback and post-install functional validation are complete.