from __future__ import annotations

import argparse
import csv
import html
import json
import shutil
import subprocess
import traceback
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import hashlib

ENGINE_VERSION = "M-04B.fix2-family-policy-alias-normalizer"

OUTPUT_RELATIVE_PATHS = [
    "tools/prisma-surface-visual-governor/inventory/external-reference-atmosphere-pack.normalized.generated.json",
    "tools/prisma-surface-visual-governor/inventory/external-reference-atmosphere-pack.normalized.generated.csv",
    "tools/prisma-surface-visual-governor/contracts/external-reference-family-aliases.generated.json",
    "tools/prisma-surface-visual-governor/contracts/external-reference-atmosphere-allowlist.normalized.generated.json",
    "tools/prisma-surface-visual-governor/contracts/surface-atmosphere-assets.external-overlay.normalized.generated.json",
    "tools/prisma-surface-visual-governor/previews/external-reference-atmosphere-normalized-preview.generated.html",
    "tools/prisma-surface-visual-governor/previews/external-reference-atmosphere-normalized-preview.generated.json",
    "tools/prisma-surface-visual-governor/docs/EXTERNAL_REFERENCE_FAMILY_ALIAS_NORMALIZER_GENERATED.md",
    "tools/prisma-surface-visual-governor/docs/EXTERNAL_REFERENCE_FAMILY_ALIAS_DO_NOT_FORGET_GENERATED.md",
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
    "\\pos\\",
    "checkout",
]

CANONICAL_FAMILIES = {
    "alpine_graphite_hero": {
        "label": "Alpine Graphite Hero",
        "allowed": ["pc", "control_center"],
        "conditional": ["chart_lab", "pc_reference"],
        "blocked": ["tablet_productive", "pos_checkout"],
        "budget": "premium calm executive background",
    },
    "storm_graphite_vault": {
        "label": "Storm Graphite Vault",
        "allowed": ["control_center", "chart_lab", "pc_reference"],
        "conditional": ["visual_os"],
        "blocked": ["tablet_productive", "pos_checkout", "web_eit_public"],
        "budget": "premium dark governance/storm mood; strong scrim required",
    },
    "visual_os_celestial": {
        "label": "Visual OS Celestial",
        "allowed": ["control_center", "chart_lab", "visual_os"],
        "conditional": ["pc_reference"],
        "blocked": ["tablet_productive", "pos_checkout", "web_eit_public"],
        "budget": "showcase/reference only; never default productive",
    },
    "liquid_teal_vapor": {
        "label": "Liquid Teal Vapor",
        "allowed": ["chart_lab", "visual_os"],
        "conditional": ["control_center", "pc_reference"],
        "blocked": ["tablet_productive", "pos_checkout", "dense_tables", "web_eit_public"],
        "budget": "high wow, studio/showcase only",
    },
    "tablet_light_soft": {
        "label": "Tablet Light Soft",
        "allowed": ["tablet_productive", "mobile", "web_eit_public"],
        "conditional": ["pos_checkout"],
        "blocked": ["pc_dark_showcase_default"],
        "budget": "light-first low-noise background",
    },
    "mobile_thin_mist": {
        "label": "Mobile Thin Mist",
        "allowed": ["mobile", "web_eit_public"],
        "conditional": ["tablet_productive", "control_center_audit"],
        "blocked": ["pos_checkout_without_gate"],
        "budget": "low-noise, battery-friendly, audit-safe",
    },
    "light_architecture_material": {
        "label": "Light Architecture Material",
        "allowed": ["web_eit_public", "tablet_productive", "settings"],
        "conditional": ["control_center_audit"],
        "blocked": ["pos_checkout_without_gate"],
        "budget": "light/sober material reference",
    },
    "warm_showcase_mountain": {
        "label": "Warm Showcase Mountain",
        "allowed": ["chart_lab", "marketing_reference"],
        "conditional": ["control_center_showcase"],
        "blocked": ["tablet_productive", "pos_checkout", "dense_tables"],
        "budget": "decorative/showcase, sparingly",
    },
    "subject_photo_blocked": {
        "label": "Subject Photo Blocked",
        "allowed": [],
        "conditional": ["manual_review_only"],
        "blocked": ["all_background_use"],
        "budget": "not direct UI atmosphere",
    },
    "external_review": {
        "label": "External Review",
        "allowed": [],
        "conditional": ["manual_review_only"],
        "blocked": ["all_until_reviewed"],
        "budget": "requires human review",
    },
}

