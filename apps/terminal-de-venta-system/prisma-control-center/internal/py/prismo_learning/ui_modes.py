"""UI mode contracts for PRISMO Learning."""
from __future__ import annotations
from typing import Any

SAFE_MODE = 'safe'
PERITO_MODE = 'perito'

def normalize_mode(mode: str | None) -> str:
    raw = (mode or SAFE_MODE).strip().lower()
    if raw in {'perito','technical','full','debug','forensic'}:
        return PERITO_MODE
    return SAFE_MODE

def mode_contract(mode: str | None = None) -> dict[str, Any]:
    mode = normalize_mode(mode)
    return {
        'mode': mode,
        'safe_mode': mode == SAFE_MODE,
        'perito_mode': mode == PERITO_MODE,
        'default_open_sections': [] if mode == SAFE_MODE else ['evidence','patterns','graph'],
        'read_only': True,
        'mutation_allowed': False,
    }
