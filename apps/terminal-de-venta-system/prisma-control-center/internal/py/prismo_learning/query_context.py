# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Learning context enhancer for the PRISMO learning API."""
from __future__ import annotations
from typing import Any
from .recommendation_engine import recommend
from .render_plan import build_render_plan


def enhance_query_context(payload: dict[str, Any], base=None) -> dict[str, Any]:
    query = str(payload.get("message") or payload.get("prompt") or payload.get("query") or "")
    rec = recommend(query, base=base, mode=str(payload.get("mode") or "ASK"))
    rec["render_plan"] = build_render_plan(rec)
    return rec
