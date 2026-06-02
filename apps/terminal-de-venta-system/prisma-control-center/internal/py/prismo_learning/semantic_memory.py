# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Semantic memory: stable facts with evidence references."""
from __future__ import annotations
from typing import Any
from .hashes import stable_json_hash
from .memory_store import read_store, write_store
from .clock import now_iso


def upsert_fact(claim: str, evidence_ids: list[str] | None = None, confidence: float = 0.7, base=None) -> dict[str, Any]:
    store = read_store("semantic", {"schema_version": "1.0.0", "facts": []}, base)
    fact_id = "fact_" + stable_json_hash({"claim": claim})[:14]
    fact = {"id": fact_id, "claim": claim, "source_evidence_ids": evidence_ids or [], "confidence": confidence, "updated_at": now_iso()}
    facts = [f for f in store.get("facts", []) if f.get("id") != fact_id]
    facts.insert(0, fact)
    store["facts"] = facts
    write_store("semantic", store, base)
    return fact


def get_fact(fact_id: str, base=None) -> dict[str, Any] | None:
    for fact in read_store("semantic", {"facts": []}, base).get("facts", []):
        if fact.get("id") == fact_id:
            return fact
    return None


def facts_for_surface(surface: str, base=None) -> list[dict[str, Any]]:
    return [f for f in read_store("semantic", {"facts": []}, base).get("facts", []) if surface.lower() in str(f).lower()]


def facts_for_protocol(protocol: str, base=None) -> list[dict[str, Any]]:
    return [f for f in read_store("semantic", {"facts": []}, base).get("facts", []) if protocol.lower() in str(f).lower()]
