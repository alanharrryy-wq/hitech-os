from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

INDEX_SCHEMA = "code_atlas_derived_query_index.v1"

def build_derived_index(
    output_path: str | Path,
    inventory: dict[str, Any],
    authorities: dict[str, Any],
    graphs: dict[str, Any],
    snapshot: dict[str, Any],
) -> str:
    path = Path(output_path)
    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.execute("""CREATE TABLE files(
            path TEXT PRIMARY KEY, size INTEGER, suffix TEXT, language TEXT, sha256 TEXT,
            historical INTEGER NOT NULL, generated INTEGER NOT NULL, sensitive INTEGER NOT NULL
        )""")
        con.execute("""CREATE TABLE authorities(
            path TEXT PRIMARY KEY, state TEXT, score INTEGER, sha256 TEXT, why_json TEXT
        )""")
        con.execute("""CREATE TABLE edges(
            graph TEXT NOT NULL, source TEXT, target TEXT, type TEXT, payload_json TEXT
        )""")
        meta = {
            "schema": INDEX_SCHEMA,
            "authoritative": "false",
            "rebuildable": "true",
            "snapshotDigest": str(snapshot.get("snapshotDigest") or ""),
            "scannerVersion": str(snapshot.get("scannerVersion") or ""),
        }
        con.executemany("INSERT INTO meta VALUES(?,?)", meta.items())
        con.executemany(
            "INSERT INTO files VALUES(?,?,?,?,?,?,?,?)",
            [
                (
                    row.get("path"), row.get("size"), row.get("suffix"), row.get("language"),
                    row.get("contentSha256"), int(bool(row.get("historical"))),
                    int(bool(row.get("generated"))), int(bool(row.get("sensitiveName"))),
                )
                for row in inventory.get("files") or []
                if row.get("path")
            ],
        )
        con.executemany(
            "INSERT INTO authorities VALUES(?,?,?,?,?)",
            [
                (
                    row.get("path"), row.get("state"), int(row.get("score") or 0),
                    row.get("contentSha256"), json.dumps(row.get("whySelected") or [], ensure_ascii=False, sort_keys=True),
                )
                for row in authorities.get("candidates") or []
                if row.get("path")
            ],
        )
        edge_rows = []
        for graph_name, value in graphs.items():
            if not isinstance(value, dict):
                continue
            for edge in value.get("edges") or []:
                edge_rows.append((
                    graph_name, edge.get("from"), edge.get("to"), edge.get("type"),
                    json.dumps(edge, ensure_ascii=False, sort_keys=True),
                ))
        con.executemany("INSERT INTO edges VALUES(?,?,?,?,?)", edge_rows)
        con.commit()
    finally:
        con.close()
    return str(path)

def query_derived_index(index_path: str | Path, query: str, *, limit: int = 50) -> dict[str, Any]:
    path = Path(index_path)
    if not path.is_file():
        raise FileNotFoundError(f"INDEX_NOT_FOUND:{path}")
    needle = f"%{query.lower()}%"
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    try:
        meta = {row["key"]: row["value"] for row in con.execute("SELECT key,value FROM meta")}
        if meta.get("authoritative") != "false":
            raise RuntimeError("DERIVED_INDEX_AUTHORITY_FLAG_INVALID")
        rows = [
            dict(row) for row in con.execute(
                """SELECT a.path,a.state,a.score,a.sha256,a.why_json
                   FROM authorities a
                   WHERE lower(a.path) LIKE ? OR lower(a.why_json) LIKE ?
                   ORDER BY a.score DESC,a.path
                   LIMIT ?""",
                (needle, needle, max(1, min(500, int(limit)))),
            )
        ]
    finally:
        con.close()
    return {
        "query": query,
        "results": rows,
        "indexAuthority": "DERIVED_NON_AUTHORITATIVE",
        "snapshotDigest": meta.get("snapshotDigest"),
        "doesNotProve": ["Truth beyond source evidence represented by the snapshot."],
    }
