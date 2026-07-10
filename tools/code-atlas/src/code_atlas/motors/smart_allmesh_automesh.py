#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRISMA AutoMesh v5
Task-scoped Authority Mesh generator with mandatory Layer Map.
Read-only against repo: no patch, no process control, no dev server, no hot Prisma.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

DEFAULT_OUT = Path(r"F:\descargasf")
DEFAULT_REPOS = [
    Path.cwd(),
    Path(r"F:\repos\hitech-os"),
    Path(r"F:\repos\hitech-os\apps\terminal-de-venta-system"),
]
EXCLUDE_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "out", ".turbo", ".cache",
    ".prisma_installer_backups", "coverage", "playwright-report", "test-results",
    ".venv", "venv", "__pycache__", ".pytest_cache", ".pnpm-store", "tmp", "temp"
}
TEXT_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".css", ".scss", ".sass",
    ".json", ".md", ".yml", ".yaml", ".html", ".txt", ".ps1", ".py", ".prisma", ".svg"
}
SURFACE_ROOTS = {
    "tablet": [
        "apps/terminal-de-venta-system/products/tablet",
        "products/tablet",
        "tablet/app",
    ],
    "pc": ["apps/terminal-de-venta-system/products/pc", "products/pc", "pc"],
    "mobile": ["apps/terminal-de-venta-system/products/mobile", "products/mobile", "mobile"],
    "app": ["apps/terminal-de-venta-system/products/mobile", "products/mobile", "mobile"],
    "chart_lab": ["chart", "chart-lab", "lab"],
    "shared_ui": ["shared", "packages", "components/ui", "shared-ui"],
    "governance": [".governance", "docs/ops", "apps/terminal-de-venta-system/docs/ops", "tools/quality", "tools/prisma"],
}
REQUIRED_REL = [
    "docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md",
    "apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md",
    "apps/terminal-de-venta-system/.governance/current/AUTHORITY_READSET.lock.json",
    "apps/terminal-de-venta-system/.governance/current/APP_IMPACT_MATRIX.md",
    "apps/terminal-de-venta-system/.governance/current/CONTRACT_AND_GATE_MATRIX.json",
    "apps/terminal-de-venta-system/.governance/current/MISSING_OR_UNMAPPED_RISK.md",
    "apps/terminal-de-venta-system/.governance/current/AGENT_PROMPT_ENVELOPE.md",
    "apps/terminal-de-venta-system/.governance/current/AUTHORITY_MESH_REPORT.md",
]
POS_KNOWN_OWNER_HINTS = [
    "apps/terminal-de-venta-system/products/tablet/app/app/pos/layout.tsx",
    "apps/terminal-de-venta-system/products/tablet/app/app/pos/page.tsx",
    "apps/terminal-de-venta-system/products/tablet/app/app/pos/prisma-pos-light-safe-shell.module.css",
    "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css",
    "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.visual.tokens.css",
    "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.visual.tokens.generated.css",
]


def progress(done: int, total: int, label: str) -> None:
    total = max(total, 1)
    pct = int(done * 100 / total)
    fill = int(30 * pct / 100)
    bar = "█" * fill + "░" * (30 - fill)
    print(f"[{bar}] {pct:3d}% | falta {100-pct:3d}% | {label}", flush=True)


