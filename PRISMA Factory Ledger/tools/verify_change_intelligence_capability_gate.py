#!/usr/bin/env python3
"""Fail-closed PRISMA Change Assurance V1 gate. Filename is a compat alias."""
from __future__ import annotations
import argparse,copy,json,subprocess
from pathlib import Path
SCHEMA="prisma.change_assurance.capability_map.v2"; LEGACY="PRISMA Change Intelligence"
MAP=Path("PRISMA Factory Ledger/PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP.json"); CONTRACT=Path("tools/code-atlas/CODE_ATLAS_CHANGE_ASSURANCE_CONTRACT.json")
IDENT={"productName":"PRISMA Change Assurance","engineName":"Code Atlas","principle":"No evidence. No green.","tagline":"Know what can change. Control what does. Prove the result."}
STAGES=("UNDERSTAND","RESOLVE","AUTHORIZE","OBSERVE","VERIFY","PROVE"); IDS="ABCDEFGHIJ"
CLASS={"DONE","VERIFY","FIX","BUILD","EXTERNAL"}; V1={"DONE","PARTIAL","MISSING","BLOCKED","NOT_REQUIRED_V1","EXPERIMENTAL"}
REN=("PUBLIC_IDENTITY_RENAME","CANONICAL_DOC_RENAME","MACHINE_CONTRACT_RENAME","INTERNAL_SYMBOL_MIGRATE","COMPAT_ALIAS_KEEP","HISTORICAL_EVIDENCE_KEEP","FALSE_POSITIVE")
OWNERSHIP_SCHEMA="prisma.change_assurance.ownership_boundary.v1"
OWNERSHIP=("ASSURANCE_CORE","ASSURANCE_PRODUCT","PRISMA_PLATFORM","PRISMA_PRODUCT","ASSURANCE_PRISMA_ADAPTER","SHARED_INFRASTRUCTURE","LEGACY_COMPAT")
OWNERSHIP_RULES={"physicalNameDeterminesOwnership":False,"massRenameRequired":False,"secondRegistryAllowed":False,"assuranceMayConsumePrismaTruthWithoutOwningProducer":True,"prismaMayBeInternalAssuranceCustomer":True,"legacyPhysicalIdentifiersMayRemainWhenCompatibilitySensitive":True,"newPublicLegacyProductIdentityAllowed":False,"newImplementationMustResolveOwnershipExplicitly":True}
INV=("Candidate != Authority","Impact Radius != Authorization","Retrieval != proof","UNKNOWN != PASS_WITH_WARNING","Snapshot/provenance lock is required for proof-bearing claims","Verification must be agent-neutral; same-agent assertion is not independent verification")
ROW=("id","name","group","owner","surface","classification","status","doNotRebuild","evidence","nextGate","proposalRule","protectedExistingOwners")
BASE=(('A','UNDERSTAND','Universal bounded repository understanding','PARTIAL','code_atlas.intelligence',1),('B','RESOLVE','Useful Impact Radius','PARTIAL','code_atlas.intelligence',1),('C','UNDERSTAND','Edge provenance','PARTIAL','code_atlas.intelligence',1),('D','RESOLVE','Better UNKNOWN','PARTIAL','code_atlas.change_intelligence',1),('E','AUTHORIZE','Conflict-first authority','PARTIAL','code_atlas.change_intelligence',1),('F','OBSERVE','Change comparison','MISSING','UNRESOLVED_V1_OWNER',0),('G','VERIFY','Agent-neutral independent verification','PARTIAL','code_atlas.change_intelligence / external evaluator',1),('H','PROVE','Portable reproducible runner','PARTIAL','code_atlas.change_intelligence',1),('I','PROVE','Evidence Bundle','PARTIAL','code_atlas.change_intelligence',1),('J','PROVE','Utility evidence','BLOCKED','external human reviewer / independent evaluator',1))
POL=("mandatoryBeforeTechnicalProposal","mandatoryBeforeRepositoryMutation","factoryLedgerFirst","capabilityIdsRequired","failClosedOnUnknownCapability","failClosedOnContradiction","failClosedOnStaleAuthorityForMutation","noRebuildWhenDoNotRebuild","noPassWithoutEvidence","freshTaskExactAuthorityMeshRequiredBeforeMutation","layerMapRequiredForVisualMutation","productIdentityLocked","sixStagesRequired","v1ChecklistRequired","noFakeGreenEnforced","legacyNamePolicyEnforced","definitionOfDoneEvidenceRequiredForDone")
PROV={"repoHead":"45762d1a6251195dae0e229dfe6fa1aed74645fa","repoTree":"ce37544fb6f431586bc5f472124c0d6a3bc1c2a8","authorityMesh":{"runId":32332472480,"artifactId":9393519072,"requestDigest":"81bf9492592090b52cc2a07b0138aa09454a423b7eca07abac9f65b1ab2798e7","downloadedArtifactSha256":"c8e67ab317a2ad47b296434cfe1818fd5d3634ce0eead115fa70b5c2b9ed6ae0","composedArtifactSha256":"e7925bdc882ad7734e8e2f11788a5bb9443a2eaa7ea73d8ef19fd1ee2952dc8e","status":"PASS_COMPOSED_AUTHORITY_MESH","layerMapPresent":True,"lanes":2,"blockers":0,"requiredAuthorityCoveragePct":100,"productionCertified":False}}
COMPAT={MAP.as_posix(),"PRISMA Factory Ledger/PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP.md","PRISMA Factory Ledger/tools/verify_change_intelligence_capability_gate.py",".github/workflows/change-intelligence-capability-gate.yml",CONTRACT.as_posix(),"tools/code-atlas/docs/PRISMA_CHANGE_ASSURANCE_V1.md","PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md"}

