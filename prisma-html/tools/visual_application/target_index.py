from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
from typing import Any
from .hashing import canonical_json_bytes, pretty_json_bytes, sha256_bytes, sha256_file

ROOT=Path(__file__).resolve().parents[2]
REPO_ROOT=ROOT.parent
RIFAT=ROOT/"authority"/"rifat"
OUT=RIFAT/"prisma-ui"/"visual-control"/"target-index"
SURFACES=("tablet","pc","mobile","web","chart-lab","control-center","shared-ui")
SUPPORTED_PROJECTION_MODES={"exact-byte-copy","existing-rifat-tablet-generator"}

def load(path:Path)->dict[str,Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))

def _manifest_match(entries:list[dict[str,Any]],evidence_path:str|None,surface:str|None)->list[dict[str,Any]]:
    if not evidence_path or not surface: return []
    normalized=evidence_path.replace("\\","/").lstrip("/")
    candidates={normalized,f"apps/terminal-de-venta-system/{normalized}"}
    return [e for e in entries if e.get("surface")==surface and str(e.get("output","")).replace("\\","/") in candidates]

def _actual_hash(repo_root:Path,raw:Any)->str|None:
    if not isinstance(raw,str) or not raw: return None
    p=repo_root/raw
    try:
        resolved=p.resolve(strict=False); resolved.relative_to(repo_root.resolve())
    except Exception:
        return None
    if not p.is_file() or p.is_symlink(): return None
    return sha256_file(p)

def build_index(root:Path=ROOT)->dict[str,Any]:
    repo_root=root.parent
    rifat=root/"authority"/"rifat"
    manifest=load(rifat/"visual-source-manifest.json")
    bindings=load(rifat/"identity"/"registries"/"element-bindings.registry.json")
    recipes=load(rifat/"identity"/"registries"/"recipe.registry.json")
    adapters=load(rifat/"identity"/"registries"/"surface-adapters.registry.json")
    layers=load(rifat/"prisma-ui"/"visual-control"/"layers.json")
    entries=manifest.get("entries",[])
    recipe_rows={r.get("recipeId"):r for r in recipes.get("recipes",[]) if r.get("recipeId")}
    adapter_rows={a.get("id"):a for a in adapters.get("adapters",[]) if a.get("id")}
    layer_rows={}
    for row in layers.get("certifiedLayers",[]):
        lid=row.get("layer_id")
        if lid: layer_rows.setdefault(lid,[]).append(row)
    records=[]; global_blockers=[]
    bad_modes=sorted({str(e.get("projectionMode")) for e in entries if e.get("projectionMode") not in SUPPORTED_PROJECTION_MODES})
    if bad_modes: global_blockers.append("unsupported-projection-modes:"+",".join(bad_modes))
    target_ids=[]
    for binding in bindings.get("bindings",[]):
        selector=binding.get("selector") or {}
        surface=selector.get("surfaceId")
        recipe_id=selector.get("recipePresetId")
        semantic=selector.get("neutralMeaningId")
        for target in binding.get("targets",[]):
            target_id=target.get("targetId"); target_ids.append(target_id)
            evidence=target.get("evidence") or {}
            matches=_manifest_match(entries,evidence.get("sourceCssPath"),surface)
            manifest_entry=matches[0] if len(matches)==1 else None
            missing=[]
            if binding.get("status")!="RESOLVED" or target.get("status")!="RESOLVED": missing.append("binding")
            layer_id=target.get("layerId")
            if not layer_id: missing.append("layer")
            if not semantic or semantic=="*": missing.append("semantic")
            if recipe_id in (None,"*") or recipe_id not in recipe_rows: missing.append("recipe")
            elif recipe_rows[recipe_id].get("recipeCoverageStatus") not in (None,"COMPLETE"):
                missing.append("recipe-coverage")
            adapter_id=target.get("adapterId")
            adapter=adapter_rows.get(adapter_id) if adapter_id else None
            if not adapter: missing.append("adapter")
            elif adapter.get("surface")!=surface: missing.append("adapter-surface")
            layer_matches=layer_rows.get(layer_id,[]) if layer_id else []
            layer=layer_matches[0] if len(layer_matches)==1 else None
            if layer_id:
                if len(layer_matches)!=1: missing.append("layer-certification")
                else:
                    expected_pairs={
                        "surface":surface,
                        "selector":target.get("selector"),
                        "implementationLayerId":target.get("implementationLayerId"),
                        "neutralMeaningId":semantic
                    }
                    for key,val in expected_pairs.items():
                        if layer.get(key)!=val: missing.append("layer-authority-mismatch")
                    if layer.get("certificationStatus")!="CERTIFIED_EXACT_SOURCE_MATCH":
                        missing.append("layer-certification")
                    if layer.get("runtimeMutationAllowed") is not True or layer.get("productApplicationAllowed") is not True:
                        missing.append("layer-application-policy")
            if len(matches)!=1: missing.append("projection")
            if manifest_entry:
                if manifest_entry.get("manualEditsForbidden") is not True: missing.append("projection-policy")
                if manifest_entry.get("projectionMode") not in SUPPORTED_PROJECTION_MODES: missing.append("projection-mode")
                src_actual=_actual_hash(repo_root,manifest_entry.get("source"))
                out_actual=_actual_hash(repo_root,manifest_entry.get("output"))
                if src_actual is None or src_actual.lower()!=str(manifest_entry.get("sourceSha256") or "").lower():
                    missing.append("source-hash-drift")
                if out_actual is None or out_actual.lower()!=str(manifest_entry.get("outputSha256") or "").lower():
                    missing.append("projection-hash-drift")
            records.append({
                "targetId":target_id,"surface":surface,"selector":target.get("selector"),
                "jsonRoot":target.get("jsonRoot"),"bindingId":binding.get("bindingId"),"layerId":layer_id,
                "implementationLayerId":target.get("implementationLayerId"),"semanticMeaningId":semantic,
                "recipeId":recipe_id,"adapterId":adapter_id,
                "canonicalSourcePath":manifest_entry.get("source") if manifest_entry else None,
                "generatedOutputPath":manifest_entry.get("output") if manifest_entry else None,
                "sourceSha256":manifest_entry.get("sourceSha256") if manifest_entry else None,
                "outputSha256":manifest_entry.get("outputSha256") if manifest_entry else None,
                "projectionMode":manifest_entry.get("projectionMode") if manifest_entry else None,
                "manualEditsForbidden":manifest_entry.get("manualEditsForbidden") if manifest_entry else None,
                "status":"APPLY_READY" if not missing else "BLOCKED","blockers":sorted(set(missing))
            })
    duplicates=sorted(str(x) for x,c in Counter(target_ids).items() if x and c>1)
    if duplicates: global_blockers.append("duplicate-target-ids:"+",".join(duplicates))
    records.sort(key=lambda r:(str(r.get("surface")),str(r.get("targetId"))))
    counts=Counter(r["status"] for r in records)
    payload={"schema":"prisma.visual.application.target-index.v1","version":"1.1.0",
             "authority":"current-rifat-and-identity-source","generated":True,"manualEditsForbidden":True,
             "supportedProjectionModes":sorted(SUPPORTED_PROJECTION_MODES),"recordCount":len(records),
             "countsByStatus":dict(sorted(counts.items())),"records":records,"globalBlockers":sorted(global_blockers)}
    payload["indexDigest"]=sha256_bytes(canonical_json_bytes(payload))
    return payload

