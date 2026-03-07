#!/usr/bin/env python3
"""
Hydration Guard Scaffold
-----------------------
Copies the standard docs and reference templates from this bundle into a target
repository output directory. It does not patch application code.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path
from typing import Iterable, Sequence, Tuple

TOOL_VERSION = "1.0.0"
DOC_FILES: Tuple[Tuple[str, str], ...] = (
    ("docs/architecture/hydration-isolation-standard.md", "docs/architecture/hydration-isolation-standard.md"),
    ("docs/architecture/hydration-isolation-adoption-guide.md", "docs/architecture/hydration-isolation-adoption-guide.md"),
)
TEMPLATE_FILES: Tuple[Tuple[str, str], ...] = (
    ("templates/internal-tool-client-only-boundary.tsx", "reference/hydration-guard/internal-tool-client-only-boundary.tsx"),
    ("templates/use-internal-tool-hydration-diagnostics.ts", "reference/hydration-guard/use-internal-tool-hydration-diagnostics.ts"),
    ("templates/scene-studio-page-client-only.tsx", "reference/hydration-guard/scene-studio-page-client-only.tsx"),
)


def print_progress(current: int, total: int, label: str) -> None:
    width = 28
    total = max(total, 1)
    ratio = min(max(current / total, 0.0), 1.0)
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    percent = int(ratio * 100)
    sys.stdout.write(f"\r[{bar}] {percent:3d}% | {label}")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def copy_with_guard(source: Path, target: Path, force: bool) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not force:
        return "skipped-existing"
    shutil.copy2(source, target)
    return "written"


def write_manifest(manifest_path: Path, lines: Iterable[str]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold hydration guard docs and reference templates into a target repo.")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Target repository root. Defaults to current working directory.")
    parser.add_argument("--output-dir", default="./hydration_guard_scaffold", help="Output directory under the repo root.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files in the output directory.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = Path(args.repo_root).expanduser().resolve()
    output_dir = (repo_root / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir).resolve()
    bundle_root = Path(__file__).resolve().parent.parent

    if not repo_root.exists() or not repo_root.is_dir():
        print(f"Target repo root does not exist or is not a directory: {repo_root}", file=sys.stderr)
        return 2

    plan = list(DOC_FILES) + list(TEMPLATE_FILES)
    manifest_lines = [
        f"Hydration Guard Scaffold Manifest",
        f"Version: {TOOL_VERSION}",
        f"Repo root: {repo_root}",
        f"Output dir: {output_dir}",
        "",
    ]

    total = len(plan)
    for index, (source_rel, target_rel) in enumerate(plan, start=1):
        source = bundle_root / source_rel
        target = output_dir / target_rel
        label = f"Scaffolding {target.name} ({index}/{total})"
        print_progress(index - 1, total, label)
        status = copy_with_guard(source, target, force=args.force)
        manifest_lines.append(f"{status}: {target} | sha256={sha256_file(target) if target.exists() else 'n/a'}")
        print_progress(index, total, label)

    write_manifest(output_dir / "reference/hydration-guard/manifest.txt", manifest_lines)
    print(f"Scaffold complete: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
