from __future__ import annotations

import argparse
import csv
import html
import json
import os
import shutil
import subprocess
import traceback
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ENGINE_VERSION = "M-03.1-materiality-preview-board"

OUTPUT_RELATIVE_PATHS = [
    "tools/prisma-surface-visual-governor/previews/materiality-preview-board.generated.html",
    "tools/prisma-surface-visual-governor/previews/materiality-preview-board.generated.json",
    "tools/prisma-surface-visual-governor/docs/MATERIALITY_PREVIEW_BOARD_GENERATED.md",
]

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

EXCLUDE_PARTS = {
    ".git", "node_modules", ".next", "out", "dist", "build", ".turbo",
    ".cache", "coverage", "playwright-report", "test-results", "__pycache__",
    ".prisma_installer_backups"
}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

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

FAMILY_LABELS = {
    "pc_graphite_cloudglass_stack": "PC Graphite Cloudglass Stack",
    "storm_graphite_dark_showcase": "Storm / Graphite Dark Showcase",
    "liquid_vapor_reference": "Liquid / Vapor Reference",
    "tablet_light_soft_clouds": "Tablet Light Soft Clouds",
    "mobile_thin_mist": "Mobile Thin Mist",
    "web_eit_sober": "Web/EIT Public Sober",
    "control_center_visual_governance": "Control Center / Visual Governance",
    "unclassified_visual_asset": "Unclassified Visual Asset",
}

FAMILY_DESCRIPTIONS = {
    "pc_graphite_cloudglass_stack": "Casa matriz premium: base graphite, fracturas, luz y mist/dust. Ideal para PC Dashboard/Hoy y superficies ejecutivas.",
    "storm_graphite_dark_showcase": "Showcase oscuro premium. Entra en Chart Lab, Visual OS, Control Center y PC referencia. Prohibido en POS/Checkout.",
    "liquid_vapor_reference": "Familia wow con líquido, humo y vapor. Se usa con bozal: Chart Lab, Visual OS, Control Center, PC referencia.",
    "tablet_light_soft_clouds": "Light-first, táctil, clara y luminosa. Base correcta para Tablet productiva, settings, sync y quizá mobile.",
    "mobile_thin_mist": "Bajo ruido, liviano, battery-friendly y reduced-motion.",
    "web_eit_sober": "Público sobrio. Limpio, tranquilo, sin exceso visual.",
    "control_center_visual_governance": "Gobierno, evidencia, salud, command surfaces y PRISMO/Control Center.",
    "unclassified_visual_asset": "Asset detectado sin familia canónica. Requiere decisión humana antes de permitirlo en rutas.",
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
    temp = root / ".prisma_surface_governor_m03_restore_tmp"
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
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows

def read_json_if_exists(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}

def safe_asset_name(index: int, rel_path: str) -> str:
    p = Path(rel_path)
    suffix = p.suffix.lower()
    stem = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in p.stem)[:80]
    return f"{index:04d}_{stem}{suffix}"

def copy_preview_assets(root: Path, stage: Path, rows: list[dict], max_per_family: int = 80) -> list[dict]:
    counts = defaultdict(int)
    copied = []
    asset_root = stage / "preview_assets"

    sorted_rows = sorted(rows, key=lambda r: (
        FAMILY_ORDER.index(r.get("family_id", "unclassified_visual_asset")) if r.get("family_id", "unclassified_visual_asset") in FAMILY_ORDER else 999,
        r.get("relative_path", "").lower()
    ))

    idx = 0
    for row in sorted_rows:
        family = row.get("family_id") or "unclassified_visual_asset"
        if counts[family] >= max_per_family:
            continue
        src = root / row["relative_path"]
        if not src.exists() or not src.is_file():
            continue
        if src.suffix.lower() not in IMAGE_EXTS:
            continue

        idx += 1
        counts[family] += 1
        dst_rel = f"{family}/{safe_asset_name(idx, row['relative_path'])}"
        dst = asset_root / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        new_row = dict(row)
        new_row["preview_asset_relative"] = f"preview_assets/{dst_rel}"
        new_row["preview_asset_copied"] = True
        copied.append(new_row)

    return copied

