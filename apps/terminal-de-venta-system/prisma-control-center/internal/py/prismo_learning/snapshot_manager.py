"""Snapshot utilities for compaction/hygiene."""
from __future__ import annotations
from typing import Any
from pathlib import Path
from .memory_store import snapshot_store, store_file

def snapshot_known_stores() -> dict[str, str | None]:
    names = ['feedback','feedback_stats','episodic','procedural','protocol_stats','patterns','authority']
    out: dict[str, str | None] = {}
    for name in names:
        try:
            snap = snapshot_store(name)
            out[name] = str(snap) if snap else None
        except Exception as exc:
            out[name] = f'error:{exc}'
    return out
