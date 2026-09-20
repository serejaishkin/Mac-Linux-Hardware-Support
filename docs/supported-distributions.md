# Supported Linux Distributions

Distribution support is modeled independently from Apple hardware support and from kernel support.

| Family | Ecosystem | Native manager | Version model | Current evidence |
|---|---|---|---|---|
| Debian | DEB | apt-get | 11/12/13 | catalog/untested |
| Ubuntu | DEB | apt-get | 20.04/22.04/24.04/26.04 | primary validation target |
| Linux Mint | DEB | apt-get | 20/21/22 | catalog/untested |
| Fedora | RPM | dnf | 40–43 | catalog/untested |
| RHEL | RPM | dnf | 8–10 | catalog/untested |
| ALT Linux | RPM | apt-get (apt-rpm) | p10/p11 | primary validation target |
| Arch Linux | Arch | pacman | rolling | catalog/untested |
| Manjaro | Arch | pacman | rolling | catalog/untested |
| openSUSE | RPM | zypper | Leap/Tumbleweed | catalog/untested |
| Alpine | apk | apk | 3.19–3.23 | catalog/untested |
| Gentoo | ebuild | emerge | rolling | catalog/untested |
| Other | native/generic | detected manually | unknown | unknown |

## Important distinction

The table describes platform **catalog coverage**, not hardware compatibility.

For every platform the engine must also determine:

1. exact distro version;
2. running kernel release;
3. kernel build tree and configuration;
4. CPU architecture;
5. compiler/build tools;
6. package manager availability;
7. driver recipe compatibility.

No distro is marked fully supported merely because its package manager is recognized.
