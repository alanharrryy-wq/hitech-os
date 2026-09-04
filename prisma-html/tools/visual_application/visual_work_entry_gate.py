from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .mandatory_gate import MandatoryGateError, run as run_mandatory_gate
from .surface_batch import plan_surface
from .target_index import CENSUS_KIND, DISCOVERY_ONLY, ENFORCED, EXACT_KIND, SURFACES, build_index, load_jsonl

PRISMA_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PRISMA_ROOT.parent
RIFAT = PRISMA_ROOT / "authority" / "rifat"
VISUAL_CONTROL = RIFAT / "prisma-ui" / "visual-control"
EXPANDED = VISUAL_CONTROL / "expanded"
SOURCE_MANIFEST = RIFAT / "visual-source-manifest.json"
SURFACES_FILE = VISUAL_CONTROL / "surfaces.json"
LEDGER = REPO_ROOT / "PRISMA Factory Ledger" / "PRISMA_FACTORY_LEDGER.json"
CAPABILITY = "visual.generic_application_engine_v1"
DECISIONS = ("GVAE_EXACT_APPLY", "SURFACE_BATCH_PLAN", "REGISTER_TARGET_FIRST", "BLOCKED")
STYLE_SUFFIXES = (".css", ".scss", ".sass", ".less")
COMPONENT_SUFFIXES = (".tsx", ".jsx")
ASSET_SUFFIXES = (".svg", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif")
FORBIDDEN_INTENTS = {"DIRECT_EDIT", "WILDCARD_EDIT", "UNTRACKED_VISUAL_MUTATION", "GUESS_AUTHORITY"}
EXECUTION_INTENTS = {"APPLY", "MUTATE", "EXECUTE", "GVAE_APPLY"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
IMPORTANT = re.compile(r"!\s*important\b", re.I)


class VisualWorkEntryError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise VisualWorkEntryError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=60,
    )
    if proc.returncode:
        raise VisualWorkEntryError(f"GIT_FAILED:{' '.join(args)}:{proc.stderr.strip()[:400]}")
    return proc.stdout


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD").strip()


def _norm(path: str) -> str:
    value = str(path or "").replace("\\", "/").strip().lstrip("./")
    if not value:
        return value
    if value.startswith(("apps/terminal-de-venta-system/", "prisma-html/", "PRISMA Factory Ledger/", ".github/")):
        return value
    if value.startswith(("products/", "prisma-control-center/", "config/", "styles/", "tools/quality/")):
        return "apps/terminal-de-venta-system/" + value
    return value


def _items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, (str, int, float))]
    return []


def _contains_wildcard(values: Iterable[str]) -> bool:
    return any("*" in str(value) for value in values)


def _ledger_truth() -> dict[str, Any]:
    doc = _load(LEDGER)
    rows = [row for row in doc.get("capabilities", []) if isinstance(row, dict) and row.get("id") == CAPABILITY]
    if len(rows) != 1:
        raise VisualWorkEntryError("FACTORY_LEDGER_CAPABILITY_NOT_CANONICAL")
    row = rows[0]
    errors = []
    if row.get("classification") != "DONE":
        errors.append("FACTORY_LEDGER_NOT_DONE")
    if row.get("status") != "SOURCE_READY":
        errors.append("FACTORY_LEDGER_NOT_SOURCE_READY")
    if row.get("doNotRebuild") is not True:
        errors.append("FACTORY_LEDGER_DNR_REQUIRED")
    return {"capability": row, "errors": errors}


