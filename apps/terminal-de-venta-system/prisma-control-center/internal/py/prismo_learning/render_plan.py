# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Render plan builder for PRISMO AI1 UI zones."""
from __future__ import annotations
from typing import Any


def build_render_plan(recommendation: dict[str, Any]) -> dict[str, Any]:
    protocols = recommendation.get("selected_protocols") or []
    blocks = [
        {"type": "protocol_ladder", "title": "Protocol Ladder", "items": protocols},
        {"type": "authority_brain", "title": "Authority Brain", "authority": recommendation.get("authority")},
        {"type": "decision_pipeline", "title": "Decision Pipeline", "trace": recommendation.get("decision_trace")},
        {"type": "evidence_vault", "title": "Evidence Vault", "items": recommendation.get("evidence_used", [])},
    ]
    return {"schema_version": "1.0.0", "blocks": blocks, "read_only": True}
