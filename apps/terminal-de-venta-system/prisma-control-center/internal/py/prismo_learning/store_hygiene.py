"""Store hygiene signals without destructive cleanup."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .paths import ensure_store

def store_hygiene_report() -> dict[str, Any]:
    root = ensure_store()
    files = [p for p in root.rglob('*') if p.is_file()]
    total = sum((p.stat().st_size for p in files), 0)
    largest = sorted(files, key=lambda p: p.stat().st_size, reverse=True)[:10]
    return {
        'ok': True, 'status': 'available', 'file_count': len(files), 'total_bytes': total,
        'largest': [{'path': str(p.relative_to(root)).replace('\\','/'), 'bytes': p.stat().st_size} for p in largest],
        'destructive_cleanup_performed': False, 'read_only': True, 'mutation_allowed': False,
    }
