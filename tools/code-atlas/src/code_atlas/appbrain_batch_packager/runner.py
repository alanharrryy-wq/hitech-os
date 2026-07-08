
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
import zipfile
import base64
from datetime import datetime
from pathlib import Path
from typing import Any

APP_NAMES = ["03_TABLET", "04_PC", "05_APP_MOVIL"]
APP_SURFACE = {
    "03_TABLET": "tablet",
    "04_PC": "pc",
    "05_APP_MOVIL": "mobile",
}
APP_LABEL = {
    "03_TABLET": "Tablet",
    "04_PC": "PC",
    "05_APP_MOVIL": "App MÃ³vil",
}
UI_EXTS = {".tsx", ".jsx"}
BLOCKED_PARTS = {
    ".git", "node_modules", ".next", "dist", "build", ".turbo", ".prisma", ".generated",
    ".wrangler", "coverage", "vendor", "__pycache__"
}
REQUIRED_DATA_ATTRS = [
    "data-surface", "data-screen", "data-zone", "data-panel", "data-target", "data-kind", "data-role"
]


def now_stamp() -> str:
    return datetime.now().strftime("%d%m %H%M%S")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", errors="replace")


def write_json(path: Path, obj: Any) -> None:
    write_text(path, json.dumps(obj, ensure_ascii=False, indent=2))


def read_json_from_zip(zip_path: Path, wanted: str) -> Any | None:
    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        for name in names:
            norm = name.replace("\\", "/")
            if norm == wanted or norm.endswith("/" + wanted) or norm.endswith(wanted):
                return json.loads(z.read(name).decode("utf-8", errors="replace"))
    return None


def copy_zip_member(zip_path: Path, wanted: str, dst: Path) -> bool:
    with zipfile.ZipFile(zip_path, "r") as z:
        for name in z.namelist():
            norm = name.replace("\\", "/")
            if norm == wanted or norm.endswith("/" + wanted) or norm.endswith(wanted):
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(z.read(name))
                return True
    return False


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_dir(source: Path, dest: Path) -> None:
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for p in sorted(source.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(source).as_posix())


