#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA Visual OS tree reorg engine 00ZA.

Creates and audits a disciplined tree under:
  apps/terminal-de-venta-system/tools/prisma-visual-os

Default behavior is non-destructive. Use --dry-run first. Apply defaults to
--move-mode scaffold, which only creates folders and writes an index/plan. Moving
files requires an explicit move mode.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PACKAGE = "PRISMA_VISUAL_OS_TREE_REORG_ENGINE_00ZA_20260504_v01"
SHORT = "prisma_visual_os_tree_reorg_00za"
DEFAULT_TARGET_ROOT = r"F:\repos\hitech-os"
DEFAULT_OUT_DIR = r"F:\descargasf"
SYSTEM_REL = Path("apps/terminal-de-venta-system")
VISUAL_OS_REL = SYSTEM_REL / "tools" / "prisma-visual-os"
STATE_DIR_REL = SYSTEM_REL / ".prisma_install_state" / "visual-os-tree-reorg-00za"
BACKUP_DIR_REL = SYSTEM_REL / ".prisma_installer_backups" / PACKAGE

TARGET_DIRS = [
    "doctors",
    "launchers",
    "verifiers",
    "realtime",
    "scoring",
    "generators",
    "gates",
    "qa",
    "docs",
    "tree",
    "_plans",
]

ROOT_KEEP = {
    "run_prisma_show_pos_doctor.cmd",
    "run_prisma_show_pos_ai_doctor.cmd",
    "README_PRISMA_VISUAL_OS_LIVE_STUDIO_00O_00T.md",
}

SELF_NAMES = {
    "prisma_visual_os_tree_reorg_00za.py",
    "run_prisma_visual_os_tree_reorg_00za.cmd",
}

RISK_MARKERS = [
    "import.meta.url",
    "__dirname",
    "Path(__file__)",
    "fileURLToPath",
    "process.cwd",
    "prisma-visual-os",
    "tools\\prisma-visual-os",
    "tools/prisma-visual-os",
]

CATEGORY_RULES: List[Tuple[str, str]] = [
    (r"^(ai_doctor_|doctor_).*\.py$", "doctors"),
    (r"^run_.*\.cmd$", "launchers"),
    (r"^verify_.*\.mjs$", "verifiers"),
    (r"^live-preview-server.*\.mjs$", "realtime"),
    (r"^score_.*\.mjs$", "scoring"),
    (r"^(generate_|print_).*\.mjs$", "generators"),
    (r"^gate_.*\.mjs$", "gates"),
    (r".*qa.*\.mjs$", "qa"),
    (r"^README_.*\.md$", "docs"),
]

@dataclass
class FilePlan:
    name: str
    source: str
    target: str
    category: str
    exists: bool
    size: int
    sha256: Optional[str]
    riskMarkers: List[str]
    riskLevel: str
    action: str
    reason: str
    shim: Optional[str] = None

