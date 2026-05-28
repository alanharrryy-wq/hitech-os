from __future__ import annotations

from typing import Any


def _safety() -> dict[str, Any]:
    return {
        "trusted": False,
        "sanitized": True,
        "interactive": False,
        "allows_scripts": False,
        "allows_network": False,
        "allows_forms": False,
        "reason": "Demo provider deterministic safe block.",
    }


def _block(block_id: str, block_type: str, title: str, data: Any, layout: str = "half", priority: str = "secondary") -> dict[str, Any]:
    return {
        "id": block_id,
        "type": block_type,
        "title": title,
        "priority": priority,
        "layout": layout,
        "safety": _safety(),
        "data": data,
    }


def demo_blocks() -> list[dict[str, Any]]:
    return [
        _block("demo_direct", "direct_answer_card", "Respuesta directa", {"answer": "PRISMO está en modo demo seguro y responde con estructura validada.", "certainty": "NO_CONFIRMADO"}, "full", "primary"),
        _block(
            "demo_evidence",
            "evidence_cards",
            "Evidence deck",
            {
                "items": [
                    {"title": "Current State", "source_type": "current_state", "summary": "Autoridad vigente si existe en contexto local.", "freshness": "current"},
                    {"title": "Legacy", "source_type": "doc_legacy", "summary": "Historia útil, nunca autoridad vigente.", "freshness": "stale"},
                    {"title": "Temporal", "source_type": "temporary_file", "summary": "Evidencia pegada por operador.", "freshness": "recent"},
                ]
            },
        ),
        _block(
            "demo_authority",
            "authority_map",
            "Authority map",
            {
                "winning_source": "PRISMA_CURRENT_STATE",
                "precedence": ["current_state", "code/runtime", "doc_current", "temporary", "planned", "legacy"],
                "warnings": ["Legacy no manda sobre current.", "Planned no equivale a implementado."],
            },
        ),
        _block(
            "demo_flow",
            "flow_diagram",
            "Ruta real PC → Tablet",
            {
                "nodes": [
                    {"id": "pc", "label": "PC Backoffice", "status": "confirmed"},
                    {"id": "delta", "label": "catalog-delta", "status": "confirmed"},
                    {"id": "tablet", "label": "Tablet pull", "status": "confirmed"},
                ],
                "edges": [
                    {"from": "pc", "to": "delta", "label": "export"},
                    {"from": "delta", "to": "tablet", "label": "pull"},
                ],
            },
        ),
        _block(
            "demo_impact",
            "impact_map",
            "Impact map",
            {
                "groups": [
                    {"label": "UI", "risk": "low", "items": ["Control Center"]},
                    {"label": "API", "risk": "medium", "items": ["/api/prismo/query"]},
                    {"label": "DB", "risk": "none", "items": ["No DB touch"]},
                    {"label": "Verifier", "risk": "low", "items": ["verify-prismo-command-nexus"]},
                ]
            },
        ),
        _block(
            "demo_runtime",
            "runtime_map",
            "Runtime signals",
            {"signals": [{"label": "Bridge", "status": "demo"}, {"label": "Mutation", "status": "blocked"}, {"label": "HTML", "status": "off"}]},
        ),
        _block(
            "demo_timeline",
            "timeline",
            "Timeline",
            {"events": [{"time": "v1", "title": "Read-only", "status": "current"}, {"time": "future", "title": "Function calling", "status": "planned"}]},
        ),
        _block(
            "demo_brief",
            "improvement_brief_board",
            "Improvement Brief",
            {
                "sections": [
                    {"title": "Intento entendido", "items": ["Analizar sin modificar."]},
                    {"title": "Riesgos", "items": ["No tratar legacy como current.", "No editar DB."]},
                    {"title": "Verificadores", "items": ["node scripts/verify-prismo-command-nexus.mjs"]},
                ]
            },
            "full",
        ),
        _block(
            "demo_context",
            "context_pack_explorer",
            "Context pack",
            {"items": [{"label": "Authority", "status": "loaded/demo"}, {"label": "Runtime", "status": "optional"}, {"label": "Evidence", "status": "temporal"}]},
        ),
        _block(
            "demo_diff",
            "diff_view",
            "Current vs legacy",
            {"columns": [{"title": "CURRENT", "items": ["catalog-delta"]}, {"title": "LEGACY/STUB", "items": ["export-pc-to-tablet"]}]},
        ),
        _block(
            "demo_risk",
            "risk_matrix",
            "Risk matrix",
            {"items": [{"risk": "Secret exposure", "level": "critical", "mitigation": "backend-only env"}, {"risk": "False green", "level": "medium", "mitigation": "NO_CONFIRMADO"}]},
        ),
        _block(
            "demo_checklist",
            "checklist",
            "Checklist",
            {"items": [{"label": "Read-only", "done": True}, {"label": "Demo fallback", "done": True}, {"label": "No function calling", "done": True}]},
        ),
        _block("demo_html", "html_sandbox_preview", "HTML preview apagado", {"html": "<div>Preview seguro sin scripts</div>", "enabled": False}),
        _block("demo_chart", "chart_spec", "Chart spec seguro", {"xAxis": {"type": "category", "data": ["ASK", "INSPECT", "IMPROVE", "EVIDENCE"]}, "series": [{"type": "bar", "data": [1, 1, 1, 1]}]}),
    ]


