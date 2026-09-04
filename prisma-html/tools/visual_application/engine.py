from __future__ import annotations
import json, uuid
from pathlib import Path
from typing import Any, Callable
from .contracts import load_request
from .css_writer import patch_css
from .json_writer import patch_json_bytes
from .hashing import sha256_bytes, sha256_file, pretty_json_bytes
from .preflight import preflight, AuthorizationVerifier
from .projection import governed_outputs, project
from .transaction import atomic_write, create_transaction, mark_after, rollback, load_transaction, save_transaction
from .evidence import evidence
from .errors import ContractError, ProjectionFailure, TamperedTransaction
from .security import contained_path, ensure_path_object_contained

IndexProvider=Callable[[],dict[str,Any]]

def _patch(source:Path,request:dict[str,Any],target:dict[str,Any])->bytes:
    data=source.read_bytes()
    for op in request["operations"]:
        if op["type"]=="cssDeclarations":
            try: text=data.decode("utf-8")
            except UnicodeDecodeError as exc: raise ContractError("CSS source must be UTF-8") from exc
            data=patch_css(text,op["path"],op["values"]).encode("utf-8")
        else:
            data=patch_json_bytes(data,op["values"],op.get("expectedCurrent"),root=op["path"])
    return data

def _manifest_bytes(repo_root:Path,target:dict[str,Any])->bytes:
    path=contained_path(repo_root,"prisma-html/authority/rifat/visual-source-manifest.json",must_exist=True,field="visual-source-manifest")
    try: doc=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: raise ProjectionFailure(f"visual-source-manifest invalid: {exc}") from exc
    hits=[e for e in doc.get("entries",[]) if e.get("source")==target["canonicalSourcePath"] and e.get("output")==target["generatedOutputPath"] and e.get("surface")==target["surface"]]
    if len(hits)!=1: raise ProjectionFailure("exact manifest entry not unique for target surface/source/output")
    row=hits[0]
    source=contained_path(repo_root,row["source"],must_exist=True,field="manifest source")
    output=contained_path(repo_root,row["output"],must_exist=True,field="manifest output")
    row["sourceSha256"]=sha256_file(source); row["outputSha256"]=sha256_file(output)
    return pretty_json_bytes(doc)

def preview(request_value:dict[str,Any]|str|Path,index_provider:IndexProvider,repo_root:Path)->dict[str,Any]:
    request=load_request(request_value); target=preflight(request,index_provider(),repo_root)
    source=contained_path(repo_root,target["canonicalSourcePath"],must_exist=True,field="canonicalSourcePath")
    desired=_patch(source,request,target)
    return evidence("PREVIEW","NO_CHANGE" if desired==source.read_bytes() else "CHANGE_PLANNED",target_id=target["targetId"],
                    details={"beforeSha256":sha256_file(source),"afterSha256":sha256_bytes(desired),"sourcePath":target["canonicalSourcePath"],
                             "projectionMode":target["projectionMode"],"authorizationRequiredForApply":True})

def _finalize_failure(repo_root:Path,tx_root:Path,tx:dict[str,Any])->None:
    for row in tx["files"]:
        p=contained_path(repo_root,row["path"],field="transaction file")
        row["afterSha256"]=sha256_file(p) if p.exists() else None
    tx["state"]="APPLIED"; save_transaction(tx_root,tx)
    rollback(repo_root,tx_root,tx)

def apply(request_value:dict[str,Any]|str|Path,index_provider:IndexProvider,repo_root:Path,tx_root:Path,
          authorization_verifier:AuthorizationVerifier|None=None)->dict[str,Any]:
    request=load_request(request_value)
    target=preflight(request,index_provider(),repo_root,authorization_verifier)
    source=contained_path(repo_root,target["canonicalSourcePath"],must_exist=True,field="canonicalSourcePath")
    desired=_patch(source,request,target)
    authority_commit=request.get("authorityCommit")
    outputs=governed_outputs(target,repo_root,authority_commit)
    manifest=contained_path(repo_root,"prisma-html/authority/rifat/visual-source-manifest.json",must_exist=True,field="visual-source-manifest")
    source_change=desired!=source.read_bytes()
    projection_ok=False; manifest_ok=False
    if not source_change:
        try:
            project(target,repo_root,authority_commit,check=True); projection_ok=True
            manifest_ok=(manifest.read_bytes()==_manifest_bytes(repo_root,target))
        except ProjectionFailure:
            projection_ok=False
        if projection_ok and manifest_ok:
            return evidence("APPLY","IDEMPOTENT_NO_CHANGE",target_id=target["targetId"],
                            details={"sourceSha256":sha256_file(source),"projectionVerified":True,
                                     "authorization":target.get("_authorization",{})})
    tx_id=request.get("transactionId") or ("gvae-"+uuid.uuid4().hex[:16])
    tx=create_transaction(repo_root,tx_root,tx_id,target["targetId"],[source,manifest,*outputs],authority_commit)
    try:
        if source_change: atomic_write(source,desired)
        project(target,repo_root,authority_commit,check=False)
        atomic_write(manifest,_manifest_bytes(repo_root,target))
        mark_after(repo_root,tx_root,tx)
    except Exception:
        _finalize_failure(repo_root,tx_root,tx); raise
    status="APPLIED_SOURCE_STATIC" if source_change else "REPAIRED_PROJECTION_DRIFT"
    return evidence("APPLY",status,target_id=target["targetId"],transaction_id=tx_id,
                    details={"sourceSha256":sha256_file(source),"projectionVerified":True,
                             "manifestVerified":True,"authorization":target.get("_authorization",{})})

def verify(request_value:dict[str,Any]|str|Path,index_provider:IndexProvider,repo_root:Path)->dict[str,Any]:
    request=load_request(request_value); target=preflight(request,index_provider(),repo_root)
    project(target,repo_root,request.get("authorityCommit"),check=True)
    manifest=contained_path(repo_root,"prisma-html/authority/rifat/visual-source-manifest.json",must_exist=True,field="visual-source-manifest")
    if manifest.read_bytes()!=_manifest_bytes(repo_root,target): raise ProjectionFailure("visual-source-manifest hash drift")
    return evidence("VERIFY","STATIC_GREEN",target_id=target["targetId"],details={"runtimeVisualGreen":False,"manifestVerified":True})

def rollback_transaction(tx_id:str,target_id:str,repo_root:Path,tx_root:Path)->dict[str,Any]:
    tx_root=ensure_path_object_contained(repo_root,tx_root,field="transactions root")
    tx=load_transaction(tx_root,tx_id)
    if tx.get("targetId")!=target_id:
        raise TamperedTransaction("rollback targetId does not match transaction-bound target")
    result=rollback(repo_root,tx_root,tx)
    return evidence("ROLLBACK",result["status"],target_id=tx["targetId"],transaction_id=tx_id,details=result)
