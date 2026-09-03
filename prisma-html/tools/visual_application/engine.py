from __future__ import annotations
import json, uuid
from pathlib import Path
from typing import Any, Callable
from .contracts import load_request
from .css_writer import patch_css
from .json_writer import patch_json_bytes
from .hashing import sha256_bytes, sha256_file, pretty_json_bytes
from .preflight import preflight
from .projection import governed_outputs, project
from .transaction import atomic_write, create_transaction, mark_after, rollback, load_transaction
from .evidence import evidence

IndexProvider=Callable[[],dict[str,Any]]

def _patch(source:Path,request:dict[str,Any])->bytes:
    data=source.read_bytes()
    for op in request["operations"]:
        if op["type"]=="cssDeclarations":
            data=patch_css(data.decode("utf-8"),op["path"],{str(k):str(v) for k,v in op["values"].items()}).encode("utf-8")
        else:
            data=patch_json_bytes(data,op["values"],op.get("expectedCurrent"))
    return data

def _update_visual_manifest(repo_root:Path,target:dict[str,Any])->bytes:
    path=repo_root/"prisma-html/authority/rifat/visual-source-manifest.json"; doc=json.loads(path.read_text(encoding="utf-8"))
    hits=[e for e in doc.get("entries",[]) if e.get("source")==target["canonicalSourcePath"] and e.get("output")==target["generatedOutputPath"]]
    if len(hits)!=1: raise RuntimeError("exact manifest entry not unique")
    row=hits[0]; row["sourceSha256"]=sha256_file(repo_root/row["source"]); row["outputSha256"]=sha256_file(repo_root/row["output"])
    return pretty_json_bytes(doc)
def preview(request_value:dict[str,Any]|str|Path,index_provider:IndexProvider,repo_root:Path)->dict[str,Any]:
    request=load_request(request_value); target=preflight(request,index_provider(),repo_root); source=repo_root/target["canonicalSourcePath"]; desired=_patch(source,request)
    return evidence("PREVIEW","NO_CHANGE" if desired==source.read_bytes() else "CHANGE_PLANNED",target_id=target["targetId"],details={"beforeSha256":sha256_file(source),"afterSha256":sha256_bytes(desired),"sourcePath":target["canonicalSourcePath"],"projectionMode":target["projectionMode"]})
def apply(request_value:dict[str,Any]|str|Path,index_provider:IndexProvider,repo_root:Path,tx_root:Path)->dict[str,Any]:
    request=load_request(request_value); target=preflight(request,index_provider(),repo_root); source=repo_root/target["canonicalSourcePath"]; desired=_patch(source,request)
    if desired==source.read_bytes(): return evidence("APPLY","IDEMPOTENT_NO_CHANGE",target_id=target["targetId"],details={"sourceSha256":sha256_file(source)})
    authority_commit=request.get("authorityCommit"); outputs=governed_outputs(target,repo_root,authority_commit); manifest=repo_root/"prisma-html/authority/rifat/visual-source-manifest.json"
    tx_id=request.get("transactionId") or ("gvae-"+uuid.uuid4().hex[:16]); tx=create_transaction(repo_root,tx_root,tx_id,[source,manifest,*outputs],authority_commit)
    try:
        atomic_write(source,desired); project(target,repo_root,authority_commit,check=False); atomic_write(manifest,_update_visual_manifest(repo_root,target)); mark_after(repo_root,tx_root,tx)
    except Exception:
        # Snapshot the state produced up to failure, then restore only while it still matches.
        for row in tx["files"]:
            p=repo_root/row["path"]; row["afterSha256"]=sha256_file(p) if p.exists() else None
        tx["state"]="APPLIED"; from .transaction import save_transaction; save_transaction(tx_root,tx); rollback(repo_root,tx_root,tx); raise
    return evidence("APPLY","APPLIED_SOURCE_STATIC",target_id=target["targetId"],transaction_id=tx_id,details={"sourceSha256":sha256_file(source),"projectionVerified":True})
def verify(request_value:dict[str,Any]|str|Path,index_provider:IndexProvider,repo_root:Path)->dict[str,Any]:
    request=load_request(request_value); target=preflight(request,index_provider(),repo_root); project(target,repo_root,request.get("authorityCommit"),check=True)
    return evidence("VERIFY","STATIC_GREEN",target_id=target["targetId"],details={"runtimeVisualGreen":False})
def rollback_transaction(tx_id:str,target_id:str,repo_root:Path,tx_root:Path)->dict[str,Any]:
    result=rollback(repo_root,tx_root,load_transaction(tx_root,tx_id)); return evidence("ROLLBACK",result["status"],target_id=target_id,transaction_id=tx_id,details=result)