def _path_rows_from_expanded() -> tuple[dict[str, list[dict[str, Any]]], dict[str, set[str]], dict[str, set[str]]]:
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    routes: dict[str, set[str]] = defaultdict(set)
    selectors: dict[str, set[str]] = defaultdict(set)
    path_fields = ("file", "ownerCss", "ownerComponent", "assetOwner", "assetOwners", "tokenOwner", "rollbackScope")
    for surface in SURFACES:
        for filename in ("layers.jsonl", "visual-regions.jsonl", "editable-slots.jsonl"):
            for row in load_jsonl(EXPANDED / surface / filename):
                if row.get("surface") != surface:
                    continue
                route = row.get("route")
                if isinstance(route, str) and route:
                    routes[surface].add(route)
                selector = row.get("selector")
                if isinstance(selector, str) and selector:
                    selectors[surface].add(selector)
                for field in path_fields:
                    for raw in _items(row.get(field)):
                        path = _norm(raw)
                        if path:
                            by_path[path].append({
                                "surface": surface,
                                "authority": f"VisualControl:{filename}",
                                "selector": selector,
                                "route": route,
                                "layerId": row.get("layer_id") or row.get("layerId"),
                            })
    return by_path, routes, selectors


def load_authority(*, index: dict[str, Any] | None = None) -> dict[str, Any]:
    index = index or build_index()
    surfaces_doc = _load(SURFACES_FILE)
    source_manifest = _load(SOURCE_MANIFEST)
    ledger = _ledger_truth()
    by_path, routes, selectors = _path_rows_from_expanded()
    surface_scopes: dict[str, list[str]] = {}
    for row in surfaces_doc.get("surfaces", []):
        if not isinstance(row, dict) or row.get("surface") not in SURFACES:
            continue
        surface = str(row["surface"])
        scopes = []
        for raw in row.get("allowedScope", []):
            raw = str(raw).removesuffix("**").rstrip("/")
            scopes.append(_norm(raw))
        surface_scopes[surface] = scopes

    manifest_paths: dict[str, list[dict[str, Any]]] = defaultdict(list)
    generated_outputs: dict[str, dict[str, Any]] = {}
    for row in source_manifest.get("entries", []):
        if not isinstance(row, dict):
            continue
        for field in ("source", "output"):
            path = _norm(str(row.get(field) or ""))
            if path:
                manifest_paths[path].append({
                    "surface": row.get("surface"),
                    "authority": f"visual-source-manifest:{field}",
                    "generated": bool(row.get("generated")),
                    "manualEditsForbidden": row.get("manualEditsForbidden"),
                })
        out = _norm(str(row.get("output") or ""))
        if out and row.get("generated") is True and row.get("manualEditsForbidden") is True:
            generated_outputs[out] = row

    targets_by_id: dict[str, dict[str, Any]] = {}
    targets_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in index.get("records", []):
        if not isinstance(row, dict) or not row.get("targetId"):
            continue
        targets_by_id[str(row["targetId"])] = row
        for field in ("canonicalSourcePath", "generatedOutputPath", "ownerCss"):
            path = _norm(str(row.get(field) or ""))
            if path:
                targets_by_path[path].append(row)

    return {
        "index": index,
        "surfaceScopes": surface_scopes,
        "visualRowsByPath": by_path,
        "manifestRowsByPath": manifest_paths,
        "generatedOutputs": generated_outputs,
        "targetsById": targets_by_id,
        "targetsByPath": targets_by_path,
        "routes": routes,
        "selectors": selectors,
        "ledger": ledger,
    }


def classify_path(path: str, authority: dict[str, Any]) -> dict[str, Any]:
    path = _norm(path)
    reasons: list[str] = []
    surfaces: set[str] = set()
    rows = authority["visualRowsByPath"].get(path, [])
    for row in rows:
        reasons.append(str(row.get("authority")))
        if row.get("surface") in SURFACES:
            surfaces.add(str(row["surface"]))
    for row in authority["manifestRowsByPath"].get(path, []):
        reasons.append(str(row.get("authority")))
        if row.get("surface") in SURFACES:
            surfaces.add(str(row["surface"]))
    targets = authority["targetsByPath"].get(path, [])
    for row in targets:
        reasons.append("GVAE:TargetIndex")
        if row.get("surface") in SURFACES:
            surfaces.add(str(row["surface"]))

    suffix = Path(path).suffix.lower()
    for surface, scopes in authority["surfaceScopes"].items():
        if any(path == scope or path.startswith(scope.rstrip("/") + "/") for scope in scopes):
            if suffix in STYLE_SUFFIXES:
                reasons.append("VisualControl:governed-style-scope")
                surfaces.add(surface)
            elif suffix in COMPONENT_SUFFIXES and rows:
                reasons.append("VisualControl:owned-component")
                surfaces.add(surface)
            elif suffix in ASSET_SUFFIXES and rows:
                reasons.append("VisualControl:owned-asset")
                surfaces.add(surface)

    return {
        "path": path,
        "visual": bool(reasons),
        "surfaces": sorted(surfaces),
        "reasons": sorted(set(reasons)),
        "targets": targets,
        "generatedProjection": path in authority["generatedOutputs"],
    }