def make_demo_response(mode: str, message: str, context: dict[str, Any], request_id: str, warnings: list[str] | None = None) -> dict[str, Any]:
    prompt = (message or "").lower()
    certainty = "NO_CONFIRMADO"
    answer = "PRISMO está en modo demo seguro: puede explicar, clasificar evidencia y generar briefs sin ejecutar acciones."
    safe_next = "Pega evidencia temporal o pide un Improvement Brief para avanzar sin mutaciones."
    status = "success"
    risk = {"level": "low", "summary": "Demo mode no llama servicios externos ni muta estado.", "reasons": [], "mitigations": ["Mantener consultas read-only."]}

    if "endpoint x" in prompt or "aunque no tengas evidencia" in prompt:
        answer = "No hay evidencia suficiente para confirmar ese endpoint. PRISMO debe marcarlo como NO_CONFIRMADO."
        certainty = "NO_CONFIRMADO"
        risk["level"] = "medium"
        risk["reasons"] = ["El prompt pide confirmar sin evidencia."]
    elif "plan" in prompt or "planned" in prompt or "implementado" in prompt:
        answer = "Un plan no confirma implementación. Si sólo aparece en roadmap, debe clasificarse como PLANEADO_NO_IMPLEMENTADO."
        certainty = "PLANEADO_NO_IMPLEMENTADO"
        risk["level"] = "medium"
        safe_next = "Busca evidencia current, código o verificador antes de llamarlo implementado."
    elif "legacy" in prompt:
        answer = "Legacy no manda como autoridad vigente. Puede servir como historia, pero PRISMO debe resolver con current state, código o docs vigentes."
        certainty = "CONFIRMADO_POR_DOC_VIGENTE"
        risk["level"] = "medium"
        safe_next = "Contrasta legacy contra current state y marca divergencias visibles."
    elif mode == "IMPROVE":
        answer = "Improvement Brief generado en modo read-only. No se modificó código, DB ni runtime."
        certainty = "NO_CONFIRMADO"
        safe_next = "Ejecuta los verificadores propuestos antes de aprobar cualquier cambio real."
    elif mode == "EVIDENCE":
        answer = "Evidencia clasificada por autoridad: current manda, temporal apoya, planned no confirma, legacy no decide."
        certainty = "CONFIRMADO_POR_DOC_VIGENTE"

    evidence = [
        {
            "id": "ev_demo_current",
            "title": "PRISMO v1 contract",
            "source_type": "doc_current",
            "summary": "PRISMO v1 es read-only, evidence-first y backend-only.",
            "confidence": "high",
            "freshness": "current",
        },
        {
            "id": "ev_demo_runtime",
            "title": "Demo provider",
            "source_type": "runtime_report",
            "summary": "Fallback determinístico cuando la llave no está visible o se fuerza demo.",
            "confidence": "high",
            "freshness": "recent",
        },
    ]
    return {
        "ok": True,
        "status": status,
        "request_id": request_id,
        "mode": mode,
        "demo_mode": True,
        "read_only": True,
        "mutation_allowed": False,
        "direct_answer": answer,
        "certainty_level": certainty,
        "authority": {
            "winning_source": "PRISMO v1 read-only contract",
            "winning_source_type": "current_doc",
            "precedence_applied": context.get("authorityRules", []),
            "notes": "Demo provider no confirma estado externo sin evidencia.",
        },
        "evidence": evidence,
        "legacy_warning": {"applies": "legacy" in prompt, "legacy_sources": ["docs legacy"], "warning": "Legacy no manda sobre current."},
        "risk": risk,
        "safe_next_step": safe_next,
        "render_blocks": demo_blocks(),
        "warnings": list(warnings or []),
        "errors": [],
        "meta": {
            "provider": "demo",
            "schema_version": "1.0.0",
            "generated_at": "",
            "input_chars": len(message or ""),
            "render_block_count": len(demo_blocks()),
        },
    }
