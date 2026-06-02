"""PRISMO UI1P render plan blueprint.

Codex should adapt this to the real render_plan.py without replacing existing learning logic.

Key correction in fix2:
- No removed format selector / no user-selected scene.
- No references to a scene field.
- Auto Render Ensemble selects all useful render blocks from objective + domain + lens + context.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


ALLOWED_BLOCKS = {
    "hero_response",
    "executive_brief",
    "next_action",
    "action_bar",
    "checklist",
    "timeline",
    "risk_matrix",
    "evidence_board",
    "flow_diagram",
    "decision_summary",
    "protocol_ladder",
    "authority_strip",
    "comparison_board",
    "insight_chips",
    "detail_drawer",
    "memory_trace",
    "feedback_panel",
    "memory_card",
    "procedural_steps",
    "procedural_recipe",
    "episodic_trace",
    "semantic_fact_grid",
    "visual_recipe_card",
    "governance_notice",
    "operational_status",
    "chart_spec_preview",
    "question_stack",
    "recommendation_ladder",
}

FORBIDDEN_BLOCKS = {
    "raw_html",
    "script",
    "iframe",
    "unbounded_markdown",
    "output_format_dropdown",
    "raw_json_main",
    "giant_table_main",
    "full_graph_main",
}

DEFAULT_PRIORITY = {
    "hero_response": 100,
    "next_action": 95,
    "executive_brief": 90,
    "protocol_ladder": 82,
    "procedural_steps": 80,
    "risk_matrix": 76,
    "flow_diagram": 70,
    "timeline": 68,
    "evidence_board": 64,
    "memory_trace": 58,
    "detail_drawer": 20,
    "feedback_panel": 10,
}


@dataclass
class ComposerIntent:
    objective: str
    domain: str
    lens: str
    free_text: str = ""
    context_note: str = ""


@dataclass
class RenderBlock:
    id: str
    type: str
    title: str
    summary: str = ""
    priority: int = 50
    confidence: float = 0.84
    payload: Dict[str, Any] = field(default_factory=dict)
    evidenceRefs: List[str] = field(default_factory=list)
    memoryRefs: List[str] = field(default_factory=list)


def stable_block_id(block: Dict[str, Any], index: int = 0) -> str:
    """Generate a deterministic candidate ID; frontend can override with persisted IDs."""
    raw = f"{block.get('type','block')}|{block.get('title','PRISMO')}|{index}"
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in raw).strip("-")
    return f"prismo-{safe[:80]}"


def normalize_block(block: Dict[str, Any], index: int = 0) -> Dict[str, Any]:
    t = block.get("type")
    if t in FORBIDDEN_BLOCKS:
        raise ValueError(f"Forbidden render block: {t}")
    if t not in ALLOWED_BLOCKS:
        block["type"] = "executive_brief"
    block.setdefault("id", stable_block_id(block, index))
    block.setdefault("title", "PRISMO")
    block.setdefault("summary", "")
    block.setdefault("payload", {})
    block.setdefault("priority", DEFAULT_PRIORITY.get(block["type"], 50))
    block.setdefault("confidence", 0.84)
    return block


def auto_render_ensemble(intent: ComposerIntent, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Select every useful block automatically.

    The user does not select a display format. PRISMO chooses the visual surfaces
    that match objective + domain + lens + evidence + memory.
    """
    blocks: List[Dict[str, Any]] = []
    objective = (intent.objective or "").lower()
    domain = (intent.domain or "").lower()
    lens = (intent.lens or "").lower()

    if objective in {"diagnose", "audit", "compare"} or context.get("risks"):
        blocks.append({
            "type": "risk_matrix",
            "title": "Riesgos detectados",
            "summary": "Prioridades y puntos delicados encontrados por PRISMO.",
            "payload": {"items": context.get("risks", [])},
        })

    if lens in {"procedural_memory", "protocols"} or objective in {"prepare_action", "recommend", "diagnose"}:
        blocks.append({
            "type": "procedural_steps",
            "title": "Ruta procedural sugerida",
            "summary": "Pasos recomendados con base en memoria procedural y protocolos previos.",
            "payload": {"steps": context.get("steps", [])},
        })

    if context.get("protocol"):
        blocks.append({
            "type": "protocol_ladder",
            "title": "Protocolo recomendado",
            "summary": "Escalera de decisión elegida por el motor.",
            "payload": {"protocol": context.get("protocol")},
        })

    if context.get("evidence"):
        blocks.append({
            "type": "evidence_board",
            "title": "Evidencia relevante",
            "summary": "Evidencia resumida; detalle completo bajo demanda.",
            "payload": {"items": context.get("evidence", [])[:8]},
        })

    if context.get("timeline"):
        blocks.append({
            "type": "timeline",
            "title": "Secuencia de eventos",
            "summary": "Historia útil para entender el estado actual.",
            "payload": {"items": context.get("timeline", [])},
        })

    if context.get("flow") or domain in {"sync", "governance", "pc_ui", "learning"}:
        blocks.append({
            "type": "flow_diagram",
            "title": "Flujo de decisión",
            "summary": "Cómo PRISMO conecta intención, memoria, evidencia y salida visual.",
            "payload": {"nodes": context.get("flow", [])},
        })

    if context.get("comparison"):
        blocks.append({
            "type": "comparison_board",
            "title": "Comparación",
            "summary": "Diferencias detectadas entre opciones, fases o estados.",
            "payload": {"items": context.get("comparison", [])},
        })

    if context.get("chart_option"):
        blocks.append({
            "type": "chart_spec_preview",
            "title": "Vista visual de datos",
            "summary": "Preview gobernado de especificación visual.",
            "payload": {"option": context.get("chart_option")},
        })

    if context.get("memory_trace"):
        blocks.append({
            "type": "memory_trace",
            "title": "Memoria usada",
            "summary": "Memoria semántica, episódica, procedural, operativa, visual y governance.",
            "payload": {"items": context.get("memory_trace", [])},
        })

    if not blocks:
        blocks.append({
            "type": "executive_brief",
            "title": "Respuesta ejecutiva",
            "summary": intent.free_text or "PRISMO generó una respuesta ejecutiva con el contexto disponible.",
            "payload": {"domain": intent.domain, "lens": intent.lens},
        })

    return [normalize_block(block, i) for i, block in enumerate(blocks)]