def _mesh_errors(mesh: Any, head: str) -> list[str]:
    if not isinstance(mesh, dict):
        return ["CURRENT_TASK_AUTHORITY_MESH_REQUIRED"]
    errors = []
    if mesh.get("status") != "PASS_COMPOSED_AUTHORITY_MESH":
        errors.append("AUTHORITY_MESH_NOT_PASS")
    if mesh.get("repoHead") != head:
        errors.append("AUTHORITY_MESH_STALE_HEAD")
    if mesh.get("requiredAuthorityCoveragePct") != 100:
        errors.append("AUTHORITY_MESH_COVERAGE_NOT_100")
    if mesh.get("blockers") != 0:
        errors.append("AUTHORITY_MESH_BLOCKERS")
    if mesh.get("layerMapPresent") is not True:
        errors.append("LAYER_MAP_REQUIRED")
    for field in ("requestDigest", "artifactDigest"):
        value = mesh.get(field)
        if not isinstance(value, str) or not HEX64.fullmatch(value):
            errors.append(f"AUTHORITY_MESH_{field.upper()}_INVALID")
    return errors


def _decision(decision: str, *, reasons: list[str], details: dict[str, Any] | None = None, missing: list[str] | None = None) -> dict[str, Any]:
    if decision not in DECISIONS:
        raise VisualWorkEntryError("INVALID_INTERNAL_DECISION")
    return {
        "schema": "prisma.visual.work-entry.decision.v1",
        "decision": decision,
        "reasons": sorted(set(reasons)),
        "missingAuthority": sorted(set(missing or [])),
        "details": details or {},
        "runtimeVisualGreen": False,
        "wholeSurfaceApplyReady": False,
        "productionReady": False,
        "doesNotProve": [
            "browser/runtime visual certification",
            "whole-surface APPLY readiness",
            "production readiness",
        ],
    }


