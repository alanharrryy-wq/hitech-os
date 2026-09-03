from __future__ import annotations
from pathlib import Path
from typing import Any
from .errors import *
from .hashing import sha256_file
from .target_index import SUPPORTED_PROJECTION_MODES


def resolve_target(index: dict[str, Any], target_id: str) -> dict[str, Any]:
    matches=[r for r in index.get("records",[]) if r.get("targetId")==target_id]
    if not matches: raise TargetNotFound(target_id)
    if len(matches)!=1: raise AmbiguousTarget(target_id)
    return matches[0]

def preflight(request: dict[str, Any], index: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    target=resolve_target(index, request["targetId"])
    mapping={"bindingId":MissingBinding,"layerId":MissingLayer,"adapterId":MissingAdapter,"recipeId":MissingRecipe,"semanticMeaningId":MissingSemantic}
    for field, exc in mapping.items():
        if not target.get(field): raise exc(field)
        if request[field]!=target[field]: raise exc(f"{field} does not match target authority")
    if target.get("status")!="APPLY_READY": raise ContractError("target is not APPLY_READY",details={"blockers":target.get("blockers",[])})
    if request["surface"]!=target.get("surface"): raise SurfaceExpansion("request surface differs from target")
    if request["surface"] in request["excludeSurfaces"]: raise ScopeExclusionViolation(request["surface"])
    if request["surface"] not in request["includeSurfaces"]: raise SurfaceExpansion(request["surface"])
    mode=target.get("projectionMode")
    if mode not in SUPPORTED_PROJECTION_MODES: raise UnsupportedProjectionMode(str(mode))
    source=target.get("canonicalSourcePath")
    output=target.get("generatedOutputPath")
    if not source or not output: raise TargetNotFound("canonical source/projection missing")
    if not source.startswith("prisma-html/authority/rifat/"): raise DirectGeneratedProductWrite(source)
    source_path=repo_root/source
    if not source_path.is_file(): raise TargetNotFound(source)
    actual=sha256_file(source_path)
    if actual!=request["expectedSourceSha256"] or actual!=target.get("sourceSha256"): raise StaleSourceHash(actual)
    suffix=source_path.suffix.lower()
    if suffix in {".css"}: expected_op="cssDeclarations"
    elif suffix==".json": expected_op="jsonValues"
    else: raise UnsupportedFileType(suffix)
    for op in request["operations"]:
        if op["type"]!=expected_op: raise UnsupportedFileType(f"operation {op['type']} incompatible with {suffix}")
    return target
