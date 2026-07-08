from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_OUT = Path(r"F:\descargasf")
APP_NAMES = ["03_TABLET", "04_PC", "05_APP_MOVIL"]


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _stamp() -> str:
    return datetime.now().strftime("%d%m %H%M%S")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")


def _write_json(path: Path, obj: Any) -> None:
    _write_text(path, json.dumps(obj, ensure_ascii=False, indent=2))


def _sha(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _zip_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        dst.unlink()
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(src).as_posix())


def _latest_appbrain_zip(out_root: Path) -> Path | None:
    patterns = ["appbrain1*result.zip", "appbrain1%20*result.zip", "*appbrain1*result.zip"]
    found: list[Path] = []
    for pat in patterns:
        found.extend(p for p in out_root.glob(pat) if p.is_file())
    if not found:
        return None
    return max(found, key=lambda p: p.stat().st_mtime)


def _read_zip_json(z: zipfile.ZipFile, suffix: str) -> Any | None:
    wanted = suffix.replace("\\", "/")
    for name in z.namelist():
        if name.replace("\\", "/").endswith(wanted):
            return json.loads(z.read(name).decode("utf-8", errors="replace"))
    return None


def _list_app_files(z: zipfile.ZipFile, app: str) -> list[str]:
    prefix = f"apps/{app}/"
    return sorted(n for n in z.namelist() if n.replace("\\", "/").startswith(prefix))


def _extract_counts_from_master(master: Any) -> dict[str, Any]:
    if not isinstance(master, dict):
        return {}
    counts: dict[str, Any] = {}
    for key in ("counts", "summary", "stats", "totals"):
        val = master.get(key)
        if isinstance(val, dict):
            counts.update(val)
    for key in ("filesScanned", "targets", "confirmedRuntimeTargets", "routes", "components", "batches"):
        if key in master and key not in counts:
            counts[key] = master[key]
    return counts


def _items_from(obj: Any, *keys: str) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        for k in keys:
            v = obj.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
        values = [v for v in obj.values() if isinstance(v, dict)]
        if values and len(values) <= 5000:
            return values
    return []




def _count_like(value: Any) -> int:
    """Return a safe count for scalar, list, dict, and numeric-string values.

    AppBrain batch fields can arrive either as counts (``targets: 37``) or as
    collections (``targets: [...]``). Treating collections as ``int(...)`` breaks
    the workbench on real appbrain1 outputs, so this helper normalizes both.
    """
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return 0
        try:
            return int(float(text))
        except ValueError:
            return 1
    if isinstance(value, (list, tuple, set)):
        return len(value)
    if isinstance(value, dict):
        for key in ("count", "total", "length", "size", "targetCount", "fileCount", "targets", "files", "items", "entries"):
            if key in value:
                nested = _count_like(value.get(key))
                if nested or value.get(key) is not None:
                    return nested
        return len(value)
    return 0


def _batch_count(batch: dict[str, Any], *keys: str) -> int:
    for key in keys:
        if key in batch:
            value = batch.get(key)
            count = _count_like(value)
            if count or value not in (None, "", [], {}):
                return count
    return 0



def _raw_files_from_batch(batch: dict[str, Any]) -> list[str]:
    """Return raw file strings from common batch shapes."""
    for key in ("files", "sourceFiles", "filePaths", "paths", "items"):
        value = batch.get(key)
        if isinstance(value, list):
            files = []
            for item in value:
                if isinstance(item, str):
                    files.append(item)
                elif isinstance(item, dict):
                    candidate = item.get("file") or item.get("path") or item.get("sourceFile")
                    if candidate:
                        files.append(str(candidate))
            if files:
                return files
        if isinstance(value, str):
            return [value]
    return []


def _source_path(raw: str) -> str:
    """Normalize AppBrain zip/member references into repo-ish paths."""
    text = str(raw).replace("\\", "/")
    if "!/source/" in text:
        text = text.split("!/source/", 1)[1]
    elif "!/" in text:
        text = text.split("!/", 1)[1]
    if text.startswith("source/"):
        text = text[len("source/"):]
    return text.strip("/")