def run_cmd(args: list[str], cwd: Path | None = None, timeout: int = 60) -> dict[str, Any]:
    try:
        p = subprocess.run(args, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return {"args": args, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"args": args, "returncode": -999, "stdout": "", "stderr": repr(exc)}


def latest_workbench_zip(out_root: Path) -> Path | None:
    patterns = ["appbrain-workbench*result.zip", "appbrain%2Dworkbench*result.zip", "appbrain*workbench*result.zip"]
    found: list[Path] = []
    for pattern in patterns:
        found.extend(out_root.glob(pattern))
    found = [p for p in found if p.is_file()]
    return sorted(found, key=lambda p: p.stat().st_mtime, reverse=True)[0] if found else None


def latest_appbrain_zip(out_root: Path) -> Path | None:
    patterns = ["appbrain1*result.zip", "appbrain1%20*result.zip"]
    found: list[Path] = []
    for pattern in patterns:
        found.extend(out_root.glob(pattern))
    found = [p for p in found if p.is_file()]
    return sorted(found, key=lambda p: p.stat().st_mtime, reverse=True)[0] if found else None



def as_list(x: Any) -> list[Any]:
    """Return a shallow list for common Workbench containers."""
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        for key in (
            "batches", "items", "actions", "rows", "targetPatchFiles",
            "patchableBatches", "patchable", "targetFiles", "files",
        ):
            v = x.get(key)
            if isinstance(v, list):
                return v
        return [x]
    return []

def safe_count(x: Any) -> int:
    if x is None:
        return 0
    if isinstance(x, (list, tuple, set, dict)):
        return len(x)
    try:
        return int(x)
    except Exception:
        return 0


def slugify(value: str, fallback: str = "batch") -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return s or fallback


def humanize(value: str) -> str:
    if not value:
        return "Unknown"
    v = str(value).replace("_", " ").replace("-", " ").replace("/", " ")
    v = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", v)
    return " ".join(w[:1].upper() + w[1:] for w in v.split())


def is_blocked_file(path: str) -> bool:
    norm = path.replace("\\", "/").lower()
    parts = set(norm.split("/"))
    if parts & BLOCKED_PARTS:
        return True
    blocked_fragments = ["/api/", "/server/", "/generated/", "/.generated/", "/prisma-client/", "/node_modules/", "/__tests__/"]
    if any(fragment in norm for fragment in blocked_fragments):
        return True
    if norm.endswith(("package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock")):
        return True
    return False


def normalize_path_from_any(item: Any) -> str | None:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ("file", "path", "sourceFile", "relativePath", "targetFile"):
            v = item.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return None


def collect_patch_files(batch: dict[str, Any]) -> list[str]:
    candidates: list[Any] = []
    for key in ("targetPatchFiles", "patchableFiles", "files", "filesToTouch", "targetFiles"):
        v = batch.get(key)
        if isinstance(v, list):
            candidates.extend(v)
    for key in ("targets", "items", "actions"):
        v = batch.get(key)
        if isinstance(v, list):
            candidates.extend(v)
    result: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        path = normalize_path_from_any(item)
        if not path:
            continue
        path = path.replace("\\", "/")
        if is_blocked_file(path):
            continue
        if Path(path).suffix.lower() not in UI_EXTS:
            continue
        key = path.lower()
        if key not in seen:
            seen.add(key)
            result.append(path)
    return result


def pick_batch(workbench: dict[str, Any], requested_id: str | None = None, app: str | None = None, semantic_group: str | None = None) -> dict[str, Any]:
    patchable = read_patchable_batches_from_workbench(workbench)
    if not patchable:
        raise RuntimeError("No patchable batches found in Workbench data.")

    def batch_id(b: dict[str, Any]) -> str:
        return str(b.get("id") or b.get("batchId") or b.get("slug") or "")

    if requested_id:
        req = requested_id.lower()
        for b in patchable:
            if req in {batch_id(b).lower(), str(b.get("name") or "").lower(), str(b.get("label") or "").lower()}:
                return b
            combo = f"{b.get('app','')} {b.get('semanticGroup','')} {b.get('screen','')} {b.get('route','')}".lower()
            if req in combo:
                return b
        raise RuntimeError(f"Requested batch not found: {requested_id}")

    filtered = patchable
    if app:
        a = app.lower()
        filtered = [b for b in filtered if a in str(b.get("app") or b.get("surface") or "").lower()]
    if semantic_group:
        sg = semantic_group.lower()
        filtered = [b for b in filtered if sg in str(b.get("semanticGroup") or b.get("group") or "").lower()]
    if not filtered:
        raise RuntimeError("No batch matched the requested filters.")

    def score(b: dict[str, Any]) -> int:
        value = safe_count(b.get("targetPatchFiles") or b.get("patchableFiles") or b.get("files"))
        value += safe_count(b.get("targets"))
        value += int(b.get("priorityScore") or b.get("score") or 0)
        if str(b.get("readiness") or "").upper() == "READY_FOR_INSTRUMENTATION_ONLY":
            value += 500
        return value

    return sorted(filtered, key=score, reverse=True)[0]



def read_patchable_batches_from_workbench(workbench: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract patchable batches from all known Workbench shapes.

    The real Workbench can store data as:
    - patchableBatches: [...]
    - PRISMA_APPBRAIN_PATCHABLE_BATCHES: [...]
    - PRISMA_APPBRAIN_PATCHABLE_BATCHES: {apps: {"03_TABLET": [...]}}
    - PRISMA_APPBRAIN_PATCHABLE_BATCHES: {apps: {"03_TABLET": {"batches": [...]}}}
    - PRISMA_APPBRAIN_PATCHABLE_BATCHES: {batches/items/patchableBatches: [...]}
    """
    batches: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add_batch(item: Any, app_name: str | None = None) -> None:
        if not isinstance(item, dict):
            return
        b = dict(item)
        if app_name and not b.get("app"):
            b["app"] = app_name
        bid = str(b.get("id") or b.get("batchId") or b.get("slug") or "")
        key = json.dumps(
            {
                "id": bid,
                "app": b.get("app"),
                "semanticGroup": b.get("semanticGroup") or b.get("group"),
                "screen": b.get("screen") or b.get("screenId") or b.get("route"),
                "files": b.get("targetPatchFiles") or b.get("patchableFiles") or b.get("files"),
            },
            sort_keys=True,
            default=str,
        )
        if key not in seen:
            seen.add(key)
            batches.append(b)

    def visit(obj: Any, app_name: str | None = None) -> None:
        if isinstance(obj, list):
            for item in obj:
                add_batch(item, app_name)
            return
        if not isinstance(obj, dict):
            return

        apps_obj = obj.get("apps")
        if isinstance(apps_obj, dict):
            for app_key, app_value in apps_obj.items():
                if isinstance(app_value, list):
                    for item in app_value:
                        add_batch(item, str(app_key))
                elif isinstance(app_value, dict):
                    local = False
                    for inner in ("batches", "items", "patchableBatches", "rows"):
                        v = app_value.get(inner)
                        if isinstance(v, list):
                            local = True
                            for item in v:
                                add_batch(item, str(app_key))
                    if not local and (
                        app_value.get("targetPatchFiles")
                        or app_value.get("patchableFiles")
                        or app_value.get("files")
                    ):
                        add_batch(app_value, str(app_key))

        for key in ("patchableBatches", "batches", "items", "patchable", "rows"):
            v = obj.get(key)
            if isinstance(v, list):
                for item in v:
                    add_batch(item, app_name)
            elif isinstance(v, dict):
                visit(v, app_name)

    direct = workbench.get("patchableBatches")
    visit(direct)
    for key in ("PRISMA_APPBRAIN_PATCHABLE_BATCHES", "patchable", "batches"):
        visit(workbench.get(key))

    return batches


def load_workbench_zip(source_zip: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    candidates = [
        "PRISMA_APPBRAIN_WORKBENCH.json",
        "PRISMA_APPBRAIN_PATCHABLE_BATCHES.json",
        "PRISMA_APPBRAIN_BATCH_EXPLORER.json",
        "PRISMA_TRI_APP_DASHBOARD.json",
        "PRISMA_APPBRAIN_NEXT_PACKAGE_PLAN.json",
    ]
    for name in candidates:
        obj = read_json_from_zip(source_zip, name)
        if obj is not None:
            key = name.replace(".json", "")
            data[key] = obj
            if name == "PRISMA_APPBRAIN_PATCHABLE_BATCHES.json":
                if isinstance(obj, dict):
                    data["patchableBatches"] = read_patchable_batches_from_workbench({key: obj})
                elif isinstance(obj, list):
                    data["patchableBatches"] = [b for b in obj if isinstance(b, dict)]
            if name == "PRISMA_APPBRAIN_WORKBENCH.json" and isinstance(obj, dict):
                data.update({k: v for k, v in obj.items() if k not in data})
    if "patchableBatches" not in data:
        data["patchableBatches"] = read_patchable_batches_from_workbench(data)
    if not data:
        raise RuntimeError(f"No Workbench JSON files found in {source_zip}")
    return data


def resolve_repo_file(repo_root: Path, rel_path: str) -> Path | None:
    """Resolve Workbench paths that may be repo-relative or app-root-relative.

    AppBrain often emits paths like products/tablet/... from the app root.
    The repo stores them under apps/terminal-de-venta-system/products/...
    """
    if not rel_path:
        return None
    raw = str(rel_path).strip().strip('"').strip("'")
    raw = raw.replace("\\", "/")
    raw = re.sub(r"^[A-Za-z]:/", "", raw)
    raw = raw.lstrip("/")
    candidates = [
        repo_root / raw,
        repo_root / "apps" / "terminal-de-venta-system" / raw,
    ]
    if raw.startswith("terminal-de-venta-system/"):
        candidates.append(repo_root / "apps" / raw)
    if raw.startswith("app/"):
        candidates.append(repo_root / "apps" / "terminal-de-venta-system" / "products" / raw)

    rr = repo_root.resolve()
    for candidate in candidates:
        try:
            rp = candidate.resolve()
            if not str(rp).lower().startswith(str(rr).lower()):
                continue
        except Exception:
            continue
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def repo_relative_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        return str(path).replace("\\", "/")


def build_plan(repo_root: Path, batch: dict[str, Any]) -> dict[str, Any]:
    app = str(batch.get("app") or batch.get("surface") or "03_TABLET")
    surface = APP_SURFACE.get(app, slugify(app, "surface"))
    semantic_group = str(batch.get("semanticGroup") or batch.get("group") or "unknown_group")
    screen = str(batch.get("screen") or batch.get("screenId") or batch.get("route") or semantic_group or "unknown_screen")
    risk = str(batch.get("risk") or "review")
    readiness = str(batch.get("readiness") or "READY_FOR_INSTRUMENTATION_ONLY")
    paths = collect_patch_files(batch)
    files: list[dict[str, Any]] = []
    missing: list[str] = []
    for source_path in paths:
        p = resolve_repo_file(repo_root, source_path)
        if not p:
            missing.append(source_path)
            continue
        repo_path = repo_relative_path(repo_root, p)
        files.append({
            "path": repo_path,
            "sourcePath": source_path,
            "sha256Before": sha256_file(p),
            "sizeBytes": p.stat().st_size,
            "surface": surface,
            "app": app,
            "semanticGroup": semantic_group,
            "screen": slugify(screen, "screen").replace("-", "_"),
            "zone": slugify(semantic_group, "zone").replace("-", "_"),
            "panel": slugify(Path(repo_path).stem, "panel").replace("-", "_"),
        })
    if not files:
        raise RuntimeError(
            "Selected batch has no existing .tsx/.jsx runtime UI files in repo. "
            f"Candidate paths checked: {paths[:20]}"
        )
    return {
        "generatedAt": now_iso(),
        "batch": batch,
        "app": app,
        "surface": surface,
        "semanticGroup": semantic_group,
        "screen": slugify(screen, "screen").replace("-", "_"),
        "risk": risk,
        "readiness": readiness,
        "files": files,
        "missingFiles": missing,
        "requiredDataAttributes": REQUIRED_DATA_ATTRS,
        "forbidden": [
            "CSS changes",
            "logic changes",
            "Prisma",
            "Git writes",
            "package/lockfile edits",
            "process kill",
            "port freeing",
            "dev server start",
        ],
    }

GENERATED_RUN_PS1 = r"""$ErrorActionPreference='Stop'
$RepoRoot = if($env:PRISMA_REPO_ROOT){$env:PRISMA_REPO_ROOT}else{'F:\repos\hitech-os'}
$OutRoot = if($env:PRISMA_OUT_ROOT){$env:PRISMA_OUT_ROOT}else{'F:\descargasf'}
$Stamp = Get-Date -Format 'ddMM HHmmss'
$RunRoot = Join-Path $OutRoot ('appbatch-tabmarks ' + $Stamp + ' staging')
$Engine = Join-Path $RunRoot 'engine.py'
New-Item -ItemType Directory -Force -Path $RunRoot,$OutRoot | Out-Null
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Copy-Item -LiteralPath (Join-Path $Here 'BATCH_PLAN.json') -Destination (Join-Path $RunRoot 'BATCH_PLAN.json') -Force
$EncodedEngine = '{ENGINE_B64_PLACEHOLDER}'
[System.IO.File]::WriteAllBytes($Engine, [System.Convert]::FromBase64String($EncodedEngine))
$Py = (Get-Command py.exe -ErrorAction SilentlyContinue).Source
$Args = @()
if($Py){$Args=@('-3')}else{$Py=(Get-Command python.exe -ErrorAction Stop).Source}
& $Py @Args $Engine --repo $RepoRoot --out $OutRoot --run-root $RunRoot --plan (Join-Path $RunRoot 'BATCH_PLAN.json')
if($LASTEXITCODE -ne 0){ throw "appbatch-tabmarks failed with exit code $LASTEXITCODE" }
"""

GENERATED_PACKAGE_ENGINE = r"""
from __future__ import annotations
import argparse, difflib, hashlib, json, os, re, shutil, subprocess, sys, traceback, zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_ATTRS = ["data-surface", "data-screen", "data-zone", "data-panel", "data-target", "data-kind", "data-role"]
NATIVE_TAGS = {
    "main","section","article","aside","header","footer","nav","div","span","strong","em","p",
    "h1","h2","h3","h4","h5","h6","button","a","input","label","form","select","option",
    "textarea","ul","ol","li","table","thead","tbody","tfoot","tr","td","th","figure","figcaption"
}
KIND_BY_TAG = {
    "button": "button", "a": "button", "input": "field", "select": "field", "textarea": "field",
    "table": "table", "thead": "table", "tbody": "table", "tr": "table", "td": "table", "th": "table",
    "h1": "text", "h2": "text", "h3": "text", "h4": "text", "h5": "text", "h6": "text", "p": "text", "span": "text", "strong": "price"
}


def now_stamp(): return datetime.now().strftime("%d%m %H%M%S")
def now_iso(): return datetime.now().isoformat(timespec="seconds")
def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8", errors="replace")
def write_json(path: Path, obj: Any): write_text(path, json.dumps(obj, ensure_ascii=False, indent=2))
def sha256_file(path: Path):
    if not path.exists() or not path.is_file(): return None
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""): h.update(b)
    return h.hexdigest()
def zip_dir(source: Path, dest: Path):
    if dest.exists(): dest.unlink()
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as z:
        for p in sorted(source.rglob("*")):
            if p.is_file(): z.write(p, p.relative_to(source).as_posix())
def rel(repo: Path, p: Path):
    try: return p.resolve().relative_to(repo.resolve()).as_posix()
    except Exception: return str(p)
def run_cmd(args, cwd=None):
    try:
        p=subprocess.run(args, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        return {"args":args,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr}
    except Exception as e:
        return {"args":args,"returncode":-999,"stdout":"","stderr":repr(e)}

def slugify(value: str, fallback="target"):
    s=re.sub(r"[^a-zA-Z0-9]+","-",str(value or "").strip().lower()).strip("-")
    return s or fallback

def line_col(text: str, idx: int):
    return text.count("\n",0,idx)+1

def remove_known_data_attrs(text: str) -> str:
    # Remove only attributes this package owns, then collapse whitespace between tag name and attributes.
    for attr in DATA_ATTRS:
        text = re.sub(r"\s+" + re.escape(attr) + r"=(?:\{[^\n{}]*\}|\"[^\"\n]*\"|'[^'\n]*')", "", text)
    return text

def infer_kind(tag: str, attrs: str, file_path: str, index: int):
    hay = f"{tag} {attrs} {file_path}".lower()
    if "total" in hay or "price" in hay or "amount" in hay or "precio" in hay: return "price"
    if "badge" in hay or "status" in hay or "pill" in hay: return "badge"
    if "card" in hay or "panel" in hay or "rail" in hay or tag in {"section","article","aside"}: return "panel"
    if "grid" in hay or "list" in hay or "row" in hay: return "layout"
    return KIND_BY_TAG.get(tag, "text" if tag in {"span","p","strong"} else "panel")

def should_skip_match(text: str, start: int, end: int) -> bool:
    # Avoid comments and strings in common cases by checking recent line prefix.
    line_start = text.rfind("\n", 0, start) + 1
    prefix = text[line_start:start]
    if "//" in prefix or "/*" in prefix or "*" == prefix.strip()[:1]: return True
    segment = text[start:end]
    if any(a in segment for a in DATA_ATTRS): return True
    if "..." in segment: return False
    return False

def add_marks_to_file(content: str, file_meta: dict[str, Any]) -> tuple[str, int, list[dict[str, Any]]]:
    surface = file_meta.get("surface") or "unknown"
    screen = file_meta.get("screen") or "unknown_screen"
    zone = file_meta.get("zone") or "unknown_zone"
    panel = file_meta.get("panel") or "unknown_panel"
    file_path = file_meta.get("path") or "unknown"
    pattern = re.compile(r"<(?P<tag>[a-z][a-z0-9]*)\b(?P<attrs>[^<>]*?)(?P<end>/?>)", re.DOTALL)
    matches = []
    for m in pattern.finditer(content):
        tag = m.group("tag")
        if tag not in NATIVE_TAGS: continue
        if should_skip_match(content, m.start(), m.end()): continue
        attrs = m.group("attrs") or ""
        # Prefer meaningful elements, avoid blasting every tiny span.
        weight = 0
        hay = f"{tag} {attrs} {file_path}".lower()
        if tag in {"main","section","article","aside","header","footer","nav","button","a","input","table","form"}: weight += 5
        if any(x in hay for x in ["checkout","pos","cart","total","pay","payment","product","sale","license","sync","status","card","panel","grid"]): weight += 4
        if tag in {"div","span"}: weight += 1
        if weight <= 1: continue
        matches.append((weight, m.start(), m.end(), m))
    matches = sorted(matches, key=lambda x: (-x[0], x[1]))[:18]
    if not matches: return content, 0, []
    inserts = []
    evidence = []
    for idx, (_, start, end, m) in enumerate(sorted(matches, key=lambda x: x[1])):
        tag = m.group("tag")
        attrs = m.group("attrs") or ""
        kind = infer_kind(tag, attrs, file_path, idx)
        target = f"{slugify(Path(file_path).stem)}-{tag}-{idx+1}"
        role = "container" if tag in {"main","section","article","aside","header","footer","nav","div"} else kind
        attr_text = (
            f' data-surface="{surface}"'
            f' data-screen="{screen}"'
            f' data-zone="{zone}"'
            f' data-panel="{panel}"'
            f' data-target="{target}"'
            f' data-kind="{kind}"'
            f' data-role="{role}"'
        )
        insert_at = m.start() + len(tag) + 1
        inserts.append((insert_at, attr_text))
        evidence.append({"line": line_col(content, m.start()), "tag": tag, "target": target, "kind": kind, "role": role})
    new = content
    for pos, txt in sorted(inserts, key=lambda x: x[0], reverse=True):
        new = new[:pos] + txt + new[pos:]
    return new, len(inserts) * len(DATA_ATTRS), evidence

def rollback_files(backups: list[dict[str, Any]], repo: Path):
    for item in backups:
        src=Path(item["backupPath"])
        dst=repo / item["path"].replace("/", os.sep)
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src,dst)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--plan", required=True)
    args=ap.parse_args()
    repo=Path(args.repo)
    out=Path(args.out)
    run=Path(args.run_root)
    plan=json.loads(Path(args.plan).read_text(encoding="utf-8", errors="replace"))
    stamp=now_stamp()
    result=out / f"appbatch-tabmarks {stamp} result.zip"
    fail=out / f"appbatch-tabmarks {stamp} fail.zip"
    for p in [run/"reports", run/"backups_before_changes", run/"changed_files_after", run/"diffs"]: p.mkdir(parents=True, exist_ok=True)
    backups=[]; changed=[]; marks_added=0; mark_evidence=[]
    try:
        git_before=run_cmd(["git","status","--short","--branch"], cwd=repo)
        write_text(run/"reports/git_status_before.txt", git_before["stdout"]+"\n"+git_before["stderr"])
        # Hash gate before any write.
        for f in plan.get("files", []):
            p=repo / str(f["path"]).replace("/", os.sep)
            if not p.exists() or p.suffix.lower() not in {".tsx",".jsx"}:
                raise RuntimeError(f"Blocked non-runtime UI or missing file: {f.get('path')}")
            got=sha256_file(p)
            expected=f.get("sha256Before")
            if expected and got != expected:
                raise RuntimeError(f"Hash gate failed for {f.get('path')}: expected {expected}, got {got}")
        for f in plan.get("files", []):
            path=f["path"]
            p=repo / path.replace("/", os.sep)
            old=p.read_text(encoding="utf-8", errors="replace")
            new, added, ev = add_marks_to_file(old, f)
            if new == old:
                continue
            # Validate semantic-only: removing package data attrs from new should match old.
            if remove_known_data_attrs(new) != remove_known_data_attrs(old):
                raise RuntimeError(f"Semantic-only validation failed before write for {path}")
            backup=run/"backups_before_changes"/path
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, backup)
            backups.append({"path":path,"backupPath":str(backup),"sha256Before":sha256_file(p)})
            p.write_text(new, encoding="utf-8", errors="replace")
            changed.append(path)
            marks_added += added
            for e in ev: e["file"]=path
            mark_evidence.extend(ev)
            after=run/"changed_files_after"/path
            after.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, after)
            diff="".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=path+" before", tofile=path+" after"))
            write_text(run/"diffs"/(slugify(path)+".diff"), diff)
        # Post validations.
        bad=[]
        for f in plan.get("files", []):
            path=f["path"]
            p=repo / path.replace("/", os.sep)
            if path in changed:
                old=(run/"backups_before_changes"/path).read_text(encoding="utf-8", errors="replace")
                new=p.read_text(encoding="utf-8", errors="replace")
                if remove_known_data_attrs(new) != remove_known_data_attrs(old):
                    bad.append(path)
        if bad:
            raise RuntimeError("Post semantic-only validation failed: "+", ".join(bad[:20]))
        git_after=run_cmd(["git","status","--short","--branch"], cwd=repo)
        write_text(run/"reports/git_status_after.txt", git_after["stdout"]+"\n"+git_after["stderr"])
        validation={
            "status":"PASS_APPBATCH_TABMARKS_GENERATED_BY_CODE_ATLAS_PACKAGER",
            "generatedAt":now_iso(),
            "readOnly":False,
            "visualPatch":False,
            "cssChanged":False,
            "logicChanged":False,
            "prisma":False,
            "gitWrites":False,
            "processKill":False,
            "portFreeing":False,
            "devServerStart":False,
            "packageOrLockfileChanges":False,
            "changedOnlyAllowlist": True,
            "onlyDataAttributesAdded": True,
            "filesModified":len(changed),
            "marksAdded":marks_added,
            "allowedFiles":len(plan.get("files", [])),
        }
        write_json(run/"reports/validation.json", validation)
        write_json(run/"APPLIED_MARKS.json", {"marksAdded":marks_added,"filesModified":changed,"evidence":mark_evidence})
        write_json(run/"backup_manifest.json", {"backups":backups})
        write_text(run/"SUMMARY_FOR_CHAT.md", f"# appbatch-tabmarks\n\nPASS. Files modified: {len(changed)}. Marks added: {marks_added}.\n")
        write_text(run/"CONTINUATION.md", "# CONTINUATION\n\nRegenerate appbrain1/tabatlas after this package to measure confidence lift.\n")
        zip_dir(run,result)
        print("RESULT_ZIP="+str(result))
    except Exception as e:
        try: rollback_files(backups, repo)
        except Exception: pass
        write_text(run/"ERROR.txt", traceback.format_exc())
        write_json(run/"backup_manifest.json", {"backups":backups})
        write_json(run/"reports/validation.json", {"status":"FAIL_APPBATCH_TABMARKS_GENERATED_BY_CODE_ATLAS_PACKAGER","error":repr(e),"rolledBack":True})
        write_text(run/"CONTINUATION.md", "# CONTINUATION\n\nPackage failed and attempted rollback. Review ERROR.txt.\n")
        zip_dir(run,fail)
        print("FAIL_ZIP="+str(fail))
        raise