def decide_request(request: dict[str, Any], *, authority: dict[str, Any] | None = None, current_head: str | None = None) -> dict[str, Any]:
    authority = authority or load_authority()
    head = current_head or _head(REPO_ROOT)
    if not isinstance(request, dict):
        return _decision("BLOCKED", reasons=["REQUEST_OBJECT_REQUIRED"])
    expected = str(request.get("expectedHead") or "").strip()
    if expected and expected != head:
        return _decision("BLOCKED", reasons=["EXPECTED_HEAD_MISMATCH"], details={"expectedHead": expected, "currentHead": head})
    if authority["ledger"]["errors"]:
        return _decision("BLOCKED", reasons=authority["ledger"]["errors"])
    if authority["index"].get("globalBlockers"):
        return _decision("BLOCKED", reasons=["TARGET_INDEX_GLOBAL_BLOCKER"], details={"blockers": authority["index"]["globalBlockers"]})

    task = str(request.get("task") or "").strip()
    if len(task) < 3:
        return _decision("BLOCKED", reasons=["TASK_REQUIRED"])
    surfaces = _items(request.get("surfaces") if request.get("surfaces") is not None else request.get("surface"))
    routes = _items(request.get("routes"))
    files = [_norm(v) for v in _items(request.get("files"))]
    selectors = _items(request.get("selectors"))
    target_ids = _items(request.get("targetIds"))
    intent = str(request.get("intention") or request.get("intent") or request.get("mode") or "ENTRY").upper().strip()
    if intent in FORBIDDEN_INTENTS:
        return _decision("BLOCKED", reasons=[f"FORBIDDEN_INTENT:{intent}"])
    if _contains_wildcard([*surfaces, *routes, *files, *selectors, *target_ids]):
        return _decision("BLOCKED", reasons=["WILDCARD_SCOPE_FORBIDDEN"])
    unknown_surfaces = sorted(set(surfaces) - set(SURFACES))
    if unknown_surfaces:
        return _decision("BLOCKED", reasons=["UNKNOWN_SURFACE"], details={"unknownSurfaces": unknown_surfaces})

    explicit_records: list[dict[str, Any]] = []
    for target_id in target_ids:
        row = authority["targetsById"].get(target_id)
        if not row:
            return _decision("BLOCKED", reasons=["TARGET_ID_UNKNOWN"], details={"targetId": target_id})
        explicit_records.append(row)
    if surfaces and any(row.get("surface") not in surfaces for row in explicit_records):
        return _decision("BLOCKED", reasons=["CROSS_SURFACE_TARGET_MISMATCH"])

    path_info = [classify_path(path, authority) for path in files]
    ambiguous = [row for row in path_info if len(row["surfaces"]) > 1]
    if ambiguous:
        return _decision("BLOCKED", reasons=["AMBIGUOUS_VISUAL_OWNERSHIP"], details={"paths": ambiguous})
    inferred_surfaces = {s for row in path_info for s in row["surfaces"]}
    if surfaces and inferred_surfaces and not inferred_surfaces.issubset(set(surfaces)):
        return _decision("BLOCKED", reasons=["CROSS_SURFACE_FILE_MISMATCH"])

    if any("hash-drift" in str(blocker) for row in explicit_records for blocker in row.get("blockers", [])):
        return _decision("BLOCKED", reasons=["STALE_SOURCE_OR_PROJECTION_HASH"])

    if explicit_records:
        if any(row.get("recordKind") == CENSUS_KIND or row.get("enforcement") == DISCOVERY_ONLY for row in explicit_records):
            missing = [str(x) for row in explicit_records for x in row.get("blockers", [])]
            return _decision("REGISTER_TARGET_FIRST", reasons=["DISCOVERY_ONLY_PHYSICAL_COORDINATE"], missing=missing, details={"targetIds": target_ids})
        if any(row.get("recordKind") != EXACT_KIND or row.get("enforcement") != ENFORCED for row in explicit_records):
            return _decision("BLOCKED", reasons=["TARGET_ENFORCEMENT_INVALID"])
        blocked = [row for row in explicit_records if row.get("status") != "APPLY_READY"]
        if blocked:
            missing = [str(x) for row in blocked for x in row.get("blockers", [])]
            return _decision("BLOCKED", reasons=["EXACT_TARGET_NOT_APPLY_READY"], missing=missing, details={"targetIds": [r.get("targetId") for r in blocked]})
        if intent in EXECUTION_INTENTS:
            mesh_errors = _mesh_errors(request.get("authorityMesh"), head)
            if mesh_errors:
                return _decision("BLOCKED", reasons=mesh_errors)
        return _decision("GVAE_EXACT_APPLY", reasons=["EXACT_GVAE_TARGET_APPLY_READY"], details={
            "targetIds": target_ids,
            "requiredExecutionGates": ["Factory Ledger MUTATION PASS", "current task-exact Authority Mesh + Layer Map", "hash-pinned Code Atlas UI Bridge plan/diff", "GVAE PREVIEW/APPLY/receipt/VERIFY"],
        })

    broad = bool(surfaces) and not any([files, selectors, routes, target_ids])
    if broad or intent in {"SURFACE_BATCH", "WHOLE_SURFACE", "BATCH_PLAN"}:
        plans = [plan_surface(surface, index=authority["index"]) for surface in surfaces]
        if not plans:
            return _decision("BLOCKED", reasons=["SURFACE_REQUIRED_FOR_BATCH"])
        if any(plan.get("recordCount", 0) == 0 for plan in plans):
            return _decision("BLOCKED", reasons=["SURFACE_HAS_NO_VISUAL_CONTROL_CENSUS"], details={"plans": plans})
        return _decision("SURFACE_BATCH_PLAN", reasons=["WHOLE_SURFACE_IS_EXACT_TARGET_COMPOSITION_NOT_WILDCARD"], details={"plans": plans})

    matched: list[dict[str, Any]] = []
    for row in path_info:
        matched.extend(row["targets"])
    if selectors:
        matched.extend(row for row in authority["index"].get("records", []) if row.get("selector") in selectors and (not surfaces or row.get("surface") in surfaces))
    matched = list({str(row.get("targetId")): row for row in matched if row.get("targetId")}.values())
    if matched:
        if any("hash-drift" in str(blocker) for row in matched for blocker in row.get("blockers", [])):
            return _decision("BLOCKED", reasons=["STALE_SOURCE_OR_PROJECTION_HASH"])
        census = [row for row in matched if row.get("recordKind") == CENSUS_KIND or row.get("enforcement") == DISCOVERY_ONLY]
        if census:
            return _decision("REGISTER_TARGET_FIRST", reasons=["VISUAL_CONTROL_CENSUS_REQUIRES_SEMANTIC_PROMOTION"], missing=[str(x) for row in census for x in row.get("blockers", [])], details={"matchedTargets": [r.get("targetId") for r in census]})
        exact = [row for row in matched if row.get("recordKind") == EXACT_KIND and row.get("enforcement") == ENFORCED]
        if exact and all(row.get("status") == "APPLY_READY" for row in exact):
            return _decision("GVAE_EXACT_APPLY", reasons=["RESOLVED_TO_EXACT_APPLY_READY_TARGETS"], details={"targetIds": [r.get("targetId") for r in exact]})
        return _decision("BLOCKED", reasons=["MATCHED_VISUAL_TARGET_NOT_APPLY_READY"])

    visual_paths = [row for row in path_info if row["visual"]]
    if visual_paths:
        return _decision("BLOCKED", reasons=["GOVERNED_VISUAL_SCOPE_WITHOUT_CENSUS_TARGET"], details={"paths": visual_paths})

    if routes:
        candidates = [surface for surface in (surfaces or list(SURFACES)) if any(route in authority["routes"].get(surface, set()) for route in routes)]
        if not candidates:
            return _decision("BLOCKED", reasons=["ROUTE_OUTSIDE_VISUAL_GOVERNANCE"])
        return _decision("SURFACE_BATCH_PLAN", reasons=["ROUTE_SCOPE_REQUIRES_BOUNDED_SURFACE_PLANNING"], details={"surfaces": candidates})

    return _decision("BLOCKED", reasons=["NO_GOVERNED_VISUAL_COORDINATE_RESOLVED"])


