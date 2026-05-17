#!/usr/bin/env python3
"""Repair external PRISMA Phase 5 warnings with backup and rollback.

This tool intentionally operates outside quality/ only when explicitly requested.
It fixes the common advisory warnings reported by Q26/Q29:
- stale Control Center .cmd launchers that do not clearly call their wrapper .ps1 files
- legacy PRISMA_LAUNCHER_RUNS markers in Control Center wrappers/docs
- missing rollback language in operator docs

Modes:
  --dry-run   Show the planned changes.
  --apply     Backup touched files, apply changes, then verify.
  --verify    Verify that the warning patterns are gone.
  --rollback  Restore a previous repair backup.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

LAUNCHER_FIXES = {
    "05_LEVANTAR_WEB_CONTROL_LOCAL.cmd": "web_control_local.ps1",
    "07_ABRIR_PANEL_CONTROL_3150.cmd": "panel_3150.ps1",
}

LEGACY_TOKEN_RE = re.compile(r"PRISMA_LAUNCHER_RUNS", re.IGNORECASE)
TEXT_EXTS = {".ps1", ".cmd", ".md", ".txt", ".json"}
STATE_FILE = "LATEST_PRISMA_PHASE5_WARNING_REPAIR.json"

ROLLBACK_SECTION = """

## Rollback operativo

Si una reparación de Phase 5 cambia launchers, wrappers o documentación externa, restaura el backup generado en `F:\\descargasf` con:

```powershell
$State = Get-Content "F:\\descargasf\\LATEST_PRISMA_PHASE5_WARNING_REPAIR.json" | ConvertFrom-Json
py -3 quality\\scripts\\repair_phase5_warnings.py --rollback --repo-root . --backup "$($State.backup)" --backup-root "F:\\descargasf"
```