def _file_ext(path: str) -> str:
    return Path(path).suffix.lower()


def _looks_generated_or_vendor(path: str) -> bool:
    p = path.lower().replace("\\", "/")
    blocked_parts = [
        "/.generated/",
        "/generated/",
        "/node_modules/",
        "/.next/",
        "/dist/",
        "/build/",
        "/coverage/",
        "/.turbo/",
        "/.prisma/",
        "/prisma-client/",
    ]
    return any(part in p for part in blocked_parts)


def _is_api_or_logic_file(path: str) -> bool:
    p = path.lower().replace("\\", "/")
    logic_needles = [
        "/api/",
        "/server/",
        "/db/",
        "/prisma/",
        "/worker",
        "/migrations/",
        "/scripts/",
        "/lib/api",
        "/lib/server",
        "/repositories/",
        "/services/",
        "/route.ts",
        "/route.js",
        ".spec.",
        ".test.",
    ]
    return any(n in p for n in logic_needles)


def _is_runtime_ui_file(path: str) -> bool:
    p = path.lower().replace("\\", "/")
    ext = _file_ext(p)
    if ext not in {".tsx", ".jsx"}:
        return False
    if _looks_generated_or_vendor(p):
        return False
    if _is_api_or_logic_file(p):
        return False
    return True


def _is_style_file(path: str) -> bool:
    return _file_ext(path) in {".css", ".scss", ".sass", ".less"}


def _classify_batch_files(batch: dict[str, Any]) -> dict[str, Any]:
    raw_files = _raw_files_from_batch(batch)
    seen: set[str] = set()
    patchable: list[str] = []
    blocked_api_logic: list[str] = []
    blocked_styles: list[str] = []
    blocked_non_ui: list[str] = []
    blocked_generated: list[str] = []
    normalized: list[str] = []

    for raw in raw_files:
        path = _source_path(raw)
        if not path or path.lower() in seen:
            continue
        seen.add(path.lower())
        normalized.append(path)
        if _looks_generated_or_vendor(path):
            blocked_generated.append(path)
        elif _is_style_file(path):
            blocked_styles.append(path)
        elif _is_api_or_logic_file(path):
            blocked_api_logic.append(path)
        elif _is_runtime_ui_file(path):
            patchable.append(path)
        else:
            blocked_non_ui.append(path)

    return {
        "rawFilesCount": len(raw_files),
        "normalizedFilesCount": len(normalized),
        "patchableRuntimeUiFiles": patchable,
        "patchableRuntimeUiFileCount": len(patchable),
        "blockedApiOrLogicFiles": blocked_api_logic,
        "blockedApiOrLogicFileCount": len(blocked_api_logic),
        "blockedStyleFiles": blocked_styles,
        "blockedStyleFileCount": len(blocked_styles),
        "blockedGeneratedOrVendorFiles": blocked_generated,
        "blockedGeneratedOrVendorFileCount": len(blocked_generated),
        "blockedNonUiFiles": blocked_non_ui,
        "blockedNonUiFileCount": len(blocked_non_ui),
        "hasPatchableRuntimeUi": bool(patchable),
        "uiRuntimeOnlyPolicy": "Only .tsx/.jsx runtime UI files may be touched by instrumentation packages. API routes, logic .ts, styles, generated/vendor, package/lockfiles are evidence only.",
    }


def _enrich_batch_for_patchability(batch: dict[str, Any]) -> dict[str, Any]:
    x = dict(batch)
    file_summary = _classify_batch_files(x)
    x["fileSummary"] = file_summary
    x["targetPatchFiles"] = file_summary["patchableRuntimeUiFiles"]
    x["blockedEvidenceFiles"] = {
        "apiOrLogic": file_summary["blockedApiOrLogicFiles"],
        "styles": file_summary["blockedStyleFiles"],
        "generatedOrVendor": file_summary["blockedGeneratedOrVendorFiles"],
        "nonUi": file_summary["blockedNonUiFiles"],
    }
    x["patchFilePolicy"] = file_summary["uiRuntimeOnlyPolicy"]
    if not file_summary["hasPatchableRuntimeUi"]:
        x["patchReadiness"] = "BLOCKED_NO_RUNTIME_UI_FILES"
        x["allowedPatchType"] = "analysis_only"
    else:
        x["patchReadiness"] = "READY_FOR_INSTRUMENTATION_ONLY"
        x["allowedPatchType"] = "instrumentation_only"
    return x



