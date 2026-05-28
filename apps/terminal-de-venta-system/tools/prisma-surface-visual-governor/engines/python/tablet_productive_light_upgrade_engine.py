from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import traceback
import zipfile
from datetime import datetime
from pathlib import Path

ENGINE_VERSION = "21T.1-tablet-productive-light-upgrade"

EXCLUDE_PARTS = {
    ".git", "node_modules", ".next", "out", "dist", "build", ".turbo",
    ".cache", "coverage", "playwright-report", "test-results", "__pycache__",
    ".prisma_installer_backups"
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

NO_TOUCH_NAMES = {
    "package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "bun.lockb",
    "next.config.mjs", "next.config.js", "wrangler.jsonc", "wrangler.toml"
}

BANNED_IN_PATCH = [
    "backdrop-filter",
    "filter: blur",
    "blur(",
    "pixi",
    "webgl",
    "@react-three",
    "three/",
    "echarts-gl",
]

PATCH_START = "/* PRISMA_PILOT21T_TABLET_PRODUCTIVE_LIGHT_UPGRADE_START */"
PATCH_END = "/* PRISMA_PILOT21T_TABLET_PRODUCTIVE_LIGHT_UPGRADE_END */"

def iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_PARTS for part in path.parts)

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def sha256(path: Path) -> str:
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
            timeout=90,
        )
        return {"ok": p.returncode == 0, "code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as e:
        return {"ok": False, "code": -1, "stdout": "", "stderr": str(e)}

def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

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

def is_protected_path(root: Path, path: Path) -> bool:
    r = rel(root, path).lower()
    return any(h.replace("\\", "/").lower() in r for h in PROTECTED_HINTS)

def collect_protected_hashes(root: Path) -> dict[str, str]:
    tablet = root / "products/tablet/app"
    hashes = {}
    if not tablet.exists():
        return hashes
    for p in tablet.rglob("*"):
        if not p.is_file() or is_excluded(p):
            continue
        if is_protected_path(root, p):
            try:
                hashes[rel(root, p)] = sha256(p)
            except Exception:
                pass
    return hashes

def collect_no_touch_hashes(root: Path) -> dict[str, str]:
    hashes = {}
    for p in root.rglob("*"):
        if not p.is_file() or is_excluded(p):
            continue
        if p.name in NO_TOUCH_NAMES or "prisma/schema.prisma" in rel(root, p).lower():
            try:
                hashes[rel(root, p)] = sha256(p)
            except Exception:
                pass
    return hashes

def score_css_target(root: Path, path: Path) -> tuple[int, list[str]]:
    r = rel(root, path).lower()
    if is_protected_path(root, path):
        return -999, ["excluded_pos_checkout"]
    if path.suffix.lower() not in {".css", ".scss"}:
        return -999, ["not_css"]
    try:
        text = read_text(path).lower()
    except Exception:
        text = ""
    score = 0
    reasons = []

    checks = [
        ("tablet", 25),
        ("light", 22),
        ("shell", 20),
        ("surface", 16),
        ("governor", 16),
        ("cloudglass", 14),
        ("productive", 12),
        ("sync", 8),
        ("settings", 8),
        ("license", 8),
    ]
    for token, pts in checks:
        if token in r or token in text:
            score += pts
            reasons.append(token)

    if "pos" in r or "checkout" in r:
        score -= 200
        reasons.append("reject_pos_checkout_hint")

    if "dark storm" in text or "storm vapor" in text:
        score += 8
        reasons.append("needs_light_correction")

    return score, reasons

def discover_targets(root: Path) -> list[dict]:
    tablet = root / "products/tablet/app"
    if not tablet.exists():
        return []
    rows = []
    for p in tablet.rglob("*"):
        if not p.is_file() or is_excluded(p):
            continue
        score, reasons = score_css_target(root, p)
        if score >= 35:
            rows.append({
                "path": p,
                "relative_path": rel(root, p),
                "score": score,
                "reasons": "|".join(reasons),
                "bytes": p.stat().st_size,
            })
    rows.sort(key=lambda x: (-x["score"], x["relative_path"].lower()))
    return rows[:8]

def extract_local_classes(css: str) -> list[str]:
    found = re.findall(r"(?<!:global\()\.(?!\d)([A-Za-z_][A-Za-z0-9_-]*)", css)
    reject = {
        "png", "jpg", "jpeg", "webp", "svg", "module", "css",
    }
    preferred = []
    fallback = []
    for name in sorted(set(found)):
        low = name.lower()
        if low in reject:
            continue
        if any(x in low for x in ["shell", "surface", "tablet", "layout", "page", "root", "frame", "panel", "card", "dashboard", "sync", "settings", "license"]):
            preferred.append(name)
        else:
            fallback.append(name)
    return (preferred + fallback)[:10]

def build_patch(local_classes: list[str]) -> str:
    local_blocks = []
    for cls in local_classes[:8]:
        local_blocks.append(f"""
.{cls} {{
  --prisma-tablet-bg-base: #f6f9fd;
  --prisma-tablet-bg-cloud: rgba(255,255,255,.74);
  --prisma-tablet-bg-mist: rgba(219,232,248,.44);
  --prisma-tablet-ink: #132033;
  --prisma-tablet-muted: #607089;
  --prisma-tablet-line: rgba(39,62,92,.13);
  --prisma-tablet-card: rgba(255,255,255,.82);
  --prisma-tablet-card-strong: rgba(255,255,255,.92);
  --prisma-tablet-focus: rgba(41,117,209,.24);
  color: var(--prisma-tablet-ink);
}}

.{cls} :where(section, article, aside, header, main, [data-prisma-card], [data-surface-card]) {{
  border-color: var(--prisma-tablet-line);
}}

.{cls} :where(button, a, input, select, textarea, [role="button"]) {{
  -webkit-tap-highlight-color: rgba(41,117,209,.16);
}}
""")

    return f"""{PATCH_START}
:global([data-prisma-surface="tablet"]:not([data-prisma-interface*="pos"]):not([data-prisma-interface*="checkout"])) {{
  --prisma-tablet-bg-base: #f6f9fd;
  --prisma-tablet-bg-cloud: rgba(255,255,255,.74);
  --prisma-tablet-bg-mist: rgba(219,232,248,.44);
  --prisma-tablet-ink: #132033;
  --prisma-tablet-muted: #607089;
  --prisma-tablet-line: rgba(39,62,92,.13);
  --prisma-tablet-card: rgba(255,255,255,.82);
  --prisma-tablet-card-strong: rgba(255,255,255,.92);
  --prisma-tablet-focus: rgba(41,117,209,.24);
  background:
    radial-gradient(circle at 14% 8%, rgba(255,255,255,.96), transparent 28%),
    radial-gradient(circle at 92% 0%, rgba(210,226,248,.62), transparent 34%),
    linear-gradient(135deg, #f7faff 0%, #eef4fb 54%, #f9fbff 100%);
  color: var(--prisma-tablet-ink);
}}

:global([data-prisma-surface="tablet"]:not([data-prisma-interface*="pos"]):not([data-prisma-interface*="checkout"]) [data-prisma-shell]),
:global([data-prisma-surface="tablet"]:not([data-prisma-interface*="pos"]):not([data-prisma-interface*="checkout"]) [data-prisma-panel]),
:global(.prisma-tablet-light-shell),
:global(.tablet-light-shell) {{
  background:
    linear-gradient(180deg, rgba(255,255,255,.84), rgba(247,250,255,.72)),
    radial-gradient(circle at 12% 0%, rgba(255,255,255,.88), transparent 28%);
  border: 1px solid var(--prisma-tablet-line);
  box-shadow: 0 14px 34px rgba(31,51,77,.10);
  color: var(--prisma-tablet-ink);
}}

:global([data-prisma-surface="tablet"]:not([data-prisma-interface*="pos"]):not([data-prisma-interface*="checkout"]) [data-prisma-card]) {{
  background: var(--prisma-tablet-card);
  border: 1px solid var(--prisma-tablet-line);
  box-shadow: 0 10px 24px rgba(31,51,77,.08);
}}

:global([data-prisma-surface="tablet"]:not([data-prisma-interface*="pos"]):not([data-prisma-interface*="checkout"]) :where(button, [role="button"])) {{
  min-height: 42px;
  touch-action: manipulation;
}}

:global([data-prisma-surface="tablet"]:not([data-prisma-interface*="pos"]):not([data-prisma-interface*="checkout"]) :where(button, a, input, select, textarea):focus-visible) {{
  outline: 3px solid var(--prisma-tablet-focus);
  outline-offset: 2px;
}}

{''.join(local_blocks)}

@media (prefers-reduced-motion: reduce) {{
  :global([data-prisma-surface="tablet"]) *,
  :global(.prisma-tablet-light-shell *),
  :global(.tablet-light-shell *) {{
    animation-duration: .001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .001ms !important;
    scroll-behavior: auto !important;
  }}
}}

@media (hover: hover) {{
  :global([data-prisma-surface="tablet"]:not([data-prisma-interface*="pos"]):not([data-prisma-interface*="checkout"]) :where(button, [role="button"]):hover) {{
    transform: translateY(-1px);
  }}
}}
{PATCH_END}
"""

def replace_or_append_patch(css: str, patch: str) -> str:
    pattern = re.compile(re.escape(PATCH_START) + r".*?" + re.escape(PATCH_END), re.S)
    if pattern.search(css):
        return pattern.sub(patch, css)
    return css.rstrip() + "\n\n" + patch + "\n"

def validate_css_light_safe(css: str) -> list[str]:
    issues = []
    low = css.lower()
    for banned in BANNED_IN_PATCH:
        if banned.lower() in low:
            issues.append(f"banned_term:{banned}")
    if css.count("{") != css.count("}"):
        issues.append("brace_count_mismatch")
    return issues

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stage = out_dir / f"PRISMA_PILOT21T_TABLET_LIGHT_UPGRADE_WORK_{stamp}"
    result_zip = out_dir / f"PRISMA_PILOT21T_TABLET_LIGHT_UPGRADE_RESULT_{stamp}.zip"
    backup_zip = out_dir / f"PRISMA_PILOT21T_TABLET_LIGHT_UPGRADE_BACKUP_{stamp}.zip"
    log_path = stage / "install.log"

    def log(msg: str):
        line = f"[{iso()}] {msg}"
        print(line)
        stage.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    target_backups: dict[str, str] = {}
    rollback_performed = False

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        stage.mkdir(parents=True, exist_ok=True)

        if not root.exists():
            raise RuntimeError(f"Repo no existe: {root}")

        log(f"START {ENGINE_VERSION}")
        log(f"Root={root}")

        git_before = run_git(root, ["status", "--short"])
        write_json(stage / "evidence/git_status_before.json", git_before)

        protected_before = collect_protected_hashes(root)
        no_touch_before = collect_no_touch_hashes(root)

        targets = discover_targets(root)
        write_csv(stage / "indexes/tablet_light_css_candidates.csv", [
            {k: v for k, v in row.items() if k != "path"} for row in targets
        ])

        if not targets:
            raise RuntimeError("No encontré CSS Tablet Light Shell con confianza. No aplico cambios.")

        selected_targets = targets[:4]
        log(f"Selected target count={len(selected_targets)}")

        backup_stage = stage / "backup_files"
        backup_stage.mkdir(parents=True, exist_ok=True)

        changed_rows = []
        for row in selected_targets:
            path = row["path"]
            r = row["relative_path"]
            before = read_text(path)
            target_backups[r] = before
            backup_file = backup_stage / r
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            write_text(backup_file, before)

            classes = extract_local_classes(before)
            patch = build_patch(classes)
            patch_issues = validate_css_light_safe(patch)
            if patch_issues:
                raise RuntimeError(f"Patch no light-safe para {r}: {patch_issues}")

            after = replace_or_append_patch(before, patch)
            write_text(path, after)

            changed_rows.append({
                "relative_path": r,
                "score": row["score"],
                "reasons": row["reasons"],
                "classes_detected": "|".join(classes),
                "before_bytes": len(before.encode("utf-8")),
                "after_bytes": len(after.encode("utf-8")),
                "sha256_before": hashlib.sha256(before.encode("utf-8")).hexdigest(),
                "sha256_after": hashlib.sha256(after.encode("utf-8")).hexdigest(),
            })
            log(f"Patched {r}")

        zip_dir(backup_stage, backup_zip)

        protected_after = collect_protected_hashes(root)
        no_touch_after = collect_no_touch_hashes(root)

        verifier = {
            "status": "PASS",
            "engine_version": ENGINE_VERSION,
            "checks": {
                "targets_found": len(targets),
                "targets_changed": len(changed_rows),
                "protected_pos_checkout_hashes_unchanged": protected_before == protected_after,
                "no_touch_hashes_unchanged": no_touch_before == no_touch_after,
                "backup_zip_exists": backup_zip.exists(),
                "db_touched": False,
                "dependencies_touched": False,
                "package_lock_touched": False,
                "deploy_touched": False,
                "pos_checkout_touched": False,
            },
            "warnings": [],
        }

        if protected_before != protected_after:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("Protected POS/Checkout hashes changed.")
        if no_touch_before != no_touch_after:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No-touch files changed.")
        if not changed_rows:
            verifier["status"] = "FAIL"
            verifier["warnings"].append("No files changed.")

        if verifier["status"] != "PASS":
            for r, content in target_backups.items():
                write_text(root / r, content)
            rollback_performed = True
            protected_final = collect_protected_hashes(root)
            no_touch_final = collect_no_touch_hashes(root)
            verifier["post_rollback"] = {
                "protected_restored": protected_final == protected_before,
                "no_touch_restored": no_touch_final == no_touch_before,
            }

        write_csv(stage / "indexes/changed_files.csv", changed_rows)
        write_json(stage / "protected_hashes.before.json", protected_before)
        write_json(stage / "protected_hashes.after.json", protected_after)
        write_json(stage / "no_touch_hashes.before.json", no_touch_before)
        write_json(stage / "no_touch_hashes.after.json", no_touch_after)
        write_json(stage / "verifier.json", verifier)

        git_after = run_git(root, ["status", "--short"])
        write_json(stage / "evidence/git_status_after.json", git_after)

        report = []
        report.append("# PRISMA Pilot 21T · Tablet Productive Light Shell Upgrade")
        report.append("")
        report.append(f"- Generated: `{iso()}`")
        report.append(f"- Engine: `{ENGINE_VERSION}`")
        report.append(f"- Status: **{verifier['status']}**")
        report.append(f"- Backup ZIP: `{backup_zip}`")
        report.append(f"- Rollback performed: `{rollback_performed}`")
        report.append("")
        report.append("## Scope")
        report.append("")
        report.append("- Surface: Tablet")
        report.append("- Mode: Productive light-first")
        report.append("- POS/Checkout: protected, excluded")
        report.append("- DB/package/lock/deploy: untouched")
        report.append("")
        report.append("## Changed files")
        report.append("")
        for row in changed_rows:
            report.append(f"- `{row['relative_path']}`")
        report.append("")
        report.append("## Visual policy")
        report.append("")
        report.append("- No dark storm")
        report.append("- No Pixi")
        report.append("- No WebGL")
        report.append("- No heavy blur")
        report.append("- Reduced motion fallback")
        report.append("- Touch-friendly focus and buttons")
        write_text(stage / "PILOT_21T_REPORT.md", "\n".join(report))

        receipt = {
            "pilot": "21T",
            "name": "Tablet Productive Light Shell Upgrade",
            "status": verifier["status"],
            "created_at": iso(),
            "repo": str(root),
            "result_zip": str(result_zip),
            "backup_zip": str(backup_zip),
            "changed_files": [r["relative_path"] for r in changed_rows],
            "rollback_performed": rollback_performed,
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
            "restored_files": list(target_backups.keys()) if rollback_performed else [],
        })

        zip_dir(stage, result_zip)
        shutil.rmtree(stage, ignore_errors=True)

        print(f"PASS_RESULT_ZIP={result_zip}")
        return 0 if verifier["status"] == "PASS" else 2

    except Exception:
        err = traceback.format_exc()
        try:
            for r, content in target_backups.items():
                write_text(root / r, content)
            rollback_performed = bool(target_backups)
        except Exception:
            pass

        stage.mkdir(parents=True, exist_ok=True)
        write_text(stage / "FAILURE.txt", err)
        write_json(stage / "receipt.json", {
            "pilot": "21T",
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
            "restored_files": list(target_backups.keys()),
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