def root():
 for p in (Path.cwd().resolve(),*Path.cwd().resolve().parents,*Path(__file__).resolve().parents):
  if (p/".git").exists() and (p/"PRISMA Factory Ledger").exists(): return p
 raise RuntimeError("REPO_ROOT_NOT_FOUND")
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def git(r,*a):
 x=subprocess.run(["git","-C",str(r),*a],capture_output=True,text=True,check=False)
 if x.returncode: raise RuntimeError("GIT_FAILED:"+" ".join(a))
 return x.stdout.strip()
def rec(d):
 f=d.get("rowFields"); rows=d.get("rows")
 if tuple(f or [])!=ROW or not isinstance(rows,list): return []
 return [dict(zip(f,x)) for x in rows if isinstance(x,list) and len(x)==len(f)]
def dod():
 out=[]
 for i,s,t,st,o,dnr in BASE:
  ev=[] if i=="F" else ["path:tools/code-atlas/docs/CODE_ATLAS_CUSTOMER_WOW_V1.contract.json"]
  out.append({"id":i,"stage":s,"title":t,"status":st,"requiredForV1":True,"claimBoundary":"Evidence-bounded; UNKNOWN/BLOCKED is valid and no stronger claim is permitted without proof.","evidence":ev,"tests":[] if i in "FJ" else ["bounded positive evidence"],"negativeTests":["missing/contradictory/unsupported evidence must not become green"],"knownBlindSpots":["bounded evidence does not prove universal completeness"],"nextEvidence":"advance only through the next evidence gate recorded for this item","owner":o,"doNotRebuild":bool(dnr)})
 return out
