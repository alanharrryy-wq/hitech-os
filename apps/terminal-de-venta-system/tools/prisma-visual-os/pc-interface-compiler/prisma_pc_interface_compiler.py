#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA PC Interface Constitution Compiler
Non-destructive scanner/generator for PC interface contracts, visual budgets,
panel registry, copy audit and smoke-test evidence.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import os
import re
import shutil
import sys
import traceback
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

PANEL_TAGS = {
    "DecisionPanel", "PrismaPanel", "DecisionHeader", "AttentionSummary",
    "NextBestAction", "EvidenceDrawer", "ActionableTableShell", "InsightChartFrame",
    "HumanEmptyState", "HumanErrorState", "Card", "Panel", "Drawer", "Sheet",
    "Dialog", "Table", "Tabs", "Accordion"
}

VISUAL_CLASS_HINTS = re.compile(
    r'className\s*=\s*(?:"[^"]*(?:panel|card|surface|shell|tile|drawer|glass|frame)[^"]*"|`[^`]*(?:panel|card|surface|shell|tile|drawer|glass|frame)[^`]*`|\{[^}]+\})',
    re.I | re.S
)

STRING_LITERAL_RE = re.compile(r'(?P<q>["\'])(?P<body>(?:\\.|(?!\1).)*?)(?P=q)', re.S)

@dataclass
class RouteInfo:
    route: str
    file: str
    kind: str
    segment_source: str
    has_contract: bool
    module: str | None = None
    question: str | None = None
    visual_budget: str | None = None

@dataclass
class PanelInfo:
    id: str
    route: str
    file: str
    kind: str
    role: str
    registered: bool
    evidence: str | None = None
    action: str | None = None
    warning: str | None = None

@dataclass
class CopyHit:
    term: str
    replacement: str
    file: str
    route: str | None
    line: int
    sample: str

@dataclass
class InterfaceTwin:
    route: str
    file: str
    module: str | None
    question: str | None
    visual_budget: str | None
    panels: int
    registered_panels: int
    unregistered_panels: int
    buttons_detected: int
    tables_detected: int
    charts_detected: int
    evidence_detected: bool
    jargon_hits: int
    qa_status: str

def now_stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")

def read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return default

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def route_from_page(app_root: Path, file: Path) -> str:
    rel = file.relative_to(app_root)
    parts = list(rel.parts[:-1])
    clean: list[str] = []
    for p in parts:
        if p.startswith("(") and p.endswith(")"):
            continue
        if p.startswith("@"):
            continue
        if p.startswith("_"):
            continue
        if p in ("src", "app", "pages"):
            continue
        clean.append(p)
    if not clean:
        return "/"
    return "/" + "/".join(clean).replace("\\", "/")

def find_pc_app(root: Path) -> Path | None:
    candidates = [
        root / "products" / "pc" / "app",
        root / "products" / "pc",
        root / "apps" / "pc",
        root / "products" / "backoffice" / "app",
        root / "products" / "backoffice",
    ]
    for c in candidates:
        if c.exists():
            return c
    # fallback: find a folder with pc-ish package.json
    for package in root.rglob("package.json"):
        s = ""
        try:
            s = package.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            pass
        path_low = str(package.parent).lower()
        if ("pc" in path_low or "backoffice" in path_low) and ("next" in s or "react" in s):
            return package.parent
    return None

def find_app_roots(pc_app: Path) -> list[Path]:
    roots = []
    for c in [pc_app / "app", pc_app / "src" / "app", pc_app / "pages", pc_app / "src" / "pages"]:
        if c.exists():
            roots.append(c)
    return roots