def _risk_from_batch(batch: dict[str, Any]) -> str:
    raw = str(batch.get("risk") or batch.get("riskLevel") or batch.get("level") or "").lower()
    if raw:
        return raw
    targets = _batch_count(batch, "targets", "targetCount")
    files = _batch_count(batch, "files", "fileCount")
    if files > 70 or targets > 250:
        return "review"
    if files > 25 or targets > 100:
        return "medium_high"
    if files > 8 or targets > 30:
        return "medium"
    return "low"


def _priority_score(app: str, batch: dict[str, Any]) -> int:
    text = json.dumps(batch, ensure_ascii=False).lower()
    file_summary = _classify_batch_files(batch)
    patchable_count = file_summary["patchableRuntimeUiFileCount"]
    blocked_logic_count = file_summary["blockedApiOrLogicFileCount"]
    blocked_style_count = file_summary["blockedStyleFileCount"]

    score = 0
    if app == "03_TABLET":
        score += 500
    if "revenue" in text or "pos" in text or "checkout" in text or "sales" in text:
        score += 900
    if "license" in text or "licencia" in text:
        score += 450
    if "mobile" in text or "companion" in text:
        score += 350
    if "pc" in text or "dashboard" in text:
        score += 260

    score += min(350, _batch_count(batch, "targets", "targetCount"))
    score += min(220, patchable_count * 6)

    if patchable_count == 0:
        score -= 900
    if blocked_logic_count > 0:
        score -= min(220, blocked_logic_count * 3)
    if blocked_style_count > 0:
        score -= min(150, blocked_style_count * 5)

    risk = _risk_from_batch(batch)
    if "high" in risk or "review" in risk:
        score -= 120
    return score



def _summarize_app(z: zipfile.ZipFile, app: str) -> dict[str, Any]:
    master = _read_zip_json(z, f"apps/{app}/APP_MASTER_SURFACE_MAP.json") or {}
    semantic = _read_zip_json(z, f"apps/{app}/APP_SEMANTIC_GROUPS.json") or {}
    batches = _read_zip_json(z, f"apps/{app}/APP_INSTRUMENTATION_BATCHES.json") or {}
    next_actions_md = None
    for name in z.namelist():
        if name.replace("\\", "/").endswith(f"apps/{app}/APP_NEXT_BEST_ACTIONS.md"):
            next_actions_md = z.read(name).decode("utf-8", errors="replace")
            break
    batch_items = _items_from(batches, "batches", "items", "actions")
    semantic_items = _items_from(semantic, "groups", "items")
    counts = _extract_counts_from_master(master)
    if not counts:
        counts = {"zipFiles": len(_list_app_files(z, app)), "semanticGroups": len(semantic_items), "batches": len(batch_items)}
    ranked_batches = []
    for idx, b in enumerate(batch_items):
        x = _enrich_batch_for_patchability(b)
        x.setdefault("app", app)
        x.setdefault("batchIndex", idx)
        x["risk"] = _risk_from_batch(x)
        x["priorityScore"] = _priority_score(app, x)
        ranked_batches.append(x)
    ranked_batches.sort(key=lambda x: x.get("priorityScore", 0), reverse=True)
    return {
        "app": app,
        "counts": counts,
        "semanticGroupsCount": len(semantic_items),
        "instrumentationBatchesCount": len(batch_items),
        "topBatches": ranked_batches[:20],
        "nextActionsPreview": (next_actions_md or "")[:5000],
        "sourceFilesInZip": len(_list_app_files(z, app)),
    }


