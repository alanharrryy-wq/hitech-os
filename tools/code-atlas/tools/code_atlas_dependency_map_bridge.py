#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code Atlas consumer bridge for Capatch dependency-map.

This script does not change Capatch core and does not edit Code Atlas graph code.
It runs the reusable Capatch dependency-map capability against a target project,
then writes Code Atlas-friendly dependency reports under the chosen downloads root.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_REPO_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_CODE_ATLAS_ROOT = DEFAULT_REPO_ROOT / "apps" / "code-atlas"
DEFAULT_CAPATCH_ROOT = DEFAULT_CODE_ATLAS_ROOT / "capatch_system"
DEFAULT_PROJECT_ROOT = DEFAULT_REPO_ROOT / "apps" / "terminal-de-venta-system"
DEFAULT_DOWNLOADS_ROOT = Path(r"F:\descargasf")
ANALYZER_RELATIVE = Path("tools") / "dependency_map" / "analyze_project.py"
STAMP_FORMAT = "%y%m%d_%H%M"


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\n", " ").split()).strip()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run_command(command: list[str], cwd: Path, timeout_seconds: int = 120) -> CommandResult:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    return CommandResult(
        command=command,
        cwd=str(cwd),
        returncode=int(proc.returncode),
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
    )


def json_payload_from_text(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    fallback: dict[str, Any] = {}
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        if not fallback:
            fallback = value
        if not text[index + end:].strip():
            return value
    return fallback


def last_json_payload(text: str) -> dict[str, Any]:
    return json_payload_from_text(text)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def classify_edges(edges: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    internal: list[dict[str, Any]] = []
    external: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for edge in edges:
        kind = str(edge.get("kind") or "")
        if "unresolved" in kind:
            unresolved.append(edge)
        elif "external" in kind or kind == "package-dependency":
            external.append(edge)
        else:
            internal.append(edge)
    return internal, external, unresolved


def detect_nextjs_entrypoints(edges: list[dict[str, Any]]) -> list[str]:
    candidates: set[str] = set()
    for edge in edges:
        source = str(edge.get("source") or "").replace("\\", "/")
        if not source:
            continue
        name = Path(source).name.lower()
        if name in {"page.tsx", "page.ts", "layout.tsx", "layout.ts", "route.ts", "route.js", "index.tsx", "index.ts", "index.js", "index.jsx"}:
            candidates.add(source)
    return sorted(candidates)


def workspace_relationships(project: dict[str, Any], edges: list[dict[str, Any]]) -> dict[str, Any]:
    workspaces = project.get("pnpm_workspaces") if isinstance(project.get("pnpm_workspaces"), list) else []
    internal_edges = [e for e in edges if "internal" in str(e.get("kind") or "")]
    return {
        "pnpm_workspaces": workspaces,
        "internal_edge_count": len(internal_edges),
        "sample_internal_edges": internal_edges[:40],
    }


def build_code_atlas_report(
    *,
    project_root: Path,
    capatch_root: Path,
    profile_payload: dict[str, Any],
    verify_payload: dict[str, Any],
    analyzer_payload: dict[str, Any],
    generated_files: dict[str, str],
    command_results: list[CommandResult],
) -> dict[str, Any]:
    profile = profile_payload.get("profile") if isinstance(profile_payload.get("profile"), dict) else {}
    verification = verify_payload.get("verification") if isinstance(verify_payload.get("verification"), dict) else verify_payload
    analyzer_project = analyzer_payload.get("project") if isinstance(analyzer_payload.get("project"), dict) else {}
    summary = analyzer_payload.get("summary") if isinstance(analyzer_payload.get("summary"), dict) else {}
    edges = analyzer_payload.get("edges") if isinstance(analyzer_payload.get("edges"), list) else []
    internal, external, unresolved = classify_edges([e for e in edges if isinstance(e, dict)])
    tsconfig = analyzer_project.get("tsconfig") if isinstance(analyzer_project.get("tsconfig"), dict) else {}

    return {
        "tool": "code-atlas dependency-map bridge",
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(project_root),
        "capatch_root": str(capatch_root),
        "status": {
            "capatch_profile_ok": bool(profile.get("exists")),
            "capatch_verify_ok": bool(verification.get("ok")),
            "analyzer_edges": int(summary.get("edges") or 0),
            "unresolved_edges": len(unresolved),
        },
        "project_profile": profile,
        "detected_languages": profile.get("languages") or sorted((summary.get("source_counts") or {}).keys()),
        "detected_package_manager": profile.get("package_manager") or analyzer_project.get("package_manager") or "unknown",
        "detected_frameworks": profile.get("frameworks") or [],
        "important_entrypoints": sorted(set((profile.get("entrypoints") or []) + detect_nextjs_entrypoints(edges))),
        "tsconfig_aliases": {
            "path": tsconfig.get("path") or "",
            "base_url": tsconfig.get("base_url") or ".",
            "paths": tsconfig.get("paths") if isinstance(tsconfig.get("paths"), dict) else {},
        },
        "workspace_package_relationships": workspace_relationships(analyzer_project, edges),
        "internal_imports": internal,
        "external_imports": external,
        "unresolved_imports": unresolved,
        "dependency_map_summary": summary,
        "capatch_verification": verification,
        "generated_files": generated_files,
        "command_evidence": [
            {
                "command": item.command,
                "cwd": item.cwd,
                "returncode": item.returncode,
                "stdout_tail": item.stdout[-2500:],
                "stderr_tail": item.stderr[-2500:],
            }
            for item in command_results
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    status = report.get("status") if isinstance(report.get("status"), dict) else {}
    profile = report.get("project_profile") if isinstance(report.get("project_profile"), dict) else {}
    aliases = report.get("tsconfig_aliases") if isinstance(report.get("tsconfig_aliases"), dict) else {}
    generated = report.get("generated_files") if isinstance(report.get("generated_files"), dict) else {}
    internal = report.get("internal_imports") if isinstance(report.get("internal_imports"), list) else []
    external = report.get("external_imports") if isinstance(report.get("external_imports"), list) else []
    unresolved = report.get("unresolved_imports") if isinstance(report.get("unresolved_imports"), list) else []
    workspaces = report.get("workspace_package_relationships") if isinstance(report.get("workspace_package_relationships"), dict) else {}

    lines = [
        "# Code Atlas Dependency Map Report",
        "",
        f"Generated: `{report.get('generated_at', '')}`",
        f"Project root: `{report.get('project_root', '')}`",
        f"Capatch root: `{report.get('capatch_root', '')}`",
        "",
        "## Status",
        "",
        f"- Capatch profile OK: `{status.get('capatch_profile_ok')}`",
        f"- Capatch verify OK: `{status.get('capatch_verify_ok')}`",
        f"- Analyzer edges: `{status.get('analyzer_edges')}`",
        f"- Unresolved edges: `{status.get('unresolved_edges')}`",
        "",
        "## Project profile",
        "",
        f"- Type: `{profile.get('project_type', '')}`",
        f"- Languages: `{', '.join(map(str, report.get('detected_languages') or []))}`",
        f"- Package manager: `{report.get('detected_package_manager', '')}`",
        f"- Frameworks: `{', '.join(map(str, report.get('detected_frameworks') or []))}`",
        f"- Entry points: `{', '.join(map(str, report.get('important_entrypoints') or []))}`",
        "",
        "## TypeScript aliases",
        "",
        f"- Config: `{aliases.get('path', '')}`",
        f"- Base URL: `{aliases.get('base_url', '.')}`",
    ]
    paths = aliases.get("paths") if isinstance(aliases.get("paths"), dict) else {}
    if paths:
        for key, value in paths.items():
            lines.append(f"- `{key}` -> `{value}`")
    else:
        lines.append("- No aliases detected.")

    lines.extend(["", "## Workspace relationships", ""])
    for item in workspaces.get("pnpm_workspaces") or []:
        lines.append(f"- Workspace pattern: `{item}`")
    lines.append(f"- Internal edge count: `{workspaces.get('internal_edge_count', 0)}`")

    def edge_lines(title: str, items: list[Any], limit: int = 80) -> None:
        lines.extend(["", title, ""])
        if not items:
            lines.append("- None detected.")
            return
        for edge in items[:limit]:
            if not isinstance(edge, dict):
                continue
            lines.append(f"- `{edge.get('source')}` -> `{edge.get('target')}` ({edge.get('kind')}: `{edge.get('raw')}`)")
        if len(items) > limit:
            lines.append(f"- ... {len(items) - limit} more")

    edge_lines("## Internal imports", internal)
    edge_lines("## External imports", external)
    edge_lines("## Unresolved imports", unresolved)

    lines.extend(["", "## Generated files", ""])
    for key, value in generated.items():
        lines.append(f"- `{key}`: `{value}`")
    return "\n".join(lines) + "\n"


def render_raw_dependency_map_markdown(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    project = payload.get("project") if isinstance(payload.get("project"), dict) else {}
    edges = payload.get("edges") if isinstance(payload.get("edges"), list) else []
    lines = [
        "# Raw dependency-map report",
        "",
        f"Root: `{payload.get('root', '')}`",
        "",
        "## Summary",
        "",
        f"- Files scanned: `{summary.get('files_scanned', 0)}`",
        f"- Source files: `{summary.get('source_files', 0)}`",
        f"- Edges: `{summary.get('edges', 0)}`",
        f"- Unresolved edges: `{summary.get('unresolved_edges', 0)}`",
        f"- Package manager: `{project.get('package_manager', '')}`",
        "",
        "## Top edges",
        "",
    ]
    for edge in edges[:100]:
        if isinstance(edge, dict):
            lines.append(f"- `{edge.get('source')}` -> `{edge.get('target')}` ({edge.get('kind')}: `{edge.get('raw')}`)")
    if len(edges) > 100:
        lines.append(f"- ... {len(edges) - 100} more")
    return "\n".join(lines) + "\n"


def build_capatch_command(capatch_root: Path, action: str, project_root: Path) -> list[str]:
    return [
        sys.executable,
        str(capatch_root / "capatch.py"),
        "--capability",
        "dependency-map",
        "--capability-action",
        action,
        "--root-dir",
        str(project_root),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Capatch dependency-map and emit a Code Atlas-friendly dependency report.")
    parser.add_argument("--project-root", default=str(DEFAULT_PROJECT_ROOT), help="Project to analyze. Default: Terminal de Venta.")
    parser.add_argument("--capatch-root", default=str(DEFAULT_CAPATCH_ROOT), help="Path to apps/code-atlas/capatch_system.")
    parser.add_argument("--downloads-root", default=str(DEFAULT_DOWNLOADS_ROOT), help="Where reports are written.")
    parser.add_argument("--format", choices=["json", "md", "both"], default="both")
    parser.add_argument("--install-if-missing", action="store_true", help="Use Capatch install when the analyzer is missing.")
    parser.add_argument("--verify-first", action="store_true", help="Run Capatch verify before emitting reports.")
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).expanduser().resolve()
    capatch_root = Path(args.capatch_root).expanduser().resolve()
    downloads_root = Path(args.downloads_root).expanduser().resolve()
    ensure_dir(downloads_root)

    if not project_root.exists() or not project_root.is_dir():
        raise SystemExit(f"Project root does not exist or is not a directory: {project_root}")
    if not capatch_root.exists() or not (capatch_root / "capatch.py").exists():
        raise SystemExit(f"Capatch root is invalid: {capatch_root}")

    stamp = datetime.now().strftime(STAMP_FORMAT)
    prefix = f"code_atlas_dependency_map_{clean_text(project_root.name) or 'project'}_{stamp}"
    analyzer = project_root / ANALYZER_RELATIVE
    command_results: list[CommandResult] = []

    health = run_command([sys.executable, str(capatch_root / "capatch.py"), "--plugin-health"], cwd=capatch_root, timeout_seconds=args.timeout_seconds)
    command_results.append(health)
    if health.returncode != 0:
        raise SystemExit("Capatch plugin health failed. Stop before touching the project.\n" + health.stderr[-2000:])

    profile_result = run_command(build_capatch_command(capatch_root, "profile", project_root), cwd=capatch_root, timeout_seconds=args.timeout_seconds)
    command_results.append(profile_result)
    if profile_result.returncode != 0:
        raise SystemExit("Capatch dependency-map profile failed.\n" + profile_result.stderr[-2000:])
    profile_payload = last_json_payload(profile_result.stdout)

    if not analyzer.exists():
        if not args.install_if_missing:
            raise SystemExit(f"Analyzer missing: {analyzer}. Re-run with --install-if-missing to let Capatch install it.")
        plan_result = run_command(build_capatch_command(capatch_root, "plan", project_root), cwd=capatch_root, timeout_seconds=args.timeout_seconds)
        command_results.append(plan_result)
        if plan_result.returncode != 0:
            raise SystemExit("Capatch dependency-map plan failed.\n" + plan_result.stderr[-2000:])
        install_result = run_command(build_capatch_command(capatch_root, "install", project_root), cwd=capatch_root, timeout_seconds=args.timeout_seconds)
        command_results.append(install_result)
        if install_result.returncode != 0:
            raise SystemExit("Capatch dependency-map install failed.\n" + install_result.stderr[-2000:])

    verify_payload: dict[str, Any] = {}
    if args.verify_first:
        verify_result = run_command(build_capatch_command(capatch_root, "verify", project_root), cwd=capatch_root, timeout_seconds=args.timeout_seconds)
        command_results.append(verify_result)
        verify_payload = last_json_payload(verify_result.stdout)
        verification = verify_payload.get("verification") if isinstance(verify_payload.get("verification"), dict) else {}
        if verify_result.returncode != 0 or not bool(verification.get("ok")):
            raise SystemExit("Capatch dependency-map verify failed.\n" + verify_result.stdout[-2500:] + verify_result.stderr[-2500:])

    raw_json_path = downloads_root / f"{prefix}_raw_dependency_map.json"
    raw_md_path = downloads_root / f"{prefix}_raw_dependency_map.md"
    atlas_json_path = downloads_root / f"{prefix}_code_atlas_report.json"
    atlas_md_path = downloads_root / f"{prefix}_code_atlas_report.md"

    analyzer_json = run_command([sys.executable, str(analyzer), "--root", str(project_root), "--format", "json", "--output", str(raw_json_path), "--max-files", str(args.max_files)], cwd=project_root, timeout_seconds=args.timeout_seconds)
    command_results.append(analyzer_json)
    if analyzer_json.returncode != 0:
        raise SystemExit("dependency-map analyzer JSON run failed.\n" + analyzer_json.stderr[-2000:])

    analyzer_payload = read_json(raw_json_path)
    if not analyzer_payload:
        raise SystemExit(f"Analyzer JSON report was not readable: {raw_json_path}")

    if args.format in {"md", "both"}:
        raw_md_path.write_text(render_raw_dependency_map_markdown(analyzer_payload), encoding="utf-8")

    generated_files = {
        "raw_json": str(raw_json_path),
        "raw_md": str(raw_md_path) if raw_md_path.exists() else "",
        "code_atlas_json": str(atlas_json_path),
        "code_atlas_md": str(atlas_md_path) if args.format in {"md", "both"} else "",
    }
    atlas_report = build_code_atlas_report(
        project_root=project_root,
        capatch_root=capatch_root,
        profile_payload=profile_payload,
        verify_payload=verify_payload,
        analyzer_payload=analyzer_payload,
        generated_files=generated_files,
        command_results=command_results,
    )

    if args.format in {"json", "both"}:
        write_json(atlas_json_path, atlas_report)
    if args.format in {"md", "both"}:
        atlas_md_path.write_text(render_markdown(atlas_report), encoding="utf-8")

    print(json.dumps({"ok": True, "generated_files": generated_files, "summary": atlas_report.get("status")}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
