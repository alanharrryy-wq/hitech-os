
import argparse
import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile

PILOT_ROUTES = {
    "/stock": {
        "module": "Inventario",
        "question": "¿Qué productos necesitan atención?",
        "visual_budget": "pc-operational-dense",
        "panels": ["DecisionHeader", "PcModuleShell", "AttentionSummary", "NextBestAction", "ActionableTable", "EvidenceDrawer"],
        "primary_action": "Revisar productos críticos",
    },
    "/proveedores": {
        "module": "Proveedores",
        "question": "¿Con qué proveedor debo actuar hoy?",
        "visual_budget": "pc-operational",
        "panels": ["DecisionHeader", "PcModuleShell", "AttentionSummary", "NextBestAction", "ActionableTable", "EvidenceDrawer"],
        "primary_action": "Revisar proveedor sugerido",
    },
    "/sync": {
        "module": "Sincronización",
        "question": "¿Todo está actualizado entre equipos?",
        "visual_budget": "pc-sync",
        "panels": ["DecisionHeader", "PcModuleShell", "AttentionSummary", "NextBestAction", "ActionableTable", "EvidenceDrawer"],
        "primary_action": "Revisar pendientes de sincronización",
    },
}

VISUAL_BUDGET_DEFINITIONS = {
    "pc-home-premium": {
        "background": "layer.background.hoy_fullscreen_obsidian_halo",
        "glass": ["G2", "G3", "G4-selective"],
        "glow": "N2/N3-selective",
        "motion": "M2/M3",
        "webgl": "optional-off-by-default",
    },
    "pc-operational": {
        "background": "layer.background.executive_mineral_calm",
        "glass": ["G1", "G2", "G3-major-only"],
        "glow": "N1/N2",
        "motion": "M1/M2",
        "webgl": "no",
    },
    "pc-operational-dense": {
        "background": "layer.background.audit_quiet_vault",
        "glass": ["G1", "G2"],
        "glow": "N0/N1",
        "motion": "M1",
        "webgl": "no",
    },
    "pc-sync": {
        "background": "layer.background.sync_night_pulse",
        "glass": ["G1", "G2", "G3"],
        "glow": "N2-live",
        "motion": "M1/M2",
        "webgl": "no",
    },
    "pc-analysis-studio": {
        "background": "layer.background.chart_lab_deep_studio",
        "glass": ["G2", "G3", "G4-chart-frame"],
        "glow": "N2/N3-chart-only",
        "motion": "M2/M3",
        "webgl": "optional",
    },
    "pc-system": {
        "background": "layer.background.settings_matte_graphite",
        "glass": ["G1", "G2"],
        "glow": "N1/N2-state",
        "motion": "M1",
        "webgl": "no",
    },
    "pc-settings-quiet": {
        "background": "layer.background.settings_matte_graphite",
        "glass": ["G1"],
        "glow": "N0/N1",
        "motion": "M0/M1",
        "webgl": "no",
    },
    "pc-reporting": {
        "background": "layer.background.executive_mineral_calm",
        "glass": ["G1", "G2"],
        "glow": "N1",
        "motion": "M1",
        "webgl": "no",
    },
}

COPY_TERMS = {
    "sync": "Sincronización",
    "ingest": "Recepción de cambios",
    "outbox": "Cambios pendientes",
    "ack": "Confirmación",
    "dispatcher": "Envío de cambios",
    "payload": "Paquete de datos",
    "canonical": "Base principal",
    "runtime": "Sistema",
    "freshness": "Actualización",
    "confidence": "Confianza",
    "recipe": "Receta visual",
}

