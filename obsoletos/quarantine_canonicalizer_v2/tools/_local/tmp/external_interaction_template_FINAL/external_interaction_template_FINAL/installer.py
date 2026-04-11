#!/usr/bin/env python3
"""Install a zipped Next.js project release into a target directory.

Features:
- Locates a project zip automatically when not provided.
- Extracts to a temporary workspace.
- Detects the real project root even when the archive is nested.
- Validates required project markers.
- Backs up an existing installation before replacement.
- Writes an install-report.json file with warnings and results.
- Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from zipfile import BadZipFile, ZipFile

REQUIRED_MARKERS = ("package.json", "app", "components", "src")
DEFAULT_ZIP_PATTERNS = (
    "external_interaction_template*.zip",
    "*.zip",
)
CONTAMINANT_RULES = (
    ".next",
    "node_modules",
    "tsconfig.tsbuildinfo",
)
SQLITE_SUFFIXES = (".db", ".sqlite", ".sqlite3")


@dataclass
class CandidateRoot:
    path: str
    depth: int
    marker_count: int
    package_name: str | None
    score: int


class InstallerError(RuntimeError):
    """Raised for expected installation errors."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def safe_project_dir_name(package_name: str | None, fallback: str) -> str:
    if package_name:
        base = package_name.split("/")[-1].strip()
        if base:
            cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in base)
            cleaned = cleaned.strip("-_")
            if cleaned:
                return cleaned
    return fallback


def expand_path(value: str | os.PathLike[str]) -> Path:
    return Path(value).expanduser().resolve()


def iter_search_dirs(user_dirs: Iterable[str] | None) -> list[Path]:
    dirs: list[Path] = []
    raw: list[Path] = []
    if user_dirs:
        raw.extend(Path(entry).expanduser() for entry in user_dirs)
    raw.extend(
        [
            Path.cwd(),
            Path(__file__).resolve().parent,
            Path.home() / "Downloads",
            Path.home() / "Desktop",
        ]
    )

    seen: set[str] = set()
    for item in raw:
        try:
            resolved = item.resolve()
        except FileNotFoundError:
            resolved = item
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        if resolved.exists() and resolved.is_dir():
            dirs.append(resolved)
    return dirs


def locate_zip(explicit_zip: str | None, search_dirs: Iterable[str] | None) -> Path:
    if explicit_zip:
        zip_path = expand_path(explicit_zip)
        if not zip_path.exists():
            raise InstallerError(f"Zip file not found: {zip_path}")
        if not zip_path.is_file():
            raise InstallerError(f"Zip path is not a file: {zip_path}")
        if zip_path.suffix.lower() != ".zip":
            raise InstallerError(f"Expected a .zip file: {zip_path}")
        return zip_path

    candidates: list[Path] = []
    for directory in iter_search_dirs(search_dirs):
        for pattern in DEFAULT_ZIP_PATTERNS:
            candidates.extend(sorted(directory.glob(pattern)))

    candidates = [path.resolve() for path in candidates if path.is_file() and path.suffix.lower() == ".zip"]
    if not candidates:
        searched = ", ".join(str(item) for item in iter_search_dirs(search_dirs))
        raise InstallerError(f"No zip file found. Searched: {searched}")

    unique_candidates: dict[str, Path] = {str(path): path for path in candidates}
    ordered = sorted(unique_candidates.values(), key=lambda p: p.stat().st_mtime, reverse=True)
    return ordered[0]


def extract_zip(zip_path: Path, workspace: Path) -> Path:
    extracted = workspace / "extracted"
    extracted.mkdir(parents=True, exist_ok=True)
    try:
        with ZipFile(zip_path) as archive:
            archive.extractall(extracted)
    except BadZipFile as exc:
        raise InstallerError(f"Invalid zip file: {zip_path}") from exc
    return extracted


def has_required_markers(directory: Path) -> bool:
    return all((directory / marker).exists() for marker in REQUIRED_MARKERS)


