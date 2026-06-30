from __future__ import annotations

import hashlib
import json
import os
import re
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TEXT_EXTS = {".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".json", ".md", ".mjs", ".cjs", ".py", ".yml", ".yaml", ".ps1", ".txt"}
EXCLUDED_DIRS = {".git", "node_modules", ".next", "dist", "build", ".turbo", ".cache", "coverage", "__pycache__", ".prisma", "tmp", "temp", "vendor", "assets"}
SECRET_NAMES = {".env", ".env.local", ".env.production", ".env.development", "id_rsa", "id_ed25519"}
MAX_WORKERS = 18
MAX_FILES_PER_SURFACE = 35000
MAX_EVIDENCE_ZIPS = 48
MAX_SNIPPET = 3200


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _terminal_root() -> Path:
    # internal/py/prismo_app_live_context.py -> prisma-control-center -> terminal-de-venta-system
    return Path(__file__).resolve().parents[3]


def _hitech_root() -> Path:
    root = _terminal_root()
    try:
        # F:/repos/hitech-os/apps/terminal-de-venta-system -> F:/repos/hitech-os
        return root.parents[1]
    except Exception:
        return root


def _descargas_root() -> Path:
    return Path(os.environ.get("PRISMO_DESCARGASF") or r"F:\descargasf")


def _cache_root() -> Path:
    raw = os.environ.get("PRISMO_APP_LIVE_CACHE") or os.environ.get("PRISMO_LEARNING_STORE") or str(_descargas_root() / "PRISMO_LEARNING_STORE")
    return Path(raw)


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def _skip_dir(name: str) -> bool:
    return name in EXCLUDED_DIRS or name.startswith(".")


def _is_secretish(path: Path) -> bool:
    name = path.name.lower()
    if name in SECRET_NAMES:
        return True
    if name.endswith(".pem") or name.endswith(".key") or name.endswith(".pfx"):
        return True
    return False


def _iter_files(base: Path, limit: int = MAX_FILES_PER_SURFACE) -> list[Path]:
    if not base.exists():
        return []
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [name for name in dirnames if not _skip_dir(name)]
        for filename in filenames:
            path = Path(dirpath) / filename
            if _is_secretish(path):
                continue
            if path.suffix.lower() in TEXT_EXTS or path.name in {"package.json", "index.html", "AGENTS.md"}:
                out.append(path)
                if len(out) >= limit:
                    return out
    return out


def _read_text_light(path: Path, max_bytes: int = 180_000) -> str:
    try:
        if _is_secretish(path):
            return ""
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def _hash_light(path: Path) -> str | None:
    try:
        if path.stat().st_size > 1_500_000 or _is_secretish(path):
            return None
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(256 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def _route_from_app_file(rel: str) -> str | None:
    norm = rel.replace("\\", "/")
    m = re.search(r"products/([^/]+)/app/(.*)/(page|layout|route)\.(tsx|jsx|ts|js)$", norm)
    if not m:
        return None
    tail = m.group(2)
    parts = [p for p in tail.split("/") if p and not p.startswith("(")]
    clean = []
    for p in parts:
        if p.startswith("[") and p.endswith("]"):
            clean.append(":" + p.strip("[]"))
        else:
            clean.append(p)
    route = "/" + "/".join(clean)
    return route.replace("//", "/") or "/"


def _imports_sample(text: str, limit: int = 12) -> list[str]:
    imports: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append(stripped[:220])
            if len(imports) >= limit:
                break
    return imports


def _css_selectors_sample(text: str, limit: int = 48) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for match in re.finditer(r"([^{}@]+)\{([^{}]*)\}", text, flags=re.S):
        selector = " ".join(match.group(1).strip().split())[:220]
        body = match.group(2)
        if not selector:
            continue
        out.append({
            "selector": selector,
            "z_index": re.findall(r"z-index\s*:\s*([^;]+)", body, flags=re.I)[:4],
            "position": re.findall(r"position\s*:\s*([^;]+)", body, flags=re.I)[:2],
            "important_count": body.count("!important"),
            "backdrop_filter": bool(re.search(r"backdrop-filter|-webkit-backdrop-filter", body, flags=re.I)),
        })
        if len(out) >= limit:
            break
    return out


def _file_meta(path: Path, root: Path) -> dict[str, Any]:
    try:
        stat = path.stat()
        rel = _safe_rel(path, root)
        name = path.name.lower()
        text = ""
        suffix = path.suffix.lower()
        if suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".py"} and stat.st_size <= 450_000:
            text = _read_text_light(path)
        is_route = name in {"page.tsx", "page.jsx", "route.ts", "route.js", "layout.tsx", "layout.jsx"}
        return {
            "rel": rel,
            "size": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "suffix": suffix,
            "is_route": is_route,
            "route": _route_from_app_file(rel) if is_route else None,
            "is_component": "/component" in rel.lower() or "\\component" in rel.lower(),
            "is_css": suffix == ".css",
            "is_doc": suffix == ".md",
            "imports_sample": _imports_sample(text) if text and suffix in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py"} else [],
            "css_selectors_sample": _css_selectors_sample(text) if text and suffix == ".css" else [],
            "sha256": _hash_light(path),
        }
    except Exception as exc:
        return {"rel": _safe_rel(path, root), "error": str(exc)}


def _scan_surface(root: Path, surface_id: str, label: str, rel_path: str, limit: int = MAX_FILES_PER_SURFACE) -> dict[str, Any]:
    base = root / rel_path
    files = _iter_files(base, limit=limit)
    metas: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(_file_meta, path, root) for path in files]
        for future in as_completed(futures):
            metas.append(future.result())
    metas.sort(key=lambda item: item.get("rel", ""))
    routes = [item for item in metas if item.get("is_route")]
    components = [item for item in metas if item.get("is_component")]
    css = [item for item in metas if item.get("is_css")]
    docs = [item for item in metas if item.get("is_doc")]
    recent = sorted(metas, key=lambda item: item.get("mtime", ""), reverse=True)[:32]
    selectors: list[dict[str, Any]] = []
    important_count = 0
    for item in css[:80]:
        for selector in item.get("css_selectors_sample") or []:
            important_count += int(selector.get("important_count") or 0)
            if selector.get("z_index") or selector.get("backdrop_filter") or selector.get("important_count"):
                selectors.append({"file": item.get("rel"), **selector})
    return {
        "id": surface_id,
        "label": label,
        "path": rel_path,
        "exists": base.exists(),
        "file_count": len(metas),
        "route_count": len(routes),
        "component_count": len(components),
        "css_count": len(css),
        "doc_count": len(docs),
        "important_count_sampled": important_count,
        "routes_sample": routes[:120],
        "components_sample": components[:120],
        "css_sample": css[:120],
        "docs_sample": docs[:80],
        "layer_signals": selectors[:120],
        "recent_files": recent,
    }


