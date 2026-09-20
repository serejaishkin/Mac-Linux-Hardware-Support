"""Model-aware, non-invasive driver resolver."""

from __future__ import annotations

from .hardware import HardwareDevice
from .registry import DEVICES, MODEL_COMPONENTS
from .recipes import get_recipe, recipe_status
from .platform import detect_platform


def _pci_candidates(devices: list[HardwareDevice]) -> dict[str, list[HardwareDevice]]:
    result: dict[str, list[HardwareDevice]] = {}
    for device in devices:
        if device.id and device.id in DEVICES:
            result.setdefault(DEVICES[device.id]["component"], []).append(device)
    return result


def resolve(system: dict, devices: list[HardwareDevice]) -> list[dict]:
    model = system.get("model", "unknown")
    components = MODEL_COMPONENTS.get(model, {})
    by_component = _pci_candidates(devices)
    platform_info = detect_platform()
    plans: list[dict] = []

    for component, spec in components.items():
        candidates = list(spec.get("drivers", []))
        evidence = by_component.get(component, [])
        selected: list[str] = []

        for device in evidence:
            if device.id in DEVICES:
                selected.append(DEVICES[device.id]["driver"])

        selected = list(dict.fromkeys(selected + candidates))
        driver_status = {}
        for driver in selected:
            recipe = get_recipe(driver)
            driver_status[driver] = recipe_status(
                recipe,
                distribution=platform_info.distribution,
                architecture=platform_info.architecture,
                kernel=platform_info.kernel,
            )
        plans.append(
            {
                "component": component,
                "status": "detected" if evidence else "not-detected",
                "hardware": [d.to_dict() for d in evidence],
                "candidates": selected,
                "driver_status": driver_status,
                "selection": "hardware-id" if evidence else "model-candidates",
                "notes": spec.get("notes", []),
            }
        )

    if not components:
        for component, evidence in by_component.items():
            plans.append(
                {
                    "component": component,
                    "status": "detected",
                    "hardware": [d.to_dict() for d in evidence],
                    "candidates": list(dict.fromkeys(
                        DEVICES[d.id]["driver"] for d in evidence if d.id in DEVICES
                    )),
                    "selection": "hardware-id",
                    "notes": [],
                }
            )
    return plans
