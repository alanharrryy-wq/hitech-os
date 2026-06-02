"""Build a compact answer pack for PRISMO UI/query."""
from __future__ import annotations
from typing import Any
from .query_enricher import enrich_query_context

def build_answer_pack(query: str) -> dict[str, Any]:
    ctx = enrich_query_context(query)
    top_protocols = (ctx.get('recommendation') or {}).get('selected_protocols') or []
    return {
        'ok': True, 'status': 'available', 'query': query,
        'summary_cards': [
            {'title':'Protocolos sugeridos','items': top_protocols[:3]},
            {'title':'Evidencia relacionada','items': ctx.get('evidence', [])[:5]},
            {'title':'Patrones relevantes','items': ctx.get('patterns', [])[:3]},
        ],
        'context': ctx,
        'read_only': True, 'mutation_allowed': False,
    }
