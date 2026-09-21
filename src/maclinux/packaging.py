"""Distribution-neutral package planning and artifact generation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol
import hashlib, json

@dataclass(frozen=True)
class PackageArtifact:
    driver: str
    package_name: str
    package_version: str
    ecosystem: str
    architecture: str
    kernel_release: str
    source_sha256: str
    modules: tuple[str, ...]
    dependencies: tuple[str, ...] = ()
    firmware: tuple[str, ...] = ()
    files: tuple[tuple[str, str], ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    @property
    def artifact_id(self) -> str:
        data = json.dumps({"driver":self.driver,"package":self.package_name,"version":self.package_version,
            "ecosystem":self.ecosystem,"arch":self.architecture,"kernel":self.kernel_release,
            "source":self.source_sha256,"modules":self.modules}, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()[:16]
    def to_dict(self) -> dict:
        return {"driver":self.driver,"package_name":self.package_name,"package_version":self.package_version,
            "ecosystem":self.ecosystem,"architecture":self.architecture,"kernel_release":self.kernel_release,
            "source_sha256":self.source_sha256,"modules":list(self.modules),"dependencies":list(self.dependencies),
            "firmware":list(self.firmware),"files":[list(x) for x in self.files],"metadata":dict(self.metadata),
            "artifact_id":self.artifact_id}

@dataclass(frozen=True)
class PackagePlan:
    ecosystem: str
    packages: tuple[str, ...]
    commands: tuple[str, ...]
    notes: tuple[str, ...] = ()
    module_commands: tuple[str, ...] = ()
    def to_dict(self) -> dict:
        return {"ecosystem":self.ecosystem,"packages":list(self.packages),"commands":list(self.commands),
                "module_commands":list(self.module_commands),"notes":list(self.notes)}

@dataclass(frozen=True)
class BackendOutput:
    ecosystem: str
    package_format: str
    recipe_path: str
    recipe: str
    build_commands: tuple[str, ...]
    notes: tuple[str, ...] = ()
    def to_dict(self) -> dict:
        return {"ecosystem":self.ecosystem,"package_format":self.package_format,"recipe_path":self.recipe_path,
                "recipe":self.recipe,"build_commands":list(self.build_commands),"notes":list(self.notes)}

class PackageBackend(Protocol):
    ecosystem: str
    package_format: str
    def render(self, artifact: PackageArtifact) -> BackendOutput: ...

def _header(a):
    return (f"# maclinux package: {a.package_name}\n# driver: {a.driver}\n"
            f"# source-sha256: {a.source_sha256}\n# kernel: {a.kernel_release}\n"
            f"# architecture: {a.architecture}\n# artifact-id: {a.artifact_id}\n")

class DebBackend:
    ecosystem, package_format = "deb", "deb"
    def render(self,a):
        deps=", ".join(a.dependencies) or "dkms"
        r=_header(a)+(f"Package: {a.package_name}\nVersion: {a.package_version}\nArchitecture: {a.architecture}\n"
          f"Depends: {deps}\n\nDescription: Apple hardware driver managed by maclinux\n"
          f"X-MacLinux-Modules: {', '.join(a.modules)}\nX-MacLinux-Firmware: {', '.join(a.firmware)}\n")
        return BackendOutput("deb","deb",f"debian/{a.package_name}.control",r,("dpkg-buildpackage -us -uc",),
          ("DEB metadata is generated here; DKMS/source integration is a separate stage.",))

class RpmBackend:
    ecosystem, package_format = "rpm", "rpm"
    def render(self,a):
        req="".join(f"Requires: {d}\n" for d in a.dependencies)
        r=_header(a)+(f"Name: {a.package_name}\nVersion: {a.package_version}\nRelease: 1%{{?dist}}\n"
          "Summary: Apple hardware driver managed by maclinux\n"
          f"License: {a.metadata.get('license','GPL-2.0-or-later')}\nBuildArch: {a.architecture}\n{req}\n"
          "%description\nApple hardware driver package.\n\n%files\n"+f"# modules: {', '.join(a.modules)}\n")
        return BackendOutput("rpm","rpm",f"{a.package_name}.spec",r,(f"rpmbuild -bb {a.package_name}.spec",))

class ArchBackend:
    ecosystem, package_format = "arch", "pkg.tar.zst"
    def render(self,a):
        deps=" ".join(repr(x) for x in a.dependencies)
        r=_header(a)+(f"pkgname={a.package_name}\npkgver={a.package_version}\npkgrel=1\n"
          f"arch=('{a.architecture}')\ndepends=({deps})\n\npackage() {{\n  # modules: {', '.join(a.modules)}\n}}\n")
        return BackendOutput("arch","pkg.tar.zst","PKGBUILD",r,("makepkg --syncdeps --cleanbuild",))

class ApkBackend:
    ecosystem, package_format = "apk", "apk"
    def render(self,a):
        r=_header(a)+(f"pkgname={a.package_name}\npkgver={a.package_version}\npkgrel=0\narch={a.architecture}\n"
          f"depends=\"{' '.join(a.dependencies)}\"\nbuild() {{ :; }}\npackage() {{\n  # modules: {', '.join(a.modules)}\n}}\n")
        return BackendOutput("apk","apk","APKBUILD",r,("abuild checksum","abuild -r"))

class GentooBackend:
    ecosystem, package_format = "gentoo", "ebuild"
    def render(self,a):
        r=_header(a)+("EAPI=8\nDESCRIPTION=\"Apple hardware driver managed by maclinux\"\n"
          f"PN=\"{a.package_name}\"\nPV=\"{a.package_version}\"\nS=\"${WORKDIR}\"\n"
          "src_compile() {\n  # matching kernel build tree supplied by maclinux\n"
          f"  # modules: {', '.join(a.modules)}\n}}\n")
        return BackendOutput("gentoo","ebuild",f"{a.package_name}-{a.package_version}.ebuild",r,
          (f"ebuild {a.package_name}-{a.package_version}.ebuild merge",))

class GenericBackend:
    ecosystem, package_format = "generic", "tar"
    def render(self,a):
        return BackendOutput("generic","tar","maclinux-manifest.json",json.dumps(a.to_dict(),indent=2,sort_keys=True),
          (f"tar -C <staging> -czf {a.package_name}-{a.package_version}.tar.gz .",),
          ("Generic output is a manifest/bundle plan; it is not an install operation.",))

_BACKENDS={"deb":DebBackend(),"rpm":RpmBackend(),"alt":RpmBackend(),"rpm-zypper":RpmBackend(),
           "arch":ArchBackend(),"apk":ApkBackend(),"gentoo":GentooBackend(),"generic":GenericBackend()}

def get_package_backend(ecosystem):
    try: return _BACKENDS[ecosystem]
    except KeyError as e: raise ValueError(f"unsupported package ecosystem: {ecosystem}") from e

def render_package(artifact): return get_package_backend(artifact.ecosystem).render(artifact)

def package_plan(distribution, driver, source="external"):
    d=distribution.lower()
    if d in {"ubuntu","debian","linuxmint","pop"}:
        e="deb"; p=("dkms","git","build-essential","linux-headers-$(uname -r)") if driver=="facetimehd" else ("linux-headers-$(uname -r)",)
        c=("sudo apt-get update","sudo apt-get install "+" ".join(p)); n=("Firmware is a separate acquisition step; proprietary firmware is not bundled.",)
    elif d in {"alt","altlinux"}:
        e="alt"; p=("kernel-headers","gcc","make","dkms") if driver=="facetimehd" else ("kernel-headers",)
        c=("apt-get update","apt-get install "+" ".join(p)); n=("Exact ALT package names must be verified against the target branch.",)
    elif d in {"fedora","rhel","centos","rocky","almalinux"}:
        e="rpm"; p=("kernel-devel","kernel-headers"); c=("sudo dnf install kernel-devel kernel-headers",); n=("DKMS availability depends on enabled repositories.",)
    elif d=="arch" or d.startswith("manjaro"):
        e="arch"; p=("base-devel","linux-headers"); c=("sudo pacman -S base-devel linux-headers",); n=()
    elif d in {"opensuse-tumbleweed","opensuse-leap","opensuse"}:
        e="rpm-zypper"; p=("kernel-default-devel","kernel-devel"); c=("sudo zypper install kernel-default-devel kernel-devel",); n=()
    elif d=="alpine":
        e="apk"; p=("build-base","linux-headers","dkms"); c=("sudo apk add build-base linux-headers dkms",); n=()
    elif d=="gentoo":
        e="gentoo"; p=("sys-kernel/linux-headers",); c=("sudo emerge sys-kernel/linux-headers",); n=("Kernel source/configuration must match the running kernel.",)
    else:
        e="generic"; p=("kernel development headers",); c=("Install the matching kernel development package using the distribution's package manager.",); n=("No automatic installation is supported for this distribution yet.",)
    return PackagePlan(e,tuple(p),tuple(c),tuple(n))

def repair_transaction(plan, *, dry_run=True):
    return {"mode":"dry-run" if dry_run else "blocked","safe_to_execute":False,
      "commands":list(plan.commands)+list(plan.module_commands),
      "rollback":"restore package/module state from the recorded preflight snapshot",
      "preflight":["re-detect model, architecture and kernel","verify package-manager availability",
                   "verify matching kernel development files","verify driver architecture compatibility",
                   "verify firmware state separately","record current driver/module bindings"],
      "reason":"Privileged repair execution is not enabled yet."}
