# -*- coding: utf-8 -*-
"""
PRISMA Black-Box i02 R4 OutputRouter.

Small, dependency-free routing layer for local black-box outputs. It keeps
runtime files under organized subfolders, adds integrated organize / cleanup /
archive commands, and avoids relying on the process current working directory.
"""
from __future__ import annotations

import argparse
import atexit
import datetime as _dt
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

VERSION = "i02-r4-output-router"
CANONICAL_FOLDERS = [
    "installers",
    "packages",
    "logs",
    "reports",
    "evidence",
    "backups",
    "runtime",
    "work",
    "docs",
    "_control",
    "_duplicates",
    "_unknown",
]
ROOT_KEEP_FILENAMES = {
    "black_box_folder_organizer.py",
    "install_black_box_i02_r4_output_router.py",
}
ROOT_KEEP_SUFFIXES = {".py"}


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")


def resolve_out_root(value: Optional[str]) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    env_value = os.environ.get("PRISMA_BLACK_BOX_OUT") or os.environ.get("BLACK_BOX_OUT")
    if env_value:
        return Path(env_value).expanduser().resolve()
    return Path(r"F:\Black-box").resolve()


def parse_flag_value(argv: Iterable[str], flag: str) -> Optional[str]:
    args = list(argv)
    for index, token in enumerate(args):
        if token == flag and index + 1 < len(args):
            return args[index + 1]
        prefix = flag + "="
        if token.startswith(prefix):
            return token[len(prefix):]
    return None


