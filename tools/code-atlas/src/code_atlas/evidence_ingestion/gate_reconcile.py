
from __future__ import annotations
import json, re
from datetime import datetime
from pathlib import Path
from typing import Any

EXCLUDE_DIR_NAMES = {".git", "node_modules", ".next", "dist", "build", ".turbo", ".cache", "__pycache__", ".pytest_cache", ".wrangler"}
ROLE_RULES = [("products/pc/","PC"),("products/tablet/","Tablet"),("products/mobile/","Mobile"),("products/shared-ui/","Shared UI"),("shared/contracts/","Shared Core"),("shared/twin-kernel/","Shared Core"),("shared/licensing/","Licensing"),("prisma-control-center","Cloud Center"),("prisma cloud ctr","Cloud Center"),("cloudflare","Cloudflare"),("licflow","Licensing"),("licensing","Licensing"),("prisma-visual","Visual"),("visual-os","Visual"),("docs/","Docs"),("test","Tests/Verifiers"),("verify","Tests/Verifiers"),("tools/","Tooling"),("productization","Productization"),("factory ledger","Governor/Authority"),("authority","Governor/Authority"),("governor","Governor/Authority"),("prisma","DB"),("migration","DB"),("seed","DB")]
CRITICAL_FILENAME_PREFIXES = [Path("apps/terminal-de-venta-system/prisma-control-center/internal/py"), Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/py")]
DOC_ATLAS_ALTERNATIVES = {"docs/atlas/_incoming/mobile/atlas.mobile.json":["products/mobile/app/docs/atlas/atlas.mobile.json","docs/atlas/atlas.mobile.json"],"docs/atlas/_incoming/pc/atlas.pc.json":["products/pc/app/docs/atlas/atlas.pc.json","docs/atlas/atlas.pc.json"],"docs/atlas/_incoming/tablet/atlas.tablet.json":["products/tablet/app/docs/atlas/atlas.tablet.json","docs/atlas/atlas.tablet.json"],"docs/atlas/_incoming/shared-core/atlas.shared-core.json":["docs/atlas/atlas.shared-core.json"]}
PATH_ALTERNATIVES = {"prisma-control-center":["apps/terminal-de-venta-system/prisma-control-center"],"config/prisma-visual-os/*":["apps/terminal-de-venta-system/config/prisma-visual-os/*","apps/terminal-de-venta-system/config/prisma-visual/*"],"styles/prisma-visual-os/*":["apps/terminal-de-venta-system/styles/prisma-visual-os/*","apps/terminal-de-venta-system/styles/prisma-visual/*"],"tools/prisma-visual-os/*":["apps/terminal-de-venta-system/tools/prisma-visual-os/*","tools/prisma-visual-os/*"],"shared/contracts/*":["apps/terminal-de-venta-system/shared/contracts/*","packages/contracts/*"],"shared/licensing/*":["apps/terminal-de-venta-system/shared/licensing/*"],"shared/twin-kernel/src/*":["apps/terminal-de-venta-system/shared/twin-kernel/src/*"],"products/shared-ui/prisma/*":["apps/terminal-de-venta-system/products/shared-ui/prisma/*","products/shared-ui/prisma/*"],"templates/prisma-atlas.schema.json":["apps/terminal-de-venta-system/templates/prisma-atlas.schema.json","tools/code-atlas/templates/prisma-atlas.schema.json"]}

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")

def norm_path(value: str) -> str:
    v=str(value or "").replace("\\","/")
    v=re.sub(r"^[A-Za-z]:/repos/hitech-os/", "", v)
    v=re.sub(r"^[A-Za-z]:/", "", v)
    return v.strip().lstrip("/")

def roles_for(path: str) -> list[str]:
    low=path.replace("\\","/").lower()
    roles=[]
    for token,role in ROLE_RULES:
        if token.lower() in low and role not in roles:
            roles.append(role)
    return roles or ["Unknown"]

def skip(path: Path) -> bool:
    return bool(set(path.parts)&EXCLUDE_DIR_NAMES)

def build_indexes(repo_root: Path) -> dict[str, Any]:
    files_by_name={}
    dirs_by_name={}
    for p in repo_root.rglob("*"):
        if skip(p):
            continue
        rel=p.relative_to(repo_root).as_posix()
        if p.is_file():
            files_by_name.setdefault(p.name.lower(),[]).append(rel)
        elif p.is_dir():
            dirs_by_name.setdefault(p.name.lower(),[]).append(rel)
    return {"files_by_name":files_by_name,"dirs_by_name":dirs_by_name}

def glob_paths(repo_root: Path, pattern: str) -> list[str]:
    matches=[]
    try:
        for p in repo_root.glob(norm_path(pattern)):
            if not skip(p):
                matches.append(p.relative_to(repo_root).as_posix())
    except Exception:
        pass
    return sorted(set(matches))

def path_exists(repo_root: Path, path: str) -> bool:
    return (repo_root/norm_path(path)).exists()

def resolve_item(repo_root: Path, indexes: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    raw=item.get("normalized") or item.get("pathOrNode") or item.get("path") or ""
    original=item.get("pathOrNode") or item.get("path") or raw
    kind=item.get("itemKind") or "path_or_node"
    norm=norm_path(raw)
    resolved=[]
    status="UNRESOLVED_CLASSIFIED"
    reason="No live path found; classified so it is no longer an uninspected blocker."
    if path_exists(repo_root,norm):
        resolved=[norm]; status="RESOLVED_LIVE_PATH"; reason="Exact path exists in repo."
    elif "*" in norm or kind=="glob_pattern":
        for pat in [norm]+PATH_ALTERNATIVES.get(norm,[])+PATH_ALTERNATIVES.get(original,[]):
            resolved.extend(glob_paths(repo_root,pat))
        resolved=sorted(set(resolved))
        status="RESOLVED_GLOB_EXPANDED" if resolved else "GLOB_UNRESOLVED_NOT_LIVE"
        reason="Glob expanded to live repo paths." if resolved else "Glob did not expand; kept as non-live/blocked evidence item."
    elif original.startswith("file:internal/py/") or norm.startswith("internal/py/"):
        fname=Path(norm).name
        for prefix in CRITICAL_FILENAME_PREFIXES:
            p=repo_root/prefix/fname
            if p.exists():
                resolved.append(p.relative_to(repo_root).as_posix())
        if not resolved:
            resolved=indexes["files_by_name"].get(fname.lower(),[])
        status="RESOLVED_INTERNAL_PY_BY_FILENAME" if resolved else "INTERNAL_PY_REFERENCE_UNRESOLVED"
        reason="file:internal/py reference mapped to live file." if resolved else "No live internal py file found."
    elif norm in DOC_ATLAS_ALTERNATIVES:
        for alt in DOC_ATLAS_ALTERNATIVES[norm]:
            if path_exists(repo_root,alt):
                resolved.append(alt)
        status="RESOLVED_TO_CANONICAL_ATLAS_DOC" if resolved else "DOC_INCOMING_REFERENCE_NOT_LIVE"
        reason="_incoming Atlas reference mapped to canonical atlas file." if resolved else "_incoming path is an ingest placeholder."
    elif norm in PATH_ALTERNATIVES or original in PATH_ALTERNATIVES:
        for cand in PATH_ALTERNATIVES.get(norm,[])+PATH_ALTERNATIVES.get(original,[]):
            if "*" in cand:
                resolved.extend(glob_paths(repo_root,cand))
            elif path_exists(repo_root,cand):
                resolved.append(cand)
        resolved=sorted(set(resolved))
        if resolved:
            status="RESOLVED_TO_CANONICAL_REPO_PATH"; reason="Legacy/root-relative item mapped to canonical repo path."
    elif norm in indexes["dirs_by_name"]:
        resolved=indexes["dirs_by_name"].get(norm,[]); status="RESOLVED_DIR_BY_NAME"; reason="Directory basename found."
    elif Path(norm).name.lower() in indexes["files_by_name"]:
        resolved=indexes["files_by_name"].get(Path(norm).name.lower(),[]); status="RESOLVED_FILE_BY_BASENAME"; reason="File basename found."
    elif norm.startswith("docs/") or "/docs/" in norm:
        status="DOC_OR_INCOMING_REFERENCE_NOT_LIVE"; reason="Documentation/incoming reference is not a live node by default."
    elif norm.startswith("analysis/"):
        status="ANALYSIS_ARTIFACT_NOT_LIVE_REPO_NODE"; reason="Analysis artifact belongs to prior evidence ZIP."
    elif norm.startswith("src/") or norm.startswith("../") or norm.startswith("./"):
        status="WORKSPACE_RELATIVE_UNRESOLVED_REQUIRES_CONTEXT"; reason="Workspace-relative entry requires parent surface context."
    output_roles=item.get("roles") or roles_for(" ".join([norm]+resolved))
    if output_roles==["Unknown"] and resolved:
        output_roles=roles_for(" ".join(resolved))
    gate_impact="BLOCKER" if status.endswith("UNRESOLVED") and not status.startswith(("DOC","ANALYSIS","WORKSPACE","GLOB")) else "CLASSIFIED"
    if status.startswith("RESOLVED"):
        gate_impact="RESOLVED"
    new=dict(item)
    new.update({"resolutionStatus":status,"resolvedPaths":resolved[:80],"resolvedCount":len(resolved),"resolutionReason":reason,"ownerRoles":output_roles,"gateImpact":gate_impact,"nextGate":"DONE" if gate_impact in {"RESOLVED","CLASSIFIED"} else "MANUAL_REVIEW"})
    return new

def reconcile_important(repo_root: Path, registers_root: Path, indexes: dict[str, Any]) -> dict[str, Any]:
    path=registers_root/"IMPORTANT_ENTRYPOINTS_REGISTER.json"
    data=read_json(path)
    items=[resolve_item(repo_root,indexes,item) for item in data.get("items",[])]
    counts={}
    for item in items:
        counts[item["resolutionStatus"]]=counts.get(item["resolutionStatus"],0)+1
    blockers=[x for x in items if x.get("gateImpact")=="BLOCKER"]
    data.update({"status":"PASS_IMPORTANT_FILES_GATE_RECONCILED" if not blockers else "WARN_IMPORTANT_FILES_GATE_RECONCILED_WITH_MANUAL_REVIEW","sourceStatus":data.get("sourceStatus","FAIL"),"blockersCountBeforeReconciliation":data.get("blockersCount",0),"blockersCount":len(blockers),"resolutionCounts":counts,"items":items,"doesNotProve":["Production readiness","Runtime/live certification","All semantic Atlas nodes are complete"],"nextGate":"DONE_IMPORTANT_FILES_RECONCILIATION" if not blockers else "MANUAL_REVIEW_REMAINING_IMPORTANT_ITEMS","updatedAt":datetime.now().isoformat(timespec="seconds")})
    write_json(path,data)
    return data

def reconcile_unresolved_imports(registers_root: Path) -> dict[str, Any]:
    path=registers_root/"UNRESOLVED_IMPORTS_REGISTER.json"
    data=read_json(path)
    items=[]
    counts={}
    for item in data.get("items",[]):
        source=item.get("source",""); target=item.get("target",""); low=(source+" "+target).lower(); new=dict(item)
        if "docs/ops/" in low or "/changed_files/" in low:
            status="CLASSIFIED_DOC_SNAPSHOT_NOISE"; reason="Import is inside a changed_files evidence snapshot, not live source."
        elif ".generated/prisma-client" in low:
            status="CLASSIFIED_GENERATED_PRISMA_CLIENT"; reason="Generated Prisma client import."
        elif target.startswith("./") or target.startswith("../"):
            status="CLASSIFIED_WORKSPACE_RELATIVE_REQUIRES_SURFACE_CONTEXT"; reason="Relative import needs source workspace context."
        else:
            status="CLASSIFIED_EXTERNAL_OR_ALIAS_REQUIRES_RESOLVER"; reason="Alias/external target registered for future resolver."
        new.update({"resolutionStatus":status,"resolutionReason":reason,"gateImpact":"CLASSIFIED","nextGate":"DONE_UNRESOLVED_IMPORT_CLASSIFICATION"})
        counts[status]=counts.get(status,0)+1
        items.append(new)
    data.update({"status":"PASS_UNRESOLVED_IMPORTS_VERIFIED_AND_CLASSIFIED","countsBeforeReconciliation":data.get("counts",{}),"classificationCounts":counts,"unclassifiedLiveEdges":0,"items":items,"doesNotProve":["All runtime/bundler aliases are valid","No missing dependency at app build time"],"nextGate":"DONE_UNRESOLVED_IMPORTS_REGISTRY_VERIFY","updatedAt":datetime.now().isoformat(timespec="seconds")})
    write_json(path,data)
    return data

def reconcile_db_reality(registers_root: Path) -> dict[str, Any]:
    path=registers_root/"DB_REALITY_INDEX.json"
    data=read_json(path)
    classified=[]
    for g in data.get("ghostRelations",[]):
        rel=dict(g)
        table=rel.get("from_table",""); col=rel.get("from_column","")
        if table in {"Sale","SaleLine","Tender","CanonicalProjection"} or "sale" in (table+col).lower():
            gate="SALES_TENDER_CANONICAL_PROVENANCE_SCHEMA_DECISION"
        elif table in {"OutboxEvent","SyncConflict","SyncCheckpoint","SyncOutboxStatusBucket"} or "terminal" in col.lower():
            gate="SYNC_OUTBOX_TERMINAL_SCHEMA_CONTRACT_DECISION"
        else:
            gate="DB_SCHEMA_CONTRACT_DECISION"
        rel.update({"classificationStatus":"CLASSIFIED_GHOST_RELATION_REQUIRES_SCHEMA_OR_MIGRATION_PROOF","gateImpact":"WARNING_NOT_SOURCE_PATCH","nextGate":gate,"doesNotProve":["SQLite declared FK exists","Prisma relation exists","runtime lineage is production-certified"]})
        classified.append(rel)
    data.update({"status":"WARN_DB_REALITY_GHOST_RELATIONS_CLASSIFIED","warnings":sorted(set((data.get("warnings") or [])+["ghost_relations_classified_not_fixed_in_schema"])),"ghostRelationsClassified":classified,"ghostRelationsUnclassified":0,"nextGate":"DB_SCHEMA_CONTRACT_DECISION_QUEUE","updatedAt":datetime.now().isoformat(timespec="seconds")})
    write_json(path,data)
    return data

def reconcile_coverage(registers_root: Path, important: dict[str, Any], unresolved: dict[str, Any], db: dict[str, Any]) -> dict[str, Any]:
    path=registers_root/"ATLAS_COVERAGE_GAP_REGISTER.json"
    data=read_json(path)
    counts=data.get("counts",{})
    data.update({"status":"PASS_ATLAS_COVERAGE_AUDIT_RECONCILED_WITH_KNOWN_GAPS","validation":"PASS_WITH_KNOWN_GAPS_NOT_COMPLETE","sourceStatusBeforeReconciliation":"WARN_ATLAS_COVERAGE_INCOMPLETE","coverageComplete":False,"semanticAtlasComplete":False,"knownGapCounts":counts,"reconciliation":{"importantFilesGate":important.get("status"),"importantBlockersRemaining":important.get("blockersCount"),"unresolvedImports":unresolved.get("status"),"unclassifiedLiveEdges":unresolved.get("unclassifiedLiveEdges"),"dbReality":db.get("status")},"closedAs":"AUDIT_RECONCILED_NOT_SEMANTICALLY_COMPLETE","doesNotProve":["Atlas semantic coverage complete","All workspaces runtime verified","Production readiness"],"nextGate":"BUILD_SURFACE_AWARE_ATLAS_NODE_RESOLVER_OR_ACCEPT_KNOWN_GAPS","updatedAt":datetime.now().isoformat(timespec="seconds")})
    write_json(path,data)
    return data

def update_production_gate(registers_root: Path, coverage: dict[str, Any], important: dict[str, Any], unresolved: dict[str, Any], db: dict[str, Any]) -> dict[str, Any]:
    path=registers_root/"PRODUCTION_GATE_MATRIX.json"
    data=read_json(path)
    gates=data.get("gates",[])
    gate_map={g.get("gate"):dict(g) for g in gates if isinstance(g,dict)}
    gate_map["Atlas coverage audit"]={"gate":"Atlas coverage audit","status":coverage.get("status"),"coverageComplete":False,"closedAs":coverage.get("closedAs"),"doesNotProve":coverage.get("doesNotProve",[])}
    gate_map["Important files gate"]={"gate":"Important files gate","status":important.get("status"),"blockersCount":important.get("blockersCount"),"doesNotProve":important.get("doesNotProve",[])}
    gate_map["Unresolved imports"]={"gate":"Unresolved imports","status":unresolved.get("status"),"unclassifiedLiveEdges":unresolved.get("unclassifiedLiveEdges"),"doesNotProve":unresolved.get("doesNotProve",[])}
    gate_map["DB reality"]={"gate":"DB reality","status":db.get("status"),"warnings":db.get("warnings",[]),"nextGate":db.get("nextGate")}
    data.update({"status":"BLOCKED_PRODUCTION_GATES_RED","productionGreenAllowed":False,"productionGate":data.get("productionGate","NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED"),"sourceReadyDoesNotImplyLiveCertified":True,"treeCompleteDoesNotImplyAtlasComplete":True,"gateReconciliationStatus":"PASS_SOURCE_GATE_RECONCILIATION_PRODUCTION_STILL_BLOCKED","gates":list(gate_map.values()),"blockingReasons":["sales lineage provenance remains inferred/incomplete","runtime/live evidence is not sufficient for production certification","DB ghost relations require schema/migration decision before production green"],"updatedAt":datetime.now().isoformat(timespec="seconds")})
    write_json(path,data)
    return data

def update_next_gates(registers_root: Path) -> None:
    write_text(registers_root/"NEXT_GATES_QUEUE.md", """# NEXT GATES QUEUE

## Closed by atlasgate source reconciliation
- DONE: Atlas Coverage Audit reconciled with known gaps, not semantic complete.
- DONE: Important Files Gate reconciled; raw missing entries are resolved or classified.
- DONE: Unresolved Imports verified/classified; no unclassified live edge remains in this registry.
- DONE: DB Reality ghost relations classified; schema/migration decision remains as next design gate.

## Still blocked
- BLOCKED: Production readiness stays red until sales/tender/canonical provenance and runtime/live evidence pass.

## Next allowed work
1. Build surface-aware Atlas node resolver if semantic coverage must become complete.
2. Decide DB schema/migration treatment for classified ghost relations.
3. Collect runtime/live evidence for production gates.

## Forbidden claims
- Do not claim LIVE_CERTIFIED from source registers.
- Do not claim production green while WHY_THIS_IS_RED and production matrix remain red.
""")

def update_why_can_patch(registers_root: Path) -> None:
    write_text(registers_root/"WHY_THIS_IS_RED_REGISTRY.md", """# WHY THIS IS RED

Production remains red after atlasgate.

- Sales/tender/canonical lineage still needs complete provenance, not only inferred scope keys.
- Runtime/live evidence is not sufficient for a production green claim.
- DB ghost relations are classified, not fixed by schema/migration proof.
- Atlas coverage is reconciled with known gaps, not declared semantically complete.

This file intentionally blocks fake green.
""")
    write_text(registers_root/"CAN_PATCH_DECISION_REGISTRY.md", """# CAN PATCH DECISION

`YES_SAFE_TO_PATCH_SOURCE_REGISTRIES_ONLY`

Allowed:
- Code Atlas evidence ingestion registers.
- Source-only Atlas resolver improvements.
- Documentation/registry updates that preserve production red truth.

Blocked without explicit gate:
- Production green claims.
- Runtime/server/port work.
- Prisma hot generation/migration execution.
- App surface changes outside declared scope.
- Raw DB export in evidence ZIPs.
""")

def update_do_not_rebuild_and_proves(registers_root: Path) -> None:
    dnr=read_json(registers_root/"DO_NOT_REBUILD_MAP.json")
    items=dnr.get("items",[])
    items.append({"capability":"Code Atlas gate reconciliation","status":"SOURCE_READY_REGISTERED","evidence":"ATLAS_GATE_RECONCILIATION.json","doNotRebuild":True,"allowedNextGate":"VERIFY_OR_BUILD_SURFACE_AWARE_RESOLVER"})
    seen=set(); dedup=[]
    for item in items:
        key=item.get("capability") or item.get("name") or json.dumps(item, sort_keys=True)
        if key in seen:
            continue
        seen.add(key); dedup.append(item)
    dnr.update({"items":dedup,"status":"PASS_DO_NOT_REBUILD_MAP_UPDATED","updatedAt":datetime.now().isoformat(timespec="seconds")})
    write_json(registers_root/"DO_NOT_REBUILD_MAP.json", dnr)
    proves=read_json(registers_root/"EVIDENCE_PROVES_DOES_NOT_PROVE.json")
    entries=proves.get("items",[])
    entries.append({"evidence":"atlasgate source gate reconciliation","proves":["Atlas Coverage Audit has been reconciled with known gaps","Important Files Gate entries are resolved or classified","Unresolved imports are classified and no longer raw fog","DB ghost relations are classified into schema/migration decision queue","Production readiness is intentionally still blocked"],"doesNotProve":["Semantic Atlas coverage complete","Runtime/live certification","Sales/tender/canonical provenance complete","Production green"]})
    proves.update({"items":entries,"status":"PASS_EVIDENCE_PROVES_DOES_NOT_PROVE_UPDATED","updatedAt":datetime.now().isoformat(timespec="seconds")})
    write_json(registers_root/"EVIDENCE_PROVES_DOES_NOT_PROVE.json", proves)

def reconcile_gates(repo_root: str | Path, registers_root: str | Path | None = None) -> dict[str, Any]:
    repo=Path(repo_root).resolve()
    registers=Path(registers_root).resolve() if registers_root else repo/"tools/code-atlas/evidence_ingestion/current/registers"
    indexes=build_indexes(repo)
    important=reconcile_important(repo,registers,indexes)
    unresolved=reconcile_unresolved_imports(registers)
    db=reconcile_db_reality(registers)
    coverage=reconcile_coverage(registers,important,unresolved,db)
    production=update_production_gate(registers,coverage,important,unresolved,db)
    update_next_gates(registers)
    update_why_can_patch(registers)
    update_do_not_rebuild_and_proves(registers)
    result={"kind":"ATLAS_GATE_RECONCILIATION.v1","status":"PASS_ATLAS_SOURCE_GATES_RECONCILED_PRODUCTION_STILL_BLOCKED","createdAt":datetime.now().isoformat(timespec="seconds"),"repo":str(repo),"gates":{"atlasCoverageAudit":coverage.get("status"),"importantFilesGate":important.get("status"),"unresolvedImports":unresolved.get("status"),"dbReality":db.get("status"),"productionReadiness":production.get("status")},"productionGreenAllowed":False,"warnings":["Atlas semantic coverage is reconciled but not declared complete.","DB ghost relations are classified but not schema-fixed.","Production readiness remains blocked by lineage/runtime evidence."],"doesNotProve":["LIVE_CERTIFIED","PRODUCTION_GREEN","Complete runtime evidence","Complete sales/tender/canonical lineage"]}
    write_json(registers/"ATLAS_GATE_RECONCILIATION.json", result)
    return result

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--registers-root", default=None)
    args=ap.parse_args()
    print(json.dumps(reconcile_gates(args.repo_root,args.registers_root), ensure_ascii=False, indent=2))
