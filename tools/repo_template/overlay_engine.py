#!/usr/bin/env python3
"""Deterministic repository template overlay engine.

This script copies only missing files from a template repository into a target
repository, never overwriting existing files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


EXCLUDED_DIR_NAMES = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    ".cache",
}


def utc_now_iso() -> str:
    """Return UTC timestamp in ISO-8601 format with Z suffix."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def file_timestamp_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def is_excluded(relative_path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in relative_path.parts)


def iter_template_files(template_root: Path) -> Iterable[Path]:
    """Yield template file paths relative to template_root in deterministic order."""
    collected: list[Path] = []
    for current_root, dir_names, file_names in os.walk(template_root):
        current_path = Path(current_root)
        try:
            relative_dir = current_path.relative_to(template_root)
        except ValueError:
            continue

        if relative_dir != Path(".") and is_excluded(relative_dir):
            dir_names[:] = []
            continue

        dir_names[:] = sorted(
            [
                directory
                for directory in dir_names
                if not is_excluded(relative_dir / directory)
            ]
        )

        for file_name in sorted(file_names):
            rel_file = (relative_dir / file_name) if relative_dir != Path(".") else Path(file_name)
            if is_excluded(rel_file):
                continue
            collected.append(rel_file)

    for relative_file in sorted(collected, key=lambda item: item.as_posix()):
        yield relative_file


def compute_template_hash(template_root: Path, template_files: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for rel_file in template_files:
        digest.update(rel_file.as_posix().encode("utf-8"))
        digest.update(b"\0")
        src_file = template_root / rel_file
        with src_file.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()


@dataclass
class OverlayResult:
    files_added: list[str]
    files_skipped: list[str]
    errors: list[str]


def overlay_template(template_root: Path, repo_root: Path, dry_run: bool) -> OverlayResult:
    files_added: list[str] = []
    files_skipped: list[str] = []
    errors: list[str] = []

    for rel_file in iter_template_files(template_root):
        src_file = template_root / rel_file
        dst_file = repo_root / rel_file

        try:
            if dst_file.exists():
                if dst_file.is_file():
                    files_skipped.append(rel_file.as_posix())
                else:
                    errors.append(
                        f"path collision (destination is not a file): {rel_file.as_posix()}"
                    )
                continue

            files_added.append(rel_file.as_posix())
            if dry_run:
                continue

            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
        except Exception as exc:  # pragma: no cover - defensive branch
            errors.append(f"{rel_file.as_posix()}: {exc}")

    return OverlayResult(
        files_added=sorted(files_added),
        files_skipped=sorted(files_skipped),
        errors=sorted(errors),
    )


def validate_paths(template_root: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    if not template_root.exists() or not template_root.is_dir():
        errors.append(f"template path is missing or not a directory: {template_root}")
    if not repo_root.exists() or not repo_root.is_dir():
        errors.append(f"repo path is missing or not a directory: {repo_root}")
    return errors


def write_report(report: dict, report_dir: Path, repo_name: str) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_name = f"{file_timestamp_utc()}_{repo_name}.json"
    report_path = report_dir / report_name
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return report_path


def sanitize_repo_name(repo_root: Path) -> str:
    name = repo_root.name.strip().lower()
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in name)
    return safe or "repo"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply a deterministic template overlay.")
    parser.add_argument("--template", required=True, help="Template repository root")
    parser.add_argument("--repo", required=True, help="Target repository root")
    parser.add_argument(
        "--report-dir",
        default=str(Path(__file__).resolve().parent / "reports"),
        help="Directory where JSON reports are written",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute actions without copying files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    template_root = Path(args.template).resolve()
    repo_root = Path(args.repo).resolve()
    report_dir = Path(args.report_dir).resolve()

    start_time = utc_now_iso()
    path_errors = validate_paths(template_root, repo_root)

    template_files = list(iter_template_files(template_root)) if not path_errors else []
    template_hash = compute_template_hash(template_root, template_files) if template_files else ""

    result = (
        OverlayResult(files_added=[], files_skipped=[], errors=path_errors.copy())
        if path_errors
        else overlay_template(template_root=template_root, repo_root=repo_root, dry_run=args.dry_run)
    )

    end_time = utc_now_iso()
    report = {
        "repo": str(repo_root),
        "files_added": result.files_added,
        "files_skipped": result.files_skipped,
        "errors": result.errors,
        "template_hash": template_hash,
        "start_time": start_time,
        "end_time": end_time,
    }

    repo_name = sanitize_repo_name(repo_root)
    report_path = write_report(report=report, report_dir=report_dir, repo_name=repo_name)
    print(str(report_path))

    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
