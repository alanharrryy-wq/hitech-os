
#!/usr/bin/env python3
from __future__ import annotations

from build_scope_index import build_scope_index
from graphviz_repo_engine import (
    DEFAULT_BACKUP_ROOT,
    DEFAULT_REPO_PATH,
    GraphRunConfig,
    open_path,
    run_graph_refresh,
    safe_print,
)


TARGET_PREFIXES = (
    "components/dev-console",
    "components/pitch/debug",
    "components/scene-studio",
    "lib/scene-studio",
    "app/pitch",
    "app/scene-studio",
)


def main() -> int:
    repo_path = DEFAULT_REPO_PATH
    tools_root = repo_path / "tools" / "graphviz"
    output_root = tools_root / "graphs_dev_console_runtime"

    config = GraphRunConfig(
        repo_path=repo_path,
        tools_root=tools_root,
        output_root=output_root,
        state_file=tools_root / ".graphviz_state_dev_console_runtime.json",
        manifest_file=tools_root / ".graphviz_manifest_dev_console_runtime.json",
        index_file=output_root / "index.html",
        scope_index_file=output_root / "scope_index.html",
        run_summary_file=output_root / "run_summary.json",
        backup_root=DEFAULT_BACKUP_ROOT,
        backup_prefix="dev_console_runtime_backup",
        output_label="dev_console_runtime_graphs",
        include_path_prefixes=TARGET_PREFIXES,
        ignore_path_prefixes=("components/dev-console/__tests__",),
        only_connected_folders=True,
        only_connected_files=True,
        min_edge_count=1,
        open_index_on_finish=True,
        pause_on_exit=False,
        extra_metadata={
            "policy": "focused_runtime_full_refresh",
            "target_prefixes": list(TARGET_PREFIXES),
            "goal": "runtime and mount-path dependencies only",
        },
    )

    safe_print("HITECH Dev Console runtime graph refresh")
    safe_print(f"Target prefixes: {', '.join(TARGET_PREFIXES)}")
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

    if config.open_index_on_finish:
        open_path(result["index_path"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