def migrate(mp):
 d=load(mp)
 if d.get("schemaVersion")==SCHEMA:return {"result":"NOOP_ALREADY_CHANGE_ASSURANCE_V2"}
 if d.get("schemaVersion")!="prisma.change_intelligence.capability_map.v1": raise RuntimeError("MIGRATION_SOURCE_SCHEMA_UNEXPECTED")
 old=copy.deepcopy(d.get("rows")); fields=copy.deepcopy(d.get("rowFields")); rs=rec(d)
 if not rs: raise RuntimeError("MIGRATION_SOURCE_ROWS_INVALID")
 ids=[x["id"] for x in rs]
 d.update({"schemaVersion":SCHEMA,"mapId":"PRISMA_CHANGE_ASSURANCE_CAPABILITY_MAP","purpose":"Canonical fail-closed anti-rework and V1 Definition-of-Done authority for PRISMA Change Assurance.","productIdentity":{**IDENT,"stages":list(STAGES),"renamingLocked":True,"legacyProductName":LEGACY,"legacyNameStatus":"DEPRECATED_COMPAT_OR_HISTORICAL_ONLY"},"generatedFrom":copy.deepcopy(PROV),"classificationEnum":["DONE","VERIFY","FIX","BUILD","EXTERNAL"],"v1ChecklistStatusEnum":["DONE","PARTIAL","MISSING","BLOCKED","NOT_REQUIRED_V1","EXPERIMENTAL"],"v1DefinitionOfDone":dod(),"v1Complete":False,"invariants":list(INV),"renameClassificationEnum":list(REN),"claimBoundary":{"allowedGlobalStates":["PASS","BLOCKED","UNKNOWN","NOT_EVALUATED"],"unknownIsValidResult":True,"passWithWarningForbidden":True,"retrievalIsProof":False,"candidateIsAuthority":False,"impactRadiusIsAuthorization":False,"productionCertified":False,"enterpriseReady":False,"paidPilotReadyFromThisRegistryAlone":False},"legacyNamePolicy":{"legacyProductName":LEGACY,"permanentProductName":IDENT["productName"],"newPublicUseForbidden":True,"allowedCurrentClassifications":["COMPAT_ALIAS_KEEP","HISTORICAL_EVIDENCE_KEEP"],"compatibilityAliases":[{"path":p,"classification":"COMPAT_ALIAS_KEEP"} for p in sorted(COMPAT) if "CHANGE_INTELLIGENCE" in p],"historicalEvidenceRule":"Existing PRs/issues/evidence remain historical and are not rewritten.","internalSymbolRule":"No breaking rename for aesthetics."},"compatibility":{"legacySchema":"prisma.change_intelligence.capability_map.v1","legacyMapId":"PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP","legacyResultAliasesRetained":True,"protectedLegacyCapabilityIds":ids,"protectedLegacyCapabilityRowCountAtMigration":len(ids),"createsSecondRegistry":False,"singleRegistryPath":MAP.as_posix()}})
 d.setdefault("gatePolicy",{}).update({k:True for k in POL[-6:]})
 g=d.setdefault("globalRules",{}); g.setdefault("forbiddenActions",[]); g.setdefault("forbiddenClaims",[])
 for x in ["PUBLIC_REINTRODUCTION_OF_LEGACY_PRODUCT_NAME"]:
  if x not in g["forbiddenActions"]:g["forbiddenActions"].append(x)
 for x in ["UNIVERSAL_FROM_BOUNDED_EVIDENCE","UNKNOWN_AS_PASS_WITH_WARNING","RETRIEVAL_AS_PROOF","IMPACT_RADIUS_AS_AUTHORIZATION","CANDIDATE_AS_AUTHORITY"]:
  if x not in g["forbiddenClaims"]:g["forbiddenClaims"].append(x)
 if d.get("rows")!=old or d.get("rowFields")!=fields: raise RuntimeError("MIGRATION_CHANGED_LEGACY_ROWS")
 mp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 return {"result":"PASS_CHANGE_ASSURANCE_MAP_MIGRATION","preservedLegacyRows":len(old),"v1DefinitionOfDoneCount":10,"v1Complete":False}
