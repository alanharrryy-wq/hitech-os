from __future__ import annotations

from pathlib import Path

from ..shared.runtime_paths import build_runtime_paths

def runtime_root() -> Path:
    return build_runtime_paths().ensure().runtime_root

def modular_root() -> Path:
    return build_runtime_paths().package_root

def shadow_root() -> Path:
    return build_runtime_paths().ensure().shadow_root
