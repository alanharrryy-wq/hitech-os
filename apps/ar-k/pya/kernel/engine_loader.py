from __future__ import annotations

import importlib
from pathlib import Path

from pya.kernel.discovery import discover_engine_manifests, load_json_file
from pya.system.admission import admit_engine_manifest
from pya.system.execution import CANONICAL_STAGE_ORDER


def _instantiate(entrypoint: str, manifest: dict[str, object]):
    module_name, class_name = entrypoint.split(":", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls(manifest=manifest)


def discover_and_load_engines(root: Path, root_manifest: dict[str, object]) -> list[object]:
    engines = []
    for manifest_path in discover_engine_manifests(root):
        manifest = load_json_file(manifest_path)
        decision = admit_engine_manifest(manifest, root_manifest)
        if not decision.admitted:
            reasons = "; ".join(decision.reasons)
            raise ValueError(f"Engine admission failed for {decision.engine_id}: {reasons}")
        engines.append(_instantiate(str(manifest["entrypoint"]), manifest))
    engines.sort(key=lambda engine: CANONICAL_STAGE_ORDER.index(engine.stage))
    return engines