def validate(d,c):
 e=[]
 if d.get("schemaVersion")!=SCHEMA:e.append("SCHEMA_MISMATCH")
 pi=d.get("productIdentity") or {}
 for k,v in IDENT.items():
  if pi.get(k)!=v:e.append("PRODUCT_IDENTITY_MISMATCH:"+k)
 if tuple(pi.get("stages") or [])!=STAGES:e.append("STAGES_MISMATCH")
 if pi.get("renamingLocked") is not True:e.append("RENAMING_LOCK_REQUIRED")
 if set(d.get("classificationEnum") or [])!=CLASS:e.append("CLASSIFICATION_ENUM_MISMATCH")
 if set(d.get("v1ChecklistStatusEnum") or [])!=V1:e.append("V1_STATUS_ENUM_MISMATCH")
 if tuple(d.get("renameClassificationEnum") or [])!=REN:e.append("RENAME_ENUM_MISMATCH")
 ob=d.get("ownershipBoundary") or {}
 if ob.get("schemaVersion")!=OWNERSHIP_SCHEMA:e.append("OWNERSHIP_SCHEMA_MISMATCH")
 if tuple(ob.get("classificationEnum") or [])!=OWNERSHIP:e.append("OWNERSHIP_ENUM_MISMATCH")
 orules=ob.get("rules") or {}
 for k,v in OWNERSHIP_RULES.items():
  if orules.get(k)!=v:e.append("OWNERSHIP_RULE_MISMATCH:"+k)
 classes=ob.get("classes") or {}
 if set(classes)!=set(OWNERSHIP):e.append("OWNERSHIP_CLASSES_MISMATCH")
 for k in OWNERSHIP:
  row=classes.get(k)
  if not isinstance(row,dict) or not row.get("definition"):e.append("OWNERSHIP_CLASS_DEFINITION_REQUIRED:"+k)
 for k in POL:
  if (d.get("gatePolicy") or {}).get(k) is not True:e.append("POLICY_REQUIRED_TRUE:"+k)
 if tuple(d.get("invariants") or [])!=INV:e.append("INVARIANTS_MISMATCH")
 cb=d.get("claimBoundary") or {}
 for k,v in {"unknownIsValidResult":True,"passWithWarningForbidden":True,"retrievalIsProof":False,"candidateIsAuthority":False,"impactRadiusIsAuthorization":False}.items():
  if cb.get(k)!=v:e.append("CLAIM_BOUNDARY_MISMATCH:"+k)
 rs=rec(d); ids=[x.get("id") for x in rs]
 if len(rs)!=len(d.get("rows") or []):e.append("INVALID_ROW_SCHEMA")
 if len(ids)!=len(set(ids)):e.append("DUPLICATE_CAPABILITY_ID")
 cp=d.get("compatibility") or {}
 if cp.get("createsSecondRegistry") is not False or cp.get("singleRegistryPath")!=MAP.as_posix():e.append("SECOND_REGISTRY_FORBIDDEN")
 if cp.get("protectedLegacyCapabilityIds")!=ids:e.append("LEGACY_CAPABILITY_IDS_DRIFT")
 for x in rs:
  i=str(x.get("id") or ""); cl=x.get("classification")
  if cl not in CLASS:e.append("INVALID_CLASSIFICATION:"+i)
  if not isinstance(x.get("doNotRebuild"),bool):e.append("DNR_BOOL_REQUIRED:"+i)
  if not x.get("status") or not x.get("nextGate") or not x.get("proposalRule") or not x.get("evidence"):e.append("ROW_REQUIRED_FIELD:"+i)
  if cl=="BUILD" and x.get("doNotRebuild"):e.append("CONTRADICTION_BUILD_DNR:"+i)
  if cl=="BUILD" and not x.get("protectedExistingOwners"):e.append("BUILD_PROTECTED_OWNERS_REQUIRED:"+i)
 dr=d.get("v1DefinitionOfDone") or []; did=[x.get("id") for x in dr if isinstance(x,dict)]
 if did!=list(IDS):e.append("V1_DOD_IDS_ORDER_MISMATCH")
 if len(did)!=len(set(did)):e.append("V1_DOD_DUPLICATE_ID")
 exp={x[0]:x for x in BASE}
 for x in dr:
  i=x.get("id"); z=exp.get(i)
  if not z or (x.get("stage"),x.get("title"))!=(z[1],z[2]):e.append("V1_DOD_CANON_MISMATCH:"+str(i))
  if x.get("status") not in V1:e.append("V1_DOD_STATUS_INVALID:"+str(i))
  if x.get("status")=="DONE":
   for k in ("evidence","tests","negativeTests"):
    if not x.get(k):e.append("V1_DONE_WITHOUT_"+k.upper()+":"+str(i))
 should=bool(dr) and all(x.get("status")=="DONE" for x in dr if x.get("requiredForV1"))
 if d.get("v1Complete") is not should:e.append("V1_COMPLETE_DERIVATION_MISMATCH")
 a=(d.get("generatedFrom") or {}).get("authorityMesh") or {}
 if a.get("status")!="PASS_COMPOSED_AUTHORITY_MESH" or a.get("requiredAuthorityCoveragePct")!=100 or a.get("blockers")!=0:e.append("MAP_MESH_INVALID")
 if not c:e.append("PRODUCT_CONTRACT_MISSING")
 else:
  if c.get("productIdentity")!={**IDENT,"renamingLocked":True,"legacyProductName":LEGACY,"legacyProductNamePolicy":"COMPAT_OR_HISTORICAL_ONLY"}:e.append("CONTRACT_IDENTITY_MISMATCH")
  if tuple(c.get("stages") or [])!=STAGES:e.append("CONTRACT_STAGES_MISMATCH")
  if [x.get("id") for x in c.get("definitionOfDone",[]) if isinstance(x,dict)]!=list(IDS):e.append("CONTRACT_DOD_MISMATCH")
  rg=c.get("registry") or {}
  if rg.get("singleAuthorityPath")!=MAP.as_posix() or rg.get("createsSecondRegistry") is not False:e.append("CONTRACT_SECOND_REGISTRY_FORBIDDEN")
  obref=c.get("ownershipBoundary") or {}
  if obref.get("authorityPath")!=MAP.as_posix() or obref.get("authorityKey")!="ownershipBoundary":e.append("CONTRACT_OWNERSHIP_AUTHORITY_MISMATCH")
  if obref.get("createsSecondRegistry") is not False:e.append("CONTRACT_OWNERSHIP_SECOND_REGISTRY_FORBIDDEN")
  if obref.get("physicalRenameRequired") is not False:e.append("CONTRACT_OWNERSHIP_PHYSICAL_RENAME_FORBIDDEN")
 return sorted(set(e))
