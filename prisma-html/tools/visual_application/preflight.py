from __future__ import annotations
from pathlib import Path
from typing import Any, Callable
from .errors import *
from .hashing import sha256_file
from .target_index import SUPPORTED_PROJECTION_MODES
from .security import contained_path

AuthorizationVerifier=Callable[[dict[str,Any],Path,dict[str,Any]],dict[str,Any]]

def resolve_target(index:dict[str,Any],target_id:str)->dict[str,Any]:
    matches=[r for r in index.get("records",[]) if r.get("targetId")==target_id]
    if not matches: raise TargetNotFound(target_id)
    if len(matches)!=1: raise AmbiguousTarget(target_id)
    return matches[0]

def preflight(request:dict[str,Any],index:dict[str,Any],repo_root:Path,authorization_verifier:AuthorizationVerifier|None=None)->dict[str,Any]:
    if index.get("globalBlockers"):
        raise ContractError("Target Index has global blockers",details={"blockers":index.get("globalBlockers")})
    target=resolve_target(index,request["targetId"])
    mapping={"bindingId":MissingBinding,"layerId":MissingLayer,"adapterId":MissingAdapter,"recipeId":MissingRecipe,"semanticMeaningId":MissingSemantic}
    for field,exc in mapping.items():
        if not target.get(field): raise exc(field)
        if request[field]!=target[field]: raise exc(f"{field} does not match target authority")
    if target.get("status")!="APPLY_READY":
        raise ContractError("target is not APPLY_READY",details={"blockers":target.get("blockers",[])})
    if request["surface"]!=target.get("surface"): raise SurfaceExpansion("request surface differs from target")
    if request["surface"] in request["excludeSurfaces"]: raise ScopeExclusionViolation(request["surface"])
    if set(request["includeSurfaces"])!={request["surface"]}: raise SurfaceExpansion("exact-target request may include only its target surface")
    mode=target.get("projectionMode")
    if mode not in SUPPORTED_PROJECTION_MODES: raise UnsupportedProjectionMode(str(mode))
    source=target.get("canonicalSourcePath"); output=target.get("generatedOutputPath")
    if not source or not output: raise TargetNotFound("canonical source/projection missing")
    if not str(source).startswith("prisma-html/authority/rifat/"): raise DirectGeneratedProductWrite(str(source))
    source_path=contained_path(repo_root,str(source),must_exist=True,field="canonicalSourcePath")
    output_path=contained_path(repo_root,str(output),field="generatedOutputPath")
    if source_path.is_symlink() or output_path.is_symlink():
        raise PathSecurityError("source/projection symlink forbidden")
    if not source_path.is_file(): raise TargetNotFound(str(source))
    actual=sha256_file(source_path)
    if actual!=request["expectedSourceSha256"] or actual!=str(target.get("sourceSha256") or "").lower():
        raise StaleSourceHash(actual)
    suffix=source_path.suffix.lower()
    expected_op="cssDeclarations" if suffix==".css" else "jsonValues" if suffix==".json" else None
    if expected_op is None: raise UnsupportedFileType(suffix)
    seen=set()
    for op in request["operations"]:
        if op["type"]!=expected_op: raise UnsupportedFileType(f"operation {op['type']} incompatible with {suffix}")
        if expected_op=="cssDeclarations":
            if op["path"]!=target.get("selector"):
                raise ScopeExclusionViolation("CSS operation selector differs from exact target selector")
            for prop in op["values"]:
                key=(op["path"],prop)
                if key in seen: raise ContractError(f"duplicate CSS property operation: {key}")
                seen.add(key)
        else:
            root=target.get("jsonRoot")
            if not root or op["path"]!=root:
                raise ScopeExclusionViolation("JSON operation root differs from governed target root")
            for pointer in op["values"]:
                if not (pointer==root or pointer.startswith(root+"/")):
                    raise ScopeExclusionViolation(f"JSON pointer escapes exact target root: {pointer}")
                if pointer in seen: raise ContractError(f"duplicate JSON pointer operation: {pointer}")
                seen.add(pointer)
    if request["mode"]=="APPLY":
        verifier=authorization_verifier
        if verifier is None:
            from .authority import verify_application_authority
            verifier=verify_application_authority
        auth_result=verifier(request,repo_root,target)
        if not isinstance(auth_result,dict):
            raise AuthorizationError("authorization verifier returned invalid result")
        target=dict(target); target["_authorization"]=auth_result
    return target