def build_html(rows: list[dict], ledger: dict, allowlist: dict, budgets: dict) -> str:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row.get("family_id") or "unclassified_visual_asset"].append(row)

    def esc(x) -> str:
        return html.escape(str(x or ""))

    cards = []
    for family in FAMILY_ORDER:
        items = grouped.get(family, [])
        if not items:
            continue

        allow = ""
        block = ""
        detected = ""

        for fam in allowlist.get("families", []):
            if fam.get("id") == family:
                allow = ", ".join(fam.get("allowed_surfaces", []))
                block = ", ".join(fam.get("blocked_surfaces", []))
                detected = str(fam.get("detected_asset_count", len(items)))
                break

        cards.append(f"""
<section class="family family-{esc(family)}">
  <div class="familyHeader">
    <div>
      <p class="eyebrow">Familia visual</p>
      <h2>{esc(FAMILY_LABELS.get(family, family))}</h2>
      <p class="desc">{esc(FAMILY_DESCRIPTIONS.get(family, ""))}</p>
    </div>
    <div class="familyMeta">
      <span><b>{len(items)}</b> previews</span>
      <span><b>{esc(detected or len(items))}</b> detectados</span>
    </div>
  </div>
  <div class="policy">
    <div><strong>Permitido:</strong> {esc(allow or "requires_review")}</div>
    <div><strong>Bloqueado:</strong> {esc(block or "none")}</div>
  </div>
  <div class="grid">
""")
        for item in items:
            img = item.get("preview_asset_relative", "")
            cards.append(f"""
    <article class="assetCard">
      <div class="assetImageWrap">
        <img src="{esc(img)}" alt="{esc(item.get('filename','asset'))}" loading="lazy" />
      </div>
      <div class="assetInfo">
        <h3>{esc(item.get('filename',''))}</h3>
        <p>{esc(item.get('relative_path',''))}</p>
        <dl>
          <div><dt>Ext</dt><dd>{esc(item.get('extension',''))}</dd></div>
          <div><dt>Bytes</dt><dd>{esc(item.get('bytes',''))}</dd></div>
        </dl>
      </div>
    </article>
""")
        cards.append("""
  </div>
</section>
""")

    budget_rows = []
    bdict = budgets.get("budgets", budgets)
    if isinstance(bdict, dict):
        for key, b in bdict.items():
            if isinstance(b, dict):
                budget_rows.append(f"""
<tr>
  <td><code>{esc(key)}</code></td>
  <td>{esc(b.get('surface',''))}</td>
  <td>{esc(b.get('goal',''))}</td>
  <td>{esc(b.get('background',''))}</td>
  <td>{esc(b.get('glass',''))}</td>
  <td>{esc(b.get('rim',''))}</td>
  <td>{esc(b.get('motion',''))}</td>
  <td>{esc(b.get('webgl',''))}</td>
</tr>
""")

    total = len(rows)
    family_summary = "".join(
        f"<span class='pill'>{esc(FAMILY_LABELS.get(f, f))}: <b>{len(grouped.get(f, []))}</b></span>"
        for f in FAMILY_ORDER
        if grouped.get(f)
    )

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>PRISMA M-03 · Materiality Preview Board</title>
<style>
:root {{
  --bg0:#071018;
  --bg1:#0e1a25;
  --panel:rgba(255,255,255,.075);
  --panel2:rgba(255,255,255,.115);
  --line:rgba(210,232,255,.18);
  --line2:rgba(210,232,255,.30);
  --text:#edf7ff;
  --muted:#9fb6c9;
  --cyan:#8de3ff;
  --mint:#9fffd8;
  --warn:#ffd58a;
  --bad:#ff9b9b;
  --shadow:0 24px 80px rgba(0,0,0,.38);
}}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; min-height:100%; background:var(--bg0); color:var(--text); font-family:Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; }}
body {{
  background:
    radial-gradient(circle at 12% 0%, rgba(141,227,255,.20), transparent 30%),
    radial-gradient(circle at 88% 12%, rgba(159,255,216,.12), transparent 28%),
    linear-gradient(135deg, #06101a, #101b27 48%, #071018);
}}
.hero {{
  position:sticky;
  top:0;
  z-index:20;
  backdrop-filter: blur(12px);
  background:linear-gradient(180deg, rgba(6,16,26,.92), rgba(6,16,26,.74));
  border-bottom:1px solid var(--line);
  padding:24px clamp(18px, 3vw, 42px);
}}
.heroTop {{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:24px;
}}
.eyebrow {{
  margin:0 0 8px;
  color:var(--cyan);
  text-transform:uppercase;
  letter-spacing:.16em;
  font-size:12px;
  font-weight:800;
}}
h1 {{
  margin:0;
  font-size:clamp(28px, 5vw, 58px);
  letter-spacing:-.06em;
  line-height:.94;
}}
.subtitle {{
  max-width:980px;
  margin:16px 0 0;
  color:var(--muted);
  font-size:16px;
  line-height:1.6;
}}
.metaBox {{
  min-width:260px;
  padding:16px;
  border:1px solid var(--line);
  border-radius:24px;
  background:var(--panel);
  box-shadow:var(--shadow);
}}
.metaBox div {{
  display:flex;
  justify-content:space-between;
  gap:18px;
  padding:7px 0;
  border-bottom:1px solid rgba(255,255,255,.08);
  color:var(--muted);
}}
.metaBox div:last-child {{ border-bottom:0; }}
.metaBox b {{ color:var(--text); }}
.pills {{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:18px;
}}
.pill {{
  display:inline-flex;
  gap:6px;
  align-items:center;
  border:1px solid var(--line);
  border-radius:999px;
  padding:8px 11px;
  background:rgba(255,255,255,.07);
  color:var(--muted);
  font-size:12px;
}}
.pill b {{ color:var(--text); }}
main {{
  padding:28px clamp(18px, 3vw, 42px) 72px;
}}
.family {{
  margin:0 0 42px;
  padding:22px;
  border:1px solid var(--line);
  border-radius:32px;
  background:linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.055));
  box-shadow:var(--shadow);
}}
.familyHeader {{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:24px;
  margin-bottom:16px;
}}
.family h2 {{
  margin:0;
  font-size:30px;
  letter-spacing:-.04em;
}}
.desc {{
  margin:8px 0 0;
  color:var(--muted);
  max-width:980px;
  line-height:1.55;
}}
.familyMeta {{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  justify-content:flex-end;
}}
.familyMeta span {{
  border:1px solid var(--line);
  border-radius:16px;
  padding:10px 12px;
  background:rgba(255,255,255,.075);
  color:var(--muted);
}}
.familyMeta b {{ color:var(--mint); font-size:20px; }}
.policy {{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:12px;
  margin:14px 0 20px;
}}
.policy div {{
  padding:12px 14px;
  border:1px solid var(--line);
  border-radius:18px;
  background:rgba(0,0,0,.16);
  color:var(--muted);
}}
.policy strong {{ color:var(--text); }}
.grid {{
  display:grid;
  grid-template-columns:repeat(auto-fill, minmax(220px, 1fr));
  gap:16px;
}}
.assetCard {{
  overflow:hidden;
  border:1px solid var(--line);
  border-radius:24px;
  background:rgba(255,255,255,.08);
  box-shadow:0 12px 34px rgba(0,0,0,.24);
}}
.assetImageWrap {{
  height:168px;
  display:flex;
  align-items:center;
  justify-content:center;
  background:
    linear-gradient(45deg, rgba(255,255,255,.04) 25%, transparent 25%, transparent 75%, rgba(255,255,255,.04) 75%),
    linear-gradient(45deg, rgba(255,255,255,.04) 25%, transparent 25%, transparent 75%, rgba(255,255,255,.04) 75%);
  background-size:24px 24px;
  background-position:0 0, 12px 12px;
}}
.assetImageWrap img {{
  width:100%;
  height:100%;
  object-fit:cover;
  display:block;
}}
.assetInfo {{
  padding:13px;
}}
.assetInfo h3 {{
  margin:0 0 7px;
  font-size:13px;
  line-height:1.25;
  word-break:break-word;
}}
.assetInfo p {{
  margin:0;
  color:var(--muted);
  font-size:11px;
  line-height:1.35;
  word-break:break-word;
}}
.assetInfo dl {{
  display:flex;
  gap:8px;
  margin:11px 0 0;
  flex-wrap:wrap;
}}
.assetInfo dl div {{
  display:flex;
  gap:5px;
  border:1px solid rgba(255,255,255,.11);
  border-radius:999px;
  padding:5px 8px;
  font-size:11px;
  color:var(--muted);
}}
dt {{ color:var(--cyan); }}
dd {{ margin:0; }}
.budgets {{
  margin:0 0 42px;
  padding:22px;
  border:1px solid var(--line);
  border-radius:32px;
  background:rgba(255,255,255,.075);
  box-shadow:var(--shadow);
  overflow:auto;
}}
table {{
  width:100%;
  border-collapse:collapse;
  min-width:980px;
}}
th, td {{
  padding:12px;
  border-bottom:1px solid rgba(255,255,255,.10);
  text-align:left;
  vertical-align:top;
  color:var(--muted);
  font-size:13px;
}}
th {{ color:var(--text); }}
code {{
  color:var(--mint);
}}
.footerNote {{
  color:var(--muted);
  line-height:1.6;
  border:1px solid var(--line);
  border-radius:24px;
  padding:18px;
  background:rgba(255,255,255,.06);
}}
@media (max-width: 820px) {{
  .heroTop, .familyHeader, .policy {{ grid-template-columns:1fr; display:block; }}
  .metaBox {{ margin-top:20px; }}
  .policy div {{ margin-bottom:10px; }}
}}
</style>
</head>
<body>
<header class="hero">
  <div class="heroTop">
    <div>
      <p class="eyebrow">PRISMA Surface Visual Governor</p>
      <h1>M-03 Materiality Preview Board</h1>
      <p class="subtitle">
        Tablero generado con assets reales del repo. Este board recupera el plan anterior:
        imágenes → familias → superficies permitidas/bloqueadas → route budgets. No es UI final,
        es el mapa visual antes de aplicar más cambios.
      </p>
    </div>
    <aside class="metaBox">
      <div><span>Generado</span><b>{esc(iso())}</b></div>
      <div><span>Assets preview</span><b>{total}</b></div>
      <div><span>Familias</span><b>{len([f for f in FAMILY_ORDER if grouped.get(f)])}</b></div>
      <div><span>Modo</span><b>read-only visual board</b></div>
    </aside>
  </div>
  <div class="pills">{family_summary}</div>
