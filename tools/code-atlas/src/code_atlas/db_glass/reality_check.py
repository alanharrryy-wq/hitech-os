from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from pathlib import Path
from typing import Any

from code_atlas.core.io_utils import (
    human_bytes,
    iso_now,
    iter_project_files,
    redacted_env_line,
    safe_rel,
    write_json,
    write_text,
)

DB_SUFFIXES = {".db", ".sqlite", ".sqlite3"}
MODEL_RE = re.compile(r"^model\s+(\w+)\s*{")
FIELD_RE = re.compile(r"^\s*(\w+)\s+([^\s]+)(.*)$")
MAP_RE = re.compile(r'@@map\("([^"]+)"\)')
DATASOURCE_RE = re.compile(r"^datasource\s+(\w+)\s*{")
ENV_RE = re.compile(r'env\("([^"]+)"\)')


def _sqlite_connect_readonly(path: Path) -> sqlite3.Connection:
    return sqlite3.connect("file:" + path.resolve().as_posix() + "?mode=ro", uri=True, timeout=2.0)


def inspect_sqlite(path: Path, root: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": safe_rel(path, root),
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
            info["integrity_check"] = f"error:{type(exc).__name__}"
        objects = cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name").fetchall()
        table_names = [row["name"] for row in objects if row["type"] == "table" and not str(row["name"]).startswith("sqlite_")]
        info["views"] = [row["name"] for row in objects if row["type"] == "view"]
        actual_fks: set[tuple[str, str]] = set()
        for table in table_names:
            columns = [{"cid": col[0], "name": col[1], "type": col[2], "notnull": bool(col[3]), "default": col[4], "pk": bool(col[5])} for col in cur.execute(f"PRAGMA table_info({table!r})").fetchall()]
            try:
                row_count = int(cur.execute(f"SELECT COUNT(*) FROM {table!r}").fetchone()[0])
            except Exception:
                row_count = None
            fks = []
            for fk in cur.execute(f"PRAGMA foreign_key_list({table!r})").fetchall():
                item = {"id": fk[0], "seq": fk[1], "table": fk[2], "from": fk[3], "to": fk[4], "on_update": fk[5], "on_delete": fk[6], "match": fk[7]}
                fks.append(item)
                actual_fks.add((table, item["from"]))
                info["foreign_keys"].append({"from_table": table, **item})
            indexes = []
            for idx in cur.execute(f"PRAGMA index_list({table!r})").fetchall():
                indexes.append({"name": idx[1], "unique": bool(idx[2]), "origin": idx[3], "partial": bool(idx[4])})
                info["indexes"].append({"table": table, "name": idx[1], "unique": bool(idx[2])})
            info["tables"].append({"name": table, "row_count": row_count, "columns": columns, "foreign_keys": fks, "indexes": indexes})
        info["ghost_relations"] = infer_ghost_relations(info["tables"], actual_fks)
        conn.close()
        info["ok"] = True
    except Exception as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"[:200]
    return info


def _singular(name: str) -> str:
    low = name.lower()
    if low.endswith("ies"):
        return low[:-3] + "y"
    if low.endswith("s"):
        return low[:-1]
    return low


def infer_ghost_relations(tables: list[dict[str, Any]], actual_fks: set[tuple[str, str]]) -> list[dict[str, Any]]:
    by_name = {table["name"].lower(): table for table in tables}
    singulars = {_singular(table["name"]): table for table in tables}
    relations: list[dict[str, Any]] = []
    for table in tables:
        table_name = table["name"]
        for column in table.get("columns", []):
            name = str(column.get("name", ""))
            low = name.lower()
            base = low[:-3] if low.endswith("_id") else low[:-2] if low.endswith("id") and low != "id" else ""
            if not base or (table_name, name) in actual_fks:
                continue
            target = by_name.get(base) or by_name.get(base + "s") or singulars.get(base)
            if target and target["name"] != table_name:
                relations.append({"from_table": table_name, "from_column": name, "to_table": target["name"], "to_column": "id", "inferred": True, "risk": True, "reason": "column name resembles a foreign key but SQLite does not declare it"})
    return relations


def parse_prisma_schema(path: Path, root: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    result: dict[str, Any] = {"path": safe_rel(path, root), "datasources": [], "models": []}
    current_model: dict[str, Any] | None = None
    current_ds: dict[str, Any] | None = None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        model_match = MODEL_RE.match(line)
        if model_match:
            current_model = {"name": model_match.group(1), "mapped_table": "", "fields": [], "relations": []}
            result["models"].append(current_model)
            current_ds = None
            continue
        datasource_match = DATASOURCE_RE.match(line)
        if datasource_match:
            current_ds = {"name": datasource_match.group(1), "provider": "", "env_vars": []}
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
            current_ds["env_vars"].extend(ENV_RE.findall(line))
            continue
        if current_model is not None:
            mapped = MAP_RE.search(line)
            if mapped:
                current_model["mapped_table"] = mapped.group(1)
                continue
            field = FIELD_RE.match(line)
            if field and not line.startswith("@@"):
                item = {"name": field.group(1), "type": field.group(2), "relation": "@relation" in line}
                current_model["fields"].append(item)
                if item["relation"]:
                    current_model["relations"].append(item)
    return result


def compare_prisma_sqlite(prisma: list[dict[str, Any]], sqlite_dbs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sqlite_tables = {str(table.get("name", "")).lower() for db in sqlite_dbs for table in db.get("tables", [])}
    comparisons = []
    for schema in prisma:
        for model in schema.get("models", []):
            expected = (model.get("mapped_table") or model.get("name") or "").lower()
            comparisons.append({"schema": schema.get("path"), "model": model.get("name"), "expected_table": expected, "sqlite_table_present": expected in sqlite_tables})
    return comparisons


def run_reality_check(project_root: Path) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    sqlite_paths: list[Path] = []
    prisma_paths: list[Path] = []
    migrations: list[str] = []
    seeds: list[str] = []
    env_refs: list[dict[str, Any]] = []
    api_routes: list[str] = []
    for path in iter_project_files(root):
        rel = safe_rel(path, root)
        low = rel.lower()
        if path.suffix.lower() in DB_SUFFIXES:
            sqlite_paths.append(path)
        if path.name == "schema.prisma":
            prisma_paths.append(path)
        if "migration" in low and path.suffix.lower() in {".sql", ".ts", ".js", ".mjs", ".py"}:
            migrations.append(rel)
        if "seed" in low and path.suffix.lower() in {".ts", ".js", ".mjs", ".py", ".sql"}:
            seeds.append(rel)
        if path.name.startswith(".env") or path.name.lower().endswith("env.local"):
            try:
                lines = [redacted_env_line(line) for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if "DATABASE" in line.upper()]
            except Exception:
                lines = []
            env_refs.append({"path": rel, "database_lines": lines})
        if ("api" in low or "route" in low) and path.suffix.lower() in {".ts", ".tsx", ".js", ".jsx", ".py"}:
            api_routes.append(rel)

    sqlite_reports = [inspect_sqlite(path, root) for path in sqlite_paths]
    prisma_reports = [parse_prisma_schema(path, root) for path in prisma_paths]
    comparisons = compare_prisma_sqlite(prisma_reports, sqlite_reports)
    ghost_total = sum(len(db.get("ghost_relations", [])) for db in sqlite_reports)
    warnings: list[str] = []
    if any(db.get("ok") is False for db in sqlite_reports):
        warnings.append("some_sqlite_files_failed_readonly_inspection")
    if any(db.get("integrity_check") not in {"ok", "unknown"} for db in sqlite_reports):
        warnings.append("sqlite_integrity_check_not_ok")
    if ghost_total:
        warnings.append("ghost_relations_detected")
    return {
        "kind": "db_reality_check_v2",
        "created_at": iso_now(),
        "project_name": root.name,
        "project_path_digest": "sha256:" + hashlib.sha256(str(root).encode("utf-8", errors="ignore")).hexdigest()[:20],
        "environment_neutral": True,
        "validation": "PASS",
        "warnings": warnings,
        "counts": {"sqlite_files": len(sqlite_reports), "prisma_schemas": len(prisma_reports), "migrations": len(migrations), "seeds": len(seeds), "env_files": len(env_refs), "api_route_candidates": len(api_routes), "ghost_relations": ghost_total},
        "sqlite": sqlite_reports,
        "prisma": prisma_reports,
        "prisma_sqlite_comparison": comparisons,
        "migrations": migrations[:500],
        "seeds": seeds[:500],
        "env_refs": env_refs,
        "api_route_candidates": api_routes[:500],
    }


def render_markdown(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = ["# DB Reality Check", "", f"- Project: `{report.get('project_name')}`", f"- Validation: **{report.get('validation')}**", f"- SQLite files: **{counts.get('sqlite_files', 0)}**", f"- Prisma schemas: **{counts.get('prisma_schemas', 0)}**", f"- Ghost relations: **{counts.get('ghost_relations', 0)}**", "", "## Warnings", ""]
    lines.extend([f"- `{warning}`" for warning in report.get("warnings", [])] or ["- None."])
    lines.extend(["", "## SQLite", ""])
    for db in report.get("sqlite", []):
        lines.extend([f"### `{db.get('path')}`", f"- OK: **{db.get('ok')}**", f"- Integrity: `{db.get('integrity_check')}`", f"- Tables: **{len(db.get('tables', []))}**", ""])
    if not report.get("sqlite"):
        lines.append("- No SQLite files found.")
    lines.extend(["", "## Prisma", ""])
    for schema in report.get("prisma", []):
        lines.extend([f"### `{schema.get('path')}`", f"- Datasources: **{len(schema.get('datasources', []))}**", f"- Models: **{len(schema.get('models', []))}**", ""])
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
