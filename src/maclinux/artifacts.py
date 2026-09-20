"""Validation of built Linux kernel module artifacts.

The validator is deliberately conservative: a .ko is only considered valid when
its ELF architecture, module name and kernel ABI metadata can be inspected.
Symbol/dependency checks are best-effort because tooling differs by distro.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class ArtifactResult:
    path: str
    status: str
    module: str
    architecture: str
    vermagic: str
    depends: tuple[str, ...]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    unresolved_symbols: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


def _run(args: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(args, text=True, capture_output=True, check=False, shell=False)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except OSError as exc:
        return 127, "", str(exc)


def _expected_elf_machine(architecture: str) -> str | None:
    return {
        "x86_64": "Advanced Micro Devices X86-64",
        "aarch64": "AArch64",
        "armv7l": "ARM",
        "riscv64": "RISC-V",
        "ppc64le": "PowerPC64",
        "s390x": "IBM S/390",
        "loongarch64": "LoongArch",
    }.get(architecture)


def _elf_machine(path: Path) -> str | None:
    readelf = shutil.which("readelf")
    if not readelf:
        return None
    rc, out, _ = _run([readelf, "-h", str(path)])
    if rc:
        return None
    match = re.search(r"^\s*Machine:\s*(.+)$", out, re.M)
    return match.group(1).strip() if match else None


def _undefined_symbols(path: Path) -> tuple[str, ...]:
    readelf = shutil.which("readelf")
    if not readelf:
        return ()
    rc, out, _ = _run([readelf, "-Ws", str(path)])
    if rc:
        return ()
    values = []
    for line in out.splitlines():
        fields = line.split()
        if len(fields) >= 8 and fields[6] == "UND":
            values.append(fields[7])
    return tuple(sorted(set(values)))


def _module_symbol_versions(path: Path) -> dict[str, str]:
    modprobe = shutil.which("modprobe")
    if not modprobe:
        return {}
    rc, out, _ = _run([modprobe, "--show-modversions", str(path)])
    if rc:
        return {}
    values = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            values[parts[-1]] = parts[0]
    return values

def _modinfo(path: Path, field: str) -> str | None:
    modinfo = shutil.which("modinfo")
    if not modinfo:
        return None
    rc, out, _ = _run([modinfo, "-F", field, str(path)])
    return out if rc == 0 else None


def validate_artifact(
    path: str,
    *,
    expected_module: str | None = None,
    expected_architecture: str | None = None,
    expected_vermagic: str | None = None,
    exported_symbols: set[str] | None = None,
    exported_symbol_crcs: dict[str, str] | None = None,
) -> ArtifactResult:
    artifact = Path(path)
    errors: list[str] = []
    warnings: list[str] = []
    module = artifact.name.removesuffix(".ko")
    if not artifact.is_file():
        return ArtifactResult(path, "invalid", module, "", "", (), ("artifact does not exist",), ())
    if artifact.suffix != ".ko":
        errors.append("artifact is not a .ko module")
    machine = _elf_machine(artifact) or ""
    expected_machine = _expected_elf_machine(expected_architecture or "") if expected_architecture else None
    if expected_machine and machine and expected_machine.lower() not in machine.lower():
        errors.append(f"ELF architecture mismatch: expected {expected_machine}, got {machine}")
    if expected_machine and not machine:
        warnings.append("readelf is unavailable; ELF architecture was not verified")
    reported_name = _modinfo(artifact, "name")
    if reported_name and expected_module and reported_name != expected_module:
        errors.append(f"module name mismatch: expected {expected_module}, got {reported_name}")
    if expected_module and not reported_name:
        warnings.append("modinfo is unavailable or could not read module metadata")
    vermagic = _modinfo(artifact, "vermagic") or ""
    if expected_vermagic and vermagic and expected_vermagic not in vermagic:
        errors.append("kernel vermagic mismatch")
    elif expected_vermagic and not vermagic:
        warnings.append("module vermagic was not available for verification")
    unresolved = _undefined_symbols(artifact)
    unresolved_symbols = tuple(x for x in unresolved if exported_symbols is not None and x not in exported_symbols)
    if exported_symbols is not None and unresolved_symbols:
        errors.append("unresolved kernel symbols: " + ", ".join(unresolved_symbols[:20]))
    elif exported_symbols is None and unresolved:
        warnings.append("kernel exported-symbol table was not supplied; undefined symbols were not resolved")
    if exported_symbol_crcs is not None:
        required_versions = _module_symbol_versions(artifact)
        crc_mismatches = tuple(
            f"{symbol}: module={crc} kernel={exported_symbol_crcs[symbol]}"
            for symbol, crc in required_versions.items()
            if symbol in exported_symbol_crcs and crc.lower() != exported_symbol_crcs[symbol].lower()
        )
        if crc_mismatches:
            errors.append("kernel symbol CRC mismatch: " + ", ".join(crc_mismatches[:20]))
        elif not required_versions:
            warnings.append("module symbol CRCs were not available; CRC validation was skipped")
    depends_raw = _modinfo(artifact, "depends") or ""
    depends = tuple(x for x in depends_raw.split(",") if x)
    status = "invalid" if errors else ("valid-with-warnings" if warnings else "valid")
    return ArtifactResult(str(artifact), status, reported_name or module, machine,
                          vermagic, depends, tuple(errors), tuple(warnings), unresolved_symbols)
