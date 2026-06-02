"""Closed-by-default technical drawer payloads."""
from __future__ import annotations
from typing import Any
from .evidence_digest import evidence_digest
from .pattern_digest import pattern_digest
from .graph_digest import graph_digest
from .authority_store import load_authority_summary

SECTIONS = ['evidence','patterns','authority','graph','reports']

def technical_drawer_payload(mode: str | None = 'safe', include: list[str] | None = None) -> dict[str, Any]:
    include = include or SECTIONS
    payload: dict[str, Any] = {'status':'available','default_open': False, 'sections': {}, 'read_only': True, 'mutation_allowed': False}
    if 'evidence' in include: payload['sections']['evidence'] = evidence_digest(mode='perito', public=False)
    if 'patterns' in include: payload['sections']['patterns'] = pattern_digest(mode='perito')
    if 'authority' in include: payload['sections']['authority'] = load_authority_summary()
    if 'graph' in include: payload['sections']['graph'] = graph_digest(mode='perito')
    if 'reports' in include: payload['sections']['reports'] = {'known_reports':['f2_intake_report.json','f3_pattern_authority_report.json','f4_to_f9_completion_report.json']}
    return payload
