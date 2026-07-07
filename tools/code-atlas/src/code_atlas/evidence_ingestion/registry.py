from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def current_root() -> Path:
    return Path(__file__).resolve().parents[3] / 'evidence_ingestion' / 'current'


def list_registers() -> list[str]:
    root = current_root() / 'registers'
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_file())


def load_register(name: str) -> Any:
    path = current_root() / 'registers' / name
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding='utf-8', errors='replace')
    if path.suffix.lower() == '.json':
        return json.loads(text)
    return text


def summarize_status() -> dict[str, Any]:
    root = current_root()
    result_path = root / 'INGESTION_RESULT.json'
    if not result_path.exists():
        return {'status': 'MISSING_INGESTION_RESULT', 'root': str(root)}
    return json.loads(result_path.read_text(encoding='utf-8', errors='replace'))
