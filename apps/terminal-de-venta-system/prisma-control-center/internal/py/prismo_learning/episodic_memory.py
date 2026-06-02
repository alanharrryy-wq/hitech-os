# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Episodic memory: operational events and validation outcomes."""
from __future__ import annotations
from typing import Any
from .clock import now_iso
from .hashes import stable_json_hash
from .memory_store import read_store, write_store


def record_episode(event_type: str, summary: str, evidence_ids: list[str] | None = None, surface: str = "unknown", outcome: str = "UNKNOWN", base=None) -> dict[str, Any]:
    episode = {
        "id": "episode_" + stable_json_hash({"event_type": event_type, "summary": summary, "at": now_iso()})[:16],
        "event_type": event_type,
        "summary": summary,
        "evidence_ids": evidence_ids or [],
        "timestamp": now_iso(),
        "surface": surface,
        "outcome": outcome,
    }
    store = read_store("episodic", {"schema_version": "1.0.0", "episodes": []}, base)
    store["episodes"] = [episode] + list(store.get("episodes", []))[:4999]
    write_store("episodic", store, base)
    return episode


def recent_episodes(limit: int = 50, base=None) -> list[dict[str, Any]]:
    return list(read_store("episodic", {"episodes": []}, base).get("episodes", []))[:limit]