def _authority_memory(root: Path) -> dict[str, Any]:
    files = [
        "docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md",
        "docs/ops/PRISMA_FIELD_MANUAL_AUTHORITY_MESH_APPENDIX.md",
        "docs/ops/PRISMA_FIELD_MANUAL_GOVMESH3_APPENDIX.md",
        "docs/ops/PRISMA_FIELD_MANUAL_VISUAL_CAPABILITY_RESOLVER_APPENDIX.md",
        ".governance/current/AUTHORITY_READSET.lock.json",
        ".governance/current/APP_IMPACT_MATRIX.md",
        ".governance/current/CONTRACT_AND_GATE_MATRIX.json",
        ".governance/current/MISSING_OR_UNMAPPED_RISK.md",
        ".governance/current/AGENT_PROMPT_ENVELOPE.md",
        ".governance/current/AUTHORITY_MESH_REPORT.md",
        "AGENTS.md",
    ]
    records = []
    for rel in files:
        p = root / rel
        rec: dict[str, Any] = {"rel": rel, "exists": p.exists()}
        if p.exists() and p.is_file():
            stat = p.stat()
            text = _read_text_light(p, max_bytes=MAX_SNIPPET)
            rec.update({
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "sha256": _hash_light(p),
                "snippet": text[:1400],
            })
        records.append(rec)
    return {
        "manual_found": any(r["rel"].endswith("APRENDIZAJE_OPERATIVO.md") and r.get("exists") for r in records),
        "readset_found": any(r["rel"].endswith("AUTHORITY_READSET.lock.json") and r.get("exists") for r in records),
        "records": records,
    }


