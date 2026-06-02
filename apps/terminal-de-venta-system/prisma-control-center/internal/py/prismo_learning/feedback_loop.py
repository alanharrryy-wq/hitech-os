# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Read-only-safe feedback loop.

Feedback does not execute actions. It records a small local event in the learning store
when called from local Control Center only. Public calls should be blocked by route layer.
"""
from __future__ import annotations
from typing import Any
from .episodic_memory import record_episode


def record_feedback(payload: dict[str, Any], base=None) -> dict[str, Any]:
    rating = str(payload.get("rating") or payload.get("outcome") or "unknown")[:80]
    summary = str(payload.get("summary") or payload.get("comment") or "PRISMO learning feedback")[:500]
    ep = record_episode("feedback", summary, surface="prismo", outcome=rating.upper(), base=base)
    return {"ok": True, "status": "recorded", "episode": ep, "read_only": True, "mutation_allowed": False}
