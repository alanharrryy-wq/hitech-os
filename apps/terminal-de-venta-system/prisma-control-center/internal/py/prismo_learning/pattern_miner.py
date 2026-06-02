# PRISMO Learning Core V1.2 F3
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: pattern-miner + authority-brain, local store writes only, read-only against repo/DB/secrets.
# Standard library only.

"""F3 operational pattern mining facade."""
from __future__ import annotations
from typing import Any
from .evidence_registry import load_registry
from .f3_engine import mine_advanced_patterns, build_f3_report
from .memory_store import write_store

def detect_repeated_failures(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [p for p in mine_advanced_patterns(records) if "fail" in str(p.get("id", "")).lower() or str(p.get("priority")) == "high"]
def detect_protocol_success(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [p for p in mine_advanced_patterns(records) if "protocol" in str(p.get("id", ""))]
def detect_surface_hotspots(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [p for p in mine_advanced_patterns(records) if "surface" in str(p.get("id", ""))]
def mine_patterns(evidence_registry: dict[str, Any] | None = None, episodic_memory: dict[str, Any] | None = None, base=None) -> dict[str, Any]:
    if evidence_registry is None: return {"schema_version": "1.2.0", "patterns": build_f3_report(base).get("patterns", []), "read_only": True, "mutation_allowed": False}
    records = list((evidence_registry or load_registry(base)).get("records") or [])
    patterns = mine_advanced_patterns(records)
    store = {"schema_version": "1.2.0", "patterns": patterns, "read_only": True, "mutation_allowed": False}
    write_store("patterns", store, base); return store
