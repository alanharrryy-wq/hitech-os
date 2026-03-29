from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path
from lib.bundles import validate_bundle_zip
from lib.common import collect_files, copy_payload, discover_repo_root, extract_zip_to_temp, normalize_relpath, resolve_under_root


def _discover_workspace_root(start: Path) -> Path:
    for candidate in [start] + list(start.parents):
        if (candidate / "AGENTS.md").exists():
            return candidate
    return start


def _default_backup_dir(repo_root: Path) -> Path:
    workspace_root = _discover_workspace_root(repo_root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return workspace_root / "tools/_local/tmp/orchestrator_factory_bundle_backups" / stamp


def _apply_atomic(payload_dir: Path, repo_root: Path, backup_dir: Path) -> list[str]:
    plan: list[tuple[str, Path, Path, bool]] = []
    for file_path in collect_files(payload_dir):
        rel = normalize_relpath(file_path.relative_to(payload_dir))
        target = resolve_under_root(repo_root, rel)
        plan.append((rel, file_path, target, target.exists()))

    backups: list[tuple[Path, Path]] = []
    created: list[Path] = []

    backup_dir.mkdir(parents=True, exist_ok=True)
    try:
        for rel, _, target, existed in plan:
            if not existed:
                continue
            backup_path = backup_dir / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_path)
            backups.append((target, backup_path))

        for _, source, target, existed in plan:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if not existed:
                created.append(target)
    except Exception:
        for target, backup_path in backups:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, target)
        for created_path in created:
            if created_path.exists():
                created_path.unlink()
        raise

    return [item[0] for item in plan]


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a validated bundle to the repo.")
    parser.add_argument("bundle_zip")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print intended payload operations without writing files.")
    parser.add_argument("--backup-dir", help="Backup directory used for atomic apply rollback.")
    args = parser.parse_args()
    repo_root = discover_repo_root(Path(__file__).resolve())
    bundle_path = Path(args.bundle_zip)
    result = validate_bundle_zip(bundle_path, repo_root)
    if not result["ok"] and not args.force:
        print("[ERROR] bundle validation failed; use --force only if you understand the risk")
        return 1

    extracted = extract_zip_to_temp(bundle_path)
    payload = extracted / "payload"
    if args.dry_run:
        copied = copy_payload(payload, repo_root, dry_run=True)
        print(f"[OK] dry-run validated {len(copied)} files")
        return 0

    backup_dir = Path(args.backup_dir) if args.backup_dir else _default_backup_dir(repo_root)
    copied = _apply_atomic(payload, repo_root, backup_dir)
    print(f"[OK] applied {len(copied)} files (atomic). backup_dir={backup_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
