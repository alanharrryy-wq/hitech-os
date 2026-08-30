#!/usr/bin/env python3
"""Deterministic FILES_MANIFEST.json generator/checker for prisma-html."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "FILES_MANIFEST.json"
IGNORED_DIRS = {
    "__pycache__",
    ".wrangler",
    "cloudflare-results",
    "dist",
    "node_modules",
}
IGNORED_NAMES = {".DS_Store", "Thumbs.db"}
IGNORED_SUFFIXES = (".fail.zip", ".partial.zip", ".pyc", ".result.zip")


def ignored(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in IGNORED_DIRS for part in relative.parts):
        return True
    if path.name in IGNORED_NAMES:
        return True
    if path.name.endswith(IGNORED_SUFFIXES):
        return True
    return False


def sha256_upper(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def build_manifest() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path == MANIFEST or ignored(path):
            continue
        files.append(
            {
                "bytes": path.stat().st_size,
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256_upper(path),
            }
        )
    return {
        "file_count_excluding_manifest": len(files),
        "files": files,
    }


def canonical_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or check prisma-html/FILES_MANIFEST.json deterministically."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Replace FILES_MANIFEST.json.")
    mode.add_argument("--check", action="store_true", help="Fail when committed manifest drifts.")
    args = parser.parse_args()

    expected = build_manifest()
    if args.write:
        MANIFEST.write_text(canonical_text(expected), encoding="utf-8", newline="\n")
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "mode": "write",
                    "manifest": MANIFEST.relative_to(ROOT).as_posix(),
                    "fileCount": expected["file_count_excluding_manifest"],
                },
                indent=2,
            )
        )
        return 0

    if not MANIFEST.is_file():
        print(json.dumps({"status": "FAIL", "reason": "FILES_MANIFEST.json missing"}, indent=2))
        return 1
    try:
        current = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "reason": f"invalid manifest: {exc}"}, indent=2))
        return 1

    if current != expected:
        current_paths = {
            row.get("path"): row for row in current.get("files", []) if isinstance(row, dict)
        }
        expected_paths = {row["path"]: row for row in expected["files"]}
        added = sorted(set(expected_paths) - set(current_paths))
        removed = sorted(set(current_paths) - set(expected_paths))
        changed = sorted(
            path
            for path in set(expected_paths) & set(current_paths)
            if expected_paths[path] != current_paths[path]
        )
        print(
            json.dumps(
                {
                    "status": "DRIFT",
                    "currentCount": current.get("file_count_excluding_manifest"),
                    "expectedCount": expected["file_count_excluding_manifest"],
                    "added": added[:50],
                    "removed": removed[:50],
                    "changed": changed[:50],
                },
                indent=2,
            )
        )
        return 2

    print(
        json.dumps(
            {
                "status": "PASS",
                "mode": "check",
                "fileCount": expected["file_count_excluding_manifest"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
