# Supported Linux Distributions

The project separates distribution support from hardware support.

| Family | Package ecosystem | Adapter |
|---|---|---|
| Debian | APT / DEB | deb |
| Ubuntu | APT / DEB | deb |
| ALT Linux | apt-rpm / RPM | alt |
| Fedora | DNF / RPM | rpm |
| RHEL-like | DNF / RPM | rpm |
| Arch Linux | pacman | arch |
| openSUSE | zypper / RPM | rpm |
| Alpine | apk | apk |
| Gentoo | ebuild | gentoo |
| Other | manual/native | generic |

Initial real-world validation targets are Ubuntu and ALT Linux. Other distributions should use the same abstraction rather than creating distribution-specific driver logic.
