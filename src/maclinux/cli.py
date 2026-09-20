"""Command-line interface for the Mac Linux Hardware Support MVP."""

from __future__ import annotations

import argparse
import json
import os
import shutil

from .compat import compatibility
from .detect import detect, firmware_candidates, module_loaded
from .registry import DEVICES, DRIVER_SOURCES


def _distro() -> str:
    values = {}
    try:
        with open("/etc/os-release", encoding="utf-8") as fh:
            for line in fh:
                if "=" in line:
                    key, value = line.rstrip().split("=", 1)
                    values[key] = value.strip('"')
    except OSError:
        pass
    return values.get("ID") or values.get("ID_LIKE") or "unknown"


def _package_manager() -> str:
    for name in ("apt-get", "dnf", "yum", "pacman", "zypper", "apk", "emerge"):
        if shutil.which(name):
            return name
    return "unknown"


def cmd_detect(args: argparse.Namespace) -> int:
    result = detect()
    result["distribution"] = _distro()
    result["package_manager"] = _package_manager()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    print(f"Model: {result['model']}")
    print(f"Architecture: {result['architecture']}")
    print(f"Kernel: {result['kernel']}")
    print(f"Distribution: {result['distribution']}")
    print(f"Package manager: {result['package_manager']}")
    print(f"Known model: {'yes' if result['model_known'] else 'no'}")
    print("\nPCI devices:")
    for item in result["devices"]:
        suffix = f" -> {item['integration']}" if item.get("integration") else ""
        print(f"  {item['slot']} {item['pci_id']}{suffix}")
    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    result = detect()
    print("Mac Linux Hardware Support 0.1.0")
    print(f"Model: {result['model']}")
    print(f"Kernel: {result['kernel']}")
    print(f"Architecture: {result['architecture']}")
    print(f"Distribution: {_distro()}")
    print()
    known = [d for d in result["devices"] if d.get("known")]
    if not known:
        print("No registered Apple-specific devices were detected.")
        return 0
    for item in known:
        meta = DEVICES[item["pci_id"]]
        print(meta["name"])
        print(f"  PCI:       {item['pci_id']}")
        print(f"  Driver:    {meta['driver']}")
        print(f"  Module:    {'loaded' if module_loaded(meta['driver']) else 'not loaded'}")
        if meta["firmware_required"]:
            firmware = firmware_candidates(meta["driver"])
            print(f"  Firmware:  {'found' if firmware else 'not found'}")
        state = compatibility(result, meta)
        print(f"  Compatibility: {state['status']}")
        print(f"  Status:    {meta['status']}")
        source = DRIVER_SOURCES.get(meta["driver"])
        if source:
            print(f"  Upstream:  {source['upstream']}")
        print()


def cmd_plan(args: argparse.Namespace) -> int:
    result = detect()
    plans = []
    for item in result["devices"]:
        if item.get("known"):
            meta = DEVICES[item["pci_id"]]
            plans.append(compatibility(result, meta))
    output = {
        "model": result["model"],
        "kernel": result["kernel"],
        "architecture": result["architecture"],
        "distribution": _distro(),
        "package_manager": _package_manager(),
        "actions": plans,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_repair(args: argparse.Namespace) -> int:
    if os.geteuid() != 0:
        print("repair requires root privileges; diagnostic commands do not.")
        return 2
    if args.component == "camera":
        print("Camera repair is intentionally not automatic in MVP 0.1.")
        print("Run: maclinux plan")
        print("The plan must pass kernel, headers, firmware and Secure Boot checks before installation.")
        return 3
    print(f"No repair workflow implemented for: {args.component}")
    return 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="maclinux")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("detect", help="detect Mac model and PCI devices")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_detect)

    p = sub.add_parser("diagnose", help="diagnose known hardware integrations")
    p.set_defaults(func=cmd_diagnose)

    p = sub.add_parser("plan", help="build a safe compatibility/install plan")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("repair", help="repair a hardware component")
    p.add_argument("component", choices=["camera", "wifi", "audio"])
    p.set_defaults(func=cmd_repair)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
