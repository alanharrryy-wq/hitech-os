#!/usr/bin/env python3
"""
Hydration Guard Audit
---------------------
Scans a repository for hydration-related patterns, broad client-only workarounds,
and likely internal tooling subtrees that may be candidates for narrow hydration
isolation.

Standard-library only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

TOOL_VERSION = "1.0.0"
MAX_FILE_BYTES = 512_000
DEFAULT_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".md", ".mdx",
    ".txt", ".yml", ".yaml",
}
SKIP_DIRS = {
    ".git", ".next", "node_modules", "dist", "build", "coverage", ".turbo",
    ".venv", "venv", "out", "tmp", "temp", "__pycache__",
}

PATTERNS: Dict[str, str] = {
    "hydration_keyword": r"hydration|hydrate|Hydration",
    "use_client": r"['\"]use client['\"]",
    "dynamic_ssr_false": r"dynamic\s*\([^\n]+?ssr\s*:\s*false",
    "suppress_hydration_warning": r"suppressHydrationWarning",
    "dom_mutation_signature": r"field_signature|form_signature|alternative_form_signature|visibility_annotation",
    "tooling_route_hint": r"scene-studio|control-room|controlroom|debug|tooling|internal|devtools|hud|workspace",
    "diagnostic_hint": r"hydrationDiag|NEXT_PUBLIC_INTERNAL_TOOL_HYDRATION_DIAGNOSTICS|console\.(info|log|warn).*hydration",
    "client_boundary_hint": r"ClientOnlyBoundary|InternalToolClientOnlyBoundary|ClientOnly",
}

RISKY_BROAD_HINTS: Tuple[str, ...] = (
    "page.tsx",
    "layout.tsx",
    "layout.jsx",
    "page.jsx",
    "app.tsx",
    "_app.tsx",
)

TEXT_ENCODING_CANDIDATES: Tuple[str, ...] = ("utf-8", "utf-8-sig", "latin-1")


@dataclass
class Finding:
    category: str
    path: str
    line_number: int
    line: str
    severity: str
    note: str


@dataclass
class RepoSummary:
    repo_root: str
    total_files_scanned: int
    total_files_skipped: int
    total_findings: int
    likely_internal_tooling_files: int
    risky_broad_workarounds: int
    version: str
    generated_at_epoch: int


def print_progress(current: int, total: int, label: str) -> None:
    width = 28
    if total <= 0:
        total = 1
    ratio = min(max(current / total, 0.0), 1.0)
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    percent = int(ratio * 100)
    sys.stdout.write(f"\r[{bar}] {percent:3d}% | {label}")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")


def is_probably_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:2048]
    except Exception:
        return True
    return b"\x00" in chunk


def iter_candidate_files(repo_root: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        base = Path(root)
        for name in files:
            path = base / name
            if path.suffix.lower() not in DEFAULT_EXTENSIONS:
                continue
            yield path


def safe_read_text(path: Path) -> str:
    for encoding in TEXT_ENCODING_CANDIDATES:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="latin-1", errors="replace")


def build_line_findings(path: Path, content: str) -> List[Finding]:
    findings: List[Finding] = []
    lines = content.splitlines()
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        for category, pattern in PATTERNS.items():
            if re.search(pattern, line, flags=re.IGNORECASE):
                severity = "medium"
                note = "pattern match"
                if category == "dynamic_ssr_false":
                    severity = "high" if any(token in path.name for token in RISKY_BROAD_HINTS) else "medium"
                    note = "broad client-only workaround candidate"
                elif category == "suppress_hydration_warning":
                    severity = "high"
                    note = "suppression should be explicitly justified"
                elif category == "dom_mutation_signature":
                    severity = "high"
                    note = "signature often associated with external DOM mutation"
                elif category == "client_boundary_hint":
                    severity = "low"
                    note = "existing boundary pattern or related naming"
                elif category == "tooling_route_hint":
                    severity = "low"
                    note = "likely internal tooling subtree"
                findings.append(
                    Finding(
                        category=category,
                        path=str(path),
                        line_number=index,
                        line=stripped[:400],
                        severity=severity,
                        note=note,
                    )
                )
    return findings


def summarize_findings(findings: Sequence[Finding]) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for finding in findings:
        counts[finding.category] += 1
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def likely_internal_tooling_paths(findings: Sequence[Finding]) -> List[str]:
    score_by_path: Dict[str, int] = defaultdict(int)
    for finding in findings:
        if finding.category == "tooling_route_hint":
            score_by_path[finding.path] += 2
        elif finding.category in {"hydration_keyword", "dom_mutation_signature", "diagnostic_hint", "client_boundary_hint"}:
            score_by_path[finding.path] += 1
    ranked = [path for path, score in sorted(score_by_path.items(), key=lambda item: (-item[1], item[0])) if score >= 2]
    return ranked[:50]


def risky_broad_workaround_paths(findings: Sequence[Finding]) -> List[str]:
    hits = []
    for finding in findings:
        path_name = Path(finding.path).name
        if finding.category in {"dynamic_ssr_false", "suppress_hydration_warning"} and path_name in RISKY_BROAD_HINTS:
            hits.append(finding.path)
    return sorted(set(hits))


def build_recommendations(findings: Sequence[Finding]) -> List[str]:
    counts = summarize_findings(findings)
    recommendations: List[str] = []

    if counts.get("dom_mutation_signature", 0) > 0:
        recommendations.append(
            "Investigate affected internal routes for narrow client-only isolation. The warning signature resembles external DOM mutation before hydration."
        )
    if counts.get("dynamic_ssr_false", 0) > 0:
        recommendations.append(
            "Review all dynamic(..., { ssr: false }) usages and confirm they are scoped narrowly to internal tooling subtrees rather than full route trees."
        )
    if counts.get("suppress_hydration_warning", 0) > 0:
        recommendations.append(
            "Audit suppressHydrationWarning usages and replace broad suppression with route-local root cause analysis where possible."
        )
    if counts.get("diagnostic_hint", 0) == 0:
        recommendations.append(
            "Add opt-in hydration diagnostics for internal tooling boundaries so route, component, and strategy are logged only when explicitly enabled."
        )
    if counts.get("client_boundary_hint", 0) == 0 and counts.get("tooling_route_hint", 0) > 0:
        recommendations.append(
            "The repo appears to contain internal tooling route hints without an obvious client-only boundary naming convention. Consider standardizing a reusable InternalToolClientOnlyBoundary."
        )
    if not recommendations:
        recommendations.append(
            "No strong hydration-guard signals were found. If issues are still observed at runtime, search the active application repo or verify that the relevant GitHub repository is selected."
        )
    return recommendations


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_markdown_report(path: Path, summary: RepoSummary, findings: Sequence[Finding], recommendations: Sequence[str]) -> None:
    counts = summarize_findings(findings)
    internal_paths = likely_internal_tooling_paths(findings)
    risky_paths = risky_broad_workaround_paths(findings)

    lines: List[str] = []
    lines.append("# Hydration Guard Audit Report")
    lines.append("")
    lines.append(f"- Repo root: `{summary.repo_root}`")
    lines.append(f"- Files scanned: **{summary.total_files_scanned}**")
    lines.append(f"- Files skipped: **{summary.total_files_skipped}**")
    lines.append(f"- Total findings: **{summary.total_findings}**")
    lines.append(f"- Tool version: **{summary.version}**")
    lines.append("")
    lines.append("## Findings by category")
    lines.append("")
    if counts:
        for category, count in counts.items():
            lines.append(f"- `{category}`: {count}")
    else:
        lines.append("- No findings matched the configured patterns.")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for item in recommendations:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Likely internal tooling paths")
    lines.append("")
    if internal_paths:
        for item in internal_paths[:20]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None identified from static pattern signals.")
    lines.append("")
    lines.append("## Risky broad workaround paths")
    lines.append("")
    if risky_paths:
        for item in risky_paths:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None detected from the configured heuristics.")
    lines.append("")
    lines.append("## Sample findings")
    lines.append("")
    if findings:
        for finding in findings[:50]:
            lines.append(
                f"- **{finding.severity.upper()}** `{finding.category}` in `{finding.path}:{finding.line_number}` -> `{finding.line}` ({finding.note})"
            )
    else:
        lines.append("- No sample findings to display.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_audit(repo_root: Path, output_dir: Path) -> int:
    start = time.time()
    files = list(iter_candidate_files(repo_root))
    findings: List[Finding] = []
    skipped = 0

    for index, path in enumerate(files, start=1):
        label = f"Scanning {path.name} ({index}/{len(files)})"
        print_progress(index - 1, len(files), label)
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                skipped += 1
                continue
            if is_probably_binary(path):
                skipped += 1
                continue
            content = safe_read_text(path)
            findings.extend(build_line_findings(path.relative_to(repo_root), content))
        except Exception:
            skipped += 1
            continue
        finally:
            print_progress(index, len(files), label)

    summary = RepoSummary(
        repo_root=str(repo_root),
        total_files_scanned=len(files) - skipped,
        total_files_skipped=skipped,
        total_findings=len(findings),
        likely_internal_tooling_files=len(likely_internal_tooling_paths(findings)),
        risky_broad_workarounds=len(risky_broad_workaround_paths(findings)),
        version=TOOL_VERSION,
        generated_at_epoch=int(time.time()),
    )

    recommendations = build_recommendations(findings)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_json(output_dir / "hydration_guard_summary.json", asdict(summary))
    write_json(output_dir / "hydration_guard_findings.json", [asdict(item) for item in findings])
    write_json(output_dir / "hydration_guard_recommendations.json", recommendations)
    write_markdown_report(output_dir / "hydration_guard_report.md", summary, findings, recommendations)

    elapsed = time.time() - start
    print(f"Audit complete in {elapsed:.2f}s")
    print(f"Report: {output_dir / 'hydration_guard_report.md'}")
    return 0


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan a repo for hydration guard patterns and likely adoption candidates.")
    parser.add_argument("--repo-root", default=os.getcwd(), help="Repository root to scan. Defaults to the current working directory.")
    parser.add_argument("--output-dir", default="./hydration_guard_output", help="Directory where reports will be written.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = Path(args.repo_root).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not repo_root.exists() or not repo_root.is_dir():
        print(f"Repository root does not exist or is not a directory: {repo_root}", file=sys.stderr)
        return 2

    return run_audit(repo_root, output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
