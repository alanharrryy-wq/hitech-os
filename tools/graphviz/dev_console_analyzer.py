
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from build_scope_index import build_scope_index
from graphviz_repo_engine import (
    DEFAULT_BACKUP_ROOT,
    DEFAULT_REPO_PATH,
    GraphRunConfig,
    iter_repo_files,
    read_text,
    run_graph_refresh,
    safe_print,
)

ANALYZER_PATTERNS = (
    "DevConsole",
    "PitchLayerDevTools",
    "PitchDevConsoleMount",
    "DevConsoleRegistry",
    "use-dev-console-runtime",
    "SceneStudio",
    "FloatingWindow",
    "PitchRuntimeBridge",
)


def discover_prefixes(repo_path: Path) -> tuple[str, ...]:
    config = GraphRunConfig(
        repo_path=repo_path,
        include_path_prefixes=(),
        ignore_path_prefixes=(),
        only_connected_folders=False,
        only_connected_files=False,
        open_index_on_finish=False,
    )

    matched_prefixes: set[str] = set()
    matched_files: list[str] = []

    for file_path in iter_repo_files(config):
        try:
            text = read_text(file_path)
        except Exception:
            continue

        if not any(pattern in text for pattern in ANALYZER_PATTERNS):
            continue

        rel_file = file_path.relative_to(repo_path).as_posix()
        matched_files.append(rel_file)
        parts = rel_file.split("/")
        if len(parts) >= 2:
            matched_prefixes.add("/".join(parts[:2]))
        elif parts:
            matched_prefixes.add(parts[0])

    report = {
        "patterns": list(ANALYZER_PATTERNS),
        "matched_prefixes": sorted(matched_prefixes),
        "matched_files_sample": matched_files[:250],
        "matched_file_count": len(matched_files),
    }

    report_path = repo_path / "tools" / "graphviz" / "dev_console_analyzer_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    safe_print(f"Analyzer report: {report_path}")
    return tuple(sorted(matched_prefixes))


def main() -> int:
    repo_path = DEFAULT_REPO_PATH
    tools_root = repo_path / "tools" / "graphviz"
    output_root = tools_root / "graphs_dev_console_analyzer"

    discovered_prefixes = discover_prefixes(repo_path)
    if not discovered_prefixes:
        safe_print("No se detectaron prefijos relacionados con Dev Console. No se generaron graphs.")
        return 0

    config = GraphRunConfig(
        repo_path=repo_path,
        tools_root=tools_root,
        output_root=output_root,
        state_file=tools_root / ".graphviz_state_dev_console_analyzer.json",
        manifest_file=tools_root / ".graphviz_manifest_dev_console_analyzer.json",
        index_file=output_root / "index.html",
        scope_index_file=output_root / "scope_index.html",
        run_summary_file=output_root / "run_summary.json",
        backup_root=DEFAULT_BACKUP_ROOT,
        backup_prefix="dev_console_analyzer_backup",
        output_label="dev_console_analyzer_graphs",
        include_path_prefixes=discovered_prefixes,
        only_connected_folders=True,
        only_connected_files=True,
        min_edge_count=1,
        open_index_on_finish=True,
        pause_on_exit=False,
        extra_metadata={
            "policy": "analyzer_discovered_prefixes_full_refresh",
            "discovered_prefixes": list(discovered_prefixes),
            "patterns": list(ANALYZER_PATTERNS),
        },
    )

    safe_print("HITECH Dev Console analyzer graph refresh")
    safe_print(f"Discovered prefixes: {', '.join(discovered_prefixes)}")
    result = run_graph_refresh(config)
    scope_result = build_scope_index(
        repo_root=config.repo_path,
        output_root=config.output_root,
        manifest_path=config.manifest_file,
        scope_index_path=config.scope_index_file,
    )

    safe_print(f"Folders generated: {result['folders_generated']}")
    safe_print(f"Backup zip:        {result['backup_zip'] or '(no previous output to back up)'}")
    safe_print(f"Index:             {result['index_path']}")
    safe_print(f"Scoped index:      {scope_result['scope_index_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
