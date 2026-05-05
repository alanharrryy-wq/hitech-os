import json
from typing import Any


def parse_jsonl_text(text: str) -> list[Any]:
    rows: list[Any] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        rows.append(json.loads(stripped))
    return rows
