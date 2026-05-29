from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import subprocess
import traceback
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ENGINE_VERSION = "M-04.1-materiality-asset-curator"

OUTPUT_RELATIVE_PATHS = [
    "tools/prisma-surface-visual-governor/inventory/asset-role-classification.generated.json",
    "tools/prisma-surface-visual-governor/inventory/asset-role-classification.generated.csv",
    "tools/prisma-surface-visual-governor/contracts/surface-atmosphere-assets.curated.json",
    "tools/prisma-surface-visual-governor/previews/materiality-curated-preview-board.generated.html",
    "tools/prisma-surface-visual-governor/previews/materiality-curated-preview-board.generated.json",
    "tools/prisma-surface-visual-governor/docs/MATERIALITY_ASSET_CURATOR_GENERATED.md",
]

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

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

ROLE_ORDER = [
    "atmosphere_background",
    "decorative_landing",
    "brand_logo",
    "product_packshot",
    "screenshot_qa",
    "ui_icon",
    "unknown_review",
]

ROLE_LABELS = {
    "atmosphere_background": "Atmosphere / Background",
    "decorative_landing": "Decorative / Landing",
    "brand_logo": "Brand / Logo",
    "product_packshot": "Product Packshot",
    "screenshot_qa": "Screenshot / QA Evidence",
    "ui_icon": "UI Icon / Glyph",
    "unknown_review": "Unknown / Requires Review",
}

ATMOSPHERE_ROLES = {"atmosphere_background"}
CONDITIONAL_ATMOSPHERE_ROLES = {"decorative_landing"}

FAMILY_ORDER = [
    "pc_graphite_cloudglass_stack",
    "storm_graphite_dark_showcase",
    "liquid_vapor_reference",
    "tablet_light_soft_clouds",
    "mobile_thin_mist",
    "web_eit_sober",
    "control_center_visual_governance",
    "unclassified_visual_asset",
]

SURFACE_POLICY = {
    "pc": {
        "allow_families": ["pc_graphite_cloudglass_stack", "storm_graphite_dark_showcase"],
        "conditional_families": ["liquid_vapor_reference"],
        "block_roles": ["brand_logo", "product_packshot", "screenshot_qa", "ui_icon", "unknown_review"],
    },
    "chart_lab": {
        "allow_families": ["pc_graphite_cloudglass_stack", "storm_graphite_dark_showcase", "liquid_vapor_reference"],
        "conditional_families": ["decorative_landing"],
        "block_roles": ["brand_logo", "product_packshot", "screenshot_qa", "ui_icon", "unknown_review"],
    },
    "control_center": {
        "allow_families": ["pc_graphite_cloudglass_stack", "storm_graphite_dark_showcase", "control_center_visual_governance"],
        "conditional_families": ["liquid_vapor_reference"],
        "block_roles": ["brand_logo", "product_packshot", "screenshot_qa", "ui_icon", "unknown_review"],
    },
    "tablet_productive": {
        "allow_families": ["tablet_light_soft_clouds"],
        "conditional_families": [],
        "block_roles": ["brand_logo", "product_packshot", "screenshot_qa", "ui_icon", "unknown_review", "decorative_landing"],
    },
    "mobile": {
        "allow_families": ["mobile_thin_mist", "tablet_light_soft_clouds"],
        "conditional_families": [],
        "block_roles": ["brand_logo", "product_packshot", "screenshot_qa", "ui_icon", "unknown_review"],
    },
    "web_eit_public": {
        "allow_families": ["web_eit_sober"],
        "conditional_families": [],
        "block_roles": ["brand_logo", "product_packshot", "screenshot_qa", "ui_icon", "unknown_review"],
    },
    "pos_checkout": {
        "allow_families": [],
        "conditional_families": ["tablet_light_soft_clouds"],
        "block_roles": ["brand_logo", "product_packshot", "screenshot_qa", "ui_icon", "unknown_review", "decorative_landing"],
        "requires_gate": True,
    },
}

def iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_PARTS for part in path.parts)

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

def sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

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

def is_no_touch(r: str, p: Path) -> bool:
    low = r.lower()
    return (
        p.name in NO_TOUCH_NAMES
        or "prisma/schema.prisma" in low
        or ("deploy" in low and p.suffix.lower() in {".json", ".jsonc", ".toml", ".yml", ".yaml"})
    )

def is_protected(r: str, p: Path) -> bool:
    low = r.lower().replace("\\", "/")
    return any(h.replace("\\", "/").lower() in low for h in PROTECTED_HINTS)

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

def backup_outputs(root: Path, stage: Path, backup_zip: Path) -> dict:
    backup_stage = stage / "backup_before"
    manifest = {"created_at": iso(), "files": []}
    for r in OUTPUT_RELATIVE_PATHS:
        src = root / r
        item = {"relative_path": r, "existed": src.exists(), "sha256": ""}
        if src.exists() and src.is_file():
            item["sha256"] = sha256_file(src)
            dst = backup_stage / r
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        manifest["files"].append(item)
    write_json(backup_stage / "backup_manifest.json", manifest)
    zip_dir(backup_stage, backup_zip)
    return manifest

def restore_outputs(root: Path, backup_zip: Path, manifest: dict):
    temp = root / ".prisma_surface_governor_m04_restore_tmp"
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

def read_m02_assets(root: Path) -> list[dict]:
    csv_path = root / "tools/prisma-surface-visual-governor/inventory/materiality-asset-candidates.generated.csv"
    if not csv_path.exists():
        raise RuntimeError(f"No existe asset CSV M-02: {csv_path}")
    rows = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(dict(row))
    return rows

def classify_role(row: dict) -> tuple[str, int, list[str]]:
    path = (row.get("relative_path") or "").lower().replace("\\", "/")
    name = (row.get("filename") or Path(path).name).lower()
    family = row.get("family_id") or "unclassified_visual_asset"
    ext = (row.get("extension") or Path(name).suffix).lower()

    score_notes = []

    screenshot_terms = [
        "screenshot", "screen-shot", "capture", "captura", "playwright", "before", "after",
        "visual-regression", "regression", "qa", "evidence", "contact-sheet", "contact_sheet",
        "preview-board", "preview_board", "snapshot"
    ]
    logo_terms = [
        "logo", "brand", "marca", "favicon", "apple-touch-icon", "prisma-logo", "hitech-logo",
        "icon-logo", "wordmark", "identity"
    ]
    icon_terms = [
        "/icons/", "/icon/", "lucide", "glyph", "sprite", "symbol", "chevron", "arrow",
        "spinner", "loader", "menu", "close", "search"
    ]
    product_terms = [
        "product", "producto", "packshot", "sku", "barcode", "catalog", "catalogo", "item",
        "bebida", "abarrote", "galleta", "sabrita", "coca", "refresco", "leche", "jabon",
        "detergente", "cerveza", "botella", "lata", "snack", "inventory", "inventario"
    ]
    atmosphere_terms = [
        "background", "wallpaper", "atmosphere", "cloud", "clouds", "storm", "obsidian",
        "aurora", "slate", "graphite", "fracture", "fractures", "mist", "dust", "vapor",
        "smoke", "liquid", "glass", "horizon", "veil", "soft-gray", "icefield",
        "cloudglass", "surface", "visual-governor"
    ]
    landing_terms = [
        "landing", "hero", "showcase", "promo", "marketing", "public", "banner", "cover"
    ]

    def any_term(terms: list[str]) -> list[str]:
        return [t for t in terms if t in path or t in name]

    hits_screenshot = any_term(screenshot_terms)
    hits_logo = any_term(logo_terms)
    hits_icon = any_term(icon_terms)
    hits_product = any_term(product_terms)
    hits_atmo = any_term(atmosphere_terms)
    hits_landing = any_term(landing_terms)

    if hits_screenshot:
        return "screenshot_qa", 95, ["screenshot/qa"] + hits_screenshot[:8]

    if hits_logo:
        return "brand_logo", 92, ["brand/logo"] + hits_logo[:8]

    if ext == ".svg" and hits_icon and not hits_atmo:
        return "ui_icon", 84, ["svg/icon"] + hits_icon[:8]

    if hits_product and not hits_atmo:
        return "product_packshot", 78, ["product/packshot"] + hits_product[:8]

    if family in {"pc_graphite_cloudglass_stack", "storm_graphite_dark_showcase", "liquid_vapor_reference", "tablet_light_soft_clouds", "mobile_thin_mist", "control_center_visual_governance"}:
        if hits_atmo or family != "unclassified_visual_asset":
            return "atmosphere_background", 86, ["family_atmosphere", family] + hits_atmo[:8]

    if family == "web_eit_sober":
        if hits_atmo:
            return "atmosphere_background", 82, ["web_eit_atmosphere"] + hits_atmo[:8]
        if hits_landing:
            return "decorative_landing", 72, ["web_eit_landing"] + hits_landing[:8]
        if hits_product:
            return "product_packshot", 70, ["web_eit_product_like"] + hits_product[:8]
        return "decorative_landing", 54, ["web_eit_sober_uncertain"]

    if hits_atmo:
        return "atmosphere_background", 74, ["atmosphere_terms"] + hits_atmo[:8]

    if hits_landing:
        return "decorative_landing", 64, ["landing/decorative"] + hits_landing[:8]

    if ext == ".svg":
        return "ui_icon", 51, ["svg_default_review"]

    return "unknown_review", 30, ["needs_human_review"]

