# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Memory compaction without losing traceability."""
from __future__ import annotations
from typing import Any
from .memory_store import read_store, write_store


def compact_episodic_memory(max_full: int = 500, base=None) -> dict[str, Any]:
    store = read_store("episodic", {"episodes": []}, base)
    episodes = list(store.get("episodes", []))
    full = episodes[:max_full]
    older = episodes[max_full:]
    summary = {
        "old_episode_count": len(older),
        "outcomes": {},
        "surfaces": {},
        "preserved_evidence_ids": sorted({eid for e in older for eid in e.get("evidence_ids", [])})[:1000],
    }
    for ep in older:
        summary["outcomes"][ep.get("outcome", "UNKNOWN")] = summary["outcomes"].get(ep.get("outcome", "UNKNOWN"), 0) + 1
        summary["surfaces"][ep.get("surface", "unknown")] = summary["surfaces"].get(ep.get("surface", "unknown"), 0) + 1
    store["episodes"] = full
    store.setdefault("compacted_summaries", []).insert(0, summary)
    write_store("episodic", store, base)
    return summary