def decide(r,d,q):
 e=validate(d,load(r/CONTRACT) if (r/CONTRACT).exists() else None); mode=str(q.get("mode") or "").upper(); ids=q.get("capabilityIds") if isinstance(q.get("capabilityIds"),list) else []
 if mode not in {"PROPOSAL","MUTATION"}:e.append("REQUEST_MODE_INVALID")
 if not ids:e.append("CAPABILITY_IDS_REQUIRED")
 by={x["id"]:x for x in rec(d)}
 for i in ids:
  x=by.get(i)
  if not x:e.append("UNKNOWN_CAPABILITY:"+str(i))
  elif x.get("classification")=="DONE" and x.get("doNotRebuild") and "build" in str(q.get("task") or "").lower():e.append("ANTI_REWORK_BUILD_ON_DONE_DNR:"+i)
 if mode=="MUTATION":
  m=q.get("authorityMesh") or {}; h=git(r,"rev-parse","HEAD")
  if m.get("status")!="PASS_COMPOSED_AUTHORITY_MESH" or m.get("repoHead")!=h or m.get("requiredAuthorityCoveragePct")!=100 or m.get("blockers")!=0 or not m.get("requestDigest") or not m.get("artifactDigest"):e.append("MUTATION_MESH_INVALID_OR_STALE")
  if q.get("visualMutation") is True and m.get("layerMapPresent") is not True:e.append("VISUAL_LAYER_MAP_REQUIRED")
 return {"schemaVersion":"prisma.change_assurance.capability_gate.result.v2","result":"PASS_CHANGE_ASSURANCE_CAPABILITY_GATE" if not e else "BLOCKED_ANTI_REWORK","errors":sorted(set(e))}
def legacy(r,base):
 if not base:return ["BASE_REF_REQUIRED"]
 out=[]; path=""
 for ln in git(r,"diff","--unified=0",base+"...HEAD").splitlines():
  if ln.startswith("+++ b/"):path=ln[6:].strip()
  elif ln.startswith("+") and not ln.startswith("+++") and LEGACY in ln:
   t=ln[1:].strip().lower()
   if path in {MAP.as_posix(),"PRISMA Factory Ledger/tools/verify_change_intelligence_capability_gate.py"}:continue
   if path in COMPAT and any(w in t for w in ("legacy","deprecated","compat","historical")):continue
   if any(w in path.lower() for w in ("evidence","snapshot","archive")):continue
   out.append("LEGACY_PUBLIC_REINTRODUCTION:"+path)
 return out
