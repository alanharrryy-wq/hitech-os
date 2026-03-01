#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.hos._core.stable_json import write_json


def export_api_mock(output_dir: Path, payloads: dict[str, dict[str, Any]]) -> list[Path]:
    api_dir = output_dir / "api_mock"
    api_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    mapping = {
        "runs": "runs.json",
        "activity": "activity.json",
        "widgets": "widgets.json",
    }
    for key in sorted(mapping):
        if key not in payloads:
            continue
        path = api_dir / mapping[key]
        write_json(path, payloads[key], indent=2, sort_keys=True)
        outputs.append(path)
    return outputs

