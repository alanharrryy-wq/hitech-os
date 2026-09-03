from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
from typing import Any
from .hashing import canonical_json_bytes, pretty_json_bytes, sha256_bytes

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
RIFAT = ROOT / "authority" / "rifat"
OUT = RIFAT / "prisma-ui" / "visual-control" / "target-index"
MANIFEST = RIFAT / "visual-source-manifest.json"
BINDINGS = RIFAT / "identity" / "registries" / "element-bindings.registry.json"
RECIPES = RIFAT / "identity" / "registries" / "recipe.registry.json"
ADAPTERS = RIFAT / "identity" / "registries" / "surface-adapters.registry.json"
SURFACES = ("tablet", "pc", "mobile", "web", "chart-lab", "control-center", "shared-ui")
SUPPORTED_PROJECTION_MODES = {"exact-byte-copy", "existing-rifat-tablet-generator"}


def load(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding="utf-8-sig"))

def _repo_rel(path: str) -> str:
    return path[len("prisma-html/"):] if path.startswith("prisma-html/") else path

def _manifest_match(entries: list[dict[str, Any]], evidence_path: str | None) -> list[dict[str, Any]]:
    if not evidence_path: return []
    normalized = evidence_path.replace("\\", "/")
    suffixes = {normalized, f"apps/terminal-de-venta-system/{normalized}"}
    return [e for e in entries if e.get("output") in suffixes or str(e.get("output", "")).endswith("/" + normalized)]

def build_index(root: Path = ROOT) -> dict[str, Any]:
    rifat = root / "authority" / "rifat"
    manifest = load(rifat / "visual-source-manifest.json")
    bindings = load(rifat / "identity" / "registries" / "element-bindings.registry.json")
    recipes = load(rifat / "identity" / "registries" / "recipe.registry.json")
    adapters = load(rifat / "identity" / "registries" / "surface-adapters.registry.json")
    entries = manifest.get("entries", [])
    recipe_ids = {r.get("recipeId") for r in recipes.get("recipes", [])}
    adapter_ids = {a.get("id") for a in adapters.get("adapters", [])}
    records: list[dict[str, Any]] = []
    global_blockers: list[str] = []
    bad_modes = sorted({str(e.get("projectionMode")) for e in entries if e.get("projectionMode") not in SUPPORTED_PROJECTION_MODES})
    if bad_modes: global_blockers.append("unsupported-projection-modes:" + ",".join(bad_modes))
    for binding in bindings.get("bindings", []):
        selector = binding.get("selector", {})
        recipe_id = selector.get("recipePresetId")
        for target in binding.get("targets", []):
            evidence = target.get("evidence") or {}
            matches = _manifest_match(entries, evidence.get("sourceCssPath"))
            manifest_entry = matches[0] if len(matches) == 1 else None
            missing = []
            if binding.get("status") != "RESOLVED" or target.get("status") != "RESOLVED": missing.append("binding")
            if not target.get("layerId"): missing.append("layer")
            if not selector.get("neutralMeaningId") or selector.get("neutralMeaningId") == "*": missing.append("semantic")
            if recipe_id in (None, "*") or recipe_id not in recipe_ids: missing.append("recipe")
            # V1 refuses to infer an exact element adapter from a surface-level adapter registry.
            adapter_id = target.get("adapterId")
            if not adapter_id or adapter_id not in adapter_ids: missing.append("adapter")
            if len(matches) != 1: missing.append("projection")
            record = {
                "targetId": target.get("targetId"), "surface": selector.get("surfaceId"),
                "selector": target.get("selector"), "bindingId": binding.get("bindingId"),
                "layerId": target.get("layerId"), "semanticMeaningId": selector.get("neutralMeaningId"),
                "recipeId": recipe_id, "adapterId": adapter_id,
                "canonicalSourcePath": manifest_entry.get("source") if manifest_entry else None,
                "generatedOutputPath": manifest_entry.get("output") if manifest_entry else None,
                "sourceSha256": manifest_entry.get("sourceSha256") if manifest_entry else None,
                "outputSha256": manifest_entry.get("outputSha256") if manifest_entry else None,
                "projectionMode": manifest_entry.get("projectionMode") if manifest_entry else None,
                "manualEditsForbidden": manifest_entry.get("manualEditsForbidden") if manifest_entry else None,
                "status": "APPLY_READY" if not missing else "BLOCKED",
                "blockers": sorted(set(missing)),
            }
            records.append(record)
    records.sort(key=lambda r: (str(r.get("surface")), str(r.get("targetId"))))
    counts = Counter(r["status"] for r in records)
    payload = {
        "schema": "prisma.visual.application.target-index.v1", "version": "1.0.0",
        "authority": "current-rifat-and-identity-source", "generated": True,
        "manualEditsForbidden": True, "supportedProjectionModes": sorted(SUPPORTED_PROJECTION_MODES),
        "recordCount": len(records), "countsByStatus": dict(sorted(counts.items())),
        "records": records, "globalBlockers": global_blockers,
    }
    payload["indexDigest"] = sha256_bytes(canonical_json_bytes(payload))
    return payload

def render_files(index: dict[str, Any]) -> dict[Path, bytes]:
    files = {OUT / "manifest.json": pretty_json_bytes(index)}
    for surface in SURFACES:
        view = {"schema":"prisma.visual.application.target-index.surface.v1","surface":surface,"indexDigest":index["indexDigest"],"records":[r for r in index["records"] if r.get("surface")==surface]}
        files[OUT / f"{surface}.json"] = pretty_json_bytes(view)
    return files

def write(index: dict[str, Any]) -> None:
    for path, data in render_files(index).items(): path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)

def check(index: dict[str, Any]) -> list[str]:
    problems=[]
    for path,data in render_files(index).items():
        if not path.exists(): problems.append(f"missing:{path.relative_to(ROOT)}")
        elif path.read_bytes()!=data: problems.append(f"drift:{path.relative_to(ROOT)}")
    return problems

def main(argv=None) -> int:
    p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True); g.add_argument("--write",action="store_true"); g.add_argument("--check",action="store_true"); g.add_argument("--status",action="store_true"); a=p.parse_args(argv)
    index=build_index()
    if a.write: write(index); print(json.dumps({"status":"WROTE","indexDigest":index["indexDigest"],"recordCount":index["recordCount"]},indent=2)); return 0
    if a.check:
        problems=check(index); print(json.dumps({"status":"PASS" if not problems else "FAIL","problems":problems},indent=2)); return 1 if problems else 0
    print(json.dumps(index,indent=2,ensure_ascii=False)); return 0
if __name__=="__main__": raise SystemExit(main())