El rollback debe ejecutarse antes de declarar release si el operador detecta drift visual, rutas incorrectas o evidencia inesperada.
"""

@dataclass
class Change:
    path: Path
    reason: str
    before: str | None
    after: str | None


def now_tag() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def norm(text: str) -> str:
    return text.replace("\\", "/").lower()


def log(log_path: Path, message: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().isoformat(timespec="seconds")
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(f"[{stamp}] {message}\n")
    print(message)


def canonical_cmd(wrapper: str) -> str:
    return (
        "@echo off\n"
        "setlocal\n"
        "set \"PRISMA_CC_DIR=%~dp0\"\n"
        f"powershell -NoProfile -ExecutionPolicy Bypass -File \"%PRISMA_CC_DIR%internal\\wrappers\\{wrapper}\" %*\n"
        "exit /b %ERRORLEVEL%\n"
    )


def iter_text_files(root: Path):
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTS:
            parts = {part.lower() for part in path.parts}
            if "node_modules" in parts or ".git" in parts:
                continue
            yield path


def plan_changes(repo_root: Path) -> list[Change]:
    changes: list[Change] = []
    cc_root = repo_root / "prisma-control-center"
    wrappers_dir = cc_root / "internal" / "wrappers"

    for launcher, wrapper in LAUNCHER_FIXES.items():
        path = cc_root / launcher
        if path.exists():
            before = read_text(path)
            if wrapper.lower() not in norm(before):
                changes.append(Change(path, f"make {launcher} call {wrapper} clearly", before, canonical_cmd(wrapper)))

    if cc_root.exists():
        for path in iter_text_files(cc_root) or []:
            before = read_text(path)
            if LEGACY_TOKEN_RE.search(before):
                after = LEGACY_TOKEN_RE.sub("PRISMA_EVIDENCE_DIR", before)
                changes.append(Change(path, "replace legacy PRISMA_LAUNCHER_RUNS marker", before, after))

    docs = [
        repo_root / "prisma-control-center" / "README_OPERADOR.md",
        repo_root / "prisma-control-center" / "README_OPERADOR_CRYSTAL.md",
        repo_root / "quality" / "docs" / "phase-5-release-operator-readiness.md",
    ]
    existing_docs = [doc for doc in docs if doc.exists()]
    target_doc = existing_docs[0] if existing_docs else repo_root / "quality" / "docs" / "phase-5-release-operator-readiness.md"
    before = read_text(target_doc) if target_doc.exists() else "# PRISMA Phase 5 Operator Notes\n"
    if "rollback" not in norm("\n".join(read_text(doc) for doc in existing_docs)):
        changes.append(Change(target_doc, "add operator rollback documentation", before, before.rstrip() + ROLLBACK_SECTION + "\n"))

    return merge_changes(changes)


def merge_changes(changes: list[Change]) -> list[Change]:
    merged: dict[Path, Change] = {}
    for change in changes:
        if change.path not in merged:
            merged[change.path] = change
            continue
        prior = merged[change.path]
        after = prior.after if prior.after is not None else (prior.before or "")
        reason = prior.reason + "; " + change.reason
        if "replace legacy PRISMA_LAUNCHER_RUNS marker" in change.reason:
            after = LEGACY_TOKEN_RE.sub("PRISMA_EVIDENCE_DIR", after)
        elif "add operator rollback documentation" in change.reason:
            if "rollback" not in norm(after):
                after = after.rstrip() + ROLLBACK_SECTION + "\n"
        elif change.after is not None:
            after = change.after
        merged[change.path] = Change(change.path, reason, prior.before, after)
    return list(merged.values())


def backup_files(changes: list[Change], repo_root: Path, backup_dir: Path) -> None:
    for change in changes:
        rel = change.path.relative_to(repo_root)
        dst = backup_dir / "files" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if change.path.exists():
            shutil.copy2(change.path, dst)
        else:
            dst.write_text("__FILE_DID_NOT_EXIST__\n", encoding="utf-8")
    manifest = [{"path": str(change.path.relative_to(repo_root)), "reason": change.reason} for change in changes]
    (backup_dir / "repair_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def apply_changes(changes: list[Change]) -> None:
    for change in changes:
        assert change.after is not None
        write_text(change.path, change.after)


def verify(repo_root: Path) -> tuple[bool, list[str]]:
    issues: list[str] = []
    cc_root = repo_root / "prisma-control-center"
    wrappers_dir = cc_root / "internal" / "wrappers"
    for launcher, wrapper in LAUNCHER_FIXES.items():
        path = cc_root / launcher
        if path.exists() and wrapper.lower() not in norm(read_text(path)):
            issues.append(f"{launcher} still does not clearly reference {wrapper}")
    if wrappers_dir.exists():
        corpus = "\n".join(read_text(path) for path in iter_text_files(wrappers_dir) or [])
        if "prisma_launcher_runs" in norm(corpus):
            issues.append("wrappers still mention PRISMA_LAUNCHER_RUNS")
    docs = [
        repo_root / "prisma-control-center" / "README_OPERADOR.md",
        repo_root / "prisma-control-center" / "README_OPERADOR_CRYSTAL.md",
        repo_root / "quality" / "docs" / "phase-5-release-operator-readiness.md",
    ]
    doc_corpus = "\n".join(read_text(doc) for doc in docs if doc.exists())
    if "rollback" not in norm(doc_corpus):
        issues.append("operator docs still do not mention rollback")
    return len(issues) == 0, issues


def rollback(repo_root: Path, backup_dir: Path, log_path: Path) -> int:
    manifest_path = backup_dir / "repair_manifest.json"
    files_root = backup_dir / "files"
    if not manifest_path.exists():
        log(log_path, f"ROLLBACK ERROR: missing {manifest_path}")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest:
        rel = Path(item["path"])
        src = files_root / rel
        dst = repo_root / rel
        if src.exists() and src.read_text(encoding="utf-8", errors="ignore") == "__FILE_DID_NOT_EXIST__\n":
            if dst.exists():
                dst.unlink()
                log(log_path, f"removed created file: {rel}")
        elif src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            log(log_path, f"restored: {rel}")
    ok, issues = verify(repo_root)
    if ok:
        log(log_path, "ROLLBACK OK: restored files; current repo may again show pre-repair warnings")
    else:
        log(log_path, "ROLLBACK NOTE: verification after rollback reports warnings as expected from original state")
        for issue in issues:
            log(log_path, "  - " + issue)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair PRISMA Phase 5 advisory warnings with backup and rollback.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    parser.add_argument("--repo-root", required=True, help="apps/terminal-de-venta-system root")
    parser.add_argument("--backup-root", default="F:/descargasf", help="Where logs/backups/state are written")
    parser.add_argument("--backup", default=None, help="Backup directory for rollback")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    backup_root = Path(args.backup_root).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)
    tag = now_tag()
    backup_dir = Path(args.backup).resolve() if args.backup else backup_root / f"PRISMA_PHASE5_WARNING_REPAIR_BACKUP_{tag}"
    log_path = backup_root / f"PRISMA_PHASE5_WARNING_REPAIR_{tag}.log"

    log(log_path, "=== PRISMA Phase 5 warning repair ===")
    log(log_path, f"repo_root: {repo_root}")
    log(log_path, f"backup_dir: {backup_dir}")

    if args.rollback:
        return rollback(repo_root, backup_dir, log_path)

    if args.verify:
        ok, issues = verify(repo_root)
        if ok:
            log(log_path, "VERIFY OK: Phase 5 warning repair patterns are clean")
            return 0
        for issue in issues:
            log(log_path, "VERIFY WARNING: " + issue)
        return 1

    changes = plan_changes(repo_root)
    if args.dry_run:
        log(log_path, f"planned_changes: {len(changes)}")
        for change in changes:
            log(log_path, f"PLAN: {change.path.relative_to(repo_root)} :: {change.reason}")
        return 0

    if args.apply:
        if not changes:
            log(log_path, "APPLY OK: no changes needed")
            state = {"createdAt": _dt.datetime.now().isoformat(timespec="seconds"), "repoRoot": str(repo_root), "backup": str(backup_dir), "log": str(log_path), "status": "no_changes_needed"}
            (backup_root / STATE_FILE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            return 0
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_files(changes, repo_root, backup_dir)
        try:
            apply_changes(changes)
            ok, issues = verify(repo_root)
            if not ok:
                for issue in issues:
                    log(log_path, "VERIFY WARNING AFTER APPLY: " + issue)
                log(log_path, "apply failed verification; rolling back")
                rollback(repo_root, backup_dir, log_path)
                return 1
            state = {"createdAt": _dt.datetime.now().isoformat(timespec="seconds"), "repoRoot": str(repo_root), "backup": str(backup_dir), "log": str(log_path), "status": "applied", "changes": len(changes)}
            (backup_root / STATE_FILE).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            log(log_path, f"APPLY OK: repaired {len(changes)} files")
            return 0
        except Exception as exc:  # noqa: BLE001
            log(log_path, f"APPLY ERROR: {exc}")
            rollback(repo_root, backup_dir, log_path)
            return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

