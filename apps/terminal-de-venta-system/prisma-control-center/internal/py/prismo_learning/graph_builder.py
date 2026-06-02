# PRISMO Learning Core V1.2 F3
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: pattern-miner + authority-brain, local store writes only, read-only against repo/DB/secrets.
# Standard library only.

"""Neural Operations Graph builder enriched by F3 patterns and authority."""
from __future__ import annotations
from typing import Any
from .evidence_registry import load_registry
from .authority_store import top_authority
from .pattern_reporter import high_priority_patterns

def graph_from_registry(registry: dict[str, Any] | None = None, base=None) -> dict[str, Any]:
    records = list((registry or load_registry(base)).get("records") or [])
    nodes: list[dict[str, Any]] = []; edges: list[dict[str, Any]] = []; type_seen=set(); status_seen=set()
    for r in records[:300]:
        typ=str(r.get("type") or "unknown"); status=str(r.get("status") or "UNKNOWN")
        if typ not in type_seen: nodes.append({"id":"type:"+typ,"label":typ,"kind":"evidence_type"}); type_seen.add(typ)
        if status not in status_seen: nodes.append({"id":"status:"+status,"label":status,"kind":"status"}); status_seen.add(status)
        edges.append({"source":"type:"+typ,"target":"status:"+status,"kind":"has_status"})
    for p in high_priority_patterns(30, base):
        pid="pattern:"+str(p.get("id")); nodes.append({"id":pid,"label":p.get("id"),"kind":"pattern","priority":p.get("priority"),"count":p.get("count")})
        for proto in p.get("recommended_protocols") or []:
            pr="protocol:"+str(proto); nodes.append({"id":pr,"label":proto,"kind":"protocol"}); edges.append({"source":pid,"target":pr,"kind":"recommends"})
    for ev in top_authority(20, base):
        eid="authority:"+str(ev.get("id")); nodes.append({"id":eid,"label":ev.get("safe_source_label"),"kind":"authority_evidence","score":ev.get("authority_score"),"status":ev.get("status")})
        if ev.get("type"): edges.append({"source":eid,"target":"type:"+str(ev.get("type")),"kind":"classified_as"})
    dedup={}
    for n in nodes: dedup[n["id"]]=n
    return {"ok": True, "status": "available", "nodes": list(dedup.values())[:220], "edges": edges[:420], "read_only": True, "mutation_allowed": False}
