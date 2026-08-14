from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_csv(path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["status"]
        rows = [{"status": "EMPTY"}]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False, sort_keys=True) if isinstance(row.get(key), (dict, list)) else row.get(key, "") for key in fields})
    return path


def write_md(path: Path, title: str, rows: Any, note: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", f"Generated: {iso_now()}", ""]
    if note:
        lines.extend([note, ""])
    if isinstance(rows, dict):
        for key, value in rows.items():
            lines.append(f"- **{key}**: `{value}`")
    elif isinstance(rows, list) and rows and isinstance(rows[0], dict):
        fields: list[str] = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
        lines.append("| " + " | ".join(fields) + " |")
        lines.append("| " + " | ".join(["---"] * len(fields)) + " |")
        for row in rows:
            values = []
            for key in fields:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False, sort_keys=True)
                values.append(str(value).replace("\n", " ").replace("|", "\\|")[:500])
            lines.append("| " + " | ".join(values) + " |")
    elif isinstance(rows, list):
        lines.extend(f"- {value}" for value in rows)
    else:
        lines.append(str(rows))
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def redact(value: Any) -> Any:
    if value is None or isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if re.search(r"(?i)(token|secret|password|passwd|bearer|authorization|api[_-]?key|private[_-]?key)", text):
        return "<REDACTED_SECRET_LIKE_VALUE>"
    if re.search(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", text, re.I):
        return "<REDACTED_EMAIL>"
    if len(text) > 160:
        return text[:157] + "..."
    return text


def run_operational_evidence(project_root: str | Path, output_dir: str | Path, **kwargs: Any) -> dict[str, Any]:
    """Compatibility wrapper that delegates to the current neutral, fail-closed runner."""
    from .final_runner import run_operational_atlas

    result_root = kwargs.get("result_root")
    return run_operational_atlas(str(project_root), str(output_dir), str(result_root) if result_root is not None else None)


__all__ = ["iso_now", "redact", "run_operational_evidence", "write_csv", "write_json", "write_md"]