def get_line(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1

def infer_module_from_route(route: str, seed_by_route: dict[str, Any]) -> str | None:
    if route in seed_by_route:
        return seed_by_route[route].get("module")
    lowered = route.lower()
    rules = [
        ("stock", "Inventario"),
        ("inventory", "Inventario"),
        ("catalog", "Catálogo"),
        ("proveedor", "Proveedores"),
        ("supplier", "Proveedores"),
        ("sync", "Sincronización"),
        ("sales", "Ventas y caja"),
        ("cash", "Ventas y caja"),
        ("purchase", "Compras"),
        ("receiv", "Compras"),
        ("report", "Reportes"),
        ("analytic", "Análisis"),
        ("chart", "Análisis"),
        ("system", "Sistema"),
        ("setting", "Configuración"),
        ("dashboard", "Hoy"),
    ]
    for key, val in rules:
        if key in lowered:
            return val
    return None

def infer_visual_budget(route: str, seed_by_route: dict[str, Any]) -> str:
    if route in seed_by_route:
        return seed_by_route[route].get("visualBudget") or "pc-operational"
    lowered = route.lower()
    if any(k in lowered for k in ("dashboard", "today", "hoy")):
        return "pc-home-premium"
    if any(k in lowered for k in ("stock", "inventory", "catalog", "barcode", "audit")):
        return "pc-operational-dense"
    if "sync" in lowered:
        return "pc-sync"
    if any(k in lowered for k in ("analytics", "analysis", "chart")):
        return "pc-analysis-studio"
    if "report" in lowered:
        return "pc-reporting"
    if any(k in lowered for k in ("system", "license", "health")):
        return "pc-system"
    if "setting" in lowered:
        return "pc-settings-quiet"
    return "pc-operational"

def extract_contract(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if "prismaInterface" not in text and "PrismaInterfaceContract" not in text:
        return out
    patterns = {
        "id": r'\bid\s*:\s*["\']([^"\']+)["\']',
        "route": r'\broute\s*:\s*["\']([^"\']+)["\']',
        "module": r'\bmodule\s*:\s*["\']([^"\']+)["\']',
        "question": r'\bquestion\s*:\s*["\']([^"\']+)["\']',
        "visualBudget": r'\bvisualBudget\s*:\s*["\']([^"\']+)["\']',
    }
    for key, pat in patterns.items():
        m = re.search(pat, text)
        if m:
            out[key] = m.group(1)
    return out

def extract_panel_contracts(text: str, route: str, file: Path) -> list[PanelInfo]:
    panels: list[PanelInfo] = []

    # Official DecisionPanel/PrismaPanel with contract prop/object nearby.
    for m in re.finditer(r'<(?P<tag>DecisionPanel|PrismaPanel|DecisionHeader|AttentionSummary|NextBestAction|EvidenceDrawer|ActionableTableShell|InsightChartFrame)\b(?P<attrs>[^>]*)>', text, re.S):
        tag = m.group("tag")
        attrs = m.group("attrs")
        around = text[m.start(): min(len(text), m.end() + 700)]
        pid = None
        role = tag
        evidence = None
        action = None
        mid = re.search(r'\bid\s*:\s*["\']([^"\']+)["\']', around)
        if mid:
            pid = mid.group(1)
        mrole = re.search(r'\brole\s*:\s*["\']([^"\']+)["\']', around)
        if mrole:
            role = mrole.group(1)
        mev = re.search(r'\bevidence\s*:\s*(?:"|\')([^"\']+)(?:"|\')', around)
        if mev:
            evidence = mev.group(1)
        ma = re.search(r'\baction\s*:\s*["\']([^"\']+)["\']', around)
        if ma:
            action = ma.group(1)
        if not pid:
            pid = f"{route.strip('/').replace('/','-') or 'root'}-{tag.lower()}-{len(panels)+1}"
        panels.append(PanelInfo(pid, route, str(file), "official-wrapper", role, True, evidence, action))

    # data-prisma-panel explicit markers.
    for m in re.finditer(r'data-prisma-panel\s*=\s*["\']([^"\']+)["\']', text):
        pid = m.group(1)
        panels.append(PanelInfo(pid, route, str(file), "data-attribute", "unknown", True))

    # Suspicious visual containers without wrapper.
    hints = list(VISUAL_CLASS_HINTS.finditer(text))
    official_count = len(panels)
    for idx, m in enumerate(hints[:80], start=1):
        start = max(0, m.start() - 80)
        snippet = text[start: min(len(text), m.end()+80)]
        if "data-prisma-panel" in snippet or "<DecisionPanel" in snippet or "<PrismaPanel" in snippet:
            continue
        pid = f"{route.strip('/').replace('/','-') or 'root'}-unregistered-panel-{idx}"
        panels.append(PanelInfo(pid, route, str(file), "className-heuristic", "visual-container", False, warning="Panel-like class without Prisma contract/wrapper"))

    return panels

def count_buttons(text: str) -> int:
    return len(re.findall(r'<button\b|<Button\b|role\s*=\s*["\']button["\']', text))

def count_tables(text: str) -> int:
    return len(re.findall(r'<table\b|useReactTable|@tanstack/react-table|ActionableTable', text, re.I))

def count_charts(text: str) -> int:
    return len(re.findall(r'echarts|ReactECharts|EChart|ChartFrame|InsightChart|<Chart\b', text, re.I))

def route_for_file(file: Path, app_roots: list[Path]) -> str | None:
    for app_root in app_roots:
        try:
            rel = file.relative_to(app_root)
            # file belongs under app/pages root
            if file.name in ("page.tsx","page.ts","index.tsx","index.ts"):
                if app_root.name == "pages":
                    parts = list(rel.parts[:-1])
                    if file.name.startswith("index"):
                        if not parts:
                            return "/"
                        return "/" + "/".join(parts)
                return route_from_page(app_root, file)
        except Exception:
            continue
    return None

def collect_string_literals(text: str) -> list[tuple[str, int]]:
    out = []
    for m in STRING_LITERAL_RE.finditer(text):
        body = m.group("body")
        if len(body) > 240:
            continue
        if re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]', body):
            out.append((body, get_line(text, m.start())))
    # JSX text crude extraction
    for m in re.finditer(r'>([^<>{}\n][^<>{}]{2,160})<', text):
        body = re.sub(r'\s+', ' ', m.group(1)).strip()
        if body and re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]', body):
            out.append((body, get_line(text, m.start())))
    return out