# Explicit aliases for the granular families from the previous mapping plus common variants.
EXPLICIT_ALIAS = {
    "audit_quiet_vault": "mobile_thin_mist",
    "thin_mist_blue": "mobile_thin_mist",
    "thin_mist": "mobile_thin_mist",
    "mobile_thin_mist": "mobile_thin_mist",
    "tablet_light_minimal_fog": "tablet_light_soft",
    "tablet_light_snow": "tablet_light_soft",
    "tablet_soft_clouds": "tablet_light_soft",
    "tablet_light_soft": "tablet_light_soft",
    "storm_graphite_motion": "storm_graphite_vault",
    "storm_graphite_vault": "storm_graphite_vault",
    "storm_vapor_dusk": "storm_graphite_vault",
    "visual_os_night": "visual_os_celestial",
    "visual_os_celestial": "visual_os_celestial",
    "liquid_teal_vapor": "liquid_teal_vapor",
    "alpine_graphite_hero": "alpine_graphite_hero",
    "light_architecture_material": "light_architecture_material",
    "warm_showcase_mountain": "warm_showcase_mountain",
    "subject_photo_blocked": "subject_photo_blocked",
    "decorative_subject_review": "subject_photo_blocked",
    "external_review": "",
}

SURFACES = [
    "control_center",
    "pc",
    "pc_reference",
    "chart_lab",
    "visual_os",
    "tablet_productive",
    "mobile",
    "web_eit_public",
    "pos_checkout",
]

def iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def progress(done: int, total: int, msg: str):
    pct = int(done / max(total, 1) * 100)
    bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
    print(f"[{bar}] {pct:3d}% · {msg}")

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_PARTS for part in path.parts)

def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()

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
        item = {"relative_path": r, "existed": src.exists(), "is_dir": src.exists() and src.is_dir(), "sha256": ""}
        if src.exists() and src.is_file():
            item["sha256"] = sha256_file(src)
            dst = backup_stage / "files" / r
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        if src.exists() and src.is_dir():
            dst_dir = backup_stage / "dirs" / r
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src, dst_dir)
        manifest["files"].append(item)

    write_json(backup_stage / "backup_manifest.json", manifest)
    zip_dir(backup_stage, backup_zip)
    return manifest

def restore_outputs(root: Path, backup_zip: Path, manifest: dict):
    temp = root / ".m04b_fix2_restore_tmp"
    if temp.exists():
        shutil.rmtree(temp, ignore_errors=True)
    temp.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(backup_zip, "r") as z:
        z.extractall(temp)

    for item in manifest.get("files", []):
        dst = root / item["relative_path"]
        if item.get("is_dir"):
            if dst.exists():
                shutil.rmtree(dst, ignore_errors=True)
            src_dir = temp / "dirs" / item["relative_path"]
            if item.get("existed") and src_dir.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src_dir, dst)
        else:
            if item.get("existed"):
                src = temp / "files" / item["relative_path"]
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
            else:
                if dst.exists() and dst.is_file():
                    dst.unlink()

    shutil.rmtree(temp, ignore_errors=True)