def selftest(r,d,c):
 assert not validate(d,c)
 b=copy.deepcopy(d);b["productIdentity"]["productName"]="x";assert "PRODUCT_IDENTITY_MISMATCH:productName" in validate(b,c)
 b=copy.deepcopy(d);b["v1DefinitionOfDone"].pop();assert "V1_DOD_IDS_ORDER_MISMATCH" in validate(b,c)
 b=copy.deepcopy(d);b["v1DefinitionOfDone"][0].update(status="DONE",evidence=[]);assert "V1_DONE_WITHOUT_EVIDENCE:A" in validate(b,c)
 cc=copy.deepcopy(c);cc["registry"]["createsSecondRegistry"]=True;assert "CONTRACT_SECOND_REGISTRY_FORBIDDEN" in validate(d,cc)
 b=copy.deepcopy(d);b["ownershipBoundary"]["rules"]["massRenameRequired"]=True;assert "OWNERSHIP_RULE_MISMATCH:massRenameRequired" in validate(b,c)
 cc=copy.deepcopy(c);cc["ownershipBoundary"]["createsSecondRegistry"]=True;assert "CONTRACT_OWNERSHIP_SECOND_REGISTRY_FORBIDDEN" in validate(d,cc)
 b=copy.deepcopy(d);b["rows"].append(copy.deepcopy(b["rows"][0]));assert "DUPLICATE_CAPABILITY_ID" in validate(b,c)
 done=next(x["id"] for x in rec(d) if x["classification"]=="DONE" and x["doNotRebuild"]);assert decide(r,d,{"mode":"PROPOSAL","capabilityIds":[done],"task":"build again"})["result"]=="BLOCKED_ANTI_REWORK"
 assert decide(r,d,{"mode":"PROPOSAL","capabilityIds":["missing"],"task":"verify"})["result"]=="BLOCKED_ANTI_REWORK"
 print("PASS_CHANGE_ASSURANCE_CAPABILITY_GATE_SELF_TEST\nCOMPAT_ALIAS:PASS_CHANGE_INTELLIGENCE_CAPABILITY_GATE_SELF_TEST")
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--map",default=str(MAP));ap.add_argument("--validate-map",action="store_true");ap.add_argument("--request");ap.add_argument("--self-test",action="store_true");ap.add_argument("--check-legacy-diff",action="store_true");ap.add_argument("--migrate-map-v2",action="store_true");ap.add_argument("--base-ref");n=ap.parse_args();r=root();mp=Path(n.map);mp=mp if mp.is_absolute() else r/mp
 if n.migrate_map_v2:
  try:o=migrate(mp);print(json.dumps(o,indent=2));return 0
  except Exception as x:print(json.dumps({"result":"BLOCKED_ANTI_REWORK","errors":[str(x)]},indent=2));return 4
 d=load(mp);c=load(r/CONTRACT) if (r/CONTRACT).exists() else None
 if n.self_test:selftest(r,d,c);return 0
 if n.check_legacy_diff:
  e=legacy(r,n.base_ref or "");print(json.dumps({"result":"PASS_CHANGE_ASSURANCE_LEGACY_NAME_DIFF" if not e else "BLOCKED_LEGACY_NAME_REINTRODUCTION","errors":e},indent=2));return 0 if not e else 3
 if n.request:
  p=Path(n.request);p=p if p.is_absolute() else r/p;o=decide(r,d,load(p));print(json.dumps(o,indent=2));return 0 if o["result"].startswith("PASS") else 2
 e=validate(d,c);o={"schemaVersion":"prisma.change_assurance.capability_gate.map_validation.v2","productName":IDENT["productName"],"result":"PASS_CHANGE_ASSURANCE_CAPABILITY_MAP" if not e else "FAIL_CHANGE_ASSURANCE_CAPABILITY_MAP","legacyPassAlias":"PASS_CHANGE_INTELLIGENCE_CAPABILITY_MAP" if not e else None,"capabilityCount":len(rec(d)),"v1DefinitionOfDoneCount":len(d.get("v1DefinitionOfDone") or []),"v1Complete":d.get("v1Complete"),"errors":e};print(json.dumps(o,indent=2));return 0 if not e else 1
if __name__=="__main__":raise SystemExit(main())