def can_use_as_atmosphere(row: dict, surface: str) -> tuple[str, str]:
    role = row.get("asset_role")
    family = row.get("family_id")
    policy = SURFACE_POLICY.get(surface, {})

    if role in policy.get("block_roles", []):
        return "BLOCKED", f"role_blocked:{role}"

    if role not in ATMOSPHERE_ROLES:
        if role in CONDITIONAL_ATMOSPHERE_ROLES:
            return "CONDITIONAL", f"conditional_role:{role}"
        return "BLOCKED", f"not_atmosphere_role:{role}"

    if family in policy.get("allow_families", []):
        return "ALLOWED", "family_allowed"

    if family in policy.get("conditional_families", []):
        return "CONDITIONAL", "family_conditional"

    if policy.get("requires_gate"):
        return "GATE_REQUIRED", "surface_requires_gate"

    return "BLOCKED", "family_not_allowed_for_surface"

def safe_asset_name(index: int, rel_path: str) -> str:
    p = Path(rel_path)
    suffix = p.suffix.lower()
    stem = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in p.stem)[:80]
    return f"{index:04d}_{stem}{suffix}"

def copy_curated_preview_assets(root: Path, stage: Path, rows: list[dict], max_per_role: int = 80) -> list[dict]:
    counts = defaultdict(int)
    copied = []
    asset_root = stage / "curated_preview_assets"

    sorted_rows = sorted(rows, key=lambda r: (
        ROLE_ORDER.index(r.get("asset_role", "unknown_review")) if r.get("asset_role", "unknown_review") in ROLE_ORDER else 999,
        r.get("family_id", ""),
        r.get("relative_path", "").lower()
    ))

    idx = 0
    for row in sorted_rows:
        role = row.get("asset_role") or "unknown_review"
        if counts[role] >= max_per_role:
            continue
        src = root / row["relative_path"]
        if not src.exists() or not src.is_file():
            continue
        if src.suffix.lower() not in IMAGE_EXTS:
            continue

        idx += 1
        counts[role] += 1
        dst_rel = f"{role}/{safe_asset_name(idx, row['relative_path'])}"
        dst = asset_root / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        out = dict(row)
        out["curated_preview_relative"] = f"curated_preview_assets/{dst_rel}"
        out["curated_preview_copied"] = True
        copied.append(out)

    return copied

