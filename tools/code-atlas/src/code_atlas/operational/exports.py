from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, data: Any) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_csv(path: str | Path, rows: list[dict[str, Any]]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields, rows = ["status"], [{"status": "EMPTY"}]
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False, sort_keys=True) if isinstance(row.get(key), (dict, list)) else row.get(key, "") for key in fields})
    return target


def write_md(path: str | Path, title: str, rows: Any, note: str = "") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    if note:
        lines.extend([note, ""])
    if isinstance(rows, dict):
        lines.extend(f"- **{key}**: `{value}`" for key, value in rows.items())
    elif isinstance(rows, list) and rows and isinstance(rows[0], dict):
        fields = list(dict.fromkeys(key for row in rows for key in row))
        lines.append("| " + " | ".join(fields) + " |")
        lines.append("| " + " | ".join(["---"] * len(fields)) + " |")
        for row in rows:
            lines.append("| " + " | ".join(str(row.get(key, "")).replace("\n", " ")[:500] for key in fields) + " |")
    elif isinstance(rows, list):
        lines.extend(f"- {value}" for value in rows)
    else:
        lines.append(str(rows))
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


__all__ = ["write_json", "write_csv", "write_md"]
