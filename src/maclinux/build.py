"""Safe, non-mutating driver build planning and execution."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, asdict

from .artifacts import validate_artifact
from .kernel import detect_kernel
from .platform import PlatformInfo
from .recipes import get_recipe, recipe_status
from .sources import get_source


@dataclass(frozen=True)
class BuildPlan:
    driver: str
    status: str
    source: dict | None
    recipe: dict | None
    platform: dict
    kernel: dict
    commands: tuple[tuple[str, ...], ...]
    output_modules: tuple[str, ...]
    blockers: tuple[str, ...]
    notes: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def plan_build(driver: str, info: PlatformInfo, *, source_dir: str | None = None) -> BuildPlan:
    recipe = get_recipe(driver)
    source = get_source(driver)
    kernel = detect_kernel(info.kernel_tree or None)
    blockers: list[str] = []
    notes: list[str] = []
    status = recipe_status(recipe, distribution=info.distribution,
                           architecture=info.architecture, kernel=info.kernel, version=info.version)
    if recipe is None:
        blockers.append("no build recipe")
    if not info.kernel_tree:
        blockers.append("matching kernel build tree/headers not found")
        status = "blocked"
    if info.compiler == "unknown":
        blockers.append("gcc or clang not found")
        status = "blocked"
    if recipe and not kernel.config_present:
        blockers.append("kernel configuration not found")
        status = "blocked"
    if recipe and not kernel.modules_symvers_present:
        blockers.append("Module.symvers not found; exported-symbol ABI cannot be verified")
        status = "blocked"
    if recipe and info.distribution not in recipe.distributions:
        blockers.append(f"distribution {info.distribution} is not covered by recipe")
    if recipe and info.architecture not in recipe.architectures:
        blockers.append(f"architecture {info.architecture} is not covered by recipe")
    if source is None:
        blockers.append("source provenance is missing")
    if source and source.proprietary:
        blockers.append("proprietary source cannot be fetched automatically")
    if source_dir and not os.path.isdir(source_dir):
        blockers.append("source directory does not exist")
    if recipe and recipe.firmware:
        notes.append("firmware is a separate input; build success does not prove firmware availability or compatibility")
    root = source_dir or f"drivers/src/{driver}"
    commands: tuple[tuple[str, ...], ...] = ()
    if recipe and not blockers:
        commands = (("make", "-C", info.kernel_tree, "M=" + os.path.abspath(root), "modules"),)
    return BuildPlan(driver, status, source.to_dict() if source else None,
                     recipe.to_dict() if recipe else None, info.to_dict(), kernel.to_dict(),
                     commands, recipe.modules if recipe else (), tuple(blockers), tuple(notes))


def execute_build(plan: BuildPlan, *, execute: bool = False) -> dict:
    """Execute only the build command; never install, load or sign a module."""
    if not execute:
        return {"status": "dry-run", "executed": False, "commands": [list(c) for c in plan.commands],
                "reason": "explicit --execute is required"}
    if plan.status != "buildable" or plan.blockers:
        return {"status": "blocked", "executed": False, "blockers": list(plan.blockers)}
    results = []
    for command in plan.commands:
        if command[0] not in {"make", "ninja", "meson"}:
            return {"status": "blocked", "executed": False, "reason": "command not permitted"}
        proc = subprocess.run(command, text=True, capture_output=True, check=False, shell=False)
        results.append({"command": list(command), "returncode": proc.returncode,
                        "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]})
        if proc.returncode:
            return {"status": "build-failed", "executed": True, "results": results}
    artifacts = []
    for module in plan.output_modules:
        for command in plan.commands:
            source_root = next((part[2:] for part in command if part.startswith("M=")), "")
            candidate = os.path.join(source_root, module + ".ko")
            result = validate_artifact(candidate, expected_module=module,
                                       expected_architecture=plan.platform.get("architecture"),
                                       expected_vermagic=plan.kernel.get("vermagic") or None)
            artifacts.append(result.to_dict())
    if any(a["status"] == "invalid" for a in artifacts):
        return {"status": "artifact-invalid", "executed": True, "results": results, "artifacts": artifacts}
    return {"status": "built", "executed": True, "results": results, "artifacts": artifacts}
