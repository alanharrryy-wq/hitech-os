#!/usr/bin/env python3
from __future__ import annotations

import sys
import argparse
from pathlib import Path
from typing import Any

_BOOT = Path(__file__).resolve()
for _parent in (_BOOT.parent, *_BOOT.parents):
    if (_parent / "package.json").exists() and (_parent / "pnpm-workspace.yaml").exists():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

from tools.hos._core.paths import load_forbidden_registry
from tools.hos._core.repo_root import find_repo_root
from tools.hos._core.stable_json import dump_json


def _iter_files(repo_root: Path, forbidden: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if any(rel == prefix or rel.startswith(prefix + "/") for prefix in forbidden):
            continue
        files.append(path)
    files.sort(key=lambda item: item.relative_to(repo_root).as_posix())
    return files


def scan_large_files(repo_root: Path, min_bytes: int, limit: int = 100) -> dict[str, Any]:
    registry = load_forbidden_registry(repo_root / "tools/hos/hygiene/forbidden_paths.json")
    files = _iter_files(repo_root=repo_root, forbidden=set(registry.entries))
    rows = []
    for path in files:
        size = path.stat().st_size
        if size < min_bytes:
            continue
        rows.append(
            {
                "path": path.relative_to(repo_root).as_posix(),
                "bytes": size,
                "mb": round(size / (1024 * 1024), 4),
            }
        )
    rows.sort(key=lambda item: (-item["bytes"], item["path"]))
    return {
        "ok": True,
        "thresholdBytes": min_bytes,
        "count": len(rows),
        "files": rows[:limit],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List files above size threshold.")
    parser.add_argument("--min-mb", type=float, default=5.0, help="Minimum file size in MB.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum row count.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = find_repo_root()
    min_bytes = max(1, int(args.min_mb * 1024 * 1024))
    payload = scan_large_files(repo_root=repo_root, min_bytes=min_bytes, limit=max(1, args.limit))
    if args.json:
        print(dump_json(payload), end="")
    else:
        print(f"[scan_large_files] thresholdBytes={payload['thresholdBytes']} count={payload['count']}")
        for row in payload["files"][:10]:
            print(f" - {row['path']} ({row['mb']} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
