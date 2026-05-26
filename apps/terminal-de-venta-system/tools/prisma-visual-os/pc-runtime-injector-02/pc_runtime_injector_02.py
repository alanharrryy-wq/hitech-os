#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA PC Runtime Injector 02

Objetivo:
- Cerrar deuda detectada por Runtime Injector 01 en rutas secundarias de inventario/catálogo.
- Agregar metadata data-prisma-panel no destructiva a panel-like JSX elements.
- No reescribir lógica, imports ni contratos de negocio.
- Crear backups y reportes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

TARGET_ROUTES = [
    "ajustes-inventario",
    "alertas-operativas",
    "auditoria-inventario",
    "catalogo-activo",
    "conteos-operativos",
    "existencias-criticas",
    "integridad-barcodes",
    "politica-precios",
    "salud-barcodes",
    "validacion-catalogo",
]

ROLE_BY_ROUTE = {
    "ajustes-inventario": "inventory-adjustments-panel",
    "alertas-operativas": "operational-alerts-panel",
    "auditoria-inventario": "inventory-audit-panel",
    "catalogo-activo": "active-catalog-panel",
    "conteos-operativos": "inventory-counts-panel",
    "existencias-criticas": "critical-stock-panel",
    "integridad-barcodes": "barcode-integrity-panel",
    "politica-precios": "pricing-policy-panel",
    "salud-barcodes": "barcode-health-panel",
    "validacion-catalogo": "catalog-validation-panel",
}

QUESTION_BY_ROUTE = {
    "ajustes-inventario": "¿Qué ajustes de inventario requieren revisión?",
    "alertas-operativas": "¿Qué alertas operativas deben atenderse?",
    "auditoria-inventario": "¿Qué cambió en inventario y cómo se sabe?",
    "catalogo-activo": "¿Qué productos están listos para vender?",
    "conteos-operativos": "¿Qué conteos necesitan seguimiento?",
    "existencias-criticas": "¿Qué existencias están en riesgo?",
    "integridad-barcodes": "¿Qué códigos de barras pueden causar errores?",
    "politica-precios": "¿Qué reglas de precio necesitan atención?",
    "salud-barcodes": "¿La salud de códigos permite vender sin conflictos?",
    "validacion-catalogo": "¿El catálogo está listo para operar?",
}

MODULE_BY_ROUTE = {
    "ajustes-inventario": "Ajustes de inventario",
    "alertas-operativas": "Alertas operativas",
    "auditoria-inventario": "Auditoría de inventario",
    "catalogo-activo": "Catálogo activo",
    "conteos-operativos": "Conteos operativos",
    "existencias-criticas": "Existencias críticas",
    "integridad-barcodes": "Integridad de códigos",
    "politica-precios": "Política de precios",
    "salud-barcodes": "Salud de códigos",
    "validacion-catalogo": "Validación de catálogo",
}

PANEL_CLASS_RE = re.compile(
    r'(<(?P<tag>div|section|article|main)\b(?![^>]*data-prisma-panel=)(?P<attrs>[^>]*className\s*=\s*(?P<quote>["\'])(?P<class>[^"\']*(?:rounded|border|shadow|bg-|backdrop|glass|card|panel|surface|shell)[^"\']*)(?P=quote)[^>]*)>)',
    re.IGNORECASE | re.MULTILINE,
)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def route_file(pc_app: Path, slug: str) -> Path:
    return pc_app / "app" / slug / "page.tsx"

def find_insert_pos(opening_tag: str) -> int:
    # before closing > of opening tag
    return len(opening_tag) - 1

def patch_file(path: Path, slug: str) -> Tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    if "data-prisma-panel=" in text:
        return False, "already_has_prisma_panel"

    match = PANEL_CLASS_RE.search(text)
    if not match:
        return False, "no_panel_like_class_found"

    panel_id = f"{slug}-registered-panel-1"
    role = ROLE_BY_ROUTE.get(slug, "route-panel")
    metadata = (
        f'\n      data-prisma-panel="{panel_id}"'
        f'\n      data-prisma-panel-role="{role}"'
        f'\n      data-prisma-panel-source="runtime-injector-02"'
        f'\n      data-prisma-panel-question="{QUESTION_BY_ROUTE.get(slug, "¿Qué debe decidir esta pantalla?")}"'
    )

    opening = match.group(1)
    pos_in_opening = find_insert_pos(opening)
    new_opening = opening[:pos_in_opening] + metadata + opening[pos_in_opening:]

    new_text = text[:match.start(1)] + new_opening + text[match.end(1):]
    path.write_text(new_text, encoding="utf-8")
    return True, "patched"

