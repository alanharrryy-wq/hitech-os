"""Build safe action previews."""
from __future__ import annotations
from typing import Any
from .action_contracts import normalize_action_request
from .approval_gate import approval_gate
from .rollback_planner import rollback_plan_for

def build_action_preview(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    action = normalize_action_request(payload)
    if action['blocked']:
        title = 'Acción bloqueada por seguridad'
        steps = ['No se ejecutará esta acción en PRISMO Learning V1.', 'Usa diagnóstico y evidencia primero.', 'Requiere aprobación explícita en una fase posterior.']
    else:
        title = action['title']
        steps = action.get('steps') or ['Revisar evidencia relacionada.', 'Confirmar protocolo recomendado.', 'Generar reporte antes de ejecutar cualquier cambio externo.']
    return {'ok': True, 'status':'preview_only', 'title': title, 'action': action, 'steps': steps, 'approval_gate': approval_gate(action), 'rollback_plan': rollback_plan_for(action), 'read_only': True, 'mutation_allowed': False}
