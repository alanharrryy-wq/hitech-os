from __future__ import annotations
import hashlib, importlib.util, json, zipfile, io
from pathlib import Path
from typing import Any
from .errors import AuthorizationError, PlanBindingError
from .hashing import sha256_file
from .security import contained_path

CAPABILITY_ID="visual.generic_application_engine_v1"

def _json_bytes(raw:bytes, label:str)->dict[str,Any]:
    try:
        value=json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise AuthorizationError(f"{label} invalid JSON") from exc
    if not isinstance(value,dict):
        raise AuthorizationError(f"{label} must be an object")
    return value

def _canonical_digest(value:Any)->str:
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def verify_mesh_artifact(auth:dict[str,Any],repo_root:Path,authority_commit:str)->dict[str,Any]:
    artifact=contained_path(repo_root,auth["authorityMeshArtifact"],must_exist=True,field="authorityMeshArtifact")
    if artifact.is_symlink() or not artifact.is_file():
        raise AuthorizationError("Authority Mesh artifact must be a regular file")
    actual=sha256_file(artifact)
    if actual!=auth["authorityMeshArtifactSha256"]:
        raise AuthorizationError("Authority Mesh artifact SHA-256 mismatch")
    try:
        outer=zipfile.ZipFile(artifact)
    except zipfile.BadZipFile as exc:
        raise AuthorizationError("Authority Mesh artifact is not a ZIP") from exc
    with outer:
        names=set(outer.namelist())
        if "prisma-automesh-composed-result.zip" in names:
            composed_bytes=outer.read("prisma-automesh-composed-result.zip")
        else:
            composed_bytes=artifact.read_bytes()
    try:
        composed=zipfile.ZipFile(io.BytesIO(composed_bytes))
    except zipfile.BadZipFile as exc:
        raise AuthorizationError("composed Authority Mesh ZIP invalid") from exc
    with composed:
        names=set(composed.namelist())
        required={"PRISMA_MESH_GATEWAY_REPORT.json","authority/PREFLIGHT_MANIFEST.json","legacy_surface_mesh.zip"}
        missing=required-names
        if missing: raise AuthorizationError("Authority Mesh missing evidence: "+",".join(sorted(missing)))
        report=_json_bytes(composed.read("PRISMA_MESH_GATEWAY_REPORT.json"),"PRISMA_MESH_GATEWAY_REPORT")
        preflight=_json_bytes(composed.read("authority/PREFLIGHT_MANIFEST.json"),"PREFLIGHT_MANIFEST")
        legacy_bytes=composed.read("legacy_surface_mesh.zip")
    if report.get("status")!="PASS_COMPOSED_AUTHORITY_MESH":
        raise AuthorizationError("Authority Mesh status is not PASS_COMPOSED_AUTHORITY_MESH")
    if report.get("repoHead")!=authority_commit:
        raise AuthorizationError("Authority Mesh repoHead does not match authorityCommit")
    if report.get("requestDigest")!=auth["authorityMeshRequestDigest"]:
        raise AuthorizationError("Authority Mesh requestDigest mismatch")
    if preflight.get("status")!="PASS_PREFLIGHT" or preflight.get("blockers"):
        raise AuthorizationError("Authority Mesh preflight is blocked")
    if preflight.get("repoHead")!=authority_commit:
        raise AuthorizationError("Authority Mesh preflight head mismatch")
    lanes=preflight.get("lanes")
    if not isinstance(lanes,list) or not lanes:
        raise AuthorizationError("Authority Mesh has no authority lanes")
    for lane in lanes:
        coverage=(lane.get("coverage") or {}).get("resolvedPercent")
        if float(coverage or 0)!=100.0 or lane.get("missing"):
            raise AuthorizationError(f"Authority Mesh lane not at 100%: {lane.get('id')}")
    try:
        legacy=zipfile.ZipFile(io.BytesIO(legacy_bytes))
    except zipfile.BadZipFile as exc:
        raise AuthorizationError("legacy surface mesh ZIP invalid") from exc
    task_id=auth["authorityTaskId"]
    layer_json=f"tasks/{task_id}/authority_mesh/reports/LAYERS_MAP.json"
    with legacy:
        lnames=set(legacy.namelist())
        if "PARALLEL_CERTIFICATION.json" not in lnames:
            raise AuthorizationError("PARALLEL_CERTIFICATION missing")
        cert=_json_bytes(legacy.read("PARALLEL_CERTIFICATION.json"),"PARALLEL_CERTIFICATION")
        if layer_json not in lnames:
            raise AuthorizationError("mandatory task Layer Map missing")
        layer_map=_json_bytes(legacy.read(layer_json),"LAYERS_MAP")
    if cert.get("status")!="PASS" or cert.get("read_only_repo") is not True or cert.get("provenance_verified") is not True:
        raise AuthorizationError("parallel Authority Mesh certification is not PASS/read-only/provenance-verified")
    drift=cert.get("repo_drift") or {}
    if drift.get("stable") is not True or drift.get("changed_count") not in (0,None):
        raise AuthorizationError("Authority Mesh repository drifted during capture")
    child=next((x for x in cert.get("children",[]) if x.get("task_id")==task_id),None)
    if not child or child.get("returncode")!=0 or child.get("manifest_status")!="PASS" or (child.get("provenance") or {}).get("verified") is not True:
        raise AuthorizationError("task-exact Authority Mesh lane is not certified")
    if not layer_map:
        raise AuthorizationError("Layer Map is empty")
    return {
        "status":"PASS_COMPOSED_AUTHORITY_MESH","repoHead":authority_commit,
        "requiredAuthorityCoveragePct":100,"blockers":0,
        "requestDigest":report["requestDigest"],"artifactDigest":actual,
        "layerMapPresent":True,"authorityTaskId":task_id
    }

