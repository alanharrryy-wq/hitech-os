#!/usr/bin/env python3
"""
HITECH OS — Constitution Tables Validator

Validates:
1) JSON Schema compliance for each table file
2) Invariants: unique columns, required fields in rows, no extra row keys, enum membership

Usage:
  python tools/hos/constitution/validate_tables.py --root .
  python tools/hos/constitution/validate_tables.py --root . --strict
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import jsonschema
except Exception as e:
    print("ERROR: Missing dependency 'jsonschema'. Install with: pip install jsonschema", file=sys.stderr)
    raise

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")

def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)

def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def find_tables(root: Path) -> List[Path]:
    tables_dir = root / "docs" / "constitution" / "tables"
    if not tables_dir.exists():
        raise FileNotFoundError(f"Tables dir not found: {tables_dir}")
    return sorted([p for p in tables_dir.glob("TBL_*.json") if p.is_file()])

def validate_schema(table: Dict[str, Any], schema: Dict[str, Any], table_path: Path) -> List[str]:
    errors: List[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(table), key=str):
        loc = "/".join([str(x) for x in err.absolute_path]) or "(root)"
        errors.append(f"{table_path.name}: schema error at {loc}: {err.message}")
    return errors

def col_map(columns: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    m: Dict[str, Dict[str, Any]] = {}
    for c in columns:
        m[c["name"]] = c
    return m

def validate_invariants(table: Dict[str, Any], table_path: Path) -> List[str]:
    errors: List[str] = []

    # Basic patterns
    tid = table.get("table_id", "")
    if not isinstance(tid, str) or not tid.startswith("TBL_"):
        errors.append(f"{table_path.name}: table_id must start with TBL_")
    ver = table.get("version", "")
    if not isinstance(ver, str) or not SEMVER_RE.match(ver):
        errors.append(f"{table_path.name}: version must be semver X.Y.Z")
    if table_path.stem != tid:
        errors.append(f"{table_path.name}: filename must match table_id (expected {tid}.json)")

    columns = table.get("columns", [])
    if not isinstance(columns, list) or not columns:
        errors.append(f"{table_path.name}: columns must be a non-empty array")
        return errors

    # Unique column names
    names = [c.get("name") for c in columns if isinstance(c, dict)]
    if len(names) != len(set(names)):
        errors.append(f"{table_path.name}: duplicate column names detected")

    cm = col_map(columns)

    # Enum columns must have enum_values and row membership must match
    enum_cols = {n: c for n, c in cm.items() if c.get("type") == "enum"}
    for n, c in enum_cols.items():
        vals = c.get("enum_values")
        if not isinstance(vals, list) or not vals:
            errors.append(f"{table_path.name}: enum column '{n}' missing enum_values")

    # Required columns exist in each row, allow row_defaults
    req_cols = {n for n, c in cm.items() if c.get("required") is True}
    defaults = table.get("row_defaults", {})
    if defaults is None:
        defaults = {}
    if not isinstance(defaults, dict):
        errors.append(f"{table_path.name}: row_defaults must be an object if provided")
        defaults = {}

    rows = table.get("rows", [])
    if not isinstance(rows, list):
        errors.append(f"{table_path.name}: rows must be an array")
        return errors

    declared_cols = set(cm.keys())

    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{table_path.name}: row[{i}] must be an object")
            continue

        merged = dict(defaults)
        merged.update(row)

        missing = [c for c in req_cols if c not in merged]
        if missing:
            errors.append(f"{table_path.name}: row[{i}] missing required columns: {', '.join(sorted(missing))}")

        extras = [k for k in merged.keys() if k not in declared_cols]
        if extras:
            errors.append(f"{table_path.name}: row[{i}] has undeclared columns: {', '.join(sorted(extras))}")

        # Enum membership
        for col, cdef in enum_cols.items():
            if col in merged:
                val = merged[col]
                allowed = cdef.get("enum_values", [])
                if allowed and val not in allowed:
                    errors.append(f"{table_path.name}: row[{i}] value '{val}' not allowed for enum '{col}'")

        # Type sanity (lightweight)
        for col, cdef in cm.items():
            if col not in merged:
                continue
            t = cdef.get("type")
            v = merged[col]
            if t == "string" and not isinstance(v, str):
                errors.append(f"{table_path.name}: row[{i}] column '{col}' must be string")
            elif t == "number" and not isinstance(v, (int, float)):
                errors.append(f"{table_path.name}: row[{i}] column '{col}' must be number")
            elif t == "boolean" and not isinstance(v, bool):
                errors.append(f"{table_path.name}: row[{i}] column '{col}' must be boolean")
            elif t == "enum" and not isinstance(v, str):
                errors.append(f"{table_path.name}: row[{i}] enum '{col}' must be string")

    return errors

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--strict", action="store_true", help="Fail on warning-level tables too")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    schema_path = root / "docs" / "constitution" / "tables" / "_schema" / "table_spec.schema.json"
    if not schema_path.exists():
        eprint(f"ERROR: schema not found: {schema_path}")
        return 2

    schema = load_json(schema_path)
    table_paths = find_tables(root)

    if not table_paths:
        eprint("ERROR: No tables found (TBL_*.json)")
        return 2

    all_errors: List[str] = []
    warned_tables: List[str] = []

    for tp in table_paths:
        table = load_json(tp)

        # Schema
        all_errors.extend(validate_schema(table, schema, tp))

        # Invariants
        all_errors.extend(validate_invariants(table, tp))

        # Authority gating
        auth = table.get("authority_level")
        if auth == "warning":
            warned_tables.append(tp.name)

    if all_errors:
        eprint("❌ Constitution tables validation FAILED:\n")
        for err in all_errors:
            eprint(" -", err)
        return 1

    # "OFF by default" behavior: warning tables only fail under --strict
    if args.strict and warned_tables:
        eprint("❌ Strict mode: warning-level tables present:")
        for t in warned_tables:
            eprint(" -", t)
        return 1

    print("✅ Constitution tables validation OK")
    if warned_tables and not args.strict:
        print("ℹ️ Note: warning-level tables exist; run with --strict to make them CI-blocking.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
