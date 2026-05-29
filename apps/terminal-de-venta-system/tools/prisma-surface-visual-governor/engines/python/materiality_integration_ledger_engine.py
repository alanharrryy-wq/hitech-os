from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

ENGINE_VERSION = "M-02.1-materiality-integration-ledger"
WORKERS_DEFAULT = 18

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
TEXT_EXTS = {".md", ".mdx", ".txt", ".json", ".jsonc", ".yaml", ".yml", ".ts", ".tsx", ".css", ".scss"}

EXCLUDE_PARTS = {
    ".git", "node_modules", ".next", "out", "dist", "build", ".turbo",
    ".cache", "coverage", "playwright-report", "test-results", "__pycache__",
    ".prisma_installer_backups"
}

NO_TOUCH_NAMES = {
    "package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "bun.lockb",
    "next.config.mjs", "next.config.js", "wrangler.jsonc", "wrangler.toml"
}

PROTECTED_HINTS = [
    "products/tablet/app/components/pos",
    "products/tablet/app/app/pos",
    "products/tablet/app/app/checkout",
    "products/tablet/app/components/checkout",
    "/pos/",
    "\\pos\\",
    "checkout",
]

SURFACE_ROOTS = [
    {"surface": "chart_lab", "label": "Chart Lab", "port": 3000, "root": "products/chart-lab/app"},
    {"surface": "web_eit", "label": "EIT/Web", "port": 3110, "root": "products/web/app"},
    {"surface": "tablet", "label": "Tablet", "port": 3120, "root": "products/tablet/app"},
    {"surface": "pc", "label": "PC", "port": 3130, "root": "products/pc/app"},
    {"surface": "mobile", "label": "Mobile", "port": 3140, "root": "products/mobile/app"},
    {"surface": "control_center_embedded", "label": "Control Center embedded", "port": 3150, "root": "products/control-center/app"},
    {"surface": "control_center_separate", "label": "PRISMA Control Center separado", "port": 3150, "root": "prisma-control-center"},
]

OUTPUT_RELATIVE_PATHS = [
    "tools/prisma-surface-visual-governor/inventory/materiality-integration-ledger.generated.json",
    "tools/prisma-surface-visual-governor/inventory/materiality-asset-candidates.generated.csv",
    "tools/prisma-surface-visual-governor/contracts/surface-atmosphere-allowlist.generated.json",
    "tools/prisma-surface-visual-governor/contracts/surface-route-budgets.generated.json",
    "tools/prisma-surface-visual-governor/docs/MATERIALITY_INTEGRATION_LEDGER_GENERATED.md",
    "tools/prisma-surface-visual-governor/docs/MATERIALITY_INTEGRATION_DO_NOT_FORGET_GENERATED.md",
]