def render_files(index:dict[str,Any])->dict[Path,bytes]:
    files={OUT/"manifest.json":pretty_json_bytes(index)}
    for surface in SURFACES:
        view={"schema":"prisma.visual.application.target-index.surface.v1","surface":surface,
              "indexDigest":index["indexDigest"],"records":[r for r in index["records"] if r.get("surface")==surface]}
        files[OUT/f"{surface}.json"]=pretty_json_bytes(view)
    return files

def write(index:dict[str,Any])->None:
    for path,data in render_files(index).items():
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)

def check(index:dict[str,Any])->list[str]:
    problems=[]
    for path,data in render_files(index).items():
        if not path.exists(): problems.append(f"missing:{path.relative_to(ROOT)}")
        elif path.read_bytes()!=data: problems.append(f"drift:{path.relative_to(ROOT)}")
    return problems

def main(argv=None)->int:
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true"); g.add_argument("--check",action="store_true"); g.add_argument("--status",action="store_true")
    a=p.parse_args(argv); index=build_index()
    if a.write:
        write(index); print(json.dumps({"status":"WROTE","indexDigest":index["indexDigest"],"recordCount":index["recordCount"]},indent=2)); return 0
    if a.check:
        problems=check(index); print(json.dumps({"status":"PASS" if not problems else "FAIL","problems":problems},indent=2)); return 1 if problems else 0
    print(json.dumps(index,indent=2,ensure_ascii=False)); return 0

if __name__=="__main__": raise SystemExit(main())