def audit_copy(text: str, file: Path, route: str | None, dictionary: dict[str, str]) -> list[CopyHit]:
    hits: list[CopyHit] = []
    literals = collect_string_literals(text)
    for sample, line in literals:
        low = sample.lower()
        for term, replacement in dictionary.items():
            if term.lower() in low:
                hits.append(CopyHit(term, replacement, str(file), route, line, sample))
    return hits

def html_escape(s: Any) -> str:
    return html.escape(str(s), quote=True)

def make_smoke_html(path: Path, data: dict[str, Any]) -> None:
    routes = data.get("routes", [])
    twins = data.get("twins", [])
    copy_hits = data.get("copy_hits", [])
    panels = data.get("panels", [])

    rows = []
    for t in twins:
        status = t.get("qa_status", "unknown")
        rows.append(f"<tr><td>{html_escape(t.get('route'))}</td><td>{html_escape(t.get('module'))}</td><td>{html_escape(t.get('question'))}</td><td>{html_escape(t.get('panels'))}</td><td>{html_escape(t.get('unregistered_panels'))}</td><td class='{html_escape(status.lower())}'>{html_escape(status)}</td></tr>")

    copy_rows = []
    for h in copy_hits[:250]:
        copy_rows.append(f"<tr><td>{html_escape(h.get('term'))}</td><td>{html_escape(h.get('replacement'))}</td><td>{html_escape(h.get('route'))}</td><td>{html_escape(h.get('line'))}</td><td>{html_escape(h.get('sample'))}</td></tr>")

    panel_rows = []
    for p in panels[:300]:
        panel_rows.append(f"<tr><td>{html_escape(p.get('route'))}</td><td>{html_escape(p.get('id'))}</td><td>{html_escape(p.get('kind'))}</td><td>{html_escape(p.get('role'))}</td><td>{html_escape(p.get('registered'))}</td><td>{html_escape(p.get('warning'))}</td></tr>")

    html_doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>PRISMA PC Interface Compiler Smoke Test</title>
