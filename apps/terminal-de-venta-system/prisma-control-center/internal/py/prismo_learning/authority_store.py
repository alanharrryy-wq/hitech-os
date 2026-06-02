# PRISMO Learning Core V1.2 F3
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: pattern-miner + authority-brain, local store writes only, read-only against repo/DB/secrets.
# Standard library only.

"""Read-only friendly helpers around the F3 authority memory file."""
from __future__ import annotations
from typing import Any
from .memory_store import read_store

def load_authority_summary(base=None) -> dict[str, Any]:
    return read_store("authority", {"schema_version": "1.2.0", "record_count": 0, "top_evidence": [], "read_only": True, "mutation_allowed": False}, base)
def top_authority(limit: int = 20, base=None) -> list[dict[str, Any]]:
    return list(load_authority_summary(base).get("top_evidence") or [])[:limit]
def authority_counts(base=None) -> dict[str, Any]:
    data = load_authority_summary(base)
    return {"record_count": data.get("record_count", 0), "status_counts": data.get("status_counts", {}), "type_counts": data.get("type_counts", {}), "average_top_authority_score": data.get("average_top_authority_score", 0)}