def _evidence_library(descargas: Path) -> dict[str, Any]:
    if not descargas.exists():
        return {"exists": False, "zip_count": 0, "items": []}
    candidates = []
    for pattern in ["*result*.zip", "*fail*.zip", "*diagnostic*.zip", "*context*.zip", "*ctx*.zip"]:
        candidates.extend(descargas.glob(pattern))
    unique = sorted({p.resolve(): p for p in candidates if p.is_file()}.values(), key=lambda p: p.stat().st_mtime, reverse=True)[:MAX_EVIDENCE_ZIPS]
    items: list[dict[str, Any]] = []
    report_names = ("RESULT.md", "RESULT.json", "DRY_RUN_REPORT.md", "DRY_RUN_REPORT.json", "VALIDATION_RESULTS.json", "ERROR.txt", "CONTINUATION.md", "AUTHORITY_MESH_REPORT.md", "manifest.json")
    for p in unique:
        rec: dict[str, Any] = {
            "name": p.name,
            "path": str(p),
            "size": p.stat().st_size,
            "mtime": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
            "kind": "fail" if "fail" in p.name.lower() or "diagnostic" in p.name.lower() else "result" if "result" in p.name.lower() else "context",
            "reports": [],
            "entry_count": None,
        }
        try:
            with zipfile.ZipFile(p, "r") as z:
                names = z.namelist()
                rec["entry_count"] = len(names)
                wanted = [name for name in names if name.split("/")[-1] in report_names][:10]
                for name in wanted:
                    try:
                        raw = z.read(name, pwd=None)[:MAX_SNIPPET]
                        snippet = raw.decode("utf-8", errors="replace")
                    except Exception as exc:
                        snippet = f"[READ_ERROR] {type(exc).__name__}"
                    rec["reports"].append({"entry": name, "snippet": snippet[:1800]})
        except Exception as exc:
            rec["zip_error"] = type(exc).__name__
        items.append(rec)
    return {
        "exists": True,
        "zip_count": len(items),
        "items": items,
        "latest_result": next((item for item in items if item.get("kind") == "result"), None),
        "latest_fail": next((item for item in items if item.get("kind") == "fail"), None),
    }


def _load_previous_current(cache: Path) -> dict[str, Any] | None:
    p = cache / "APP_LIVE_INDEX" / "app_live_context.current.json"
    try:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _delta(current_apps: list[dict[str, Any]], previous: dict[str, Any] | None) -> dict[str, Any]:
    if not previous:
        return {"available": False, "reason": "no_previous_index", "changed_files_sample": [], "summary": "Primer índice fresco guardado."}
    prev_files = {}
    for app in previous.get("apps") or []:
        for bucket in ("recent_files", "routes_sample", "components_sample", "css_sample", "docs_sample"):
            for item in app.get(bucket) or []:
                rel = item.get("rel")
                if rel:
                    prev_files[rel] = item
    curr_files = {}
    for app in current_apps:
        for bucket in ("recent_files", "routes_sample", "components_sample", "css_sample", "docs_sample"):
            for item in app.get(bucket) or []:
                rel = item.get("rel")
                if rel:
                    curr_files[rel] = item
    changed = []
    added = []
    for rel, item in curr_files.items():
        prev = prev_files.get(rel)
        if not prev:
            added.append(item)
        elif item.get("sha256") and prev.get("sha256") and item.get("sha256") != prev.get("sha256"):
            changed.append(item)
        elif item.get("mtime") != prev.get("mtime"):
            changed.append(item)
    return {
        "available": True,
        "changed_count_sampled": len(changed),
        "added_count_sampled": len(added),
        "changed_files_sample": changed[:40],
        "added_files_sample": added[:40],
    }