def ensure_contract_docs(root: Path) -> None:
    docs = root / "docs" / "design" / "pc-runtime-injector-02"
    contracts = docs / "interface-contracts"
    contracts.mkdir(parents=True, exist_ok=True)

    for slug in TARGET_ROUTES:
        contract = {
            "schema": "prisma.pc.interface.contract.v2",
            "route": f"/{slug}",
            "module": MODULE_BY_ROUTE.get(slug, slug),
            "question": QUESTION_BY_ROUTE.get(slug, "¿Qué debe decidir esta pantalla?"),
            "visualBudget": "pc-operational-dense",
            "requiredLayers": [
                "lectura_rapida",
                "acciones_recomendadas",
                "detalle_operativo",
                "evidencia_tecnica"
            ],
            "registeredBy": "runtime-injector-02",
            "panelRole": ROLE_BY_ROUTE.get(slug, "route-panel"),
            "evidenceRequired": True
        }
        (contracts / f"{slug}.interface-contract.json").write_text(
            json.dumps(contract, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    readme = docs / "README.md"
    readme.write_text(
        "# PRISMA PC Runtime Injector 02\n\n"
        "Cierra deuda de paneles no registrados detectada después de Runtime Injector 01.\n\n"
        "Alcance: rutas secundarias de inventario/catálogo reportadas como panel-like sin contrato.\n\n"
        "La inyección agrega metadata `data-prisma-panel` sin cambiar lógica, imports ni negocio.\n",
        encoding="utf-8"
    )

def make_report(results: List[Dict], report: Path) -> None:
    patched = sum(1 for r in results if r["status"] == "patched")
    skipped = len(results) - patched

    lines = [
        "# PRISMA PC Runtime Injector 02 Report",
        "",
        f"Generated: `{datetime.now().strftime('%Y%m%d_%H%M%S')}`",
        "",
        "## Summary",
        "",
        f"- Targets: {len(results)}",
        f"- Patched: {patched}",
        f"- Skipped: {skipped}",
        "",
        "## Route patch results",
        "",
        "| Route | Status | Reason |",
        "|---|---|---|",
    ]

    for r in results:
        lines.append(f"| `/{r['slug']}` | {r['status']} | {r['reason']} |")

    lines += [
        "",
        "## Notes",
        "",
        "- Metadata injection is intentionally non-destructive.",
        "- This pass closes panel registration debt for secondary inventory/catalog routes.",
        "- If a route was skipped because no panel-like class was found, it should be reviewed manually or added to a route contract resolver.",
    ]

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")

def make_smoke(root: Path, results: List[Dict]) -> None:
    gen = root / "docs" / "design" / "pc-runtime-injector-02" / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    cards = []
    for r in results:
        status = r["status"]
        color = "#34d399" if status == "patched" else "#fbbf24"
        cards.append(
            f'<article class="card"><span style="color:{color}">{status}</span>'
            f'<h2>/{r["slug"]}</h2><p>{r["reason"]}</p></article>'
        )
    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>PRISMA PC Runtime Injector 02 Smoke</title>
<style>
:root {{ color-scheme: dark; font-family: Inter, Segoe UI, sans-serif; }}
body {{ margin:0; min-height:100vh; background: radial-gradient(circle at 25% 20%, rgba(120,170,255,.18), transparent 34%), linear-gradient(135deg,#080a0d,#151b23 52%,#202733); color:#eef5ff; }}
main {{ padding:32px; max-width:1120px; margin:auto; }}
h1 {{ font-size:34px; margin:0 0 8px; }}
.grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(240px,1fr)); gap:14px; margin-top:24px; }}
.card {{ border:1px solid rgba(255,255,255,.16); background:rgba(120,145,175,.12); backdrop-filter: blur(18px); border-radius:22px; padding:18px; box-shadow:0 20px 60px rgba(0,0,0,.28); }}
.card h2 {{ margin:8px 0; font-size:18px; }}
.card p {{ color:#b8c5d6; }}
</style>
</head>
<body>
<main>
<h1>PRISMA PC Runtime Injector 02</h1>
<p>Debt sweep para paneles secundarios de inventario/catálogo.</p>
<section class="grid">
{''.join(cards)}
</section>
</main>
</body>
</html>"""
    (gen / "pc-runtime-injector-02-smoke-test.html").write_text(html, encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--work-root", required=True)
    ap.add_argument("--patch-json", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    pc_app = root / "products" / "pc" / "app"
    work_root = Path(args.work_root)
    backup_root = work_root / "rollback" / "backups"
    patched_root = work_root / "rollback" / "patched-target-files"

    results: List[Dict] = []
    for slug in TARGET_ROUTES:
        path = route_file(pc_app, slug)
        rec: Dict = {"slug": slug, "path": str(path), "status": "skipped", "reason": ""}
        if not path.exists():
            rec["reason"] = "missing_route_page"
            results.append(rec)
            continue

        before = sha256(path)
        rel = path.relative_to(root)
        backup = backup_root / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)

        changed, reason = patch_file(path, slug)
        after = sha256(path)
        rec.update({
            "status": "patched" if changed else "skipped",
            "reason": reason,
            "before_sha256": before,
            "after_sha256": after,
        })

        patched = patched_root / rel
        patched.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, patched)
        results.append(rec)

    ensure_contract_docs(root)
    make_report(results, Path(args.report))
    make_smoke(root, results)

    pj = Path(args.patch_json)
    pj.parent.mkdir(parents=True, exist_ok=True)
    pj.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[PRISMA PC Runtime Injector 02] patched={sum(1 for r in results if r['status']=='patched')} targets={len(results)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
