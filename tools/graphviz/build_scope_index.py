
#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from graphviz_repo_engine import (
    DEFAULT_MANIFEST_FILE,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_REPO_PATH,
    DEFAULT_SCOPE_INDEX_FILE,
    FOCUS_PREFIXES,
    NOISE_PREFIXES,
    normalize_rel_path,
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def classify_scope(rel_folder: str) -> str:
    rel_folder = normalize_rel_path(rel_folder)
    for prefix in FOCUS_PREFIXES:
        if rel_folder.startswith(prefix):
            return prefix.rstrip("/")
    if rel_folder == ".":
        return "root"
    return rel_folder.split("/", 1)[0] if "/" in rel_folder else rel_folder


def is_noise(rel_folder: str) -> bool:
    rel_folder = normalize_rel_path(rel_folder)
    return any(rel_folder.startswith(prefix) for prefix in NOISE_PREFIXES)


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        return {"folders": {}}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def build_scope_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    folders = manifest.get("folders", {})
    if not isinstance(folders, dict):
        folders = {}

    rows: list[dict[str, Any]] = []
    for folder, record in folders.items():
        if not isinstance(record, dict):
            continue
        edge_count = int(record.get("edge_count_total", 0))
        source_file_count = int(record.get("source_file_count", 0))
        connected_node_count = int(record.get("connected_node_count", 0))
        scope = str(record.get("scope") or classify_scope(str(folder)))
        noise = bool(record.get("is_noise", is_noise(str(folder))))
        risk_score = (edge_count * 3) + (connected_node_count * 2) + source_file_count + (8 if not noise else 0)

        rows.append(
            {
                "folder": str(folder),
                "scope": scope,
                "is_noise": noise,
                "source_file_count": source_file_count,
                "connected_node_count": connected_node_count,
                "edge_count_total": edge_count,
                "dir_name": str(record.get("dir_name", "")),
                "risk_score": risk_score,
            }
        )

    rows.sort(key=lambda row: (-row["risk_score"], -row["edge_count_total"], row["folder"]))

    scope_stats: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = scope_stats.setdefault(
            row["scope"],
            {"folder_count": 0, "edge_count_total": 0, "source_file_count": 0, "connected_node_count": 0},
        )
        bucket["folder_count"] += 1
        bucket["edge_count_total"] += row["edge_count_total"]
        bucket["source_file_count"] += row["source_file_count"]
        bucket["connected_node_count"] += row["connected_node_count"]

    return {
        "schema_version": 1,
        "generated_at_utc": now_utc(),
        "counts": {
            "folders": len(rows),
            "focus_folders": sum(1 for row in rows if not row["is_noise"]),
            "noise_folders": sum(1 for row in rows if row["is_noise"]),
        },
        "scope_stats": dict(sorted(scope_stats.items(), key=lambda item: (-item[1]["folder_count"], item[0]))),
        "top_risks": rows[:120],
        "all_rows": rows,
    }


def render_scope_index(summary: dict[str, Any], repo_root: Path) -> str:
    counts = summary.get("counts", {})
    scope_stats = summary.get("scope_stats", {})
    top_risks = summary.get("top_risks", [])
    all_rows = summary.get("all_rows", [])

    scope_rows = "\n".join(
        f"<tr><td>{html.escape(scope)}</td><td>{stats['folder_count']}</td><td>{stats['edge_count_total']}</td><td>{stats['source_file_count']}</td><td>{stats['connected_node_count']}</td></tr>"
        for scope, stats in scope_stats.items()
    ) or "<tr><td colspan='5'>Sin datos</td></tr>"

    risk_rows = "\n".join(
        (
            "<tr>"
            f"<td>{html.escape(str(row.get('folder', '')))}</td>"
            f"<td>{html.escape(str(row.get('scope', '')))}</td>"
            f"<td>{int(row.get('source_file_count', 0))}</td>"
            f"<td>{int(row.get('connected_node_count', 0))}</td>"
            f"<td>{int(row.get('edge_count_total', 0))}</td>"
            f"<td>{int(row.get('risk_score', 0))}</td>"
            f"<td><a href='./{html.escape(str(row.get('dir_name', '')))}/graph.svg'>graph.svg</a></td>"
            "</tr>"
        )
        for row in top_risks
    ) or "<tr><td colspan='7'>Sin datos</td></tr>"

    all_rows_html = "\n".join(
        (
            "<tr>"
            f"<td>{html.escape(str(row.get('folder', '')))}</td>"
            f"<td>{html.escape(str(row.get('scope', '')))}</td>"
            f"<td>{'noise' if row.get('is_noise') else 'focus'}</td>"
            f"<td>{int(row.get('source_file_count', 0))}</td>"
            f"<td>{int(row.get('connected_node_count', 0))}</td>"
            f"<td>{int(row.get('edge_count_total', 0))}</td>"
            f"<td><a href='./{html.escape(str(row.get('dir_name', '')))}/summary.json'>summary.json</a></td>"
            "</tr>"
        )
        for row in all_rows[:600]
    ) or "<tr><td colspan='7'>Sin datos</td></tr>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HITECH Graphviz Scoped Index</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; background: #0b1320; color: #e5eefb; }}
    a {{ color: #7dd3fc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .panel {{ background: #132238; border: 1px solid #223a5a; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #223a5a; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ color: #9fc5db; }}
    .muted {{ color: #88a7c2; }}
  </style>
</head>
<body>
  <div class="panel">
    <h1>HITECH Graphviz Scoped Index</h1>
    <p class="muted">Snapshot actual solamente. Cada corrida reemplaza el output activo después de generar backup.</p>
    <p>repo={html.escape(str(repo_root))} | folders={counts.get("folders", 0)} | focus={counts.get("focus_folders", 0)} | noise={counts.get("noise_folders", 0)}</p>
  </div>

  <div class="panel">
    <h2>Scope stats</h2>
    <table>
      <thead>
        <tr><th>scope</th><th>folders</th><th>edges</th><th>source_files</th><th>connected_nodes</th></tr>
      </thead>
      <tbody>{scope_rows}</tbody>
    </table>
  </div>

  <div class="panel">
    <h2>Top risk folders</h2>
    <table>
      <thead>
        <tr><th>folder</th><th>scope</th><th>source_files</th><th>connected_nodes</th><th>edges</th><th>risk_score</th><th>graph</th></tr>
      </thead>
      <tbody>{risk_rows}</tbody>
    </table>
  </div>

  <div class="panel">
    <h2>Snapshot folders</h2>
    <table>
      <thead>
        <tr><th>folder</th><th>scope</th><th>class</th><th>source_files</th><th>connected_nodes</th><th>edges</th><th>summary</th></tr>
      </thead>
      <tbody>{all_rows_html}</tbody>
    </table>
  </div>
</body>
</html>
"""


def build_scope_index(
    repo_root: Path = DEFAULT_REPO_PATH,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    manifest_path: Path = DEFAULT_MANIFEST_FILE,
    scope_index_path: Path = DEFAULT_SCOPE_INDEX_FILE,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    summary = build_scope_summary(manifest)
    scope_index_path.parent.mkdir(parents=True, exist_ok=True)
    scope_index_path.write_text(render_scope_index(summary, repo_root), encoding="utf-8")
    summary_path = output_root / "scope_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "scope_index_path": scope_index_path,
        "scope_summary_path": summary_path,
        "counts": summary.get("counts", {}),
    }


if __name__ == "__main__":
    result = build_scope_index()
    print("Scoped index generado:")
    print(result["scope_index_path"])
    print(result["scope_summary_path"])
