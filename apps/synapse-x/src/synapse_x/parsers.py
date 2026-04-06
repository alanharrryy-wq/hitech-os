from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS = {".json", ".jsonl", ".log", ".txt", ".md", ".report"}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_path(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()

    if suffix == ".json":
        return {
            "kind": "json",
            "source_path": str(path),
            "payload": json.loads(_read_text(path)),
        }

    if suffix == ".jsonl":
        rows: list[Any] = []
        for line in _read_text(path).splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        return {
            "kind": "jsonl",
            "source_path": str(path),
            "payload": rows,
        }

    if suffix in {".log", ".txt"}:
        return {
            "kind": "log",
            "source_path": str(path),
            "payload": _read_text(path),
        }

    if suffix in {".md", ".report"}:
        return {
            "kind": "report",
            "source_path": str(path),
            "payload": _read_text(path),
        }

    raise ValueError(f"Unsupported file type: {path}")