def verify_ui_bridge_plan(auth:dict[str,Any],repo_root:Path,target:dict[str,Any],request:dict[str,Any])->dict[str,Any]:
    plan_path=contained_path(repo_root,auth["uiBridgePlanPath"],must_exist=True,field="uiBridgePlanPath")
    diff_path=contained_path(repo_root,auth["uiBridgeSemanticDiffPath"],must_exist=True,field="uiBridgeSemanticDiffPath")
    if plan_path.is_symlink() or diff_path.is_symlink():
        raise PlanBindingError("UI Bridge evidence cannot be symlinked")
    if sha256_file(plan_path)!=auth["uiBridgePlanSha256"] or sha256_file(diff_path)!=auth["uiBridgeSemanticDiffSha256"]:
        raise PlanBindingError("UI Bridge evidence SHA-256 mismatch")
    try:
        plan=json.loads(plan_path.read_text(encoding="utf-8"))
        diff=json.loads(diff_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise PlanBindingError("UI Bridge plan/diff JSON invalid") from exc
    if plan.get("schema")!="prisma.ui.bridge.plan.v1" or plan.get("mode")!="READ_ONLY_SOURCE_PLAN":
        raise PlanBindingError("UI Bridge plan schema/mode invalid")
    if plan.get("status")!="PLAN_READY_FOR_REVIEW" or plan.get("applicationEnabled") is not False or plan.get("blockingReasons"):
        raise PlanBindingError("UI Bridge plan is not a clean reviewed read-only plan")
    if diff.get("schema")!="prisma.ui.bridge.semantic-diff.v1" or diff.get("planId")!=plan.get("planId"):
        raise PlanBindingError("UI Bridge semantic diff does not bind to planId")
    if diff.get("status")!="DIFF_READY" or diff.get("sourceMutationPerformed") is not False:
        raise PlanBindingError("UI Bridge semantic diff is not read-only DIFF_READY")
    if diff.get("operations")!=plan.get("operations"):
        raise PlanBindingError("UI Bridge plan and semantic diff operations differ")
    if diff.get("checksum")!=_canonical_digest(diff.get("operations")):
        raise PlanBindingError("UI Bridge semantic diff checksum invalid")
    checks={"bindingId":"bindingId","layerId":"layerId","adapterId":"adapterId","recipeId":"recipeId"}
    for pfield,tfield in checks.items():
        if plan.get(pfield)!=target.get(tfield):
            raise PlanBindingError(f"UI Bridge {pfield} does not match exact target")
    plan_ops=plan.get("operations")
    if not isinstance(plan_ops,list) or not plan_ops:
        raise PlanBindingError("UI Bridge plan has no operations")
    if any(op.get("type")=="jsonValues" for op in request["operations"]):
        raise PlanBindingError("JSON APPLY requires an explicit governed UI Bridge JSON-root plan contract")
    for op in request["operations"]:
        selector=op["path"]
        candidates=[p for p in plan_ops if p.get("selector")==selector and p.get("targetResolutionStatus")=="SOURCE_RESOLVED"]
        if len(candidates)!=1:
            raise PlanBindingError(f"UI Bridge plan does not resolve exact selector once: {selector}")
        allowed={str(x.get("property")) for x in candidates[0].get("propertyChanges",[]) if isinstance(x,dict)}
        requested=set(op["values"])
        if not requested<=allowed:
            raise PlanBindingError(f"requested CSS properties exceed reviewed UI Bridge plan: {sorted(requested-allowed)}")
    return {"planId":plan.get("planId"),"semanticDiffChecksum":diff.get("checksum")}

def _load_factory_gate(repo_root:Path):
    path=contained_path(repo_root,"PRISMA Factory Ledger/tools/verify_prisma_anti_rework_gate.py",must_exist=True,field="Factory Ledger gate")
    spec=importlib.util.spec_from_file_location("prisma_factory_anti_rework_gate",path)
    if spec is None or spec.loader is None:
        raise AuthorizationError("cannot load Factory Ledger anti-rework gate")
    module=importlib.util.module_from_spec(spec)
    try: spec.loader.exec_module(module)
    except Exception as exc: raise AuthorizationError(f"cannot execute Factory Ledger anti-rework gate: {exc}") from exc
    return module

def verify_factory_ledger_gate(auth:dict[str,Any],repo_root:Path,authority_commit:str,mesh:dict[str,Any])->dict[str,Any]:
    module=_load_factory_gate(repo_root)
    try:
        authority=module.read_authority(repo_root)
        gate_request={
            "schemaVersion":module.SCHEMA,"mode":"MUTATION","expectedHead":authority_commit,
            "task":auth["task"],"capabilities":[{"id":CAPABILITY_ID,"requestedAction":"REUSE"}],
            "authorityMesh":{k:mesh[k] for k in ("status","repoHead","requiredAuthorityCoveragePct","blockers","requestDigest","artifactDigest","layerMapPresent")},
            "visualMutation":True
        }
        result=module.decide(repo_root,authority,gate_request)
    except Exception as exc:
        raise AuthorizationError(f"Factory Ledger gate execution failed: {exc}") from exc
    if result.get("result")!="PASS_ANTI_REWORK_GATE":
        raise AuthorizationError("Factory Ledger MUTATION gate blocked",details={"errors":result.get("errors",[])})
    return result

def verify_application_authority(request:dict[str,Any],repo_root:Path,target:dict[str,Any])->dict[str,Any]:
    authority_commit=request.get("authorityCommit")
    auth=request.get("authorization") or {}
    mesh=verify_mesh_artifact(auth,repo_root,authority_commit)
    gate=verify_factory_ledger_gate(auth,repo_root,authority_commit,mesh)
    plan=verify_ui_bridge_plan(auth,repo_root,target,request)
    return {"mesh":mesh,"factoryLedgerDecisionDigest":gate.get("decisionDigest"),"uiBridge":plan}