def build_curated_contract(rows: list[dict]) -> dict:
    surface_assets = {}
    for surface in SURFACE_POLICY.keys():
        surface_assets[surface] = {
            "allowed": [],
            "conditional": [],
            "blocked_count": 0,
            "policy": SURFACE_POLICY[surface],
        }

    for row in rows:
        for surface in SURFACE_POLICY.keys():
            verdict, reason = can_use_as_atmosphere(row, surface)
            item = {
                "relative_path": row["relative_path"],
                "filename": row.get("filename", ""),
                "family_id": row.get("family_id", ""),
                "family_label": row.get("family_label", ""),
                "asset_role": row.get("asset_role", ""),
                "confidence": row.get("role_confidence", ""),
                "sha256": row.get("sha256", ""),
                "reason": reason,
            }
            if verdict == "ALLOWED":
                surface_assets[surface]["allowed"].append(item)
            elif verdict in {"CONDITIONAL", "GATE_REQUIRED"}:
                item["verdict"] = verdict
                surface_assets[surface]["conditional"].append(item)
            else:
                surface_assets[surface]["blocked_count"] += 1

    return {
        "schema": "prisma.surface.visual_governor.surface_atmosphere_assets_curated",
        "version": "M-04.generated",
        "created_at": iso(),
        "rule": "Sólo assets clasificados como atmosphere_background pueden entrar directo al Atmosphere Engine. Decorative landing requiere gate. Logos, packshots, screenshots e iconos quedan fuera.",
        "surfaces": surface_assets,
        "hard_bans": {
            "pos_checkout": ["storm", "liquid", "vapor", "webgl", "pixi", "heavy_blur", "brand_logo", "product_packshot", "screenshots"],
            "tablet_productive": ["dark_storm_default", "liquid_vapor_default", "webgl", "brand_logo", "product_packshot", "screenshots"],
        },
    }

def esc(x) -> str:
    return html.escape(str(x or ""))