def _memory_layers(root: Path, apps: list[dict[str, Any]], authority: dict[str, Any], evidence: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "semantic_memory": {
            "purpose": "Qué es cada superficie, ruta, componente y contrato del proyecto.",
            "signals": [f"{app.get('label')}: {app.get('file_count')} files / {app.get('route_count')} rutas" for app in apps if app.get("exists")][:8],
            "confidence": "high" if apps else "low",
        },
        "procedural_memory": {
            "purpose": "Cómo se trabaja sin romper: Mesh, scopes, gates, evidencia, rollback y no fake green.",
            "signals": ["Authority Mesh antes de cambios", "Product apps read-only en modo conocimiento", "No matar procesos ni hot Prisma", "Evidence ZIP primero cuando hay incertidumbre"],
            "confidence": "high" if authority.get("manual_found") else "medium",
        },
        "episodic_memory": {
            "purpose": "Qué pasó antes: result/fail/diagnostic ZIPs y reportes recientes.",
            "signals": [f"{evidence.get('zip_count', 0)} paquetes de evidencia indexados", f"latest_result={bool(evidence.get('latest_result'))}", f"latest_fail={bool(evidence.get('latest_fail'))}"],
            "confidence": "high" if evidence.get("zip_count") else "medium",
        },
        "operational_memory": {
            "purpose": "Estado actual del árbol, cambios recientes, rutas y señales runtime si existen.",
            "signals": [f"delta_available={delta.get('available')}", f"changed_sample={delta.get('changed_count_sampled', 0)}", f"added_sample={delta.get('added_count_sampled', 0)}"],
            "confidence": "medium",
        },
        "visual_memory": {
            "purpose": "Capas CSS, z-index, selectors visuales y deuda como !important existente.",
            "signals": [f"{app.get('label')}: {app.get('css_count')} CSS" for app in apps if app.get("css_count")][:8],
            "confidence": "medium",
        },
        "governance_memory": {
            "purpose": "Manual, matrices y contratos que dicen qué verdad manda.",
            "signals": [f"manual_found={authority.get('manual_found')}", f"readset_found={authority.get('readset_found')}"],
            "confidence": "high" if authority.get("manual_found") else "medium",
        },
    }
    return summary


def _question_router() -> list[dict[str, Any]]:
    return [
        {"pattern": "qué falta / terminar / pendiente", "uses": ["semantic_memory", "evidence_library", "authority_memory"], "render": "checklist + runtime_map"},
        {"pattern": "por qué falló / error / fail", "uses": ["episodic_memory", "evidence_library", "delta_scanner"], "render": "timeline + evidence_board"},
        {"pattern": "qué cambió / desde ayer", "uses": ["delta_scanner", "operational_memory"], "render": "timeline"},
        {"pattern": "qué CSS / layer / selector manda", "uses": ["visual_memory", "layer_investigator"], "render": "authority_map + checklist"},
        {"pattern": "qué riesgo", "uses": ["authority_memory", "evidence_library", "procedural_memory"], "render": "risk_matrix"},
        {"pattern": "apps / rutas / componentes", "uses": ["project_brain_index", "semantic_memory"], "render": "runtime_map"},
    ]


