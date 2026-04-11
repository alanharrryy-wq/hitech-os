#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical navigation checker for HITECH OS.

This script validates that key repository navigation files exist. It is
intentionally narrow and focused on the highest-value discoverability points,
not on every folder in the repository.

Checks:
- critical root docs exist
- critical local README files exist
- README coverage for key tooling and workflow directories exists

Outputs:
- human-readable report
- optional JSON report

Exit code:
- 0 when all required files are present
- 1 when required files are missing
- 2 on execution/configuration error
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional


REQUIRED_FILES = [
    "README.md",
    "README_START_HERE.md",
    "docs/README.md",
    "docs/GETTING_STARTED.md",
    "docs/TOOLING_GUIDE.md",
    "docs/WORKFLOW_CATALOG.md",
    "docs/REPO_NAVIGATION_STANDARD.md",
    "docs/NOTEBOOK_ENTRY_TEMPLATE.md",
    "tools/health/README.md",
    "tools/scripts/README.md",
    "tools/codex/README.md",
    "tools/snapshot/README.md",
    ".github/workflows/README.md",
    "apps/keystone/README.md",
    "apps/demo-engine/README.md",
    "services/core-api/README.md",
    "services/ai-agent/README.md",
    "packages/contracts/README.md",
    "packages/ui-kit/README.md",
    "packages/tooling/README.md",
]


@dataclass
class Finding:
    level: str
    code: str
    message: str
    path: Optional[str] = None


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def validate(repo_root: Path) -> List[Finding]:
    findings: List[Finding] = []
    for rel in REQUIRED_FILES:
        path = repo_root / Path(rel)
        if not path.exists():
            findings.append(Finding("error", "missing_required_navigation_file", f"Required navigation file is missing: {rel}", str(path)))
    return findings


def render_text(repo_root: Path, findings: List[Finding]) -> str:
    lines = []
    lines.append("HITECH OS - repo navigation report")
    lines.append(f"generated_at: {dt.datetime.now().isoformat()}")
    lines.append(f"repo_root: {repo_root}")
    lines.append("")
    lines.append("required files:")
    for rel in REQUIRED_FILES:
        lines.append(f"- {rel}")
    lines.append("")
    lines.append("findings:")
    if findings:
        for f in findings:
            lines.append(f"- [{f.level.upper()}] {f.code}: {f.message}")
            if f.path:
                lines.append(f"  path: {f.path}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-text", default="")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    if not repo_root.exists():
        print(f"[ERROR] repo root does not exist: {repo_root}", file=sys.stderr)
        return 2

    findings = validate(repo_root)
    report_text = render_text(repo_root, findings)
    print(report_text, end="")

    if args.output_json:
        payload = {
            "generated_at": dt.datetime.now().isoformat(),
            "repo_root": str(repo_root),
            "required_files": REQUIRED_FILES,
            "findings": [asdict(f) for f in findings],
        }
        write_text(Path(args.output_json).expanduser().resolve(), json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    if args.output_text:
        write_text(Path(args.output_text).expanduser().resolve(), report_text)

    error_count = sum(1 for f in findings if f.level == "error")
    if args.strict and error_count > 0:
        return 1
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