def _changed_paths(repo: Path, base: str, head: str) -> list[str]:
    raw = _git(repo, "diff", "--name-only", "--diff-filter=ACDMRTUXB", base, head, "--")
    return sorted({_norm(line) for line in raw.splitlines() if line.strip()})


def _added_important(repo: Path, base: str, head: str, visual_paths: set[str]) -> list[str]:
    patch = _git(repo, "diff", "--unified=0", base, head, "--", *sorted(visual_paths)) if visual_paths else ""
    hits = []
    current = ""
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            current = _norm(line[6:])
        elif line.startswith("+") and not line.startswith("+++") and IMPORTANT.search(line[1:]):
            hits.append(current or "UNKNOWN")
    return sorted(set(hits))


def _source_for_projection(path: str, authority: dict[str, Any]) -> str | None:
    row = authority["generatedOutputs"].get(path)
    return _norm(str(row.get("source") or "")) if isinstance(row, dict) else None


def evaluate_changed(*, authority: dict[str, Any], changed: Iterable[str], mandatory_result: dict[str, Any], important_paths: Iterable[str] = ()) -> dict[str, Any]:
    changed_set = {_norm(p) for p in changed}
    infos = [classify_path(p, authority) for p in sorted(changed_set)]
    visual = [row for row in infos if row["visual"]]
    errors: list[str] = []
    if important_paths:
        errors.extend(f"PRIORITY_OVERRIDE_FORBIDDEN:{_norm(p)}" for p in important_paths)
    for info in visual:
        path = info["path"]
        if len(info["surfaces"]) > 1:
            errors.append(f"AMBIGUOUS_VISUAL_OWNERSHIP:{path}")
            continue
        if info["generatedProjection"]:
            source = _source_for_projection(path, authority)
            if not source or source not in changed_set:
                errors.append(f"GENERATED_PROJECTION_MANUAL_EDIT:{path}")
        rows = info["targets"]
        exact = [r for r in rows if r.get("recordKind") == EXACT_KIND and r.get("enforcement") == ENFORCED]
        census = [r for r in rows if r.get("recordKind") == CENSUS_KIND or r.get("enforcement") == DISCOVERY_ONLY]
        if any("hash-drift" in str(b) for r in rows for b in r.get("blockers", [])):
            errors.append(f"STALE_VISUAL_AUTHORITY:{path}")
        if exact:
            if any(r.get("status") != "APPLY_READY" for r in exact):
                errors.append(f"EXACT_TARGET_NOT_APPLY_READY:{path}")
            elif mandatory_result.get("status") != "PASS_GVAE_MANDATORY_GATE":
                errors.append(f"GVAE_RECEIPT_GATE_REQUIRED:{path}")
        elif census:
            errors.append(f"REGISTER_TARGET_FIRST_REQUIRED:{path}")
        else:
            errors.append(f"UNREGISTERED_GOVERNED_VISUAL_MUTATION:{path}")
    if mandatory_result.get("status") != "PASS_GVAE_MANDATORY_GATE" and mandatory_result.get("protectedChanged"):
        errors.extend(str(x) for x in mandatory_result.get("errors", []))
    return {
        "schema": "prisma.visual.work-entry.diff-enforcement.v1",
        "status": "PASS_VISUAL_WORK_ENTRY_DIFF_GATE" if not errors else "BLOCKED_VISUAL_WORK_ENTRY_DIFF_GATE",
        "changedCount": len(changed_set),
        "visualChangedCount": len(visual),
        "visualChanges": visual,
        "errors": sorted(set(errors)),
        "mandatoryGate": mandatory_result,
        "runtimeVisualGreen": False,
        "productionReady": False,
    }


