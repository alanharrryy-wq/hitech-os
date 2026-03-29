# %%
# HITECH-OS DEV CONSOLE
# Ejecuta este archivo por bloques con Shift + Enter en VS Code.
# Requiere extensiones Python + Jupyter.
#
# Sugerencia:
# 1) abre este archivo
# 2) selecciona kernel de Python
# 3) ve corriendo bloque por bloque con Shift + Enter

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

# %%
# =========================
# CONFIG
# =========================

@dataclass
class Config:
    project_name: str = "HITECH-OS"
    repo_path: str = r"F:\repos\hitech-os"
    main_branch: str = "main"
    remote: str = "origin"
    default_commit_message: str = "chore(repo): clean artifacts and update workspace"
    smoke_command: Optional[List[str]] = None
    reports_dir_name: str = "_tmp_dev_console_reports"
    ignore_patterns: List[str] = None
    auto_untrack_patterns: List[str] = None

    def __post_init__(self):
        if self.ignore_patterns is None:
            self.ignore_patterns = [
                "*.dot",
                "*.backup_*",
                "*.restorecheck_*",
                "_dev_console_zips/",
                "tools/ui_map/_logs/*.zip",
                "__pycache__/",
                "*.pyc",
                "*.pyo",
                ".DS_Store",
                "Thumbs.db",
            ]
        if self.auto_untrack_patterns is None:
            self.auto_untrack_patterns = [
                "*.dot",
                "*.pyc",
                "*.pyo",
                ".DS_Store",
                "Thumbs.db",
            ]


CFG = Config()

# %%
# =========================
# CORE HELPERS
# =========================

def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

def log(msg: str) -> None:
    print(f"[{ts()}] {msg}")

def banner(title: str) -> None:
    print(f"\n[{ts()}] {'=' * 18} {title} {'=' * 18}")

def progress(label: str, i: int, total: int) -> None:
    total = max(total, 1)
    pct = int(i * 100 / total)
    width = 28
    filled = int(width * pct / 100)
    bar = "█" * filled + "░" * (width - filled)
    print(f"[{ts()}] [{bar}] {pct:>3}% | {label}")

def pretty_cmd(cmd: List[str]) -> str:
    return " ".join(shlex.quote(c) for c in cmd)

class DevConsoleError(RuntimeError):
    pass

# %%
# =========================
# PATH / REPO DISCOVERY
# =========================

def detect_repo_path() -> Path:
    env_repo = os.environ.get("PROJECT_DIR", "").strip()
    candidates: List[Path] = []

    if env_repo:
        candidates.append(Path(env_repo))

    candidates.append(Path(CFG.repo_path))

    try:
        here = Path(__file__).resolve()
        candidates.append(here.parents[2])  # tools/dev/file.py -> repo root
    except Exception:
        pass

    cwd = Path.cwd()
    candidates.append(cwd)

    seen = set()
    unique: List[Path] = []
    for c in candidates:
        c = c.resolve()
        if str(c).lower() not in seen:
            unique.append(c)
            seen.add(str(c).lower())

    for candidate in unique:
        if (candidate / ".git").exists():
            return candidate

    raise DevConsoleError(
        "No pude detectar el repo.\n"
        "Define PROJECT_DIR o actualiza CFG.repo_path."
    )

REPO = detect_repo_path()
REPORTS_DIR = REPO / CFG.reports_dir_name
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

banner("BOOT")
log(f"Proyecto: {CFG.project_name}")
log(f"Repo detectado: {REPO}")
log(f"Reportes: {REPORTS_DIR}")

# %%
# =========================
# GIT SHELL
# =========================

def run(
    cmd: List[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess:
    cwd = cwd or REPO
    log(f"$ {pretty_cmd(cmd)}")
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.stdout.strip():
        print(proc.stdout.rstrip())
    if proc.stderr.strip():
        print(proc.stderr.rstrip())
    if check and proc.returncode != 0:
        raise DevConsoleError(
            f"Comando fallo con exit code {proc.returncode}: {pretty_cmd(cmd)}"
        )
    return proc

def git(args: List[str], check: bool = True) -> subprocess.CompletedProcess:
    return run(["git", *args], cwd=REPO, check=check, capture=True)

def ensure_git() -> None:
    banner("CHECK GIT")
    if shutil.which("git") is None:
        raise DevConsoleError("Git no esta disponible en PATH.")
    run(["git", "--version"], cwd=REPO)

def ensure_repo_clean_or_warn() -> None:
    banner("GIT STATUS")
    git(["status"])

def get_current_branch() -> str:
    return git(["branch", "--show-current"]).stdout.strip()

def get_local_branches() -> List[str]:
    out = git(["for-each-ref", "refs/heads", "--format=%(refname:short)"]).stdout
    return [x.strip() for x in out.splitlines() if x.strip()]

def has_upstream() -> bool:
    proc = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], check=False)
    return proc.returncode == 0

# %%
# =========================
# GITIGNORE / CLEANUP
# =========================

def ensure_gitignore_patterns(patterns: Iterable[str]) -> List[str]:
    banner("ENSURE .gitignore")
    path = REPO / ".gitignore"
    existing = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    existing_lines = set(existing.splitlines())

    missing = [p for p in patterns if p not in existing_lines]
    if not missing:
        log(".gitignore ya estaba bien. Cero drama.")
        return []

    block = []
    if existing and not existing.endswith("\n"):
        block.append("")
    block.append("# HITECH-OS dev console artifacts")
    block.extend(missing)
    text = "\n".join(block) + "\n"

    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(text)

    log(f"Patrones agregados: {missing}")
    return missing