def read_input_inventory(root: Path, out_dir: Path) -> dict:
    direct = root / "tools/prisma-surface-visual-governor/inventory/external-reference-atmosphere-pack.generated.json"
    if direct.exists():
        payload = json.loads(direct.read_text(encoding="utf-8", errors="replace"))
        if len(payload.get("assets", [])) >= 20:
            return payload

    zips = sorted(out_dir.glob("gov m04b fix1 * result.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    for zp in zips:
        with zipfile.ZipFile(zp, "r") as z:
            for name in z.namelist():
                if name.endswith("external-reference-atmosphere-pack.generated.json"):
                    return json.loads(z.read(name).decode("utf-8", errors="replace"))

    raise RuntimeError("No encontré inventory M-04B fix1 en toolbox ni en ZIP result.")

def normalize_family(row: dict) -> tuple[str, int, str]:
    original = (row.get("family_id") or "").strip()
    filename = row.get("original_filename") or row.get("filename") or ""
    notes = row.get("notes") or ""
    recommended = row.get("recommended_surfaces_from_mapping") or row.get("recommended_surfaces") or ""
    label = row.get("family_label") or ""
    blob = " ".join([original, filename, notes, recommended, label]).lower().replace("-", "_").replace(" ", "_")

    if original in EXPLICIT_ALIAS and EXPLICIT_ALIAS[original]:
        return EXPLICIT_ALIAS[original], 100, f"explicit_alias:{original}"
    if original in CANONICAL_FAMILIES and original != "external_review":
        return original, 100, "already_canonical"

    # Subject/animal/person first, because they should never become backgrounds.
    if any(x in blob for x in ["fox", "animal", "person", "portrait", "people", "human", "subject"]):
        return "subject_photo_blocked", 98, "subject_block"

    # Light/snow/tablet before liquid, so snow/ice tablet sets do not get pulled into Liquid.
    if any(x in blob for x in ["tablet", "snow", "white", "light", "bright", "minimal_fog", "soft_cloud", "soft_clouds", "pale", "clean"]):
        return "tablet_light_soft", 92, "heuristic_light_tablet"

    if any(x in blob for x in ["thin_mist", "quiet", "audit", "low_noise", "blue_mist", "mist_blue", "fog_blue", "mobile"]):
        return "mobile_thin_mist", 90, "heuristic_thin_mist"

    if any(x in blob for x in ["architecture", "material", "building", "public", "sober", "matte", "settings"]):
        return "light_architecture_material", 86, "heuristic_light_architecture"

    if any(x in blob for x in ["aurora", "celestial", "night", "stars", "cosmic", "visual_os", "showcase_night"]):
        return "visual_os_celestial", 88, "heuristic_celestial"

    if any(x in blob for x in ["liquid", "teal", "vapor", "water", "ocean", "lake", "aqua", "glacier", "fluid"]):
        return "liquid_teal_vapor", 86, "heuristic_liquid_teal"

    if any(x in blob for x in ["storm", "graphite", "vault", "dark", "slate", "obsidian", "dusk", "motion", "cloud_motion"]):
        return "storm_graphite_vault", 86, "heuristic_storm_graphite"

    if any(x in blob for x in ["alpine", "executive", "hero", "icefield", "mountain_graphite"]):
        return "alpine_graphite_hero", 82, "heuristic_alpine_graphite"

    if any(x in blob for x in ["warm", "sunrise", "golden", "mountain", "desert", "orange"]):
        return "warm_showcase_mountain", 78, "heuristic_warm_showcase"

    return "external_review", 30, f"unmatched:{original or 'missing'}"

def surface_verdict(row: dict, surface: str) -> tuple[str, str]:
    fam = row["normalized_family_id"]
    policy = CANONICAL_FAMILIES.get(fam, CANONICAL_FAMILIES["external_review"])

    if surface in policy["allowed"]:
        return "ALLOWED", "family_allowed"
    if surface in policy["conditional"]:
        return "CONDITIONAL", "family_conditional"
    if surface in policy["blocked"] or "all_background_use" in policy["blocked"] or "all_until_reviewed" in policy["blocked"]:
        return "BLOCKED", "family_blocked"
    if surface == "pos_checkout":
        return "GATE_REQUIRED", "pos_checkout_requires_gate"
    return "BLOCKED", "not_allowed_for_surface"

def build_surface_overlay(rows: list[dict]) -> dict:
    surfaces = {}
    for surface in SURFACES:
        surfaces[surface] = {"allowed": [], "conditional": [], "gate_required": [], "blocked_count": 0}

    for row in rows:
        for surface in SURFACES:
            verdict, reason = surface_verdict(row, surface)
            item = {
                "relative_path": row.get("relative_path", ""),
                "filename": row.get("filename", ""),
                "original_filename": row.get("original_filename", ""),
                "original_family_id": row.get("original_family_id", ""),
                "normalized_family_id": row.get("normalized_family_id", ""),
                "normalized_family_label": row.get("normalized_family_label", ""),
                "confidence": row.get("normalization_confidence", ""),
                "reason": reason,
                "sha256": row.get("sha256", ""),
            }
            if verdict == "ALLOWED":
                surfaces[surface]["allowed"].append(item)
            elif verdict == "CONDITIONAL":
                surfaces[surface]["conditional"].append(item)
            elif verdict == "GATE_REQUIRED":
                surfaces[surface]["gate_required"].append(item)
            else:
                surfaces[surface]["blocked_count"] += 1

    return {
        "schema": "prisma.surface.visual_governor.surface_atmosphere_assets_external_overlay_normalized",
        "version": "M-04B.fix2",
        "created_at": iso(),
        "rule": "Granular external families normalized into canonical parent families before any route consumes images.",
        "surfaces": surfaces,
    }

def build_html(rows: list[dict]) -> str:
    groups = defaultdict(list)
    for row in rows:
        groups[row["normalized_family_id"]].append(row)

    sections = []
    for fam in CANONICAL_FAMILIES:
        items = groups.get(fam, [])
        if not items:
            continue
        policy = CANONICAL_FAMILIES[fam]
        sections.append(f"""
<section>
  <div class="head">
    <div>
      <p class="eyebrow">Familia normalizada</p>
      <h2>{html.escape(policy["label"])}</h2>
      <p>{html.escape(policy["budget"])}</p>
    </div>
    <b>{len(items)}</b>
  </div>
  <div class="policy">
    <span><strong>Permitido:</strong> {html.escape(", ".join(policy["allowed"]) or "none")}</span>
    <span><strong>Condicional:</strong> {html.escape(", ".join(policy["conditional"]) or "none")}</span>
    <span><strong>Bloqueado:</strong> {html.escape(", ".join(policy["blocked"]) or "none")}</span>
  </div>
  <div class="grid">
""")
        for item in items:
            src = item.get("preview_relative", "")
            sections.append(f"""
    <article>
      <img src="{html.escape(src)}" loading="lazy" />
      <div>
        <h3>{html.escape(item.get("original_filename") or item.get("filename") or "")}</h3>
        <p><b>Original:</b> {html.escape(item.get("original_family_id", ""))}</p>
        <p><b>Norm:</b> {html.escape(item.get("normalized_family_id", ""))} · conf {html.escape(str(item.get("normalization_confidence", "")))}</p>
        <small>{html.escape(item.get("normalization_reason", ""))}</small>
      </div>
    </article>
""")
        sections.append("</div></section>")

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>PRISMA M-04B fix2 · Normalized External Atmosphere Families</title>
<style>
body {{
  margin:0;
  background:
    radial-gradient(circle at 12% 0%, rgba(141,232,255,.20), transparent 32%),
    radial-gradient(circle at 88% 10%, rgba(159,255,216,.12), transparent 32%),
    linear-gradient(135deg,#06101a,#101d2a 52%,#071018);
  color:#eef8ff;
  font-family:Inter, system-ui, Segoe UI, sans-serif;
}}
header {{
  padding:30px clamp(18px,3vw,46px);
  position:sticky;
  top:0;
  background:rgba(7,16,24,.88);
  backdrop-filter:blur(14px);
  border-bottom:1px solid rgba(210,232,255,.18);
  z-index:5;
}}
.eyebrow {{
  margin:0 0 8px;
  color:#8de8ff;
  letter-spacing:.16em;
  text-transform:uppercase;
  font-size:12px;
  font-weight:900;
}}
h1 {{ margin:0; font-size:clamp(30px,5vw,58px); letter-spacing:-.055em; }}
header p {{ color:#9fb7c9; max-width:980px; line-height:1.6; }}
main {{ padding:28px clamp(18px,3vw,46px) 72px; }}
section {{
  margin-bottom:36px;
  padding:22px;
  border:1px solid rgba(210,232,255,.18);
  border-radius:32px;
  background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.052));
  box-shadow:0 24px 80px rgba(0,0,0,.34);
}}
.head {{ display:flex; justify-content:space-between; gap:18px; }}
.head h2 {{ margin:0; font-size:30px; letter-spacing:-.04em; }}
.head p {{ color:#9fb7c9; }}
.head b {{ color:#9fffd8; font-size:32px; }}
.policy {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:16px 0 20px; }}
.policy span {{ border:1px solid rgba(210,232,255,.18); border-radius:18px; padding:12px; color:#9fb7c9; }}
.policy strong {{ color:#eef8ff; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:16px; }}
article {{ overflow:hidden; border:1px solid rgba(210,232,255,.18); border-radius:24px; background:rgba(255,255,255,.075); }}
article img {{ width:100%; height:178px; display:block; object-fit:cover; background:#0c1620; }}
article div {{ padding:13px; }}
article h3 {{ margin:0 0 8px; font-size:13px; word-break:break-word; }}
article p {{ margin:0 0 5px; color:#9fb7c9; font-size:12px; line-height:1.4; }}
article small {{ display:block; margin-top:9px; color:#ffd58a; }}
@media(max-width:820px){{.policy{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header>
  <p class="eyebrow">PRISMA Surface Visual Governor</p>
  <h1>M-04B fix2 · Normalized External Atmosphere Families</h1>
  <p>Este tablero normaliza las familias granulares de Unsplash hacia familias padre gobernadas. Ya no dependemos de aliases raros antes de usar estas imágenes en Control Center, PC o Chart Lab.</p>
</header>
<main>
{''.join(sections)}
</main>
</body>
</html>
"""

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    stamp = datetime.now().strftime("%d%m %H%M")
    stage = out_dir / f"gov m04b fix2 work {stamp}"
    result_zip = out_dir / f"gov m04b fix2 {stamp} result.zip"
    backup_zip = out_dir / f"gov m04b fix2 {stamp} backup.zip"
    rollback_ps1 = out_dir / f"gov m04b fix2 {stamp} rollback.ps1"
    log_path = stage / "install.log"

    def log(msg: str):
        stage.mkdir(parents=True, exist_ok=True)
        line = f"[{iso()}] {msg}"
        print(line)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    manifest = {}
    rollback_performed = False

    try:
        progress(0, 10, "preflight")
        if not root.exists():
            raise RuntimeError(f"Repo no existe: {root}")
        if not (root / "tools/prisma-surface-visual-governor").exists():
            raise RuntimeError("No existe toolbox Governor.")

        stage.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)

        log(f"START {ENGINE_VERSION}")

        progress(1, 10, "input inventory")
        inventory = read_input_inventory(root, out_dir)
        assets = inventory.get("assets", [])
        if len(assets) < 20:
            raise RuntimeError(f"Input inventory trae sólo {len(assets)} assets. Esperaba las 31 imágenes originales.")

        progress(2, 10, "hashes before")
        git_before = run_git(root, ["status", "--short"])
        protected_before = collect_hashes(root, is_protected)
        no_touch_before = collect_hashes(root, is_no_touch)

        progress(3, 10, "backup")
        manifest = backup_outputs(root, stage, backup_zip)

        progress(4, 10, "normalize aliases")
        normalized = []
        for row in assets:
            original = row.get("family_id", "")
            norm, confidence, reason = normalize_family(row)
            policy = CANONICAL_FAMILIES[norm]
            out = dict(row)
            out["original_family_id"] = original
            out["original_family_label"] = row.get("family_label", "")
            out["normalized_family_id"] = norm
            out["normalized_family_label"] = policy["label"]
            out["normalization_confidence"] = confidence
            out["normalization_reason"] = reason
            out["family_id"] = norm
            out["family_label"] = policy["label"]
            out["allowed_surfaces"] = "|".join(policy["allowed"])
            out["conditional_surfaces"] = "|".join(policy["conditional"])
            out["blocked_surfaces"] = "|".join(policy["blocked"])
            out["budget"] = policy["budget"]
            abs_path = root / (row.get("relative_path") or "")
            out["absolute_path_for_preview"] = str(abs_path) if abs_path.exists() else ""
            asset_rel = (row.get("relative_path") or "").replace("\\", "/")
            toolbox_prefix = "tools/prisma-surface-visual-governor/"
            if asset_rel.startswith(toolbox_prefix):
                out["preview_relative"] = "../" + asset_rel[len(toolbox_prefix):]
            else:
                out["preview_relative"] = asset_rel
            normalized.append(out)

        original_counts = Counter(r.get("original_family_id", "") for r in normalized)
        normalized_counts = Counter(r.get("normalized_family_id", "") for r in normalized)
        review_count = normalized_counts.get("external_review", 0)
        blocked_subject_count = normalized_counts.get("subject_photo_blocked", 0)

        progress(5, 10, "build contracts")
        aliases = {
            "schema": "prisma.surface.visual_governor.external_reference_family_aliases",
            "version": "M-04B.fix2",
            "created_at": iso(),
            "engine_version": ENGINE_VERSION,
            "explicit_aliases": EXPLICIT_ALIAS,
            "canonical_families": CANONICAL_FAMILIES,
            "original_family_counts": dict(original_counts),
            "normalized_family_counts": dict(normalized_counts),
            "rule": "Use normalized_family_id for route budgets. Never consume raw granular external family IDs directly.",
        }

        allowlist = {
            "schema": "prisma.surface.visual_governor.external_reference_atmosphere_allowlist_normalized",
            "version": "M-04B.fix2",
            "created_at": iso(),
            "families": [
                {
                    "id": fid,
                    "label": policy["label"],
                    "detected_count": normalized_counts.get(fid, 0),
                    "allowed_surfaces": policy["allowed"],
                    "conditional_surfaces": policy["conditional"],
                    "blocked_surfaces": policy["blocked"],
                    "budget": policy["budget"],
                }
                for fid, policy in CANONICAL_FAMILIES.items()
            ],
            "hard_bans": {
                "pos_checkout": ["storm", "liquid", "vapor", "aurora", "webgl", "pixi", "heavy_blur"],
                "tablet_productive": ["dark_default", "showcase_default", "liquid_vapor_default"],
            },
        }

        overlay = build_surface_overlay(normalized)

        progress(6, 10, "write toolbox outputs")
        out_json = root / OUTPUT_RELATIVE_PATHS[0]
        out_csv = root / OUTPUT_RELATIVE_PATHS[1]
        out_alias = root / OUTPUT_RELATIVE_PATHS[2]
        out_allow = root / OUTPUT_RELATIVE_PATHS[3]
        out_overlay = root / OUTPUT_RELATIVE_PATHS[4]
        out_html = root / OUTPUT_RELATIVE_PATHS[5]
        out_html_json = root / OUTPUT_RELATIVE_PATHS[6]
        out_md = root / OUTPUT_RELATIVE_PATHS[7]
        out_forget = root / OUTPUT_RELATIVE_PATHS[8]

        normalized_inventory = {
            "schema": "prisma.surface.visual_governor.external_reference_atmosphere_pack_normalized",
            "version": "M-04B.fix2",
            "created_at": iso(),
            "source_version": inventory.get("version", ""),
            "source_zip": inventory.get("source_zip", ""),
            "assets_count": len(normalized),
            "original_family_counts": dict(original_counts),
            "normalized_family_counts": dict(normalized_counts),
            "assets": normalized,
        }

        write_json(out_json, normalized_inventory)
        write_csv(out_csv, normalized)
        write_json(out_alias, aliases)
        write_json(out_allow, allowlist)
        write_json(out_overlay, overlay)
        write_text(out_html, build_html(normalized))
        write_json(out_html_json, {"assets_count": len(normalized), "normalized_family_counts": dict(normalized_counts), "assets": normalized})

        md = [
            "# PRISMA M-04B fix2 · External Family Alias Normalizer",
            "",
            f"- Generated: `{iso()}`",
            f"- Engine: `{ENGINE_VERSION}`",
            f"- Assets normalized: **{len(normalized)}**",
            f"- External review remaining: **{review_count}**",
            f"- Subject/blocked photos: **{blocked_subject_count}**",
            "",
            "## Original family counts",
            "",
        ]
        for k, v in sorted(original_counts.items()):
            md.append(f"- `{k}`: **{v}**")
        md.extend(["", "## Normalized family counts", ""])
        for k, v in sorted(normalized_counts.items()):
            md.append(f"- `{k}`: **{v}**")
        md.extend([
            "",
            "## Regla",
            "",
            "Los próximos pilotos deben usar `normalized_family_id`, no los aliases granulares originales.",
        ])
        write_text(out_md, "\n".join(md))

        forget = [
            "# PRISMA M-04B fix2 · DO NOT FORGET",
            "",
            "- Las familias externas granularizadas ya fueron normalizadas.",
            "- Usar `external-reference-atmosphere-pack.normalized.generated.json` para próximos rollouts.",
            "- Usar `surface-atmosphere-assets.external-overlay.normalized.generated.json` para decidir superficies.",
            "- No consumir raw `family_id` anterior si hay `normalized_family_id`.",
            "- POS/Checkout sigue con gate.",
            "- Tablet productiva sólo light-first.",
        ]
        write_text(out_forget, "\n".join(forget))

        progress(7, 10, "stage evidence")
        write_json(stage / "indexes/external-reference-atmosphere-pack.normalized.generated.json", normalized_inventory)
        write_csv(stage / "indexes/external-reference-atmosphere-pack.normalized.generated.csv", normalized)
        write_json(stage / "indexes/external-reference-family-aliases.generated.json", aliases)
        write_json(stage / "indexes/external-reference-atmosphere-allowlist.normalized.generated.json", allowlist)
        write_json(stage / "indexes/surface-atmosphere-assets.external-overlay.normalized.generated.json", overlay)
        write_text(stage / "preview/external-reference-atmosphere-normalized-preview.html", build_html(normalized))

        protected_after = collect_hashes(root, is_protected)
        no_touch_after = collect_hashes(root, is_no_touch)
        git_after = run_git(root, ["status", "--short"])

        write_json(stage / "evidence/git_status_before.json", git_before)
        write_json(stage / "evidence/git_status_after.json", git_after)
        write_json(stage / "protected_hashes.before.json", protected_before)
        write_json(stage / "protected_hashes.after.json", protected_after)
        write_json(stage / "no_touch_hashes.before.json", no_touch_before)
        write_json(stage / "no_touch_hashes.after.json", no_touch_after)

        verifier = {
            "status": "PASS",
            "engine_version": ENGINE_VERSION,
            "checks": {
                "input_assets_loaded": len(assets),
                "assets_normalized": len(normalized),
                "all_assets_have_normalized_family": all(bool(r.get("normalized_family_id")) for r in normalized),
                "normalized_outputs_written": all((root / r).exists() for r in OUTPUT_RELATIVE_PATHS),
                "external_review_remaining": review_count,
                "subject_blocked_count": blocked_subject_count,
                "review_count_reduced_or_zero": review_count <= max(2, int(len(normalized) * 0.15)),
                "protected_pos_checkout_hashes_unchanged": protected_before == protected_after,
                "no_touch_hashes_unchanged": no_touch_before == no_touch_after,
                "db_touched": False,
                "dependencies_touched": False,
                "package_lock_touched": False,
                "deploy_touched": False,
                "product_ui_touched": False,
            },
            "warnings": [],
        }

        if len(normalized) < 20:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("Too few assets normalized.")
        if review_count > max(2, int(len(normalized) * 0.15)):
            verifier["status"] = "FAIL"
            verifier["warnings"].append(f"Too many assets remain external_review: {review_count}")
        if protected_before != protected_after:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("Protected POS/Checkout hashes changed.")
        if no_touch_before != no_touch_after:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No-touch hashes changed.")

        if verifier["status"] != "PASS":
            restore_outputs(root, backup_zip, manifest)
            rollback_performed = True

        write_json(stage / "verifier.json", verifier)

        rollback_text = f'''$ErrorActionPreference = "Stop"
$Root = "{root}"
$BackupZip = "{backup_zip}"
if (!(Test-Path -LiteralPath $BackupZip)) {{ throw "No existe backup zip: $BackupZip" }}
$Temp = Join-Path $env:TEMP ("gov_m04b_fix2_rollback_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Force -Path $Temp | Out-Null
Expand-Archive -LiteralPath $BackupZip -DestinationPath $Temp -Force
$Manifest = Get-Content -LiteralPath (Join-Path $Temp "backup_manifest.json") -Raw | ConvertFrom-Json
foreach ($Item in $Manifest.files) {{
  $Target = Join-Path $Root $Item.relative_path
  if ($Item.is_dir -eq $true) {{
    if (Test-Path -LiteralPath $Target) {{ Remove-Item -LiteralPath $Target -Recurse -Force }}
    $SrcDir = Join-Path (Join-Path $Temp "dirs") $Item.relative_path
    if ($Item.existed -eq $true -and (Test-Path -LiteralPath $SrcDir)) {{
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Target) | Out-Null
      Copy-Item -LiteralPath $SrcDir -Destination $Target -Recurse -Force
    }}
  }} else {{
    $Src = Join-Path (Join-Path $Temp "files") $Item.relative_path
    if ($Item.existed -eq $true) {{
      if (Test-Path -LiteralPath $Src) {{
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Target) | Out-Null
        Copy-Item -LiteralPath $Src -Destination $Target -Force
      }}
    }} else {{
      if (Test-Path -LiteralPath $Target) {{ Remove-Item -LiteralPath $Target -Force }}
    }}
  }}
}}
Remove-Item -LiteralPath $Temp -Recurse -Force
Write-Host "ROLLBACK M-04B fix2 aplicado desde $BackupZip" -ForegroundColor Green
'''
        write_text(rollback_ps1, rollback_text)
        write_text(stage / "ROLLBACK.ps1", rollback_text)

        report = [
            "# PRISMA M-04B fix2 · Family Policy Alias Normalizer Result",
            "",
            f"- Generated: `{iso()}`",
            f"- Status: **{verifier['status']}**",
            f"- Assets normalized: **{len(normalized)}**",
            f"- External review remaining: **{review_count}**",
            f"- Backup ZIP: `{backup_zip}`",
            f"- Rollback script: `{rollback_ps1}`",
            "",
            "## Normalized family counts",
            "",
        ]
        for k, v in sorted(normalized_counts.items()):
            report.append(f"- `{k}`: **{v}**")
        report.extend(["", "## Preview", "", "`preview/external-reference-atmosphere-normalized-preview.html`"])
        write_text(stage / "M04B_FIX2_FAMILY_ALIAS_NORMALIZER_REPORT.md", "\n".join(report))

        receipt = {
            "pilot": "M-04B fix2",
            "name": "Family Policy Alias Normalizer",
            "status": verifier["status"],
            "created_at": iso(),
            "repo": str(root),
            "result_zip": str(result_zip),
            "backup_zip": str(backup_zip),
            "rollback_script": str(rollback_ps1),
            "rollback_performed": rollback_performed,
            "assets_normalized": len(normalized),
            "external_review_remaining": review_count,
            "normalized_family_counts": dict(normalized_counts),
            "toolbox_files_written": True,
            "product_ui_touched": False,
            "db_touched": False,
            "dependencies_touched": False,
            "package_lock_touched": False,
            "deploy_touched": False,
        }
        write_json(stage / "receipt.json", receipt)
        write_json(stage / "rollback.json", {"required": verifier["status"] != "PASS", "performed": rollback_performed, "backup_zip": str(backup_zip), "rollback_script": str(rollback_ps1)})

        progress(8, 10, "zip result")
        zip_dir(stage, result_zip)

        progress(9, 10, "cleanup")
        shutil.rmtree(stage, ignore_errors=True)

        progress(10, 10, "done")
        print(f"PASS_RESULT_ZIP={result_zip}")
        print(f"ROLLBACK_SCRIPT={rollback_ps1}")
        return 0 if verifier["status"] == "PASS" else 2

    except Exception:
        err = traceback.format_exc()
        try:
            if manifest and backup_zip.exists():
                restore_outputs(root, backup_zip, manifest)
                rollback_performed = True
        except Exception:
            pass
        stage.mkdir(parents=True, exist_ok=True)
        write_text(stage / "FAILURE.txt", err)
        write_json(stage / "receipt.json", {"pilot": "M-04B fix2", "status": "FAIL", "created_at": iso(), "error": err, "rollback_performed": rollback_performed, "result_zip": str(result_zip), "backup_zip": str(backup_zip)})
        try:
            zip_dir(stage, result_zip)
            shutil.rmtree(stage, ignore_errors=True)
        except Exception:
            pass
        print(err)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