<style>
:root {{ color-scheme: dark; --bg:#080a0d; --panel:rgba(150,170,200,.10); --line:rgba(255,255,255,.14); --text:#eff6ff; --muted:rgba(224,232,244,.68); --ok:#7ee6b8; --warn:#f4c56d; --fail:#ff7b86; }}
body {{ margin:0; font-family: Inter, Segoe UI, system-ui, sans-serif; background: radial-gradient(circle at 80% 10%, rgba(86,145,220,.16), transparent 30%), linear-gradient(145deg,#080a0d,#121923); color:var(--text); }}
main {{ padding:28px; }}
section {{ background:var(--panel); border:1px solid var(--line); border-radius:24px; padding:20px; margin:18px 0; backdrop-filter: blur(16px); box-shadow:0 20px 60px rgba(0,0,0,.25); }}
h1,h2 {{ margin:0 0 10px; }}
p {{ color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ text-align:left; border-bottom:1px solid var(--line); padding:10px; vertical-align:top; }}
th {{ color:#b9d6ff; }}
.pass {{ color:var(--ok); }}
.warn {{ color:var(--warn); }}
.fail {{ color:var(--fail); }}
.badge {{ display:inline-flex; border:1px solid var(--line); border-radius:999px; padding:6px 10px; margin-right:8px; color:var(--muted); }}
</style>
</head>
<body>
<main>
<h1>PRISMA PC Interface Compiler · Smoke Test</h1>
<p>Generado: {html_escape(data.get('generated_at'))}. Este smoke test resume rutas, paneles, copy técnico y estado diagnóstico.</p>
<section>
<span class="badge">Rutas: {len(routes)}</span>
<span class="badge">Paneles detectados: {len(panels)}</span>
<span class="badge">Copy hits: {len(copy_hits)}</span>
<span class="badge">Estado: {html_escape(data.get('overall_status'))}</span>
</section>
<section>
<h2>Interface Twins</h2>
<table><thead><tr><th>Ruta</th><th>Módulo</th><th>Pregunta</th><th>Paneles</th><th>No registrados</th><th>QA</th></tr></thead><tbody>
{''.join(rows)}
</tbody></table>
</section>
<section>
<h2>Panel Registry</h2>
<table><thead><tr><th>Ruta</th><th>ID</th><th>Tipo</th><th>Rol</th><th>Registrado</th><th>Warning</th></tr></thead><tbody>
{''.join(panel_rows)}
</tbody></table>
</section>
<section>
<h2>Copy técnico detectado</h2>
<table><thead><tr><th>Término</th><th>Traducción sugerida</th><th>Ruta</th><th>Línea</th><th>Muestra</th></tr></thead><tbody>
{''.join(copy_rows)}
</tbody></table>
</section>
</main>
</body>
</html>"""
    path.write_text(html_doc, encoding="utf-8")

def make_report(path: Path, data: dict[str, Any]) -> None:
    twins = data.get("twins", [])
    panels = data.get("panels", [])
    copy_hits = data.get("copy_hits", [])
    unregistered = [p for p in panels if not p.get("registered")]
    lines = []
    lines.append("# PRISMA PC Interface Compiler Report")
    lines.append("")
    lines.append(f"**Generado:** {data.get('generated_at')}")
    lines.append(f"**Root:** `{data.get('root')}`")
    lines.append(f"**PC App:** `{data.get('pc_app')}`")
    lines.append(f"**Modo:** `{data.get('mode')}`")
    lines.append(f"**Estado general:** `{data.get('overall_status')}`")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Rutas detectadas: **{len(data.get('routes', []))}**")
    lines.append(f"- Paneles detectados: **{len(panels)}**")
    lines.append(f"- Paneles no registrados: **{len(unregistered)}**")
    lines.append(f"- Hits de copy técnico: **{len(copy_hits)}**")
    lines.append("")
    lines.append("## Interface Twins")
    lines.append("")
    lines.append("| Ruta | Módulo | Pregunta | Panels | No registrados | Charts | Tables | Evidence | Jargon | QA |")
    lines.append("|---|---|---|---:|---:|---:|---:|---|---:|---|")
    for t in twins:
        lines.append(f"| `{t.get('route')}` | {t.get('module') or '—'} | {t.get('question') or '—'} | {t.get('panels')} | {t.get('unregistered_panels')} | {t.get('charts_detected')} | {t.get('tables_detected')} | {t.get('evidence_detected')} | {t.get('jargon_hits')} | **{t.get('qa_status')}** |")
    lines.append("")
    lines.append("## Paneles no registrados")
    lines.append("")
    if unregistered:
        lines.append("| Ruta | ID | Archivo | Warning |")
        lines.append("|---|---|---|---|")
        for p in unregistered[:200]:
            lines.append(f"| `{p.get('route')}` | `{p.get('id')}` | `{p.get('file')}` | {p.get('warning') or ''} |")
    else:
        lines.append("No se detectaron paneles sospechosos sin contrato.")
    lines.append("")
    lines.append("## Copy técnico visible detectado")
    lines.append("")
    if copy_hits:
        lines.append("| Término | Sugerencia | Ruta | Línea | Muestra |")
        lines.append("|---|---|---|---:|---|")
        for h in copy_hits[:200]:
            lines.append(f"| `{h.get('term')}` | {h.get('replacement')} | `{h.get('route')}` | {h.get('line')} | {h.get('sample')} |")
    else:
        lines.append("No se detectó copy técnico usando el diccionario actual.")
    lines.append("")
    lines.append("## Siguiente paso recomendado")
    lines.append("")
    lines.append("Migrar primero `/stock`, `/proveedores` y `/sync` a `DecisionPage`, `DecisionPanel`, `EvidenceDrawer`, `ActionableTableShell` e `InsightChartFrame`. Luego ejecutar el compilador en modo estricto.")
    path.write_text("\n".join(lines), encoding="utf-8")

def create_result_zip(outroot: Path, generated_dir: Path, stamp: str, status: str) -> Path:
    outroot.mkdir(parents=True, exist_ok=True)
    zip_path = outroot / f"PRISMA_PC_INTERFACE_COMPILER_RESULT_{stamp}_{status}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in generated_dir.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(generated_dir.parent))
    return zip_path

def run(root: Path, outroot: Path, strict: bool = False) -> int:
    stamp = now_stamp()
    docs_dir = root / "docs" / "design" / "pc-interface-constitution-engine"
    generated = docs_dir / "generated"
    generated.mkdir(parents=True, exist_ok=True)

    seed = read_json(docs_dir / "pc-interface-seed-contracts.json", {"contracts":[]})
    dictionary_data = read_json(docs_dir / "human-copy-dictionary.json", {"terms":{}})
    visual_budgets = read_json(docs_dir / "pc-visual-budgets.json", {"budgets":{}})
    seed_by_route = {c.get("route"): c for c in seed.get("contracts", []) if c.get("route")}
    dictionary = dictionary_data.get("terms", {})

    pc_app = find_pc_app(root)
    if not pc_app:
        report = {
            "generated_at": stamp,
            "root": str(root),
            "pc_app": None,
            "mode": "strict" if strict else "diagnostic",
            "overall_status": "FAIL",
            "error": "No PC app directory found."
        }
        write_json(generated / "pc-interface-compiler-error.json", report)
        make_report(generated / "pc-interface-compiler-report.md", {**report, "routes":[], "panels":[], "twins":[], "copy_hits":[]})
        create_result_zip(outroot, generated, stamp, "FAIL")
        return 2 if strict else 0

    app_roots = find_app_roots(pc_app)
    if not app_roots:
        # fallback to scan src for TSX, no route mapping
        app_roots = [pc_app]

    route_infos: list[RouteInfo] = []
    panels: list[PanelInfo] = []
    copy_hits: list[CopyHit] = []
    per_route_metrics: dict[str, dict[str, Any]] = {}

    files = []
    for app_root in app_roots:
        for pat in ("*.tsx", "*.ts", "*.jsx", "*.js"):
            files.extend(app_root.rglob(pat))
    # avoid generated/build/vendor
    files = [f for f in files if not any(part in {".next","node_modules","out","dist","build",".turbo"} for part in f.parts)]
    files = sorted(set(files), key=lambda p: str(p).lower())

    for file in files:
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        route = route_for_file(file, app_roots)
        contract = extract_contract(text)
        effective_route = contract.get("route") or route

        if route or contract:
            r = effective_route or route or f"unmapped::{file.name}"
            module = contract.get("module") or infer_module_from_route(r, seed_by_route)
            question = contract.get("question") or (seed_by_route.get(r, {}) or {}).get("question")
            visual_budget = contract.get("visualBudget") or infer_visual_budget(r, seed_by_route)
            if route:
                route_infos.append(RouteInfo(
                    route=r, file=str(file), kind=file.name, segment_source=str(file.parent),
                    has_contract=bool(contract), module=module, question=question, visual_budget=visual_budget
                ))

        # panels/copy can be mapped to route if known
        mapped_route = effective_route or route
        if mapped_route:
            file_panels = extract_panel_contracts(text, mapped_route, file)
            panels.extend(file_panels)
            copy_hits.extend(audit_copy(text, file, mapped_route, dictionary))
            metrics = per_route_metrics.setdefault(mapped_route, {
                "buttons":0, "tables":0, "charts":0, "evidence":False, "files":set(), "jargon":0
            })
            metrics["buttons"] += count_buttons(text)
            metrics["tables"] += count_tables(text)
            metrics["charts"] += count_charts(text)
            metrics["evidence"] = metrics["evidence"] or ("EvidenceDrawer" in text or "data-prisma-panel-role=\"evidence\"" in text or "technical" in text.lower() or "evidencia" in text.lower())
            metrics["files"].add(str(file))
            metrics["jargon"] += len(audit_copy(text, file, mapped_route, dictionary))

    # Include seed routes not found, as planned routes.
    detected_routes = {r.route for r in route_infos}
    for c in seed.get("contracts", []):
        if c.get("route") not in detected_routes:
            route_infos.append(RouteInfo(
                route=c.get("route","/"), file="", kind="seed-only", segment_source="pc-interface-seed-contracts",
                has_contract=False, module=c.get("module"), question=c.get("question"), visual_budget=c.get("visualBudget")
            ))

    route_infos = sorted(route_infos, key=lambda r: (r.route, r.file))

    twins: list[InterfaceTwin] = []
    for r in route_infos:
        route_panels = [p for p in panels if p.route == r.route]
        unreg = [p for p in route_panels if not p.registered]
        metrics = per_route_metrics.get(r.route, {"buttons":0,"tables":0,"charts":0,"evidence":False,"jargon":0})
        route_copy_hits = [h for h in copy_hits if h.route == r.route]
        warn_reasons = []
        if not r.question:
            warn_reasons.append("missing-question")
        if unreg:
            warn_reasons.append("unregistered-panels")
        if route_copy_hits:
            warn_reasons.append("technical-copy")
        if (seed_by_route.get(r.route, {}) or {}).get("evidenceRequired") and not metrics.get("evidence"):
            warn_reasons.append("missing-evidence-disclosure")
        if r.visual_budget not in visual_budgets.get("budgets", {}):
            warn_reasons.append("unknown-visual-budget")
        status = "PASS" if not warn_reasons else ("FAIL" if strict and any(x in warn_reasons for x in ("missing-question","unregistered-panels")) else "WARN")
        twins.append(InterfaceTwin(
            route=r.route, file=r.file, module=r.module, question=r.question, visual_budget=r.visual_budget,
            panels=len(route_panels), registered_panels=len(route_panels)-len(unreg), unregistered_panels=len(unreg),
            buttons_detected=metrics.get("buttons", 0), tables_detected=metrics.get("tables",0), charts_detected=metrics.get("charts",0),
            evidence_detected=bool(metrics.get("evidence")), jargon_hits=len(route_copy_hits), qa_status=status
        ))

    overall = "PASS"
    if any(t.qa_status == "FAIL" for t in twins):
        overall = "FAIL"
    elif any(t.qa_status == "WARN" for t in twins):
        overall = "WARN"

    data = {
        "schema": "prisma.pc.interface-compiler.result.v1",
        "generated_at": stamp,
        "root": str(root),
        "pc_app": str(pc_app),
        "app_roots": [str(p) for p in app_roots],
        "mode": "strict" if strict else "diagnostic",
        "overall_status": overall,
        "routes": [asdict(r) for r in route_infos],
        "panels": [asdict(p) for p in panels],
        "copy_hits": [asdict(h) for h in copy_hits],
        "twins": [asdict(t) for t in twins],
    }

    write_json(generated / "pc-route-registry.generated.json", data["routes"])
    write_json(generated / "pc-panel-registry.generated.json", data["panels"])
    write_json(generated / "pc-copy-audit.generated.json", data["copy_hits"])
    write_json(generated / "pc-interface-twins.generated.json", data["twins"])
    write_json(generated / "pc-visual-budget.generated.json", {
        "generated_at": stamp,
        "routeBudgets": {t.route: t.visual_budget for t in twins},
        "budgetDefinitions": visual_budgets.get("budgets", {}),
    })
    write_json(generated / "pc-evidence-graph.generated.json", {
        "generated_at": stamp,
        "nodes": [
            {
                "route": p.route, "panel": p.id, "evidence": p.evidence, "action": p.action,
                "status": "declared" if p.evidence else "missing"
            }
            for p in panels if p.registered
        ]
    })
    write_json(generated / "pc-interface-compiler-summary.json", {
        "generated_at": stamp,
        "overall_status": overall,
        "routes": len(route_infos),
        "panels": len(panels),
        "unregistered_panels": len([p for p in panels if not p.registered]),
        "copy_hits": len(copy_hits),
        "strict": strict,
    })

    make_report(generated / "pc-interface-compiler-report.md", data)
    make_smoke_html(generated / "pc-interface-smoke-test.html", data)

    zip_path = create_result_zip(outroot, generated, stamp, overall)
    print(f"[PRISMA PC Interface Compiler] status={overall}")
    print(f"[PRISMA PC Interface Compiler] report={generated / 'pc-interface-compiler-report.md'}")
    print(f"[PRISMA PC Interface Compiler] smoke={generated / 'pc-interface-smoke-test.html'}")
    print(f"[PRISMA PC Interface Compiler] evidence_zip={zip_path}")

    if strict and overall == "FAIL":
        return 3
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--outroot", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    try:
        return run(Path(args.root).resolve(), Path(args.outroot).resolve(), args.strict)
    except Exception as exc:
        stamp = now_stamp()
        outroot = Path(args.outroot)
        outroot.mkdir(parents=True, exist_ok=True)
        err = outroot / f"PRISMA_PC_INTERFACE_COMPILER_FATAL_{stamp}.log"
        err.write_text(traceback.format_exc(), encoding="utf-8")
        print(f"[PRISMA PC Interface Compiler] FATAL: {exc}", file=sys.stderr)
        print(f"[PRISMA PC Interface Compiler] log={err}", file=sys.stderr)
        return 10

if __name__ == "__main__":
    raise SystemExit(main())