def get_tracked_files(patterns: Iterable[str]) -> List[str]:
    args = ["ls-files", "--", *patterns]
    out = git(args).stdout
    return [x.strip() for x in out.splitlines() if x.strip()]

def untrack_files(files: Iterable[str]) -> None:
    files = list(files)
    if not files:
        log("No habia archivos trackeados para sacar del indice.")
        return

    banner("UNTRACK FILES")
    total = len(files)
    for i, f in enumerate(files, start=1):
        progress(f"untracking {f}", i, total)
        git(["rm", "--cached", "--force", "--", f])

def stage_all() -> None:
    banner("STAGE ALL")
    git(["add", "-A"])

def commit_all(message: Optional[str] = None) -> None:
    banner("COMMIT")
    message = message or CFG.default_commit_message
    proc = git(["diff", "--cached", "--quiet", "--exit-code"], check=False)
    if proc.returncode == 0:
        log("No hay cambios staged. Git anda sobrio, no hay nada que commitear.")
        return
    git(["commit", "-m", message])

def push_current_branch() -> None:
    banner("PUSH")
    branch = get_current_branch()
    if has_upstream():
        git(["push"])
    else:
        git(["push", "-u", CFG.remote, branch])

def clean_and_commit(message: Optional[str] = None) -> None:
    ensure_gitignore_patterns(CFG.ignore_patterns)
    tracked_noise = get_tracked_files(CFG.auto_untrack_patterns)
    untrack_files(tracked_noise)
    stage_all()
    commit_all(message or CFG.default_commit_message)
    push_current_branch()
    banner("FINAL STATUS")
    git(["status"])

# %%
# =========================
# LARGE FILES / DIAGNOSTICS
# =========================

def iter_files(root: Path) -> Iterable[Path]:
    skip_dirs = {
        ".git",
        "node_modules",
        ".next",
        "dist",
        "build",
        "__pycache__",
        ".turbo",
        ".venv",
        "venv",
    }
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        yield path

def human_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    n = float(size)
    for u in units:
        if n < 1024 or u == units[-1]:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{size} B"

def show_largest_files(limit: int = 25) -> List[dict]:
    banner(f"LARGEST FILES TOP {limit}")
    items = []
    for file in iter_files(REPO):
        try:
            size = file.stat().st_size
            items.append({
                "path": str(file.relative_to(REPO)),
                "bytes": size,
                "human": human_size(size),
            })
        except OSError:
            continue

    items.sort(key=lambda x: x["bytes"], reverse=True)
    top = items[:limit]
    for row in top:
        print(f"{row['human']:>10} | {row['path']}")
    return top

# %%
# =========================
# REPO SNAPSHOT
# =========================

def build_repo_snapshot() -> dict:
    banner("REPO SNAPSHOT")
    snapshot = {
        "generated_at": ts(),
        "project_name": CFG.project_name,
        "repo": str(REPO),
        "branch": get_current_branch(),
        "branches": get_local_branches(),
        "git_status_short": git(["status", "--short"]).stdout.splitlines(),
        "largest_files": show_largest_files(limit=15),
    }
    return snapshot

def save_repo_snapshot() -> Path:
    snapshot = build_repo_snapshot()
    filename = f"repo_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = REPORTS_DIR / filename
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"Snapshot guardado en: {path}")
    return path

# %%
# =========================
# OPTIONAL SMOKE COMMAND
# =========================

def run_smoke() -> None:
    banner("SMOKE")
    if not CFG.smoke_command:
        log("CFG.smoke_command esta en None. Ponle un comando si quieres humo controlado.")
        return
    run(CFG.smoke_command, cwd=REPO)

# %%
# =========================
# QUICK ACTIONS
# =========================
# Ejecuta las que quieras con Shift + Enter

ensure_git()
ensure_repo_clean_or_warn()

# %%
# Solo ver ramas
branches = get_local_branches()
banner("LOCAL BRANCHES")
for b in branches:
    print("-", b)

# %%
# Solo ver archivos grandes
_ = show_largest_files(limit=30)

# %%
# Solo guardar snapshot de diagnostico
snapshot_path = save_repo_snapshot()

# %%
# Solo arreglar .gitignore
added_patterns = ensure_gitignore_patterns(CFG.ignore_patterns)

# %%
# Solo sacar del indice archivos ruidosos ya trackeados
tracked_noise = get_tracked_files(CFG.auto_untrack_patterns)
tracked_noise[:20], len(tracked_noise)

# %%
# Ejecuta esta celda para destrackearlos
untrack_files(tracked_noise)

# %%
# Stage manual
stage_all()

# %%
# Commit manual
commit_all("chore(repo): clean tracked artifacts and workspace noise")

# %%
# Push manual
push_current_branch()

# %%
# Combo completo: ignore + untrack + add + commit + push
# Cambia el mensaje si quieres algo mas fino.
clean_and_commit("feat(keystone): dev console runtime + pitch diagnostics + repo cleanup")

# %%
# Status final
git(["status"])