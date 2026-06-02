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
        _block(
            "demo_direct",
            "direct_answer_card",
            "Operational AI Core",
            {
                "answer": "PRISMO convierte señales, evidencia y contexto técnico en decisiones operativas claras, trazables y seguras.",
                "certainty": "CONFIRMADO_POR_DOC_VIGENTE",
            },
            "full",
            "primary",
        ),
        _block(
            "demo_evidence",
            "evidence_cards",
            "Evidence Vault",
            {
                "items": [
                    {"title": "Evidencia local", "source_type": "local_read_only", "summary": "Lectura segura preparada para clasificar.", "freshness": "current"},
                    {"title": "Gobernanza", "source_type": "governance", "summary": "Reglas, permisos y límites de mutación visibles.", "freshness": "current"},
                    {"title": "Estado visual", "source_type": "visual_state", "summary": "Rutas, capturas y regresiones integrables.", "freshness": "recent"},
                ]
            },
        ),
        _block(
            "demo_authority",
            "authority_map",
            "Authority Brain",
            {
                "winning_source": "PRISMA local",
                "precedence": ["PRISMA local", "código y rutas", "evidencia temporal", "documentación vigente"],
                "warnings": ["Mutaciones bloqueadas.", "La autoridad se decide con evidencia visible."],
            },
        ),
        _block(
            "demo_neural_graph",
            "flow_diagram",
            "Neural Operations Graph",
            {
                "variant": "neural_operations_graph",
                "nodes": [
                    {"id": "control", "label": "Control Center", "status": "reads evidence"},
                    {"id": "gemini", "label": "Gemini Bridge", "status": "server-side AI"},
                    {"id": "vault", "label": "Evidence Vault", "status": "traceability"},
                    {"id": "governance", "label": "Governance Canon", "status": "governs action"},
                    {"id": "visual", "label": "Static Visual Checks", "status": "validates layers"},
                    {"id": "atlas", "label": "Dependency Atlas", "status": "maps dependency"},
                    {"id": "surfaces", "label": "PC · Tablet · Mobile", "status": "multisurface impact"},
                    {"id": "chart", "label": "Chart Lab", "status": "visual intelligence"},
                ],
                "edges": [
                    {"from": "control", "to": "vault", "label": "reads evidence"},
                    {"from": "vault", "to": "governance", "label": "supports decision"},
                    {"from": "gemini", "to": "control", "label": "feeds context"},
                ],
            },
            "full",
            "primary",
        ),
        _block(
            "demo_impact",
            "impact_map",
            "Multisurface Impact",
            {
                "groups": [
                    {"label": "UI", "risk": "low", "items": ["Control Center"]},
                    {"label": "API", "risk": "low", "items": ["/api/prismo/theater/query", "/api/prismo/status"]},
                    {"label": "DB", "risk": "low", "items": ["Sin escrituras"]},
                    {"label": "Verifier", "risk": "low", "items": ["prismo:verify"]},
                ]
            },
        ),
        _block(
            "demo_runtime",
            "runtime_map",
            "Operational Signals",
            {"signals": [{"label": "Gemini", "status": "server-side"}, {"label": "Mutaciones", "status": "blocked"}, {"label": "Modo", "status": "read-only"}]},
        ),
        _block(
            "demo_timeline",
            "timeline",
            "Decision Timeline",
            {"events": [{"time": "fase 1", "title": "Lectura segura", "status": "vigente"}, {"time": "fase 2", "title": "Evidencia gobernada", "status": "por permisos"}]},
        ),
        _block(
            "demo_brief",
            "improvement_brief_board",
            "Executive Brief",
            {
                "sections": [
                    {"title": "Impacto", "items": ["Diagnóstico más rápido.", "Evidencia centralizada.", "Decisiones más claras."]},
                    {"title": "Decisión", "items": ["Mantener lectura segura.", "Priorizar evidencia verificable."]},
                    {"title": "Siguiente paso", "items": ["Ejecutar prismo:verify y revisar evidencia estática."]},
                ]
            },
            "full",
        ),
        _block(
            "demo_context",
            "context_pack_explorer",
            "Context Pack Factory",
            {"items": [{"label": "Authority Brain", "status": "activo"}, {"label": "Evidence Vault", "status": "preparado"}, {"label": "Theater Query", "status": "visible"}]},
        ),
        _block(
            "demo_diff",
            "diff_view",
            "Authority Comparison",
            {"columns": [{"title": "Autoridad visible", "items": ["PRISMA local", "evidencia segura"]}, {"title": "Apoyo contextual", "items": ["documentación", "historial técnico"]}]},
        ),
        _block(
            "demo_risk",
            "risk_matrix",
            "Risk Matrix",
            {"items": [{"risk": "Exposición de secretos", "level": "critical", "mitigation": "IA server-side y sin llaves en frontend"}, {"risk": "Verde falso", "level": "medium", "mitigation": "Evidencia antes de afirmar"}]},
        ),
        _block(
            "demo_checklist",
            "checklist",
            "Decision Checklist",
            {"items": [{"label": "Solo lectura", "done": True}, {"label": "Mutaciones bloqueadas", "done": True}, {"label": "Evidencia trazable", "done": True}]},
        ),
    ]


def make_demo_response(mode: str, message: str, context: dict[str, Any], request_id: str, warnings: list[str] | None = None) -> dict[str, Any]:
    prompt = (message or "").lower()
    certainty = "NO_CONFIRMADO"
    answer = "PRISMO es la capa de inteligencia operacional de PRISMA: entiende señales, organiza evidencia, explica prioridades y guía la siguiente acción segura."
    safe_next = "Escribe una pregunta, pega evidencia temporal o pide un brief operativo para avanzar sin mutaciones."
    status = "success"
    risk = {"level": "low", "summary": "La consulta local no llama servicios externos ni muta estado cuando el bridge está en adaptador determinístico.", "reasons": [], "mitigations": ["Mantener consultas con evidencia verificable."]}

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
        answer = "Executive Brief generado en modo solo lectura. No se modificó código, DB ni estado operativo."
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
