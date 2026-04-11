from __future__ import annotations

import json
from pathlib import Path


def discover_engine_manifests(root: Path) -> list[Path]:
    engine_root = root / "pya" / "engines"
    return sorted(engine_root.glob("*/manifest.json"))


def load_json_file(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_files(target: Path) -> list[Path]:
    return sorted(path for path in target.rglob("*") if path.is_file())
