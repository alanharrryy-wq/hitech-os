#!/usr/bin/env python3
"""Fail-closed anti-rework gate for PRISMA Change Intelligence."""
from __future__ import annotations
import argparse, copy, json, subprocess
from pathlib import Path
from typing import Any

SCHEMA="prisma.change_intelligence.capability_map.v1"
MAP_REL=Path("PRISMA Factory Ledger/PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP.json")
VALID={"DONE","VERIFY","FIX","BUILD","EXTERNAL"}
REQ_POLICY=("mandatoryBeforeTechnicalProposal","mandatoryBeforeRepositoryMutation","factoryLedgerFirst","capabilityIdsRequired","failClosedOnUnknownCapability","failClosedOnContradiction","failClosedOnStaleAuthorityForMutation","noRebuildWhenDoNotRebuild","noPassWithoutEvidence","freshTaskExactAuthorityMeshRequiredBeforeMutation","layerMapRequiredForVisualMutation")
REQ_FIELDS=("id","name","group","owner","surface","classification","status","doNotRebuild","evidence","nextGate","proposalRule","protectedExistingOwners")

class GateError(RuntimeError): pass

def root()->Path:
    for p in (Path.cwd().resolve(),*Path.cwd().resolve().parents):
        if (p/".git").exists() and (p/"PRISMA Factory Ledger").exists(): return p
    for p in Path(__file__).resolve().parents:
        if (p/".git").exists() and (p/"PRISMA Factory Ledger").exists(): return p
    raise GateError("REPO_ROOT_NOT_FOUND")

def load(p:Path)->Any: return json.loads(p.read_text(encoding="utf-8"))
def head(r:Path)->str:
    x=subprocess.run(["git","-C",str(r),"rev-parse","HEAD"],capture_output=True,text=True,check=False)
    return x.stdout.strip() if x.returncode==0 else ""

def records(d:dict[str,Any])->list[dict[str,Any]]:
    f=d.get("rowFields")
    rows=d.get("rows")
    if not isinstance(f,list) or tuple(f)!=REQ_FIELDS or not isinstance(rows,list): return []
    out=[]
    for row in rows:
        if isinstance(row,list) and len(row)==len(f): out.append(dict(zip(f,row)))
    return out

def validate(r:Path,d:dict[str,Any])->list[str]:
    e=[]
    if d.get("schemaVersion")!=SCHEMA: e.append("SCHEMA_MISMATCH")
    p=d.get("gatePolicy") or {}
    for k in REQ_POLICY:
        if p.get(k) is not True: e.append("POLICY_REQUIRED_TRUE:"+k)
    if set(d.get("classificationEnum") or [])!=VALID: e.append("CLASSIFICATION_ENUM_MISMATCH")
    rules=d.get("globalRules") or {}
    for k in ("forbiddenActions","forbiddenClaims","externalForbidden","buildForbidden"):
        if not isinstance(rules.get(k),list) or not rules.get(k): e.append("GLOBAL_RULE_REQUIRED:"+k)
    if "REBUILD_DNR" not in (rules.get("forbiddenActions") or []): e.append("DNR_GLOBAL_BLOCK_MISSING")
    if "SOURCE_FIX_FROM_EXTERNAL_BLOCKER" not in (rules.get("externalForbidden") or []): e.append("EXTERNAL_GLOBAL_BLOCK_MISSING")
    if "SECOND_SOURCE_OF_TRUTH" not in (rules.get("buildForbidden") or []): e.append("SECOND_TRUTH_BLOCK_MISSING")
    rec=records(d)
    if not rec or len(rec)!=len(d.get("rows") or []): e.append("INVALID_ROW_SCHEMA")
    ids=[x.get("id") for x in rec]
    if len(ids)!=len(set(ids)): e.append("DUPLICATE_CAPABILITY_ID")
    for c in rec:
        cid=str(c.get("id") or "")
        cls=c.get("classification")
        if not cid: e.append("CAPABILITY_ID_REQUIRED"); continue
        if cls not in VALID: e.append(f"INVALID_CLASSIFICATION:{cid}:{cls}")
        if not c.get("status"): e.append("STATUS_REQUIRED:"+cid)
        if not isinstance(c.get("doNotRebuild"),bool): e.append("DNR_BOOL_REQUIRED:"+cid)
        if not c.get("nextGate"): e.append("NEXT_GATE_REQUIRED:"+cid)
        if not c.get("proposalRule"): e.append("PROPOSAL_RULE_REQUIRED:"+cid)
        if not isinstance(c.get("evidence"),list) or not c["evidence"]: e.append("EVIDENCE_REQUIRED:"+cid)
        if cls=="BUILD" and c.get("doNotRebuild"): e.append("CONTRADICTION_BUILD_DNR:"+cid)
        if cls=="BUILD" and not c.get("protectedExistingOwners"): e.append("BUILD_PROTECTED_OWNERS_REQUIRED:"+cid)
        if cls=="EXTERNAL" and not c.get("doNotRebuild"): e.append("EXTERNAL_MUST_NOT_TRIGGER_REBUILD:"+cid)
        for ev in c.get("evidence") or []:
            if not isinstance(ev,str): e.append("EVIDENCE_FORMAT:"+cid); continue
            if ev.startswith("path:"):
                rp=ev[5:]
                if not rp or not (r/rp).exists(): e.append(f"EVIDENCE_PATH_MISSING:{cid}:{rp}")
            elif not ev.startswith("pr:"):
                e.append(f"EVIDENCE_TYPE_UNKNOWN:{cid}:{ev}")
    a=((d.get("generatedFrom") or {}).get("authorityMesh") or {})
    if a.get("status")!="PASS_COMPOSED_AUTHORITY_MESH": e.append("MAP_MESH_NOT_PASS")
    if a.get("layerMapPresent") is not True: e.append("MAP_LAYER_MAP_MISSING")
    if a.get("requiredAuthorityCoveragePct")!=100: e.append("MAP_COVERAGE_NOT_100")
    if a.get("blockers")!=0: e.append("MAP_BLOCKERS")
    return e

