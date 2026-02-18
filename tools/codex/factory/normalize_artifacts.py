from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TIMESTAMP_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\+\d{2}:\d{2}|Z)")
RUN_ID_RE = re.compile(r"\b[a-z0-9_]+_\d{8}_\d{6}(?:_[a-f0-9]{8})?(?:_\d{3})?\b", re.IGNORECASE)


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned = {}
        for key in sorted(value):
            lowered = key.lower()
            if lowered in {"ts_utc", "started_at", "ended_at", "created_at"}:
                cleaned[key] = "<TS>"
                continue
            if lowered in {"run_id"}:
                cleaned[key] = "<RUN_ID>"
                continue
            cleaned[key] = normalize_value(value[key])
        return cleaned
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, str):
        text = TIMESTAMP_RE.sub("<TS>", value)
        text = RUN_ID_RE.sub("<RUN_ID>", text)
        return text
    return value


def normalize_json_text(text: str) -> str:
    payload = json.loads(text)
    normalized = normalize_value(payload)
    return json.dumps(normalized, indent=2, sort_keys=True) + "\n"


def normalize_report_text(text: str) -> str:
    normalized = TIMESTAMP_RE.sub("<TS>", text)
    normalized = RUN_ID_RE.sub("<RUN_ID>", normalized)
    return normalized


def normalize_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return normalize_json_text(text)
    return normalize_report_text(text)