class Log:
    def __init__(self, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        self.path = out_dir / f"{SHORT}_int_{datetime.now().strftime('%y%m%d_%H%M')}.log"
        self.path.write_text(f"[{now()}] START {PACKAGE}\n", encoding="utf-8")
    def write(self, msg: str) -> None:
        line = f"[{now()}] {msg}"
        print(line)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

def now() -> str:
    return datetime.now().isoformat(timespec="seconds")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def classify(name: str) -> str:
    for pattern, category in CATEGORY_RULES:
        if re.match(pattern, name, flags=re.IGNORECASE):
            return category
    return "root_misc"

def risk_markers(path: Path) -> List[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        text = read_text(path)
    except Exception:
        return ["binary_or_unreadable"]
    return [marker for marker in RISK_MARKERS if marker in text]

def detect_node() -> Optional[str]:
    for candidate in ["node.exe", "node"]:
        found = shutil.which(candidate)
        if found:
            return found
    return None

def detect_python() -> str:
    return sys.executable

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Create, audit and optionally apply a clean PRISMA Visual OS tool tree."
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Generate plan only. No file changes.")
    mode.add_argument("--apply", action="store_true", help="Apply selected move mode with backups/state.")
    mode.add_argument("--verify", action="store_true", help="Verify tree folders/state/shims after apply.")
    mode.add_argument("--rollback", action="store_true", help="Rollback the latest apply state.")
    ap.add_argument("--target-root", default=DEFAULT_TARGET_ROOT, help="Repository root. Default: F:\\repos\\hitech-os")
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Output/log directory. Default: F:\\descargasf")
    ap.add_argument(
        "--move-mode",
        choices=["scaffold", "conservative", "full"],
        default="scaffold",
        help="scaffold creates folders only; conservative moves low-risk files; full moves all planned files with shims.",
    )
    ap.add_argument("--force", action="store_true", help="Required with --apply --move-mode full.")
    ap.add_argument("--state", default=None, help="Rollback/verify a specific state JSON path.")
    return ap.parse_args()

def mode_of(args: argparse.Namespace) -> str:
    if args.apply:
        return "apply"
    if args.verify:
        return "verify"
    if args.rollback:
        return "rollback"
    return "dry-run"

def resolve_roots(args: argparse.Namespace, log: Log) -> Tuple[Path, Path, Path, Path]:
    target_root = Path(args.target_root).expanduser().resolve()
    system_root = target_root / SYSTEM_REL
    visual_root = target_root / VISUAL_OS_REL
    out_dir = Path(args.out_dir).expanduser().resolve()
    if not target_root.exists():
        raise FileNotFoundError(f"target root not found: {target_root}")
    if not system_root.exists():
        raise FileNotFoundError(f"system root not found: {system_root}")
    if not visual_root.exists():
        raise FileNotFoundError(f"visual-os root not found: {visual_root}")
    log.write(f"TARGET {target_root}")
    log.write(f"VISUAL_OS {visual_root}")
    return target_root, system_root, visual_root, out_dir

def list_root_files(visual_root: Path) -> List[Path]:
    return sorted([p for p in visual_root.iterdir() if p.is_file()], key=lambda p: p.name.lower())

def plan_files(visual_root: Path, move_mode: str) -> List[FilePlan]:
    plans: List[FilePlan] = []
    for path in list_root_files(visual_root):
        name = path.name
        if name in SELF_NAMES:
            continue
        category = classify(name)
        target = visual_root / category / name if category != "root_misc" else visual_root / "_plans" / name
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        digest = sha256_file(path) if exists else None
        markers = risk_markers(path)
        risk = "high" if markers else "low"
        action = "keep"
        reason = "default keep"
        shim = None
        if name in ROOT_KEEP:
            action = "keep"
            reason = "canonical root contract; keep until dependent verifier/docs are updated"
        elif category == "root_misc":
            action = "keep"
            reason = "unknown category; not moved automatically"
        elif move_mode == "scaffold":
            action = "plan"
            reason = "scaffold mode creates folders and plan only"
        elif move_mode == "conservative":
            if risk == "low" and category in {"scoring", "generators", "gates", "qa"}:
                action = "move_with_shim"
                reason = "low-risk non-canonical tool in conservative set"
                shim = str(path)
            else:
                action = "defer"
                reason = "path-sensitive or canonical entrypoint; requires wrapper/audit before move"
        elif move_mode == "full":
            action = "move_with_shim"
            reason = "full mode requested; compatibility shim will remain at root"
            shim = str(path)
        plans.append(FilePlan(
            name=name,
            source=str(path),
            target=str(target),
            category=category,
            exists=exists,
            size=size,
            sha256=digest,
            riskMarkers=markers,
            riskLevel=risk,
            action=action,
            reason=reason,
            shim=shim,
        ))
    return plans

def plan_summary(plans: List[FilePlan]) -> Dict[str, Any]:
    by_action: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    for p in plans:
        by_action[p.action] = by_action.get(p.action, 0) + 1
        by_category[p.category] = by_category.get(p.category, 0) + 1
    return {"total": len(plans), "byAction": by_action, "byCategory": by_category}

def write_plan(out_dir: Path, visual_root: Path, mode: str, move_mode: str, plans: List[FilePlan], log: Log) -> Path:
    payload = {
        "package": PACKAGE,
        "createdAt": now(),
        "mode": mode,
        "moveMode": move_mode,
        "visualRoot": str(visual_root),
        "targetTree": TARGET_DIRS,
        "summary": plan_summary(plans),
        "files": [asdict(p) for p in plans],
        "notes": [
            "dry-run and scaffold do not move runtime files",
            "full mode is intentionally explicit because many files are path-sensitive",
            "canonical root launchers should remain available as compatibility shims",
        ],
    }
    path = out_dir / f"{SHORT}_plan_{datetime.now().strftime('%y%m%d_%H%M')}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    log.write(f"PLAN {path}")
    return path

def ensure_dirs(visual_root: Path, log: Log) -> List[str]:
    created: List[str] = []
    for rel in TARGET_DIRS:
        d = visual_root / rel
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(d))
            log.write(f"MKDIR {d}")
        else:
            log.write(f"DIR exists {d}")
    return created

def write_tree_index(visual_root: Path, plans: List[FilePlan], log: Log) -> Path:
    index_path = visual_root / "tree" / "PRISMA_VISUAL_OS_TREE_00ZA_INDEX.md"
    lines = [
        "# PRISMA Visual OS Tree 00ZA",
        "",
        "Este índice fue generado por `prisma_visual_os_tree_reorg_00za.py`.",
        "",
        "## Carpetas objetivo",
        "",
    ]
    for d in TARGET_DIRS:
        lines.append(f"- `{d}/`")
    lines += ["", "## Plan por archivo", ""]
    for p in plans:
        lines.append(f"- `{p.name}` -> `{p.category}/` | action: `{p.action}` | risk: `{p.riskLevel}`")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log.write(f"INDEX {index_path}")
    return index_path

def backup_path_for(backup_root: Path, source: Path, visual_root: Path) -> Path:
    rel = source.relative_to(visual_root)
    return backup_root / rel

def shim_content(original_name: str, target_category: str) -> str:
    if original_name.endswith(".cmd"):
        return f"@echo off\r\nsetlocal\r\nset SCRIPT_DIR=%~dp0\r\ncall \"%SCRIPT_DIR%{target_category}\\{original_name}\" %*\r\nexit /b %ERRORLEVEL%\r\n"
    if original_name.endswith(".py"):
        return (
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            "import runpy\n"
            f"runpy.run_path(str(Path(__file__).resolve().parent / '{target_category}' / '{original_name}'), run_name='__main__')\n"
        )
    if original_name.endswith(".mjs"):
        return (
            "#!/usr/bin/env node\n"
            "import { pathToFileURL } from 'node:url';\n"
            "import { dirname, join } from 'node:path';\n"
            "import { fileURLToPath } from 'node:url';\n"
            "const here = dirname(fileURLToPath(import.meta.url));\n"
            f"await import(pathToFileURL(join(here, '{target_category}', '{original_name}')).href);\n"
        )
    return f"Moved to {target_category}/{original_name}\n"

def move_with_backup(plan: FilePlan, visual_root: Path, backup_root: Path, log: Log) -> Dict[str, Any]:
    src = Path(plan.source)
    dst = Path(plan.target)
    if not src.exists():
        raise FileNotFoundError(f"source missing: {src}")
    if dst.exists():
        raise FileExistsError(f"target already exists: {dst}")
    backup = backup_path_for(backup_root, src, visual_root)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, backup)
    log.write(f"BACKUP {src} -> {backup}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    log.write(f"MOVE {src} -> {dst}")
    shim = shim_content(src.name, plan.category)
    if src.suffix.lower() == ".cmd":
        src.write_text(shim, encoding="utf-8", newline="\r\n")
    else:
        src.write_text(shim, encoding="utf-8", newline="\n")
    log.write(f"SHIM {src}")
    return {
        "name": plan.name,
        "source": str(src),
        "target": str(dst),
        "backup": str(backup),
        "category": plan.category,
        "sha256Before": plan.sha256,
        "action": plan.action,
    }

def latest_state_path(target_root: Path) -> Optional[Path]:
    state_dir = target_root / STATE_DIR_REL
    if not state_dir.exists():
        return None
    states = sorted(state_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return states[0] if states else None

def write_state(target_root: Path, out_dir: Path, mode: str, move_mode: str, created_dirs: List[str], moved: List[Dict[str, Any]], plan_path: Path, index_path: Path, log: Log) -> Path:
    state_dir = target_root / STATE_DIR_REL
    state_dir.mkdir(parents=True, exist_ok=True)
    state_path = state_dir / f"{SHORT}_state_{datetime.now().strftime('%y%m%d_%H%M%S')}.json"
    state = {
        "package": PACKAGE,
        "createdAt": now(),
        "mode": mode,
        "moveMode": move_mode,
        "createdDirs": created_dirs,
        "moved": moved,
        "planPath": str(plan_path),
        "indexPath": str(index_path),
        "logPath": str(log.path),
        "status": "applied",
    }
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    # Mirror a copy to out_dir so it is easy to attach in chat.
    mirror = out_dir / state_path.name
    mirror.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    log.write(f"STATE {state_path}")
    log.write(f"STATE_MIRROR {mirror}")
    return state_path

def apply(args: argparse.Namespace, target_root: Path, visual_root: Path, out_dir: Path, log: Log) -> Dict[str, Any]:
    if args.move_mode == "full" and not args.force:
        raise RuntimeError("--apply --move-mode full requires --force")
    plans = plan_files(visual_root, args.move_mode)
    created_dirs = ensure_dirs(visual_root, log)
    plan_path = write_plan(out_dir, visual_root, "apply", args.move_mode, plans, log)
    index_path = write_tree_index(visual_root, plans, log)
    moved: List[Dict[str, Any]] = []
    backup_root = target_root / BACKUP_DIR_REL / datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        for p in plans:
            if p.action == "move_with_shim":
                moved.append(move_with_backup(p, visual_root, backup_root, log))
        state_path = write_state(target_root, out_dir, "apply", args.move_mode, created_dirs, moved, plan_path, index_path, log)
        return {"status": "applied", "state": str(state_path), "moved": len(moved), "createdDirs": len(created_dirs)}
    except Exception:
        log.write("ERROR apply failed; automatic rollback begins")
        rollback_records(moved, log)
        raise

def verify(args: argparse.Namespace, target_root: Path, visual_root: Path, log: Log) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    for rel in TARGET_DIRS:
        d = visual_root / rel
        checks.append({"name": f"dir {rel}", "ok": d.exists() and d.is_dir(), "path": str(d)})
    state_path = Path(args.state).resolve() if args.state else latest_state_path(target_root)
    checks.append({"name": "state exists", "ok": state_path is not None and state_path.exists(), "path": str(state_path) if state_path else None})
    if state_path and state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        for rec in state.get("moved", []):
            src = Path(rec["source"])
            dst = Path(rec["target"])
            checks.append({"name": f"target {dst.name}", "ok": dst.exists(), "path": str(dst)})
            checks.append({"name": f"shim {src.name}", "ok": src.exists(), "path": str(src)})
    ok = all(c["ok"] for c in checks)
    for c in checks:
        log.write(f"VERIFY {c['name']} ok={c['ok']}")
    if not ok:
        raise RuntimeError("verify failed")
    return {"status": "verified", "checks": checks}

def rollback_records(records: List[Dict[str, Any]], log: Log) -> None:
    for rec in reversed(records):
        src = Path(rec["source"])
        dst = Path(rec["target"])
        backup = Path(rec["backup"])
        if src.exists():
            src.unlink()
            log.write(f"ROLLBACK remove shim {src}")
        if backup.exists():
            shutil.copy2(backup, src)
            log.write(f"ROLLBACK restore original {src}")
        if dst.exists():
            dst.unlink()
            log.write(f"ROLLBACK remove moved {dst}")

def rollback(args: argparse.Namespace, target_root: Path, log: Log) -> Dict[str, Any]:
    state_path = Path(args.state).resolve() if args.state else latest_state_path(target_root)
    if not state_path or not state_path.exists():
        raise FileNotFoundError("No state file found for rollback")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    rollback_records(state.get("moved", []), log)
    index_path = Path(state.get("indexPath", "")) if state.get("indexPath") else None
    if index_path and index_path.exists():
        index_path.unlink()
        log.write(f"ROLLBACK remove index {index_path}")
    removed_dirs = []
    for raw in reversed(state.get("createdDirs", [])):
        d = Path(raw)
        try:
            if d.exists() and d.is_dir() and not any(d.iterdir()):
                d.rmdir()
                removed_dirs.append(str(d))
                log.write(f"ROLLBACK remove empty dir {d}")
        except OSError:
            log.write(f"ROLLBACK keep non-empty dir {d}")
    state["status"] = "rolled_back"
    state["rolledBackAt"] = now()
    state["removedDirs"] = removed_dirs
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    log.write(f"ROLLBACK_STATE {state_path}")
    return {"status": "rolled_back", "state": str(state_path), "movedReverted": len(state.get("moved", [])), "removedDirs": len(removed_dirs)}

def dry_run(args: argparse.Namespace, visual_root: Path, out_dir: Path, log: Log) -> Dict[str, Any]:
    plans = plan_files(visual_root, args.move_mode)
    plan_path = write_plan(out_dir, visual_root, "dry-run", args.move_mode, plans, log)
    return {"status": "ready", "planPath": str(plan_path), "summary": plan_summary(plans)}

def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).expanduser().resolve()
    log = Log(out_dir)
    result: Dict[str, Any] = {"status": "unknown"}
    try:
        mode = mode_of(args)
        target_root, system_root, visual_root, out_dir = resolve_roots(args, log)
        if mode == "dry-run":
            result = dry_run(args, visual_root, out_dir, log)
        elif mode == "apply":
            result = apply(args, target_root, visual_root, out_dir, log)
        elif mode == "verify":
            result = verify(args, target_root, visual_root, log)
        elif mode == "rollback":
            result = rollback(args, target_root, log)
        result.update({
            "package": PACKAGE,
            "mode": mode,
            "moveMode": args.move_mode,
            "targetRoot": str(target_root),
            "visualRoot": str(visual_root),
            "log": str(log.path),
            "finishedAt": now(),
        })
        out_json = out_dir / f"{SHORT}_int_{datetime.now().strftime('%y%m%d_%H%M')}.json"
        out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        log.write(f"JSON {out_json}")
        log.write(f"STATUS {result.get('status')}")
        return 0
    except Exception as exc:
        result = {"package": PACKAGE, "status": "failed", "error": str(exc), "log": str(log.path), "finishedAt": now()}
        out_json = out_dir / f"{SHORT}_FAILED_{datetime.now().strftime('%y%m%d_%H%M')}.json"
        out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        log.write(f"FAILED {exc}")
        log.write(f"JSON {out_json}")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
