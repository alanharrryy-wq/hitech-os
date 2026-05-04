#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Iterable
from .profile import ProjectProfile
EXCLUDED_DIR_NAMES={".git",".hg",".svn",".idea",".vscode","__pycache__",".mypy_cache",".pytest_cache",".ruff_cache",".tox",".nox",".venv","venv","env","node_modules","dist","build",".next",".turbo","coverage","out"}
SOURCE_EXTENSIONS={".py":"python",".pyw":"python",".ts":"typescript",".tsx":"typescript",".js":"javascript",".jsx":"javascript",".mjs":"javascript",".cjs":"javascript"}
def _walk_files(root:Path,max_files:int=5000)->Iterable[Path]:
    count=0
    for current_root,dir_names,file_names in os.walk(root):
        dir_names[:]=sorted(d for d in dir_names if d not in EXCLUDED_DIR_NAMES)
        for file_name in sorted(file_names):
            count+=1
            if count>max_files: return
            yield Path(current_root)/file_name
def _exists(root:Path,rel:str)->bool: return (root/rel).exists()
def _package_manager(root:Path)->str:
    if _exists(root,"pnpm-lock.yaml") or _exists(root,"pnpm-workspace.yaml"): return "pnpm"
    if _exists(root,"yarn.lock"): return "yarn"
    if _exists(root,"package-lock.json") or _exists(root,"package.json"): return "npm"
    return "unknown"
def _frameworks(root:Path)->list[str]:
    found=set()
    for name in ["next.config.js","next.config.mjs","next.config.ts"]:
        if _exists(root,name): found.add("nextjs")
    for name in ["vite.config.js","vite.config.mjs","vite.config.ts"]:
        if _exists(root,name): found.add("vite")
    if _exists(root,"prisma/schema.prisma"): found.add("prisma")
    p=root/"package.json"
    if p.exists():
        try:
            data=json.loads(p.read_text(encoding="utf-8")); deps={}
            for k in ["dependencies","devDependencies","peerDependencies","optionalDependencies"]:
                if isinstance(data.get(k),dict): deps.update(data[k])
            for dep,fw in [("next","nextjs"),("vite","vite"),("react","react"),("vue","vue")]:
                if dep in deps: found.add(fw)
        except Exception: pass
    return sorted(found)
def detect_project(root:Path|str,*,max_files:int=5000)->ProjectProfile:
    r=Path(root).expanduser()
    try: r=r.resolve()
    except Exception: pass
    prof=ProjectProfile(root=str(r),exists=r.exists())
    if not prof.exists:
        prof.notes.append("root-not-found"); return prof
    cfgs=["package.json","pnpm-workspace.yaml","tsconfig.json","jsconfig.json","pyproject.toml","requirements.txt","requirements-dev.txt","pytest.ini","docker-compose.yml","compose.yml","Dockerfile",".github/workflows","prisma/schema.prisma"]
    prof.config_files=[c for c in cfgs if (r/c).exists()]
    prof.package_manager=_package_manager(r); prof.frameworks=_frameworks(r)
    entries=["src/main.py","src/app.py","main.py","app.py","src/index.ts","src/index.tsx","src/main.ts","src/main.tsx","app/page.tsx","pages/index.tsx","apps","packages","products","services"]
    prof.entrypoints=[e for e in entries if (r/e).exists()]
    langs=set(); counts={}; total=0
    for path in _walk_files(r,max_files=max_files):
        total+=1; lang=SOURCE_EXTENSIONS.get(path.suffix.lower())
        if lang: langs.add(lang); counts[lang]=counts.get(lang,0)+1
    prof.languages=sorted(langs); prof.source_counts=dict(sorted(counts.items()))
    if total>=max_files: prof.notes.append(f"scan-truncated-at-{max_files}-files")
    has_ws="pnpm-workspace.yaml" in prof.config_files or (r/"packages").exists() or (r/"apps").exists()
    if has_ws and ({"typescript","javascript"}&langs or (r/"package.json").exists()): prof.project_type="node-monorepo"
    elif {"typescript","javascript"}&langs or (r/"package.json").exists(): prof.project_type="node-app"
    elif "python" in langs or (r/"pyproject.toml").exists() or (r/"requirements.txt").exists(): prof.project_type="python"
    elif has_ws: prof.project_type="monorepo"
    return prof