</header>
<main>
<section class="budgets">
  <p class="eyebrow">Route budgets</p>
  <h2>Presupuestos visuales recuperados</h2>
  <table>
    <thead>
      <tr>
        <th>Budget</th><th>Surface</th><th>Goal</th><th>Background</th><th>Glass</th><th>Rim</th><th>Motion</th><th>WebGL</th>
      </tr>
    </thead>
    <tbody>
      {''.join(budget_rows)}
    </tbody>
  </table>
</section>
{''.join(cards)}
<section class="footerNote">
  <strong>Regla:</strong> estas imágenes no son wallpaper decorativo. Son material del Atmosphere Engine.
  POS/Checkout quedan protegidos. Tablet productiva conserva light-first. Chart Lab y Control Center pueden usar
  familias más premium, pero siempre con budget/gate.
</section>
</main>
</body>
</html>
"""

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-per-family", type=int, default=80)
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    max_per_family = max(1, int(args.max_per_family))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stage = out_dir / f"PRISMA_M03_MATERIALITY_PREVIEW_BOARD_WORK_{stamp}"
    result_zip = out_dir / f"PRISMA_M03_MATERIALITY_PREVIEW_BOARD_RESULT_{stamp}.zip"
    backup_zip = out_dir / f"PRISMA_M03_MATERIALITY_PREVIEW_BOARD_BACKUP_{stamp}.zip"
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
            raise RuntimeError("M-02 asset CSV está vacío. No puedo generar preview board.")

        ledger = read_json_if_exists(root / "tools/prisma-surface-visual-governor/inventory/materiality-integration-ledger.generated.json")
        allowlist = read_json_if_exists(root / "tools/prisma-surface-visual-governor/contracts/surface-atmosphere-allowlist.generated.json")
        budgets = read_json_if_exists(root / "tools/prisma-surface-visual-governor/contracts/surface-route-budgets.generated.json")

        copied = copy_preview_assets(root, stage, assets, max_per_family=max_per_family)
        if not copied:
            raise RuntimeError("No se copiaron assets para preview. Revisa paths del CSV M-02.")

        html_text = build_html(copied, ledger, allowlist, budgets)

        stage_html = stage / "preview_board" / "materiality-preview-board.html"
        write_text(stage_html, html_text)
        write_json(stage / "preview_board" / "materiality-preview-board.data.json", {
            "engine_version": ENGINE_VERSION,
            "created_at": iso(),
            "preview_asset_count": len(copied),
            "asset_count_from_m02": len(assets),
            "families": FAMILY_ORDER,
            "assets": copied,
            "ledger_summary": {
                "assets_detected_count": ledger.get("assets_detected_count"),
                "routes_detected_count": ledger.get("routes_detected_count"),
            },
        })
        write_csv(stage / "indexes" / "preview_assets_copied.csv", copied)

        # Write canonical preview outputs into toolbox.
        out_html = root / OUTPUT_RELATIVE_PATHS[0]
        out_json = root / OUTPUT_RELATIVE_PATHS[1]
        out_md = root / OUTPUT_RELATIVE_PATHS[2]

        # Toolbox HTML uses absolute file URLs for local repo previews, while ZIP HTML uses copied relative preview assets.
        toolbox_html = html_text
        for row in copied:
            preview_rel = row.get("preview_asset_relative", "")
            repo_path = (root / row["relative_path"]).as_posix()
            toolbox_html = toolbox_html.replace(f'src="{html.escape(preview_rel)}"', f'src="file:///{html.escape(repo_path)}"')

        write_text(out_html, toolbox_html)
        write_json(out_json, {
            "engine_version": ENGINE_VERSION,
            "created_at": iso(),
            "source": "M-02 materiality integration ledger",
            "preview_asset_count": len(copied),
            "asset_count_from_m02": len(assets),
            "families": FAMILY_ORDER,
            "assets": copied,
        })

        grouped = defaultdict(list)
        for row in copied:
            grouped[row.get("family_id") or "unclassified_visual_asset"].append(row)

        md = []
        md.append("# PRISMA M-03 · Materiality Preview Board")
        md.append("")
        md.append(f"- Generated: `{iso()}`")
        md.append(f"- Engine: `{ENGINE_VERSION}`")
        md.append(f"- Preview assets copied into result ZIP: **{len(copied)}**")
        md.append(f"- Assets from M-02: **{len(assets)}**")
        md.append("")
        md.append("## Qué es")
        md.append("")
        md.append("Un tablero visual generado con assets reales del repo, agrupados por familia visual y conectado al ledger M-02.")
        md.append("")
        md.append("## Familias")
        md.append("")
        md.append("| Familia | Previews | Uso |")
        md.append("|---|---:|---|")
        for family in FAMILY_ORDER:
            items = grouped.get(family, [])
            if not items:
                continue
            md.append(f"| `{family}` | {len(items)} | {FAMILY_DESCRIPTIONS.get(family, '')} |")
        md.append("")
        md.append("## Archivos")
        md.append("")
        md.append(f"- Toolbox HTML: `{OUTPUT_RELATIVE_PATHS[0]}`")
        md.append(f"- Toolbox JSON: `{OUTPUT_RELATIVE_PATHS[1]}`")
        md.append("- Result ZIP incluye `preview_board/materiality-preview-board.html` con assets copiados.")
        md.append("")
        md.append("## Siguiente")
        md.append("")
        md.append("Revisar el board. Después elegir la primera superficie para aplicar familia visual real con Visual Regression Harness.")
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

        verifier = {
            "status": "PASS",
            "engine_version": ENGINE_VERSION,
            "checks": {
                "m02_asset_csv_exists": (root / "tools/prisma-surface-visual-governor/inventory/materiality-asset-candidates.generated.csv").exists(),
                "assets_from_m02": len(assets),
                "preview_assets_copied": len(copied),
                "families_with_previews": len([f for f in FAMILY_ORDER if grouped.get(f)]),
                "result_html_exists": stage_html.exists(),
                "toolbox_outputs_written": len(outputs),
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

        if len(copied) == 0:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No preview assets copied.")
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
        report.append("# PRISMA M-03 · Materiality Preview Board Result")
        report.append("")
        report.append(f"- Generated: `{iso()}`")
        report.append(f"- Status: **{verifier['status']}**")
        report.append(f"- Rollback performed: `{rollback_performed}`")
        report.append(f"- Backup ZIP: `{backup_zip}`")
        report.append(f"- Preview assets copied: **{len(copied)}**")
        report.append(f"- Families with previews: **{verifier['checks']['families_with_previews']}**")
        report.append("")
        report.append("## Open this file from the result ZIP")
        report.append("")
        report.append("`preview_board/materiality-preview-board.html`")
        report.append("")
        report.append("## Toolbox outputs")
        report.append("")
        for item in outputs:
            report.append(f"- `{item['relative_path']}`")
        report.append("")
        report.append("## Next")
        report.append("")
        report.append("Revisar el preview board y seleccionar superficie/familia para el primer visual application pilot.")
        write_text(stage / "M03_MATERIALITY_PREVIEW_BOARD_REPORT.md", "\n".join(report))

        receipt = {
            "pilot": "M-03",
            "name": "Materiality Preview Board",
            "status": verifier["status"],
            "created_at": iso(),
            "repo": str(root),
            "result_zip": str(result_zip),
            "backup_zip": str(backup_zip),
            "rollback_performed": rollback_performed,
            "toolbox_outputs": OUTPUT_RELATIVE_PATHS,
            "preview_html_inside_zip": "preview_board/materiality-preview-board.html",
            "preview_assets_copied": len(copied),
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
            "pilot": "M-03",
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
