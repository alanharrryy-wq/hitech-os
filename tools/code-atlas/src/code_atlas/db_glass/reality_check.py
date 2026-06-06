from __future__ import annotations

import argparse
import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from code_atlas.core.io_utils import (
    human_bytes,
    iter_project_files,
    redacted_env_line,
    safe_rel,
    write_json,
    write_text,
    iso_now,
)

DB_SUFFIXES = {".db", ".sqlite", ".sqlite3"}
MODEL_RE = re.compile(r"^model\s+(\w+)\s*{")
FIELD_RE = re.compile(r"^\s*(\w+)\s+([^\s]+)(.*)$")
MAP_RE = re.compile(r'@@map\("([^"]+)"\)')
DATASOURCE_RE = re.compile(r"^datasource\s+(\w+)\s*{")
ENV_RE = re.compile(r'env\("([^"]+)"\)')


def _sqlite_connect_readonly(path: Path) -> sqlite3.Connection:
    uri = "file:" + path.resolve().as_posix() + "?mode=ro"
    return sqlite3.connect(uri, uri=True, timeout=2.0)


def inspect_sqlite(path: Path, root: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": safe_rel(path, root),
        "absolute_path": str(path),
        "size_bytes": path.stat().st_size,
        "size": human_bytes(path.stat().st_size),
        "ok": False,
        "error": "",
        "integrity_check": "unknown",
        "tables": [],
        "views": [],
        "foreign_keys": [],
        "indexes": [],
        "ghost_relations": [],
    }
    try:
        conn = _sqlite_connect_readonly(path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            info["integrity_check"] = str(cur.execute("PRAGMA integrity_check").fetchone()[0])
        except Exception as exc:
            info["integrity_check"] = f"error: {exc}"
        objects = cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name").fetchall()
        table_names = [r["name"] for r in objects if r["type"] == "table" and not str(r["name"]).startswith("sqlite_")]
        view_names = [r["name"] for r in objects if r["type"] == "view"]
        info["views"] = view_names
        actual_fks: set[tuple[str, str]] = set()
        for table in table_names:
            columns = []
            for col in cur.execute(f"PRAGMA table_info({table!r})").fetchall():
                columns.append({
                    "cid": col[0], "name": col[1], "type": col[2], "notnull": bool(col[3]),
                    "default": col[4], "pk": bool(col[5]),
                })
            row_count = None
            try:
                row_count = int(cur.execute(f"SELECT COUNT(*) FROM {table!r}").fetchone()[0])
            except Exception:
                row_count = None
            fks = []
            for fk in cur.execute(f"PRAGMA foreign_key_list({table!r})").fetchall():
                item = {
                    "id": fk[0], "seq": fk[1], "table": fk[2], "from": fk[3], "to": fk[4],
                    "on_update": fk[5], "on_delete": fk[6], "match": fk[7],
                }
                fks.append(item)
                actual_fks.add((table, item["from"]))
                info["foreign_keys"].append({"from_table": table, **item})
            idxs = []
            for idx in cur.execute(f"PRAGMA index_list({table!r})").fetchall():
                idxs.append({"name": idx[1], "unique": bool(idx[2]), "origin": idx[3], "partial": bool(idx[4])})
                info["indexes"].append({"table": table, "name": idx[1], "unique": bool(idx[2])})
            info["tables"].append({"name": table, "row_count": row_count, "columns": columns, "foreign_keys": fks, "indexes": idxs})
        info["ghost_relations"] = infer_ghost_relations(info["tables"], actual_fks)
        conn.close()
        info["ok"] = True
    except Exception as exc:
        info["error"] = str(exc)
    return info


def _singular(name: str) -> str:
    n = name.lower()
    if n.endswith("ies"):
        return n[:-3] + "y"
    if n.endswith("s"):
        return n[:-1]
    return n


def infer_ghost_relations(tables: list[dict[str, Any]], actual_fks: set[tuple[str, str]]) -> list[dict[str, Any]]:
    by_name = {t["name"].lower(): t for t in tables}
    singulars = {_singular(t["name"]): t for t in tables}
    relations = []
    for table in tables:
        table_name = table["name"]
        for col in table.get("columns", []):
            cname = str(col.get("name", ""))
            lower = cname.lower()
            base = ""
            if lower.endswith("_id"):
                base = lower[:-3]
            elif lower.endswith("id") and lower != "id":
                base = lower[:-2]
            if not base or (table_name, cname) in actual_fks:
                continue
            target = by_name.get(base) or by_name.get(base + "s") or singulars.get(base)
            if target and target["name"] != table_name:
                relations.append({
                    "from_table": table_name,
                    "from_column": cname,
                    "to_table": target["name"],
                    "to_column": "id",
                    "inferred": True,
                    "risk": True,
                    "reason": "column name looks like a foreign key but SQLite does not declare it",
                })
    return relations


def parse_prisma_schema(path: Path, root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    result = {"path": safe_rel(path, root), "datasources": [], "models": []}
    current_model: dict[str, Any] | None = None
    current_ds: dict[str, Any] | None = None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        m = MODEL_RE.match(line)
        if m:
            current_model = {"name": m.group(1), "mapped_table": "", "fields": [], "relations": []}
            result["models"].append(current_model)
            current_ds = None
            continue
        d = DATASOURCE_RE.match(line)
        if d:
            current_ds = {"name": d.group(1), "provider": "", "env_vars": []}
            result["datasources"].append(current_ds)
            current_model = None
            continue
        if line == "}":
            current_model = None
            current_ds = None
            continue
        if current_ds is not None:
            if line.startswith("provider") and "=" in line:
                current_ds["provider"] = line.split("=", 1)[1].strip().strip('"')
            for env in ENV_RE.findall(line):
                current_ds["env_vars"].append(env)
            continue
        if current_model is not None:
            mm = MAP_RE.search(line)
            if mm:
                current_model["mapped_table"] = mm.group(1)
                continue
            fm = FIELD_RE.match(line)
            if fm and not line.startswith("@@"):
                field = {"name": fm.group(1), "type": fm.group(2), "raw": line, "relation": "@relation" in line}
                current_model["fields"].append(field)
                if field["relation"]:
                    current_model["relations"].append(field)
    return result


def compare_prisma_sqlite(prisma: list[dict[str, Any]], sqlite_dbs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sqlite_tables = set()
    for db in sqlite_dbs:
        for table in db.get("tables", []):
            sqlite_tables.add(str(table.get("name", "")).lower())
    comparisons = []
    for schema in prisma:
        for model in schema.get("models", []):
            expected = (model.get("mapped_table") or model.get("name") or "").lower()
            comparisons.append({
                "schema": schema.get("path"),
                "model": model.get("name"),
                "expected_table": expected,
                "sqlite_table_present": expected in sqlite_tables,
            })
    return comparisons


def run_reality_check(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    sqlite_paths = []
    prisma_paths = []
    migrations = []
    seeds = []
    env_refs = []
    api_routes = []
    for p in iter_project_files(root):
        rel = safe_rel(p, root)
        lower = rel.lower()
        if p.suffix.lower() in DB_SUFFIXES:
            sqlite_paths.append(p)
        if p.name == "schema.prisma":
            prisma_paths.append(p)
        if "migration" in lower and p.suffix.lower() in {".sql", ".ts", ".js", ".mjs", ".py"}:
            migrations.append(rel)
        if "seed" in lower and p.suffix.lower() in {".ts", ".js", ".mjs", ".py", ".sql"}:
            seeds.append(rel)
        if p.name.startswith(".env") or p.name.lower().endswith("env.local"):
            try:
                lines = [redacted_env_line(x) for x in p.read_text(encoding="utf-8", errors="replace").splitlines() if "DATABASE" in x.upper() or "PRISMA" in x.upper()]
            except Exception:
                lines = []
            env_refs.append({"path": rel, "database_lines": lines})
        if ("api" in lower or "route" in lower) and p.suffix.lower() in {".ts", ".tsx", ".js", ".jsx", ".py"}:
            api_routes.append(rel)

    sqlite_reports = [inspect_sqlite(p, root) for p in sqlite_paths]
    prisma_reports = [parse_prisma_schema(p, root) for p in prisma_paths]
    comparisons = compare_prisma_sqlite(prisma_reports, sqlite_reports)
    ghost_total = sum(len(db.get("ghost_relations", [])) for db in sqlite_reports)
    validation = "PASS"
    warnings = []
    if any(db.get("ok") is False for db in sqlite_reports):
        warnings.append("some_sqlite_files_failed_readonly_inspection")
    if any(db.get("integrity_check") not in {"ok", "unknown"} for db in sqlite_reports):
        warnings.append("sqlite_integrity_check_not_ok")
    if ghost_total:
        warnings.append("ghost_relations_detected")
    return {
        "kind": "db_reality_check_v1",
        "created_at": iso_now(),
        "project_root": str(root),
        "validation": validation,
        "warnings": warnings,
        "counts": {
            "sqlite_files": len(sqlite_reports),
            "prisma_schemas": len(prisma_reports),
            "migrations": len(migrations),
            "seeds": len(seeds),
            "env_files": len(env_refs),
            "api_route_candidates": len(api_routes),
            "ghost_relations": ghost_total,
        },
        "sqlite": sqlite_reports,
        "prisma": prisma_reports,
        "prisma_sqlite_comparison": comparisons,
        "migrations": migrations[:500],
        "seeds": seeds[:500],
        "env_refs": env_refs,
        "api_route_candidates": api_routes[:500],
    }


def render_markdown(report: dict[str, Any]) -> str:
    c = report.get("counts", {})
    lines = [
        "# DB Reality Check",
        "",
        f"- Project: `{report.get('project_root')}`",
        f"- Validation: **{report.get('validation')}**",
        f"- SQLite files: **{c.get('sqlite_files', 0)}**",
        f"- Prisma schemas: **{c.get('prisma_schemas', 0)}**",
        f"- Ghost relations: **{c.get('ghost_relations', 0)}**",
        "",
        "## Warnings",
        "",
    ]
    warnings = report.get("warnings") or []
    lines.extend([f"- `{w}`" for w in warnings] or ["- None."])
    lines += ["", "## SQLite", ""]
    for db in report.get("sqlite", []):
        lines.append(f"### `{db.get('path')}`")
        lines.append(f"- OK: **{db.get('ok')}**")
        lines.append(f"- Integrity: `{db.get('integrity_check')}`")
        lines.append(f"- Tables: **{len(db.get('tables', []))}**")
        for table in db.get("tables", [])[:80]:
            lines.append(f"  - `{table.get('name')}` rows={table.get('row_count')} cols={len(table.get('columns', []))} fks={len(table.get('foreign_keys', []))}")
        ghosts = db.get("ghost_relations") or []
        if ghosts:
            lines.append("- Ghost relations:")
            for g in ghosts[:80]:
                lines.append(f"  - `{g['from_table']}.{g['from_column']}` -> `{g['to_table']}.{g['to_column']}` risk={g['risk']}")
        lines.append("")
    if not report.get("sqlite"):
        lines.append("- No SQLite files found.")
    lines += ["", "## Prisma", ""]
    for schema in report.get("prisma", []):
        lines.append(f"### `{schema.get('path')}`")
        lines.append(f"- Datasources: **{len(schema.get('datasources', []))}**")
        lines.append(f"- Models: **{len(schema.get('models', []))}**")
        for model in schema.get("models", [])[:100]:
            mapped = f" -> `{model.get('mapped_table')}`" if model.get("mapped_table") else ""
            lines.append(f"  - `{model.get('name')}`{mapped} fields={len(model.get('fields', []))} relations={len(model.get('relations', []))}")
        lines.append("")
    if not report.get("prisma"):
        lines.append("- No Prisma schemas found.")
    return "\n".join(lines).rstrip() + "\n"


def save_reality_check(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "db_reality_check.json"
    md_path = output_dir / "db_reality_check.md"
    write_json(json_path, report)
    write_text(md_path, render_markdown(report))
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DB Reality Check.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out", default="reports/atlas_plus")
    args = parser.parse_args(argv)
    report = run_reality_check(Path(args.project_root))
    _, md = save_reality_check(report, Path(args.out))
    print(f"DB Reality Check: {report['validation']} -> {md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