def read_package_name(directory: Path) -> str | None:
    package_json = directory / "package.json"
    if not package_json.exists():
        return None
    try:
        data = read_json(package_json)
    except Exception:
        return None
    value = data.get("name")
    return value if isinstance(value, str) else None


def score_candidate(root: Path, base: Path) -> CandidateRoot:
    relative = root.relative_to(base)
    depth = len(relative.parts)
    marker_count = sum(1 for marker in REQUIRED_MARKERS if (root / marker).exists())
    package_name = read_package_name(root)
    score = (marker_count * 100) - depth
    if package_name and "external_interaction_template" in package_name:
        score += 25
    if root.name == "external_interaction_template":
        score += 10
    return CandidateRoot(
        path=str(root),
        depth=depth,
        marker_count=marker_count,
        package_name=package_name,
        score=score,
    )


def find_project_root(extracted_root: Path) -> tuple[Path, list[CandidateRoot]]:
    candidates: list[CandidateRoot] = []
    if has_required_markers(extracted_root):
        candidates.append(score_candidate(extracted_root, extracted_root))

    for current, dirnames, _filenames in os.walk(extracted_root):
        current_path = Path(current)
        if has_required_markers(current_path):
            candidates.append(score_candidate(current_path, extracted_root))

        dirnames[:] = [
            name for name in dirnames
            if name not in {"node_modules", ".next", ".git", "__pycache__"}
        ]

    if not candidates:
        raise InstallerError(
            "Unable to locate the project root. Required markers missing: "
            + ", ".join(REQUIRED_MARKERS)
        )

    ordered = sorted(candidates, key=lambda item: (-item.score, item.depth, item.path))
    return Path(ordered[0].path), ordered


def collect_hygiene_warnings(project_root: Path) -> dict[str, Any]:
    warnings: list[str] = []
    contaminants: list[str] = []

    for rule in CONTAMINANT_RULES:
        for match in project_root.rglob(rule):
            relative = match.relative_to(project_root)
            contaminants.append(str(relative))

    for match in project_root.rglob("*.tsbuildinfo"):
        relative = match.relative_to(project_root)
        value = str(relative)
        if value not in contaminants:
            contaminants.append(value)

    demo_databases: list[str] = []
    prisma_dir = project_root / "prisma"
    if prisma_dir.exists():
        for item in prisma_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() in SQLITE_SUFFIXES:
                demo_databases.append(str(item.relative_to(project_root)))

    if contaminants:
        warnings.append("Archive contains build or dependency artifacts that should usually be excluded from release zips.")
    if demo_databases:
        warnings.append("Archive contains a local database file under prisma/. Decide explicitly whether demo data belongs in the release.")

    return {
        "warnings": warnings,
        "contaminants": sorted(set(contaminants)),
        "demo_databases": sorted(set(demo_databases)),
    }


def copy_project_tree(source_root: Path, staging_root: Path) -> Path:
    destination = staging_root / source_root.name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source_root, destination)
    return destination


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_existing_install(target_dir: Path, backup_root: Path) -> Path | None:
    if not target_dir.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / f"{target_dir.name}-{timestamp}"
    shutil.move(str(target_dir), str(backup_path))
    return backup_path


def replace_install(staged_project_dir: Path, target_dir: Path) -> None:
    ensure_parent(target_dir)
    if target_dir.exists():
        raise InstallerError(f"Target already exists after backup/cleanup step: {target_dir}")
    shutil.move(str(staged_project_dir), str(target_dir))


