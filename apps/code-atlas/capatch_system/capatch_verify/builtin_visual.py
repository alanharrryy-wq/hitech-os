from __future__ import annotations

import re
from pathlib import Path


def detect_important_flood(text: str, *, max_count: int = 8) -> dict[str, object]:
    count = len(re.findall(r'!important\b', text))
    return {'ok': count <= max_count, 'count': count, 'max_count': max_count}


def detect_accidental_dark_theme(text: str) -> dict[str, object]:
    lowered = text.lower()
    dark_tokens = ['#000', '#050505', '#0b0b0b', '#111', 'background: black', 'background-color: black']
    hits = [token for token in dark_tokens if token in lowered]
    return {'ok': not hits, 'hits': hits}


def validate_visual_static_file(path_value: Path) -> dict[str, object]:
    path_value = Path(path_value)
    if not path_value.exists() or not path_value.is_file():
        return {'ok': False, 'reason': 'file missing'}
    text = path_value.read_text(encoding='utf-8', errors='replace')
    important = detect_important_flood(text)
    dark = detect_accidental_dark_theme(text)
    return {'ok': bool(important['ok'] and dark['ok']), 'important': important, 'dark': dark}
