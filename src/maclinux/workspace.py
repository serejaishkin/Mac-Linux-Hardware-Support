"""Isolated build workspace and source provenance helpers."""
from __future__ import annotations
import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Workspace:
    path: str
    source_path: str
    source_sha256: str
    cleanup: bool = True
    def to_dict(self) -> dict:
        return asdict(self)

def source_sha256(source_dir: str) -> str:
    root = os.path.abspath(source_dir)
    digest = hashlib.sha256()
    for base, dirs, files in os.walk(root):
        dirs.sort()
        files.sort()
        for name in files:
            path = os.path.join(base, name)
            digest.update(os.path.relpath(path, root).encode("utf-8"))
            with open(path, "rb") as fh:
                while True:
                    chunk = fh.read(1024 * 1024)
                    if not chunk:
                        break
                    digest.update(chunk)
    return digest.hexdigest()

def create_workspace(driver: str, source_dir: str) -> Workspace:
    root = tempfile.mkdtemp(prefix=f"maclinux-{driver}-")
    target = os.path.join(root, "source")
    shutil.copytree(os.path.abspath(source_dir), target)
    return Workspace(root, target, source_sha256(target))