def ensure_black_box_layout(out_root: Path | str) -> Dict[str, str]:
    root = Path(out_root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    created = {}
    for name in CANONICAL_FOLDERS:
        path = root / name
        path.mkdir(parents=True, exist_ok=True)
        created[name] = str(path)
    archive_root = root / "runtime" / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    marker = root / "runtime" / "i02_r4_output_router_layout.json"
    marker.write_text(json.dumps({
        "version": VERSION,
        "out_root": str(root),
        "folders": created,
        "archive_root": str(archive_root),
        "updated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    return created


def _is_root_file_candidate(path: Path, root: Path) -> bool:
    try:
        if path.parent.resolve() != root.resolve():
            return False
    except OSError:
        return False
    if not path.is_file():
        return False
    name = path.name
    if name in ROOT_KEEP_FILENAMES:
        return False
    if path.suffix.lower() in ROOT_KEEP_SUFFIXES:
        return False
    if name.startswith("."):
        return False
    return True


def classify_loose_file(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix == ".zip":
        return "packages"
    if suffix in {".log", ".jsonl"}:
        return "logs"
    if "evidence" in name or "snapshot" in name or "capture" in name:
        return "evidence"
    if "backup" in name or suffix in {".bak", ".backup"}:
        return "backups"
    if "manifest" in name or "checksum" in name or name.endswith(".sha256"):
        return "_control"
    if any(token in name for token in ("report", "summary", "status", "check", "diagnostic", "collect")):
        if suffix in {".json", ".md", ".txt", ".html", ".csv"}:
            return "reports"
    if suffix in {".md", ".txt", ".pdf"}:
        return "docs"
    if suffix in {".json"}:
        return "runtime"
    return "_unknown"


def unique_destination(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    counter = 2
    while True:
        candidate = dest.with_name(f"{stem}__dup{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize_black_box_root(out_root: Path | str, dry_run: bool = False) -> Dict[str, object]:
    root = Path(out_root).expanduser().resolve()
    ensure_black_box_layout(root)
    moved: List[Dict[str, str]] = []
    skipped: List[str] = []
    for item in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not _is_root_file_candidate(item, root):
            skipped.append(str(item))
            continue
        folder = classify_loose_file(item)
        dest_dir = root / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = unique_destination(dest_dir / item.name)
        moved.append({"from": str(item), "to": str(dest), "folder": folder})
        if not dry_run:
            shutil.move(str(item), str(dest))
    return {
        "version": VERSION,
        "out_root": str(root),
        "dry_run": dry_run,
        "moved_count": len(moved),
        "moved": moved,
        "skipped_count": len(skipped),
    }


def cleanup_black_box_root(out_root: Path | str, dry_run: bool = False) -> Dict[str, object]:
    root = Path(out_root).expanduser().resolve()
    organize_result = organize_black_box_root(root, dry_run=dry_run)
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "version": VERSION,
        "action": "cleanup",
        "out_root": str(root),
        "dry_run": dry_run,
        "organize": organize_result,
        "note": "Cleanup is non-destructive in i02 R4. It organizes loose root outputs and records this report.",
        "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    if not dry_run:
        report_path = report_dir / f"black_box_cleanup_{utc_stamp()}.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        report["report_path"] = str(report_path)
    return report


def archive_black_box_outputs(out_root: Path | str, dry_run: bool = False, older_than_days: int = 30) -> Dict[str, object]:
    root = Path(out_root).expanduser().resolve()
    ensure_black_box_layout(root)
    cutoff = _dt.datetime.now().timestamp() - (older_than_days * 86400)
    archive_root = root / "runtime" / "archive" / utc_stamp()
    candidates: List[Path] = []
    for folder_name in ("reports", "logs", "evidence"):
        folder = root / folder_name
        if not folder.exists():
            continue
        for item in folder.iterdir():
            if item.is_file() and item.stat().st_mtime < cutoff:
                candidates.append(item)
    moved: List[Dict[str, str]] = []
    if candidates and not dry_run:
        archive_root.mkdir(parents=True, exist_ok=True)
    for item in candidates:
        dest = archive_root / item.parent.name / item.name
        moved.append({"from": str(item), "to": str(dest)})
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(item), str(unique_destination(dest)))
    result = {
        "version": VERSION,
        "action": "archive",
        "out_root": str(root),
        "dry_run": dry_run,
        "older_than_days": older_than_days,
        "candidate_count": len(candidates),
        "moved": moved,
        "archive_root": str(archive_root),
        "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    if not dry_run:
        report_dir = root / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"black_box_archive_{utc_stamp()}.json"
        report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        result["report_path"] = str(report_path)
    return result


def bootstrap_output_router_from_argv(argv: Optional[Iterable[str]] = None) -> None:
    args = list(argv if argv is not None else sys.argv)
    out_value = parse_flag_value(args, "--out") or parse_flag_value(args, "--out-root")
    out_root = resolve_out_root(out_value)
    ensure_black_box_layout(out_root)

    # Normalize loose outputs once the command finishes. This is deliberately
    # conservative: Python installers and scripts in the root are not moved.
    def _finalize() -> None:
        try:
            organize_black_box_root(out_root, dry_run=False)
        except Exception as exc:  # pragma: no cover - best-effort shutdown path
            print(f"[black-box i02 R4 WARN] output routing finalize skipped: {exc}", file=sys.stderr)

    atexit.register(_finalize)


def _build_parser(command: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"black_box.py {command}",
        description=f"PRISMA Black-Box {command} command provided by i02 R4 OutputRouter.",
    )
    parser.add_argument("--root", default=None, help="Project root. Accepted for command symmetry; not mutated by OutputRouter.")
    parser.add_argument("--out", default=None, help="Black-box output root. Default: F:\\Black-box or PRISMA_BLACK_BOX_OUT.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned routing without moving files.")
    if command == "archive":
        parser.add_argument("--older-than-days", type=int, default=30, help="Archive files older than this many days. Default: 30.")
    return parser


def run_output_router_command(command: str, argv_tail: Optional[List[str]] = None) -> int:
    parser = _build_parser(command)
    ns = parser.parse_args(argv_tail if argv_tail is not None else sys.argv[2:])
    out_root = resolve_out_root(ns.out)
    if command == "organize":
        result = organize_black_box_root(out_root, dry_run=ns.dry_run)
    elif command == "cleanup":
        result = cleanup_black_box_root(out_root, dry_run=ns.dry_run)
    elif command == "archive":
        result = archive_black_box_outputs(out_root, dry_run=ns.dry_run, older_than_days=ns.older_than_days)
    else:
        raise SystemExit(f"Unsupported i02 R4 command: {command}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def maybe_handle_i02_r4_command(argv: Optional[Iterable[str]] = None) -> bool:
    args = list(argv if argv is not None else sys.argv)
    if len(args) < 2:
        return False
    command = args[1]
    if command not in {"organize", "cleanup", "archive"}:
        return False
    raise SystemExit(run_output_router_command(command, args[2:]))
