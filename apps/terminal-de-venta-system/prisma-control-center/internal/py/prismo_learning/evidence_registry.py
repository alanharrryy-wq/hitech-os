# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Evidence registry: load, save, upsert, query."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .atomic_io import atomic_write_json, read_json
from .clock import now_iso
from .hashes import stable_json_hash
from .paths import ensure_store
from .constants import MAX_REGISTRY_RECORDS


def registry_path(base: str | Path | None = None) -> Path:
    return ensure_store(base) / "01_EVIDENCE_REGISTRY" / "evidence_registry.json"


def empty_registry() -> dict[str, Any]:
    return {"schema_version": "1.0.0", "generated_at": now_iso(), "records": []}


def load_registry(base: str | Path | None = None) -> dict[str, Any]:
    data = read_json(registry_path(base), empty_registry())
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        return empty_registry()
    return data


def save_registry(registry: dict[str, Any], base: str | Path | None = None) -> Path:
    registry = dict(registry)
    registry["generated_at"] = now_iso()
    registry["records"] = list(registry.get("records") or [])[:MAX_REGISTRY_RECORDS]
    path = registry_path(base)
    atomic_write_json(path, registry)
    return path


def evidence_id(record: dict[str, Any]) -> str:
    key = record.get("sha256") or record.get("source_path") or stable_json_hash(record)
    return "ev_" + stable_json_hash({"key": key, "type": record.get("type")})[:16]


def upsert_evidence(record: dict[str, Any], base: str | Path | None = None) -> dict[str, Any]:
    registry = load_registry(base)
    enriched = dict(record)
    enriched.setdefault("created_at", now_iso())
    enriched.setdefault("id", evidence_id(enriched))
    records = [r for r in registry.get("records", []) if r.get("id") != enriched["id"]]
    records.insert(0, enriched)
    registry["records"] = records[:MAX_REGISTRY_RECORDS]
    save_registry(registry, base)
    return enriched


def query_evidence(filters: dict[str, Any] | None = None, base: str | Path | None = None, limit: int = 100) -> list[dict[str, Any]]:
    filters = filters or {}
    records = load_registry(base).get("records", [])
    out: list[dict[str, Any]] = []
    for rec in records:
        ok = True
        for key, value in filters.items():
            if value is None: continue
            rv = rec.get(key)
            if isinstance(rv, list):
                ok = value in rv
            else:
                ok = str(rv).lower() == str(value).lower()
            if not ok: break
        if ok:
            out.append(rec)
        if len(out) >= limit:
            break
    return out


def latest_by_type(evidence_type: str, base: str | Path | None = None) -> dict[str, Any] | None:
    rows = query_evidence({"type": evidence_type}, base=base, limit=1)
    return rows[0] if rows else None
