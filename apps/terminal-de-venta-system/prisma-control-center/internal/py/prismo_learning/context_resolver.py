# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Context resolver for PRISMO query payloads."""
from __future__ import annotations
from typing import Any
from .surface_detector import detect_surfaces


def resolve_context(payload: dict[str, Any]) -> dict[str, Any]:
    query = str(payload.get("query") or payload.get("message") or payload.get("prompt") or "")
    explicit = payload.get("surface")
    surfaces = [explicit] if explicit else detect_surfaces(query)
    return {"query": query, "surfaces": surfaces, "mode": str(payload.get("mode") or "ASK").upper()}