def write_report(report_path: Path, report: dict[str, Any]) -> None:
    ensure_parent(report_path)
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install a zipped external_interaction_template release.")
    parser.add_argument("--zip", dest="zip_path", help="Path to the release zip. If omitted, the newest matching zip is auto-detected.")
    parser.add_argument("--target", help="Target installation directory. Default: ./<project-name>")
    parser.add_argument("--backup-root", help="Directory that stores backups. Default: <target-parent>/_backups")
    parser.add_argument("--report", help="Path for install-report.json. Default: <target>/install-report.json")
    parser.add_argument(
        "--search-dir",
        action="append",
        default=[],
        help="Additional directory to search when --zip is omitted. Can be passed multiple times.",
    )
    parser.add_argument("--project-name", help="Override the installed directory name.")
    parser.add_argument("--no-backup", action="store_true", help="Remove any existing target instead of moving it to a backup directory.")
    parser.add_argument("--keep-temp", action="store_true", help="Keep the temporary extraction workspace for troubleshooting.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    workspace_obj: tempfile.TemporaryDirectory[str] | None = None
    workspace_path: Path | None = None
    report: dict[str, Any] = {
        "tool": "installer.py",
        "started_at": utc_now_iso(),
        "success": False,
        "inputs": {
            "zip": args.zip_path,
            "target": args.target,
            "backup_root": args.backup_root,
            "report": args.report,
            "search_dirs": args.search_dir,
            "project_name": args.project_name,
            "no_backup": args.no_backup,
            "keep_temp": args.keep_temp,
        },
    }

    report_path: Path | None = None

    try:
        workspace_obj = tempfile.TemporaryDirectory(prefix="external-interaction-install-")
        workspace_path = Path(workspace_obj.name).resolve()

        zip_path = locate_zip(args.zip_path, args.search_dir)
        extracted_root = extract_zip(zip_path, workspace_path)
        project_root, candidates = find_project_root(extracted_root)
        hygiene = collect_hygiene_warnings(project_root)

        package_name = read_package_name(project_root)
        project_dir_name = safe_project_dir_name(args.project_name or package_name, project_root.name)
        default_target = Path.cwd() / project_dir_name
        target_dir = expand_path(args.target) if args.target else default_target.resolve()
        backup_root = expand_path(args.backup_root) if args.backup_root else target_dir.parent / "_backups"
        report_path = expand_path(args.report) if args.report else target_dir / "install-report.json"

        if target_dir.exists() and not target_dir.is_dir():
            raise InstallerError(f"Target path exists and is not a directory: {target_dir}")
        if target_dir == project_root:
            raise InstallerError("Target directory cannot point at the extracted source directory.")
        if target_dir in zip_path.parents:
            # Allowed, but call it out in the report because it can surprise users.
            hygiene["warnings"].append("Target directory is inside the directory that contains the source zip. This is supported but may not be ideal for repeated installs.")

        staging_parent = workspace_path / "staging"
        staged_project_dir = copy_project_tree(project_root, staging_parent)

        backup_path: Path | None = None
        if target_dir.exists():
            if args.no_backup:
                shutil.rmtree(target_dir)
            else:
                backup_path = backup_existing_install(target_dir, backup_root)

        replace_install(staged_project_dir, target_dir)

        report.update(
            {
                "finished_at": utc_now_iso(),
                "success": True,
                "zip_path": str(zip_path),
                "workspace": str(workspace_path),
                "project_root": str(project_root),
                "target_dir": str(target_dir),
                "backup_path": str(backup_path) if backup_path else None,
                "report_path": str(report_path),
                "package_name": package_name,
                "required_markers": list(REQUIRED_MARKERS),
                "candidate_roots": [asdict(candidate) for candidate in candidates],
                "artifact_hygiene": hygiene,
            }
        )

        write_report(report_path, report)
        print(f"Installed to: {target_dir}")
        print(f"Report: {report_path}")
        if backup_path:
            print(f"Backup: {backup_path}")
        if hygiene["warnings"]:
            print("Warnings:")
            for warning in hygiene["warnings"]:
                print(f"- {warning}")
        return 0

    except Exception as exc:
        report.update(
            {
                "finished_at": utc_now_iso(),
                "success": False,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                "workspace": str(workspace_path) if workspace_path else None,
            }
        )
        if report_path is None:
            fallback = Path.cwd() / "install-report.json"
            report_path = fallback.resolve()
        try:
            write_report(report_path, report)
        except Exception:
            pass
        print(f"ERROR: {exc}", file=sys.stderr)
        print(f"Report: {report_path}", file=sys.stderr)
        return 1
    finally:
        if workspace_obj is not None and not args.keep_temp:
            workspace_obj.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
