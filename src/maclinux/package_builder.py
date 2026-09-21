"""Native package build planning/execution without installation."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path

from .packaging import BackendOutput, PackageArtifact, render_package


@dataclass(frozen=True)
class PackageBuildPlan:
    status: str
    ecosystem: str
    package_format: str
    recipe_path: str
    staging: str
    output_dir: str
    commands: tuple[tuple[str, ...], ...]
    blockers: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return asdict(self)


def _tool_for(ecosystem: str) -> str | None:
    return {
        "deb": "dpkg-deb",
        "rpm": "rpmbuild",
        "arch": "makepkg",
        "apk": "abuild",
        "gentoo": "ebuild",
        "generic": "tar",
    }.get(ecosystem)


def _write_recipe(root: Path, output: BackendOutput) -> Path:
    recipe = root / output.recipe_path
    recipe.parent.mkdir(parents=True, exist_ok=True)
    recipe.write_text(output.recipe, encoding="utf-8")
    return recipe


def _stage_modules(root: Path, artifact: PackageArtifact, module_paths: tuple[str, ...]) -> tuple[str, ...]:
    if len(module_paths) != len(artifact.modules):
        raise ValueError("module_paths count must match artifact.modules")
    target = root / "lib" / "modules" / artifact.kernel_release / "extra" / artifact.driver
    target.mkdir(parents=True, exist_ok=True)
    staged = []
    for module, source in zip(artifact.modules, module_paths):
        src = Path(source)
        if not src.is_file():
            raise FileNotFoundError(str(src))
        dest = target / (module + ".ko")
        shutil.copy2(src, dest)
        staged.append(str(dest))
    return tuple(staged)


def _prepare_deb(root: Path, artifact: PackageArtifact) -> None:
    control_dir = root / "DEBIAN"
    control_dir.mkdir(parents=True, exist_ok=True)
    deps = ", ".join(artifact.dependencies) or "dkms"
    control = (
        f"Package: {artifact.package_name}\nVersion: {artifact.package_version}\n"
        f"Architecture: {artifact.architecture}\nDepends: {deps}\n"
        "Section: kernel\nPriority: optional\n"
        "Maintainer: maclinux\n"
        "Description: Apple hardware driver managed by maclinux\n"
    )
    (control_dir / "control").write_text(control, encoding="utf-8")


def _prepare_generic(root: Path, artifact: PackageArtifact) -> None:
    import json
    (root / "maclinux-manifest.json").write_text(
        json.dumps(artifact.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def plan_package_build(
    artifact: PackageArtifact,
    module_paths: tuple[str, ...],
    *,
    output_dir: str | None = None,
) -> PackageBuildPlan:
    output = render_package(artifact)
    blockers: list[str] = []
    notes: list[str] = []
    tool = _tool_for(output.ecosystem)
    if not tool:
        blockers.append(f"no package builder for ecosystem {output.ecosystem}")
    elif not shutil.which(tool):
        blockers.append(f"package builder not found: {tool}")
    if len(module_paths) != len(artifact.modules):
        blockers.append("module_paths count does not match artifact.modules")
    for path in module_paths:
        if not os.path.isfile(path):
            blockers.append(f"module artifact not found: {path}")
    root = tempfile.mkdtemp(prefix=f"maclinux-package-{artifact.driver}-")
    outdir = os.path.abspath(output_dir or os.path.join(root, "dist"))
    Path(outdir).mkdir(parents=True, exist_ok=True)
    return PackageBuildPlan(
        status="blocked" if blockers else "buildable",
        ecosystem=output.ecosystem,
        package_format=output.package_format,
        recipe_path=output.recipe_path,
        staging=root,
        output_dir=outdir,
        commands=(),
        blockers=tuple(blockers),
        notes=tuple(notes),
    )


def execute_package_build(
    artifact: PackageArtifact,
    module_paths: tuple[str, ...],
    *,
    output_dir: str | None = None,
    execute: bool = False,
) -> dict:
    plan = plan_package_build(artifact, module_paths, output_dir=output_dir)
    if not execute:
        return {"status": "dry-run", "executed": False, "plan": plan.to_dict(),
                "reason": "explicit package build execution is required"}
    if plan.blockers:
        return {"status": "blocked", "executed": False, "plan": plan.to_dict()}
    root = Path(plan.staging)
    output = render_package(artifact)
    recipe = _write_recipe(root, output)
    _stage_modules(root, artifact, module_paths)

    if output.ecosystem == "deb":
        _prepare_deb(root, artifact)
        package_path = Path(plan.output_dir) / f"{artifact.package_name}_{artifact.package_version}_{artifact.architecture}.deb"
        command = ("dpkg-deb", "--build", str(root), str(package_path))
    elif output.ecosystem == "generic":
        _prepare_generic(root, artifact)
        package_path = Path(plan.output_dir) / f"{artifact.package_name}-{artifact.package_version}.tar.gz"
        command = ("tar", "-C", str(root), "-czf", str(package_path), ".")
    else:
        # Other ecosystems currently receive their canonical recipe plus staged modules.
        # Their native helpers are deliberately not guessed into a fake package.
        return {"status": "recipe-ready", "executed": True, "plan": plan.to_dict(),
                "recipe": str(recipe), "reason": "native recipe requires distro-specific build context"}
    proc = subprocess.run(command, text=True, capture_output=True, check=False, shell=False)
    result = {"command": list(command), "returncode": proc.returncode,
              "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}
    if proc.returncode:
        return {"status": "package-build-failed", "executed": True, "plan": plan.to_dict(),
                "result": result}
    return {"status": "built", "executed": True, "plan": plan.to_dict(),
            "recipe": str(recipe), "package": str(package_path), "result": result}
