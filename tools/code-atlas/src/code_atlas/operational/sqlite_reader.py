from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any
from code_atlas.core.io_utils import human_bytes, iter_project_files, safe_rel
from .security import classify_field_name, redact_row
DB_SUFFIXES = {".db", ".sqlite", ".sqlite3"}
def find_sqlite_databases(project_root: Path) -> list[Path]:
    root = project_root.resolve()
    return sorted((p for p in iter_project_files(root) if p.suffix.lower() in DB_SUFFIXES), key=lambda p: safe_rel(p, root).lower())
def inspect_sqlite_database(path: Path, root: Path, *, max_sample_rows: int = 0) -> dict[str, Any]:
    info: dict[str, Any] = {"path": safe_rel(path, root), "absolute_path": str(path), "size_bytes": path.stat().st_size if path.exists() else 0, "size": human_bytes(path.stat().st_size if path.exists() else 0), "ok": False, "error": "", "integrity_check": "unknown", "tables": [], "views": [], "indexes": [], "foreign_keys": []}
    try:
        conn = sqlite3.connect("file:" + path.resolve().as_posix() + "?mode=ro", uri=True, timeout=2.0)
        conn.row_factory = sqlite3.Row; cur = conn.cursor()
        try: info["integrity_check"] = str(cur.execute("PRAGMA integrity_check").fetchone()[0])
        except Exception as exc: info["integrity_check"] = f"error: {exc}"
        objects = cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name").fetchall()
        table_names = [str(r["name"]) for r in objects if r["type"] == "table" and not str(r["name"]).startswith("sqlite_")]
        info["views"] = [str(r["name"]) for r in objects if r["type"] == "view"]
        for table in table_names:
            columns = []
            for col in cur.execute(f"PRAGMA table_info({table!r})").fetchall():
                cn = str(col[1]); columns.append({"cid": col[0], "name": cn, "type": col[2], "notnull": bool(col[3]), "default": col[4], "pk": bool(col[5]), "privacy_class": classify_field_name(cn)})
            try: row_count = int(cur.execute(f"SELECT COUNT(*) FROM {table!r}").fetchone()[0])
            except Exception: row_count = None
            samples = []
            if max_sample_rows > 0 and row_count:
                try: samples = [redact_row(dict(r)) for r in cur.execute(f"SELECT * FROM {table!r} LIMIT ?", (int(max_sample_rows),)).fetchall()]
                except Exception: samples = []
            fks = []
            for fk in cur.execute(f"PRAGMA foreign_key_list({table!r})").fetchall():
                item = {"id": fk[0], "seq": fk[1], "table": fk[2], "from": fk[3], "to": fk[4], "on_update": fk[5], "on_delete": fk[6], "match": fk[7]}
                fks.append(item); info["foreign_keys"].append({"from_table": table, **item})
            idxs = []
            for idx in cur.execute(f"PRAGMA index_list({table!r})").fetchall():
                item = {"table": table, "name": idx[1], "unique": bool(idx[2]), "origin": idx[3], "partial": bool(idx[4])}
                idxs.append(item); info["indexes"].append(item)
            info["tables"].append({"name": table, "row_count": row_count, "columns": columns, "foreign_keys": fks, "indexes": idxs, "sample_rows_sanitized": samples})
        conn.close(); info["ok"] = True
    except Exception as exc: info["error"] = str(exc)
    return info
def inspect_project_sqlite(project_root: Path, *, max_sample_rows: int = 0) -> list[dict[str, Any]]:
    root = project_root.resolve()
    return [inspect_sqlite_database(p, root, max_sample_rows=max_sample_rows) for p in find_sqlite_databases(root)]