def build_render_plan(intent: ComposerIntent, memory_context: Dict[str, Any]) -> Dict[str, Any]:
    """Build a clean Theater render plan.

    No output-format selector and no removed format selector. The plan always returns:
    hero + blocks + actions + detail drawer + trace.
    """
    hero = normalize_block({
        "type": "hero_response",
        "title": "PRISMO estructuró la respuesta",
        "summary": f"{intent.objective} · {intent.domain} · {intent.lens}",
        "payload": {"intent": asdict(intent)},
        "priority": 100,
    })

    blocks = auto_render_ensemble(intent, memory_context)

    next_action = normalize_block({
        "type": "next_action",
        "title": "Siguiente mejor acción",
        "summary": memory_context.get("next_action", "Revisar la recomendación, abrir evidencia si hace falta y preparar acción segura."),
        "payload": {"actions": memory_context.get("actions", [])},
        "priority": 95,
    })

    detail = normalize_block({
        "type": "detail_drawer",
        "title": "Detalle técnico",
        "summary": "Evidencia, memoria, protocolos y trazabilidad bajo demanda.",
        "payload": memory_context,
        "priority": 20,
    })

    return {
        "version": "ui1p.render_plan.fix2",
        "autoRender": True,
        "hero": hero,
        "blocks": [next_action] + blocks + [detail],
        "actions": memory_context.get("actions", []),
        "trace": {
            "intent": asdict(intent),
            "memory_context_keys": list(memory_context.keys()),
            "format_selected_by_user": False,
            "auto_render_ensemble": True,
        },
    }