def enforce_diff(repo: Path, base: str, head: str) -> dict[str, Any]:
    authority = load_authority()
    changed = _changed_paths(repo, base, head)
    visual_paths = {p for p in changed if classify_path(p, authority)["visual"]}
    try:
        mandatory = run_mandatory_gate(repo, base, head)
    except (MandatoryGateError, OSError, ValueError, KeyError, TypeError) as exc:
        mandatory = {"status": "BLOCKED_GVAE_MANDATORY_GATE", "protectedChanged": [], "errors": [f"MANDATORY_GATE_EXECUTION_ERROR:{exc}"]}
    return evaluate_changed(
        authority=authority,
        changed=changed,
        mandatory_result=mandatory,
        important_paths=_added_important(repo, base, head, visual_paths),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Universal fail-closed entry gate for PRISMA governed visual work")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--request", help="visual-work-entry request JSON")
    mode.add_argument("--base", help="PR diff base SHA")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    try:
        repo = Path(args.repo_root).resolve()
        if args.request:
            path = Path(args.request)
            if not path.is_absolute():
                path = repo / path
            result = decide_request(_load(path), current_head=_head(repo))
            code = 0 if result["decision"] != "BLOCKED" else 2
        else:
            result = enforce_diff(repo, args.base, args.head)
            code = 0 if result["status"] == "PASS_VISUAL_WORK_ENTRY_DIFF_GATE" else 2
    except Exception as exc:
        result = _decision("BLOCKED", reasons=[f"GATE_EXECUTION_ERROR:{type(exc).__name__}:{exc}"])
        code = 2
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