def _build_cross_app(apps: list[dict[str, Any]]) -> dict[str, Any]:
    all_batches = []
    for app in apps:
        all_batches.extend(app.get("topBatches") or [])
    all_batches.sort(key=lambda x: x.get("priorityScore", 0), reverse=True)
    risk_counts = Counter(str(b.get("risk", "unknown")) for b in all_batches)
    return {
        "generatedAt": _now(),
        "recommendedOrder": all_batches[:50],
        "riskCounts": dict(risk_counts),
        "appOrder": [a["app"] for a in sorted(apps, key=lambda a: sum(b.get("priorityScore", 0) for b in a.get("topBatches", [])[:5]), reverse=True)],
    }


def _build_mesh_requests(cross: dict[str, Any]) -> list[dict[str, Any]]:
    requests = []
    for i, batch in enumerate(cross.get("recommendedOrder", [])[:25], start=1):
        enriched = _enrich_batch_for_patchability(batch)
        app = enriched.get("app", "unknown")
        group = enriched.get("semanticGroup") or enriched.get("group") or enriched.get("screen") or enriched.get("screenId") or "unknown_group"
        patchable_files = enriched.get("targetPatchFiles") or []
        allowed_patch_type = "instrumentation_only" if patchable_files else "analysis_only"
        requests.append({
            "rank": i,
            "app": app,
            "batch": group,
            "recommendedMeshName": f"mesh-{app.lower().replace('_','-')}-{str(group).lower().replace(' ', '-').replace('_','-')}",
            "allowedPatchType": allowed_patch_type,
            "patchReadiness": enriched.get("patchReadiness"),
            "requiresRollback": allowed_patch_type == "instrumentation_only",
            "requiresHashGate": allowed_patch_type == "instrumentation_only",
            "targetPatchFiles": patchable_files,
            "targetPatchFileCount": len(patchable_files),
            "blockedEvidenceFiles": enriched.get("blockedEvidenceFiles"),
            "patchFilePolicy": enriched.get("patchFilePolicy"),
            "forbidden": ["visual CSS", "business logic", "API routes", "logic .ts files", "Prisma", "Git writes", "package/lockfiles", "process/port/dev-server operations", "!important"],
            "priorityScore": enriched.get("priorityScore"),
            "risk": enriched.get("risk"),
            "sourceBatch": enriched,
        })
    return requests


