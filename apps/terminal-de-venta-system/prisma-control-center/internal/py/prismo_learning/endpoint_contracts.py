"""Endpoint contract listing for PRISMO Learning."""
from __future__ import annotations
ENDPOINTS = [
    {"method":"GET","path":"/api/prismo/learning/status","public":"redacted"},
    {"method":"GET","path":"/api/prismo/learning/evidence-index","public":"redacted"},
    {"method":"GET","path":"/api/prismo/learning/recommend-protocol","public":"redacted"},
    {"method":"GET","path":"/api/prismo/learning/insights","public":"redacted"},
    {"method":"GET","path":"/api/prismo/learning/graph","public":"redacted"},
    {"method":"GET","path":"/api/prismo/learning/patterns","public":"redacted"},
    {"method":"GET","path":"/api/prismo/learning/authority","public":"redacted"},
    {"method":"GET","path":"/api/prismo/learning/f3/status","public":"safe"},
    {"method":"GET","path":"/api/prismo/learning/technical-drawer","public":"blocked/redacted"},
    {"method":"GET","path":"/api/prismo/learning/feedback/stats","public":"safe"},
    {"method":"GET","path":"/api/prismo/learning/compaction/status","public":"safe"},
    {"method":"POST","path":"/api/prismo/learning/compaction/run","public":"blocked"},
    {"method":"GET","path":"/api/prismo/learning/governance/status","public":"safe"},
    {"method":"GET","path":"/api/prismo/learning/context-enrichment","public":"redacted"},
    {"method":"GET","path":"/api/prismo/learning/action/status","public":"safe"},
    {"method":"POST","path":"/api/prismo/learning/action/preview","public":"preview-only"},
    {"method":"GET","path":"/api/prismo/learning/completion/status","public":"safe"},
    {"method":"POST","path":"/api/prismo/learning/completion/run","public":"blocked"},
    {"method":"POST","path":"/api/prismo/learning/feedback","public":"blocked"},
]
def endpoint_contracts():
    return {"schema_version":"1.4.0","endpoints":ENDPOINTS,"read_only":True,"mutation_allowed":False}
