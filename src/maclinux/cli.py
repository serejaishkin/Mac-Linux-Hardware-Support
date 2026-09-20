"""Command-line interface for Mac Linux Hardware Support."""

from __future__ import annotations

import argparse
import json
import os
import shutil

from .compat import compatibility
from .detect import detect, firmware_candidates, hardware_devices, module_loaded
from .registry import DEVICES, DRIVER_SOURCES
from .packaging import package_plan
from .resolver import resolve


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


def _system(result: dict) -> dict:
    return {
        **result,
        "distribution": _distro(),
        "package_manager": _package_manager(),
    }


def cmd_detect(args: argparse.Namespace) -> int:
    result = _system(detect())
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
        bound = f" [{item['driver']}]" if item.get("driver") else ""
        print(f"  {item['slot']} {item['pci_id']}{bound}{suffix}")
    print(f"USB devices: {len(result['usb_devices'])}")
    print(f"Loaded modules: {len(result['loaded_modules'])}")
    return 0


def cmd_inventory(args: argparse.Namespace) -> int:
    result = _system(detect())
    devices = [d.to_dict() for d in hardware_devices(result)]
    output = {
        "model": result["model"],
        "architecture": result["architecture"],
        "kernel": result["kernel"],
        "distribution": result["distribution"],
        "pci": devices,
        "usb": result["usb_devices"],
        "loaded_modules": result["loaded_modules"],
        "sysfs_buses": result["sysfs_buses"],
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    result = _system(detect())
    plans = resolve(result, hardware_devices(result))
    output = {
        "model": result["model"],
        "model_known": result["model_known"],
        "architecture": result["architecture"],
        "kernel": result["kernel"],
        "distribution": result["distribution"],
        "package_manager": result["package_manager"],
        "components": plans,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_diagnose(args: argparse.Namespace) -> int:
    result = _system(detect())
    print("Mac Linux Hardware Support 0.2.0")
    print(f"Model: {result['model']}")
    print(f"Kernel: {result['kernel']}")
    print(f"Architecture: {result['architecture']}")
    print(f"Distribution: {result['distribution']}")
    print()
    plans = resolve(result, hardware_devices(result))
    for plan in plans:
        candidates = ", ".join(plan["candidates"]) or "none"
        print(f"{plan['component']}: {plan['status']} -> {candidates}")
        for note in plan["notes"]:
            print(f"  note: {note}")
    print()
    known = [d for d in result["devices"] if d.get("known")]
    for item in known:
        meta = DEVICES[item["pci_id"]]
        print(meta["name"])
        print(f"  PCI:       {item['pci_id']}")
        print(f"  Driver:    {meta['driver']}")
        print(f"  Module:    {'loaded' if module_loaded(meta['driver'], result) else 'not loaded'}")
        if meta.get("firmware_required"):
            firmware = firmware_candidates(meta["id"])
            print(f"  Firmware:  {'found' if firmware else 'not found'}")
        source = DRIVER_SOURCES.get(meta["driver"])
        if source:
            print(f"  Upstream:  {source['upstream']}")
        print()


def cmd_plan(args: argparse.Namespace) -> int:
    result = _system(detect())
    plans = resolve(result, hardware_devices(result))
    output = {
        "model": result["model"],
        "kernel": result["kernel"],
        "architecture": result["architecture"],
        "distribution": result["distribution"],
        "package_manager": result["package_manager"],
        "components": plans,
        "actions": [],
    }
    for item in result["devices"]:
        if item.get("known"):
            meta = DEVICES[item["pci_id"]]
            action = compatibility(result, meta)
            action["package_plan"] = package_plan(result["distribution"], meta["driver"], meta.get("source", "external")).to_dict()
            output["actions"].append(action)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    from .validation import validate
    components = [args.component] if args.component else None
    results = validate(components)
    if args.json:
        print(json.dumps([item.to_dict() for item in results], indent=2, ensure_ascii=False))
        return 0 if all(item.status != "fail" for item in results) else 1
    for item in results:
        detail = item.evidence or item.reason
        print(f"{item.component}: {item.check}: {item.status}" + (f" — {detail}" if detail else ""))
    return 0 if all(item.status != "fail" for item in results) else 1


def cmd_repair(args: argparse.Namespace) -> int:
    if os.geteuid() != 0:
        print("repair requires root privileges; diagnostic commands do not.")
        return 2
    print(f"Repair workflow for {args.component} is not enabled yet.")
    print("Run: maclinux resolve")
    print("Installation remains intentionally read-only until distro adapters and validation are complete.")
    return 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="maclinux")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("detect", help="detect Mac model and hardware")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_detect)

    p = sub.add_parser("inventory", help="show normalized hardware inventory")
    p.set_defaults(func=cmd_inventory)

    p = sub.add_parser("resolve", help="resolve hardware to driver candidates")
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("diagnose", help="diagnose known hardware integrations")
    p.set_defaults(func=cmd_diagnose)

    p = sub.add_parser("plan", help="build a safe compatibility/install plan")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("test", help="run non-invasive functional hardware checks")
    p.add_argument("component", nargs="?")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_test)

    p = sub.add_parser("repair", help="repair a hardware component")
    p.add_argument("component")
    p.set_defaults(func=cmd_repair)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
