"""Human copy for safe presentation."""
from __future__ import annotations
from typing import Any

def status_sentence(evidence_count: int, pattern_count: int) -> str:
    if evidence_count <= 0:
        return 'PRISMO Learning está seguro, pero todavía sin evidencia indexada.'
    if pattern_count <= 0:
        return f'PRISMO Learning tiene {evidence_count} evidencias y está listo para detectar patrones.'
    return f'PRISMO Learning opera en modo seguro con {evidence_count} evidencias y {pattern_count} patrones detectados.'

def next_action(patterns: list[dict[str, Any]], evidence_count: int) -> dict[str, Any]:
    if not evidence_count:
        return {'title':'Cargar evidencia segura','reason':'El Vault está vacío.','action':'Ejecutar Evidence Intake local'}
    if patterns:
        top = patterns[0]
        label = top.get('label') or top.get('id') or top.get('signal') or 'patrón principal'
        return {'title':'Revisar patrón principal','reason':f'El patrón más relevante es {label}.','action':'Abrir modo Perito si necesitas detalle'}
    return {'title':'Mantener vigilancia','reason':'Hay evidencia, pero sin patrón crítico dominante.','action':'Revisar recomendaciones'}