def run_git(repo: Path, args: List[str], timeout: int = 45) -> Dict[str, Any]:
    try:
        p = subprocess.run(args, cwd=str(repo), text=True, encoding="utf-8", errors="replace",
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, shell=False)
        return {"args": args, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"args": args, "returncode": 999, "stdout": "", "stderr": repr(exc)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(repo: Path, p: Path) -> str:
    try:
        return p.relative_to(repo).as_posix()
    except Exception:
        return p.as_posix()


def is_skipped(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)


def read_text(path: Path, max_bytes: int = 2_500_000) -> str | None:
    try:
        if path.stat().st_size > max_bytes:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def find_repo(explicit: str | None) -> Path:
    candidates: List[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(DEFAULT_REPOS)
    seen = set()
    for c in candidates:
        try:
            c = c.resolve()
        except Exception:
            continue
        for p in [c] + list(c.parents):
            key = str(p).lower()
            if key in seen:
                continue
            seen.add(key)
            if (p / ".git").exists():
                return p
    raise RuntimeError("NO_REPO: no encontré repo Git. Usa -Repo F:\\repos\\hitech-os")


def tokenize(task: str, surface: str) -> List[str]:
    raw = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_./:-]{3,}", task)
    extras = [
        surface, "pos", "/pos", "tablet", "layout", "header", "search", "busqueda", "búsqueda",
        "category", "rail", "product", "grid", "ticket", "cart", "checkout", "payment", "dock",
        "reembolso", "guardar", "cancelar", "venta", "limpiar", "button", "className", "module.css",
        "layer", "overlay", "pseudo", "background", "visual", "tokens", "zero-important"
    ]
    seen, out = set(), []
    for x in raw + extras:
        y = x.strip().strip('"\'`,;()[]{}').lower()
        if len(y) >= 3 and y not in seen:
            seen.add(y)
            out.append(y)
    return out


def detect_surfaces(task: str, surface: str) -> Dict[str, Any]:
    low = task.lower()
    included = []
    requested = surface.lower().strip() if surface else ""
    aliases = {"mobile_app": "mobile", "movil": "mobile", "móvil": "mobile"}
    requested = aliases.get(requested, requested)
    if requested:
        included.append(requested)
    else:
        if any(x in low for x in ["tablet", "/pos", "pos", "carrito", "checkout"]): included.append("tablet")
        if re.search(r"\bpc\b", low): included.append("pc")
        if any(x in low for x in ["mobile", "movil", "móvil", " app "]): included.append("mobile")
        if "chart" in low or "lab" in low: included.append("chart_lab")
        if "shared" in low or "global" in low: included.append("shared_ui")
    if not included:
        included = ["unknown_task_surface"]
    all_surfaces = ["tablet", "pc", "mobile", "chart_lab", "shared_ui"]
    return {"included": sorted(set(included)), "excluded": [s for s in all_surfaces if s not in included]}


def iter_files(repo: Path) -> List[Path]:
    out = []
    for root, dirs, files in os.walk(repo):
        rootp = Path(root)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        if is_skipped(rootp):
            continue
        for name in files:
            p = rootp / name
            if p.suffix.lower() in TEXT_EXTS and not is_skipped(p):
                out.append(p)
    return out


def shard(items: List[Path], count: int) -> List[List[Path]]:
    count = max(1, min(count, max(1, len(items))))
    buckets = [[] for _ in range(count)]
    for i, item in enumerate(items):
        buckets[i % count].append(item)
    return buckets


def score_one(repo: Path, p: Path, terms: List[str], surfaces: Dict[str, Any]) -> Dict[str, Any] | None:
    txt = read_text(p)
    if txt is None:
        return None
    rp = rel(repo, p)
    lowp = rp.lower()
    lowt = txt.lower()
    score = 0
    found: List[str] = []
    for term in terms:
        if term in lowp:
            score += 12
            found.append(term)
        c = lowt.count(term)
        if c:
            score += min(24, c * 3)
            found.append(term)
    for s in surfaces["included"]:
        for root in SURFACE_ROOTS.get(s, []):
            if root.lower() in lowp:
                score += 25
                found.append(f"surface:{s}")
    if any(h.lower() == lowp for h in POS_KNOWN_OWNER_HINTS):
        score += 90
        found.append("known-pos-owner")
    if "/pos/" in lowp or "components/pos" in lowp or "pos." in lowp:
        score += 30
        found.append("pos-path")
    if ".governance/current" in lowp:
        score += 20
        found.append("governance-current")
    if "prisma_field_manual" in lowp:
        score += 80
        found.append("manual")
    if p.suffix.lower() in {".css", ".scss", ".sass"} and any(x in lowt for x in ["button", "grid", "dock", "panel", "layer", "background"]):
        score += 16
        found.append("css-visual-owner")
    if p.suffix.lower() in {".tsx", ".jsx", ".ts", ".js"} and any(x in lowt for x in ["classname", "button", "pos", "cart", "checkout", "product"]):
        score += 16
        found.append("component-owner")
    if score <= 0:
        return None
    snippets = []
    lines = txt.splitlines()
    needle = [x.replace("surface:", "") for x in found if len(x) > 2][:25]
    for i, line in enumerate(lines, 1):
        ll = line.lower()
        if any(n.lower() in ll for n in needle):
            snippets.append({"line": i, "text": line[:700]})
        if len(snippets) >= 20:
            break
    return {"path": rp, "score": score, "size": p.stat().st_size, "sha256": sha256(p), "suffix": p.suffix.lower(), "terms": sorted(set(found)), "snippets": snippets}


def scan_shard(args: Tuple[Path, List[Path], List[str], Dict[str, Any]]) -> List[Dict[str, Any]]:
    repo, files, terms, surfaces = args
    out = []
    for p in files:
        h = score_one(repo, p, terms, surfaces)
        if h:
            out.append(h)
    return out


def copy_selected(repo: Path, out_dir: Path, hits: List[Dict[str, Any]], max_files: int, max_mb: int) -> List[Dict[str, Any]]:
    selected: Dict[str, Dict[str, Any]] = {}
    for h in hits:
        selected[h["path"]] = h
    for path in REQUIRED_REL + POS_KNOWN_OWNER_HINTS:
        p = repo / path
        if p.exists() and p.is_file():
            selected[path] = {"path": path, "score": 999, "size": p.stat().st_size, "sha256": sha256(p), "suffix": p.suffix.lower(), "terms": ["required-or-known-owner"], "snippets": []}
    ranked = sorted(selected.values(), key=lambda x: (-x.get("score", 0), x["path"]))
    root = out_dir / "repo_files"
    root.mkdir(parents=True, exist_ok=True)
    total = 0
    copied = []
    for h in ranked:
        if len(copied) >= max_files:
            break
        p = repo / h["path"]
        if not p.exists() or not p.is_file():
            continue
        size = p.stat().st_size
        if h.get("score", 0) < 999 and total + size > max_mb * 1024 * 1024:
            continue
        dst = root / h["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        total += size
        copied.append({k: h[k] for k in ["path", "score", "size", "sha256", "suffix", "terms"] if k in h})
    return copied


def extract_selectors(txt: str | None, limit: int = 40) -> List[str]:
    if not txt:
        return []
    out = []
    for m in re.finditer(r"(?:^|\n)\s*([^@\n{}][^{}]{0,180})\s*\{", txt):
        s = re.sub(r"\s+", " ", m.group(1).strip())
        if s and s not in out:
            out.append(s)
        if len(out) >= limit:
            break
    return out


def extract_classnames(txt: str | None, limit: int = 40) -> List[str]:
    if not txt:
        return []
    out = []
    patterns = [r'className\s*=\s*"([^"]+)"', r"className\s*=\s*'([^']+)'", r"styles\.([A-Za-z0-9_-]+)"]
    for pat in patterns:
        for m in re.finditer(pat, txt):
            parts = re.split(r"\s+", m.group(1))
            for part in parts:
                val = part.strip("{} `.$[]()")
                if val and val not in out:
                    out.append(val)
                if len(out) >= limit:
                    return out
    return out


def layer_kind(path: str, suffix: str, txt: str | None) -> str:
    low = path.lower()
    body = (txt or "").lower()
    if "layout" in low: return "layout_shell"
    if low.endswith("page.tsx") or "/app/pos/" in low: return "route_or_page_owner"
    if suffix in {".css", ".scss", ".sass"}:
        if "module" in low: return "css_module_owner"
        return "visual_tokens_or_global_style"
    if "dock" in low or "action" in low or "button" in body: return "action_dock_or_controls"
    if "cart" in low or "ticket" in body or "checkout" in body: return "cart_ticket_checkout_layer"
    if "product" in low or "grid" in body: return "product_grid_layer"
    if "category" in low or "rail" in body: return "category_rail_layer"
    if ".governance" in low: return "governance_authority_layer"
    if "pos" in low: return "pos_component_layer"
    return "candidate_layer"


def build_layers(repo: Path, selected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    layers = []
    for item in selected:
        p = repo / item["path"]
        txt = read_text(p)
        layers.append({
            "path": item["path"],
            "layer_kind": layer_kind(item["path"], p.suffix.lower(), txt),
            "score": item.get("score", 0),
            "suffix": p.suffix.lower(),
            "selectors": extract_selectors(txt),
            "classnames": extract_classnames(txt),
        })
    return layers


def zip_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        dst.unlink()
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for p in src.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src.parent).as_posix())


def write_reports(out_dir: Path, repo: Path, args: argparse.Namespace, surfaces: Dict[str, Any], hits: List[Dict[str, Any]], selected: List[Dict[str, Any]], layers: List[Dict[str, Any]], git_state: Dict[str, Any]) -> None:
    reports = out_dir / "reports"
    auth = out_dir / ".governance" / "current"
    reports.mkdir(parents=True, exist_ok=True)
    auth.mkdir(parents=True, exist_ok=True)
    missing = []
    root_manual = "docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md"
    app_manual = "apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md"
    for p in REQUIRED_REL:
        if p == root_manual and ((repo / root_manual).exists() or (repo / app_manual).exists()):
            continue
        if p == app_manual and ((repo / root_manual).exists() or (repo / app_manual).exists()):
            continue
        if not (repo / p).exists():
            missing.append(p)
    readset = {
        "kind": "PRISMA_AUTHORITY_READSET",
        "version": "automesh-v5",
        "generated_at": _dt.datetime.now().isoformat(),
        "task": args.task,
        "repo": str(repo),
        "surface_argument": args.surface,
        "workers": args.workers,
        "shards": args.shards,
        "surfaces": surfaces,
        "git_state": git_state,
        "hits_count": len(hits),
        "selected_files_count": len(selected),
        "selected_files": selected,
        "missing_expected_authority_files": missing,
        "layer_map_required": True,
        "layer_map_count": len(layers),
        "constraints": {
            "read_only_repo_scan": True,
            "no_process_kill": True,
            "no_port_free": True,
            "no_dev_server_start": True,
            "no_hot_prisma_regeneration": True,
            "no_visual_patch_authorized_without_layer_map": True,
            "no_css_important": True,
            "no_priority_override_tokens": True,
        },
    }
    (auth / "AUTHORITY_READSET.lock.json").write_text(json.dumps(readset, indent=2, ensure_ascii=False), encoding="utf-8")
    (reports / "LAYERS_MAP.json").write_text(json.dumps(layers, indent=2, ensure_ascii=False), encoding="utf-8")
    lm = ["# LAYERS_MAP", "", f"Task: {args.task}", ""]
    for layer in layers:
        lm += [f"## {layer['path']}", f"- kind: `{layer['layer_kind']}`", f"- score: `{layer['score']}`"]
        if layer["selectors"]:
            lm.append("- selectors:")
            lm += [f"  - `{x}`" for x in layer["selectors"][:25]]
        if layer["classnames"]:
            lm.append("- classnames:")
            lm += [f"  - `{x}`" for x in layer["classnames"][:25]]
        lm.append("")
    (reports / "LAYERS_MAP.md").write_text("\n".join(lm), encoding="utf-8")
    impact = ["# APP_IMPACT_MATRIX", "", f"Task: {args.task}", "", "## Included", *[f"- {s}" for s in surfaces["included"]], "", "## Explicitly excluded", *[f"- {s}" for s in surfaces["excluded"]], "", "## Rule", "Patch must remain inside included surfaces unless this readset proves shared ownership."]
    (reports / "APP_IMPACT_MATRIX.md").write_text("\n".join(impact), encoding="utf-8")
    contract = {
        "task": args.task,
        "recommended_gates": ["zero-important gate", "focused static validation", "visual verification after patch", "no functional-smoke-only visual PASS"],
        "forbidden": ["git reset --hard", "git clean", "assume-unchanged", "process kill", "port free", "dev server start", "hot Prisma regeneration", "global override patch"],
        "package_scripts": {},
    }
    for pkg in repo.rglob("package.json"):
        if is_skipped(pkg):
            continue
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
            if data.get("scripts"):
                contract["package_scripts"][rel(repo, pkg)] = data["scripts"]
        except Exception:
            pass
    (reports / "CONTRACT_AND_GATE_MATRIX.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
    risk = ["# MISSING_OR_UNMAPPED_RISK", "", "## Missing expected authority files", *([f"- `{m}`" for m in missing] if missing else ["- None detected"]), "", "## Risks", "- Do not patch from screenshot only.", "- Confirm canonical TSX/CSS owners before visual changes.", "- Do not use priority overrides or `!important`.", "- Re-run context after any repo state change before patching."]
    (reports / "MISSING_OR_UNMAPPED_RISK.md").write_text("\n".join(risk), encoding="utf-8")
    env = f"""# AGENT_PROMPT_ENVELOPE

Task:
{args.task}

Use:
- `.governance/current/AUTHORITY_READSET.lock.json`
- `reports/APP_IMPACT_MATRIX.md`
- `reports/CONTRACT_AND_GATE_MATRIX.json`
- `reports/MISSING_OR_UNMAPPED_RISK.md`
- `reports/LAYERS_MAP.md`
- `reports/LAYERS_MAP.json`
- `reports/AUTHORITY_MESH_REPORT.md`

Rules:
- Do not patch without reviewing this Mesh.
- Do not touch excluded surfaces.
- No `!important`, no priority override tokens, no global hack layer.
- No process kill, no port free, no dev server start, no hot Prisma.
"""
    (reports / "AGENT_PROMPT_ENVELOPE.md").write_text(env, encoding="utf-8")
    report = ["# AUTHORITY_MESH_REPORT", "", f"Generated: {_dt.datetime.now().isoformat()}", f"Repo: `{repo}`", f"Task: {args.task}", "", "## Summary", f"- Workers: `{args.workers}`", f"- Shards: `{args.shards}`", f"- Hits: `{len(hits)}`", f"- Selected files: `{len(selected)}`", f"- Layer entries: `{len(layers)}`", f"- Git status return code: `{git_state.get('status_short', {}).get('returncode')}`", "", "## Status", "PASS: compact task-scoped Mesh generated with mandatory layer map."]
    (reports / "AUTHORITY_MESH_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    (reports / "hits.json").write_text(json.dumps(hits, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "CONTINUATION.md").write_text("\n".join(report) + "\n\nUpload this ZIP before patching.\n", encoding="utf-8")


def self_test() -> int:
    fake = list(range(111))
    buckets = shard([Path(str(x)) for x in fake], 54)
    assert sum(len(x) for x in buckets) == 111
    assert len(buckets) == 54
    print("AUTOMESH V5 SELFTEST OK: sharders=54 workers_cap=18")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA AutoMesh v5")
    parser.add_argument("--task", required=False)
    parser.add_argument("--surface", default="")
    parser.add_argument("--repo", default="")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--shards", type=int, default=54)
    parser.add_argument("--max-files", type=int, default=120)
    parser.add_argument("--max-mb", type=int, default=40)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.task:
        raise SystemExit("Falta --task")
    args.workers = max(1, min(18, args.workers))
    args.shards = max(args.workers, min(216, args.shards))
    base = Path(args.out)
    base.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%d%m %H%M")
    out_dir = base / f"automesh mesh1 {stamp} result"
    zip_path = base / f"automesh mesh1 {stamp} result.zip"
    fail_zip = base / f"automesh mesh1 {stamp} fail.zip"
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        progress(1, 10, "detectando repo")
        repo = find_repo(args.repo or None)
        progress(2, 10, "capturando git status read-only")
        git_state = {
            "status_short": run_git(repo, ["git", "status", "--short"]),
            "head": run_git(repo, ["git", "rev-parse", "HEAD"]),
            "branch": run_git(repo, ["git", "branch", "--show-current"]),
        }
        progress(3, 10, "detectando superficies y tokens")
        surfaces = detect_surfaces(args.task, args.surface)
        terms = tokenize(args.task, args.surface)
        progress(4, 10, "escaneando archivos texto")
        files = iter_files(repo)
        progress(5, 10, f"dividiendo {len(files)} archivos en {args.shards} sharders")
        buckets = shard(files, args.shards)
        hits: List[Dict[str, Any]] = []
        done = 0
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = [ex.submit(scan_shard, (repo, b, terms, surfaces)) for b in buckets]
            for fut in cf.as_completed(futures):
                done += 1
                hits.extend(fut.result())
                if done == len(futures) or done % max(1, len(futures)//10) == 0:
                    progress(5 + min(2, int(done * 2 / max(1, len(futures)))), 10, f"procesando sharders {done}/{len(futures)}")
        progress(7, 10, "copiando candidatos compactos")
        selected = copy_selected(repo, out_dir, hits, args.max_files, args.max_mb)
        progress(8, 10, "generando layer map obligatorio")
        layers = build_layers(repo, selected)
        if not layers:
            raise RuntimeError("LAYER_MAP_EMPTY: Mesh incompleto, ajusta task/surface.")
        progress(9, 10, "escribiendo matrices y reportes")
        write_reports(out_dir, repo, args, surfaces, hits, selected, layers, git_state)
        progress(10, 10, "comprimiendo result ZIP")
        zip_dir(out_dir, zip_path)
        print(f"OK_RESULT_ZIP={zip_path}")
        return 0
    except Exception as exc:
        (out_dir / "ERROR.txt").write_text(repr(exc), encoding="utf-8", errors="replace")
        try:
            zip_dir(out_dir, fail_zip)
            print(f"FAIL_ZIP={fail_zip}")
        finally:
            raise

if __name__ == "__main__":
    raise SystemExit(main())
