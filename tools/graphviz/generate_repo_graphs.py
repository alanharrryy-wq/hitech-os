
#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from build_scope_index import build_scope_index
from graphviz_repo_engine import (
    DEFAULT_BACKUP_ROOT,
    DEFAULT_REPO_PATH,
    DEFAULT_TOOLS_ROOT,
    GraphRunConfig,
    open_path,
    run_graph_refresh,
    safe_print,
)


def main() -> int:
    repo_path = DEFAULT_REPO_PATH
    tools_root = DEFAULT_TOOLS_ROOT
    output_root = tools_root / "graphs"

    config = GraphRunConfig(
        repo_path=repo_path,
        tools_root=tools_root,
        output_root=output_root,
        state_file=tools_root / ".graphviz_state.json",
        manifest_file=tools_root / ".graphviz_manifest.json",
        index_file=output_root / "index.html",
        scope_index_file=output_root / "scope_index.html",
        run_summary_file=output_root / "run_summary.json",
        backup_root=DEFAULT_BACKUP_ROOT,
        backup_prefix="repo_graphs_backup",
        output_label="full_repo_graphs",
        include_external_packages=False,
        internal_only=True,
        only_connected_folders=True,
        only_connected_files=True,
        min_edge_count=1,
        max_edges_per_folder=700,
        include_path_prefixes=(),
        ignore_path_prefixes=(),
        open_index_on_finish=True,
        pause_on_exit=False,
        extra_metadata={
            "policy": "always_backup_then_full_refresh",
            "notes": [
                "Every run creates a backup zip of the previous active output before deleting it.",
                "The active output directory is rebuilt from scratch every run.",
                "Only folders with real internal dependency edges are graphed.",
            ],
        },
    )

    safe_print("=" * 72)
    safe_print("HITECH Graphviz | full refresh + backup + dependency-only filters")
    safe_print("=" * 72)
    safe_print(f"Repo:        {config.repo_path}")
    safe_print(f"Output root: {config.output_root}")
    safe_print(f"Backup root: {config.backup_root}")
    safe_print("Policy:      backup old output -> delete active output -> full repo scan -> rebuild graphs")
    safe_print()

    result = run_graph_refresh(config)

    scope_result = build_scope_index(
        repo_root=config.repo_path,
        output_root=config.output_root,
        manifest_path=config.manifest_file,
        scope_index_path=config.scope_index_file,
    )

    safe_print()
    safe_print("Corrida terminada.")
    safe_print(f"Files scanned:      {result['files_scanned']}")
    safe_print(f"Folders generated:  {result['folders_generated']}")
    safe_print(f"Backup zip:         {result['backup_zip'] or '(no previous output to back up)'}")
    safe_print(f"Index:              {result['index_path']}")
    safe_print(f"Scoped index:       {scope_result['scope_index_path']}")
    safe_print(f"Run summary:        {result['run_summary_path']}")

    if config.open_index_on_finish:
        open_path(Path(result["index_path"]))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
