"""PRISMO Theater Query Blueprint

Codex should adapt this blueprint into the real Control Center backend.
It unifies existing learning endpoints/adapters into one response contract for the UI.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

@dataclass
class TheaterQuery:
    objective: str
    domain: str
    lens: str
    freeText: str = ""
    contextNote: str = ""
    autoRender: bool = True


def select_blocks(query: TheaterQuery, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    blocks.append({"id":"hero","type":"hero_response","title":"PRISMO revisó la solicitud","priority":100,"payload":{"summary":query.freeText or "Consulta preparada"}})
    if query.objective in {"diagnose","audit","prepare_action"}:
        blocks.append({"id":"risk","type":"risk_matrix","title":"Riesgos y prioridad","priority":82,"payload":{"items":context.get("risks", [])}})
    if query.lens in {"procedural_memory","protocols"}:
        blocks.append({"id":"steps","type":"procedural_steps","title":"Protocolo sugerido","priority":88,"payload":{"steps":context.get("procedural_steps", [])}})
    if context.get("evidence"):
        blocks.append({"id":"evidence","type":"evidence_board","title":"Evidencia usada","priority":74,"payload":{"evidence":context.get("evidence", [])[:5]}})
    if context.get("memory_used"):
        blocks.append({"id":"memory","type":"memory_trace","title":"Memoria consultada","priority":68,"collapseDefault":True,"payload":{"memory":context.get("memory_used", [])}})
    blocks.append({"id":"actions","type":"action_bar","title":"Acciones","priority":60,"payload":{"actions":context.get("actions", [])}})
    return sorted(blocks, key=lambda b: b.get("priority", 0), reverse=True)


def build_theater_response(payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    query = TheaterQuery(**payload)
    blocks = select_blocks(query, context)
    return {
        "schema":"prismo.theater.query.response.v1",
        "input": asdict(query),
        "autoRender": True,
        "visualPreset": context.get("visualPreset", "refrigerant_emerald_theater"),
        "hero": blocks[0] if blocks else None,
        "blocks": blocks[1:] if blocks else [],
        "evidenceRefs": context.get("evidenceRefs", []),
        "memoryRefs": context.get("memoryRefs", []),
        "technicalTrace": context.get("technicalTrace", {}),
        "feedbackHooks": ["helpful","not_helpful","save_protocol","save_reference"],
    }
