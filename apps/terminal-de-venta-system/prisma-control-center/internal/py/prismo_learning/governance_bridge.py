"""Governance bridge: aligns evidence, policies, canon and release train."""
from __future__ import annotations
from typing import Any
from .canon_resolver import governance_canon_summary
from .release_train_alignment import release_train_status
from .policy_checks import check_learning_policy
from .clock import now_iso
from .memory_store import write_store

def governance_status() -> dict[str, Any]:
    payload = {
        'ok': True, 'status':'available', 'phase':'F7 Governance Bridge', 'generated_at': now_iso(),
        'canon': governance_canon_summary(), 'release_train': release_train_status(),
        'policy': check_learning_policy({'read_only': True, 'mutation_allowed': False, 'actions': []}),
        'read_only': True, 'mutation_allowed': False,
    }
    write_store('governance', payload)
    return payload