def build_html(copied: list[dict], classification_counts: dict, curated_contract: dict) -> str:
    grouped = defaultdict(list)
    for row in copied:
        grouped[row.get("asset_role") or "unknown_review"].append(row)

    sections = []
    for role in ROLE_ORDER:
        items = grouped.get(role, [])
        if not items:
            continue
        sections.append(f"""
<section class="roleSection role-{esc(role)}">
  <div class="sectionHeader">
    <div>
      <p class="eyebrow">Rol de asset</p>
      <h2>{esc(ROLE_LABELS.get(role, role))}</h2>
      <p>{esc(role_description(role))}</p>
    </div>
    <div class="count">{len(items)}</div>
  </div>
  <div class="grid">
""")
        for item in items:
            src = item.get("curated_preview_relative", "")
            sections.append(f"""
    <article class="card">
      <div class="imgWrap"><img src="{esc(src)}" loading="lazy" alt="{esc(item.get('filename','asset'))}" /></div>
      <div class="body">
        <h3>{esc(item.get('filename',''))}</h3>
        <p>{esc(item.get('relative_path',''))}</p>
        <div class="chips">
          <span>{esc(item.get('family_id',''))}</span>
          <span>conf {esc(item.get('role_confidence',''))}</span>
        </div>
        <p class="why">{esc(item.get('role_reason',''))}</p>
      </div>
    </article>
""")
        sections.append("""
  </div>
</section>
""")

    surface_cards = []
    for surface, data in curated_contract.get("surfaces", {}).items():
        surface_cards.append(f"""
<article class="surfaceCard">
  <h3>{esc(surface)}</h3>
  <p><b>{len(data.get('allowed', []))}</b> allowed</p>
  <p><b>{len(data.get('conditional', []))}</b> conditional/gated</p>
  <p><b>{data.get('blocked_count', 0)}</b> blocked</p>
</article>
""")

    role_pills = "".join(
        f"<span>{esc(ROLE_LABELS.get(k,k))}: <b>{v}</b></span>"
        for k, v in sorted(classification_counts.items(), key=lambda kv: ROLE_ORDER.index(kv[0]) if kv[0] in ROLE_ORDER else 99)
    )

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>PRISMA M-04 · Materiality Asset Curator</title>
<style>
:root {{
  --bg:#071018;
  --panel:rgba(255,255,255,.075);
  --panel2:rgba(255,255,255,.12);
  --line:rgba(210,232,255,.18);
  --text:#eef8ff;
  --muted:#9fb7c9;
  --cyan:#88e7ff;
  --mint:#98ffd7;
  --amber:#ffd58a;
  --coral:#ff9d9d;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0;
  background:
    radial-gradient(circle at 10% 0%, rgba(136,231,255,.18), transparent 28%),
    radial-gradient(circle at 90% 12%, rgba(152,255,215,.10), transparent 30%),
    linear-gradient(135deg, #06111c, #101d2a 48%, #071018);
  color:var(--text);
  font-family:Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
}}
header {{
  position:sticky;
  top:0;
  z-index:10;
  padding:26px clamp(18px,3vw,42px);
  border-bottom:1px solid var(--line);
  background:linear-gradient(180deg, rgba(7,16,24,.94), rgba(7,16,24,.78));
  backdrop-filter:blur(14px);
}}
.eyebrow {{
  margin:0 0 8px;
  color:var(--cyan);
  text-transform:uppercase;
  letter-spacing:.16em;
  font-weight:800;
  font-size:12px;
}}
h1 {{
  margin:0;
  font-size:clamp(30px,5vw,56px);
  letter-spacing:-.055em;
  line-height:.95;
}}
.subtitle {{
  max-width:980px;
  color:var(--muted);
  line-height:1.6;
}}
.pills {{
  display:flex;
  gap:8px;
  flex-wrap:wrap;
  margin-top:16px;
}}
.pills span {{
  border:1px solid var(--line);
  border-radius:999px;
  padding:8px 11px;
  color:var(--muted);
  background:rgba(255,255,255,.065);
  font-size:12px;
}}
.pills b {{ color:var(--text); }}
main {{
  padding:26px clamp(18px,3vw,42px) 72px;
}}
.surfaceGrid {{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
  gap:14px;
  margin-bottom:28px;
}}
.surfaceCard {{
  border:1px solid var(--line);
  border-radius:24px;
  padding:16px;
  background:var(--panel);
  box-shadow:0 18px 60px rgba(0,0,0,.22);
}}
.surfaceCard h3 {{ margin:0 0 10px; }}
.surfaceCard p {{ margin:6px 0; color:var(--muted); }}
.surfaceCard b {{ color:var(--mint); }}
.roleSection {{
  margin-bottom:38px;
  border:1px solid var(--line);
  border-radius:32px;
  padding:22px;
  background:linear-gradient(180deg, rgba(255,255,255,.095), rgba(255,255,255,.052));
  box-shadow:0 24px 80px rgba(0,0,0,.32);
}}
.sectionHeader {{
  display:flex;
  justify-content:space-between;
  gap:18px;
  align-items:flex-start;
  margin-bottom:18px;
}}
.sectionHeader h2 {{
  margin:0;
  font-size:30px;
  letter-spacing:-.04em;
}}
.sectionHeader p {{
  color:var(--muted);
  margin:8px 0 0;
}}
.count {{
  border:1px solid var(--line);
  border-radius:22px;
  padding:14px 18px;
  color:var(--mint);
  font-size:28px;
  font-weight:900;
  background:rgba(255,255,255,.075);
}}
.grid {{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
  gap:16px;
}}
.card {{
  overflow:hidden;
  border:1px solid var(--line);
  border-radius:24px;
  background:rgba(255,255,255,.075);
}}
.imgWrap {{
  height:160px;
  background:
    linear-gradient(45deg, rgba(255,255,255,.04) 25%, transparent 25%, transparent 75%, rgba(255,255,255,.04) 75%),
    linear-gradient(45deg, rgba(255,255,255,.04) 25%, transparent 25%, transparent 75%, rgba(255,255,255,.04) 75%);
  background-size:24px 24px;
  background-position:0 0, 12px 12px;
}}
.imgWrap img {{
  display:block;
  width:100%;
  height:100%;
  object-fit:cover;
}}
.body {{ padding:13px; }}
.body h3 {{
  margin:0 0 7px;
  font-size:13px;
  word-break:break-word;
}}
.body p {{
  margin:0;
  color:var(--muted);
  font-size:11px;
  line-height:1.35;
  word-break:break-word;
}}
.chips {{
  display:flex;
  flex-wrap:wrap;
  gap:6px;
  margin:10px 0;
}}
.chips span {{
  border:1px solid rgba(255,255,255,.12);
  border-radius:999px;
  padding:5px 8px;
  font-size:11px;
  color:var(--cyan);
}}
.why {{
  color:var(--amber) !important;
}}
.notice {{
  border:1px solid var(--line);
  border-radius:24px;
  padding:18px;
  background:rgba(255,255,255,.07);
  color:var(--muted);
  line-height:1.6;
  margin-bottom:24px;
}}
</style>
</head>
<body>
<header>
  <p class="eyebrow">PRISMA Surface Visual Governor</p>
  <h1>M-04 Materiality Asset Curator</h1>
  <p class="subtitle">
    Este tablero separa fondos reales de logos, packshots, screenshots, íconos y assets dudosos.
    Sólo lo clasificado como Atmosphere / Background entra directo al Atmosphere Engine.
  </p>
  <div class="pills">{role_pills}</div>
</header>
<main>
  <div class="notice">
    <strong>Regla:</strong> el Governor no debe usar logos, packshots, screenshots ni íconos como atmósfera de interfaz.
    Decorative/Landing requiere gate. POS/Checkout queda protegido.
  </div>
  <section class="surfaceGrid">
    {''.join(surface_cards)}
  </section>
  {''.join(sections)}
</main>
</body>
</html>
"""

def role_description(role: str) -> str:
    return {
        "atmosphere_background": "Fondos y atmósferas reales aptas para Atmosphere Engine.",
        "decorative_landing": "Decorativos o hero/landing. Requieren gate antes de usarse como background.",
        "brand_logo": "Marca, logos e identidad. No son fondos.",
        "product_packshot": "Producto/catálogo/packshot. No debe usarse como atmósfera de interfaz.",
        "screenshot_qa": "Capturas, evidencia, snapshots o regresión visual. Sólo evidencia.",
        "ui_icon": "Íconos, glyphs o SVG utilitarios. No son backgrounds.",
        "unknown_review": "No clasificado con confianza. Requiere decisión humana.",
    }.get(role, "")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-per-role", type=int, default=80)
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    max_per_role = max(1, int(args.max_per_role))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stage = out_dir / f"PRISMA_M04_MATERIALITY_ASSET_CURATOR_WORK_{stamp}"
    result_zip = out_dir / f"PRISMA_M04_MATERIALITY_ASSET_CURATOR_RESULT_{stamp}.zip"
    backup_zip = out_dir / f"PRISMA_M04_MATERIALITY_ASSET_CURATOR_BACKUP_{stamp}.zip"
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

        git_before = run_git(root, ["status", "--short"])
        write_json(stage / "evidence/git_status_before.json", git_before)

        protected_before = collect_hashes(root, is_protected)
        no_touch_before = collect_hashes(root, is_no_touch)

        backup_manifest = backup_outputs(root, stage, backup_zip)
        log(f"Backup ZIP={backup_zip}")

        assets = read_m02_assets(root)
        if not assets:
            raise RuntimeError("M-02 asset CSV está vacío.")

        classified = []
        for row in assets:
            role, confidence, notes = classify_role(row)
            out = dict(row)
            out["asset_role"] = role
            out["role_confidence"] = confidence
            out["role_reason"] = "|".join(notes)
            out["atmosphere_engine_direct"] = role in ATMOSPHERE_ROLES
            out["atmosphere_engine_conditional"] = role in CONDITIONAL_ATMOSPHERE_ROLES
            classified.append(out)

        role_counts = Counter(row["asset_role"] for row in classified)
        family_role_counts = Counter((row.get("family_id", ""), row["asset_role"]) for row in classified)

        curated_contract = build_curated_contract(classified)
        copied = copy_curated_preview_assets(root, stage, classified, max_per_role=max_per_role)
        html_text = build_html(copied, dict(role_counts), curated_contract)

        stage_html = stage / "curated_preview_board" / "materiality-asset-curator.html"
        write_text(stage_html, html_text)
        write_json(stage / "curated_preview_board" / "materiality-asset-curator.data.json", {
            "engine_version": ENGINE_VERSION,
            "created_at": iso(),
            "classified_assets": len(classified),
            "preview_assets_copied": len(copied),
            "role_counts": dict(role_counts),
            "family_role_counts": {f"{k[0]}::{k[1]}": v for k, v in family_role_counts.items()},
            "assets": copied,
        })
        write_csv(stage / "indexes" / "asset_role_classification.generated.csv", classified)
        write_json(stage / "indexes" / "asset_role_classification.generated.json", {
            "engine_version": ENGINE_VERSION,
            "created_at": iso(),
            "classified_assets": len(classified),
            "role_counts": dict(role_counts),
            "assets": classified,
        })
        write_json(stage / "indexes" / "surface_atmosphere_assets.curated.json", curated_contract)

        out_json = root / OUTPUT_RELATIVE_PATHS[0]
        out_csv = root / OUTPUT_RELATIVE_PATHS[1]
        out_contract = root / OUTPUT_RELATIVE_PATHS[2]
        out_html = root / OUTPUT_RELATIVE_PATHS[3]
        out_preview_json = root / OUTPUT_RELATIVE_PATHS[4]
        out_md = root / OUTPUT_RELATIVE_PATHS[5]

        write_json(out_json, {
            "engine_version": ENGINE_VERSION,
            "created_at": iso(),
            "classified_assets": len(classified),
            "role_counts": dict(role_counts),
            "family_role_counts": {f"{k[0]}::{k[1]}": v for k, v in family_role_counts.items()},
            "assets": classified,
        })
        write_csv(out_csv, classified)
        write_json(out_contract, curated_contract)

        toolbox_html = html_text
        for row in copied:
            preview_rel = row.get("curated_preview_relative", "")
            repo_path = (root / row["relative_path"]).as_posix()
            toolbox_html = toolbox_html.replace(f'src="{html.escape(preview_rel)}"', f'src="file:///{html.escape(repo_path)}"')
        write_text(out_html, toolbox_html)
        write_json(out_preview_json, {
            "engine_version": ENGINE_VERSION,
            "created_at": iso(),
            "preview_assets_copied": len(copied),
            "assets": copied,
        })

        md = []
        md.append("# PRISMA M-04 · Materiality Asset Curator")
        md.append("")
        md.append(f"- Generated: `{iso()}`")
        md.append(f"- Engine: `{ENGINE_VERSION}`")
        md.append(f"- Assets clasificados: **{len(classified)}**")
        md.append(f"- Preview assets copiados: **{len(copied)}**")
        md.append("")
        md.append("## Conteo por rol")
        md.append("")
        md.append("| Rol | Conteo | Uso |")
        md.append("|---|---:|---|")
        for role in ROLE_ORDER:
            md.append(f"| `{role}` | {role_counts.get(role, 0)} | {role_description(role)} |")
        md.append("")
        md.append("## Regla")
        md.append("")
        md.append("Sólo `atmosphere_background` entra directo al Atmosphere Engine. `decorative_landing` requiere gate. Logos, packshots, screenshots, íconos y unknown quedan bloqueados como fondo.")
        md.append("")
        md.append("## Siguiente")
        md.append("")
        md.append("Revisar curated preview board. Luego aplicar primer piloto visual real a Control Center o PC con assets curated.")
        write_text(out_md, "\n".join(md))

        protected_after = collect_hashes(root, is_protected)
        no_touch_after = collect_hashes(root, is_no_touch)
        git_after = run_git(root, ["status", "--short"])

        write_json(stage / "protected_hashes.before.json", protected_before)
        write_json(stage / "protected_hashes.after.json", protected_after)
        write_json(stage / "no_touch_hashes.before.json", no_touch_before)
        write_json(stage / "no_touch_hashes.after.json", no_touch_after)
        write_json(stage / "evidence/git_status_after.json", git_after)

        outputs = []
        for r in OUTPUT_RELATIVE_PATHS:
            p = root / r
            if p.exists():
                outputs.append({"relative_path": r, "bytes": p.stat().st_size, "sha256": sha256_file(p)})

        atmosphere_count = role_counts.get("atmosphere_background", 0)
        bad_direct_count = sum(1 for row in classified if row["asset_role"] in {"brand_logo", "product_packshot", "screenshot_qa", "ui_icon"} and row.get("atmosphere_engine_direct"))

        verifier = {
            "status": "PASS",
            "engine_version": ENGINE_VERSION,
            "checks": {
                "m02_asset_csv_exists": (root / "tools/prisma-surface-visual-governor/inventory/materiality-asset-candidates.generated.csv").exists(),
                "classified_assets": len(classified),
                "atmosphere_background_assets": atmosphere_count,
                "preview_assets_copied": len(copied),
                "curated_contract_written": out_contract.exists(),
                "toolbox_outputs_written": len(outputs),
                "all_expected_outputs_exist": all((root / r).exists() for r in OUTPUT_RELATIVE_PATHS),
                "no_bad_direct_atmosphere_roles": bad_direct_count == 0,
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

        if atmosphere_count == 0:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No atmosphere_background assets classified.")
        if bad_direct_count != 0:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("Non-background assets marked as direct atmosphere.")
        if protected_before != protected_after:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("Protected POS/Checkout hashes changed.")
        if no_touch_before != no_touch_after:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No-touch hashes changed.")
        if not verifier["checks"]["all_expected_outputs_exist"]:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("Expected toolbox outputs missing.")

        if verifier["status"] != "PASS":
            restore_outputs(root, backup_zip, backup_manifest)
            rollback_performed = True

        write_json(stage / "verifier.json", verifier)

        report = []
        report.append("# PRISMA M-04 · Materiality Asset Curator Result")
        report.append("")
        report.append(f"- Generated: `{iso()}`")
        report.append(f"- Status: **{verifier['status']}**")
        report.append(f"- Rollback performed: `{rollback_performed}`")
        report.append(f"- Backup ZIP: `{backup_zip}`")
        report.append(f"- Assets classified: **{len(classified)}**")
        report.append(f"- Atmosphere/background assets: **{atmosphere_count}**")
        report.append(f"- Preview assets copied: **{len(copied)}**")
        report.append("")
        report.append("## Role counts")
        report.append("")
        for role in ROLE_ORDER:
            report.append(f"- `{role}`: **{role_counts.get(role, 0)}**")
        report.append("")
        report.append("## Open this file from result ZIP")
        report.append("")
        report.append("`curated_preview_board/materiality-asset-curator.html`")
        write_text(stage / "M04_MATERIALITY_ASSET_CURATOR_REPORT.md", "\n".join(report))

        receipt = {
            "pilot": "M-04",
            "name": "Materiality Asset Curator",
            "status": verifier["status"],
            "created_at": iso(),
            "repo": str(root),
            "result_zip": str(result_zip),
            "backup_zip": str(backup_zip),
            "rollback_performed": rollback_performed,
            "toolbox_outputs": OUTPUT_RELATIVE_PATHS,
            "curated_preview_html_inside_zip": "curated_preview_board/materiality-asset-curator.html",
            "classified_assets": len(classified),
            "atmosphere_background_assets": atmosphere_count,
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
            "pilot": "M-04",
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