if __name__ == "__main__": main()
"""


def create_instrumentation_package(plan: dict[str, Any], out_dir: Path) -> Path:
    slug = slugify(f"{plan.get('app','app')} {plan.get('semanticGroup','batch')} tabmarks pkg", "appbatch-tabmarks-pkg")
    pkg_root = out_dir / slug
    if pkg_root.exists():
        shutil.rmtree(pkg_root)
    pkg_root.mkdir(parents=True, exist_ok=True)
    engine = GENERATED_PACKAGE_ENGINE
    run_ps1 = GENERATED_RUN_PS1.replace("{ENGINE_B64_PLACEHOLDER}", base64.b64encode(engine.encode("utf-8")).decode("ascii"))
    write_text(pkg_root / "RUN.ps1", run_ps1)
    write_json(pkg_root / "BATCH_PLAN.json", plan)
    write_text(pkg_root / "README.md", f"# {slug}\n\nGenerated by Code Atlas AppBrain Batch Packager. Instrumentation-only package.\n")
    write_text(pkg_root / "ROLLBACK.ps1", "Write-Host 'Rollback lives inside each executed result/fail ZIP backups. If package was not run, no-op.'\n")
    pkg_zip = out_dir / f"{slug}.zip"
    zip_dir(pkg_root, pkg_zip)
    return pkg_zip


def build_outputs(repo_root: Path, out_root: Path, source_zip: Path, output_zip: Path | None = None, batch_id: str | None = None, app: str | None = None, semantic_group: str | None = None, dry_run: bool = False) -> Path:
    stamp = now_stamp()
    run_name = f"appbrain-batch-packager {stamp}"
    run = out_root / f"{run_name} staging"
    result_zip = output_zip or out_root / f"{run_name} result.zip"
    fail_zip = out_root / f"{run_name} fail.zip"
    for p in [run, run/"reports", run/"source", run/"generated_packages", run/"mesh"]:
        p.mkdir(parents=True, exist_ok=True)
    try:
        workbench = load_workbench_zip(source_zip)
        batch = pick_batch(workbench, requested_id=batch_id, app=app, semantic_group=semantic_group)
        plan = build_plan(repo_root, batch)
        pkg_zip = create_instrumentation_package(plan, run / "generated_packages") if not dry_run else None
        copy_zip_member(source_zip, "PRISMA_APPBRAIN_PATCHABLE_BATCHES.json", run/"source"/"PRISMA_APPBRAIN_PATCHABLE_BATCHES.json")
        copy_zip_member(source_zip, "PRISMA_APPBRAIN_WORKBENCH.json", run/"source"/"PRISMA_APPBRAIN_WORKBENCH.json")
        shutil.copy2(source_zip, run/"source"/source_zip.name)

        authority = {
            "meshId": f"catlas4-batch-packager-{stamp}",
            "generatedAt": now_iso(),
            "sourceWorkbenchZip": str(source_zip),
            "selectedBatch": batch,
            "authorizesPatch": False,
            "nextGeneratedPackage": str(pkg_zip) if pkg_zip else None,
            "plan": plan,
            "rules": [
                "Generated package must modify only .tsx/.jsx runtime UI files listed in BATCH_PLAN.json.",
                "Only semantic data-* attributes may be inserted.",
                "No CSS, no business logic, no Prisma, no Git writes, no dev server/process/port operations.",
                "Generated package contains hash gates, backups, rollback, result/fail ZIP.",
            ],
        }
        write_json(run/"AUTHORITY_READSET.lock.json", authority)
        write_json(run/"APPBRAIN_BATCH_PACKAGE_PLAN.json", plan)
        write_json(run/"APPBRAIN_GENERATED_PACKAGE_INDEX.json", {"generatedPackage": str(pkg_zip) if pkg_zip else None, "dryRun": dry_run})
        write_text(run/"APPBRAIN_BATCH_PACKAGE_PLAN.md", f"# AppBrain Batch Package Plan\n\nApp: {plan['app']}\n\nSemantic group: {plan['semanticGroup']}\n\nPatch files: {len(plan['files'])}\n\nGenerated package: `{pkg_zip}`\n")
        write_text(run/"APP_IMPACT_MATRIX.md", f"# APP_IMPACT_MATRIX\n\nSelected app: {plan['app']}\n\nPatch type: instrumentation-only. Tablet/PC/Mobile files outside selected batch are excluded. API, CSS, logic and lockfiles are blocked.\n")
        write_json(run/"CONTRACT_AND_GATE_MATRIX.json", {"generatedAt": now_iso(), "patchType": "instrumentation_only", "requiredRollback": True, "requiredHashGate": True, "blocked": ["css", "logic", "api", "prisma", "git", "ports", "dev servers", "package/lockfiles"]})
        write_json(run/"LAYER_MAP.json", {"generatedAt": now_iso(), "selectedBatch": batch, "files": plan["files"]})
        write_text(run/"LAYER_MAP.md", "# LAYER_MAP\n\n" + "\n".join(f"- `{f['path']}`" for f in plan["files"]))
        write_text(run/"MISSING_OR_UNMAPPED_RISK.md", "# MISSING_OR_UNMAPPED_RISK\n\nGenerated package must be reviewed if missingFiles is not empty.\n")
        write_text(run/"AGENT_PROMPT_ENVELOPE.md", "# AGENT_PROMPT_ENVELOPE\n\nUse generated package only as instrumentation-only with rollback.\n")
        write_text(run/"AUTHORITY_MESH_REPORT.md", f"# AUTHORITY_MESH_REPORT\n\nStatus: PASS_APPBRAIN_BATCH_PACKAGER_GENERATED\n\nGenerated package: `{pkg_zip}`\n")
        git = run_cmd(["git","status","--short","--branch"], cwd=repo_root)
        write_text(run/"reports/git_status.txt", git["stdout"]+"\n"+git["stderr"])
        validation = {"status":"PASS_APPBRAIN_BATCH_PACKAGER_GENERATED", "generatedAt": now_iso(), "sourceWorkbenchZip": str(source_zip), "patchFiles": len(plan["files"]), "generatedPackage": str(pkg_zip) if pkg_zip else None, "dryRun": dry_run, "readOnlyInstall": True}
        write_json(run/"reports/validation.json", validation)
        write_text(run/"SUMMARY_FOR_CHAT.md", f"# AppBrain Batch Packager\n\nPASS. Generated instrumentation package for `{plan['app']} / {plan['semanticGroup']}` with {len(plan['files'])} patch files.\n")
        write_text(run/"CONTINUATION.md", "# CONTINUATION\n\nReview generated package inside generated_packages/. Run it only after approval.\n")
        zip_dir(run, result_zip)
        return result_zip
    except Exception as exc:
        write_text(run/"ERROR.txt", traceback.format_exc())
        write_json(run/"reports/validation.json", {"status":"FAIL_APPBRAIN_BATCH_PACKAGER", "error": repr(exc), "generatedAt": now_iso()})
        write_text(run/"CONTINUATION.md", "# CONTINUATION\n\nBatch packager failed. Review ERROR.txt.\n")
        zip_dir(run, fail_zip)
        raise


def run_workbench_batch_packager(source_zip: Path | None = None, repo_root: Path | None = None, out_root: Path | None = None, batch_id: str | None = None, app: str | None = None, semantic_group: str | None = None, output_zip: Path | None = None, dry_run: bool = False) -> Path:
    repo_root = repo_root or Path(os.environ.get("PRISMA_REPO_ROOT", r"F:\repos\hitech-os"))
    out_root = out_root or Path(os.environ.get("PRISMA_OUT_ROOT", r"F:\descargasf"))
    out_root.mkdir(parents=True, exist_ok=True)
    source_zip = source_zip or latest_workbench_zip(out_root)
    if not source_zip:
        raise RuntimeError("No appbrain-workbench result.zip found. Run RUN_APPBRAIN_WORKBENCH.ps1 first.")
    return build_outputs(repo_root, out_root, source_zip, output_zip=output_zip, batch_id=batch_id, app=app, semantic_group=semantic_group, dry_run=dry_run)

# catlas4fix3-appbrain-batch-packager-path-resolver
