"""Command-line interface for Mac Linux Hardware Support."""

from __future__ import annotations

import argparse
import json
import os
import shutil

from .compat import compatibility
from .detect import detect, firmware_candidates, hardware_devices, module_loaded
from .registry import DEVICES, DRIVER_SOURCES
from .packaging import PackageArtifact, package_plan, render_package, repair_transaction
from .resolver import resolve
from .validation import correlate_resolution, validate

from .build import execute_build, plan_build
from .platform import detect_platform


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


def cmd_platform(args: argparse.Namespace) -> int:
    info = detect_platform()
    print(json.dumps(info.to_dict(), indent=2, ensure_ascii=False))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    info = detect_platform()
    plan = plan_build(args.driver, info, source_dir=args.source_dir)
    result = execute_build(plan, execute=args.execute)
    output = {"plan": plan.to_dict(), "execution": result}
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if result["status"] in {"dry-run", "built"} else 1


def cmd_package(args: argparse.Namespace) -> int:
    info = detect_platform()
    recipe = __import__("maclinux.recipes", fromlist=["get_recipe"]).get_recipe(args.driver)
    if recipe is None:
        print(json.dumps({"status": "unknown", "reason": "no recipe for driver"}, indent=2))
        return 2
    source_hash = args.source_sha256
    if args.source_dir and not source_hash:
        from .workspace import source_sha256
        source_hash = source_sha256(args.source_dir)
    if not source_hash:
        print(json.dumps({"status": "blocked", "reason": "source SHA-256 is required; use --source-dir or --source-sha256"}, indent=2))
        return 1
    artifact = PackageArtifact(
        driver=args.driver,
        package_name=args.package_name or "maclinux-" + args.driver,
        package_version=args.version,
        ecosystem=info.ecosystem,
        architecture=info.architecture,
        kernel_release=info.kernel,
        source_sha256=source_hash,
        modules=recipe.modules,
        # recipe.packages are build prerequisites, not runtime package dependencies.
        dependencies=(),
        firmware=recipe.firmware,
        metadata={"distribution": info.distribution, "distribution_version": info.version},
    )
    output = render_package(artifact)
    print(json.dumps({"status": "planned", "artifact": artifact.to_dict(), "backend": output.to_dict()},
                     indent=2, ensure_ascii=False))
    return 0


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
    print("Mac Linux Hardware Support 0.7.0")
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
    components = [args.component] if args.component else None
    results = validate(components)
    system = _system(detect())
    plans = resolve(system, hardware_devices(system))
    if args.component:
        plans = [p for p in plans if p["component"] == args.component]
    correlated = correlate_resolution(plans, results)
    if args.json:
        print(json.dumps({"model": system["model"], "kernel": system["kernel"],
                          "architecture": system["architecture"], "components": correlated},
                         indent=2, ensure_ascii=False))
        return 0 if all(item.status != "fail" for item in results) else 1
    for item in results:
        detail = item.evidence or item.reason
        print(f"{item.component}: {item.check}: {item.status}" + (f" — {detail}" if detail else ""))
    for plan in correlated:
        candidates = ", ".join(plan.get("candidates", [])) or "none"
        binding = ", ".join((x.get("module") or x.get("driver") or "unbound") for x in plan.get("binding", [])) or "not detected"
        print(f"  resolution: {candidates}; binding: {binding}; validation: {plan['validation']}")
    return 0 if all(item.status != "fail" for item in results) else 1


def cmd_repair(args: argparse.Namespace) -> int:
    """Print an auditable repair transaction; never execute it yet."""
    result = _system(detect())
    plans = resolve(result, hardware_devices(result))
    selected = [p for p in plans if p["component"] == args.component]
    if not selected:
        print(f"Unknown component: {args.component}")
        return 2
    transactions = []
    for candidate in selected[0].get("candidates", []):
        pkg = package_plan(result["distribution"], candidate)
        transactions.append({"driver": candidate, "package_plan": pkg.to_dict(),
                             "transaction": repair_transaction(pkg, dry_run=True)})
    print(json.dumps({"component": args.component, "model": result["model"],
                      "architecture": result["architecture"], "kernel": result["kernel"],
                      "transactions": transactions}, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="maclinux")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("platform", help="detect distribution, package ecosystem and kernel build environment")
    p.set_defaults(func=cmd_platform)

    p = sub.add_parser("build", help="plan or execute a driver build")
    p.add_argument("driver")
    p.add_argument("--source-dir")
    p.add_argument("--execute", action="store_true", help="actually run the build command")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("package", help="generate a deterministic package recipe")
    p.add_argument("driver")
    p.add_argument("--version", default="0.1.0")
    p.add_argument("--package-name")
    p.add_argument("--source-dir")
    p.add_argument("--source-sha256")
    p.set_defaults(func=cmd_package)

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
