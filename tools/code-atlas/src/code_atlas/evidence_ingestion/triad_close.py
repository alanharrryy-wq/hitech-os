# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
from .surface_resolver import build_surface_aware_index
from .db_schema_decisions import build_db_ghost_decisions
from .runtime_evidence_collector import collect_runtime_evidence
def load_json(path:Path,default=None):
    try: return json.loads(path.read_text(encoding='utf-8', errors='replace'))
    except Exception: return {} if default is None else default
def write_json(path:Path,obj): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
def run_triad_close(repo_root:str,out_root:str='F:/descargasf')->Dict[str,Any]:
    repo=Path(repo_root); registers=repo/'tools/code-atlas/evidence_ingestion/current/registers'; registers.mkdir(parents=True, exist_ok=True)
    surface=build_surface_aware_index(repo,registers); db_decisions=build_db_ghost_decisions(registers); runtime=collect_runtime_evidence(Path(out_root))
    write_json(registers/'SURFACE_AWARE_ATLAS_NODE_RESOLVER.json',surface); write_json(registers/'ATLAS_NODE_RESOLUTION_REGISTER.json',surface); write_json(registers/'DB_GHOST_RELATION_DECISION_REGISTER.json',db_decisions); write_json(registers/'RUNTIME_LIVE_EVIDENCE_REGISTER.json',runtime)
    production=load_json(registers/'PRODUCTION_GATE_MATRIX.json',{})
    if not isinstance(production,dict): production={}
    production.update({'status':'BLOCKED_PRODUCTION_READINESS_TRUTHFUL_AFTER_TRIAD','productionGreenAllowed':False,'productionCertified':False,'triadClosed':True,'triadBlockers':runtime.get('productionBlockers',[]),'requires':['complete sales/tender/canonical provenance','runtime artifacts linked to production gate rows','DB schema/migration decisions for ghost relations']})
    write_json(registers/'PRODUCTION_GATE_MATRIX.json',production)
    blockers={'status':'BLOCKED_PRODUCTION_READINESS_TRUTHFUL_AFTER_TRIAD','productionGreenAllowed':False,'blockers':runtime.get('productionBlockers',[]),'doesProve':['source gates triad has been closed/classified','production block is explicit'],'doesNotProve':['live production certification','complete provenance']}
    write_json(registers/'PRODUCTION_READINESS_BLOCKERS_REGISTER.json',blockers)
    ep=load_json(registers/'EVIDENCE_PROVES_DOES_NOT_PROVE.json',{})
    if not isinstance(ep,dict): ep={}
    ep['atlastriad']={'proves':['surface-aware Atlas resolver exists and classified paths by owner role','DB ghost relations are classified into decision gates','existing runtime/live evidence artifacts were inventoried without touching runtime','production remains blocked truthfully'],'doesNotProve':['semantic Atlas coverage is complete','DB schema/migrations are corrected','fresh runtime/live tests were executed','production readiness is green']}
    write_json(registers/'EVIDENCE_PROVES_DOES_NOT_PROVE.json',ep)
    queue="# NEXT GATES QUEUE\n\n## Closed by atlastriad\n\n- DONE: BUILD surface-aware Atlas node resolver\n- DONE: DECIDE/CLASSIFY DB schema/migration treatment for ghost relations\n- DONE: COLLECT existing runtime/live evidence artifacts without launching runtime\n- BLOCKED: Production readiness remains red until provenance/runtime/schema decisions close\n\n## Remaining gates\n\n1. VERIFY surface resolver reduces missing atlas nodes by owner and excludes docs/cache noise.\n2. HUMAN DECISION: approve DB schema/migration treatment for ghost relations.\n3. LINK runtime artifacts to production gate rows; collect missing live evidence only if explicitly approved.\n4. CLOSE sales/tender/canonical provenance before any production green claim.\n"
    (registers/'NEXT_GATES_QUEUE.md').write_text(queue, encoding='utf-8')
    report={'status':'PASS_ATLAS_TRIAD_CLOSED_PRODUCTION_STILL_BLOCKED','surfaceResolver':surface['status'],'dbGhostDecisions':db_decisions['status'],'runtimeEvidence':runtime['status'],'productionGreenAllowed':False,'registersWritten':['SURFACE_AWARE_ATLAS_NODE_RESOLVER.json','ATLAS_NODE_RESOLUTION_REGISTER.json','DB_GHOST_RELATION_DECISION_REGISTER.json','RUNTIME_LIVE_EVIDENCE_REGISTER.json','PRODUCTION_READINESS_BLOCKERS_REGISTER.json','PRODUCTION_GATE_MATRIX.json','EVIDENCE_PROVES_DOES_NOT_PROVE.json','NEXT_GATES_QUEUE.md'],'summary':{'surfaceTotalResolvedCandidates':surface.get('totalResolvedCandidates'),'surfaceUnknownCount':surface.get('unknownCount'),'ghostRelationsClassified':db_decisions.get('totalGhostRelationsClassified'),'runtimeZipsInspected':runtime.get('totalZipsInspected'),'runtimeLikeEvidenceCount':runtime.get('runtimeLikeEvidenceCount'),'dbEvidenceCount':runtime.get('dbEvidenceCount')}}
    write_json(registers/'TRIAD_GATE_CLOSURE.json',report)
    md=['# Atlas Triad Gate Closure','','`PASS_ATLAS_TRIAD_CLOSED_PRODUCTION_STILL_BLOCKED`','','## Closed','','- DONE: surface-aware Atlas node resolver built','- DONE: DB ghost relation treatment classified as decision gates, no schema edits','- DONE: existing runtime/live evidence artifacts collected, no runtime launched','- BLOCKED: production remains red truthfully','','## Summary','',f"- Surface candidates: `{surface.get('totalResolvedCandidates')}`",f"- Unknown paths: `{surface.get('unknownCount')}`",f"- Ghost relations classified: `{db_decisions.get('totalGhostRelationsClassified')}`",f"- Runtime/evidence ZIPs inspected: `{runtime.get('totalZipsInspected')}`",f"- Runtime-like evidence count: `{runtime.get('runtimeLikeEvidenceCount')}`",'','## Does not prove','','- Production green','- Complete sales/tender/canonical provenance','- Fresh runtime/browser test execution','- DB schema/migration correction']
    (registers/'TRIAD_GATE_CLOSURE_REPORT.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
    return report
