"""Context enrichment endpoint facade."""
from __future__ import annotations
from typing import Any
from .answer_pack_builder import build_answer_pack

def context_enrichment_payload(query: str = '') -> dict[str, Any]:
    return build_answer_pack(query or 'prismo learning status')