FAMILY_RULES = [
    {
        "id": "pc_graphite_cloudglass_stack",
        "label": "PC Graphite Cloudglass Stack",
        "match": ["01_prisma_base_graphite_cloudglass", "02_prisma_fractures_light_overlay", "03_prisma_mist_dust_overlay", "graphite", "fracture", "mist_dust"],
        "allowed": ["pc", "chart_lab", "control_center_separate", "control_center_embedded"],
        "blocked": ["pos_checkout"],
        "notes": "Casa matriz Cloudglass: base graphite + fracture/light + mist/dust.",
    },
    {
        "id": "storm_graphite_dark_showcase",
        "label": "Storm / Graphite Dark Showcase",
        "match": ["storm", "obsidian", "aurora", "slate", "storm-cloud", "storm-glass", "obsidian-cloud", "aurora-slate"],
        "allowed": ["pc_reference", "chart_lab", "control_center_separate", "control_center_embedded", "visual_os"],
        "blocked": ["tablet_productive", "pos_checkout", "checkout", "web_eit_public"],
        "notes": "Premium oscuro para showcase, Visual OS, Chart Lab y PC referencia. No POS/Checkout.",
    },
    {
        "id": "liquid_vapor_reference",
        "label": "Liquid / Vapor Reference",
        "match": ["liquid", "vapor", "smoke", "hydro", "fluid"],
        "allowed": ["chart_lab", "control_center_separate", "control_center_embedded", "visual_os", "pc_reference"],
        "blocked": ["tablet_productive", "pos_checkout", "checkout", "dense_tables"],
        "notes": "Familia wow con humo/líquido. Entra con route budget y bozal.",
    },
    {
        "id": "tablet_light_soft_clouds",
        "label": "Tablet Light Soft Clouds",
        "match": ["tablet-soft-gray-clouds", "soft-gray", "light-cloud", "tablet-light", "soft_cloud", "soft-cloud"],
        "allowed": ["tablet_productive", "tablet_settings", "tablet_sync", "mobile"],
        "blocked": ["pc_dark_showcase"],
        "notes": "Light-first para Tablet productiva. POS sólo con gate explícito.",
    },
    {
        "id": "mobile_thin_mist",
        "label": "Mobile Thin Mist",
        "match": ["mobile", "thin-mist", "thin_mist", "mist-mobile"],
        "allowed": ["mobile"],
        "blocked": ["pos_checkout"],
        "notes": "Bajo ruido, battery-friendly, reduced motion.",
    },
    {
        "id": "web_eit_sober",
        "label": "Web/EIT Public Sober",
        "match": ["sober", "public", "eit", "web-public", "public-sober"],
        "allowed": ["web_eit_public"],
        "blocked": ["showcase", "demo"],
        "notes": "Público sobrio. Nada de exceso visual.",
    },
    {
        "id": "control_center_visual_governance",
        "label": "Control Center / Visual Governance",
        "match": ["control-center", "control_center", "prismo", "visual-os", "visual_os", "governance"],
        "allowed": ["control_center_separate", "control_center_embedded", "visual_os"],
        "blocked": ["pos_checkout"],
        "notes": "Gobierno, salud, evidencia y command surfaces.",
    },
]

ROUTE_BUDGETS = {
    "pc_dashboard_hoy": {
        "surface": "pc",
        "goal": "Centro de decisiones premium.",
        "allowed_families": ["pc_graphite_cloudglass_stack", "storm_graphite_dark_showcase"],
        "blocked_families": ["liquid_vapor_reference_on_dense_tables"],
        "background": "high",
        "glass": "medium-high",
        "rim": "signature_only",
        "glow": "1 strong / 3 medium",
        "motion": "ambient + micro",
        "webgl": "none unless demo",
    },
    "pc_settings_license": {
        "surface": "pc",
        "goal": "Claridad de configuración.",
        "allowed_families": ["pc_graphite_cloudglass_stack"],
        "background": "low-medium",
        "glass": "low-medium",
        "rim": "R0-R2",
        "glow": "focus/action only",
        "motion": "micro",
        "webgl": "none",
    },
    "chart_lab": {
        "surface": "chart_lab",
        "goal": "Taller visual / Power Studio.",
        "allowed_families": ["storm_graphite_dark_showcase", "liquid_vapor_reference", "pc_graphite_cloudglass_stack"],
        "background": "high",
        "glass": "medium",
        "rim": "R1-R4",
        "glow": "chart dependent",
        "motion": "ambient + chart motion",
        "webgl": "optional gated",
    },
    "tablet_productive": {
        "surface": "tablet",
        "goal": "Touch claro, light-first.",
        "allowed_families": ["tablet_light_soft_clouds"],
        "blocked_families": ["storm_graphite_dark_showcase", "liquid_vapor_reference"],
        "background": "light / low noise",
        "glass": "low-medium",
        "rim": "R0-R2",
        "glow": "semantic only",
        "motion": "micro",
        "webgl": "none",
    },
    "pos_checkout": {
        "surface": "tablet_pos_checkout",
        "goal": "Vender rápido y tocar fácil.",
        "allowed_families": ["tablet_light_soft_clouds_only_if_gate_passes"],
        "blocked_families": ["storm_graphite_dark_showcase", "liquid_vapor_reference", "pc_graphite_cloudglass_stack"],
        "background": "light-only",
        "glass": "low",
        "rim": "R0-R1",
        "glow": "semantic only",
        "motion": "micro/reduced",
        "webgl": "forbidden",
        "extra_bans": ["Pixi", "heavy blur", "dark storm", "vapor competing with products/payment"],
    },
    "mobile": {
        "surface": "mobile",
        "goal": "Supervisor ligero.",
        "allowed_families": ["mobile_thin_mist", "tablet_light_soft_clouds"],
        "background": "low noise",
        "glass": "low",
        "rim": "R0-R1",
        "glow": "semantic only",
        "motion": "reduced/micro",
        "webgl": "none",
    },
    "web_eit": {
        "surface": "web_eit",
        "goal": "Público sobrio.",
        "allowed_families": ["web_eit_sober"],
        "background": "low",
        "glass": "low",
        "rim": "R0-R1",
        "glow": "minimal",
        "motion": "minimal",
        "webgl": "none",
    },
    "control_center": {
        "surface": "control_center",
        "goal": "Gobierno, salud y evidencia premium.",
        "allowed_families": ["storm_graphite_dark_showcase", "pc_graphite_cloudglass_stack", "control_center_visual_governance"],
        "conditional_families": ["liquid_vapor_reference only in showcase/reference zones"],
        "background": "medium-high",
        "glass": "medium-high",
        "rim": "R1-R4 controlled",
        "glow": "semantic/evidence/live only",
        "motion": "ambient + micro",
        "webgl": "demo/reference only",
    },
}

def iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_PARTS for part in path.parts)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run_git(root: Path, args: list[str]) -> dict:
    try:
        p = subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        return {"ok": p.returncode == 0, "code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as e:
        return {"ok": False, "code": -1, "stdout": "", "stderr": str(e)}

def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({k for row in rows for k in row.keys()}) if rows else ["empty"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for row in rows:
            w.writerow(row)

def zip_dir(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in src.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src).as_posix())

def find_latest_materiality_audit_zip(out_dir: Path) -> Path | None:
    zips = sorted(
        out_dir.glob("PRISMA_MATERIALITY_CATALOG_AUDIT_RESULT_*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return zips[0] if zips else None

def inspect_zip(zip_path: Path | None) -> dict:
    if not zip_path or not zip_path.exists():
        return {
            "found": False,
            "zip_path": "",
            "entries": 0,
            "image_entries": [],
            "index_entries": [],
            "json_entries": [],
            "md_entries": [],
        }

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

    return {
        "found": True,
        "zip_path": str(zip_path),
        "entries": len(names),
        "image_entries": [n for n in names if Path(n).suffix.lower() in IMAGE_EXTS][:500],
        "index_entries": [n for n in names if "index" in n.lower() or "csv" in n.lower()][:100],
        "json_entries": [n for n in names if n.lower().endswith(".json")][:100],
        "md_entries": [n for n in names if n.lower().endswith((".md", ".txt"))][:100],
    }

def classify_asset(relative_path: str) -> tuple[str, str, list[str], list[str], str]:
    low = relative_path.lower().replace("\\", "/")
    best = None
    best_hits = []

    for rule in FAMILY_RULES:
        hits = [token for token in rule["match"] if token.lower() in low]
        if hits and (best is None or len(hits) > len(best_hits)):
            best = rule
            best_hits = hits

    if not best:
        return (
            "unclassified_visual_asset",
            "Unclassified visual asset",
            [],
            [],
            "Asset visual detectado, pero requiere decisión humana antes de usarse.",
        )

    return (
        best["id"],
        best["label"],
        best["allowed"],
        best["blocked"],
        best["notes"] + " Hits: " + ", ".join(best_hits),
    )

def scan_asset_one(root: Path, path: Path) -> dict:
    r = rel(root, path)
    family_id, family_label, allowed, blocked, notes = classify_asset(r)
    return {
        "relative_path": r,
        "filename": path.name,
        "extension": path.suffix.lower(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "family_id": family_id,
        "family_label": family_label,
        "allowed_surfaces": "|".join(allowed),
        "blocked_surfaces": "|".join(blocked),
        "notes": notes,
    }

def scan_assets(root: Path, workers: int) -> list[dict]:
    candidates = [
        p for p in root.rglob("*")
        if p.is_file()
        and not is_excluded(p)
        and p.suffix.lower() in IMAGE_EXTS
    ]

    rows = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futures = [ex.submit(scan_asset_one, root, p) for p in candidates]
        for fut in as_completed(futures):
            rows.append(fut.result())

    return sorted(rows, key=lambda x: (x["family_id"], x["relative_path"].lower()))

def detect_routes(root: Path) -> list[dict]:
    rows = []
    for s in SURFACE_ROOTS:
        sr = root / s["root"]
        if not sr.exists():
            rows.append({
                "surface": s["surface"],
                "label": s["label"],
                "port": s["port"],
                "route": "",
                "relative_path": s["root"],
                "status": "SURFACE_ROOT_MISSING",
            })
            continue

        app_root = sr / "app"
        if not app_root.exists():
            app_root = sr

        for p in sr.rglob("*"):
            if not p.is_file() or is_excluded(p):
                continue
            if p.name not in {"page.tsx", "layout.tsx"}:
                continue
            try:
                rp = p.relative_to(app_root).as_posix()
            except Exception:
                rp = p.relative_to(sr).as_posix()

            route = "/"
            if rp.endswith("/page.tsx"):
                route = "/" + rp[:-len("/page.tsx")].strip("/")
            elif rp == "page.tsx":
                route = "/"
            elif rp.endswith("/layout.tsx"):
                route = "/" + rp[:-len("/layout.tsx")].strip("/")
            elif rp == "layout.tsx":
                route = "/"

            rows.append({
                "surface": s["surface"],
                "label": s["label"],
                "port": s["port"],
                "route": route,
                "relative_path": rel(root, p),
                "status": "ROUTE_FILE_DETECTED",
            })
    return sorted(rows, key=lambda x: (x["surface"], x["route"], x["relative_path"]))

def collect_hashes(root: Path, predicate) -> dict[str, str]:
    out = {}
    for p in root.rglob("*"):
        if not p.is_file() or is_excluded(p):
            continue
        r = rel(root, p)
        if predicate(r, p):
            try:
                out[r] = sha256_file(p)
            except Exception:
                pass
    return out

def is_no_touch(r: str, p: Path) -> bool:
    low = r.lower()
    return p.name in NO_TOUCH_NAMES or "prisma/schema.prisma" in low or "deploy" in low and p.suffix.lower() in {".json", ".jsonc", ".toml", ".yml", ".yaml"}

def is_protected(r: str, p: Path) -> bool:
    low = r.lower().replace("\\", "/")
    return any(h.replace("\\", "/").lower() in low for h in PROTECTED_HINTS)

def backup_outputs(root: Path, stage: Path, backup_zip: Path) -> dict:
    backup_stage = stage / "backup_before"
    manifest = {
        "created_at": iso(),
        "files": [],
    }

    for r in OUTPUT_RELATIVE_PATHS:
        src = root / r
        entry = {"relative_path": r, "existed": src.exists(), "sha256": ""}
        if src.exists() and src.is_file():
            entry["sha256"] = sha256_file(src)
            dst = backup_stage / r
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        manifest["files"].append(entry)

    write_json(backup_stage / "backup_manifest.json", manifest)
    zip_dir(backup_stage, backup_zip)
    return manifest

def restore_outputs(root: Path, backup_zip: Path, manifest: dict):
    temp = root / ".prisma_surface_governor_m02_restore_tmp"
    if temp.exists():
        shutil.rmtree(temp, ignore_errors=True)
    temp.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(backup_zip, "r") as z:
        z.extractall(temp)

    for item in manifest.get("files", []):
        r = item["relative_path"]
        dst = root / r
        src = temp / r
        if item.get("existed"):
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        else:
            if dst.exists():
                dst.unlink()

    shutil.rmtree(temp, ignore_errors=True)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--workers", type=int, default=WORKERS_DEFAULT)
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    workers = max(1, int(args.workers))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stage = out_dir / f"PRISMA_M02_MATERIALITY_INTEGRATION_LEDGER_WORK_{stamp}"
    result_zip = out_dir / f"PRISMA_M02_MATERIALITY_INTEGRATION_LEDGER_RESULT_{stamp}.zip"
    backup_zip = out_dir / f"PRISMA_M02_MATERIALITY_INTEGRATION_LEDGER_BACKUP_{stamp}.zip"
    log_path = stage / "install.log"

    def log(msg: str):
        stage.mkdir(parents=True, exist_ok=True)
        line = f"[{iso()}] {msg}"
        print(line)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    backup_manifest = {}
    rollback_performed = False

    try:
        if not root.exists():
            raise RuntimeError(f"Repo no existe: {root}")
        out_dir.mkdir(parents=True, exist_ok=True)
        stage.mkdir(parents=True, exist_ok=True)

        log(f"START {ENGINE_VERSION}")
        log(f"Root={root}")
        log(f"Workers={workers}")

        git_before = run_git(root, ["status", "--short"])
        write_json(stage / "evidence/git_status_before.json", git_before)

        protected_before = collect_hashes(root, is_protected)
        no_touch_before = collect_hashes(root, is_no_touch)

        backup_manifest = backup_outputs(root, stage, backup_zip)
        log(f"Backup ZIP={backup_zip}")

        audit_zip = find_latest_materiality_audit_zip(out_dir)
        audit_inspection = inspect_zip(audit_zip)
        write_json(stage / "evidence/materiality_audit_zip_inspection.json", audit_inspection)

        assets = scan_assets(root, workers)
        routes = detect_routes(root)

        family_counts = {}
        for a in assets:
            family_counts[a["family_id"]] = family_counts.get(a["family_id"], 0) + 1

        allowlist = {
            "schema": "prisma.surface.visual_governor.surface_atmosphere_allowlist",
            "version": "M-02.generated",
            "created_at": iso(),
            "rule": "Las imágenes reales son core del Atmosphere Engine. Ninguna familia entra a una ruta sin budget/gate.",
            "families": [
                {
                    "id": rule["id"],
                    "label": rule["label"],
                    "allowed_surfaces": rule["allowed"],
                    "blocked_surfaces": rule["blocked"],
                    "notes": rule["notes"],
                    "detected_asset_count": family_counts.get(rule["id"], 0),
                }
                for rule in FAMILY_RULES
            ],
            "unclassified_visual_asset_count": family_counts.get("unclassified_visual_asset", 0),
            "hard_bans": {
                "pos_checkout": [
                    "storm_graphite_dark_showcase",
                    "liquid_vapor_reference",
                    "webgl",
                    "pixi",
                    "heavy_blur",
                    "dark_storm",
                    "background_competes_with_products_or_payment",
                ],
                "tablet_productive": [
                    "default_dark_theme",
                    "storm_vapor_default",
                    "webgl",
                    "heavy_blur",
                ],
            },
        }

        ledger = {
            "schema": "prisma.surface.visual_governor.materiality_integration_ledger",
            "version": ENGINE_VERSION,
            "created_at": iso(),
            "repo": str(root),
            "purpose": "Integra el plan pasado de imágenes/presets con el Governor actual para que el rollout visual no se aplique a lo pendejo.",
            "principle": "Plan viejo = qué estética va dónde. Governor actual = cómo se aplica, audita y bloquea por ruta.",
            "materiality_audit_zip": audit_inspection,
            "surface_roots": SURFACE_ROOTS,
            "asset_families": allowlist["families"],
            "route_budgets": ROUTE_BUDGETS,
            "routes_detected_count": len([r for r in routes if r["status"] == "ROUTE_FILE_DETECTED"]),
            "assets_detected_count": len(assets),
            "asset_family_counts": family_counts,
            "rollout_order": [
                {
                    "order": 1,
                    "pilot": "M-03",
                    "target": "Materiality Preview Board",
                    "mode": "read-only / generated preview",
                    "reason": "Ver assets reales por familia antes de aplicar UI.",
                },
                {
                    "order": 2,
                    "pilot": "M-04",
                    "target": "Control Center / Visual OS alignment",
                    "mode": "separate repo lane",
                    "reason": "Pantallas premium de gobierno/evidencia pueden usar familias fuertes.",
                },
                {
                    "order": 3,
                    "pilot": "M-05",
                    "target": "PC Dashboard/Hoy",
                    "mode": "visual upgrade with budgets",
                    "reason": "Cloudglass executive con Graphite stack.",
                },
                {
                    "order": 4,
                    "pilot": "M-06",
                    "target": "Chart Lab",
                    "mode": "studio visual / Power Studio",
                    "reason": "Chart Lab es taller, puede usar Storm/Liquid con gates.",
                },
                {
                    "order": 5,
                    "pilot": "M-07",
                    "target": "Tablet productive",
                    "mode": "light-first correction",
                    "reason": "Tablet debe quedar clara, táctil y luminosa.",
                },
                {
                    "order": 6,
                    "pilot": "M-08",
                    "target": "Mobile / Web EIT",
                    "mode": "thin/sober",
                    "reason": "Bajo ruido y bajo presupuesto visual.",
                },
                {
                    "order": 7,
                    "pilot": "M-09",
                    "target": "POS/Checkout",
                    "mode": "gate only",
                    "reason": "Sólo light-safe con verificación explícita.",
                },
            ],
        }

        budgets = {
            "schema": "prisma.surface.visual_governor.surface_route_budgets",
            "version": "M-02.generated",
            "created_at": iso(),
            "budgets": ROUTE_BUDGETS,
        }

        output_json = root / OUTPUT_RELATIVE_PATHS[0]
        output_csv = root / OUTPUT_RELATIVE_PATHS[1]
        output_allowlist = root / OUTPUT_RELATIVE_PATHS[2]
        output_budgets = root / OUTPUT_RELATIVE_PATHS[3]
        output_md = root / OUTPUT_RELATIVE_PATHS[4]
        output_forget = root / OUTPUT_RELATIVE_PATHS[5]

        write_json(output_json, ledger)
        write_csv(output_csv, assets)
        write_json(output_allowlist, allowlist)
        write_json(output_budgets, budgets)

        md = []
        md.append("# PRISMA M-02 · Materiality Integration Ledger")
        md.append("")
        md.append(f"- Generated: `{iso()}`")
        md.append(f"- Engine: `{ENGINE_VERSION}`")
        md.append(f"- Repo: `{root}`")
        md.append(f"- Materiality audit ZIP: `{audit_inspection.get('zip_path') or 'NOT_FOUND'}`")
        md.append(f"- Assets visuales detectados: **{len(assets)}**")
        md.append(f"- Rutas detectadas: **{ledger['routes_detected_count']}**")
        md.append("")
        md.append("## Qué integra")
        md.append("")
        md.append("Este ledger une el plan pasado de imágenes/presets con el Surface Visual Governor actual.")
        md.append("")
        md.append("- El set de imágenes se convierte en familias del Atmosphere Engine.")
        md.append("- El Ultra Codex se usa como catálogo paramétrico.")
        md.append("- La receta Cloudglass se vuelve budgets por ruta.")
        md.append("- POS/Checkout quedan bloqueados contra familias visuales peligrosas.")
        md.append("- Tablet productiva queda light-first.")
        md.append("")
        md.append("## Familias visuales")
        md.append("")
        md.append("| Familia | Assets | Permitido | Bloqueado | Nota |")
        md.append("|---|---:|---|---|---|")
        for fam in allowlist["families"]:
            md.append(f"| `{fam['id']}` | {fam['detected_asset_count']} | `{', '.join(fam['allowed_surfaces'])}` | `{', '.join(fam['blocked_surfaces'])}` | {fam['notes']} |")
        md.append(f"| `unclassified_visual_asset` | {allowlist['unclassified_visual_asset_count']} | `requires_review` | `all_until_classified` | Requiere decisión humana antes de uso. |")
        md.append("")
        md.append("## Budgets por objetivo")
        md.append("")
        md.append("| Budget | Surface | Goal | Background | Glass | Rim | Motion | WebGL |")
        md.append("|---|---|---|---|---|---|---|---|")
        for key, b in ROUTE_BUDGETS.items():
            md.append(f"| `{key}` | `{b.get('surface','')}` | {b.get('goal','')} | `{b.get('background','')}` | `{b.get('glass','')}` | `{b.get('rim','')}` | `{b.get('motion','')}` | `{b.get('webgl','')}` |")
        md.append("")
        md.append("## Siguiente paso")
        md.append("")
        md.append("M-03 debe generar un Preview Board/contact sheet de assets reales por familia y superficie antes de aplicar más UI.")
        write_text(output_md, "\n".join(md))

        forget = []
        forget.append("# PRISMA M-02 · DO NOT FORGET")
        forget.append("")
        forget.append("- No reemplazar imágenes reales con gradientes tristes.")
        forget.append("- Las imágenes reales son parte del Atmosphere Engine.")
        forget.append("- Storm/Liquid/Vapor son familias premium, no default productivo.")
        forget.append("- Tablet productiva es light-first.")
        forget.append("- POS/Checkout sólo light-safe y con gate.")
        forget.append("- Chart Lab es taller visual, no consumidor productivo normal.")
        forget.append("- Control Center separado va por carril propio.")
        forget.append("- Route Budget Enforcer decide qué entra completo, con bozal o no entra.")
        write_text(output_forget, "\n".join(forget))

        write_csv(stage / "indexes/materiality_asset_candidates.generated.csv", assets)
        write_json(stage / "indexes/materiality_integration_ledger.generated.json", ledger)
        write_json(stage / "indexes/surface_atmosphere_allowlist.generated.json", allowlist)
        write_json(stage / "indexes/surface_route_budgets.generated.json", budgets)
        write_csv(stage / "indexes/routes_detected.csv", routes)

        protected_after = collect_hashes(root, is_protected)
        no_touch_after = collect_hashes(root, is_no_touch)
        git_after = run_git(root, ["status", "--short"])
        write_json(stage / "evidence/git_status_after.json", git_after)

        changed_outputs = []
        for r in OUTPUT_RELATIVE_PATHS:
            p = root / r
            if p.exists():
                changed_outputs.append({
                    "relative_path": r,
                    "bytes": p.stat().st_size,
                    "sha256": sha256_file(p),
                })

        verifier = {
            "status": "PASS",
            "engine_version": ENGINE_VERSION,
            "checks": {
                "toolbox_exists": (root / "tools/prisma-surface-visual-governor").exists(),
                "materiality_audit_zip_found": bool(audit_inspection.get("found")),
                "assets_detected": len(assets),
                "routes_detected": ledger["routes_detected_count"],
                "outputs_written": len(changed_outputs),
                "all_expected_outputs_exist": all((root / r).exists() for r in OUTPUT_RELATIVE_PATHS),
                "protected_pos_checkout_hashes_unchanged": protected_before == protected_after,
                "no_touch_hashes_unchanged": no_touch_before == no_touch_after,
                "db_touched": False,
                "dependencies_touched": False,
                "package_lock_touched": False,
                "deploy_touched": False,
                "ui_product_files_touched": False,
            },
            "warnings": [],
        }

        if not audit_inspection.get("found"):
            verifier["warnings"].append("No encontré PRISMA_MATERIALITY_CATALOG_AUDIT_RESULT_*.zip en <LOCAL_PATH> Ledger generado desde repo/assets solamente.")
        if len(assets) == 0:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No assets visuales detectados.")
        if protected_before != protected_after:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("Protected POS/Checkout hashes changed.")
        if no_touch_before != no_touch_after:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No-touch files changed.")
        if not verifier["checks"]["all_expected_outputs_exist"]:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No se generaron todos los outputs esperados.")

        if verifier["status"] != "PASS":
            restore_outputs(root, backup_zip, backup_manifest)
            rollback_performed = True

        write_json(stage / "verifier.json", verifier)
        write_json(stage / "protected_hashes.before.json", protected_before)
        write_json(stage / "protected_hashes.after.json", protected_after)
        write_json(stage / "no_touch_hashes.before.json", no_touch_before)
        write_json(stage / "no_touch_hashes.after.json", no_touch_after)

        report = []
        report.append("# PRISMA M-02 · Materiality Integration Ledger Result")
        report.append("")
        report.append(f"- Generated: `{iso()}`")
        report.append(f"- Status: **{verifier['status']}**")
        report.append(f"- Rollback performed: `{rollback_performed}`")
        report.append(f"- Backup ZIP: `{backup_zip}`")
        report.append(f"- Assets detected: **{len(assets)}**")
        report.append(f"- Routes detected: **{ledger['routes_detected_count']}**")
        report.append("")
        report.append("## Outputs")
        report.append("")
        for row in changed_outputs:
            report.append(f"- `{row['relative_path']}`")
        report.append("")
        report.append("## Family counts")
        report.append("")
        for k, v in sorted(family_counts.items()):
            report.append(f"- `{k}`: **{v}**")
        report.append("")
        report.append("## Next")
        report.append("")
        report.append("M-03 · Materiality Preview Board / contact sheet de assets reales por familia y superficie.")
        write_text(stage / "M02_MATERIALITY_INTEGRATION_LEDGER_REPORT.md", "\n".join(report))

        receipt = {
            "pilot": "M-02",
            "name": "Materiality Integration Ledger",
            "status": verifier["status"],
            "created_at": iso(),
            "repo": str(root),
            "result_zip": str(result_zip),
            "backup_zip": str(backup_zip),
            "rollback_performed": rollback_performed,
            "outputs": OUTPUT_RELATIVE_PATHS,
            "assets_detected": len(assets),
            "routes_detected": ledger["routes_detected_count"],
            "read_only_product_ui": True,
            "toolbox_files_written": True,
            "db_touched": False,
            "dependencies_touched": False,
            "package_lock_touched": False,
            "deploy_touched": False,
            "pos_checkout_touched": False,
        }
        write_json(stage / "receipt.json", receipt)
        write_json(stage / "rollback.json", {
            "required": verifier["status"] != "PASS",
            "performed": rollback_performed,
            "backup_zip": str(backup_zip),
            "restored_outputs": OUTPUT_RELATIVE_PATHS if rollback_performed else [],
        })

        zip_dir(stage, result_zip)
        shutil.rmtree(stage, ignore_errors=True)

        print(f"PASS_RESULT_ZIP={result_zip}")
        return 0 if verifier["status"] == "PASS" else 2

    except Exception:
        err = traceback.format_exc()
        try:
            if backup_manifest and backup_zip.exists():
                restore_outputs(root, backup_zip, backup_manifest)
                rollback_performed = True
        except Exception:
            pass

        stage.mkdir(parents=True, exist_ok=True)
        write_text(stage / "FAILURE.txt", err)
        write_json(stage / "receipt.json", {
            "pilot": "M-02",
            "status": "FAIL",
            "created_at": iso(),
            "error": err,
            "rollback_performed": rollback_performed,
            "result_zip": str(result_zip),
            "backup_zip": str(backup_zip),
        })
        write_json(stage / "rollback.json", {
            "required": True,
            "performed": rollback_performed,
            "backup_zip": str(backup_zip),
        })
        try:
            zip_dir(stage, result_zip)
            shutil.rmtree(stage, ignore_errors=True)
        except Exception:
            pass

        print(err)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