def _write_cache(cache: Path, payload: dict[str, Any]) -> dict[str, Any]:
    written: dict[str, Any] = {"ok": False, "paths": []}
    try:
        index_root = cache / "APP_LIVE_INDEX"
        memory_root = cache / "MEMORY_LAYERS"
        evidence_root = cache / "EVIDENCE_LIBRARY"
        journal_root = cache / "MEMORY_JOURNAL"
        for p in [index_root, memory_root, evidence_root, journal_root]:
            p.mkdir(parents=True, exist_ok=True)
        current = index_root / "app_live_context.current.json"
        current.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot = index_root / f"app_live_context.{stamp}.json"
        snapshot.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        (memory_root / "memory_layers.current.json").write_text(json.dumps(payload.get("memory_layers"), ensure_ascii=False, indent=2), encoding="utf-8")
        (evidence_root / "evidence_library.current.json").write_text(json.dumps(payload.get("evidence_library"), ensure_ascii=False, indent=2), encoding="utf-8")
        journal_entry = {
            "timestamp": payload.get("generated_at"),
            "event": "project_brain_refresh",
            "summary": payload.get("summary"),
            "memory_confidence": {k: v.get("confidence") for k, v in (payload.get("memory_layers") or {}).items()},
        }
        with (journal_root / "memory_journal.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(journal_entry, ensure_ascii=False) + "\n")
        written = {"ok": True, "paths": [str(current), str(snapshot), str(memory_root / "memory_layers.current.json"), str(evidence_root / "evidence_library.current.json"), str(journal_root / "memory_journal.jsonl")]}
    except Exception as exc:
        written = {"ok": False, "error": type(exc).__name__}
    return written


def app_live_context_payload(query: str = "", public: bool = False) -> dict[str, Any]:
    if public:
        return {"ok": False, "status": "blocked", "block_reason": "PUBLIC_APP_LIVE_CONTEXT_BLOCKED", "read_only": True, "mutation_allowed": False}
    started = time.perf_counter()
    root = _terminal_root()
    hitech = _hitech_root()
    descargas = _descargas_root()
    cache = _cache_root()
    previous = _load_previous_current(cache)
    surfaces = [
        ("tablet", "Tablet", "products/tablet/app"),
        ("pc", "PC", "products/pc/app"),
        ("mobile", "Mobile", "products/mobile/app"),
        ("chart_lab", "Chart Lab", "products/chart-lab"),
        ("eit", "EIT/Web", "external_interaction_template"),
        ("shared_docs", "Docs/Ops", "docs"),
        ("governance", "Governance", ".governance"),
        ("prisma_control_center", "PRISMO Control Center", "prisma-control-center"),
    ]
    apps = [_scan_surface(root, surface_id, label, rel_path) for surface_id, label, rel_path in surfaces]
    authority = _authority_memory(root)
    evidence = _evidence_library(descargas)
    delta = _delta(apps, previous)
    memory_layers = _memory_layers(root, apps, authority, evidence, delta)
    summary = {
        "app_count": len(apps),
        "file_count": sum(int(app.get("file_count") or 0) for app in apps),
        "route_count": sum(int(app.get("route_count") or 0) for app in apps),
        "css_count": sum(int(app.get("css_count") or 0) for app in apps),
        "component_count": sum(int(app.get("component_count") or 0) for app in apps),
        "doc_count": sum(int(app.get("doc_count") or 0) for app in apps),
        "evidence_zip_count": evidence.get("zip_count", 0),
        "memory_layer_count": len(memory_layers),
        "delta_available": bool(delta.get("available")),
    }
    payload: dict[str, Any] = {
        "ok": True,
        "status": "ready",
        "schema_version": "prismo.project_brain.v2",
        "read_only": True,
        "mutation_allowed": False,
        "repo_root": str(root),
        "hitech_root": str(hitech),
        "descargas_root": str(descargas),
        "query_hint": str(query or "")[:280],
        "generated_at": _now(),
        "apps": apps,
        "summary": summary,
        "project_brain": {
            "name": "PRISMO Project Brain Index",
            "description": "Read-only map of PRISMA apps, routes, components, CSS, docs, governance and evidence.",
            "surfaces": [{"id": app.get("id"), "label": app.get("label"), "path": app.get("path"), "exists": app.get("exists"), "file_count": app.get("file_count"), "route_count": app.get("route_count"), "css_count": app.get("css_count")} for app in apps],
            "question_router": _question_router(),
        },
        "memory_layers": memory_layers,
        "authority_memory": authority,
        "evidence_library": evidence,
        "delta_scanner": delta,
        "layer_investigator": {
            "surface_layer_samples": [{"surface": app.get("id"), "signals": app.get("layer_signals", [])[:24], "important_count_sampled": app.get("important_count_sampled", 0)} for app in apps if app.get("css_count")],
            "rule": "No agregar !important; ubicar selector canónico y capa propietaria.",
        },
        "safety": {
            "writes_repo": False,
            "kills_processes": False,
            "starts_servers": False,
            "frees_ports": False,
            "prisma_generate": False,
            "reads_env_secrets": False,
            "modifies_apps": False,
            "cache_only": True,
        },
    }
    cache_status = _write_cache(cache, payload)
    payload["cache_written"] = bool(cache_status.get("ok"))
    payload["cache_status"] = cache_status
    payload["cache_path"] = cache_status.get("paths", [None])[0]
    payload["elapsed_ms"] = round((time.perf_counter() - started) * 1000)
    return payload