def _build_patchable_batches(app_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    by_app: dict[str, list[dict[str, Any]]] = {}
    blocked: list[dict[str, Any]] = []
    for app in app_summaries:
        app_id = app.get("app", "unknown")
        patchable_items: list[dict[str, Any]] = []
        for batch in app.get("topBatches", []):
            enriched = _enrich_batch_for_patchability(batch)
            if enriched.get("targetPatchFiles"):
                patchable_items.append({
                    "app": app_id,
                    "batch": enriched.get("semanticGroup") or enriched.get("screenId") or enriched.get("group") or "unknown_group",
                    "batchId": enriched.get("batchId"),
                    "screenId": enriched.get("screenId"),
                    "screenLabel": enriched.get("screenLabel"),
                    "risk": enriched.get("risk"),
                    "priorityScore": enriched.get("priorityScore"),
                    "targetPatchFiles": enriched.get("targetPatchFiles"),
                    "targetPatchFileCount": len(enriched.get("targetPatchFiles") or []),
                    "blockedEvidenceFiles": enriched.get("blockedEvidenceFiles"),
                    "patchReadiness": enriched.get("patchReadiness"),
                    "patchFilePolicy": enriched.get("patchFilePolicy"),
                })
            else:
                blocked.append({
                    "app": app_id,
                    "batchId": enriched.get("batchId"),
                    "batch": enriched.get("semanticGroup") or enriched.get("screenId") or enriched.get("group") or "unknown_group",
                    "patchReadiness": enriched.get("patchReadiness"),
                    "fileSummary": enriched.get("fileSummary"),
                })
        patchable_items.sort(key=lambda x: x.get("priorityScore", 0), reverse=True)
        by_app[app_id] = patchable_items
    all_patchable = [x for xs in by_app.values() for x in xs]
    all_patchable.sort(key=lambda x: x.get("priorityScore", 0), reverse=True)
    return {
        "generatedAt": _now(),
        "policy": "Only .tsx/.jsx runtime UI files may be patch targets. API routes, logic .ts files, styles, generated/vendor, package/lockfiles are evidence only.",
        "apps": by_app,
        "recommendedPatchableOrder": all_patchable[:50],
        "blockedNoRuntimeUiFiles": blocked[:200],
        "counts": {
            "patchableBatches": len(all_patchable),
            "blockedNoRuntimeUiBatches": len(blocked),
            "patchableFilesTotal": sum(len(x.get("targetPatchFiles") or []) for x in all_patchable),
        },
    }


def run_workbench(source_zip: Path | None = None, out_root: Path = DEFAULT_OUT, repo_root: Path = Path(r"F:\repos\hitech-os"), label: str = "appbrain-workbench", output_zip: Path | None = None) -> Path:
    out_root.mkdir(parents=True, exist_ok=True)
    source = source_zip or _latest_appbrain_zip(out_root)
    if source is None or not source.exists():
        raise FileNotFoundError(f"No encontré appbrain1 ... result.zip en {out_root}")
    stamp = _stamp()
    work = out_root / f"{label} {stamp} staging"
    if output_zip is None:
        output_zip = out_root / f"{label} {stamp} result.zip"
    if work.exists():
        shutil.rmtree(work)
    (work / "reports").mkdir(parents=True, exist_ok=True)
    (work / "source").mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(source, "r") as z:
        listing = sorted(z.namelist())
        validation = _read_zip_json(z, "reports/validation.json") or {}
        app_index = _read_zip_json(z, "global/APP_BRAIN_INDEX.json") or {}
        cross_alignment = _read_zip_json(z, "global/CROSS_APP_ALIGNMENT_MATRIX.json") or {}
        app_summaries = [_summarize_app(z, app) for app in APP_NAMES]
        cross = _build_cross_app(app_summaries)
        mesh_requests = _build_mesh_requests(cross)
        shutil.copy2(source, work / "source" / source.name)
        _write_text(work / "reports" / "source_zip_listing.txt", "\n".join(listing))

    source_index = {
        "sourceZip": str(source),
        "sourceSha256": _sha(source),
        "validationStatus": validation.get("status"),
        "appBrainIndexKeys": sorted(app_index.keys()) if isinstance(app_index, dict) else [],
        "crossAlignmentKeys": sorted(cross_alignment.keys()) if isinstance(cross_alignment, dict) else [],
    }
    dashboard = {
        "generatedAt": _now(),
        "source": source_index,
        "apps": app_summaries,
        "crossApp": cross,
        "workbenchModes": ["Discover", "Understand", "Decide", "Prepare"],
    }
    workbench = {
        "status": "PASS_APPBRAIN_WORKBENCH_GENERATED",
        "generatedAt": _now(),
        "readOnly": True,
        "authorizesPatch": False,
        "repoRoot": str(repo_root),
        "sourceZip": str(source),
        "sourceSha256": _sha(source),
        "dashboard": dashboard,
    }
    batch_explorer = {"generatedAt": _now(), "apps": {a["app"]: a.get("topBatches", []) for a in app_summaries}, "recommendedOrder": cross.get("recommendedOrder", [])}
    patchable_batches = _build_patchable_batches(app_summaries)
    next_plan = {
        "generatedAt": _now(),
        "recommendedNext": mesh_requests[0] if mesh_requests else None,
        "allMeshRequests": mesh_requests,
        "packageRules": {"mustGenerateAuthorityMeshFirst": True, "mustIncludeRollback": True, "mustUseHashGate": True, "visualPatchAllowed": False, "instrumentationOnlyFirst": True},
    }
    diff_readiness = {
        "generatedAt": _now(),
        "historyDetection": "Use two appbrain1 result ZIPs to compute target/batch deltas. This run imported a single source ZIP.",
        "readyForFutureDiff": True,
        "requiredInputsForDiff": ["previous appbrain1 result.zip", "current appbrain1 result.zip"],
    }
    import_summary = {
        "generatedAt": _now(),
        "sourceZip": str(source),
        "sourceStatus": validation.get("status"),
        "appsImported": [a["app"] for a in app_summaries],
        "totalSourceFilesInZip": sum(a.get("sourceFilesInZip", 0) for a in app_summaries),
        "topRecommendation": mesh_requests[0] if mesh_requests else None,
    }

    _write_json(work / "PRISMA_APPBRAIN_WORKBENCH.json", workbench)
    _write_json(work / "PRISMA_TRI_APP_DASHBOARD.json", dashboard)
    _write_json(work / "PRISMA_APPBRAIN_BATCH_EXPLORER.json", batch_explorer)
    _write_json(work / "PRISMA_APPBRAIN_PATCHABLE_BATCHES.json", patchable_batches)
    _write_json(work / "PRISMA_APPBRAIN_IMPORT_SUMMARY.json", import_summary)
    _write_json(work / "PRISMA_APPBRAIN_MESH_REQUESTS.json", mesh_requests)
    _write_json(work / "PRISMA_APPBRAIN_NEXT_PACKAGE_PLAN.json", next_plan)
    _write_json(work / "PRISMA_APPBRAIN_DIFF_READINESS.json", diff_readiness)
    _write_json(work / "PRISMA_APPBRAIN_SOURCE_INDEX.json", source_index)

    patch_md = ["# PRISMA AppBrain Patchable Batches", "", patchable_batches["policy"], "", "## Recommended patchable order"]
    for item in patchable_batches.get("recommendedPatchableOrder", [])[:25]:
        patch_md.append(f"- `{item.get('app')}` / `{item.get('batch')}` / files={item.get('targetPatchFileCount')} / risk `{item.get('risk')}` / readiness `{item.get('patchReadiness')}`")
    patch_md.extend(["", "## Blocked evidence-only batches"])
    for item in patchable_batches.get("blockedNoRuntimeUiFiles", [])[:50]:
        patch_md.append(f"- `{item.get('app')}` / `{item.get('batch')}` / `{item.get('patchReadiness')}`")
    _write_text(work / "PRISMA_APPBRAIN_PATCHABLE_BATCHES.md", "\n".join(patch_md) + "\n")

    md = ["# PRISMA AppBrain Workbench", "", f"Generated: {_now()}", "", f"Source: `{source}`", "", "## Apps"]
    for app in app_summaries:
        md.append(f"- **{app['app']}**: batches={app.get('instrumentationBatchesCount')}, groups={app.get('semanticGroupsCount')}, sourceZipFiles={app.get('sourceFilesInZip')}")
    md.extend(["", "## Recommended order"])
    for req in mesh_requests[:15]:
        md.append(f"{req['rank']}. `{req['app']}` / `{req['batch']}` / patch `{req['allowedPatchType']}` / uiFiles `{req.get('targetPatchFileCount', 0)}` / risk `{req['risk']}` / score `{req['priorityScore']}`")
    _write_text(work / "PRISMA_APPBRAIN_WORKBENCH.md", "\n".join(md) + "\n")

    req_md = ["# PRISMA AppBrain Mesh Requests", "", "These are read-only recommendations. They do not authorize a patch by themselves.", ""]
    for req in mesh_requests[:25]:
        req_md.extend([f"## {req['rank']}. {req['app']} / {req['batch']}", f"- Mesh name: `{req['recommendedMeshName']}`", f"- Patch type: `{req['allowedPatchType']}`", f"- Patchable UI files: `{req.get('targetPatchFileCount', 0)}`", f"- Risk: `{req['risk']}`", f"- Score: `{req['priorityScore']}`", ""])
    _write_text(work / "PRISMA_APPBRAIN_MESH_REQUESTS.md", "\n".join(req_md))

    plan_md = ["# PRISMA AppBrain Next Package Plan", "", "Recommended next action is to generate a fresh Authority Mesh for the selected batch, then build an instrumentation-only package.", ""]
    if mesh_requests:
        first = mesh_requests[0]
        plan_md.extend([f"Recommended first batch: `{first['app']}` / `{first['batch']}`", f"Risk: `{first['risk']}`", f"Patch type: `{first['allowedPatchType']}`", f"Patchable UI files: `{first.get('targetPatchFileCount', 0)}`", "Allowed patch files are targetPatchFiles only; API/logic/style files are evidence-only."])
    _write_text(work / "PRISMA_APPBRAIN_NEXT_PACKAGE_PLAN.md", "\n".join(plan_md) + "\n")

    summary = f"""# SUMMARY_FOR_CHAT

Status: PASS_APPBRAIN_WORKBENCH_GENERATED

Source: `{source}`

Apps imported: {', '.join(a['app'] for a in app_summaries)}

Recommended next batch: `{mesh_requests[0]['app'] if mesh_requests else 'none'}` / `{mesh_requests[0]['batch'] if mesh_requests else 'none'}`

Patchable UI files for that batch: `{mesh_requests[0].get('targetPatchFileCount', 0) if mesh_requests else 0}`

This workbench is read-only and does not authorize patches by itself.
"""
    _write_text(work / "SUMMARY_FOR_CHAT.md", summary)
    _write_text(work / "CONTINUATION.md", "# CONTINUATION\n\nUse this ZIP to choose an appbrain batch and generate a fresh mesh before any patch.\n")
    _write_json(work / "reports" / "validation.json", {"status": "PASS_APPBRAIN_WORKBENCH_GENERATED", "generatedAt": _now(), "readOnly": True, "authorizesPatch": False, "sourceZip": str(source), "sourceSha256": _sha(source), "appsImported": [a["app"] for a in app_summaries], "meshRequests": len(mesh_requests), "patchFilePolicy": patchable_batches.get("policy"), "patchableBatches": patchable_batches.get("counts", {}).get("patchableBatches"), "blockedNoRuntimeUiBatches": patchable_batches.get("counts", {}).get("blockedNoRuntimeUiBatches")})

    _zip_dir(work, output_zip)
    shutil.rmtree(work, ignore_errors=True)
    return output_zip


def run_self_test(out_root: Path, repo_root: Path) -> int:
    out_root.mkdir(parents=True, exist_ok=True)
    tmp = out_root / "appbrain_workbench_selftest"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    fake = tmp / "appbrain1 synthetic result.zip"
    with zipfile.ZipFile(fake, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("reports/validation.json", json.dumps({"status": "PASS_APPBRAIN1_TRI_APP_MASTER_MAP_GENERATED"}))
        z.writestr("global/APP_BRAIN_INDEX.json", json.dumps({"apps": APP_NAMES}))
        z.writestr("global/CROSS_APP_ALIGNMENT_MATRIX.json", json.dumps({"ok": True}))
        for app in APP_NAMES:
            z.writestr(f"apps/{app}/APP_MASTER_SURFACE_MAP.json", json.dumps({"counts": {"filesScanned": 1, "targets": 2, "confirmedRuntimeTargets": 1}}))
            z.writestr(f"apps/{app}/APP_SEMANTIC_GROUPS.json", json.dumps({"groups": [{"id": "revenue_core"}]}))
            z.writestr(f"apps/{app}/APP_INSTRUMENTATION_BATCHES.json", json.dumps({"batches": [{"semanticGroup": "revenue_core", "screen": "POS", "targets": [1,2,3], "files": ["source/products/tablet/app/components/pos/pos-screen.tsx", "source/products/tablet/app/app/api/pos/sales/today/route.ts"]}]}))
            z.writestr(f"apps/{app}/APP_NEXT_BEST_ACTIONS.md", "# Next\n")
    output_zip = tmp / "selftest result.zip"
    result = run_workbench(source_zip=fake, out_root=tmp, repo_root=repo_root, label="selftest", output_zip=output_zip)
    if not result.exists():
        raise RuntimeError("self-test did not produce result zip")
    with zipfile.ZipFile(result, "r") as z:
        required = ["PRISMA_APPBRAIN_WORKBENCH.json", "PRISMA_APPBRAIN_MESH_REQUESTS.json", "PRISMA_APPBRAIN_PATCHABLE_BATCHES.json", "reports/validation.json"]
        missing = [x for x in required if x not in z.namelist()]
        if missing:
            raise RuntimeError("self-test missing outputs: " + ", ".join(missing))
    shutil.rmtree(tmp, ignore_errors=True)
    print("PASS_APPBRAIN_WORKBENCH_SELF_TEST")
    return 0
