"""Graph simplification for safe UI."""
from __future__ import annotations
from typing import Any
from .graph_builder import graph_from_registry
from .noise_budget import budget_for_mode

NODE_WEIGHT_KEYS = ('weight','authority_score','count','confidence')

def _node_weight(n: dict[str, Any]) -> float:
    for k in NODE_WEIGHT_KEYS:
        try: return float(n.get(k) or 0)
        except Exception: pass
    return 0.0

def graph_digest(mode: str | None = None) -> dict[str, Any]:
    graph = graph_from_registry()
    budget = budget_for_mode(mode)
    nodes = list(graph.get('nodes') or [])
    edges = list(graph.get('edges') or [])
    nodes = sorted(nodes, key=_node_weight, reverse=True)[:budget['graph_nodes']]
    ids = {n.get('id') for n in nodes}
    edges = [e for e in edges if e.get('source') in ids and e.get('target') in ids][:budget['graph_edges']]
    return {'nodes': nodes, 'edges': edges, 'node_count': len(graph.get('nodes') or []), 'edge_count': len(graph.get('edges') or []), 'read_only': True, 'mutation_allowed': False}
