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

        # Exact hardware metadata can override model defaults, but an ID with
        # multiple candidates must expose those candidates rather than the
        # synthetic "detect-driver" marker.
        for device in evidence:
            meta = DEVICES.get(device.id)
            if not meta:
                continue
            selected.extend(meta.get("candidates") or [meta["driver"]])

        selected = list(dict.fromkeys(selected + candidates))
        driver_status = {}
        for driver in selected:
            recipe = get_recipe(driver)
            driver_status[driver] = recipe_status(
                recipe,
                distribution=platform_info.distribution,
                architecture=platform_info.architecture,
                kernel=platform_info.kernel,
                version=platform_info.version,
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
            candidates: list[str] = []
            for device in evidence:
                meta = DEVICES.get(device.id)
                if meta:
                    candidates.extend(meta.get("candidates") or [meta["driver"]])
            plans.append(
                {
                    "component": component,
                    "status": "detected",
                    "hardware": [d.to_dict() for d in evidence],
                    "candidates": list(dict.fromkeys(candidates)),
                    "selection": "hardware-id",
                    "notes": [],
                }
            )
    return plans