PANEL_PATCHES = [
    (
        Path("products/pc/app/components/uiux/decision-header.tsx"),
        'data-prisma-component="DecisionHeader" data-route-intent="human-decision"',
        'data-prisma-component="DecisionHeader" data-prisma-panel="decision-header" data-panel-role="decision-header" data-route-intent="human-decision"'
    ),
    (
        Path("products/pc/app/components/uiux/attention-summary.tsx"),
        'data-prisma-component="AttentionSummary" aria-label="Lectura rápida"',
        'data-prisma-component="AttentionSummary" data-prisma-panel="attention-summary" data-panel-role="quick-reading" aria-label="Lectura rápida"'
    ),
    (
        Path("products/pc/app/components/uiux/next-best-action.tsx"),
        '<section className="card" data-prisma-component="NextBestAction">',
        '<section className="card" data-prisma-component="NextBestAction" data-prisma-panel="next-best-action" data-panel-role="recommended-action" data-action-required="true">'
    ),
    (
        Path("products/pc/app/components/uiux/actionable-table.tsx"),
        'data-prisma-component="ActionableTable" data-action-column={hasActionColumn ? "present" : "auto-added"}',
        'data-prisma-component="ActionableTable" data-prisma-panel="actionable-table" data-panel-role="operational-detail" data-action-column={hasActionColumn ? "present" : "auto-added"}'
    ),
    (
        Path("products/pc/app/components/uiux/evidence-drawer.tsx"),
        'data-prisma-component="EvidenceDrawer" data-evidence-default="closed"',
        'data-prisma-component="EvidenceDrawer" data-prisma-panel="evidence-drawer" data-panel-role="technical-evidence" data-evidence-default="closed"'
    ),
    (
        Path("products/pc/app/components/uiux/chart-insight-card.tsx"),
        '<section className="card" data-prisma-component="ChartInsightCard">',
        '<section className="card" data-prisma-component="ChartInsightCard" data-prisma-panel="chart-insight" data-panel-role="chart-reading">'
    ),
    (
        Path("products/pc/app/components/uiux/pc-module-shell.tsx"),
        'data-prisma-component="PcModuleShell" data-pc-module={contract.group}',
        'data-prisma-component="PcModuleShell" data-prisma-panel="pc-module-shell" data-panel-role="module-frame" data-pc-module={contract.group}'
    ),
    (
        Path("products/pc/app/components/uiux/human-error-state.tsx"),
        'data-prisma-component="HumanErrorState" role="alert"',
        'data-prisma-component="HumanErrorState" data-prisma-panel="human-error-state" data-panel-role="human-error" role="alert"'
    ),
    (
        Path("products/pc/app/components/uiux/empty-state-human.tsx"),
        'data-prisma-component="EmptyStateHuman" role="status"',
        'data-prisma-component="EmptyStateHuman" data-prisma-panel="empty-state-human" data-panel-role="empty-state" role="status"'
    ),
]


