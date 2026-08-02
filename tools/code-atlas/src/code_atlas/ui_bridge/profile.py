from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _expand(value: str) -> str:
    out = os.path.expandvars(value)
    for key, val in os.environ.items():
        out = out.replace("${" + key + "}", val)
    return out

@dataclass(frozen=True)
class BridgeProfile:
    profile_id: str
    product_root: str
    governor_root: str
    output_root: str
    application_enabled: bool = False
    adapter_ids: dict[str, str] = field(default_factory=dict)
    recipe_paths: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def load_profile(path: str | Path | None = None) -> BridgeProfile:
    if path is None:
        raw = {
            "profileId": "generic-ui-bridge",
            "productRoot": os.environ.get("PRISMA_PRODUCT_ROOT", "."),
            "governorRoot": os.environ.get("PRISMA_GOVERNOR_ROOT", "."),
            "outputRoot": os.environ.get("CODE_ATLAS_OUTPUT_ROOT", "./code-atlas-out"),
            "applicationEnabled": False,
            "adapterIds": {},
            "recipePaths": [],
        }
    else:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return BridgeProfile(
        profile_id=str(raw.get("profileId", "generic-ui-bridge")),
        product_root=_expand(str(raw.get("productRoot", "."))),
        governor_root=_expand(str(raw.get("governorRoot", "."))),
        output_root=_expand(str(raw.get("outputRoot", "./code-atlas-out"))),
        application_enabled=bool(raw.get("applicationEnabled", False)),
        adapter_ids={str(k): str(v) for k, v in raw.get("adapterIds", {}).items()},
        recipe_paths=[_expand(str(v)) for v in raw.get("recipePaths", [])],
        metadata=dict(raw.get("metadata", {})),
    )