def decide(r:Path,d:dict[str,Any],q:dict[str,Any])->dict[str,Any]:
    e=validate(r,d); mode=str(q.get("mode") or "").upper()
    if mode not in {"PROPOSAL","MUTATION"}: e.append("REQUEST_MODE_INVALID")
    ids=q.get("capabilityIds")
    if not isinstance(ids,list) or not ids or any(not isinstance(x,str) for x in ids):
        e.append("CAPABILITY_IDS_REQUIRED"); ids=[]
    by={x["id"]:x for x in records(d)}
    selected=[]
    for cid in ids:
        c=by.get(cid)
        if not c: e.append("UNKNOWN_CAPABILITY:"+cid); continue
        selected.append(c)
        if c["classification"]=="DONE" and c["doNotRebuild"] and "build" in str(q.get("task") or "").lower():
            e.append("ANTI_REWORK_BUILD_ON_DONE_DNR:"+cid)
    if mode=="MUTATION":
        m=q.get("authorityMesh")
        if not isinstance(m,dict): e.append("MUTATION_MESH_REQUIRED")
        else:
            if m.get("status")!="PASS_COMPOSED_AUTHORITY_MESH": e.append("MUTATION_MESH_NOT_PASS")
            if m.get("requiredAuthorityCoveragePct")!=100: e.append("MUTATION_MESH_COVERAGE")
            if m.get("blockers")!=0: e.append("MUTATION_MESH_BLOCKERS")
            h=head(r)
            if h and m.get("repoHead")!=h: e.append(f"MUTATION_MESH_STALE_HEAD:{m.get('repoHead')}:{h}")
            if q.get("visualMutation") is True and m.get("layerMapPresent") is not True: e.append("VISUAL_LAYER_MAP_REQUIRED")
    out=[{"id":c["id"],"classification":c["classification"],"status":c["status"],"doNotRebuild":c["doNotRebuild"],"nextGate":c["nextGate"],"proposalRule":c["proposalRule"]} for c in selected]
    return {"schemaVersion":"prisma.change_intelligence.capability_gate.result.v1","result":"PASS_CAPABILITY_GATE" if not e else "BLOCKED_ANTI_REWORK","mode":mode,"selected":out,"errors":e}

def selftest(r:Path,d:dict[str,Any])->None:
    assert not validate(r,d)
    b=copy.deepcopy(d); b["rows"].append(copy.deepcopy(b["rows"][0])); assert "DUPLICATE_CAPABILITY_ID" in validate(r,b)
    b=copy.deepcopy(d); ix=b["rowFields"].index("classification"); b["rows"][0][ix]="BUILD"; assert any("CONTRADICTION_BUILD_DNR" in x for x in validate(r,b))
    done=next(x["id"] for x in records(d) if x["classification"]=="DONE" and x["doNotRebuild"])
    assert decide(r,d,{"mode":"PROPOSAL","capabilityIds":[done],"task":"build it again"})["result"]=="BLOCKED_ANTI_REWORK"
    assert decide(r,d,{"mode":"PROPOSAL","capabilityIds":["missing.cap"],"task":"x"})["result"]=="BLOCKED_ANTI_REWORK"
    build=next(x["id"] for x in records(d) if x["classification"]=="BUILD")
    assert decide(r,d,{"mode":"MUTATION","capabilityIds":[build],"task":"adapter"})["result"]=="BLOCKED_ANTI_REWORK"
    print("PASS_CHANGE_INTELLIGENCE_CAPABILITY_GATE_SELF_TEST")

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--map",default=str(MAP_REL)); ap.add_argument("--validate-map",action="store_true"); ap.add_argument("--request"); ap.add_argument("--self-test",action="store_true"); ns=ap.parse_args()
    r=root(); mp=Path(ns.map); mp=mp if mp.is_absolute() else r/mp; d=load(mp)
    if ns.self_test: selftest(r,d); return 0
    if ns.request:
        rp=Path(ns.request); rp=rp if rp.is_absolute() else r/rp; out=decide(r,d,load(rp)); print(json.dumps(out,indent=2,ensure_ascii=False)); return 0 if out["result"]=="PASS_CAPABILITY_GATE" else 2
    e=validate(r,d); out={"schemaVersion":"prisma.change_intelligence.capability_gate.map_validation.v1","result":"PASS_CHANGE_INTELLIGENCE_CAPABILITY_MAP" if not e else "FAIL_CHANGE_INTELLIGENCE_CAPABILITY_MAP","capabilityCount":len(records(d)),"errors":e}; print(json.dumps(out,indent=2,ensure_ascii=False)); return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