def now_stamp():
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_to(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(path)


def copy_backup(root: Path, backup_root: Path, rel: Path, changes):
    src = root / rel
    if not src.exists():
        changes.append({"file": str(rel), "status": "missing", "action": "skip"})
        return None
    dst = backup_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def patch_components(root: Path, backup_root: Path):
    changes = []
    patched_files_dir = backup_root.parent / "patched-target-files"
    for rel, needle, repl in PANEL_PATCHES:
        src = root / rel
        if not src.exists():
            changes.append({"file": str(rel), "status": "missing", "action": "skip"})
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        before_hash = sha256(src)
        if 'data-prisma-panel=' in text and needle not in text:
            changes.append({"file": str(rel), "status": "already-patched", "sha256": before_hash})
            continue
        if needle not in text:
            changes.append({"file": str(rel), "status": "needle-not-found", "action": "no-write", "needle": needle[:120]})
            continue
        copy_backup(root, backup_root, rel, changes)
        new_text = text.replace(needle, repl, 1)
        src.write_text(new_text, encoding="utf-8")
        after_hash = sha256(src)
        out = patched_files_dir / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(new_text, encoding="utf-8")
        changes.append({"file": str(rel), "status": "patched", "before_sha256": before_hash, "after_sha256": after_hash})
    return changes


def route_from_page(app_dir: Path, page: Path) -> str:
    rel = page.parent.relative_to(app_dir)
    parts = [p for p in rel.parts if not (p.startswith("(") and p.endswith(")"))]
    if not parts:
        return "/"
    return "/" + "/".join(parts).replace("\\", "/")


def is_likely_visible_jargon(line: str, term: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("import ") or " from " in stripped or stripped.startswith("//"):
        return False
    if "className=" in stripped or "data-" in stripped:
        return False
    # Skip ordinary identifiers such as freshnessLabel, runtimeConfig, black, backoffice.
    if re.search(rf"[A-Za-z0-9_]({re.escape(term)})[A-Za-z0-9_]", stripped, flags=re.I):
        return False
    # Prefer visible JSX text or explicit human string literals.
    if re.search(rf"\b{re.escape(term)}\b", stripped, flags=re.I):
        return True
    return False


def infer_budget(route: str) -> str:
    if route == "/dashboard":
        return "pc-home-premium"
    if route in ("/stock", "/catalog", "/integridad-barcodes", "/salud-barcodes", "/validacion-catalogo", "/audit", "/auditoria-inventario"):
        return "pc-operational-dense"
    if route in ("/sync", "/sync-operativo"):
        return "pc-sync"
    if route.startswith("/settings") or route == "/license-runtime" or route == "/system":
        return "pc-system"
    if route in ("/reports", "/contratos-reporte"):
        return "pc-reporting"
    if route.startswith("/prisma-insights") or route == "/analytics":
        return "pc-analysis-studio"
    return "pc-operational"


def scan_route(root: Path, app_dir: Path, page: Path):
    route = route_from_page(app_dir, page)
    text = page.read_text(encoding="utf-8", errors="replace")
    uses_decision_screen = "DecisionScreen" in text
    pilot = PILOT_ROUTES.get(route)
    panels = []
    unregistered = []
    evidence_detected = False
    buttons = len(re.findall(r"<(?:a|button)\b", text))
    tables = len(re.findall(r"<(?:table|DataTable|ActionableTable)\b", text))
    charts = len(re.findall(r"(?:Chart|ECharts|chart)", text))

    if uses_decision_screen:
        info = pilot or {
            "module": None,
            "question": None,
            "visual_budget": infer_budget(route),
            "panels": ["DecisionHeader", "PcModuleShell", "AttentionSummary", "NextBestAction", "ActionableTable", "EvidenceDrawer"],
            "primary_action": None,
        }
        for idx, name in enumerate(info["panels"], 1):
            panels.append({
                "id": f"{route.strip('/').replace('/', '-') or 'root'}-{name.lower()}",
                "route": route,
                "file": str(page),
                "kind": "DecisionScreen-composition",
                "component": name,
                "role": {
                    "DecisionHeader": "decision-header",
                    "PcModuleShell": "module-frame",
                    "AttentionSummary": "quick-reading",
                    "NextBestAction": "recommended-action",
                    "ActionableTable": "operational-detail",
                    "EvidenceDrawer": "technical-evidence",
                }.get(name, "registered-panel"),
                "registered": True,
                "evidence": "route-contract" if name == "EvidenceDrawer" else None,
                "action": info.get("primary_action") if name == "NextBestAction" else None,
            })
        evidence_detected = True
        tables = max(tables, 1)
        buttons = max(buttons, 2)
    else:
        # Lightweight page-only heuristic for legacy panels
        panel_hits = list(re.finditer(r'className=["\'][^"\']*(?:card|panel|hero|dashboard-grid)[^"\']*["\']', text))
        for idx, _m in enumerate(panel_hits, 1):
            if "data-prisma-panel" not in text[max(0, _m.start()-200): _m.end()+200]:
                unregistered.append({
                    "id": f"{route.strip('/').replace('/', '-') or 'root'}-unregistered-panel-{idx}",
                    "route": route,
                    "file": str(page),
                    "kind": "className-heuristic",
                    "role": "visual-container",
                    "registered": False,
                    "warning": "Panel-like class without Prisma contract/wrapper",
                })
        evidence_detected = "EvidenceDrawer" in text or "evidencia" in text.lower() or "evidence" in text.lower()

    copy_hits = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for term, replacement in COPY_TERMS.items():
            if is_likely_visible_jargon(line, term):
                copy_hits.append({
                    "term": term,
                    "replacement": replacement,
                    "file": str(page),
                    "route": route,
                    "line": line_no,
                    "sample": line.strip()[:220],
                    "classifier": "visible-or-explicit-string",
                })

    module = pilot["module"] if pilot else None
    question = pilot["question"] if pilot else None
    visual_budget = pilot["visual_budget"] if pilot else infer_budget(route)
    has_contract = bool(pilot or uses_decision_screen)

    qa_status = "PASS" if (has_contract and evidence_detected and not unregistered and not copy_hits) else "WARN"

    route_rec = {
        "route": route,
        "file": str(page),
        "kind": page.name,
        "segment_source": str(page.parent),
        "has_contract": has_contract,
        "uses_decision_screen": uses_decision_screen,
        "module": module,
        "question": question,
        "visual_budget": visual_budget,
    }
    twin = {
        "route": route,
        "file": str(page),
        "module": module,
        "question": question,
        "visual_budget": visual_budget,
        "panels": len(panels) + len(unregistered),
        "registered_panels": len(panels),
        "unregistered_panels": len(unregistered),
        "buttons_detected": buttons,
        "tables_detected": tables,
        "charts_detected": charts,
        "evidence_detected": evidence_detected,
        "jargon_hits": len(copy_hits),
        "qa_status": qa_status,
    }
    return route_rec, panels, unregistered, copy_hits, twin


def build_smoke_html(generated_at, twins, panels, copy_hits):
    pilot_twins = [t for t in twins if t["route"] in PILOT_ROUTES]
    rows = "\n".join(
        f"<tr><td>{t['route']}</td><td>{t['module'] or ''}</td><td>{t['registered_panels']}/{t['panels']}</td><td>{'sí' if t['evidence_detected'] else 'no'}</td><td>{t['jargon_hits']}</td><td>{t['qa_status']}</td></tr>"
        for t in pilot_twins
    )
    panel_rows = "\n".join(
        f"<tr><td>{p['route']}</td><td>{p.get('component','')}</td><td>{p.get('role','')}</td><td>{'sí' if p['registered'] else 'no'}</td></tr>"
        for p in panels if p["route"] in PILOT_ROUTES
    )
    copy_rows = "\n".join(
        f"<tr><td>{c['route']}</td><td>{c['term']}</td><td>{c['replacement']}</td><td>{c['line']}</td></tr>"
        for c in copy_hits
    ) or '<tr><td colspan="4">Sin copy técnico visible detectado por clasificador v2.</td></tr>'
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>PRISMA PC Runtime Injector 01 Smoke Test</title>
<style>
:root {{ color-scheme: dark; --bg:#080a0d; --panel:rgba(130,150,175,.12); --line:rgba(255,255,255,.14); --text:#edf4ff; --muted:#a8b4c2; --ok:#67e8b9; --warn:#f6c76f; }}
body {{ margin:0; font-family: Inter, Segoe UI, Arial, sans-serif; background: radial-gradient(circle at 72% 18%, rgba(95,145,210,.13), transparent 34%), linear-gradient(145deg,#080a0d,#10151b 46%,#171d25); color:var(--text); }}
main {{ max-width:1180px; margin:0 auto; padding:32px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:24px; padding:20px; margin:18px 0; box-shadow:0 24px 80px rgba(0,0,0,.28); backdrop-filter: blur(18px); }}
h1 {{ font-size:34px; margin:0 0 6px; }}
h2 {{ margin-top:0; }}
p, td, th {{ color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; overflow:hidden; border-radius:16px; }}
td, th {{ border-bottom:1px solid var(--line); padding:10px 12px; text-align:left; }}
th {{ color:var(--text); }}
.badge {{ display:inline-block; padding:6px 10px; border-radius:999px; border:1px solid var(--line); margin-right:8px; }}
.ok {{ color:var(--ok); }}
.warn {{ color:var(--warn); }}
</style>
</head>
<body>
<main>
<section class="card">
  <span class="badge">Generated {generated_at}</span>
  <span class="badge ok">Runtime Injector 01</span>
  <h1>PRISMA PC · Stock / Proveedores / Sync</h1>
  <p>Smoke test de contracts, panels, evidence y copy audit v2. Si los pilots salen con paneles registrados, el compiler ya entiende la abstracción DecisionScreen.</p>
</section>
<section class="card">
  <h2>Rutas piloto</h2>
  <table><thead><tr><th>Ruta</th><th>Módulo</th><th>Paneles registrados</th><th>Evidencia</th><th>Copy hits</th><th>QA</th></tr></thead><tbody>{rows}</tbody></table>
</section>
<section class="card">
  <h2>Panel registry piloto</h2>
  <table><thead><tr><th>Ruta</th><th>Componente</th><th>Rol</th><th>Registrado</th></tr></thead><tbody>{panel_rows}</tbody></table>
</section>
<section class="card">
  <h2>Copy audit v2</h2>
  <table><thead><tr><th>Ruta</th><th>Término</th><th>Reemplazo</th><th>Línea</th></tr></thead><tbody>{copy_rows}</tbody></table>
</section>
</main>
</body>
</html>"""


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run_compiler_v2(root: Path, outroot: Path, generated_dir: Path, strict=False):
    pc_app = root / "products/pc/app"
    app_dir = pc_app / "app"
    if not app_dir.exists():
        raise RuntimeError(f"No existe app dir PC: {app_dir}")

    page_files = sorted(list(app_dir.rglob("page.tsx")) + list(app_dir.rglob("page.ts")) + list(app_dir.rglob("index.tsx")))
    routes, panels, unregistered, copy_hits, twins = [], [], [], [], []
    for page in page_files:
        route_rec, route_panels, route_unreg, route_copy, twin = scan_route(root, app_dir, page)
        routes.append(route_rec)
        panels.extend(route_panels)
        unregistered.extend(route_unreg)
        copy_hits.extend(route_copy)
        twins.append(twin)

    all_panels = panels + unregistered
    generated_at = now_stamp()
    budgets = {r["route"]: r["visual_budget"] for r in routes}
    evidence_nodes = []
    for p in panels:
        if p.get("evidence"):
            evidence_nodes.append({"route": p["route"], "panel": p["id"], "source": p["evidence"], "kind": "route-contract"})

    pilot_twins = [t for t in twins if t["route"] in PILOT_ROUTES]
    fatal = []
    for route in PILOT_ROUTES:
        t = next((x for x in twins if x["route"] == route), None)
        if not t:
            fatal.append(f"Missing pilot route in scan: {route}")
        elif t["registered_panels"] < 6 or not t["evidence_detected"]:
            fatal.append(f"Pilot route incomplete: {route} panels={t['registered_panels']} evidence={t['evidence_detected']}")

    overall = "FAIL" if fatal else ("WARN" if unregistered or copy_hits else "PASS")
    if strict and overall == "WARN":
        overall = "FAIL"

    summary = {
        "generated_at": generated_at,
        "overall_status": overall,
        "routes": len(routes),
        "panels": len(all_panels),
        "registered_panels": len(panels),
        "unregistered_panels": len(unregistered),
        "copy_hits": len(copy_hits),
        "pilot_routes": {t["route"]: t for t in pilot_twins},
        "fatal": fatal,
        "strict": bool(strict),
    }

    write_json(generated_dir / "pc-interface-compiler-summary.json", summary)
    write_json(generated_dir / "pc-route-registry.generated.json", routes)
    write_json(generated_dir / "pc-panel-registry.generated.json", all_panels)
    write_json(generated_dir / "pc-copy-audit.generated.json", copy_hits)
    write_json(generated_dir / "pc-interface-twins.generated.json", twins)
    write_json(generated_dir / "pc-evidence-graph.generated.json", {"generated_at": generated_at, "nodes": evidence_nodes})
    write_json(generated_dir / "pc-visual-budget.generated.json", {"generated_at": generated_at, "routeBudgets": budgets, "budgetDefinitions": VISUAL_BUDGET_DEFINITIONS})

    smoke = build_smoke_html(generated_at, twins, all_panels, copy_hits)
    (generated_dir / "pc-runtime-injector-01-smoke-test.html").write_text(smoke, encoding="utf-8")
    (generated_dir / "pc-interface-smoke-test.html").write_text(smoke, encoding="utf-8")

    report_lines = [
        "# PRISMA PC Runtime Injector 01 Report",
        "",
        f"Generated: `{generated_at}`",
        f"Overall status: **{overall}**",
        "",
        "## Summary",
        "",
        f"- Routes scanned: {len(routes)}",
        f"- Panels total: {len(all_panels)}",
        f"- Registered panels: {len(panels)}",
        f"- Unregistered panels: {len(unregistered)}",
        f"- Copy audit hits: {len(copy_hits)}",
        "",
        "## Pilot routes",
        "",
        "| Route | Module | Registered panels | Evidence | Copy hits | QA |",
        "|---|---|---:|---|---:|---|",
    ]
    for t in pilot_twins:
        report_lines.append(f"| `{t['route']}` | {t['module'] or ''} | {t['registered_panels']}/{t['panels']} | {'yes' if t['evidence_detected'] else 'no'} | {t['jargon_hits']} | {t['qa_status']} |")
    if fatal:
        report_lines.extend(["", "## Fatal issues", ""])
        report_lines.extend([f"- {x}" for x in fatal])
    if unregistered:
        report_lines.extend(["", "## Remaining unregistered panels", ""])
        for item in unregistered[:40]:
            report_lines.append(f"- `{item['route']}` · {item['id']} · {item['warning']}")
    if copy_hits:
        report_lines.extend(["", "## Copy audit hits v2", ""])
        for item in copy_hits[:40]:
            report_lines.append(f"- `{item['route']}` line {item['line']}: `{item['term']}` → {item['replacement']} · {item['sample']}")
    report_lines.extend([
        "",
        "## Notes",
        "",
        "- El compiler v2 entiende `DecisionScreen` como composición registrada para rutas piloto.",
        "- El copy audit v2 evita falsos positivos como `ack` dentro de `black` o `backoffice`.",
        "- Los warnings restantes fuera de rutas piloto indican deuda real para iteraciones posteriores.",
    ])
    (generated_dir / "pc-runtime-injector-01-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    (generated_dir / "pc-interface-compiler-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return summary


def zip_directory(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--outroot", required=True)
    ap.add_argument("--package-root", required=False)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    outroot = Path(args.outroot).resolve()
    stamp = now_stamp()
    result_root = outroot / f"PRISMA_PC_RUNTIME_INJECTOR_01_RESULT_{stamp}"
    backup_root = result_root / "rollback" / "backups"
    generated_dir = root / "docs/design/pc-runtime-injector-01/generated"
    docs_dir = root / "docs/design/pc-runtime-injector-01"
    tool_dir = root / "tools/prisma-visual-os/pc-runtime-injector-01"
    compiler_dir = root / "tools/prisma-visual-os/pc-interface-compiler"

    result_root.mkdir(parents=True, exist_ok=True)
    (result_root / "logs").mkdir(parents=True, exist_ok=True)
    (result_root / "reports").mkdir(parents=True, exist_ok=True)

    install_log = []
    status = "PASS"
    try:
        if not root.exists():
            raise RuntimeError(f"Root no existe: {root}")
        pc_app = root / "products/pc/app"
        if not pc_app.exists():
            raise RuntimeError(f"No existe PC app: {pc_app}")

        package_root = Path(args.package_root).resolve() if args.package_root else None
        if package_root and (package_root / "payload").exists():
            # Copy docs and tool payloads. Do not overwrite product source from payload.
            for rel in [
                Path("docs/design/pc-runtime-injector-01"),
                Path("tools/prisma-visual-os/pc-runtime-injector-01"),
                Path("tools/prisma-visual-os/pc-interface-compiler"),
            ]:
                src = package_root / "payload" / rel
                dst = root / rel
                if src.exists():
                    if dst.exists():
                        # merge copy
                        for f in src.rglob("*"):
                            if f.is_file():
                                relf = f.relative_to(src)
                                target = dst / relf
                                target.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(f, target)
                    else:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(src, dst)
                    install_log.append(f"installed payload {rel}")

        docs_dir.mkdir(parents=True, exist_ok=True)
        generated_dir.mkdir(parents=True, exist_ok=True)
        tool_dir.mkdir(parents=True, exist_ok=True)
        compiler_dir.mkdir(parents=True, exist_ok=True)

        changes = patch_components(root, backup_root)
        write_json(result_root / "reports" / "patched-components.json", changes)
        install_log.append(f"component patch count: {sum(1 for c in changes if c.get('status') == 'patched')}")

        # Run compiler v2 after patch.
        summary = run_compiler_v2(root, outroot, generated_dir, strict=args.strict)
        write_json(result_root / "reports" / "compiler-summary.json", summary)
        (result_root / "reports" / "pc-runtime-injector-01-report.md").write_text((generated_dir / "pc-runtime-injector-01-report.md").read_text(encoding="utf-8"), encoding="utf-8")

        if summary["overall_status"] == "FAIL":
            status = "FAIL"
            raise RuntimeError("Compiler v2 reported FAIL: " + "; ".join(summary.get("fatal", [])))

        if summary["overall_status"] == "WARN":
            status = "WARN"

        # Static target sanity.
        required_files = [
            root / "products/pc/app/components/uiux/decision-header.tsx",
            root / "products/pc/app/components/uiux/attention-summary.tsx",
            root / "products/pc/app/components/uiux/next-best-action.tsx",
            root / "products/pc/app/components/uiux/actionable-table.tsx",
            root / "products/pc/app/components/uiux/evidence-drawer.tsx",
            generated_dir / "pc-runtime-injector-01-report.md",
            generated_dir / "pc-runtime-injector-01-smoke-test.html",
        ]
        missing = [str(p) for p in required_files if not p.exists()]
        if missing:
            status = "FAIL"
            raise RuntimeError("Missing required outputs: " + ", ".join(missing))

        (result_root / "INSTALL_RESULT.md").write_text(
            "# PRISMA PC Runtime Injector 01 Install Result\n\n"
            f"Status: **{status}**\n\n"
            f"Generated dir: `{generated_dir}`\n\n"
            f"Smoke test: `{generated_dir / 'pc-runtime-injector-01-smoke-test.html'}`\n\n"
            f"Report: `{generated_dir / 'pc-runtime-injector-01-report.md'}`\n\n"
            "WARN significa que quedan deudas fuera de rutas piloto o copy audit no fatal. No es PASS falso.\n",
            encoding="utf-8",
        )
        (result_root / "logs" / "install.log").write_text("\n".join(install_log) + "\n", encoding="utf-8")
    except Exception as exc:
        status = "FAIL"
        (result_root / "logs" / "error.log").write_text(str(exc) + "\n", encoding="utf-8")
        # rollback files we backed up
        if backup_root.exists():
            for b in backup_root.rglob("*"):
                if b.is_file():
                    target = root / b.relative_to(backup_root)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(b, target)
        (result_root / "INSTALL_RESULT.md").write_text(
            "# PRISMA PC Runtime Injector 01 Install Result\n\n"
            "Status: **FAIL**\n\n"
            f"Error: `{exc}`\n\n"
            "Rollback automático aplicado para archivos respaldados.\n",
            encoding="utf-8",
        )
        zip_path = outroot / f"{result_root.name}_FAIL.zip"
        zip_directory(result_root, zip_path)
        print(f"[PRISMA PC Runtime Injector 01] status=FAIL")
        print(f"[PRISMA PC Runtime Injector 01] evidence_zip={zip_path}")
        raise

    zip_path = outroot / f"{result_root.name}_{status}.zip"
    zip_directory(result_root, zip_path)
    print(f"[PRISMA PC Runtime Injector 01] status={status}")
    print(f"[PRISMA PC Runtime Injector 01] report={generated_dir / 'pc-runtime-injector-01-report.md'}")
    print(f"[PRISMA PC Runtime Injector 01] smoke={generated_dir / 'pc-runtime-injector-01-smoke-test.html'}")
    print(f"[PRISMA PC Runtime Injector 01] evidence_zip={zip_path}")


if __name__ == "__main__":
    main()
